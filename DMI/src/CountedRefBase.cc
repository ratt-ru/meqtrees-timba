//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC81037E.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC81037E.cm

//## begin module%3C10CC81037E.cp preserve=no
//## end module%3C10CC81037E.cp

//## Module: CountedRefBase%3C10CC81037E; Package body
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar8\oms\LOFAR\DMI\src\CountedRefBase.cc

//## begin module%3C10CC81037E.additionalIncludes preserve=no
//## end module%3C10CC81037E.additionalIncludes

//## begin module%3C10CC81037E.includes preserve=yes
//## end module%3C10CC81037E.includes

// CountedRefBase
#include "CountedRefBase.h"
//## begin module%3C10CC81037E.declarations preserve=no
//## end module%3C10CC81037E.declarations

//## begin module%3C10CC81037E.additionalDeclarations preserve=yes

InitDebugContext(CountedRefBase,"CRef");

void CountedRefBase::cloneTarget () const
{
  if( !valid() )
    return;
  dprintf1(2)("  %s: cloning target\n",debug(0));
  // clone the target
  CountedRefTarget *newtarget = target->clone(delayed_clone_flags,delayed_clone_depth);
  // detach from old list
  if( prev ) 
    prev->next = next;
  else // no previous ref, so update ptr from target
    target->owner_ref = next;
  if( next )
    next->prev = prev;
  // attach ourselves to new reflist
  prev = next = 0;
  target = newtarget;
  target->owner_ref = (CountedRefBase*)this;
  anonObject = True;
  // clear delayed-clone flag
  delayed_clone = False;
}
//## end module%3C10CC81037E.additionalDeclarations


// Class CountedRefBase 


//## Other Operations (implementation)
void CountedRefBase::copy (const CountedRefBase& other, int flags)
{
  //## begin CountedRefBase::copy%3C0CDEE2018A.body preserve=yes
  dprintf(2)("copying from %s\n",other.debug());
  detach();
  if( !other.valid() ) // copying invalid ref?
    empty();
  else
  {
    // if the other ref is delayed-clone, then resolve it now
    if( other.delayed_clone )
    {
      dprintf(2)("  performing delayed cloning\n");
      ((CountedRefBase*)&other)->cloneTarget();
    }
    if( flags&DMI::READONLY )
      flags &= ~DMI::WRITE;
    else
      FailWhen( flags&DMI::WRITE && (!other.isWritable() || other.isExclusiveWrite()),
             "r/w access violation: copy(WRITABLE)");
    // insert copy into list after other
    target = other.target;
    prev = (CountedRefBase*)&other;
    next = other.next;
    ((CountedRefBase&)other).next = this;
    // setup properties
    locked = (flags&DMI::LOCKED) != 0;
    anonObject = other.isAnonObject();
    // writable property is inherited unless exclusive, or READONLY is specified
    // (guard condition above already checks for access violations)
    writable = (flags&DMI::WRITE) != 0 ||
               ( (flags&DMI::PRESERVE_RW) && other.isWritable() );
    persistent = (flags&DMI::PERSIST) != 0;
    exclusiveWrite = delayed_clone = False;
  }
  dprintf1(2)("  made %s\n",debug(Debug(3)?3:2,"  "));
  //## end CountedRefBase::copy%3C0CDEE2018A.body
}

void CountedRefBase::xfer (CountedRefBase& other)
{
  //## begin CountedRefBase::xfer%3C0CDEE20180.body preserve=yes
  dprintf(3)("xferring from %s\n",other.debug());
  detach();
  if( !other.valid() )
    empty();
  else
  {
    FailWhen( other.isLocked(),"can't transfer a locked ref" );
    FailWhen( other.isPersistent(),"can't transfer a persistent ref" );
    // insert myself into list in place of other
    if( (prev = other.prev) !=0 )
      other.prev->next = this;
    else if( other.target )
      other.target->owner_ref = this;
    else
      Throw("transfer of corrupted ref");
    if( (next = other.next) != 0 )
      other.next->prev = this;
    // copy all fields
    target = other.target;
    locked = False;
    anonObject = other.isAnonObject();
    writable = other.isWritable();
    exclusiveWrite = other.isExclusiveWrite();
    delayed_clone = False;
    // invalidate other ref
    other.empty();
  }
  dprintf(3)("  is now %s\n",debug(-1));
  //## end CountedRefBase::xfer%3C0CDEE20180.body
}

