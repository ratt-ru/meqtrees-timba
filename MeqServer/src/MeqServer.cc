#include "MeqServer.h"
#include "AID-MeqServer.h"
#include <DMI/AID-DMI.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MeqNodes/ParmTable.h>
#include <DMI/BOIO.h>
#include <DMI/List.h>
#include <MeqServer/MeqPython.h>
#include <MeqServer/Sink.h>
#include <MeqServer/Spigot.h>

#include <linux/unistd.h>

// TEST_PYTHON_CONVERSION: if defined, will test objects for 
// convertability to Python (see below)
// only useful for debugging really
#if LOFAR_DEBUG
//  #define TEST_PYTHON_CONVERSION 1
#else
  #undef TEST_PYTHON_CONVERSION
#endif
    
using Debug::ssprintf;
using namespace AppAgent;
    
namespace Meq 
{
  
static int dum =  aidRegistry_MeqServer() + 
                  aidRegistry_Meq() + 
                  aidRegistry_MeqNodes();

const HIID MeqCommandPrefix = AidCommand;
const HIID MeqCommandMask   = AidCommand|AidWildcard;
const HIID MeqResultPrefix  = AidResult;


const HIID DataProcessingError = AidData|AidProcessing|AidError;
  
InitDebugContext(MeqServer,"MeqServer");

// this flag can be set in the input record of all commands dealing with
// individual nodes to have the new node state included in the command result.
// (The exception is Node.Get.State, which returns the node state anyway)
const HIID FGetState = AidGet|AidState;
// this flag can be set in the input record of most commands to request
// a forest status update in the reply 
// Set to 1 to get basic status in field forest_status
// Set to 2 to also get the full forest state record in field forest_state
// (The exception is Node.Get.State, which returns the node state as the 
// top-level record, Node.Create, where the input record is the node state,
// and Set.Forest.State, which returns the full status anyway)
const HIID FGetForestStatus = AidGet|AidForest|AidStatus;

// this field is set to the new serial number in the output record of a command
// whenever the forest itself has changed (i.e. nodes created or deleted, etc.)
const HIID FForestChanged = AidForest|AidChanged;
// The forest serial number is also returned from Get.Node.List; and can
// also be supplied back to it to cause a no-op
const HIID FForestSerial = AidForest|AidSerial;

// this field is set to True in the output record of a command when 
// publishing is disabled for all nodes.
const HIID FDisabledAllPublishing = AidDisabled|AidAll|AidPublishing;

// ...as field node_state
// const HIID FNodeState = AidNode|AidState;

//const HIID FBreakpoint = AidBreakpoint;
const HIID FSingleShot = AidSingle|AidShot;

MeqServer * MeqServer::mqs_ = 0;

// application run-states
const int AppState_Idle    = -( AidIdle.id() );
const int AppState_Stream  = -( AidStream.id() );
const int AppState_Execute = -( AidExecute.id() );
const int AppState_Debug   = -( AidDebug.id() );
  
//##ModelId=3F5F195E0140
MeqServer::MeqServer()
    : forest_serial(1)
{
  if( mqs_ )
    Throw1("A singleton MeqServer has already been created");
  
  state_ = AidIdle;
  
  // default control channel is null
  control_channel_.attach(new AppAgent::EventChannel,DMI::SHARED|DMI::WRITE);
  
  mqs_ = this;
  
  command_map["Halt"] = &MeqServer::halt;
  
  command_map["Get.Forest.State"] = &MeqServer::getForestState;
  command_map["Set.Forest.State"] = &MeqServer::setForestState;
  
  command_map["Create.Node"] = &MeqServer::createNode;
  command_map["Create.Node.Batch"] = &MeqServer::createNodeBatch;
  command_map["Delete.Node"] = &MeqServer::deleteNode;
  command_map["Resolve"] = &MeqServer::resolve;
  command_map["Resolve.Batch"] = &MeqServer::resolveBatch;
  command_map["Get.Node.List"] = &MeqServer::getNodeList;
  command_map["Get.Forest.Status"] = &MeqServer::getForestStatus;
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
  
  command_map["Debug.Set.Level"] = &MeqServer::debugSetLevel;
  command_map["Debug.Single.Step"] = &MeqServer::debugSingleStep;
  command_map["Debug.Next.Node"] = &MeqServer::debugNextNode;
  command_map["Debug.Until.Node"] = &MeqServer::debugUntilNode;
  command_map["Debug.Continue"] = &MeqServer::debugContinue;
  
  debug_next_node = 0;
  running_ = executing_ = false;
}

MeqServer::~MeqServer ()
{
}

static string makeNodeLabel (const string &name,int)
{
  return ssprintf("node '%s'",name.c_str());
}

static string makeNodeLabel (const Meq::Node &node)
{
  return ssprintf("node '%s'",node.name().c_str());
}

static string makeNodeMessage (const Meq::Node &node,const string &msg)
{
  return makeNodeLabel(node) + ": " + msg;
}

static string makeNodeMessage (const string &msg1,const Meq::Node &node,const string &msg2 = string())
{
  string str = msg1 + " " + makeNodeLabel(node);
  if( !msg2.empty() )
    str += " " + msg2;
  return str;
}


//##ModelId=3F6196800325
Node & MeqServer::resolveNode (bool &getstate,const DMI::Record &rec)
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


void MeqServer::halt (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  cdebug(1)<<"halting MeqServer"<<endl;
  running_ = false;
  out()[AidMessage] = "halting the meqserver";
}

void MeqServer::setForestState (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  cdebug(3)<<"setForestState()"<<endl;
  DMI::Record::Ref ref = in[AidState].ref();
  forest.setState(ref);
  fillForestStatus(out(),2);
}

void MeqServer::getForestState (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  fillForestStatus(out(),2);
}

void MeqServer::getForestStatus (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  fillForestStatus(out(),in[FGetForestStatus].as<int>(1));
}

void MeqServer::createNode (DMI::Record::Ref &out,DMI::Record::Ref &initrec)
{
  cdebug(2)<<"creating node ";
  cdebug(3)<<initrec->sdebug(3);
  cdebug(2)<<endl;
  int nodeindex;
  Node & node = forest.create(nodeindex,initrec);
  // form a response message
  const string & name = node.name();
  string classname = node.className();
  
  out[AidNodeIndex] = nodeindex;
  out[AidName] = name;
  out[AidClass] = classname;
  out[AidMessage] = makeNodeMessage("created",node,"of class "+classname);
  out[FForestChanged] = incrementForestSerial();
}

void MeqServer::createNodeBatch (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  DMI::Container &batch = in[AidBatch].as_wr<DMI::Container>();
  int nn = batch.size();
  postMessage(ssprintf("creating %d nodes, please wait",nn));
  cdebug(2)<<"batch-creating "<<nn<<" nodes";
  for( int i=0; i<nn; i++ )
  {
    ObjRef ref;
    batch[i].detach(&ref);
    DMI::Record::Ref recref(ref);
    ref.detach();
    int nodeindex;
    try
    {
      Node & node = forest.create(nodeindex,recref);
    }
    catch( std::exception &exc )
    {
      postError(exc);
    }
  }
  // form a response message
  out[AidMessage] = ssprintf("created %d nodes",nn);
  out[FForestChanged] = incrementForestSerial();
}

void MeqServer::deleteNode (DMI::Record::Ref &out,DMI::Record::Ref &in)
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
  Node &node = forest.get(nodeindex);
  string name = node.name();
  cdebug(2)<<"deleting node "<<name<<"("<<nodeindex<<")\n";
  // remove from forest
  forest.remove(nodeindex);
  // do not use node below: ref no longer valid
  out[AidMessage] = "deleted " + makeNodeLabel(name,nodeindex);
  // fill optional responce fields
  fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
  out[FForestChanged] = incrementForestSerial();
}

