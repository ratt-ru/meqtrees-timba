//#  NestableContainer.h: base class for containers
//#
//#  Copyright (C) 2002-2003
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$

#ifndef DMI_NestableContainer_h
#define DMI_NestableContainer_h 1

// Some notes on hooks.
// NestableContainer can define an innumerable amount of inlined accessor
// methods (basically, for all types known to the system).
// This can lead to unnecessarily long compilation times, hence you can
//    #define NC_SKIP_HOOKS 1
// to have it skip all these methods.
//
// In addition, it can define accessors for some AIPS++ types (Arrays and 
// Strings). This is off by default; if you do need them, you need to
//    #define AIPSPP_HOOKS 1
//    <include NestableContainer.h or another file that eventually includes it>
// and later, #include <DMI/AIPSPP-Hooks.h>
// The reason you need to include AIPSPP-Hooks separately is that this file
// pulls in DataField.h and DataArray.h, which in turn include 
// NestableContainer.h. 
      
#include <Common/Thread/Mutex.h>
#include <DMI/DMI.h>
#include <DMI/TypeInfo.h>
#include <DMI/Timestamp.h>
#include <DMI/BlockableObject.h>
#include <DMI/Registry.h>
#include <DMI/HIIDSet.h>
#include <DMI/CountedRef.h>
#include <DMI/Loki/TypeManip.h>
#ifndef NC_SKIP_HOOKS
  #include <DMI/TID-DMI.h>
  #include <DMI/TypeIterMacros.h>
#endif

// pull in type definitions from configured packages    
// if you add DMI-aware types to a package of your own, add it here
#ifdef HAVE_LOFAR_OCTOPUSSY
  #include <OCTOPUSSY/TID-OCTOPUSSY.h>
#endif
#ifdef HAVE_LOFAR_VISCUBE
  #include <VisCube/TID-VisCube.h>
#endif
#ifdef HAVE_LOFAR_MEQ
  #include <MEQ/TID-Meq.h>
#endif

// pull in AIPS++ types if AIPS++ hooks are configured
#ifdef AIPSPP_HOOKS
#ifndef HAVE_AIPSPP
  #error Must configure AIPS++ support for AIPSPP_HOOKS
#endif
#include <aips/Arrays/Array.h>
#include <aips/Arrays/Vector.h>
#include <aips/Arrays/Matrix.h>
#include <aips/Utilities/String.h>
#endif

#include <list>
#include <deque>


using Debug::ssprintf;
using Loki::Int2Type;
using Loki::Type2Type;

class NestableContainer;
class NCBaseIter;

//##ModelId=3BE97CE100AF
//##Documentation
//## This is an abstract base class for data containers. It implements
//## hooks (see Hook and Hook below) that allow access to elements
//## of the container via the [HIID] and [int] operators.
//## 
//## To derive a specific container that will be compatible with hooks
//## (and thus can be accessed via []), you need to implement, as a
//## minimum, four virtual methods: get(), insert(), size(), type(). See
//## below for specifics.
//## 
//## You can optionally implement getn(), insertn(), if accessing via a
//## numeric index is a special case for your container. If your
//## container supports removing, then remove() and/or removen() should
//## be implemented. Finally, if your container stores data in a
//## contiguous block of memory, isContiguous() should be redefined to
//## return True.

class NestableContainer : public BlockableObject
{
  public:
    //##ModelId=3E9BD919036A
    DefineRefTypes(NestableContainer,Ref);
      
    //##ModelId=3E9BD91500B8
    typedef NestableContainer::Ref NCRef;

    class Hook;
    
    //##ModelId=4017F6290317
    EXCEPTION_CLASS(NCException,LOFAR::Exception);
    //##ModelId=4017F62A015F
    EXCEPTION_CLASS(ConvError,NCException);
    //##ModelId=4017F62A03DC
    EXCEPTION_CLASS(ReadOnly,NCException);
    //##ModelId=4017F62B034A
    EXCEPTION_CLASS(NotContainer,NCException);
    //##ModelId=4017F62C01CC
    EXCEPTION_CLASS(Uninitialized,NCException);
    //##ModelId=4017F62C0343
    EXCEPTION_CLASS(Inconsistency,NCException);
    
