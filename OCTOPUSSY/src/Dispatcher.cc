//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C7B7F30004B.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C7B7F30004B.cm

//## begin module%3C7B7F30004B.cp preserve=no
//## end module%3C7B7F30004B.cp

//## Module: Dispatcher%3C7B7F30004B; Package body
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\Dispatcher.cc

//## begin module%3C7B7F30004B.additionalIncludes preserve=no
//## end module%3C7B7F30004B.additionalIncludes

//## begin module%3C7B7F30004B.includes preserve=yes
#include <sys/time.h>
#include <errno.h>
#include <string.h>
#include "OCTOPUSSY/OctopussyConfig.h"
//## end module%3C7B7F30004B.includes

// WPInterface
#include "OCTOPUSSY/WPInterface.h"
// Dispatcher
#include "OCTOPUSSY/Dispatcher.h"
//## begin module%3C7B7F30004B.declarations preserve=no
//## end module%3C7B7F30004B.declarations

//## begin module%3C7B7F30004B.additionalDeclarations preserve=yes
// pulls in registry definitions
static int dum = aidRegistry_OCTOPUSSY();

Dispatcher * Dispatcher::dispatcher = 0;
sigset_t Dispatcher::raisedSignals,Dispatcher::allSignals;
struct sigaction * Dispatcher::orig_sigaction[_NSIG];
bool Dispatcher::stop_polling = False;

int Dispatcher::signal_counter[Dispatcher::max_signals];

      
// static signal handler

void Dispatcher::signalHandler (int signum,siginfo_t *,void *)
{
#ifdef USE_THREADS
  printf("thread %d: received signal %d (%s)\n",(int)Thread::self(),signum,sys_siglist[signum]);
#endif
  sigaddset(&raisedSignals,signum);
  signal_counter[signum]++;
  // interrupt any poll loops
  if( signum == SIGINT )
    stop_polling = True;
}
//## end module%3C7B7F30004B.additionalDeclarations


// Class Dispatcher 

Dispatcher::Dispatcher (AtomicID process, AtomicID host, int hz)
  //## begin Dispatcher::Dispatcher%3C7CD444039C.hasinit preserve=no
  //## end Dispatcher::Dispatcher%3C7CD444039C.hasinit
  //## begin Dispatcher::Dispatcher%3C7CD444039C.initialization preserve=yes
    : DebugContext("Dsp",&OctopussyDebugContext::getDebugContext()),
      heartbeat_hz(hz),
      config(OctopussyConfig::global())
  //## end Dispatcher::Dispatcher%3C7CD444039C.initialization
{
  //## begin Dispatcher::Dispatcher%3C7CD444039C.body preserve=yes
  address = MsgAddress(AidDispatcher,0,process,host);
  memset(signal_counter,0,sizeof(signal_counter));
  // init everything
  init();
  //## end Dispatcher::Dispatcher%3C7CD444039C.body
}

Dispatcher::Dispatcher (int hz)
  //## begin Dispatcher::Dispatcher%3CD012B70209.hasinit preserve=no
  //## end Dispatcher::Dispatcher%3CD012B70209.hasinit
  //## begin Dispatcher::Dispatcher%3CD012B70209.initialization preserve=yes
    : DebugContext("Dsp",&OctopussyDebugContext::getDebugContext()),
      heartbeat_hz(hz),
      config(OctopussyConfig::global())
  //## end Dispatcher::Dispatcher%3CD012B70209.initialization
{
  //## begin Dispatcher::Dispatcher%3CD012B70209.body preserve=yes
  // check that required config items have been found
  int hostid = 0;
  if( !config.get("hostid",hostid) )
    dprintf(0)("warning: hostid not configured, using 1\n");
  // setup address
  address = MsgAddress(AidDispatcher,0,getpid(),hostid);
  init();
  //## end Dispatcher::Dispatcher%3CD012B70209.body
}


Dispatcher::~Dispatcher()
{
  //## begin Dispatcher::~Dispatcher%3C7B6A3E00A0_dest.body preserve=yes
  if( running )
    stop();
  wps.clear();
  dispatcher = 0;
  //## end Dispatcher::~Dispatcher%3C7B6A3E00A0_dest.body
}



//## Other Operations (implementation)
void Dispatcher::init ()
{
  //## begin Dispatcher::init%3CD014D00180.body preserve=yes
  if( dispatcher )
    Throw("multiple Dispatchers initialized");
  dispatcher = this;
  // set the log levels
  int lev;
  if( config.get("wploglevel",lev) || 
      config.getOption("lc",lev) || 
      config.getOption("l",lev) )
    WPInterface::setLogLevel(lev);
  // set the frequency
  config.get("hz",heartbeat_hz);
  // init internals
  memset(orig_sigaction,0,sizeof(orig_sigaction));
  sigemptyset(&raisedSignals);
  sigemptyset(&allSignals);
  running = in_start = False;
  poll_depth = -1;
  dprintf(1)("created\n");
  //## end Dispatcher::init%3CD014D00180.body
}

