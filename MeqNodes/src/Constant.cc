//# Constant.cc: Real or complex constant
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

#include <MeqNodes/Constant.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/MeqVocabulary.h>
#include <Common/Debug.h>
#include <Common/Lorrays.h>
// #include <casa/BasicMath/Math.h>

namespace Meq {

const HIID symdeps[] = { FDomain,FResolution };

//const HIID FDomain = AidDomain;
const HIID FVells = AidVells;

//##ModelId=400E5305008F
Constant::Constant (double value,bool integrated)
: Node (0), // must have 0 children
  itsValue (new Vells(value, false),DMI::ANONWR),
  itsIntegrated(integrated)
{
  setKnownSymDeps(symdeps,2);
  // intregrated results depend on cells
  if( integrated )
    setActiveSymDeps(symdeps,2);
}

//##ModelId=400E53050094
Constant::Constant (const dcomplex& value,bool integrated)
: Node (0),
  itsValue(new Vells(value, false),DMI::ANONWR),
  itsIntegrated(integrated)
{
  setKnownSymDeps(symdeps,2);
  // intregrated results depend on cells
  if( integrated )
    setActiveSymDeps(symdeps,2);
}

//##ModelId=400E53050098
Constant::~Constant()
{}

//##ModelId=400E5305009C
int Constant::getResult (Result::Ref& resref,
			 const std::vector<Result::Ref>&,
			 const Request& request, bool)
{
  // Create result object and attach to the ref that was passed in
  Result& result = resref <<= new Result(1,request); // result has one vellset
  VellSet& vs = result.setNewVellSet(0);
  // if value is a Vells, check that shapes match
  Vells &val = itsValue();
  FailWhen(hasShape && !val.isCompatible(request.cells().shape()),
      "shape of Vells in Constant node not compatible with request");
  vs.setValue(val);
  if( itsIntegrated )
    result.integrate();
  return 0;
}

//##ModelId=400E530500B5
void Constant::setStateImpl (DataRecord& rec, bool initializing)
{
  Node::setStateImpl(rec,initializing);
  // get integrated flag
  if( rec[FIntegrated].get(itsIntegrated,initializing) )
  {
    if( itsIntegrated )
      setActiveSymDeps(symdeps,2);
    else // not integrated -- no dependency (value same regardless of domain/cells)
      setActiveSymDeps();
  }
  // Get value
  DataRecord::Hook hook(rec,FValue);
  DataRecord::Hook hook2(rec,FVells);
  if( hook.exists() ) 
  {
    TypeId type = hook.type();
    // complex values forced to dcomplex; all other to double
    if( type == Tpdcomplex || type == Tpfcomplex ) 
      itsValue <<= new Vells(hook.as<dcomplex>());
    else 
      itsValue <<= new Vells(hook.as<double>());
    hasShape = false;
  }
  else if( hook2.exists() )
  {
    itsValue <<= new Vells(hook2.as_p<DataArray>());
    hasShape = true;
  }
  else if( initializing ) // init state record with default value
  {
    rec[FValue] <<= itsValue->getDataArray();
    hasShape = false;
  }
}

//##ModelId=400E530500AD
string Constant::sdebug (int detail, const string &prefix,const char* nm) const
{
  return Node::sdebug(detail,prefix,nm);
}

} // namespace Meq
