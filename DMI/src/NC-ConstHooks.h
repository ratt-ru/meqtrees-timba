
protected:
// as_impl_p()
// Internal helper template that eventually maps to get_address
// If used with an incompatile type, a compile-time error is generated
template<class T>
const T * as_impl_p (const T * deflt,ContentInfo &info=_dum_info,bool pointer=False) const
{ 
  STATIC_CHECK(DMITypeTraits<T>::isContainable,Type_not_supported_by_containers);
  return static_cast<const T*>(
      get_address(info,DMITypeTraits<T>::typeId,False,pointer,deflt)); 
} 

// as_impl() with default value
// This is a version for non-scalar types; pass in by ref; return *as_impl_p
template<class T> // first int2type: ParamByRef; second: isScalar 
typename DMITypeTraits<T>::ContainerReturnType 
    as_impl (const T& deflt,Int2Type<true>,Int2Type<false>) const
{
  return *as_impl_p(&deflt);
}
// This is a version for non-scalar types; pass in by value; return *as_impl_p
template<class T> // first int2type: ParamByRef; second: isScalar
typename DMITypeTraits<T>::ContainerReturnType 
    as_impl (T deflt,Int2Type<false>,Int2Type<false>) const
{
  return *as_impl_p(&deflt);
}
// version for scalars: pass in and return by value, with conversion
template<class T> // first int2type: ParamByRef; second: isScalar
T as_impl (T deflt,Int2Type<false>,Int2Type<true>) const
{
 T x; return get_scalar(&x,DMITypeTraits<T>::typeId,True) ? x : deflt; 
} 
// both scalar and by-ref is impossible, so throw an error
template<class T> // first int2type: ParamByRef; second: isScalar
T as_impl (T,Int2Type<true>,Int2Type<true>) const
{
  STATIC_CHECK(false,Oops_unexpected_type_traits_scalar_and_by_ref);
  return T();
} 
// as_impl() with no default value
// scalar version will provide conversion (and return by-value), non-scalar won't
template<class T> // int2type: isScalar
typename DMITypeTraits<T>::ContainerReturnType 
    as_impl (Int2Type<false>,Type2Type<T>  = Type2Type<T>()) const
{
  return *as_impl_p((T*)0);
}
template<class T> // int2type: isScalar
T as_impl (Int2Type<true>,Type2Type<T> = Type2Type<T>()) const
{
 T x; get_scalar(&x,DMITypeTraits<T>::typeId); 
 return x; 
} 
// BUG, damn it! Lorrays inhibit checking for writability

// now, implement the public as() methods:
public:
// as<T>() 
template<class T>
typename DMITypeTraits<T>::ContainerReturnType as (Type2Type<T> = Type2Type<T>()) const
{ return as_impl(Int2Type<DMITypeTraits<T>::isNumeric>(),Type2Type<T>()); }

// as<T>(default_value)  
template<class T>
typename DMITypeTraits<T>::ContainerReturnType as (typename DMITypeTraits<T>::ContainerParamType deflt) const
{ return as_impl(deflt,Int2Type<DMITypeTraits<T>::ParamByRef>(),Int2Type<DMITypeTraits<T>::isNumeric>()); }

// as_p<T>() returns pointer  
template<class T>
const T * as_p (int &sz=_dum_int,Type2Type<T> = Type2Type<T>()) const
{ 
  ContentInfo info;
  const T * ptr = as_impl_p((T*)0,info,True);
  sz = info.size;
  return ptr;
} 

// implicit conversion operators

// stupid compiler can't figure this out, hence the explicit instantiations below:
// template<class T>
// operator typename DMITypeTraits<T>::ContainerReturnType () const
// { return as(Type2Type<T>()); }

#define __convert(T,arg) operator DMITypeTraits<T>::ContainerReturnType () const { return as(Type2Type<T>()); }
DoForAllNumericTypes(__convert,);
DoForAllBinaryTypes(__convert,);
DoForAllSpecialTypes(__convert,);
DoForAllDynamicTypes(__convert,);
// DoForAllIntermediateTypes(__convert,);
#undef __convert

// arrays returned by value
template<class T,int N>
operator blitz::Array<T,N> () const
{ return as(Type2Type<blitz::Array<T,N> >()); }


// implicit conversions to pointers
template<class T>
operator const T * () const 
{ 
  STATIC_CHECK( int(DMITypeTraits<T>::TypeCategory) != int(TypeCategories::INTERMEDIATE),
      Cannot_take_pointer_to_intermediate_type);
  FailWhen(!addressed,"missing '&' operator");
  return as_impl_p((T*)0,_dum_info,True);
}

// Define an as_vector<> template. This should work for all
// contiguous containers.
template<class T>
std::vector<T> as_vector (Type2Type<T> =Type2Type<T>()) const;
// second version provides a default value
template<class T>
std::vector<T> as_vector (const std::vector<T> &deflt) const;
// partial specialization of implicit conversion to vectors
template<class T>
operator std::vector<T> () const
{ return as_vector(Type2Type<T>()); }

#ifdef AIPSPP_HOOKS
// define accessors for some AIPS++ types
template<class T> 
Array<T> as_AipsArray (Type2Type<T> =Type2Type<T>()) const;
template<class T> 
Vector<T> as_AipsVector (Type2Type<T> =Type2Type<T>()) const;
template<class T> 
Matrix<T> as_AipsMatrix (Type2Type<T> =Type2Type<T>()) const;
String as_String () const;

// provide implicit conversions using the accessors above
template<class T> 
operator Array<T> () const 
{ return as_AipsArray(Type2Type<T>()); }
template<class T>
operator Vector<T> () const 
{ return as_AipsVector(Type2Type<T>()); }
template<class T> 
operator Matrix<T> () const 
{ return as_AipsMatrix(Type2Type<T>()); }
operator String () const
{ return as_String(); }
#endif
