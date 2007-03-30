//# Result.cc: A set of Result results
//#
//# Copyright (C) 2002
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//# This program is free software; you can redistribute it and/or modify
//# it under the terms of the GNU General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or
//# (at your option) any later version.
//#
//# This program is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License
//# along with this program; if not, write to the Free Software
//# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//# $Id$


#include "Result.h"
#include "Request.h"
#include "Cells.h"
#include "MeqVocabulary.h"
#include <DMI/NumArray.h>

namespace Meq {

static DMI::Container::Register reg(TpMeqResult,true);

//##ModelId=3F86887000CE
Result::Result (int nvellsets,bool integrated)
  : pvellsets_(0),pcells_(0)
{
  setIsIntegrated(integrated);
  if( nvellsets>0 )
    allocateVellSets(nvellsets);
}

Result::Result (const Dims &dims,bool integrated)
  : pvellsets_(0),pcells_(0)
{
  setIsIntegrated(integrated);
  allocateVellSets(dims);
}

//##ModelId=400E53550116
Result::Result (const DMI::Record &other,int flags,int depth)
: Record(),
  pvellsets_(0),pcells_(0)
{
  Record::cloneOther(other,flags,depth,true);
}

//##ModelId=3F86887000D3
Result::~Result()
{
}

bool Result::verifyShape (const LoShape &cellshape) const
{
  bool hasshapes = false;
  for( int i=0; i<numVellSets(); i++ )
  {
    const VellSet &vs = vellSet(i);
    if( vs.hasShape() )
    {
      FailWhen(!Vells::isCompatible(vs.shape(),cellshape),
              "shape of vellset does not conform to cells");
      hasshapes = true;
    }
  }
  return isIntegrated() || hasshapes;
}


void Result::verifyShape (bool reset)
{
  Thread::Mutex::Lock lock(mutex());
  // with cells, verify shapes and remove cells if nothing variable
  if( hasCells() )
  {
    bool hasshape = verifyShape(cells().shape());
    if( reset && !hasshape )
    {
      // remove cells when no variability
      Record::removeField(FCells,true,0);
      pcells_ = 0;
    }
  }
  // w/o cells, verify that vellsets have noshapes
  else
  {
    for( int i=0; i<numVellSets(); i++ )
    {
      FailWhen(vellSet(i).hasShape(),
              "vellset has a shape but result cells are not set");
    }
  }
}

LoShape Result::getVellSetShape () const
{
  LoShape shape;
  for( int i=0; i<numVellSets(); i++ )
    if( !Axis::mergeShape(shape,vellSet(i).shape()) )
      Throw("vellsets in Result contain incompatible shapes");
  return shape;
}

//##ModelId=3F86887000D4
void Result::setCells (const Cells *cells,int flags,bool force)
{
  Thread::Mutex::Lock lock(mutex());
  ObjRef ref(cells,flags);
  // check that shape is correct, and set cells if needed 
  if( verifyShape(cells->shape()) || force )
  {
    Field & field = Record::addField(FCells,ref,DMI::REPLACE|Record::PROTECT);
    pcells_ = &(field.ref().ref_cast<Cells>());
  }
  else
  {
    Record::removeField(FCells,true,0);
    pcells_ = 0;
  }
}

bool Result::needsCells (const Cells &cells) const
{
  return !hasCells() && verifyShape(cells.shape());
}

void Result::clearCells ()
{
  Thread::Mutex::Lock lock(mutex());
  for( int i=0; i<numVellSets(); i++ )
  {
    FailWhen(vellSet(i).hasShape(),
            "vellset has a shape, can't clear result cells");
  }
  Record::removeField(FCells,true,0);
  pcells_ = 0;
}

//##ModelId=400E53550156
void Result::validateContent (bool)
{
  Thread::Mutex::Lock lock(mutex());
  // ensure that our record contains all the right fields, and that they're
  // indeed writable. Setup shortcuts to their contents
  try
  {
    // get integrated flag
// 04/01/2007 phased out  
//    is_integrated_ = (*this)[FIntegrated].as<bool>(false);
    // get vellsets
    Field * fld = Record::findField(FVellSets);
    if( fld )
    {
      fld->protect(true);
      pvellsets_ = &( fld->ref().ref_cast<DMI::Vec>() );
    }
    else
      pvellsets_ = 0;
    // get dimensions
    if( (*this)[FDims].get_vector(dims_) )
    {
      // product of dims must match # of vellsets in tensor
      FailWhen(dims_.product()!=numVellSets(),"dimensions do not match number of vellsets");
    }
    else
    {
      if( numVellSets() > 1 )
      {
        dims_.resize(1);
        dims_[0] = numVellSets();
      }
      else
        dims_.clear();
    }
    // get cells
    fld = Record::findField(FCells);
    if( fld )
    {
      fld->protect(true);
      pcells_ = &( fld->ref().ref_cast<Cells>() );
    }
    else
      pcells_ = 0;
    verifyShape();
  }
  catch( std::exception &err )
  {
    ThrowMore(err,"validate of Result record failed");
  }
  catch( ... )
  {
    Throw("validate of Result record failed with unknown exception");
  }  
}

//##ModelId=400E5355017B
int Result::allocateVellSets (int nvellsets)
{
  Thread::Mutex::Lock lock(mutex());
  FailWhen(numVellSets(),"allocateVellSets() can only be called on an empty result");
  ObjRef ref(new DMI::Vec(TpMeqVellSet,nvellsets));
  Field & field = Record::addField(FVellSets,ref,DMI::REPLACE|Record::PROTECT);
  pvellsets_ = &(field.ref().ref_cast<DMI::Vec>());
  // setup trivial dims
  if( nvellsets>1 )
  {
    dims_.resize(1);
    return dims_[0] = nvellsets;
  }
  return nvellsets;
}

int Result::allocateVellSets (const Dims &dims)
{
  Thread::Mutex::Lock lock(mutex());
  FailWhen(numVellSets(),"allocateVellSets() can only be called on an empty result");
  // compute total number of vellsets based on dims
  int nvs = dims.product();
  ObjRef ref(new DMI::Vec(TpMeqVellSet,nvs));
  Field & field = Record::addField(FVellSets,ref,DMI::REPLACE|Record::PROTECT);
  pvellsets_ = &(field.ref().ref_cast<DMI::Vec>());
  // 1 element? this corresponds to zero dimensions
  if( nvs == 1 )
    dims_.clear();
  else
    dims_ = dims;
  // if dims are non-trivial, store them in record
  if( dims.size() > 1 )
  {
    ref <<= new DMI::Vec(Tpint,dims.size(),&(dims[0]));
    Record::addField(FDims,ref,DMI::REPLACE|Record::PROTECT);
  }
  return nvs;
}

int Result::setDims (const Dims &dims)
{
  Thread::Mutex::Lock lock(mutex());
  if( !numVellSets() )
    return allocateVellSets(dims);
  // else verify that number of vellsets does not change
  int nvs = dims.product();
  FailWhen(nvs!=numVellSets(),"new result dimensions do not match number of vellsets");
  if( nvs>1 )
    dims_ = dims;
  else
    dims_.clear();
  // dimensions only stored in record if non-vector
  if( dims_.size()>1 )
  {
    ObjRef ref(new DMI::Vec(Tpint,dims_.size(),&(dims[0])));
    Record::addField(FDims,ref,DMI::REPLACE|Record::PROTECT);
  }
  else
  {
    Record::removeField(FDims,true,0);
  }
  return nvs;
}

// 04/01/2007 phased out  
// void Result::setIsIntegrated (bool integrated)
// {
//   Thread::Mutex::Lock lock(mutex());
//   is_integrated_ = integrated;
//   if( integrated )
//     (*this)[FIntegrated] = integrated;
//   else
//     Record::removeField(FIntegrated,true);
// }

VellSet & Result::setNewVellSet (int i,int nspids,int npertsets)
{ 
  Thread::Mutex::Lock lock(mutex());
  VellSet & vs = setVellSet(i,new VellSet(nspids,npertsets));
  return vs;
}

//##ModelId=400E535501D1
bool Result::hasFails () const
{
  Thread::Mutex::Lock lock(mutex());
  for( int i=0; i<numVellSets(); i++ )
    if( vellSet(i).isFail() )
      return true;
  return false;
}

//##ModelId=400E535501D4
int Result::numFails () const
{
  Thread::Mutex::Lock lock(mutex());
  int count=0;
  for( int i=0; i<numVellSets(); i++ )
    if( vellSet(i).isFail() )
      count++;
  return count;
}

DMI::ExceptionList & Result::addToExceptionList (DMI::ExceptionList &list) const
{
  for( int i=0; i<numVellSets(); i++ )
    if( vellSet(i).isFail() )
      vellSet(i).addToExceptionList(list);
  return list;
}

// 04/01/2007 phased out  
// void Result::integrate (const Cells *pcells,bool reverse)
// {
//   Thread::Mutex::Lock lock(mutex());
//   if( reverse && isIntegrated() )
//     return;
//   if( !reverse && !isIntegrated() )
//     return;
//   if( !hasCells() )
//   {
//     FailWhen(!pcells,"can't integrate Result without cells");
//   }
//   else
//     pcells = &( cells() );
//   // compute cellsize, as scalar or matrix, depending on properties of cells
//   Vells cellsize;
//   // is the cell size regular?
//   bool is_regular = true;
//   double csz = 1;
//   for( int i=0; i<Axis::MaxAxis; i++ )
//     if( pcells->isDefined(i) )
//     {
//       if( pcells->numSegments(i)>1 )
//       {
//         is_regular = false;
//         break;
//       }
//       else
//         csz *= double(pcells->cellSize(i)(0));
//     }
//   // regular cell sizes -- have been accumulated in csz
//   if( is_regular )
//   {
//     if( reverse )
//       csz = 1/csz;
//     cellsize = Vells(csz);
//   }
//   else // irregular sizes -- compute a Vells of cell sizes
//   {
//     cellsize = Vells(1.);
//     Vells::Shape shape0(pcells->rank());
//     for( int i=0; i<pcells->rank(); i++ )
//       shape0[i] = 1;
//     // multiply repeatedly by each cell size
//     for( int iaxis=0; iaxis<pcells->rank(); iaxis++ )
//       if( pcells->isDefined(iaxis) )
//       {
//         // create Vells variable only along this axis, containing cell sizes
//         Vells::Shape shape(shape0);
//         int nc = pcells->ncells(iaxis);
//         shape[iaxis] = nc;
//         Vells sz(double(0),shape,false);
//         memcpy(sz.realStorage(),pcells->cellSize(iaxis).data(),sizeof(double)*nc);
//         // multiply accumulated size
//         cellsize *= sz;
//       }
//     if( reverse )
//       cellsize = 1/cellsize;
//   }
//   // loop over vellsets, applying cellsize
//   for( int ivs=0; ivs<numVellSets(); ivs++ )
//   {
//     VellSet &vs = vellSetWr(ivs);
//     if( !vs.isFail() )
//     {
//       vs.setValue(vs.getValue()*cellsize);
//       for( int iset=0; iset<vs.numPertSets(); iset++ )
//         for( int i=0; i<vs.numSpids(); i++ )
//         {
//           Vells::Ref res(new Vells(vs.getPerturbedValue(i,iset)*cellsize));
//           vs.setPerturbedValue(i,res,iset);
//         }
//     }
//   }
//   // if all succeeds, set flag
//   setIsIntegrated(!reverse);
//   // attach cells as needed
//   if( !hasCells() && !reverse )
//     setCells(pcells);
// }

//##ModelId=3F868870014C
void Result::show (std::ostream& os) const
{
  Thread::Mutex::Lock lock(mutex());
  for( int i=0; i<numVellSets(); i++ )
  {
    const VellSet &vs = vellSet(i);
    os << "VellSet "<<i<<": "<<&vs<<endl;
    vs.show(os);
  }
}

} // namespace Meq
