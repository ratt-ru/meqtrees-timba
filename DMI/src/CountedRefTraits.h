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

#ifndef DMI_CountedRefTraits_h
#define DMI_CountedRefTraits_h 1
    
#include <DMI/TypeId.h>
#include <DMI/CountedRef.h>
    
namespace DMI
{
    
template<class T>
class CountedRefTraits : public DMITypeTraits<T>
{
  public:
    enum { isCountedRef  = false };
    typedef void TargetType; 
};

// a partial specialization of the traits for CountedRefs
template<class T>
class CountedRefTraits< CountedRef<T> > : public DMITypeTraits< CountedRef<T> >
{
  public:
    enum { isCountedRef  = true };
    typedef T TargetType; 
};
    
};
#endif
