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
#include "ResampleMachine.h"
#include "MeqVocabulary.h"
#include <DMI/BlockSet.h>
#include <DMI/DataRecord.h>
#include <DMI/DataField.h>
#include <DMI/DataArray.h>
#include <algorithm>

namespace Meq {

InitDebugContext(Node,"MeqNode");

using Debug::ssprintf;


//##ModelId=3F5F43E000A0
Node::Node (int nchildren,const HIID *labels,int nmandatory)
    : check_nchildren_(nchildren),
      check_nmandatory_(nmandatory),
      depend_mask_(0),
      node_groups_(1,FAll),
      auto_resample_(RESAMPLE_NONE),
      disable_auto_resample_(false)
{
  Assert(nchildren>=0 || !labels);
  Assert(nchildren<0 || nchildren>=nmandatory);
  if( labels )   // copy labels
  {
    child_labels_.resize(nchildren);
    for( int i=0; i<nchildren; i++ )
      child_labels_[i] = labels[i];
  }
  // else child_labels_ stays empty to indicate no labels -- this is checked below
}

//##ModelId=3F5F44A401BC
Node::~Node()
{
}

void Node::setDependMask (int mask)
{
  depend_mask_ = mask;
  if( staterec_.valid() )
    staterec_()[FDependMask] = mask;
  cdebug(3)<<ssprintf("new depend mask is %x\n",depend_mask_);
}

void Node::setKnownSymDeps (const HIID deps[],int ndeps)
{
  known_symdeps_ .assign(deps,deps+ndeps);
  if( staterec_.valid() )
    staterec_()[FKnownSymDeps].replace() = known_symdeps_;
}

void Node::setActiveSymDeps (const HIID deps[],int ndeps)
{
  cdebug(2)<<"setting "<<ndeps<<" active symdeps\n";
  active_symdeps_.assign(deps,deps+ndeps);
  if( known_symdeps_.empty() )
  {
    known_symdeps_ = active_symdeps_;
    if( staterec_.valid() )
      staterec_()[FKnownSymDeps].replace() = known_symdeps_;
  }
  if( staterec_.valid() )
    staterec_()[FActiveSymDeps].replace() = active_symdeps_;
  resetDependMasks();
}

void Node::setGenSymDeps (const HIID symdeps[],const int depmasks[],int ndeps,const HIID &group)
{
  cdebug(2)<<"setting "<<ndeps<<" generated symdeps\n";
  gen_symdep_fullmask_ = 0;
  for( int i=0; i<ndeps; i++ )
  {
    gen_symdep_fullmask_ |= 
        gen_symdep_masks_[symdeps[i]] = depmasks[i];
  }
  gen_symdep_group_ = group;
}

int Node::getGenSymDepMask (const HIID &symdep) const
{
  std::map<HIID,int>::const_iterator iter = gen_symdep_masks_.find(symdep);
  return iter == gen_symdep_masks_.end() ? 0 : iter->second;
}


int Node::computeDependMask (const std::vector<HIID> &symdeps) 
{
  int mask = 0;
  for( uint i=0; i<symdeps.size(); i++ )
  {
    const HIID &id = symdeps[i];
//    cdebug(3)<<"adding symdep "<<id<<ssprintf(": mask %x\n",symdep_masks_[id]);
    mask |= symdep_masks_[id];
  }
  return mask;
}

void Node::resetDependMasks ()
{ 
  setDependMask(computeDependMask(active_symdeps_)); 
}

// this initializes the children-related fields
//##ModelId=400E531F0085
void Node::initChildren (int nch)
{
  // check against expected number
  if( check_nchildren_ >= 0 && !check_nmandatory_ )
  {
    FailWhen( nch != check_nchildren_,
              ssprintf("%d children specified, %d expected",nch,check_nchildren_) );
  }
  FailWhen( nch < check_nmandatory_,
            ssprintf("%d children specified, at least %d expected",
            nch,check_nmandatory_) );
  children_.resize(nch);
  // form the children name/index fields
  if( nch )
  {
    NestableContainer *p1,*p2;
    if( !child_labels_.empty() ) // children are labelled: use records
    {
      child_indices_ <<= p1 = new DataRecord;
      child_names_ <<= p2 = new DataRecord;
    }
    else // children are unlabelled: use fields
    {
      child_indices_ <<= p1 = new DataField(Tpint,nch);
      child_names_ <<= p2 = new DataField(Tpstring,nch);
    }
    // set up map from label to child number 
    // (if no labels are defined, trivial "0", "1", etc. are used)
    for( int i=0; i<nch; i++ )
      child_map_[getChildLabel(i)] = i;
    wstate()[FChildren].replace() <<= p1;
    wstate()[FChildrenNames].replace() <<= p2;
  }
  else
  {
    wstate()[FChildren].remove();
    wstate()[FChildrenNames].remove();
  }
}

//##ModelId=400E530F0090
void Node::reinit (DataRecord::Ref::Xfer &initrec, Forest* frst)
{
  cdebug(1)<<"reinitializing node"<<endl;
  forest_ = frst;
      
  // xfer & privatize the state record -- we don't want anyone
  // changichildrec.size()ng it under us
  DataRecord &rec = staterec_.xfer(initrec).privatize(DMI::WRITE|DMI::DEEP);
  
  // set num children based on the FChildren field
  cdebug(2)<<"reinitializing node children"<<endl;
  // set node index, if specified
  if( rec[FNodeIndex].exists() )
    node_index_ = rec[FNodeIndex].as<int>();
  // set resolve ID, if any
  node_resolve_id_ = rec[FResolveParentId].as<int>(-1);
  
  // setup children directly from relevant fields
  if( rec[FChildren].exists() )
  {
    child_indices_ = rec[FChildren].ref(true);
    child_names_ = rec[FChildrenNames].ref(true);
    int nch = child_indices_->size();
    children_.resize(nch);
    for( int i=0; i<nch; i++ )
      child_map_[getChildLabel(i)] = i;
    rcr_cache_.resize(children_.size());
    cdebug(2)<<"reinitialized with "<<children_.size()<<" children"<<endl;
  }
  else
  {
    cdebug(2)<<"no children to reintialize"<<endl;
  }
  
  // finally, call setStateImpl to set up reconfigurable node state
  cdebug(2)<<"reinitializing node (setStateImpl)"<<endl;
  cdebug(3)<<"state is "<<staterec_().sdebug(10,"    ")<<endl;
  setStateImpl(staterec_(),true);
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
  FailWhen(rec[FResolveParentId].exists(),"can't specify "+FResolveParentId.toString()+" in init record");
  node_resolve_id_ = -1;
  checkInitState(rec);
  
  // setup children
  cdebug(2)<<"initializing node (others)"<<endl;
  // set node index, if specified
  if( rec[FNodeIndex].exists() )
    node_index_ = rec[FNodeIndex].as<int>();
  
  // get children spec. If this is a single boolean False, then ignore
  DataRecord::Hook hchildren(rec,FChildren);
  if( hchildren.type() == Tpbool && hchildren.size() == 1 &&
      !hchildren.as<bool>() )
  {
    cdebug(2)<<"Children=[False], skipping child creation"<<endl;
  }
  // Not [F}, so go on to process children
  else if( hchildren.exists() )
  {
    ObjRef ref = hchildren.remove();
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
        processChildSpec(childrec,child_labels_.empty() ? AtomicID(ifield) : id,id );
        ifield++;
      }
    }
    else if( ref->objectType() == TpDataField || ref->objectType() == TpDataList )
    {
      NestableContainer &childrec = ref.ref_cast<NestableContainer>();
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
    // if a mandatory number of children (NM) is requested, make sure
    // that the first NM children are set
    if( check_nmandatory_ )
    {
      FailWhen(children_.size()<uint(check_nmandatory_),"too few children specified");
      for( int i=0; i<check_nmandatory_; i++ )
        if( !children_[i].valid() )
        {
          Throw("mandatory child "+getChildLabel(i).toString()+" not specified" );
        }
    }
    rcr_cache_.resize(children_.size());
    cdebug(2)<<numChildren()<<" children"<<endl;
  }
  
