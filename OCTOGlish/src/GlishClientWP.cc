#include <sys/time.h> 
#include <sys/types.h> 
#include <unistd.h> 
#include <tasking/Glish.h>
#include <casa/Arrays/Array.h>
#include <casa/Arrays/ArrayMath.h>

#include <DMI/DataRecord.h>
#include <DMI/DataField.h>
#include <DMI/DataArray.h>
#include <DMI/Global-Registry.h>

#include "GlishClientWP.h"
#include <Common/BlitzToAips.h>
#include "GlishUtil.h"

static int dum = aidRegistry_OCTOGlish();
static int dum2 = aidRegistry_Global();


// Class GlishClientWP 

//##ModelId=3CB562BB0226
//##ModelId=3DB9369503DE
//##ModelId=3DB9369600AA
GlishClientWP::GlishClientWP (GlishSysEventSource *src, bool autostp, AtomicID wpc)
  : WorkProcess(wpc),evsrc(src),autostop_(autostp)
{
  connected = evsrc->connected();
  has_events = False;
}


//##ModelId=3DB9369201C7
GlishClientWP::~GlishClientWP()
{
  if( evsrc )
    delete evsrc;
}

//##ModelId=3E9BD6E900D3
void GlishClientWP::init ()
{
//  dprintf(2)("init: waiting for glish start event\n");
  glish_started = False;
//  while( !glish_started )
//  {
//    GlishSysEvent event = evsrc->nextGlishEvent();
//    handleEvent(event);
//  }
  dprintf(2)("init complete\n");
}

//##ModelId=3E9BD6E900DD
GlishValue GlishClientWP::handleEvent (GlishSysEvent &event)
{
  dprintf(2)("got event '%s'\n", event.type().c_str());
  Bool result = True;       // AIPS++ Bool for event result

  if( event.type() == "shutdown" ) // shutdown event
  {
    shutdown();
  }
  else 
  {
    try // catch all event processing exceptions
    {
      // all other events must carry a GlishRecord
      // FailWhen(event.valType() != GlishValue::RECORD,"event value not a record");
      // get the record out and process stuff
      GlishValue val = event.val();
      GlishArray tmp;
      if( event.type() == "start" )
      {
        FailWhen( glish_started,"unexpected start event" );
        glish_started = True;
      }
      else if( event.type() == "subscribe" )
      {
        GlishRecord rec = val;
        FailWhen( rec.nelements() != 2,"illegal event value" );
        String idstr; int scope;
        tmp = rec.get(0); tmp.get(idstr);
        tmp = rec.get(1); tmp.get(scope);
        HIID id(idstr);
        FailWhen( !id.size(),"null HIID in subscribe" );
        subscribe(id,scope);
      }
      else if( event.type() == "unsubscribe" )
      {
        GlishRecord rec = val;
        FailWhen( rec.nelements() != 1,"illegal event value" );
        String idstr; 
        tmp = rec.get(0); tmp.get(idstr);
        HIID id(idstr);
        FailWhen( !id.size(),"null HIID in unsubscribe" );
        unsubscribe(id);
      }
      else if( event.type() == "send" )
      {
        FailWhen(!glish_started,"got send event before start event");
        String tostr; 
        FailWhen(!val.attributeExists("to"),"missing 'to' attribute");
        tmp = val.getAttribute("to"); tmp.get(tostr);
        HIID to(tostr);
        FailWhen(!to.size(),"bad 'to' attribute");
        AtomicID wpi,process=AidLocal,host=AidLocal;
        if( to.size() > 1 )  wpi = to[1];
        if( to.size() > 2 )  process = to[2];
        if( to.size() > 3 )  host = to[3];
        MessageRef ref = glishValueToMessage(val);
        setState(ref->state());
        dprintf(4)("sending message: %s\n",ref->sdebug(10).c_str());
        send(ref,MsgAddress(to[0],wpi,process,host));
      }
      else if( event.type() == "publish" )
      {
        FailWhen(!glish_started,"got publish event before start event");
        int scope;
        FailWhen( !val.attributeExists("scope"),"missing 'scope' attribute");
        tmp = val.getAttribute("scope"); tmp.get(scope);
        MessageRef ref = glishValueToMessage(val);
        setState(ref->state());
        dprintf(4)("publishing message: %s\n",ref->sdebug(10).c_str());
        publish(ref,scope);
      }
      else if( event.type() == "log" )
      {
        GlishRecord rec = val;
        FailWhen(!glish_started,"got log event before start event");
        FailWhen( rec.nelements() != 3,"illegal event value" );
        String msg,typestr; int level;
        tmp = rec.get(0); tmp.get(msg);
        tmp = rec.get(1); tmp.get(level);
        tmp = rec.get(2); tmp.get(typestr);
        AtomicID type(typestr);
        log(msg,level,type);
      }
      else if( event.type() == "debug" )
      {
        GlishRecord rec = val;
        FailWhen( rec.nelements() != 2,"illegal event value" );
        Array<String> contexts; int level;
        tmp = rec.get(0); tmp.get(contexts);
        tmp = rec.get(1); tmp.get(level);
        for( Array<String>::const_iterator iter = contexts.begin();
            iter != contexts.end(); iter++ )
          Debug::setLevel(*iter,level);
      }
      else
        Throw("unknown event");
    } // end try 
    catch ( std::exception &exc ) 
    {
      dprintf(1)("exception processing glish event, ignoring: %s\n",exc.what());
      result = False;
    }
    catch ( ... ) 
    {
      dprintf(1)("unknown exception processing glish event\n");
      result = False;
    }
  }
  return GlishArray(result);
}

