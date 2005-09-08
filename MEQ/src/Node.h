//#  Node.h: base MeqNode class
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
#ifndef MEQ_NODE_H_HEADER_INCLUDED_E5514413
#define MEQ_NODE_H_HEADER_INCLUDED_E5514413
    
#include <Common/Stopwatch.h>
#include <DMI/Record.h>
#include <MEQ/EventGenerator.h>
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
#pragma aid Add Clear Known Active Gen Dep Deps Symdep Symdeps Mask Masks
#pragma aid Parm Value Resolution Domain Dataset Resolve Parent Init Id
#pragma aid Link Or Create Control Status New Breakpoint Single Shot Step
#pragma aid Cache Policy Stats All New Requests Parents Num Active
#pragma aid Profiling Stats Total Children Get Result Ticks Per Second CPU MHz

namespace Meq 
{ 
using namespace DMI;

class Forest;
class Request;

//== Node state fields
const HIID FChildren      = AidChildren;
const HIID FChildrenNames = AidChildren|AidName;
const HIID FStepChildren  = AidStep|AidChildren;
const HIID FStepChildrenNames = AidStep|AidChildren|AidName;
const HIID FName          = AidName;
const HIID FNodeIndex     = AidNodeIndex;
const HIID FNodeGroups    = AidNode|AidGroups;
const HIID FAutoResample  = AidAuto|AidResample; 
const HIID FControlStatus = AidControl|AidStatus;
const HIID FNewRequest    = AidNew|AidRequest;
const HIID FBreakpoint    = AidBreakpoint;
const HIID FBreakpointSingleShot = AidBreakpoint|AidSingle|AidShot;

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
const HIID FKnownSymDeps = AidKnown|AidSymdeps;
const HIID FActiveSymDeps = AidActive|AidSymdeps;
const HIID FSymDepMasks = AidSymdep|AidMasks;

// const HIID FGenSymDep       = AidGen|AidSymdep;
// const HIID FGenSymDepGroup  = AidGen|AidSymdep|AidGroup;

const HIID FResolveParentId = AidResolve|AidParent|AidId;

//== Node commands
const HIID FResolveChildren = AidResolve|AidChildren;
const HIID FInitDepMask = AidInit|AidDep|AidMask;
const HIID FClearDepMask = AidClear|AidDep|AidMask;
const HIID FAddDepMask = AidAdd|AidDep|AidMask;

// the All group
const HIID FAll = AidAll;

//##ModelId=3F5F436202FE
class Node : public DMI::BObj
{
  public:
    //##ModelId=3F5F43620304
    typedef CountedRef<Node> Ref;
  
    //##ModelId=3F698825005B
    //##Documentation
    //## These are flags returned by execute(), and processCommands(),
    //## indicating result properties.
    //## The lower RQIDM_NBITS (currently 16) bits are reserved for request 
    //## dependency masks; see RequestId.h for details.
    //## Note that the meaning of the bits is chosen so that the flags of
    //## of a node's result will generally be a bitwise OR of the child
    //## flags, plus any flags added by the node itself.
    typedef enum 
    {
      // Result should not be cached, either because it is volatile (i.e. may 
      // change even if the request doesn't), or because node state has changed.
      // In always-cache mode, we may still cache it (for debugging), but never
      // use such a cache!
      RES_VOLATILE     = 0x01<<RQIDM_NBITS,  
      // Result has been updated (as opposed to pulled from the node's cache)
      RES_UPDATED      = 0x02<<RQIDM_NBITS,  
      // Result not yet available, must wait. This flag may be combined
      // with other flags (except FAIL) to indicate dependencies.
      RES_WAIT         = 0x10<<RQIDM_NBITS,    
      // Result is a complete fail (i.e. not a mix of failed and OK VellSets,
      // just a complete fail)
      RES_FAIL         = 0x80<<RQIDM_NBITS    
    } ResultAttributes;
    
    //##Documentation
    //## Auto-resample modes. Nodes may enable automatic resampling of child
    //## results, for cases where children return results at different 
    //## resolutions
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
      
