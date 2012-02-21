//#  Node.h: base MeqNode class
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
#ifndef MEQ_NODE_H_HEADER_INCLUDED_E5514413
#define MEQ_NODE_H_HEADER_INCLUDED_E5514413

#include <TimBase/Stopwatch.h>
#include <TimBase/Thread/Condition.h>
#include <DMI/Record.h>
#include <MEQ/NodeFace.h>
#include <MEQ/NodeNursery.h>
#include <MEQ/SymdepMap.h>
#include <MEQ/Result.h>
#include <MEQ/RequestId.h>
#include <MEQ/Request.h>
#include <MEQ/Cells.h>
#include <MEQ/AID-Meq.h>
#include <MEQ/TID-Meq.h>
#include <map>
#include <vector>

#pragma aidgroup Meq
#pragma types #Meq::Node
#pragma aid Add Clear Known Active Gen Dep Deps Symdep Symdeps Mask Masks Depth Current
#pragma aid Parm Value Resolution Domain Dataset Resolve Parent Init Id
#pragma aid Link Or Create Control Status New Breakpoint Single Shot Step
#pragma aid Cache Policy Stats All New Requests Parents Num Active Description
#pragma aid Profiling Stats Total Children Get Result Ticks Per Second CPU MHz
#pragma aid Poll Polling Order MT Propagate Child Fails Message Error Data
#pragma aid Parent Indices Is Internal Publishing Level Recursive Log


// forward declaration of MeqPython stuff -- only here to enable the
// friend declaration in Node
namespace MeqPython
{
  class PyNodeAccessor;
}


namespace Meq
{
using namespace DMI;

class Forest;
class Request;

const HIID FNode          = AidNode;

//== Node state fields
const HIID FChildren          = AidChildren;
const HIID FStepChildren      = AidStep|AidChildren;
const HIID FChildIndices      = AidChild|AidIndices;
const HIID FStepChildIndices  = AidStep|AidChild|AidIndices;
const HIID FParentIndices     = AidParent|AidIndices;
const HIID FIsStepParent      = AidIs|AidStep|AidParent;

const HIID FName          = AidName;
const HIID FNodeIndex     = AidNodeIndex;
const HIID FNodeGroups    = AidNode|AidGroups;
const HIID FAutoResample  = AidAuto|AidResample;
const HIID FControlStatus = AidControl|AidStatus;
const HIID FNewRequest    = AidNew|AidRequest;
const HIID FBreakpoint    = AidBreakpoint;
const HIID FBreakpointSingleShot = AidBreakpoint|AidSingle|AidShot;

const HIID FMTPolling      = AidMT|AidPolling;

const HIID FPublishingLevel = AidPublishing|AidLevel;

// cache stored here
const HIID FCache     = AidCache; // top level subrecord
  // subfields
  const HIID FResultCode = AidResult|AidCode;
  // const HIID FRequestId  = AidRequest|AidId; // already defined in MeqVocabulary

const HIID FCachePolicy     = AidCache|AidPolicy;
// if non-0, overrides the default parent count when making caching decisions
const HIID FCacheNumActiveParents = AidCache|AidNum|AidActive|AidParents;
// cache stats record
const HIID FCacheStats      = AidCache|AidStats;
  // and its fields
  const HIID FAllRequests     = AidAll|AidRequests;
  const HIID FNewRequests     = AidNew|AidRequests;
  const HIID FParents         = AidParents;

const HIID FLogPolicy     = AidLog|AidPolicy;


// profiling stats record
const HIID FProfilingStats      = AidProfiling|AidStats;
  const HIID FCPUMhz            = AidCPU|AidMHz;
  const HIID FTicksPerSecond    = AidTicks|AidPer|AidSecond;
  // and its fields
  const HIID FTotal         = AidTotal;
  // const HIID FChildren      = AidChildren; / already defined
  const HIID FGetResult     = AidGet|AidResult;

// flag for child init-records, specifying that child node may be directly
// linked to if it already exists
const HIID FLinkOrCreate = AidLink|AidOr|AidCreate;

const HIID FDependMask = AidDep|AidMask;
const HIID FActiveSymDeps = AidActive|AidSymdeps;

const HIID FCurrentRequestDepth = AidCurrent|AidRequest|AidDepth;

// const HIID FGenSymDep       = AidGen|AidSymdep;
// const HIID FGenSymDepGroup  = AidGen|AidSymdep|AidGroup;

const HIID FInternalInitIndex = AidInternal|AidInit|AidIndex;

//== fields for Node commands
const HIID FLevel = AidLevel;
const HIID FSingleShot = AidSingle|AidShot;
const HIID FRecursive = AidRecursive;

//== Event IDs
const HIID EvNodeResult = AidNode|AidResult;

// the All group
const HIID FAll = AidAll;

namespace MTPool
{
  class WorkOrder;
  class Brigade;
}

// A Node implements a locally-computed tree node with NodeFace children.

class Node : public NodeFace
{
  public:
    friend class MeqPython::PyNodeAccessor;
    typedef CountedRef<Node> Ref;

