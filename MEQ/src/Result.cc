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
Result::Result (int nvellsets)
: itsCells(0)
{
  nctor++;
  if( nvellsets>0 )
    allocateVellSets(nvellsets);
}

//##ModelId=400E535500F5
Result::Result (int nvellsets,const Request &req)
{
  nctor++;
  if( nvellsets>0 )
    allocateVellSets(nvellsets);
  setCells(&req.cells());
}

//##ModelId=400E53550105
Result::Result (const Request &req,int nvellsets)
{
  nctor++;
  if( nvellsets>0 )
    allocateVellSets(nvellsets);
  setCells(&req.cells());
}
  
//##ModelId=3F8688700151
Result::Result (const Request &req)
{
  nctor++;
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
  itsVellSets <<= new DataField(TpMeqVellSet,nvellsets);
  DataRecord::replace(FVellSets,itsVellSets.dewr_p(),DMI::ANONWR);
}

//  implement privatize
//##ModelId=400E53550142
void Result::privatize (int flags, int depth)
{
  // if deep-privatizing, then detach shortcuts -- they will be reattached 
  // by validateContent()
  if( flags&DMI::DEEP || depth>0 )
    itsVellSets.detach();
  DataRecord::privatize(flags,depth);
}

//##ModelId=400E53550156
void Result::validateContent ()
{
  Thread::Mutex::Lock lock(mutex());
  // ensure that our record contains all the right fields, and that they're
  // indeed writable. Setup shortcuts to their contents
  try
  {
    if( hasField(FCells) ) // verify cells field
      itsCells = (*this)[FCells].as_p<Cells>();
    else
      itsCells = 0;
    itsVellSets.detach();
    // get pointer to vellsets field
    if( DataRecord::hasField(FVellSets) )
    {
      itsVellSets <<= (*this)[FVellSets].ref();
      FailWhen(itsVellSets->type()!=TpMeqVellSet,"illegal "+FVellSets.toString()+" field");
    }
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
  itsCells = flags&DMI::CLONE ? new Cells(*cells) : cells;
  DataRecord::replace(FCells,itsCells,flags|DMI::READONLY);
}


DataField & Result::wrVellSets ()
{
  Thread::Mutex::Lock lock(mutex());
  if( !itsVellSets.isWritable() )
  {
    itsVellSets.privatize(DMI::WRITE);
    DataRecord::replace(FVellSets,itsVellSets.dewr_p(),DMI::ANONWR);
  }
  return itsVellSets();
}


//##ModelId=400E5355019D
VellSet & Result::setVellSet (int i,VellSet *vellset)
{
//  DbgFailWhen(isFail(),"Result marked as a fail, can't set vellset");
  wrVellSets().put(i,vellset,DMI::ANONWR);
  return *vellset;
}
  
//##ModelId=400E535501AD
VellSet & Result::setVellSet (int i,VellSet::Ref::Xfer &vellset)
{
//  DbgFailWhen(isFail(),"Result marked as a fail, can't set vellset");
  VellSet *pvs;
  wrVellSets().put(i,pvs=vellset.dewr_p(),DMI::ANONWR);
  vellset.detach();
  return *pvs;
}

//##ModelId=400E535501D1
bool Result::hasFails () const
{
  for( int i=0; i<numVellSets(); i++ )
    if( vellSet(i).isFail() )
      return true;
  return false;
}

//##ModelId=400E535501D4
int Result::numFails () const
{
  int count=0;
  for( int i=0; i<numVellSets(); i++ )
    if( vellSet(i).isFail() )
      count++;
  return count;
}

//##ModelId=3F868870014C
void Result::show (std::ostream& os) const
{
  for( int i=0; i<numVellSets(); i++ )
  {
    const VellSet &vs = vellSet(i);
    os << "VellSet "<<i<<": "<<&vs<<endl;
    vs.show(os);
  }
}

} // namespace Meq
