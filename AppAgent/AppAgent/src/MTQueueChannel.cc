#include "MTQueueChannel.h"
#include "AID-AppAgent.h"

    
namespace AppAgent
{    

// const AtomicID AppEvent::EventCategories[] = { AidNormal,AidNotify,AidWarning,AidError,AidCritical,AidInfo,AidDebug };

using namespace AppEvent;
using namespace EventChannelVocabulary;


MTQueueChannel::MTQueueChannel (const EventChannel::Ref &channel)
{
  remote_chanref_ = channel;
  premote_ = remote_chanref_.dewr_p();
  setState(CLOSED);
  remote_thread_ = 0;
}

MTQueueChannel::MTQueueChannel (EventChannel *pchannel)
{
  remote_chanref_ <<= premote_ = pchannel;
  setState(CLOSED);
  remote_thread_ = 0;
}

MTQueueChannel::~MTQueueChannel ()
{
  if( state() != CLOSED )
    close("destroying queue channel");
}

void * MTQueueChannel::start_workerThread (void *args)
{
  return static_cast<MTQueueChannel*>(args)->runWorker();
}

int MTQueueChannel::init (const DMI::Record &data)
{
  if( EventChannel::init(data) < 0 )
    return state();
  // if we haven't got an event flag attached, create one since we need it for
  // talking to the remote channel
  if( !hasEventFlag() )
    attach(*new EventFlag);
  // attach our flag to remote channel
  remote().attach(eventFlag());
  // setup queues
  queue_size_ = data[FMTQueueSize].as<int>(DEFAULT_QUEUE_SIZE);
  FailWhen(queue_size_<1,"illegal queue size");
  post_queue_.clear();
  get_queue_.clear();
  // launch worker thread
  initrec_.attach(data);
  remote_thread_ = Thread::create(start_workerThread,this);
  return state();
}

void * MTQueueChannel::runWorker ()
{
  HIID id,source;
  ObjRef data;
  int stat = OPEN;
  // lock the remote event flag so that it cannot be raised by main thread
  Thread::Mutex::Lock lock(eventFlag().condVar());
  // init the remote channel
  remote().init(*initrec_);
  initrec_.detach();
  while( remote().state() != CLOSED || !get_queue_.empty() )
  {
    // clear the post_queue of any accumulated events
    while( !post_queue_.empty() )
    {
      // has remote channel been closed? discard queue then
      if( remote().state() == CLOSED )
      {
        post_queue_.clear();
        break;
      }
      // get next event and post it to remote
      QueueEntry qe = post_queue_.front();
      post_queue_.pop_front();
      // raise event flag for ourselves in case the main thread is waiting 
      // for the post_queue to free up, then release lock on flag while 
      // we post the event, so that main
      // thread has a chance to post something else
      raiseEventFlag();
      lock.release();
      remote().postEvent(qe.id,qe.data,qe.category,qe.addr);
      lock.lock(eventFlag().condVar());
    }
    // clear our event flag since our queue is clear
    clearEventFlag();
    // if input queue is full, wait on the event flag for the main app
    // either to retrieve a message, or to post something else
    if( get_queue_.size() >= queue_size_ )
    {
      eventFlag().condVar().wait(); // will relock mutex on exit
      continue;
    }
    // clear event flag again
    clearEventFlag();
    // if remote channel is closed, wait for get_queue to clear up and exit
    if( remote().state() == CLOSED )
    {
      while( !get_queue_.empty() )
        eventFlag().condVar().wait(); // will relock mutex on exit
      return 0;
    }
    // get_queue has space. Wait for event to arrive. We don't release the lock
    // here since it will be released anyway if we decide to wait on the flag.
    // Event flag will be raised by main thread if something is posted.
    stat = remote().getEvent(id,data,HIID(),AppEvent::NOWAIT,source);
    // post event if we have one
    if( stat == AppEvent::SUCCESS )
    {
      get_queue_.push_back(QueueEntry());
      QueueEntry &qe = get_queue_.back();
      qe.id = id;
      qe.data.xfer(data);
      qe.addr = source;
      // raise event flag to wake up main thread
      raiseEventFlag();
    }
    // check if channel has closed
    if( remote().state() == CLOSED )
      continue;   // back up to top, we break out only when queue is empty
    // now sleep on flag if we had no events
    if( stat == AppEvent::WAIT ) 
      eventFlag().condVar().wait();
   // go back to top of loop to check the post_queue
  }
  return 0;
}

void MTQueueChannel::postEvent (const HIID &id,const ObjRef &data,
                                AtomicID category,const HIID &destination)
{
  // obtain lock on event flag
  Thread::Mutex::Lock lock(eventFlag().condVar());
  if( remote().state() == CLOSED )
  {
    lock.release();
    close(remote().stateString());
    return;
  }
  // as long as the post queue is full, wait on the flag
  while( post_queue_.size() >= queue_size_ )
    eventFlag().condVar().wait();
  post_queue_.push_back(QueueEntry());
  QueueEntry &qe = post_queue_.back();
  qe.id = id;
  qe.data = data;
  qe.category = category;
  qe.addr = destination;
  // raise event flag to wake up remote thread
  raiseEventFlag();
}


int MTQueueChannel::getEvent (HIID &id,ObjRef &data,
                              const HIID &mask,int wait,HIID &source)
{
  Thread::Mutex::Lock lock(eventFlag().condVar());
  // if queue is empty, return WAIT or block or close
  if( get_queue_.empty() )
  {
    if( remote().state() == CLOSED )
    {
      lock.release();
      close(remote().stateString());
      return CLOSED;
    }
    if( wait == WAIT )
    {
      while( get_queue_.empty() )
        eventFlag().condVar().wait();
    }
    else
      return WAIT;
  }
  // ok, queue not empty, check head
  QueueEntry & qe = get_queue_.front();
  if( !mask.empty() && !mask.matches(qe.id) )
    return OUTOFSEQ;
  // raise flag since we have removed something, to wake up remote thread
  raiseEventFlag();
  // return event
  id = qe.id;
  data = qe.data;
  source = qe.addr;
  get_queue_.pop_front();
  return SUCCESS;
}

int MTQueueChannel::hasEvent (const HIID &mask,HIID &out)
{
  Thread::Mutex::Lock lock(eventFlag().condVar());
  // if queue is empty, check if remote channel is closed
  if( get_queue_.empty() )
  {
    if( remote().state() == CLOSED )
    {
      lock.release();
      close(remote().stateString());
      return CLOSED;
    }
    return WAIT;
  }
  // check head of queue
  if( mask.empty() || mask.matches(get_queue_.front().id) )
    return SUCCESS;
  else
    return OUTOFSEQ;
}

void MTQueueChannel::close (const string &str)
{
  EventChannel::close(str);
  // do nothing if no remote is running
  if( !remote_thread_ )
    return;
  // clear all queues and signal remote to close
  Thread::Mutex::Lock lock(eventFlag().condVar());
  get_queue_.clear();
  post_queue_.clear();
  if( remote().state() != CLOSED )
    remote().close(str);
  // raise event flag to notify remote
  raiseEventFlag();
  lock.release();
  // now rejoin remote thread
  remote_thread_.join();
  remote_thread_ = 0;
}

void MTQueueChannel::solicitEvent (const HIID &mask)
{
  Thread::Mutex::Lock lock(eventFlag().condVar());
  remote().solicitEvent(mask);
}

bool MTQueueChannel::isEventBound (const HIID &id,AtomicID category)
{
  Thread::Mutex::Lock lock(eventFlag().condVar());
  return remote().isEventBound(id,category);
}

void MTQueueChannel::flush ()
{
  // flush the post queue
  Thread::Mutex::Lock lock(eventFlag().condVar());
  while( !post_queue_.empty() )
    eventFlag().condVar().wait();
}



}
