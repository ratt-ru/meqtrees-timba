protected:
// -----------------------------------------------------------------------
// as_impl_wp<T>()
// Internal helper template that maps to get_address
// If used with an incompatible type, a compile-time error is generated
// -----------------------------------------------------------------------
template<class T>
T * as_impl_wp (T *,ContentInfo &info=_dum_info,bool pointer=False) const
{ 
  STATIC_CHECK(DMITypeTraits<T>::isContainable,Type_not_supported_by_containers);
  return static_cast<T*>(const_cast<void*>(
      get_address(info,DMITypeTraits<T>::typeId,True,pointer))); 
} 

public:
// -----------------------------------------------------------------------
// as_wr<T>(); as_wp<T>()
// returns non-const ("writable") reference or pointer
// + implicit conversion operators  
// -----------------------------------------------------------------------
template<class T>
T * as_wp (int &sz=_dum_int) const
{ 
  ContentInfo info;
  T * ptr = as_impl_wp((T*)0,info,True);
  sz = info.size;
  return ptr;
} 

template<class T>
T * implicit_ptr (Type2Type<T> =Type2Type<T>()) const 
{ 
   FailWhen(!addressed,"missing '&' operator");
   return as_impl_wp((T*)0,_dum_info,True);
}
 

// as_wr<T>() returns writable reference  
template<class T>
T & as_wr (Type2Type<T> =Type2Type<T>()) const
{ 
  return *as_impl_wp((T*)0);
} 

#define __convert1(T,arg) operator T* () const { return implicit_ptr(Type2Type<T>()); }
// #define __convert2(T,arg) operator T& () const { return as_wr(Type2Type<T>()); }
// #define __convert(T,arg) __convert1(T,) __convert2(T,) 
// 
 DoForAllNumericTypes(__convert1,);
 DoForAllBinaryTypes(__convert1,);
 DoForAllDynamicTypes(__convert1,);
 DoForAllSpecialTypes(__convert1,);
// DoForAllBinaryTypes(__convert2,);
// DoForAllDynamicTypes(__convert2,);
// DoForAllSpecialTypes(__convert2,);
// 
// #undef __convert
// #undef __convert1
// #undef __convert2
// 
 
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

// generate special error for dynamic types (must use <<= )
template<class T,class Any1,class Any2>
T& assign_impl (const T& value,Any1,Any2,Int2Type<true>) const
{ 
  STATIC_CHECK(false,Cannot_use_assignment_with_dynamic_types_use_xfer_instead);
};

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
// assigning an AIPS++ array will init a DataArray object. This
// will also work for Vectors, Matrices and Cubes
template<class T>
void operator = (const Array<T> &other) const;
// assigning an AIPS++ string assigns an STL string 
string & operator = (const String &other) const;
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
// container (provided the shape/size matches), or inits a new DataField
template<class T>
void operator = (const std::vector<T> &other) const
{
  typedef DMITypeTraits<T> TT;
  STATIC_CHECK(TT::isNumeric || TT::isBinary || TT::isSpecial,
               Vector_cannot_be_assigned_to_container);
  assign_vector_select(other,Int2Type<TT::isLorrayable>());
}

// -----------------------------------------------------------------------
// <<= and =: xfer or copy CountedRefs
// -----------------------------------------------------------------------
// the transfer operator is defined for all counted refs -- it xfers a ref
template<class T>
void operator <<= ( const CountedRef<T> &ref ) const 
{ 
  assign_objref(ref.ref_cast(Type2Type<BlockableObject>()),0); 
}; 
// assigning countedrefs will make a copy
template<class T>
const CountedRef<T> & operator = ( const CountedRef<T> &ref ) const  
{ 
  assign_objref(ref.ref_cast(Type2Type<BlockableObject>()),DMI::COPYREF|DMI::PRESERVE_RW); 
  return ref;
}

// -----------------------------------------------------------------------
// operator <<= 
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
  STATIC_CHECK(SUPERSUBCLASS(BlockableObject,T),xfer_operator_only_available_for_dynamic_types);
  assign_object(ptr,ptr->objectType(),flags); 
  return *ptr; 
};
template<class T>
typename RefTraits<T>::RetType xfer_impl ( T * ptr,int,Int2Type<true> ) const
{ 
  assign_objref(ptr->ref_cast(Type2Type<BlockableObject>()),0); 
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



