#ifndef OCTOPUSSY_OCTOPUSSY_H 
#define OCTOPUSSY_OCTOPUSSY_H 1

#include <Common/Thread.h>
    
class Dispatcher;    

namespace Octopussy
{
  Dispatcher &  init     (bool start_gateways=true);
  void          start    ();
  void          pollLoop ();
  void          stop     ();
  void          destroy  ();
  
  
  Thread::ThrID  initThread  (bool wait_for_start=false);
  void           stopThread  ();
  
  Thread::ThrID  threadId    ();
  
  Dispatcher &   dispatcher  ();
  
  bool           isRunning ();
};
    
#endif
