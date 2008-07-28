//# FITSReader.cc: Read a FITS file and return the Result
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

#include <MeqNodes/FITSReader.h>
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


//##ModelId=400E5355029C
FITSReader::FITSReader()
	: Node(0) //no children
{

}

//##ModelId=400E5355029D
FITSReader::~FITSReader()
{}

void FITSReader::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
	Node::setStateImpl(rec,initializing);

	rec[FFilename].get(filename_,initializing);
#ifdef DEBUG
  cout<<"File Name ="<<filename_<<endl;
#endif

}


int FITSReader::getResult (Result::Ref &resref,
                       const std::vector<Result::Ref> &childres,
                       const Request &request,bool)
{

	double *data;
	double **centers;
	long int naxis, *naxes;
	int is_complex;
  int flag=simple_read_fits_file(filename_.c_str(), &data,  &centers, &naxis, &naxes, &is_complex);

	FailWhen(flag!=0,"Meq::FITSReader file read failed");
#ifdef DEBUG
	cout<<"Read "<<naxis<<" Axes with flag "<<flag<<endl;
	for (int i=0;i<naxis;i++) {
		cout<<i<<": "<<naxes[i]<<",";
	}
	cout<<endl;
#endif
	//create cells
	//
  Domain::Ref domain(new Domain());
  //get the frequency from the request
  const Cells &incells=request.cells();
  const Domain &old_dom=incells.domain();
	for (int i=0;i<naxis;i++) {
			if (naxes[i]) {
			   if (old_dom.isDefined(i)) {
            //domain().defineAxis(i, old_dom.start(i), old_dom.end(i));
            //domain().defineAxis(i, std::min(centers[i][0]-1, old_dom.start(i)),std::max(centers[i][naxes[i]-1]+1, old_dom.end(i)));
            domain().defineAxis(i, centers[i][0]-1,centers[i][naxes[i]-1]+1);
			   } else { //not defined in old domain
            //domain().defineAxis(i, -1e6, 1e6);
            domain().defineAxis(i, centers[i][0]-1,centers[i][naxes[i]-1]+1);
		     }

			}
	}

  Cells::Ref cells_ref;
  Cells &cells=cells_ref<<=new Cells(*domain);

	for (int i=0;i<naxis;i++) {
		if (naxes[i]) {
      blitz::Array<double,1> l_center(centers[i], blitz::shape(naxes[i]), blitz::duplicateData);
      blitz::Array<double,1> l_space(naxes[i]);
			//calculate spacings
			for (int j=1; j<naxes[i]-1; j++) {
				l_space(j)=(l_center(j)-l_center(j-1))/2+ (l_center(j+1)-l_center(j))/2;
			}
			if (naxes[i]>1) {
       l_space(0)=l_center(1)-l_center(0);
       l_space(naxes[i]-1)=l_center(naxes[i]-1)-l_center(naxes[i]-2);
			} else {
			 l_space(0)=1;
			}
     //attach to cells
#ifdef DEBUG
		cout<<i<<": "<<l_center<<","<<l_space<<endl;
#endif
     cells.setCells(i,l_center,l_space);
		}
	}

  // create a result with one VellSet (1)
  Result &result=resref<<= new Result(1);

	//VellSet
	VellSet::Ref ref0;
	VellSet &vs0=ref0<<=new VellSet(0,1);
	Vells::Shape shape(incells.shape());

	if(shape.size()<(unsigned)naxis) {
		//we need to extend the shape
		shape.resize(naxis,1);//resize and make all 1
	}

	for (int i=0;i<naxis;i++) {
		if (naxes[i]) {
			shape[i]=naxes[i];
		} else {
			shape[i]=1;
		}
	}

#ifdef DEBUG
	cout<<"Shape "<<shape<<endl;
#endif
	if (!is_complex) {
	if (naxis==0) {
	  // scalar
	  vs0.setValue(new Vells(*data));
	} else {
	vs0.setShape(shape);
	Vells &out=vs0.setValue(new Vells(0.0,shape));
	if (naxis==1) {
	  blitz::Array<double,1> A(data,shape,blitz::duplicateData);
		VellsSlicer<double,1> slout(out,0);
		slout=A;
	}else if (naxis==2) {
	  blitz::Array<double,2> A(data,shape,blitz::duplicateData);
		VellsSlicer<double,2> slout(out,0,1);
		slout=A;
	}else if (naxis==3) {
	  blitz::Array<double,3> A(data,shape,blitz::duplicateData);
		VellsSlicer<double,3> slout(out,0,1,2);
		slout=A;
	}else if (naxis==4) {
	  blitz::Array<double,4> A(data,shape,blitz::duplicateData);
		VellsSlicer<double,4> slout(out,0,1,2,3);
		slout=A;
	}
	}
	} else { //we have complex data
		dcomplex *cdata=reinterpret_cast<dcomplex *>(data);

  	if (naxis==0) {
	    // scalar
	    vs0.setValue(new Vells(*cdata));
	   } else {
	    vs0.setShape(shape);
	    Vells &out=vs0.setValue(new Vells(make_dcomplex(0.0),shape));
	    if (naxis==1) {
	     blitz::Array<dcomplex,1> A(cdata,shape,blitz::duplicateData);
		   VellsSlicer<dcomplex,1> slout(out,0);
		   slout=A;
	   }else if (naxis==2) {
	     blitz::Array<dcomplex,2> A(cdata,shape,blitz::duplicateData);
		   VellsSlicer<dcomplex,2> slout(out,0,1);
		   slout=A;
	   }else if (naxis==3) {
	     blitz::Array<dcomplex,3> A(cdata,shape,blitz::duplicateData);
		   VellsSlicer<dcomplex,3> slout(out,0,1,2);
		   slout=A;
	   }else if (naxis==4) {
	     blitz::Array<dcomplex,4> A(cdata,shape,blitz::duplicateData);
		   VellsSlicer<dcomplex,4> slout(out,0,1,2,3);
		   slout=A;
	   }
	 }
	}
	result.setVellSet(0,ref0);
	if (naxis) {
	 result.setCells(cells);
	}

	for (long int ii=0; ii<naxis; ii++) {
		free(centers[ii]);
	}
	if (naxis) {
	 free(naxes);
	 free(centers);
	}
	free(data);
 return flag;
}


} // namespace Meq
