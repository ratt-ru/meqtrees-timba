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
#include <MEQ/Axis.h>

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
                                  DoForAllUnaryFuncs4(Do,x)  \
                                  DoForAllUnaryFuncs5(Do,x)  
                                
// Unary group 1: defined for all Vells. Preserves real/complex
#define DoForAllUnaryFuncs1(Do,x) \
  Do(cos,x) Do(cosh,x) Do(exp,x) Do(log,x) Do(sin,x) Do(sinh,x) \
  Do(sqr,x) Do(sqrt,x) Do(tan,x) Do(tanh,x) \
  Do(pow2,x) Do(pow3,x) Do(pow4,x) Do(pow5,x) Do(pow6,x) Do(pow7,x) Do(pow8,x)
// Do(log10,x) commented out for now -- doesn't seem to have a complex version

// Unary group 2: defined for real Vells only, returns real
#define DoForAllUnaryFuncs2(Do,x) \
  Do(ceil,x) Do(floor,x) Do(acos,x) Do(asin,x) Do(atan,x) 

// Unary group 3: defined for all Vells, result is always real
#define DoForAllUnaryFuncs3(Do,x) \
  Do(abs,x) Do(fabs,x) Do(norm,x) Do(arg,x) Do(real,x) Do(imag,x) 
  
// Unary group 4: others functions requiring special treatment
#define DoForAllUnaryFuncs4(Do,x) \
  Do(conj,x) 
  
// Unary group 5: reduction functions not requiring a shape.
// These return a constant Vells (i.e. reduction along all axes)
// In the future, we'll support reduction along a designated axis
#define DoForAllUnaryFuncs5(Do,x) \
  Do(min,x) Do(max,x) Do(mean,x) 

// Unary reduction functions requiring a shape.
// Called as func(vells,shape).
// A shape argument is required because a Vells that is constant
// along some axis must be treated as N distinct points with the same value
// for the purposes of these functions.
// These return a constant Vells (i.e. reduction along all axes).
// In the future, we'll support reduction along a designated axis.
#define DoForAllUnaryFuncsWithShape(Do,x) \
  Do(sum,x) Do(product,x) Do(nelements,x)

// Binary functions
#define DoForAllBinaryFuncs(Do,x) \
  Do(posdiff,x) Do(tocomplex,x) Do(polar,x) Do(pow,x) Do(atan2,x)

namespace Meq {

// Conditionally include declarations for Vells math.
// Skipping these functions saves time/memory when compiling code that
// doesn't need them (such as the Meq service classes, and Vells itself).
// Note that the functions go into their own separate namespace. This keeps 
// the compiler from tripping over abs() and such.
#ifndef MEQVELLS_SKIP_FUNCTIONS
class Vells;
namespace VellsMath 
{
  #define declareUnaryFunc(FUNCNAME,x) \
    Vells FUNCNAME (const Vells &);
  DoForAllUnaryFuncs(declareUnaryFunc,);
  #define declareUnaryFuncWithShape(FUNCNAME,x) \
    Vells FUNCNAME (const Vells &,const Axis::Shape &);
  DoForAllUnaryFuncsWithShape(declareUnaryFuncWithShape,);
  #define declareBinaryFunc(FUNCNAME,x) \
    Vells FUNCNAME (const Vells &,const Vells &);
  DoForAllBinaryFuncs(declareBinaryFunc,);
  #undef declareUnaryFunc
  #undef declareUnaryFuncWithShape
  #undef declareBinaryFunc
};
#endif

// we provide two versions of each operation (real and complex)
const int VELLS_LUT_SIZE = 2;

//##ModelId=3F86886E0229
//##Documentation
// The Vells class contains a sampling (or integration) of a function over
// an arbitrary N-dimensional grid. 
class Vells : public SingularRefTarget
{
public:
  template<typename T,int N>
  struct DataType
  {
    typedef const blitz::Array<T,N> & ConstRetType;
    typedef blitz::Array<T,N> & RetType;
  };
  template<typename T>
  struct DataType<T,0>
  {
    typedef T ConstRetType;
    typedef T & RetType;
  };
    
    //##ModelId=400E530400F0
  typedef CountedRef<Vells> Ref;
  typedef Axis::Shape       Shape;
  typedef uint              Flags;
    
  //##ModelId=3F86887001D4
  //##Documentation
  // A null Vells with no data
  Vells();

