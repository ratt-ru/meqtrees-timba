//# Atan2.cc: return Arctan y / x
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
//# $Id: Atan2.cc 5418 2007-07-19 16:49:13Z oms $

#include <MeqNodes/Atan2.h>

#include <MEQ/Vells.h>

using namespace Meq::VellsMath;

namespace Meq {    


Atan2::Atan2()
{}

Atan2::~Atan2()
{}

// according to Blitz++ docs, the following should return the inverse
// tangent of y / x where x == values[0] and y == values[1]
Vells Atan2::evaluate (const Request&,const LoShape &,
			const vector<const Vells*>& values)
{
  return atan2(*(values[0]) , *(values[1]));
}


} // namespace Meq
