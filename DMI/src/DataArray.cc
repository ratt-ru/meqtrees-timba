//  DataArray.cc: DMI Array class (using AIPS++ Arrays)
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
#include "DMI/DataArray.h"

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

#undef OneLine  

//##ModelId=3DB949AE039F
DataArray::DataArray (int flags)
: NestableContainer(flags&DMI::WRITE != 0),
  itsArray    (0)
{
  initSubArray();
}

//##ModelId=3DB949AE03A4
DataArray::DataArray (TypeId type, const LoShape & shape,
		      int flags, int ) // shm_flags not yet used
: NestableContainer(flags&DMI::WRITE != 0),
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
  itsElemSize = TypeInfo::find(itsScaType).size;
  init(shape,flags);
}

// instantiate this constructor template for all other types
// #undef __instantiate
// #define __instantiate(T,arg) template DataArray::DataArray (const Array<T>& array,int flags, int shm_flags);
// DoForAllArrayTypes(__instantiate,);
// __instantiate(string,);


//##ModelId=3DB949AE03AF
DataArray::DataArray (const DataArray& other, int flags, int depth)
: NestableContainer(flags&DMI::WRITE != 0),
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
  nc_writelock;
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
  nc_readlock1(other);
  Assert (!valid());
  setWritable ((flags&DMI::WRITE) != 0);
  if (other.itsArray) 
  {
    itsData.copy (other.itsData).privatize(flags|DMI::LOCK);
    itsDataOffset = other.itsDataOffset;
    itsShape      = other.itsShape;
    makeArray();
  }
}

void DataArray::makeArray ()
{
  itsArray = allocateArrayWithData(itsScaType,itsArrayData,itsShape);
}

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
  itsShape = shape;
  int sz = sizeof(int) * (3 + shape.size());
  // Align data on 8 bytes.
  itsDataOffset = (sz+7) / 8 * 8;
  sz = itsDataOffset + shape.product() * itsElemSize;
  // Allocate enough space in the SmartBlock.
  /// Circumvent temporary SmartBlock problem
  ///  itsData.attach (new SmartBlock (sz, flags, shm_flags),
  itsData.attach (new SmartBlock(sz,flags),
		  DMI::WRITE|DMI::ANON|DMI::LOCK);
  setHeaderType(itsType);
  setHeaderSize(shape.product());
  void* dataPtr = itsData.dewr().data();
  Assert(dataPtr);
  int* hdrPtr = static_cast<int*>(dataPtr);
  hdrPtr[2] = shape.size();
  for (uInt i=0; i<shape.size(); i++) {
    hdrPtr[i+3] = shape[i];
  }
  // take pointer to data
  itsArrayData = static_cast<char*>(dataPtr) + itsDataOffset;
  // allocate the array object
  makeArray();
}



//##ModelId=3DB949AF0029
void DataArray::reinit()
{
  const void* dataPtr = itsData->data();
  Assert (dataPtr);
  const int* hdrPtr = static_cast<const int*>(dataPtr);
  int nrel = hdrPtr[2];
  itsShape.resize(nrel);
  for (int i=0; i<nrel; i++) 
    itsShape[i] = hdrPtr[i+3];
  int sz = sizeof(int) * (3+nrel);
  // Data is aligned on 8 bytes.
  itsDataOffset = (sz+7) / 8 * 8;
  itsArrayData = const_cast<char *>(static_cast<const char*>(dataPtr) + itsDataOffset);
  // allocate the array object
  makeArray();
}

//##ModelId=3DB949AF002C
void DataArray::clear()
{
  nc_writelock;
  if( itsArray ) 
    destroyArray(elementType(),rank(),itsArray);
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
    itsSubArrayPtr = 0;
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
    return headerSize();
  // else return 1 for full array type
  if( tid == itsType )
    return 1;
  // <0 for type mismatch
  return -1;
}

//##ModelId=3DB949AE03C0
int DataArray::fromBlock (BlockSet& set)
{
  nc_writelock;
  dprintf1(2)("%s: fromBlock\n",debug());
  clear();
  // Get data block and privatize.
  set.pop (itsData);  
  int npopped = 1;
  size_t hsize = itsData->size();
  AssertStr (hsize >= 3*sizeof(int), "malformed header block");
  itsData.privatize ((isWritable() ? DMI::WRITE : 0) | DMI::LOCK);
  // Create the Array object.
  reinit();
  return npopped;
}