CountedRefBase& CountedRefBase::privatize (int flags, int depth)
{
  //## begin CountedRefBase::privatize%3C0CDEE20164.body preserve=yes
  dprintf1(2)("%s: privatizing to depth %d, target:\n",debug(),flags&DMI::DEEP?-1:depth);
  FailWhen( !valid(),"can't privatize an invalid ref" );
  dprintf1(2)("  %s\n",target->debug(2,"  "));
  // readonly overrides writable and disables delayed cloning
  if( flags&DMI::READONLY )
    flags &= ~(DMI::DLY_CLONE|DMI::WRITE);
  // forcing a clone disables delayed cloning
  if( flags&DMI::FORCE_CLONE )
    flags &= ~DMI::DLY_CLONE;
  // no cloning is done if the object is anon, and either
  //   (1) we are the only ref, or
  //   (2) cloning is read-only, and all other refs are read-only.
  // but the FORCE_CLONE flag can force a clone anyway
  bool do_clone=False;
  if( !(flags&DMI::FORCE_CLONE) && isAnonObject() )
  {
    if( prev || next )  // other refs exist? Scan for writable ones
    {
      if( flags&DMI::WRITE )  // clone will be writable?
        do_clone = True;
      else
      {
        // readonly clone -- make ourselves readonly, and do a clone
        // if any writable refs are left.
        writable = False;
        if( target->refCountWrite() )
          do_clone=True;
      }
    }
  }
  else // non-anon is always cloned
    do_clone=True;
  
  if( do_clone )
  {
    delayed_clone_flags = flags;
    delayed_clone_depth = depth;
    if( flags&DMI::DLY_CLONE ) // mark for delayed cloning, if requested
    {
      delayed_clone = True;
      // if deep-delay is not specified, turn off delay for target flags
      if( flags&DMI::DEEP_DLY_CLONE != DMI::DEEP_DLY_CLONE )
        delayed_clone_flags &= ~DMI::DLY_CLONE;
      dprintf(2)("  marked for delayed cloning\n");
    }
    else // else clone now
      cloneTarget();
  }
  else
  {
    // we are sole reference to target, privatize it
    target->privatize(flags,depth);
    delayed_clone = False;
  }
  // now setup ref properties
  if( flags&DMI::LOCKED )
    locked = True;
  else if( flags&DMI::UNLOCKED )
    locked = False;
  // writable remains as-is unless overridden by flags
  if( flags&DMI::WRITE )
    writable = True;
  else 
    writable = False;
  // exclusiveWrite remains as-is unless overridden
  if( flags&DMI::EXCL_WRITE )
    exclusiveWrite = True;
  else if( flags&DMI::NONEXCL_WRITE )
    exclusiveWrite = False;
  // persistent flag may be raised explicitly
  if( flags&DMI::PERSIST )
    persistent = True;
  
  dprintf(2)("has been privatized\n");
  return *this;
  //## end CountedRefBase::privatize%3C0CDEE20164.body
}

CountedRefBase& CountedRefBase::change (int flags)
{
  //## begin CountedRefBase::change%3C18873600E9.body preserve=yes
  // readonly downgrade
  dprintf(3)("changing to ");
  FailWhen( !valid(),"changing an invalid ref");
  if( flags&DMI::READONLY )
    writable = False;
  else if( flags&DMI::WRITE )
  {
    FailWhen(!isWritable(),"can't upgrade read-only ref to read-write");
  }
  // lock/unlock
  if( flags&DMI::LOCKED )
    locked = True;
  else if( flags&DMI::UNLOCKED )
    locked = False;
  // persist
  if( flags&DMI::PERSIST )
    persistent = True;
  // exclusive/non-exclusive write
  if( flags&DMI::NONEXCL_WRITE )
  {
    FailWhen(!isWritable(),"ref is read-only, can't make it nonexclusive-write");
    exclusiveWrite = False;
  }
  else if( flags&DMI::EXCL_WRITE )
    setExclusiveWrite();
  
  dprintf1(3)("%s\n",debug(-1));
  return *this;
  //## end CountedRefBase::change%3C18873600E9.body
}

CountedRefBase& CountedRefBase::setExclusiveWrite ()
{
  //## begin CountedRefBase::setExclusiveWrite%3C1888B001A1.body preserve=yes
  dprintf(3)("setExclusiveWrite\n");
  if( !isExclusiveWrite() )
  {
    FailWhen( !valid(),"ref is invalid");
    FailWhen( !isWritable(),"ref is read-only, can't make it exclusive-write");
    FailWhen( hasOtherWriters(),"can't make exclusive because other writable refs exist");
    writable = exclusiveWrite = True;
  }
  return *this;
  //## end CountedRefBase::setExclusiveWrite%3C1888B001A1.body
}

