
protected:
// -----------------------------------------------------------------------
// as_impl()
// helper methods for as<T>()
// -----------------------------------------------------------------------

// as_impl() with default value
// This is a version for non-scalar types; pass in by ref; return ref/value
template<class T> // first int2type: ParamByRef; second: isScalar 
typename DMITypeTraits<T>::ContainerReturnType 
    as_impl (const T& deflt,Int2Type<true>,Int2Type<false>) const
{
  STATIC_CHECK(DMITypeTraits<T>::isContainable,Type_not_supported_by_containers);
  ContentInfo info;
  const void *ptr = get_address(info,DMITypeTraits<T>::typeId,False,False,False); 
  return ptr ? *static_cast<const T*>(ptr) : deflt;
}
// This is a version for non-scalar types; pass in by value; return ref/value
template<class T> // first int2type: ParamByRef; second: isScalar
typename DMITypeTraits<T>::ContainerReturnType 
    as_impl (T deflt,Int2Type<false>,Int2Type<false>) const
{
  STATIC_CHECK(DMITypeTraits<T>::isContainable,Type_not_supported_by_containers);
  ContentInfo info;
  const void *ptr = get_address(info,DMITypeTraits<T>::typeId,False,
                                false,false); 
  return ptr ? *static_cast<const T*>(ptr) : deflt;
}
// version for scalars: pass in and return by value, with conversion
template<class T> // first int2type: ParamByRef; second: isScalar
T as_impl (T deflt,Int2Type<false>,Int2Type<true>) const
{
  T x; 
  return get_scalar(&x,DMITypeTraits<T>::typeId,False) ? x : deflt; 
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
  STATIC_CHECK(DMITypeTraits<T>::isContainable,Type_not_supported_by_containers);
  ContentInfo info;
  return *static_cast<const T*>( get_address(info,DMITypeTraits<T>::typeId,False,
                                        False,True) ); 
}
template<class T> // int2type: isScalar
T as_impl (Int2Type<true>,Type2Type<T> = Type2Type<T>()) const
{
 T x; get_scalar(&x,DMITypeTraits<T>::typeId); 
 return x; 
}

// -----------------------------------------------------------------------
// get_impl()
// helper methods for get<T>()
// -----------------------------------------------------------------------

// get_impl(T &val): assign & return true if value is available, return 
// false if not
// Default version catches illegal type use
template<class T,class TypeCategory>
bool get_impl (T&,TypeCategory) const
{
  STATIC_CHECK(false,Get_cannot_be_used_with_this_type);
  return false;
}
    
// scalar version will provide conversion, 
template<class T> // int2type: isScalar=false
bool get_impl (T &value,Int2Type<TypeCategories::NUMERIC>) const
{
  return get_scalar(&value,DMITypeTraits<T>::typeId,false);
}

// non-scalar version just uses the assignment operator
template<class T> 
bool get_impl (T &value,Int2Type<TypeCategories::BINARY>) const
{
  ContentInfo info;
  const void *ptr = get_address(info,DMITypeTraits<T>::typeId,false,false,false); 
  return ptr ? (value=*static_cast<const T*>(ptr)),true : false;
}
template<class T> 
bool get_impl (T &value,Int2Type<TypeCategories::SPECIAL>) const
{
  return get_impl(value,Int2Type<TypeCategories::BINARY>());
}

// array version
template<class T,class isArray> 
bool get_impl_intermediate (T &value,isArray) const
{
  STATIC_CHECK(false,Get_cannot_be_used_with_this_type);
  return false;
}
template<class T> 
bool get_impl_intermediate (T &value,Int2Type<true>) const
{
  ContentInfo info;
  const void *ptr = get_address(info,DMITypeTraits<T>::typeId,false,false,false); 
  return ptr ? value.reference(*static_cast<const T*>(ptr)),true : false;
}

template<class T> 
bool get_impl (T &value,Int2Type<TypeCategories::INTERMEDIATE>) const
{
  return get_impl_intermediate(value,Int2Type<DMITypeTraits<T>::isArray>());
}

// -----------------------------------------------------------------------
// as<T>(), as<T>(default), as_p<T>()
// -----------------------------------------------------------------------

public:
// as<T>() 
template<class T>
typename DMITypeTraits<T>::ContainerReturnType as (Type2Type<T> = Type2Type<T>()) const
{ return as_impl(Int2Type<DMITypeTraits<T>::isNumeric>(),Type2Type<T>()); }

