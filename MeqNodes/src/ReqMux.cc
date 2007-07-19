//# ReqMux.cc: resamples result resolutions
//#
//# Copyright (C) 2002-2007
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# and The MeqTree Foundation
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

#include <MeqNodes/ReqMux.h>
#include <MEQ/MeqVocabulary.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MEQ/Cells.h>


namespace Meq {

const HIID FResultIndex = AidResult|AidIndex;

//##ModelId=400E5355029C
ReqMux::ReqMux()
: Node(-2),which_result_(0) // at least one child required
{
  // change default children policies -- we want to ignore errors and pass them on
  children().setFailPolicy(AidIgnore);
  children().setMissingDataPolicy(AidIgnore);
}

//##ModelId=400E5355029D
ReqMux::~ReqMux()
{}

void ReqMux::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  if( rec[FResultIndex].get(which_result_,initializing) )
  {
    FailWhen( which_result_ <0 || which_result_ >= numChildren(),
              "illegal "+FResultIndex.toString()+" value");
  }
}

int ReqMux::pollChildren (Result::Ref &resref,
                          std::vector<Result::Ref> &childres,
                          const Request &req)
{
  // get results from all children using standard method
  int retcode = Node::pollChildren(resref,childres,req);
  // return a cumulative FAIL code as is (we'll only get it if a non-ignore error policy
  // was explicitly set)
  if( retcode&(RES_FAIL|RES_MISSING) )
    return retcode;
  else
    return children().childRetcode(which_result_);
}

int ReqMux::discoverSpids (Result::Ref &resref,
                           const std::vector<Result::Ref> &chres,
                           const Request &)
{
  // only return spids from designated child
  resref = chres[which_result_];
  return 0;
}

int ReqMux::getResult (Result::Ref &resref, 
                       const std::vector<Result::Ref> &chres,
                       const Request &,bool)
{
  resref = chres[which_result_];
  return 0;
}

} // namespace Meq
