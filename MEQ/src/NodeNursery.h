//#  NodeNursery.h: class to manage collections of children
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
#ifndef MEQ_NODENURSERY_H_HEADER_INCLUDED_E5514413
#define MEQ_NODENURSERY_H_HEADER_INCLUDED_E5514413
    
#include <TimBase/Stopwatch.h>
#include <TimBase/Thread/Condition.h>
#include <MEQ/NodeFace.h>
#include <MEQ/Result.h>
#include <MEQ/Request.h>
#include <vector>  

#pragma aid Fail Missing Data Policy Child Poll Order

//## Error handling policies defines what the nursery does with 
//## RES_FAIL and RES_MISSING results from its children when polling
//## in synchronous mode (i.e. via syncPoll()). Note that in async mode
//## no error handling is done at all; async pollers are expected to
//## handle this themselves.
//
//## The policies for handling RES_FAIL and RES_MISSING can be set 
//## independently below. The following policies are available:

//## Default policy is to poll all children and collect their results.
//## * all children are polled
//## * for FAIL mode only: all FAIL results are collected into the Result object
//## * Cumulative result code will contain RES_FAIL or RES_MISSING
#pragma aid CollectPropagate

//## The abandon & propagate policy works as follows:
//## * polling stops as soon as one child returns a fail or missing data
//## * for FAIL mode only: any FAIL results are collected into the Result object
//## * Cumulative result code will contain RES_FAIL or RES_MISSING
#pragma aid AbandonPropagate 

//## The ignore policy works as follows:
//## * all children are polled
//## * fail results and missing results are not checked at all
//## * RES_FAIL and RES_MISSING is not returned in the cumulative code,
//##   it is up to the calling Node to handle child results
#pragma aid Ignore
  
namespace Meq 
{ 
using namespace DMI;

namespace MTPool 
{
  class WorkOrder; 
  class Brigade; 
}

const HIID FFailPolicy        = AidFail|AidPolicy;
const HIID FMissingDataPolicy = AidMissing|AidData|AidPolicy;
const HIID FChildPollOrder    = AidChild|AidPoll|AidOrder;

    
class NodeNursery
{
  public:
    NodeNursery ();
  
    //## =============== GLOBAL STATE
  
    //## forces non-mt mode for service requests
    //##  this is a workaround to some AIPS++ table locking problems
    //##  If true, service requests are always single-threaded
    static void forceSequentialServiceRequests (bool force=true)
    { sequential_service_requests_ = force; }
  
  
    //## =============== INITIALIZATION METHODS
  
    //## Initializes nursery for a specific number of children
    //## All children are initially invalid and disabled
    void init (int num_children,const std::string &name="");
    
    //## false before init() is called, true afterwards
    bool isInitialized () const
    { return initialized_; }
    
    //## Sets child number n, with an optional label (used for debug messages)
    //## If a label is not supplied, it will be initialized to "n".
    //## Child will be enabled.
    void setChild (int n,NodeFace &child,const HIID &label = HIID());
    
    //## Sets error handling policies, poll order, etc.
    //## from a state record. Meant to be called from Node::setStateImpl().
    void setState (DMI::Record::Ref &state,bool initializing);
 
    //## Attaches an abort-flag to the nursery. The flag is checked during
    //## polling; whenever it is true the poll returns immediately with 
    //## a RES_ABORT code.
    void attachAbortFlag (const bool *pflag)
    { pabort_flag_ = pflag; }
    
    typedef void (*IdleCallback)(void*);
    //## Attaches callbacks for the idle/busy states.
    //## The idle callback is called with the supplied args whenever 
    //## a nursery executes a child node, or waits for a result.
    //## The busy callback is called with the supplied args whenever
    //## the wait is finished or execute() returns.
    //## Null callbacks may be supplied.
    //## See the Node class for an example of use.
    void setIdleCallbacks (IdleCallback idle,IdleCallback busy,void *args)
    { cb_idle_ = idle; cb_busy_ = busy; cb_args_ = args; }

