//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C90BFDD0240.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C90BFDD0240.cm

//## begin module%3C90BFDD0240.cp preserve=no
//## end module%3C90BFDD0240.cp

//## Module: MTGatewayWP%3C90BFDD0240; Package body
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\MTGatewayWP.cc

//## begin module%3C90BFDD0240.additionalIncludes preserve=no
//## end module%3C90BFDD0240.additionalIncludes

//## begin module%3C90BFDD0240.includes preserve=yes
#ifdef USE_THREADS

#include "Gateways.h"
#include <deque>
//## end module%3C90BFDD0240.includes

// MTGatewayWP
#include "OCTOPUSSY/MTGatewayWP.h"
//## begin module%3C90BFDD0240.declarations preserve=no
//## end module%3C90BFDD0240.declarations

//## begin module%3C90BFDD0240.additionalDeclarations preserve=yes

// use large timeouts because we're not multithreaded anymore
const Timeval to_init(30.0),
              to_write(30.0),
              to_heartbeat(5.0);
              
// all packet headers must start with this signature
//##ModelId=3DB958F402A7
const char * MTGatewayWP::PacketSignature = "oMs";
    
//##ModelId=3DB958F403D0
//##ModelId=3DB958F6017C
//##ModelId=3DB958F6017E
//## end module%3C90BFDD0240.additionalDeclarations


// Class MTGatewayWP 

MTGatewayWP::MTGatewayWP (Socket* sk)
  //## begin MTGatewayWP::MTGatewayWP%3C95C53D00AE.hasinit preserve=no
  //## end MTGatewayWP::MTGatewayWP%3C95C53D00AE.hasinit
  //## begin MTGatewayWP::MTGatewayWP%3C95C53D00AE.initialization preserve=yes
  : WorkProcess(AidGatewayWP),sock(sk)
  //## end MTGatewayWP::MTGatewayWP%3C95C53D00AE.initialization
{
  //## begin MTGatewayWP::MTGatewayWP%3C95C53D00AE.body preserve=yes
#ifndef USE_THREADS
  Throw("MTGatewayWP not compiled for thread support");
#endif
  dprintf(2)("constructor\n");
  setState(0);
  setPeerState(INITIALIZING);
  peerlist = 0;
  rprocess = rhost = 0;
  reading_socket = first_message_read = False;
  shutdown_done = False;
  statmon.time_not_reading.reset();
  //## end MTGatewayWP::MTGatewayWP%3C95C53D00AE.body
}


//##ModelId=3DB958F5004C
MTGatewayWP::~MTGatewayWP()
{
  //## begin MTGatewayWP::~MTGatewayWP%3C90BEF001E5_dest.body preserve=yes
  dprintf(2)("destructor\n");
  if( sock )
    delete sock;
  //## end MTGatewayWP::~MTGatewayWP%3C90BEF001E5_dest.body
}



//##ModelId=3DB958F5004D
//## Other Operations (implementation)
void MTGatewayWP::init ()
{
  //## begin MTGatewayWP::init%3CC9500602CC.body preserve=yes
  dprintf(2)("init\n");
  // subscribe to local subscribe notifications and Bye messages
  // (they will be forwarded to peer as-is)
  subscribe(MsgSubscribe|AidWildcard,Message::LOCAL);
  subscribe(MsgBye|AidWildcard,Message::LOCAL);
  //## end MTGatewayWP::init%3CC9500602CC.body
}

