#include <Common/Debug.h>    
#include "ApplicationBase.h"
#include "AID-AppUtils.h"
    
InitDebugContext(ApplicationBase,"Applications");

static int dum = aidRegistry_AppUtils ();
    
//##ModelId=3E43BBE301BA
ApplicationBase::ApplicationBase()
    : thread_(0),control_(0)
{
}

//##ModelId=3E3FE7660131
ApplicationBase::~ApplicationBase()
{
}

//##ModelId=3E77212C02CD
void ApplicationBase::attach (AppControlAgent *ctrl, int flags)
{
  AppAgent::Ref ref(ctrl,flags);
  FailWhen(control_,"control agent already attached");
  control_ = ctrl;
  attachRef(ref);
}

//##ModelId=3E7721560344
void ApplicationBase::attach (VisAgent::InputAgent *, int)
{
  Throw("can't attach input agent to this application");
}

//##ModelId=3E7721810096
void ApplicationBase::attach (VisAgent::OutputAgent *, int)
{
  Throw("can't attach output agent to this application");
}

//##ModelId=3E7722D50064
void ApplicationBase::attachRef (AppAgent::Ref::Xfer & agent)
{
  agentrefs_.push_front(agent);
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

//##ModelId=3E7894E90398
bool ApplicationBase::verifySetup (bool throw_exc) const
{
  if( !hasControlAgent() )
  {
    if( throw_exc )
      Throw("control agent not attached");
    return False;
  }
  else
    return True;
}

//##ModelId=3E3FE1BB0220
Thread::ThrID ApplicationBase::runThread (bool del_on_exit)
{
  cdebug(2)<<"running in separate thread\n";
  delete_on_exit = del_on_exit;
  thread_ = Thread::create(startThread,this);
  cdebug(2)<<"launched as thread "<<thread_<<endl;
  return thread_;
}

//##ModelId=3E3FE1DD017A
void * ApplicationBase::startThread (void *arg)
{
  ApplicationBase *object = static_cast<ApplicationBase*>(arg);
  object->do_run();
  return 0;
}

//##ModelId=3E8C1A5D01E9
void ApplicationBase::do_run ()
{
  try
  {
    run();
  }
  catch( std::exception &exc )
  {
    cdebug(0)<<"thread terminated with exception: "<<exc.what()<<endl; 
  }
  catch( ... )
  {
    cdebug(0)<<"thread terminated with unknown exception\n"; 
  }
}

string ApplicationBase::sdebug (int,const string &,const char *name) const
{
  return name ? name : "App";
}
