//#  BlitzToAips.h: Conversion methods for Blitz++ and AIPS++ data structures.
//#
//#  Copyright (C) 2002-2004
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$

#ifndef LOFAR_COMMON_BLITZTOAIPS_H
#define LOFAR_COMMON_BLITZTOAIPS_H

#include <lofar_config.h>

#ifndef HAVE_BLITZ
#error Blitz support required
#endif

#ifndef HAVE_AIPSPP
#error AIPS++ support required
#endif
    
#include <Common/Lorrays.h>
#include <casa/Arrays/Array.h>

#ifndef LORRAYS_USE_BLITZ
#error Must use Blitz Lorrays
#endif

namespace LOFAR
{
   
  template<int N>
  void convertShape (casa::IPosition &ipos,const blitz::TinyVector<int,N> &tv)
  {
    ipos.resize(N);
    for( int i=0; i<N; i++ )
      ipos(i) = tv[i];
  }

  template<int N>
  void convertShape( blitz::TinyVector<int,N> &tv,const casa::IPosition &ipos)
  {
    using namespace DebugDefault;
    FailWhen(ipos.nelements() != N,"casa::IPosition size mismatch");
    for( int i=0; i<N; i++ )
      tv[i] = ipos(i);
  }

  // Versions of the above that return result by value
  template<int N>
  casa::IPosition blitzToAips (const blitz::TinyVector<int,N> &tv)
  {
    casa::IPosition ret;
    convertShape(ret,tv);
    return ret;
  }

  template<int N>
  blitz::TinyVector<int,N> aipsToBlitz (const casa::IPosition &ipos)
  {
    blitz::TinyVector<int,N> ret;
    convertShape(ret,tv);
    return ret;
  }

   
  // Makes the AIPS++ array "out" a copy of the blitz array "in".
  // The data is always copied.
  template<class T1,class T2,int N>
  void copyArray ( casa::Array<T1> &out,const blitz::Array<T2,N> &in )
  {
    T1 *data = new T1[in.size()],*ptr = data;
    if( in.size() )
      for( typename blitz::Array<T2,N>::const_iterator iter = in.begin();
           iter != in.end(); iter++,ptr++ )
        *ptr = static_cast<T1>(*iter);
    casa::IPosition shape;
    convertShape(shape,in.shape());
    out.takeStorage(shape,data,casa::TAKE_OVER);
  }

  // Makes the AIPS++ array "out" a reference to the blitz array "in".
  // The AIPS++ array will not delete the data when done, hence it is up to the
  // caller to ensure that the "in" object outlives the out object.
  // The blitz array must be contiguous for this (otherwise a copy is made) 
  template<class T1,class T2,int N>
  void refArray ( casa::Array<T1> &out,blitz::Array<T2,N> &in )
  {
    if( !in.isStorageContiguous() )
      copyArray(out,in);
    else
    {
      casa::IPosition shape;
      convertShape(shape,in.shape());
      out.takeStorage(shape,reinterpret_cast<T1*>(in.data()),casa::SHARE);
    }
  }

  // Versions of the above that return result by value
  template<class T,int N>
  casa::Array<T> copyBlitzToAips ( const blitz::Array<T,N> &in )
  {
    casa::Array<T> out;
    copyArray(out,in);
    return out;
  }

  template<class T,int N>
  casa::Array<T> refBlitzToAips ( blitz::Array<T,N> &in )
  {
    casa::Array<T> out;
    refArray(out,in);
    return out;
  }


  // Helper function for converting AIPS++ arrays to blitz (refArray() and 
  // copyArray() below use it)
  template<class T,int N>
  void aipsToBlitz ( blitz::Array<T,N> &out,casa::Array<T> &in,blitz::preexistingMemoryPolicy policy )
  {
    using namespace DebugDefault;
    FailWhen( in.ndim() != N,"array rank mismatch" );
    blitz::TinyVector<int,N> shape;
    convertShape(shape,in.shape());
    bool deleteData;
    T* ptr = in.getStorage(deleteData);
    // if deleteData is True, we can take over the storage. Else make copy
    blitz::Array<T,N> tmp(ptr,shape,
                          deleteData ? blitz::deleteDataWhenDone : policy );
    out.reference(tmp);
  }

  // Makes the blitz array "out" a copy of the AIPS++ array "in".
  // The data is always copied.
  template<class T,int N>
  void copyArray ( blitz::Array<T,N> &out,const casa::Array<T> &in )
  {
    using namespace DebugDefault;
    // cast away const but that's OK since data will be duplicated
    aipsToBlitz(out,const_cast<casa::Array<T>&>(in),blitz::duplicateData);
  }

  // Makes the Blitz array "out" a reference to the AIPS++ array "in".
  // The Blitz array will not delete the data when done, hence it is up to the
  // caller to ensure that the "in" object outlives the out object.
  // The AIPS++ array must be contiguous for this (otherwise a copy is always made) 
  template<class T,int N>
  void refArray ( blitz::Array<T,N> &out,casa::Array<T> &in )
  {
    using namespace DebugDefault;
    aipsToBlitz(out,in,blitz::neverDeleteData);
  }

  // Versions of the above that return result by value
  template<class T,int N>
  blitz::Array<T,N> copyAipsToBlitz ( const casa::Array<T> &in )
  {
    blitz::Array<T,N> out;
    copyArray(out,in);
    return out;
  }

  template<class T,int N>
  blitz::Array<T,N> refAipsToBlitz ( casa::Array<T> &in )
  {
    blitz::Array<T,N> out;
    refArray(out,in);
    return out;
  }


  // Copies data between arrays. Shapes must match to begin with
  template<class T,int N>
  void assignArray( casa::Array<T> &to,const blitz::Array<T,N> &from )
  {
    using namespace DebugDefault;
    FailWhen( to.ndim() != N,"array rank mismatch" );
    for( int i=0; i<N; i++ )
    {
      FailWhen( to.shape()(i) != from.shape()[i],"array shape mismatch" );
    }
    if( !to.size() )
      return;
    // BUG!!
    // Use of getStorage() is not terribly efficient in case of not-contiguous
    // AIPS++ arrays. Check with Ger, how do we quickly iterate through one?
    bool del;
    T* data = to.getStorage(del),*ptr = data;
    // copy data
    for( typename blitz::Array<T,N>::const_iterator iter = from.begin();
         iter != from.end(); iter++,ptr++ )
      *ptr = *iter;
    // reset storage
    to.putStorage(data,del);
  }

  template<class T,int N>
  void assignArray( blitz::Array<T,N> &to,const casa::Array<T> &from )
  {
    using namespace DebugDefault;
    FailWhen( to.ndim() != N,"array rank mismatch" );
    for( int i=0; i<N; i++ )
    {
      FailWhen( to.shape()(i) != from.shape()[i],"array shape mismatch" );
    }
    if( !to.size() )
      return;
    // BUG!!
    // Use of getStorage() is not terribly efficient in case of not-contiguous
    // AIPS++ arrays. Check with Ger, how do we quickly iterate through one?
    bool del;
    const T* data = from.getStorage(del),*ptr = data;
    // copy data
    for( typename blitz::Array<T,N>::iterator iter = to.begin();
         iter != to.end(); iter++,ptr++ )
      *iter = *iter;
    // reset storage
    from.freeStorage(data,del);
  }

} // namespace LOFAR

#endif
