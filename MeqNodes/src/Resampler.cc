//# Resampler.cc: resamples result resolutions
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
//# $Id$

#include <MeqNodes/Resampler.h>
#include <MEQ/MeqVocabulary.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
//#include <MEQ/ResampleMachine.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>

namespace Meq {

//#define DEBUG
const HIID FFlagDensity = AidFlag|AidDensity;

//##ModelId=400E5355029C
Resampler::Resampler()
: Node(1), // 1 child expected
  flag_mask(-1),flag_bit(0),flag_density(0.5)
{}

//##ModelId=400E5355029D
Resampler::~Resampler()
{}

void Resampler::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
//  rec[FIntegrate].get(integrate,initializing);
  rec[FFlagMask].get(flag_mask,initializing);
  rec[FFlagBit].get(flag_bit,initializing);
  rec[FFlagDensity].get(flag_density,initializing);
}

int Resampler::getResult (Result::Ref &resref, 
                           const std::vector<Result::Ref> &childres,
                           const Request &request,bool)
{
  std::vector<Thread::Mutex::Lock> child_reslock(numChildren());
  lockMutexes(child_reslock,childres);
  Assert(childres.size()==1);
  const Result &chres = *( childres.front() );
  const Cells &incells = chres.cells();
  const Cells &outcells = request.cells();
  // create resampler
  ResampleMachine resampler(incells, outcells);
  // return child result directly if nothing is to be done
  if( resampler.isIdentical() )
  {
    resref.copy(childres.front());
    return 0;
  }
  // do the resampling  
  resampler.setFlagPolicy(flag_mask,flag_bit,flag_density);
  int nvs = chres.numVellSets();
  Result & result = resref <<= new Result(nvs,chres.isIntegrated());
  for( int ivs=0; ivs<nvs; ivs++ )
  {
    VellSet::Ref ref;
		const VellSet &invs=chres.vellSet(ivs);
		VellSet &outvs= ref<<= new VellSet(invs.numSpids(),invs.numPertSets());
    // call the resampler
    //resampler.apply(ref,invs,chres.isIntegrated());
    resampler.apply(outvs,invs);

    result.setVellSet(ivs,ref);
  }

	result.setCells(outcells);
	result.setDims(chres.dims());
  return 0;
}


