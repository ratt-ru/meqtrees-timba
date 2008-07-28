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

  // pointer to brigade context
Thread::Key Brigade::context_pointer_;

  // current id counter for creating new brigades
int Brigade::max_brigade_id_ = 0;

Brigade *main_brigade_ = 0;
int max_busy_ = 1;

void start (int nworkers,int max_busy)
{
  FailWhen(main_brigade_,"MTPool already started");
  main_brigade_ = new Brigade(nworkers,max_busy);
  max_busy_ = max_busy;
}

void stop  ()
{
  if( main_brigade_ )
  {
    main_brigade_->stop();
    delete main_brigade_;
  }
}


Brigade::Brigade (int nwork,int nbusy,Thread::Mutex::Lock *plock)
{
  workers_.reserve(128);
  Thread::Mutex::Lock lock;
  if( !plock )
    plock = &lock;
  plock->relock(cond());
  brigade_id_ = max_brigade_id_++;
  max_busy_ = nbusy;
  max_workers_ = nbusy*4;
  // spawn worker threads
  for( int i=0; i<nwork; i++ )
  {
    workers_.push_back(WorkerData());
    WorkerData &wd = workers_.back();
    wd.state = IDLE;
    wd.brigade = this;
    wd.thread_id = Thread::create(startWorker,&wd);
  }
  nthr_[IDLE] = nwork;
  nthr_[BUSY] = 0;
  nthr_[BLOCKED] = 0;
  pid_ = getpid();
}

// adds thread to brigade
void Brigade::join (int state)
{
  Thread::Mutex::Lock lock(cond());
  workers_.push_back(WorkerData());
  WorkerData &wd = workers_.back();
  wd.state = state;
  wd.brigade = this;
  wd.thread_id = Thread::self();
  wd.launched_by_us = false;
  context_pointer_.set(&wd);
  nthr_[state]++;
  cdebug1(1)<<sdebug(1)+" joined brigade\n";
}

// returns brigade label
string Brigade::sdebug (int detail)
{
  Thread::Mutex::Lock lock(cond());
  using Debug::ssprintf;
  string s;
  if( detail>=0 )
    s = ssprintf("%d B%dT%d",pid_,brigade_id_,Thread::getThreadNum(Thread::self())+1);
  if( detail>=0 || detail==-1 )
  {
    Debug::appendf(s,"%di%db%dw q:%d",nthr_[IDLE],nthr_[BUSY],nthr_[BLOCKED],wo_queue_.size());
  }
  return s;
}

// worker thread: remap to Brigade's method
void * Brigade::startWorker (void *pwd)
{
  WorkerData & wd = *static_cast<WorkerData*>(pwd);
  wd.launched_by_us = true;
  // store per-thread context
  context_pointer_.set(pwd);
  // enable immediate cancellation
  pthread_setcancelstate(PTHREAD_CANCEL_ENABLE,0);
  pthread_setcanceltype(PTHREAD_CANCEL_ASYNCHRONOUS,0);
  return wd.brigade->workerLoop();
}

