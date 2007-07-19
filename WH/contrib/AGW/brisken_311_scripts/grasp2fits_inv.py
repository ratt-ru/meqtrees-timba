#!/usr/bin/env python

#% $Id$ 

#
# Copyright (C) 2002-2007
# ASTRON (Netherlands Foundation for Research in Astronomy)
# and The MeqTree Foundation
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# a python script to convert GRASP 'grd' files to 
# FITS files. Thanks to Walter Brisken (NRAO) for
# the code that reads in the GRASP data.

import os
import sys
import numarray
import pyfits
import math 
from string import split, strip

def usage( prog ):
        print 'usage : %s <infile_grasp> <outfile_fits> ' % prog
        return 1

def getdata( filename ):
	text = open(filename, 'r').readlines()
	data = []
	L = len(text)
	i = 0
	while(text[i][0:4] != '++++'):
		i = i+1
		if i >= L:
			print 'bogus input file : ++++ never found'
			return data,0

	print 'input grd file contains %d comments' % i
	
	info = split(strip(text[i+1]))
	if(info[0] != '1'):
		print 'bogus input file'
		return data,0
	
	info = split(strip(text[i+2]))
	icomp = int(info[1])
	ncomp = int(info[2])
	igrid = int(info[3])
	if igrid != 1:
		print 'not a UV grid'
		return data,0
	if icomp != 3:
		print 'not linear polarization'
		return data,0
	
	info = split(strip(text[i+5]))
	nx = int(info[0])
	ny = int(info[1])
	if nx != ny:
		print 'unsupported : nx != ny'
		return data, 0
	
	info = split(strip(text[i+4]))
	scale = (float(info[2])-float(info[0]))/float(nx-1)
	
	for j in range(2*ncomp):
		data.append([])
	
	for j in range(i+6, L):
		comps = split(strip(text[j]))
		for k in range(2*ncomp):
			data[k].append(float(comps[k]))

	return data, (scale*180.0/math.pi)

def totalpower( data, nx ):
	Z = numarray.zeros( (nx, nx), numarray.Float64 )
	C = len(data)
	L = len(data[0])
	m = 0.0
        y_max = -1000
        x_max = -1000
        data_max = -1000000.0
	for y in range(nx):
		for x in range(nx):	
			i = y + nx*x
			s = 0.0;
			for j in range(C):
				s = s + data[j][i]*data[j][i];
			Z[x][y] = s
                        if Z[x][y] > data_max:
                          data_max = Z[x][y]
                          x_max = x
                          y_max = y

			if s > m:
				m = s;

	Z = Z/m
	
	return Z, x_max, y_max

def main( argv ):
        data, scale = getdata(argv[1])

	ncomp = len(data)
	if(ncomp <= 0): 
		exit

	size = len(data[0])

	nx = int(math.sqrt(size))
	if(nx*nx != size):
		print 'data not square'
		exit

	print 'grd file x, y dimensions = %d' % nx
	print 'grd file scale = %f deg / pix' % scale

        # convert to radians'
        scale = math.pi * scale  / 180.0

        # presently get data array as total power 
        # we may want additional formats
	Z, x_max, y_max = totalpower(data, nx);
        print 'array max and position ', Z.max(), ' ', x_max,' ', y_max

        # transpose Z
        axes = numarray.arange(Z.rank)[::-1]
        Z1 = numarray.transpose(Z, axes) 
        # turn 2D array into a 4D array so that pyfits will
        # generate an image with NAXIS = 4
        temp_array = numarray.zeros((1,1,Z1.shape[0],Z1.shape[1]),type=Z1.type())
        temp_array[0,0,:Z1.shape[0],:Z1.shape[1]] = Z1

        # create basic FITS file
        hdu = pyfits.PrimaryHDU(temp_array)

        # note: defining M as the fastest moving axis (FITS uses
        # FORTRAN-style indexing) produces an image that when
        # viewed with kview / ds9 etc looks correct on the sky 
        # with M increasing to left and L increasing toward top
        # of displayed image
        hdu.header.update('CTYPE1', 'M')
        hdu.header.update('CDELT1', (-1.0) * scale, 'in radians')
        hdu.header.update('CRPIX1', y_max+1, 'reference pixel (one relative)')
        hdu.header.update('CRVAL1', 0.0, 'M = 0 at beam peak')
        hdu.header.update('CTYPE2', 'L')
        hdu.header.update('CDELT2', scale, 'in radians')
        hdu.header.update('CRPIX2', x_max+1, 'reference pixel (one relative)')
        hdu.header.update('CRVAL2', 0.0, 'L = 0 at beam peak')

        # add dummy stuff for freq (axis 3) / time (axis4)
        # as a Vells must always have time and frequency axes
        hdu.header.update('CTYPE3', 'FREQ')
        hdu.header.update('CDELT3', 1, 'in Hz')
        hdu.header.update('CRPIX3', 1, 'in pixels (one relative)')
        hdu.header.update('CRVAL3', 1.0, 'equates to grid point')
        hdu.header.update('CTYPE4', 'TIME')
        hdu.header.update('CDELT4', 1, 'in sec')
        hdu.header.update('CRPIX4', 1, 'in pixels (one relative)')
        hdu.header.update('CRVAL4', 1.0, 'equates to grid point')
        hdu.header.update('CPLX', 0, 'false as data is real ')
        hdu.header.update('CELLS', 1, 'true as we want cells')

        # create initial HDUList
        hdulist = pyfits.HDUList([hdu])

        # create auxiliary table for FitsReader with:
        # No of columns  = no. of axes
        # No. of rows = length of the axis with maximum grid points + 1
        # Table name = 'Cells_TBL' - not done
        # In each column, the first element gives the length of that axis
        # (column).
        # So if an axis is undefined, this is 0 and no elements from 
        # that column is read.
        axis1_vals = numarray.zeros((Z.shape[1]+1,),type=numarray.Float32)
        axis1_vals[0] = Z.shape[1]
        for i in range(Z.shape[1]):
          axis1_vals[i+1] =  scale * (y_max - i)
        c1 = pyfits.Column(name='naxis1',format='E', array=axis1_vals)
        axis2_vals = numarray.zeros((Z.shape[0]+1,),type=numarray.Float32)
        axis2_vals[0] = Z.shape[0]
        for i in range(Z.shape[0]):
          axis2_vals[i+1] = (-1.0) * scale * (x_max - i)
        c2 = pyfits.Column(name='naxis2',format='E', array=axis2_vals)

        #last two columns are dummies
        c3 = pyfits.Column(name='naxis3',format='E', array=[1,1])
        c4 = pyfits.Column(name='naxis4',format='E', array=[1,1])

        aux_table = pyfits.new_table([c1,c2,c3,c4])

        # add this auxiliary table to HDUList
        hdulist.append(aux_table)

        # write out FITS file
        outfile = argv[2]
        # delete any previous file
        if os.path.exists(outfile):
          os.remove(outfile)
        hdulist.writeto(outfile)
#=============================
if __name__ == "__main__":
  if len(sys.argv) < 3:
    usage(sys.argv[0])
  else:
    main(sys.argv)
