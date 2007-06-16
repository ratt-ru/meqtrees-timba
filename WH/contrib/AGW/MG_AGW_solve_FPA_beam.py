#!/usr/bin/python

#
# Copyright (C) 2006
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


# Short description:
#  The script should just read in a 2-D array of points from a
#  FITS file, assign them to a FITSImage, and then solve for
#  the maximum positions ans the widths of a corresponding
#  gaussian.

#  It solves for the x hand and y hand beams separately

# History:
# - 23 Jan 2007: creation:

#=======================================================================
# Import of Python / TDL modules:

import math
import random
import os

from string import split, strip
from numarray import *

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meqds
from Timba.Meq import meq
import Meow.Bookmarks

# to force caching put 100
Settings.forest_state.cache_policy = 100

# MEP table for derived quantities fitted in this script
mep_beam_locations = 'beam_locations.mep';

# first, make sure that any previous version of the mep table is
# obliterated so nothing strange happens in succeeding steps
try:
  os.system("rm -fr "+ mep_beam_locations);
except:   pass

def create_polc(c00=0.0,degree_f=0,degree_t=0):
  """helper function to create a t/f polc with the given c00 coefficient,
  and with given order in t/f""";
  polc = meq.polc(zeros((degree_t+1, degree_f+1))*0.0);
  polc.coeff[0,0] = c00;
  return polc;

def tpolc (tdeg,c00=0.0):
  return Meq.Parm(create_polc(degree_f=0,degree_t=tdeg,c00=c00),
                  node_groups='Parm',
                  constrain = [-0.04,0.04],
                  table_name=mep_beam_locations);

def wpolc (tdeg,c00=0.0):
  return Meq.Parm(create_polc(degree_f=0,degree_t=tdeg,c00=c00),
                  node_groups='Parm',
                  constrain = [1.0e-5,0.04],
                  table_name=mep_beam_locations);

########################################################
def _define_forest(ns):  


  ns.ln_16 << Meq.Constant(-2.7725887)
  # fits a Gaussian to each beam to locate its maximum 

  ns.width_x << wpolc(tdeg=0,c00=0.01)
  ns.width_y << wpolc(tdeg=0,c00=0.01)

  laxis = ns.laxis << Meq.Grid(axis=2);
  maxis = ns.maxis << Meq.Grid(axis=3);

# read in beam images
  home_dir = os.environ.get('LOFAR_AGW','.');
  # read in beam data

  infile_name_re_yx = home_dir + '/veidt_stuff/yx_real.fits'
  infile_name_im_yx = home_dir + '/veidt_stuff/yx_imag.fits'
  infile_name_re_yy = home_dir + '/veidt_stuff/yy_real.fits'
  infile_name_im_yy = home_dir + '/veidt_stuff/yy_imag.fits'
  ns.image_re_yx << Meq.FITSImage(filename=infile_name_re_yx,cutoff=1.0,mode=2)
  ns.image_im_yx << Meq.FITSImage(filename=infile_name_im_yx,cutoff=1.0,mode=2)
  ns.image_re_yy << Meq.FITSImage(filename=infile_name_re_yy,cutoff=1.0,mode=2)
  ns.image_im_yy << Meq.FITSImage(filename=infile_name_im_yy,cutoff=1.0,mode=2)

  infile_name_re_xx = home_dir + '/veidt_stuff/xx_real.fits'
  infile_name_im_xx = home_dir + '/veidt_stuff/xx_imag.fits'
  infile_name_re_xy = home_dir + '/veidt_stuff/xy_real.fits'
  infile_name_im_xy = home_dir + '/veidt_stuff/xy_imag.fits'
  ns.image_re_xx << Meq.FITSImage(filename=infile_name_re_xx,cutoff=1.0,mode=2)
  ns.image_im_xx << Meq.FITSImage(filename=infile_name_im_xx,cutoff=1.0,mode=2)
  ns.image_re_xy << Meq.FITSImage(filename=infile_name_re_xy,cutoff=1.0,mode=2)
  ns.image_im_xy << Meq.FITSImage(filename=infile_name_im_xy,cutoff=1.0,mode=2)

  ns.im_sq_x << ns.image_re_xx * ns.image_re_xx + ns.image_im_xx * ns.image_im_xx + ns.image_re_xy * ns.image_re_xy + ns.image_im_xy * ns.image_im_xy
  ns.im_x << Meq.Sqrt(ns.im_sq_x)
  ns.image_x << ns.im_x / Meq.Max(ns.im_x)
  ns.resampler_x << Meq.Resampler(ns.image_x)
  ns.l_x<< tpolc(0)
  ns.m_x<< tpolc(0)
  ns.lm_x_sq << Meq.Sqr(laxis - ns.l_x) + Meq.Sqr(maxis - ns.m_x) 
  ns.gaussian_x << Meq.Exp((ns.lm_x_sq * ns.ln_16)/Meq.Sqr(ns.width_x));

  ns.condeq_x<<Meq.Condeq(children=(ns.resampler_x, ns.gaussian_x))
  ns.solver(0)<<Meq.Solver(ns.condeq_x,num_iter=50,epsilon=1e-4,solvable=[ns.l_x,ns.m_x,ns.width_x],save_funklets=True,last_update=True)


  ns.im_sq_y << ns.image_re_yy * ns.image_re_yy + ns.image_im_yy * ns.image_im_yy + ns.image_re_yx * ns.image_re_yx + ns.image_im_yx * ns.image_im_yx
  ns.im_y << Meq.Sqrt(ns.im_sq_y)
  ns.image_y << ns.im_y / Meq.Max(ns.im_y)
  ns.resampler_y << Meq.Resampler(ns.image_y)
  ns.l_y<< tpolc(0)
  ns.m_y<< tpolc(0)
  ns.lm_y_sq << Meq.Sqr(laxis - ns.l_y) + Meq.Sqr(maxis - ns.m_y) 
  ns.gaussian_y << Meq.Exp((ns.lm_y_sq * ns.ln_16)/Meq.Sqr(ns.width_y));

  ns.condeq_y<<Meq.Condeq(children=(ns.resampler_y, ns.gaussian_y))
  ns.solver(1)<<Meq.Solver(ns.condeq_y,num_iter=50,epsilon=1e-4,solvable=[ns.l_y,ns.m_y,ns.width_y],save_funklets=True,last_update=True)
  ns.req_mux<<Meq.ReqMux(children=[ns.solver(k) for k in range(0,2)])

########################################################################

def _test_forest(mqs,parent):

# any large time range will do
  t0 = 0.0;
  t1 = 1.5e70

# any large frequency range will do
  f0 = 0.0
  f1 = 1.5e70

  lm_range = [-0.04,0.04];
  lm_num = 50;
# define request
  request = make_request(dom_range = [[f0,f1],[t0,t1],lm_range,lm_range], nr_cells = [1,1,lm_num,lm_num])
# execute request
  mqs.meq('Node.Execute',record(name='req_mux',request=request),wait=True);

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
  
