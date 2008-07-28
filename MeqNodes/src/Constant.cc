//# Constant.cc: Real or complex constant
//#
//# Copyright (C) 2002-2007
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# and The MeqTree Foundation
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
#include <TimBase/Debug.h>
#include <TimBase/Lorrays.h>
// #include <casa/BasicMath/Math.h>

namespace Meq {

const HIID dom_symdeps[] = { FDomain,FResolution };

//const HIID FDomain = AidDomain;
const HIID FVells = AidVells;

Constant::Constant ()
: Node (0), // must have 0 children
  integrated_(false)
{
  (result_ <<= new Result(1)).setNewVellSet(0);
}

//##ModelId=400E5305008F
Constant::Constant (double value,bool integrated)
: Node (0), // must have 0 children
  integrated_(integrated)
{
  (result_ <<= new Result(1)).setNewVellSet(0).setValue(new Vells(value,false));
  // intregrated results depend on cells
  if( integrated )
    setActiveSymDeps(dom_symdeps,2);
}

//##ModelId=400E53050094
Constant::Constant (const dcomplex& value,bool integrated)
: Node (0),
  integrated_(integrated)
{
  (result_ <<= new Result(1)).setNewVellSet(0).setValue(new Vells(value,false));
  // intregrated results depend on cells
  if( integrated )
    setActiveSymDeps(dom_symdeps,2);
}

//##ModelId=400E53050098
Constant::~Constant()
{}

//##ModelId=400E5305009C
int Constant::getResult (Result::Ref& resref,
			 const std::vector<Result::Ref>&,
			 const Request& request, bool)
{
  // Copy result to output
  resref = result_;
  // integrate or simply attach cells as needed
  const Cells &cells = request.cells();
  if( resref->needsCells(cells) )
    resref().setCells(cells);
  return 0;
}

//##ModelId=400E530500B5
void Constant::setStateImpl (DMI::Record::Ref& rec, bool initializing)
{
  Node::setStateImpl(rec,initializing);
  // get integrated flag
  if( rec[FIntegrated].get(integrated_,initializing) )
  {
    if( integrated_ )
      setActiveSymDeps(dom_symdeps,2);
    else // not integrated -- no dependency (value same regardless of domain/cells)
      setActiveSymDeps();
  }
  // Get value
  DMI::Record::Hook hook(rec,FValue);
  DMI::Record::Hook hook2(rec,FVells);
  if( hook.exists() )
  {
    TypeId type = hook.type();
    // can we access this as a NumArray?
    const DMI::NumArray *parr = hook.as_po<DMI::NumArray>();
    // a scalar may have been passed in as a 1-element array
    if( parr )
    {
      const LoShape &shp = parr->shape();
      if( parr->size() < 1 )
        Throw("illegal array size in field "+FValue.toString());
      type = parr->elementType();
      // [1] array treated as scalar
      if( shp.size() == 1 && parr->size() == 1 )
      {
        // create scalar vells for result, using the hook conversion functions
        Vells::Ref vells;
        if( type == Tpdcomplex || type == Tpfcomplex )
          vells <<= new Vells((*parr)[HIID()].as<dcomplex>(),false);
        else
          vells <<= new Vells((*parr)[HIID()].as<double>(),false);
        (result_ <<= new Result(1)).setNewVellSet(0).setValue(vells);
      }
      else // tensor result
      {
        FailWhen(type!=Tpdcomplex && type!=Tpdouble,
            "field "+FValue.toString()+" is of illegal type "+type.toString());
        if( type == Tpdcomplex )
        {
          Result &res = result_ <<= new Result(shp);
          const dcomplex *data = static_cast<const dcomplex*>(parr->getConstDataPtr());
          for( int i=0; i<parr->size(); i++ )
            res.setNewVellSet(i).setValue(new Vells(data[i],false));
        }
        else if( type == Tpdouble )
        {
          Result &res = result_ <<= new Result(shp);
          const double *data = static_cast<const double*>(parr->getConstDataPtr());
          for( int i=0; i<parr->size(); i++ )
            res.setNewVellSet(i).setValue(new Vells(data[i],false));
        }
      }
    }
    else // scalar value: create scalar result
    {
      Vells::Ref vells;
      // complex values forced to dcomplex; all other to double
      if( type == Tpdcomplex || type == Tpfcomplex )
        vells <<= new Vells(hook.as<dcomplex>(),false);
      else
        vells <<= new Vells(hook.as<double>(),false);
      (result_ <<= new Result(1)).setNewVellSet(0).setValue(vells);
    }
  }
  else if( hook2.exists() ) // kludge to insert explicit vells
  {
    Vells::Ref vells(new Vells(hook2.as<DMI::NumArray>()));
    (result_ <<= new Result(1)).setNewVellSet(0).setValue(vells);
  }
  else if( initializing ) // init state record with default value
  {
    if( result_->vellSet(0).hasValue() )
      rec[FValue] <<= result_->vellSet(0).getValue();
  }
}

//##ModelId=400E530500AD
string Constant::sdebug (int detail, const string &prefix,const char* nm) const
{
  return Node::sdebug(detail,prefix,nm);
}

} // namespace Meq
