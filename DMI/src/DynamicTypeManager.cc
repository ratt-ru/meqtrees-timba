//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC8202B7.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC8202B7.cm

//## begin module%3C10CC8202B7.cp preserve=no
//## end module%3C10CC8202B7.cp

//## Module: DynamicTypeManager%3C10CC8202B7; Package body
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\DynamicTypeManager.cc

//## begin module%3C10CC8202B7.additionalIncludes preserve=no
//## end module%3C10CC8202B7.additionalIncludes

//## begin module%3C10CC8202B7.includes preserve=yes
//## end module%3C10CC8202B7.includes

// DynamicTypeManager
#include "DMI/DynamicTypeManager.h"
//## begin module%3C10CC8202B7.declarations preserve=no
//## end module%3C10CC8202B7.declarations

//## begin module%3C10CC8202B7.additionalDeclarations preserve=yes
DefineRegistry(DynamicTypeManager,0);
//## end module%3C10CC8202B7.additionalDeclarations


// Class Utility DynamicTypeManager 


//## Other Operations (implementation)
BlockableObject * DynamicTypeManager::construct (TypeId tid, BlockSet& bset, int n)
{
  //## begin DynamicTypeManager::construct%3BE96C5F03A7.body preserve=yes
  BlockableObject *obj = construct(tid,n);
  for( int i=0; i<(n?n:1); i++ )
    obj[i].fromBlock(bset);
  return obj;
  //## end DynamicTypeManager::construct%3BE96C5F03A7.body
}

BlockableObject * DynamicTypeManager::construct (TypeId tid, int n)
{
  //## begin DynamicTypeManager::construct%3BE96C7402D5.body preserve=yes
  cdebug1(2)<<"DynTypeMgr: constructing "<<tid.toString();
  if( n ) 
    cdebug1(2)<<"["<<n<<"]";
  cdebug1(2)<<": ";
  PtrConstructor ptr = registry.find(tid);
  FailWhen( !ptr,"Unregistered type "+tid.toString() );
  BlockableObject *obj = (*ptr)(n);
  dprintf1(2)(" @%p\n",obj);
  return obj;
  //## end DynamicTypeManager::construct%3BE96C7402D5.body
}

bool DynamicTypeManager::isRegistered (TypeId tid)
{
  //## begin DynamicTypeManager::isRegistered%3BF905EE020E.body preserve=yes
  return registry.find(tid) != 0;
  //## end DynamicTypeManager::isRegistered%3BF905EE020E.body
}

// Additional Declarations
  //## begin DynamicTypeManager%3BE96C040003.declarations preserve=yes
  //## end DynamicTypeManager%3BE96C040003.declarations

//## begin module%3C10CC8202B7.epilog preserve=yes
//## end module%3C10CC8202B7.epilog


// Detached code regions:
#if 0

#endif
