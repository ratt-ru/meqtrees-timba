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
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <complex>

namespace Meq {

const HIID FFlagDensity = AidFlag|AidDensity;
const HIID FMode = AidMode;

const HIID FKeepAxes = AidCommon|AidAxes;

//##ModelId=400E5355029C
Resampler::Resampler()
: Node(1), // 1 child expected
  flag_mask(-1),mode(1),flag_bit(0),flag_density(0.5)
{}

//##ModelId=400E5355029D
Resampler::~Resampler()
{}

void Resampler::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
//  rec[FIntegrate].get(integrate,initializing);
  rec[FFlagMask].get(flag_mask,initializing);
  rec[FMode].get(mode,initializing);
  rec[FFlagBit].get(flag_bit,initializing);
  rec[FFlagDensity].get(flag_density,initializing);

	//get axes to keep
	std::vector<HIID> tmp=keep_axes_;
	if (rec[FKeepAxes].get_vector(tmp,initializing) ) {
	  if (tmp.size()!=0) {
	    keep_axes_.resize(tmp.size());
		  keep_axes_=tmp;
		}

	}

}

int Resampler::getResult (Result::Ref &resref, 
                           const std::vector<Result::Ref> &childres,
                           const Request &request,bool)
{
  Assert(childres.size()==1);

  const Result &chres = *( childres.front() );
	//if result has no cells, must be a scalar
	//pass it up
  if (!chres.hasCells() || !request.hasCells()) {
    resref.copy(childres.front());
    return 0;
	}
  const Cells &incells = chres.cells();
  const Cells &outcells = request.cells();

	//envelope of the two domains
	Domain::Ref  newdomain(new Domain(Domain::envelope(incells.domain(),outcells.domain())));
	
	//Domain *newdomain=incells.domain().clone();
	//newdomain.envelope(outcells.domain());
	Cells::Ref cells_ref;
	Cells &newcells=cells_ref<<=new Cells(*newdomain);
	bool use_new_cells=false;
	for( int ax=0; ax<Axis::MaxAxis; ax++ ) {
		//check to see if we keep this axes
		bool keep_this=false;
		for(unsigned int ii=0; ii<keep_axes_.size(); ii++) {
	    if(keep_axes_[ii]==Axis::axisId(ax)) {
					keep_this=true;
			}
	  }
		if (outcells.isDefined(ax) and !keep_this) {
			newcells.setCells(ax,outcells.center(ax),outcells.cellSize(ax));
		} else if (keep_this & incells.isDefined(ax)) {
			newcells.setCells(ax,incells.center(ax),incells.cellSize(ax));
			use_new_cells=true;
		} else if (incells.isDefined(ax)) {
			double x0=incells.domain().start(ax);
			double x1=incells.domain().end(ax);
			newcells.setCells(ax,x0,x1,1);
		}
	}


	ResamplerFactory resfac;
  ResampleMachine *resampler=0;
  // create resampler: interpolation
	if (mode==1) {
   resampler=resfac.create(ResamplerFactory::INTERPOLATOR,0);
	} else { //mode==2: integration: used for real (MS) data
   resampler=resfac.create(ResamplerFactory::INTEGRATOR,0);
	}
	if (!use_new_cells) {
	 resampler->setup(incells, outcells);
	} else {
#ifdef DEBUG
	 cout<<"Using new cells"<<endl;
#endif
	 resampler->setup(incells, newcells);
	}

  // return child result directly if nothing is to be done
  if( resampler->isIdentical() )
  {
    resref.copy(childres.front());
    //resref=childres[0];
    return 0;
  }
  // do the resampling  
  resampler->setFlagPolicy(flag_mask,flag_bit,flag_density);
  int nvs = chres.numVellSets();
  Result & result = resref <<= new Result(nvs,chres.isIntegrated());
  for( int ivs=0; ivs<nvs; ivs++ )
  {
    VellSet::Ref ref;
		const VellSet &invs=chres.vellSet(ivs);
		//only non empty vellsets are handled
		if (!invs.isEmpty()) {
		VellSet &outvs= ref<<= new VellSet(invs.numSpids(),invs.numPertSets());
    // call the resampler
      resampler->apply(invs,outvs);
      result.setVellSet(ivs,ref);
		}
  }

	if (!use_new_cells) {
	 result.setCells(outcells);
	} else {
		result.setCells(newcells);
	}
	result.setDims(chres.dims());
	delete resampler;
  return 0;
}


//binary search
int ResampleMachine::bin_search(std::vector<double> xarr,double x,int i_start,int i_end) {
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
		if (xarr[i_start]==x)
				return i_start;
	  else {
			cerr<<"ERROR: bin search error 1"<<endl;
	    return -1;
    }
	}

	//trivial case with length 2 array
	if (i_end==i_start+1) {
		if (x>=xarr[i_start] && x<xarr[i_end]) {
				return i_start;
		} else {
			cerr<<"ERROR: bin search error 2"<<endl;
	    return -2;
    }
	}

	//compare the mid point
	int i=(int)((i_start+i_end)/2);
	if (x>=xarr[i] && x<xarr[i+1]) {
		 return i;
	} else {
		//go to lower half of the upper half of the array
		if (x<xarr[i])
			return bin_search(xarr,x,i_start,i);
		else 
			return bin_search(xarr,x,i,i_end);
	}

	//will not reach here
  cerr<<"ERROR: bin search error 3"<<endl;
  return -3;
}



