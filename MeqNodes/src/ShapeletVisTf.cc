//# ShapeletVisTf.cc: modifies request resolutions
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
//# $Id: ShapeletVisTf.cc,v 1.11 2006/05/30 16:44:32 sarod Exp $

#include <MeqNodes/ShapeletVisTf.h>
#include <MEQ/MeqVocabulary.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MEQ/VellsSlicer.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>


//#define DEBUG 
namespace Meq {

const HIID FFilename= AidFilename;
const HIID FCutoff= AidCutoff;

//const HIID FResolutionId         = AidResolution|AidId;
const HIID FResolutionSymdeps    = AidResolution|AidSymdeps;
const HIID FSequenceSymdeps = AidSequence|AidSymdeps;
const HIID symdeps_all[] = { FDomain,FResolutionSymdeps,FState,FIteration,FSequenceSymdeps };

//##ModelId=400E5355029C
ShapeletVisTf::ShapeletVisTf()
: Node(0),n0_(-1),cutoff_(0) // no children expected
{

}

//##ModelId=400E5355029D
ShapeletVisTf::~ShapeletVisTf()
{}

void ShapeletVisTf::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);


  setActiveSymDeps(symdeps_all,5);
	//never cache
	setCachePolicy(Node::CACHE_NEVER);

	rec[FFilename].get(filename_,initializing);
#ifdef DEBUG
  cout<<"File Name ="<<filename_<<endl;
#endif

	if(rec[FCutoff].get(cutoff_,initializing)) {
#ifdef DEBUG
   cout<<"Cutoff ="<<cutoff_<<endl;
#endif
	}
}


