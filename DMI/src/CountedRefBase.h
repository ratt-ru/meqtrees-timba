//  CountedRefBase.h: generic linked/counted ref implementation
//
//  Copyright (C) 2002
//  ASTRON (Netherlands Foundation for Research in Astronomy)
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

#ifndef DMI_CountedRefBase_h
#define DMI_CountedRefBase_h 1

#include <Common/Debug.h>
#include <DMI/Common.h>
#include <DMI/DMI.h>
#include <DMI/CountedRefTarget.h>
    
#include <ostream>
// Uncomment this to enable verification calls during countedref operations
// #define COUNTEDREF_VERIFY 1

#ifdef USE_THREADS
  #define threadLock(t) Thread::Mutex::Lock t##_lock(t->cref_mutex)
#else
  #define threadLock(t) 
#endif


//##ModelId=3C0CDEE200FE
//##Documentation
//## Implements a counted reference mechanism. See CountedRef<T> for a
//## type-specific interface. CountedRefs have destructive copy semantics.

class CountedRefBase 
{
  public:
    //##ModelId=3DB9345B0265
      LocalDebugContext;

  public:
    //##ModelId=3C0CE1C10277
      CountedRefBase();

      //##ModelId=3DB9345D022B
    //##Documentation
    //## Generic copy constructor. Default behaviour is destructive transfer
    //## (via xferOther()). If the DMI::COPYREF flag is used, calls copy(other)
    //## to make a copy. If depth>=0 or DMI::DEEP or DMI::PRIVATIZE is used,
    //## will privatize the copy. See copy()/privatize() below for other flags.
      CountedRefBase (const CountedRefBase& other, int flags = 0, int depth = -1);

    //##ModelId=3DB9345E0229
      ~CountedRefBase();

    //##ModelId=3DB9345E0297
      CountedRefBase & operator=(const CountedRefBase &right);


      //##ModelId=3C0CDEE2015A
      //##Documentation
      //## Returns True if reference is valid (i.e. has a target).
      bool valid () const;

      //##ModelId=3C0CDEE2015B
      //##Documentation
      //## Dereferences, returns const reference to target.
      const CountedRefTarget* getTarget () const;

      //##ModelId=3C0CE2970094
      //##Documentation
      //## Dereferences to writable target (exception if not writable).
      CountedRefTarget* getTargetWr () const;

      //##ModelId=3C0CDEE20162
    //##Documentation
    //## Makes and returns a copy of the reference. If DMI::DEEP and/or
    //## DMI::PRIVATIZE  is set and/or depth>=0, then makes a r/o copy, and
    //## privatizes it using the supplied flags and depth (DMI::PRIVATIZE by
    //## itself is equivalent to depth=0). Other flags are
    //## DMI::LOCKED to lock the copy, DMI::WRITE for writable copy (defaults
    //## is READONLY), DMI::PRESERVE_RW to preserve original r/w permissions.
      CountedRefBase copy (int flags = 0, int depth = -1) const;

      //##ModelId=3C0CDEE2018A
    //##Documentation
    //## Makes this a copy of the other reference. 
    //## See copy() above for meaning of flags and depth.
      void copy (const CountedRefBase& other, int flags = 0, int depth = -1);

      //##ModelId=3C0CDEE20180
      //##Documentation
      //## Destructive transfer of other ref
      void xfer (const CountedRefBase& other);

      //##ModelId=3C0CDEE20164
      //##Documentation
      //## Creates a "private copy" of the target. Will clone() the target as
      //## necessary.
      //## Without DMI::WRITE, simply guarantees a non-volatile target (i.e.
      //## clones it in the presense of any writers). With WRITE, makes a
      //## writable clone of the target.
      //## The depth argument determines the depth of privatization and/or
      //## cloning: if non 0, then the target's privatize() method is called
      //## with depth=depth-1, in order to privatize and/or clone nested data
      //## structures. The DMI::DEEP flag corresponds to infinte depth, and
      //## should be passed down the structure.
      //## Other flags: DMI::FORCE_CLONE to force  cloning, DMI::LOCKED to lock
      //## the ref, DMI::EXCL_WRITE to make exclusive writer.
      CountedRefBase& privatize (int flags = 0, int depth = 0);