//binary search
int ResampleMachine::bin_search(blitz::Array<double,1> xarr,double x,int i_start,int i_end) {
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
			cerr<<"ERROR: bin search error 1"<<endl;
	    return -1;
    }
	}

	//trivial case with length 2 array
	if (i_end==i_start+1) {
		if (x>=xarr(i_start) && x<xarr(i_end)) {
				return i_start;
		} else {
			cerr<<"ERROR: bin search error 2"<<endl;
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
  cerr<<"ERROR: bin search error 3"<<endl;
  return -3;
}


////////////////////////////////////////////////////////////////////
void  
Integrator::setup(const Cells &in, const Cells &out) {

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

	int nxs=nx0_=xaxs.extent(0);
	int nys=ny0_=yaxs.extent(0);

	//if out cells are smaller than in cells
	//it will be taken to be idential for the moment
  identical_=((nx_==nxs)&&(ny_==nys));	
#ifdef DEBUG
  cout<<"Identical "<<identical_<<endl;
#endif
  //we need a resampler only if not identical
	//so if idential_, stop here
	if (identical_) {
			return;
	}
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


#ifndef FMULT
#define FMULT(a,b)\
				((a)==1.0?(b):((b)==1.0?(a):(a)*(b)))
#endif

template<class T> int  
Integrator::do_resample(blitz::Array<T,2> A,  blitz::Array<T,2> B ){
#ifdef DEBUG
				bx_[0].print();
				bx_[1].print();
#endif
        int nx0=B.extent(0);
        int ny0=B.extent(1);

				double tmp;
				cell_weight_=0;
        //handle scalar case as a special case
        if (nx0==1 || ny0==1) {
          if (nx0==1 && ny0==1) {
            A=B(0,0)*nx0_*ny0_/(nx_*ny_); //divide by correct weight
            return 0;
          } else if(nx0==1) {
        	  for (int i=0; i<bx_[0].size();i++) {
						Bnode &xx=bx_[0].get(i);
						for (int j=0; j<bx_[1].size(); j++) {
						 Bnode &yy=bx_[1].get(j);
						 std::list<Bedge>::iterator fx=xx.begin();
						 std::list<Bedge>::iterator fy=yy.begin();
						 while(fx!=xx.end()) {
							while(fy!=yy.end()) {
								tmp=((*fx).w)*((*fy).w);
								cell_weight_(i,j)+=tmp;
								A(i,j)+=tmp*B(0,(*fy).id);
								std::advance(fy,1);
							}
                fy=yy.begin();
								std::advance(fx,1);
						 }
						}
				   }
          } else {
        	  for (int i=0; i<bx_[0].size();i++) {
						Bnode &xx=bx_[0].get(i);
						for (int j=0; j<bx_[1].size(); j++) {
						 Bnode &yy=bx_[1].get(j);
						 std::list<Bedge>::iterator fx=xx.begin();
						 std::list<Bedge>::iterator fy=yy.begin();
						 while(fx!=xx.end()) {
							while(fy!=yy.end()) {
								tmp=((*fx).w)*((*fy).w);
								cell_weight_(i,j)+=tmp;
								A(i,j)+=tmp*B((*fx).id,0);
								std::advance(fy,1);
							}
                fy=yy.begin();
								std::advance(fx,1);
						 }
						}
				   }
          }

        } else {

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
       }
#ifdef DEBUG
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

#define DEBUG
//return 0 if no new flags were created,
//return 1 if new flags were created
template<class T> int  
Integrator::do_resample(blitz::Array<T,2> A,  blitz::Array<T,2> B,  
			  VellsFlagType *Fp, bool has_flags, 
				blitz::Array<VellsFlagType,2> Aflag) {
				double tmp;
				int create_flags=0;
         //get Flags
				 blitz::Array<VellsFlagType,2> F(const_cast<VellsFlagType*>(Fp),blitz::shape(B.extent(0),B.extent(1)),blitz::neverDeleteData);
         //an array to count actual contributed cell count
				 blitz::Array<int,2> Acell(nx_,ny_); 
         //an array to store contributed flag value
				 blitz::Array<int,2> Aflg(nx_,ny_); 

#ifdef DEBUG
				 cout <<"Flags "<<F<<endl;
#endif
				 Acell=0;
				 Aflg=0;
				 cell_weight_=0;
        int nx0=B.extent(0);
        int ny0=B.extent(1);


        //handle scalar case as a special case
        if (nx0==1 || ny0==1) {
          if (nx0==1 && ny0==1) {
            A=B(0,0)*nx0_*ny0_/(nx_*ny_); //divide by correct weight
            return 0;
          } else if(nx0==1) {
        	  for (int i=0; i<bx_[0].size();i++) {
						Bnode &xx=bx_[0].get(i);
						for (int j=0; j<bx_[1].size(); j++) {
						 Bnode &yy=bx_[1].get(j);
						 std::list<Bedge>::iterator fx=xx.begin();
						 std::list<Bedge>::iterator fy=yy.begin();
						 while(fx!=xx.end()) {
							while(fy!=yy.end()) {
								tmp=((*fx).w)*((*fy).w);
								cell_weight_(i,j)+=tmp;
								A(i,j)+=tmp*B(0,(*fy).id);
								std::advance(fy,1);
							}
                fy=yy.begin();
								std::advance(fx,1);
						 }
						}
				   }
          } else {
        	  for (int i=0; i<bx_[0].size();i++) {
						Bnode &xx=bx_[0].get(i);
						for (int j=0; j<bx_[1].size(); j++) {
						 Bnode &yy=bx_[1].get(j);
						 std::list<Bedge>::iterator fx=xx.begin();
						 std::list<Bedge>::iterator fy=yy.begin();
						 while(fx!=xx.end()) {
							while(fy!=yy.end()) {
								tmp=((*fx).w)*((*fy).w);
								cell_weight_(i,j)+=tmp;
								A(i,j)+=tmp*B((*fx).id,0);
								std::advance(fy,1);
							}
                fy=yy.begin();
								std::advance(fx,1);
						 }
						}
				   }
          }

        } else {
				 for (int i=0; i<bx_[0].size();i++) {
						Bnode &xx=bx_[0].get(i);
						for (int j=0; j<bx_[1].size(); j++) {
						 Bnode &yy=bx_[1].get(j);
						 std::list<Bedge>::iterator fx=xx.begin();
						 std::list<Bedge>::iterator fy=yy.begin();
						 while(fx!=xx.end()) {
							while(fy!=yy.end()) {
							  //tmp=FMULT(((*fx).w),((*fy).w));
                Acell(i,j)++;
                if (!(F((*fx).id,(*fy).id) &flag_mask_)) {
								// no flags, or flags are ignored
								tmp=((*fx).w)*((*fy).w);
								cell_weight_(i,j)+=tmp;
								A(i,j)+=tmp*B((*fx).id,(*fy).id);
								} else {
									//we have a flag
								Aflag(i,j)++;
								Aflg(i,j)|=(F((*fx).id,(*fy).id) &flag_mask_);
								}
								std::advance(fy,1);
							}
                fy=yy.begin();
								std::advance(fx,1);
						 }
						 //cout<<"A("<<i<<","<<j<<")="<<A(i,j)<<endl;
						}
				}
      }
#ifdef DEBUG

			 cout<<" Weight "<<cell_weight_<<endl;
       cout<<" size "<<nx_<<","<<ny_<<endl;
       cout<<" Acell"<<Acell<<endl;
       cout<<" Aflg"<<Aflg<<endl;
       cout<<" Afalg"<<Aflag<<endl;
			 cout<<" mask="<<flag_mask_<<" density="<<flag_density_<<" bit="<<flag_bit_<<endl;
#endif
				for (int i=0; i<nx_; i++) {
				 for (int j=0; j<ny_; j++) {
          if(cell_weight_(i,j)!=0)
           A(i,j)/=cell_weight_(i,j);
					//recalculate flags if any
					if (static_cast<double>(Aflag(i,j))/static_cast<double>(Acell(i,j)) >flag_density_) {
           Aflag(i,j)=(flag_bit_?flag_bit_:Aflg(i,j));
					 if (Aflag(i,j))
					  create_flags=1;
					} else {
           Aflag(i,j)=0; //do not flag output
					}
				 }
				}
				return create_flags;
}

#undef DEBUG

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
Integrator::insert(int incell,int cell1, int cell2, int axis,
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


int Integrator::apply(const VellSet &in, VellSet &out)
{

				Vells invl=in.getValue();
				int nxs,nys;
				nxs=invl.extent(0);
				nys=invl.extent(1);

				VellsFlagType *F=0;
				//check for flags
				if (invl.hasDataFlags() ) {
        Vells &flvl=const_cast<Vells &>(invl.dataFlags());

				blitz::Array<VellsFlagType,2> FF=flvl.as<VellsFlagType,2>()(blitz::Range(0,nxs-1),blitz::Range(0,nys-1)); 

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
				 blitz::Array<double,2> B=invl.as<double,2>()(blitz::Range(0,nxs-1),blitz::Range(0,nys-1)); 
         blitz::Array<double,2> A(nx_,ny_);
				 A=0;
#ifdef DEBUG
				 cout<<" A "<<A.shape()<<endl;
				 cout<<" B "<<B.shape()<<endl;
#endif
				if (!invl.hasDataFlags() ) {
         do_resample(A,  B);
				  out.setValue(new Vells(A));
				}else {
         //allocate memory for flags
				blitz::Array<VellsFlagType,2> Aflag(nx_,ny_); 
				 Aflag=0;
         int has_flags=do_resample( A,  B,  F, invl.hasDataFlags(), Aflag);
				  out.setValue(new Vells(A));
				 if (has_flags)
					out.setDataFlags(new Vells(Aflag));
				}
				}else{
				 blitz::Array<dcomplex,2> Bc=invl.as<dcomplex,2>()(blitz::Range(0,nxs-1),blitz::Range(0,nys-1)); 
         blitz::Array<dcomplex,2> Ac(nx_,ny_);
				 Ac = make_dcomplex(0);

				if (!invl.hasDataFlags() ) {
         do_resample( Ac,  Bc);
				  out.setValue(new Vells(Ac));
				}else{
				 blitz::Array<VellsFlagType,2> Aflag(nx_,ny_); 
				 Aflag=0;
         int has_flags=do_resample( Ac,  Bc,  F, invl.hasDataFlags(),Aflag);
				 out.setValue(new Vells(Ac));
				 // only attach flags if new flags were created
				 if (has_flags)
					out.setDataFlags(new Vells(Aflag));
				}
				}

				return 0;
}

////////////////////////////////////////////////////////////////////////
// ********************  INTERPOLATOR *********************************

//1D cubic hermite interpolation
//Piecewise Cubic Hermite Imterpolation
// In : grid points xin and values yin size n x 1
// In : interpolating points xout size m x 1
// out : interpolated values yout size m x 1
//
// References:
// F. N. Fritsch and R. E. Carlson, "Monotone Piecewise Cubic
// Interpolation", SIAM J. Numerical Analysis 17, 1980, 238-246.
// David Kahaner, Cleve Moler and Stephen Nash, Numerical Methods
// and Software, Prentice Hall, 1988.
// 
template<class T> void
 Interpolator::pchip_int(blitz::Array<double,1> xin, blitz::Array<T,1> yin, int n, blitz::Array<double,1> xout,  blitz::Array<T,1> yout, int m, blitz::Array<int,1> xindex) {

	//special case: n==1 and m> 1, oversample from a scalar, just copy the value
	if (n==1 && m >=1) {yout=yin(0); return;}

	//another special case, input and output is exact
	int is_identical=1;
	if (m==n) {
		int i=0;
		while(is_identical && i<n) {	
			if (xin(i)!=xout(i)) {is_identical=0; break;}
			i++;
		}
		if (i==n && is_identical) {
#ifdef DEBUG
			cout<<"Identical, ignoring"<<endl;
#endif
      yout=yin; return;
		}
	}
	//array to store first derivatives used in interpolation
	blitz::Array<T,1> d(n);
	//array to store first divided differences
	blitz::Array<T,1> del(n);
	//Note: the values of above arrays at the end points are determined 
	//in a special 3 point way
	//array to store x differences
	blitz::Array<double,1> h(n);

	if (n==2) {
		//linear interpolation
		h(0)=h(1)=(xin(1)-xin(0));
		del(0)=del(1)=d(0)=d(1)=(yin(1)-yin(0))/h(0);
	  for (int i=0; i<m; i++) {
	   yout(i)=d(0)*(xout(i)-xin(0))+yin(0);
		}
#ifdef DEBUG
	cout<<"Yout"<<yout<<endl;
#endif
		return;

	} else {
	for (int i=0; i<n-1; i++) {
			h(i)=xin(i+1)-xin(i);
			del(i)=(yin(i+1)-yin(i))/h(i);
	}
	del(n-1)=del(n-2);
	h(n-1)=h(n-2);
	for (int k=1; k<n-1; k++) {
		if (del(k-1)==0 || del(k)==0 || ((del(k)) >0 && del(k-1)<0) 
									 || (del(k) <0 && del(k-1)>0) )	{
				d(k)=0;
		} else {
		//if del(k) and del(k-1) have same sign and two intervals
		//have same length, take harmonic mean
		double w1=2*h(k)+h(k-1);
		double w2=h(k)+2*h(k-1);
		d(k)=(w1+w1)/(w1/del(k-1)+w2/del(k));
		}
	}

	//slopes at endpoints
	d(0)=((2*h(0)+h(1))*del(0)-h(0)*del(1))/(h(0)+h(1));
	if (((del(1) >0 && del(0)<0) || (del(1) <0 && del(0)>0))
				&& (fabs(d(0))> 3*fabs(del(0)))) {
			d(0)=3*del(0);
	} 

	d(n-1)=((2*h(n-1)+h(n-2))*del(n-1)-h(n-1)*del(n-2))/(h(n-1)+h(n-2));
	if (((del(n-1) >0 && del(n-2)<0) || (del(n-1) <0 && del(n-2)>0))
				&& (fabs(d(n-1))> 3*fabs(del(n-1)))) {
			d(n-1)=3*del(n-1);
	} 


	}
#ifdef DEBUG
	cout<<"Xin"<<xin<<endl;
	cout<<"Yin"<<yin<<endl;
	cout<<"Xout"<<xout<<endl;
	cout<<"Idx"<<xindex<<endl;
	cout<<"d"<<d<<endl;
	cout<<"del"<<del<<endl;
	cout<<"h"<<h<<endl;
#endif

	//find the range where we can interpolate: xindex(k) >= 1 and
	// xindex(k) <= n-1
	int x_l_limit=0;
	int x_u_limit=m-1;

	while( (x_l_limit<m)&& (xindex(x_l_limit)<1) ) x_l_limit++;
	while( (x_u_limit>=0) && (xindex(x_u_limit)>n-1) ) x_u_limit--;
	//sanuty check
	if ( xindex(0)==0 && xindex(m-1)==0) { //everything to the left
  	for (int i=0; i<m; i++) {
	    yout(i)=d(0)*(xout(i)-xin(0))+yin(0);
   	}
		return;
	}  else if (xindex(0)==n && xindex(m-1)==n) { //everything to the right
  	for (int i=0; i<m; i++) {
	    yout(i)=d(n-1)*(xout(i)-xin(n-1))+yin(n-1);
	  }
    return;
	}
#ifdef DEBUG
	 cout<<"Limits : cubic interp["<<x_l_limit<<","<<x_u_limit<<"]"<<endl;
#endif

	//interpolation
	for (int i=x_l_limit; i<=x_u_limit; i++) {
		double s=xout(i)-xin(xindex(i)-1);
		double &hh=h(xindex(i)-1);
		double aa=(3*hh-2*s)*s*s/(hh*hh*hh);
		yout(i)=aa*yin(xindex(i))+(1-aa)*yin(xindex(i)-1);
		if (d(xindex(i)) !=0) {
		  yout(i)+=s*s*(s-hh)/(hh*hh)*d(xindex(i));
		}
		if (d(xindex(i)-1) !=0) {
		  yout(i)+=s*(s-hh)*(s-hh)/(hh*hh)*d(xindex(i)-1);
		}

	}
	//extrapolation
 	for (int i=0; i<x_l_limit; i++) {
	    yout(i)=d(0)*(xout(i)-xin(0))+yin(0);
 	}
	for (int i=x_u_limit+1; i<m; i++) {
	  yout(i)=d(n-1)*(xout(i)-xin(n-1))+yin(n-1);
	}
#ifdef DEBUG
	cout<<"Yout"<<yout<<endl;
#endif
}


void
 Interpolator::pchip_int(blitz::Array<double,1> xin, blitz::Array<dcomplex,1> yin, int n, blitz::Array<double,1> xout,  blitz::Array<dcomplex,1> yout, int m, blitz::Array<int,1> xindex) {

	//special case: n==1 and m> 1, oversample from a scalar, just copy the value
	if (n==1 && m >=1) { yout=yin(0); return;}

	//another special case, input and output is exact
	int is_identical=1;
	if (m==n) {
		int i=0;
		while(is_identical && i<n) {	
			if (xin(i)!=xout(i)) {is_identical=0; break;}
			i++;
		}
		if (i==n && is_identical) {
#ifdef DEBUG
			cout<<"Identical, ignoring"<<endl;
#endif
      yout=yin; return;
		}
	}
	//array to store first derivatives used in interpolation
	blitz::Array<dcomplex,1> d(n);
	//array to store first divided differences
	blitz::Array<dcomplex,1> del(n);
	//Note: the values of above arrays at the end points are determined 
	//in a special 3 point way
	//array to store x differences
	blitz::Array<double,1> h(n);

	if (n==2) {
		//linear interpolation
		h(0)=h(1)=(xin(1)-xin(0));
		del(0)=del(1)=d(0)=d(1)=(yin(1)-yin(0))/h(0);
	  for (int i=0; i<m; i++) {
	   yout(i)=d(0)*(xout(i)-xin(0))+yin(0);
		}
		return;

	} else {
	for (int i=0; i<n-1; i++) {
			h(i)=xin(i+1)-xin(i);
			del(i)=(yin(i+1)-yin(i))/h(i);
	}
	del(n-1)=del(n-2);
	h(n-1)=h(n-2);
	for (int k=1; k<n-1; k++) {
    //calculate real and imag parts separately
    double delr1=creal(del(k-1));
    double deli1=cimag(del(k-1));
    double delr=creal(del(k));
    double deli=cimag(del(k));

    double dr=0;
    double di=0;
		if (!(delr1==0 || delr==0 || ((delr) >0 && delr1<0) 
									 || (delr <0 && delr1>0) ))	 {
		 double w1=2*h(k)+h(k-1);
		 double w2=h(k)+2*h(k-1);
		 dr=(w1+w1)/(w1/delr1+w2/delr);
    }
		if (!(deli1==0 || deli==0 || ((deli) >0 && deli1<0) 
									 || (deli <0 && deli1>0) ))	 {
		 double w1=2*h(k)+h(k-1);
		 double w2=h(k)+2*h(k-1);
		 di=(w1+w1)/(w1/deli1+w2/deli);
    }
	  d(k)=make_dcomplex(dr,di);
	}

#ifdef DEBUG
	cout<<"xin()"<<xin<<endl;
	cout<<"h()"<<h<<endl;
#endif
	//slopes at endpoints
	d(0)=((2*h(0)+h(1))*del(0)-h(0)*del(1))/(h(0)+h(1));
	if ((abs(d(0))> 3*abs(del(0)))) {
			d(0)=3*del(0);
	} 

	d(n-1)=((2*h(n-1)+h(n-2))*del(n-1)-h(n-1)*del(n-2))/(h(n-1)+h(n-2));
	if ((abs(d(n-1))> 3*abs(del(n-1)))) {
			d(n-1)=3*del(n-1);
	} 


	}

	//find the range where we can interpolate: xindex(k) >= 1 and
	// xindex(k) <= n-1
	int x_l_limit=0;
	int x_u_limit=m-1;

	while( (x_l_limit<m)&& (xindex(x_l_limit)<1) ) x_l_limit++;
	while( (x_u_limit>=0) && (xindex(x_u_limit)>n-1) ) x_u_limit--;
	//sanuty check
	if ( xindex(0)==0 && xindex(m-1)==0) { //everything to the left
  	for (int i=0; i<m; i++) {
	    yout(i)=d(0)*(xout(i)-xin(0))+yin(0);
   	}
		return;
	}  else if (xindex(0)==n && xindex(m-1)==n) { //everything to the right
  	for (int i=0; i<m; i++) {
	    yout(i)=d(n-1)*(xout(i)-xin(n-1))+yin(n-1);
	  }
    return;
	}
#ifdef DEBUG
	 cout<<"Limits : cubic interp["<<x_l_limit<<","<<x_u_limit<<"]"<<endl;
#endif

	//interpolation
	for (int i=x_l_limit; i<=x_u_limit; i++) {
		double s=xout(i)-xin(xindex(i)-1);
		double &hh=h(xindex(i)-1);
		double aa=(3*hh-2*s)*s*s/(hh*hh*hh);
		yout(i)=aa*yin(xindex(i))+(1-aa)*yin(xindex(i)-1);
		if (d(xindex(i)) !=0) {
		  yout(i)+=s*s*(s-hh)/(hh*hh)*d(xindex(i));
		}
		if (d(xindex(i)-1) !=0) {
		  yout(i)+=s*(s-hh)*(s-hh)/(hh*hh)*d(xindex(i)-1);
		}

	}
	//extrapolation
 	for (int i=0; i<x_l_limit; i++) {
	    yout(i)=d(0)*(xout(i)-xin(0))+yin(0);
 	}
	for (int i=x_u_limit+1; i<m; i++) {
	  yout(i)=d(n-1)*(xout(i)-xin(n-1))+yin(n-1);
	}
#ifdef DEBUG
 if (abs(yout(0)) > 1e6) {
  cout<<abs(yout(0))<<endl;
	cout<<"xin()"<<xin<<endl;
	cout<<"h()"<<h<<endl;
	cout<<"d()="<<endl;
  for (int ci=0; ci<d.size(); ci++) {
	 cout<<" "<<ci<<": "<<abs(d(ci))<<endl;
  }
	cout<<endl<<"del()="<<endl;
  for (int ci=0; ci<del.size(); ci++) {
	 cout<<" "<<ci<<": "<<abs(del(ci))<<endl;
  }
	cout<<endl<<"yin()="<<endl;
  for (int ci=0; ci<yin.size(); ci++) {
	  cout<<" "<<ci<<": "<<abs(yin(ci))<<endl;
  }
	cout<<endl<<"yout()="<<endl;
  for (int ci=0; ci<yout.size(); ci++) {
	  cout<<" "<<ci<<": "<<abs(yout(ci))<<endl;
  }
  cout<<"m="<<m<<",N="<<n<<endl;
 }
#endif
}

//setup routine:
//1) see if any missing axes in input or output cells, and add a dummy scalar to it
//2) prepare the indices for later interpolation
void
Interpolator::setup( const Cells &in, const Cells &out) {
    
			
		unsigned int dimension=std::max(in.rank(),out.rank());
	  incells_.resize(dimension);	
	  outcells_.resize(dimension);

	  for (int i=0; i<std::min(in.rank(),out.rank()); i++) {
					//special case: is len(in[i])==1, regardless of len(out[i]) size, we
					//fix it to be 1
					incells_[i].resize(in.center(i).size());
					incells_[i]=in.center(i);
					if ((in.center(i).size()<=1) && (out.center(i).size()> 1)) {
	//								cout<<"Override Axis"<<endl;
					 outcells_[i].resize(1);
					 outcells_[i]=out.center(i)(0);
					} else {
					 outcells_[i].resize(out.center(i).size());
					 outcells_[i]=out.center(i);
					}
	  }
	  for (unsigned int i=in.rank(); i<dimension; i++) {
					outcells_[i].resize(out.center(i).size());
					outcells_[i]=out.center(i);
		}
	  for (unsigned int i=out.rank(); i<dimension; i++) {
					incells_[i].resize(in.center(i).size());
					incells_[i]=in.center(i);
		}

	  for (unsigned int i=0; i<dimension; i++) {
				 if(incells_[i].size()==0) {
					if (outcells_[i].size()==0){
					 incells_[i].resize(1);
					 outcells_[i].resize(1);
					 incells_[i](0)=outcells_[i](0)=0;
					} else {
					 incells_[i].resize(1);
					 incells_[i](0)=(outcells_[i](0)+outcells_[i](outcells_[i].extent(0)-1))/2;
					}
				 } else {
					if (outcells_[i].size()==0){
					 outcells_[i].resize(1);
					 outcells_[i](0)=(incells_[i](0)+incells_[i](incells_[i].extent(0)-1))/2;
					}
				 }
	  }

	 //do binary search
  xindex_.resize(dimension); 
	std::vector<double> tempx;
	for (unsigned int i=0; i<dimension; i++) {
	 unsigned int n=incells_[i].size();
	 tempx.resize(n+2);
	 for (unsigned int j=1; j<n+1; j++) 
	  tempx[j]=incells_[i](j-1);
	 tempx[0]=-INFINITY;
	 tempx[n+1]=INFINITY;
	 xindex_[i].resize(outcells_[i].size());
	 for (int j=0; j<outcells_[i].size(); j++) 
		xindex_[i](j)=bin_search(tempx,outcells_[i](j),0,n+1);
	}

#ifdef DEBUG
	      cout<<"Incells"<<endl;
				for (unsigned int i=0; i<dimension; i++) {
				 cout<<incells_[i]<<endl;
				}
	      cout<<"Outcells"<<endl;
				for (unsigned int i=0; i<dimension; i++) {
				 cout<<outcells_[i]<<endl;
				}
	      cout<<"Index"<<endl;
				for (unsigned int i=0; i<dimension; i++) {
				 cout<<xindex_[i]<<endl;
				}
#endif

}




int 
Interpolator::apply( const VellSet &in, VellSet &out ) {
  int dim=incells_.size();


	std::vector<int> indim;
	std::vector<int> outdim;
	std::vector<int> totdim;
  indim.resize(dim);
  outdim.resize(dim);
	totdim.resize(dim);

	for (int i=0; i<dim; i++) {
		indim[i]=incells_[i].size();
		outdim[i]=outcells_[i].size();
		totdim[i]=std::max(indim[i],outdim[i]);
	}
  if (in.hasValue()) {
	 const Vells &invl=in.getValue();
	 //check for scalar values
	 if (invl.isScalar()) {
	  out.setValue(invl);
	 } else {
		//check for compatibility of this vells with the cells
		for (int i=0; i<dim; i++) {
		 if (indim[i]>invl.extent(i)) {indim[i]=invl.extent(i);}
		 totdim[i]=std::max(indim[i],outdim[i]);
		}

	  out.setValue(really_apply(invl, indim, outdim, totdim));
	 }
	}

	//see if we have any perturbed values
	int npert=in.numPertSets();
	int nspid=in.numSpids();
	if (npert*nspid>0) {
		out.copySpids(in);
		out.copyPerturbations(in);
    for(int ipert=0; ipert<npert; ipert++) {
			for (int ispid=0; ispid<nspid; ispid++) {
			 const Vells &pvl=in.getPerturbedValue(ispid,ipert);
	     out.setPerturbedValue(ispid,really_apply(pvl, indim, outdim, totdim),ipert);
			}
		}
	}

	return dim;
}


Vells *
Interpolator::really_apply(const Vells &in,  std::vector<int> indim, std::vector<int> outdim, std::vector<int> totdim) {
  int dim=incells_.size();

	const Vells &invl=in;
	
	Vells *out=0;

	if (invl.isReal()) {
	double *indata=const_cast<double*>(invl.realStorage());
	if (dim==1) {
   blitz::Array<double,1> A(indata,blitz::shape(indim[0]),blitz::neverDeleteData);
   blitz::Array<double,1> B(outdim[0]);
           pchip_int(incells_[0], A(blitz::Range(0,indim[0]-1)),  indim[0], outcells_[0], B(blitz::Range(0,outdim[0]-1)), outdim[0], xindex_[0]);
#ifdef DEBUG
	 cout<<"A="<<A<<endl;
	 cout<<"B="<<B<<endl;
#endif
   blitz::Array<double,1> C=B(blitz::Range(0,outdim[0]-1));
#ifdef DEBUG
	 cout<<"C="<<C<<endl;
#endif

	 out=new Vells(C);
	}
	else if (dim==2) {
   blitz::Array<double,2> A(indata,blitz::shape(indim[0],indim[1]),blitz::neverDeleteData);
   blitz::Array<double,2> B(outdim[0],totdim[1]);
	 for (int i=0; i<indim[1]; i++) {
           pchip_int(incells_[0], A(blitz::Range(0,indim[0]-1),i),  indim[0], outcells_[0], B(blitz::Range(0,outdim[0]-1),i), outdim[0], xindex_[0]);
	 }
#ifdef DEBUG
	 cout<<"A="<<A<<endl;
	 cout<<"B="<<B<<endl;
#endif
	 //copy the remaining dimensions
	 blitz::Array<double,1> yin;
	 blitz::Array<double,1> yout;
	 yin.resize(indim[1]);
	 yout.resize(outdim[1]);
	 for (int i=0; i<outdim[0]; i++) {
					 yin=B(i,blitz::Range(0,indim[1]-1));
           pchip_int(incells_[1], yin,  indim[1], outcells_[1], yout, outdim[1], xindex_[1]);
           B(i,blitz::Range(0,outdim[1]-1))=yout;
	 }
#ifdef DEBUG
	 cout<<"B="<<B<<endl;
#endif
   blitz::Array<double,2> C=B(blitz::Range(0,outdim[0]-1),blitz::Range(0,outdim[1]-1));
#ifdef DEBUG
	 cout<<"C="<<C<<endl;
#endif
	 out=new Vells(C);
	}

	else if (dim==3) {
   blitz::Array<double,3> A(indata,blitz::shape(indim[0],indim[1],indim[2]),blitz::neverDeleteData);
   blitz::Array<double,3> B(outdim[0],totdim[1],totdim[2]);
	 for (int i=0; i<indim[1]; i++) {
	   for (int j=0; j<indim[2]; j++) {
           pchip_int(incells_[0], A(blitz::Range(0,indim[0]-1),i,j),  indim[0], outcells_[0], B(blitz::Range(0,outdim[0]-1),i,j), outdim[0], xindex_[0]);
		 }
	 }
#ifdef DEBUG
	 cout<<"A="<<A<<endl;
	 cout<<"B="<<B<<endl;
#endif
	 //copy the remaining dimensions
	 blitz::Array<double,1> yin;
	 blitz::Array<double,1> yout;
	 yin.resize(indim[1]);
	 yout.resize(outdim[1]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<indim[2]; j++) {
					 yin=B(i,blitz::Range(0,indim[1]-1),j);
           pchip_int(incells_[1], yin,  indim[1], outcells_[1], yout, outdim[1], xindex_[1]);
           B(i,blitz::Range(0,outdim[1]-1),j)=yout;
		 }
	 }
#ifdef DEBUG
	 cout<<"B="<<B<<endl;
#endif
	 yin.resize(indim[2]);
	 yout.resize(outdim[2]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<outdim[1]; j++) {
					 yin=B(i,j,blitz::Range(0,indim[2]-1));
           pchip_int(incells_[2], yin,  indim[2], outcells_[2], yout, outdim[2], xindex_[2]);
           B(i,j,blitz::Range(0,outdim[2]-1))=yout;
		 }
	 }
#ifdef DEBUG
	 cout<<"B="<<B<<endl;
#endif
   blitz::Array<double,3> C=B(blitz::Range(0,outdim[0]-1),blitz::Range(0,outdim[1]-1),blitz::Range(0,outdim[2]-1));
#ifdef DEBUG
	 cout<<"C="<<C<<endl;
#endif
	 out=new Vells(C);
	}

	else if (dim==4) {
   blitz::Array<double,4> A(indata,blitz::shape(indim[0],indim[1],indim[2],indim[3]),blitz::neverDeleteData);
   blitz::Array<double,4> B(outdim[0],totdim[1],totdim[2],totdim[3]);
	 for (int i=0; i<indim[1]; i++) {
	   for (int j=0; j<indim[2]; j++) {
	     for (int k=0; k<indim[3]; k++) {
           pchip_int(incells_[0], A(blitz::Range(0,indim[0]-1),i,j,k),  indim[0], outcells_[0], B(blitz::Range(0,outdim[0]-1),i,j,k), outdim[0], xindex_[0]);
			 }
		 }
	 }
#ifdef DEBUG
	 cout<<"A="<<A<<endl;
	 cout<<"B="<<B<<endl;
#endif
	 //copy the remaining dimensions
	 blitz::Array<double,1> yin;
	 blitz::Array<double,1> yout;
	 yin.resize(indim[1]);
	 yout.resize(outdim[1]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<indim[2]; j++) {
	     for (int k=0; k<indim[3]; k++) {
					 yin=B(i,blitz::Range(0,indim[1]-1),j,k);
           pchip_int(incells_[1], yin,  indim[1], outcells_[1], yout, outdim[1], xindex_[1]);
           B(i,blitz::Range(0,outdim[1]-1),j,k)=yout;
			 }
		 }
	 }
#ifdef DEBUG
	 cout<<"B="<<B<<endl;
#endif
	 yin.resize(indim[2]);
	 yout.resize(outdim[2]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<outdim[1]; j++) {
	     for (int k=0; k<indim[3]; k++) {
					 yin=B(i,j,blitz::Range(0,indim[2]-1),k);
           pchip_int(incells_[2], yin,  indim[2], outcells_[2], yout, outdim[2], xindex_[2]);
           B(i,j,blitz::Range(0,outdim[2]-1),k)=yout;
			 }
		 }
	 }
#ifdef DEBUG
	 cout<<"B="<<B<<endl;
#endif
	 yin.resize(indim[3]);
	 yout.resize(outdim[3]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<outdim[1]; j++) {
	     for (int k=0; k<outdim[2]; k++) {
					 yin=B(i,j,k,blitz::Range(0,indim[3]-1));
           pchip_int(incells_[3], yin,  indim[3], outcells_[3], yout, outdim[3], xindex_[3]);
           B(i,j,k,blitz::Range(0,outdim[3]-1))=yout;
			 }
		 }
	 }
#ifdef DEBUG
	 cout<<"B="<<B<<endl;
#endif


   blitz::Array<double,4> C=B(blitz::Range(0,outdim[0]-1),blitz::Range(0,outdim[1]-1),blitz::Range(0,outdim[2]-1),blitz::Range(0,outdim[3]-1));
#ifdef DEBUG
	 cout<<"C="<<C<<endl;
#endif
	 out=new Vells(C);
	}

	else if (dim==5) {
   blitz::Array<double,5> A(indata,blitz::shape(indim[0],indim[1],indim[2],indim[3],indim[4]),blitz::neverDeleteData);
   blitz::Array<double,5> B(outdim[0],totdim[1],totdim[2],totdim[3],totdim[4]);
	 for (int i=0; i<indim[1]; i++) {
	   for (int j=0; j<indim[2]; j++) {
	     for (int k=0; k<indim[3]; k++) {
	       for (int l=0; l<indim[4]; l++) {
           pchip_int(incells_[0], A(blitz::Range(0,indim[0]-1),i,j,k,l),  indim[0], outcells_[0], B(blitz::Range(0,outdim[0]-1),i,j,k,l), outdim[0], xindex_[0]);
				 }
			 }
		 }
	 }
#ifdef DEBUG
	 cout<<"A="<<A<<endl;
	 cout<<"B="<<B<<endl;
#endif
	 //copy the remaining dimensions
	 blitz::Array<double,1> yin;
	 blitz::Array<double,1> yout;
	 yin.resize(indim[1]);
	 yout.resize(outdim[1]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<indim[2]; j++) {
	     for (int k=0; k<indim[3]; k++) {
	       for (int l=0; l<indim[4]; l++) {
					 yin=B(i,blitz::Range(0,indim[1]-1),j,k,l);
           pchip_int(incells_[1], yin,  indim[1], outcells_[1], yout, outdim[1], xindex_[1]);
           B(i,blitz::Range(0,outdim[1]-1),j,k,l)=yout;
				 }
			 }
		 }
	 }
#ifdef DEBUG
	 cout<<"B="<<B<<endl;
#endif
	 yin.resize(indim[2]);
	 yout.resize(outdim[2]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<outdim[1]; j++) {
	     for (int k=0; k<indim[3]; k++) {
	       for (int l=0; l<indim[4]; l++) {
					 yin=B(i,j,blitz::Range(0,indim[2]-1),k,l);
           pchip_int(incells_[2], yin,  indim[2], outcells_[2], yout, outdim[2], xindex_[2]);
           B(i,j,blitz::Range(0,outdim[2]-1),k,l)=yout;
				 }
			 }
		 }
	 }
