//# Vells.h: Values for Meq expressions
//#
//# Copyright (C) 2002
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//# This program is free software; you can redistribute it and/or modify
//# it under the terms of the GNU General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or
//# (at your option) any later version.
//#
//# This program is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License
//# along with this program; if not, write to the Free Software
//# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//# $Id$

#ifndef MEQ_VELLS_H
#define MEQ_VELLS_H

#include <DMI/DataArray.h>

// This provides a list of operators and functions defined by Vells

// Unary operators
#define DoForAllUnaryOperators(Do,x) \
          Do(-,UNARY_MINUS,x)
// Binary operators
#define DoForAllBinaryOperators(Do,x) \
          Do(+,ADD,x) Do(-,SUB,x) Do(*,MUL,x) Do(/,DIV,x) 
// In-place operators
#define DoForAllInPlaceOperators(Do,x) \
          Do(+,ADD1,x) Do(-,SUB1,x) Do(*,MUL1,x) Do(/,DIV1,x) 

// Unary functions are split up several groups
#define DoForAllUnaryFuncs(Do,x)  DoForAllUnaryFuncs1(Do,x)  \
                                  DoForAllUnaryFuncs2(Do,x)  \
                                  DoForAllUnaryFuncs3(Do,x)  \
                                  DoForAllUnaryFuncs4(Do,x)  
                                
// Unary group 1: defined for all Vells. Preserves real/complex
#define DoForAllUnaryFuncs1(Do,x) \
  Do(cos,x) Do(cosh,x) Do(exp,x) Do(log,x) Do(log10,x) Do(sin,x) Do(sinh,x) \
  Do(sqr,x) Do(sqrt,x) Do(tan,x) Do(tanh,x) \
  Do(pow2,x) Do(pow3,x) Do(pow4,x) Do(pow5,x) Do(pow6,x) Do(pow7,x) Do(pow8,x)

// Unary group 2: defined for real Vells only
#define DoForAllUnaryFuncs2(Do,x) \
  Do(ceil,x) Do(floor,x) Do(acos,x) Do(asin,x) Do(atan,x) 

// Unary group 3: defined for all Vells, but result is always real
#define DoForAllUnaryFuncs3(Do,x) \
  Do(abs,x) Do(fabs,x) Do(norm,x) Do(arg,x) Do(real,x) Do(imag,x) 
  
// Unary group 4: all others, requiring special treatment
#define DoForAllUnaryFuncs4(Do,x) \
  Do(conj,x) Do(min,x) Do(max,x) Do(mean,x) Do(sum,x) Do(product,x)

// skip these for now:
//  Do(cexp) Do(csqrt) 
  
// Binary functions
#define DoForAllBinaryFuncs(Do,x) \
  Do(posdiff,x) Do(tocomplex,x) Do(pow,x) Do(atan2,x)

namespace Meq {

// Conditionally include declarations for Vells math.
// Skipping these functions saves time/memory when compiling code that
// doesn't need them (such as the Meq service classes, and Vells itself).
// The functions go into their own separate namespace. This keeps the 
// compiler from tripping over abs() and such.
#ifndef MEQVELLS_SKIP_FUNCTIONS
class Vells;
namespace VellsMath 
{
  #define declareUnaryFunc(FUNCNAME,x) \
    Vells FUNCNAME (const Vells &);
  DoForAllUnaryFuncs(declareUnaryFunc,);
  #define declareBinaryFunc(FUNCNAME,x) \
    Vells FUNCNAME (const Vells &,const Vells &);
  DoForAllBinaryFuncs(declareBinaryFunc,);
  #undef declareUnaryFunc
  #undef declareBinaryFunc
};
#endif

// we provide four versions of each operation (real scalar, complex scalar,
// real matrix, complex matrix). In the future this may be extended to
// vectors
const int VELLS_LUT_SIZE = 4;

//##ModelId=3F86886E0229
class Vells : public SingularRefTarget
{
public:
    //##ModelId=400E530400F0
  typedef CountedRef<Vells> Ref;
    
