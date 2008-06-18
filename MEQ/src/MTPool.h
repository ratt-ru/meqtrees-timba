//
//% $Id$ 
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation & 
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc., 
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
#ifndef MEQ_MTPOOL_H
#define MEQ_MTPOOL_H

#include <TimBase/Thread/Condition.h>
#include <TimBase/Timer.h>
#include <MEQ/NodeNursery.h>
#include <list>
    
namespace Meq
{
  
  namespace MTPool
  {
    class Brigade;
    
    // This class represents an abstract work order for a worker thread.
    // A WO is usually (but does not have to be) associated with a node.
    class AbstractWorkOrder 
    {
      public:
        // executes the WO. 
        virtual void execute (Brigade &brig) =0;
        
        virtual ~AbstractWorkOrder ()
        {}
    };
    
    // An WorkOrder makes an execute() call on a node
    // This is used from NodeNurseries to do mutlithreaded polls.
    class WorkOrder : public AbstractWorkOrder
    {
      public:
        typedef void (NodeNursery::*Callback)(int,WorkOrder &);
        
        // creates an "EXECUTE" workorder
        WorkOrder (NodeNursery &client,Callback cb,NodeFace &child,int i,const Request &req)
        : clientref(client),
          callback(cb),
          noderef(child,DMI::SHARED),
          ichild(i),
          reqref(req)
        {}
        
        virtual void execute (Brigade &brig);      // runs the work order. 
        
        NodeNursery & clientref;  // who placed the order
        Callback callback;    // where to deliver result within the caller
        
        NodeFace::Ref noderef;  // which node to execute
        int ichild;             // child number of node to execute
        Request::Ref reqref;    // request to execute
        
        Result::Ref resref;     // result of request (when completed)
        int retcode;            // return code (when completed)
        LOFAR::NSTimer timer;   // execution timer
    };
    
    // a brigate is a set of worker threads sharing a WO queue
    class Brigade 
    {
      public:
        // creates new idle brigade with the given id. By default, brigade 
        // will be one worker short (most brigades are activated when a thread
        // joins it). If lock pointer is supplied, cond() will be locked.
        Brigade (Thread::Mutex::Lock *plock=0,bool one_short=true);
         
        int id () const
        { return brigade_id_; }
      
        Thread::Condition & cond ()
        { return cond_; }
        
        Thread::Condition & busyCond ()
        { return busy_cond_; }
        
        // puts a new work order on the brigade's queue. 
        // !!! The caller must obtain a lock on cond() before calling this.
        // Ownership of order object is transferred to the queue. 
        inline void placeWorkOrder (AbstractWorkOrder *wo)
        { 
          // queue is LIFO so orders are pushed in the front
          wo_queue_.push_front(wo);
        }
        
        // Clears the brigade's work order queue.
        // !!! The caller must obtain a lock on cond() before calling this.
        inline void clearQueue ()
        { wo_queue_.clear(); }
        
        // gets next work order on from the queue.
        // !!! The caller must obtain a lock on cond() before calling this.
        // If queue is empty and wait=false, returns 0. 
        // If queue is empty and wait=true, marks thread as idle and
        // waits for an order indefinitely (a return value of 0 will
        // cancel the thread)
        // The work order will have its nodelock set, so WorkOrder::execute() 
        // may be called immediately. 
        // Ownership of order object is transferred to caller. 
        AbstractWorkOrder * getWorkOrder (bool wait=true);
        
        // returns brigade to which the current thread belongs
        static Brigade * current ()
        { return static_cast<Brigade*>(context_pointer_.get()); }
        
        // checks if queue is empty
        // !!! The caller must obtain a lock on cond() before calling this.
        bool queueEmpty () const
        { return wo_queue_.empty(); }
        
        // returns number of busy worker threads 
        int numBusy () const
        { return num_busy_; }
        
        // returns number of non-blocked workers
        int numNonblocked () 
        { return num_nonblocked_; }
        
        // returns true if brigade has loaned a worker to another brigade
        bool missingTemp() const
        { return missing_temp_; }
        
        // waits until brigade is idle (numBusy() <= minbusy and
        // missingTemp() is false). This is normally called when a poll
        // is aborted and the node has to wait for all polling threads
        // to subside. Minbusy==1 normally since the caller still belongs
        // to the brigade, otherwise set it to 0.
        void waitUntilIdle (int minbusy=1);
        
        // causes current thread to leave this brigade indefinitely.
        // !!! The caller must obtain a lock on cond() before calling this.
        void leave ();
        // causes current thread to join this brigade. 
        // !!! The caller must obtain a lock on cond() before calling this.
        void join ();
        
