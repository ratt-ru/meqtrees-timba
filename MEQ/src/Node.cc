//#  Node.cc: base MeqNode class
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

#include "Node.h"
#include "Forest.h"
#include "ResampleMachine.h"
#include "MeqVocabulary.h"
#include "MTPool.h"
#include <DMI/BlockSet.h>
#include <DMI/Record.h>
#include <DMI/Vec.h>
#include <DMI/NumArray.h>
#include <algorithm>

namespace Meq {

InitDebugContext(Node,"MeqNode");

using Debug::ssprintf;
ObjRef Node::_dummy_objref;


//##ModelId=3F5F43E000A0
Node::Node (int nchildren,const HIID *labels,int nmandatory)
    : control_status_(CS_ACTIVE),
      depend_mask_(0),
      node_groups_(1,FAll),
      auto_resample_(RESAMPLE_FAIL),
      disable_auto_resample_(false)
{
  description_ = name() + ':' + objectType().toString();
  executing_ = false;
  // figure out # of children
  if( nchildren<0 )               // negative: specifies N or more
  {
    check_max_children_ = -1;
    check_min_children_ = nchildren = -(nchildren+1);
  }
  else // positive: specifies exactly N
  {
    check_max_children_ = check_min_children_ = nchildren;
  }
  // nmandatory: specifies at least N
  if( nmandatory>=0 )
  {
    Assert(nmandatory<=nchildren);
    check_min_children_ = nmandatory;
  }
  // if labels are supplied, then nchildren must be set
  if( labels )   // copy labels and populate reverse map
  {
    Assert(nchildren>0);
    child_labels_.resize(nchildren);
    for( int i=0; i<nchildren; i++ )
    {
      child_labels_[i] = labels[i];
      child_label_map_[labels[i]] = i;
    }
  }
  // else child_labels_ stays empty to indicate no labels

  // other init
  internal_init_index_ = -1;
  breakpoints_ = breakpoints_ss_ = 0;
  publishing_level_ = 0;
  cache_policy_ = 0;
  log_policy_ = 0;
  cache_.is_valid = false;
  cache_.rescode = 0;
  has_state_dep_ = false;
  // init cache stats
  {
    DMI::Record &rec = cache_stats_ <<= new DMI::Record;
    // note that DMI::Vec always initializes contents to 0 for us
    DMI::Vec &vec_tot = rec[FAllRequests] <<= new DMI::Vec(Tpint,sizeof(CacheStats)/sizeof(int));
    DMI::Vec &vec_new = rec[FNewRequests] <<= new DMI::Vec(Tpint,sizeof(CacheStats)/sizeof(int));
    DMI::Vec &vec_par = rec[FParents] <<= new DMI::Vec(Tpint,sizeof(CacheParentInfo)/sizeof(int));
    // all stats are structs of ints, so we can reinterpret-cast here
    pcs_total_ = reinterpret_cast<CacheStats*>(vec_tot[HIID()].as_wp<int>());
    pcs_new_   = reinterpret_cast<CacheStats*>(vec_new[HIID()].as_wp<int>());
    pcparents_ = reinterpret_cast<CacheParentInfo*>(vec_par[HIID()].as_wp<int>());
    pcrescode_ = ( rec[FResultCode] <<= new DMI::Vec(Tpint,-1) )[HIID()].as_wp<int>();
  }
  // init profiling stats
  {
    DMI::Record &rec = profile_stats_ <<= new DMI::Record;
    rec[FCPUMhz]      = LOFAR::NSTimer::cpuSpeedInMHz();
    // all stats are structs of doubles, so we can reinterpret-cast here
    const int n = sizeof(ProfilingStats)/sizeof(double);
    pprof_total_     = reinterpret_cast<ProfilingStats*>
        ((rec[FTotal] <<= new DMI::Vec(Tpdouble,n))[HIID()].as_wp<double>());
    pprof_children_  = reinterpret_cast<ProfilingStats*>
        ((rec[FChildren] <<= new DMI::Vec(Tpdouble,n))[HIID()].as_wp<double>());
    pprof_getresult_ = reinterpret_cast<ProfilingStats*>
        ((rec[FGetResult] <<= new DMI::Vec(Tpdouble,n))[HIID()].as_wp<double>());
  }
}

//##ModelId=3F5F44A401BC
Node::~Node()
{
}

int Node::childLabelToNumber (const HIID &label) const
{
  ChildLabelMap::const_iterator iter = child_label_map_.find(label);
  if( iter != child_label_map_.end() )
    return iter->second;
  // not found, maybe numeric?
  if( label.size() != 1 )
    return -1;
  return label[0].index();   // AtomicID::index() returns -1 if non-numeric
}

void Node::postEvent (const HIID &type,const ObjRef &data)
{
  forest().postEvent(type,data);
}

void Node::postMessage (const string &msg,const ObjRef &data,AtomicID type)
{
  ObjRef ref;
  DMI::Record *prec;
  // if data is a record, place message into it, else create
  // new record and nest data in it
  if( data.valid() )
  {
    if( data->objectType() == TpDMIRecord )
    {
      ref = data;
      prec = ref.ref_cast<DMI::Record>().dewr_p();
    }
    else
    {
      ref <<= prec = new DMI::Record;
      (*prec)[AidData] = data;
    }
  }
  else
    ref <<= prec = new DMI::Record;
  // add node name and message
  (*prec)[FNode] = name();
  (*prec)[type] = "node '"+name()+"': "+msg;
  // post to forest
  forest().postEvent(type,ref);
}

void Node::setDependMask (int mask)
{
  depend_mask_ = mask;
  if( staterec_.valid() )
    staterec_()[FDependMask] = mask;
  cdebug(3)<<ssprintf("new depend mask is %x\n",depend_mask_);
}

// rebuilds (if needed) and returns a representative cache record
const DMI::Record & Node::Cache::record ()
{
  if( recref_.valid() )
    return *recref_;
  Record & rec = recref_ <<= new Record;
  if( result.valid() )
  {
    if( is_valid )
      rec.add(FResult,result);
    else
      rec.add(FFail,result);
  }
  rec[FRequestId] = rqid;
  rec[FResultCode] = rescode;
  return rec;
}

// reset cache from record
bool Node::Cache::fromRecord (const Record &rec)
{
  if( rec.size() == 0 )
  {
    clear();
    return false;
  }
// FailWhen1(rec.size()<2 || rec.size()>4,"illegal cache record");
  try
  {
    const Result *res = rec[FResult].as_po<Result>();
    if( res )
      is_valid = true;
    else
    {
      is_valid = false;
      res = rec[FFail].as_po<Result>();
    }
    if( res )
      result <<= res;
    else
      result.detach();
    rqid = rec[FRequestId].as<HIID>();
    rescode = rec[FResultCode].as<int>();
    return true;
  }
  catch( std::exception &exc )
  {
    cdebug1(3)<<"error parsing cache record: "<<exceptionToString(exc);
    clear();
    ThrowMore1(exc,"illegal cache record");
  }
  catch( ... )
  {
    clear();
    cdebug1(3)<<"unknown exception parsing cache record"<<endl;
    Throw1("illegal cache record");
  }
}

//##ModelId=400E531402D1
void Node::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  // if initializing, put in name and nodeindex
  if( initializing )
  {
    rec[FName] = name();
    rec[FNodeIndex] = nodeIndex();
  }
  else
  // else check for immutable fields
  {
    protectStateField(rec,FClass);
    protectStateField(rec,FChildren);
    protectStateField(rec,FStepChildren);
    protectStateField(rec,FChildIndices);
    protectStateField(rec,FStepChildIndices);
    protectStateField(rec,FParentIndices);
    protectStateField(rec,FIsStepParent);
    protectStateField(rec,FName);
    protectStateField(rec,FNodeIndex);
    protectStateField(rec,FInternalInitIndex);
  }
  // apply changes to mutable bits of control state
  int cs0 = control_status_;
  int new_cs;
  if( rec[FControlStatus].get(new_cs) )
    control_status_ = (control_status_&~CS_WRITABLE_MASK)|(new_cs&CS_WRITABLE_MASK);
  // set publishing level
  if( rec[FPublishingLevel].get(publishing_level_,initializing) )
  {
    if( publishing_level_ )
      control_status_ |= CS_PUBLISHING;
    else
      control_status_ &= ~CS_PUBLISHING;
  }
  // set breakpoints
  if( rec[FBreakpoint].get(breakpoints_) )
    control_status_ = breakpoints_ ? control_status_|CS_BREAKPOINT : control_status_&~CS_BREAKPOINT;
  if( rec[FBreakpointSingleShot].get(breakpoints_ss_) )
    control_status_ = breakpoints_ss_ ? control_status_|CS_BREAKPOINT_SS : control_status_&~CS_BREAKPOINT_SS;
  // set cache: must be a record parsable by the Node::Cache class
  const DMI::Record * pcache = rec[FCache].as_po<DMI::Record>();
  if( pcache )
  {
    // Thread::Mutex::Lock lock(cache_.mutex);
    if( cache_.fromRecord(*pcache) )
      control_status_ |= CS_CACHED;
    else
      control_status_ &= ~CS_CACHED;
  }
  // set/clear last request
  const Request * preq = rec[FRequest].as_po<Request>();
  if( preq )
    current_request_ <<= preq;

