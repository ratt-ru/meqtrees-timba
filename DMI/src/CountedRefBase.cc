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
//## Source file: F:\LOFAR\dvl\LOFAR\cep\cpa\pscf\src\CountedRefBase.cc

//## begin module%3C10CC81037E.additionalIncludes preserve=no
//## end module%3C10CC81037E.additionalIncludes

//## begin module%3C10CC81037E.includes preserve=yes
//## end module%3C10CC81037E.includes

// CountedRefBase
#include "CountedRefBase.h"
//## begin module%3C10CC81037E.declarations preserve=no
//## end module%3C10CC81037E.declarations

//## begin module%3C10CC81037E.additionalDeclarations preserve=yes
//## end module%3C10CC81037E.additionalDeclarations


// Class CountedRefBase 


//## Other Operations (implementation)
void CountedRefBase::copy (const CountedRefBase& other, int flags)
{
  //## begin CountedRefBase::copy%3C0CDEE2018A.body preserve=yes
  dprintf(2)("%s: copying to %s\n",other.debug(),debug(0));
  detach();
  if( !other.isValid() ) // copying invalid ref?
    empty();
  else
  {
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
    writable = (flags&DMI::WRITE) != 0;
    exclusiveWrite = False;
  }
  dprintf(2)("  made %s\n",debug(Debug(3)?3:2,"  "));
  //## end CountedRefBase::copy%3C0CDEE2018A.body
}

void CountedRefBase::xfer (CountedRefBase& other)
{
  //## begin CountedRefBase::xfer%3C0CDEE20180.body preserve=yes
  dprintf(3)("%s: xferring to %s\n",other.debug(),debug(0));
  detach();
  FailWhen( other.isLocked(),"can't transfer a locked ref" );
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
  // invalidate other ref
  other.empty();
  dprintf(3)("  %s now %s\n",debug(0),debug(-1));
  //## end CountedRefBase::xfer%3C0CDEE20180.body
}

CountedRefBase& CountedRefBase::privatize (int flags)
{
  //## begin CountedRefBase::privatize%3C0CDEE20164.body preserve=yes
  dprintf(2)("%s: privatizing target:\n",debug());
  FailWhen( !isValid(),"can't privatize an invalid ref" );
  dprintf(2)("  %s\n",target->debug(2,"  "));
  // readonly overrides writable
  if( flags&DMI::READONLY )
    flags &= ~DMI::WRITE;
  // no cloning is done if the object is anon, and either
  // (1) we are the only ref, or
  // (2) cloning is read-only, and all other refs are read-only.
  // but the FORCE_CLONE flag can force a clone anyway
  Bool do_clone=False;
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
    dprintf(2)("  %s: cloning target\n",debug(0));
    // clone the target
    CountedRefTarget *newtarget = target->clone(flags);
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
    target->owner_ref = this;
    anonObject = True;
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
  
  dprintf(2)("%s has been privatized\n",debug());
  return *this;
  //## end CountedRefBase::privatize%3C0CDEE20164.body
}

CountedRefBase& CountedRefBase::change (int flags)
{
  //## begin CountedRefBase::change%3C18873600E9.body preserve=yes
  // readonly downgrade
  dprintf(3)("%s: changing to ",debug());
  FailWhen( !isValid(),"changing an invalid ref");
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
  // exclusive/non-exclusive write
  if( flags&DMI::NONEXCL_WRITE )
  {
    FailWhen(!isWritable(),"ref is read-only, can't make it nonexclusive-write");
    exclusiveWrite = False;
  }
  else if( flags&DMI::EXCL_WRITE )
    setExclusiveWrite();
  
  dprintf(3)("%s\n",debug(-1));
  return *this;
  //## end CountedRefBase::change%3C18873600E9.body
}

CountedRefBase& CountedRefBase::setExclusiveWrite ()
{
  //## begin CountedRefBase::setExclusiveWrite%3C1888B001A1.body preserve=yes
  dprintf(3)("%s: setExclusiveWrite\n",debug());
  if( !isExclusiveWrite() )
  {
    FailWhen( !isValid(),"ref is invalid");
    FailWhen( !isWritable(),"ref is read-only, can't make it exclusive-write");
    // temporarily make ourselves read-only, and check for more write refs.
    writable = False; 
    FailWhen( target->refCountWrite(),"can't make exclusive because other writable refs exist");
    writable = exclusiveWrite = True;
  }
  return *this;
  //## end CountedRefBase::setExclusiveWrite%3C1888B001A1.body
}

CountedRefBase& CountedRefBase::attach (CountedRefTarget* targ, int flags)
{
  //## begin CountedRefBase::attach%3C0CDEE20171.body preserve=yes
  // detach from old target, if any
  dprintf(3)("%s: attaching to %s\n",debug(),targ->debug());
  if( isValid() )
    detach();
  // refuse to attach to NULL targets
  FailWhen( !targ,"can't attach to null target" );
  // If anon/external specified explicitly, check for consistency with
  // other refs to same object. Otherwise, inherit property from other refs.
  // If no other refs and nothing specified, assume external.
  Bool anon = (flags&DMI::ANON)!=0;
  if( targ->getOwner() )
  {
    Bool other = targ->getOwner()->isAnonObject();
    FailWhen( anon && !other, "object already referenced as external, can't attach as anon");
    FailWhen( (flags&DMI::NON_ANON) && other, "object already referenced as anon, can't attach as external");
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
  if( !isValid() )
    return;
  dprintf(3)("%s: detaching\n",debug());
  // locked refs can't be detached (only destroyed)
  FailWhen( isLocked(),"can't detach a locked ref");
  // delete object if anon, and we are last ref to it
  if( !prev && !next ) 
  {
    if( isAnonObject() ) 
    {
      dprintf(3)("  %s: last ref, anon target will be deleted\n",debug(0));
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

void CountedRefBase::privatizeOther (const CountedRefBase& other, int flags)
{
  //## begin CountedRefBase::privatizeOther%3C1611C702DB.body preserve=yes
  // to make a clone, first do a read-only copy, then clone that
  copy(other,DMI::READONLY);
  privatize(flags);
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
    if( isValid() )
      out += Debug::ssprintf(">%08x",(int)target); 
  }
  if( detail >= 1 || detail == -1 && isValid() )   // normal detail
  {
    if( isValid() )
    {
      Debug::appendf(out,"%c%c%c%c",
                         isAnonObject() ? 'A' : '-', 
                         isWritable() ? 'W' : '-', 
                         isExclusiveWrite() ? 'E' : '-', 
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
    if( out.length() )
      out += "\n"+prefix+"  ";
    out += "->" + target->sdebug(abs(detail)-1,prefix+"  ");
  }
  nesting--;
  return out;
}

  //## end CountedRefBase%3C0CDEE200FE.declarations
//## begin module%3C10CC81037E.epilog preserve=yes
//## end module%3C10CC81037E.epilog


// Detached code regions:
#if 0
//## begin module%3C0CDEE200FE.additionalDeclarations preserve=yes
DebugDefinitions(DMI);
//## end module%3C0CDEE200FE.additionalDeclarations

#endif
