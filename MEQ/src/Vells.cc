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

//##ModelId=3F86887001D4
Vells::Vells()
: num_elements_ (0),
  element_type_ (0),
  element_size_ (0),
  is_temp_      (false),
  storage_      (0)
{}

void Vells::initArrayPointers (const DataArray *parr,int flags)
{
  // privatize if so asked
  if( flags&DMI::PRIVATIZE )
    parr = array_.privatize(flags|DMI::DEEP).dewr_p();
  shape_ = parr->shape();
  num_elements_ = parr->size();
  element_type_ = parr->elementType();
  element_size_ = parr->elementSize();
  storage_ = const_cast<void*>(parr->getConstDataPtr());
}

//##ModelId=400E5356013E
void Vells::initFromDataArray (const DataArray *parr,int flags)
{
  FailWhen(parr->rank()>Axis::MaxAxis,"can't init Meq::Vells from array: rank too high");
  element_type_ = parr->elementType();
  if( !element_type_  )
  {
    // initializing from empty array makes empty vells
    initArrayPointers(parr,flags);
  }
  else
  {
    FailWhen(element_type_!=Tpdouble && element_type_!=Tpdcomplex,
             "can't init Meq::Vells from array of type "+element_type_.toString());
    initArrayPointers(parr,flags);
  }
}

//##ModelId=3F86887001D5
// creating a Vells from a scalar is "quick" because no DataArray
// is allocated. It will be allocated on-demand later if required
Vells::Vells (double value,bool temp)
: shape_        (1),
  num_elements_ (1),
  element_type_ (Tpdouble),
  element_size_ (sizeof(double)),
  is_temp_      (temp)
{
  *static_cast<double*>(storage_ = scalar_storage_) = value;
}

//##ModelId=3F86887001DC
Vells::Vells (const dcomplex& value,bool temp)
: shape_        (1),
  num_elements_ (1),
  element_type_ (Tpdcomplex),
  element_size_ (sizeof(dcomplex)),
  is_temp_      (temp)
{
  *static_cast<dcomplex*>(storage_ = scalar_storage_) = value;
}

// helper function returns ref to data array. If one of the "quick scalar"
// constructors above was used, we may need to create the array on the fly here
const DataArray::Ref & Vells::getArrayRef (bool write) const
{
  // I didn't want to make array_ and storage_ mutable, since
  // this is the only const method that actually modifies them
  // Hence the const casts
  if( array_.valid() )
  {
    if( write )
      const_cast<Vells*>(this)->makeWritable();
    return array_;
  }
  if( num_elements_ == 1 )
  {
    Vells & self = *const_cast<Vells*>(this);
    DataArray *parr;
    self.array_ <<= parr = new DataArray(element_type_,shape_);
    self.storage_ = parr->getDataPtr();
    memcpy(self.storage_,scalar_storage_,parr->elementSize());
    return array_;
  }
  Throw("taking array ref of empty Vells, or array missing");
}

//##ModelId=3F86887001E3
Vells::Vells (double value,const Vells::Shape &shape, bool init)
: is_temp_ (false)
{
  DataArray *parr;
  array_ <<= parr = new DataArray(Tpdouble,shape);
  initFromDataArray(parr);
  if( init )
  {
    double *begin = static_cast<double*>(storage_),
           *end   = begin + num_elements_;
    while( begin<end )
      *(begin++) = value;
  }
}

Vells::Vells (const dcomplex &value,const Vells::Shape &shape, bool init)
: is_temp_ (false)
{
  DataArray *parr;
  array_ <<= parr = new DataArray(Tpdcomplex,shape);
  initFromDataArray(parr);
  if( init )
  {
    dcomplex *begin = static_cast<dcomplex*>(storage_),
             *end   = begin + num_elements_;
    while( begin<end )
      *(begin++) = value;
  }
}

//##ModelId=3F8688700216
Vells::Vells (DataArray *parr,int flags)
: is_temp_ (false)
{
  array_.attach(parr,(flags&~DMI::READONLY)|DMI::WRITE);
  initFromDataArray(parr,flags);
}

//##ModelId=3F868870021C
Vells::Vells (const DataArray *parr,int flags)
: is_temp_ (false)
{
  array_.attach(parr,(flags&~DMI::WRITE)|DMI::READONLY);
  initFromDataArray(parr,flags);
}

//##ModelId=3F8688700223
Vells::Vells (const DataArray::Ref::Xfer &ref)
: is_temp_ (false)
{
  array_ = ref;
  initFromDataArray(array_.deref_p());
}

