//  DataArray.cc: Array container (using Blitz Arrays)
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
//  Revision 1.34  2005/01/07 07:56:28  diepen
//  %[ER: 222]%
//  Use AIPS++ casa namespace
//
//  Revision 1.33  2004/10/03 20:59:26  smirnov
//  %[ER: 16]%
//  Fixed error in DataArray::privatize
//
//  Revision 1.32  2004/03/17 07:51:20  smirnov
//  %[ER: 16]%
//  Extended access by pointer in DataArray
//
//  Revision 1.31  2004/01/28 16:23:34  smirnov
//  %[ER: 16]%
//  Revised the hook infrastructure, got rid of NC::writable flag.
//  Simplified CountedRefs
//
//  Revision 1.30.2.1  2004/01/26 14:57:40  smirnov
//  %[ER: 16]%
//  Commiting overhaul of Hook classes
//
//  Revision 1.30  2004/01/21 11:08:58  smirnov
//  %[ER: 16]%
//  brought the Rose model up-to-date; this got a bunch of IDs inserted into the
//  sources, hence the massive update.
//
//  Revision 1.29  2003/11/12 16:57:18  smirnov
//  %[ER: 16]%
//  Added arrays accessors to DataArray
//
//  Revision 1.28  2003/10/20 14:40:56  smirnov
//  %[ER: 37]%
//  Minor fixes to improve parsing of nested data structures
//
//  Revision 1.27  2003/10/09 17:43:04  smirnov
//  %[ER: 16]%
//  Re-enabled single element access to DataArray, as removing it broke
//  compatibility with Glish. Did it properly this time!
//
//  Revision 1.26  2003/10/08 12:29:18  diepen
//  %[PR: 36]%
//  Removed DataArray functionality to retrieve an array as a scalar
//
//  Revision 1.25  2003/09/10 15:11:05  smirnov
//  %[BugId: ]%
//  Various small fixes & cleanups.
//  Allowed numeric (i.e. single-index) field names in DataRecord. The old
//  way of accessing field by its number is available via the special HIID "#.n"
//  (AidHash|n).
//  Fixed bug with resizing DataFields with a dynamic type content -- these would
//  fail a toBlock/fromBlock after a resize.
//
//  Revision 1.24  2003/05/14 10:28:11  smirnov
//  %[BugId: 26]%
//  Fixed bug when constructing from a 0-dim AIPS++ array
//
//  Revision 1.23  2003/04/29 07:19:31  smirnov
//  %[BugId: 26]%
//  Various updates to hooks
//
//  Revision 1.22  2003/04/09 09:50:13  smirnov
//  %[BugId: 26]%
//  Revised DataRecord to hold any NC (not just a DataField). This makes for
//  far more consistent subscripting into records.
//
//  Revision 1.21  2003/01/08 10:32:41  diepen
//  %[BugId: 76]%
//  <ostream> was not found for gcc2.95.3
//  Fixed typo in DataArray line 412
//
//  Revision 1.20  2002/12/09 08:22:31  smirnov
//  %[BugId: 112]%
//  Simplified string support in DataAarray
//
//  Revision 1.19  2002/12/05 10:15:22  smirnov
//  %[BugId: 112]%
//  Fixed Lorray support in DataArrays, etc.
//  Revised AIPS++ hooks.
//
//  Revision 1.18  2002/12/03 20:36:14  smirnov
//  %[BugId: 112]%
//  Ported DMI to use Lorrays (with blitz arrays)
//
//  Revision 1.17  2002/10/29 13:10:38  smirnov
//  %[BugId: 26]%
//  Re-worked build_aid_maps.pl and TypeIterMacros.h to enable on-demand
//  importing of data types from other packages. Basically, data types from package
//  X will be pulled in by NestableContainer only when included from
//  package Y that has an explicit dependence on package X. DMI itself depends
//  only on Common.
//
//  Migrated to new Rose C++ add-in, so all Rose markup has changed.
//
//  Revision 1.16  2002/07/30 13:08:03  smirnov
//  %[BugId: 26]%
//  Lots of fixes for multithreading
//
//  Revision 1.15  2002/07/03 14:13:16  smirnov
//  %[BugId: 26]%
//  Major overhaul to enable multithreading (use "-pthread -DUSE_THREADS" flags
//  to g++ to enable).
//  Added NCIter classes.
//
//  Revision 1.14  2002/06/11 12:15:08  smirnov
//  %[BugId: 26]%
//  Further fixes to array-mode hook addressing.
//  Added an optional tid argument to NestableContainer::size().
//
//  Revision 1.13  2002/06/10 12:39:18  smirnov
//  %[BugId: 26]%
//  Revised NestableContainer::get() interface to return info in a ContentInfo
//  structure.
//  Added optional size argument to hook.as_type_p() and _wp() methods.
//  Cleaned up size handling, added working as_vector<T> and =(vector<T>).
//
//  Revision 1.12  2002/06/07 14:22:48  smirnov
//  %[BugId: 26]%
//  Many revisions related to support of arrays and vectors (including AIPS++) by
//  hooks. Checking in now because I plan to modify the NestableContainer interface.
//
//  Revision 1.11  2002/05/30 12:15:13  diepen
//
//  %[BugId: 25]%
//  Added the required constructors
//
//  Revision 1.10  2002/05/22 13:53:43  gvd
//  %[BugId: 6]%
//  Fixed an invalid cast (found by KAI C++)
//
//  Revision 1.9  2002/05/14 09:48:10  gvd
//  Fix a few problems in cloneOther and reinit
//
//  Revision 1.8  2002/05/14 09:31:28  oms
//  Fixed bug with itsElemSize not initialized in clone
//
//  Revision 1.7  2002/05/14 08:08:03  oms
//  Added operator () to hooks.
//  Fixed flags in DataArray.
//
//  Revision 1.6  2002/05/13 08:59:42  gvd
//  Fixed cloneOther (removed assignment) and added Tpbool, etc. to constructor
//
//  Revision 1.5  2002/05/07 11:46:00  gvd
//  The 'final' version supporting array subsets
//
//  Revision 1.3  2002/04/08 14:27:07  oms
//  Added isScalar(tid) to DataArray.
//  Fixed isContiguous() in DataField.
//
//  Revision 1.2  2002/04/08 13:53:48  oms
//  Many fixes to hooks. Added NestableContainer::isContiguous() method.
//
//  Revision 1.1  2002/04/05 13:05:46  gvd
//  First version
//


