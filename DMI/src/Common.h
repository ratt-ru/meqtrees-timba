//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C14B70800A2.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C14B70800A2.cm

//## begin module%3C14B70800A2.cp preserve=no
//## end module%3C14B70800A2.cp

//## Module: Common%3C14B70800A2; Package specification
//## Subsystem: <Top Level>
//## Source file: F:\LOFAR\dvl\LOFAR\CEP\CPA\PSCF\src\Common.h

#ifndef Common_h
#define Common_h 1

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif


//## begin module%3C14B70800A2.additionalIncludes preserve=no
//## end module%3C14B70800A2.additionalIncludes

//## begin module%3C14B70800A2.includes preserve=yes
#include <string>
#include <vector>
//## end module%3C14B70800A2.includes

//## begin module%3C14B70800A2.declarations preserve=no
//## end module%3C14B70800A2.declarations

//## begin module%3C14B70800A2.additionalDeclarations preserve=yes
using namespace std;



//## end module%3C14B70800A2.additionalDeclarations


//## begin Bool%3C14B6D4002F.preface preserve=yes
//## end Bool%3C14B6D4002F.preface

//## Class: Bool%3C14B6D4002F
//## Category: Common%3C14B6CE0199
//## Subsystem: <Top Level>
//## Persistence: Transient
//## Cardinality/Multiplicity: n




//## begin Bool%3C14B6D4002F.postscript preserve=yes
// Define capitalized Bool types.
// If available, use AIPS++ to do that.
#if defined(HAVE_AIPSPP)
# include <aips/aipstype.h>
#else
 typedef bool Bool;
 const Bool True = true;
 const Bool False = false;
#endif
//## end Bool%3C14B6D4002F.postscript

//## begin module%3C14B70800A2.epilog preserve=yes
//## end module%3C14B70800A2.epilog



#endif