  // apply any changes to control status
  if( cs0 != control_status_ )
  {
    rec[FControlStatus] = control_status_;
    forest_->newControlStatus(*this,cs0,control_status_);
  }

  // get/set description
  if( !rec[FNodeDescription].get(description_) && initializing )
  {
    description_ = name() + ':' + objectType().toString();
    rec[FNodeDescription] = description_;
  }

  // set the caching policy
  rec[FCachePolicy].get(cache_policy_,initializing);
  rec[FCacheNumActiveParents].get(pcparents_->nact,initializing);

  // set the logging policy
  rec[FLogPolicy].get(log_policy_,initializing);

  // active symdeps
  SymdepMap::DepSet active_symdeps;
  if( initializing )
    active_symdeps = symdeps().getActive();
  if( rec[FActiveSymDeps].get_vector(active_symdeps,initializing) )
  {
    cdebug(2)<<"active_symdeps set via state\n";
    setActiveSymDeps(active_symdeps);
  }

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

  // set children nursery state
  children().setState(rec,initializing);

  // enable multithreading
  if( MTPool::num_threads() > 1 )
  {
    bool mtpoll = children().multiThreaded();
    if( rec[FMTPolling].get(mtpoll,initializing) )
    {
      children().enableMultiThreaded(mtpoll);
      stepchildren().enableMultiThreaded(mtpoll);
    }
  }
}

//##ModelId=3F5F445A00AC
void Node::setState (DMI::Record::Ref &rec)
{
  Thread::Mutex::Lock lock(stateMutex());
  // when initializing, we're called with our own state record, which
  // makes the rules somewhat different:
  bool initializing = ( rec == staterec_ );
  cdebug(2)<<"setState(init="<<initializing<<"): "<<rec.sdebug(10)<<endl;
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
    throw; // No cleanup required, just re-throw
  }
  catch( std::exception &exc )
  {
    if( !initializing )
      setStateImpl(staterec_,true);
    ThrowMore(exc,"setState() failed");
  }
  catch( ... )
  {
    if( !initializing )
      setStateImpl(staterec_,true);
    Throw("setState() failed with unknown exception");
  }
  // success: merge record into state record
  if( !initializing )
    wstate().merge(rec,true);
  // make sure nodes upstream get themselves a state dependency
  propagateStateDependency();
}

