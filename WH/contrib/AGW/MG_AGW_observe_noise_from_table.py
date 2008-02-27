#!/usr/bin/python

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


# Short description:
# A script to generate noise visibilities from FPA observations with 
# weightings obtained from input mep table

# History:
# - 23 Jan 2007: creation:

#=======================================================================
# Import of Python / TDL modules:

import math
import random
import os

from numarray import *

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meqds
from Timba.Meq import meq

try:
  from pyrap_tables import *
except:
  try:
    from pycasatable import *
  except:
    has_table_interface = False
    exit

# setup a bookmark for display of results with a 'Collections Plotter'
Settings.forest_state = record(bookmarks=[
  record(name='Collector',page=[
    record(udi="/node/collector",viewer="Collections Plotter",pos=(0,0)),
    record(udi="/node/inspect_predicts",viewer="Collections Plotter",pos=(1,0))])]);
# to force caching put 100
Settings.forest_state.cache_policy = 100

# Attempt to 'form' a Gaussian beam?
TDLCompileOption('use_gauss','Use Gaussian weights from mep table?',[False,True])

# define antenna list
ANTENNAS = range(1,31);

# derive interferometer list
IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ];

# default flux
I = 1; Q = .0; U = .0; V = .0

# input table with beam weights 
mep_beam_weights = 'beam_weights.mep'
#mep_beam_weights = 'beam_weights_0_0_conj.mep'

# first load weights data from aips++ 'mep ' table
# we read the values directly from the
# table because the MG_AGW_store_beam_weights.py
# script will store two sets of values if
# gaussian fitting is done.
# The weights are stored in a list for further processing

t = table(mep_beam_weights)
print 'loading weights'
row_number = -1
weight_re = []
weight_im = []
status = True
I_parm_max = 1.0
if use_gauss:
  add_weight = False
  while status:
    row_number = row_number + 1
    try:
      name = t.getcell('NAME', row_number)
    except:
      status = False
    if not add_weight:
      if name.find('I_parm_max') > -1:
        add_weight = True
    else:
      try: 
        if name.find('I_parm_max_g') > -1:
          I_parm_max = t.getcell('VALUES',row_number)[0][0]
          status = False
        else:
          weight_re.append(t.getcell('VALUES',row_number)[0][0])
          row_number = row_number + 1
          name = t.getcell('NAME', row_number)
          weight_im.append(t.getcell('VALUES',row_number)[0][0])
      except:
        status = False
else:
  add_weight = True
  while status:
    row_number = row_number + 1
    try:
      name = t.getcell('NAME', row_number)
    except:
      status = False
    if add_weight:
      if name.find('I_parm_max') > -1:
        I_parm_max = t.getcell('VALUES',row_number)[0][0]
        add_weight = False
        status = False
      else:
        try: 
          weight_re.append(t.getcell('VALUES',row_number)[0][0])
          row_number = row_number + 1
          name = t.getcell('NAME', row_number)
          weight_im.append(t.getcell('VALUES',row_number)[0][0])
        except:
          status = False
t.close()

# random number seed value - used so we will generate the same
# sequence of random numbers for each run of the script
#random_seed = random.uniform(0, 4096)
random_seed = 154321

########################################################
def _define_forest(ns):

