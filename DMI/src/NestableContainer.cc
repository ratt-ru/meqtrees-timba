#define NC_SKIP_HOOKS 1
#define NC_INCLUDE_VECTOR_HOOKS 1

#include "NestableContainer.h"
#include "DataArray.h"
#include "DataField.h"
    
#include <list>

// define some handy macros for throwing standard exceptions 
#define ThrowConvError(from,to) \
  ThrowExc(ConvError,"can't convert "+(from).toString()+" to "+(to).toString());

#define ThrowConvError1(from,to,ptr) \
  ThrowExc(ConvError,"can't convert "+(from).toString()+(ptr)+ " to "+(to).toString()+(ptr));

#define ThrowAssignError(from,to) \
  ThrowExc(ConvError,"can't assign "+(from).toString()+" to "+(to).toString());

#define ThrowReadOnly \
  ThrowExc(ReadOnly,"r/w access violation");

#define ThrowNotContainer \
  ThrowExc(NotContainer,"indexing into non-existing or non-container element");

#define ThrowUninitialized \
  ThrowExc(Uninitialized,"uninitialized element");

DefineRegistry(NestableContainer,False);

//##ModelId=4017F62300EF
int NestableContainer::Hook::_dum_int;
//##ModelId=4017F623014A
NestableContainer::ContentInfo NestableContainer::Hook::_dum_info;

// common init code for constructors
void NestableContainer::Hook::initialize (const NestableContainer *pnc,const HIID &id1,bool nonconst)
{
  nc = const_cast<NestableContainer *>(pnc);
  nclock0.relock(nc->mutex());
  nc_writable = nonconst;
  pid = 0;  // pid==0 implies initializing 
  ncptr0 = nc_writable ? nc : 0; 
  addressed = replacing = False;
  target.ptr = 0;
  // initialize via operator []. We don't initialize directly because
  // id may contain multiple subscripts (separated by slashes); hence let
  // operator [] comlete the initialization
  operator [] (id1);
}

//##ModelId=3C8739B50167
const NestableContainer::Hook & NestableContainer::Hook::operator [] (const HIID &id1) const
{
  DbgFailWhen(replacing,"can't apply subscript after replace()");
  DbgFailWhen(addressed,"can't apply subscript after '&' operator");
  // handle multiple-subscript IDs (i.e. containing slashes)
  if( !id1.empty() )
  {
    int nid = id1.size();
    int sep = id1.findFirstSlash();
    if( sep >= 0 )
    {
      if( !sep )                              // trim leading slash
        return (*this)[id1.subId(1)];
      else if( sep == nid-1 )                 // or trim trailing slash
        return (*this)[id1.subId(0,sep)];
      else                                    // or split in two and apply consecutively
        return (*this)[id1.subId(0,sep-1)][id1.subId(sep+1)];
    }
  }
  // If pid==0, we've been called from constructor, so just complete
  // the initialization
  if( pid == 0 ) 
  {
    pid = &link0.id;
    link0.id = id1;
    target.ptr = 0;
  }
  else // else apply current subscript and go on to next one
  {
    nextContainer(id1,False); // exception on error
  }
  return *this;
}

