//# Functional.cc: Calculates result from string (see Aips++ CompiledFunction) 
//# describing function. Paramters in the string are given by the children.
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
//# $Id:
#include <MeqNodes/Functional.h>
#include <MEQ/Request.h>
#include <MEQ/AID-Meq.h>

#include <MEQ/VellSet.h>
#include <MEQ/Vells.h>


using namespace Meq::VellsMath;
namespace Meq {


  const string NotAvailableString="Not Available";
  
  Functional::Functional()
    : TensorFunction(),
      function_string_(NotAvailableString),
      shapes_(0),
      childnr_(0),
      vellsnr_(0)
  {
    Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex
    itsComplexFunction = new casa::CompiledFunction<casa::DComplex>();
    itsRealFunction = new casa::CompiledFunction<double>();
    //setFunction etc...
    for(int j=0;j<MaxNrDims;j++)
      for(int i=0;i<MaxNrDims;i++)
	MaxN_[i][j]=0;
  }
    
  Functional::~Functional()
  {
    Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex

    delete itsComplexFunction;
    delete itsRealFunction;
  }


  void Functional::setStateImpl (DMI::Record::Ref &rec,bool initializing)
  {
    TensorFunction::setStateImpl(rec,initializing);
    if(rec->hasField(FFunction))
      {
	rec[FFunction].get(function_string_,initializing);  
	//map_parameters(function_string_);//change function_string to AIPS++ interpretable thing and map variables, do this at python side??
	setFunction(function_string_);
	
      }
    int Ndim=0;
    if(rec->hasField(FChildMap))
      {
	//GET CHILDMAP
	//	std::vector<DMI::Record::Ref> childmap;
	//FailWhen(!rec[FChildMap].get_vector(childmap,0),"childmap incorrect type");
	const DMI::Vec * childmap = rec[FChildMap].as_po<DMI::Vec>();
	std::vector<int> mapv;
	int childnr;
	Ninput_=0;
	Ndim = childmap->size();
	FailWhen(Ndim >MaxNrDims,"Nr. of children is exceeding maximum");
	childnr_.resize(Ndim);
	for(int i=0;i<Ndim;i++){
	  childmap->as<DMI::Record>(i)[AidChild|AidNum].get(childnr,0);
	  childmap->as<DMI::Record>(i)[AidIndex].get_vector(mapv,0);
	  
	  map_parameters(i,childnr,mapv);
	}
	//Ninput is max of first elements of all mapv
      }
    FailWhen(Ndim_>Ndim,"Too few children specified");
  }
      

  void Functional::map_parameters(int dimnr,int childnr,const std::vector<int> & mapv){
    uint size = mapv.size();
    if(!size) return;
    if(childnr_.size()<=uint(dimnr)) childnr_.resize(dimnr+1);
    childnr_[dimnr]=childnr;
    if((childnr+1)>Ninput_) Ninput_=childnr+1;
    if(vellsnr_.size()<=uint(dimnr)) vellsnr_.resize(dimnr+1);
    //we do not know shapes of children here, so save the indices
    vellsnr_[dimnr]=mapv;
    Ndims_[childnr]=size;
    for(uint i=0;i<size;i++)
      MaxN_[childnr][i]=std::max(vellsnr_[dimnr][i],MaxN_[childnr][i]);
  }

 


  void Functional::setFunction(const string &funcstring){
    //check if this is a valid string
    Thread::Mutex::Lock lock(aipspp_mutex); // AIPS++ is not thread-safe, so lock mutex
    FailWhen(!itsComplexFunction->setFunction(funcstring),std::string(itsComplexFunction->errorMessage()));
    FailWhen(!itsRealFunction->setFunction(funcstring),std::string(itsRealFunction->errorMessage()));
    Ndim_ = itsRealFunction->ndim();
    
    
  }

  LoShape Functional::getResultDims (const vector<const LoShape *> &input_dims)
  {
    //check ifinput_dims have correct shape
    
    FailWhen(function_string_ == NotAvailableString,"No Function available");
    Assert(input_dims.size()>=uint(Ninput_));
    
    shapes_.resize(Ninput_);
    for(int i=0;i<Ninput_;i++)
      {
	const LoShape dim = *(input_dims[i]);
	FailWhen(dim.size() && dim.size()!=Ndims_[i],"child : wrong dimensions");
	shapes_[i]=dim;
	for(int j= 0;j<Ndims_[i] && j<dim.size();j++)
	  FailWhen(dim[j]<MaxN_[i][j],"child : wrong shape");

    
      }
  
    return LoShape();
    //MXM implement more dimensions lateron

  }
    
