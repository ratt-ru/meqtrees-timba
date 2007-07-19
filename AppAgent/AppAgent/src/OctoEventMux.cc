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

#include "OctoEventMux.h"
#include "OctoChannel.h"
#include <OCTOPUSSY/WPInterface.h>

namespace AppAgent    
{

InitDebugContext(OctoEventMux,"OctoEventMux");
  
using namespace AppEvent;
using namespace Octopussy;

//##ModelId=3E26BE240137
OctoEventMux::OctoEventMux (AtomicID wpid)
    : WorkProcess(wpid)
{
  pheadmsg = 0;
  eventFlag_ <<= new EventFlag;
  // register ourselves with the EventFlag as an async event source
  ef_channel_num = eventFlag().addSource(true);
  // disable WP polling
  disablePolling();
}

//##ModelId=3E26BE670240
OctoEventMux::~OctoEventMux ()
{
  channels.clear();
}

//##ModelId=3E47C84502CD
void OctoEventMux::notify ()
{
  // notify signals on the event flag 
  eventFlag().raise(ef_channel_num);
}

//##ModelId=3E47CFA70203
void OctoEventMux::stop()
{
  // raise the event flag since we've stopped
  eventFlag().raise(ef_channel_num);
}

//##ModelId=3E535889025A
OctoChannel & OctoEventMux::newChannel ()
{
  OctoChannel * pchannel = new OctoChannel(*this,DMI::ANONWR);
  return *pchannel;
}

//##ModelId=3E428F93013E
OctoEventMux& OctoEventMux::addChannel (OctoChannel::Ref &channel)
{
  channel().setMultiplexId(channels.size());
  channels.push_back(channel);
  return *this;
}

//##ModelId=3E26BE760036
OctoEventMux&  OctoEventMux::addChannel (OctoChannel* channel,int flags)
{
  OctoChannel::Ref ref(channel,flags|DMI::WRITE);
  return addChannel(ref);
}

//##ModelId=3E428F70021D
OctoEventMux&  OctoEventMux::addChannel (OctoChannel& channel,int flags)
{
  OctoChannel::Ref ref(channel,flags|DMI::WRITE);
  return addChannel(ref);
}

//##ModelId=3E50E02C024B
void OctoEventMux::init()
{
  close();
}

//##ModelId=3E50E292002B
void OctoEventMux::close()
{
  pheadmsg = 0;
  assigned_data.detach();
}

//##ModelId=3E3FC3A7000B
int OctoEventMux::checkQueue (const HIID& mask,int wait,int channel_id)
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
      if( assigned_channel == channel_id && 
          ( mask.empty() || assigned_event.matches(mask) ) )
      {
        // remove message from queue -- assigned_event 
        // and assigned_data will contain the event
        cdebug(4)<<"cached message assigned to this channel ("<<channel_id<<"): SUCCESS\n";
        queue().pop_front();
        return SUCCESS;
      }
      cdebug(4)<<"cached message not assigned to this channel ("<<channel_id<<"): OUTOFSEQ\n";
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
      cdebug(4)<<"message queue is empty, clearing event flag #"<<channel_id<<"\n";
      // Since we've locked an empty queue, receive() above can't be called 
      // (since it's only ever called when something's in the queue to begin with)
      // First, clear our event flag bit
      eventFlag().clear(ef_channel_num);
      // Is there anything else in the event flag? must be someone else's event
      if( eventFlag().isRaised() )
      {
        if( wait == BLOCK ) // if blocking is requested, wait on our queue variable
        {
          cdebug(4)<<"other channels have pending events, BLOCKing on queue_cond\n";
          queueCondition().wait();
        }
        else // otherwise, return out-of-sequence
        {
          cdebug(4)<<"other channels have pending events: OUTOFSEQ\n";
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
    // check against input map of every channel
    bool assigned = false;
    for( uint i=0; i<channels.size(); i++ )
    {
      if( channels[i]().mapReceiveEvent(assigned_event,msg.id()) )
      {
        assigned = true;
        pheadmsg = &msg;
        assigned_channel = i;
        assigned_data = msg.payload();
        assigned_source = msg.from();
        cdebug(3)<<"maps to "<<channels[i]->sdebug(1)<<", event "<<assigned_event<<endl;
        if( i == uint(channel_id) )
        {
          if( mask.empty() || assigned_event.matches(mask) )
          {
            queue().pop_front();
            return SUCCESS;
          }
          else if( wait != AppEvent::BLOCK ) // message for this channel, doesn't match
            return OUTOFSEQ;
        }
        else if( wait != AppEvent::BLOCK ) // message for other channel
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
      // the message has not been assigned to any channel.
      // Discard it and go back for another try
      cdebug(3)<<"unmapped message, discarding\n";
      queue().pop_front();
      // go back for another try
    }
  }
}

//##ModelId=3E26D2D6021D
int OctoEventMux::getEvent (HIID& id,ObjRef& data,const HIID& mask,int wait,HIID &source,int channel_id)
{
  // check the queue
  int res = checkQueue(mask,wait,channel_id);
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
int OctoEventMux::hasEvent (const HIID& mask,HIID &out,int channel_id)
{
  int res = checkQueue(mask,NOWAIT,channel_id);
  if( res == SUCCESS )
    out = assigned_event;
  return res;
}


string OctoEventMux::sdebug (int detail, const string &prefix, const char *name) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s/%p",name?name:"OctoEventMux",this);
  }
  if( detail >= 1 || detail == -1 )
  {
    appendf(out,"channels:%d",channels.size());
    appendf(out,"wp:%s",WorkProcess::sdebug(abs(detail),prefix).c_str());
  }
  return out;
}

};

