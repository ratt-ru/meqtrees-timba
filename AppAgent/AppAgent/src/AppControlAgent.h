#ifndef APPAGENT_SRC_APPCONTROLAGENT_H_HEADER_INCLUDED_C530D733
#define APPAGENT_SRC_APPCONTROLAGENT_H_HEADER_INCLUDED_C530D733
    
#include <AppAgent/AppEventAgentBase.h>
#include <AppAgent/AID-AppAgent.h>
#include <Common/Thread/Condition.h>
    
#include <functional>
    
class AppEventAgentBase;
class AppEventSink;
class DataRecord;

#pragma aid App Control Parameters Event Init Start Stop Pause Resume Halt
#pragma aid Always Wait Start Throw Error Notify Auto Exit

namespace AppEvent 
{
  //##ModelId=3E40FDEA0225
  typedef enum
  {
    // additional return codes for AppControlAgent::getCommand()
    NEWSTATE =     100,   // got state-changing command
    PAUSED   =     -100,  // got pause command
    RESUMED  =     -101,  // got resume command

  } AppControl_EventCodes;
};
    
namespace AppState
{
  //##ModelId=3E40FDEA018D
  typedef enum 
  {
    // standard states
    // subclasses may extend this with their own states. The convention is that
    // operational states are >0, and error/stopped states are <0
    INIT    =     0,   // initializing (on startup/after Init/Reinit event)
    RUNNING =     1,   // application is running
    STOPPED =     -1,  // stopped 
    HALTED  =     -2,  // halted
    ERROR   =     AppEvent::ERROR
        
  } States;
};

namespace AppControlAgentVocabulary
{
  using namespace AppEventSinkVocabulary;
  
  const HIID 
      FControlParams   = AidControl|AidParameters,
      
      FWaitStart       = AidWait|AidStart,
      FAutoExit        = AidAuto|AidExit,
      
      // standard prefix for app control events
      ControlPrefix    = AidApp|AidControl,
      
      InitEvent        = ControlPrefix|AidInit,
      StartEvent       = ControlPrefix|AidStart,
      StopEvent        = ControlPrefix|AidStop,
      PauseEvent       = ControlPrefix|AidPause,
      ResumeEvent      = ControlPrefix|AidResume,
      HaltEvent        = ControlPrefix|AidHalt,
      
      InitNotifyEvent  = AidApp|AidNotify|AidInit,
      StopNotifyEvent  = AidApp|AidNotify|AidStop,
      
      ControlEventMask = ControlPrefix|AidWildcard;
};

    
//##ModelId=3DFF2FC1009C
class AppControlAgent : public AppEventAgentBase
{
  public:
    //##ModelId=3E40EDC3036F
    explicit AppControlAgent (const HIID &initf = AidControl);
    //##ModelId=3E394E4F02D2
    AppControlAgent(AppEventSink & sink, const HIID & initf = AidControl);
    //##ModelId=3E50FA3702B9
    AppControlAgent(AppEventSink *sink, int dmiflags, const HIID &initf = AidControl);
    
    //##ModelId=3E3FF3FA00C0
    //##Documentation
    //## Agent initialization method. Called by the application to initialize
    //## or reinitialize an agent. Agent parameters are supplied via a
    //## DataRecord.
    virtual bool init (const DataRecord &data);
    
    //##ModelId=3E40F90F02BA
    virtual bool init (bool waitstart = False, const DataRecord &data = DataRecord() );
    
    //##ModelId=3E510A600340
    //##Documentation
    //## Applications call close() when they're done speaking to an agent.
    virtual void close ();

    //##ModelId=3E3957E10329
    virtual int getCommand (HIID &id,DataRecord::Ref &data,int wait = AppEvent::WAIT);
    
    //##ModelId=3E4112CC0139
    virtual int hasCommand() const;
    
    //##ModelId=3E4274C60015
    //##Documentation
    //## Posts an event on behalf of the application.
    virtual void postEvent(const HIID &id, const ObjRef::Xfer &data = ObjRef());
    //##ModelId=3E4274C601C8
    void postEvent(const HIID &id, const DataRecord::Ref::Xfer &data);
    //##ModelId=3E4274C60230
    void postEvent(const HIID &id, const string &text);

    //##ModelId=3E394E080055
    //##Documentation
    virtual int setState (int newstate);
    
    //##ModelId=3E40FAF50397
    virtual int setErrorState (const string& msg);
    
    //##ModelId=3E394E960305
    virtual int state() const;
    //##ModelId=3E394E9C01D7
    virtual string stateString() const;
    