// //##ModelId=3F85710E028E
// NodeFace & Node::getChild (const HIID &id)
// {
//   ChildrenMap::const_iterator iter = child_map_.find(id);
//   FailWhen(iter==child_map_.end(),"unknown child "+id.toString());
//   return getChild(iter->second);
// }
//
// //##ModelId=3F98D9D20201
// inline int Node::getChildNumber (const HIID &id)
// {
//   ChildrenMap::const_iterator iter = child_map_.find(id);
//   return iter == child_map_.end() ? -1 : iter->second;
// }
//

void Node::fillProfilingStats (ProfilingStats *st,const LOFAR::NSTimer &timer)
{
  const double scale = 1e-3/LOFAR::NSTimer::cpuSpeedInMHz();
  st->total    = timer.totalTime()*scale;
  st->count    = timer.shotCount();
  st->average  = timer.shotCount() ? timer.faverageTime()*scale : 0;
}

void Node::getSyncState (DMI::Record::Ref &ref)
{
  Thread::Mutex::Lock lock(stateMutex());
  DMI::Record & st = wstate();
  if( current_request_.valid() )
    st.replace(FRequest,current_request_);
  else
    st.remove(FRequest);
  st.replace(FProfilingStats,profile_stats_);
  fillProfilingStats(pprof_total_,timers_.total);
  fillProfilingStats(pprof_children_,timers_.children);
  fillProfilingStats(pprof_getresult_,timers_.getresult);
  {
    if( has_state_dep_ )
      cache_.rescode |= symdeps().getMask(FState);
    // Thread::Mutex::Lock lock(cache_.mutex);
    st.replace(FCache,cache_.record());
    st.replace(FCacheStats,cache_stats_);
    if( cache_.valid() )
      control_status_ |= CS_CACHED;
    else
      control_status_ &= ~CS_CACHED;
  }
  st[FRequestId]       = current_reqid_;
  st[FControlStatus]   = control_status_;
  st[FBreakpointSingleShot] = breakpoints_ss_;
  st[FBreakpoint] = breakpoints_;
  ref = staterec_;
}

//##ModelId=3F9919B10014
void Node::setCurrentRequest (const Request &req)
{
  current_request_.attach(req);
  current_reqid_ = req.id();
}

void Node::propagateStateDependency ()
{
  // do nothing if we are already dependent on state, parents will know anyway
  if( has_state_dep_ )
    return;
  has_state_dep_ = true;
  // notify parents
  for( int i=0; i<numParents(); i++ )
    getParent(i).propagateStateDependency();
}

//##ModelId=400E531300C8
void Node::clearCache (bool recursive) throw()
{
  Thread::Mutex::Lock lock(execCond());
  cache_.clear();
  if( control_status_ & CS_CACHED )
    setControlStatus(control_status_&~CS_CACHED,recursive); // sync if recursive
  if( recursive )
  {
    // in recursive mode, also clear stats
    memset(pcs_total_,0,sizeof(CacheStats));
    memset(pcs_new_,0,sizeof(CacheStats));
    for( int i=0; i<children().numChildren(); i++ )
      if( children().isChildValid(i) )
        children().getChild(i).clearCache(true);
    for( int i=0; i<stepchildren().numChildren(); i++ )
      stepchildren().getChild(i).clearCache(true);
  }
}

// static FILE *flog = fopen("cache.log","w");

//##ModelId=400E531A021A
bool Node::getCachedResult (int &retcode,Result::Ref &ref,const Request &req)
{
  // Thread::Mutex::Lock lock(cache_.mutex);
  // no cache -- return false
  if( !cache_.valid() )
  {
    pcs_total_->none++;
    if( new_request_ )
      pcs_new_->none++;
    return false;
  }
  if( has_state_dep_ )
    cache_.rescode |= symdeps().getMask(FState);
  // Check that cached result is applicable:
  // (1) An empty reqid never matches, hence it can be used to
  //     always force a recalculation.
  // (2) Ignore PARM_UPDATE requests if we have no dependency on
  //     iteration
  // (3) Do a masked compare of rqids using the dependency mask.
  //   (3b) As a special case, reuse a cached result w/perts if no perts
  //        are requested -- strip them off
  cdebug(4)<<"checking cache: request "<<cache_.rqid<<", code "<<ssprintf("0x%x",cache_.rescode)<<endl;
//   fprintf(flog,"%s: cache contains %s, code %x, request is %s\n",
//           name().c_str(),
//           cache_.rqid.toString().c_str(),cache_.rescode,req.id().toString().c_str());
  RequestId rqid = req.id();
  bool match = false;
  // (1) empty rqid never matches
  if( rqid.empty() || cache_.rqid.empty() )
    match = false;
  // (2) ignore PU requests if no dependency on iteration
  else if( req.requestType() == RequestType::PARM_UPDATE &&
           !(cache_.rescode&symdeps().getMask(FIteration)) )
  {
    ref <<= new Result;
    match = true;
  }
  // (3) find the diffmask
  else
  {
    int diffmask = RqId::diffMask(rqid,cache_.rqid)&cache_.rescode;
    // (3a) exact match -- return the cached request
    if( !diffmask )
    {
      ref = cache_.result;
      match = true;
    }
    // (3b) last special case: E0 requests match E1/E2 cache, but derivatives are stripped off
    else if( diffmask == RequestType::DEPMASK_TYPE &&
             req.evalMode() == 0 &&
             RequestType::evalMode(cache_.rqid) > 0 )
    {
      ref = cache_.result;
      Result &res = ref();
      for( int i=0; i<res.numVellSets(); i++ )
        if( res.vellSet(i).numPertSets() )
          res.vellSetWr(i).setNumPertSets(0);
      match = true;
    }
    else
      match = false;
  }
  // finally, do we have a match?
  if( match )
  {
    cdebug(4)<<"cache hit"<<endl;
    pcs_total_->hits++;
    if( new_request_ )
      pcs_new_->hits++;
//     fprintf(flog,"%s: reusing cache, cache cells are %x, req cells are %x\n",
//         name().c_str(),
//         (ref->hasCells() ? int(&(ref->cells())) : 0),
//         (req.hasCells() ? int(&(req.cells())) : 0));
    retcode = cache_.rescode;
    // if we're returning a cached result for a new request, clear the parent stats
    if( new_request_ )
    {
      int npar = pcparents_->nact ? pcparents_->nact : pcparents_->npar ;
      pcparents_->nhint = pcparents_->nhold = 0;
    }
    return true;
  }
  cdebug(4)<<"cache miss"<<endl;
  pcs_total_->miss++;
  if( new_request_ )
    pcs_new_->miss++;
//  fprintf(flog,"%s: cache missed\n",name().c_str());
  // no match -- clear cache and return
  clearCache(false);
  return false;
}