void MeqServer::nodeGetState (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  bool getstate;
  Node & node = resolveNode(getstate,*in);
  cdebug(3)<<"getState for node "<<node.name()<<" ";
  cdebug(4)<<in->sdebug(3);
  cdebug(3)<<endl;
  out.attach(node.syncState());
  cdebug(5)<<"Returned state is: "<<out->sdebug(20)<<endl;
}

void MeqServer::getNodeIndex (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  string name = in[AidName].as<string>();
  out[AidNodeIndex] = forest.findIndex(name);
  fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
}

void MeqServer::nodeSetState (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  DMI::Record::Ref rec = in;
  bool getstate;
  Node & node = resolveNode(getstate,*rec);
  cdebug(3)<<"setState for node "<<node.name()<<endl;
  DMI::Record::Ref ref = rec[AidState].ref();
  node.setState(ref);
  if( getstate )
    out[FNodeState] <<= node.syncState();
  fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
}

//##ModelId=3F98D91A03B9
void MeqServer::resolve (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  DMI::Record::Ref rec = in;
  bool getstate;
  Node & node = resolveNode(getstate,*rec);
  cdebug(2)<<"resolve for node "<<node.name()<<endl;
  node.resolve(0,false,rec,0);
  cdebug(3)<<"resolve complete"<<endl;
  out[AidMessage] = makeNodeMessage(node,"resolve complete");
  if( getstate )
    out[FNodeState] <<= node.syncState();
  fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
}