    //##Documentation
    //## Control state bitmasks. These are set in the control_status_ field
    typedef enum 
    { 
      // control bits which can be set from outside
      // node is active
      CS_ACTIVE              = 0x0001,
      // mask of all writable control bits
      CS_MASK_CONTROL        = 0x000F,
          
      // status bits (readonly)
      // mask of bits representing type of most recent result
      CS_RES_MASK            = 0x0070,
      // no result yet (node never executed)
      CS_RES_NONE            = 0x0000,
      // most recent result was ok
      CS_RES_OK              = 0x0010,
      // most recent result was a wait code
      CS_RES_WAIT            = 0x0020,
      // most recent result was empty
      CS_RES_EMPTY           = 0x0030,
      // most recent result was missing data
      CS_RES_MISSING         = 0x0040,
      // most recent result was a fail
      CS_RES_FAIL            = 0x0050,
      // flag: node is publishing
      CS_PUBLISHING          = 0x0100,
      // flag: node has a cached result
      CS_CACHED              = 0x0200,
      // flag: most recent result was returned from cache 
      CS_RETCACHE            = 0x0400,
      // flag: have breakpoints
      CS_BREAKPOINT          = 0x0800,
      // flag: have single-shot breakpoints
      CS_BREAKPOINT_SS       = 0x1000,
      // flag: stopped at breakpoint
      CS_STOP_BREAKPOINT     = 0x2000,
      // mask of all read-only status bits
      CS_MASK_STATUS         = 0xFFF0,
          
      // first bit representing execution state
      CS_LSB_EXECSTATE       = 16,
      CS_MASK_EXECSTATE      = 0xF<<CS_LSB_EXECSTATE,
      // exec states
      CS_ES_IDLE             = 0x0<<CS_LSB_EXECSTATE, // inactive
      CS_ES_REQUEST          = 0x1<<CS_LSB_EXECSTATE, // got request, checking cache
      CS_ES_COMMAND          = 0x2<<CS_LSB_EXECSTATE, // checking/executing rider commands
      CS_ES_POLLING          = 0x3<<CS_LSB_EXECSTATE, // polling children
      CS_ES_POLLING_CHILDREN = CS_ES_POLLING,
      CS_ES_EVALUATING       = 0x4<<CS_LSB_EXECSTATE, // evaluating result
      
      // mask of all bits (useful for breakpoints and such)
      CS_ALL                 = 0xFFFFFFFF,
      
      // short mask for all breakpoints
      CS_BP_ALL              = 0xFF,
      // mask of bits that may be set from outside (via setState)
      CS_WRITABLE_MASK    = CS_MASK_CONTROL,
    } ControlStatus;

    // cache management policies
    typedef enum
    {
      CACHE_NEVER      = -10,    // nothing is cached at all
      CACHE_MINIMAL    = -1,     // cache held until all parents get result
      CACHE_DEFAULT    =  0,     // use global (forest default) policy
      CACHE_SMART      =  1,     // smart caching based on next-request hints, 
                                 // conservative (when in doubt, don't cache)
      CACHE_SMART_AGR  =  10,    // smart caching based on next-request hints
                                 // aggressive (when in doubt, cache)
                                 // (NB: no difference right now)
      CACHE_ALWAYS     =  20     // always cache
    } CachePolicy;
    
    // helper function: returns a breakpoint mask corresponding to the given exec-state
    static inline int breakpointMask (int execstate)
    { return 1<<(execstate>>CS_LSB_EXECSTATE); }

    //##ModelId=3F5F43E000A0
    //##Documentation
    //## Child labels may be specified in constructror as a C array of HIIDs.
    //## If labels==0, no labels are defined.
    //## If nchildren>=0, specifies that an exact number of children is expected.
    //## If nmandatory>0, spefifies that at least nmandatory children are 
    //##    expected; note that if labels are supplied, then the first 
    //##    nmand labels are considered the mandatory ones, and the rest are
    //##    optional
    Node (int nchildren=-1,const HIID *labels = 0,int nmandatory=0);
        
    //##ModelId=3F5F44A401BC
    virtual ~Node();

    //##ModelId=3F5F45D202D5
    // initializes node. Ref will be transferred & COWed
    virtual void init (DMI::Record::Ref &initrec, Forest* frst);
    
    //##ModelId=400E530F0090
    // reinitializes node after loading. Ref will be transferred & COWed
    virtual void reinit (DMI::Record::Ref &initrec, Forest* frst);

    // Resolves children and symdeps. Must be called after init(),
    // before a node is executed() for the first time.
    // When called recursively, parent is set to the parent node, so
    // that the parents_ vector is populated. Stepparent is true
    // if we are a stepchild of that parent.
    // Root nodes are called with a parent of 0.
    int resolve (Node *parent,bool stepparent,DMI::Record::Ref &depmasks,int rsid);
        
    //##ModelId=3F83FAC80375
    void resolveChildren (bool recursive=true);
    
    //##ModelId=400E531101C8
    // relinks children after a node has been reinitialized from its state record
    void relinkChildren ();
        
    //##ModelId=3F5F44820166
    const string & name() const
    { return myname_; }
    
    //##ModelId=400E5311029C
    int nodeIndex() const 
    { return node_index_; }
    
    //##ModelId=400E53110383
    string className() const
    { return objectType().toString(); }
    
    //##ModelId=3F5F441602D2
    // returns state record
    const DMI::Record & state() const
    { return *staterec_; }
    
    // syncs rapidly-updated object state (that may not be immediately
    // put into the state record)
    const DMI::Record & syncState();
    
    bool hasState () const
    { return staterec_.valid(); }
    
    int getControlStatus () const
    { return control_status_; }
    
    bool getControlStatus (int mask) const
    { return control_status_&mask; }
    
    int getExecState () const
    { return control_status_&CS_MASK_EXECSTATE; } 
    
    std::string getStrExecState () const
    { return getStrExecState(getExecState()); }
    