// This applies the current subscript to the hook, caching the result
// in target. Returns pointer to object.
// If hook resolves to an ObjRef and flags&DMI::NC_DEREFERENCE is set,
//    resolves the ref and returns pointer to object, else returns pointer 
//    to ref (==target.ptr).
// If flags&DMI::WRITE is set, ensures non-constness of the returned object, 
//    by privatizing as necessary, or throwing a ReadOnly exception if that 
//    is impossible. 
// All flags are passed to the get() method.
//##ModelId=4017F62501D7
inline const void * NestableContainer::Hook::resolveTarget (int flags,TypeId hint) const
{
  // A maximum of three passes:
  //    1. Current target doesn't match. get() is done but reports readonly,
  //       hook chain is privatized
  //    2. get() is repeated to obtain new target
  //    3. One more pass returns target
  // Anything more means complete failure
  for( int attempt = 0; attempt<3; attempt++ )
  {
    // have we already resolved to a target? 
    if( target.ptr )
    {
      // do we need to resolve refs? Writability to object is then determined
      // by the ref  rather than by the container
      if( flags&DMI::NC_DEREFERENCE && target.tid == TpObjRef )
      {
        ObjRef &ref = *static_cast<ObjRef*>(const_cast<void*>(target.ptr));
        // is writability OK? 
        if( flags&DMI::WRITE && !ref.isWritable() )
        {
          if( target.writable )  // not OK, but we can privatize
            return ref.privatize(DMI::WRITE).deref_p();
          // else ref is const so we can't privatize it. Try to privatize
          // the hook chain to ensure writability
          target.ptr = 0;
          resolveToWritableContainer(); // throws ReadOnly if not possible
          // fall through to re-query the now writable container
        }
        else
          return ref.deref_p();
      }
      else // writability is determined normally
      {
        if( !(flags&DMI::WRITE) || target.writable )
          return target.ptr;
        // non-writable -- fall through
      }
      // if we got here, this means that target was of a matching type, but
      // not writable, while DMI::WRITE is set. 
    }
    // (re)query the container
    target.tid = hint;
    int res = nc->get(*pid,target,nc_writable,flags);
    if( !res )       // return 0 if no such element
      return target.ptr = 0;
    // size<0 indicates a non-writable target; we need to make the container
    // writable and try again
    if( res<0 )
    {
      target.ptr = 0;
      resolveToWritableContainer(); // throws ReadOnly if not possible
    }
    else // target ok, set the nestable flag
      target_nestable = isNestable(target.obj_tid);
    // go back to resolve target at top of loop
  }
  // we should never-ever-ever get here!
  ThrowExc(Inconsistency,"resolveTarget: unexpected failure after two attempts");
}

// helper function applies current subscript to hook in preparation
// for setting a new one. Insures that current target is a container.
//##ModelId=4017F6250392
bool NestableContainer::Hook::nextContainer (const HIID &next_id,bool nothrow) const
{
  resolveTarget();
  // check that we get back a valid ref to a container
  if( !target.ptr )
  {
    if( nothrow ) return False;
    else          ThrowExc(NotContainer,"indexing into non-existing element");
  }
  if( target.tid != TpObjRef || !target_nestable )
  {
    if( nothrow ) return False;
    else          
      ThrowExc(NotContainer,"indexing into a "+
                target.obj_tid.toString()+": not a container");
  }
  NestableContainer::Ref &ref = 
      *static_cast<NestableContainer::Ref *>(const_cast<void*>(target.ptr));
  if( !ref.valid() )
  {
    if( nothrow ) return False;
    else          
      ThrowExc(NotContainer,"indexing into a "+
                target.obj_tid.toString()+": not a valid ref");
  }
  NestableContainer *newnc = const_cast<NestableContainer *>(ref.deref_p());
  bool new_writable = ref.isWritable();
  // figure out which chain scenario we're dealing with here --
  // see comments in NestableContainer.h, next to the chain member declaration.
  // (1) new container is nonconst; becomes base of chain (case [a] or [d])
  if( new_writable )
  {
    ncref0 = 0;   
    ncptr0 = newnc;
    nclock0.relock(nc->mutex()); // always keep a lock on the parent container 
    link0.lock.relock(newnc->mutex()); 
    pid = &link0.id;
    chain.clear();
  }
  // (2) new container is const but ref to it is nonconst -- current ref 
  // becomes base of chain
  else if( target.writable )
  {
    ncref0 = &ref;
    ncptr0 = 0;
    nclock0.relock(nc->mutex()); // always keep a lock on the parent container 
    link0.lock.relock(newnc->mutex());
    pid = &link0.id;
    chain.clear();
  }
  // (3) both are const. If we have a chain, add container to its end.
  // Otherwise, keep reusing link0, since there's no chain
  else 
  {
    Link *plink;
    // if ncref0 or ncptr0 != 0, then we have a chain rooted at a nonconst
    // something, so add new container to it
    if( ncref0 || ncptr0 )
    {
      chain.push_back(Link());
      plink = &( chain.back() );
    }
    // else no chain, so keep reusing link0.
    else  
    {
      nclock0.relock(nc->mutex()); // always keep a lock on the parent container 
      plink = &link0;
    }
    plink->lock.relock(newnc->mutex());
    pid = &plink->id;
  }
  // move to the next container and clear the target
  nc = newnc;
  nc_writable = new_writable;
  target.ptr = 0;
  // set new indices
  *pid = next_id;
  return True; // success
}