void Vells::clone (const Vells &other,int flags)
{
  // Assigning or copying a temp vells always yields a non-temp vells.
  // This means that temp Vells can only occur as intermediate objects
  // in Vells math expressions (unless created/set as temp explicitly).
  is_temp_ = false;
  shape_   = other.shape_;
  num_elements_ = other.num_elements_;
  element_type_ = other.element_type_;
  element_size_ = other.element_size_;
  // other vells has a real array attached
  if( other.array_.valid() )
  {
    if( flags&DMI::PRIVATIZE )
      flags = (flags&~DMI::READONLY)|DMI::WRITE;
    else
      flags = (flags&~DMI::WRITE)|DMI::READONLY;
    array_.copy(other.array_,flags);
    storage_ = const_cast<void*>( array_->getConstDataPtr() );
  }
  else   // no array, must be empty or using temp scalar storage
  {
    array_.detach();
    if( num_elements_ == 1 )
    {
      Assert(other.storage_ == other.scalar_storage_);
      storage_ = scalar_storage_;
      memcpy(storage_,other.storage_,element_size_);
    }
    else
    {
      Assert(!num_elements_);
      storage_ = 0;
    }
  }
  dataflags_.copy(other.dataflags_,flags);
}

  //##ModelId=3F868870022A
Vells::Vells (const Vells& other,int flags)
: SingularRefTarget()
{
  clone(other,flags);
}

//##ModelId=3F868870023B
Vells& Vells::operator= (const Vells& other)
{
  if (this != &other) 
    clone(other);
  else
    is_temp_ = false;
  return *this;
}

//##ModelId=3F8688700238
Vells::~Vells()
{
}

void Vells::privatize (int flags,int depth)
{
  if( array_.valid() )
  {
    DataArray & arr = array_.privatize(flags,depth).dewr();
    storage_ = const_cast<void*>(arr.getConstDataPtr());
  }
}

// void Vells::makeWritable () 
// { 
//   if( array_.valid() && !array_.isWritable() )
//   {
//     array_.privatize(DMI::WRITE);
//     storage_ = array_().getDataPtr();
//   }
// }
// 
// 
//##ModelId=3F8688700282
void Vells::show (std::ostream& os) const
{
  os<<sdebug(2);
}

//##ModelId=400E53560110
void Vells::copyData (const Vells &other)
{
  makeWritable();
  if( this != &other && array_ != other.array_ )
  {
    FailWhen( shape() != other.shape() || elementType() != other.elementType(),
        "Meq::Vells size/type mismatch");
    memcpy(storage_,other.storage_,nelements()*elementSize());
  }
}
  
