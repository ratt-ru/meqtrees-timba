//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C8F26A30123.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C8F26A30123.cm

//## begin module%3C8F26A30123.cp preserve=no
//## end module%3C8F26A30123.cp

//## Module: WPInterface%3C8F26A30123; Package body
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\WPInterface.cc

//## begin module%3C8F26A30123.additionalIncludes preserve=no
//## end module%3C8F26A30123.additionalIncludes

//## begin module%3C8F26A30123.includes preserve=yes
#include "OctopussyConfig.h"
//## end module%3C8F26A30123.includes

// Dispatcher
#include "OCTOPUSSY/Dispatcher.h"
// WPInterface
#include "OCTOPUSSY/WPInterface.h"
//## begin module%3C8F26A30123.declarations preserve=no
//## end module%3C8F26A30123.declarations

//## begin module%3C8F26A30123.additionalDeclarations preserve=yes
//## end module%3C8F26A30123.additionalDeclarations


// Class WPInterface 

//## begin WPInterface::logLevel%3CA07E5F00D8.attr preserve=no  public: static int {U} 2
int WPInterface::logLevel_ = 2;
//## end WPInterface::logLevel%3CA07E5F00D8.attr

WPInterface::WPInterface (AtomicID wpc)
  //## begin WPInterface::WPInterface%3C7CBB10027A.hasinit preserve=no
  //## end WPInterface::WPInterface%3C7CBB10027A.hasinit
  //## begin WPInterface::WPInterface%3C7CBB10027A.initialization preserve=yes
  : DebugContext(wpc.toString(),&OctopussyDebugContext::getDebugContext()),
    config(OctopussyConfig::global()),
    address_(wpc),running(False),autoCatch_(False),
    dsp_(0),queue_(0),wpid_(wpc)
  //## end WPInterface::WPInterface%3C7CBB10027A.initialization
{
  //## begin WPInterface::WPInterface%3C7CBB10027A.body preserve=yes
  full_lock = receive_lock = started = False;
  //## end WPInterface::WPInterface%3C7CBB10027A.body
}


WPInterface::~WPInterface()
{
  //## begin WPInterface::~WPInterface%3C7B6A3702E5_dest.body preserve=yes
  //## end WPInterface::~WPInterface%3C7B6A3702E5_dest.body
}



//## Other Operations (implementation)
void WPInterface::attach (Dispatcher* pdsp)
{
  //## begin WPInterface::attach%3C7CBAED007B.body preserve=yes
  dsp_ = pdsp;
  //## end WPInterface::attach%3C7CBAED007B.body
}

void WPInterface::do_init ()
{
  //## begin WPInterface::do_init%3C99B0070017.body preserve=yes
  setNeedRepoll(False);
  full_lock = receive_lock = started = False;
  running = True;
  if( autoCatch() )
  {
    try { 
      init(); 
    }
    catch(std::exception &exc) {
      lprintf(0,LogFatal,"caught exception in init(): %s; shutting down",exc.what());
      dsp()->detach(this,True);
    }
  }
  else  
    init();
  //## end WPInterface::do_init%3C99B0070017.body
}

bool WPInterface::do_start ()
{
  //## begin WPInterface::do_start%3C99B00B00D1.body preserve=yes
  log("starting up",2);
  MessageRef ref(new Message(MsgHello|address()),DMI::ANON|DMI::WRITE);
  publish(ref);
  if( autoCatch() )
  {
    try { 
      raiseNeedRepoll( start() );
    }
    catch(std::exception &exc) {
      lprintf(0,LogFatal,"caught exception in start(): %s; shutting down",exc.what());
      dsp()->detach(this,True);
    }
  }
  else  
    raiseNeedRepoll( start() );
  // publish subscriptions (even if empty)
  started = True;
  publishSubscriptions();
  return needRepoll();
  //## end WPInterface::do_start%3C99B00B00D1.body
}