//##ModelId=3DB958F5004F
bool MTGatewayWP::start ()
{
  //## begin MTGatewayWP::start%3C90BF460080.body preserve=yes
  dprintf(2)("start\n");
  WorkProcess::start();
  dprintf(5)("start: getting peer list\n");
  // this must exist by now (client GWs are always started!)
  ObjRef plref = dsp()->localData(GWPeerList)[0].ref(DMI::WRITE);
  peerlist = dynamic_cast<DataRecord*>(plref.dewr_p());
  FailWhen(!peerlist,"Local peer-list does not seem to be a DataRecord");
  
  dprintf(5)("start: adding signal handlers\n");
  // handle & ignore SIGURG -- out-of-band data on socket. 
  // addInput() will catch an exception on the fd anyway
  addSignal(SIGURG,EV_IGNORE);
  // ignore SIGPIPE
  addSignal(SIGPIPE,EV_IGNORE);
  
  dprintf(5)("start: generating init message: getting WP iterator\n");
  // collect local subscriptions data and send it to peer
  // iterate over all WPs to find total size of all subscriptions
  size_t nwp = 0, datasize = 0;
  Dispatcher::WPIter iter = dsp()->initWPIter();
  WPID id;
  const WPInterface *pwp;
  
  while( dsp()->getWPIter(iter,id,pwp) )
  {
    dprintf(9)("start: generating init message: iterating\n");
    if( id.wpclass() != AidGatewayWP ) // ignore gateway WPs
    {
      nwp++;
      datasize += pwp->getSubscriptions().packSize() + pwp->address().packSize();
    }
  }
  iter.release();
  dprintf(5)("start: released iterator\n");
  size_t hdrsize = (1+2*nwp)*sizeof(size_t);
  // form block containing addresses and subscriptions
  SmartBlock *block = new SmartBlock(hdrsize+datasize);
  BlockRef blockref(block,DMI::ANON);
  size_t *hdr = static_cast<size_t*>(block->data());
  char *data  = static_cast<char*>(block->data()) + hdrsize;
  *(hdr++) = nwp;
  dprintf(5)("start: generating init message: getting WP iterator, pass two\n");
  iter = dsp()->initWPIter();
  while( dsp()->getWPIter(iter,id,pwp) )
  {
    dprintf(9)("start: generating init message: iterating\n");
    if( id.wpclass() != AidGatewayWP ) // ignore gateway WPs
    {
      data += *(hdr++) = pwp->address().pack(data,datasize);
      data += *(hdr++) = pwp->getSubscriptions().pack(data,datasize);
    }
  }
  iter.release();
  dprintf(5)("start: released iterator\n");
  Assert( !datasize );
  dprintf(1)("generating init message for %d subscriptions, block size %d\n",
      nwp,hdrsize+datasize);
  // put this block into a message and send it to peer
  initmsg <<= new Message(AidSubscriptions,blockref);
  initmsg().setFrom(address());
  initmsg()[AidPeers] = plref.copy(DMI::READONLY);
  initmsg_sent = False;
  
//  dprintf(5)("start: prepareMessage\n");
//  prepareMessage(msg);
  
  // init timeouts
  dprintf(5)("start: setting timeouts\n");
  addTimeout(to_init,AidInit,EV_ONESHOT);
  addTimeout(to_heartbeat,AidHeartbeat,EV_CONT);
  
  // init the status counters
  statmon.counter = 0;
  statmon.read = statmon.written = 0;
  statmon.ts = Timestamp::now();
  
  write_seq = 0;
  writing = False;
  
  sock->setBlocking(True);
  
  // spawn worker threads (for writing)
  for( int i=0; i<NumWriterThreads; i++ )
  {
    Thread::ThrID tid = createWorker();
    dprintf(0)("created worker thread %d\n",(int)tid);
  }
  
  // spawn several reader threads
  for( int i=0; i<NumReaderThreads; i++ )
  {
    reader_threads[i] = Thread::create(start_readerThread,this);
    FailWhen(!reader_threads[i],"failed to create reader thread");
    dprintf(0)("created reader thread %d\n",(int)reader_threads[i]);
  }
  
  return False;
  //## end MTGatewayWP::start%3C90BF460080.body
}

//##ModelId=3DB958F50051
void MTGatewayWP::stop ()
{
  //## begin MTGatewayWP::stop%3C90BF4A039D.body preserve=yes
  dprintf(4)("stop\n");
  shutdown();
  if( sock )
    delete sock;
  sock = 0;
  //## end MTGatewayWP::stop%3C90BF4A039D.body
}