// ensures that current NC is writable, by privatizing the hook chain
// as necessary. See comments in NestableContainer.h, next to the Hook::chain
// declaration. Those comments outline scenarios (a) to (d) which we refer
// to here
//##ModelId=4017F62600FF
void NestableContainer::Hook::resolveToWritableContainer() const
{
  if( nc_writable ) // (a): current nc is already writable, do nothing
  {
    DbgAssert(!ncref0);
    DbgAssert(chain.empty());
    return;
  }
  if( ncref0 ) // (b): base of chain is non-const ref, privatize to get container
  {
    ncptr0 = ncref0->privatize(DMI::WRITE).dewr_p();
    link0.lock.relock(ncptr0->mutex());
    ncref0 = 0;
  }
  else if( !ncptr0 ) // (d): no chain, fail completely
  {
    DbgAssert(chain.empty());
    ThrowReadOnly;
  }
  HIID id0 = *pid;
  // At this point, ncptr0 points to a writable container corresponding to link0
  // in the chain. If the chain is empty, then this is simply the current 
  // container. Else start privatizing down the chain
  nc = ncptr0;
  pid = &link0.id;
  nc_writable = True;
  target.ptr = 0;
  while( !chain.empty() )
  {
    ContentInfo info;
    // index into current link, expect an ObjRef back
    int ret = ncptr0->get(link0.id,info,True,0);
    #define ThrowChainFail(str) \
        ThrowExc(Inconsistency,(str)+string(" while privatizing container chain"));
    if( ret<0 || !info.writable )
      ThrowChainFail("r/o link ["+link0.id.toString()+"]");
    if( !ret )
      ThrowChainFail("missing link ["+link0.id.toString()+"]");
    if( info.tid != TpObjRef )
      ThrowChainFail("link ["+link0.id.toString()+"] has unexpected type "+info.tid.toString());
    // privatize the ref and get writable container from it
    ObjRef &ref = *static_cast<ObjRef*>(const_cast<void*>(info.ptr));
    ref.privatize(DMI::WRITE);
    NestableContainer *nc1 = dynamic_cast<NestableContainer *>(ref.dewr_p());
    if( !nc1 )
      ThrowChainFail("link ["+link0.id.toString()+"] not a container");
    // advance to next chain element
    nclock0.relock(ncptr0->mutex());
    link0.lock.relock((nc=ncptr0=nc1)->mutex());
    link0.id = chain.front().id;
    chain.pop_front();
  }
  // once we get here, we're all set
}

//##ModelId=4017F62400B7
TypeId NestableContainer::Hook::type () const
{
  const void *targ = resolveTarget(DMI::NC_DEREFERENCE);
  if( !targ )
    return 0;
  // not container? Return object type
  else if( !target_nestable )
    return target.obj_tid;
  //  else look in container for type
  TypeId type = static_cast<const NestableContainer *>(targ)->type();
  // if container is of a fixed content type, return that, else 
  // return container's own object type
  return type ? type : target.obj_tid;
}

//##ModelId=3CAB0A3500AC
int NestableContainer::Hook::size (TypeId tid) const
{
  const void *targ = resolveTarget(DMI::NC_DEREFERENCE,tid);
  if( !targ )
    return 0;
  else if( target.obj_tid == tid ) // target matches type? return 1
    return 1;
  else if( target_nestable )
    return static_cast<const NestableContainer *>(targ)->size(tid);
  else
    return target.size;
}

// This is called to treat the hook target as an ObjRef (exception otherwise)
// If write is true, assures writability to the ref (i.e. container
// writability)
//##ModelId=4017F62500F7
const ObjRef * NestableContainer::Hook::asRef (bool write) const
{
  DbgFailWhen(addressed,"unexpected '&' operator");
  // check for element
  resolveTarget(write?DMI::WRITE:0);
  FailWhen(!target.ptr,"element does not exist");
  FailWhen(target.tid!=TpObjRef,"hook does not refer to a ref");
  return static_cast<const ObjRef*>(target.ptr);
}

// This is called to treat the hook target as an ObjRef (exception otherwise).
// If write is true, assures writability of ref itself
//##ModelId=3C8770A70215
inline ObjRef NestableContainer::Hook::ref (bool write) const
{
  DbgFailWhen(addressed,"unexpected '&' operator");
  // resolve to ref first, to check types
  resolveTarget();
  FailWhen(!target.ptr,"element does not exist");
  FailWhen(target.tid!=TpObjRef,"hook does not refer to a ref");
  // resolve to writable object -- this will privatize as necessary
  const BlockableObject *pobj = static_cast<const BlockableObject*>
      ( resolveTarget(DMI::NC_DEREFERENCE|(write?DMI::WRITE:0)) );
  FailWhen(!pobj,"element does not exist");
  // attach ref and return. cast away const when attaching, since 
  // writability (if needed) is ensured above
  return ObjRef(const_cast<BlockableObject*>(pobj),write?DMI::WRITE:0);
}

