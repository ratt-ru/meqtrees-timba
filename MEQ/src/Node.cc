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
#include <DMI/DataField.h>
#include <DMI/DataArray.h>

namespace Meq {

InitDebugContext(Node,"MeqNode");

//##ModelId=3F5F43E000A0
Node::Node()
{
}

//##ModelId=3F5F44A401BC
Node::~Node()
{
}

//##ModelId=3F9505E50010
void Node::processChildSpec (NestableContainer &children,const HIID &id)
{
  // child specified by init-record: create recursively
  TypeId spec_type = children[id].type();
  if( spec_type == TpDataRecord )
  {
    cdebug(4)<<"  child "<<id<<" specified by init record"<<endl;
    int index;
    ObjRef child_initrec = children[id].remove();
    try
    {
      cdebug(2)<<"  creating child "<<id<<endl;
      Node &child = forest_->create(index,child_initrec.ref_cast<DataRecord>());
      addChild(id,&child);
    }
    catch( std::exception &exc )
    {
      Throw("Failed to create child node "+id.toString()+": "+exc.what());
    }
  }
  else // not an init record
  {
    if( TypeInfo::isArray(spec_type) )
      spec_type = TypeInfo::typeOfArrayElem(spec_type);
    cdebug(4)<<"  child "<<id<<" entry of type "<<spec_type<<endl;
    // child specified by name -- look it up in the forest
    if( spec_type == Tpstring )
    {
      const string & name = children[id].as<string>();
      if( name.length() ) // skip if empty string
      {
        int index = forest_->findIndex(name);
        if( index >= 0 )
        {
          Node &child = forest_->get(index);
          cdebug(2)<<"  child "<<id<<"="<<name<<" resolves to node "<<index<<endl;
          addChild(id,&child);
        }
        else
        { // defer until later if not found
          cdebug(2)<<"  child "<<id<<"="<<name<<" currently unresolved"<<endl;
          addChild(id,0);
          unresolved_children_.push_back(name);
        }
      }
    }
    // child specified by index -- just get & attach it directly
    else if( spec_type == Tpint )
    {
      int index = children[id];
      Node &child = forest_->get(index);
      cdebug(2)<<"  child "<<id<<"="<<index<<endl;
      addChild(id,&child);
    }
    else
      Throw("illegal specification for child "+id.toString()+" (type "+
            spec_type.toString()+")");
  }
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
    // children specified via a record
    if( state()[AidChildren].containerType() == TpDataRecord )
    {
      DataRecord &childrec = wstate()[AidChildren].as_wr<DataRecord>();
      // iterate through children record and create the child nodes
      DataRecord::Iterator iter = childrec.initFieldIter();
      HIID id;
      NestableContainer::Ref child_ref;
      while( childrec.getFieldIter(iter,id,child_ref) )
        processChildSpec(childrec,id);
    }
    else if( state()[AidChildren].containerType() == TpDataField )
    {
      DataField &childrec = wstate()[AidChildren].as_wr<DataField>();
      for( int i=0; i<childrec.size(); i++ )
        processChildSpec(childrec,AtomicID(i));
    }
    else if( state()[AidChildren].containerType() == TpDataArray )
    {
      DataArray &childarr = wstate()[AidChildren].as_wr<DataArray>();
      FailWhen(childarr.rank()!=1,"illegal child array");
      for( int i=0; i<childarr.shape()[0]; i++ )
        processChildSpec(childarr,AtomicID(i));
    }
    cdebug(2)<<numChildren()<<" children, "
             <<unresolved_children_.size()<<" unresolved"<<endl;
  }
}

//##ModelId=3F8433C20193
void Node::addChild (const HIID &id,Node *childnode)
{
  int n = children_.size();
  children_.resize(n+1);
  child_map_[id] = n;
  // attach ref to child if specified (will stay unresolved otherwise)
  if( childnode )
    children_[n].attach(childnode,DMI::WRITE);
  cdebug(3)<<"added child "<<n<<": "<<id<<endl;
}