#define NC_SKIP_HOOKS 1
#include "DataArray.h"

static NestableContainer::Register reg(TpDataArray,true);

  // Methods for the method table are naturally implemented via
  // templates. Refer to DataArray.cc to see how they are populated.
  
// templated method to allocate an empty Lorray(N,T)
template<class T,int N>
static void * newArrayDefault ()
{ 
  return new blitz::Array<T,N>; 
}

// templated method to allocate a Lorray(N,T) of the given shape, using
// pre-existing data
template<class T,int N>
static void * newArrayWithData (void *data,const LoShape & shape)
{ 
  return new blitz::Array<T,N>(static_cast<T*>(data),shape,blitz::neverDeleteData); 
} 

// templated method to assign the data (using the given shape & stride)
// to an array
template<class T,int N>
static void referenceDataWithStride (void *parr,void *data,const LoShape & shape,const LoShape &stride)
{ 
  blitz::Array<T,N> tmp(static_cast<T*>(data),shape,stride,blitz::neverDeleteData);
  static_cast<blitz::Array<T,N>*>(parr)->reference(tmp);
}

// templated method to delete a Lorray(N,T) at the given address
template<class T,int N>
static void deleteArray (void *parr)
{ 
  delete static_cast<blitz::Array<T,N>*>(parr); 
}

// templated method to copy one Lorray to another
template<class T,int N>
static void copyArrayImpl (void *target,const void *source)
{ 
  *static_cast<blitz::Array<T,N>*>(target) = 
    *static_cast<const blitz::Array<T,N>*>(source); 
}

// templated method to copy return the shape of a Lorray
template<class T,int N>
static void returnShapeOfArray (LoShape &shape,const void *ptr)
{ 
  shape = static_cast<const blitz::Array<T,N>*>(ptr)->shape(); 
}


// populate the method tables via the DoForAll macros
#define OneLine(T,arg) { DoForAllArrayRanks1(OneElement,T) }

