//## begin module%1.4%.codegen_version preserve=yes
//   Read the documentation to learn more about C++ code generator
//   versioning.
//## end module%1.4%.codegen_version

//## begin module%3C10CC830069.cm preserve=no
//	  %X% %Q% %Z% %W%
//## end module%3C10CC830069.cm

//## begin module%3C10CC830069.cp preserve=no
//## end module%3C10CC830069.cp

//## Module: NestableContainer%3C10CC830069; Package body
//## Subsystem: DMI%3C10CC810155
//	f:\lofar\dvl\lofar\cep\cpa\pscf\src
//## Source file: F:\lofar8\oms\LOFAR\src-links\DMI\NestableContainer.cc

//## begin module%3C10CC830069.additionalIncludes preserve=no
//## end module%3C10CC830069.additionalIncludes

//## begin module%3C10CC830069.includes preserve=yes
#define NC_SKIP_HOOKS 1
#include <list>
#include "DMI/DataArray.h"
#include "DMI/DataField.h"
//## end module%3C10CC830069.includes

// NestableContainer
#include "DMI/NestableContainer.h"
//## begin module%3C10CC830069.declarations preserve=no
//## end module%3C10CC830069.declarations

//## begin module%3C10CC830069.additionalDeclarations preserve=yes
DefineRegistry(NestableContainer,False);

//##ModelId=3DB934920303
int NestableContainer::ConstHook::_dum_int;
//##ModelId=3DB9349203A5
NestableContainer::ContentInfo NestableContainer::ConstHook::_dum_info;
//##ModelId=3C87380503BE
//## end module%3C10CC830069.additionalDeclarations


// Class NestableContainer::ConstHook 


//## Other Operations (implementation)
int NestableContainer::ConstHook::size (TypeId tid) const
{
  //## begin NestableContainer::ConstHook::size%3C87380503BE.body preserve=yes
  ContentInfo info;
  const void *targ = collapseIndex(info,0,0);
  if( !targ )
    return 0;
  const NestableContainer *nc1 = asNestable(targ,info.tid);
  if( nc1 )
    return nc1->size(tid);
  return info.size;
  //## end NestableContainer::ConstHook::size%3C87380503BE.body
}

// Additional Declarations
//##ModelId=3C87665E0178
  //## begin NestableContainer::ConstHook%3C614FDE0039.declarations preserve=yes
  //## end NestableContainer::ConstHook%3C614FDE0039.declarations

// Class NestableContainer::Hook 


//## Other Operations (implementation)
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
    targ = collapseIndex(info,0,0);
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
    targ = const_cast<void*>( collapseIndex(info,0,DMI::WRITE) );
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
// The actual type of the target element is returned via target_tid. 
// Normally, this will be ==tid (or an exception will be thrown by the
// container), unless:
// (a) tid & container type are both dynamic (then target must be an ObjRef)
// (b) tid & container type are both numeric (Hook will do conversion)
// For other type categories, a strict match should be enforced by the container.
//##ModelId=3DB934C00071
void * NestableContainer::Hook::prepare_put( ContentInfo &info,TypeId tid ) const
{
  FailWhen(addressed,"unexpected '&' operator");
  void *target = const_cast<void*>( collapseIndex(info,0,DMI::WRITE) );
  // non-existing object: try to a insert new one
  if( !target  )
  {
//    #ifdef USE_THREADS
//    lock.relock(True);
//    #endif
    // The resulting target_tid may be different from the requested tid
    // in the case of scalars (where conversion is allowed)
    target = index>=0 ? nc->insertn(index,tid,info.tid)
                      : nc->insert(id,tid,info.tid);
    if( TypeInfo::isDynamic(info.tid) )
      info.tid = TpObjRef;
  }
  else
  {
    // have we resolved to an existing sub-container, and we're not explicitly
    // trying to assign the same type of sub-container? Try to either init the 
    // container with whatever is being assigned, or assign to it as a scalar
    NestableContainer *nc1 = nextNC(asNestableWr(target,info.tid));
    if( nc1 && nc1->objectType() != tid )
    {
      if( nc1->size() )
      {
        target = const_cast<void*>(
            nc1->get(HIID(),info,tid,DMI::WRITE|DMI::NC_SCALAR));
      }
      else
      {
        target = nc1->insert(HIID(),tid,info.tid);
        if( TypeInfo::isDynamic(info.tid) )
          info.tid = TpObjRef;
      }
    }
  }
  return target;
}

