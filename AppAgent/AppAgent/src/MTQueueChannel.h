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

#ifndef _APPAGENT_MTQUEUECHANNEL_H
#define _APPAGENT_MTQUEUECHANNEL_H 1

#include <AppAgent/EventChannel.h>
#include <DMI/Exception.h>

#pragma aidgroup AppAgent
#pragma aid MT Queue Size Init

namespace AppAgent
{    

namespace EventChannelVocabulary
{
  const HIID FMTQueueSize  = AidMT|AidQueue|AidSize;
  
  const int DEFAULT_QUEUE_SIZE = 256;
};


//##ModelId=3E394D4C0195
//##Documentation
//## MTQueueChannel is an mt interface to another event channel.
//## The second channel is polled in a separate thread, so it executes
//## in parallel. Messages are exchanged back and forth via two queues.
//## In the init-record, the MT.Queue.Size field specifies the maximum 
//## queue size. Once either queue reaches this size, the sending end 
//## is blocked until the queue becomes smaller.
//## The rest of the record is passed on to the other channel.

class MTQueueChannel : public EventChannel
{
  public:
    //##ModelId=3E410DB50060
    DefineRefTypes(MTQueueChannel,Ref);
  
    //##ModelId=3E4100E40257
    MTQueueChannel (const EventChannel::Ref &channel);
    
    MTQueueChannel (EventChannel *pchannel);
    
    ~MTQueueChannel ();
    
    //##ModelId=3E4143B200F2
    //##Documentation
    //## Inits agent, sets up queues, starts a separate thread for the other end.
    virtual int init (const DMI::Record &data);
    
    //## flushes output events, closes the agent and stops worker thread
    virtual void close (const string &str = "");
    
    //## aborts output, aborts the agent and stops worker thread
    virtual void abort (const string &str = "");
    
    //##ModelId=3E8C3BDC0159
    //##Documentation
    //## Advertises the fact that an app is interested in a specific
    //## event or set of events (wildcards may be employed). Default version does
    //## nothing. Subclasses with explicit event filtering (e.g., those using
    //## publish/subscribe) will probably redefine this to something useful.
    virtual void solicitEvent (const HIID &mask);
    
    //##ModelId=3E394D4C02BB
    //##Documentation
    virtual int getEvent ( HIID &id,ObjRef &data,
                           const HIID &mask,
                           int wait = AppEvent::WAIT,
                           HIID &source = _dummy_hiid );

    //##ModelId=3E394D4C02C1
    //##Documentation
    //## Checks if there is an event pending that matches the specified
    //## mask (default - no mask - matches any event). Id of event is
    //## returned via the out argument.
    //## Return codes are the same as would have been returned by
    //## getEvent(wait=NOWAIT), above.
    virtual int hasEvent (const HIID &mask = HIID(),HIID &out = _dummy_hiid);
      
    //##ModelId=3E394D4C02C9
    //##Documentation
    //## Posts an event on behalf of the application.
    //## If a non-empty destination is specified, the event is directed at
    //## a specific destination, if the event channel implementation supports 
    //## this (e.g., if responding to a request event, destination could be
    //## equal to the original event source).
    //## The event category may be used by some channels to discriminate
    //## between, e.g., Normal and Debug events. Most channels can and do 
    //## ignore the category.
    virtual void postEvent (const HIID &id,
                            const ObjRef &data = ObjRef(),
                            AtomicID category = AidNormal,
                            const HIID &destination = HIID() );
    //##ModelId=3E8C1F8703DC
    //##Documentation
    //## Checks whether a specific event is bound to any output. I.e., if the
    //## event would be simply discarded when posted, returns false; otherwise,
    //## returns true. Apps can check this before posting "expensive" events.
    //## Default implementation always returns false.
    virtual bool isEventBound (const HIID &id,AtomicID category);

    //##ModelId=3E394D4C02D7
    //##Documentation
    virtual void flush ();
      
    //##ModelId=3E47852A012C
    //## returns true if channel is capable of generating events asynchronously
    //## of the calling thread. OctoChannel for example is multithreaded,
    //## so it's asynchronous. Channels that read files, on the other hand,
    //## are not.
    virtual bool isAsynchronous() const
    { return true; }
      
    //##ModelId=3E394D4C02DE
    virtual string sdebug ( int = 1,const string & = "",
                            const char * = 0 ) const
    { return "MTQueueChannel"; }
      
  protected:
    static void * start_workerThread (void *args);

    void * runWorker ();
    
    // helper method: waits for remote channel to initialize itself,
    // if it already hasn't. !!! caller must have lock on eventFlag().condVar()
    void assureRemoteInit () const
    {
      while( !remote_initialized_ )
        eventFlag().condVar().wait();
    }
    
    // helper method: if error list is not empty, grabs a copy of the list,
    // clears the list, wakes up remote thread, and throws list as exception
    void checkErrorQueue ();
      
    EventChannel & remote ()
    { return *premote_; }
    
    const EventChannel & remote () const
    { return *premote_; }
  
    EventChannel * premote_;
    EventChannel::Ref remote_chanref_;
    
    typedef struct
    {
      HIID id;
      HIID addr;
      AtomicID category;
      ObjRef data;
    } QueueEntry;
    
    typedef std::deque<QueueEntry> Queue;
    
    Queue post_queue_;
    Queue get_queue_;
    
    // error queue -- for exceptions from remote agent
    DMI::ExceptionList err_queue_;
    
    // max queue size 
    uint queue_size_;
    
    Thread::ThrID remote_thread_;
    
    DMI::Record::Ref initrec_;
    
    // flag: remote channel has completed its init
    bool remote_initialized_;
    // flag: main channel has been aborted rather than closed
    bool aborted_;
};
    
};
#endif
    
    
