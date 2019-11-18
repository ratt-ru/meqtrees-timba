//
//% $Id$ 
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation & 
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc., 
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

#define NC_SKIP_HOOKS 1
#define NC_INCLUDE_VECTOR_HOOKS 1
#include <csignal>
#include "Container.h"
#include "NumArray.h"
#include "Vec.h"
    
#include <list>

// define some handy macros for throwing standard exceptions 
#define ConvErrorMessage(from,to) "can't convert "+(from)+" to "+(to)
    
#define ThrowConvError(from,to) \
  ThrowExc(ConvError,ConvErrorMessage((from).toString(),(to).toString()))

#define ThrowConvError1(from,to,ptr) \
  ThrowExc(ConvError,ConvErrorMessage((from).toString()+(ptr),(to).toString()+(ptr)));

#define ThrowAssignError(from,to) \
  ThrowExc(ConvError,"can't assign "+(from).toString()+" to "+(to).toString());

#define ThrowReadOnly \
  ThrowExc(ReadOnly,"r/w access violation");

#define ThrowNotContainer \
  ThrowExc(NotContainer,"indexing into non-existing or non-container element");

#define ThrowUninitialized \
  ThrowExc(Uninitialized,"uninitialized element");

DefineRegistry(DMI::Container,false);

//##ModelId=4017F62300EF
int DMI::Container::Hook::_dum_int;
//##ModelId=4017F623014A
DMI::Container::ContentInfo DMI::Container::Hook::_dum_info;

// inline function to convert IDs to strings of form ["id"] 
static inline string idToString (const DMI::HIID &id)
{
  if( id.empty() )
    return "[]";
  return "[" + id.toString() + "]";
}


// common init code for constructors
void DMI::Container::Hook::initialize (const DMI::Container *pnc,const HIID &id1,bool nonconst)
{
  nc = const_cast<DMI::Container *>(pnc);
  nclock0.relock(nc->mutex());
  nc_writable = nonconst;
  pid = 0;  // pid==0 implies initializing 
  ncptr0 = nc_writable ? nc : 0; 
  addressed = replacing = false;
  target.ptr = 0;
  // initialize via operator []. We don't initialize directly because
  // id may contain multiple subscripts (separated by slashes); hence let
  // operator [] complete the initialization
  operator [] (id1);
}

//##ModelId=3C8739B50167
const DMI::Container::Hook & DMI::Container::Hook::operator [] (const HIID &id1) const
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
    nextContainer(id1,false); // exception on error
  }
  return *this;
}

// This applies the current subscript to the hook, caching the result
// in target. Returns pointer to object.
// If hook resolves to an ObjRef and flags&DMI::DEREFERENCE is set,
//    resolves the ref and returns pointer to object, else returns pointer 
//    to ref (==target.ptr)
// If flags&DMI::WRITE is set, ensures non-constness of the returned object, 
//    by privatizing as necessary, or throwing a ReadOnly exception if that 
//    is impossible. 
// All flags are passed to the get() method.
//##ModelId=4017F62501D7
const void * DMI::Container::Hook::resolveTarget (int flags,TypeId hint) const
{
  bool writing = flags&DMI::WRITE;
  // container is const, but writing is required: try to resolve to a writable 
  // container. This will go back and attempt to privatize the ref chain
  if( writing && !nc_writable )
  {
    target.ptr = 0;
    resolveToWritableContainer(); // throws ReadOnly if not possible
  }
  // query container if no target
  if( !target.ptr )
  {
    target.tid = hint;
    if( !nc->get(*pid,target,nc_writable,flags) )
      return 0;
    target_nestable = isNestable(target.obj_tid);
  }
  // do we need to resolve refs? 
  if( flags&DMI::DEREFERENCE && target.tid == TpDMIObjRef )
  {
    ObjRef &ref = *static_cast<ObjRef*>(const_cast<void*>(target.ptr));
    if( !ref.valid() )
      return 0;
    // the code above already ensures that container itself is writable if necessary, 
    // so we can deref for writing and assume COW will do its thing
    return writing ? ref.dewr_p() : ref.deref_p();
  }
  // no need to resolve, just return target
  return target.ptr;
}