    // the ContentInfo struct is used to pass information on a 
    // container element
    //##ModelId=3DB9343D035B
    class ContentInfo
    {
      public:
        //##ModelId=4017F6230074
        const void *ptr;    // pointer to ObjRef or object
        //##ModelId=3DB934920264
        TypeId tid;         // type of contents pointed to
        //##ModelId=4017F6230081
        TypeId obj_tid;     // type of object (differs only when tid==TpObjRef)
        //##ModelId=3DB93492026D
        bool writable;      // flag: can modify contents?
        //##ModelId=3DB934920277
        int  size;          // # of contigious elements at pointer
    };

    //##ModelId=3C8739B50135
    //##Documentation
    //## Hook is a helper class generated by applying the [id] and [n]
    //## operators to a const NestableContainer. It provides transparent
    //## access to objects in the container.
    //## 
    class Hook 
    {
      // Note that since Hooks are almost always treated as const 
      // (since they only appear as temporary objects), all their methods have to
      // be declared as const. Ugly, but that's C++ for you...
      
      friend class NCBaseIter;
      
      protected:
        //##ModelId=4017F62300EF
          static int _dum_int; // dummy by-ref argument
        //##ModelId=4017F623014A
          static ContentInfo _dum_info; 

      public:
          // some public constructors
          Hook (const NestableContainer &parent,const HIID &id1);
          Hook (NestableContainer &parent,const HIID &id1);
      
          template<class T>
          Hook (const CountedRef<T> &parent,const HIID &id1);
          template<class T>
          Hook (CountedRef<T> &parent,const HIID &id1);


          //##ModelId=3C8739B50167
          //##Documentation
          //## If the hook points to a container, subscripts into the container.
          //## Throws exception otherwise.
          const NestableContainer::Hook & operator [] (const HIID &id1) const;

          //##ModelId=3C8739B50176
          //##Documentation
          //## Address-of: enables implicit conversion-to-pointer operators.
          //## After this operator is applied, you can only retrieve the a
          //## contents by pointer.
          const NestableContainer::Hook & operator & () const;

          //##ModelId=4017F6240072
          //##Documentation
          //## True if the hook points to a valid, initialized element.
          bool exists () const;
          
          //##ModelId=4017F62400B7
          //##Documentation
          //## Final type of element pointed to. If it is is a fixed-type container, 
          //## should return type of contents instead. Returns 0 (NullType) 
          //## if element doesn't exist.
          TypeId type () const;

          //##ModelId=4017F62400FB
          //##Documentation
          //## Returns the real type of the element being pointed to. For
          //## containers & dynamic objects, this will be TpObjRef rather
          //## than the object type.
          TypeId actualType () const;

          //##ModelId=4017F6240144
          //##Documentation
          //## If pointing to a container, returns the container type
          //## Returns 0 (NullType) if not pointing to a container.
          TypeId containerType () const;

          //##ModelId=4017F6240190
          //##Documentation
          //## Returns True if pointing to a container element.
          bool isContainer () const;

          //##ModelId=4017F62401D7
          //##Documentation
          //## Returns true if the element being pointed to is held in an 
          //## ObjRef.
          bool isRef () const;

          //##ModelId=3CAB0A3500AC
          //##Documentation
          //## Size of element being pointed to, given the type. 
          //## ***** update this!!!
          //## Always 1 for non-container element
          //## For containers, returns the size of the container. Returns 0 if the
          //## element doesn't exist.
          int size (TypeId tid = 0) const;

          //##ModelId=3CAAE9BB0332
          //##Documentation
          //## Second version, stores size in sz and returns *this
          const NestableContainer::Hook & size (int &sz, TypeId tid = 0) const;

          //##ModelId=3C8770A70215
          //##Documentation
          //## If the element is held in a ref, returns a read-only copy of
          //## the ref. Throws exception otherwise.
          ObjRef ref (int flags=0) const;
          
        //##ModelId=4017F624023A
          //## If the element is held in a ref, attaches it to input ref.
          //## Throws exception otherwise.
          const NestableContainer::Hook & attachObjRef (ObjRef &ref,int flags=0) const;
          
//           //##Documentation
//           //## inlined template to accept refs of any type.
//           //## Throws exception if types are incompatible.
//           template<class T>
//           const NestableContainer::Hook & attach (CountedRef<T> &ref,int flags=0) const
//           { return attachObjRef(ref.ref_cast<BlockableObject>(),flags); }

