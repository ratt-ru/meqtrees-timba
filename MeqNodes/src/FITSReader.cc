//# FITSReader.cc: Read a FITS file and return the Result
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

#include <MeqNodes/FITSReader.h>
#include <MEQ/MeqVocabulary.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MEQ/VellsSlicer.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>

#define DEBUG
extern "C" {
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
// the following is available from the libcfitsio-dev package on Debian,
// in a perfect world it should be found by configure
#include <fitsio.h>
int simple_read_fits_file(const char *filename,  double **myarr,  double ***cells,
				long int *naxis, long int **naxes);

}/* extern C */

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
	double **cells;
	long int naxis, *naxes;
  int flag=simple_read_fits_file(filename_.c_str(), &data,  &cells, &naxis, &naxes);


	free(naxes);
	for (long int ii=0; ii<naxis; ii++) {
		free(cells[ii]);
	}
	free(cells);
	free(data);
 return flag;
}


} // namespace Meq
int simple_read_fits_file(const char *filename,  double **arr,  double ***cells,
			long int *naxis, long int **naxes) {

       fitsfile *fptr;
			 int status;

			 long int  nelements;
			 int datatype=0;
			 long int ii,jj;

			 int bitpix;
			 long int *increment, *fpix, *lpix;

			 long int firstrow,firstelem;
			 long int nrows;
			 int  ncols,hdunum,hdutype;
			 int null_flag=0;
			 int anynulls=0;
			 int stat;

			 long int *mynaxes;
			 int mynaxis;
			 double *colarr;

			 status=0;
			 stat=fits_open_file(&fptr, filename, READONLY, &status);
       if(stat!=0) return -1;


			 fits_get_img_dim(fptr,&mynaxis,&status);

			 if ((mynaxes=(long int*)calloc((size_t)mynaxis,sizeof(long int)))==0) {
			   fprintf(stderr,"no free memory\n");
				 exit(1);
			 }
			 /* the following arrays are needed to read in the image */
			 if ((increment=(long int*)calloc((size_t)mynaxis,sizeof(long int)))==0) {
			   fprintf(stderr,"no free memory\n");
				 exit(1);
			 }
			 if ((fpix=(long int*)calloc((size_t)mynaxis,sizeof(long int)))==0) {
			   fprintf(stderr,"no free memory\n");
				 exit(1);
			 }
			 if ((lpix=(long int*)calloc((size_t)mynaxis,sizeof(long int)))==0) {
			   fprintf(stderr,"no free memory\n");
				 exit(1);
			 }

			 fits_get_img_size(fptr,mynaxis, mynaxes, &status);
#ifdef DEBUG
			 printf("image has %d axes\n",mynaxis);
			 for (ii=0; ii<mynaxis; ii++)
				 printf("%ld ( %ld ) ",ii,mynaxes[ii]);
			 printf("\n");
#endif
       fits_get_img_type(fptr,&bitpix,&status);
			 if (bitpix!=DOUBLE_IMG)
					printf("wrong data type\n");

			 switch (bitpix) {
				case BYTE_IMG:
					datatype=TBYTE;
					break;
				case SHORT_IMG:
					datatype=TSHORT;
					break;
				case LONG_IMG:
					datatype=TLONG;
					break;
				case FLOAT_IMG:
					datatype=TFLOAT;
					break;
				case DOUBLE_IMG:
					datatype=TDOUBLE;
					break;

			  default:
			    break;		
			 }

			 nelements=1;
			 for (ii=0; ii<mynaxis; ii++) {
				if (mynaxes[ii]) {
				 nelements*=mynaxes[ii];
				 increment[ii]=1;
				 fpix[ii]=1;
				 lpix[ii]=mynaxes[ii];
				}else{
				 increment[ii]=0;
				 fpix[ii]=0;
				 lpix[ii]=mynaxes[ii];
				}
       }

			 /* allocate array for data */
			 if ((*arr=(double*)calloc((size_t)nelements,sizeof(double)))==0) {
				fprintf(stderr,"no free memory\n");
				exit(1);
			 }
			 /* read the whole image increment=[1,1,1,..]*/
			 fits_read_subset(fptr, datatype, fpix, lpix, increment,
													    0, *arr, &null_flag, &status);

#ifdef DEBUG
			 for (ii=0;ii<nelements;ii++) {
					printf("%ld: %lf ",ii,(*arr)[ii]);
			 }
			 printf("\n");
#endif

			 /* the table */
			 if ( fits_get_hdu_num(fptr, &hdunum) == 1 ) {
			  /* This is the primary array;  try to move to the */
			  /* first extension and see if it is a table */
			  fits_movabs_hdu(fptr, 2, &hdutype, &status);
			 } else {
					printf("no table found\n");
					status=-1;
			 }

			 if (hdutype != BINARY_TBL)  {
				printf("Error: expected to find a binary table in this HDU\n");
				status=-1;
			 }

			 fits_get_num_rows(fptr,&nrows,&status);
			 fits_get_num_cols(fptr,&ncols,&status);


#ifdef DEBUG
			 printf("table cols=%d (expected=%d), rows=%ld\n",ncols,mynaxis,nrows);
#endif
			 *naxis=ncols; /* the true number of axes  */
       /* cells of each axes (centers) */
	  	 if ((*cells=(double**)calloc((size_t)ncols,sizeof(double*)))==0) {
				fprintf(stderr,"no free memory\n");
				exit(1);
			 }
			 /* storage for each column */
			 if ((colarr=(double*)calloc((size_t)(nrows),sizeof(double)))==0) {
				fprintf(stderr,"no free memory\n");
				exit(1);
			 }

			 if ((*naxes=(long int*)calloc((size_t)ncols,sizeof(long int)))==0) {
			   fprintf(stderr,"no free memory\n");
				 exit(1);
			 }

			 firstrow=1;
			 firstelem=1;
			 /* read each column */
			 for (ii=0; ii<ncols; ii++) {
				memset(colarr,0,sizeof(double)*(size_t)(nrows));
    		fits_read_col(fptr, TDOUBLE, ii+1, firstrow, firstelem, nrows,
														&null_flag, colarr, &anynulls, &status);

				(*naxes)[ii]=(long int)colarr[0];
				if ((*naxes)[ii]) {
	  	   if (((*cells)[ii]=(double*)calloc((size_t)(*naxes)[ii],sizeof(double)))==0) {
				  fprintf(stderr,"no free memory\n");
				  exit(1);
			   }
					memcpy((*cells)[ii],&colarr[1],sizeof(double)*((size_t)((*naxes)[ii])));
				}
			 }


#ifdef DEBUG
			 for (ii=0; ii<*naxis; ii++) {
				printf("axis %ld\n",ii);
	  		 for (jj=0; jj<(*naxes)[ii];jj++) 
		   			printf(" %lf, ",(*cells)[ii][jj]);
				 printf("\n");

			 }
#endif
			 fits_close_file(fptr,&status);


			 fits_report_error(stderr, status);

  		 free(mynaxes);

			 free(increment);
			 free(fpix);
			 free(lpix);

			 free(colarr);


			return 0;
}
