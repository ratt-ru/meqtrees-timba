#include "DynamicTypeManager.h"

namespace DMI
{    
    
DefineRegistry(DynamicTypeManager,0);

ObjRef DynamicTypeManager::construct (TypeId tid, BlockSet& bset)
{
  if( tid == 0 )
    tid = static_cast<const BObj::Header *>(bset.front()->data())->tid;
  BObj * pobj = construct(tid);
  if( pobj )
  {
    ObjRef ref(pobj);
    pobj->fromBlock(bset);
    return ref;
  }
  return ObjRef();
}

//##ModelId=3BE96C5F03A7
BObj * DynamicTypeManager::construct (TypeId tid, BlockSet& bset, int n)
{
  if( tid == 0 )
    tid = static_cast<const BObj::Header *>(bset.front()->data())->tid;
  BObj *obj = construct(tid,n);
  for( int i=0; i<(n?n:1); i++ )
    obj[i].fromBlock(bset);
  return obj;
}

//##ModelId=3BE96C7402D5
BObj * DynamicTypeManager::construct (TypeId tid, int n)
{
  cdebug1(2)<<"DynTypeMgr: constructing "<<tid.toString();
  if( n ) 
    cdebug1(2)<<"["<<n<<"]";
  cdebug1(2)<<": ";
  PtrConstructor ptr = registry.find(tid);
  FailWhen( !ptr,"Unregistered type "+tid.toString() );
  BObj *obj = (*ptr)(n);
  dprintf1(2)(" @%p\n",obj);
  return obj;
}

//##ModelId=3BF905EE020E
bool DynamicTypeManager::isRegistered (TypeId tid)
{
  return registry.find(tid) != 0;
}


};