//##ModelId=3F83FAC80375
void Node::resolveChildren ()
{
  if( !unresolved_children_.empty() )
  {
    cdebug(2)<<"trying to resolve "<<unresolved_children_.size()<<" children"<<endl;
    for( int i=0; i<numChildren(); i++ )
    {
      if( !children_[i].valid() )
      {
        string name = unresolved_children_.front();
        cdebug(3)<<"resolving child "<<i<<":"<<name<<endl;
        // findNode() will throw an exception if the node is not found,
        // which is exactly what we want
        try
        {
          Node &childnode = forest_->findNode(name);
          children_[i].attach(childnode,DMI::WRITE);
        }
        catch( ... )
        {
          Throw(Debug::ssprintf("failed to resolve child %d:%s",i,name.c_str()));
        }
        unresolved_children_.pop_front();
      }
    }
    FailWhen(!unresolved_children_.empty(),"error, unexpected unresolved names remain");
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

//##ModelId=3F85710E011F
Node & Node::getChild (int i)
{
  FailWhen(!children_[i].valid(),"unresolved child");
  return children_[i].dewr();
}

//##ModelId=3F85710E028E
Node & Node::getChild (const HIID &id)
{
  ChildrenMap::const_iterator iter = child_map_.find(id);
  FailWhen(iter==child_map_.end(),"unknown child "+id.toString());
  return getChild(iter->second);
}

//##ModelId=3F98D9D20201
inline int Node::getChildNumber (const HIID &id)
{
  ChildrenMap::const_iterator iter = child_map_.find(id);
  return iter == child_map_.end() ? -1 : iter->second;
}

//##ModelId=3F5F445A00AC
void Node::setState (const DataRecord &rec)
{
  // copy relevant fields from new record
  // the only relevant one at this level is Name
  if( rec[AidName].exists() )
    staterec_()[AidName] = myname_ = rec[AidName].as<string>();
}

void Node::setCurrentRequest (const Request &req)
{
  wstate()[AidRequest|AidId] = current_req_id_ = req.id();
}

//##ModelId=3F6726C4039D
int Node::getResult (ResultSet::Ref &ref, const Request &req)
{
  cdebug(3)<<"getResult, request ID "<<req.id()<<": "<<req.sdebug(DebugLevel-1,"    ")<<endl;
  // do we have a new request?
  bool newreq = req.id() != currentRequestId();
  if( newreq )
  {
    cdebug(3)<<"  new request, clearing cache"<<endl;
    // clear cache
    wstate()[AidResult].remove(); 
    res_cache_.detach();
    // change to the current request
    setCurrentRequest(req);
    // do we have a rider record? process it
    if( req[AidRider].exists() )
    {
      const DataRecord &rider = req[AidRider];
      processRequestRider(rider);
      // process rider stuff common to all nodes (setState, etc.)
      // ...
      // none for now
    }
  }
  else // old request -- check the cache and return if it's valid
  {
    if( res_cache_.valid() )
    {
      ref.copy(res_cache_,DMI::PRESERVE_RW);
      cdebug(3)<<"  old request, returning cached result"<<
                 "    "<<ref->sdebug(DebugLevel-1,"    ")<<endl;
      return 0;
    }
    else
    {
      cdebug(3)<<"  old request but cache is empty"<<endl;
    }
  }
  // new request and/or no cache -- recompute the result
  int flags = getResultImpl(ref,req,newreq);
  cdebug(3)<<"  getResultImpl returns flags: "<<flags<<endl;
  cdebug(3)<<"  result is: "<<ref.sdebug(DebugLevel-1,"    ")<<endl;
  if( DebugLevel>3 && ref.valid() )
  {
    for( int i=0; i<ref->numResults(); i++ )
    {
      cdebug(4)<<"  plane "<<i<<": "<<ref->resultConst(i).getValue()<<endl;
    }
  }
  //  cache result in the state record
  if( flags != RES_FAIL && !(flags&RES_WAIT) )
  {
    res_cache_.copy(ref,DMI::PRESERVE_RW);
    wstate()[AidResult] <<= *ref; 
  }
  return flags;
}

// default version does nothing
//##ModelId=3F98D9D2006B
void Node::processRequestRider (const DataRecord &)
{
}

//##ModelId=3F98D9D100B9
int Node::getResultImpl (ResultSet::Ref &, const Request &,bool)
{
  Throw("Meq::Node::getResultImpl not implemented");
}

// throw exceptions for unimplemented DMI functions
//##ModelId=3F5F4363030F
CountedRefTarget* Node::clone(int,int) const
{
  Throw("Meq::Node::clone not implemented");
}

//##ModelId=3F5F43630315
int Node::fromBlock(BlockSet&)
{
  Throw("Meq::Node::fromBlock not implemented");
}

//##ModelId=3F5F43630318
int Node::toBlock(BlockSet &) const
{
  Throw("Meq::Node::toBlock not implemented");
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
    string typestr = nm?nm:objectType().toString();
    append(out,typestr + "(" + name() + ")");
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
           + ( children_[iter->second].valid() 
               ? children_[iter->second]->sdebug(abs(detail)-2)
               : "unresolved" );
    }
  }
  return out;
}

} // namespace Meq
