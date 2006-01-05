#include "EventFlag.h"

namespace AppAgent
{    

    
//##ModelId=3E43E49702A5
EventFlag::EventFlag ()
    : flagword(0),nsources(0),have_async(false)
{
}

//##ModelId=3E43E49702AE
EventFlag::EventFlag (const EventFlag& right)
    : SingularRefTarget()
{
  operator = (right);
}

//##ModelId=3E43E49702D4
EventFlag& EventFlag::operator= (const EventFlag& right)
{
  if( this != &right )
  {
    Thread::Mutex::Lock lock(cond);
    flagword = 0;
    nsources = right.nsources;
    have_async = right.have_async;
  }
  return *this;
}


//##ModelId=3E43EDCD037F
int EventFlag::addSource (bool is_async)
{
  FailWhen( nsources >= MAXSOURCES,"too many sinks registered");
  if( is_async )
    have_async = true;
  return nsources++;
}


//##ModelId=3E43E440007D
void EventFlag::raise (int snum)
{
  FailWhen(snum<0 || snum>=nsources,"illegal event source number");
  Thread::Mutex::Lock lock(cond);
  flagword |= (1<<snum);
  cond.broadcast();
}

//##ModelId=3E43EA3D0366
void EventFlag::clear (int snum)
{
  FailWhen(snum<0 || snum>=nsources,"illegal event source number");
  Thread::Mutex::Lock lock(cond);
  flagword &= ~(1<<snum);
}

bool EventFlag::wait (ulong mask,bool lock) const
{
  if( flagword&mask )
    return true;
  // if we don't have any async event sources, then return false
  // since then we would wait forever
  if( !have_async )
    return false;
  Thread::Mutex::Lock mlock;
  if( lock )
    mlock.lock(cond);
  while( !(flagword&mask) )
    cond.wait();
  return true;
}

};
