//  DMI::NumArray.cc: Array container (using Blitz Arrays)
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
//  Revision 1.48  2006/06/14 17:41:49  smirnov
//  Added missing innitialization of "writable_ref" flag
//
//  Revision 1.47  2006/06/03 11:25:34  smirnov
//  Added NumArray methods to make an array that is a reference to a slice through
//  another array.
//  Revised VellsSlicer so that it can represent the slice as a Vells.
//
//  Revision 1.46  2005/11/30 13:44:24  smirnov
//  Fixed bug with treatment of literal HIIDs.
//  Fixes for 64-bit copatibility.
//
//  Revision 1.45  2005/09/15 11:46:44  smirnov
//  Revised error reporting to allow hierarchical exceptions
//
//  Revision 1.44.2.1  2005/09/13 06:34:45  smirnov
//  Revising the Exceptions mechanism to allow hierarchical exceptions to accumulate.
//
//  Revision 1.44  2005/08/15 12:41:58  smirnov
//  Upped the max array rank to 16.
//  Split up NumArray LUT-functions into 8 separate .cc files to speed up
//  compilation, with the rank up to 16 all those methods really took ages
//  to compile.
//
//  Revision 1.43  2005/05/20 13:35:53  smirnov
//  %[ER: ]%
//  Some speedups to HIIDs and Containers, cut down on memory allocs/reallocs
//
//  Revision 1.42  2005/05/17 21:15:07  smirnov
//  %[ER: ]%
//  Fixed memory leak in NumArray.
//  Misc cleanups to nodes to make memory leaks easier to find.
//
//  Revision 1.41  2005/03/26 13:43:57  smirnov
//  %[ER: ]%
//  Fixing conversion of pathological data structures to/from Glish and Python
//
//  Revision 1.40  2005/02/03 12:54:53  smirnov
//  %[ER: 16]%
//  1. Added support for flag Vells and flagging. Not yet fully tested,
//  but works with existsing test scripts.
//  2. Fixed major bug in toBlock()ing of Vells (block had the wrong objectId in it)
//  3. Revised GaussNoise and added support for blitz++ random generators
//
//  Revision 1.39  2005/01/24 14:47:43  smirnov
//  %[ER: ]%
//  Changed all BObj derivatives to have a standard BObj::Header at the start
//  of the first block in their toBlock representation. This gives the object
//  type and total block count, and thus makes blocksets completely self-contained.
//
//  Revision 1.38  2005/01/21 15:54:38  smirnov
//  %[ER: ]%
//  Made the changeover to C-storage Lorrays (i.e., use default
//  blitz storage -- row-major -- and convert to aips++ arrays on the fly)
//
//  Revision 1.37  2005/01/17 13:53:04  smirnov
//  %[ER: 16]%
//  DMI completely revised to DMI2
//
//  Revision 1.33  2004/10/03 20:59:26  smirnov
//  %[ER: 16]%
//  Fixed error in DMI::NumArray::privatize
//
//  Revision 1.32  2004/03/17 07:51:20  smirnov
//  %[ER: 16]%
//  Extended access by pointer in DMI::NumArray
//
//  Revision 1.31  2004/01/28 16:23:34  smirnov
//  %[ER: 16]%
//  Revised the hook infrastructure, got rid of NC::writable flag.
//  Simplified CountedRefs
//

#define NC_SKIP_HOOKS 1
#include "NumArray.h"
#include "NumArrayFuncs.h"

static DMI::Container::Register reg(TpDMINumArray,true);

using namespace DMI::NumArrayFuncs;


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
DMI::NumArray::NumArray ()
: Container (),
  itsArrayValid(false),
  itsWritableRef(false)    
{
  initSubArray();
}

//##ModelId=3DB949AE03A4
DMI::NumArray::NumArray (TypeId type, const LoShape & shape,int flags,TypeId realtype) 
: Container (),
  itsArrayValid(false),
  itsWritableRef(false)    
{
  initSubArray();
  init(type,shape,flags,realtype);
}

void DMI::NumArray::init (TypeId type, const LoShape & shape,int flags,TypeId realtype) 
{
  clear();
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
  init(shape,flags,realtype);
}

//##ModelId=3DB949AE03AF
DMI::NumArray::NumArray (TypeId tid,const void *other,TypeId realtype) 
: Container (),
  itsArrayValid(false),
  itsWritableRef(false)    
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
  init(shape,0,realtype);
  // copy data
  copyArray(itsScaType,rank,itsArray,other);
}

//##ModelId=3F5487DA034E
DMI::NumArray::NumArray (const NumArray& other, int flags,int depth,TypeId realtype)
: Container (),
  itsArrayValid(false),
  itsWritableRef(false)    
{
  initSubArray();
  cloneOther(other,flags,depth,true,realtype);
}