    //## Enables or disables mt-mode polling. If enable=true but threads
    //## are not available (running in single-thread mode), ignores the call.
    void enableMultiThreaded (bool enable);
    
    //## returns true if mt-mode is enabled
    bool multiThreaded () const
    { return mt.enabled_; }

    //## Returns name of nursery
    const string & name () const
    { return name_; }
    
    
    //## =============== ACCESS TO CHILDREN
    
    //## Returns number of children
    int numChildren () const
    { return children_.size(); }
    
    //## Returns child #n.
    //## Throws exception if child is invalid
    NodeFace & getChild (int n) 
    { 
      FailWhen(!isChildValid(n),"accessing invalid child "+getChildLabel(n).toString());
      return children_[n](); 
    }
    
    //## Returns true if child is valid (i.e. has been set)
    bool isChildValid (int n) const
    { return children_[n].valid(); }
    
    //## Returns label of child #n.
    const HIID & getChildLabel (int n) const
    { return child_labels_[n]; }
    
    //## Returns true if child is enabled
    bool isChildEnabled (int n) const
    { return children_[n].valid() && child_enabled_[n]; }
    
    //## Enables or disables a child
    bool enableChild (int n,bool enable=true) 
    { return child_enabled_[n] = enable; }
    
    bool disableChild (int n,bool disable=true) 
    { return child_enabled_[n] = !disable; }
    
    
    //## =============== SYNCHRONOUS POLLING METHODS
    
    //## Polls all enabled children synchronously (i.e. does not return
    //## until poll is complete).
    //## Returns the cumulative result code (i.e. a bitwise or of the child
    //## return codes). If an Ignore policy is in effect for fails
    //## or missing data, the RES_FAIL or RES_MISSING bit will be cleared from
    //## the cumulative code.
    //## If the aborting() flag is raised during polling, returns
    //## RES_ABORT.
    //## If an async poll or background poll is in progress (see below), 
    //## throws an exception.
    //## Postconditions:
    //##  * If RES_ABORT is returned, nothing may be assumed. Otherwise:
    //##  * Each valid and enabled child (isChildEnabled(n)==true)
    //##    will have a valid result in childres[n], unless a
    //##    AbandonPropagate policy is in effect: in this case some
    //##    children's results may be invalid (as the poll is abandoned mid-way).
    int syncPoll (Result::Ref &resref,std::vector<Result::Ref> &childres,const Request &req);
    
  
    //## =============== CHILD RESULT CODES
    
    //## Returns cumulative result code from the last syncPoll()
    int cumulativeRetcode () const
    { return child_cumul_retcode_; }
    
    //## Returns child result code for child #n from the last poll (sync,
    //## async or background).
    //## If syncPoll() was done and an AbandonPropagate policy is in 
    //## effect, the poll may have been incomplete, so the code is meaningful
    //## only if that child's result is valid.
    int childRetcode (int n) const
    { return child_retcodes_[n]; }
    
    //## Returns vector of child result codes from the last poll
    const std::vector<int> childRetcodes () const
    { return child_retcodes_; }
    
    
    
    //## =============== ASYNC POLLING METHODS
    
    //## Async mode is employed when a caller can usefully process the child 
    //## results one by one. Nodes with many children (such as the Solver) 
    //## make use of this mode to minimize their memory use.
    //## In async mode, the caller initiates the polling process by calling
    //## the startAsyncPoll() method. This returns the number of children
    //## that will be polled (and in mt-mode, starts executing the children
    //## in parallel threads). The caller then repeatedly calls
    //## awaitChildResult() to fetch the results one by one, until -1
    //## is returned (see below).
    //## Child return codes are retained and may be accessed later via
    //## childRetcode().
    //## Once an async poll is in progress, no other polls may be initiated until
    //## the async poll ends (i.e. awaitChildResult() returns -1, or finishPoll()
    //## or abortPoll() is called). If startAsyncPoll() returns 0 (i.e. no
    //## children to be polled), the poll is not considered to have started.
    //## If another async poll or a background poll is in progress, throws 
    //## an exception.
    int  startAsyncPoll   (const Request &req);
    
