#include <Common/Debug.h>    
#include "ApplicationBase.h"
#include "AID-AppUtils.h"
    
InitDebugContext(ApplicationBase,"Applications");

static int dum = aidRegistry_AppUtils ();
    
//##ModelId=3E43BBE301BA
ApplicationBase::ApplicationBase(AppControlAgent &ctrl)
    : thread_(0),control_(ctrl)
{
  controlref_.attach(ctrl,DMI::WRITE);
}

//##ModelId=3E3FE7660131
ApplicationBase::~ApplicationBase()
{
}
    
//##ModelId=3E3FE1C8036D
int ApplicationBase::state() const
{
  return control().state();
}

//##ModelId=3E3FE1CD009F
string ApplicationBase::stateString () const
{
  return control().stateString();
}

//##ModelId=3E3FE1BB0220
Thread::ThrID ApplicationBase::runThread (DataRecord::Ref &initrec,bool del_on_exit)
{
  cdebug(2)<<"running in separate thread\n";
  initrec_cache = initrec;
  delete_on_exit = del_on_exit;
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
