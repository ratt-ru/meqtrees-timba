#ifndef APPMANAGERWP_H_HEADER_INCLUDED_B38CC241
#define APPMANAGERWP_H_HEADER_INCLUDED_B38CC241

#include <OCTOPUSSY/WorkProcess.h>
#include <OCTOPUSSY/AppRegistry.h>
    
#include <map>
    
#pragma aid AppManager AppManagerWP Start Stop Launch Halt Launched Halted App Fail 
#pragma aid ID Address Parameters
    
namespace AppManagerVocabulary
{
  const HIID  // AppManager publishes these to report its status
              MsgStarted     = AidAppManager|AidStart,
              MsgStopped     = AidAppManager|AidStop,
      
              // these are commands sent to the AppManager
              MsgLaunch      = AidAppManager|AidLaunch,             // launch app
              MsgHalt        = AidAppManager|AidHalt|AidAny|AidAny, // halt app
      
              // 
              MsgLaunched     = AidAppManager|AidApp|AidLaunched,
              MsgHalted       = AidAppManager|AidApp|AidHalted,
              MsgLaunchFailed = AidAppManager|AidApp|AidFail|AidLaunch,
              MsgHaltFailed   = AidAppManager|AidApp|AidFail|AidHalt;
  
};
    
//##ModelId=3E316F2A00BA
class AppManagerWP : public WorkProcess, public AppRegistry
{
  public:
    //##ModelId=3E316F2A01FD
    AppManagerWP ();
    
  protected:
    //##ModelId=3E316F2A01FE
    virtual void init ();

    //##ModelId=3E316F2A0200
    virtual bool start ();
    
    //##ModelId=3E316F2A0202
    virtual void stop ();
    
    //##ModelId=3E316F2A0204
    virtual int receive (MessageRef &mref);

  private:
    //##ModelId=3E316F2A020D
    AppManagerWP(const AppManagerWP& right);

    //##ModelId=3E316F2A0216
    AppManagerWP& operator=(const AppManagerWP& right);
    
    
    // map of local apps
    //##ModelId=3E316F2A00C0
    typedef struct 
    { 
      WPRef       wpref; 
      bool        started;
      MsgAddress  creator; 
    } AppMapEntry;
    //##ModelId=3E316F2A00C7
    typedef std::map<WPID,AppMapEntry> AppMap;
    //##ModelId=3E316F2A00CD
    typedef AppMap::iterator AMI;
    //##ModelId=3E316F2A00D4
    typedef AppMap::const_iterator CAMI;

    //##ModelId=3E316F2A01F1
    AppMap appmap;
};



#endif /* APPMANAGERWP_H_HEADER_INCLUDED_B38CC241 */
