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

#include <DMI/DataRecord.h>
#include <MEQ/Polc.h>
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Vells.h>
#include <MEQ/MeqVocabulary.h>
#include <Common/Debug.h>
#include <casa/Arrays/Matrix.h>
#include <Common/lofar_vector.h>
#include <cstdlib>
#include <cmath>

namespace Meq {

//##ModelId=3F86886F0357
double Polc::theirPascal[10][10];
//##ModelId=3F86886F035E
bool   Polc::theirPascalFilled = false;

static NestableContainer::Register reg(TpMeqPolc,True);

static Domain nullDomain;

Polc::Polc()
    : itsDomain(&nullDomain),itsNrSpid(0)
{ 
  itsPertValue = defaultPolcPerturbation; 
  itsWeight = defaultPolcWeight;
  itsId = -1;
}

//##ModelId=3F86886F0366
Polc::Polc(double c00,double freq0,double freqsc,double time0,double timesc,
            double pert,double weight,DbId id)
  : itsCoeff(c00),itsDomain(&nullDomain),itsNrSpid(0)
{
  DataRecord::replace(FCoeff,&itsCoeff.getDataArray(),DMI::WRITE);
  setEverything(freq0,freqsc,time0,timesc,pert,weight,id);
}

Polc::Polc(LoMat_double arr,double freq0,double freqsc,double time0,double timesc,
            double pert,double weight,DbId id)
  : itsCoeff(arr),itsDomain(&nullDomain),itsNrSpid(0)
{
  DataRecord::replace(FCoeff,&itsCoeff.getDataArray(),DMI::WRITE);
  setEverything(freq0,freqsc,time0,timesc,pert,weight,id);
}

Polc::Polc(DataArray *parr,double freq0,double freqsc,double time0,double timesc,
            double pert,double weight,DbId id)
  : itsCoeff(parr),itsDomain(&nullDomain),itsNrSpid(0)
{
  DataRecord::replace(FCoeff,&itsCoeff.getDataArray(),DMI::WRITE);
  setEverything(freq0,freqsc,time0,timesc,pert,weight,id);
}

Polc::Polc(const Vells &coeff,double freq0,double freqsc,double time0,double timesc,
            double pert,double weight,DbId id)
  : itsDomain(&nullDomain),itsNrSpid(0)
{
  itsCoeff = coeff.clone();
  DataRecord::replace(FCoeff,&itsCoeff.getDataArray(),DMI::WRITE);
  setEverything(freq0,freqsc,time0,timesc,pert,weight,id);
}

void Polc::setEverything (double freq0,double freqsc,double time0,double timesc,
                          double pert,double weight,DbId id)
{
  DataRecord::replace(FCoeff,&itsCoeff.getDataArray(),DMI::WRITE);
  (*this)[FPerturbation] = itsPertValue = pert;
  (*this)[FFreq0] = itsFreq0 = freq0;
  (*this)[FTime0] = itsTime0 = time0;
  (*this)[FFreqScale] = itsFreqScale = freqsc;
  (*this)[FTimeScale] = itsTimeScale = timesc;
  (*this)[FWeight] = itsWeight = weight;
  (*this)[FDbId] = itsId = id;
}


//##ModelId=400E5354033A
Polc::Polc (const DataRecord &other,int flags,int depth)
  : DataRecord(other,flags,depth),itsDomain(&nullDomain),itsNrSpid(0)
{
  validateContent();
}

void Polc::privatize (int flags,int depth)
{
  if( flags&DMI::DEEP || depth>0 )
    itsCoeff = Vells();
  DataRecord::privatize(flags,depth);
}

  
void Polc::validateContent ()    
{
  Thread::Mutex::Lock lock(mutex());
  // ensure that our record contains all the right fields; setup shortcuts
  // to their contents
  try
  {
    if( DataRecord::hasField(FDomain) ) // verify cells field
      itsDomain = (*this)[FDomain].as_p<Domain>();
    else
      itsDomain = &nullDomain;
    // get vellsets field
    if( DataRecord::hasField(FCoeff) )
      itsCoeff = Vells((*this)[FCoeff].ref());
    else
      itsCoeff = Vells();
    // get various others
    itsPertValue = (*this)[FPerturbation].as<double>(defaultPolcPerturbation);
    itsFreq0     = (*this)[FFreq0].as<double>(0);
    itsTime0     = (*this)[FTime0].as<double>(0);
    itsFreqScale = (*this)[FFreqScale].as<double>(1);
    itsTimeScale = (*this)[FTimeScale].as<double>(1);
    itsWeight    = (*this)[FWeight].as<double>(defaultPolcWeight);
    itsId        = (*this)[FDbId].as<int>(-1);
  }
  catch( std::exception &err )
  {
    Throw(string("validate of Polc record failed: ") + err.what());
  }
  catch( ... )
  {
    Throw("validate of Polc record failed with unknown exception");
  }
}

void Polc::setDomain (const Domain& domain)
{
  (*this)[FDomain].replace() <<= new Domain(domain);
  itsDomain = (*this)[FDomain].as_p<Domain>();
}

void Polc::setPerturbation (double perturbation)
{ (*this)[FPerturbation] = itsPertValue = perturbation; }

void Polc::setWeight (double weight)
{ (*this)[FWeight] = itsWeight = weight; }

void Polc::setDbId (Polc::DbId id)
{ (*this)[FDbId] = itsId = id; }

void Polc::setFreq0 (double freq0)
{ (*this)[FFreq0] = itsFreq0 = freq0; }

void Polc::setTime0 (double time0)
{ (*this)[FTime0] = itsTime0 = time0; }

void Polc::setFreqScale (double freqScale)
{ (*this)[FFreqScale] = itsFreqScale = freqScale; }

void Polc::setTimeScale (double timeScale)
{ (*this)[FTimeScale] = itsTimeScale = timeScale; }

//##ModelId=3F86886F0373
void Polc::setCoeff (const Vells& values)
{
  Thread::Mutex::Lock lock(mutex());
  // note that record contains a separate Vells object, but internally
  // they will reference the same DataArray
  itsCoeff = values.clone();
  DataRecord::replace(FCoeff,&itsCoeff.getDataArray(),DMI::WRITE);
  clearSolvable();
}

//##ModelId=400E53540350
void Polc::evaluate (VellSet &result,const Request& request) const
{
  PERFPROFILE(__PRETTY_FUNCTION__);
  const Cells& cells = request.cells();
  evaluate(result,cells.center(0),cells.center(1),request.calcDeriv());
}

//##ModelId=400E53540350
void Polc::evaluate (VellSet &result,
    const LoVec_double &xgrid,const LoVec_double &ygrid,int makeDiff) const
{
  PERFPROFILE(__PRETTY_FUNCTION__);
  // Find if perturbed values are to be calculated.
  if( itsNrSpid <= 0 ) // no active solvable spids? Force no perturbations then
    makeDiff = 0;
  else if( makeDiff ) 
    result.setSpids(itsSpids);
  result.setShape(xgrid.size(),ygrid.size());
  // If there is only one coefficient, the polynomial is independent
  // of x and y.
  // So set the value to the coefficient and possibly set the perturbed value.
  // Make sure it is turned into a scalar value.
  if( itsCoeff.nelements() == 1 ) 
  {
    double c00 = itsCoeff.realStorage()[0];
    result.setValue(new Vells(c00,false));
    double d = itsPertValue;
    for( int ipert=0; ipert<makeDiff; ipert++,d=-d )
    {
      result.setPerturbedValue(0,new Vells(c00+d,false),ipert);
      result.setPerturbation(0,d,ipert);
    }
  }
  else 
  {
    // The polynomial has multiple coefficients.
    // Get number of steps and coefficients in x (freq) and y (time);
    int ndx = xgrid.extent(0);
    int ndy = ygrid.extent(0);
    int ncx = itsCoeff.nx();
    int ncy = itsCoeff.ny();
    // Get normalized values
    LoVec_double vecx(ndx),vecy(ndy);
    vecx = (xgrid - itsFreq0) / itsFreqScale;
    vecy = (ygrid - itsTime0) / itsTimeScale;
    // Evaluate the expression (as double).
    const double* coeffData = itsCoeff.realStorage();
    double* pertValPtr[MaxNumPerts][100];
    for( int ipert=0; ipert<makeDiff; ipert++ )
    {
      // Create the matrix for each perturbed value.
      // Keep a pointer to the internal matrix data.
      for( uint i=0; i<itsSpidInx.size(); i++) 
        if( itsSpidInx[i] >= 0 )
          pertValPtr[ipert][i] = 
              result.setPerturbedValue(itsSpidInx[i],new Vells(0.,ndx,ndy,true),ipert)
                    .realStorage();
        else
          pertValPtr[ipert][i] = 0;
    }
    // Create matrix for the value itself and keep a pointer to its data.
    LoMat_double& matv = result.setReal (ndx, ndy);
    matv = 0;
    double* value = matv.data();
    // Iterate over all cells in the domain.
    for (int j=0; j<ndy; j++) 
    {
      double valy = vecy(j);
      for (int i=0; i<ndx; i++) 
      {
        double valx = vecx(i);
        const double* coeff = coeffData;
        double total = 0;
        // Only 1 coefficient in X, it is independent of x.
        // So only calculate for the Y values in the most efficient way.
        if (ncx == 1) 
        {
          total = coeff[ncy-1];
          for (int iy=ncy-2; iy>=0; iy--) {
            total *= valy;
            total += coeff[iy];
          }
          if( makeDiff ) {
            double powy = 1;
            for (int iy=0; iy<ncy; iy++) {
              double d = itsPerturbation[iy] * powy;
              for( int ipert=0; ipert<makeDiff; ipert++,d=-d ) {
                if (pertValPtr[ipert][iy]) {
                  *(pertValPtr[ipert][iy]) = total + d;
                  pertValPtr[ipert][iy]++;
                }
              }
              powy *= valy;
            }
          }
        } 
        else // multiple coeffs in X
        {
          double powy = 1;
          for (int iy=0; iy<ncy; iy++) 
          {
            double tmp = coeff[ncx-1];
            for (int ix=ncx-2; ix>=0; ix--) 
            {
              tmp *= valx;
              tmp += coeff[ix];
            }
            total += tmp * powy;
            powy *= valy;
            coeff += ncx;
          }
          if( makeDiff ) 
          {
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
                double d = itsPerturbation[ik] * powersx[ix] * powy;
                for( int ipert=0; ipert<makeDiff; ipert++,d=-d ) {
                  if( pertValPtr[ipert][ik] ) {
                    *(pertValPtr[ipert][ik]) = total + d;
                    pertValPtr[ipert][ik]++;
                  }
                }
                ik++;
              }
              powy *= valy;
            }
          }
        }
        *value++ = total;
      } // endfor(i) over cells
    } // endfor(j) over cells
    // Set the perturbations.
    if( makeDiff )
      for (unsigned int i=0; i<itsSpidInx.size(); i++)
        if (itsSpidInx[i] >= 0) 
        {
          result.setPerturbation(itsSpidInx[i],itsPerturbation[i],0);
          if( makeDiff>1 )
            result.setPerturbation(itsSpidInx[i],-itsPerturbation[i],1);
        }
  } // end else (multiple polcs)
}

