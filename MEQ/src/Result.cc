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
#include <DMI/DataArray.h>

namespace Meq {

//##ModelId=3F8688700098
int Result::nctor = 0;
//##ModelId=3F868870009A
int Result::ndtor = 0;

static NestableContainer::Register reg(TpMeqResult,True);

//##ModelId=3F86887000CE
Result::Result (int nvellsets,bool integrated)
{
  nctor++;
  setIsIntegrated(integrated);
  if( nvellsets>0 )
    allocateVellSets(nvellsets);
}

//##ModelId=400E535500F5
Result::Result (int nvellsets,const Request &req,bool integrated)
{
  nctor++;
  setIsIntegrated(integrated);
  if( nvellsets>0 )
    allocateVellSets(nvellsets);
  if( req.hasCells() )
    setCells(&req.cells());
}

//##ModelId=400E53550105
Result::Result (const Request &req,int nvellsets,bool integrated)
{
  nctor++;
  setIsIntegrated(integrated);
  if( nvellsets>0 )
    allocateVellSets(nvellsets);
  if( req.hasCells() )
    setCells(&req.cells());
}
  
//##ModelId=3F8688700151
Result::Result (const Request &req,bool integrated)
{
  nctor++;
  setIsIntegrated(integrated);
  if( req.hasCells() )
    setCells(&req.cells());
}

//##ModelId=400E53550116
Result::Result (const DataRecord &other,int flags,int depth)
: DataRecord(other,flags,depth)
{
  nctor++;
  validateContent();
}

//##ModelId=3F86887000D3
Result::~Result()
{
  ndtor--;
}

//##ModelId=400E5355017B
void Result::allocateVellSets (int nvellsets)
{
  Thread::Mutex::Lock lock(mutex());
  vellsets_ <<= new DataField(TpMeqVellSet,nvellsets);
  DataRecord::replace(FVellSets,vellsets_.dewr_p(),DMI::ANONWR);
}

//  implement privatize
//##ModelId=400E53550142
void Result::privatize (int flags, int depth)
{
  // if deep-privatizing, then detach shortcuts -- they will be reattached 
  // by validateContent()
  if( flags&DMI::DEEP || depth>0 )
  {
    Thread::Mutex::Lock lock(mutex());
    vellsets_.detach();
    DataRecord::privatize(flags,depth);
  }
}

void Result::revalidateContent ()
{
  Thread::Mutex::Lock lock(mutex());
  if( DataRecord::hasField(FVellSets) )
    vellsets_ <<= (*this)[FVellSets].ref();
  else
    vellsets_.detach();
  if( DataRecord::hasField(FCells) )
    cells_ <<= (*this)[FCells].ref();
  else
    cells_.detach();
  protectAllFields();
}

//##ModelId=400E53550156
void Result::validateContent ()
{
  Thread::Mutex::Lock lock(mutex());
  // ensure that our record contains all the right fields, and that they're
  // indeed writable. Setup shortcuts to their contents
  try
  {
    is_integrated_ = (*this)[FIntegrated].as<bool>(false);
    revalidateContent();
  }
  catch( std::exception &err )
  {
    Throw(string("validate of Result record failed: ") + err.what());
  }
  catch( ... )
  {
    Throw("validate of Result record failed with unknown exception");
  }  
}

int Result::remove (const HIID &id)
{ 
  if( id == FCells || id == FVellSets )
    Throw("remove(" + id.toString() +" from a Meq::Result not allowed"); 
  return DataRecord::remove(id);
}

//##ModelId=3F86887000D4
void Result::setCells (const Cells *cells,int flags)
{
  Thread::Mutex::Lock lock(mutex());
  // if we have no idea how to attach object, make a copy
  if( !(flags&(DMI::ANON|DMI::EXTERNAL)) && !cells->refCount() )
    cells_ <<= new Cells(*cells);
  else
    cells_ <<= cells;
  DataRecord::replace(FCells,cells_.deref_p(),DMI::READONLY);
}

void Result::setIsIntegrated (bool integrated)
{
  Thread::Mutex::Lock lock(mutex());
  is_integrated_ = integrated;
  DataRecord::replace(FIntegrated,new DataField(Tpbool,-1,&is_integrated_),DMI::ANONWR);
}

DataField & Result::wrVellSets ()
{
  Thread::Mutex::Lock lock(mutex());
  if( !vellsets_.isWritable() )
  {
    vellsets_.privatize(DMI::WRITE);
    DataRecord::replace(FVellSets,vellsets_.dewr_p(),DMI::ANONWR);
  }
  return vellsets_();
}

VellSet & Result::setNewVellSet (int i,int nspids,int nset)
{ 
  Thread::Mutex::Lock lock(mutex());
  VellSet *pvs = new VellSet(nspids,nset);
  VellSet::Ref resref(pvs,DMI::ANONWR); 
  setVellSet(i,resref);
  if( hasCells() )
    pvs->setShape(cells().shape());
  return *pvs;
}


//##ModelId=400E535501AD
const VellSet & Result::setVellSet (int i,VellSet::Ref::Xfer &vellset)
{
  Thread::Mutex::Lock lock(mutex());
//  DbgFailWhen(isFail(),"Result marked as a fail, can't set vellset");
  const VellSet & vs = *vellset;
  ObjRef ref = vellset;
  wrVellSets().put(i,ref);
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

void Result::integrate (bool reverse)
{
  Thread::Mutex::Lock lock(mutex());
  const Cells &cc = cells();
  if( reverse && isIntegrated() )
    return;
  if( !reverse && !isIntegrated() )
    return;
  // compute cellsize, as scalar or matrix, depending on properties of cells
  Vells cellsize;
  // is the cell size regular?
  bool is_regular = true;
  double csz = 1;
  for( int i=0; i<Axis::MaxAxis; i++ )
    if( cc.isDefined(i) )
    {
      if( cc.numSegments(i)>1 )
      {
        is_regular = false;
        break;
      }
      else
        csz *= double(cc.cellSize(i)(0));
    }
  // regular cell sizes -- have been accumulated in csz
  if( is_regular )
  {
    if( reverse )
      csz = 1/csz;
    cellsize = Vells(csz);
  }
  else // irregular sizes -- compute a Vells of cell sizes
  {
    cellsize = Vells(1.);
    Vells::Shape shape0(cc.rank());
    for( int i=0; i<cc.rank(); i++ )
      shape0[i] = 1;
    // multiply repeatedly by each cell size
    for( int iaxis=0; iaxis<cc.rank(); iaxis++ )
      if( cc.isDefined(iaxis) )
      {
        // create Vells variable only along this axis, containing cell sizes
        Vells::Shape shape(shape0);
        int nc = cc.ncells(iaxis);
        shape[iaxis] = nc;
        Vells sz(0.,shape,false);
        memcpy(sz.realStorage(),cc.cellSize(iaxis).data(),sizeof(double)*nc);
        // multiply accumulated size
        cellsize *= sz;
      }
    if( reverse )
      cellsize = 1/cellsize;
  }
  // loop over vellsets, applying cellsize
  for( int ivs=0; ivs<numVellSets(); ivs++ )
  {
    VellSet &vs = vellSetWr(ivs);
    if( !vs.isFail() )
    {
      vs.setValue(vs.getValue()*cellsize);
      for( int iset=0; iset<vs.numPertSets(); iset++ )
        for( int i=0; i<vs.numSpids(); i++ )
          vs.setPerturbedValue(i,vs.getPerturbedValue(i,iset)*cellsize,iset);
    }
  }
  // if all succeeds, set flag
  setIsIntegrated(!reverse);
}

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
