//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC820357.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC820357.cm

//## begin module%3C10CC820357.cp preserve=no
//## end module%3C10CC820357.cp

//## Module: HIID%3C10CC820357; Package body
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\HIID.cc

//## begin module%3C10CC820357.additionalIncludes preserve=no
//## end module%3C10CC820357.additionalIncludes

//## begin module%3C10CC820357.includes preserve=yes
//## end module%3C10CC820357.includes

// HIID
#include "HIID.h"
//## begin module%3C10CC820357.declarations preserve=no
//## end module%3C10CC820357.declarations

//## begin module%3C10CC820357.additionalDeclarations preserve=yes
//## end module%3C10CC820357.additionalDeclarations


// Class HIID 


//## Other Operations (implementation)
HIID & HIID::add (HIID &other)
{
  //## begin HIID::add%3BE977510397.body preserve=yes
  if( other.atoms.empty() )
    return *this;
  int n = atoms.size();
  atoms.reserve(n+other.atoms.size());
  for( AtomsConstIter iter = other.atoms.begin(); iter != other.atoms.end(); iter++ )
    atoms[n++] = *iter;
  return *this;
  //## end HIID::add%3BE977510397.body
}

Bool HIID::matches (const HIID &other) const
{
  //## begin HIID::matches%3BE9792B0135.body preserve=yes
  if( other.length() > length() )  // other is longer - no match then
    return False;
  AtomsConstIter iter = atoms.begin(),
                 oiter = other.atoms.begin();
  for( ; iter != atoms.end() && oiter != other.atoms.end(); iter++,oiter++ )
  {
    if( iter->isWildcard() || oiter->isWildcard() )   // wildcard in either will match
      return True;
    if( !iter->matches(*oiter) )  // mismatch at this position - drop out
      return False;
  } 
  // got to end of one or the other? Then it's a match if both are at the end.
  return iter == atoms.end() && oiter == other.atoms.end();
  //## end HIID::matches%3BE9792B0135.body
}

string HIID::toString () const
{
  //## begin HIID::toString%3C0F8BD5004F.body preserve=yes
  string s("(null)");
  if( length()>0 )
  {
    AtomsConstIter iter = atoms.begin();
    s = iter->toString();
    for( ; iter != atoms.end(); iter++ )
      s += "." + iter->toString();
  }
  return s;
  //## end HIID::toString%3C0F8BD5004F.body
}

// Additional Declarations
  //## begin HIID%3BE96FE601C5.declarations preserve=yes
  //## end HIID%3BE96FE601C5.declarations

//## begin module%3C10CC820357.epilog preserve=yes
//## end module%3C10CC820357.epilog