void WPInterface::do_stop ()
{
  //## begin WPInterface::do_stop%3C99B00F0254.body preserve=yes
  log("stopping",2);
  MessageRef ref(new Message(MsgBye|address()),DMI::ANON|DMI::WRITE);
  publish(ref);
  running = False;
  if( autoCatch() )
  {
    try { 
      stop();
    }
    catch(std::exception &exc) {
      lprintf(0,LogError,"caught exception in stop(): %s; ignoring",exc.what());
    }
  }
  else  
    stop();
  //## end WPInterface::do_stop%3C99B00F0254.body
}

void WPInterface::init ()
{
  //## begin WPInterface::init%3C7F882B00E6.body preserve=yes
  //## end WPInterface::init%3C7F882B00E6.body
}

bool WPInterface::start ()
{
  //## begin WPInterface::start%3C7E4A99016B.body preserve=yes
  return False;
  //## end WPInterface::start%3C7E4A99016B.body
}

void WPInterface::stop ()
{
  //## begin WPInterface::stop%3C7E4A9C0133.body preserve=yes
  //## end WPInterface::stop%3C7E4A9C0133.body
}

int WPInterface::getPollPriority (ulong tick)
{
  //## begin WPInterface::getPollPriority%3CB55EEA032F.body preserve=yes
  // return queue priority, provided a repoll is required
  // note that we add the message age (tick - QueueEntry.tick) to its
  // priority. Thus, messages that have been sitting undelivered for a while
  // (perhaps because the system is saturated with higher-priority messages)
  // will eventually get bumped up and become favoured.
  if( needRepoll() && !queueLocked() )
  {
    const QueueEntry * qe = topOfQueue();
    if( qe )
    {
      return max(qe->priority,Message::PRI_LOWEST)
             + static_cast<int>(tick - qe->tick);
    }
  }
  return -1;
  //## end WPInterface::getPollPriority%3CB55EEA032F.body
}

bool WPInterface::do_poll (ulong tick)
{
  //## begin WPInterface::do_poll%3C8F13B903E4.body preserve=yes
  // Call the virtual poll method, and set needRepoll according to what
  // it has returned.
  if( autoCatch() )
  {
    try { 
      setNeedRepoll( poll(tick) );
    }
    catch(std::exception &exc) {
      lprintf(2,LogError,"caught exception in poll(): %s; ignoring",exc.what());
    }
  }
  else  
    setNeedRepoll( poll(tick) );
  // return if queue is empty
  if( !queue().size() )
    return needRepoll();  
  int res = Message::ACCEPT;
  // remove message from queue
  QueueEntry qe = queue().front();
  queue().pop_front();
  
  const Message &msg = qe.mref.deref();
  const HIID &id = msg.id();
  FailWhen( !id.size(),"null message ID" );
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
          lprintf(2,LogError,"caught exception in timeout(): %s; ignoring",exc.what());
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
            lprintf(2,LogError,"caught exception in input(): %s; ignoring",exc.what());
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
          lprintf(2,LogError,"caught exception in signal(): %s; ignoring",exc.what());
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
        lprintf(2,LogError,"caught exception in receive(): %s; ignoring message",exc.what());
      }
    }
    else  
      res = receive(qe.mref);
    receive_lock = False;
  }
  // dispence of queue() accordingly
  if( res == Message::ACCEPT )   // message accepted, remove from queue
  {
    dprintf(3)("result code: OK, de-queuing\n");
  }
  else      // message not accepted, stays in queue
  {
    FailWhen( !qe.mref.valid(),"message was not accepted but its ref was detached or xferred" );
    if( res == Message::HOLD )
    {
      dprintf(3)("result code: HOLD, leaving at head of queue\n");
      queue().push_front(qe);
      return needRepoll();
    }
    else if( res == Message::REQUEUE )
    {
      dprintf(3)("result code: REQUEUE\n");
      // requeue - re-insert into queue() according to priority
      enqueue(qe.mref,tick);  // this sets repoll if head of queue has changed
    }
  }
  // ask for repoll if head of queue has changed
  if( queue().size() )
  {
    // this resets the age at the head of the queue. Effectively, this means
    // we have a "queue age" rather than a message age.
    queue().front().tick = tick;
    if( queue().front().mref != qe.mref )
      return setNeedRepoll(True);
  }

  return needRepoll();
  //## end WPInterface::do_poll%3C8F13B903E4.body
}