    static std::string getStrExecState (int state);
    
    //##ModelId=400E53120082
    void setNodeIndex (int nodeindex);
    
    //##ModelId=3F5F445A00AC
    void setState (DMI::Record::Ref &rec);
    
    //##ModelId=3F6726C4039D
    int execute (Result::Ref &resref, const Request &);
    
    //##ModelId=3F9919B00313
    const HIID & currentRequestId () const
    { return current_reqid_; }
    
    int autoResample () const
    { return auto_resample_; }
    
    void setAutoResample (int mode)
    { auto_resample_ = mode; }
    
    //##ModelId=400E531300C8
    //##Documentation
    //## Clears cache (optionally recursively)
    //## If quiet is false, updates control_status but does not advertise
    void clearCache (bool recursive=false,bool quiet=false);
    
    //## called by parent node (from holdChildCaches() usually) to hint to 
    //## a child whether it needs to hold cache or not
    void holdCache (bool hold);
    
    
    //##Documentation
    //## adds an event slot to which generated results will be published
    void addResultSubscriber    (const EventSlot &slot);
    //##Documentation
    //## removes subscription for specified event slot
    void removeResultSubscriber (const EventSlot &slot);
    //##Documentation
    //## removes all subscriptions for specified recepient
    void removeResultSubscriber (const EventRecepient *recepient);
    
    //##ModelId=3F98D9D20372
    Forest & forest ()
    { return *forest_; }

    //##ModelId=3F85710E002E
    int numChildren () const
    { return children_.size(); }
    
    int numStepChildren () const
    { return stepchildren_.size(); }
    
    int numParents () const
    { return parents_.size(); }
    
    //##ModelId=3F85710E011F
    //## return child by number
    Node & getChild (int i)
    {
      FailWhen(!children_[i].valid(),"unresolved child");
      return children_[i].dewr();
    }
    const Node & getChild (int i) const
    {
      FailWhen(!children_[i].valid(),"unresolved child");
      return children_[i].deref();
    }
    //## return stepchild by number
    Node & getStepChild (int i)
    {
      FailWhen(!stepchildren_[i].valid(),"unresolved stepchild");
      return stepchildren_[i].dewr();
    }
    const Node & getStepChild (int i) const
    {
      FailWhen(!stepchildren_[i].valid(),"unresolved stepchild");
      return stepchildren_[i].deref();
    }
    //## return parent by number
    Node & getParent (int i)
    { return parents_[i].ref.dewr(); }
    
    const Node & getParent (int i) const
    { return parents_[i].ref.deref(); }
    
    bool isStepParent (int i) const
    { return parents_[i].stepparent; }
    
    //##ModelId=3F85710E028E
    //## return child by ID
    Node & getChild (const HIID &id);
    
    //##ModelId=3F98D9D20201
    int getChildNumber (const HIID &id);
    
    const std::string & childName (int i) const;
    
    const std::vector<HIID> & getNodeGroups () const
    { return node_groups_; }
    
    int getDependMask () const
    { return depend_mask_; }
    
    const std::vector<HIID> & getKnownSymDeps () const
    { return known_symdeps_; }
    
    const std::vector<HIID> & getActiveSymDeps () const
    { return active_symdeps_; }
    
// 18/04/05 OMS: phasing this out, ModRes will need to be rewritten a-la Solver
//     //##Documentation
//     //## Gets the full generated symdep mask (bitwise OR of all generated
//     //## symdeps)
//     int getGenSymDepMask () const
//     { return gen_symdep_fullmask_; }
//     
//     //##Documentation
//     //## Gets the generated symdep mask for a specific symdep (0 if not found)
//     int getGenSymDepMask (const HIID &symdep) const;
            
    //##Documentation
    //## checking level used for extra sanity checks (presumably expensive), 
    //## set to non-0 for debugging
    static int checkingLevel ()
    { return checking_level_; }
    
    static void setCheckingLevel (int level)
    { checking_level_ = level; }

    // sets breakpoint(s)
    void setBreakpoint (int bpmask,bool single_shot=false);
    // clears breakpoint(s)
    void clearBreakpoint (int bpmask,bool single_shot=false);
    
    int getBreakpoints (bool single_shot=false) const
    { return single_shot ? breakpoints_ss_ : breakpoints_; }
    
    
    //##ModelId=3F5F4363030F
    //##Documentation
    //## Clones a node. 
    //## Currently not implemented (throws exception)
    virtual CountedRefTarget* clone(int flags = 0, int depth = 0) const;
    
    //##ModelId=3F5F43630313
    //##Documentation
    //## Returns the class TypeId
    virtual TypeId objectType() const
    { return TpMeqNode; }
    
    //##ModelId=3F5F43630315
    //##Documentation
    //## Un-serialize.
    //## currently not implemented
    virtual int fromBlock (BlockSet& set);
    //##ModelId=3F5F43630318
    //##Documentation
    //## Serialize.
    //## currently not implemented
    virtual int toBlock (BlockSet &set) const;
    
