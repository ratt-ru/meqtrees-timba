//# Polc.cc: Polynomial coefficients
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

#include <Common/Profiling/PerfProfile.h>

#include <MEQ/Polc.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Vells.h>
#include <MEQ/MeqVocabulary.h>
#include <Common/Debug.h>
#include <aips/Arrays/Matrix.h>
#include <Common/lofar_vector.h>
#include <cstdlib>
#include <cmath>

namespace Meq {

//##ModelId=3F86886F0357
double Polc::theirPascal[10][10];
//##ModelId=3F86886F035E
bool   Polc::theirPascalFilled = false;


//##ModelId=3F86886F0366
Polc::Polc()
: itsNrSpid     (0),
  itsPertValue  (1e-6),
  itsFreq0      (0),
  itsTime0      (0),
  itsFreqScale  (1),
  itsTimeScale  (1)
{}

//##ModelId=400E5354033A
Polc::Polc (DataRecord &rec)
: itsCoeff(rec[FVellSets].as_wp<DataArray>())
{
  itsDomain    = rec[FDomain].as<Domain>();
  itsPertValue = rec[FPerturbedValues];
  itsFreq0     = rec[FFreq0];
  itsTime0     = rec[FTime0];
  itsFreqScale = rec[FFreqScale];
  itsTimeScale = rec[FTimeScale];
}

//##ModelId=400E53540345
void Polc::fillRecord (DataRecord &rec) 
{
  rec[FDomain] <<= new Domain(domain());
  rec[FVellSets] <<= &(itsCoeff.getDataArray());
  rec[FPerturbedValues] = itsPertValue;
  rec[FMask] = itsMask;
  rec[FFreq0] = itsFreq0;
  rec[FTime0] = itsTime0;
  rec[FFreqScale] = itsFreqScale;
  rec[FTimeScale] = itsTimeScale;
}

//##ModelId=3F86886F0373
void Polc::setCoeff (const Vells& values)
{
  itsCoeff = values.clone();
  itsMask.resize (values.nelements());
  for (int i=0; i<values.nelements(); i++) {
    itsMask[i] = true;
  }
  clearSolvable();
}

//##ModelId=3F86886F037A
void Polc::setCoeff (const Vells& values,
		     const Matrix<bool>& mask)
{
  Assert (values.nx()==mask.shape()(0) && values.ny()==mask.shape()(1));
  itsCoeff = values.clone();
  itsMask.resize (values.nelements());
  bool deleteM;
  const bool* mdata = mask.getStorage(deleteM);
  for (unsigned int i=0; i<mask.nelements(); i++) {
    itsMask[i] = mdata[i];
  }
  mask.freeStorage (mdata, deleteM);
  clearSolvable();
}

//##ModelId=3F86886F0384
void Polc::setCoeffOnly (const Vells& values)
{
  itsCoeff = values.clone();
  clearSolvable();
}

//##ModelId=400E53540350
void Polc::evaluate (VellSet &result, const Request& request)
{
  PERFPROFILE(__PRETTY_FUNCTION__);
  // Find if perturbed values are to be calculated.
  bool makeDiff = itsNrSpid > 0  &&  request.calcDeriv();
  if (makeDiff) {
    result.setSpids (itsSpids);
  }
  // It is not checked if the domain is valid.
  // In that way any value can be used for the default domain [-1,1].
  // Because the values are calculated for the center of each cell,
  // it is only checked if the centers are in the polc domain.
  const Cells& cells = request.cells();
  const Domain& domain = cells.domain();
  //Assert (domain.startFreq() + request.stepX()/2 >= itsDomain.startFreq());
  //Assert (domain.startTime() + request.stepY()/2 >= itsDomain.startTime());
  //Assert (domain.endX() - request.stepX()/2 <= itsDomain.endX());
  //Assert (domain.endY() - request.stepY()/2 <= itsDomain.endY());
  
  // If there is only one coefficient, the polynomial is independent
  // of x and y.
  // So set the value to the coefficient and possibly set the perturbed value.
  // Make sure it is turned into a scalar value.
  if (itsCoeff.nelements() == 1) {
    LoMat_double& matv = result.setReal (1, 1);
    matv(0,0) = itsCoeff.realStorage()[0];
    if (makeDiff) {
      result.setPerturbedValue (0,
				Vells(*itsCoeff.realStorage() + itsPertValue));
      result.setPerturbation (0, itsPertValue);
// 	cout << "polc " << itsSpidInx[0] << ' ' << result.getValue()
// 	     << result.getPerturbedValue(itsSpidInx[0]) << itsPerturbation
// 	     << ' ' << itsCoeff << endl;
    }
  } else {
    // The polynomial has multiple coefficients.
    // Get the step and start values in the normalized domain.
    double stepx = cells.stepFreq() / itsFreqScale;
    double stx = (domain.startFreq() - itsFreq0) / itsFreqScale + stepx * .5;
    // Get number of steps and coefficients in x (freq) and y (time).
    int ndx = cells.nfreq();
    int ndy = cells.ntime();
    int ncx = itsCoeff.nx();
    int ncy = itsCoeff.ny();
    // Evaluate the expression (as double).
    const double* coeffData = itsCoeff.realStorage();
    const double* pertData = 0;
    double* pertValPtr[100];
    if (makeDiff) {
      pertData = itsPerturbation.realStorage();
      // Create the matrix for each perturbed value.
      // Keep a pointer to the internal matrix data.
      for (unsigned int i=0; i<itsSpidInx.size(); i++) {
	if (itsSpidInx[i] >= 0) {
	  Vells vells(0., ndx, ndy, true);
	  result.setPerturbedValue (itsSpidInx[i], vells);
	  pertValPtr[i] = vells.realStorage();
	}
      }
    }
    // Create matrix for the value itself and keep a pointer to its data.
    LoMat_double& matv = result.setReal (ndx, ndy);
    matv = 0;
    double* value = matv.data();
    // Iterate over all cells in the domain.
    for (int j=0; j<ndy; j++) {
      double valy = (cells.time(j) - itsTime0) / itsTimeScale;
      double valx = stx;
      for (int i=0; i<ndx; i++) {
	const double* coeff = coeffData;
	const double* pert  = pertData;
	double total = 0;
	if (ncx == 1) {
	  // Only 1 coefficient in X, it is independent of x.
	  // So only calculate for the Y values in the most efficient way.
	  total = coeff[ncy-1];
	  for (int iy=ncy-2; iy>=0; iy--) {
	    total *= valy;
	    total += coeff[iy];
	  }
	  if (makeDiff) {
	    double powy = 1;
	    for (int iy=0; iy<ncy; iy++) {
	      if (pertValPtr[iy]) {
		*(pertValPtr[iy]) = total + pert[iy] * powy;
		pertValPtr[iy]++;
	      }
	      powy *= valy;
	    }
	  }
	} else {
	  double powy = 1;
	  for (int iy=0; iy<ncy; iy++) {
	    double tmp = coeff[ncx-1];
	    for (int ix=ncx-2; ix>=0; ix--) {
	      tmp *= valx;
	      tmp += coeff[ix];
	    }
	    total += tmp * powy;
	    powy *= valy;
	    coeff += ncx;
	  }
	  if (makeDiff) {
	    double powersx[10];
	    double powx = 1;
	    for (int ix=0; ix<ncx; ix++) {
	      powersx[ix] = powx;
	      powx *= valx;
	    }
	    double powy = 1;
	    int ik = 0;
	    for (int iy=0; iy<ncy; iy++) {
	      for (int ix=0; ix<ncx; ix++) {
		if (pertValPtr[ik]) {
		  *(pertValPtr[ik]) = total + pert[ik] * powersx[ix] * powy;
		  pertValPtr[ik]++;
		}
		ik++;
	      }
	      powy *= valy;
	    }
	  }
	}
	*value++ = total;
	valx += stepx;
      }
    }
    // Set the perturbations.
    if (makeDiff) {
      const double* pert  = itsPerturbation.realStorage();
      for (unsigned int i=0; i<itsSpidInx.size(); i++) {
	if (itsSpidInx[i] >= 0) {
	  result.setPerturbation (itsSpidInx[i], pert[i]);
	}
      }
    }
  }
}

//##ModelId=3F86886F03A6
int Polc::makeSolvable (int spidIndex)
{
  Assert (itsSpidInx.size() == 0);
  itsSpidInx.resize (itsCoeff.nelements());
  itsSpids.reserve (itsCoeff.nelements());
  itsNrSpid = 0;
  for (int i=0; i<itsCoeff.nelements(); i++) {
    if (itsMask[i]) {
      itsSpidInx[i] = itsNrSpid++;
      itsSpids.push_back (spidIndex++);
    } else {
      itsSpidInx[i] = -1;
    }
  }
  // Precalculate the perturbed coefficients.
  // The perturbation is absolute.
  // If the coefficient is too small, take absolute.
  if (itsNrSpid > 0) {
    itsPerturbation = itsCoeff.clone();
    const double* coeff = itsCoeff.realStorage();
    double* pert  = itsPerturbation.realStorage();
    int i=0;
    for (int ix=0; ix<itsCoeff.nx(); ix++) {
      for (int iy=0; iy<itsCoeff.ny(); iy++) {
	double perturbation = itsPertValue;
	pert[i++] = perturbation;
      }
    }
  }
  return itsNrSpid;
}

//##ModelId=3F86886F03A4
void Polc::clearSolvable()
{
  itsSpidInx.resize (0);
  itsSpids.resize (0);
  itsNrSpid       = 0;
  itsPerturbation = Vells();
}

//##ModelId=3F86886F03AC
void Polc::getInitial (Vells& values) const
{
  double* data = values.realStorage();
  const double* coeff = itsCoeff.realStorage();
  for (unsigned int i=0; i<itsSpidInx.size(); i++) {
    if (itsSpidInx[i] >= 0) {
      Assert (itsSpidInx[i] < values.nx());
      data[itsSpidInx[i]] = coeff[i];
    }
  }
}

//##ModelId=3F86886F03B3
void Polc::getCurrentValue (Vells& value, bool denorm) const
{
  value = itsCoeff;
}

//##ModelId=3F86886F03BE
uint Polc::update (const double* values, uint nrval)
{
  double* coeff = itsCoeff.realStorage();
  uint inx=0;
  for (unsigned int i=0; i<itsSpidInx.size(); i++) {
    if (itsSpidInx[i] >= 0) {
      Assert (inx < nrval);
      coeff[i] += values[inx++];
    }
  }
  return inx;
}


//##ModelId=3F8688700008
Vells Polc::normalize (const Vells& coeff, const Domain& domain)
{
  return normDouble (coeff,
		     domain.scaleFreq(), domain.scaleTime(),
		     domain.offsetFreq()-itsFreq0,
		     domain.offsetTime()-itsTime0);
}
  
//##ModelId=3F8688700011
Vells Polc::denormalize (const Vells& coeff) const
{
  return normDouble (coeff,
		     1/itsDomain.scaleFreq(), 1/itsDomain.scaleTime(),
		     (itsFreq0-itsDomain.offsetFreq())/itsDomain.scaleFreq(),
		     (itsTime0-itsDomain.offsetTime())/itsDomain.scaleTime());
}
  
//##ModelId=3F868870002F
void Polc::fillPascal()
{
  for (int j=0; j<10; j++) {
    theirPascal[j][0] = 1;
    for (int i=1; i<=j; i++) {
      theirPascal[j][i] = theirPascal[j-1][i-1] + theirPascal[j-1][i];
    }
  }
  theirPascalFilled = true;
}

//##ModelId=3F8688700019
Vells Polc::normDouble (const Vells& coeff, double sx,
			double sy, double ox, double oy)
{
  // Fill Pascal's triangle if not done yet.
  if (!theirPascalFilled) {
    fillPascal();
  }
  int nx = coeff.nx();
  int ny = coeff.ny();
  const double* pcold = coeff.realStorage();
  // Create vectors holding the powers of the scale and offset values.
  vector<double> sxp(nx);
  vector<double> syp(ny);
  vector<double> oxp(nx);
  vector<double> oyp(ny);
  sxp[0] = 1;
  oxp[0] = 1;
  for (int i=1; i<nx; i++) {
    sxp[i] = sxp[i-1] * sx;
    oxp[i] = oxp[i-1] * ox;
  }
  syp[0] = 1;
  oyp[0] = 1;
  for (int i=1; i<ny; i++) {
    syp[i] = syp[i-1] * sy;
    oyp[i] = oyp[i-1] * oy;
  }
  // Create the new coefficient matrix.
  // Create a vector to hold the terms of (sy+oy)^j
  Vells newc (double(0), nx, ny, true);
  double* pcnew = newc.realStorage();
  vector<double> psyp(ny);
  // Loop through all coefficients in the y direction.
  for (int j=0; j<ny; j++) {
    // Precalculate the terms of (sy+oy)^j
    for (int k=0; k<=j; k++) {
      psyp[k] = oyp[j-k] * syp[k] * theirPascal[j][k];
    }
    // Loop through all coefficients in the x direction.
    for (int i=0; i<nx; i++) {
      // Get original coefficient.
      double f = *pcold++;
      // Calculate all terms of (sx+ox)^i
      for (int k1=0; k1<=i; k1++) {
	double c = oxp[i-k1] * sxp[k1] * theirPascal[i][k1] * f;
	// Multiply each term with the precalculated terms of (sy+oy)^j
	// and add the result to the appropriate new coefficient.
	for (int k2=0; k2<=j; k2++) {
	  pcnew[k1 + k2*nx] += c * psyp[k2];
	}
      }
    }
  }
  return newc;
}

} // namespace Meq
