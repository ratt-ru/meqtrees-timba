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


//##ModelId=3DB949AE039F
DataArray::DataArray (int flags)
: NestableContainer(flags&DMI::WRITE != 0),
  itsArray    (0),
  itsSubArray (0)
{}

//##ModelId=3DB949AE03A4
DataArray::DataArray (TypeId type, const IPosition& shape,
		      int flags, int ) // shm_flags not yet used
: NestableContainer(flags&DMI::WRITE != 0),
  itsArray    (0),
  itsSubArray (0)
{
  if( TypeInfo::isArrayable(type) )
    type = TypeInfo::elemToArr(type);
  else if( !TypeInfo::isArray(type) )
  {
    AssertMsg (0, "Typeid " << type << " is not a valid DataArray type");
  }
  
  itsElemSize = TypeInfo::find( TypeInfo::arrToElem(type) ).size;
  
  // Size of type + size + shape.
  int sz = sizeof(int) * (3+shape.nelements());
  // Align data on 8 bytes.
  itsDataOffset = (sz+7) / 8 * 8;
  sz = itsDataOffset + shape.product() * itsElemSize;
  // Allocate enough space in the SmartBlock.
  /// Circumvent temporary SmartBlock problem
  ///  itsData.attach (new SmartBlock (sz, flags, shm_flags),
  itsData.attach (new SmartBlock (sz, flags),
		  DMI::WRITE|DMI::ANON|DMI::LOCK);
  setHeaderType (type);
  setHeaderSize (shape.product());
  init (shape);
}

// templated constructor from an array
template<class T>
DataArray::DataArray (const Array<T>& array,
		      int flags, int )  // shm_flags not yet used
: NestableContainer(flags&DMI::WRITE != 0),
  itsArray    (0),
  itsSubArray (0)
{
  itsElemSize = sizeof(T);
  TypeId type = typeIdOfArray(T);
  const IPosition& shape = array.shape();
  // Size of type + size + shape.
  int sz = sizeof(int) * (3+shape.nelements());
  // Align data on 8 bytes.
  itsDataOffset = (sz+7) / 8 * 8;
  sz = itsDataOffset + shape.product() * itsElemSize;
  // Allocate enough space in the SmartBlock.
  /// Circumvent temporary SmartBlock problem
  ///  itsData.attach (new SmartBlock (sz, flags, shm_flags),
  itsData.attach (new SmartBlock (sz, flags),
		  DMI::WRITE|DMI::ANON|DMI::LOCK);
  setHeaderType (type);
  setHeaderSize (shape.product());
  init (shape);
  *static_cast<Array<T>*>(itsArray) = array;
}


// instantiate this constructor template for all other types
#undef __instantiate
#define __instantiate(T,arg) template DataArray::DataArray (const Array<T>& array,int flags, int shm_flags);
DoForAllArrayTypes(__instantiate,);
// __instantiate(string,);


//##ModelId=3DB949AE03AF
DataArray::DataArray (const DataArray& other, int flags, int depth)
: NestableContainer(flags&DMI::WRITE != 0),
  itsArray    (0),
  itsSubArray (0)
{
  cloneOther (other, flags, depth);
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
  if (this != &other) {
    clear();
    cloneOther (other);
  }
  return *this;
}

//##ModelId=3DB949AF002E
void DataArray::cloneOther (const DataArray& other, int flags, int)
{
  nc_readlock1(other);
  Assert (!valid());
  setWritable ((flags&DMI::WRITE) != 0);
  if (other.itsArray) {
    itsData.copy (other.itsData).privatize(flags|DMI::LOCK);
    itsDataOffset = other.itsDataOffset;
    itsShape      = other.itsShape;
    makeArray();
  }
}

//##ModelId=3DB949AF0024
void DataArray::init (const IPosition& shape)
{
  itsShape.resize (shape.nelements());
  itsShape = shape;
  void* dataPtr = itsData.dewr().data();
  Assert (dataPtr);
  int* hdrPtr = static_cast<int*>(dataPtr);
  hdrPtr[2] = shape.nelements();
  for (uInt i=0; i<shape.nelements(); i++) {
    hdrPtr[i+3] = shape(i);
  }
  makeArray();
}

