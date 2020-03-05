//  NumArray.h: casacore::Array container (using Blitz Arrays)
//
//  Copyright (C) 2002-2007
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  and The MeqTree Foundation
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
//  Revision 1.44  2006/06/14 17:41:49  smirnov
//  Added missing innitialization of "writable_ref" flag
//
//  Revision 1.43  2006/06/03 11:25:34  smirnov
//  Added NumArray methods to make an array that is a reference to a slice through
//  another array.
//  Revised VellsSlicer so that it can represent the slice as a Vells.
//
//  Revision 1.42  2006/01/31 12:23:09  smirnov
//  Common renamed to TimBase
//
//  Revision 1.41  2005/09/15 11:46:44  smirnov
//  Revised error reporting to allow hierarchical exceptions
//
//  Revision 1.40.2.1  2005/09/13 06:34:45  smirnov
//  Revising the Exceptions mechanism to allow hierarchical exceptions to accumulate.
//
//  Revision 1.40  2005/08/15 12:41:58  smirnov
//  Upped the max array rank to 16.
//  Split up NumArray LUT-functions into 8 separate .cc files to speed up
//  compilation, with the rank up to 16 all those methods really took ages
//  to compile.
//
//  Revision 1.39  2005/05/20 13:35:53  smirnov
//  %[ER: ]%
//  Some speedups to HIIDs and Containers, cut down on memory allocs/reallocs
//
//  Revision 1.38  2005/05/17 21:15:07  smirnov
//  %[ER: ]%
//  Fixed memory leak in NumArray.
//  Misc cleanups to nodes to make memory leaks easier to find.
//
//  Revision 1.37  2005/03/24 15:03:35  smirnov
//  %[ER: ]%
//  Fixed bug in conversion of arrays to Glish
//  Fixed ordering in Solver output
//
//  Revision 1.36  2005/02/03 12:54:53  smirnov
//  %[ER: 16]%
//  1. Added support for flag Vells and flagging. Not yet fully tested,
//  but works with existsing test scripts.
//  2. Fixed major bug in toBlock()ing of Vells (block had the wrong objectId in it)
//  3. Revised GaussNoise and added support for blitz++ random generators
//
//  Revision 1.35  2005/01/24 14:47:43  smirnov
//  %[ER: ]%
//  Changed all BObj derivatives to have a standard BObj::Header at the start
//  of the first block in their toBlock representation. This gives the object
//  type and total block count, and thus makes blocksets completely self-contained.
//
//  Revision 1.34  2005/01/21 15:54:38  smirnov
//  %[ER: ]%
//  Made the changeover to C-storage Lorrays (i.e., use default
//  blitz storage -- row-major -- and convert to aips++ arrays on the fly)
//
//  Revision 1.33  2005/01/19 17:46:41  smirnov
//  %[ER: ]%
//  A number of small changes to accomodate gcc-3.4.3.
//  (Can't link with it at the moment due to some aips++ probs)
//
//  Revision 1.32  2005/01/17 13:53:04  smirnov
//  %[ER: 16]%
//  DMI completely revised to DMI2
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
//  Extended access by pointer in NumArray
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
//  Added arrays accessors to NumArray
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
//  Fixed Lorray support in NumArrays, etc.
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
//  Added isScalar(tid) to NumArray.
//  Fixed isContiguous() in DataField.
//
//  Revision 1.1  2002/04/05 13:05:46  gvd
//  First version
//
#ifndef DMI_NUMARRAY_H
#define DMI_NUMARRAY_H

#include <TimBase/Lorrays.h>
#include <TimBase/Thread/Mutex.h>
#include <TimBase/Thread/Key.h>
#include <DMI/DMI.h>
#include <DMI/Container.h>
#include <DMI/NumArrayFuncs.h>

#ifdef HAVE_AIPSPP
#include <casacore/casa/Arrays.h>
#include <TimBase/BlitzToAips.h>
#endif

#pragma types #DMI::NumArray


// We assume Blitz support here, AIPS++ can be re-integrated later
#ifndef LORRAYS_USE_BLITZ
  #error This version of NumArray requires Blitz Lorrays
#endif

