//# tMeqVells.cc: Test program for Meq::Vells classes
//# Copyright (C) 2002
//# Associated Universities, Inc. Washington DC, USA.
//#
//# This library is free software; you can redistribute it and/or modify it
//# under the terms of the GNU Library General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or (at your
//# option) any later version.
//#
//# This library is distributed in the hope that it will be useful, but WITHOUT
//# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
//# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Library General Public
//# License for more details.
//#
//# You should have received a copy of the GNU Library General Public License
//# along with this library; if not, write to the Free Software Foundation,
//# Inc., 675 Massachusetts Ave, Cambridge, MA 02139, USA.
//#
//# Correspondence concerning AIPS++ should be addressed as follows:
//#        Internet email: aips2-request@nrao.edu.
//#        Postal address: AIPS++ Project Office
//#                        National Radio Astronomy Observatory
//#                        520 Edgemont Road
//#                        Charlottesville, VA 22903-2475 USA
//#
//# $Id$


#include <MEQ/Vells.h>
#include <MEQ/VellsTmp.h>
#include <aips/Arrays/Matrix.h>
#include <aips/Arrays/ArrayMath.h>
#include <aips/Mathematics/Complex.h>
#include <aips/OS/Timer.h>
#include <aips/Exceptions/Error.h>
#include <aips/iostream.h>
#include <aips/strstream.h>

using namespace Meq;


void showDouble (const VellsTmp& v)
{
  cout << v << endl;
}
void showDComplex (const VellsTmp& v)
{
  cout << v << endl;
}

void doIt()
{
  Double d1[] = {1,2,3,4,5,6};
  Double d2[] = {2,3,4,5,6,7};
  LoMat_double m1(d1, LoMatShape(2,3), blitz::neverDeleteData);
  LoMat_double m2(d2, LoMatShape(2,3), blitz::neverDeleteData);
  Vells v1(&m1);
  Vells v2(&m2);
  Vells v3(double(10));
  showDouble (v1 + v2);
  showDouble (v1 + v2 + v1 + v2 + v3 + v3);

  DComplex dc1[6];
  dc1[0] = DComplex(1,2);
  dc1[1] = DComplex(3,4);
  dc1[2] = DComplex(5,6);
  dc1[3] = DComplex(7,8);
  dc1[4] = DComplex(9,10);
  dc1[5] = DComplex(11,12);
  LoMat_dcomplex mc1(dc1, LoMatShape(2,3), blitz::neverDeleteData);
  Vells vc1 (&mc1);
  Vells vc2 = v1 + v2 + vc1;
  Vells vc3 = v1 + vc1 + v2;
  Vells vc4 = vc1 + vc2;
  Vells vc5 = (v1 - vc1) * vc2;
  Vells vc6 = (vc2 - vc1) * v2;
  Vells vc7 = (vc2 - vc1) * vc2;
}

void doIt2 (uInt length, uInt nr)
{
  uInt i;
  {
    Double* d1 = new Double[length];
    Double* r  = new Double[length];
    for (i=0; i<length; i++) {
      d1[i] = 1;
    }
    double v3 = 10;
    Timer tim;
    for (i=0; i<nr; i++) {
      for(uInt j=0; j<length; j++) {
	r[j] = d1[j] + d1[j] + d1[j] + v3 + d1[j] + v3 + d1[j] + v3
	  + d1[j] + d1[j];
      }
    }
    tim.show ("C    ");
    delete [] d1;
    delete [] r;
  }
  {
    Double* d1 = new Double[length];
    for (i=0; i<length; i++) {
      d1[i] = 1;
    }
    LoMat_double m1(d1, LoMatShape(length,1), blitz::neverDeleteData);
    Vells v1 (&m1);
    Vells v3(double(10));
    Vells v2;
    Timer tim;
    for (i=0; i<nr; i++) {
      v2 = v1 + v1 + v1 + v3 + v1 + v3 + v1 + v3 + v1 + v1;
    }
    tim.show ("Meq  ");
    delete [] d1;
  }
  {
    Double* d1 = new Double[length];
    for (i=0; i<length; i++) {
      d1[i] = 1;
    }
    LoMat_double v1(d1, LoMatShape(length,1), blitz::neverDeleteData);
    LoMat_double v2(LoMatShape(length,1));
    double v3 = 10;
    Timer tim;
    for (i=0; i<nr; i++) {
      v2 = v1 + v1 + v1 + v3 + v1 + v3 + v1 + v3 + v1 + v1;
    }
    tim.show ("Blitz");
    delete [] d1;
  }
  {
    Array<Double> v1(IPosition(1,length));
    Array<Double> v2(IPosition(1,length));
    v1.set (1);
    double v3 = 10;
    Timer tim;
    for (i=0; i<nr; i++) {
      v2 = v1 + v1 + v1 + v3 + v1 + v3 + v1 + v3 + v1 + v1;
    }
    tim.show ("Array");
  }
}


int main (int argc, char** argv)
{
  uInt nr = 100;
  if (argc > 1) {
    istrstream istr(argv[1]);
    istr >> nr;
  }
  try {
    doIt();
    if (nr > 0) {
      doIt2 (1, nr);
      doIt2 (8, nr);
      doIt2 (128, nr);
      doIt2 (12800, nr/10);
    }
  } catch (AipsError x) {
    cout << "Caught an exception: " << x.getMesg() << endl;
    return 1;
  }
  cout << "MeqMat " << VellsRep::nctor << ' ' << VellsRep::ndtor
       << ' ' << VellsRep::nctor + VellsRep::ndtor << endl;
  cout << "OK" << endl;
  return 0;
}
