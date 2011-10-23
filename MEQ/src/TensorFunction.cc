//# TensorFunction.cc: Base class for a tensor-aware function (i.e. where operations are no just plane-by-plane)

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

#include <MEQ/TensorFunction.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MEQ/VellSet.h>
#include <MEQ/Vells.h>

namespace Meq {

TensorFunction::TensorFunction (int nchildren,const HIID *labels,int nmandatory)
  : Function(nchildren,labels,nmandatory)
{}

TensorFunction::~TensorFunction ()
{
}

void TensorFunction::computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &childres,const Request &request)
{
  // figure out if we have a cells from any child, use first one
  for( uint i=0; i<childres.size(); i++ )
    if( childres[i]->hasCells() )
    {
      ref.attach(childres[i]->cells());
      return;
    }
  // if none, try request cells
  if( request.hasCells() )
    ref.attach(request.cells());
}

LoShape TensorFunction::getResultDims (const vector<const LoShape *> &)
{
  return LoShape();
}


void TensorFunction::evaluateTensorFlags (
        std::vector<Vells::Ref> & out_flags,
        const std::vector<std::vector<const VellSet *> > &pvs )
{
  uint nchild = pvs.size();
  // ensure flagmask is same size as number of children
  if( flagmask_.empty() )
    flagmask_.resize(nchild);
  else
  {
    Assert(flagmask_.size() == nchild);
  }
  // compute merged child flags, and merge them all into one output pile
  Vells::Ref out;
  for( uint ichild = 0; ichild < nchild; ichild++ )
  {
    Vells::Ref child_flags;
    if( flagmask_[ichild] )
    {
      for( uint i=0; i<pvs[ichild].size(); i++ )
        if( pvs[ichild][i] && !pvs[ichild][i]->isNull() && pvs[ichild][i]->hasDataFlags() )
          Vells::mergeFlags(child_flags,pvs[ichild][i]->dataFlags(),flagmask_[ichild]);
    }
    if( child_flags.valid() )
      if( out.valid() )
        out() |= *child_flags;
      else
        out = child_flags;
  }
  // now merge into outputs
  if( out.valid() )
    for( uint i = 0; i < out_flags.size(); i++ )
      if( out_flags[i].valid() )
        out_flags[i]() |= *out;
      else
        out_flags[i] = out;
}