    //## Control state bitmasks. These are set in the control_status_ field
    typedef enum
    {
      //## control bits which can be set from outside
      //## node is active
      CS_ACTIVE              = 0x0001,
      //## mask of all writable control bits
      CS_MASK_CONTROL        = 0x000F,

      //## status bits (readonly)
      //## mask of bits representing type of most recent result
      CS_RES_MASK            = 0x0070,
      //## no result yet (node never executed)
      CS_RES_NONE            = 0x0000,
      //## most recent result was ok
      CS_RES_OK              = 0x0010,
      //## most recent result was a wait code
      CS_RES_WAIT            = 0x0020,
      //## most recent result was empty
      CS_RES_EMPTY           = 0x0030,
      //## most recent result was missing data
      CS_RES_MISSING         = 0x0040,
      //## most recent result was a fail
      CS_RES_FAIL            = 0x0050,
      //## flag: node is publishing
      CS_PUBLISHING          = 0x0100,
      //## flag: node has a cached result
      CS_CACHED              = 0x0200,
      //## flag: most recent result was returned from cache
      CS_RETCACHE            = 0x0400,
      //## flag: have breakpoints
      CS_BREAKPOINT          = 0x0800,
      //## flag: have single-shot breakpoints
      CS_BREAKPOINT_SS       = 0x1000,
      //## flag: stopped
      CS_STOPPED             = 0x2000,
      //## flag: stopped at breakpoint (in mt-mode, one node may stop
      //## at a breakpoint, and the others will simply stop).
      CS_STOP_BREAKPOINT     = 0x4000,
      //## mask of all bits related to breakpoints
      CS_MASK_BREAKPOINTS    = 0x7800,
      //## mask of all read-only status bits
      CS_MASK_STATUS         = 0xFFF0,

      //## first bit representing execution state
      CS_LSB_EXECSTATE       = 16,
      CS_MASK_EXECSTATE      = 0xF<<CS_LSB_EXECSTATE,
      //## exec states
      CS_ES_IDLE             = 0x0<<CS_LSB_EXECSTATE, //## inactive
      CS_ES_REQUEST          = 0x1<<CS_LSB_EXECSTATE, //## got request, checking cache
      CS_ES_COMMAND          = 0x2<<CS_LSB_EXECSTATE, //## checking/executing rider commands
      CS_ES_POLLING          = 0x3<<CS_LSB_EXECSTATE, //## polling children
      CS_ES_POLLING_CHILDREN = CS_ES_POLLING,
      CS_ES_EVALUATING       = 0x4<<CS_LSB_EXECSTATE, //## evaluating result

      //## mask of all bits (useful for breakpoints and such)
      CS_ALL                 = 0xFFFFFFFF,

      //## short mask for all breakpoints
      CS_BP_ALL              = 0xFF,
      //## mask of bits that may be set from outside (via setState)
      CS_WRITABLE_MASK    = CS_MASK_CONTROL,
    } ControlStatus;

    typedef enum
    {
      //## bits 0-4 automatically derived from exec state via breakpointMask() below

      //## special breakpoint on FAIL
      BP_FAIL  = 0x80,
      //## all breakpoints
      BP_ALL   = 0xFF
    } BreakpointMasks;

    //## cache management policies
    typedef enum
    {
      CACHE_NEVER      = -10,    //## nothing is cached at all
      CACHE_MINIMAL    = -1,     //## cache held until all parents get result
      CACHE_DEFAULT    =  0,     //## use global (forest default) policy
      //## note that a forest default of 0 actually corresponds to CACHE_SMART
      CACHE_SMART      =  1,     //## smart caching based on next-request hints,
                                 //## conservative (when in doubt, don't cache)
      CACHE_SMART_AGR  =  10,    //## smart caching based on next-request hints
                                 //## aggressive (when in doubt, cache)
                                 //## (NB: no difference right now)
      CACHE_ALWAYS     =  20     //## always cache
    } CachePolicy;