//##ModelId=3DB949AE03B8
DMI::NumArray::~NumArray()
{
  clear();
}

//##ModelId=3DB949AE03B9
DMI::NumArray& DMI::NumArray::operator = (const NumArray& other)
{
  Thread::Mutex::Lock _nclock(mutex());
  if( this != &other ) 
  {
    clear();
    cloneOther(other,0,0,false,objectType());
  }
  return *this;
}

//##ModelId=3DB949AF002E
void DMI::NumArray::cloneOther (const NumArray& other,int flags,int depth,bool constructing,TypeId realtype)
{
  Thread::Mutex::Lock _nclock(mutex());
  Thread::Mutex::Lock _nclock1(other.mutex());
  Assert (!valid());
  itsWritableRef = false;
  if( other.itsArrayValid ) 
  {
    itsScaType  = other.itsScaType;
    itsType     = other.itsType;
    itsShape    = other.itsShape;
    itsSize     = other.itsSize;
    itsElemSize = other.itsElemSize;
    itsDataOffset = other.itsDataOffset;
    itsData.unlock().copy(other.itsData,flags,depth).lock();
    if( !realtype )
      realtype = objectType();
    if( realtype != other.objectType() )
    {
      Header *hdr = itsData().pdata<Header>();
      BObj::fillHeader(hdr,1,realtype);
    }
    else
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
  validateContent(!constructing);
}

void DMI::NumArray::makeArray ()
{
  allocateArrayWithData(itsScaType,itsArray,itsArrayData,itsShape);
  itsArrayValid = true;
}

//##ModelId=3E9BD91803CC
void * DMI::NumArray::makeSubArray (void *data,const LoShape & shape,const LoShape &stride) const
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
void DMI::NumArray::init (const LoShape & shape,int flags,TypeId realtype)
{
#ifdef HAVE_AIPSPP
  // sanity check -- can we treat string as an AIPS++ String?
  FailWhen( sizeof(string) != sizeof(casa::String),"AIPS++ String is not equivalent to std::string" );
#endif
  itsWritableRef = false;    
  itsShape = shape;
  itsSize  = shape.product();
  int sz = sizeof(NumArray::Header) + sizeof(uint)*shape.size();
  // Align data on 8 bytes.
  itsDataOffset = (sz+7) / 8 * 8;
  sz = itsDataOffset + itsSize*itsElemSize;
  // Allocate one SmartBlock for everything
  itsData.unlock().attach(new SmartBlock(sz,flags&DMI::NOZERO ? 0 : DMI::ZERO)).lock();
  void *dataptr = itsData().data();
  // fill block header
  if( !realtype )
    realtype = objectType();
  Header *phead = static_cast<Header*>(dataptr);
  BObj::fillHeader(phead,1,realtype);
  phead->sca_tid = itsScaType;
  phead->rank    = shape.size();
  for( uint i=0; i<shape.size(); i++ )
    phead->shape[i] = shape[i];
  // pointer to start of array data
  itsArrayData = static_cast<char*>(dataptr) + itsDataOffset;
  // init string objects, if needed
  if( itsScaType == Tpstring )
    initStringArray(itsArrayData,itsSize);
  
  // allocate the array object
  makeArray();
}

// method to make this array a reference to a slice through another NumArray
// if writable=true, 
void DMI::NumArray::make_reference (void * pdata,bool writable,
          const LoShape &shape,const LoShape &strides,const NumArray &other)
{
#ifdef HAVE_AIPSPP
  // sanity check -- can we treat string as an AIPS++ String?
  FailWhen( sizeof(string) != sizeof(casa::String),"AIPS++ String is not equivalent to std::string" );
#endif
  FailWhen(&other == this,"cannot make NumArray a reference to self");
  FailWhen(!other.itsArrayValid,"cannot make reference to an empty NumArray");
  clear();
  itsWritableRef = writable;    
  itsScaType  = other.itsScaType;
  itsType     = TpArray(itsScaType,shape.size());;
  itsShape    = shape;
  itsSize     = shape.product();
  itsElemSize = other.itsElemSize;
  itsDataOffset = other.itsDataOffset;
  itsArrayData = static_cast<char*>(pdata);
  itsData.unlock().copy(other.itsData).lock();
  // make array as a subarray
  allocatePlacementArray(itsScaType,shape.size(),itsArray);
  assignWithStride (itsScaType,itsArray,pdata,shape,strides);
  itsArrayValid = true;
}

//##ModelId=3DB949AF002C
void DMI::NumArray::clear()
{
  Thread::Mutex::Lock _nclock(mutex());
  if( itsArrayValid )
  {
    // NB:**********************************************************************************
    // since itsArray is allocated with placement-new, we don't bother deleting it
    // (mostly because explicit call of a templated destructor is not quite supported)
    // This is ok with blitz (as of 0.8) since Array doesn't even have a destructor
    destroyPlacementArray(elementType(),rank(),itsArray);
    itsArrayValid = false;
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
  itsShape.resize (0);
  
  itsData.unlock().detach();
}

//##ModelId=3DB949AE03BE
DMI::TypeId DMI::NumArray::objectType() const
{
  return TpDMINumArray;
}

//##ModelId=3DB949AF000C
DMI::TypeId DMI::NumArray::type () const
{
  return itsType;
}

//##ModelId=3DB949AF0007
int DMI::NumArray::size (TypeId tid) const
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
int DMI::NumArray::fromBlock (BlockSet& set)
{
  Thread::Mutex::Lock _nclock(mutex());
  dprintf1(2)("%s: fromBlock\n",debug());
  clear();
  // Get data block.
  BlockRef href;
  set.pop(href);  
  size_t hsize = href->size();
  FailWhen(hsize < sizeof(Header),"malformed data block");
  const char *dataptr = static_cast<const char*>(href->data());
  const Header *hdr = static_cast<const Header*>(href->data());
  FailWhen(BObj::checkHeader(hdr)!=1,"invalid block count in block header");
  // get element type and rank from header
  itsScaType = hdr->sca_tid;
  if( itsScaType == 0 ) // empty array
  {
    FailWhen(hdr->rank != 0 || hsize != sizeof(Header),"malformed data block");
  }
  else // proper array, get data out
  {
    TypeInfo typeinfo = TypeInfo::find(itsScaType);
    FailWhen( typeinfo.category != TypeInfo::NUMERIC && itsScaType != Tpstring,
              "invalid array element type" + itsScaType.toString() ); 
    uint rank = hdr->rank;
    FailWhen( rank < 1 || rank > MaxLorrayRank,"invalid array rank" );
    FailWhen( hsize < (2+rank)*sizeof(int), "malformed data block" );
    // derive array type & element size
    itsType = TpArray(itsScaType,rank);
    itsElemSize = itsScaType == Tpstring ? sizeof(string) : typeinfo.size;

    // get shape from header & compute total size
    itsShape.resize(rank);
    itsSize = 1;
    for( uint i=0; i<rank; i++ )
      itsSize *= itsShape[i] = hdr->shape[i];

    // compute size of data block & offset into it
    size_t blocksize = sizeof(Header) + sizeof(uint)*rank;
    // Align data on 8 bytes.
    itsDataOffset = (blocksize + 7) / 8 * 8;
    blocksize = itsDataOffset + itsSize*itsElemSize;

    // strings are a special case since they need to be copied from the block
    if( itsScaType == Tpstring )
    {
      // string block expected to contain string lengths too
      size_t expected_size = sizeof(Header)+sizeof(uint)*rank+itsSize*sizeof(int);
      FailWhen( hsize < expected_size,"malformed data block" );
      // actual array to be stored here
      BlockRef newdata(new SmartBlock(blocksize));
      itsArrayData = newdata().cdata() + itsDataOffset;
      initStringArray(itsArrayData,itsSize);
      // start of string array
      string *pstr = reinterpret_cast<string*>(itsArrayData);
      // get pointer to vector of string lengths
      const uint *lengths = reinterpret_cast<const uint*>(dataptr+sizeof(Header)) + rank;
      // and string data here
      const char *chardata = reinterpret_cast<const char*>(lengths+itsSize);
      // copy strings one by one
      for( int i=0; i<itsSize; i++,pstr++ )
      {
        uint len = *lengths++;       // length from header
        expected_size += len;   // adjust expect size & check for spacd
        FailWhen( hsize < expected_size,"malformed data block" );
        // assign to string
        pstr->assign(chardata,len); 
        chardata += len;
      }
      FailWhen( hsize != expected_size,"malformed data block" );
      // xfer data block
      itsData.unlock().xfer(newdata).lock();
    }
    else // else take the data block
    {
      FailWhen( blocksize != hsize,"malformed data block");
      itsData.unlock().xfer(href).lock();
      itsArrayData = const_cast<char *>(itsData->cdata()) + itsDataOffset;
    }
    // Create the Array object.
    makeArray();
  }
  validateContent(true);
  return 1;
}

//##ModelId=3DB949AE03C5
int DMI::NumArray::toBlock (BlockSet& set) const
{
  Thread::Mutex::Lock _nclock(mutex());
  if( !valid() ) 
  {
    dprintf1(2)("%s: toBlock (empty numarray)\n",debug());
    // for empty fields, use null block 
    BlockRef ref(new SmartBlock(sizeof(Header),DMI::ZERO));
    Header * hdr = ref().pdata<Header>();
    BObj::fillHeader(hdr,1);
    hdr->rank = 0;
    hdr->sca_tid = 0;
    set.push(ref);
    return 1;
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
    // allocate block: need to store header, plus string lengths, plus
    // string data
    BlockRef ref(new SmartBlock(
        sizeof(NumArray::Header) +
        (itsShape.size()+itsSize)*sizeof(int) + totlen));
    // fill the block, first the header
    char *dataptr = static_cast<char*>(ref().data());
    Header *phead = static_cast<Header*>(ref().data());
    BObj::fillHeader(phead,1);
    phead->sca_tid = itsScaType;
    phead->rank    = rank();
    for( int i=0; i<rank(); i++ )
      phead->shape[i] = shape()[i];
    // now, string lengths will go here
    uint *lengths = reinterpret_cast<uint*>(dataptr+sizeof(Header)) + rank();
    // and string data here
    char *data = reinterpret_cast<char*>(lengths + itsSize);
    ptr = reinterpret_cast<string*>(itsArrayData);
    for( int i=0; i<itsSize; i++,ptr++ )
    {
      uint len = *lengths++ = ptr->copy(data,string::npos);
      data += len;
    }
    set.push(ref);
  }
  else // else simply push out copy of data block
  {
    set.push(itsData);
  }
  return 1;
}

//##ModelId=3DB949AE03CB
DMI::CountedRefTarget* DMI::NumArray::clone (int flags, int depth) const
{
  return new NumArray (*this, flags, depth);
}

//##ModelId=400E4D68035F
const void * DMI::NumArray::getConstArrayPtr (TypeId element_tid,uint nrank) const
{
  FailWhen( itsScaType!=element_tid || nrank != itsShape.size(),
            "can't access "+itsType.toString()+" as "+
            TpArray(element_tid,nrank).toString() );
  return itsArray;
}

const void * DMI::NumArray::getConstArrayPtr (TypeId array_tid) const
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
int DMI::NumArray::get (const HIID& id, ContentInfo &info,bool nonconst,int flags) const
{
  Thread::Mutex::Lock _nclock(mutex());
  // non-writability directly determined by constness
  if( flags&DMI::WRITE )
  {
    Assert1(nonconst);
    const_cast<NumArray*>(this)->makeWritable();
  }
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
      for( int i = ndim-1; i>=0; i-- )
      {
        offset += which[i]*stride;
        stride *= itsShape[i];
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
  int iax=naxes-1, offset=0, stride=1;
  for( int i=ndim-1; i>=0; i-- )
  {
    // stride is the stride of the current (i'th) axis, in elements
    // Get the starting position within this axis and add it to offset
    offset += st[i]*stride;
    // if keeping the axis, then add it to output shape & stride
    if( keepAxes[i] )
    {
      subshape[iax] = (end[i]-st[i])/incr[i];
      substride[iax] = incr[i]*stride;
      iax--;
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
int DMI::NumArray::parseHIID (const HIID& id, LoPos & st, LoPos & end,LoPos & incr, 
                          vector<bool> & keepAxes) const
{
  int ndim = itsShape.nelements();
  int nid = id.length();
  // An axis can be removed if a single index is given for it.
  keepAxes.resize(ndim);
  keepAxes.assign(ndim,false);
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
      keepAxes[nraxes] = true;
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
        keepAxes[nraxes] = true;
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
          keepAxes[nraxes] = true;
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
int DMI::NumArray::insert (const HIID&,ContentInfo &info)
{
  Throw("insert() not supported for DMI::NumArray");
}

//##ModelId=3F5487DB0110
string DMI::NumArray::sdebug ( int detail,const string &prefix,const char *name ) const
{
  Thread::Mutex::Lock _nclock(mutex());
  string out;
  if( detail>=0 ) // basic detail
  {
    out = name ? string(name) : objectType().toString();
  }
  if( detail >= 1 || detail == -1 )   // normal detail
  {
    out += ssprintf("/%p",(void*)this);
    if( !itsArrayValid )
      Debug::append(out,"empty");
    else
    {
      Debug::append(out,itsType.toString() + " ");
      for( uint i=0; i<itsShape.size(); i++ )
        out += Debug::ssprintf("%c%d",(i?'x':' '),itsShape[i]);
    }
  }
  if( detail >= 2 || detail <= -2 )   // high detail
  {
    if( itsArrayValid )
    {
      // append debug info from block
      string str = itsData.sdebug(2,prefix,"data");
    }
  }
  return out;
}

