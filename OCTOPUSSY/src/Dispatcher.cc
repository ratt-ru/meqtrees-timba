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
      
// static signal handler
void Dispatcher::signalHandler (int signum,siginfo_t *,void *)
{
  sigaddset(&raisedSignals,signum);
  // if this signal is in the maps, increment its counters
  pair<CSMI,CSMI> rng = dispatcher->signals.equal_range(signum);
  for( CSMI iter = rng.first; iter != rng.second; iter++ )
    if( iter->second.counter )
      (*iter->second.counter)++;
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
    wps[wpid] = wpref;
    if( running )
    {
      wp.do_init();
      repoll |= wp.do_start();
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
  WPI iter = wps.find(id); 
  FailWhen( iter == wps.end(),
      "wpid '"+id.toString()+"' is not attached to this dispatcher");
  WPInterface *pwp = iter->second;
  pwp->do_stop();
  // remove all events associated with this WP
  for( TOILI iter = timeouts.begin(); iter != timeouts.end(); )
    if( iter->pwp == pwp )
      timeouts.erase(iter++);
    else
      iter++;
  rebuildInputs(pwp);
  rebuildSignals(pwp);
  // if asked to delay, then move WP ref to delay stack, it will be
  // detached later in poll()
  if( delay )   
    detached_wps.push(iter->second);
  wps.erase(iter);
  GWI iter2 = gateways.find(id);
  if( iter2 != gateways.end() )
    gateways.erase(iter2);
  //## end Dispatcher::detach%3C8CDE320231.body
}

void Dispatcher::declareForwarder (WPInterface *wp)
{
  //## begin Dispatcher::declareForwarder%3C95C73F022A.body preserve=yes
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
  // setup signal handler for SIGALRM
  sigemptyset(&raisedSignals);
  rebuildSignals();
  num_active_fds = 0;
  rebuildInputs();
  // setup heartbeat timer
  long period_usec = 1000000/heartbeat_hz;
  // when stuck in a poll loop, do a select() at least this often:
  inputs_poll_period = Timestamp(0,period_usec/2);
  next_select = Timestamp::now();
  //  start the timer
  struct itimerval tval = { {0,period_usec},{0,period_usec} };
  setitimer(ITIMER_REAL,&tval,0);
  // say start to all WPs
  dprintf(2)("start: starting WPs\n");
  for( WPI iter = wps.begin(); iter != wps.end(); iter++ )
    repoll |= iter->second().do_start();
  in_start = False;
  // if someone has launched any new WPs already, start them now
  if( attached_wps.size() )
  {
    dprintf(2)("start: initializing %d dynamically-added WPs\n",attached_wps.size());
    while( attached_wps.size() )
    {
      WPRef &ref = attached_wps.top();
      ref().do_init();
      repoll |= ref().do_start();
      wps[ref->wpid()] = ref;
      attached_wps.pop();
    }
  }
  dprintf(2)("start: complete\n");
  //## end Dispatcher::start%3C7DFF770140.body
}

void Dispatcher::stop ()
{
  //## begin Dispatcher::stop%3C7E0270027B.body preserve=yes
  running = False;
  dprintf(1)("stopping\n");
  // stop the heartbeat timer
  struct itimerval tval = { {0,0},{0,0} };
  setitimer(ITIMER_REAL,&tval,0);
  // tell all WPs that we are stopping
  for( WPI iter = wps.begin(); iter != wps.end(); iter++ )
    iter->second().do_stop();
  // clear all event lists
  timeouts.clear();
  inputs.clear();
  signals.clear();
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
  // set the message to-address
  msg.setTo(to);
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
        repoll |= iter->second().enqueue(mref.copy(),tick);
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
        repoll |= iter->second().enqueue(mref.copy(),tick);
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
        repoll |= iter->second->enqueue(mref.copy(),tick);
        ndeliver++;
      }
  }
  if( !ndeliver )
    dprintf(2)("not delivered anywhere\n");
  return ndeliver;
  //## end Dispatcher::send%3C7B8867015B.body
}

