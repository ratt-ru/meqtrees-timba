//# FITSWriter.cc: Write a Result to a FITS file
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

#include <MeqNodes/FITSWriter.h>
#include <MeqNodes/FITSUtils.h>
#include <MEQ/MeqVocabulary.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MEQ/VellsSlicer.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>
#include <unistd.h>

//#define DEBUG
namespace Meq {

const HIID FFilename= AidFilename;


//##ModelId=400E5355029C
FITSWriter::FITSWriter()
	: Node(1)
{

}

//##ModelId=400E5355029D
FITSWriter::~FITSWriter()
{}

void FITSWriter::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
	Node::setStateImpl(rec,initializing);

	rec[FFilename].get(filename_,initializing);
#ifdef DEBUG
  cout<<"File Name ="<<filename_<<endl;
#endif

}

 
int FITSWriter::getResult (Result::Ref &resref, 
                       const std::vector<Result::Ref> &childres,
                       const Request &request,bool)
{

  const Result &chres = *( childres.front() );

	//no vellsets
	if (chres.numVellSets()==0) {
    resref=childres[0];
    return 0;
	}
	//we only write the first vellset
	const Vells &invs=chres.vellSet(0).getValue();
	long int naxis;
	long int *naxes;
	double **cells;

#ifdef DEBUG
	cout<<"Dims ="<<chres.dims()<<" Rank="<<chres.tensorRank()<<endl;
#endif

	Vells::Shape shape=chres.vellSet(0).shape();
	if (chres.hasCells()) {
	  naxis=shape.size();

  if ((naxes=(long int*)calloc((size_t)naxis,sizeof(long int)))==0) {
		fprintf(stderr,"no free memory\n");
		exit(1);
  }
#ifdef DEBUG
	cout<<"Shape ="<<shape<<endl;
#endif
	for (long int ii=0; ii<naxis; ii++) {
		naxes[ii]=shape[ii];
	}

	/* cells of each axes (centers) */
	if ((cells=(double**)calloc((size_t)naxis,sizeof(double*)))==0) {
		fprintf(stderr,"no free memory\n");
		exit(1);
  }

	const Cells &incells = chres.cells();
	for (long int ii=0; ii<naxis; ii++) {
		if (naxes[ii]) {
		blitz::Array<double,1> xx=incells.center(ii);
#ifdef DEBUG
		cout<<"ax ="<<naxes[ii]<<" but cells "<<xx.extent(0)<<endl;
#endif
		if (naxes[ii]>xx.extent(0))
      naxes[ii]=xx.extent(0); //sanity check
		if ((cells[ii]=(double*)calloc((size_t)naxes[ii],sizeof(double)))==0) {
		 fprintf(stderr,"no free memory\n");
		 exit(1);
		}
		//copy values
		for(int jj=0; jj<naxes[ii]; jj++) 
			cells[ii][jj]=xx(jj);
		} else {
			cells[ii]=0;
		}
  }
	} else { /* no cells: scalar */
		naxis=1; //just a scalar
   if ((naxes=(long int*)calloc((size_t)naxis,sizeof(long int)))==0) {
		fprintf(stderr,"no free memory\n");
		exit(1);
   }
		cells=0;
		naxes[0]=1;
	}

	int flag=0;
	if (invs.isReal()) { /* assert that all vells are either real or complex */
   /* allocate memory for data array */
   double **data;
   int nvs=chres.numVellSets();
   if ((data=(double**)calloc((size_t)nvs,sizeof(double*)))==0) {
		 fprintf(stderr,"no free memory\n");
		 exit(1);
   }
   for (int ci=0; ci<nvs; ci++) {
	  const Vells &invells=chres.vellSet(ci).getValue();
    if ((data[ci]=(double*)calloc((size_t)invells.nelements(),sizeof(double)))==0) {
		 fprintf(stderr,"no free memory\n");
		 exit(1);
    }
	  memcpy(data[ci],const_cast<double *>(invells.realStorage()),sizeof(double)*(size_t)invells.nelements());
   }
   unlink(filename_.c_str());
   flag=write_fits_file(filename_.c_str(), data,  nvs, cells, naxis, naxes, 0);
   for (int ci=0; ci<nvs; ci++) {
    free(data[ci]);
   }
   free(data);
	} else { //complex data
   double **data;
   int nvs=chres.numVellSets();
   if ((data=(double**)calloc((size_t)nvs*2,sizeof(double*)))==0) {
		 fprintf(stderr,"no free memory\n");
		 exit(1);
   }
   for (int ci=0; ci<nvs; ci++) {
	  const Vells &invells=chres.vellSet(ci).getValue();
	  const Vells &invsr=Meq::VellsMath::real(invells);
    if ((data[2*ci]=(double*)calloc((size_t)invsr.nelements(),sizeof(double)))==0) {
		 fprintf(stderr,"no free memory\n");
		 exit(1);
    }
	  memcpy(data[2*ci],(invsr.realStorage()),sizeof(double)*(size_t)invsr.nelements());
	  const Vells &invsi=Meq::VellsMath::imag(invells);
    if ((data[2*ci+1]=(double*)calloc((size_t)invsi.nelements(),sizeof(double)))==0) {
		 fprintf(stderr,"no free memory\n");
		 exit(1);
    }
	  memcpy(data[2*ci+1],(invsi.realStorage()),sizeof(double)*(size_t)invsi.nelements());
   }
   unlink(filename_.c_str());
   flag=write_fits_file(filename_.c_str(), data,  nvs, cells, naxis, naxes, 1);
   for (int ci=0; ci<nvs; ci++) {
    free(data[2*ci]);
    free(data[2*ci+1]);
   }
   free(data);
	}


	free(naxes);

	if (chres.hasCells()) {
	for (long int ii=0; ii<naxis; ii++) {
		free(cells[ii]);
	}
	free(cells);
	}

	//keep the original result
  resref=childres[0];
 return flag;
}


} // namespace Meq
