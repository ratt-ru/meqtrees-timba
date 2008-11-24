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
#include "TID-DMI.h"
    
  // Methods for the method table are naturally implemented via
  // templates. Refer to DMI::NumArray.cc to see how they are populated.

// populate the method tables via the DoForAll macros
#define OneLine(T,arg) { DoForAllArrayRanks1(OneElement,T) }
  
  
using std::string;

namespace DMI
{
namespace NumArrayFuncs
{
// templated method to placement-new allocate an Lorray(N,T)
template<class T,int N>
static void newArrayPlacement (void *where)
{ 
  new (where) blitz::Array<T,N>; 
}

AllocatorPlacement allocatorPlacement[NumArrayTypes][MaxLorrayRank] =
{
#define OneElement(N,T) &newArrayPlacement<T,N>
  DoForAllArrayTypes1(OneLine,)
#undef OneElement
};

// templated method to allocate an empty Lorray(N,T)
template<class T,int N>
static void * newArrayDefault ()
{ 
  return new blitz::Array<T,N>; 
}

AllocatorDefault allocatorDefault[NumArrayTypes][MaxLorrayRank] =
{
#define OneElement(N,T) &newArrayDefault<T,N>
  DoForAllArrayTypes1(OneLine,)
#undef OneElement
};

  

int typeIndices[NumTypes];

bool initTypeIndices ()
{
  for(int i=0; i<NumTypes; i++)
    typeIndices[i] = -1;
  int i0 = 0;
  #define addIndex(type,arg) typeIndices[-(Tp##type##_int-Tpbool_int)] = i0++;
  DoForAllArrayTypes(addIndex,)
  #undef addIndex
  return true;
}

bool _initialized_typeindices = initTypeIndices();

}};
