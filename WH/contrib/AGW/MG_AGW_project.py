#!/usr/bin/python


#% $Id: MG_AGW_project.py 3929 2006-09-01 20:17:51Z twillis $ 

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

script_name = 'MG_AGW_project.py'

# Short description:
#  The script should just read in a 2-D array of points from a
#  FITS file and assign them to a FITSImage, which is independent of 
#  time and frequency, but knows about L and M.

# History:
# - 24 Oct 2006: creation:

#=======================================================================
# Import of Python / TDL modules:

import math
import random

from Timba.Trees import JEN_bookmarks

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meq

# Scripts needed to run a MG_JEN script:
from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state
from Timba.Contrib.MXM import MG_MXM_functional
from Timba.Contrib.JEN.util import JEN_bookmarks


# to force caching put 100
Settings.forest_state.cache_policy = 100


########################################################
def _define_forest(ns):  
    
 home_dir = os.environ['HOME']
 BEAMS = range(1,26)

 # L,M coordinates
 l=0.0
 m=0.0

 for k in BEAMS:
   infile_name = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(k) + '.fits'
   ns.image(k) << Meq.FITSImage(filename=infile_name,cutoff=1.0,mode=2)
   ns.resampler(k) << Meq.Resampler(ns.image(k))
   ns.l0(k)<< Meq.Parm(l,node_groups='Parm')
   ns.m0(k)<< Meq.Parm(m,node_groups='Parm')

 # this will generate the LM grid
   ns.lm(k)<<Meq.Composer(ns.l0(k), ns.m0(k))
   ns.y(k)<<Meq.Compounder(children=[ns.lm(k),ns.resampler(k)],common_axes=[hiid('l'),hiid('m')])
 ns['combined'] << Meq.Add(*[ns.y(k) for k in BEAMS])
 ns['result'] <<  ns['combined'] / 26


########################################################################

def _test_forest(mqs,parent):

# any old time and frequency domain will do
# time - cover one day
  t0 = 0.5;
  t1 = 1.5

# any old frequency
  f1 = 1.5
  f0 = 0.5

####
# Make cells array - a period of one day divided into 120 segments

  cells = meq.cells(meq.domain(f0,f1,t0,t1),num_freq=2,num_time=2);

# define request
  request = meq.request(cells,rqtype='e1')
# execute request
  mqs.meq('Node.Execute',record(name='result',request=request),wait=True);
   

#####################################################################

if __name__=='__main__':
  ns=NodeScope()
  define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
  
