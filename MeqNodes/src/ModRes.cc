//# ModRes.cc: modifies request resolutions
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
//# $Id$

#include <MeqNodes/ModRes.h>
#include <MEQ/MeqVocabulary.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>


//#define DEBUG 
namespace Meq {

//const HIID FFactor = AidFactor;
const HIID FNumCells = AidNum|AidCells;
const HIID FUpsample = AidUpsample;
const HIID FDownsample = AidDownsample;

const HIID FResolutionSymdeps    = AidResolution|AidSymdeps;
const HIID FResolutionId         = AidResolution|AidId;

const HIID symdeps[] = { FDomain,FResolution };

//##ModelId=400E5355029C
ModRes::ModRes()
: Node(1), // 1 child expected
	do_resample_(0),do_upsample_(0),do_downsample_(0),res_index_(0)
{
  // our own result depends on domain & resolution
  res_symdeps_.assign(1,AidResolution);
}

//##ModelId=400E5355029D
ModRes::~ModRes()
{}

void ModRes::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
  Node::setStateImpl(rec,initializing);
  std::vector<int> numcells;
  if (rec[FNumCells].get_vector(numcells)) {
#ifdef DEBUG
    cout<<"Initializing "<<numcells.size()<<" Cells ";
    for (unsigned int i=0;i<numcells.size();i++) cout<<numcells[i]<<", ";
    cout<<endl;
#endif
    if (numcells.size()>0) {
    do_resample_=1;
    nx_=numcells[0];
    }
    if (numcells.size()>1)
    ny_=numcells[1];
  }

  if (rec[FUpsample].get_vector(upsample_)) {
#ifdef DEBUG
    cout<<"Initializing "<<upsample_.size()<<" Cells ";
    for (unsigned int i=0;i<upsample_.size();i++) cout<<upsample_[i]<<", ";
    cout<<endl;
#endif
		if (upsample_.size()==2) {
     do_resample_=1;
     do_upsample_=1;
		}
	}
  if (rec[FDownsample].get_vector(downsample_)) {
#ifdef DEBUG
    cout<<"Initializing "<<downsample_.size()<<" Cells ";
    for (unsigned int i=0;i<downsample_.size();i++) cout<<downsample_[i]<<", ";
    cout<<endl;
#endif
		if (downsample_.size()==2) {
     do_resample_=1;
     do_downsample_=1;
		}
	}


  // get symdeps
  rec[FResolutionSymdeps].get_vector(res_symdeps_,initializing);
  // get resolution index
  rec[FResolutionId].get(res_index_,initializing);
}

