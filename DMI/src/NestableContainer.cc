#define NC_SKIP_HOOKS 1
#define NC_INCLUDE_VECTOR_HOOKS 1

#include "NestableContainer.h"
#include "DataArray.h"
#include "DataField.h"
    
#include <list>

DefineRegistry(NestableContainer,False);

//##ModelId=3DB934920303
int NestableContainer::ConstHook::_dum_int;
//##ModelId=3DB9349203A5
NestableContainer::ContentInfo NestableContainer::ConstHook::_dum_info;

//##ModelId=3C87377803A8
const NestableContainer::ConstHook & NestableContainer::ConstHook::operator [] (const HIID &id1) const
{
  FailWhen(addressed,"unexpected '&' operator");
  if( id1.size() )
  {
    int sep = id1.findFirstSlash();
    if( !sep )
      return (*this)[id1.subId(1)];
    else if( sep == (int)(id1.size()-1) )
      return (*this)[id1.subId(0,id1.size()-1)];
    else if( sep > 0 )
      return (*this)[id1.subId(0,sep-1)][id1.subId(sep+1)];
  }
  // apply any previous subscripts
  // (if index==-2, we've been called from constructor, so don't do it)
  if( index >= -1 ) 
    nextIndex();
  // set the new subscript
  id=id1; index=-1;
  return *this;
}

//##ModelId=3C8737C80081
const NestableContainer::ConstHook & NestableContainer::ConstHook::operator [] (int n) const
{
  FailWhen(addressed,"unexpected '&' operator");
  nextIndex();
  id.clear(); index=n;
  return *this;
}

//##ModelId=3C8737E002A3
TypeId NestableContainer::ConstHook::type () const
{
  ContentInfo info;
  const void *targ = collapseIndex(info,0,0);
  if( !targ )
    return 0;
  const NestableContainer *nc1 = asNestable(targ,info.tid);
  return nc1 ? nc1->type() : info.tid;
}

//##ModelId=3C8737F702D8
TypeId NestableContainer::ConstHook::actualType () const
{
  ContentInfo info;
  const void *targ = collapseIndex(info,0,0);
  return targ ? info.tid : NullType;
}


//##ModelId=3C87380503BE
int NestableContainer::ConstHook::size (TypeId tid) const
{
  ContentInfo info;
  const void *targ = collapseIndex(info,0,0);
  if( !targ )
    return 0;
  const NestableContainer *nc1 = asNestable(targ,info.tid);
  if( nc1 )
    return nc1->size(tid);
  return info.size;
}

// This is called to treat the hook target as an ObjRef (exception otherwise)
//##ModelId=3DB9349E0198
const ObjRef * NestableContainer::ConstHook::asRef( bool write ) const
{
  FailWhen(addressed,"unexpected '&' operator");
  ContentInfo info;
  const void *target = collapseIndex(info,TpObjRef,write?DMI::WRITE:0);
  FailWhen(!target,"element does not exist");
  return static_cast<const ObjRef*>(target);
}

// This is called to access by pointer, for all types
// Defers to get_address(pointer=True)
//##ModelId=3DB934AC03C2
const void * NestableContainer::ConstHook::get_pointer (int &sz,
    TypeId tid,bool must_write,bool implicit,
    const void *deflt,Thread::Mutex::Lock *keeplock) const
{
  FailWhen(!addressed && implicit,"missing '&' operator");
  // Defers to get_address(pointer=True)
  ContentInfo info;
  const void *ret = get_address(info,tid,must_write,True,deflt,keeplock);
  sz = info.size;
  return ret;
}

// helper function applies current subscript to hook in preparation
// for setting a new one. Insures that current target is a container.
//##ModelId=3DB934A50226
void NestableContainer::ConstHook::nextIndex () const
{
  // subscript into container for new target
  const NestableContainer *newnc = asNestable();
  FailWhen(!newnc,"indexing into non-existing or non-container element");
  nc = const_cast<NestableContainer*>(newnc);
#ifdef USE_THREADS
  lock.relock(nc->mutex());
#endif
}

