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

#define AX1 "L"
#define AX2 "M"

//#define DEBUG 
namespace Meq {

const HIID FFilename= AidFilename;
const HIID FCutoff= AidCutoff;
const HIID FMethod = AidMethod;
const HIID child_labels[] = { AidModes };
const int num_children = sizeof(child_labels)/sizeof(child_labels[0]);



//const HIID FResolutionId         = AidResolution|AidId;
const HIID FResolutionSymdeps    = AidResolution|AidSymdeps;
const HIID FSequenceSymdeps = AidSequence|AidSymdeps;
const HIID symdeps_all[] = { FDomain,FResolutionSymdeps,FState,FIteration,FSequenceSymdeps };

//##ModelId=400E5355029C
ShapeletVisTf::ShapeletVisTf()
: TensorFunction(num_children,child_labels) //only one child
{
 cutoff_=0.0;
 method_=0; //default rectangular
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

//	rec[FFilename].get(filename_,initializing);
#ifdef DEBUG
 // cout<<"File Name ="<<filename_<<endl;
#endif

	if(rec[FMethod].get(method_,initializing)) {
#ifdef DEBUG
   cout<<"method="<<method_<<endl;
#endif
   if (method_>1) method_=0; //default
	}
}


void ShapeletVisTf::computeResultCells (Cells::Ref &ref,const std::vector<Result::Ref> &,const Request &request)
{
  // NB: for the time being we only support scalar child results, 
  // and so we ignore the child cells, and only use the request cells
  // (while checking that they have a time axis)
  const Cells &incells = request.cells();
	//create new cells with collapsed axis
	const Domain &old_dom=incells.domain();
	Domain::Ref domain(new Domain());
	domain().defineAxis(Axis::TIME, old_dom.start(Axis::TIME), old_dom.end(Axis::TIME));
	domain().defineAxis(Axis::FREQ, old_dom.start(Axis::FREQ), old_dom.end(Axis::FREQ));
	domain().defineAxis(Axis::axis(AX1), old_dom.start(Axis::axis(AX1)), old_dom.end(Axis::axis(AX1)));
	domain().defineAxis(Axis::axis(AX2), old_dom.start(Axis::axis(AX2)), old_dom.end(Axis::axis(AX2)));
	Cells::Ref outcells_ref;
	Cells &outcells=outcells_ref<<=new Cells(*domain);

	outcells.setCells(Axis::TIME, old_dom.start(Axis::TIME), old_dom.end(Axis::TIME), 1);
	outcells.setCells(Axis::FREQ, old_dom.start(Axis::FREQ), old_dom.end(Axis::FREQ), 1);

	outcells.setCells(Axis::axis(AX1), incells.center(Axis::axis(AX1)), incells.cellSize(Axis::axis(AX1)));
	outcells.setCells(Axis::axis(AX2), incells.center(Axis::axis(AX2)), incells.cellSize(Axis::axis(AX2)));


  ref.attach(outcells);
}
 
LoShape ShapeletVisTf::getResultDims (const vector<const LoShape *> &input_dims)
{
  Assert(input_dims.size()>=1);
  // result is a single vellset
  return LoShape(1);
}

//#define DEBUG
void ShapeletVisTf::evaluateTensors (std::vector<Vells> & out,
                            const std::vector<std::vector<const Vells *> > &args)
{
  //get child values: beta, then modes
  //calculate num of vellsets
  int nvells=args[0].size();
#ifdef DEBUG
 std::cout<<"args= "<<args.size()<<std::endl;
 std::cout<<"Vellsets= "<<nvells<<std::endl;
#endif
  const Vells &vbeta=*(args[0][0]);
  double beta_=vbeta.getScalar<double>();
  //modes
  int nmodes=nvells-1; // first one is beta

	const Cells &incells=resultCells();
	//get U,V axes
	blitz::Array<double,1> uax=incells.center(Axis::axis(AX1));
	blitz::Array<double,1> vax=incells.center(Axis::axis(AX2));


#ifdef DEBUG
	cout<<"Grid "<<endl;
	cout<<uax<<endl;
	cout<<vax<<endl;
#endif
	double *u=uax.data();
	double *v=vax.data();
  int ntime = incells.ncells(Axis::TIME);
  int nfreq = incells.ncells(Axis::FREQ);
	int Nu=uax.extent(0);
	int Nv=vax.extent(0);
#ifdef DEBUG
  cout<<"Cells (t,f,u,v)"<<ntime<<" "<<nfreq<<" "<<Nu<<" "<<Nv<<endl;
#endif


/////////////////////////////////////////////////////////////////////////
///// rectangular method

  if (!method_) {
  int n0_=(int)sqrt(nmodes);
#ifdef DEBUG
 std::cout<<"Rectangular Modes = "<<n0_<<std::endl;
#endif
	//note: we decompose f(-l,m) so the Fourier transform is F(-u,v)
	//so negate the u grid
	uax=-uax;

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

  // M : U,V,n0,n0
	M.transposeSelf(3,2,1,0);
#ifdef DEBUG
	cout<<"Fund "<<M(blitz::Range::all(),blitz::Range::all(),0,0)<<endl;
#endif
  //Ca: n0,n0
	Ca.transposeSelf(1,0);


  //read in mode params
  double *mc;
	//allocate memory for modes
	if ((mc=(double*)calloc((size_t)(nmodes),sizeof(double)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}
  for (int ci=0; ci<nmodes; ci++) {
   const Vells &vmode=*(args[0][ci+1]);
   mc[ci]=vmode.getScalar<double>();
  }
	blitz::Array<double,2> md_(mc,blitz::shape(n0_,n0_),blitz::neverDeleteData);
	md_.transposeSelf(1,0);

	Vells realv(0.0,incells.shape());
	Vells imagv(0.0,incells.shape());

  
  double* datar = realv.realStorage();
  double* datai = imagv.realStorage();
	blitz::Array<double,4> realsum(datar,blitz::shape(ntime,nfreq,Nu,Nv));
	blitz::Array<double,4> imagsum(datai,blitz::shape(ntime,nfreq,Nu,Nv));

  for (int ci=0; ci<ntime; ci++) {
    for (int cj=0; cj<nfreq; cj++) {
          //get a uv slice for this time,freq
          blitz::Array<double,2> A=realsum(ci,cj,blitz::Range::all(),blitz::Range::all());  
          blitz::Array<double,2> B=imagsum(ci,cj,blitz::Range::all(),blitz::Range::all());  
	        A=0;
	        B=0;
	        for (int n1=0; n1<n0_; n1++) {
	          for (int n2=0; n2<n0_; n2++) {
#ifdef DEBUG
		cout<<"Mode "<<n1<<","<<n2<<": "<<md_(n1,n2)<<" complx :"<<Ca(n1,n2)<<endl;
#endif
		        if (Ca(n1,n2)) {
	            B+=M(blitz::Range::all(),blitz::Range::all(),n1,n2)*md_(n1,n2);
		        } else {
	            A+=M(blitz::Range::all(),blitz::Range::all(),n1,n2)*md_(n1,n2);
		       }
	        }
         }
       //F=make_dcomplex(realsum,imagsum);
       //blitz::real(F)=realsum;
       //blitz::imag(F)=imagsum;
   }
  }


	out[0]=Vells((VellsMath::tocomplex(realv,imagv)));
	free(cplx);
	free(UV);
  free(mc);

  } else {
  //////////////////////////////////////////////////////
  /////// polar method
  int n0_=(int)((sqrt(8.0*nmodes+1.0)-1)/2.0);
#ifdef DEBUG
 std::cout<<"Polar Modes = ="<<n0_<<", total="<<nmodes<<std::endl;
#endif


	Vells realv(0.0,incells.shape());
	Vells imagv(0.0,incells.shape());
  double* datar = realv.realStorage();
  double* datai = imagv.realStorage();
	blitz::Array<double,4> realsum(datar,blitz::shape(ntime,nfreq,Nu,Nv));
	blitz::Array<double,4> imagsum(datai,blitz::shape(ntime,nfreq,Nu,Nv));

	 double *UVr, *UVi;
   //NB: u,v axes are azimuth, elevation: theta,r in polar in practice
   calculate_polar_mode_vectors(v, Nv, u, Nu, n0_,beta_, &UVr, &UVi);

 	 blitz::Array<double ,3> Mr(UVr,blitz::shape(nmodes,Nu,Nv),blitz::neverDeleteData);
 	 blitz::Array<double ,3> Mi(UVi,blitz::shape(nmodes,Nu,Nv),blitz::neverDeleteData);

  //U,V,mode
	Mr.transposeSelf(2,1,0);
	Mi.transposeSelf(2,1,0);
  //read in mode params (complex)
  dcomplex *mc;
	//allocate memory for modes
	if ((mc=(dcomplex*)calloc((size_t)(nmodes),sizeof(dcomplex)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}
  for (int ci=0; ci<nmodes; ci++) {
   const Vells &vmode=*(args[0][ci+1]);
   mc[ci]=vmode.getScalar<dcomplex>();
#ifdef DEBUG
   std::cout<<"mode "<<ci<<" = "<<creal(mc[ci])<<"+ j*"<<cimag(mc[ci])<<std::endl;
#endif
  }

  double tmpr,tmpi;
  for (int ci=0; ci<ntime; ci++) {
    for (int cj=0; cj<nfreq; cj++) {
    //each time,freq slice, iterate over modes
     blitz::Array<double,2> A=realsum(ci,cj,blitz::Range::all(),blitz::Range::all());  
     blitz::Array<double,2> B=imagsum(ci,cj,blitz::Range::all(),blitz::Range::all());  
	   A=0;
	   B=0;
     for (int n1=0; n1<nmodes; n1++) {
       tmpr=creal(mc[n1]); 
       tmpi=cimag(mc[n1]); 
       A+=(Mr(blitz::Range::all(),blitz::Range::all(),n1))*(tmpr)-(Mi(blitz::Range::all(),blitz::Range::all(),n1))*(tmpi);
       B+=(Mr(blitz::Range::all(),blitz::Range::all(),n1))*(tmpi)+(Mi(blitz::Range::all(),blitz::Range::all(),n1))*(tmpr);
       //A=(Mr(blitz::Range::all(),blitz::Range::all(),1));
       //B=(Mi(blitz::Range::all(),blitz::Range::all(),1));
       //A(ci,cj,blitz::Range::all(),blitz::Range::all())=(M(blitz::Range::all(),blitz::Range::all(),0));
     }
    }
  }
 
	 out[0]=Vells((VellsMath::tocomplex(realv,imagv)));
   free(UVr);
   free(UVi);
   free(mc);
  }
}

/*int ShapeletVisTf::getResult (Result::Ref &resref, 
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
	blitz::Array<double,1> uax=incells.center(Axis::axis(AX1));
	blitz::Array<double,1> vax=incells.center(Axis::axis(AX2));
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
	domain().defineAxis(Axis::axis(AX1), old_dom.start(Axis::axis(AX1)), old_dom.end(Axis::axis(AX1)));
	domain().defineAxis(Axis::axis(AX2), old_dom.start(Axis::axis(AX2)), old_dom.end(Axis::axis(AX2)));
	Cells::Ref outcells_ref;
	Cells &outcells=outcells_ref<<=new Cells(*domain);

	outcells.setCells(Axis::TIME, old_dom.start(Axis::TIME), old_dom.end(Axis::TIME), 1);
	outcells.setCells(Axis::FREQ, old_dom.start(Axis::FREQ), old_dom.end(Axis::FREQ), 1);

	outcells.setCells(Axis::axis(AX1), incells.center(Axis::axis(AX1)), incells.cellSize(Axis::axis(AX1)));
	outcells.setCells(Axis::axis(AX2), incells.center(Axis::axis(AX2)), incells.cellSize(Axis::axis(AX2)));

	VellSet::Ref vref;
	VellSet &vs=vref<<= new VellSet(0,1);

	Vells realv(0.0,outcells.shape());
	Vells imagv(0.0,outcells.shape());
	VellsSlicer<double,2> rlsl(realv,Axis::axis(AX1),Axis::axis(AX2));
	VellsSlicer<double,2> imsl(imagv,Axis::axis(AX1),Axis::axis(AX2));
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
} */


//////////////////////////// shapelet stuff
/* evaluate Hermite polynomial value using recursion
 *  */
inline double
H_e(double x, int n) {
  if(n==0) return 1.0;
  if(n==1) return 2*x;
  return 2*x*H_e(x,n-1)-2*(n-1)*H_e(x,n-2);
}

/** calculate the UV mode vectors (block version, needs at least 2 grid points)
 * in: u,v: arrays of the grid points in UV domain
 *      M: number of modes
 *      beta: scale factor
 *      n0: number of modes in each dimension
 * out:
 *      Av: array of mode vectors size Nu.Nv times n0.n0, in column major order
 *      cplx: array of integers, size n0*n0, if 1 this mode is imaginary, else real
 *
 */
int
calculate_uv_mode_vectors(double *u, int Nu, double *v, int Nv, double beta, int n0, double **Av, int **cplx) {

	double *grid;
	int *xindex,*yindex;
	int xci,yci,zci,Ntot;
	int *neg_grid;

	double **shpvl, *fact;
	int n1,n2,start;
	double pi_4r=1/sqrt(sqrt(M_PI));
	double xval,sqr_beta;
	int signval;

  /* image size: Nu by Nv pixels
   */
	/* allocate memory to store grid points */
  if ((grid=(double*)calloc((size_t)(Nu+Nv),sizeof(double)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}

  if ((xindex=(int*)calloc((size_t)(Nu),sizeof(int)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}
  if ((yindex=(int*)calloc((size_t)(Nv),sizeof(int)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}

	/* merge axes coordinates */
	xci=yci=zci=0;
	while(xci<Nu && yci<Nv ) {
	 if (u[xci]==v[yci]){
		/* common index */
		grid[zci]=u[xci];
		xindex[xci]=zci;
		yindex[yci]=zci;
	  zci++;
	  xci++;	 
	  yci++;	 
	 } else if (u[xci]<v[yci]){
		 grid[zci]=u[xci];
		 xindex[xci]=zci;
	   zci++;
	   xci++;	 
	 } else {
		 grid[zci]=v[yci];
		 yindex[yci]=zci;
	   zci++;
	   yci++;	 
	 }	 
	}
	/* copy the tail */
	if(xci<Nu && yci==Nv) {
		/* tail from x */
		while(xci<Nu) {
		 grid[zci]=u[xci];
		 xindex[xci]=zci;
	   zci++;
	   xci++;	 
		}
	} else if (xci==Nu && yci<Nv) {
		/* tail from y */
		while(yci<Nv) {
		 grid[zci]=v[yci];
		 yindex[yci]=zci;
	   zci++;
	   yci++;	 
		}
	}
	Ntot=zci;

	if (Ntot<2) {
		fprintf(stderr,"Error: Need at least 2 grid points\n");
		exit(1);
	}
#ifdef DEBUG
	printf("\n");
	for (xci=0; xci<Nu; xci++) {
	 printf("[%d]=%lf ",xci,u[xci]);
	}
	printf("\n");
	for (xci=0; xci<Nv; xci++) {
	 printf("[%d]=%lf ",xci,v[xci]);
	}
	printf("\n");
	for (xci=0; xci<Ntot; xci++) {
	 printf("[%d]=%lf ",xci,grid[xci]);
	}
	printf("\n");
	for (xci=0; xci<Nu; xci++) {
	 printf("[%d]=%d ",xci,xindex[xci]);
	}
	printf("\n");
	for (xci=0; xci<Nv; xci++) {
	 printf("[%d]=%d ",xci,yindex[xci]);
	}
	printf("\n");
#endif
	/* wrap up negative values to positive ones if possible */
  if ((neg_grid=(int*)calloc((size_t)(Ntot),sizeof(int)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}
	for (zci=0; zci<Ntot; zci++) {
			neg_grid[zci]=-1;
	}
	zci=Ntot-1;
	xci=0;
	/* find positive values to all negative values if possible */
	while(xci<Ntot && grid[xci]<0) {
	 /* try to find a positive value for this is possible */
	 while(zci>=0 && grid[zci]>0 && -grid[xci]<grid[zci]) {
				zci--;
	 }
	 /* now we might have found a correct value */
	 if (zci>=0 && grid[zci]>0 && -grid[xci]==grid[zci]) {
			neg_grid[xci]=zci;
	 }
	 xci++;
	}

#ifdef DEBUG
	for (xci=0; xci<Ntot; xci++) {
	 printf("[%d]=%d ",xci,neg_grid[xci]);
	}
	printf("\n");
#endif


	/* set up factorial array */
  if ((fact=(double*)calloc((size_t)(n0),sizeof(double)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}
  fact[0]=1;
	for (xci=1; xci<(n0); xci++) {
		fact[xci]=(xci+1)*fact[xci-1];
	}

#ifdef DEBUG
	printf("Fact\n");
	for (xci=0; xci<(n0); xci++) {
	 printf("[%d]=%lf ",xci,fact[xci]);
	}
	printf("\n");
#endif

	/* setup array to store calculated shapelet value */
	/* need max storage Ntot x n0 */
  if ((shpvl=(double**)calloc((size_t)(Ntot),sizeof(double*)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}
	for (xci=0; xci<Ntot; xci++) {
   if ((shpvl[xci]=(double*)calloc((size_t)(n0),sizeof(double)))==0) {
	   fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	   exit(1);
	 }
	}

	sqr_beta=sqrt(beta);
	/* start filling in the array from the positive values */
	for (zci=Ntot-1; zci>=0; zci--) {
    /* check to see if there are any positive values */
     if (neg_grid[zci] !=-1) {
			/* copy in the values from positive one, with appropriate sign change */
	     for (xci=0; xci<(n0); xci++) {
				 shpvl[zci][xci]=(xci%2==1?-shpvl[neg_grid[zci]][xci]:shpvl[neg_grid[zci]][xci]);
			 }
		 } else {
	     for (xci=0; xci<(n0); xci++) {
				/*take into account the scaling - in Fourier domain
				*/
				 xval=grid[zci]*beta;
				 shpvl[zci][xci]=sqr_beta*pi_4r*H_e(xval,xci)*exp(-0.5*xval*xval)/sqrt((2<<xci)*fact[xci]);
		   }
		 }
	}


#ifdef DEBUG
	for (zci=0; zci<Ntot; zci++) {
		printf("%lf= ",grid[zci]);
	  for (xci=0; xci<(n0); xci++) {
		  printf("%lf, ",shpvl[zci][xci]);
		}
		printf("\n");
	}
#endif

	/* now calculate the mode vectors */
	/* each vector is Nu x Nv length and there are n0*n0 of them */
  if ((*Av=(double*)calloc((size_t)(Nu*Nv*(n0)*(n0)),sizeof(double)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}
  if ((*cplx=(int*)calloc((size_t)((n0)*(n0)),sizeof(int)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}

  for (n2=0; n2<(n0); n2++) {
	 for (n1=0; n1<(n0); n1++) {
	  (*cplx)[n2*n0+n1]=((n1+n2)%2==0?0:1) /* even (real) or odd (imaginary)*/;
		/* sign */
		if ((*cplx)[n2*n0+n1]==0) {
			signval=(((n1+n2)/2)%2==0?1:-1);
		} else {
			signval=(((n1+n2-1)/2)%2==0?1:-1);
		}

    /* fill in Nu*Nv*(zci) to Nu*Nv*(zci+1)-1 */
		start=Nu*Nv*(n2*(n0)+n1);
		if (signval==-1) {
	  for (yci=0; yci<Nv; yci++) {
	    for (xci=0; xci<Nu; xci++) {
        (*Av)[start+Nv*yci+xci]=-shpvl[xindex[xci]][n1]*shpvl[yindex[yci]][n2];
			}
		}
		} else {
	  for (yci=0; yci<Nv; yci++) {
	    for (xci=0; xci<Nu; xci++) {
        (*Av)[start+Nv*yci+xci]=shpvl[xindex[xci]][n1]*shpvl[yindex[yci]][n2];
			}
		}
		}
	 }
	}

#ifdef DEBUG
	printf("Matrix dimension=%d by %d\n",Nu*Nv,(n0)*(n0));
#endif
#ifdef DEBUG
	for (n1=0; n1<(n0); n1++) {
	 for (n2=0; n2<(n0); n2++) {
		start=Nu*Nv*(n1*(n0)+n2);
	  for (xci=0; xci<Nu; xci++) {
	    for (yci=0; yci<Nv; yci++) {
        printf("%lf ",(*Av)[start+Nv*xci+yci]);
			}
		}
		printf("\n");
	 }
	}
#endif
	free(grid);
	free(xindex);
	free(yindex);
	free(neg_grid);
	free(fact);
	for (xci=0; xci<Ntot; xci++) {
	 free(shpvl[xci]);
	}
	free(shpvl);

  return 0;
}

/** calculate the UV mode vectors (scalar version, only 1 point)
 * in: u,v: arrays of the grid points in UV domain
 *      M: number of modes
 *      beta: scale factor
 *      n0: number of modes in each dimension
 * out:
 *      Av: array of mode vectors size Nu.Nv times n0.n0, in column major order
 *      cplx: array of integers, size n0*n0, if 1 this mode is imaginary, else real
 *
 */
int
calculate_uv_mode_vectors_scalar(double *u, int Nu, double *v, int Nv, double beta, int n0, double **Av, int **cplx) {

	int xci,zci,Ntot;

	double **shpvl, *fact;
	int n1,n2,start;
	double pi_4r=1/sqrt(sqrt(M_PI));
	double xval,sqr_beta;
	int signval;

  /* image size: Nu by Nv pixels
   */
	if (Nu!=1 || Nv != 1) { 
	  fprintf(stderr,"%s: %d: U,V arrays must be length 1\n",__FILE__,__LINE__);
	  exit(1);
	}
  Ntot=2; /* u,v seperately */
	/* set up factorial array */
  if ((fact=(double*)calloc((size_t)(n0),sizeof(double)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}
  fact[0]=1;
	for (xci=1; xci<(n0); xci++) {
		fact[xci]=(xci+1)*fact[xci-1];
	}

#ifdef DEBUG
	printf("Fact\n");
	for (xci=0; xci<(n0); xci++) {
	 printf("[%d]=%lf ",xci,fact[xci]);
	}
	printf("\n");
#endif

	/* setup array to store calculated shapelet value */
	/* need max storage Ntot x n0 */
  if ((shpvl=(double**)calloc((size_t)(Ntot),sizeof(double*)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}
	for (xci=0; xci<Ntot; xci++) {
   if ((shpvl[xci]=(double*)calloc((size_t)(n0),sizeof(double)))==0) {
	   fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	   exit(1);
	 }
	}

	sqr_beta=sqrt(beta);
	/* start filling in the array from the positive values */
	zci=0;
	for (xci=0; xci<n0; xci++) {
		xval=u[0]*beta;
		shpvl[zci][xci]=sqr_beta*pi_4r*H_e(xval,xci)*exp(-0.5*xval*xval)/sqrt((2<<xci)*fact[xci]);
	}
	zci=1;
	for (xci=0; xci<n0; xci++) {
		xval=v[0]*beta;
		shpvl[zci][xci]=sqr_beta*pi_4r*H_e(xval,xci)*exp(-0.5*xval*xval)/sqrt((2<<xci)*fact[xci]);
	}


#ifdef DEBUG
	for (zci=0; zci<Ntot; zci++) {
	  for (xci=0; xci<(n0); xci++) {
		  printf("%lf, ",shpvl[zci][xci]);
		}
		printf("\n");
	}
#endif

	/* now calculate the mode vectors */
	/* each vector is Nu x Nv length and there are n0*n0 of them */
  if ((*Av=(double*)calloc((size_t)(Nu*Nv*(n0)*(n0)),sizeof(double)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}
  if ((*cplx=(int*)calloc((size_t)((n0)*(n0)),sizeof(int)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}

  for (n2=0; n2<(n0); n2++) {
	 for (n1=0; n1<(n0); n1++) {
	  (*cplx)[n2*n0+n1]=((n1+n2)%2==0?0:1) /* even (real) or odd (imaginary)*/;
		/* sign */
		if ((*cplx)[n2*n0+n1]==0) {
			signval=(((n1+n2)/2)%2==0?1:-1);
		} else {
			signval=(((n1+n2-1)/2)%2==0?1:-1);
		}

    /* fill in Nu*Nv*(zci) to Nu*Nv*(zci+1)-1 */
		start=Nu*Nv*(n2*(n0)+n1);
		if (signval==-1) {
        (*Av)[start]=-shpvl[0][n1]*shpvl[1][n2];
		} else {
        (*Av)[start]=shpvl[0][n1]*shpvl[1][n2];
		}
	 }
	}

#ifdef DEBUG
	printf("Matrix dimension=%d by %d\n",Nu*Nv,(n0)*(n0));
#endif
#ifdef DEBUG
	for (n1=0; n1<(n0); n1++) {
	 for (n2=0; n2<(n0); n2++) {
		start=Nu*Nv*(n1*(n0)+n2);
        printf("%lf ",(*Av)[start]);
		printf("\n");
	 }
	}
#endif
	free(fact);
	for (xci=0; xci<Ntot; xci++) {
	 free(shpvl[xci]);
	}
	free(shpvl);

  return 0;
}
/** calculate the UV mode vectors (block version, needs at least 2 grid points)
 * in: u,v: arrays of the grid points in UV domain
 *      M: number of modes
 *      beta: scale factor
 *      n0: number of modes in each dimension
 * out:
 *      Av: array of mode vectors size Nu.Nv times n0.n0, in column major order
 *      cplx: array of integers, size n0*n0, if 1 this mode is imaginary, else real
 *
 */
int
ShapeletVisTf::calculate_uv_mode_vectors(double *u, int Nu, double *v, int Nv, double beta, int n0, double **Av, int **cplx) {

	double *grid;
	int *xindex,*yindex;
	int xci,yci,zci,Ntot;
	int *neg_grid;

	double **shpvl, *fact;
	int n1,n2,start;
	double pi_4r=1/sqrt(sqrt(M_PI));
	double xval,sqr_beta;
	int signval;

  /* image size: Nu by Nv pixels
   */
	/* allocate memory to store grid points */
  if ((grid=(double*)calloc((size_t)(Nu+Nv),sizeof(double)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}

  if ((xindex=(int*)calloc((size_t)(Nu),sizeof(int)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}
  if ((yindex=(int*)calloc((size_t)(Nv),sizeof(int)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}

	/* merge axes coordinates */
	xci=yci=zci=0;
	while(xci<Nu && yci<Nv ) {
	 if (u[xci]==v[yci]){
		/* common index */
		grid[zci]=u[xci];
		xindex[xci]=zci;
		yindex[yci]=zci;
	  zci++;
	  xci++;	 
	  yci++;	 
	 } else if (u[xci]<v[yci]){
		 grid[zci]=u[xci];
		 xindex[xci]=zci;
	   zci++;
	   xci++;	 
	 } else {
		 grid[zci]=v[yci];
		 yindex[yci]=zci;
	   zci++;
	   yci++;	 
	 }	 
	}
	/* copy the tail */
	if(xci<Nu && yci==Nv) {
		/* tail from x */
		while(xci<Nu) {
		 grid[zci]=u[xci];
		 xindex[xci]=zci;
	   zci++;
	   xci++;	 
		}
	} else if (xci==Nu && yci<Nv) {
		/* tail from y */
		while(yci<Nv) {
		 grid[zci]=v[yci];
		 yindex[yci]=zci;
	   zci++;
	   yci++;	 
		}
	}
	Ntot=zci;

	if (Ntot<2) {
		fprintf(stderr,"Error: Need at least 2 grid points\n");
		exit(1);
	}
#ifdef DEBUG
	printf("\n");
	for (xci=0; xci<Nu; xci++) {
	 printf("[%d]=%lf ",xci,u[xci]);
	}
	printf("\n");
	for (xci=0; xci<Nv; xci++) {
	 printf("[%d]=%lf ",xci,v[xci]);
	}
	printf("\n");
	for (xci=0; xci<Ntot; xci++) {
	 printf("[%d]=%lf ",xci,grid[xci]);
	}
	printf("\n");
	for (xci=0; xci<Nu; xci++) {
	 printf("[%d]=%d ",xci,xindex[xci]);
	}
	printf("\n");
	for (xci=0; xci<Nv; xci++) {
	 printf("[%d]=%d ",xci,yindex[xci]);
	}
	printf("\n");
#endif
	/* wrap up negative values to positive ones if possible */
  if ((neg_grid=(int*)calloc((size_t)(Ntot),sizeof(int)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}
	for (zci=0; zci<Ntot; zci++) {
			neg_grid[zci]=-1;
	}
	zci=Ntot-1;
	xci=0;
	/* find positive values to all negative values if possible */
	while(xci<Ntot && grid[xci]<0) {
	 /* try to find a positive value for this is possible */
	 while(zci>=0 && grid[zci]>0 && -grid[xci]<grid[zci]) {
				zci--;
	 }
	 /* now we might have found a correct value */
	 if (zci>=0 && grid[zci]>0 && -grid[xci]==grid[zci]) {
			neg_grid[xci]=zci;
	 }
	 xci++;
	}

#ifdef DEBUG
	for (xci=0; xci<Ntot; xci++) {
	 printf("[%d]=%d ",xci,neg_grid[xci]);
	}
	printf("\n");
#endif


	/* set up factorial array */
  if ((fact=(double*)calloc((size_t)(n0),sizeof(double)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}
  fact[0]=1;
	for (xci=1; xci<(n0); xci++) {
		fact[xci]=(xci+1)*fact[xci-1];
	}

#ifdef DEBUG
	printf("Fact\n");
	for (xci=0; xci<(n0); xci++) {
	 printf("[%d]=%lf ",xci,fact[xci]);
	}
	printf("\n");
#endif

	/* setup array to store calculated shapelet value */
	/* need max storage Ntot x n0 */
  if ((shpvl=(double**)calloc((size_t)(Ntot),sizeof(double*)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}
	for (xci=0; xci<Ntot; xci++) {
   if ((shpvl[xci]=(double*)calloc((size_t)(n0),sizeof(double)))==0) {
	   fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	   exit(1);
	 }
	}

	sqr_beta=sqrt(beta);
	/* start filling in the array from the positive values */
	for (zci=Ntot-1; zci>=0; zci--) {
    /* check to see if there are any positive values */
     if (neg_grid[zci] !=-1) {
			/* copy in the values from positive one, with appropriate sign change */
	     for (xci=0; xci<(n0); xci++) {
				 shpvl[zci][xci]=(xci%2==1?-shpvl[neg_grid[zci]][xci]:shpvl[neg_grid[zci]][xci]);
			 }
		 } else {
	     for (xci=0; xci<(n0); xci++) {
				/*take into account the scaling - in Fourier domain
				*/
				 xval=grid[zci]*beta;
				 shpvl[zci][xci]=sqr_beta*pi_4r*H_e(xval,xci)*exp(-0.5*xval*xval)/sqrt((2<<xci)*fact[xci]);
		   }
		 }
	}


#ifdef DEBUG
	for (zci=0; zci<Ntot; zci++) {
		printf("%lf= ",grid[zci]);
	  for (xci=0; xci<(n0); xci++) {
		  printf("%lf, ",shpvl[zci][xci]);
		}
		printf("\n");
	}
#endif

	/* now calculate the mode vectors */
	/* each vector is Nu x Nv length and there are n0*n0 of them */
  if ((*Av=(double*)calloc((size_t)(Nu*Nv*(n0)*(n0)),sizeof(double)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}
  if ((*cplx=(int*)calloc((size_t)((n0)*(n0)),sizeof(int)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}

  for (n2=0; n2<(n0); n2++) {
	 for (n1=0; n1<(n0); n1++) {
	  (*cplx)[n2*n0+n1]=((n1+n2)%2==0?0:1) /* even (real) or odd (imaginary)*/;
		/* sign */
		if ((*cplx)[n2*n0+n1]==0) {
			signval=(((n1+n2)/2)%2==0?1:-1);
		} else {
			signval=(((n1+n2-1)/2)%2==0?1:-1);
		}

    /* fill in Nu*Nv*(zci) to Nu*Nv*(zci+1)-1 */
		start=Nu*Nv*(n2*(n0)+n1);
		if (signval==-1) {
	  for (yci=0; yci<Nv; yci++) {
	    for (xci=0; xci<Nu; xci++) {
        (*Av)[start+Nv*yci+xci]=-shpvl[xindex[xci]][n1]*shpvl[yindex[yci]][n2];
			}
		}
		} else {
	  for (yci=0; yci<Nv; yci++) {
	    for (xci=0; xci<Nu; xci++) {
        (*Av)[start+Nv*yci+xci]=shpvl[xindex[xci]][n1]*shpvl[yindex[yci]][n2];
			}
		}
		}
	 }
	}

#ifdef DEBUG
	printf("Matrix dimension=%d by %d\n",Nu*Nv,(n0)*(n0));
#endif
#ifdef DEBUG
	for (n1=0; n1<(n0); n1++) {
	 for (n2=0; n2<(n0); n2++) {
		start=Nu*Nv*(n1*(n0)+n2);
	  for (xci=0; xci<Nu; xci++) {
	    for (yci=0; yci<Nv; yci++) {
        printf("%lf ",(*Av)[start+Nv*xci+yci]);
			}
		}
		printf("\n");
	 }
	}
#endif
	free(grid);
	free(xindex);
	free(yindex);
	free(neg_grid);
	free(fact);
	for (xci=0; xci<Ntot; xci++) {
	 free(shpvl[xci]);
	}
	free(shpvl);

  return 0;
}

/** calculate the UV mode vectors (scalar version, only 1 point)
 * in: u,v: arrays of the grid points in UV domain
 *      M: number of modes
 *      beta: scale factor
 *      n0: number of modes in each dimension
 * out:
 *      Av: array of mode vectors size Nu.Nv times n0.n0, in column major order
 *      cplx: array of integers, size n0*n0, if 1 this mode is imaginary, else real
 *
 */
int
ShapeletVisTf::calculate_uv_mode_vectors_scalar(double *u, int Nu, double *v, int Nv, double beta, int n0, double **Av, int **cplx) {

	int xci,zci,Ntot;

	double **shpvl, *fact;
	int n1,n2,start;
	double pi_4r=1/sqrt(sqrt(M_PI));
	double xval,sqr_beta;
	int signval;

  /* image size: Nu by Nv pixels
   */
	if (Nu!=1 || Nv != 1) { 
	  fprintf(stderr,"%s: %d: U,V arrays must be length 1\n",__FILE__,__LINE__);
	  exit(1);
	}
  Ntot=2; /* u,v seperately */
	/* set up factorial array */
  if ((fact=(double*)calloc((size_t)(n0),sizeof(double)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}
  fact[0]=1;
	for (xci=1; xci<(n0); xci++) {
		fact[xci]=(xci+1)*fact[xci-1];
	}

#ifdef DEBUG
	printf("Fact\n");
	for (xci=0; xci<(n0); xci++) {
	 printf("[%d]=%lf ",xci,fact[xci]);
	}
	printf("\n");
#endif

	/* setup array to store calculated shapelet value */
	/* need max storage Ntot x n0 */
  if ((shpvl=(double**)calloc((size_t)(Ntot),sizeof(double*)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}
	for (xci=0; xci<Ntot; xci++) {
   if ((shpvl[xci]=(double*)calloc((size_t)(n0),sizeof(double)))==0) {
	   fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	   exit(1);
	 }
	}

	sqr_beta=sqrt(beta);
	/* start filling in the array from the positive values */
	zci=0;
	for (xci=0; xci<n0; xci++) {
		xval=u[0]*beta;
		shpvl[zci][xci]=sqr_beta*pi_4r*H_e(xval,xci)*exp(-0.5*xval*xval)/sqrt((2<<xci)*fact[xci]);
	}
	zci=1;
	for (xci=0; xci<n0; xci++) {
		xval=v[0]*beta;
		shpvl[zci][xci]=sqr_beta*pi_4r*H_e(xval,xci)*exp(-0.5*xval*xval)/sqrt((2<<xci)*fact[xci]);
	}


#ifdef DEBUG
	for (zci=0; zci<Ntot; zci++) {
	  for (xci=0; xci<(n0); xci++) {
		  printf("%lf, ",shpvl[zci][xci]);
		}
		printf("\n");
	}
#endif

	/* now calculate the mode vectors */
	/* each vector is Nu x Nv length and there are n0*n0 of them */
  if ((*Av=(double*)calloc((size_t)(Nu*Nv*(n0)*(n0)),sizeof(double)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}
  if ((*cplx=(int*)calloc((size_t)((n0)*(n0)),sizeof(int)))==0) {
	  fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
	  exit(1);
	}

  for (n2=0; n2<(n0); n2++) {
	 for (n1=0; n1<(n0); n1++) {
	  (*cplx)[n2*n0+n1]=((n1+n2)%2==0?0:1) /* even (real) or odd (imaginary)*/;
		/* sign */
		if ((*cplx)[n2*n0+n1]==0) {
			signval=(((n1+n2)/2)%2==0?1:-1);
		} else {
			signval=(((n1+n2-1)/2)%2==0?1:-1);
		}

    /* fill in Nu*Nv*(zci) to Nu*Nv*(zci+1)-1 */
		start=Nu*Nv*(n2*(n0)+n1);
		if (signval==-1) {
        (*Av)[start]=-shpvl[0][n1]*shpvl[1][n2];
		} else {
        (*Av)[start]=shpvl[0][n1]*shpvl[1][n2];
		}
	 }
	}

#ifdef DEBUG
	printf("Matrix dimension=%d by %d\n",Nu*Nv,(n0)*(n0));
#endif
#ifdef DEBUG
	for (n1=0; n1<(n0); n1++) {
	 for (n2=0; n2<(n0); n2++) {
		start=Nu*Nv*(n1*(n0)+n2);
        printf("%lf ",(*Av)[start]);
		printf("\n");
	 }
	}
#endif
	free(fact);
	for (xci=0; xci<Ntot; xci++) {
	 free(shpvl[xci]);
	}
	free(shpvl);

  return 0;
}



///// polar shapelet stuff

/* generalized Laguerre polynomial L_p^q(x) */
static double
L_g(int p, int q, double x) {
  if(p==0) return 1.0;
  if(p==1) return 1.0-x+(double)q;
  return (2+((double)q-1.0-x)/(double)p)*L_g(p-1,q,x)-(1+((double)q-1.0)/(double)p)*L_g(p-2,q,x);
}


/* calculate mode vectors for polar shapelet basis, 
 *  n0: max number in n, so m goes from -n0,...,n0
 *  the number of modes is then n0*(n0+1)/2
 *  r: first axis, radial
 *  Nr: length of r
 *  th: second axis, angular
 *  Nt: length of th
 *  Av: array of mode vectors, column major order, real and imaginary
*/
int 
ShapeletVisTf::calculate_polar_mode_vectors(double *r, int Nr, double *th, int Nt, int n0,double beta, double **Avr, double **Avi) {
 double *fact,*betam;
 double **pream,**rgridm;
 dcomplex **thgrid;
 dcomplex ****M;
 double ***Lg;
 int xci,yci,zci, xlen, npm,nmm;
 double inv_beta_sq;

 int nmodes,rank;

 FILE *dbg;
 inv_beta_sq=1.0/(beta*beta);

 /* factorial array, store from 0! to ((n0+|m|)/2)! at the 
 * respective position of the array - length n+1
 * size  n0+1
 */
 if ((fact=(double*)calloc((size_t)(n0+1),sizeof(double)))==0) {
    fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
    exit(1);
 }
 fact[0]=1;
 for (xci=1; xci<=(n0); xci++) {
    fact[xci]=(xci+1)*fact[xci-1];
 }

 /* storage to calculate 1/beta^{|m|+1} , from 0 to n0 */
 /* size n0+1 */
 if ((betam=(double*)calloc((size_t)(n0+1),sizeof(double)))==0) {
    fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
    exit(1);
 }
 betam[0]=1/beta;
 for (xci=1; xci<=(n0); xci++) {
    betam[xci]=betam[xci-1]/beta;
 }

 /* storage to calculate r^|m| for all possible values, also
 * multiplied by exp(-r^2/2beta^2) */
 /* size Nr x (n0+1) */
 if ((rgridm=(double**)calloc((size_t)(Nr),sizeof(double*)))==0) {
    fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
    exit(1);
 }
 for (xci=0; xci<(Nr); xci++) {
  if ((rgridm[xci]=(double*)calloc((size_t)(n0+1),sizeof(double)))==0) {
    fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
    exit(1);
  }
  rgridm[xci][0]=exp(-0.5*r[xci]*r[xci]/(beta*beta));
  for (yci=1; yci<=(n0); yci++) {
   rgridm[xci][yci]=r[xci]*rgridm[xci][yci-1];
  }
 }
 
 /* storage to calculate exp(-j*m*theta) for all possible values */
 /* only calculate m from 0 .. to n0 because negative is conjugate */
 /* size Nt x (n0+1) */
 if ((thgrid=(dcomplex**)calloc((size_t)(Nt),sizeof(dcomplex*)))==0) {
    fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
    exit(1);
 }
 for (xci=0; xci<(Nt); xci++) {
  if ((thgrid[xci]=(dcomplex*)calloc((size_t)(n0+1),sizeof(dcomplex)))==0) {
    fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
    exit(1);
  }
  for (yci=0; yci<=(n0); yci++) {
   thgrid[xci][yci]=make_dcomplex(cos(yci*th[xci]),-sin(yci*th[xci]));
  }
 }

 /* storage to calculate preamble, dependent only on n and |m| */
 /* size n0 x [1,1,2,2,3,3,...] varying */
 if ((pream=(double**)calloc((size_t)(n0),sizeof(double*)))==0) {
    fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
    exit(1);
 }
 for (xci=0; xci<(n0); xci++) {
  /* for each xci, |m| goes from 0/1,2/3,...,xci */
  xlen=xci/2+1;
  if ((pream[xci]=(double*)calloc((size_t)(xlen),sizeof(double)))==0) {
    fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
    exit(1);
  }
  zci=xlen-1;
  for (yci=xci; yci>=0; yci-=2) {
   npm=(xci+yci)/2;
   nmm=(xci-yci)/2;
   /* reverse fill */
   pream[xci][zci]=sqrt((double)fact[nmm]/((double)fact[npm]*M_PI))/betam[yci];
   if (nmm%2)  { /* odd */
    pream[xci][zci]=-pream[xci][zci];
   }
   zci--;
  }
 }

 /* storage to calculate Laguerre polynomical for given n,|m|,r */
 /* size n0 x [1,1,2,2,3,3,....] x  Nr */
 if ((Lg=(double***)calloc((size_t)(n0),sizeof(double**)))==0) {
    fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
    exit(1);
 }

 for (xci=0; xci<(n0); xci++) {
  /* for each xci, |m| goes from 0/1,2/3,...,xci */
  xlen=xci/2+1;
  if ((Lg[xci]=(double**)calloc((size_t)(xlen),sizeof(double*)))==0) {
    fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
    exit(1);
  }
  zci=0;
  for (yci=xci%2; yci<=xci; yci+=2) {
    if ((Lg[xci][zci]=(double*)calloc((size_t)(Nr),sizeof(double)))==0) {
     fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
     exit(1);
    } 

    nmm=(xci-yci)/2; /* (n-|m|)/2 */
    for (npm=0; npm<Nr; npm++) {
      Lg[xci][zci][npm]=L_g(nmm,yci,r[npm]*r[npm]*inv_beta_sq);
    }
    zci++;
  }
 }
 
 free(fact);
 free(betam);
 /* now form the product of pream(n,|m|) ,  rgridm(r,|m|), 
 * thgrid(m ,theta)  (m positive) and Lg(n, |m|, r)
 * size: n0 x [0, 2, 3, 4, 5, ..] x Nr x Nt
 */
 if ((M=(dcomplex****)calloc((size_t)(n0),sizeof(dcomplex***)))==0) {
    fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
    exit(1);
 }
 for(xci=0; xci<n0; xci++) {
   if ((M[xci]=(dcomplex***)calloc((size_t)(xci+1),sizeof(dcomplex**)))==0) {
     fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
     exit(1);
   }
   for (yci=0; yci<=xci; yci++) {
     if ((M[xci][yci]=(dcomplex**)calloc((size_t)(Nr),sizeof(dcomplex*)))==0) {
       fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
       exit(1);
     }
     for (zci=0; zci<Nr; zci++) {
       if ((M[xci][yci][zci]=(dcomplex*)calloc((size_t)(Nt),sizeof(dcomplex)))==0) {
         fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
         exit(1);
       }
       
     }

   }
 }

 for(xci=0; xci<n0; xci++) {
  yci=0; /* present m index */
  xlen=0; /* present |m| index */
  for (npm=xci%2; npm<=xci; npm+=2) {
    if (npm) { /* m not zero */
     /* calculate m and -m */
     for (zci=0; zci<Nr; zci++) {
        for (nmm=0; nmm<Nt; nmm++) {
          M[xci][yci][zci][nmm]=pream[xci][xlen]*rgridm[zci][xlen]*thgrid[nmm][npm]*Lg[xci][xlen][zci];
          /* this is conjugate */
          M[xci][yci+1][zci][nmm]=make_dcomplex(creal(M[xci][yci][zci][nmm]), -cimag(M[xci][yci][zci][nmm]));
        }
     }
     yci+=2;
    } else { /* m is zero */
     /* calculate for m */
     for (zci=0; zci<Nr; zci++) {
        for (nmm=0; nmm<Nt; nmm++) {
          M[xci][yci][zci][nmm]=pream[xci][xlen]*rgridm[zci][xlen]*thgrid[nmm][npm]*Lg[xci][xlen][zci];
        }
     }
     yci++;
    }
    xlen++;
  }
 }

#ifdef DEBUG
 printf("preamble n, |m|\n");
 for (xci=0; xci<(n0); xci++) {
  xlen=xci/2+1;
  for (yci=0; yci<xlen; yci++) {
   printf("[%d %d]: %lf ",xci,yci,pream[xci][yci]);
  }
  printf("\n");
 }
 
 printf("thetagrid theta, |m|\n");
 for (xci=0; xci<(Nt); xci++) {
  for (yci=0; yci<=(n0); yci++) {
   printf("[%d %d]: %lf(%lf) ",xci,yci,creal(thgrid[xci][yci]), cimag(thgrid[xci][yci]));
  }
  printf("\n");
 }

 printf("rmgrid r, |m|\n");
 for (xci=0; xci<(Nr); xci++) {
  for (yci=0; yci<=(n0); yci++) {
   printf("[%d %d]: %lf ",xci,yci,rgridm[xci][yci]);
  }
  printf("\n");
 }
#endif

 for(xci=0; xci<n0; xci++) {
  free(pream[xci]);
 }
 free(pream);
 for(xci=0; xci<Nr; xci++) {
  free(rgridm[xci]);
 }
 free(rgridm);
 for(xci=0; xci<Nt; xci++) {
  free(thgrid[xci]);
 }
 free(thgrid);
 for(xci=0; xci<n0; xci++) {
   xlen=xci/2+1;
   for(yci=0; yci<xlen; yci++) {
    free(Lg[xci][yci]);
   }
   free(Lg[xci]);
 }
 free(Lg);

#ifdef DEBUG
 printf("Product\n");
 for(xci=0; xci<n0; xci++) {
   for (yci=0; yci<=xci; yci++) {
     for (zci=0; zci<Nr; zci++) {
        printf("[%d %d %d]: ", xci,yci,zci);
        for (nmm=0; nmm<Nt; nmm++) {
         printf("%lf(%lf)  ",creal(M[xci][yci][zci][nmm]),cimag(M[xci][yci][zci][nmm]));
        }
     printf("\n");
     }
   } 
 }
#endif

 nmodes=(n0)*(n0+1)/2;
 printf("nmodes=%d\n",nmodes);
 printf("ncols=%d\n",Nr*Nt);

 if ((*Avr=(double*)calloc((size_t)(Nr*Nt*nmodes),sizeof(double)))==0) {
    fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
    exit(1);
 }
 if ((*Avi=(double*)calloc((size_t)(Nr*Nt*nmodes),sizeof(double)))==0) {
    fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
    exit(1);
 }

 /* copy to A */
 xlen=0;
 for(xci=0; xci<n0; xci++) {
 for (yci=0; yci<=xci; yci++) {
  for (zci=0; zci<Nr; zci++) {
   for (nmm=0; nmm<Nt; nmm++) {
     (*Avr)[xlen]=creal(M[xci][yci][zci][nmm]);
     (*Avi)[xlen]=cimag(M[xci][yci][zci][nmm]);
     xlen++;
     }
   }
  }
 }

 printf("\n");
 printf("r=[");
 for(xci=0; xci<Nr; xci++) {
  printf("%lf, ",r[xci]);
 }
 printf("];\n");
 printf("theta=[");
 for(xci=0; xci<Nt; xci++) {
  printf("%lf, ",th[xci]);
 }
 printf("];\n");


 /* print debug to file */
 if ((dbg=fopen("debug","w"))==0) {
    fprintf(stderr,"%s: %d: cannot open file\n",__FILE__,__LINE__);
    exit(1);
 }
 for (zci=0; zci<Nr; zci++) {
  for (nmm=0; nmm<Nt; nmm++) {
    for(xci=0; xci<n0; xci++) {
     for (yci=0; yci<=xci; yci++) {
         fprintf(dbg," %lf %lf",creal(M[xci][yci][zci][nmm]),cimag(M[xci][yci][zci][nmm]));
     }
    }
    fprintf(dbg,"\n");
    }
 }
 fclose(dbg);

 for(xci=0; xci<n0; xci++) {
   for (yci=0; yci<=xci; yci++) {
     for (zci=0; zci<Nr; zci++) {
       free(M[xci][yci][zci]);
     }
     free(M[xci][yci]);
   }
  free(M[xci]);
 }
 free(M);


 return 0;
}


} // namespace Meq
