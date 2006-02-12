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
#include "MTPool.h"
#include <DMI/BlockSet.h>
#include <DMI/Record.h>
#include <DMI/Vec.h>
#include <DMI/NumArray.h>
#include <algorithm>

namespace Meq {

InitDebugContext(Node,"MeqNode");

using Debug::ssprintf;

//##ModelId=3F5F43E000A0
Node::Node (int nchildren,const HIID *labels,int nmandatory)
    : control_status_(CS_ACTIVE),
      propagate_child_fails_(true),
      depend_mask_(0),
//      symdep_masks_(defaultSymdepMasks()),
      node_groups_(1,FAll),
      auto_resample_(RESAMPLE_NONE),
      disable_auto_resample_(false)
{
  mt.enabled_ = false; // multithreading disabled by default
  mt.cur_brigade_ = 0;
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
  if( labels )   // copy labels
  {
    Assert(nchildren>0);
    child_labels_.resize(nchildren);
    for( int i=0; i<nchildren; i++ )
      child_labels_[i] = labels[i];
  }
  // else child_labels_ stays empty to indicate no labels -- this is checked below

  // other init
  breakpoints_ = breakpoints_ss_ = 0;
  cache_policy_ = 0;
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

ObjRef Node::_dummy_objref;

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

// 18/04/05 OMS: phasing this out, ModRes will need to be rewritten a-la Solver
// void Node::setGenSymDeps (const HIID symdeps[],const int depmasks[],int ndeps,const HIID &group)
// {
//   cdebug(2)<<"setting "<<ndeps<<" generated symdeps\n";
//   gen_symdep_fullmask_ = 0;
//   for( int i=0; i<ndeps; i++ )
//   {
//     gen_symdep_fullmask_ |= 
//         gen_symdep_masks_[symdeps[i]] = depmasks[i];
//   }
//   gen_symdep_group_ = group;
// }
// 
// int Node::getGenSymDepMask (const HIID &symdep) const
// {
//   std::map<HIID,int>::const_iterator iter = gen_symdep_masks_.find(symdep);
//   return iter == gen_symdep_masks_.end() ? 0 : iter->second;
// }


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
  FailWhen1(rec.size()<3 || rec.size()>4,"illegal cache record");
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
  // if not initializing, check for immutable fields
  if( !initializing )
  {
    protectStateField(rec,FClass);
    protectStateField(rec,FChildren);
    protectStateField(rec,FChildrenNames);
    protectStateField(rec,FNodeIndex);
    protectStateField(rec,FResolveParentId);
  }
  // apply changes to mutable bits of control state
  int cs0 = control_status_;
  int new_cs;
  if( rec[FControlStatus].get(new_cs) )
    control_status_ = (control_status_&~CS_WRITABLE_MASK)|(new_cs&CS_WRITABLE_MASK);
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
  
  // set the name
  rec[FName].get(myname_,initializing);
  // get/set description
  if( !rec[FNodeDescription].get(description_) && initializing )
  {
    description_ = myname_ + ':' + objectType().toString();
    rec[FNodeDescription] = description_; 
  }
  
  // set the caching policy
  rec[FCachePolicy].get(cache_policy_,initializing);
  rec[FCacheNumActiveParents].get(pcparents_->nact,initializing);
  // get known symdeps
  rec[FKnownSymDeps].get_vector(known_symdeps_,initializing && !known_symdeps_.empty());
  // get symdep masks, if specified
  DMI::Record::Hook hdepmasks(rec,FSymDepMasks);
  if( hdepmasks.exists() )
  {
    symdep_masks_.clear();
    if( hdepmasks.type() == TpDMIRecord )
    {
      cdebug(2)<<"new symdep_masks set via state\n";
      const DMI::Record &maskrec = hdepmasks.as<DMI::Record>();
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
//   // set auto-resample mode
//   int ars = auto_resample_;
//   if( rec[FAutoResample].get(ars,initializing) )
//   {
//     if( disable_auto_resample_ && ars != RESAMPLE_NONE )
//     {
//       NodeThrow(FailWithCleanup,"can't use auto-resampling with this node");
//     }
//     auto_resample_ = ars;
//   }

  rec[FPropagateChildFails].get(propagate_child_fails_,initializing);
  
  // set child poll order
  std::vector<string> cpo;
  if( rec[FChildPollOrder].get_vector(cpo) )
    setChildPollOrder(cpo);
  
  // enable multithreading
  if( MTPool::Brigade::numBrigades() )
  {
    bool mtpoll = mt.enabled_;
    rec[FMTPolling].get(mtpoll,initializing);
    enableMultiThreadedPolling(mtpoll);
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
  markStateDependency();
}

//##ModelId=400E53120082
void Node::setNodeIndex (int nodeindex)
{
  wstate()[FNodeIndex] = node_index_ = nodeindex;
}

string Node::getChildName (int i) const
{
  if( children_[i].valid() )
      return children_[i]->name();
  else
  {
    HIID label = getChildLabel(i);
    return state()[FChildrenNames][label].as<string>();
  }
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

void Node::fillProfilingStats (ProfilingStats *st,const LOFAR::NSTimer &timer)
{
  const double scale = 1e-3/LOFAR::NSTimer::cpuSpeedInMHz();
  st->total    = timer.totalTime()*scale;
  st->count    = timer.shotCount();
  st->average  = timer.shotCount() ? timer.faverageTime()*scale : 0;
}

void Node::syncState (DMI::Record::Ref &ref)
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
      cache_.rescode |= forest().getStateDependMask();
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

void Node::markStateDependency ()
{
  // do nothing if we are already dependent on state, parents will know anyway
  if( has_state_dep_ )
    return;
  has_state_dep_ = true;
  // notify parents
  for( int i=0; i<numParents(); i++ )
    getParent(i).markStateDependency();
}

//##ModelId=400E531300C8
void Node::clearCache (bool recursive,bool quiet)
{
  Thread::Mutex::Lock lock(execCond());
  cache_.clear();
  // clearRCRCache();
  if( control_status_ & CS_CACHED )
  {
    if( quiet )
      control_status_ &= ~CS_CACHED;
    else
      setControlStatus(control_status_ & ~CS_CACHED);
  }
  if( recursive )
  {
    // in recursive mode, also clear stats
    memset(pcs_total_,0,sizeof(CacheStats));
    memset(pcs_new_,0,sizeof(CacheStats));
    for( int i=0; i<numChildren(); i++ )
      if( isChildValid(i) )
        getChild(i).clearCache(true,quiet);
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
    cache_.rescode |= forest().getStateDependMask();
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
           !(cache_.rescode&getDependMask(AidIteration)) )
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
  // Thread::Mutex::Lock lock(cache_.mutex);
  has_state_dep_ = false;
  // clear the parent stats
  int npar = pcparents_->nact ? pcparents_->nact : pcparents_->npar ; 
  pcparents_->nhint = pcparents_->nhold = 0;
  *pcrescode_ = retcode&((1<<RQIDM_NBITS)-1);
  // clear child results if we're holding any
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
    // sync state and publish to all result subscribers
    if( result_event_gen_.active() )
    {
      syncState();
      result_event_gen_.generateEvent(staterec_.copy());  
    }
  }
  else // clear cache
  {
    // if we need to publish state, insert cache temporarily
    if( result_event_gen_.active() )
    {
      cache_.set(ref,req,retcode&~RES_UPDATED);
      syncState();
      result_event_gen_.generateEvent(staterec_.copy());  
    }
    // now quietly clear cache
    clearCache(false,true);
  }
  return retcode;
}

// tells children to hold or release cache as appropriate
// if hold=false, children always release cache
// if hold=true, children will release cache if they are not dependant on
// diffmask
void Node::holdChildCaches (bool hold,int diffmask)
{
  for( int i=0; i<numChildren(); i++ )
    if( !child_disabled_[i] )
      getChild(i).holdCache(hold && !(child_retcodes_[i]&diffmask) );
  for( int i=0; i<numStepChildren(); i++ )
    getStepChild(i).holdCache(hold && !(stepchild_retcodes_[i]&diffmask) );
}

// called by parent node to ask us to hold cache, or to allow release of cache
void Node::holdCache (bool hold)
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
    clearCache(false,false);
  }
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
  setControlStatus(control_status_ | CS_PUBLISHING);
  cdebug(2)<<"added result subscription "<<slot.evId().id()<<":"<<slot.recepient()<<endl;
}

void Node::removeResultSubscriber (const EventRecepient *recepient)
{
  result_event_gen_.removeSlot(recepient);
  if( !result_event_gen_.active() )
    setControlStatus(control_status_ & ~CS_PUBLISHING);
  cdebug(2)<<"removing all subscriptions for "<<recepient<<endl;
}

void Node::removeResultSubscriber (const EventSlot &slot)
{
  result_event_gen_.removeSlot(slot);
  if( !result_event_gen_.active() )
    setControlStatus(control_status_ & ~CS_PUBLISHING);
  cdebug(2)<<"removing result subscriber "<<slot.evId().id()<<":"<<slot.recepient()<<endl;
}

void Node::resampleChildren (Cells::Ref &rescells,std::vector<Result::Ref> &childres)
{
  if( auto_resample_ == RESAMPLE_NONE )
    return;
  const Cells *pcells = 0;
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
          res = pcells->compare(cc); // again, for debugging
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
    Throw("resampling currently disabled");
//     cdebug(3)<<"resampling child results to "<<*pcells<<endl;
//     ResampleMachine resample(*pcells);
//     for( uint ich=0; ich<childres.size(); ich++ )
//     {
//       if( childres[ich]->hasCells() )
//       {
//         resample.setInputRes(childres[ich]->cells());
//         if( resample.isIdentical() ) // child at correct resolution already
//         {
//           cdebug(3)<<"child "<<ich<<": already at this resolution\n";
//           // clear resample cache for this child
//           clearRCRCache(ich);
//         }
//         else
//         {
//           // check if resampled-child cache already contains the resampled result
//           if( !checkRCRCache(childres[ich],ich,*pcells) )
//           {
//             cdebug(3)<<"child "<<ich<<": resampling\n";
//             // privatize child result for writing
//             Result &chres = childres[ich].privatize(DMI::WRITE)(); 
//             chres.setCells(pcells);
//             // resample and cache the child result 
//             for( int ivs=0; ivs<chres.numVellSets(); ivs++ )
//             {
//               VellSet::Ref ref;
//               resample.apply(ref,chres.vellSetRef(ivs),chres.isIntegrated());
//               chres.setVellSet(ivs,ref);
//             }
//             cacheRCR(ich,childres[ich]);
//           }
//           else
//           {
//             cdebug(3)<<"child "<<ich<<": already cached at this resolution, reusing\n";
//           }
//         }
//       }
//     }
  }
  else if( rescells.valid() ) // no resampling needed and cells were present, clear cache of all resampled children
    clearRCRCache();
}

int Node::resolve (Node *parent,bool stepparent,DMI::Record::Ref &depmasks,int rpid)
{
  try
  {
    // increment the parent count
    if( parent )
    {
      pcparents_->npar++;
      parents_.push_back(ParentEntry());
      parents_.back().ref.attach(parent,DMI::SHARED);
      parents_.back().stepparent = stepparent;
    }
    // if node already resolved with this resolve parent ID, do nothing
    if( node_resolve_id_ == rpid )
    {
      cdebug(4)<<"node already resolved for rpid "<<rpid<<endl;
      return 0;
    }
    cdebug(3)<<"resolving node, rpid="<<rpid<<endl;
    wstate()[FResolveParentId] = node_resolve_id_ = rpid;
    // resolve children
    resolveChildren();
    // process depmasks 
    if( !known_symdeps_.empty() )
    {
      cdebug(3)<<"checking for "<<known_symdeps_.size()<<" known symdeps\n";
      const DMI::Record &rec = *depmasks;
      bool changed = false;
      for( uint i=0; i<node_groups_.size(); i++ )
      {
        DMI::Record::Hook hgroup(rec,node_groups_[i]);
        if( hgroup.exists() )
        {
          cdebug(4)<<"found symdeps for group "<<node_groups_[i]<<endl;
          const DMI::Record &grouprec = hgroup.as<DMI::Record>();
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
        DMI::Record &known = wstate()[FSymDepMasks].replace() <<= new DMI::Record;
        for( uint i=0; i<known_symdeps_.size(); i++ )
          known[known_symdeps_[i]] = symdep_masks_[known_symdeps_[i]];
      }
    }
  }
  catch( std::exception &exc )
  {
    ThrowMore(exc,"failed to resolve node '"+name()+"'");
  }
  catch( ... )
  {
    Throw("failed to resolve node '"+name()+"'");
  }
  // init other stuff
  child_results_.resize(numChildren());
  child_retcodes_.resize(numChildren());
  stepchild_retcodes_.resize(numStepChildren());
  // pass recursively onto children
  for( int i=0; i<numChildren(); i++ )
    if( isChildValid(i) )
      getChild(i).resolve(this,false,depmasks,rpid);
  for( int i=0; i<numStepChildren(); i++ )
    getStepChild(i).resolve(this,true,depmasks,rpid);
  return 0;
}

// process Node-specific commands
int Node::processCommands (Result::Ref &,const DMI::Record &rec,const Request &req)
{
  bool generate_symdeps = false;
  // process the Resolve.Children command: call resolve children
  // non-recursively (since the request + command is going up 
  // recursively anyway)
  if( rec[FResolveChildren].as<bool>(false) )
  {
    cdebug(4)<<"processCommands("<<FResolveChildren<<")\n";
    resolveChildren();
  }
  // process the "State" command: change node state
  ObjRef stateref = rec[FState].ref(true);
  if( stateref.valid() )
  {
    cdebug(4)<<"processCommands("<<FState<<"): calling setState()"<<endl;
    setState(stateref.ref_cast<DMI::Record>());
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
  DMI::Record::Hook hdep(rec,FAddDepMask);
  if( hdep.exists() )
  {
    if( !known_symdeps_.empty() && hdep.type() == TpDMIRecord )
    {
      cdebug(2)<<"processCommands("<<FAddDepMask<<"): checking for masks\n";
      const DMI::Record &deprec = hdep.as<DMI::Record>();
      // reinit the sysdep_masks field in the state record as we go along
      DMI::Record &known = wstate()[FSymDepMasks].replace() <<= new DMI::Record;
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
  return 0;
}

int Node::discoverSpids (Result::Ref &ref,const std::vector<Result::Ref> &child_results,
                         const Request &)
{
  Result *presult = 0;
  // loop over child results
  for( uint i=0; i<child_results.size(); i++ )
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

//##ModelId=3F6726C4039D
int Node::execute (Result::Ref &ref,const Request &req)
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
    MTPool::Brigade::markThreadAsBlocked(*this);
    while( executing_ )
      execCond().wait();
    MTPool::Brigade::markThreadAsUnblocked(*this);
  }
  executing_ = true;
#endif
  // since we use the same execCond() mutex for the cache, hold lock until we 
  // have checked cache below
  
  // now set a lock on the state mutex
  Thread::Mutex::Lock state_lock(stateMutex());
  pstate_lock_ = &state_lock;
  
  cdebug(3)<<"execute, request ID "<<req.id()<<": "<<req.sdebug(DebugLevel-1,"    ")<<endl;
  FailWhen(node_resolve_id_<0,"execute() called before resolve()");
  int retcode = 0;
  // this indicates the current stage (for exception handler)
  string stage;
  string local_error;              // non-empty if error is generated
  DMI::ExceptionList local_fails;  // this is non-empty if we detect a local fail
  try
  {
    // check for abort flag
    if( forest().abortFlag() )
      return exitAbort(retcode);
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
      // check if node is ready to go on to the new request, return WAIT if not
      stage = "calling readyForRequest()";
      if( !readyForRequest(req) )
      {
        cdebug(3)<<"  node not ready for new request, returning RES_WAIT"<<endl;
        setExecState(CS_ES_IDLE,control_status_|CS_RES_WAIT);
        return exitExecute(RES_WAIT);
      }
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
      rescells.attach(req.cells());
      retcode = 0;
    }
    // Pass request on to children and accumulate their results
    int result_status; // result status, this will be placed into our control_status
    if( numChildren() )
    {
      stage = "polling children";
      retcode |= pollChildren(ref,req);
      // a WAIT from any child is returned immediately w/o a result
      if( retcode&RES_WAIT )
      {
        setExecState(CS_ES_IDLE,control_status_|CS_RES_WAIT);
        return exitExecute(retcode);
      }
      // if failed, then cache & return the fail
      if( retcode&RES_FAIL )
      {
        lock.relock(execCond());
        int ret = cacheResult(ref,req,retcode) | RES_UPDATED;
        setExecState(CS_ES_IDLE,control_status_|CS_RES_FAIL);
        return exitExecute(ret);
      }
      // if request has cells, then resample children (will do nothing if disabled)
      resampleChildren(rescells,child_results_);
    }
    if( forest().abortFlag() )
      return exitAbort(retcode);
    // does request have a Cells object? Compute our Result then
    if( req.hasCells() )
    {
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
        retcode |= code | getDependMask();
        cdebug(3)<<"  getResult() returns code "<<ssprintf("0x%x",code)<<
            ", cumulative "<<ssprintf("0x%x",retcode)<<endl;
        // a WAIT is returned immediately with no valid result expected
        if( code&RES_WAIT )
        {
          setExecState(CS_ES_IDLE,control_status_|CS_RES_WAIT);
          return exitExecute(retcode);
        }
        // Set Cells in the Result object as needed
        // (will do nothing when no variability)
        if( ref.valid() && !ref->hasCells() && rescells.valid() )
          ref().setCells(*rescells);
      }
      else if( req.requestType() == RequestType::DISCOVER_SPIDS )
      {
        stage = "discovering spids";
        retcode |= discoverSpids(ref,child_results_,req);
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
      return exitAbort(retcode);
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
  if( timers_.getresult.isRunning() )
    timers_.getresult.stop();
  if( timers_.children.isRunning() )
    timers_.children.stop();
  int ret;
  // post local fails if any have accumulated
  if( !local_error.empty() )
    postError(local_error,local_fails.makeList());
  // any exceptions here need to be caught so that we clean up properly
  try
  {
    lock.relock(execCond());
    ret = cacheResult(ref,req,RES_FAIL) | RES_UPDATED;
  }
  catch( ... )
  {
    setExecState(CS_ES_IDLE,
          (control_status_&~(CS_RETCACHE|CS_RES_MASK))|CS_RES_FAIL);
    exitExecute(ret);
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
      publishParentalStatus();  // recursively publish parents' control status
      forest_->processBreakpoint(*this,bp,!local);
      pstate_lock_->relock(state_mutex_);
      // clear stop bit from control status
      setControlStatus(control_status_&~(CS_STOP_BREAKPOINT|CS_STOPPED),sync);
    }
    return;
  }
  // no breakpoints, simply update control status
  // But do check if forest is stopped at a breakpoint in another thread.
  // If this is the case, then stop here and wait
  if( !forest().abortFlag() && forest_->isStopFlagRaised() )
  {
    setControlStatus(newst|CS_STOPPED,sync);
    pstate_lock_->release();
    publishParentalStatus();  // recursively publish parents' control status
    forest_->waitOnStopFlag();
    pstate_lock_->relock(state_mutex_);
  }
  setControlStatus(newst,sync);
}

void Node::publishParentalStatus ()
{
  parent_status_published_ = true;
  // skip when already hit by this loop
  for( int i=0; i<numParents(); i++ )
  {
    Node &parent = getParent(i);
    // force out a status message for parent
    if( !parent.parent_status_published_ )
    {
      forest_->newControlStatus(parent,parent.getControlStatus(),parent.getControlStatus(),true);
      parent.publishParentalStatus();
    }
  }
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
