#include "ApplicationBase.h"
#include <Common/Debug.h>    
    
InitDebugContext(ApplicationBase,"Applications");
    
//##ModelId=3E3FE4020002
ApplicationBase::ApplicationBase()
    : thread_(0)
{
}

//##ModelId=3E3FE7660131
ApplicationBase::~ApplicationBase()
{
}
    
//##ModelId=3E3FE1C8036D
int ApplicationBase::state() const
{
  return 0;
}

//##ModelId=3E3FE1CD009F
string ApplicationBase::stateString () const
{
  return Debug::ssprintf("%d",state());
}

//##ModelId=3E3FE1BB0220
Thread::ThrID ApplicationBase::runThread (DataRecord::Ref &initrec)
{
  cdebug(2)<<"running in separate thread\n";
  initrec_cache = initrec;
  thread_ = Thread::create(startThread,this);
  cdebug(2)<<"launched as thread "<<thread_<<endl;
  return thread_;
}

//##ModelId=3E3FE1DD017A
void * ApplicationBase::startThread (void *arg)
{
  ApplicationBase *object = static_cast<ApplicationBase*>(arg);
  object->run(object->initrec_cache);
  return 0;
}


string ApplicationBase::sdebug (int,const string &,const char *name) const
{
  return name ? name : "App";
}
