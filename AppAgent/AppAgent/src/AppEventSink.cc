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

namespace AppAgent
{    

// const AtomicID AppEvent::EventCategories[] = { AidNormal,AidNotify,AidWarning,AidError,AidCritical,AidInfo,AidDebug };

using namespace AppEvent;
using namespace AppEventSinkVocabulary;


DefineRegistry(AppEventSink,0);


//##ModelId=3F5F43630252
HIID AppEventSink::_dummy_hiid;

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
  eventFlag.attach(evflag,dmiflags|DMI::SHARED|DMI::WRITE);
  sink_num = evflag.addSource(isAsynchronous());
}


//##ModelId=3E4143B200F2
bool AppEventSink::init (const DMI::Record &params)
{
  close();
  string infile = params[FRecordInput].as<string>("");
  if( !infile.empty() )
    record_input.open(infile,BOIO::WRITE);
  string outfile = params[FRecordOutput].as<string>("");
  if( !outfile.empty() )
    record_output.open(outfile,BOIO::WRITE);
  return true;
}

void AppEventSink::close ()
{
  record_output.close();
  record_input.close();
}
    
//##ModelId=3E394D4C02BB
int AppEventSink::getEvent (HIID &id,ObjRef &ref,const HIID &mask,int wait,HIID &source)
{ 
  return waitOtherEvents(wait);
}

//##ModelId=3E394D4C02C1
int AppEventSink::hasEvent (const HIID &mask,HIID &out) const
{ 
  // if we have an event flag and it's raised, this means some other sink
  // has an event pending. In this case return OUTOFSEQ
  return eventFlag.valid() && eventFlag->isRaised() 
         ? OUTOFSEQ 
  // otherwise, since we don't generate any events here, simply return WAIT
         : WAIT; 
}

void AppEventSink::recordEvent (BOIO &boio,const HIID &id, const ObjRef &data,AtomicID cat,const HIID &addr) const
{
  cdebug(3)<<"storing event "<<id<<endl;
  ObjRef recref;
  DMI::Record & rec = * new DMI::Record;
  recref.attach(rec,DMI::ANONWR);
  rec[AidEvent] = id;
  rec[AidCategory] = cat;
  rec[AidAddress] = addr;
  if( data.valid() )
    rec[AidData] = data.copy();
  boio << recref;
}

//##ModelId=3E394D4C02C9
void AppEventSink::postEvent (const HIID &id, const ObjRef &ref,AtomicID cat,const HIID &source)
{
  recordOutputEvent(id,ref,cat,source);
}

void AppEventSink::flush ()
{
}

//##ModelId=3E3E744E0258
int AppEventSink::getEvent (HIID &id, DMI::Record::Ref &data, 
                            const HIID &mask,int wait,HIID &source)
{
  ObjRef ref;
  int res = getEvent(id,ref,mask,wait,source);
  if( res == SUCCESS && ref.valid() )
    data = ref.ref_cast<DMI::Record>();
  return res;
}

//##ModelId=3E3E747A0120
void AppEventSink::postEvent (const HIID &id, const DMI::Record::Ref &data,
                              AtomicID cat,const HIID &destination)
{
  if( data.valid() )
    postEvent(id,data.ref_cast<DMI::BObj>(),cat,destination);
  else
    postEvent(id,ObjRef(),cat,destination);
}

//##ModelId=3E3FD6180308
void AppEventSink::postEvent (const HIID &id, const string &text,
                              AtomicID cat,const HIID &destination)
{
  DMI::Record::Ref ref;
  ref <<= new DMI::Record;
  ref()[AidText] = text;
  postEvent(id,ref,cat,destination);
}

//##ModelId=3E47843B0350
void AppEventSink::raiseEventFlag() const
{
  if( eventFlag.valid() )
    eventFlag().raise(sink_num);
}

//##ModelId=3E47844701DE
void AppEventSink::clearEventFlag() const
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
    // AppEventFlag::wait() will return false
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
//##ModelId=3E8C1F8703DC
bool AppEventSink::isEventBound (const HIID &,AtomicID)
{
  return false;
}

//##ModelId=3E8C3BDC0159
void AppEventSink::solicitEvent (const HIID &)
{
}

};