namespace DMI
{

//##ModelId=3DB949AE00C5
class NumArray : public Container
{
public:
  // Array<T,N> is a traits-type structure defining various types 
  // and constants for a <T,N> array. This is meant to isolate us from
  // blitz++ types.
  template<class T,int N> 
  struct Traits
  {
    public:
        typedef blitz::Array<T,N> Array;
        typedef T Element;
        enum    { 
                  Rank = N,
                  ElementTypeId = DMITypeTraits<T>::typeId,
                  ArrayTypeId = TpArray_int(ElementTypeId,N),
                };
  };
    
  // Create the object without an array in it.
    //##ModelId=3DB949AE039F
  NumArray ();

  // Create the object with an array of the given shape.
  // flags: DMI::NOZERO to skip initialization of array with 0
  // realtype is required for derived classes -- they should pass in their
  // type id here, as the array block is filled in the constructor and
  // the virtual objectType() when called from within does not return the
  // correct type
    //##ModelId=3DB949AE03A4
  NumArray (TypeId type,const LoShape & shape,int flags=0,TypeId realtype=0);
  
  // Create the object, and initialize data from array. "other" should point 
  // to a Lorray<T,N> object (where T,N correspond to array_tid)
    //##ModelId=3DB949AE03AF
  NumArray (TypeId array_tid,const void *other,TypeId realtype=0);

  // templated constructor to create a copy of the given Lorray.
  template<class T,int N>
  explicit NumArray (const typename Traits<T,N>::Array & array,TypeId realtype=0);
  // an extra version for explicit blitz naming, to keep the compiler happy
  template<class T,int N>
  explicit NumArray (const blitz::Array <T,N> & array,TypeId realtype=0);
  
#ifdef HAVE_AIPSPP
  // templated constructor makes a copy of the given AIPS++ array
  template<class T>
  explicit NumArray (const casacore::Array<T> & array,TypeId realtype=0);
  
  // templated method to init with a copy of the given AIPS++ array
  template<class T>
  void init (const casacore::Array<T> & array,TypeId realtype=0);
#endif

  // Copy (ref/cow semantics unless DMI::DEEP is specified).
    //##ModelId=3F5487DA034E
  NumArray (const NumArray& other, int flags=0, int depth=0,TypeId realtype=0);

    //##ModelId=3DB949AE03B8
  ~NumArray();

  // Assignment (ref/cow semantics).
    //##ModelId=3DB949AE03B9
  NumArray& operator = (const NumArray& other);
  
  // method to make a writable reference to a slice through another NumArray
  void reference (void * pdata,const LoShape &shape,const LoShape &strides,const NumArray &other)
  { make_reference(pdata,true,shape,strides,other); }

  // method to make a const reference to a slice through another NumArray
  void reference (const void * pdata,const LoShape &shape,const LoShape &strides,const NumArray &other)
  { make_reference(const_cast<void*>(pdata),false,shape,strides,other); }
  
  // method to make a writable reference to a slice through another NumArray
  template<class T,int N>
  void reference (blitz::Array<T,N> &subarray,NumArray &other)
  { make_reference(subarray.data(),true,subarray.shape(),subarray.stride(),other); }

  // method to make a const reference to a slice through another NumArray
  template<class T,int N>
  void reference (const blitz::Array<T,N> &subarray,const NumArray &other)
  { make_reference(const_cast<T*>(subarray.data()),false,subarray.shape(),subarray.stride(),other); }
  
  // Initialize everything and create array.
  // This can be used to init an array that was created via the default constructor.
  // flags: DMI::NOZERO to skip init of array
  // realtype only needs to be supplied when calling from constructor
  // (otherwise the virtual objectType() is used)
  void init (TypeId type,const LoShape & shape,int flags=0,TypeId realtype=0);
 
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
  //  argument allows you to say "function_one((T*)0)" instead)
  template<class T>
  casacore::Array<T> copyAipsArray (const T*) const;
#endif
  
    //##ModelId=400E4D68035F
  // return pointer to underlying array object, checking element type and rank
  const void * getConstArrayPtr (TypeId element_tid,uint nrank) const;
  // return pointer to underlying array object, checking array type and rank
  const void * getConstArrayPtr (TypeId array_tid) const;
  