//##ModelId=3DB949AE03C5
int DataArray::toBlock (BlockSet& set) const
{
  nc_readlock;
  if (!valid()) {
    dprintf1(2)("%s: toBlock=0 (field empty)\n",debug());
    return 0;
  }
  dprintf1(2)("%s: toBlock\n",debug());
  set.push (itsData.copy(DMI::READONLY));
  int npushed = 1;
  return npushed;
}

//##ModelId=3DB949AE03CB
CountedRefTarget* DataArray::clone (int flags, int depth) const
{
  return new DataArray (*this, flags, depth);
}

//##ModelId=3DB949AE03D2
void DataArray::privatize (int flags, int)
{
  nc_writelock;
  setWritable((flags&DMI::WRITE) != 0);
  if( !valid() ) 
    return;
  // Privatize the data.
  itsData.privatize(flags|DMI::LOCK);
}

// full HIID -> type can be Tpfloat
// no HIID   -> type can be TpArray_float (or Tpfloat if array has 1 element)
// partial HIID -> type must be TpArray_float and create such array on heap
//                 which gets deleted by clear()
//##ModelId=3DB949AE03DA
const void* DataArray::get (const HIID& id, ContentInfo &info,
			    TypeId check_tid, int flags) const
{
  nc_lock(flags&DMI::WRITE);
  info.writable = isWritable();
  info.tid = itsType;
  info.size = 1;
  FailWhen( flags&DMI::WRITE && !info.writable, "write access violation" ); 
  int nid = id.length();
  int ndim = itsShape.size();
  // If a full HIID is given, we might need to return a single element
  // which is a scalar.
  if( nid == ndim )     // full HIID?
  {
    bool single = true;
    LoShape which(itsShape.nelements());
    for (int i=0; i<nid; i++) 
    {
      which[i] = id[i];
      if( which[i] < 0 ) // all elements for this axis?
      {
	      single = false;
	      break;
      }
    }
    if( single ) 
    {
      info.tid = itsScaType;
      FailWhen(check_tid && check_tid != itsScaType &&
		    (check_tid != TpNumeric || !TypeInfo::isNumeric(itsScaType)),
		    "type mismatch: expecting "+check_tid.toString() + ", got " +
		    itsScaType.toString());
      for (int i=0; i<nid; i++) 
      {
        FailWhen(which[i] >= itsShape[i],"array position out of range");
      }
      // Return a single element in the array.
      info.size = 1;
      // compute the element offset
      int offset = 0, stride = 1;
      LoShape::const_iterator iwhich = which.begin(), 
                              ishape = itsShape.begin();
      for( ; iwhich != which.end(); iwhich++,ishape++ )
      {
        offset += *iwhich;
        stride *= *ishape;
      }
      return itsArrayData + itsElemSize*offset;
    }
  } 
  else if( nid == 0 )  // else not full HIID; null HIID?
  {
    // Scalar pointer requested? Return full array data
    if( check_tid == itsScaType ) 
    {
      info.tid = itsScaType;
      FailWhen(!(flags&DMI::NC_POINTER),
		      "array cannot be accessed as non-pointer scalar");
      info.size = itsShape.product();
      return itsArrayData;
    }
    else
    {
      FailWhen( check_tid && check_tid != info.tid, "array type mismatch (" +
	                check_tid.toString() + "/" +
	                info.tid.toString() +")"  );
      return itsArray;
    }
  }
  // Else not a full HIID: return a subset of the array as an array.
  LoPos st,end,incr;
  vector<bool> keepAxes;
  // naxes is the number of axes in the subarray.
  // axes in the source array with keepAxes = false are removed (sliced out).
  int naxes = parseHIID(id,st,end,incr,keepAxes);
  // now check the type
  info.tid = TpArray(itsScaType,naxes);
  FailWhen( check_tid && check_tid != info.tid, "array type mismatch (" +
	            check_tid.toString() + "/" +
	            info.tid.toString() +")"  );
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
  
  return makeSubArray(itsArrayData + itsElemSize*offset,subshape,substride);
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
  bool hadRange = true;
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
void* DataArray::insert (const HIID&, TypeId, TypeId&)
{
  Throw("insert() not supported for DataArray");
}