int ShapeletVisTf::getResult (Result::Ref &resref, 
                       const std::vector<Result::Ref> &childres,
                       const Request &request,bool)
{

  if ( request.requestType() ==RequestType::DISCOVER_SPIDS 
	|| request.requestType() ==RequestType::PARM_UPDATE ) {  
		resref<<=new Result(0);
		resref().setCells(request.cells());
		return 0;
	}
  if ( !request.hasCells()) {
		resref<<=new Result(0);
		return 0;
  }


	//read decomposition file, only if not done so
	if(n0_==-1) {
  double *mc;
  FILE *dfp=fopen(filename_.c_str(),"r");
	fread(&beta_,sizeof(double),(size_t)1,dfp);
	fread(&n0_,sizeof(int),(size_t)1,dfp);
	//allocate memory for modes
	if ((mc=(double*)calloc((size_t)(n0_*n0_),sizeof(double)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}
	fread(mc,sizeof(double),(size_t)n0_*n0_,dfp);
	//read image grid
	int Nx,Ny;
	double *x, *y;

	fread(&Nx,sizeof(int),(size_t)1,dfp);
	if ((x=(double*)calloc((size_t)(Nx),sizeof(double)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}
	fread(x,sizeof(double),(size_t)Nx,dfp);
	fread(&Ny,sizeof(int),(size_t)1,dfp);
	if ((y=(double*)calloc((size_t)(Ny),sizeof(double)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}
	fread(y,sizeof(double),(size_t)Ny,dfp);

	fclose(dfp);

	//create blitz array for modes
	md_.resize(n0_,n0_);//array of modes
	blitz::Array<double,2> tmpm_(mc,blitz::shape(n0_,n0_),blitz::neverDeleteData);
	md_=tmpm_;

	//a little quirck: the shapelet decom was done on a RA,Dec grid. In the l,m 
	//grid the sign of l is reversed. So we need to change the coefficients to 
	//the l,m grid. This means each coeff has to be multiplied bu (-1)^n1
	// where n1 is the order of the basis functio in l axis
	//for (int i=1; i<n0_; i+=2) 
  // md_(blitz::Range::all(),i)=-tmpm_(blitz::Range::all(),i);

	blitz::Array<double,1> x_(x,blitz::shape(Nx),blitz::neverDeleteData);
	blitz::Array<double,1> y_(y,blitz::shape(Ny),blitz::neverDeleteData);
	free(mc);
	free(x);
	free(y);
	
	if (cutoff_ != 0) beta_=cutoff_;
#ifndef DEBUG
	cout<<"Modes="<<n0_<<" beta="<<beta_<<endl;
	cout<<"Coeff "<<endl;
	cout<<md_<<endl;
#endif
	}
	const Cells &incells=request.cells();
	//get U,V axes
	blitz::Array<double,1> uax=incells.center(Axis::axis("U"));
	blitz::Array<double,1> vax=incells.center(Axis::axis("V"));
	//note: we decompose f(-l,m) so the Fourier transform is F(-u,v)
	//so negate the u grid
	uax=-uax;
#ifdef DEBUG
	cout<<"Grid "<<endl;
	cout<<uax<<endl;
	cout<<vax<<endl;
#endif
	double *u=uax.data();
	double *v=vax.data();
	int Nu=uax.extent(0);
	int Nv=vax.extent(0);


	double *UV;
	int *cplx;

	if (Nu==1 && Nv==1) {
#ifdef DEBUG
	 cout<<"scalar case "<<endl;
#endif
	 calculate_uv_mode_vectors_scalar(u,Nu,v,Nv,beta_,n0_,&UV,&cplx);
  } else {
	calculate_uv_mode_vectors(u,Nu,v,Nv,beta_,n0_,&UV,&cplx);
	}

	blitz::Array<double,4> M(UV,blitz::shape(n0_,n0_,Nv,Nu),blitz::neverDeleteData);
	blitz::Array<int,2> Ca(cplx,blitz::shape(n0_,n0_),blitz::neverDeleteData);

	M.transposeSelf(3,2,1,0);
#ifdef DEBUG
	cout<<"Fund "<<M(blitz::Range::all(),blitz::Range::all(),0,0)<<endl;
#endif
	Ca.transposeSelf(1,0);

	Result &result=resref<<= new Result(1,0);

	//create new cells with collapsed axis
	const Domain &old_dom=incells.domain();
	Domain::Ref domain(new Domain());
	domain().defineAxis(Axis::TIME, old_dom.start(Axis::TIME), old_dom.end(Axis::TIME));
	domain().defineAxis(Axis::FREQ, old_dom.start(Axis::FREQ), old_dom.end(Axis::FREQ));
	domain().defineAxis(Axis::axis("U"), old_dom.start(Axis::axis("U")), old_dom.end(Axis::axis("U")));
	domain().defineAxis(Axis::axis("V"), old_dom.start(Axis::axis("V")), old_dom.end(Axis::axis("V")));
	Cells::Ref outcells_ref;
	Cells &outcells=outcells_ref<<=new Cells(*domain);

	outcells.setCells(Axis::TIME, old_dom.start(Axis::TIME), old_dom.end(Axis::TIME), 1);
	outcells.setCells(Axis::FREQ, old_dom.start(Axis::FREQ), old_dom.end(Axis::FREQ), 1);

	outcells.setCells(Axis::axis("U"), incells.center(Axis::axis("U")), incells.cellSize(Axis::axis("U")));
	outcells.setCells(Axis::axis("V"), incells.center(Axis::axis("V")), incells.cellSize(Axis::axis("V")));

	VellSet::Ref vref;
	VellSet &vs=vref<<= new VellSet(0,1);

	Vells realv(0.0,outcells.shape());
	Vells imagv(0.0,outcells.shape());
	VellsSlicer<double,2> rlsl(realv,Axis::axis("U"),Axis::axis("V"));
	VellsSlicer<double,2> imsl(imagv,Axis::axis("U"),Axis::axis("V"));
	blitz::Array<double,2> realsum(Nu,Nv);
	blitz::Array<double,2> imagsum(Nu,Nv);
	realsum=0;
	imagsum=0;
	for (int n1=0; n1<n0_; n1++) {
	 for (int n2=0; n2<n0_; n2++) {
#ifdef DEBUG
		cout<<"Mode "<<n1<<","<<n2<<": "<<md_(n1,n2)<<" complx :"<<Ca(n1,n2)<<endl;
#endif
		if (Ca(n1,n2)) {
	    imagsum+=M(blitz::Range::all(),blitz::Range::all(),n1,n2)*md_(n1,n2);
		} else {
	    realsum+=M(blitz::Range::all(),blitz::Range::all(),n1,n2)*md_(n1,n2);
		}
	 }
	}
	rlsl=realsum;
	imsl=imagsum;

	Vells &out=vs.setValue(new Vells(VellsMath::tocomplex(realv,imagv)));
	vs.setShape(outcells.shape());
	result.setVellSet(0,vref);
	result.setCells(outcells);

	free(cplx);
	free(UV);
  return 0;
}


} // namespace Meq