    //## logging policies
    typedef enum
    {
      LOG_NOTHING      = -10,    //## no logging at all
      LOG_DEFAULT      =  0,     //## use global (forest default) log policy
      //## note that a forest default of 0 actually corresponds to LOG_NOTHING
      LOG_RESULTS      =  10,    //## log all results
    } LogPolicy;

    // needs to be moved out
    typedef enum
    {
      // fail if child resolutions differ (default for e.g. Function nodes)
      RESAMPLE_FAIL      = -2,
      // do not do any resampling
      RESAMPLE_NONE      =  0,
      // integrate all child results to lowest resolution
      RESAMPLE_INTEGRATE = -1,
      // upsample all child results to highest resolution
      RESAMPLE_UPSAMPLE  =  1,
    } AutoResampleModes;


    //## helper function: returns a breakpoint mask corresponding to the given
    //## exec-state
    static inline int breakpointMask (int es)
    { return 1<<(es>>CS_LSB_EXECSTATE); }

    //## If nchildren>=0, specifies that exactly N=nch children is
    //## expected.
    //## If nchildren<0, specifies that at least N=-(nch+1) children are
    //## expected.
    //## If labels are supplied, this must be an array of N HIIDs.
    //## If nmandatory>=0, then only the first nmand children are
    //## considered mandatory, the rest may be missing
    Node (int nchildren=-1,const HIID *labels=0,int nmandatory=-1);

    virtual ~Node();

    //## pre-initializes the node by attaching its initial state
    //## and doing preliminary checks of children, etc.
    //## Ref will be transferred & COWed
    void attachInitRecord (DMI::Record::Ref &initrec, Forest* frst);

    //## pre-initializes node after loading it from a record.
    //## Ref will be transferred & COWed
    void reattachInitRecord (DMI::Record::Ref &initrec, Forest* frst);

    //====== NodeFace method
    //## Initializes node. By this stage, all parent/children nodes exist.
    virtual void init ();

    //====== NodeFace method
    //## initializes node after reloading (from, e.g., a file).
    //## In summary:
    //##  When creating new nodes:
    //##    1. create and attachInitRecord() on all nodes
    //##    2. call init() on ROOT nodes to finalize init
    //##  When reloading nodes from saved records:
    //##    1. create and reattachInitRecord() on all nodes
    //##    2. call reinit() on ALL nodes to finalize init
    virtual void reinit ();

    //## false before init()/reinit(), true afterwards.
    bool isInitialized () const
    { return internal_init_index_ >= 0; }

    const string & description () const
    { return description_; }

    NodeNursery & children ()
    { return children_; }
    const NodeNursery & children () const
    { return children_; }

    NodeNursery & stepchildren ()
    { return stepchildren_; }
    const NodeNursery & stepchildren () const
    { return stepchildren_; }

    // temporary, needs to be moved out
    void setAutoResample (int ar)
    { auto_resample_ = ar; }

    void disableAutoResample ()
    { disable_auto_resample_ = true; auto_resample_ = RESAMPLE_NONE; }

    //====== NodeFace methods
    //## Access to node state
    //## Each node has a state record. Some extra rapidly-changing info
    //## (timers, cache, etc.) is cached outside the state record for
    //## performance, and only synced on a syncState() call.
    virtual void getState (DMI::Record::Ref &ref) const
    { ref = staterec_; }
    virtual void getSyncState (DMI::Record::Ref &ref);

    //## Returns state record in a form suitable for saving.
    //## Basically equivalent to getSyncState(), but also populates
    //## parent information which is not normally in the record.
    void saveState (DMI::Record::Ref &ref);

    //## Control status word
    //## This is a bitmask specifying the various states of a node.
    //## These functions provide control status manipulation
    int getControlStatus () const
    { return control_status_; }

    bool getControlStatus (int mask) const
    { return control_status_&mask; }

    int getExecState () const
    { return control_status_&CS_MASK_EXECSTATE; }

    std::string getStrExecState () const
    { return getStrExecState(getExecState()); }

    static std::string getStrExecState (int state);


    //====== NodeFace method
    //## Changes to node state
    virtual void setState (DMI::Record::Ref &rec);

    //====== NodeFace method
    //## Executes a request on the node
    virtual int execute (Result::Ref &resref,const Request &req,int depth) throw();

