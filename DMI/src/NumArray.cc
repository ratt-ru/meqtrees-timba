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


#include "DataArray.h"

static NestableContainer::Register reg(TpDataArray,True);


DataArray::DataArray (int flags)
: NestableContainer(flags&DMI::WRITE != 0),
  itsArray (0)
{}

DataArray::DataArray (TypeId type, const IPosition& shape,
		      int flags, int shm_flags)
: NestableContainer(flags&DMI::WRITE != 0),
  itsArray (0)
{
  int tsz;
  if (type == TpArray_float) {
    tsz = sizeof(float);
  } else if (type == TpArray_double) {
    tsz = sizeof(double);
  } else {
//    AssertMsg (0, "Typeid " << type << " is not a valid DataArray type");
  }
  // Size of type + size + shape.
  int sz = sizeof(int) * (3+shape.nelements());
  // Align data on 8 bytes.
  itsDataOffset = (sz+7) / 8 * 8;
  sz = itsDataOffset + shape.product() * tsz;
  // Allocate enough space in the SmartBlock.
  /// Circumvent temporary SmartBlock problem
  ///  itsData.attach (new SmartBlock (sz, flags, shm_flags),
  itsData.attach (new SmartBlock (sz, flags),
		  DMI::WRITE|DMI::ANON|DMI::LOCK);
  setHeaderType (type);
  setHeaderSize (shape.product());
  attach (shape);
}

DataArray::DataArray (const DataArray& other, int flags, int depth)
: NestableContainer(flags&DMI::WRITE != 0),
  itsArray (0)
{
  cloneOther (other, flags, depth);
}

DataArray::~DataArray()
{
  clear();
}

DataArray& DataArray::operator= (const DataArray& other)
{
  if (this != &other) {
    clear();
    cloneOther (other);
  }
  return *this;
}

void DataArray::cloneOther (const DataArray& other, int flags, int)
{
  Assert (!valid());
  setWritable ((flags&DMI::WRITE) != 0);
  if (other.itsArray) {
    itsData.copy (other.itsData).privatize (flags|DMI::LOCK);
    itsData = other.itsData;
    itsDataOffset = other.itsDataOffset;
    attach (other.itsShape);
  }
}

void DataArray::attach (const IPosition& shape)
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

void DataArray::attach()
{
  const void* dataPtr = itsData->data();
  Assert (dataPtr);
  const int* hdrPtr = static_cast<const int*>(dataPtr);
  int nrel = hdrPtr[2];
  itsShape.resize (nrel);
  for (int i=0; i<nrel; i++) {
    itsShape(i) = hdrPtr[i+3];
  }
  makeArray();
}

void DataArray::makeArray()
{
  char* ptr = static_cast<char*>(itsData.dewr().data());
  Assert (ptr);
  itsArrayData = ptr + itsDataOffset;
  void* dataPtr = itsArrayData;
  int type = headerType();
  if (type == TpArray_float) {
    itsScaType = Tpfloat;
    itsElemSize = sizeof(float);
    itsArray = new Array_float (itsShape,
			       static_cast<float*>(dataPtr), SHARE);
  } else if (type == TpArray_double) {
    itsScaType = Tpdouble;
    itsElemSize = sizeof(double);
    itsArray = new Array_double (itsShape,
				static_cast<double*>(dataPtr), SHARE);
  } else {
//    AssertMsg (0, "Typeid " << type << " is not a valid DataArray type");
  }
}

void DataArray::clear()
{
  if (itsArray) {
    int type = headerType();
    if (type == TpArray_float) {
      delete static_cast<Array_float*>(itsArray);
    } else if (type == TpArray_double) {
      delete static_cast<Array_double*>(itsArray);
    } else {
//      AssertMsg (0, "Typeid " << type << " is not a valid DataArray type");
    }
  }
  itsArray = 0;
  itsData.unlock().detach();
}

TypeId DataArray::objectType() const
{
  return TpDataArray;
}

TypeId DataArray::type () const
{
  return headerType();
}

int DataArray::size () const
{
  return headerSize();
}

bool DataArray::isContiguous() const
{
  return true;
}

bool DataArray::isScalar (TypeId tid) const
{
  // for a single numeric type, scalar when size == 1
  if( TypeInfo::isNumeric(tid) )
    return itsShape.nelements() == 1 && itsShape(0) == 1;
  // for Array_type, always scalar
  // (should really check that tid == TpArray_<type>, but this is OK for now
  // since get() will throw an exception anyway)
  return True;
}

int DataArray::fromBlock (BlockSet& set)
{
  dprintf1(2)("%s: fromBlock\n",debug());
  clear();
  // Get data block and privatize.
  set.pop (itsData);  
  int npopped = 1;
  size_t hsize = itsData->size();
//  AssertStr (hsize >= 3*sizeof(int), "malformed header block");
  itsData.privatize ((isWritable() ? DMI::WRITE : 0) | DMI::LOCK);
  // Create the Array object.
  attach();
  return npopped;
}

int DataArray::toBlock (BlockSet& set) const
{
  if (!valid()) {
    dprintf1(2)("%s: toBlock=0 (field empty)\n",debug());
    return 0;
  }
  dprintf1(2)("%s: toBlock\n",debug());
  set.push (itsData.copy(DMI::READONLY));
  int npushed = 1;
  return npushed;
}

CountedRefTarget* DataArray::clone (int flags, int depth) const
{
  return new DataArray (*this, flags, depth);
}

void DataArray::privatize (int flags, int)
{
  setWritable ((flags&DMI::WRITE) != 0);
  if (!valid()) {
    return;
  }
  // Privatize the data.
  itsData.privatize (DMI::WRITE|DMI::LOCK);
}

// full HIID -> type can be Tpfloat
// no HIID   -> type can be TpArray_float (or Tpfloat if array has 1 element)
// partial HIID -> type must be TpArray_float and create such array on heap
//                 which gets deleted by clear()
const void* DataArray::get (const HIID& id, TypeId& tid, bool& can_write,
			    TypeId check_tid,
			    bool must_write, int) const
{
  can_write = isWritable();
  tid = check_tid;
  FailWhen(must_write && !can_write,"write access violation"); 
  int nid = id.length();
  if (nid == int(itsShape.nelements())) {
    FailWhen( check_tid && check_tid != itsScaType &&
              (check_tid != TpNumeric || !TypeInfo::isNumeric(itsScaType)),
	      "type mismatch: expecting "+check_tid.toString() + ", got " +
	      itsScaType.toString());
    tid = itsScaType;
    IPosition which(itsShape.nelements());
    for (int i=0; i<nid; i++) {
      which(i) = id[i];
    }
    // Use a global function in IPosition.h to get the element offset.
    uInt offs = toOffsetInArray (which, itsShape);
    return itsArrayData + itsElemSize*offs;
  } else if (nid == 0) {
    if (check_tid == itsScaType) {
      return itsArrayData;
    }
//    AssertStr (check_tid == headerType(), "array type mismatch");
    return itsArray;
  }
//  AssertMsg (0, "Partial DataArray's not supported yet");
}

void* DataArray::insert (const HIID&, TypeId, TypeId&)
{
//  AssertMsg (0, "DataArray::insert is not possible");
}


string DataArray::sdebug (int detail, const string& prefix,
			  const char* name) const
{
  return "";
}
