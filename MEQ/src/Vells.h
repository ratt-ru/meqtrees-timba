//# Vells.h: Values for Meq expressions
//#
//# Copyright (C) 2002-2007
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# and The MeqTree Foundation
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

#include <DMI/NumArray.h>
#include <MEQ/Meq.h>
#include <MEQ/Axis.h>

#pragma type #Meq::Vells

// This provides a list of operators and functions defined over Vells objects
// All of these will only work with double or dcomplex Vells, and throw
// an exception on any other type.

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
  Do(cos,x) Do(cosh,x) Do(exp,x) Do(log,x) Do(sin,x) Do(sinh,x) \
  Do(sqr,x) Do(sqrt,x) Do(tan,x) Do(tanh,x) \
  Do(pow2,x) Do(pow3,x) Do(pow4,x) Do(pow5,x) Do(pow6,x) Do(pow7,x) Do(pow8,x)
// Do(log10,x) commented out for now -- doesn't seem to have a complex version

// Unary group 2: defined for real Vells only, returns real
#define DoForAllUnaryFuncs2(Do,x) \
  Do(ceil,x) Do(floor,x) \
  Do(acos,x) Do(asin,x) Do(atan,x)

// Unary group 3: defined for all Vells, result is always real
#define DoForAllUnaryFuncs3(Do,x) \
  Do(abs,x) Do(fabs,x) Do(norm,x) Do(arg,x) Do(real,x) Do(imag,x)

// Unary group 4: others functions requiring special treatment
#define DoForAllUnaryFuncs4(Do,x) \
  Do(conj,x)

// Unary reduction functions not requiring a shape.
// Called as func(vells[,flagmask]).
// These return a constant Vells (i.e. reduction along all axes)
// In the future, we'll support reduction along a designated axis
#define DoForAllUnaryRdFuncs(Do,x) \
  Do(min,x) Do(max,x) Do(mean,x)

// Unary reduction functions requiring a shape.
// Called as func(vells,shape[,flagmask]).
// A shape argument is required because a Vells that is constant
// along some axis must be treated as N distinct points with the same value
// for the purposes of these functions.
// These return a constant Vells (i.e. reduction along all axes).
// In the future, we'll support reduction along a designated axis.
#define DoForAllUnaryRdFuncsWS(Do,x) \
  Do(sum,x) Do(product,x) Do(nelements,x)

// Binary functions
#define DoForAllBinaryFuncs(Do,x) \
  Do(posdiff,x) Do(tocomplex,x) Do(polar,x) Do(pow,x) Do(atan2,x) \
  Do(fmod,x) Do(remainder,x)

// Binary functions using flags
// Called as func(a,b,flagmask_a,flagmask_b)
#define DoForAllBinaryFuncsWF(Do,x) \
  Do(min,x) Do(max,x)

// Finally, VellsFlagType Vells define bitwise logical operators:
// unary  ~ (NOT)
#define DoForAllUnaryFlagOperators(Do,x) \
          Do(~,NOT,x)
// Binary and in-place | & and ^ (OR AND XOR). The second operand may be a
// Vells or a VellsFlagType scalar.
#define DoForAllBinaryFlagOperators(Do,x) \
          Do(|,OR,x) Do(&,AND,x) Do(^,XOR,x)
#define DoForAllInPlaceFlagOperators(Do,x) \
          Do(|,OR1,x) Do(&,AND1,x) Do(^,XOR1,x)



namespace Meq
{
using namespace DMI;
using namespace DebugMeq;


// dataflag type
typedef int VellsFlagType;
const VellsFlagType VellsFullFlagMask = 0xFFFFFFFF;
const TypeId VellsFlagTypeId = typeIdOf(VellsFlagType);


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
  #define declareUnaryRdFunc(FUNCNAME,x) \
    Vells FUNCNAME (const Vells &,VellsFlagType flagmask=VellsFullFlagMask);
  DoForAllUnaryRdFuncs(declareUnaryRdFunc,);
  #define declareUnaryRdFuncWS(FUNCNAME,x) \
    Vells FUNCNAME (const Vells &,const Axis::Shape &,VellsFlagType flagmask=VellsFullFlagMask);
  DoForAllUnaryRdFuncsWS(declareUnaryRdFuncWS,);
  #define declareBinaryFunc(FUNCNAME,x) \
    Vells FUNCNAME (const Vells &,const Vells &);
  DoForAllBinaryFuncs(declareBinaryFunc,);
  #define declareBinaryFuncWF(FUNCNAME,x) \
    Vells FUNCNAME (const Vells &,const Vells &,\
      VellsFlagType flagmask1=VellsFullFlagMask,VellsFlagType flagmask2=VellsFullFlagMask);
  DoForAllBinaryFuncsWF(declareBinaryFuncWF,);
  #undef declareUnaryFunc
  #undef declareUnaryRdFunc
  #undef declareUnaryRdFuncWS
  #undef declareBinaryFunc
  #undef declareBinaryFuncWF

