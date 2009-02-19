//#  Forest.cc: MeqForest class
//#
//#  Copyright (C) 2002-2007
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  and The MeqTree Foundation
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$

#include "Forest.h"
#include "MeqVocabulary.h"
#include <DMI/DynamicTypeManager.h>
#include <DMI/List.h>
#include <DMI/Timestamp.h>

// pull in registry
static int dum = aidRegistry_Meq();

namespace Meq
{

InitDebugContext(Forest,"MeqForest");

// forest state fields
const HIID FAxisMap = AidAxis|AidMap;
const HIID FAxisList = AidAxis|AidList;
const HIID FNumInitErrors = AidNum|AidInit|AidErrors;
const HIID FDebugLevel = AidDebug|AidLevel;
const HIID FKnownSymdeps = AidKnown|AidSymdeps;
const HIID FSymdeps = AidSymdeps;
const HIID FProfilingEnabled = AidProfiling|AidEnabled;
const HIID FCwd = AidCwd;
const HIID FLogFileName = AidLog|AidFile|AidName;
const HIID FLogAppend = AidLog|AidAppend;


//##ModelId=3F60697A00ED
Forest::Forest ()
{
  staterec_ <<= new DMI::Record;
  // init default symdep set
  symdeps_.set(AidIteration,  0x02);
  symdeps_.set(AidState,depmask_state_ = 0x04);
  symdeps_.set(AidResolution, 0x08);
  symdeps_.set(AidDomain,     0x10);
  symdeps_.set(AidDataset,    0x20);
  // resize repository to 1 initially, so that index #0 is never used
  nodes.reserve(RepositoryChunkSize);
  nodes.resize(1);
  num_valid_nodes = 0;
  breakpoints = breakpoints_ss = 0;
  node_status_callback = 0;
  node_breakpoint_callback = 0;
  event_callback = 0;
  debug_level_ = 0;
  stop_flag_ = false;
  wstate()[FNumInitErrors] = num_init_errors = 0;
  // default cache policy
  cache_policy_ = Node::CACHE_SMART;
  log_policy_ = Node::LOG_NOTHING;
  log_append_ = false;
  log_filename_ = "meqlog.mql";
  profiling_enabled_ = true;
  abort_flag_ = false;

  // init the state record
  initDefaultState();
}

//##ModelId=400E53050193
void Forest::clear ()
{
  wstate()[FNumInitErrors] = num_init_errors = 0;
  nodes.resize(1);
  name_map.clear();
  num_valid_nodes = 0;
  logger_.close();
  Axis::resetDefaultMap();
}

//##ModelId=3F5F572601B2
NodeFace & Forest::create (int &node_index,DMI::Record::Ref &initrec,bool reinitializing)
{
  string classname;
  string nodename;
  NodeFace::Ref noderef;
  NodeFace *pnode;
  // get class from initrec and try to construct a node of that class
  try
  {
    classname = (*initrec)[FClass].as<string>("");
    nodename = (*initrec)[FName].as<string>("");
    node_index = (*initrec)[FNodeIndex].as<int>(-1);
    // check the node name for duplicates
    if( !nodename.empty() && name_map.find(nodename) != name_map.end() )
      Throw("node '"+nodename+"' already exists");
    // attempt to create node
    FailWhen(classname.empty(),"missing or invalid 'class' field in init record");
    DMI::BObj * pbp = DynamicTypeManager::construct(TypeId(classname));
    FailWhen(!pbp,classname+" is not a known node class");
    pnode = dynamic_cast<Meq::NodeFace*>(pbp);
    if( !pnode )
    {
      delete pbp;
      Throw("'"+classname+"' is not a node class");
    }
    noderef.attach(pnode,DMI::SHARED);
    // check if node index is already set (i.e. via init record),
    if( node_index > 0 ) // node index already set (i.e. when reloading)
    {
      FailWhen(node_index<int(nodes.size()) && nodes[node_index].valid(),
          Debug::ssprintf("%s: node %d already created",nodename.c_str(),node_index));
    }
    else  // not set, allocate new node index
      node_index = nodes.size();
    // if this is an actual node and not some weird NodeFace variation, reattach its inti-record
    pnode->setNameAndIndex(nodename,node_index);
    Node *pnode1 = dynamic_cast<Meq::Node*>(pnode);
    if( pnode1 )
    {
      if( reinitializing )
        pnode1->reattachInitRecord(initrec,this);
      else
        pnode1->attachInitRecord(initrec,this);
    }
  }
  catch( std::exception &exc )
  {
    wstate()[FNumInitErrors] = ++num_init_errors;
    ThrowMore(exc,"failed to create node '"+nodename +"' of class "+classname);
  }
  catch(...)
  {
    wstate()[FNumInitErrors] = ++num_init_errors;
    Throw("failed to create node '"+nodename +"' of class "+classname);
  }
  // resize repository as needed, and put node into it
  if( node_index >= int(nodes.capacity()) )
    nodes.reserve(node_index + RepositoryChunkSize);
  if( node_index >= int(nodes.size()) )
    nodes.resize(node_index+1);
  nodes[node_index] = noderef;
  // add to repository and name map
  num_valid_nodes++;
  if( !nodename.empty() )
    name_map[nodename] = node_index;
  return *pnode;
}

void Forest::initAll ()
{
  // call init() on all nodes
  for( uint i=0; i<nodes.size(); i++ )
    if( nodes[i].valid() )
    {
      try
      {
        nodes[i]().init();
      }
      catch( std::exception &exc )
      {
        wstate()[FNumInitErrors] = ++num_init_errors;
        postError(exc);
      }
    }
  // call checkChildren() on all nodes
  for( uint i=0; i<nodes.size(); i++ )
    if( nodes[i].valid() )
    {
      try
      {
        nodes[i]().checkChildren();
      }
      catch( std::exception &exc )
      {
        wstate()[FNumInitErrors] = ++num_init_errors;
        postError(exc);
      }
    }
}

//##ModelId=3F5F5CA300E0
int Forest::remove (int node_index)
{
  FailWhen(node_index<=0 || node_index>int(nodes.size()),
          "invalid node index");
  NodeFace::Ref &ref = nodes[node_index];
  FailWhen(!ref.valid(),"invalid node index");
  string name = ref->name();
  // detach the node & shrink repository if needed
  ref.detach();
  if( node_index == int(nodes.size())-1 )
    nodes.resize(node_index);
  num_valid_nodes--;
  if( !name.empty() )
  {
    // remove name from map, ignore if not found
    // (although it shouldn't happen)
    NameMap::iterator iter = name_map.find(name);
    if( iter != name_map.end() )
      name_map.erase(iter);
  }
  return 1;
}

//##ModelId=3F5F5B4F01BD
NodeFace & Forest::get (int node_index)
{
  FailWhen(node_index<=0 || node_index>int(nodes.size()),
          "invalid node index");
  NodeFace::Ref &ref = nodes[node_index];
  FailWhen(!ref.valid(),"invalid node index");
  return ref();
}

//##ModelId=3F5F5B9D016A
bool Forest::valid (int node_index) const
{
  return node_index>0 && node_index<int(nodes.size())
         && nodes[node_index].valid();
}

//##ModelId=3F5F5BB2032C
int Forest::findIndex (const string& name) const
{
  NameMap::const_iterator iter = name_map.find(name);
  return iter == name_map.end() ? -1 : iter->second;
}

//##ModelId=3F60549B02FE
NodeFace & Forest::findNode (const string &name)
{
  // lookup node index in map
  NameMap::const_iterator iter = name_map.find(name);
  FailWhen(iter == name_map.end(),"node '"+name+"' not found");
  int node_index = iter->second;
  // debug-fails here since name map should be consistent with repository
  DbgFailWhen(node_index<=0 || node_index>int(nodes.size()),"invalid node index");
  NodeFace::Ref &ref = nodes[node_index];
  DbgFailWhen(!ref.valid(),"invalid node index");
  return ref();
}

//##ModelId=3F7048570004
const NodeFace::Ref & Forest::getRef (int node_index)
{
  FailWhen(node_index<=0 || node_index>int(nodes.size()),
          "invalid node index");
  return nodes[node_index];
}

void Forest::incrRequestId (RequestId &rqid,const HIID &symdep)
{
  int depmask = getDependMask(symdep);
  if( !depmask )
    return;
  // the assigned value will be the max of index and whatever is already
  // at the specified position in rqid
  int index = ++symdep_counts[symdep];
  // find MSB of mask
  RqId::setSubId(rqid,depmask,index);
}

int Forest::getNodeList (DMI::Record &list,int content)
{
  Thread::Mutex::Lock lock(forestMutex());
  int num = num_valid_nodes;
  // create lists (arrays) for all known content
  DMI::Vec *lni=0,*lname=0,*lclass=0,*lstate=0,*lrqid=0,*lprof=0,*lcache=0;
  DMI::List *lchildren=0,*lstepchildren=0;
  if( content&NL_NODEINDEX )
    list[AidNodeIndex] <<= lni = new DMI::Vec(Tpint,num);
  if( content&NL_NAME )
    list[AidName] <<= lname = new DMI::Vec(Tpstring,num);
  if( content&NL_CLASS )
    list[AidClass] <<= lclass = new DMI::Vec(Tpstring,num);
  if( content&NL_CHILDREN )
  {
    list[AidChildren] <<= lchildren = new DMI::List;
    list[AidStep|AidChildren] <<= lstepchildren = new DMI::List;
  }
  if( content&NL_CONTROL_STATUS )
  {
    list[FControlStatus] <<= lstate = new DMI::Vec(Tpint,num);
    list[FRequestId] <<= lrqid = new DMI::Vec(TpDMIHIID,num);
  }
  if( content&NL_PROFILING_STATS )
  {
    list[FProfilingStats] <<= lprof = new DMI::Vec(TpDMIRecord,num);
    list[FCacheStats] <<= lcache = new DMI::Vec(TpDMIRecord,num);
  }
  if( num )
  {
    // fill them up
    int i0 = 0;
    for( uint i=1; i<nodes.size(); i++ )
      if( nodes[i].valid() )
      {
        FailWhen(i0>num,"forest inconsistency: too many valid nodes");
        NodeFace &node = nodes[i]();
        DMI::Record::Ref nodestate;
        if( lni )
          (*lni)[i0] = i;
        if( lname )
          (*lname)[i0] = node.name();
        if( lclass )
          (*lclass)[i0] = node.className();
        Node *pnode = dynamic_cast<Node*>(&node);
        if( pnode )
        {
          if( lstate )
            (*lstate)[i0] = pnode->getControlStatus();
          if( lrqid )
            (*lrqid)[i0] = pnode->currentRequestId();
        }
        if( lchildren )
        {
          node.getState(nodestate);
          DMI::Record::Hook hook(*nodestate,FChildren);
          if( hook.exists() )
            lchildren->addBack(hook.ref(true));
          else
            lchildren->addBack(new DMI::List);
          DMI::Record::Hook hook1(*nodestate,FStepChildren);
          if( hook1.exists() )
            lstepchildren->addBack(hook1.ref(true));
          else
            lstepchildren->addBack(new DMI::List);
        }
        if( lprof )
        {
          node.getSyncState(nodestate);
          (*lprof)[i0] = (*nodestate)[FProfilingStats].ref(true);
          (*lcache)[i0] = (*nodestate)[FCacheStats].ref(true);
        }
        i0++;
      }
    FailWhen(i0<num,"forest inconsistency: too few valid nodes found");
  }
  return num;
}

void Forest::initDefaultState ()
{
  DMI::Record &st = wstate();
  // get CWD
  const size_t cwdsize = 16384;
  char *cwd_temp = new char[cwdsize];
  getcwd(cwd_temp,cwdsize);
  st[FCwd] = cwd_temp;
  delete [] cwd_temp;
  // state maps
  st[FAxisMap] = Axis::getAxisRecords();
  st[FAxisList] = Axis::getAxisIds();
  st[FDebugLevel] = debug_level_;
  st[FSymdeps] <<= symdeps().toRecord();
  st[FCachePolicy] = cache_policy_;
  st[FProfilingEnabled] = profiling_enabled_;
  st[FBreakpoint] = breakpoints;
  st[FBreakpointSingleShot] = breakpoints_ss;
}

DMI::Record::Ref Forest::state () const
{
  Thread::Mutex::Lock lock(forestMutex());
  // update axis map
  staterec_()[FAxisMap] = Axis::getAxisRecords();
  staterec_()[FAxisList] = Axis::getAxisIds();
  return staterec_.copy();
}

void Forest::setStateImpl (DMI::Record::Ref &rec)
{
  // always ignore cwd field
//  if( rec->hasField(FCwd) )
//    rec().removeField(FCwd);

  // axis map may be specified as list of ids or list of records
  if( rec->hasField(FAxisMap) )
  {
    Axis::setAxisRecords(rec[FAxisMap].as<DMI::Vec>());
    rec[FAxisList] = Axis::getAxisIds();
  }
  else if( rec->hasField(FAxisList) )
  {
    Axis::setAxisMap(rec[FAxisList].as<DMI::Vec>());
    rec[FAxisMap] = Axis::getAxisRecords();
  }
  rec[FCachePolicy].get(cache_policy_);
  rec[FLogPolicy].get(log_policy_);
  rec[FLogFileName].get(log_filename_);
  rec[FLogAppend].get(log_append_);
  rec[FProfilingEnabled].get(profiling_enabled_);
  rec[FBreakpoint].get(breakpoints);
  rec[FBreakpointSingleShot].get(breakpoints_ss);
//  FailWhen(rec->hasField(FKnownSymdeps),"immutable field: "+FKnownSymdeps.toString());
//  FailWhen(rec->hasField(FSymdeps),"immutable field: "+FSymdeps.toString());
//   if( rec->hasField(FSymDeps) )
//   {
//     const DMI::Record &rec = rec[FSymDeps];
//     // retrieve map
//     DMI::Record::const_iterator iter = rec.begin();
//     SymdepMap map;
//     for( ; iter != rec.end(); iter++ )
//       map[iter.id()] = iter.ref().as<DMI::Container>()[HIID()].as<int>();
//     // check that all known symdeps are present
//     for( SymdepMap::const_iterator iter = known_symdeps.begin();
//          iter != known_symdeps.end(); iter++ )
//     {
//       FailWhen(map.find(iter->first) == map.end(),FSymDeps.toString()+" does not "
//           " contain required symdep "+iter->first.toString());
//     }
//     // copy
//     symdep_map = map;
//     for( SymdepMap::iterator iter = known_symdeps.begin();
//          iter != known_symdeps.end(); iter++ )
//       iter->second = map[iter->first];
//     // reset state fields
//     fillSymDeps(wstate()[FKnownSymDeps].replace() <<= new DMI::Record,known_symdeps);
//   }
}

void Forest::setState (DMI::Record::Ref &rec,bool complete)
{
  Thread::Mutex::Lock lock(forestMutex());
  cdebug(2)<<"setState(complete="<<complete<<"): "<<rec.sdebug(10)<<endl;
  string fail;
  try
  {
    setStateImpl(rec);
  }
  catch( FailWithoutCleanup &exc )
  {
    throw; // No cleanup required, just re-throw
  }
  catch( std::exception &exc )
  {
    setStateImpl(staterec_);
    ThrowMore(exc,"Forest::setState() failed");
  }
  catch( ... )
  {
    setStateImpl(staterec_);
    Throw("Forest::setState() failed with unknown exception");
  }
  // success, merge or overwrite current state
  if( complete )
    staterec_ = rec;
  else
    wstate().merge(rec,true);
}

void Forest::raiseStopFlag ()
{
  stop_flag_ = true;
}

// This clears the stopped_at_breakpoint flag and signals on the
// condition variable so as to restart all threads
void Forest::clearStopFlag ()
{
  Thread::Mutex::Lock lock(stop_flag_cond_);
  stop_flag_ = false;
  stop_flag_cond_.broadcast();
}

// Waits for the stopped_at_breakpoint flag to clear, then returns.
// In mt-mode, when one thread is halted at a breakpoint, this
// flag is used to halt the other threads at the first opportunity.
// In single-threaded mode this function should never be called.
void Forest::waitOnStopFlag () const
{
  Thread::Mutex::Lock lock(stop_flag_cond_);
  while( stop_flag_ )
    stop_flag_cond_.wait();
}

// sets global breakpoint(s)
void Forest::setBreakpoint (int bpmask,bool single_shot)
{
  Thread::Mutex::Lock lock(forestMutex());
  if( single_shot )
    wstate()[FBreakpointSingleShot] = breakpoints_ss |= bpmask;
  else
    wstate()[FBreakpoint] = breakpoints |= bpmask;
}

// clears global breakpoint(s)
void Forest::clearBreakpoint (int bpmask,bool single_shot)
{
  Thread::Mutex::Lock lock(forestMutex());
  if( single_shot )
    wstate()[FBreakpointSingleShot] = breakpoints_ss &= ~bpmask;
  else
    wstate()[FBreakpoint] = breakpoints &= ~bpmask;
}

void Forest::processBreakpoint (Node &node,int bpmask,bool global)
{
  Thread::Mutex::Lock lock(stop_flag_cond_);
  raiseStopFlag();
  if( node_breakpoint_callback )
    (*node_breakpoint_callback)(node,bpmask,global);
  lock.release();
  waitOnStopFlag();
}

void Forest::flushLog ()
{
  Thread::Mutex::Lock lock(log_mutex_);
  if( logger_.isOpen() )
    logger_.flush();
}

void Forest::closeLog ()
{
  Thread::Mutex::Lock lock(log_mutex_);
  if( logger_.isOpen() )
    logger_.close();
}

void Forest::logNodeResult (const Node &node,const Request &req,const Result &res)
{
  // create log entry
  DMI::Record entry;
  entry[FName]      = node.name();
  entry[FRequestId] = req.id();
  entry[AidTimestamp] = Timestamp::now().seconds();
  entry[FRequest]   = req;
  entry[FResult]    = res;
  Thread::Mutex::Lock lock(log_mutex_);
  // open logger as necessary
  if( !logger_.isOpen() )
    logger_.open(log_filename_,log_append_ ? BOIO::APPEND : BOIO::WRITE);
  logger_ << entry;
}

void Forest::postError (const std::exception &exc)
{
  DMI::Record *prec = new DMI::Record;
  ObjRef out(prec);
  (*prec)[AidError] = exceptionToObj(exc);
  postEvent(AidError,out);
}

void Forest::postMessage (const std::string &msg,const HIID &type)
{
  DMI::Record *prec = new DMI::Record;
  ObjRef out(prec);
  if( type == HIID(AidError) )
    (*prec)[AidError] = msg;
  else
    (*prec)[AidMessage] = msg;
  postEvent(type,out);
}

    
} // namespace Meq