// This is called to access by pointer, for all types
// Defers to get_address(pointer=True)
//##ModelId=4017F62702A0
const void * NestableContainer::Hook::get_pointer (int &sz,
    TypeId tid,bool must_write,bool implicit,
    bool must_exist,Thread::Mutex::Lock *keeplock) const
{
  DbgFailWhen(!addressed && implicit,"missing '&' operator");
  // Defers to get_address(pointer=True)
  ContentInfo info;
  const void *ret = get_address(info,tid,must_write,True,must_exist,keeplock);
  sz = info.size;
  return ret;
}

//##ModelId=3C8739B5017B
const NestableContainer::Hook & NestableContainer::Hook::init (TypeId tid) const
{
  DbgFailWhen(addressed,"unexpected '&' operator");
  ContentInfo info;
  prepare_put(info,tid);
  return *this;
}

//##ModelId=3C8739B5017C
const NestableContainer::Hook & NestableContainer::Hook::privatize (int flags) const
{
  DbgFailWhen(addressed,"unexpected '&' operator");
  // resolve to non-const ref
  ObjRef &ref = *const_cast<ObjRef*>( asRef(True) );
  ref.privatize(flags);
  return *this;
}

//##ModelId=4017F624023A
const NestableContainer::Hook & NestableContainer::Hook::attachObjRef (ObjRef &out,int flags) const
{
  DbgFailWhen(addressed,"unexpected '&' operator");
  // resolve to ref
  out = ref((flags&DMI::WRITE)!=0);
//  const ObjRef *ref = asRef(False);
//   DbgAssert(ref);
//   // if we want a writable ref but this one is r/o, re-resolve to 
//   // a non-const ref
//   if( flags&DMI::WRITE && !ref->isWritable() )
//   {
//     ref = asRef(True);
//     const_cast<ObjRef*>(ref)->privatize(flags);
//   }
//   // copy ref to output ref
//   out.copy(*ref,flags);
  return *this;
}

//##ModelId=4017F625031C
void * NestableContainer::Hook::removeTarget () const
{
  resolveToWritableContainer();
  nc->remove(*pid);
  target.ptr = 0;
  return 0; 
}


//##ModelId=3C876DCE0266
ObjRef NestableContainer::Hook::remove () const
{
  DbgFailWhen(addressed,"unexpected '&' operator");
  // ensure writability to container
  if( !nc_writable )
    resolveToWritableContainer();
  ObjRef ret;
  if( isRef() )
  {
    ret.xfer(const_cast<ObjRef*>(asRef(True))->unlock());
  }
  nc->remove(*pid);
  target.ptr = 0;
  return ret;
}

//##ModelId=3C876E140018
const NestableContainer::Hook & NestableContainer::Hook::detach (ObjRef* ref) const
{
  DbgFailWhen(addressed,"unexpected '&' operator");
  // ensure writability to container
  if( !nc_writable )
    resolveToWritableContainer();
  ObjRef *ref0 = const_cast<ObjRef*>(asRef(True));
  ref0->unlock();
  if( ref )
    ref->xfer(*ref0);
  else
    ref0->detach();
  target.obj_tid = 0;
  return *this;
}

// This is called to get a value, for built-in scalar types only.
// Automatic conversion is done between numeric types.
// If no such element exists: if must_exist=True, throws 
// an Uninitialized exception, else returns False
// Always throws ConvError on type mismatch.
//##ModelId=4017F626017A
bool NestableContainer::Hook::get_scalar( void *data,TypeId tid,bool must_exist ) const
{
  DbgFailWhen(addressed,"unexpected '&' operator");
  int flags = DMI::NC_DEREFERENCE;
  // We do two attempts to access the hook. If the current target is of
  // the wrong type but happens to be a subcontainer, then we move the
  // target to the subcontainer and attempt another access with HIID().
  // Any error during the first attempt is re-thrown as is;
  // during the second attempt it is rethrown as a conversion error.
  for( int attempt=0; attempt<2; attempt++ )
  {
    // resolve hook target
    const void *targ;
    try { targ = resolveTarget(flags,tid); }
    catch ( std::exception &exc ) {
      if( attempt ) break; 
      else          throw(exc);
    } 
    if( !targ )
    {
      if( must_exist ) 
        ThrowUninitialized;
      return False;
    }
    // if target is not a container, attempt the conversion
    // this should work for all numerics and single-element arrays
    if( !target_nestable )
    {
      if( !TypeInfo::convert(targ,target.tid,data,tid) )
        ThrowConvError(target.tid,tid);
      return True;
    }
    // else try to treat it as a container
    if( !attempt )
    {
      if( !nextContainer(HIID()) ) // not a container? throw conversion error
        ThrowConvError(target.obj_tid,tid);
    }
  }
  // if we got to here, we have a conversion error
  ThrowConvError(target.obj_tid,tid);
}