  typedef Vells (*UnaryRdFunc)(const Vells &,VellsFlagType);
  typedef Vells (*UnaryRdFuncWS)(const Vells &,const LoShape &,VellsFlagType);
};
#endif

// we provide two versions of each operation (real and complex)
const int VELLS_LUT_SIZE = 2;

namespace VellsTraits
{
  // this is a traits-type structure that defines parameters and return types
  template<typename T,int N>
  class DataType
  {
    public:
        typedef const typename NumArray::Traits<T,N>::Array & ParamType;
        typedef const typename NumArray::Traits<T,N>::Array & ConstRetType;
        typedef typename NumArray::Traits<T,N>::Array & RetType;
  };
  template<typename T>
  class DataType<T,0>
  {
    public:
        typedef T ParamType;
        typedef T ConstRetType;
        typedef T & RetType;
  };
  template<>
  class DataType<dcomplex,0>
  {
    public:
        typedef const dcomplex & ParamType;
        typedef dcomplex ConstRetType;
        typedef dcomplex & RetType;
  };
};

//##ModelId=3F86886E0229
//##Documentation
// The Vells class contains a sampling (or integration) of a function over
// an arbitrary N-dimensional grid.
// It is essentially a specialization of DMI::NumArray.
class Vells : public DMI::NumArray
{
private:
  template<class T>
  inline void init_scalar (T value)
  { *static_cast<T*>(const_cast<void*>(getConstDataPtr())) = value; }

  template<class T>
  inline void init_array (T value)
  { T *ptr = static_cast<T*>(const_cast<void*>(getConstDataPtr())),
      *end = ptr + nelements();
    for( ; ptr != end; ptr++ )
     *ptr = value;
  }

public:
  //##ModelId=400E530400F0
  typedef CountedRef<Vells> Ref;
  typedef Axis::Shape       Shape;
  typedef int Strides[Axis::MaxAxis];

  static Strides null_strides;

  // deine some constant Vells
  static const Vells & Null  ()   { _init_static_data(); return *pNull_; }
  static const Vells & Unity ()   { _init_static_data(); return *pUnity_; }

  //##ModelId=3F86887001D4
  //##Documentation
  // Default constructor creates a null Vells (double 0.0)
  Vells();

  // Creates a scalar Vells
  inline Vells(double value)
  : NumArray(Tpdouble,LoShape(1),DMI::NOZERO,TpMeqVells)
  { init_scalar(value); }

  inline Vells(const dcomplex &value)
  : NumArray(Tpdcomplex,LoShape(1),DMI::NOZERO,TpMeqVells)
  { init_scalar(value); }

  // Create a Vells of given shape.
  // If the init flag is true, the Vells is initialized to the given value.
  // Otherwise value only determines type, and Vells is initialized with zeroes.
  // NB: the argument type really ought to be VellsTraits::DataType<T,0>::ParamType
  // and not just T, but stupid compiler won't recognize it for some reason...
  inline Vells(double value,const Shape &shape,bool init=true)
  : NumArray(Tpdouble,shape,DMI::NOZERO,TpMeqVells)
  {
    if( init )
      init_array(value);
  }
  inline Vells(const dcomplex &value,const Shape &shape,bool init=true)
  : NumArray(Tpdcomplex,shape,DMI::NOZERO,TpMeqVells)
  {
    if( init )
      init_array(value);
  }

  // Create a flag Vells of the given shape
  // Note that order of constructor arguments is reversed here to avoid
  // confusion with other constructors: otherwise it's too easy to
  // unintentionally create a flag vells when a normal one was intended
  // simply by using Vells(0,shape).
  inline Vells(const Shape &shape,VellsFlagType value,bool init=true)
  : NumArray(VellsFlagTypeId,shape,DMI::NOZERO,TpMeqVells)
  {
    if( init )
      init_array(value);
  }

  // create Vells of the same type as 'other', but with a different
  // shape. If init=true, fills with 0s
  inline Vells (const Vells &other,const Shape &shape,bool init=true)
  : NumArray(other.elementType(),shape,init?0:DMI::NOZERO,TpMeqVells)
  {
  }

  //##ModelId=3F868870022A
  // Copy constructor (reference semantics, unless DMI::DEEP or depth>0 is
  // specified). A Vells may be created from a NumArray of a compatible type
  Vells (const DMI::NumArray &other,int flags=0,int depth=0);
  Vells (const Vells &other,int flags=0,int depth=0);

  // Construct from array
  template<class T,int N>
  Vells (const blitz::Array<T,N> &arr)
  : DMI::NumArray(arr,TpMeqVells)
  { validateContent(false); }

    //##ModelId=3F8688700238
  ~Vells();

  // Assignment (reference semantics).
    //##ModelId=3F868870023B
  Vells& operator= (const Vells& other);

