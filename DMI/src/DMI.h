//#  DMI.h: constants and bitflags for the DMI package
//#
//#  Copyright (C) 2002-2007
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  and The MeqTree Foundation
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
#include <TimBase/Debug.h>
#include <TimBase/LofarTypes.h>
#include <stdio.h>
#include <string>
#include <vector>

#include <lofar_config.h>

namespace DebugDMI
{
  extern ::Debug::Context DebugContext; 
  inline ::Debug::Context & getDebugContext() { return DebugContext; };
};

namespace DMI
{
  using std::string;
  using std::vector;

   
// must be called somewhere on startup before any DMI-using
// global initializers constructors
  extern int initialize ();
  
//##ModelId=3DB949AE00AC
  typedef enum { 
  // flags for r/w access rights (refs, containers and such)
      READONLY        = 0x001,
      WRITE           = 0x002,
  // ref copy-on-write flag: default unless shared is specified
      COW             = 0x004,
  // ref shared flag
      SHARED          = 0x008,
  // flags for CountedRef target ownership, passed to attach()
  //  mask is mask of all flags:
      OWNERSHIP_MASK  = 0x030,
  // anon is the default, unless external is specified explicitly           
      ANON            = 0x010,
  // external
      EXTERNAL        = 0x020,
  // auto-clone if target is not already attached 
      AUTOCLONE       = 0x030,
  // flags for a locked ref          
      LOCKED          = 0x100,
      LOCK            = LOCKED,
      UNLOCKED        = 0x200,
  // some common combinations
      ANONWRITE       = WRITE|ANON,
      ANONWR          = ANONWRITE,
      ANONRO          = READONLY|ANON,
  // forces a deep copy when copying/cloning refs or objects
      DEEP            = 0x1000,
      
  // these are used in ref copy constructor calls to force copy() or xfer()
      COPYREF         = 0x2000,  // new default
      XFER            = 0x4000,        
      
  // _SmartBlock_-specific flags
      HINT_SHMEM      =0x10000,  // constructor hint: block will be sent
                                 // to other processes, so consider shmem
      SHMEM           =0x20000,  // constructor: forces use of shmem
      CLONE           =0x40000,  // copy constructor: clones block
      ZERO            =0x80000,  // constructor: zeroes allocated block
      
  // _BlockSet_-specific flags
      MAKE_READONLY   =0x4000000,   // for copyAll(): makes source set read-only

  // DMI::Container::get() flags
      ASSIGN          =0x1000000,  // container accessed for assignment
      DEREFERENCE     =0x2000000,  // refs will be dereferenced
       
  // Other container-specific flags
      REPLACE         =0x1000000,  // object in container is replaced
      NOZERO          =0x4000000,  // do not initialize NumArray/data block to 0   
      
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
