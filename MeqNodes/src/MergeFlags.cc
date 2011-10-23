//# MergeFlags.cc: a trivial flagger: flags ==0 or !=0
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

#include <MeqNodes/MergeFlags.h>
#include <MeqNodes/AID-MeqNodes.h>

namespace Meq {

const HIID FMergeAll = AidMerge|AidAll;
  
//##ModelId=400E5355029C
MergeFlags::MergeFlags()
  : Function(-2),merge_all_(false)
{}

//##ModelId=400E5355029D
MergeFlags::~MergeFlags()
{}
 
void MergeFlags::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Function::setStateImpl(rec,initializing);
  rec[FMergeAll].get(merge_all_,initializing);
}

void MergeFlags::mergeChildFlags (Result::Ref &resref,int ivs,const VellSet &vs,VellsFlagType fm)
{
  Vells::Ref flags;
  const VellSet &vs0 = resref->vellSet(ivs);
  if( vs0.hasDataFlags() )
    flags.attach(vs0.dataFlags());
  Vells::mergeFlags(flags,vs.dataFlags(),fm);
  if( flags.valid() )
    resref().vellSetWr(ivs).setDataFlags(flags);
}

int MergeFlags::getResult (Result::Ref &resref, 
                            const std::vector<Result::Ref> &childres,
                            const Request &request,bool)
{
  int nch = childres.size();
  if( flagmask_.empty() )
    flagmask_.assign(childres.size(),VellsFullFlagMask);
  else
  {
    Assert(flagmask_.size() == childres.size());
  }
  // copy first child result to output
  resref = childres[0];
  int nvs0 = resref->numVellSets();
  // only one result? Merge flags of all child elements
  if( nch == 1 )
  {
    Vells::Ref flags;
    // less than two vellsets? Nothing to merge then, return as-is
    if( nvs0 <= 1 )
      return 0;
    // else merge
    for( int i=0; i<nvs0; i++ )
    {
      const VellSet &vs = resref->vellSet(i);
      if( vs.hasDataFlags() )
        Vells::mergeFlags(flags,vs.dataFlags(),flagmask_[0]);
    }
    // got any flags at all? reattach them
    if( flags.valid() )
    {
      Result &result = resref();
      for( int i=0; i<nvs0; i++ )
        result.vellSetWr(i).setDataFlags(flags);
    }
    return 0;
  }
  // multiple results, merge all child flags into child 1
  // nothing to merge if no vellsets
  if( nvs0<1 )
    return 0;
  const LoShape & resdims = resref->dims();
  // loop over all children
  for( int ich=1; ich<nch; ich++ )
  {
    VellsFlagType fm = flagmask_[ich];
    // ignore children with empty mask
    if( !fm )
      continue;
    const Result &chres = *childres[ich];
    // ignore children w/o a vellset
    int nvs1 = chres.numVellSets();
    if( !nvs1 )
      continue;
    if( merge_all_ ) // merge all child flags: ignore shapes and everything, just merge
    {
      for( int i=0; i<nvs0; i++ )
        for( int j=0; j<nvs1; j++ )
        {
          const VellSet &vs1 = chres.vellSet(j);
          if( vs1.hasDataFlags() )
            mergeChildFlags(resref,i,vs1,fm);
        }
    }
    else if( resdims == chres.dims() )    // same tensor shape: merge element-by-element 
    {
      for( int i=0; i<nvs0; i++ )
      {
        const VellSet &vs1 = chres.vellSet(i);
        if( vs1.hasDataFlags() )
          mergeChildFlags(resref,i,vs1,fm);
      }
    }
    else if( chres.dims().empty() )  // scalar flag source: merge with all elements
    {
      const VellSet &vs1 = chres.vellSet(0);
      if( vs1.hasDataFlags() )
        for( int i=0; i<nvs0; i++ )
          mergeChildFlags(resref,i,vs1,fm);
    }
    else if( resdims.empty() )       // scalar destination: merge all tensor flags with scalar
    {
      Vells::Ref flags;
      const VellSet &vs0 = resref->vellSet(0);
      if( vs0.hasDataFlags() )
        flags.attach(vs0.dataFlags());
      for( int i=0; i<nvs1; i++ )
      {
        const VellSet &vs1 = chres.vellSet(i);
        if( vs1.hasDataFlags() )
          Vells::mergeFlags(flags,vs1.dataFlags(),fm);
      }
      if( flags.valid() )
        resref().vellSetWr(0).setDataFlags(flags);
    }
    else
    {
      Throw("dimensions of tensor child results do not match");
    }
  }
  
  // return 0 flag, since we don't add any dependencies of our own
  return 0;
}

} // namespace Meq
