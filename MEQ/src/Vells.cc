//# Vells.cc: Values for Meq expressions
//#
//# Copyright (C) 2003
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

// #define MEQVELLS_SKIP_FUNCTIONS 1
#include <MEQ/Vells.h>
#include <Common/Debug.h>
#include <cmath>
#include <complex>

namespace Meq {

Vells::Vells()
: itsRealArray   (0),
  itsComplexArray(0),
  itsNx          (0),
  itsNy          (0),
  itsIsTemp      (false),
  itsIsScalar    (true)
{}

Vells::Vells (double value,bool temp)
: itsRealArray   (0),
  itsComplexArray(0),
  itsNx          (1),
  itsNy          (1),
  itsIsTemp      (temp),
  itsIsScalar    (true)
{
  DataArray *parr;
  itsArray <<= parr = new DataArray(Tpdouble,makeLoShape(1,1));
  parr->getArrayPtr(itsRealArray);
  itsRealArray->data()[0] = value;
}

Vells::Vells (const dcomplex& value,bool temp)
: itsRealArray   (0),
  itsComplexArray(0),
  itsNx          (1),
  itsNy          (1),
  itsIsTemp      (temp),
  itsIsScalar    (true)
{
  DataArray *parr;
  itsArray <<= parr = new DataArray(Tpdcomplex,makeLoShape(1,1));
  parr->getArrayPtr(itsComplexArray);
  itsComplexArray->data()[0] = value;
}

Vells::Vells (double value, int nx, int ny, bool init)
: itsRealArray   (0),
  itsComplexArray(0),
  itsNx          (nx),
  itsNy          (ny),
  itsIsTemp      (false),
  itsIsScalar    (nx==1 && ny==1)
{
  DataArray *parr;
  itsArray <<= parr = new DataArray(Tpdouble,makeLoShape(nx,ny));
  parr->getArrayPtr(itsRealArray);
  if( init )
    *(itsRealArray) = value;
}

Vells::Vells (const dcomplex& value, int nx, int ny, bool init)
: itsRealArray   (0),
  itsComplexArray(0),
  itsNx          (nx),
  itsNy          (ny),
  itsIsTemp      (false),
  itsIsScalar    (nx==1 && ny==1)
{
  DataArray *parr;
  itsArray <<= parr = new DataArray(Tpdcomplex,makeLoShape(nx,ny));
  parr->getArrayPtr(itsComplexArray);
  if( init )
    *(itsComplexArray) = value;
}

Vells::Vells (LoMat_double& array)
: itsRealArray   (0),
  itsComplexArray(0),
  itsNx          (array.extent(blitz::firstDim)),
  itsNy          (array.extent(blitz::secondDim)),
  itsIsTemp      (false),
  itsIsScalar    (itsNx==1 && itsNy==1)
{
  DataArray *parr;
  itsArray <<= parr = new DataArray(array);
  parr->getArrayPtr(itsRealArray);
}

Vells::Vells (LoMat_dcomplex& array)
: itsRealArray   (0),
  itsComplexArray(0),
  itsNx          (array.extent(blitz::firstDim)),
  itsNy          (array.extent(blitz::secondDim)),
  itsIsTemp      (false),
  itsIsScalar    (itsNx==1 && itsNy==1)
{
  DataArray *parr;
  itsArray <<= parr = new DataArray(array);
  parr->getArrayPtr(itsComplexArray);
}

Vells::Vells (DataArray *parr,int flags)
: itsRealArray   (0),
  itsComplexArray(0),
  itsNx          (parr->shape()[0]),
  itsNy          (parr->shape()[1]),
  itsIsTemp      (false),
  itsIsScalar    (itsNx==1 && itsNy==1)
{
  itsArray.attach(parr,flags|DMI::WRITE);
  Assert( parr->rank() == 2 );
  // privatize if so asked
  if( flags&DMI::PRIVATIZE )
    parr = itsArray.privatize(DMI::WRITE|DMI::DEEP).dewr_p();
  // check type
  TypeId tid = parr->elementType();
  if( tid == Tpdouble )
    parr->getArrayPtr(itsRealArray);
  else if( tid == Tpdcomplex )
    parr->getArrayPtr(itsComplexArray);
  else
  {
    Throw("Meq::Vells does not support arrays of type "+tid.toString());
  }
}

Vells::Vells (const Vells& that,int flags)
: SingularRefTarget(),
  itsArray        (that.itsArray,flags|DMI::COPYREF|DMI::WRITE),
  itsRealArray    (0),
  itsComplexArray (0),
  itsNx           (that.itsNx),
  itsNy           (that.itsNy),
  itsIsTemp       (false),
  itsIsScalar     (that.itsIsScalar)
{
  // since array may have been privatized, re-obtain flags
  if( itsArray.valid() )
  {
    if( that.isReal() )
      itsArray().getArrayPtr(itsRealArray);
    else 
      itsArray().getArrayPtr(itsComplexArray);
  }
}

//Vells::clone() const
//{ 
//  return Vells(itsRep->clone()); 
//}

Vells& Vells::operator= (const Vells& that)
{
  if (this != &that) 
  {
    itsArray.copy(that.itsArray,DMI::WRITE);
    itsRealArray    = that.itsRealArray;
    itsComplexArray = that.itsComplexArray;
    itsNx           = that.itsNx;
    itsNy           = that.itsNy;
    itsIsTemp       = that.itsIsTemp;
    itsIsScalar     = that.itsIsScalar;
  }
  return *this;
}

Vells::~Vells()
{
}

Vells & Vells::privatize() 
{
  if( itsArray.valid() )
  {
    DataArray *parr = itsArray.privatize(DMI::WRITE|DMI::DEEP).dewr_p();
    if( isReal() )
      parr->getArrayPtr(itsRealArray);
    else 
      parr->getArrayPtr(itsComplexArray);
  }
  return *this;
}

void Vells::show (std::ostream& os) const
{
  os<<sdebug(2);
  if( !isNull() )
  {
    os<<": ";
    if( itsRealArray )
      os<<*itsRealArray;
    if( itsComplexArray )
      os<<*itsComplexArray;
  }
}

void Vells::copyData (const Vells &other)
{
  if( this != &other && itsArray != other.itsArray )
  {
    FailWhen( nx() != other.nx() || ny() != other.ny() || isReal() != other.isReal(),
        "Meq::Vells size/type mismatch");
    if( isReal() )
      memcpy(realStorage(),other.realStorage(),sizeof(double)*nelements());
    else 
      memcpy(complexStorage(),other.complexStorage(),sizeof(dcomplex)*nelements());
  }
}
  
void Vells::zeroData ()
{
  if( isReal() )
    memset(realStorage(),0,sizeof(double)*nelements());
  else if( isComplex() )
    memset(complexStorage(),0,sizeof(dcomplex)*nelements());
}

inline bool Vells::tryReference (bool real,const Vells &other)
{
  if( other.isTemp() && other.isCongruent(real,itsNx,itsNy) )
  {
    itsArray.copy(other.itsArray,DMI::PRESERVE_RW);
    itsRealArray = other.itsRealArray;
    itsComplexArray = other.itsComplexArray;
    return True;
  }
  return False;
}

// constructor for a temp vells in unary expression
Vells::Vells (const Vells &other,int flags,const std::string &opname)
: itsIsTemp       (true)
{
  // check input if requested by flags
  FailWhen(flags&VF_CHECKREAL && other.isComplex(),
      opname + "() can only be used with a real Meq::Vells");
  FailWhen(flags&VF_CHECKCOMPLEX && other.isReal(),
      opname + "() can only be used with a complex Meq::Vells");
  // determine shape
  if( flags&VF_SCALAR ) // force a scalar Vells
  {
    itsNx = itsNy =1;
    itsIsScalar = True;
  }
  else // else inherit shape from other
  {
    itsNx = other.nx(); itsNy = other.ny();
    itsIsScalar = other.itsIsScalar;
  }
  // determine type
  bool real = flags&VF_REAL ? true : (flags&VF_COMPLEX ? false : other.isReal() );
  // now, if we're still congruent with the other Vells, and it's
  // a temporary, then tryReference() will reuse its array. Else allocate new
  // one.
  if( !tryReference(real,other) )
  {
    DataArray *parr;
    itsArray <<= parr = new DataArray(real?Tpdouble:Tpdcomplex,makeLoShape(itsNx,itsNy));
    if( real )
      { parr->getArrayPtr(itsRealArray); itsComplexArray = 0; }
    else
      { parr->getArrayPtr(itsComplexArray); itsRealArray = 0; }
  }
}

// constructor for a temp vells in binary expression
Vells::Vells (const Vells &a,const Vells &b,int flags,const std::string &opname)
: itsIsTemp       (true)
{
  // check input if requested by flags
  FailWhen(flags&VF_CHECKREAL && (a.isComplex() || b.isComplex()),
      opname + "() can only be used with two real Meq::Vells");
  FailWhen(flags&VF_CHECKCOMPLEX && (a.isReal() || b.isReal()),
      opname + "() can only be used with two complex Meq::Vells");
  // determine shape
  if( flags&VF_SCALAR ) // scalar Vells?
  {
    itsNx = itsNy =1;
    itsIsScalar = True;
  }
  else // else inherit shape of bigger 
  {
    itsNx = a.nx() > b.nx() ? a.nx() : b.nx(); 
    itsNy = a.ny() > b.ny() ? a.ny() : b.ny(); 
    itsIsScalar = ( itsNx == 1 && itsNy == 1);
  }
  // determine type. If not specified via flags, then promote to
  // complex if either arg is complex
  bool real = flags&VF_REAL ? true : 
      (flags&VF_COMPLEX ? false : ( a.isReal() && b.isReal() ) );
  // now, if we're still congruent with the a or b, and it's
  // a temporary, then we can reuse its storage. Else allocate new
  if( !( tryReference(real,a) || tryReference(real,b) ) )
  {
    DataArray *parr;
    itsArray <<= parr = new DataArray(real?Tpdouble:Tpdcomplex,makeLoShape(itsNx,itsNy));
    if( real )
      { parr->getArrayPtr(itsRealArray); itsComplexArray = 0; }
    else
      { parr->getArrayPtr(itsComplexArray); itsRealArray = 0; }
  }
}

string Vells::sdebug (int detail,const string &,const char *nm) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  string out;
  if( detail >= 0 ) // basic detail
  {
    out = ssprintf("%s/%08x",nm?nm:"MeqVells",(void*)this);
  }
  else if( detail >= 1 || detail == -1 ) // basic detail
  {
    if( isNull() )
      append(out,"(null)");
    else
      appendf(out,"%dx%d%s%s",nx(),ny(),isReal()?"R":"C",isTemp()?"t":"");
  }
  else if( detail >= 2 || detail == -2 ) // basic detail
  {
    if( !isNull() )
      appendf(out,"arr:%08x",(void*)itsArray.deref_p());
  }
  return out;
}

} // namespace Meq

