#include "OctopussyConfig.h"
#include "Dispatcher.h"
#include "WPInterface.h"
    
#include <stdarg.h>

#ifdef USE_DEBUG
  #include <Common/Stopwatch.h>
  #define stopwatch_init   Stopwatch _sw
  #define stopwatch_dump   _sw.sdelta("%.9f",true,Stopwatch::REAL).c_str()
  #define stopwatch_reset  _sw.reset()
#else
  #define stopwatch_init   
  #define stopwatch_dump   ""
  #define stopwatch_reset  
#endif

using namespace LOFAR;

#if defined(USE_THREADS) && defined(ENABLE_LATENCY_STATS)
//##ModelId=3DB937230313
void WPInterface::addWaiter ()
{
  Timestamp now;
  reportWaiters();
  // if no-one was waiting, time it 
  if( !num_waiting_workers++ )
  {
    tsw.none.total += now - tsw.none.start;
    tsw.some.start = now;
  }
  else if( num_waiting_workers > 1 )
    tsw.multi.start = now; 
  // if everyone's waiting, time it
  if( num_waiting_workers == num_worker_threads )
    tsw.all.start = now;
}

//##ModelId=3DB937250068
void WPInterface::removeWaiter ()
{
  Timestamp now;
  if( num_waiting_workers == num_worker_threads )
    tsw.all.total += now - tsw.all.start;
  if( num_waiting_workers == 2 )
    tsw.multi.total += now - tsw.multi.start;
  else if( num_waiting_workers == 1)
  {
    tsw.some.total += now - tsw.some.start;
    tsw.none.start = now;
  }
  num_waiting_workers--;
}

//##ModelId=3DB937260023
void WPInterface::reportWaiters ()
{
  Timestamp now;
  double total = now - tsw.last_report;
  if( total < 10 )
    return;
  // add to existing stats
  if( !num_waiting_workers )
  {
    tsw.none.total += now - tsw.none.start;
    tsw.none.start = now;
  }
  else 
  {
    tsw.multi.total += now - tsw.multi.start;
    tsw.multi.start = now;
    if( num_waiting_workers < num_worker_threads )
    {
      tsw.some.total += now - tsw.some.start;
      tsw.some.start = now;
    }
    else
    {
      tsw.all.total += now - tsw.all.start;
      tsw.all.start = now;
    }
  }
  // report the stats
  dprintf(1)("%.2fs elapsed since last report, %d worker threads\n",
      total,num_worker_threads);
  dprintf(1)("no threads waiting for   %6.3fs (%5.2f%%)\n",
      tsw.none.total.seconds(),tsw.none.total.seconds()/total*100);
  dprintf(1)("at least one waiting for %6.3fs (%5.2f%%)\n",
      tsw.some.total.seconds(),tsw.some.total.seconds()/total*100);
  dprintf(1)("multiple waiting for     %6.3fs (%5.2f%%)\n",
      tsw.multi.total.seconds(),tsw.multi.total.seconds()/total*100);
  dprintf(1)("all threads waiting for  %6.3fs (%5.2f%%)\n",
      tsw.all.total.seconds(),tsw.all.total.seconds()/total*100);
  tsw.none.total.reset();
  tsw.some.total.reset();
  tsw.multi.total.reset();
  tsw.all.total.reset();
  tsw.last_report = now;
}
#endif