ResampleMachine::ResampleMachine(const Cells &in, const Cells &out)
  : flag_mask_(-1),flag_bit_(0),flag_density_(0.5),identical_(false)
{

	// in: cells of the old (child) grid
	// out: cells of the request (new grid)
	//using the in and out cells, we find the grid points of
	//new cell centers. Note it is always assumed that out cells
	// are larger than in cells so that more than one can be included.
	// Also check to see if they are identical.
	
				//setup arrays for  binary search
  blitz::Array<double,1> xax=out.center(0);
	blitz::Array<double,1> yax=out.center(1);
	double xstart=out.domain().start(0);
	double xend=out.domain().end(0);
	double ystart=out.domain().start(1);
	double yend=out.domain().end(1);
	blitz::Array<double,1> xcellsize=out.cellSize(0); 
	blitz::Array<double,1> ycellsize=out.cellSize(1); 
	blitz::Array<double,1> inxcellsize=in.cellSize(0); 
	blitz::Array<double,1> inycellsize=in.cellSize(1); 

	//array of values to be searched
  blitz::Array<double,1> xaxs=in.center(0);
  blitz::Array<double,1> yaxs=in.center(1);
#ifdef DEBUG
	cout<<"Out X "<<xax<<endl;
	cout<<"Out Y "<<yax<<endl;
	//array of values to be searched
	cout<<"In X "<<xaxs<<endl;
	cout<<"In Y "<<yaxs<<endl;
#endif
	nx_=xax.extent(0);
	ny_=yax.extent(0);

	int nxs=xaxs.extent(0);
	int nys=yaxs.extent(0);

	//if out cells are smaller than in cells
	//it will be taken to be idential for the moment
  identical_=((nx_==nxs)&&(ny_==nys));	
#ifdef DEBUG
  cout<<"Itentical "<<identical_<<endl;
#endif

	//resize the array to store cumulative flags+weights
	cell_weight_.resize(nx_,ny_);
	//make it zero
  cell_weight_=0; 

	////////////////////////////////
	bx_.resize(2);
	bx_[0].resize(nx_);
	bx_[1].resize(ny_);

#ifdef DEBUG
 cout<<inxcellsize<<endl<<xaxs<<endl;
#endif
 //array to be searched - input cells
 blitz::Array<double,1> xx(nxs-1); 
 for (int i=0; i<nxs-1;i++) {
		xx(i)=xaxs(i)+inxcellsize(i)*0.5;
 }
#ifdef DEBUG
 cout<<xx<<endl;
#endif
 //arrayf of values within search is done
 blitz::Array<double,1> inxx(nx_+1); 
 inxx(0)=xstart;
 inxx(nx_)=xend;
 for (int i=1; i<nx_;i++) {
  inxx(i)=xax(i-1)+xcellsize(i-1)*0.5;
 }	
#ifdef DEBUG
 cout<<inxx<<endl;
#endif
 blitz::Array<int,1> xxindex(nxs-1); 
 // do the search
 for (int i=0; i<nxs-1;i++)
	  xxindex(i)=bin_search(inxx,xx(i),0,nx_+1);
#ifdef DEBUG
 cout<<xxindex<<endl;
#endif

 int cli=0;
#ifdef DEBUG
 cout<<"Cell "<<cli<<" falls on cells ["<<0<<","<<xxindex(cli)<<"]"<<endl;
#endif
 insert(cli,0,xxindex(cli), 0,inxcellsize,xcellsize,xaxs,xax);
	
 cli++;
 while(cli<nxs-1){
#ifdef DEBUG
  cout<<"Cell "<<cli<<" falls on cells ["<<xxindex(cli-1)<<","<<xxindex(cli)<<"]"<<endl;
#endif
  insert(cli, xxindex(cli-1),xxindex(cli), 0,inxcellsize,xcellsize,xaxs,xax);
  cli++;
 }
#ifdef DEBUG
 cout<<"Cell "<<cli<<" falls on cells ["<<xxindex(cli-1)<<","<<nx_-1<<"]"<<endl;
#endif
 insert(cli, xxindex(cli-1),nx_-1, 0,inxcellsize,xcellsize,xaxs,xax);

#ifdef DEBUG
 bx_[0].print();
#endif

 blitz::Array<double,1> yy(nys-1); 
 for (int i=0; i<nys-1;i++) {
		yy(i)=yaxs(i)+inycellsize(i)*0.5;
 }
#ifdef DEBUG
 cout<<yy<<endl;
#endif
 //arrayf of values within search is done
 blitz::Array<double,1> inyy(ny_+1); 
 inyy(0)=ystart;
 inyy(ny_)=yend;
 for (int i=1; i<ny_;i++) {
  inyy(i)=yax(i-1)+ycellsize(i-1)*0.5;
 }	
#ifdef DEBUG
 cout<<inyy<<endl;
#endif
 blitz::Array<int,1> yyindex(nys-1); 
 // do the search
 for (int i=0; i<nys-1;i++)
	  yyindex(i)=bin_search(inyy,yy(i),0,ny_+1);
#ifdef DEBUG
 cout<<yyindex<<endl;
#endif

 cli=0;
#ifdef DEBUG
 cout<<"Cell "<<cli<<" falls on cells ["<<0<<","<<yyindex(cli)<<"]"<<endl;
#endif
 insert(cli,0,yyindex(cli), 1,inycellsize,ycellsize,yaxs,yax);
	
 cli++;
 while(cli<nys-1){
#ifdef DEBUG
  cout<<"Cell "<<cli<<" falls on cells ["<<yyindex(cli-1)<<","<<yyindex(cli)<<"]"<<endl;
#endif
  insert(cli, yyindex(cli-1),yyindex(cli), 1,inycellsize,ycellsize,yaxs,yax);
  cli++;
 }
#ifdef DEBUG
 cout<<"Cell "<<cli<<" falls on cells ["<<yyindex(cli-1)<<","<<ny_-1<<"]"<<endl;
#endif
 insert(cli, yyindex(cli-1),ny_-1, 1,inycellsize,ycellsize,yaxs,yax);

#ifdef DEBUG
 bx_[1].print();
#endif

}

ResampleMachine::~ResampleMachine()
{
}