#ifdef DEBUG
	 cout<<"B="<<B<<endl;
#endif
	 yin.resize(indim[3]);
	 yout.resize(outdim[3]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<outdim[1]; j++) {
	     for (int k=0; k<outdim[2]; k++) {
	       for (int l=0; l<indim[4]; l++) {
					 yin=B(i,j,k,blitz::Range(0,indim[3]-1),l);
           pchip_int(incells_[3], yin,  indim[3], outcells_[3], yout, outdim[3], xindex_[3]);
           B(i,j,k,blitz::Range(0,outdim[3]-1),l)=yout;
				 }
			 }
		 }
	 }
	 yin.resize(indim[4]);
	 yout.resize(outdim[4]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<outdim[1]; j++) {
	     for (int k=0; k<outdim[2]; k++) {
	       for (int l=0; l<outdim[3]; l++) {
					 yin=B(i,j,k,l,blitz::Range(0,indim[4]-1));
           pchip_int(incells_[4], yin,  indim[4], outcells_[4], yout, outdim[4], xindex_[4]);
           B(i,j,k,l,blitz::Range(0,outdim[4]-1))=yout;
				 }
			 }
		 }
	 }
#ifdef DEBUG
	 cout<<"B="<<B<<endl;
#endif


   blitz::Array<double,5> C=B(blitz::Range(0,outdim[0]-1),blitz::Range(0,outdim[1]-1),blitz::Range(0,outdim[2]-1),blitz::Range(0,outdim[3]-1),blitz::Range(0,outdim[4]-1));
