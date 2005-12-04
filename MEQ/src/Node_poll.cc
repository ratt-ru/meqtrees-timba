#include "Node.h"
#include "MTPool.h"
    
namespace Meq
{    
    
void Node::enableMultiThreadedPolling ()
{
  if( MTPool::numWorkerThreads() )
  {
    mt.enabled_ = true;
    mt.child_poll_order_.resize(numChildren());
    for( int i=0; i<numChildren(); i++ )
      mt.child_poll_order_[i] = i;
  }
}

int Node::startAsyncPoll (const Request &req)
{
  setExecState(CS_ES_POLLING);
  async_poll_child_ = 0;
  //
  if( multithreaded() )
  {
    mt.numchildren_ = numChildren() + numStepChildren();
    mt.child_retcount_    = 0;
    mt.child_retqueue_.reserve(numChildren());
    mt.child_retqueue_.resize(0);
    // place work orders on the pool queue
    Thread::Mutex::Lock lock(MTPool::queueCond());
    for( int i=0; i<numStepChildren(); i++ )
      MTPool::placeWorkOrder(new MTPool::WorkOrder(
          *this,&Node::mt_receiveAsyncStepchildResult,getStepChild(i),i,req));
    // since later orders are executed sooner, we put the stepchild orders first
    for( int i=0; i<numChildren(); i++ )
    {
      int ichild = mt.child_poll_order_[i];
      MTPool::placeWorkOrder(new MTPool::WorkOrder(
          *this,&Node::mt_receiveAsyncChildResult,getChild(ichild),ichild,req));
    }
    // wake up all worker threads
    MTPool::queueCond().broadcast();
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
void Node::mt_receiveAsyncStepchildResult (int ichild,MTPool::WorkOrder &res)
{
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

int Node::awaitChildResult (int &rescode,Result::Ref &resref,const Request &req)
{
  if( multithreaded() )
  {
    while( true )
    {
      Thread::Mutex::Lock lock(mt.child_poll_cond_);
      // if polling is finished, return -1
      if( mt.child_retcount_ == mt.numchildren_)
        return -1;
      // check child result queue and return result from queue if available
      if( !mt.child_retqueue_.empty() )
      {
        MT_ChildResult &qres = mt.child_retqueue_.back();
        resref.xfer(qres.resref);
        rescode = qres.retcode;
        int ichild = qres.ichild;
        mt.child_retqueue_.pop_back();
        return ichild;
      }
      // no result on queue, so we can grab a work order from the global queue 
      Thread::Mutex::Lock lock2(MTPool::queueCond());
      MTPool::WorkOrder *wo = MTPool::getWorkOrder();
      lock2.release();
      // if there's nothing on the queue, then we have to wait for all worker
      // threads to finish and deliver a result, so just go to sleep
      if( !wo )
      {
        mt.child_poll_cond_.wait();
        // once woken, go back to top of loop to see what we have received
        continue;
      }
      // ok, we have a work order -- release child results lock and go on to 
      // fill it
      lock.release();
      wo->execute();
      delete wo;
      mt.child_retcount_++;
      // reacquire child results lock and go back up to check our result queue
      lock.relock(mt.child_poll_cond_);
    }
  }
  else // single-thread case
  {
    // out of children? return -1
    if( async_poll_child_ >= numChildren() )
      return -1;
    // poll current child
    int ichild = async_poll_child_;
    timers_.children.start();
    child_retcodes_[ichild] = rescode = getChild(ichild).execute(resref,req);
    // last child? poll all stepchildren
    if( ++async_poll_child_ >= numChildren() )
      pollStepChildren(req);
    timers_.children.stop();
    return ichild;
  }
}

//##ModelId=400E531702FD
int Node::pollChildren (std::vector<Result::Ref> &child_results,
                        Result::Ref &resref,
                        const Request &req)
{
//   // in verbose mode, child results will also be stuck into the state record
//   DMI::Vec *chres = 0;
//   if( forest().verbosity()>1 )
//     wstate()[FChildResults] <<= chres = new DMI::Vec(TpMeqResult,numChildren());
//   
  setExecState(CS_ES_POLLING);
  bool cache_result = false;
  int retcode = 0;
  cdebug(3)<<"  calling execute() on "<<numChildren()<<" child nodes"<<endl;
  int nfails = 0;
  timers_.children.start();
  child_fails_.resize(0);
  for( int i=0; i<numChildren(); i++ )
  {
    if( isChildValid(i) )
    {
      int childcode = child_retcodes_[i] = getChild(i).execute(child_results[i],req);
      cdebug(4)<<"    child "<<i<<" returns code "<<ssprintf("0x%x",childcode)<<endl;
      retcode |= childcode;
      if( !(childcode&RES_WAIT) )
      {
        const Result * pchildres = child_results[i].deref_p();
  //       // cache it in verbose mode
  //       if( chres )
  //         chres[i] <<= pchildres;
        if( childcode&RES_FAIL )
        {
          child_fails_.push_back(pchildres);
          nfails += pchildres->numFails();
        }
      }
      // if child is updated, clear resampled result cache
      if( childcode&RES_UPDATED )
        clearRCRCache(i);
    }
    else // missing child marked simply by FAIL code
      child_retcodes_[i] = RES_FAIL;
  }
  // now poll stepchildren (their results are always ignored)
  pollStepChildren(req);
  timers_.children.stop();
  // if any child has completely failed, return a Result containing all of the fails 
  if( !child_fails_.empty() )
  {
    if( propagate_child_fails_ )
    {
      cdebug(3)<<"  got RES_FAIL from children ("<<nfails<<"), returning fail-result"<<endl;
      Result &result = resref <<= new Result(nfails);
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
      retcode &= ~RES_FAIL;
    }
  }
  cdebug(3)<<"  cumulative result code is "<<ssprintf("0x%x",retcode)<<endl;
  return retcode;
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