const MsgAddress & Dispatcher::attach (WPRef &wpref)
{
  //## begin Dispatcher::attach%3C8CDDFD0361.body preserve=yes
  // lock mutex on entry
  Thread::Mutex::Lock lock(wpmutex);
  FailWhen( !wpref.isWritable(),"writable ref required" ); 
  WPInterface & wp = wpref;
  FailWhen( wp.isAttached() && wp.dsp() != this,"wp is already attached" );
  // assign instance number to this WP
  AtomicID wpclass = wp.address().wpclass();
  int ninst = wp_instances[wpclass]++;
  WPID wpid(wpclass,ninst);
  wp.setAddress( MsgAddress(wpid,processId(),hostId()) );
  dprintf(1)("attaching WP: %s\n",wp.sdebug().c_str());
  wp.attach(this);
  // if already starting up, then place attached wps onto a temp stack,
  // to be attached later.
  if( in_start )
    attached_wps.push(wpref); // let start handle it
  else // add to map and activate
  {
    (wps[wpid] = wpref).persist();
    lock.release();
    if( running )
    {
      wp.do_init();
      if( wp.do_start() )
        repoll = True;
    }
  }
  return wp.address();
  //## end Dispatcher::attach%3C8CDDFD0361.body
}

const MsgAddress & Dispatcher::attach (WPInterface* wp, int flags)
{
  //## begin Dispatcher::attach%3C7B885A027F.body preserve=yes
  WPRef ref(wp,flags|DMI::WRITE);
  return attach(ref);
  //## end Dispatcher::attach%3C7B885A027F.body
}

void Dispatcher::detach (WPInterface* wp, bool delay)
{
  //## begin Dispatcher::detach%3C8CA2BD01B0.body preserve=yes
  FailWhen( wp->dsp() != this,
      "wp '"+wp->sdebug(1)+"' is not attached to this dispatcher");
  detach(wp->address().wpid(),delay);
  //## end Dispatcher::detach%3C8CA2BD01B0.body
}

void Dispatcher::detach (const WPID &id, bool delay)
{
  //## begin Dispatcher::detach%3C8CDE320231.body preserve=yes
  // lock mutex on entry
  Thread::Mutex::Lock lock(wpmutex);
  WPI iter = wps.find(id); 
  FailWhen( iter == wps.end(),
      "wpid '"+id.toString()+"' is not attached to this dispatcher");
  WPInterface *pwp = iter->second;
  // remove all events associated with this WP
  for( TOILI iter = timeouts.begin(); iter != timeouts.end(); )
    if( iter->pwp == pwp )
      timeouts.erase(iter++);
    else
      iter++;
  rebuildInputs(pwp);
  rebuildSignals(pwp);
  // if asked to delay, then move WP ref to delay stack, it will be
  // detached later in poll() (together with the do_stop() call)
  if( delay )   
    detached_wps.push(iter->second);
  else
    pwp->do_stop();
  wps.erase(iter);
  GWI iter2 = gateways.find(id);
  if( iter2 != gateways.end() )
    gateways.erase(iter2);
  //## end Dispatcher::detach%3C8CDE320231.body
}

void Dispatcher::declareForwarder (WPInterface *wp)
{
//## begin Dispatcher::declareForwarder%3C95C73F022A.body preserve=yes
  // lock mutex on entry
  Thread::Mutex::Lock lock(wpmutex);
  CWPI iter = wps.find(wp->wpid()); 
  FailWhen( iter == wps.end() || iter->second.deref_p() != wp,
      "WP not attached to this dispatcher");
  gateways[wp->wpid()] = wp;
  //## end Dispatcher::declareForwarder%3C95C73F022A.body
}

void Dispatcher::start ()
{
  //## begin Dispatcher::start%3C7DFF770140.body preserve=yes
  running = in_start = True;
  in_pollLoop = False;
  stop_polling = False;
  tick = 0;
  // say init to all WPs
  dprintf(1)("starting\n");
  dprintf(2)("start: initializing WPs\n");
  for( WPI iter = wps.begin(); iter != wps.end(); iter++ )
    iter->second().do_init();

#ifdef USE_THREADS
  // main thread blocks all signals
  main_thread = Thread::self();
  Thread::signalMask(SIG_BLOCK,validSignals());
  // launch event processing thread -- no timer required
  event_thread = Thread::create(start_eventThread,this);
#else
  // setup heartbeat timer
  long period_usec = 1000000/heartbeat_hz;
  // when stuck in a poll loop, do a select() at least this often:
  inputs_poll_period = Timestamp(0,period_usec/2);
  next_select = Timestamp::now();
// start heartbeat timer
  struct itimerval tval = { {0,period_usec},{0,period_usec} };
  setitimer(ITIMER_REAL,&tval,0);
#endif
  
  // init event processing
  sigemptyset(&raisedSignals);
  rebuildSignals();
  num_active_fds = 0;
  rebuildInputs();
  
  // say start to all WPs. Note that some WP's subthreads may already re-enter
  // the dispatcher at this point, so we can't hold a mutex on the wp map.
  // Hence, we make a copy and iterate over that copy.
  dprintf(2)("start: starting WPs\n");
  map<WPID,WPRef> wps1 = wps;
  for( WPI iter = wps1.begin(); iter != wps1.end(); iter++ )
    if( iter->second().do_start() )
      repoll = True;
  
#ifdef USE_THREADS
// signal that start is complete so that the event thread can proceed
  {
    Thread::Mutex::Lock lock(repoll_cond);
    in_start = False;
    repoll_cond.signal();
  }
#else
  in_start = False;
#endif
  
  // if someone has launched any new WPs already, start them now
  Thread::Mutex::Lock lock(wpmutex);
  if( !attached_wps.empty() )
  {
    dprintf(2)("start: initializing %d dynamically-added WPs\n",attached_wps.size());
    while( !attached_wps.empty() )
    {
      WPRef ref = attached_wps.top();
      attached_wps.pop();
      // release the wp map mutex before doing init or start on the wp
      lock.release();
      ref().do_init();
      if( ref().do_start() )
        repoll = True;
      lock.relock(wpmutex);
      (wps[ref->wpid()] = ref).persist();
    }
  }
  dprintf(2)("start: complete\n");
  //## end Dispatcher::start%3C7DFF770140.body
}