#ifdef DEBUG
	 cout<<"C="<<C<<endl;
#endif
	 out=new Vells(C);
	}

	else if (dim==6) {
   blitz::Array<double,6> A(indata,blitz::shape(indim[0],indim[1],indim[2],indim[3],indim[4],indim[5]),blitz::neverDeleteData);
   blitz::Array<double,6> B(outdim[0],totdim[1],totdim[2],totdim[3],totdim[4],totdim[5]);
	 for (int i=0; i<indim[1]; i++) {
	   for (int j=0; j<indim[2]; j++) {
	     for (int k=0; k<indim[3]; k++) {
	       for (int l=0; l<indim[4]; l++) {
	         for (int p=0; p<indim[5]; p++) {
           pchip_int(incells_[0], A(blitz::Range(0,indim[0]-1),i,j,k,l,p),  indim[0], outcells_[0], B(blitz::Range(0,outdim[0]-1),i,j,k,l,p), outdim[0], xindex_[0]);
					 }
				 }
			 }
		 }
	 }
#ifdef DEBUG
	 cout<<"loop 1"<<endl;
	 cout<<"A="<<A<<endl;
	 cout<<"B="<<B<<endl;
#endif
	 //copy the remaining dimensions
	 blitz::Array<double,1> yin;
	 blitz::Array<double,1> yout;
	 yin.resize(indim[1]);
	 yout.resize(outdim[1]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<indim[2]; j++) {
	     for (int k=0; k<indim[3]; k++) {
	       for (int l=0; l<indim[4]; l++) {
	         for (int p=0; p<indim[5]; p++) {
					  yin=B(i,blitz::Range(0,indim[1]-1),j,k,l,p);
            pchip_int(incells_[1], yin,  indim[1], outcells_[1], yout, outdim[1], xindex_[1]);
            B(i,blitz::Range(0,outdim[1]-1),j,k,l,p)=yout;
					 }
				 }
			 }
		 }
	 }