    //## Waits for a child to return a result, returns it in (rescode,resref).
    //## Return value: 
    //##  * the child number
    //##  * -1 once all children have returned and poll is ended (or if no 
    //##    poll was in progress)
    //## Postconditions:
    //##  * resref is valid, unless -1 is returned
    int  awaitChildResult (int &rescode,Result::Ref &resref,const Request &req);
    
    //## Returns true if an async poll is in progress
    bool asyncPollInProgress () const
    { return async_poll_in_progress_; }
 
    //## Does an background poll. This is normally used for stepchildren, when
    //## we want to send them a request but are not interested in a result.
    //## In single-threaded mode, this method will not return until the poll 
    //## is completed. In mt mode, the method may return immediately
    //## and do the poll truly in the background (depending on the availability
    //## of CPUs/worker threads).
    //## Child return codes are retained and may be accessed later via
    //## childRetcode(). Child results are discarded.
    //## If another poll is in progress, throws an exception.
    void backgroundPoll (const Request &req);

    //## Returns true if a background poll is in progress
    bool backroundPollInProgress () const
    { return background_poll_in_progress_; }
    
        
    //## =============== END-POLL METHODS
    
    //## Returns true if any non-sync (async or background) poll is in progress
    bool isPollInProgress () const
    { return async_poll_in_progress_ || background_poll_in_progress_; }
    
    //## Called for normal cleanup after a poll. This detaches all cached
    //## child results, etc. If a background or async poll was started 
    //## in mt-mode, waits for it to complete before returning. 
    void finishPoll ();
    
    //## Called to abort a poll. The difference with finishPoll() is only
    //## apparent in mt-mode: any async or background polls will be cleanly
    //## terminated instead of waiting for all children to complete.
    void abortPoll ();
    
    
    
    //## =============== ERROR HANDLING POLICIES
    
    AtomicID failPolicy () const
    { return fail_policy_; }
    
    AtomicID missingDataPolicy () const
    { return missing_data_policy_; }
    
    void setFailPolicy (AtomicID policy);
    
    void setMissingDataPolicy (AtomicID policy);
    
    
    //## =============== ODDS & ENDS
    
    //## access to the polling timer. The poll timer is updated
    //## with the total time spent polling.
    LOFAR::NSTimer & timer ()
    { return timer_; }
    
    //## returns debug info; only the name for now
    string sdebug (int=0) const
    { return name(); }

  private:
    NodeNursery (const NodeNursery &other);
    void operator = (const NodeNursery &other);
    
    //## if an abort flag is attached, returns its value
    bool aborting () const
    { return pabort_flag_ && *pabort_flag_; }

    //## uses callbacks to notify of the idle state
    void becomeIdle ()
    { 
      if( cb_idle_ )
        (*cb_idle_)(cb_args_);
    }
    
    //## uses callbacks to notify of the busy state
    void becomeBusy ()
    { 
      if( cb_busy_ )
        (*cb_busy_)(cb_args_);
    }
    
    //## helper function: checks that argument specifies a valid error handling policy,
    //## returns it if yes, throws exception if not
    AtomicID validatePolicy (AtomicID policy);
    
    //## helper method called (from setStateImpl()) to set a non-default child
    //## poll order. Order must contain valid names of child nodes.
    //## The number of elements in order may be fewer than numChildren(),
    //## in which case the unspecifed children will be automatically added
    //## at the end of the list
    void setChildPollOrder (const std::vector<string> &order);
    
    
    //## helper methods for multithreaded polls
    //## Checks if poll can be done in mt mode. If yes, sets
    //## mt.cur_brigade_ to the current brigade, and returns this value
    //## if not, returns 0.
    MTPool::Brigade * mt_checkBrigadeAvailability (Thread::Mutex::Lock &lock,const Request &req);
    
