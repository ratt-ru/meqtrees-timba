
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
// -----------------------------------------------------------------------
// as_impl()
// helper methods for as<T>()
// -----------------------------------------------------------------------

// takes dynamic cast and returns true if ptr can be converted to given type
template<class T>
static bool can_convert (const DMI::BObj *ptr)
{ return dynamic_cast<const T *>(ptr) != 0; }

// returns the type name as a string
template<class T>
static string DMITypeName (Type2Type<T> = Type2Type<T>())
{ return TypeId(DMITypeTraits<T>::typeId).toString(); }


// as_impl() with default value
// catch-all template for impossible type traits
//    first int2type: ParamByRef; second: isDynamic; third: type category
//    Note that abstract base classes of dynamic types will have a type
//    category of OTHER; the dynamic version of as_impl (see below)
//    can handle them anyway, thus the type category is actually ignored
//    for isDynamic=true
template<class T,class ParamByRef,class isDynamic,class Category> // 
const T & as_impl (const T &def,ParamByRef,isDynamic,Category) const
{
  STATIC_CHECK(false,Oops_illegal_combination_of_type_traits_in_container_access);
  return def;
}
// This is a default version for passing in by ref and returning ref/value
// Works for non-dynamic and non-scalar types
template<class T,class Category> 
typename DMITypeTraits<T>::ContainerReturnType 
    as_impl (const T& deflt,Int2Type<true>,Int2Type<false>,Category) const
{
  STATIC_CHECK(DMITypeTraits<T>::isContainable,Type_not_supported_by_containers);
  ContentInfo info;
  const void *ptr = get_address(info,DMITypeTraits<T>::typeId,false,false,false); 
  return ptr ? *static_cast<const T*>(ptr) : deflt;
}
// specialization for scalars: pass in and return by value, with implicit conversion
template<class T> 
T as_impl (T deflt,Int2Type<false>,Int2Type<false>,Int2Type<TypeCategories::NUMERIC>) const
{
  T x; 
  return get_scalar(&x,DMITypeTraits<T>::typeId,false) ? x : deflt; 
} 
// specialization for dynamic types: access as base type (DMI::BObj), then use
// dynamic cast to see if type is compatible. This allows subclasses to be visible as
// parent classes
template<class T,class ParamByRef,class Category> // 
const T & as_impl (const T &deflt,ParamByRef,Int2Type<true>,Category) const
{
  ContentInfo info;
  info.tid = typeIdOf(T);
  const T * ptr = reinterpret_cast<const T*>(
                      get_address_bo(info,can_convert<T>,false,false,false));
  return ptr ? *ptr : deflt;
}


