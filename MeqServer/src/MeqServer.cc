//
//% $Id$
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation &
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc.,
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

#include "MeqServer.h"
#include "AID-MeqServer.h"
#include <DMI/AID-DMI.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MEQ/MTPool.h>

#include "config.h"
#ifdef HAVE_MPI
#include <MeqMPI/MeqMPI.h>
#include <MeqMPI/AID-MeqMPI.h>
#endif

#ifndef HAVE_PARMDB
#include <MeqNodes/ParmTableUtils.h>
#endif

#include <DMI/BOIO.h>
#include <DMI/List.h>
#include <MeqServer/MeqPython.h>
#include <MeqServer/Sink.h>
#include <MeqServer/Spigot.h>

#ifdef DARWIN
#include <limits.h>
#define HOST_NAME_MAX _POSIX_HOST_NAME_MAX
#else
#include <linux/unistd.h>
#endif

// TEST_PYTHON_CONVERSION: if defined, will test objects for
// convertability to Python (see below)
// only useful for debugging really
#if LOFAR_DEBUG
  #define TEST_PYTHON_CONVERSION 1
#else
  #undef TEST_PYTHON_CONVERSION
#endif

using Debug::ssprintf;
using namespace AppAgent;

namespace Meq
{

static int dum =  aidRegistry_MeqServer() +
                  aidRegistry_Meq() +
#ifdef HAVE_MPI
                  aidRegistry_MeqMPI() +
#endif
                  aidRegistry_MeqNodes();

const HIID MeqCommandPrefix = AidCommand;
const HIID MeqCommandMask   = AidCommand|AidWildcard;
const HIID MeqResultPrefix  = AidResult;


const HIID DataProcessingError = AidData|AidProcessing|AidError;

InitDebugContext(MeqServer,"MeqServ");

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

  async_commands["Halt"] = &MeqServer::halt;

  async_commands["Get.Forest.State"] = &MeqServer::getForestState;
  async_commands["Set.Forest.State"] = &MeqServer::setForestState;

  sync_commands["Create.Node"] = &MeqServer::createNode;
  #ifdef HAVE_MPI
  sync_commands["Create.Node.Batch"] = &MeqServer::createNodeBatch_Mpi;
  #else
  sync_commands["Create.Node.Batch"] = &MeqServer::createNodeBatch;
  #endif

  sync_commands["Delete.Node"] = &MeqServer::deleteNode;
  async_commands["Set.Cwd"] = &MeqServer::setCurrentDir;
  async_commands["Set.Session.Name"] = &MeqServer::setSessionName;
  #ifdef HAVE_MPI
  async_commands["Get.Node.List"] = &MeqServer::getNodeList_Mpi;
  #else
  async_commands["Get.Node.List"] = &MeqServer::getNodeList;
  #endif
  async_commands["Get.Forest.Status"] = &MeqServer::getForestStatus;
  async_commands["Get.NodeIndex"] = &MeqServer::getNodeIndex;

  async_commands["Disable.Publish.Results"] = &MeqServer::disablePublishResults;
//  sync_commands["Save.Forest"] = &MeqServer::saveForest;
//  sync_commands["Load.Forest"] = &MeqServer::loadForest;
  sync_commands["Clear.Forest"] = &MeqServer::clearForest;

  // per-node commands
  async_commands["Node.Get.State"] = &MeqServer::nodeGetState;
  sync_commands["Node.Execute"] = &MeqServer::nodeExecute;
  // commands with a 0 pointer are automatically mapped to
  // Node::processCommand() with the Node prefix truncated.
  // A null map entry is used to mark sync-only commands.
//  async_commands["Node.Set.State"] = 0; // &MeqServer::nodeSetState;
  sync_commands["Node.Clear.Cache"] = 0; // &MeqServer::nodeClearCache;
//  async_commands["Node.Publish.Results"] = 0; // &MeqServer::publishResults;
//  async_commands["Node.Set.Breakpoint"] = 0; // &MeqServer::nodeSetBreakpoint;
//  async_commands["Node.Clear.Breakpoint"] = 0; // &MeqServer::nodeClearBreakpoint;
  async_commands["Set.Forest.Breakpoint"] = &MeqServer::setForestBreakpoint;
  async_commands["Clear.Forest.Breakpoint"] = &MeqServer::clearForestBreakpoint;

  async_commands["Execute.Abort"] = &MeqServer::executeAbort;
  async_commands["Debug.Set.Level"] = &MeqServer::debugSetLevel;
  async_commands["Debug.Interrupt"] = &MeqServer::debugInterrupt;
  async_commands["Debug.Single.Step"] = &MeqServer::debugSingleStep;
  async_commands["Debug.Next.Node"] = &MeqServer::debugNextNode;
  async_commands["Debug.Until.Node"] = &MeqServer::debugUntilNode;
  async_commands["Debug.Continue"] = &MeqServer::debugContinue;

  debug_next_node = 0;
  running_ = executing_ = clear_stop_flag_ = false;
  forest_breakpoint_ = 0;
}

MeqServer::~MeqServer ()
{
}

