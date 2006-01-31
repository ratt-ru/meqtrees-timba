#include <TimBase/Thread/Thread.h>

#include <TimBase/CheckConfig.h>
#ifdef USE_THREADS
CHECK_CONFIG_CC(UseThreads,yes);
#include <map>
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
    
    std::map<ThrID,int> thread_map_;
    std::vector<ThrID> thread_list_;
    
    static inline ThrID mapThread (ThrID id)
    {
      thread_map_[id] = thread_list_.size(); 
      thread_list_.push_back(id);
      return id;
    }
    
    //  creates a thread
    ThrID create (void * (*start)(void*),void *arg,const Attributes &attr)
    { 
      // if first time a new thread is created, then self() is the main thread,
      // so add it to the map
      if( thread_list_.empty() )
      {
        thread_list_.reserve(64);
        mapThread(self());
      }
      // create new thread
      pthread_t id = 0;
      pthread_create(&id,attr,start,arg);
      // add to map
      return mapThread(id);
    }
    
    // exits current thread
    void exit (void *value)
    { 
      pthread_exit(value); 
    }

    // rejoins thread
    int ThrID::join (void * &value)
    { 
      return pthread_join(id_,&value);  
    }
    
    

    // Additional Declarations
#endif

  } // namespace Thread

} // namespace LOFAR
