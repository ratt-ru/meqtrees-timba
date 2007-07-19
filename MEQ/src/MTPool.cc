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

#include "MTPool.h"
#include <vector>
    
namespace Meq
{
  
InitDebugContext(MTPool,"mt");
  
namespace MTPool
{
    
static std::vector<Thread::ThrID> workers;

  // pointer to brigade context
Thread::Key Brigade::context_pointer_;

  // nominal brigade size, 0 if mt is disabled
int Brigade::brigade_size_ = 0;
  // global brigade pool mutex
Thread::Mutex Brigade::brigade_mutex_;
  // pool of idle brigades
std::list<Brigade *> Brigade::idle_brigades_;
  // list of all brigades
std::vector<Brigade *> Brigade::all_brigades_;
  // current id counter for creating new brigades
int Brigade::max_brigade_id_ = 0;
  // number of active brigades
int Brigade::num_active_brigades_;

// sets the nominal size of all brigades
void Brigade::setBrigadeSize (int size)
{ 
  brigade_size_ = size;
  workers.reserve(size*16);
  all_brigades_.reserve(16);
}

Brigade::Brigade (Thread::Mutex::Lock *plock,bool one_short)
{
  Thread::Mutex::Lock lock;
  if( !plock )
    plock = &lock;
  plock->relock(cond());
  brigade_id_ = max_brigade_id_++;
  suspended_ = active_ = missing_temp_ = false;
  num_workers_ = one_short ? brigade_size_-1 : brigade_size_;
  num_nonblocked_ = num_workers_;
  // Nbusy initially set to Nworkers, each worker will eventually idle itself
  // within the initial getWorkOrder() call
  num_busy_ = num_workers_;
  // spawn worker threads
  for( int i=0; i<num_workers_; i++ )
    workers.push_back(Thread::create(startWorker,this));
}

// returns brigade label
string Brigade::sdebug (int detail)
{
  Thread::Mutex::Lock lock(cond());
  using Debug::ssprintf;
  string s;
  if( detail>=0 )
    s = ssprintf("B%dT%d",brigade_id_,Thread::getThreadNum(Thread::self())+1); 
  if( detail>=0 || detail==-1 )    
  {
    Debug::appendf(s,"%dw%db%dnb q:%d",num_workers_,num_busy_,num_nonblocked_,wo_queue_.size());
    if( active_ )
      Debug::append(s,"A");
    if( suspended_ )
      Debug::append(s,"(sus)");
  }
  return s;
}

// worker thread: remap to Brigade's method
void * Brigade::startWorker (void *brig)
{
  Brigade * brigade = static_cast<Brigade*>(brig);
  // store per-thread context
  context_pointer_.set(brigade);
  // enable immediate cancellation
  pthread_setcancelstate(PTHREAD_CANCEL_ENABLE,0);
  pthread_setcanceltype(PTHREAD_CANCEL_ASYNCHRONOUS,0);
  return brigade->workerLoop();
}

void * Brigade::workerLoop ()
{
  // NB: all the cdebug() statements here are funny because in a mt scenario stream
  // ops seem to get in each others way, so we try to output atomic strings only.
  // Hence we form the entire output with '+' before dumping it to the stream.
  cdebug1(0)<<sdebug(1)+" started worker thread\n";
  while( true )
  {
    Thread::Mutex::Lock lock;
    // check for cancellation
    Thread::testCancel();
    // wait on the queue condition for a work order to show up
    lock.relock(cond());
    WorkOrder *wo = getWorkOrder(true);
    lock.release();
    // execute order if any
    if( wo )
    {
      wo->execute(*this);
      delete wo;
    }
    else  // no WO despite wait=true causes exit
    {
      cdebug1(0)<<sdebug(1)+" WO=0, exiting worker thread\n";
      return 0;
    }
  }
  return 0;
}

void Brigade::suspend ()
{
  if( suspended_ )
    return;
  cdebug1(1)<<sdebug(1)+" brigade suspended\n";
  suspended_ = true;
  deactivated();
}

void Brigade::resume ()
{
  if( !suspended_ )
    return;
  cdebug1(1)<<sdebug(1)+" brigade resumed\n";
  suspended_ = false;
  activated();
}

void Brigade::activated ()
{  
  if( active_ )
    return;
  active_ = true;
  Thread::Mutex::Lock lock(globMutex());
  num_active_brigades_++;
  cdebug1(1)<<sdebug(1)+ssprintf(" brigade activated, %d brigades now active\n",num_active_brigades_);
  DbgAssert(num_active_brigades_<=int(all_brigades_.size()));
  cond().broadcast();
}

void Brigade::deactivated ()
{
  if( !active_ )
    return;
  active_ = false;
  Thread::Mutex::Lock lock(globMutex());
  num_active_brigades_--;
  cdebug1(1)<<sdebug(1)+ssprintf(" brigade deactivated, %d brigades now active\n",num_active_brigades_);
  DbgAssert(num_active_brigades_>=0);
}

     
// gets a WorkOrder from the brigade queue
// assume we have a lock on cond()
WorkOrder * Brigade::getWorkOrder (bool wait)
{
  bool idled = false;
  while( true )
  {
    // brigade has been suspended -- sleep until resume
    if( isSuspended() )
    {
      if( !wait )
        return 0;
      cdebug1(1)<<sdebug(1)+" brigade suspended, sleeping...\n";
      // wait for brigade to be activated
      do 
        cond().wait();
      while( isSuspended() );
      cdebug1(1)<<sdebug(1)+" brigade resumes\n";
    }
    // now check the WO queue
    if( wo_queue_.empty() )
    {
      if( !wait )
        return 0;
      // idle this thread if it was busy
      if( !idled )
      {
        // mark this thread as non-busy, and wake up anyone waiting
        // for the busy status to change
        Thread::Mutex::Lock lock(busyCond());
        num_busy_--;
        idled = true;
        busyCond().broadcast();
        lock.release();
        DbgAssert(num_busy_>=0);
        cdebug1(1)<<sdebug(1)+" no WOs queued, idling thread\n";
        // if whole brigade is idle, move it to idle pool
        if( !num_busy_ )
        {
          deactivated();
          allowIdling();
        }
      }
      // sleep until something happens to queue
      cond().wait();
    }
    else  // else we have an order from the queue, mark thread/brigade as active
    {
      if( idled )
      {
        cdebug1(1)<<sdebug(1)+" un-idling thread\n";
        Thread::Mutex::Lock lock(busyCond());
        idled = false;
        num_busy_++;
        busyCond().broadcast();
        lock.release();
        DbgAssert(num_busy_<=num_workers_);
      }
      activated();
      WorkOrder * wo = wo_queue_.front();
      wo_queue_.pop_front();
      return wo;
    }
  }
}

// marks thread as blocked or unblocked
void Brigade::markAsBlocked (const NodeFace &node)
{
  Thread::Mutex::Lock lock(cond());
  num_nonblocked_--;
  DbgAssert(num_nonblocked_>=0);
  if( !num_nonblocked_ )
    deactivated();
  cdebug1(1)<<sdebug(1)+" thread blocked in node "+node.name()+"\n";
}

void Brigade::markAsUnblocked (const NodeFace &node)
{
  Thread::Mutex::Lock lock(cond());
  if( !isSuspended() )
    activated(); 
  num_nonblocked_++;
  DbgAssert(num_nonblocked_<=num_workers_);
  cdebug1(1)<<sdebug(1)+" thread unblocked in node "+node.name()+"\n";
}

// adds brigade to idle pool, if possible
void Brigade::allowIdling ()
{
  if( missing_temp_ )
  {
    cdebug1(1)<<sdebug(1)+" temporarily missing worker, not adding to idle pool\n";
  }
  else
  {
    Thread::Mutex::Lock lock(globMutex());
    idle_brigades_.push_back(this);
    cdebug1(1)<<sdebug(1)+ssprintf(" added to idle pool, %d brigades now idle\n",idle_brigades_.size());
  }
}

void Brigade::join ()
{
  context_pointer_.set(this);
  Thread::Mutex::Lock lock(busyCond());
  num_workers_++;
  num_nonblocked_++;
  num_busy_++;
  busyCond().broadcast();
  lock.release();
  cdebug1(1)<<sdebug(1)+" joined brigade\n";
  DbgAssert(num_workers_<=brigade_size_ && num_nonblocked_<=num_workers_ && num_busy_<=num_workers_);
  activated();
}

void Brigade::leave ()
{
  context_pointer_.set(0);
  Thread::Mutex::Lock lock(busyCond());
  num_workers_--;
  num_nonblocked_--;
  num_busy_--;
  busyCond().broadcast();
  lock.release();
  cdebug1(1)<<sdebug(1)+" left brigade\n";
  DbgAssert(num_workers_>=0 && num_nonblocked_>=0 && num_busy_>=0);
  // if brigade is no longer busy, idle it
  if( !num_busy_ )
  {
    deactivated();
    allowIdling();
  }
}

void Brigade::tempLeave ()
{
  context_pointer_.set(0);
  Thread::Mutex::Lock lock(busyCond());
  missing_temp_ = true;
  num_workers_--;
  num_nonblocked_--;
  num_busy_--;
  busyCond().broadcast();
  lock.release();
  if( !num_busy_ )
    deactivated();
  cdebug1(1)<<sdebug(1)+" temporarily left brigade\n";
  DbgAssert(num_workers_>=0 && num_nonblocked_>=0 && num_busy_>=0);
}

void Brigade::rejoin ()
{
  context_pointer_.set(this);
  Thread::Mutex::Lock lock(busyCond());
  num_workers_++;
  num_nonblocked_++;
  num_busy_++;
  cdebug1(1)<<sdebug(1)+" rejoined brigade\n";
  DbgAssert(num_workers_<=brigade_size_ && num_nonblocked_<=num_workers_ && num_busy_<=num_workers_);
  if( num_workers_ == brigade_size_ )
  {
    missing_temp_ = false;
    cdebug1(1)<<sdebug(1)+" brigade back up to full strength\n";
    resume();
  }
  busyCond().broadcast();
  lock.release();
  activated();
}

void Brigade::waitUntilIdle (int minbusy)
{
  cdebug1(1)<<sdebug(1)+ssprintf(" waiting until brigade idles with minbusy %d\n",minbusy);
  Thread::Mutex::Lock lock(cond());
  // clear the WO queue 
  clearQueue();
  lock.release();
  // now we must wait for the brigade to become idle. 
  lock.relock(busyCond());
  while( num_busy_ > minbusy || missing_temp_ )
  {
    cdebug1(2)<<sdebug(1)+ssprintf(" missing_temp is %d\n",int(missing_temp_));
    busyCond().wait();
  }
  cdebug1(1)<<sdebug(1)+ssprintf(" brigade is idle with minbusy %d\n",minbusy);
  lock.release();
}

// this executes a work order. 
void WorkOrder::execute (Brigade &brigade)
{
  timer.start();
  NodeFace &node = noderef();
  const Request &req = *reqref;
  cdebug1(1)<<brigade.sdebug(1)+" executing WO "+req.id().toString('.')+" on node "+node.name()+"\n";
  // note that this will block if node is already being executed
  retcode = node.execute(resref,req);
  cdebug1(1)<<brigade.sdebug(1)+" finished WO "+req.id().toString('.')+" on node "+node.name()+"\n";
  timer.stop();
  // notify client of completed order
  (clientref.*callback)(ichild,*this);
}

// starts a new brigade and returns pointer to it
Brigade * Brigade::startNewBrigade (Thread::Mutex::Lock *plock,bool one_short)
{
  FailWhen1(!brigade_size_,"multithreading disabled, can't start worker threads");
  Brigade *brigade = new Brigade(plock,one_short);
  all_brigades_.push_back(brigade);
  return brigade;
}

// joins an idle brigade (allocates a new one as needed) and returns 
// pointer to it; sets lock on brigade->cond()
Brigade * Brigade::joinIdleBrigade (Thread::Mutex::Lock &lock)
{
  Thread::Mutex::Lock lock2(globMutex());
  Brigade *brigade;
  // get idle brigade or new brigade
  if( !idle_brigades_.empty() )
  {
    brigade = idle_brigades_.front();
    idle_brigades_.pop_front();
    lock2.release();
    lock.relock(brigade->cond());
    brigade->join();
    cdebug1(1)<<ssprintf("removed %s from idle pool and joined, %d brigades now idle\n",
                 brigade->sdebug(0).c_str(),idle_brigades_.size());
    return brigade;
  }
  else
  {
    brigade = startNewBrigade(&lock,true);
    brigade->join();
    cdebug1(1)<<ssprintf("joined new idle brigade %s, %d brigades now idle\n",
                 brigade->sdebug(0).c_str(),idle_brigades_.size());
    return brigade;
  }
}

void Brigade::stopAll ()
{
  Thread::Mutex::Lock lock(globMutex());
  cdebug1(0)<<"cancelling all worker threads\n";
  // first cancel and rejoin all worker threads
  // send cancellation requests to all workers
  for( uint i=0; i<workers.size(); i++ )
    workers[i].cancel();
// // rejoin them all
// // looks like they all die anyway, so no point join()ing
//  cdebug1(0)<<"rejoining all worker threads\n";
//  for( uint i=0; i<workers.size(); i++ )
//    workers[i].join();
  // delete brigades
  cdebug1(0)<<"deleting brigades\n";
// // this may cause memory corruption on exit, so disabling it and
// // to hell with the leak
  for( uint i=0; i<all_brigades_.size(); i++ )
    delete all_brigades_[i];
  all_brigades_.clear();
  idle_brigades_.clear();
}

}
}