// wakes up one worker thread. If no worker threads are idle, launches a new thread
// we're expected to hold a lock on cond()
void Brigade::awakenWorker (bool always_spawn)
{
  if( wo_queue_.empty() || nthr_[BUSY] >= max_busy_ )
    return;
  DbgAssert(nthr_[IDLE]>=0);
  if( !nthr_[IDLE] && ( int(workers_.size()) < max_workers_ || always_spawn ) )
  {
    cdebug1(1)<<sdebug(1)+" no idle workers found, creating a new one\n";
    workers_.push_back(WorkerData());
    WorkerData &wd = workers_.back();
    wd.state = IDLE;
    wd.brigade = this;
    wd.thread_id = Thread::create(startWorker,&wd);
    nthr_[IDLE]++;
  }
  else
  {
    cdebug1(2)<<sdebug(1)+" awakening a worker\n";
    cond().signal();
  }
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
    AbstractWorkOrder *wo = getWorkOrder(true);
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
// gets a AbstractWorkOrder from the brigade queue
// assume we have a lock on cond()
AbstractWorkOrder * Brigade::getWorkOrder (bool wait)
{
  WorkerData &wd = workerData();
  while( true )
  {
    // check the WO queue
    if( wo_queue_.empty() )
    {
      if( !wait )
        return 0;
      // idle this thread if it wasn't idle
      if( wd.state != IDLE )
      {
        nthr_[wd.state]--;
        DbgAssert(nthr_[wd.state]>=0);
        wd.state = IDLE;
        nthr_[IDLE]++;
        cdebug1(1)<<sdebug(1)+" no WOs queued, idling thread\n";
        // if whole brigade is idle, move it to idle pool
      }
      // sleep until something happens to queue
      cond().wait();
    }
    else  // else we have an order on the queue
    {
      if( wd.state == IDLE )
      {
        // are we even allowed to wake up? check how many threads are busy
        if( nthr_[BUSY] >= max_busy_ )
        {
          if( !wait )
            return 0;
          cdebug1(2)<<sdebug(1)+" too many busy threads, will sleep\n";
          cond().wait();
          continue;
        }
        nthr_[IDLE]--;
        DbgAssert(nthr_[IDLE]>=0);
        wd.state = BUSY;
        nthr_[BUSY]++;
      }
      else if( wd.state == BUSY )
      {
        // if too many threads are busy, idle ourselves and go to sleep
        if( nthr_[BUSY] > max_busy_ )
        {
          if( !wait )
            return 0;
          cdebug1(2)<<sdebug(1)+" too many busy threads, will sleep\n";
          nthr_[IDLE]++;
          nthr_[BUSY]--;
          wd.state = IDLE;
          cond().wait();
          continue;
        }
      }
      else
      {
        Throw("unexpected thread state in getWorkOrder()");
      }
      AbstractWorkOrder * wo = wo_queue_.front();
      wo_queue_.pop_front();
      cdebug1(2)<<sdebug(1)+" got queued order\n";
      // if there's more stuff on the queue, can we wake up another thread?
      awakenWorker();
      return wo;
    }
  }
}

void Brigade::clearQueue (const NodeNursery &client)
{
  Thread::Mutex::Lock lock(cond());
  for( WorkOrderQueue::iterator iter = wo_queue_.begin(); iter != wo_queue_.end(); )
  {
    WorkOrder *wo = dynamic_cast<WorkOrder*>(*iter);
    if( wo && &(wo->clientref) == &client )
      wo_queue_.erase(iter++);
    else
      ++iter;
  }
}

// marks thread as blocked or unblocked
void Brigade::markAsBlocked (const string &where,WorkerData &wd)
{
  Thread::Mutex::Lock lock(cond());
  if( wd.state != BLOCKED )
  {
    nthr_[wd.state]--;
    DbgAssert(nthr_[wd.state]>=0);
    wd.state = BLOCKED;
    nthr_[BLOCKED]++;
    // if there's stuff on the queue, and not enough busy threads, wake someone up
    awakenWorker();
  }
  cdebug1(1)<<sdebug(1)+" thread blocked in "+where+"\n";
}

void Brigade::markAsUnblocked (const string &where,WorkerData &wd,bool)
{
  Thread::Mutex::Lock lock(cond());
  DbgAssert(wd.state==BLOCKED);
  nthr_[BLOCKED]--;
  DbgAssert(nthr_[BLOCKED]>=0);
  nthr_[wd.state=BUSY]++;
  cdebug1(1)<<sdebug(1)+" thread unblocked in "+where+"\n";
}

void Brigade::stop ()
{
  cdebug1(0)<<"cancelling all worker threads\n";
  // send cancellation requests to all workers
  for( uint i=0; i<workers_.size(); i++ )
    if( workers_[i].launched_by_us )
      workers_[i].thread_id.cancel();
}

// this executes a node-execute work order.
void WorkOrder::execute (Brigade &brigade)
{
  timer.start();
  NodeFace &node = noderef();
  const Request &req = *reqref;
  cdebug1(1)<<brigade.sdebug(1)+" executing WO "+req.id().toString('.')+" on node "+node.name()+"\n";
  // note that this will block if node is already being executed
  retcode = node.execute(resref,req,depth());
  cdebug1(1)<<brigade.sdebug(1)+" finished WO "+req.id().toString('.')+" on node "+node.name()+"\n";
  timer.stop();
  // notify client of completed order
  (clientref.*callback)(ichild,*this);
}



}
}