        // causes current thread to temporaily leave this brigade, to rejoin
        // later. A brigade temporarily missing a worker will not make itself
        // available in the idle pool.
        // !!! The caller must obtain a lock on cond() before calling this.
        void tempLeave ();
        // rejoins brigade, and resumes it if suspended and back up to
        // full strength. tempLeave()/rejoin() must be paired.
        // !!! The caller must obtain a lock on cond() before calling this.
        void rejoin ();
        
        // deactivates brigade, decrements count of active brigades
        // !!! The caller must obtain a lock on cond() before calling this.
        void suspend ();
        
        // activates brigade, increments count of active brigades
        // !!! The caller must obtain a lock on cond() before calling this.
        void resume ();
        
        // is brigade suspended?
        bool isSuspended () const
        { return suspended_; }
        
        // is brigade active? (i.e. not suspended, not all blocked, not idle)
        bool isActive () const
        { return active_; }
        
        // marks current thread as blocked/unblocked
        void markAsBlocked (const NodeFace &node);
        void markAsUnblocked (const NodeFace &node);
        
        // marks current thread as blocked/unblocked, gets brigade from per-thread context
        static void markThreadAsBlocked (const NodeFace &node)
        {
          Brigade *cur = current();
          if( cur )
            cur->markAsBlocked(node);
        }
        static void markThreadAsUnblocked (const NodeFace &node)
        {
          Brigade *cur = current();
          if( cur )
            cur->markAsUnblocked(node);
        }
        
        // ======== static Brigade methods
        
        // sets the nominal size of all brigades
        static void setBrigadeSize (int size);
        
        static int getBrigadeSize ()
        { return brigade_size_; }
        
        // global mutex for brigade pool
        static Thread::Mutex & globMutex ()
        { return brigade_mutex_; }
        
        // starts a new brigade and returns pointer to it
        static Brigade * startNewBrigade (Thread::Mutex::Lock *plock=0,bool one_short=true);
        
        // starts a new brigade and returns pointer to it
        static Brigade * getIdleBrigade (Thread::Mutex::Lock &lock,bool one_short=true);

        // joins an idle brigade (allocates a new one as needed) and returns 
        // pointer to it; sets lock on brigade->cond()
        static Brigade * joinIdleBrigade (Thread::Mutex::Lock &lock);
        
        // stops all brigades
        static void stopAll ();
        
        // total number of brigades 
        static int numBrigades ()
        { return all_brigades_.size(); }
        
        // total number of active brigades 
        static int numActiveBrigades ()
        { return num_active_brigades_; }
        
        // returns short brigade label
        string sdebug (int detail=0);
      
      private:
        // runs the actual worker thread
        void * workerLoop ();
        // static method to start a worker thread
        static void * startWorker (void *brigade);
        
        // marks brigade as activated/deactivated
        // !!! The caller must obtain a lock on cond() before calling this.
        void activated ();
        void deactivated ();
        
        // helper method, called when the number of busy threads in the brigade
        // goes to 0. Will add the brigade to the idle pool, unless the
        // missing_temp_ flag below is set.
        // !!! The caller must obtain a lock on cond() before calling this.
        void allowIdling ();
          
        int brigade_id_; // brigade id
          // flag: brigade has been suspended (i.e. when all nodes are locked)
          // workers in a suspended brigade will do nothing until resumed
        bool suspended_; 
          // flag: brigade is active (cleared when all threads go idle,
          // or when all go blocked, or when suspended). This is needed to 
          // keep track of how many brigades are active, so as to limit
          // the number of active brigades
        bool active_;
          // flag: brigade is temporarily missing a worker. Set when a worker
          // temporarily leaves a brigade, cleared when all workers rejoin.
          // A brigade with this flag set will not join the idle pool.
        bool missing_temp_;
          // number of worker threads
        int num_workers_;         
          // number of running and non-blocked worker threads
        int num_nonblocked_; 
          // number of busy worker threads (including blocked)
        int num_busy_; 
          // brigade state condition variable & mutex
        Thread::Condition cond_;  
          // brigade idle/busy condition variable & mutex
        Thread::Condition busy_cond_;  
          // work order queue
        typedef std::list<AbstractWorkOrder *> WorkOrderQueue;  
        WorkOrderQueue wo_queue_;
          
          // thread key used to hold context structure for each thread
        static Thread::Key context_pointer_;
        
          // nominal brigade size
        static int brigade_size_;
          // global brigade pool mutex
        static Thread::Mutex brigade_mutex_;
          // number of active brigades
        static int num_active_brigades_;
          // pool of idle brigades
        static std::list<Brigade *> idle_brigades_;
          // list of all brigades
        static std::vector<Brigade *> all_brigades_;
          // current id counter for creating new brigades
        static int max_brigade_id_;
    };
    
    LocalDebugContext_ns;
  }

  
};

#endif