static string makeNodeLabel (const string &name,int)
{
  return ssprintf("node '%s'",name.c_str());
}

static string makeNodeLabel (const Meq::NodeFace &node)
{
  return ssprintf("node '%s'",node.name().c_str());
}

static string makeNodeMessage (const Meq::NodeFace &node,const string &msg)
{
  return makeNodeLabel(node) + ": " + msg;
}

static string makeNodeMessage (const string &msg1,const Meq::NodeFace &node,const string &msg2 = string())
{
  string str = msg1 + " " + makeNodeLabel(node);
  if( !msg2.empty() )
    str += " " + msg2;
  return str;
}


//##ModelId=3F6196800325
NodeFace & MeqServer::resolveNode (bool &getstate,const DMI::Record &rec)
{
  int nodeindex = rec[AidNodeIndex].as<int>(-1);
  string name = rec[AidName].as<string>("");
  getstate = rec[FGetState].as<bool>(false);
  if( nodeindex>0 )
  {
    NodeFace &node = forest.get(nodeindex);
    FailWhen( name.length() && node.name() != name,"node specified by index is "+
        node.name()+", which does not match specified name "+name);
    return node;
  }
  FailWhen( !name.length(),"either nodeindex or name must be specified");
  cdebug(3)<<"looking up node name "<<name<<endl;
  return forest.findNode(name);
}


void MeqServer::halt (DMI::Record::Ref &out,DMI::Record::Ref &)
{
  cdebug(1)<<"halting MeqServer"<<endl;
  running_ = false;
  out()[AidMessage] = "halting the meqserver";
  forest.closeLog();
}

void MeqServer::setForestState (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  cdebug(3)<<"setForestState()"<<endl;
  // if running under MPI, post state to all subservers
  #ifdef HAVE_MPI
  for( int proc=1; proc<MeqMPI::self->comm_size(); proc++ )
  {
    ObjRef objref = in;
    MeqMPI::self->postCommand(MeqMPI::TAG_SET_FOREST_STATE,proc,objref);
  }
  #endif
  DMI::Record::Ref ref = in[AidState].ref();
  forest.setState(ref);
  fillForestStatus(out(),in[FGetForestStatus].as<int>(2));
}

void MeqServer::getForestState (DMI::Record::Ref &out,DMI::Record::Ref &)
{
  fillForestStatus(out(),2);
}

// safe POSIX-complicant method to change working directory
std::string getCwd ()
{
  char *pbuf = 0;
  std::vector<char> buf;
  while( !pbuf )
  {
    buf.resize(buf.size()+1024);
    pbuf = getcwd(&(buf[0]),buf.size());
    if( !pbuf && errno != ERANGE )
      return "";
  }
  return std::string(pbuf);
}

void MeqServer::setCurrentDir (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  cdebug(3)<<"setCurrentDir()"<<endl;
  string dirname = in[AidCwd].as<string>("");
  if( !dirname.empty() )
  {
    string old_wd = getCwd();
    // change WD
    if( chdir(dirname.c_str())<0 )
    {
      out()[AidError] = string("error changing directory to ")+dirname+": "+strerror(errno);
    }
    else
    {
      // compare to cwd, to see if anything has changed (do it the roundabout way to handle symlinks, etc.)
      string new_wd = getCwd();
      if( new_wd.compare(old_wd) )
        out()[AidMessage] = "kernel working directory is now "+new_wd;
    }
  }
  fillForestStatus(out(),in[FGetForestStatus].as<int>(2));
}

void MeqServer::setSessionName (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  cdebug(3)<<"setSessionName()"<<endl;
  session_name_ = in[AidSession|AidName].as<string>("");
  out()[AidMessage] = "kernel session renamed to '"+session_name_+"'";
  fillForestStatus(out(),in[FGetForestStatus].as<int>(2));
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
  NodeFace & node = forest.create(nodeindex,initrec);
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
  setState(AidConstructing);
  script_name_ = in[AidScript|AidName].as<string>("");
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
      forest.create(nodeindex,recref);
    }
    catch( std::exception &exc )
    {
      postError(exc);
    }
  }
  // if no errors, initialize
  if( !forest.numInitErrors() )
  {
    postMessage("initializing nodes, please wait");
    forest.initAll();
  }
  // form a response message
  if( forest.numInitErrors() )
    out[AidError] = ssprintf("%d nodes failed to initialize properly",
                      forest.numInitErrors());
  else
    out[AidMessage] = ssprintf("successfully created %d nodes",nn);
  out[FForestChanged] = incrementForestSerial();
  fillForestStatus(out(),in[FGetForestStatus].as<int>(1));
}