bool WPInterface::poll (ulong )
{
  //## begin WPInterface::poll%3CB55D0E01C2.body preserve=yes
  return False;
  //## end WPInterface::poll%3CB55D0E01C2.body
}

bool WPInterface::enqueue (const MessageRef &msg, ulong tick)
{
  //## begin WPInterface::enqueue%3C8F204A01EF.body preserve=yes
  int pri = msg->priority();
  // iterate from end of queue() as long as msg priority is higher
  MQI iter = queue().begin();
  int count = 0;
  while( iter != queue().end() && iter->priority >= pri )
    iter++,count++;
  // if inserting at head of queue (which is end), then raise the repoll flag
  if( !count )
  {
    dprintf(3)("queueing [%s] at head of queue\n",msg->debug(1));
    setNeedRepoll(True);
  }
  else
    dprintf(3)("queueing [%s] at h+%d\n",msg->debug(1),count);
  QueueEntry qe = { msg,pri,tick };
  queue().insert(iter,qe);
  return needRepoll();
  //## end WPInterface::enqueue%3C8F204A01EF.body
}

bool WPInterface::dequeue (const HIID &id, MessageRef *ref)
{
  //## begin WPInterface::dequeue%3C8F204D0370.body preserve=yes
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
  return raiseNeedRepoll( erased_head && queue().size() );
  //## end WPInterface::dequeue%3C8F204D0370.body
}

bool WPInterface::dequeue (int pos, MessageRef *ref)
{
  //## begin WPInterface::dequeue%3C8F205103D0.body preserve=yes
  FailWhen( (uint)pos >= queue().size(),"dequeue: illegal position" );
  raiseNeedRepoll( !pos && queue().size()>1 );
  // iterate to the req. position
  MQI iter = queue().begin();
  while( pos-- )
    iter++;
  if( ref )
    *ref = iter->mref;
  queue().erase(iter);
  return needRepoll();
  //## end WPInterface::dequeue%3C8F205103D0.body
}

int WPInterface::searchQueue (const HIID &id, int pos, MessageRef *ref)
{
  //## begin WPInterface::searchQueue%3C8F205601EC.body preserve=yes
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
  //## end WPInterface::searchQueue%3C8F205601EC.body
}

const WPInterface::QueueEntry * WPInterface::topOfQueue () const
{
  //## begin WPInterface::topOfQueue%3C8F206C0071.body preserve=yes
  return queue().size() 
    ? &queue().front() 
    : 0;
  //## end WPInterface::topOfQueue%3C8F206C0071.body
}

bool WPInterface::queueLocked () const
{
  //## begin WPInterface::queueLocked%3C8F207902AB.body preserve=yes
  if( full_lock )
    return True;
  if( receive_lock )
  {
    const QueueEntry * qe = topOfQueue();
    if( qe && qe->mref->id()[0] != AidEvent )
      return True;
  }
  return False;
  //## end WPInterface::queueLocked%3C8F207902AB.body
}

bool WPInterface::subscribe (const HIID &id, const MsgAddress &scope)
{
  //## begin WPInterface::subscribe%3C99AB6E0187.body preserve=yes
  // If something has changed in the subs, _and_ WP has been started,
  // then re-publish the whole thing.
  // (If not yet started, then everything will be eventually published 
  // by do_start(), above)
  dprintf(2)("subscribing to %s scope %s\n",id.toString().c_str(),scope.toString().c_str());
  bool change = subscriptions.add(id,scope);
  if( change  && started )
    publishSubscriptions();
  return change;
  //## end WPInterface::subscribe%3C99AB6E0187.body
}