  void * getArrayPtr (TypeId element_tid,uint nrank)
  { Thread::Mutex::Lock lock(mutex()); makeWritable(); return const_cast<void*>(getConstArrayPtr(element_tid,nrank)); }
  void * getArrayPtr (TypeId array_tid)
  { Thread::Mutex::Lock lock(mutex()); makeWritable(); return const_cast<void*>(getConstArrayPtr(array_tid)); }
  
  template<class T,int N>
  const typename Traits<T,N>::Array & getConstArray (Type2Type<T> =Type2Type<T>(),Int2Type<N> =Int2Type<N>()) const
  { return *static_cast<const typename Traits<T,N>::Array *>(getConstArrayPtr(typeIdOf(T),N)); }
  
  template<class T,int N>
  typename Traits<T,N>::Array & getArray (Type2Type<T> =Type2Type<T>(),Int2Type<N> =Int2Type<N>()) 
  { Thread::Mutex::Lock lock(mutex()); makeWritable(); 
    return *static_cast<typename Traits<T,N>::Array*>(
            const_cast<void*>(getArrayPtr(typeIdOf(T),N))); }
  
  template<class T,int N>
  void getConstArrayPtr (const typename Traits<T,N>::Array * &ptr) const
  { ptr = static_cast<const typename Traits<T,N>::Array*>(getConstArrayPtr(typeIdOf(T),N)); }

  template<class T,int N>
  void getArrayPtr (typename Traits<T,N>::Array * &ptr) 
  { ptr = static_cast<typename Traits<T,N>::Array*>(getArrayPtr(typeIdOf(T),N)); }
  
    //##ModelId=400E4D680386
  const void * getConstDataPtr () const
  { return itsArrayData; }
  
    //##ModelId=400E4D68038A
  void * getDataPtr () 
  { Thread::Mutex::Lock lock(mutex()); makeWritable(); return itsArrayData; }
  
  // Return the object type (TpNumArray).
    //##ModelId=3DB949AE03BE
  virtual TypeId objectType() const;

  // Reconstruct the NumArray object from a BlockSet.
    //##ModelId=3DB949AE03C0
  virtual int fromBlock (BlockSet& set);

  // Add the NumArray object to the BlockSet.
    //##ModelId=3DB949AE03C5
  virtual int toBlock (BlockSet& set) const;

  // Clone the object.
    //##ModelId=3DB949AE03CB
  virtual CountedRefTarget* clone (int flags = 0, int depth = 0) const;

  // Insertion is not possible (throws exception).
    //##ModelId=3DB949AE03E5
  virtual int insert (const HIID& id,ContentInfo &info);

  // The size is the number of array elements.
    //##ModelId=3DB949AF0007
  virtual int size (TypeId tid = 0) const;

  // The actual type of the array (TpArray_float, etc.).
    //##ModelId=3DB949AF000C
  virtual TypeId type() const;
  
  // Ensures writability of underlying data block, inlined here for speed
  void makeWritable ()
  {
    Thread::Mutex::Lock _nclock(mutex());
    if( itsWritableRef )
      return;
    if( itsData.privatize() )
    {
      itsArrayData = itsData().cdata() + itsDataOffset;
      NumArrayFuncs::assignDataReference(itsScaType,itsArray,itsArrayData,itsShape);
    }
  }
  
  // Parse a HIID describing a subset and fill start,end,incr.
  // NB: "end" is one past ending position at each axis: 
  //        i.e. [start,end) is the interval, using conventional notation.
  // It fills in keepAxes telling which axes should be kept in the
  // subarray. Returns number of axes to keep.
    //##ModelId=3DB949AF000E
  int parseHIID (const HIID& id, LoPos& st, LoPos& end,LoPos& incr, 
                 vector<bool> &keepAxes) const;
  
    //##ModelId=3F5487DB0110
  string sdebug ( int detail = 0,const string &prefix = "",
                  const char *name = 0 ) const;
  
    //##ModelId=3DB949AF001C
  typedef CountedRef<NumArray> Ref;

protected:
    //##ModelId=3DB949AE03DA
  virtual int get (const HIID& id,ContentInfo &info,bool nonconst,int flags) const;

private:
  // Initialize internal shape and create array using the given shape.
  // flags: DMI::NOZERO to skip init of array
  // realtype only needs to be supplied when calling from constructor
  // (otherwise the virtual objectType() is used)
    //##ModelId=3DB949AF0024
  void init (const LoShape & shape,int flags=0,TypeId realtype=0);

