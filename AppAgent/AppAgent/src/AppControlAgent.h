#ifndef APPAGENT_SRC_APPCONTROLAGENT_H_HEADER_INCLUDED_C530D733
#define APPAGENT_SRC_APPCONTROLAGENT_H_HEADER_INCLUDED_C530D733
    
#include <AppAgent/AppAgent.h>
#include <AppAgent/AID-AppAgent.h>
#include <Common/Thread/Mutex.h>

#pragma aid App Control Event Init Stop Pause Resume Halt
    
namespace AppControlAgentVocabulary
{
  const HIID 
      
      InitEvent        = AidApp|AidControl|AidInit,
      StopEvent        = AidApp|AidControl|AidStop,
      PauseEvent       = AidApp|AidControl|AidPause,
      ResumeEvent      = AidApp|AidControl|AidResume,
      HaltEvent        = AidApp|AidControl|AidHalt,
      
      ControlEventMask =  AidApp|AidControl|AidWildcard;
      
  // this defines the standard states and commands returned by the control 
  // agent
  typedef enum 
  {
    // standard states
    // subclasses may extend this with their own states. The convention is that
    // operational states are >0, and error/stopped states are <0
    
    INIT    =     0,   // initializing (on startup/after Init/Reinit event)
    RUNNING =     1,   // application is running
    STOPPED =     -1,  // stopped 
    HALTED  =     -2,  // halted
        
    // additional return codes from getCommand()
    NEWSTATE =     100,   // got state-changing command
    PAUSED   =     -100,  // got pause command
    RESUMED  =     -101,  // got resume command
        
  } ControlStates;
      
};
    
//##ModelId=3DFF2FC1009C
class AppControlAgent : public AppAgent
{
  public:

    //##ModelId=3E394E4F02D2
    AppControlAgent();

    //##ModelId=3E3957E10329
    virtual int getCommand (HIID &id,DataRecord::Ref &data,int wait = AppAgent::WAIT);
    
    //##ModelId=3E394E080055
    //##Documentation
    virtual int setState (int newstate);
    
    //##ModelId=3E394E960305
    virtual int state() const;
  
    //##ModelId=3E394E9C01D7
    virtual string stateString() const;
    
    //##ModelId=3E3A74D40114
    bool isPaused() const;
    
    
    //##ModelId=3E3AA17103E6
    Thread::Mutex & mutex () const;
    
  protected:
      
    //##ModelId=3E3A9E520156
    int checkStateEvent (const HIID &id);
  
    // hide getEvent from public, we use getCommand
    //##ModelId=3E3A9E5100A3
    AppAgent::getEvent;
  
  private:
      
    //##ModelId=3E394E1E0267
    int state_;
  
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

