#include "OctoEventMultiplexer.h"
#include "OctoEventSink.h"
#include <OCTOPUSSY/WPInterface.h>

namespace AppAgent    
{
  
namespace OctoAgent    
{

InitDebugContext(EventMultiplexer,"OctoEventMux");
  
using namespace AppEvent;

//##ModelId=3E26BE240137
EventMultiplexer::EventMultiplexer (AtomicID wpid)
    : WorkProcess(wpid)
{
  pheadmsg = 0;
  eventFlag_ <<= new AppEventFlag;
  // register ourselves with the EventFlag as an async event source
  ef_sink_num = eventFlag().addSource(true);
  // disable WP polling
  disablePolling();
}

//##ModelId=3E26BE670240
EventMultiplexer::~EventMultiplexer ()
{
  sinks.clear();
}

//##ModelId=3E47C84502CD
void EventMultiplexer::notify ()
{
  // notify signals on the event flag 
  eventFlag().raise(ef_sink_num);
}

//##ModelId=3E47CFA70203
void EventMultiplexer::stop()
{
  // raise the event flag since we've stopped
  eventFlag().raise(ef_sink_num);
}

//##ModelId=3E535889025A
EventSink & EventMultiplexer::newSink ()
{
  EventSink * psink = new EventSink(*this,DMI::ANONWR);
  return *psink;
}

//##ModelId=3E428F93013E
EventMultiplexer& EventMultiplexer::addSink (EventSink::Ref &sink)
{
  FailWhen(!sink.valid() || !sink.isWritable(),"valid writable ref required");
  sink().setMultiplexId(sinks.size());
  sinks.push_back(sink);
  return *this;
}

//##ModelId=3E26BE760036
EventMultiplexer&  EventMultiplexer::addSink (EventSink* sink,int flags)
{
  EventSink::Ref ref(sink,flags|DMI::WRITE);
  return addSink(ref);
}

//##ModelId=3E428F70021D
EventMultiplexer&  EventMultiplexer::addSink (EventSink& sink,int flags)
{
  EventSink::Ref ref(sink,flags|DMI::WRITE);
  return addSink(ref);
}

//##ModelId=3E50E02C024B
void EventMultiplexer::init()
{
  close();
}

//##ModelId=3E50E292002B
void EventMultiplexer::close()
{
  pheadmsg = 0;
  assigned_data.detach();
}

//##ModelId=3E3FC3A7000B
int EventMultiplexer::checkQueue (const HIID& mask,int wait,int sink_id)
{
  if( !isRunning() )
    return CLOSED;
  // lock the queue first 
  Thread::Mutex::Lock lock( queueCondition() );
  // do we have a cached event (at the head of the message queue) that hasn't
  // been picked up yet?
  if( pheadmsg )
  {
    cdebug(4)<<"have cached message "<<pheadmsg->sdebug(2)<<endl;
    // has the head of the queue changed?
    if( queue().empty() || queue().front().mref.deref_p() != pheadmsg )
    {
      // discard cached event, and fall through to below
      cdebug(4)<<"head of queue has changed, forgetting about cached message\n";
      pheadmsg = 0;
      assigned_data.detach();
    }
    else
    {
      // assigned to us, with a matching mask? Return success
      if( assigned_sink == sink_id && assigned_event.matches(mask) )
      {
        // remove message from queue -- assigned_event 
        // and assigned_data will contain the event
        cdebug(4)<<"cached message assigned to this sink ("<<sink_id<<"): SUCCESS\n";
        queue().pop_front();
        return SUCCESS;
      }
      cdebug(4)<<"cached message not assigned to this sink ("<<sink_id<<"): OUTOFSEQ\n";
      // not assigned to us? Return out-of-sequence
      return OUTOFSEQ;
    }
  }
  // OK, no event cached.  
  for(;;) // will only break out of loop via return statement
  {
    // First fart around until the queue's got something in it
    while( queue().empty() )
    {
      // in case we get shut down within this loop
      if( !isRunning() )
        return CLOSED;
      cdebug(4)<<"message queue is empty, clearing event flag #"<<sink_id<<"\n";
      // Since we've locked an empty queue, receive() above can't be called 
      // (since it's only ever called when something's in the queue to begin with)
      // First, clear our event flag bit
      eventFlag().clear(ef_sink_num);
      // Is there anything else in the event flag? must be someone else's event
      if( eventFlag().isRaised() )
      {
        if( wait == BLOCK ) // if blocking is requested, wait on our queue variable
        {
          cdebug(4)<<"other sinks have pending events, BLOCKing on queue_cond\n";
          queueCondition().wait();
        }
        else // otherwise, return out-of-sequence
        {
          cdebug(4)<<"other sinks have pending events: OUTOFSEQ\n";
          return OUTOFSEQ;
        }
      }
      // else event flag is totally clear
      else 
      {
        if( wait == NOWAIT )        // asked not to wait? return now
        {
          cdebug(4)<<"no pending events: WAIT\n";
          return WAIT;
        }
        else if( wait == BLOCK )    // blocking wait -- wait on our queue
        {
          cdebug(4)<<"no pending events, BLOCKing on queue_cond\n";
          queueCondition().wait();
        }
        else                        // non-blocking wait -- wait on event flag
        {
          // release lock on queue and wait for some other event
          lock.release();
          cdebug(4)<<"no pending events, WAITing on event flag\n";
          eventFlag().wait();
          // reaquire queue lock since we're looping back for another check
          lock.relock( queueCondition() );
        }
      }
    }
    // Ok, at this point our queue is no longer empty, and we have a lock on it
    // Get the lead message from the queue and figure out which agent to
    // assign it to
    const Message &msg = queue().front().mref.deref();
    cdebug(3)<<"checking message "<<msg.sdebug(2)<<endl;
    // check against input map of every sink
    bool assigned = false;
    for( uint i=0; i<sinks.size(); i++ )
    {
      if( sinks[i]().mapReceiveEvent(assigned_event,msg.id()) )
      {
        assigned = true;
        pheadmsg = &msg;
        assigned_sink = i;
        assigned_data = msg.payload();
        assigned_source = msg.from();
        cdebug(3)<<"maps to "<<sinks[i]->sdebug(1)<<", event "<<assigned_event<<endl;
        if( i == uint(sink_id) )
        {
          if( assigned_event.matches(mask) )
          {
            queue().pop_front();
            return SUCCESS;
          }
          else if( wait != AppEvent::BLOCK ) // message for this sink, doesn't match
            return OUTOFSEQ;
        }
        else if( wait != AppEvent::BLOCK ) // message for other sink
          return OUTOFSEQ;
        break;
      }
    }
    // message assigned but not returned -- must be in blocking mode then,
    // so wait for the queue to change
    if( assigned )
      queueCondition().wait();
    else
    {
      // the message has not been assigned to any sink.
      // Discard it and go back for another try
      cdebug(3)<<"unmapped message, discarding\n";
      queue().pop_front();
      // go back for another try
    }
  }
}

//##ModelId=3E26D2D6021D
int EventMultiplexer::getEvent (HIID& id,ObjRef& data,const HIID& mask,int wait,HIID &source,int sink_id)
{
  // check the queue
  int res = checkQueue(mask,wait,sink_id);
  if( res == SUCCESS )
  {
    // return cached event if successful
    id = assigned_event;
    data = assigned_data;
    source = assigned_source;
    pheadmsg = 0; // and clear the cache
    return SUCCESS;
  }
  return res;
}

//##ModelId=3E3FC3A601B0
int EventMultiplexer::hasEvent (const HIID& mask,int sink_id)
{
  return checkQueue(mask,NOWAIT,sink_id);
}


string EventMultiplexer::sdebug (int detail, const string &prefix, const char *name) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s/%08x",name?name:"OctoEventMux",(int)this);
  }
  if( detail >= 1 || detail == -1 )
  {
    appendf(out,"sinks:%d",sinks.size());
    appendf(out,"wp:%s",WorkProcess::sdebug(abs(detail),prefix).c_str());
  }
  return out;
}

} // namespace OctoAgent    

};

