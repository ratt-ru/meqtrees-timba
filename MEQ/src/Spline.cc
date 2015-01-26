//
//% $Id$ 
//
//
// Copyright (C) 2002-2007
// The MeqTree Foundation & 
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>,
// or write to the Free Software Foundation, Inc., 
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//

#include <TimBase/Profiling/PerfProfile.h>

#include "Spline.h"
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/MeqVocabulary.h>
#include <TimBase/Debug.h>
#include <TimBase/lofar_vector.h>
#include <cstdlib>
#include <cmath>

namespace Meq {

static DMI::Container::Register reg(TpMeqSpline,true);

  Spline::Spline(double pert,double weight,DbId id):
    Funklet(pert,weight,id)
  {
    (*this)[FClass]=objectType().toString();
    validateContent(false); // not recursive

  }


  Spline::Spline (const DMI::Record &other,int flags,int depth):
    Funklet(other,flags,depth)
  {
    (*this)[FClass]=objectType().toString();
    validateContent(false); // not recursive
  }

  Spline::Spline (const Spline &other,int flags,int depth):
    Funklet(other,flags,depth)
  {
    (*this)[FClass]=objectType().toString();
    validateContent(false); // not recursive, does init for you

  }


  Spline::Spline(double c00, const Domain & dom,int Npoints,double pert,double weight,DbId id)
    : Funklet(pert,weight,id)
{
  (*this)[FClass]=objectType().toString();
  setCoeff(c00);
  LoShape shape(Npoints);
  setCoeffShape(shape);
  setDomain(dom);
  init();
}


Spline::Spline(const LoVec_double &coeff, const Domain & dom,
           int iaxis,double x0,double xsc,
           double pert,double weight,DbId id)
  : Funklet(1,&iaxis,&x0,&xsc,pert,weight,id)
{
  (*this)[FClass]=objectType().toString();
  setCoeff(coeff);
  setDomain(dom);
  init();
}

  Spline::Spline(const LoMat_double &coeff, const Domain & dom,
           const int iaxis[],const double offset[],const double scale[],
           double pert,double weight,DbId id)
  : Funklet(2,iaxis,offset,scale,pert,weight,id)
{
  (*this)[FClass]=objectType().toString();
  setCoeff(coeff);
  setDomain(dom);
  init();
}

  Spline::Spline(DMI::NumArray *pcoeff, const Domain & dom,
           const int iaxis[],const double offset[],const double scale[],
           double pert,double weight,DbId id)
{
  (*this)[FClass]=objectType().toString();

  ObjRef ref(pcoeff);
  FailWhen(pcoeff->elementType() != Tpdouble,"can't create Meq::Spline from this array: not double");
  int rnk = pcoeff->rank();
  FailWhen(rnk>MaxSplineRank,"can't create Meq::Spline from this array: rank too high");
  // if only a single coeff, rank is 0
  if( rnk == 1 && pcoeff->size() == 1 )
    rnk = 0;
  Funklet::init(rnk,iaxis,offset,scale,pert,weight,id);
  Field & field = Record::addField(FCoeff,ref,Record::PROTECT|DMI::REPLACE);
  pcoeff_ = &( field.ref().ref_cast<DMI::NumArray>() );
  setDomain(dom);
  init();
}

void Spline::validateContent (bool recursive)
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
	FailWhen((*pcoeff_)->elementType()!=Tpdouble,"Meq::Spline: coeff array must be of type double");

	// check for sanity
	FailWhen((*pcoeff_)->rank()>MaxSplineRank,"Meq::Spline: coeff can have max. rank of 8");

      }
      else
	pcoeff_ = 0;
    }
    //initialize now
    init();

  }
  catch( std::exception &err )
  {
    ThrowMore(err,"validate of Spline record failed");
  }
  catch( ... )
  {
    Throw("validate of Spline record failed with unknown exception");
  }
}



