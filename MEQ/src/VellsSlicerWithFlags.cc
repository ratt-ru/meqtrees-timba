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
  // fill in vstrides_, fstrides_: the stride of each axis in the vells/flag vells.
  // iterated_ and flag_iterated_ will be true if axis is non-trivial, false if collapsed
  // ns_shape_: this is the non-sliced shape, i.e. 1 for every axis that is
  // sliced (or collapsed) in the input, and >1 for every non-sliced axis.
  ns_shape_.resize(rank);
  for( int i=rank-1; i>=0; i-- )
  {
    vstrides_[i] = vsz;
    vsz *= vs = ( i < int(vshape.size()) ? vshape[i] : 1 );
    iterated_[i] = vs > 1;
    fstrides_[i] = fsz;
    fsz *= fs = ( i < int(fshape.size()) ? fshape[i] : 1 );
    flag_iterated_[i] = fs > 1;
    // if axis is present in either flags or data, copy it to output shape 
    ns_shape_[i] = std::max(vs,fs);
  }
  // now fill our own shape and stride, and the shape and stride
  // of the non-sliced dimensions
  shape_.resize(n);
  flag_shape_.resize(n);
  strides_.resize(n);
  flag_strides_.resize(n);
  for( int i=0; i<n; i++ )
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
      axis_sliced = true;
      iterated_[iaxis] = false;
      shape_[i] = vshape[iaxis];
      strides_[i] = vstrides_[iaxis];
    }
    if( iaxis<int(fshape.size()) && fshape[iaxis] > 1 )
    {
      axis_sliced = true;
      flag_iterated_[iaxis] = false;
      flag_shape_[i] = fshape[iaxis];
      flag_strides_[i] = fstrides_[iaxis];
    }
    // if slicing along this axis, collapse the non-sliced shape 
    if( axis_sliced )
      ns_shape_[iaxis] = 1;
  }
  sizeof_slice_ = shape_.product()*data_size_;
  sizeof_flag_slice_ = flag_shape_.product()*flag_data_size_;
  // now setup a DimCounter over the non-sliced axes
  counter_.init(ns_shape_);
  // setup initial data pointer
  pdata_  = static_cast<char*>(const_cast<void*>(vells.getConstDataPtr()));
  pdata_end_ = pdata_ + vells.size()*data_size_;
  if( fvells0_ )
  {
    pflags_ = static_cast<const char*>(fvells0_->getConstDataPtr());
    pflags_end_ = pflags_ + fvells0_->size()*flag_data_size_;
  }
  else
    pflags_ = pflags_end_ = 0;
  initRefVells();
}

void ConstVellsSlicerWithFlags0::initRefVells ()
{
  FailWhen(pdata_+sizeof_slice_ > pdata_end_,"VellsSlicerWithFlags iterated past end of data. This should never happen: please file a bug report");
  vells_.reference(pdata_,shape_,strides_,*const_cast<const Vells*>(pvells0_));
  if( fvells0_ )
  {
    FailWhen(pflags_+sizeof_flag_slice_ > pflags_end_,"VellsSlicerWithFlags iterated past end of flags. This should never happen: please file a bug report");
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
  bool advanced = false;
  bool flag_advanced = false;
  // loop over every dimension that has been advanced, beginning from the last
  // (the fastest-moving one).
  // dim0 is the first (slowest) dimension to have advanced
  int dim0 = counter_.rank()-ndim;
  for( int i=counter_.rank()-1; i >= dim0; i-- )
  {
    // if a dimension is properly iterated over, then advance the pointer
    // by the given stride. If the dimension then "ticks over" (i>dim0, i.e. is not the last dimension
    // to have been incremented), then reset the pointer back.
    if( iterated_[i] )
    {
      pdata_ += vstrides_[i]*data_size_;
      // if this dimension has "ticked over" (i.e. is not the leftmost to have been incremented),
      // then reset the pointer back to the start of the slice
      if( i>dim0 )
        pdata_ -= vstrides_[i-1]*data_size_;
    }
    if( flag_iterated_[i] )
    {
      pflags_ += fstrides_[i]*flag_data_size_;
      // if this dimension has "ticked over" (i.e. is not the leftmost to have been incremented),
      // then reset the pointer back to the start of the slice
      if( i>dim0 )
        pflags_ -= fstrides_[i-1]*flag_data_size_;
    }
  }
  initRefVells();
  return true;
}


};


