//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C999E14021C.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C999E14021C.cm

//## begin module%3C999E14021C.cp preserve=no
//## end module%3C999E14021C.cp

//## Module: Subscriptions%3C999E14021C; Package body
//## Subsystem: OCTOPUSSY%3C5A73670223
//## Source file: F:\lofar8\oms\LOFAR\src-links\OCTOPUSSY\Subscriptions.cc

//## begin module%3C999E14021C.additionalIncludes preserve=no
//## end module%3C999E14021C.additionalIncludes

//## begin module%3C999E14021C.includes preserve=yes
//## end module%3C999E14021C.includes

// Subscriptions
#include "OCTOPUSSY/Subscriptions.h"
//## begin module%3C999E14021C.declarations preserve=no
//## end module%3C999E14021C.declarations

//## begin module%3C999E14021C.additionalDeclarations preserve=yes
//## end module%3C999E14021C.additionalDeclarations


// Class Subscriptions 

Subscriptions::Subscriptions()
  //## begin Subscriptions::Subscriptions%3C999C8400AF_const.hasinit preserve=no
  //## end Subscriptions::Subscriptions%3C999C8400AF_const.hasinit
  //## begin Subscriptions::Subscriptions%3C999C8400AF_const.initialization preserve=yes
  : pksize( sizeof(size_t) )
  //## end Subscriptions::Subscriptions%3C999C8400AF_const.initialization
{
  //## begin Subscriptions::Subscriptions%3C999C8400AF_const.body preserve=yes
  //## end Subscriptions::Subscriptions%3C999C8400AF_const.body
}



//## Other Operations (implementation)
bool Subscriptions::add (const HIID& id, const MsgAddress &scope)
{
  //## begin Subscriptions::add%3C999D010361.body preserve=yes
  // check if it matches an existing subscription
  for( SSI iter = subs.begin(); iter != subs.end(); iter++ )
  {
    // new sub is a strict subset of existing one? no change then
    if( id.subsetOf(iter->mask) && scope.subsetOf(iter->scope) )
      return False;
    // new sub extends existing one? Update
    if( iter->mask.subsetOf(id) && iter->scope.subsetOf(scope) )
    {
      pksize += id.packSize() - iter->mask.packSize() +
                scope.packSize() - iter->scope.packSize();
      iter->mask = id;
      iter->scope = scope;
      return True;
    }
    // else keep on looking
  }
  // not found, so add a subscription
  SubElement newelem = { id,scope };
  subs.push_back(newelem);
  pksize += id.packSize() + scope.packSize() + 2*sizeof(size_t);
  return True;
  //## end Subscriptions::add%3C999D010361.body
}

bool Subscriptions::remove (const HIID &id)
{
  //## begin Subscriptions::remove%3C999D40033A.body preserve=yes
  bool ret = False;
  for( SSI iter = subs.begin(); iter != subs.end(); )
  {
    // remove all subsets of specified ID
    if( iter->mask.subsetOf(id) )
    {
      pksize -= iter->mask.packSize() + iter->scope.packSize() + 2*sizeof(size_t);
      subs.erase(iter++);
      ret = True;
    }
    else
      iter++;
  }
  return ret;
  //## end Subscriptions::remove%3C999D40033A.body
}

void Subscriptions::clear ()
{
  //## begin Subscriptions::clear%3C999E0B0223.body preserve=yes
  subs.clear();
  pksize = sizeof(size_t);
  //## end Subscriptions::clear%3C999E0B0223.body
}

bool Subscriptions::merge (const Subscriptions &other)
{
  //## begin Subscriptions::merge%3C999D64004D.body preserve=yes
  bool ret = False;
  for( CSSI iter = other.subs.begin(); iter != other.subs.end(); iter++ )
    ret |= add(iter->mask,iter->scope);
  return ret;
  //## end Subscriptions::merge%3C999D64004D.body
}

bool Subscriptions::matches (const Message &msg) const
{
  //## begin Subscriptions::matches%3C999D780005.body preserve=yes
  for( CSSI iter = subs.begin(); iter != subs.end(); iter++ )
    if( msg.id().matches(iter->mask) && msg.from().matches(iter->scope) )
      return True;
  return False;
  //## end Subscriptions::matches%3C999D780005.body
}

size_t Subscriptions::pack (void* block, size_t &nleft) const
{
  //## begin Subscriptions::pack%3C99AC2F01DF.body preserve=yes
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
  //## end Subscriptions::pack%3C99AC2F01DF.body
}

void Subscriptions::unpack (const void* block, size_t sz)
{
  //## begin Subscriptions::unpack%3C99AC2F022F.body preserve=yes
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
  //## end Subscriptions::unpack%3C99AC2F022F.body
}

// Additional Declarations
  //## begin Subscriptions%3C999C8400AF.declarations preserve=yes
  //## end Subscriptions%3C999C8400AF.declarations

//## begin module%3C999E14021C.epilog preserve=yes
//## end module%3C999E14021C.epilog
