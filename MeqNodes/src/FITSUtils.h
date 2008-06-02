//# FITSUtils.h: Everything and anything related to FITS files
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

#ifndef MEQNODES_FITSUTILS_H
#define MEQNODES_FITSUTILS_H
//for the Mutex
#include <TimBase/Thread/Mutex.h>
extern LOFAR::Thread::Mutex cfitsio_mutex;


    
//#define DEBUG
namespace Meq {

#ifdef __cplusplus
				extern "C" {
#endif
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
// the following is available from the libcfitsio-dev package on Debian,
// in a perfect world it should be found by configure
#include <fitsio.h>

#ifdef HAVE_CASACORE
// wcs should've been found by configure
#include <wcslib/wcs.h>
#include <wcslib/prj.h>
#include <wcslib/wcshdr.h>
#include <wcslib/wcsfix.h>
#else
// else we are a damned soul that is still using aips++...
// the following is w.r.t. the aips++ include path, kinda kludgy
#include <../casa/wcslib/wcs.h>
#include <../casa/wcslib/prj.h>
#include <../casa/wcslib/wcshdr.h>
#include <../casa/wcslib/wcsfix.h>
#endif

//for the FITSImage
typedef struct nlimits_ {
		int naxis;
		long int *d;
		long int *lpix;
		long int *hpix;
		double tol;
		int datatype;
} nlims; /* struct to store array dimensions */
int zero_image_float(long totalrows, long offset, long firstrow, long nrows,
   int ncols, iteratorCol *cols, void *user_struct);
int get_min_max(long totalrows, long offset, long firstrow, long nrows,
   int ncols, iteratorCol *cols, void *user_struct);
int read_fits_file(const char *infilename, double cutoff, double **myarr, long int *naxis, double **lgrid, double **mgrid, double **lspace, double **mspace,
								double *ra0, double *dec0, double **fgrid, double **fspace, int mode);

typedef struct drange_ {
		double lims[2]; /* min, max values */
		int datatype;
} drange; /* struct to store min, max limits of image, needs the data type used in the pixels as well */




//for the FITSReader
int simple_read_fits_file(const char *filename,  double **myarr,  double ***cells,
				long int *naxis, long int **naxes, int *is_complex);

//for the FITSWriter
int write_fits_file(const char *filename,  double **myarr,  int nvells, double **cells,
				long int naxis, long int *naxes, int is_complex);


//for the FITSDataMux
typedef struct __io_buff__ {
 fitsfile *fptr;
 nlims arr_dims;
 struct wcsprm *wcs;
} io_buff;

int mux_read_fits_file(const char *infilename, double cutoff, double **myarr, long int *naxis, double **lgrid, double **mgrid, double **lspace, double **mspace,
								double *ra0, double *dec0, double **fgrid, double **fspace, io_buff *fbuff);

int mux_write_fits_file(double *myarr, io_buff fbuff);


#ifdef __cplusplus
				} /* extern "C" */
#endif

} /* namespace Meq */
#endif /* MEQNODES_FITSUTILS_H */ 