      //##ModelId=3C187D92023F
      //##Documentation
      //## Locks the ref. Locked refs can't be detached or transferred.
      CountedRefBase& lock ();

      //##ModelId=3C187D9A022C
      //##Documentation
      //## Unlocks the ref.
      CountedRefBase& unlock ();

      //##ModelId=3C5019FB0000
      CountedRefBase & persist ();

      //##ModelId=3C501A0201A5
      CountedRefBase& unpersist ();

      //##ModelId=3C18873600E9
      //##Documentation
      //## Changes ref properties, if possible. Recognized flags:
      //## DMI::WRITE/READONLY, LOCKED/UNLOCKED, EXCL_WRITE/NONEXCL_WRITE.
      CountedRefBase& change (int flags);

      //##ModelId=3C1888B001A1
      //##Documentation
      //## Makes the ref an exclusive writer, if no other writers exist
      //## (exception otherwise)
      CountedRefBase& setExclusiveWrite ();

      //##ModelId=3C0CDEE20171
      //##Documentation
      //## Attaches to target object. Flags:
      //## DMI::ANON for anonymous object (default EXTERNAL), WRITE for
      //## writable ref (default READONLY), LOCKED to lock the ref, EXCL_WRITE
      //## for exclusive write access.
      CountedRefBase& attach (CountedRefTarget* targ, int flags = 0);

      //##ModelId=3C0CDEE20178
      //##Documentation
      //## Attaches to target, with READONLY forced.
      CountedRefBase& attach (const CountedRefTarget* targ, int flags = 0);

      //##ModelId=3C1612A60137
      //##Documentation
      //## Detaches ref from its target. Can't be called if ref is locked.
      void detach ();

      //##ModelId=3C19F62B0137
      //##Documentation
      //## Alias for isWritable().
      bool isWrite () const;

      //##ModelId=3C583B9F03B8
      //##Documentation
      //## Returns True if there exist other refs to target that are writable
      bool hasOtherWriters ();

    //##ModelId=3DB9345F0072
      bool isLocked () const;

    //##ModelId=3DB9345F0180
      bool isWritable () const;

    //##ModelId=3DB9345F025C
      bool isExclusiveWrite () const;

      //	True if target is an anonymous object (i.e. will be deleted when last
      //	reference to it is deleted.)
    //##ModelId=3DB9345F0343
      bool isAnonObject () const;

    //##ModelId=3DB93460004B
      bool isPersistent () const;

    //##ModelId=3DB93460013B
      const CountedRefBase * getPrev () const;

    //##ModelId=3DB934600236
      const CountedRefBase * getNext () const;

    // Additional Public Declarations
      // verifies ref chain and throws an exception if any errors are found
    //##ModelId=3DB934600330
      static void verify (const CountedRefBase *ref);
      
      // verifies self
    //##ModelId=3DB9346101AB
      void verify () const
      { verify(this); }
      
      // non-const versions of getNext() and getPrev()
    //##ModelId=3DB9346102B9
      CountedRefBase * getNext ();
    //##ModelId=3DB934610364
      CountedRefBase * getPrev ();

      // prints to stream
      void print (std::ostream &str) const;
      
      // prints to cout, with endline. Not inlined, so that it can
      // be called from a debugger
      void print () const;
      
