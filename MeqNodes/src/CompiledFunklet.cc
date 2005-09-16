#include <Common/Profiling/PerfProfile.h>

#include "CompiledFunklet.h"
#include <MEQ/Request.h>
#include <MEQ/VellSet.h>
#include <MEQ/MeqVocabulary.h>
#include <Common/Debug.h>
#include <Common/lofar_vector.h>
#include <cstdlib>
#include <cmath>

namespace Meq {

static DMI::Container::Register reg(TpMeqCompiledFunklet,true);

CompiledFunklet::CompiledFunklet(double pert,double weight,DbId id)
  : Funklet(pert,weight,id)
{
     if(hasField(FFunction)){
	string fstr;
	(*this)[FFunction].get(fstr,0);
	
	setFunction(fstr);
      }
    itsState<<=new Funklet(*this);
}


CompiledFunklet::CompiledFunklet (const DMI::Record &other,int flags,int depth)
  : Funklet(other,flags,depth)
{
  
  if(hasField(FFunction)){
    string fstr;
    (*this)[FFunction].get(fstr,0);
    
    setFunction(fstr);
  }
  itsState<<=new Funklet(*this);
 }

CompiledFunklet::CompiledFunklet (const CompiledFunklet &other,int flags,int depth)
  : Funklet(other,flags,depth),
    itsDerFunction(other.itsDerFunction),
    itsFunction(other.itsFunction)
  {
    

    itsState<<=new Funklet(*this);
  }


  int CompiledFunklet::dependsOn(int i){
    //to be implemented
    return 1;
  }
  
  void CompiledFunklet::fill_values(double *value, double * pertValPtr[],double *xval,const Vells::Shape & res_shape ,const int dimN, const LoVec_double grid[],const std::vector<double> &perts, const std::vector<int> &spidIndex, const int makePerturbed, int &pos) const
{
   
  casa::AutoDiff<casa::Double> thederval;
    for(int i=0;i<res_shape[dimN];i++){
      xval[dimN]=grid[dimN](i);
      if(dimN<Ndim-1){
	fill_values(value,pertValPtr,xval,res_shape,dimN+1,grid,perts,spidIndex,makePerturbed,pos);
      }
      else{//the real filling
	if( makePerturbed ) 
	  {
	    thederval = itsDerFunction(xval);
	    value[pos] = thederval.value();
	    for( uint ispid=0; ispid<spidIndex.size(); ispid++) 
	      if( spidIndex[ispid] >= 0 ){
		int d=1;
		//fill perturbed
		double deriv=thederval.derivatives()[ispid];
		for( int ipert=0; ipert<makePerturbed; ipert++ ,d=-d)
		  {
		    //	      cdebug(0)<<"der "<<ispid<<" : "<<deriv<<endl;
		    ((pertValPtr[ipert*spidIndex.size()+ispid][pos])) = d*deriv*perts[ispid]+ thederval.value();
		  }
	      }
	  }
	else
	  {//not solvable use simple function instead
	    value[pos] = itsFunction(xval);
	    
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
  int ndim = itsFunction.ndim();

  LoVec_double grid[ndim];
  if(ndim==0){
    //constant 
    if( makePerturbed )
      {
	const casa::AutoDiff<casa::Double> thederval = itsDerFunction();
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
	vs.setValue(new Vells(itsFunction(),false));
      }
    return;
  }



  for(int i=0;i<ndim;i++)
    {
  

      int iaxis = getAxis(i);
      FailWhen(!cells.isDefined(iaxis),
            "Meq::CompiledFunklet: axis " + Axis::axisId(iaxis).toString() + 
            " is not defined in Cells");
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



void CompiledFunklet::do_update (const double values[],const std::vector<int> &spidIndex)
{
  Thread::Mutex::Lock lock(mutex());
  double* coeff = static_cast<double*>(coeffWr().getDataPtr());
  for( uint i=0; i<spidIndex.size(); i++ ) 
  {
    if( spidIndex[i] >= 0 ) 
      {
	cdebug(3)<<"updateing polc "<< coeff[i]<<" adding "<< values[spidIndex[i]]<<spidIndex[i]<<endl;
	coeff[i] += values[spidIndex[i]];
	setParam();
      }
  }
  itsState().setCoeff(this->coeff());
}




}
