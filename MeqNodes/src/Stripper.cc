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
                     const std::vector<Result::Ref> &child_result, 
		     const Request &request,bool newreq) {
  // Create result object and attach to the ref that was passed in.
  Result & result = resref <<= new Result(1);
  // carry Cells along
  const Cells &cells = child_result[0]->cells();
  result.setCells(cells);
  // we want to strip off and return just the first Vells from the
  // single child
  const Vells &val = child_result[0]->vellSet(0).getValue();
  // attach this value to the result that will be returned
  result.setNewVellSet(0).setValue(val);
  return 0;
}

} // namespace Meq
