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

#include "Common.h"
#include "DMI.h"

#pragma types #DataArray
#pragma types -Array_bool -Array_int -Array_float -Array_double
#pragma types -Array_fcomplex -Array_dcomplex

#include "NestableContainer.h"
#include "HIID.h"
#include "SmartBlock.h"

#include <aips/Arrays/Array.h>


class DataArray : public NestableContainer
{
public:
  explicit DataArray (int flags = DMI::WRITE);

  DataArray (TypeId type, const IPosition& shape, int flags = DMI::WRITE,
	     int shm_flags = 0);

  DataArray (const DataArray& other, int flags = 0, int depth = 0);

  ~DataArray();

  DataArray& operator= (const DataArray& other);


  virtual TypeId objectType() const;

  virtual int fromBlock (BlockSet& set);

  virtual int toBlock (BlockSet& set) const;

  virtual CountedRefTarget* clone (int flags = 0, int depth = 0) const;

  virtual void privatize (int flags = 0, int depth = 0);

  virtual const void* get (const HIID& id, TypeId& tid, bool& can_write,
			   TypeId check_tid = 0,int flags=0) const;

  virtual void* insert (const HIID& id, TypeId tid, TypeId& real_tid);

  virtual int size() const;

  virtual TypeId type() const;
  
  string sdebug (int detail = 1, const string& prefix = "",
		 const char* name = 0) const;
      
private:
  bool valid() const 
    { return itsArray; }
  void attach (const IPosition& shape);
  void attach();
  void makeArray();
  void clear();
  void cloneOther (const DataArray& other, int flags = 0, int depth = 0);
  int headerType() const
    { return static_cast<const int*>(*itsData.deref())[0]; }
  int headerSize() const
    { return static_cast<const int*>(*itsData.deref())[1]; }
  void setHeaderType (int type)
    { static_cast<int*>(*itsData.dewr())[0] = type; }
  void setHeaderSize (int size)
    { static_cast<int*>(*itsData.dewr())[1] = size; }

  IPosition  itsShape;
  BlockRef   itsData;
  TypeId     itsScaType;
  int        itsElemSize;
  int        itsDataOffset;
  char*      itsArrayData;
  void*      itsArray;
};


#endif