    //====== NodeFace method
    //## Processes node-specific commands. Args is expected to contain
    //## a DMI::Record. Standard commands defined at this level are:
    //## State, args: {any state sub-record}
    //##    Changes the state of the node for the fields found in args record.
    //## Set.State, args: {state={any state sub-record}}
    //##    Alternative version. Changes the state of the node for the fields
    //##    found in args.state.
    //## Clear.Cache, args: {recursive=bool} (optional, default false)
    //##    Clears cache, optionally recursively
    //## Clear.Cache.Recursive, args: none
    //##    Clears cache recursively
    //## Set.Publish.Level args: {level=int} (optional, default 1)
    //##    equivalent to setPublishLevel(level)
    //## Set.Breakpoint args: {breakpoint=int,    # optional, default REQUEST
    //##                       single_shot=bool}  # optional, default false
    //##    equivalent to setBreakpoint(breakpoint,single_shot)
    //## Clear.Breakpoint args: {breakpoint=int,    # optional, default ALL
    //##                         single_shot=bool}  # optional, default false
    //##    equivalent to clearBreakpoint(breakpoint,single_shot)
    //## None of the commands defined here return a Result. If the
    //## command is passed in via a Request rider, this method will be
    //## called from execute() BEFORE polling children.
    //## If subclasses that redefine this to return a Result for some commands,
    //## note the following: normally the same Result is passed into
    //## getResult() and discoverSpids(), so these methods should take care
    //## to modify but not replace it. However, if a child poll fails and a
    //## collect-fails policy is in effect, the collected fails will be
    //## attached to the Result, so any Result returned from
    //## processCommand() by a subclass will be lost.
    virtual int processCommand (Result::Ref &resref,
                                const HIID &command,
                                DMI::Record::Ref &args,
                                const RequestId &rqid = RequestId(),
                                int verbosity=0);

    //## true while node is inside execute()
    bool isExecuting () const
    { return executing_; }

    //## current (or most recent) request id being processed
    const HIID & currentRequestId () const
    { return current_reqid_; }

    const Request & currentRequest () const
    { return *current_request_; }

    //====== NodeFace method
    //## Clears cache (optionally recursively)
    //## If quiet is false, updates control_status but does not advertise
    //## marker is used to avoid entering the same node again when clearing recursively
    virtual void clearCache (bool recursive=false,long marker=0) throw();

    //## sets verbosity level for publishing of state snapshots
    //## level 0 means no publishing
    //## at the moment, anything >0 just publishes a snapshot after
    //## each execute().
    void setPublishingLevel (int level=1);

    Forest & forest ()
    { return *forest_; }

    //## condition variable used to signal when Node::execute() is returning
    //## Also used as a mutex to protect the executing_ flag.
    Thread::Condition & execCond ()
    { return exec_cond_; }

    Thread::Mutex & stateMutex () const
    { return state_mutex_; }

    //## returns true if Node should poll its children in multithreaded mode
    bool multithreaded () const
    { return children().multiThreaded(); }

    int numParents () const
    { return parents_.size(); }

    //## returns number of children. Note that child_indices_.size() is always
    //## identical to children().size(), but is setup earlier on (i.e.
    //## before resolveLinks()), so it's mopre suitable.
    int numChildren () const
    { return child_indices_.size(); }

    //## return parent by number
    NodeFace & getParent (int i)
    { return parents_[i].ref.dewr(); }

    const NodeFace & getParent (int i) const
    { return parents_[i].ref.deref(); }

    const std::vector<HIID> & getNodeGroups () const
    { return node_groups_; }


    int getDependMask () const
    { return depend_mask_; }

    int cachePolicy () const
    { return cache_policy_; }

    void setCachePolicy (int policy)
    { cache_policy_ = policy; }

    int logPolicy () const
    { return log_policy_; }

    void setLogPolicy (int policy)
    { log_policy_ = policy; }

    //## depth of currently executing request
    int currentRequestDepth () const
    { return current_request_depth_; }

    //## checking level used for extra sanity checks (presumably expensive),
    //## set to non-0 for debugging
    static int checkingLevel ()
    { return checking_level_; }

    static void setCheckingLevel (int level)
    { checking_level_ = level; }

    //## sets breakpoint(s)
    void setBreakpoint (int bpmask,bool single_shot=false);
    //## clears breakpoint(s)
    void clearBreakpoint (int bpmask,bool single_shot=false);

    int getBreakpoints (bool single_shot=false) const
    { return single_shot ? breakpoints_ss_ : breakpoints_; }


