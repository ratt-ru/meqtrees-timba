//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC81015F.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC81015F.cm

//## begin module%3C10CC81015F.cp preserve=no
//## end module%3C10CC81015F.cp

//## Module: AtomicID%3C10CC81015F; Package body
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\AtomicID.cc

//## begin module%3C10CC81015F.additionalIncludes preserve=no
//## end module%3C10CC81015F.additionalIncludes

//## begin module%3C10CC81015F.includes preserve=yes
#include <ctype.h>
#include "DMI.h"
//## end module%3C10CC81015F.includes

// AtomicID
#include "AtomicID.h"
//## begin module%3C10CC81015F.declarations preserve=no
//## end module%3C10CC81015F.declarations

//## begin module%3C10CC81015F.additionalDeclarations preserve=yes
DefineBiRegistry(AtomicID,0,"");

// pull in all auto-generated registry definitions
#include "AID-Registry.h"
//## end module%3C10CC81015F.additionalDeclarations


// Class AtomicID 

AtomicID::AtomicID (const string &str)
  //## begin AtomicID::AtomicID%3C5E74CB0112.hasinit preserve=no
  //## end AtomicID::AtomicID%3C5E74CB0112.hasinit
  //## begin AtomicID::AtomicID%3C5E74CB0112.initialization preserve=yes
  //## end AtomicID::AtomicID%3C5E74CB0112.initialization
{
  //## begin AtomicID::AtomicID%3C5E74CB0112.body preserve=yes
  // check if string consists only of digits, if a non-digit was
  // found, then assume it's a name and look it up in the registry
  for( size_t i=0; i<str.length(); i++ )
    if( !isdigit( str[i] ) )
    {
      aid = registry.rfind(str);
      return;
    }
  aid = atoi(str.c_str());
  //## end AtomicID::AtomicID%3C5E74CB0112.body
}



//## Other Operations (implementation)
string AtomicID::toString () const
{
  //## begin AtomicID::toString%3BE9709700A7.body preserve=yes
  char s[64];
  // if ID is an index, return that
  int idx = index();
  if( idx>=0 )
  {
    sprintf(s,"%d",idx);
    return s;
  }
  // lookup ID in symbolic name map, return if found
  string name = registry.find(id());
  if( name.length() )
    return name;
  // else return unknown ID
  sprintf(s,"[?%d]",id());
  return s;
  //## end AtomicID::toString%3BE9709700A7.body
}

// Additional Declarations
  //## begin AtomicID%3BE970170297.declarations preserve=yes
//template class StaticRegistry<AtomicID,int,string>;
static AtomicID::Register
     null (AidNull.id(),"0"),
     any (AidAny.id(),"?"),
     wild(AidWildcard.id(),"*"),
     dot(AidDot.id(),":");
  //## end AtomicID%3BE970170297.declarations
// Class AidIndex 

// Additional Declarations
  //## begin AidIndex%3C553F440092.declarations preserve=yes
  //## end AidIndex%3C553F440092.declarations

//## begin module%3C10CC81015F.epilog preserve=yes
//## end module%3C10CC81015F.epilog
