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
//## Source file: f:\lofar\dvl\lofar\cep\cpa\pscf\src\NestableContainer.cc

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

// Additional Declarations
  //## begin NestableContainer::Hook%3C62A13101C9.declarations preserve=yes
  //## end NestableContainer::Hook%3C62A13101C9.declarations

// Class NestableContainer 


//## Other Operations (implementation)
bool NestableContainer::getFieldInfo (const HIID &id, TypeId &tid, bool& can_write, bool no_throw) const
{
  //## begin NestableContainer::getFieldInfo%3BE9828D0266.body preserve=yes
  if( no_throw )
  {
    try {
      return get(id,tid,can_write) ? True : False;
    } catch( Debug::Error &x ) {
      return False;
    }
  }
  else
    return get(id,tid,can_write) ? True : False;
  //## end NestableContainer::getFieldInfo%3BE9828D0266.body
}

bool NestableContainer::hasField (const HIID &id) const
{
  //## begin NestableContainer::hasField%3C56AC2902A1.body preserve=yes
  TypeId dum1; bool dum2;
  return getFieldInfo(id,dum1,dum2,True);
  //## end NestableContainer::hasField%3C56AC2902A1.body
}

TypeId NestableContainer::fieldType (const HIID &id) const
{
  //## begin NestableContainer::fieldType%3C5958C203A0.body preserve=yes
  TypeId tid; bool dum2;
  return getFieldInfo(id,tid,dum2,True) ? tid : NullType;
  //## end NestableContainer::fieldType%3C5958C203A0.body
}

// Additional Declarations
  //## begin NestableContainer%3BE97CE100AF.declarations preserve=yes

// NB: think about being able to accumulate a HIID for, e.g., accessing
// arrays and tables. E.g. arr[n][m] should be treated as a slice, so,
// applying the [n] and [m] ops sequentially should retain the same target
// but somehow update something (residual ID?) so that later, at point of access,
// it can be resolved.  


// This is called to get a value, for built-in scalar types only
void NestableContainer::ConstHook::get_scalar( void *data,TypeId tid,bool implicit ) const
{
  // check for residual index
  FailWhen(addressed,"unexpected '&' operator");
  FailWhen(resid.size(),"uninitialized element ["+resid.toString()+"]"); 
  FailWhen(resindex>=0,ssprintf("uninitialized element [%d]",resindex)); 
  // if referring to a non-object type, attempt the conversion
  if( !isDynamicType(target_tid) )
  {
    convertScalar(target,target_tid,data,tid);
    return;
  }
  // if target is a container, then try to access it in scalar mode
  // ...but not implicitly
  FailWhen(implicit,"can't implicitly convert "+target_tid.toString()+" to "+tid.toString());
  const NestableContainer *nc = NestableContainer::isNestable(target_tid) ?
      static_cast<NestableContainer *>(target) : 0;
  FailWhen(!nc,"can't convert "+target_tid.toString()+" to "+tid.toString());
  TypeId ttid; bool dum;
  // access in scalar mode, checking that type is built-in
  const void *tdata = nc->get(HIID(),ttid,dum,TpNumeric,False);
  FailWhen( !convertScalar(tdata,ttid,data,tid),
            "can't convert "+ttid.toString()+" to "+tid.toString());
}

// This is called to access by reference, for all types
const void * NestableContainer::ConstHook::get_address(TypeId tid,bool must_write,bool implicit,bool pointer ) const
{
  // check for residual index
  FailWhen(resid.size(),"uninitialized element ["+resid.toString()+"]"); 
  FailWhen(resindex>=0,ssprintf("uninitialized element [%d]",resindex)); 
  if( tid != target_tid )
  {
    // type mismatch? Fail if implicit
    FailWhen(implicit,"can't implicitly convert "+target_tid.toString()+"* to "+tid.toString()+"*");
    // else try to treat it as a container, and access in scalar mode 
    const NestableContainer *nc = NestableContainer::isNestable(target_tid) ?
        static_cast<NestableContainer *>(target) : 0;
    FailWhen(!nc,"can't convert "+target_tid.toString()+" to "+tid.toString());
    FailWhen(!nc->type(),"this container does not support pointers");
    // check for scalar/vector violation
    if( nc->size()>1 )
    {
      FailWhen(!pointer,"accessing vector container as scalar");
      FailWhen(isDynamicType(nc->type()),"can't take pointer to vector of dynamic objects");
    }
    // access in scalar mode, verifying type & writability
    TypeId ttid; bool dum;
    return nc->get(HIID(),ttid,dum,tid,must_write);
  }
  return target;
}