      // This is a typical debug() method setup. The sdebug()
      // method creates a debug info string at the given level of detail.
      // If detail<0, then partial info is returned: e.g., for detail==-2,
      // then only level 2 info is returned, without level 0 or 1.
      // Other conventions: no trailing \n; if newlines are embedded
      // inside the string, they are followed by prefix.
      // If class name is not specified, a default one is inserted.
      // It is sometimes useful to have a virtual sdebug(). 
    //##ModelId=3DB934620030
      string sdebug ( int detail = 1,const string &prefix = "",
                      const char *name = 0 ) const;
      // The debug() method is an alternative interface to sdebug(),
      // which copies the string to a static buffer (see Debug.h), and returns 
      // a const char *. Thus debug()s can't be nested, while sdebug()s can.
    //##ModelId=3DB934630289
      const char * debug ( int detail = 1,const string &prefix = "",
                           const char *name = 0 ) const
      { return Debug::staticBuffer(sdebug(detail,prefix,name)); }
      
      
  protected:

      //##ModelId=3C1611C702DB
      //##Documentation
      //## Privatizes a reference.
      void privatizeOther (const CountedRefBase& other, int flags, int depth);

      //##ModelId=3C161C330291
      //##Documentation
      //## Nulls internals.
      void empty ();

    // Data Members for Associations

      //##ModelId=3C0CDF6503A5
      //##Documentation
      //## Reference target
      mutable CountedRefTarget *target;

  private:
    // Data Members for Associations

      //##ModelId=3C0CE0FA0394
      //##Documentation
      //## prev ref in list (0 if first ref)
      mutable CountedRefBase *prev;

      //##ModelId=3C0CE0FB0010
      //##Documentation
      //## next ref in list (0 if last ref)
      mutable CountedRefBase *next;

    // Additional Private Declarations
      // flag: target should be cloned at next writable dereference
    //##ModelId=3DB9345B0368
      mutable bool delayed_clone; 
    //##ModelId=3DB9345C0139
      int delayed_clone_flags; 
    //##ModelId=3DB9345C028E
      int delayed_clone_depth;
      
      // helper function to do the delayed cloning
    //##ModelId=3DB9346500B5
      void cloneTarget () const;
  private:
    // Data Members for Class Attributes

      //##ModelId=3C15DF4D036D
      //##Documentation
      //## Flag: locked ref. Locked references can't be transferred, only
      //## copy()d. Also, they may not be detached.
      bool locked;

      //##ModelId=3C0CDEE20112
      //##Documentation
      //## True if reference target is writable.
      bool writable;

      //##ModelId=3C0CDEE20127
      //##Documentation
      //## True if this is an exclusive-write reference, i.e., other writable
      //## refs can't be created.
      bool exclusiveWrite;


      //##ModelId=3C5018D1011A
      //##Documentation
      //## True if the ref is persistent, i.e., copy constructors and "=" do a
      //## true copy (not destructive)
      bool persistent;

    // Additional Implementation Declarations
    friend class CountedRefTarget;
};

inline std::ostream & operator << (std::ostream &str,const CountedRefBase &ref)
{
  ref.print(str);
  return str;
}

//##ModelId=3C0CE1C10277
inline CountedRefBase::CountedRefBase()
{
  empty();
  dprintf(5)("default constructor\n");
}

//##ModelId=3DB9345D022B
inline CountedRefBase::CountedRefBase (const CountedRefBase& other, int flags, int depth)
{
  empty();
  dprintf(5)("copy constructor(%s,%x,%d)\n",other.debug(1),flags,depth);
  if( !other.valid() ) // construct empty ref
    return;
  // constructing [maybe private] copy of reference  
  else if( depth >= 0 || flags&(DMI::COPYREF|DMI::DEEP|DMI::PRIVATIZE) ) 
    copy(other,flags&~DMI::COPYREF);
  else if( other.isPersistent() ) // persistent: do true copy of reference too
    copy(other,flags|DMI::PRESERVE_RW);
  else  // else do destructive copy
    xfer(other);
}


//##ModelId=3DB9345E0229
inline CountedRefBase::~CountedRefBase()
{
  dprintf(5)("destructor\n");
  if( isLocked() )
    unlock();
  detach();
}


//##ModelId=3DB9345E0297
inline CountedRefBase & CountedRefBase::operator=(const CountedRefBase &right)
{
  dprintf(5)("assignment of %s\n",right.debug(1));
  if( &right != this )
  {
    if( right.isPersistent() )
      copy(right,0);
    else
      xfer(right);
  }
  return *this;
}



