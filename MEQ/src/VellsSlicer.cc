#define MEQVELLS_SKIP_FUNCTIONS 1
#include <MEQ/VellsSlicer.h>
    
    
namespace Meq 
{
  
void ConstVellsSlicer0::init (const Vells &vells,bool writable,const int *axes,int n)
{
  int rank = vells.rank();
  FailWhen(n>rank,"rank of VellsSlicer is too high");
  // init internals
  writable_ = writable;
  pvells0_ = const_cast<Vells*>(&vells);
  data_size_ = vells.elementSize();
  // figure out source strides
  const LoShape &vshape = vells.shape();
  int vsz=1;
  for( int i=rank-1; i>=0; i-- )
  {
    vstrides_[i] = vsz;
    vsz *= vshape[i];
  }
  memset(sliced_,0,sizeof(sliced_));
  // now fill our own shape and stride, and the shape and stride
  // of the non-sliced dimensions
  ns_shape_ = vshape;
  shape_.resize(n);
  strides_.resize(n);
  int totsize = 1;
  int nsliced = 0;
  for( int i=0; i<n; i++ )
  {
    int iaxis = axes[i];
    FailWhen(iaxis>=Axis::MaxAxis,ssprintf("VellsSlice axis %d out of range",iaxis));
    if( iaxis<int(vshape.size()) )
    {
      sliced_[iaxis] = true;
      shape_[i] = vshape[iaxis];
      strides_[i] = vstrides_[iaxis];
      // collapse this axis in the non-sliced shape
      if( iaxis == int(ns_shape_.size())-1 )
        ns_shape_.resize(iaxis);
      else
        ns_shape_[iaxis] = 1;       
    }
    else
      shape_[i] = strides_[i] = 1;
    totsize *= shape_[i];
  }
  // now setup a DimCounter over the non-sliced axes
  counter_.init(ns_shape_);
  // setup initial data pointer
  pdata_ = static_cast<char*>(const_cast<void*>(vells.getConstDataPtr()));
  // setup reference Vells
  initRefVells();
}

void ConstVellsSlicer0::initRefVells ()
{
  if( writable_ )
    vells_.reference(pdata_,shape_,strides_,*pvells0_);
  else
    vells_.reference(const_cast<const char*>(pdata_),shape_,strides_,*const_cast<const Vells*>(pvells0_));
}

bool ConstVellsSlicer0::incr ()
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
        pdata_ += vstrides_[i]*data_size_;
      prev_sliced = false;
    }
    else // sliced axis: decrement by stride to get back to start of previous axis
    {
      if( !prev_sliced ) 
        pdata_ -= vstrides_[i]*data_size_;
      prev_sliced = true;
    }
  }
  initRefVells();
  return true;
}


};


