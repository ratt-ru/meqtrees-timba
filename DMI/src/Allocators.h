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

#ifndef DMI_Allocators_h
#define DMI_Allocators_h 1

// with non-gnu compilers, fall back to standard allocator
#if __GNUC__ < 3
  #define DMI_USE_STD_ALLOC 1
#endif

#include <ext/pool_allocator.h>
//#include <ext/bit/usr/include/c++/4.4/ext/bitmap_allocator.hmap_allocator.h>
#include <ext/mt_allocator.h>
#include <ext/malloc_allocator.h>
#include <ext/bitmap_allocator.h>
// define macro names for different allocators

#define DMI_Std_Allocator std::allocator
#define DMI_Pool_Allocator __gnu_cxx::__pool_alloc
// bitmap_allocator is broken in g++ 3.4
//#define DMI_Bitmap_Allocator __gnu_cxx::bitmap_allocator
#define DMI_MT_Allocator __gnu_cxx::__mt_alloc
#define DMI_Malloc_Allocator __gnu_cxx::malloc_allocator
#define DMI_Bitmap_Allocator __gnu_cxx::bitmap_allocator

// pick default allocator based on predefined macros

// mt allocator appears to have a threading-related bug (as of 3.4.3)
// See bugzilla bug 300. Switching to std::allocator for now, may want
// to look into other allocators later.
// #define DMI_USE_STD_ALLOC 1
        
#if defined(DMI_USE_STD_ALLOC)

  #define DMI_Allocator DMI_Std_Allocator
  
  // redefine other allocators to use the standard
  #undef DMI_Pool_Allocator 
  #undef DMI_MT_Allocator 
  #define DMI_Pool_Allocator DMI_Std_Allocator
  #define DMI_MT_Allocator DMI_Std_Allocator
  
#elif defined(DMI_USE_POOL_ALLOC)

  #define DMI_Allocator DMI_Pool_Allocator

#elif defined(DMI_USE_BITMAP_ALLOC)

  #define DMI_Allocator DMI_Bitmap_Allocator
  
#elif defined(DMI_USE_MALLOC_ALLOC)

  #define DMI_Allocator DMI_Malloc_Allocator

#else // default is mt_alloc

  #define DMI_Allocator DMI_MT_Allocator
  
#endif

#define ObjRefAllocator DMI_Allocator<ObjRef>
#define BlockSetAllocator DMI_Allocator<BlockSet>
  
// universal allocator for countedref types  
#define DMI_RefAllocator(T) DMI_Allocator<T>

#endif

