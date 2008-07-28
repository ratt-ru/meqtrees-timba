//# MatrixMultiply.cc: Multiply 2 or more matrix results
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

#include <MeqNodes/MatrixMultiply.h>

namespace Meq
{


//##ModelId=400E530A0105
MatrixMultiply::MatrixMultiply()
 : Function(-2) // at least 1 child expected
{}

//##ModelId=400E530A0106
MatrixMultiply::~MatrixMultiply()
{}

inline Vells * computeSum (Vells &out,const Vells * pv[],int nsum)
{
  int j=0;
  for( int i=0; i<nsum; i++ )
  {
    const Vells *pa = pv[j++];
    const Vells *pb = pv[j++];
    if( pa && pb )
      out += (*pa)*(*pb);
  }
  return &out;
}

// multiplies a scalar result by a tensor result
void MatrixMultiply::scalarMultiply (Result::Ref &res,
    const Result &scalar,const Result &tensor,
    VellsFlagType fms,VellsFlagType fmt,
    int tensor_ich)
{
  // for consistency, refuse to have anything to do with >2 rank tensors
  FailWhen(tensor.tensorRank()>2,ssprintf(
                    "child %d: illegal tensor rank",tensor_ich));
  // empty result: treat as null
  if( !scalar.numVellSets() )
  {
    (res <<= new Result(1)).setNewVellSet(0);
    return;
  }
  const VellSet & sca_vs = scalar.vellSet(0);
  // check for some quick shortcuts
  // fail scalar: return it
  if( sca_vs.isFail() )
  {
    (res <<= new Result(1)).setVellSet(0,sca_vs);
    return;
  }
  // empty scalar vellset: return empty result
  if( !sca_vs.hasValue() )
  {
    (res <<= new Result(1)).setNewVellSet(0);
    return;
  }
  const Vells & sca_val = sca_vs.getValue();
  if( !sca_vs.numSpids() )
  {
    // null scalar and no perturbations: return null Vells without flags
    // (flags swallowed by null values...)
    if( sca_val.isNull() )
    {
      (res <<= new Result(1)).setNewVellSet(0).setValue(new Vells);
      return;
    }
    // unity and no perturbations: return tensor itself, applying flags
    if( sca_val.isUnity() )
    {
      res.attach(tensor);
      if( sca_vs.hasDataFlags() && fms || fmt != VellsFullFlagMask )
      {
        for( int i=0; i<res->numVellSets(); i++ )
        {
          Vells::Ref flags;
          const VellSet &vs0 = res->vellSet(i);
          if( vs0.hasDataFlags() && !vs0.isNull() )
            Vells::mergeFlags(flags,vs0.dataFlags(),fmt);
          if( sca_vs.hasDataFlags() ) // not a null in this case
            Vells::mergeFlags(flags,sca_vs.dataFlags(),fms);
          if( flags.valid() && !vs0.sameDataFlags(flags) )
            res().vellSetWr(i).setDataFlags(flags);
        }
      }
      return;
    }
  }
  // ok, no such luck, so we need to work out a full result
  Result &result = res <<= new Result(tensor.dims());
  // use cell shape for result shape, most subclasses will ignore it anyway
  // and let vells math determine the shape instead
  vector<const VellSet*> child_vs(2);
  vector<const Vells*>   pvv(2);
  child_vs[1] = &sca_vs;
  pvv[1] = &sca_val;
  int nplanes = result.numVellSets();
  for( int ivs = 0; ivs < nplanes; ivs++ )
  {
    const VellSet &tvs = tensor.vellSet(ivs);
    // if no value in tensor element (i.e. fail or missing), copy to output
    // and go on to next one
    if( !tvs.hasValue() )
    {
      result.setVellSet(ivs,tvs);
      continue;
    }
    child_vs[0] = &tvs;
    // create a vellset for this plane
    VellSet &vellset = result.setNewVellSet(ivs,0,0);
    // compute main value
    pvv[0] = &(tvs.getValue());
    Vells::Ref valref(pvv[0]);
    valref() *= sca_val;
    vellset.setValue(valref);
    // combine flags if present and values are not null
    if( !sca_vs.isNull() && !tvs.isNull() )
    {
      Vells::Ref flags;
      if( sca_vs.hasDataFlags() )
        Vells::mergeFlags(flags,sca_vs.dataFlags(),fms);
      if( tvs.hasDataFlags() )
        Vells::mergeFlags(flags,tvs.dataFlags(),fmt);
      if( flags.valid() )
        vellset.setDataFlags(flags);
    }
    // now figure out perturbed values
    int npertsets;
    vector<int> spids = findSpids(npertsets,child_vs);
    // allocate new vellset object with given number of spids, add to set
    vellset.setNumPertSets(npertsets);
    vellset.setSpids(spids);
    // Evaluate all perturbed values.
    vector<const Vells*> pert_values[npertsets];
    double pert[npertsets];
    int found[npertsets];
    int indices[2] = {0,0};
    for( uint ispid=0; ispid<spids.size(); ispid++)
    {
      // pert_values start with pointers to each child's main value, the
      // loop below then replaces them with values from children that
      // have a corresponding perturbed value
      for( int ipert=0; ipert<npertsets; ipert++ )
      {
        found[ipert] = -1;
        pert_values[ipert] = pvv;
      }
      // loop over children. For every child that contains a perturbed
      // value for spid[j], put a pointer to the perturbed value into
      // pert_values[ipert][ichild]. For children that do not contain a
      // perturbed value, it will retain a pointer to the main value.
      // The pertubations themselves are collected into pert[]; these
      // must match across all children
      for( int ich=0; ich<2; ich++ )
      {
        const VellSet &vs = *(child_vs[ich]);
        int inx = vs.isDefined(spids[ispid],indices[ich]);
        if( inx >= 0 )
        {
          for( int ipert=0; ipert<std::max(vs.numPertSets(),npertsets); ipert++ )
          {
            const Vells &pvv = vs.getPerturbedValue(inx,ipert);
            pert_values[ipert][ich] = &pvv;
            if( found[ipert] >=0 )
            {
              FailWhen(pert[ipert]!=vs.getPerturbation(inx,ipert),
                  ssprintf("perturbation %d for spid %d does not match between child results %d and %d",
                    ipert,spids[ispid],found[ipert],ich));
            }
            else
            {
              pert[ipert] = vs.getPerturbation(inx,ipert);
              found[ipert] = ich;
            }
          }
        }
      }
      // now do multiplication to obtain the perturbed values of the function
      for( int ipert=0; ipert<npertsets; ipert++ )
      {
        FailWhen(found[ipert]<0,
                 ssprintf("no perturbation set %d found for spid %d",
                          ipert,spids[ispid]));
        vellset.setPerturbation(ispid,pert[ipert],ipert);
        Vells::Ref valref(pert_values[ipert][0]);
        valref() *= *(pert_values[ipert][1]);
        vellset.setPerturbedValue(ispid,valref,ipert);
      }
    } // end for(ispid)
  } // end for(ivs)
}

int MatrixMultiply::getResult (Result::Ref &resref,
                               const std::vector<Result::Ref> &childres,
                               const Request &request,bool)
{
  int nrch = childres.size();
  if( flagmask_.empty() )
    flagmask_.assign(childres.size(),VellsFullFlagMask);
  else
  {
    Assert(flagmask_.size() == childres.size());
  }
  Assert( nrch>1 );
  resref = childres[0];
  VellsFlagType fm0 = flagmask_[0];
  // apply flagmask to first child
  if( fm0 != VellsFullFlagMask )
  {
    for( int i=0; i<resref->numVellSets(); i++ )
      if( resref().vellSet(i).hasDataFlags() )
      {
        VellSet &vs = resref().vellSetWr(i);
        vs.setDataFlags(new Vells(vs.dataFlags()&fm0));
      }
  }
  // process one child at a time, multiplying sequentially. Current
  // result is attached to resref.
  for( int ich=1; ich<nrch; ich++ )
  {
    Result::Ref resref1;
    const Result &arga = *resref;
    const Result &argb = *childres[ich];
    VellsFlagType fm = flagmask_[ich];
    // fall back to scalar multiplication if either argument is scalar
    if( !arga.tensorRank() )
      scalarMultiply(resref1,arga,argb,VellsFullFlagMask,fm,ich);
    else if( !argb.tensorRank() )
      scalarMultiply(resref1,argb,arga,fm,VellsFullFlagMask,ich-1);
    else
    {
      // figure out tensor dimensions
      LoShape da,db;
      switch( arga.tensorRank() )
      {
        case 1: da = LoShape(arga.numVellSets(),1); break;
        case 2: da = arga.dims(); break;
        default: Throw(ssprintf(
                    "child %d: illegal tensor rank",ich-1));
      }
      switch( argb.tensorRank() )
      {
        case 1: db = LoShape(argb.numVellSets(),1); break;
        case 2: db = argb.dims(); break;
        default: Throw(ssprintf(
                    "child %d: illegal tensor rank",ich));
      }
      // check for matching dims
      FailWhen(da[1] != db[0],
               ssprintf("matrix dimensions of child %d incompatible with previous child",ich));
      // setup output result
      Result *pres;
      if( db[1] == 1 )
        resref1 <<= pres = new Result(da[0]); // vector or scalar result
      else
        resref1 <<= pres = new Result(LoShape(da[0],db[1]));
      // attach it to ref to ensure cleanup on exception
      int iplane = 0;
      int nsum = da[1]; // number of indices summed over
      // these vectors will hold pointers to values for each summation
      // (A/B values alternating)
      const Vells * pvv[nsum*2];
      // pointers to each vellset in the sum
      vector<const VellSet *> pvset(nsum*2);
      // compute matrix multiplication as Cik = sum( Aij*Bjk )
      for( int i=0; i<da[0]; i++ )
      {
        for( int k=0; k<db[1]; k++,iplane++ )
        {
          // however, for every output vellset we also need to compute
          // multiplication for perturbed values, so this is gonna get hairy
          // (and borrow heavily from Function.cc)
          VellSet &vellset = pres->setNewVellSet(iplane,0,0);
          // figure out which vells will be summed, accumulate flags
          int ja = i*da[1]; // index of (i,*) element of A
          int jb = k;       // index of (*,k) element of B
          int nvs = 0;
          Vells::Ref flagref;
          for( int j=0; j<nsum; j++,ja++,jb+=db[1] )
          {
            const VellSet &vsa = arga.vellSet(ja);
            const VellSet &vsb = argb.vellSet(jb);
            // propagate fails
            if( vsa.isFail() || vsb.isFail() )
            { // collect fails from child vellset
              for( int ii=0; ii<vsa.numFails(); ii++ )
                vellset.addFail(vsa.getFail(ii));
              for( int ii=0; ii<vsb.numFails(); ii++ )
                vellset.addFail(vsb.getFail(ii));
            }
            // continue if we have any fails -- gotta accumulate them all
            if( vellset.isFail() )
              continue;
            pvset[nvs]   = &(vsa);
            pvv  [nvs++] = vsa.hasValue() ? &( vsa.getValue() ) : 0;
            pvset[nvs]   = &(vsb);
            pvv  [nvs++] = vsb.hasValue() ? &( vsb.getValue() ) : 0;
            // flags
            if( !vsa.isNull() && !vsb.isNull() )
            {
              if( vsa.hasDataFlags() )
                Vells::mergeFlags(flagref,vsa.dataFlags(),VellsFullFlagMask);
              if( vsb.hasDataFlags() )
                Vells::mergeFlags(flagref,vsb.dataFlags(),fm);
            }
          }
          // if output is a fail, go to next element
          if( vellset.isFail() )
            continue;
          if( flagref.valid() )
            vellset.setDataFlags(flagref);
          // now compute the sum
          Vells::Ref valref(DMI::ANONWR);
          vellset.setValue(computeSum(valref(),pvv,nsum));
          // now repeat this whole rigamole for perturbed values
          // work out the spids first
          int npertsets;
          vector<int> spids = findSpids(npertsets,pvset);
          // allocate perturbations in output vellset
          vellset.setNumPertSets(npertsets);
          vellset.setSpids(spids);
          // Evaluate all perturbed values.
          const Vells* pert_values[npertsets][nsum*2];
          double pert[npertsets];
          vector<int> indices(nvs,0);
          int found[npertsets];
          for( uint ispid=0; ispid<spids.size(); ispid++)
          {
            // pert_values start with pointers to each child's main value, the
            // loop below then replaces them with values from children that
            // have a corresponding perturbed value
            for( int ipert=0; ipert<npertsets; ipert++ )
            {
              found[ipert] = -1;
              memcpy(pert_values[ipert],pvv,sizeof(pvv));
            }
            // loop over child vellsets. For every vs that contains a perturbed
            // value for spid[ispid], put a pointer to the perturbed value into
            // pert_values[ipert][ichild]. For children that do not contain a
            // perturbed value, it will retain a pointer to the main value.
            // The pertubations themselves are collected into pert[]; these
            // must match across all children
            for( int ivs=0; ivs<nvs; ivs++ )
            // only consider vellsets that have a main value (the other
            // are nulls by definition)
              if( pvv[ivs] )
              {
                const VellSet &vs = *(pvset[ivs]);
                int inx = vs.isDefined(spids[ispid],indices[ivs]);
                if( inx >= 0 )
                {
                  for( int ipert=0; ipert<std::max(vs.numPertSets(),npertsets); ipert++ )
                  {
                    const Vells &pvv = vs.getPerturbedValue(inx,ipert);
                    pert_values[ipert][ivs] = &pvv;
                    if( found[ipert] >=0 )
                    {
                      FailWhen(pert[ipert]!=vs.getPerturbation(inx,ipert),
                          ssprintf("perturbation %d for spid %d does not match between child results %d and %d",
                            ipert,spids[ispid],found[ipert],ivs));
                    }
                    else
                    {
                      pert[ipert] = vs.getPerturbation(inx,ipert);
                      found[ipert] = ivs;
                    }
                  }
                }
              }
            // now, call computeSum() on the pert_values vectors to obtain the
            // perturbed values of the function
            for( int ipert=0; ipert<npertsets; ipert++ )
            {
              FailWhen(found[ipert]<0,
                       ssprintf("no perturbation set %d found for spid %d",
                                ipert,spids[ispid]));
              vellset.setPerturbation(ispid,pert[ipert],ipert);
              Vells &out = valref <<= new Vells;
              vellset.setPerturbedValue(ispid,computeSum(out,pert_values[ipert],nsum),ipert);
            }
          } // for spids
        } // for j
      } // for i
    } // else (end of proper multiplication case)
    // store result in resref and possibly go back for another loop
    resref = resref1;
    // drop out with a fail if the multiplication was a total fail
    if( resref->numFails() == resref->numVellSets() )
      return RES_FAIL;
  } // end of loop over children

   // return 0 flag, since we don't add any dependencies of our own
  return 0;
}

} // namespace Meq
