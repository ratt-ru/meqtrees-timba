//# NElements.cc: Take mean of a node
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

#include <MeqNodes/NElements.h>

#include <MEQ/Vells.h>

using namespace Meq::VellsMath;

namespace Meq {    

//##ModelId=400E53550241
NElements::NElements()
: Function(-1,0,1) // must have at least one child
{}

//##ModelId=400E53550242
NElements::~NElements()
{}

//##ModelId=400E53550246
Vells NElements::evaluate (const Request&,const LoShape &shape,
		     const vector<const Vells*>& values)
{
  Vells res = nelements(*(values[0]),shape);
  for( uint i=1; i<values.size(); i++ )
    res += nelements(*(values[i]),shape);
  return res;
}

} // namespace Meq