// This is called to access by reference, for all types
// If pointer is True, then a pointer is being taken
//##ModelId=4017F6260346
const void * NestableContainer::Hook::get_address (ContentInfo &info,
    TypeId tid,bool must_write,bool pointer,
    bool must_exist,Thread::Mutex::Lock *keeplock) const
{
  // we ask the container for an ObjRef or just an object
  int flags = (tid==TpObjRef ? 0 : DMI::NC_DEREFERENCE) |
              (must_write    ? DMI::WRITE : 0);
  // We do two attempts a-la get_scalar() above
  for( int attempt=0; attempt<2; attempt++ )
  {
    const void *targ;
    try { targ = resolveTarget(flags,tid); }
    catch ( std::exception &exc ) {
      if( attempt ) break; 
      else          throw(exc);
    } 
    // fail if no such element, unless a default is provided
    if( !targ )
    {
      if( must_exist ) 
        ThrowUninitialized;
      return 0;
    }
    // success: types match
    if( tid == TpObjRef || tid == target.obj_tid )
    {
      if( target.size > 1 && !pointer )
        ThrowExc(ConvError,"accessing array of "+target.obj_tid.toString()+" as a scalar");
      info = target;
      // set lock if asked to
      if( keeplock )
      {
        if( chain.empty() )
          *keeplock = link0.lock;
        else
          *keeplock = chain.back().lock;
      }
      return targ;
    }
    // else try to treat the target as a container 
    if( !attempt )
    {
      if( !nextContainer(HIID()) ) // not a container? throw conversion error
        ThrowConvError1(target.obj_tid,tid,(pointer?"*":""));
    }
  }
  // if we got to here, we have a conversion error
  ThrowConvError1(target.obj_tid,tid,(pointer?"*":""));
}

// This prepares the hook for assignment, by resolving to the target element,
// and failing that, trying to insert() a new element.
// The actual type of the target element is returned via info.tid. 
// Normally, this will be ==tid (or a ConvError will be thrown by the
// container), unless:
// (a) tid==TpObjRef: info.tid must contain required object type on entry
//     Return value will be a pointer to the ObjRef. Note that all
//     dynamic objects must be assigned this way.
// (b) tid & container type are both numeric (caller is expected to 
//     do the conversion)
// For other type categories, a strict match should be enforced by the container.
//##ModelId=3DB934C00071
void * NestableContainer::Hook::prepare_put( ContentInfo &info,TypeId tid ) const
{
  // verify correct assignments
  DbgFailWhen(TypeInfo::isDynamic(tid),"dynamic types must be assigned via ObjRef");
  DbgFailWhen(tid==TpObjRef && !TypeInfo::isDynamic(info.tid),"assigning via ObjRef to non-dynamic type");
  DbgFailWhen(addressed,"unexpected '&' operator");
  void *targ = 0;
  TypeId real_tid = tid == TpObjRef ? info.tid : tid; 
  int flags = (tid==TpObjRef ? 0 : DMI::NC_DEREFERENCE)
              |DMI::WRITE|DMI::NC_ASSIGN;
  // as usual, two attempts (see comments in functions above)
  for( int attempt=0; attempt<2; attempt++ )
  {
    // resolve to hook target, make it writable
    try { targ = const_cast<void*>(resolveTarget(flags,tid)); }
    catch ( std::exception &exc ) {
      if( attempt ) break; 
      else          throw(exc);
    } 
    // no such element: attempt an insert on the current container
    if( !targ )
    {
      // ensure writability
      resolveToWritableContainer();
      target.tid = tid;
      target.obj_tid = real_tid;      
      nc->insert(*pid,target);  // exception on failure
      targ = const_cast<void*>(target.ptr);
    }
    info = target;
    // if we get here, then the hook points to an existing, writable element. 
    // This is either a matching type, or a subcontainer
    if( tid == TpObjRef && target.tid == TpObjRef )
    {
      // check for type compatibility, if container enforces types.
      // Also check that either ref is empty, or is of the same type,
      // or replacement is allowed.
      TypeId nctype = nc->type();
      if( ( !nctype || real_tid == nctype ) &&
          ( !target.obj_tid || target.obj_tid == real_tid || replacing ) )
        return targ;
    }
    // matching type, or both are numeric -- return target
    else if( tid == target.obj_tid || TypeInfo::isConvertible(tid,target.tid) )
      return targ;
    // non-matching type but replacement is allowed -- try a remove/insert 
    else if( replacing )
    {
      removeTarget();
      target.tid = tid; target.obj_tid = real_tid;
      nc->insert(*pid,target);  // exception on failure
      info = target;
      return const_cast<void*>(target.ptr);
    }
    if( !attempt )
    {
      // if we got here, then we're dealing with a non-matching type. Try to 
      // treat it as a subcontainer, move on to it and try again
      if( !nextContainer(HIID()) ) // not a container? throw conversion error
        ThrowAssignError(real_tid,target.obj_tid);
    }
  }
  // got here? fail everything then
  ThrowAssignError(real_tid,target.tid);
}