void MeqServer::resolveBatch (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  const DMI::Vec & names = in[AidName].as<DMI::Vec>();
  int nn = names.size(Tpstring);
  postMessage(ssprintf("resolving %d nodes, please wait",nn));
  cdebug(2)<<"batch-resolve of "<<nn<<" nodes\n";
  for( int i=0; i<nn; i++ )
  {
    Node &node = forest.findNode(names[i].as<string>());
    node.resolve(0,false,in,0);
  }
  cdebug(3)<<"resolve complete"<<endl;
  out[AidMessage] = ssprintf("resolved %d nodes",nn);
  fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
}

void MeqServer::getNodeList (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  cdebug(2)<<"getNodeList: building list"<<endl;
  DMI::Record &list = out <<= new DMI::Record;
  int serial = in[FForestSerial].as<int>(0);
  if( !serial || serial != forest_serial )
  {
    int content = 
      ( in[AidNodeIndex].as<bool>(true) ? Forest::NL_NODEINDEX : 0 ) | 
      ( in[AidName].as<bool>(true) ? Forest::NL_NAME : 0 ) | 
      ( in[AidClass].as<bool>(true) ? Forest::NL_CLASS : 0 ) | 
      ( in[AidChildren].as<bool>(false) ? Forest::NL_CHILDREN : 0 ) |
      ( in[FControlStatus].as<bool>(false) ? Forest::NL_CONTROL_STATUS : 0 ) |
      ( in[FProfilingStats].as<bool>(false) ? Forest::NL_PROFILING_STATS : 0 );
    int count = forest.getNodeList(list,content);
    cdebug(2)<<"getNodeList: got list of "<<count<<" nodes"<<endl;
    out[FForestSerial] = forest_serial;
  }
  fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
}

//##ModelId=400E5B6C015E
void MeqServer::nodeExecute (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  AtomicID oldstate = setState(AidExecuting);
  try
  {
    DMI::Record::Ref rec = in;
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
    // post status event
    executing_ = true;
    DMI::Record::Ref status(DMI::ANONWR);
    status[AidMessage] = ssprintf("executing node '%s'",node.name().c_str());
    fillForestStatus(status());
    postEvent("Forest.Status",status);
    // execute node
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
    if( flags&Node::RES_FAIL )
    {
      string msg;
      // extract fail message fro result
      if( resref.valid() && resref->numVellSets() >= 1 )
      {
        const VellSet &vs = resref->vellSet(0);
        if( vs.isFail() && vs.numFails() > 0 )
          msg = ": "+vs.getFailMessage(0);
      }
      out[AidError] = makeNodeMessage(node,ssprintf("execute() failed%s (return code 0x%x)",msg.c_str(),flags));
    }
    else
      out[AidMessage] = makeNodeMessage(node,ssprintf("execute() successful (return code 0x%x)",flags));
    if( resref.valid() )
      out[AidResult] <<= resref;
    if( getstate )
      out[FNodeState] <<= node.syncState();
    fillForestStatus(out(),in[FGetForestStatus].as<int>(1));
  }
  catch( std::exception &exc )
  {
    executing_ = false;
    setState(oldstate);
//    control().setState(old_control_state);
//    old_paused ? control().pause() : control().resume();
    throw;
  }
  executing_ = false;
  setState(oldstate);
//  control().setState(old_control_state);
//  old_paused ? control().pause() : control().resume();
}


