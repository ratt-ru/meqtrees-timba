//# Function.cc: Base class for an expression node
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

#include "Function.h"
#include "Request.h"
#include "MeqVocabulary.h"

namespace Meq {

using Debug::ssprintf;

//##ModelId=3F86886E03C5
Function::Function(int nchildren,const HIID *labels,int nmandatory)
  : Node(nchildren,labels,nmandatory),
    enable_flags_(true),force_integrated_(false)
{
  setAutoResample(RESAMPLE_FAIL);
}

//##ModelId=3F86886E03D1
Function::~Function()
{}

//##ModelId=400E53070274
TypeId Function::objectType() const
{
  return TpMeqFunction;
}


void Function::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  // check if we have an explicit integrated property for result
  force_integrated_ = rec[FIntegrated].get(integrated_);
  // get [vector of] flag masks
  vector<int> fm;
  if( rec[FFlagMask].get_vector(fm) )
  {
    enable_flags_ = true;
    // single element? 
    if( fm.size() == 1 )
    {
      int flag = fm.front();
      if( flag == -1 )        // [-1] means full mask (i.e. disable masking completely)
        flagmask_.clear();    //      this is indicated by clearing the vector
      else if( flag == 0 )    // [0] means no flags on output
        enable_flags_ = false;
      else                    // [M] same mask for all elements
        flagmask_.assign(numChildren(),flag);
    }
    else // must have Nchildren masks
    {
      if( fm.size() != uint(numChildren()) )
        NodeThrow1("size of "+FFlagMask.toString()+" vector does not match number of children");
      flagmask_ = fm;
    }
  }
}

void Function::evaluateFlags (Vells::Ref &out,const Request &,const LoShape &,const vector<const Vells*> &pchf)
{
  for( uint i=0; i<pchf.size(); i++ )
    if( pchf[i] )
      if( out.valid() )
        out() |= *(pchf[i]);
      else
        out <<= pchf[i];
}

//##ModelId=3F86886E03DD
int Function::getResult (Result::Ref &resref,
                         const std::vector<Result::Ref> &childres,
                         const Request &request,bool)
{
  int nrch = numChildren();
  Assert(flagmask_.empty() || flagmask_.size() == childres.size());
// 30/01/05 OMS: remove these locks for now: usage of COW refs everywhere 
// makes them unnecessary. If our thread holds a ref to the object, it's 
// guranteed to not change under us thanks to COW.
//  std::vector<Thread::Mutex::Lock> child_reslock(numChildren());
//  lockMutexes(child_reslock,childres);
//  std::vector<Thread::Mutex::Lock> childvs_lock(nrch);
//  std::vector<Thread::Mutex::Lock> childval_lock(nrch);
//  std::vector<Thread::Mutex::Lock> childpvv_lock[2];
//  childpvv_lock[0].resize(nrch);
//  childpvv_lock[1].resize(nrch);

  // check that resolution match. Also, figure out the max number of 
  // child planes, and figure out if result should be marked as integrated.
  // If no children, assume one plane.
  int nplanes = 1;
  bool integr = false;
  if( nrch )
  {
    childres[0]->numVellSets();   // max # of planes in children
    bool integr = childres[0]->isIntegrated();  // flag: is any child integrated
    for( int i=1; i<nrch; i++ )
    {
      nplanes = std::max(nplanes,childres[i]->numVellSets());
      integr |= childres[i]->isIntegrated();
    }
    // override the integrated flag if the state record provides one
  }
  if( force_integrated_ )
    integr = integrated_;
  // Create result and attach to the ref that was passed in
  Result & result = resref <<= new Result(nplanes,integr);
  // Use cells of first child (they all must be the same anyway, we'll verify
  // at least shapes later on). If no children, use request cells.
  const Cells *pcells = 0;
  LoShape res_shape;
  // fill cells from children, else from request
  for( int i=0; i<nrch; i++ )
    if( childres[0]->hasCells() )
    {
      pcells = &( childres[0]->cells() );
      break;
    }
  if( !pcells && request.hasCells() )
    pcells = &( request.cells() );
  // fill cells and shape accordingly
  if( pcells )
  {
    result.setCells(pcells);
    res_shape = pcells->shape();
  }
  vector<const VellSet*> child_vs(nrch);
  vector<const Vells*>  values(nrch);
  vector<const Vells*>  flags(nrch);
  int nfails = 0;
  for( int iplane = 0; iplane < nplanes; iplane++ )
  {
    // create a vellset for this plane
    VellSet &vellset = result.setNewVellSet(iplane,0,0);
    // collect vector of pointers to child vellsets #iplane, and a vector of 
    // pointers to their main values. If a child has fewer vellsets, generate 
    // a fail -- unless the child returned exactly 1 vellset, in which
    // case it is reused repeatedly. If any child vellsets are fails, collect 
    // them for propagation
    for( int i=0; i<nrch; i++ )
    {
      int nvs = childres[i]->numVellSets();
      if( nvs != 1 && iplane >= nvs )
      {
        MakeFailVellSet(vellset,ssprintf("child %d: only %d vellsets",i,nvs));
      }
      else 
      {
        child_vs[i] = &( childres[i]->vellSet(nvs==1?0:iplane) );
//        childvs_lock[i].relock(child_vs[i]->mutex());
        if( child_vs[i]->isFail() ) 
        { // collect fails from child vellset
          for( int j=0; j<child_vs[i]->numFails(); j++ )
            vellset.addFail(&child_vs[i]->getFail(j));
        }
        else
        {
          flags[i] = child_vs[i]->hasDataFlags() ? &(child_vs[i]->dataFlags()) : 0;
          const Vells &val = child_vs[i]->getValue();
//          childval_lock[i].relock(val.mutex());
          FailWhen(!val.isCompatible(res_shape),"mismatch in child result shapes");
          values[i] = &val;
        }
      }
    }
    // continue evaluation only if no fails popped up
    if( !vellset.isFail() )
    {
      // catch exceptions during evaluation and stuff them into fails
      try
      {
        // Find all spids from the children.
        int npertsets;
        vector<int> spids = findSpids(npertsets,child_vs);
        // allocate new vellset object with given number of spids, add to set
        vellset.setNumPertSets(npertsets);
        vellset.setSpids(spids);
        // Evaluate flags
        Vells::Ref flagref;
        evaluateFlags(flagref,request,res_shape,flags);
        if( flagref.valid() )
        {
          flagref().makeNonTemp();
          vellset.setDataFlags(flagref);
        }
        // Evaluate the main value.
        vellset.setValue(evaluate(request,res_shape,values).makeNonTemp());
        // Evaluate all perturbed values.
        vector<vector<const Vells*> > pert_values(npertsets);
        vector<double> pert(npertsets);
        vector<int> indices(nrch,0);
        vector<int> found(npertsets);
        for( uint j=0; j<spids.size(); j++) 
        {
          found.assign(npertsets,-1);
          // pert_values start with pointers to each child's main value
          pert_values.assign(npertsets,values);
          // loop over children. For every child that contains a perturbed
          // value for spid[j], put a pointer to the perturbed value into 
          // pert_values[ipert][ichild]. For children that do not contain a 
          // perturbed value, it will retain a pointer to the main value.
          // The pertubations themselves are collected into pert[]; these
          // must match across all children
          for( int ich=0; ich<nrch; ich++ )
          {
            const VellSet &vs = *(child_vs[ich]);
            int inx = vs.isDefined(spids[j],indices[ich]);
            if( inx >= 0 )
            {
              for( int ipert=0; ipert<std::max(vs.numPertSets(),npertsets); ipert++ )
              {
                const Vells &pvv = vs.getPerturbedValue(inx,ipert);
//                childpvv_lock[ipert][ich].relock(pvv.mutex());
                FailWhen(!pvv.isCompatible(res_shape),"mismatch in child result shapes");
                pert_values[ipert][ich] = &pvv;
                if( found[ipert] >=0 )
                {
                  FailWhen(pert[ipert]!=vs.getPerturbation(inx,ipert),
                      ssprintf("perturbation %d for spid %d does not match between child results %d and %d",
                        ipert,spids[j],found[ipert],ich));
                }
                else
                {
                  pert[ipert] = vs.getPerturbation(inx,ipert);
                  found[ipert] = ich;
                }
              }
            }
          }
          // now, call evaluate() on the pert_values vectors to obtain the
          // perturbed values of the function
          for( int ipert=0; ipert<npertsets; ipert++ )
          {
            FailWhen(found[ipert]<0,
                     ssprintf("no perturbation set %d found for spid %d",
                              ipert,spids[j]));
            vellset.setPerturbation(j,pert[ipert],ipert);
            vellset.setPerturbedValue(j,evaluate(request,res_shape,pert_values[ipert]).makeNonTemp(),ipert);
          }
        } // end for(j) over spids
      }
      catch( std::exception &x )
      {
        MakeFailVellSet(vellset,
            string("exception in Function::getResult: ")
            + x.what());
      }
    } // endif( !vellset.isFail() )
    // count the # of fails
    if( vellset.isFail() )
      nfails++;
  }
  // return RES_FAIL is all planes have failed
  if( nfails == nplanes )
    return RES_FAIL;
  // return 0 flag, since we don't add any dependencies of our own
  return 0;
}