#ifdef USE_THREADS
// This is the multithreaded poll version: it checks the message queue,
// and distributes all messages into receive/input/timeout/signal methods.
// Default version of wakeup() simply calls this method
//##ModelId=3DB937070121
int WPInterface::deliver (Thread::Mutex::Lock &lock)
{
  // check if something is in the queue
  if( !queue().empty() )
  {
    addWaiter();
    int res = Message::ACCEPT;
    // remove message from queue and release mutex
    QueueEntry qe = queue().front();
    queue().pop_front();
    setNeedRepoll(False);
    
#ifdef ENABLE_LATENCY_STATS
    Timestamp now;
    if( qe.thrid == Thread::self() )
    {
      tot_qlat += now - qe.ts;
      nlat++;
    }
    else
    {
      tot_qlat_mt += now - qe.ts;
      nlat_mt++;
    }
    if( now.seconds() >= last_lat_report + 10 )
    {
      if( nlat )
      {
        dprintf(1)("%d in-thread messages delivered, average latency %.3fms\n",
            nlat,tot_qlat.seconds()*1000/nlat);
      }
      if( nlat_mt )
      {
        dprintf(1)("%d cross-thread messages delivered, average latency %.3fms\n",
            nlat_mt,tot_qlat_mt.seconds()*1000/nlat_mt);
      }
      last_lat_report = now;
      tot_qlat.reset(); tot_qlat_mt.reset();
      nlat = nlat_mt = 0;
    }
#endif
    removeWaiter();
    lock.release();

    const Message &msg = qe.mref.deref();
    const HIID &id = msg.id();
    FailWhen( id.empty(),"null message ID" );
    dprintf1(3)("%s: receiving %s\n",sdebug(1).c_str(),msg.debug(1));

    // is it a system event message?
    if( id[0] == AidEvent ) 
    {
      // Once the event has been delivered, reset its state to 0.
      // This helps the dispatcher keep track of when a new event message is
      // required (as opposed to updating a previous message that's still
      // undelivered). See Dispatcher::checkEvents() for details.
      if( qe.mref.isWritable() )
      {
        qe.mref().latency.measure("RCV");
        qe.mref().setState(0);
      }

      if( id[1] == AidTimeout ) // deliver timeout message
      {
        FailWhen( id.size() < 2,"malformed "+id.toString()+" message" );
        HIID to_id = id.subId(2);
        res = timeout(to_id);
        if( res == Message::CANCEL )
          dsp()->removeTimeout(this,to_id);
        res = Message::ACCEPT;
      }
      else if( id[1] == AidInput ) // deliver input message
      {
        FailWhen( id.size() != 3,"malformed "+id.toString()+" message" );
        int fd=id[2],flags=msg.state();
        if( flags )  // no flags? Means the input has been already removed. Ignore
        {
          res = input(fd,flags);
          if( res == Message::CANCEL )
            dsp()->removeInput(this,fd,flags);
          res = Message::ACCEPT;
        }
      }
      else if( id[1] == AidSignal ) // deliver input message
      {
        FailWhen( id.size() != 3,"malformed "+id.toString()+" message" );
        int signum = id[2];
        res = signal(signum);
        if( res == Message::CANCEL )
          dsp()->removeSignal(this,signum);
        res = Message::ACCEPT;
      }
      else
        Throw("unexpected event" + id.toString());
    }
    else // deliver regular message
    {
      if( qe.mref.isWritable() )
        qe.mref().latency.measure("RCV");
      res = receive(qe.mref);
    }
    // dispence of queue according to result code
    const Message *old_msg = 0; // for comparison below
    if( res == Message::ACCEPT )   // message accepted, remove from queue
    {
      dprintf(3)("result code: OK, de-queuing\n");
      // in fact, already dequeued
    }
    else      // message not accepted, stays in queue
    {
      FailWhen( !qe.mref.valid(),"message was not accepted but its ref was detached or xferred");
      old_msg = qe.mref.deref_p();
      if( res == Message::HOLD )
      {
        dprintf(3)("result code: HOLD\n");
        // requeue - re-insert at head of queue
        enqueueFront(qe.mref,dsp()->getTick(),False);  // this sets repoll if head of queue has changed
      }
      else if( res == Message::REQUEUE )
      {
        dprintf(3)("result code: REQUEUE\n");
        // requeue - re-insert into queue() according to priority
        enqueue(qe.mref,dsp()->getTick(),False);  // this sets repoll if head of queue has changed
      }
      else
        Throw("invalid result code");
    }
    lock.relock(queue_cond);
    if( !queue().empty() )
    {
      // this resets the age at the head of the queue. Effectively, this means
      // we have a "queue age" rather than a message age.
      queue().front().tick = dsp()->getTick();
      // if we find ourselves with something different at the head of the queue,
      // force a repoll. Otherwise (as a result of HOLD/REQUEUE), no repoll is
      // done until something comes up
      if( queue().front().mref.deref_p() != old_msg )
      {
        dprintf(3)("head of queue is different, forcing repoll\n");
        setNeedRepoll(True);
      }
      else
      {
        dprintf(3)("head of queue is same, repoll=%d\n",(int)needRepoll());
      }
    }
  }
  else // else nothing is in the queue, so set needRepoll to false
    setNeedRepoll(False);
  return 0;
}

//##ModelId=3DB9370803D5
bool WPInterface::mtWakeup (Thread::Mutex::Lock &lock)
{
  while( needRepoll() && running ) 
    deliver(lock);
  return True;
}

//##ModelId=3DB9371F00D6
void WPInterface::runWorker ()
{
  Thread::Mutex::Lock lock(queue_cond);
  while( running )
  {
    stopwatch_init;
    addWaiter();
    while( !needRepoll() && isRunning() )
    {
      stopwatch_reset;
      dprintf(3)("waiting on queue condition variable\n");
      queue_cond.wait();
      dprintf(3)("wait time: %s sec\n",stopwatch_dump);
    }
    removeWaiter();
    // check for stop condition
    if( !isRunning() )
    {
      dprintf(3)("worker thread: WP is no longer running");
      break;
    }
    // do a wakeup call
    if( !mtWakeup(lock) )
    {
      dprintf(3)("worker thread: wakeup() signalled exit");
      break;
    }
  }
}

