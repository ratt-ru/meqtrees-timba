#include <Common/Thread/Condition.h>
#include <Common/Timer.h>
#include <MEQ/Node.h>
#include <list>
    
namespace Meq
{
  
  namespace MTPool
  {
    // This class represents a work order to be executed
    class WorkOrder
    {
      public:
        typedef void (Node::*Callback)(int,WorkOrder &);  
        
        WorkOrder (Node &client,Callback cb,Node &child,int i,const Request &req)
        : clientref(client,DMI::SHARED),
          callback(cb),
          noderef(child,DMI::SHARED),
          ichild(i),
          reqref(req)
        {}
        
        void execute ();      // runs the work order. 
        // Caller must successfully call lockNode() first.
        
        // Sets a lock on the target node's execMutex(). If wait=True,
        // blocks until lock is obtained and returns True.
        // If wait is False, tries to obtain lock and returns False on failure.
        bool lockNode (bool wait=false)
        { 
          nodelock.relock(noderef().execMutex(),wait?0:Thread::Mutex::TRY);
          return nodelock.locked();
        }
          
        Node::Ref clientref;  // who placed the order
        Callback callback;    // where to deliver result within the caller
        
        Node::Ref noderef;    // which node to execute
        int ichild;           // child number of node to execute
        Request::Ref reqref;  // request to execute
        
        Result::Ref resref;   // result of request (when completed)
        int retcode;          // return code (when completed)
        LOFAR::NSTimer timer; // execution timer
        
        // a lock is held on node's execMutex() while executing
        Thread::Mutex::Lock  nodelock;
    };
    
    // ------------------------------------------------------------------------
    // stuff related to the WorkOrder queue
    
    // this is the work order stack
    typedef std::list<WorkOrder *> WorkOrderQueue;
    
    extern WorkOrderQueue    wo_queue_;
    extern Thread::Condition queue_cond_;
    
    // returns (by ref) the mutex/condition variable for the order queue (stack)
    inline Thread::Condition & queueCond ()
    { return queue_cond_; }
    
    // puts a new work order on the queue. 
    // Ownership of order object is transferred to the queue. 
    // The caller must obtain a lock on queueCond() before calling this.
    inline void placeWorkOrder (WorkOrder *wo)
    { 
      // queue is LIFO so orders are pushed in the front
      wo_queue_.push_front(wo);
    }
    
    // gets next work order on from the queue.
    // If queue is empty, returns 0. 
    // The work order will have its nodelock set, so WorkOrder::execute() 
    // may be called immeiately.
    // The queue may be scanned for lockable orders, so order is generally
    // LIFO but not really guaranteed.
    // Ownership of order object is transferred to caller. 
    // The caller must obtain a lock on queueCond() before calling this.
    WorkOrder * getWorkOrder ();
    
    // ------------------------------------------------------------------------
    // stuff related to worker threads
    
    // starts up a pool of worker threads, they will all wait on the work order
    // queue
    void spawnWorkerThreads (uint num_threads);
    
    // stops all worker threads
    void stopWorkerThreads ();
    
    int  numWorkerThreads ();
    
    LocalDebugContext_ns;
  }

  
};