    //##ModelId=3F5F48180303
    //##Documentation
    //## Standard debug info method
    virtual string sdebug(int detail = 1, const string &prefix = "", const char *name = 0) const;

    //##ModelId=3F8433C1039E
    LocalDebugContext;


    //##Documentation
    //## Rider is a utility class providing functions for manipulating
    //## the request rider.
    class Rider
    {   
      public:
      //##Documentation
      //## bitwise flags for methods below. Note that they are cumulative
      typedef enum {
        NEW_RIDER     = 0x01,
        NEW_GROUPREC  = 0x02,
        NEW_CMDREC    = 0x04,
        NEW_ALL       = 0x07
      } RiderFlags;
        
      //##Documentation
      //## Clears the rider from the request, if any.
      //## Reqref will be COWed as needed.
      static void clear (Request::Ref &reqref);

      //##Documentation
      //## Inits (if necessary) and returns the rider.
      //## Reqref will be COWed as needed.
      //## If the NEW_RIDER flag is given, always creates a new rider.
      static DMI::Record & getRider (Request::Ref &reqref,int flags=0);

      //##Documentation
      //## Inits (if necessary) and returns the group command record for 'group'.
      //## Reqref will be COWed as needed.
      //## If the NEW_RIDER flag is given, always creates a new rider.
      //## If the NEW_GROUPREC flag is given, always creates a new GCR.
      static DMI::Record & getGroupRec (Request::Ref &reqref,const HIID &group,int flags=0);

      //##Documentation
      //## Inits (if necessary) and returns the command_all subrecord for the given group.
      //## Reqref will be COWed as needed.
      //## If the NEW_RIDER flag is given, always creates a new rider.
      //## If the NEW_GROUPREC flag is given, always creates a new GCR.
      //## If the NEW_CMDREC flag is given, always creates a new command subrecord.
      static DMI::Record & getCmdRec_All (Request::Ref &reqref,const HIID &group,int flags=0);

      //##Documentation
      //## Inits (if necessary) and returns the command_by_nodeindex subrecord for 
      //## the given group. Reqref will be COWed as needed.
      //## If the NEW_RIDER flag is given, always creates a new rider.
      //## If the NEW_GROUPREC flag is given, always creates a new GCR.
      //## If the NEW_CMDREC flag is given, always creates a new command subrecord.
      static DMI::Record & getCmdRec_ByNodeIndex (Request::Ref &reqref,const HIID &group,int flags=0);

      //##Documentation
      //## Inits (if necessary) and returns the command_by_list subrecord (field) for 
      //## the given group. Reqref will be COWed as needed.
      //## If the NEW_RIDER flag is given, always creates a new rider.
      //## If the NEW_GROUPREC flag is given, always creates a new GCR.
      //## If the NEW_CMDREC flag is given, always creates a new command subrecord.
      static DMI::Vec & getCmdRec_ByList (Request::Ref &reqref,const HIID &group,int flags=0);
      
      //## Adds a symdep mask for the given group (FAll by default). Inits
      //## riders and subrecords as necessary.
      static void addSymDepMask (Request::Ref &reqref,const HIID &symdep,
                                 int mask,const HIID &group = AidAll );
      
      //##Documentation
      //## Inits (if necessary) and returns a subrecord for rec[field]
      static DMI::Record & getOrInit (DMI::Record &rec,const HIID &field);
    };

  protected:
    // ----------------- control state management
    // sets new control state and notifies the Forest object
    // (the Forest may publish messages, etc.)
    // if sync is true, the state record is immediately updated
    void setControlStatus (int newst,bool sync=false);
    
    // changes execution state and control status in one call, checks
    // if breakpoints have been hit
    void setExecState (int es,int cs,bool sync=false);

    // overloaded function to change exec state but not rest of control status
    void setExecState (int es)
    { setExecState(es,control_status_,false); }
    
  
    //##Documentation
    //## generally called from constructor, to indicate that a node class does   
    //## not support auto-resampling of child results            
    void disableAutoResample ()
    { disable_auto_resample_ = true; auto_resample_ = RESAMPLE_NONE; }
    
    //##Documentation
    //## generally called from constructor, to indicate that a node class does   
    //## not want to automatically fail if one of the children returns a RES_FAIL.
    //## RES_FAIL from children is then ignored (and masked out of the cumulative
    //## result code)
    void disableFailPropagation ()
    { propagate_child_fails_ = false; }
    
    
    //##Documentation
    //## Helper function to poll a node's set of stepchildren. 
    //## Stepchildren's results are normally discarded.
    int pollStepChildren (const Request &req);
      
    // ----------------- virtual methods defining node behaviour --------------
      
    //##ModelId=3F83FADF011D
    //##Documentation
    //## called from resolveChildren(), meant to check children types if the node
    //## requires specific children. Throw exception on failure. 
    virtual void checkChildren()
    {} // base version does no checking
    
