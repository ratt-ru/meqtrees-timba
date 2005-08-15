#include "NumArrayFuncs.h"
    
  // Methods for the method table are naturally implemented via
  // templates. Refer to DMI::NumArray.cc to see how they are populated.

// populate the method tables via the DoForAll macros
#define OneLine(T,arg) { DoForAllArrayRanks1(OneElement,T) }
  

// templated method to allocate an empty Lorray(N,T)
template<class T,int N>
static void * newArrayDefault ()
{ 
  return new blitz::Array<T,N>; 
}
DMI::NumArrayFuncs::AllocatorDefault DMI::NumArrayFuncs::allocatorDefault[NumTypes][MaxLorrayRank] =
{
#define OneElement(N,T) &newArrayDefault<T,N>
  DoForAllArrayTypes1(OneLine,)
#undef OneElement
};

  
// // templated method to placement-new allocate an Lorray(N,T)
// template<class T,int N>
// static void newArrayPlacement (void *where)
// { 
//   new (where) blitz::Array<T,N>; 
// }
// DMI::NumArrayFuncs::AllocatorPlacement DMI::NumArrayFuncs::allocatorPlacement[NumTypes][MaxLorrayRank] =
// {
// #define OneElement(N,T) &newArrayPlacement<T,N>
//   DoForAllArrayTypes1(OneLine,)
// #undef OneElement
// };
// 