        //##ModelId=3C8739B5017B
          //##Documentation
          //## Initializes element being pointed to. If element exists, does
          //## nothing.
          const NestableContainer::Hook & init (TypeId tid = 0) const;

          //##ModelId=3C873AE302FC
          const NestableContainer::Hook & put (BlockableObject &obj, int flags) const;

          //##ModelId=3C873B8F01C2
          const NestableContainer::Hook & put (const BlockableObject &obj, int flags) const;

          //##ModelId=3C873B980248
          const NestableContainer::Hook & put (const ObjRef &ref, int flags) const;

        //##ModelId=3C8739B5017C
          //##Documentation
          //## If container is writable, and the element being pointed to is held
          //## in an ObjRef, then privatizes the ObjRef. Throws exception otherwise.
          const NestableContainer::Hook & privatize (int flags) const;
          
        //##ModelId=3F5C8EBD01C4
          //##Documentation
          //## Marks the hook for "replacing". The next assignment operation
          //## will attempt to replace the element being pointed to. The 
          //## difference is apparent if you consider, e.g., a record:
          //##    record[Field] = 0;      // assigns integer field to record
          //##    record[Field] = "xxx";  // fails: type mismatch
          //##    record[Field].replace() = "xxx";  // OK, replaces with string field
          const NestableContainer::Hook & replace () const;
          
        //##ModelId=3C876DCE0266
          //##Documentation
          //## Removes the element being pointed to from the container.  If the
          //## element is held in an ObjRef, returns a ref to it, so you can
          //## do stuff like ref = rec["field"].remove() to remove it from the
          //## container and place it in a local ref.
          //## If there is no such element (or if not held in an ObjRef), it
          //## returns an invalid ref.
          ObjRef remove () const;
          
        //##ModelId=3C876E140018
          //##Documentation
          //## Can only be called for elements held in an ObjRef. Detaches element
          //## but leaves the ObjRef in the container. Returns ref to self, so it's
          //## possible to do things like rec[field].detach(&old_ref) <<= new
          //## Object;
          const NestableContainer::Hook & detach (
              //##Documentation
              //## If specified, then the element will be re-attached to this ref.
              ObjRef* ref = 0
          ) const;
          
        // Additional Public Declarations
          friend class NestableContainer;
          
        // declare inlined operator [] for other forms of HIIDs (see CountedRef.h)
          declareSubscriptAliases(NestableContainer::Hook,const) 
        // declare inlined operator () to implicitly concatenate AtomicIDs (see CountedRef.h)
          declareParenthesesAliases(NestableContainer::Hook,const) 
          
        // include all the wornderful accessor methods
          #ifndef NC_SKIP_HOOKS
          #include <DMI/NC-ConstHooks.h>
          #include <DMI/NC-Hooks.h>
          #endif
          
          // standard debug info
        //##ModelId=3DB934BC01D9
          string sdebug (int detail = 1,const string &prefix = "",const char *name = "Hook") const;
        //##ModelId=3DB934BE007D
          const char *debug (int detail = 1,const string &prefix = "",const char *name = "Hook") const
          { return Debug::staticBuffer(sdebug(detail,prefix,name)); }
          
      protected:
          //##ModelId=3C8739B50153
          Hook (const NestableContainer &parent,const HIID &id1,bool nonconst);
          //##ModelId=3C8739B5015E
          Hook (const NestableContainer::Ref &parent,const HIID &id1,bool nonconst);
          
          void initialize (const NestableContainer *pnc,const HIID &id1,bool nonconst);
          
          
          // When repeated subscripts are applied to non-writable containers,
          // a chain is maintained in the hook so that if a write to the 
          // hook occurs, it can go back and privatize starting with the
          // last writable container. This class stores the chain's 
          // elements.
        //##ModelId=4017F61E007D
          class Link
          {         
            public:
            //##ModelId=4017F623009E
            Thread::Mutex::Lock lock;
            //##ModelId=4017F62300B1
                     HIID id;
            //##ModelId=4017F62300C1
                     Link (const NestableContainer &,const HIID &);
            //##ModelId=4017F62300C7
                     Link () {};
          };
          
          //##ModelId=4017F6230180
          // pointer to current container
          mutable NestableContainer *nc;
          // flag indicating writability of current container 
        //##ModelId=4017F62301AD
          mutable bool nc_writable; 
          