//##ModelId=3CBA97E70232
bool GlishClientWP::start ()
{
  fd_set fdset;
  FD_ZERO(&fdset);
  if( evsrc->addInputMask(&fdset) )
  {
    for( int fd=0; fd<FD_SETSIZE; fd++ )
      if( FD_ISSET(fd,&fdset) )
      {
        dprintf(2)("adding input for fd %d\n",fd);
        addInput(fd,EV_FDREAD);
      }
  }
  else
  {
    dprintf(2)("no input fds indicated by GlishEventSource\n");
  }
  // add a timeout to keep checking for connectedness
  addTimeout(2.0,HIID(),EV_CONT);
  
  return False;
}

//##ModelId=3CBABEA10165
void GlishClientWP::stop ()
{
//  if( evsrc && connected )
//    evsrc->postEvent("//exit",GlishValue());
}

//##ModelId=3CBACB920259
int GlishClientWP::input (int , int )
{
  if( !evsrc->connected() )
  {
    // got disconnected?
    if( connected )
      dprintf(1)("disconnected from Glish process\n");
    shutdown();
  }
  else
  {
    GlishSysEvent event;
    // The event loop
    // loop until the max # of events is reached, or no more events
    for( int i=0; i < MaxEventsPerPoll && connected; i++ )
      if( !evsrc->nextGlishEvent(event,0) )
      {
        has_events=False; // no events? reset flag and exit
        break;
      }
      else   // else process the event
      {
        GlishValue result = handleEvent(event);
        if( evsrc->replyPending() )
          evsrc->reply(result);
      } // end of event loop
  }
  return Message::ACCEPT;
}

//##ModelId=3CBACFC6013D
int GlishClientWP::timeout (const HIID &)
{
  // fake an input all to check for connectedness, etc.
  return input(0,0);
}

//##ModelId=3CB5622B01ED
int GlishClientWP::receive (MessageRef &mref)
{
  // if no connection, then just ignore it
  if( !evsrc->connected() )
  {
    dprintf(2)("not connected, ignoring [%s]\n",mref->sdebug(1).c_str());
    return Message::ACCEPT;
  }
  // wrap the message into a value and post it
  GlishValue value = messageToGlishValue(mref.deref());
  string ev = strlowercase(mref->id().toString('_'));
  evsrc->postEvent(ev.c_str(),value);
  
  return Message::ACCEPT;
}

