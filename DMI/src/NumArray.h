//  DataArray.h: Array container (using Blitz Arrays)
//
//  Copyright (C) 2002
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//
//  This program is free software; you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation; either version 2 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//  $Id$
//
//  $Log$
//  Revision 1.30  2005/01/17 12:47:34  cvs
//  Moved with cvsmv from LOFAR/DMI/src, creating new revision
//
//  Revision 1.29  2005/01/07 07:56:28  diepen
//  %[ER: 222]%
//  Use AIPS++ casa namespace
//
//  Revision 1.28  2004/09/13 15:40:52  smirnov
//  %[ER: 16]%
//  Added elementSize() convenience function
//
//  Revision 1.27  2004/08/31 07:48:56  diepen
//  %[ER: 70]%
//  Changed for new AIPS++ structure
//
//  Revision 1.26  2004/03/17 07:51:20  smirnov
//  %[ER: 16]%
//  Extended access by pointer in DataArray
//
//  Revision 1.25  2004/01/28 16:23:34  smirnov
//  %[ER: 16]%
//  Revised the hook infrastructure, got rid of NC::writable flag.
//  Simplified CountedRefs
//
//  Revision 1.24.2.1  2004/01/26 14:57:40  smirnov
//  %[ER: 16]%
//  Commiting overhaul of Hook classes
//
//  Revision 1.24  2004/01/21 11:08:58  smirnov
//  %[ER: 16]%
//  brought the Rose model up-to-date; this got a bunch of IDs inserted into the
//  sources, hence the massive update.
//
//  Revision 1.23  2003/11/24 22:13:25  smirnov
//  %[ER: 16]%
//  Some minor fixes related to data accessorts.
//  Added validateContent() calls to privatize() methods.
//
//  Revision 1.22  2003/11/12 16:57:18  smirnov
//  %[ER: 16]%
//  Added arrays accessors to DataArray
//
//  Revision 1.21  2003/09/10 15:11:05  smirnov
//  %[BugId: ]%
//  Various small fixes & cleanups.
//  Allowed numeric (i.e. single-index) field names in DataRecord. The old
//  way of accessing field by its number is available via the special HIID "#.n"
//  (AidHash|n).
//  Fixed bug with resizing DataFields with a dynamic type content -- these would
//  fail a toBlock/fromBlock after a resize.
//
//  Revision 1.20  2003/05/14 10:28:11  smirnov
//  %[BugId: 26]%
//  Fixed bug when constructing from a 0-dim AIPS++ array
//
//  Revision 1.19  2003/04/29 07:19:31  smirnov
//  %[BugId: 26]%
//  Various updates to hooks
//
//  Revision 1.18  2002/12/09 08:22:31  smirnov
//  %[BugId: 112]%
//  Simplified string support in DataAarray
//
//  Revision 1.17  2002/12/06 15:29:02  smirnov
//  %[BugId: 112]%
//  Fixed some bugs in the AIPS++ hooks;
//  fixed size returned from DataRecord iterator.
//
//  Revision 1.16  2002/12/05 10:15:22  smirnov
//  %[BugId: 112]%
//  Fixed Lorray support in DataArrays, etc.
//  Revised AIPS++ hooks.
//
//  Revision 1.15  2002/12/03 20:36:14  smirnov
//  %[BugId: 112]%
//  Ported DMI to use Lorrays (with blitz arrays)
//
//  Revision 1.14  2002/10/29 16:28:17  smirnov
//  %[BugId: 26]%
//  Added missing TypeIter-DMI.h file.
//  Removed spurious #include of BlockSet1.h (thanks a lot, Rose...)
//
//  Revision 1.13  2002/10/29 13:10:38  smirnov
//  %[BugId: 26]%
//  Re-worked build_aid_maps.pl and TypeIterMacros.h to enable on-demand
//  importing of data types from other packages. Basically, data types from package
//  X will be pulled in by NestableContainer only when included from
//  package Y that has an explicit dependence on package X. DMI itself depends
//  only on Common.
//
//  Migrated to new Rose C++ add-in, so all Rose markup has changed.
//
//  Revision 1.12  2002/06/11 12:15:08  smirnov
//  %[BugId: 26]%
//  Further fixes to array-mode hook addressing.
//  Added an optional tid argument to NestableContainer::size().
//
//  Revision 1.11  2002/06/10 12:39:18  smirnov
//  %[BugId: 26]%
//  Revised NestableContainer::get() interface to return info in a ContentInfo
//  structure.
//  Added optional size argument to hook.as_type_p() and _wp() methods.
//  Cleaned up size handling, added working as_vector<T> and =(vector<T>).
//
//  Revision 1.10  2002/06/07 14:22:48  smirnov
//  %[BugId: 26]%
//  Many revisions related to support of arrays and vectors (including AIPS++) by
//  hooks. Checking in now because I plan to modify the NestableContainer interface.
//
//  Revision 1.9  2002/05/30 12:15:13  diepen
//
//  %[BugId: 25]%
//  Added the required constructors
//
//  Revision 1.8  2002/05/14 09:48:00  gvd
//  Removed public which was left in
//
//  Revision 1.7  2002/05/07 13:48:52  oms
//  Minor fixes for the new build environment.
//  The code has been re-generated by Rose, hence the world+dog has
//  been updated.
//
//  Revision 1.6  2002/05/07 11:46:00  gvd
//  The 'final' version supporting array subsets
//
//  Revision 1.5  2002/04/17 12:19:31  oms
//  Added the "Intermediate" type category (for Array_xxx) and support for it
//  in hooks.
//
//  Revision 1.4  2002/04/12 10:15:09  oms
//  Added fcomplex and dcomplex types.
//  Changes to NestableContainer::get():
//   - merged autoprivatize and must_write args into a single flags arg
//   - added NC_SCALAR and NC_POINTER flags that are passed to get()
//  Got rid of isScalar() and isContiguous(), checking is now up to get().
//
//  Revision 1.3  2002/04/12 07:47:53  oms
//  Added fcomplex and dcomplex types
//
//  Revision 1.2  2002/04/08 14:27:07  oms
//  Added isScalar(tid) to DataArray.
//  Fixed isContiguous() in DataField.
//
//  Revision 1.1  2002/04/05 13:05:46  gvd
//  First version
//
#ifndef DMI_DATAARRAY_H
#define DMI_DATAARRAY_H