    //##ModelId=3F98D9D2006B
    //##Documentation
    //## called from init(), meant to check the initrec for required fields,
    //## and to fill in any missing defaults. Throws exception on failure 
    //## (i.e. if a required field is missing)
    //## Record will be COWed as needed
    virtual void checkInitState (DMI::Record::Ref &)
    {}
    
    //##ModelId=400E531402D1
    //##Documentation
    //## called from init() and setState(), meant to update internal state
    //## in accordance to rec. If initializing==true (i.e. when called from 
    //## init()), rec is a complete state record.
    //## Record will be COWed as needed.
    virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);
    
    //##Documentation
    //## virtual method called whenever any symdeps or symdep masks change.
    //## Default version computes & sets the default depend_mask by using the 
    //## currently active symdeps
    virtual void resetDependMasks ();
    
    //##ModelId=400E531600B8
    //##Documentation
    //## called from execute() when a new request is received. Should return
    //## true if it is OK to proceed, false otherwise (RES_WAIT will be returned
    //## by execute() on a false). Nodes tied to external data sources may need 
    //## to override this.
    virtual bool readyForRequest (const Request &)
    { return true; } // base version always ready
    
    //##ModelId=400E531603C7
    //##Documentation
    //## called to process request rider commands, if any. This is allowed
    //## to modify the request object, a ref is passed in to facilitate COW
    //## (since the request is normally received as read-only).
    //## Node is allowed to return stuff from processCommands, to do this
    //## it should attach a Result to resref (if not already attached)
    //## and populate its rider with whatever it wants to return.
    virtual int processCommands (Result::Ref &resref,const DMI::Record &rec,Request::Ref &reqref);

    //##ModelId=400E531702FD
    //##Documentation
    //## Called from execute() to collect the child results for a given request.
    //## Child_results vector is pre-sized to the number of children.
    //## The method is expected to pass the request on to the children,  
    //## collect their results in the vector, and return the accumulated
    //## result code. If RES_FAIL is returned, then resref should point
    //## to a Result with the fails in it; this result will be returned by
    //## execute() immediately with the RES_FAIL code.
    //## Default version does just that. If any child returns RES_FAIL,
    //## collects all fails into resref and returns RES_FAIL. If no children
    //## fail, resref is left untouched.
    //## Stepchildren are also polled, after all children have been polled
    //## (even if children return fails).
    //## Parallelization-wise, the semantics of this call are synchronous:
    //## send request to children, wait for all children to return a result.
    //## Nodes should only reimplement this if they prefer to poll children 
    //## themselves (i.e. the Solver). 
    virtual int pollChildren (std::vector<Result::Ref> &child_results,
                              Result::Ref &resref,
                              const Request &req);
                              
    //## Helper function for asynchronous polling:
    //## Starts the async poll (send request to all children and stepchildren, presumably).
    //## Returns number of children (stepchildren excluded).
    int  startAsyncPoll   (const Request &req);
    
    //## Helper function for asynchronous polling: waits for one child result and 
    //## returns it in (rescode,resref).
    //## The return value is the child number, or -1 once all children have returned.
    int  awaitChildResult (int &rescode,Result::Ref &resref,const Request &req);
                              
    //##ModelId=3F98D9D100B9
    //##Documentation
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
    
    //##Documentation
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
    
    // ----------------- symdep and depmask management ------------------------
    
    //##Documentation
    //## sets the node's dependency mask
    void setDependMask (int mask);
    
    //##Documentation
    //## sets the node's set of known symbolic dependencies. Should normally 
    //## be done once at init time. Note that it also possible to only call 
    //## setActiveSymDeps() directly from the constructor, if the known and
    //## active set is the same to begin with.
    //## Known symdeps will have their dependency masks tracked
    //## by processCommand(). 
    void setKnownSymDeps (const HIID deps[],int ndeps);
    
    void setKnownSymDeps (const std::vector<HIID> &deps)
    { setKnownSymDeps(&deps.front(),deps.size()); }
    
    void setKnownSymDeps (const HIID &dep)
    { setKnownSymDeps(&dep,1); }
    
    void setKnownSymDeps ()
    { static HIID dum; setKnownSymDeps(&dum,0); }
    
    //##Documentation
    //## Sets the node's set of active symbolic dependencies. Must be a subset
    //## of the known symdeps. This will call recomputeDependMask().
    void setActiveSymDeps (const HIID deps[],int ndeps);
    
    void setActiveSymDeps (const HIID &dep)
    { setActiveSymDeps(&dep,1); }
    
    void setActiveSymDeps (const std::vector<HIID> &deps)
    { setActiveSymDeps(&deps.front(),deps.size()); }
    
    void setActiveSymDeps ()
    { static HIID dum; setActiveSymDeps(&dum,0); }
    
