//# MatrixInvert22.cc: quick invert of 2x2 matrix
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

#include <MeqNodes/MatrixInvert22.h>

namespace Meq
{


//##ModelId=400E530A0105
MatrixInvert22::MatrixInvert22()
 : Function(1)
{}

//##ModelId=400E530A0106
MatrixInvert22::~MatrixInvert22()
{}

// computes invert
inline void MatrixInvert22::computeInvert (Vells::Ref out[],
      const std::vector<const Vells*> &in,const std::vector<bool> &changed)
{
  const int a=0,b=1,c=2,d=3;
  // recalc intermediates
  if( changed[a] || changed[d] )
    ad_ = (*in[a])*(*in[d]);
  if( changed[b] || changed[c] )
    bc_ = (*in[b])*(*in[c]);
  Vells det = 1/(ad_-bc_);
  Vells mdet = -det;
  // calc final values
  out[a] <<= new Vells( (*in[d])*det );
  out[b] <<= new Vells( (*in[b])*mdet );
  out[c] <<= new Vells( (*in[c])*mdet );
  out[d] <<= new Vells( (*in[a])*det );
}

int MatrixInvert22::getResult (Result::Ref &resref,
                               const std::vector<Result::Ref> &childres,
                               const Request &request,bool)
{
  Assert(childres.size() == 1);
  if( flagmask_.empty() )
    flagmask_.assign(childres.size(),VellsFullFlagMask);
  else
  {
    Assert(flagmask_.size() == childres.size());
  }
  const Result &chres = *childres[0];
  const LoShape &dims = chres.dims();
  // scalar result corresponds to simple inversion
  if( dims.empty() )
  {
    int nvs = chres.numVellSets();
    Assert(nvs==1);
    // copy vellSet to output
    Result &result = resref <<= new Result(1);
    const VellSet &chvs = chres.vellSet(0);
    result.setVellSet(0,&(chvs));
    // if it's a fail, return immediately
    if( chvs.isFail() )
      return RES_FAIL;
    // get writable ref to output VellSet (invokes COW I guess)
    VellSet &vs = result.vellSetWr(0);
    // invert main value
    vs.setValue(1/vs.getValue());
    // invert perturbed values
    for( int ipertset=0; ipertset<vs.numPertSets(); ipertset++)
      for( int ipert=0; ipert<vs.nperturbed(); ipert++)
      {
        const Vells &pertval = vs.getPerturbedValue(ipert,ipertset);
        vs.setPerturbedValue(ipert,1/pertval,ipertset);
      }
  }
  // else do proper 2x2 inversion
  else
  {
    FailWhen(dims.size()!=2 || dims[0]!=2 || dims[1]!=2,"scalar or 2x2 child result expected");
    // since inversion involves all the elements simultaneously, all the
    // spids are going to get mixed in here. So, collect all values
    // into one flat array.
    // Use 'nvs' instead of '4' for future-proffing the code
    int nvs = chres.numVellSets();
    Assert(nvs==4);

    // pointers to each input vellset
    vector<const VellSet *> pvset(nvs);
    vector<const Vells *> pvv(nvs);
    Vells::Ref flagref;
    VellSet::Ref fail_vs(DMI::ANONWR);
    // accumulate flags and pointers to main values
    const Vells *pNull = &(Vells::Null());
    for( int ivs=0; ivs<nvs; ivs++ )
    {
      const VellSet &vs = chres.vellSet(ivs);
      // propagate fails
      if( vs.isFail() )
      { // collect fails from child vellset
        for( int ii=0; ii<vs.numFails(); ii++ )
          fail_vs().addFail(vs.getFail(ii));
      }
      // continue if we have any fails -- gotta accumulate them all
      if( fail_vs->isFail() )
        continue;
      pvset[ivs] = &(vs);
      pvv  [ivs] = vs.hasValue() ? &( vs.getValue() ) : pNull;
      // flags
      if( vs.hasDataFlags() )
        Vells::mergeFlags(flagref,vs.dataFlags(),flagmask_[0]);
    }
    // any fails? return them
    if( fail_vs->isFail() )
    {
      Result &result = resref <<= new Result(1);
      result.setVellSet(0,fail_vs);
      return RES_FAIL;
    }
    // else output has same 2x2 shape
    Result &result = resref <<= new Result(dims);
    // allocate output vellsets and attach flags, if any
    VellSet * outvs[nvs];
    for( int i=0; i<nvs; i++ )
    {
      outvs[i] = &(result.setNewVellSet(i));
      // attach flags to output vellsets
      if( flagref.valid() )
        outvs[i]->setDataFlags(flagref);
    }
    // invert main values
    Vells ad0 = (*pvv[0])*(*pvv[3]);
    Vells bc0 = (*pvv[1])*(*pvv[2]);
    Vells det0 = 1/(ad0-bc0);
    Vells mdet0 = -det0;
    outvs[0]->setValue((*pvv[3])*det0);
    outvs[1]->setValue((*pvv[1])*mdet0);
    outvs[2]->setValue((*pvv[2])*mdet0);
    outvs[3]->setValue((*pvv[0])*det0);
    // work out the output spids
    int npertsets;
    vector<int> spids = findSpids(npertsets,pvset);
    if( !spids.empty() )
    {
      for( int i=0; i<nvs; i++ )
      {
        outvs[i]->setNumPertSets(npertsets);
        outvs[i]->setSpids(spids);
      }
      // Evaluate all perturbed values.
      vector<const Vells*> pert_values[npertsets];
      double pert[npertsets];
      vector<int> indices(nvs,0);
      int found[npertsets];
      vector<bool> changed(nvs);
      for( uint ispid=0; ispid<spids.size(); ispid++)
      {
        // pert_values start with pointers to each child's main value, the
        // loop below then replaces them with values from children that
        // have a corresponding perturbed value
        for( int ipert=0; ipert<npertsets; ipert++ )
        {
          found[ipert] = -1;
          pert_values[ipert] = pvv;
          changed.assign(nvs,false);
        }
        // loop over child vellsets. For every vs that contains a perturbed
        // value for spid[ispid], put a pointer to the perturbed value into
        // pert_values[ipert][ichild]. For children that do not contain a
        // perturbed value, it will retain a pointer to the main value.
        // The pertubations themselves are collected into pert[]; these
        // must match across all children
        for( int ivs=0; ivs<nvs; ivs++ )
          if( pvv[ivs] != pNull )
          {
            const VellSet &vs = *(pvset[ivs]);
            int inx = vs.isDefined(spids[ispid],indices[ivs]);
            if( inx >= 0 )
            {
              changed[ivs] = true;
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
        // now, invert the perturbed matrices
        for( int ipert=0; ipert<npertsets; ipert++ )
        {
          FailWhen(found[ipert]<0,
                   ssprintf("no perturbation set %d found for spid %d",
                            ipert,spids[ispid]));
          for( int i=0; i<nvs; i++ )
            outvs[i]->setPerturbation(ispid,pert[ipert],ipert);
          // recalc
          Vells ad = changed[0] || changed[3]
                ? (*pert_values[ipert][0])*(*pert_values[ipert][3])
                : ad0;
          Vells bc = changed[1] || changed[2]
                ? (*pert_values[ipert][1])*(*pert_values[ipert][2])
                : bc0;
          Vells det = 1/(ad-bc);
          Vells mdet = -det;
          outvs[0]->setPerturbedValue(ispid,(*pert_values[ipert][3])*det,ipert);
          outvs[1]->setPerturbedValue(ispid,(*pert_values[ipert][1])*mdet,ipert);
          outvs[2]->setPerturbedValue(ispid,(*pert_values[ipert][2])*mdet,ipert);
          outvs[3]->setPerturbedValue(ispid,(*pert_values[ipert][0])*det,ipert);
        }
      } // for spids
    }
  }

  // return 0 flag, since we don't add any dependencies of our own
  return 0;
}

} // namespace Meq
