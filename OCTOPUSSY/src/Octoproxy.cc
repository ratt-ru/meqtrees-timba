#include "Octoproxy.h"
#include "OctoproxyWP.h"
#include "Dispatcher.h"
    
namespace Octoproxy 
{
  
//##ModelId=3E08FF0D035E
class ProxyWP : public WorkProcess
{
  public:
    //##ModelId=3E08FFD30196
    ProxyWP(AtomicID wpid);
  
  
  protected:

  private:

    //##ModelId=3E08FF12002C
    ProxyWP();

    //##ModelId=3E08FF120032
    ProxyWP& operator=(const ProxyWP& right);
    //##ModelId=3E08FF12002E
    ProxyWP(const ProxyWP& right);
};

ProxyWP::ProxyWP (AtomicID wpid)
    : WorkProcess(wpid)
{
// disable polling of this WP, since all dequeue operations will be
// handled by the main thread on our behalf
  disablePolling();
}
  
Identity::Identity (AtomicID wpid)
{
  FailWhen(!Dispatcher::dispatcher,"OCTOPUSSY dispatcher not initialized");
  // instantiate proxy and attach to Dispatcher
  proxy <<= new ProxyWP(wpid);
  Dispatcher::dispatcher->attach(proxy.copy(DMI::READWRITE));
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