    //##Documentation
    //## computes a dependency mask, by bitwise-ORing tracked symdep masks 
    //## corresponding to currently active symdeps.
    int computeDependMask (const std::vector<HIID> &symdeps);
    
// 18/04/05 OMS: phasing this out, ModRes will need to be rewritten a-la Solver
//     //##Documentation
//     //## Nodes that generate their own requests (e.g. Sink, Solver, ModRes)
//     //## have to define a mapping between named symdeps and masks (which are used
//     //## to generate new request IDs). These mappings will be sent up the tree
//     //## so that other nodes may collect the depmasks corresponding to their set
//     //## of known dependencies. This sets the node's generated symdeps.
//     //## An optional group argument restricts the symdeps to a specific node
//     //## group.
//     void setGenSymDeps (const HIID symdeps[],const int depmasks[],int ndeps,const HIID &group = HIID());
//     
//     void setGenSymDeps (const std::vector<HIID> &symdeps,
//                        const std::vector<int>  &depmasks,
//                        const HIID &group = HIID())
//     { DbgAssert(symdeps.size()==depmasks.size()); 
//       setGenSymDeps(&symdeps.front(),&depmasks.front(),symdeps.size(),group); }
//                        
//     void setGenSymDeps (const HIID &symdep,int depmask,const HIID &group = HIID())
//     { setGenSymDeps(&symdep,&depmask,1,group); }
//     
//     void setGenSymDepGroup (const HIID &group)
//     { gen_symdep_group_ = group; }
    
    // ----------------- misc helper methods ----------------------------------
    
    //##Documentation
    //## resamples children to common resolution according to auto_resample_
    //## setting. Returns output resolution in rescells.
    //## If auto-resampling is disabled, does nothing.  
    //## NB: current implementation does no resampling at all, but will
    //## check for cells conformance if AUTORESAMPLE_FAIL is enabled.
    void resampleChildren (Cells::Ref &rescells,std::vector<Result::Ref> &childres);
    
    //##ModelId=3F83F9A5022C
    //##Documentation
    //## write-access to the state record
    DMI::Record & wstate()
    { return staterec_(); }
    
    //##ModelId=3F9919B10014
    //##Documentation
    //## sets the current request
    void setCurrentRequest (const Request &req);

    //## If node is currently executing and force=false, does nothing.
    //## Otherwise, clears cache and recursively calls parents to do the same
    //## (with force=false, to avoid already active parents, since these
    //## will have a recalculated cache anyway).
    //## This is meant to be used by child nodes to flush their caches
    //## when their state changes.
    void flushUpstreamCache (bool force=true,bool quiet=false);
    
    //##ModelId=400E531A021A
    //##Documentation
    //## Checks for cached result; if hit, attaches it to ref and returns true.
    //## On a miss, clears the cache (NB: for now!)
    bool getCachedResult (int &retcode,Result::Ref &ref,const Request &req);
    
    //##ModelId=400E531C0200
    //##Documentation
    //## Conditionally stores result in cache according to current policy.
    //## Returns the retcode.
    int  cacheResult   (const Result::Ref &ref,const Request &req,int retcode);
    
    //##Documentation
    //## checks the Resampled Child Result (RCR) cache for a cached result 
    //## matching the given resolution.
    //## On a match, attaches the result to ref and returns true.
    //## On a mismatch, clears the cache and returns false. 
    bool checkRCRCache (Result::Ref &ref,int ich,const Cells &cells);

    //##Documentation
    //## clears the RCR cache for child ich. If ich<0, then clears all 
    void clearRCRCache (int ich=-1);
    
    //##Documentation
    //## caches a resampled result for child ich
    void cacheRCR      (int ich,const Result::Ref::Copy &res);
    
    //##ModelId=400E531E008F
    //##Documentation
    //## creates a message of the form "Node CLASS ('NAME'): MESSAGE"
    string makeMessage (const string &msg) const
      { return  "Node " + className() + "('" + name() + "'): " + msg; }
    
    //##Documentation
    //## NodeThrow can be used to throw an exception, with the message
    //## passed through makeMessage()
    #define NodeThrow(exc,msg) \
      { THROW(exc,makeMessage(msg)); }
    //##Documentation
    //## NodeThrow1 thows a FailWithoutCleanup exception, with the message
    //## passed through makeMessage()
    #define NodeThrow1(msg) \
      { THROW(FailWithoutCleanup,makeMessage(msg)); }

    //##Documentation
    //## Helper method for init(). Checks that initrec field exists, throws a
    //## FailWithoutCleanup with the appropriate message if it doesn't.
    //## Defined as macro so that exception gets proper file/line info
    #define requiresInitField(rec,field) \
      { if( !(rec)[field].exists() ) \
         NodeThrow(FailWithoutCleanup,"missing initrec."+(field).toString()); } \
    //##Documentation
    //## Helper method for init(). Checks that initrec field exists and inserts
    //## a default value if it doesn't.
    #define defaultInitField(rec,field,deflt) \
      { DMI::Record::Hook hook(rec,field); \
        if( !hook.exists() ) hook = (deflt); }
        
