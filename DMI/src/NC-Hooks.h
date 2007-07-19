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

protected:
// as_wp_impl() returns pointer and size, throws Uninitialized if must_exist=true
// default version (non-dynamic) checkes for exact type match
template<class T,class isDynamic>
T * as_wp_impl (int &sz,bool pointer,bool must_exist,Type2Type<T>,isDynamic) const
{
  STATIC_CHECK(DMITypeTraits<T>::isContainable,Type_not_supported_by_containers);
  ContentInfo info;
  const void *ptr = get_address(info,DMITypeTraits<T>::typeId,true,pointer,must_exist);
  sz = info.size;
  return static_cast<T*>(const_cast<void*>(ptr));
}
// version for dynamic types checks for castability
template<class T>
T * as_wp_impl (int &sz,bool pointer,bool must_exist,Type2Type<T>,Int2Type<true>) const
{
  ContentInfo info;
  info.tid = typeIdOf(T);
  const T * ptr = reinterpret_cast<const T*>(
                    get_address_bo(info,can_convert<T>,true,pointer,must_exist));
  sz = info.size;
  return const_cast<T*>(ptr);
}

    
public:
// -----------------------------------------------------------------------
// as_wp<T>(); as_wpo<T>(); as_wr<T>(); 
// returns non-const ("writable") pointer or reference
// + implicit conversion operators  
// -----------------------------------------------------------------------
template<class T>
T * as_wp (int &sz=_dum_int,Type2Type<T> =Type2Type<T>()) const
{ 
  return as_wp_impl(sz,true,true,Type2Type<T>(),Int2Type<SUPERSUBCLASS(BObj,T)>());
}

template<class T>
T * as_wpo (int &sz=_dum_int,Type2Type<T> =Type2Type<T>()) const
{ 
  return as_wp_impl(sz,true,false,Type2Type<T>(),Int2Type<SUPERSUBCLASS(BObj,T)>());
}

template<class T>
T * implicit_ptr (Type2Type<T> =Type2Type<T>()) const 
{ 
   FailWhen(!addressed,"missing '&' operator");
   int dum;
   return as_wp(dum,Type2Type<T>());
}
 

// as_wr<T>() returns writable reference  
template<class T>
T & as_wr (Type2Type<T> =Type2Type<T>()) const
{ 
  int dum;
  return *as_wp_impl(dum,false,true,Type2Type<T>(),Int2Type<SUPERSUBCLASS(BObj,T)>());
}

template<class T>
operator T* () const 
{ return implicit_ptr(Type2Type<T>()); }

// #define __convert1(T,arg) operator T* () const { return implicit_ptr(Type2Type<T>()); }
// // #define __convert2(T,arg) operator T& () const { return as_wr(Type2Type<T>()); }
// // #define __convert(T,arg) __convert1(T,) __convert2(T,) 
// // 
//  DoForAllNumericTypes(__convert1,);
//  DoForAllBinaryTypes(__convert1,);
// // DoForAllDynamicTypes(__convert1,);
//  DoForAllSpecialTypes(__convert1,);
// // DoForAllBinaryTypes(__convert2,);
// // DoForAllDynamicTypes(__convert2,);
// // DoForAllSpecialTypes(__convert2,);
// // 
// // #undef __convert
// // #undef __convert1
// // #undef __convert2
// // 