//##ModelId=3DB949AF0029
void DataArray::reinit()
{
  const void* dataPtr = itsData->data();
  Assert (dataPtr);
  const int* hdrPtr = static_cast<const int*>(dataPtr);
  int nrel = hdrPtr[2];
  itsShape.resize (nrel);
  for (int i=0; i<nrel; i++) {
    itsShape(i) = hdrPtr[i+3];
  }
  int sz = sizeof(int) * (3+nrel);
  // Data is aligned on 8 bytes.
  itsDataOffset = (sz+7) / 8 * 8;
  makeArray();
}

//##ModelId=3DB949AF002B
void DataArray::makeArray()
{
  char* ptr = const_cast<char*>(static_cast<const char*>(itsData->data()));
  Assert (ptr);
  itsArrayData = ptr + itsDataOffset;
  void* dataPtr = itsArrayData;
  int type = headerType();
  if (type == TpArray_bool) {
    itsScaType  = Tpbool;
    itsElemSize = sizeof(bool);
    itsArray = new Array_bool (itsShape,
			       static_cast<bool*>(dataPtr), SHARE);
    itsSubArray = new Array_bool();
  } else if (type == TpArray_int) {
    itsScaType  = Tpint;
    itsElemSize = sizeof(int);
    itsArray = new Array_int (itsShape,
			      static_cast<int*>(dataPtr), SHARE);
    itsSubArray = new Array_int();
  } else if (type == TpArray_float) {
    itsScaType  = Tpfloat;
    itsElemSize = sizeof(float);
    itsArray = new Array_float (itsShape,
				static_cast<float*>(dataPtr), SHARE);
    itsSubArray = new Array_float();
  } else if (type == TpArray_double) {
    itsScaType  = Tpdouble;
    itsElemSize = sizeof(double);
    itsArray = new Array_double (itsShape,
				 static_cast<double*>(dataPtr), SHARE);
    itsSubArray = new Array_double();
  } else if (type == TpArray_fcomplex) {
    itsScaType  = Tpfcomplex;
    itsElemSize = sizeof(fcomplex);
    itsArray = new Array_fcomplex (itsShape,
				   static_cast<fcomplex*>(dataPtr), SHARE);
    itsSubArray = new Array_fcomplex();
  } else if (type == TpArray_dcomplex) {
    itsScaType  = Tpdcomplex;
    itsElemSize = sizeof(dcomplex);
    itsArray = new Array_dcomplex (itsShape,
				   static_cast<dcomplex*>(dataPtr), SHARE);
    itsSubArray = new Array_dcomplex();
  } else {
    AssertMsg (0, "Typeid " << type << " is not a valid DataArray type");
  }
}

//##ModelId=3DB949AF002C
void DataArray::clear()
{
  nc_writelock;
  if (itsArray) {
    int type = headerType();
    if (type == TpArray_bool) {
      delete static_cast<Array_bool*>(itsSubArray);
      delete static_cast<Array_bool*>(itsArray);
    } else if (type == TpArray_int) {
      delete static_cast<Array_int*>(itsSubArray);
      delete static_cast<Array_int*>(itsArray);
    } else if (type == TpArray_float) {
      delete static_cast<Array_float*>(itsSubArray);
      delete static_cast<Array_float*>(itsArray);
    } else if (type == TpArray_double) {
      delete static_cast<Array_double*>(itsSubArray);
      delete static_cast<Array_double*>(itsArray);
    } else if (type == TpArray_fcomplex) {
      delete static_cast<Array_fcomplex*>(itsSubArray);
      delete static_cast<Array_fcomplex*>(itsArray);
    } else if (type == TpArray_dcomplex) {
      delete static_cast<Array_dcomplex*>(itsSubArray);
      delete static_cast<Array_dcomplex*>(itsArray);
    } else {
      AssertMsg (0, "Typeid " << type << " is not a valid DataArray type");
    }
  }
  itsSubArray = 0;
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
  return headerType();
}

