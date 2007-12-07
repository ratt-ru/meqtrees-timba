#!/usr/bin/python

#
# Copyright (C) 2007
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

# utility functions to handle FPA beams

from Timba.TDL import *

def read_in_FPA_beams(ns, fpa_directory):
  if fpa_directory.find('30') >= 0:
    num_beams = 30
  else:
    num_beams = 90
# read in beam images
  BEAMS = range(0,num_beams)
  for k in BEAMS:
    # read in beam data - y dipoles
    infile_name_re_yx = fpa_directory + '/fpa_pat_' + str(k+num_beams) + '_Re_x.fits'
    infile_name_im_yx = fpa_directory + '/fpa_pat_' + str(k+num_beams) +'_Im_x.fits'
    infile_name_re_yy = fpa_directory + '/fpa_pat_' + str(k+num_beams) +'_Re_y.fits'
    infile_name_im_yy = fpa_directory + '/fpa_pat_' + str(k+num_beams) +'_Im_y.fits' 
    ns.image_re_yx(k) << Meq.FITSImage(filename=infile_name_re_yx,cutoff=1.0,mode=2)
    ns.image_im_yx(k) << Meq.FITSImage(filename=infile_name_im_yx,cutoff=1.0,mode=2)
    ns.image_re_yy(k) << Meq.FITSImage(filename=infile_name_re_yy,cutoff=1.0,mode=2)
    ns.image_im_yy(k) << Meq.FITSImage(filename=infile_name_im_yy,cutoff=1.0,mode=2)

    # read in beam data - x dipoles 
    infile_name_re_xx = fpa_directory + '/fpa_pat_' + str(k) + '_Re_x.fits'
    infile_name_im_xx = fpa_directory + '/fpa_pat_' + str(k) + '_Im_x.fits'
    infile_name_re_xy = fpa_directory + '/fpa_pat_' + str(k) + '_Re_y.fits'
    infile_name_im_xy = fpa_directory + '/fpa_pat_' + str(k) + '_Im_y.fits' 
    ns.image_re_xy(k) << Meq.FITSImage(filename=infile_name_re_xy,cutoff=1.0,mode=2)
    ns.image_im_xy(k) << Meq.FITSImage(filename=infile_name_im_xy,cutoff=1.0,mode=2)
    ns.image_re_xx(k) << Meq.FITSImage(filename=infile_name_re_xx,cutoff=1.0,mode=2)
    ns.image_im_xx(k) << Meq.FITSImage(filename=infile_name_im_xx,cutoff=1.0,mode=2)

  return num_beams