//##ModelId=3DB958F50053
bool MTGatewayWP::willForward (const Message &msg) const
{
  //## begin MTGatewayWP::willForward%3C90BF5C001E.body preserve=yes
  if( peerState() != CONNECTED )
    return False;
  // We're doing a simple everybody-connects-to-everybody topology.
  // This determines the logic below:
  dprintf(3)("willForward(%s)",msg.sdebug(1).c_str());
  // Normally, messages will only be forwarded once (i.e, only
  // when hopcount=0).
  // GwServerBound are the exception: they're forwarded up to three times.
  // This insures that when, e.g, the following link ("=") is established:
  //    A1\       /B1
  //       A0 = B0
  //    A2/       \B2
  // ... A1/A2/B1/B2 can quickly learn about each other's server ports.
  if( msg.id().matches(MsgGWServerOpen|AidWildcard) )
  {
    if( msg.forwarder() == address() )
    {
      dprintf(3)("no, we were the forwarder\n");
      return False;
    }
    if( msg.hops() > 3 )
    {
      dprintf(3)("no, hopcount = %d\n",msg.hops() );
      return False;
    }
  }
  else if( msg.hops() > 0 )
  {
    dprintf(3)("no, non-local origin, hopcount = %d\n",msg.hops() );
    return False;
  }
  // Check that to-scope of message matches remote 
  if( !rprocess.matches( msg.to().process() ) ||
      !rhost.matches( msg.to().host() ) )
  {
    dprintf(3)("no, `to' does not match remote %s.%s\n",
               rprocess.toString().c_str(),rhost.toString().c_str());
    return False;
  }
  // if message is published, search thru remote subscriptions
  Thread::Mutex::Lock lock(remote_subs_mutex);
  if( msg.to().wpclass() == AidPublish )
  {
    for( CRSI iter = remote_subs.begin(); iter != remote_subs.end(); iter++ )
      if( iter->second.matches(msg) )
      {
        dprintf(3)("yes, subscribed to by remote %s\n",iter->first.toString().c_str());
        return True;
      }
    dprintf(3)("no, no remote subscribers\n");
  }
  else // else check for match with a remote address
  {
    for( CRSI iter = remote_subs.begin(); iter != remote_subs.end(); iter++ )
      if( iter->first.matches(msg.to()) )
      {
        dprintf(3)("yes, `to' address matches remote %s\n",
            iter->first.toString().c_str());
        return True;
      }
    dprintf(3)("no, no matching remote WPs\n");
  }
  return False;
  //## end MTGatewayWP::willForward%3C90BF5C001E.body
}

//##ModelId=3DB958F500B8
int MTGatewayWP::receive (MessageRef& mref)
{
  //## begin MTGatewayWP::receive%3C90BF63005A.body preserve=yes
  // hold off while still initializing the connection
  if( peerState() == INITIALIZING )
    return Message::HOLD;
  // else ignore if not connected
  else if( peerState() != CONNECTED )
    return Message::ACCEPT;
  
  // ignore any messages out of the remote's scope
  if( !rprocess.matches(mref->to().process()) ||
      !rhost.matches(mref->to().host()) )
  {
    dprintf(3)("ignoring [%s]: does not match remote process/host\n",mref->sdebug(1).c_str());
    return Message::ACCEPT;
  }
  // ignore any messages from MTGatewayWPs, with the exception of Remote.Up
  if( mref->from().wpclass() == AidGatewayWP &&
      !mref->id().matches(MsgGWRemoteUp) )
  {
    dprintf(3)("ignoring [%s]: from a gateway\n",mref->sdebug(1).c_str());
    return Message::ACCEPT;
  }
  
  // start transmitting the message
  transmitMessage(mref);
  
  return Message::ACCEPT;
  //## end MTGatewayWP::receive%3C90BF63005A.body
}