      //##ModelId=400E530403C1
  virtual TypeId objectType () const
  { return TpMeqVells; }

  // implement standard clone method via copy constructor
    //##ModelId=400E530403C5
  virtual CountedRefTarget* clone (int flags=0,int depth=0) const
  { return new Vells(*this,flags,depth); }

  // validate array contents and setup shortcuts to them. This is called
  // automatically whenever a Vells object is made from a DMI::NumArray
    //##ModelId=400E530403DB
  virtual void validateContent (bool recursive);

    //##ModelId=3F8688700280
  // is it a null vells (representing 0)?
  bool isNull () const
  { return !NumArray::valid() || ( isScalar() &&
    ( isReal() ? as<double>() == double(0) : as<dcomplex>() == make_dcomplex(0,0) ) ); }

  bool isUnity () const
  { return isScalar() &&
    ( isReal() ? as<double>() == double(1) : as<dcomplex>() == make_dcomplex(1,0) ); }

  // does this Vells have flags attached?
  bool hasDataFlags () const
  { return dataflags_.valid(); }

  // returns flags of this Vells
  const Vells & dataFlags () const
  { return *dataflags_; }

  // sets the dataflags of a Vells
  void setDataFlags (const Vells::Ref &flags)
  { dataflags_ = flags; }
  void setDataFlags (const Vells &flags)
  { dataflags_.attach(flags); }
  void setDataFlags (const Vells *flags)
  { dataflags_.attach(flags); }

  void clearDataFlags ()
  { dataflags_.detach(); }

  static int extent (const Vells::Shape &shp,uint idim)
  { return idim < shp.size() ? shp[idim] : 1; }

  int extent (uint idim) const
  { return extent(shape(),idim); }

    //##ModelId=3F868870027E
  int nelements() const
  { return NumArray::size(); }

  bool isScalar () const
  { return nelements() == 1; }

    //##ModelId=3F868870028A
  bool isReal() const
  { return elementType() == Tpdouble; }

    //##ModelId=400E535600B5
  bool isComplex() const
  { return elementType() == Tpdcomplex; }

  bool isFlags() const
  { return elementType() == VellsFlagTypeId; }