// Close the namespace Meq declaration, since we don't want any Meq math
// functions polluting the current scope -- this can confuse the compiler
// in the code below.

// -----------------------------------------------------------------------
// Vells math
// 
// -----------------------------------------------------------------------
using namespace std;
using namespace blitz;

// define a traits-like structure for type conversions:
//    Convert<T>::to_double       // preserves rank
//    Convert<T>::to_dcomplex     // preserves rank
//    Convert<T>::to_scalar       // preserves type
//    Convert<T>::to_matrix       // preserves type
template<class T> struct Convert;
#define defineConversions(from,todbl,tocompl,toscal) \
  template<> struct Convert<from> \
  { \
    typedef todbl to_double; \
    typedef tocompl to_dcomplex; \
    typedef toscal  to_scalar; \
    typedef LoMat_##toscal to_matrix; \
  };
defineConversions(double,double,dcomplex,double);
defineConversions(dcomplex,double,dcomplex,dcomplex);
defineConversions(LoMat_double,LoMat_double,LoMat_dcomplex,double);
defineConversions(LoMat_dcomplex,LoMat_double,LoMat_dcomplex,dcomplex);

// define a traits-like structure for type promotions:
//    Promote<T1,T2>::type returns biggest type
template<class T1,class T2> struct Promote;
template<class T> struct Promote<T,T> { typedef T type; };
#define definePromotion1(a) \
  template<> struct Promote<a,a> { typedef a type; }; \
  template<> struct Promote<a,LoMat_##a> { typedef LoMat_##a type; }; \
  template<> struct Promote<LoMat_##a,a> { typedef LoMat_##a type; }; \
  template<> struct Promote<LoMat_##a,LoMat_##a> { typedef LoMat_##a type; };
