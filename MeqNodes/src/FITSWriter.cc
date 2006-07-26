//# FITSWriter.cc: Write a Result to a FITS file
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

#include <MeqNodes/FITSWriter.h>
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
	if (invs.isReal()) {
	 double *data=const_cast<double *>(invs.realStorage());
   flag=write_fits_file(filename_.c_str(), data,  cells, naxis, naxes, 0);
	} else { //complex data
	 double *data=const_cast<double*>(reinterpret_cast<const double *>(invs.complexStorage()));
   flag=write_fits_file(filename_.c_str(), data,  cells, naxis, naxes, 1);
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