  // Create a scalar Vells from a value. Default is temporary Vells.
  //##ModelId=3F86887001D5
  Vells (double value,bool temp=True);
  //##ModelId=3F86887001DC
  Vells (const dcomplex& value,bool temp=True);

  // Create a Vells of given shape.
  // If the init flag is true, the matrix is initialized to the given value.
  // Otherwise the value only indicates the type of matrix to be created.
  Vells (double, const Shape &shape, bool init=true);
  Vells (const dcomplex&, const Shape &shape, bool init=true);

  // Create a Vells from a DataArray pointer
  // Default is reference semantics (attaches ref to array), unless 
  // DMI::PRIVATIZE is specified, in which case the array is privatized.
  //##ModelId=3F8688700216
  explicit Vells (DataArray *,int flags = 0);
  //##ModelId=3F868870021C
  explicit Vells (const DataArray *,int flags = 0);
  //##ModelId=3F8688700223
  // creates from array ref. Ref is transferred
  explicit Vells (const DataArray::Ref::Xfer &ref);

  //##ModelId=3F868870022A
  // Copy constructor (reference semantics, unless DMI::PRIVATIZE is specified)
  Vells (const Vells& that,int flags = DMI::COPYREF);

    //##ModelId=3F8688700238
  ~Vells();

  // Assignment (reference semantics).
    //##ModelId=3F868870023B
  Vells& operator= (const Vells& other);

  // privatize function: assures of a private copy of the data
  virtual void privatize (int flags=0,int depth=0);
  
  // Clones the Vells -- assures of a private copy of the data
    //##ModelId=3F8688700249
  Vells clone () const
  { return Vells(*this,DMI::PRIVATIZE); }

  // is it a null vells?
    //##ModelId=3F8688700280
  bool isNull() const
  { return !num_elements_; }

  // Is the Vells a temporary object? The constructors above always
  // produce a non-temp Vells. Vells math (below) uses the private
  // constructors to produce temp Vells. Temp Vells allow for efficient 
  // re-use of storage.
    //##ModelId=400E53560092
  bool isTemp () const
  { return is_temp_; }
  
  bool isWritable () const
  { return !array_.valid() || array_.isWritable(); }
  
  //##ModelId=400E53560099
  void makeWritable () 
  { 
    if( array_.valid() && !array_.isWritable() )
    {
      array_.privatize(DMI::WRITE);
      storage_ = array_().getDataPtr();
    }
  }

  // changes the temp property
    //##ModelId=400E5356009D
  Vells & makeTemp (bool temp=true) 
  { is_temp_ = temp; return *this; }
  
    //##ModelId=400E535600A9
  Vells & makeNonTemp () 
  { is_temp_ = false; return *this; }
  
  const Shape & shape () const
  { return shape_; }
  
  const int shape (uint iaxis) const
  { return iaxis<shape_.size() ? shape_[iaxis] : 1; }
  
    //##ModelId=3F868870027E
  int nelements() const
  { return num_elements_; }
  
  bool isScalar () const
  { return nelements() == 1; }

    //##ModelId=3F868870028A
  bool isReal() const
  { return element_type_ == Tpdouble; }
  
    //##ModelId=400E535600B5
  bool isComplex() const
  { return element_type_ == Tpdcomplex; }
  
  TypeId elementType () const
  { return element_type_; }
  
  size_t elementSize () const
  { return element_size_; }
  
  int rank () const
  { return shape_.size(); }


  // Returns true if a sub-shape is compatible with the specified main shape.
  // A sub-shape is compatible if it does not have greater variability, i.e.:
  // 1. Its rank is not higher
  // 2. Its extent along each axis is either 1, or equal to the shape's extent
  static bool isCompatible (const Axis::Shape &subshape,const Axis::Shape &mainshape)
  {
    int rank = subshape.size();
    if( rank > int(mainshape.size()) )
      return false;
    for( int i=0; i<rank; i++ )
      if( subshape[i] != 1 && subshape[i] != mainshape[i] )
        return false;
    return true;
  }

  // Returns true if Vells is compatible with the specified mainshape.
  bool isCompatible (const Axis::Shape &mainshape) const
  { return isCompatible(shape(),mainshape); }
  
