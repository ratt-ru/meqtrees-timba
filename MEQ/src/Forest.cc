//#  Forest.cc: MeqForest class
//#
//#  Copyright (C) 2002-2003
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
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
    
// pull in registry
static int dum = aidRegistry_Meq();

namespace Meq
{

InitDebugContext(Forest,"MeqForest");

// forest state fields
const HIID FAxisMap = AidAxis|AidMap;
const HIID FDebugLevel = AidDebug|AidLevel;
const HIID FKnownSymdeps = AidKnown|AidSymdeps;
const HIID FSymdeps = AidSymdeps;
const HIID FProfilingEnabled = AidProfiling|AidEnabled;
  
//##ModelId=3F60697A00ED
Forest::Forest ()
{
  staterec_ <<= new DMI::Record;
  // init default symdep set
  known_symdeps[AidIteration]  = 0x01;
  known_symdeps[AidSolution]   = 0x02;
  known_symdeps[AidDomain]     = 0x04;
  known_symdeps[AidResolution] = 0x04; // same as domain for now
  known_symdeps[AidDataset]    = 0x08;
  symdep_map = known_symdeps;
  // init required depmasks
  depmask_dataset_ = symdep_map[AidDataset];
  depmask_domain_  = symdep_map[AidDomain];
  // resize repository to 1 initially, so that index #0 is never used
  nodes.reserve(RepositoryChunkSize);
  nodes.resize(1);
  num_valid_nodes = 0;
  breakpoints = breakpoints_ss = 0;
  node_status_callback = 0;
  node_breakpoint_callback = 0;
  debug_level_ = 0;
  // default cache policy
  cache_policy_ = Node::CACHE_SMART;
  profiling_enabled_ = true;
  
  // init the state record
  initDefaultState();
}

//##ModelId=400E53050193
void Forest::clear ()
{
  nodes.resize(1);
  name_map.clear();
  num_valid_nodes = 0;
  if( evgen_delete.active() )
    evgen_delete.generateEvent(ObjRef(),0); // null ptr means all nodes deleted
}

//##ModelId=3F5F572601B2
Node & Forest::create (int &node_index,DMI::Record::Ref &initrec,bool reinitializing)
{
  string classname;
  Node::Ref noderef;
  Node *pnode;
  // get class from initrec and try to construct a node of that class
  try
  {
    classname = (*initrec)[FClass].as<string>("");
    node_index = (*initrec)[FNodeIndex].as<int>(-1);
    FailWhen( !classname.length(),"missing or invalid Class field in init record"); 
    DMI::BObj * pbp = DynamicTypeManager::construct(TypeId(classname));
    FailWhen(!pbp,"construct failed");
    pnode = dynamic_cast<Meq::Node*>(pbp);
    if( !pnode )
    {
      delete pbp;
      Throw(classname+" is not a Meq::Node descendant");
    }
    noderef.attach(pnode,DMI::SHARED);
    if( reinitializing )
      pnode->reinit(initrec,this);
    else
      pnode->init(initrec,this);
  }
  catch( std::exception &exc )
  {
    Throw("failed to init a "+classname+": "+exc.what()); 
  }
  catch(...)
  {
    Throw("failed to init a "+classname); 
  }
  // check the node name for duplicates
  string name = noderef->name();
  if( !name.empty() && name_map.find(name) != name_map.end() )
    Throw("node '"+name+"' already exists");
  // check if node index is already set (i.e. via init record),
  if( node_index > 0 ) // node index already set (i.e. when reloading)
  {
    FailWhen(node_index<int(nodes.size()) && nodes[node_index].valid(),
        Debug::ssprintf("node %d already created",node_index));
  }
  else  // not set, allocate new node index
    node_index = nodes.size();
  // resize repository as needed, and put node into it
  if( node_index >= int(nodes.capacity()) )
    nodes.reserve(node_index + RepositoryChunkSize);
  if( node_index >= int(nodes.size()) )
    nodes.resize(node_index+1);
  nodes[node_index] = noderef;
  pnode->setNodeIndex(node_index);
  // add to repository and name map
  num_valid_nodes++;
  if( !name.empty() )
    name_map[name] = node_index;
  // post event
  if( evgen_create.active() )
    evgen_create.generateEvent(ObjRef(pnode->state()),pnode);
  return *pnode;
}

//##ModelId=3F5F5CA300E0
int Forest::remove (int node_index)
{
  FailWhen(node_index<=0 || node_index>int(nodes.size()),
          "invalid node index");
  Node::Ref &ref = nodes[node_index];
  FailWhen(!ref.valid(),"invalid node index");
  string name = ref->name();
  // generate delete event
  if( evgen_delete.active() )
    evgen_delete.generateEvent(ObjRef(),ref.dewr_p());
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
Node & Forest::get (int node_index)
{
  FailWhen(node_index<=0 || node_index>int(nodes.size()),
          "invalid node index");
  Node::Ref &ref = nodes[node_index];
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
Node & Forest::findNode (const string &name)
{
  // lookup node index in map
  NameMap::const_iterator iter = name_map.find(name);
  FailWhen(iter == name_map.end(),"node '"+name+"' not found");
  int node_index = iter->second;
  // debug-fails here since name map should be consistent with repository
  DbgFailWhen(node_index<=0 || node_index>int(nodes.size()),"invalid node index");
  Node::Ref &ref = nodes[node_index];
  DbgFailWhen(!ref.valid(),"invalid node index");
  return ref();
}

//##ModelId=3F7048570004
const Node::Ref & Forest::getRef (int node_index)
{
  FailWhen(node_index<=0 || node_index>int(nodes.size()),
          "invalid node index");
  return nodes[node_index];
}

// //##ModelId=3F9937F601A5
// const HIID & Forest::assignRequestId (Request &req)
// {
//   if( !last_req_cells.valid() ) // first request ever?
//   {
//     incrSubId(last_req_id,depmask_dataset_);
//     last_req_cells.attach(req.cells());
//   }
//   else
//   {
//     // cells do not match last request? Update the ID
//     if( req.cells() != *last_req_cells )
//     {
//       last_req_cells.attach(req.cells());
//       incrSubId(last_req_id,depmask_domain_);
//     }
//   }
//   req.setId(last_req_id);
//   return last_req_id;
// }
// 
// 
// void Forest::resetForNewDataSet ()
// {
//   last_req_cells.detach();
// }

void Forest::incrRequestId (RequestId &rqid,const HIID &symdep)
{
  int depmask = getDependMask(symdep);
  if( !depmask )
    return;
  // the assigned value will be the max of index and whatever is already
  // at the specified position in rqid
  int & index = ++symdep_counts[symdep];
  // find MSB of mask
  uint msb=0;
  for( int m1=depmask; m1 != 0; m1 >>= 1 )
    msb++;
  // if request ID is shorter, resize
  if( rqid.size() < msb )
    rqid.push_front(0,msb-rqid.size());
  // start from end 
  HIID::reverse_iterator iter = rqid.rbegin();
  // ... until we run out of bits, or get to the start of the id
  for( int m1=1; 
       m1 < (1<<RQIDM_NBITS) && iter != rqid.rend(); 
       m1<<=1,iter++ )
  {
    if( depmask&m1 && *iter >= index )
      index = *iter+1;
  }
  // now assign the index
  iter = rqid.rbegin();
  // ... until we run out of bits, or get to the start of the id
  for( int m1=1; 
       m1 < (1<<RQIDM_NBITS) && iter != rqid.rend(); 
       m1<<=1,iter++ )
  {
    if( depmask&m1 )
      *iter = index;
  }
}

int Forest::getNodeList (DMI::Record &list,int content)
{
  int num = num_valid_nodes;
  // create lists (arrays) for all known content
  DMI::Vec *lni=0,*lname=0,*lclass=0,*lstate=0;
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
    list[FControlStatus] <<= lstate = new DMI::Vec(Tpint,num);
  if( num )
  {
    // fill them up
    int i0 = 0;
    for( uint i=1; i<nodes.size(); i++ )
      if( nodes[i].valid() )
      {
        FailWhen(i0>num,"forest inconsistency: too many valid nodes");
        const Node &node = *nodes[i];
        if( lni )
          (*lni)[i0] = i;
        if( lname )
          (*lname)[i0] = node.name();
        if( lclass )
          (*lclass)[i0] = node.className();
        if( lstate )
          (*lstate)[i0] = node.getControlStatus();
        if( lchildren )
        {
          lchildren->addBack(node.state()[FChildren].ref(true));
          lstepchildren->addBack(node.state()[FStepChildren].ref(true));
        }
        i0++;
      }
    FailWhen(i0<num,"forest inconsistency: too few valid nodes found");
  }
  return num;
}

EventGenerator & Forest::getEventGenerator (const HIID &evtype)
{
  if( evtype == AidCreate )
    return evgen_create;
  else if( evtype == AidDelete )
    return evgen_delete;
  else
  {
    Throw("unknown event type: "+evtype.toString());
  }
}

void Forest::fillSymDeps (DMI::Record &rec,const SymdepMap &map)
{
  for( SymdepMap::const_iterator iter = map.begin(); iter != map.end(); iter++ )
    rec[iter->first] = iter->second;
}

void Forest::initDefaultState ()
{
  DMI::Record &st = wstate();
  st[FAxisMap] = Axis::getAxisRecords();
  st[FDebugLevel] = debug_level_;
  DMI::Record &known = st[FKnownSymDeps] <<= new DMI::Record;
  fillSymDeps(st[FKnownSymdeps] <<= new DMI::Record,known_symdeps);
  fillSymDeps(st[FSymdeps] <<= new DMI::Record,symdep_map);
  st[FCachePolicy] = cache_policy_;
  st[FProfilingEnabled] = profiling_enabled_;
}

void Forest::setStateImpl (DMI::Record::Ref &rec)
{
  if( rec->hasField(FAxisMap) )
    Axis::setAxisRecords(rec[FAxisMap].as<DMI::Vec>());
  rec[FCachePolicy].get(cache_policy_);
  rec[FProfilingEnabled].get(profiling_enabled_);
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
  Thread::Mutex::Lock lock(rec->mutex()),lock2(state().mutex());
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
    fail = string("setState() failed: ") + exc.what();
  }
  catch( ... )
  {
    fail = "setState() failed with unknown exception";
  }
  // has setStateImpl() failed?
  if( fail.length() )
  {
    // reset the state by reinitializing with the current record.
    // that an exception from this call indicates that the forest is well 
    // & truly fscked, sowe might as well re-throw it, 
    // letting the caller deal with it.
    setStateImpl(staterec_);
    Throw(fail); // rethrow the fail
  }
  // success, merge or overwrite current state
  if( complete )
    staterec_ = rec;
  else  
    wstate().merge(rec,true);
}



} // namespace Meq
