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

#ifdef USE_THREADS

#include "Gateways.h"
#include "MTGatewayWP.h"
#include <deque>
#include <DMI/Exception.h>

namespace Octopussy
{


// use large timeouts because we're not multithreaded anymore
const Timeval to_init(30.0),
              to_write(30.0),
              to_heartbeat(5.0);
              
// all packet headers must start with this signature
const char * MTGatewayWP::PacketSignature = "oMs";
    


// Class MTGatewayWP 

MTGatewayWP::MTGatewayWP (Socket* sk)
  : WorkProcess(AidGatewayWP),sock(sk)
{
#ifndef USE_THREADS
  Throw("MTGatewayWP not compiled for thread support");
#endif
  dprintf(2)("constructor\n");
  setState(0);
  setPeerState(INITIALIZING);
  rprocess = rhost = 0;
  reading_socket = first_message_read = false;
  shutdown_done = shutting_down = false;
  statmon.time_not_reading.reset();
}


MTGatewayWP::~MTGatewayWP()
{
  dprintf(2)("destructor\n");
  if( sock )
    delete sock;
}



void MTGatewayWP::init ()
{
  dprintf(2)("init\n");
  // subscribe to local subscribe notifications and Bye messages
  // (they will be forwarded to peer as-is)
  subscribe(MsgSubscribe|AidWildcard,Message::LOCAL);
  subscribe(MsgBye|AidWildcard,Message::LOCAL);
}

bool MTGatewayWP::start ()
{
  dprintf(2)("start\n");
  WorkProcess::start();
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
  initmsg()[AidPeers] = gatewayPeerList;
  initmsg_sent = false;
  
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
  writing = false;
  
  sock->setBlocking(true);
  
  // spawn worker threads (for writing)
  for( int i=0; i<NumWriterThreads; i++ )
  {
    Thread::ThrID tid = createWorker();
    dprintf(1)("created worker thread %d\n",(int)tid);
  }
  
  // spawn several reader threads
  for( int i=0; i<NumReaderThreads; i++ )
  {
    ReaderThreadInfo &info = reader_threads[i];
    info.running = true;
    info.self = this;
    info.thr_id = Thread::create(start_readerThread,&info);
    FailWhen(!info.thr_id,"failed to create reader thread");
    dprintf(1)("created reader thread %d\n",(int)info.thr_id);
  }
  
  return false;
}

void MTGatewayWP::stop ()
{
  // this is the normal stop() entrypoint: by this stage, all worker
  // threads will have been shut down
  dprintf(4)("stop\n");
  // but we still call shutdown() to take care of reader threads
  shutdown();
  if( sock )
    delete sock;
  sock = 0;
}

bool MTGatewayWP::willForward (const Message &msg) const
{
  if( peerState() != CONNECTED )
    return false;
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
      return false;
    }
    if( msg.hops() > 3 )
    {
      dprintf(3)("no, hopcount = %d\n",msg.hops() );
      return false;
    }
  }
  else if( msg.hops() > 0 )
  {
    dprintf(3)("no, non-local origin, hopcount = %d\n",msg.hops() );
    return false;
  }
  // Check that to-scope of message matches remote 
  if( !rprocess.matches( msg.to().process() ) ||
      !rhost.matches( msg.to().host() ) )
  {
    dprintf(3)("no, `to' does not match remote %s.%s\n",
               rprocess.toString().c_str(),rhost.toString().c_str());
    return false;
  }
  // if message is published, search thru remote subscriptions
  Thread::Mutex::Lock lock(remote_subs_mutex);
  if( msg.to().wpclass() == AidPublish )
  {
    for( CRSI iter = remote_subs.begin(); iter != remote_subs.end(); iter++ )
      if( iter->second.matches(msg) )
      {
        dprintf(3)("yes, subscribed to by remote %s\n",iter->first.toString().c_str());
        return true;
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
        return true;
      }
    dprintf(3)("no, no matching remote WPs\n");
  }
  return false;
}

int MTGatewayWP::receive (Message::Ref& mref)
{
  // process shutdown event from ourselves (from a reader thread, presumably)
  if( mref->id() == AidBye && mref->from() == address() )
  {
    shutdown();
    return Message::ACCEPT;
  }
  
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
}

int MTGatewayWP::timeout (const HIID &id)
{
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
      lprintf(1,AidLogError,"timed out waiting for write()\n");
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
}