  // Returns true if a sub-shape is compatible with the specified main shape.
  // A sub-shape is compatible if it does not have greater variability, i.e.:
  // 1. Its rank is not higher
  // 2. Its extent along each axis is either 1, or equal to the shape's extent
  static bool isCompatible (const Axis::Shape &subshape,const Axis::Shape &mainshape)
  {
    int rank = subshape.size();
   /* if( rank > int(mainshape.size()) )
      return false; */
    for( int i=0; i<int(mainshape.size()) && i<rank; i++ )
      if(  subshape[i] != 1 && subshape[i] != mainshape[i] )
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
      return false;
    for( uint i=0; i<a.size(); i++ )
      if( a[i] != b[i] && a[i]>1 && b[i]>1 )
        return false;
    return true;
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

  // Define templated getStorage<T>() function
  // Default version will produce a compile-time error; specializations
  // are provided below for double & dcomplex
  template<class T>
  const T* getStorage ( Type2Type<T> = Type2Type<T>() ) const
  {
    const TypeId tid = typeIdOf(T);
    FailWhen(elementType()!=tid,"can't access "+elementType().toString()+" Vells as "+tid.toString());
    return static_cast<const T*>(NumArray::getConstDataPtr());
  }
  template<class T>
  T* getStorage ( Type2Type<T> = Type2Type<T>() )
  {
    const TypeId tid = typeIdOf(T);
    FailWhen(elementType()!=tid,"can't access "+elementType().toString()+" Vells as "+tid.toString());
    return static_cast<T*>(NumArray::getDataPtr());
  }

  // begin<T> is same as getStorage()
  // end<T> is begin<T> + nelements()
  template<class T>
  const T* begin ( Type2Type<T> = Type2Type<T>() ) const
  { return getStorage(Type2Type<T>()); }
  template<class T>
  T* begin ( Type2Type<T> = Type2Type<T>() )
  { return getStorage(Type2Type<T>()); }
  template<class T>
  const T* end ( Type2Type<T> = Type2Type<T>() ) const
  { return getStorage(Type2Type<T>()) + nelements(); }
  template<class T>
  T* end ( Type2Type<T> = Type2Type<T>() )
  { return getStorage(Type2Type<T>()) + nelements(); }

  // begin_flags() and end_flags() return pointer to flags, or to nil flag
  // if there are none
  const VellsFlagType * beginFlags () const
  { return hasDataFlags() ? dataFlags().begin<VellsFlagType>() : &null_flag_; }

  const VellsFlagType * endFlags () const
  { return hasDataFlags() ? dataFlags().end<VellsFlagType>() : &(null_flag_)+1; }

  int nflags () const
  { return hasDataFlags() ? dataFlags().nelements() : 1; }

  int flagRank () const
  { return hasDataFlags() ? dataFlags().rank() : 1; }

  const Shape & flagShape () const
  { return hasDataFlags() ? dataFlags().shape() : null_flag_shape_; }

  // whereEq(value,out_eq,out_ne)
  // Compares all values in the Vells to value, creates (in out)
  // a flag Vells composed of out_eq where values match, and out_ne where
  // they mismatch.
  // Returns 1 if everything matched,  -1 if nothing matched, or 0 otherwise
  template<class T>
  int whereEq (Vells &out,T value,VellsFlagType out_eq=1,VellsFlagType out_ne=0)
  {
    // init a flag vells with out_ne
    out = Vells(shape(),out_ne,true);
    const T * ptr = begin<T>();
    VellsFlagType * pout = out.begin<VellsFlagType>();
    bool matched = false;
    bool mismatched = false;
    for( ; ptr != end<T>(); ptr++,pout++ )
    {
      if( *ptr == value )
      {
        *pout = out_eq;
        matched = true;
      }
      else
        mismatched = true;
    }
    if( matched && !mismatched )
      return 1;
    else if( mismatched && !matched )
      return -1;
    else
      return 0;
  }

// NumArray already defines templated getArray<T>() and getConstArray<T>() functions
//   template<class T,int N>
//   const typename Traits<T,N>::Array & getArray (Type2Type<T> =Type2Type<T>(),Int2Type<N> =Int2Type<N>()) const
//   { return NumArray::getConstArray(Type2Type<T>(),Int2Type<N>()); }
//   template<class T,int N>
//   typename Traits<T,N> & getArray (Type2Type<T> =Type2Type<T>(),Int2Type<N> =Int2Type<N>())
//   { return *static_cast<typename Traits<T,N>::Array*>(
//                 NumArray::getArrayPtr(typeIdOf(T),N)); }

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
  typename VellsTraits::DataType<T,N>::ConstRetType as (Type2Type<T> =Type2Type<T>(),Int2Type<N> = Int2Type<N>()) const
  { return getArray(Type2Type<T>(),Int2Type<N>()); }

  template<class T,int N>
  typename VellsTraits::DataType<T,N>::RetType as (Type2Type<T> =Type2Type<T>(),Int2Type<N> = Int2Type<N>())
  { return getArray(Type2Type<T>(),Int2Type<N>()); }

  template<class T>
  T as (Type2Type<T> =Type2Type<T>()) const
  { return getScalar(Type2Type<T>()); }

  template<class T>
  T & as (Type2Type<T> =Type2Type<T>())
  { return getScalar(Type2Type<T>()); }

  // Provides access to array storage
    //##ModelId=3F8688700295
  const double* realStorage() const
  { return getStorage<double>(); }
    //##ModelId=3F8688700298
  double* realStorage()
  { return getStorage<double>(); }
    //##ModelId=3F8688700299
  const dcomplex* complexStorage() const
  { return getStorage<dcomplex>(); }
    //##ModelId=3F868870029B
  dcomplex* complexStorage()
  { return getStorage<dcomplex>(); }

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

  // =========================== Iterator and stride support
  // helper function to compute the stride along each axis, given a Vells shape
  // returns the total number of elements corresponding to shape
  static int computeStrides (Vells::Strides &strides,const Vells::Shape &shape);

  // same function, but returns the stride for this Vells
  int computeStrides (Vells::Strides &strides)
  { return computeStrides(strides,shape()); }

  // helper funtion to compute output shape and data strides, given two
  // input shapes. Used throughout Vells math
  static void computeStrides (Vells::Shape &outshape,
                              Strides strides[],
                              int nshapes,const Vells::Shape * shapes[],
                              const string &opname = "computeStrides");

  // convenience version for two Vells arguments
  static void computeStrides (Vells::Shape &shape,
                              Strides strides[2],
                              const Vells::Shape &a,const Vells::Shape &b,
                              const string &opname = "computeStrides")
  {
    const Vells::Shape * shapes[2] = { &a,&b };
    computeStrides(shape,strides,2,shapes,opname);
  }

  // convenience version for two Vells arguments with optional flags
  // strides filled as follows: 0/1 Vells a/b, 2/3 flags a/b
  static void computeStrides (Vells::Shape &shape,
                              Strides strides[4],
                              const Vells &a,const Vells &b,
                              const string &opname = "computeStrides")
  {
    const Vells::Shape * shapes[4] = { &a.shape(),&b.shape(),&a.flagShape(),&b.flagShape() };
    computeStrides(shape,strides,4,shapes,opname);
  }

  // === Iterator
  // Helper class implementing iteration over a strided vells
  template<class T>
  class ConstStridedIterator
  {
    protected:
      const T   *ptr;
      const int *strides;

    public:
      ConstStridedIterator ()
      {}

      ConstStridedIterator (const T * p,const Strides &str)
      { init(p,str); }

      ConstStridedIterator (const Vells &vells,const Strides &str)
      { init(vells,str); }

      ConstStridedIterator (const T & value)
      { init(value); }

      void init (const T * p,const Strides &str)
      { ptr = p; strides = str; }

      void init (const Meq::Vells &vells,const Strides &str)
      { ptr = vells.begin(Type2Type<T>()); strides = str; }

      // a trivial iterator always returning the same value
      void init (const T &value)
      { ptr = &value; strides = Vells::null_strides; }

      const T & operator * () const
      { return *ptr; }

      // advances to next element in the specified number of dimensions
      // (i.e. if ndim==3, then advances along dimensions 1,2 and 3)
      void incr (int ndim=1)
      {
        for( int i=0; i<ndim; i++ )
          ptr += strides[i];
      }
  };

  // Helper class implementing iteration over a strided flag vells
  class ConstStridedFlagIterator : public ConstStridedIterator<VellsFlagType>
  {
    public:
      ConstStridedFlagIterator (const Vells &vells,const Strides &str)
      {
        if( vells.hasDataFlags() )
          init(vells.dataFlags(),str);
        else
        {
          static VellsFlagType zero = 0;
          init(zero);
        }
      }

  };

  // Helper class implementing iteration over an N-dimensional shape
  class DimCounter
  {
    protected:
      int   rank_;
      int   shape_[Axis::MaxAxis];
      int   counter_[Axis::MaxAxis];
      bool  valid_;

    public:
      void init (const Vells::Shape &shape0)
      // note that dimensions in 'shape' are reversed for convenience,
      // since the it's the last dimension of the Vells array that iterates
      // fastest. The strides returned by computeStrides() above are also
      // reversed in this manner. The shape() and counter() accessors
      // below reverse dimensions yet again.
      {
        valid_ = true;
        rank_ = shape0.size();
        int j = rank_ - 1;
        for( int i=0; i<rank_; i++,j-- )
          shape_[i] = shape0[j];
        memset(counter_,0,sizeof(int)*rank_);
      }

      DimCounter ()
      : rank_(0),valid_(false)
      {}

      DimCounter (const Meq::Vells &vells)
      { init(vells.shape()); }

      DimCounter (const Meq::Vells::Shape &shape)
      { init(shape); }

      bool valid () const
      { return valid_; }

      int rank () const
      { return rank_; }

      int shape (int idim) const
      { idim = rank_ - idim - 1; return idim>=0 ? shape_[idim] : 0; }

      int counter (int idim) const
      { idim = rank_ - idim - 1; return idim>=0 ? counter_[idim] : 0; }

      // increments counter. Returns number of dimensions incremented
      // (i.e. 1 most of the time, when only the last dimension is being
      // incremented, 2 when the second-to-last is incremented as well, etc.),
      // or 0 when finished
      int incr ()
      {
        int idim = 0;
        while( idim<rank_ && ++counter_[idim] >= shape_[idim] )
        {
          counter_[idim] = 0;
          ++idim;
        }
        if( idim >= rank_ )
          return valid_ = 0;
        return idim+1;
      }
  };

  // Helper function to merge vells flags using copy-on-write
  // Executes flags0 |= flags1 & fm
  // If flags0 is invalid, attaches new flags.
  static void mergeFlags (Vells::Ref &flags0,const Vells &flags1,VellsFlagType fm);

// internal initialization of static Vells data
// (to be done only once, preferrably on startup)
  static int _init_static_data ()
  {
    if( !_static_init_done )
      _init_static_impl();
    return 1;
  }

private:
  Vells::Ref  dataflags_;

  static bool _static_init_done;
  static void _init_static_impl ();

  static const Vells *pNull_;
  static const Vells *pUnity_;

  static VellsFlagType null_flag_;
  static Shape null_flag_shape_;

  //##ModelId=400E5356002F
//  void *  storage_;

  // temp storage for scalar Vells -- big enough for biggest scalar type
//  char scalar_storage_[sizeof(dcomplex)];

  // OK, now it gets hairy. Implement math on Vells
  // The following flags may be supplied to the constructors below:
    //##ModelId=400E530400FC
  typedef enum {
    VF_REAL         = 0x01, // result is forced real
    VF_COMPLEX      = 0x02, // result is forced complex
    VF_SCALAR       = 0x04, // result is forced scalar
    VF_CHECKREAL    = 0x08, // operand(s) must be real
    VF_CHECKCOMPLEX = 0x10, // operand(s) must be complex
    VF_FLAGTYPE     = 0x20, // result and operand(s) are VellsFlagType
    VF_FLAG_STRIDES = 0x40, // compute strides for dataflags too
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
         Strides strides[],const std::string &opname);

  // helper functions for these two constructors
    //##ModelId=400E5356019D
  bool tryReference (const Vells &other);

  static TypeId getResultType (int flags,bool arg_is_complex);

  bool canApplyInPlace (const Vells &other,Strides &strides,const std::string &opname);

  //##ModelId=400E535601CB
  int getLutIndex () const
  {
    if( isComplex() )
      return 1;
    else if( isReal() )
      return 0;
    else
      Throw("can't apply math operation to Vells of type "+elementType().toString());
  }


public:
// pointer to function implementing an unary operation
    //##ModelId=400E53040108
  typedef void (*UnaryOperPtr)(Vells &,const Vells &);
  typedef void (*UnaryRdFuncPtr)(Vells &,const Vells &,VellsFlagType);
  typedef void (*UnaryRdFuncWSPtr)(Vells &,const Vells &,const Shape &,VellsFlagType);
// pointer to function implementing a binary operation
    //##ModelId=400E53040116
  typedef void (*BinaryOperPtr)(Vells &out,const Vells &,const Vells &,
                                const Strides [2]);
  typedef void (*BinaryFuncWFPtr)(Vells &out,const Vells &,const Vells &,
                                  VellsFlagType,VellsFlagType,const Strides [4]);
// pointer to function implementing an unary in-place operation
  typedef void (*InPlaceOperPtr)(Vells &out,const Vells &,const Strides &);

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

// unary flag operators implemented explicitly (no LUT needed)
#define declareUnaryFlagOperator(OPER,OPERNAME,x) \
  public: Vells operator OPER () const;

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
          { Strides strides[2]; \
            Vells result(*this,right,0,strides,"operator "#OPER); \
            (*binary_##OPERNAME##_lut[getLutIndex()][right.getLutIndex()])(result,*this,right,strides);  \
            return result; }
//  DoForAllBinaryOperators(declareBinaryOperator,);
// declare binary operators explicitly for efficiency
// addition and multiplication by zero/unity shows up so often that it
// makes sense to check for it explicitly

// binary addition
  private: static BinaryOperPtr binary_ADD_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE];
  public: Vells operator + (const Vells &right) const
          {
            if( isNull() )
              return right;
            if( right.isNull() )
              return *this;
            Strides strides[2];
            Vells result(*this,right,0,strides,"operator +");
            (*binary_ADD_lut[getLutIndex()][right.getLutIndex()])(result,*this,right,strides);
            return result;
          }
  private: static BinaryOperPtr binary_MUL_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE];
  public: Vells operator * (const Vells &right) const
          {
            if( isNull() || right.isNull() )
              return Vells();
            if( isUnity() )
              return right;
            if( right.isUnity() )
              return *this;
            Strides strides[2];
            Vells result(*this,right,0,strides,"operator *");
            (*binary_MUL_lut[getLutIndex()][right.getLutIndex()])(result,*this,right,strides);
            return result;
          }
  // subtraction/multiplication infrequent, no point optimizing
  declareBinaryOperator(-,SUB,);
  declareBinaryOperator(/,DIV,);

// Declares in-place (i.e. += and such) operator OPER (internally named OPERNAME)
// plus lookup table for implementations
// This just calls the method in the OPERNAME_lut lookup table, using the
// LUT index of this Vells object. The Vells itself is used as the result
// storage.
#define declareInPlaceOperator(OPER,OPERNAME,x) \
  private: static InPlaceOperPtr inplace_##OPERNAME##_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE];  \
  public: Vells & operator OPER##= (const Vells &right) \
          { Strides strides; \
            if( canApplyInPlace(right,strides,#OPERNAME) ) \
              (*inplace_##OPERNAME##_lut[getLutIndex()][right.getLutIndex()])(*this,right,strides); \
            else \
              (*this) = (*this) OPER right; \
            return *this; \
          }
//  DoForAllInPlaceOperators(declareInPlaceOperator,);
// declare binary operators explicitly for efficiency
// addition and multiplication by zero/unity shows up so often that it
// makes sense to check for it explicitly
  private: static InPlaceOperPtr inplace_ADD1_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE];
  public: Vells & operator += (const Vells &right)
          {
            if( right.isNull() )
              return *this;
            if( isNull() )
              return (*this) = right;
            Strides strides;
            if( canApplyInPlace(right,strides,"ADD1") )
              (*inplace_ADD1_lut[getLutIndex()][right.getLutIndex()])(*this,right,strides);
            else
              (*this) = (*this) + right;
            return *this;
          }
  private: static InPlaceOperPtr inplace_MUL1_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE];
  public: Vells & operator *= (const Vells &right)
          {
            if( isNull() || right.isNull() )
              return (*this) = Vells();
            if( isUnity() )
              return (*this) = right;
            if( right.isUnity() )
              return *this;
            Strides strides;
            if( canApplyInPlace(right,strides,"ADD1") )
              (*inplace_MUL1_lut[getLutIndex()][right.getLutIndex()])(*this,right,strides);
            else
              (*this) = (*this) * right;
            return *this;
          }
  declareInPlaceOperator(-,SUB1,);
  declareInPlaceOperator(/,DIV1,);

// in-place flag operators implemented explicitly (no LUT needed)
#define declareInPlaceFlagOperator(OPER,OPERNAME,x) \
  public: Vells & operator OPER##= (const Vells &right); \
          Vells & operator OPER##= (VellsFlagType right);

// binary flag operators implemented explicitly (no LUT needed)
#define declareBinaryFlagOperator(OPER,OPERNAME,x) \
  public: Vells operator OPER (const Vells &right) const; \
          Vells operator OPER (VellsFlagType right) const;

// Defines lookup tables for implementations of unary math functions
#define declareUnaryFuncLut(FUNCNAME,x) \
  private: static UnaryOperPtr unifunc_##FUNCNAME##_lut[VELLS_LUT_SIZE];

#define declareUnaryRdFuncLut(FUNCNAME,x) \
  private: static UnaryRdFuncPtr unifunc_##FUNCNAME##_lut[VELLS_LUT_SIZE];

#define declareUnaryRdFuncWSLut(FUNCNAME,x) \
  private: static UnaryRdFuncWSPtr unifunc_##FUNCNAME##_lut[VELLS_LUT_SIZE];

// Declares binary function FUNCNAME
// Defines lookup tables for implementations of binary math functions
#define declareBinaryFuncLut(FUNCNAME,x) \
  private: static BinaryOperPtr binfunc_##FUNCNAME##_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE];
#define declareBinaryFuncWFLut(FUNCNAME,x) \
  private: static BinaryFuncWFPtr binfunc_##FUNCNAME##_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE];

// insert all declarations using the macros above
    //##ModelId=400E535601D0
  DoForAllUnaryOperators(declareUnaryOperator,);
  DoForAllUnaryFlagOperators(declareUnaryFlagOperator,);
    //##ModelId=400E535601D9
  DoForAllInPlaceFlagOperators(declareInPlaceFlagOperator,);
    //##ModelId=400E535601E3
  DoForAllBinaryFlagOperators(declareBinaryFlagOperator,);
    //##ModelId=400E535601EC
  DoForAllUnaryFuncs(declareUnaryFuncLut,);
  DoForAllUnaryRdFuncs(declareUnaryRdFuncLut,);
  DoForAllUnaryRdFuncsWS(declareUnaryRdFuncWSLut,);
    //##ModelId=400E535601F6
  DoForAllBinaryFuncs(declareBinaryFuncLut,);
  DoForAllBinaryFuncsWF(declareBinaryFuncWFLut,);

#undef declareUnaryOperator
#undef declareUnaryFlagOperator
#undef declareInPlaceOperator
#undef declareInPlaceFlagOperator
#undef declareBinaryOperator
#undef declareBinaryFlagOperator
#undef declareUnaryFuncLut
#undef declareBinaryFuncLut
#undef declareBinaryFuncWFLut

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
  #define declareUnaryRdFunc(FUNCNAME,x) \
    public: friend Vells VellsMath::FUNCNAME (const Vells &,VellsFlagType);
  DoForAllUnaryRdFuncs(declareUnaryRdFunc,);
  #define declareUnaryRdFuncWS(FUNCNAME,x) \
    public: friend Vells VellsMath::FUNCNAME (const Vells &,const Vells::Shape &,VellsFlagType);
  DoForAllUnaryRdFuncsWS(declareUnaryRdFuncWS,);

  #define declareBinaryFunc(FUNCNAME,x) \
    public: friend Vells VellsMath::FUNCNAME (const Vells &,const Vells &);
    //##ModelId=400E5356020A
  DoForAllBinaryFuncs(declareBinaryFunc,);

  #define declareBinaryFuncWF(FUNCNAME,x) \
    public: friend Vells VellsMath::FUNCNAME (const Vells &,const Vells &,VellsFlagType,VellsFlagType);
    //##ModelId=400E5356020A
  DoForAllBinaryFuncsWF(declareBinaryFuncWF,);

  #undef declareUnaryFunc
  #undef declareUnaryRdFunc
  #undef declareUnaryRdFuncWS
  #undef declareBinaryFunc
  #undef declareBinaryFuncWF
#endif
};

// Convenience function to create uninitialized flag Vells of given shape
inline Vells FlagVells (const LoShape &shp)
{ return Vells(shp,VellsFlagType(),false); }

// Convenience function to create & initialize a flag Vells of given shape
inline Vells FlagVells (VellsFlagType value,const LoShape &shp,bool init=true)
{ return Vells(shp,value,init); }


// Conditionally include inline definitions of Vells math functions
#ifndef MEQVELLS_SKIP_FUNCTIONS

#define defineUnaryFunc(FUNCNAME,flags) \
  inline Vells VellsMath::FUNCNAME (const Vells &arg) \
  { Vells result(arg,flags,#FUNCNAME); \
    (*Vells::unifunc_##FUNCNAME##_lut[arg.getLutIndex()])(result,arg); \
    return result; }
#define defineUnaryRdFunc(FUNCNAME,flags) \
  inline Vells VellsMath::FUNCNAME (const Vells &arg,VellsFlagType flagmask) \
  { Vells result(arg,flags,#FUNCNAME); \
    (*Vells::unifunc_##FUNCNAME##_lut[arg.getLutIndex()])(result,arg,flagmask); \
    return result; }
#define defineUnaryRdFuncWS(FUNCNAME,flags) \
  inline Vells VellsMath::FUNCNAME (const Vells &arg,const Vells::Shape &shape,VellsFlagType flagmask) \
  { Vells result(arg,flags,#FUNCNAME); \
    (*Vells::unifunc_##FUNCNAME##_lut[arg.getLutIndex()])(result,arg,shape,flagmask); \
    return result; }

DoForAllUnaryFuncs1(defineUnaryFunc,0);
DoForAllUnaryFuncs2(defineUnaryFunc,Vells::VF_REAL|Vells::VF_CHECKREAL);
DoForAllUnaryFuncs3(defineUnaryFunc,Vells::VF_REAL);
// group 4: define explicitly
defineUnaryFunc(conj,0);
// group 5: reduction to scalar, no shape
defineUnaryRdFunc(min,Vells::VF_SCALAR|Vells::VF_REAL|Vells::VF_CHECKREAL);
defineUnaryRdFunc(max,Vells::VF_SCALAR|Vells::VF_REAL|Vells::VF_CHECKREAL);
defineUnaryRdFunc(mean,Vells::VF_SCALAR);
// group 6: reduction to scalar, with shape
defineUnaryRdFuncWS(sum,Vells::VF_SCALAR);
defineUnaryRdFuncWS(product,Vells::VF_SCALAR);
defineUnaryRdFuncWS(nelements,Vells::VF_SCALAR|Vells::VF_REAL);

#define defineBinaryFunc(FUNCNAME,flags) \
  inline Vells VellsMath::FUNCNAME (const Vells &left,const Vells &right) \
  { Vells::Strides strides[2]; \
    Vells result(left,right,flags,strides,#FUNCNAME); \
    (*Vells::binfunc_##FUNCNAME##_lut[left.getLutIndex()][right.getLutIndex()])(result,left,right,strides);  \
    return result; }
defineBinaryFunc(pow,0);
defineBinaryFunc(tocomplex,Vells::VF_COMPLEX|Vells::VF_CHECKREAL);
defineBinaryFunc(polar,Vells::VF_COMPLEX|Vells::VF_CHECKREAL);
defineBinaryFunc(posdiff,Vells::VF_REAL|Vells::VF_CHECKREAL);
defineBinaryFunc(atan2,Vells::VF_REAL|Vells::VF_CHECKREAL);
defineBinaryFunc(fmod,Vells::VF_REAL|Vells::VF_CHECKREAL);
defineBinaryFunc(remainder,Vells::VF_REAL|Vells::VF_CHECKREAL);

#define defineBinaryFuncWF(FUNCNAME,flags) \
  inline Vells VellsMath::FUNCNAME (const Vells &a,const Vells &b,VellsFlagType flagmask_a,VellsFlagType flagmask_b) \
  { Vells::Strides strides[4]; \
    Vells result(a,b,flags|Vells::VF_FLAG_STRIDES,strides,#FUNCNAME); \
    (*Vells::binfunc_##FUNCNAME##_lut[a.getLutIndex()][b.getLutIndex()])(result,a,b,flagmask_a,flagmask_b,strides);  \
    return result; }
defineBinaryFuncWF(min,Vells::VF_REAL|Vells::VF_CHECKREAL);
defineBinaryFuncWF(max,Vells::VF_REAL|Vells::VF_CHECKREAL);

#undef defineUnaryFunc
#undef defineUnaryRdFunc
#undef defineUnaryRdFuncWS
#undef defineBinaryFunc
#undef defineBinaryFuncWF

// declare versions of binary operators where the first argument is
// a scalar
#define defineBinaryOper(OPER,OPERNAME,dum) \
  inline Vells operator OPER (double left,const Vells &right) \
  { return Vells(left) OPER right; } \
  inline Vells operator OPER (const dcomplex &left,const Vells &right) \
  { return Vells(left) OPER right; }

DoForAllBinaryOperators(defineBinaryOper,);

#undef defineBinaryOper

// declare versions of binary flag operators where the first argument is
// a scalar. All of them commute, so this is trivial
#define defineBinaryFlagOper(OPER,OPERNAME,dum) \
  inline Vells operator OPER (VellsFlagType left,const Vells &right) \
  { return right OPER left; } \

DoForAllBinaryFlagOperators(defineBinaryFlagOper,);

#undef defineBinaryFlagOper

#endif


inline std::ostream& operator<< (std::ostream& os, const Vells& vec)
  { vec.show (os); return os; }

} // namespace Meq

#endif