// helper function applies current subscript to hook in preparation
// for setting a new one. Insures that current target is a container.
//##ModelId=4017F6250392
bool DMI::Container::Hook::nextContainer (const HIID &next_id,bool nothrow) const
{
  
  // apply index so that we resolve the hook to a target
  resolveTarget();
  // check that we get back a valid ref to a container
  if( !target.ptr )
  {
    if( nothrow ) return false;
    else          ThrowExc(NotContainer,"indexing into non-existing element");
  }
  if( target.tid != TpDMIObjRef || !target_nestable )
  {
    if( nothrow ) return false;
    else          
      ThrowExc(NotContainer,"indexing into a "+
                target.obj_tid.toString()+", which is not a container");
  }
  DMI::Container::Ref &ref = 
      *static_cast<DMI::Container::Ref *>(const_cast<void*>(target.ptr));
  if( !ref.valid() )
  {
    if( nothrow ) return false;
    else          
      ThrowExc(NotContainer,"indexing into a "+
                target.obj_tid.toString()+", but not a valid ref");
  }
  DMI::Container *newnc = const_cast<DMI::Container *>(ref.deref_p());
//  bool new_writable = nc_writable && ref.isDirectlyWritable();
  // figure out which chain scenario we're dealing with here --
  // see comments in Container.h, next to the chain member declaration.
  // (1) current container is non-const
  if( nc_writable )
  {
    // (1a) new container is also non-const; becomes base of chain (case [a] or [d])
    if( ref.isDirectlyWritable() )
    {
      ncref0 = 0;   
      ncptr0 = newnc;
      nclock0.relock(nc->mutex()); // always keep a lock on the parent container 
      link0.lock.relock(newnc->mutex()); 
      pid = &link0.id;
      chain.clear();
    }
    // (1b) new container is const -- current becomes base of chain
    else 
    {
      nc_writable = false;
      ncref0 = &ref;
      ncptr0 = 0;
      nclock0.relock(nc->mutex()); // always keep a lock on the parent container 
      link0.lock.relock(newnc->mutex());
      pid = &link0.id;
      chain.clear();
    }
  }
  // (2) both are const. If we have a chain, add container to its end.
  // Otherwise, keep reusing link0, since there's no chain at all
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
  target.ptr = 0;
  // set new indices
  *pid = next_id;
  return true; // success
}

