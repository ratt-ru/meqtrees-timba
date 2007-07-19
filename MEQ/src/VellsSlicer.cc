//
//% $Id$ 
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


