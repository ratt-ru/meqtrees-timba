#include "MeqServer.h"
#include "AID-MeqServer.h"
#include <DMI/AID-DMI.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <MeqGen/AID-MeqGen.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MeqNodes/ParmTable.h>
#include <DMI/BOIO.h>

    
using Debug::ssprintf;
using namespace AppControlAgentVocabulary;
using namespace VisRepeaterVocabulary;
using namespace VisVocabulary;
using namespace VisAgent;
    
namespace Meq 
{
  
static int dum =  aidRegistry_MeqServer() + 
                  aidRegistry_Meq() + 
                  aidRegistry_MeqNodes() + 
                  aidRegistry_MeqGen();

const HIID DataProcessingError = AidData|AidProcessing|AidError;
  
InitDebugContext(MeqServer,"MeqServer");

// this flag can be set in the input record of all commands dealing with
// individual nodes to have the new node state included in the command result.
// (The exception is Node.Get.State, which returns the node state anyway)
const HIID FGetState = AidGet|AidState;

// ...as field node_state
const HIID FNodeState = AidNode|AidState;

//const HIID FBreakpoint = AidBreakpoint;
const HIID FSingleShot = AidSingle|AidShot;

MeqServer * MeqServer::mqs_ = 0;

  
//##ModelId=3F5F195E0140
MeqServer::MeqServer()
    : data_mux(forest)
{
  if( mqs_ )
    Throw1("A singleton MeqServer has already been created");
  mqs_ = this;
  
  command_map["Create.Node"] = &MeqServer::createNode;
  command_map["Delete.Node"] = &MeqServer::deleteNode;
  command_map["Resolve"] = &MeqServer::resolve;
  command_map["Get.Node.List"] = &MeqServer::getNodeList;
  command_map["Get.NodeIndex"] = &MeqServer::getNodeIndex;

  command_map["Disable.Publish.Results"] = &MeqServer::disablePublishResults;
  command_map["Save.Forest"] = &MeqServer::saveForest;
  command_map["Load.Forest"] = &MeqServer::loadForest;
  command_map["Clear.Forest"] = &MeqServer::clearForest;

  // per-node commands  
  command_map["Node.Get.State"] = &MeqServer::nodeGetState;
  command_map["Node.Set.State"] = &MeqServer::nodeSetState;
  command_map["Node.Execute"] = &MeqServer::nodeExecute;
  command_map["Node.Clear.Cache"] = &MeqServer::nodeClearCache;
  command_map["Node.Publish.Results"] = &MeqServer::publishResults;
  command_map["Node.Set.Breakpoint"] = &MeqServer::nodeSetBreakpoint;
  command_map["Node.Clear.Breakpoint"] = &MeqServer::nodeClearBreakpoint;
  
  command_map["Set.Verbosity"] = &MeqServer::setVerbosity;
  command_map["Debug.Single.Step"] = &MeqServer::debugSingleStep;
  command_map["Debug.Next.Node"] = &MeqServer::debugNextNode;
  command_map["Debug.Until.Node"] = &MeqServer::debugUntilNode;
  command_map["Debug.Continue"] = &MeqServer::debugContinue;
  
  in_debugger = debug_nextnode = 0;
}

//##ModelId=3F6196800325
Node & MeqServer::resolveNode (bool &getstate,const DataRecord &rec)
{
  int nodeindex = rec[AidNodeIndex].as<int>(-1);
  string name = rec[AidName].as<string>("");
  getstate = rec[FGetState].as<bool>(false);
  if( nodeindex>0 )
  {
    Node &node = forest.get(nodeindex);
    FailWhen( name.length() && node.name() != name,"node specified by index is "+ 
        node.name()+", which does not match specified name "+name); 
    return node;
  }
  FailWhen( !name.length(),"either nodeindex or name must be specified");
  cdebug(3)<<"looking up node name "<<name<<endl;
  return forest.findNode(name);
}


void MeqServer::createNode (DataRecord::Ref &out,DataRecord::Ref::Xfer &initrec)
{
  cdebug(2)<<"creating node ";
  cdebug(3)<<initrec->sdebug(3);
  cdebug(2)<<endl;
  int nodeindex;
  const Node::Ref &ref = forest.create(nodeindex,initrec);
  // form a response message
  const string & name = ref->name();
  string classname = ref->className();
  
  out[AidNodeIndex] = nodeindex;
  out[AidName] = name;
  out[AidClass] = classname;
  out[AidMessage] = ssprintf("created node %d:%s of class %s",
                        nodeindex,name.c_str(),classname.c_str());
}

void MeqServer::deleteNode (DataRecord::Ref &out,DataRecord::Ref::Xfer &in)
{
  int nodeindex = (*in)[AidNodeIndex].as<int>(-1);
  if( nodeindex<0 )
  {
    string name = (*in)[AidName].as<string>("");
    cdebug(3)<<"looking up node name "<<name<<endl;
    FailWhen( !name.length(),"either nodeindex or name must be specified");
    nodeindex = forest.findIndex(name);
    FailWhen( nodeindex<0,"node '"+name+"' not found");
  }
  const Node::Ref &noderef = forest.getRef(nodeindex);
  string name = noderef->name();
  cdebug(2)<<"deleting node "<<name<<"("<<nodeindex<<")\n";
  // remove from forest
  forest.remove(nodeindex);
  out[AidMessage] = ssprintf("node %d (%s): deleted",nodeindex,name.c_str());
}

void MeqServer::nodeGetState (DataRecord::Ref &out,DataRecord::Ref::Xfer &in)
{
  bool getstate;
  Node & node = resolveNode(getstate,*in);
  cdebug(3)<<"getState for node "<<node.name()<<" ";
  cdebug(4)<<in->sdebug(3);
  cdebug(3)<<endl;
  out.attach(node.syncState(),DMI::READONLY|DMI::ANON);
  cdebug(5)<<"Returned state is: "<<out->sdebug(20)<<endl;
}

void MeqServer::getNodeIndex (DataRecord::Ref &out,DataRecord::Ref::Xfer &in)
{
  string name = in[AidName].as<string>();
  out[AidNodeIndex] = forest.findIndex(name);
}

void MeqServer::nodeSetState (DataRecord::Ref &out,DataRecord::Ref::Xfer &in)
{
  DataRecord::Ref rec = in;
  bool getstate;
  Node & node = resolveNode(getstate,*rec);
  cdebug(3)<<"setState for node "<<node.name()<<endl;
  rec.privatize(DMI::WRITE|DMI::DEEP);
  node.setState(rec[AidState].as_wr<DataRecord>());
  if( getstate )
    out[FNodeState] <<= node.syncState();
}

//##ModelId=3F98D91A03B9
void MeqServer::resolve (DataRecord::Ref &out,DataRecord::Ref::Xfer &in)
{
  DataRecord::Ref rec = in;
  bool getstate;
  Node & node = resolveNode(getstate,*rec);
  cdebug(2)<<"resolve for node "<<node.name()<<endl;
  // create request for the commands. Note that request ID will be null,
  // meaning it will ignore cache and go up the entire tree
  node.resolve(rec,0);
  cdebug(3)<<"resolve complete"<<endl;
  out[AidMessage] = ssprintf("node %d (%s): resolve complete",
      node.nodeIndex(),node.name().c_str());
  if( getstate )
    out[FNodeState] <<= node.syncState();
}

void MeqServer::getNodeList (DataRecord::Ref &out,DataRecord::Ref::Xfer &in)
{
  cdebug(2)<<"getNodeList: building list"<<endl;
  DataRecord &list = out <<= new DataRecord;
  int content = 
    ( in[AidNodeIndex].as<bool>(true) ? Forest::NL_NODEINDEX : 0 ) | 
    ( in[AidName].as<bool>(true) ? Forest::NL_NAME : 0 ) | 
    ( in[AidClass].as<bool>(true) ? Forest::NL_CLASS : 0 ) | 
    ( in[AidChildren].as<bool>(false) ? Forest::NL_CHILDREN : 0 ) |
    ( in[FControlStatus].as<bool>(false) ? Forest::NL_CONTROL_STATUS : 0 );
  int count = forest.getNodeList(list,content);
  cdebug(2)<<"getNodeList: got list of "<<count<<" nodes"<<endl;
}

//##ModelId=400E5B6C015E
void MeqServer::nodeExecute (DataRecord::Ref &out,DataRecord::Ref::Xfer &in)
{
  DataRecord::Ref rec = in;
  bool getstate;
  Node & node = resolveNode(getstate,*rec);
  cdebug(2)<<"nodeExecute for node "<<node.name()<<endl;
  // take request object out of record
  Request &req = rec[AidRequest].as_wr<Request>();
  if( Debug(0) )
  {
    cdebug(3)<<"    request is "<<req.sdebug(DebugLevel-1,"    ")<<endl;
    if( req.hasCells() )
    {
      cdebug(3)<<"    request cells are: "<<req.cells();
    }
  }
  Result::Ref resref;
  int flags = node.execute(resref,req);
  cdebug(2)<<"  execute() returns flags "<<ssprintf("0x%x",flags)<<endl;
  cdebug(3)<<"    result is "<<resref.sdebug(DebugLevel-1,"    ")<<endl;
  if( DebugLevel>3 && resref.valid() )
  {
    for( int i=0; i<resref->numVellSets(); i++ ) 
    {
      const VellSet &vs = resref->vellSet(i);
      if( vs.isFail() ) {
        cdebug(4)<<"  vellset "<<i<<": FAIL"<<endl;
      } else {
        cdebug(4)<<"  vellset "<<i<<": "<<vs.getValue()<<endl;
      }
    }
  }
  out[AidResult|AidCode] = flags;
  if( resref.valid() )
    out[AidResult] <<= resref;
  out[AidMessage] = ssprintf("node %d (%s): execute() returns %x",
      node.nodeIndex(),node.name().c_str(),flags);
  if( getstate )
    out[FNodeState] <<= node.syncState();
}


//##ModelId=400E5B6C01DD
void MeqServer::nodeClearCache (DataRecord::Ref &out,DataRecord::Ref::Xfer &in)
{
  DataRecord::Ref rec = in;
  bool getstate;
  Node & node = resolveNode(getstate,*rec);
  bool recursive = (*rec)[FRecursive].as<bool>(false);
  cdebug(2)<<"nodeClearCache for node "<<node.name()<<", recursive: "<<recursive<<endl;
  node.clearCache(recursive);
  out[AidMessage] = ssprintf("node %d (%s): cache cleared%s",
      node.nodeIndex(),node.name().c_str(),recursive?" recursively":"");
  if( getstate )
    out[FNodeState] <<= node.syncState();
}

//##ModelId=400E5B6C0247
void MeqServer::saveForest (DataRecord::Ref &out,DataRecord::Ref::Xfer &in)
{
  string filename = (*in)[FFileName].as<string>();
  cdebug(1)<<"saving forest to file "<<filename<<endl;
  BOIO boio(filename,BOIO::WRITE);
  int nsaved = 0;
  for( int i=1; i<=forest.maxNodeIndex(); i++ )
    if( forest.valid(i) )
    {
      Node &node = forest.get(i);
      cdebug(3)<<"saving node "<<node.name()<<endl;
      boio << node.syncState();
      nsaved++;
    }
  cdebug(1)<<"saved "<<nsaved<<" nodes to file "<<filename<<endl;
  out[AidMessage] = ssprintf("saved %d nodes to file %s",
      nsaved,filename.c_str());
}

//##ModelId=400E5B6C02B3
void MeqServer::loadForest (DataRecord::Ref &out,DataRecord::Ref::Xfer &in)
{
  string filename = (*in)[FFileName].as<string>();
  cdebug(1)<<"loading forest from file "<<filename<<endl;
  BOIO boio(filename,BOIO::READ);
  forest.clear();
  int nloaded = 0;
  DataRecord::Ref ref;
  while( boio >> ref )
  {
    int nodeindex;
    // create the node, while
    const Node & node = *forest.create(nodeindex,ref,true);
    cdebug(3)<<"loaded node "<<node.name()<<endl;
    nloaded++;
  }
  cdebug(2)<<"loaded "<<nloaded<<" nodes, setting child links"<<endl;
  for( int i=1; i<=forest.maxNodeIndex(); i++ )
    if( forest.valid(i) )
    {
      Node &node = forest.get(i);
      cdebug(3)<<"setting children for node "<<node.name()<<endl;
      node.relinkChildren();
    }
  out[AidMessage] = ssprintf("loaded %d nodes from file %s",
      nloaded,filename.c_str());
}

//##ModelId=400E5B6C0324
void MeqServer::clearForest (DataRecord::Ref &out,DataRecord::Ref::Xfer &)
{
  cdebug(1)<<"clearing forest: deleting all nodes"<<endl;
  forest.clear();
// ****
// **** added this to relinquish parm tables --- really ought to go away
  ParmTable::closeTables();
// ****
  out[AidMessage] = "all nodes deleted";
}

void MeqServer::publishResults (DataRecord::Ref &out,DataRecord::Ref::Xfer &in)
{
  DataRecord::Ref rec = in;
  bool getstate;
  Node & node = resolveNode(getstate,*rec);
  bool enable = rec[FEnable].as<bool>(true);
  const HIID &evid = rec[FEventId].as<HIID>(EvNodeResult);
  if( enable )
  {
    cdebug(2)<<"publishResults: enabling for node "<<node.name()<<endl;
    node.addResultSubscriber(EventSlot(evid,this));
    out[AidMessage] = ssprintf("node %d (%s): publishing results",
        node.nodeIndex(),node.name().c_str());
  }
  else
  {
    cdebug(2)<<"publishResults: disabling for node "<<node.name()<<endl;
    node.removeResultSubscriber(EventSlot(evid,this));
    out[AidMessage] = ssprintf("node %d (%s): no longer publishing results",
        node.nodeIndex(),node.name().c_str());
  }
  if( getstate )
    out[FNodeState] <<= node.syncState();
}

void MeqServer::setVerbosity (DataRecord::Ref &out,DataRecord::Ref::Xfer &in)
{
  cdebug(1)<<"setting verbosity level"<<endl;
  int verb = in[AidVerbosity].as<int>();
  verb = std::min(verb,2);
  verb = std::max(verb,0);
  forest.setVerbosity(verb);
  out[AidMessage] = Debug::ssprintf("verbosity level %d set",verb);
}

void MeqServer::disablePublishResults (DataRecord::Ref &out,DataRecord::Ref::Xfer &)
{
  cdebug(2)<<"disablePublishResults: disabling for all nodes"<<endl;
  for( int i=0; i<=forest.maxNodeIndex(); i++ )
    if( forest.valid(i) )
      forest.get(i).removeResultSubscriber(this);
  out[AidMessage] = "nodes no longer publishing results";
}

void MeqServer::nodeSetBreakpoint (DataRecord::Ref &out,DataRecord::Ref::Xfer &in)
{
  DataRecord::Ref rec = in;
  bool getstate;
  Node & node = resolveNode(getstate,*rec);
  int bpmask = rec[FBreakpoint].as<int>(Node::breakpointMask(Node::CS_ES_REQUEST));
  bool oneshot = rec[FSingleShot].as<bool>(false);
  cdebug(2)<<"nodeSetBreakpoint: node "<<node.name()<<" mask "<<bpmask<<(oneshot?" single-shot\n":"\n");
  node.setBreakpoint(bpmask,oneshot);
  if( getstate )
    out[FNodeState] <<= node.syncState();
  out[AidMessage] = Debug::ssprintf("node %s: set %sbreakpoint %X; "
        "new bp mask is %X",
        node.name().c_str(),oneshot?"one-shot":"",
        bpmask,node.getBreakpoints(oneshot));
}

void MeqServer::nodeClearBreakpoint (DataRecord::Ref &out,DataRecord::Ref::Xfer &in)
{
  DataRecord::Ref rec = in;
  bool getstate;
  Node & node = resolveNode(getstate,*rec);
  int bpmask = rec[FBreakpoint].as<int>(Node::CS_BP_ALL);
  bool oneshot = rec[FSingleShot].as<bool>(false);
  cdebug(2)<<"nodeClearBreakpoint: node "<<node.name()<<" mask "<<bpmask<<(oneshot?" single-shot\n":"\n");
  node.clearBreakpoint(bpmask,oneshot);
  if( getstate )
    out[FNodeState] <<= node.syncState();
  out[AidMessage] = Debug::ssprintf("node %s: clearing breakpoint %X; "
        "new bp mask is %X",node.name().c_str(),bpmask,node.getBreakpoints(oneshot));
}

void MeqServer::debugContinue (DataRecord::Ref &,DataRecord::Ref::Xfer &)
{
  if( !in_debugger )
    Throw1("can't execute a Continue command when not debugging");
  // clear all global breakpoints and continue
  forest.clearBreakpoint(Node::CS_ALL,false);
  forest.clearBreakpoint(Node::CS_ALL,true);
  debug_continue = true;
}

void MeqServer::debugSingleStep (DataRecord::Ref &out,DataRecord::Ref::Xfer &in)
{
  if( !in_debugger )
    Throw1("can't execute Debug.Single.Step command when not debugging");
  // set a global one-shot breakpoint on everything
  forest.setBreakpoint(Node::CS_ALL,true);
  debug_nextnode = 0;
  debug_continue = true;
}

void MeqServer::debugNextNode (DataRecord::Ref &out,DataRecord::Ref::Xfer &in)
{
  if( !in_debugger )
    Throw1("can't execute Debug.Next.Node command when not debugging");
  // set a global breakpoint on everything, will keep firing until a different
  // node is reached (or until a local node breakpoint occurs)
  forest.setBreakpoint(Node::CS_ALL);
  debug_nextnode = in_debugger;
  debug_continue = true;
}

void MeqServer::debugUntilNode (DataRecord::Ref &out,DataRecord::Ref::Xfer &in)
{
  if( !in_debugger )
    Throw1("can't execute Debug.Until.Node command when not debugging");
  bool getstate;
  Node & node = resolveNode(getstate,*in);
  // set one-shot breakpoint on anything in this node
  node.setBreakpoint(Node::CS_ALL,true);
  // clear all global breakpoints and continue
  forest.clearBreakpoint(Node::CS_ALL,false);
  forest.clearBreakpoint(Node::CS_ALL,true);
  debug_continue = true;
}

int MeqServer::receiveEvent (const EventIdentifier &evid,const ObjRef::Xfer &evdata,void *) 
{
  cdebug(4)<<"received event "<<evid.id()<<endl;
  control().postEvent(evid.id(),evdata);
  return 1;
}

void MeqServer::reportNodeStatus (Node &node,int oldstat,int newstat)
{
  if( forest.verbosity() <= 0 )
    return;
  // check what's changed
  int changemask = oldstat^newstat;
  // at verbosity level 1, only report changes to result type
  // at level>1, report changes to anything
  if( changemask&Node::CS_RES_MASK ||
      ( forest.verbosity()>1 && changemask )  )
  {
    DataRecord::Ref ref;
    DataRecord &rec = ref <<= new DataRecord;
    rec[AidName] = node.name();
    rec[AidNodeIndex] = node.nodeIndex();
    rec[FControlStatus] = newstat;
    if( forest.verbosity()>1 )
      rec[FRequestId] = node.currentRequestId();
    control().postEvent(EvNodeStatus,ref);
  }
}

void MeqServer::processBreakpoint (Node &node,int bpmask,bool global)
{
  // return immediately if we hit a global breakpoint after a next-node
  // command, and node hasn't changed yet
  if( global && debug_nextnode == &node )
    return;
  in_debugger = &node;
  debug_continue = false;
  // post event indicating we're stopped in the debugger
  DataRecord::Ref ref;
  DataRecord &rec = ref <<= new DataRecord;
  rec[AidName] = node.name();
  rec[AidNodeIndex] = node.nodeIndex();
  rec[FNodeState] <<= node.syncState();
  rec[AidMessage] = "stopped at breakpoint " + node.name() + ":" + node.getStrExecState();
  control().postEvent(EvDebugStop,ref);
  // keep on processing commands until asked to continue
  while( control().state() > 0 && !debug_continue )  // while in a running state
    processCommands();
  in_debugger = 0;
}

// static callbacks mapping to methods of the global MeqServer object
void MeqServer::mqs_reportNodeStatus (Node &node,int oldstat,int newstat)
{
  mqs_->reportNodeStatus(node,oldstat,newstat);
}

void MeqServer::mqs_processBreakpoint (Node &node,int bpmask,bool global)
{
  mqs_->processBreakpoint(node,bpmask,global);
}

void MeqServer::processCommands ()
{
  // check for any commands from the control agent
  HIID cmdid;
  DataRecord::Ref cmddata;
  if( control().getCommand(cmdid,cmddata,AppEvent::WAIT) == AppEvent::SUCCESS 
      && cmdid.matches(AppCommandMask) )
  {
    // strip off the App.Control.Command prefix -- the -1 is not very
    // nice because it assumes a wildcard is the last thing in the mask.
    // Which it usually will be
    cmdid = cmdid.subId(AppCommandMask.length()-1);
    cdebug(3)<<"received app command "<<cmdid.toString()<<endl;
    int request_id = 0;
    bool silent = false;
    DataRecord::Ref retval(DMI::ANONWR);
    bool have_error = true;
    string error_str;
    try
    {
      request_id = cmddata[FRequestId].as<int>(0);
      ObjRef ref = cmddata[FArgs].remove();
      silent     = cmddata[FSilent].as<bool>(false);
      DataRecord::Ref args;
      if( ref.valid() )
      {
        FailWhen(!ref->objectType()==TpDataRecord,"invalid args field");
        args = ref.ref_cast<DataRecord>();
      }
      CommandMap::const_iterator iter = command_map.find(cmdid);
      if( iter != command_map.end() )
      {
        // execute the command, catching any errors
        (this->*(iter->second))(retval,args);
        // got here? success!
        have_error = false;
      }
      else // command not found
        error_str = "unknown command "+cmdid.toString();
    }
    catch( std::exception &exc )
    {
      have_error = true;
      error_str = exc.what();
    }
    catch( ... )
    {
      have_error = true;
      error_str = "unknown exception while processing command";
    }
    // send back reply if quiet flag has not been raised;
    // errors are always sent back
    if( !silent || have_error )
    {
      // in case of error, insert error message into return value
      if( have_error )
        retval[AidError] = error_str;
      HIID reply_id = CommandResultPrefix|cmdid;
      if( request_id )
        reply_id |= request_id;
      control().postEvent(reply_id,retval);
    }
  }
}

//##ModelId=3F608106021C
void MeqServer::run ()
{
  // connect forest events to data_mux slots (so that the mux can register
  // i/o nodes)
  forest.addSubscriber(AidCreate,EventSlot(VisDataMux::EventCreate,&data_mux));
  forest.addSubscriber(AidDelete,EventSlot(VisDataMux::EventDelete,&data_mux));
  forest.setDebuggingCallbacks(mqs_reportNodeStatus,mqs_processBreakpoint);
  
  verifySetup(True);
  DataRecord::Ref initrec;
  HIID output_event;
  string doing_what,error_str;
  bool have_error;
  // keep running as long as start() on the control agent succeeds
  while( control().start(initrec) == AppState::RUNNING )
  {
    have_error = false;
    try
    {
      // [re]initialize i/o agents with record returned by control
      if( initrec[input().initfield()].exists() )
      {
        doing_what = "initializing input agent";
        output_event = InputInitFailed;
        cdebug(1)<<doing_what<<endl;
        if( !input().init(*initrec) )
          Throw("init failed");
      }
      if( initrec[output().initfield()].exists() )
      {
        doing_what = "initializing output agent";
        output_event = OutputInitFailed;
        cdebug(1)<<doing_what<<endl;
        if( !output().init(*initrec) )
          Throw("init failed");
      }
    }
    catch( std::exception &exc )
    { have_error = true; error_str = exc.what(); }
    catch( ... )
    { have_error = true; error_str = "unknown exception"; }
    // in case of error, generate event and go back to start
    if( have_error )
    {
      error_str = "error " + doing_what + ": " + error_str;
      cdebug(1)<<error_str<<", waiting for reinitialization"<<endl;
      DataRecord::Ref retval(DMI::ANONWR);
      retval[AidError] = error_str;
      control().postEvent(output_event,retval);
      continue;
    }
    
    // init the data mux
    data_mux.init(*initrec,input(),output(),control());
    // get params from control record
    int ntiles = 0;
    DataRecord::Ref header;
    bool reading_data=False;
    HIID vdsid,datatype;
    
    control().setStatus(StStreamState,"none");
    control().setStatus(StNumTiles,0);
    control().setStatus(StVDSID,vdsid);
    
    // run main loop
    while( control().state() > 0 )  // while in a running state
    {
      // check for any incoming data
      DataRecord::Ref eventrec;
      eventrec.detach();
      cdebug(4)<<"checking input\n";
      HIID id;
      ObjRef ref,header_ref;
      int instat = input().getNext(id,ref,0,AppEvent::WAIT);
      if( instat > 0 )
      { 
        string output_message;
        HIID output_event;
        have_error = false;
        try
        {
          // process data event
          if( instat == DATA )
          {
            doing_what = "processing input DATA event";
            VisTile::Ref tileref = ref.ref_cast<VisTile>().copy(DMI::WRITE);
            cdebug(4)<<"received tile "<<tileref->tileId()<<endl;
            if( !reading_data )
            {
              control().setStatus(StStreamState,"DATA");
              reading_data = True;
            }
            ntiles++;
            if( !(ntiles%100) )
              control().setStatus(StNumTiles,ntiles);
            // deliver tile to data mux
            data_mux.deliverTile(tileref);
          }
          else if( instat == FOOTER )
          {
            doing_what = "processing input FOOTER event";
            cdebug(2)<<"received footer"<<endl;
            reading_data = False;
            eventrec <<= new DataRecord;
            if( header.valid() )
              eventrec[AidHeader] <<= header.copy();
            if( ref.valid() )
              eventrec[AidFooter] <<= ref.copy();
            data_mux.deliverFooter(*(ref.ref_cast<DataRecord>()));
            output_event = DataSetFooter;
            output_message = ssprintf("received footer for dataset %s, %d tiles written",
                id.toString().c_str(),ntiles);
            control().setStatus(StStreamState,"END");
            control().setStatus(StNumTiles,ntiles);
            // post to output only if writing some data
          }
          else if( instat == HEADER )
          {
            doing_what = "processing input HEADER event";
            cdebug(2)<<"received header"<<endl;
            reading_data = False;
            header = ref;
            eventrec <<= new DataRecord;
            eventrec[AidHeader] <<= header.copy();
            data_mux.deliverHeader(*header);
            output_event = DataSetHeader;
            output_message = "received header for dataset "+id.toString();
            if( !datatype.empty() )
              output_message += ", " + datatype.toString();
            control().setStatus(StStreamState,"HEADER");
            control().setStatus(StNumTiles,ntiles=0);
            control().setStatus(StVDSID,vdsid = id);
            control().setStatus(FDataType,datatype);
          }
          // generate output event if one was queued up
          if( !output_event.empty() )
            postDataEvent(output_event,output_message,eventrec);
        }
        catch( std::exception &exc )
        {
          have_error = true;
          error_str = exc.what();
          cdebug(2)<<"got exception while " + doing_what + ": "<<exc.what()<<endl;
        }
        catch( ... )
        {
          have_error = true;
          error_str = "unknown exception";
          cdebug(2)<<"unknown exception processing input"<<endl;
        }
        // in case of error, generate event
        if( have_error )
        {
          DataRecord::Ref retval(DMI::ANONWR);
          retval[AidError] = error_str;
          retval[AidData|AidId] = id;
          control().postEvent(DataProcessingError,retval);
        }
      }
      processCommands();
    }
    // go back up for another start() call
  }
  cdebug(1)<<"exiting with control state "<<control().stateString()<<endl;
  control().close();
  forest.removeSubscriber(AidCreate,&data_mux);
  forest.removeSubscriber(AidDelete,&data_mux);
}

//##ModelId=3F5F195E0156
string MeqServer::sdebug(int detail, const string &prefix, const char *name) const
{
  return "MeqServer";
}

};