// stores result in cache as per current policy, returns retcode
//##ModelId=400E531C0200
int Node::cacheResult (const Result::Ref &ref,const Request &req,int retcode)
{
  // log result to forest, if necessary
  if( logPolicy() >= LOG_RESULTS ||
      ( logPolicy() == LOG_DEFAULT && forest().logPolicy() >= LOG_RESULTS ) )
    forest().logNodeResult(*this,req,*ref);
  has_state_dep_ = false;
  // clear the parent stats
  int npar = pcparents_->nact ? pcparents_->nact : pcparents_->npar ;
  pcparents_->nhint = pcparents_->nhold = 0;
  *pcrescode_ = retcode&((1<<RQIDM_NBITS)-1);
  // clear cached child results
  for( uint i=0; i<child_results_.size(); i++ )
    child_results_[i].detach();
  // policy decided by ourselves or forest
  actual_cache_policy_ = cache_policy_;
  if( actual_cache_policy_ == CACHE_DEFAULT )
    actual_cache_policy_ = forest().cachePolicy();
  // decide if we cache of not
  int diffmask = RqId::diffMask(req.id(),req.nextId());
  if( !(retcode&RES_IGNORE_TYPE) )
    retcode |= RequestType::DEPMASK_TYPE;
  bool do_cache = false;    // do we cache at all?
  bool longcache = false;   // do we cache beyond the last parent?
  if( retcode&RES_FAIL )
  {
    do_cache = longcache = true;           // fails always cached
  }
  else if( actual_cache_policy_ <= CACHE_NEVER )         // never cache
  {
    do_cache = longcache = false;
  }
  else if( actual_cache_policy_ <= CACHE_MINIMAL )  // hold for parents only
  {
    do_cache  = npar > 1;     // only cache when >1 parent
    longcache = false;
  }
  else if( actual_cache_policy_ < CACHE_ALWAYS )  // some form of smart caching
  {
    // cache if result is not invalidated by next request
    longcache = !(diffmask&retcode);
    do_cache = longcache || npar > 1;
  }
  else    // CACHE_ALWAYS: always retain cache
  {
    do_cache = longcache = true;
  }
  // if we don't hold our own cache, children should hold if they're not
  // invalidated by the diffmask
  holdChildCaches(!longcache,diffmask);
  // finally, set up cache if asked to
  if( do_cache )
  {
    // update stats
    pcs_total_->cached++;
    if( new_request_ )
      pcs_new_->cached++;
    if( longcache )
    {
      pcs_total_->longcached++;
      if( new_request_ )
        pcs_new_->longcached++;
    }
    // update the rest
    // note that we retain the state dependency bit if it is already set -- this
    // is because any state-updated child of ours updates this bit UP the tree,
    // so this may have already been set for us.
    // OMS: 04/12 no no this plays hell with Jan's reqseqs. Reverting
//    cache_.set(ref,req,retcode&~RES_UPDATED|(cache_.rescode&forest().getStateDependMask()));
    cache_.set(ref,req,retcode&~RES_UPDATED);
    cdebug(3)<<"caching result "<<req.id()<<" with code "<<ssprintf("0x%x",retcode&~RES_UPDATED)<<endl;
    // control status set directly (not via setControlStatus call) because
    // caller (execute(), presumably) is going to update status anyway
    control_status_ |= CS_CACHED;
    // sync state and publish event
    if( publishing_level_ )
    {
      syncState();
      postEvent(EvNodeResult,ObjRef(*staterec_));
    }
  }
  else // clear cache
  {
    // if we need to publish state, insert cache temporarily
    if( publishing_level_ )
    {
      syncState();
      ObjRef stateref(staterec_);
      DMI::Record &st = stateref.as<DMI::Record>();  // causes COW
      cache_.set(ref,req,retcode&~RES_UPDATED);
      st.replace(FCache,cache_.record());
      postEvent(EvNodeResult,stateref);
    }
    // now quietly clear cache
    clearCache(false);
  }
  return retcode;
}

void Node::setPublishingLevel (int level)
{
  wstate()[FPublishingLevel] = publishing_level_ = level;
  if( level )
    setControlStatus(control_status_ | CS_PUBLISHING);
  else
    setControlStatus(control_status_ & ~CS_PUBLISHING);
}

