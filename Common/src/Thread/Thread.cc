#include <Common/Thread/Thread.h>

#include <Common/CheckConfig.h>
#ifdef USE_THREADS
CHECK_CONFIG_CC(UseThreads,yes);
#else
CHECK_CONFIG_CC(UseThreads,no);
#endif

namespace LOFAR
{
  namespace Thread 
  {
    Debug::Context DebugContext("Thread");
  
#ifdef USE_THREADS
    void * dummy_pvoid;
    int dummy_int;
    const Attributes _null_attributes;

    //  create creates a thread
    ThrID create (void * (*start)(void*),void *arg,const Attributes &attr)
    { 
      pthread_t id = 0;
      pthread_create(&id,attr,start,arg);
      return ThrID(id);
    }

    // Class Thread::ThrID 

    // Additional Declarations
#endif

  } // namespace Thread

} // namespace LOFAR
