
#ifndef APPAGENT_SRC_APPAGENTBASE_H_HEADER_INCLUDED_E593B6F4
#define APPAGENT_SRC_APPAGENTBASE_H_HEADER_INCLUDED_E593B6F4
    
#include <Common/Debug.h>
#include <DMI/CountedRef.h>
#include <DMI/DataRecord.h>
#include <AppAgent/AID-AppAgent.h>

#pragma aidgroup AppAgent
#pragma aid Throw Error
    
const HIID FThrowError = AidThrow|AidError;

namespace AppState
{
  //##ModelId=3E8C1A5B00B9
  typedef enum 
  {
    // standard states
    // subclasses may extend this with their own states. The convention is that
    // operational states are >0, and error/stopped states are <0
    INIT    =     0,   // initializing (on startup/after Init/Reinit event)
    RUNNING =     1,   // application is running
    STOPPED =     -1,  // stopped 
    HALTED  =     -2,  // halted
    ERROR   =     -999
        
  } States;
};

    
//##ModelId=3E40EACD0054
class AppAgent : public SingularRefTarget
{
  public:
    //##ModelId=3E40EE6100F8
    AppAgent(const HIID &initf);

    //##ModelId=3E40EB1D0317
    //##Documentation
    //## Agent initialization method. Called by the application to initialize
    //## or reinitialize an agent. Agent parameters are supplied via a
    //## DataRecord.
    virtual bool init (const DataRecord &data) = 0;

    //##ModelId=3E40EB22007D
    //##Documentation
    //## Applications call close() when they're done speaking to an agent.
    virtual void close ()
    {
    }

    //##ModelId=3E40EB31031C
    //##Documentation
    //## Returns agent state
    virtual int state () const
    {
      return 0;
    }

    //##ModelId=3E40EB350091
    //##Documentation
    //## Returns agent state as a string
    virtual string stateString () const
    {
      return "OK";
    }

    //##ModelId=3E40EE490013
    const HIID &initfield () const;
    
    //##ModelId=3E40F026018A
    DefineRefTypes(AppAgent,Ref);

  private:
    //##ModelId=3E40EE2C0286
    HIID initfield_;

};

//##ModelId=3E40EE6100F8
inline AppAgent::AppAgent (const HIID &initf)
    : initfield_(initf)
{
}

//##ModelId=3E40EE490013
inline const HIID & AppAgent::initfield () const
{
  return initfield_;
}


#endif /* APPAGENT_SRC_APPAGENTBASE_H_HEADER_INCLUDED_E593B6F4 */
