//# Function.cc: Base class for an expression node
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
  allow_missing_data_ = false;
//  setAutoResample(RESAMPLE_FAIL);
}

//##ModelId=3F86886E03D1
Function::~Function()
{}

void Function::allowMissingData ()
{
  allow_missing_data_ = true;
  children().setMissingDataPolicy(AidIgnore);
}

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
        flagmask_.assign(numChildren(),VellsFullFlagMask);  
      else if( flag == 0 )    // [0] means no flags on output
      {
        flagmask_.assign(numChildren(),0);  
        enable_flags_ = false;
      }
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
  else if( initializing )
  {
    flagmask_.assign(numChildren(),VellsFullFlagMask);
    rec[FFlagMask] = flagmask_;
  }
}

void Function::evaluateFlags (Vells::Ref &out,const Request &,const LoShape &,const vector<const VellSet *> &pvs)
{
  for( uint i=0; i<pvs.size(); i++ )
    if( pvs[i] && !pvs[i]->isNull() && pvs[i]->hasDataFlags() )
      Vells::mergeFlags(out,pvs[i]->dataFlags(),flagmask_[i]);
}

//##ModelId=3F86886E03DD
int Function::getResult (Result::Ref &resref,
                         const std::vector<Result::Ref> &childres,
                         const Request &request,bool)
{
  int nrch = numChildren();
  if( flagmask_.empty() )
    flagmask_.assign(childres.size(),VellsFullFlagMask);
  else
  {
    Assert(flagmask_.size() == childres.size());
  }

  // Figure out the dimensions of the output result, and see if all children
  // match these dimensions. Also, figure out if result should be marked as 
  // integrated.  Ino children, assume one plane.
  Result::Dims out_dims;
  bool integr = false;
  if( nrch )
  {
    FailWhen(!childres[0]->numVellSets(),"no vellsets in result of child 0");
    out_dims = childres[0]->dims();
    integr   = childres[0]->isIntegrated();  // flag: is any child integrated
    for( int i=1; i<nrch; i++ )
    {
      const Result &res = *childres[i];
      FailWhen(!res.numVellSets(),ssprintf("no vellsets in result of child %d",i));
      if( res.tensorRank() > 0 )
      {
        if( out_dims.empty() )
          out_dims = res.dims();
        else
        {
          FailWhen(res.dims()!=out_dims,"dimensions of tensor child results do not match");
        }
      }
      integr |= childres[i]->isIntegrated();
    }
  }
  // override the integrated flag if the state record provides one
  if( force_integrated_ )
    integr = integrated_;
  // Create result and attach to the ref that was passed in
  Result & result = resref <<= new Result(out_dims,integr);
  // Find cumulative shape from all children
  // If no children, use the request cells shape.
  LoShape res_shape;
  // look for cells in child results
  for( int i=0; i<nrch; i++ )
    Axis::mergeShape(res_shape,childres[i]->getVellSetShape());
  // if not found, use request cells
  if( res_shape.empty() && request.hasCells() )
    res_shape = request.cells().shape();
  // use cell shape for result shape, most subclasses will ignore it anyway
  // and let vells math determine the shape instead
  vector<const VellSet*> child_vs(nrch);
  vector<const Vells*>   values(nrch);
  int nfails = 0;
  int nplanes = result.numVellSets();
  int missing_planes = 0;
  for( int iplane = 0; iplane < nplanes; iplane++ )
  {
    // create a vellset for this plane
    VellSet &vellset = result.setNewVellSet(iplane,0,0);
    // collect vector of pointers to child vellsets #iplane, and a vector of 
    // pointers to their main values. If a child is of tensor rank 0, always
    // reuse its single vellset. If any child vellsets are fails, collect 
    // them for propagation
    int nmissing = 0;
    for( int i=0; i<nrch; i++ )
    {
      child_vs[i] = 0;
      values[i] = 0;
      const Result &chres = *childres[i];
      const HIID &label = children().getChildLabel(i);
      // does this child have a vellset?
      if( chres.numVellSets() )
      {
        const VellSet &vs = chres.vellSet( chres.tensorRank()>0 ? iplane : 0 );
        if( vs.isFail() )
        { // collect fails from child vellset
          for( int j=0; j<vs.numFails(); j++ )
            vellset.addFail(vs.getFail(j));
        }
        else if( vs.hasValue() )
        {
          const Vells &val = vs.getValue();
          FailWhen(!val.isCompatible(res_shape),"shape mismatch for result of child '"+label.toString()+"'");
          child_vs[i] = &vs;
          values[i] = &val;
        }
      }
      // no value found?
      if( !values[i] )
      {
        FailWhen(!allow_missing_data_,"child '"+label.toString()+"' returned missing data, which is not allowed in this Function node");
        nmissing++;
      }
    }
    // if everything is missing, then we return no data for this VellSet
    // (unless we have a special case of a Function with no children)
    if( nrch && nmissing == nrch )
    {
      missing_planes++;
      continue;
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
        evaluateFlags(flagref,request,res_shape,child_vs);
        if( flagref.valid() )
          vellset.setDataFlags(flagref);
        // Evaluate the main value.
        vellset.setValue(evaluate(request,res_shape,values));
        // Evaluate all perturbed values.
        vector<vector<const Vells*> > pert_values(npertsets);
        vector<double> pert(npertsets);
        vector<int> indices(nrch,0);
        vector<int> found(npertsets);
        for( uint j=0; j<spids.size(); j++) 
        {
          found.assign(npertsets,-1);
          // pert_values start with pointers to each child's main value, the
          // loop below then replaces them with values from children that 
          // have a corresponding perturbed value
          pert_values.assign(npertsets,values);
          // loop over children. For every child that contains a perturbed
          // value for spid[j], put a pointer to the perturbed value into 
          // pert_values[ipert][ichild]. For children that do not contain a 
          // perturbed value, it will retain a pointer to the main value.
          // The pertubations themselves are collected into pert[]; these
          // must match across all children
          for( int ich=0; ich<nrch; ich++ )
          {
            if( !child_vs[ich] )
              continue;
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
            vellset.setPerturbedValue(j,evaluate(request,res_shape,pert_values[ipert]),ipert);
          }
        } // end for(j) over spids
      }
      catch( std::exception &x )
      {
        MakeFailVellSetMore(vellset,x,"exception in Function::getResult");
      }
      catch( ... )
      {
        MakeFailVellSet(vellset,"uknown exception in Function::getResult");
      }
    } // endif( !vellset.isFail() )
    // count the # of fails
    if( vellset.isFail() )
      nfails++;
  }
  // return RES_FAIL is all planes have failed
  if( nfails == nplanes )
    return RES_FAIL;
  if( missing_planes == nplanes )
    return RES_MISSING;
   // return 0 flag, since we don't add any dependencies of our own
  return 0;
}

//##ModelId=3F86886F0108
vector<int> Function::findSpids (int &npertsets,const vector<const VellSet*> &results)
{
  // Determine the maximum number of spids.
  int nrspid = 0;
  int nrch = results.size();
  for (int i=0; i<nrch; i++) 
    if( results[i] )
      nrspid += results[i]->numSpids();
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
  for (int ch=0; ch<nrch; ch++) 
  {
    if( !results[ch] )
      continue;
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


