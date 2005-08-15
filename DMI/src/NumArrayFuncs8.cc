#include "NumArrayFuncs.h"
    
  // Methods for the method table are naturally implemented via
  // templates. Refer to DMI::NumArray.cc to see how they are populated.

// populate the method tables via the DoForAll macros
#define OneLine(T,arg) { DoForAllArrayRanks1(OneElement,T) }
  


  
  
// templated method to copy return the shape of a Lorray
template<class T,int N>
static void returnShapeOfArray (LoShape &shape,const void *ptr)
{ 
  shape = static_cast<const blitz::Array<T,N>*>(ptr)->shape(); 
}
DMI::NumArrayFuncs::ShapeOfArray DMI::NumArrayFuncs::shapeOfArray[NumTypes][MaxLorrayRank] =
{
#define OneElement(N,T) &returnShapeOfArray<T,N>
  DoForAllArrayTypes1(OneLine,)
#undef OneElement
};