#include "Common/Lorrays.h"
#include "Common/Thread/Mutex.h"
#include "Common/Thread/Key.h"
#include "DMI/DMI.h"
#include "DMI/NestableContainer.h"

#ifdef HAVE_AIPSPP
#include <casa/Arrays.h>
#endif

#pragma types #DataArray


// We assume Blitz support here, AIPS++ can be re-integrated later
#ifndef LORRAYS_USE_BLITZ
  #error This version of DataArray requires Blitz Lorrays
#endif

//##ModelId=3DB949AE00C5
class DataArray : public NestableContainer
{
public:
  // Create the object without an array in it.
    //##ModelId=3DB949AE039F
  DataArray ();

  // Create the object with an array of the given shape.
    //##ModelId=3DB949AE03A4
  DataArray (TypeId type,const LoShape & shape,int flags=0,int shm_flags=0);
  
  // Create the object, and initialize data from array. "other" should point 
  // to a Lorray<T,N> object (where T,N correspond to array_tid)
    //##ModelId=3DB949AE03AF
  DataArray (TypeId array_tid,const void *other,int flags=0,int shm_flags=0);

  // Create the object with an array of the given shape.
//   explicit DataArray (const Array<bool>& array, int flags = DMI::WRITE,
// 		      int shm_flags = 0);
//   explicit DataArray (const Array<int>& array, int flags = DMI::WRITE,
// 		      int shm_flags = 0);
//   explicit DataArray (const Array<float>& array, int flags = DMI::WRITE,
// 		      int shm_flags = 0);
//   explicit DataArray (const Array<double>& array, int flags = DMI::WRITE,
// 		      int shm_flags = 0);
//   explicit DataArray (const Array<fcomplex>& array, int flags = DMI::WRITE,
// 		      int shm_flags = 0);
//   explicit DataArray (const Array<dcomplex>& array, int flags = DMI::WRITE,
// 		      int shm_flags = 0);
//   
  // templated method to create a copy of the given Lorray.
  // We make use of the fact that a Lorray(N,T) is actually a blitz::Array<T,N>.
  // Hence this templated definition is equivalent to a bunch of non-templated
  // ones, each with its own type and rank.
  // For non-templated compilers, this can be redefined using the DoFor...()
  // type iterator macros
  template<class T,int N>
  explicit DataArray (const blitz::Array<T,N> & array,int flags=0,int shm_flags=0);

#ifdef HAVE_AIPSPP
  // templated method to create a copy of the given AIPS++ array
  template<class T>
  explicit DataArray (const casa::Array<T> & array,int flags=0,int shm_flags=0);
#endif