// helper function repoints hook at new container and sets null subscript
//##ModelId=3DB934A60032
NestableContainer * NestableContainer::ConstHook::nextNC (const NestableContainer *nc1) const
{
  if( !nc1 )
    return 0;
  nc = const_cast<NestableContainer *>(nc1);
  index = -1;
  id.clear();
#ifdef USE_THREADS
  lock.relock(nc->mutex());
#endif
  return nc;
}



//##ModelId=3C87665E0178
bool NestableContainer::Hook::isWritable () const
{
  //## begin NestableContainer::Hook::isWritable%3C87665E0178.body preserve=yes
  ContentInfo info;
  const void *target = collapseIndex(info,0,0);
  // doesn't exist? It's writable if our container is writable
  if( !target )
    return nc->isWritable();
  // is it a reference? Deref it then
  if( info.tid == TpObjRef )
  {
    if( !static_cast<const ObjRef*>(target)->isWritable() ) // non-writable ref?
      return False;
    target = &static_cast<const ObjRef*>(target)->deref();
    info.tid = static_cast<const BlockableObject*>(target)->objectType();
  }
  // is it a sub-container? Return its writable property
  if( NestableContainer::isNestable(info.tid) )
    return static_cast<const NestableContainer*>(target)->isWritable();
  // otherwise, it's writable according to what collapseIndex() returned
  return info.writable;
  //## end NestableContainer::Hook::isWritable%3C87665E0178.body
}

//##ModelId=3C8739B5017B
const NestableContainer::Hook & NestableContainer::Hook::init (TypeId tid) const
{
  //## begin NestableContainer::Hook::init%3C8739B5017B.body preserve=yes
  FailWhen(addressed,"unexpected '&' operator");
  ContentInfo info;
  prepare_put(info,tid);
  return *this;
  //## end NestableContainer::Hook::init%3C8739B5017B.body
}

//##ModelId=3C8739B5017C
const NestableContainer::Hook & NestableContainer::Hook::privatize (int flags) const
{
  //## begin NestableContainer::Hook::privatize%3C8739B5017C.body preserve=yes
  FailWhen(addressed,"unexpected '&' operator");
  ContentInfo info;
  if( index<0 )
    nc->get(id,info,0,flags|DMI::PRIVATIZE);
  else
    nc->getn(index,info,0,flags|DMI::PRIVATIZE);
  return *this;
  //## end NestableContainer::Hook::privatize%3C8739B5017C.body
}

//##ModelId=3C876DCE0266
ObjRef NestableContainer::Hook::remove () const
{
  //## begin NestableContainer::Hook::remove%3C876DCE0266.body preserve=yes
//#ifdef USE_THREADS
//  lock.relock(True);
//#endif
  FailWhen(!nc->isWritable(),"r/w access violation");
  ObjRef ret;
  if( isRef() )
  {
    // cast away const here: even though ref may be read-only, as long as the 
    // container is writable, we're allowed to detach it
    ObjRef *ref0 = const_cast<ObjRef*>( asRef(False) );
    ret.xfer(ref0->unlock());
  }
  index >= 0 ? nc->removen(index) : nc->remove(id);
  return ret;
  //## end NestableContainer::Hook::remove%3C876DCE0266.body
}

//##ModelId=3C876E140018
const NestableContainer::Hook & NestableContainer::Hook::detach (ObjRef* ref) const
{
  //## begin NestableContainer::Hook::detach%3C876E140018.body preserve=yes
//#ifdef USE_THREADS
//  lock.relock(True);
//#endif
  FailWhen(!nc->isWritable(),"r/w access violation");
  // cast away const here: even though ref may be read-only, as long as the 
  // container is writable, we can still detach it
  ObjRef *ref0 = const_cast<ObjRef*>( asRef(False) );
  ref0->unlock();
  if( ref )
    ref->xfer(*ref0);
  else
    ref0->detach();
  return *this;
  //## end NestableContainer::Hook::detach%3C876E140018.body
}

