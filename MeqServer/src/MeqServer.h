#ifndef MEQSERVER_SRC_MEQSERVER_H_HEADER_INCLUDED_D338579D
#define MEQSERVER_SRC_MEQSERVER_H_HEADER_INCLUDED_D338579D

#include <DMI/Events.h>
#include <MEQ/Forest.h>
#include <AppAgent/EventChannel.h>
#include <MeqServer/AID-MeqServer.h>

#pragma aidgroup MeqServer    
#pragma aid MeqClient
#pragma aid Node Name NodeIndex MeqServer Meq 
#pragma aid Create Delete Get Set State Request Resolve Child Children List Batch
#pragma aid App Command Args Result Data Processing Error Message Code
#pragma aid Execute Clear Cache Save Load Forest Recursive Forest Header Version 
#pragma aid Publish Results Enable Disable Event Id Silent Idle Stream 
#pragma aid Debug Breakpoint Single Shot Step Continue Until Stop Level
#pragma aid Get Forest Status Stack Running Changed All Disabled Publishing
#pragma aid Python Init TDL Script File Source Serial String
#pragma aid Idle Executing Debug
    
namespace Meq
{
  const HIID  
    FArgs             = AidArgs,
    FSilent           = AidSilent,
      
    FRecursive        = AidRecursive, 
    FFileName         = AidFile|AidName,
      
    FEnable           = AidEnable,
    FEventId          = AidEvent|AidId,
    FEventData        = AidEvent|AidData,
      
    EvNodeResult      = AidNode|AidResult,
    
    EvNodeStatus      = AidNode|AidStatus,
    
    EvDebugStop       = AidDebug|AidStop;
  
  

//##ModelId=3F5F195E013B
//##Documentation
class MeqServer : public DMI::EventRecepient
{
  public:
    //##ModelId=3F5F195E0140
    MeqServer ();
  
    // attaches a control channel to this MeqServer
    void attachControl (const AppAgent::EventChannel::Ref &channel)
    { control_channel_ = channel; }
    
    virtual ~MeqServer ();

    //##ModelId=3F608106021C
    // runs command processing loop until Halt command is received or control 
    // channel is closed
    virtual void run ();

    // halts the meqserver
    void halt (DMI::Record::Ref &out,DMI::Record::Ref &in);
    
    // sets state
    void setForestState (DMI::Record::Ref &out,DMI::Record::Ref &in);
    // gets status + state record
    void getForestState (DMI::Record::Ref &out,DMI::Record::Ref &in);
    // gets status only
    void getForestStatus (DMI::Record::Ref &out,DMI::Record::Ref &in);
    
    //##ModelId=3F61920F01A8
    void createNode   (DMI::Record::Ref &out,DMI::Record::Ref &in);
    void createNodeBatch (DMI::Record::Ref &out,DMI::Record::Ref &in);
    //##ModelId=3F61920F01FA
    void deleteNode   (DMI::Record::Ref &out,DMI::Record::Ref &in);
    //##ModelId=3F61920F024E
    void nodeGetState (DMI::Record::Ref &out,DMI::Record::Ref &in);
    //##ModelId=3F61920F02A4
    void nodeSetState (DMI::Record::Ref &out,DMI::Record::Ref &in);
    //##ModelId=3F98D91A03B9
    void resolve      (DMI::Record::Ref &out,DMI::Record::Ref &in);
    void resolveBatch (DMI::Record::Ref &out,DMI::Record::Ref &in);
    //##ModelId=3F98D91B0064
    void getNodeList  (DMI::Record::Ref &out,DMI::Record::Ref &in);
    
    void getNodeIndex (DMI::Record::Ref &out,DMI::Record::Ref &in);
    
    //##ModelId=400E5B6C015E
    void nodeExecute  (DMI::Record::Ref &out,DMI::Record::Ref &in);
    //##ModelId=400E5B6C01DD
    void nodeClearCache (DMI::Record::Ref &out,DMI::Record::Ref &in);
    //##ModelId=400E5B6C0247
    void saveForest (DMI::Record::Ref &out,DMI::Record::Ref &in);
    //##ModelId=400E5B6C02B3
    void loadForest (DMI::Record::Ref &out,DMI::Record::Ref &in);
    //##ModelId=400E5B6C0324
    void clearForest (DMI::Record::Ref &out,DMI::Record::Ref &in);
    