//##ModelId=3DB937200087
void * WPInterface::workerThread ()
{
  Thread::signalMask(SIG_BLOCK,Dispatcher::validSignals());
  try
  {
    stopwatch_init;
    // do start in the worker thread and signal this to the main thread
    dprintf(2)("initializing worker thread\n");
    bool res = mtInit(Thread::self());
    dprintf(2)("time: %s, signaling end of worker init\n",stopwatch_dump);
    Thread::Mutex::Lock lock(worker_cond);
    dprintf(3)("time spent waiting for worker_cond mutex: %s\n",stopwatch_dump);
    num_initialized_workers++;
    worker_cond.broadcast();
    lock.release();
    // wait for main thread to complete startup
    stopwatch_reset;
    dprintf(2)("waiting for WP startup to complete\n");
    lock.relock(startup_cond);
    dprintf(3)("time spent waiting for startup_cond mutex: %s\n",stopwatch_dump);
    while( !started )
      startup_cond.wait();
    lock.release();
    dprintf(2)("WP startup complete, time: %s\n",stopwatch_dump);
    // exit if init was false
    if( !res )
    {
      dprintf(2)("mtinit()=False, exiting worker thread\n");
      return 0;
    }
    // do startup, exit if false
    dprintf(2)("starting worker thread\n");
    stopwatch_reset;
    res = mtStart(Thread::self());
    dprintf(2)("mtStart() time: %s\n",stopwatch_dump);
    if( !res )
    {
      dprintf(2)("mtstart()=False, exiting worker thread\n");
      return 0;
    }
    // run the worker thread
    dprintf(2)("running worker thread\n");
    runWorker();
    // once it exits, call mtStop() and exit
    dprintf(2)("stopping worker thread\n");
    mtStop(Thread::self());
  }
  catch( std::exception &exc )
  {
    lprintf(0,AidLogFatal,"worker thread %d terminated with exception: %s",(int)Thread::self(),exc.what());
  }
  return 0;
}

//##ModelId=3DB937210093
void * WPInterface::start_workerThread (void *pwp)
{
  return static_cast<WPInterface*>(pwp)->workerThread();
}

//##ModelId=3DB9370203A9
int WPInterface::wakeWorker (bool everybody)
{
  Thread::Mutex::Lock lock(queue_cond);
  return everybody ? queue_cond.broadcast() : queue_cond.signal();
}

//##ModelId=3DB937050309
int WPInterface::repollWorker (bool everybody)
{
  Thread::Mutex::Lock lock(queue_cond);
  setNeedRepoll(True);
  return everybody ? queue_cond.broadcast() : queue_cond.signal();
}

//##ModelId=3DB9370200EC
Thread::ThrID WPInterface::createWorker ()
{
  // threaded WPs are not polled
  disablePolling();
  dprintf(2)("launching worker thread\n");
  FailWhen(num_worker_threads>=MaxWorkerThreads,"too many worker threads started");
  stopwatch_init;
  // launch worker thread
  Thread::Mutex::Lock lock(worker_cond);
  dprintf(3)("time to obtain worker_cond mutex: %s\n",stopwatch_dump);
  Thread::ThrID thr = Thread::create(start_workerThread,this);
  dprintf(3)("time to create thread: %s\n",stopwatch_dump);
  FailWhen(!thr,"Thread::create failed");
  worker_threads[num_worker_threads++] = thr;
  // wait for the worker thread to complete its startup
  dprintf(2)("waiting for WT %d to complete initialization\n",(int)thr);
  stopwatch_reset;
  while( num_initialized_workers < num_worker_threads )
    worker_cond.wait();
  dprintf(2)("WT %d startup complete after %s\n",(int)thr,stopwatch_dump);
  return thr;
}
#endif



// Class WPInterface 

//##ModelId=3CA07E5F00D8
int WPInterface::logLevel_ = 2;

//##ModelId=3C7CBB10027A
//##ModelId=3DB93715004D
//##ModelId=3DB9371502EC
WPInterface::WPInterface (AtomicID wpc)
  : DebugContext(wpc.toString(),&OctopussyDebugContext::getDebugContext()),
    config(OctopussyConfig::global()),
    address_(wpc),state_(0),running(False),autoCatch_(False),
    dsp_(0),queue_(0),wpid_(wpc)
{
  full_lock = receive_lock = started = False;
  enablePolling();
#ifdef USE_THREADS
  num_worker_threads = num_initialized_workers = 0;
#endif
}


//##ModelId=3DB936E700B2
WPInterface::~WPInterface()
{
}



//##ModelId=3C7CBAED007B
void WPInterface::attach (Dispatcher* pdsp)
{
  dsp_ = pdsp;
}