bool WPInterface::unsubscribe (const HIID &id)
{
  //## begin WPInterface::unsubscribe%3C7CB9C50365.body preserve=yes
  // If something has changed in the subs, _and_ WP has been started,
  // then re-publish the whole thing.
  // (If not yet started, then everything will be eventually published 
  // by do_start(), above)
  dprintf(2)("unsubscribing from %s\n",id.toString().c_str());
  bool change = subscriptions.remove(id);
  if( change && started )
    publishSubscriptions();
  return change;
  //## end WPInterface::unsubscribe%3C7CB9C50365.body
}

int WPInterface::receive (MessageRef &mref)
{
  //## begin WPInterface::receive%3C7CC0950089.body preserve=yes
  dprintf(1)("unhandled receive(%s)\n",mref->sdebug(1).c_str());
  return Message::ACCEPT;
  //## end WPInterface::receive%3C7CC0950089.body
}

int WPInterface::timeout (const HIID &id)
{
  //## begin WPInterface::timeout%3C7CC2AB02AD.body preserve=yes
  dprintf(1)("unhandled timeout(%s)\n",id.toString().c_str());
  return Message::ACCEPT;
  //## end WPInterface::timeout%3C7CC2AB02AD.body
}

int WPInterface::input (int fd, int flags)
{
  //## begin WPInterface::input%3C7CC2C40386.body preserve=yes
  dprintf(1)("unhandled input(%d,%x)\n",fd,flags);
  return Message::ACCEPT;
  //## end WPInterface::input%3C7CC2C40386.body
}

int WPInterface::signal (int signum)
{
  //## begin WPInterface::signal%3C7DFD240203.body preserve=yes
  dprintf(1)("unhandled signal(%s)\n",sys_siglist[signum]);
  return Message::ACCEPT;
  //## end WPInterface::signal%3C7DFD240203.body
}

int WPInterface::send (MessageRef msg, MsgAddress to)
{
  //## begin WPInterface::send%3C7CB9E802CF.body preserve=yes
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
  //## end WPInterface::send%3C7CB9E802CF.body
}

int WPInterface::send (const HIID &id, MsgAddress to, int priority)
{
  //## begin WPInterface::send%3CBDAD020297.body preserve=yes
  MessageRef msg( new Message(id,priority),DMI::ANON|DMI::WRITE );
  send(msg,to);
  //## end WPInterface::send%3CBDAD020297.body
}

int WPInterface::publish (MessageRef msg, int scope)
{
  //## begin WPInterface::publish%3C7CB9EB01CF.body preserve=yes
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
  //## end WPInterface::publish%3C7CB9EB01CF.body
}

int WPInterface::publish (const HIID &id, int scope, int priority)
{
  //## begin WPInterface::publish%3CBDACCC028F.body preserve=yes
  MessageRef msg( new Message(id,priority),DMI::ANON|DMI::WRITE );
  return publish(msg,scope);
  //## end WPInterface::publish%3CBDACCC028F.body
}

void WPInterface::setState (int newstate, bool delay_publish)
{
  //## begin WPInterface::setState%3CBED9EF0197.body preserve=yes
  if( state_ != newstate )
  {
    state_ = newstate;
    if( started && !delay_publish )
      publish(MsgWPState);
  }
  //## end WPInterface::setState%3CBED9EF0197.body
}

void WPInterface::log (string str, int level, AtomicID type)
{
  //## begin WPInterface::log%3CA0457F01BD.body preserve=yes
  if( level > logLevel() )
    return;
  // see if type override was specified in the string
  const char * stypes[] = { "warning:", "error:", "fatal:", "debug:", "normal:" };
  const AtomicID types[] = { LogWarning,LogError,LogFatal,LogDebug,LogNormal };
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
    if( type == LogWarning )
      tps = stypes[0];
    else if( type == LogError )
      tps = stypes[1];
    Debug::dbg_stream<<sdebug(1)<<":"<<tps<<" "<<str;
    if( str[str.length()-1] != '\n' )
      Debug::dbg_stream<<endl;
  }
  // publish as MsgLog
  SmartBlock *bl = new SmartBlock(str.length());
  str.copy(static_cast<char*>(bl->data()),str.length());
  MessageRef mref(
      new Message(MsgLog|type|level,bl,DMI::ANON),
      DMI::ANON|DMI::WRITE);
  publish(mref);
  //## end WPInterface::log%3CA0457F01BD.body
}