# read in beam weights
  num_beams = len(weight_re) / 2
  BEAMS = range(0,num_beams)
  beam_counter = -1
  # read in all x weights first
  for k in BEAMS:
    beam_counter = beam_counter + 1
    ns.beam_wt_re_x(k) << Meq.Constant(weight_re[beam_counter])
    ns.beam_wt_im_x(k) << Meq.Constant(weight_im[beam_counter])
    ns.beam_weight_x(k) << Meq.ToComplex(ns.beam_wt_re_x(k), ns.beam_wt_im_x(k))

  # now read in y weights first and compute weighted noise
  for k in BEAMS:
    beam_counter = beam_counter + 1
    ns.beam_wt_re_y(k) << Meq.Constant(weight_re[beam_counter])
    ns.beam_wt_im_y(k) << Meq.Constant(weight_im[beam_counter])
    ns.beam_weight_y(k) << Meq.ToComplex(ns.beam_wt_re_y(k), ns.beam_wt_im_y(k))

    for p in ANTENNAS:

      # G Jones for x and y dipoles = random noise (complex)
      ns.gauss_xr(p,k) << Meq.GaussNoise(stddev=0.1,seed=random_seed)
      ns.gauss_xi(p,k) << Meq.GaussNoise(stddev=0.1,seed=random_seed)
      # G Jones for y dipole = random noise
      ns.gauss_yr(p,k) << Meq.GaussNoise(stddev=0.1,seed=random_seed)
      ns.gauss_yi(p,k) << Meq.GaussNoise(stddev=0.1,seed=random_seed)

      ns.Gxn(p,k) << Meq.ToComplex(ns.gauss_xr(p,k), ns.gauss_xi(p,k))
      ns.Gyn(p,k) << Meq.ToComplex(ns.gauss_yr(p,k), ns.gauss_yi(p,k))
      # weighted x and y noisy G-Jones for one FPA beam
      ns.Gxw(p,k) << ns.Gxn(p,k) * ns.beam_weight_x(k)
      ns.Gyw(p,k) << ns.Gyn(p,k) * ns.beam_weight_y(k)

  # summed weights for normalization 
  ns.sum_wt_x << Meq.Add(*[ns.beam_weight_x(k) for k in BEAMS])
  ns.sum_wt_y << Meq.Add(*[ns.beam_weight_y(k) for k in BEAMS])

  for p in ANTENNAS:
    # sum up weighted 'noisy' gains
    ns.Gx_n(p) << Meq.Add(*[ns.Gxw(p,k) for k in BEAMS]) / ns.sum_wt_x
    ns.Gy_n(p) << Meq.Add(*[ns.Gyw(p,k) for k in BEAMS]) / ns.sum_wt_y

    # we can now create the full 2 x 2 G Jones and its complex conjugate
    ns.G_n(p) << Meq.Matrix22(ns.Gx_n(p), 0.0, 0.0, ns.Gy_n(p))
    ns.Gt_n(p) << Meq.ConjTranspose(ns.G_n(p))

  # gains display - the Composer node collects data for the
  # gains of the individual antennas together for display as
  # a function of time by the Collections Plotter - see the
  # bookmark set up near the beginning of the script
  ns.collector << Meq.Composer(dims=[0], tab_label = 'XNTD',
                  *[ns.G_n(p) for p in ANTENNAS]);

  # now define predicted visibilities, and attach to sinks for writing out
  # to the measurement set. We just calculate the measurement equation
  # for each source and interferometer pair though the MatrixMultiply
  # node 
  for p,q in IFRS:
    # make a predict that includes the time-variable randomized G Jones 
    ns.predict(p,q) << Meq.MatrixMultiply(ns.G_n(p),ns.Gt_n(q)) / I_parm_max 
    ns.sink(p,q) << Meq.Sink(ns.predict(p,q),station_1_index=p-1,station_2_index=q-1,output_col='DATA');

  # node to show visibilities for the output predicts
  ns.inspect_predicts << Meq.Composer(
     dims=[0],
     plot_label=["%s-%s"%(p,q) for p,q in IFRS],
     *[ns.predict(p,q) for p,q in IFRS]
  );

  # and thats it. Finally we define a VisDataMux node which essentially
  # has the sinks as implicit children. When we send a request
  # to the VisDataMux node in the _test_forest function below, it
  # sends requests to the sinks, which then propagate requests through
  # the tree ....
  ns.vdm << Meq.VisDataMux(pre=ns.collector,post=ns.inspect_predicts,*[ns.sink(p,q) for p,q in IFRS]);


########################################################################

def _test_forest(mqs,parent,wait=True):

# now observe sources - tells the system which MS to use and
# which column is to be used to write out our simulated observation
  req = meq.request();
  req.input = record(
    ms = record(
#     ms_name          = 'TEST_XNTD_30_960.MS',
      ms_name          = 'TEST_XNTD_60_480.MS',
      tile_size        = 480,
      selection = record(channel_start_index=0,
                             channel_end_index=0,
                             channel_increment=1,
                             selection_string='')
    ),
    python_init = 'Meow.ReadVisHeader'
  );
  req.output = record(
    ms = record(
      data_column = 'CORRECTED_DATA'
    )
  );
  # execute
  mqs.execute('vdm',req,wait);

if __name__ == '__main__':
 # run in batch mode?
 if '-run' in sys.argv:
   from Timba.Apps import meqserver
   from Timba.TDL import Compile

   # this starts a kernel.
   mqs = meqserver.default_mqs(wait_init=10);

   # This compiles a script as a TDL module. Any errors will be thrown as
   # an exception, so this always returns successfully. We pass in
   # __file__ so as to compile ourselves.
   (mod,ns,msg) = Compile.compile_file(mqs,__file__);

   # this runs the _test_forest job.
   mod._test_forest(mqs,None,wait=True);
   print 'finished'
   sys.exit()
 else:
# Timba.TDL._dbg.set_verbose(5);
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())

