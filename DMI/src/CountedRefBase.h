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

#ifndef DMI_CountedRefBase_h
#define DMI_CountedRefBase_h 1

// define this to use a linked list instead of plain ref counts
// note that linked lists are being phased out, and haven't been tested
// for thread safety too well
// #define COUNTEDREF_LINKED_LIST 1

#include <TimBase/Debug.h>
#include <DMI/DMI.h>
#include <DMI/CountedRefTarget.h>
    
#include <TimBase/lofar_iostream.h>
// Uncomment this to enable verification calls during countedref operations
// #define COUNTEDREF_VERIFY 1

namespace DMI 
{

//##ModelId=3C0CDEE200FE
//##Documentation
//## Implements a counted reference mechanism. See CountedRef<T> for a
//## type-specific interface. 
//## The ref target may be _anon_ or _external_. An anon target (default) is
//## considered owned by the ref(s), and is deleted when the last ref is
//## detached. An external target is not owned by refs and will not be 
//## deleted.
//## Writability of the target is determined by two mechanisms: 
//## copy-on-write (default) or sharing.
//## 1. Default case: COW, anon target:
//##    * isDirectlyWritable() true if we are the sole ref to that target
//##    * dereferencing for writing clones new target if not directly writable
//## 2. COW, external target:
//##    * Initial writability determined by flags when attach()ed.
//##    * isDirectlyWritable() true if we are the sole ref to that target_ and
//##      the target is initially writable
//##    * dereferencing for writing clones new target if not directly writable.
//##      Note that new target automatically becomes anon.
//## 3. SHARED 
//##    * Always writable
//##    * All other refs must be attached as SHARED too.
//##    
//## Thread safety:
//##   Refs themselves are NOT THREAD SAFE. Ref targets are. What this means
//##   is:
//##   * Where two threads may be accessing the same ref, make sure you 
//##     lock a mutex (presumably on the ref container).
//##   * Two threads may share a target via their own refs, in this case 
//##     accessing the target (including COW) is thread-safe.
  
class CountedRefBase 
{
  public:
    //##ModelId=3DB9345B0265
      LocalDebugContext;

  public:
    //##ModelId=3C0CE1C10277
      CountedRefBase()
      {
        empty();
        dprintf(5)("default constructor\n");
      }
      

      //##ModelId=3DB9345D022B
    //##Documentation
    //## Generic copy constructor. 
    //## Copies ref (via copy(other,flags,depth)).
    //## Throws exception if DMI::XFER flag is used
    //## If depth>=0 or DMI::DEEP or DMI::PRIVATIZE is used, will privatize 
    //## the copy. DMI::LOCKED will lock the copy.
    //## DMI::SHARED or DMI::COW will enforce shared or cow ref (default
    //## inherits from copy)
      CountedRefBase (const CountedRefBase& other, int flags = 0, int depth = -1);
      
    //##Documentation
    //## Non-const copy constructor.
    //## Default behaviour is just like const copy.
    //## If the DMI::XFER flag is used, then calls xfer(other)
    //## If depth>=0 or DMI::DEEP or DMI::PRIVATIZE is used, will privatize 
    //## the copy. DMI::LOCKED will lock the copy.
    //## DMI::SHARED or DMI::COW will enforce shared or cow ref (default
    //## inherits from copy)
      CountedRefBase (CountedRefBase& other, int flags = 0, int depth = -1);

    //##ModelId=3DB9345E0229
      ~CountedRefBase();

    //##ModelId=3DB9345E0297
      CountedRefBase & operator=(const CountedRefBase &right);


      //##ModelId=3C0CDEE2015A
      //##Documentation
      //## Returns true if reference is valid (i.e. has a target).
      bool valid () const
      { return target_ != 0; }

      //##ModelId=3C0CDEE2015B
      //##Documentation
      //## Dereferences, returns const reference to target.
      const CountedRefTarget* getTarget () const
      {
        FailWhen( !valid(),"dereferencing invalid ref");
        return target_;
      }

      //##ModelId=3C0CE2970094
      //##Documentation
      //## Dereferences to writable target (exception if shared and 
      //## not writable, else does copy-on-write as needed)
      CountedRefTarget* getTargetWr ()
      {
        FailWhen( !valid(),"dereferencing invalid ref");
        if( !isDirectlyWritable() )
          privatize();  // do COW
        return target_;
      }