// tells children to hold or release cache as appropriate
// if hold=false, children always release cache
// if hold=true, children will release cache if they are not dependant on
// diffmask
void Node::holdChildCaches (bool hold,int diffmask)
{
  // finish any child/stepchild polls that may be in progress, since
  // we need their return codes now
  children().finishPoll();
  stepchildren().finishPoll();

  for( int i=0; i<children().numChildren(); i++ )
    if( children().isChildEnabled(i) )
    {
      bool hold_child_cache = hold && !(children().childRetcode(i)&diffmask);
      children().getChild(i).holdCache(hold_child_cache);
    }
  for( int i=0; i<stepchildren().numChildren(); i++ )
    if( stepchildren().isChildEnabled(i) )
    {
      bool hold_child_cache = hold && !(stepchildren().childRetcode(i)&diffmask);
      stepchildren().getChild(i).holdCache(hold_child_cache);
    }
}

// called by parent node to ask us to hold cache, or to allow release of cache
void Node::holdCache (bool hold) throw()
{
  Thread::Mutex::Lock lock(execCond());
  pcparents_->nhint++;
  if( hold )
    pcparents_->nhold++;
  cdebug(3)<<"parent cache hint: "<<
     pcparents_->npar<<" "<<pcparents_->nact<<" "<<pcparents_->nhint<<" "<<pcparents_->nhold<<endl;
  // have all parents checked in, and has noone asked for a hold (in smart mode)?
  if( actual_cache_policy_ < CACHE_ALWAYS &&
      pcparents_->nhint >= ( pcparents_->nact ? pcparents_->nact : pcparents_->npar ) &&
      ( actual_cache_policy_ <= CACHE_MINIMAL || !pcparents_->nhold ) )
  {
    cdebug(3)<<"clearing cache\n";
    clearCache(false);
  }
}

void Node::checkChildCells (Cells::Ref &rescells,const std::vector<Result::Ref> &childres)
{
  if( auto_resample_ == RESAMPLE_NONE )
    return;
  // if only one child: returns its cells, if any
  if( childres.size() == 1 )
  {
    if( childres[0].valid() && childres[0]->hasCells() )
      rescells <<= &( childres[0]->cells() );
    return;
  }
  // this will hold the "cumulative" shape of the children,
  // i.e., a superset of all their vellset shapes
  LoShape resshape;
  // now loop over all children to verify that their cells are mutually
  // consistent 
  for( uint ich=0; ich<childres.size(); ich++ )
  {
    if( !childres[ich].valid() )
      continue;
    const Result &chres = *childres[ich];
    if( !chres.hasCells() )
      continue;
    const Cells &cc = childres[ich]->cells();
    if( !rescells.valid() ) // first cells? Init result cells with it
    {
      rescells <<= &cc;
      resshape = chres.getVellSetShape();
    }
    // otherwise, check this "next cells" for compatibility with accumulated
    // cells (unless it happens to be the same object)
    else if( rescells.deref_p() != &( cc ) )
    {
      LoShape shape1 = chres.getVellSetShape();
      // check every axis
      for( uint iaxis = 0; iaxis<std::max(resshape.size(),shape1.size()); iaxis++ )
      {
        int np1 = cc.ncells(iaxis);
        // axis not defined in next cells? skip it
        if( !np1 )
          continue;
        // axis not defined in accumulated cells? merge it in
        int np = rescells->ncells(iaxis);
        if( !np )
        {
          rescells().setCells(iaxis,cc.center(iaxis),cc.cellSize(iaxis));
          rescells().recomputeDomain();
          continue;
        }
        // else check axes for compatibility, but only if there's a real
        // shape in the cumulative result. Otherwise the axis is degenerate
        // and we can use the axis from this child's cells
        // 1. degenerate axis in cumulative result
        if( iaxis >= resshape.size() || resshape[iaxis] == 1 )
        {
          // 1.1. non-degenerate axis in next result, merge cells 
          if( iaxis < shape1.size() && shape1[iaxis] > 1 )
          {
            rescells().setCells(iaxis,cc.center(iaxis),cc.cellSize(iaxis));
            rescells().recomputeDomain();
          }
          // 1.2. degenerate axis in next result, do nothing
          continue;
        }
        // 2. non-degenerate axis in cumulative result
        else
        {
          // 2.1. degenerate axis in next result, ignore it
          if( iaxis >= shape1.size() || shape1[iaxis] == 1 )
            continue;
          // 2.2. both axes non-degenerate, compare cells
          if( np != np1 || 
              fabs(rescells->domain().start(iaxis) - cc.domain().start(iaxis)) > 1e-16 ||
              fabs(rescells->domain().end(iaxis) - cc.domain().end(iaxis))     > 1e-16 )
          {
            double diff1 = rescells->domain().start(iaxis) - cc.domain().start(iaxis);
            double diff2 = rescells->domain().end(iaxis) - cc.domain().end(iaxis);
            Throw(ssprintf("cells of child result %d, axis %s do not match those of previous children",
                  ich,Axis::axisId(iaxis).toString().c_str()));
          }
        }
      }
      // merge this result's shape into the cumulative shape
      if( !Axis::mergeShape(resshape,shape1) )
        Throw(ssprintf("shape of child result %d does not match that of previous children",ich));
    }
  }
}

