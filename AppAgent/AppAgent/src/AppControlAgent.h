#ifndef APPAGENT_SRC_APPCONTROLAGENT_H_HEADER_INCLUDED_C530D733
#define APPAGENT_SRC_APPCONTROLAGENT_H_HEADER_INCLUDED_C530D733
    
#include <AppAgent/AppEventAgentBase.h>
#include <AppAgent/AID-AppAgent.h>
#include <Common/Thread/Mutex.h>

#pragma aid App Control Parameters Event Init Start Stop Pause Resume Halt
#pragma aid Always Wait Start Throw Error

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
      
      InitEvent        = AidApp|AidControl|AidInit,
      StartEvent       = AidApp|AidControl|AidStart,
      StopEvent        = AidApp|AidControl|AidStop,
      PauseEvent       = AidApp|AidControl|AidPause,
      ResumeEvent      = AidApp|AidControl|AidResume,
      HaltEvent        = AidApp|AidControl|AidHalt,
      
      ControlEventMask = AidApp|AidControl|AidWildcard;
      
};

    
//##ModelId=3DFF2FC1009C
class AppControlAgent : public AppEventAgentBase
{
  public:
      
    //##ModelId=3E40EDC3036F
    explicit AppControlAgent (const HIID &initf = AppControlAgentVocabulary::FControlParams)
        : AppEventAgentBase(initf) {}

    //##ModelId=3E394E4F02D2
    AppControlAgent(AppEventSink & sink, const HIID & initf = AppControlAgentVocabulary::FControlParams)
        : AppEventAgentBase(sink,initf) {}
    
    //##ModelId=3E3FF3FA00C0
    //##Documentation
    //## Agent initialization method. Called by the application to initialize
    //## or reinitialize an agent. Agent parameters are supplied via a
    //## DataRecord.
    virtual bool init (const DataRecord &data);
    
    //##ModelId=3E40F90F02BA
    virtual bool init (bool waitstart = False, const DataRecord &data = DataRecord() );

    //##ModelId=3E3957E10329
    virtual int getCommand (HIID &id,DataRecord::Ref &data,int wait = AppEvent::WAIT);
    
    //##ModelId=3E4112CC0139
    virtual int hasCommand() const;
    
    //##ModelId=3E4274C60015
    //##Documentation
    //## Posts an event on behalf of the application.
    virtual void postEvent(const HIID &id, const ObjRef &data = ObjRef());
    //##ModelId=3E4274C601C8
    void postEvent(const HIID &id, const DataRecord::Ref &data);
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
    
    //##ModelId=3E3A74D40114
    bool isPaused() const;
    
    //##ModelId=3E3AA17103E6
    Thread::Mutex & mutex () const;
    
    //##ModelId=3E40FEA700DF
    virtual string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;

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
    //##ModelId=3E3A9E510382
    mutable Thread::Mutex mutex_;

};

//##ModelId=3E3A74D40114
inline bool AppControlAgent::isPaused() const
{
  return paused_;
}

//##ModelId=3E3AA17103E6
inline Thread::Mutex & AppControlAgent::mutex () const
{
  return mutex_;
}

#endif /* APPAGENT_SRC_APPCONTROLAGENT_H_HEADER_INCLUDED_C530D733 */