void Dispatcher::stop ()
{
  //## begin Dispatcher::stop%3C7E0270027B.body preserve=yes
  dprintf(1)("stopping\n");
#ifdef USE_THREADS
  running = False;
  stop_polling = True;
  // if stop() is being called from a different thread than start(),
  // then assume we have a separate main thread, so kill it off
  if( Thread::self() != main_thread )
  {
    // use repoll_cond to wake up and terminate the polling thread
    Thread::Mutex::Lock lock(repoll_cond);
    repoll_cond.signal();
    lock.release();
    Thread::join(main_thread);
  }
  // cancel the event thread
  Thread::kill(event_thread,SIGUSR1);
  Thread::join(event_thread);
#else
  running = False;
  // stop the heartbeat timer
  struct itimerval tval = { {0,0},{0,0} };
  setitimer(ITIMER_REAL,&tval,0);
#endif
  // tell all WPs that we are stopping. Do not hold a mutex since they
  // may re-enter the dispatcher
  map<WPID,WPRef> wps1 = wps;
  for( WPI iter = wps1.begin(); iter != wps1.end(); iter++ )
    iter->second().do_stop();
  Thread::Mutex::Lock lock(wpmutex);
  // clear all event lists
  timeouts.clear();
  inputs.clear();
  signal_map.clear();
  // this will effectively remove all signal handlers
  rebuildSignals();
  //## end Dispatcher::stop%3C7E0270027B.body
}

int Dispatcher::send (MessageRef &mref, const MsgAddress &to)
{
  //## begin Dispatcher::send%3C7B8867015B.body preserve=yes
  int ndeliver = 0;
  Message &msg = mref;
  dprintf(2)("send(%s,%s)\n",msg.sdebug().c_str(),to.toString().c_str());
  // add latency measurement (no-op when compiled w/o -DENABLE_LATENCY_STATS)
  msg.latency.measure("<SND");
  // set the message to-address
  msg.setTo(to);
  // lock mutex on entry
  Thread::Mutex::Lock lock(wpmutex);
  // local delivery: check that host/process spec matches ours
  if( to.host().matches(hostId()) && to.process().matches(processId()) )
  {
    // addressed to specific wp class/instance?
    AtomicID wpc = to.wpclass(),wpi=to.inst();
    if( !wildcardAddr(wpc) && !wildcardAddr(wpi) )
    {
      WPI iter = wps.find(to.wpid()); // do we have that ID?
      if( iter != wps.end() )
      {
        dprintf(2)("  queing for: %s\n",iter->second->debug(1));
        // for first delivery, privatize the whole message & payload as read-only
        if( !ndeliver )
          mref.privatize(DMI::READONLY|DMI::DEEP);
        enqueue(iter->second,mref.copy());
        ndeliver++;
      }
    }
    else // else it's a publish/b-cast: scan thru all WPs
    {
      for( WPI iter = wps.begin(); iter != wps.end(); iter++ )
      {
        const MsgAddress & wpaddr = iter->second->address();
        if( wpc.matches(wpaddr.wpclass()) && wpi.matches(wpaddr.inst()) )
        {
          dprintf(2)("  delivering to %s\n",iter->second->debug(1));
        }
        else if( wpc == AidPublish && 
                 iter->second->getSubscriptions().matches(msg) )
        {
          dprintf(2)("  publishing to %s\n",iter->second->debug(1));
        }
        else // else continue, so as to skip the deligvery below
          continue;
        // for first delivery, privatize the whole message & payload as read-only
        if( !ndeliver )
          mref.privatize(DMI::READONLY|DMI::DEEP);
        enqueue(iter->second,mref.copy());
        ndeliver++;
      }
    }
  }
  else
    dprintf(2)("  destination address is not local\n");
  // If the message has a wider-than-local scope, then see if any gateways
  // will take it
  if( to.host() != hostId() || to.process() != processId() )
  {
    for( GWI iter = gateways.begin(); iter != gateways.end(); iter++ )
      if( iter->second->willForward(msg) )
      {
        dprintf(2)("  forwarding via %s\n",iter->second->debug(1));
        if( !ndeliver )
          mref.privatize(DMI::READONLY|DMI::DEEP);
        enqueue(iter->second,mref.copy());
        ndeliver++;
      }
  }
  if( !ndeliver )
    { dprintf(2)("not delivered anywhere\n"); }
  else
    { dprintf(3)("send done, ndeliver=%d, repoll=%d\n",ndeliver,(int)repoll); }
//  msg.latency.measure("SND>");
  return ndeliver;
  //## end Dispatcher::send%3C7B8867015B.body
}