//##ModelId=3DB958F5011C
int MTGatewayWP::timeout (const HIID &id)
{
  //## begin MTGatewayWP::timeout%3C90BF6702C3.body preserve=yes
  if( id == AidInit )  // connection timeout
  { 
    if( peerState() == INITIALIZING )
    {
      lprintf(1,"error: timed out waiting for init message from peer\n");
      shutdown();
    }
    return Message::CANCEL;
  }
  else if( id == AidHeartbeat )  // heartbeat 
  {
    // check that write is not blocked
    if( writing && Timestamp::now() - write_timestamp >= to_write )
    {
      lprintf(1,LogError,"timed out waiting for write()\n");
      shutdown();
    }
    // report on status
    Thread::Mutex::Lock lock(statmon.stat_mutex);
    if( (statmon.counter++)%4 == 0 )
    {
      Thread::Mutex::Lock lock2(statmon.read_mutex);
      Thread::Mutex::Lock lock3(statmon.write_mutex);
      double now = Timestamp::now(), d = now - statmon.ts,
        nr = statmon.time_not_reading;
      statmon.time_not_reading.reset();
      lprintf(2,"%.2f seconds elapsed since last stats report\n"
                 "read %llu bytes (%.3f MB/s)\n"
                 "wrote %llu bytes (%.3f MB/s)\n"
                 "not reading for %.3f ms (%.2f%%)\n",
                 d,statmon.read,statmon.read/(1024*1024*d),
                 statmon.written,statmon.written/(1024*1024*d),
                 nr*1000,nr/d*100);
      statmon.ts = now;
      statmon.read = statmon.written = 0;
    }
  }
  return Message::ACCEPT;
  //## end MTGatewayWP::timeout%3C90BF6702C3.body
}

// Additional Declarations
//##ModelId=3DB958F50385
  //## begin MTGatewayWP%3C90BEF001E5.declarations preserve=yes
