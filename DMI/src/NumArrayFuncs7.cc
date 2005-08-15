#include "NumArrayFuncs.h"
    
  // Methods for the method table are naturally implemented via
  // templates. Refer to DMI::NumArray.cc to see how they are populated.

// populate the method tables via the DoForAll macros
#define OneLine(T,arg) { DoForAllArrayRanks1(OneElement,T) }
  


  
 

// templated method to delete a Lorray(N,T) at the given address
template<class T,int N>
static void deleteArray (void *parr)
{ 
  delete static_cast<blitz::Array<T,N>*>(parr); 
}
DMI::NumArrayFuncs::Destructor DMI::NumArrayFuncs::destructor[NumTypes][MaxLorrayRank] =
{
#define OneElement(N,T) &deleteArray<T,N>
  DoForAllArrayTypes1(OneLine,)
#undef OneElement
};


    
