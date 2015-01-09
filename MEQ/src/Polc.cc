//# Polc.cc: Polynomial coefficients
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

#include <TimBase/Profiling/PerfProfile.h>

#include "Polc.h"
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/Vells.h>
#include <MEQ/MeqVocabulary.h>
#include <TimBase/Debug.h>
#include <TimBase/lofar_vector.h>
#include <cstdlib>
#include <cmath>

namespace Meq {

static DMI::Container::Register reg(TpMeqPolc,true);

 const int    defaultPolcAxes[MaxPolcRank]       = {0,1};
 const double defaultPolcOffset[MaxPolcRank]     = {0,0};
 const double defaultPolcScale[MaxPolcRank]      = {1,1};
//   const int    defaultPolcAxes[MaxPolcRank]       = {0,1,2,3,4,5,6,7};
//   const double defaultPolcOffset[MaxPolcRank]     = {0,0,0,0,0,0,0,0};
//   const double defaultPolcScale[MaxPolcRank]      = {1,1,1,1,1,1,1,1};

static std::vector<int> default_axes(defaultPolcAxes,defaultPolcAxes+MaxPolcRank);
static std::vector<double> default_offset(defaultPolcOffset,defaultPolcOffset+MaxPolcRank);
static std::vector<double> default_scale(defaultPolcScale,defaultPolcScale+MaxPolcRank);

Polc::Polc(double pert,double weight,DbId id)
  : Funklet(pert,weight,id)
{
    (*this)[FClass]=objectType().toString();

}

//##ModelId=3F86886F0366
Polc::Polc(double c00,double pert,double weight,DbId id)
  : Funklet(pert,weight,id)
{
  (*this)[FClass]=objectType().toString();
  setCoeff(c00);
}

Polc::Polc(const LoVec_double &coeff,
           int iaxis,double x0,double xsc,
           double pert,double weight,DbId id)
  : Funklet(1,&iaxis,&x0,&xsc,pert,weight,id)
{
  (*this)[FClass]=objectType().toString();
  setCoeff(coeff);
}

Polc::Polc(const LoMat_double &coeff,
           const int iaxis[],const double offset[],const double scale[],
           double pert,double weight,DbId id)
  : Funklet(2,iaxis,offset,scale,pert,weight,id)
{
  (*this)[FClass]=objectType().toString();
  setCoeff(coeff);
}

Polc::Polc(DMI::NumArray *pcoeff,
           const int iaxis[],const double offset[],const double scale[],
           double pert,double weight,DbId id)
{
  (*this)[FClass]=objectType().toString();

  ObjRef ref(pcoeff);
  FailWhen(pcoeff->elementType() != Tpdouble,"can't create Meq::Polc from this array: not double");
  int rnk = pcoeff->rank();
  FailWhen(rnk>MaxPolcRank,"can't create Meq::Polc from this array: rank too high");
  // if only a single coeff, rank is 0
  if( rnk == 1 && pcoeff->size() == 1 )
    rnk = 0;
  init(rnk,iaxis,offset,scale,pert,weight,id);
  Field & field = Record::addField(FCoeff,ref,Record::PROTECT|DMI::REPLACE);
  pcoeff_ = &( field.ref().ref_cast<DMI::NumArray>() );
}

//##ModelId=400E5354033A
Polc::Polc (const DMI::Record &other,int flags,int depth)
  : Funklet(other,flags,depth)
{
  (*this)[FClass]=objectType().toString();
  validateContent(false); // not recursive
}

Polc::Polc (const Polc &other,int flags,int depth)
  : Funklet(other,flags,depth)
{
  (*this)[FClass]=objectType().toString();

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
    else{
      Field * fld = Record::findField(FCoeff);
      if( fld ){
	pcoeff_ = &( fld->ref().ref_cast<DMI::NumArray>() );
	//coeff should be doubles:
	if ((*pcoeff_)->elementType()==Tpint ||(*pcoeff_)->elementType()==Tpfloat||(*pcoeff_)->elementType()==Tplong )
	{
	  //convert to double

	}
	FailWhen((*pcoeff_)->elementType()!=Tpdouble,"Meq::Polc: coeff array must be of type double");

	// check for sanity
	FailWhen((*pcoeff_)->rank()>MaxPolcRank,"Meq::Polc: coeff can have max. rank of 2");

      }
      else
	pcoeff_ = 0;
    }

  }
  catch( std::exception &err )
  {
    ThrowMore(err,"validate of Polc record failed");
  }
  catch( ... )
  {
    Throw("validate of Polc record failed with unknown exception");
  }
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
  DbgAssert(coeff_rank<=MaxPolcRank); // for now
  const LoShape & cshape = coeff().shape();
  int coeff_size = coeff().size();
  LoVec_double grid[2];
  for( int i=0; i<coeff_rank; i++ )
  {
    if( cshape[i] > 1 )
    {
      int iaxis = getAxis(i);
      FailWhen(!cells.isDefined(iaxis),
            "Meq::Polc: axis " + Axis::axisId(iaxis).toString() +
            " is not defined in Cells");
      if(cells.domain().start(i)<domain().start(i) ||cells.domain().end(i)>domain().end(i) )
	{
	  LoVec_double tempgrid = ( cells.center(iaxis));
	  int k=0;
	  while(tempgrid(k)< domain().start(i) && k < tempgrid.size()){k++;}
	  int firstk=k;
	  k=tempgrid.size()-1;
	  while(tempgrid(k)>domain().end(i) && k > 0){k--;}
	  int lastk=k;
	  //reduce grid, such that it fits on domain of this funklet
	  if(lastk<firstk) return;


	  grid[i].resize(lastk-firstk+1);
	  if(firstk==0 && lastk==(tempgrid.size()-1))
	    {
	      grid[i]=tempgrid;
	    }
	  else{
	    for(k=firstk;k<=lastk;k++){
	      grid[i](k-firstk)=tempgrid(k);
	    }
	  }
	}
      else
	{
	  grid[i].resize(cells.ncells(iaxis));
	  grid[i] = cells.center(iaxis);
	}
      //apply axis function here
      axis_function(iaxis,grid[i]);

      //faster to multiply could be done init of course...
      double one_over_scale=(getScale(i) ? 1./getScale(i) : 1.);




      grid[i] = ( grid[i] - getOffset(i) )*one_over_scale;

      cdebug(4)<<"calculating polc on grid "<<i<<" : "<<grid[i]<<endl;
      res_shape[iaxis] = std::max(int(grid[i].size()),1);
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
    LoVec_double gridn(cshape[0] > 1 ? grid[0] : grid[1]);
    // Get number of steps and coefficients in x and y
    int ndx = gridn.size();
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
              vs.setPerturbedValue(spidIndex[i],new Vells(double(0),res_shape,true),ipert)
                    .realStorage();
        else
          pertValPtr[ipert][i] = 0;
    }
    // Create matrix for the main value and keep a pointer to its storage
    double* value = vs.setValue(new Vells(double(0),res_shape,true)).realStorage();
    for( int i=0; i<ndx; i++ )
    {
      double valx = gridn(i);
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
  double* pertValPtr[MaxNumPerts][spidIndex.size()];
  for( int ipert=0; ipert<makePerturbed; ipert++ )
  {
    // Create a vells for each perturbed value.
    // Keep a pointer to its storage
    for( uint i=0; i<spidIndex.size(); i++)
      if( spidIndex[i] >= 0 )
        pertValPtr[ipert][i] =
            vs.setPerturbedValue(spidIndex[i],new Vells(double(0),res_shape,true),ipert)
                  .realStorage();
      else
        pertValPtr[ipert][i] = 0;
  }
  // Create matrix for the main value and keep a pointer to its storage
  double* value = vs.setValue(new Vells(double(0),res_shape,true)).realStorage();
  // Iterate over all cells in the domain.
  // The Y index iterates faster, hence the outer loop is over j over X values
  for (int j=0; j<ndx; j++)
  {
    double valx = grid[0](j);
    for (int i=0; i<ndy; i++)  // inner loop: i over Y values
    {
      double valy = grid[1](i);
      const double* coeff = coeffData;
      double total = 0;
      double powx = 1;
      for (int ix=0; ix<ncx; ix++)
      {
        double tmp = coeff[ncy-1];
        for (int iy=ncy-2; iy>=0; iy--)
        {
          tmp *= valy;
          tmp += coeff[iy];
        }
        total += tmp * powx;
        powx *= valx;
        coeff += ncy;
      }
      if( makePerturbed )
      {
        double powersy[10];
        double powy = 1;
        for (int iy=0; iy<ncy; iy++) {
          powersy[iy] = powy;
          powy *= valy;
        }
        double powx = 1;
        int ik = 0;
        for (int ix=0; ix<ncx; ix++) {
          for (int iy=0; iy<ncy; iy++) {
            double d = perts[ik] * powersy[iy] * powx;
            for( int ipert=0; ipert<makePerturbed; ipert++,d=-d ) {
              if( pertValPtr[ipert][ik] ) {
                *(pertValPtr[ipert][ik]) = total + d;
                pertValPtr[ipert][ik]++;
              }
            }
            ik++;
          }
          powx *= valx;
        }
      }
      cdebug(4)<<"value  "<<i<<","<<j<<" ("<<valx<<","<<valy<<") : "<<total<<endl;
      *value++ = total;
    } // endfor(i) over cells
  } // endfor(j) over cells


}

//##ModelId=3F86886F03BE
void Polc::do_update (const double values[],const std::vector<int> &spidIndex,bool force_positive)
{
  Thread::Mutex::Lock lock(mutex());
  double* coeff = static_cast<double*>(coeffWr().getDataPtr());
  for( uint i=0; i<spidIndex.size(); i++ )
  {
    if( spidIndex[i] >= 0 )
      {
	cdebug(3)<<"updateing polc "<< coeff[i]<<" adding "<< values[spidIndex[i]]<<spidIndex[i]<<endl;
	coeff[i] += values[spidIndex[i]];
	if(force_positive && isConstant())
	  coeff[i]=std::fabs(coeff[i]);
      }
  }
}

//##ModelId=3F86886F03BE
void Polc::do_update (const double values[],const std::vector<int> &spidIndex,const std::vector<double> &constraints,bool force_positive)
{
  Thread::Mutex::Lock lock(mutex());
  if(! isConstant()) {do_update (values,spidIndex); return;}//only contraint if constant
  double* coeff = static_cast<double*>(coeffWr().getDataPtr());
  for( uint i=0; i<spidIndex.size(); i++ )
  {
    if( spidIndex[i] >= 0 )
      {
	cdebug(3)<<"updateing polc "<< coeff[i]<<" adding "<< values[spidIndex[i]]<<spidIndex[i]<<endl;
	coeff[i] += values[spidIndex[i]];
	coeff[i] = std::min(coeff[i],constraints[1]);
	coeff[i] = std::max(coeff[i],constraints[0]);
	if(force_positive && isConstant())
	  coeff[i]=std::fabs(coeff[i]);
      }
  }
}

void Polc::do_update (const double values[],const std::vector<int> &spidIndex,const std::vector<double> &constraints_min,const std::vector<double> &constraints_max,bool force_positive)
{
  Thread::Mutex::Lock lock(mutex());
  double* coeff = static_cast<double*>(coeffWr().getDataPtr());
  for( uint i=0; i<spidIndex.size(); i++ )
  {
    if( spidIndex[i] >= 0 )
      {
	cdebug(3)<<"updateing polc "<< coeff[i]<<" adding "<< values[spidIndex[i]]<<spidIndex[i]<<endl;
	coeff[i] += values[spidIndex[i]];
	if(i<constraints_max.size())
	  coeff[i] = std::min(coeff[i],constraints_max[i]);
	if(i<constraints_min.size())
	  coeff[i] = std::max(coeff[i],constraints_min[i]);
	if(force_positive && isConstant())
	  coeff[i]=std::fabs(coeff[i]);
      }
  }
}


void Polc::changeSolveDomain(const Domain & solveDomain){
  Thread::Mutex::Lock lock(mutex());

  if(!hasDomain()) return; //nothing to change
    else{
      const Domain &valDomain =  domain(); //validity domain
      std::vector<double> newoffsets(2);
      std::vector<double> newscales(2);
      for(int axisi=0;axisi<2;axisi++){
	newoffsets[axisi] = solveDomain.start(axisi)*valDomain.end(axisi)-
	  solveDomain.end(axisi)*valDomain.start(axisi);
	newoffsets[axisi] /= solveDomain.start(axisi)-solveDomain.end(axisi);
	newscales[axisi] = valDomain.end(axisi) - valDomain.start(axisi);
	newscales[axisi] /= solveDomain.end(axisi) - solveDomain.start(axisi);

      }
     transformCoeff(newoffsets,newscales);

    }

}


  void Polc::changeSolveDomain(const std::vector<double> & solveDomain){
    Thread::Mutex::Lock lock(mutex());

    if(solveDomain.size()<2) return; //incorrect format
    if(!hasDomain()) return; //nothing to change
    else{
      const Domain &valDomain =  domain(); //validity domain
      std::vector<double> newoffsets(2);
      std::vector<double> newscales(2);
      for(int axisi=0;axisi<2;axisi++){
	newoffsets[axisi] = solveDomain[0]*valDomain.end(axisi)-
	  solveDomain[1]*valDomain.start(axisi);
	newoffsets[axisi] /= solveDomain[0]-solveDomain[1];
	newscales[axisi] = valDomain.end(axisi) - valDomain.start(axisi);
	newscales[axisi] /= solveDomain[1] - solveDomain[0];

      }
     transformCoeff(newoffsets,newscales);

    }

}



int Polc::makeSolvable (int spidIndex){
  Thread::Mutex::Lock lock(mutex());

  if( ncoeff()<4) return Funklet::makeSolvable(spidIndex) ;
  const LoShape shape =  getCoeffShape ();
  if(shape.size()<=1) return Funklet::makeSolvable(spidIndex) ; //only 1 dimension
  int NX=shape[0];
  int NY=shape[1];
  int maxRank = std::max(NX,NY)-1;
  std::vector<bool> mask;
  if((*this)[FCoeffMask].get_vector(mask)){
    //check shapes
    uint size=mask.size();
    if(int(size) == getNumParms())
      return Funklet::makeSolvable(spidIndex,mask);
  }
  //if user did not specify a mask, set the default to everything but the lower right triangle

  double* coeff = static_cast<double*>(coeffWr().getDataPtr());
  mask = std::vector<bool>(NX*NY);

  for(int xi=0;xi<NX;xi++){
    for(int yi=0;yi<NY;yi++)
      {

	if(xi+yi > maxRank){
	  coeff[xi*NY+yi]=0.;
	  mask[xi*NY+yi]=false;
	}
	else mask[xi*NY+yi]=true;

      }
  }
  (*this)[FCoeffMask].replace()=mask;
  return Funklet::makeSolvable(spidIndex,mask);

}


void Polc::transformCoeff(const std::vector<double> & newoffsets,const std::vector<double> & newscales){
  //sets new offsets/scales and transforms Coeff if necessary
  Thread::Mutex::Lock lock(mutex());
  const LoShape shape =  getCoeffShape ();
  int NX=1;
  int NY=1;
  uint coeff_rank = coeff().rank();
  for(uint i=0;i<coeff_rank&&i<2;i++){
    if(i==0) NX=std::max(NX,shape[i]);
    if(i==1) NY=std::max(NY,shape[i]);
  }
  double C[NX][NY];
  double oldOffset[MaxPolcRank];
  double oldScale[MaxPolcRank];
  double diffOffset[MaxPolcRank];
  double diffScale[MaxPolcRank];


  double* coeff = static_cast<double*>(coeffWr().getDataPtr());
  int realchange=0;
  for(uint  i =0; i<newoffsets.size();i++){
    oldOffset[i]=getOffset(i);
    oldScale[i]=getScale(i);
    if(oldScale[i]==0) oldScale[i]=1.;
    if(newscales[i]==0) return; //shouldnt happen

    diffOffset[i]=(newoffsets[i]-oldOffset[i])/newscales[i];
    diffScale[i]=newscales[i]/oldScale[i];

    setOffset(i,newoffsets[i]);
    setScale(i,newscales[i]);
    if(diffOffset[i]!=0 || diffScale[i]!=1) realchange=1;
  }


  if(NX<=1 && NY<=1) return; //no x,y dpendencies, no change needed
  if(!realchange) return; //nothing changed really
  for(int xi=0;xi<NX;xi++)
    for(int yi=0;yi<NY;yi++){
      if((xi>0 || yi>0) && coeff[xi*NY+yi]!=0) realchange=0;
      C[xi][yi]=0;    }

  if(realchange) //all coefficients 0, no updat needed
    return;

  for(int xi=0;xi<NX;xi++)
    for(int yi=0;yi<NY;yi++)
      {
	double Cxy=coeff[xi*NY+yi];
	for(int rx=0;rx<=xi;rx++)
	  //loop over x ranking
	  for(int ry=0;ry<=yi;ry++)
	    {//loop over y ranking

	      C[rx][ry] += noverm(xi,rx)*noverm(yi,ry) *pow(diffOffset[0],xi-rx)*pow(diffOffset[1],yi-ry) * Cxy *(pow(diffScale[0],xi)*pow(diffScale[1],yi));
	    }

      }


  for(int xi=0;xi<NX;xi++)
    for(int yi=0;yi<NY;yi++)
      {
	cdebug(2)<<"transforming coeff["<<xi<<","<<yi<<"] from "<<coeff[xi*NY+yi];

	coeff[xi*NY+yi]=C[xi][yi];
	cdebug(2)<<" to "<<coeff[xi*NY+yi]<<endl;
      }


}







  void Polc::setCoeff (const LoVec_double & coeff){
    if (rank()<1)
      setRank(1);
    Funklet::setCoeff(coeff);

}




  void Polc::setCoeff (const LoMat_double & coeff){
  if (rank()<2)
    setRank(2);
  Funklet::setCoeff(coeff);

}



  void Polc::setCoeff (const DMI::NumArray & coeff){
  if (rank()<coeff.rank())
    setRank(coeff.rank());
  Funklet::setCoeff(coeff);

  }


void Polc::setCoeffShape(const LoShape & shape){

  if(coeff().shape()==shape) return;

  //  if(coeff().shape().size()< shape.size()){
    // init problem??
  //taken care off in Funklet::setCoeff

  //}
  DMI::NumArray coeffnew(Tpdouble,shape);
  double * dataptr = static_cast<double*>(coeffWr().getDataPtr());
  double * newdataptr = static_cast<double*>(coeffnew.getDataPtr());

  int N=coeff().size();
  int Nnew=coeffnew.size();
  const int rank=coeff().rank();
  const int ranknew=coeffnew.rank();
  int i[rank];
  for(int j=0;j<rank;j++)
    i[j]=0;
  for(int n=0;n<N;n++){
    int element=0;
    for(int j=0;j<ranknew&&j<rank;j++)
      {//calculate position
	element*=shape[j];
	element+=i[j];
	if(i[j]>0 && (j>int(shape.size())||i[j]>=shape[j]))
	  element=Nnew;
	//dont fill this one
	//we can go faster in case we are outside the scope of the new array
      }
    for(int j=rank-1;j>=0;j--)
      {
	//update coordinates, all this is necessary to allow N-dimensional stuff....
	i[j]++;
	if(i[j]>=coeff().shape()[j])
	  i[j]=0;
	else
	  break;

      }
    if(element<Nnew)
      newdataptr[element]=dataptr[n];


  }

  setCoeff(coeffnew);
}


} // namespace Meq