  // Copy (copy semantics).
    //##ModelId=3F5487DA034E
  DataArray (const DataArray& other, int flags=0, int depth=0);

    //##ModelId=3DB949AE03B8
  ~DataArray();

  // Assignment (copy semantics).
    //##ModelId=3DB949AE03B9
  DataArray& operator= (const DataArray& other);

  // True if the object contains an initialized array
  //##ModelId=3DB949AF0022
  bool valid() const;
      
  // returns rank of array
    //##ModelId=3E9BD91800B4
  int rank () const;
  
  // returns shape of array
    //##ModelId=3E9BD91800B7
  const LoShape & shape () const;
  
  // returns type of array element
  // (the virtual type() method, below, overriding the abstract one in 
  // NestableContainer, will return the array type)
    //##ModelId=3E9BD91800B9
  TypeId elementType () const;
  
  // returns size of array element
  int elementSize () const
  { return itsElemSize; }
  
#ifdef HAVE_AIPSPP
  // Returns contents as an AIPS++ array (by copy or reference)
  // The dummy T* argument is to help in template instantiation
  // (gcc has a problem resolving stuff like:
  //
  //    template<class T> T function_one ();
  //    template<class T> T function_two ()
  //    { return function_one<T>(); }
  //  ... the <T> in the invocation is considered an error. The dummy
  //  argument allows you to say "function_one((T*)0)" instead)
  template<class T>
  casa::Array<T> refAipsArray (const T*);
  template<class T>
  casa::Array<T> copyAipsArray (const T*) const;
#endif
  
    //##ModelId=400E4D68035F
  // return pointer to underlying array object, checking element type and rank
  const void * getConstArrayPtr (TypeId element_tid,uint nrank) const;
  // return pointer to underlying array object, checking array type and rank
  const void * getConstArrayPtr (TypeId array_tid) const;
  
  void * getArrayPtr (TypeId element_tid,uint nrank)
  { return const_cast<void*>(getConstArrayPtr(element_tid,nrank)); }
  void * getArrayPtr (TypeId array_tid)
  { return const_cast<void*>(getConstArrayPtr(array_tid)); }
  
  template<class T,int N>
  const blitz::Array<T,N> & getConstArray () const
  { return *static_cast<const blitz::Array<T,N>*>(getConstArrayPtr(typeIdOf(T),N)); }
  
  template<class T,int N>
  blitz::Array<T,N> & getArray () 
  { return *static_cast<blitz::Array<T,N>*>(
            const_cast<void*>(getArrayPtr(typeIdOf(T),N))); }
  
  template<class T,int N>
  void getConstArrayPtr (const blitz::Array<T,N> * &ptr) const
  { ptr = static_cast<const blitz::Array<T,N>*>(getConstArrayPtr(typeIdOf(T),N)); }

  template<class T,int N>
  void getArrayPtr (blitz::Array<T,N> * &ptr) 
  { ptr = static_cast<blitz::Array<T,N>*>(
          const_cast<void*>(getArrayPtr(typeIdOf(T),N))); }
  
    //##ModelId=400E4D680386
  const void * getConstDataPtr () const
  { return itsArrayData; }
  