// Tries to make current NC writable, by running through the hook chain again, dereferencing
// for writing along the way (which causes COW to do its thing). 
// See comments in Container.h, next to the Hook::chain member declaration.
// Those comments outline scenarios (a) to (d) which we refer to here
//##ModelId=4017F62600FF
void DMI::Container::Hook::resolveToWritableContainer() const
{
  if( nc_writable ) // (a): current nc is already writable, do nothing
  {
    DbgAssert(!ncref0);
    DbgAssert(chain.empty());
    return;
  }
  if( ncref0 ) // (b): base of chain is non-const ref, deref for writing (COW) to get container
  {
    ncptr0 = ncref0->dewr_p();
    link0.lock.relock(ncptr0->mutex());
    ncref0 = 0;
  }
  else if( !ncptr0 ) // (d): no chain, fail completely
  {
    DbgAssert(chain.empty());
    ThrowReadOnly;
  }
  HIID id0 = *pid;
  // At this point, ncptr0 points to a non-const container corresponding to link0
  // in the chain. If the chain is empty, then this is simply the current 
  // container. Else start privatizing down the chain
  nc = ncptr0;
  pid = &link0.id;
  nc_writable = true;
  target.ptr = 0;
  while( !chain.empty() )
  {
    ContentInfo info;
    // index into current link, expect an ObjRef back
    int ret = ncptr0->get(link0.id,info,true,0);
    #define ThrowChainFail(str) \
        ThrowExc(Inconsistency,(str)+string(" while COW-ing container chain"));
    if( !ret )
      ThrowChainFail("missing link ["+link0.id.toString()+"]");
    if( info.tid != TpDMIObjRef )
      ThrowChainFail("link ["+link0.id.toString()+"] has unexpected type "+info.tid.toString());
    // get writable container from ref 
    ObjRef &ref = *static_cast<ObjRef*>(const_cast<void*>(info.ptr));
    DMI::Container *nc1 = dynamic_cast<DMI::Container *>(ref.dewr_p());
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
DMI::TypeId DMI::Container::Hook::type () const
{
  const void *targ = resolveTarget(DMI::DEREFERENCE);
  if( !targ )
    return 0;
  // not container? Return object type
  else if( !target_nestable )
    return target.obj_tid;
  //  else look in container for type
  TypeId type = static_cast<const DMI::Container *>(targ)->type();
  // if container is of a fixed content type, return that, else 
  // return container's own object type
  return type ? type : target.obj_tid;
}

//##ModelId=3CAB0A3500AC
int DMI::Container::Hook::size (TypeId tid) const
{
  const void *targ = resolveTarget(DMI::DEREFERENCE,tid);
  if( !targ )
    return 0;
  else if( target.obj_tid == tid ) // target matches type? return 1
    return 1;
  else if( !target_nestable )
    return target.size;
  else // else target is container, look inside for size
    return static_cast<const DMI::Container *>(targ)->size(tid);
}

// This is called to treat the hook target as an ObjRef (exception otherwise)
// If write is true, assures writability to the ref (i.e. container
// writability)
//##ModelId=4017F62500F7
const DMI::ObjRef * DMI::Container::Hook::asRef (bool ignore_missing) const
{
  DbgFailWhen(addressed,"unexpected '&' operator");
  // check for element
  resolveTarget();
  if( !target.ptr )
  {
    if( ignore_missing )
      return 0;
    else
      ThrowUninitialized;
  }
  if( target.tid != TpDMIObjRef )
    ThrowConvError(target.tid,TpDMIObjRef);
  return static_cast<const ObjRef*>(target.ptr);
}

// This is called to treat the hook target as an ObjRef (exception otherwise).
// If write is true, assures writability of ref itself
//##ModelId=3C8770A70215
DMI::ObjRef DMI::Container::Hook::ref (bool ignore_missing) const
{
  DbgFailWhen(addressed,"unexpected '&' operator");
  // resolve to ref first, to check types
  const ObjRef * pref = asRef(ignore_missing);
  return pref ? *pref : ObjRef(); 
}

// This is called to access by pointer, for all types
// Defers to get_address(pointer=true)
//##ModelId=4017F62702A0
const void * DMI::Container::Hook::get_pointer (int &sz,
    TypeId tid,bool must_write,bool implicit,
    bool must_exist,Thread::Mutex::Lock *keeplock) const
{
  DbgFailWhen(!addressed && implicit,"missing '&' operator");
  // Defers to get_address(pointer=true)
  ContentInfo info;
  const void *ret = get_address(info,tid,must_write,true,must_exist,keeplock);
  sz = info.size;
  return ret;
}

//##ModelId=3C8739B5017B
const DMI::Container::Hook & DMI::Container::Hook::init (TypeId tid) const
{
  DbgFailWhen(addressed,"unexpected '&' operator");
  ContentInfo info;
  prepare_put(info,tid);
  return *this;
}

//##ModelId=4017F624023A
const DMI::Container::Hook & DMI::Container::Hook::attachObjRef (ObjRef &out) const
{
  DbgFailWhen(addressed,"unexpected '&' operator");
  out.copy(*asRef(false));
  return *this;
}

//##ModelId=4017F625031C
void * DMI::Container::Hook::removeTarget () const
{
  resolveToWritableContainer();
  nc->remove(*pid);
  target.ptr = 0;
  return 0; 
}

//##ModelId=3C876DCE0266
DMI::ObjRef DMI::Container::Hook::remove () const
{
  DbgFailWhen(addressed,"unexpected '&' operator");
  resolveToWritableContainer();
  ObjRef ret;
  if( isRef() )
    ret.xfer(const_cast<ObjRef*>(asRef(false))->unlock());
  nc->remove(*pid);
  target.ptr = 0;
  return ret;
}

//##ModelId=3C876E140018
const DMI::Container::Hook & DMI::Container::Hook::detach (ObjRef* ref) const
{
  DbgFailWhen(addressed,"unexpected '&' operator");
  resolveToWritableContainer();
  ObjRef *ref0 = const_cast<ObjRef*>(asRef(false));
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
// If no such element exists: if must_exist=true, throws 
// an Uninitialized exception, else returns false
// Always throws ConvError on type mismatch.
//##ModelId=4017F626017A
bool DMI::Container::Hook::get_scalar( void *data,TypeId tid,bool must_exist ) const
{
  DbgFailWhen(addressed,"unexpected '&' operator");
  int flags = DMI::DEREFERENCE;
  // We do two attempts to access the hook. If the current target is of
  // the wrong type but happens to be a subcontainer, then we move to the
  // subcontainer and attempt a scalar-mode access (i.e. with a null HIID).
  // Any error during the first attempt is re-thrown as is;
  // during the second attempt it is rethrown as a conversion error.
  for( int attempt=0; attempt<2; attempt++ )
  {
    // resolve hook target
    const void *targ;
    try { targ = resolveTarget(flags,tid); }
    catch ( std::exception &exc ) {
      if( attempt ) break; 
      else          throw;
    } 
    if( !targ )
    {
      if( must_exist ) 
        ThrowUninitialized;
      return false;
    }
    // if target is not a container, attempt the conversion
    // this should work for all numerics and single-element arrays
    if( !target_nestable )
    {
      if( !TypeInfo::convert(targ,target.tid,data,tid) ){
        ThrowConvError(target.tid,tid);
      }
      return true;
    }
    // else try to treat it as a container
    if( !attempt )
    {
      if( !nextContainer(HIID()) ){ // not a container? throw conversion error
        ThrowConvError(target.obj_tid,tid);
      }
    }
  }
  // if we got to here, we have a conversion error
  ThrowConvError(target.obj_tid,tid);
}

// This is called to access by reference, for all types
// If pointer is true, then a pointer is being taken
//##ModelId=4017F6260346
const void * DMI::Container::Hook::get_address (ContentInfo &info,
    TypeId tid,bool must_write,bool pointer,
    bool must_exist,Thread::Mutex::Lock *keeplock) const
{
  // we ask the container for an ObjRef or just an object
  int flags = (tid==TpDMIObjRef ? 0 : DMI::DEREFERENCE) |
          (must_write    ? DMI::WRITE : 0);
  // We do two attempts a-la get_scalar() above
  for( int attempt=0; attempt<2; attempt++ )
  {
    const void *targ;
    try { targ = resolveTarget(flags,tid); }
    catch ( std::exception &exc ) {
      if( attempt ) break; 
      else          throw;
    } 
    // fail if no such element, unless a default is provided
    if( !targ )
    {
      if( must_exist ) 
        ThrowUninitialized;
      info.size = 0;
      return 0;
    }
    // success if types match
    bool match = tid == TpDMIObjRef || tid == target.obj_tid;
    if( match )
    {
      if( target.size > 1 && !pointer )
        ThrowExc(ConvError,ConvErrorMessage("array of "+target.obj_tid.toString(),"a scalar"));
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
      if( !nextContainer(HIID()) ){ // not a container? throw conversion error
        ThrowConvError1(target.obj_tid,tid,(pointer?"*":""));
      }
    }
  }
  // if we got to here, we have a conversion error
  ThrowConvError1(target.obj_tid,tid,(pointer?"*":""));
}

const DMI::BObj * DMI::Container::Hook::get_address_bo (ContentInfo &info,
    bool (*can_convert)(const DMI::BObj *),
    bool must_write,bool pointer,bool must_exist,Thread::Mutex::Lock *keeplock) const
{
  // We do two attempts a-la get_scalar() above
  for( int attempt=0; attempt<2; attempt++ )
  {
    const void *targ;
    try { targ = resolveTarget(must_write?DMI::WRITE:0); }
    catch ( std::exception &exc ) {
      if( attempt ) break; 
      else          throw;
    }
    // fail if no such element, unless a default is provided
    if( !targ )
    {
      if( must_exist ) 
        ThrowUninitialized;
      info.size = 0;
      return 0;
    }
    // for all BO-derived types, an Objref is expected
    if( target.tid != TpDMIObjRef )
    {
      if( info.tid )
        ThrowExc(ConvError,ConvErrorMessage(target.obj_tid.toString(),info.tid.toString()))
      else
        ThrowExc(ConvError,ConvErrorMessage(target.obj_tid.toString(),"an object"));
    }
    // check again, if target is an undefined ref, return 0
    if( !static_cast<const ObjRef *>(targ)->valid() )
    {
      if( must_exist ) 
        ThrowUninitialized;
      info.size = 0;
      return 0;
    }
    const DMI::BObj *ptr = static_cast<const ObjRef *>(targ)->deref_p();
    if( (*can_convert)(ptr) )
    {
      if( target.size > 1 && !pointer )
        ThrowExc(ConvError,"can't access array of "+target.obj_tid.toString()+"s as a scalar");
      info = target;
      // set lock if asked to
      if( keeplock )
      {
        if( chain.empty() )
          *keeplock = link0.lock;
        else
          *keeplock = chain.back().lock;
      }
      return ptr;
    }
    // can't convert to this type: try to treat as container, and go into it
    if( !attempt )
    {
      if( !nextContainer(HIID()) ) // not a container? throw conversion error
        break;
    }
  }
  // fail here
  if( info.tid )
    ThrowExc(ConvError,ConvErrorMessage(target.obj_tid.toString(),info.tid.toString()))
  else
    ThrowExc(ConvError,ConvErrorMessage(target.obj_tid.toString(),"an object"));
}


// This prepares the hook for assignment, by resolving to the target element,
// and failing that, trying to insert() a new element.
// The actual type of the target element is returned via info.tid. 
// Normally, this will be ==tid (or a ConvError will be thrown by the
// container), unless:
// (a) tid==TpDMIObjRef: info.tid must contain required object type on entry
//     Return value will be a pointer to the ObjRef. Note that all
//     dynamic objects must be assigned this way.
// (b) tid & container type are both numeric (caller is expected to 
//     do the conversion)
// For other type categories, a strict match should be enforced by the container.
//##ModelId=3DB934C00071
void * DMI::Container::Hook::prepare_put( ContentInfo &info,TypeId tid ) const
{
  // verify correct assignments
  DbgFailWhen(TypeInfo::isDynamic(tid),"dynamic types must be assigned via ObjRef");
  DbgFailWhen(tid==TpDMIObjRef && !TypeInfo::isDynamic(info.tid),"assigning via ObjRef to non-dynamic type");
  DbgFailWhen(addressed,"unexpected '&' operator");
  void *targ = 0;
  TypeId real_tid = tid == TpDMIObjRef ? info.tid : tid; 
  int flags = (tid==TpDMIObjRef ? 0 : DMI::DEREFERENCE)
              |DMI::WRITE|DMI::ASSIGN;
  // as usual, two attempts (see comments in functions above)
  for( int attempt=0; attempt<2; attempt++ )
  {
    // resolve to hook target, make it writable
    try { targ = const_cast<void*>(resolveTarget(flags,tid)); }
    catch ( std::exception &exc ) {
      if( attempt ) break; 
      else          throw;
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
    if( tid == TpDMIObjRef && target.tid == TpDMIObjRef )
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
const void * DMI::Container::Hook::put_scalar( const void *data,TypeId tid,size_t sz ) const
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
void DMI::Container::Hook::assign_object( DMI::BObj *obj,TypeId tid,int flags ) const
{
  ContentInfo info;
  info.tid = tid;
  void *targ = prepare_put(info,TpDMIObjRef);
  static_cast<ObjRef*>(targ)->unlock().attach(obj,flags);
  target.ptr = 0;
}

// Helper function assigns an objref     
//##ModelId=3DB934C801DF
DMI::ObjRef & DMI::Container::Hook::assign_objref ( ObjRef &ref,int flags ) const
{
  ContentInfo info;
  info.tid = ref->objectType();
  void *targ = prepare_put(info,TpDMIObjRef);
  target.ptr = 0;
  if( flags&DMI::XFER )
    return static_cast<ObjRef*>(targ)->unlock().xfer(ref,flags);
  else
    return static_cast<ObjRef*>(targ)->unlock().copy(ref,flags);
}

// This prepares the hook for assigning a Lorray.
// Will return 0 if hook points to an uninitialized element.
// Otherwise, attemps to access the hook target. If it's an array of
// matching type/rank, returns pointer to array object and sets 
// haveArray=true (*does not check for shape match!*). If rank is 1 and 
// hook points to a block of contiguous scalars of matching size, returns 
// pointer to first element and sets haveArray=false. If it's a subcontainer, 
// repeats previous steps for the subcontainer. Otherwise throws a ConvError.
//##ModelId=3E7081A50350
void * DMI::Container::Hook::prepare_assign_array (bool &haveArray,TypeId tid,const LoShape &shape) const
{
  DbgFailWhen(addressed,"unexpected '&' operator");
  TypeId tidarr = TpArray(tid,shape.size());
  int flags = DMI::DEREFERENCE|DMI::WRITE|DMI::ASSIGN;
  // as usual, two attempts (see comments in functions above)
  for( int attempt=0; attempt<2; attempt++ )
  {
    // resolve to writable object
    void *targ;
    try { targ = const_cast<void*>( resolveTarget(flags,tidarr) ); }
    catch ( std::exception &exc ) {
      if( attempt ) break; 
      else          throw;
    } 
    if( !targ  )   // non-existing object
      return 0; 
    // got an array? check shapes, etc.
    if( TypeInfo::isArray(target.tid) )
    {
      // array matches
      if( target.tid == tidarr )
      {
        haveArray = true;
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
      haveArray = false;
      return targ;
    }
    // else if we have an ObjRef, and replacing is enabled, then just remove
    // the damn thing and return 0
    else if( target.tid == TpDMIObjRef && replacing )
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
// types. The difference is that a DMI::NumArray is initialized rather
// than a DMI::Vec, and that vector<T> may be assigned to an Array(T,1), 
// if that's what the hook is pointing at
template<class T,class Iter> 
void DMI::Container::Hook::assign_arrayable (int size,Iter begin,Iter end,Type2Type<T>) const
{
  bool haveArray;
  // call method above to prepare for assignment
  void * targ = prepare_assign_array(haveArray,typeIdOf(T),LoShape(size));
  T *ptr;
  // non-existing object: try to a initialize a new DMI::NumArray
  if( !targ )
  {
    Container * parr = new DMI::NumArray(typeIdOf(T),LoShape(size));
    ObjRef ref(parr);
    ContentInfo info;
    info.tid = typeIdOf(T);
    int res = parr->get(HIID(),info,true,DMI::WRITE);
    DbgAssert(res>0 && info.ptr && info.tid == typeIdOf(T) );
    ptr = static_cast<T*>( const_cast<void*>(info.ptr) );
    haveArray = false;
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
#define __inst(T,arg) template void DMI::Container::Hook::assign_arrayable \
  (int, std::vector<T>::const_iterator, \
        std::vector<T>::const_iterator, Type2Type<T>) const;
DoForAllArrayTypes(__inst,);
#undef __inst

//##ModelId=4017F6280225
void * DMI::Container::Hook::prepare_assign_vector (TypeId tid,int size) const
{
  DbgFailWhen(addressed,"unexpected '&' operator");
  int flags = DMI::DEREFERENCE|DMI::WRITE|DMI::ASSIGN;
  // as usual, two attempts (see comments in functions above)
  for( int attempt=0; attempt<2; attempt++ )
  {
    // resolve to writable object
    void *targ;
    try { targ = const_cast<void*>( resolveTarget(flags,tid) ); }
    catch ( std::exception &exc ) {
      if( attempt ) break; 
      else          throw;
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
    else if( target.tid == TpDMIObjRef && replacing )
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
void * DMI::Container::Hook::assign_vector (TypeId tid,int size) const
{
  // call method above to prepare for assignment
  void * targ = prepare_assign_vector(tid,size);
  if( targ )
    return targ;
  // else non-existing object: try to a initialize a new DMI::Vec
  Container * pvec = new DMI::Vec(tid,size);
  ObjRef ref(pvec);
  assign_objref(ref,0);
  ContentInfo info; 
  info.tid = tid;
  int res = pvec->get(HIID(),info,true,DMI::WRITE);
  DbgAssert(res>0 && info.ptr && info.tid == tid );
  return const_cast<void*>(info.ptr);
}

//##ModelId=3DB934BC01D9
string DMI::Container::Hook::sdebug (int detail,const string &prefix,const char *name) const
{
  if( !name )
    name = "";
  string out = name;
  if( addressed )
    out += "&";
  if( nc_writable || !(ncref0 || ncptr0) ) // case (a) or (d), empty chain (see comments in Container.h)
  {
    out += "<" + nc->sdebug(detail,prefix) +">";
    out += idToString(*pid);
  }
  else
  {
    if( ncref0 ) // case (b)
      out += "<" + (*ncref0)->sdebug(detail,prefix) + ">";
    else if( ncptr0 ) // case (c)
      out += "<" + ncptr0->sdebug(detail,prefix) + ">";
    // now add chain
    out += idToString(link0.id);
    for( LinkChain::const_iterator iter = chain.begin(); iter != chain.end(); iter++ )
      out += idToString(iter->id);
  }
  return out;
}