int ModRes::pollChildren (Result::Ref &resref,
                          std::vector<Result::Ref> &childres,
                          const Request &request)
{
  res_depmask_ = symdeps().getMask(res_symdeps_);
  if( do_resample_ && request.hasCells()) 
  {
     Request::Ref newreq(request);
    const Cells &incells = request.cells();

    Cells::Ref outcells_ref; 
    int nx=incells.center(0).extent(0);
    int ny=incells.center(1).extent(0);

		if (!(do_upsample_ | do_downsample_)) {
		//simple uniform resampling
    //determine the resampling to be done
    int nx1=nx_;
    int ny1=ny_;
    //sanity check: if either is zero, do not resample in that dimension
    if (nx1<1) nx1=nx;
    if (ny1<1) ny1=ny;
#ifdef DEBUG
    cout<<"Resampling Request new size "<<nx1<<" x "<<ny1<<endl;
#endif
    Cells &outcells = outcells_ref<<=new Cells(request.cells().domain(),nx1,ny1);
    newreq().setCells(outcells);
		} else {
      blitz::Array<double,1> xax;
      blitz::Array<double,1> xsp;
      blitz::Array<double,1> yax;
      blitz::Array<double,1> ysp;

			//we have a complex situation. determine what to do
			if (do_upsample_&&(upsample_[0]>1)) {
					//upsample X axis
        blitz::Array<double,1> x_orig=incells.center(0);
        blitz::Array<double,1> xsp_orig=incells.cellSize(0);
				//each 1 cell will give rise to upsample_[0] new cells
				xax.resize(upsample_[0]*x_orig.size());
				xsp.resize(upsample_[0]*x_orig.size());
				for (int i=0; i<x_orig.size();i++) {
								double x0=x_orig(i)-xsp_orig(i)*0.5;
								double x1=xsp_orig(i)/(double)upsample_[0];
								int start=i*upsample_[0];
								xax(start)=x0+x1*0.5;
								xsp(start)=x1;
								for (int j=1;j<upsample_[0];j++) {
									xax(start+j)=xax(start+j-1)+x1;
								  xsp(start+j)=x1;
								}
				}
#ifdef DEBUG
				cout<<"Orig "<<x_orig<<endl<<xsp_orig<<endl;
				cout<<"New "<<xax<<endl<<xsp<<endl;
#endif
			} else if (do_downsample_&&(downsample_[0]>1))  {
				 //downsample X axis
				 //each downsample_[0] cells will be converted to one cell
				 //the tail will have the remainder
        

        blitz::Array<double,1> x_orig=incells.center(0);
        blitz::Array<double,1> xsp_orig=incells.cellSize(0);

				//sanity check 
				if (downsample_[0]>incells.center(0).size()) {
						downsample_[0]=incells.center(0).size();
				}
				int N=(int)ceil((double)x_orig.size()/(double)downsample_[0]);
				xax.resize(N);
				xsp.resize(N);
				double x0,x1;
				for (int i=0;i<N-1;i++) {
          x0=x_orig(i*downsample_[0])-xsp_orig(i*downsample_[0])*0.5;
          x1=x_orig((i+1)*downsample_[0]-1)+xsp_orig((i+1)*downsample_[0]-1)*0.5;
					xax(i)=(x0+x1)*0.5;
					xsp(i)=(x1-x0);
				}
				//last cell is the tail
        x0=x_orig((N-1)*downsample_[0])-xsp_orig((N-1)*downsample_[0])*0.5;
        x1=x_orig(x_orig.size()-1)+xsp_orig(x_orig.size()-1)*0.5;
				xax(N-1)=(x0+x1)*0.5;
				xsp(N-1)=(x1-x0);
#ifdef DEBUG
				cout<<"Orig "<<x_orig<<endl<<xsp_orig<<endl;
				cout<<"New "<<xax<<endl<<xsp<<endl;
#endif

			} else {
				//X axis is not being changed
				xax=incells.center(0);
				xsp=incells.cellSize(0);
			}
			if (do_upsample_&&(upsample_[1]>1)) {
					//upsample Y axis
        blitz::Array<double,1> y_orig=incells.center(1);
        blitz::Array<double,1> ysp_orig=incells.cellSize(1);
				//each 1 cell will give rise to upsample_[1] new cells
				yax.resize(upsample_[1]*y_orig.size());
				ysp.resize(upsample_[1]*y_orig.size());
				for (int i=0; i<y_orig.size();i++) {
								double y0=y_orig(i)-ysp_orig(i)*0.5;
								double y1=ysp_orig(i)/(double)upsample_[1];
								int start=i*upsample_[1];
								yax(start)=y0+y1*0.5;
								ysp(start)=y1;
								for (int j=1;j<upsample_[1];j++) {
									yax(start+j)=yax(start+j-1)+y1;
								  ysp(start+j)=y1;
								}
				}
#ifdef DEBUG
				cout<<"Orig "<<y_orig<<endl<<ysp_orig<<endl;
				cout<<"New "<<yax<<endl<<ysp<<endl;
#endif
			} else if (do_downsample_&&(downsample_[1]>1))  {
				 //downsample Y axis
        blitz::Array<double,1> y_orig=incells.center(1);
        blitz::Array<double,1> ysp_orig=incells.cellSize(1);

				//sanity check 
				if (downsample_[1]>incells.center(1).size()) {
						downsample_[1]=incells.center(1).size();
				}

				int N=(int)ceil((double)y_orig.size()/(double)downsample_[1]);
				yax.resize(N);
				ysp.resize(N);
				double y0,y1;
				for (int i=0;i<N-1;i++) {
          y0=y_orig(i*downsample_[1])-ysp_orig(i*downsample_[1])*0.5;
          y1=y_orig((i+1)*downsample_[1]-1)+ysp_orig((i+1)*downsample_[1]-1)*0.5;
					yax(i)=(y0+y1)*0.5;
					ysp(i)=(y1-y0);
				}
				//last cell is the tail
        y0=y_orig((N-1)*downsample_[1])-ysp_orig((N-1)*downsample_[1])*0.5;
        y1=y_orig(y_orig.size()-1)+ysp_orig(y_orig.size()-1)*0.5;
				yax(N-1)=(y0+y1)*0.5;
				ysp(N-1)=(y1-y0);
#ifdef DEBUG
				cout<<"Orig "<<y_orig<<endl<<ysp_orig<<endl;
				cout<<"New "<<yax<<endl<<ysp<<endl;
#endif

			} else {
				//Y axis is not being changed
				yax=incells.center(1);
				ysp=incells.cellSize(1);
			}

			//create new cells using new axes
			Cells &outcells=outcells_ref<<=new Cells(incells.domain());
			//copy the first two axes 
			outcells.setCells(Axis::TIME, xax,xsp);
			outcells.setCells(Axis::FREQ, yax,ysp);
      newreq().setCells(outcells);
		}
    //FIXME: can cache the current cells
    // update request id according to symdeps
    RequestId newid = request.id();
    if( res_index_ )
      RqId::setSubId(newid,res_depmask_,res_index_);
    else
      RqId::incrSubId(newid,res_depmask_);
    newreq().setId(newid);
    return Node::pollChildren(resref,childres,newreq);

  } else {
    //do nothing
    return Node::pollChildren(resref,childres,request);
  }
  // will not get here
  return 0;
} 

int ModRes::getResult (Result::Ref &resref, 
                       const std::vector<Result::Ref> &childres,
                       const Request &request,bool)
{
  Assert(childres.size()==1);
  resref=childres[0];
  return 0;
}


} // namespace Meq