DataArray::AllocatorWithData DataArray::allocatorWithData[NumTypes][MaxLorrayRank] =
{
#define OneElement(N,T) &newArrayWithData<T,N>
  DoForAllArrayTypes1(OneLine,)
#undef OneElement
};

DataArray::AssignWithStride DataArray::assignerWithStride[NumTypes][MaxLorrayRank] =
{
#define OneElement(N,T) &referenceDataWithStride<T,N>
  DoForAllArrayTypes1(OneLine,)
#undef OneElement
};

DataArray::AllocatorDefault DataArray::allocatorDefault[NumTypes][MaxLorrayRank] =
{
#define OneElement(N,T) &newArrayDefault<T,N>
  DoForAllArrayTypes1(OneLine,)
#undef OneElement
};

DataArray::Destructor DataArray::destructor[NumTypes][MaxLorrayRank] =
{
#define OneElement(N,T) &deleteArray<T,N>
  DoForAllArrayTypes1(OneLine,)
#undef OneElement
};

//##ModelId=3F5487DA023F
DataArray::ArrayCopier DataArray::copier[NumTypes][MaxLorrayRank] =
{
#define OneElement(N,T) &copyArrayImpl<T,N>
  DoForAllArrayTypes1(OneLine,)
#undef OneElement
};

//##ModelId=3F5487DA0273
DataArray::ShapeOfArray DataArray::shapeOfArray[NumTypes][MaxLorrayRank] =
{
#define OneElement(N,T) &returnShapeOfArray<T,N>
  DoForAllArrayTypes1(OneLine,)
#undef OneElement
};

#undef OneLine  

// initializes num std::string objects located at start
static void initStringArray (void *start,int num)
{
  string *ptr = static_cast<string*>(start),*end = ptr+num,*dum;
  for( ; ptr<end; ptr++ )
    dum = new(ptr) string; 
}
// destroys num std::string objects located at start
static void destroyStringArray (void *start,int num)
{
  string *ptr = static_cast<string*>(start),*end = ptr+num;
  for( int i=0; i<num; i++,ptr++ )
    for( ; ptr<end; ptr++ )
      ptr->~string();
}

//##ModelId=3DB949AE039F
DataArray::DataArray ()
: NestableContainer(),
  itsArray    (0)
{
  initSubArray();
}

//##ModelId=3DB949AE03A4
DataArray::DataArray (TypeId type, const LoShape & shape,int flags,int) // shm_flags not used
: NestableContainer(),
  itsArray    (0)
{
  initSubArray();
  // check arguments
  FailWhen( shape.size() < 1 || shape.size() > MaxLorrayRank,"invalid array rank");
  if( TypeInfo::isArrayable(type) )
  {
    itsType = TpArray(type,shape.size());
    itsScaType = type;
  }
  else 
  {
    FailWhen( !TypeInfo::isArray(type),
        Debug::ssprintf("TypeId %s is not an array",type.toString().c_str()));
    itsType = type;
    itsScaType = TypeInfo::typeOfArrayElem(type);
    uint rank = TypeInfo::rankOfArray(type);
    FailWhen( rank != shape.size(),
        Debug::ssprintf("TypeId %s conflicts with shape of rank %d",type.toString().c_str(),shape.size()));
  }
  itsElemSize = type == Tpstring ? sizeof(string) : TypeInfo::find(itsScaType).size;
  init(shape,flags);
}

//##ModelId=3DB949AE03AF
DataArray::DataArray (TypeId tid,const void *other,int flags,int) // shm_flags not used
: NestableContainer(),
  itsArray    (0)
{
  initSubArray();
  // check arguments
  FailWhen( !TypeInfo::isArray(tid),
      Debug::ssprintf("TypeId %s is not an array",tid.toString().c_str()));
  // get rank, element types/sizes
  itsType = tid;
  itsScaType = TypeInfo::typeOfArrayElem(tid);
  uint rank = TypeInfo::rankOfArray(tid);
  FailWhen( rank<1 || rank>MaxLorrayRank,
      Debug::ssprintf("Unsupported array rank %d",rank));
  // get shape from other array
  LoShape shape;
  getShapeOfArray(itsScaType,rank,shape,other);
  FailWhen( shape.size() != rank,"shape of array does not match indicated type" );
  // init internal array
  itsElemSize = itsScaType == Tpstring ? sizeof(string) : TypeInfo::find(itsScaType).size;
  init(shape,flags);
  // copy data
  copyArray(itsScaType,rank,itsArray,other);
}

