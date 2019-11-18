//# Vells.cc: Values for Meq expressions
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

// #define MEQVELLS_SKIP_FUNCTIONS 1
#include <MEQ/Vells.h>
#include <TimBase/Debug.h>
#include <DMI/Global-Registry.h>
#include <cmath>
#include <complex>

namespace DebugMeq
{
  ::Debug::Context DebugContext("Meq");
}

namespace Meq
{

static DMI::Container::Register reg(TpMeqVells,true);

VellsFlagType Vells::null_flag_(0);
Vells::Shape Vells::null_flag_shape_(1);

const Vells * Vells::pNull_ = 0;
const Vells * Vells::pUnity_ = 0;

void Vells::_init_static_impl ()
{
  Vells::pNull_  = new Vells(double(0),false);
  Vells::pUnity_ = new Vells(double(1),false);
}

Vells::Strides Vells::null_strides;

static void * _init_null_strides = memset(const_cast<Vells::Strides*>(&Vells::null_strides),0,sizeof(Vells::null_strides));

void Vells::mergeFlags (Vells::Ref &flags0,const Vells &flags1,VellsFlagType fm)
{
  if( !fm )
    return;
  if( flags0.valid() )
  {
    if( fm == VellsFullFlagMask )
      flags0() |= flags1;
    else
      flags0() |= (flags1 & fm);
  }
  else
  {
    flags0.attach(flags1);
    if( fm != VellsFullFlagMask )
      flags0() &= fm;
  }
}

//##ModelId=3F86887001D4
// default constructor initializes a by-ref copy of nullVells
Vells::Vells()
: NumArray(Null(),0,0,TpMeqVells)
{
}

// //##ModelId=3F86887001D5
// Vells::Vells (double value,bool temp)
// : NumArray(Tpdouble,LoShape(1),DMI::NOZERO),
//   is_temp_(temp)
// {
//   // casting away const is kinda faster here because we know we
//   // don't need to make the array writable or worry about COW in constructor
//   *static_cast<double*>(const_cast<void*>(getConstDataPtr())) = value;
// }
//
// //##ModelId=3F86887001DC
// Vells::Vells (const dcomplex& value,bool temp)
// : NumArray(Tpdcomplex,LoShape(1),DMI::NOZERO),
//   is_temp_      (temp)
// {
//   // casting away const is kinda faster here because we know we
//   // don't need to make the array writable or worry about COW in constructor
//   *static_cast<dcomplex*>(const_cast<void*>(getConstDataPtr())) = value;
// }
//
// //##ModelId=3F86887001E3
// Vells::Vells (double value,const Vells::Shape &shape, bool init)
// : NumArray(Tpdouble,shape,DMI::NOZERO),
//   is_temp_ (false)
// {
//   if( init )
//   {
//     double *begin = static_cast<double*>(const_cast<void*>(getConstDataPtr())),
//            *end   = begin + nelements();
//     while( begin<end )
//       *(begin++) = value;
//   }
// }
//
// Vells::Vells (const dcomplex &value,const Vells::Shape &shape, bool init)
// : NumArray(Tpdcomplex,shape,DMI::NOZERO),
//   is_temp_ (false)
// {
//   if( init )
//   {
//     dcomplex *begin = static_cast<dcomplex*>(const_cast<void*>(getConstDataPtr())),
//              *end   = begin + nelements();
//     while( begin<end )
//       *(begin++) = value;
//   }
// }

Vells::Vells (const NumArray &that,int flags,int depth)
: NumArray(that,flags,depth,TpMeqVells)
{
  validateContent(false);
}

Vells::Vells (const Vells &that,int flags,int depth)
: NumArray(that,flags,depth,TpMeqVells)
{
  dataflags_.copy(that.dataflags_);
}

//##ModelId=3F868870023B
Vells& Vells::operator= (const Vells& other)
{
  if( this != &other)
  {
    NumArray::operator = (other);
    dataflags_ = other.dataflags_;
  }
  return *this;
}

void Vells::validateContent (bool)
{
  FailWhen(rank()>Axis::MaxAxis,"can't init Meq::Vells from array: rank too high");
//  FailWhen(elementType()!=Tpdouble && elementType()!=Tpdcomplex,
//      "can't init Meq::Vells from array of type "+elementType().toString());
}

//##ModelId=3F8688700238
Vells::~Vells()
{
}

//##ModelId=3F8688700282
void Vells::show (std::ostream& os) const
{
  os<<sdebug(2);
}

//##ModelId=400E53560110
void Vells::copyData (const Vells &other)
{
  if( this != &other )
  {
    FailWhen( shape() != other.shape() || elementType() != other.elementType(),
        "Meq::Vells size/type mismatch");
    memcpy(getDataPtr(),other.getConstDataPtr(),nelements()*elementSize());
  }
}

//##ModelId=400E5356011C
void Vells::zeroData ()
{
  makeWritable();
  memset(getDataPtr(),0,nelements()*elementSize());
}


// // a HyperPlane iterator iterates over hyperplanes defined by a set of axes
// Vells::ConstHPIterator::ConstHPIterator (const Vells &vells,const std::vector<int> &axes)
//   : vells_(vells),hpaxes_(vells.size(),false);
// {
//   for( uint i=0; i<axes.size(); i++ )
//   {
//     FailWhen(axes[i]<0 || axes[i]>=int(vells.size()),"illegal axis number");
//     hpaxes_[axes[i]] = true;
//   }
//   init();
// }
//
// Vells::ConstHPIterator::ConstHPIterator (const Vells &vells,const std::vector<bool> &axes)
//   : vells_(vells),hpaxes_(axes)
// {
//   FailWhen(hpaxes_.size()!=vells.size(),"axes array size mismatch");
//   init();
// }
//
// Vells::ConstHPIterator::ConstHPIterator (const Vells &vells,int axis)
//   : vells_(vells),hpaxes_(vells.size(),false);
// {
//   FailWhen(axis<0 || axis>=int(vells.size()),"illegal axis number");
//   hpaxes_[axis] = true;
//   init();
// }
//
// void Vells::ConstHPIterator::operator bool ()
// {
// }
//
// void Vells::ConstHPIterator::init ()
// {
//
// }
//
//
//

//##ModelId=400E5356019D
inline bool Vells::tryReference (const Vells &)
{
// disable for now: figure out how this plays with COWs later
//   // the 'other' array can be reused if it's a temp, it has the
//   // same size and type, and it's writable
//   if( other.isTemp() &&
//       other.array_.valid() &&
//       elementType() == other.elementType() &&
//       shape() == other.shape() )
//   {
//     // if other is not directly writable, no point in reusing it
//     if( !other.array_.isDirectlyWritable() )
//       return false;
//     array_ = other.array_;
//     storage_ = other.storage_;
//     return true;
//   }
  return false;
}

// helper function used to figure out type of result
TypeId Vells::getResultType (int flags,bool arg_is_complex)
{
  if( flags&VF_FLAGTYPE )
    return VellsFlagTypeId;
  else if( flags&Vells::VF_COMPLEX || ( !(flags&Vells::VF_REAL) && arg_is_complex ) )
    return Tpdcomplex;
  else
    return Tpdouble;
}

// constructor for a temp vells in unary expression
//##ModelId=3F8688700231
Vells::Vells (const Vells &other,int flags,const std::string &opname)
{
  // check input if requested by flags
  FailWhen(flags&VF_CHECKREAL && other.isComplex(),
      opname + "() can only be used with a real Meq::Vells");
  FailWhen(flags&VF_CHECKCOMPLEX && other.isReal(),
      opname + "() can only be used with a complex Meq::Vells");
  FailWhen(flags&VF_FLAGTYPE && !other.isFlags(),
      opname + "() can only be used with a flags Meq::Vells");
  // determine shape
  if( !tryReference(other) )
    NumArray::init( getResultType(flags,other.isComplex()),
        flags&VF_SCALAR ? LoShape(1) : other.shape(),DMI::NOZERO);
}

// // constructor for a temp vells in a unary reduction expression
// // (i.e. result is collapsed along one axis)
// //##ModelId=3F8688700231
// Vells::Vells (const Vells &other,int axis,int flags,const std::string &opname)
// : is_temp_ (true)
// {
//   // check input if requested by flags
//   FailWhen(flags&VF_CHECKREAL && other.isComplex(),
//       opname + "() can only be used with a real Meq::Vells");
//   FailWhen(flags&VF_CHECKCOMPLEX && other.isReal(),
//       opname + "() can only be used with a complex Meq::Vells");
//   FailWhen(axis<0,"illegal axis<0 specified");
//   int nred;
//   if( axis >= other.rank() || (nred = other.shape()[axis]) == 1)
//   {
//     // no reduction needed, clone and return
//     clone(other);
//     nstr = 0;
//   }
//   else // reduction required
//   {
//     shape_ = other.shape();
//     shape_[axis] = 1;
//     num_elements_ = other.num_elements_/nred;
//     setSizeType(flags,other.isComplex());
//     // setup output array
//     DMI::NumArray *parr;
//     array_ <<= parr = new DMI::NumArray(element_type_,shape_);
//     storage_ = parr->getDataPtr();
//     // setup strides for reduction iterator. The output iterates over
//     // every contiguous point. The input has to iterate over the starting point
//     // of
//     int ired = 0;
//     int tot = 1;
//     bool degen = true;
//     for( int i=0; i<rank(); i++)
//     {
//       // compute stride -- treat axis being reduced as a degenerate axis
//       stride[i] = i!=axis && shape_[i]>1 ? normalAxis(tot,degen) : degenerateAxis(tot,degen);
//
//     }
//   }
// }
//
// Helper functions for setting up strides below
// Marks axis i as normally strided
inline int normalAxis (int total,bool &degenerate)
{
  // If previous dimensions were degenerate (this is also true when i=0, as the
  // flag is initialized to true), then the stride along this axis corresponds
  // to the size of a full sub-plane (i.e. hyperplane in all lower dimensions),
  // or 1 initially.
  // If previous axes are normal, then stride must be 0 (since iterating over
  // a sub-plane automatically gets us to the next sub-plane).
  if( !degenerate )
    return 0;
  degenerate = false;
  return total;
}
// Marks axis i as degenerate
inline int degenerateAxis (int total,bool &degenerate)
{
  // If previous dimensions were degenerate (this is also true when i=0, as the
  // flag is initialized to true), then the stride along this axis is just 0.
  // If previous axes were normal, then we must go back to the start of the
  // array, which corresponds to a stride of -total.
  if( degenerate )
    return 0;
  degenerate = true;
  return -total;
}

// computes strides corresponding to the given shape
int Vells::computeStrides (Vells::Strides &strides,const Vells::Shape &shape)
{
  int cur_stride = 1;
  int i;
  for( i=Axis::MaxAxis-1; i>=int(shape.size()); i-- )
    strides[i] = 0;
  for( ; i>=0; i-- )
  {
    strides[i] = cur_stride;
    cur_stride *= shape[i];
  }
  return cur_stride;
}

// general function to compute shape of output, plus strides required,
// given N argument shapes.
// note that strides are placed in reverse order, since Vells are now
// stored in row-major order. I.e. the last dimension has a stride of 1,
// and previous dimensions have larger strides.
void Vells::computeStrides (Vells::Shape &outshape,
                            Strides strides[],
                            int nshapes,const Vells::Shape * shapes[],
                            const string &opname)
{
  uint rnk = 0;
  for( int i=0; i<nshapes; i++ )
    rnk = std::max(rnk,uint(shapes[i]->size()));
  outshape.resize(rnk);
  // initialize per-shape arrays for loop below
  int tot[nshapes];
  bool deg[nshapes];
  for( int j=0; j<nshapes; j++ )
  {
    tot[j] = 1;
    deg[j] = true;
  }
  // Loop over all axes to determine output shape and input strides for iterators.
  uint idim = rnk-1;
  for( uint i=0; i<rnk; i++,idim-- )
  {
    int sz0 = 1;
    // get size along each shape's axis #idim -- if past the last rank, use 1
    for( int j=0; j<nshapes; j++ )
    {
      int sz = idim < shapes[j]->size() ? (*shapes[j])[idim] : 1;
      bool big = sz > 1;
      // if not trivial size, check for consistency with sz0
      if( big )
      {
        if( sz0 == 1 )
          sz0 = sz;
        else if( sz != sz0 )
          { Throw1("arguments to "+opname+" have incompatible shapes"); }
      }
      // set strides
      strides[j][i] = big ? normalAxis(tot[j],deg[j]) : degenerateAxis(tot[j],deg[j]);
      // increase eleemnt count
      tot[j] *= sz;
    }
    // set output shape
    outshape[idim] = sz0;
  }
}

// Constructor for a temp vells for the result of a binary expression.
// The shape of the result is the maximum of the argument shapes;
// the constructor will also compute strides for the arguments.
//##ModelId=400E53560174
Vells::Vells (const Vells &a,const Vells &b,int flags,
              Strides strides[],const std::string &opname)
{
  // check input if requested by flags
  FailWhen(flags&VF_FLAGTYPE && !(a.isFlags() && b.isFlags()),
      opname + "() can only be applied to two flags Meq::Vells");
  FailWhen(flags&VF_CHECKREAL && (a.isComplex() || b.isComplex()),
      opname + "() can only be applied to two real Meq::Vells");
  FailWhen(flags&VF_CHECKCOMPLEX && (a.isReal() || b.isReal()),
      opname + "() can only be applied to two complex Meq::Vells");
  // determine shape and strides
  LoShape shp;
  if( flags&VF_FLAG_STRIDES )
    computeStrides(shp,strides,a,b,opname);
  else
    computeStrides(shp,strides,a.shape(),b.shape(),opname);
  // now, if we're still congruent with the a or b, and it's
  // a temporary, then we can reuse its storage. Else allocate new
  if( !( tryReference(a) || tryReference(b) ) )
    NumArray::init(getResultType(flags,a.isComplex() || b.isComplex()),shp,DMI::NOZERO);
}

// Determines if other Vells can be applied to us in-place (i.e. += and such).
// This is only possible if our type and shape are not lower-ranked.
// If operation is not applicable, returns false.
// If it is, returns true and populates strides[] with the incremental strides
// which need to be applied to other.
bool Vells::canApplyInPlace (const Vells &other,Strides & strides,const std::string &opname)
{
  // try the simple tests first
  if( (isReal() && other.isComplex()) || (rank() < other.rank()) )
    return false;
  // Loop over all axes to determine if shapes match. Our rank is higher thanks
  // to test above
  int  total=1;
  int  idim=rank()-1;
  bool deg=true;
  for( int i=0; i<rank(); i++,idim-- )
  {
    // get size along each axis -- if past the last rank, use 1
    int sz_ours  = extent(idim);
    int sz_other = other.extent(idim);
    if( sz_other == 1 ) // other is constant along this axis
      strides[i] = degenerateAxis(total,deg);
    else if( sz_ours == sz_other ) // shape of this axis >1 and matches
      strides[i] = normalAxis(total,deg);
    else if( sz_ours == 1 ) // we are constant along this axis but other isn't -- bug out
      return false;
    else // both non-constant, but incompatible
      Throw("argument to "+opname+" has an incompatible shape");
    total *= sz_other;
  }
  return true;
}

//##ModelId=400E5356011F
string Vells::sdebug (int detail,const string &pf,const char *nm) const
{
  return NumArray::sdebug(detail,pf,nm?nm:"MeqVells");
}

} // namespace Meq

