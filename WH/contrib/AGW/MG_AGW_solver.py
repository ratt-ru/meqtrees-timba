#!/usr/bin/python

#% $Id: MG_AGW_solver.py 3929 2006-09-01 20:17:51Z twillis $ 

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

script_name = 'MG_AGW_solver.py'

# Short description:
#  The script should just read in a 2-D array of points from a
#  FITS file, assign them to a FITSImage, and then solve for
#  the maximum position

# History:
# - 24 Oct 2006: creation:

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


########################################################
def _define_forest(ns):  

  # first read in locations of beam peaks given to nearest pixel
  # from 'beam_locations' text file
  # fits aGaussian to each beam to locate its maximum 

  l=0.
  m=0.0
  constrain = [-0.002,0.002]
  width  = ns.width << Meq.Parm(3e-7)

  laxis = ns.laxis << Meq.Grid(axis=2);
  maxis = ns.maxis << Meq.Grid(axis=3);
  # BEAMS = range(1,num_beams+1)
  # Only fit first 26 beams
  BEAMS = range(1,26)

  home_dir = os.environ['HOME']
  for k in BEAMS:
    infile_name = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(k) + '.fits'
    ns.image(k) << Meq.FITSImage(filename=infile_name,cutoff=1.0,mode=2)
    ns.resampler(k) << Meq.Resampler(ns.image(k))
    ns.l0(k)<< Meq.Parm(l,node_groups='Parm',constrain=constrain)
    ns.m0(k)<< Meq.Parm(m,node_groups='Parm',constrain=constrain)

    ns.gaussian(k) << Meq.Exp((-Meq.Sqr(laxis - ns.l0(k)) -Meq.Sqr(maxis - ns.m0(k)))/width);

    ns.condeq(k)<<Meq.Condeq(children=(ns.resampler(k), ns.gaussian(k)))
    ns.solver(k)<<Meq.Solver(ns.condeq(k),num_iter=50,epsilon=1e-4,solvable=[ns.l0(k),ns.m0(k)])
  ns.req_mux<<Meq.ReqMux(children=[ns.solver(k) for k in BEAMS])


########################################################################

def _test_forest(mqs,parent):

# any old time will do
  t0 = 0.5;
  t1 = 1.5

# any old frequency
  f0 = 0.5
  f1 = 1.5

  lm_range = [-0.003,0.003];
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
  
