#include "DMI/TypeInfo.h"
#include "DMI/TypeIterMacros.h"

static AtomicID::Register reg1(TpNumeric,"Numeric"),
    reg2(TpIncomplete,"Incomplete"),
    reg3(TpObject,"Object");

// This inserts AtomicID::Register definitions for all array types and ranks
#define _regarray(type,rank) static AtomicID::Register reg##type##rank(TpArray(Tp##type,rank),"Array(" #type "," #rank ")");
#define _regrank(rank,arg) DoForAllArrayTypes(_regarray,rank);
DoForAllArrayRanks(_regrank,);
#undef _regarray
#undef _regrank

// Defines the TypeInfo registry    
DefineRegistry(TypeInfoReg,TypeInfo::NONE);

// -----------------------------------------------------------------------
// type converter, scalar-scalar
// -----------------------------------------------------------------------
//--- templated implementation of a type converter, scalar to scalar
template<class From,class To> 
bool _convertScaSca (const void * from,void * to)
{ 
  *static_cast<To*>(to) = To(*static_cast<const From *>(from)); 
  return True;
}
//    special case for complex: use real part
template<class From,class To> 
bool _convertComplexScaSca (const void * from,void * to)
{ 
  *static_cast<To*>(to) = To(static_cast<const From *>(from)->real()); 
  return True;
}
//--- convert scalar to single-element vector
template<class From,class To> 
bool _convertScaVec (const void * from,void * to)
{ 
  blitz::Array<To,1> &arr = *static_cast<blitz::Array<To,1>*>(to);
  if( arr.numElements() != 1 )
    return False;
  *(arr.data()) = To(*static_cast<const From *>(from)); 
  return True;
}
//    special case for complex: use real part
template<class From,class To> 
bool _convertComplexScaVec (const void * from,void * to)
{ 
  blitz::Array<To,1> &arr = *static_cast<blitz::Array<To,1>*>(to);
  if( arr.numElements() != 1 )
    return False;
  *(arr.data()) = To(static_cast<const From *>(from)->real()); 
  return True;
}
//--- convert single-element vector to scalar
template<class From,class To> 
bool _convertVecSca (const void * from,void * to)
{ 
  const blitz::Array<From,1> &arr = *static_cast<const blitz::Array<From,1>*>(from);
  if( arr.numElements() != 1 )
    return False;
  *static_cast<To*>(to) = To(*(arr.data()));
  return True;
}
//    special case for complex: use real part
template<class From,class To> 
bool _convertComplexVecSca (const void * from,void * to)
{ 
  const blitz::Array<From,1> &arr 
      = *static_cast<const blitz::Array<From,1>*>(from);
  if( arr.numElements() != 1 )
    return False;
  *static_cast<To*>(to) = To(arr.data()->real());
  return True;
}

// This defines the conversion matrices
#undef From
#define From(type,arg) _convertScaSca<arg,type>
#undef FromComplex
#define FromComplex(type,arg) _convertComplexScaSca<arg,type>
TypeConverter _typeconverters_sca_sca[16][16] = 
{
  { DoForAllNumericTypes1(From,bool) },
  { DoForAllNumericTypes1(From,char) },
  { DoForAllNumericTypes1(From,uchar) },
  { DoForAllNumericTypes1(From,short) },
  { DoForAllNumericTypes1(From,ushort) },
  { DoForAllNumericTypes1(From,int) },
  { DoForAllNumericTypes1(From,uint) },
  { DoForAllNumericTypes1(From,long) },
  { DoForAllNumericTypes1(From,ulong) },
  { DoForAllNumericTypes1(From,longlong) },
  { DoForAllNumericTypes1(From,ulonglong) },
  { DoForAllNumericTypes1(From,float) },
  { DoForAllNumericTypes1(From,double) },
  { DoForAllNumericTypes1(From,ldouble) },
  { DoForAllNumericTypes1(FromComplex,fcomplex) },
  { DoForAllNumericTypes1(FromComplex,dcomplex) } 
};

// This defines the conversion matrices
#undef From
#define From(type,arg) _convertVecSca<arg,type>
#undef FromComplex
#define FromComplex(type,arg) _convertComplexVecSca<arg,type>
TypeConverter _typeconverters_vec_sca[16][16] = 
{
  { DoForAllNumericTypes1(From,bool) },
  { DoForAllNumericTypes1(From,char) },
  { DoForAllNumericTypes1(From,uchar) },
  { DoForAllNumericTypes1(From,short) },
  { DoForAllNumericTypes1(From,ushort) },
  { DoForAllNumericTypes1(From,int) },
  { DoForAllNumericTypes1(From,uint) },
  { DoForAllNumericTypes1(From,long) },
  { DoForAllNumericTypes1(From,ulong) },
  { DoForAllNumericTypes1(From,longlong) },
  { DoForAllNumericTypes1(From,ulonglong) },
  { DoForAllNumericTypes1(From,float) },
  { DoForAllNumericTypes1(From,double) },
  { DoForAllNumericTypes1(From,ldouble) },
  { DoForAllNumericTypes1(FromComplex,fcomplex) },
  { DoForAllNumericTypes1(FromComplex,dcomplex) } 
};

// This defines the conversion matrices
#undef From
#define From(type,arg) _convertScaVec<arg,type>
#undef FromComplex
#define FromComplex(type,arg) _convertComplexScaVec<arg,type>
TypeConverter _typeconverters_sca_vec[16][16] = 
{
  { DoForAllNumericTypes1(From,bool) },
  { DoForAllNumericTypes1(From,char) },
  { DoForAllNumericTypes1(From,uchar) },
  { DoForAllNumericTypes1(From,short) },
  { DoForAllNumericTypes1(From,ushort) },
  { DoForAllNumericTypes1(From,int) },
  { DoForAllNumericTypes1(From,uint) },
  { DoForAllNumericTypes1(From,long) },
  { DoForAllNumericTypes1(From,ulong) },
  { DoForAllNumericTypes1(From,longlong) },
  { DoForAllNumericTypes1(From,ulonglong) },
  { DoForAllNumericTypes1(From,float) },
  { DoForAllNumericTypes1(From,double) },
  { DoForAllNumericTypes1(From,ldouble) },
  { DoForAllNumericTypes1(FromComplex,fcomplex) },
  { DoForAllNumericTypes1(FromComplex,dcomplex) } 
};

