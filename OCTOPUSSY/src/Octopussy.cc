#include <Common/Debug.h>
#include "Dispatcher.h"
#include "Gateways.h"
#include "LoggerWP.h"

namespace Octopussy
{

Dispatcher *pdsp = 0;

Thread::ThrID thread = 0;
  
        
bool isRunning ()
{
  return pdsp != 0;
}

Dispatcher &  init     (bool start_gateways=True)
{
  FailWhen( pdsp,"OCTOPUSSY already initialized" );
  pdsp = new Dispatcher;
  pdsp->attach(new LoggerWP(10,Message::LOCAL),DMI::ANON);
  if( start_gateways )
    initGateways(*pdsp);
  return *pdsp;
}

void          start    ()
{
  FailWhen( !pdsp,"OCTOPUSSY not initialized" );
  pdsp->start();
  
}

void          stop     ()
{
  FailWhen( !pdsp,"OCTOPUSSY not initialized" );
  pdsp->stop();
}

void          pollLoop ()
{
  FailWhen( !pdsp,"OCTOPUSSY not initialized" );
  pdsp->pollLoop();
}

void          destroy  ()
{
  FailWhen( !pdsp,"OCTOPUSSY not initialized" );
  delete pdsp;
  pdsp = 0;
}


Thread::ThrID  initThread (bool wait_for_start)
{
#ifndef USE_THREADS
  Throw("OCTOPUSSY was built w/o thread support");
#else
  if( !pdsp )
    init();
  return thread = pdsp->startThread(wait_for_start);
#endif
}

void           stopThread  ()
{
#ifndef USE_THREADS
  Throw("OCTOPUSSY was built w/o thread support");
#else
  stop();
#endif
}

Thread::ThrID  threadId    ()
{
  return thread;
}

Dispatcher &   dispatcher  ()
{
  return *pdsp;
}

};