int Node::discoverSpids (Result::Ref &ref,const std::vector<Result::Ref> &child_results,
                         const Request &)
{
  Result *presult = 0;
  // loop over child results
  for( uint i=0; i<child_results.size(); i++ )
    if( child_results[i].valid() )
    {
      const Result &chres = *child_results[i];
      const DMI::Record *pchmap = chres[FSpidMap].as_po<DMI::Record>();
      if( pchmap )
      {
        // no output result yet? simply attach copy of this result
        if( !ref.valid() )
          ref.attach(chres);
        // else have a result
        else
        {
          if( !presult )
            presult = ref.dewr_p(); // COW the result
          // does it have a spid map? If not, insert child's map
          DMI::Record *pmap = presult->as_po<DMI::Record>(FSpidMap);
          if( !pmap )
            presult->add(FSpidMap,pchmap);
          else // else merge child spid map into result map
            pmap->merge(*pchmap,false);
        }
      }
    }
  return 0;
}

int Node::pollChildren (Result::Ref &resref,
                        std::vector<Result::Ref> &childres,
                        const Request &req)
{
  setExecState(CS_ES_POLLING);
  timers().children.start();
  int retcode = children().syncPoll(resref,childres,req);
  // if aborted, return without polling stepchildren
  if( retcode&RES_ABORT ||
      ( retcode&RES_FAIL && children().failPolicy() == AidAbandonPropagate ) ||
      ( retcode&RES_MISSING && children().failPolicy() == AidAbandonPropagate ) )
  {
    timers().children.stop();
    return retcode;
  }
  // do a background poll of the stepchildren
  stepchildren().backgroundPoll(req);
  timers().children.stop();
  return retcode;
}

