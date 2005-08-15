#include "NumArrayFuncs.h"
    
  // Methods for the method table are naturally implemented via
  // templates. Refer to DMI::NumArray.cc to see how they are populated.

// populate the method tables via the DoForAll macros
#define OneLine(T,arg) { DoForAllArrayRanks1(OneElement,T) }


    
// templated method to assign a ref to the data (using the given shape & stride)
// to an array
template<class T,int N>
static void referenceDataWithStride (void *parr,void *data,const LoShape & shape,const LoShape &stride)
{ 
  blitz::Array<T,N> tmp(static_cast<T*>(data),shape,stride,blitz::neverDeleteData);
  static_cast<blitz::Array<T,N>*>(parr)->reference(tmp);
}
DMI::NumArrayFuncs::AssignWithStride DMI::NumArrayFuncs::assignerWithStride[NumTypes][MaxLorrayRank] =
{
#define OneElement(N,T) &referenceDataWithStride<T,N>
  DoForAllArrayTypes1(OneLine,)
#undef OneElement
};
