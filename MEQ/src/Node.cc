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
#include "MeqVocabulary.h"
#include <DMI/BlockSet.h>
#include <DMI/DataRecord.h>
#include <DMI/DataField.h>
#include <DMI/DataArray.h>
#include <algorithm>

namespace Meq {

InitDebugContext(Node,"MeqNode");

//##ModelId=3F5F43E000A0
Node::Node (int nchildren,const HIID *labels)
    : child_labels_(labels),
      check_nchildren_(nchildren)
{
}

//##ModelId=3F5F44A401BC
Node::~Node()
{
}

void Node::checkInitState (DataRecord &rec)
{
  defaultInitField(rec,FName,"");
      // defaultInitField(rec,FNodeIndex,0);
}


// this initializes the children-related fields
void Node::initChildren (int nch)
{
  // check against expected number
  if( check_nchildren_ >= 0 )
  {
    FailWhen( nch != check_nchildren_,
              ssprintf("%d children specified, %d expected",nch,check_nchildren_) );
  }
  else
  {
    FailWhen( nch < -check_nchildren_-1,
              ssprintf("%d children specified, at least %d expected",
              nch,-check_nchildren_-1) );
  }
  children_.resize(nch);
  // form the children name/index fields
  if( nch )
  {
    NestableContainer *p1,*p2;
    // children are labelled: use records
    if( child_labels_ )
    {
      child_indices_ <<= p1 = new DataRecord;
      child_names_ <<= p2 = new DataRecord;
      // set up map from label to child number 
      for( int i=0; i<nch; i++ )
        child_map_[child_labels_[i]] = i;
    }
    // children are unlabelled: use fields
    else
    {
      child_indices_ <<= p1 = new DataField(Tpint,nch);
      child_names_ <<= p2 = new DataField(Tpstring,nch);
      // set up trivial map ("i"->i)
      for( int i=0; i<nch; i++ )
        child_map_[AtomicID(i)] = i;
    }
    wstate()[FChildren].replace() <<= p1;
    wstate()[FChildrenNames].replace() <<= p2;
  }
  else
  {
    wstate()[FChildren].remove();
    wstate()[FChildrenNames].remove();
  }
}

void Node::reinit (DataRecord::Ref::Xfer &initrec, Forest* frst)
{
  cdebug(1)<<"reinitializing node"<<endl;
  forest_ = frst;
  // xfer & privatize the state record -- we don't want anyone
  // changichildrec.size()ng it under us
  DataRecord &rec = staterec_.xfer(initrec).privatize(DMI::WRITE|DMI::DEEP);
  
  // call setStateImpl to set up reconfigurable node state
  cdebug(2)<<"reinitializing node (setStateImpl)"<<endl;
  cdebug(3)<<"state is "<<staterec_().sdebug(10,"    ")<<endl;
  setStateImpl(staterec_(),true);
  
  // set num children based on the FChildren field
  cdebug(2)<<"reinitializing node children"<<endl;
  // set node index, if specified
  if( rec[FChildren].exists() )
  {
    child_indices_ = rec[FChildren].ref(DMI::WRITE);
    child_names_ = rec[FChildrenNames].ref(DMI::WRITE);
    int nch = child_indices_->size();
    children_.resize(nch);
    for( int i=0; i<nch; i++ )
    {
      if( child_labels_ )
        child_map_[child_labels_[i]] = i;
      else
        child_map_[AtomicID(i)] = i;
    }
    cdebug(2)<<"reinitialized with "<<children_.size()<<" children"<<endl;
  }
  else
  {
    cdebug(2)<<"no children to reintialize"<<endl;
  }
}  

//##ModelId=3F5F45D202D5
void Node::init (DataRecord::Ref::Xfer &initrec, Forest* frst)
{
  cdebug(1)<<"initializing node"<<endl;
  forest_ = frst;
  // xfer & privatize the state record -- we don't want anyone
  // changichildrec.size()ng it under us
  DataRecord &rec = staterec_.xfer(initrec).privatize(DMI::WRITE|DMI::DEEP);
  
  // set defaults and check for missing fields
  cdebug(2)<<"initializing node (checkInitState)"<<endl;
  // add node class if needed, else check for consistency
  if( rec[FClass].exists() )
  {
    FailWhen(strlowercase(rec[FClass].as<string>()) != strlowercase(objectType().toString()),
      "node class does not match initrec.class. This is not supposed to happen!");
  }
  else
    rec[FClass] = objectType().toString();
  // do other checks
  checkInitState(rec);
  
  // call setStateImpl to set up reconfigurable node state
  cdebug(2)<<"initializing node (setStateImpl)"<<endl;
  cdebug(3)<<"initial state is "<<staterec_().sdebug(10,"    ")<<endl;
  setStateImpl(staterec_(),true);
  
  // setup the non-reconfigurable stuff
  cdebug(2)<<"initializing node (others)"<<endl;
  // set node index, if specified
  if( rec[FNodeIndex].exists() )
    node_index_ = rec[FNodeIndex].as<int>();
  // setup child nodes, if specified
  if( rec[FChildren].exists() )
  {
    ObjRef ref = rec[FChildren].remove();
    // children specified via a record
    if( ref->objectType() == TpDataRecord )
    {
      DataRecord &childrec = ref.ref_cast<DataRecord>();
      initChildren(childrec.size());
      // iterate through children record and create the child nodes
      DataRecord::Iterator iter = childrec.initFieldIter();
      HIID id;
      int ifield = 0;
      NestableContainer::Ref child_ref;
      while( childrec.getFieldIter(iter,id,child_ref) )
      {
        // if child labels are not specified, use the field number instead
        processChildSpec(childrec,child_labels_ ? id : AtomicID(ifield),id );
        ifield++;
      }
    }
    else if( ref->objectType() == TpDataField )
    {
      DataField &childrec = ref.ref_cast<DataField>();
      initChildren(childrec.size());
      for( int i=0; i<childrec.size(); i++ )
        processChildSpec(childrec,AtomicID(i),AtomicID(i));
    }
    else if( ref->objectType() == TpDataArray )
    {
      DataArray &childarr = ref.ref_cast<DataArray>();
      FailWhen(childarr.rank()!=1,"illegal child array");
      int nch = childarr.shape()[0];
      initChildren(nch);
      for( int i=0; i<nch; i++ )
        processChildSpec(childarr,AtomicID(i),AtomicID(i));
    }
    cdebug(2)<<numChildren()<<" children"<<endl;
  }
}

void Node::setStateImpl (DataRecord &rec,bool initializing)
{
  // if not initializing, check for immutable fields
  if( !initializing )
  {
    protectStateField(rec,FClass);
    protectStateField(rec,FChildren);
    protectStateField(rec,FNodeIndex);
  }
  // set/clear cached result
  //   the cache_result field must be either a Result object,
  //   or a boolean false to clear the cache. Else throw exception.
  TypeId type = rec[FCacheResult].type();
  if( type == TpMeqResult ) // a result
    cache_result_ <<= rec[FCacheResult].as_wp<Result>();
  else if( type == Tpbool && !rec[FCacheResult].as<bool>() ) // a bool False
    cache_result_.detach();
  else if( type != 0 ) // anything else (if type=0, then field is missing)
  {
    NodeThrow(FailWithCleanup,"illegal state."+FCacheResult.toString()+" field");
  }
  // set the name
  getStateField(myname_,rec,FName);
  // set the caching policy
  //      TBD
  // set config groups
  if( rec[FConfigGroups].exists() )
  {
    config_groups_ = rec[FConfigGroups].as_vector<HIID>();
    // the "All" group is defined for every node
    config_groups_.push_back(FAll);
  }
  // set current request ID
  getStateField(current_reqid_,rec,FRequestId);
  // set cache resultcode
  getStateField(cache_retcode_,rec,FCacheResultCode);
}

//##ModelId=3F5F445A00AC
void Node::setState (DataRecord &rec)
{
  // lock records until we're through
  Thread::Mutex::Lock lock(rec.mutex()),lock2(state().mutex());
  // when initializing, we're called with our own state record, which
  // makes the rules somewhat different:
  bool initializing = ( &rec == &(wstate()) );
  cdebug(2)<<"setState(init="<<initializing<<"): "<<rec.sdebug(10)<<endl;
  string fail;
  // setStateImpl() is allowed to throw exceptions if something goes wrong.
  // This may leave the node with an inconsistency between the state record
  // and internal state. To recover from this, we can call setStateImpl() with
  // the current state record to reset the node state.
  // If the exception occurs before any change of state, then no cleanup is 
  // needed. Implementations may throw a FailWithoutCleanup exception to
  // indicate this.
  try
  {
    setStateImpl(rec,initializing);
  }
  catch( FailWithoutCleanup &exc )
  {
    throw exc; // No cleanup required, just re-throw
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
    // reset the state by reinitializing with the state record (this is
    // obviously pointless if we were initializing to begin with). Note
    // that an exception from this call indicates that the node is well 
    // & truly fscked (a good node should always be reinitializable), so
    // we might as well let the caller deal with it.
    if( !initializing )
      setStateImpl(wstate(),true);
    Throw(fail); // rethrow the fail
  }
  else // success
  {
    // success: merge record into state record; deep-privatize for writing 
    if( !initializing )
      wstate().merge(rec,True,DMI::PRIVATIZE|DMI::WRITE|DMI::DEEP);
  }
}

//##ModelId=3F9505E50010
void Node::processChildSpec (NestableContainer &children,const HIID &chid,const HIID &id)
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
      addChild(chid,&child);
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
          addChild(chid,&child);
        }
        else
        { // defer until later if not found
          cdebug(2)<<"  child "<<id<<"="<<name<<" currently unresolved"<<endl;
          addChild(chid,0);
          // add to child names so that we remember the name at least 
          child_names_()[chid] = name;
        }
      }
    }
    // child specified by index -- just get & attach it directly
    else if( spec_type == Tpint )
    {
      int index = children[id];
      Node &child = forest_->get(index);
      cdebug(2)<<"  child "<<id<<"="<<index<<endl;
      addChild(chid,&child);
    }
    else
      Throw("illegal specification for child "+id.toString()+" (type "+
            spec_type.toString()+")");
  }
}

