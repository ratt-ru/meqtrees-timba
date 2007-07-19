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

#include "TypeInfo.h"
#include "TypeIterMacros.h"

namespace DMI
{
    
static AtomicID::Register reg1(TpNumeric,"Numeric"),
    reg2(TpIncomplete,"Incomplete"),
    reg3(TpObject,"Object");

// This inserts AtomicID::Register definitions for all array types and ranks
#define _regarray(type,rank) static AtomicID::Register reg##type##rank(TpArray(Tp##type,rank),"Array(" #type "," #rank ")");
#define _regrank(rank,arg) DoForAllArrayTypes(_regarray,rank);
DoForAllArrayRanks(_regrank,);
#undef _regarray
#undef _regrank

// Defines the TypeInfo registry    
DefineRegistry(TypeInfoReg,TypeInfo::NONE);

// -----------------------------------------------------------------------
// type converter, scalar-scalar
// -----------------------------------------------------------------------

// templated inline function to convert scalars. Sadly needed because g++ 4.x
// does not allow implicit conversions from non-complex type (e.g. 
// "float y; float _Complex x = y" is an error), but instead needs an explicit 
// "float _Complex x = y + 0i". 
template <class From,class To>
static inline void _Convert (const From *x,To *y)
{ *y = To(*x); }

#ifndef USE_STD_COMPLEX
template <class From>
static inline void _Convert (const From *x,fcomplex *y)
{ *y = float(*x) + 0.fi; }
template <class From>
static inline void _Convert (const From *x,dcomplex *y)
{ *y = double(*x) + 0.i; }
#endif

//--- templated implementation of a type converter, scalar to scalar
template<class From,class To> 
bool _convertScaSca (const void * from,void * to)
{ 
  _Convert(static_cast<const From *>(from),static_cast<To*>(to)); 
  return true;
}
//    special case for complex-to-non-complex: use real part
template<class From,class To> 
bool _convertComplexScaSca (const void * from,void * to)
{ 
  *static_cast<To*>(to) = To(creal(*static_cast<const From *>(from))); 
  return true;
}
template<> 
bool _convertComplexScaSca<dcomplex,dcomplex> (const void * from,void * to)
{ 
  memcpy(to,from,sizeof(dcomplex));
  return true;
}
template<> 
bool _convertComplexScaSca<fcomplex,fcomplex> (const void * from,void * to)
{ 
  memcpy(to,from,sizeof(fcomplex));
  return true;
}
template<> 
bool _convertComplexScaSca<dcomplex,fcomplex> (const void * from,void * to)
{ 
  *static_cast<fcomplex*>(to) = *static_cast<const dcomplex *>(from); 
  return true;
}
template<> 
bool _convertComplexScaSca<fcomplex,dcomplex> (const void * from,void * to)
{ 
  *static_cast<dcomplex*>(to) = *static_cast<const fcomplex *>(from); 
  return true;
}

//--- convert scalar to single-element vector
template<class From,class To> 
bool _convertScaVec (const void * from,void * to)
{ 
  blitz::Array<To,1> &arr = *static_cast<blitz::Array<To,1>*>(to);
  if( arr.numElements() != 1 )
    return false;
  return _convertScaSca<From,To>(from,arr.data());
//  *(arr.data()) = To(*static_cast<const From *>(from)); 
//  return true;
}
//    special case for complex: use real part
template<class From,class To> 
bool _convertComplexScaVec (const void * from,void * to)
{ 
  blitz::Array<To,1> &arr = *static_cast<blitz::Array<To,1>*>(to);
  if( arr.numElements() != 1 )
    return false;
  return _convertComplexScaSca<From,To>(from,arr.data());
//  *(arr.data()) = To(static_cast<const From *>(from)->real()); 
//  return true;
}
//--- convert single-element vector to scalar
template<class From,class To> 
bool _convertVecSca (const void * from,void * to)
{ 
  const blitz::Array<From,1> &arr = *static_cast<const blitz::Array<From,1>*>(from);
  if( arr.numElements() != 1 )
    return false;
  return _convertScaSca<From,To>(arr.data(),to);
//  *static_cast<To*>(to) = To(*(arr.data()));
//  return true;
}
//    special case for complex: use real part
template<class From,class To> 
bool _convertComplexVecSca (const void * from,void * to)
{ 
  const blitz::Array<From,1> &arr 
      = *static_cast<const blitz::Array<From,1>*>(from);
  if( arr.numElements() != 1 )
    return false;
  return _convertComplexScaSca<From,To>(arr.data(),to);
//  *static_cast<To*>(to) = To(arr.data()->real());
//  return true;
}

// This defines the conversion matrices
#undef From
#define From(type,arg) _convertScaSca<arg,type>
#undef FromComplex
#define FromComplex(type,arg) _convertComplexScaSca<arg,type>
TypeConverter _typeconverters_sca_sca[16][16] = 
{
  { DoForAllNumericTypes1(From,bool) },
  { DoForAllNumericTypes1(From,char) },
  { DoForAllNumericTypes1(From,uchar) },
  { DoForAllNumericTypes1(From,short) },
  { DoForAllNumericTypes1(From,ushort) },
  { DoForAllNumericTypes1(From,int) },
  { DoForAllNumericTypes1(From,uint) },
  { DoForAllNumericTypes1(From,long) },
  { DoForAllNumericTypes1(From,ulong) },
  { DoForAllNumericTypes1(From,longlong) },
  { DoForAllNumericTypes1(From,ulonglong) },
  { DoForAllNumericTypes1(From,float) },
  { DoForAllNumericTypes1(From,double) },
  { DoForAllNumericTypes1(From,ldouble) },
  { DoForAllNumericTypes1(FromComplex,fcomplex) },
  { DoForAllNumericTypes1(FromComplex,dcomplex) } 
};

// This defines the conversion matrices
#undef From
#define From(type,arg) _convertVecSca<arg,type>
#undef FromComplex
#define FromComplex(type,arg) _convertComplexVecSca<arg,type>
TypeConverter _typeconverters_vec_sca[16][16] = 
{
  { DoForAllNumericTypes1(From,bool) },
  { DoForAllNumericTypes1(From,char) },
  { DoForAllNumericTypes1(From,uchar) },
  { DoForAllNumericTypes1(From,short) },
  { DoForAllNumericTypes1(From,ushort) },
  { DoForAllNumericTypes1(From,int) },
  { DoForAllNumericTypes1(From,uint) },
  { DoForAllNumericTypes1(From,long) },
  { DoForAllNumericTypes1(From,ulong) },
  { DoForAllNumericTypes1(From,longlong) },
  { DoForAllNumericTypes1(From,ulonglong) },
  { DoForAllNumericTypes1(From,float) },
  { DoForAllNumericTypes1(From,double) },
  { DoForAllNumericTypes1(From,ldouble) },
  { DoForAllNumericTypes1(FromComplex,fcomplex) },
  { DoForAllNumericTypes1(FromComplex,dcomplex) } 
};

// This defines the conversion matrices
#undef From
#define From(type,arg) _convertScaVec<arg,type>
#undef FromComplex
#define FromComplex(type,arg) _convertComplexScaVec<arg,type>
TypeConverter _typeconverters_sca_vec[16][16] = 
{
  { DoForAllNumericTypes1(From,bool) },
  { DoForAllNumericTypes1(From,char) },
  { DoForAllNumericTypes1(From,uchar) },
  { DoForAllNumericTypes1(From,short) },
  { DoForAllNumericTypes1(From,ushort) },
  { DoForAllNumericTypes1(From,int) },
  { DoForAllNumericTypes1(From,uint) },
  { DoForAllNumericTypes1(From,long) },
  { DoForAllNumericTypes1(From,ulong) },
  { DoForAllNumericTypes1(From,longlong) },
  { DoForAllNumericTypes1(From,ulonglong) },
  { DoForAllNumericTypes1(From,float) },
  { DoForAllNumericTypes1(From,double) },
  { DoForAllNumericTypes1(From,ldouble) },
  { DoForAllNumericTypes1(FromComplex,fcomplex) },
  { DoForAllNumericTypes1(FromComplex,dcomplex) } 
};



};