          // First element in chain is always present, so
          // we make it a member for efficiency.
        //##ModelId=4017F623020B
          mutable Link link0;
          // rest of chain
        //##ModelId=4017F6230237
          mutable std::deque<Link> chain;
          
          // pointers/lock to non-const objects at start of chain
        //##ModelId=4017F62302A3
          mutable CountedRef<NestableContainer> *ncref0;
        //##ModelId=4017F62302D6
          mutable NestableContainer *ncptr0;
          // The following scenarios are possible:
          //  (a) nc_writable=true: current container (@link0) is already 
          //      writable, no privatization needed (chain should be empty and
          //      ncref0 should be 0).
          // else nc_writable=false and:
          //  (b) ncref0!=0 => ncref0 is nonconst, refers to const container 
          //      at link0. Privatization will start with ncref0. (nclock0 may
          //      be holding a lock on the container of *ncref0.)
          // else ncref0==0 and:
          //  (c) ncptr0!=0 => we have a nonconst container at link0,
          //      pointed to by ncptr0. Privatization will start from 
          //      subsequent chain links. (Assert: chain can't be empty.)
          //  (d) ncptr0==0 => fail with ReadOnly, since we have no 
          //      base to start privatizing at. (Assert: chain must be empty.)
          
          // A lock is maintained on the _parent_ of link0 (if possible)
          // to make sure it's not pulled from under our feet
        //##ModelId=4017F6230304
          mutable Thread::Mutex::Lock nclock0;

          //##ModelId=4017F6230330
          // pointer to HIID subscript being applied to current container
          mutable HIID *pid;            
          
          // current hook target -- valid only after a resolveTarget() call
        //##ModelId=4017F6230361
          mutable ContentInfo target;
          // True if hook target is a NestableContainer. Set in resolveTarget()
        //##ModelId=4017F6230396
          mutable bool target_nestable;  
          
          //##ModelId=4017F624000E
          mutable bool addressed;     // flag: & operator has been applied
        //##ModelId=3F5C8EBD016A
          mutable bool replacing;     // flag: replace allowed
          
          
          
          
          
          // if target is an ObjRef, returns it, checking for writability
          // else throws an exception
        //##ModelId=4017F62500F7
          const ObjRef * asRef (bool write=False) const;

          // This applies the current subscript to the hook, caching the result
          // in target. Returns pointer to target object. Sets target_nestable.
          // If flags&DMI_DEREFERENCE is set and hook resolves to an ObjRef, 
          //    then it resolves the ref and returns pointer to object. Note that
          //    target.ptr still refers to the ObjRef in this case.
          // If flags&DMI::WRITE is set, ensures non-constness of the returned
          //    object by privatizing as necessary, or throwing a ReadOnly 
          //    exception if that is impossible. 
          // All flags are also passed to the NC::get() method.
          // The hint argument is passed to NC::get() via the info.tid argument,
          // see documentation of get() below.
        //##ModelId=4017F62501D7
          const void * resolveTarget (int flags=0,TypeId hint=0) const;
          
          // ensures writability, removes current target, returns 0
        //##ModelId=4017F625031C
          void * removeTarget () const;
          
          // Attempts to treat current target as a container and moves the
          // hook to it, setting the next index. Returns True on success.
          // If target is not a container, either returns False (if 
          // nothrow==True), or throws a NotContainer exception.
        //##ModelId=4017F6250392
          bool nextContainer (const HIID &next_id,bool nothrow=True) const;
    
          // attempts to make current container writable, by privatizing
          // everything up the chain. Throws ReadOnly if this is not possible.
        //##ModelId=4017F62600FF
          void resolveToWritableContainer() const;
          
          // This is called to get a value, for built-in scalar types only
        //##ModelId=4017F626017A
          bool get_scalar( void *data,TypeId tid,bool nothrow=False ) const;

          // This is called to access by reference, for all types
        //##ModelId=4017F6260346
          const void *get_address(ContentInfo &info,TypeId tid,bool must_write,
              bool pointer=False,const void *deflt=0,Thread::Mutex::Lock *keeplock=0) const;

          // This is called to access by pointer, for all types
        //##ModelId=4017F62702A0
          const void *get_pointer(int &sz,TypeId tid,bool must_write,bool implicit=False,
              const void *deflt=0,Thread::Mutex::Lock *keeplock=0) const;