    //## Clones a node.
    //## Currently not implemented (throws exception)
    virtual CountedRefTarget* clone(int flags = 0, int depth = 0) const;

    //## Returns the class TypeId
    virtual TypeId objectType() const
    { return TpMeqNode; }

    //## Un-serialize.
    virtual int fromBlock (BlockSet& set);
    //## Serialize.
    virtual int toBlock (BlockSet &set) const;

    //## Standard debug info method
    virtual string sdebug(int detail = 0, const string &prefix = "", const char *name = 0) const;

  protected:
    //====== NodeFace method
    //## called by parent node (from holdChildCaches() usually) to hint to
    //## a child whether it needs to hold cache or not
    virtual void holdCache (bool hold) throw();

    //====== NodeFace method
    //## marks the current cache (if any) of the node with
    //## Forest::getStateDependMask(). If node is already dependent on
    //## state, does nothing. Otherwise, recursively does same to parents.
    //## This is called from setState() to make sure that parents of the
    //## current node update themselves properly when receiving a request
    //## with a different state id (which is usually incremented by the
    //## request sequencer)
    virtual void propagateStateDependency ();

    //## clears state dependency introduced by method above. Used by Nodes such as
    //## the Solver to indicate that they have accounted for all state changes above them
    void clearStateDependency ()
    { has_state_dep_ = false; }

    //## recursively publishes status messages for parents of node
    virtual void publishParentalStatus ();


    //## ----------------- control state management
    //## sets new control state and notifies the Forest object
    //## (the Forest may publish messages, etc.)
    //## if sync is true, the state record is immediately updated
    void setControlStatus (int newst,bool sync=false);

    //## changes execution state and control status in one call, checks
    //## if breakpoints have been hit
    void setExecState (int es,int cs,bool sync=false);

    //## overloaded function to change exec state but not rest of control status
    void setExecState (int es)
    { setExecState(es,control_status_,false); }

    //------------------ generating events
    //## posts an event on behalf of the node. posting is done via the
    //## forest
    void postEvent (const HIID &type,const ObjRef &data = _dummy_objref );
    //## posts a message event, will post a record of the form
    //## {node=nodename,<type>=msg,...} or {node=nodename,<type>=msg,data=data}
    //## If data is a record then the first form is used, with node and <type>
    //## fields being inserted
    void postMessage (const string &msg,const ObjRef &data = _dummy_objref,AtomicID type=AidMessage);
    //## shortcut for posting a message of type Error
    void postError   (const string &msg,const ObjRef &data = _dummy_objref )
    { postMessage(msg,data,AidError); }


    //## called to enable/disable multithreaded polling on a node
    //## (must be enabled in forest first)
    void enableMultiThreadedPolling (bool enable=true);


    //## called from init() and setState(), meant to update internal state
    //## in accordance to rec. If initializing==true (i.e. when called from
    //## init()), rec is a complete state record.
    //## Record will be COWed as needed.
    virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);

    //## Called from execute() to collect the child results for a given request.
    //## Default behaviour is to call NodeNursery::syncPoll() on children,
    //## followed by NodeNursery::backgroundPoll() on stepchildren.
    //## Some special nodes may override this if they implement their own
    //## polling strategies.
    virtual int pollChildren (Result::Ref &resref,
                              std::vector<Result::Ref> &childres,
                              const Request &req);

    //## Called from execute() to compute the result of a request, when
    //## the request contains a Cells field, and eval mode is GET_RESULT
    //## or higher.
    //##    childres: vector of child results (empty if no children);
    //##    req:      request;
    //##    newreq:   true if the request is new.
    //## Result should be created and attached to resref. Return code indicates
    //## result properties. If the RES_WAIT flag is returned, then no result is
    //## expected; otherwise a Result must be attached to the ref.
    //## RES_FAIL may be returned to indicate complete failure.
    virtual int getResult (Result::Ref &resref,
                           const std::vector<Result::Ref> &childres,
                           const Request &req,bool newreq);

    //## Called from execute() when request contains a Cells field, and eval
    //## mode is DISCOVER_SPIDS
    //##    resref:   ref to Result, may be invalid, in which case
    //##              a result should be attached as needed.
    //##    childres: vector of child results (empty if no children);
    //##    cells:    cells for which spids are requested;
    //##    req:      request for which spids are requested;
    //## Return code indicates result properties, and is added
    //## to the execute() return code.
    //## RES_FAIL may be returned to indicate complete failure.
    //## Default version simply merges spid maps of all children.
    virtual int discoverSpids (Result::Ref &resref,
                               const std::vector<Result::Ref> &childres,
                               const Request &req);