//##ModelId=3F6726C4039D
int Node::execute (Result::Ref &ref,const Request &req) throw()
{
  // check for re-entrancy
#ifdef DISABLE_NODE_MT
  if( executing_  )
  {
    Throw("can't re-enter Node::execute(). Are you trying to reexecute a node "
          "that is stopped at a breakpoint, or its parent?");
  }
#else
  Thread::Mutex::Lock lock(execCond());
  // if node is executing, then wait for it to finish, and meanwhile
  // mark our thread as blocked
  if( executing_ )
  {
    MTPool::Brigade::markThreadAsBlocked(name());
    while( executing_ )
      execCond().wait();
    MTPool::Brigade::markThreadAsUnblocked(name());
  }
  executing_ = true;
#endif
  // since we use the same execCond() mutex for the cache, hold lock until we
  // have checked cache below

  // now set a lock on the state mutex
  Thread::Mutex::Lock state_lock(stateMutex());
  pstate_lock_ = &state_lock;

  cdebug(3)<<"execute, request ID "<<req.id()<<": "<<req.sdebug(DebugLevel-1,"    ")<<endl;
  FailWhen(internal_init_index_<0,"execute() called before resolve()");
  int retcode = 0;
  // this indicates the current stage (for exception handler)
  string stage;
  string local_error;              // non-empty if error is generated
  DMI::ExceptionList local_fails;  // this is non-empty if we detect a local fail
  try
  {
    // check for abort flag
    if( forest().abortFlag() )
      return exitAbort(RES_ABORT);
    timers_.total.start();
    if( forest().debugLevel()>1 )
      wstate()[FNewRequest].replace() <<= req;
    setExecState(CS_ES_REQUEST);
    // do we have a new request? Empty request id treated as always new
    new_request_ = !current_request_.valid() ||
                   req.id().empty() ||
                   req.id() != current_reqid_;
    // update stats
    pcs_total_->req++;
    if( new_request_ )
      pcs_new_->req++;
    // check the cache, return on match (cache will be cleared on mismatch)
    stage = "checking cache";
    if( getCachedResult(retcode,ref,req) )
    {
        cdebug(3)<<"  cache hit, returning cached code "<<ssprintf("0x%x",retcode)<<" and result:"<<endl<<
                   "    "<<ref->sdebug(DebugLevel-1,"    ")<<endl;
        setExecState(CS_ES_IDLE,control_status_|CS_RETCACHE);
        return exitExecute(retcode);
    }
    lock.release();
    has_state_dep_ = false;
    // clear out the RETCACHE flag and the result state, since we
    // have no result for now
    control_status_ &= ~(CS_RETCACHE|CS_RES_MASK);
    if( new_request_ )
    {
//       // check if node is ready to go on to the new request, return WAIT if not
//       stage = "calling readyForRequest()";
//       if( !readyForRequest(req) )
//       {
//         cdebug(3)<<"  node not ready for new request, returning RES_WAIT"<<endl;
//         setExecState(CS_ES_IDLE,control_status_|CS_RES_WAIT);
//         return exitExecute(RES_WAIT);
//       }
      // set this request as current
      setCurrentRequest(req);
      // check for request riders
      if( req.hasRider() )
      {
        setExecState(CS_ES_COMMAND);
        stage = "processing rider";
        retcode = processRequestRider(ref,req);
      }
    } // endif( new_request_ )
    // if node is deactivated, return an empty result at this point
    if( !getControlStatus(CS_ACTIVE) )
    {
      if( !ref.valid() )
        ref <<= new Result(0);
      cdebug(3)<<"  node deactivated, empty result. Cumulative result code is "<<ssprintf("0x%x",retcode)<<endl;
      lock.relock(execCond());
      int ret = cacheResult(ref,req,retcode) | RES_UPDATED;
      setExecState(CS_ES_IDLE,control_status_|CS_RES_EMPTY);
      return exitExecute(ret);
    }
    // clear the retcode if the request has cells, children code + getResult()
    // will be considered the real result
    Cells::Ref rescells;
    if( req.hasCells() )
    {
      // rescells.attach(req.cells());
      retcode = 0;
    }
    // Pass request on to children and accumulate their results
    int result_status; // result status, this will be placed into our control_status
    stage = "polling children";
    retcode |= pollChildren(ref,child_results_,req);
    if( forest().abortFlag() )
      return exitAbort(RES_ABORT);
    // a WAIT from any child is returned immediately w/o a result
    if( retcode&RES_WAIT )
    {
      setExecState(CS_ES_IDLE,control_status_|CS_RES_WAIT);
      return exitExecute(retcode);
    }
    // if failed, then cache & return the result
    else if( retcode&RES_FAIL )
    {
      lock.relock(execCond());
      int ret = cacheResult(ref,req,retcode) | RES_UPDATED;
      setExecState(CS_ES_IDLE,control_status_|CS_RES_FAIL);
      return exitExecute(ret);
    }
    // if missing data, form and return a missing data result
    else if( retcode&RES_MISSING )
    {
      lock.relock(execCond());
      ref <<= new Result(1);
      ref().setVellSet(0,new VellSet);
      int ret = cacheResult(ref,req,retcode) | RES_UPDATED;
      setExecState(CS_ES_IDLE,control_status_|CS_RES_MISSING);
      return exitExecute(ret);
    }
    // add in default depend mask
    retcode |= getDependMask();
    //if( forest().abortFlag() )
    //      return exitAbort(RES_ABORT);
    // does request have a Cells object? Compute our Result then
    if( req.hasCells() )
    {
      // if request has cells, then check child cells for consistency
      //****** replace this with the auto-resampler
      checkChildCells(rescells,child_results_);
      // if no children cells were found, attach request cells
      if( !rescells.valid() && req.hasCells() )
        rescells.attach(req.cells());

      setExecState(CS_ES_EVALUATING);
      // EVAL/SINGLE/DOUBLE: normal getResult() mode
      if( req.evalMode() >= 0 )
      {
        stage = "getting result";
        cdebug(3)<<"  calling getResult(): cells are "<<req.cells();
        timers_.getresult.start();
        int code = getResult(ref,child_results_,req,new_request_);
        timers_.getresult.stop();
        // default dependency mask added to return code
        retcode |= code;
        cdebug(3)<<"  getResult() returns code "<<ssprintf("0x%x",code)<<
            ", cumulative "<<ssprintf("0x%x",retcode)<<endl;
        // a WAIT is returned immediately with no valid result expected
        if( code&RES_WAIT )
        {
          setExecState(CS_ES_IDLE,control_status_|CS_RES_WAIT);
          return exitExecute(retcode);
        }
        // Set Cells in the Result object as needed
        // (setCells() will do nothing when result has no variability axes)
        if( ref.valid() && !ref->hasCells() && rescells.valid() )
          ref().setCells(*rescells);
      }
      else if( req.requestType() == RequestType::DISCOVER_SPIDS )
      {
        stage = "discovering spids";
        int code = discoverSpids(ref,child_results_,req);
        retcode |= code | getDependMask();
      }
      // if FAIL is returned, prepare error message
      if( retcode&RES_FAIL )
      {
        bool added = false;
        if( ref.valid() )
          for( int i=0; i<ref->numVellSets(); i++ )
          {
            const VellSet &vs = ref->vellSet(i);
            if( vs.isFail() )
            {
              if( local_error.empty() )
                local_error = vs.getFailMessage();
              vs.addToExceptionList(local_fails);
            }
          }
      }
      if( local_error.empty() )
        local_error = "unknown failure while "+stage+" for request "+req.id().toString('.');
      else
        local_error += " (while "+stage+" for request "+req.id().toString('.')+")";
      result_status = retcode&RES_FAIL ? CS_RES_FAIL : CS_RES_OK;
    }
    else // no cells at all, allocate an empty result
    {
      result_status = CS_RES_EMPTY;
    }
    if( forest().abortFlag() )
      return exitAbort(RES_ABORT);
    // end of request processing
    // still no result? allocate an empty one just in case
    if( !ref.valid() )
      ref <<= new Result(0);
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
    // stop timers
    if( timers().getresult.isRunning() )
      timers().getresult.stop();
    if( timers().children.isRunning() )
      timers().children.stop();
    // cache & return accumulated return code
    lock.relock(execCond());
    int ret = cacheResult(ref,req,retcode) | RES_UPDATED;
    setExecState(CS_ES_IDLE,control_status_|result_status);
    return exitExecute(ret);
  }
  // catch any exceptions, form up a fail result
  catch( std::exception &exc )
  {
    ref <<= new Result(1);
    VellSet & res = ref().setNewVellSet(0);
    local_error = string(exc.what())+" (while "+stage+" for request "+req.id().toString('.')+")";
    local_fails.add(exc);
    MakeFailVellSetMore(res,exc,"exception in execute() while "+stage);
  }
  catch( ... )
  {
    ref <<= new Result(1);
    VellSet & res = ref().setNewVellSet(0);
    local_error = "unknown error while "+stage+" for request "+req.id().toString('.');
    MakeFailVellSet(res,"unknown exception in execute() while "+stage);
  }
  // clean up and return the fail
  if( timers().getresult.isRunning() )
    timers().getresult.stop();
  if( timers().children.isRunning() )
    timers().children.stop();
  int ret;
  // post local fails if any have accumulated
  if( !local_error.empty() )
    postError(local_error,local_fails.makeList());
  // any exceptions here need to be caught so that we clean up properly
  try
  {
    lock.relock(execCond());
    ret = cacheResult(ref,req,retcode|RES_FAIL) | RES_UPDATED;
  }
  catch( ... )
  {
    setExecState(CS_ES_IDLE,
          (control_status_&~(CS_RETCACHE|CS_RES_MASK))|CS_RES_FAIL);
    exitExecute(retcode|RES_FAIL);
    throw;
  }
  // no error, return
  setExecState(CS_ES_IDLE,
        (control_status_&~(CS_RETCACHE|CS_RES_MASK))|CS_RES_FAIL);
  return exitExecute(ret);
}