#ifdef DEBUG
	 cout<<"loop 2"<<endl;
	 cout<<"B="<<B<<endl;
#endif
	 yin.resize(indim[2]);
	 yout.resize(outdim[2]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<outdim[1]; j++) {
	     for (int k=0; k<indim[3]; k++) {
	       for (int l=0; l<indim[4]; l++) {
	         for (int p=0; p<indim[5]; p++) {
					  yin=B(i,j,blitz::Range(0,indim[2]-1),k,l,p);
            pchip_int(incells_[2], yin,  indim[2], outcells_[2], yout, outdim[2], xindex_[2]);
            B(i,j,blitz::Range(0,outdim[2]-1),k,l,p)=yout;
					 }
				 }
			 }
		 }
	 }
#ifdef DEBUG
	 cout<<"loop 3"<<endl;
	 cout<<"B="<<B<<endl;
#endif
	 yin.resize(indim[3]);
	 yout.resize(outdim[3]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<outdim[1]; j++) {
	     for (int k=0; k<outdim[2]; k++) {
	       for (int l=0; l<indim[4]; l++) {
	         for (int p=0; p<indim[5]; p++) {
					  yin=B(i,j,k,blitz::Range(0,indim[3]-1),l,p);
            pchip_int(incells_[3], yin,  indim[3], outcells_[3], yout, outdim[3], xindex_[3]);
            B(i,j,k,blitz::Range(0,outdim[3]-1),l,p)=yout;
					 }
				 }
			 }
		 }
	 }
	 yin.resize(indim[4]);
	 yout.resize(outdim[4]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<outdim[1]; j++) {
	     for (int k=0; k<outdim[2]; k++) {
	       for (int l=0; l<outdim[3]; l++) {
	         for (int p=0; p<indim[5]; p++) {
					  yin=B(i,j,k,l,blitz::Range(0,indim[4]-1),p);
            pchip_int(incells_[4], yin,  indim[4], outcells_[4], yout, outdim[4], xindex_[4]);
            B(i,j,k,l,blitz::Range(0,outdim[4]-1),p)=yout;
					 }
				 }
			 }
		 }
	 }