    //## ----------------- symdep and depmask management ------------------------

    //## sets the node's dependency mask
    void setDependMask (int mask);

    //## access to the node's symdep map
    const SymdepMap & symdeps () const
    { return symdeps_; }
    SymdepMap & symdeps ()
    { return symdeps_; }

    //## Sets the node's set of active symbolic dependencies.
    //## This will recompute depend_mask_ automatically
    void setActiveSymDeps (const HIID deps[],int ndeps)
    { setDependMask(symdeps().setActive(deps,ndeps)); }

    void setActiveSymDeps (const HIID &dep)
    { setDependMask(symdeps().setActive(dep)); }

    void setActiveSymDeps (const std::vector<HIID> &deps)
    { setDependMask(symdeps().setActive(deps)); }

    void setActiveSymDeps ()
    { setDependMask(symdeps().setActive()); }

    //## ----------------- misc helper methods ----------------------------------

    // helper function, placeholder for in-node resampler
    // if autoresample is RESAMPLE_NONE, does nothing.
    // if autoresample is RESAMPLE_FAIL, checks that all child results
    // has the same cells and throws an exception if not.
    // Attaches these cells to rescells.
    void checkChildCells (Cells::Ref &rescells,const std::vector<Result::Ref> &childres);

    //## write-access to the state record
    DMI::Record & wstate()
    { return staterec_(); }

    //## sets the current request
    void setCurrentRequest (const Request &req);

    //## Checks for cached result; if hit, attaches it to ref and returns true.
    //## On a miss, clears the cache (NB: for now!)
    bool getCachedResult (int &retcode,Result::Ref &ref,const Request &req);

    //## Conditionally stores result in cache according to current policy.
    //## Returns the retcode.
    int  cacheResult   (const Result::Ref &ref,const Request &req,int retcode);

    //## MakeNodeException creates an exception with the given message,
    //## and insert the node identifier
    #define MakeNodeExceptionOfType(exctype,msg) exctype(msg,description(),__HERE__)

    #define MakeNodeException(msg) MakeNodeExceptionOfType(LOFAR::Exception,msg)

    //## NodeThrow can be used to throw an exception, with the message
    //## passed through makeMessage()
    #define NodeThrow(exc,msg) \
      { throw MakeNodeExceptionOfType(exc,msg); }
    //## NodeThrow1 thows a FailWithoutCleanup exception, with the message
    //## passed through makeMessage()
    #define NodeThrow1(msg) NodeThrow(FailWithoutCleanup,msg)

    //## Helper method for setStateImpl(). Meant to check for immutable state
    //## fields. Checks if record rec contains the given field, throws a
    //## FailWithoutCleanup with the appropriate message if it does.
    //## Defined as macro so that exception gets proper file/line info
    #define protectStateField(rec,field) \
      { if( (rec)[field].exists() ) \
          NodeThrow(FailWithoutCleanup,"state field "+(field).toString()+" not reconfigurable"); }

    //## Returns HIID label for child #i
    //## If i>(number of defined labels), then this is simply "i".
    HIID getChildLabel (int ich) const
    { return ich<int(child_labels_.size()) ? child_labels_[ich] : AtomicID(ich); }

    //## Performs reverse lookup, returns number for child labelled 'label'.
    //## If label is not defined but is numeric, returns that number.
    //## otherwise returns -1.
    int  childLabelToNumber (const HIID &label) const;

    //## tells children (including stepchildren) to hold or release cache.
    //## if hold=false, holdCache(false) is called on all children
    //## if hold=true, holdChild(true) is called on those childeren whose
    //##   child_retcode or stepchild_retcode_ is not dependant on depmask;
    //##   the rest get holdCache(false)
    void holdChildCaches (bool hold,int depmask=0);

    //## access to profiling timers
    typedef struct
    {
      LOFAR::NSTimer total;
      LOFAR::NSTimer children;
      LOFAR::NSTimer getresult;
    } ProfilingTimers;

    ProfilingTimers & timers ()
    { return timers_; }

    //## helper methods for keeping the state mutex locked/unlocked while polling children
    void lockStateMutex ();
    void unlockStateMutex ();

    //## this flag is set inside Node::execute() to prevent reentrancy
    bool executing_;

    //## condition variable used to signal when executing_ is cleared.
    Thread::Condition exec_cond_;

