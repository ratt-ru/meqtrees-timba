#include "OctoproxyWP.h"

    
//##ModelId=3E08FFD30196
Octoproxy::ProxyWP::ProxyWP(AtomicID wpid)
    : WorkProcess(wpid)
{
// disable polling of this WP, since all dequeue operations will be
// handled by the main thread on our behalf
  disablePolling();
}

    


