#ifndef TypeId_h
#define TypeId_h 1

#include "DMI/Common.h"
#include "DMI/DMI.h"
#include "DMI/TypeIterMacros.h"

#include "DMI/Registry.h"
#include <complex>

// AtomicID
#include "DMI/AtomicID.h"

//##ModelId=3BFBA88F001D

typedef AtomicID TypeId;


// standard type definitions
//##ModelId=3DB9343F00F1
typedef unsigned char uchar;
//##ModelId=3DB9343F01C4
typedef unsigned short ushort;
//##ModelId=3DB9343F012D
typedef unsigned int uint;
//##ModelId=3DB9343F015F
typedef unsigned long ulong;
//##ModelId=3DB9343F00B5
typedef long long longlong;
//##ModelId=3DB9343F0191
typedef unsigned long long ulonglong;
//##ModelId=3DB9343F0051
typedef long double ldouble;
//##ModelId=3DB9343F0015
typedef complex<float> fcomplex;
//##ModelId=3DB9343E03CB
typedef complex<double> dcomplex;

#ifndef DoForAllNumericTypes1
// Defines alternative version of the "for all numeric types"
// macro, with comma as separator
#define DoForAllNumericTypes1(Do,arg) \
        Do(char,arg) , \
        Do(uchar,arg) , \
        Do(short,arg) , \
        Do(ushort,arg) , \
        Do(int,arg) , \
        Do(uint,arg) , \
        Do(long,arg) , \
        Do(ulong,arg) , \
        Do(longlong,arg) , \
        Do(ulonglong,arg) , \
        Do(float,arg) , \
        Do(double,arg) , \
        Do(ldouble,arg) , \
        Do(fcomplex,arg) , \
        Do(dcomplex,arg) , \
        Do(bool,arg) 
#endif

// arrays are supported for a limited subset of scalar types (for Glish
// compatibility)

#ifndef DoForAllArrayTypes

// These are the type iterators for all arrayable types
// NB: for now, strings are disabled, until Ger adds the template instantiation
#define DoForAllArrayTypes_Sep(Do,arg,sep) Do(bool,arg) sep Do(uchar,arg) sep Do(short,arg) sep Do(int,arg) sep Do(float,arg) sep Do(double,arg) sep Do(dcomplex,arg) sep Do(fcomplex,arg) 
#define DoForAllArrayTypes(Do,arg) DoForAllArrayTypes_Sep(Do,arg,;)
#define DoForAllArrayTypes1(Do,arg) Do(bool,arg), Do(uchar,arg), Do(short,arg), Do(int,arg), Do(float,arg), Do(double,arg), Do(dcomplex,arg), Do(fcomplex,arg)

// Another iterator for numeric but non-arrayble types (this is needed
// for, e.g., template instantiation, where you define a specialization for
// arrayable types, and want to instantiate the non-arrayable ones from
// the default template)
#define DoForAllNonArrayTypes_Sep(Do,arg,sep) Do(char,arg) sep Do(ushort,arg) sep Do(uint,arg) sep Do(long,arg) sep Do(ulong,arg) sep Do(longlong,arg) sep Do(ulonglong,arg) sep Do(ldouble,arg) 
#define DoForAllNonArrayTypes(Do,arg) DoForAllNonArrayTypes_Sep(Do,arg,;)

#endif

template<class T> class Array;
#define __typedefArray(T,arg) typedef Array<T> Array_##T;
DoForAllArrayTypes(__typedefArray,);
__typedefArray(string,);

// Declare the standard types (':' prefix means do not generate constructors)
// Numbers will be explicitly assigned; note that TypeIDs are negative
// so Tpchar will be -10, Tpuchar -11, etc.
#pragma type +char=10 +uchar=11 +short=12 +ushort=13 +int=14 +uint=15 
#pragma type +long=16 +ulong=17 +longlong=18 +ulonglong=19 
#pragma type +float=20 +double=21 +ldouble=22 
#pragma type +fcomplex=23 +dcomplex=24
#pragma type +bool=25

#pragma type noinclude =string=29

// For arrays, numbers are explicitly assigned as type+20

#pragma type %Array_uchar=31 %Array_int=34 %Array_short=32 
#pragma type %Array_float=40 %Array_double=41 
#pragma type %Array_fcomplex=43 %Array_dcomplex=44
#pragma type %Array_bool=45 %Array_string=49

// commented out for now, to support a limited subset
//
//pragma type %Array_char=30 %Array_uchar=31 %Array_short=32 %Array_ushort=33 %Array_int=34 %Array_uint=35 
//pragma type %Array_long=36 %Array_ulong=37 %Array_longlong=38 %Array_ulonglong=39 
//pragma type %Array_float=40 %Array_double=41 %Array_ldouble=42 
//pragma type %Array_fcomplex=43 %Array_dcomplex=44
//pragma type %Array_bool=45

#pragma type :AtomicID

// these constants are used to distinguish built-ins from other types
// (note that actual numeric values are all negative)
const int TpFirstNumeric = -25, TpLastNumeric = -10;

// Offset between type and Array_type
const int tpElemToArrayOffset = -20;

// Some special type constants
// The null type 
const TypeId NullType(0),TpNull(0);
// Numeric type
const TypeId TpNumeric(-9);
// Incomplete type
const TypeId TpIncomplete(-8);
// Dereferenced type (see NestableContainer::get())
const TypeId TpObject(-7);




#endif
