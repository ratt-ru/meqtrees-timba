//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC830069.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC830069.cm

//## begin module%3C10CC830069.cp preserve=no
//## end module%3C10CC830069.cp

//## Module: NestableContainer%3C10CC830069; Package body
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\NestableContainer.cc

//## begin module%3C10CC830069.additionalIncludes preserve=no
//## end module%3C10CC830069.additionalIncludes

//## begin module%3C10CC830069.includes preserve=yes
//## end module%3C10CC830069.includes

// NestableContainer
#include "NestableContainer.h"
//## begin module%3C10CC830069.declarations preserve=no
//## end module%3C10CC830069.declarations

//## begin module%3C10CC830069.additionalDeclarations preserve=yes
DefineRegistry(NestableContainer,False);
//## end module%3C10CC830069.additionalDeclarations


// Class NestableContainer 


//## Other Operations (implementation)
bool NestableContainer::getFieldInfo (const HIID &id, TypeId &tid, bool& can_write, bool no_throw) const
{
  //## begin NestableContainer::getFieldInfo%3BE9828D0266.body preserve=yes
  if( no_throw )
  {
    try {
      return get(id,tid,can_write) ? True : False;
    } catch( Debug::Error &x ) {
      return False;
    }
  }
  else
    return get(id,tid,can_write) ? True : False;
  //## end NestableContainer::getFieldInfo%3BE9828D0266.body
}

bool NestableContainer::hasField (const HIID &id) const
{
  //## begin NestableContainer::hasField%3C56AC2902A1.body preserve=yes
  TypeId dum1; bool dum2;
  return getFieldInfo(id,dum1,dum2,True);
  //## end NestableContainer::hasField%3C56AC2902A1.body
}

TypeId NestableContainer::fieldType (const HIID &id) const
{
  //## begin NestableContainer::fieldType%3C5958C203A0.body preserve=yes
  TypeId tid; bool dum2;
  return getFieldInfo(id,tid,dum2,True) ? tid : NullType;
  //## end NestableContainer::fieldType%3C5958C203A0.body
}

// Additional Declarations
  //## begin NestableContainer%3BE97CE100AF.declarations preserve=yes
  //## end NestableContainer%3BE97CE100AF.declarations

//## begin module%3C10CC830069.epilog preserve=yes
//## end module%3C10CC830069.epilog
