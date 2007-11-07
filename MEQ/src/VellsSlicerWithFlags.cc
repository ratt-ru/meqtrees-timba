//
//% $Id: VellsSlicer.cc 5418 2007-07-19 16:49:13Z oms $ 
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

#define MEQVELLS_SKIP_FUNCTIONS 1
#include <MEQ/VellsSlicerWithFlags.h>
    
    
namespace Meq 
{

void ConstVellsSlicerWithFlags0::init (const Vells &vells,const int *axes,int n)
{
  // if flags not attached, use the static "null" flags
  fvells0_ = vells.hasDataFlags() ? &(vells.dataFlags()) : 0;
  int rank = std::max(vells.rank(),(fvells0_ ? fvells0_->rank() : 0));
  FailWhen(n>rank,"rank of VellsSlicer is too high");
  // init internals
  pvells0_ = const_cast<Vells*>(&vells);
  data_size_ = vells.elementSize();
  flag_data_size_ = sizeof(VellsFlagType);
  // figure out source strides
  const LoShape &vshape = vells.shape();
  // if no flags, then fshape is empty, then nothing is done about flags
  // later on...
  const LoShape &fshape = fvells0_ ? fvells0_->shape() : LoShape();
  int vsz=1,fsz=1,vs,fs;
  ns_shape_.resize(rank);
  for( int i=rank-1; i>=0; i-- )
  {
    vstrides_[i] = vsz;
    vsz *= vs = ( i < int(vshape.size()) ? vshape[i] : 1 );
    fstrides_[i] = fsz;
    fsz *= fs = ( i < int(fshape.size()) ? fshape[i] : 1 );
    // if axis is present in either flags or data, copy it to output shape 
    ns_shape_[i] = std::max(vs,fs);
  }
  // reset the "sliced" flags
  memset(sliced_,0,sizeof(sliced_));
  memset(flag_sliced_,0,sizeof(flag_sliced_));
  // now fill our own shape and stride, and the shape and stride
  // of the non-sliced dimensions
  shape_.resize(n);
  flag_shape_.resize(n);
  strides_.resize(n);
  flag_strides_.resize(n);
  for( int i=0; i<rank; i++ )
  {
    shape_[i] = flag_shape_[i] = strides_[i] = flag_strides_[i] = 1;
  }
  for( int i=0; i<n; i++ )
  {
    int iaxis = axes[i];
    FailWhen(iaxis>=Axis::MaxAxis,ssprintf("VellsSlice axis %d out of range",iaxis));
    int axis_sliced = false;
    if( iaxis<int(vshape.size()) && vshape[iaxis] > 1 )
    {
      sliced_[iaxis] = axis_sliced = true;
      shape_[i] = vshape[iaxis];
      strides_[i] = vstrides_[iaxis];
    }
    if( iaxis<int(fshape.size()) && fshape[iaxis] > 1 )
    {
      flag_sliced_[iaxis] = axis_sliced = true;
      flag_shape_[i] = fshape[iaxis];
      flag_strides_[i] = fstrides_[iaxis];
    }
    // if slicing along this axis, collapse the non-sliced shape 
    if( axis_sliced )
      ns_shape_[iaxis] = 1;
  }
  // now setup a DimCounter over the non-sliced axes
  counter_.init(ns_shape_);
  // setup initial data pointer
  pdata_  = static_cast<char*>(const_cast<void*>(vells.getConstDataPtr()));
  pflags_ = fvells0_ ? static_cast<const char*>(fvells0_->getConstDataPtr()) : 0;
  initRefVells();
}

void ConstVellsSlicerWithFlags0::initRefVells ()
{
  vells_.reference(pdata_,shape_,strides_,*const_cast<const Vells*>(pvells0_));
  if( fvells0_ )
  {
    Vells::Ref flags;
    flags <<= new Vells;
    flags().reference(pflags_,flag_shape_,flag_strides_,*fvells0_);
    vells_.setDataFlags(flags);
  }
}

bool ConstVellsSlicerWithFlags0::incr ()
{ 
  // increment counter and return false on end
  int ndim = counter_.incr();
  if( !ndim )
    return false;
  // else we have incremented ndim dimensions (starting from the last)
  // adjust data pointer accordingly
  bool prev_sliced = true;
  bool prev_flag_sliced = true;
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
    if( fvells0_ )
    {
      // non-sliced flag axis: increment by stride if prev axis was sliced
      if( !flag_sliced_[i] )
      {
        if( prev_flag_sliced )
          pflags_ += fstrides_[i]*flag_data_size_;
        prev_flag_sliced = false;
      }
      else // sliced flag axis: decrement by stride to get back to start of previous axis
      {
        if( !prev_flag_sliced ) 
          pflags_ -= fstrides_[i]*flag_data_size_;
        prev_flag_sliced = true;
      }
    }
  }
  initRefVells();
  return true;
}


};