  // Two Vells shapes are congruent if the extents of each dimension are
  // congruent. Congruency of extents means both are equal, or either one is 1.
  // (An extent of 1 means that the value is constant along that axis).
  // Vells of congruent shape may have math operations performed on them.
  static bool isCongruent (const Axis::Shape &a,const Axis::Shape &b)
  {
    if( a.size() != b.size() )
      return False;
    for( uint i=0; i<a.size(); i++ )
      if( a[i] != b[i] && a[i]>1 && b[i]>1 )
        return False;
    return True;
  }

  // returns true if shape matches the one specified
  bool isCongruent (const Axis::Shape &shp) const
  { return isCongruent(shape(),shp); }

  // returns true if type/shape matches the one specified
  //##ModelId=400E535600E7
  bool isCongruent (TypeId type,const Axis::Shape &shp) const
  { return elementType() == type && isCongruent(shape(),shp); }

  // returns true if type/shape matches other Vells
  //##ModelId=400E535600CE
  bool isCongruent (const Vells &other) const
  { return isCongruent(other.elementType(),other.shape()); }

    
  const Thread::Mutex & mutex () const
  { return array_.valid() ? array_->mutex() : mutex_; }
    
  //##ModelId=400E53560109
  const DataArray & getDataArray () const
  { return getArrayRef(false).deref(); }
  
  //##ModelId=400E5356010C
  DataArray & getDataArrayWr ()
  { return getArrayRef(true).dewr(); }

  // Define templated getStorage<T>() function
  // Default version will produce a compile-time error; specializations
  // are provided below for double & dcomplex
  template<class T>
  const T* getStorage ( Type2Type<T> = Type2Type<T>() ) const
  { STATIC_CHECK(0,illegal_Vells_getStorage_type); }
  template<class T>
  T* getStorage ( Type2Type<T> = Type2Type<T>() )
  { STATIC_CHECK(0,illegal_Vells_getStorage_type); }
  
  // Define templated getArray<T>() function
  template<class T,int N>
  const blitz::Array<T,N> & getArray (Type2Type<T> =Type2Type<T>(),Int2Type<N> =Int2Type<N>()) const
  { return *static_cast<const blitz::Array<T,N>*>(
                getDataArray().getConstArrayPtr(typeIdOf(T),N)); }
  
  template<class T,int N>
  blitz::Array<T,N> & getArray (Type2Type<T> =Type2Type<T>(),Int2Type<N> =Int2Type<N>())
  { return *static_cast<blitz::Array<T,N>*>(
                getDataArrayWr().getArrayPtr(typeIdOf(T),N)); }
  
//   template<class T,int N>
//   blitz::Array<T,N> convertArray (Type2Type<T> =Type2Type<T>(),Int2Type<N> =Int2Type<N>())
//   { 
//     FailWhen(rank()>N,Debug::ssprintf("can't treat %d-D Vells as %d-D array",rank(),N));
//     if( rank() == N )
//       return getArray(Type2Type<T>(),Int2Type<N>());
//     else 
//     {
//       TinyVector<N> shp;
//       int i;
//       for( i=0; i<rank(); i++ )
//         shp[i] = shape_[i];
//       for( ; i<N; i++ )
//         shp[i] = 1;
//       return blitz::Array<T,N>(getStorage(Type2Type<T>()),neverDeleteData);
//     }
//   }; 

  template<class T>
  T getScalar (Type2Type<T> =Type2Type<T>()) const
  { 
    FailWhen(!isScalar(),"can't access this Meq::Vells as scalar"); 
    return *static_cast<const T *>(getStorage(Type2Type<T>())); 
  }
  template<class T>
  T & getScalar (Type2Type<T> =Type2Type<T>()) 
  { 
    FailWhen(!isScalar(),"can't access this Meq::Vells as scalar"); 
    return *static_cast<T*>(getStorage(Type2Type<T>())); 
  }
 
  
  // Define templated as<T,N>() functions, returning arrays or scalars (N=0)
  // Default version maps to getArray
  template<class T,int N>
  typename DataType<T,N>::ConstRetType as (Type2Type<T> =Type2Type<T>(),Int2Type<N> = Int2Type<N>()) const
  { return getArray(Type2Type<T>(),Int2Type<N>()); }
  
  template<class T,int N>
  typename DataType<T,N>::RetType as (Type2Type<T> =Type2Type<T>(),Int2Type<N> = Int2Type<N>()) 
  { return getArray(Type2Type<T>(),Int2Type<N>()); }