// Additional Declarations
//##ModelId=3CB2B438020F
  //## begin NestableContainer::Hook%3C8739B50135.declarations preserve=yes
  //## end NestableContainer::Hook%3C8739B50135.declarations

// Class NestableContainer 


//## Other Operations (implementation)
NestableContainer::Hook NestableContainer::setBranch (const HIID &id, int flags)
{
  //## begin NestableContainer::setBranch%3CB2B438020F.body preserve=yes
  nc_writelock;
  FailWhen(!isWritable(),"write access violation");
  // auto-privatize everything for write -- let Hook do it
  if( flags&DMI::PRIVATIZE && flags&DMI::WRITE )
  {
    dprintf(2)("privatizing branch %s\n",id.toString().c_str());
    // auto-privatizing hook
    Hook hook(*this,id,DMI::WRITE|DMI::PRIVATIZE);
    if( flags&DMI::DEEP )
      hook.privatize(DMI::WRITE|DMI::DEEP);
    return hook;
  }
  // else it's a privatize only as needed
  FailWhen( !flags&DMI::WRITE,"invalid flags");
  dprintf(2)("ensuring writability of branch %s\n",id.toString().c_str());
  // During first pass, we go down the branch to figure out the writability
  // of each container. To privatize the final element (if this is required), 
  // we need to privatize everything starting from the _last_ writable container 
  // in the chain.
  list<BranchEntry> branch;
  HIID id0,id1=id;    
  bool writable = isWritable();
  // note that if entire branch is to be privatized read-only, we'll 
  // auto-privatize it for writing during the first pass. This more or less 
  // insures that a clone is made.
  Hook hook(*this,-2); 
  // form list of branch elements
  int index=0,last_writable=-1;
  while( id1.size() )
  {
    // split off next subscript
    BranchEntry be;
    be.id = id1.splitAtSlash();
    if( id0.size() )
      id0 |= AidSlash;
    id0 |= be.id;
    if( !be.id.size() ) // ignore if null
      continue;
    // cast away const but that's OK since we track writability
    be.nc = const_cast<NestableContainer*>(hook.asNestable());  // container pointed to by current hook
    // apply subscript to current hook 
    if( be.nc )
    {
#ifdef USE_THREADS
      be.lock.relock(be.nc->mutex());
#endif
      if( be.nc->isWritable() )
        last_writable = index; // keeps track of last writable container in chain
    }
    hook[be.id];
    writable = be.writable = hook.isWritable();
    branch.push_back(be);
    index++;
  }
  // is the last hook writable? Just return it
  if( hook.isWritable() )
  {
    dprintf(2)("last branch element is writable already\n");
    return hook;
  }
  // else restart at the last writable container
  // Start with initial hook again, and apply subscripts until we
  // reach the writable container
  FailWhen( last_writable<0,"unable to privatize: complete branch is read-only");
  dprintf(2)("privatizing starting from branch element %d\n",last_writable);
  Hook hook1(*this,-2); 
  list<BranchEntry>::const_iterator iter = branch.begin();
  for( int i=0; i<last_writable; i++,iter++ )
    hook1[iter->id];
  Assert(iter != branch.end() && iter->nc->isWritable() );
  hook1.autoprivatize = DMI::WRITE|DMI::PRIVATIZE;  // enable auto-privatize
  // apply remaining subscripts
  for( ; iter != branch.end(); iter++ )
    hook1[iter->id];
  // return the hook
  return hook1;
  //## end NestableContainer::setBranch%3CB2B438020F.body
}

//##ModelId=3BE982760231
bool NestableContainer::select (const HIIDSet &)
{
  //## begin NestableContainer::select%3BE982760231.body preserve=yes
  return False;
  //## end NestableContainer::select%3BE982760231.body
}

//##ModelId=3BFBDC0D025A
void NestableContainer::clearSelection ()
{
  //## begin NestableContainer::clearSelection%3BFBDC0D025A.body preserve=yes
  //## end NestableContainer::clearSelection%3BFBDC0D025A.body
}

