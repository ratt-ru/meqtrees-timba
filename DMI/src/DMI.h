#ifndef DMI_h
#define DMI_h 1

#include "Common.h"
#include "Debug.h"
#include <stdio.h>
    
#define DebugContext DMI::Debug    

namespace DMI
{
//## begin DMI%3C14BA2803C4.initialDeclarations preserve=yes

  // this defines a standard namespace for the debugging message mechanism
  DebugWithLevels;
  
  typedef enum { 
      WRITE           =0x001,
      READONLY        =0x002,
      EXCL_WRITE      =0x004,
      NONEXCL_WRITE   =0x008,
      ANON            =0x010,
      NON_ANON        =0x020,
      EXTERNAL        =0x020,
      NO_DELETE       =0x040,
      DELETE          =0x080,          
      LOCKED          =0x100,
      UNLOCKED        =0x200,
  
      PRIVATIZE       =0x1000,
      FORCE_CLONE     =0x2000,
      COPYREF         =0x4000,
      
      SHMEM           =0x8000,
      SHARED          =0x10000,
      CLONE           =0x20000
  }
  DMIFlags;

};


#endif