// instantiate this constructor template for all other types
// #undef __instantiate
// #define __instantiate(T,arg) template DataArray::DataArray (const Array<T>& array,int flags, int shm_flags);
// DoForAllArrayTypes(__instantiate,);
// __instantiate(string,);


//##ModelId=3F5487DA034E
DataArray::DataArray (const DataArray& other, int flags, int depth)
: NestableContainer(),
  itsArray    (0)
{
  initSubArray();
  cloneOther(other,flags,depth);
}

//##ModelId=3DB949AE03B8
DataArray::~DataArray()
{
  clear();
}

//##ModelId=3DB949AE03B9
DataArray& DataArray::operator= (const DataArray& other)
{
  Thread::Mutex::Lock _nclock(mutex());
  if( this != &other ) 
  {
    clear();
    cloneOther(other);
  }
  return *this;
}

//##ModelId=3DB949AF002E
void DataArray::cloneOther (const DataArray& other, int flags, int)
{
  Thread::Mutex::Lock _nclock(mutex());
  Thread::Mutex::Lock _nclock1(other.mutex());
  Assert (!valid());
  if( other.itsArray ) 
  {
    itsScaType  = other.itsScaType;
    itsType     = other.itsType;
    itsShape    = other.itsShape;
    itsSize     = other.itsSize;
    itsElemSize = other.itsElemSize;
    itsDataOffset = other.itsDataOffset;
    itsData.copy(other.itsData).privatize(DMI::WRITE|DMI::LOCK);
    itsArrayData = const_cast<char*>(itsData->cdata()) + itsDataOffset;
    // strings need to be initialized & copied over explicitly
    if( itsScaType == Tpstring )
    {
      string *dest = reinterpret_cast<string*>(itsArrayData), 
             *end = dest + itsSize;
      const string *src = reinterpret_cast<string*>(other.itsArrayData);
      // construct & assign strings in block
      for( ; dest < end; dest++,src++ )
        *(new(dest) string) = *src;
    }
    makeArray();
  }
}

void DataArray::makeArray ()
{
  itsArray = allocateArrayWithData(itsScaType,itsArrayData,itsShape);
}

//##ModelId=3E9BD91803CC
void * DataArray::makeSubArray (void *data,const LoShape & shape,const LoShape &stride) const
{
  // first, figure out which subarray object to assign to the data.
  // parr will point to this, eventually
  void *parr;
  int rank = shape.size();
#ifdef USE_THREADS
  // subarrays reside in a per-thread map
  Thread::ThrID self = Thread::self();
  SubArrayMap::iterator iter = itsSubArrayMap.find(self);
  // no entry for this thread? Init one
  if( iter == itsSubArrayMap.end() )
  {
    parr = allocateArrayDefault(itsScaType,rank);
    SubArray subarr = { parr,rank };
    itsSubArrayMap[self] = subarr;
  }
  else // use existing subarray if same rank
  {
    FailWhen(!iter->second.ptr,"null subarray pointer");
    if( iter->second.rank != rank )
    {
      destroyArray(itsScaType,iter->second.rank,iter->second.ptr);
      parr = iter->second.ptr = allocateArrayDefault(itsScaType,rank);
      iter->second.rank = rank;
    }
    else
      parr = iter->second.ptr;
  }
#else
  // non-threaded version simply allocates an array on demand
  parr = itsSubArray.ptr;
  if( !parr || itsSubArray.rank != rank )
  {
    if( parr )
      destroyArray(itsScaType,itsSubArray.rank,parr);
    itsSubArray.ptr = parr = allocateArrayDefault(itsScaType,rank);
    itsSubArray.rank = rank;
  }
#endif
  // make the subarray reference the data
  assignWithStride(itsScaType,parr,data,shape,stride);
  return parr;
}

