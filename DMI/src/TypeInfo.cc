#include "TypeInfo.h"
#include "TypeIterMacros.h"

static AtomicID::Register reg1(TpNumeric,"Numeric"),
    reg2(TpIncomplete,"Incomplete"),
    reg3(TpObject,"Object");

    
// Defines the TypeInfo registry    
DefineRegistry(TypeInfoReg,TypeInfo::NONE);

// This is a templated implementation of a type converter 
// Implemented as a template (but can be re-done explicitly by manually
// definiting a shitload of functions
template<class From,class To> 
void _convertScalar( const void * from,void * to )
{ 
  *static_cast<To*>(to) = (To) *static_cast<const From *>(from); 
}

// This defines the conversion matrix
#undef From
#define From(type,arg) _convertScalar<arg,type>
TypeConverter _typeconverters[14][14] = {
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
  { DoForAllNumericTypes1(From,bool) } };