  void Functional::evaluateTensors (std::vector<Vells> & out,   
				    const std::vector<std::vector<const Vells *> > &args )
  {
    FailWhen(function_string_ == NotAvailableString,"No Function available");
    
    std::vector<Vells::Ref>  out_args(Ndim_);
    int all_real(0),all_complex(0);

    int arraynr_[Ndim_];
    const Vells::Shape * shapes[Ndim_];
    Vells::Ref vref;
    for(int dim_nr=0;dim_nr<Ndim_;dim_nr++)
      {

	//get arraynr_
	vector<int> mapv = vellsnr_[dim_nr];
	LoShape shape = shapes_[childnr_[dim_nr]];
	arraynr_[dim_nr]=0;
	for(int imap = 0; imap<mapv.size()-1;imap++)
	  arraynr_[dim_nr]+=shape[imap]*mapv[imap];
	arraynr_[dim_nr]+=mapv.back();
	


	const Vells * tmp_vells  = args[childnr_[dim_nr]][arraynr_[dim_nr]];
	if(tmp_vells->isReal()) all_real++;
	else all_complex++;
	vref<<= tmp_vells;
	out_args[dim_nr]=vref;
	shapes[dim_nr]=&(out_args[dim_nr]->shape());
      }
    Vells::Strides      *strides;
    strides = new Vells::Strides[Ndim_];
    Vells::Shape outshape;
    if(all_complex != Ndim_ && all_real!=Ndim_)
      {
	//loop once more to create pointers to the new vells
	for(int dim_nr=0;dim_nr<Ndim_;dim_nr++)
	  if(out_args[dim_nr]->isReal()){
	    vref <<= new Vells(tocomplex(out_args[dim_nr](),0.));
	    out_args[dim_nr]=vref;
	    shapes[dim_nr]=&(out_args[dim_nr]->shape());
	  }
	
      }
    //loop with strided iterators here
    Vells::computeStrides(outshape,strides,Ndim_,shapes,"Functional::evaluateTensors");
    
    
    try{
      if( all_real== Ndim_ )
	fill_double_xval(out,out_args,outshape,strides);
      else
	fill_complex_xval(out,out_args,outshape,strides);
    //    out[0] = (*itsFunction)(xval);
    }
    catch(...)
      {
	delete strides;
	return;
      }
    delete strides;
    
  }


  void Functional::fill_complex_xval(std::vector<Vells> & out,const std::vector<Vells::Ref>  &args,const Vells::Shape &outshape,const Vells::Strides * strides_)
{


  Vells::DimCounter counter(outshape);
  std::vector<Vells::ConstStridedIterator<dcomplex> > strided_iter(Ndim_);
  for(int i =0; i<Ndim_;i++){
    strided_iter[i]= Vells::ConstStridedIterator<dcomplex>(*(args[i]),strides_[i]);
  }
  complex<double> xval[Ndim_];
  Vells & output = out[0];
//// OMS 19/12/06: the line below used to say:
//  output=Vells(reinterpret_cast<dcomplex> (*reinterpret_cast<dcomplex*>(&xval[0])),outshape,false);
//// which I don't understand. Why the double cast??. gcc4 trips up over it. In any case, since the
//// third argument('init') = false, the actual value does not matter, so it's easier to just
//// pass in a dcomplex 0.
  output=Vells(make_dcomplex(0),outshape,false);
  dcomplex * res = output.getStorage<dcomplex>();
  while(true){
    for(int i =0; i<Ndim_;i++)
      xval[i]=*(reinterpret_cast<const complex<double> *>(&*(strided_iter[i])));
    complex<double> result = (*itsComplexFunction)(xval);
    *res = *(reinterpret_cast<dcomplex*>(&result));
    res++;
    int ndim = counter.incr(); 
    if( !ndim )    // break out when counter is finished
      break;
    for(int i =0; i<Ndim_;i++)
      strided_iter[i].incr(ndim);

  }
  }



  void Functional::fill_double_xval(std::vector<Vells> & out,const std::vector<Vells::Ref>  &args,const Vells::Shape &outshape,const Vells::Strides * strides_)
{


  Vells::DimCounter counter(outshape);
  std::vector<Vells::ConstStridedIterator<double> > strided_iter(Ndim_);
  for(int i =0; i<Ndim_;i++){
    strided_iter[i]= Vells::ConstStridedIterator<double>(*(args[i]),strides_[i]);
    
  }
  double xval[Ndim_];
  Vells & output = out[0];
  output=Vells(xval[0],outshape,false);
  double * res = out[0].getStorage<double>();
  while(true){
    for(int i =0; i<Ndim_;i++)
	xval[i]=*(strided_iter[i]);
    *res= (*itsRealFunction)(xval);
    res++;
    int ndim = counter.incr(); 
    if( !ndim )    // break out when counter is finished
      break;
    for(int i =0; i<Ndim_;i++)
      strided_iter[i].incr(ndim);

  }
  }
  
  
} // namespace Meq
 