//##ModelId=3DB949AF0024
void DataArray::init (const LoShape & shape,int flags)
{
#ifdef HAVE_AIPSPP
  // sanity check -- can we treat string as an AIPS++ String?
  FailWhen( sizeof(string) != sizeof(casa::String),"AIPS++ String is not equivalent to std::string" );
#endif
      
  itsShape = shape;
  itsSize  = shape.product();
  int sz = sizeof(int) * (2 + shape.size());
  // Align data on 8 bytes.
  itsDataOffset = (sz+7) / 8 * 8;
  sz = itsDataOffset + itsSize*itsElemSize;
  // Allocate enough space in the SmartBlock.
  /// Circumvent temporary SmartBlock problem
  ///  itsData.attach (new SmartBlock (sz, flags, shm_flags),
  itsData.attach(new SmartBlock(sz,flags),DMI::ANONWR|DMI::LOCK);
  void *dataptr = itsData().data();

  // store type, ndim, and shape into block header
  int *hdr = static_cast<int*>(dataptr);
  *hdr++ = itsScaType;
  *hdr++ = shape.size();
  for( uint i=0; i<shape.size(); i++ )
    *hdr++ = shape[i];
  
  // take pointer to data
  itsArrayData = static_cast<char*>(dataptr) + itsDataOffset;
  
  // init string objects, if needed
  if( itsScaType == Tpstring )
    initStringArray(itsArrayData,itsSize);
  
  // allocate the array object
  makeArray();
}

//##ModelId=3DB949AF002C
void DataArray::clear()
{
  Thread::Mutex::Lock _nclock(mutex());
  if( itsArray )
  {
    destroyArray(elementType(),rank(),itsArray);
    // destroy string objects, if needed
    if( itsScaType == Tpstring )
      destroyStringArray(itsArrayData,itsSize);
  }
  
#ifdef USE_THREADS
  for( SubArrayMap::const_iterator iter = itsSubArrayMap.begin();
       iter != itsSubArrayMap.end(); iter ++ )
  {
    FailWhen(!iter->second.ptr,"null subarray pointer");
    destroyArray(elementType(),iter->second.rank,iter->second.ptr);
  }
  itsSubArrayMap.clear();
#else
  if( itsSubArray.ptr )
  {
    destroyArray(elementType(),itsSubArray.rank,itsSubArray.ptr);
    itsSubArray.ptr = 0;
  }
#endif
  itsArray    = 0;
  itsShape.resize (0);
  
  itsData.unlock().detach();
}

//##ModelId=3DB949AE03BE
TypeId DataArray::objectType() const
{
  return TpDataArray;
}

//##ModelId=3DB949AF000C
TypeId DataArray::type () const
{
  return itsType;
}

//##ModelId=3DB949AF0007
int DataArray::size (TypeId tid) const
{
  // by default, return size of scalar type
  if( !tid || tid == itsScaType )
    return itsSize;
  // else return 1 for full array type
  if( tid == itsType )
    return 1;
  // <0 for type mismatch
  return -1;
}

//##ModelId=3DB949AE03C0
int DataArray::fromBlock (BlockSet& set)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf1(2)("%s: fromBlock\n",debug());
  clear();
  
  // Get data block.
  BlockRef href;
  set.pop(href);  
  size_t hsize = href->size();
  FailWhen( hsize < 2*sizeof(int), "malformed data block");
  const int *hdr = static_cast<const int*>(href->data());
  
  // get element type and rank from header
  itsScaType = *hdr++;
  TypeInfo typeinfo = TypeInfo::find(itsScaType);
  FailWhen( typeinfo.category != TypeInfo::NUMERIC && itsScaType != Tpstring,
            "invalid array element type" + itsScaType.toString() ); 
  uint rank = *hdr++;
  FailWhen( rank < 1 || rank > MaxLorrayRank,"invalid array rank" );
  FailWhen( hsize < (2+rank)*sizeof(int), "malformed data block" );
  // derive array type & element size
  itsType = TpArray(itsScaType,rank);
  itsElemSize = itsScaType == Tpstring ? sizeof(string) : typeinfo.size;
  
  // get shape from header & compute total size
  itsShape.resize(rank);
  itsSize = 1;
  for( uint i=0; i<rank; i++ )
    itsSize *= itsShape[i] = *hdr++;
  
  // compute size of data block & offset into it
  size_t blocksize = sizeof(int) * (2 + rank);
  // Align data on 8 bytes.
  itsDataOffset = (blocksize + 7) / 8 * 8;
  blocksize = itsDataOffset + itsSize*itsElemSize;
  
  // strings are a special case since they need to be copied from the block
  if( itsScaType == Tpstring )
  {
    size_t expected_size = (2 + rank + itsSize)*sizeof(int);
    FailWhen( hsize < expected_size,"malformed data block" );
    // actual array to be stored here
    BlockRef newdata(new SmartBlock(blocksize),DMI::ANONWR);
    itsArrayData = newdata().cdata() + itsDataOffset;
    initStringArray(itsArrayData,itsSize);
    // start of string array
    string *pstr = reinterpret_cast<string*>(itsArrayData);
    // hdr now points at array of string lengths
    // string data starts at hdr[itsSize];
    const char *chardata = reinterpret_cast<const char*>(hdr+itsSize);
    // copy strings one by one
    for( int i=0; i<itsSize; i++,pstr++ )
    {
      int len = *hdr++;       // length from header
      expected_size += len;   // adjust expect size & check for spacd
      FailWhen( hsize < expected_size,"malformed data block" );
      // assign to string
      pstr->assign(chardata,len); 
      chardata += len;
    }
    FailWhen( hsize != expected_size,"malformed data block" );
    // xfer data block
    itsData = newdata;
  }
  else // else simply privatize the data block
  {
    FailWhen( blocksize != hsize,"malformed data block");
    itsData = href;
    itsData.privatize(DMI::WRITE|DMI::LOCK);
    itsArrayData = const_cast<char *>(itsData->cdata()) + itsDataOffset;
  }
  // Create the Array object.
  makeArray();
  return 1;
}