  // method to make this array a reference to a slice through another NumArray
  // if writable=true, 
  void make_reference (void * pdata,bool writable,
            const LoShape &shape,const LoShape &strides,const NumArray &other);

  // Create the actual casacore::Array object.
  // It is created from the array data part in the SmartBlock.
    //##ModelId=3DB949AF002B
  void makeArray();

  // Clear the object (thus remove the casacore::Array).
    //##ModelId=3DB949AF002C
  void clear();

  // Clone the object.
    //##ModelId=3DB949AF002E
  void cloneOther (const NumArray& other, int flags, int depth, bool constructing,TypeId realtype);

    //##ModelId=3DB949AE036D
  LoShape    itsShape;          // actual shape
  
  TypeId     itsType;           // array TypeId
    //##ModelId=3DB949AE0379
  TypeId     itsScaType;        // scalar data type matching the array type
    //##ModelId=3DB949AE0383
  size_t     itsElemSize;       // #bytes of an array element
    //##ModelId=3DB949AE0389
  size_t     itsSize;           // total size of array (in elements)
    //##ModelId=3E9BD91703CC
  size_t     itsDataOffset;     // array data offset in SmartBlock
    //##ModelId=3DB949AE038E
  char*      itsArrayData;      // pointer to array data in SmartBlock
    //##ModelId=3DB949AE0394
  // void *     itsArray;
  
  // blitz array object created here via placement-new
  unsigned char itsArray [sizeof(blitz::Array<dcomplex,10>)];

  // true when object is valid
  bool       itsArrayValid;
  
  // true when we are a writable ref to another NumArray, in this case
  // no attempt is made to COW the underlying block.
  bool       itsWritableRef;

  //##ModelId=3DB949AE0370
  BlockRef    itsData;
  