#ifdef HAVE_MPI
// MPI version of batch-creation function
void MeqServer::createNodeBatch_Mpi (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  setState(AidConstructing);
  script_name_ = in[AidScript|AidName].as<string>("");
  DMI::Container &batch = in[AidBatch].as_wr<DMI::Container>();
  int nn = batch.size();
  postMessage(ssprintf("creating %d nodes, please wait",nn));
  cdebug(2)<<"splitting up nodes among MPI processors"<<endl;
  // create lists of node specifications per processor
  int nproc = MeqMPI::self->comm_size();
  DMI::List::Ref nodelist[nproc];
  for( int i=0; i<nproc; i++ )
    nodelist[i] <<= new DMI::List;
  // now, go through list of node specifications, and distribute it into per-processor lists
  for( int i=0; i<nn; i++ )
  {
    ObjRef ref;
    batch[i].detach(&ref);
    DMI::Record::Ref recref(ref);
    ref.detach();
    // get processor index from node state
    int proc = recref[AidProc].as<int>(0);
    if( proc < 0 || proc >= nproc )
    {
      postError(ssprintf("invalid proc=%d specification for node '%s'",proc,recref[AidName].as<string>("").c_str()));
      continue;
    }
    cdebug(4)<<"node "<<recref[AidName].as<string>()<<": processor "<<proc<<endl;
    // add nodespec to list associated with this processor
    nodelist[proc]().addBack(recref);
    // make a nodespec for an MPIProxy node representing this node
    DMI::Record::Ref spec;
    spec <<= new DMI::Record;
    spec[FClass] = "MeqMPIProxy";
    spec[FName] = recref[FName].as<string>();
    spec[FNodeIndex] = recref[FNodeIndex].as<int>(-1);
    spec[AidRemote|AidProc] = proc;
//    if( recref[FChildren].exists() )
//      spec[FChildren] = recref[FChildren].ref();
//    if( recref[FStepChildren].exists() )
//      spec[FStepChildren] = recref[FStepChildren].ref();
    // add this spec to back of all other remote nodelists
    for( int i=0; i<nproc; i++ )
      if( i != proc )
        nodelist[i]().addBack(spec);
  }
  // send remote nodelists off for processing
  cdebug(2)<<"sending off lists to remote processors"<<endl;
  MeqMPI::ReplyEndpoint replies[nproc];
  for( int i=1; i<nproc; i++ )
  {
    cdebug(2)<<"proc "<<i<<": "<<nodelist[i]->size()<<" nodes"<<endl;
    ObjRef ref(nodelist[i]);
    MeqMPI::self->postCommand(MeqMPI::TAG_CREATE_NODES,i,replies[i],ref);
  }
  // create local nodes
  DMI::List &local_list = nodelist[0]();
  DMI::List::iterator iter = local_list.begin();
  for( iter = local_list.begin(); iter != local_list.end(); iter++ )
  {
    DMI::Record::Ref recref(*iter);
    iter->detach();
    try
    {
      int nodeindex;
      forest.create(nodeindex,recref);
    }
    catch( std::exception &exc )
    {
      postError(exc);
    }
  }
  forest.initAll();
  cdebug(2)<<"waiting for completion replies from remotes"<<endl;
  ObjRef ref;
  for( int i=1; i<nproc; i++ )
    replies[i].await(ref);
  // form a response message
  out[AidMessage] = ssprintf("created %d nodes",nn);
  out[FForestChanged] = incrementForestSerial();
  fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
}
#endif

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
  NodeFace &node = forest.get(nodeindex);
  string name = node.name();
  cdebug(2)<<"deleting node "<<name<<"("<<nodeindex<<")\n";
  // remove from forest
  forest.remove(nodeindex);
  // do not use node below: ref no longer valid
  out[AidMessage] = "deleted " + makeNodeLabel(name,nodeindex);
  // fill optional response fields
  fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
  out[FForestChanged] = incrementForestSerial();
}

void MeqServer::nodeGetState (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  bool getstate;
  NodeFace & node = resolveNode(getstate,*in);
  cdebug(3)<<"getState for node "<<node.name()<<" ";
  cdebug(4)<<in->sdebug(3);
  cdebug(3)<<endl;
  node.getSyncState(out);
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
  NodeFace & node = resolveNode(getstate,*rec);
  cdebug(3)<<"setState for node "<<node.name()<<endl;
  DMI::Record::Ref ref = rec[AidState].ref();
  node.setState(ref);
  if( getstate )
    out[FNodeState] <<= node.syncState();
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

#ifdef HAVE_MPI
void MeqServer::getNodeList_Mpi (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  cdebug(2)<<"getNodeList: building list"<<endl;
  out <<= new DMI::Record;
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
    // dispatch requests to subservers
    cdebug(2)<<"requesting nodelists from remote processors"<<endl;
    int nproc = MeqMPI::self->comm_size();
    MeqMPI::ReplyEndpoint replies[nproc];
    for( int i=1; i<nproc; i++ )
    {
      MeqMPI::HdrGetNodeList hdr = { content,&replies[i] };
      MeqMPI::self->postCommand(MeqMPI::TAG_GET_NODE_LIST,i,hdr);
    }
    // get local list
    DMI::Vec *proclist;
    out[AidProc] <<= proclist = new DMI::Vec(TpDMIRecord,nproc);
    ObjRef ref;
    ref <<= new DMI::Record;
    int count = MeqMPI::getNodeList(ref.as<DMI::Record>(),content,forest);
    cdebug(2)<<"getNodeList: local list has "<<count<<" nodes"<<endl;
    (*proclist)[0] = ref;
    // now wait for replies from all remotes
    for( int i=1; i<nproc; i++ )
    {
      int num = replies[i].await(ref);
      (*proclist)[i] = ref;
      cdebug(2)<<"getNodeList: proc "<<i<<" returns "<<num<<" nodes\n";
    }
    out[FForestSerial] = forest_serial;
  }
  fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
}
#endif

