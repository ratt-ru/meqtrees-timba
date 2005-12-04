#include "MTPool.h"
#include <vector>
    
namespace Meq
{
  
InitDebugContext(MTPool,"mt");
  
namespace MTPool
{

WorkOrderQueue wo_queue_;
Thread::Condition queue_cond_;
    
static std::vector<Thread::ThrID> workers;

// gets a WorkOrder from the queue
WorkOrder * getWorkOrder ()
{
  if( wo_queue_.empty() )
    return 0;
  // look for a lockable order
  for( WorkOrderQueue::iterator iter = wo_queue_.begin(); iter != wo_queue_.end(); iter++ )
  {
    WorkOrder *wo = *iter;
    if( wo->lockNode(false) )   // wait=false, so just try a lock
    {
      // success, remove from queue and return
      wo_queue_.erase(iter);
      return wo;
    }
  }
  // all work orders appear to be blocked so there's nothing for us to do --
  // pop first order from queue and wait for its lock to be released
  WorkOrder *wo = wo_queue_.front();
  wo_queue_.pop_front();
  wo->lockNode(true);
  return wo;
}

// runs a worker thread
static void * runWorkerThread (void *)
{
  cdebug1(0)<<"started worker thread "<<Thread::self()<<endl;
  while( true )
  {
    Thread::Mutex::Lock lock;
    // wait on the queue condition for a work order to show up
    lock.relock(queueCond());
    WorkOrder *wo;
    while( !(wo = getWorkOrder()) )
    {
      cdebug1(1)<<"T"<<Thread::self()<<" no WOs, sleeping\n";
      queueCond().wait();
      cdebug1(1)<<"T"<<Thread::self()<<" woken\n";
    }
    lock.release();
    // execute order if any
    if( wo )
    {
      wo->execute();
      delete wo;
    }
    // go back to top of loop to sleep again
  }
  return 0;
}

void spawnWorkerThreads (uint num_threads)
{
  workers.resize(num_threads);
  for( uint i=0; i<num_threads; i++ )
    workers[i] = Thread::create(runWorkerThread);
}
    
void stopWorkerThreads ()
{
  // send cancellation requests to all workers
  for( uint i=0; i<workers.size(); i++ )
    workers[i].cancel();
  // rejoin them all
  for( uint i=0; i<workers.size(); i++ )
    workers[i].join();
}

int numWorkerThreads ()
{ 
  return workers.size(); 
}


// this method executes a work order. Caller is expected to successfully
// have called WorkOrder::lockNode() first
void WorkOrder::execute ()
{
  timer.start();
  Node &node = noderef();
  cdebug1(1)<<"T"<<Thread::self()<<" executing WO on node "<<node.name()<<endl;
  // execute node and release lock
  retcode = node.execute(resref,*reqref);
  nodelock.release();
  // notify client of completed order
  (clientref().*callback)(ichild,*this);
  timer.stop();
}



}
}

