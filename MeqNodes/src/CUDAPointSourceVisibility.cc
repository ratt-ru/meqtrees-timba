//# CUDAPointSourceVisibility.cc: The point source DFT component for a station
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
//# $Id: CUDAPointSourceVisibility.cc 8270 2011-07-06 12:17:23Z oms $

#include <MeqNodes/CUDAPointSourceVisibility.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <casa/BasicSL/Constants.h>

namespace Meq {

InitDebugContext(CUDAPointSourceVisibility,"CUDAPSV");
  
  
using namespace VellsMath;

const HIID child_labels[] = { AidLMN,AidB,AidUVW };
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);


CUDAPointSourceVisibility::CUDAPointSourceVisibility()
: TensorFunction(num_children,child_labels)
{
  // dependence on frequency
  const HIID symdeps[] = { AidDomain,AidResolution };
  setActiveSymDeps(symdeps,2);
}

CUDAPointSourceVisibility::~CUDAPointSourceVisibility()
{}

const LoShape shape_3vec(3),shape_2x3(2,3);

LoShape CUDAPointSourceVisibility::getResultDims (const vector<const LoShape *> &input_dims)
{
  // this gets called to check that the child results have the right shape
  const LoShape &lmn = *input_dims[0], &b = *input_dims[1], &uvw = *input_dims[2];
  
  // the first child (LMN) is expected to be of shape Nx3, the second (B) of Nx2x2, and the third (UVW) is a 3-vector
  FailWhen(lmn.size()!=2 || lmn[1]!=3,"child '"+child_labels[0].toString()+"': an Nx3 result expected");
  FailWhen(b.size()!=3 || b[1]!=2 || b[2]!=2,"child '"+child_labels[1].toString()+"': an Nx2x2 result expected");
  FailWhen(lmn[0] != b[0],"shape mismatch between child '"+
                           child_labels[0].toString()+"' and '"+child_labels[1].toString()+"'");
  FailWhen(uvw.size() != 1 || uvw[0] != 3,"child '"+child_labels[2].toString()+"': a 3-vector expected");
  
  num_sources_ = lmn[0];
  // result is a 2x2 matrix 
  return LoShape(2,2);
}


void CUDAPointSourceVisibility::evaluateTensors (std::vector<Vells> & out,
     const std::vector<std::vector<const Vells *> > &args )
{
  // cells
  const Cells & cells = resultCells();
  const double _2pi_over_c = -casa::C::_2pi / casa::C::c;
  // the frequency axis
  int nfreq = cells.ncells(Axis::FREQ);
  const double * freq_data = cells.center(Axis::FREQ).data();
  const double * freq_cell = cells.cellSize(Axis::FREQ).data();
  // the time axis
  int ntime = cells.ncells(Axis::TIME);
  
  LoShape timeshape = Axis::timeVector(ntime);
  LoShape freqshape = Axis::freqVector(nfreq);
  LoShape timefreqshape = Axis::freqTimeMatrix(nfreq,ntime);
  
  // uvw coordinates are the same for all sources, and each had better be a 'timeshape' vector
  const Vells & vu = *(args[2][0]);
  const Vells & vv = *(args[2][1]);
  const Vells & vw = *(args[2][2]);
  FailWhen(vu.shape() != timeshape || vv.shape() != timeshape || vw.shape() != timeshape,"expecting UVWs that are a vector in time");
  
  // these will be vectors of ntime points each
  const double *pu = vu.realStorage();
  const double *pv = vu.realStorage();
  const double *pw = vu.realStorage();
  
  // allocate storage for results, and get pointers to storage
  const int NUM_MATRIX_ELEMENTS = 4;
  dcomplex * pout[NUM_MATRIX_ELEMENTS];
  
  for( int j=0; j<4; j++ )
  {
    out[j] = Vells(numeric_zero<dcomplex>(),timefreqshape);
    pout[j] = out[j].complexStorage();
    // pout[j] points to an NTIME x NFREQ array
  }
  
  // need to compute B*exp{ i*_2pi_over_c*freq*(u*l+v*m+w*n) } for every source, and sum over all sources
  for( int isrc=0; isrc < num_sources_; isrc++ )
  {
    // get the LMNs for this source
    const Vells & vl = *(args[0][isrc*3]);
    const Vells & vm = *(args[0][isrc*3+1]);
    const Vells & vn = *(args[0][isrc*3+2]);
    FailWhen(!vl.isScalar() || !vm.isScalar() || !vn.isScalar(),"expecting scalar LMNs");
    double l = vl.as<double>();
    double m = vm.as<double>();
    double n = vn.as<double>();
    // get the B matrix elements -- there should be four of them
    for( int j=0; j<NUM_MATRIX_ELEMENTS; j++ )
    {
      const Vells &b = *(args[1][isrc*NUM_MATRIX_ELEMENTS + j]);
      FailWhen(!b.isScalar() && b.shape() != freqshape,"expecting B matrix elements that are either scalar, or a vector in frequency");
      // for each element, either b.isScalar() is true and you can access it as b.as<double>, or
      // b.realStorage() is a vector of nfreq doubles.
      
      //...do the actual work...
    }
  }
}


} // namespace Meq