void TensorFunction::computeTensorResult (Result::Ref &resref,
                                     const std::vector<Result::Ref> &childres)
{
  uint nchild = childres.size();
  pvs_vector_.resize(nchild);
  dims_vector_.resize(nchild);
  mainval_vector_.resize(nchild);
  index_vector_.resize(nchild);
  int total_vellsets = 0;
  // collect pointers to child results, check them along the way
  for( uint ichild = 0; ichild < nchild; ichild++ )
  {
    const Result &chres = *(childres[ichild]);
    // get integrated property
    // get dimensions
    const LoShape & dims = chres.dims();
    dims_vector_[ichild] = &dims;
    // get vellsets
    CVPVector &mvp = mainval_vector_[ichild];
    CVSPVector &pvs = pvs_vector_[ichild];
    int nvs = chres.numVellSets();
    total_vellsets += nvs;
    pvs.resize(nvs);
    mvp.resize(nvs);
    index_vector_[ichild].resize(nvs);
    index_vector_[ichild].assign(nvs,0);
    // fill in pointers to vellsets, and to main value of each
    for( int ivs = 0; ivs < chres.numVellSets(); ivs++ )
    {
      const VellSet &vs = chres.vellSet(ivs);
      pvs[ivs] = &vs;
      mvp[ivs] = &( vs.getValue() );
    }
  }
  // get result dims. This should also check everything for consistency
  LoShape result_dims = getResultDims(dims_vector_);
  int nvs_result = result_dims.product();
  // resize output vectors
  resval_vector_.resize(nvs_result);
  flag_vector_.resize(nvs_result);
  for( int i=0; i<nvs_result; i++ )
    flag_vector_[i].detach();

  // now compute main value and flags
  evaluateTensors(resval_vector_,mainval_vector_);
  evaluateTensorFlags(flag_vector_,pvs_vector_);

  // now we need to collect all vellsets into a flat array, to use
  // the findSpids() function
  pvs_all_.resize(total_vellsets);
  int iall = 0;
  for( uint ichild=0; ichild<nchild; ichild++ )
  {
    CVSPVector &pvs = pvs_vector_[ichild];
    for( uint i=0; i<pvs.size(); i++ )
      pvs_all_[iall++] = pvs[i];
  }
  // use findSpids() to compute the total spid set
  int npertsets;
  std::vector<int> spids = findSpids(npertsets,pvs_all_);

  // construct result and assign main values and flags to it
  Result &result = resref <<= new Result(result_dims);
  for( int ivs=0; ivs<nvs_result; ivs++ )
  {
    VellSet &vs = result.setNewVellSet(ivs,0,0);
    vs.setValue(resval_vector_[ivs]);
    if( flag_vector_[ivs].valid() )
    {
      flag_vector_[ivs]();
      vs.setDataFlags(flag_vector_[ivs]);
    }
    vs.setNumPertSets(npertsets);
    vs.setSpids(spids);
  }

  // now loop over all spids to compute perturbed values
  pert_vectors_.resize(npertsets);
  // these three arrays contain the search status as we lookup each spid;
  // they're basically meant to check that the perturbations for each spid
  // are consistent across all child results defining that spid
  // pert: the perturbation associated with this spid/perturbation set
  double pert[npertsets];
  // the child number at which this spid was found for the first time
  int    found_at_child[npertsets];
  // the vellset number (within the child) at which this spid was found
  int    found_at_vs[npertsets];
  for( uint ispid=0; ispid<spids.size(); ispid++ )
  {
    for( int ipert=0; ipert<npertsets; ipert++ )
      found_at_child[ipert] = -1;
    // pert_values start with pointers to each child's main value, the
    // loop below then replaces them with values from children that
    // have a corresponding perturbed value
    pert_vectors_.assign(npertsets,mainval_vector_);
    // loop over children. For every child that contains a perturbed
    // value for spid[ispid], put a pointer to the perturbed value into
    // pert_values[ipert][ichild]. For children that do not contain a
    // perturbed value, it will retain a pointer to the main value.
    // The pertubations themselves are collected into pert[]; these
    // must match across all children
    for( uint ichild=0; ichild<nchild; ichild++ )
    {
      std::vector<const VellSet *> &pvs = pvs_vector_[ichild];
      uint nvs = pvs.size();
      for( uint ivs = 0; ivs < nvs; ivs++ )
      {
        const VellSet &vs = *pvs[ivs];
        int inx = vs.isDefined(spids[ispid],index_vector_[ichild][ivs]);
        if( inx >= 0 )
        {
          for( int ipert=0; ipert<std::max(vs.numPertSets(),npertsets); ipert++ )
          {
            const Vells &pvv = vs.getPerturbedValue(inx,ipert);
            pert_vectors_[ipert][ichild][ivs] = &pvv;
            if( found_at_child[ipert] >=0 )
            {
              FailWhen(pert[ipert]!=vs.getPerturbation(inx,ipert),
                  ssprintf("perturbation %d for spid %d does not match between child results %d[%d] and %d[%d]",
                    ipert,spids[ispid],found_at_child[ipert],found_at_vs[ipert],
                    ichild,ivs));
            }
            else
            {
              pert[ipert] = vs.getPerturbation(inx,ipert);
              found_at_child[ipert] = ichild;
              found_at_vs[ipert] = ivs;
            }
          }
        }
      }
    }
    // now, call evaluate() on the pert_values vectors to obtain the
    // perturbed values of the function
    for( int ipert=0; ipert<npertsets; ipert++ )
    {
      FailWhen(found_at_child[ipert]<0,
               ssprintf("spid %d, perturbation set %d: no value found",
                        ipert,spids[ispid]));
      evaluateTensors(resval_vector_,pert_vectors_[ipert]);
      for( int ivs=0; ivs<nvs_result; ivs++ )
      {
        VellSet &vs = result.vellSetWr(ivs);
        vs.setPerturbation(ispid,pert[ipert],ipert);
        vs.setPerturbedValue(ispid,resval_vector_[ivs],ipert);
      }
    }
  } // end for(ispid) over spids

  // done, phew
}



int TensorFunction::getResult (Result::Ref &resref,
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
