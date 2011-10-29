//# TensorFunctionPert.h: Base class for a tensor-aware function with explicit handling of perturbed values
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
//# $Id: TensorFunctionPert.cc 6289 2008-07-28 12:50:27Z oms $

#include <MEQ/TensorFunctionPert.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MEQ/VellSet.h>
#include <MEQ/Vells.h>

namespace Meq {

TensorFunctionPert::TensorFunctionPert (int nchildren,const HIID *labels,int nmandatory)
  : TensorFunction(nchildren,labels,nmandatory)
{
  vp_ = 0;
  nvp_ = 0;
}

TensorFunctionPert::~TensorFunctionPert ()
{
  if( vp_ )
    delete [] vp_;
}

void TensorFunctionPert::computeTensorResult (Result::Ref &resref,
                                     const std::vector<Result::Ref> &childres)
{
  int nchild = childres.size();
  nvs_child_.resize(nchild);
  // find total number of vellsets, and one per child
  int totplanes = 0;
  maxplanes_ = 0;
  for( uint ichild = 0; ichild < nchild; ichild++ )
  {
    int n = childres[ichild]->numVellSets();
    maxplanes_ = std::max(maxplanes_,n);
    totplanes += n;
    nvs_child_[ichild] = n;
  }
  // now we need to collect all vellsets into a flat array, to use the Function::findSpids() method
  pvs_all_.resize(totplanes);
  int iall = 0;
  for( uint ichild=0; ichild<nchild; ichild++ )
  {
    const Result &chres = *(childres[ichild]);
    for( uint i=0; i<chres.numVellSets(); i++ )
      pvs_all_[iall++] = &( chres.vellSet(i) );
  }
  // use findSpids() to compute the total spid set
  int npertsets;
  std::vector<int> all_spids = findSpids(npertsets,pvs_all_);
  // NB: double-differencing is not supported here, so bail out
  FailWhen(npertsets==2,"double-differencing not supported by this node");
  num_spids_  = all_spids.size();

  // allocate pointer array for Vells: NCHILDxNVELLSETSx(1+NPERT)
  int nvp = nchild*maxplanes_*(1+num_spids_);
  // if old array is big enough, do not reallocate
  if( nvp > nvp_ )
  {
    if( vp_ )
      delete [] vp_;
    vp_ = new const Vells *[nvp_=nvp];
  }
  // fill with zeroes
  memset(vp_,0,sizeof(Vells*)*nvp_);
  
  // pert: the perturbation associated with each spid
  std::vector<double> perts(num_spids_);
  // these will indicate the child and vellset at which a spid was first found
  int found_at_child[num_spids_],found_at_vs[num_spids_];
  for( int i=0; i<num_spids_; i++ )
    found_at_child[i] = -1;
  dims_vector_.resize(nchild);
  pvs_vector_.resize(nchild);
  // loop over all children and vellsets to fill in pointers
  for( uint ichild = 0; ichild < nchild; ichild++ )
  {
    const Result &chres = *(childres[ichild]);
    dims_vector_[ichild] = &( chres.dims() );
    // fill in pointers to vellsets, and to main value of each
    CVSPVector &pvs = pvs_vector_[ichild];
    pvs.resize(chres.numVellSets());
    for( int ivs = 0; ivs < chres.numVellSets(); ivs++ )
    {
      const VellSet &vs = chres.vellSet(ivs);
      pvs[ivs] = &vs;
      // fill in pointer to main value (ispid=0)
      vp_[IPTR(ichild,0,ivs)] = &(vs.getValue());
      // and to all perturbations
      // starting position in list
      int ispid = 0;
      for( int j=0; j<vs.numSpids(); j++ )
      {
        int spid = vs.getSpid(j);
        // iterate through list of all spids (which is in increasing order) until we get to this one or beyond
        while( all_spids[ispid] < spid && ispid < num_spids_ )
          ispid++;
        // if we got this one, add pointer to list
        if( ispid < num_spids_ && all_spids[ispid] == spid )
        {
          vp_[IPTR(ichild,ispid+1,ivs)] = &(vs.getPerturbedValue(j));
          // get value of perturbation and check for consistency with previous instances
          if( found_at_child[ispid] < 0 )
          {
            perts[ispid] = vs.getPerturbation(j);
            found_at_child[ispid] = ichild;
            found_at_vs[ispid] = ivs;
          }
          else
          {
            FailWhen(perts[ispid]!=vs.getPerturbation(j),
                ssprintf("perturbation %d for spid %d does not match between child results %d[%d] and %d[%d]",
                  j,all_spids[ispid],found_at_child[ispid],found_at_vs[ispid],
                  ichild,ivs));
          }
        }
      }
    }
  }
  // get result dims. This should also check everything for consistency
  LoShape result_dims = getResultDims(dims_vector_);
  int nvs_result = result_dims.product();
  // init result vellsets
  Result & res = resref <<= new Result(result_dims);
  for( int i=0; i<nvs_result; i++ )
  {
    VellSet & vs = res.setNewVellSet(i,num_spids_);
    if( num_spids_ )
    {
      vs.setSpids(all_spids);
      vs.setPerturbations(perts);
    }
  }
  // call subclass to compute the result
  evaluateTensors(res,num_spids_,nchild);

  // resize output vectors for flags
  flag_vector_.resize(nvs_result);
  for( int i=0; i<nvs_result; i++ )
    flag_vector_[i].detach();

  // now compute flags
  evaluateTensorFlags(flag_vector_,pvs_vector_);

  // verify output vells shapes (this si necessary since evaluateTensors() will not have filled in the shaps properly),
  // and assign flags as needed
  for( int i=0; i<nvs_result; i++ )
  {
    VellSet & vs = res.vellSetWr(i);
    vs.verifyShape();
    if( flag_vector_[i].valid() )
    {
      flag_vector_[i]();
      vs.setDataFlags(flag_vector_[i]);
    }
  }
  // done, phew
}



int TensorFunctionPert::getResult (Result::Ref &resref,
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool)
{
  // compute result cells
  result_cells_.detach();
  computeResultCells(result_cells_,childres,req);

  // fill result
  computeTensorResult(resref,childres);

  // assign cells if available
  if( result_cells_.valid() )
    resref().setCells(*result_cells_);

  return 0;
}

};
