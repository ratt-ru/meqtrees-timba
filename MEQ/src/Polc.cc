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

static DMI::Container::Register reg(TpMeqPolc,true);

const int    defaultPolcAxes[MaxPolcRank]       = {0,1};
const double defaultPolcOffset[MaxPolcRank]     = {0,0};
const double defaultPolcScale[MaxPolcRank]      = {1,1};

static std::vector<int> default_axes(defaultPolcAxes,defaultPolcAxes+MaxPolcRank);
static std::vector<double> default_offset(defaultPolcOffset,defaultPolcOffset+MaxPolcRank);
static std::vector<double> default_scale(defaultPolcScale,defaultPolcScale+MaxPolcRank);

Polc::Polc(double pert,double weight,DbId id)
  : Funklet(pert,weight,id),pcoeff_(0)
{
}

//##ModelId=3F86886F0366
Polc::Polc(double c00,double pert,double weight,DbId id)
  : Funklet(pert,weight,id)
{
  setCoeff(c00);
}

Polc::Polc(const LoVec_double &coeff,
           int iaxis,double x0,double xsc,
           double pert,double weight,DbId id)
  : Funklet(1,&iaxis,&x0,&xsc,pert,weight,id)
{
  setCoeff(coeff);
}

Polc::Polc(const LoMat_double &coeff,
           const int iaxis[],const double offset[],const double scale[],
           double pert,double weight,DbId id)
  : Funklet(2,iaxis,offset,scale,pert,weight,id)
{
  setCoeff(coeff);
}

Polc::Polc(DMI::NumArray *pcoeff,
           const int iaxis[],const double offset[],const double scale[],
           double pert,double weight,DbId id)
{
  ObjRef ref(pcoeff);
  FailWhen(pcoeff->elementType() != Tpdouble,"can't create Meq::Polc from this array: not double");
  FailWhen(pcoeff->rank()>MaxPolcRank,"can't create Meq::Polc from this array: rank too high");
  int rnk = pcoeff->rank();
  // if only a single coeff, rank is 0
  if( rnk == 1 && pcoeff->size() == 1 )
    rnk = 0;
  init(rnk,iaxis,offset,scale,pert,weight,id);
  Field & field = Record::addField(FCoeff,ref,Record::PROTECT|DMI::REPLACE);
  pcoeff_ = &( field.ref.ref_cast<DMI::NumArray>() );
}

//##ModelId=400E5354033A
Polc::Polc (const DMI::Record &other,int flags,int depth)
  : Funklet(other,flags,depth)
{
  validateContent(false); // not recursive
}

Polc::Polc (const Polc &other,int flags,int depth)
  : Funklet(other,flags,depth)
{
// no need to validate content outside the coeff, eveything else handled by funklet copy
  Field * fld = Record::findField(FCoeff);
  pcoeff_ = fld ? &( fld->ref.ref_cast<DMI::NumArray>() ) : 0;
}