CountedRefBase& CountedRefBase::attach (CountedRefTarget* targ, int flags)
{
  //## begin CountedRefBase::attach%3C0CDEE20171.body preserve=yes
  // detach from old target, if any
  dprintf(3)("attaching to %s\n",targ->debug());
  if( valid() )
    detach();
  // refuse to attach to NULL targets
  FailWhen( !targ,"can't attach to null target" );
  // If anon/external specified explicitly, check for consistency with
  // other refs to same object. Otherwise, inherit property from other refs.
  // If no other refs and nothing specified, assume external.
  bool anon = (flags&DMI::ANON)!=0;
  if( targ->getOwner() )
  {
    bool other = targ->getOwner()->isAnonObject();
    FailWhen( flags&DMI::ANON && !other,"object already referenced as external, can't attach as anon" );
    FailWhen( !(flags&DMI::ANON) && other,"object already referenced as anon, can't attach as external" );
    anon = other;
  }
  // setup properties
  if( flags&DMI::WRITE && !(flags&DMI::READONLY) ) // writable attach?
  {
    FailWhen( targ->refWriteExclusions(),"can't attach writeable ref: exclusivity violation");
    writable = True;
  }
  else
    writable = False;
  locked = (flags&DMI::LOCKED)!=0;
  anonObject = anon;
  if( flags&DMI::EXCL_WRITE )
    setExclusiveWrite();
  // persistent flag may be raised explicitly
  persistent = (flags&DMI::PERSIST) != 0;

  // add to list 
  target = targ;
  prev = 0;
  if( (next = target->getOwner()) != 0 )
    next->prev = this;
  target->owner_ref = this;

  dprintf(3)("  ref target now %s\n",target->debug(2,"  "));
  return *this;
  //## end CountedRefBase::attach%3C0CDEE20171.body
}

void CountedRefBase::detach ()
{
  //## begin CountedRefBase::detach%3C1612A60137.body preserve=yes
  if( !valid() )
    return;
  dprintf1(3)("%s: detaching\n",debug());
  // locked refs can't be detached (only destroyed)
  FailWhen( isLocked(),"can't detach a locked ref");
  // delete object if anon, and we are last ref to it
  if( !prev && !next ) 
  {
    if( isAnonObject() ) 
    {
      dprintf(3)("last ref, anon target will be deleted\n");
      anonObject = False; // so that the target doesn't complain
      delete target;
    }
  }
  else  // else just detach ourselves from list
  {
    if( prev ) 
      prev->next = next;
    else // no previous ref, so update ptr from target
      target->owner_ref = next;
    if( next )
      next->prev = prev;
    dprintf(3)("  old target is now: %s\n",target->debug(2,"  "));
  }
  empty();
  //## end CountedRefBase::detach%3C1612A60137.body
}

bool CountedRefBase::hasOtherWriters ()
{
  //## begin CountedRefBase::hasOtherWriters%3C583B9F03B8.body preserve=yes
  if( !valid() )
    return False;
  for( const CountedRefBase *ref = target->getOwner(); ref != 0; ref = ref->next )
    if( ref != this && ref->isWritable() )
      return True;
  return False;
  //## end CountedRefBase::hasOtherWriters%3C583B9F03B8.body
}

void CountedRefBase::privatizeOther (const CountedRefBase& other, int flags, int depth)
{
  //## begin CountedRefBase::privatizeOther%3C1611C702DB.body preserve=yes
  // to make a clone, first do a read-only copy, then clone that
  copy(other,DMI::READONLY);
  privatize(flags,depth);
  //## end CountedRefBase::privatizeOther%3C1611C702DB.body
}

// Additional Declarations
  //## begin CountedRefBase%3C0CDEE200FE.declarations preserve=yes
string CountedRefBase::sdebug ( int detail,const string &prefix,const char *name ) const
{
  static int nesting=0;
  if( nesting++>1000 )
  {
    cerr<<"Too many nested CountedRefBase::sdebug() calls";
    abort();
  }
  string out;
  // low detail
  if( detail>=0 )
  {
    Debug::appendf(out,"%s/%08x",name?name:"CRef",(int)this);
    if( valid() )
    {
      out += Debug::ssprintf(">%08x",(int)target); 
      if( delayed_clone )
      {
        out += "*";
        if( delayed_clone_flags&DMI::DLY_CLONE )
          out += "/";
      }
    }
    else
    {
      out += ">-";
    }
  }
  if( detail >= 1 || detail == -1 && valid() )   // normal detail
  {
    if( valid() )
    {
      Debug::appendf(out,"%c%c%c%c%c",
                         isAnonObject() ? 'A' : '-', 
                         isWritable() ? 'W' : '-', 
                         isExclusiveWrite() ? 'E' : '-', 
                         isPersistent() ? 'P' : '-',
                         isLocked() ? 'L' : '-');
      if( prev )
        Debug::appendf(out,"p/%08x",(int)prev);
      else
        Debug::appendf(out,"p/-");
      if( next )
        Debug::appendf(out,"n/%08x",(int)next);
      else
        Debug::appendf(out,"n/-");
    }
  }
  if( detail >= 2 || detail <= -2 ) // high detail - include target info
  {
    if( valid() )
    {
      if( out.length() )
        out += "\n"+prefix+"  ";
      out += "->" + target->sdebug(abs(detail)-1,prefix+"  ");
    }
  }
  nesting--;
  return out;
}

  //## end CountedRefBase%3C0CDEE200FE.declarations
//## begin module%3C10CC81037E.epilog preserve=yes
//## end module%3C10CC81037E.epilog
