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

// This is a templated implementation of a type converter 
// Implemented as a template (but can be re-done explicitly by manually
// definining a shitload of functions
template<class From,class To> 
void _convertScalar( const void * from,void * to )
{ 
  *static_cast<To*>(to) = (To) *static_cast<const From *>(from); 
}

template<class From,class To> 
void _convertComplex( const void * from,void * to )
{ 
  *static_cast<To*>(to) = (To) static_cast<const From *>(from)->real(); 
}

//template<> 
//void _convertScalar<dcomplex,class To>( const void * from,void * to )
//{ 
//  *static_cast<To*>(to) = (To) static_cast<const dcomplex *>(from)->real(); 
//}

// This defines the conversion matrix
#undef From
#define From(type,arg) _convertScalar<arg,type>
#undef FromComplex
#define FromComplex(type,arg) _convertComplex<arg,type>
TypeConverter _typeconverters[16][16] = {
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
  { DoForAllNumericTypes1(FromComplex,dcomplex) },
  { DoForAllNumericTypes1(From,bool) } };