    //##ModelId=400E4D68038A
  void * getDataPtr () 
  { return itsArrayData; }

  // Return the object type (TpDataArray).
    //##ModelId=3DB949AE03BE
  virtual TypeId objectType() const;

  // Reconstruct the DataArray object from a BlockSet.
    //##ModelId=3DB949AE03C0
  virtual int fromBlock (BlockSet& set);

  // Add the DataArray object to the BlockSet.
    //##ModelId=3DB949AE03C5
  virtual int toBlock (BlockSet& set) const;

  // Clone the object.
    //##ModelId=3DB949AE03CB
  virtual CountedRefTarget* clone (int flags = 0, int depth = 0) const;

  // Privatize the object.
    //##ModelId=3DB949AE03D2
  virtual void privatize (int flags = 0, int depth = 0);

  // Insertion is not possible (throws exception).
    //##ModelId=3DB949AE03E5
  virtual int insert (const HIID& id,ContentInfo &info);

  // The size is the number of array elements.
    //##ModelId=3DB949AF0007
  virtual int size (TypeId tid = 0) const;

  // The actual type of the array (TpArray_float, etc.).
    //##ModelId=3DB949AF000C
  virtual TypeId type() const;
  
  // Parse a HIID describing a subset and fill start,end,incr.
  // NB: "end" is one past ending position at each axis: 
  //        i.e. [start,end) is the interval, using conventional notation.
  // It fills in keepAxes telling which axes should be kept in the
  // subarray. Returns number of axes to keep.
    //##ModelId=3DB949AF000E
  int parseHIID (const HIID& id, LoPos& st, LoPos& end,LoPos& incr, 
                 vector<bool> &keepAxes) const;
  
    //##ModelId=3F5487DB0110
  string sdebug ( int detail = 1,const string &prefix = "",
                  const char *name = 0 ) const;
  
    //##ModelId=3DB949AF001C
  DefineRefTypes(DataArray,Ref);

    //##ModelId=3E9BD91703A8
  static const int NumTypes = Tpbool_int - Tpstring_int + 1;

protected:
    //##ModelId=3DB949AE03DA
  virtual int get (const HIID& id,ContentInfo &info,bool nonconst,int flags) const;
  
private:
  // Initialize internal shape and create array using the given shape.
    //##ModelId=3DB949AF0024
  void init (const LoShape & shape,int flags);

  // Create the actual Array object.
  // It is created from the array data part in the SmartBlock.
    //##ModelId=3DB949AF002B
  void makeArray();

  // Clear the object (thus remove the Array).
    //##ModelId=3DB949AF002C
  void clear();

  // Clone the object.
    //##ModelId=3DB949AF002E
  void cloneOther (const DataArray& other, int flags = 0, int depth = 0);

    //##ModelId=3DB949AE036D
  LoShape    itsShape;          // actual shape
  
  TypeId     itsType;           // array TypeId
    //##ModelId=3DB949AE0379
  TypeId     itsScaType;        // scalar data type matching the array type
    //##ModelId=3DB949AE0383
  int        itsElemSize;       // #bytes of an array element
    //##ModelId=3DB949AE0389
  int        itsSize;           // total size of array (in elements)
    //##ModelId=3E9BD91703CC
  int        itsDataOffset;     // array data offset in SmartBlock
    //##ModelId=3DB949AE038E
  char*      itsArrayData;      // pointer to array data in SmartBlock
    //##ModelId=3DB949AE0394
  void *     itsArray;

  //##ModelId=3DB949AE0370
  BlockRef    itsData;

  // OK, setup some circus hoops. Rank & type of DataArray is set at runtime,
  // while for blitz arrays it's compile-time. So, for every blitz operation
  // required in DataArray, we'll setup an N(ranks) x N(types) matrix of 
  // function pointers, then use rank & type to call the appropriate function.
  // This matrix is called the "method table".
  
  // Methods for the method table are naturally implemented via
  // templates. Refer to DataArray.cc.
  