  // A null vector (i.e. no vector assigned yet).
  // This can be used to clear the 'cache'.
    //##ModelId=3F86887001D4
  Vells();

  // Create a scalar Vells from a value. Default is temporary Vells.
  // <group>
    //##ModelId=3F86887001D5
  Vells (double value,bool temp=True);
    //##ModelId=3F86887001DC
  Vells (const dcomplex& value,bool temp=True);
  // <group>

  // Create a Vells of given size.
  // If the init flag is true, the matrix is initialized to the given value.
  // Otherwise the value only indicates the type of matrix to be created.
  // <group>
    //##ModelId=3F86887001E3
  Vells (double, int nx, int ny, bool init=true);
    //##ModelId=3F86887001F6
  Vells (const dcomplex&, int nx, int ny, bool init=true);
  // <group>

  // Create a Vells from a blitz array.
  // <group>
    //##ModelId=3F8688700209
  explicit Vells (LoMat_double&);
    //##ModelId=3F868870020F
  explicit Vells (LoMat_dcomplex&);
  // </group>
  
  // Create a Vells from a DataArray pointer
  // Default is reference semantics (attaches ref to array), unless 
  // DMI::PRIVATIZE is specified, in which case the array is privatized.
  // <group>
    //##ModelId=3F8688700216
  explicit Vells (DataArray *,int flags = 0);
    //##ModelId=3F868870021C
  explicit Vells (const DataArray *,int flags = 0);
  // creates from array ref. Ref is transferred
    //##ModelId=3F8688700223
  explicit Vells (const DataArray::Ref::Xfer &ref);
  // </group>

  // Copy constructor (reference semantics, unless DMI::PRIVATIZE is specified)
    //##ModelId=3F868870022A
  Vells (const Vells& that,int flags = DMI::COPYREF);

    //##ModelId=3F8688700238
  ~Vells();

  // Assignment (reference semantics).
    //##ModelId=3F868870023B
  Vells& operator= (const Vells& other);

  virtual void privatize (int flags=0,int depth=0);
  
  // Clones the matrix -- assures of a private copy
    //##ModelId=3F8688700249
  Vells clone () const
  { return Vells(*this,DMI::PRIVATIZE); }

  // is it a null vells?
    //##ModelId=3F8688700280
  bool isNull() const
    { return !(itsArray.valid()); }

  // Is the Vells a temporary object? The constructors above always
  // produce a non-temp Vells. Vells math (below) uses the private
  // constructors to produce temp Vells. Temp Vells allow for efficient 
  // re-use of storage.
    //##ModelId=400E53560092
  bool isTemp () const
    { return itsIsTemp; }
  
  bool isWritable () const
    { return !itsArray.valid() || itsArray.isWritable(); }
  
    //##ModelId=400E53560099
  void makeWritable () 
  { 
//    FailWhen(!itsArray.isWritable(),"Vells: r/w access violation");
    if( itsArray.valid() && !itsArray.isWritable() )
      initArrayPointers(0,DMI::PRIVATIZE|DMI::WRITE);
  }

  // changes the temp property
    //##ModelId=400E5356009D
  Vells & makeTemp (bool temp=true) 
  { itsIsTemp = temp; return *this; }
  
    //##ModelId=400E535600A9
  Vells & makeNonTemp () 
  { itsIsTemp = false; return *this; }
  
  const LoShape2 & shape () const
    { return itsShape; }
  
    //##ModelId=3F8688700279
  int nx() const
    { return itsShape[0]; }

    //##ModelId=3F868870027C
  int ny() const
    { return itsShape[1]; }

    //##ModelId=3F868870027E
  int nelements() const
    { return nx()*ny(); }

    //##ModelId=400E535600AC
  bool isScalar() const
    { return itsIsScalar; }
    //##ModelId=400E535600B0
  bool isArray() const
    { return !itsIsScalar; }
  