void Polc::validateContent (bool recursive)    
{
  Thread::Mutex::Lock lock(mutex());
  // ensure that our record contains all the right fields; setup shortcuts
  // to their contents
  try
  {
    // init polc fields
    if( recursive )
      Funklet::validateContent(true);
    // get polc coefficients
    Field * fld = Record::findField(FCoeff);
    if( fld )
      pcoeff_ = &( fld->ref.ref_cast<DMI::NumArray>() );
    else
      pcoeff_ = 0;
    // check for sanity
    Assert(rank()<=MaxPolcRank && coeff().rank()<=rank());
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

void Polc::setCoeff (const DMI::NumArray &arr)
{
  Thread::Mutex::Lock lock(mutex());
  FailWhen(rank()!=arr.rank(),"Meq::Polc: coeff rank mismatch");
  FailWhen(arr.elementType()!=Tpdouble,"Meq::Polc: coeff array must be of type double");
  ObjRef ref(new DMI::NumArray(arr));
  Field & field = Record::addField(FCoeff,ref,Record::PROTECT|DMI::REPLACE);
  pcoeff_ = &( field.ref.ref_cast<DMI::NumArray>() );
}

void Polc::setCoeff (double c00)
{
  Thread::Mutex::Lock lock(mutex());
  FailWhen(rank()!=0,"Meq::Polc: coeff rank mismatch");
  LoVec_double coeff(1);
  coeff = c00;
  ObjRef ref(new DMI::NumArray(coeff));
  Field & field = Record::addField(FCoeff,ref,Record::PROTECT|DMI::REPLACE);
  pcoeff_ = &( field.ref.ref_cast<DMI::NumArray>() );
}

void Polc::setCoeff (const LoVec_double & coeff)
{
  Thread::Mutex::Lock lock(mutex());
  if( !rank() )
    init(1,defaultPolcAxes,defaultPolcOffset,defaultPolcScale);
  else {
    FailWhen(rank()!=1,"Meq::Polc: coeff rank mismatch");
  }
  ObjRef ref(new DMI::NumArray(coeff));
  Field & field = Record::addField(FCoeff,ref,Record::PROTECT|DMI::REPLACE);
  pcoeff_ = &( field.ref.ref_cast<DMI::NumArray>() );
}

void Polc::setCoeff (const LoMat_double & coeff)
{
  Thread::Mutex::Lock lock(mutex());
  if( !rank() )
    init(2,defaultPolcAxes,defaultPolcOffset,defaultPolcScale);
  else {
    FailWhen(rank()!=2,"Meq::Polc: coeff rank mismatch");
  }
  ObjRef ref(new DMI::NumArray(coeff));
  Field & field = Record::addField(FCoeff,ref,Record::PROTECT|DMI::REPLACE);
  pcoeff_ = &( field.ref.ref_cast<DMI::NumArray>() );
}


void Polc::do_evaluate (VellSet &vs,const Cells &cells,
    const std::vector<double> &perts,
    const std::vector<int>    &spidIndex,
    int makePerturbed) const
{
  // init shape of result
  Vells::Shape res_shape;
  Axis::degenerateShape(res_shape,cells.rank());
  // Now, check that Cells includes all our axes of variability, and compute
  // a normalized grid along those axes.
  // If an axis is not defined in the Cells, then we can only proceed if we have
  // no dependence on that axis (i.e. only one coeff in that direction)
  int coeff_rank = coeff().rank();
  DbgAssert(coeff_rank<=2); // for now
  const LoShape & cshape = coeff().shape();
  int coeff_size = coeff().size();
  LoVec_double grid[2];
  for( int i=0; i<coeff_rank; i++ )
  {
    if( cshape[i] > 1 )
    {
      int iaxis = getAxis(i);
      FailWhen(!cells.isDefined(iaxis),
            "Meq::Polc: axis " + Axis::name(iaxis).toString() + 
            " is not defined in Cells");
      grid[i].resize(cells.ncells(i));
      grid[i] = ( cells.center(iaxis) - getOffset(i) ) * getScale(i);
      res_shape[iaxis] = grid[i].size();
    }
  }
  // now evaluate
  // If there is only one coefficient, the polynomial is independent
  // of x and y.
  // So set the value to the coefficient and possibly set the perturbed value.
  // Make sure it is turned into a scalar value.
  if( coeff_size == 1 )
  {
    double c00 = getCoeff0();
    vs.setValue(new Vells(c00,false));
    if( makePerturbed )
    {
      double d = perts[0];
      for( int ipert=0; ipert<makePerturbed; ipert++,d=-d )
        vs.setPerturbedValue(0,new Vells(c00+d,false),ipert);
    }
    return;
  }
  // else check if we're dealing with a 1D poly. Note that a 1xN poly
  // is also treated as 1D; we simply use the second grid array
  if( coeff_rank == 1 || cshape[0] == 1 || cshape[1] == 1 ) // evaluate 1D poly
  {
    // determine which grid points to actually use
    LoVec_double grid(cshape[0] > 1 ? grid[0] : grid[1]);
    // Get number of steps and coefficients in x and y 
    int ndx = grid.size();
    int ncx = coeff_size;
    // Evaluate the expression (as double).
    const double* coeffData = static_cast<const double *>(coeff().getConstDataPtr());
    double* pertValPtr[MaxNumPerts][spidIndex.size()];
    for( int ipert=0; ipert<makePerturbed; ipert++ )
    {
      // Create a vells for each perturbed value.
      // Keep a pointer to its storage
      for( uint i=0; i<spidIndex.size(); i++) 
        if( spidIndex[i] >= 0 )
          pertValPtr[ipert][i] = 
              vs.setPerturbedValue(spidIndex[i],new Vells(0.,res_shape,true),ipert)
                    .realStorage();
        else
          pertValPtr[ipert][i] = 0;
    }
    // Create matrix for the main value and keep a pointer to its storage
    double* value = vs.setValue(new Vells(0,res_shape,true)).realStorage();
    for( int i=0; i<ndx; i++ )
    {
      double valx = grid(i);
      double total = coeffData[ncx-1];
      for (int j=ncx-2; j>=0; j--) 
      {
        total *= valx;
        total += coeffData[j];
      }
      if( makePerturbed ) 
      {
        double powx = 1;
        for (int j=0; j<ncx; j++) 
        {
          double d = perts[j] * powx;
          for( int ipert=0; ipert<makePerturbed; ipert++,d=-d ) 
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
  const double* coeffData = static_cast<const double *>(coeff().getConstDataPtr());
  double* pertValPtr[MaxNumPerts][100];
  for( int ipert=0; ipert<makePerturbed; ipert++ )
  {
    // Create a vells for each perturbed value.
    // Keep a pointer to its storage
    for( uint i=0; i<spidIndex.size(); i++) 
      if( spidIndex[i] >= 0 )
        pertValPtr[ipert][i] = 
            vs.setPerturbedValue(spidIndex[i],new Vells(0.,res_shape,true),ipert)
                  .realStorage();
      else
        pertValPtr[ipert][i] = 0;
  }
  // Create matrix for the main value and keep a pointer to its storage
  double* value = vs.setValue(new Vells(0,res_shape,true)).realStorage();
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
      if( makePerturbed ) 
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
            double d = perts[ik] * powersx[ix] * powy;
            for( int ipert=0; ipert<makePerturbed; ipert++,d=-d ) {
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
}

//##ModelId=3F86886F03BE
void Polc::do_update (const double values[],const std::vector<int> &spidIndex)
{
  Thread::Mutex::Lock lock(mutex());
  double* coeff = static_cast<double*>(coeffWr().getDataPtr());
  for( uint i=0; i<spidIndex.size(); i++ ) 
  {
    if( spidIndex[i] >= 0 ) 
      coeff[i] += values[spidIndex[i]];
  }
}

} // namespace Meq