//##ModelId=400E5B6C01DD
void MeqServer::nodeClearCache (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  DMI::Record::Ref rec = in;
  bool getstate;
  Node & node = resolveNode(getstate,*rec);
  bool recursive = (*rec)[FRecursive].as<bool>(false);
  cdebug(2)<<"nodeClearCache for node "<<node.name()<<", recursive: "<<recursive<<endl;
  node.clearCache(recursive);
  out[AidMessage] = makeNodeMessage(node,recursive?"cache cleared recursively":"cache cleared");
  if( getstate )
    out[FNodeState] <<= node.syncState();
  fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
}

//##ModelId=400E5B6C0247
void MeqServer::saveForest (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  if( !debug_stack.empty() )
    Throw1("can't execute Save.Forest while debugging");
  string filename = (*in)[FFileName].as<string>();
  cdebug(1)<<"saving forest to file "<<filename<<endl;
  postMessage(ssprintf("saving forest to file %s, please wait",filename.c_str()));
  BOIO boio(filename,BOIO::WRITE);
  int nsaved = 0;
  // write header record
  DMI::Record header;
  header["Forest.Header.Version"] = 1;
  boio << header;
  // write forest state
  boio << forest.state();
  // write all nodes
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
  fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
}

//##ModelId=400E5B6C02B3
void MeqServer::loadForest (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  if( !debug_stack.empty() )
    Throw1("can't execute Load.Forest while debugging");
  string filename = (*in)[FFileName].as<string>();
  cdebug(1)<<"loading forest from file "<<filename<<endl;
  postMessage(ssprintf("loading forest from file %s, please wait",filename.c_str()));
  forest.clear();
  int nloaded = 0;
  DMI::Record::Ref ref;
  std::string fmessage;
  // open file
  BOIO boio(filename,BOIO::READ);
  // get header record out
  if( ! (boio >> ref) )
  {
    Throw("no records in file");
  }
  // is this a version record?
  int version = ref["Forest.Header.Version"].as<int>(-1);
  if( version >=1 )
  {
    // version 1+: forest state comes first
    if( !(boio >> ref) )
    {
      Throw("no forest state in file");
    }
    forest.setState(ref,true);
    // then get next node record for loop below
    if( !(boio >> ref) )
      ref.detach();
    fmessage = "loaded %d nodes and forest state from file %s";
  }
  else
  {
    // else version 0: nothing but node records in here, so fall through
    fmessage = "loaded %d nodes from old-style file %s";
  }
  // ok, at this point we expect a bunch of node records
  do
  {
    int nodeindex;
    // create the node
    Node & node = forest.create(nodeindex,ref,true);
    cdebug(3)<<"loaded node "<<node.name()<<endl;
    nloaded++;
  }
  while( boio >> ref );
  cdebug(2)<<"loaded "<<nloaded<<" nodes, setting child links"<<endl;
  for( int i=1; i<=forest.maxNodeIndex(); i++ )
    if( forest.valid(i) )
    {
      Node &node = forest.get(i);
      cdebug(3)<<"setting children for node "<<node.name()<<endl;
      node.relinkChildren();
    }
  out[AidMessage] = ssprintf(fmessage.c_str(),nloaded,filename.c_str());
  fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
  out[FForestChanged] = incrementForestSerial();
}

//##ModelId=400E5B6C0324
void MeqServer::clearForest (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  if( !debug_stack.empty() )
    Throw1("can't execute Clear.Forest while debugging");
  cdebug(1)<<"clearing forest: deleting all nodes"<<endl;
  forest.clear();
// ****
// **** added this to relinquish parm tables --- really ought to go away
  ParmTable::closeTables();
// ****
  out[AidMessage] = "all nodes deleted";
  fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
  out[FForestChanged] = incrementForestSerial();
}

void MeqServer::publishResults (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  DMI::Record::Ref rec = in;
  bool getstate;
  Node & node = resolveNode(getstate,*rec);
  bool enable = rec[FEnable].as<bool>(true);
  const HIID &evid = rec[FEventId].as<HIID>(EvNodeResult);
  if( enable )
  {
    cdebug(2)<<"publishResults: enabling for node "<<node.name()<<endl;
    node.addResultSubscriber(EventSlot(evid,this));
    out[AidMessage] = makeNodeMessage(node,"publishing snapshots");
  }
  else
  {
    cdebug(2)<<"publishResults: disabling for node "<<node.name()<<endl;
    node.removeResultSubscriber(EventSlot(evid,this));
    out[AidMessage] = makeNodeMessage(node,"not publishing snapshots");
  }
  if( getstate )
    out[FNodeState] <<= node.syncState();
  fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
}