    //##ModelId=3F868870028A
  bool isReal() const
    { return itsRealArray != 0; }
    //##ModelId=400E535600B5
  bool isComplex() const
    { return itsComplexArray != 0; }
  
// returns true if this is a higher-ranked Vells (i.e. complex>double,array>scalar)
    //##ModelId=400E535600B9
  bool higherThan (const Vells &other) const
  { return isComplex() > other.isComplex() || isArray() > other.isArray(); }

  // returns true if type/shape matches other
    //##ModelId=400E535600CE
  bool isCongruent (const Vells &other) const
    { return isReal() == other.isReal() && shape() == other.shape(); }
  
  // returns true if type/shape matches the one specified
    //##ModelId=400E535600E7
  bool isCongruent (bool is_Real,const LoShape2 &shp) const
    { return isReal() == is_Real && shape() == shp; }
  
  bool isCongruent (bool is_Real,int nx,int ny) const
    { return isCongruent(is_Real,LoShape2(nx,ny)); }
  
    //##ModelId=400E53560109
  const DataArray & getDataArray () const
    { return *itsArray; }
  
    //##ModelId=400E5356010C
  DataArray & getDataArrayWr ()
    { return itsArray(); }

  // Provides access to underlying arrays
  // In debug mode, check type
    //##ModelId=3F868870028C
  const LoMat_double& getRealArray() const
  { DbgAssert(itsRealArray!=0); return *itsRealArray; }
    //##ModelId=3F868870028F
  const LoMat_dcomplex& getComplexArray() const
  { DbgAssert(itsComplexArray!=0); return *itsComplexArray; }
    //##ModelId=3F8688700291
  LoMat_double& getRealArray()
  { DbgAssert(itsRealArray!=0); makeWritable(); 
    return *const_cast<LoMat_double*>(itsRealArray); }
    //##ModelId=3F8688700292
  LoMat_dcomplex& getComplexArray()
  { DbgAssert(itsComplexArray!=0); makeWritable(); 
    return *const_cast<LoMat_dcomplex*>(itsComplexArray); }
  
  // initializes with value
    //##ModelId=3F8688700294
  void init (double val)
  { if (isReal()) getRealArray()=val; else getComplexArray()=dcomplex(val); }

  // Define templated as<T>() function
  // Default version will produce a compile-time error; specializations
  // are provided below for double, dcomplex, LoMat_double and LoMat_dcomplex
  template<class T> const T & as (Type2Type<T> = Type2Type<T>() ) const
  { STATIC_CHECK(0,illegal_Vells_as_type); }
  template<class T> T & as (Type2Type<T> = Type2Type<T>()) 
  { STATIC_CHECK(0,illegal_Vells_as_type); }
  
  // Define templated getStorage<T>() function
  // Default version will produce a compile-time error; specializations
  // are provided below for double & dcomplex
  template<class T>
  const T* getStorage ( Type2Type<T> = Type2Type<T>() ) const
  { STATIC_CHECK(0,illegal_Vells_getStorage_type); }
  template<class T>
  T* getStorage ( Type2Type<T> = Type2Type<T>() )
  { STATIC_CHECK(0,illegal_Vells_getStorage_type); }
 
  // Provides access to array storage
    //##ModelId=3F8688700295
  const double* realStorage() const
  { return getRealArray().data(); }
    //##ModelId=3F8688700298
  double* realStorage()
  { return getRealArray().data(); }
    //##ModelId=3F8688700299
  const dcomplex* complexStorage() const
  { return getComplexArray().data(); }
    //##ModelId=3F868870029B
  dcomplex* complexStorage()
  { return getComplexArray().data(); }
  
  // copies data from other Vells. Checks for matching shape/type
    //##ModelId=400E53560110
  void copyData (const Vells &other);
  
  // zeroes data
    //##ModelId=400E5356011C
  void zeroData ();
  
  // dumps to output
    //##ModelId=3F8688700282
  void show (std::ostream& os) const;

