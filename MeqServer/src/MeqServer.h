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
#pragma aid Execute Clear Cache Save Load Forest Recursive 
#pragma aid Publish Results Enable Disable Event Id Silent
#pragma aid Debug Breakpoint Single Shot Step Continue Until Stop Level
#pragma aid addstate
    
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
class MeqServer : public VisRepeater, public EventRecepient
{
  public:
    //##ModelId=3F5F195E0140
    MeqServer();

    //##ModelId=3F608106021C
    virtual void run();

    //##ModelId=3F61920F01A8
    void createNode   (DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    //##ModelId=3F61920F01FA
    void deleteNode   (DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    //##ModelId=3F61920F024E
    void nodeGetState (DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    //##ModelId=3F61920F02A4
    void nodeSetState (DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    //##ModelId=3F98D91A03B9
    void resolve      (DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    //##ModelId=3F98D91B0064
    void getNodeList  (DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    
    void getNodeIndex (DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    
    //##ModelId=400E5B6C015E
    void nodeExecute  (DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    //##ModelId=400E5B6C01DD
    void nodeClearCache (DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    //##ModelId=400E5B6C0247
    void saveForest (DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    //##ModelId=400E5B6C02B3
    void loadForest (DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    //##ModelId=400E5B6C0324
    void clearForest (DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    
    void publishResults (DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    void disablePublishResults (DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    
    void nodeSetBreakpoint (DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    void nodeClearBreakpoint (DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    
    void debugSetLevel      (DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    void debugSingleStep    (DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    void debugNextNode      (DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    void debugContinue      (DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    void debugUntilNode     (DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    
    virtual int receiveEvent (const EventIdentifier &evid,const ObjRef::Xfer &,void *);
    
    //##ModelId=3F5F195E0156
    virtual string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;

    //##ModelId=3F5F195E013F
    LocalDebugContext;

  private:
    //##ModelId=3F6196800325
    Node & resolveNode (bool &getstate,const DataRecord &rec);

    void processCommands();
    
    void reportNodeStatus (Node &node,int oldstat,int newstat);

    void processBreakpoint (Node &node,int bpmask,bool global);
      
    //##ModelId=3F5F218F02BD
    Forest forest;
  
    //##ModelId=3F61920F0158
    typedef void (MeqServer::*PtrCommandMethod)(DataRecord::Ref &out,DataRecord::Ref::Xfer &in);
    //##ModelId=3F61920F016E
    typedef std::map<HIID,PtrCommandMethod> CommandMap;
    //##ModelId=3F61920F0193
    CommandMap command_map;
    //##ModelId=3F9CE0D3027D
    VisDataMux data_mux;
    
    Node * in_debugger;
    const Node * debug_nextnode;
    bool debug_continue;
    
    static MeqServer *mqs_;
    
    static void mqs_reportNodeStatus (Node &node,int oldstat,int newstat);

    static void mqs_processBreakpoint (Node &node,int bpmask,bool global);
    
};

}; // namespace Meq

#endif /* MEQSERVER_SRC_MEQSERVER_H_HEADER_INCLUDED_D338579D */
