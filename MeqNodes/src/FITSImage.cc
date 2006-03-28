//# FITSImage.cc: Read a FITS file and convert the Image HDU to  Vellsets
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

#include <MeqNodes/FITSImage.h>
#include <MEQ/MeqVocabulary.h>
#include <MEQ/Request.h>
#include <MEQ/Result.h>
#include <MEQ/VellsSlicer.h>
#include <MEQ/AID-Meq.h>
#include <MeqNodes/AID-MeqNodes.h>

extern "C" {
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* the following is w.r.t. /aips++/prod/code/casa */
#include  <../../../cfitsio/fitsio.h>
#include <wcslib/wcs.h>
#include <wcslib/prj.h>
#include <wcslib/wcshdr.h>
#include <wcslib/wcsfix.h>

typedef struct nlimits_ {
		int naxis;
		long int *d;
		long int *lpix;
		long int *hpix;
		double tol;
} nlims; /* struct to store array dimensions */
int zero_image_float(long totalrows, long offset, long firstrow, long nrows,
   int ncols, iteratorCol *cols, void *user_struct);
int get_min_max(long totalrows, long offset, long firstrow, long nrows,
   int ncols, iteratorCol *cols, void *user_struct);
int read_fits_file(const char *infilename, double cutoff, double **myarr, long int *naxis, double **lgrid, double **mgrid, double **lspace, double **mspace,
								double *ra0, double *dec0);

}/* extern C */

