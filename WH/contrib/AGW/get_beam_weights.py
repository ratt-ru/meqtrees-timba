#!/usr/bin/env python

# a python script to read fits files, find the pixel value
# at the specified l, m location and write the values in to
# a file for later use as weights in focal plane array 
# beamforming

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
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
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import os
import sys
import numarray
import numarray.mlab
import pyfits
import math 
from string import split, strip

def getdata(l, m ):
 # process all 180 beams
  outfile = 'focal_plane_beam_weights'
  myfile = open(outfile, 'w')

  BEAMS = range(1,181)
  home_dir = os.environ['HOME']
  # read in beam data
  for k in BEAMS:
    print 'processing beam ', k
    if k <= 90:
      fits_num = k
      infile_name_re_x = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + 'x_Re_x.fits'
      infile_name_im_x = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + 'x_Im_x.fits'
      infile_name_re_y = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + 'x_Re_y.fits'
      infile_name_im_y = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + 'x_Im_y.fits'
    else:
      fits_num = k - 90
      infile_name_re_x = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + 'y_Re_x.fits'
      infile_name_im_x = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + 'y_Im_x.fits'
      infile_name_re_y = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + 'y_Re_y.fits'
      infile_name_im_y = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + 'y_Im_y.fits'

    data_array = []
    for i in range(4):
      if i == 0:
        filename = infile_name_re_x
      if i == 1:
        filename = infile_name_im_x
      if i == 2:
        filename = infile_name_re_y
      if i == 3:
        filename = infile_name_im_y
      image = pyfits.open(filename)
# get data
      data_array.append(image[0].data * image[0].data)
      image.close()
    for i in range(1,4):
      data_array[0] = data_array[0] + data_array[i]
    beam_array = numarray.sqrt(data_array[0])
    beam_array_norm = beam_array.max()

    for i in range(2):
      if i == 0:
        filename = infile_name_re_x
      if i == 1:
        filename = infile_name_im_x
      image = pyfits.open(filename)
# get data
      image_array = image[0].data
    # get pixel increment in l and m
      header = image[0].header
      l_delta = header['CDELT1'] #note -interpreted by sarod as units = degrees
      m_delta = header['CDELT2'] #note -interpreted by sarod as units = degrees
      l_ref = header['CRPIX1']
      m_ref = header['CRPIX2']
      l_delta = float(l_delta) * math.pi / 180.0 # convert to rad for Sarod equiv
      m_delta = float(m_delta) * math.pi / 180.0 # convert to rad for Sarod equiv
    
      l_pixel = int(float(l) / l_delta + float(l_ref) - 1)
      m_pixel = int(float(m) / m_delta + float(m_ref) - 1)
      data_out = image_array[0,0, l_pixel, m_pixel] / beam_array_norm 
      outstring = filename + ' ' + str(data_out) + '\n'
      myfile.write(outstring)
      image.close()
  myfile.close()

def main( argv ):
  l = argv[1]
  m = argv[2]
  getdata(l,m)

#=============================
if __name__ == "__main__":
# if len(sys.argv) < 3:
#   usage(sys.argv[0])
# else:
    main(sys.argv)
