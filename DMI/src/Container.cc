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
//## Source file: F:\lofar8\oms\LOFAR\cep\cpa\pscf\src\NestableContainer.cc

//## begin module%3C10CC830069.additionalIncludes preserve=no
//## end module%3C10CC830069.additionalIncludes

//## begin module%3C10CC830069.includes preserve=yes
//## end module%3C10CC830069.includes

// NestableContainer
#include "NestableContainer.h"
//## begin module%3C10CC830069.declarations preserve=no
//## end module%3C10CC830069.declarations

//## begin module%3C10CC830069.additionalDeclarations preserve=yes
DefineRegistry(NestableContainer,False);
//## end module%3C10CC830069.additionalDeclarations


// Class NestableContainer::ConstHook 

// Additional Declarations
  //## begin NestableContainer::ConstHook%3C614FDE0039.declarations preserve=yes
  //## end NestableContainer::ConstHook%3C614FDE0039.declarations

// Class NestableContainer::Hook 


//## Other Operations (implementation)
bool NestableContainer::Hook::isWritable () const
{
  //## begin NestableContainer::Hook::isWritable%3C87665E0178.body preserve=yes
  TypeId tid; bool write;
  const void *target = collapseIndex(tid,write,0,False);
  // doesn't exist? It's writable if our container is writable
  if( !target )
    return nc->isWritable();
  // is it a reference? Deref it then
  if( tid == TpObjRef )
  {
    if( !static_cast<const ObjRef*>(target)->isWritable() ) // non-writable ref?
      return False;
    target = &static_cast<const ObjRef*>(target)->deref();
    tid = static_cast<const BlockableObject*>(target)->objectType();
  }
  // is it a sub-container? Return its writable property
  if( NestableContainer::isNestable(tid) )
    return static_cast<const NestableContainer*>(target)->isWritable();
  // otherwise, it's writable according to what collapseIndex() returned
  return write;
  //## end NestableContainer::Hook::isWritable%3C87665E0178.body
}

const NestableContainer::Hook & NestableContainer::Hook::init (TypeId tid) const
{
  //## begin NestableContainer::Hook::init%3C8739B5017B.body preserve=yes
  FailWhen(addressed,"unexpected '&' operator");
  TypeId target_tid;
  resolveTarget(target_tid,tid);
  return *this;
  //## end NestableContainer::Hook::init%3C8739B5017B.body
}

const NestableContainer::Hook & NestableContainer::Hook::privatize (int flags) const
{
  //## begin NestableContainer::Hook::privatize%3C8739B5017C.body preserve=yes
  FailWhen(addressed,"unexpected '&' operator");
  FailWhen(!nc->isWritable(),"r/w access violation");
  TypeId target_tid; bool dum;
  void *target = const_cast<void*>(collapseIndex(target_tid,dum,TpObjRef,False));
  FailWhen(!target,"uninitialized element");
  static_cast<ObjRef*>(target)->privatize(flags);
  return *this;
  //## end NestableContainer::Hook::privatize%3C8739B5017C.body
}

bool NestableContainer::Hook::remove (ObjRef* ref) const
{
  //## begin NestableContainer::Hook::remove%3C876DCE0266.body preserve=yes
  FailWhen(!nc->isWritable(),"r/w access violation");
  if( ref )
  {
    // cast away const here: even though ref may be read-only, as long as the 
    // container is writable, we can detach it
    ObjRef *ref0 = const_cast<ObjRef*>( asRef(False) );
    ref->xfer(ref0->unlock());
  }
  return index >= 0 ? nc->removen(index) : nc->remove(id);
  //## end NestableContainer::Hook::remove%3C876DCE0266.body
}

