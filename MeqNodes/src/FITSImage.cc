//# FITSImage.cc: Read a FITS file and convert the Image HDU to  Vellsets
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

#include <MeqNodes/FITSImage.h>
#include <MeqNodes/FITSUtils.h>
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
const HIID FMode= AidMode;


//##ModelId=400E5355029C
FITSImage::FITSImage()
	: Node(0),cutoff_(1.0),has_prev_result_(false),mode_(1)
{

	//create 2 new axes -- Freq is already present
	Axis::addAxis("L"); //L
	Axis::addAxis("M"); //M
}

//##ModelId=400E5355029D
FITSImage::~FITSImage()
{}

void FITSImage::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
	Node::setStateImpl(rec,initializing);

	rec[FFilename].get(filename_,initializing);
#ifdef DEBUG
  cout<<"File Name ="<<filename_<<endl;
#endif
	if(rec[FCutoff].get(cutoff_,initializing)) {
#ifdef DEBUG
   cout<<"Cutoff ="<<cutoff_<<endl;
#endif
	}

	if(rec[FMode].get(mode_,initializing)) {
#ifdef DEBUG
   cout<<"Mode ="<<mode_<<endl;
#endif
	}
	//always cache
	setCachePolicy(Node::CACHE_ALWAYS);
}


int FITSImage::getResult (Result::Ref &resref,
                       const std::vector<Result::Ref> &childres,
                       const Request &request,bool)
{
 double *arr, *lgrid, *mgrid, *lspace, *mspace, ra0, dec0, *fgrid, *fspace;
 long int naxis[4]={0,0,0,0};
 //if (has_prev_result_) {resref=old_res_; return 0; }
 int flag=read_fits_file(filename_.c_str(),cutoff_,&arr, naxis, &lgrid, &mgrid, &lspace, &mspace, &ra0, &dec0, &fgrid, &fspace,mode_);

 FailWhen(flag," Error Reading Fits File "+flag);

#ifdef DEBUG
 for (int i=0;i<4;i++) {cout<<" i="<<i<<" "<<naxis[i]<<endl;}
#endif
 if (mode_==1) {
 //create a result with 6 vellsets, is integrated
 //if integrated=0, cells is removed
 old_res_<<= new Result(6);
 } else {
 //create a result a single vellset, is NOT integrated
 old_res_<<= new Result(1);
 }

 Result &result=old_res_;
 if (mode_==1) {
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
 }


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
 const Cells &incells=request.cells();
 const Domain &old_dom=incells.domain();
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
        blitz::Array<double,1> f1(f_space.size());
        f1 = blitz::abs(f_space);
	cells.setCells(Axis::FREQ,f_center.reverse(0),f1.reverse(0));
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
  Vells::Shape shape(incells.shape());

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
 // but here we have Freq,Stokes,M,L
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
  slout=A(blitz::Range(naxis[3]-1,0,-1), lrange, blitz::Range::all(),0);
 } else {
  slout=A(blitz::Range::all(), lrange, blitz::Range::all(),0);
 }
 if (mode_==1) {
 result.setVellSet(2,refI);
 } else {
  //this is the only vellset
 result.setVellSet(0,refI);
 }


 if (mode_==1) {
 //Stokes Q
 VellSet::Ref refQ;
 if (naxis[2]>1) {
  VellSet &vsQ= refQ<<= new VellSet(0,1);
  Vells &outQ=vsQ.setValue(new Vells(0.0,shape));
  vsQ.setShape(shape);
  VellsSlicer<double,3> sloutQ(outQ,Axis::FREQ,Axis::axis("L"),Axis::axis("M"));

 if (reverse_freq) {
  sloutQ=A(blitz::Range(naxis[3]-1,0,-1), lrange, blitz::Range::all(),1);
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
  sloutU=A(blitz::Range(naxis[3]-1,0,-1), lrange, blitz::Range::all(),2);
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
  sloutV=A(blitz::Range(naxis[3]-1,0,-1), lrange, blitz::Range::all(),3);
 } else {
  sloutV=A(blitz::Range::all(), lrange, blitz::Range::all(),3);
 }
  result.setVellSet(5,refV);
 } else {
  VellSet &vsV=refV<<= new VellSet(0,1);
  Vells &outV=vsV.setValue(new Vells(0.0));
  result.setVellSet(5,refV);
 }
 }
 result.setCells(cells);

 //transfer result
 resref=old_res_;
 has_prev_result_=true;

 free(arr);
 free(lgrid);
 free(lspace);
 free(mgrid);
 free(mspace);
 free(fgrid);
 free(fspace);
 return 0;
}


} // namespace Meq
