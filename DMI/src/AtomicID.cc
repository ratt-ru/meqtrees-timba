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
//## Source file: F:\lofar8\oms\LOFAR\DMI\src\AtomicID.cc

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
int aidRegistry_DMI();
static int dum = aidRegistry_DMI();
//## end module%3C10CC81015F.additionalDeclarations


// Class AtomicID 


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

int AtomicID::findName (const string &str)
{
  //## begin AtomicID::findName%3C68D5ED01F8.body preserve=yes
  for( size_t i=0; i<str.length(); i++ )
    if( !isdigit( str[i] ) )
      return registry.rfind(str);
  return atoi(str.c_str());
  //## end AtomicID::findName%3C68D5ED01F8.body
}

// Additional Declarations
  //## begin AtomicID%3BE970170297.declarations preserve=yes
//template class StaticRegistry<AtomicID,int,string>;
static AtomicID::Register
     null(AidNull.id(),"0"),
     any(AidAny.id(),"?"),
     wild(AidWildcard.id(),"*"),
     slash(AidSlash.id(),"/"),
     range(AidRange.id(),":"),
     empty(AidEmpty.id(),"_");
  //## end AtomicID%3BE970170297.declarations
// Class AidIndex 

// Additional Declarations
  //## begin AidIndex%3C553F440092.declarations preserve=yes
  //## end AidIndex%3C553F440092.declarations

//## begin module%3C10CC81015F.epilog preserve=yes
//## end module%3C10CC81015F.epilog
