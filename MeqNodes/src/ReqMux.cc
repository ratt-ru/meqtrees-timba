//# ReqMux.cc: resamples result resolutions
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

#include <MeqNodes/ReqMux.h>
#include <MEQ/MeqVocabulary.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MEQ/Cells.h>


namespace Meq {

const HIID FOper = AidOper;
const HIID FUpsample[]  = { AidUpsample |AidFreq, AidUpsample |AidTime };
const HIID FIntegrate[] = { AidIntegrate|AidFreq, AidIntegrate|AidTime };
const HIID FPass = AidPass;
const HIID FWait = AidWait;


//##ModelId=400E5355029C
ReqMux::ReqMux()
: Node(-1,0,1), // at least one child required
  res_depend_mask_(RQIDM_RESOLUTION)
{}

//##ModelId=400E5355029D
ReqMux::~ReqMux()
{}

void ReqMux::setStateImpl (DataRecord &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  // get dependency mask for resolution changes
  rec[FResolutionDependMask].get(res_depend_mask_,initializing);
  // check for operation specs
  int noper = rec[FOper].size(TpDataRecord);
  if( noper )
  {
    std::vector<OpSpec> ops(noper);
    pass_child_ = -1;
    // parse the operation specs
    for( int ich=0; ich<noper; ich++ )
    {
      OpSpec & op = ops[ich];
      const DataRecord &oprec = rec[FOper][ich];
      // get upsample/integrate commands
      for( int i=0; i<DOMAIN_NAXES; i++ )
      {
        bool got1 = oprec[FUpsample [i]].get(op.upsample [i]);
        bool got2 = oprec[FIntegrate[i]].get(op.integrate[i]);
        if( got1 && got2 )
          NodeThrow1("can't specify both upsample and integrate for the same axis");
        op.resample = got1 || got2;
      }
      // get wait and pass commands
      op.wait = oprec[FWait].as<bool>(false);
      if( oprec[FPass].as<bool>(false) )
      {
        if( pass_child_ >= 0 )
          NodeThrow1("'pass' operation can only be enabled for one child");
        pass_child_ = ich;
      }
    }
    // if no errors, assign to ops_
    ops_ = ops;
  }
}


int ReqMux::pollChildren (std::vector<Result::Ref> &child_results,
                          Result::Ref &resref,
                          const Request &req)
{
  if( int(ops_.size()) != numChildren() )
    NodeThrow1("number of "+FOper.toString()+" elements does not match numer of children");
    
    
  int retcode = 0;
  // get components of domain ID
  RequestId rqid = req.id();
  
  // figure out the child requests first
  child_results.resize(numChildren());
  for( int ich=0; ich<numChildren(); ich++ )
  {
    const OpSpec & op = ops_[ich];
    const Request *preq = &req; // pointer to request which will be used for this child
    Request::Ref reqref;
    Request *newreq;      // pointer and ref to new request, if created
    
    newreq=0;
    // do we need to resample the request cells?
    if( req.hasCells() && op.resample )
    {
      // create new request based on current one, attach to ref, set pointer
      if( !newreq )
      {
        reqref <<= preq = newreq = new Request(req);
        // set new request ID, by adding an extra index to the domain ID
        incrSubId(rqid,res_depend_mask_);
        newreq->setId(rqid);
      }
      // create new cells object
      Cells *pc = new Cells;
      Cells::Ref cellsref(pc,DMI::ANONWR);
      for( int iaxis=0; iaxis<DOMAIN_NAXES; iaxis++ )
      {
        int nc = req.cells().ncells(iaxis);
        const LoVec_double & cen0  = req.cells().center(iaxis);
        const LoVec_double & size0 = req.cells().cellSize(iaxis);
        LoVec_double cen,size;
        // upsample along this axis
        if( op.upsample[iaxis] )
        {
          int factor = op.upsample[iaxis];
          cen.resize(nc*factor);
          size.resize(nc*factor);
          int i1=0; // i1 is index of upsampled cell
          for( int i=0; i<nc; i++ )
          {
            double s1 = size0(i)/factor, // size of upsampled cell
              // center of first cell corresponding to original cell i
                   c1 = cen0(i) - size0(i)/2 + s1/2; 
            for( int j=0; j<factor; j++,i1++ )
            {
              cen(i1)  = c1; c1 += s1;
              size(i1) = s1; 
            }
          }
        }
        // integrate along this axis
        else if( op.integrate[iaxis] )
        {
          int factor = op.integrate[iaxis];
          int nc1 = nc/factor;
          cen.resize(nc1);
          size.resize(nc1);
          int i0=0; 
          for( int i=0; i<nc1; i++)
          {
            // x1 is start of first cell in integrated block
            double x1 = cen0(i0) - size0(i0)/2;
            i0 += factor;
            // x2 is end of last cell in integrated block
            double x2 = cen0(i0-1) + size0(i0-1)/2;
            cen(i)  = (x1+x2)/2;
            size(i) = x2-x1;
          }
        }
        else
        {
          cen.reference(cen0);
          size.reference(size0);
        }
        pc->setCells(iaxis,cen,size);
        pc->recomputeSegments(iaxis);
      }
      pc->recomputeDomain();
      newreq->setCells(pc);
    }
    // no other operations yet -- just reused the parent request
     
    // get child result
    int code = getChild(ich).execute(child_results[ich],*preq);
    // ***** NB: gotta do something about RES_WAIT here
    
    // if this is the pass-through child result, set return value to
    // its return code
    if( ich == pass_child_ )
      retcode = code;
  }
  return retcode;
}



int ReqMux::getResult (Result::Ref &resref, 
                       const std::vector<Result::Ref> &childres,
                       const Request &,bool)
{
  // getResult is very simple -- just pass on the result of whichever
  // child was configured with the pass option (see above)
  if( pass_child_>=0 )
  {
    Assert(pass_child_<int(childres.size()));
    resref = childres[pass_child_];
  }
  else
    resref <<= new Result;
  // no additional dependencies. Note that the child's code has already been
  // returned by pollChildren(), above
  return 0;
}

} // namespace Meq
