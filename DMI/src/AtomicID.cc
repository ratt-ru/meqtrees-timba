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
#include "DMI.h"
//## end module%3C10CC81015F.includes

// AtomicID
#include "AtomicID.h"
//## begin module%3C10CC81015F.declarations preserve=no
//## end module%3C10CC81015F.declarations

//## begin module%3C10CC81015F.additionalDeclarations preserve=yes
//## end module%3C10CC81015F.additionalDeclarations


// Class AtomicID::Register 

AtomicID::Register::Register (int id, const string &name)
  //## begin AtomicID::Register::Register%3C1DB26B00CD.hasinit preserve=no
  //## end AtomicID::Register::Register%3C1DB26B00CD.hasinit
  //## begin AtomicID::Register::Register%3C1DB26B00CD.initialization preserve=yes
  //## end AtomicID::Register::Register%3C1DB26B00CD.initialization
{
  //## begin AtomicID::Register::Register%3C1DB26B00CD.body preserve=yes
  AtomicID::registerName(id,name);
  //## end AtomicID::Register::Register%3C1DB26B00CD.body
}


// Additional Declarations
  //## begin AtomicID::Register%3C1DB25B039C.declarations preserve=yes
  //## end AtomicID::Register%3C1DB25B039C.declarations

// Class AtomicID 

//## begin AtomicID::names%3BEBE9870055.attr preserve=no  private: static map<int,string> {U} 
map<int,string> AtomicID::names;
//## end AtomicID::names%3BEBE9870055.attr


//## Other Operations (implementation)
string AtomicID::toString () const
{
  //## begin AtomicID::toString%3BE9709700A7.body preserve=yes
  // lookup ID in symbolic name map, return if found
  CMI found = names.find(id);
  if( found != names.end() )
    return found->second;
  // else return unknown ID
  char s[64];
  sprintf(s,"[!%d]",id);
  return s;
  //## end AtomicID::toString%3BE9709700A7.body
}

void AtomicID::registerName (int n, const string &name)
{
  //## begin AtomicID::registerName%3C1A2B2101E8.body preserve=yes
  if( names.find(n) != names.end() && names[n] != name )
    Throw1("AtomicID '"+name+"' previously defined as '"+names[n]+"'");
  names[n] = name;
  //## end AtomicID::registerName%3C1A2B2101E8.body
}

// Additional Declarations
  //## begin AtomicID%3BE970170297.declarations preserve=yes
static AtomicID::Register 
     any ((int)AidAny,"?"),
     wild((int)AidWildcard,"*");
  //## end AtomicID%3BE970170297.declarations
//## begin module%3C10CC81015F.epilog preserve=yes
//## end module%3C10CC81015F.epilog
