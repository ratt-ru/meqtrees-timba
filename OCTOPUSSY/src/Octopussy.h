#ifndef OCTOPUSSY_OCTOPUSSY_H 
#define OCTOPUSSY_OCTOPUSSY_H 1

#include <Common/Thread.h>
    
class Dispatcher;    
        
namespace Octopussy
{
  Dispatcher &  init     ();
  void          start    ();
  void          pollLoop ();
  void          stop     ();
  void          destroy  ();
  
  
  Thread::ThrID  initThread  (bool wait_for_start=False);
  void           stopThread  ();
  
  Thread::ThrID  threadId    ();
  
  Dispatcher &   dispatcher  ();
};
    
#endif