    //##ModelId=3E5650EE0209
    const DataRecord &status() const;
    //##ModelId=3E5650FE024A
    DataRecord &status();
    
    //##Documentation
    //## Blocks the calling thread until the control agent enters a state
    //## for which predicate(state) == True
    template<class Pred>
    void waitUntil (Pred predicate) const;
    
    //##Documentation
    //## Same as waitUntil() above, but has a timeout in secobds.
    //## Returns True if wait was successful, or False on timeout.    
    template<class Pred>
    bool waitUntil (Pred predicate,double seconds) const;
    
    //##ModelId=3E5368C003DC
    //##Documentation
    //## Alias for waiting until state == waitstate
    void waitUntilEntersState (int waitstate) const;
    //##ModelId=3E53696202BE
    //##Documentation
    //## Alias for waiting until state == waitstate
    bool waitUntilEntersState (int waitstate, double seconds) const;
    
    //##ModelId=3E536C9E028F
    //##Documentation
    //## Alias for waiting until state != waitstate
    void waitUntilLeavesState (int waitstate) const;
    //##ModelId=3E536C9F009F
    //##Documentation
    //## Alias for waiting until state != waitstate
    bool waitUntilLeavesState (int waitstate, double seconds) const;
  
    
    //##ModelId=3E3A74D40114
    bool isPaused() const;
    
    //##ModelId=3E3AA17103E6
    Thread::Mutex & mutex () const;
    //##ModelId=3E53687B0065
    Thread::Condition & stateCondition() const;
    
    //##ModelId=3E40FEA700DF
    virtual string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;
    

    //##ModelId=3E5505A90042
    LocalDebugContext;
    
  protected:
    //##ModelId=3E3A9E520156
    int checkStateEvent (const HIID &id);
  
  private:
    //##ModelId=3E394E1E0267
    int state_;
    //##ModelId=3E40FB0B0172
    string errmsg_;
    //##ModelId=3E3A74B70078
    bool paused_;
    //##ModelId=3E5505A9039F
    bool auto_exit_;
    //##ModelId=3E5650D900AE
    DataRecord::Ref status_;
    
    //##ModelId=3E3A9E510382
    mutable Thread::Condition state_condition_;
    //##ModelId=3E4CD0B00081
    std::vector<int> input_flags_;
    //##ModelId=3E4CD1450162
    std::vector<int> input_term_states_;

    //##ModelId=3E4CCF420044
    std::vector<AppEventAgentBase::Ref> inputs;
};

//##ModelId=3E40EDC3036F
inline AppControlAgent::AppControlAgent (const HIID &initf)
    : AppEventAgentBase(initf),state_(AppState::INIT)
{}

//##ModelId=3E394E4F02D2
inline AppControlAgent::AppControlAgent (AppEventSink & sink, const HIID & initf)
    : AppEventAgentBase(sink,initf),state_(AppState::INIT)
{}

//##ModelId=3E50FA3702B9
inline AppControlAgent::AppControlAgent (AppEventSink *sink, int dmiflags, const HIID &initf)
    : AppEventAgentBase(sink,dmiflags,initf),state_(AppState::INIT)
{}

//##ModelId=3E5650EE0209
inline const DataRecord & AppControlAgent::status () const
{
  return status_.deref();
}

//##ModelId=3E5650FE024A
inline DataRecord & AppControlAgent::status ()
{
  return status_.dewr();
}
    
//##ModelId=3E3A74D40114
inline bool AppControlAgent::isPaused() const
{
  return paused_;
}

//##ModelId=3E3AA17103E6
inline Thread::Mutex & AppControlAgent::mutex () const
{
  return state_condition_;
}

//##ModelId=3E53687B0065
inline Thread::Condition & AppControlAgent::stateCondition() const
{
  return state_condition_;
}

template<class Pred>
void AppControlAgent::waitUntil (Pred predicate) const
{
  Thread::Mutex::Lock lock(state_condition_);
  while( !predicate(state_) )
    state_condition_.wait();
}

template<class Pred>
bool AppControlAgent::waitUntil (Pred predicate,double seconds) const
{
  Timestamp endtime = Timestamp::now() + Timestamp(seconds);
  Thread::Mutex::Lock lock(state_condition_);
  while( !predicate(state_) && Timestamp::now() < endtime )
    state_condition_.wait((endtime-Timestamp::now()).seconds());
  return predicate(state_);
}



#endif /* APPAGENT_SRC_APPCONTROLAGENT_H_HEADER_INCLUDED_C530D733 */