#ifdef DEBUG
	 cout<<"loop 4"<<endl;
	 cout<<"B="<<B<<endl;
#endif

	 yin.resize(indim[5]);
	 yout.resize(outdim[5]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<outdim[1]; j++) {
	     for (int k=0; k<outdim[2]; k++) {
	       for (int l=0; l<outdim[3]; l++) {
	         for (int p=0; p<outdim[4]; p++) {
					  yin=B(i,j,k,l,p,blitz::Range(0,indim[5]-1));
            pchip_int(incells_[5], yin,  indim[5], outcells_[5], yout, outdim[5], xindex_[5]);
            B(i,j,k,l,p,blitz::Range(0,outdim[5]-1))=yout;
					 }
				 }
			 }
		 }
	 }
#ifdef DEBUG
	 cout<<"loop 5"<<endl;
	 cout<<"B="<<B<<endl;
#endif

   blitz::Array<double,6> C=B(blitz::Range(0,outdim[0]-1),blitz::Range(0,outdim[1]-1),blitz::Range(0,outdim[2]-1),blitz::Range(0,outdim[3]-1),blitz::Range(0,outdim[4]-1), blitz::Range(0,outdim[5]-1));
#ifdef DEBUG
	 cout<<"C="<<C<<endl;
#endif
	 out=new Vells(C);
	} else {
		cout<<"Dimension "<<dim<<" is WIP"<<endl;
	}
	} else if (invl.isComplex()) {
	dcomplex *indata=const_cast<dcomplex*>(invl.complexStorage());
	if (dim==1) {
   blitz::Array<dcomplex,1> A(indata,blitz::shape(indim[0]),blitz::neverDeleteData);
   blitz::Array<dcomplex,1> B(outdim[0]);
           pchip_int(incells_[0], A(blitz::Range(0,indim[0]-1)),  indim[0], outcells_[0], B(blitz::Range(0,outdim[0]-1)), outdim[0], xindex_[0]);
   blitz::Array<dcomplex,1> C=B(blitz::Range(0,outdim[0]-1));

	 out=new Vells(C);
	}
	else if (dim==2) {
   blitz::Array<dcomplex,2> A(indata,blitz::shape(indim[0],indim[1]),blitz::neverDeleteData);
   blitz::Array<dcomplex,2> B(outdim[0],totdim[1]);
	 for (int i=0; i<indim[1]; i++) {
           pchip_int(incells_[0], A(blitz::Range(0,indim[0]-1),i),  indim[0], outcells_[0], B(blitz::Range(0,outdim[0]-1),i), outdim[0], xindex_[0]);
	 }
	 //copy the remaining dimensions
	 blitz::Array<dcomplex,1> yin;
	 blitz::Array<dcomplex,1> yout;
	 yin.resize(indim[1]);
	 yout.resize(outdim[1]);
	 for (int i=0; i<outdim[0]; i++) {
					 yin=B(i,blitz::Range(0,indim[1]-1));
           pchip_int(incells_[1], yin,  indim[1], outcells_[1], yout, outdim[1], xindex_[1]);
           B(i,blitz::Range(0,outdim[1]-1))=yout;
	 }
   blitz::Array<dcomplex,2> C=B(blitz::Range(0,outdim[0]-1),blitz::Range(0,outdim[1]-1));
	 out=new Vells(C);
	}

	else if (dim==3) {
   blitz::Array<dcomplex,3> A(indata,blitz::shape(indim[0],indim[1],indim[2]),blitz::neverDeleteData);
   blitz::Array<dcomplex,3> B(outdim[0],totdim[1],totdim[2]);
	 for (int i=0; i<indim[1]; i++) {
	   for (int j=0; j<indim[2]; j++) {
           pchip_int(incells_[0], A(blitz::Range(0,indim[0]-1),i,j),  indim[0], outcells_[0], B(blitz::Range(0,outdim[0]-1),i,j), outdim[0], xindex_[0]);
		 }
	 }
	 //copy the remaining dimensions
	 blitz::Array<dcomplex,1> yin;
	 blitz::Array<dcomplex,1> yout;
	 yin.resize(indim[1]);
	 yout.resize(outdim[1]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<indim[2]; j++) {
					 yin=B(i,blitz::Range(0,indim[1]-1),j);
           pchip_int(incells_[1], yin,  indim[1], outcells_[1], yout, outdim[1], xindex_[1]);
           B(i,blitz::Range(0,outdim[1]-1),j)=yout;
		 }
	 }
	 yin.resize(indim[2]);
	 yout.resize(outdim[2]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<outdim[1]; j++) {
					 yin=B(i,j,blitz::Range(0,indim[2]-1));
           pchip_int(incells_[2], yin,  indim[2], outcells_[2], yout, outdim[2], xindex_[2]);
           B(i,j,blitz::Range(0,outdim[2]-1))=yout;
		 }
	 }
   blitz::Array<dcomplex,3> C=B(blitz::Range(0,outdim[0]-1),blitz::Range(0,outdim[1]-1),blitz::Range(0,outdim[2]-1));
	 out=new Vells(C);
	}

	else if (dim==4) {
   blitz::Array<dcomplex,4> A(indata,blitz::shape(indim[0],indim[1],indim[2],indim[3]),blitz::neverDeleteData);
   blitz::Array<dcomplex,4> B(outdim[0],totdim[1],totdim[2],totdim[3]);
	 for (int i=0; i<indim[1]; i++) {
	   for (int j=0; j<indim[2]; j++) {
	     for (int k=0; k<indim[3]; k++) {
           pchip_int(incells_[0], A(blitz::Range(0,indim[0]-1),i,j,k),  indim[0], outcells_[0], B(blitz::Range(0,outdim[0]-1),i,j,k), outdim[0], xindex_[0]);
			 }
		 }
	 }
	 //copy the remaining dimensions
	 blitz::Array<dcomplex,1> yin;
	 blitz::Array<dcomplex,1> yout;
	 yin.resize(indim[1]);
	 yout.resize(outdim[1]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<indim[2]; j++) {
	     for (int k=0; k<indim[3]; k++) {
					 yin=B(i,blitz::Range(0,indim[1]-1),j,k);
           pchip_int(incells_[1], yin,  indim[1], outcells_[1], yout, outdim[1], xindex_[1]);
           B(i,blitz::Range(0,outdim[1]-1),j,k)=yout;
			 }
		 }
	 }
	 yin.resize(indim[2]);
	 yout.resize(outdim[2]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<outdim[1]; j++) {
	     for (int k=0; k<indim[3]; k++) {
					 yin=B(i,j,blitz::Range(0,indim[2]-1),k);
           pchip_int(incells_[2], yin,  indim[2], outcells_[2], yout, outdim[2], xindex_[2]);
           B(i,j,blitz::Range(0,outdim[2]-1),k)=yout;
			 }
		 }
	 }
	 yin.resize(indim[3]);
	 yout.resize(outdim[3]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<outdim[1]; j++) {
	     for (int k=0; k<outdim[2]; k++) {
					 yin=B(i,j,k,blitz::Range(0,indim[3]-1));
           pchip_int(incells_[3], yin,  indim[3], outcells_[3], yout, outdim[3], xindex_[3]);
           B(i,j,k,blitz::Range(0,outdim[3]-1))=yout;
			 }
		 }
	 }


   blitz::Array<dcomplex,4> C=B(blitz::Range(0,outdim[0]-1),blitz::Range(0,outdim[1]-1),blitz::Range(0,outdim[2]-1),blitz::Range(0,outdim[3]-1));
	 out=new Vells(C);
	}

	else if (dim==5) {
   blitz::Array<dcomplex,5> A(indata,blitz::shape(indim[0],indim[1],indim[2],indim[3],indim[4]),blitz::neverDeleteData);
   blitz::Array<dcomplex,5> B(outdim[0],totdim[1],totdim[2],totdim[3],totdim[4]);
	 for (int i=0; i<indim[1]; i++) {
	   for (int j=0; j<indim[2]; j++) {
	     for (int k=0; k<indim[3]; k++) {
	       for (int l=0; l<indim[4]; l++) {
           pchip_int(incells_[0], A(blitz::Range(0,indim[0]-1),i,j,k,l),  indim[0], outcells_[0], B(blitz::Range(0,outdim[0]-1),i,j,k,l), outdim[0], xindex_[0]);
				 }
			 }
		 }
	 }
	 //copy the remaining dimensions
	 blitz::Array<dcomplex,1> yin;
	 blitz::Array<dcomplex,1> yout;
	 yin.resize(indim[1]);
	 yout.resize(outdim[1]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<indim[2]; j++) {
	     for (int k=0; k<indim[3]; k++) {
	       for (int l=0; l<indim[4]; l++) {
					 yin=B(i,blitz::Range(0,indim[1]-1),j,k,l);
           pchip_int(incells_[1], yin,  indim[1], outcells_[1], yout, outdim[1], xindex_[1]);
           B(i,blitz::Range(0,outdim[1]-1),j,k,l)=yout;
				 }
			 }
		 }
	 }
	 yin.resize(indim[2]);
	 yout.resize(outdim[2]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<outdim[1]; j++) {
	     for (int k=0; k<indim[3]; k++) {
	       for (int l=0; l<indim[4]; l++) {
					 yin=B(i,j,blitz::Range(0,indim[2]-1),k,l);
           pchip_int(incells_[2], yin,  indim[2], outcells_[2], yout, outdim[2], xindex_[2]);
           B(i,j,blitz::Range(0,outdim[2]-1),k,l)=yout;
				 }
			 }
		 }
	 }
	 yin.resize(indim[3]);
	 yout.resize(outdim[3]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<outdim[1]; j++) {
	     for (int k=0; k<outdim[2]; k++) {
	       for (int l=0; l<indim[4]; l++) {
					 yin=B(i,j,k,blitz::Range(0,indim[3]-1),l);
           pchip_int(incells_[3], yin,  indim[3], outcells_[3], yout, outdim[3], xindex_[3]);
           B(i,j,k,blitz::Range(0,outdim[3]-1),l)=yout;
				 }
			 }
		 }
	 }
	 yin.resize(indim[4]);
	 yout.resize(outdim[4]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<outdim[1]; j++) {
	     for (int k=0; k<outdim[2]; k++) {
	       for (int l=0; l<outdim[3]; l++) {
					 yin=B(i,j,k,l,blitz::Range(0,indim[4]-1));
           pchip_int(incells_[4], yin,  indim[4], outcells_[4], yout, outdim[4], xindex_[4]);
           B(i,j,k,l,blitz::Range(0,outdim[4]-1))=yout;
				 }
			 }
		 }
	 }

   blitz::Array<dcomplex,5> C=B(blitz::Range(0,outdim[0]-1),blitz::Range(0,outdim[1]-1),blitz::Range(0,outdim[2]-1),blitz::Range(0,outdim[3]-1),blitz::Range(0,outdim[4]-1));
	 out=new Vells(C);
	}
	else if (dim==6) {
	 blitz::Array<dcomplex,1> yin;
	 blitz::Array<dcomplex,1> yout;
	 yin.resize(indim[0]);
	 yout.resize(outdim[0]);
   blitz::Array<dcomplex,6> A(indata,blitz::shape(indim[0],indim[1],indim[2],indim[3],indim[4],indim[5]),blitz::duplicateData);
   blitz::Array<dcomplex,6> B(outdim[0],totdim[1],totdim[2],totdim[3],totdim[4],totdim[5]);
	 for (int i=0; i<indim[1]; i++) {
	   for (int j=0; j<indim[2]; j++) {
	     for (int k=0; k<indim[3]; k++) {
	       for (int l=0; l<indim[4]; l++) {
	         for (int p=0; p<indim[5]; p++) {
					 yin=A(blitz::Range(0,indim[0]-1),i,j,k,l,p);
           //pchip_int(incells_[0], A(blitz::Range(0,indim[0]-1),i,j,k,l,p),  indim[0], outcells_[0], B(blitz::Range(0,outdim[0]-1),i,j,k,l,p), outdim[0], xindex_[0]);
           pchip_int(incells_[0], yin,  indim[0], outcells_[0], yout, outdim[0], xindex_[0]);
            B(blitz::Range(0,outdim[0]-1),i,j,k,l,p)=yout;
					 }
				 }
			 }
		 }
	 }
#ifdef DEBUG
	 cout<<"loop 1"<<endl;
#endif


	 //copy the remaining dimensions
	 yin.resize(indim[1]);
	 yout.resize(outdim[1]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<indim[2]; j++) {
	     for (int k=0; k<indim[3]; k++) {
	       for (int l=0; l<indim[4]; l++) {
	         for (int p=0; p<indim[5]; p++) {
					  yin=B(i,blitz::Range(0,indim[1]-1),j,k,l,p);
            pchip_int(incells_[1], yin,  indim[1], outcells_[1], yout, outdim[1], xindex_[1]);
            B(i,blitz::Range(0,outdim[1]-1),j,k,l,p)=yout;
					 }
				 }
			 }
		 }
	 }