// This is called to assign a value, for scalar & binary types
//##ModelId=3DB934C102D5
const void * NestableContainer::Hook::put_scalar( const void *data,TypeId tid,size_t sz ) const
{
  ContentInfo info;
  void *targ = prepare_put(info,tid);
  // if types don't match, it must be a scalar, use conversion
  if( tid != info.tid )
  {
    if( !TypeInfo::convert(data,tid,targ,info.tid) )
      ThrowConvError(tid,info.tid);
  }
  else // else it's a binary type, use copy
    memcpy(const_cast<void*>(targ),data,sz);
  return targ;
}

// Helper function to assign an object.  
//##ModelId=3DB934C30364
void NestableContainer::Hook::assign_object( BlockableObject *obj,TypeId tid,int flags ) const
{
  ContentInfo info;
  info.tid = tid;
  void *targ = prepare_put(info,TpObjRef);
  static_cast<ObjRef*>(targ)->unlock().attach(obj,flags).lock();
  target.ptr = 0;
}

// Helper function assigns an objref     
//##ModelId=3DB934C801DF
ObjRef & NestableContainer::Hook::assign_objref ( const ObjRef &ref,int flags ) const
{
  ContentInfo info;
  info.tid = ref->objectType();
  void *targ = prepare_put(info,TpObjRef);
  target.ptr = 0;
  if( flags&DMI::COPYREF )
    return static_cast<ObjRef*>(targ)->unlock().copy(ref,flags).lock();
  else
    return static_cast<ObjRef*>(targ)->unlock().xfer(const_cast<ObjRef&>(ref)).lock();
}

// This prepares the hook for assigning a Lorray.
// Will return 0 if hook points to an uninitialized element.
// Otherwise, attemps to access the hook target. If it's an array of
// matching type/rank, returns pointer to array object and sets 
// haveArray=True (*does not check for shape match!*). If rank is 1 and 
// hook points to a block of contiguous scalars of matching size, returns 
// pointer to first element and sets haveArray=False. If it's a subcontainer, 
// repeats previous steps for the subcontainer. Otherwise throws a ConvError.
//##ModelId=3E7081A50350
void * NestableContainer::Hook::prepare_assign_array (bool &haveArray,TypeId tid,const LoShape &shape) const
{
  DbgFailWhen(addressed,"unexpected '&' operator");
  TypeId tidarr = TpArray(tid,shape.size());
  int flags = DMI::NC_DEREFERENCE|DMI::WRITE|DMI::NC_ASSIGN;
  // as usual, two attempts (see comments in functions above)
  for( int attempt=0; attempt<2; attempt++ )
  {
    // resolve to writable object
    void *targ;
    try { targ = const_cast<void*>( resolveTarget(flags,tidarr) ); }
    catch ( std::exception &exc ) {
      if( attempt ) break; 
      else          throw(exc);
    } 
    if( !targ  )   // non-existing object
      return 0; 
    // got an array? check shapes, etc.
    if( TypeInfo::isArray(target.tid) )
    {
      // array matches
      if( target.tid == tidarr )
      {
        haveArray = True;
        return targ;
      }
      // no match -- remove if replacing and return 0, else fail
      if( replacing )
        return removeTarget();
      ThrowAssignError(tidarr,target.tid);
    }
    // else got pointer to scalar
    else if( target.tid == tid )
    {
      // we must thenn be expecting a 1D array of that exact shape
      if( shape.size() > 1 || target.size != shape[0] )
        ThrowExc(ConvError,"can't assign "+tidarr.toString()+": shape mismatch");
      haveArray = False;
      return targ;
    }
    // else if we have an ObjRef, and replacing is enabled, then just remove
    // the damn thing and return 0
    else if( target.tid == TpObjRef && replacing )
      return removeTarget();
    // last option is resolving to an existing sub-container. Try to move the
    // hook to this container, and throw exceptions on failure
    else if( !attempt )
    {
      if( !nextContainer(HIID()) ) // not a container? throw conversion error
        ThrowAssignError(tidarr,target.obj_tid);
    }
  }
  // got to here? fail assignment then
  ThrowAssignError(tidarr,target.obj_tid);
}

