#include "Octoproxy.h"
#include "OctoproxyWP.h"
#include "Dispatcher.h"
    
namespace Octoproxy 
{
  
Identity::Identity (AtomicID wpid)
{
  FailWhen(!Dispatcher::dispatcher,"OCTOPUSSY dispatcher not initialized");
  // instantiate proxy and attach to Dispatcher
  proxy <<= new ProxyWP(wpid);
  WPRef ref(proxy,DMI::COPYREF|DMI::WRITE);
  Dispatcher::dispatcher->attach(ref);
}


//##ModelId=3E08ECB30275
Identity::Identity (const Identity& right)
    : proxy(right.proxy,DMI::COPYREF|DMI::PRESERVE_RW)
{
}

//##ModelId=3E08ECB302D7
Identity::~Identity ()
{
// detach proxy WP from Dispatcher
  FailWhen(!Dispatcher::dispatcher,"OCTOPUSSY dispatcher not initialized");
  Dispatcher::dispatcher->detach(proxy.dewr_p());
}

//##ModelId=3E08ECB30303
Identity & Identity::operator= (const Identity& right)
{
  if( this != & right )
  {
    proxy.copy(right.proxy,DMI::PRESERVE_RW);
  }
  return *this;
}

void Identity::wait ()
{
  FailWhen( !wp().isRunning(),"OCTOPUSSY not started" );
  Thread::Mutex::Lock lock(wp().queueCondition());
  wp().queueCondition().wait();
}

//##ModelId=3E09032400F1
bool Identity::receive(Message::Ref &mref,bool wait)
{
  FailWhen( !wp().isRunning(),"OCTOPUSSY not started" );
  mref.detach();
  Thread::Mutex::Lock lock(wp().queueCondition());
  wp().queueCondition().wait();
}

} // namespace Octoproxy
