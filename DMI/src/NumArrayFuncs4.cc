#include "NumArrayFuncs.h"
    
  // Methods for the method table are naturally implemented via
  // templates. Refer to DMI::NumArray.cc to see how they are populated.

// populate the method tables via the DoForAll macros
#define OneLine(T,arg) { DoForAllArrayRanks1(OneElement,T) }

    
    
// templated method to copy one Lorray to another
template<class T,int N>
static void copyArrayImpl (void *target,const void *source)
{ 
  *static_cast<blitz::Array<T,N>*>(target) = 
    *static_cast<const blitz::Array<T,N>*>(source); 
}
DMI::NumArrayFuncs::ArrayCopier DMI::NumArrayFuncs::copier[NumTypes][MaxLorrayRank] =
{
#define OneElement(N,T) &copyArrayImpl<T,N>
  DoForAllArrayTypes1(OneLine,)
#undef OneElement
};
