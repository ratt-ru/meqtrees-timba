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

int Result::nctor = 0;
int Result::ndtor = 0;

static NestableContainer::Register reg(TpMeqResult,True);

Result::Result (int nvellsets)
: itsCells(0)
{
  nctor++;
  if( nvellsets>0 )
    allocateVellSets(nvellsets);
}

Result::Result (int nvellsets,const Request &req)
{
  nctor++;
  if( nvellsets>0 )
    allocateVellSets(nvellsets);
  setCells(&req.cells());
}

Result::Result (const Request &req,int nvellsets)
{
  nctor++;
  if( nvellsets>0 )
    allocateVellSets(nvellsets);
  setCells(&req.cells());
}
  
Result::Result (const Request &req)
{
  nctor++;
  setCells(&req.cells());
}

Result::Result (const DataRecord &other,int flags,int depth)
: DataRecord(other,flags,depth)
{
  nctor++;
  validateContent();
}

Result::~Result()
{
  ndtor--;
}

void Result::allocateVellSets (int nvellsets)
{
  itsVellSets <<= new DataField(TpMeqVellSet,nvellsets);
  DataRecord::replace(FVellSets,itsVellSets.dewr_p(),DMI::ANONWR);
}

//  implement privatize
void Result::privatize (int flags, int depth)
{
  // if deep-privatizing, detach shortcuts
  if( flags&DMI::DEEP || depth>0 )
    itsVellSets.detach();
  DataRecord::privatize(flags,depth);
}

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
      itsVellSets <<= (*this)[FVellSets].ref(DMI::PRESERVE_RW);
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

void Result::setCells (const Cells *cells,int flags)
{
  FailWhen(!isWritable(),"r/w access violation");
  itsCells = flags&DMI::CLONE ? new Cells(*cells) : cells;
  DataRecord::replace(FCells,itsCells,flags|DMI::READONLY);
}

VellSet & Result::setVellSet (int i,VellSet *vellset)
{
  FailWhen(!isWritable(),"r/w access violation");
//  DbgFailWhen(isFail(),"Result marked as a fail, can't set vellset");
  itsVellSets().put(i,vellset,DMI::ANONWR);
  return *vellset;
}
  
VellSet & Result::setVellSet (int i,VellSet::Ref::Xfer &vellset)
{
  FailWhen(!isWritable(),"r/w access violation");
//  DbgFailWhen(isFail(),"Result marked as a fail, can't set vellset");
  VellSet *pvs;
  itsVellSets().put(i,pvs=vellset.dewr_p(),DMI::ANONWR);
  vellset.detach();
  return *pvs;
}

bool Result::hasFails () const
{
  for( int i=0; i<numVellSets(); i++ )
    if( vellSetConst(i).isFail() )
      return true;
  return false;
}

int Result::numFails () const
{
  int count=0;
  for( int i=0; i<numVellSets(); i++ )
    if( vellSetConst(i).isFail() )
      count++;
  return count;
}

void Result::show (std::ostream& os) const
{
  if( !isWritable() )
    os << "(readonly)";
  for( int i=0; i<numVellSets(); i++ )
  {
    os << "VellSet "<<i<<endl;
    vellSetConst(i).show(os);
  }
}

} // namespace Meq
