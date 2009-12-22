//# VisPhaseShift.cc: The point source DFT component for a station
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

#include <MeqNodes/VisPhaseShift.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <casa/BasicSL/Constants.h>

namespace Meq {    

using namespace VellsMath;

const HIID child_labels[] = { AidLMN,AidUVW };
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);

const HIID FDomain = AidDomain;

VisPhaseShift::VisPhaseShift()
: TensorFunction(num_children,child_labels)
{
  // dependence on frequency 
  const HIID symdeps[] = { AidDomain,AidResolution };
  setActiveSymDeps(symdeps,2);
}

VisPhaseShift::~VisPhaseShift()
{}

LoShape VisPhaseShift::getResultDims (const vector<const LoShape *> &input_dims)
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


void VisPhaseShift::evaluateTensors (std::vector<Vells> & out,   
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
  
  // compute phase term
  Vells r1 = -(vu*vl + vv*vm + vw*vn);
  const double _2pi_over_c = casa::C::_2pi / casa::C::c;

  // Now, if r1 is only variable in time, and we only have one
  // regularly-spaced frequency segment, we can use a quick algorithm
  // to compute only the exponent at freq0 and df, and then multiply
  // the rest.
  // Otherwise we fall back to the (potentially slower) full VellsMath
  
  if( r1.extent(Axis::TIME) == r1.nelements() &&
      cells.ncells(Axis::FREQ) > 1            &&
      cells.numSegments(Axis::FREQ) == 1        )  // fast eval possible
  {
    // Calculate 2pi/wavelength, where wavelength=c/freq.
    // Calculate it for the frequency step if needed.
    double f0 = cells.center(Axis::FREQ)(0);
    double df = cells.center(Axis::FREQ)(1) - f0;
    double wavel0 = f0 * _2pi_over_c;
    double dwavel = df / f0;

    r1 *= wavel0;

    Vells vf0 = polar(1,r1);
    Vells vdf = polar(1,r1*dwavel);
    
    int ntime = r1.extent(Axis::TIME);
    int nfreq = cells.ncells(Axis::FREQ);
    LoShape result_shape(ntime,nfreq);

    out[0]              = Vells(numeric_zero<dcomplex>(),result_shape);
    dcomplex* resdata   = out[0].complexStorage();
    const dcomplex* pf0 = vf0.complexStorage();
    const dcomplex* pdf = vdf.complexStorage();

    int step = (ntime > 1 ? 1 : 0);
    for(int i = 0; i < ntime; i++)
    {
      dcomplex val0 = *pf0;
      *resdata++    = val0;
      dcomplex dval = *pdf;
      for(int j=1; j < nfreq; j++)
      {
        val0      *= dval;
        *resdata++ = val0;
      }// for j (freq)
      pf0 += step;
      pdf += step;
    }// for i (time)
  }
  else // slower but much simpler
  {
    // create freq vells from grid 
    int nfreq = cells.ncells(Axis::FREQ);
    Vells freq(0,Axis::vectorShape(Axis::FREQ,nfreq),false);
    memcpy(freq.realStorage(),cells.center(Axis::FREQ).data(),nfreq*sizeof(double));
    out[0] = polar(1,r1*(_2pi_over_c*freq));
  }

}


} // namespace Meq
