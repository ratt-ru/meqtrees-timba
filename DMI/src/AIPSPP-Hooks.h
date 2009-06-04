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

#ifndef DMI_AIPSPP_Hooks_h
#define DMI_AIPSPP_Hooks_h 1
    
#ifdef AIPSPP_HOOKS
    
#include <casa/Arrays/Array.h>
#include <casa/Arrays/Vector.h>
#include <casa/Arrays/Matrix.h>
#include <casa/BasicSL/String.h>
    
#include <DMI/NumArray.h>
#include <TimBase/BlitzToAips.h>

namespace AIPSPP_Hooks 
{
  using namespace DebugDMI;
  
  // templated helper method to create a 1D array using a copy of data
  template<class T>
  inline casa::Array<T> copyVector (DMI::TypeId tid,int n,const void *data)
  { 
    if( tid != typeIdOf(T) )
    {
      ThrowExc(DMI::Container::ConvError,"can't convert "+tid.toString()+
                  " to AIPS++ Array<"+typeIdOf(T).toString()+">");
    }
    return casa::Array<T>(casa::IPosition(1,n),static_cast<const T*>(data));
  };

  // specialization for casa::String, with conversion from std::string
  template<>
  inline casa::Array<casa::String> copyVector (DMI::TypeId tid,int n,const void *data)
  { 
    if( tid != Tpstring )
    {
      ThrowExc(DMI::Container::ConvError,"can't convert "+tid.toString()+
                  " to AIPS++ Array<casa::String>");
    }
    casa::String *dest0 = new casa::String[n], *dest = dest0;
    const string *src = static_cast<const string *>(data);
    for( int i=0; i<n; i++,dest++,src++ )
      *dest = *src;
    return casa::Array<casa::String>(casa::IPosition(1,n),dest0,casa::TAKE_OVER);
  };
  
};


inline casa::String DMI::Container::Hook::as_String () const
{
  return casa::String(as<string>());
}

template<class T>
casa::Array<T> DMI::Container::Hook::as_AipsArray (Type2Type<T>) const
{
  const void *targ = resolveTarget(DMI::DEREFERENCE);
  // Have we resolved to a DMI::Array? 
  if( target.obj_tid == TpDMINumArray )
    return static_cast<const DMI::NumArray *>(targ)->copyAipsArray((T*)0);
  // have we resolved to a blitz array?
  else if( TypeInfo::isArray(target.obj_tid) )
  {
    casa::Array<T> out;
    switch( TypeInfo::rankOfArray(target.obj_tid) )
    {
      case 1: B2A::copyArray(out,*static_cast<const blitz::Array<T,1>*>(target.ptr)); break;
      case 2: B2A::copyArray(out,*static_cast<const blitz::Array<T,2>*>(target.ptr)); break;
      case 3: B2A::copyArray(out,*static_cast<const blitz::Array<T,3>*>(target.ptr)); break;
      case 4: B2A::copyArray(out,*static_cast<const blitz::Array<T,4>*>(target.ptr)); break;
      case 5: B2A::copyArray(out,*static_cast<const blitz::Array<T,5>*>(target.ptr)); break;
      case 6: B2A::copyArray(out,*static_cast<const blitz::Array<T,6>*>(target.ptr)); break;
      case 7: B2A::copyArray(out,*static_cast<const blitz::Array<T,7>*>(target.ptr)); break;
      case 8: B2A::copyArray(out,*static_cast<const blitz::Array<T,8>*>(target.ptr)); break;
      case 9: B2A::copyArray(out,*static_cast<const blitz::Array<T,9>*>(target.ptr)); break;
      case 10:B2A::copyArray(out,*static_cast<const blitz::Array<T,10>*>(target.ptr)); break;
      default: 
        ThrowExc(ConvError,"can't convert "+target.obj_tid.toString()+
                    " to AIPS++ Array<"+typeIdOf(T).toString()+">: rank too high");
    }
    return out;
  }
  // have we resolved to scalar? Try the copyVector method
  return AIPSPP_Hooks::copyVector<T>(target.obj_tid,target.size,target.ptr);
}

template<class T>
casa::Vector<T> DMI::Container::Hook::as_AipsVector (Type2Type<T>) const
{
  casa::Array<T> arr = as_AipsArray(Type2Type<T>());
  FailWhen( arr.ndim() != 1,"can't access array as Vector" );
  return casa::Vector<T>(arr);
}

template<class T>
casa::Matrix<T> DMI::Container::Hook::as_AipsMatrix (Type2Type<T>) const
{
  casa::Array<T> arr = as_AipsArray(Type2Type<T>());
  FailWhen( arr.ndim() != 2,"can't access array as Matrix" );
  return casa::Matrix<T>(arr);
}

template<class T>
void DMI::Container::Hook::operator = (const casa::Array<T> &other) const
{
  (*this) <<= new DMI::NumArray(other);
}

// assigning a casa::String simply assigns a string
inline string & DMI::Container::Hook::operator = (const casa::String &other) const
{
  return operator = ( static_cast<const string &>(other) );
}

#endif

#endif