void Dispatcher::poll (int maxloops)
{
  //## begin Dispatcher::poll%3C7B888E01CF.body preserve=yes
#ifndef USE_THREADS
  if( Debug(11) )
  {
    static Timestamp last_poll;
    Timestamp now;
    Timestamp elapsed = now - last_poll;
    dprintf(11)("entering poll() after %ld.%03ld ms\n",
                elapsed.sec()*1000+elapsed.usec()/1000,elapsed.usec()%1000);
    last_poll = now;
  }
#endif
  FailWhen(!running,"not running");
  // destroy all delay-detached WPs
  if( !++poll_depth )
  {
    Thread::Mutex::Lock lock(wpmutex);
    while( !detached_wps.empty() )
    {
      WPRef ref = detached_wps.top();
      detached_wps.pop();
      lock.release();
      ref().do_stop();
      ref.detach(); // this destroys the WP, if last ref
      lock.relock(wpmutex);
    }
  }
  // main polling loop
  int nloop = 0;
#ifdef USE_THREADS
  // threaded version: just loop while repoll is raised
  while( repoll && !stop_polling )
#else
  // non-threaded version: loop & check for events 
  while( !stop_polling && ( checkEvents() || repoll ) )
#endif
  {
    // break out if max number of loops exceeded
    if( maxloops >= 0 && nloop++ > maxloops )
      break;
    tick++;
    // find max priority queue
    int maxpri = -1;
    WPInterface *maxwp = 0;
    int num_repoll = 0; // # of WPs needing a repoll
    repoll = False;
    // Find WP with maximum polling priority
    // Count the number of WPs that required polling, too
    Thread::Mutex::Lock lock(wpmutex);
    for( WPI wpi = wps.begin(); wpi != wps.end(); wpi++ )
    {
      WPInterface *pwp = wpi->second;
      int pri = pwp->getPollPriority(tick);
      if( pri >= 0 )
      {
        num_repoll++;
        if( pri >= maxpri )
        {
          maxwp = pwp;
          maxpri = pri;
        }
      }
    }
    lock.release();
    // if more than 1 WP needs a repoll, force another loop
    if( num_repoll > 1 )
      repoll = True;
    // deliver message, if a queue was found
    if( maxwp )
    {
      dprintf(3)("poll: max priority %d in %s, repoll=%d\n",maxpri,maxwp->debug(1),(int)repoll);
      if( maxwp->do_poll(tick) )
        repoll = True;
      dprintf(3)("poll done: repoll=%d\n",(int)repoll);
    }
  }
  if( stop_polling )
    dprintf(2)("poll: exiting on stop_polling condition\n");
  --poll_depth;
  //## end Dispatcher::poll%3C7B888E01CF.body
}

void Dispatcher::pollLoop ()
{
  //## begin Dispatcher::pollLoop%3C8C87AF031F.body preserve=yes
  FailWhen(!running,"not running");
  FailWhen(in_pollLoop,"already in pollLoop()");
  in_pollLoop = True;
  stop_polling = False;
  rebuildSignals();
#ifdef USE_THREADS
  // multithreaded version: loop until stop_polling is raised
  // wait on the repoll_cond variable, and call poll when awoken
  Thread::Mutex::Lock lock;
  while( !stop_polling )
  {
    lock.relock(repoll_cond);
    while( !repoll && !stop_polling )
      repoll_cond.wait();
    lock.release();
    poll();
  }
#else
  // non-threaded version: loop until stop_polling is raised, while watching active fds
  while( !stop_polling )
  {
    poll();
    // pause until next heartbeat (SIGALRM), or until an fd is active
    if( max_fd >= 0 ) // use select(2) 
    {
      fds_active = fds_watched;
      num_active_fds = select(max_fd,&fds_active.r,&fds_active.w,&fds_active.x,NULL);
      // we don't expect any errors except perhaps EINTR (interrupted by signal)
      if( num_active_fds < 0 && errno != EINTR )
        dprintf(0)("select(): unexpected error %d (%s)\n",errno,strerror(errno));
      next_select = Timestamp::now() + inputs_poll_period;
    }
    else
      pause();       // use plain pause(2)
  }
#endif
  in_pollLoop = False;
  //## end Dispatcher::pollLoop%3C8C87AF031F.body
}

bool Dispatcher::yield ()
{
  //## begin Dispatcher::yield%3CE0BD3F0026.body preserve=yes
  poll();
  return !sigismember(&raisedSignals,SIGINT) && !stop_polling;
  //## end Dispatcher::yield%3CE0BD3F0026.body
}

void Dispatcher::stopPolling ()
{
  //## begin Dispatcher::stopPolling%3CA09EB503C1.body preserve=yes
  stop_polling = True;
#ifdef USE_THREADS
  Thread::Mutex::Lock lock(repoll_cond);
  repoll_cond.signal();
#endif
  //## end Dispatcher::stopPolling%3CA09EB503C1.body
}

void Dispatcher::addTimeout (WPInterface* pwp, const Timestamp &period, const HIID &id, int flags, int priority)
{
  //## begin Dispatcher::addTimeout%3C7D28C30061.body preserve=yes
  FailWhen(!period,"addTimeout: null period");
  // setup a new timeout structure
  TimeoutInfo ti(pwp,id,priority);
  ti.period = period;
  ti.next = Timestamp() + period;
  ti.flags = flags;
  ti.id = id;
  // add to list
  Thread::Mutex::Lock lock(tomutex);
  timeouts.push_front(ti);
  // check when it is to fire
  if( !next_to || ti.next < next_to )
  {
    next_to = ti.next;
#ifdef USE_THREADS
    lock.release();
    // send signal to event thread to re-do a select
    Thread::kill(event_thread,SIGUSR1);
#endif
  }
  //## end Dispatcher::addTimeout%3C7D28C30061.body
}

