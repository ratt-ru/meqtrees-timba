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

#include "Polc.h"
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Vells.h>
#include <MEQ/MeqVocabulary.h>
#include <Common/Debug.h>
#include <Common/lofar_vector.h>
#include <cstdlib>
#include <cmath>

namespace Meq {

// //##ModelId=3F86886F0357
// double Polc::theirPascal[10][10];
// //##ModelId=3F86886F035E
// bool   Polc::theirPascalFilled = false;



static NestableContainer::Register reg(TpMeqPolc,True);

const int    defaultPolcAxes[maxPolcRank]       = {0,1};
const double defaultPolcOffset[maxPolcRank]     = {0,0};
const double defaultPolcScale[maxPolcRank]      = {1,1};

static std::vector<int> default_axes(defaultPolcAxes,defaultPolcAxes+maxPolcRank);
static std::vector<double> default_offset(defaultPolcOffset,defaultPolcOffset+maxPolcRank);
static std::vector<double> default_scale(defaultPolcScale,defaultPolcScale+maxPolcRank);

Domain Polc::default_domain;


Polc::Polc()
: rank_(-1),nrSpid_(0)
{
  pertValue_ = defaultPolcPerturbation; 
  weight_    = defaultPolcWeight;
  id_        = -1;
}

//##ModelId=3F86886F0366
Polc::Polc(double c00,double pert,double weight,DbId id)
: rank_(-1),nrSpid_(0)
{
  init(0,0,0,0,pert,weight,id);
  setCoeff(c00);
}

Polc::Polc(const LoVec_double &coeff,
           int iaxis,double x0,double xsc,
           double pert,double weight,DbId id)
: rank_(-1),nrSpid_(0)
{
  init(1,&iaxis,&x0,&xsc,pert,weight,id);
  setCoeff(coeff);
}

Polc::Polc(const LoMat_double &coeff,
           const int iaxis[],const double offset[],const double scale[],
           double pert,double weight,DbId id)
: rank_(-1),nrSpid_(0)
{
  init(2,iaxis,offset,scale,pert,weight,id);
  setCoeff(coeff);
}

Polc::Polc(DataArray *pcoeff,
           const int iaxis[],const double offset[],const double scale[],
           double pert,double weight,DbId id)
: rank_(-1),nrSpid_(0)
{
  coeff_ <<= pcoeff;
  FailWhen(pcoeff->elementType() != Tpdouble,"can't create Meq::Polc from this array: not double");
  FailWhen(pcoeff->rank()>maxPolcRank,"can't create Meq::Polc from this array: rank too high");
  int rnk = pcoeff->rank();
  if( rnk == 1 && pcoeff->size() == 1 )
    rnk = 0;
  init(rnk,iaxis,offset,scale,pert,weight,id);
  // if only a single coeff, rank is 0
  DataRecord::replace(FCoeff,pcoeff,DMI::ANONWR);
}

//##ModelId=400E5354033A
Polc::Polc (const DataRecord &other,int flags,int depth)
  : DataRecord(other,flags,depth),nrSpid_(0)
{
  validateContent();
}

// sets all of a polc's axes and attributes in one go
void Polc::init (int rnk,
                 const int iaxis[],
                 const double offset[],
                 const double scale[],
                 double pert,double weight,DbId id)
{
  Thread::Mutex::Lock lock(mutex());
  // this ensures a rank match
  // first time 'round, set the rank
  if( rank() < 0 )
  {
    FailWhen(rnk<0 || rnk>maxPolcRank,"Meq::Polc already initialized with a different rank");
    rank_ = rnk;
    axes_.resize(rnk);
    offsets_.resize(rnk);
    scales_.resize(rnk);
  }
  else // otherwise ensure rank did not change
  {
    FailWhen(rank() != rnk,"Meq::Polc already initialized with a different rank");
  }
  // init fields
  if( rnk )
  {
    // assign defaults
    axes_.assign(iaxis,iaxis+rnk);
    offsets_.assign(offset,offset+rnk);
    scales_.assign(scale,scale+rnk);
    (*this)[FAxisIndex]      = axes_;
    (*this)[FOffset] = offsets_;
    (*this)[FScale]     = scales_;
  }
  (*this)[FPerturbation] = pertValue_ = pert;
  (*this)[FWeight] = weight_ = weight;
  (*this)[FDbId] = id_ = id;
}

void Polc::setDomain (const Domain * domain,int flags)
{
  Thread::Mutex::Lock lock(mutex());
  if( !(flags&(DMI::ANON|DMI::EXTERNAL)) )
  {
    if( domain->refCount() )
      domain_.attach(domain,DMI::READONLY);
    else
      domain_.attach(new Domain(*domain),DMI::ANON|DMI::READONLY);
  }
  else
    domain_.attach(domain,(flags&~DMI::WRITE)|DMI::READONLY);
  (*this)[FDomain] <<= domain_.copy();
}

// sets up an axis of variability
void Polc::setAxis (int i,int iaxis,double offset,double scale)
{
  Thread::Mutex::Lock lock(mutex());
  FailWhen(i<0 || i>=rank(),"illegal Meq::Polc axis");
  (*this)[FAxisIndex][i] = axes_[i] = iaxis;
  (*this)[FOffset][i] = offsets_[i] = offset;
  (*this)[FScale][i] = scales_[i] = scale;
}

void Polc::setPerturbation (double perturbation)
{ (*this)[FPerturbation] = pertValue_ = perturbation; }

void Polc::setWeight (double weight)
{ (*this)[FWeight] = weight_ = weight; }

void Polc::setDbId (Polc::DbId id)
{ (*this)[FDbId] = id_ = id; }


void Polc::setCoeff (double c00)
{
  Thread::Mutex::Lock lock(mutex());
  if( rank()<0 )
    init(0);
  else {
    FailWhen(rank()!=0,"Meq::Polc: coeff rank mismatch");
  }
  LoVec_double coeff(1);
  coeff = c00;
  coeff_ <<= new DataArray(coeff);
  DataRecord::replace(FCoeff,coeff_.dewr_p(),DMI::ANONWR);
}

void Polc::setCoeff (const LoVec_double & coeff)
{
  Thread::Mutex::Lock lock(mutex());
  if( rank()<0 )
    init(1);
  else {
    FailWhen(rank()!=1,"Meq::Polc: coeff rank mismatch");
  }
  coeff_ <<= new DataArray(coeff);
  DataRecord::replace(FCoeff,coeff_.dewr_p(),DMI::ANONWR);
}

void Polc::setCoeff (const LoMat_double & coeff)
{
  Thread::Mutex::Lock lock(mutex());
  if( rank()<0 )
    init(2);
  else {
    FailWhen(rank()!=2,"Meq::Polc: coeff rank mismatch");
  }
  coeff_ <<= new DataArray(coeff);
  DataRecord::replace(FCoeff,coeff_.dewr_p(),DMI::ANONWR);
}

void Polc::privatize (int flags,int depth)
{
  Thread::Mutex::Lock lock(mutex());
  DataRecord::privatize(flags,depth);
}
  
void Polc::validateContent ()    
{
  Thread::Mutex::Lock lock(mutex());
  // ensure that our record contains all the right fields; setup shortcuts
  // to their contents
  try
  {
    rank_ = -1;
    if( DataRecord::hasField(FDomain) ) // verify cells field
      domain_ <<= (*this)[FDomain].as_p<Domain>();
    else
      domain_ <<= new Domain;
    // get coefficients
    if( DataRecord::hasField(FCoeff) )
    {
      coeff_ = DataRecord::field(FCoeff);
      rank_  = coeff_->rank();
      if( rank_ == 1 && coeff_->size() == 1 )
        rank_ = 0;
    }
    else
    {
      coeff_.detach();
      rank_ = -1;
    }
    // get various others
    axes_       = (*this)[FAxisIndex].as_vector(default_axes);
    offsets_    = (*this)[FOffset].as_vector(default_offset);
    scales_     = (*this)[FScale].as_vector(default_scale);
    Assert(axes_.size()>=uint(rank()) && offsets_.size()>=uint(rank()) && 
           scales_.size()>=uint(rank()));
    pertValue_  = (*this)[FPerturbation].as<double>(defaultPolcPerturbation);
    weight_     = (*this)[FWeight].as<double>(defaultPolcWeight);
    id_         = (*this)[FDbId].as<int>(-1);
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
//##ModelId=400E53540350
void Polc::evaluate (VellSet &vs,const Request &request) const
{
  Thread::Mutex::Lock lock(mutex());
  PERFPROFILE(__PRETTY_FUNCTION__);
  const Cells& cells = request.cells();
  evaluate(vs,cells,request.calcDeriv());
}

void Polc::evaluate (VellSet &vs,const Cells &cells,int deriv) const
{
  Thread::Mutex::Lock lock(mutex());
  PERFPROFILE(__PRETTY_FUNCTION__);
  // init shape of result
  Vells::Shape res_shape;
  Axis::degenerateShape(res_shape,cells.rank());
  // Now, check that Cells includes all our axes of variability.
  // If an axis is not defined, then we can only proceed if we have
  // no dependence on that axis (i.e. only one coeff in that direction)
  LoVec_double grid[2];
  const LoShape & coeff_shape = coeff_->shape();
  for( int i=0; i<rank(); i++ )
  {
    if( coeff_shape[i] > 1 )
    {
      int iaxis = axes_[i];
      FailWhen(!cells.isDefined(iaxis),
            "Meq::Polc: axis " + Axis::name(iaxis).toString() + 
            " is not defined in Cells");
      grid[i].resize(cells.ncells(i));
      grid[i] = ( cells.center(iaxis) - offsets_[i] ) * scales_[i];
      res_shape[iaxis] = grid[i].size();
    }
  }
  // now evaluate
  evaluate(vs,res_shape,grid,deriv);
}

//##ModelId=400E53540350
void Polc::evaluate (VellSet &vs,const Vells::Shape &vshape,const LoVec_double grid[],int makeDiff) const
{
  Thread::Mutex::Lock lock(mutex());
  PERFPROFILE(__PRETTY_FUNCTION__);
  // Find if perturbed values are to be calculated.
  if( nrSpid_ <= 0 ) // no active solvable spids? Force no perturbations then
    makeDiff = 0;
  else if( makeDiff ) 
    vs.setSpids(spids_);
  // If there is only one coefficient, the polynomial is independent
  // of x and y.
  // So set the value to the coefficient and possibly set the perturbed value.
  // Make sure it is turned into a scalar value.
  if( coeff_->size() == 1 )
  {
    double c00 = getCoeff0();
    vs.setValue(new Vells(c00,false));
    double d = pertValue_;
    for( int ipert=0; ipert<makeDiff; ipert++,d=-d )
    {
      vs.setPerturbedValue(0,new Vells(c00+d,false),ipert);
      vs.setPerturbation(0,d,ipert);
    }
    return;
  }
  // else check if we're dealing with a 1D poly. Note that a 1xN poly
  // is also treated as 1D; we simply use the second grid array
  const LoShape &cshape = coeff_->shape();
  if( rank() == 1 || cshape[0] == 1 || cshape[1] == 1 ) // evaluate 1D poly
  {
    // determine which grid points to actually use
    LoVec_double grid(cshape[0] > 1 ? grid[0] : grid[1]);
    // Get number of steps and coefficients in x and y 
    int ndx = grid.size();
    int ncx = coeff_->size();
    // Evaluate the expression (as double).
    const double* coeffData = static_cast<const double *>(coeff_->getConstDataPtr());
    double* pertValPtr[MaxNumPerts][spidInx_.size()];
    for( int ipert=0; ipert<makeDiff; ipert++ )
    {
      // Create a vells for each perturbed value.
      // Keep a pointer to its storage
      for( uint i=0; i<spidInx_.size(); i++) 
        if( spidInx_[i] >= 0 )
          pertValPtr[ipert][i] = 
              vs.setPerturbedValue(spidInx_[i],new Vells(0.,vshape,true),ipert)
                    .realStorage();
        else
          pertValPtr[ipert][i] = 0;
    }
    // Create matrix for the main value and keep a pointer to its storage
    double* value = vs.setValue(new Vells(0,vshape,true)).realStorage();
    for( int i=0; i<ndx; i++ )
    {
      double valx = grid(i);
      double total = coeffData[ncx-1];
      for (int j=ncx-2; j>=0; j--) 
      {
        total *= valx;
        total += coeffData[j];
      }
      if( makeDiff ) 
      {
        double powx = 1;
        for (int j=0; j<ncx; j++) 
        {
          double d = perturbation_[j] * powx;
          for( int ipert=0; ipert<makeDiff; ipert++,d=-d ) 
          {
            if (pertValPtr[ipert][j]) 
            {
              *(pertValPtr[ipert][j]) = total + d;
              pertValPtr[ipert][j]++;
            }
          }
          powx *= valx;
        }
      }
      *value++ = total;
    }
    return;
  }
  // OK, at this stage, we're stuck evaluating a truly 2D polynomial
  // Get number of steps and coefficients in x and y 
  int ndx = grid[0].size();
  int ndy = grid[1].size();
  int ncx = cshape[0];
  int ncy = cshape[1];
  // Evaluate the expression (as double).
  const double* coeffData = static_cast<const double *>(coeff_->getConstDataPtr());
  double* pertValPtr[MaxNumPerts][100];
  for( int ipert=0; ipert<makeDiff; ipert++ )
  {
    // Create a vells for each perturbed value.
    // Keep a pointer to its storage
    for( uint i=0; i<spidInx_.size(); i++) 
      if( spidInx_[i] >= 0 )
        pertValPtr[ipert][i] = 
            vs.setPerturbedValue(spidInx_[i],new Vells(0.,vshape,true),ipert)
                  .realStorage();
      else
        pertValPtr[ipert][i] = 0;
  }
  // Create matrix for the main value and keep a pointer to its storage
  double* value = vs.setValue(new Vells(0,vshape,true)).realStorage();
  // Iterate over all cells in the domain.
  for (int j=0; j<ndy; j++) 
  {
    double valy = grid[1](j);
    for (int i=0; i<ndx; i++) 
    {
      double valx = grid[0](i);
      const double* coeff = coeffData;
      double total = 0;
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
            double d = perturbation_[ik] * powersx[ix] * powy;
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
      *value++ = total;
    } // endfor(i) over cells
  } // endfor(j) over cells
  // Set the perturbations.
  if( makeDiff )
    for (unsigned int i=0; i<spidInx_.size(); i++)
      if (spidInx_[i] >= 0) 
      {
        vs.setPerturbation(spidInx_[i],perturbation_[i],0);
        if( makeDiff>1 )
          vs.setPerturbation(spidInx_[i],-perturbation_[i],1);
      }
}

//##ModelId=3F86886F03A6
int Polc::makeSolvable (int spidIndex)
{
  Assert (spidInx_.size() == 0);
  spidInx_.resize(coeff_->size());
  spids_.reserve(coeff_->size());
  nrSpid_ = 0;
  for (int i=0; i<coeff_->size(); i++) 
  {
    spidInx_[i] = nrSpid_++;
    spids_.push_back (spidIndex++);
  }
//   // Precalculate the perturbed coefficients.
//   // The perturbation is absolute.
//   // If the coefficient is too small, take absolute.
  
// for now, go with the trivial and use the same pert value for
// all coefficients. In the future we will be a lot smarter...
  if(nrSpid_ > 0) 
  {
    perturbation_.resize(coeff_->size());
    perturbation_.assign(coeff_->size(),pertValue_);
  }
//     const double* coeff = coeff_.realStorage();
//     int i=0;
//     for (int ix=0; ix<coeff_.nx(); ix++) 
//       for (int iy=0; iy<coeff_.ny(); iy++) 
//         perturbation_[i++] = pertValue_;
  return nrSpid_;
}

//##ModelId=3F86886F03A4
void Polc::clearSolvable()
{
  nrSpid_ = 0;
  spidInx_.clear();
  spids_.clear();
  perturbation_.clear();
}

// //##ModelId=3F86886F03AC
// void Polc::getInitial (Vells& values) const
// {
//   double* data = values.realStorage();
//   const double* coeff = coeff_.datarealStorage();
//   for (unsigned int i=0; i<spidInx_.size(); i++) {
//     if (spidInx_[i] >= 0) {
//       Assert (spidInx_[i] < values.nx());
//       data[spidInx_[i]] = coeff[i];
//     }
//   }
// }
// 
// //##ModelId=3F86886F03B3
// void Polc::getCurrentValue (Vells& value, bool denorm) const
// {
//   value = coeff_;
// }
// 

//##ModelId=3F86886F03BE
uint Polc::update (const double* values, uint nrval)
{
  Thread::Mutex::Lock lock(mutex());
  if( !coeff_.isWritable() )
  {
    coeff_.privatize(DMI::WRITE|DMI::DEEP);
    DataRecord::replace(FCoeff,coeff_.dewr_p(),DMI::WRITE);
  }
  double* coeff = static_cast<double*>(coeff_().getDataPtr());
  uint inx=0;
  for (unsigned int i=0; i<spidInx_.size(); i++) {
    if (spidInx_[i] >= 0) {
      Assert (inx < nrval);
      coeff[i] += values[inx++];
    }
  }
  return inx;
}

// 
// //##ModelId=3F868870002F
// void Polc::fillPascal()
// {
//   for (int j=0; j<10; j++) {
//     theirPascal[j][0] = 1;
//     for (int i=1; i<=j; i++) {
//       theirPascal[j][i] = theirPascal[j-1][i-1] + theirPascal[j-1][i];
//     }
//   }
//   theirPascalFilled = true;
// }
// 
// //##ModelId=3F8688700019
// Vells Polc::normDouble (const Vells& coeff, double sx,
//                         double sy, double ox, double oy)
// {
//   // Fill Pascal's triangle if not done yet.
//   if (!theirPascalFilled) {
//     fillPascal();
//   }
//   int nx = coeff.nx();
//   int ny = coeff.ny();
//   const double* pcold = coeff.realStorage();
//   // Create vectors holding the powers of the scale and offset values.
//   vector<double> sxp(nx);
//   vector<double> syp(ny);
//   vector<double> oxp(nx);
//   vector<double> oyp(ny);
//   sxp[0] = 1;
//   oxp[0] = 1;
//   for (int i=1; i<nx; i++) {
//     sxp[i] = sxp[i-1] * sx;
//     oxp[i] = oxp[i-1] * ox;
//   }
//   syp[0] = 1;
//   oyp[0] = 1;
//   for (int i=1; i<ny; i++) {
//     syp[i] = syp[i-1] * sy;
//     oyp[i] = oyp[i-1] * oy;
//   }
//   // Create the new coefficient matrix.
//   // Create a vector to hold the terms of (sy+oy)^j
//   Vells newc (double(0), nx, ny, true);
//   double* pcnew = newc.realStorage();
//   vector<double> psyp(ny);
//   // Loop through all coefficients in the y direction.
//   for (int j=0; j<ny; j++) {
//     // Precalculate the terms of (sy+oy)^j
//     for (int k=0; k<=j; k++) {
//       psyp[k] = oyp[j-k] * syp[k] * theirPascal[j][k];
//     }
//     // Loop through all coefficients in the x direction.
//     for (int i=0; i<nx; i++) {
//       // Get original coefficient.
//       double f = *pcold++;
//       // Calculate all terms of (sx+ox)^i
//       for (int k1=0; k1<=i; k1++) {
//         double c = oxp[i-k1] * sxp[k1] * theirPascal[i][k1] * f;
//         // Multiply each term with the precalculated terms of (sy+oy)^j
//         // and add the result to the appropriate new coefficient.
//         for (int k2=0; k2<=j; k2++) {
//           pcnew[k1 + k2*nx] += c * psyp[k2];
//         }
//       }
//     }
//   }
//   return newc;
// }
// 

} // namespace Meq
