#ifndef TypeId_h
#define TypeId_h 1

#include "Common/Lorrays.h"
#include "DMI/Common.h"
#include "DMI/DMI.h"
#include "DMI/TypeIterMacros.h"
#include "DMI/Registry.h"
#include "DMI/AtomicID.h"
#include <complex>
    
#ifndef LORRAYS_USE_BLITZ
  #error AIPS++ array support disabled for now
#endif

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


// Declare the standard types.
// Numbers will be explicitly assigned; note that TypeIds are negative
// so Tpbool will be -32, Tpchar -33, etc.
// Basic types occupy the space between -32 and -63, ranked by precision.
// Numerics are from -32 to -47, and string is -48.
// Note that order is vitally important: the numbers must be defined in
// the same order as in the DoForAllNumericTypes macro.

#pragma type +bool=32
#pragma type +char=33 +uchar=34 +short=35 +ushort=36 +int=37 +uint=38 
#pragma type +long=39 +ulong=40 +longlong=41 +ulonglong=42 
#pragma type +float=43 +double=44 +ldouble=45 
#pragma type +fcomplex=46 +dcomplex=47
#pragma type noinclude =string=48

// For arrays, numbers are explicitly assigned as type + 32*(rank+1) 
// but we don't define separate constants. Just these inlines here:

// TpArray(tpelem,ndim) returns the TypeId of array with element type tpelem,
// and rank ndim,
inline TypeId TpArray (TypeId tpelem,int ndim)
{ return - (32*ndim - tpelem.id()); }
// Alias for vector
inline TypeId TpVec (TypeId tpelem)
{ return TpArray(tpelem,1); }
// Alias for matrix
inline TypeId TpMat (TypeId tpelem)
{ return TpArray(tpelem,2); }
// Alias for cube
inline TypeId TpCube (TypeId tpelem)
{ return TpArray(tpelem,3); }

#pragma type :AtomicID

// these constants are used to distinguish built-ins from other types
// (note that actual numeric values are all negative)
const int TpFirstNumeric = -47, TpLastNumeric = -32,
      TpNumberOfNumerics = TpLastNumeric - TpFirstNumeric;

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