//##ModelId=3C99B0070017
void WPInterface::do_init ()
{
  setNeedRepoll(False);
  full_lock = receive_lock = started = False;
  running = True;
  if( autoCatch() )
  {
    try { 
      init(); 
    }
    catch(std::exception &exc) {
      lprintf(0,AidLogFatal,"caught exception in init(): %s; shutting down",exc.what());
      dsp()->detach(this,True);
    }
  }
  else  
    init();
}

//##ModelId=3C99B00B00D1
bool WPInterface::do_start ()
{
#ifdef ENABLE_LATENCY_STATS
  Timestamp now;
  last_lat_report = now;
  tot_qlat.reset();
  tot_qlat_mt.reset();
  nlat = nlat_mt = 0;
#ifdef USE_THREADS
  tsw.none.total.reset();
  tsw.some.total.reset();
  tsw.multi.total.reset();
  tsw.all.total.reset();
  tsw.none.start = now;
  tsw.last_report = now;
  num_waiting_workers = 0;
#endif
#endif
  log("starting up",2);
  MessageRef ref(new Message(MsgHello|address()),DMI::ANON|DMI::WRITE);
  publish(ref);
  
  if( autoCatch() )
  {
    try { 
      raiseNeedRepoll( start() );
    }
    catch(std::exception &exc) {
      lprintf(0,AidLogFatal,"caught exception in start(): %s; shutting down",exc.what());
      dsp()->detach(this,True);
      return False;
    }
  }
  else  
    raiseNeedRepoll( start() );
  // publish subscriptions (even if empty)
  publishSubscriptions();
  
  // startup complete (need to advertise this to worker threads, if any)
#ifdef USE_THREADS
  dprintf(2)("broadcasting that start() is complete\n");
  stopwatch_init;
  Thread::Mutex::Lock lock(startup_cond);
  dprintf(3)("time to obtain startup_cond mutex: %s\n",stopwatch_dump);
  started = True;
  startup_cond.broadcast();
  lock.release();
#else
  started = True;
#endif
  return needRepoll();
}

//##ModelId=3C99B00F0254
void WPInterface::do_stop ()
{
  log("stopping",2);
  MessageRef ref(new Message(MsgBye|address()),DMI::ANON|DMI::WRITE);
  publish(ref);
  running = False;
#ifdef USE_THREADS
  // if running worker threads, stop them now
  if( num_worker_threads )
  {
    // wake them all up so that they all exit (they ought to check for isRunning()!)
    repollWorker(True);
    // join them
    for( int i=0; i<num_worker_threads; i++ )
    {
      dprintf(2)("re-joining worker thread %d\n",(int)worker_threads[i]);
      worker_threads[i].join();
    }
  }
#endif
  // call the normal stop callback
  if( autoCatch() )
  {
    try { 
      stop();
    }
    catch(std::exception &exc) {
      lprintf(0,AidLogError,"caught exception in stop(): %s; ignoring",exc.what());
    }
  }
  else  
    stop();
  // wake up anyone who may be waiting on the queue condition variable
#ifdef USE_THREADS
  queueCondition().broadcast();
#endif
}

//##ModelId=3C7F882B00E6
void WPInterface::init ()
{
}

//##ModelId=3C7E4A99016B
bool WPInterface::start ()
{
  return False;
}

//##ModelId=3C7E4A9C0133
void WPInterface::stop ()
{
}

void WPInterface::notify ()
{
}

//##ModelId=3CB55EEA032F
int WPInterface::getPollPriority (ulong tick)
{
  if( !pollingEnabled() )
    return -1;
  // return queue priority, provided a repoll is required
  // note that we add the message age (tick - QueueEntry.tick) to its
  // priority. Thus, messages that have been sitting undelivered for a while
  // (perhaps because the system is saturated with higher-priority messages)
  // will eventually get bumped up and become favoured.
  
  if( needRepoll() && !queueLocked() )
  {
    Thread::Mutex::Lock lock(queue_cond);
    if( !queue().empty() )
    {
      const QueueEntry &qe = queue().front();
      int lowest = Message::PRI_LOWEST;
      return max(qe.priority,lowest) + static_cast<int>(tick - qe.tick);
    }
  }
  return -1;
}

