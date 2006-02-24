#include "Node.h"
#include "MTPool.h"
#include "Forest.h"
        
namespace Meq
{    
void Node::setChildPollOrder (const std::vector<string> &order)
{
  std::vector<bool> specified(numChildren(),false);
  child_poll_order_.resize(numChildren());
  int nord = 0;
  FailWhen(order.size()>uint(numChildren()),"child_poll_order: too many elements");
  for( uint i=0; i<order.size(); i++ )
  {
    const string &child_name = order[i];
    int ich;
    for( ich=0; ich<numChildren(); ich++ )
    {
      if( getChildName(ich) == child_name )
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
  Assert(nord == numChildren() );
}

// Checks if an MT poll is possible, returns brigade if it is. Sets
// a lock on the brigade's cond() mutex/variable.
// If MT is not possible (i.e. do serially in same thread), returns 0.
// As a side effect, inits mt.old_brigade_ if the current thread
// switches brigades.
MTPool::Brigade * Node::mt_checkBrigadeAvailability (Thread::Mutex::Lock &lock)
{
  // completely disabled
  if( !multithreaded() || (numChildren()+numStepChildren())<2 )
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

int Node::startAsyncPoll (const Request &req)
{
  setExecState(CS_ES_POLLING);
  async_poll_child_ = 0;
  Thread::Mutex::Lock lock;
  // multithreaded version
  if( mt_checkBrigadeAvailability(lock) )
  {
    mt.polling_ = true;
    mt.numchildren_ = numStepChildren(); // children counted separately since some may be disabled
    mt.child_retcount_ = 0;
    mt.child_retqueue_.reserve(numChildren());
    mt.child_retqueue_.resize(0);
    // place work orders on the pool queue
    cdebug(1)<<endl<<"T"<<std::hex<<Thread::self()<<std::dec<<" node "<<name()<<
            "placing async WOs for "<<numChildren()<<" child nodes and "<<numStepChildren()<<" stepchildren"<<endl;
    for( int i=0; i<numStepChildren(); i++ )
      mt.cur_brigade_->placeWorkOrder(new MTPool::WorkOrder(
          *this,&Node::mt_receiveStepchildResult,getStepChild(i),i,req));
    // since later orders are executed sooner, we put the stepchild orders first
    for( int i=numChildren()-1; i>=0; i-- )
    {
      int ichild = child_poll_order_[i];
      if( child_disabled_[ichild] )
        child_retcodes_[ichild] = RES_FAIL;
      else
      {
        mt.cur_brigade_->placeWorkOrder(new MTPool::WorkOrder(
            *this,&Node::mt_receiveAsyncChildResult,getChild(ichild),ichild,req));
        mt.numchildren_++;
      }
    }
    // wake up all worker threads in brigade
    mt.cur_brigade_->cond().broadcast();
    lock.release();
    // NB!!!!!!!!! this may violate the child order, and does not guarantee
    // that all children will finish executing before a stepchild is called.
    // Probably this is not a problem. If it does become a problem, stepchildren
    // should be polled in a separate step, in a manner similar to pollChildren()
    // (which is yet to be developed in the MT case).
  }
  return numChildren();
}

// this will be called by a worker thread to drop off a child's result,
// when operating in async poll mode (i.e. Solver)
void Node::mt_receiveAsyncChildResult (int ichild,MTPool::WorkOrder &res)
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
  timers_.children.add(res.timer);
  // wake parent thread since it may be waiting for a child result
  mt.child_retcount_++;
  mt.child_poll_cond_.broadcast();
}

// this will be called by a worker thread to drop off a stepchild's result,
// when operating in async poll mode
void Node::mt_receiveStepchildResult (int ichild,MTPool::WorkOrder &res)
{
  // do nothing if poll is already finished (this may be possible if the
  // main thread aborted execute())
  if( !mt.polling_ )
    return;
  Thread::Mutex::Lock lock(mt.child_poll_cond_);
  res.resref.detach(); // discard stepchild result
  stepchild_retcodes_[ichild] = res.retcode;
  // add time to profiling timer
  timers_.children.add(res.timer);
  // if last result, broadcast it to wake parent thread, since it may be
  // waiting for all stepchildren to finish
  if( ++mt.child_retcount_ >= mt.numchildren_ )
    mt.child_poll_cond_.broadcast();
}

void Node::mt_finishPoll ()
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
}

 // this is called when execute() aborts in the middle of an MT poll 
 // (i.e. mt.cur_brigade_ != 0 on return from execute())
 // deactivates worker threads and cleans up
void Node::mt_abortPoll ()
{
  if( !mt.cur_brigade_ )
    return;
  mt.polling_ = false;
  // if we joined up with a new brigade for this poll, then
  // we must wait for it to become idle. Since we haven't left
  // it yet, minbusy is 1 (we are still marked busy)
  if( mt.old_brigade_ )
    mt.cur_brigade_->waitUntilIdle(1);
  // clean up (leaving brigade if needed)
  mt_finishPoll();
}

int Node::awaitChildResult (int &rescode,Result::Ref &resref,const Request &req)
{
  if( mt.cur_brigade_ )
  {
    while( true )
    {
      // interrupt poll if aborting forest. Cleanup will be handled by
      // mt_abortPoll() above, on exit from execute()
      if( forest().abortFlag() )
        return -1;
      Thread::Mutex::Lock lock(mt.child_poll_cond_);
      // if return queue is empty, finish poll provided all children have checked in
      if( mt.child_retqueue_.empty() )
      {
        // if polling is finished, return -1
        if( mt.child_retcount_ >= mt.numchildren_)
        {
          mt_finishPoll();
          return -1;
        }
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
        pstate_lock_->release(); // release state lock while executing
        mt.child_poll_cond_.wait();
        pstate_lock_->relock(stateMutex());
        // once woken, go back to top of loop to see what we have received
        continue;
      }
      // ok, we have a work order -- release child results lock and go on to 
      // fill it
      lock.release();
      pstate_lock_->release();        // release state lock while executing
      wo->execute(*mt.cur_brigade_);
      pstate_lock_->relock(stateMutex());
      delete wo;
      // reacquire child results lock and go back up to check our result queue
      lock.relock(mt.child_poll_cond_);
    }
  }
  else // single-thread case
  {
    if( forest().abortFlag() )
      return -1;
    int ichild;
    // loop while we have children yet to poll
    while( async_poll_child_ < numChildren() )
    {
      int ichild = child_poll_order_[async_poll_child_++];
      // if we find a non-disabled child, poll it and return result
      if( !child_disabled_[ichild] )
      {
        pstate_lock_->release(); // temporarily release state lock while executing
        timers_.children.start();
        child_retcodes_[ichild] = rescode = getChild(ichild).execute(resref,req);
        timers_.children.stop();
        pstate_lock_->relock(stateMutex());
        return ichild;
      }
    }
    // no more children -- poll stepchildren and return -1
    pstate_lock_->release(); // temporarily release state lock
    timers_.children.start();
    pollStepChildren(req);
    timers_.children.stop();
    pstate_lock_->relock(stateMutex());
    return -1;
  }
}

// this will be called by a worker thread to drop off a child's result,
// when operating in sync poll mode (i.e. normal pollChildren())
void Node::mt_receiveSyncChildResult (int ichild,MTPool::WorkOrder &res)
{
  // do nothing if poll is already finished (this may be possible if the
  // main thread aborted execute())
  if( !mt.polling_ )
    return;
  Thread::Mutex::Lock lock(mt.child_poll_cond_);
  // store result in child result queue
  child_results_[ichild].xfer(res.resref);
  child_cumul_retcode_ |= child_retcodes_[ichild] = res.retcode;
  // register a fail if received
  if( res.retcode&RES_FAIL )
  {
    const Result * pchildres = child_results_[ichild].deref_p();
    child_fails_.push_back(pchildres);
    num_child_fails_ += pchildres->numFails();
  }
  // add time to profiling timer
  timers_.children.add(res.timer);
  // wake parent thread since it may be waiting for a child result
  mt.child_retcount_++;
  if( mt.child_retcount_ >= mt.numchildren_ )
    mt.child_poll_cond_.broadcast();
}


//##ModelId=400E531702FD
int Node::pollChildren (Result::Ref &resref,const Request &req)
{
//   // in verbose mode, child results will also be stuck into the state record
//   DMI::Vec *chres = 0;
//   if( forest().verbosity()>1 )
//     wstate()[FChildResults] <<= chres = new DMI::Vec(TpMeqResult,numChildren());
//   
  setExecState(CS_ES_POLLING);
  // temporarily release our state lock, and make sure we relock it after 
  // we're finished -- hence the try/catch block
  pstate_lock_->release();
  try
  {
    // init polling structures
    child_cumul_retcode_ = 0;
    num_child_fails_ = 0;
    child_fails_.resize(0);

    // multithreaded poll
    Thread::Mutex::Lock lock;
    if( mt_checkBrigadeAvailability(lock) )
    {
      cdebug(1)<<endl<<"T"<<std::hex<<Thread::self()<<std::dec<<" node "<<name()<<
              "placing WOs for "<<numChildren()<<" child nodes and "<<numStepChildren()<<" stepchildren"<<endl;
      mt.polling_ = true;
      mt.numchildren_ = numStepChildren(); // children counted separately below
      mt.child_retcount_ = 0;
      // place work orders on the pool queue
      for( int i=0; i<numStepChildren(); i++ )
        mt.cur_brigade_->placeWorkOrder(new MTPool::WorkOrder(
            *this,&Node::mt_receiveStepchildResult,getStepChild(i),i,req));
      // since later orders are executed sooner, we put the stepchild orders first
      for( int i=numChildren()-1; i>=0; i-- ) // child 0 we handle ourselves
      {
        int ichild = child_poll_order_[i];
        if( child_disabled_[ichild] )
          child_retcodes_[ichild] = RES_FAIL;
        else
        {
          mt.cur_brigade_->placeWorkOrder(new MTPool::WorkOrder(
              *this,&Node::mt_receiveSyncChildResult,getChild(ichild),ichild,req));
          mt.numchildren_++;
        }
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
      mt_finishPoll();
    }
    else // single-threaded poll
    {
      cdebug(3)<<"  calling execute() on "<<numChildren()<<" child nodes"<<endl;
      timers_.children.start();
      for( int i=0; i<numChildren(); i++ )
      {
        int ichild = child_poll_order_[i];
        if( child_disabled_[ichild] )
          child_retcodes_[ichild] = RES_FAIL;
        else
        {
          int childcode = child_retcodes_[ichild] = getChild(ichild).execute(child_results_[ichild],req);
          cdebug(4)<<"    child "<<ichild<<" returns code "<<ssprintf("0x%x",childcode)<<endl;
          child_cumul_retcode_ |= childcode;
          if( !(childcode&(RES_ABORT|RES_WAIT)) )
          {
            const Result * pchildres = child_results_[ichild].deref_p();
      //       // cache it in verbose mode
      //       if( chres )
      //         chres[ichild] <<= pchildres;
            if( childcode&RES_FAIL )
            {
              child_fails_.push_back(pchildres);
              num_child_fails_ += pchildres->numFails();
            }
          }
        }
      }
      // now poll stepchildren (their results are always ignored)
      pollStepChildren(req);
      timers_.children.stop();
    }
    if( forest().abortFlag() )
    {
      pstate_lock_->relock(stateMutex());
      return RES_ABORT;
    }
    // if any child has completely failed, return a Result containing all of the fails 
    if( !child_fails_.empty() )
    {
      if( propagate_child_fails_ )
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
      else
      {
        cdebug(3)<<"  ignoring RES_FAIL from children since fail propagation is off"<<endl;
        child_cumul_retcode_ &= ~RES_FAIL;
      }
    }
    cdebug(3)<<"  cumulative result code is "<<ssprintf("0x%x",child_cumul_retcode_)<<endl;
  }
  catch(...)
  {
    pstate_lock_->relock(stateMutex());
    throw;
  }
  pstate_lock_->relock(stateMutex());
  return child_cumul_retcode_;
}

int Node::pollStepChildren (const Request &req)
{
  int retcode = 0;
  for( int i=0; i<numStepChildren(); i++ )
  {
    Result::Ref dum;
    int childcode = stepchild_retcodes_[i] = getStepChild(i).execute(dum,req);
    cdebug(4)<<"    child "<<i<<" returns code "<<ssprintf("0x%x",childcode)<<endl;
    retcode |= childcode;
  }
  return retcode;
}

};