  class Header : public BObj::Header
  {
    public: TypeId sca_tid;
            uint rank;
            uint shape[];
  };


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
  static bool isStringArray (const casacore::Array<T> &);
  // helper function returns True if array contains the same data type
  // (with AIPS++ casacore::String matching Tpstring)
  template<class T>
  bool verifyAipsType (const T*) const;
  // helper function copies strings from source array
#endif
};

DefineRefTypes(NumArray,NumArrayRef);

inline bool NumArray::valid () const
{
  return itsArrayValid;
}

    
// returns rank of array
//##ModelId=3E9BD91800B4
inline int NumArray::rank () const
{
  return itsShape.size();
}
  
// returns shape of array
//##ModelId=3E9BD91800B7
inline const LoShape & NumArray::shape () const
{
  return itsShape;
}
  
// returns type of array element
// (the virtual type() method, below, overriding the abstract one in 
// NestableContainer, will return the array type)
//##ModelId=3E9BD91800B9
inline TypeId NumArray::elementType () const
{
  return itsScaType;
}

// templated constructor from an array
template<class T,int N>
NumArray::NumArray (const typename Traits<T,N>::Array & array,TypeId realtype)
: Container(),
  itsArrayValid(false),
  itsWritableRef(false)    
{
  initSubArray();
  itsScaType  = typeIdOf(T);
  itsElemSize = sizeof(T);
  itsType     = typeIdOfArray(T,N);
  init(array.shape(),DMI::NOZERO,realtype);
  // after an init, itsArray contains a valid array of the given shape,
  // so we can assign the other array to it, to copy the data over
  *reinterpret_cast<typename Traits<T,N>::Array*>(itsArray) = array;
}

template<class T,int N>
NumArray::NumArray (const blitz::Array<T,N> &array,TypeId realtype)
: Container(),
  itsArrayValid(false),
  itsWritableRef(false)    
{
  initSubArray();
  itsScaType  = typeIdOf(T);
  itsElemSize = sizeof(T);
  itsType     = typeIdOfArray(T,N);
  init(array.shape(),DMI::NOZERO,realtype);
  // after an init, itsArray contains a valid array of the given shape,
  // so we can assign the other array to it, to copy the data over
  *reinterpret_cast<blitz::Array<T,N>*>(itsArray) = array;
}

#ifdef HAVE_AIPSPP
template<class T>
inline bool NumArray::isStringArray (const casacore::Array<T> &)
{ return false; }
  
template<>
inline bool NumArray::isStringArray (const casacore::Array<casacore::String> &)
{ return true; }

template<class T> 
inline bool NumArray::verifyAipsType (const T*) const
{
  return itsScaType == typeIdOf(T);
}

template<> 
inline bool NumArray::verifyAipsType (const casacore::String*) const
{
  return itsScaType == Tpstring;
}

// templated constructor from an AIPS++ array
template<class T>
NumArray::NumArray (const casacore::Array<T> &array,TypeId realtype)
: Container(),
  itsArrayValid(false),
  itsWritableRef(false)    
{
  initSubArray();
  init(array,realtype);
}

template<class T>
void NumArray::init (const casacore::Array<T> &array,TypeId realtype)
{
  FailWhen( array.ndim() > 10,"NumArray(casacore::Array<T>): illegal array rank" );
  itsScaType  = isStringArray(array) ? Tpstring : typeIdOf(T);
  itsElemSize = isStringArray(array) ? sizeof(string) : sizeof(T);
  itsType     = TpArray(itsScaType,array.ndim());
  init(array.ndim() ? LoShape(array.shape()) : LoShape(0),DMI::NOZERO,realtype);
  // after an init, itsArray contains a valid array of the given shape,
  // so we can copy the data over
  switch( array.ndim() )
  {
    case 0:   break;
    case 1:   B2A::assignArray(*reinterpret_cast<typename Traits<T,1>::Array*>(itsArray),array); break;
    case 2:   B2A::assignArray(*reinterpret_cast<typename Traits<T,2>::Array*>(itsArray),array); break;
    case 3:   B2A::assignArray(*reinterpret_cast<typename Traits<T,3>::Array*>(itsArray),array); break;
    case 4:   B2A::assignArray(*reinterpret_cast<typename Traits<T,4>::Array*>(itsArray),array); break;
    case 5:   B2A::assignArray(*reinterpret_cast<typename Traits<T,5>::Array*>(itsArray),array); break;
    case 6:   B2A::assignArray(*reinterpret_cast<typename Traits<T,6>::Array*>(itsArray),array); break;
    case 7:   B2A::assignArray(*reinterpret_cast<typename Traits<T,7>::Array*>(itsArray),array); break;
    case 8:   B2A::assignArray(*reinterpret_cast<typename Traits<T,8>::Array*>(itsArray),array); break;
    case 9:   B2A::assignArray(*reinterpret_cast<typename Traits<T,9>::Array*>(itsArray),array); break;
    case 10:  B2A::assignArray(*reinterpret_cast<typename Traits<T,10>::Array*>(itsArray),array); break;
  }
}


template<class T>
casacore::Array<T> NumArray::copyAipsArray (const T* dum) const
{
  FailWhen( !valid(),"invalid NumArray" );
  FailWhen( !verifyAipsType(dum),"array type mismatch" );
  switch( rank() )
  {
    case 0: return casacore::Array<T>();
    case 1: return B2A::copyBlitzToAips(*reinterpret_cast<const typename Traits<T,1>::Array*>(itsArray));
    case 2: return B2A::copyBlitzToAips(*reinterpret_cast<const typename Traits<T,2>::Array*>(itsArray));
    case 3: return B2A::copyBlitzToAips(*reinterpret_cast<const typename Traits<T,3>::Array*>(itsArray));
    case 4: return B2A::copyBlitzToAips(*reinterpret_cast<const typename Traits<T,4>::Array*>(itsArray));
    case 5: return B2A::copyBlitzToAips(*reinterpret_cast<const typename Traits<T,5>::Array*>(itsArray));
    case 6: return B2A::copyBlitzToAips(*reinterpret_cast<const typename Traits<T,6>::Array*>(itsArray));
    case 7: return B2A::copyBlitzToAips(*reinterpret_cast<const typename Traits<T,7>::Array*>(itsArray));
    case 8: return B2A::copyBlitzToAips(*reinterpret_cast<const typename Traits<T,8>::Array*>(itsArray));
    case 9: return B2A::copyBlitzToAips(*reinterpret_cast<const typename Traits<T,9>::Array*>(itsArray));
    case 10:return B2A::copyBlitzToAips(*reinterpret_cast<const typename Traits<T,10>::Array*>(itsArray));
    default: Throw("copyAipsArray(): array rank too high");
  }
}

#endif

};
#endif
