#include "AppRegistry.h"
    
DefineRegistry(AppRegistry,0);

//##ModelId=3E3013C2008F
void AppRegistry::registerApp (AtomicID id, Constructor ctor)
{
  Constructor ctor0 = registry.find(id);
  if( ctor0 )
  {
    FailWhen( ctor0 != ctor,"App "+id.toString()+" already registered with different constructor" );
  }
  else
    registry.add(id,ctor);
}

//##ModelId=3E30141D00CA
bool AppRegistry::isRegistered (AtomicID id)
{
  return registry.find(id) != 0;
}

//##ModelId=3E30143C0391
int AppRegistry::construct (WPRef &out, AtomicID id, DataRecord::Ref &initrec)
{
  Constructor ctor = registry.find(id);
  if( !ctor )
    return 0;
  out = (*ctor)(initrec);
  FailWhen( !out.valid(),"constructor for "+id.toString()+" returned invalid ref" );
  return 1;
}

