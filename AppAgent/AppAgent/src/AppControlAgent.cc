#include "AppControlAgent.h"

using namespace AppControlAgentVocabulary;
using namespace AppState;
using namespace AppEvent;
    
static int dum = aidRegistry_AppAgent();

InitDebugContext(AppControlAgent,"AppControl");

using namespace std;

//##ModelId=3E40EDC3036F
AppControlAgent::AppControlAgent (const HIID &initf)
    : AppEventAgentBase(initf),state_(AppState::STOPPED)
{
  status_ref_ <<= pstatus_ = new DataRecord;
}

//##ModelId=3E394E4F02D2
AppControlAgent::AppControlAgent (AppEventSink & sink, const HIID & initf)
    : AppEventAgentBase(sink,initf),state_(AppState::STOPPED)
{
  status_ref_ <<= pstatus_ = new DataRecord;
}

//##ModelId=3E50FA3702B9
AppControlAgent::AppControlAgent (AppEventSink *sink, int dmiflags, const HIID &initf)
    : AppEventAgentBase(sink,dmiflags,initf),state_(AppState::STOPPED)
{
  status_ref_ <<= pstatus_ = new DataRecord;
}

bool AppControlAgent::preinit (DataRecord::Ref::Xfer &initrec)
{
  // set the INIT state
  cdebug(1)<<"pre-initializing control agent\n";
  // cache the init record
  initrec_ref_ <<= initrec;  
  initrec_used_ = False;
  // try an init
  bool res = init(*initrec_ref_);
  FailWhen( !res,"control agent init failed" ); 
  return res;
}
  
bool AppControlAgent::init (const DataRecord &data)
{  
  rethrow_ = data[FThrowError].as<bool>(False);
  cdebug(1)<<"initializing control agent\n";
  try 
  {
    // no init sub-record? Do nothing then
    if( !data[initfield()].exists() )
      return True;
    const DataRecord &rec = data[initfield()];
    initrec_used_ = True;
    // if init record specifies delayed initialization, then we don't
    // transit to INIT state here. This will cause start() below to wait
    // for another init event
    if( !rec[FDelayInit].as<bool>(False) )
      setState(INIT); 
    // init event base (and event sink)
    if( !AppEventAgentBase::init(data) )
      Throw("event base init failed");
    // setup the auto_exit parameter
    auto_exit_ = rec[FAutoExit].as<bool>(False);
    // setup the waitstart_ parameter
    waitstart_ = rec[FWaitStart].as<bool>(False);
    postEvent(InitNotifyEvent);
    return True;
  }
  catch( std::exception &exc )
  {
    cdebug(1)<<"init() failed\n";
    if( rethrow_ )
      throw(exc);
    setErrorState(exc.what());
    return False;
  }
}

int AppControlAgent::start (DataRecord::Ref &initrec)
{
  try
  {
    paused_ = False;
    // if called while not in an INIT state, wait for transition
    while( state() != INIT )
    {
      // break out if HALTED
      if( state() == HALTED )
        return HALTED;
      HIID id;
      DataRecord::Ref dum;
      int res = getCommand(id,dum,AppEvent::BLOCK);
      FailWhen( res != SUCCESS,"getCommand() failed while waiting for INIT event");
      cdebug(2)<<"got command "<<id<<", state is now "<<stateString()<<endl;
    }
    // once in INIT state, we must have a cached init record, else we're borked
    FailWhen( !initrec_ref_.valid(),"INIT state reached but no init record cached" ); 
    initrec.xfer(initrec_ref_);
    // if we haven't used the init record yet, use it now to reinit ourselves
    if( !initrec_used_ )
    {
      bool res = init(*initrec_ref_);
      FailWhen(!res,"control agent init failed" ); 
    }
    // do we need to wait for an explicit transition to RUNNING state?
    if( waitstart_ )
    {
      cdebug(1)<<"waiting for transition out of INIT state\n";
      HIID id;
      DataRecord::Ref dum;
      while( state() == INIT )
      {
        int res = getCommand(id,dum,AppEvent::BLOCK);
        FailWhen( res != SUCCESS,"getCommand() failed while waiting for start event");
        cdebug(2)<<"got command "<<id<<", state is now "<<stateString()<<endl;
      }
    }
    else // else go into RUNNING directly
      setState(RUNNING);
  }
  catch( std::exception &exc )
  {
    cdebug(1)<<"start() failed\n";
    if( rethrow_ )
      throw(exc);
    setErrorState(exc.what());
  }
  
  return state();
}


//##ModelId=3E510A600340
void AppControlAgent::close ()
{
  postEvent(StopNotifyEvent);
  AppEventAgentBase::close();
}

//##ModelId=3E3A9E520156
int AppControlAgent::checkStateEvent (const HIID &id,const DataRecord::Ref::Copy &data)
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
    initrec_ref_.copy(data,DMI::PRESERVE_RW);
    initrec_used_ = False;
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
  return SUCCESS; // unknown event
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
    Thread::Mutex::Lock lock(state_condition_);
    if( checkStateEvent(id,data) == NEWSTATE )
    {
      cdebug(2)<<"state is now "<<stateString()<<endl;
      return NEWSTATE;
    }
    // else simply returns success
  }
  return res;
}

//##ModelId=3E4112CC0139
int AppControlAgent::hasCommand() const
{
  return sink().hasEvent(ControlEventMask);
}

//##ModelId=3E4274C60015
void AppControlAgent::postEvent (const HIID &id, const ObjRef::Xfer &data)
{
  sink().postEvent(id,data);
}

//##ModelId=3E4274C601C8
void AppControlAgent::postEvent (const HIID &id, const DataRecord::Ref::Xfer &data)
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
  Thread::Mutex::Lock lock(state_condition_);
  if( newstate != state_ )
  {
    if( auto_exit_ && newstate < 0 && newstate != HALTED )
    {
      cdebug(1)<<"auto-exit enabled, halting on state "<<newstate<<endl;
      newstate = HALTED;
    }
    state_ = newstate;
    state_condition_.broadcast();
  }
  return state_;
}

//##ModelId=3E5368C003DC
void AppControlAgent::waitUntilEntersState (int waitstate) const
{ 
  waitUntil(std::bind2nd(std::equal_to<int>(),waitstate)); 
}

//##ModelId=3E53696202BE
bool AppControlAgent::waitUntilEntersState (int waitstate, double seconds) const
{ 
  return waitUntil(std::bind2nd(std::equal_to<int>(),waitstate),seconds); 
}

//##ModelId=3E536C9E028F
void AppControlAgent::waitUntilLeavesState (int waitstate) const
{ 
  waitUntil(std::bind2nd(std::not_equal_to<int>(),waitstate)); 
}

//##ModelId=3E536C9F009F
bool AppControlAgent::waitUntilLeavesState (int waitstate, double seconds) const
{ 
  return waitUntil(std::bind2nd(std::not_equal_to<int>(),waitstate),seconds); 
}

//##ModelId=3E40FAF50397
int AppControlAgent::setErrorState (const string& msg)
{
  Thread::Mutex::Lock lock(state_condition_);
  errmsg_ = msg;
  return state_ = AppState::ERROR;
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
  Thread::Mutex::Lock lock(state_condition_);
  switch( state() )
  {
    case INIT:            out = "INIT";     break;
    case RUNNING:         out = "RUNNING";  break;
    case STOPPED:         out = "STOPPED";  break;
    case HALTED:          out = "HALTED";   break;
    case AppState::ERROR: out = "ERROR: " + errmsg_; break;
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