//##ModelId=3C8F13B903E4
bool WPInterface::do_poll (ulong tick)
{
  FailWhen( !pollingEnabled(),"do_poll called on non-polled WP");
  // Call the virtual poll method, and set needRepoll according to what
  // it has returned.
  if( autoCatch() )
  {
    try { 
      setNeedRepoll( poll(tick) );
    }
    catch(std::exception &exc) {
      lprintf(2,AidLogError,"caught exception in poll(): %s; ignoring",exc.what());
    }
  }
  else  
    setNeedRepoll( poll(tick) );
  
  // lock queue because other threads may be running
  Thread::Mutex::Lock lock(queue_cond);
  // return if queue is empty
  if( queue().empty() )
    return needRepoll();  
  int res = Message::ACCEPT;
  
  // get ref to first queue entry
  QueueEntry & qe = queue().front();
// we no longer pop: see below. queue().pop_front();
  lock.release(); // release the queue lock
  
#ifdef ENABLE_LATENCY_STATS
  Timestamp now;
  tot_qlat += now - qe.ts;
  nlat++;
  if( Timestamp::now().seconds() >= last_lat_report + 10 )
  {
    if( nlat )
    {
      dprintf(1)("%d messages delivered, average latency %.3fms\n",
          nlat,tot_qlat.seconds()*1e-3/nlat);
    }
    last_lat_report = now.seconds();
    tot_qlat.reset();
    nlat = 0;
  }
#endif
  
  const Message &msg = qe.mref.deref();
  const HIID &id = msg.id();
  FailWhen( id.empty(),"null message ID" );
  dprintf1(3)("%s: receiving %s\n",sdebug(1).c_str(),msg.debug(1));
  // is it a system event message?
  if( id[0] == AidEvent ) 
  {
    if( full_lock ) 
      return False;
    if( id[1] == AidTimeout ) // deliver timeout message
    {
      FailWhen( id.size() < 2,"malformed "+id.toString()+" message" );
      HIID to_id = id.subId(2);
      res = Message::ACCEPT;
      if( autoCatch() )
      {
        try { 
          res = timeout(to_id);
        }
        catch(std::exception &exc) {
          lprintf(2,AidLogError,"caught exception in timeout(): %s; ignoring",exc.what());
        }
      }
      else  
        res = timeout(to_id);
      if( res == Message::CANCEL )
        dsp()->removeTimeout(this,to_id);
      res = Message::ACCEPT;
    }
    else if( id[1] == AidInput ) // deliver input message
    {
      FailWhen( id.size() != 3,"malformed "+id.toString()+" message" );
      int fd=id[2],flags=msg.state();
      if( flags )  // no flags? Means the input has been already removed. Ignore
      {
        res = Message::ACCEPT;
        if( autoCatch() )
        {
          try { 
            res = input(fd,flags);
          }
          catch(std::exception &exc) {
            lprintf(2,AidLogError,"caught exception in input(): %s; ignoring",exc.what());
          }
        }
        else  
          res = input(fd,flags);
        if( res == Message::CANCEL )
          dsp()->removeInput(this,fd,flags);
        res = Message::ACCEPT;
      }
    }
    else if( id[1] == AidSignal ) // deliver input message
    {
      FailWhen( id.size() != 3,"malformed "+id.toString()+" message" );
      int signum = id[2];
      res = Message::ACCEPT;
      if( autoCatch() )
      {
        try { 
          res = signal(signum);
        }
        catch(std::exception &exc) {
          lprintf(2,AidLogError,"caught exception in signal(): %s; ignoring",exc.what());
        }
      }
      else  
        res = signal(signum);
      if( res == Message::CANCEL )
        dsp()->removeSignal(this,signum);
      res = Message::ACCEPT;
    }
    else
      Throw("unexpected event" + id.toString());
    // Once the event has been delivered, reset its state to 0.
    // This helps the dispatcher keep track of when a new event message is
    // required (as opposed to updating a previous message that's still
    // undelivered). See Dispatcher::checkEvents() for details.
    if( qe.mref.isWritable() )
      qe.mref().setState(0);
  }
  else // deliver regular message
  {
    if( receive_lock || full_lock )
      return False;
    // lock 
    receive_lock = True;
    res = Message::ACCEPT;
    if( autoCatch() )
    {
      try { 
        res = receive(qe.mref);
      }
      catch(std::exception &exc) {
        lprintf(2,AidLogError,"caught exception in receive(): %s; ignoring message",exc.what());
      }
    }
    else  
      res = receive(qe.mref);
    receive_lock = False;
  }
  lock.relock(queue_cond);
  // dispence of queue accordingly
  Message::Ref mref;
  if( res == Message::REQUEUE )
    mref = qe.mref;   // save a ref to the message, since it will need requeuing
  
  // if message was accepted or requeued, we have to remove the queue entry
  if( res == Message::ACCEPT || res == Message::REQUEUE )
  {
    // something else may be at the head of the queue
    // by now. So, scan through the queue until we locate the entry
    MQI iter = queue().begin();
    for( ; iter != queue().end(); iter++ )
      if( &qe == &(*iter) )
      {
        queue().erase(iter);
        break;
      }
  }
  // dispense with message depending on result code
  if( res == Message::ACCEPT )   
  {
    dprintf(3)("result code: OK, message dequeued\n");
    // if queue is not empty, we need a repoll
    if( !queue().empty() )
    {
      // this resets the age at the head of the queue. Effectively, this means
      // we have a "queue age" rather than a message age.
      queue().front().tick = tick;
      return setNeedRepoll(True);
    }
  }
  else if( res == Message::HOLD ) // not accepted
  {
    FailWhen( !qe.mref.valid(),"message was not accepted but its ref was detached or xferred" );
    dprintf(3)("result code: HOLD, leaving in place\n");
    // needRepoll will have been raised if something else was placed at the head 
    // of the queue
    return needRepoll();
  }
  else if( res == Message::REQUEUE )
  {
    FailWhen( !mref.valid(),"message was not accepted but its ref was detached or xferred" );
    dprintf(3)("result code: REQUEUE, requeueing\n");
    // re-insert into queue according to priority. Ask enqueue() to not
    // raise the repoll flag, since we do that explicitly just below
    enqueue(mref,tick,ENQ_NOREPOLL);  
    if( !queue().empty() )
    {
      // this resets the age at the head of the queue. Effectively, this means
      // we have a "queue age" rather than a message age.
      queue().front().tick = tick;
      // if head of queue has changed, we need a repoll
      if( queue().front().mref != mref )
        return setNeedRepoll(True);
    }
  }

  return needRepoll();
}

