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
#include <casa/Arrays/Matrix.h>
#include <casa/Arrays/ArrayMath.h>
#include <casa/BasicSL/Complex.h>
#include <casa/OS/Timer.h>
#include <casa/Exceptions/Error.h>
#include <casa/iostream.h>
#include <sstream>

using namespace LOFAR;
using namespace Meq;
using namespace Meq::VellsMath;


void showDouble (const Vells & v)
{
  cout << v << endl;
}
void showDComplex (const Vells & v)
{
  cout << v << endl;
}

void doIt()
{
  Double d1[] = {1,2,3,4,5,6};
  Double d2[] = {2,3,4,5,6,7};
  LoMat_double m1(d1, LoMatShape(2,3), blitz::neverDeleteData);
  LoMat_double m2(d2, LoMatShape(2,3), blitz::neverDeleteData);
  Vells v1(m1);
  Vells v2(m2);
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
  Vells vc1 (mc1);
  Vells vc2 = v1 + v2 + vc1;
  Vells vc3 = v1 + vc1 + v2;
  Vells vc4 = vc1 + vc2;
  Vells vc5 = (v1 - vc1) * vc2;
  Vells vc6 = (vc2 - vc1) * v2;
  Vells vc7 = (vc2 - vc1) * vc2;
}

void doIt2 (uInt length, uInt nr)
{
  Double * ref;
  uInt i;
  {
    Double* d1 = new Double[length];
    Double* r  = ref = new Double[length];
    for (i=0; i<length; i++) {
      d1[i] = 1;
    }
    double v3 = 10;
    Timer tim;
    for (i=0; i<nr; i++) {
      for(uInt j=0; j<length; j++) {
	      r[j] = d1[j] + d1[j] + d1[j] + v3 + d1[j] + v3 + d1[j] + v3 + d1[j] + d1[j];
      }
    }
    tim.show ("C[]  ");
    delete [] d1;
  }
  {
    Double* d1 = new Double[length],*d1i;
    Double* r  = new Double[length],*ri,*rend = r+length;
    for (i=0; i<length; i++) {
      d1[i] = 1;
    }
    double v3 = 10;
    Timer tim;
    for (i=0; i<nr; i++) {
      for( d1i=d1, ri=r; ri < rend; d1i++,ri++ )
	      *ri = *d1i + *d1i + *d1i + v3 + *d1i + v3 + *d1i + v3 + *d1i + *d1i;
    }
    tim.show ("C*   ");
    delete [] d1;
    Assert(memcmp(r,ref,sizeof(Double)*length)==0);
    delete [] r;
  }
  {
    Vells v1(1.0,length,1,true);
    Vells v3(double(10));
    Vells v2;
    Timer tim;
    for (i=0; i<nr; i++) {
      v2 = v1 + v1 + v1 + v3 + v1 + v3 + v1 + v3 + v1 + v1;
    }
    tim.show ("Meq  ");
    Assert(memcmp(v2.getStorage<double>(),ref,sizeof(Double)*length)==0);
  }
  {
    Vells v1(1.0,length,1,true);
    Vells v3(double(10));
    Vells v2(0.0,length,1,false);
    Timer tim;
    for (i=0; i<nr; i++) {
      v2.as<LoMat_double>() = 
         v1.as<LoMat_double>() + v1.as<LoMat_double>() + v1.as<LoMat_double>() +
         v3.as<double>() + v1.as<LoMat_double>() + v3.as<double>() +
         v1.as<LoMat_double>() + v3.as<double>() + v1.as<LoMat_double>() +
         v1.as<LoMat_double>();
    }
    tim.show ("Meq/B");
    Assert(memcmp(v2.getStorage<double>(),ref,sizeof(Double)*length)==0);
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
    Assert(memcmp(v2.data(),ref,sizeof(Double)*length)==0);
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
    Assert(memcmp(&v2(IPosition(1,0)),ref,sizeof(Double)*length)==0);
  }
}


int main (int argc, char** argv)
{
  uInt nr = 100;
  if (argc > 1) {
    std::istringstream istr(argv[1]);
    istr >> nr;
  }
  try {
    doIt();
    if (nr > 0) {
      doIt2 (1, nr);
      doIt2 (8, nr);
      doIt2 (128, nr);
      doIt2 (12800, nr/10);
      doIt2 (128000, nr/10);
    }
  } catch (std::exception &x) {
    cout << "Caught an exception: " << x.what() << endl;
    return 1;
  }
//   cout << "MeqMat " << Vells::nctor << ' ' << Vells::ndtor
//        << ' ' << Vells::nctor + Vells::ndtor << endl;
  cout << "OK" << endl;
  return 0;
}
