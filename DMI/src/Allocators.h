#ifndef DMI_Allocators_h
#define DMI_Allocators_h 1

// with non-gnu compilers, fall back to standard allocator
#if __GNUC__ < 3
  #define DMI_USE_STD_ALLOC 1
#endif
            
// DMI_USE_STD_ALLOC: define this to use the standard allocator (new/delete)
// rather than the pool-based multithreaded one

#if defined(DMI_USE_STD_ALLOC)

  #define DMI_Allocator std::alloc
  
#elsif defined(DMI_USE_POOL_ALLOC)

  #include <ext/pool_allocator.h>
  #define DMI_Allocator __gnu_cxx::__pool_alloc

#elsif defined(DMI_USE_BITMAP_ALLOC)

  #include <ext/bitmap_allocator.h>
  #define DMI_Allocator __gnu_cxx::bitmap_allocator
  
#else // default is mt_alloc

  #include <ext/mt_allocator.h>
  #define DMI_Allocator __gnu_cxx::__mt_alloc
  
#endif

#define ObjRefAllocator DMI_Allocator<ObjRef>
#define BlockSetAllocator DMI_Allocator<BlockSet>
  
// universal allocator for countedref types  
#define DMI_RefAllocator(T) DMI_Allocator<T>

#endif