void MeqServer::executeAbort (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  forest.raiseAbortFlag();
  if( state() == AidExecuting )
    out()[AidMessage] = "aborting tree execution";
  if( forest.isStopFlagRaised() )
  {
    forest.clearBreakpoint(Node::CS_ALL&~forest_breakpoint_,false);
    forest.clearBreakpoint(Node::CS_ALL,true);
    debug_next_node = debug_bp_node = 0;
    clear_stop_flag_ = true;
  }
  fillForestStatus(out(),in[FGetForestStatus].as<int>(1));
}

//##ModelId=400E5B6C015E
void MeqServer::nodeExecute (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  setState(AidExecuting);
  try
  {
    // close all parm tables to free up memory
#ifndef HAVE_PARMDB
    ParmTableUtils::closeTables();
#endif
    forest.clearAbortFlag();
    DMI::Record::Ref rec = in;
    bool getstate;
    NodeFace & node = resolveNode(getstate,*rec);
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
    int flags = node.execute(resref,req,0);
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
    executing_ = false;
    #ifndef HAVE_PARMDB
    ParmTableUtils::flushTables();
    #endif
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
    else if( flags&Node::RES_ABORT )
      out[AidMessage] = makeNodeMessage(node,ssprintf("execute() aborted (return code 0x%x)",flags));
    else
      out[AidMessage] = makeNodeMessage(node,ssprintf("execute() successful (return code 0x%x)",flags));
    if( resref.valid() )
      out[AidResult] <<= resref;
    if( getstate )
      out[FNodeState] <<= node.syncState();
    fillForestStatus(out(),in[FGetForestStatus].as<int>(1));
    forest.closeLog();
  }
  catch( ... )
  {
    executing_ = false;
    throw;
  }
  executing_ = false;
}


// //##ModelId=400E5B6C0247
// void MeqServer::saveForest (DMI::Record::Ref &out,DMI::Record::Ref &in)
// {
//   setState(AidUpdating);
//   string filename = (*in)[FFileName].as<string>();
//   cdebug(1)<<"saving forest to file "<<filename<<endl;
//   postMessage(ssprintf("saving forest to file %s, please wait",filename.c_str()));
//   BOIO boio(filename,BOIO::WRITE);
//   int nsaved = 0;
//
//   // write header record
//   DMI::Record header;
//   header["Forest.Header.Version"] = 1;
//   boio << header;
//   // write forest state
//   boio << *(forest.state());
//   // write all nodes
//   for( int i=1; i<=forest.maxNodeIndex(); i++ )
//     if( forest.valid(i) )
//     {
//       NodeFace &node = forest.get(i);
//       // if node is unresolved, fail and delete file
//       if( !node.isInitialized() )
//       {
//         boio.close();
//         unlink(filename.c_str());
//         Throw("can't save forest: uninitialized node "+node.name());
//       }
//       cdebug(3)<<"saving node "<<node.name()<<endl;
//       DMI::Record::Ref saverec;
//       node.saveState(saverec);
//       boio << *saverec;
//       nsaved++;
//     }
//   cdebug(1)<<"saved "<<nsaved<<" nodes to file "<<filename<<endl;
//   out[AidMessage] = ssprintf("saved %d nodes to file %s",
//       nsaved,filename.c_str());
//   fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
// }
//
// //##ModelId=400E5B6C02B3
// void MeqServer::loadForest (DMI::Record::Ref &out,DMI::Record::Ref &in)
// {
//   setState(AidUpdating);
//   string filename = (*in)[FFileName].as<string>();
//   cdebug(1)<<"loading forest from file "<<filename<<endl;
//   postMessage(ssprintf("loading forest from file %s, please wait",filename.c_str()));
//   forest.clear();
//   int nloaded = 0;
//   DMI::Record::Ref ref;
//   std::string fmessage;
//   // open file
//   BOIO boio(filename,BOIO::READ);
//   // get header record out
//   if( ! (boio >> ref) )
//   {
//     Throw("no records in file");
//   }
//   // is this a version record?
//   int version = ref["Forest.Header.Version"].as<int>(-1);
//   if( version >=1 )
//   {
//     // version 1+: forest state comes first
//     if( !(boio >> ref) )
//     {
//       Throw("no forest state in file");
//     }
//     forest.setState(ref,true);
//     // then get next node record for loop below
//     if( !(boio >> ref) )
//       ref.detach();
//     fmessage = "loaded %d nodes and forest state from file %s";
//   }
//   else
//   {
//     // else version 0: nothing but node records in here, so fall through
//     fmessage = "loaded %d nodes from old-style file %s";
//   }
//   // ok, at this point we expect a bunch of node records
//   do
//   {
//     int nodeindex;
//     // create the node
//     Node & node = forest.create(nodeindex,ref,true);
//     cdebug(3)<<"loaded node "<<node.name()<<endl;
//     nloaded++;
//   }
//   while( boio >> ref );
//   cdebug(2)<<"loaded "<<nloaded<<" nodes, setting child links"<<endl;
//   for( int i=1; i<=forest.maxNodeIndex(); i++ )
//     if( forest.valid(i) )
//     {
//       Node &node = forest.get(i);
//       cdebug(3)<<"setting children for node "<<node.name()<<endl;
//       node.reinit();
//     }
//   out[AidMessage] = ssprintf(fmessage.c_str(),nloaded,filename.c_str());
//   fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
//   out[FForestChanged] = incrementForestSerial();
// }

