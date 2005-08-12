//# Stokes.cc: Application of the Stokes Matrix
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

#include <MeqNodes/Stokes.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Cells.h>
#include <MEQ/Vells.h>
//#include <MeqNodes/Add.h>
//#include <MeqNodes/ToComplex.h>

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
    const Result &tempres = childres.at(0);
    const Cells& cells = childres.at(0)->cells();

    const VellSet &vsI = tempres.vellSet(0);
    const VellSet &vsQ = tempres.vellSet(1);
    const VellSet &vsU = tempres.vellSet(2);
    const VellSet &vsV = tempres.vellSet(3);

    const Vells::Shape &shape = vsI.shape();

    const Vells &vellsI = vsI.getValue();
    const Vells &vellsQ = vsQ.getValue();
    const Vells &vellsU = vsU.getValue();
    const Vells &vellsV = vsV.getValue();

    Vells vellsc0 = Vells(double(0.0),shape,false);

    // For now consider Linear Polarization
    Vells vellsXX = tocomplex((vellsI + vellsQ)/2,vellsc0);
    Vells vellsXY = tocomplex(vellsU/2,vellsV/2);
    Vells vellsYX = tocomplex(vellsU/2,-vellsV/2);
    Vells vellsYY = tocomplex((vellsI-vellsQ)/2,vellsc0);

    resref <<= new Result(4);

    VellSet& vs0 = resref().setNewVellSet(0);
    VellSet& vs1 = resref().setNewVellSet(1);
    VellSet& vs2 = resref().setNewVellSet(2);
    VellSet& vs3 = resref().setNewVellSet(3);

    vs0.setValue(vellsXX);
    vs1.setValue(vellsXY);
    vs2.setValue(vellsYX);
    vs3.setValue(vellsYY);

    resref().setCells(cells);
    
    return 0;
    
  };
  
  void Stokes::setStateImpl (DMI::Record::Ref& rec, bool initializing)
  {
    Node::setStateImpl(rec,initializing);
  }

  
} // namespace Meq
