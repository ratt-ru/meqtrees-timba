#!/usr/bin/python

#% $Id: MG_AGW_form_beam.py 3929 2006-09-01 20:17:51Z twillis $ 

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

# script_name = 'MG_AGW_form_beam.py'

# Short description:
# We read in a group of focal plane array beams, corrresponding
# weights, and form a combined, weighted beam.

# History:
# - 22 Dec 2006: creation:

#=======================================================================
# Import of Python / TDL modules:

import math
import random

from string import split, strip
from numarray import *

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meqds
from Timba.Meq import meq

# to force caching put 100
Settings.forest_state.cache_policy = 100

# ASCII table iof beam weights
beam_weights = 'focal_plane_beam_weights'

########################################################
def _define_forest(ns):  

# read in beam weights
  weights = {}
  myfile = open(beam_weights, 'r')
  text = myfile.readlines()
  num_records = len(text)
  for i in range(num_records):
    info = split(strip(text[i]))
    weights[info[0]] = float(info[1])
  myfile.close()

# read in beam images
 # fit all 180 beams
  BEAMS = range(1,181)
  BEAMS_1 = range(1,91)
  BEAMS_2 = range(91,181)
  home_dir = os.environ['HOME']
  # read in beam data
  for k in BEAMS:
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
    ns.image_re_x(k) << Meq.FITSImage(filename=infile_name_re_x,cutoff=1.0,mode=2)
    ns.image_im_x(k) << Meq.FITSImage(filename=infile_name_im_x,cutoff=1.0,mode=2)
    ns.image_re_y(k) << Meq.FITSImage(filename=infile_name_re_y,cutoff=1.0,mode=2)
    ns.image_im_y(k) << Meq.FITSImage(filename=infile_name_im_y,cutoff=1.0,mode=2)

    ns.beam_squared(k) << ns.image_re_x(k) * ns.image_re_x(k) + ns.image_im_x(k) * ns.image_im_x(k) + ns.image_re_y(k) * ns.image_re_y(k) + ns.image_im_y(k) * ns.image_im_y(k)
    ns.beam_sqrt(k) << Meq.Sqrt(ns.beam_squared(k))
    ns.normalize(k) << Meq.Max(ns.beam_sqrt(k))
    ns.beam_re_x(k) << ns.image_re_x(k) / ns.normalize(k)
    ns.beam_im_x(k) << ns.image_im_x(k) / ns.normalize(k)
    ns.beam_re_y(k) << ns.image_re_y(k) / ns.normalize(k)
    ns.beam_im_y(k) << ns.image_im_y(k) / ns.normalize(k)
    ns.beam_x(k) << Meq.ToComplex(ns.beam_re_x(k), ns.beam_im_x(k))
    ns.beam_y(k) << Meq.ToComplex(ns.beam_re_y(k), ns.beam_im_y(k))
    ns.beam_weight(k) << Meq.ToComplex(weights[infile_name_re_x], weights[infile_name_im_x])
    ns.beam_wt(k) << Meq.ConjTranspose(ns.beam_weight(k))
    ns.wt_beam_x(k) << ns.beam_x(k) * ns.beam_wt(k)
    ns.wt_beam_y(k) << ns.beam_y(k) * ns.beam_wt(k)

  ns.beam_wt_sum_1 << Meq.Add(*[ns.beam_wt(k) for k in BEAMS_1])
  ns.beam_wt_sum_2 << Meq.Add(*[ns.beam_wt(k) for k in BEAMS_2])

  ns.voltage_sum_x_1 << Meq.Add(*[ns.wt_beam_x(k) for k in BEAMS_1]) / ns.beam_wt_sum_1
  ns.voltage_sum_y_1 << Meq.Add(*[ns.wt_beam_y(k) for k in BEAMS_1]) / ns.beam_wt_sum_1
  ns.voltage_sum_x_2 << Meq.Add(*[ns.wt_beam_x(k) for k in BEAMS_2]) / ns.beam_wt_sum_2
  ns.voltage_sum_y_2 << Meq.Add(*[ns.wt_beam_y(k) for k in BEAMS_2]) / ns.beam_wt_sum_2

  ns.E << Meq.Matrix22(ns.voltage_sum_x_1, ns.voltage_sum_y_2,ns.voltage_sum_y_1, ns.voltage_sum_x_2)

########################################################################
def _test_forest(mqs,parent):

# any large time range will do
  t0 = 0.0;
  t1 = 1.5e70

  f0 = 0.5
  f1 = 1.5

  lm_range = [-0.04,0.04];
  lm_num = 50;
# define request
  request = make_request(dom_range = [[f0,f1],[t0,t1],lm_range,lm_range], nr_cells = [1,1,lm_num,lm_num])
# execute request
  mqs.meq('Node.Execute',record(name='E',request=request),wait=True);

#####################################################################
def make_request(Ndim=4,dom_range=[0.,1.],nr_cells=5):

    """make multidimensional request, dom_range should have length 2 or be a list of
    ranges with length Ndim, nr_cells should be scalar or list of scalars with length Ndim"""
    forest_state=meqds.get_forest_state();
    axis_map=forest_state.axis_map;
    
    range0 = [];
    if is_scalar(dom_range[0]):
        for i in range(Ndim):		
            range0.append(dom_range);
    else:
        range0=dom_range;
    nr_c=[];
    if is_scalar(nr_cells):
        for i in range(Ndim):		
            nr_c.append(nr_cells);
    else:
        nr_c =nr_cells;
    dom = meq.domain(range0[0][0],range0[0][1],range0[1][0],range0[1][1]); #f0,f1,t0,t1
    cells = meq.cells(dom,num_freq=nr_c[0],num_time=nr_c[1]);
    
    # workaround to get domain with more axes running 

    for dim in range(2,Ndim):
        id = axis_map[dim].id;
        if id:
            dom[id] = [float(range0[dim][0]),float(range0[dim][1])];
            step_size=float(range0[dim][1]-range0[dim][0])/nr_c[dim];
            startgrid=0.5*step_size+range0[dim][0];
            grid = [];
            cell_size=[];
        for i in range(nr_c[dim]):
            grid.append(i*step_size+startgrid);
            cell_size.append(step_size);
            cells.cell_size[id]=array(cell_size);
            cells.grid[id]=array(grid);
            cells.segments[id]=record(start_index=0,end_index=nr_c[dim]-1);

    cells.domain=dom;
    request = meq.request(cells);
    return request;

if __name__=='__main__':
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
  