void Dispatcher::addInput (WPInterface* pwp, int fd, int flags, int priority)
{
  //## begin Dispatcher::addInput%3C7D28E3032E.body preserve=yes
  FailWhen(fd<0,Debug::ssprintf("addInput: invalid fd %d",fd));
  FailWhen(!(flags&EV_FDALL),"addInput: no fd flags specified");
  // check if perhaps this fd is already being watched, then we only need to 
  // add to the flags
  Thread::Mutex::Lock lock(inpmutex);
  for( IILI iter = inputs.begin(); iter != inputs.end(); iter++ )
  {
    if( iter->pwp == pwp && iter->fd == fd )
    {
      iter->flags = flags | (iter->flags&EV_FDALL);
      iter->msg().setPriority(priority);
      rebuildInputs();
      return;
    }
  }
  // else setup a new input structure
  InputInfo ii(pwp,AtomicID(fd),priority);
  ii.fd = fd;
  ii.flags = flags;
  // add to list
  inputs.push_front(ii);
  // rebuild input sets
  rebuildInputs();
  //## end Dispatcher::addInput%3C7D28E3032E.body
}

void Dispatcher::addSignal (WPInterface* pwp, int signum, int flags, int priority)
{
  //## begin Dispatcher::addSignal%3C7DFF4A0344.body preserve=yes
  FailWhen(signum<0,Debug::ssprintf("addSignal: invalid signal %d",signum));
  // look at map for this signal to see if this WP is already registered
  Thread::Mutex::Lock lock(sigmutex);
  for( SMI iter = signal_map.lower_bound(signum); 
       iter->first == signum && iter != signal_map.end(); iter++ )
  {
    if( iter->second.pwp == pwp )  // found it? change priority & return
    {
      iter->second.msg().setPriority(priority);
      return;
    }
  }
  // insert WP into map
  SignalInfo si(pwp,AtomicID(signum),priority);
  si.signum = signum;
  si.flags = flags;
  si.msg().setState(0);
  signal_map.insert( SMPair(signum,si) );
  rebuildSignals();
  //## end Dispatcher::addSignal%3C7DFF4A0344.body
}

bool Dispatcher::removeTimeout (WPInterface* pwp, const HIID &id)
{
  //## begin Dispatcher::removeTimeout%3C7D28F202F3.body preserve=yes
  Thread::Mutex::Lock lock(tomutex);
  for( TOILI iter = timeouts.begin(); iter != timeouts.end(); )
  {
    if( iter->pwp == pwp && id.matches(iter->id) )
    {
      // remove any remaining timeout messages from this queue
      if( pwp->dequeue(iter->msg->id()) )
        repoll = True;
      timeouts.erase(iter++);
      return True;
    }
    else
      iter++;
  }
  return False;
  //## end Dispatcher::removeTimeout%3C7D28F202F3.body
}

bool Dispatcher::removeInput (WPInterface* pwp, int fd, int flags)
{
  //## begin Dispatcher::removeInput%3C7D2947002F.body preserve=yes
  if( fd<0 )  // fd<0 means remove everything
    flags = ~0;
  Thread::Mutex::Lock lock(inpmutex);
  for( IILI iter = inputs.begin(); iter != inputs.end(); iter++ )
  {
    // is an input message sitting intill undelivered?
    // (WPInterface::poll() will reset its state to 0 when delivered)
    // input messages are dequeued/modified inside WorkProcess::removeInput.
    if( iter->pwp == pwp && (fd<0 || iter->fd == fd) ) 
    {   
       // is an input message sitting in the queue, undelivered? Clear its flags
      MessageRef & ref = iter->last_msg;
      if( ref.valid() && ref.isWritable() && ref->state() )
        ref().setState(ref->state()&~flags);
      // clear flags of input
      if( ( iter->flags &= ~flags ) == 0 ) // removed all modes? 
        inputs.erase(iter);
      rebuildInputs();
      return True;
    }
  }
  return False;
  //## end Dispatcher::removeInput%3C7D2947002F.body
}

bool Dispatcher::removeSignal (WPInterface* pwp, int signum)
{
  //## begin Dispatcher::removeSignal%3C7DFF57025C.body preserve=yes
  bool res = False;
  pair<SMI,SMI> rng;
  Thread::Mutex::Lock lock(sigmutex);
  // if signum<0, removes all signal_map for this WP
  if( signum<0 )
    rng = pair<SMI,SMI>(signal_map.begin(),signal_map.end()); // range = all signal_map
  else 
    rng = signal_map.equal_range(signum);  // range = this signal's entries
  // iterate over the range
  for( SMI iter = rng.first; iter != rng.second; )
  {
    if( iter->second.pwp == pwp )
    {
      signal_map.erase(iter++);
      res = True;
    }
    else
      iter++;
  }
  // remove any pending messages from WP's queue
  HIID id = AidEvent|AidSignal|AtomicID(signum);
  if( signum<0 )
    id[2] = AidWildcard;
  if( pwp->dequeue(id) )
    repoll = True;
  
  if( res )
    rebuildSignals();
  
  return res;
  //## end Dispatcher::removeSignal%3C7DFF57025C.body
}

Dispatcher::WPIter Dispatcher::initWPIter ()
{
  //## begin Dispatcher::initWPIter%3C98D4530076.body preserve=yes
  return WPIter(wps.begin(),wpmutex);
  //## end Dispatcher::initWPIter%3C98D4530076.body
}