  // finally, call setStateImpl to set up reconfigurable node state
  cdebug(2)<<"initializing node (setStateImpl)"<<endl;
  cdebug(3)<<"initial state is "<<staterec_().sdebug(10,"    ")<<endl;
  setStateImpl(staterec_(),true);
}

//##ModelId=400E531402D1
void Node::setStateImpl (DataRecord &rec,bool initializing)
{
  // if not initializing, check for immutable fields
  if( !initializing )
  {
    protectStateField(rec,FClass);
    protectStateField(rec,FChildren);
    protectStateField(rec,FNodeIndex);
    protectStateField(rec,FResolveParentId);
  }
  // set/clear cached result
  //   the cache_result field must be either a Result object,
  //   or a boolean false to clear the cache. Else throw exception.
  DataRecord::Hook hcache(rec,FCacheResult);
  TypeId type = hcache.type();
  if( type == TpMeqResult ) // a result
    cache_result_ <<= hcache.as_wp<Result>();
  else if( type == Tpbool && !hcache.as<bool>() ) // a bool False
    cache_result_.detach();
  else if( type != 0 ) // anything else (if type=0, then field is missing)
  {
    NodeThrow(FailWithCleanup,"illegal state."+FCacheResult.toString()+" field");
  }
  // set the name
  rec[FName].get(myname_,initializing);
  // set the caching policy
  //      TBD
  
  // get known symdeps
  rec[FKnownSymDeps].get_vector(known_symdeps_,initializing && !known_symdeps_.empty());
  // get symdep masks, if specified
  DataRecord::Hook hdepmasks(rec,FSymDepMasks);
  if( hdepmasks.exists() )
  {
    symdep_masks_.clear();
    if( hdepmasks.type() == TpDataRecord )
    {
      cdebug(2)<<"new symdep_masks set via state\n";
      const DataRecord &maskrec = hdepmasks;
      for( uint i=0; i<known_symdeps_.size(); i++ )
      {
        const HIID &id = known_symdeps_[i];
        symdep_masks_[id] = maskrec[id].as<int>(0);
      }
      resetDependMasks();
    }
    else // not a record, clear everything
    {
      cdebug(2)<<"symdep_masks cleared via state\n";
      resetDependMasks();
    }
  }
  // recompute depmask if active sysdeps change
  if( rec[FActiveSymDeps].get_vector(active_symdeps_,initializing && !known_symdeps_.empty()) )
  {
    cdebug(2)<<"active_symdeps set via state\n";
    resetDependMasks();
  }
  // get generated symdeps, if any are specified
  DataRecord::Hook genhook(rec,FGenSymDep);
  if( genhook.exists() )
  {
    try 
    {
      const DataRecord &deps = genhook.as<DataRecord>();
      std::map<HIID,int>::iterator iter = gen_symdep_masks_.begin();
      gen_symdep_fullmask_ = 0;
      for( ; iter != gen_symdep_masks_.end(); iter++ )
        gen_symdep_fullmask_ |= iter->second = deps[iter->first].as<int>();
    } 
    catch( std::exception & )
    {
      NodeThrow(FailWithCleanup,
          "incorrect or incomplete "+FGenSymDep.toString()+" state field");
    }
  }
  // else place them into data record
  else if( initializing && !gen_symdep_masks_.empty() )
  {
    DataRecord &deps = genhook <<= new DataRecord;
    std::map<HIID,int>::const_iterator iter = gen_symdep_masks_.begin();
    for( ; iter != gen_symdep_masks_.end(); iter++ )
      deps[iter->first] = iter->second;
  }
  // get generated symdep group, if specified
  rec[FGenSymDepGroup].get(gen_symdep_group_,initializing && !gen_symdep_masks_.empty());
  
  // now set the dependency mask if specified; this will override
  // possible modifications made above
  rec[FDependMask].get(depend_mask_,initializing);
  
  // set node groups, but always implicitly insert "All" at start
  std::vector<HIID> ngr;
  if( rec[FNodeGroups].get_vector(ngr) )
  {
    node_groups_.resize(ngr.size()+1);
    node_groups_.front() = FAll;
    for( uint i=0; i<ngr.size(); i++ )
      node_groups_[i+1] = ngr[i];
  }
  
  // set current request ID
  rec[FRequestId].get(current_reqid_);
  // set cache resultcode
  rec[FCacheResultCode].get(cache_retcode_);
  // set auto-resample mode
  int ars = auto_resample_;
  if( rec[FAutoResample].get(ars,initializing) )
  {
    if( disable_auto_resample_ && ars != RESAMPLE_NONE )
    {
      NodeThrow(FailWithCleanup,"can't use auto-resampling with this node");
    }
    auto_resample_ = ars;
  }
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
    // we might as well re-throw itm, letting the caller deal with it.
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
    DataRecord::Ref child_initrec = children[id].ref();
    // check if named child already exists
    string name = child_initrec[FName].as<string>("");
    int index = -1;
    if( !name.empty() && ( index = forest_->findIndex(name) ) >= 0 )
    {
      cdebug(4)<<"  child already exists as #"<<index<<endl;
      // If link_or_create=T, we allow this, otherwise, throw exception
      if( !child_initrec[FLinkOrCreate].as<bool>(false) )
      {
        Throw("Failed to create child node "+id.toString()+": a node named '"
              +name+"' already exists");
      }
      Node &child = forest_->get(index);
      cdebug(2)<<"  child "<<id<<"="<<name<<" relinked as #"<<index<<endl;
      addChild(chid,&child);
    }
    else
    {
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

//##ModelId=400E53120082
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
    // look for id within child labels
    vector<HIID>::const_iterator lbl;
    lbl = std::find(child_labels_.begin(),child_labels_.end(),id);
    FailWhen(lbl == child_labels_.end(),id.toString() + ": unknown child label");
    ich = lbl - child_labels_.begin();
  }
  // attach ref to child if specified (will stay unresolved otherwise)
  if( childnode )
  {
    children_[ich].attach(childnode,DMI::WRITE);
    child_names_()[getChildLabel(ich)] = childnode->name();
    child_indices_()[getChildLabel(ich)] = childnode->nodeIndex();
  }
  cdebug(3)<<"added child "<<ich<<": "<<id<<endl;
}