    //##Documentation
    //## Helper method for setStateImpl(). Meant to check for immutable state 
    //## fields. Checks if record rec contains the given field, throws a 
    //## FailWithoutCleanup with the appropriate message if it does.
    //## Defined as macro so that exception gets proper file/line info
    #define protectStateField(rec,field) \
      { if( (rec)[field].exists() ) \
          NodeThrow(FailWithoutCleanup,"state field "+(field).toString()+" not reconfigurable"); }

// 31/03/04: phased out, since rec[Field].get(variable) does the same thing
//     // Helper method for setStateImpl(). Checks if rec[field] exists, if yes,
//     // assigns it to 'out', returns true. Otherwise returns false.
//     template<class T>
//     bool getStateField (T &out,const DMI::Record &rec,const HIID &field)

  
    //##Documentation
    //## Returns label for child #i
    //## If i>(number of defined labels), then this is simply "i".
    //## Labels are used as indices into the child_names and child_indices
    //## containers.
    HIID getChildLabel (int ich) const
    { return ich<int(child_labels_.size()) ? child_labels_[ich] : AtomicID(ich); }
    
    // tells children (including stepchildren) to hold or release cache.
    // if hold=false, holdCache(false) is called on all children
    // if hold=true, holdChild(true) is called on those childeren whose
    //   child_retcode or stepchild_retcode_ is not dependant on depmask;
    //   the rest get holdCache(false)
    void holdChildCaches (bool hold,int depmask=0);
        
    //## control_status word
    int control_status_;
    
    //## vector of child results, filled in during execute()
    std::vector<Result::Ref> child_results_;
    //## vector of child return codes, filled in by pollChildren()
    std::vector<int> child_retcodes_;
    //## vector of stepchild return codes, filled in by pollStepChildren()
    std::vector<int> stepchild_retcodes_;
    std::vector<const Result *> child_fails_;
    
    // cache policy setting
    int cache_policy_;
     
  private:
    //##Documentation
    //## processes the request rider, and calls processCommand() as appropriate.
    //## The request object may be modified; a ref is passed in to facilitate
    //## copy-on-write
    int processRequestRider (Result::Ref &resref,Request::Ref &reqref);
  
    //------------------------- helper methods to manage children
    //##ModelId=400E531F0085
    void initChildren (int nch);
    void initStepChildren (int nch);
    void allocChildSupport (int nch);
    //##ModelId=3F8433C20193
    // adds a child or stepchild. A child may be specified by index or label
    // (if labels are defined); stepchildren always use indices.
    // Ref is transferred.
    void addChild (const HIID &id,Node::Ref &childnode);
    void addStepChild (int n,Node::Ref &childnode);
    //##ModelId=3F9505E50010
    // processes a single [step]child specification. 'child' specifies the child.
    // (this can be a true HIID only if not a stepchild, and child_labels_ are specified;
    // otherwise it's an single-element index) . 'id' is the actual field
    // in 'children' that contains the child specification.
    void processChildSpec (DMI::Container &children,const HIID &chid,const HIID &id,bool stepchild);
    
    // Looks into record, gets out the FChildren or FStepChildren field, and 
    // processes it as a list of [step]children
    void setupChildren (DMI::Record &init,bool stepchildren);
    
    //##ModelId=3F8433ED0337
    //##Documentation
    //## vector of refs to children
    std::vector<Node::Ref> children_;
    //## vector of refs to stepchildren
    std::vector<Node::Ref> stepchildren_;

    typedef struct
    {
      Node::Ref ref;
      bool stepparent;
    } ParentEntry;    
    std::vector<ParentEntry> parents_;
    
    // flag: parents, children & stepchildren have been resolved
    // bool nodes_resolved_;
    //##ModelId=400E530A0143
    //##Documentation
    //## child labels specified in constructor. Labelled children may
    //## be assigned via the record [label=child] form in init(). 
    //## If no labels specified, this is initialized with trivial HIIDs:
    //## '0', '1', etc.
    vector<HIID> child_labels_;
    //##ModelId=3F8433C10295
    typedef std::map<HIID,int> ChildrenMap;
    //##ModelId=400E530B03D6
    //##Documentation
    //## map from child labels to numbers (i.e. indices into the children_ vector)
    ChildrenMap child_map_;
    //##ModelId=400E530A016A
    //##Documentation
    //## specified in constructor. If non-0, node must have that fixed number
    //## of children
    int check_nchildren_;
    //##Documentation
    //## specified in constructor. If non-0, node must have no less than 
    //## that number of children
    int check_nmandatory_;
    
    //##ModelId=3F5F4363030D
    DMI::Record::Ref staterec_;
    
    //##ModelId=3F5F48040177
    string myname_;
    //##ModelId=400E530A0368
    int node_index_;
    //##ModelId=3F5F43930004
    Forest *forest_;
    
    //##ModelId=400E530B018B
    //##Documentation
    //## current (or last executed) request, set in execute()
    HIID current_reqid_;
    Request::Ref current_request_;
    
    // flag set in execute() indicating a new request
    bool new_request_;
    
    //##Documentation
    //## Dependency mask indicating which parts of a RequestId the node's own
    //## value depends on (this is in addition to any child dependencies).
    //## This is (re)generated automatically whenever a Set.Depend.Mask command
    //## is received, based on a node's symbolic dependencies.
    int depend_mask_;
    
