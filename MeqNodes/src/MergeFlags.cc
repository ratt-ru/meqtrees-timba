//# MergeFlags.cc: a trivial flagger: flags ==0 or !=0
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

#include <MeqNodes/MergeFlags.h>

namespace Meq {

//##ModelId=400E5355029C
MergeFlags::MergeFlags()
{}

//##ModelId=400E5355029D
MergeFlags::~MergeFlags()
{}

int MergeFlags::getResult (Result::Ref &resref, 
                            const std::vector<Result::Ref> &childres,
                            const Request &request,bool)
{
  std::vector<Thread::Mutex::Lock> child_reslock(numChildren());
  lockMutexes(child_reslock,childres);
  int nch = childres.size();
  // if not enough flags in mask, extend with default value
  int i = flagmask_.size();
  if( i < nch )
  {
    flagmask_.resize(nch);
    for( ; i<nch; i++ )
      flagmask_[i] = -1;
  }
  // copy first child result to output; privatize for writing since we intend
  // to modify flags
  resref = childres[0];
  resref.privatize(DMI::WRITE);
  Result & result = resref();
  // check # of input vellsets
  int nvs = result.numVellSets();
  for( int ich=1; ich<nch; ich++ )
  {
    int n = childres[ich]->numVellSets();
    // all children must have either 1 VellSet, or more than child 0
    if( n>1 && n<nvs )
      NodeThrow1(Debug::ssprintf("error: child 1 returns %d VellSets, child %d returns %d",nvs,ich+1,n));
  }
  // loop over vellsets
  for( int iplane = 0; iplane < nvs; iplane++ )
  {
    VellSet &vs = result.vellSetWr(iplane);
    bool had_flags = vs.hasOptCol(VellSet::FLAGS);
    // get main values 
    VellSet::FlagArrayType & flags = vs.getOptColWr<VellSet::FLAGS>();
    // apply first mask, unless we didn't have any flags to begin with
    if( had_flags )
      flags &= flagmask_[0];
    // loop over children to add their flags
    for( int ich=1; ich<nch; ich++ )
    {
      const Result &chres = *(childres[ich]);
      const VellSet &vs = chres.vellSet(std::max(chres.numVellSets()-1,iplane));
      // if child vellset has flags and mask !=0, merge with result
      if( flagmask_[ich] && vs.hasOptCol(VellSet::FLAGS) )
        flags |= vs.getOptCol<VellSet::FLAGS>() & flagmask_[ich];
    }
  }
  // return 0 flag, since we don't add any dependencies of our own
  return 0;
}

} // namespace Meq
