//# ReductionFunction.cc: Take mean of a node
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

#include <MeqNodes/ReductionFunction.h>
#include <MeqNodes/AID-MeqNodes.h>

#include <MEQ/Vells.h>
#include <MEQ/MeqVocabulary.h>

namespace Meq {    

const HIID FReductionAxes = AidReduction|AidAxes;

//##ModelId=400E53550241
ReductionFunction::ReductionFunction (int nchildren)
: Function(nchildren),
  has_axes_ids_(false)
{}

void ReductionFunction::setStateImpl (DMI::Record::Ref& rec, bool initializing)
{
  Function::setStateImpl(rec,initializing);
  // get reduction axes
  if( rec[FReductionAxes].exists() )
  {
    reduction_axes_.clear();
    // try to access as indices first
    try
    {
      rec[FReductionAxes].get_vector(reduction_axes_);
      has_axes_ids_ = false;
      return;
    }
    catch( ... ) // if this fails, try to access as HIIDs
    {
      try
      {
        rec[FReductionAxes].get_vector(reduction_axes_ids_);
      }
      catch( ... ) // finally, try as strings
      {
        std::vector<string> axes;
        rec[FReductionAxes].get_vector(axes);
        reduction_axes_ids_.resize(axes.size());
        for( uint i=0; i<axes.size(); i++ )
          reduction_axes_ids_[i] = axes[i];
      }
      has_axes_ids_ = true;
    }
    if( !reduction_axes_.empty() || !reduction_axes_ids_.empty() )
    {
      FailWhen(numChildren()>1,"cannot use reduction axes when multiple children are present");
    }
  }
}

// helper function: checks if a flag vells is fully flagged with a given mask,
// returns mask if so, or 0 if at least one point is not flagged
VellsFlagType ReductionFunction::isAllFlagged (const Vells &flagvells,VellsFlagType mask)
{
  // output will have a flag only if all of input is flagged
  const VellsFlagType *pflag = flagvells.begin<VellsFlagType>();
  for( ; pflag != flagvells.end<VellsFlagType>(); pflag++ )
    if( !(*pflag)&mask )
      return 0;
  // if we got here, than all points are flagged
  return mask;
}

void ReductionFunction::makeVellsSlicer (Vells::Ref &out,ConstVellsSlicerWithFlags0 &slicer,const Vells &invells)
{
  // create slicer
  slicer.init(invells,reduction_axes_);
  // create output Vells, not initialized
  out <<= new Vells(invells,slicer.nonSlicedShape(),false);
}

void ReductionFunction::makeVellsSlicer (Vells::Ref &out,ConstVellsSlicer0 &slicer,const Vells &invells)
{
  // create slicer
  slicer.init(invells,reduction_axes_);
  // create output Vells, not initialized
  out <<= new Vells(invells,slicer.nonSlicedShape(),false);
}

Vells ReductionFunction::apply (VellsMath::UnaryRdFunc func,const Vells &invells,VellsFlagType flagmask)
{
  // make slicer and output vells
  Vells::Ref outref;
  ConstVellsSlicerWithFlags0 slicer;
  makeVellsSlicer(outref,slicer,invells);
  Vells &out = outref();
  // get pointers to output data
  char * ptr = static_cast<char*>(out.getDataPtr());
  size_t size = out.elementSize();
  char * endptr = ptr + size*out.nelements();
  // iterate slicer and output pointers (they must match)
  for( ; slicer.valid(); slicer.incr(),ptr+=size )
  {
    DbgAssert(ptr<endptr);
    Vells result = (*func)(slicer.vells(),flagmask);
    memcpy(ptr,result.getConstDataPtr(),size);
  }
  DbgAssert(ptr==endptr);
  return out;
}

Vells ReductionFunction::apply (VellsMath::UnaryRdFuncWS func,const Vells &invells,const LoShape &res_shape0,VellsFlagType flagmask)
{
  // make slicer and output vells
  Vells::Ref outref;
  ConstVellsSlicerWithFlags0 slicer;
  makeVellsSlicer(outref,slicer,invells);
  Vells &out = outref();
  // adjust shape: it may be bigger than the slice shape (i.e. if taking
  // a sum while some axes are collapsed). So, for every axis that is present
  // in the non-sliced shape, collapse the corresponding axis in the result shape
  LoShape res_shape = res_shape0;
  const LoShape &ns_shape = slicer.nonSlicedShape();
  for( uint i=0; i<ns_shape.size(); i++ )
  {
    if( i<res_shape.size() && ns_shape[i] > 1  )
      res_shape[i] = 1;
  }
  // get pointers to output data
  char * ptr = static_cast<char*>(out.getDataPtr());
  size_t size = out.elementSize();
  char * endptr = ptr + size*out.nelements();
  // iterate slicer and output pointers (they must match)
  for( ; slicer.valid(); slicer.incr(),ptr+=size )
  {
    DbgAssert(ptr<endptr);
    Vells result = (*func)(slicer.vells(),res_shape,flagmask);
    memcpy(ptr,result.getConstDataPtr(),size);
  }
  DbgAssert(ptr==endptr);
  return out;
}
      
void ReductionFunction::evaluateFlags (Vells::Ref &out,const Request &req,const LoShape &shape,const vector<const VellSet *> &pvs)
{
  // if no reduction axes are present...
  if( !hasReductionAxes() )
  {
    // with multiple children, we reduce along the "child" axis,
    // so only flag the output if all the inputs are flagged
    if( pvs.size() > 1 )
    {
      VellsFlagType totflagmask = 0;
      // temp flag object, each bit #i will be 1 if child has its flag set
      Vells flagged(makeLoShape(1),totflagmask);  
      for( uint i=0; i<pvs.size(); i++ )
      {
        if( flagmask_[i] && pvs[i] && !pvs[i]->isNull() && pvs[i]->hasDataFlags() )
        { 
          totflagmask |= flagmask_[i];
          Vells vs_flagged;
          Vells masked_flags = pvs[i]->dataFlags()&flagmask_[i];
          // whereEq() will return 1 if all flags are ==0
          if( masked_flags.whereEq(vs_flagged,VellsFlagType(0),0,1<<i) != 1 )
            flagged |= vs_flagged;
        }
      }
      // any flags at all considered?
      if( totflagmask )
      {
        // now find the points that were flagged for ALL children,
        // and assign totflags to them
        Vells realflags;
        if( flagged.whereEq(realflags,(1<<pvs.size())-1,totflagmask,0) >=0 )
          Vells::mergeFlags(out,realflags,totflagmask);
      }
    }
    // single child: reduce to a single scalar
    else
    {
      VellsFlagType tot_flags = 0;
      for( uint i=0; i<pvs.size(); i++ )
        if( pvs[i] && flagmask_[i] && pvs[i]->hasDataFlags() )
          tot_flags |= isAllFlagged(pvs[i]->dataFlags(),flagmask_[i]);
      // if we have accumulated a flag, merge it in
      if( tot_flags )
      {
        Vells::Ref flagref;
        flagref <<= new Vells(makeLoShape(1),tot_flags,true);
        Vells::mergeFlags(out,*flagref,tot_flags);
      }
    }
  }
  // else collapse flags along the reduction axes (we may safely assume a
  // single child due to the check in setStateImpl() above)
  else
  {
    DbgAssert(pvs.size()==1);
    VellsFlagType flagmask = flagmask_[0];
    if( !flagmask || !pvs[0] )
      return;
    const VellSet & vs = *pvs[0];
    if( !vs.hasDataFlags() )
      return;
    // create slicer and output flags
    Vells::Ref outflag_ref;
    ConstVellsSlicer0 slicer;
    makeVellsSlicer(outflag_ref,slicer,vs.dataFlags());
    Vells & flags = outflag_ref();
    // now iterate over the output and over the slicer,
    VellsFlagType *pflag = flags.begin<VellsFlagType>();
    VellsFlagType tot_flags = 0;
    for( ; pflag != flags.end<VellsFlagType>(); pflag++ )
    {
      DbgAssert(slicer.valid());
      // output flag is set only if all of the current slice is flagged
      tot_flags |= *pflag = isAllFlagged(slicer.vells(),flagmask);
      slicer.incr();
    }
    // have we flagged anything at all in the output? assign flags then
    if( tot_flags )
      Vells::mergeFlags(out,flags,flagmask);
  }
}

int ReductionFunction::getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &childres,
                         const Request &req,bool newreq)
{
  if( has_axes_ids_ && !reduction_axes_ids_.empty() )
  {
    int naxes = reduction_axes_ids_.size();
    reduction_axes_.resize(naxes);
    for( int i=0; i<naxes; i++ )
      reduction_axes_[i] = Axis::axis(reduction_axes_ids_[i]);
  }
  return Function::getResult(resref,childres,req,newreq);
}

} // namespace Meq
