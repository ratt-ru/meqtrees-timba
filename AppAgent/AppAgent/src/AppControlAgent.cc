#include "AppControlAgent.h"
#include "AppEventSink.h"
    
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
  
//##ModelId=3E40F90F02BA
bool AppControlAgent::init (const DataRecord &data)
{  
  rethrow_ = data[FThrowError].as<bool>(False);
  cdebug(1)<<"initializing control agent\n";
  cdebug(3)<<"init record: "<<data.sdebug(DebugLevel-1,"  ")<<endl;
  try 
  {
    // no init sub-record? Do nothing then
    if( !data[initfield()].exists() )
      return True;
    const DataRecord &rec = data[initfield()].as<DataRecord>();
    cdebug(3)<<"subrecord: "<<rec.sdebug(DebugLevel-1,"  ")<<endl;
    initrec_used_ = True;
    // solicit application control commands
    solicitCommand(ControlPrefix|AidWildcard);
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

//##ModelId=3E8C1A5C030E
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
      FailWhen(res<0,"getCommand() failed while waiting for INIT transition");
      cdebug(2)<<"got command "<<id<<", state is now "<<stateString()<<endl;
    }
    // once in INIT state, we must have a cached init record, else we're borked
    FailWhen( !initrec_ref_.valid(),"INIT state reached but no init record cached" ); 
    initrec.xfer(initrec_ref_);
    // if we haven't used the init record yet, use it now to reinit ourselves
    if( !initrec_used_ )
    {
      bool res = init(*initrec);
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

//##ModelId=3E8C3DDB02CA
void AppControlAgent::solicitCommand (const HIID &mask)
{
  sink().solicitEvent(mask);
}

//##ModelId=3E510A600340
void AppControlAgent::close ()
{
  postEvent(StopNotifyEvent);
  AppEventAgentBase::close();
}

//##ModelId=3EB2425300E4
int AppControlAgent::pause ()
{
  if( paused_ )
    return SUCCESS;
  paused_ = True;
  postState();
  return PAUSED;
}

//##ModelId=3EB24253013A
int AppControlAgent::resume ()
{
  if( !paused_ )
    return SUCCESS;
  paused_ = False;
  postState();
  return RESUMED;
}

//##ModelId=3E3A9E520156
int AppControlAgent::checkStateEvent (const HIID &id,const DataRecord::Ref::Copy &data)
{
  if( id == InitEvent )
  {
    initrec_ref_.copy(data,DMI::PRESERVE_RW);
    initrec_used_ = False;
    setState(INIT,True);
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
    setState(STOPPED,True);
    return NEWSTATE;
  }
  else if( id == HaltEvent )
  {
    setState(HALTED,True);
    return NEWSTATE;
  }
  return AppEvent::ERROR; // unknown event
}

//##ModelId=3EB24253018C
int AppControlAgent::processCommand (const HIID &id,const DataRecord::Ref &data,const HIID &source)
{
  cdebug(3)<<"got control event "<<id<<" from ["<<source<<"]\n";
  // is it a status request?
  if( id == PauseEvent )
    return pause();
  else if( id == ResumeEvent )
    return resume();
  else if( id == StatusRequest )
  {
    if( data.valid() ) // post specific sub-field of the status record
      postStatus((*data)[FField].as<HIID>(HIID()),
                 (*data)[FRequestId].as<HIID>(HIID()),
                 source);
    else               // post full status record
      postStatus(HIID(),HIID(),source);
  }
  // is it a state request?
  else if( id == StateRequest )
  {
    if( data.valid() ) // post specific sub-field of the status record
      postState((*data)[FRequestId].as<HIID>(HIID()),source);
    else
      postState(HIID(),source);
  }
  else if( !id.matches(AppCommandMask) )
  {
    // try to change state according to event
    Thread::Mutex::Lock lock(state_condition_);
    int res = checkStateEvent(id,data);
    if( res == NEWSTATE )
      return NEWSTATE;
    else if( res == AppEvent::ERROR )
      postCommandError("ignoring unrecognized command "+id.toString(),
                        id,data.copy(),source);
    lock.release();
  }
  return SUCCESS;
}

//##ModelId=3EB2425303B2
void AppControlAgent::postCommandError (const string &msg,const HIID &id,
    const DataRecord::Ref::Xfer &data,const HIID &source)
{
  DataRecord::Ref ref(new DataRecord,DMI::ANONWR);
  ref()[AidText] = "Error processing command " +
                    id.toString() + ": " + msg;
  ref()[AidError] = msg;
  ref()[AidCommand] = id;
  if( data.valid() )
    ref()[AidData] <<= data;
  postEvent(CommandErrorNotifyEvent,ref,source);
}


//##ModelId=3E3957E10329
int AppControlAgent::getCommand (HIID &id,DataRecord::Ref &data, int wait)
{
  // get an application control event, return error code if not successful
  int res;
  do
  {
    HIID source;
    if( isPaused() ) // if paused, force a blocking wait
      wait = AppEvent::BLOCK;
    res = sink().getEvent(id,data,ControlEventMask,wait,source);
    if( isPaused() )
    {
      cdebug(2)<<"paused, and getEvent returns "<<res<<endl;
    }
    if( res != SUCCESS ) // break out on error
    {
      if( res == CLOSED )
      {
        cdebug(1)<<"event sink closed, setting state to HALTED\n";
        setState(HALTED,True);
        return NEWSTATE;
      }
      return res;
    }
    // app-specific command to be returned directly to application?
    if( id.matches(AppCommandMask) )
      res = AppEvent::SUCCESS;
    else // attempt to process the command in the control agent
    {
      try
      {
        res = processCommand(id,data,source);
      }
      catch( std::exception &exc )
      {
        postCommandError(exc.what(),id,data,source);
      }
      catch( ... )
      {
        postCommandError("unknown exception",id,data,source);
      }
    }
  }
  // if the agent gets paused, this will cause it to loop until
  // a resume, or until a terminal state is arrived at
  while( isPaused() );
  return res;
}

//##ModelId=3E4112CC0139
int AppControlAgent::hasCommand() const
{
  return sink().hasEvent(ControlEventMask);
}

//##ModelId=3E8C209A01E7
bool AppControlAgent::isEventBound (const HIID &id)
{
  return sink().isEventBound(id);
}


//##ModelId=3E4274C60015
void AppControlAgent::postEvent (const HIID &id,const ObjRef::Xfer &data,
                                 const HIID &destination)
{
  sink().postEvent(id,data,destination);
}

//##ModelId=3E4274C601C8
void AppControlAgent::postEvent (const HIID &id, const DataRecord::Ref::Xfer &data,
                                 const HIID &destination)
{
  sink().postEvent(id,data,destination);
}

//##ModelId=3E4274C60230
void AppControlAgent::postEvent (const HIID &id, const string &text,
                                 const HIID &destination)
{
  sink().postEvent(id,text,destination);
}

//##ModelId=3E394E080055
int AppControlAgent::setState (int newstate,bool unpause)
{
  Thread::Mutex::Lock lock(state_condition_);
  if( newstate != state_ || ( unpause && paused_ ) )
  {
    if( auto_exit_ && newstate < 0 && newstate != HALTED )
    {
      cdebug(1)<<"auto-exit enabled, halting on state "<<newstate<<endl;
      newstate = HALTED;
    }
    state_ = newstate;
    if( unpause )
      paused_ = False;
    state_condition_.broadcast();
    postState();
  }
  return state_;
}

//##ModelId=3E9BD63E00DD
void AppControlAgent::postState (const HIID &rqid,const HIID &destination)
{
  Thread::Mutex::Lock lock(state_condition_);
  cdebug(2)<<"state is now "<<stateString()<<endl;
  cdebug(3)<<"posting state to ["<<destination<<"] with RQID="<<rqid<<endl;
  DataRecord::Ref ref;
  DataRecord &rec = ref <<= new DataRecord;
  rec[FState] = state();
  rec[FPaused] = isPaused();
  rec[FStateString] = stateString();
  rec[FRequestId] = rqid;
  postEvent(StateNotifyEvent|rqid,ref,destination);
}

//##ModelId=3EB24254039F
void AppControlAgent::postStatus (const HIID &field,const HIID &rqid,const HIID &destination)
{
  cdebug(3)<<"posting status field ["<<field<<"] to ["<<destination
            <<"] with RQID="<<rqid<<endl;
  DataRecord::Ref ref;
  DataRecord &rec = ref <<= new DataRecord;
  if( field.empty() )
  {
    rec[FField] = HIID();
    rec[FValue] <<= status_ref_.copy(DMI::READONLY);
  }
  else
  {
    rec[FField] = field;
    try 
    {
      rec[FValue] <<= (*pstatus_)[field].ref();
    }
    catch( std::exception &exc )
    {
      rec[FValue] = "error accessing field \"" + field.toString() + 
                    string("\":") + exc.what(); 
    }
  }
  rec[FRequestId] = rqid;
  postEvent(StatusNotifyEvent|rqid,ref,destination);
}

//##ModelId=3EB2425501DA
void AppControlAgent::postStatusUpdate (
    const HIID &subrec,const HIID &field,DataRecord::Ref::Xfer &rec)
{
  cdebug(3)<<"posting update for status field ["<<subrec<<"/"<<field<<"]\n";
  HIID evname = StatusUpdateEvent;
  if( !subrec.empty() )
    evname |= subrec|AidSlash;
  postEvent(evname|field,rec);
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
  // standard states are <= RUNNING
  if( state() <= RUNNING )
  {
    switch( state() )
    {
      case INIT:            out = "INIT";     break;
      case RUNNING:         out = "RUNNING";  break;
      case STOPPED:         out = "STOPPED";  break;
      case HALTED:          out = "HALTED";   break;
      case AppState::ERROR: out = "ERROR: " + errmsg_; break;
    }
  }
  // non-standard states (>0): interpret as AtomicIDs (note that AIDs are 
  // negative, hence the unary minus)
  else
    out = struppercase(AtomicID(-state()).toString());
  // paused?
  if( isPaused() )
    out += "[PAUSED]";
  return out;
}

//##ModelId=3E40FEA700DF
string AppControlAgent::sdebug (int detail,const string &prefix,const char *name) const
{
  return AppEventAgentBase::sdebug(detail,prefix,name?name:"AppControlAgent");
}


