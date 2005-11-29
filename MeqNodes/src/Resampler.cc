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

	blitz::Array<double,1> tempx(nx_+2);
	tempx(blitz::Range(1,nx_))=xax;
	tempx(0)=xstart;
	tempx(nx_+1)=xend;
#ifdef DEBUG
	cout<<"In X "<<tempx<<endl;
#endif

	blitz::Array<double,1> tempy(ny_+2);
	tempy(blitz::Range(1,ny_))=yax;
	tempy(0)=ystart;
	tempy(ny_+1)=yend;

#ifdef DEBUG
	cout<<"In Y "<<tempy<<endl;
#endif
	//if out cells are smaller than in cells
	//it will be taken to be idential for the moment
  identical_=(nx_>nxs)||(ny_>nys) 
					||((nx_==nxs)&&(ny_==nys));	
#ifdef DEBUG
  cout<<"Itentical "<<identical_<<endl;
#endif
  // array of indices
	xindex_.resize(nxs);
	yindex_.resize(nys);

  // do the search
	for (int i=0; i<nxs;i++)
	  xindex_(i)=bin_search(tempx,xaxs(i),0,nx_+1);
	for (int i=0; i<nys;i++)
	  yindex_(i)=bin_search(tempy,yaxs(i),0,ny_+1);

#ifdef DEBUG
	cout<<"X index "<<xindex_<<endl;
	cout<<"Y index "<<yindex_<<endl;
#endif
	//now calculate the weights
	//each old cell is smaller than new cells. So there are 2 cases to consider
	// --|  /.....\  |-- old cell completely within new cell
	// /...--|....\  |-- old cell shared by 2 new cells     
	// So for each axis we have 2 wights for each old cell (left,right) 
	// The area is proportional to the product of the weights of X,Y axes
	// Note also that left,right weights sum up to 1.
	// Consider special cases where xindex==0 or xindex==nx_
	// because they are at the domain boundary.

	//just for the time being assume exact resampling. That is
	//if an old cell center belongs to a new cell, that old cell is
	//entirely included in the new cell
	
	xweights_.resize(nxs);  
	for (int i=0; i<nxs; i++) {
     if(xindex_(i)==0) {
						 xweights_[0](i)=0;
						 xweights_[1](i)=1;
		 } else if(xindex_(i)==nx_) {
						 xweights_[0](i)=1;
						 xweights_[1](i)=0;
		 } else {
						 if ((xaxs(i)-xax(xindex_(i)-1)) >
														 (xcellsize(xindex_(i)-1)+inxcellsize(i))/2) {
						  xweights_[0](i)=0;
						  xweights_[1](i)=1;
						 }else if ((-xaxs(i)+xax(xindex_(i))) >
														 (xcellsize(xindex_(i))+inxcellsize(i))/2) {
						  xweights_[0](i)=1;
						  xweights_[1](i)=0;
						 } else {
						  xweights_[0](i)=((xcellsize(xindex_(i)-1)+inxcellsize(i))/2
                -(xaxs(i)-xax(xindex_(i)-1)))/inxcellsize(i);
						  xweights_[1](i)=1-xweights_[0](i);
						 }
		 }
	}

#ifdef DEBUG
	cout<<"X weights"<<xweights_<<endl;
#endif
	yweights_.resize(nys);  
	for (int i=0; i<nys; i++) {
     if(yindex_(i)==0) {
						 yweights_[0](i)=0;
						 yweights_[1](i)=1;
		 } else if(yindex_(i)==ny_) {
						 yweights_[0](i)=1;
						 yweights_[1](i)=0;
		 } else {
						 if ((yaxs(i)-yax(yindex_(i)-1)) > 
														 (ycellsize(yindex_(i)-1)+inycellsize(i))/2) {
						  yweights_[0](i)=0;
						  yweights_[1](i)=1;
						 } else if ((-yaxs(i)+yax(yindex_(i))) > 
														 (ycellsize(yindex_(i))+inycellsize(i))/2) {
						  yweights_[0](i)=1;
						  yweights_[1](i)=0;
						 } else {
						  yweights_[0](i)=((ycellsize(yindex_(i)-1)+inycellsize(i))/2
                -(yaxs(i)-yax(yindex_(i)-1)))/inycellsize(i);
						  yweights_[1](i)=1-yweights_[0](i);
						 }
		 }
	}