void Spline::do_evaluate (VellSet &vs,const Cells &cells,
    const std::vector<double> &perts,
    const std::vector<int>    &spidIndex,
    int makePerturbed) const
{
  double A[100],B[100],C[100];
  double Ap[2][100][100],Bp[2][100][100],Cp[2][100][100];
  // init shape of result
  Vells::Shape res_shape;
  // Now, check that Cells includes all our axes of variability, and compute
  // a normalized grid along those axes.
  // If an axis is not defined in the Cells, then we can only proceed if we have
  // no dependence on that axis (i.e. only one coeff in that direction)
  int coeff_rank = std::min(coeff().rank(),cells.rank());
  Axis::degenerateShape(res_shape,cells.rank());
  DbgAssert(coeff_rank<=MaxSplineRank); // for now
  const LoShape & cshape = coeff().shape();
  int coeff_size = coeff().size();
  LoVec_double grid[MaxSplineRank];
  int total=1;
  for( int i=0; i<coeff_rank; i++ )
  {
    res_shape[i]=1;
    if( cshape[i] > 1 )
    {
      //      int iaxis = getAxis(i);
      int iaxis = i;//not understood bug
      FailWhen(!cells.isDefined(iaxis),
            "Meq::Polc: axis " + Axis::axisId(iaxis).toString() +
            " is not defined in Cells");
      grid[i].resize(cells.ncells(iaxis));
      grid[i] = cells.center(iaxis);
      res_shape[iaxis] = std::max(int(grid[i].size()),1);
      total*=res_shape[iaxis];
    }
  }

  create_spline(res_shape,perts,spidIndex,makePerturbed,A,B,C,Ap,Bp,Cp);
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

  double valx[MaxSplineRank];
  int idx[MaxSplineRank];
  for(int num =0;num<total;num++){//loop over all data points
    int shapes=num;
    for (int axis=coeff_rank-1;axis>=0; axis--)
      {//get indices
	idx[axis]=0;
	valx[axis]=0;
	if(res_shape[axis]>1)
	  {
	    idx[axis]=shapes%res_shape[axis];
	    shapes-=idx[axis];
	    shapes/=res_shape[axis];
	    valx[axis] = grid[axis](idx[axis]);
	  }
      }
    *value++ = get_value(valx,-1,-1,0.,A,B,C,Ap,Bp,Cp);
  //perturbations
  if( makePerturbed )
      {
	for(int ipert=0;ipert <makePerturbed; ipert++){
	  for(int ik =0;ik <ncoeff();ik++)
	    if( pertValPtr[ipert][ik] ) {
	      *(pertValPtr[ipert][ik])++ = get_value(valx,ipert,ik,perts[ik],A,B,C,Ap,Bp,Cp);
	    }
	}
      }
  }

}


void Spline::init(){
    Domain dom = domain();
    LoShape shape = coeff().shape();
    for(int axis = 0;axis<coeff().rank();axis++){
      N[axis]=0;
      dx[axis]=dom.end(axis)-dom.start(axis);
      x0[axis]=dom.start(axis);
      if(shape[axis]>1)
	{
	      N[axis]=shape[axis];
	      dx[axis]/=N[axis]-1;
	      //	      x0[axis]+=0.5*dx[axis];

	}
    }

}

double Spline::get_value(const double *x,const int ipert,const int perturb,const double pert,
			 double A[],double B[],double C[],
			 double Ap[2][100][100],double Bp[2][100][100],double Cp[2][100][100]) const{
   //get index for all x, (for now len(x))=1;
   int idx_x=-1;
   double delta_x = 0.;
   for(int axis = 0;axis<coeff().rank();axis++){
     if(N[axis]>1)
       {
	 idx_x=int((x[axis]-x0[axis])/dx[axis]);
	 if(idx_x<=0) idx_x =1;
	 if(idx_x>=N[axis]-2) idx_x=N[axis]-3;
	 delta_x = x[axis]- x0[axis] - idx_x*dx[axis] ;
	 delta_x/=(N[axis]-1)*dx[axis]; //define dx=1/(N[axis]-1); needed because otherwise the A,B,C get too smallfor our large time freq domains
	 break;
       }
   }
   const double *y =  static_cast<const double*>(coeff().getConstDataPtr());
   if(idx_x<=0)  return y[0];
   double fx;
   if(perturb>=0){
     fx=y[idx_x] + Ap[ipert][perturb][idx_x]*(delta_x) +Bp[ipert][perturb][idx_x]*(delta_x*delta_x)+Cp[ipert][perturb][idx_x]*(delta_x*delta_x*delta_x);
     if(idx_x == perturb) fx += pert; //add perturbation to y[idx_x]
   }
   else
     fx=y[idx_x] + A[idx_x]*(delta_x) +B[idx_x]*(delta_x*delta_x)+C[idx_x]*(delta_x*delta_x*delta_x);
   return fx;
  }