// Additional Declarations
void MTGatewayWP::processIncoming (Message::Ref &ref)
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
      bool success = false;
      if( msg.data() )
      {
        try {
          subs.unpack(msg.data(),msg.datasize());
          success = true;
        } catch( std::exception &exc ) {
          lprintf(2,"warning: failed to unpack Subscribe message: %s\n",
              exceptionToString(exc).c_str());
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
      shutdownReaderThread();
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
      Thread::Mutex::Lock peerlock(gatewayPeerList.mutex());
      // paranoid case: if we already have a connection to the peer, shutdown
      // (this really ought not to happen)
      if( gatewayPeerList[peerid].exists() )
      {
        lprintf(1,AidLogError,"already connected to %s (%s:%d %s), closing gateway",
              peerid.toString().c_str(),
             gatewayPeerList[peerid][AidHost].as<string>().c_str(),
             gatewayPeerList[peerid][AidPort].as<int>(),
             gatewayPeerList[peerid][AidTimestamp].as<Timestamp>().toString("%T").c_str());
        Message *msg1 = new Message(MsgGWRemoteDuplicate|peerid);
        Message::Ref mref1; mref1 <<= msg1;
        (*msg1)[AidHost] = sock->host();
        (*msg1)[AidPort] = atoi(sock->port().c_str());
        publish(mref1,0,Message::LOCAL);
        setPeerState(CLOSING);
        shutdownReaderThread();
        return;
      }
      // add this connection to the local peerlist
      DMI::Record & rec = gatewayPeerList[peerid] <<= new DMI::Record;
      rec[AidTimestamp] = Timestamp::now();
      rec[AidHost] = sock->host();
      rec[AidPort] = atoi(sock->port().c_str());
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
      lprintf(1,"error: processing init message: %s\n",
          exceptionToString(exc).c_str());
      shutdownReaderThread();
      return;
    }
    // publish (locally only) fake Hello messages on behalf of all remote WPs
    // to avoid deadlock, we first generate a list of messages, then send them
    // off once the remote_subs mutex has been released
    deque<Message::Ref> hellos;
    Thread::Mutex::Lock subslock(remote_subs_mutex);
    for( CRSI iter = remote_subs.begin(); iter != remote_subs.end(); iter++ )
    {
      hellos.push_back(Message::Ref());
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
    shutdownReaderThread();
  }
}

// processes subscriptions contained in peer's init-message
// (the message block is formed in start(), above)
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

// This is called from a reader thread to initiate a shutdown sequence
// Since we hold a lock on the reader mutex when calling this, we can check for 
// shutting_down to see if it has already been initiated
void MTGatewayWP::shutdownReaderThread () 
{
  if( !shutting_down )
  {
    shutting_down = true;
    // send a shutdown message to wake up a worker thread
    send(AidBye,address(),0,Message::PRI_EVENT);
  }
}

// this is called to initiate shutdownn() from the main thread
void MTGatewayWP::shutdown () 
{
  // shutdown called only once, and by any thread
  Thread::Mutex::Lock lock(gwmutex);
  if( shutdown_done )
    return;
  shutdown_done = shutting_down = true;
  //// NB 19/12/07: this can cause a segfault if one worker/reader thread calls shutdown itself, then exits,
  //// then this thread tries to send it a signal. So I have moved the mutex release down after
  //// the reader threads have been interrupted
  // // release gwmutex now: now that the flag is set, only one thread
  // // will get this far
  if( peerState() == CONNECTED )     // publish a Remote.Down message
  {
    HIID peerid = rprocess|rhost;
    Message::Ref mref(new Message(MsgGWRemoteDown|peerid),DMI::ANON);
    gatewayPeerList[peerid].remove();
    publish(mref,0,Message::LOCAL);
    lprintf(1,"shutting down connection to %s",(rprocess|rhost).toString().c_str());
  }
  else
    lprintf(1,"shutting down");
  
  dprintf(4)("shutdown: interrupting socket\n");
  sock->interrupt();
  setPeerState(CLOSING); 
  detachMyself();
  dprintf(4)("shutdown: WP detached\n");
  // send interruption signals and rejoin the reader threads
  dprintf(1)("shutdown: interrupting reader threads\n");
  for( int i=0; i < NumReaderThreads; i++ )
    if( reader_threads[i].thr_id != Thread::self() && reader_threads[i].running )
      reader_threads[i].thr_id.kill(SIGPIPE);
  // release lock: we must allow the reader threads to exit
  lock.release();
  // now wait .5 sec for any stray reader threads, then send the signal again
  struct timeval timeout = {0,500000};
  select(0,0,0,0,&timeout);
  lock.relock(gwmutex);
  dprintf(1)("shutdown: reinterrupting reader threads\n");
  for( int i=0; i < NumReaderThreads; i++ )
    if( reader_threads[i].thr_id != Thread::self() && reader_threads[i].running )
      reader_threads[i].thr_id.kill(SIGPIPE);
  // release lock so that reader threads can exit
  lock.release();
  // now rejoin them
  dprintf(1)("shutdown: rejoining reader threads\n");
  for( int i=0; i < NumReaderThreads; i++ )
    if( reader_threads[i].thr_id != Thread::self() )
      reader_threads[i].thr_id.join();
  dprintf(4)("shutdown completed\n");
}

bool MTGatewayWP::mtStart (Thread::ThrID)
{
  // unblock SIGPIPE so that our system calls can be interrupted
  Thread::signalMask(SIG_UNBLOCK,SIGPIPE);
  // ensure that this piece of code is done once per gateway (i.e., by just
  // one worker thread)
  dprintf(1)("mtStart() entry\n");
  Thread::Mutex::Lock lock(gwmutex);
  if( initmsg_sent )
    return true;
  initmsg_sent = true;
  lock.release();
  
  dprintf(2)("First worker thread, transmitting init message\n");
  // init the write header
  memcpy(wr_header.signature,PacketSignature,sizeof(wr_header.signature));
  
  // transmit the message
  transmitMessage(initmsg);
  return true;
}

void MTGatewayWP::stopWorkers ()
{
  // send termination signals to interrupt the worker threads
  // (in case they're busy in a write() call)
  dprintf(1)("stopWorkers: interrupting worker threads\n");
  killWorkers(SIGPIPE);
}

void * MTGatewayWP::start_readerThread (void *pinfo)
{
  ReaderThreadInfo &info = *static_cast<ReaderThreadInfo*>(pinfo);
  void *ret =  info.self->readerThread();
  Thread::Mutex::Lock lock(info.self->gwmutex);
  info.running = false;
  return ret;
}

};

#endif // USE_THREADS