//##ModelId=3DB949AE03C5
int DataArray::toBlock (BlockSet& set) const
{
  Thread::Mutex::Lock _nclock(mutex());
  if( !valid() ) 
  {
    dprintf1(2)("%s: toBlock=0 (field empty)\n",debug());
    return 0;
  }
  dprintf1(2)("%s: toBlock\n",debug());
// strings are handled separately since the data needs to be copied out
  if( itsScaType == Tpstring )
  {
    int totlen = 0;
    // count up the string lengths
    string *ptr = reinterpret_cast<string*>(itsArrayData);
    for( int i=0; i<itsSize; i++,ptr++ )
      totlen += ptr->length();
    // allocate block for type, ndim, shape, string lengths & string data
    BlockRef ref(new SmartBlock(
        (2+itsShape.size()+itsSize)*sizeof(int) + totlen),DMI::ANONWR);
    // fill the block, first the header
    int *hdr   = static_cast<int*>(ref().data());
    *hdr++ = Tpstring;
    *hdr++ = itsShape.size();
    for( uint i=0; i<itsShape.size(); i++ )
      *hdr++ = itsShape[i];
    // now store strings & string lengths
    char *data = reinterpret_cast<char*>(hdr + itsSize);
    ptr = reinterpret_cast<string*>(itsArrayData);
    for( int i=0; i<itsSize; i++,ptr++ )
    {
      int len = *hdr++ = ptr->copy(data,string::npos);
      data += len;
    }
    set.push(ref);
  }
  else // else simply push out copy of data block
  {
    set.push(itsData.copy(DMI::READONLY));
  }
  return 1;
}
  
//##ModelId=3DB949AE03CB
CountedRefTarget* DataArray::clone (int flags, int depth) const
{
  return new DataArray (*this, flags, depth);
}

//##ModelId=3DB949AE03D2
void DataArray::privatize (int flags, int)
{
  Thread::Mutex::Lock _nclock(mutex());
  if( !valid() ) 
    return;
  // Privatize the data.
  const char *oldptr = itsData->cdata();
  itsData.privatize(DMI::WRITE|DMI::LOCK);
  // reset array and pointer to array data
  const char *newptr = itsData->cdata();
  if( newptr != oldptr )
  {
    itsArrayData = const_cast<char*>(newptr) + itsDataOffset;
    makeArray();
  }
}

//##ModelId=400E4D68035F
const void * DataArray::getConstArrayPtr (TypeId element_tid,uint nrank) const
{
  FailWhen( itsScaType!=element_tid || nrank != itsShape.size(),
            "can't access "+itsType.toString()+" as "+
            TpArray(element_tid,nrank).toString() );
  return itsArray;
}

const void * DataArray::getConstArrayPtr (TypeId array_tid) const
{
  FailWhen( itsType!=array_tid,
            "can't access "+itsType.toString()+" as "+array_tid.toString() );
  return itsArray;
}

