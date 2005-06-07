#ifndef DMI_Allocators_h
#define DMI_Allocators_h 1

// with non-gnu compilers, fall back to standard allocator
#if __GNUC__ < 3
  #define DMI_USE_STD_ALLOC 1
#endif

#include <ext/pool_allocator.h>
//#include <ext/bitmap_allocator.h>
#include <ext/mt_allocator.h>

// define macro names for different allocators

#define DMI_Std_Allocator std::allocator
#define DMI_Pool_Allocator __gnu_cxx::__pool_alloc
//#define DMI_Bitmap_Allocator __gnu_cxx::bitmap_allocator
#define DMI_MT_Allocator __gnu_cxx::__mt_alloc

// pick default allocator based on predefined macros
        
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
  
#else // default is mt_alloc

  #define DMI_Allocator DMI_MT_Allocator
  
#endif

#define ObjRefAllocator DMI_MT_Allocator<ObjRef>
#define BlockSetAllocator DMI_MT_Allocator<BlockSet>
  
// universal allocator for countedref types  
#define DMI_RefAllocator(T) DMI_MT_Allocator<T>

#endif

