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

#include "MTQueueChannel.h"
#include "AID-AppAgent.h"

    
namespace AppAgent
{    

// const AtomicID AppEvent::EventCategories[] = { AidNormal,AidNotify,AidWarning,AidError,AidCritical,AidInfo,AidDebug };

using namespace AppEvent;
using namespace EventChannelVocabulary;

const HIID FQueueInit = AidQueue|AidInit;

MTQueueChannel::MTQueueChannel (const EventChannel::Ref &channel)
{
  remote_chanref_ = channel;
  premote_ = remote_chanref_.dewr_p();
  setState(CLOSED);
  remote_thread_ = 0;
  aborted_ = false;
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
  // the init-record is meant for the remote channel.
  // our own init-record is in a subrecord
  const DMI::Record *plocal = data[FQueueInit].as_po<DMI::Record>();
  DMI::Record::Ref localinit(plocal ? plocal : new DMI::Record);
  if( EventChannel::init(localinit) < 0 )
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
  remote_initialized_ = false;
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
  try
  {
    remote().init(*initrec_);
  }
  catch( std::exception &exc )
  {
    err_queue_.add(exc);
  }
  remote_initialized_ = true;  // set initialized flag and wake main thread if waiting
  eventFlag().condVar().broadcast();
  initrec_.detach();
  while( remote().state() != CLOSED || !get_queue_.empty() )
  {
    // if any errors have accumulated, wait for exception queue to clear
    while( !err_queue_.empty() )
    {
      // has channel been closed? break out
      if( state() == CLOSED )
        remote().close();
      if( remote().state() == CLOSED )
        continue;
      eventFlag().condVar().wait();
    }
    // clear the post_queue of any accumulated events
    while( !post_queue_.empty() )
    {
      // has remote channel been closed? close & discard queue then
      if( state() == CLOSED )
        aborted_ ? remote().abort() : remote().close();
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
      try
      {
        remote().postEvent(qe.id,qe.data,qe.category,qe.addr);
      }
      catch( std::exception &exc )
      {
        lock.lock(eventFlag().condVar());
        err_queue_.add(exc);
        eventFlag().condVar().broadcast();
        continue;
      }
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
    if( state() == CLOSED )
      aborted_ ? remote().abort() : remote().close();
    if( remote().state() == CLOSED )
    {
      while( !get_queue_.empty() )
        eventFlag().condVar().wait(); // will relock mutex on exit
      continue;
    }
    // get_queue has space. Wait for event to arrive. We don't release the lock
    // here since it will be released anyway if we decide to wait on the flag.
    // Event flag will be raised by main thread if something is posted.
    try
    {
      stat = remote().getEvent(id,data,HIID(),AppEvent::NOWAIT,source);
    }
    catch( std::exception &exc )
    {
      err_queue_.add(exc);
      eventFlag().condVar().broadcast();
      continue;
    }
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
    if( state() == CLOSED )
      aborted_ ? remote().abort() : remote().close();
    if( remote().state() == CLOSED )
      continue;   // back up to top, we break out only when queue is empty
    // now sleep on flag if we had no events
    if( stat == AppEvent::WAIT ) 
      eventFlag().condVar().wait();
   // go back to top of loop to check the post_queue
  }
  eventFlag().condVar().broadcast();
  return 0;
}

void MTQueueChannel::postEvent (const HIID &id,const ObjRef &data,
                                AtomicID category,const HIID &destination)
{
  // obtain lock on event flag
  Thread::Mutex::Lock lock(eventFlag().condVar());
  assureRemoteInit();
  if( remote().state() == CLOSED )
  {
    lock.release();
    close(remote().stateString());
    return;
  }
  checkErrorQueue();
  // as long as the post queue is full, wait on the flag
  while( post_queue_.size() >= queue_size_ && err_queue_.empty() )
    eventFlag().condVar().wait();
  checkErrorQueue();
  post_queue_.push_back(QueueEntry());
  QueueEntry &qe = post_queue_.back();
  qe.id = id;
  qe.data = data;
  qe.category = category;
  qe.addr = destination;
  // raise event flag to wake up remote thread
  raiseEventFlag();
}

void MTQueueChannel::checkErrorQueue ()
{
  if( !err_queue_.empty() )
  {
    DMI::ExceptionList err = err_queue_;
    err_queue_.clear();
    eventFlag().condVar().broadcast();
    throw err;
  }
}

int MTQueueChannel::getEvent (HIID &id,ObjRef &data,
                              const HIID &mask,int wait,HIID &source)
{
  Thread::Mutex::Lock lock(eventFlag().condVar());
  assureRemoteInit();
  // check error queue
  checkErrorQueue();
  // if get_queue is empty, return WAIT or block or close
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
      while( get_queue_.empty() && err_queue_.empty() )
        eventFlag().condVar().wait();
    }
    else
      return WAIT;
  }
  checkErrorQueue();
  // ok, get_queue not empty, check head
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
  assureRemoteInit();
  checkErrorQueue();
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
  // if closing normally (i.e. not from abort()), flush the output queue
  if( !aborted_ )
    flush();
  // clear all queues and signal remote to close
  Thread::Mutex::Lock lock(eventFlag().condVar());
  assureRemoteInit();
  get_queue_.clear();
  post_queue_.clear();
  // raise event flag to notify remote
  raiseEventFlag();
  while( remote().state() != CLOSED )
    eventFlag().condVar().wait();
  lock.release();
  // now rejoin remote thread
  remote_thread_.join();
  remote_thread_ = 0;
  // check for errors
  checkErrorQueue();
}

void MTQueueChannel::abort (const string &str)
{
  aborted_ = true;
  EventChannel::abort(str);
}

void MTQueueChannel::solicitEvent (const HIID &mask)
{
  Thread::Mutex::Lock lock(eventFlag().condVar());
  assureRemoteInit();
  remote().solicitEvent(mask);
}

bool MTQueueChannel::isEventBound (const HIID &id,AtomicID category)
{
  Thread::Mutex::Lock lock(eventFlag().condVar());
  assureRemoteInit();
  return remote().isEventBound(id,category);
}

void MTQueueChannel::flush ()
{
  // flush the post queue
  Thread::Mutex::Lock lock(eventFlag().condVar());
  assureRemoteInit();
  while( !aborted_ && !post_queue_.empty() )
    eventFlag().condVar().wait();
}



}
