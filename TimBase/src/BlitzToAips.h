//#  BlitzToAips.h: Conversion methods for Blitz++ and AIPS++ data structures.
//#
//#  Copyright (C) 2002-2007
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  and The MeqTree Foundation
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
    
#include <TimBase/Lorrays.h>
#include <casacore/casa/Arrays/Array.h>

#ifndef LORRAYS_USE_BLITZ
#error Must use Blitz Lorrays
#endif

namespace B2A
{

template<int N>
void convertShape (casacore::IPosition &ipos,const blitz::TinyVector<int,N> &tv)
{
  ipos.resize(N);
  for( int i=0; i<N; i++ )
    ipos(i) = tv[i];
}

template<int N>
void convertShape( blitz::TinyVector<int,N> &tv,const casacore::IPosition &ipos)
{
  using namespace DebugDefault;
  FailWhen(ipos.nelements() != N,"casacore::IPosition size mismatch");
  for( int i=0; i<N; i++ )
    tv[i] = ipos(i);
}

// Versions of the above that return result by value
template<int N>
casacore::IPosition blitzToAips (const blitz::TinyVector<int,N> &tv)
{
  casacore::IPosition ret;
  convertShape(ret,tv);
  return ret;
}

template<int N>
blitz::TinyVector<int,N> aipsToBlitz (const casacore::IPosition &ipos)
{
  blitz::TinyVector<int,N> ret;
  convertShape(ret,ipos);
  return ret;
}


// Makes the AIPS++ array "out" a copy of the blitz array "in".
// The data is always copied.
template<class T1,class T2,int N>
void copyArray ( casacore::Array<T1> &out,const blitz::Array<T2,N> &in )
{
  T1 *data = new T1[in.size()];
  // create temp array representing the data in column (aips++) order
  blitz::Array<T1,N> tmp(data,in.shape(),blitz::neverDeleteData,blitz::ColumnMajorArray<N>());
  // use blitz assignment to copy data: presumably, this is fast enough
  tmp = in;
  // give data to aips++ array
  casacore::IPosition shape;
  convertShape(shape,in.shape());
  out.takeStorage(shape,data,casacore::TAKE_OVER);
}

#ifndef USE_STD_COMPLEX
template<class T,int N>
void copyArray (casacore::Array<casacore::Complex> &out,const blitz::Array<T,N> &in)
{
  casacore::Complex *data = new casacore::Complex[in.size()];
  // create temp array representing the data in column (aips++) order
  // use a hard pointer cast to make this appear to be an fcomplex array
  blitz::Array<fcomplex,N> tmp(reinterpret_cast<fcomplex*>(data),in.shape(),blitz::neverDeleteData,blitz::ColumnMajorArray<N>());
  // use blitz assignment to copy data: presumably, this is fast enough
  tmp = in;
  // give data to aips++ array
  casacore::IPosition shape;
  convertShape(shape,in.shape());
  out.takeStorage(shape,data,casacore::TAKE_OVER);
}
#endif

// Versions of the above that return result by value
template<class T,int N>
casacore::Array<T> copyBlitzToAips ( const blitz::Array<T,N> &in )
{
  casacore::Array<T> out;
  copyArray(out,in);
  return out;
}

//   template<class T,int N>
//   casacore::Array<T> refBlitzToAips ( blitz::Array<T,N> &in )
//   {
//     casacore::Array<T> out;
//     refArray(out,in);
//     return out;
//   }


// Helper function for converting AIPS++ arrays to blitz (refArray() and 
// copyArray() below use it)
template<class T,int N>
void aipsToBlitz ( blitz::Array<T,N> &out,casacore::Array<T> &in,blitz::preexistingMemoryPolicy policy )
{
  using namespace DebugDefault;
  FailWhen( in.ndim() != N,"array rank mismatch" );
  blitz::TinyVector<int,N> shape;
  convertShape(shape,in.shape());
  bool deleteData;
  T* ptr = in.getStorage(deleteData);
  // if deleteData is True, we can take over the storage. Else make copy
  blitz::Array<T,N> tmp(ptr,shape,
                        deleteData ? blitz::deleteDataWhenDone : policy,
                        blitz::ColumnMajorArray<N>());
  out.reference(tmp);
}

// Makes the blitz array "out" a copy of the AIPS++ array "in".
// The data is always copied.
template<class T,int N>
void copyArray ( blitz::Array<T,N> &out,const casacore::Array<T> &in )
{
  using namespace DebugDefault;
  // cast away const but that's OK since data will be duplicated
  aipsToBlitz(out,const_cast<casacore::Array<T>&>(in),blitz::duplicateData);
}

// Makes the Blitz array "out" a reference to the AIPS++ array "in".
// The Blitz array will not delete the data when done, hence it is up to the
// caller to ensure that the "in" object outlives the out object.
// The AIPS++ array must be contiguous for this (otherwise a copy is always made) 
template<class T,int N>
void refArray ( blitz::Array<T,N> &out,casacore::Array<T> &in )
{
  using namespace DebugDefault;
  aipsToBlitz(out,in,blitz::neverDeleteData);
}

// Helper function for converting AIPS++ arrays to Blitz arrays
// with a hard-and-dangerous pointer cast.
// Types must be binary-compatible.
// NB! we assume that the C99 _Complex is binary-compatible to
// AIPS++ complex
template<class TA,class TB,int N>
void _aipsToBlitz_cast ( blitz::Array<TB,N> &out,casacore::Array<TA> &in,blitz::preexistingMemoryPolicy policy )
{
  using namespace DebugDefault;
  FailWhen( in.ndim() != N,"array rank mismatch" );
  blitz::TinyVector<int,N> shape;
  convertShape(shape,in.shape());
  bool deleteData;
  TA* ptr = in.getStorage(deleteData);
  // if deleteData is True, we can take over the storage. Else make copy
  blitz::Array<TB,N> tmp(reinterpret_cast<TB*>(ptr),shape,
                        deleteData ? blitz::deleteDataWhenDone : policy,
                        blitz::ColumnMajorArray<N>());
  out.reference(tmp);
}
// Makes the blitz array "out" a copy of the AIPS++ array "in".
// The data is always copied.
template<class TA,class TB,int N>
void _copyArray_cast ( blitz::Array<TB,N> &out,const casacore::Array<TA> &in )
{
  using namespace DebugDefault;
  // cast away const but that's OK since data will be duplicated
  _aipsToBlitz_cast(out,const_cast<casacore::Array<TA>&>(in),blitz::duplicateData);
}

// Makes the Blitz array "out" a reference to the AIPS++ array "in".
// The Blitz array will not delete the data when done, hence it is up to the
// caller to ensure that the "in" object outlives the out object.
// The AIPS++ array must be contiguous for this (otherwise a copy is always made) 
template<class TA,class TB,int N>
void _refArray_cast ( blitz::Array<TB,N> &out,casacore::Array<TA> &in )
{
  using namespace DebugDefault;
  _aipsToBlitz_cast(out,in,blitz::neverDeleteData);
}


// Versions of the above that return result by value
template<class T,int N>
blitz::Array<T,N> copyAipsToBlitz ( const casacore::Array<T> &in )
{
  blitz::Array<T,N> out;
  copyArray(out,in);
  return out;
}

template<class T,int N>
blitz::Array<T,N> refAipsToBlitz ( casacore::Array<T> &in )
{
  blitz::Array<T,N> out;
  refArray(out,in);
  return out;
}

//#ifndef USE_STD_COMPLEX
template<int N>
inline blitz::Array<fcomplex,N> copyAipsToBlitzComplex ( const casacore::Array<casacore::Complex> &in )
{
  blitz::Array<fcomplex,N> out;
  _copyArray_cast(out,in);
  return out;
}

template<int N>
inline blitz::Array<fcomplex,N> refAipsToBlitzComplex ( casacore::Array<casacore::Complex> &in )
{
  blitz::Array<fcomplex,N> out;
  _refArray_cast(out,in);
  return out;
}

template<int N>
inline blitz::Array<dcomplex,N> copyAipsToBlitzComplex ( const casacore::Array<casacore::DComplex> &in )
{
  blitz::Array<dcomplex,N> out;
  _copyArray_cast(out,in);
  return out;
}

template<int N>
inline blitz::Array<dcomplex,N> refAipsToBlitzComplex ( casacore::Array<casacore::DComplex> &in )
{
  blitz::Array<dcomplex,N> out;
  _refArray_cast(out,in);
  return out;
}
//#endif


// Copies data between arrays. Shapes must match to begin with
template<class T,int N>
void assignArray( casacore::Array<T> &to,const blitz::Array<T,N> &from )
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
  T* data = to.getStorage(del);
  // copy data
  blitz::Array<T,N> tmp(data,from.shape(),blitz::neverDeleteData,blitz::ColumnMajorArray<N>());
  // use blitz assignment to copy data: presumably, this is fast enough
  tmp = from;
  // reset storage
  to.putStorage(data,del);
}

template<class T,int N>
void assignArray( blitz::Array<T,N> &to,const casacore::Array<T> &from )
{
  using namespace DebugDefault;
  FailWhen( from.ndim() != N,"array rank mismatch" );
  for( int i=0; i<N; i++ )
  {
    FailWhen( to.extent(i) != from.shape()[i],"array shape mismatch" );
  }
  if( !to.size() )
    return;
  // BUG!!
  // Use of getStorage() is not terribly efficient in case of not-contiguous
  // AIPS++ arrays. Check with Ger, how do we quickly iterate through one?
  bool del;
  const T* data = from.getStorage(del);
  // copy data -- cast away const here to construct array, but we only copy from it
  blitz::Array<T,N> tmp(const_cast<T*>(data),to.shape(),blitz::neverDeleteData,blitz::ColumnMajorArray<N>());
  // use blitz assignment to copy data: presumably, this is fast enough
  to = tmp;
  // reset storage
  from.freeStorage(data,del);
}

};

#endif