// full HIID -> type can only be Tpfloat
// no HIID   -> type can be TpArray_float (or Tpfloat if array has 1 element)
// partial HIID -> type must be TpArray_float and create such array on heap
//                 which gets deleted by clear()
//##ModelId=3DB949AE03DA
int DataArray::get (const HIID& id, ContentInfo &info,bool nonconst,int flags) const
{
  // non-writability directly determined by constness
  if( flags&DMI::WRITE && !nonconst )
    return -1;
  Thread::Mutex::Lock _nclock(mutex());
  TypeId hint = info.tid;
  info.writable = nonconst;
  int nid = id.length();
  int ndim = itsShape.size();
  // If a full HIID is given, we might need to return a single element
  // which is a scalar. 
//  // If the array itself is scalar (itsSize==1), then it's considered 0-dimensional
  if( nid == ndim )     // full HIID?
  {
    bool single = true;
    LoShape which(LoShape::SETRANK|ndim);
    if( nid ) // non-null HIID => see if it refers to a single array element
    {
      for( int i=0; i<nid; i++ ) 
      {
        which[i] = id[i];
        if( which[i] < 0 ) // all elements for this axis?
        {
	        single = false;
	        break;
        }
      }
    }
    else // this is the case of a single-element array, and a null HIID
    {
      single = false;
      which[0] = 0;
    }
    // have we resolved to a single element?
    if( single )
    {
      // Return a single element in the array.
      info.size = 1;
      info.tid = info.obj_tid = itsScaType;
      for (int i=0; i<nid; i++) 
      {
        FailWhen(which[i] >= itsShape[i],"array position out of range");
      }
      // compute the element offset
      int offset = 0, stride = 1;
      LoShape::const_iterator iwhich = which.begin(), 
                              ishape = itsShape.begin();
      for( ; iwhich != which.end(); iwhich++,ishape++ )
      {
        offset += *iwhich*stride;
        stride *= *ishape;
      }
      info.ptr = itsArrayData + itsElemSize*offset;
      return 1;
    }
  }
  if( nid == 0 )  // else a null HIID 
  {
    if( hint == itsScaType )   // return scalars only if specifically requested
    {
      info.tid = info.obj_tid = itsScaType;
      info.size = itsShape.product();
      info.ptr = itsArrayData;
    }
    else
    {
      info.tid = info.obj_tid = itsType;
      info.size = 1;
      info.ptr = itsArray;
    }
    return 1;
  }
  // If we drop through here, then we have a partial HIID referring to
  // a subset of the array. Figure out which subset.
  LoPos st,end,incr;
  vector<bool> keepAxes;
  // naxes is the number of axes in the subarray.
  // axes in the source array with keepAxes = false are removed (sliced out).
  int naxes = parseHIID(id,st,end,incr,keepAxes);
  // now check the type
  LoShape subshape(LoShape::SETRANK|naxes),
          substride(LoShape::SETRANK|naxes);
  int iax=0, offset=0, stride=1;
  for( int i=0; i<ndim; i++ )
  {
    // stride is the stride of the current (i'th) axis, in elements
    // Get the starting position within this axis and add it to offset
    offset += st[i]*stride;
    // if keeping the axis, then add it to output shape & stride
    if( keepAxes[i] )
    {
      subshape[iax] = (end[i]-st[i])/incr[i];
      substride[iax] = incr[i]*stride;
      iax++;
    }
    stride *= itsShape[i];
  }
  // if callers wants scalars and subarray has only one element, return scalars
  if( hint == itsScaType && subshape.product() == 1 )
  {
    info.tid = info.obj_tid = itsScaType;
    info.ptr = itsArrayData + itsElemSize*offset;
  }
  else
  {
    info.tid = info.obj_tid = TpArray(itsScaType,naxes);
    info.ptr = makeSubArray(itsArrayData + itsElemSize*offset,subshape,substride);
  }
  info.size = 1;
  return 1;
}