void Spline::do_update (const double values[],const std::vector<int> &spidIndex,bool force_positive)
{
  Thread::Mutex::Lock lock(mutex());
  double* coeff = static_cast<double*>(coeffWr().getDataPtr());
  for( uint i=0; i<spidIndex.size(); i++ )
  {
    if( spidIndex[i] >= 0 )
      {
	cdebug(3)<<"updateing polc "<< coeff[i]<<" adding "<< values[spidIndex[i]]<<" "<<spidIndex[i]<<endl;
	coeff[i] += values[spidIndex[i]];
      }
  }
}


void Spline::do_update (const double values[],const std::vector<int> &spidIndex,const std::vector<double> &constraints,bool force_positive)
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


void Spline ::do_update (const double values[],const std::vector<int> &spidIndex,const std::vector<double> &constraints_min,const std::vector<double> &constraints_max,bool force_positive)
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
      }
  }
}


void Spline::setCoeffShape(const LoShape & shape){

  if(coeff().shape()==shape) return;

  //  if(coeff().shape().size()< shape.size()){
    // init problem??
  //taken care off in Funklet::setCoeff

  //}
  DMI::NumArray coeffnew(Tpdouble,shape);
  double * newdataptr = static_cast<double*>(coeffnew.getDataPtr());

  if(ncoeff()==1) //init all with c00
    {
      double c00 = getCoeff0();
      for(int i =0 ; i<coeffnew.size();i++)
	{
	  newdataptr[i]=c00;
	}
      setCoeff(coeffnew);
      return;
    }

  double * dataptr = static_cast<double*>(coeffWr().getDataPtr());

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


void Spline::create_spline(const Axis::Shape& res_shape,
			   const std::vector<double> &perts,
			   const std::vector<int>    &spidIndex,
			   int makePerturbed,
			   double A[],double B[],double C[],
			   double Ap[2][100][100],double Bp[2][100][100],double Cp[2][100][100])const {
  //fills the coefficients of all splines + all perturbed splines
  const double *y =  static_cast<const double*>(coeff().getConstDataPtr());
  //first get C1
  for(int axis = 0;axis<coeff().rank();axis++){
    if(N[axis]>1)
      {
	double dd = 1./(N[axis]-1); //x runs from 0 to 1
	double C_A[N[axis]]; C_A[1]=-1.;
	double C_B[N[axis]]; C_B[1]=0.;
	A[1]=(y[2]-y[0])/(2.*dd);
	B[1]=(y[2]+y[0]-2*y[1])/(2.*dd*dd);
	if(makePerturbed)
	  {
	    for( int ipert=0; ipert<makePerturbed; ipert++ )
	      {
		for( uint isp=0; isp<spidIndex.size(); isp++)
		  if( spidIndex[isp] >= 0 ){
		    Ap[ipert][isp][1]=(y[2]-y[0])/(2.*dd);
		    Bp[ipert][isp][1]=(y[2]+y[0]-2*y[1])/(2.*dd*dd);
		    if(isp == 0){
		      Ap[ipert][isp][1]-=0.5*perts[isp]*pow(-1,ipert)/dd;
		      Bp[ipert][isp][1]+=0.5*perts[isp]*pow(-1,ipert)/(dd*dd);
		    }
		    if(isp == 1){
		      Bp[ipert][isp][1]-=perts[isp]*pow(-1,ipert)/(dd*dd);
		    }
		    if(isp == 2){
		      Ap[ipert][isp][1]+=0.5*perts[isp]*pow(-1,ipert)/dd;
		      Bp[ipert][isp][1]+=0.5*perts[isp]*pow(-1,ipert)/(dd*dd);
		    }
		  }}}

	for(uint i=2;i<=uint(N[axis]-3);i++)
	  {
	    A[i] = 3*(y[i]-y[i-1])/dd-2*A[i-1]-B[i-1]*dd;
	    C_A[i]=-2*C_A[i-1] - dd*C_B[i-1];
	    B[i] = 3*(y[i]-y[i-1])/(dd*dd)-3*A[i-1]/dd-2*B[i-1];
	    C_B[i]=-3*C_A[i-1]/dd - 2*C_B[i-1];
	    if(makePerturbed)
	      {
		for( int ipert=0; ipert<makePerturbed; ipert++ )
		  {
		    for( uint isp=0; isp<spidIndex.size(); isp++)
		      if( spidIndex[isp] >= 0 ){
			Ap[ipert][isp][i] = 3*(y[i]-y[i-1])/dd-2*Ap[ipert][isp][i-1]-Bp[ipert][isp][i-1]*dd;
			Bp[ipert][isp][i] = 3*(y[i]-y[i-1])/(dd*dd)-3*Ap[ipert][isp][i-1]/dd-2*Bp[ipert][isp][i-1];
			if(isp ==i)
			  {
			    Ap[ipert][isp][i] += 3*perts[isp]*pow(-1,ipert)/dd;
			    Bp[ipert][isp][i] += 3*perts[isp]*pow(-1,ipert)/(dd*dd);
			  }
			if(isp ==(i-1))
			  {
			    Ap[ipert][isp][i] -= 3*perts[isp]*pow(-1,ipert)/dd;
			    Bp[ipert][isp][i] -= 3*perts[isp]*pow(-1,ipert)/(dd*dd);
			  }

		      }

		  }

	      }
	  }
	uint n=N[axis]-3;
	C[1] = 7*(y[n+1]-y[n])/(dd*dd*dd) -(y[n+2]-y[n+1])/(dd*dd*dd) - 6*A[n]/(dd*dd) -4*B[n]/dd;
	C[1]/= (6*C_A[n]+4*C_B[n]);

	A[1]-=C[1]*dd*dd;
	if(makePerturbed)
	  {
	    for( int ipert=0; ipert<makePerturbed; ipert++ )
	      {
		for( uint isp=0; isp<spidIndex.size(); isp++)
		  if( spidIndex[isp] >= 0 ){


		    Cp[ipert][isp][1] = 7*(y[n+1]-y[n])/(dd*dd*dd) -(y[n+2]-y[n+1])/(dd*dd*dd) - 6*Ap[ipert][isp][n]/(dd*dd) -4*Bp[ipert][isp][n]/dd;
		    if(isp ==n)
		      {
			Cp[ipert][isp][1] -=7*perts[isp]*pow(-1,ipert)/(dd*dd*dd);
		      }
		    if(isp ==(n+1))
		      {
			Cp[ipert][isp][1] +=8*perts[isp]*pow(-1,ipert)/(dd*dd*dd);

		      }
		    if(isp ==(n+2))
		      {
			Cp[ipert][isp][1] -=perts[isp]*pow(-1,ipert)/(dd*dd*dd);

		      }
		    Cp[ipert][isp][1]/=(6*C_A[n]+4*C_B[n]);
		    Ap[ipert][isp][1] -= Cp[ipert][isp][1]*dd*dd;

		  }

	      }

	  }


	//now correct and get A,B,C

	for(uint i=2;i<=uint(N[axis]-3);i++)
	  {
	    A[i] += C_A[i]*C[1]*dd*dd;
	    B[i] += C_B[i]*C[1]*dd;
	    C[i] = (y[i+1] - y[i])/(dd*dd*dd) - A[i]/(dd*dd) - B[i]/dd;


	    if(makePerturbed)
	      {
		for( int ipert=0; ipert<makePerturbed; ipert++ )
		  {
		    for( uint isp=0; isp<spidIndex.size(); isp++)
		      {
			if( spidIndex[isp] >= 0 ){
			  Ap[ipert][isp][i] += C_A[i]*Cp[ipert][isp][1]*dd*dd;
			  Bp[ipert][isp][i] += C_B[i]*Cp[ipert][isp][1]*dd;
			  Cp[ipert][isp][i] =  (y[i+1] - y[i])/(dd*dd*dd) -Ap[ipert][isp][i]/(dd*dd)-Bp[ipert][isp][i]/dd;
			  if(isp==i)
			    Cp[ipert][isp][i]-=perts[isp]*pow(-1,ipert)/(dd*dd*dd);
			  if(isp==(i+1))
			    Cp[ipert][isp][i]+=perts[isp]*pow(-1,ipert)/(dd*dd*dd);
			}
		      }
		  }
	      }
	  }
      }
  }
}


}//namespace Meq