//##ModelId=3C0CDEE2015A
inline bool CountedRefBase::valid () const
{
  return target != 0;
}

//##ModelId=3C0CDEE2015B
inline const CountedRefTarget* CountedRefBase::getTarget () const
{
  FailWhen( !valid(),"dereferencing invalid ref");
  // should we do this for read-only?  
  if( delayed_clone )
  {
    dprintf1(2)("%s: performing delayed cloning\n",debug());
    // deliberate const violation, but we need to clone the target
    cloneTarget();
  }
  return target;
}

//##ModelId=3C0CE2970094
inline CountedRefTarget* CountedRefBase::getTargetWr () const
{
  FailWhen( !valid(),"dereferencing invalid ref");
  FailWhen( !isWritable(),"r/w access violation: non-const dereference");
  if( delayed_clone )
  {
    dprintf1(2)("%s: performing delayed cloning\n",debug());
    cloneTarget();
  }
  return target;
}

//##ModelId=3C0CDEE20162
inline CountedRefBase CountedRefBase::copy (int flags, int depth) const
{
  return CountedRefBase(*this,flags|DMI::COPYREF,depth);
}

//##ModelId=3C187D92023F
inline CountedRefBase& CountedRefBase::lock ()
{
  dprintf1(3)("%s: locking\n",debug());
  locked = True;
  return *this;
}

//##ModelId=3C187D9A022C
inline CountedRefBase& CountedRefBase::unlock ()
{
  dprintf1(3)("%s: unlocking\n",debug());
  locked = False;
  return *this;
}

//##ModelId=3C5019FB0000
inline CountedRefBase & CountedRefBase::persist ()
{
  dprintf1(3)("%s: persisting\n",debug());
  persistent = True;
  return *this;
}

//##ModelId=3C501A0201A5
inline CountedRefBase& CountedRefBase::unpersist ()
{
  dprintf1(3)("%s: unpersisting\n",debug());
  persistent = False;
  return *this;
}

//##ModelId=3C0CDEE20178
inline CountedRefBase& CountedRefBase::attach (const CountedRefTarget* targ, int flags)
{
  // delegate to other version of attach, with READONLY flag set
  if( flags&DMI::READONLY )
    flags &= ~DMI::WRITE;
  else
    FailWhen(flags&DMI::WRITE,"can't attach writable ref to const object");
  return attach((CountedRefTarget*)targ,flags|DMI::READONLY);
}

//##ModelId=3C19F62B0137
inline bool CountedRefBase::isWrite () const
{
  return isWritable();
}

//##ModelId=3C161C330291
inline void CountedRefBase::empty ()
{
  target=0; next=prev=0;
  locked=writable=exclusiveWrite=persistent=delayed_clone=False;
}

//##ModelId=3DB9345F0072
inline bool CountedRefBase::isLocked () const
{
  return locked;
}

//##ModelId=3DB9345F0180
inline bool CountedRefBase::isWritable () const
{
  return writable;
}

//##ModelId=3DB9345F025C
inline bool CountedRefBase::isExclusiveWrite () const
{
  return exclusiveWrite;
}

//##ModelId=3DB9345F0343
inline bool CountedRefBase::isAnonObject () const
{
  return target && target->anon;
}

//##ModelId=3DB93460004B
inline bool CountedRefBase::isPersistent () const
{
  return persistent;
}

//##ModelId=3DB93460013B
inline const CountedRefBase * CountedRefBase::getPrev () const
{
  return prev;
}

//##ModelId=3DB934600236
inline const CountedRefBase * CountedRefBase::getNext () const
{
  return next;
}

//##ModelId=3DB934610364
inline CountedRefBase * CountedRefBase::getPrev ()
{
  return prev;
}
//##ModelId=3DB9346102B9
inline CountedRefBase * CountedRefBase::getNext ()
{
  return next;
}

#undef threadLock



#endif


