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
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\TypeId.h

#ifndef TypeId_h
#define TypeId_h 1

//## begin module%3C10CC8301F8.additionalIncludes preserve=no
#include "Common.h"
#include "DMI.h"
//## end module%3C10CC8301F8.additionalIncludes

//## begin module%3C10CC8301F8.includes preserve=yes
#include "Registry.h"
//## end module%3C10CC8301F8.includes

// AtomicID
#include "AtomicID.h"
//## begin module%3C10CC8301F8.declarations preserve=no
//## end module%3C10CC8301F8.declarations

//## begin module%3C10CC8301F8.additionalDeclarations preserve=yes
//## end module%3C10CC8301F8.additionalDeclarations


//## begin TypeId%3BFBA88F001D.preface preserve=yes
//## end TypeId%3BFBA88F001D.preface

//## Class: TypeId%3BFBA88F001D
//## Category: PSCF::DMI%3BEAB1F2006B; Global
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
typedef long double ldouble;

// Declare the standard types (':' prefix means do not generate constructors)
// Numbers will be explicitly assigned; note that TypeIDs are negative
// so Tpchar will be -10, Tpuchar -11, etc.
#pragma typegroup Global
#pragma types +char=10 +uchar=11 +short=12 +ushort=13 +int=14 +uint=15 
#pragma types +long=16 +ulong=17 +float=18 +double=19 +ldouble=20 +bool=21
#pragma types -string=30

#pragma types :AtomicID

// The null type 
const TypeId NullType(0);

//## end TypeId%3BFBA88F001D.postscript

//## begin module%3C10CC8301F8.epilog preserve=yes
//## end module%3C10CC8301F8.epilog


#endif
