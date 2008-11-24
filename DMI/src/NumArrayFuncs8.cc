//
//% $Id$ 
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation & 
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc., 
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

#include "NumArrayFuncs.h"
    
  // Methods for the method table are naturally implemented via
  // templates. Refer to DMI::NumArray.cc to see how they are populated.

// populate the method tables via the DoForAll macros
#define OneLine(T,arg) { DoForAllArrayRanks1(OneElement,T) }
  


  
  
// templated method to copy return the shape of a Lorray
template<class T,int N>
static void returnShapeOfArray (LoShape &shape,const void *ptr)
{ 
  shape = static_cast<const blitz::Array<T,N>*>(ptr)->shape(); 
}
DMI::NumArrayFuncs::ShapeOfArray DMI::NumArrayFuncs::shapeOfArray[NumArrayTypes][MaxLorrayRank] =
{
#define OneElement(N,T) &returnShapeOfArray<T,N>
  DoForAllArrayTypes1(OneLine,)
#undef OneElement
};