// as<T>(default_value)  
template<class T>
typename DMITypeTraits<T>::ContainerReturnType as (typename DMITypeTraits<T>::ContainerParamType deflt) const
{ return as_impl(deflt,Int2Type<DMITypeTraits<T>::ParamByRef>(),Int2Type<DMITypeTraits<T>::isNumeric>()); }

// as_p<T>() returns pointer, throws Uninitialized if no such element
template<class T>
const T * as_p (int &sz=_dum_int,Type2Type<T> = Type2Type<T>()) const
{
  STATIC_CHECK(DMITypeTraits<T>::isContainable,Type_not_supported_by_containers);
  ContentInfo info;
  const void *ptr = get_address(info,DMITypeTraits<T>::typeId,False,True,True); 
  sz = info.size;
  return static_cast<const T*>(ptr);
}

// as_po<T>() (for "pointer, optional") returns pointer, or 0 if no such element
template<class T>
const T * as_po (int &sz=_dum_int,Type2Type<T> = Type2Type<T>()) const
{
  STATIC_CHECK(DMITypeTraits<T>::isContainable,Type_not_supported_by_containers);
  ContentInfo info;
  const void *ptr = get_address(info,DMITypeTraits<T>::typeId,False,True,False); 
  sz = info.size;
  return static_cast<const T*>(ptr);
}

// -----------------------------------------------------------------------
// get(T &var)
// if hook target exists, assigns to var and returns true
// if target does not exist, returns false
// -----------------------------------------------------------------------

template<class T>
bool get (T &value) const
{ return get_impl(value,Int2Type<DMITypeTraits<T>::TypeCategory>()); }


// -----------------------------------------------------------------------
// implicit conversion operators
// -----------------------------------------------------------------------

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


// -----------------------------------------------------------------------
// conversion to array 
// BUG, damn it! Lorrays inhibit checking for writability
// -----------------------------------------------------------------------

template<class T,int N>
operator blitz::Array<T,N> () const
{ return as(Type2Type<blitz::Array<T,N> >()); }



// -----------------------------------------------------------------------
// implicit conversion to pointers
// -----------------------------------------------------------------------

template<class T>
operator const T * () const 
{ 
  STATIC_CHECK(DMITypeTraits<T>::isContainable,Type_not_supported_by_containers);
  STATIC_CHECK( int(DMITypeTraits<T>::TypeCategory) != int(TypeCategories::INTERMEDIATE),
      Cannot_take_pointer_to_intermediate_type);
  FailWhen(!addressed,"missing '&' operator");
  ContentInfo info;
  return static_cast<const T*>( get_address(info,DMITypeTraits<T>::typeId,False,
                                True,True) ); 
}


// -----------------------------------------------------------------------
// conversion to std::vector
// -----------------------------------------------------------------------

// helper function gets vector, optionally ensuring existence
protected:
template<class T>
bool get_vector_impl (std::vector<T> &value,bool must_exist) const;

public:
// Define a get_vector<> template. This should work for all contiguous 
// containers.
template<class T>
bool get_vector (std::vector<T> &value) const
{ return get_vector_impl(value,false); }

// Define an as_vector<> template. This should work for all
// contiguous containers.
template<class T>
std::vector<T> as_vector (Type2Type<T> =Type2Type<T>()) const
{ std::vector<T> res; get_vector_impl(res,true); return res; }
// second version provides a default value
template<class T>
std::vector<T> as_vector (const std::vector<T> &deflt) const
{ std::vector<T> res; return get_vector_impl(res,false) ?  res : deflt; }

// partial specialization of implicit conversion to vectors
template<class T>
operator std::vector<T> () const
{ std::vector<T> res; get_vector_impl(res,true); return res; }

// // define a specialization of as<T> for T=vector<T1>
// NB: doesn't work, as it confuses the compiler
// template<class T>
// std::vector<T> as (Type2Type<std::vector<T> > = Type2Type<std::vector<T> >()) const
// { std::vector<T> res; get_vector(res,true); return res; }
// template<class T>
// std::vector<T> as (const std::vector<T> &deflt ) const
// { std::vector<T> res; return get_vector(res,false) ?  res : deflt; }

// // define a specialization of get<T> for T=vector<T1>
// template<class T>
// bool get (std::vector<T> &value) const
// { return get_vector(value,false); }
    

// -----------------------------------------------------------------------
// conversion to some AIPS++ types
// -----------------------------------------------------------------------

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