void Node::setBreakpoint (int bpmask,bool oneshot)
{
  Thread::Mutex::Lock lock(stateMutex());
  if( oneshot )
  {
    breakpoints_ss_ |= bpmask;
    setControlStatus(breakpoints_ss_ ? control_status_|CS_BREAKPOINT_SS : control_status_&~CS_BREAKPOINT_SS);
  }
  else
  {
    breakpoints_ |= bpmask;
    setControlStatus(breakpoints_ ? control_status_|CS_BREAKPOINT : control_status_&~CS_BREAKPOINT);
  }
}

void Node::clearBreakpoint (int bpmask,bool oneshot)
{
  Thread::Mutex::Lock lock(stateMutex());
  if( oneshot )
  {
    breakpoints_ss_ &= ~bpmask;
    setControlStatus(breakpoints_ss_ ? control_status_|CS_BREAKPOINT_SS : control_status_&~CS_BREAKPOINT_SS);
  }
  else
  {
    breakpoints_ &= ~bpmask;
    setControlStatus(breakpoints_ ? control_status_|CS_BREAKPOINT : control_status_&~CS_BREAKPOINT);
  }
}

void Node::setControlStatus (int newst,bool sync)
{
  if( sync )
    wstate()[FControlStatus] = newst;
  if( control_status_ != newst )
  {
    int oldst = control_status_;
    control_status_ = newst;
    forest_->newControlStatus(*this,oldst,newst);
  }
}

void Node::setExecState (int es,int newst,bool sync)
{
  parent_status_published_ = false;
  // update exec state in new control status
  newst = (newst&~CS_MASK_EXECSTATE) | es;
  if( !forest().abortFlag() )
  {
    // check breakpoints
    int bp = breakpointMask(newst);
    // if fail result is being returned, add BP_FAIL to mask
    if( es == CS_ES_IDLE && (newst&CS_RES_MASK) == CS_RES_FAIL )
      bp |= BP_FAIL;
    // always check global breakpoints first (to make sure single-shots are cleared)
    bool breakpoint = forest_->checkGlobalBreakpoints(bp);
    // the local flag is true if a local breakpoint (also) occurs
    bool local = false;
    // always check and flush local single-shot breakpoints
    if( breakpoints_ss_&bp )
    {
      breakpoint = local = true;
      breakpoints_ss_ = 0;
      newst &= ~CS_BREAKPOINT_SS;
    }
    else if( breakpoints_&bp ) // finally check for persistent local breakpoints
      breakpoint = local = true;
    // finally, check persistent local breakpoints too
    if( breakpoint )
    {
      // update control status
      // the breakpoint flag is only raised if we stopped because of a local
      // breakpoint
      if( local )
        newst |= CS_STOP_BREAKPOINT;
      setControlStatus(newst|CS_STOPPED,sync);
      // now notify the forest of breakpoint (presumably this will wait
      // on the stop flag)
      pstate_lock_->release();
      publishParentalStatus();  // recursively publish control status
      forest_->processBreakpoint(*this,bp,!local);
      pstate_lock_->relock(state_mutex_);
      // clear stop bit from control status
      setControlStatus(control_status_&~(CS_STOP_BREAKPOINT|CS_STOPPED),sync);
    }
    else
      setControlStatus(newst,sync);
    return;
  }
  // no breakpoints, simply update control status
  // But do check if forest is stopped at a breakpoint in another thread.
  // If this is the case, then stop here and wait
  if( !forest().abortFlag() && forest_->isStopFlagRaised() )
  {
    setControlStatus(newst|CS_STOPPED,sync);
    pstate_lock_->release();
    publishParentalStatus();  // recursively publish control status
    forest_->waitOnStopFlag();
    pstate_lock_->relock(state_mutex_);
  }
  setControlStatus(newst,sync);
}

void Node::publishParentalStatus ()
{
  if( parent_status_published_ )
    return;
  parent_status_published_ = true;
  forest().newControlStatus(*this,control_status_,control_status_,true);
  // skip when already hit by this loop
  for( int i=0; i<numParents(); i++ )
    getParent(i).publishParentalStatus();
}

std::string Node::getStrExecState (int state)
{
  switch( state )
  {
    case CS_ES_IDLE:        return "IDLE";
    case CS_ES_REQUEST:     return "REQUEST";
    case CS_ES_COMMAND:     return "COMMAND";
    case CS_ES_POLLING:     return "POLLING";
    case CS_ES_EVALUATING:  return "EVALUATING";
    default:                return "(unknown exec state)";
  }
}

void Node::enableMultiThreadedPolling (bool enable)
{
  if( MTPool::num_threads() < 2 )
    enable = false;
  children().enableMultiThreaded(enable);
  stepchildren().enableMultiThreaded(enable);
}

// these are called from the nurseries' idle loops
void Node::lockStateMutex ()
{
  pstate_lock_->lock(stateMutex());
}

void Node::unlockStateMutex ()
{
  pstate_lock_->release();
}

void Node::Node_lockStateMutex (void *args)
{
  static_cast<Node*>(args)->lockStateMutex();
}

void Node::Node_unlockStateMutex (void *args)
{
  static_cast<Node*>(args)->unlockStateMutex();
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
    out = description_;
  }
  if( detail >= 1 || detail == -1 )
  {
    appendf(out,"cs:%x",getControlStatus());
  }
  return out;
}

} // namespace Meq