//##ModelId=400E5B6C0324
void MeqServer::clearForest (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  setState(AidUpdating);
  cdebug(1)<<"clearing forest: deleting all nodes"<<endl;
  forest.clear();
  MeqPython::forceModuleReload();
// ****
// **** added this to relinquish parm tables --- really ought to go away
#ifndef HAVE_PARMDB
  ParmTableUtils::closeTables();
#endif
// ****
  out[AidMessage] = "all nodes deleted";
  fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
  out[FForestChanged] = incrementForestSerial();
}

void MeqServer::disablePublishResults (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  cdebug(2)<<"disablePublishResults: disabling for all nodes"<<endl;
  for( int i=0; i<=forest.maxNodeIndex(); i++ )
    if( forest.valid(i) )
      forest.get(i).setPublishingLevel(0);
  out[AidMessage] = "snapshots disabled on all nodes";
  out[FDisabledAllPublishing] = true;
  fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
}

void MeqServer::setForestBreakpoint (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  DMI::Record::Ref rec = in;
  int bpmask = rec[FBreakpoint].as<int>(0);
  cdebug(2)<<"setForestBreakpoint: mask "<<bpmask<<endl;
  forest.setBreakpoint(bpmask);
  forest_breakpoint_ |= bpmask;
  out[AidMessage] = ssprintf("set global breakpoint %X; new bp mask is %X",
                             bpmask,forest_breakpoint_);

  fillForestStatus(out(),in[FGetForestStatus].as<int>(0));
}

