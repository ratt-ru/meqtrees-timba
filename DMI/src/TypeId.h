//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC8301F8.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC8301F8.cm

//## begin module%3C10CC8301F8.cp preserve=no
//## end module%3C10CC8301F8.cp

//## Module: TypeId%3C10CC8301F8; Package specification
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar8\oms\LOFAR\src-links\DMI\TypeId.h

#ifndef TypeId_h
#define TypeId_h 1

//## begin module%3C10CC8301F8.additionalIncludes preserve=no
#include "DMI/Common.h"
#include "DMI/DMI.h"
#include "DMI/TypeIterMacros.h"
//## end module%3C10CC8301F8.additionalIncludes

//## begin module%3C10CC8301F8.includes preserve=yes
#include "DMI/Registry.h"
#include <complex>
//## end module%3C10CC8301F8.includes

// AtomicID
#include "DMI/AtomicID.h"
//## begin module%3C10CC8301F8.declarations preserve=no
//## end module%3C10CC8301F8.declarations

//## begin module%3C10CC8301F8.additionalDeclarations preserve=yes
//## end module%3C10CC8301F8.additionalDeclarations


//## begin TypeId%3BFBA88F001D.preface preserve=yes
//## end TypeId%3BFBA88F001D.preface

//## Class: TypeId%3BFBA88F001D
//## Category: DOMIN0%3BEAB1F2006B; Global
//## Subsystem: DMI%3C10CC810155
//## Persistence: Transient
//## Cardinality/Multiplicity: n



//## Uses: <unnamed>%3BFBA8B500CC;AtomicID { -> }

typedef AtomicID TypeId;

//## begin TypeId%3BFBA88F001D.postscript preserve=yes

// standard type definitions
typedef unsigned char uchar;
typedef unsigned short ushort;
typedef unsigned int uint;
typedef unsigned long ulong;
typedef long long longlong;
typedef unsigned long long ulonglong;
typedef long double ldouble;
typedef complex<float> fcomplex;
typedef complex<double> dcomplex;

// arrays are supported for a limited subset of scalar types (for Glish
// compatibility)

// These are the type iterators for all arrayable types
// NB: for now, strings are disabled, until Ger adds the template instantiation
#define DoForAllArrayTypes2(Do,arg,sep) Do(bool,arg) sep Do(int,arg) sep Do(float,arg) sep Do(double,arg) sep Do(dcomplex,arg) sep Do(fcomplex,arg) 
#define DoForAllArrayTypes(Do,arg) DoForAllArrayTypes2(Do,arg,;)
#define DoForAllArrayTypes1(Do,arg) Do(bool,arg), Do(int,arg), Do(float,arg), Do(double,arg), Do(dcomplex,arg), Do(fcomplex,arg)

// Another iterator for numeric but non-arrayble types (this is needed
// for, e.g., template instantiation, where you define a specialization for
// arrayable types, and want to instantiate the non-arrayable ones from
// the default template)
#define DoForAllNonArrayTypes2(Do,arg,sep) Do(char,arg) sep Do(uchar,arg) sep Do(short,arg) sep Do(ushort,arg) sep Do(uint,arg) sep Do(long,arg) sep Do(ulong,arg) sep Do(longlong,arg) sep Do(ulonglong,arg) sep Do(ldouble,arg) 
#define DoForAllNonArrayTypes(Do,arg) DoForAllNonArrayTypes2(Do,arg,;)


template<class T> class Array;
#define __typedefArray(T,arg) typedef Array<T> Array_##T;
DoForAllArrayTypes(__typedefArray,);

// Declare the standard types (':' prefix means do not generate constructors)
// Numbers will be explicitly assigned; note that TypeIDs are negative
// so Tpchar will be -10, Tpuchar -11, etc.
#pragma type +char=10 +uchar=11 +short=12 +ushort=13 +int=14 +uint=15 
#pragma type +long=16 +ulong=17 +longlong=18 +ulonglong=19 
#pragma type +float=20 +double=21 +ldouble=22 
#pragma type +fcomplex=23 +dcomplex=24
#pragma type +bool=25

#pragma type noinclude =string=29

// For arrays, numebrs are explicitly assigned as type+20
#pragma type %Array_int=34 
#pragma type %Array_float=40 %Array_double=41 
#pragma type %Array_fcomplex=43 %Array_dcomplex=44
#pragma type %Array_bool=45

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


//## end TypeId%3BFBA88F001D.postscript

//## begin module%3C10CC8301F8.epilog preserve=yes
//## end module%3C10CC8301F8.epilog


#endif