// -----------------------------------------------------------------------
// operator =
// -----------------------------------------------------------------------
protected:
// generic implementation of assign_impl will produce a compile-time error
// if called for an unsupported type category
template<class T,class isScalar,class isAssign,class isDynamic>
T& assign_impl (const T& value,isScalar,isAssign,isDynamic) const
{    
  STATIC_CHECK(false,Type_not_supported_by_containers);
  return const_cast<T&>(value);
}
// partial specialization for numeric types -- this should never happen,
// see assign_value below instead
template<class T,class Any1,class Any2>
T& assign_impl (const T& value,Int2Type<true>,Any1,Any2) const
{ 
  STATIC_CHECK(false,OOPS_shouldnt_be_here_ever_ever_ever);
  return const_cast<T&>(value); 
};
// partial specialization for binary structs & special types
// (uses the assignment operator)
template<class T,class Any1,class Any2>
T& assign_impl (const T& value,Any1,Int2Type<true>,Any2) const
{ 
  const int tid = DMITypeTraits<T>::typeId; 
  ContentInfo info; void *data = prepare_put(info,tid);
  DbgAssert(info.tid==tid); 
  return *static_cast<T*>(data) = value; 
};
// use reinterpret_cast below because these templates are instantiated
// when declaration of T is not yet available, thus static_cast to BObj* 
// doesn't work. These functions are only called for dynamic types
template<class T>
T& assign_dyn_impl (T* value,int flags) const
{ 
  assign_object(reinterpret_cast<BObj*>(value),TypeId(DMITypeTraits<T>::typeId),flags);
  return *value;
}
template<class T>
const T& assign_const_dyn_impl (const T* value,int flags) const
{ 
  assign_object(const_cast<BObj*>(reinterpret_cast<const BObj*>(value)),TypeId(DMITypeTraits<T>::typeId),DMI::READONLY|flags);
  return *value;
}

// numeric types assigned by value
template<class T>
T assign_value (T value) const
{ 
  put_scalar(&value,DMITypeTraits<T>::typeId,sizeof(T)); 
  return value; 
};

// finally, generate the generalized assignment method
template<class T>
T& assign (const T& value) const
{ 
  enum { Cat = DMITypeTraits<T>::TypeCategory };
  return assign_impl(value,
      Int2Type<int(Cat)==int(TypeInfo::NUMERIC)>(),
      Int2Type<int(Cat)==int(TypeInfo::BINARY ) || int(Cat)==int(TypeInfo::SPECIAL)>(),
      Int2Type<int(Cat)==int(TypeInfo::DYNAMIC)>()
    ); 
}

public:

// define specific assignment by-value for numeric types
#define __assign(T,arg) T operator = (T value) const { return assign_value(value); }
DoForAllNumericTypes(__assign,);
#undef __assign
#define __assign(T,arg) T& operator = (const T& value) const { return assign(value); }
DoForAllSpecialTypes(__assign,);
DoForAllBinaryTypes(__assign,);
#undef __assign
#define __assign(T,arg) \
  T& operator = (T& value) const { return assign_dyn_impl(&value,DMI::AUTOCLONE); } \
  const T& operator = (const T& value) const { return assign_const_dyn_impl(&value,DMI::AUTOCLONE); } \
  T& operator = (T* value) const { return assign_dyn_impl(value,0); } \
  const T& operator = (const T* value) const { return assign_const_dyn_impl(value,0); } 
DoForAllDynamicTypes(__assign,);
#undef __assign
// -----------------------------------------------------------------------
// some special assignments
// -----------------------------------------------------------------------
// special case: C strings assigned as STL strings
string & operator = ( const char *cstr ) const
{
  string str(cstr); 
  return assign(str); 
}

#ifdef AIPSPP_HOOKS
// assigning an AIPS++ array will init a DMI::Array object. This
// will also work for Vectors, Matrices and Cubes
template<class T>
void operator = (const casa::Array<T> &other) const;
// assigning an AIPS++ string assigns an STL string 
string & operator = (const casa::String &other) const;
#endif

// assigning an array returns void
template<class T,int N> 
void operator = (const blitz::Array<T,N> &other) const;

protected:
// // Templated function implements operator = (vector<T>) for arrayable types
// // moved to main header:
//  template<class T> 
//  void assign_arrayable (const std::vector<T> &other) const;
// Templated function implements operator = (vector<T>) for other types
template<class T,class Iter> 
void assign_sequence (uint size,Iter begin,Iter end,Type2Type<T>) const;
// helper template to select which vector assignment operation to use
template<class T>
void assign_vector_select (const std::vector<T> &other,Int2Type<false>) const
{ assign_sequence(other.size(),other.begin(),other.end(),Type2Type<T>()); }
template<class T>
void assign_vector_select (const std::vector<T> &other,Int2Type<true>) const
{ assign_arrayable(other.size(),other.begin(),other.end(),Type2Type<T>()); }

