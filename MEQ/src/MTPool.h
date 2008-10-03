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

    extern Brigade * main_brigade_;
    extern int max_busy_;

    inline bool enabled ()
    { return main_brigade_ != 0; }

    inline int num_threads ()
    { return max_busy_; }

    inline Brigade & brigade ()
    { return *main_brigade_; }

    void start (int nwork,int max_busy);
    void stop  ();

    // This class represents an abstract work order for a worker thread.
    // A WO is usually (but does not have to be) associated with a node.
    class AbstractWorkOrder
    {
      public:
        AbstractWorkOrder (int depth1)
        : depth_(depth1)
        {}

        // executes the WO.
        virtual void execute (Brigade &brig) =0;

        virtual ~AbstractWorkOrder ()
        {}

        int depth () const
        { return depth_; }

        virtual string sdebug (int=0) const
        { return ""; }

      protected:
        int depth_;
    };

    // An WorkOrder makes an execute() call on a node
    // This is used from NodeNurseries to do mutlithreaded polls.
    class WorkOrder : public AbstractWorkOrder
    {
      public:
        typedef void (NodeNursery::*Callback)(int,WorkOrder &);

        // creates an "EXECUTE" workorder
        WorkOrder (NodeNursery &client,Callback cb,NodeFace &child,int i,
                   const Request &req,int depth1)
        : AbstractWorkOrder(depth1),
          clientref(client),
          callback(cb),
          noderef(child,DMI::SHARED),
          ichild(i),
          reqref(req)
        {}

        virtual void execute (Brigade &brig);      // runs the work order.

        virtual string sdebug (int detail=0) const;

        NodeNursery & clientref;  // who placed the order
        Callback callback;    // where to deliver result within the caller

        NodeFace::Ref noderef;  // which node to execute
        int ichild;             // child number of node to execute
        Request::Ref reqref;    // request to execute

        Result::Ref resref;     // result of request (when completed)
        int retcode;            // return code (when completed)
        LOFAR::NSTimer timer;   // execution timer
    };

    typedef enum { IDLE,BUSY,BLOCKED } ThreadState;

    typedef struct
    {
      int            state;
      Brigade       *brigade;
      Thread::ThrID  thread_id;
      bool           launched_by_us;
    } WorkerData;

    // a brigate is a set of worker threads sharing a WO queue
    class Brigade
    {
      public:
        Brigade (int nwork,int maxbusy,Thread::Mutex::Lock *plock=0);

        int id () const
        { return brigade_id_; }

        Thread::Condition & cond ()
        { return cond_; }

        // adds current thread to brigade, marks it as having the given state
        // if state is BUSY, a depth needs to be supplied (normally 0)
        void join (int state,int depth);

        // puts a new work order on the brigade's queue.
        // !!! The caller must obtain a lock on cond() before calling this.
        // Ownership of order object is transferred to the queue.
        inline void placeWorkOrder (AbstractWorkOrder *wo)
        {
          // queue is LIFO so orders are pushed in the front
          wo_queue_.push_front(wo);
          // resize vector of thread counters if needed
          if( wo->depth() >= int(nthr_.size()) )
            nthr_.resize(wo->depth()+100,0);
        }

        // Clears the brigade's work order queue of WorkOrders associated with the
        // given NodeNursery
        void clearQueue (const NodeNursery &client);

        // gets next work order from the queue.
        // !!! The caller must obtain a lock on cond() before calling this.
        // If head of queue has a WO with a depth>=mindepth, returns the WO.
        // If head of queue has a WO with a depth<mindepth, returns 0.
        // If queue is empty OR too many threads are busy and wait=false, returns 0.
        // If queue is empty and wait=true, marks thread as idle and
        // waits for an order indefinitely.
        // The work order will have its nodelock set, so WorkOrder::execute()
        // may be called immediately.
        // Ownership of order object is transferred to caller.
        // If returning a WO, marks thread as busy.
        AbstractWorkOrder * getWorkOrder (bool wait=true,int mindepth=0);
        
        // finishes with work order, deallocates object
        void finishWithWorkOrder (AbstractWorkOrder *wo);

        // checks if queue is empty
        // !!! The caller must obtain a lock on cond() before calling this.
        bool queueEmpty () const
        { return wo_queue_.empty(); }

        // wakes up a worker thread. If no idle workers are available,
        // and not too many workers are already running (or always_spawn is true),
        // spawns a new worker thread.
        // !!! The caller must obtain a lock on cond() before calling this.
        void awakenWorker ();

        // marks current thread as blocked/unblocked
        void markAsBlocked   (const string &where,WorkerData &wd);
        void markAsUnblocked (const string &where,WorkerData &wd,bool can_stop=true);

        // marks current thread as blocked/unblocked, gets brigade from per-thread context
        static void markThreadAsBlocked (const string &where)
        {
          WorkerData &wd = workerData();
          if( wd.brigade )
            wd.brigade->markAsBlocked(where,wd);
        }
        static void markThreadAsUnblocked (const string &where,bool can_stop=true)
        {
          WorkerData &wd = workerData();
          if( wd.brigade )
            wd.brigade->markAsUnblocked(where,wd,can_stop);
        }

        static WorkerData & workerData ()
        { return *static_cast<WorkerData*>(context_pointer_.get()); }

        // stops all workers
        void stop ();

        // returns short brigade label
        string sdebug (int detail=0);

      private:
        // runs the actual worker thread
        void * workerLoop ();
        // static method to start a worker thread
        static void * startWorker (void *brigade);

        int brigade_id_; // brigade id

        // max number of busy threads
        int max_busy_;

        // our PID -- for debugging messages only, really
        int pid_;

          // brigade state condition variable & mutex
        Thread::Condition cond_;
          // brigade idle/busy condition variable & mutex
        Thread::Condition busy_cond_;
          // work order queue
        typedef std::list<AbstractWorkOrder *> WorkOrderQueue;
        WorkOrderQueue wo_queue_;

      // worker threads
        std::vector<WorkerData> workers_;

        // number of busy threads per each tree depth
        std::vector<int> nthr_;

        // number of idle threads
        int nidle_;

          // thread key used to hold context structure for each thread
        static Thread::Key context_pointer_;

          // current id counter for creating new brigades
        static int max_brigade_id_;
    };

    LocalDebugContext_ns;
  }


};

#endif