// This is called to assign a value, for scalar & binary types
//##ModelId=3DB934C102D5
const void * NestableContainer::Hook::put_scalar( const void *data,TypeId tid,size_t sz ) const
{
  ContentInfo info;
  void *target = prepare_put(info,tid);
  // if types don't match, assume standard conversion
  if( tid != info.tid )
    FailWhen( !convertScalar(data,tid,target,info.tid),
          "can't assign "+tid.toString()+" to "+info.tid.toString() )
  else // else a binary type
    memcpy(const_cast<void*>(target),data,sz);
  return target;
}

// Helper function to assign an object.  
//##ModelId=3DB934C30364
void NestableContainer::Hook::assign_object( BlockableObject *obj,TypeId tid,int flags ) const
{
  ContentInfo info;
  void *target = prepare_put(info,tid);
  FailWhen(info.tid!=TpObjRef,"can't attach "+tid.toString()+" to "+info.tid.toString());
  static_cast<ObjRef*>(target)->unlock().attach(obj,flags).lock();
}

// Helper function assigns an objref     
//##ModelId=3DB934C801DF
ObjRef & NestableContainer::Hook::assign_objref ( const ObjRef &ref,int flags ) const
{
  FailWhen(addressed,"unexpected '&' operator");
  ContentInfo info;
  void *target = prepare_put(info,ref->objectType());
  FailWhen(info.tid!=TpObjRef,"can't assign ObjRef to "+info.tid.toString());
  if( flags&DMI::COPYREF )
    return static_cast<ObjRef*>(target)->unlock().copy(ref,flags).lock();
  else
    return static_cast<ObjRef*>(target)->unlock().xfer(const_cast<ObjRef&>(ref)).lock();
}


// Assignment of an Array either assigns to the underlying object,
// or inits a new DataArray
template<class T> 
const Array<T> & NestableContainer::Hook::operator = (const Array<T> &other) const
{
  FailWhen(addressed,"unexpected '&' operator");
  ContentInfo info;
  void *target = const_cast<void*>( collapseIndex(info,0,DMI::WRITE) );
  // non-existing object: try to a initialize a new DataArray
  if( !target  )
  {
    ObjRef ref(new DataArray(other,DMI::WRITE),DMI::ANONWR);
    assign_objref(ref,0);
  }
  // hook resolved to an array -- check shapes, etc.
  else if( info.tid == typeIdOfArray(T) )
  {
    Array<T> *arr = static_cast<Array<T>*>(target);
    FailWhen( arr->shape() != other.shape(),"can't assign array: shape mismatch" );
    *arr = other;
  }
  // else we should have resolved to an existing sub-container
  else
  {
    FailWhen( !nextNC(asNestableWr(target,info.tid)),
              "can't assign array: type mismatch");
    // for 1D arrays, use linear addressing, so all contiguous containers
    // are supported
    if( other.shape().nelements() == 1 )
    {
      // check that size matches
      FailWhen( nc->size() != other.shape()(0),"can't assign array: shape mismatch" );
      // get pointer to first element (use pointer mode to ensure contiguity,
      // and pass in T as the check_tid.
      target = const_cast<void*>(
          nc->get(HIID(),info,typeIdOf(T),DMI::WRITE|DMI::NC_POINTER|autoprivatize));
      FailWhen(!target,"uninitialized element");
      Array<T> arr(other.shape(),static_cast<T*>(target),SHARE);
      arr = other;
    }
    // else try to access it as a true array, and assign to it
    else
    {
      FailWhen( TpOfArrayElem(&other) == Tpstring,
          "multidimensional arrays of strings not supported" );
      target = const_cast<void*>(
          nc->get(HIID(),info,typeIdOfArray(T),DMI::WRITE));
      FailWhen(!target,"uninitialized element");
      Array<T> *arr = static_cast<Array<T>*>(target);
      FailWhen(arr->shape() != other.shape(),"can't assign array: shape mismatch" );
      *arr = other;
    }
  }
  return other;
}