//##ModelId=3E9BD6E900D5
// Converts a Message to a GlishValue
// (The payload is converted to a GlishValue, while message attributes
// are passed as attributes) 
GlishValue GlishClientWP::messageToGlishValue (const Message &msg)
{
  // default value is empty record
  GlishValue value = GlishRecord();
  // convert payload, if any
  if( msg.payload().valid() )
  {
    value = GlishUtil::objectToGlishValue( *(msg.payload()),False );
    TypeId tid = msg.payload()->objectType();
    value.addAttribute("payload",GlishArray(tid.toString()));
  }
  // add data block, if any
  if( msg.block().valid() )
  {
    size_t sz = msg.datasize();
    value.addAttribute("datasize",GlishArray((int)sz));
    if( sz )
      value.addAttribute("data",GlishArray(Array<uChar>(IPosition(1,sz),
		static_cast<uChar*>(const_cast<void*>(msg.data())),COPY)));
  }
  // add message attributes
  value.addAttribute("id",GlishArray(msg.id().toString()));
  value.addAttribute("to",GlishArray(msg.id().toString()));
  value.addAttribute("from",GlishArray(msg.from().toString()));
  value.addAttribute("priority",GlishArray(msg.priority()));
  value.addAttribute("state",GlishArray(msg.state()));
  
  return value;
}

//##ModelId=3E9BD6E900D9
MessageRef GlishClientWP::glishValueToMessage (const GlishValue &value)
{
  // get message attributes
  FailWhen( !value.attributeExists("id") ||
            !value.attributeExists("priority"),"missing 'id' or 'priority' attribute");
  String idstr; 
  int priority,state=0;
  GlishArray tmp;
  tmp = value.getAttribute("id"); tmp.get(idstr);
  tmp = value.getAttribute("priority"); tmp.get(priority);
  if( value.attributeExists("state") )
  {
    tmp = value.getAttribute("state"); tmp.get(state);
  }
  // setup message & ref
  HIID id(idstr);
  Message &msg = *new Message(id,priority);
  MessageRef ref(msg,DMI::ANON|DMI::WRITE);
  ref().setState(state);
  // do we have a payload?
  if( value.attributeExists("payload") )
  {
    String typestr; 
    tmp = value.getAttribute("payload"); tmp.get(typestr);
    msg <<= GlishUtil::glishValueToObject(value,False);
  }
  // do we have a data block as well?
  if( value.attributeExists("datablock") )
  {
    Array<uChar> data;
    tmp = value.getAttribute("datablock"); tmp.get(data);
    size_t sz = data.nelements();
    SmartBlock *block = new SmartBlock(sz);
    msg <<= block;
    if( sz )
    {
      bool del;
      const uChar *pdata = data.getStorage(del);
      memcpy(block->data(),pdata,sz);
      data.freeStorage(pdata,del);
    }
  }
  return ref;
}

//##ModelId=3DB9369900E1
void GlishClientWP::shutdown ()
{
  dprintf(1)("shutting down\n");
  connected = False;
  setState(-1);
  removeInput(-1);
  removeTimeout("*");
  if( autostop() )
  {
    dprintf(1)("autostop is on: stopping the system\n");
    dsp()->stopPolling();
  }
  else
  {
    dprintf(1)("detaching\n");
    detachMyself();
  }
}

GlishClientWP * makeGlishClientWP (int argc,const char *argv[],bool autostop )
{
  // stupid glish wants non-const argv
  GlishSysEventSource *evsrc = 
      new GlishSysEventSource(argc,const_cast<char**>(argv));
  AtomicID wpc = AidGlishClientWP;
  // scan arguments for an override
  string wpcstr;
  for( int i=1; i<argc; i++ )
  {
    if( string(argv[i]) == "-wpc" && i < argc-1 )
    {
      wpcstr = argv[i+1];
      break;
    }
  }
  if( wpcstr.length() )
    wpc = AtomicID(wpcstr);
  
  return new GlishClientWP(evsrc,autostop,wpc);
}


