#ifndef MEQSERVER_SRC_MEQSERVER_H_HEADER_INCLUDED_D338579D
#define MEQSERVER_SRC_MEQSERVER_H_HEADER_INCLUDED_D338579D

#include <DMI/Events.h>
#include <MEQ/Forest.h>
#include <AppUtils/VisPipe.h>
#include <MeqServer/VisDataMux.h>
#include <AppUtils/VisRepeater.h>

#pragma aidgroup MeqServer    
#pragma aid Node Name NodeIndex MeqServer
#pragma aid Create Delete Get Set State Request Resolve Child Children List
#pragma aid App Command Args Result Data Processing Error Message Code
#pragma aid Execute Clear Cache Save Load Forest Recursive Forest Header Version 
#pragma aid Publish Results Enable Disable Event Id Silent Idle Stream 
#pragma aid Debug Breakpoint Single Shot Step Continue Until Stop Level
#pragma aid Get Forest Status Stack Running Changed All Disabled Publishing
    
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
class MeqServer : public AppAgent::VisRepeater, public AppAgent::EventRecepient
{
  public:
    //##ModelId=3F5F195E0140
    MeqServer();

    //##ModelId=3F608106021C
    virtual void run();

    // sets state
    void setForestState (DMI::Record::Ref &out,DMI::Record::Ref &in);
    // gets status + state record
    void getForestState (DMI::Record::Ref &out,DMI::Record::Ref &in);
    // gets status only
    void getForestStatus (DMI::Record::Ref &out,DMI::Record::Ref &in);
    
    //##ModelId=3F61920F01A8
    void createNode   (DMI::Record::Ref &out,DMI::Record::Ref &in);
    //##ModelId=3F61920F01FA
    void deleteNode   (DMI::Record::Ref &out,DMI::Record::Ref &in);
    //##ModelId=3F61920F024E
    void nodeGetState (DMI::Record::Ref &out,DMI::Record::Ref &in);
    //##ModelId=3F61920F02A4
    void nodeSetState (DMI::Record::Ref &out,DMI::Record::Ref &in);
    //##ModelId=3F98D91A03B9
    void resolve      (DMI::Record::Ref &out,DMI::Record::Ref &in);
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
    
    virtual int receiveEvent (const EventIdentifier &evid,const ObjRef &,void *);

    // posts a message or error event (with type==AidError) to the control agent
    void postMessage (const std::string &msg,const HIID &type = AidMessage,AtomicID category = AidNormal);
    
    //##ModelId=3F5F195E0156
    virtual string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;

    //##ModelId=3F5F195E013F
    LocalDebugContext;

  private:
    //##ModelId=3F6196800325
    Node & resolveNode (bool &getstate,const DMI::Record &rec);

    void processCommands();
    
    void reportNodeStatus  (Node &node,int oldstat,int newstat);

    void processBreakpoint (Node &node,int bpmask,bool global);
    
    // fills a record with forest_status (level>0) and 
    // and forest_state (level>1). If level==0, does nothing.
    void fillForestStatus  (DMI::Record &rec,int level=1);
      
    //##ModelId=3F5F218F02BD
    Forest forest;
  
    //##ModelId=3F61920F0158
    typedef void (MeqServer::*PtrCommandMethod)(DMI::Record::Ref &out,DMI::Record::Ref &in);
    //##ModelId=3F61920F016E
    typedef std::map<HIID,PtrCommandMethod> CommandMap;
    //##ModelId=3F61920F0193
    CommandMap command_map;
    //##ModelId=3F9CE0D3027D
    VisDataMux data_mux;
    
    typedef struct {
      Node *       node;
    } DebugFrame;
    
    typedef std::list<DebugFrame> DebugStack;
    
    DebugStack debug_stack;
    
    const Node * debug_next_node;
    bool  debug_continue;
    
    
    static MeqServer *mqs_;
    
    static void mqs_reportNodeStatus (Node &node,int oldstat,int newstat);

    static void mqs_processBreakpoint (Node &node,int bpmask,bool global);
    
};

}; // namespace Meq

#endif /* MEQSERVER_SRC_MEQSERVER_H_HEADER_INCLUDED_D338579D */
