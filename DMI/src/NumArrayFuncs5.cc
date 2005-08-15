#include "NumArrayFuncs.h"
    
  // Methods for the method table are naturally implemented via
  // templates. Refer to DMI::NumArray.cc to see how they are populated.

// populate the method tables via the DoForAll macros
#define OneLine(T,arg) { DoForAllArrayRanks1(OneElement,T) }
  


// templated method to destroy a Lorray(N,T) at the given address without deallocing the memory
template<class T,int N>
static void deletePlacementArray (void *parr)
{ 
  typedef blitz::Array<T,N> ArrType;
  static_cast<ArrType*>(parr)->~ArrType(); 
}
DMI::NumArrayFuncs::Destructor DMI::NumArrayFuncs::destructor_inplace[NumTypes][MaxLorrayRank] =
{
#define OneElement(N,T) &deletePlacementArray<T,N>
  DoForAllArrayTypes1(OneLine,)
#undef OneElement
};





  