    //##Documentation
    //## The set of a node's symbolic dependencies. This can be set by calling
    //## setSymbolicDependencies(), or via the Symbolic.Depend field of the
    //## state record. Note that setting the dependencies always clears 
    //## depend_mask_, so a subsequent Set.Depend.Mask command should be 
    //## issued.
    std::vector<HIID> known_symdeps_;
    std::vector<HIID> active_symdeps_;
    std::map<HIID,int> symdep_masks_;
    
// 18/04/05 OMS: phasing this out, ModRes will need to be rewritten a-la Solver
//     //##Documentation
//     //## The set of symdeps generated by this node (for nodes that generate
//     //## requests). This is a mapping between symdeps and thweir masks.
//     std::map<HIID,int> gen_symdep_masks_;
//     //##Documentation
//     //## The full symdep mask: a bitwise-OR of all gen_symdep_masks_
//     int gen_symdep_fullmask_;
//     //##Documentation
//     //## symdeps may apply to a specific node group only. If empty, the All
//     //## group will be used    
//     HIID gen_symdep_group_;
    
    // used by resolve()
    int node_resolve_id_;
    
    // used during async polling
    int async_poll_child_;
    
    //##ModelId=400E55D00080
    //##Documentation
    //## Group(s) that a node belongs to. Node groups determine 
    std::vector<HIID> node_groups_;
    
    //##Documentation
    //## auto-resample mode for child results
    int auto_resample_;
    //##Documentation
    //## flag: auto-resampling for child results is not available
    bool disable_auto_resample_;
    
    //## flag: child fails automatically propagated
    bool propagate_child_fails_;
    
   
    //##Documentation
    //## cache of resampled child results
    std::vector<Result::Ref> rcr_cache_;
    
    //##Documentation
    //## event generator for result-is-available events
    EventGenerator result_event_gen_;
    
    //## mask of current breakpoints
    int breakpoints_;
    //## mask of current single-shot breakpoints
    int breakpoints_ss_;
    
    // real cache policy (equal to forest policy if ours is 0)
    int actual_cache_policy_;
    
    // cache management info
    // The Cache class encapsulates a cached result
    class Cache
    {
      public:
        // sets the cache
        void set (const Result::Ref &resref,const Request &req,int code)
        {
          result  = resref;
          rqid    = req.id();
          service_flag = req.serviceFlag();
          rescode = code;
          recref_.detach();
          is_valid = true;
        }
        // clears the cache
        void clear ()
        {
          if( !(rescode&RES_FAIL) ) // fail results preserved
            result.detach();
          is_valid = false;
          recref_.detach();
        }
        // is cache valid?
        bool valid () const
        {
          return is_valid && result.valid();
        }
          
        // rebuilds (if needed) and returns a representative cache record
        const Record & record ();
        // resets cache from record, returns validity flag
        bool fromRecord (const Record &rec);
          
        Result::Ref result;
        RequestId   rqid;
        int         rescode;
        bool        service_flag;
        bool        is_valid;
        
      private:
        DMI::Record::Ref recref_;
    };
    
    Cache cache_;
    // flag: release cache when all parents allow it
    bool parents_release_cache_;
    
    // cache statistics
    DMI::Record::Ref cache_stats_;
    typedef struct
    {
      int req;        // total number of requests
      int hits;       // total number of cache hits
      int miss;       // total number of cache misses (wrong cache)
      int none;       // total number of requests with no cache available
      int cached;     // total number of all cached results
      int longcached; // total number of results cached persistently
    } CacheStats;
    // total cache stats (including same requests)
    CacheStats * pcs_total_;
    // cache stats for new requests only
    CacheStats * pcs_new_;
    typedef struct
    {
      int npar;     // number of parents
      int nact;     // number of active parents
      int nhint;    // number of parents that issued hold/release hints
      int nhold;    // of which, how many were hold hints
    } CacheParentInfo;
    CacheParentInfo * pcparents_;
    // another copy of the result code goes here
    int * pcrescode_;
    
    // profiling stats
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
    
    // timers
    struct
    {
      LOFAR::NSTimer total;
      LOFAR::NSTimer children;
      LOFAR::NSTimer getresult;
    } timers_;
    
    static int checking_level_;
};

// convenience functions to lock/unlock objects en-masse
template<class T>
void lockMutexes (std::vector<Thread::Mutex::Lock> &mutexes,
                   const std::vector<CountedRef<T> > &containers )
{
  mutexes.resize(containers.size());
  for( uint i=0; i<containers.size(); i++ )
    if( containers[i].valid() )
      mutexes[i].relock(containers[i]->mutex());
}

    
inline void releaseMutexes (std::vector<Thread::Mutex::Lock> &mutexes)
{
  for( uint i=0; i<mutexes.size(); i++ )
    mutexes[i].release();
}   

} // namespace Meq

#endif /* MeqSERVER_SRC_NODE_H_HEADER_INCLUDED_E5514413 */
