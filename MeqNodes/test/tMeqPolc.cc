//# tMeqPolc.cc: test program for class Meq::Polc
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


#include <MEQ/Polc.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Vells.h>
#include <TimBase/Debug.h>

using namespace LOFAR;
using namespace Meq;
using namespace Meq::VellsMath;


bool compare(const Vells& m1, const Vells& m2)
{
  const LoShape &shp = m1.shape();
  if (shp != m2.shape()) {
    return false;
  }
  Vells res = sum(sqr(m1-m2),shp);
  if (res.isReal()) {
    return (res.realStorage()[0] < 1.e-7);
  }
  complex<double> resc = res.complexStorage()[0];
  return (resc.real() < 1.e-7  &&  resc.imag() < 1.e-7);
}

void doIt (Polc& polc)
{
  Domain domain(0.5,4.5, -2.5,1.5);
//   Vells newc = polc.normalize (polc.getCoeff(), domain);
//   Polc newpolc;
//   newpolc.setCoeff (newc);
//   newpolc.setDomain (domain);
//   newpolc.setFreq0 (polc.getFreq0());
//   newpolc.setTime0 (polc.getTime0());
//   Vells backc = newpolc.denormalize (newpolc.getCoeff());
//   // Check if final coefficients match original.
//   Assert (compare(polc.getCoeff(), backc));
  // Evaluate both polynomials for some values.
  polc.makeSolvable(1);
  Request req(new Cells(domain, 4, 4),0);
  VellSet res1(0);
  VellSet::Ref refres1(res1, DMI::WRITE | DMI::EXTERNAL);
  refres1().setShape(req.cells().shape());
  polc.evaluate(refres1, req);
  cout << res1;
}

void doIt2 (Polc& polc,int calcDeriv)
{
  Domain domain(0,1,0,1);
  // Evaluate both polynomials for some values.
  polc.makeSolvable(1);
  Request req(new Cells(domain, 4, 4),calcDeriv);
  VellSet res1(0,calcDeriv);
  VellSet::Ref refres1(res1, DMI::WRITE | DMI::EXTERNAL);
  refres1().setShape(req.cells().shape());
  polc.evaluate(refres1, req);
  cout << res1;
}

int main()
{
  try
  {
    
    for (int i=0; i<2; i++) {
      Polc polc;
      polc.setAxis(0,Axis::FREQ,i*0.5,i+1);
      polc.setAxis(1,Axis::TIME,-i*2,1./(i+1));

      polc.setCoeff(Vells(2.,LoShape(1,1)));
      doIt (polc);

      polc.setCoeff(Vells(2.,LoShape(2,1),true));
      doIt (polc);

      polc.setCoeff(Vells(2.,LoShape(1,2),true));
      doIt (polc);

      polc.setCoeff(Vells(2.,LoShape(2,2),true));
      doIt (polc);

      double c0[4] = {4, 3, 2, 1};
      LoMat_double mat0a(c0, LoMatShape(1,4), blitz::duplicateData);
      polc.setCoeff(mat0a);
      doIt(polc);
      LoMat_double mat0b(c0, LoMatShape(4,1), blitz::duplicateData);
      polc.setCoeff(mat0b);
      doIt(polc);
      LoMat_double mat0c(c0, LoMatShape(2,2), blitz::duplicateData);
      polc.setCoeff(mat0c);
      doIt(polc);

      double c1[12] = {1.5, 2.1, -0.3, -2,
		       1.45, -2.3, 0.34, 1.7,
		       5, 1, 0, -1};
      LoMat_double mat1(c1, LoMatShape(3,4), blitz::duplicateData);
      polc.setCoeff(mat1);
      doIt(polc);
      LoMat_double mat2(c1, LoMatShape(4,3), blitz::duplicateData);
      polc.setCoeff(mat2);
      doIt(polc);
      LoMat_double mat3(c1, LoMatShape(6,2), blitz::duplicateData);
      polc.setCoeff(mat3);
      doIt(polc);
      LoMat_double mat4(c1, LoMatShape(2,6), blitz::duplicateData);
      polc.setCoeff(mat4);
      doIt(polc);
    }
    
    Polc polc;
    polc.setAxis(0,Axis::FREQ,0,1);
    polc.setAxis(1,Axis::TIME,0,1);
    double c0[4] = {3, 2, 2, 1};
    cout<<"calculating polc [3,2,2,1] (4x1):\n";
    LoMat_double mat0a(c0, LoMatShape(4,1), blitz::duplicateData);
    polc.setCoeff(mat0a);
    doIt2(polc,1);
    polc.setCoeff(mat0a);
    doIt2(polc,2);
    
    cout<<"calculating polc [3,2,2,1] (1x4):\n";
    LoMat_double mat0b(c0, LoMatShape(1,4), blitz::duplicateData);
    polc.setCoeff(mat0b);
    doIt2(polc,2);
    
    cout<<"calculating polc [[3,2],[2,1]] (2x2):\n";
    LoMat_double mat0c(c0, LoMatShape(2,2), blitz::duplicateData);
    polc.setCoeff(mat0c);
    doIt2(polc,2);
  }
  catch( std::exception &err )
  {
    cout << "ERROR: " <<err.what()<< endl;
    return 1;
  }
  cout << "OK" << endl;
  return 0;
}