namespace Meq {

const HIID FFilename= AidFilename;
const HIID FCutoff= AidCutoff;


//##ModelId=400E5355029C
FITSImage::FITSImage()
	: Node(0),cutoff_(0.1)
{

	//create 4 axes -- Freq is already present
	Axis::addAxis("R"); //RA
	Axis::addAxis("D"); //Dec
	Axis::addAxis("S"); //Stokes
}

//##ModelId=400E5355029D
FITSImage::~FITSImage()
{}

void FITSImage::setStateImpl (DMI::Record::Ref &rec,bool initializing)
{
	Node::setStateImpl(rec,initializing);

	rec[FFilename].get(filename_,initializing);
  cout<<"File Name ="<<filename_<<endl;
	if(rec[FCutoff].get(cutoff_,initializing)) {
   cout<<"Cutoff ="<<cutoff_<<endl;
	}

}

 
int FITSImage::getResult (Result::Ref &resref, 
                       const std::vector<Result::Ref> &childres,
                       const Request &request,bool)
{
 double *arr, *lgrid, *mgrid, *lspace, *mspace, ra0, dec0;
 long int naxis[4]={0,0,0,0};
 int flag=read_fits_file(filename_.c_str(),cutoff_,&arr, naxis, &lgrid, &mgrid, &lspace, &mspace, &ra0, &dec0);
 FailWhen(flag," Error Reading Fits File "+flag);

 for (int i=0;i<4;i++) {cout<<" i="<<i<<" "<<naxis[i]<<endl;}
 //create a result with 3 vellset, is integrated
 //if integrated=0, cells is removed
 Result &result=resref<<= new Result(3,1); 

 /* RA vellset */
 VellSet::Ref ref0;
 VellSet &vs0= ref0<<= new VellSet(0,1);
 Vells ra_vells=vs0.setValue(new Vells(ra0));
 result.setVellSet(0,ref0);

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
 cout<<"Grid :"<<l_center<<m_center<<endl;
 cout<<"Space:"<<l_space<<m_space<<endl;

 Domain::Ref domain(new Domain());
 domain().defineAxis(Axis::TIME,0,1);
 domain().defineAxis(Axis::FREQ,0,1);
 domain().defineAxis(Axis::axis("R"),l_center(0)-l_space(0)/2,l_center(naxis[0]-1)+l_space(naxis[0]-1)/2);
 domain().defineAxis(Axis::axis("D"),m_center(0)-m_space(0)/2,m_center(naxis[1]-1)+m_space(naxis[1]-1)/2);
 domain().defineAxis(Axis::axis("S"),0,1);
 Cells::Ref cells_ref;
 Cells &cells=cells_ref<<=new Cells(*domain);

 //axis, [left,right], segments
 cells.setCells(Axis::TIME,0,1,1);
 cells.setCells(Axis::FREQ,0,1,naxis[3]);
 cells.setCells(Axis::axis("R"),l_center,l_space);
 cells.setCells(Axis::axis("D"),m_center,m_space);
 cells.setCells(Axis::axis("S"),0,1,naxis[2]);

 cout<<"Cells ="<<cells<<endl;
 cout<<"Axis T "<<cells.ncells(Axis::TIME)<<endl;
 cout<<"Axis F "<<cells.ncells(Axis::FREQ)<<endl;
 cout<<"Axis R "<<cells.ncells(Axis::axis("R"))<<endl;
 cout<<"Axis D "<<cells.ncells(Axis::axis("D"))<<endl;
 cout<<"Axis S "<<cells.ncells(Axis::axis("S"))<<endl;
 Vells::Shape shape(1,naxis[3],naxis[0],naxis[1],naxis[2]);
 //Axis::degenerateShape(shape,cells.rank());
 cout<<"Ranks "<<shape.size()<<"and "<<cells.rank()<<endl;
 cout<<"Shapes "<<shape<<cells.shape()<<endl;
 cout<<"Ranks "<<shape.size()<<"and "<<cells.rank()<<endl;
 // axes are RA(0),Dec(1),Stokes(2),Freq(3)
 // but here we have Freq,Stokes,Dec,RA
 blitz::Array<double,4> A(arr, blitz::shape(naxis[3],naxis[2],naxis[1],naxis[0]), blitz::duplicateData); 

 //cout<<"Original ="<<A<<endl;
 //transpose array such that Freq,RA,Dec,Stokes
 A.transposeSelf(0,3,2,1);
 //cout<<"Transpose ="<<A<<endl;
 cout<<"Transpose ="<<A.shape()<<endl;

 VellSet::Ref ref;
 VellSet &vs= ref<<= new VellSet(0,1);
 //create 5D vells Time,Freq,RA,Dec,Stokes
 Vells &out=vs.setValue(new Vells(0.0,shape));
 vs.setShape(shape);
 VellsSlicer<double,4> slout(out,1,2,3,4);
 //copy A to the time slice of varr
 slout=A;
 //blitz::Array<double,5> varr(out.getArray<double,5>());
 //varr(0,LoRange::all(),LoRange::all(),LoRange::all(),LoRange::all())=A;
//cout<<"Output array: "<<out.getArray<double,5>();
 cout<<"Output array: "<<out.getArray<double,5>().shape();

 result.setVellSet(2,ref);
 result.setCells(cells);

 free(arr);
 free(lgrid);
 free(lspace);
 free(mgrid);
 free(mspace);
 return 0;
}


} // namespace Meq
int zero_image_float(long totalrows, long offset, long firstrow, long nrows,
   int ncols, iteratorCol *cols, void *user_struct) {
    int ii, status = 0;

    /* declare counts static to preserve the values between calls */
		/* so it traverses the whole array */
    static float *counts;
		static double tmpval;
		static long int pt,d1,d2,d3,d4;
    static long int xmin;
		static long int ymin,xmax,ymax;

    nlims *arr_dims=(nlims*)user_struct;
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
    for (ii=0;ii<arr_dims->naxis;ii++) {
			printf("%d %ld\n",ii,arr_dims->d[ii]);
		}
       /* assign the input pointers to the appropriate arrays and null ptrs*/
       counts   = (float *)  fits_iter_get_array(&cols[0]);
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

    for (ii = 1; ii <= nrows; ii++)
    {
			//printf("arr =%f\n",counts[ii]);
       //counts[ii] = 1.;
			 tmpval=(double)counts[ii];
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

    double *xylims=(double*)user_struct;
    static float *counts;
    if (firstrow == 1)
    {
       if (ncols != 1)
           return(-1);  /* number of columns incorrect */
       /* assign the input pointers to the appropriate arrays and null ptrs*/
       counts   = (float *)  fits_iter_get_array(&cols[0]);

		min_val=1e6;
		max_val=-1e6;
    }

    for (ii = 1; ii <= nrows; ii++) {
			 tmpval=(double)counts[ii];
		   if (min_val>tmpval) min_val=tmpval;
		   if (max_val<tmpval) max_val=tmpval;
    }

		xylims[0]=min_val;
		xylims[1]=max_val;
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
int read_fits_file(const char *filename,double cutoff, double**myarr, long int *new_naxis, double **lgrid, double **mgrid, double **lspace, double **mspace, 
								double *ra0, double *dec0) {
    fitsfile *fptr,*outfptr;
    iteratorCol cols[3];  /* structure used by the iterator function */
    int n_cols;
    long rows_per_loop, offset;
		nlims arr_dims;
		double arr_limits[2];

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
    printf("File =%s\n",filename);
    fits_open_file(&fptr, filename, READWRITE, &status); /* open file */

/* WCSLIB et al. */
		/* read FITS header */
		if (status = fits_hdr2str(fptr, 1, NULL, 0, &header, &ncard, &status)) {
		 fits_report_error(stderr, status);
		 return 1;
		}

		printf("header %s\n",header); 
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
	  if (status = wcsprt(wcs)) return status;






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
			printf("Type Bytes\n");
			datatype=TBYTE;
		}else if(bitpix==SHORT_IMG) {
			printf("Type Short Int\n");
			datatype=TSHORT;
		}else if(bitpix==LONG_IMG) {
			printf("Type Long Int\n");
			datatype=TLONG;
		}else if(bitpix==FLOAT_IMG) {
			printf("Type Float\n");
			datatype=TFLOAT;
		}else if(bitpix==DOUBLE_IMG) {
			printf("Type Double\n");
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
    fits_iterate_data(n_cols, cols, offset, rows_per_loop,
                      get_min_max, (void*)&arr_limits, &status);

		printf("Limits Min %lf, Max %lf\n",arr_limits[0],arr_limits[1]);
		arr_dims.tol=cutoff*(arr_limits[1]-arr_limits[0])+arr_limits[0];
    /* apply the rate function to each row of the table */
    printf("Calling iterator function...%d\n", status);

    rows_per_loop = 0;  /* use default optimum number of rows */
    offset = 0;         /* process all the rows */
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
	  printf("(%ld %ld %ld %ld) ",arr_dims.lpix[0],
									arr_dims.lpix[1],	arr_dims.lpix[2], arr_dims.lpix[3]);
	  printf(" to (%ld %ld %ld %ld)\n",arr_dims.hpix[0],
									arr_dims.hpix[1],	arr_dims.hpix[2], arr_dims.hpix[3]);
	  
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

		printf("writing %ld pixels\n",totalpix);
		
		if ((*myarr=(double*)calloc((size_t)totalpix,sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		}

		/* turn off scaling so that we copy the pixel values */
		bscale=1.0; bzero=0.0;
    fits_set_bscale(fptr,  bscale, bzero, &status);

		/* read the subset increment=[1,1,1,..]*/
		fits_read_subset(fptr, TDOUBLE, arr_dims.lpix, arr_dims.hpix, increment,
									 0, *myarr, &null_flag, &status);

    

		/* ******************BEGIN create grid for the cells using WCS */
    printf("found axis %d\n",wcs->naxis);
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

/*		for (ii=0; ii<ncoord;ii++) {
  	 if ((pixelc[ii]=(double*)calloc((size_t)wcs->naxis,sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		 }
  	 if ((imgc[ii]=(double*)calloc((size_t)wcs->naxis,sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		 }
  	 if ((worldc[ii]=(double*)calloc((size_t)wcs->naxis,sizeof(double)))==0) {
			fprintf(stderr,"%s: %d: no free memory\n",__FILE__,__LINE__);
			return 1;
		 }
		} */
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

		printf("total %d, created %d\n",ncoord,kk);
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

    /* find the phase centre in RA,Dec */
		/* now kk has passed the last pixel */
		kk=(ncoord-1)*4;
		printf("finished %d\n",kk);
		*ra0=(worldc[0]+worldc[kk])*M_PI/360.0;
		*dec0=(worldc[1]+worldc[kk+1])*M_PI/360.0;
		l0=(imgc[0]+imgc[kk])*0.5;
		m0=(imgc[1]+imgc[kk+1])*0.5;
		printf("phase centre celestial=(%lf,%lf) native l,m=(%lf,%lf)\n",*ra0,*dec0,l0,m0);

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
					(*lgrid)[new_naxis[0]-ii-1]=imgc[ii*4*new_naxis[1]]-l0;
		}
		/* different strides */
		for (ii=0;ii<new_naxis[1];ii++) {
					(*mgrid)[ii]=imgc[ii*4+1]-m0;
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