//##ModelId=3BFBDC1D028F
int NestableContainer::selectionToBlock (BlockSet& )
{
  //## begin NestableContainer::selectionToBlock%3BFBDC1D028F.body preserve=yes
  return 0;
  //## end NestableContainer::selectionToBlock%3BFBDC1D028F.body
}

// Additional Declarations
//##ModelId=3DB934A002CB
  //## begin NestableContainer%3BE97CE100AF.declarations preserve=yes
// Attempts to treat the hook target as an NC, by collapsing subscripts,
// dereferencing ObjRefs, etc.
const NestableContainer * NestableContainer::ConstHook::asNestable (const void *targ,TypeId tid) const
{
  if( index<-1 ) // uninitialized -- just return nc
    return nc;
  ContentInfo info;
  info.tid = tid;
  if( !targ )
  {
    targ = collapseIndex(info,TpObject,0);
    if( !targ )
      return 0;
  }
  if( info.tid == TpObjRef )
  {
    if( !static_cast<const ObjRef*>(targ)->valid() )
      return 0;
    targ = &static_cast<const ObjRef*>(targ)->deref();
    info.tid = static_cast<const BlockableObject*>(targ)->objectType();
  }
  return NestableContainer::isNestable(info.tid) 
    ? static_cast<const NestableContainer*>(targ) 
    : 0;
}

// Same thing, but insures writability
//##ModelId=3DB934A200F8
NestableContainer * NestableContainer::ConstHook::asNestableWr (void *targ,TypeId tid) const
{
  if( index<-1 ) // uninitialized -- just return nc
    return nc;
  ContentInfo info;
  info.tid = tid;
  if( !targ )
  {
    targ = const_cast<void*>( collapseIndex(info,TpObject,DMI::WRITE) );
    if( !targ )
      return 0;
  }
  if( tid == TpObjRef )
  {
    if( !static_cast<ObjRef*>(targ)->valid() )
      return 0;
    targ = &static_cast<ObjRef*>(targ)->dewr();
    info.tid = static_cast<BlockableObject*>(targ)->objectType();
  }
  return NestableContainer::isNestable(info.tid) 
    ? static_cast<NestableContainer*>(targ) 
    : 0;
}

// This is called to get a value, for built-in scalar types only
//##ModelId=3DB934A603C2
bool NestableContainer::ConstHook::get_scalar( void *data,TypeId tid,bool nothrow ) const
{
  // check for residual index
  FailWhen(addressed,"unexpected '&' operator");
  ContentInfo info;
  const void *target;
  if( index>=0 || id.size() )
  {
    target = collapseIndex(info,0,0);
    if( !target )
    {
      FailWhen(!nothrow,"uninitialized element");
      return False;
    }
  }
  else
  {
    target = nc;
    info.tid = nc->objectType();
  }
  // if referring to a non-dynamic type, attempt the conversion
  if( !TypeInfo::isDynamic(info.tid) && info.tid != TpObjRef )
  {
    FailWhen(!convertScalar(target,info.tid,data,tid),
             "can't convert "+info.tid.toString()+" to "+tid.toString());
    return True;
  }
  // if target is a container, then try to access it in scalar mode
  FailWhen( !nextNC(asNestable(target,info.tid)),
            "can't convert "+info.tid.toString()+" to "+tid.toString());
  // access in scalar mode, checking that type is numeric
  target = nc->get(HIID(),info,TpNumeric,DMI::NC_SCALAR|autoprivatize);
  FailWhen( !convertScalar(target,info.tid,data,tid),
            "can't convert "+info.tid.toString()+" to "+tid.toString());
  
  return True;
}

