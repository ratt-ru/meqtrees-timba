//# FITSUtils.cc: Everything and anything related to FITS files
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

#include <MeqNodes/FITSUtils.h>
//global mutex
LOFAR::Thread::Mutex cfitsio_mutex;

//#define DEBUG
namespace Meq {

int zero_image_float(long totalrows, long offset, long firstrow, long nrows,
   int ncols, iteratorCol *cols, void *user_struct) {
    int ii, status = 0;

    /* declare counts static to preserve the values between calls */
		/* so it traverses the whole array */
		static char *charp;
		static short int *sintp;
		static long int *lintp;
		static float *fptr;
		static double *dptr;

		static double tmpval;
		static long int pt,d1,d2,d3,d4;
    static long int xmin;
		static long int ymin,xmax,ymax;

    nlims *arr_dims=(nlims*)user_struct;
		int datatype=arr_dims->datatype;
    /*for (ii=0;ii<arr_dims->naxis;ii++) {
			printf("%d %ld\n",ii,arr_dims->d[ii]);
		}*/


    /*--------------------------------------------------------*/
    /*  Initialization procedures: execute on the first call  */
    /*--------------------------------------------------------*/
    if (firstrow == 1)
    {
       if (ncols != 1)
           return(-1);  /* number of columns incorrect */
#ifdef DEBUG
    for (ii=0;ii<arr_dims->naxis;ii++) {
			printf("%d %ld\n",ii,arr_dims->d[ii]);
		}
#endif
       /* assign the input pointers to the appropriate arrays and null ptrs*/
    switch (datatype) {
			case TBYTE:
       charp= (char *)  fits_iter_get_array(&cols[0]);
			 break;
		  case TSHORT:
       sintp= (short int*)  fits_iter_get_array(&cols[0]);
       break;
			case TLONG:
       lintp= (long int*)  fits_iter_get_array(&cols[0]);
       break;
			case TFLOAT:
       fptr= (float *)  fits_iter_get_array(&cols[0]);
			 break;
			case TDOUBLE:
       dptr= (double *)  fits_iter_get_array(&cols[0]);
			 
		}
			 /* initialize the limits */
			 xmin=arr_dims->d[0];
			 xmax=-1;
			 ymin=arr_dims->d[1];
			 ymax=-1;
    }

    //printf("limit (%ld,%ld)---(%ld,%ld)\n",xmin,ymin,xmax,ymax); 
    /*--------------------------------------------*/
    /*  Main loop: process all the rows of data */
    /*--------------------------------------------*/

    /*  NOTE: 1st element of array is the null pixel value!  */
    /*  Loop from 1 to nrows, not 0 to nrows - 1.  */

    switch (datatype) {
			case TBYTE:
         for (ii = 1; ii <= nrows; ii++) {
			     //printf("arr =%f\n",counts[ii]);
           //counts[ii] = 1.;
			     tmpval=(double)charp[ii];
			     if (arr_dims->tol<=fabs(tmpval)) {
			       //printf("arr =%lf\n",tmpval);
				     /* calculate 4D coords */
				     pt=firstrow+ii-1;
				     //printf("coord point=%ld ",pt);
				     d4=pt/(arr_dims->d[0]*arr_dims->d[1]*arr_dims->d[2]);
				     pt-=(arr_dims->d[0]*arr_dims->d[1]*arr_dims->d[2])*d4;
				     d3=pt/(arr_dims->d[0]*arr_dims->d[1]);
				     pt-=(arr_dims->d[0]*arr_dims->d[1])*d3;
				     d2=pt/(arr_dims->d[0]);
				     pt-=(arr_dims->d[0])*d2;
				     d1=pt;
				     //printf("coords =(%ld,%ld,%ld,%ld)\n",d1,d2,d3,d4);
				     /* find current limit */
				     if (xmin>d1) {
						    xmin=d1;
				     }
				     if(xmax<d1) {
					      xmax=d1;
				     }
				     if (ymin>d2) {
						    ymin=d2;
				     }
				     if(ymax<d2) {
					      ymax=d2;
				     }
			
			    }

       }
			 break;

			case TSHORT:
         for (ii = 1; ii <= nrows; ii++) {
           //counts[ii] = 1.;
			     tmpval=(double)sintp[ii];
			     //printf("arr =%lf\n",tmpval);
			     if (arr_dims->tol<=fabs(tmpval)) {
			       //printf("arr =%lf\n",tmpval);
				     /* calculate 4D coords */
				     pt=firstrow+ii-1;
				     //printf("coord point=%ld ",pt);
				     d4=pt/(arr_dims->d[0]*arr_dims->d[1]*arr_dims->d[2]);
				     pt-=(arr_dims->d[0]*arr_dims->d[1]*arr_dims->d[2])*d4;
				     d3=pt/(arr_dims->d[0]*arr_dims->d[1]);
				     pt-=(arr_dims->d[0]*arr_dims->d[1])*d3;
				     d2=pt/(arr_dims->d[0]);
				     pt-=(arr_dims->d[0])*d2;
				     d1=pt;
				     //printf("coords =(%ld,%ld,%ld,%ld)\n",d1,d2,d3,d4);
				     /* find current limit */
				     if (xmin>d1) {
						    xmin=d1;
				     }
				     if(xmax<d1) {
					      xmax=d1;
				     }
				     if (ymin>d2) {
						    ymin=d2;
				     }
				     if(ymax<d2) {
					      ymax=d2;
				     }
			
			    }

       }
			 break;

			case TLONG:
         for (ii = 1; ii <= nrows; ii++) {
			     //printf("arr =%f\n",counts[ii]);
           //counts[ii] = 1.;
			     tmpval=(double)lintp[ii];
			     if (arr_dims->tol<=fabs(tmpval)) {
			       //printf("arr =%lf\n",tmpval);
				     /* calculate 4D coords */
				     pt=firstrow+ii-1;
				     //printf("coord point=%ld ",pt);
				     d4=pt/(arr_dims->d[0]*arr_dims->d[1]*arr_dims->d[2]);
				     pt-=(arr_dims->d[0]*arr_dims->d[1]*arr_dims->d[2])*d4;
				     d3=pt/(arr_dims->d[0]*arr_dims->d[1]);
				     pt-=(arr_dims->d[0]*arr_dims->d[1])*d3;
				     d2=pt/(arr_dims->d[0]);
				     pt-=(arr_dims->d[0])*d2;
				     d1=pt;
				     //printf("coords =(%ld,%ld,%ld,%ld)\n",d1,d2,d3,d4);
				     /* find current limit */
				     if (xmin>d1) {
						    xmin=d1;
				     }
				     if(xmax<d1) {
					      xmax=d1;
				     }
				     if (ymin>d2) {
						    ymin=d2;
				     }
				     if(ymax<d2) {
					      ymax=d2;
				     }
			
			    }

       }
			 break;

			case TFLOAT:
         for (ii = 1; ii <= nrows; ii++) {
			     //printf("arr =%f\n",counts[ii]);
           //counts[ii] = 1.;
			     tmpval=(double)fptr[ii];
			     if (arr_dims->tol<=fabs(tmpval)) {
			       //printf("arr =%lf\n",tmpval);
				     /* calculate 4D coords */
				     pt=firstrow+ii-1;
				     //printf("coord point=%ld ",pt);
				     d4=pt/(arr_dims->d[0]*arr_dims->d[1]*arr_dims->d[2]);
				     pt-=(arr_dims->d[0]*arr_dims->d[1]*arr_dims->d[2])*d4;
				     d3=pt/(arr_dims->d[0]*arr_dims->d[1]);
				     pt-=(arr_dims->d[0]*arr_dims->d[1])*d3;
				     d2=pt/(arr_dims->d[0]);
				     pt-=(arr_dims->d[0])*d2;
				     d1=pt;
				     //printf("coords =(%ld,%ld,%ld,%ld)\n",d1,d2,d3,d4);
				     /* find current limit */
				     if (xmin>d1) {
						    xmin=d1;
				     }
				     if(xmax<d1) {
					      xmax=d1;
				     }
				     if (ymin>d2) {
						    ymin=d2;
				     }
				     if(ymax<d2) {
					      ymax=d2;
				     }
			
			    }

       }
			 break;

			case TDOUBLE:
         for (ii = 1; ii <= nrows; ii++) {
			     //printf("arr =%f\n",counts[ii]);
           //counts[ii] = 1.;
			     tmpval=(double)dptr[ii];
			     if (arr_dims->tol<=fabs(tmpval)) {
			       //printf("arr =%lf\n",tmpval);
				     /* calculate 4D coords */
				     pt=firstrow+ii-1;
				     //printf("coord point=%ld ",pt);
				     d4=pt/(arr_dims->d[0]*arr_dims->d[1]*arr_dims->d[2]);
				     pt-=(arr_dims->d[0]*arr_dims->d[1]*arr_dims->d[2])*d4;
				     d3=pt/(arr_dims->d[0]*arr_dims->d[1]);
				     pt-=(arr_dims->d[0]*arr_dims->d[1])*d3;
				     d2=pt/(arr_dims->d[0]);
				     pt-=(arr_dims->d[0])*d2;
				     d1=pt;
				     //printf("coords =(%ld,%ld,%ld,%ld)\n",d1,d2,d3,d4);
				     /* find current limit */
				     if (xmin>d1) {
						    xmin=d1;
				     }
				     if(xmax<d1) {
					      xmax=d1;
				     }
				     if (ymin>d2) {
						    ymin=d2;
				     }
				     if(ymax<d2) {
					      ymax=d2;
				     }
			
			    }

       }
			 break;


		}
    //printf("cols =%d, starting row=%ld, nrows = %ld\n", ncols, firstrow, nrows);
    //printf("limit (%ld,%ld)---(%ld,%ld)\n",xmin,ymin,xmax,ymax); 
		/* set the current limit */
    arr_dims->lpix[0]=xmin;
    arr_dims->lpix[1]=ymin;
    arr_dims->lpix[2]=0;
    arr_dims->lpix[3]=0;
    arr_dims->hpix[0]=xmax;
    arr_dims->hpix[1]=ymax;
    arr_dims->hpix[2]=arr_dims->d[2]-1;
    arr_dims->hpix[3]=arr_dims->d[3]-1;
 
    return(0);  /* return successful status */

}

/* function to read min-max values of fits file */
int get_min_max(long totalrows, long offset, long firstrow, long nrows,
   int ncols, iteratorCol *cols, void *user_struct) {

		static double min_val;
		static double max_val;
		static double tmpval;
		int ii;

    drange *xylims=(drange *)user_struct;
		static char *charp;
		static short int *sintp;
		static long int *lintp;
		static float *fptr;
		static double *dptr;
	  int		datatype=xylims->datatype;


    if (firstrow == 1)
    {
       if (ncols != 1)
           return(-1);  /* number of columns incorrect */
       /* assign the input pointers to the appropriate arrays and null ptrs*/
    switch (datatype) {
			case TBYTE:
       charp= (char *)  fits_iter_get_array(&cols[0]);
			 break;
		  case TSHORT:
       sintp= (short int*)  fits_iter_get_array(&cols[0]);
       break;
			case TLONG:
       lintp= (long int*)  fits_iter_get_array(&cols[0]);
       break;
			case TFLOAT:
       fptr= (float *)  fits_iter_get_array(&cols[0]);
			 break;
			case TDOUBLE:
       dptr= (double *)  fits_iter_get_array(&cols[0]);
			 
		}

		min_val=1e6;
		max_val=-1e6;
    }

   switch (datatype) {
			case TBYTE:
        for (ii = 1; ii <= nrows; ii++) {
			    tmpval=(double)charp[ii];
		      if (min_val>tmpval) min_val=tmpval;
		      if (max_val<tmpval) max_val=tmpval;
        }
				break;
		  case TSHORT:
        for (ii = 1; ii <= nrows; ii++) {
			    tmpval=(double)sintp[ii];
					//printf("%lf==%d\n",tmpval,sintp[ii]);
		      if (min_val>tmpval) min_val=tmpval;
		      if (max_val<tmpval) max_val=tmpval;
        }
				break;
			case TLONG:
        for (ii = 1; ii <= nrows; ii++) {
			    tmpval=(double)lintp[ii];
		      if (min_val>tmpval) min_val=tmpval;
		      if (max_val<tmpval) max_val=tmpval;
        }
				break;
			case TFLOAT:
        for (ii = 1; ii <= nrows; ii++) {
			    tmpval=(double)fptr[ii];
		      if (min_val>tmpval) min_val=tmpval;
		      if (max_val<tmpval) max_val=tmpval;
        }
				break;
			case TDOUBLE:
        for (ii = 1; ii <= nrows; ii++) {
			    tmpval=(double)dptr[ii];
		      if (min_val>tmpval) min_val=tmpval;
		      if (max_val<tmpval) max_val=tmpval;
        }
				break;
	 }

		xylims->lims[0]=min_val;
		xylims->lims[1]=max_val;
#ifdef DEBUG
		//printf("min_max: min=%lf max=%lf\n",min_val,max_val);
#endif
		return 0;
}
 

/* filename: file name
 * cutoff: cutoff to truncate the image
 * myarr: 4D data array of truncated image
 * new_naxis: array of dimensions of each axis
 * lgrid: grid points in l axis
 * mgrid: grid points in m axis
 * lspace: spacing in l axis
 * mspace: spacing in m axis
 * ra0,dec0: coords of phase centre
 * mode: 1 (shift grid if even), 2: no shift
 */
int read_fits_file(const char *filename,double cutoff, double**myarr, long int *new_naxis, double **lgrid, double **mgrid, double **lspace, double **mspace, 
								double *ra0, double *dec0, double **fgrid, double **fspace, int mode) {
    /* lock mutex */
    Thread::Mutex::Lock lock(cfitsio_mutex);
    fitsfile *fptr;
    iteratorCol cols[3];  /* structure used by the iterator function */
    int n_cols;
    long rows_per_loop, offset;
		nlims arr_dims;
		drange arr_limits;
		//double arr_limits[2];

    int status;
		int naxis;
		int bitpix;

		int ii,nkeys,jj,kk;
		char card[81]; /*for keywords */
		int datatype=0;
		long int totalpix;
		double bscale,bzero;
		long int increment[4]={1,1,1,1};
		float *arr;
		int null_flag=0;


		/* stuctures from WCSLIB */
		struct wcsprm *wcs;
		char *header;
		int ncard,nreject,nwcs;
		//extern const char *wcshdr_errmsg[];
		int ncoord;
		double *pixelc, *imgc, *worldc, *phic, *thetac;
		int *statc;
		double phi0,theta0,l0,m0;

		int stat[NWCSFIX];

		
    status = 0; 
#ifdef DEBUG
    printf("File =%s\n",filename);
#endif
    fits_open_file(&fptr, filename, READWRITE, &status); /* open file */

/* WCSLIB et al. */
		/* read FITS header */
		if (status = fits_hdr2str(fptr, 1, NULL, 0, &header, &ncard, &status)) {
		 fits_report_error(stderr, status);
		 return 1;
		}

#ifdef DEBUG
		printf("header %s\n",header); 
#endif
/* Parse the primary header of the FITS file. */
    if (status = wcspih(header, ncard, WCSHDR_all, 2, &nreject, &nwcs, &wcs)) {
	      fprintf(stderr, "wcspih ERROR %d\n", status);
		}

		/* Fix non-standard WCS keyvalues. */
		if (status = wcsfix(7, 0, wcs, stat)) {
		  printf("wcsfix ERROR, status returns: (");
			  for (ii = 0; ii < NWCSFIX; ii++) {
					printf(ii ? ", %d" : "%d", stat[ii]);
				}
				printf(")\n\n");
	  }

		if (status = wcsset(wcs)) {
		  fprintf(stderr, "wcsset ERROR %d:\n", status);
		  return 1;
		}

	  /* Print the struct. */
#ifdef DEBUG
	  if (status = wcsprt(wcs)) return status;
#endif

    //read scaling parameters
    //fits_read_key(fptr, TDOUBLE, "BSCALE", &bscale_in, NULL, &status);
    //fits_read_key(fptr, TDOUBLE, "BZERO", &bzero_in, NULL, &status);
		//printf("Bscale=%lf Bzero=%lf\n",bscale_in,bzero_in);

		/* turn off scaling so that we copy the pixel values */
		bscale=1.0; bzero=0.0;
    fits_set_bscale(fptr,  bscale, bzero, &status);


		fits_get_img_dim(fptr, &naxis, &status);
		if ((arr_dims.d=(long int*)calloc((size_t)naxis,sizeof(long int)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
		if ((arr_dims.lpix=(long int*)calloc((size_t)naxis,sizeof(long int)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
		if ((arr_dims.hpix=(long int*)calloc((size_t)naxis,sizeof(long int)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
		/* get axis dimensions */
		fits_get_img_size(fptr, naxis, arr_dims.d, &status);
		arr_dims.naxis=naxis;
		arr_dims.tol=cutoff;
		/* get data type */
		fits_get_img_type(fptr, &bitpix, &status);
		if(bitpix==BYTE_IMG) {
#ifdef DEBUG
			printf("Type Bytes\n");
#endif
			datatype=TBYTE;
		}else if(bitpix==SHORT_IMG) {
#ifdef DEBUG
			printf("Type Short Int\n");
#endif
			datatype=TSHORT;
		}else if(bitpix==LONG_IMG) {
#ifdef DEBUG
			printf("Type Long Int\n");
#endif
			datatype=TLONG;
		}else if(bitpix==FLOAT_IMG) {
#ifdef DEBUG
			printf("Type Float\n");
#endif
			datatype=TFLOAT;
		}else if(bitpix==DOUBLE_IMG) {
#ifdef DEBUG
			printf("Type Double\n");
#endif
			datatype=TDOUBLE;
		}


    n_cols = 1;

    /* define input column structure members for the iterator function */
    fits_iter_set_file(&cols[0], fptr);
    fits_iter_set_iotype(&cols[0], InputOutputCol);
    fits_iter_set_datatype(&cols[0], 0);

    rows_per_loop = 0;  /* use default optimum number of rows */
    offset = 0;         /* process all the rows */


		/* determine limits of image data */
		arr_limits.datatype=datatype;
    fits_iterate_data(n_cols, cols, offset, rows_per_loop,
                      get_min_max, (void*)&arr_limits, &status);

#ifdef DEBUG
		printf("Limits Min %lf, Max %lf\n",arr_limits.lims[0],arr_limits.lims[1]);
#endif
		arr_dims.tol=(1-cutoff)*(arr_limits.lims[1]-arr_limits.lims[0])+arr_limits.lims[0];
		/* need to transfer this to real value in the FITS file */
		/* using the inverse scaling , zero */
#ifdef DEBUG
		printf("cutoff for %lfx100 %% is %lf\n",cutoff,arr_dims.tol);
#endif
    /* apply the rate function to each row of the table */
#ifdef DEBUG
    printf("Calling iterator function...%d\n", status);
#endif

		/* turn off scaling so that we copy the pixel values */
		//bscale=1.0; bzero=0.0;
    //fits_set_bscale(fptr,  bscale, bzero, &status);


    rows_per_loop = 0;  /* use default optimum number of rows */
    offset = 0;         /* process all the rows */
		arr_dims.datatype=datatype;
    fits_iterate_data(n_cols, cols, offset, rows_per_loop,
                      zero_image_float, (void*)&arr_dims, &status);

		/* print the limits of the hypercube */
		/* sanity check: if no good pixels are found, include whole
		 * image 
		 */
		if(arr_dims.lpix[0]==arr_dims.d[0] || arr_dims.lpix[1]==arr_dims.d[1]
			||arr_dims.hpix[0]==-1 || arr_dims.hpix[1]==-1) {
					printf("No pixels found\n");
     arr_dims.hpix[0]=arr_dims.d[0]-1;
     arr_dims.hpix[1]=arr_dims.d[1]-1;
     arr_dims.lpix[0]=arr_dims.lpix[1]=0;
		}
		/* correct the coordinates for 1 indexing */
     arr_dims.hpix[0]++;
     arr_dims.hpix[1]++;
     arr_dims.hpix[2]++;
     arr_dims.hpix[3]++;
     arr_dims.lpix[0]++;
     arr_dims.lpix[1]++;
     arr_dims.lpix[2]++;
     arr_dims.lpix[3]++;

#ifdef DEBUG
	  printf("(%ld %ld %ld %ld) ",arr_dims.lpix[0],
									arr_dims.lpix[1],	arr_dims.lpix[2], arr_dims.lpix[3]);
	  printf(" to (%ld %ld %ld %ld)\n",arr_dims.hpix[0],
									arr_dims.hpix[1],	arr_dims.hpix[2], arr_dims.hpix[3]);
#endif
	  /******* create new array **********/	
		new_naxis[0]=arr_dims.hpix[0]-arr_dims.lpix[0]+1;
		new_naxis[1]=arr_dims.hpix[1]-arr_dims.lpix[1]+1;
		new_naxis[2]=arr_dims.hpix[2]-arr_dims.lpix[2]+1;
		new_naxis[3]=arr_dims.hpix[3]-arr_dims.lpix[3]+1;
		/* calculate total number of pixels */
    totalpix=((arr_dims.hpix[0]-arr_dims.lpix[0]+1)
     *(arr_dims.hpix[1]-arr_dims.lpix[1]+1)
     *(arr_dims.hpix[2]-arr_dims.lpix[2]+1)
     *(arr_dims.hpix[3]-arr_dims.lpix[3]+1));

#ifdef DEBUG
		printf("selecting %ld pixels\n",totalpix);
#endif
		
		if ((*myarr=(double*)calloc((size_t)totalpix,sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}

		/* turn off scaling so that we copy the pixel values */
		//bscale=1.0; bzero=0.0;
    //fits_set_bscale(fptr,  bscale, bzero, &status);

		/* read the subset increment=[1,1,1,..]*/
		fits_read_subset(fptr, TDOUBLE, arr_dims.lpix, arr_dims.hpix, increment,
									 0, *myarr, &null_flag, &status);

    

		/* ******************BEGIN create grid for the cells using WCS */
#ifdef DEBUG
    printf("found axis %d\n",wcs->naxis);
#endif
		/* allocate memory for pixel/world coordinate arrays */
		ncoord=new_naxis[0]*new_naxis[1]*1*1; /* consider only one plane fron freq, and stokes axes because RA,Dec will not change */
  	if ((pixelc=(double*)calloc((size_t)ncoord*4,sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
  	if ((imgc=(double*)calloc((size_t)ncoord*4,sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
  	if ((worldc=(double*)calloc((size_t)ncoord*4,sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
		if ((phic=(double*)calloc((size_t)ncoord,sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
		if ((thetac=(double*)calloc((size_t)ncoord,sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
		if ((statc=(int*)calloc((size_t)ncoord,sizeof(int)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}

		/* fill up the pixel coordinate array */
    kk=0;
    for (ii=arr_dims.lpix[0];ii<=arr_dims.hpix[0];ii++)
     for (jj=arr_dims.lpix[1];jj<=arr_dims.hpix[1];jj++) {
						 pixelc[kk+0]=(double)ii;
						 pixelc[kk+1]=(double)jj;
						 pixelc[kk+2]=(double)1.0;
						 pixelc[kk+3]=(double)1.0;
						 kk+=4;
		 }
		/* now kk has passed the last pixel */
#ifdef DEBUG
		printf("total %d, created %d\n",ncoord,kk);
#endif
		if (status = wcsp2s(wcs, ncoord, wcs->naxis, pixelc, imgc, phic, thetac,
			 worldc, statc)) {
			 fprintf(stderr,"wcsp2s ERROR %2d\n", status);
			 /* Handle Invalid pixel coordinates. */
			 if (status == 8) status = 0;
	  }

		/* convert to radians */
		for (ii=0;ii<ncoord;ii++) {
				phic[ii]*=M_PI/180.0;
				thetac[ii]*=M_PI/180.0;
		}
		/* compare the results */
    /*kk=0;
    for (ii=arr_dims.lpix[0];ii<=arr_dims.hpix[0];ii++)
     for (jj=arr_dims.lpix[1];jj<=arr_dims.hpix[1];jj++) {
				printf("(%lf: %lf) : [%lf:%lf:%lf:%lf] : (%lf,%lf), [%lf:%lf:%lf:%lf] :: %d\n",pixelc[kk+0],pixelc[kk+1],
				imgc[kk+0],imgc[kk+1],imgc[kk+2],imgc[kk+3],phic[kk/4],thetac[kk/4],
				worldc[kk+0],worldc[kk+1],worldc[kk+2],worldc[kk+3],statc[kk/4]
				);
						 kk+=4;
		 } */ 

    /* find center coordinates, handle even numbers correctly */
		/* even, use the pixel to the right as the center */
		/* odd, use middle pixel */
		/* find corresponding kk value =(l_c-1)*M +m_c-1 */
		kk=4*((new_naxis[0]/2)*new_naxis[1]+(new_naxis[1]/2));

#ifdef DEBUG
		printf("found center %d\n",kk);
#endif
    /* find the phase centre in RA,Dec */
             if(mode==1) {
     /* normal grid: average min, max values */
     /* shifted grid : apply NO shift at all */
		*ra0=(worldc[kk])*M_PI/180.0;
		*dec0=(worldc[kk+1])*M_PI/180.0;
		l0=imgc[kk];
		m0=imgc[kk+1];
		//l0=m0=0.0;
             } else {
         /* dont really need ra and dec here */
         /* apply no shift and take header values as origin */
	       *ra0=(worldc[0]+worldc[4*(ncoord-1)])*M_PI/360.0;
	       *dec0=(worldc[1]+worldc[4*(ncoord-1)+1])*M_PI/360.0;
          l0=m0=0.0;
             }

#ifdef DEBUG
		printf("phase centre celestial=(%lf,%lf) native l,m=(%lf,%lf)\n",*ra0,*dec0,l0,m0);
#endif

		/* recreate the l,m grid using the RA,Dec grid with the new phase 
		 * centre -- just do a linear transform assuming shift is small
		 */


		/* now calculate new (l,m) values for the phi,theta values with the new phase centre */

	if ((*lgrid=(double*)calloc((size_t)new_naxis[0],sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
	if ((*mgrid=(double*)calloc((size_t)new_naxis[1],sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
	if ((*lspace=(double*)calloc((size_t)new_naxis[0],sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
	if ((*mspace=(double*)calloc((size_t)new_naxis[1],sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}

		for (ii=0;ii<new_naxis[0];ii++) {
					(*lgrid)[new_naxis[0]-ii-1]=(imgc[ii*4*new_naxis[1]]-l0)*M_PI/180.0;
		}
		/* different strides */
		for (ii=0;ii<new_naxis[1];ii++) {
					(*mgrid)[ii]=(imgc[ii*4+1]-m0)*M_PI/180.0;
		}
		/* calculate spacing */
		for (ii=1;ii<new_naxis[0];ii++) {
			(*lspace)[ii]=(*lgrid)[ii]-(*lgrid)[ii-1];
		}
    (*lspace)[0]=(*lspace)[new_naxis[0]-1];
		for (ii=1;ii<new_naxis[1];ii++) {
			(*mspace)[ii]=(*mgrid)[ii]-(*mgrid)[ii-1];
		}
    (*mspace)[0]=(*mspace)[new_naxis[1]-1];



		/***** determinig frequencies ********/
		if (ncoord<new_naxis[3]){ 
			ncoord=new_naxis[3];
      /* reallocate memory */
  	if ((pixelc=(double*)realloc((void*)pixelc,(size_t)ncoord*4*sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
  	if ((imgc=(double*)realloc((void*)imgc,(size_t)ncoord*4*sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
  	if ((worldc=(double*)realloc((void*)worldc,(size_t)ncoord*4*sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
		if ((phic=(double*)realloc((void*)phic,(size_t)ncoord*sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
		if ((thetac=(double*)realloc((void*)thetac,(size_t)ncoord*sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
		if ((statc=(int*)realloc((void*)statc,(size_t)ncoord*sizeof(int)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}

		}

    kk=0;
	  ncoord=new_naxis[3];
    for (ii=1;ii<=new_naxis[3];ii++) {
						 pixelc[kk+0]=(double)1; /* l */
						 pixelc[kk+1]=(double)1; /* m */
						 pixelc[kk+2]=(double)1.0; /* stokes */
						 pixelc[kk+3]=(double)ii-1.0; /* freq */
						 kk+=4;
		 }
		if (status = wcsp2s(wcs, ncoord, wcs->naxis, pixelc, imgc, phic, thetac,
			 worldc, statc)) {
			 fprintf(stderr,"wcsp2s ERROR %2d\n", status);
			 /* Handle Invalid pixel coordinates. */
			 if (status == 8) status = 0;
	  }

  	if ((*fgrid=(double*)calloc((size_t)new_naxis[3],sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
  	if ((*fspace=(double*)calloc((size_t)new_naxis[3],sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
 /*   kk=0;
    for (ii=1;ii<=new_naxis[3];ii++) {
				printf("(%lf: %lf) : [%lf:%lf:%lf:%lf] : (%lf,%lf), [%lf:%lf:%lf:%lf] :: %d\n",pixelc[kk+0],pixelc[kk+1],
				imgc[kk+0],imgc[kk+1],imgc[kk+2],imgc[kk+3],phic[kk/4],thetac[kk/4],
				worldc[kk+0],worldc[kk+1],worldc[kk+2],worldc[kk+3],statc[kk/4]
				);
						 kk+=4;
		 } */

    kk=0;
		for (ii=0;ii<new_naxis[3];ii++) {
					(*fgrid)[ii]= worldc[kk+3];
					kk+=4;
		}
		for (ii=1;ii<new_naxis[3];ii++) {
					(*fspace)[ii]=(*fgrid)[ii]- (*fgrid)[ii-1];
		}
		if (new_naxis[3]>1) {
      (*fspace)[0]=(*fspace)[1];
		} else {
      (*fspace)[0]=1.0;
		}
		/*************************************/


		/* ******************END create grid for the cells using WCS */
    fits_close_file(fptr, &status);      /* all done */

    if (status) 
        fits_report_error(stderr, status);  /* print out error messages */

		free(arr_dims.d);
		free(arr_dims.lpix);
		free(arr_dims.hpix);
		wcsfree(wcs);
    free(wcs);
		free(header);
		
/*		for (ii=0; ii<ncoord;ii++) {
			free(pixelc[ii]);
			free(imgc[ii]);
			free(worldc[ii]);
		} */
		free(pixelc);
		free(imgc);
		free(worldc);
		free(phic);
		free(thetac);
		free(statc);

    return(status);
}


int simple_read_fits_file(const char *filename,  double **arr,  double ***cells,
			long int *naxis, long int **naxes, int *is_complex) {

       /* lock mutex */
       Thread::Mutex::Lock lock(cfitsio_mutex);

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
			 int mynaxis=0;
			 double *colarr=0;
			 int has_cells;



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
			 fits_read_subset(fptr, TDOUBLE, fpix, lpix, increment,
													    0, *arr, &null_flag, &status);

#ifdef DEBUG
			 for (ii=0;ii<nelements;ii++) {
					printf("%ld: %lf ",ii,(*arr)[ii]);
			 }
			 printf("\n");
#endif
			 /* read the hader key to see if data is complex */
			 fits_read_key(fptr,TINT,"CPLEX",is_complex,NULL,&status);
			 if (status==KEY_NO_EXIST) {
					*is_complex=0;
					status=0;
			 }


			 /* read the hader key to see if cells are present */
			 fits_read_key(fptr,TINT,"CELLS",&has_cells,NULL,&status);
			 if (status==KEY_NO_EXIST) {
					/* no cells ! */
					has_cells=0;
					status=0;
			 }
#ifdef DEBUG
			 printf("cells present=%d\n",has_cells);
#endif

			 if (has_cells) {
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

#ifdef DEBUG
   for (jj=0; jj<nrows; jj++) {
		 printf("##%lf, ",colarr[jj]);
   }
#endif
				(*naxes)[ii]=(long int)colarr[0];
				if ((*naxes)[ii]) {
	  	   if (((*cells)[ii]=(double*)calloc((size_t)(*naxes)[ii],sizeof(double)))==0) {
				  fprintf(stderr,"no free memory\n");
				  exit(1);
			   }
					memcpy((*cells)[ii],&colarr[1],sizeof(double)*((size_t)((*naxes)[ii])));
         /* since we have only stored the abs value of first point
            and the offsets of others, calculate absolute values : DONT*/
       /* for (jj=1; jj<(*naxes)[ii]; jj++) {
          (*cells)[ii][jj]+=(*cells)[ii][0];
        } */
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

			 } else {
				/* no cells present, could be a scalar */
				/* *naxis=0; */
				/* but try to parse header keywords */
				fits_read_key(fptr, TLONG,"NAXIS",naxis,0,&status);
				*naxis=*naxis+2;
				/* time and freq are 0, 1 */
			  if ((*naxes=(long int*)calloc((size_t)(*naxis),sizeof(long int)))==0) {
			    fprintf(stderr,"no free memory\n");
				  exit(1);
			  }
				(*naxes)[0]=(*naxes)[1]=0; /* no t,f dependence */
				fits_read_key(fptr, TLONG,"NAXIS1",&((*naxes)[2]),0,&status);
				fits_read_key(fptr, TLONG,"NAXIS2",&((*naxes)[3]),0,&status);
				/* determine the grid */
        /* cells of each axes (centers) */
	  	  if ((*cells=(double**)calloc((size_t)(*naxis),sizeof(double*)))==0) {
			  	fprintf(stderr,"no free memory\n");
			  	exit(1);
			  }
				for (ii=0; ii<*naxis; ii++) {
				if ((*naxes)[ii]) {
	  	   if (((*cells)[ii]=(double*)calloc((size_t)((*naxes)[ii]),sizeof(double)))==0) {
				  fprintf(stderr,"no free memory\n");
				  exit(1);
			   }
				}
				}
        double cdelt,crpix; 
				fits_read_key(fptr, TDOUBLE,"CDELT1",&cdelt,0,&status);
				fits_read_key(fptr, TDOUBLE,"CRPIX1",&crpix,0,&status);
				/* axis 1 */
				for (ii=0; ii<(*naxes)[2]; ii++) {
         (*cells)[2][ii]=(ii+1-crpix)*cdelt;
				}
				fits_read_key(fptr, TDOUBLE,"CDELT2",&cdelt,0,&status);
				fits_read_key(fptr, TDOUBLE,"CRPIX2",&crpix,0,&status);
				/* axis 1 */
				for (ii=0; ii<(*naxes)[3]; ii++) {
         (*cells)[3][ii]=(ii+1-crpix)*cdelt;
				}

			 }
			 fits_close_file(fptr,&status);


			 fits_report_error(stderr, status);

  		 free(mynaxes);

			 free(increment);
			 free(fpix);
			 free(lpix);

			 if (has_cells) 
			  free(colarr);


			return 0;
}


int write_fits_file(const char *filename,  double **arr,  int nvells, double **cells,
			long int naxis, long int *naxes, int is_complex) {

    Thread::Mutex::Lock lock(cfitsio_mutex);
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
       double refpix, *refval, *refdel;
       char *keyname, *keycomm;
       int keycommlen=128;
       int keynamelen=20;

 
#ifdef DEBUG
			 printf("axis =%ld vells=%d\n",naxis,nvells);
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
			 if ((refval=(double*)calloc((size_t)totaxs,sizeof(double)))==0) {
					fprintf(stderr,"no free memory\n");
					exit(1);
			 }
			 if ((refdel=(double*)calloc((size_t)totaxs,sizeof(double)))==0) {
					fprintf(stderr,"no free memory\n");
					exit(1);
			 }
			 jj=0;
			 for (ii=0; ii<naxis; ii++) {
			  if (naxes[ii] && jj<totaxs) {
					real_naxes[jj]=naxes[ii];
          if (cells) {
           refval[jj]=(cells[ii][0])*180/M_PI;
           if (real_naxes[jj] >1) {
            refdel[jj++]=(cells[ii][1]-cells[ii][0])*180/M_PI;
           } else {
            refdel[jj++]=1;
           }
          } else {
           refval[jj]=0;
           refdel[jj++]=1;
          }
				}
			 }

#ifdef DEBUG
			 printf("found %ld real axes\n",totaxs);
			 for (ii=0; ii<totaxs; ii++) {
					printf("%ld: %ld ",ii,real_naxes[ii]);
			 }
			 printf("\n");
#endif

			 status=0;
			 
			 fits_create_file(&outfptr,filename,&status);

			 if (cells) { /* has cells */
        has_cells=1;
       }

       /* reference pixel value */
       refpix=0;
  		 /* allocate memory for keywords and comments */
			 if ((keyname=(char*)calloc((size_t)keynamelen,sizeof(char)))==0) {
					fprintf(stderr,"no free memory\n");
					exit(1);
			 }
  		 if ((keycomm=(char*)calloc((size_t)keycommlen,sizeof(char)))==0) {
					fprintf(stderr,"no free memory\n");
					exit(1);
			 }
   
       /* write all vellsets */
       if (!is_complex) {
        for (ii=0; ii<nvells; ii++) {
			   fits_create_img(outfptr,DOUBLE_IMG,totaxs,real_naxes,&status);
			   fits_write_img(outfptr,TDOUBLE,fpixel,nelements,arr[ii],&status);
			   /* write key to indicate complex or not */
			   fits_update_key(outfptr, TINT, "CPLEX", &is_complex,"Complex data 1: yes 0: no", &status);
         if (cells) { /* has cells */
			     /* write a keyword to indicate the presence of cells */
			     fits_update_key(outfptr, TINT, "CELLS", &has_cells,"Has Cells 1: yes 0: no", &status);
         }
         for (jj=0; jj<totaxs; jj++) {
          snprintf(keyname,keynamelen,"CTYPE%ld",jj+1);
          snprintf(keycomm,keycommlen,"Ax %ld of %ld",jj+1,ii);
          fits_update_key(outfptr, TSTRING, keyname,keycomm,0,&status);
          snprintf(keyname,keynamelen,"CRPIX%ld",jj+1);
          fits_update_key(outfptr, TDOUBLE, keyname,&refpix,0,&status);
          snprintf(keyname,keynamelen,"CRVAL%ld",jj+1);
          fits_update_key(outfptr, TDOUBLE, keyname,&refval[jj],0,&status);
          snprintf(keyname,keynamelen,"CDELT%ld",jj+1);
          fits_update_key(outfptr, TDOUBLE, keyname,&refdel[jj],0,&status);
          snprintf(keyname,keynamelen,"CUNIT%ld",jj+1);
          snprintf(keycomm,keycommlen,"deg");
          fits_update_key(outfptr, TSTRING, keyname,keycomm,0,&status);
         }
        }
       } else { /* complex data */
        for (ii=0; ii<nvells*2; ii++) {
			   fits_create_img(outfptr,DOUBLE_IMG,totaxs,real_naxes,&status);
			   fits_write_img(outfptr,TDOUBLE,fpixel,nelements,arr[ii],&status);
			   /* write key to indicate complex or not */
			   fits_update_key(outfptr, TINT, "CPLEX", &is_complex,"Complex data 1: yes 0: no", &status);
         if (cells) { /* has cells */
			     /* write a keyword to indicate the presence of cells */
			     fits_update_key(outfptr, TINT, "CELLS", &has_cells,"Has Cells 1: yes 0: no", &status);
         }
         for (jj=0; jj<totaxs; jj++) {
          snprintf(keyname,keynamelen,"CTYPE%ld",jj+1);
          snprintf(keycomm,keycommlen,"Ax %ld of %ld",jj+1,ii);
          fits_update_key(outfptr, TSTRING, keyname,keycomm,0,&status);
          snprintf(keyname,keynamelen,"CRPIX%ld",jj+1);
          fits_update_key(outfptr, TDOUBLE, keyname,&refpix,0,&status);
          snprintf(keyname,keynamelen,"CRVAL%ld",jj+1);
          fits_update_key(outfptr, TDOUBLE, keyname,&refval[jj],0,&status);
          snprintf(keyname,keynamelen,"CDELT%ld",jj+1);
          fits_update_key(outfptr, TDOUBLE, keyname,&refdel[jj],0,&status);
          snprintf(keyname,keynamelen,"CUNIT%ld",jj+1);
          snprintf(keycomm,keycommlen,"deg");
          fits_update_key(outfptr, TSTRING, keyname,keycomm,0,&status);
         }
        }
       }

			 if (cells) { /* has cells */
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
				 sprintf(tform[ii],"1D");
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
       free(refval);
       free(refdel);
       free(keyname);
       free(keycomm);
			return 0;
}


/* filename: file name
 * cutoff: cutoff to truncate the image
 * myarr: 4D data array of truncated image
 * new_naxis: array of dimensions of each axis
 * lgrid: grid points in l axis
 * mgrid: grid points in m axis
 * lspace: spacing in l axis
 * mspace: spacing in m axis
 * ra0,dec0: coords of phase centre
 */
int mux_read_fits_file(const char *filename,double cutoff, double**myarr, long int *new_naxis, double **lgrid, double **mgrid, double **lspace, double **mspace, 
								double *ra0, double *dec0, double **fgrid, double **fspace, io_buff *fbuff) {

    Thread::Mutex::Lock lock(cfitsio_mutex);
    iteratorCol cols[3];  /* structure used by the iterator function */
    int n_cols;
    long rows_per_loop, offset;
		drange arr_limits;
		//double arr_limits[2];

    int status;
		int naxis;
		int bitpix;

		int ii,nkeys,jj,kk;
		char card[81]; /*for keywords */
		int datatype=0;
		long int totalpix;
		double bscale,bzero;
		long int increment[4]={1,1,1,1};
		float *arr;
		int null_flag=0;

		/* stuctures from WCSLIB */
		char *header;
		int ncard,nreject,nwcs;
		//extern const char *wcshdr_errmsg[];
		int ncoord;
		double *pixelc, *imgc, *worldc, *phic, *thetac;
		int *statc;
		double phi0,theta0,l0,m0;

		int stat[NWCSFIX];

		
    status = 0; 
#ifdef DEBUG
    printf("File =%s\n",filename);
#endif
    fits_open_file(&fbuff->fptr, filename, READWRITE, &status); /* open file */

/* WCSLIB et al. */
		/* read FITS header */
		if (status = fits_hdr2str(fbuff->fptr, 1, NULL, 0, &header, &ncard, &status)) {
		 fits_report_error(stderr, status);
		 return 1;
		}

#ifdef DEBUG
		printf("header %s\n",header); 
#endif
/* Parse the primary header of the FITS file. */
    if (status = wcspih(header, ncard, WCSHDR_all, 2, &nreject, &nwcs, &fbuff->wcs)) {
	      fprintf(stderr, "wcspih ERROR %d\n", status);
		}

		/* Fix non-standard WCS keyvalues. */
		if (status = wcsfix(7, 0, fbuff->wcs, stat)) {
		  printf("wcsfix ERROR, status returns: (");
			  for (ii = 0; ii < NWCSFIX; ii++) {
					printf(ii ? ", %d" : "%d", stat[ii]);
				}
				printf(")\n\n");
	  }

		if (status = wcsset(fbuff->wcs)) {
		  fprintf(stderr, "wcsset ERROR %d:\n", status);
		  return 1;
		}

	  /* Print the struct. */
#ifdef DEBUG
	  if (status = wcsprt(fbuff->wcs)) return status;
#endif


		/* turn off scaling so that we copy the pixel values */
		bscale=1.0; bzero=0.0;
    fits_set_bscale(fbuff->fptr,  bscale, bzero, &status);


		fits_get_img_dim(fbuff->fptr, &naxis, &status);
		if ((fbuff->arr_dims.d=(long int*)calloc((size_t)naxis,sizeof(long int)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
		if ((fbuff->arr_dims.lpix=(long int*)calloc((size_t)naxis,sizeof(long int)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
		if ((fbuff->arr_dims.hpix=(long int*)calloc((size_t)naxis,sizeof(long int)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
		/* get axis dimensions */
		fits_get_img_size(fbuff->fptr, naxis, fbuff->arr_dims.d, &status);
		fbuff->arr_dims.naxis=naxis;
		fbuff->arr_dims.tol=cutoff;
		/* get data type */
		fits_get_img_type(fbuff->fptr, &bitpix, &status);
		if(bitpix==BYTE_IMG) {
#ifdef DEBUG
			printf("Type Bytes\n");
#endif
			datatype=TBYTE;
		}else if(bitpix==SHORT_IMG) {
#ifdef DEBUG
			printf("Type Short Int\n");
#endif
			datatype=TSHORT;
		}else if(bitpix==LONG_IMG) {
#ifdef DEBUG
			printf("Type Long Int\n");
#endif
			datatype=TLONG;
		}else if(bitpix==FLOAT_IMG) {
#ifdef DEBUG
			printf("Type Float\n");
#endif
			datatype=TFLOAT;
		}else if(bitpix==DOUBLE_IMG) {
#ifdef DEBUG
			printf("Type Double\n");
#endif
			datatype=TDOUBLE;
		}


    n_cols = 1;

    /* define input column structure members for the iterator function */
    fits_iter_set_file(&cols[0], fbuff->fptr);
    fits_iter_set_iotype(&cols[0], InputOutputCol);
    fits_iter_set_datatype(&cols[0], 0);

    rows_per_loop = 0;  /* use default optimum number of rows */
    offset = 0;         /* process all the rows */


		/* determine limits of image data */
		arr_limits.datatype=datatype;
    fits_iterate_data(n_cols, cols, offset, rows_per_loop,
                      get_min_max, (void*)&arr_limits, &status);

#ifdef DEBUG
		printf("Limits Min %lf, Max %lf\n",arr_limits.lims[0],arr_limits.lims[1]);
#endif
		fbuff->arr_dims.tol=(1-cutoff)*(arr_limits.lims[1]-arr_limits.lims[0])+arr_limits.lims[0];
		/* need to transfer this to real value in the FITS file */
		/* using the inverse scaling , zero */
#ifdef DEBUG
		printf("cutoff for %lfx100 %% is %lf\n",cutoff,fbuff->arr_dims.tol);
#endif
    /* apply the rate function to each row of the table */
#ifdef DEBUG
    printf("Calling iterator function...%d\n", status);
#endif


    rows_per_loop = 0;  /* use default optimum number of rows */
    offset = 0;         /* process all the rows */
		fbuff->arr_dims.datatype=datatype;
    fits_iterate_data(n_cols, cols, offset, rows_per_loop,
                      zero_image_float, (void*)&fbuff->arr_dims, &status);

		/* print the limits of the hypercube */
		/* sanity check: if no good pixels are found, include whole
		 * image 
		 */
		if(fbuff->arr_dims.lpix[0]==fbuff->arr_dims.d[0] || fbuff->arr_dims.lpix[1]==fbuff->arr_dims.d[1]
			||fbuff->arr_dims.hpix[0]==-1 || fbuff->arr_dims.hpix[1]==-1) {
					printf("No pixels found\n");
     fbuff->arr_dims.hpix[0]=fbuff->arr_dims.d[0]-1;
     fbuff->arr_dims.hpix[1]=fbuff->arr_dims.d[1]-1;
     fbuff->arr_dims.lpix[0]=fbuff->arr_dims.lpix[1]=0;
		}
		/* correct the coordinates for 1 indexing */
     fbuff->arr_dims.hpix[0]++;
     fbuff->arr_dims.hpix[1]++;
     fbuff->arr_dims.hpix[2]++;
     fbuff->arr_dims.hpix[3]++;
     fbuff->arr_dims.lpix[0]++;
     fbuff->arr_dims.lpix[1]++;
     fbuff->arr_dims.lpix[2]++;
     fbuff->arr_dims.lpix[3]++;

#ifdef DEBUG
	  printf("(%ld %ld %ld %ld) ",fbuff->arr_dims.lpix[0],
									fbuff->arr_dims.lpix[1],	fbuff->arr_dims.lpix[2], fbuff->arr_dims.lpix[3]);
	  printf(" to (%ld %ld %ld %ld)\n",fbuff->arr_dims.hpix[0],
									fbuff->arr_dims.hpix[1],	fbuff->arr_dims.hpix[2], fbuff->arr_dims.hpix[3]);
#endif
	  /******* create new array **********/	
		new_naxis[0]=fbuff->arr_dims.hpix[0]-fbuff->arr_dims.lpix[0]+1;
		new_naxis[1]=fbuff->arr_dims.hpix[1]-fbuff->arr_dims.lpix[1]+1;
		new_naxis[2]=fbuff->arr_dims.hpix[2]-fbuff->arr_dims.lpix[2]+1;
		new_naxis[3]=fbuff->arr_dims.hpix[3]-fbuff->arr_dims.lpix[3]+1;
		/* calculate total number of pixels */
    totalpix=((fbuff->arr_dims.hpix[0]-fbuff->arr_dims.lpix[0]+1)
     *(fbuff->arr_dims.hpix[1]-fbuff->arr_dims.lpix[1]+1)
     *(fbuff->arr_dims.hpix[2]-fbuff->arr_dims.lpix[2]+1)
     *(fbuff->arr_dims.hpix[3]-fbuff->arr_dims.lpix[3]+1));

#ifdef DEBUG
		printf("selecting %ld pixels\n",totalpix);
#endif
		
		if ((*myarr=(double*)calloc((size_t)totalpix,sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}


		/* read the subset increment=[1,1,1,..]*/
		fits_read_subset(fbuff->fptr, TDOUBLE, fbuff->arr_dims.lpix, fbuff->arr_dims.hpix, increment,
									 0, *myarr, &null_flag, &status);

    

		/* ******************BEGIN create grid for the cells using WCS */
#ifdef DEBUG
    printf("found axis %d\n",fbuff->wcs->naxis);
#endif
		/* allocate memory for pixel/world coordinate arrays */
		ncoord=new_naxis[0]*new_naxis[1]*1*1; /* consider only one plane fron freq, and stokes axes because RA,Dec will not change */
  	if ((pixelc=(double*)calloc((size_t)ncoord*4,sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
  	if ((imgc=(double*)calloc((size_t)ncoord*4,sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
  	if ((worldc=(double*)calloc((size_t)ncoord*4,sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
		if ((phic=(double*)calloc((size_t)ncoord,sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
		if ((thetac=(double*)calloc((size_t)ncoord,sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
		if ((statc=(int*)calloc((size_t)ncoord,sizeof(int)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}

		/* fill up the pixel coordinate array */
    kk=0;
    for (ii=fbuff->arr_dims.lpix[0];ii<=fbuff->arr_dims.hpix[0];ii++)
     for (jj=fbuff->arr_dims.lpix[1];jj<=fbuff->arr_dims.hpix[1];jj++) {
						 pixelc[kk+0]=(double)ii;
						 pixelc[kk+1]=(double)jj;
						 pixelc[kk+2]=(double)1.0;
						 pixelc[kk+3]=(double)1.0;
						 kk+=4;
		 }
		/* now kk has passed the last pixel */
#ifdef DEBUG
		printf("total %d, created %d\n",ncoord,kk);
#endif
		if (status = wcsp2s(fbuff->wcs, ncoord, fbuff->wcs->naxis, pixelc, imgc, phic, thetac,
			 worldc, statc)) {
			 fprintf(stderr,"wcsp2s ERROR %2d\n", status);
			 /* Handle Invalid pixel coordinates. */
			 if (status == 8) status = 0;
	  }

		/* convert to radians */
		for (ii=0;ii<ncoord;ii++) {
				phic[ii]*=M_PI/180.0;
				thetac[ii]*=M_PI/180.0;
		}
		/* compare the results */
    /*kk=0;
    for (ii=fbuff->arr_dims.lpix[0];ii<=fbuff->arr_dims.hpix[0];ii++)
     for (jj=fbuff->arr_dims.lpix[1];jj<=fbuff->arr_dims.hpix[1];jj++) {
				printf("(%lf: %lf) : [%lf:%lf:%lf:%lf] : (%lf,%lf), [%lf:%lf:%lf:%lf] :: %d\n",pixelc[kk+0],pixelc[kk+1],
				imgc[kk+0],imgc[kk+1],imgc[kk+2],imgc[kk+3],phic[kk/4],thetac[kk/4],
				worldc[kk+0],worldc[kk+1],worldc[kk+2],worldc[kk+3],statc[kk/4]
				);
						 kk+=4;
		 } */ 

    /* find center coordinates, handle even numbers correctly */
		/* even, use the pixel to the right as the center */
		/* odd, use middle pixel */
		/* find corresponding kk value =(l_c-1)*M +m_c-1 */
		kk=4*((new_naxis[0]/2)*new_naxis[1]+(new_naxis[1]/2));

#ifdef DEBUG
		printf("found center %d\n",kk);
#endif
    /* find the phase centre in RA,Dec */
		*ra0=(worldc[kk])*M_PI/180.0;
		*dec0=(worldc[kk+1])*M_PI/180.0;
		l0=imgc[kk];
		m0=imgc[kk+1];

#ifdef DEBUG
		printf("phase centre celestial=(%lf,%lf) native l,m=(%lf,%lf)\n",*ra0,*dec0,l0,m0);
#endif

		/* recreate the l,m grid using the RA,Dec grid with the new phase 
		 * centre -- just do a linear transform assuming shift is small
		 */


		/* now calculate new (l,m) values for the phi,theta values with the new phase centre */

	if ((*lgrid=(double*)calloc((size_t)new_naxis[0],sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
	if ((*mgrid=(double*)calloc((size_t)new_naxis[1],sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
	if ((*lspace=(double*)calloc((size_t)new_naxis[0],sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
	if ((*mspace=(double*)calloc((size_t)new_naxis[1],sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}

		for (ii=0;ii<new_naxis[0];ii++) {
					(*lgrid)[new_naxis[0]-ii-1]=(imgc[ii*4*new_naxis[1]]-l0)*M_PI/180.0;
		}
		/* different strides */
		for (ii=0;ii<new_naxis[1];ii++) {
					(*mgrid)[ii]=(imgc[ii*4+1]-m0)*M_PI/180.0;
		}
		/* calculate spacing */
		for (ii=1;ii<new_naxis[0];ii++) {
			(*lspace)[ii]=(*lgrid)[ii]-(*lgrid)[ii-1];
		}
    (*lspace)[0]=(*lspace)[new_naxis[0]-1];
		for (ii=1;ii<new_naxis[1];ii++) {
			(*mspace)[ii]=(*mgrid)[ii]-(*mgrid)[ii-1];
		}
    (*mspace)[0]=(*mspace)[new_naxis[1]-1];



		/***** determinig frequencies ********/
		if (ncoord<new_naxis[3]){ 
			ncoord=new_naxis[3];
      /* reallocate memory */
  	if ((pixelc=(double*)realloc((void*)pixelc,(size_t)ncoord*4*sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
  	if ((imgc=(double*)realloc((void*)imgc,(size_t)ncoord*4*sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
  	if ((worldc=(double*)realloc((void*)worldc,(size_t)ncoord*4*sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
		if ((phic=(double*)realloc((void*)phic,(size_t)ncoord*sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
		if ((thetac=(double*)realloc((void*)thetac,(size_t)ncoord*sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
		if ((statc=(int*)realloc((void*)statc,(size_t)ncoord*sizeof(int)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}

		}

    kk=0;
	  ncoord=new_naxis[3];
    for (ii=1;ii<=new_naxis[3];ii++) {
						 pixelc[kk+0]=(double)1; /* l */
						 pixelc[kk+1]=(double)1; /* m */
						 pixelc[kk+2]=(double)1.0; /* stokes */
						 pixelc[kk+3]=(double)ii; /* freq */
						 kk+=4;
		 }
		if (status = wcsp2s(fbuff->wcs, ncoord, fbuff->wcs->naxis, pixelc, imgc, phic, thetac,
			 worldc, statc)) {
			 fprintf(stderr,"wcsp2s ERROR %2d\n", status);
			 /* Handle Invalid pixel coordinates. */
			 if (status == 8) status = 0;
	  }

  	if ((*fgrid=(double*)calloc((size_t)new_naxis[3],sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
  	if ((*fspace=(double*)calloc((size_t)new_naxis[3],sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}
 /*   kk=0;
    for (ii=1;ii<=new_naxis[3];ii++) {
				printf("(%lf: %lf) : [%lf:%lf:%lf:%lf] : (%lf,%lf), [%lf:%lf:%lf:%lf] :: %d\n",pixelc[kk+0],pixelc[kk+1],
				imgc[kk+0],imgc[kk+1],imgc[kk+2],imgc[kk+3],phic[kk/4],thetac[kk/4],
				worldc[kk+0],worldc[kk+1],worldc[kk+2],worldc[kk+3],statc[kk/4]
				);
						 kk+=4;
		 } */

    kk=0;
		for (ii=0;ii<new_naxis[3];ii++) {
					(*fgrid)[ii]= worldc[kk+3];
					kk+=4;
		}
		for (ii=1;ii<new_naxis[3];ii++) {
					(*fspace)[ii]=(*fgrid)[ii]- (*fgrid)[ii-1];
		}
		if (new_naxis[3]>1) {
      (*fspace)[0]=(*fspace)[1];
		} else {
      (*fspace)[0]=1.0;
		}
		/*************************************/


    if (status) 
        fits_report_error(stderr, status);  /* print out error messages */

		free(header);
		
		free(pixelc);
		free(imgc);
		free(worldc);
		free(phic);
		free(thetac);
		free(statc);

    return(status);
}

int mux_write_fits_file(double *myarr, io_buff fbuff) {

   Thread::Mutex::Lock lock(cfitsio_mutex);
   int status=0;
	 long int totalpix;
	 float *arr;
	 long int ii;
   /* normally the image is stored as FLOAT
		* so do the type conversion
		*/
	 /*
	 if (fbuff.arr_dims.datatype==TFLOAT) {

    totalpix=((fbuff.arr_dims.hpix[0]-fbuff.arr_dims.lpix[0]+1)
     *(fbuff.arr_dims.hpix[1]-fbuff.arr_dims.lpix[1]+1)
     *(fbuff.arr_dims.hpix[2]-fbuff.arr_dims.lpix[2]+1)
     *(fbuff.arr_dims.hpix[3]-fbuff.arr_dims.lpix[3]+1));

#ifdef DEBUG
		printf("writing %ld pixels\n",totalpix);
#endif
		
		 if ((arr=(float*)calloc((size_t)totalpix,sizeof(float)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		 }
		 for (ii=0; ii<totalpix; ii++) {
			arr[ii]=(float)myarr[ii];
		 }
		 fits_write_subset(fbuff.fptr, fbuff.arr_dims.datatype, fbuff.arr_dims.lpix, fbuff.arr_dims.hpix, arr, &status);
		 free(arr);
	 } else if (fbuff.arr_dims.datatype==TDOUBLE) {
		fits_write_subset(fbuff.fptr, fbuff.arr_dims.datatype, fbuff.arr_dims.lpix, fbuff.arr_dims.hpix, myarr, &status);
	 } else {
		fprintf(stderr,"unsupported data type in FITS file\n");
	 } */

		fits_write_subset(fbuff.fptr, TDOUBLE, fbuff.arr_dims.lpix, fbuff.arr_dims.hpix, myarr, &status);



    fits_close_file(fbuff.fptr, &status);      /* all done */

    if (status) 
        fits_report_error(stderr, status);  /* print out error messages */

		free(fbuff.arr_dims.d);
		free(fbuff.arr_dims.lpix);
		free(fbuff.arr_dims.hpix);
		wcsfree(fbuff.wcs);
    free(fbuff.wcs);
	
		return(status);
}

} /* namespace Meq */
