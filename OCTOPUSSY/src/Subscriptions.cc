#include "Subscriptions.h"
#include "OctopussyDebugContext.h"

using namespace DebugOctopussy;

namespace Octopussy
{

Subscriptions::Subscriptions()
  : pksize( sizeof(size_t) )
{
}



bool Subscriptions::add (const HIID& id, const MsgAddress &scope)
{
  // check if it matches an existing subscription
  for( SSI iter = subs.begin(); iter != subs.end(); iter++ )
  {
    // new sub is a strict subset of existing one? no change then
    if( id.subsetOf(iter->mask) && scope.subsetOf(iter->scope) )
      return false;
    // new sub extends existing one? Update
    if( iter->mask.subsetOf(id) && iter->scope.subsetOf(scope) )
    {
      pksize += id.packSize() - iter->mask.packSize() +
                scope.packSize() - iter->scope.packSize();
      iter->mask = id;
      iter->scope = scope;
      return true;
    }
    // else keep on looking
  }
  // not found, so add a subscription
  SubElement newelem = { id,scope };
  subs.push_back(newelem);
  pksize += id.packSize() + scope.packSize() + 2*sizeof(size_t);
  return true;
}

bool Subscriptions::remove (const HIID &id)
{
  bool ret = false;
  for( SSI iter = subs.begin(); iter != subs.end(); )
  {
    // remove all subsets of specified ID
    if( iter->mask.subsetOf(id) )
    {
      pksize -= iter->mask.packSize() + iter->scope.packSize() + 2*sizeof(size_t);
      subs.erase(iter++);
      ret = true;
    }
    else
      iter++;
  }
  return ret;
}

void Subscriptions::clear ()
{
  subs.clear();
  pksize = sizeof(size_t);
}

bool Subscriptions::merge (const Subscriptions &other)
{
  bool ret = false;
  for( CSSI iter = other.subs.begin(); iter != other.subs.end(); iter++ )
    ret |= add(iter->mask,iter->scope);
  return ret;
}

bool Subscriptions::matches (const Message &msg) const
{
  for( CSSI iter = subs.begin(); iter != subs.end(); iter++ )
    if( msg.id().matches(iter->mask) && msg.from().matches(iter->scope) )
      return true;
  return false;
}

size_t Subscriptions::pack (void* block, size_t &nleft) const
{
  size_t hdrsize = sizeof(size_t)*(1+2*subs.size());
  Assert(hdrsize <= pksize ); // make sure our accounting is right
  FailWhen(nleft<hdrsize,"block too small");
  size_t * hdr = static_cast<size_t*>(block);
  char *  data = static_cast<char*>(block) + hdrsize;
  
  *(hdr++) = subs.size(); 
  nleft -= hdrsize;
  
  for( CSSI iter = subs.begin(); iter != subs.end(); iter++ )
  {
    size_t sz1 = iter->mask.pack(data,nleft); data += sz1;
    size_t sz2 = iter->scope.pack(data,nleft); data += sz2;
    *(hdr++) = sz1;
    *(hdr++) = sz2;
    hdrsize += sz1+sz2;
  }
  Assert( hdrsize==pksize ); 
  return hdrsize;
}

void Subscriptions::unpack (const void* block, size_t sz)
{
  FailWhen(sz<sizeof(size_t),"corrupt block");
  subs.clear();
  pksize = sz;
  const size_t * hdr = static_cast<const size_t*>(block);
  int n = static_cast<int>(*(hdr++));
  size_t chksize = sizeof(size_t)*(1+2*n);
  FailWhen(sz<chksize,"corrupt block");
  const char *  data = static_cast<const char*>(block) + chksize;
  while( n-->0 )
  {
    size_t sz1 = *(hdr++), sz2 = *(hdr++);
    chksize += sz1 + sz2;
    FailWhen(sz<chksize,"corrupt block");
    SubElement newelem;
    newelem.mask.unpack(data,sz1); data += sz1;
    newelem.scope.unpack(data,sz2); data += sz2;
    subs.push_back(newelem);
  }
  FailWhen(sz!=chksize,"corrupt block");
}

// Additional Declarations

};