// This provides a specialization of operator = (vector<T>) for arrayable
// types. The difference is that a DataArray is initialized rather
// than a DataField, and that vector<T> may be assigned to an Array_T, 
// if the hook returns that.
template<class T> 
const vector<T> & NestableContainer::Hook::assign_arrayable (const vector<T> &other) const
{
  FailWhen(addressed,"unexpected '&' operator");
  ContentInfo info;
  void *target = const_cast<void*>( collapseIndex(info,0,DMI::WRITE) );
  // non-existing object: try to a initialize a new DataArray
  if( !target  )
  {
    DataArray *darr = new DataArray(typeIdOf(T),IPosition(1,other.size()),DMI::WRITE);
    ObjRef ref(darr,DMI::ANONWR);
    T * ptr = static_cast<T*>( const_cast<void*>(
        darr->get(HIID(),info,typeIdOf(T),DMI::WRITE|DMI::NC_POINTER) 
        ));
    for( typename vector<T>::const_iterator iter = other.begin(); iter != other.end(); iter++ )
      *ptr++ = *iter;
    assign_objref(ref,0);
  }
  // else maybe hook has resolved to an array -- check shapes, etc.
  else if( info.tid == typeIdOfArray(T) )
  {
    // NB: typeinfo should incorporate mapping between array types and
    // numeric types
    Array<T> *arr = static_cast<Array<T>*>(target);
    int n = other.size();
    FailWhen( arr->shape().nelements() != 1
              || arr->shape()(0) != (int)(other.size()),"can't assign vector: shape mismatch" );
    for( int i=0; i<n; i++ )
      (*arr)(IPosition(1,i)) = other[i];
  }
  // else we should have resolved to an existing sub-container
  else
  {
    FailWhen( !nextNC(asNestableWr(target,info.tid)),
              "can't assign vector: type mismatch" );
    target = const_cast<void*>(
        nc->get(HIID(),info,typeIdOf(T),DMI::WRITE|DMI::NC_POINTER|autoprivatize));
    FailWhen(!target,"can't assign vector");
    FailWhen(info.size != (int)other.size(),"can't assign vector: shape mismatch" );
    T * ptr = static_cast<T*>(target);
    for( typename vector<T>::const_iterator iter = other.begin(); iter != other.end(); iter++ )
      *ptr++ = *iter;
  }
  return other;
}

// This helper method does all the work of preparing a hook for assignment of
// vector. This minimizes template size.
//##ModelId=3DB934CA0142
void * NestableContainer::Hook::prepare_vector (TypeId tid,int size) const
{
  FailWhen(addressed,"unexpected '&' operator");
  ContentInfo info;
  void *target = const_cast<void*>( collapseIndex(info,0,DMI::WRITE) );
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


template<class T> 
inline const vector<T> & NestableContainer::Hook::assign_vector (const vector<T> &other,TypeId tid) const
{ 
  T * ptr = static_cast<T*>( prepare_vector(tid,other.size()) ); 
  for( typename vector<T>::const_iterator iter = other.begin(); iter != other.end(); iter++ ) 
    *ptr++ = *iter; 
  return other; 
}

// Assignment of an STL vector either assigns to the underlying object,
// or inits a new DataField.
// instantiate =(vector<T>) for all non-arrayable types
// We define a macro to provide a template specialization, so that we
// can use the TpType constants
#define __assign_vector(T,arg) template<> const vector<T> & NestableContainer::Hook::operator = (const vector<T> &other) const { return assign_vector(other,Tp##T); }
DoForAllNonArrayTypes(__assign_vector,);
DoForAllBinaryTypes(__assign_vector,);
DoForAllSpecialTypes(__assign_vector,);
#undef __assign_vector

// instantiate =(Array<T>) for all arrayable types
#define __instantiate(T,arg) template const Array<T> & NestableContainer::Hook::operator = (const Array<T> &other) const;
DoForAllArrayTypes(__instantiate,);
#undef __instantiate

// provide specializations of =(vector<T>) for all arrayable types
#define __specialize(T,arg) template<> const vector<T> & NestableContainer::Hook::operator = (const vector<T> &other) const { return assign_arrayable(other); }
DoForAllArrayTypes(__specialize,);
#undef __specialize


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
  //## end NestableContainer%3BE97CE100AF.declarations
//## begin module%3C10CC830069.epilog preserve=yes
//## end module%3C10CC830069.epilog
