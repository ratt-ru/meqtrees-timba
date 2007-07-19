//# ReqSeq.cc: resamples result resolutions
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


//##ModelId=400E5355029C
ReqSeq::ReqSeq()
: Node(-2), // at least one child required
  which_result_(0),
  cells_only_(false)
{
  // change default children policies -- we want to ignore errors and pass them on
  children().setFailPolicy(AidIgnore);
  children().setMissingDataPolicy(AidIgnore);
  // init default seq symdeps 
  seq_symdeps_.resize(1);
  seq_symdeps_.assign(1,AidState);
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
  rec[FSequenceSymdeps].get_vector(seq_symdeps_,initializing);
}


int ReqSeq::pollChildren (Result::Ref &resref,
                          std::vector<Result::Ref> &childres,
                          const Request &req)
{
  seq_depmask_ = symdeps().getMask(seq_symdeps_);
  resref.detach();
  // in cells-only mode, process cell-less requests just like a regular Node
  if( cells_only_ && !req.hasCells() )
    return Node::pollChildren(resref,childres,req);
  setExecState(CS_ES_POLLING);
  timers().children.start();
  int retcode = result_code_ = 0;
  cdebug(3)<<"calling execute() on "<<numChildren()<<" children in turn"<<endl;
  Request::Ref reqref(req);
  RequestId rqid = req.id();
  for( int ichild=0; ichild<numChildren(); ichild++ )
  {
    Result::Ref child_res;
    // increment sequence ID for subsequent children
    if( ichild && seq_depmask_ )
    {
      RqId::incrSubId(rqid,seq_depmask_);
      reqref().setId(rqid);
    }
    // poll current child
    unlockStateMutex();
    int code = children().getChild(ichild).execute(child_res,*reqref);
    lockStateMutex();
    cdebug(4)<<"    child "<<ichild<<" returns code "<<ssprintf("0x%x",code)<<endl;
    if( forest().abortFlag() )
      return RES_ABORT;
    // a wait is returned immediately
    if( code&RES_WAIT )
    {
      timers().children.stop();
      return result_code_;
    }
    // handle child fail according to mode
    if( code&RES_FAIL )
    {
      // if fail policy is Ignore, ignore fails from non-selected children 
      if( children().failPolicy() == AidIgnore )
      {
        if( ichild != which_result_ )
          code &= ~RES_FAIL;
      }
      else // else return error directly
      {
        resref.xfer(child_res);
        timers().children.stop();
        return result_code_|code;
      }
    }
    // handle missing data according to current mode
    if( code&RES_MISSING )
    {
      // if fail policy is Ignore, ignore fails from non-selected children 
      if( children().missingDataPolicy() == AidIgnore )
      {
        if( ichild != which_result_ )
          code &= ~RES_MISSING;
      }
      else // else return error directly
      {
        resref.xfer(child_res);
        timers().children.stop();
        return result_code_|code;
      }
    }
    // merge return value into result
    result_code_ |= code;
    // note that we only cache the result if the request has cells in it,
    // since otherwise our getResult is not called at all
    if( ichild == which_result_ && req.hasCells() )
    {
      cdebug(3)<<"retaining result of child "<<ichild<<" with code "<<code<<endl;
      result_ = child_res;
    }
  }
  unlockStateMutex();
  stepchildren().backgroundPoll(*reqref);
  timers().children.stop();
  lockStateMutex();
  return 0;
}

int ReqSeq::discoverSpids (Result::Ref &ref,
                         const std::vector<Result::Ref> &,
                         const Request &)
{
  // ignore child results since we don't keep any, but return the result
  // we were holding from the active child
  ref.xfer(result_);
  return result_code_;
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