definePromotion1(double); 
definePromotion1(dcomplex); 

#define definePromotion2(a,b,to) \
  template<> struct Promote<a,b> { typedef to type; }; \
  template<> struct Promote<b,a> { typedef to type; };
definePromotion2(double,dcomplex,dcomplex);
definePromotion2(double,LoMat_dcomplex,LoMat_dcomplex);
definePromotion2(LoMat_double,dcomplex,LoMat_dcomplex);
definePromotion2(LoMat_double,LoMat_dcomplex,LoMat_dcomplex);

// repeats macro invocation Do(type,x,y) in order of increasing LUT types
#define RepeatForLUTs(Do) \
  Do(double), Do(LoMat_double), \
  Do(dcomplex), Do(LoMat_dcomplex)  

#define RepeatForLUTs1(Do,x) \
  Do(double,x), Do(LoMat_double,x), \
  Do(dcomplex,x), Do(LoMat_dcomplex,x)  
  
#define RepeatForLUTs2(Do,x,y) \
  Do(double,x,y), Do(LoMat_double,x,y), \
  Do(dcomplex,x,y), Do(LoMat_dcomplex,x,y)  

// expands to list of pointers to templated functions
// in order of increasing LUT types, with different funcs for real and scalar
#define ExpandMethodList2(FREAL,FCOMPLEX) \
  { &implement_##FREAL<double>,&implement_##FREAL<LoMat_double>, \
    &implement_##FCOMPLEX<dcomplex>,&implement_##FCOMPLEX<LoMat_dcomplex>, \
  }

