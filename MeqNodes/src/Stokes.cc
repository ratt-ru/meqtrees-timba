//# Stokes.cc: Application of the Stokes Matrix
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

#include <MeqNodes/Stokes.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/Vells.h>

using namespace Meq::VellsMath;

namespace Meq {
  
  Stokes::Stokes()
  { };
  
  Stokes::~Stokes()
  { };
  
  
  int Stokes::getResult (Result::Ref &resref,
			  const std::vector<Result::Ref> &childres,
			  const Request &request,bool newreq)
  {

    // Combine the four (real) planes of the child result into four new (complex) planes:
    // plane 0 = (plane 0 + plane 1)/2
    // plane 1 = (plane 2 + I * plane 3)/2
    // plane 2 = (plane 2 - I * plane 3)/2
    // plane 3 = (plane 0 - plane 1)/2
    //
    // To do: 1) what if certain planes do not exist
    //        2) this is linear polarization, what for circular polarization?

    const Result &tempres = childres.at(0);
    const Cells& cells = childres.at(0)->cells();

    const VellSet &vsI = tempres.vellSet(0);
    const VellSet &vsQ = tempres.vellSet(1);
    const VellSet &vsU = tempres.vellSet(2);
    const VellSet &vsV = tempres.vellSet(3);

    const Vells::Shape &shape = vsI.shape();

    const Vells &vellsI = vsI.getValue();
    
    // if no U/V polarization, form up diagonal matrix
    if( vsU.isNull() && vsV.isNull() ) 
    {
      // if no Q, even easier, form up a scalar
      if( vsQ.isNull() )
      {
        resref <<= new Result(1);
        resref().setNewVellSet(0).setValue(vellsI/2);
      }
      // else diagonal matrix
      else
      {
        const Vells &vellsQ = vsQ.getValue();
        resref <<= new Result(4);
        resref().setNewVellSet(0).setValue((vellsI+vellsQ)/2);
        resref().setNewVellSet(1); // null XY
        resref().setNewVellSet(2); // null YX
        resref().setNewVellSet(3).setValue((vellsI-vellsQ)/2);
      }
    }
    // full 2x2 matrix
    else
    {
      const Vells &vellsQ = vsQ.getValue();
      const Vells &vellsU = vsU.getValue();
      const Vells &vellsV = vsV.getValue();
  
      Vells vellsc0 = Vells(double(0.0),shape,true);
  
      // For now consider Linear Polarization
      Vells vellsXX = (vellsI + vellsQ)/2;
      Vells vellsXY = tocomplex(vellsU/2,vellsV/2);
      Vells vellsYX = tocomplex(vellsU/2,-vellsV/2);
      Vells vellsYY = (vellsI-vellsQ)/2;
  
      resref <<= new Result(4);
  
      VellSet& vs0 = resref().setNewVellSet(0);
      VellSet& vs1 = resref().setNewVellSet(1);
      VellSet& vs2 = resref().setNewVellSet(2);
      VellSet& vs3 = resref().setNewVellSet(3);
  
      vs0.setValue(vellsXX);
      vs1.setValue(vellsXY);
      vs2.setValue(vellsYX);
      vs3.setValue(vellsYY);
  
      resref().setDims(LoShape(2,2));
    }
    resref().setCells(cells);
    
    return 0;
    
  };
  
  void Stokes::setStateImpl (DMI::Record::Ref& rec, bool initializing)
  {
    Node::setStateImpl(rec,initializing);
  }

  
} // namespace Meq
