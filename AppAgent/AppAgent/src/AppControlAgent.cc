#include "AppControlAgent.h"

using namespace AppControlAgentVocabulary;
    
//##ModelId=3E40F90F02BA
bool AppControlAgent::init (bool waitstart, const DataRecord &data)
{
  bool rethrow = data[FThrowError].as_bool(False);
  cdebug(1)<<"initializing\n";
  try 
  {
    if( !AppEventAgentBase::init(data) )
    {
      Throw("event base init failed");
    }
    // do we need to wait for a start event here?
    if( waitstart )
    {
      cdebug(1)<<"waiting for INIT->RUNNING transition\n";
      HIID id;
      DataRecord::Ref dum;
      while( state() == INIT )
      {
        int res = getCommand(id,dum,AppEventSink::BLOCK);
        FailWhen( res != SUCCESS,"getCommand() failed while waiting for start event");
        cdebug(2)<<"got command "<<id<<", state is now "<<stateString()<<endl;
      }
    }
    return True;
  }
  catch( std::exception &exc )
  {
    cdebug(1)<<"init failed\n";
    if( rethrow )
      throw(exc);
    setErrorState(exc.what());
    return False;
  }
}

//##ModelId=3E3FF3FA00C0
bool AppControlAgent::init (const DataRecord &data)
{
  cdebug(1)<<"initializing\n";
  try 
  {
    bool waitstart = False;
    // get the waitstart parameter from init record
    if( data[initfield()].exists() )
      waitstart = data[initfield()][FWaitStart].as_bool(False);
    
    return init(waitstart,data);
  }
  catch( std::exception &exc )
  {
    cdebug(1)<<"init failed\n";
    setErrorState(exc.what());
    return False;
  }
}

//##ModelId=3E3A9E520156
int AppControlAgent::checkStateEvent (const HIID &id)
{
  if( id == PauseEvent )
  {
    paused_ = True;
    return PAUSED;
  }
  else if( id == ResumeEvent )
  {
    paused_ = False;
    return RESUMED;
  }
  else if( id == InitEvent )
  {
    paused_ = False;
    setState(INIT);
    return NEWSTATE;
  }
  else if( id == StartEvent )
  {
    if( state() == INIT )
    {
      setState(RUNNING);
      return NEWSTATE;
    }
    return state();
  }
  else if( id == StopEvent )
  {
    paused_ = False;
    setState(STOPPED);
    return NEWSTATE;
  }
  else if( id == HaltEvent )
  {
    paused_ = False;
    setState(HALTED);
    return NEWSTATE;
  }
  return -1; // unknown event
}

//##ModelId=3E3957E10329
int AppControlAgent::getCommand (HIID &id,DataRecord::Ref &data, int wait)
{
  // get an application control event, return error code if not successful
  int res = sink().getEvent(id,data,ControlEventMask,wait);
  if( res == SUCCESS )
  {
    cdebug(3)<<"got control event "<<id<<endl;
    // change state according to event
    Thread::Mutex::Lock lock(mutex_);
    res = checkStateEvent(id);
    FailWhen(res<0,"unexpected state event "+id.toString());
    if( res == NEWSTATE )
    {
      cdebug(2)<<"state is now "<<stateString()<<endl;
    }
  }
  return res;
}

//##ModelId=3E4112CC0139
int AppControlAgent::hasCommand() const
{
  return sink().hasEvent(ControlEventMask);
}

//##ModelId=3E4274C60015
void AppControlAgent::postEvent (const HIID &id, const ObjRef &data)
{
  sink().postEvent(id,data);
}

//##ModelId=3E4274C601C8
void AppControlAgent::postEvent (const HIID &id, const DataRecord::Ref &data)
{
  sink().postEvent(id,data);
}

//##ModelId=3E4274C60230
void AppControlAgent::postEvent (const HIID &id, const string &text)
{
  sink().postEvent(id,text);
}


//##ModelId=3E394E080055
int AppControlAgent::setState (int newstate)
{
  Thread::Mutex::Lock lock(mutex_);
  return state_ = newstate;
}

//##ModelId=3E40FAF50397
int AppControlAgent::setErrorState (const string& msg)
{
  Thread::Mutex::Lock lock(mutex_);
  errmsg_ = msg;
  return state_ = ERROR;
}

//##ModelId=3E394E960305
int AppControlAgent::state () const
{
  return state_;
}

//##ModelId=3E394E9C01D7
string AppControlAgent::stateString () const
{
  string out;
  Thread::Mutex::Lock lock(mutex_);
  switch( state() )
  {
    case INIT:     out = "INIT";     break;
    case RUNNING:  out = "RUNNING";  break;
    case STOPPED:  out = "STOPPED";  break;
    case HALTED:   out = "HALTED";   break;
    case ERROR:    out = "ERROR: " + errmsg_; break;
  }
  if( isPaused() )
    out += "(PAUSED)";
  
  return out;
}

//##ModelId=3E40FEA700DF
string AppControlAgent::sdebug (int detail,const string &prefix,const char *name) const
{
  return AppEventAgentBase::sdebug(detail,prefix,name?name:"AppControlAgent");
}

