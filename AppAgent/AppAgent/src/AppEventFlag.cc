#include "AppEventFlag.h"

//##ModelId=3E43E49702A5
AppEventFlag::AppEventFlag ()
    : flagword(0),nsources(0),have_async(False)
{
}

//##ModelId=3E43E49702AE
AppEventFlag::AppEventFlag (const AppEventFlag& right)
    : SingularRefTarget()
{
  operator = (right);
}

//##ModelId=3E43E49702D4
AppEventFlag& AppEventFlag::operator= (const AppEventFlag& right)
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
int AppEventFlag::addSource (bool is_async)
{
  FailWhen( nsources >= MAXSOURCES,"too many sinks registered");
  if( is_async )
    have_async = True;
  return nsources++;
}


//##ModelId=3E43E440007D
void AppEventFlag::raise (int snum)
{
  FailWhen(snum<0 || snum>=nsources,"illegal event source number");
  Thread::Mutex::Lock lock(cond);
  flagword |= (1<<snum);
  cond.broadcast();
}

//##ModelId=3E43EA3D0366
void AppEventFlag::clear (int snum)
{
  FailWhen(snum<0 || snum>=nsources,"illegal event source number");
  Thread::Mutex::Lock lock(cond);
  flagword &= ~(1<<snum);
}

//##ModelId=3E43E42300F1
bool AppEventFlag::wait () const
{
  if( flagword )
    return True;
  // if we don't have any async event sources, then return False
  // since then we would wait forever
  if( !have_async )
    return False;
  Thread::Mutex::Lock lock(cond);
  while( !flagword )
    cond.wait();
  return True;
}