//##ModelId=400E5356011C
void Vells::zeroData ()
{
  makeWritable();
  memcpy(storage_,0,nelements()*elementSize());
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
inline bool Vells::tryReference (const Vells &other)
{
  // the 'other' array can be reused if it's a temp, it has the
  // same size and type, and it's writable
  if( other.isTemp() && 
      other.array_.valid() &&
      elementType() == other.elementType() &&
      shape() == other.shape() )
  {
    // if other is not writable, we can still make it so by privatizing its 
    // array for writing if it is the sole referrer
    if( !other.array_.isWritable() )
    {
      if( other.array_->refCount() > 1 )
        return false;
      const_cast<Vells&>(other).privatize(DMI::WRITE);
    }
    array_.copy(other.array_,DMI::PRESERVE_RW);
    storage_ = other.storage_;
    return true;
  }
  return false;
}

void Vells::setSizeType (int flags,bool arg_is_complex)
{
  if( flags&VF_COMPLEX || (!flags&VF_REAL && arg_is_complex) )
  {
    element_type_ = Tpdcomplex;
    element_size_ = sizeof(dcomplex);
  }
  else
  {
    element_type_ = Tpdouble;
    element_size_ = sizeof(double);
  }
}

// constructor for a temp vells in unary expression
//##ModelId=3F8688700231
Vells::Vells (const Vells &other,int flags,const std::string &opname)
: is_temp_ (true)
{
  // check input if requested by flags
  FailWhen(flags&VF_CHECKREAL && other.isComplex(),
      opname + "() can only be used with a real Meq::Vells");
  FailWhen(flags&VF_CHECKCOMPLEX && other.isReal(),
      opname + "() can only be used with a complex Meq::Vells");
  // determine shape
  if( flags&VF_SCALAR ) // force a scalar Vells
  {
    shape_ = LoShape(1);
    num_elements_ = 1;
  }
  else // else inherit shape from other
  {
    shape_ = other.shape();
    num_elements_ = other.num_elements_;
  }
  // determine type
  setSizeType(flags,other.isComplex());
  // now, if we're still congruent with the other Vells, and it's
  // a temporary, then tryReference() will reuse its array. Else allocate new
  // one.
  if( !tryReference(other) )
  {
    DataArray *parr;
    array_ <<= parr = new DataArray(element_type_,shape_);
    storage_ = parr->getDataPtr();
  }
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
//     DataArray *parr;
//     array_ <<= parr = new DataArray(element_type_,shape_);
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

// computes shape of output, plus strides required
void Vells::computeStrides (Vells::Shape &shape,
                            int strides_a[],int strides_b[],
                            const Vells &a,const Vells &b,
                            const string &opname)
{
  int rnk = max(a.rank(),b.rank());
  shape.resize(rnk);
  // Loop over all axes to determine output shape and input strides for iterators.
  int tota=1,totb=1;
  bool dega=true,degb=true;
  for( int i=0; i<rnk; i++ ) 
  {
    // get size along each axis -- if past the last rank, use 1
    int sza = i < a.rank() ? a.shape_[i] : 1;
    int szb = i < b.rank() ? b.shape_[i] : 1;
    bool a_big = sza>1;
    bool b_big = szb>1;
    if( a_big && b_big && sza != szb )
    {
      Throw1("arguments to "+opname+" have incompatible shapes");
    }
    // set strides
    strides_a[i] = a_big ? normalAxis(tota,dega) : degenerateAxis(tota,dega);
    strides_b[i] = b_big ? normalAxis(totb,degb) : degenerateAxis(totb,degb);
    // set output shape
    shape[i] = std::max(sza,szb); 
    // increase element counts
    tota *= sza;
    totb *= szb;
  }
}

// Constructor for a temp vells for the result of a binary expression. 
// The shape of the result is the maximum of the argument shapes;
// the constructor will also compute strides for the arguments.
//##ModelId=400E53560174
Vells::Vells (const Vells &a,const Vells &b,int flags,
              int strides_a[],int strides_b[],const std::string &opname)
: is_temp_ (true)
{
  // check input if requested by flags
  FailWhen(flags&VF_CHECKREAL && (a.isComplex() || b.isComplex()),
      opname + "() can only be applied to two real Meq::Vells");
  FailWhen(flags&VF_CHECKCOMPLEX && (a.isReal() || b.isReal()),
      opname + "() can only be applied to two complex Meq::Vells");
  // determine shape and strides 
  computeStrides(shape_,strides_a,strides_b,a,b,opname);
  num_elements_ = shape_.product();
  // determine type. 
  setSizeType(flags,a.isComplex() || b.isComplex());
  // now, if we're still congruent with the a or b, and it's
  // a temporary, then we can reuse its storage. Else allocate new
  if( !( tryReference(a) || tryReference(b) ) )
  {
    if( num_elements_ == 1 ) // use scalar storage
      storage_ = scalar_storage_;
    else // allocate array
    {
      DataArray *parr;
      array_ <<= parr = new DataArray(element_type_,shape_);
      storage_ = parr->getDataPtr();
    }
  }
}

// Determines if other Vells can be applied to us in-place (i.e. += and such).
// This is only possible if our type and shape are not lower-ranked.
// If operation is not applicable, returns False.
// If it is, returns True and populates strides[] with the incremental strides
// which need to be applied to other.
bool Vells::canApplyInPlace (const Vells &other,int strides[],const std::string &opname)
{
  // try the simple tests first
  if( (isReal() && other.isComplex()) || (rank() < other.rank()) )
    return false;
  // Loop over all axes to determine if shapes match. Our rank is higher thanks
  // to test above
  int  total=1;
  bool deg=true;
  for( int i=0; i<rank(); i++ ) 
  {
    // get size along each axis -- if past the last rank, use 1
    int sz_ours  = shape_[i];
    int sz_other = i < other.rank() ? other.shape_[i] : 1;
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
string Vells::sdebug (int detail,const string &,const char *nm) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  string out;
  if( detail >= 0 ) // basic detail
  {
    out = ssprintf("%s/%08x",nm?nm:"MeqVells",(void*)this);
    if( isTemp() )
      out += "/tmp";
  }
  else if( detail >= 1 || detail == -1 ) // basic detail
  {
    if( isNull() )
      append(out,"(null)");
    else
    {
      out += " ";
      for( uint i=0; i<shape_.size(); i++ )  
        out += ssprintf("%s%d",i?"x":"",shape_[i]);
      out += isReal()?"R":"C";
    }
  }
  else if( detail >= 2 || detail == -2 ) // basic detail
  {
    if( !isNull() )
      appendf(out,"arr:%08x",(void*)array_.deref_p());
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
// defines a standard error function (for illegal binary ops)
#define defineErrorFunc2(errname,message) \
  static void errname (Meq::Vells &,const Meq::Vells &,const Meq::Vells &,const int [],const int []) \
  { Throw(message); }
  
// defines a standard error function template (for illegal unary ops)
#define defineErrorFuncTemplate(FUNCNAME,message) defineErrorFuncTemplate2(FUNCNAME,message)
#define defineErrorFuncTemplate2(FUNCNAME,message) \
  template<class T1,class T2> defineErrorFunc(implement_error_##FUNCNAME,message);
// defines a standard error function template (for illegal binary ops)
#define defineErrorFuncTemplate3(FUNCNAME,message) \
  template<class T1,class T2,class T3> defineErrorFunc(implement_error_##FUNCNAME,message);

template<class TY,class TX>
static void implement_copy (Meq::Vells &out,const Meq::Vells &in)
{ out.copyData(in); }

template<class TY,class TX>
static void implement_zero (Meq::Vells &out,const Meq::Vells &)
{ out.zeroData(); }


// Helper class implementing iteration over a strided velss
template<class T>
class ConstStridedIterator
{
  protected:
    const T   *ptr;
    const int *strides;
  
  public:
    ConstStridedIterator (const T * p,const int str[])
    : ptr(p),strides(str)
    {}
  
    ConstStridedIterator (const Meq::Vells &vells,const int str[])
    : ptr(vells.getStorage(Type2Type<T>())),strides(str)
    {}
    
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

// Helper class implementing iteration over an N-dimensional shape
class DimCounter 
{
  protected:
    const Meq::Vells::Shape &shape;
    int   maxdim;
    int   counter[Meq::Axis::MaxAxis];
  
  public:
      DimCounter (const Meq::Vells &vells)
        : shape(vells.shape()),maxdim(vells.rank())
      { memset(counter,0,sizeof(int)*maxdim); }
  
      // increments counter. Returns number of dimensions incremented
      // (i.e. 1 most of the time, when only the first dimension is being
      // incremented, 2 when the second one is incremented as well, etc.),
      // or 0 when finished
      int incr ()
      {
        int idim = 0;
        while( ++counter[idim] >= shape[idim] )
        {
          counter[idim] = 0;
          if( ++idim >= maxdim )
            return 0;
        }
        return idim+1;
      }
};

// defines a templated implementation of an unary function
//    y = FUNC(x)
#define defineUnaryOperTemplate(FUNC,FUNCNAME,dum) \
  template<class TY,class TX> \
  static void implement_##FUNCNAME (Meq::Vells &y,const Meq::Vells &x) \
  { const TX *px = x.getStorage(Type2Type<TX>()); \
    TY *py = y.getStorage(Type2Type<TY>()), \
       *py_end = py + y.nelements();  \
    for( ; py < py_end; px++,py++ ) \
      *py = FUNC(*px); \
  }

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

// -----------------------------------------------------------------------
// definitions for unary operators
// defined for all types, preserves type
// -----------------------------------------------------------------------
#define implementUnaryOperator(OPER,OPERNAME,x) \
  defineUnaryOperTemplate(OPER,OPERNAME,x); \
  Meq::Vells::UnaryOperPtr Meq::Vells::unary_##OPERNAME##_lut[VELLS_LUT_SIZE] = \
    ExpandMethodList(OPERNAME);

DoForAllUnaryOperators(implementUnaryOperator,);

// -----------------------------------------------------------------------
// definitions for unary functions, Group 1
// defined for all types, preserves type
// -----------------------------------------------------------------------
template<class T> inline T sqr (T x) { return x*x; }
template<class T> inline T pow2(T x) { return x*x; }
template<class T> inline T pow3(T x) { return x*x*x; }
template<class T> inline T pow4(T x) { T t1 = x*x; return t1*t1; }    
template<class T> inline T pow5(T x) { T t1 = x*x; return t1*t1*x; }  
template<class T> inline T pow6(T x) { T t1 = x*x*x; return t1*t1; }  
template<class T> inline T pow7(T x) { T t1 = x*x; return t1*t1*t1*x; } 
template<class T> inline T pow8(T x) { T t1 = x*x, t2=t1*t1; return t2*t2; }

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
    ExpandMethodList2_FixOut(zero,real,double);

// norm()
// Use standard template for complex numbers, and sqr for doubles
Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_norm_lut[VELLS_LUT_SIZE] = 
    ExpandMethodList2_FixOut(sqr,norm,double);

// version of arg() for doubles
static inline double arg (double x) 
{ return x>=0 ? 0 : -M_PI; }
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
// Defines a templated implementation of an unary reduction function 
// which computes: y=x(0), then y=FUNC(y,x(i)) for all i, and returns y
// This is a helper template for all reduction functions, since it returns
// y by value rather than storing it in a Vells.
#define defineReductionFuncImpl(FUNC,FUNCNAME,dum) \
  template<class TY,class TX> \
  static inline TY implement_##FUNCNAME##_impl (const Meq::Vells &x, \
    Type2Type<TY> = Type2Type<TY>(),Type2Type<TX> = Type2Type<TX>() )  \
  { const TX *px = x.getStorage(Type2Type<TX>()), \
             *px_end = px + x.nelements(); \
    TY y0 = *px++; \
    for(; px < px_end; px++) \
      y0 = FUNC(y0,*px); \
    return y0; \
  }
  
// Defines a templated implementation of an unary reduction function 
// which computes: y=x(0), then y=FUNC(y,x(i)) for all i, and returns y
// This is a helper template for all reduction functions, since it returns
// y by value rather than storing it in a Vells.
#define defineAxisReductionFuncImpl(FUNC,FUNCNAME,dum) \
  template<class TY,class TX> \
  static void implement_##FUNCNAME##_impl (Meq::Vells &y,const Meq::Vells &x,int axis) \
    Type2Type<TY> = Type2Type<TY>(),Type2Type<TX> = Type2Type<TX>() )  \
  { const TX *px = x.getStorage(Type2Type<TX>()), \
             *px_end = px + x.nelements(); \
    TY y0 = *px++; \
    for(; px < px_end; px++) \
      y0 = FUNC(y0,*px); \
    return y0; \
  }

// defines a templated implementation of an unary reduction function such
// as min() or max(), which works by applying y=FUNC(y,x) to all elements
#define defineReductionFuncTemplate(FUNC,dum) \
  defineReductionFuncImpl(FUNC,FUNC,dum); \
  template<class TY,class TX> \
  static void implement_##FUNC (Meq::Vells &y,const Meq::Vells &x) \
  { *(y.getStorage(Type2Type<TY>())) = \
    implement_##FUNC##_impl(x,Type2Type<TY>(),Type2Type<TX>()); }

defineReductionFuncTemplate(min,);
defineErrorFuncTemplate(min,"min() can only be applied to a real Meq::Vells");
defineReductionFuncTemplate(max,);
defineErrorFuncTemplate(max,"max() can only be applied to a real Meq::Vells");
Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_min_lut[VELLS_LUT_SIZE] = 
  ExpandMethodList2(min,error_min);
Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_max_lut[VELLS_LUT_SIZE] = 
  ExpandMethodList2(max,error_max);

// implement a DOSUM function which sums up a complete Vells. This
// sum is unnormalized because it does not take into account scalar axes
#define DOSUM(x,y) ((x)+(y))
defineReductionFuncImpl(DOSUM,DOSUM,x);

template<class TY,class TX> 
static void implement_mean (Meq::Vells &y,const Meq::Vells &x) 
{ 
  TY y0 = implement_DOSUM_impl(x,Type2Type<TY>(),Type2Type<TX>());
  double nel = x.nelements(); 
  *( y.getStorage(Type2Type<TY>()) ) = y0 / nel; 
}
Meq::Vells::UnaryOperPtr Meq::Vells::unifunc_mean_lut[VELLS_LUT_SIZE] = 
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
static void implement_sum (Meq::Vells &y,const Meq::Vells &x,const Meq::Vells::Shape &shape) 
{
  TY y0 = implement_DOSUM_impl(x,Type2Type<TY>(),Type2Type<TX>());
  double renorm = shape.product()/x.nelements();
  *( y.getStorage(Type2Type<TY>()) ) = y0 * renorm;
}

#define DOPROD(x,y) ((x)*(y))
defineReductionFuncImpl(DOPROD,DOPROD,x);
template<class TY,class TX> 
static void implement_product (Meq::Vells &y,const Meq::Vells &x,const Meq::Vells::Shape &shape) 
{ 
  TY y0 = implement_DOPROD_impl(x,Type2Type<TY>(),Type2Type<TX>());
  *( y.getStorage(Type2Type<TY>()) ) = std::pow(y0,shape.product()/x.nelements());
}

static void implement_nelements (Meq::Vells &y,const Meq::Vells &,const Meq::Vells::Shape &shape) 
{ 
  *(y.getStorage<double>()) = shape.product();
}

Meq::Vells::UnaryWithShapeOperPtr Meq::Vells::unifunc_sum_lut[VELLS_LUT_SIZE] = 
  ExpandMethodList(sum);
Meq::Vells::UnaryWithShapeOperPtr Meq::Vells::unifunc_product_lut[VELLS_LUT_SIZE] = 
  ExpandMethodList(product);
Meq::Vells::UnaryWithShapeOperPtr Meq::Vells::unifunc_nelements_lut[VELLS_LUT_SIZE] = 
  { implement_nelements,implement_nelements };
  

// -----------------------------------------------------------------------
// definitions for binary operators
// -----------------------------------------------------------------------
// defines a templated implementation of a binary function
//    y = FUNC(a,b)
#define defineBinaryFuncTemplate(FUNC,FUNCNAME,dum) \
  template<class TY,class TA,class TB> \
  static void implement_binary_##FUNCNAME (Meq::Vells &y,\
                  const Meq::Vells &a,const Meq::Vells &b,\
                  const int strides_a[],const int strides_b[]) \
  { TY *py = y.getStorage(Type2Type<TY>()); \
    const TA *pa = a.getStorage(Type2Type<TA>()); \
    const TB *pb = b.getStorage(Type2Type<TB>()); \
    if( a.isScalar() && b.isScalar() ) \
      *py = FUNC(*pa,*pb); \
    else { \
      DimCounter counter(y);  \
      ConstStridedIterator<TA> ia(pa,strides_a); \
      ConstStridedIterator<TB> ib(pb,strides_b); \
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
// definitions for in-place operators
// -----------------------------------------------------------------------

//****************** think how to do this properly
// problem is, we may need to reformat Y if X has variability along an axis
// that is constant in Y. In this case, perhaps explicitly remap y OP= X
// to y = y OP x? 

// defines a templated implementation of an in-place operator
//    y OPER = x (i.e., +=, -=, etc.)
// this version only called when the variability of y is not less than that of x
#define defineInPlaceOperTemplate(OPER,OPERNAME,dum) \
  template<class TOut,class TY,class TX> \
  static void implement_binary_##OPERNAME##_inplace (Meq::Vells &y,\
                  const Meq::Vells &x,\
                  const int strides_x[]) \
  { TOut *py = y.getStorage(Type2Type<TOut>()); \
    const TX *px = x.getStorage(Type2Type<TX>()); \
    if( y.isScalar() && x.isScalar() ) \
      *py OPER##= *px; \
    else { \
      DimCounter counter(y);  \
      ConstStridedIterator<TX> ix(px,strides_x); \
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
// definitions for binary functions
// -----------------------------------------------------------------------

// pow() maps directly to the pow call 
defineBinaryFuncTemplate(pow,pow,);
Meq::Vells::BinaryOperPtr Meq::Vells::binfunc_pow_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE] = \
    ExpandBinaryLUTMatrix(pow);

// tocomplex()
// define standard template (will only be invoked for real arguments)
defineBinaryFuncTemplate(dcomplex,tocomplex,);
// error function for complex arguments
defineErrorFunc2(error_binary_tocomplex,"tocomplex() can only be applied to two real Meq::Vells"); 
// LUT 
Meq::Vells::BinaryOperPtr Meq::Vells::binfunc_tocomplex_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE] = \
    ExpandRealToComplexBinaryLUTMatrix(tocomplex);

// polreptocomplex()
#define polar(x,y) (x)*exp(dcomplex(0,y))
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
defineErrorFunc2(error_binary_atan2,"atan2() can only be applied to two real Meq::Vells "); 
// LUT 
Meq::Vells::BinaryOperPtr Meq::Vells::binfunc_atan2_lut[VELLS_LUT_SIZE][VELLS_LUT_SIZE] = 
    ExpandRealBinaryLUTMatrix(atan2);