void WPInterface::lprintf (int level, int type, const char *format, ... )
{
  //## begin WPInterface::lprintf%3CA0738D007F.body preserve=yes
  if( level > logLevel() )
    return;
  // create the string
  char str[1024];
  va_list(ap);
  va_start(ap,format);
  vsnprintf(str,sizeof(str),format,ap);
  va_end(ap);
  log(str,level,type);
  //## end WPInterface::lprintf%3CA0738D007F.body
}

void WPInterface::lprintf (int level, const char *format, ... )
{
  //## begin WPInterface::lprintf%3CA0739F0247.body preserve=yes
  if( level > logLevel() )
    return;
  char str[1024];
  va_list(ap);
  va_start(ap,format);
  vsnprintf(str,sizeof(str),format,ap);
  va_end(ap);
  log(str,level,LogNormal);
  //## end WPInterface::lprintf%3CA0739F0247.body
}

// Additional Declarations
  //## begin WPInterface%3C7B6A3702E5.declarations preserve=yes

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
    Debug::appendf(out,"Q:%d",queue().size());
  }
  if( detail >= 1 || detail == -1 )   // normal detail
  {
    Debug::appendf(out,"st:%d",state_);
  }
  return out;
}
  //## end WPInterface%3C7B6A3702E5.declarations
//## begin module%3C8F26A30123.epilog preserve=yes
//## end module%3C8F26A30123.epilog


// Detached code regions:
#if 0
//## begin WPInterface::subscribe%3C7CB9B70120.body preserve=yes
  subscribe(id,MsgAddress(
      AidAny,AidAny,
      scope < Message::PROCESS ? address().process() : AidAny,
      scope < Message::GLOBAL ?  address().host() : AidAny));
//## end WPInterface::subscribe%3C7CB9B70120.body

//## begin WPInterface::publish%3C99BFA502B0.body preserve=yes
  FailWhen( !isAttached(),"unattached wp");
  // if not writable, privatize for writing (but not deeply)
  if( !msg.isWritable() )
    msg.privatize(DMI::WRITE);
  msg().setFrom(address());
  msg().setState(state());
  dprintf(2)("publish [%s] scope %d\n",msg->sdebug(1).c_str(),scope);
  AtomicID host = (scope < Message::GLOBAL) ? dsp()->hostId() : AidAny;
  AtomicID process = (scope < Message::HOST) ? dsp()->processId() : AidAny;
  return dsp()->send(msg,MsgAddress(AidPublish,AidPublish,process,host));
//## end WPInterface::publish%3C99BFA502B0.body

//## begin WPInterface::subscribesTo%3C8F14310315.body preserve=yes
  // determine minimum subscription scope
  int minscope = Message::PROCESS;
  if( msg.from().process() != address().process() )
    minscope = Message::HOST;
  if( msg.from().host() != address().host() )
    minscope = Message::GLOBAL;
  // look thru map
  for( CSSI iter = subs.begin(); iter != subs.end(); iter++ )
    if( iter->first.matches(msg.id()) && iter->second >= minscope )
      return True;
  return False;
//## end WPInterface::subscribesTo%3C8F14310315.body

//## begin WPInterface::initSubsIterator%3C98D8090048.body preserve=yes
  return subs.begin();
//## end WPInterface::initSubsIterator%3C98D8090048.body

//## begin WPInterface::iterateSubs%3C98D81C0077.body preserve=yes
  if( iter == 
//## end WPInterface::iterateSubs%3C98D81C0077.body

//## begin WPInterface::wpclass%3C905E8B000E.body preserve=yes
  // default wp class is 0
  return 0;
//## end WPInterface::wpclass%3C905E8B000E.body

#endif