// This provides a specialization of operator = (vector<T>) for arrayable
// types. The difference is that a DataArray is initialized rather
// than a DataField, and that vector<T> may be assigned to an Array(T,1), 
// if that's what the hook is pointing at
template<class T,class Iter> 
void NestableContainer::Hook::assign_arrayable (int size,Iter begin,Iter end,Type2Type<T>) const
{
  bool haveArray;
  // call method above to prepare for assignment
  void * targ = prepare_assign_array(haveArray,typeIdOf(T),LoShape(size));
  T *ptr;
  // non-existing object: try to a initialize a new DataArray
  if( !targ )
  {
    NestableContainer *darr = new DataArray(typeIdOf(T),LoShape(size),DMI::WRITE);
    ObjRef ref(darr,DMI::ANONWR);
    ContentInfo info;
    info.tid = typeIdOf(T);
    int res = darr->get(HIID(),info,True,DMI::WRITE);
    DbgAssert(res>0 && info.ptr && info.tid == typeIdOf(T) );
    ptr = static_cast<T*>( const_cast<void*>(info.ptr) );
    haveArray = False;
    assign_objref(ref,0);
  }
  // hook has resolved to a 1D array -- check shapes and copy
  else if( haveArray ) 
  {
    // NB: typeinfo should incorporate mapping between array types and
    // numeric types
    blitz::Array<T,1> *arr = static_cast<blitz::Array<T,1>*>(targ);
    if( arr->shape()[0] != size )
      ThrowExc(ConvError,
          Debug::ssprintf("can't assign vector:%d to array:%d",size,arr->shape()[0]));
    typename blitz::Array<T,1>::iterator iarr = arr->begin();
    for( ; begin != end; ++begin,++iarr )
      *iarr = *begin;
    return;
  }
  // else we've resolved to a contiguous block of elements of the right size
  else
    ptr = static_cast<T*>(targ);
  // copy over array data
  for( ; begin != end; ++begin,++ptr )
    *ptr = *begin;
}

// provide instantiations of assign_arrayable for vectors of all arrayable types
#define __inst(T,arg) template void NestableContainer::Hook::assign_arrayable \
  (int, std::vector<T>::const_iterator, \
        std::vector<T>::const_iterator, Type2Type<T>) const;
DoForAllArrayTypes(__inst,);
#undef __inst

//##ModelId=4017F6280225
void * NestableContainer::Hook::prepare_assign_vector (TypeId tid,int size) const
{
  DbgFailWhen(addressed,"unexpected '&' operator");
  int flags = DMI::NC_DEREFERENCE|DMI::WRITE|DMI::NC_ASSIGN;
  // as usual, two attempts (see comments in functions above)
  for( int attempt=0; attempt<2; attempt++ )
  {
    // resolve to writable object
    void *targ;
    try { targ = const_cast<void*>( resolveTarget(flags,tid) ); }
    catch ( std::exception &exc ) {
      if( attempt ) break; 
      else          throw(exc);
    } 
    if( !targ  )   // non-existing object? 
      return 0;
    // got pointer to scalar? 
    if( target.tid == tid )
    {
      if( size == target.size ) 
        return targ;
      else if( replacing ) 
        return removeTarget();
      else {
        ThrowExc(ConvError,"can't assign vector of "+tid.toString()+": size mismatch");
      }
    }
    // else if we have an ObjRef, and replacing is enabled, then just remove
    // the damn thing and return 0
    else if( target.tid == TpObjRef && replacing )
    {
      return removeTarget();
    }
    // last option is resolving to an existing sub-container. Try to move the
    // hook to this container, and throw exceptions on failure
    else if( !attempt )
    {
      if( !nextContainer(HIID()) ) // not a container? throw conversion error
        ThrowAssignError(tid,target.obj_tid);
    }
  }
  // got to here? fail assignment then
  ThrowAssignError(tid,target.obj_tid);
}