// expands to list of pointers to templated functions
#define ExpandMethodList(FUNC) ExpandMethodList2(FUNC,FUNC)

// defines a standard error function (for illegal unary ops)
#define defineErrorFunc(errname,message) \
  static void errname (Meq::Vells &,const Meq::Vells &) \
  { Throw(message); }
  
// defines a standard error function template (for illegal unary ops)
#define defineErrorFuncTemplate(FUNCNAME,message) \
  template<class T> defineErrorFunc(implement_error_##FUNCNAME,message);

template<class T>
static void implement_copy (Meq::Vells &out,const Meq::Vells &in)
{ out.copyData(in); }

template<class T>
static void implement_zero (Meq::Vells &out,const Meq::Vells &)
{ out.zeroData(); }

// -----------------------------------------------------------------------
// definitions for unary operators
// -----------------------------------------------------------------------
#define implementUnaryOperator(OPER,OPERNAME,x) \
  template<class T> \
  static void implement_##OPERNAME (Meq::Vells &out,const Meq::Vells &in) \
  { out.as(Type2Type<T>()) = OPER in.as(Type2Type<T>()); } \
  \
  Meq::Vells::UnaryOperPtr Meq::Vells::unary_##OPERNAME##_lut[VELLS_LUT_SIZE] = \
    ExpandMethodList(OPERNAME);

DoForAllUnaryOperators(implementUnaryOperator,);

// -----------------------------------------------------------------------
// definitions for in-place operators
// -----------------------------------------------------------------------

#define implementInPlaceOperator(OPER,OPERNAME,x) \
  template<class T> \
  static void implement_##OPERNAME (Meq::Vells &out,const Meq::Vells &in) \
  { out.as(Type2Type<T>()) OPER in.as(Type2Type<T>()); } \
  \
  Meq::Vells::UnaryOperPtr Meq::Vells::inplace_##OPERNAME##_lut[VELLS_LUT_SIZE] = \
    ExpandMethodList(OPERNAME);

DoForAllInPlaceOperators(implementInPlaceOperator,);

// -----------------------------------------------------------------------
// definitions for unary functions, Group 1
// for all types, preserves type
// -----------------------------------------------------------------------
inline double sqr (double x) 
{ return x*x; }
inline dcomplex sqr (const dcomplex &x) 
{ return x*x; }

#define defineUnaryFuncTemplate(FUNCNAME,x) \
  template<class T> \
  static void implement_##FUNCNAME (Meq::Vells &out,const Meq::Vells &in) \
  { out.as(Type2Type<T>()) = FUNCNAME(in.as(Type2Type<T>())); } \
    
#define implementUnaryFunc1(FUNCNAME,x) \
  defineUnaryFuncTemplate(FUNCNAME,x) \
  Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_##FUNCNAME##_lut[VELLS_LUT_SIZE] = \
    ExpandMethodList(FUNCNAME);

DoForAllUnaryFuncs1(implementUnaryFunc1,);

// -----------------------------------------------------------------------
// definitions for unary functions, Group 2
// for real Vells only
// -----------------------------------------------------------------------

#define implementUnaryFunc2(FUNCNAME,x) \
  defineUnaryFuncTemplate(FUNCNAME,x) \
  defineErrorFuncTemplate(FUNCNAME,#FUNCNAME "() can only be used with real Meq::Vells") \
  Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_##FUNCNAME##_lut[VELLS_LUT_SIZE] = \
    ExpandMethodList2(FUNCNAME,error_##FUNCNAME);

DoForAllUnaryFuncs2(implementUnaryFunc2,);

// -----------------------------------------------------------------------
// definitions for unary functions, Group 3
// for all types, but always returns a real Vells
// -----------------------------------------------------------------------

// Template for scalars and matrices
// This will work for all complex functions
#define defineUnaryRealFuncTemplate(FUNCNAME,x) \
  template<class T> \
  static void implement_##FUNCNAME (Meq::Vells &out,const Meq::Vells &in) \
    { out.as(Type2Type<typename Convert<T>::to_double>()) = FUNCNAME(in.as(Type2Type<T>())); } \
    
DoForAllUnaryFuncs3(defineUnaryRealFuncTemplate,);
    
// fabs():     use abs for complex and fabs for real
  Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_fabs_lut[VELLS_LUT_SIZE] = \
    ExpandMethodList2(fabs,abs);
  
// abs():      same as fabs
Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_abs_lut[VELLS_LUT_SIZE] = 
    ExpandMethodList2(fabs,abs);

// real()
// Use standard template for complex numbers, and copy for doubles
Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_real_lut[VELLS_LUT_SIZE] = 
    ExpandMethodList2(copy,real);

// imag()
// Use standard template for complex numbers, and zero for doubles
Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_imag_lut[VELLS_LUT_SIZE] = 
    ExpandMethodList2(zero,real);

// norm()
// Use standard template for complex numbers, and sqr for doubles
Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_norm_lut[VELLS_LUT_SIZE] = 
    ExpandMethodList2(sqr,norm);

// arg()
// Provide specialization for doubles, and use template
template<>
static void implement_arg<double> (Meq::Vells &out,const Meq::Vells &in)
{ double x = in.as<double>(); 
  out.as<double>() = x>=0 ? 0 : -M_PI; }
template<>
static void implement_arg<LoMat_double> (Meq::Vells &out,const Meq::Vells &in)
{ const LoMat_double &x = in.as<LoMat_double>(); 
  out.as<LoMat_double>() = where(x>=0, 0 , -M_PI); }
  
Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_arg_lut[VELLS_LUT_SIZE] = 
    ExpandMethodList(arg);

// -----------------------------------------------------------------------
// definitions for unary functions, Group 4
// special treatment
// -----------------------------------------------------------------------

// conj()
// Use standard template for complex numbers, and copy for doubles
defineUnaryFuncTemplate(conj,x) 
Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_conj_lut[VELLS_LUT_SIZE] = 
    ExpandMethodList2(copy,conj);

#define defineUnaryScalarFuncTemplate(FUNCNAME) \
  template<class T> \
  static void implement_##FUNCNAME (Meq::Vells &out,const Meq::Vells &in) \
  { out.as(Type2Type<typename Convert<T>::to_scalar>()) = FUNCNAME(in.as(Type2Type<T>())); }

// some missing implementations
inline double max (double x) { return x; };
inline double min (double x) { return x; };
inline double sum (double x) { return x; };
inline dcomplex sum (const dcomplex &x) { return x; };
inline double mean (double x) { return x; };
inline dcomplex mean (const dcomplex &x) { return x; };
inline double product (double x) { return x; };
inline dcomplex product (const dcomplex &x) { return x; };

defineUnaryScalarFuncTemplate(min);
defineErrorFuncTemplate(min,"min() can only be used with real Meq::Vells") \
defineUnaryScalarFuncTemplate(max);
defineErrorFuncTemplate(max,"max() can only be used with real Meq::Vells") \
defineUnaryScalarFuncTemplate(sum);
defineUnaryScalarFuncTemplate(product);
// implement mean() manually, because blitz refuses to divide 
// dcomplex by int???
template<class T> 
static void implement_mean (Meq::Vells &out,const Meq::Vells &in) \
{ out.as(Type2Type<typename Convert<T>::to_scalar>())
    = sum(in.as(Type2Type<T>()))/double(in.nelements()); }
  
Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_min_lut[VELLS_LUT_SIZE] = 
  ExpandMethodList2(min,error_min);
Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_max_lut[VELLS_LUT_SIZE] = 
  ExpandMethodList2(max,error_max);
Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_mean_lut[VELLS_LUT_SIZE] = 
  ExpandMethodList(mean);
Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_sum_lut[VELLS_LUT_SIZE] = 
  ExpandMethodList(sum);
Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_product_lut[VELLS_LUT_SIZE] = 
  ExpandMethodList(sum);
  

// -----------------------------------------------------------------------
// definitions for binary operators
// -----------------------------------------------------------------------

#define defineBinaryOperTemplate(OPER,OPERNAME) \
  template<class TLeft,class TRight> \
  void implement_binary_##OPERNAME (Meq::Vells &out,const Meq::Vells &left,const Meq::Vells &right) \
  { out.as(Type2Type<typename Promote<TRight,TLeft>::type>()) \
      = left.as(Type2Type<TLeft>()) OPER right.as(Type2Type<TRight>()); }  \
  template<> \
  void implement_binary_##OPERNAME<LoMat_double,LoMat_double> (Meq::Vells &out,const Meq::Vells &left,const Meq::Vells &right) \
  { double *po = out.getStorage<double>(); \
    const double *p1=left.getStorage<double>(),*p2=right.getStorage<double>(); \
    int n = left.nelements(); for( int i=0; i<n; i++ ) po[i] = p1[i] OPER p2[i]; \
  }  \
  template<> \
  void implement_binary_##OPERNAME<double,LoMat_double> (Meq::Vells &out,const Meq::Vells &left,const Meq::Vells &right) \
  { double *po = out.getStorage<double>(); \
    double p1=left.as<double>(); const double *p2=right.getStorage<double>(); \
    int n = left.nelements(); for( int i=0; i<n; i++ ) po[i] = p1 OPER p2[i]; \
  }  \
  template<> \
  void implement_binary_##OPERNAME<LoMat_double,double> (Meq::Vells &out,const Meq::Vells &left,const Meq::Vells &right) \
  { double *po = out.getStorage<double>(); \
    const double *p1=left.getStorage<double>(); double p2=right.as<double>(); \
    int n = left.nelements(); for( int i=0; i<n; i++ ) po[i] = p1[i] OPER p2; \
  }  \
    
// Expands to address of a binary function defined above
#define AddrBinaryFunction(TRight,TLeft,FUNC) \
  &implement_binary_##FUNC<TLeft,TRight>

// Expands to one row of binary LUT table, TLeft is constant, TRight
// goes through all LUT indices
#define BinaryLUTRow(TLeft,FUNC) \
  { RepeatForLUTs2(AddrBinaryFunction,TLeft,FUNC) } 

// Expands to full binary LUT table. 
//    minor (second) index corresponds to LUT index of right argument
//    major (first) index corresponds to LUT index of left argument
#define ExpandBinaryLUTMatrix(FUNC) \
  { RepeatForLUTs1(BinaryLUTRow,FUNC) }

// Implements all binary operators via the template above  
#define implementBinaryOperator(OPER,OPERNAME,dum) \
  defineBinaryOperTemplate(OPER,OPERNAME) \
  Meq::Vells::BinaryOperPtr Meq::Vells::binary_##OPERNAME##_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE] = \
    ExpandBinaryLUTMatrix(OPERNAME);

DoForAllBinaryOperators(implementBinaryOperator,);

// -----------------------------------------------------------------------
// definitions for binary functions
// -----------------------------------------------------------------------

#define defineBinaryFuncTemplate(FUNCTION) \
  template<class TLeft,class TRight> \
  void implement_binary_##OPERNAME (Meq::Vells &out,const Meq::Vells &left,const Meq::Vells &right) \
  { out.as(Type2Type<typename Promote<TRight,TLeft>::type>()) \
      = FUNCTION(left.as(Type2Type<TLeft>()),right.as(Type2Type<TRight>())); } 

// pow() maps directly to the pow call (std or blitz)
template<class TLeft,class TRight> 
void implement_binary_pow (Meq::Vells &out,const Meq::Vells &left,const Meq::Vells &right) 
{ out.as(Type2Type<typename Promote<TRight,TLeft>::type>()) 
    = pow(left.as(Type2Type<TLeft>()),right.as(Type2Type<TRight>())); } 

Meq::Vells::BinaryOperPtr Meq::Vells::binfunc_pow_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE] = \
    ExpandBinaryLUTMatrix(pow);

// tocomplex()
// default template reports error
template<class TLeft,class TRight> 
void implement_binary_tocomplex (Meq::Vells &,const Meq::Vells &,const Meq::Vells &)
{ Throw("tocomplex() can only be used with two real Meq::Vells"); }
// legal specializations for double arguments
template<> 
void implement_binary_tocomplex<double,double> (Meq::Vells &out,const Meq::Vells &left,const Meq::Vells &right)
{ out.as<dcomplex>() = dcomplex(left.as<double>(),right.as<double>()); }
template<> 
void implement_binary_tocomplex<LoMat_double,double> (Meq::Vells &out,const Meq::Vells &left,const Meq::Vells &right)
{ out.as<LoMat_dcomplex>() = 
    zip(left.as<LoMat_double>(),right.as<double>(),dcomplex()); }
template<> 
void implement_binary_tocomplex<double,LoMat_double> (Meq::Vells &out,const Meq::Vells &left,const Meq::Vells &right)
{ out.as<LoMat_dcomplex>() = 
    zip(left.as<double>(),right.as<LoMat_double>(),dcomplex()); }

Meq::Vells::BinaryOperPtr Meq::Vells::binfunc_tocomplex_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE] = \
    ExpandBinaryLUTMatrix(tocomplex);

// posdiff() is defined for two real arguments
// default throws exception
template<class TLeft,class TRight> 
inline void implement_binary_posdiff (Meq::Vells &,const Meq::Vells &,const Meq::Vells &)
{ Throw("posdiff() can only be used with two real Meq::Vells"); }

// define inlined helper template for array posdiff
template<class TLeft,class TRight> 
inline void implement_array_posdiff (Meq::Vells &out,const Meq::Vells &left,const Meq::Vells &right)
{ 
  LoMat_double & diff = out.as(Type2Type<LoMat_double>());  
  diff = left.as(Type2Type<TLeft>()) - right.as(Type2Type<TRight>());
  diff = where( diff < -M_PI , diff + M_2_PI , 
                 where(diff > M_PI , diff - M_2_PI , diff ) );
}
// specialization for two double scalars
template<> 
void implement_binary_posdiff<double,double> (Meq::Vells &out,const Meq::Vells &left,const Meq::Vells &right)
{ 
   double diff = left.as<double>() - right.as<double>();
   out.as<double>() = diff < -M_PI ? diff + M_2_PI :
                            ( diff > M_PI ? diff - M_2_PI : diff );
}
// specializations for arrays
template<>
inline void implement_binary_posdiff<double,LoMat_double> (Meq::Vells &out,const Meq::Vells &left,const Meq::Vells &right)
{ implement_array_posdiff<double,LoMat_double>(out,left,right); }
template<>
inline void implement_binary_posdiff<LoMat_double,double> (Meq::Vells &out,const Meq::Vells &left,const Meq::Vells &right)
{ implement_array_posdiff<LoMat_double,double>(out,left,right); }
template<>
inline void implement_binary_posdiff<LoMat_double,LoMat_double> (Meq::Vells &out,const Meq::Vells &left,const Meq::Vells &right)
{ implement_array_posdiff<LoMat_double,LoMat_double>(out,left,right); }

Meq::Vells::BinaryOperPtr Meq::Vells::binfunc_posdiff_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE] = \
    ExpandBinaryLUTMatrix(posdiff);
    
