#ifndef DMI_Allocators_h
#define DMI_Allocators_h 1

// with non-gnu compilers, fall back to standard allocator
#if __GNUC__ < 3    
  #undef  DMI_USE_STD_ALLOC
  #define DMI_USE_STD_ALLOC 1
#endif
            
// DMI_USE_STD_ALLOC: define this to use the standard allocator (new/delete)
// rather than the pool-based multithreaded one

#if DMI_USE_STD_ALLOC

  #define DMI_Allocator std::alloc

#else

  #include <ext/mt_allocator.h>

  #define DMI_Allocator __gnu_cxx::__mt_alloc
  
#endif

#define ObjRefAllocator DMI_Allocator<ObjRef>
#define BlockSetAllocator DMI_Allocator<BlockSet>
  
// universal allocator for countedref types  
#define DMI_RefAllocator(T) DMI_Allocator<T>

#endif