    //##ModelId=400E5356011F
  string sdebug (int detail=1,const string &prefix="",const char *nm=0) const;
  

private:
  // helper function for constructors
    //##ModelId=400E5356013E
  void initFromDataArray (const DataArray *parr,int flags);
  void initArrayPointers (const DataArray *parr,int flags);
    
    //##ModelId=400E53560024
  DataArray::Ref  itsArray;

    //##ModelId=3F86887001A3
  const LoMat_double*   itsRealArray;
    //##ModelId=3F86887001AB
  const LoMat_dcomplex* itsComplexArray;
    //##ModelId=3F86887001B3
  LoShape2              itsShape;
    //##ModelId=400E5356002F
  bool            itsIsTemp;
    //##ModelId=400E53560039
  bool            itsIsWritable;
    //##ModelId=3F86887001C3
  bool            itsIsScalar;
  
  // OK, now it gets hairy. Implement math on Vells
  // The following flags may be supplied to the constructors below:
    //##ModelId=400E530400FC
  typedef enum { 
    VF_REAL         = 1, 
    VF_COMPLEX      = 2, 
    VF_SCALAR       = 4,
    VF_CHECKREAL    = 8,
    VF_CHECKCOMPLEX = 16
  } VellsFlags;
  // Special constructor for a result of a unary Vells operation.
  // If other is a temporary Vells, will re-use its storage if possible,
  // otherwise, will create new storage. 
  // By default, the Vells will have the same type/shape as 'other', but
  // flags may override it:
  //    flags&VF_REAL     forces a real Vells
  //    flags&VF_COMPLEX  forces a complex Vells
  //    flags&VF_SCALAR   forces a scalar Vells
  //    flags&VF_CHECKxxx input must be real/complex (exception otherwise)
  // The opname argument is used for error reporting
    //##ModelId=3F8688700231
  Vells (const Vells &other,int flags,const std::string &opname);

  // Special constructor for a result of a binary Vells operation.
  // If either a or b is a temporary Vells, will re-use its storage if possible.
  // Otherwise, will create new storage. 
  // By default, the type/shape of the Vells will be chosen via type/shape
  // promotion, but flags may override it:
  //    flags&VF_REAL     forces a real Vells
  //    flags&VF_COMPLEX  forces a complex Vells
  //    flags&VF_SCALAR   forces a scalar Vells
  //    flags&VF_CHECKxxx input must be real/complex (exception otherwise)
  // The opname argument is used for error reporting
    //##ModelId=400E53560174
  Vells (const Vells &a,const Vells &b,int flags,const std::string &opname);