void MeqServer::disablePublishResults (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  cdebug(2)<<"disablePublishResults: disabling for all nodes"<<endl;
  for( int i=0; i<=forest.maxNodeIndex(); i++ )
    if( forest.valid(i) )
      forest.get(i).removeResultSubscriber(this);
  out[AidMessage] = "snapshots disabled on all nodes";
  out[FDisabledAllPublishing] = true;
  fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
}

void MeqServer::nodeSetBreakpoint (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  DMI::Record::Ref rec = in;
  bool getstate;
  Node & node = resolveNode(getstate,*rec);
  int bpmask = rec[FBreakpoint].as<int>(Node::breakpointMask(Node::CS_ES_REQUEST));
  bool oneshot = rec[FSingleShot].as<bool>(false);
  cdebug(2)<<"nodeSetBreakpoint: node "<<node.name()<<" mask "<<bpmask<<(oneshot?" single-shot\n":"\n");
  node.setBreakpoint(bpmask,oneshot);
  if( getstate )
    out[FNodeState] <<= node.syncState();
  out[AidMessage] = makeNodeMessage(node,ssprintf("set %sbreakpoint %X; "
                                    "new bp mask is %X",
                                    oneshot?"one-shot ":"",
                                    bpmask,node.getBreakpoints(oneshot)));
  fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
}

void MeqServer::nodeClearBreakpoint (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  DMI::Record::Ref rec = in;
  bool getstate;
  Node & node = resolveNode(getstate,*rec);
  int bpmask = rec[FBreakpoint].as<int>(Node::CS_BP_ALL);
  bool oneshot = rec[FSingleShot].as<bool>(false);
  cdebug(2)<<"nodeClearBreakpoint: node "<<node.name()<<" mask "<<bpmask<<(oneshot?" single-shot\n":"\n");
  node.clearBreakpoint(bpmask,oneshot);
  if( getstate )
    out[FNodeState] <<= node.syncState();
  out[AidMessage] = makeNodeMessage(node,ssprintf("clearing breakpoint %X; "
        "new bp mask is %X",bpmask,node.getBreakpoints(oneshot)));
  fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
}

void MeqServer::debugSetLevel (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  cdebug(1)<<"setting debugging level"<<endl;
  int verb = in[AidDebug|AidLevel].as<int>();
  verb = std::min(verb,2);
  verb = std::max(verb,0);
  forest.setDebugLevel(verb);
  std::string msg = Debug::ssprintf("debug level %d set",verb);
  if( !verb )
    msg += " (disabled)";
  out[AidMessage] = msg;
  fillForestStatus(out(),in[FGetForestStatus].as<int>(1));
}


void MeqServer::debugContinue (DMI::Record::Ref &,DMI::Record::Ref &)
{
// continue always allowed, since it doesn't hurt anything
//  if( in_debugger )
//    Throw1("can't execute a Continue command when not debugging");
  // clear all global breakpoints and continue
  forest.clearBreakpoint(Node::CS_ALL,false);
  forest.clearBreakpoint(Node::CS_ALL,true);
  debug_continue = true;
}

void MeqServer::debugSingleStep (DMI::Record::Ref &,DMI::Record::Ref &in)
{
  if( debug_stack.empty() )
    Throw1("can't execute Debug.Single.Step command when not debugging");
  // set a global one-shot breakpoint on everything
  forest.setBreakpoint(Node::CS_ALL,true);
  debug_next_node = 0;
  debug_continue = true;
}

void MeqServer::debugNextNode (DMI::Record::Ref &,DMI::Record::Ref &in)
{
  if( debug_stack.empty() )
    Throw1("can't execute Debug.Next.Node command when not debugging");
  // set a global breakpoint on everything, will keep firing until a different
  // node is reached (or until a local node breakpoint occurs)
  forest.setBreakpoint(Node::CS_ALL);
  debug_next_node = debug_stack.front().node;
  debug_continue = true;
}