#ifdef DEBUG
	 cout<<"loop 2"<<endl;
#endif


	 yin.resize(indim[2]);
	 yout.resize(outdim[2]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<outdim[1]; j++) {
	     for (int k=0; k<indim[3]; k++) {
	       for (int l=0; l<indim[4]; l++) {
	         for (int p=0; p<indim[5]; p++) {
					  yin=B(i,j,blitz::Range(0,indim[2]-1),k,l,p);
            pchip_int(incells_[2], yin,  indim[2], outcells_[2], yout, outdim[2], xindex_[2]);
            B(i,j,blitz::Range(0,outdim[2]-1),k,l,p)=yout;
					 }
				 }
			 }
		 }
	 }
#ifdef DEBUG
	 cout<<"loop 3"<<endl;
#endif


	 yin.resize(indim[3]);
	 yout.resize(outdim[3]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<outdim[1]; j++) {
	     for (int k=0; k<outdim[2]; k++) {
	       for (int l=0; l<indim[4]; l++) {
	         for (int p=0; p<indim[5]; p++) {
					  yin=B(i,j,k,blitz::Range(0,indim[3]-1),l,p);
            pchip_int(incells_[3], yin,  indim[3], outcells_[3], yout, outdim[3], xindex_[3]);
            B(i,j,k,blitz::Range(0,outdim[3]-1),l,p)=yout;
					 }
				 }
			 }
		 }
	 }
