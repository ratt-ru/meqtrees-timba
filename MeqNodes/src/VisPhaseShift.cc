//# VisPhaseShift.cc: The point source DFT component for a station
//#
//# Copyright (C) 2004
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
: CompoundFunction(num_children,child_labels)
{
  // dependence on frequency 
  const HIID symdeps[] = { FDomain,FResolution };
  setActiveSymDeps(symdeps,2);
}

VisPhaseShift::~VisPhaseShift()
{}

void VisPhaseShift::evalResult (std::vector<Vells> &res,
                            const std::vector<const Vells*> &values,
                            const Cells *pcells)
{
  // Get L,M,N and U,V,W.
  #define vl (*(values[0]))
  #define vm (*(values[1]))
  #define vn (*(values[2]))
  #define vu (*(values[3]))
  #define vv (*(values[4]))
  #define vw (*(values[5]))
  Assert(pcells);
  
  // Some important assumptions
  // For the time being we only support scalars for LMN, 
  Assert(vl.isScalar() && vm.isScalar() && vn.isScalar() );
  // and only time-variable UVW
  Assert(vu.extent(Axis::TIME) == vu.nelements());
  Assert(vv.extent(Axis::TIME) == vv.nelements());
  Assert(vw.extent(Axis::TIME) == vw.nelements());
  Assert(pcells->numSegments(Axis::FREQ) == 1);
  // Loop over all frequency segments, and generate an F0/DF pair for each
  //  for( int iseg = 0; iseg < pcells->numSegments(Axis::FREQ); iseg++ )
  //  {
  int seg0 = pcells->segmentStart(Axis::FREQ)(0);
  // Calculate 2pi/wavelength, where wavelength=c/freq.
  // Calculate it for the frequency step if needed.
  double f0 = pcells->center(Axis::FREQ)(seg0);
  double df = pcells->cellSize(Axis::FREQ)(seg0);
  double wavel0 = casa::C::_2pi * f0 / casa::C::c;
  double dwavel = df / f0;
  
  Vells r1 = -(vu*vl + vv*vm +vw*vn ) * wavel0;

  Vells vf0 = polar(1,r1);
  Vells vdf = polar(1,r1*dwavel);

  res[0]              = Vells(dcomplex(0), itsResult_shape, false);
  dcomplex* resdata   = res[0].complexStorage();
  const dcomplex* pf0 = vf0.complexStorage();
  const dcomplex* pdf = vdf.complexStorage();

  int step = (vf0.extent(Axis::TIME) > 1 ? 1 : 0);
  for(int i = 0; i < itsNtime; i++){
      dcomplex val0 = *pf0;
      *resdata++    = val0;
      dcomplex dval = *pdf;
      for(int j=1; j < itsNfreq; j++){
          val0      *= dval;
          *resdata++ = val0;
      }// for j (freq)
      pf0 += step;
      pdf += step;
  }// for i (time)

//    res[iout++] = polar(1,r1);
//    res[iout++] = polar(1,r1*dwavel);
//  }
}


int VisPhaseShift::getResult (Result::Ref &resref, 
				   const std::vector<Result::Ref> &childres,
				   const Request &request, bool newreq)
{
  std::vector<Thread::Mutex::Lock> child_reslock(numChildren());
  lockMutexes(child_reslock,childres);
  const int expect_nvs[]        = {3,3}; // number of Vells in children
  const int expect_integrated[] = {-1,-1};
  Assert(int(childres.size()) == num_children);

  // Check that child results are all OK (no fails, expected # of vellsets per child)
  vector<const VellSet *> child_vs(6);
  if( checkChildResults(resref,child_vs,childres,expect_nvs,
        expect_integrated) == RES_FAIL ){
      return RES_FAIL;
  }

  // allocate proper output result (integrated=false??)
  const Cells &cells = request.cells();
  FailWhen(!cells.isDefined(Axis::FREQ),"Cells must define a frequency axis");
  FailWhen(!cells.isDefined(Axis::TIME),"Cells must define a time axis");
  
  Result& result = resref <<= new Result(1);
  itsNfreq        = cells.ncells(Axis::FREQ);
  itsNtime        = cells.ncells(Axis::TIME);
  itsResult_shape = Axis::freqTimeMatrix(itsNfreq, itsNtime);
  
  // fill it
  computeValues(resref(),child_vs,&cells);
  result.setCells(cells);
  
  return 0;
}

} // namespace Meq