public:    
// Assigning an STL vector of some type will assign to the underlying 
// container (provided the shape/size matches), or inits a new DMI::Vec
template<class T>
void operator = (const std::vector<T> &other) const
{
  typedef DMITypeTraits<T> TT;
  STATIC_CHECK(TT::isNumeric || TT::isBinary || TT::isSpecial,
               Vector_cannot_be_assigned_to_container);
  assign_vector_select(other,Int2Type<TT::isLorrayable>());
}

// -----------------------------------------------------------------------
// get(T &var,bool init), get_vector(std::vector<T> &var,bool init)
// if hook target exists, assigns to var and returns true
// if target does not exist: if init=true, assigns var to target. Returns false
// -----------------------------------------------------------------------
template<class T>
bool get (T &value,bool init) const
{ 
  if( get_impl(value,Int2Type<DMITypeTraits<T>::TypeCategory>()) )
    return true;
  if( init )
    operator = (value);
  return false;
}

template<class T>
bool get_vector (std::vector<T> &value,bool init) const
{ 
  if( get_vector_impl(value,false) )
    return true;
  if( init )
    operator = (value);
  return false;
}


// -----------------------------------------------------------------------
// =: for CountedRefs, copies refs
// -----------------------------------------------------------------------
// // the transfer operator is defined for all counted refs -- it xfers a ref
// template<class T>
// void operator <<= ( CountedRef<T> &ref ) const 
// { 
//   assign_objref(ref.ref_cast(Type2Type<BObj>()),DMI::XFER); 
// }; 
// assigning countedrefs will make a copy
template<class T>
const CountedRef<T> & operator = ( const CountedRef<T> &ref ) const  
{ 
  assign_objref(ref.ref_cast(Type2Type<BObj>()),0); 
  return ref;
}

// -----------------------------------------------------------------------
// operator = and <<= 
// attach a dynamic type
// -----------------------------------------------------------------------
protected:
template<class T>
class RefTraits { 
  public: enum { isRef = false }; 
          typedef T & RetType; 
          typedef const T & ConstRetType; 
};
template<class T>
class RefTraits<CountedRef<T> > { 
  public: enum { isRef = true }; 
          typedef void RetType; 
          typedef void ConstRetType; 
};        
// generic implementation of xfer_impl will differentiate between
// object and ref, and produce a compile-time error if called for a non-dynamic type
template<class T,class isRef>
typename RefTraits<T>::RetType xfer_impl ( T * ptr,int flags,isRef ) const
{ 
  STATIC_CHECK(SUPERSUBCLASS(DMI::BObj,T),xfer_operator_only_available_for_dynamic_types);
  assign_object(ptr,ptr->objectType(),flags); 
  return *ptr; 
};
template<class T>
typename RefTraits<T>::RetType xfer_impl ( T * ptr,int,Int2Type<true> ) const
{ 
  assign_objref(ptr->ref_cast(Type2Type<DMI::BObj>()),DMI::XFER); 
};

template<class T>
typename RefTraits<T>::RetType xfer_impl ( T * ptr,int flags ) const
{ return xfer_impl(ptr,flags,Int2Type<RefTraits<T>::isRef>()); }

public:
// define operator <<= for dynamic types
template<class T>
typename RefTraits<T>::RetType operator <<= ( T * x ) const 
{ 
  return xfer_impl(x,DMI::ANONWR);
}
template<class T>
typename RefTraits<T>::ConstRetType operator <<= ( const T * x ) const 
{ 
  return xfer_impl(const_cast<T*>(x),DMI::ANON|DMI::READONLY);
}
template<class T>
typename RefTraits<T>::RetType operator <<= ( T & x ) const 
{ 
  return xfer_impl(&x,DMI::ANONWR);
}
template<class T>
typename RefTraits<T>::ConstRetType operator <<= ( const T & x ) const 
{ 
  return xfer_impl(const_cast<T*>(&x),DMI::ANON|DMI::READONLY);
}