void MeqServer::clearForestBreakpoint (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  DMI::Record::Ref rec = in;
  int bpmask = rec[FBreakpoint].as<int>(Node::BP_ALL);
  cdebug(2)<<"clearForestBreakpoint: mask "<<bpmask<<endl;
  forest.clearBreakpoint(bpmask);
  forest_breakpoint_ &= ~bpmask;
  out[AidMessage] = ssprintf("clearing global breakpoint %X; new bp mask is %X",
                             bpmask,forest_breakpoint_);
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


void MeqServer::debugInterrupt (DMI::Record::Ref &,DMI::Record::Ref &)
{
  if( !forest.isStopFlagRaised() )
    // set a global one-shot breakpoint on everything
    forest.setBreakpoint(Node::CS_ALL,true);
}

void MeqServer::debugContinue (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  if( forest.isStopFlagRaised() )
  {
    forest.clearBreakpoint(Node::CS_ALL&~forest_breakpoint_,false);
    forest.clearBreakpoint(Node::CS_ALL,true);
    debug_next_node = debug_bp_node = 0;
    clear_stop_flag_ = true;
  }
  fillForestStatus(out(),in[FGetForestStatus].as<int>(1));
}

void MeqServer::debugSingleStep (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  if( forest.isStopFlagRaised() )
  {
    // set a global one-shot breakpoint on everything
    forest.setBreakpoint(Node::CS_ALL,true);
    debug_next_node = debug_bp_node = 0;
    clear_stop_flag_ = true;
  }
  fillForestStatus(out(),in[FGetForestStatus].as<int>(1));
}

void MeqServer::debugNextNode (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  if( forest.isStopFlagRaised() )
  {
    // set a one-shot breakpoint on everything
    forest.setBreakpoint(Node::CS_ALL);
    debug_next_node = debug_bp_node;
    clear_stop_flag_ = true;
  }
  fillForestStatus(out(),in[FGetForestStatus].as<int>(1));
}

void MeqServer::debugUntilNode (DMI::Record::Ref &out,DMI::Record::Ref &in)
{
  bool getstate;
  NodeFace & node = resolveNode(getstate,*in);
  // set one-shot breakpoint on anything in this node
  node.setBreakpoint(Node::CS_ALL,true);
  if( forest.isStopFlagRaised() )
  {
    // clear all global breakpoints and continue
    forest.clearBreakpoint(Node::CS_ALL&~forest_breakpoint_,false);
    forest.clearBreakpoint(Node::CS_ALL,true);
    debug_next_node = debug_bp_node = 0;
    clear_stop_flag_ = true;
  }
  fillForestStatus(out(),in[FGetForestStatus].as<int>(1));
}

int MeqServer::receiveEvent (const EventIdentifier &evid,const ObjRef &evdata,void *)
{
  Thread::Mutex::Lock lock(control_mutex_);
  cdebug(4)<<"received event "<<evid.id()<<endl;
#if 0 // #ifdef TEST_PYTHON_CONVERSION
  MeqPython::testConversion(*evdata);
#endif
  control().postEvent(evid.id(),evdata);
  return 1;
}

void MeqServer::postEvent (const HIID &type,const ObjRef &data)
{
  Thread::Mutex::Lock lock(control_mutex_);
  control().postEvent(type,data);
}

void MeqServer::postEvent (const HIID &type,const DMI::Record::Ref &data)
{
  Thread::Mutex::Lock lock(control_mutex_);
  control().postEvent(type,data);
}

void MeqServer::postError (const std::exception &exc,AtomicID category)
{
  Thread::Mutex::Lock lock(control_mutex_);
  DMI::Record::Ref out(new DMI::Record);
  out[AidError] = exceptionToObj(exc);
  control().postEvent(AidError,out,category);
}

void MeqServer::postMessage (const std::string &msg,const HIID &type,AtomicID category)
{
  Thread::Mutex::Lock lock(control_mutex_);
  DMI::Record::Ref out(new DMI::Record);
  if( type == HIID(AidError) )
    out[AidError] = msg;
  else
    out[AidMessage] = msg;
  control().postEvent(type,out,category);
}

void MeqServer::reportNodeStatus (Node &node,int oldstat,int newstat)
{
  // node status reported within the message ID itself. Message payload is empty
  HIID ev = EvNodeStatus | node.nodeIndex() | newstat;
  ev |= node.currentRequestId();
  control().postEvent(ev,ObjRef(),AidDebug);
}

void MeqServer::fillAppState (DMI::Record &rec)
{
  Thread::Mutex::Lock lock(exec_cond_);
  int sz = exec_queue_.size();
  lock.release();
  HIID st = state();
  if( forest.isStopFlagRaised() && !clear_stop_flag_ )
    st |= AidDebug;
  rec[AidApp|AidState] = st;
  string str = st.toString('.');
  if( sz>1 )
    str += ssprintf(" (%d)",sz-1);
  rec[AidApp|AidState|AidString] = str;
  rec[AidApp|AidExec|AidQueue|AidSize] = sz;
  char hostname[HOST_NAME_MAX];
  gethostname(hostname,sizeof(hostname));
  hostname[sizeof(hostname)-1] = 0;
  rec[AidApp|AidHost] = hostname;
  rec[AidForest|AidSize] = forest.maxNodeIndex();
  rec[AidSession|AidName] = session_name_;
  rec[AidScript|AidName] = script_name_;
  // get cwd
  static char buf[16384];
  if( getcwd(buf,sizeof(buf)) )
    rec[AidCwd] = buf;
  else
    rec[AidCwd] = '.';
}

void MeqServer::fillForestStatus  (DMI::Record &rec,int level)
{
  if( !level )
    return;
  if( level>1 )
    rec[AidForest|AidState] = forest.state();
  DMI::Record &fst = rec[AidForest|AidStatus] <<= new DMI::Record;
  fillAppState(rec);
  // get other stuff
  #ifdef HAVE_MPI
  fst[AidMPI|AidNum|AidProc] = MeqMPI::self->comm_size();
  #else
  fst[AidMPI|AidNum|AidProc] = 0;
  #endif
  fst[AidNum|AidInit|AidErrors] = forest.numInitErrors();
  fst[AidBreakpoint] = forest_breakpoint_;
  fst[AidExecuting] = executing_;
  fst[AidDebug|AidLevel] = forest.debugLevel();
  fst[AidStopped] = forest.isStopFlagRaised() && !clear_stop_flag_;
}

void MeqServer::processBreakpoint (Node &node,int bpmask,bool global)
{
  // if we're doing a global breakpoint on a step-to-next-node,
  // return if we're still in the previous node
  if( global && debug_next_node == &node )
  {
    forest.clearStopFlag();
    return;
  }
  debug_next_node = 0;
  // post event indicating we're stopped in the debugger
  DMI::Record::Ref ref;
  DMI::Record &rec = ref <<= new DMI::Record;
  fillForestStatus(rec);
  rec[AidMessage] = makeNodeMessage("stopped at ",node,":" + node.getStrExecState());
  control().postEvent(EvDebugStop,ref);
  debug_bp_node = &node;
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
  fillAppState(rec());
  postEvent("App.Notify.State",rec);
}

AtomicID MeqServer::setState (AtomicID state,bool quiet)
{
  AtomicID oldstate = state_;
  state_ = state;
  if( !quiet && oldstate != state )
    publishState();
  return oldstate;
}

bool MeqServer::execNodeCommand (DMI::Record::Ref &out,ExecQueueEntry &qe)
{
  bool verbose = false;
  // verify inputs
  Assert(qe.command[0] = AidNode);
  HIID command = qe.command.subId(1);
  // use argument record to resolve to a Node object, throw exception on failure
  bool getstate;
  int get_forest_status = (*qe.args)[FGetForestStatus].as<int>(0);
  NodeFace &node = resolveNode(getstate,*qe.args);
  // add node name to output event record
  out[AidNode] = node.name();
  // pass command to node. Exceptions will be caught by our caller's handler
  Result::Ref resref;
  int retcode = node.processCommand(resref,command,qe.args,RequestId(),qe.silent?0:1); // verbosity=1 if not silent
  // generate "unknown command" message if RES_OK not set in return value
  if( !(retcode&Node::RES_OK) )
  {
    out[AidError] = "node '"+node.name()+"': unrecognized command '"+command.toString('.')+"'";
    verbose = true;
  }
  // if node returns a valid Result, add to output record
  if( resref.valid() )
    out[AidResult] = resref;
  // if state or forest status was requested, add to output record
  if( getstate )
    out[FNodeState] <<= node.syncState();
  fillForestStatus(out(),get_forest_status);
  return verbose;
}

DMI::Record::Ref MeqServer::execCommandEntry (ExecQueueEntry &qe,bool savestate,bool post_results)
{
  AtomicID oldstate = state();    // save app state prior to command
  DMI::Record::Ref out(DMI::ANONWR);
  // has_reply will be true if the command produces a result that needs
  // to be posted back. Note that if post_results=false, then this will be
  // ignored anyway, since in this mode we return the result or throw an error.
  bool has_reply = !qe.silent;
  Result::Ref resref;
  try
  {
    // qe.proc!=0: call specified command handler
    if( qe.proc )
      (this->*(qe.proc))(out,qe.args);\
    // else this is a Node.* command. Call helper function and set the
    // has_reply flag if it returns true (which usually means an error)
    else
      has_reply |= execNodeCommand(out,qe);
  }
  catch( std::exception &exc )
  {
    if( !post_results )
    {
      if( savestate )
        setState(oldstate);
      throw;
    }
    // post error event
    out[AidError] = exceptionToObj(exc);
    has_reply = true;
  }
  catch( ... )
  {
    if( !post_results )
    {
      if( savestate )
        setState(oldstate);
      throw;
    }
    out[AidError] = "unknown exception while processing command "+qe.command.toString('.');
    has_reply = true;
  }
  // if we need to clear the stop flag at end of command (i.e. when releasing
  // from breakpoint), lock the condition variable to keep the execution threads
  // stopped until we have posted the command result. Otherwise the exec
  // thread may reache the next breakpoint and post an event BEFORE we have
  // posted our reply below, which confuses the browser no end.
  Thread::Mutex::Lock lock;
  if( clear_stop_flag_ )
  {
    lock.lock(forest.stopFlagCond());
    forest.clearStopFlag();
    clear_stop_flag_ = false;
  }
  // post reply if asked to, including state
  if( post_results && has_reply )
  {
    if( savestate && state() != oldstate )
    {
      setState(oldstate,true);  // quiet=true, no publish, since we post event anyway
      fillAppState(out());
    }
    control().postEvent(qe.reply,out);
    out.detach();
    return out;
  }
  else if( savestate ) // no reply, so simply reset state if needed
    setState(oldstate);

  return out;
}

DMI::Record::Ref MeqServer::executeCommand (const HIID &cmdid,DMI::Record::Ref &cmd_data,bool post_results,bool wait_for_async_queue)
{
  DMI::Record::Ref result;
  // MeqCommands are expected to have a DMI::Record payload
  if( !cmd_data.valid() || cmd_data->objectType() != TpDMIRecord )
  {
    if( post_results )
      postError("command "+cmdid.toString('.')+" does not contain a record, ignoring");
    else
      Throw("command "+cmdid.toString('.')+" does not contain a record, ignoring");
    return result;
  }
  // extract payload and fill in an ExecQueueEntry
  DMI::Record &cmddata = cmd_data.as<DMI::Record>();
  cdebug(3)<<"received command "<<cmdid.toString('.')<<endl;
  ExecQueueEntry qe;
  qe.command = cmdid;
  qe.reply = MeqResultPrefix|cmdid;
  int command_index = cmddata[FCommandIndex].as<int>(0);
  if( command_index )
    qe.reply |= command_index;
  qe.args    = cmddata[FArgs].remove();
  if( !qe.args.valid() )
    qe.args <<= new DMI::Record;
  qe.silent  = !post_results || qe.args[FSilent].as<bool>(false);
  // a command may be explicitly specified as sync (but not vice versa --
  // sync=false is always overridden if command is in the sync map)
  bool sync = qe.args[FSync].as<bool>(false);
  // find command in async map first, then sync map
  qe.proc = 0;
  CommandMap::const_iterator iter = async_commands.find(qe.command);
  if( iter != async_commands.end() )
    qe.proc = iter->second;
  else // not found in async map, try the sync map
  {
    iter = sync_commands.find(qe.command);
    if( iter != sync_commands.end() )
    {
      qe.proc = iter->second;
      sync = true; // it's a sync-only command, so force sync mode
    }
    // else is it a Node.* command?
    else if( qe.command[0] == AidNode )
      qe.proc = 0;
    // else not found at all
    else
    {
      if( post_results )
      {
        DMI::Record::Ref out(DMI::ANONWR);
        out[AidError] = "unknown command "+cmdid.toString('.');
        control().postEvent(qe.reply,out);
        return result;
      }
      else
        Throw("unknown command "+cmdid.toString('.'));
    }
  }
  // qe.proc may now be 0 to indicate a Node.* command

  // directly execute command if found in map
  if( !sync )
  {
    if( wait_for_async_queue )
    {
      // for sync commands, make sure the async queue is completed first
      Thread::Mutex::Lock lock(exec_cond_);
      while( !exec_queue_.empty() )
        exec_cond_.wait();
    }
    result = execCommandEntry(qe,false,post_results); // false=do not save/restore state
  }
  // else push onto sync queue for exec thread to handle
  else
  {
    Thread::Mutex::Lock lock(exec_cond_);
    int sz = exec_queue_.size();
    exec_queue_.push_back(qe);
    exec_cond_.broadcast();
    if( sz && post_results )
      postMessage(ssprintf("queueing %s command (%d)",cmdid.toString('.').c_str(),sz));
    lock.release();
    // return empty result
    result <<= new DMI::Record;
  }
  return result;
}

//##ModelId=3F608106021C
void MeqServer::run ()
{
  running_ = true;
  // connect debugging callbacks
  forest.setDebuggingCallbacks(mqs_reportNodeStatus,mqs_processBreakpoint);
  forest.setEventCallback(mqs_postEvent);
  // init Python interface
  MeqPython::initMeqPython(this);
  // start node exec thread
  exec_thread_ = Thread::create(startExecutionThread,this);

  setState(AidIdle);
  while( running_ )
  {
    // get an event from the control channel
    HIID cmdid;
    ObjRef cmd_data;
    HIID event_source;
    int state = control().getEvent(cmdid,cmd_data,event_source);
    if( state == AppEvent::CLOSED )
    {
      running_ = false;   // closed? break out
      break;
    }
    cdebug(4)<<"state "<<state<<", got event "<<cmdid.toString('.')<<endl;
    if( state != AppEvent::SUCCESS ) // if unsuccessful, try again
      continue;
    // regular commands go to the generic interface
    if( cmdid.matches(MeqCommandMask) )
    {
      // strip off the Meq command mask -- the -1 is there because
      // we know a wildcard is the last thing in the mask.
      cmdid = cmdid.subId(MeqCommandMask.length()-1);
      // all MeqCommands are expected to have a DMI::Record payload
      if( !cmd_data.valid() || cmd_data->objectType() != TpDMIRecord )
        postError("command "+cmdid.toString('.')+" does not contain a record, ignoring");
      else
      {
        DMI::Record::Ref cmdrec = cmd_data;
        executeCommand(cmdid,cmdrec,true); // true=post results to output
      }
    }
    // else process some explicit commands
    else if( cmdid == HIID("Request.State") )
      publishState();
    else if( cmdid == HIID("Halt") )
    {
      Thread::Mutex::Lock lock(exec_cond_);
      bool busy = !exec_queue_.empty();
      running_ = false;
      exec_cond_.broadcast();
      lock.release();
      if( busy )
        postMessage("halt command received, exiting once current command finishes");
      else
        postMessage("halt command received, exiting");
    }
    else
      postError("unknown command "+cmdid.toString('.'));
  }
  // signal exec thread to exit (running_ = false)
  Thread::Mutex::Lock lock(exec_cond_);
  exec_cond_.signal();
  lock.release();
  exec_thread_.join();

  // clear the forest
  forest.clear();
  // close any parm tables
#ifndef HAVE_PARMDB
  ParmTableUtils::closeTables();
#endif
  // close control channel
  control().close();
  // destroy python interface
  MeqPython::destroyMeqPython();
}


void * MeqServer::runExecutionThread ()
{
  Thread::Mutex::Lock lock(exec_cond_);
  if( MTPool::enabled() )
    MTPool::brigade().join(MTPool::BUSY,0);
  while( true )
  {
    while( running_ && exec_queue_.empty() )
    {
      if( MTPool::enabled() )
        MTPool::Brigade::markThreadAsBlocked("main");
      exec_cond_.wait();
      if( MTPool::enabled() )
        MTPool::Brigade::markThreadAsUnblocked("main",false);  // can_stop=false
    }
    // exit if no longer running
    if( !running_ )
      return 0;
    // else get request from queue and execute it
    ExecQueueEntry qe = exec_queue_.front();
    lock.release();
    execCommandEntry(qe,true,true); // 1st true: saves/restores state, 2nd true: post reply with results
    publishState();
    // relock queue and remove front entry (unless it's been flushed for us...)
    lock.relock(exec_cond_);
    if( !exec_queue_.empty() )
      exec_queue_.pop_front();
    if( exec_queue_.empty() )
      exec_cond_.broadcast();
    // go back to top for next queue entry
  }
  return 0;
}

void * MeqServer::startExecutionThread (void *mqs)
{
  return static_cast<MeqServer*>(mqs)->runExecutionThread();
}

//##ModelId=3F5F195E0156
string MeqServer::sdebug(int detail, const string &prefix, const char *name) const
{
  return "MeqServer";
}

};


