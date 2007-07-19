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
import numarray.mlab
import pyfits
import math 
from string import split, strip

def usage( prog ):
        print 'usage : %s <infile_grasp> <outfile_fits> rot_multiplier' % prog
        return 1

def getdata( filename ):
        flip = False
	text = open(filename, 'r').readlines()
	L = len(text)
	i = 0
	while(text[i][0:4] != '++++'):
		i = i+1
		if i >= L:
			print 'bogus input file : ++++ never found'
			return data,0

#	print 'input grd file contains %d comments' % i
	
	info = split(strip(text[i+1]))
	if(info[0] != '1'):
		print 'bogus input file'
		return data,0
	
	info = split(strip(text[i+2]))
        num_beams = int(info[0])
	icomp = int(info[1])
	ncomp = int(info[2])
	igrid = int(info[3])
	if igrid != 1:
		print 'not a UV grid'
		return data,0
	if icomp != 3:
		print 'not linear polarization'
		return data,0
	
        array_beams = []
        index = i+10
        for l in range(num_beams):
          print 'beam number ', l
          beam={}
          print 'getting nx, ny from line ', index+1
	  info = split(strip(text[index+1]))
	  nx = int(info[0])
	  ny = int(info[1])
          print 'array dims ', nx, ' ', ny
          num_points = nx * ny
	  if nx != ny:
		print 'unsupported : nx != ny'
		return data, 0
	
          print 'getting scale from line ', index
	  info = split(strip(text[index]))
	  beam['scale'] = (float(info[2])-float(info[0]))/float(nx-1)
	
	  data = []
	  for j in range(2*ncomp):
		  data.append([])
	
	  for j in range(index+2, index+2+num_points):
		  comps = split(strip(text[j]))
		  for k in range(2*ncomp):
			  data[k].append(float(comps[k]))
          beam['data'] = data
          beam['flip'] = flip
          beam['nx'] = nx
          array_beams.append(beam)
          index= index+2+num_points

	return array_beams

def get_column( data, flip, nx, mV=0, mH=0, col_no=0 ):
        print'get_column parameters flip, mV, mH, col_no ', flip, ' ', ' ', mV, ' ', mH, ' ', col_no
	Z = numarray.zeros( (nx, nx), numarray.Float64 )
	C = len(data)
	L = len(data[0])
	m = 0.0
        y_max = -1000
        x_max = -1000
        data_max = - 100000000.0
	for y in range(nx):
		for x in range(nx):	
                        if mV > 0:
                         x_index = nx - 1 - x
                        else:
                         x_index = x
                        if mH > 0:
                         y_index = nx - 1 - y
                        else:
                         y_index = y
			i = y + nx*x
			s = 0.0;
                        start_col = 0
                        end_col = C
                        if col_no > 0:
                          start_col = col_no - 1
                          end_col = col_no
                          if flip:
                            if start_col == 0:
                              start_col = 2
                              end_col = 3
                            elif start_col == 1:
                              start_col = 3
                              end_col = 4
                            elif start_col == 2:
                              start_col = 0
                              end_col = 1
                            elif start_col == 3:
                              start_col = 1
                              end_col = 2
			for j in range(start_col,end_col):
				s = s + data[j][i]
			Z[x_index][y_index] = s
                        if s > data_max:
                          data_max = s
                          x_max = x_index
                          y_max = y_index

                        if s > m:
                                m = s;

	
        print 'x_max y_max ', x_max, ' ', y_max
	return Z, x_max, y_max

def create_fits_file(beam,col_no,mV,mH,rot_factor,name,seq):
        data = beam['data']
        scale = beam['scale']
        # at present Sarod uses input scale of degrees
#        scale = scale  * 180.0 / math.pi

# a scale of 0.07 will creat voltage patterns whose corresponding
# HPBW is approx 0.6 degrees
        scale = 0.07

	ncomp = len(data)
	if(ncomp <= 0): 
		exit

	size = len(data[0])

	nx = int(math.sqrt(size))
	if(nx*nx != size):
		print 'data not square'
		exit

	Z, x_max, y_max = get_column(data, beam['flip'], nx, mV, mH,col_no);
        
        # grab a subsection of the image
        array_selector = []
        axis_slice = slice(21,81)
        axis_slice1 = slice(40,100)
        array_selector.append(axis_slice)
        array_selector.append(axis_slice1)

        Z2 = Z[tuple(array_selector)] 
        # turn 2D array into a 4D array so that pyfits will
        # generate an image with NAXIS = 4
        Z1 = numarray.mlab.rot90(Z2, rot_factor)
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
        hdu.header.update('CDELT1', (-1.0) * scale, 'in degrees for Meq.FITSImage')
        hdu.header.update('CRPIX1', Z1.shape[0]/2 + 1, 'reference pixel (one relative)')
        hdu.header.update('CRVAL1', 0.0, 'M = 0 at beam peak')
        hdu.header.update('CUNIT1', 'deg     ')

        hdu.header.update('CTYPE2', 'L')
        hdu.header.update('CDELT2', scale, 'in degrees for Meq.FITSImage')
        hdu.header.update('CRPIX2', Z1.shape[1]/2 + 1, 'reference pixel (one relative)')
        hdu.header.update('CRVAL2', 0.0, 'L = 0 at beam peak')
        hdu.header.update('CUNIT2', 'deg     ')

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
        add_on = ""
        if col_no == 1:
          add_on = "_Re_x"
        if col_no == 2:
          add_on = "_Im_x"
        if col_no == 3:
          add_on = "_Re_y"
        if col_no == 4:
          add_on = "_Im_y"
#       outfile = out_string + add_on + ".fits"
        orientation = "y"
        if rot_factor > 0:
          orientation = "x"
        outfile = name + str(seq) + orientation + add_on + ".fits"
        print 'creating fits_file ', outfile
        # delete any previous file
        if os.path.exists(outfile):
          os.remove(outfile)
        hdulist.writeto(outfile)
def main( argv ):
        print 'processing grd file ', argv[1]
        array_beams  = getdata(argv[1])
        # presently get data array as total power 
        # we may want additional formats
        # mirror horizontally?
        mV = 0
        try:
          mV = int(argv[3])
        except:
          pass
        mH = 0
        try:
          mH = int(argv[4])
        except:
          pass
        # rotate matrix by x * 90 deg?
        try:
          rot_factor = int(argv[5])
        except:
          rot_factor = 0
        # select data by a particular column?
        try:
          col_no = int(argv[6])
        except:
          col_no = 0

        for i in range(len(array_beams)):
          create_fits_file(array_beams[i],col_no,mV,mH,rot_factor,argv[2],i)

#=============================
# argv[1]  incoming grd file
# argv[2]  front part of output fits file
# argv[3]  1: mirror vertically
# argv[4]  1: mirror horizontally
# argv[5]  rotate matrix 90 deg x argv[5]
# argv[6]  column number to read
if __name__ == "__main__":
  if len(sys.argv) < 3:
    usage(sys.argv[0])
  else:
    main(sys.argv)