bool Dispatcher::getWPIter (Dispatcher::WPIter &iter, WPID &wpid, const WPInterface *&pwp)
{
  //## begin Dispatcher::getWPIter%3C98D47B02B9.body preserve=yes
  if( iter.iter == wps.end() )
  {
    iter.lock.release();
    return False;
  }
  wpid = iter.iter->first;
  pwp = iter.iter->second.deref_p();
  iter.iter++;
  return True;
  //## end Dispatcher::getWPIter%3C98D47B02B9.body
}

void Dispatcher::addLocalData (const HIID &id, ObjRef ref)
{
  //## begin Dispatcher::addLocalData%3CBEDDD8001A.body preserve=yes
  FailWhen( localData_[id].exists(),id.toString()+" is already defined in local data");
  localData_[id] <<= ref;
  //## end Dispatcher::addLocalData%3CBEDDD8001A.body
}

DataField & Dispatcher::addLocalData (const HIID &id)
{
  //## begin Dispatcher::addLocalData%3CBEE41702F4.body preserve=yes
  FailWhen( localData_[id].exists(),id.toString()+" is already defined in local data");
  DataField *field = new DataField;
  localData_[id] <<= field;
  return *field;
  //## end Dispatcher::addLocalData%3CBEE41702F4.body
}

NestableContainer::Hook Dispatcher::localData (const HIID &id)
{
  //## begin Dispatcher::localData%3CC405480057.body preserve=yes
  return localData_[id];
  //## end Dispatcher::localData%3CC405480057.body
}

bool Dispatcher::hasLocalData (const HIID &id)
{
  //## begin Dispatcher::hasLocalData%3CC00549020D.body preserve=yes
  return localData_[id].exists();
  //## end Dispatcher::hasLocalData%3CC00549020D.body
}

// Additional Declarations
  //## begin Dispatcher%3C7B6A3E00A0.declarations preserve=yes
void Dispatcher::rebuildInputs (WPInterface *remove)
{
  Thread::Mutex::Lock lock(inpmutex);
  Thread::Mutex::Lock lock2(fds_watched_mutex);
  FD_ZERO(&fds_watched.r);
  FD_ZERO(&fds_watched.w);
  FD_ZERO(&fds_watched.x);
  max_fd = -1;
  for( IILI iter = inputs.begin(); iter != inputs.end(); )
  {
    if( remove && iter->pwp == remove )
      inputs.erase(iter++);
    else
    {
      if( iter->flags&EV_FDREAD )
        FD_SET(iter->fd,&fds_watched.r);
      if( iter->flags&EV_FDWRITE )
        FD_SET(iter->fd,&fds_watched.w);
      if( iter->flags&EV_FDEXCEPTION )
        FD_SET(iter->fd,&fds_watched.x);
      if( iter->fd > max_fd )
        max_fd = iter->fd;
      iter++;
    }
  }
  if( max_fd >=0 )
    max_fd++; // this is the 'n' argument to select(2)
#ifdef USE_THREADS
  // send a signal to the event thread, to re-do a select() with the new fd sets
  lock2.release();
  Thread::kill(event_thread,SIGUSR1);
#endif
}

void Dispatcher::rebuildSignals (WPInterface *remove)
{
  // rebuild mask of handled signal_map
  Thread::Mutex::Lock lock(sigmutex);
  sigset_t newmask;
  sigemptyset(&newmask);
#ifdef USE_THREADS
  // INT handled by event thread
  sigaddset(&newmask,SIGINT);  
  // USR1 handled by event thread
  sigaddset(&newmask,SIGUSR1);  
  // ALRM not handled since we use select() for pausing instead
#else
  if( running )
    sigaddset(&newmask,SIGALRM); // ALRM handled when running
  if( in_pollLoop )
    sigaddset(&newmask,SIGINT);  // INT handled in pollLoop
#endif
  int sig0 = -1;
  for( SMI iter = signal_map.begin(); iter != signal_map.end(); )
  {
    if( remove && iter->second.pwp == remove )
      signal_map.erase(iter++);
    else
    {
      if( iter->first != sig0 )
        sigaddset(&newmask,sig0=iter->first);
      iter++;
    }
  }
  // init a sigaction structure
  struct sigaction sa;
  sa.sa_handler = 0;
  sa.sa_sigaction = Dispatcher::signalHandler;
  sa.sa_mask = newmask;
  sa.sa_flags = SA_SIGINFO;
  // go thru all signal_map
  for( int sig = 0; sig < _NSIG; sig++ )
  {
    bool newsig = sigismember(&newmask,sig),
         oldsig = sigismember(&allSignals,sig);
    if( newsig && !oldsig )   // start handling signal?
    {
      Assert(!orig_sigaction[sig]);  // to store old handler
      orig_sigaction[sig] = new struct sigaction;
      sigaction(sig,&sa,orig_sigaction[sig]);
    }
    else if( !newsig && oldsig ) // stop handling?
    {
      Assert(orig_sigaction[sig]);
      sigaction(sig,0,orig_sigaction[sig]); // reset old handler
      delete orig_sigaction[sig];
      orig_sigaction[sig] = 0;
    }
  }
  allSignals = newmask;
}