void Node::setNodeIndex (int nodeindex)
{
  wstate()[FNodeIndex] = node_index_ = nodeindex;
}

//##ModelId=3F8433C20193
void Node::addChild (const HIID &id,Node *childnode)
{
  int ich;
  // numeric id is simply child number
  if( id.length() == 1 && id[0].id() >= 0 )
  {
    ich = id[0].id();
    FailWhen(ich<0 || ich>numChildren(),"child number "+id.toString()+" is out of range");
  }
  else // non-numeric: look in in child labels
  {
    FailWhen(!child_labels_,"node does not define child labels, "
      "can't specify child as "+id.toString());
    // look for id within child labels
    const HIID *lbl = std::find(child_labels_,child_labels_+numChildren(),id);
    FailWhen(lbl == child_labels_+numChildren(),
        id.toString() + ": unknown child label");
    ich = lbl - child_labels_;
  }
  // attach ref to child if specified (will stay unresolved otherwise)
  if( childnode )
  {
    children_[ich].attach(childnode,DMI::WRITE);
    child_names_()[id] = childnode->name();
    child_indices_()[id] = childnode->nodeIndex();
  }
  cdebug(3)<<"added child "<<ich<<": "<<id<<endl;
}

// relink children -- resets pointers to all children. This is called
// after restoring a node from a file. 
void Node::relinkChildren ()
{
  for( int i=0; i<numChildren(); i++ )
  {
    if( child_labels_ )
      children_[i].attach(forest().get((*child_indices_)[child_labels_[i]]),DMI::WRITE);
    else
      children_[i].attach(forest().get((*child_indices_)[i]),DMI::WRITE);
  }
  checkChildren();
}