//##ModelId=3CB55D0E01C2
bool WPInterface::poll (ulong )
{
  return False;
}

void WPInterface::notifyOfRepoll (bool do_signal)
{
  setNeedRepoll(True);
  if( do_signal )
    queue_cond.signal();
  notify();
}

//##ModelId=3C8F204A01EF
int WPInterface::enqueue (const MessageRef &msg, ulong tick, int flags)
{
  Thread::Mutex::Lock lock(queue_cond);
  int pri = msg->priority();
  QueueEntry qe(msg,pri,tick);
  // some optimizations here to optimize lookup time for very long queues
  bool setrepoll = !(flags&ENQ_NOREPOLL),
       do_signal = !(flags&ENQ_NOSIGNAL);
  
  
  // (a): empty queue
  if( queue().empty() )
  {
    dprintf(3)("queueing [%s] into empty queue {case:A}\n",qe.mref->debug(1));
    if( setrepoll )
      notifyOfRepoll(do_signal);
    queue().push_front(qe);
    return pri;
  }
  // (b): message belongs at back
  int back_pri = queue().back().priority;
  if( pri <= back_pri )
  {
    dprintf(3)("queueing [%s] at end of queue {case:B}\n",qe.mref->debug(1));
    queue().push_back(qe);
    return -1;
  }
  // (c): message belongs at front
  int front_pri = queue().front().priority;
  if( pri > front_pri )
  {
    dprintf(3)("queueing [%s] at head of queue {case:C}\n",qe.mref->debug(1));
    if( setrepoll )
      notifyOfRepoll(do_signal);
    queue().push_front(qe);
    return pri;
  }
  // (d): iterate to find the right spot
  // iterate from head of queue() as long as msg priority is higher
  MQI iter = queue().begin();
  int count = 0;
  while( iter != queue().end() && iter->priority >= pri )
    iter++,count++;
  // if inserting at head of queue, then raise the repoll flag
  if( !count )
  {
    dprintf(3)("queueing [%s] at head of queue {case:D}\n",qe.mref->debug(1));
    if( setrepoll )
      notifyOfRepoll(do_signal);
    return pri;
  }
  dprintf(3)("queueing [%s] at h+%d {case:D}\n",qe.mref->debug(1),count);
  queue().insert(iter,qe);
  return -1;
}

//##ModelId=3C8F204D0370
bool WPInterface::dequeue (const HIID &id, MessageRef *ref)
{
  Thread::Mutex::Lock lock(queue_cond);
  bool erased_head = True;
  for( MQI iter = queue().begin(); iter != queue().end(); )
  {
    if( id.matches( iter->mref->id() ) )
    {
      // is this the head of the queue? 
      erased_head |= ( iter == queue().begin() );
      if( ref )
        *ref = iter->mref; // xfer the reference
      queue().erase(iter++);
      // we're done if a ref was asked for
      if( ref )
        break;
    }
    else
      iter++;
  }
  if( erased_head && !queue().empty() )
  {
    setNeedRepoll(True);
    queue_cond.signal();
  }
  return needRepoll();
}

//##ModelId=3C8F205103D0
bool WPInterface::dequeue (int pos, MessageRef *ref)
{
  Thread::Mutex::Lock lock(queue_cond);
  int qsz = queue().size();
  FailWhen( pos >= qsz,"dequeue: illegal position" );
  if( !pos && qsz>1 )
  {
    setNeedRepoll(True);
    queue_cond.signal();
  }
  // iterate to the req. position
  MQI iter = queue().begin();
  while( pos-- )
    iter++;
  if( ref )
    *ref = iter->mref;
  queue().erase(iter);
  return needRepoll();
}