void Dispatcher::poll ()
{
  //## begin Dispatcher::poll%3C7B888E01CF.body preserve=yes
  if( Debug(11) )
  {
    static Timestamp last_poll;
    Timestamp now;
    Timestamp elapsed = now - last_poll;
    dprintf(11)("entering poll() after %ld.%03ld ms\n",
                elapsed.sec()*1000+elapsed.usec()/1000,elapsed.usec()%1000);
    last_poll = now;
  }
  FailWhen(!running,"not running");
  // destroy all delay-detached WPs
  if( !++poll_depth )
    while( detached_wps.size() )
      detached_wps.pop();
  // main polling loop
  while( !stop_polling && ( checkEvents() || repoll ) )
  {
    tick++;
    // find max priority queue
    int maxpri = -1;
    WPInterface *maxwp = 0;
    int num_repoll = 0; // # of WPs needing a repoll
    // Find WP with maximum polling priority
    // Count the number of WPs that required polling, too
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
    // if more than 1 WP needs a repoll, force another loop
    repoll = ( num_repoll > 1 );
    // deliver message, if a queue was found
    if( maxwp )
    {
      dprintf(3)("poll: max priority %d in %s, repoll=%d\n",maxpri,maxwp->debug(1),(int)repoll);
      repoll |= maxwp->do_poll(tick);
    }
  }
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
  // loop until a SIGINT
  while( !sigismember(&raisedSignals,SIGINT) && !stop_polling )
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
  in_pollLoop = False;
  //## end Dispatcher::pollLoop%3C8C87AF031F.body
}

void Dispatcher::stopPolling ()
{
  //## begin Dispatcher::stopPolling%3CA09EB503C1.body preserve=yes
  stop_polling = True;
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
  if( !next_to || ti.next < next_to )
    next_to = ti.next;
  ti.flags = flags;
  ti.id = id;
  // add to list
  timeouts.push_front(ti);
  //## end Dispatcher::addTimeout%3C7D28C30061.body
}

