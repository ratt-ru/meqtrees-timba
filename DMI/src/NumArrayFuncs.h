//  NumArrayFuncs.h: defines lookup tables and functions for NumArrays
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
//  Revision 1.3  2006/06/03 11:25:34  smirnov
//  Added NumArray methods to make an array that is a reference to a slice through
//  another array.
//  Revised VellsSlicer so that it can represent the slice as a Vells.
//
//  Revision 1.2  2006/01/31 12:23:09  smirnov
//  Common renamed to TimBase
//
//  Revision 1.1  2005/08/15 12:41:58  smirnov
//  Upped the max array rank to 16.
//  Split up NumArray LUT-functions into 8 separate .cc files to speed up
//  compilation, with the rank up to 16 all those methods really took ages
//  to compile.
//
//
#ifndef DMI_NUMARRAYFUNCS_H
#define DMI_NUMARRAYFUNCS_H

#include <TimBase/Lorrays.h>
#include <DMI/TID-DMI.h>

#ifndef LORRAYS_USE_BLITZ
  #error This version of NumArray requires Blitz Lorrays
#endif

namespace DMI
{

//##ModelId=3DB949AE00C5
namespace NumArrayFuncs
{
  // converts a type id into a numeric offset into the table above
  const int NumTypes = 17;  // CHANGE THIS IF NEW TYPES ARE ADDED!!!
  extern int typeIndices[NumTypes];
  
  using Debug::getDebugContext;
  
  // converts a type id into a numeric offset into the table above
  inline int typeIndex (int tid)  // CHANGE THIS IF Tpbool CHANGES!!!
  { 
    int index = -(tid-Tpbool_int); 
    FailWhen1(index < 0 || index >= NumTypes,Debug::ssprintf("illegal array type %d",tid));
    index = typeIndices[index];
    FailWhen1(index < 0,Debug::ssprintf("illegal array type %d",tid));
    return index;
  }
  

  // OK, setup some circus hoops. Rank & type of NumArray is set at runtime,
  // while for blitz arrays it's compile-time. So, for every blitz operation
  // required in NumArray, we'll setup an N(ranks) x N(types) matrix of 
  // function pointers, then use rank & type to call the appropriate function.
  // This matrix is called the "method table".
  
  // Methods for the method table are naturally implemented via
  // templates. Refer to NumArray.cc.
  
  // These are the actual method tables
    //##ModelId=3E9BD9140364
  typedef void * (*AllocatorWithData)(void*,void*,const LoShape &);
    //##ModelId=3E9BD9140377
  typedef void * (*AllocatorDefault)();
  typedef void (*AllocatorPlacement)(void*);
    //##ModelId=3E9BD914038B
  typedef void (*AssignWithStride)(void*,void *,const LoShape &,const LoShape &);
  typedef void (*AssignDataReference)(void*,void *,const LoShape &);
    //##ModelId=3E9BD91403A0
  typedef void (*Destructor)(void*);
  
    //##ModelId=3F5487DA00A7
  typedef void (*ArrayCopier)(void*,const void*);
  
    //##ModelId=3F5487DA015B
  typedef void (*ShapeOfArray)(LoShape &,const void*);
  
  extern AllocatorWithData    allocatorWithData     [NumArrayTypes][MaxLorrayRank];
  extern AllocatorDefault     allocatorDefault      [NumArrayTypes][MaxLorrayRank];
  extern AllocatorPlacement   allocatorPlacement    [NumArrayTypes][MaxLorrayRank];
  extern AssignWithStride     assignerWithStride    [NumArrayTypes][MaxLorrayRank];
  extern AssignDataReference  assignerDataReference [NumArrayTypes][MaxLorrayRank];
  extern Destructor           destructor            [NumArrayTypes][MaxLorrayRank];
  extern Destructor           destructor_inplace    [NumArrayTypes][MaxLorrayRank];
    //##ModelId=3F5487DA023F
  extern ArrayCopier          copier                [NumArrayTypes][MaxLorrayRank];
    //##ModelId=3F5487DA0273
  extern ShapeOfArray         shapeOfArray          [NumArrayTypes][MaxLorrayRank];
  
  // These methods do a lookup & call into each method table
    //##ModelId=3E9BD918015A
  inline void * allocateArrayWithData (int tid,void *where,void *data,const LoShape &shape )
  {
    return (*allocatorWithData[typeIndex(tid)][shape.size()-1])(where,data,shape);
  }
    //##ModelId=3E9BD91801EA
  inline void assignWithStride (int tid,void *ptr,void *data,const LoShape &shape,const LoShape &stride )
  {
    (*assignerWithStride[typeIndex(tid)][shape.size()-1])(ptr,data,shape,stride);
  }
  
  inline void assignDataReference (int tid,void *ptr,void *data,const LoShape &shape)
  {
    (*assignerDataReference[typeIndex(tid)][shape.size()-1])(ptr,data,shape);
  }
    //##ModelId=3E9BD91802D8
  inline void * allocateArrayDefault (int tid,int rank)
  {
    return (*allocatorDefault[typeIndex(tid)][rank-1])();
  }
    //##ModelId=3E9BD91802D8
  inline void allocatePlacementArray (int tid,int rank,void *ptr)
  {
    return (*allocatorPlacement[typeIndex(tid)][rank-1])(ptr);
  }
  
    //##ModelId=3E9BD9180339
  inline void destroyArray (int tid,int rank,void *ptr)
  {
    (*destructor[typeIndex(tid)][rank-1])(ptr);
  }
  
  inline void destroyPlacementArray (int tid,int rank,void *ptr)
  {
    (*destructor_inplace[typeIndex(tid)][rank-1])(ptr);
  }
  
    //##ModelId=3F5487DB02E7
  inline void copyArray (int tid,int rank,void *target,const void *source)
  {
    (*copier[typeIndex(tid)][rank-1])(target,source);
  }
  
    //##ModelId=3F5487DC0121
  inline void getShapeOfArray (int tid,int rank,LoShape &shape,const void *ptr)
  {
    (*shapeOfArray[typeIndex(tid)][rank-1])(shape,ptr);
  }

};

};
#endif
