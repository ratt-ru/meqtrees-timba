//#  DMI.h: constants and bitflags for the DMI package
//#
//#  Copyright (C) 2002-2003
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$

#ifndef DMI_DMI_H
#define DMI_DMI_H 1

#define MAKE_LOFAR_SYMBOLS_GLOBAL 1

#include "config.h"
#include "lofar_config.h"
#include <DMI/Common.h>
#include <Common/Debug.h>
#include <stdio.h>

namespace DMI
{
  extern ::Debug::Context DebugContext; 
  inline ::Debug::Context & getDebugContext() { return DebugContext; };
  
  
//##ModelId=3DB949AE00AC
  typedef enum { 
  // flags for CountedRefs & other objects
      WRITE           = 0x001,
      READONLY        = 0x002,
      ANON            = 0x004,
      DELETE          =     ANON,
      NON_ANON        = 0x008,
      EXTERNAL        =     NON_ANON,
      NO_DELETE       =     NON_ANON,
      LOCKED          = 0x010,
      LOCK            =     LOCKED,
      UNLOCKED        = 0x020,
      PERSIST         = 0x040,
      
      
 
//   // by default, refs are privatize-on-write (that is, a read-only ref 
//   // will auto-privatize the object if write access is requested). If attached
//   // as SHARED, the object becomes shared between the owner ref and the new
//   // ref, and access is completely controlled via the READ/WRITE flags
//       POW             = 0,
//       NOPOW           = 0x080,
//         SHARED        =   NOPOW,    
      
  // when attaching a ref as ANON or EXTERN, and the target is already 
  // referenced, use the established ref type even if it conflicts with the flags
      NONSTRICT       =  0,        // default is non-strict
      STRICT          =  0x80000,
      
  // some common combinations
      ANONWRITE       = WRITE|ANON,
      ANONWR          = ANONWRITE,
      ANONRO          = READONLY|ANON,
  
  // These are used in privatize() and clone()
      // makes deep clone or privatizes deeply
      DEEP           = 0x01000,
  // forces private copy even if not normnally necessary
      FORCE_CLONE    = 0x02000,
      
  // these are used in ref copy constructor calls to force copy() or privatize() 
      PRIVATIZE       =  0x10000,
      COPYREF         =  0x20000,
      XFER            =  0,        // XFER is the default, so 0
      
  // preserve r/w privilege for ref copy. Only matters if NOPOW (=SHARED) is
  // also specified. A ref copied with POW is always writable, with 
  // privatization occurring on first access
      PRESERVE_RW     =  0x40000,  
      
  // container-specific flags for privatize (privatize-and-reset)
      RESET           =  0x80000,

  // _SmartBlock_-specific flags
      HINT_SHMEM      =0x1000000,  // constructor hint: block will be sent
                                   //     to other processes, so consider shmem
      SHMEM           =0x2000000,  // constructor: forces use of shmem
      CLONE           =COPYREF,    // copy constructor: clones block
      ZERO            =DEEP,       // constructor: zeroes allocated block
      
  // _BlockSet_-specific flags
      MAKE_READONLY   =0x4000000,   // for copyAll(): makes source set read-only

  // NestableContainer::get() flags
      NC_ASSIGN          =0x1000000,  // container accessed for assignment
      NC_DEREFERENCE     =0x2000000,  // refs will be dereferenced 
      
      DMI_ZERO_FLAG   =0
  }
  DMIFlags;

  // compile-time error reporting. This is borrowed from Alexandrescu
  template<int> struct CompileTimeError;
  template<> struct CompileTimeError<true> {};

};

#define STATIC_CHECK(expr,msg) \
  { DMI::CompileTimeError<((expr) != 0)> ERROR_##msg; (void)ERROR_##msg; }
// typedef DMI::CompileTimeChecker<(expr)!=0> Checker; 
//  (void)sizeof( Checker( ERROR_##msg() ) ); }

// OMS: 21/10/04: reverting to using namespace LOFAR in DMI etc. for now
// using namespace LOFAR;

// OMS: 26/11/04: need this because DMI pulls in Thread, so verything that uses
// DMI better have this symbol defined!

#endif