// This is called to assign a value, for scalar & binary types
const void * NestableContainer::Hook::put_scalar( const void *data,TypeId tid,size_t sz ) const
{
  FailWhen(addressed,"unexpected '&' operator");
  FailWhen(!writable,"write access violation");
  // if we have a residual index, then assume container & create new object
  if( resid.size() || resindex>=0 )
  {
    FailWhen( !isDynamicType(target_tid),"element ["+resid.toString()+"] is not initialized");
    NestableContainer *nc = NestableContainer::isNestable(target_tid) ?
        static_cast<NestableContainer *>(target) : 0;
    FailWhen(!nc,"can't assign "+tid.toString()+" to "+target_tid.toString());
    // This will allocate space in the container for the object.
    // The resulting target_tid may be different from the requested tid
    // in the case of scalars (where conversion is allowed)
    TypeId dum;
    target = resindex>=0 ? nc->insert(resindex,tid,dum)
                         : nc->insert(resid,tid,dum);
  }
  if( tid != target_tid )
    FailWhen( !convertScalar(data,tid,target,target_tid),
          "can't assign "+tid.toString()+" to "+target_tid.toString() )
  else if( tid == Tpstring )
    *static_cast<string*>(const_cast<void*>(target)) = 
                                *static_cast<string*>(data);
  else 
    memcpy(const_cast<void*>(target),data,sz);
  return target;
}

// This is called to allocate a new object in the container (index is >0)
ObjRef * NestableContainer::Hook::alloc_objref (TypeId tid) const
{
  FailWhen( !isDynamicType(target_tid),"element ["+resid.toString()+"] is not initialized");
  NestableContainer *nc = NestableContainer::isNestable(target_tid) ?
        static_cast<NestableContainer *>(target) : 0;
  FailWhen(!nc,"can't assign "+tid.toString()+" to "+target_tid.toString());
  // This will allocate space in the container for the object, and
  // return a pointer to the ObjRef
  TypeId dum;
  return static_cast<ObjRef*>
    ( resindex>=0 ? nc->insert(resindex,tid,dum) : nc->insert(resid,tid,dum) );
}

// Helper function to assign an object.  
void NestableContainer::Hook::assign_object( BlockableObject *obj,TypeId tid,int flags ) const
{
  FailWhen(addressed,"unexpected '&' operator");
  FailWhen(!writable,"write access violation");
  // residual index -- allocate
  if( resid.size() || resindex>=0 )
    target = alloc_objref(tid);
  else
    FailWhen(target_tid != tid,"can't assign "+tid.toString()+" to "+target_tid.toString());
  static_cast<ObjRef*>(target)->unlock().attach(obj,flags);
}

// Helper function assigns an objref     
ObjRef & NestableContainer::Hook::assign_objref ( const ObjRef &ref,int flags ) const
{
  FailWhen(addressed,"unexpected '&' operator");
  FailWhen(!writable,"write access violation");
  // residual index -- allocate
  if( resid.size() || resindex>=0 )
    target = alloc_objref(ref->objectType());
  else
    FailWhen(target_tid != ref->objectType(),"can't assign "+
        ref->objectType().toString()+" to "+target_tid.toString());
  if( flags&DMI::COPYREF )
    return static_cast<ObjRef*>(target)->unlock().copy(ref,flags);
  else
    return static_cast<ObjRef*>(target)->unlock().xfer(const_cast<ObjRef&>(ref));
}

const NestableContainer::Hook & NestableContainer::Hook::init () const
{
  FailWhen(addressed,"unexpected '&' operator");
  FailWhen(!writable,"write access violation");
  if( resid.size() || resindex>=0 )
  {
    FailWhen( !isDynamicType(target_tid),"not a container");
    NestableContainer *nc = NestableContainer::isNestable(target_tid) ?
          static_cast<NestableContainer *>(target) : 0;
    FailWhen(!nc,"not a container");
    // This will allocate space in the container for the object
    TypeId dum;
    if( resindex>=0 )
      nc->insert(resindex,0,dum);
    else
      nc->insert(resid,0,dum);
  }
  return *this;
}

string NestableContainer::ConstHook::sdebug ( int detail,const string &prefix,const char *name ) const
{
  string out;
  if( detail == 0 )
    out = ssprintf("%s(%x)",name,(int)target);
  if( detail>0 || detail == -1 )
  {
    string targ;
    if( isDynamicType(target_tid) )
      targ = static_cast<BlockableObject*>(target)->sdebug(detail,prefix);
    else
      targ = target_tid.toString();
    out = ssprintf("%s(%s)",name,targ.c_str());
    if( resindex >=0 )
      Debug::appendf(out,"[%d]",resindex);
    if( resid.size() )
      Debug::appendf(out,"[%s]",resid.toString().c_str());
    if( writable )
      out += "W";
    if( addressed )
      out += "&";
  }
  return out;  
}

    
  //## end NestableContainer%3BE97CE100AF.declarations
//## begin module%3C10CC830069.epilog preserve=yes
//## end module%3C10CC830069.epilog