          // Helper function resolves current index to a target. Returns target
          // in info
        //##ModelId=3DB934C00071
          void * prepare_put (ContentInfo &info,TypeId tid) const;
              
          // This is called to assign a value, for scalar & binary types
        //##ModelId=3DB934C102D5
          const void * put_scalar( const void *data,TypeId tid,size_t sz ) const;

          // Helper function to assign an object.  
        //##ModelId=3DB934C30364
          void assign_object( BlockableObject *obj,TypeId tid,int flags ) const;

          // const version forces a read-only ref
        //##ModelId=3DB934C600BA
          void assign_object( const BlockableObject *obj,TypeId tid,int flags ) const;

          // Helper function assigns an objref     
        //##ModelId=3DB934C801DF
          ObjRef & assign_objref ( const ObjRef &ref,int flags ) const;

          // Helper functions for assignment of vectors
        //##ModelId=4017F6280225
          void * prepare_assign_vector (TypeId tid,int size) const;
        //##ModelId=4017F62803A9
          void * assign_vector (TypeId tid,int size) const;
          
          // helper function prepares for array assignment
        //##ModelId=3E7081A50350
          void * prepare_assign_array (bool &haveArray,TypeId tid,const LoShape &shape) const;
          // Templated function implements operator = (vector<T>) for arrayable types
          template<class T,class Iter> 
          void assign_arrayable (int size,Iter begin,Iter end,Type2Type<T> = Type2Type<T>()) const;
          
      private:
        //##ModelId=3DB934CC00F5
          Hook();

        //##ModelId=3DB934CC02E9
          Hook & operator= (const Hook &right);

    };

    //##ModelId=3F549251022F
    //##Documentation
    //## Abstract base class for anything that needs to subscribe to
    //## container events. See NestableContainer::subscribe() below
    class Subscriber
    {
      public:
        //##ModelId=400E4D670364
        //##Documentation
        //## Container event types
        typedef enum
        {
          NC_MODIFY   = 1,    // contents modified
          NC_DELETE   = 2     // container deleted
        }
        ContainerEventTypes;
          
        //##ModelId=3F5C8F2503AB
        //##Documentation
        //## This virtual method is called every time a container
        //## event occurs
        virtual int ncSubscriberNotify (const HIID &id, int event) = 0;
    };

    //##ModelId=3F54921B0175
    class Subscription
    {
      private:
        //##ModelId=3F5D83F3016E
        //##Documentation
        //## user-supplied event ID. Can be anything
        HIID id;
        //##ModelId=3F54929100C0
        //##Documentation
        //## ref to user's subscriber object
        NestableContainer::Subscriber &subscriber;
        //##ModelId=3F5D838600F4
        //##Documentation
        //## mask of subscribed events
        int event_mask;

      public:
        //##ModelId=3F5C8F9700E4
        Subscription (const HIID& id_, NestableContainer::Subscriber &subs, int evmask)
          : id(id_),subscriber(subs),event_mask(evmask) {}
      
        //##ModelId=3F5C8FBA0243
        //##Documentation
        //## notifies subscriber if event matches mask
        int notify (int event)
        { return event&event_mask 
                 ? subscriber.ncSubscriberNotify(id,event) : 1; }
        
    };

