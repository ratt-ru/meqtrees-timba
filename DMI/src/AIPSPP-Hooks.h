#ifndef AIPSPP_Hooks_h
#define AIPSPP_Hooks_h 1
    
#ifdef AIPSPP_HOOKS
    
#include <aips/Arrays/Array.h>
#include <aips/Arrays/Vector.h>
#include <aips/Arrays/Matrix.h>
#include <aips/Utilities/String.h>
    
#include "DMI/DataField.h"
#include "DMI/DataArray.h"

inline String NestableContainer::ConstHook::as_String () const
{
  return String((*this).as_string());
}

template<class T>
inline Vector<T> NestableContainer::ConstHook::as_Vector () const
{
  int n;
  const T *data = &((*this).size(n));
  return Vector<T>(IPosition(1,n),data);
}

template<>
inline Vector<String> NestableContainer::ConstHook::as_Vector<String> () const
{
  int n;
  const string *data = &((*this).size(n));
  Vector<String> vec(n);
  for( int i=0; i<n; i++ )
    vec(i) = data[i];
  return vec;
}

template<class T>
inline Matrix<T> NestableContainer::ConstHook::as_Matrix (int n1,int n2) const
{
  int n;
  const T *data = &((*this).size(n));
  FailWhen(n!=n1*n2,"array size mismatch");
  return Matrix<T>(IPosition(2,n1,n2),data);
}

// template<class MVal>
// MVal NestableContainer::ConstHook::as_MV ()
// {
//   return MVal(as_Vector<double>);
// }
// 
// template<class Meas>
// Meas NestableContainer::ConstHook::as_M (const Meas::Types &type)
// {
//   return Meas(as_MV<Meas::MVType>(),type);
// }
// 

inline const Vector<String> & NestableContainer::Hook::operator = (const Vector<String> &other) const
{
  DataField *df = new DataField(Tpstring,other.nelements());
  (*this) <<= df;
  for( uint i=0; i<other.nelements(); i++ )
    (*df)[i] = other(i);
  return other;
}

inline const String & NestableContainer::Hook::operator = (const String &other) const
{
  (*this) = static_cast<const string &>(other);
  return other;
}

#endif

#endif
