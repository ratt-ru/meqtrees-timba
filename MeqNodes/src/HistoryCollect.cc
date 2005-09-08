//# HistoryCollect.cc: prototype visualization node
//#
//# Copyright (C) 2003
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//# This program is free software; you can redistribute it and/or modify
//# it under the terms of the GNU General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or
//# (at your option) any later version.
//#
//# This program is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License
//# along with this program; if not, write to the Free Software
//# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#

#include "HistoryCollect.h"
#include <DMI/List.h>
#include <DMI/Vec.h>
#include <MEQ/MeqVocabulary.h>
#include <MeqNodes/AID-MeqNodes.h>
    

namespace Meq {

const HIID FTopLabel        = AidTop|AidLabel;
const HIID FInputIndex      = AidInput|AidIndex;
const HIID FHistoryList     = AidHistory|AidList;
const HIID FMaxListSize     = AidMax|AidList|AidSize;
const HIID FVerbose         = AidVerbose;

const HIID FLastError       = AidLast|AidError;
const HIID FLastErrorResult = AidLast|AidError|AidResult;

const HIID CmdGetHistory    = AidGet|AidHistory;


HistoryCollect::HistoryCollect()
  : Node(1), // at least 1 child must be present
    top_label_(AidHistory),
    input_index_(FVellSets|AidSlash|0|AidSlash|FValue),
    max_size_(-1),
    verbose_(false),
    temp_verbose_(false)
{
}

HistoryCollect::~HistoryCollect()
{
}

void HistoryCollect::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  // get/init labels from state record
  rec[FTopLabel].get(top_label_,initializing);
  rec[FInputIndex].get(input_index_,initializing);
  rec[FMaxListSize].get(max_size_,initializing);
  rec[FVerbose].get(verbose_,initializing);
  // reset list if specified
  if( rec[FHistoryList].exists() || initializing )
    rec[FHistoryList].replace() <<= new DMI::List;
}

void HistoryCollect::fillResult (Result::Ref &resref,const DMI::List &list)
{
  if( !resref.valid() )
    resref <<= new Result(0);
  Result & result = resref();
  DMI::Record &toprec = result[top_label_] <<= new DMI::Record;
  toprec[FValue] = list;
}

int HistoryCollect::processCommands (Result::Ref &resref,const DMI::Record &rec,Request::Ref &reqref)
{
  if( rec[CmdGetHistory].as<bool>(false) )
  {
    // if request has a cells field, then our getResult() will be called
    // anyway, so just set a flag instead of filling it in
    if( reqref->hasCells() )
      temp_verbose_ = true;
    else
      fillResult(resref,state()[FHistoryList].as<DMI::List>());
  }
  return 0;
}

int HistoryCollect::getResult (Result::Ref &resref, 
                       const std::vector<Result::Ref> &child_result,
                       const Request &request, bool newreq)
{
  Assert(child_result.size() == 1 );
  const Result &chres = *child_result.front();
  // get item out of child result
  ObjRef ref;
  try
  {
    ref = chres[input_index_].ref();
    if( !ref.valid() )
      Throw("empty item "+input_index_.toString());
  }
  catch( std::exception &exc )
  {
    wstate()[FLastError] = exc.what();
    wstate()[FLastErrorResult].replace() = chres;
  }
  if( ref.valid() )
  {
    // add item to list
    DMI::List & list = wstate()[FHistoryList].as_wr<DMI::List>();
    list.addBack(ref);
    // trim list if a max size is specified
    if( max_size_ > 0 )
    {
      int nr = list.size() - max_size_;
      for( int i=0; i<nr; i++ )
        list.remove(0);
    }
    // if verbose, then add list to result
    if( verbose_ || temp_verbose_ )
      fillResult(resref,list);
  }
  temp_verbose_ = false;
  return 0;
}

} // namespace Meq
