#include "DynamicTypeManager.h"

DefineRegistry(DynamicTypeManager,0);


BlockableObject * DynamicTypeManager::construct (TypeId tid, BlockSet& bset, int n)
{
  BlockableObject *obj = construct(tid,n);
  for( int i=0; i<(n?n:1); i++ )
    obj[i].fromBlock(bset);
  return obj;
}

//##ModelId=3BE96C7402D5
BlockableObject * DynamicTypeManager::construct (TypeId tid, int n)
{
  cdebug1(2)<<"DynTypeMgr: constructing "<<tid.toString();
  if( n ) 
    cdebug1(2)<<"["<<n<<"]";
  cdebug1(2)<<": ";
  PtrConstructor ptr = registry.find(tid);
  FailWhen( !ptr,"Unregistered type "+tid.toString() );
  BlockableObject *obj = (*ptr)(n);
  dprintf1(2)(" @%p\n",obj);
  return obj;
}

//##ModelId=3BF905EE020E
bool DynamicTypeManager::isRegistered (TypeId tid)
{
  return registry.find(tid) != 0;
}


