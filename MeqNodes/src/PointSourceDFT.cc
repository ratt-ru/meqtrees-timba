//# PointSourceDFT.cc: The point source DFT component for a station
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

#include <MeqNodes/PointSourceDFT.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <casa/BasicSL/Constants.h>

namespace Meq {    

using namespace VellsMath;

const HIID child_labels[] = { AidSt|AidDFT|1,AidSt|AidDFT|2,AidN };
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);

PointSourceDFT::PointSourceDFT()
: CompoundFunction(num_children,child_labels)
{}

PointSourceDFT::~PointSourceDFT()
{}

void PointSourceDFT::evalResult (std::vector<Vells> &res,
				 const std::vector<const Vells*> &values,
				 const Cells &cells)
{
  // Assume that frequency is the first axis.
  Assert(Axis::FREQ==0);
  // for now, only work with 1 frequency segment (2 values from each station's DFT)
  int nval = values.size();
  Assert(nval == 5);
  #define vs1f0 (*values[0])
  #define vs1df (*values[1])
  #define vs2f0 (*values[2])
  #define vs2df (*values[3])
  #define vn    (*values[4])
  // output is a single value
  #define vres  (res[0])
  
  // It is tried to compute the DFT as efficient as possible.
  // Therefore the baseline contribution is split into its antenna parts.
  // dft = exp(2i.pi(ul+vm+wn)) / n                 (with u,v,w in wavelengths)
  //     = (exp(2i.pi((u1.l+v1.m+w1.n) - (u2.l+v2.m+w2.n))/wvl))/n (u,v,w in m)
  //     = ((exp(i(u1.l+v1.m+w1.n)) / exp(i(u2.l+v2.m+w2.m))) ^ (2.pi/wvl)) / n
  // So left and right return the exp values independent of wavelength.
  // Thereafter they are scaled to the freq domain by raising the values
  // for each time to the appropriate powers.
  // Alas the rule
  //   x^(a*b) = (x^a)^b
  // which is valid for real numbers, is only valid for complex numbers
  // if b is an integer number.
  // Therefore the station calculations (in MeqStatSources) are done as
  // follows, where it should be noted that the frequencies are regularly
  // strided.
  //  f = f0 + k.df   (k = 0 ... nchan-1)
  //  s1 = (u1.l+v1.m+w1.n).2i.pi/c
  //  s2 = (u2.l+v2.m+w2.n).2i.pi/c
  //  dft = exp(s1(f0+k.df)) / exp(s2(f0+k.df)) / n
  //      = (exp(s1.f0)/exp(s2.f0)) . (exp(s1.k.df)/exp(s2.k.df)) / n
  //      = (exp(s1.f0)/exp(s2.f0)) . (exp(s1.df)/exp(s2.df))^k / n
  // In principle the power is expensive, but because the frequencies are
  // regularly strided, it is possible to use multiplication.
  // So it gets
  // dft(f0) = (exp(s1.f0)/exp(s2.f0)) / n
  // dft(fj) = dft(fj-1) * (exp(s1.df)/exp(s2.df))
  // Using a python script (tuvw.py) is is checked that this way of
  // calculation is accurate enough.
  // Another optimization can be achieved in the division of the two
  // complex numbers which can be turned into a cheaper multiplication.
  //  exp(x)/exp(y) = (cos(x) + i.sin(x)) / (cos(y) + i.sin(y))
  //                = (cos(x) + i.sin(x)) * (cos(y) - i.sin(y))

  const complex<double>* tmpl = vs1f0.complexStorage();
  const complex<double>* tmpr = vs2f0.complexStorage();
  const complex<double>* deltal = vs1df.complexStorage();
  const complex<double>* deltar = vs2df.complexStorage();
  const double* tmpnk = vn.realStorage();

  vres = Vells(dcomplex(0),res_shape,false);
  dcomplex* resdata = vres.complexStorage();

  // vn can be a scalar or an array (in time axis), so set its step to 0
  // if it is a scalar.
  int stepnk = (vn.shape(Axis::TIME) > 1  ?  1 : 0);
  int stepv  = (vs1f0.shape(Axis::TIME) > 1  ?  1 : 0);
  Assert(vs1f0.shape(Axis::TIME) == vs2f0.shape(Axis::TIME)  &&
	 vs1f0.shape(Axis::TIME) == vs1df.shape(Axis::TIME)  &&
	 vs1f0.shape(Axis::TIME) == vs2df.shape(Axis::TIME) );
  for (int i=0; i<ntime; i++) {
    dcomplex val0 = *tmpr * conj(*tmpl) / *tmpnk;
    *resdata++ = val0;
    if (nfreq > 1) {
      dcomplex dval = *deltar * conj(*deltal);
      for (int j=1; j<nfreq; j++) {
        val0 *= dval;
        *resdata++ = val0;
      }
    }
    tmpnk  += stepnk;
    tmpl   += stepv;
    tmpr   += stepv;
    deltal += stepv;
    deltar += stepv;
  }
}

int PointSourceDFT::getResult (Result::Ref &resref, 
                               const std::vector<Result::Ref> &childres,
                               const Request &request, bool newreq)
{
  const int expect_nvs[]        = {2,2,1};
  const int expect_integrated[] = {-1,-1,0};
  
  // Check that child results are all OK (no fails, expected # of vellsets per child)
  Assert(int(childres.size()) == num_children);
  vector<const VellSet *> child_vs(5);
  if( checkChildResults(resref,child_vs,childres,expect_nvs,
        expect_integrated) == RES_FAIL )
    return RES_FAIL;
  
  // allocate proper output result (integrated=false??)
  const Cells &cells = childres[0]->cells();
  Assert(cells.isDefined(Axis::FREQ) && cells.isDefined(Axis::TIME));
  Result &result = resref <<= new Result(1);
  result.setCells(cells);

  // result is variable in time and frequency
  nfreq = cells.ncells(Axis::FREQ);
  ntime = cells.ncells(Axis::TIME);
  res_shape = Axis::freqTimeMatrix(nfreq,ntime);
  
  // fill it
  computeValues(resref(),child_vs);
  
  return 0;
}

} // namespace Meq
