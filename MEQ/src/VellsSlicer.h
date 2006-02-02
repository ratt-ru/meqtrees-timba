#ifndef MEQ_VELLSSLICER_H
#define MEQ_VELLSSLICER_H

#include <MEQ/Vells.h>
    
namespace Meq 
{
  
// A VellsSlicer represents an N-dimensional slice through an M (>=N)
// dimensional Vells. You create a VS from a Vells by specifying the
// axes along which the slice is to be taken. The iterator then points
// at the first slice in the Vells. You can then increment the iterator
// to obtain additional slices, until the Vells is exhausted.
template<typename T,int N>
class ConstVellsSlicer 
{
  public:
      ConstVellsSlicer (const Vells &vells,const int *axes)
      { 
        init(vells,axes); 
      }
  
      ConstVellsSlicer (const Vells &vells,const LoShape &axes)
      { 
        FailWhen(axes.size()!=N,"VellsSlicer: incorrect number of axes supplied");
        init(vells,axes.begin()); 
      }
      
      ConstVellsSlicer (const Vells &vells,const blitz::TinyVector<int,N> &axes)
      { 
        init(vells,&(axes[0])); 
      }
  
      ConstVellsSlicer (const Vells &vells,int axis0,int axis1=-1,int axis2=-1,int axis3=-1)
      {
        STATIC_CHECK(N<=4,VellsSlicer_not_enough_axes_supplied);
        int axes[4] = {axis0,axis1,axis2,axis3 };
        init(vells,axes);
      }

      const blitz::TinyVector<int,N> & shape () const
      { return shape_; }
      
      const blitz::TinyVector<int,N> & strides () const
      { return strides_; }
      
      bool valid () const
      { return counter_.valid(); }
      
      bool incr ();
      
      const T * pdata () const
      { return pdata_; }
      
      const blitz::Array<T,N> array () const
      { return blitz::Array<T,N>(pdata_,shape_,strides_,blitz::neverDeleteData); } 

  protected:
      // init with Vells and N axes
      void init (const Vells &vells,const int *axes);
      // init with arbitrary hypercube
      void init (const T *data,const LoShape &shape,const Vells::Strides &strides,const int *axes);
      
      T * pdata_;
      blitz::TinyVector<int,N> shape_;    // shape of slice
      blitz::TinyVector<int,N> strides_;  // strides of slice
      
      bool sliced_[Axis::MaxAxis];    // flag: true if axis is in slice  
      
      Vells::DimCounter counter_;     // counter for non-sliced dims
      Vells::Strides vstrides_;       // strides of source data
};

template<typename T,int N>
class VellsSlicer : public ConstVellsSlicer<T,N>
{
  public: 
      VellsSlicer (Vells &vells,const int *axes)
      : ConstVellsSlicer<T,N>(vells,axes)
      {}
  
      VellsSlicer (Vells &vells,const LoShape &axes)
      : ConstVellsSlicer<T,N>(vells,axes)
      {}
      
      VellsSlicer (Vells &vells,const blitz::TinyVector<int,N> &axes)
      : ConstVellsSlicer<T,N>(vells,axes)
      {}
  
      VellsSlicer (Vells &vells,int axis0,int axis1=-1,int axis2=-1,int axis3=-1)
        : ConstVellsSlicer<T,N>(vells,axis0,axis1,axis2,axis3)
      {}
      
      T * pdata ()
      { return ConstVellsSlicer<T,N>::pdata_; }
      
      blitz::Array<T,N> array () 
      { return blitz::Array<T,N>(pdata(),ConstVellsSlicer<T,N>::shape(),ConstVellsSlicer<T,N>::strides(),blitz::neverDeleteData); }
      
      blitz::Array<T,N> operator = (const blitz::Array<T,N> &other) 
      { return array() = other; }
};


template<typename T,int N>
void ConstVellsSlicer<T,N>::init (const Vells &vells,const int *axes)
{
  TypeId tid = typeIdOf(T);
  FailWhen(vells.elementType()!=typeIdOf(T),"Can't init a "+tid.toString()+
            " VellsSlicer from a "+vells.elementType().toString()+" Vells");
  int rank = vells.rank();
  FailWhen(N>rank,"rank of VellsSlicer is too high");
  // figure out source strides
  const LoShape &vshape = vells.shape();
  int vsz=1;
  for( int i=rank-1; i>=0; i-- )
  {
    vstrides_[i] = vsz;
    vsz *= vshape[i];
  }
  init(static_cast<const T*>(vells.getConstDataPtr()),vshape,vstrides_,axes);
}

template<typename T,int N>
void ConstVellsSlicer<T,N>::init (const T *data,const LoShape &vshape,const Vells::Strides &vstrides,const int *axes)
{
  memcpy(vstrides_,vstrides,sizeof(vstrides_));
  memset(sliced_,0,sizeof(sliced_));
  // now fill our own shape and stride, and the shape and stride
  // of the non-sliced dimensions
  LoShape ns_shape(vshape);
  int totsize = 1;
  int nsliced = 0;
  for( int i=0; i<N; i++ )
  {
    int iaxis = axes[i];
    FailWhen(iaxis>=Axis::MaxAxis,ssprintf("VellsSlice axis %d out of range",iaxis));
    if( iaxis<int(vshape.size()) )
    {
      sliced_[iaxis] = true;
      shape_[i] = vshape[iaxis];
      strides_[i] = vstrides_[iaxis];
      ns_shape[iaxis] = 1;       
    }
    else
      shape_[i] = strides_[i] = 1;
    totsize *= shape_[i];
  }
  // now setup a DimCounter over the non-sliced axes
  counter_.init(ns_shape);
  // setup initial data pointer
  pdata_ = const_cast<T*>(data);
}

template<typename T,int N>
bool ConstVellsSlicer<T,N>::incr ()
{ 
  // increment counter and return false on end
  int ndim = counter_.incr();
  if( !ndim )
    return false;
  // else we have incremented ndim dimensions (starting from the last)
  // adjust data pointer accordingly
  bool prev_sliced = true;
  for( int i=counter_.rank()-1; i>=counter_.rank()-ndim; i-- )
  {
    // non-sliced axis: increment by stride if prev axis was sliced
    if( !sliced_[i] )
    {
      if( prev_sliced )
        pdata_ += vstrides_[i];
      prev_sliced = false;
    }
    else // sliced axis: decrement by stride to get back to start of previous axis
    {
      if( !prev_sliced ) 
        pdata_ -= vstrides_[i];
      prev_sliced = true;
    }
  }
  return true;
}


}; // namespace Meq

#endif
