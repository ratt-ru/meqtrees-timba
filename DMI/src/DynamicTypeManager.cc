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
#include "DynamicTypeManager.h"
//## begin module%3C10CC8202B7.declarations preserve=no
//## end module%3C10CC8202B7.declarations

//## begin module%3C10CC8202B7.additionalDeclarations preserve=yes
//## end module%3C10CC8202B7.additionalDeclarations


// Class Utility DynamicTypeManager 

//## begin DynamicTypeManager::constructor_map%3BE96C8901DB.attr preserve=no  private: static map<int,DynamicTypeManager::PtrConstructor> {U} 
map<int,DynamicTypeManager::PtrConstructor> DynamicTypeManager::constructor_map;
//## end DynamicTypeManager::constructor_map%3BE96C8901DB.attr


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
  cdebug(2)<<"DynTypeMgr: constructing "<<tid.toString();
  if( n ) 
    cdebug(2)<<"["<<n<<"]";
  cdebug(2)<<": ";
  FailWhen1( !isRegistered(tid),"Unregistered type "+tid.toString() );
  BlockableObject *obj = (*(constructor_map[tid]))(n);
  dprintf(2)(" @%p\n",obj);
  return obj;
  //## end DynamicTypeManager::construct%3BE96C7402D5.body
}

void DynamicTypeManager::registerType (TypeId tid, PtrConstructor constructor)
{
  //## begin DynamicTypeManager::registerType%3BE96C6D0090.body preserve=yes
  cdebug(2)<<"DynTypeMgr: registering type "<<tid.toString()<<endl;
  if( isRegistered(tid) && constructor_map[tid] != constructor )
    Throw1("Redefining constructor for type "+tid.toString());
  constructor_map[tid] = constructor;
  //## end DynamicTypeManager::registerType%3BE96C6D0090.body
}

bool DynamicTypeManager::isRegistered (TypeId tid)
{
  //## begin DynamicTypeManager::isRegistered%3BF905EE020E.body preserve=yes
  return constructor_map.find(tid) != constructor_map.end();
  //## end DynamicTypeManager::isRegistered%3BF905EE020E.body
}

// Additional Declarations
  //## begin DynamicTypeManager%3BE96C040003.declarations preserve=yes
  //## end DynamicTypeManager%3BE96C040003.declarations

//## begin module%3C10CC8202B7.epilog preserve=yes
//## end module%3C10CC8202B7.epilog