      //##ModelId=3C0CDEE20162
    //##Documentation
    //## Makes and returns a copy of the reference. If DMI::DEEP and/or
    //## DMI::PRIVATIZE is set and/or depth>=0, then copy of target is made
    //## by calling privatize() with the same flags. 
    //## DMI::LOCKED will lock the copy. 
    //## DMI::SHARED or DMI::COW will change to shared or cow ref.
      CountedRefBase copy (int flags = 0, int depth = -1) const
      { return CountedRefBase(*this,flags|DMI::COPYREF,depth); }

    //##Documentation
    //## Transfer the reference in-place, by returning a copy and detaching
    //## this ref. flags/depth have same meaning as copy()
    //## DMI::SHARED or DMI::COW will enforce shared or cow ref (default
    //## inherits from xferred)
      CountedRefBase xfer (int flags = 0, int depth = -1) 
      { return CountedRefBase(*this,flags|DMI::XFER,depth); }

      //##ModelId=3C0CDEE2018A
    //##Documentation
    //## Makes this a copy of the other reference. 
    //## See copy() above for meaning of flags and depth.
      void copy (const CountedRefBase& other, int flags = 0, int depth = -1);

      //##ModelId=3C0CDEE20180
      //##Documentation
      //## Destructive transfer of other ref
      void xfer (CountedRefBase& other, int flags = 0, int depth = -1);

      //##ModelId=3C0CDEE20164
      //##Documentation
      //## Creates a "private copy" of the target. Will clone() the target 
      //## if: (a) we are not the only ref to it, or (b) target is external,
      //## or (c) target is not writable, or (d) DMI::DEEP flag is specified
      //## or depth>0. Copy is always attached as anon, and clone() is called
      //## with depth-1.
      //## Other flags: 
      //##    DMI::LOCKED/UNLOCKED to lock/unlock the ref.
      //##    DMI::SHARED or DMI::COW to make ref shared or COW.
      //## Returns true if target was cloned, else false.
      bool privatize (int flags = 0, int depth = 0);

      //##ModelId=3C187D92023F
      //##Documentation
      //## Locks the ref. Locked refs can't be detached or transferred.
      CountedRefBase& lock ()
      {
        dprintf(3)("locking\n");
        locked_ = true;
        return *this;
      }
 

      //##ModelId=3C187D9A022C
      //##Documentation
      //## Unlocks the ref.
      CountedRefBase& unlock ()
      {
        dprintf(3)("unlocking\n");
        locked_ = false;
        return *this;
      }


      //##ModelId=3C18873600E9
      //##Documentation
      //## Changes ref properties, if possible. Recognized flags:
      //## LOCKED/UNLOCKED, SHARED/COW, READONLY 
      CountedRefBase& change (int flags);

      //##ModelId=3C0CDEE20171
      //##Documentation
      //## Attaches to target object. Ownership is determined as follows:
      //## 1. If object is already referenced, uses the same ownership mode
      //##    (anon or external), ignoring ownership flags
      //## 2. If object is unreferenced:
      //##    default is ANON attachment, unless one of the following is
      //##    specified:
      //##      DMI::EXTERNAL for external object (default ANON),
      //##      DMI::AUTOCLONE to clone object (DMI::DEEP flag then applies)
      //## DMI::SHARED to attach as shared ref (default COW)
      //## DMI::READONLY to attach as readonly ref
      //## DMI::LOCKED to lock the ref
      CountedRefBase& attach (CountedRefTarget* targ, int flags = 0);

      //##ModelId=3C0CDEE20178
      //##Documentation
      //## Attaches to target_, with READONLY forced (otherwise same as above)
      CountedRefBase& attach (const CountedRefTarget* targ, int flags = 0)
      {
        // delegate to other version of attach, with READONLY flag set
        FailWhen(flags&DMI::WRITE,"can't attach writable ref to const object");
        return attach(const_cast<CountedRefTarget*>(targ),flags|DMI::READONLY);
      }

      //##ModelId=3C1612A60137
      //##Documentation
      //## Detaches ref from its target. Can't be called if ref is locked.
      void detach ();

      //##Documentation
      //## Can ref target be written to without cloning? For COW refs,
      //## true if ref is only ref to target and writable is true.
      //## For shared refs, awlays true
      bool isDirectlyWritable () const
      { return ( writable_ && isOnlyRef() ) || shared_; }

      //##ModelId=3C583B9F03B8
      //##Documentation
      //## Returns true if there are no other refs to target
      bool isOnlyRef () const
      {
      #ifdef COUNTEDREF_LINKED_LIST
        return !next_ && !prev_;
      #else
        return !target_ || target_->targetReferenceCount() == 1;
      #endif
      }