#ifdef DEBUG
	 cout<<"loop 4"<<endl;
#endif


	 yin.resize(indim[4]);
	 yout.resize(outdim[4]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<outdim[1]; j++) {
	     for (int k=0; k<outdim[2]; k++) {
	       for (int l=0; l<outdim[3]; l++) {
	         for (int p=0; p<indim[5]; p++) {
					  yin=B(i,j,k,l,blitz::Range(0,indim[4]-1),p);
            pchip_int(incells_[4], yin,  indim[4], outcells_[4], yout, outdim[4], xindex_[4]);
            B(i,j,k,l,blitz::Range(0,outdim[4]-1),p)=yout;
					 }
				 }
			 }
		 }
	 }
#ifdef DEBUG
	 cout<<"loop 5"<<endl;
#endif


	 yin.resize(indim[5]);
	 yout.resize(outdim[5]);
	 for (int i=0; i<outdim[0]; i++) {
	   for (int j=0; j<outdim[1]; j++) {
	     for (int k=0; k<outdim[2]; k++) {
	       for (int l=0; l<outdim[3]; l++) {
	         for (int p=0; p<outdim[4]; p++) {
					  yin=B(i,j,k,l,p,blitz::Range(0,indim[5]-1));
            pchip_int(incells_[5], yin,  indim[5], outcells_[5], yout, outdim[5], xindex_[5]);
            B(i,j,k,l,p,blitz::Range(0,outdim[5]-1))=yout;
					 }
				 }
			 }
		 }
	 }
#ifdef DEBUG
	 cout<<"loop 6"<<endl;
#endif


   blitz::Array<dcomplex,6> C=B(blitz::Range(0,outdim[0]-1),blitz::Range(0,outdim[1]-1),blitz::Range(0,outdim[2]-1),blitz::Range(0,outdim[3]-1),blitz::Range(0,outdim[4]-1), blitz::Range(0,outdim[5]-1));
	 out=new Vells(C);
	}
	}
	return out;
}
} // namespace Meq
