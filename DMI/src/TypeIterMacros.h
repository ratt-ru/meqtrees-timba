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

#ifndef DMI_TypeIterMacros_h
#define DMI_TypeIterMacros_h 1
    
#include <config.h>
    
// 
// This file defines "type iterator" macros, i.e. macros that will repeat
// a certain bit of code for every type in a category.
//
    
// This macro is used internally to expand the iterator definitions 
// pulled in from every package. Any new packages should be
// added to the list here.
#define DoForSomeTypes(Which,Do,arg); \
          DoForSomeTypes_DMI(Which,Do,arg); \
          DoForSomeTypes_OCTOPUSSY(Which,Do,arg) ;\
          DoForSomeTypes_VisCube(Which,Do,arg); \
          DoForSomeTypes_Meq(Which,Do,arg); 
        
// DMI types are always pulled in
#include "DMI/TypeIter-DMI.h"
#define DoForSomeTypes_DMI(Which,Do,arg) \
          DoForAll##Which##Types_DMI(Do,arg,;)
    
// Pull in iterators definitions from each configured dependency package. 
// If package is not configured, define dummy iterators for it.
// New packages should be added here in the same manner

#ifdef HAVE_LOFAR_OCTOPUSSY
  #include "OCTOPUSSY/TypeIter-OCTOPUSSY.h"
  #define DoForSomeTypes_OCTOPUSSY(Which,Do,arg) \
            DoForAll##Which##Types_OCTOPUSSY(Do,arg,;);
#else
  #define DoForSomeTypes_OCTOPUSSY(Which,Do,arg) 
#endif
    
#ifdef HAVE_LOFAR_VISCUBE
  #include "VisCube/TypeIter-VisCube.h"
  #define DoForSomeTypes_VisCube(Which,Do,arg) \
            DoForAll##Which##Types_VisCube(Do,arg,;);
#else
  #define DoForSomeTypes_VisCube(Which,Do,arg) 
#endif

#ifdef HAVE_LOFAR_MEQ
  #include "MEQ/TypeIter-Meq.h"
  #define DoForSomeTypes_Meq(Which,Do,arg) \
            DoForAll##Which##Types_Meq(Do,arg,;);
#else
  #define DoForSomeTypes_Meq(Which,Do,arg) 
#endif

    
// Now define the macros themselves

#ifndef DoForAllNumericTypes
  #define DoForAllNumericTypes(Do,arg) \
            DoForSomeTypes(Numeric,Do,arg)
#endif
          
#define DoForAllBinaryTypes(Do,arg) \
          DoForSomeTypes(Binary,Do,arg)
          
#define DoForAllDynamicTypes(Do,arg) \
          DoForSomeTypes(Dynamic,Do,arg)
          
#define DoForAllIntermediateTypes(Do,arg) \
          DoForSomeTypes(Intermediate,Do,arg)
          
#define DoForAllSpecialTypes(Do,arg) \
          DoForSomeTypes(Special,Do,arg)
          
#define DoForAllOtherTypes(Do,arg) \
          DoForSomeTypes(Other,Do,arg)

#endif
