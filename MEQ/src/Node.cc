//#  Node.cc: base MeqNode class
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

#include "Node.h"
#include "Forest.h"
#include <DMI/BlockSet.h>
#include <DMI/DataRecord.h>

namespace MEQ {

InitDebugContext(Node,"MeqNode");

//##ModelId=3F5F43E000A0
Node::Node()
{
}

//##ModelId=3F5F44A401BC
Node::~Node()
{
}

//##ModelId=3F5F45D202D5
void Node::init (DataRecord::Ref::Xfer &initrec, Forest* frst)
{
  forest_ = frst;
  // xfer & privatize the state record -- we don't want anyone
  // changing it under us
  staterec_ = initrec;
  staterec_.privatize(DMI::WRITE|DMI::DEEP);
  // extract node name
  myname_ = (*staterec_)[AidName].as<string>("");
  cdebug(1)<<"initializing MeqNode "<<myname_<<endl;
  // setup child nodes, if specified
  if( state()[AidChildren].exists() )
  {
    DataRecord &childrec = state()[AidChildren].as_wr<DataRecord>();
    // iterate thorugh children record and create the child nodes
    DataRecord::Iterator iter = childrec.initFieldIter();
    HIID id;
    NestableContainer::Ref child_ref;
    while( childrec.getFieldIter(iter,id,child_ref) )
    {
      // child specified by init-record: create recursively
      if( childrec[id].containerType() == TpDataRecord )
      {
        cdebug(4)<<"  child "<<id<<" specified by init record"<<endl;
        int index;
        ObjRef child_initrec = childrec[id].remove();
        try
        {
          cdebug(2)<<"  creating child "<<id<<endl;
          Node &child = forest_->create(index,child_initrec.ref_cast<DataRecord>());
          addChild(id,child);
        }
        catch( std::exception &exc )
        {
          Throw("Failed to create child node "+id.toString()+": "+exc.what());
        }
      }
      else // not an init record
      {
        TypeId type = childrec[id].type();
        cdebug(4)<<"  child "<<id<<" entry of type "<<type<<endl;
        // child specified by name -- look it up in the forest_
        if( type == Tpstring )
        {
          const string & name = childrec[id].as<string>();
          int index = forest_->findIndex(name);
          if( index >= 0 )
          {
            Node &child = forest_->get(index);
            cdebug(2)<<"  child "<<id<<"="<<name<<" resolves to node "<<index<<endl;
            addChild(id,child);
          }
          else
          { // defer until later if not found
            cdebug(2)<<"  child "<<id<<"="<<name<<" currently unresolved"<<endl;
            unresolved_children_.push_back(
                UnresolvedChild(id,name));
          }
        }
        // child specified by index -- just get & attach it directly
        else if( type == Tpint )
        {
          int index = childrec[id];
          Node &child = forest_->get(index);
          cdebug(2)<<"  child "<<id<<"="<<index<<endl;
          addChild(id,child);
        }
        else
          Throw("illegal specification for child "+id.toString()+" (type "+
                type.toString()+")");
      }
    }
    cdebug(2)<<numChildren()<<" children attached, "
             <<unresolved_children_.size()<<" deferred"<<endl;
  }
}

//##ModelId=3F8433C20193
void Node::addChild (const HIID &id,Node &childnode)
{
  int n = children_.size();
  children_.resize(n+1);
  children_[n].attach(childnode,DMI::WRITE);
  child_map_[id] = n;
  cdebug(3)<<"added child "<<n<<": "<<id<<endl;
}

//##ModelId=3F83FAC80375
void Node::resolveChildren ()
{
  if( !unresolved_children_.empty() )
  {
    cdebug(2)<<"trying to resolve "<<unresolved_children_.size()<<" children"<<endl;
  }
  
  while( !unresolved_children_.empty() )
  {
    UnresolvedChild &child = unresolved_children_.front();
    cdebug(3)<<"resolving child "<<child.first<<"="<<child.second<<endl;
    // findNode() will throw an exception if the node is not found,
    // which is exactly what we want
    try
    {
      Node & childnode = forest_->findNode(child.second);
      addChild(child.first,childnode);
    }
    catch( ... )
    {
      Throw("failed to resolve child "+child.first.toString()+"="+child.second);
    }
    unresolved_children_.pop_front();
  }
  // recursively call resolve on the children
  for( int i=0; i<numChildren(); i++ )
    getChild(i).resolveChildren();
  // check children for consistency
  checkChildren();
}

//##ModelId=3F83FADF011D
void Node::checkChildren ()
{
// default version does nothing, always succeeeds
}

Node & Node::getChild (const HIID &id)
{
  ChildrenMap::const_iterator iter = child_map_.find(id);
  FailWhen(iter==child_map_.end(),"unresolved child "+id.toString());
  return getChild(iter->second);
}

//##ModelId=3F5F445A00AC
void Node::setState (const DataRecord &rec)
{
  // copy relevant fields from new record
  // the only relevant one at this level is Name
  if( rec[AidName].exists() )
    staterec_()[AidName] = myname_ = rec[AidName].as<string>();
}

//##ModelId=3F6726C4039D
int Node::getResult (Result::Ref &, const Request&)
{
  Throw("MEQ::Node::getResult not implemented");
}

// throw exceptions for unimplemented DMI functions
//##ModelId=3F5F4363030F
CountedRefTarget* Node::clone(int,int) const
{
  Throw("MEQ::Node::clone not implemented");
}

//##ModelId=3F5F43630315
int Node::fromBlock(BlockSet&)
{
  Throw("MEQ::Node::fromBlock not implemented");
}

//##ModelId=3F5F43630318
int Node::toBlock(BlockSet &) const
{
  Throw("MEQ::Node::toBlock not implemented");
}

//##ModelId=3F5F48180303
string Node::sdebug (int detail, const string &prefix, const char *nm) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s(%s)",nm?nm:"MEQ::Node",name().c_str());
  }
  if( detail >= 1 || detail == -1 )
  {
    appendf(out,"children:%d",numChildren());
    if( unresolved_children_.size() )
      appendf(out,"unresolved:%d",unresolved_children_.size());
  }
  if( abs(detail) >= 2 )
  {
    ChildrenMap::const_iterator iter = child_map_.begin();
    for( ; iter != child_map_.end(); iter++ )
    {
      out += "\n" + prefix + "  " + iter->first.toString() + ": " 
           + children_[iter->second]->sdebug(abs(detail)-2);
    }
  }
  return out;
}

} // namespace MEQ
