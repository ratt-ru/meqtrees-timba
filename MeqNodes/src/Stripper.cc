//# Stripper.cc: strip off any Vells other than first from child
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

#include <MeqNodes/Stripper.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>

namespace Meq {    


Stripper::Stripper()
  : Node(1)  // must have precisely 1 child
{ 
}

Stripper::~Stripper()
{}

int Stripper::getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &child_results, 
		                     const Request &request,bool newreq)
{
  Assert(child_results.size() == 1);
  // Create result object as copy of input
  resref = child_results.front();
  // loop over all vellsets and strip off perturbed values as needed
  // We take advantage of copy-on-write here, so if there's nothing
  // to strip, the child result gets returned unchanged
  int nvs = resref->numVellSets();
  for( int i=0; i<nvs; i++ )
  {
    const VellSet &vs = resref->vellSet(i);
    if( vs.hasValue() && vs.numSpids()>0 )
      resref().setNewVellSet(i).setValue(vs.getValue());
  }
  // if something has changed in the result, call verify shape, since
  // that'll strip off cells too if they are no longer needed
  if( child_results.front() != resref )
    resref().verifyShape();
  
  return 0;
}

} // namespace Meq
