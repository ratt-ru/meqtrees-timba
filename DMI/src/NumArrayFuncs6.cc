#include "NumArrayFuncs.h"
    
  // Methods for the method table are naturally implemented via
  // templates. Refer to DMI::NumArray.cc to see how they are populated.

// populate the method tables via the DoForAll macros
#define OneLine(T,arg) { DoForAllArrayRanks1(OneElement,T) }
  



// templated method to assign a ref to the data to an array
template<class T,int N>
static void referenceData (void *parr,void *data,const LoShape & shape)
{ 
  blitz::Array<T,N> tmp(static_cast<T*>(data),shape,blitz::neverDeleteData);
  static_cast<blitz::Array<T,N>*>(parr)->reference(tmp);
}
DMI::NumArrayFuncs::AssignDataReference DMI::NumArrayFuncs::assignerDataReference[NumTypes][MaxLorrayRank] =
{
#define OneElement(N,T) &referenceData<T,N>
  DoForAllArrayTypes1(OneLine,)
#undef OneElement
};