  protected:
      //##ModelId=3C56A6C50088
      //##Documentation
      //## get(HIID): Abstract method for dereferencing a container element
      //## indicated by id. Must be implemented by all child classes. This is
      //## the method called by the hook operator [](const HIID &). See Data
      //## Record and DataField for example implementations.
      //## Parameters: see below.
      //## Return values:
      //##  >0  indicates success.
      //##  =0  indicates that the element doesn't exist but 
      //##      can be insert()ed (e.g. no such field in record). 
      //##  <0  const violation. DMI::WRITE was set, but write access to the 
      //##      element was not granted because of constness. 
      //## An exception may be thrown for other errors, such as an illegal id.
      virtual int get (
          //##Documentation
          //## Specifies an element within the container.
          //## An empty HIID implies accessing the entire container in vector
          //## mode; the container may throw an exception if this is not
          //## supported (i.e. if its items are non-contiguous)
          const HIID &id,
          //##Documentation
          //## On entry, info.tid may contain the TypeId of the "preferred"
          //## data representation (e.g. a DataArray may be seen as containing
          //## an Array<int,N>, or a block of ints). This should be interpreted
          //## as a hint only; if such a type is not supported, then container
          //## should ignore the hint. If info.tid=0, the default representation
          //## should be returned.
          //## On return, this describes the contents: pointer to data,
          //## TypeId, writability, size. Note that all dynamic objects must
          //## be returned via refs (i.e. info.ptr should point to the ref, 
          //## info.tid==TpObjRef, info.obj_tid is actual object type,
          //## info.writable indicates non-constness of the ref itself and
          //## not the ref target). For all other object types, ptr points 
          //## to the object itself, and info.tid==info.obj_tid.
          ContentInfo &info,
          //##Documentation
          //## Is container object non-const. If true, the container may modify 
          //## itself to grant write access (see below).
          //## Due to C++ limitations (specifically, the enforced const-ness
          //## of intermediate objects), get() is declared as a const method,
          //## and Hooks keep track of constness in run-time.
          bool nonconst,     
          //##Documentation
          //## The following flags are recognized: 
          //## DMI::WRITE: write access to object is requested. If nonconst,
          //##    the container should modify itself as needed (i.e., 
          //##    privatizing refs, etc.) to grant write acccess.
          //## DMI::NC_DEREFERENCE: if object is held via a ref, then 
          //##    DMI::WRITE applies to the object (i.e. the ref target) 
          //##    rather than the ref itself. This means a const ref to a
          //##    writable target is OK. A non-const ref to a readonly
          //##    target is also OK, since hooks know how to privatize
          //##    targets for themselves. Therefore, <0 (const violation)
          //##    should only be returned only if !nonconst AND the ref is 
          //##    readonly.
          //## DMI::NC_ASSIGN (implies DMI::WRITE): element will be assigned to,
          //##    so container is free to initialize it if non-existent (and
          //##    if it has sufficient type info). So far, only DataField
          //##    supports this.
          int flags) const = 0;

  public:
      //##ModelId=3C7A13D703AA
      //##Documentation
      //## insert(HIID). This is an abstract method for allocating a new element
      //## in a container. Must be implemented by all child classes.
      //## Inserts element and returns a pointer to it. 
      //## If tid=TpObjRef, then a new (unattached) ObjRef must be inserted
      //## and a pointer to it returned. Otherwise, a new object should be 
      //## initialized, and the return value must be a pointer to the object.
      //## Returns >1 on success; throws exception on failure.
      virtual int insert (
          //##Documentation
          //## ID of element to be allocated.
          //## Throw an exception if an element with such an ID can't be inserted
          //## (e.g. arrays can allow insert() only at end of array).
          const HIID &id,
          //##Documentation
          //## On entry, info.obj_tid contains the type of element 
          //## to be inserted. 
          //## If the container is of a fixed type which does not match info,
          //## an exception should be thrown, unless a conversion exists
          //## between the two types (see TypeInfo::isConvertible()). 
          //## If info.obj_tid=0 and the container is of a fixed type and has 
          //## been initialized, then that type may be assumed. Otherwise an
          //## exception should be thrown.
          //## On return, the contents of info should be exactly the same as
          //## after a get(...,DMI::WRITE) call. 
          ContentInfo &info
      ) = 0;

      //##ModelId=3C87752F031F
      //##Documentation
      //## Virtual method for removing the element indicated by id.
      //## Should return >0 if element was removed, =0 for no such
      //## element, or throw an exception on logic error.
      //## Default implementation throws a "container does not support remove"
      //## exception.
      virtual int remove (const HIID &)
      { Throw("container "+objectType().toString()+
              " does not support remove()"); }

      //##ModelId=3C7A154E01AB
      //##Documentation
      //## Abstract method. Must returns the number of elements in the
      //## container.
      virtual int size (TypeId tid = 0) const = 0;

      //##ModelId=3C7A1552012E
      //##Documentation
      //## Should return the type of the contents. If container is not of a
      //## fixed type (e.g. a record), or hasn't been initialized yet, then
      //## just return NullType (0). Default version returns 0.
      virtual TypeId type () const
      { return NullType; }
      
    //##ModelId=400E4D6C0281
      //##Documentation
      //## This method is called after a copy constructor, assignment
      //## or fromBlock() operation. It is meant to validate the integrity of 
      //## the container, for application-specific containers derived 
      //## from the standard system ones. Default version does nothing. 
      virtual void validateContent () 
      {};