  private:
    //## sets up nursery objects based on the child_indices_ and stepchild_indices_
    //## vectors which are populated by init() or reinit(). Called
    //## from resolveLinks(), and also when loading the node from a file.
    void setupNurseries ();

    //## recreates the parents_ vector based on fields in the state record
    //## Used by relinkRelatives() after loading the node from a record
    void relinkParents ();

    // callbacks that map to [un]lockStateMutex() via the pnode argument. Used
    // with NodeNursery
    static void Node_lockStateMutex (void *pnode);
    static void Node_unlockStateMutex (void *pnode);

    //## processes the request rider, and calls processCommand() as appropriate.
    int processRequestRider (Result::Ref &resref,const Request &req);

    //## helper function for above. Calls processCommand() for every field
    //## in the list. List must therefore may only contain sub-records
    //## (or invalid refs)
    int processCommands (Result::Ref &resref,const DMI::Record &list,const RequestId &rqid);

    //## The state mutex is locked whenever a node is liable to change its
    //## state. Normally this is locked through all of execute(), except
    //## when we go to poll children.
    mutable Thread::Mutex state_mutex_;
    //## this points to the current state_mutex lock object, which
    //## is allocated on the stack in Node::execute(). pollChildren()
    //## needs to release this lock temporarily.
    Thread::Mutex::Lock * pstate_lock_;

    //## flag used to keep track of whether parental branch has already published
    bool parent_status_published_;

    //## control_status word
    int control_status_;

    //## cache policy setting
    int cache_policy_;

    //## log policy setting
    int log_policy_;

    //## flag: cache should be made explicitly dependent on "State". This
    //## flag is "dropped" on us from child nodes when their state changes, and is
    //## primarily meant as a kludge against the Solver-ReqSeq conundrum.
    //## Nodes clear this flag in execute(), and set it via markStateDependency().
    //## The Solver clears this flag explicitly.
    bool has_state_dep_;

    //## profiling timers
    ProfilingTimers timers_;

    //## convenience class: construct from timer to start timer,
    //## destroy to stop timer
    class TimerStart
    {
      public:
        TimerStart (LOFAR::NSTimer &tm)
          : timer_(tm)
        { timer_.start(); }

        ~TimerStart ()
        { timer_.stop(); }

      private:
        LOFAR::NSTimer & timer_;
    };

    //## helper function to cleanup upon exit from execute() (stops timers,
    //## clears flags, etc.) Retcode is passed as-is, making this a handy
    //## wrapper around the return value
    int exitExecute (int retcode)
    {
#ifdef DISABLE_NODE_MT
      executing_ = false;
#else
      //## if we're aborting execute() while a poll is in progress,
      //## we need to clean up
      children().finishPoll();
      stepchildren().finishPoll();
      Thread::Mutex::Lock lock(execCond());
      executing_ = false;
      execCond().broadcast();
#endif
      timers_.total.stop();
      return retcode;
    }

    //## helper function to exit when the abort flag is raised
    int exitAbort (int retcode)
    {
      // abort any running polls
      children().abortPoll();
      stepchildren().abortPoll();
      Result::Ref ref(new Result(0));
      cdebug(3)<<"  abort flag raised, returning"<<endl;
      Thread::Mutex::Lock lock(execCond());
      setExecState(CS_ES_IDLE,control_status_|CS_RES_EMPTY);
      return exitExecute(retcode|RES_ABORT);
    }

    //## vector of parent info
    typedef struct
    {
      NodeFace::Ref ref;
    } ParentEntry;
    std::vector<ParentEntry> parents_;
    // vector of parent indices
    std::vector<int> parent_indices_;

    //======= CHILD INFORMATION

    NodeNursery children_;
    NodeNursery stepchildren_;

    //## vectors of child and stepchild indices
    std::vector<int> child_indices_;
    std::vector<int> stepchild_indices_;

    //## child labels specified in constructor. Labelled children may
    //## be assigned via the record [label=child] form in init().
    //## If no labels specified, this is initialized with trivial HIIDs:
    //## '0', '1', etc.
    vector<HIID> child_labels_;
    //## map from child labels to numbers, reverse of the child_labels_ vector.
    //## this is populated in the constructor
    typedef std::map<HIID,int> ChildLabelMap;
    ChildLabelMap child_label_map_;
    //## set up in constructor. Minimum number of children required,
    //## and max number allowed (-1 if unlimited).
    int check_min_children_;
    int check_max_children_;


    //======= STATE RECORD and other state

    DMI::Record::Ref staterec_;