bool Dispatcher::checkEvents()
{
  // ------ check timeouts
  // next_to gives us the timestamp of the nearest timeout
  Thread::Mutex::Lock wplock(wpmutex);
  Thread::Mutex::Lock lock(tomutex);
  Timestamp now;
  if( next_to && next_to <= now )
  {
    next_to.reset();
    // see which timeouts are up, and update next_to as well
    for( TOILI iter = timeouts.begin(); iter != timeouts.end(); )
    {
      if( iter->next <= now ) // this timeout has fired?
      {
        enqueue(iter->pwp, iter->msg.copy(DMI::READONLY));
        if( iter->flags&EV_ONESHOT ) // not continouos? clear it now
        {
          timeouts.erase(iter++);
          continue;
        }
        // else continous, so set the next timestamp
        iter->next = now + iter->period;
      }
      if( !next_to || iter->next < next_to )
        next_to = iter->next;
      iter++;
    }
  }
  dprintf(5)("next timeout in %.6f\n",(next_to-now).seconds());
  lock.release();
  lock.relock(inpmutex);
  // ------ check inputs
  // while in Dispatcher::pollLoop(), select() is already being done for
  // us. Check the fds otherwise
  if( !inputs.empty() && now >= next_select )
  {
    struct timeval to = {0,0}; // select will return immediately
    fds_active = fds_watched;
    num_active_fds = select(max_fd,&fds_active.r,&fds_active.w,&fds_active.x,&to);
    // we don't expect any errors except perhaps EINTR (interrupted by signal)
    if( num_active_fds < 0 && errno != EINTR )
      dprintf(0)("select(): unexpected error %d (%s)\n",errno,strerror(errno));
    next_select = now + inputs_poll_period;
  }
  if( num_active_fds>0 )
  {
    // iterate over all inputs
    for( IILI iter = inputs.begin(); iter != inputs.end(); )
    {
      // set local flags var according to state of fd
      int flags = 0;
      if( iter->flags&EV_FDREAD && FD_ISSET(iter->fd,&fds_active.r) )
        flags |= EV_FDREAD;
      if( iter->flags&EV_FDWRITE && FD_ISSET(iter->fd,&fds_active.w) )
        flags |= EV_FDWRITE;
      if( iter->flags&EV_FDEXCEPTION && FD_ISSET(iter->fd,&fds_active.x) )
        flags |= EV_FDEXCEPTION;
      // anything raised?
      if( flags )
      {
        MessageRef & ref = iter->last_msg;
        // is a previous message still undelivered?
        // (WPInterface::poll() will reset its state to 0 when delivered)
        if( ref.valid() && ref->state() != 0 )
        {
          ref().setState(ref->state()|flags); // update state
          // is this same message at the head of the queue? repoll then
          if( iter->pwp->compareHeadOfQueue(ref) )
          {
            repoll = True;     
            iter->pwp->setNeedRepoll(True);
          }
        }
        else // not found, so enqueue a message
        {
          // make a writable copy of the template message, because we set state
          ref = iter->msg.copy().privatize(DMI::WRITE);
          ref().setState(flags);
          enqueue(iter->pwp,ref.copy(DMI::WRITE));  
        }
        // if event is one-shot, clear it
        if( iter->flags&EV_ONESHOT )
        {
          inputs.erase(iter++);
          continue;
        }
      }
      iter++;
    }
    // clear active fds 
    num_active_fds = 0;
  }
  // ------ check signal_map
  lock.release();
  lock.relock(sigmutex);
  // grab & flush the current raised-mask
  sigset_t mask = raisedSignals;
  sigemptyset(&raisedSignals);
  // go through all raised signal_map
  for( int sig = 0; sig < _NSIG; sig++ )
  {
    if( sigismember(&mask,sig) ) // signal raised? See who wants it
    {
      pair<SMI,SMI> rng = signal_map.equal_range(sig);
      for( SMI iter = rng.first; iter != rng.second; )
      {
        // no message generated for EV_IGNORE
        if( !(iter->second.flags&EV_IGNORE) )
        {
          // discrete signal events requested, so always enqueue a message
          if( iter->second.flags&EV_DISCRETE )
          {
            enqueue(iter->second.pwp,iter->second.msg.copy(DMI::WRITE));
          }
          else // else see if event is already enqueued & not delivered
          {
            // is a previous message still undelivered?
            // (WPInterface::poll() will reset its state to 0 when delivered)
            if( iter->second.msg->state() )
            {
              // simply ask for a repoll if the message is at top of queue
              if( iter->second.pwp->compareHeadOfQueue(iter->second.msg) )
                iter->second.pwp->setNeedRepoll(repoll=True);
            }
            else // not in queue anymore, so enqueue a message
            {
              iter->second.msg().setState(1); // state=1 means undelivered
              enqueue(iter->second.pwp,iter->second.msg.copy(DMI::WRITE));
            }
          }
        }
        // remove signal if one-shot
        if( iter->second.flags&EV_ONESHOT )
          signal_map.erase(iter++);
        else
          iter++;
      }
    }
  }
  
  return repoll;
}

void Dispatcher::enqueue (WPInterface *pwp,const Message::Ref &ref)
{
// place the message into the WP's queue
  bool res = pwp->enqueue(ref,tick) >= 0;
#ifdef USE_THREADS
// if the WP is not in a separate thread, a repoll may be required
  if( !pwp->isThreaded() && res )
  {
    repoll = True;
    // wake up the dispatcher thread
    if( Thread::self() != main_thread )
    {
      Thread::Mutex::Lock lock(repoll_cond);
      repoll_cond.signal();
    }
  }
  return;
#else
// non-threaded version: simply raise the repoll flag if enqueue indicates
// that the WP needs a repoll
  if( res )
    repoll = True;
#endif
}

