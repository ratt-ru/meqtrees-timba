//# Stripper.cc: strip off any Vells other than first from child
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

#include <MeqNodes/Stripper.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>

namespace Meq {    

const HIID FDomain = AidDomain;

Stripper::Stripper()
  : Node(1,0,0)  // must have precisely 1 child
{ 
}

Stripper::~Stripper()
{}

int Stripper::getResult (Result::Ref &resref, 
                         const std::vector<Result::Ref> &child_results, 
		                     const Request &request,bool newreq)
{
  std::vector<Thread::Mutex::Lock> child_reslock(numChildren());
  lockMutexes(child_reslock,child_results);
  // Create result object and attach to the ref that was passed in.
  // use same # of vellsets and integration flag as input result
  const Result & child_res = *child_results[0];
  int nvs = child_res.numVellSets();
  Result & result = resref <<= new Result(nvs,child_res.isIntegrated());
  // carry Cells along
  result.setCells(child_res.cells());
  for( int i=0; i<nvs; i++ )
  {
    const VellSet &child_vs = child_res.vellSet(i);
    if( child_vs.isFail() )
    {
      // a fail-vellset is passed along as-is
      result.setVellSet(0,&child_vs);
    }
    else
    {
      // a normal vellset: strip off and return just the main Vells from VellSet
      result.setNewVellSet(0).setValue(child_vs.getValue());
    }
  }
  return 0;
}

} // namespace Meq
