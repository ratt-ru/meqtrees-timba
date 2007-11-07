//
//% $Id: VellsSlicer.h 5418 2007-07-19 16:49:13Z oms $ 
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

#ifndef MEQ_VELLSSLICERWITHFLAGS_H
#define MEQ_VELLSSLICERWITHFLAGS_H

#include <MEQ/Vells.h>
    
namespace Meq 
{

// A VellsSlicer represents an N-dimensional slice through an M (>=N)
// dimensional Vells. You create a VS from a Vells by specifying the
// axes along which the slice is to be taken. The iterator then points
// at the first slice in the Vells. You can then increment the iterator
// to obtain additional slices, until the Vells is exhausted.
//
// The Slicer0 class is non-templated, it provides access to the slice
// via a Vells object (which encapsulates type and rank information). This
// is useful when all you want to do with the slices is VellsMath.
// The Slicer classes are templated on element type and rank, and provide
// access to the slice as a blitz Array

class ConstVellsSlicerWithFlags0   
{
  public:
      ConstVellsSlicerWithFlags0 ()
      {}
  
      ConstVellsSlicerWithFlags0 (const Vells &vells,const int *axes,int naxes)
      { 
        init(vells,axes,naxes); 
      }
  
      ConstVellsSlicerWithFlags0 (const Vells &vells,const LoShape &axes)
      { 
        init(vells,&(axes[0]),axes.size()); 
      }
      
      template<int N>
      ConstVellsSlicerWithFlags0 (const Vells &vells,const blitz::TinyVector<int,N> &axes)
      { 
        init(vells,&(axes[0]),N); 
      }
  
      ConstVellsSlicerWithFlags0 (const Vells &vells,int axis0,int axis1=-1,int axis2=-1,int axis3=-1)
      {
        int N=1;
        if( axis3 >= 0 ) 
          N = 4;
        else if( axis2 >= 0 )
          N = 3;
        else if( axis1 >= 0 )
          N = 2;
        int axes[] = {axis0,axis1,axis2,axis3 };
        init(vells,axes,N);
      }
      
      void init (const Vells &vells,const LoShape &axes)
      {
        init(vells,&(axes[0]),axes.size()); 
      }

      const LoShape & shape () const
      { return shape_; }
      
      const LoShape & nonSlicedShape () const
      { return ns_shape_; }
      
      const LoShape & strides () const
      { return strides_; }
      
      bool valid () const
      { return counter_.valid(); }
      
      bool incr ();
      
      const void * pdata () const
      { return pdata_; }
      
      const Vells & vells () const
      { return vells_; }
      
      template<class T,int N>
      const blitz::Array<T,N> & getArray () const
      { return vells_.getConstArray<T,N>(); } 
      
  protected:
      // init with Vells and N axes
      void init (const Vells &vells,const int *axes,int naxes);
  
      // inits reference Vells for current slice
      void initRefVells ();
      
      char * pdata_;        // current data pointer
      size_t data_size_;    // size of array element
      const char * pflags_;       // current flag data pointer
      size_t flag_data_size_;    // size of flag array element
      Vells  vells_;        // current reference Vells
      Vells * pvells0_;     // original Vells being sliced
      const Vells * fvells0_;     // original flag Vells being sliced
      LoShape shape_;       // shape of slice
      LoShape flag_shape_;  // shape of flag slice
      LoShape strides_;     // strides of slice
      LoShape flag_strides_;  // strides of flag slice
      LoShape ns_shape_;      // shape of non-sliced axes
      
      bool sliced_[Axis::MaxAxis];    // flag: true if axis is in slice  
      bool flag_sliced_[Axis::MaxAxis];    // flag: true if axis is in slice  
      
      Vells::DimCounter counter_;     // counter for non-sliced dims
      Vells::Strides vstrides_;       // strides of source data
      Vells::Strides fstrides_;       // strides of flag data
};
    

template<typename T,int N>
class ConstVellsSlicerWithFlags : public ConstVellsSlicerWithFlags0
{
  public:
      ConstVellsSlicerWithFlags (const Vells &vells,const int *axes)
        : ConstVellsSlicerWithFlags0(vells,axes,N)
      { 
        checkType(vells);
      }
  
      ConstVellsSlicerWithFlags (const Vells &vells,const LoShape &axes)
        : ConstVellsSlicerWithFlags0(vells,&(axes[0]),N)
      { 
        FailWhen(axes.size()!=N,"ConstVellsSlicerWithFlags: incorrect number of axes supplied");
        checkType(vells);
      }
      
      ConstVellsSlicerWithFlags (const Vells &vells,const blitz::TinyVector<int,N> &axes)
        : ConstVellsSlicerWithFlags0(vells,&(axes[0]),N)
      { 
        checkType(vells);
      }
  
      ConstVellsSlicerWithFlags (const Vells &vells,int axis0,int axis1=-1,int axis2=-1,int axis3=-1)
        : ConstVellsSlicerWithFlags0(vells,axis0,axis1,axis2,axis3)
      {
        checkType(vells);
      }
      
      const T * pdata () 
      { return static_cast<const T*>(ConstVellsSlicerWithFlags0::pdata()); }

      const blitz::Array<T,N> & array () const
      { return getArray<T,N>(); }
      
      const blitz::Array<T,N> & operator () () const
      { return array(); }

  private:      
      void checkType (const Vells &vells)
      {
        FailWhen(vells.elementType()!=typeIdOf(T),"can't init"
          " ConstVellsSlicerWithFlags<"+typeIdOf(T).toString()+
          "> from Vells of type "+vells.elementType().toString());
      }
      
};


}; // namespace Meq

#endif
