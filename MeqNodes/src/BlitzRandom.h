#ifndef MEQNODES_BLITZRANDOM_H
#define MEQNODES_BLITZRANDOM_H

#include <TimBase/Thread.h>
#include <time.h>
    
#include <random/uniform.h>
#include <random/normal.h>
        
namespace Meq
{

namespace RndGen
{
  // blitz++ random generators are not thread-safe, hence
  // provide a mutex to lock when using them
  extern Thread::Mutex mutex;
  
  template<class T>
  class Uniform : public ranlib::Uniform<T>
  {
    public:
      Uniform ()
      { this->seed(time(0)); }
  };
  
  template<class T>
  class Normal : public ranlib::Normal<T>
  {
    public:
      Normal (T mean,T stddev)
        : ranlib::Normal<T>(mean,stddev)
      { this->seed(time(0)); }
  };
  
  
  
}

};
    
#endif