void Dispatcher::addInput (WPInterface* pwp, int fd, int flags, int priority)
{
  //## begin Dispatcher::addInput%3C7D28E3032E.body preserve=yes
  FailWhen(fd<0,Debug::ssprintf("addInput: invalid fd %d",fd));
  FailWhen(!(flags&EV_FDALL),"addInput: no fd flags specified");
  // check if perhaps this fd is already being watched, then we only need to 
  // add to the flags
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

void Dispatcher::addSignal (WPInterface* pwp, int signum, int flags, volatile int* counter, int priority)
{
  //## begin Dispatcher::addSignal%3C7DFF4A0344.body preserve=yes
  FailWhen(signum<0,Debug::ssprintf("addSignal: invalid signal %d",signum));
   // look at map for this signal to see if this WP is already registered
  for( SMI iter = signals.lower_bound(signum); 
       iter->first == signum && iter != signals.end(); iter++ )
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
  si.counter = counter;
  si.msg().setState(0);
  signals.insert( SMPair(signum,si) );
  rebuildSignals();
  //## end Dispatcher::addSignal%3C7DFF4A0344.body
}

bool Dispatcher::removeTimeout (WPInterface* pwp, const HIID &id)
{
  //## begin Dispatcher::removeTimeout%3C7D28F202F3.body preserve=yes
  for( TOILI iter = timeouts.begin(); iter != timeouts.end(); )
  {
    if( iter->pwp == pwp && id.matches(iter->id) )
    {
      // remove any remaining timeout messages from this queue
      repoll |= pwp->dequeue(iter->msg->id());
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
  // if signum<0, removes all signals for this WP
  if( signum<0 )
    rng = pair<SMI,SMI>(signals.begin(),signals.end()); // range = all signals
  else 
    rng = signals.equal_range(signum);  // range = this signal's entries
  // iterate over the range
  for( SMI iter = rng.first; iter != rng.second; )
  {
    if( iter->second.pwp == pwp )
    {
      signals.erase(iter++);
      res = True;
    }
    else
      iter++;
  }
  // remove any pending messages from WP's queue
  HIID id = AidEvent|AidSignal|AtomicID(signum);
  if( signum<0 )
    id[2] = AidWildcard;
  repoll |= pwp->dequeue(id);
  
  if( res )
    rebuildSignals();
  
  return res;
  //## end Dispatcher::removeSignal%3C7DFF57025C.body
}

Dispatcher::WPIter Dispatcher::initWPIter ()
{
  //## begin Dispatcher::initWPIter%3C98D4530076.body preserve=yes
  return wps.begin();
  //## end Dispatcher::initWPIter%3C98D4530076.body
}

bool Dispatcher::getWPIter (Dispatcher::WPIter &iter, WPID &wpid, const WPInterface *&pwp)
{
  //## begin Dispatcher::getWPIter%3C98D47B02B9.body preserve=yes
  if( iter == wps.end() )
    return False;
  wpid = iter->first;
  pwp = iter->second.deref_p();
  iter++;
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
}

void Dispatcher::rebuildSignals (WPInterface *remove)
{
  // rebuild mask of handled signals
  sigset_t newmask;
  sigemptyset(&newmask);
  if( running )
    sigaddset(&newmask,SIGALRM); // ALRM handled when running
  if( in_pollLoop )
    sigaddset(&newmask,SIGINT);  // INT handled in pollLoop
  int sig0 = -1;
  for( SMI iter = signals.begin(); iter != signals.end(); )
  {
    if( remove && iter->second.pwp == remove )
      signals.erase(iter++);
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
  // go thru all signals
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
  Timestamp now;
  if( next_to && next_to <= now )
  {
    next_to = 0;
    // see which timeouts are up, and update next_to as well
    for( TOILI iter = timeouts.begin(); iter != timeouts.end(); )
    {
      if( iter->next <= now ) // this timeout has fired?
      {
        repoll |= iter->pwp->enqueue( iter->msg.copy(DMI::READONLY),tick );
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
  // ------ check inputs
  // while in Dispatcher::pollLoop(), select() is already being done for
  // us. Check the fds otherwise
  if( inputs.size() && now >= next_select )
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
          const WPInterface::QueueEntry *qe = iter->pwp->topOfQueue();
          if( qe && qe->mref == ref )
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
          repoll |= iter->pwp->enqueue(ref.copy(DMI::WRITE),tick);  
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
  // ------ check signals
  // grab & flush the current raised-mask
  sigset_t mask = raisedSignals;
  sigemptyset(&raisedSignals);
  // go through all raised signals
  for( int sig = 0; sig < _NSIG; sig++ )
  {
    if( sigismember(&mask,sig) ) // signal raised? See who wants it
    {
      pair<SMI,SMI> rng = signals.equal_range(sig);
      for( SMI iter = rng.first; iter != rng.second; )
      {
        // no message generated for EV_IGNORE
        if( !(iter->second.flags&EV_IGNORE) )
        {
          // discrete signal events requested, so always enqueue a message
          if( iter->second.flags&EV_DISCRETE )
          {
            repoll |= iter->second.pwp->enqueue(iter->second.msg.copy(DMI::WRITE),tick);
          }
          else // else see if event is already enqueued & not delivered
          {
            // is a previous message still undelivered?
            // (WPInterface::poll() will reset its state to 0 when delivered)
            if( iter->second.msg->state() )
            {
              // simply ask for a repoll if the message is at top of queue
              const WPInterface::QueueEntry *qe = iter->second.pwp->topOfQueue();
              if( qe && qe->mref == iter->second.msg )
                iter->second.pwp->setNeedRepoll(repoll=True);
            }
            else // not in queue anymore, so enqueue a message
            {
              iter->second.msg().setState(1); // state=1 means undelivered
              repoll |= iter->second.pwp->enqueue(iter->second.msg.copy(DMI::WRITE),tick);
            }
          }
        }
        // remove signal if one-shot
        if( iter->second.flags&EV_ONESHOT )
          signals.erase(iter++);
        else
          iter++;
      }
    }
  }
  
  return repoll;
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