    //## callbacks to deliver child results in MT mode
    void mt_receiveAsyncChildResult (int ichild,MTPool::WorkOrder &res);
    void mt_receiveSyncChildResult  (int ichild,MTPool::WorkOrder &res);
    void mt_receiveBackgroundResult (int ichild,MTPool::WorkOrder &res);
    
    //## this is called when an MT poll is finished, to clean up, abandon
    //## brigades, etc.
    void mt_cleanupAfterPoll ();
    
    //## this is called when an MT poll needs to be aborted 
    //## (i.e. if one is still in progress when finishPoll() or abortPoll()
    //## is called). This clears the WO queue and waits for worker
    //## threads to finish, then calls cleanupAfterPoll()
    void mt_abortPoll ();

    //## this is called when an MT poll is in progress and we want to
    //## wait for all worker threads to finish, but does not call 
    //## cleanupAfterPoll()
    void mt_waitForEndOfPoll ();
    
    
    //## vector of refs to children
    std::vector<NodeFace::Ref> children_;
  
    //## child labels
    std::vector<HIID>          child_labels_;
  
    //## order in which children are polled, default order_[i] == i but
    //## can be overridden by the child_poll_order state field.
    std::vector<int> child_poll_order_;
    //## polling of individual children may be disabled via this vector
    std::vector<bool> child_enabled_;
    //## vector of child return codes, filled in by syncPoll()
    std::vector<int> child_retcodes_;
    //## cumulative return code, filled in by syncPoll()
    int child_cumul_retcode_;
    
    //## temporary vector of fail results from children, collected in syncPoll()
    std::vector<const Result *> child_fails_;
    //## temporary counter of fail vellsets from children,collected in syncPoll()
    int num_child_fails_;
    
    //## current fail handling policy
    AtomicID fail_policy_;    
    
    //## current missing data handling policy
    AtomicID missing_data_policy_;    
    
    //## flag: async poll is in progress
    bool async_poll_in_progress_;
    
    //## flag: background poll is in progress
    bool background_poll_in_progress_;
    
    //## current child, used during single-threaded async polling
    int async_poll_child_;

    //## in multithread polling mode, this structure is used to hold the child results
    typedef struct
    {
      int ichild;
      int retcode;
      Result::Ref resref;
    } MT_ChildResult;
    
    //## data members for multithreaded support
    struct NodeMT
    {
      bool enabled_;       //## true if MT is enabled
      int numchildren_;    //## number of children yet to poll in mt mode
      int child_retcount_; //## number of children that have returned a result
      //## for async polling -- return queue of results
      std::vector<MT_ChildResult> child_retqueue_;  
      //## pointer to vector of child results filled in by syncPoll()
      std::vector<Result::Ref> *pchildres_;
      //## condition variable used to signal arrival of child results
      Thread::Condition child_poll_cond_;
      //## current mt brigade -- null if not an mt poll
      MTPool::Brigade * cur_brigade_; 
      //## old mt brigade -- if 0, we used to be orphaned
      MTPool::Brigade * old_brigade_; 
      //## true if we need to rejoin old brigade on exit
      bool rejoin_old_;   
      //## true as long as polling is in progress
      bool polling_;
      //## true if poll is being abandoned (in AbandonCollect mode)
      bool abandon_; 
    } mt;
    
    //## pointer to abort flag, if set
    const bool * pabort_flag_;
    
    //## name used in debug messages
    string name_;
    
    //## flag: init() has been called
    bool initialized_;
    
    //## polling timer
    LOFAR::NSTimer timer_;
    
    IdleCallback cb_idle_;
    IdleCallback cb_busy_;
    void  * cb_args_;
    
    //##  this is a workaround to some AIPS++ table locking problems
    //##  If true, service requests are always single-threaded
    static bool sequential_service_requests_;
    
};    


};

    
#endif
    
