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
from Timba.Meq import meq

# to force caching put 100
Settings.forest_state.cache_policy = 100


########################################################
def _define_forest(ns):  

# first read in locations of beam peaks given to nearest pixel
# from 'beam_locations' text file

  text = open("./beam_locations", 'r').readlines()
  num_beams = len(text)
  l = zeros((num_beams,),type=Float64)
  m = zeros((num_beams,),type=Float64)
  for i in range(num_beams):
    info = split(strip(text[i]))
    beam = int(info[0])
    l[i] = float(info[1])
    m[i] = float(info[2])

# BEAMS = range(1,num_beams+1)
# Only fit first 26 beams
  BEAMS = range(1,26)

  home_dir = os.environ['HOME']
  for k in BEAMS:
    infile_name = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(k) + '.fits'
    ns.image(k) << Meq.FITSImage(filename=infile_name,cutoff=1.0,mode=2)
    ns.resampler(k) << Meq.Resampler(ns.image(k), dep_mask=0xff)
    # add 0.00005 offsets in L, M so solvers have something to work at
    ns.l0(k)<< Meq.Parm(l[k-1]+0.00005,node_groups='Parm')
    ns.m0(k)<< Meq.Parm(m[k-1]-0.00005,node_groups='Parm')
    ns.lm(k)<<Meq.Composer(ns.l0(k),ns.m0(k))
    ns.compounder(k)<<Meq.Compounder(children=[ns.lm(k),ns.resampler(k)],common_axes=[hiid('l'),hiid('m')])
    ns.condeq(k)<<Meq.Condeq(children=(ns.compounder(k), 1))
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

# Make cells array
  cells = meq.cells(meq.domain(f0,f1,t0,t1),num_freq=1,num_time=1);

# define request
  request = meq.request(cells,rqtype='e1')
# execute request
  mqs.meq('Node.Execute',record(name='req_mux',request=request),wait=True);

#####################################################################

if __name__=='__main__':
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
  