      //##ModelId=3BFCD8180044
      bool isNestable () const
      { return True; }
      
      // public interface to protected get() which translates const-ness
      // of object into the appropriate arguments.
    //##ModelId=4017F62E0007
      int get (const HIID &id,ContentInfo &info,int flags) const
      { return get(id,info,False,flags); }
      
    //##ModelId=4017F62E031D
      int get (const HIID &id,ContentInfo &info,int flags)
      { return get(id,info,True,flags); }

      //##ModelId=3C5551E201AE
      //##Documentation
      //## Static function, checks if a type is a nestable (or a subclass
      //## thereof).
      static bool isNestable (TypeId tid)
      { return registry.find(tid); }
      
    //##ModelId=3DB934E10329
      const Thread::Mutex & mutex() const
      { return mutex_; }

  public:
      friend class Hook;
    //##ModelId=4017F61E00B4
      typedef Hook OpSubscriptReturnType;
  
      //##ModelId=3C8742310264
      NestableContainer::Hook operator [] (const HIID &id) const
      { return Hook(*this,id,False); }

      //##ModelId=3C874250006A
      NestableContainer::Hook operator [] (const HIID &id)
      { return Hook(*this,id,True); }

      // static method called by ::Ref::operator [] to create a hook
      // from a const container reference
    //##ModelId=4017F62F02D6
      template<class T>
      static NestableContainer::Hook apply_subscript (const CountedRef<T> &ref,const HIID &id)
      { return Hook(ref.ref_cast(Type2Type<NestableContainer>()),id,False); }
      
      // static method called by ::Ref::operator [] to create a hook
      // from a non-const container reference
    //##ModelId=4017F63000ED
      template<class T>
      static NestableContainer::Hook apply_subscript (CountedRef<T> &ref,const HIID &id)
      { return Hook(ref.ref_cast(Type2Type<NestableContainer>()),id,True); }
      
        // declare inlined operator [] for other forms of HIIDs (see CountedRef.h)
    //##ModelId=4017F63002D9
      declareSubscriptAliases(NestableContainer::Hook,const);
    //##ModelId=4017F631016D
      declareSubscriptAliases(NestableContainer::Hook,);
        // declare inlined operator () to implicitly concatenate AtomicIDs (see CountedRef.h)
    //##ModelId=4017F6310253
      declareParenthesesAliases(NestableContainer::Hook,const);
    //##ModelId=4017F63103DF
      declareParenthesesAliases(NestableContainer::Hook,);
      
  protected:
      // helper function checks for type compatibility
    //##ModelId=4017F63200ED
      static bool checkTypes (TypeId check_tid,TypeId tid) 
      {
        return !check_tid || check_tid == tid  ||
               ( check_tid == TpObject && tid != TpObjRef ) ||
               ( check_tid == TpNumeric && TypeInfo::isNumeric(tid) );
      }


  private:
    //##ModelId=3DB934E200BE
      DeclareRegistry(NestableContainer,int,bool);

      //##ModelId=3F5D822702D6
      //##Documentation
      //## list of subscribers to container events
      std::list<Subscription> subscriptions;
      
    //##ModelId=3E7081A601A0
      Thread::Mutex mutex_;
};

// construct from container [HIID]
// The ncwrite argument is True if the container is non-const
//##ModelId=3C8739B50153
inline NestableContainer::Hook::Hook (const NestableContainer &parent,const HIID &id1,bool nonconst)
  : link0(parent,HIID()),
    ncref0(0)
{
  initialize(&parent,id1,nonconst);
}


// construct from container ref [HIID]
// The ncwrite argument is True if the ref object is non-const
//##ModelId=3C8739B5015E
inline NestableContainer::Hook::Hook (const NestableContainer::Ref &ref,const HIID &id1,bool refnonconst)
  : link0(*ref,HIID()),
    ncref0((refnonconst && !ref.isWritable())
             ? const_cast<NestableContainer::Ref *>(&ref) : 0)
{
  initialize(ref.deref_p(),id1,ref.isWritable());
}


inline NestableContainer::Hook::Hook (const NestableContainer &parent,const HIID &id1)
  : link0(parent,HIID()),
    ncref0(0)
{ 
  initialize(&parent,id1,False);
}

