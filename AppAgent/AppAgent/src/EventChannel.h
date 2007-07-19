//  EventChannel.h: abstract interface for an event channel
//
//  Copyright (C) 2002-2007
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  and The MeqTree Foundation
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

#ifndef _APPAGENT_EVENTCHANNEL_H
#define _APPAGENT_EVENTCHANNEL_H 1

#include <AppAgent/EventFlag.h>
#include <AppAgent/AID-AppAgent.h>
#include <DMI/BOIO.h>
#include <DMI/Record.h>
  
#pragma aidgroup AppAgent
#pragma aid AppAgent Event Text Category Destination Address
#pragma aid Normal Notify Warning Error Critical Info Debug
#pragma aid Record Input Output Channel Type Delete On Abort

namespace AppAgent
{    

namespace AppEvent
{
  //##ModelId=3E8C1A5B0043
  //##Documentation
  //## This defines the return codes for the getEvent/hasEvent methods,
  //## as well as wait-states, etc.
  typedef enum {
    SUCCESS   = 1,
    WAIT      = 0,      // no event pending, must wait
    CLOSED    = -1,     // event stream is closed or disconnected (already defined above)
    OUTOFSEQ  = -2,     // request is out of sequence (see below)
    ERROR     = -999,   // generic error code

    // defines values for the wait argument to getEvent() below
    // WAIT=0 already defined above
    NOWAIT    = -1,   
    BLOCK     = 1

  } EventCodes;
};

namespace EventChannelVocabulary
{
  const HIID FChannel      = AidChannel;
  
  const HIID FRecordInput   = AidRecord|AidInput;
  const HIID FRecordOutput  = AidRecord|AidOutput;
  const HIID FDeleteOnAbort = AidDelete|AidOn|AidAbort;
};


// list of all known event categories
const AtomicID EventCategories[] =
      { AidNormal,AidNotify,AidWarning,AidError,AidCritical,AidInfo,AidDebug };

//##ModelId=3E394D4C0195
//##Documentation
//## EventChannel represents a r/w event channel.
//## An event is represented by a HIID id and an optional ObjRef holding 
//## event data (most often a DMI::Record).
//##
//## The default EventChannel acts like a null sink: it does not return any 
//## events, and swallows all events directed at it. It does have the capability
//## of recording all posted events to a BOIO file, and provides hooks for
//## subclasses to record their incoming/outgoing events as well.
//## Recording is enabled via the Record.Input and Record.Output fields of
//## the init record; these should be set to filenames.

class EventChannel : public SingularRefTarget
{
  public:
    //##ModelId=3E410DB50060
    DefineRefTypes(EventChannel,Ref);
  
    typedef enum {
      OPEN      = 0,
      CLOSED    = -1,
    } ChannelStates;
  
    //##ModelId=3E4100E40257
    EventChannel ();
    
    //##ModelId=3E4784B1021A
    // Constructs with an event flag. Event flags may be required when
    // a single thread wants to poll multiple channels. In this case
    // the channels must share an event flag, so that when they are told
    // to wait for an event, they know to stop waiting if another channel
    // sharing the same flag has an event of its own.
    EventChannel (EventFlag &evflag);
    
    //##ModelId=3E4787070046
    // attaches an event flag
    void attach  (EventFlag & evflag);
    
    bool hasEventFlag () const
    { return event_flag_.valid(); }
    
    EventFlag::Ref eventFlagRef () const
    { return event_flag_.copy(); }
    
    EventFlag & eventFlag () const 
    { return event_flag_(); }
    
    // returns the channel number for this channel within the event flag
    int flagChannelNumber () const
    { return channel_num_; }
    
    //##ModelId=3E4143B200F2
    //##Documentation
    //## Agent initialization method. Called by the application to initialize
    //## or reinitialize an agent. Agent parameters are supplied via a
    //## DMI::Record.
    //## Recognized fields: 
    //##    Record.Input (string) filename for recording input events
    //##    Record.Output (string) filename for recording output events
    //## An exception will be thrown if the file cannot be opened for 
    //## writing.
    //## After a successful init the channel is in the OPEN state.
    //## Return value is channel state.
    virtual int init (const DMI::Record &data);
    
    //## closes the agent. Sets its state to CLOSED and closes recording
    //## files, if any. If str is supplied, the state string is set
    virtual void close (const string &str = "");
    
    //## aborts the agent, intended to be used on error instead of close().
    //## Default implementation optionally deletes any recording files
    //## (if Delete.On.Abort was set, which is the default), then calls
    //## close().
    virtual void abort (const string &str = "");
    
    //## returns channel state, if <0 then channel is closed
    int state () const
    { return state_; }
    
    const string & stateString () const
    { return state_str_; }
  
    //##ModelId=3E8C3BDC0159
    //##Documentation
    //## Advertises the fact that an app is interested in a specific
    //## event or set of events (wildcards may be employed). Default version does
    //## nothing. Subclasses with explicit event filtering (e.g., those using
    //## publish/subscribe) will probably redefine this to something useful.
    virtual void solicitEvent (const HIID &mask);
    