    //## node description (from state record)
    string description_;

    //## our managing forest object
    Forest *forest_;

    //## vector of child results collected by pollChildren()
    std::vector<Result::Ref> child_results_;

    //## current (or last executed) request, set in execute()
    HIID current_reqid_;
    Request::Ref current_request_;

    //## flag set in execute() indicating a new request
    bool new_request_;

    //## Dependency mask indicating which parts of a RequestId the node's own
    //## value depends on (this is in addition to any child dependencies).
    int depend_mask_;

    //## Dependency mask indicating dependency on domain (a constant, essentially)
    int domain_depend_mask_;

    //## A node's set of symdeps
    SymdepMap symdeps_;

    //## used by init() to go into a node only once when resolving
    //## recursively. -1 when node is created and before init() is called.
    int internal_init_index_;

    int current_request_depth_;

    //## used during async polling
    int async_poll_child_;

    //## Group(s) that a node belongs to. Node groups determine
    std::vector<HIID> node_groups_;

//     //##Documentation
//     //## auto-resample mode for child results
// needs to be moved out
    int auto_resample_;
//     //##Documentation
//     //## flag: auto-resampling for child results is not available
// needs to be moved out
    bool disable_auto_resample_;

    //## verbosity level of snapshots being published, 0 if none
    int publishing_level_;

    //## mask of current breakpoints
    int breakpoints_;
    //## mask of current single-shot breakpoints
    int breakpoints_ss_;

    //## real cache policy (equal to forest policy if ours is 0)
    int actual_cache_policy_;

    //## cache management info
    //## The Cache class encapsulates a cached result
    class Cache
    {
      public:
        //## sets the cache
        void set (const Result::Ref &resref,const Request &req,int code)
        {
          result  = resref;
          rqid    = req.id();
          rescode = code;
          recref_.detach();
          is_valid = true;
        }
        //## clears the cache
        void clear ()
        {
          if( !(rescode&RES_FAIL) ) //## fail results preserved
            result.detach();
          is_valid = false;
          recref_.detach();
        }
        //## is cache valid?
        bool valid () const
        {
          return is_valid && result.valid();
        }

        //## rebuilds (if needed) and returns a representative cache record
        const Record & record ();
        //## resets cache from record, returns validity flag
        bool fromRecord (const Record &rec);

        Result::Ref result;
        RequestId   rqid;
        int         rescode;
        bool        is_valid;

        long        last_clear_cache_marker_;

        //## flag: ignore parent requests to release cache. This flag
        // is normally cleared, but is raised when an empty result is returned in
        // response to a DISCOVER_SPIDS or PARM_UPDATE request, thus protecting
        // the actual cache. When parent request that the cache be cleared, and
        // this flag is raised. the actual cache survives.
        bool ignore_parent_releases_;

        //## cache mutex held during cache ops
        Thread::Mutex mutex;
      private:
        DMI::Record::Ref recref_;
    };

    Cache cache_;

    //## flag: release cache when all parents allow it
    bool parents_release_cache_;

    //## cache statistics
    DMI::Record::Ref cache_stats_;
    typedef struct
    {
      int req;        //## total number of requests
      int hits;       //## total number of cache hits
      int miss;       //## total number of cache misses (wrong cache)
      int none;       //## total number of requests with no cache available
      int cached;     //## total number of all cached results
      int longcached; //## total number of results cached persistently
    } CacheStats;
    //## total cache stats (including same requests)
    CacheStats * pcs_total_;
    //## cache stats for new requests only
    CacheStats * pcs_new_;
    typedef struct
    {
      int npar;     //## number of parents
      int nact;     //## number of active parents
      int nhint;    //## number of parents that issued hold/release hints
      int nhold;    //## of which, how many were hold hints
    } CacheParentInfo;
    CacheParentInfo * pcparents_;
    //## another copy of the result code goes here
    int * pcrescode_;

    //## profiling stats
    DMI::Record::Ref profile_stats_;
    typedef struct
    {
      double total;
      double count;
      double average;
    }
    ProfilingStats;

    void fillProfilingStats (ProfilingStats *st,const LOFAR::NSTimer &timer);

    ProfilingStats * pprof_total_;
    ProfilingStats * pprof_children_;
    ProfilingStats * pprof_getresult_;

    static int checking_level_;

    static ObjRef _dummy_objref;


};


} // namespace Meq

#endif /* MeqSERVER_SRC_NODE_H_HEADER_INCLUDED_E5514413 */
