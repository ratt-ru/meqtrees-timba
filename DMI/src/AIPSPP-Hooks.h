#ifndef DMI_AIPSPP_Hooks_h
#define DMI_AIPSPP_Hooks_h 1
    
#ifdef AIPSPP_HOOKS
    
#include <aips/Arrays/Array.h>
#include <aips/Arrays/Vector.h>
#include <aips/Arrays/Matrix.h>
#include <aips/Utilities/String.h>
    
#include "DMI/DataArray.h"

namespace AIPSPP_Hooks 
{
  // templated helper method to create a 1D array using a copy of data
  template<class T>
  Array<T> copyVector (int n,const void *data)
  { 
    return Array<T>(IPosition(1,n),static_cast<const T*>(data));
  };

  // specialization for String, with conversion from std::string
  template<>
  Array<String> copyVector (int n,const void *data)
  { 
    String *dest0 = new String[n], *dest = dest0;
    const string *src = static_cast<const string *>(data);
    for( int i=0; i<n; i++,dest++,src++ )
      *dest = *src;
    return Array<String>(IPosition(1,n),dest0,TAKE_OVER);
  };
};


inline String NestableContainer::ConstHook::as_String () const
{
  return String((*this).as_string());
}

template<class T>
Array<T> NestableContainer::ConstHook::as_AipsArray () const
{
  ContentInfo info;
  const void *target;
  // resolve any existing index
  if( index>=0 || id.size() )
  {
    target = collapseIndex(info,0,0);
    FailWhen(!target,"uninitialized element");
  }
  else
  {
    target = nc;
    info.tid = nc->objectType();
    info.size = 1;
  }
  // If pointing at an ObjRef, dereference to object
  if( info.tid == TpObjRef )
  {
    FailWhen( !static_cast<const ObjRef*>(target)->valid(),"invalid ObjRef" );
    target = static_cast<const ObjRef*>(target)->deref_p();
    info.tid = static_cast<const BlockableObject *>(target)->objectType();
    info.size = 1;
  }
  // Have we resolved to a DataArray? 
  if( info.tid == TpDataArray )
    return static_cast<const DataArray *>(target)->copyAipsArray((T*)0);
  // no, then try to treat target as a container in scalar mode
  TypeId tid = typeIdOf(T);
  FailWhen( !nextNC(asNestable(target,info.tid)),
            "can't convert "+info.tid.toString()+" to vector of "+tid.toString());
  int flags = autoprivatize|DMI::NC_SCALAR|DMI::NC_POINTER;
  target = nc->get(HIID(),info,tid,flags);
  FailWhen( !target,"can't convert "+info.tid.toString()+" to vector of "+tid.toString());
  // make 1D array by copying container data
  return AIPSPP_Hooks::copyVector<T>(info.size,target);
}

template<class T>
Vector<T> NestableContainer::ConstHook::as_AipsVector () const
{
  Array<T> arr = as_AipsArray();
  FailWhen( arr.ndim() != 1,"can't access array as Vector" );
  return Vector<T>(arr);
}

template<class T>
Matrix<T> NestableContainer::ConstHook::as_AipsMatrix () const
{
  Array<T> arr = as_AipsArray();
  FailWhen( arr.ndim() != 2,"can't access array as Matrix" );
  return Matrix<T>(arr);
}

template<class T>
const Array<T> & NestableContainer::Hook::operator = (const Array<T> &other) const
{
  (*this) <<= new DataArray(other,DMI::WRITE);
}

// assigning a String simply assigns a string
inline const String & NestableContainer::Hook::operator = (const String &other) const
{
  (*this) = static_cast<const string &>(other);
  return other;
}

#endif

#endif
