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
#include <DMI/DataList.h>
    
// pull in registry
static int dum = aidRegistry_Meq();

namespace Meq
{

InitDebugContext(Forest,"MeqForest");

  
//##ModelId=3F60697A00ED
Forest::Forest ()
{
  // resize repository to 1 initially, so that index #0 is never used
  nodes.reserve(RepositoryChunkSize);
  nodes.resize(1);
  num_valid_nodes = 0;
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
const Node::Ref & Forest::create (int &node_index,
    DataRecord::Ref::Xfer &initrec,bool reinitializing)
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
    BlockableObject * pbp = DynamicTypeManager::construct(TypeId(classname));
    FailWhen(!pbp,"construct failed");
    pnode = dynamic_cast<Meq::Node*>(pbp);
    if( !pnode )
    {
      delete pbp;
      Throw(classname+" is not a Meq::Node descendant");
    }
    noderef <<= pnode;
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
  return nodes[node_index];
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

//##ModelId=3F9937F601A5
const HIID & Forest::assignRequestId (Request &req)
{
  if( !last_req_cells.valid() ) // first request ever request?
  {
    last_req_cells.attach(req.cells()).privatize(DMI::READONLY|DMI::DEEP);
    last_req_id = HIID(1);
  }
  else
  {
    // cells do not match lastious request? Update the ID
    if( req.cells() != *last_req_cells )
    {
      last_req_cells.attach(req.cells()).privatize(DMI::READONLY|DMI::DEEP);
      last_req_id[0] = last_req_id[0]+1;
    }
  }
  req.setId(last_req_id);
  return last_req_id;
}

int Forest::getNodeList (DataRecord &list,int content)
{
  int num = num_valid_nodes;
  // create lists (arrays) for all known content
  DataField *lni=0,*lname=0,*lclass=0;
  DataList *lchildren=0;
  if( content&NL_NODEINDEX )
    list[AidNodeIndex] <<= lni = new DataField(Tpint,num);
  if( content&NL_NAME )
    list[AidName] <<= lname = new DataField(Tpstring,num);
  if( content&NL_CLASS )
    list[AidClass] <<= lclass = new DataField(Tpstring,num);
  if( content&NL_CHILDREN )
    list[AidChildren] <<= lchildren = new DataList;
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
        if( lchildren )
        {
          DataRecord::Hook hook(node.state(),FChildren);
          if( hook.type() == TpDataField )
            lchildren->addBack(hook.as_p<DataField>());
          else if( hook.type() == TpDataRecord )
            lchildren->addBack(hook.as_p<DataRecord>());
          else
            lchildren->addBack(new DataField,DMI::ANONWR);
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

} // namespace Meq