  // Provides access to array storage
    //##ModelId=3F8688700295
  const double* realStorage() const;
    //##ModelId=3F8688700298
  double* realStorage();
    //##ModelId=3F8688700299
  const dcomplex* complexStorage() const;
    //##ModelId=3F868870029B
  dcomplex* complexStorage();
  
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
  void clone (const Vells &other,int flags=0);
    
  // helper function for constructors
    //##ModelId=400E5356013E
  void initFromDataArray (const DataArray *parr,int flags=0);
  void initArrayPointers (const DataArray *parr,int flags=0);

  const DataArray::Ref & getArrayRef (bool write=false) const;
    
  //##ModelId=400E53560024
  DataArray::Ref  array_;
  
  DataArray::Ref  dataflags_;

  //##ModelId=3F86887001B3
  Shape   shape_;
  int     num_elements_;
  TypeId  element_type_;
  size_t  element_size_;
  //##ModelId=400E5356002F
  bool    is_temp_;
  void *  storage_;
  
  // temp storage for scalar Vells -- big enough for biggest scalar type
  char scalar_storage_[sizeof(dcomplex)];
  
  Thread::Mutex mutex_;
  
  
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
  Vells (const Vells &a,const Vells &b,int flags,
         int strides_a[],int strides_b[],const std::string &opname);

  // helper functions for these two constructors
    //##ModelId=400E5356019D
  bool tryReference (const Vells &other);

  void setSizeType (int flags,bool arg_is_complex);

  bool canApplyInPlace (const Vells &other,int strides[],const std::string &opname);