#ifdef DEBUG
	cout<<"Y weights"<<yweights_<<endl;
#endif
	//resize the array to store cumulative flags+weights
	cell_weight_.resize(nx_,ny_);
	//make it zero
  cell_weight_=0; 
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
				//before doing the proper summation, find out limits
				//for boundary points
        int xlow=0;
        while(xindex_(xlow)==0 && xlow <nxs) xlow++;				
        int xhigh=nxs-1;
        while(xindex_(xhigh)==nx_ && xhigh>=0) xhigh--;				
        int ylow=0;
        while(yindex_(ylow)==0 && ylow <nys) ylow++;				
        int yhigh=nys-1;
        while(yindex_(yhigh)==ny_ && yhigh>=0) yhigh--;				
#ifdef DEBUG
        cout<<"Limits ["<<xlow<<","<<xhigh<<"]["<<ylow<<","<<yhigh<<"]"<<endl; 
#endif

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
         do_resample(xlow, xhigh, nxs, ylow, yhigh, nys, 
				  A,  B);
				  out.setValue(new Vells(A));
				}else {
         //allocate memory for flags
				blitz::Array<VellsFlagType,2> Aflag(nx_,ny_); 
				 Aflag=0;
         do_resample(xlow, xhigh, nxs, ylow, yhigh, nys, 
				  A,  B,  F, invl.hasDataFlags(), Aflag);
				  out.setValue(new Vells(A));
					out.setDataFlags(new Vells(Aflag));
				}
				}else{
				 blitz::Array<dcomplex,2> Bc=invl.as<dcomplex,2>()(LoRange::all(),LoRange::all()); 
         blitz::Array<dcomplex,2> Ac(nx_,ny_);
				 Ac = 0;

#ifdef DEBUG
				 cout<<" Ac "<<Ac<<endl;
				 cout<<" Bc "<<Bc<<endl;
#endif
				if (!invl.hasDataFlags() ) {
         do_resample(xlow, xhigh, nxs, ylow, yhigh, nys, 
				  Ac,  Bc);
				  out.setValue(new Vells(Ac));
				}else{
				 blitz::Array<VellsFlagType,2> Aflag(nx_,ny_); 
				 Aflag=0;
         do_resample(xlow, xhigh, nxs, ylow, yhigh, nys, 
				  Ac,  Bc,  F, invl.hasDataFlags(),Aflag);
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


template<class T> int  
ResampleMachine::do_resample(int xlow, int xhigh, int nxs, int ylow, int yhigh, int nys, 
				blitz::Array<T,2> A,  blitz::Array<T,2> B ){
				double tmp;
				for (int i=0;i<xlow;i++) {
				 for (int j=0;j<ylow;j++) {
             tmp=xweights_[1](i)*yweights_[1](j);
             cell_weight_(xindex_(i), yindex_(j))+=tmp;
             A(xindex_(i), yindex_(j))+=tmp*B(i,j);
				 }
				 for (int j=ylow;j<=yhigh;j++) {
             tmp=xweights_[1](i)*yweights_[0](j);
             cell_weight_(xindex_(i), yindex_(j)-1)+=tmp;
             A(xindex_(i), yindex_(j)-1)+=tmp*B(i,j);
						 tmp=xweights_[1](i)*yweights_[1](j);
             cell_weight_(xindex_(i), yindex_(j))+=tmp;
             A(xindex_(i), yindex_(j))+=tmp*B(i,j);
				 }
				 for (int j=yhigh+1;j<nys;j++) {
						tmp=xweights_[1](i)*yweights_[0](j);
            cell_weight_(xindex_(i), yindex_(j)-1)+=tmp;
             A(xindex_(i), yindex_(j)-1)+=tmp*B(i,j);
				 }
				}
				for (int i=xlow;i<=xhigh;i++) {
				 for (int j=0;j<ylow;j++) {
						tmp=xweights_[0](i)*yweights_[1](j);
            cell_weight_(xindex_(i)-1, yindex_(j))+=tmp;
             A(xindex_(i)-1, yindex_(j))+=tmp*B(i,j);
						tmp=xweights_[1](i)*yweights_[1](j);
            cell_weight_(xindex_(i), yindex_(j))+=tmp;
             A(xindex_(i), yindex_(j))+=tmp*B(i,j);
				 }
				 for (int j=ylow;j<=yhigh;j++) {
						 tmp=xweights_[0](i)*yweights_[0](j);
             cell_weight_(xindex_(i)-1, yindex_(j)-1)+=tmp;
             A(xindex_(i)-1, yindex_(j)-1)+=tmp*B(i,j);
						 tmp=xweights_[0](i)*yweights_[1](j);
             cell_weight_(xindex_(i)-1, yindex_(j))+=tmp;
             A(xindex_(i)-1, yindex_(j))+=tmp*B(i,j);
						 tmp=xweights_[1](i)*yweights_[0](j);
             cell_weight_(xindex_(i), yindex_(j)-1)+=tmp;
             A(xindex_(i), yindex_(j)-1)+=tmp*B(i,j);
						 tmp=xweights_[1](i)*yweights_[1](j);
             cell_weight_(xindex_(i), yindex_(j))+=tmp;
             A(xindex_(i), yindex_(j))+=tmp*B(i,j);
				 }
				 for (int j=yhigh+1;j<nys;j++) {
						 tmp=xweights_[0](i)*yweights_[0](j);
             cell_weight_(xindex_(i)-1, yindex_(j)-1)+=tmp;
             A(xindex_(i)-1, yindex_(j)-1)+=tmp*B(i,j);
						 tmp=xweights_[1](i)*yweights_[0](j);
             cell_weight_(xindex_(i), yindex_(j)-1)+=tmp;
             A(xindex_(i), yindex_(j)-1)+=tmp*B(i,j);
				 }
				}
				for (int i=xhigh+1;i<nxs;i++) {
				 for (int j=0;j<ylow;j++) {
						 tmp=xweights_[0](i)*yweights_[1](j);
             cell_weight_(xindex_(i)-1, yindex_(j))+=tmp;
             A(xindex_(i)-1, yindex_(j))+=tmp*B(i,j);
				 }
				 for (int j=ylow;j<=yhigh;j++) {
						 tmp=xweights_[0](i)*yweights_[0](j);
             cell_weight_(xindex_(i)-1, yindex_(j)-1)+=tmp;
             A(xindex_(i)-1, yindex_(j)-1)+=tmp*B(i,j);
						 tmp=xweights_[0](i)*yweights_[1](j);
             cell_weight_(xindex_(i)-1, yindex_(j))+=tmp;
             A(xindex_(i)-1, yindex_(j))+=tmp*B(i,j);
				 }
				 for (int j=yhigh+1;j<nys;j++) {
						 tmp=xweights_[0](i)*yweights_[0](j);
             cell_weight_(xindex_(i)-1, yindex_(j)-1)+=tmp;
             A(xindex_(i)-1, yindex_(j)-1)+=tmp*B(i,j);
				 }
				}

#ifdef DEBUG
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
ResampleMachine::do_resample(int xlow, int xhigh, int nxs, int ylow, int yhigh, int nys, 
				blitz::Array<T,2> A,  blitz::Array<T,2> B,  
			  VellsFlagType *Fp, bool has_flags, 
				blitz::Array<VellsFlagType,2> Aflag) {
				double tmp;
         //get Flags
				 blitz::Array<VellsFlagType,2> F(const_cast<VellsFlagType*>(Fp),blitz::shape(B.extent(0),B.extent(1)),blitz::neverDeleteData);

#ifdef DEBUG
				 cout <<"Flags "<<F<<endl;
#endif
				for (int i=0;i<xlow;i++) {
				 for (int j=0;j<ylow;j++) {
             if (!F(i,j)) {
             tmp=xweights_[1](i)*yweights_[1](j);
             cell_weight_(xindex_(i), yindex_(j))+=tmp;
             A(xindex_(i), yindex_(j))+=tmp*B(i,j);
						 }
				 }
				 for (int j=ylow;j<=yhigh;j++) {
             if (!F(i,j)) {
             tmp=xweights_[1](i)*yweights_[0](j);
             cell_weight_(xindex_(i), yindex_(j)-1)+=tmp;
             A(xindex_(i), yindex_(j)-1)+=tmp*B(i,j);
						 tmp=xweights_[1](i)*yweights_[1](j);
             cell_weight_(xindex_(i), yindex_(j))+=tmp;
             A(xindex_(i), yindex_(j))+=tmp*B(i,j);
						 }
				 }
				 for (int j=yhigh+1;j<nys;j++) {
             if (!F(i,j)) {
						tmp=xweights_[1](i)*yweights_[0](j);
            cell_weight_(xindex_(i), yindex_(j)-1)+=tmp;
             A(xindex_(i), yindex_(j)-1)+=tmp*B(i,j);
						 }
				 }
				}
				for (int i=xlow;i<=xhigh;i++) {
				 for (int j=0;j<ylow;j++) {
             if (!F(i,j)) {
						tmp=xweights_[0](i)*yweights_[1](j);
            cell_weight_(xindex_(i)-1, yindex_(j))+=tmp;
             A(xindex_(i)-1, yindex_(j))+=tmp*B(i,j);
						tmp=xweights_[1](i)*yweights_[1](j);
            cell_weight_(xindex_(i), yindex_(j))+=tmp;
             A(xindex_(i), yindex_(j))+=tmp*B(i,j);
						 }
				 }
				 for (int j=ylow;j<=yhigh;j++) {
             if (!F(i,j)) {
						 tmp=xweights_[0](i)*yweights_[0](j);
             cell_weight_(xindex_(i)-1, yindex_(j)-1)+=tmp;
             A(xindex_(i)-1, yindex_(j)-1)+=tmp*B(i,j);
						 tmp=xweights_[0](i)*yweights_[1](j);
             cell_weight_(xindex_(i)-1, yindex_(j))+=tmp;
             A(xindex_(i)-1, yindex_(j))+=tmp*B(i,j);
						 tmp=xweights_[1](i)*yweights_[0](j);
             cell_weight_(xindex_(i), yindex_(j)-1)+=tmp;
             A(xindex_(i), yindex_(j)-1)+=tmp*B(i,j);
						 tmp=xweights_[1](i)*yweights_[1](j);
             cell_weight_(xindex_(i), yindex_(j))+=tmp;
             A(xindex_(i), yindex_(j))+=tmp*B(i,j);
						 }else{
										 Aflag(xindex_(i)-1, yindex_(j)-1)++;
						 }

				 }
				 for (int j=yhigh+1;j<nys;j++) {
             if (!F(i,j)) {
						 tmp=xweights_[0](i)*yweights_[0](j);
             cell_weight_(xindex_(i)-1, yindex_(j)-1)+=tmp;
             A(xindex_(i)-1, yindex_(j)-1)+=tmp*B(i,j);
						 tmp=xweights_[1](i)*yweights_[0](j);
             cell_weight_(xindex_(i), yindex_(j)-1)+=tmp;
             A(xindex_(i), yindex_(j)-1)+=tmp*B(i,j);
						 }
				 }
				}
				for (int i=xhigh+1;i<nxs;i++) {
				 for (int j=0;j<ylow;j++) {
             if (!F(i,j)) {
						 tmp=xweights_[0](i)*yweights_[1](j);
             cell_weight_(xindex_(i)-1, yindex_(j))+=tmp;
             A(xindex_(i)-1, yindex_(j))+=tmp*B(i,j);
						 }
				 }
				 for (int j=ylow;j<=yhigh;j++) {
             if (!F(i,j)) {
						 tmp=xweights_[0](i)*yweights_[0](j);
             cell_weight_(xindex_(i)-1, yindex_(j)-1)+=tmp;
             A(xindex_(i)-1, yindex_(j)-1)+=tmp*B(i,j);
						 tmp=xweights_[0](i)*yweights_[1](j);
             cell_weight_(xindex_(i)-1, yindex_(j))+=tmp;
             A(xindex_(i)-1, yindex_(j))+=tmp*B(i,j);
						 }
				 }
				 for (int j=yhigh+1;j<nys;j++) {
             if (!F(i,j)) {
						 tmp=xweights_[0](i)*yweights_[0](j);
             cell_weight_(xindex_(i)-1, yindex_(j)-1)+=tmp;
             A(xindex_(i)-1, yindex_(j)-1)+=tmp*B(i,j);
						 }
				 }
				}

#ifdef DEBUG
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
} // namespace Meq
