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
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar8\oms\LOFAR\src-links\DMI\Common.h

#ifndef Common_h
#define Common_h 1

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


//## begin module%3C14B70800A2.epilog preserve=yes
// Define capitalized Bool types.
// If available, use AIPS++ to do that.
#if defined(HAVE_AIPSPP) || defined(AIPS_LINUX)
  #include <aips/aipstype.h>
#else
  typedef bool Bool;
  const Bool True = true;
  const Bool False = false;
#endif
//## end module%3C14B70800A2.epilog


#endif


// Detached code regions:
#if 0
//## begin Bool%3C14B6D4002F.postscript preserve=yes
//## end Bool%3C14B6D4002F.postscript

#endif