    //##ModelId=3E394D4C02BB
    //##Documentation
    //## Requests the next event from an agent. The event's id and data object
    //## are returned via the first two parameters. 
    //## A HIID describing the event source is returned in the final argument,
    //## provided the event channel supports distinct event sources (see e.g. OctoAgents)
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
    //##            may be returned.
    //##            Note that the agent must have some sort of priority-based
    //##            event queue, otherwise waiting for a matching event
    //##            could be indefinitely blocked by a non-matching one.
    //##            In this case, an exception should be thrown (instead of
    //##            waiting forever).
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
    //## Flushes any output events (commits to disk, or sends out to OCTOPUSSY,
    //## or whatever)
      virtual void flush ();
      
      //##ModelId=3E47843B0350
      // raises the event flag. If the channel is waiting on the flag, it will be woken.
      void raiseEventFlag  () const;
      //##ModelId=3E47844701DE
      // clears the event flag. 
      void clearEventFlag () const;
      
      //##ModelId=3E47852A012C
      //## returns true if channel is capable of generating events asynchronously
      //## of the calling thread. OctoChannel for example is multithreaded,
      //## so it's asynchronous. Channels that read files, on the other hand,
      //## are not.
      virtual bool isAsynchronous() const
      { return false; }
      
    //##ModelId=3E4790150278
      //## alias for getEvent() which expects a DMI::Record payload.
      //## An exception will be thrown if the payload is a different type.
      int getEvent ( HIID &id,DMI::Record::Ref &data,const HIID &mask,
                     int wait = AppEvent::WAIT,
                     HIID &source = _dummy_hiid );
          
    //##ModelId=3E3E747A0120
    //##Documentation
    //## alias for postEvent to post a DMI::Record 
      void postEvent (const HIID &id,
                      const DMI::Record::Ref & data,
                      AtomicID category = AidNormal,
                      const HIID &destination = HIID())
      {
        if( data.valid() )
          postEvent(id,data.ref_cast<DMI::BObj>(),category,destination);
        else
          postEvent(id,ObjRef(),category,destination);
      }
      
    //##ModelId=3E394D4C02D9
    //##Documentation
    //## Alias for getEvent() with an empty mask, which retrieves the next
    //## pending event whatever it is.
      int getEvent(HIID &id, ObjRef &data, 
                   int wait = AppEvent::WAIT,HIID &source = _dummy_hiid)
      { return getEvent(id,data,HIID(),wait,source); }
      
    //##ModelId=3E3E74620245
    //##Documentation
    //## Alias for getEvent() with an empty mask, which retrieves the next
    //## pending event whatever it is, with a DMI::Record payload
    //## An exception will be thrown if the payload is a different type.
      int getEvent(HIID &id, DMI::Record::Ref &data, 
                   int wait = AppEvent::WAIT,HIID &source = _dummy_hiid)
      { return getEvent(id,data,HIID(),wait,source); }
      
    //##ModelId=3E394D4C02DE
      virtual string sdebug ( int = 1,const string & = "",
                              const char * = 0 ) const
      { return "NullEventChannel"; }
      
  protected:
    // sets the channel state
    int setState (int st,const string &str = "")
    { state_str_ = str; return state_ = st; }
      
    // helper method: waits on the event flag and returns if the flag is
    // raised for any other channel. A channel must call this when it has
    // no events to return.
    int waitOnFlag (int wait) const;
  
    // helper method: records input event to boio log
    void recordInputEvent (const HIID &id, const ObjRef &ref,const HIID &source) const
    {
      if( record_input_.isOpen() )
        recordEvent(record_input_,id,ref,AidNormal,source);
    }
    
    // helper method: records output event to boio log
    void recordOutputEvent (const HIID &id,const ObjRef &ref,AtomicID category,const HIID &dest) const
    {
      if( record_output_.isOpen() )
        recordEvent(record_output_,id,ref,category,dest);
    }
    
    //##ModelId=3F5F43630252
    static HIID     _dummy_hiid;     // non-static since not thread-safe
        
  private:
    // helper function, records event on given BOIO object
    void recordEvent (BOIO &boio,const HIID &id, const ObjRef &ref,AtomicID category,const HIID &addr) const;

    // helper function for close(), renames recording file or throws an exception
    void renameRecording (const string &from,const string &to);
    
    //##ModelId=3E43E3B30155
    mutable EventFlag::Ref event_flag_;
  
    // all I/O events are optionally recorded (see init())
    mutable BOIO record_input_;
    mutable BOIO record_output_;
    
    // filenames to record to. Initially recorded to tmp files,
    // renamed on successful close(), deleted on abort().
    string record_input_filename_;
    string record_output_filename_;
    
    // flag: recording files deleted on abort
    bool delete_on_abort_;
  
    //##ModelId=3E47837F02C2
    // channel number within the event flag
    int channel_num_;
    
    int state_;
    
    string state_str_;
};
    
};    
#endif
    
