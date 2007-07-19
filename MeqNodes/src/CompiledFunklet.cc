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

#include "CompiledFunklet.h"
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/MeqVocabulary.h>
#include <TimBase/Debug.h>
#include <TimBase/lofar_vector.h>
#include <cstdlib>
#include <cmath>

namespace Meq {

static DMI::Container::Register reg(TpMeqCompiledFunklet,true);

  CompiledFunklet::CompiledFunklet(double pert,double weight,DbId id):
    Funklet(pert,weight,id)
  {
    (*this)[FClass]=objectType().toString();
    Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex
    itsFunction = new casa::CompiledFunction<casa::Double>();
    itsDerFunction = new casa::CompiledFunction<casa::AutoDiff<casa::Double> >();
    if(hasField(FFunction)){
      string fstr;
      (*this)[FFunction].get(fstr,0);
      
      setFunction(fstr);
    }
  }
  

  CompiledFunklet::CompiledFunklet (const DMI::Record &other,int flags,int depth):
    Funklet(other,flags,depth)
  {
    (*this)[FClass]=objectType().toString();
    Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex
    itsFunction = new casa::CompiledFunction<casa::Double>();
    itsDerFunction = new casa::CompiledFunction<casa::AutoDiff<casa::Double> >();

    if(hasField(FFunction)){
      string fstr;
      (*this)[FFunction].get(fstr,0);
    
      setFunction(fstr);
    }
  }

  CompiledFunklet::CompiledFunklet (const CompiledFunklet &other,int flags,int depth):
    Funklet(other,flags,depth),Npar(other.Npar),Ndim(other.Ndim)
  {
    (*this)[FClass]=objectType().toString();
    Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex
  
    itsFunction=new casa::CompiledFunction<casa::Double>((*other.itsFunction));
    itsDerFunction = new casa::CompiledFunction<casa::AutoDiff<casa::Double> >(*(other.itsDerFunction));
      
  }


  int CompiledFunklet::dependsOn(int i){
    //to be implemented
    return 1;
  }
  
  void CompiledFunklet::fill_values(double *value, double * pertValPtr[],double *xval,const Vells::Shape & res_shape ,const int dimN, const LoVec_double grid[],const std::vector<double> &perts, const std::vector<int> &spidIndex, const int makePerturbed, int &pos) const
{
   
  //    Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex
    for(int datai=0;datai<res_shape[dimN];datai++){
      xval[dimN]=grid[dimN](datai);
      if(dimN < (Ndim-1.) && (dimN <(res_shape.size()-1)))

	
	{
	  fill_values(value,pertValPtr,xval,res_shape,dimN+1,grid,perts,spidIndex,makePerturbed,pos);
	}
      else{//the real filling
	//fill missing x's with 0
	for(int i = dimN+1;i<Ndim;i++)
	  xval[i]=0.;


	value[pos] = (*itsFunction)(xval);
	if( makePerturbed ) 
	  {
	    
	    const casa::Vector<casa::Double> deriv=(*itsDerFunction)(xval).derivatives();


	    for( uint ispid=0; ispid<spidIndex.size(); ispid++) 
	      if( spidIndex[ispid] >= 0 ){
		int d=1;
		//fill perturbed
		
		for( int ipert=0; ipert<makePerturbed; ipert++ ,d=-d)
		  {
		    //	      cdebug(3)<<"der "<<ispid<<" : "<<deriv<<endl;
		    ((pertValPtr[ipert*spidIndex.size()+ispid][pos])) = d*deriv[ispid]*perts[ispid]+ value[pos];
		  }
	      }
	  }
	pos++;
      }
    }
  }



void CompiledFunklet::do_evaluate (VellSet &vs,const Cells &cells,
    const std::vector<double> &perts,
    const std::vector<int>    &spidIndex,
    int makePerturbed) const
{
  // init shape of result
  Vells::Shape res_shape;
  Axis::degenerateShape(res_shape,cells.rank());
  Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex
  int ndim = Ndim;
  int ndim2 = std::min(ndim,cells.rank());
  LoVec_double grid[ndim2];
  if(ndim==0){
    //constant 
    if( makePerturbed )
      {
	const casa::AutoDiff<casa::Double> thederval = (*itsDerFunction)();
	vs.setValue(new Vells(thederval.value(),false));
	for( uint ispid=0; ispid<spidIndex.size(); ispid++) 
	  if( spidIndex[ispid] >= 0 ){
	    int d=1;
	    //fill perturbed
	    double deriv=thederval.derivatives()[ispid];
	    for( int ipert=0; ipert<makePerturbed; ipert++ ,d=-d)
	      {
		double dp = d*deriv*perts[ispid]+ thederval.value();
		vs.setPerturbedValue(ispid,new Vells(dp,false),ipert);
	      }
	  }
      }
    else
      {
	vs.setValue(new Vells((*itsFunction)(),false));
      }
    return;
  }



  for(int i=0;i<ndim;i++)
    {
  

      int iaxis = getAxis(i);
      //FailWhen(!cells.isDefined(iaxis),
      //       "Meq::CompiledFunklet: axis " + Axis::axisId(iaxis).toString() + 
      //" is not defined in Cells");
      

      if (!cells.isDefined(iaxis))
	{
	  cdebug(2)<<"Warning: axis "<<Axis::axisId(iaxis).toString()<<" is not defined in Cells, assume 0"<<endl;
	  continue;
	}

      //faster to multiply could be done init of course...
      //apply axis function here
      // if(_function_axis[i])
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
      axis_function(iaxis,grid[i]);

      double one_over_scale=(getScale(i) ? 1./getScale(i) : 1.);

      grid[i] = ( grid[i] - getOffset(i) )*one_over_scale;
      cdebug(2)<<"calculating polc on grid["<<i<<"]"<<grid[i]<<endl;
      res_shape[iaxis] = std::max(grid[i].size(),1);
    }

  double xval[ndim];
  int pos=0;
  double* pertValPtr[2*spidIndex.size()];
  for( int ipert=0; ipert<makePerturbed; ipert++ )
    {
      // Create a vells for each perturbed value.
      // Keep a pointer to its storage
      for( uint i=0; i<spidIndex.size(); i++) 
        if( spidIndex[i] >= 0 )
          pertValPtr[ipert*spidIndex.size()+i] = 
	    vs.setPerturbedValue(spidIndex[i],new Vells(double(0),res_shape,true),ipert)
	    .realStorage();
        else
          pertValPtr[ipert*spidIndex.size()+i] = 0;
    }
  // Create matrix for the main value and keep a pointer to its storage
  double* value = vs.setValue(new Vells(double(0),res_shape,true)).realStorage();
  
  fill_values(value,pertValPtr,xval,res_shape,0,grid,perts,spidIndex,makePerturbed,pos);

}



void CompiledFunklet::do_update (const double values[],const std::vector<int> &spidIndex,bool force_positive)
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
  setParam();
}

void CompiledFunklet::do_update (const double values[],const std::vector<int> &spidIndex,const std::vector<double> &constraints_min,const std::vector<double> &constraints_max,bool force_positive)
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
  setParam();
}




}//namespace Meq