int ResampleMachine::apply(VellSet &out, const VellSet &in)
{

				Vells invl=in.getValue();
				int nxs,nys;
				nxs=invl.extent(0);
				nys=invl.extent(1);

				VellsFlagType *F=0;
				//check for flags
				if (invl.hasDataFlags() ) {
        Vells &flvl=const_cast<Vells &>(invl.dataFlags());

				blitz::Array<VellsFlagType,2> FF=flvl.as<VellsFlagType,2>()(LoRange::all(),LoRange::all()); 

#ifdef DEBUG
				cout <<"Flags 1"<<FF<<endl;
#endif
				//F=const_cast<VellsFlagType*>(flvl.beginFlags());
				F= const_cast<VellsFlagType*>(FF.data());

#ifdef DEBUG
				cout <<"Flags "<<F<<endl;
#endif
				}

				if (invl.isReal()) {
				 blitz::Array<double,2> B=invl.as<double,2>()(LoRange::all(),LoRange::all()); 
         blitz::Array<double,2> A(nx_,ny_);
				 A=0;
#ifdef DEBUG
				 cout<<" A "<<A<<endl;
				 cout<<" B "<<B<<endl;
#endif
				if (!invl.hasDataFlags() ) {
         do_resample(A,  B);
				  out.setValue(new Vells(A));
				}else {
         //allocate memory for flags
				blitz::Array<VellsFlagType,2> Aflag(nx_,ny_); 
				 Aflag=0;
         do_resample( A,  B,  F, invl.hasDataFlags(), Aflag);
				  out.setValue(new Vells(A));
					out.setDataFlags(new Vells(Aflag));
				}
				}else{
				 blitz::Array<dcomplex,2> Bc=invl.as<dcomplex,2>()(LoRange::all(),LoRange::all()); 
         blitz::Array<dcomplex,2> Ac(nx_,ny_);
				 Ac = make_dcomplex(0);

#ifdef DEBUG
				 cout<<" Ac "<<Ac<<endl;
				 cout<<" Bc "<<Bc<<endl;
#endif
				if (!invl.hasDataFlags() ) {
         do_resample( Ac,  Bc);
				  out.setValue(new Vells(Ac));
				}else{
				 blitz::Array<VellsFlagType,2> Aflag(nx_,ny_); 
				 Aflag=0;
         do_resample( Ac,  Bc,  F, invl.hasDataFlags(),Aflag);
				  out.setValue(new Vells(Ac));
					out.setDataFlags(new Vells(Aflag));
				}
				}

				return 0;
}

//binary search
int  ResampleMachine::bin_search(blitz::Array<double,1> xarr,double x,int i_start,int i_end) {
	/*
	 * xarr: array of sorted values, make sure x is within the range 
	 * x: value to search
	 * i_start: starting index of array to search 
	 * i_end: end index of array to search 
	 *
	 * return value: index k, such that xarr[k]<= x< xarr[k+1]
	 * for errors: return negative values
	 */
	//trivial case
	if (i_start==i_end) {
		if (xarr(i_start)==x)
				return i_start;
	  else {
			cerr<<"bin search error 1"<<endl;
	    return -1;
    }
	}

	//trivial case with length 2 array
	if (i_end==i_start+1) {
		if (x>=xarr(i_start) && x<xarr(i_end)) {
				return i_start;
		} else {
			cerr<<"bin search error 2"<<endl;
	    return -2;
    }
	}

	//compare the mid point
	int i=(int)((i_start+i_end)/2);
	if (x>=xarr(i) && x<xarr(i+1)) {
		 return i;
	} else {
		//go to lower half of the upper half of the array
		if (x<xarr(i))
			return bin_search(xarr,x,i_start,i);
		else 
			return bin_search(xarr,x,i,i_end);
	}

	//will not reach here
  cerr<<"bin search error 3"<<endl;
  return -3;
}

#ifndef FMULT
#define FMULT(a,b)\
				((a)==1.0?(b):((b)==1.0?(a):(a)*(b)))
#endif

template<class T> int  
ResampleMachine::do_resample(blitz::Array<T,2> A,  blitz::Array<T,2> B ){
#ifdef DEBUG
				bx_[0].print();
				bx_[1].print();
#endif
				double tmp;
				for (int i=0; i<bx_[0].size();i++) {
						Bnode &xx=bx_[0].get(i);
						for (int j=0; j<bx_[1].size(); j++) {
						 Bnode &yy=bx_[1].get(j);
						 std::list<Bedge>::iterator fx=xx.begin();
						 std::list<Bedge>::iterator fy=yy.begin();
						 while(fx!=xx.end()) {
							while(fy!=yy.end()) {
								tmp=((*fx).w)*((*fy).w);
							  //tmp=FMULT(((*fx).w),((*fy).w));
								cell_weight_(i,j)+=tmp;
								//cout<<"add to ("<<i<<","<<j<<") from ["<<(*fx).id<<","<<(*fy).id<<"]"<<endl;
								A(i,j)+=tmp*B((*fx).id,(*fy).id);
								std::advance(fy,1);
							}
                fy=yy.begin();
								std::advance(fx,1);
						 }
						}
				}
#ifdef DEBUG
				cout<<" Bc "<<B<<endl;
				cout<<" A "<<A<<endl;
				cout<<" Weight "<<cell_weight_<<endl;

       cout<<" size "<<nx_<<","<<ny_<<endl;
#endif
				for (int i=0; i<nx_; i++) {
				 for (int j=0; j<ny_; j++) {
          if(cell_weight_(i,j)!=0)
           A(i,j)/=cell_weight_(i,j);
				 }
				}
				return 0;
}