void MTGatewayWP::processIncoming (MessageRef &ref)
{
  Message &msg = ref;
  msg.setForwarder(address());
  msg.addHop(); // increment message hop-count
  dprintf(5)("received from remote [%s]\n",msg.sdebug(1).c_str());
// if connected, it is a true remote message, so send it off
  if( peerState() == CONNECTED )
  {
    // Bye message from remote: drop WP from routing table
    if( msg.id().prefixedBy(MsgBye) )
    {
      Thread::Mutex::Lock lock(remote_subs_mutex);
      RSI iter = remote_subs.find(msg.from());
      if( iter == remote_subs.end() )
        lprintf(1,"warning: got Bye [%s] from unknown remote WP\n",msg.sdebug(1).c_str());
      else
      {
        dprintf(2)("got Bye [%s], deleting routing entry\n",msg.sdebug(1).c_str());
        remote_subs.erase(iter);
      }
    } 
    // Subscribe message from remote: update table
    else if( msg.id().prefixedBy(MsgSubscribe) )
    {
      // unpack subscriptions block, catching any exceptions
      Subscriptions subs;
      bool success = False;
      if( msg.data() )
      {
        try {
          subs.unpack(msg.data(),msg.datasize());
          success = True;
        } catch( std::exception &exc ) {
          lprintf(2,"warning: failed to unpack Subscribe message: %s\n",exc.what());
        }
      }
      if( success )
      {
        dprintf(2)("got Subscriptions [%s]: %d subscriptions\n",
                    msg.sdebug(1).c_str(),subs.size());
        Thread::Mutex::Lock lock(remote_subs_mutex);
        RSI iter = remote_subs.find(msg.from());
        if( iter == remote_subs.end() )
        {
          dprintf(2)("inserting new entry into routing table\n");
          remote_subs[msg.from()] = subs;
        }
        else
        {
          dprintf(2)("updating entry in routing table\n");
          iter->second = subs;
        }
      }
      else
      {
        lprintf(2,"warning: ignoring bad Subscriptions message [%s]\n",msg.sdebug(1).c_str());
      }
    }
    // send the message on, regardless of the above
    // (call Dispatcher directly in order to bypass WPInterface::send,
    // thus retaining the original from address and hopcount)
    dsp()->send(ref,msg.to());
  }
// if initializing, then it must be a Subscriptions message from peer
// (see start(), above)
  else if( peerState() == INITIALIZING ) 
  {
    dprintf(1)("received init message from peer: %s\n",msg.sdebug(1).c_str());
    if( msg.id() != HIID(AidSubscriptions) )
    {
      lprintf(1,"error: unexpected init message\n");
      shutdown();
      return;
    }
    // catch all exceptions during processing of init message
    try 
    {
      // remote peer process/host id
      rprocess = msg.from().process();
      rhost = msg.from().host();
      HIID peerid(rprocess|rhost);
      // lock the peerlist so only one gateway at a time can update it
      Thread::Mutex::Lock peerlock((*peerlist).mutex());
      // paranoid case: if we already have a connection to the peer, shutdown
      // (this really ought not to happen)
      if( (*peerlist)[peerid].exists() )
      {
        lprintf(1,LogError,"already connected to %s (%s:%d %s), closing gateway",
              peerid.toString().c_str(),
             (*peerlist)[peerid][AidHost].as_string().c_str(),
             (*peerlist)[peerid][AidPort].as_int(),
             (*peerlist)[peerid][AidTimestamp].as_Timestamp().toString("%T").c_str());
        Message *msg1 = new Message(MsgGWRemoteDuplicate|peerid);
        MessageRef mref1; mref1 <<= msg1;
        (*msg1)[AidHost] = sock->host();
        (*msg1)[AidPort] = atoi(sock->port().c_str());
        publish(mref1,0,Message::LOCAL);
        setPeerState(CLOSING);
        shutdown();
        return;
      }
      // add this connection to the local peerlist
      DataRecord *rec = new DataRecord;
      (*peerlist)[peerid] <<= rec;
      (*rec)[AidTimestamp] = Timestamp::now();
      (*rec)[AidHost] = sock->host();
      (*rec)[AidPort] = atoi(sock->port().c_str());
      peerlock.release();
      
      // process remote subscriptions data
      int nsubs = processInitMessage(msg.data(),msg.datasize());
      // set states
      setPeerState(CONNECTED);
      // we can now wake up & repoll a worker thread since they can
      // now receive messages
      repollWorker();
      
      lprintf(2,("connected to remote peer " + msg.from().toString() +
                " and initialized routing for %d remote WPs\n").c_str(),nsubs);
      
      // re-publish the init message as Remote.Up 
      msg.setId(MsgGWRemoteUp|peerid);
      msg[AidHost] = sock->host();
      msg[AidPort] = atoi(sock->port().c_str());
      publish(ref,Message::GLOBAL);
    }
    catch( std::exception &exc ) 
    {
      lprintf(1,"error: processing init message: %s\n",exc.what());
      shutdown();
      return;
    }
    // publish (locally only) fake Hello messages on behalf of all remote WPs
    // to avoid deadlock, we first generate a list of messages, then send them
    // off once the remote_subs mutex has been released
    deque<MessageRef> hellos;
    Thread::Mutex::Lock subslock(remote_subs_mutex);
    for( CRSI iter = remote_subs.begin(); iter != remote_subs.end(); iter++ )
    {
      hellos.push_back(MessageRef());
      Message *msg = new Message(MsgHello|iter->first);
      hellos.back() <<= msg;
      msg->setFrom(iter->first);
    }
    subslock.release();
    // tell dispatcher that we can forward messages now
    // (note that doing it here ensures that the GWRemoteUp message is
    // only published to peers on "this" side of the connection)
    dsp()->declareForwarder(this);
    // send off the fake hello messages
    while( !hellos.empty() )
    {
      dsp()->send(hellos.front(),MsgAddress(AidPublish,AidPublish,
                                address().process(),address().host()));
      hellos.pop_front();
    }
  }
  else
  {
    lprintf(1,"error: received remote message while in unexpected peer-state\n");
    shutdown();
  }
}