//##ModelId=3F86886F03A6
int Polc::makeSolvable (int spidIndex)
{
  Assert (itsSpidInx.size() == 0);
  itsSpidInx.resize (itsCoeff.nelements());
  itsSpids.reserve (itsCoeff.nelements());
  itsNrSpid = 0;
  for (int i=0; i<itsCoeff.nelements(); i++) 
  {
    itsSpidInx[i] = itsNrSpid++;
    itsSpids.push_back (spidIndex++);
  }
//   // Precalculate the perturbed coefficients.
//   // The perturbation is absolute.
//   // If the coefficient is too small, take absolute.
  
// for now, go with the trivial and use the same pert value for
// all coefficients. In the future we will be a lot smarter...
  if(itsNrSpid > 0) 
  {
    itsPerturbation.resize(itsCoeff.nelements());
    itsPerturbation.assign(itsCoeff.nelements(),itsPertValue);
  }
//     const double* coeff = itsCoeff.realStorage();
//     int i=0;
//     for (int ix=0; ix<itsCoeff.nx(); ix++) 
//       for (int iy=0; iy<itsCoeff.ny(); iy++) 
//         itsPerturbation[i++] = itsPertValue;
  return itsNrSpid;
}

//##ModelId=3F86886F03A4
void Polc::clearSolvable()
{
  itsNrSpid = 0;
  itsSpidInx.clear();
  itsSpids.clear();
  itsPerturbation.clear();
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
  Thread::Mutex::Lock lock(mutex());
  if( !itsCoeff.isWritable() )
  {
    itsCoeff.privatize(DMI::WRITE|DMI::DEEP);
    DataRecord::replace(FCoeff,&itsCoeff.getDataArray(),DMI::WRITE);
  }
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


// //##ModelId=3F8688700008
// Vells Polc::normalize (const Vells& coeff, const Domain& domain)
// {
//   return normDouble (coeff,
//                      domain.scaleFreq(), domain.scaleTime(),
//                      domain.offsetFreq()-itsFreq0,
//                      domain.offsetTime()-itsTime0);
// }
//   
// //##ModelId=3F8688700011
// Vells Polc::denormalize (const Vells& coeff) const
// {
//   return normDouble (coeff,
//                      1/itsDomain.scaleFreq(), 1/itsDomain.scaleTime(),
//                      (itsFreq0-itsDomain.offsetFreq())/itsDomain.scaleFreq(),
//                      (itsTime0-itsDomain.offsetTime())/itsDomain.scaleTime());
// }
//   
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