// as_impl() with no default value
// default version: no conversion, types expected to match exactly
template<class T,class isDynamic,class Category> 
typename DMITypeTraits<T>::ContainerReturnType 
    as_impl (Type2Type<T>,isDynamic,Category) const
{
  STATIC_CHECK(DMITypeTraits<T>::isContainable,Type_not_supported_by_containers);
  ContentInfo info;
  return *static_cast<const T*>( get_address(info,DMITypeTraits<T>::typeId,false,
                                        false,true) ); 
}
// specialization for scalar version: do numeric conversion
template<class T>  
T as_impl (Type2Type<T>,Int2Type<false>,Int2Type<TypeCategories::NUMERIC>) const
{
 T x; get_scalar(&x,DMITypeTraits<T>::typeId); 
 return x; 
}
// specialization for dynamic types: access as base type (DMI::BObj), then use
// dynamic cast to see if type is compatible. This allows subclasses to be visible as
// parent classes
template<class T,class Category> // first int2type: isScalar; second int2type: isDynamic
const T & as_impl (Type2Type<T>,Int2Type<true>,Category) const
{
  ContentInfo info;
  info.tid = typeIdOf(T);
  return *reinterpret_cast<const T*>( get_address_bo(info,can_convert<T>,false,false,true) );
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
  STATIC_CHECK(false,Method_get_cannot_be_used_with_this_type);
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
{ 
  return as_impl(Type2Type<T>(),
                  Int2Type<SUPERSUBCLASS(BObj,T)>(),
                  Int2Type<DMITypeTraits<T>::TypeCategory>()); 
}

// as<T>(default_value)  
template<class T>
typename DMITypeTraits<T>::ContainerReturnType as (typename DMITypeTraits<T>::ContainerParamType deflt) const
{ 
  return as_impl(deflt,Int2Type<DMITypeTraits<T>::ParamByRef>(),
                  Int2Type<SUPERSUBCLASS(BObj,T)>(),
                  Int2Type<DMITypeTraits<T>::TypeCategory>());
}
  

protected:
// as_p_impl() returns pointer and size, throws Uninitialized if must_exist=true
// default (non-dynamic) version checked for exact type match
template<class T,class isDynamic>
const T * as_p_impl (int &sz,bool must_exist,Type2Type<T>,isDynamic) const
{
  STATIC_CHECK(DMITypeTraits<T>::isContainable,Type_not_supported_by_containers);
  ContentInfo info;
  const void *ptr = get_address(info,DMITypeTraits<T>::typeId,false,true,must_exist); 
  sz = info.size;
  return static_cast<const T*>(ptr);
}
// version for dynamic types checks for castability
template<class T>
const T * as_p_impl (int &sz,bool must_exist,Type2Type<T>,Int2Type<true>) const
{
  ContentInfo info;
  info.tid = typeIdOf(T);
  const T * ptr = reinterpret_cast<const T*>(get_address_bo(info,can_convert<T>,false,true,must_exist)); 
  sz = info.size;
  return ptr;
}

public:
// as_p<T>() returns pointer, throws Uninitialized if no such element
template<class T>
const T * as_p (int &sz=_dum_int,Type2Type<T> = Type2Type<T>()) const
{
  return as_p_impl(sz,true,Type2Type<T>(),Int2Type<SUPERSUBCLASS(BObj,T)>());
}

// as_po<T>() (for "pointer, optional") returns pointer, or 0 if no such element
template<class T>
const T * as_po (int &sz=_dum_int,Type2Type<T> = Type2Type<T>()) const
{
  return as_p_impl(sz,false,Type2Type<T>(),Int2Type<SUPERSUBCLASS(BObj,T)>());
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

// // stupid compiler can't figure this out, hence the explicit instantiations below:
// template<class T>
// operator typename DMITypeTraits<T>::ContainerReturnType () const
// { return as(Type2Type<T>()); }
// 
#define __convert(T,arg) operator DMITypeTraits<T>::ContainerReturnType () const { return as(Type2Type<T>()); }
DoForAllNumericTypes(__convert,);
DoForAllBinaryTypes(__convert,);
DoForAllSpecialTypes(__convert,);
// DoForAllDynamicTypes(__convert,);
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
  STATIC_CHECK( int(DMITypeTraits<T>::TypeCategory) != int(TypeCategories::INTERMEDIATE),
      Cannot_take_pointer_to_intermediate_type);
  FailWhen(!addressed,"missing '&' operator");
  int dum;
  return as_p(dum,Type2Type<T>()); 
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

// define a specialization of as<T> for T=vector<T1>
// NB: doesn't work, as it confuses the compiler
// template<class T>
// std::vector<T> as (Type2Type<std::vector<T> > = Type2Type<std::vector<T> >()) const
// { std::vector<T> res; get_vector(res,true); return res; }
// template<class T>
// std::vector<T> as (const std::vector<T> &deflt ) const
// { std::vector<T> res; return get_vector(res,false) ?  res : deflt; }
// 
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
casa::Array<T> as_AipsArray (Type2Type<T> =Type2Type<T>()) const;
template<class T> 
casa::Vector<T> as_AipsVector (Type2Type<T> =Type2Type<T>()) const;
template<class T> 
casa::Matrix<T> as_AipsMatrix (Type2Type<T> =Type2Type<T>()) const;
casa::String as_String () const;

// provide implicit conversions using the accessors above
template<class T> 
operator casa::Array<T> () const 
{ return as_AipsArray(Type2Type<T>()); }
template<class T>
operator casa::Vector<T> () const 
{ return as_AipsVector(Type2Type<T>()); }
template<class T> 
operator casa::Matrix<T> () const 
{ return as_AipsMatrix(Type2Type<T>()); }
operator casa::String () const
{ return as_String(); }
#endif
