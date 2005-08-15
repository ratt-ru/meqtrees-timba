#include "NumArrayFuncs.h"
    
  // Methods for the method table are naturally implemented via
  // templates. Refer to DMI::NumArray.cc to see how they are populated.

// populate the method tables via the DoForAll macros
#define OneLine(T,arg) { DoForAllArrayRanks1(OneElement,T) }

    
// templated method to allocate a Lorray(N,T) of the given shape, using pre-existing data
template<class T,int N>
static void * newArrayWithData (void *where,void *data,const LoShape & shape)
{ 
  return new (where) blitz::Array<T,N>(static_cast<T*>(data),shape,blitz::neverDeleteData); 
} 
DMI::NumArrayFuncs::AllocatorWithData DMI::NumArrayFuncs::allocatorWithData[NumTypes][MaxLorrayRank] =
{
#define OneElement(N,T) &newArrayWithData<T,N>
  DoForAllArrayTypes1(OneLine,)
#undef OneElement
};