// processes subscriptions contained in peer's init-message
// (the message block is formed in start(), above)
//##ModelId=3DB958F60003
int MTGatewayWP::processInitMessage (const void *block,size_t blocksize)
{
  FailWhen( !block,"no block" );
  size_t hdrsize;
  const size_t *hdr = static_cast<const size_t *>(block);
  int nwp;
  // big enough for header? 
  FailWhen( blocksize < sizeof(size_t) || 
            blocksize < ( hdrsize = (1 + 2*( nwp = *(hdr++) ))*sizeof(size_t) ),
            "corrupt block");
  // scan addresses and subscription blocks
  const char *data = static_cast<const char *>(block) + hdrsize,
             *enddata = static_cast<const char *>(block) + blocksize;
  
  Thread::Mutex::Lock(remote_subs_mutex);
  for( int i=0; i<nwp; i++ )
  {
    size_t asz = *(hdr++), ssz = *(hdr++);
    // check block size again
    FailWhen( data+asz+ssz > enddata,"corrupt block" ); 
    // unpack address 
    MsgAddress addr; 
    addr.unpack(data,asz); data += asz;
    // unpack subscriptions
    Subscriptions &subs(remote_subs[addr]);
    subs.unpack(data,ssz);
    data += ssz;
  }
  FailWhen(data != enddata,"corrupt block");
  
  return remote_subs.size();
}

//##ModelId=3DB958F50181
void MTGatewayWP::shutdown () 
{
  // shutdown called only once, and by any thread
  Thread::Mutex::Lock lock(gwmutex);
  if( shutdown_done )
    return;
  shutdown_done = True;
  
  dprintf(4)("shutdown\n");
  if( peerState() == CONNECTED )     // publish a Remote.Down message
  {
    HIID peerid = rprocess|rhost;
    lprintf(1,"shutting down connection to %s",(rprocess|rhost).toString().c_str());
    MessageRef mref(new Message(MsgGWRemoteDown|peerid),DMI::ANON);
    (*peerlist)[peerid].remove();
    publish(mref,0,Message::LOCAL);
  }
  else
    lprintf(1,"shutting down");
  
  setPeerState(CLOSING); 
  detachMyself();
  dprintf(4)("shutdown completed\n");
}

//##ModelId=3DB958F6012F
bool MTGatewayWP::mtStart (Thread::ThrID)
{
  // unblock SIGPIPE so that our system calls can be interrupted
  Thread::signalMask(SIG_UNBLOCK,SIGPIPE);
  // ensure that this piece of code is done once per gateway (i.e., by just
  // one worker thread)
  dprintf(1)("mtStart() entry\n");
  Thread::Mutex::Lock lock(gwmutex);
  if( initmsg_sent )
    return True;
  initmsg_sent = True;
  lock.release();
  
  dprintf(2)("First worker thread, transmitting init message\n");
  // init the write header
  memcpy(wr_header.signature,PacketSignature,sizeof(wr_header.signature));
  
  // transmit the message
  transmitMessage(initmsg);
  return True;
}

//##ModelId=3DB958F6017B
void MTGatewayWP::stopWorkers ()
{
  sock->interrupt();
  // send interruption signals and rejoin the reader threads
  dprintf(1)("stopWorkers: interrupting and rejoining reader threads\n");
  for( int i=0; i < NumReaderThreads; i++ )
    Thread::kill(reader_threads[i],SIGPIPE);
  for( int i=0; i < NumReaderThreads; i++ )
    Thread::join(reader_threads[i]);
  // send termination signals to interrupt the worker threads
  // (in case they're busy in a write() call)
  dprintf(1)("stopWorkers: interrupting worker threads\n");
  for( int i=0; i < numWorkers(); i++ )
    Thread::kill( workerID(i),SIGPIPE );
}

//##ModelId=3DB958F60246
void * MTGatewayWP::start_readerThread (void *pwp)
{
  return static_cast<MTGatewayWP*>(pwp)->readerThread();
}

  //## end MTGatewayWP%3C90BEF001E5.declarations
//## begin module%3C90BFDD0240.epilog preserve=yes
#endif // USE_THREADS
//## end module%3C90BFDD0240.epilog
