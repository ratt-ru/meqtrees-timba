#include "AppControlAgent.h"

using namespace AppControlAgentVocabulary;
    
//##ModelId=3E394E4F02D2
AppControlAgent::AppControlAgent()
    : paused_(False)
{
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
  return 0; // no state changes
}

//##ModelId=3E3957E10329
int AppControlAgent::getCommand (HIID &id,DataRecord::Ref &data, int wait)
{
  // get an application control event, return error code if not successful
  int res = getEvent(id,data,ControlEventMask,wait);
  if( res == SUCCESS )
  {
    // change state according to event
    Thread::Mutex::Lock lock(mutex_);
    res = checkStateEvent(id);
    FailWhen(!res,"unexpected state event "+id.toString());
  }
  return res;
}

//##ModelId=3E394E080055
int AppControlAgent::setState (int newstate)
{
  Thread::Mutex::Lock lock(mutex_);
  return state_ = newstate;
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
  }
  if( isPaused() )
    out += "(PAUSED)";
  
  return out;
}