using namespace DMI;
using namespace DebugMeq;
using std::min;
using std::max;

// Close the namespace Meq declaration, since we don't want any Meq math
// functions polluting the current scope -- this can confuse the compiler
// in the code below.

// -----------------------------------------------------------------------
// Vells math
//
// -----------------------------------------------------------------------
// define a traits-like structure for type promotions:
//    Promote<T1,T2>::type returns bigger type of the two
template<class T1,class T2> struct Promote;

template<class T> struct Promote<T,T> { typedef T type; };

#define definePromotion2(a,b,to) \
  template<> struct Promote<a,b> { typedef to type; }; \
  template<> struct Promote<b,a> { typedef to type; };
definePromotion2(double,dcomplex,dcomplex);


// repeats macro invocation Do(type,x,y) in order of increasing LUT types
#define RepeatForRealLUTs(Do) \
  Do(double)
#define RepeatForComplexLUTs(Do) \
  Do(dcomplex)
#define RepeatForLUTs(Do) \
  RepeatForRealLUTs(Do), RepeatForComplexLUTs(Do)

#define RepeatForRealLUTs1(Do,x) \
  Do(double,x)
#define RepeatForComplexLUTs1(Do,x) \
  Do(dcomplex,x)
#define RepeatForLUTs1(Do,x) \
  RepeatForRealLUTs1(Do,x), RepeatForComplexLUTs1(Do,x)

