//# Request.cc: The request for an evaluation of an expression
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

#include "Request.h"
#include "MeqVocabulary.h"

namespace Meq {

static NestableContainer::Register reg(TpMeqRequest,True);

//##ModelId=3F8688700056
Request::Request()
    : itsCalcDeriv(False),itsCells(0)
{
}

//##ModelId=3F8688700061
Request::Request (const DataRecord &other,int flags,int depth)
: DataRecord   (other,flags,depth),
  itsCalcDeriv (False),itsCells(0)
{
  validateContent();
}

//##ModelId=400E535403DD
Request::Request (const Cells& cells, bool calcDeriv, const HIID &id,int cellflags)
: itsCalcDeriv (calcDeriv),
  itsCells     (0)
{
  setCells(cells,cellflags);
  setId(id);
  (*this)[FCalcDeriv] = calcDeriv;
}

//##ModelId=400E53550016
Request::Request (const Cells * cells, bool calcDeriv, const HIID &id,int cellflags)
: itsCalcDeriv (calcDeriv),
  itsCells     (0)
{
  setCells(cells,cellflags);
  setId(id);
  (*this)[FCalcDeriv] = calcDeriv;
}

// Set the request id.
//##ModelId=3F8688700075
void Request::setId (const HIID &id)
{
  (*this)[FRequestId] = itsId = id;
}

//##ModelId=3F868870006E
void Request::setCells (const Cells * cells,int flags)
{
  itsCells = flags&DMI::CLONE ? new Cells(*cells) : cells;
  DataRecord::replace(FCells,itsCells,flags|DMI::READONLY);
}

//##ModelId=400E53550049
void Request::validateContent ()
{
  Thread::Mutex::Lock lock(mutex());
  // ensure that our record contains all the right fields, and that they're
  // indeed writable. Setup shortcuts to their contents
  try
  {
    // get cells field
    if( (*this)[FCells].exists() ) 
      itsCells = (*this)[FCells].as_p<Cells>();
    else
      itsCells = 0;
    // request ID
    itsId = (*this)[FRequestId].as<HIID>(HIID());
    // calc-driv flag
    itsCalcDeriv = (*this)[FCalcDeriv].as<bool>(False);
  }
  catch( std::exception &err )
  {
    cerr<<"Failed request: "<<sdebug(10);
    Throw(string("validate of Request record failed: ") + err.what());
  }
  catch( ... )
  {
    Throw("validate of Request record failed with unknown exception");
  }  
}

int Request::remove (const HIID &id)
{ 
  if( id == FCells || id == FRequestId || id==FCalcDeriv )
    Throw("remove(" + id.toString() +" from a Meq::Request not allowed"); 
  return DataRecord::remove(id);
}

} // namespace Meq
