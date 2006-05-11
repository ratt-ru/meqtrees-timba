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
#include <MEQ/MeqVocabulary.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MEQ/VellsSlicer.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>

//#define DEBUG
extern "C" {
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
// the following is available from the libcfitsio-dev package on Debian,
// in a perfect world it should be found by configure
#include <fitsio.h>
int write_fits_file(const char *filename,  double *myarr,  double **cells,
				long int naxis, long int *naxes);

}/* extern C */

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

	double *data=const_cast<double *>(invs.realStorage());
  int flag=write_fits_file(filename_.c_str(), data,  cells, naxis, naxes);


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
int write_fits_file(const char *filename,  double *arr,  double **cells,
			long int naxis, long int *naxes) {

				/* what do we do about axes with zero length: we do not consider them
				 * to be present in the image but we store that information in the table
				 * each table column will begin with the number in that axes
				 */
       fitsfile *outfptr;
			 int status;

			 long int nelements, maxrow;
			 long int fpixel=1;
			 long int ii,jj;

			 char **ttype,**tform,**tunit;
			 long int firstrow,firstelem;
			 long int totaxs, *real_naxes;
			 double *colarr;
			 int has_cells;

 
#ifdef DEBUG
			 printf("axis =%ld\n",naxis);
#endif
			 maxrow=0;
       nelements=1;
			 totaxs=0;
			 for (ii=0; ii<naxis; ii++) {
#ifdef DEBUG
					printf("axis %ld has %ld\n",ii,naxes[ii]);
#endif
				if (maxrow<naxes[ii]) maxrow=naxes[ii];
			  if (naxes[ii]) {
         nelements*=naxes[ii];
				 totaxs++;
				}
			 }	

			 /* now allocate memory for real axes array */
			 if ((real_naxes=(long int*)calloc((size_t)totaxs,sizeof(long int)))==0) {
					fprintf(stderr,"no free memory\n");
					exit(1);
			 }

			 jj=0;
			 for (ii=0; ii<naxis; ii++) {
			  if (naxes[ii] && jj<totaxs) {
					real_naxes[jj++]=naxes[ii];
				}
			 }

#ifdef DEBUG
			 printf("found %ld real axes\n",totaxs);
			 for (ii=0; ii<totaxs; ii++) {
					printf("%ld: %ld ",ii,real_naxes[ii]);
			 }
			 printf("\n");
			 for (ii=0;ii<nelements;ii++) {
					printf("%ld: %lf ",ii,arr[ii]);
			 }
			 printf("\n");
#endif

			 status=0;
			 
			 fits_create_file(&outfptr,filename,&status);

			 fits_create_img(outfptr,DOUBLE_IMG,totaxs,real_naxes,&status);

			 fits_write_img(outfptr,TDOUBLE,fpixel,nelements,arr,&status);


			 if (cells) { /* has cells */
			 /* write a keyword to indicate the presence of cells */
       has_cells=1;
			 fits_update_key(outfptr, TINT, "CELLS", &has_cells,"Has Cells 1: yes 0: no", &status);

			 /* the table to store the cells: one column for one axis */
			 /* the number of rows will be the max axis length */
			 /* define the name, datatype, and physical units for all the columns */
			 if ((ttype=(char**)calloc((size_t)naxis,sizeof(char*)))==0) {
				fprintf(stderr,"no free memory\n");
				exit(1);
			 }
			 if ((tform=(char**)calloc((size_t)naxis,sizeof(char*)))==0) {
				fprintf(stderr,"no free memory\n");
				exit(1);
			 }
			 if ((tunit=(char**)calloc((size_t)naxis,sizeof(char*)))==0) {
				fprintf(stderr,"no free memory\n");
				exit(1);
			 }

			 for (ii=0; ii<naxis; ii++) {
  			 if ((ttype[ii]=(char*)calloc((size_t)6,sizeof(char)))==0) {
  				fprintf(stderr,"no free memory\n");
  				exit(1);
  			 }
  			 if ((tform[ii]=(char*)calloc((size_t)3,sizeof(char)))==0) {
  				fprintf(stderr,"no free memory\n");
  				exit(1);
  			 }
  			 if ((tunit[ii]=(char*)calloc((size_t)1,sizeof(char)))==0) {
  				fprintf(stderr,"no free memory\n");
  				exit(1);
  			 }
				 /* copy column names */
				 sprintf(ttype[ii],"Ax %ld",ii);
				 /* form of data */
				 sprintf(tform[ii],"1E");
				 /*tunit is not needed, so we just null terminate */
				 strcpy(tunit[ii],"\0");
			 }


#ifdef DEBUG
			printf("axes in table %ld\n",naxis);
			 for (ii=0; ii<naxis; ii++) {
				printf("axis %ld\n",ii);
				if (naxes[ii]) {
	  		 for (jj=0; jj<naxes[ii];jj++) 
		   			printf(" %lf, ",cells[ii][jj]);
				}
				 printf("\n");

			 }
#endif

			 /* create table */
			 /* add one more row such that we can write no of elements in each axis */
			 fits_create_tbl( outfptr, BINARY_TBL, maxrow+1, naxis, ttype, tform,
																	                tunit, "Cells_TBL", &status);


			 firstrow  = 1;  /* first row in table to write   */
			 firstelem = 1;  /* first element in row  (ignored in ASCII tables) */

       /* the array where we create each column before writing */
			 if ((colarr=(double*)calloc((size_t)(maxrow+1),sizeof(double)))==0) {
				fprintf(stderr,"no free memory\n");
				exit(1);
			 }
			 for (ii=0; ii<naxis; ii++) {
				/* write only if this axis is defined */
				memset(colarr,0,sizeof(double)*(size_t)(maxrow+1));
				colarr[0]=naxes[ii];
				if (naxes[ii]) {
					memcpy((void*)&colarr[1],(void*)cells[ii],sizeof(double)*(size_t)naxes[ii]);
				}
#ifdef DEBUG
				printf("axis %ld\n",ii);
				for (jj=0; jj<naxes[ii]+1;jj++) 
		   			printf(" %lf, ",colarr[jj]);
				printf("\n");
#endif
			  fits_write_col(outfptr, TDOUBLE, ii+1, firstrow, firstelem, naxes[ii]+1, colarr, &status);
			 }
			 for (ii=0; ii<naxis; ii++) {
							 free(ttype[ii]);
							 free(tform[ii]);
							 free(tunit[ii]);
			 }

			 free(ttype);
			 free(tform);
			 free(tunit);
			 free(colarr);



			 } else { /* no cells */

       has_cells=0;
			 fits_update_key(outfptr, TINT, "CELLS", &has_cells,"Has Cells 1: yes 0: no", &status);
#ifdef DEBUG
			 printf("no cells were present\n");
#endif
			 }
			 fits_close_file(outfptr,&status);

			 fits_report_error(stderr,status);
			 
			 free(real_naxes);

			return 0;
}
