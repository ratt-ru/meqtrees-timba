#include <sys/time.h> 
#include <sys/types.h> 
#include <unistd.h> 
#include <aips/Glish.h>
#include <aips/Arrays/Array.h>
#include <aips/Arrays/ArrayMath.h>

#include <DMI/DataRecord.h>
#include <DMI/DataField.h>
#include <DMI/DataArray.h>
#include <DMI/Global-Registry.h>

#include "GlishThreadWP.h"

static int dum = aidRegistry_OCTOGlish();
static int dum2 = aidRegistry_Global();


// Class GlishThreadedClientWP 

GlishThreadedClientWP::GlishThreadedClientWP (
    GlishSysEventSource *dest,GlishSysEventSource *spig,
    bool autostp, AtomicID wpc)
 : GlishClientWP(dest,autostp,wpc),
  evspigot(spig)
{
  setConnected( isConnected() && evspigot->connected() );
  rcv_thread_ = 0;
}


GlishThreadedClientWP::~GlishThreadedClientWP()
{
  if( evspigot )
    delete evspigot;
}

void GlishThreadedClientWP::init ()
{
  GlishClientWP::init();
}

void * GlishThreadedClientWP::start_receiveThread (void *pwp)
{
  return static_cast<GlishThreadedClientWP*>(pwp)->receiveThread();
}

bool GlishThreadedClientWP::start ()
{
  // do not start the client, start our own event reading thread instead
  rcv_thread_ = Thread::create(start_receiveThread,this);
  return False;
}

void GlishThreadedClientWP::stop ()
{
  if( rcv_thread_ )
  {
    cdebug(2)<<"cancelling receive thread\n"<<endl;
    rcv_thread_.cancel();
    cdebug(2)<<"sending INT to receive thread\n"<<endl;
    rcv_thread_.kill(SIGINT);
    cdebug(2)<<"rejoining receive thread\n"<<endl;
    rcv_thread_.join();
  }
}

void * GlishThreadedClientWP::receiveThread ()
{
  // loop indefinitely while connected
  while( eventSpigot().connected() )
  {
    GlishSysEvent event;
    // handle any incoming events; timeout every .5 sec to check
    // for thread cancellations
    if( eventSpigot().nextGlishEvent(event,500) )
    {
      dprintf(4)("got Glish event, handling it\n");
      GlishValue result = handleEvent(event);
      if( eventSpigot().replyPending() )
        eventSpigot().reply(result);
    }
    Thread::testCancel();
  }
  // drop here if we get disconnected from Glish
  setConnected(false);
  dprintf(1)("disconnected from Glish process\n");
  if( isAttached() )
    shutdown();
  // exit the thread
  Thread::exit();
  return 0;
}

