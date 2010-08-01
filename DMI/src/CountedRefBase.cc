//  CountedRefBase.h: generic linked/counted ref implementation
//
//  Copyright (C) 2002-2007
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  and The MeqTree Foundation
//  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//
//  This program is free software; you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation; either version 2 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//  $Id$

#include "CountedRefBase.h"

#include <iomanip>

namespace DMI
{

#undef VERIFY
#if COUNTEDREF_VERIFY
  #define VERIFY verify()
#else
  #define VERIFY 
#endif

// Note that CRefs themselves are not thread-safe, but target_s are.
// I.e. different threads should never access the same CRef, but both
// can hold different refs to the same target_.
// The only exception is ref.copy(): this is thread-safe.
// This means that containers need only set a read-lock when accessing
// their contents via ref.copy().


InitDebugContext(CountedRefBase,"CRef");


// cloneTarget
//   Helper function called to actually clone a ref's target_
//   (either from privatize directly, or via delayed-cloning)
//##ModelId=3DB9346500B5
void CountedRefBase::cloneTarget (int flags,int depth) const
{
  if( !valid() )
    return;
  Thread::Mutex::Lock target_lock(target_->crefMutex());
  Assert1(!target_->deleted_);
  VERIFY;
  dprintf1(2)("  %s: cloning target_\n",debug(0));
  // clone the target_
  CountedRefTarget *newtarget_ = target_->clone(flags,depth);
  flags = newtarget_->modifyAttachFlags(flags);
#ifdef COUNTEDREF_LINKED_LIST
  // detach from old list
  if( prev_ ) 
    prev_->next_ = next_;
  else // no prev_ious ref, so update ptr from target_
    target_->owner_ref_ = next_;
  if( next_ )
    next_->prev_ = prev_;
  #if COUNTEDREF_VERIFY
  verify(target_->owner_ref_);
  #endif
  // attach ourselves to new target_
  prev_ = next_ = 0;
  newtarget_->owner_ref_ = const_cast<CountedRefBase*>(this);
#else
  target_->ref_count_--;
  newtarget_->ref_count_ = 1;
#endif
  target_ = newtarget_;
  target_->anon_ = true;
  locked_   = flags&DMI::LOCKED;
  shared_   = flags&DMI::SHARED;
  writable_ = !(flags&DMI::READONLY);
  VERIFY;
}

// verify
//   Checks the reference chain for consistency. 
//##ModelId=3DB934600330
void CountedRefBase::verify (const CountedRefBase *start)
{
  if( !start )
    return;
  const CountedRefTarget *target_ = start->target_;
  if( !target_ )
    return;
  Thread::Mutex::Lock target_lock(target_->crefMutex());
  Assert1(!target_->deleted_);
#ifdef COUNTEDREF_LINKED_LIST
  // run through & verify ref chain
  const CountedRefBase *ref = target_->owner_ref_;
  Assert1(ref);
  Assert1(ref->prev_ == 0);
  bool found_start = false;
  while( ref )
  {
    Assert1( ref->target_ == target_ );
    if( ref == start )
      found_start = true;
    if( ref->next_ )
    {
      Assert1(ref->next_->prev_ == ref);
    }
    ref = ref->next_;
  }
  Assert1(found_start);
#else
  Assert1(target_->ref_count_>0);
#endif
}

void CountedRefBase::copy (const CountedRefBase& other, int flags, int depth)
{
  if( &other == this )
    return;
  dprintf(2)("copying from %s(%x,%d)\n",other.debug(),flags,depth);
  detach();
  // do a little jig and dance to make sure the other is not deleting the target
  // as we speak
  if( !other.valid() ) // copying invalid ref?
    empty();
  else
  {
    Thread::Mutex::Lock other_target_lock(other.target_->crefMutex());
    Assert1(!other.target_->deleted_);
#if COUNTEDREF_VERIFY
    other.verify();
#endif
    target_ = other.target_;
#ifdef COUNTEDREF_LINKED_LIST
    // insert copy into list after other
    prev_ = const_cast<CountedRefBase*>(&other);
    next_ = other.next_;
    const_cast<CountedRefBase&>(other).next_ = this;
    if( next_ )
      next_->prev_ = this;
#else
    target_->ref_count_++;
#endif
    VERIFY;
    // deep copy? do a privatize now
    if( flags&DMI::DEEP || depth>0 )
    {
      // clear all properties (privatize() will set them up according to flags)
      locked_ = false;
      privatize(flags,depth);
    }
    // else use remaining flags to set up ref properties
    else
    {
      // setup properties
      locked_ = flags&DMI::LOCKED;
      writable_ = other.writable_;
      if( flags&DMI::SHARED )
        shared_ = true;
      else if( flags&DMI::COW )
        shared_ = false;
      else
        shared_ = other.shared_;
    }
  }
  dprintf1(2)("  made %s\n",debug(Debug(3)?3:2,"  "));
}

//##ModelId=3C0CDEE20180
void CountedRefBase::xfer (CountedRefBase& other,int flags,int depth)
{
  if( &other == this )
    return;
  dprintf(3)("xferring from %s\n",other.debug());
  detach();
  if( !other.valid() )
    empty();
  else
  {
    Thread::Mutex::Lock other_target_lock(other.target_->crefMutex());
    Assert1(!other.target_->deleted_);
#if COUNTEDREF_VERIFY
    other.verify();
#endif
    FailWhen( other.isLocked(),"can't transfer a locked_ ref" );
#ifdef COUNTEDREF_LINKED_LIST
    // insert myself into list in place of other
    if( (prev_ = other.prev_) !=0 )
      other.prev_->next_ = this;
    else if( other.target_ )
      other.target_->owner_ref_ = this;
    else
      Throw("transfer of corrupted ref");
    if( (next_ = other.next_) != 0 )
      other.next_->prev_ = this;
#endif
    target_ = other.target_;
    VERIFY;
    // copy all fields
    locked_ = flags&DMI::LOCKED;
    writable_ = other.writable_;
    if( flags&DMI::SHARED )
      shared_ = true;
    else if( flags&DMI::COW )
      shared_ = false;
    else
      shared_ = other.shared_;
    // invalidate other ref (const violation here, but that's a consequence
    // of our destructive semantics)
    other.empty();
    // deep copy? do a privatize now
    if( flags&DMI::DEEP || depth>0 )
    {
      // clear all properties (privatize() will set them up according to flags)
      locked_ = false;
      privatize(flags,depth);
    }
  }
  dprintf(3)("  is now %s\n",debug(-1));
}

//##ModelId=3C0CDEE20164
bool CountedRefBase::privatize (int flags, int depth)
{
  // This is a mask of all flags used by privatize. These flags are interpreted
  // here and _NOT_ passed on to target->clone()
  // All other flags are passed on. 
  const int mask_local_flags = DMI::LOCKED|DMI::UNLOCKED|DMI::SHARED|DMI::COW;
  FailWhen( !valid(),"can't privatize an invalid ref" );
  dprintf1(2)("%s: privatizing to depth %d\n",debug(),flags&DMI::DEEP?-1:depth);
  Thread::Mutex::Lock target_lock(target_->crefMutex());
  Assert1(!target_->deleted_);
  dprintf1(2)("  %s\n",target_->debug(2,"  "));
  // no cloning is done if the object is anon_ and writable_ and we are the only ref
  bool res = true;
  if( !isAnonTarget() || !isOnlyRef() || !writable_ || depth>0 || flags&DMI::DEEP)
    cloneTarget(flags&~mask_local_flags,depth-1);
  else
    res = false;
  // now change ref properties if asked to
  if( flags&DMI::LOCKED )
    locked_ = true;
  else if( flags&DMI::UNLOCKED )
    locked_ = false;
  if( flags&DMI::SHARED )
    shared_ = true;
  else if( flags&DMI::COW )
    shared_ = false;
  writable_ = true;
  dprintf(2)("has been privatized\n");
  return res;
}

//##ModelId=3C18873600E9
CountedRefBase& CountedRefBase::change (int flags)
{
  // readonly downgrade
  dprintf(3)("changing to ");
  FailWhen( !valid(),"changing an invalid ref");
  // lock/unlock
  if( flags&DMI::LOCKED )
    locked_ = true;
  else if( flags&DMI::UNLOCKED )
    locked_ = false;
  if( flags&DMI::READONLY )
    writable_ = false;
  if( flags&DMI::SHARED )
    shared_ = true;
  else if( flags&DMI::COW )
    shared_ = false;
  dprintf1(3)("%s\n",debug(-1));
  return *this;
}

//##ModelId=3C0CDEE20171
CountedRefBase& CountedRefBase::attach (CountedRefTarget* targ, int flags)
{
  if( targ == target_ )
    return *this;
  // detach from old target_, if any
  Assert1(!targ->deleted_);
  dprintf(3)("attaching to %s\n",targ->debug());
  if( valid() )
    detach();
  // refuse to attach to NULL target_s
  FailWhen( !targ,"can't attach to null target_" );
  // If target_ is already referenced, check anon_/external for 
  // consistency with supplied flags.
  // Else, use flags to determine how to attach (anon_ by default).
  Thread::Mutex::Lock targ_lock(targ->crefMutex());
  flags = targ->modifyAttachFlags(flags);
  // if target is unattached, determine ownership
  if( !targ->isTargetAttached() )
  {
    int own = flags&DMI::OWNERSHIP_MASK;
    if( own == DMI::AUTOCLONE )
    {
      targ = targ->clone(flags&DMI::DEEP);
      targ->anon_ = true;
      flags &= ~DMI::READONLY;
    }
    else
      targ->anon_ = own != DMI::EXTERNAL;
  }
  target_ = targ;
#ifdef COUNTEDREF_LINKED_LIST
  CountedRefBase *owner = target_->getTargetOwner();
  if( owner )
    (next_=owner)->prev_ = this;
  prev_ = 0;
  target_->owner_ref_ = this;
#else
  target_->ref_count_++;
#endif
  VERIFY;
  shared_ = flags&DMI::SHARED;
  locked_ = flags&DMI::LOCKED;
  writable_ = target_->anon_ || !(flags&DMI::READONLY);
  dprintf(3)("  ref target_ now %s\n",target_->debug(2,"  "));
  return *this;
}

//##ModelId=3C1612A60137
void CountedRefBase::detach ()
{
  if( !valid() )
    return;
  dprintf1(3)("%s: detaching\n",debug());
  // locked_ refs can't be detached (only destroyed)
  FailWhen( isLocked(),"can't detach a locked_ ref");
  // delete object if anon_, and we are last ref to it
  Thread::Mutex::Lock target_lock(target_->crefMutex());
  Assert1(!target_->deleted_);
  VERIFY;
#ifdef COUNTEDREF_LINKED_LIST
  if( !prev_ && !next_ ) 
  {
    target_->owner_ref_ = 0;
    if( isAnonTarget() )
    {
      dprintf(3)("last ref, anon_ target_ will be deleted\n");
      CountedRefTarget *tmp = target_;
      empty();
      // explicitly release target_ mutex prior to destroying it (otherwise,
      // we'll be destroying a locked_ mutex, which is in bad taste). Since
      // the target_ is anon_, no-one else can be legally referencing it at 
      // this point. Which means it's OK to release the mutex: no-one else
      // can [legally] grab it.
      // NB: BAD LOGIC! Some other thread may be inside ref::copy() just now
      // waiting on the mutex -- then as soon as we release, it reattaches 
      // itself to the target before we can clear ourselves; we then proceed
      // to delete the target from under the other ref. The solution is to
      // call empty() before releasing the lock, see above.
      target_lock.release();
      delete tmp;
      return;
    }
  }
  else  // else just detach ourselves from list
  {
    if( prev_ ) 
      prev_->next_ = next_;
    else // no prev_ious ref, so update ptr from target_
      target_->owner_ref_ = next_;
    if( next_ )
      next_->prev_ = prev_;
#if COUNTEDREF_VERIFY
    target_->owner_ref_->verify();
#endif
    dprintf(3)("  old target_ is now: %s\n",target_->debug(2,"  "));
  }
#else
  // decrement ref count of target_, if 0 and anon_, delete it
  if( !(--target_->ref_count_) && isAnonTarget() )
  {
      CountedRefTarget *tmp = target_;
  #ifdef USE_THREADS
      Thread::Mutex *pmutex = &( target_->crefMutex() );
  #endif      
      tmp->deleted_ = true;
      empty();
      delete tmp;
  // explicitly delete the mutex
  #ifdef USE_THREADS
      target_lock.release();
      CountedRefTarget::deleteMutex(pmutex);
  #endif      
      return;
  }
#endif
  empty();
}

//##ModelId=3C1611C702DB
void CountedRefBase::privatizeOther (const CountedRefBase& other, int flags, int depth)
{
  // to make a clone, first do copy, then clone that
  copy(other);
  privatize(flags,depth);
}



// Additional Declarations
//##ModelId=3DB934620030
string CountedRefBase::sdebug ( int detail,const string &prefix,const char *name ) const
{
  string out;
  // low detail
  if( detail>=0 ) // basic detail
  {
    out += name ? name : "CountedRef";
  }
  if( detail >= 1 || detail == -1 )   // normal detail
  {
    Debug::appendf(out,"/%p",(void*)this);
    if( valid() )
      out += Debug::ssprintf(">%p",(void*)target_); 
    else
      out += ">-";
  }
  if( detail >= 1 || detail == -1 && valid() )   // normal detail
  {
    if( valid() )
    {
      Debug::appendf(out,"%c%c%c%c",
                         isAnonTarget() ? 'A' : '-', 
                         isSharedTarget() ? 'S' : '-', 
                         isDirectlyWritable() ? 'W' : '-', 
                         isLocked() ? 'L' : '-');
#ifdef COUNTEDREF_LINKED_LIST
      if( prev_ )
        Debug::appendf(out,"p/%08x",(int)prev_);
      else
        Debug::appendf(out,"p/-");
      if( next_ )
        Debug::appendf(out,"n/%08x",(int)next_);
      else
        Debug::appendf(out,"n/-");
#else
      Debug::appendf(out,"rc:%d",target_->targetReferenceCount());
#endif
    }
  }
  if( detail >= 2 || detail <= -2 ) // high detail - include target_ info
  {
    if( valid() )
    {
      if( out.length() )
        out += "\n"+prefix+"  ";
      out += "->" + target_->sdebug(abs(detail)-1,prefix+"  ");
    }
  }
  return out;
}

//##ModelId=3E01B0C403E3
void CountedRefBase::print (std::ostream &str) const
{
  if( valid() )
  {
    str<<"CRef->@"<<std::hex<<((void*)target_)<<std::dec<<":";
    target_->print(str);
  }
  else
    str<<"CRef->0";
}

//##ModelId=3E01BE0603A1
void CountedRefBase::print () const
{ 
  print(std::cout); 
  std::cout<<endl;
}

}; // namespacer DMI