//##ModelId=3DB949AF0007
int DataArray::size (TypeId tid) const
{
  // by default, return size of scalar type
  if( !tid || tid == itsScaType )
    return headerSize();
  // else return 1 for full array type
  if( tid == TypeInfo::elemToArr( itsScaType ) )
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
  setWritable ((flags&DMI::WRITE) != 0);
  if (!valid()) {
    return;
  }
  // Privatize the data.
  itsData.privatize (flags|DMI::LOCK);
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
  info.tid = headerType();
  info.size = 1;
  FailWhen (flags&DMI::WRITE && !info.writable, "write access violation"); 
  int nid = id.length();
  int ndim = itsShape.nelements();
  // If a full HIID is given, we might need to return a single element
  // which is a scalar.
  if (nid == ndim) {
    bool single = true;
    IPosition which(itsShape.nelements());
    for (int i=0; i<nid; i++) {
      which(i) = id[i];
      if (which(i) < 0) {
	single = false;
	break;
      }
    }
    if (single) {
      FailWhen (check_tid && check_tid != itsScaType &&
		(check_tid != TpNumeric || !TypeInfo::isNumeric(itsScaType)),
		"type mismatch: expecting "+check_tid.toString() + ", got " +
		itsScaType.toString());
      for (int i=0; i<nid; i++) {
	AssertStr (which(i) < itsShape(i), "array position " << which
		   << " outside shape " << itsShape);
      }
      // Return a single element in the array.
      info.tid = itsScaType;
      // Use a global function in IPosition.h to get the element offset.
      uInt offs = toOffsetInArray (which, itsShape);
      info.size = 1;
      return itsArrayData + itsElemSize*offs;
    }
  } else if (nid == 0) {
    // Return the full array.
    if (check_tid == itsScaType) {
      AssertStr (flags&DMI::NC_POINTER,
		 "array cannot be accessed as non-pointer scalar");
      info.size = itsShape.product();
      return itsArrayData;
    }
    AssertStr (check_tid == info.tid, "array type mismatch ("
	       << check_tid.toString()
	       << ' ' << info.tid.toString() << ')');
    return itsArray;
  }
  // Return a subset of the array as an array.
  AssertStr (!check_tid  ||  check_tid == info.tid,
	     "array type mismatch (" << check_tid.toString()
	     << ' ' << info.tid.toString() << ')');
  IPosition st, end, incr, keepAxes;
  bool removeAxes = parseHIID (id, st, end, incr, keepAxes);
  int type = headerType();
  if (type == TpArray_bool) {
    Array_bool tmp =
               (*static_cast<Array_bool*>(itsArray))(st, end, incr);
    if (removeAxes) {
      Array_bool tmp2 = tmp.nonDegenerate (keepAxes);
      static_cast<Array_bool*>(itsSubArray)->reference (tmp2);
    } else {
      static_cast<Array_bool*>(itsSubArray)->reference (tmp);
    }
  } else if (type == TpArray_int) {
    Array_int tmp =
               (*static_cast<Array_int*>(itsArray))(st, end, incr);
    if (removeAxes) {
      Array_int tmp2 = tmp.nonDegenerate (keepAxes);
      static_cast<Array_int*>(itsSubArray)->reference (tmp2);
    } else {
      static_cast<Array_int*>(itsSubArray)->reference (tmp);
    }
  } else if (type == TpArray_float) {
    Array_float tmp =
               (*static_cast<Array_float*>(itsArray))(st, end, incr);
    if (removeAxes) {
      Array_float tmp2 = tmp.nonDegenerate (keepAxes);
      static_cast<Array_float*>(itsSubArray)->reference (tmp2);
    } else {
      static_cast<Array_float*>(itsSubArray)->reference (tmp);
    }
  } else if (type == TpArray_double) {
    Array_double tmp =
               (*static_cast<Array_double*>(itsArray))(st, end, incr);
    if (removeAxes) {
      Array_double tmp2 = tmp.nonDegenerate (keepAxes);
      static_cast<Array_double*>(itsSubArray)->reference (tmp2);
    } else {
      static_cast<Array_double*>(itsSubArray)->reference (tmp);
    }
  } else if (type == TpArray_fcomplex) {
    Array_fcomplex tmp =
               (*static_cast<Array_fcomplex*>(itsArray))(st, end, incr);
    if (removeAxes) {
      Array_fcomplex tmp2 = tmp.nonDegenerate (keepAxes);
      static_cast<Array_fcomplex*>(itsSubArray)->reference (tmp2);
    } else {
      static_cast<Array_fcomplex*>(itsSubArray)->reference (tmp);
    }
  } else if (type == TpArray_dcomplex) {
    Array_dcomplex tmp =
               (*static_cast<Array_dcomplex*>(itsArray))(st, end, incr);
    if (removeAxes) {
      Array_dcomplex tmp2 = tmp.nonDegenerate (keepAxes);
      static_cast<Array_dcomplex*>(itsSubArray)->reference (tmp2);
    } else {
      static_cast<Array_dcomplex*>(itsSubArray)->reference (tmp);
    }
  } else {
    AssertMsg (0, "Typeid " << type << " is not a valid DataArray type");
  }
  return itsSubArray;
}