#ifdef USE_THREADS
void * Dispatcher::start_eventThread (void *pdsp)
{
  return static_cast<Dispatcher*>(pdsp)->eventThread();
}
    
void * Dispatcher::eventThread ()
{
  // no signals are blocked
  try
  {
    dprintf(1)("Entering event thread\n");
    // unblock all signals
    Thread::signalMask(SIG_UNBLOCK,validSignals());
    // wait for startup to complete
    Thread::Mutex::Lock lock(repoll_cond);
    while( in_start )
      repoll_cond.wait();
    lock.release();
    dprintf(1)("Event thread startup complete\n");
      
    // loop while still running
    while( running )
    {
      // call checkEvents() to distribute timeout/input/signal events
      dprintf(5)("Checking events\n");
      checkEvents();
      if( stop_polling )
        stopPolling();
      // pause until next timeout, or until an fd is active
      Thread::Mutex::Lock lock(tomutex);
      struct timeval tv,*ptv = &tv;
      if( next_to )
      {
        (next_to - Timestamp::now()).to_timeval(tv);
//        dprintf(5)("next TO in %ld.%06ld\n",tv.tv_sec,tv.tv_usec);
        if( tv.tv_sec < 0 ) // already time for timeout?
          ptv = 0;
      }
      else
        ptv = 0;
      lock.relock(fds_watched_mutex);
      if( max_fd >= 0 ) // poll fds using select(2) 
      {
        fds_active = fds_watched;
        lock.release();
        if( ptv )
          { dprintf(5)("select(%d,%ld:%ld)\n",max_fd,ptv->tv_sec,ptv->tv_usec); }
        else
          { dprintf(5)("select(%d,null)\n",max_fd); }
        // NB: if timeouts change, should also deliver a signal
        num_active_fds = select(max_fd,&fds_active.r,&fds_active.w,&fds_active.x,ptv);
        // we don't expect any errors except perhaps EINTR (interrupted by signal)
        dprintf(5)("select()=%d, errno=%d (%s), running=%d\n",num_active_fds,num_active_fds<0?errno:0,num_active_fds<0?strerror(errno):"",(int)running);
        if( num_active_fds < 0 && errno != EINTR )
          dprintf(0)("select(): unexpected error %d (%s)\n",errno,strerror(errno));
      }
      else  // else just use select(2) to sleep until next timeout
      {
        lock.release();
        if( ptv )
          { dprintf(5)("select(0,%ld:%ld)\n",ptv->tv_sec,ptv->tv_usec); }
        else
          { dprintf(5)("select(0,null)\n"); }
        int res = select(0,NULL,NULL,NULL,ptv);
        dprintf(5)("select()=%d, errno=%d (%s), running=%d\n",res,res<0?errno:0,res<0?strerror(errno):"",(int)running);
      }
    }
  }
  catch( std::exception exc )
  {
    cerr<<"Dipatcher event thread terminated with exception "<<exc.what()<<endl;
  }
  return 0;
}

void * Dispatcher::start_pollThread (void *pdsp)
{
  return static_cast<Dispatcher*>(pdsp)->pollThread();
}
    
void * Dispatcher::pollThread ()
{
  try
  {
    dprintf(1)("Starting poll thread\n");
    start();
    dprintf(1)("Entering poll loop in poll thread\n");
    pollLoop();
    // call stop() (unless it's already been called for us: running = False)
    Thread::Mutex::Lock lock(repoll_cond);
    if( running )
    {
      dprintf(1)("Poll loop exited, stopping and exiting\n");
      lock.release();
      stop();
    }
    else
    {
      dprintf(1)("stop() call detected, exiting\n");
    }
  }
  catch( std::exception exc )
  {
    cerr<<"Dipatcher event thread terminated with exception "<<exc.what()<<endl;
  }
  return 0;
}

Thread::ThrID Dispatcher::startThread ()
{
  // block all dispatcher-handled signals
  Thread::signalMask(SIG_BLOCK,validSignals());
  // launch a polling thread
  return Thread::create(start_pollThread,this);
}
#endif



const sigset_t * Dispatcher::validSignals ()
{
  static bool init = False;
  static sigset_t set;
  
  if( !init )
  {
    init = True;
    sigemptyset(&set);
    sigaddset(&set,SIGINT);
    sigaddset(&set,SIGALRM);
    sigaddset(&set,SIGPIPE);
    sigaddset(&set,SIGUSR1);
    sigaddset(&set,SIGUSR2);
    sigaddset(&set,SIGURG);
  }
  
  return &set;
}


string Dispatcher::sdebug ( int detail,const string &,const char *name ) const
{
  string out;
  if( detail>=0 ) // basic detail
  {
    if( name )
      out = string(name) + "/";
    out += address.toString();
    if( detail>3 )
      out += Debug::ssprintf("/%08x",this);
#ifdef USE_THREADS
    Debug::appendf(out,"T%d",(int)Thread::self());
#endif    
  }
  if( detail >= 1 || detail == -1 )   // normal detail
  {
    Debug::appendf(out,"wps:%d",wps.size());
    if( !running )
      Debug::append(out,"stopped");
  }
  return out;
}
  //## end Dispatcher%3C7B6A3E00A0.declarations
//## begin module%3C7B7F30004B.epilog preserve=yes
//## end module%3C7B7F30004B.epilog