inline NestableContainer::Hook::Hook (NestableContainer &parent,const HIID &id1)
  : link0(parent,HIID()),
    ncref0(0)
{ 
  initialize(&parent,id1,True);
}


template<class T>
inline NestableContainer::Hook::Hook (const CountedRef<T> &ref,const HIID &id1)
  : nc(const_cast<NestableContainer *>(ref.ref_cast(Type2Type<NestableContainer>()).deref_p())),
    link0(*nc,HIID()),
    ncref0(0)
{
  initialize(nc,id1,False);
}


template<class T>
inline NestableContainer::Hook::Hook (CountedRef<T> &ref,const HIID &id1)
  : nc(const_cast<NestableContainer *>(ref.ref_cast(Type2Type<NestableContainer>()).deref_p())),
    link0(*nc,HIID()),
    ncref0(ref.isWritable() 
             ? reinterpret_cast<NestableContainer::Ref *>(&ref) : 0)
{ 
  initialize(nc,id1,True);
}


// Hook::operator & simply raises the addressed flag
//##ModelId=3C8739B50176
inline const NestableContainer::Hook & NestableContainer::Hook::operator & () const
{
  DbgFailWhen(addressed,"unexpected second '&' operator");
  addressed = True;
  return *this;
}

//##ModelId=4017F6240072
inline bool NestableContainer::Hook::exists () const
{
  return resolveTarget() != 0;
}

//##ModelId=4017F62400FB
inline TypeId NestableContainer::Hook::actualType () const
{
  return resolveTarget() ? target.tid : NullType;
}

//##ModelId=4017F6240190
inline bool NestableContainer::Hook::isContainer () const
{
  return resolveTarget() && target_nestable;
}

//##ModelId=4017F6240144
inline TypeId NestableContainer::Hook::containerType () const
{
  return isContainer() ? target.obj_tid : NullType;
}


//##ModelId=4017F62401D7
inline bool NestableContainer::Hook::isRef () const
{
  return resolveTarget() && target.tid == TpObjRef;
}

//##ModelId=3CAAE9BB0332
inline const NestableContainer::Hook & NestableContainer::Hook::size (int &sz, TypeId tid) const
{
  sz = size(tid);
  return *this;
}

//##ModelId=3C8770A70215
inline ObjRef NestableContainer::Hook::ref (int flags) const
{
  return ObjRef(*asRef(flags&DMI::WRITE),flags|DMI::COPYREF);
}

//##ModelId=3F5C8EBD01C4
inline const NestableContainer::Hook & NestableContainer::Hook::replace () const
{
  replacing = True;
  return *this;
}

//##ModelId=3C873AE302FC
inline const NestableContainer::Hook & NestableContainer::Hook::put (BlockableObject &obj, int flags) const
{
  assign_object(&obj,obj.objectType(),flags);
  return *this;
}

//##ModelId=3C873B8F01C2
inline const NestableContainer::Hook & NestableContainer::Hook::put (const BlockableObject &obj, int flags) const
{
  assign_object(&obj,obj.objectType(),flags);
  return *this;
}

//##ModelId=3C873B980248
inline const NestableContainer::Hook & NestableContainer::Hook::put (const ObjRef &ref, int flags) const
{
  assign_objref(ref,flags);
  return *this;
}

// const version of assign_object forces a read-only ref to be attached
//##ModelId=3DB934C600BA
inline void NestableContainer::Hook::assign_object( const BlockableObject *obj,TypeId tid,int flags ) const
{
  // cast away const but that's OK since we force r/o ref  
  return assign_object(const_cast<BlockableObject*>(obj),tid,(flags&~DMI::WRITE)|DMI::READONLY);
}


//##ModelId=4017F62300C1
inline NestableContainer::Hook::Link::Link (const NestableContainer &nc,const HIID &id1)
  : lock(nc.mutex()),id(id1)
{}

// // This applies the current subscript to the hook without updating the target
// //##ModelId=3DB934A30258
// inline const void * NestableContainer::Hook::collapseIndex (ContentInfo &info,TypeId check_tid,int flags) const
// {
//   const void *ret = index<0 
//       ? nc->get(id,info,check_tid,flags|autoprivatize)
//       : nc->getn(index,info,check_tid,flags|autoprivatize);
//   return ret;
// }
// 
#ifndef NC_SKIP_HOOKS
  #include <DMI/NC-Hooks-Templ.h>
#endif

#endif
