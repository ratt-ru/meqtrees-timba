//  AppEventSink.cc: abstract interface for an event agent
//
//  Copyright (C) 2002
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//
//  This program is free software; you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation; either version 2 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//  $Id$

#include "AppEventSink.h"
#include "AID-AppAgent.h"

using namespace AppEvent;

//##ModelId=3E4100E40257
AppEventSink::AppEventSink (const HIID &initf)
  : AppAgent(initf)
{
}

//##ModelId=3E4784B1021A
AppEventSink::AppEventSink(const HIID &initf, AppEventFlag &evflag)
  : AppAgent(initf)
{
  attach(evflag);
}

//##ModelId=3E4787070046
void AppEventSink::attach (AppEventFlag& evflag,int dmiflags)
{
  if( eventFlag.valid() ) // can't attach more than one
  {
    FailWhen( eventFlag.deref_p() != &evflag,"sink already has an AppEventFlag attached");
    return;
  }
  eventFlag.attach(evflag,dmiflags|DMI::WRITE);
  sink_num = evflag.addSource(isAsynchronous());
}


//##ModelId=3E4143B200F2
bool AppEventSink::init (const DataRecord &)
{
  return True;
}
    
//##ModelId=3E394D4C02BB
int AppEventSink::getEvent (HIID &,ObjRef &,const HIID &,int wait)
{ 
  return waitOtherEvents(wait);
}

//##ModelId=3E394D4C02C1
int AppEventSink::hasEvent (const HIID &) const
{ 
  // if we have an event flag and it's raised, this means some other sink
  // has an event pending. In this case return OUTOFSEQ
  return eventFlag.valid() && eventFlag->isRaised() 
         ? OUTOFSEQ 
  // otherwise, since we don't generate any events here, simply return WAIT
         : WAIT; 
}

//##ModelId=3E394D4C02C9
void AppEventSink::postEvent (const HIID &, const ObjRef::Xfer &ref)
{
  // this is OK since we're meant to xfer the ref anyway
  const_cast<ObjRef&>(ref).detach();
}

void AppEventSink::flush ()
{
}

//##ModelId=3E3E744E0258
int AppEventSink::getEvent (HIID &id, DataRecord::Ref &data, const HIID &mask, int wait)
{
  ObjRef ref;
  int res = getEvent(id,ref,mask,wait);
  if( res == SUCCESS && ref.valid() )
    data = ref.ref_cast<DataRecord>();
  return res;
}

//##ModelId=3E3E747A0120
void AppEventSink::postEvent (const HIID &id, const DataRecord::Ref::Xfer & data)
{
  if( data.valid() )
    postEvent(id,data.ref_cast<BlockableObject>());
  else
    postEvent(id);
}

//##ModelId=3E3FD6180308
void AppEventSink::postEvent (const HIID &id, const string &text)
{
  DataRecord::Ref ref;
  ref <<= new DataRecord;
  ref()[AidText] = text;
  postEvent(id,ref);
}

//##ModelId=3E47843B0350
void AppEventSink::raiseEventFlag()
{
  if( eventFlag.valid() )
    eventFlag().raise(sink_num);
}

//##ModelId=3E47844701DE
void AppEventSink::clearEventFlag()
{
  if( eventFlag.valid() )
    eventFlag().clear(sink_num);
}

//##ModelId=3E4790150278
int AppEventSink::waitOtherEvents (int wait) const
{
  if( wait == WAIT )
  {
    // if we have an event flag, then we can wait on it and return an 
    // out-of-sequence error when an event arrives for another sink.
    // If there are no sinks around capable of generating asyncronous events,
    // AppEventFlag::wait() will return False
    FailWhen(!eventFlag.valid() || !eventFlag->wait(),
        "waiting for an event here would block indefinitely");
    return OUTOFSEQ;
  }
  else if( wait == BLOCK )
  {
    // boo-boo, can't block here since we never get an event to unblock us...
    Throw("blocking for an event here would block indefinitely");
  }
  else
    return WAIT;
}