  // These are the actual method tables
    //##ModelId=3E9BD9140364
  typedef void * (*AllocatorWithData)(void*,const LoShape &);
    //##ModelId=3E9BD9140377
  typedef void * (*AllocatorDefault)();
    //##ModelId=3E9BD914038B
  typedef void (*AssignWithStride)(void*,void *,const LoShape &,const LoShape &);
    //##ModelId=3E9BD91403A0
  typedef void (*Destructor)(void*);
  
    //##ModelId=3F5487DA00A7
  typedef void (*ArrayCopier)(void*,const void*);
  
    //##ModelId=3F5487DA015B
  typedef void (*ShapeOfArray)(LoShape &,const void*);
  
  static AllocatorWithData    allocatorWithData   [NumTypes][MaxLorrayRank];
  static AllocatorDefault     allocatorDefault    [NumTypes][MaxLorrayRank];
  static AssignWithStride     assignerWithStride  [NumTypes][MaxLorrayRank];
  static Destructor           destructor          [NumTypes][MaxLorrayRank];
    //##ModelId=3F5487DA023F
  static ArrayCopier          copier              [NumTypes][MaxLorrayRank];
    //##ModelId=3F5487DA0273
  static ShapeOfArray         shapeOfArray        [NumTypes][MaxLorrayRank];
  
  // converts a type id into a numeric offset into the table above
    //##ModelId=3E9BD9180129
  static int typeIndex (TypeId tid)
  { return Tpbool_int - tid.id(); }
  // These methods do a lookup & call into each method table
    //##ModelId=3E9BD918015A
  static void * allocateArrayWithData (TypeId tid,void *data,const LoShape &shape )
  {
    return (*allocatorWithData[typeIndex(tid)][shape.size()-1])(data,shape);
  }
    //##ModelId=3E9BD91801EA
  static void assignWithStride (TypeId tid,void *ptr,void *data,const LoShape &shape,const LoShape &stride )
  {
    (*assignerWithStride[typeIndex(tid)][shape.size()-1])(ptr,data,shape,stride);
  }
    //##ModelId=3E9BD91802D8
  static void * allocateArrayDefault (TypeId tid,int rank)
  {
    return (*allocatorDefault[typeIndex(tid)][rank-1])();
  }
    //##ModelId=3E9BD9180339
  static void destroyArray (TypeId tid,int rank,void *ptr)
  {
    (*destructor[typeIndex(tid)][rank-1])(ptr);
  }
  
    //##ModelId=3F5487DB02E7
  static void copyArray (TypeId tid,int rank,void *target,const void *source)
  {
    (*copier[typeIndex(tid)][rank-1])(target,source);
  }
  
    //##ModelId=3F5487DC0121
  static void getShapeOfArray (TypeId tid,int rank,LoShape &shape,const void *ptr)
  {
    (*shapeOfArray[typeIndex(tid)][rank-1])(shape,ptr);
  }
  

  // Define the subarray object (for slicing into an array)
    //##ModelId=3E9BD91403B3
  typedef struct { void *ptr; int rank; }  SubArray;
#ifdef USE_THREADS
  // Each thread must have its own subarray pointer. Use a map to accomplish
  // this -- I would use thread keys, but the number is way too limited.
    //##ModelId=3E9BD91403C7
  typedef std::map<Thread::ThrID,SubArray> SubArrayMap;
  mutable SubArrayMap itsSubArrayMap;
  
    //##ModelId=3E9BD91803C9
  void initSubArray () const
  {}
#else
  // non-threaded mode -- keep a single entry
  mutable SubArray itsSubArray;
  
  void initSubArray () const
  { itsSubArray.ptr = 0; }
#endif
  // this helper function creates the subarray object with the given data,
  // shape & stride. 
    //##ModelId=3E9BD91803CC
  void * makeSubArray (void *data,const LoShape & shape,const LoShape &stride) const;
  
#ifdef HAVE_AIPSPP
  // helper function to implement templates below without resorting to a
  // specialization (which seems to cause redefined symbol trouble)
  template<class T>
  static bool isStringArray (const casa::Array<T> &);
  // helper function returns True if array contains the same data type
  // (with AIPS++ String matching Tpstring)
  template<class T>
  bool verifyAipsType (const T*) const;
  // helper function copies strings from source array
    //##ModelId=3E9BD9190074
  void copyStringArray (const void *source);
#endif
};

