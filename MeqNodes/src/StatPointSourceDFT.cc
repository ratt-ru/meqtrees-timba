//# StatPointSourceDFT.cc: The point source DFT component for a station
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

#include <MeqNodes/StatPointSourceDFT.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <casa/BasicSL/Constants.h>

namespace Meq {    

using namespace VellsMath;

const HIID child_labels[] = { AidLMN,AidUVW };
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);

const HIID FDomain = AidDomain;

StatPointSourceDFT::StatPointSourceDFT()
: CompoundFunction(num_children,child_labels)
{
  // dependence on frequency 
  const HIID symdeps[] = { FDomain,FResolution };
  setActiveSymDeps(symdeps,2);
}

StatPointSourceDFT::~StatPointSourceDFT()
{}

void StatPointSourceDFT::evalResult (std::vector<Vells> &res,
                            const std::vector<const Vells*> &values,
                            const Cells &cells)
{
  // Get L,M,N and U,V,W.
  #define vl (*(values[0]))
  #define vm (*(values[1]))
  #define vn (*(values[2]))
  #define vu (*(values[3]))
  #define vv (*(values[4]))
  #define vw (*(values[5]))
  
  // For the time being we only support scalars for LMN
  Assert (vl.isScalar() && vm.isScalar() && vn.isScalar());
  
  // Loop over all frequency segments, and generate an F0/DF pair for each
  int iout = 0;
  for( int iseg = 0; iseg < cells.numSegments(FREQ); iseg++ )
  {
    int seg0 = cells.segmentStart(FREQ)(iseg);
    // Calculate 2pi/wavelength, where wavelength=c/freq.
    // Calculate it for the frequency step if needed.
    double f0 = cells.center(FREQ)(seg0);
    double df = cells.cellSize(FREQ)(seg0);
    double wavel0 = C::_2pi * f0 / C::c;
    double dwavel = df / f0;
    Vells r1 = (vu*vl + vv*vm + vw*vn) * wavel0;
    r1.makeNonTemp();
    res[iout]  = tocomplex(cos(r1), sin(r1));
    res[iout++].makeNonTemp();
    r1 *= dwavel;
    res[iout]  = tocomplex(cos(r1), sin(r1));
    res[iout++].makeNonTemp();
  }
}


int StatPointSourceDFT::getResult (Result::Ref &resref, 
				   const std::vector<Result::Ref> &childres,
				   const Request &request, bool newreq)
{
  const int expect_nvs[]        = {3,3};
  const int expect_integrated[] = {-1,-1};
  Assert(int(childres.size()) == num_children);

  // Check that child results are all OK (no fails, expected # of vellsets per child)
  vector<const VellSet *> child_vs(6);
  if( checkChildResults(resref,child_vs,childres,expect_nvs,
        expect_integrated) == RES_FAIL )
    return RES_FAIL;
  
  // allocate proper output result (integrated=false??)
  const Cells &cells = childres[0]->cells();
  Result &result = resref <<= new Result(cells.numSegments(FREQ)*2,false);
  result.setCells(cells);
  // fill it
  computeValues(result,child_vs);
  
  return 0;
}

} // namespace Meq