// This provides a specialization of operator = (vector<T>) for non-arrayable
// types.
//##ModelId=4017F62803A9
void * NestableContainer::Hook::assign_vector (TypeId tid,int size) const
{
  // call method above to prepare for assignment
  void * targ = prepare_assign_vector(tid,size);
  if( targ )
    return targ;
  // else non-existing object: try to a initialize a new DataField
  NestableContainer *df = new DataField(tid,size);
  ObjRef ref(df,DMI::ANONWR);
  assign_objref(ref,0);
  ContentInfo info; 
  info.tid = tid;
  int res = df->get(HIID(),info,True,DMI::WRITE);
  DbgAssert(res>0 && info.ptr && info.tid == tid );
  return const_cast<void*>(info.ptr);
}

//##ModelId=3DB934BC01D9
string NestableContainer::Hook::sdebug ( int detail,const string &prefix,const char *name ) const
{
  if( !name )
    name = "Hook";
  string out;
  out = ssprintf("%s%s[%s]",name,addressed?"&":"",nc->sdebug(detail,prefix).c_str());
  out += "["+pid->toString()+"]"; 
  return out;  
}

// Assigns hook to hook
// void NestableContainer::Hook::operator = (const NestableContainer::Hook &hook )
// {
//   ContentInfo info;
//   const void *source;
//   // resolve hook to target element
//   if( hook.index >=0 || hook.id.size() )
//   {
//     source = hook.collapseIndex(info,0,0);
//     FailWhen( !source,"uninitialized element");
//   }
//   else
//   {
//     // assign container as object
//     // BUG: must check for writability here!
//     assign_object(const_cast<BlockableObject*>(hook.nc),hook.nc->objectType(),
//                   DMI::READONLY);
//     return;
//   }
//   // is it an objref? Assign a copy
//   if( info.tid == TpObjRef )
//   {
//     assign_objref(*static_cast<const ObjRef *>(source),DMI::COPYREF|DMI::PRESERVE_RW);
//   }
//   else 
//   {
//     // lookup type info
//     const TypeInfo & ti = TypeInfo::find(info.tid);
//     switch( ti.category )
//     {
//       case TypeInfo::NUMERIC:
//       case TypeInfo::BINARY:  // numeric or binary -- assign scalar or vector
//           if( info.size == 1 )
//             put_scalar(source,info.tid,ti.size);
//           else
//           {
//             void *target = prepare_vector(info.tid,info.size);
//             memcpy(target,source,info.size*ti.size);
//           }
//           break;
//           
//       case TypeInfo::SPECIAL: // special type -- use TypeInfo's copy method
//           if( info.size == 1 )
//           {
//             ContentInfo putinfo;
//             void *target = prepare_put(putinfo,info.tid);
//             (*ti.CopyMethod)(target,source);
//           }
//           else
//           {
//             char *target = static_cast<char*>(prepare_vector(info.tid,info.size));
//             const char *src = static_cast<const char*>(source);
//             for( int i=0; i<info.size; i++ )
//             {
//               (*ti.CopyMethod)(target,src);
//               target += ti.size;
//               src += ti.size;
//             }
//           }
//           break;
//           
//       case TypeInfo::DYNAMIC: // dynamic object -- attach ref
//           // cast away const is OK since we enforce the right set of flags
//           assign_object(static_cast<BlockableObject*>(const_cast<void*>(source)),
//                         info.tid,info.writable?DMI::WRITE:DMI::READONLY);
//           break;
//           
//       case TypeInfo::INTERMEDIATE:
//           Throw("assignment of Arrays not supported yet");
//           // special case for handling arrays
// //           if( TypeInfo::isArray(info.tid) )
// //           {
// //             bool haveArray;
// //             void *target = prepare_assign_array(haveArray,info.tid,
// //             
// //           }
//           // else fall through to throw below
//       default:
//           Throw("don't know how to assign RHS of this expression");
//     }
//   }
// }

