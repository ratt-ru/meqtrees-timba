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

void start (int nwork,int max_busy)
{
  FailWhen(main_brigade_,"MTPool already started");
  dprintf(0)("pid %d starting pool of %d threads, max busy is %d\n",getpid(),nwork,max_busy);
  main_brigade_ = new Brigade(nwork,max_busy);
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


Brigade::Brigade (int nwork,int max_busy,Thread::Mutex::Lock *plock)
{
  workers_.reserve(128);
  Thread::Mutex::Lock lock;
  if( !plock )
    plock = &lock;
  plock->relock(cond());
  brigade_id_ = max_brigade_id_++;
  max_busy_ = max_busy;
  nthr_.resize(100,0);
  nidle_ = nwork;
  // spawn worker threads
  for( int i=0; i<nwork; i++ )
  {
    workers_.push_back(WorkerData());
    WorkerData &wd = workers_.back();
    wd.state = IDLE;
    wd.brigade = this;
    wd.thread_id = Thread::create(startWorker,&wd);
  }
  pid_ = getpid();
}

// adds thread to brigade
void Brigade::join (int state,int depth)
{
  Thread::Mutex::Lock lock(cond());
  workers_.push_back(WorkerData());
  WorkerData &wd = workers_.back();
  wd.state = state;
  if( state == IDLE )
    nidle_++;
  else
  {
    if( nthr_.size() >= uint(depth) )
      nthr_.resize(depth+100,0);
    nthr_[depth]++;
  }
  wd.brigade = this;
  wd.thread_id = Thread::self();
  wd.launched_by_us = false;
  context_pointer_.set(&wd);
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
    Debug::appendf(s,"q:%d",wo_queue_.size());
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
void Brigade::awakenWorker ()
{
  if( wo_queue_.empty() )
    return;
  const AbstractWorkOrder &wo = *(wo_queue_.front());
  int depth = wo.depth();
  // allow at most max_busy_ threads at any tree depth
  if( nthr_[depth] >= max_busy_ )
  {
    dprintf(1)("awakenWorker(), queue %s, %d threads already running, no action\n",
               wo.sdebug().c_str(),nthr_[depth]);
    return;
  }
  // if there are no idle threads, start a new worker
  if( !nidle_ )
  {
    dprintf(1)("awakenWorker() queue %s, %d threads running but none idle, creating new worker\n",
               wo.sdebug().c_str(),nthr_[depth]);
    workers_.push_back(WorkerData());
    WorkerData &wd = workers_.back();
    nidle_++;
    wd.state = IDLE;
    wd.brigade = this;
    wd.thread_id = Thread::create(startWorker,&wd);
  }
  // else simply awaken an idle worker
  else
  {
    dprintf(2)("awakenWorker() queue %s, awakening a worker\n",wo.sdebug().c_str());
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
      finishWithWorkOrder(wo);
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
        wd.state = IDLE;
        ++nidle_;
        dprintf(1)("no WOs queued, %d threads now idle\n",nidle_);
      }
      // sleep until something happens to queue
      cond().wait();
    }
    else  // else we have an order on the queue
    {
      AbstractWorkOrder *pwo = wo_queue_.front();
      int depth = pwo->depth();
      dprintf(2)("head of WO queue is %s\n",pwo->sdebug().c_str());
      // first case is us waking up from idle
      if( wd.state == IDLE )
      {
        // check that not too many threads are busy at this depth, go back to sleep if so
        if( nthr_[depth] >= max_busy_ )
        {
          if( !wait )
            return 0;
          dprintf(2)("nthr_[%d]=%d, going back to sleep\n",depth,nthr_[depth]);
          cond().wait();
          continue;
        }
        // else unidle ourselves
        if( nidle_ <=0 )
        {
          dprintf(0)("worker is going idle->busy, but nidle_=%d\n",nidle_);
        }
        else
          --nidle_;
        wd.state = BUSY;
      }
      // second case: we're still counted as busy, so see if we should grab another WO
      else if( wd.state == BUSY )
      {
        // if too many threads are busy, idle ourselves and go to sleep
        if( nthr_[depth] > max_busy_ )
        {
          if( !wait )
            return 0;
          dprintf(2)("nthr_[%d]=%d, going to sleep\n",depth,nthr_[depth]);
          wd.state = IDLE;
          ++nidle_;
          cond().wait();
          continue;
        }
        // else go on to process the order
      }
      else
      {
        Throw("unexpected thread state in getWorkOrder()");
      }
      wo_queue_.pop_front();
      ++nthr_[depth];
      cdebug1(2)<<sdebug(1)+" got queued order\n";
      // if there's more stuff on the queue, can we wake up another thread?
      awakenWorker();
      return pwo;
    }
  }
}

void Brigade::finishWithWorkOrder (AbstractWorkOrder *wo)
{
  Thread::Mutex::Lock lock(cond());
  int depth = wo->depth();
  if( nthr_[depth] <=0 )
  {
    dprintf(0)("finished with WO, but nthr_[%d]=%d\n",depth,nthr_[depth]);
  }
  else
    --nthr_[depth];
  delete wo;
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
void Brigade::markAsBlocked (const string &where,WorkerData &)
{
/*  Thread::Mutex::Lock lock(cond());
  if( wd.state != BLOCKED )
  {
    nthr_[wd.state]--;
    DbgAssert(nthr_[wd.state]>=0);
    wd.state = BLOCKED;
    nthr_[BLOCKED]++;
    // if there's stuff on the queue, and not enough busy threads, wake someone up
    awakenWorker();
  }*/
  cdebug1(1)<<sdebug(1)+" thread blocked in "+where+"\n";
}

void Brigade::markAsUnblocked (const string &where,WorkerData &,bool)
{
/*  Thread::Mutex::Lock lock(cond());
  DbgAssert(wd.state==BLOCKED);
  nthr_[BLOCKED]--;
  DbgAssert(nthr_[BLOCKED]>=0);
  nthr_[wd.state=BUSY]++;*/
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
  cdebug1(1)<<brigade.sdebug(1)+" executing "+sdebug(1)+" on node "+node.name()+"\n";
  // note that this will block if node is already being executed
  retcode = node.execute(resref,req,depth());
  cdebug1(1)<<brigade.sdebug(1)+" finished "+sdebug(1)+" on node "+node.name()+"\n";
  timer.stop();
  // notify client of completed order
  (clientref.*callback)(ichild,*this);
}

string WorkOrder::sdebug (int) const
{
  const NodeFace &node = *noderef;
  return Debug::ssprintf("WO(%s,%s,%d)",node.name().c_str(),reqref->id().toString('.').c_str(),depth());
}


}
}