// This is called to access by reference, for all types
// If pointer is True, then a pointer type is being taken
//##ModelId=3DB934A90100
const void * NestableContainer::ConstHook::get_address (ContentInfo &info,
    TypeId tid,bool must_write,bool pointer,
    const void *deflt,Thread::Mutex::Lock *keeplock) const
{
  const void *target;
  if( index>=0 || id.size() )
  {
    target = collapseIndex(info,0,0);
    if( !target )
    {
      FailWhen(!deflt,"uninitialized element");
      return deflt;
    }
  }
  else
  {
    target = nc;
    info.tid = nc->objectType();
    info.size = 1;
  }
  // If types don't match, then 
  // (b) else try to treat target as a container in scalar mode
  if( tid != info.tid )
  {
    // (a) if target is an ObjRef, try to resolve to ref target
    if( info.tid == TpObjRef )
    {
      FailWhen( !static_cast<const ObjRef*>(target)->valid(),
                "can't convert "+info.tid.toString()+" to "+tid.toString()+"*");
      info.writable = static_cast<const ObjRef*>(target)->isWritable();
      target = static_cast<const ObjRef*>(target)->deref_p();
      info.tid = static_cast<const BlockableObject *>(target)->objectType();
      info.size = 1;
    }
    // still no match? Try to treat target as a container in scalar mode
    if( tid != info.tid )
    {
      FailWhen( !nextNC(asNestable(target,info.tid)),
                  "can't convert "+info.tid.toString()+" to "+tid.toString()+"*");
      int flags = (must_write?DMI::WRITE:0)|autoprivatize|
                  DMI::NC_SCALAR|(pointer?DMI::NC_POINTER:0);
      if( keeplock )
        *keeplock = lock;
      return nc->get(HIID(),info,tid,flags);
    }
  }
  FailWhen(!info.writable && must_write,"write access violation");
  if( keeplock )
    *keeplock = lock;
  return target;
}

// This prepares the hook for assignment, by resolving to the target element,
// and failing that, trying to insert() a new element.
// The actual type of the target element is returned via info.tid. 
// Normally, this will be ==tid (or an exception will be thrown by the
// container), unless:
// (a) tid==TpObjRef: info.tid must contain actual object type on entry
// (b) tid & container type are both numeric (Hook will do conversion)
// For other type categories, a strict match should be enforced by the container.
//##ModelId=3DB934C00071
void * NestableContainer::Hook::prepare_put( ContentInfo &info,TypeId tid ) const
{
  FailWhen(addressed,"unexpected '&' operator");
  void *target;
  TypeId real_tid = info.tid; // save value since it may be modified by collapseIndex
  // are we replacing the element? Start by removing existing target
  if( replacing )
  {
    index >= 0 ? nc->removen(index) 
               : nc->remove(id);
    target = 0;
  }
  else // assigning to element: try to resolve to it first
  {
    // no DMI::WRITE is passed to collapseIndex(), since we check for writability
    // ourselves, below
    target = const_cast<void*>( collapseIndex(info,0,0) );
  }
  // non-existing object (or we're replacing it): try to a insert new one
  if( !target  )
  {
    return index>=0 ? nc->insertn(index,tid,info.tid=real_tid)
                    : nc->insert(id,tid,info.tid=real_tid);
  }
  // Resolved to existing object. Check if this is a writable subcontainer
  NestableContainer *nc1;
  bool writable = True;
  try         { nc1 = asNestableWr(target,info.tid); }
  catch(...)  { nc1 = 0; }
  
  if( !nc1 )
  {
    // It's a non-container, or it's not a writable one. 
    // We can then assign to the element if the types match, and if the current 
    // container itself is writable.
    FailWhen( !nc->isWritable(),"r/w access violation" );
    FailWhen( tid != info.tid && 
              !(TypeInfo::isNumeric(tid) && TypeInfo::isNumeric(info.tid)),
              "can't assign "+tid.toString()+" to "+info.tid.toString() );
    return target;
  }
  // Else it's a writable sub-container -- assign to it
  nc1 = nextNC(nc1);
  info.tid = real_tid; 
  if( nc1->size() )   // not empty? Try to assign to it in scalar mode
  {
    target = const_cast<void*>(
        nc1->get(HIID(),info,tid,DMI::WRITE|DMI::NC_SCALAR));
  }
  else // empty? Try to insert a new element in scalar mode
  {
    target = nc1->insert(HIID(),tid,info.tid);
  }
  FailWhen( !target,"can't assign to this sub-container" );
  return target;
}