//##ModelId=3DB949AF000E
int DataArray::parseHIID (const HIID& id, LoPos & st, LoPos & end,LoPos & incr, 
                          vector<bool> & keepAxes) const
{
  int ndim = itsShape.nelements();
  int nid = id.length();
  // An axis can be removed if a single index is given for it.
  keepAxes.resize(ndim);
  keepAxes.assign(ndim,False);
  // Initialize start, end, and stride to all elements.
  st.resize(ndim);
  st = 0;
  end = itsShape;
  incr.resize(ndim);
  incr = 1;
  
  int nraxes = 0;
  int nr = 0;
  // The user can specify ranges using the syntax st:end:incr
  // where st, end, and incr are optional.
  // If only an st value is given, the axis will later be removed
  // Class HIID transforms a string to a HIID object, where each value and
  // separator is an AtomicID (separator and wildcard have a negative value).
  // When it finds two successive separators, it inserts AidEmpty, so e.g.
  // the string ..::3 will get AidEmpty AidEmpty AidRange AidEmpty AidRange 3.
  // AidEmpty is effectively the same as AidWildcard.
  bool hadRange = nid>0;
  for( int i=0; i<nid; i++ ) 
  {
    if( id[i] == AidRange ) 
    {
      AssertMsg(!hadRange, "HIID " << id.toString()
		    << " does not have a value before range delimiter");
      // 'Colon' found, thus next value for this axis.
      // More than a single start value is given, thus keep the axis.
      nr++;
      keepAxes[nraxes] = True;
      hadRange = true;
    }
    else 
    {
      if( !hadRange ) 
      {
	      nr = 0;
	      nraxes++;
	      AssertMsg (nraxes < ndim, "HIID " << id.toString()
		         << " has more axes than the array (" << ndim << ')');
      }
      hadRange = false;
      if( id[i] < 0 )
      {
	      // Wildcard (or empty)is allowed.
	      AssertMsg( id[i] == AidWildcard  ||  id[i] == AidEmpty,
		         "Invalid id " << id[i].toString()
		         << " in HIID " << id.toString());
        keepAxes[nraxes] = True;
      }
      else 
      {
	      if (nr == 0) 
        {
	        st[nraxes] = id[i];
	        end[nraxes] = id[i] + 1;
	        AssertMsg (st[nraxes] < itsShape[nraxes], "Start " << st[nraxes]
		           << " should be < axis length " << itsShape[nraxes]
		           << " in HIID " << id.toString());
	      }
        else if( nr == 1 ) 
        {
          keepAxes[nraxes] = True;
	        end[nraxes] = id[i].id() + 1;
	        AssertMsg (end[nraxes] > st[nraxes], "End " << end[nraxes]-1
		           << " should be >= start " << st[nraxes]
		           << " in HIID " << id.toString());
        }
        else if( nr == 2 ) 
        {
	        incr[nraxes] = id[i];
	        AssertMsg (incr[nraxes] > 0, "Stride " << incr[nraxes]
		           << " should be > 0 in HIID " << id.toString());
	      }
        else 
        {
	        AssertMsg (0, "Only 3 values (start:end:incr) can be given per axis "
		           "in HIID " << id.toString());
	      }
      }
    }
  }
  AssertMsg (!hadRange, "HIID " << id.toString()
	     << " does not have a value after range delimiter");
  
  int nkeep = 0;
  for( int i=0; i<ndim; i++ )
    if( keepAxes[i] )
      nkeep++;
  
  return nkeep;
}

//##ModelId=3DB949AE03E5
int DataArray::insert (const HIID&,ContentInfo &info)
{
  Throw("insert() not supported for DataArray");
}

//##ModelId=3F5487DB0110
string DataArray::sdebug ( int detail,const string &prefix,const char *name ) const
{
  Thread::Mutex::Lock _nclock(mutex());
  string out;
  if( detail>=0 ) // basic detail
  {
    Debug::appendf(out,"%s/%08x",name?name:"DataArray",(int)this);
  }
  if( detail >= 1 || detail == -1 )   // normal detail
  {
    if( !itsArray )
      out += "empty";
    else
    {
      out += itsType.toString() + " ";
      for( uint i=0; i<itsShape.size(); i++ )
        out += Debug::ssprintf("%c%d",(i?'x':' '),itsShape[i]);
    }
  }
  if( detail >= 2 || detail <= -2 )   // high detail
  {
    if( itsArray )
    {
      // append debug info from block
      string str = itsData.sdebug(2,prefix,"data");
    }
  }
  return out;
}