template<class T> int  
ResampleMachine::do_resample(blitz::Array<T,2> A,  blitz::Array<T,2> B,  
			  VellsFlagType *Fp, bool has_flags, 
				blitz::Array<VellsFlagType,2> Aflag) {
				double tmp;
         //get Flags
				 blitz::Array<VellsFlagType,2> F(const_cast<VellsFlagType*>(Fp),blitz::shape(B.extent(0),B.extent(1)),blitz::neverDeleteData);

#ifdef DEBUG
				 cout <<"Flags "<<F<<endl;
#endif
				for (int i=0; i<bx_[0].size();i++) {
						Bnode &xx=bx_[0].get(i);
						for (int j=0; j<bx_[1].size(); j++) {
						 Bnode &yy=bx_[1].get(j);
						 std::list<Bedge>::iterator fx=xx.begin();
						 std::list<Bedge>::iterator fy=yy.begin();
						 while(fx!=xx.end()) {
							while(fy!=yy.end()) {
								tmp=((*fx).w)*((*fy).w);
							  //tmp=FMULT(((*fx).w),((*fy).w));
								cell_weight_(i,j)+=tmp;

                if (!F((*fx).id,(*fy).id)) {
								A(i,j)+=tmp*B((*fx).id,(*fy).id);
								} else {
								Aflag(i, j)++;
								}
								std::advance(fy,1);
							}
                fy=yy.begin();
								std::advance(fx,1);
						 }
						}
				}

#ifdef DEBUG
				cout<<" Bc "<<B<<endl;
				cout<<" A "<<A<<endl;
				cout<<" Weight "<<cell_weight_<<endl;

       cout<<" size "<<nx_<<","<<ny_<<endl;
#endif
				for (int i=0; i<nx_; i++) {
				 for (int j=0; j<ny_; j++) {
          if(cell_weight_(i,j)!=0)
           A(i,j)/=cell_weight_(i,j);
				 }
				}
        //A/=cell_weight_; 
				return 0;
}

#ifndef MAX
#define MAX(a,b)\
				(a>b?a:b)
#endif
#ifndef MIN
#define MIN(a,b)\
				(a<b?a:b)
#endif

#ifndef INSERT
#define INSERT(i,j,w,gg)\
				Bnode &b=(gg).get((j));\
        Bedge ed((i),(w));\
        b.append(ed);
#endif

//update the graph for input cell number incell, that is included
//within the range of output cells in range cell1,cell2
void
ResampleMachine::insert(int incell,int cell1, int cell2, int axis,
	blitz::Array<double,1> incellsize,blitz::Array<double,1> outcellsize,
	blitz::Array<double,1> incenter,blitz::Array<double,1> outcenter
								) {
//the trivial case where the input cell is enclosed by one output cell

 if (cell1==cell2) {
  //find intersection length - must be the orignal
	//cell length, so the weight is 1
  INSERT(incell,cell1,1.0,bx_[axis]);	
 } else {
	double ledge=incenter(incell)-incellsize(incell)*0.5;
	double redge=incenter(incell)+incellsize(incell)*0.5;
	for (int i=cell1; i<=cell2;i++) {
 //find common length = min(right_edge)-max(left_edge)
  double ll=outcenter(i)-outcellsize(i)*0.5; 
  double rr=outcenter(i)+outcellsize(i)*0.5; 
	double comm=MIN(rr,redge)-MAX(ll,ledge);
#ifdef DEBUG
	cout<<"W ="<<comm<<"/"<<incellsize(incell)<<endl;
#endif
	double weight=comm/incellsize(incell);
  INSERT(incell,i,weight,bx_[axis]);	
	}
 }
}


} // namespace Meq