// Assigns hook to hook
// void NestableContainer::Hook::operator = (const NestableContainer::ConstHook &hook )
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

// This is called to assign a value, for scalar & binary types
//##ModelId=3DB934C102D5
const void * NestableContainer::Hook::put_scalar( const void *data,TypeId tid,size_t sz ) const
{
  ContentInfo info;
  void *target = prepare_put(info,tid);
  // if types don't match, assume standard conversion
  if( tid != info.tid )
  {
    FailWhen( !convertScalar(data,tid,target,info.tid),
          "can't assign "+tid.toString()+" to "+info.tid.toString() );
  }
  else // else a binary type
    memcpy(const_cast<void*>(target),data,sz);
  return target;
}

// Helper function to assign an object.  
//##ModelId=3DB934C30364
void NestableContainer::Hook::assign_object( BlockableObject *obj,TypeId tid,int flags ) const
{
  ContentInfo info;
  info.tid = tid;
  void *target = prepare_put(info,TpObjRef);
  static_cast<ObjRef*>(target)->unlock().attach(obj,flags).lock();
}

// Helper function assigns an objref     
//##ModelId=3DB934C801DF
ObjRef & NestableContainer::Hook::assign_objref ( const ObjRef &ref,int flags ) const
{
  FailWhen(addressed,"unexpected '&' operator");
  ContentInfo info;
  info.tid = ref->objectType();
  void *target = prepare_put(info,TpObjRef);
  if( flags&DMI::COPYREF )
    return static_cast<ObjRef*>(target)->unlock().copy(ref,flags).lock();
  else
    return static_cast<ObjRef*>(target)->unlock().xfer(const_cast<ObjRef&>(ref)).lock();
}


// This does most of the work of assigning an Array
// This either assigns to the underlying object, or inits a new DataArray
//##ModelId=3E7081A50350
void * NestableContainer::Hook::prepare_assign_array (bool &haveArray,TypeId tid,const LoShape &shape) const
{
  FailWhen(addressed,"unexpected '&' operator");
  ContentInfo info;
  // are we replacing the element? Start by removing existing target
  if( replacing )
  {
    index >= 0 ? nc->removen(index) 
               : nc->remove(id);
    return 0; // non-existing object
  }
  void * target = const_cast<void*>( collapseIndex(info,0,DMI::WRITE) );
  if( !target  )   // non-existing object
    return 0; 
  // hook resolved to an array -- check shapes, etc.
  if( TypeInfo::isArray(info.tid) )
  {
    FailWhen( info.tid != TpArray(tid,shape.size()),"can't assign array: type or rank mismatch" );
    haveArray = True;
    return target;
  }
  // else we should have resolved to an existing sub-container
  else
  {
    FailWhen( !nextNC(asNestableWr(target,info.tid)),"can't assign array: type mismatch");
    // for 1D arrays, use linear addressing, so all contiguous containers
    // are supported
    if( shape.size() == 1 )
    {
      // check that size matches
      FailWhen( nc->size() != shape[0],"can't assign array: shape mismatch" );
      // get pointer to first element (use pointer mode to ensure contiguity,
      // and pass in T as the check_tid.)
      target = const_cast<void*>(
          nc->get(HIID(),info,tid,DMI::WRITE|DMI::NC_POINTER|autoprivatize));
      FailWhen(!target,"uninitialized element");
      haveArray = False;
      return target;
    }
    // else try to access it as a true array, and assign to it
    else
    {
      target = const_cast<void*>(
          nc->get(HIID(),info,TpArray(tid,shape.size()),DMI::WRITE));
      FailWhen(!target,"uninitialized element");
      haveArray = True;
      return target;
    }
  }
}
  
