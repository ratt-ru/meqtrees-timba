#!/usr/bin/python

#% $Id: MG_AGW_solve_720_beams.py 3929 2006-09-01 20:17:51Z twillis $ 

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

# script_name = 'MG_AGW_solve_720_beams.py'

# Short description:
#  The script should just read in a 2-D array of points from a
#  FITS file, assign them to a FITSImage, and then solve for
#  the maximum position.

#  It solves for all 180 beams in the Brisken vivaldi array
#  It first reads in and combines the data from the Re(x) Im(x) Re(y) Im(y)
#  data for each beam

# History:
# - 24 Nov 2006: creation:

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

# setup a few bookmarks
Settings.forest_state = record(bookmarks=[
  Meow.Bookmarks.PlotPage("Beams",["image:1","image:12"],["image:19","image:25"],["image:91","image:102"],["image:109","image:115"]),
  Meow.Bookmarks.PlotPage("All Beams y1",["image:1","image:16","image:17","image:18"],["image:2","image:5","image:20","image:21"],["image:3","image:6","image:8", "image:23"],["image:4","image:7","image:9","image:10"]),
  Meow.Bookmarks.PlotPage("All Beams y2",["image:19","image:22","image:24","image:25"],["image:11","image:12","image:13","image:14"],["image:15"]),
  Meow.Bookmarks.PlotPage("All Beams y3",["image:26","image:41","image:42","image:43"],["image:27","image:30","image:45","image:46"],["image:28","image:31","image:33", "image:48"],["image:29","image:32","image:34","image:35"]),
  Meow.Bookmarks.PlotPage("All Beams y4",["image:44","image:47","image:49","image:50"],["image:36","image:37","image:38","image:39"],["image:40"]),
  Meow.Bookmarks.PlotPage("All Beams y5",["image:51","image:66","image:67","image:68"],["image:52","image:55","image:70"],["image:53","image:56","image:58"],["image:54","image:57","image:59","image:60"]),
  Meow.Bookmarks.PlotPage("All Beams y6",["image:69"],["image:61","image:62","image:63","image:64"],["image:65"]),
  Meow.Bookmarks.PlotPage("All Beams y7",["image:71","image:86","image:87","image:88"],["image:72","image:75","image:90"],["image:73","image:76","image:78"],["image:74","image:77","image:79","image:80"]),
  Meow.Bookmarks.PlotPage("All Beams y8",["image:89"],["image:81","image:82","image:83","image:84"],["image:85"]),
  Meow.Bookmarks.PlotPage("All Beams x1",["image:91","image:106","image:107","image:108"],["image:92","image:95","image:110","image:111"],["image:93","image:96","image:98", "image:113"],["image:94","image:97","image:99","image:100"]),
  Meow.Bookmarks.PlotPage("All Beams x2",["image:109","image:112","image:114","image:115"],["image:101","image:102","image:103","image:104"],["image:105"]),
  Meow.Bookmarks.PlotPage("Condeqs",["condeq:1","condeq:12"],["condeq:19","condeq:25"],["condeq:91","condeq:102"],["condeq:109","condeq:115"])
]);

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


########################################################
def _define_forest(ns):  

  # fits a Gaussian to each beam to locate its maximum 

  l=0.
  m=0.0
  width  = ns.width << Meq.Parm(1e-4)

  laxis = ns.laxis << Meq.Grid(axis=2);
  maxis = ns.maxis << Meq.Grid(axis=3);

  # fit all 180 beams
  BEAMS = range(1,181)
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
    # add up squares of beam components
    ns.im_sq(k) << ns.image_re_x(k) * ns.image_re_x(k) + ns.image_im_x(k) * ns.image_im_x(k) +  ns.image_re_y(k) * ns.image_re_y(k) + ns.image_im_y(k) * ns.image_im_y(k)
    # get the square root
    ns.im(k) << Meq.Sqrt(ns.im_sq(k))
    # normalize peak to 1
    ns.image(k) << ns.im(k) / Meq.Max(ns.im(k))
    ns.resampler(k) << Meq.Resampler(ns.image(k))
    ns.l0(k)<< tpolc(0)
    ns.m0(k)<< tpolc(0)
    ns.gaussian(k) << Meq.Exp((-Meq.Sqr(laxis - ns.l0(k)) -Meq.Sqr(maxis - ns.m0(k)))/width);

    ns.condeq(k)<<Meq.Condeq(children=(ns.resampler(k), ns.gaussian(k)))
    ns.solver(k)<<Meq.Solver(ns.condeq(k),num_iter=50,epsilon=1e-4,solvable=[ns.l0(k),ns.m0(k)],save_funklets=True,last_update=True)
  ns.req_mux<<Meq.ReqMux(children=[ns.solver(k) for k in BEAMS])


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
  