void MeqServer::debugUntilNode (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  if( debug_stack.empty() )
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

int MeqServer::receiveEvent (const EventIdentifier &evid,const ObjRef &evdata,void *) 
{
  cdebug(4)<<"received event "<<evid.id()<<endl;
#ifdef TEST_PYTHON_CONVERSION
  MeqPython::testConversion(*evdata);
#endif
  control().postEvent(evid.id(),evdata);
  return 1;
}

void MeqServer::postEvent (const HIID &type,const ObjRef &data)
{
  control().postEvent(type,data);
}

void MeqServer::postEvent (const HIID &type,const DMI::Record::Ref &data)
{
  control().postEvent(type,data);
}

void MeqServer::postError (const std::exception &exc,AtomicID category)
{
  DMI::Record::Ref out(new DMI::Record);
  out[AidError] = exceptionToObj(exc);
  control().postEvent(AidError,out,category);
}

void MeqServer::postMessage (const std::string &msg,const HIID &type,AtomicID category)
{
  DMI::Record::Ref out(new DMI::Record);
  if( type == HIID(AidError) )
    out[AidError] = msg;
  else
    out[AidMessage] = msg;
  control().postEvent(type,out,category);
}

void MeqServer::reportNodeStatus (Node &node,int oldstat,int newstat)
{
  if( forest.debugLevel() <= 0 )
    return;
  // check what's changed
  int changemask = oldstat^newstat;
  // at verbosity level 1, only report changes to result type
  // at level>1, report changes to anything
  if( changemask&Node::CS_RES_MASK ||
      ( forest.debugLevel()>1 && changemask )  )
  {
    // node status reported within the message ID itself. Message payload is empty
    HIID ev = EvNodeStatus | node.nodeIndex() | newstat;
    if( forest.debugLevel()>1 )
      ev |= node.currentRequestId();
    control().postEvent(ev,ObjRef(),AidDebug);
  }
}

void MeqServer::fillForestStatus  (DMI::Record &rec,int level)
{
  if( !level )
    return;
  if( level>1 )
    rec[AidForest|AidState] = forest.state();
  DMI::Record &fst = rec[AidForest|AidStatus] <<= new DMI::Record;
  fst[AidState] = control().state();
  fst[AidRunning] = executing_;
  fst[AidDebug|AidLevel] = forest.debugLevel();
  if( forest.debugLevel() )
  {
    DMI::List &stack = fst[AidDebug|AidStack] <<= new DMI::List;
    int i=0;
    for( DebugStack::const_iterator iter = debug_stack.begin(); 
         iter != debug_stack.end(); iter++,i++ )
    {
      DMI::Record &entry = stack[i] <<= new DMI::Record;
      entry[AidName] = iter->node->name();
      entry[AidNodeIndex] = iter->node->nodeIndex();
      entry[AidControl|AidStatus] = iter->node->getControlStatus();
      // currently stopped node gets its state too
      if( !i )
        entry[AidState] <<= iter->node->syncState();
    }
  }
}

void MeqServer::processBreakpoint (Node &node,int bpmask,bool global)
{
  // if forest.debugLevel is 0, debugging has been disabled -- ignore the breakpoint
  if( forest.debugLevel() <= 0 )
    return;
  // return immediately if we hit a global breakpoint after a next-node
  // command, and node hasn't changed yet
  if( global && debug_next_node == &node )
    return;
  // suspend input stream on first breakpoint
  if( debug_stack.empty() )
  {
//    input().suspend();
// implement this!!!
  }
  // allocate a new debug frame
  debug_stack.push_front(DebugFrame());
  DebugFrame & frame = debug_stack.front();
  frame.node = &node;
  debug_continue = false;
  // post event indicating we're stopped in the debugger
  DMI::Record::Ref ref;
  DMI::Record &rec = ref <<= new DMI::Record;
  fillForestStatus(rec);
  rec[AidMessage] = makeNodeMessage("stopped at ",node,":" + node.getStrExecState());
  control().postEvent(EvDebugStop,ref);
//  int old_state = control().state();
//  control().setState(AppState_Debug);
//  input().suspend();
  // keep on processing commands until asked to continue
  while( forest.debugLevel() > 0 && running_ && !debug_continue )  // while in a running state
  {
    processCommands();
  }
  // clear debug frame 
  debug_stack.pop_front();
//  if( debug_stack.empty() )
//    input().resume();
//  control().setState(old_state);
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

void MeqServer::mqs_postEvent (const HIID &id,const ObjRef &data)
{
  mqs_->postEvent(id,data);
}

void MeqServer::publishState ()
{
  DMI::Record::Ref rec(DMI::ANONWR);
  rec[AidState] = HIID(state_);
  rec[AidState|AidString] = HIID(state_).toString();
  control().postEvent("App.Notify.State",rec);
}
      
AtomicID MeqServer::setState (AtomicID state)
{
  AtomicID oldstate = state_;
  state_ = state;
  publishState();
  return oldstate;
}


DMI::Record::Ref MeqServer::executeCommand (const HIID &cmd,const ObjRef &argref)
{
  DMI::Record::Ref retval(DMI::ANONWR);
  DMI::Record::Ref args;
  CommandMap::const_iterator iter = command_map.find(cmd);
  FailWhen(iter == command_map.end(),"unknown command "+cmd.toString('.'));
  // provide an args record
  if( argref.valid() )
  {
    FailWhen(!argref->objectType()==TpDMIRecord,"invalid args field");
    args = argref.ref_cast<DMI::Record>();
  }
  else
    args <<= new DMI::Record;
  // execute the command, catching any errors
  (this->*(iter->second))(retval,args);
  return retval;
}

void MeqServer::processCommands ()
{
  // check for any commands from the control agent
  HIID cmdid;
  ObjRef cmd_data;
  // get an event from the control channel
  int state = control().getEvent(cmdid,cmd_data);
  if( state == AppEvent::CLOSED )
  {
    running_ = false;   // closed? break out
    return;
  }
  cdebug(4)<<"state "<<state<<", got event "<<cmdid.toString('.')<<endl;
  if( state != AppEvent::SUCCESS ) // if unsuccessful, break out
    return;
  // is it a MeqCommand?
  if( cmdid.matches(MeqCommandMask) )
  {
    // strip off the Meq command mask -- the -1 is there because 
    // we know a wildcard is the last thing in the mask.
    cmdid = cmdid.subId(MeqCommandMask.length()-1);
    // MeqCommands are expected to have a DMI::Record payload
    if( !cmd_data.valid() || cmd_data->objectType() != TpDMIRecord )
    {
      postError("command "+cmdid.toString('.')+" does not contain a record, ignoring");
      return;
    }
    // extract payload
    DMI::Record &cmddata = cmd_data.as<DMI::Record>();
    cdebug(3)<<"received command "<<cmdid.toString('.')<<endl;
    int request_id = 0;
    bool silent = false;
    DMI::Record::Ref retval;
    bool have_error = true;
//    int oldstate = control().state();
    request_id = cmddata[FRequestId].as<int>(0);
    ObjRef ref = cmddata[FArgs].remove();
    silent     = cmddata[FSilent].as<bool>(false);
    try
    {
      retval = executeCommand(cmdid,ref);
      have_error = false;
    }
    catch( std::exception &exc )
    {
      (retval <<= new DMI::Record)[AidError] = exceptionToObj(exc);
    }
    catch( ... )
    {
      (retval <<= new DMI::Record)[AidError] = "unknown exception while processing command";
    }
    // send back reply if quiet flag has not been raised;
    // errors are always sent back
    if( !silent || have_error )
    {
      HIID reply_id = MeqResultPrefix|cmdid;
      if( request_id )
        reply_id |= request_id;
      control().postEvent(reply_id,retval);
    }
  }
  else // other commands -- ignore for now
  {
    if( cmdid == HIID("Request.State") )
      publishState();
    else if( cmdid == HIID("Halt") )
    {
      running_ = false;
      postMessage("halt command received, exiting");
    }
    else
      postError("ignoring unrecognized event "+cmdid.toString('.'));
  }
}

//##ModelId=3F608106021C
void MeqServer::run ()
{
  // connect debugging callbacks
  forest.setDebuggingCallbacks(mqs_reportNodeStatus,mqs_processBreakpoint);
  forest.setEventCallback(mqs_postEvent);
  // init Python interface
  MeqPython::initMeqPython(this);

  setState(AidIdle);  
  running_ = true;
  while( running_ )
  {
    // process any pending commands
    processCommands();
  }
  
  // clear the forest
  forest.clear();
  // close control channel
  control().close();
  // destroy python interface
  MeqPython::destroyMeqPython();
}

//##ModelId=3F5F195E0156
string MeqServer::sdebug(int detail, const string &prefix, const char *name) const
{
  return "MeqServer";
}

};