  // helper function for these two constructors
    //##ModelId=400E5356019D
  bool tryReference (bool real,const Vells &other);
  
// returns lookup table index for a combination of Vells properties
//      bit 0: isComplex, bit 1: isArray
// 0: real scalar 1: real array, 2: complex scalar, 3: complex array
    //##ModelId=400E535601B4
  static int getLutIndex (bool isCompl,bool isArr)
  { return (isCompl<<1) + isArr; }
  
// returns LUT index for this Vells  
    //##ModelId=400E535601CB
  int getLutIndex () const
  { return getLutIndex(isComplex(),isArray()); }
  
  
public:
// pointer to function implementing an unary operation 
    //##ModelId=400E53040108
  typedef void (*UnaryOperPtr)(Vells &out,const Vells &in);
// pointer to function implementing a binary operation 
    //##ModelId=400E53040116
  typedef void (*BinaryOperPtr)(Vells &out,const Vells &,const Vells &);
// pointer to unary function returning new result by value
//  typedef Vells (*UnaryFuncPtr)(const Vells &in);
  
// Declares inline unary operator OPER (internally named OPERNAME),
// plus lookup table for implementations
// This: 1. Creates a result Vells (using the special constructor to
//          decide whether to duplicate or reuse the storage), and 
//       2. Calls the method in the OPERNAME_lut lookup table, using the
//          LUT index of this Vells object. 
#define declareUnaryOperator(OPER,OPERNAME,x) \
  private: static UnaryOperPtr unary_##OPERNAME##_lut[VELLS_LUT_SIZE];  \
  public: Vells operator OPER () const \
          { Vells result(*this,0,"operator "#OPER); \
            (*unary_##OPERNAME##_lut[getLutIndex()])(result,*this);  \
            return result; }
          
// Declares binary operator OPER (internally named OPERNAME)
// plus lookup table for implementations
// This: 1. Creates a result Vells (using the special constructor to
//          decide whether to duplicate or reuse the storage), and 
//       2. Calls the method in the OPERNAME_lut lookup table, using the
//          LUT index generated from the two Vells operands
#define declareBinaryOperator(OPER,OPERNAME,x) \
  private: static BinaryOperPtr binary_##OPERNAME##_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE];  \
  public: Vells operator OPER (const Vells &right) const \
          { Vells result(*this,right,0,"operator "#OPER); \
            (*binary_##OPERNAME##_lut[getLutIndex()][right.getLutIndex()])(result,*this,right);  \
            return result; }
            
// Declares in-place (i.e. += and such) operator OPER (internally named OPERNAME)
// plus lookup table for implementations
// This just calls the method in the OPERNAME_lut lookup table, using the
// LUT index of this Vells object. The Vells itself is used as the result
// storage.
#define declareInPlaceOperator(OPER,OPERNAME,x) \
  private: static UnaryOperPtr inplace_##OPERNAME##_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE];  \
  public: Vells & operator OPER##= (const Vells &right) \
          { if( right.higherThan(*this) ) { \
              (*this) = (*this) OPER right; \
            } else { \
              (*inplace_##OPERNAME##_lut[getLutIndex()][right.getLutIndex()])(*this,right); \
            } \
            return *this; \
          }

// Defines lookup tables for implementations of unary math functions
#define declareUnaryFuncLut(FUNCNAME,x) \
  private: static UnaryOperPtr unifunc_##FUNCNAME##_lut[VELLS_LUT_SIZE];  
  
// Declares binary function FUNCNAME
// Defines lookup tables for implementations of binary math functions
#define declareBinaryFuncLut(FUNCNAME,x) \
  private: static BinaryOperPtr binfunc_##FUNCNAME##_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE];  

// insert all declarations using the macros above  
    //##ModelId=400E535601D0
  DoForAllUnaryOperators(declareUnaryOperator,);
    //##ModelId=400E535601D9
  DoForAllInPlaceOperators(declareInPlaceOperator,);
    //##ModelId=400E535601E3
  DoForAllBinaryOperators(declareBinaryOperator,);
    //##ModelId=400E535601EC
  DoForAllUnaryFuncs(declareUnaryFuncLut,);
    //##ModelId=400E535601F6
  DoForAllBinaryFuncs(declareBinaryFuncLut,);

#undef declareUnaryOperator
#undef declareInPlaceOperator
#undef declareBinaryOperator
#undef declareUnaryFuncLut
#undef declareBinaryFuncLut
  
// Conditionally include friend declarations for Vells math.
// Skipping them saves time/memory when compiling code that
// doesn't need them (such as the Meq service classes, and Vells itself).
// Also, it avoids namespace pollution and leads to more sensible compiler
// errors.
#ifndef MEQVELLS_SKIP_FUNCTIONS
  #define declareUnaryFunc(FUNCNAME,x) \
    public: friend Vells VellsMath::FUNCNAME (const Vells &);
    //##ModelId=400E53560200
  DoForAllUnaryFuncs(declareUnaryFunc,);
  
  #define declareBinaryFunc(FUNCNAME,x) \
    public: friend Vells VellsMath::FUNCNAME (const Vells &,const Vells &);
    //##ModelId=400E5356020A
  DoForAllBinaryFuncs(declareBinaryFunc,);
  
  #undef declareUnaryFunc
  #undef declareBinaryFunc
#endif
};

// Conditionally include inline definitions of Vells math functions
#ifndef MEQVELLS_SKIP_FUNCTIONS

#define defineUnaryFunc(FUNCNAME,flags) \
  inline Vells VellsMath::FUNCNAME (const Vells &arg) \
  { Vells result(arg,flags,#FUNCNAME); \
    (*Vells::unifunc_##FUNCNAME##_lut[arg.getLutIndex()])(result,arg); \
    return result; }

DoForAllUnaryFuncs1(defineUnaryFunc,0);
DoForAllUnaryFuncs2(defineUnaryFunc,Vells::VF_REAL|Vells::VF_CHECKREAL);
DoForAllUnaryFuncs3(defineUnaryFunc,Vells::VF_REAL);
// all others
defineUnaryFunc(conj,0);
defineUnaryFunc(min,Vells::VF_SCALAR|Vells::VF_REAL|Vells::VF_CHECKREAL);
defineUnaryFunc(max,Vells::VF_SCALAR|Vells::VF_REAL|Vells::VF_CHECKREAL);
defineUnaryFunc(mean,Vells::VF_SCALAR);
defineUnaryFunc(sum,Vells::VF_SCALAR);
defineUnaryFunc(product,Vells::VF_SCALAR);

#define defineBinaryFunc(FUNCNAME,flags) \
  inline Vells VellsMath::FUNCNAME (const Vells &left,const Vells &right) \
  { Vells result(left,right,flags,#FUNCNAME); \
    (*Vells::binfunc_##FUNCNAME##_lut[left.getLutIndex()][right.getLutIndex()])(result,left,right); \
    return result; }

defineBinaryFunc(pow,0);
defineBinaryFunc(tocomplex,Vells::VF_COMPLEX|Vells::VF_CHECKREAL);
defineBinaryFunc(posdiff,Vells::VF_REAL|Vells::VF_CHECKREAL);
defineBinaryFunc(atan2,Vells::VF_REAL|Vells::VF_CHECKREAL);

#undef defineUnaryFunc
#undef defineBinaryFunc

// declare versions of binary operators where the first argument is
// a scalar
#define defineBinaryOper(OPER,OPERNAME,dum) \
  inline Vells operator OPER (double left,const Vells &right) \
  { return Vells(left) OPER right; } \
  inline Vells operator OPER (const dcomplex &left,const Vells &right) \
  { return Vells(left) OPER right; } 

DoForAllBinaryOperators(defineBinaryOper,);

#undef defineBinaryOper
#endif

// provide inline specializations for the getArray/getScalar templates

template<> 
inline const LoMat_double & Vells::as (Type2Type<LoMat_double>) const
{ return getRealArray(); };
template<> 
inline const LoMat_dcomplex & Vells::as (Type2Type<LoMat_dcomplex>) const
{ return getComplexArray(); };
template<> 
inline LoMat_double & Vells::as (Type2Type<LoMat_double>) 
{ return getRealArray(); };
template<> 
inline LoMat_dcomplex & Vells::as (Type2Type<LoMat_dcomplex>) 
{ return getComplexArray(); };

template<> 
inline const double & Vells::as (Type2Type<double>) const
{ return getRealArray().data()[0]; };
template<> 
inline const dcomplex & Vells::as (Type2Type<dcomplex>) const
{ return getComplexArray().data()[0]; };
template<> 
inline double & Vells::as (Type2Type<double>) 
{ return getRealArray().data()[0]; };
template<> 
inline dcomplex & Vells::as (Type2Type<dcomplex>) 
{ return getComplexArray().data()[0]; };

template<>
inline const double * Vells::getStorage (Type2Type<double>) const
{ return realStorage(); }
template<>
inline const dcomplex * Vells::getStorage (Type2Type<dcomplex>) const
{ return complexStorage(); }
template<>
inline double * Vells::getStorage (Type2Type<double>) 
{ return realStorage(); }
template<>
inline dcomplex * Vells::getStorage (Type2Type<dcomplex>) 
{ return complexStorage(); }


inline std::ostream& operator<< (std::ostream& os, const Vells& vec)
  { vec.show (os); return os; }

} // namespace Meq

#endif