//##ModelId=3C8F205601EC
int WPInterface::searchQueue (const HIID &id, int pos, MessageRef *ref)
{
  Thread::Mutex::Lock lock(queue_cond);
  FailWhen( (uint)pos >= queue().size(),"dequeue: illegal position" );
  // iterate to the req. position
  MQI iter = queue().begin();
  for( int i=0; i<pos; i++ )
    iter++;
  // start searching
  for( ; iter != queue().end(); iter++,pos++ )
    if( id.matches( iter->mref->id() ) )
    {
      if( ref )
        *ref = iter->mref.copy(DMI::PRESERVE_RW);
      return pos;
    }
  // not found
  return -1;
}

//##ModelId=3C8F206C0071
bool WPInterface::queueLocked () const
{
  if( full_lock )
    return True;
  if( receive_lock )
  {
    Thread::Mutex::Lock lock(queue_cond);
    return !queue().empty() && queue().front().mref->id()[0] != AidEvent;
  }
  return False;
}

//##ModelId=3C99AB6E0187
bool WPInterface::subscribe (const HIID &id, const MsgAddress &scope)
{
  // If something has changed in the subs, _and_ WP has been started,
  // then re-publish the whole thing.
  // (If not yet started, then everything will be eventually published 
  // by do_start(), above)
  dprintf(2)("subscribing to %s scope %s\n",id.toString().c_str(),scope.toString().c_str());
  bool change = subscriptions.add(id,scope);
  if( change  && started )
    publishSubscriptions();
  return change;
}

//##ModelId=3C7CB9C50365
bool WPInterface::unsubscribe (const HIID &id)
{
  // If something has changed in the subs, _and_ WP has been started,
  // then re-publish the whole thing.
  // (If not yet started, then everything will be eventually published 
  // by do_start(), above)
  dprintf(2)("unsubscribing from %s\n",id.toString().c_str());
  bool change = subscriptions.remove(id);
  if( change && started )
    publishSubscriptions();
  return change;
}

//##ModelId=3C7CC0950089
int WPInterface::receive (MessageRef &mref)
{
  dprintf(1)("unhandled receive(%s)\n",mref->sdebug(1).c_str());
  return Message::ACCEPT;
}

//##ModelId=3C7CC2AB02AD
int WPInterface::timeout (const HIID &id)
{
  dprintf(1)("unhandled timeout(%s)\n",id.toString().c_str());
  return Message::ACCEPT;
}

//##ModelId=3C7CC2C40386
int WPInterface::input (int fd, int flags)
{
  dprintf(1)("unhandled input(%d,%x)\n",fd,flags);
  return Message::ACCEPT;
}

//##ModelId=3C7DFD240203
int WPInterface::signal (int signum)
{
  dprintf(1)("unhandled signal(%s)\n",sys_siglist[signum]);
  return Message::ACCEPT;
}

//##ModelId=3C7CB9E802CF
int WPInterface::send (MessageRef msg, MsgAddress to, int)
{
  FailWhen( !isAttached(),"unattached wp");
  // if not writable, privatize for writing (but not deeply)
  if( !msg.isWritable() )
    msg.privatize(DMI::WRITE);
  msg().setHops(0);
  msg().setFrom(address());
  msg().setState(state());
  dprintf(2)("send [%s] to %s\n",msg->sdebug(1).c_str(),to.toString().c_str());
  // substitute 'Local' for actual addresses
  if( to.host() == AidLocal )
    to.host() = address().host();
  if( to.process() == AidLocal )
    to.process() = address().process();
  return dsp()->send(msg,to); 
}

//##ModelId=3CBDAD020297
int WPInterface::send (const HIID &id, MsgAddress to, int , int priority)
{
  MessageRef msg( new Message(id,priority),DMI::ANON|DMI::WRITE );
  return send(msg,to);
}

//##ModelId=3C7CB9EB01CF
int WPInterface::publish (MessageRef msg,int , int scope)
{
  FailWhen( !isAttached(),"unattached wp");
  // if not writable, privatize for writing (but not deeply)
  if( !msg.isWritable() )
    msg.privatize(DMI::WRITE);
  msg().setFrom(address());
  msg().setState(state());
  msg().setHops(0);
  dprintf(2)("publish [%s] scope %d\n",msg->sdebug(1).c_str(),scope);
  AtomicID host = (scope < Message::GLOBAL) ? address().host() : AidAny;
  AtomicID process = (scope < Message::HOST) ? address().process() : AidAny;
  return dsp()->send(msg,MsgAddress(AidPublish,AidPublish,process,host));
}

//##ModelId=3CBDACCC028F
int WPInterface::publish (const HIID &id,int,int scope, int priority)
{
  MessageRef msg( new Message(id,priority),DMI::ANON|DMI::WRITE );
  return publish(msg,scope);
}

