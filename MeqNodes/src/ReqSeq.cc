//# ReqSeq.cc: resamples result resolutions
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
//# $Id$

#include <MeqNodes/ReqSeq.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MEQ/Forest.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>


namespace Meq {

const HIID FResultIndex = AidResult|AidIndex;
const HIID FCellsOnly = AidCells|AidOnly;
const HIID FSequenceSymdeps = AidSequence|AidSymdeps;
const HIID FSequenceDependMask = AidSequence|AidDepend|AidMask;


//##ModelId=400E5355029C
ReqSeq::ReqSeq()
: Node(-1,0,1), // at least one child required
  which_result_(0),
  cells_only_(false)
{
  disableAutoResample();
  // init default seq symdeps 
  seq_symdeps_.assign(1,AidSequence);
  setKnownSymDeps(seq_symdeps_);
}

//##ModelId=400E5355029D
ReqSeq::~ReqSeq()
{}

void ReqSeq::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  rec[FCellsOnly].get(cells_only_,initializing);
  if( rec[FResultIndex].get(which_result_,initializing) )
  {
    FailWhen( which_result_ <0 || which_result_ >= numChildren(),
              "illegal "+FResultIndex.toString()+" value");
  }
  // get symdeps
  if( rec[FSequenceSymdeps].get_vector(seq_symdeps_,initializing) || initializing )
    wstate()[FSequenceDependMask] = seq_depmask_ = computeDependMask(seq_symdeps_);
  // now reset the dependency mask if specified; this will override
  // possible modifications made above
  rec[FSequenceDependMask].get(seq_depmask_,initializing);
}


int ReqSeq::pollChildren (std::vector<Result::Ref> &chres,
                          Result::Ref &resref,
                          const Request &req)
{
  setExecState(CS_ES_POLLING);
  // in cells-only mode, process cell-less requests just like a regular Node
  if( cells_only_ && !req.hasCells() )
    return Node::pollChildren(chres,resref,req);
  int retcode = result_code_ = 0;
  cdebug(3)<<"calling execute() on "<<numChildren()<<" children in turn"<<endl;
  Request::Ref reqref(req);
  RequestId rqid = req.id();
  for( int i=0; i<numChildren(); i++ )
  {
    Result::Ref res;
    // increment sequence ID for subsequent children
    if( i )
    {
      RqId::incrSubId(rqid,seq_depmask_);
      reqref().setId(rqid);
    }
    // poll children
    int code = getChild(i).execute(res,*reqref);
    cdebug(4)<<"    child "<<i<<" returns code "<<ssprintf("0x%x",code)<<endl;
    // a wait is returne immediately
    result_code_ |= code;
    if( code&RES_WAIT )
      return result_code_;
    // note that we only cache the result if the request has cells in it,
    // since otherwise our getResult is not called at all
    if( i == which_result_ && req.hasCells() )
    {
      cdebug(3)<<"retaining result of child "<<i<<" with code "<<code<<endl;
      result_ = res;
    }
  }
  pollStepChildren(*reqref);
  return 0;
}



int ReqSeq::getResult (Result::Ref &resref, 
                       const std::vector<Result::Ref> &,
                       const Request &,bool)
{
  // just pass on the result of whatever was cached by pollChildren above
  Assert(result_.valid());
  resref.xfer(result_);
  return result_code_;
}

} // namespace Meq
