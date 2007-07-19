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

#include "NodeNursery.h"
#include "MTPool.h"
#include "AID-Meq.h"
        
namespace Meq
{

bool NodeNursery::sequential_service_requests_ = false;
  
NodeNursery::NodeNursery ()
{
  initialized_ = false;
  pabort_flag_ = 0;
  cb_idle_ = cb_busy_ = 0;
  async_poll_in_progress_ = background_poll_in_progress_ = false;
  fail_policy_ = missing_data_policy_ = AidCollectPropagate;

  mt.enabled_ = mt.polling_ = mt.abandon_ = mt.rejoin_old_ = false;
  mt.cur_brigade_ = mt.old_brigade_ = 0;
}  


void NodeNursery::init (int num_children,const std::string &name)
{
  initialized_ = true;
  name_ = name;
  // init internal per-child vectors
  children_.resize(num_children);
  child_labels_.resize(num_children);
  for( int i=0; i<num_children; i++ )
    child_labels_[i] = AtomicID(i);
  child_enabled_.resize(num_children);
  child_enabled_.assign(num_children,false);
  child_retcodes_.resize(num_children);
  
  // setup default polling order
  child_poll_order_.resize(num_children);
  for( int i=0; i<num_children; i++ )
    child_poll_order_[i] = i;
}

void NodeNursery::setChild (int n,NodeFace &child,const HIID &label)
{
  FailWhen(isChildValid(n),"child "+child_labels_[n].toString()+" already set");
  children_[n].attach(child,DMI::SHARED);
  if( !label.empty() )
    child_labels_[n] = label;
  child_enabled_[n] = true;
}

void NodeNursery::setState (DMI::Record::Ref &rec,bool initializing)
{
  // get error handling properties (passed in as single-element HIIDs)
  HIID fpol = fail_policy_;
  if( rec[FFailPolicy].get(fpol,initializing) )
  {
    FailWhen(fpol.size()!=1,"invalid fail_policy '"+fpol.toString()+"'");
    fail_policy_ = fpol[0];
  }
  HIID mdpol = missing_data_policy_;
  if( rec[FMissingDataPolicy].get(mdpol,initializing) )
  {
    FailWhen(mdpol.size()!=1,"invalid missing_data_policy '"+fpol.toString()+"'");
    missing_data_policy_ = mdpol[0];
  }
  // set child poll order
  std::vector<string> cpo;
  if( rec[FChildPollOrder].get_vector(cpo) )
    setChildPollOrder(cpo);
}



#ifdef DISABLE_NODE_MT
void NodeNursery::enableMultiThreaded (bool)
{
  mt.enabled_ = false;
}
#else
void NodeNursery::enableMultiThreaded (bool enable)
{
  if( enable )
  {
    if( MTPool::Brigade::numBrigades() )
      mt.enabled_ = true;
  }
  else
    mt.enabled_ = false;
}
#endif

void NodeNursery::setChildPollOrder (const std::vector<string> &order)
{
  std::vector<bool> specified(numChildren(),false);
  int nord = 0;
  FailWhen(order.size()>uint(numChildren()),"child_poll_order: too many elements");
  for( uint i=0; i<order.size(); i++ )
  {
    const string &child_name = order[i];
    int ich;
    for( ich=0; ich<numChildren(); ich++ )
    {
      if( isChildValid(ich) && getChild(ich).name() == child_name )
      {
        FailWhen(specified[ich],"child_poll_order: duplicate child \""+child_name+"\"");
        specified[ich] = true;
        child_poll_order_[nord++] = ich;
        break;
      }
    }
    FailWhen(ich>=numChildren(),"child_poll_order: child \""+child_name+"\" not found");
  }
  // specify remaining children in any order
  if( nord<numChildren() )
  {
    for( int ich=0; ich<numChildren(); ich++ )
      if( !specified[ich] )
        child_poll_order_[nord++] = ich;
  }
  Assert(nord == numChildren());
}

void NodeNursery::setFailPolicy (AtomicID policy) 
{ 
  fail_policy_ = validatePolicy(policy);
}
    
void NodeNursery::setMissingDataPolicy (AtomicID policy) 
{ 
  missing_data_policy_ = validatePolicy(policy);
}

AtomicID NodeNursery::validatePolicy (AtomicID policy)
{
  if( policy != AidIgnore && policy != AidAbandonPropagate && policy != AidCollectPropagate )
    Throw("invalid policy '"+policy.toString()+"'");
  return policy;
}


// Checks if an MT poll is possible, returns brigade if it is. Sets
// a lock on the brigade's cond() mutex/variable.
// If MT is not possible (i.e. must poll serially in same thread), returns 0.
// As a side effect, inits mt.old_brigade_ if the current thread
// switches brigades.
MTPool::Brigade * NodeNursery::mt_checkBrigadeAvailability (Thread::Mutex::Lock &lock,const Request &req)
{
  // completely disabled, or only one child to poll anyway,
  // or is a service request and we have requested serialization
  if( !multiThreaded() || numChildren()<2 ||
      ( sequential_service_requests_ && req.evalMode() <0 ) )
    return 0;
  mt.old_brigade_ = 0;
  mt.rejoin_old_ = false;
  MTPool::Brigade * current = MTPool::Brigade::current();
  if( current )
  {
    lock.relock(current->cond());
    // (A) if our brigade is idle (we are the only busy thread in it),
    //     and has no orders queued, use it for polling right away
    if( current->numBusy() < 2 && current->queueEmpty() )
      return mt.cur_brigade_ = current;
    Thread::Mutex::Lock lock2(MTPool::Brigade::globMutex());
    // we allow at most 2 active brigades, so:
    // (B) if rest of our brigade is blocked (numNonblocked()<2), suspend it
    //    and join an idle brigade (this keeps the number of active brigades 
    //    unchanged)
    // (C) If ours is the only active brigade, leave it and join an idle 
    //     brigade.
    // Otherwise, return 0 (too many active brigades)
    if( current->numNonblocked() < 2 )
      current->suspend();
    else if( MTPool::Brigade::numActiveBrigades() > 1 )
    {
      lock.release();
      return 0;
    }
    // ok, leave our brigade temporarily -- we will rejoin it at end of poll
    current->tempLeave();
    mt.old_brigade_ = current;
    mt.rejoin_old_ = true;
    current = 0;
    lock.release();
  }
  else  // we are somehow orphaned, so if <2 brigades are active,
        // we can (re)activate and join one
  {
    mt.old_brigade_ = 0;
    if( MTPool::Brigade::numActiveBrigades() > 1 )
      return 0;
    mt.rejoin_old_ = true;
  }
  // ok, at this point we have no brigade but we're allowed to join an idle one
  return mt.cur_brigade_ = MTPool::Brigade::joinIdleBrigade(lock);
}

int NodeNursery::startAsyncPoll (const Request &req)
{
  FailWhen(async_poll_in_progress_ || background_poll_in_progress_,"another poll is already in progress");
  int numchildren = 0; // number of children to poll (accounting for disabled children)
  Thread::Mutex::Lock lock;
  // multithreaded version
  if( mt_checkBrigadeAvailability(lock,req) )
  {
    mt.polling_ = true;
    mt.child_retcount_ = 0;
    mt.child_retqueue_.reserve(numChildren());
    mt.child_retqueue_.resize(0);
    // place work orders on the pool queue
    cdebug(1)<<endl<<"T"<<std::hex<<Thread::self()<<std::dec<<" node "<<name()<<
            "placing async WOs for "<<numChildren()<<" child nodes "<<endl;
    // since later orders are executed sooner, we put the stepchild orders first
    for( int i=numChildren()-1; i>=0; i-- )
    {
      int ichild = child_poll_order_[i];
      if( isChildEnabled(ichild) )
      {
        mt.cur_brigade_->placeWorkOrder(new MTPool::WorkOrder(
            *this,&NodeNursery::mt_receiveAsyncChildResult,getChild(ichild),ichild,req));
        numchildren++;
      }
      else
        child_retcodes_[ichild] = 0;
    }
    // wake up all worker threads in brigade
    mt.cur_brigade_->cond().broadcast();
    lock.release();
    mt.numchildren_ = numchildren;
  }
  else
  {
    for( int i=0; i<numChildren(); i++ )
      if( isChildEnabled(i) )
        numchildren++;
  }
  if( numchildren )
  {
    async_poll_in_progress_ = true;
    async_poll_child_ = 0;
  }
  return numchildren;
}

// this will be called by a worker thread to drop off a child's result,
// when operating in async poll mode (i.e. Solver)
void NodeNursery::mt_receiveAsyncChildResult (int ichild,MTPool::WorkOrder &res)
{
  // do nothing if poll is already finished (this may be possible if the
  // main thread aborted execute())
  if( !mt.polling_ )
    return;
  Thread::Mutex::Lock lock(mt.child_poll_cond_);
  // store result in child result queue
  mt.child_retqueue_.push_back(MT_ChildResult());
  MT_ChildResult &qres = mt.child_retqueue_.back();
  qres.ichild = ichild;
  qres.resref.xfer(res.resref);
  qres.retcode = child_retcodes_[ichild] = res.retcode;
  // add time to profiling timer
  timer().add(res.timer);
  // wake parent thread since it may be waiting for a child result
  mt.child_retcount_++;
  mt.child_poll_cond_.broadcast();
}

// this will be called by a worker thread to drop off a child's result
// when doing a background poll
void NodeNursery::mt_receiveBackgroundResult (int ichild,MTPool::WorkOrder &res)
{
  // do nothing if poll is already finished (this may be possible if the
  // main thread aborted execute())
  if( !mt.polling_ )
    return;
  Thread::Mutex::Lock lock(mt.child_poll_cond_);
  res.resref.detach(); // discard result straight off but do store the return code
  child_retcodes_[ichild] = res.retcode;
  // add time to profiling timer
  timer().add(res.timer);
  // if last result, broadcast it to wake parent thread, since it may be
  // waiting for children to finish
  if( ++mt.child_retcount_ >= mt.numchildren_ )
    mt.child_poll_cond_.broadcast();
}

void NodeNursery::mt_cleanupAfterPoll ()
{
   // if we have an old brigade waiting to be rejoined, do it
   mt.polling_ = false;
   if( mt.rejoin_old_ )
   {
     Thread::Mutex::Lock lock(mt.cur_brigade_->cond());
     mt.cur_brigade_->leave();  // this will make it idle as needed
     mt.cur_brigade_ = 0;
     lock.release();
     if( mt.old_brigade_ )
     {
       lock.relock(mt.old_brigade_->cond());
       mt.old_brigade_->rejoin();  // this will resume it as needed
     }
   }
   mt.child_retqueue_.clear();
   async_poll_in_progress_ = background_poll_in_progress_ = false;
}

// this is called when execute() aborts in the middle of an MT poll 
// (i.e. mt.cur_brigade_ != 0 on return from execute())
// deactivates worker threads and cleans up
void NodeNursery::mt_abortPoll ()
{
  if( !mt.cur_brigade_ )
    return;
  Thread::Mutex::Lock lock(mt.cur_brigade_->cond());
  mt.abandon_ = true;
  mt.polling_ = false;
  mt.cur_brigade_->clearQueue();
  lock.release();
  // wait for brigade to become idle
  // **************** review this -- do we really want to do this? not 
  // sure why the if() is there in the first place, shouldn't we always wait?
  if( mt.old_brigade_ )
    mt.cur_brigade_->waitUntilIdle(1);
  // clean up (leaving brigade if needed)
  mt_cleanupAfterPoll();
}

// this is called to wait for an mt poll to finish
void NodeNursery::mt_waitForEndOfPoll ()
{
  if( !mt.cur_brigade_ )
    return;
  Thread::Mutex::Lock lock(mt.child_poll_cond_);
  // loop until all children have returned a result
  while( mt.child_retcount_ < mt.numchildren_ )
  {
    // else grab a work order for ourselves
    Thread::Mutex::Lock lock2(mt.cur_brigade_->cond());
    MTPool::WorkOrder *wo = mt.cur_brigade_->getWorkOrder(false); // wait=false
    lock2.release();
    // if there's nothing on the queue, then we have to wait for all worker
    // threads to finish and deliver a result, so just go to sleep
    if( !wo )
    {
      becomeIdle(); 
      mt.child_poll_cond_.wait();
      becomeBusy(); 
      // once woken, go back to top of loop to see what we have received
      continue;
    }
    // ok, we have a work order -- release child results lock and go on to 
    // fill it
    lock.release();
    becomeIdle(); 
    wo->execute(*mt.cur_brigade_);
    becomeBusy(); 
    delete wo;
    // reacquire child results lock and go back up recheck
    lock.relock(mt.child_poll_cond_);
  }
  // cleanup
  async_poll_in_progress_ = background_poll_in_progress_ = false;
  mt_cleanupAfterPoll();
}

int NodeNursery::awaitChildResult (int &rescode,Result::Ref &resref,const Request &req)
{
  if( aborting() || !async_poll_in_progress_ )
  {
    async_poll_in_progress_ = false;
    return -1;
  }
  // mt mode first
  if( mt.cur_brigade_ )
  {
    while( true )
    {
      Thread::Mutex::Lock lock(mt.child_poll_cond_);
      // if return queue is empty, finish poll provided all children have checked in
      if( mt.child_retqueue_.empty() )
      {
        // if polling is finished, return -1
        if( mt.child_retcount_ >= mt.numchildren_)
        {
          mt_cleanupAfterPoll();
          return -1;
        }
        // else fall through below to grab a work order for ourselves
      }
      // else return next result from queue
      else
      {
        MT_ChildResult &qres = mt.child_retqueue_.back();
        resref.xfer(qres.resref);
        rescode = qres.retcode;
        int ichild = qres.ichild;
        mt.child_retqueue_.pop_back();
        return ichild;
      }
      // no result on queue, so we can grab a work order from the brigade queue 
      Thread::Mutex::Lock lock2(mt.cur_brigade_->cond());
      MTPool::WorkOrder *wo = mt.cur_brigade_->getWorkOrder(false); // wait=false
      lock2.release();
      // if there's nothing on the queue, then we have to wait for all worker
      // threads to finish and deliver a result, so just go to sleep
      if( !wo )
      {
        becomeIdle(); 
        mt.child_poll_cond_.wait();
        becomeBusy(); 
        // once woken, go back to top of loop to see what we have received
        continue;
      }
      // ok, we have a work order -- release child results lock and go on to 
      // fill it
      lock.release();
      becomeIdle(); 
      wo->execute(*mt.cur_brigade_);
      becomeBusy(); 
      delete wo;
      // reacquire child results lock and go back up to check our result queue
      lock.relock(mt.child_poll_cond_);
    }
  }
  else // single-thread case
  {
    int ichild;
    // loop while we have children yet to poll
    while( async_poll_child_ < numChildren() )
    {
      int ichild = child_poll_order_[async_poll_child_++];
      // if we find a non-disabled child, poll it and return result
      if( isChildEnabled(ichild) )
      {
        timer().start();
        becomeIdle(); 
        child_retcodes_[ichild] = rescode = getChild(ichild).execute(resref,req);
        becomeBusy(); 
        timer().stop();
        return ichild;
      }
    }
    // no more children -- return -1
    async_poll_in_progress_ = false;
    return -1;
  }
}

// this will be called by a worker thread to drop off a child's result,
// when operating in sync poll mode
void NodeNursery::mt_receiveSyncChildResult (int ichild,MTPool::WorkOrder &res)
{
  Thread::Mutex::Lock lock(mt.child_poll_cond_);
  // do nothing if poll is already finished or is being abandoned
  if( !mt.polling_ || mt.abandon_ )
    return;
  // store result in child result queue
  (*mt.pchildres_)[ichild].xfer(res.resref);
  child_cumul_retcode_ |= child_retcodes_[ichild] = res.retcode;
  // register a fail if received
  if( res.retcode&NodeFace::RES_FAIL )
  {
    const Result * pchildres = (*mt.pchildres_)[ichild].deref_p();
    child_fails_.push_back(pchildres);
    num_child_fails_ += pchildres->numFails();
    if( failPolicy() == AidAbandonPropagate )
      mt.abandon_ = true;
  }
  else if( res.retcode&NodeFace::RES_MISSING )
  {
    if( missingDataPolicy() == AidAbandonPropagate )
      mt.abandon_ = true;
  }
  else if( res.retcode&NodeFace::RES_ABORT )
    mt.abandon_ = true;
  // add time to profiling timer
  timer().add(res.timer);
  // wake parent thread since it may be waiting for a child result
  mt.child_retcount_++;
  if( mt.child_retcount_ >= mt.numchildren_ )
    mt.child_poll_cond_.broadcast();
  // if abandoning poll, clear work order queue. Due to the mutex lock
  // above, this will happen only once
  if( mt.abandon_ )
  {
    lock.release();
    lock.relock(mt.cur_brigade_->cond());
    mt.cur_brigade_->clearQueue();
  }
}


//##ModelId=400E531702FD
int NodeNursery::syncPoll (Result::Ref &resref,std::vector<Result::Ref> &childres,const Request &req)
{
  childres.resize(numChildren());
  // make sure the becomeBusy() call is paired -- hence the try/catch/rethrow block
  becomeIdle();
  try
  {
    // init polling structures
    child_cumul_retcode_ = 0;
    num_child_fails_ = 0;
    child_fails_.resize(0);
    // multithreaded poll
    Thread::Mutex::Lock lock;
    if( mt_checkBrigadeAvailability(lock,req) )
    {
      cdebug(1)<<endl<<"T"<<std::hex<<Thread::self()<<std::dec<<" node "<<name()<<
              "placing WOs for "<<numChildren()<<" child nodes"<<endl;
      mt.polling_ = true;
      mt.abandon_ = false;
      mt.numchildren_ = 0;
      mt.child_retcount_ = 0;
      mt.pchildres_ = &childres;
      // since later orders are executed sooner, we put the stepchild orders first
      for( int i=numChildren()-1; i>=0; i-- ) // child 0 we handle ourselves
      {
        int ichild = child_poll_order_[i];
        if( isChildEnabled(ichild) )
        {
          mt.cur_brigade_->placeWorkOrder(new MTPool::WorkOrder(
              *this,&NodeNursery::mt_receiveSyncChildResult,getChild(ichild),ichild,req));
          mt.numchildren_++;
        }
        else
          child_retcodes_[ichild] = 0;
      }
      // get the last WO back from the queue since we'll be executing it ourselves
      MTPool::WorkOrder *wo = mt.cur_brigade_->getWorkOrder(false); // wait=false
      // wake up one or all worker threads
      if( mt.numchildren_ > 2 )
        mt.cur_brigade_->cond().broadcast();
      else  // only two WOs so only one worker needs to be woken
        mt.cur_brigade_->cond().signal();
      // release queue lock and go on to fill WO for first child
      lock.release();
      // keep executing work orders until queue is empty
      while( wo )
      {
        wo->execute(*mt.cur_brigade_);
        delete wo;
        lock.relock(mt.cur_brigade_->cond());
        wo = mt.cur_brigade_->getWorkOrder(false);  // wait=false
        lock.release();
      }
      // no more WOs -- sleep until all children have returned 
      Thread::Mutex::Lock lock2(mt.child_poll_cond_);
      while( mt.child_retcount_ < mt.numchildren_ )
        mt.child_poll_cond_.wait();
      lock2.release();
      // finish up
      mt_cleanupAfterPoll();
    }
    else // single-threaded poll
    {
      cdebug(3)<<"  calling execute() on "<<numChildren()<<" child nodes"<<endl;
      timer().start();
      for( int i=0; i<numChildren(); i++ )
      {
        int ichild = child_poll_order_[i];
        if( isChildEnabled(ichild) )
        {
          int childcode = child_retcodes_[ichild] = getChild(ichild).execute(childres[ichild],req);
          cdebug(4)<<"    child "<<ichild<<" returns code "<<ssprintf("0x%x",childcode)<<endl;
          child_cumul_retcode_ |= childcode;
          //*****  if( childcode&NodeFace::RES_WAIT )
          //*****     do nothing, WAIT code not handled yet
          if( childcode&NodeFace::RES_ABORT )
            break;
          else if( childcode&NodeFace::RES_FAIL )
          {
            const Result * pchildres = childres[ichild].deref_p();
            child_fails_.push_back(pchildres);
            num_child_fails_ += pchildres->numFails();
            if( failPolicy() == AidAbandonPropagate )
              break;
          }
          else if( childcode&NodeFace::RES_MISSING )
          {
            if( missingDataPolicy() == AidAbandonPropagate )
              break;
          }
        }
        else // disabled child
          child_retcodes_[ichild] = 0;
      }
      timer().stop();
    } // end of single-threaded poll
    if( aborting() )
    {
      becomeBusy();
      return NodeFace::RES_ABORT;
    }
    // if fail policy is Ignore, make sure FAIL bit is cleared
    if( failPolicy() == AidIgnore )
      child_cumul_retcode_ &= ~NodeFace::RES_FAIL;
    // else if we have any fails, return a Result containing all of the fails 
    else if( !child_fails_.empty() )
    {
      cdebug(3)<<"  got RES_FAIL from children ("<<num_child_fails_<<"), returning fail-result"<<endl;
      Result &result = resref <<= new Result(num_child_fails_);
      int ires = 0;
      for( uint i=0; i<child_fails_.size(); i++ )
      {
        const Result &childres = *(child_fails_[i]);
        for( int j=0; j<childres.numVellSets(); j++ )
        {
          const VellSet &vs = childres.vellSet(j);
          if( vs.isFail() )
            result.setVellSet(ires++,&vs);
        }
      }
    }
    // if fail policy is Ignore, make sure MISSING bit is cleared
    if( missingDataPolicy() == AidIgnore )
      child_cumul_retcode_ &= ~NodeFace::RES_MISSING;
    cdebug(3)<<"  cumulative result code is "<<ssprintf("0x%x",child_cumul_retcode_)<<endl;
  }
  catch(...)
  {
    becomeBusy();
    throw;
  }
  becomeBusy();
  return child_cumul_retcode_;
}


void NodeNursery::backgroundPoll (const Request &req)
{
  FailWhen(async_poll_in_progress_ || background_poll_in_progress_,"another poll is already in progress");
  Thread::Mutex::Lock lock;
  // multithreaded version
  if( mt_checkBrigadeAvailability(lock,req) )
  {
    background_poll_in_progress_ = true;
    mt.polling_ = true;
    mt.child_retcount_ = 0;
    mt.child_retqueue_.reserve(numChildren());
    mt.child_retqueue_.resize(0);
    mt.numchildren_ = 0;
    // place work orders on the pool queue
    cdebug(1)<<endl<<"T"<<std::hex<<Thread::self()<<std::dec<<" node "<<name()<<
            "placing async WOs for "<<numChildren()<<" child nodes "<<endl;
//    for( int i=0; i<numStepChildren(); i++ )
//      mt.cur_brigade_->placeWorkOrder(new MTPool::WorkOrder(
//          *this,&Node::mt_receiveStepchildResult,getStepChild(i),i,req));
    // since later orders are executed sooner, we put the stepchild orders first
    for( int i=numChildren()-1; i>=0; i-- )
    {
      int ichild = child_poll_order_[i];
      if( isChildEnabled(i) )
      {
        mt.cur_brigade_->placeWorkOrder(new MTPool::WorkOrder(
            *this,&NodeNursery::mt_receiveBackgroundResult,getChild(ichild),ichild,req));
        mt.numchildren_++;
      }
      else
        child_retcodes_[ichild] = 0;
    }
    // wake up all worker threads in brigade
    mt.cur_brigade_->cond().broadcast();
    lock.release();
  }
  // single-threaded version
  else
  {
    timer().start();
    for( int i=0; i<numChildren(); i++ )
    {
      int ichild = child_poll_order_[i];
      if( isChildEnabled(ichild)  )
      {
        Result::Ref dum;
        int childcode = child_retcodes_[ichild] = getChild(ichild).execute(dum,req);
        cdebug(4)<<"    child "<<ichild<<" returns code "<<ssprintf("0x%x",childcode)<<endl;
        if( childcode&NodeFace::RES_ABORT )
          break;
      }
      else
        child_retcodes_[ichild] = 0;
    }
    timer().stop();
  }
}


void NodeNursery::finishPoll ()
{
  // if an mt poll is in progress, wait for finish
  if( mt.cur_brigade_ )
    mt_waitForEndOfPoll();
}
  
  
void NodeNursery::abortPoll ()
{
  // if an mt poll is in progress, abort it
  if( mt.cur_brigade_ )
    mt_abortPoll();
  // call finish to flush everything else
  finishPoll();
}
  
  
};
