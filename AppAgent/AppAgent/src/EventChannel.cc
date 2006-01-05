//  EventChannel.cc: abstract interface for an event agent
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

#include "EventChannel.h"
#include "AID-AppAgent.h"

namespace AppAgent
{    

// const AtomicID AppEvent::EventCategories[] = { AidNormal,AidNotify,AidWarning,AidError,AidCritical,AidInfo,AidDebug };

using namespace AppEvent;
using namespace EventChannelVocabulary;


HIID EventChannel::_dummy_hiid;

//##ModelId=3E4100E40257
EventChannel::EventChannel ()
  : state_(OPEN)
{
}

//##ModelId=3E4784B1021A
EventChannel::EventChannel (EventFlag &evflag)
  : state_(OPEN)
{
  attach(evflag);
}

//##ModelId=3E4787070046
void EventChannel::attach (EventFlag& evflag)
{
  if( event_flag_.valid() ) // can't attach more than one
  {
    FailWhen( event_flag_.deref_p() != &evflag,"channel already has an EventFlag attached");
    return;
  }
  event_flag_.attach(evflag,DMI::SHARED|DMI::WRITE);
  channel_num_ = evflag.addSource(isAsynchronous());
}


//##ModelId=3E4143B200F2
int EventChannel::init (const DMI::Record &params)
{
  close();
  string infile = params[FRecordInput].as<string>("");
  if( !infile.empty() )
    record_input_.open(infile,BOIO::WRITE);
  string outfile = params[FRecordOutput].as<string>("");
  if( !outfile.empty() )
    record_output_.open(outfile,BOIO::WRITE);
  return setState(OPEN);
}

void EventChannel::close (const string &str)
{
  record_output_.close();
  record_input_.close();
  setState(CLOSED,str);
}
    
//##ModelId=3E394D4C02BB
int EventChannel::getEvent (HIID &,ObjRef &,const HIID &,int wait,HIID &)
{ 
  return waitOnFlag(wait);
}

//##ModelId=3E394D4C02C1
int EventChannel::hasEvent (const HIID &,HIID &) 
{ 
  // if we have an event flag and it's raised, this means some other channel
  // has an event pending. In this case return OUTOFSEQ
  return event_flag_.valid() && event_flag_->isRaised() 
         ? OUTOFSEQ 
  // otherwise, since we don't generate any events here, simply return WAIT
         : WAIT; 
}

void EventChannel::recordEvent (BOIO &boio,const HIID &id,
                    const ObjRef &data,AtomicID category,const HIID &addr) const
{
  cdebug(3)<<"storing event "<<id<<endl;
  ObjRef recref;
  DMI::Record & rec = * new DMI::Record;
  recref.attach(rec,DMI::ANONWR);
  rec[AidEvent] = id;
  rec[AidAddress] = addr;
  rec[AidCategory] = category;
  if( data.valid() )
    rec[AidData] = data.copy();
  boio << recref;
}

//##ModelId=3E394D4C02C9
void EventChannel::postEvent (const HIID &id, const ObjRef &ref,AtomicID category,const HIID &source)
{
  recordOutputEvent(id,ref,category,source);
}

void EventChannel::flush ()
{
}

//##ModelId=3E3E744E0258
int EventChannel::getEvent (HIID &id, DMI::Record::Ref &data, 
                            const HIID &mask,int wait,HIID &source)
{
  ObjRef ref;
  int res = getEvent(id,ref,mask,wait,source);
  if( res == SUCCESS && ref.valid() )
    data.xfer(ref.ref_cast<DMI::Record>());
  return res;
}

//##ModelId=3E47843B0350
void EventChannel::raiseEventFlag() const
{
  if( event_flag_.valid() )
    event_flag_().raise(channel_num_);
}

//##ModelId=3E47844701DE
void EventChannel::clearEventFlag() const
{
  if( event_flag_.valid() )
    event_flag_().clear(channel_num_);
}

//##ModelId=3E4790150278
int EventChannel::waitOnFlag (int wait) const
{
  if( wait == WAIT )
  {
    // if we have an event flag, then we can wait on it and return an 
    // out-of-sequence error when an event arrives for another channel.
    // If there are no channels around capable of generating asyncronous events,
    // EventFlag::wait() will return false
    FailWhen(!event_flag_.valid() || !event_flag_->wait(),
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

//##ModelId=3E8C1F8703DC
bool EventChannel::isEventBound (const HIID &,AtomicID)
{
  return false;
}

//##ModelId=3E8C3BDC0159
void EventChannel::solicitEvent (const HIID &)
{
}

};