  static void computeStrides (Vells::Shape &shape,
                              int strides_a[],int strides_b[],
                              const Vells &a,const Vells &b,
                              const string &opname);
  
// returns LUT index for this Vells  
    //##ModelId=400E535601CB
  int getLutIndex () const
  { return isComplex() ? 1 : 0; }
  
  
public:
// pointer to function implementing an unary operation 
    //##ModelId=400E53040108
  typedef void (*UnaryOperPtr)(Vells &,const Vells &);
  typedef void (*UnaryWithShapeOperPtr)(Vells &,const Vells &,const Shape &);
// pointer to function implementing a binary operation 
    //##ModelId=400E53040116
  typedef void (*BinaryOperPtr)(Vells &out,const Vells &,const Vells &,
                                const int [], const int []);
// pointer to function implementing an unary in-place operation 
  typedef void (*InPlaceOperPtr)(Vells &out,const Vells &,const int []);
  
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
//          decide whether to duplicate or reuse the storage, and to init
//          strides) 
//       2. Calls the method in the OPERNAME_lut lookup table, using the
//          LUT index generated from the two Vells operands
#define declareBinaryOperator(OPER,OPERNAME,x) \
  private: static BinaryOperPtr binary_##OPERNAME##_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE];  \
  public: Vells operator OPER (const Vells &right) const \
          { int sta[Axis::MaxAxis],stb[Axis::MaxAxis]; \
            Vells result(*this,right,0,sta,stb,"operator "#OPER); \
            (*binary_##OPERNAME##_lut[getLutIndex()][right.getLutIndex()])(result,*this,right,sta,stb);  \
            return result; }
            
// Declares in-place (i.e. += and such) operator OPER (internally named OPERNAME)
// plus lookup table for implementations
// This just calls the method in the OPERNAME_lut lookup table, using the
// LUT index of this Vells object. The Vells itself is used as the result
// storage.
#define declareInPlaceOperator(OPER,OPERNAME,x) \
  private: static InPlaceOperPtr inplace_##OPERNAME##_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE];  \
  public: Vells & operator OPER##= (const Vells &right) \
          { int strides[Axis::MaxAxis]; \
            if( canApplyInPlace(right,strides,#OPERNAME) ) \
              (*inplace_##OPERNAME##_lut[getLutIndex()][right.getLutIndex()])(*this,right,strides); \
            else \
              (*this) = (*this) OPER right; \
            return *this; \
          }

// Defines lookup tables for implementations of unary math functions
#define declareUnaryFuncLut(FUNCNAME,x) \
  private: static UnaryOperPtr unifunc_##FUNCNAME##_lut[VELLS_LUT_SIZE];  

#define declareUnaryFuncLutWithShape(FUNCNAME,x) \
  private: static UnaryWithShapeOperPtr unifunc_##FUNCNAME##_lut[VELLS_LUT_SIZE];  
  
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
  DoForAllUnaryFuncsWithShape(declareUnaryFuncLutWithShape,);
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
  #define declareUnaryFuncWithShape(FUNCNAME,x) \
    public: friend Vells VellsMath::FUNCNAME (const Vells &,const Vells::Shape &);
  DoForAllUnaryFuncsWithShape(declareUnaryFuncWithShape,);
  
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
#define defineUnaryFuncWithShape(FUNCNAME,flags) \
  inline Vells VellsMath::FUNCNAME (const Vells &arg,const Vells::Shape &shape) \
  { Vells result(arg,flags,#FUNCNAME); \
    (*Vells::unifunc_##FUNCNAME##_lut[arg.getLutIndex()])(result,arg,shape); \
    return result; }

DoForAllUnaryFuncs1(defineUnaryFunc,0);
DoForAllUnaryFuncs2(defineUnaryFunc,Vells::VF_REAL|Vells::VF_CHECKREAL);
DoForAllUnaryFuncs3(defineUnaryFunc,Vells::VF_REAL);
// group 4: define explicitly
defineUnaryFunc(conj,0);
// group 5: reduction to scalar, no shape
defineUnaryFunc(min,Vells::VF_SCALAR|Vells::VF_REAL|Vells::VF_CHECKREAL);
defineUnaryFunc(max,Vells::VF_SCALAR|Vells::VF_REAL|Vells::VF_CHECKREAL);
defineUnaryFunc(mean,Vells::VF_SCALAR);
// group 6: reduction to scalar, with shape
defineUnaryFuncWithShape(sum,Vells::VF_SCALAR);
defineUnaryFuncWithShape(product,Vells::VF_SCALAR);
defineUnaryFuncWithShape(nelements,Vells::VF_SCALAR|Vells::VF_REAL);

#define defineBinaryFunc(FUNCNAME,flags) \
  inline Vells VellsMath::FUNCNAME (const Vells &left,const Vells &right) \
  { int sta[Axis::MaxAxis],stb[Axis::MaxAxis]; \
    Vells result(left,right,flags,sta,stb,#FUNCNAME); \
    (*Vells::binfunc_##FUNCNAME##_lut[left.getLutIndex()][right.getLutIndex()])(result,left,right,sta,stb);  \
    return result; }
defineBinaryFunc(pow,0);
defineBinaryFunc(tocomplex,Vells::VF_COMPLEX|Vells::VF_CHECKREAL);
defineBinaryFunc(polar,Vells::VF_COMPLEX|Vells::VF_CHECKREAL);
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

// provide inline specializations for the getStorage templates
template<>
inline const double * Vells::getStorage (Type2Type<double>) const
{ 
  FailWhen(element_type_ != Tpdouble,"mismatch in Vells type");
  return static_cast<const double *>(storage_);
}

template<>
inline const dcomplex * Vells::getStorage (Type2Type<dcomplex>) const
{ 
  FailWhen(element_type_ != Tpdcomplex,"mismatch in Vells type");
  return static_cast<const dcomplex *>(storage_);
}

template<>
inline double * Vells::getStorage (Type2Type<double>) 
{ 
  FailWhen(element_type_ != Tpdouble,"mismatch in Vells type");
  makeWritable();
  return static_cast<double *>(storage_);
}

template<>
inline dcomplex * Vells::getStorage (Type2Type<dcomplex>) 
{ 
  FailWhen(element_type_ != Tpdcomplex,"mismatch in Vells type");
  makeWritable();
  return static_cast<dcomplex *>(storage_);
}

  //##ModelId=3F8688700295
inline const double* Vells::realStorage() const
{ return getStorage<double>(); }
  //##ModelId=3F8688700298
inline double* Vells::realStorage()
{ return getStorage<double>(); }
  //##ModelId=3F8688700299
inline const dcomplex* Vells::complexStorage() const
{ return getStorage<dcomplex>(); }
  //##ModelId=3F868870029B
inline dcomplex* Vells::complexStorage()
{ return getStorage<dcomplex>(); }

inline std::ostream& operator<< (std::ostream& os, const Vells& vec)
  { vec.show (os); return os; }

} // namespace Meq

#endif