      //##ModelId=3DB9345F0072
      bool isLocked () const
      { return locked_; }
      
      bool isSharedTarget () const
      { return target_ && shared_; }

      //##ModelId=3DB9345F0343
      //##Documentation
      //## true if target is an anonymous object (i.e. will be deleted when last
      //## reference to it is deleted.)
      bool isAnonTarget () const
      { return target_ && target_->anon_; }

#ifdef COUNTEDREF_LINKED_LIST
    //##ModelId=3DB93460013B
      const CountedRefBase * getPrev () const
      { return prev_; }
    //##ModelId=3DB934600236
      const CountedRefBase * getNext () const
      { return next_; }
    //##ModelId=3DB934610364
      CountedRefBase * getPrev ()
      { return prev_; }
    //##ModelId=3DB9346102B9
      CountedRefBase * getNext ()
      { return next_; }
#endif
      
    // Additional Public Declarations
      // verifies ref chain and throws an exception if any errors are found
    //##ModelId=3DB934600330
      static void verify (const CountedRefBase *ref);
      
      // verifies self
    //##ModelId=3DB9346101AB
      void verify () const
      { verify(this); }
      
      // prints to stream
    //##ModelId=3E01B0C403E3
      void print (std::ostream &str) const;
      
      // prints to cout, with endline. Not inlined, so that it can
      // be called from a debugger
    //##ModelId=3E01BE0603A1
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
      string sdebug ( int detail = 0,const string &prefix = "",
                      const char *name = 0 ) const;
      // The debug() method is an alternative interface to sdebug(),
      // which copies the string to a static buffer (see Debug.h), and returns 
      // a const char *. Thus debug()s can't be nested, while sdebug()s can.
    //##ModelId=3DB934630289
      const char * debug ( int detail = 0,const string &prefix = "",
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
      void empty ()
      {
        target_ = 0; 
      #ifdef COUNTEDREF_LINKED_LIST
        next_ = prev_ = 0;
      #endif
        locked_ = writable_ = shared_ = false;
      }

    // Data Members for Associations

      //##ModelId=3C0CDF6503A5
      //##Documentation
      //## Reference target_
      mutable CountedRefTarget *target_;
      
      // ref mutex
      mutable Thread::Mutex mutex_;

  private:
#ifdef COUNTEDREF_LINKED_LIST
      //##ModelId=3C0CE0FA0394
      //##Documentation
      //## prev_ ref in list (0 if first ref)
      mutable CountedRefBase *prev_;

      //##ModelId=3C0CE0FB0010
      //##Documentation
      //## next_ ref in list (0 if last ref)
      mutable CountedRefBase *next_;
#endif
      
      // helper function to do the delayed cloning
    //##ModelId=3DB9346500B5
      void cloneTarget (int flags,int depth) const;

      //##ModelId=3C15DF4D036D
      //##Documentation
      //## Flag: locked_ ref. Locked references can't be transferred, only
      //## copy()d. Also, they may not be detached.
      mutable bool locked_;
      //##ModelId=3C0CDEE20112
      //##Documentation
      //## true if reference target_ is writable_.
      mutable bool writable_;
      mutable bool shared_;
      
    // Additional Implementation Declarations
    friend class CountedRefTarget;
};

inline std::ostream & operator << (std::ostream &str,const CountedRefBase &ref)
{
  ref.print(str);
  return str;
}

//##ModelId=3DB9345D022B
inline CountedRefBase::CountedRefBase (const CountedRefBase& other, int flags, int depth)
{
  empty();
  dprintf(5)("copy constructor(%s,%x,%d)\n",other.debug(1),flags,depth);
  if( !other.valid() ) // construct empty ref
    return;
  FailWhen(flags&DMI::XFER ,"can't transfer a const ref");
  copy(other,flags,depth);
}

inline CountedRefBase::CountedRefBase (CountedRefBase& other, int flags, int depth)
{
  empty();
  dprintf(5)("copy constructor(%s,%x,%d)\n",other.debug(1),flags,depth);
  if( !other.valid() ) // construct empty ref
    return;
  else if( flags&DMI::XFER )  // do destructive copy
    xfer(other,flags,depth);
  // else construct [maybe private] copy of reference  
  else  
    copy(other,flags,depth);
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
    copy(right);
  return *this;
}


#undef threadLock


}; // namespace DMI

#endif