//##ModelId=3F86886F0108
vector<int> Function::findSpids (int &npertsets,const vector<const VellSet*> &results)
{
  // Determine the maximum number of spids.
  int nrspid = 0;
  int nrch = results.size();
  for (int i=0; i<nrch; i++) {
    nrspid += results[i]->numSpids();
  }
  npertsets = 0;
  // Allocate a vector of that size.
  // Exit immediately if nothing to be done.
  vector<int> spids(nrspid);
  if (nrspid == 0) {
    return spids;
  }
  // Merge all spids by doing that child by child.
  // The merged spids are stored from the end of the spids vector, so
  // eventually all resulting spids are at the beginning of the vector.
  int stinx = nrspid;          // start at end
  nrspid = 0;                  // no resulting spids yet
  // Loop through all children.
  for (int ch=0; ch<nrch; ch++) {
    const VellSet &resch = *results[ch];
    npertsets = std::max(npertsets,resch.numPertSets());
    int nrchsp = resch.numSpids();
    if (nrchsp > 0) {
      // Only handle a child with spids.
      // Get a direct pointer to its spids (is faster).
      int inx = stinx;       // index where previous merge result starts.
      int lastinx = inx + nrspid;
      stinx -= nrchsp;       // index where new result is stored.
      int inxout = stinx;
      int lastspid = -1;
      // Loop through all spids of the child.
      for (int i=0; i<nrchsp; i++) {
        // Copy spids until exceeding current child's spid.
        int spid = resch.getSpid(i);
        while (inx < lastinx  &&  spids[inx] <= spid) {
          lastspid = spids[inx++];
          spids[inxout++] = lastspid;
        }
        // Only store child's spid if different.
        if (spid != lastspid) {
          spids[inxout++] = spid;
        }
      }
      // Copy possible remaining spids.
      while (inx < lastinx) {
        spids[inxout++] = spids[inx++];
      }
      nrspid = inxout - stinx;
    }
  }
  spids.resize(nrspid);
  return spids;
}

Vells Function::evaluate (const Request &,const LoShape &,const vector<const Vells*>&)
{
  Throw("evaluate() not implemented in this class");
}


} // namespace Meq