//##ModelId=3F83FAC80375
void Node::resolveChildren ()
{
  cdebug(2)<<"resolving children\n";
  for( int i=0; i<numChildren(); i++ )
  {
    if( !children_[i].valid() )
    {
      string name;
      if( child_labels_ )
        name = (*child_names_)[child_labels_[i]].as<string>();
      else
        name = (*child_names_)[i].as<string>();
      cdebug(3)<<"resolving child "<<i<<":"<<name<<endl;
      // findNode() will throw an exception if the node is not found,
      // which is exactly what we want
      try
      {
        Node &childnode = forest_->findNode(name);
        children_[i].attach(childnode,DMI::WRITE);
        if( child_labels_ )
          child_indices_()[child_labels_[i]] = childnode.nodeIndex();
        else
          child_indices_()[i] = childnode.nodeIndex();
      }
      catch( ... )
      {
        Throw(Debug::ssprintf("failed to resolve child %d:%s",i,name.c_str()));
      }
    }
    // recursively call resolve on the children
    children_[i]().resolveChildren();
  }
  // check children for consistency
  checkChildren();
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

void Node::setCurrentRequest (const Request &req)
{
  wstate()[FRequestId].replace() = current_reqid_ = req.id();
}

void Node::clearCache (bool recursive)
{
  cache_result_.detach();
  wstate()[FCacheResult].replace() = false;
  wstate()[FCacheResultCode].replace() = cache_retcode_ = 0;
  if( recursive )
  {
    for( int i=0; i<numChildren(); i++ )
      getChild(i).clearCache(true);
  }
}

// 
bool Node::getCachedResult (int &retcode,Result::Ref &ref,const Request &req)
{
  // no cache -- return false
  if( !cache_result_.valid() )
    return false;
  // Do the request Ids match? Return cached result then
  // (note that an empty reqid never matches, hence it can be used to 
  // always force a recalculation)
  if( !current_reqid_.empty() && cache_result_.valid() && 
      req.id() == current_reqid_ )
  {
    ref.copy(cache_result_,DMI::PRESERVE_RW);
    retcode = cache_retcode_;
    return true;
  }
  // no match -- clear cache and return 
  clearCache(false);
  return false; 
}

// stores result in cache as per current policy, returns retcode
int Node::cacheResult (const Result::Ref &ref,int retcode)
{
  // for now, always cache, since we don't implement any other policy
  // NB: perhaps fails should be marked separately?
  cache_result_.copy(ref,DMI::WRITE);
  wstate()[FCacheResult].replace() <<= cache_result_.dewr_p();
  wstate()[FCacheResultCode].replace() = cache_retcode_ = retcode;
  cdebug(3)<<"  caching result with code "<<retcode<<endl;
  return retcode;
}

int Node::pollChildren (std::vector<Result::Ref> &child_results,
                        Result::Ref &resref,
                        const Request &req)
{
  bool cache_result = False;
  int retcode = 0;
  cdebug(3)<<"  calling execute() on "<<numChildren()<<" child nodes"<<endl;
  std::vector<Result *> child_fails; // RES_FAILs from children are kept track of separately
  child_fails.reserve(numChildren());
  int nfails = 0;
  for( int i=0; i<numChildren(); i++ )
  {
    int childcode = getChild(i).execute(child_results[i],req);
    cdebug(4)<<"    child "<<i<<" returns code "<<childcode<<endl;
    retcode |= childcode;
    if( !(childcode&RES_WAIT) && childcode&RES_FAIL )
    {
      Result *pchildres = child_results[i].dewr_p();
      child_fails.push_back(pchildres);
      nfails += pchildres->numFails();
    }
  }
  // if any child has completely failed, return a Result containing all of the fails 
  if( !child_fails.empty() )
  {
    cdebug(3)<<"  got RES_FAIL from children ("<<nfails<<"), returning"<<endl;
    Result &result = resref <<= new Result(nfails,req);
    int ires = 0;
    for( uint i=0; i<child_fails.size(); i++ )
    {
      Result &childres = *(child_fails[i]);
      for( int j=0; j<childres.numVellSets(); j++ )
      {
        VellSet &vs = childres.vellSet(j);
        if( vs.isFail() )
          result.setVellSet(ires++,&vs);
      }
    }
  }
  cdebug(3)<<"  cumulative result code is "<<retcode<<endl;
  return retcode;
} 

//##ModelId=3F6726C4039D
int Node::execute (Result::Ref &ref, const Request &req)
{
  cdebug(3)<<"execute, request ID "<<req.id()<<": "<<req.sdebug(DebugLevel-1,"    ")<<endl;
  // this indicates the current stage (for exception handler)
  string stage;
  try
  {
    int retcode = 0;
    // check the cache, return on match (method will clear on mismatch)
    stage = "checking cache";
    if( getCachedResult(retcode,ref,req) )
    {
        cdebug(3)<<"  cache hit, returning cached code "<<retcode<<" and result:"<<endl<<
                   "    "<<ref->sdebug(DebugLevel-1,"    ")<<endl;
        return retcode;
    }
    // do we have a new request? Empty request id treated as always new
    bool newreq = req.id().empty() || ( req.id() != current_reqid_ );
    if( newreq )
    {
      // check if node is ready to go on to the new request, return WAIT if not
      stage = "calling readyForRequest()";
      if( !readyForRequest(req) )
      {
        cdebug(3)<<"  node not ready for new request, returning RES_WAIT"<<endl;
        return RES_WAIT;
      }
      // set this request as current
      setCurrentRequest(req);
      // check for change-of-state in the request
      if( req[FNodeState].exists() )
      {
        stage = "processing node_state";
        cdebug(3)<<"  processing node_state"<<endl;
        // *** cast away const for now, need to revise this later on
        DataRecord &nodestate = const_cast<DataRecord&>(req[FNodeState].as<DataRecord>());
        for( uint i=0; i<config_groups_.size(); i++ )
        {
          if( nodestate[config_groups_[i]].exists() )
          {
            cdebug(3)<<"    found config group "<<config_groups_[i]<<endl;
            DataRecord &group = nodestate[config_groups_[i]].as_wr<DataRecord>();
            // check for entry nodeindex map
            if( group[FByNodeIndex].exists() && group[FByNodeIndex][nodeIndex()].exists() )
            {
              cdebug(4)<<"    found "<<FByNodeIndex<<"["<<nodeIndex()<<"]"<<endl;
              setState(group[FByNodeIndex][nodeIndex()].as_wr<DataRecord>());
            }
            if( group[FByList].exists() )
            {
              DataField &list = group[FByList].as_wr<DataField>();
              cdebug(3)<<"      checking "<<list.size()<<" list entries"<<endl;
              bool matched = false;
              for( int i=0; i<list.size() && !matched; i++ )
              {
                DataRecord &entry = list[i];
                std::vector<string> names;
                std::vector<int> indices;
                DataRecord &newst = entry[FState];
                if( entry[FName].exists() ) // get list of names, if any
                  names = entry[FName];
                if( entry[FNodeIndex].exists() ) // get list of node indices, if any
                  indices = entry[FNodeIndex];
                cdebug(4)<<"        "<<indices.size()<<" indices, "<<
                           names.size()<<" names"<<endl;
                matched = ( std::find(indices.begin(),indices.end(),nodeIndex())
                              != indices.end() ||
                            std::find(names.begin(),names.end(),name())
                              != names.end() ||
                            std::find(names.begin(),names.end(),"*") 
                              != names.end() );
                if( matched )
                {
                  cdebug(4)<<"        node matched, setting state"<<endl;
                  setState(newst);
                }
              }
              if( !matched ) {
                cdebug(3)<<"      no matches in list"<<endl;
              }
            }
          }
        }
      }
      // check for request rider
      if( req[FRider].exists() )
      {
        stage = "processing rider";
        cdebug(3)<<"  processing request rider"<<endl;
        const DataRecord &rider = req[FRider];
        processRider(rider);
        // process rider stuff common to all nodes (setState, etc.)
        // ...
        // none for now
      }
    } // endif( newreq )
    
    // Pass request on to children and accumulate their results
    std::vector<Result::Ref> child_results(numChildren());
    if( numChildren() )
    {
      stage = "polling children";
      retcode = pollChildren(child_results,ref,req);
      // a WAIT from any child is returned immediately w/o a result
      if( retcode&RES_WAIT )
        return retcode;
      // if failed, then cache & return the fail
      if( retcode&RES_FAIL )
        return cacheResult(ref,retcode);
    }
    
    // does request have a Cells object? Compute our Result then
    if( req.hasCells() )
    {
      stage = "getting result";
      cdebug(3)<<"  calling getResult(): cells are "<<req.cells();
      int code = getResult(ref,child_results,req,newreq);
      retcode |= code;
      cdebug(3)<<"  getResult() returns code "<<code<<", cumulative "<<retcode<<endl;
      // a WAIT is returned immediately with no valid result expected
      if( code&RES_WAIT ) 
        return retcode;
      // else we must have a valid Result object now, even if it's a fail.
      // (in case of RES_FAIL, getResult() should have put a fail in there)
      if( !ref.valid() )
      {
        NodeThrow1("must return a valid Result or else RES_WAIT");
      }
      // Make sure the Cells are in the Result object
      if( !(code&RES_FAIL) && !ref->hasCells() )
        ref().setCells(req.cells());
    }
    else // no cells, ensure an empty result
    {
      ref <<= new Result(0);
      cdebug(3)<<"  empty result; cumulative result code is "<<retcode<<endl;
      return retcode; // no caching of empty results
    }
    // OK, at this point we have a valid Result to return
    if( DebugLevel>=3 ) // print it out
    {
      cdebug(3)<<"  cumulative result code is "<<retcode<<endl;
      cdebug(3)<<"  result is "<<ref.sdebug(DebugLevel-1,"    ")<<endl;
      if( DebugLevel>3 && ref.valid() )
      {
        ref->show(Debug::dbg_stream);
      }
    }
    // cache & return accumulated return code
    return cacheResult(ref,retcode);
  }
  // catch any exceptions, return a single fail result
  catch( std::exception &x )
  {
    ref <<= new Result(1);
    VellSet & res = ref().setNewVellSet(0);
    MakeFailVellSet(res,string("exception in execute() while "+stage+": ")+x.what());
    return cacheResult(ref,RES_FAIL);
  }
}

//##ModelId=3F98D9D100B9
int Node::getResult (Result::Ref &,const std::vector<Result::Ref> &,
                     const Request &,bool)
{
  NodeThrow1("getResult() not implemented");
}


// throw exceptions for unimplemented DMI functions
//##ModelId=3F5F4363030F
CountedRefTarget* Node::clone(int,int) const
{
  NodeThrow1("clone() not implemented");
}

//##ModelId=3F5F43630315
int Node::fromBlock(BlockSet&)
{
  NodeThrow1("fromBlock() not implemented");
}

//##ModelId=3F5F43630318
int Node::toBlock(BlockSet &) const
{
  NodeThrow1("toBlock() not implemented");
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
