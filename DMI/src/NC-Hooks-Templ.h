// -----------------------------------------------------------------------
// access as STL vectors 
// -----------------------------------------------------------------------

// some out-of-line templates for hooks
// Define an get_vector<> template. This should work for all
// contiguous containers.
// This copies data so is not very efficient, but is quite
// convenient where sizes are small.
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

template<class T>
bool DMI::Container::Hook::get_vector_impl (std::vector<T> &value,bool must_exist) const
{
  int n;
  const T *data = as_po(n,Type2Type<T>());
  if( !data )
    return false;
  value.resize(n);
  value.assign(data,data+n);
  return true;
}

// -----------------------------------------------------------------------
// assignment of Lorrays
// this will create a new DMI::Array object, or else assign to the underlying
// array. Note the void return type -- we may not have an array object to
// return at all (i.e. when the underlying data is not held in an Array)
// -----------------------------------------------------------------------
template<class T,int N> 
void DMI::Container::Hook::operator = (const blitz::Array<T,N> &other) const
{
  bool haveArray;
  void * target = prepare_assign_array(haveArray,typeIdOf(T),other.shape());
  if( !target )             // no object - create new field
  {
    DMI::ObjRef ref(new DMI::NumArray(other));
    assign_objref(ref,0);
  }
  else if( haveArray )       // got array object - use assignment
  {
    blitz::Array<T,N> *pdest = static_cast<blitz::Array<T,N>*>(target);
    for( int i=0; i<N; i++ )
      if( pdest->extent(i) != other.extent(i) )
        ThrowExc(ConvError,"can't assign array: shape mismatch");
    (*pdest) = other;
  }
  else                      // got pointer to data - use flat copy
  {
    blitz::Array<T,N> dest(static_cast<T*>(target),other.shape(),blitz::neverDeleteData);
    dest = other;
  }
}

// -----------------------------------------------------------------------
// assign_sequence
// helper function to assign sequences of non-arrayable types
// -----------------------------------------------------------------------
template<class T,class Iter> 
void DMI::Container::Hook::assign_sequence(uint size,Iter begin,Iter end,Type2Type<T>) const
{ 
  const int tid = DMITypeTraits<T>::typeId;
  T * ptr = static_cast<T*>( assign_vector(tid,size) ); 
  for( ; begin != end; begin++ )
    *ptr++ = *begin; 
}


