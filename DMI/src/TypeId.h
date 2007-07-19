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

#ifndef DMI_TypeId_h
#define DMI_TypeId_h 1

#include <TimBase/LofarTypedefs.h>
#include <TimBase/Lorrays.h>
#include <DMI/DMI.h>
#include <DMI/TypeIterMacros.h>
#include <DMI/Registry.h>
#include <DMI/AtomicID.h>
#include <DMI/Loki/TypeTraits.h>
#include <DMI/Loki/TypeManip.h>
#include <complex>
    
#ifndef LORRAYS_USE_BLITZ
  #error AIPS++ array support disabled for now
#endif

namespace DMI
{

using Loki::TypeTraits;

//##ModelId=3BFBA88F001D
typedef AtomicID TypeId;

// these are now in LofarTypedefs.h
// standard type definitions
// //##ModelId=3DB9343F00F1
// typedef unsigned char uchar;
// //##ModelId=3DB9343F01C4
// typedef unsigned short ushort;
// //##ModelId=3DB9343F012D
// typedef unsigned int uint;
// //##ModelId=3DB9343F015F
// typedef unsigned long ulong;
// //##ModelId=3DB9343F00B5
// typedef long long longlong;
// //##ModelId=3DB9343F0191
// typedef unsigned long long ulonglong;
// //##ModelId=3DB9343F0051
// typedef long double ldouble;
// //##ModelId=3DB9343F0015
// typedef complex<float> fcomplex;
// //##ModelId=3DB9343E03CB
// typedef complex<double> dcomplex;

#ifndef DoForAllNumericTypes1
// Defines alternative version of the <for all numeric types>
// macro, with comma as separator
#define DoForAllNumericTypes1(Do,arg) \
        Do(char,arg) , \
        Do(uchar,arg) , \
        Do(short,arg) , \
        Do(ushort,arg) , \
        Do(int,arg) , \
        Do(uint,arg) , \
        Do(long,arg) , \
        Do(ulong,arg) , \
        Do(longlong,arg) , \
        Do(ulonglong,arg) , \
        Do(float,arg) , \
        Do(double,arg) , \
        Do(ldouble,arg) , \
        Do(fcomplex,arg) , \
        Do(dcomplex,arg) , \
        Do(bool,arg) 
#endif

// arrays are supported for a limited subset of scalar types (for Glish
// compatibility)

#ifndef DoForAllArrayTypes
// These are the type iterators for all arrayable types
// NB: for now, strings are disabled, until Ger adds the template instantiation
#define DoForAllArrayTypes_Sep(Do,arg,sep) Do(bool,arg) sep Do(uchar,arg) sep Do(short,arg) sep Do(int,arg) sep Do(float,arg) sep Do(double,arg) sep Do(dcomplex,arg) sep Do(fcomplex,arg) 
#define DoForAllArrayTypes(Do,arg) DoForAllArrayTypes_Sep(Do,arg,;)
#define DoForAllArrayTypes1(Do,arg) Do(bool,arg), Do(uchar,arg), Do(short,arg), Do(int,arg), Do(float,arg), Do(double,arg), Do(dcomplex,arg), Do(fcomplex,arg)

// Another iterator for numeric but non-arrayble types (this is needed
// for, e.g., template instantiation, where you define a specialization for
// arrayable types, and want to instantiate the non-arrayable ones from
// the default template)
#define DoForAllNonArrayTypes_Sep(Do,arg,sep) Do(char,arg) sep Do(ushort,arg) sep Do(uint,arg) sep Do(long,arg) sep Do(ulong,arg) sep Do(longlong,arg) sep Do(ulonglong,arg) sep Do(ldouble,arg) 
#define DoForAllNonArrayTypes(Do,arg) DoForAllNonArrayTypes_Sep(Do,arg,;)
#endif

// define typelist of arrayable types. A limited subset is supported for now,
// for compatibility with Glish
namespace DMI_TL
{
  using namespace Loki::TL;
  typedef TYPELIST_8(bool,uchar,short,int,float,double,dcomplex,fcomplex)
            Arrayables;
}

// Declare the standard types.
// Numbers will be explicitly assigned; note that TypeIds are negative
// so Tpbool will be -32, Tpchar -33, etc.
// Basic types occupy the space between -32 and -63, ranked by precision.
// Numerics are from -32 to -47, and string is -48.
// Note that order is vitally important: the numbers must be defined in
// the same order as in the DoForAllNumericTypes macro.

#pragma type +bool=32
#pragma type +char=33 +uchar=34 +short=35 +ushort=36 +int=37 +uint=38 
#pragma type +long=39 +ulong=40 +longlong=41 +ulonglong=42 
#pragma type +float=43 +double=44 +ldouble=45 
#pragma type +fcomplex=46 +dcomplex=47
#pragma type noinclude =string=48

// For arrays, numbers are explicitly assigned as type + 32*(rank+1) 
// but we don't define separate constants. Just these inlines here:

// TpArray(tpelem,ndim) returns the TypeId of array with element type tpelem,
// and rank ndim,
#define TpArray_int(tpelem,ndim) (-(32*(ndim) - (tpelem)))
inline TypeId TpArray (TypeId tpelem,int ndim)
{ return TpArray_int(tpelem.id(),ndim); }
// Alias for vector
inline TypeId TpVec (TypeId tpelem)
{ return TpArray(tpelem,1); }
// Alias for matrix
inline TypeId TpMat (TypeId tpelem)
{ return TpArray(tpelem,2); }
// Alias for cube
inline TypeId TpCube (TypeId tpelem)
{ return TpArray(tpelem,3); }

#pragma type :DMI::AtomicID

// these constants are used to distinguish built-ins from other types
// (note that actual numeric values are all negative)
const int TpFirstNumeric = -47, TpLastNumeric = -32,
      TpNumberOfNumerics = TpLastNumeric - TpFirstNumeric;

// Some special type constants
// The null type 
const TypeId NullType(0),TpNull(0);
// Numeric type
const TypeId TpNumeric(-9);
// Incomplete type
const TypeId TpIncomplete(-8);
// Dereferenced type (see DMI::Container::get())
const TypeId TpObject(-7);

//##ModelId=3E9BD9150133
class TypeCategories
{
  public:
    //##ModelId=3E9BD915013C
    typedef enum 
    { 
      NONE=0,NUMERIC=1,BINARY=2,DYNAMIC=3,SPECIAL=4,INTERMEDIATE=5,OTHER=6 
    } Category;
};

//##ModelId=3E9BD914029D
template<class T>
class DMIBaseTypeTraits : public TypeTraits<T>
{
  public:
  // define DMI-specific type traits.
  // This is the default definition; all DMI-supported types
  // will provide a specialization.
  // can type go into a DMI::Container?
    //##ModelId=3E9BD91702B5
  enum { isContainable = false };
  // TypeId
    //##ModelId=3E9BD91702C2
  enum { typeId = 0 };
  // what is this type's DMI category? Default is other
    //##ModelId=3E9BD91702CF
  enum { TypeCategory = TypeCategories::OTHER };
  // how is this type passed to/returned from a DMI::Container? 
    //##ModelId=3E9BD91402C3
  typedef typename TypeTraits<T>::ParameterType ContainerReturnType;
    //##ModelId=3E9BD91402CD
  typedef typename TypeTraits<T>::ParameterType ContainerParamType;
};
  

// this uses the base DMI traits to compute some derived ones
//##ModelId=3E9BD91402E7
template<class T>
class DMITypeTraits : public DMIBaseTypeTraits<T>
{
  public:
  //    some simple bools derived from the type category
    //##ModelId=3E9BD91702EB
  enum { isNumeric      = int(DMIBaseTypeTraits<T>::TypeCategory) == int(TypeCategories::NUMERIC) };
    //##ModelId=3E9BD91702F7
  enum { isBinary       = int(DMIBaseTypeTraits<T>::TypeCategory) == int(TypeCategories::BINARY) };
    //##ModelId=3E9BD9170304
  enum { isDynamic      = int(DMIBaseTypeTraits<T>::TypeCategory) == int(TypeCategories::DYNAMIC) };
    //##ModelId=3E9BD9170311
  enum { isSpecial      = int(DMIBaseTypeTraits<T>::TypeCategory) == int(TypeCategories::SPECIAL) };
    //##ModelId=3E9BD917031D
  enum { isIntermediate = int(DMIBaseTypeTraits<T>::TypeCategory) == int(TypeCategories::INTERMEDIATE) };
    //##ModelId=3E9BD917032A
  enum { isOther        = int(DMIBaseTypeTraits<T>::TypeCategory) == int(TypeCategories::OTHER) };
  // does this type support Lorrays?
    //##ModelId=3E9BD9170337
  enum { isLorrayable = DMI_TL::IndexOf<DMI_TL::Arrayables,T>::value >= 0 };
    //##ModelId=3E9BD9170345
  enum { isArrayable  = isLorrayable };
  enum { isLorray     = false };
  enum { isArray      = true };
};

// a partial specialization of the traits for Lorrays
template<class T,int N>
class DMIBaseTypeTraits< blitz::Array<T,N> > : public TypeTraits< blitz::Array<T,N> >
{
  public:
  enum { isContainable = DMITypeTraits<T>::isLorrayable && N<10 };
  enum { typeId = TpArray_int(DMIBaseTypeTraits<T>::typeId,N) };
  enum { TypeCategory = TypeCategories::INTERMEDIATE };
  enum { isLorray     = true };
  enum { isArray      = true };
  typedef T ArrayElemType; 
  typedef blitz::Array<T,N> ContainerReturnType;
  typedef const blitz::Array<T,N> & ContainerParamType;
  enum { ParamByRef = true, ReturnByRef = false };
};

};
#endif
