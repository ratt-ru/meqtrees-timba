//# ModRes.cc: modifies request resolutions
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

#include <MeqNodes/ModRes.h>
#include <MEQ/MeqVocabulary.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MEQ/ResampleMachine.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>

namespace Meq {

const HIID FFactor = AidFactor;
const HIID FNumCells = AidNum|AidCells;
const HIID FCacheCells = AidCache|AidCells;
const HIID FCacheRequestId = AidCache|AidRequest|AidId;

//##ModelId=400E5355029C
ModRes::ModRes()
: Node(1), // 1 child expected
  has_ops(false)
{
  // our own result depends on domain & resolution
  const HIID symdeps[] = { FDomain,FResolution };
  setActiveSymDeps(symdeps,2);
  setGenSymDeps(FResolution,RQIDM_RESOLUTION);
}

//##ModelId=400E5355029D
ModRes::~ModRes()
{}

void ModRes::setStateImpl (DataRecord &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  bool new_ops = false;
  // check for resampling factor
  if( rec[FFactor].get_vector(factor) )
  {
    new_ops = true;
    // if a single element, resize and assign to entire vector
    if( factor.size() == 1 )
    {
      factor.resize(DOMAIN_NAXES);
      factor.assign(DOMAIN_NAXES,factor.front());
    }
    else if( factor.size() != DOMAIN_NAXES )
    {
      NodeThrow(FailWithCleanup,"illegal "+FFactor.toString()+" field");
    }
  }
  // check for direct cell number
  if( rec[FNumCells].get_vector(numcells) )
  {
    new_ops = true;
    // if a single element, resize and assign to entire vector
    if( numcells.size() == 1 )
    {
      numcells.resize(DOMAIN_NAXES);
      numcells.assign(DOMAIN_NAXES,numcells.front());
    }
    else if( numcells.size() != DOMAIN_NAXES )
    {
      NodeThrow(FailWithCleanup,"illegal "+FNumCells.toString()+" field");
    }
  }
  // if new ops were specified, recompute the ops array
  if( new_ops )
  {
    // clear the cached cells
    cache_cells_.detach();
    wstate()[FCacheCells].remove();
    wstate()[FCacheRequestId].remove();
    has_ops = false;
    // precompute new Cells constructor arguments
    for( int i=0; i<DOMAIN_NAXES; i++ )
    {
      if( !numcells.empty() && numcells[i] )
      {
        cells_op[i]  = Cells::SET_NCELLS; 
        cells_arg[i] = numcells[i];
        has_ops = true;
      }
      else if( !factor.empty() && factor[i]<1 )
      {
        cells_op[i]  = Cells::INTEGRATE; 
        cells_arg[i] = -factor[i];
        has_ops = true;
      }
      else if( !factor.empty() && factor[i]>1 )
      {
        cells_op[i]  = Cells::UPSAMPLE; 
        cells_arg[i] = factor[i];
        has_ops = true;
      }
      else
        cells_arg[i] = Cells::NONE;
    }
  }
}

int ModRes::pollChildren (std::vector<Result::Ref> &child_results,
                          Result::Ref &resref,
                          const Request &req)
{
  // no cells in request, or no operations configured? Pass everything 
  // on to standard method
  if( !req.hasCells() || !has_ops )
    return Node::pollChildren(child_results,resref,req);
  // create new request as copy of current one
  Request::Ref newref;
  Request &newreq = newref <<= new Request(req);
  // see if we already have a cached cells for this operation
  if( cache_cells_.valid() && maskedCompare(req.id(),cache_rqid_,getDependMask()) )
  {
    newreq.setCells(*cache_cells_);
  }
  else
  {
    // create & cache new cells based on original cells and current 
    // operations array
    const Cells *cells = new Cells(req.cells(),cells_op,cells_arg);
    wstate()[FCacheCells].replace() <<= cells;
    wstate()[FCacheRequestId] = cache_rqid_ = req.id();
    cache_cells_ <<= cells;
    newreq.setCells(cells);
  }
  // increment the resolution-ID in the request
  newreq.setId(incrSubId(req.id(),getGenSymDepMask()));
  // call standard method with the new request
  return Node::pollChildren(child_results,resref,newreq);
} 

int ModRes::getResult (Result::Ref &resref, 
                       const std::vector<Result::Ref> &childres,
                       const Request &,bool)
{
  Assert(childres.size()==1);
  resref.xfer(childres[0]);
  return 0;
}

} // namespace Meq