//##ModelId=3DB949AF000E
bool DataArray::parseHIID (const HIID& id, IPosition& st, IPosition& end,
			   IPosition& incr, IPosition& keepAxes) const
{
  int ndim = itsShape.nelements();
  int nid = id.length();
  // An axis can be removed if a single index is given for it.
  IPosition singleAxes(ndim, 0);
  // Initialize start, end, and stride to all elements.
  st.resize(ndim);
  end.resize(ndim);
  incr.resize(ndim);
  st = 0;
  end = itsShape-1;
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
  for (int i=0; i<nid; i++) {
    if (id[i] == AidRange) {
      AssertMsg (!hadRange, "HIID " << id.toString()
		 << " does not have a value before range delimiter");
      // 'Colon' found, thus next value for this axis.
      // More than a single start value is given, thus keep the axis.
      nr++;
      singleAxes(nraxes) = 0;
      hadRange = true;
    } else {
      if (!hadRange) {
	nr = 0;
	nraxes++;
	AssertMsg (nraxes < ndim, "HIID " << id.toString()
		   << " has more axes than the array (" << ndim << ')');
      }
      hadRange = false;
      if (id[i] < 0) {
	// Wildcard (or empty)is allowed.
	AssertMsg (id[i] == AidWildcard  ||  id[i] == AidEmpty,
		   "Invalid id " << id[i].toString()
		   << " in HIID " << id.toString());
	if (nr == 1) {
	  end(nraxes) = itsShape(nraxes) - 1;
	}
      } else {
	if (nr == 0) {
	  st(nraxes) = id[i];
	  end(nraxes) = id[i];
	  singleAxes(nraxes) = 1;
	  AssertMsg (st(nraxes) < itsShape(nraxes), "Start " << st(nraxes)
		     << " should be < axis length " << itsShape(nraxes)
		     << " in HIID " << id.toString());
	} else if (nr == 1) {
	  end(nraxes) = id[i];
	  AssertMsg (end(nraxes) >= st(nraxes), "End " << end(nraxes)
		     << " should be >= start " << st(nraxes)
		     << " in HIID " << id.toString());
	} else if (nr == 2) {
	  incr(nraxes) = id[i];
	  AssertMsg (incr(nraxes) > 0, "Stride " << incr(nraxes)
		     << " should be > 0 in HIID " << id.toString());
	} else {
	  AssertMsg (0, "Only 3 values (start:end:incr) can be given per axis "
		     "in HIID " << id.toString());
	}
      }
    }
  }
  AssertMsg (!hadRange, "HIID " << id.toString()
	     << " does not have a value after range delimiter");
  // If all axes are not single, no axes have to be removed.
  // Fill in the axis number of the ones to be kept.
  bool removeAxes = false;
  keepAxes.resize (ndim);
  int nra = 0;
  for (int i=0; i<ndim; i++) {
    if (singleAxes(i) == 0) {
      keepAxes(nra++) = i;
    } else {
      removeAxes = true;
    }
  }
  keepAxes.resize (nra);
  return removeAxes;
}

//##ModelId=3DB949AE03E5
void* DataArray::insert (const HIID&, TypeId, TypeId&)
{
  AssertMsg (0, "DataArray::insert is not possible");
}