DefineRefTypes(DataArray,DataArrayRef);

inline bool DataArray::valid () const
{
  return itsArray != 0 ;
}

    
// returns rank of array
//##ModelId=3E9BD91800B4
inline int DataArray::rank () const
{
  return itsShape.size();
}
  
// returns shape of array
//##ModelId=3E9BD91800B7
inline const LoShape & DataArray::shape () const
{
  return itsShape;
}
  
// returns type of array element
// (the virtual type() method, below, overriding the abstract one in 
// NestableContainer, will return the array type)
//##ModelId=3E9BD91800B9
inline TypeId DataArray::elementType () const
{
  return itsScaType;
}

// templated constructor from a Blitz array
template<class T,int N>
DataArray::DataArray (const blitz::Array<T,N>& array,
		      int flags, int )  // shm_flags not yet used
: NestableContainer(),
  itsArray    (0)
{
  initSubArray();
  itsScaType  = typeIdOf(T);
  itsElemSize = sizeof(T);
  itsType     = typeIdOfArray(T,N);
  init(array.shape(),flags);
  // after an init, itsArray contains a valid array of the given shape,
  // so we can assign the other array to it, to copy the data over
  *static_cast<blitz::Array<T,N>*>(itsArray) = array;
}

#ifdef HAVE_AIPSPP
template<class T>
inline bool DataArray::isStringArray (const casa::Array<T> &)
{ return False; }
  
template<>
inline bool DataArray::isStringArray (const casa::Array<casa::String> &)
{ return True; }

template<class T> 
inline bool DataArray::verifyAipsType (const T*) const
{
  return itsScaType == typeIdOf(T);
}

template<> 
inline bool DataArray::verifyAipsType (const casa::String*) const
{
  return itsScaType == Tpstring;
}

//##ModelId=3E9BD9190074
inline void DataArray::copyStringArray (const void *source)
{
  const casa::String *data = static_cast<const casa::String*>(source);
  string *dest = reinterpret_cast<string *>(itsArrayData),*end = dest + itsSize;
  for( ; dest < end; dest++,data++ )
    *dest = *data;
}

// templated constructor from an AIPS++ array
template<class T>
DataArray::DataArray (const casa::Array<T> &array,int flags, int )  // shm_flags not yet used
: NestableContainer(),
  itsArray    (0)
{
  initSubArray();
  itsScaType  = isStringArray(array) ? Tpstring : typeIdOf(T);
  itsElemSize = isStringArray(array) ? sizeof(casa::String) : sizeof(T);
  itsType     = TpArray(itsScaType,array.ndim());
  init(array.ndim() ? LoShape(array.shape()) : LoShape(0),flags);
  // after an init, itsArray contains a valid array of the given shape,
  // so we can copy the data over
  // BUG here! use a more efficient AIPS++ array iterator
  bool del;
  const T *data = array.getStorage(del);
  if( isStringArray(array) )
    copyStringArray(data);
  else
    memcpy(itsArrayData,data,itsSize*itsElemSize);
  array.freeStorage(data,del);
}


template<class T>
casa::Array<T> DataArray::copyAipsArray (const T* dum) const
{
  FailWhen( !valid(),"invalid DataArray" );
  FailWhen( !verifyAipsType(dum),"array type mismatch" );
  return casa::Array<T>(itsShape,reinterpret_cast<const T*>(itsArrayData));
}

template<class T>
casa::Array<T> DataArray::refAipsArray (const T*)
{
  FailWhen( !valid(),"invalid DataArray" );
  FailWhen( !isWritable(),"r/w access violation" );
  FailWhen( !verifyAipsType(dum),"array type mismatch" );
  return casa::Array<T>(itsShape,itsArrayData,SHARE);
}

#endif

#endif