//##ModelId=3CBED9EF0197
void WPInterface::setState (int newstate, bool delay_publish)
{
  if( state_ != newstate )
  {
    state_ = newstate;
    if( started && !delay_publish )
      publish(MsgWPState);
  }
}

//##ModelId=3CA0457F01BD
void WPInterface::log (string str, int level, AtomicID type)
{
  if( level > logLevel() )
    return;
  // see if type override was specified in the string
  const char * stypes[] = { "warning:", "error:", "fatal:", "debug:", "normal:" };
  const AtomicID types[] = { AidLogWarning,AidLogError,AidLogFatal,AidLogDebug,AidLogNormal };
  for( int i=0; i<4; i++ )
  {
    uint len = strlen(stypes[i]);
    if( str.length() >= len && !strncasecmp(str.c_str(),stypes[i],len) )
    {
      type = types[i];
      // chop the override string off
      while( len < str.length() && isspace(str[len]) )
        len++;
      str = str.substr(len);
      break;
    }
  }
  // duplicate to stdout if appropriate debug level is set
  if( level <= DebugLevel )
  {
    const char *tps = "";
    if( type == AidLogWarning )
      tps = stypes[0];
    else if( type == AidLogError )
      tps = stypes[1];
    Debug::getDebugStream()<<sdebug(1)<<":"<<tps<<" "<<str;
    if( str[str.length()-1] != '\n' )
      Debug::getDebugStream()<<endl;
  }
  // publish as MsgLog
  MessageRef mref;
  DataRecord &rec = Message::withDataRecord(mref,AidMsgLog|type|level,str);
  rec[AidType] = type;
  rec[AidLevel] = level;
  publish(mref);
}

//##ModelId=3CA0738D007F
void WPInterface::lprintf (int level, int type, const char *format, ... )
{
  if( level > logLevel() )
    return;
  // create the string
  char str[1024];
  va_list(ap);
  va_start(ap,format);
  vsnprintf(str,sizeof(str),format,ap);
  va_end(ap);
  log(str,level,type);
}

//##ModelId=3CA0739F0247
void WPInterface::lprintf (int level, const char *format, ... )
{
  if( level > logLevel() )
    return;
  char str[1024];
  va_list(ap);
  va_start(ap,format);
  vsnprintf(str,sizeof(str),format,ap);
  va_end(ap);
  log(str,level,AidLogNormal);
}

// Additional Declarations
//##ModelId=3DB936F40172
bool WPInterface::compareHeadOfQueue( const Message *pmsg )
{
  Thread::Mutex::Lock lock(queue_cond);
  if( queue().empty() )
    return False;
  return queue().front().mref.deref_p() == pmsg;
}


// enqueues message _in front_ of all messages with lesser or equal priority
// This is used for the HOLD result code (i.e. to leave message at head of
// queue, unless something with higher priority has arrived while we were
// processing it)
//##ModelId=3DB937190389
bool WPInterface::enqueueFront (const MessageRef &msg, ulong tick,bool setrepoll)
{
  Thread::Mutex::Lock lock(queue_cond);
  int pri = msg->priority();
  // iterate from head of queue(), as long as msg priority is higher
  MQI iter = queue().begin();
  int count = 0;
  while( iter != queue().end() && iter->priority > pri )
    iter++,count++;
  // if inserting at head of queue, then raise the repoll flag
  if( !count )
  {
    dprintf(3)("queueing [%s] at head of queue\n",msg->debug(1));
    if( setrepoll )
    {
      setNeedRepoll(True);
      queue_cond.signal();
    }
  }
  else
    dprintf(3)("queueing [%s] at h+%d\n",msg->debug(1),count);
  queue().insert(iter,QueueEntry(msg,pri,tick));
  return needRepoll();
}




//##ModelId=3DB937130361
void WPInterface::publishSubscriptions ()
{
  // pack subscriptions into a block
  size_t sz = subscriptions.packSize();
  BlockRef bref(new SmartBlock(sz),DMI::ANON|DMI::WRITE);
  subscriptions.pack(bref().data(),sz);
  // publish it
  MessageRef ref( new Message(MsgSubscribe|address(),
                              bref,0),
                  DMI::ANONWR);
  publish(ref);
}


string WPInterface::sdebug ( int detail,const string &,const char *nm ) const
{
  string out;
  if( detail>=0 ) // basic detail
  {
    if( nm )
      out = string(nm) + "/";
    out += address().toString();
    out += Debug::ssprintf("/%08x",this);
#ifdef USE_THREADS
    if( num_worker_threads )
      Debug::appendf(out,"T%d",(int)Thread::self());
#endif
    Thread::Mutex::Lock lock(queue_cond);
    Debug::appendf(out,"Q:%d",queue().size());
  }
  if( detail >= 1 || detail == -1 )   // normal detail
  {
    Debug::appendf(out,"st:%d",state_);
  }
  return out;
}


