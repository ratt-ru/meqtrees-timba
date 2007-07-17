//# Private.cc: Private 2 or more nodes
//#
//# Copyright (C) 2003
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
//# $Id: Private.cc$
#include <MeqNodes/PrivateFunction.h>



using namespace Meq::VellsMath;
namespace Meq {    

PrivateFunction::PrivateFunction()
{
  allowMissingData();
  pt2doubleFunc = 0;
  pt2complexFunc = 0;
  Npar=Nx=0; 
  handle=0;
}


//##ModelId=3F86886E0293
PrivateFunction::~PrivateFunction()
{
    if(handle) 
      dlclose(handle);
}



  void  PrivateFunction::init_functions(const string  &lib_name, const string & function_name){

    if(handle) 
      dlclose(handle);
    handle = dlopen (lib_name.c_str(), RTLD_LAZY);
    FailWhen(!handle, dlerror());
    dlerror();    /* Clear any existing error */
    
    char double_name[1000];
    char complex_name[1000];
    sprintf(double_name,"%s_double",function_name.c_str());
    sprintf(complex_name,"%s_complex",function_name.c_str());

    *(void **) (&pt2doubleFunc) = dlsym(handle,double_name);
    if(dlerror() !=NULL){
      pt2doubleFunc=0;
      
    }
    if(!pt2doubleFunc){
      *(void **) (&pt2doubleFunc) = dlsym(handle,function_name.c_str());
      if(dlerror() !=NULL){
	pt2doubleFunc=0;
	
      }
    }
    *(void **) (&pt2complexFunc) = dlsym(handle,complex_name);
    if(dlerror() !=NULL){
      pt2complexFunc=0;
      
    }
    FailWhen(!pt2complexFunc && !pt2doubleFunc,"Cannot find function (double or complex)");
    Nx=1;
    Npar=1;
    
    char N_x[1000];
    char N_par[1000];
    sprintf(N_x,"Nx_%s",function_name.c_str());
    sprintf(N_par,"Npar_%s",function_name.c_str());
    
    int *N;
    N  = (int *)dlsym(handle,N_x);
    FailWhen(dlerror() !=NULL,"Nx_<function_name> must be specified");
    Nx = *N;
    FailWhen(Nx>Axis::MaxAxis,"Nx too large");
    N = (int *)dlsym(handle,N_par);
    FailWhen(dlerror() !=NULL,"Npar_<function_name> must be specified");
    Npar = *N;

}











//##ModelId=400E53040332
Vells PrivateFunction::evaluate (const Request& request, const LoShape& ,
			 const vector<const Vells*>& values)
{

  FailWhen(values.size() !=uint(Npar),"Number of children not equal to Npar");

  //get grid from request, as in MeqFreq
  vector<Vells::Ref> grid;
  grid.resize(Nx);
  const Cells& cells = request.cells();
  uint isComplex=0;
  std::vector<Vells::Ref>  out_args(Npar);
  for(uint i=0;i<values.size();i++)
    {
      if(values[i]->isComplex()) isComplex++;
      out_args[i]<<=values[i];
    }
  FailWhen(isComplex>0 && !pt2complexFunc,"Got complex Vells and no complex function defined");
    

  if(isComplex>0 && isComplex<values.size()){
    //loop once more to create pointers to the new vells
    Vells::Ref vref;
    for(uint i=0;i<out_args.size();i++)
      if(out_args[i]->isReal()){
	vref <<= new Vells(tocomplex(out_args[i](),0.));
	out_args[i]=vref;
      }
  }
  for(int axisi=0;axisi<Nx;axisi++){
    HIID axis = Axis::axisId(axisi);

    if( cells.isDefined(axisi) )
      {
	Vells::Shape shape;
	Axis::degenerateShape(shape,cells.rank());
	int nc = shape[axisi] = cells.ncells(axisi);
	grid[axisi] <<=new  Vells(0,shape,false);
	memcpy(grid[axisi]().realStorage(),cells.center(axisi).data(),nc*sizeof(double));
      }
    else
      grid[axisi] <<=new  Vells(0.);
  }


  int Ndim_=Npar+Nx;
  const Vells::Shape * shapes[Ndim_];
  for(int i=0;i<Nx;i++)
       shapes[i]=&(grid[i]->shape());
  for(int i=Nx;i<Ndim_;i++)
       shapes[i]=&(out_args[i-Nx]->shape());

  // create strides
  Vells::Strides *strides = new Vells::Strides[Ndim_];

  // Compute strides
  Vells::Shape outshape;
  Vells::computeStrides(outshape,strides,Ndim_,shapes,"Functional::evaluateTensors");
 
  Vells output;
  if(isComplex>0)
    
    output= evaluateComplex(grid,out_args, outshape,strides);
  else
    output= evaluateDouble(grid,out_args, outshape,strides);
  delete strides;
  return output; 
}

Vells PrivateFunction::evaluateDouble(const std::vector<Vells::Ref>  &grid,const std::vector<Vells::Ref>  &values,const Vells::Shape &outshape,const Vells::Strides * strides){
  int Ndim_=Nx+Npar;
  //create iterators
  Vells::DimCounter counter(outshape);
  std::vector<Vells::ConstStridedIterator<double> > strided_iter(Ndim_);
  for(int i =0; i<Nx;i++){
    strided_iter[i]= Vells::ConstStridedIterator<double>(grid[i],strides[i]);
    
  }
  for(int i =Nx; i<Ndim_;i++){
    strided_iter[i]= Vells::ConstStridedIterator<double>(*(values[i-Nx]),strides[i]);
    
  }
  
  //now loop over your vells
  Vells output =  Vells(0.,outshape);
  double * res = output.getStorage<double>();
  double x[Nx];
  double par[Npar];
  while(true){
    for(int i =0; i<Nx;i++)
      //do some calculation
      x[i]=  *(strided_iter[i]);
    for(int i =Nx; i<Ndim_;i++)
      //do some calculation
      par[i-Nx]=  *(strided_iter[i]);
    *res = pt2doubleFunc(par,x);
    //to next point in my output
    res++;
    //increment iterators
    int ndim = counter.incr(); 
    if( !ndim )    // break out when counter is finished
      break;
    for(int i =0; i<Ndim_;i++)
      strided_iter[i].incr(ndim);

  }
  return output;


}


Vells PrivateFunction::evaluateComplex(const std::vector<Vells::Ref>  &grid,const std::vector<Vells::Ref>  &values,const Vells::Shape &outshape,const Vells::Strides * strides){
  
  int Ndim_=Nx+Npar;
  //create iterators
  Vells::DimCounter counter(outshape);
  std::vector<Vells::ConstStridedIterator<dcomplex> > strided_iter(Ndim_);
  Vells::Ref vref;
  std::vector<Vells::Ref> ngrid;
  ngrid.resize(Nx);
  
  for(int i =0; i<Nx;i++){
    vref <<= new Vells(tocomplex(grid[i],0.));
    ngrid[i]=vref;
    strided_iter[i]= Vells::ConstStridedIterator<dcomplex>(ngrid[i],strides[i]);
    
  }
  for(int i =Nx; i<Ndim_;i++){
    strided_iter[i]= Vells::ConstStridedIterator<dcomplex>(*(values[i-Nx]),strides[i]);
    
  }
  
  //now loop over your vells
  Vells output =  Vells(make_dcomplex(0.),outshape);
  dcomplex * res = output.getStorage<dcomplex>();
  dcomplex x[Nx];
  dcomplex par[Npar];
  while(true){
    for(int i =0; i<Nx;i++)
      //do some calculation
      x[i]=  *(strided_iter[i]);
    for(int i =Nx; i<Ndim_;i++)
      //do some calculation
      par[i-Nx]=  *(strided_iter[i]);
    *res = pt2complexFunc(par,x);
    //to next point in my output
    res++;
    //increment iterators
    int ndim = counter.incr(); 
    if( !ndim )    // break out when counter is finished
      break;
    for(int i =0; i<Ndim_;i++)
      strided_iter[i].incr(ndim);

  }
  return output;

  

}



void PrivateFunction::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Function::setStateImpl(rec,initializing);
  string nml;
  string nmf;
  
  FailWhen( !rec[FLibName].get(nml,0),"no library name specified" );
  FailWhen( !rec[FFunctionName].get(nmf,0),"no function name specified" );
  init_functions(nml,nmf);

}


} // namespace Meq
