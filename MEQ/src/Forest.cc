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
#include "AID-Meq.h"
#include <DMI/DynamicTypeManager.h>
    
// pull in registry
static int dum = aidRegistry_Meq();

namespace Meq
{

InitDebugContext(Forest,"MeqForest");

  
//##ModelId=3F60697A00ED
Forest::Forest ()
    : last_req_cells(Domain(),1,1)
{
  // resize repository to 1 initially, so that index #0 is never used
  nodes.reserve(RepositoryChunkSize);
  nodes.resize(1);
}

//##ModelId=3F5F572601B2
const Node::Ref & Forest::create (int &node_index,DataRecord::Ref::Xfer &initrec)
{
  string classname;
  Node::Ref noderef;
  // get class from initrec and try to construct a node of that class
  try
  {
    classname = (*initrec)[AidClass].as<string>("");
    FailWhen( !classname.length(),"missing or invalid Class field in init record"); 
    BlockableObject * pbp = DynamicTypeManager::construct(TypeId(classname));
    FailWhen(!pbp,"construct failed");
    Meq::Node * pnode = dynamic_cast<Meq::Node*>(pbp);
    if( !pnode )
    {
      delete pbp;
      Throw(classname+" is not a Meq::Node descendant");
    }
    noderef <<= pnode;
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
  if( name.length() && name_map.find(name) != name_map.end() )
    Throw("node '"+name+"' already exists");
  // allocate entry in repository, extend when needed
  node_index = nodes.size();
  if( node_index >= int(nodes.capacity()) )
    nodes.reserve(nodes.size()+RepositoryChunkSize);
  // add to repository and name map
  nodes.push_back(noderef);
  name_map[name] = node_index;
  return nodes.back();
}

//##ModelId=3F5F5CA300E0
int Forest::remove (int node_index)
{
  FailWhen(node_index<=0 || node_index>int(nodes.size()),
          "invalid node index");
  Node::Ref &ref = nodes[node_index];
  FailWhen(!ref.valid(),"invalid node index");
  string name = ref->name();
  // detach the node & shrink repository if needed
  ref.detach();
  if( node_index == int(nodes.size())-1 )
    nodes.resize(node_index);
  // remove name from map, ignore if not found
  // (although it shouldn't happen)
  NameMap::iterator iter = name_map.find(name);
  if( iter != name_map.end() )
    name_map.erase(iter);
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
  DbgFailWhen(node_index<=0 || node_index>nodes.size(),"invalid node index");
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

const HIID & Forest::assignRequestId (Request &req)
{
  if( last_req_id.empty() ) // no lastious request?
  {
    last_req_id = HIID(1);
    last_req_cells = req.cells();
  }
  else
  {
    // cells do not match lastious request? Update the ID
    if( req.cells() != last_req_cells )
    {
      last_req_cells = req.cells();
      last_req_id[0] = last_req_id[0]+1;
    }
  }
  req.setId(last_req_id);
  return last_req_id;
}

} // namespace Meq