// This provides a specialization of operator = (vector<T>) for arrayable
// types. The difference is that a DataArray is initialized rather
// than a DataField, and that vector<T> may be assigned to an Array(T,1), 
// if the hook returns that.
template<class T,class Iter> 
void NestableContainer::Hook::assign_arrayable (int size,Iter begin,Iter end,Type2Type<T>) const
{
  FailWhen(addressed,"unexpected '&' operator");
  ContentInfo info;
  void *target=0;
  // are we replacing the element? Start by removing existing target
  if( replacing )
  {
    index >= 0 ? nc->removen(index) 
               : nc->remove(id);
  }
  else
    target = const_cast<void*>( collapseIndex(info,0,DMI::WRITE) );
  T * ptr; // pointer to destination array data 
  // non-existing object: try to a initialize a new DataArray
  if( !target  )
  {
    DataArray *darr = new DataArray(typeIdOf(T),LoShape(size),DMI::WRITE);
    ObjRef ref(darr,DMI::ANONWR);
    ptr = static_cast<T*>( const_cast<void*>(
            darr->get(HIID(),info,typeIdOf(T),DMI::WRITE|DMI::NC_POINTER) 
          ));
    assign_objref(ref,0);
  }
  // else maybe hook has resolved to a 1D array? check shapes, etc.
  else if( TypeInfo::isArray(info.tid) ) 
  {
    FailWhen( info.tid != typeIdOfArray(T,1),
        "can't assign vector to array field: type or rank mismatch" );
    // NB: typeinfo should incorporate mapping between array types and
    // numeric types
    blitz::Array<T,1> *arr = static_cast<blitz::Array<T,1>*>(target);
    FailWhen( arr->shape()[0] != size,"can't assign vector to array field: shape mismatch" );
    typename blitz::Array<T,1>::iterator iarr = arr->begin();
    for( ; begin != end; ++begin,++iarr )
      *iarr = *begin;
    return;
  }
  // else we should have resolved to an existing sub-container
  else
  {
    FailWhen( !nextNC(asNestableWr(target,info.tid)),
              "can't assign vector: type mismatch" );
    target = const_cast<void*>(
        nc->get(HIID(),info,typeIdOf(T),DMI::WRITE|DMI::NC_POINTER|autoprivatize));
    FailWhen(!target,"can't assign vector");
    FailWhen(info.size != size,"can't assign vector: shape mismatch" );
    ptr = static_cast<T*>(target);
  }
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


// This helper method does all the work of preparing a hook for assignment of
// vector. This minimizes template size.
//##ModelId=3DB934CA0142
void * NestableContainer::Hook::prepare_vector (TypeId tid,int size) const
{
  FailWhen(addressed,"unexpected '&' operator");
  ContentInfo info;
  // are we replacing the element? Start by removing existing target
  void *target = 0;
  if( replacing )
  {
    index >= 0 ? nc->removen(index) 
               : nc->remove(id);
  }
  else
    target = const_cast<void*>( collapseIndex(info,0,DMI::WRITE) );
  // non-existing object: try to a initialize a new DataField
  if( !target  )
  {
    DataField *df = new DataField(tid,size,DMI::WRITE);
    ObjRef ref(df,DMI::ANONWR);
    assign_objref(ref,0);
    nextNC(df);
  }
  // else we should have resolved to an existing sub-container
  else
  {
    FailWhen( !nextNC(asNestableWr(target,info.tid)),
              "can't assign vector: type mismatch");
  }
  // get pointer to first element (use pointer mode to ensure contiguity)
  // cast away const since we set DMI::WRITE
  target = const_cast<void*>(
      nc->get(HIID(),info,tid,DMI::WRITE|DMI::NC_POINTER|autoprivatize));
  FailWhen(info.size != size,"can't assign vector: shape mismatch");
  FailWhen(!target,"can't assign vector");
  return target;
}

//##ModelId=3DB9349A0087
string NestableContainer::ConstHook::sdebug ( int detail,const string &prefix,const char *name ) const
{
  if( !name )
    name = "CHook";
  string out;
  out = ssprintf("%s%s[%s]",name,addressed?"&":"",nc->sdebug(detail,prefix).c_str());
  out += index >= 0 
      ? ssprintf("[%d]",index) 
      : "["+id.toString()+"]"; 
  return out;  
}
