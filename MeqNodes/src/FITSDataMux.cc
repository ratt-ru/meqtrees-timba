//# FITSDataMux.cc: Read a FITS file and return the Result
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

#include <MeqNodes/FITSDataMux.h>
#include <MeqNodes/FITSUtils.h>
#include <MeqNodes/FITSSpigot.h>
#include <MEQ/MeqVocabulary.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MEQ/VellsSlicer.h>
#include <MEQ/Forest.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>


//#define DEBUG
namespace Meq {

const HIID FFilename= AidFilename;
const HIID FCutoff= AidCutoff;
const HIID FInput    = AidInput;
const HIID symdeps[] = { FDomain,FResolution };
const HIID FSequenceSymdeps = AidSequence|AidSymdeps;


FITSDataMux::FITSDataMux()
	: Node() //
{

}

FITSDataMux::~FITSDataMux()
{}

void FITSDataMux::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
	Node::setStateImpl(rec,initializing);
	//create 2 new axes -- Freq is already present
	Axis::addAxis("L"); //L
	Axis::addAxis("M"); //M

	//default seq symdeps
	seq_symdeps_.resize(1);
	seq_symdeps_.assign(1,AidState);
}

int FITSDataMux::pollChildren (Result::Ref &resref,
                            std::vector<Result::Ref> &childres,
                            const Request &req) {

		const DMI::Record * inrec = req[FInput].as_po<DMI::Record>();
		if( !inrec )
				return Node::pollChildren(resref,childres,req);
    init_self_(*inrec);
		//1)Read FITS file
		//2)create result, give it to spigot
		//3)create Request to cover the result domain
		//4)poll children
		//5)get result from children and write back to FITS file

////////////////////////////////////// BEGIN paste of FITSImage code
    double *arr, *lgrid, *mgrid, *lspace, *mspace, ra0, dec0, *fgrid, *fspace;
    long int naxis[4]={0,0,0,0};
    int flag=mux_read_fits_file(filename_.c_str(),cutoff_,&arr, naxis, &lgrid, &mgrid, &lspace, &mspace, &ra0, &dec0, &fgrid, &fspace, &filep_);
    FailWhen(flag," Error Reading Fits File "+flag);
 //create a result with 6 vellsets, is integrated
 //if integrated=0, cells is removed
 Result::Ref old_res_;
 Result &result=old_res_<<= new Result(6,1); 

 /* RA0 vellset */
 VellSet::Ref ref0;
 VellSet &vs0= ref0<<= new VellSet(0,1);
 Vells ra_vells=vs0.setValue(new Vells(ra0));
 result.setVellSet(0,ref0);

 /* Dec0 vellset */
 VellSet::Ref ref1;
 VellSet &vs1= ref1<<= new VellSet(0,1);
 Vells dec_vells=vs1.setValue(new Vells(dec0));
 result.setVellSet(1,ref1);


 //the real business begins
 //create blitz arrays for new axes l,m
 blitz::Array<double,1> l_center(lgrid, blitz::shape(naxis[0]), blitz::duplicateData); 
 blitz::Array<double,1> l_space(lspace, blitz::shape(naxis[0]), blitz::duplicateData); 
 blitz::Array<double,1> m_center(mgrid, blitz::shape(naxis[1]), blitz::duplicateData); 
 blitz::Array<double,1> m_space(mspace, blitz::shape(naxis[1]), blitz::duplicateData); 
 blitz::Array<double,1> f_center(fgrid, blitz::shape(naxis[3]), blitz::duplicateData); 
 blitz::Array<double,1> f_space(fspace, blitz::shape(naxis[3]), blitz::duplicateData); 
#ifdef DEBUG
 cout<<"Grid :"<<l_center<<m_center<<f_center<<endl;
 cout<<"Space:"<<l_space<<m_space<<f_space<<endl;
#endif

 //see if frequency axis is reversed
 bool reverse_freq=(f_center(0)> f_center(naxis[3]-1));

 Domain::Ref domain(new Domain());
 //get the frequency from the request
 if (reverse_freq ) {
   domain().defineAxis(Axis::FREQ,f_center(naxis[3]-1)+f_space(naxis[3]-1)/2, f_center(0)-f_space(0)/2);
 } else {
  domain().defineAxis(Axis::FREQ,f_center(0)-f_space(0)/2,f_center(naxis[3]-1)+f_space(naxis[3]-1)/2);
 }
 domain().defineAxis(Axis::axis("L"),l_center(0)-l_space(0)/2,l_center(naxis[0]-1)+l_space(naxis[0]-1)/2);
 domain().defineAxis(Axis::axis("M"),m_center(0)-m_space(0)/2,m_center(naxis[1]-1)+m_space(naxis[1]-1)/2);
 Cells::Ref cells_ref;
 Cells &cells=cells_ref<<=new Cells(*domain);

 //axis, [left,right], segments
 if (reverse_freq ) {
  blitz::Array<double,1> f1;
	f1=blitz::abs(f_space);
	cells.setCells(Axis::FREQ,f_center.reverse(0),f1);
 } else {
	cells.setCells(Axis::FREQ,f_center,f_space);
 }
 cells.setCells(Axis::axis("L"),l_center,l_space);
 cells.setCells(Axis::axis("M"),m_center,m_space);

#ifdef DEBUG
 cout<<"Cells ="<<cells<<endl;
 cout<<"Axis F "<<cells.ncells(Axis::FREQ)<<endl;
 cout<<"Axis L "<<cells.ncells(Axis::axis("L"))<<endl;
 cout<<"Axis M "<<cells.ncells(Axis::axis("M"))<<endl;
#endif
  Vells::Shape shape;

 unsigned int maxrank=std::max(Axis::axis("L"),Axis::axis("M"));
 if (shape.size()<maxrank+1) {
		shape.resize(maxrank+1,1);//resize, and make a all 1 vector
 }
 //shape is time=1,freq,l,m and other axes (u,v)
 shape[Axis::TIME]=1;
 shape[Axis::FREQ]=naxis[3];
 shape[Axis::axis("L")]=naxis[0];
 shape[Axis::axis("M")]=naxis[1];
 //Vells::Shape shape(1,naxis[3],naxis[0],naxis[1]);
#ifdef DEBUG
 cout<<"Ranks "<<shape.size()<<"and "<<cells.rank()<<endl;
 cout<<"Shapes "<<shape<<cells.shape()<<endl;
#endif
 // axes are L(0),M(1),Stokes(2),Freq(3)
 // but here we have Freq,Stokes,L,M
 blitz::Array<double,4> A(arr, blitz::shape(naxis[3],naxis[2],naxis[1],naxis[0]), blitz::duplicateData); 

 //transpose array such that Freq,L,M,Stokes
 A.transposeSelf(0,3,2,1);
 //cout<<"Transpose ="<<A<<endl;
#ifdef DEBUG
 cout<<"Transpose ="<<A.shape()<<endl;
#endif

 //blitz::Range lrange=blitz::Range::all();
 blitz::Range lrange=blitz::Range(naxis[0]-1,0,-1);
 ///Stokes I
 VellSet::Ref refI;
 VellSet &vs= refI<<= new VellSet(0,1);
 //create 3D vells Time=1,Freq,L,M
 Vells &out=vs.setValue(new Vells(0.0,shape));
 vs.setShape(shape);
 //select all 3 axes of the output (slice through axes Freq,L,M)
 VellsSlicer<double,3> slout(out,Axis::FREQ,Axis::axis("L"),Axis::axis("M"));
 //copy A to the time slice of varr
 if (reverse_freq) {
  slout=A(blitz::Range(blitz::toEnd,blitz::fromStart,-1), lrange, blitz::Range::all(),0);
 } else {
  slout=A(blitz::Range::all(), lrange, blitz::Range::all(),0);
 }
 result.setVellSet(2,refI);


 //Stokes Q
 VellSet::Ref refQ;
 if (naxis[2]>1) {
  VellSet &vsQ= refQ<<= new VellSet(0,1);
  Vells &outQ=vsQ.setValue(new Vells(0.0,shape));
  vsQ.setShape(shape);
  VellsSlicer<double,3> sloutQ(outQ,Axis::FREQ,Axis::axis("L"),Axis::axis("M"));

 if (reverse_freq) {
  sloutQ=A(blitz::Range(blitz::toEnd,blitz::fromStart,-1), lrange, blitz::Range::all(),1);
 } else {
  sloutQ=A(blitz::Range::all(), lrange, blitz::Range::all(),1);
 }
  result.setVellSet(3,refQ);
 } else {
  VellSet &vsQ=refQ<<= new VellSet(0,1);
  vsQ.setValue(new Vells(0.0));
  result.setVellSet(3,refQ);
 }

 //Stokes U
 VellSet::Ref refU;
 if (naxis[2]>2) {
  VellSet &vsU= refU<<= new VellSet(0,1);
  Vells &outU=vsU.setValue(new Vells(0.0,shape));
  vsU.setShape(shape);
  VellsSlicer<double,3> sloutU(outU,Axis::FREQ,Axis::axis("L"),Axis::axis("M"));
 if (reverse_freq) {
  sloutU=A(blitz::Range(blitz::toEnd,blitz::fromStart,-1), lrange, blitz::Range::all(),2);
 } else {
  sloutU=A(blitz::Range::all(), lrange, blitz::Range::all(),2);
 }
  result.setVellSet(4,refU);
 } else {
  VellSet &vsU=refU<<= new VellSet(0,1);
  Vells &outU=vsU.setValue(new Vells(0.0));
  result.setVellSet(4,refU);
 }

 //Stokes V
 VellSet::Ref refV;
 if (naxis[2]>3) {
  VellSet &vsV= refV<<= new VellSet(0,1);
  Vells &outV=vsV.setValue(new Vells(0.0,shape));
  vsV.setShape(shape);
  VellsSlicer<double,3> sloutV(outV,Axis::FREQ,Axis::axis("L"),Axis::axis("M"));
 if (reverse_freq) {
  sloutV=A(blitz::Range(blitz::toEnd,blitz::fromStart,-1), lrange, blitz::Range::all(),3);
 } else {
  sloutV=A(blitz::Range::all(), lrange, blitz::Range::all(),3);
 }
  result.setVellSet(5,refV);
 } else {
  VellSet &vsV=refV<<= new VellSet(0,1);
  Vells &outV=vsV.setValue(new Vells(0.0));
  result.setVellSet(5,refV);
 }
 result.setCells(cells);

 //transfer result
 resref=old_res_;

 free(lgrid);
 free(lspace);
 free(mgrid);
 free(mspace);
 free(fgrid);
 free(fspace);


///////////////////////////////////// END paste

 //get spigot
 FITSSpigot * spigot = dynamic_cast<FITSSpigot*>(&(stepchildren().getChild(0)));
 FailWhen(!spigot,"Stepchild 0 is not a FITSSpigot"); 
 spigot->putResult(old_res_);


 //poll children
    setExecState(CS_ES_POLLING);
    timers().children.start();
    Result::Ref child_res;
    childres.resize(numChildren());

	//create new request
		Request::Ref newreq(req);
		newreq().setCells(cells);
  //increment request sequence sub id
	  seq_depmask_ = symdeps().getMask(seq_symdeps_);

		RequestId rqid=req.id();
		RqId::incrSubId(rqid,seq_depmask_);
		newreq().setId(rqid);


		for (int ii=0; ii<numChildren(); ii++) {
    unlockStateMutex();
    int code=children().getChild(ii).execute(child_res,newreq);
    lockStateMutex();
    childres[ii]=child_res;

    //handle standard error states
    if(forest().abortFlag())
      return RES_ABORT;
    if(code&RES_WAIT) {
      //this node will need to run again 
      timers().children.stop();
      return 0;
    }
    if (code&RES_FAIL) {
      resref.xfer(childres[0]);
      timers().children.stop();
      return code;
    }
		}

    timers().children.stop();


		//write the result of children back to FITS file
		//only handle child 1 for the moment
		//expect a sixpack
		int nvs=childres[0]->numVellSets();
		FailWhen(nvs!=6,"Need a Sixpack from children");

		Vells sI=childres[0]->vellSet(2).getValue();
		Vells sQ=childres[0]->vellSet(3).getValue();
		Vells sU=childres[0]->vellSet(4).getValue();
		Vells sV=childres[0]->vellSet(5).getValue();
		if (!sI.isScalar()) {

     VellsSlicer<double,3> slout(sI,Axis::FREQ,Axis::axis("L"),Axis::axis("M"));
     A(blitz::Range::all(), lrange, blitz::Range::all(),0)=slout.array();
		} else {
     A(blitz::Range::all(), lrange, blitz::Range::all(),0)=sI.getScalar<double>();
		}
		if (naxis[2]>1) {
 		  if (!sQ.isScalar()) {
       VellsSlicer<double,3> slout(sQ,Axis::FREQ,Axis::axis("L"),Axis::axis("M"));
       A(blitz::Range::all(), lrange, blitz::Range::all(),1)=slout.array();
		  } else {
       A(blitz::Range::all(), lrange, blitz::Range::all(),1)=sQ.getScalar<double>();
		  }
		}
		if (naxis[2]>2) {
  	  if (!sU.isScalar()) {
       VellsSlicer<double,3> slout(sU,Axis::FREQ,Axis::axis("L"),Axis::axis("M"));
       A(blitz::Range::all(), lrange, blitz::Range::all(),2)=slout.array();
		  } else {
       A(blitz::Range::all(), lrange, blitz::Range::all(),2)=sU.getScalar<double>();
		  }
		}
		if (naxis[2]>3) {
   	  if (!sV.isScalar()) {
       VellsSlicer<double,3> slout(sV,Axis::FREQ,Axis::axis("L"),Axis::axis("M"));
       A(blitz::Range::all(), lrange, blitz::Range::all(),3)=slout.array();
		  } else {
       A(blitz::Range::all(), lrange, blitz::Range::all(),3)=sV.getScalar<double>();
		  }
		}
 

    A.transposeSelf(0,3,2,1);
		mux_write_fits_file((double*)A.data(),filep_);
    free(arr);
		return 0;
}
 

void FITSDataMux::init_self_(const DMI::Record &rec) {
  //get from init record
	if (rec.hasField(FFilename)) { 	
	  rec[FFilename].get(filename_); 	
	} else { 
		FailWhen(1,"Need a FITS file name as input");
	}

	cutoff_=1.0;
	if(rec.hasField(FCutoff)) {
			rec[FCutoff].get(cutoff_);
	}
  cout<<"File Name ="<<filename_<<endl;
  cout<<"Cutoff="<<cutoff_<<endl;
}
} // namespace Meq
