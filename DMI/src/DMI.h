#ifndef DMI_h
#define DMI_h 1

#include "DMI/Common.h"
#include "Common/Debug.h"
#include <stdio.h>


namespace DMI
{
//## begin DMI%3C14BA2803C4.initialDeclarations preserve=yes
  extern ::Debug::Context DebugContext; 
  inline ::Debug::Context & getDebugContext() { return DebugContext; };
  
  
//##ModelId=3DB949AE00AC
  typedef enum { 
  // flags for CountedRefs & other objects
      WRITE           =0x001,
      READONLY        =0x002,
      EXCL_WRITE      =0x004,
      NONEXCL_WRITE   =0x008,
      ANON            =0x010,
      NON_ANON        =0x020,
      EXTERNAL        =NON_ANON,
      NO_DELETE       =0x040,
      DELETE          =0x080,          
      LOCKED          =0x100,
      LOCK            =LOCKED,
      UNLOCKED        =0x200,
      PERSIST         =0x400,
      
  // some common combinations
      ANONWRITE       = WRITE|ANON,
      ANONWR          = ANONWRITE,
      ANONRO          = READONLY|ANON,
  
  // These are used in privatize() and clone()
      // makes deep clone or privatizes deeply
      DEEP           = 0x01000,  
      // for write-privatization or cloning, will delay actual cloning
      // until the next access
      DLY_CLONE      = 0x02000,  
      DEEP_DLY_CLONE = 0x06000,
      // for ref.privatize(), forces cloning immediately even when not needed
      // (overrides DELAY_CLONE, hence the conflict with it)
      FORCE_CLONE     =  0x04000,
      
  // these are used in ref copy constructor calls to force copy() or privatize() 
      PRIVATIZE       =  0x10000,  
      COPYREF         =  0x20000,
      XFER            =  0,        // XFER is the default, so 0
  // preserve r/w privilege for ref copy
      PRESERVE_RW     =  0x40000,  
      
  // container-specific flags for privatize (privatize-and-reset)
      RESET           =  0x80000,

  // _SmartBlock_-specific flags
      SHARED          =0x1000000,  // constructor hint: block will be sent
                                   //     to other processes, so consider shmem
      SHMEM           =0x2000000,  // constructor: forces use of shmem
      CLONE           =PRIVATIZE,  // copy constructor: clones block
      ZERO            =DEEP,       // constructor: zeroes allocated block
      
  // _BlockSet_-specific flags
      MAKE_READONLY   =0x4000000,   // for copyAll(): makes source set read-only      

  // NestableContainer::get flags
      NC_SCALAR       =0x1000000,  // container accessed as a scalar
      NC_POINTER      =0x2000000,  // container accessed as a pointer 
      
      DMI_ZERO_FLAG   =0
  }
  DMIFlags;

};

using DMI::DebugContext;

#endif
