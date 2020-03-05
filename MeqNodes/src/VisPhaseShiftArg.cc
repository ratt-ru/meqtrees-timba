//# VisPhaseShiftArg.cc: The point source DFT component for a station
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
//# $Id: VisPhaseShiftArg.cc 5418 2007-07-19 16:49:13Z oms $

#include <MeqNodes/VisPhaseShiftArg.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <casacore/casa/BasicSL/Constants.h>

namespace Meq {    

using namespace VellsMath;

const HIID child_labels[] = { AidLMN,AidUVW };
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);


VisPhaseShiftArg::VisPhaseShiftArg()
: TensorFunction(num_children,child_labels)
{
  // dependence on frequency 
  const HIID symdeps[] = { AidDomain,AidResolution };
  setActiveSymDeps(symdeps,2);
}

VisPhaseShiftArg::~VisPhaseShiftArg()
{}

LoShape VisPhaseShiftArg::getResultDims (const vector<const LoShape *> &input_dims)
{
  Assert(input_dims.size()==2);
  // inputs are 2-vectors
  for( int i=0; i<2; i++ )
  {
    const LoShape &dim = *input_dims[i];
    FailWhen(dim.size()!=1 || dim[0]!=3,"child '"+child_labels[i].toString()+"': 3-vector expected");
  }
  // check cells
  FailWhen(!hasResultCells(),"no cells found in either child results or request");
  // result is a scalar
  return LoShape();
}


void VisPhaseShiftArg::evaluateTensors (std::vector<Vells> & out,   
     const std::vector<std::vector<const Vells *> > &args )
{
  // lmn
  const Vells & vl = *(args[0][0]);
  const Vells & vm = *(args[0][1]);
  const Vells & vn = *(args[0][2]);
  // uvw 
  const Vells & vu = *(args[1][0]);
  const Vells & vv = *(args[1][1]);
  const Vells & vw = *(args[1][2]);
  // cells
  const Cells & cells = resultCells();
  
  // compute argument term
  Vells r1 = -(vu*vl + vv*vm + vw*vn);
  const double _2pi_over_c = casacore::C::_2pi / casacore::C::c;

  int nfreq = cells.ncells(Axis::FREQ);
  Vells freq(0,Axis::vectorShape(Axis::FREQ,nfreq),false);
  memcpy(freq.realStorage(),cells.center(Axis::FREQ).data(),nfreq*sizeof(double));
  out[0] = r1*(_2pi_over_c*freq);
}


} // namespace Meq
