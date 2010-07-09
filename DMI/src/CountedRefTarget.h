//  CountedRefTarget.h: abstract prototype for a ref target
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

#ifndef DMI_CountedRefTarget_h
#define DMI_CountedRefTarget_h 1

#include <DMI/DMI.h>
#include <TimBase/Thread.h>
#include <TimBase/CheckConfig.h>

#include <TimBase/lofar_iostream.h>

CHECK_CONFIG_THREADS(DMI);

namespace DMI
{

class CountedRefBase;


//##ModelId=3C0CDF41029F
//##Documentation
//## Abstract base class for anything that can be referenced by a Counted
//## Ref.
class CountedRefTarget 
{
  public:
    //##ModelId=3DB93466002B
      CountedRefTarget();

    //##ModelId=3DB934660053
      CountedRefTarget(const CountedRefTarget &right);

    //##ModelId=3DB9346600F3
      virtual ~CountedRefTarget();


      //##ModelId=3C0CE728002B
      //##Documentation
      //## Abstract method for cloning an object. Should allocate a new object
      //## with "new" and return pointer to it. If DMI::WRITE is specified,
      //## then a writable clone is required.
      //## The depth argument specifies cloning depth (the DMI::DEEP flag
      //## means infinite depth). If depth=0, then any nested refs should only
      //## be copy()d. ). If depth>0, then nested refs should be copied and
      //## privatize()d , with depth=depth-1.
      //## The DMI::DEEP flag  corresponds to infinitely deep cloning. If this
      //## is set, then depth should be ignored, and nested refs should be
      //## privatize()d with DMI::DEEP.
      //## 
      //## Otherwise, nested refs should be copied & privatized  with
      //## depth=depth-1 and the DMI::DEEP flag passed on.
      virtual CountedRefTarget* clone (int flags = 0, int depth = 0) const = 0;

      //##ModelId=3C18899002BB
      //##Documentation
      //## Returns a reference count. Note that the ref count methods may be
      //## redefined in derived classes (i.e. SmartBlock) to support, e.g.,
      //## shared memory (i.e. refs from multiple processes), in which case
      //## they are only compelled to be accurate to 0, 1 or 2 ("more").
#ifdef COUNTEDREF_LINKED_LIST
      int targetReferenceCount () const;
      
      bool isTargetAttached () const
      { return owner_ref_ != 0; }
#else
      int targetReferenceCount () const
      { return ref_count_; }
      
      bool isTargetAttached () const
      { return ref_count_ != 0; }
#endif

      //##ModelId=4017F6210026
      bool isAnonTarget () const
      { return anon_; }
      
#ifdef COUNTEDREF_LINKED_LIST
    //##ModelId=3DB934660201
      const CountedRefBase * getTargetOwner () const
      { return owner_ref_; }

    // Additional Public Declarations
    //##ModelId=3DB934660265
      CountedRefBase * getTargetOwner ()
      { return owner_ref_; }
#endif
      
    //##ModelId=3DB9346602A2
      const Thread::Mutex & crefMutex() const
      { return cref_mutex_; }
      
    //##ModelId=3E01B0CE01E8
      virtual void print (std::ostream &str) const
      { str << "CountedRefTarget"; }
      
      // prints to cout, with endline. Not inlined, so that it can
      // be called from a debugger. This uses the virtual print, above,
      // hence it need not be redefined by child classes.
    //##ModelId=3E01BE070204
      void print () const;
      
      // This is a typical debug() method setup. The sdebug()
      // method creates a debug info string at the given level of detail.
      // If detail<0, then partial info is returned: e.g., for detail==-2,
      // then only level 2 info is returned, without level 0 or 1.
      // Other conventions: no trailing \n; if newlines are embedded
      // inside the string, they are followed by prefix.
      // If class name is not specified, a default one is inserted.
      // It is sometimes useful to have a virtual sdebug().
    //##ModelId=3DB9346602E8
      virtual string sdebug ( int detail = 0,const string &prefix = "",
                      const char *name = 0 ) const;
      // The debug() method is an alternative interface to sdebug(),
      // which copies the string to a static buffer (see Debug.h), and returns 
      // a const char *. Thus debug()s can't be nested, while sdebug()s can.
    //##ModelId=3DB934670163
      const char * debug ( int detail = 0,const string &prefix = "",
                           const char *name = 0 ) const
      { return Debug::staticBuffer(sdebug(detail,prefix,name)); }
      
    //##ModelId=400E4D68027F
      ImportDebugContext(DebugDMI);
      
    //##ModelId=4017F61D0145
      typedef void OpSubscriptReturnType;
    //##ModelId=4017F61D0306
      typedef CountedRefTarget OpSubscriptRefType;
      
  protected:
      //## virtual method called when a ref is first attached to a target.
      //## The flags passed to attached are passed through this
      //## method. This can be used to force such things as SHARED and
      //## READONLY if needed (e.g. SingularRefTarget enforces SHARED).
      virtual int modifyAttachFlags (int flags)
      { return flags; } 

#ifdef COUNTEDREF_LINKED_LIST
      //##ModelId=3C0CDF6503B9
      //##Documentation
      //## First ref in list of refs to this target
      mutable CountedRefBase *owner_ref_;
#else
      mutable int ref_count_;
#endif

    // Additional Implementation Declarations
    //##ModelId=3DB934650322
      bool anon_;
      
    //##ModelId=3E9BD917024B
      Thread::Mutex cref_mutex_;

    friend class CountedRefBase;
};

//##ModelId=3C8CDBB901EB
//##Documentation
//## SingularRefTarget is simply a CountedRefTarget with clone()
//## redefined to throw an exception (hence the name 'singular', since
//## such a target cannot be cloned). You can derive your classes from
//## SingularRefTarget if you just want to make use of CountedRefs as
//## auto pointers (i.e., to automatically delete an object once the last
//## ref has been detached), but do not want to implement cloning or
//## privatization.
class SingularRefTarget : public CountedRefTarget
{
  public:
      //##ModelId=3C8CDBF40236
      //##Documentation
      //## Cloning a singular target always fails
      virtual CountedRefTarget* clone (int  = 0, int  = 0) const;

  protected:
      virtual int modifyAttachFlags (int flags)
      { return flags|DMI::SHARED; } 
};

inline std::ostream & operator << (std::ostream &str,const CountedRefTarget &target)
{
  target.print(str);
  return str;
}

//##ModelId=3C8CDBF40236
inline CountedRefTarget* SingularRefTarget::clone (int , int ) const
{
  Throw("can't clone a singular target");
}

}; // namespace DMI

#endif