const NestableContainer::Hook & NestableContainer::Hook::detach (ObjRef* ref) const
{
  //## begin NestableContainer::Hook::detach%3C876E140018.body preserve=yes
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
  //## begin NestableContainer::Hook%3C8739B50135.declarations preserve=yes
  //## end NestableContainer::Hook%3C8739B50135.declarations

// Class NestableContainer 


//## Other Operations (implementation)
bool NestableContainer::select (const HIIDSet &)
{
  //## begin NestableContainer::select%3BE982760231.body preserve=yes
  return False;
  //## end NestableContainer::select%3BE982760231.body
}

void NestableContainer::clearSelection ()
{
  //## begin NestableContainer::clearSelection%3BFBDC0D025A.body preserve=yes
  //## end NestableContainer::clearSelection%3BFBDC0D025A.body
}

int NestableContainer::selectionToBlock (BlockSet& )
{
  //## begin NestableContainer::selectionToBlock%3BFBDC1D028F.body preserve=yes
  return 0;
  //## end NestableContainer::selectionToBlock%3BFBDC1D028F.body
}

// Additional Declarations
  //## begin NestableContainer%3BE97CE100AF.declarations preserve=yes

// NB: think about being able to accumulate a HIID for, e.g., accessing
// arrays and tables. E.g. arr[n][m] should be treated as a slice, so,
// applying the [n] and [m] ops sequentially should retain the same target
// but somehow update something (residual ID?) so that later, at point of access,
// it can be resolved.  


const NestableContainer * NestableContainer::ConstHook::asNestable (const void *targ=0,TypeId tid=0) const
{
  if( !targ )
  {
    bool dum;
    targ = collapseIndex(tid,dum,0,False);
    if( !targ )
      return 0;
  }
  if( tid == TpObjRef )
  {
    if( !static_cast<const ObjRef*>(targ)->valid() )
      return 0;
    targ = &static_cast<const ObjRef*>(targ)->deref();
    tid = static_cast<const BlockableObject*>(targ)->objectType();
  }
  return NestableContainer::isNestable(tid) 
    ? static_cast<const NestableContainer*>(targ) 
    : 0;
}

NestableContainer * NestableContainer::ConstHook::asNestableWr (void *targ=0,TypeId tid=0) const
{
  if( !targ )
  {
    bool dum;
    targ = const_cast<void*>( collapseIndex(tid,dum,0,True) );
    if( !targ )
      return 0;
  }
  if( !targ )
    return 0;
  if( tid == TpObjRef )
  {
    if( !static_cast<ObjRef*>(targ)->valid() )
      return 0;
    targ = &static_cast<ObjRef*>(targ)->dewr();
    tid = static_cast<BlockableObject*>(targ)->objectType();
  }
  return NestableContainer::isNestable(tid) 
    ? static_cast<NestableContainer*>(targ) 
    : 0;
}

// This is called to get a value, for built-in scalar types only
void NestableContainer::ConstHook::get_scalar( void *data,TypeId tid,bool ) const
{
  // check for residual index
  FailWhen(addressed,"unexpected '&' operator");
  TypeId target_tid; bool dum; 
  const void *target = collapseIndex(target_tid,dum,0,False);
  FailWhen(!target,"uninitialized element");
  // if referring to a non-dynamic type, attempt the conversion
  if( !isDynamicType(target_tid) && target_tid != TpObjRef )
  {
    FailWhen(!convertScalar(target,target_tid,data,tid),
             "can't convert "+target_tid.toString()+" to "+tid.toString());
    return;
  }
  // if target is a container, then try to access it in scalar mode
  // // ...but not implicitly
  // // FailWhen(implicit,"can't implicitly convert "+target_tid.toString()+" to "+tid.toString());
  const NestableContainer *nc = asNestable(target,target_tid);
  FailWhen(!nc,"can't convert "+target_tid.toString()+" to "+tid.toString());
  // access in scalar mode, checking that type is built-in
  target = nc->get(HIID(),target_tid,dum,TpNumeric,False);
  FailWhen( !convertScalar(target,target_tid,data,tid),
            "can't convert "+target_tid.toString()+" to "+tid.toString());
}

// This is called to access by reference, for all types
const void * NestableContainer::ConstHook::get_address(TypeId tid,bool must_write,bool,bool pointer ) const
{
  TypeId target_tid; bool dum; 
  const void *target = collapseIndex(target_tid,dum,0,False);
  FailWhen(!target,"uninitialized element");
  // If types don't match, then try to treat it as a container, 
  // and return pointer to first element (if this is allowed)
  if( tid != target_tid )
  {
    const NestableContainer *nc = asNestable(target,target_tid);
    FailWhen(!nc,"can't convert "+target_tid.toString()+" to "+tid.toString()+"*");
    FailWhen(pointer && !nc->type(),"this container does not support pointers");
    // check for scalar/vector violation
    if( nc->size()>1 )
    {
      FailWhen(!pointer,"can't access multiple-element container as scalar");
      FailWhen(!nc->isContiguous() && nc->size()>1,
                "can't take pointer to this container's storage");
    }
    // access first element, verifying type & writability
    return nc->get(HIID(),target_tid,dum,tid,must_write);
  }
  return target;
}

// this resolves to the target pointed at by index or id, by doing get(),
// followed by insert(), if get fails
void * NestableContainer::Hook::resolveTarget( TypeId &target_tid,TypeId tid ) const
{
  FailWhen(addressed,"unexpected '&' operator");
  bool dum; 
  void *target = const_cast<void*>( collapseIndex(target_tid,dum,0,True) );
  // non-existing object: try to a insert new one
  if( !target  )
  {
    // The resulting target_tid may be different from the requested tid
    // in the case of scalars (where conversion is allowed)
    target = index>=0 ? nc->insertn(index,tid,target_tid)
                      : nc->insert(id,tid,target_tid);
    if( isDynamicType(target_tid) )
      target_tid = TpObjRef;
  }
  else
  {
    // have we resolved to an existing sub-container, and we're not explicitly
    // trying to assign the same type of sub-container? Try to init it
    NestableContainer *nc1 = asNestableWr(target,target_tid);
    if( nc1 && nc1->objectType() != tid )
    {
      target = nc1->insert(HIID(),tid,target_tid);
      if( isDynamicType(target_tid) )
        target_tid = TpObjRef;
    }
  }
  return target;
}

// This is called to assign a value, for scalar & binary types
const void * NestableContainer::Hook::put_scalar( const void *data,TypeId tid,size_t sz ) const
{
  TypeId target_tid;
  void *target = resolveTarget(target_tid,tid);
  // if types don't match, assume standard conversion
  if( tid != target_tid )
    FailWhen( !convertScalar(data,tid,target,target_tid),
          "can't assign "+tid.toString()+" to "+target_tid.toString() )
  else if( tid == Tpstring ) // else special string case
    *static_cast<string*>(target) = *static_cast<const string*>(data);
  else // else a binary type
    memcpy(const_cast<void*>(target),data,sz);
  return target;
}

// Helper function to assign an object.  
void NestableContainer::Hook::assign_object( BlockableObject *obj,TypeId tid,int flags ) const
{
  TypeId target_tid;
  void *target = resolveTarget(target_tid,tid);
  FailWhen(target_tid!=TpObjRef,"can't attach "+tid.toString()+" to "+target_tid.toString());
  static_cast<ObjRef*>(target)->unlock().attach(obj,flags).lock();
}

// Helper function assigns an objref     
ObjRef & NestableContainer::Hook::assign_objref ( const ObjRef &ref,int flags ) const
{
  FailWhen(addressed,"unexpected '&' operator");
  TypeId target_tid;
  void *target = resolveTarget(target_tid,ref->objectType());
  FailWhen(target_tid!=TpObjRef,"can't assign ObjRef to "+target_tid.toString());
  if( flags&DMI::COPYREF )
    return static_cast<ObjRef*>(target)->unlock().copy(ref,flags).lock();
  else
    return static_cast<ObjRef*>(target)->unlock().xfer(const_cast<ObjRef&>(ref)).lock();
}

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