    void publishResults (DMI::Record::Ref &out,DMI::Record::Ref &in);
    void disablePublishResults (DMI::Record::Ref &out,DMI::Record::Ref &in);
    
    void nodeSetBreakpoint (DMI::Record::Ref &out,DMI::Record::Ref &in);
    void nodeClearBreakpoint (DMI::Record::Ref &out,DMI::Record::Ref &in);
    
    void debugSetLevel      (DMI::Record::Ref &out,DMI::Record::Ref &in);
    void debugSingleStep    (DMI::Record::Ref &out,DMI::Record::Ref &in);
    void debugNextNode      (DMI::Record::Ref &out,DMI::Record::Ref &in);
    void debugContinue      (DMI::Record::Ref &out,DMI::Record::Ref &in);
    void debugUntilNode     (DMI::Record::Ref &out,DMI::Record::Ref &in);

    
    // executes one of the above commands, as specified by cmd
    DMI::Record::Ref executeCommand (const HIID &cmd,const ObjRef &argref);
    
    // returns control channel
    AppAgent::EventChannel & control ()
    { return control_channel_(); }
    
    // callback for receiving an event
    virtual int receiveEvent (const EventIdentifier &evid,const ObjRef &,void *);

    // posts a message or error event (with type==AidError) on the control channel
    void postMessage (const std::string &msg,const HIID &type = AidMessage,AtomicID category = AidNormal);
    
    // error messages are posted with a type of Error and a Normal category by default
    void postError (const std::string &msg,AtomicID category = AidNormal)
    { postMessage(msg,AidError,category); }
    
    // posts an error message corresponding to exception
    // error messages are posted with a type of Error and a Normal category by default
    void postError (const std::exception &exc,AtomicID category = AidNormal);
    
    // posts a generic event on the control channel
    void postEvent (const HIID &type,const ObjRef &data = ObjRef());
    void postEvent (const HIID &type,const DMI::Record::Ref &data);
    
    //##ModelId=3F5F195E0156
    virtual string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;

    //##ModelId=3F5F195E013F
    LocalDebugContext;

  private:
    // publishes state message to control channel
    void publishState ();  
      
    // sets internal state and calls publishState(), returns old state
    AtomicID setState (AtomicID state);
    
    AtomicID state () const
    { return state_; }
      
    //##ModelId=3F6196800325
    Node & resolveNode (bool &getstate,const DMI::Record &rec);

    void processCommands();
    
    void reportNodeStatus  (Node &node,int oldstat,int newstat);

    void processBreakpoint (Node &node,int bpmask,bool global);
    
    // fills a record with forest_status (level>0) and 
    // and forest_state (level>1). If level==0, does nothing.
    void fillForestStatus  (DMI::Record &rec,int level=1);
      
    // control channel
    AppAgent::EventChannel::Ref control_channel_;
    
    //##ModelId=3F5F218F02BD
    Forest forest;
    
    int forest_serial;
    int incrementForestSerial ()
    { 
      if( ++forest_serial < 1 )
        forest_serial = 1;
      return forest_serial;
    }
  
    //##ModelId=3F61920F0158
    typedef void (MeqServer::*PtrCommandMethod)(DMI::Record::Ref &out,DMI::Record::Ref &in);
    //##ModelId=3F61920F016E
    typedef std::map<HIID,PtrCommandMethod> CommandMap;
    //##ModelId=3F61920F0193
    CommandMap command_map;
    
    typedef struct {
      Node *       node;
    } DebugFrame;
    
    typedef std::list<DebugFrame> DebugStack;
    
    DebugStack debug_stack;
    
    const Node * debug_next_node;
    bool  debug_continue;
    
    // true as long as we're not exiting
    bool running_;
    
    // true if we are executing a node
    bool executing_;
    
    AtomicID state_;
    
    
    static MeqServer *mqs_;
    
    static void mqs_reportNodeStatus (Node &node,int oldstat,int newstat);

    static void mqs_processBreakpoint (Node &node,int bpmask,bool global);
    
    static void mqs_postEvent (const HIID &type,const ObjRef &data);
    
};

}; // namespace Meq

#endif /* MEQSERVER_SRC_MEQSERVER_H_HEADER_INCLUDED_D338579D */
