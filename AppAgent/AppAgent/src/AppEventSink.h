//  AppEventSink.h: abstract interface for an event agent
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

#ifndef _APPAGENT_APPEVENTSINK_H
#define _APPAGENT_APPEVENTSINK_H 1

#include <AppAgent/AppAgent.h>
#include <AppAgent/AppEventFlag.h>
  
#pragma aidgroup AppAgent
#pragma aid AppAgent Event Text

namespace AppEvent
{
  //##ModelId=3E40FE3E03B7
  //##Documentation
  //## This defines the return codes for the getEvent/hasEvent methods,
  //## as well as wait-states, etc.
  typedef enum {
    SUCCESS   = 1,
    WAIT      = 0,      // no event pending, must wait
    OUTOFSEQ  = -1,     // request is out of sequence (see below)
    CLOSED    = -2,     // event stream is closed or disconnected
    ERROR     = -999,   // generic error code

    // defines values for the wait argument to getEvent() below
    // WAIT=0 already defined above
    NOWAIT    = -1,   
    BLOCK     = 1

  } EventCodes;
};

namespace AppEventSinkVocabulary
{
};
  
//##ModelId=3E394D4C0195
//##Documentation
//## AppAgent is an abstract interface class for an "application agent". An
//## agent sits between an application and a data source or sink. The AppAgent
//## interface hides the details of a particular data source: it can be a
//## measurement set, a pipeline, a test file, etc.
//## 
//## Agents talk to an application by exchanging events. Each event has an id
//## (a HIID), and can contain an arbitrary DataRecord.
class AppEventSink : public AppAgent
{
  public:
    //##ModelId=3E410DB50060
    DefineRefTypes(AppEventSink,Ref);
  
    //##ModelId=3E4100E40257
    explicit AppEventSink (const HIID &initf);
    
    //##ModelId=3E4784B1021A
    AppEventSink (const HIID &initf, AppEventFlag &evflag);
    
    //##ModelId=3E4787070046
    void attach (AppEventFlag& evflag,int dmiflags = DMI::WRITE);
    
    //##ModelId=3E4143B200F2
    //##Documentation
    //## Agent initialization method. Called by the application to initialize
    //## or reinitialize an agent. Agent parameters are supplied via a
    //## DataRecord.
    virtual bool init(const DataRecord &data);
  
    //##ModelId=3E394D4C02BB
    //##Documentation
    //## Requests the next event from an agent. The event's id and data object
    //## are returned via the first two parameters. 
    //## If mask is non-empty, then only events matching that mask are
    //## returned; a non-matching event produces an OUTOFSEQ return code.
    //## Defined return codes:
    //##   SUCCESS (=1):   successfully returned a matching event
    //##   WAIT (=0):      no events pending, must wait
    //##   OUTOFSEQ (=-1): mask specified, and pending event does not match it
    //##   CLOSED (=-2):   event stream has been closed
    //## 
    //## If no [matching] event is currently pending, the agent must do one 
    //## of three things, depending on the value of wait:
    //##   NOWAIT:  return immediately with WAIT or OUTOFSEQ.
    //##   WAIT:    block and wait for any event to arrive. If a non-matching
    //##            event arrives, return OUTOFSEQ. Only SUCCESS, OUTOFSEQ or
    //##            CLOSED may be returned.
    //##   BLOCK:   block and wait for a matching event to arrive. If a
    //##            non-matching event arrives (or was pending to begin with),
    //##            keep waiting for matching events. Only SUCCESS or CLOSED
    //##            CLOSED may be returned.
    //##            Note that the agent must have some sort of priority-based
    //##            event queue, otherwise waiting for a matching event
    //##            could be indefinitely blocked by a non-matching one.
    //##            In this case, an exception should be thrown (instead of
    //##            waiting forever).
      virtual int getEvent (HIID &id,ObjRef &data,const HIID &mask,int wait = AppEvent::WAIT);

    //##ModelId=3E394D4C02C1
    //##Documentation
    //## Returns True if there is an event pending that matches the specified
    //## mask (default - no mask - matches any event). 
    //## Return codes are the same as would have been returned by
    //## getEvent(wait=NOWAIT), above.
      virtual int hasEvent (const HIID &mask = HIID()) const;

    //##ModelId=3E394D4C02C9
    //##Documentation
    //## Posts an event on behalf of the application.
      virtual void postEvent (const HIID &id, const ObjRef::Xfer &data = ObjRef());

    //##ModelId=3E394D4C02D7
    //##Documentation
    //## Flushes any output events (commits to disk, or sends out to OCTOPUSSY,
    //## or whatever)
      virtual void flush ();
      
      //##ModelId=3E47843B0350
      void raiseEventFlag  ();
      //##ModelId=3E47844701DE
      void clearEventFlag ();
      
      //##ModelId=3E47852A012C
      virtual bool isAsynchronous() const
      { return False; }
      
    //##ModelId=3E4790150278
      int waitOtherEvents (int wait) const;
          
    //##ModelId=3E3E744E0258
      int getEvent (HIID &id, DataRecord::Ref &data, const HIID &mask, int wait = AppEvent::WAIT);

    //##ModelId=3E3E747A0120
      void postEvent (const HIID &id, const DataRecord::Ref::Xfer & data);
      
    //##ModelId=3E3FD6180308
      void postEvent (const HIID &id, const string &text);
    
    //##ModelId=3E394D4C02D9
    //##Documentation
    //## Alias for getEvent() with an empty mask, which retrieves the next
    //## pending event whatever it is.
      int getEvent(HIID &id, ObjRef &data, int wait = AppEvent::WAIT)
      { return getEvent(id,data,HIID(),wait); }
      
    //##ModelId=3E3E74620245
      int getEvent(HIID &id, DataRecord::Ref &data, int wait = AppEvent::WAIT)
      { return getEvent(id,data,HIID(),wait); }
      
    //##ModelId=3E394D4C02DE
      virtual string sdebug ( int detail = 1,const string &prefix = "",
                              const char *name = 0 ) const
      { return "NullEventSink"; }


  private:
    //##ModelId=3E43E3B30155
    AppEventFlag::Ref eventFlag;
    //##ModelId=3E47837F02C2
    int sink_num;


};
    
    
#endif
    