// relink children -- resets pointers to all children. This is called
// after restoring a node from a file. 
//##ModelId=400E531101C8
void Node::relinkChildren ()
{
  for( int i=0; i<numChildren(); i++ )
  {
    children_[i].attach(forest().get((*child_indices_)[getChildLabel(i)]),DMI::WRITE);
  }
  checkChildren();
}

//##ModelId=3F83FAC80375
void Node::resolveChildren (bool recursive)
{
  cdebug(2)<<"resolving children\n";
  for( int i=0; i<numChildren(); i++ )
  {
    if( !children_[i].valid() )
    {
      HIID label = getChildLabel(i);
      string name = (*child_names_)[label].as<string>();
      cdebug(3)<<"resolving child "<<i<<":"<<name<<endl;
      // findNode() will throw an exception if the node is not found,
      // which is exactly what we want
      try
      {
        Node &childnode = forest_->findNode(name);
        children_[i].attach(childnode,DMI::WRITE);
        child_indices_()[label] = childnode.nodeIndex();
      }
      catch( ... )
      {
        Throw(Debug::ssprintf("failed to resolve child %d:%s",i,name.c_str()));
      }
    }
    // recursively call resolve on the children
    if( recursive )
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

//##ModelId=3F9919B10014
void Node::setCurrentRequest (const Request &req)
{
  wstate()[FRequest].replace().put(req,DMI::READONLY);
  wstate()[FRequestId].replace() = current_reqid_ = req.id();
}

//##ModelId=400E531300C8
void Node::clearCache (bool recursive)
{
  cache_result_.detach();
  wstate()[FCacheResult].replace() = false;
  wstate()[FCacheResultCode].replace() = cache_retcode_ = 0;
  wstate()[FRequestId].replace() = current_reqid_ = HIID();
  wstate()[FRequest].remove();
  clearRCRCache();
  if( recursive )
  {
    for( int i=0; i<numChildren(); i++ )
      getChild(i).clearCache(true);
  }
}

//##ModelId=400E531A021A
bool Node::getCachedResult (int &retcode,Result::Ref &ref,const Request &req)
{
  // no cache -- return false
  if( !cache_result_.valid() )
    return false;
  // Check that cached result is applicable:
  // (1) An empty reqid never matches, hence it can be used to 
  //     always force a recalculation.
  // (2) A cached RES_VOLATILE code requires an exact ID match
  //     (i.e. volatile results recomputed for any different request)
  // (3) Otherwise, do a masked compare using the cached result code
  if( !req.id().empty() &&
      (cache_retcode_&RES_VOLATILE 
        ? req.id() == current_reqid_
        : maskedCompare(req.id(),current_reqid_,cache_retcode_) ) )
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
//##ModelId=400E531C0200
int Node::cacheResult (const Result::Ref &ref,int retcode)
{
  // clear the updated flag from cached results
  retcode &= ~RES_UPDATED;
  // for now, always cache, since we don't implement any other policy
  // NB: perhaps fails should be marked separately?
  cache_result_.copy(ref);
  wstate()[FCacheResult].replace() <<= cache_result_.deref_p();
  wstate()[FCacheResultCode].replace() = cache_retcode_ = retcode;
  cdebug(3)<<"  caching result with code "<<ssprintf("0x%x",retcode)<<endl;
  // publish current state to all result subscribers
  if( result_event_gen_.active() )
    result_event_gen_.generateEvent(staterec_.copy());  
  // NB***: if we don't cache the result, we have to publish it regardless
  // this is to be implemented later, with caching policies
  return retcode;
}

bool Node::checkRCRCache (Result::Ref &ref,int ich,const Cells &cells)
{
  if( ich<0 || ich>=int(rcr_cache_.size()) || !rcr_cache_[ich].valid() )
    return false;
  // check if resolution of cached result matches the request
  if( cells.compare(rcr_cache_[ich]->cells()) )
  {
    rcr_cache_[ich].detach();
    return false;
  }
  // match, return true
  ref.copy(rcr_cache_[ich]);
  return true;
}

void Node::clearRCRCache (int ich)
{
  if( ich<0 ) // clear all
  {
    for( int i=0; i<numChildren(); i++ )
      rcr_cache_[i].detach();
  }
  else
    rcr_cache_[ich].detach();
}

void Node::cacheRCR (int ich,const Result::Ref::Copy &res)
{
  if( ich >= int(rcr_cache_.size()) )
    rcr_cache_.resize(ich+1);
  rcr_cache_[ich].copy(res);
  // at this point we can perhaps tell the child to release cache, if there's
  // no change expected. Still have to think this through
}

void Node::addResultSubscriber (const EventSlot &slot)
{
  result_event_gen_.addSlot(slot);
  cdebug(2)<<"added result subscription "<<slot.evId().id()<<":"<<slot.recepient()<<endl;
}

void Node::removeResultSubscriber (const EventRecepient *recepient)
{
  result_event_gen_.removeSlot(recepient);
  cdebug(2)<<"removing all subscriptions for "<<recepient<<endl;
}

void Node::removeResultSubscriber (const EventSlot &slot)
{
  result_event_gen_.removeSlot(slot);
  cdebug(2)<<"removing result subscriber "<<slot.evId().id()<<":"<<slot.recepient()<<endl;
}

void Node::resampleChildren (Cells::Ref rescells,std::vector<Result::Ref> &childres)
{
  if( auto_resample_ == RESAMPLE_NONE )
    return;
  const Cells *pcells = 0;
  rescells.detach();
//  rescells <<= pcells = &( childres[0]->cells() );
  bool need_resampling = false;
  for( uint ich=0; ich<childres.size(); ich++ )
  {
    const Result &chres = *childres[ich];
    if( chres.hasCells() )
    {
      const Cells &cc = childres[ich]->cells();
      if( !pcells ) // first cells? Init pcells with it
        rescells <<= pcells = &cc;
      else
      {
        // check if resolution matches
        int res = pcells->compare(cc);
        if( res<0 )       // result<0: domains differ, fail
        {
          NodeThrow1("domains of child results do not match");
        }
        else if( res>0 )  // result>0: domains same, resolutions differ
        {
          // fail if auto-resampling is disabled
          if( auto_resample_ == RESAMPLE_FAIL )
          {
            NodeThrow1("resolutions of child results do not match and auto-resampling is disabled");
          }
          else 
          // generate new output Cells by upsampling or integrating
          // the special Cells constructor will do the right thing for us, according
          // to the auto_resample_ setting
          {
            cdebug(3)<<"child result "<<ich<<" has different resolution\n";
            rescells <<= pcells = new Cells(*pcells,cc,auto_resample_);
            need_resampling = true;
          }
        }
      }
    }
  }
  // resample child results if required
  if( need_resampling )
  {
    cdebug(3)<<"resampling child results to "<<*pcells<<endl;
    ResampleMachine resample(*pcells);
    for( uint ich=0; ich<childres.size(); ich++ )
    {
      if( childres[ich]->hasCells() )
      {
        resample.setInputRes(childres[ich]->cells());
        if( resample.isIdentical() ) // child at correct resolution already
        {
          cdebug(3)<<"child "<<ich<<": already at this resolution\n";
          // clear resample cache for this child
          clearRCRCache(ich);
        }
        else
        {
          // check if resampled-child cache already contains the resampled result
          if( !checkRCRCache(childres[ich],ich,*pcells) )
          {
            cdebug(3)<<"child "<<ich<<": resampling\n";
            // privatize child result for writing
            Result &chres = childres[ich].privatize(DMI::WRITE)(); 
            chres.setCells(pcells);
            // resample and cache the child result 
            for( int ivs=0; ivs<chres.numVellSets(); ivs++ )
            {
              VellSet::Ref ref;
              resample.apply(ref,chres.vellSetRef(ivs),chres.isIntegrated());
              chres.setVellSet(ivs,ref);
            }
            cacheRCR(ich,childres[ich]);
          }
          else
          {
            cdebug(3)<<"child "<<ich<<": already cached at this resolution, reusing\n";
          }
        }
      }
    }
  }
  else // no resampling needed, clear cache of all resampled children
    clearRCRCache();
}

//##ModelId=400E531702FD
int Node::pollChildren (std::vector<Result::Ref> &child_results,
                        Result::Ref &resref,
                        const Request &req)
{
  bool cache_result = False;
  int retcode = 0;
  cdebug(3)<<"  calling execute() on "<<numChildren()<<" child nodes"<<endl;
  std::vector<const Result *> child_fails; // RES_FAILs from children are kept track of separately
  child_fails.reserve(numChildren());
  int nfails = 0;
  for( int i=0; i<numChildren(); i++ )
  {
    int childcode = getChild(i).execute(child_results[i],req);
    cdebug(4)<<"    child "<<i<<" returns code "<<ssprintf("0x%x",childcode)<<endl;
    retcode |= childcode;
    if( !(childcode&RES_WAIT) && childcode&RES_FAIL )
    {
      const Result *pchildres = child_results[i].deref_p();
      child_fails.push_back(pchildres);
      nfails += pchildres->numFails();
    }
    // if child is updated, clear resampled result cache
    if( childcode&RES_UPDATED )
      clearRCRCache(i);
  }
  // if any child has completely failed, return a Result containing all of the fails 
  if( !child_fails.empty() )
  {
    cdebug(3)<<"  got RES_FAIL from children ("<<nfails<<"), returning"<<endl;
    Result &result = resref <<= new Result(nfails,req);
    int ires = 0;
    for( uint i=0; i<child_fails.size(); i++ )
    {
      const Result &childres = *(child_fails[i]);
      for( int j=0; j<childres.numVellSets(); j++ )
      {
        const VellSet &vs = childres.vellSet(j);
        if( vs.isFail() )
          result.setVellSet(ires++,&vs);
      }
    }
  }
  cdebug(3)<<"  cumulative result code is "<<ssprintf("0x%x",retcode)<<endl;
  return retcode;
} 

int Node::resolve (DataRecord::Ref &depmasks,int rpid)
{
  // if node already resolved with this parent ID, do nothing
  if( node_resolve_id_ == rpid )
  {
    cdebug(4)<<"node already resolved for rpid "<<rpid<<endl;
    return 0;
  }
  cdebug(3)<<"resolving node, rpid="<<rpid<<endl;
  wstate()[FResolveParentId] = node_resolve_id_ = rpid;
  // resolve children
  resolveChildren(false);
  // process depmasks 
  if( !known_symdeps_.empty() )
  {
    cdebug(3)<<"checking for "<<known_symdeps_.size()<<" known symdeps\n";
    const DataRecord &rec = *depmasks;
    bool changed = false;
    for( uint i=0; i<node_groups_.size(); i++ )
    {
      DataRecord::Hook hgroup(rec,node_groups_[i]);
      if( hgroup.exists() )
      {
        cdebug(4)<<"found symdeps for group "<<node_groups_[i]<<endl;
        const DataRecord &grouprec = hgroup.as<DataRecord>();
        for( uint i=0; i<known_symdeps_.size(); i++ )
        {
          const HIID &id = known_symdeps_[i];
          int mask;
          if( grouprec[id].get(mask) )
          {
            // add to its mask, if the symdep is present in the record.
            symdep_masks_[id] |= mask;
            cdebug(4)<<"symdep_mask["<<id<<"]="<<ssprintf("%x\n",symdep_masks_[id]);
            changed = true;
          }
        }
      }
    }
    // recompute stuff if anything has changed
    if( changed )
    {
      cdebug(3)<<"recomputing depmasks\n"<<endl;
      // recompute the active depend mask
      resetDependMasks();
      // reset subrecord in state rec
      DataRecord &known = wstate()[FSymDepMasks].replace() <<= new DataRecord;
      for( uint i=0; i<known_symdeps_.size(); i++ )
        known[known_symdeps_[i]] = symdep_masks_[known_symdeps_[i]];
    }
  }
  // add our own generated symdeps, if any. This changes the record, so
  // privatize it
  if( !gen_symdep_masks_.empty() )
  {
    rpid = nodeIndex(); // change the rpid
    depmasks.privatize(DMI::WRITE);
    const HIID &group = gen_symdep_group_.empty() ? FAll : gen_symdep_group_;
    cdebug(3)<<"inserting generated symdeps for group "<<group<<endl;
    DataRecord &grouprec = Rider::getOrInit(depmasks(),group);
    std::map<HIID,int>::const_iterator iter = gen_symdep_masks_.begin();
    for( ; iter != gen_symdep_masks_.end(); iter++ )
    {
      DataRecord::Hook hook(grouprec,iter->first);
      if( hook.exists() )
        hook.as_wr<int>() |=  iter->second;
      else
        hook = iter->second;
    }
    depmasks.privatize(DMI::READONLY|DMI::DEEP);
  }
  // pass recursively onto children
  for( int i=0; i<numChildren(); i++ )
    children_[i]().resolve(depmasks,rpid);
  return 0;
}

// process Node-specific commands
int Node::processCommands (const DataRecord &rec,Request::Ref &reqref)
{
  bool generate_symdeps = false;
  // process the Resolve.Children command: call resolve children
  // non-recursively (since the request + command is going up 
  // recursively anyway)
  if( rec[FResolveChildren].as<bool>(false) )
  {
    cdebug(4)<<"processCommands("<<FResolveChildren<<")\n";
    resolveChildren(false);
  }
  // process the "State" command: change node state
  DataRecord::Hook hstate(rec,FState);
  if( hstate.exists() )
  {
    cdebug(4)<<"processCommands("<<FState<<"): calling setState()"<<endl;
    setState(hstate.as_wr<DataRecord>());
  }
  // process the "Clear.Dep.Mask" command: flush known symdep masks and
  // set our mask to 0
  if( rec[FClearDepMask].as<bool>(false) )
  {
    cdebug(2)<<"processCommands("<<FClearDepMask<<"): clearing symdep_masks"<<endl;
    symdep_masks_.clear();
    wstate()[FSymDepMasks].remove();
    setDependMask(0);
  }
  // process the "Add.Dep.Mask" command, if we track any symdeps
  DataRecord::Hook hdep(rec,FAddDepMask);
  if( hdep.exists() )
  {
    if( !known_symdeps_.empty() && hdep.type() == TpDataRecord )
    {
      cdebug(2)<<"processCommands("<<FAddDepMask<<"): checking for masks\n";
      const DataRecord &deprec = hdep;
      // reinit the sysdep_masks field in the state record as we go along
      DataRecord &known = wstate()[FSymDepMasks].replace() <<= new DataRecord;
      for( uint i=0; i<known_symdeps_.size(); i++ )
      {
        const HIID &id = known_symdeps_[i];
        // add to its mask, if the symdep is present in the record.
        known[id] = symdep_masks_[id] |= deprec[id].as<int>(0);
        cdebug(3)<<"symdep_mask["<<id<<"]="<<ssprintf("%x\n",symdep_masks_[id]);
      } 
      // recompute the active depend mask
      resetDependMasks();
    }
  }
  // Init.Dep.Mask command: add our own symdeps to the request rider
  // (by inserting Add.Dep.Mask commands)
  if( rec[FInitDepMask].as<bool>(false) && !gen_symdep_masks_.empty() )
  {
    const HIID &group = gen_symdep_group_.empty() ? FAll : gen_symdep_group_;
    DataRecord &cmdrec = Rider::getCmdRec_All(reqref,group);
    DataRecord &deprec = Rider::getOrInit(cmdrec,FAddDepMask);
    std::map<HIID,int>::const_iterator iter = gen_symdep_masks_.begin();
    for( ; iter != gen_symdep_masks_.end(); iter++ )
    {
      DataRecord::Hook hook(deprec,iter->first);
      if( hook.exists() )
        hook.as_wr<int>() |=  iter->second;
      else
        hook = iter->second;
    }
  }
//  // should never cache a processCommand() result
// or should we? I think we should (if only to ignore the same command
// coming from multiple parents)
  return RES_VOLATILE;
}

//##ModelId=3F6726C4039D
int Node::execute (Result::Ref &ref,const Request &req0)
{
  DbgFailWhen(!req0.getOwner(),"Request object must have at least one ref attached");
  cdebug(3)<<"execute, request ID "<<req0.id()<<": "<<req0.sdebug(DebugLevel-1,"    ")<<endl;
  FailWhen(node_resolve_id_<0,"execute() called before resolve()");
  // this indicates the current stage (for exception handler)
  string stage;
  try
  {
    int retcode = 0;
    // check the cache, return on match (method will clear on mismatch)
    stage = "checking cache";
    if( getCachedResult(retcode,ref,req0) )
    {
        cdebug(3)<<"  cache hit, returning cached code "<<ssprintf("0x%x",retcode)<<" and result:"<<endl<<
                   "    "<<ref->sdebug(DebugLevel-1,"    ")<<endl;
        return retcode;
    }
    // do we have a new request? Empty request id treated as always new
    bool newreq = req0.id().empty() || ( req0.id() != current_reqid_ );
    // attach a ref to the request; processRequestRider() is allowed to modify
    // the request; this will result in a copy-on-write operation on this ref
    Request::Ref reqref(req0,DMI::READONLY);
    if( newreq )
    {
      // check if node is ready to go on to the new request, return WAIT if not
      stage = "calling readyForRequest()";
      if( !readyForRequest(req0) )
      {
        cdebug(3)<<"  node not ready for new request, returning RES_WAIT"<<endl;
        return RES_WAIT;
      }
      // set this request as current
      setCurrentRequest(req0);
      // check for request riders
      if( req0.hasRider() )
        retcode = processRequestRider(reqref);
    } // endif( newreq )
    // in case processRequestRider modified the request, work with the new
    // request object from now on
    const Request &req = *reqref;
    // clear the retcode if the request has cells, children code + getResult() 
    // will be considered the real result
    if( req.hasCells() )
      retcode = 0;
    // Pass request on to children and accumulate their results
    std::vector<Result::Ref> child_results(numChildren());
    Cells::Ref rescells;
    if( numChildren() )
    {
      stage = "polling children";
      retcode |= pollChildren(child_results,ref,req);
      // a WAIT from any child is returned immediately w/o a result
      if( retcode&RES_WAIT )
        return retcode;
      // if failed, then cache & return the fail
      if( retcode&RES_FAIL )
        return cacheResult(ref,retcode) | RES_UPDATED;
      // resample children (will do nothing if disabled)
      resampleChildren(rescells,child_results);
    }
    // does request have a Cells object? Compute our Result then
    if( req.hasCells() )
    {
      stage = "getting result";
      cdebug(3)<<"  calling getResult(): cells are "<<req.cells();
      int code = getResult(ref,child_results,req,newreq);
      // default dependency mask added to return code
      retcode |= code | getDependMask();
      cdebug(3)<<"  getResult() returns code "<<ssprintf("0x%x",code)<<
          ", cumulative "<<ssprintf("0x%x",retcode)<<endl;
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
      // privatize the result for readonly -- this ensures that copy-on-write
      // is performed down the line
      ref.privatize(DMI::DEEP|DMI::READONLY);
    }
    else // no cells, ensure an empty result
    {
      ref <<= new Result(0);
      cdebug(3)<<"  empty result. Cumulative result code is "<<ssprintf("0x%x",retcode)<<endl;
      return cacheResult(ref,retcode) | RES_UPDATED;
    }
    // OK, at this point we have a valid Result to return
    if( DebugLevel>=3 ) // print it out
    {
      cdebug(3)<<"  cumulative result code is "<<ssprintf("0x%x",retcode)<<endl;
      cdebug(3)<<"  result is "<<ref.sdebug(DebugLevel-1,"    ")<<endl;
      if( DebugLevel>3 && ref.valid() )
      {
        ref->show(Debug::getDebugStream());
      }
    }
    // cache & return accumulated return code
    return cacheResult(ref,retcode) | RES_UPDATED;
  }
  // catch any exceptions, return a single fail result
  catch( std::exception &exc )
  {
    ref <<= new Result(1);
    VellSet & res = ref().setNewVellSet(0);
    MakeFailVellSet(res,string("exception in execute() while "+stage+": ")+exc.what());
    return cacheResult(ref,RES_FAIL) | RES_UPDATED;
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