#define RepeatForRealLUTs2(Do,x,y) \
  Do(double,x,y)
#define RepeatForComplexLUTs2(Do,x,y) \
  Do(dcomplex,x,y)
#define RepeatForLUTs2(Do,x,y) \
  RepeatForRealLUTs2(Do,x,y), RepeatForComplexLUTs2(Do,x,y)

// defines a standard error function (for illegal unary ops)
#define defineErrorFunc(errname,message) \
  static void errname (Meq::Vells &,const Meq::Vells &) \
  { Throw(message); }
// defines a standard error function (for illegal unary ops with flags)
#define defineErrorRedFunc(errname,message) \
  static void errname (Meq::Vells &,const Meq::Vells &,FT) \
  { Throw(message); }
// defines a standard error function (for illegal binary ops)
#define defineErrorFunc2(errname,message) \
  static void errname (Meq::Vells &,const Meq::Vells &,const Meq::Vells &,const Meq::Vells::Strides [2]) \
  { Throw(message); }
// defines a standard error function (for illegal binary ops with flags)
#define defineErrorFunc2WF(errname,message) \
  static void errname (Meq::Vells &,const Meq::Vells &,const Meq::Vells &,FT,FT,const Meq::Vells::Strides [4]) \
  { Throw(message); }

// defines a standard error function template (for illegal unary ops)
#define defineErrorFuncTemplate(FUNCNAME,message) defineErrorFuncTemplate2(FUNCNAME,message)
#define defineErrorFuncTemplate2(FUNCNAME,message) \
  template<class T1,class T2> defineErrorFunc(implement_error_##FUNCNAME,message);
#define defineErrorRedFuncTemplate(FUNCNAME,message) \
  template<class T1,class T2> defineErrorRedFunc(implement_error_##FUNCNAME,message);
// defines a standard error function template (for illegal binary ops)
#define defineErrorFuncTemplate3(FUNCNAME,message) \
  template<class T1,class T2,class T3> defineErrorFunc(implement_error_##FUNCNAME,message);

template<class TY,class TX>
static void implement_copy (Meq::Vells &out,const Meq::Vells &in)
{ out.copyData(in); }

template<class TY,class TX>
static void implement_zero (Meq::Vells &out,const Meq::Vells &)
{ out.zeroData(); }


// -----------------------------------------------------------------------
// Vells math implementation
// This is where it gets hairy...
// -----------------------------------------------------------------------

// expands to list of methods with matching argument types
#define ExpandMethodList(FUNC) \
  ExpandMethodList2(FUNC,FUNC)

// expands to list of methods with matching argument types, uses different
// funcs for real and complex
#define ExpandMethodList2(FR,FC) \
  { &implement_##FR<double,double>, &implement_##FC<dcomplex,dcomplex> }

// expands to list of methods with fixed output type
#define ExpandMethodList_FixOut(FUNC,TOUT) \
  ExpandMethodList2_FixOut(FUNC,FUNC,TOUT)

#define ExpandMethodList2_FixOut(FR,FC,TOUT) \
  { &implement_##FR<TOUT,double>, &implement_##FC<TOUT,dcomplex> }

typedef Meq::VellsFlagType FT; // to keep things compact

template<class T> inline T sqr (T x) { return x*x; }
template<class T> inline T pow2(T x) { return x*x; }
template<class T> inline T pow3(T x) { return x*x*x; }
template<class T> inline T pow4(T x) { T t1 = x*x; return t1*t1; }
template<class T> inline T pow5(T x) { T t1 = x*x; return t1*t1*x; }
template<class T> inline T pow6(T x) { T t1 = x*x*x; return t1*t1; }
template<class T> inline T pow7(T x) { T t1 = x*x; return t1*t1*t1*x; }
template<class T> inline T pow8(T x) { T t1 = x*x, t2=t1*t1; return t2*t2; }

#ifdef USE_STD_COMPLEX

template<typename T>
inline T UNARY_MINUS_impl (T x)
{ return -x; }

inline double arg (const double x)
{
    return std::arg(*reinterpret_cast<const std::complex<double>*>(&x));
}
#else

// unary minus -- not defined for C99 _Complex, so implement explicitly
inline double UNARY_MINUS_impl (double x)
{ return -x; }
inline dcomplex UNARY_MINUS_impl (dcomplex x)
{ return - __real__ x - 1i*(__imag__ x); }


// Define _Complex double versions for unary functions, group 1.
// most of them map to gcc __builtin_c<func>() functions, with the exception
// of the inlines already declared above.
#define defineComplexFunc(FUNCNAME,x) \
  inline dcomplex FUNCNAME (dcomplex arg) \
  { return __builtin_c##FUNCNAME(arg); }
// temporary hack since builtin_clog appears to be missing in gcc (as of 3.4.5)
inline dcomplex __builtin_clog (dcomplex x)
{
  std::complex<double> y = log(*reinterpret_cast<std::complex<double>*>(&x));
  return *reinterpret_cast<dcomplex*>(&y);
}

defineComplexFunc(cos,x) defineComplexFunc(cosh,x)
defineComplexFunc(exp,x) defineComplexFunc(log,x)
defineComplexFunc(sin,x) defineComplexFunc(sinh,x)
defineComplexFunc(tan,x) defineComplexFunc(tanh,x)
defineComplexFunc(sqrt,x)

#define __builtin_cfabs(x) __builtin_cabs(x)
#define __builtin_cnorm(x) __builtin_cabs(x)

#undef defineComplexFunc
#define defineComplexFunc(FUNCNAME,x) \
  inline double FUNCNAME (dcomplex arg) \
  { return __builtin_c##FUNCNAME(arg); }
#define abs _tmpabs_
DoForAllUnaryFuncs3(defineComplexFunc,);
#undef abs

inline dcomplex conj (dcomplex x)
{ return ~x; }

inline dcomplex pow (dcomplex x,dcomplex y)
{ return __builtin_cpow(x,y); }

inline dcomplex pow (dcomplex x,double y)
{ return __builtin_cpow(x,y+0i); }

inline dcomplex pow (double x,dcomplex y)
{ return __builtin_cpow(x+0i,y); }

// version of arg() for doubles
inline double arg (const double x)
{ return x>=0 ? 0 : -M_PI; }

#endif


// -----------------------------------------------------------------------
// definitions for unary operators
// defined for all types, preserves type
// -----------------------------------------------------------------------
// defines a templated implementation of an unary function
//    y = FUNC(x)
#define defineUnaryOperTemplate(FUNC,FUNCNAME,dum) \
  template<class TY,class TX> \
  static void implement_##FUNCNAME (Meq::Vells &y,const Meq::Vells &x) \
  { const TX *px = x.getStorage(Type2Type<TX>()); \
    TY *py = y.begin(Type2Type<TY>()), \
       *py_end = y.end(Type2Type<TY>());  \
    for( ; py < py_end; px++,py++ ) \
      *py = FUNC(*px); \
  }

#define implementUnaryOperator(OPER,OPERNAME,x) \
  defineUnaryOperTemplate(OPERNAME##_impl,OPERNAME,x); \
  Meq::Vells::UnaryOperPtr Meq::Vells::unary_##OPERNAME##_lut[VELLS_LUT_SIZE] = \
    ExpandMethodList(OPERNAME);

DoForAllUnaryOperators(implementUnaryOperator,);

// -----------------------------------------------------------------------
// definitions for unary flag operators
// -----------------------------------------------------------------------
#define implementUnaryFlagOperator(OPER,OPERNAME,x) \
  Meq::Vells Meq::Vells::operator OPER () const \
  { \
    Vells result(*this,VF_FLAGTYPE,"operator "#OPER); \
    for( FT *ptr = result.begin<FT>(); ptr != result.end<FT>(); ptr++ ) \
       (*ptr) = OPER (*ptr); \
    return result; \
  }

DoForAllUnaryFlagOperators(implementUnaryFlagOperator,);


// -----------------------------------------------------------------------
// definitions for unary functions, Group 1
// defined for all types, preserves type
// -----------------------------------------------------------------------

#define defineUnaryFuncTemplate(FUNC,x) defineUnaryOperTemplate(FUNC,FUNC,x)

#define implementUnaryFunc1(FUNCNAME,x) \
  defineUnaryFuncTemplate(FUNCNAME,x) \
  Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_##FUNCNAME##_lut[VELLS_LUT_SIZE] = \
    ExpandMethodList(FUNCNAME);

DoForAllUnaryFuncs1(implementUnaryFunc1,);

// -----------------------------------------------------------------------
// definitions for unary functions, Group 2
// For real Vells only, result is real
// -----------------------------------------------------------------------
// defines a standard error function template for illegal unary ops
#define defineErrorUniFuncTemplate(FUNCNAME,message) \
  template<class T1,class T2> defineErrorFunc(implement_error_##FUNCNAME,message);

#define implementUnaryFunc2(FUNCNAME,x) \
  defineUnaryFuncTemplate(FUNCNAME,x) \
  defineErrorFuncTemplate(FUNCNAME,#FUNCNAME "() can only be applied to a real Meq::Vells") \
  Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_##FUNCNAME##_lut[VELLS_LUT_SIZE] = \
    ExpandMethodList2(FUNCNAME,error_##FUNCNAME);

DoForAllUnaryFuncs2(implementUnaryFunc2,);

// -----------------------------------------------------------------------
// definitions for unary functions, Group 3
// for all types, but always returns a real Vells
// -----------------------------------------------------------------------

DoForAllUnaryFuncs3(defineUnaryFuncTemplate,);

// fabs():     use abs for complex and fabs for real
  Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_fabs_lut[VELLS_LUT_SIZE] = \
    ExpandMethodList2_FixOut(fabs,abs,double);
// abs():      same as fabs
Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_abs_lut[VELLS_LUT_SIZE] =
    ExpandMethodList2_FixOut(fabs,abs,double);

// real()
// Use standard template for complex numbers, and copy for doubles
Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_real_lut[VELLS_LUT_SIZE] =
    ExpandMethodList2_FixOut(copy,real,double);

// imag()
// Use standard template for complex numbers, and zero for doubles
Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_imag_lut[VELLS_LUT_SIZE] =
    ExpandMethodList2_FixOut(zero,imag,double);

// norm()
// Use standard template for complex numbers, and sqr for doubles
Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_norm_lut[VELLS_LUT_SIZE] =
    ExpandMethodList2_FixOut(sqr,norm,double);

// arg()
Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_arg_lut[VELLS_LUT_SIZE] =
    ExpandMethodList_FixOut(arg,double);


// -----------------------------------------------------------------------
// definitions for unary functions, Group 4
// special treatment
// -----------------------------------------------------------------------

// conj()
// Use standard template for complex numbers, and copy for doubles
defineUnaryFuncTemplate(conj,x);
Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_conj_lut[VELLS_LUT_SIZE] =
    ExpandMethodList2(copy,conj);


// -----------------------------------------------------------------------
// definitions for unary functions, Group 5
// reduction to scalar, no shape required (min, max, mean etc.)
// -----------------------------------------------------------------------
// since "0" does not automatically convert to a complex,
// provide explicit conversion via these functions.
// the second pointer argument is a dummy used for type matching
inline double mkconst (double x,double *)
{ return x; }
inline dcomplex mkconst (double x,dcomplex *)
{ return x + complex<double>(0, 0); }
inline dcomplex mkconst (int x,dcomplex *)
{ return double(x) + complex<double>(0, 0); }

// Defines a templated implementation of an unary reduction function
// which computes: y=y0, then y=FUNC(y,x(i)) for all i, and returns y
// This is a helper template for all reduction functions.
#define defineReductionFuncImpl(FUNC,FUNCNAME,y_init) \
  template<class TY,class TX> \
  static inline TY implement_##FUNCNAME##_impl (int &nel,const Meq::Vells &x,FT flagmask,\
    Type2Type<TY> = Type2Type<TY>(),Type2Type<TX> = Type2Type<TX>() ) \
  { \
    TY y0 = mkconst(y_init,(TY*)0); \
    if( flagmask && x.hasDataFlags() ) { \
      Meq::Vells::Strides st[2]; \
      Meq::Vells::Shape shp; \
      const Meq::Vells & flags = x.dataFlags(); \
      Meq::Vells::computeStrides(shp,st,x.shape(),flags.shape(),#FUNCNAME); \
      Meq::Vells::DimCounter counter(shp);  \
      Meq::Vells::ConstStridedIterator<TX> ix(x.begin(Type2Type<TX>()),st[0]); \
      Meq::Vells::ConstStridedIterator<FT> ifl(flags.begin(Type2Type<FT>()),st[1]); \
      nel=0; \
      for(;;) { \
        if( !((*ifl)&flagmask) ) \
          { FUNC(y0,*ix); nel++; } \
        int ndim = counter.incr(); \
        if( ndim <= 0 ) \
          break; \
        ix.incr(ndim); ifl.incr(ndim); \
      } \
    } \
    else { \
      const TX *px = x.begin(Type2Type<TX>()), \
               *px_end = x.end(Type2Type<TX>()); \
      nel = px_end - px; \
      for(; px < px_end; px++) \
        FUNC(y0,*px); \
    } \
    return y0; \
  }

// defines a templated implementation of an unary reduction function such
// as min() or max(), which works by applying y=FUNC(y,x) to all
// (non-flagged) elements
#define defineReductionFuncTemplate(FUNC,y_init) \
  defineReductionFuncImpl(Do_##FUNC,FUNC,y_init); \
  template<class TY,class TX> \
  static void implement_##FUNC (Meq::Vells &y,const Meq::Vells &x,FT flagmask) \
  { int nel; \
    y.as(Type2Type<TY>()) = \
      implement_##FUNC##_impl(nel,x,flagmask,Type2Type<TY>(),Type2Type<TX>()); \
  }

#define Do_min(y,x) y=min(x,y)
defineReductionFuncTemplate(min,std::numeric_limits<TY>::max());
defineErrorRedFuncTemplate(min,"min() can only be applied to a real Meq::Vells");
#define Do_max(y,x) y=max(x,y)
defineReductionFuncTemplate(max,std::numeric_limits<TY>::min());
defineErrorRedFuncTemplate(max,"max() can only be applied to a real Meq::Vells");

Meq::Vells::UnaryRdFuncPtr Meq::Vells::unifunc_min_lut[VELLS_LUT_SIZE] =
  ExpandMethodList2(min,error_min);
Meq::Vells::UnaryRdFuncPtr Meq::Vells::unifunc_max_lut[VELLS_LUT_SIZE] =
  ExpandMethodList2(max,error_max);

// implement a DOSUM function which sums up a complete Vells. This
// sum is unnormalized because it does not take into account scalar axes
#define DOSUM(y,x) ((y) += (x))
defineReductionFuncImpl(DOSUM,sum,0);

template<class TY,class TX>
static void implement_mean (Meq::Vells &y,const Meq::Vells &x,FT flagmask)
{
  int nel;
  TY y0 = implement_sum_impl(nel,x,flagmask,Type2Type<TY>(),Type2Type<TX>());
  y.as(Type2Type<TY>()) = nel ? y0/mkconst(nel,&y0) : mkconst(0,&y0);
}
Meq::Vells::UnaryRdFuncPtr Meq::Vells::unifunc_mean_lut[VELLS_LUT_SIZE] =
  ExpandMethodList(mean);


// -----------------------------------------------------------------------
// definitions for unary functions, Group 6
// reduction to scalar, shape required (sum, product, etc.)
// -----------------------------------------------------------------------
// these functions require a renormalization term, to take into account the
// fact that a Vells constant along axis #i will only contain one
// actual value to represent Ni points.
// The renormalization term is (N points in full shape)/(N actual points in Vells)
template<class TY,class TX>
static void implement_sum (Meq::Vells &y,const Meq::Vells &x,const Meq::Vells::Shape &shape,FT flagmask)
{
  int nel;
  TY y0 = implement_sum_impl(nel,x,flagmask,Type2Type<TY>(),Type2Type<TX>());
  int renorm = shape.product()/x.nelements(); // renorm factor for collapsed dimensions
  y.as(Type2Type<TY>()) = y0 * mkconst(renorm,&y0);
}

#define DOPROD(y,x) ((y) *= (x))
defineReductionFuncImpl(DOPROD,product,1);
template<class TY,class TX>
static void implement_product (Meq::Vells &y,const Meq::Vells &x,const Meq::Vells::Shape &shape,FT flagmask)
{
  int nel;
  TY y0 = implement_product_impl(nel,x,flagmask,Type2Type<TY>(),Type2Type<TX>());
  int renorm = shape.product()/x.nelements(); // renorm factor for collapsed dimensions
  y.as(Type2Type<TY>()) = pow(y0,renorm);
}

// empty def because nel argument counts for us
#define DOCOUNT(y,x)
defineReductionFuncImpl(DOCOUNT,nelements,0);
template<class TY,class TX>
static void implement_nelements (Meq::Vells &y,const Meq::Vells &x,const Meq::Vells::Shape &shape,FT flagmask)
{
  if( flagmask && x.hasDataFlags() )
  {
    int nel;
    implement_nelements_impl(nel,x,flagmask,Type2Type<TY>(),Type2Type<TX>());
    // now, nel counts the non-flagged elements, auto-expanding collapsed axes
    // to the union of the data shape and the flag shape. If input shape is
    // bigger still, we need to renormalize by the remaining collapsed dimensions.
    const Meq::Vells &df = x.dataFlags();
    for( uint i=0; i<shape.size(); i++ )
      if( shape[i] > 1 && x.extent(i) == 1 && df.extent(i) == 1 )
        nel *= shape[i];
    y.as<double>() = nel;
  }
  else
    y.as<double>() = shape.product();
}

Meq::Vells::UnaryRdFuncWSPtr Meq::Vells::unifunc_sum_lut[VELLS_LUT_SIZE] =
  ExpandMethodList(sum);
Meq::Vells::UnaryRdFuncWSPtr Meq::Vells::unifunc_product_lut[VELLS_LUT_SIZE] =
  ExpandMethodList(product);
Meq::Vells::UnaryRdFuncWSPtr Meq::Vells::unifunc_nelements_lut[VELLS_LUT_SIZE] =
  ExpandMethodList(nelements);


// -----------------------------------------------------------------------
// definitions for binary operators
// -----------------------------------------------------------------------
// defines a templated implementation of a binary function
//    y = FUNC(a,b)
#define defineBinaryFuncTemplate(FUNC,FUNCNAME,dum) \
  template<class TY,class TA,class TB> \
  static void implement_binary_##FUNCNAME (Meq::Vells &y,\
                  const Meq::Vells &a,const Meq::Vells &b,\
                  const Meq::Vells::Strides strides[2]) \
  { TY *py = y.getStorage(Type2Type<TY>()); \
    const TA *pa = a.getStorage(Type2Type<TA>()); \
    const TB *pb = b.getStorage(Type2Type<TB>()); \
    if( a.isScalar() && b.isScalar() ) \
      *py = FUNC(*pa,*pb); \
    else { \
      Meq::Vells::DimCounter counter(y);  \
      Meq::Vells::ConstStridedIterator<TA> ia(pa,strides[0]); \
      Meq::Vells::ConstStridedIterator<TB> ib(pb,strides[1]); \
       for(;;) { \
        *py = FUNC(*ia,*ib); \
        int ndim = counter.incr(); \
        if( ndim <= 0 ) \
          break; \
        py++; ia.incr(ndim); ib.incr(ndim); \
      } \
    } \
  }

// define "functions" for the four binary operators
#define ADD(a,b) ((a)+(b))
#define SUB(a,b) ((a)-(b))
#define MUL(a,b) ((a)*(b))
#define DIV(a,b) ((a)/(b))

// Expands to address of binary function template defined above,
// with the result type being the type-promotion of its argument types
#define AddrBinaryFunction(TRight,TLeft,FUNC) \
  &implement_binary_##FUNC<Promote<TRight,TLeft>::type,TLeft,TRight>
// Expands to address of binary function template defined above,
// with the result type always dcomplex
#define AddrComplexBinaryFunction(TRight,TLeft,FUNC) \
  &implement_binary_##FUNC<dcomplex,TLeft,TRight>
// Expands to address of an error function
#define AddrErrorFunction(TRight,TLeft,FUNC) \
  &error_binary_##FUNC

// Expands to one row of binary LUT table. TLeft is constant, TRight
// goes through all LUT indices
#define BinaryLUTRow(TLeft,FUNC) \
  { RepeatForLUTs2(AddrBinaryFunction,TLeft,FUNC) }

// Expands to one row of binary LUT table. TLeft is constant, TRight
// goes through all LUT indices. For complex TRight arguments, maps
// to error function.
#define BinaryRealLUTRow(TLeft,FUNC) \
  { RepeatForRealLUTs2(AddrBinaryFunction,TLeft,FUNC), \
    RepeatForComplexLUTs2(AddrErrorFunction,TLeft,FUNC) }
// Expands to one row of binary LUT table with dcomplex result.
// TLeft is constant, TRight
// goes through all LUT indices. For complex TRight arguments, maps
// to error function.
#define BinaryRealToComplexLUTRow(TLeft,FUNC) \
  { RepeatForRealLUTs2(AddrComplexBinaryFunction,TLeft,FUNC), \
    RepeatForComplexLUTs2(AddrErrorFunction,TLeft,FUNC) }
// Expands to one row of binary LUT table, composed of references to the
// error function.
#define BinaryErrorLUTRow(TLeft,FUNC) \
  { RepeatForLUTs2(AddrErrorFunction,TLeft,FUNC) }

// Expands to full binary LUT table.
//    minor (second) index corresponds to LUT index of right argument
//    major (first) index corresponds to LUT index of left argument
#define ExpandBinaryLUTMatrix(FUNC) \
  { RepeatForLUTs1(BinaryLUTRow,FUNC) }
// Expands to real-only binary LUT table
// (complex arguments mapped to error funcs)
#define ExpandRealBinaryLUTMatrix(FUNC) \
  { RepeatForRealLUTs1(BinaryRealLUTRow,FUNC), \
    RepeatForComplexLUTs1(BinaryErrorLUTRow,FUNC) }
// Expands to real-only binary LUT table returning dcomplex
// (complex arguments mapped to error funcs)
#define ExpandRealToComplexBinaryLUTMatrix(FUNC) \
  { RepeatForRealLUTs1(BinaryRealToComplexLUTRow,FUNC), \
    RepeatForComplexLUTs1(BinaryErrorLUTRow,FUNC) }

// Implements all binary operators via the template above
#define implementBinaryOperator(OPER,OPERNAME,dum) \
  defineBinaryFuncTemplate(OPERNAME,OPERNAME,dum) \
  Meq::Vells::BinaryOperPtr Meq::Vells::binary_##OPERNAME##_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE] = \
    ExpandBinaryLUTMatrix(OPERNAME);

DoForAllBinaryOperators(implementBinaryOperator,);

// -----------------------------------------------------------------------
// definitions for binary flag operators
// -----------------------------------------------------------------------

// provide implementation for flag ops: separate ones for a Vells rhs
// and for a scalar rhs
#define implementBinaryFlagOperator(OPER,OPERNAME,dum) \
  Meq::Vells Meq::Vells::operator OPER (const Meq::Vells &right) const \
  { Strides st[2]; \
    Vells result(*this,right,VF_FLAGTYPE,st,"operator "#OPER); \
    FT *py = result.begin<FT>(); \
    const FT *pa = begin<FT>(); \
    const FT *pb = right.begin<FT>(); \
    if( isScalar() && right.isScalar() ) \
      *py = (*pa) OPER (*pb); \
    else { \
      Meq::Vells::DimCounter counter(result);  \
      Meq::Vells::ConstStridedIterator<FT> ia(pa,st[0]); \
      Meq::Vells::ConstStridedIterator<FT> ib(pb,st[1]); \
      for(;;) { \
        *py = (*ia) OPER (*ib); \
        int ndim = counter.incr(); \
        if( ndim <= 0 ) \
          break; \
        py++; ia.incr(ndim); ib.incr(ndim); \
      } \
    } \
    return result; \
  } \
  Meq::Vells Meq::Vells::operator OPER (FT right) const \
  { \
    Vells result(*this,VF_FLAGTYPE,"operator "#OPER); \
    const FT *px = begin<FT>(); \
    for( FT *py = result.begin<FT>(); py != result.end<FT>(); px++,py++ ) \
       (*py) = (*px) OPER right; \
    return result; \
  }

DoForAllBinaryFlagOperators(implementBinaryFlagOperator,);

// -----------------------------------------------------------------------
// definitions for in-place operators
// -----------------------------------------------------------------------

// defines a templated implementation of an in-place operator
//    y OPER = x (i.e., +=, -=, etc.)
// this version only called when the variability of y is >= that of x,
// (otherwise remapped to y = y + x, see declarations in Vells.h)
#define defineInPlaceOperTemplate(OPER,OPERNAME,dum) \
  template<class TOut,class TY,class TX> \
  static void implement_binary_##OPERNAME##_inplace (Meq::Vells &y,\
                  const Meq::Vells &x,\
                  const Meq::Vells::Strides &strides_x) \
  { TOut *py = y.getStorage(Type2Type<TOut>()); \
    const TX *px = x.getStorage(Type2Type<TX>()); \
    if( y.isScalar() && x.isScalar() ) \
      *py OPER##= *px; \
    else { \
      Meq::Vells::DimCounter counter(y);  \
      Meq::Vells::ConstStridedIterator<TX> ix(px,strides_x); \
      for(;;) { \
        *py OPER##= *ix; \
        int ndim = counter.incr(); \
        if( ndim <= 0 ) \
          break; \
        py++; ix.incr(ndim); \
      } \
    } \
  }

#define implementInPlaceOperator(OPER,OPERNAME,x) \
  defineInPlaceOperTemplate(OPER,OPERNAME,x); \
  Meq::Vells::InPlaceOperPtr Meq::Vells::inplace_##OPERNAME##_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE] = \
    ExpandBinaryLUTMatrix(OPERNAME##_inplace);

DoForAllInPlaceOperators(implementInPlaceOperator,);

// -----------------------------------------------------------------------
// definitions for in-place flag operators
// -----------------------------------------------------------------------

// defines a templated implementation of an in-place flag operator
//    y OPER = x (i.e., +=, -=, etc.)
#define implementInPlaceFlagOperator(OPER,OPERNAME,dum) \
  Meq::Vells & Meq::Vells::operator OPER##= (const Meq::Vells &right) \
  { FailWhen(!isFlags() || !right.isFlags(),"=" #OPER " can only be applied to flags"); \
    Meq::Vells::Strides strides; \
    if( canApplyInPlace(right,strides,#OPERNAME) ) \
    { \
      FT * py = this->begin<FT>(); \
      Meq::Vells::DimCounter counter(*this);  \
      Meq::Vells::ConstStridedIterator<FT> ix(right.begin<FT>(),strides); \
      for(;;) { \
        *py OPER##= *ix; \
        int ndim = counter.incr(); \
        if( ndim <= 0 ) \
          break; \
        py++; ix.incr(ndim); \
      } \
    } \
    else \
     (*this) = (*this) OPER right; \
    return *this; \
  } \
  Meq::Vells & Meq::Vells::operator OPER##= (FT right) \
  { FailWhen(!isFlags(),"=" #OPER " can only be applied to flags"); \
    for( FT *ptr = begin<FT>(); ptr != end<FT>(); ptr++ ) \
       (*ptr) OPER##= right; \
    return *this; \
  }

DoForAllInPlaceFlagOperators(implementInPlaceFlagOperator,);

// -----------------------------------------------------------------------
// definitions for binary functions with flags
// -----------------------------------------------------------------------
// defines a templated implementation of a binary function
//    y = FUNC(a,b,flagmask_a,flagmask_b)
#define defineBinaryFuncWFTemplate(FUNC,FUNCNAME,deflt) \
  template<class TY,class TA,class TB> \
  static void implement_binary_##FUNCNAME (Meq::Vells &y,\
                  const Meq::Vells &a,const Meq::Vells &b, \
                  FT flagmask_a,FT flagmask_b, \
                  const Meq::Vells::Strides strides[4]) \
  { TY *py = y.getStorage(Type2Type<TY>()); \
    const TA *pa = a.begin(Type2Type<TA>()); \
    const TB *pb = b.begin(Type2Type<TB>()); \
    const FT *fa = a.beginFlags(); \
    const FT *fb = b.beginFlags(); \
    Meq::Vells::DimCounter counter(y);  \
    Meq::Vells::ConstStridedIterator<TA> ia(pa,strides[0]); \
    Meq::Vells::ConstStridedIterator<TB> ib(pb,strides[1]); \
    Meq::Vells::ConstStridedIterator<FT> ifa(fa,strides[2]); \
    Meq::Vells::ConstStridedIterator<FT> ifb(fb,strides[3]); \
    for(;;) { \
      if( (*ifa)&flagmask_a ) \
        *py = (*ifb)&flagmask_b ? deflt : *ib; \
      else \
        *py = (*ifb)&flagmask_b ? *ia : FUNC(*ia,*ib); \
      int ndim = counter.incr(); \
      if( ndim <= 0 ) \
        break; \
      py++; ia.incr(ndim); ib.incr(ndim); ifa.incr(ndim); ifb.incr(ndim); \
    } \
  }

defineBinaryFuncWFTemplate(std::min,min,(*ia));
defineErrorFunc2WF(error_binary_min,"min() cannot be applied to complex Meq::Vells");
Meq::Vells::BinaryFuncWFPtr Meq::Vells::binfunc_min_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE] =
    ExpandRealBinaryLUTMatrix(min);

defineBinaryFuncWFTemplate(std::max,max,(*ia));
defineErrorFunc2WF(error_binary_max,"max() cannot be applied to complex Meq::Vells");
Meq::Vells::BinaryFuncWFPtr Meq::Vells::binfunc_max_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE] =
    ExpandRealBinaryLUTMatrix(max);


// -----------------------------------------------------------------------
// definitions for binary functions
// -----------------------------------------------------------------------

// pow() maps directly to the pow call
defineBinaryFuncTemplate(pow,pow,);
Meq::Vells::BinaryOperPtr Meq::Vells::binfunc_pow_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE] = \
    ExpandBinaryLUTMatrix(pow);

// tocomplex()
// define standard template (will only be invoked for real arguments)
defineBinaryFuncTemplate(make_dcomplex,tocomplex,);
// error function for complex arguments
defineErrorFunc2(error_binary_tocomplex,"tocomplex() can only be applied to two real Meq::Vells");
// LUT
Meq::Vells::BinaryOperPtr Meq::Vells::binfunc_tocomplex_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE] = \
    ExpandRealToComplexBinaryLUTMatrix(tocomplex);

// define complex functions missing if std::complex is not being used

// polreptocomplex()
#define polar(x,y) (x)*exp(make_dcomplex(0,y))
// define standard template (will only be invoked for real arguments)
defineBinaryFuncTemplate(polar,polar,);
// error function for complex arguments
defineErrorFunc2(error_binary_polar,"polar() can only be applied to two real Meq::Vells");
// LUT
Meq::Vells::BinaryOperPtr Meq::Vells::binfunc_polar_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE] = \
    ExpandRealToComplexBinaryLUTMatrix(polar);

// posdiff()
// defined for two real arguments only
static inline double posdiff (double x,double y)
{
  double diff = x-y;
  return diff < -M_PI ? diff + M_2_PI : ( diff > M_PI ? diff - M_2_PI : diff );
}
defineBinaryFuncTemplate(posdiff,posdiff,);
defineErrorFunc2(error_binary_posdiff,"posdiff() can only be applied to two real Meq::Vells");
// LUT
Meq::Vells::BinaryOperPtr Meq::Vells::binfunc_posdiff_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE] =
    ExpandRealBinaryLUTMatrix(posdiff);

// atan2()
// defined for two real arguments only
defineBinaryFuncTemplate(atan2,atan2,);
defineErrorFunc2(error_binary_atan2,"atan2() can only be applied to two real Meq::Vells");
// LUT
Meq::Vells::BinaryOperPtr Meq::Vells::binfunc_atan2_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE] =
    ExpandRealBinaryLUTMatrix(atan2);

// fmod()
// defined for two real arguments only
defineBinaryFuncTemplate(fmod,fmod,);
defineErrorFunc2(error_binary_fmod,"fmod() can only be applied to two real Meq::Vells");
// LUT
Meq::Vells::BinaryOperPtr Meq::Vells::binfunc_fmod_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE] =
    ExpandRealBinaryLUTMatrix(fmod);

// remainder()
// defined for two real arguments only
defineBinaryFuncTemplate(remainder,remainder,);
defineErrorFunc2(error_binary_remainder,"remainder() can only be applied to two real Meq::Vells");
// LUT
Meq::Vells::BinaryOperPtr Meq::Vells::binfunc_remainder_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE] =
    ExpandRealBinaryLUTMatrix(remainder);
