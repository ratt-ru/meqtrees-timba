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

#include "MTGatewayWP.h"
#include <DMI/Exception.h>

namespace Octopussy
{
    
// all packet headers must start with this signature
static const char PacketSignature[] = "oMs";
        
//##ModelId=3DB958F502B8
int MTGatewayWP::requestResync ()
{
  // Should eventually send an OOB message for a resync.
  // For now, just start looking for a header
  return readyForHeader();
}

//##ModelId=3DB958F502BA
int MTGatewayWP::requestRetry ()
{
  // Should eventually send an OOB message for a retransmit.
  // For now, just fllush incoming blocks and start looking for a header.
  return readyForHeader();
}

//##ModelId=3DB958F502BC
int MTGatewayWP::readyForHeader ()
{
  read_buf_size = sizeof(header);
  read_buf = reinterpret_cast<char*>(&header);
  nread = 0;
  readstate = HEADER;
  dprintf(5)("read state is now HEADER\n");
  return 0;
}

//##ModelId=3DB958F502BD
int MTGatewayWP::readyForTrailer ()
{
  read_buf_size = sizeof(trailer);
  read_buf = reinterpret_cast<char*>(&trailer);
  nread = 0;
  readstate = TRAILER;
  dprintf(5)("read state is now TRAILER\n");
  return 0;
}

//##ModelId=3DB958F502BF
int MTGatewayWP::readyForData ( const PacketHeader &hdr,BlockSet &bset )
{
  read_buf_size = hdr.content;
  if( read_buf_size > MaxBlockSize )
  {
    lprintf(1,AidLogWarning,"incoming block too big (%d), skipping\n",read_buf_size);
    return requestResync();
  }
  nread = 0;
  // if this is the first block of a message, get a timestamp
  if( bset.empty() )
    Timestamp::now(&start_message_read);
  
  SmartBlock * bl = new SmartBlock(read_buf_size);
  bset.pushNew().attach(bl,DMI::ANONWR);
  read_buf = static_cast<char*>(bl->data());
  readstate = BLOCK;
  dprintf(5)("read state is now BLOCK\n");
  read_checksum = 0;
  return 0;
}

//##ModelId=3DB958F602AB
void * MTGatewayWP::readerThread ()
{
  dprintf(3)("readerThread entry\n");
  Thread::signalMask(SIG_BLOCK,Dispatcher::validSignals());
  // unblock SIGPIPE so that our system calls can be interrupted
  Thread::signalMask(SIG_UNBLOCK,SIGPIPE);
  BlockSet bset;
  Thread::Mutex::Lock reader_lock;
  dprintf(3)("waiting for main thread to finish startup\n");
  awaitMainThreadStartup();
  dprintf(3)("main thread has completed startup\n");
  try
  {
    int read_junk = 0,incoming_checksum = 0;
    // obtain a lock on the reader mutex, so that only one thread
    // at a time may be reading data. We will hold this lock
    // until return from this function
    reader_lock.relock(reader_mutex);
    readyForHeader();
    while( isRunning() && !shutting_down )
    {
      // if we are not in a reading-socket state (i.e., after a message
      // has been sent off), then time how long we were in it
      if( !reading_socket )
      { 
        // time how long no-one was reading anything
        Thread::Mutex::Lock lock(statmon.read_mutex);
        if( first_message_read )
          statmon.time_not_reading += Timestamp::now() - ts_stopread;
        reading_socket = true;
      }
      // read up to full buffer
      while( nread < read_buf_size )
      {
        dprintf(6)("readerThread: going into readBlocking\n");
        Thread::Mutex::Lock lock1(gwmutex);
        if( !isRunning() || shutting_down )
        {
          dprintf(2)("readerThread: shutdown detected, exiting\n");
          return 0; 
        }
        lock1.release();
        int n = sock->readBlocking(read_buf + nread,read_buf_size - nread);
        dprintf(5)("readBlocking(buf+%d,%d)=%d\n",nread,read_buf_size-nread,n);
        if( n<0 )
          dprintf(5)("errno=%d (%s)\n",errno,strerror(errno));
        if( !isRunning() || shutting_down )
        {
          dprintf(2)("readerThread: shutdown detected, exiting\n");
          return 0; 
        }
        else if( n <= 0 )
        {
          // on read error, just commit harakiri. GWClient/ServerWP will
          // take care of reopening a connection, eventually
          lprintf(1,AidLogError,"error on socket read(): %s. Aborting.\n",sock->errstr().c_str());
          shutdownReaderThread();
          return 0; 
        }
        else if( n > 0 )
        {
          Thread::Mutex::Lock lock(statmon.read_mutex);
          statmon.read += n;
          Timestamp::now(&statmon.last_read);
          lock.release();
          // update checksum and advance the nread pointer
          #if GATEWAY_CHECKSUM
          for( ; n>0; n--,nread++ )
            read_checksum += read_buf[nread];
          #else
          nread += n;
          #endif
        }
      }
      // since we got here, we have a complete buffer, so dispose of it according to mode
      if( readstate == HEADER ) // got a packet header?
      {
        if( memcmp(header.signature,PacketSignature,sizeof(header.signature)) ||
            header.type > MT_MAXTYPE )
        {
          dprintf(5)("header does not start with signature\n");
          // invalid header -- flush it
          if( !read_junk )
          {
            dprintf(2)("error: junk data before header\n");
            requestResync();  // request resync if this is first instance
          }
          // look for first byte of signature in this header
          void *pos = memchr(&header,PacketSignature[0],sizeof(header));
          if( !pos ) // not found? flush everything
          {
            dprintf(5)("no signature found, flushing everything\n");
            nread = 0;
            read_junk += sizeof(header);
          }
          else
          { // else flush everything up to matching byte
            int njunk = static_cast<char*>(pos) - reinterpret_cast<char*>(&header);
            nread = sizeof(header) - njunk;
            read_junk += njunk;
            memmove(&header,pos,nread);
            dprintf(5)("signature found, flushing %d junk bytes\n",njunk);
          }
        }
        // else header is valid
        else
        {
          if( read_junk )
          { 
            // got any junk before it? report it
            lprintf(2,AidLogWarning,"%d junk bytes before header were discarded\n",read_junk);
            read_junk = 0;
          }
          switch( header.type )
          {
            case MT_PING: 
                dprintf(5)("PING packet, ignoring\n");
                break; // ignore ping message

            case MT_DATA:       // data block coming up
                readyForData(header,bset); // sets buffers and read states accordingly
                break;

            case MT_ACK:         // acknowledgement of data message
                dprintf(5)("ACK packet, ignoring\n");
                // to do later
            case MT_RETRY:       // retry data message
                dprintf(5)("RETRY packet, ignoring\n");
                // to do later
                break;
            default:
                lprintf(2,AidLogWarning,"unknown packet type %d, ignoring\n",header.type);
          }
        } // end else header is valid
      } // end if( readState() == HEADER )
      else if( readstate == BLOCK )
      {
        incoming_checksum = read_checksum;
        readyForTrailer(); // sets buffers and read states accordingly
      }
      else if( readstate == TRAILER )
      {
        // to do: check sequence number
        // verify checksum
        #if GATEWAY_CHECKSUM
        if( incoming_checksum == trailer.checksum )
        #endif
        {
          dprintf(4)("received block #%d (tms=%d) of size %d, %d blocks in set\n",
              trailer.seq,trailer.msgsize,bset.back()->size(),bset.size());
          // can't access some members anymore, since we're releasing the mutex
          // so cache them as local variables
          int tmsgsize = trailer.msgsize;
          if( tmsgsize ) // accumulated a complete message?
          {
            Timestamp start_read = start_message_read; // cache before releasing mutex
            // maintain timings of when reading has stopped
            Timestamp::now(&ts_stopread);
            reading_socket = false;
            first_message_read = true;
            
            if( bset.size() != tmsgsize )
            { // major oops
              lprintf(1,AidLogWarning,"expected %d blocks, got %d, discarding message\n",tmsgsize,bset.size());
              bset.clear();
            }
            else
            {
              // convert & process the incoming message
              Message *msg = new Message;
              Message::Ref ref(msg,DMI::ANONWR);
              bool success = false;
              try
              {
                msg->fromBlock(bset);
                success = true;
              }
              catch( std::exception &exc )
              {
                lprintf(0,AidLogError,"Exception while unpacking message: %s",
                    exceptionToString(exc).c_str());
                lprintf(0,AidLogError,"Message will be dropped");
              }
              catch( ... )
              {
                lprintf(0,AidLogError,"Unknown exception while unpacking message");
                lprintf(0,AidLogError,"Message will be dropped");
              }
              if( success )
              {
#ifdef ENABLE_LATENCY_STATS
                msg->latency.add(start_read,"<RCV");
                msg->latency.measure("RCV>");
#endif
                if( !bset.empty() )
                  lprintf(2,"warning: %d unclaimed incoming blocks will be discarded\n",bset.size());
  // OMS 04/01/2005: commented this out...
  //               // release the reader mutex so that other threads may go into their
  //               // own read state while we fuck around with the received message.
  //               // If still initializing the connection, then also acquire the gwmutex,
  //               // to ensure that no incoming messages are processed until
  //               // parsing of the init-message is complete.
  //               if( peerState() == INITIALIZING )
  //                 reader_lock.relock(gwmutex);
  //               else
  //                 reader_lock.release();
  // OMS 04/01/2005: ...because not holding a lock while the incoming message
  // is being processed can possibly lead to the incoming message sequence being 
  // violated (if another reader thread preempts this one inside processIncoming()).
  // Thus, we'll always acquire gwmutex here and then release the reader mutex.
                Thread::Mutex::Lock lock1(gwmutex);
                reader_lock.release();
                // process the message
                processIncoming(ref);
              }
            }
            reader_lock.release();
            // reacquire mutex to go into read state again
            reader_lock.relock(reader_mutex);
          }
          // expect header next
          readyForHeader(); // sets buffers and read states accordingly
        }
        #if GATEWAY_CHECKSUM
        else
        {
          dprintf(2)("block #%d: bad checksum\n",trailer.seq);
          requestRetry();  // ask for retry, clear buffer
        }
        #endif
      }
      else
        Throw("unexpected read state");
    }
  }
  catch( std::exception &exc )
  {
    lprintf(0,AidLogError,"Reader thread %ld terminated with exception %s",(long)Thread::self().id(),
        exceptionToString(exc).c_str());
  }
  // pthread_cancel will cause an exception
  catch( ... )
  {
    lprintf(1,AidLogError,"Reader thread %ld terminated with unknown exception",(long)Thread::self().id());
    throw;
  }
  shutdownReaderThread();
  dprintf(3)("readerThread: exiting\n");
  return 0;
}

//##ModelId=3DB958F60001
void MTGatewayWP::reportWriteError ()
{
  // on write error, just commit harakiri. GWClient/ServerWP will
  // take care of reopening a connection eventually
  lprintf(1,AidLogError,"error on socket write(): %s. Aborting.\n",sock->errstr().c_str());
  shutdown();
}

    
//##ModelId=3DB958F600CB
void MTGatewayWP::transmitMessage (Message::Ref &mref)
{
  dprintf(4)("transmitMessage [%s]\n",mref->sdebug(1).c_str());
// OMS 04/01/2005: same thing, if toBlock() is preempted, another thread
// can get in and write its message out ahead of time. Do a two-stage sync
// a-la readerThread();
  Thread::Mutex::Lock lock0(pre_writer_mutex);
#ifdef ENABLE_LATENCY_STATS
  mref().latency.measure("XMIT");
#endif
  // convert the message to blocks, placing them into the write queue
  BlockSet bset;
  mref->toBlock(bset);
  mref.detach();
  
// OMS 04/01/2005: release pre-write mutex and acquire write
  Thread::Mutex::Lock lock(writer_mutex);
  lock0.release();
  
  int nwr = 0;
  
//  int nnonzero = 0; // for valgrind trap below
  
  // send the blocks off one by one
  int msgsize = bset.size();
  while( !bset.empty() && isRunning() )
  {
    BlockRef ref;
    bset.pop(ref);
    wr_header.type = MT_DATA;
    wr_header.content = ref->size();
    // write the header
    Timestamp::now(&write_timestamp);
    writing = true;
    int n = sock->writeBlocking(&wr_header,sizeof(wr_header));
    if( !isRunning() )
      break;
    dprintf(5)("writeBlocking(header,%d)=%d\n",sizeof(wr_header),n);
    if( n == sizeof(wr_header) )
    {
      nwr += n;
      // write data block
      const char *data = static_cast<const char *>(ref->data());
      int sz = ref->size();
      
      // valgrind trap for catching uninitialized values in the block
//      for( int i=0; i<sz; i++ )
//        if( data[i] )
//          nnonzero++;
      // end of valgrind trap
      
      Timestamp::now(&write_timestamp);
      n = sock->writeBlocking(data,sz);
      if( !isRunning() )
        break;
      dprintf(5)("writeBlocking(data,%d)=%d\n",sz,n);
      // compute checksum & write trailer
      if( n == sz )
      {
        nwr += n;
        DataTrailer wr_trailer;
        #if GATEWAY_CHECKSUM
        wr_trailer.checksum = 0;
        while( sz-- )
          wr_trailer.checksum += *data++;
        #else
        wr_trailer.checksum = 0;
        #endif
        wr_trailer.seq = write_seq++;
        if( !bset.empty() )  // something left in queue?
          wr_trailer.msgsize = 0;
        else
          wr_trailer.msgsize = msgsize;
        Timestamp::now(&write_timestamp);
        n = sock->writeBlocking(&wr_trailer,sizeof(wr_trailer));
        dprintf(5)("writeBlocking(trailer,%d)=%d\n",sizeof(wr_trailer),n);
        if( n == sizeof(wr_trailer) )
          nwr += n;
        else
          n = -1;
      }
      else
        n = -1;
    }
    else
      n = -1;
    if( n < 0 )
    {
      lock.release(); // release writer lock to report error
      reportWriteError();
      break;
    }
    else
    {
      // update status monitor
      Thread::Mutex::Lock stlock(statmon.write_mutex);
      statmon.written += nwr;
      Timestamp::now(&statmon.last_write);
      stlock.release();
    }
    nwr = 0;
  } // end  while( !bset.empty()) 
  writing = false;
  // this releases the writer mutex
}


#endif // USE_THREADS
};
