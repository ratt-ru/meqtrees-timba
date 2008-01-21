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

# setup a bookmark for display of results with a 'Collections Plotter'
Settings.forest_state = record(bookmarks=[
  record(name='Collector',page=[
    record(udi="/node/collector",viewer="Collections Plotter",pos=(0,0)),
    record(udi="/node/inspect_predicts",viewer="Collections Plotter",pos=(1,0))])]);
# to force caching put 100
Settings.forest_state.cache_policy = 100

# define antenna list
ANTENNAS = range(1,31);

# derive interferometer list
IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ];

# default flux
I = 1; Q = .0; U = .0; V = .0

# input table with beam weights 
mep_beam_weights = 'beam_weights.mep'

# random number seed value - used so we will generate the same
# sequence of random numbers for each run of the script
random_seed = 154321

########################################################
def _define_forest(ns):

# direction of fake source
  l = 0.00543675
  m = 0.00543675

  n = math.sqrt(1-l*l-m*m);
  ns.lmn_minus1 << Meq.Composer(l,m,n-1);

# read in beam weights
  BEAMS = range(0,30)
  for k in BEAMS:
  # read in beam weight data - y dipoles followed by x dipoles
    ns.beam_wt_re_y(k) << Meq.Parm(table_name =  mep_beam_weights)
    ns.beam_wt_im_y(k) << Meq.Parm(table_name =  mep_beam_weights)

    ns.beam_weight_y(k) << Meq.ToComplex(ns.beam_wt_re_y(k), ns.beam_wt_im_y(k))

    ns.beam_wt_re_x(k) << Meq.Parm(table_name =  mep_beam_weights)
    ns.beam_wt_im_x(k) << Meq.Parm(table_name =  mep_beam_weights)

    ns.beam_weight_x(k) << Meq.ToComplex(ns.beam_wt_re_x(k), ns.beam_wt_im_x(k))

    for p in ANTENNAS:

      # G Jones for x dipole = random noise
      ns.gauss_x(p,k) << Meq.GaussNoise(stddev=0.1,seed=random_seed)
      # G Jones for y dipole = random noise
      ns.gauss_y(p,k) << Meq.GaussNoise(stddev=0.1,seed=random_seed)

      # G Jones for x and y dipoles  =  1.0 + random noise
      ns.Gxn(p,k) << 1.0+ ns.gauss_x(p,k)
      ns.Gyn(p,k) << 1.0+ ns.gauss_y(p,k)
      # weighted x and y noisy G-Jones for one FPA beam
      ns.Gxw(p,k) << ns.Gxn(p,k) * ns.beam_weight_x(k)
      ns.Gyw(p,k) << ns.Gyn(p,k) * ns.beam_weight_y(k)

      # weighted x and y noise-free G-Jones for one FPA beam
      ns.Gx(p,k) << 1.0 * ns.beam_weight_x(k) 
      ns.Gy(p,k) << 1.0 * ns.beam_weight_y(k) 
      

  # summed weights for normalization - not presently used
  ns.sum_wt_x << Meq.Add(*[ns.beam_weight_x(k) for k in BEAMS])
  ns.sum_wt_y << Meq.Add(*[ns.beam_weight_y(k) for k in BEAMS])

  for p in ANTENNAS:
    # sum up weighted 'noisy' gains
    ns.Gx_n(p) << Meq.Add(*[ns.Gxw(p,k) for k in BEAMS]) / ns.sum_wt_x
    ns.Gy_n(p) << Meq.Add(*[ns.Gyw(p,k) for k in BEAMS]) / ns.sum_wt_y

    # sum up weighted 'noise-free' gains
    ns.Gx(p) << Meq.Add(*[ns.Gx(p,k) for k in BEAMS]) / ns.sum_wt_x 
    ns.Gy(p) << Meq.Add(*[ns.Gy(p,k) for k in BEAMS]) / ns.sum_wt_y

 # first set up nodes for phase center
  ns.radec0 = Meq.Composer(ns.ra<<0,ns.dec<<0);

  # nodes for array reference position
  ns.xyz0 = Meq.Composer(ns.x0<<0,ns.y0<<0,ns.z0<<0);

  # now define per-station stuff: XYZs and UVWs
  for p in ANTENNAS:
    # set up individual positions and uvw
    ns.xyz(p) << Meq.Composer(ns.x(p)<<0,ns.y(p)<<0,ns.z(p)<<0);
    ns.uvw(p) << Meq.Negate(Meq.UVW(radec=ns.radec0,xyz_0=ns.xyz0,xyz=ns.xyz(p)));
    # NOTE: in the above lines of code since the ns.radec0 = statement
    # we have been creating nodes with placeholder values of zero. These
    # get set to actual values when the statement 
    # python_init = 'Meow.ReadVisHeader' gets executed during the 
    # _test_forest function is called. The state of the above nodes
    # gets updated by contents read in from the MS
    
    # so we can now create the full 2 x 2 G Jones and its
    # complex conjugate
    ns.G_n(p) << Meq.Matrix22(ns.Gx_n(p), 0.0, 0.0, ns.Gy_n(p))
    ns.Gt_n(p) << Meq.ConjTranspose(ns.G_n(p))
    ns.G(p) << Meq.Matrix22(ns.Gx(p), 0.0, 0.0, ns.Gy(p))
    ns.Gt(p) << Meq.ConjTranspose(ns.G(p))

    # define K-jones matrices
    ns.K(p) << Meq.VisPhaseShift(lmn=ns.lmn_minus1,uvw=ns.uvw(p));
    ns.Kt(p) << Meq.ConjTranspose(ns.K(p));

  # gains display - the Composer node collects data for the
  # gains of the individual antennas together for display as
  # a function of time by the Collections Plotter - see the
  # bookmark set up near the beginning of the script
  ns.collector << Meq.Composer(dims=[0], tab_label = 'XNTD',
                  *[ns.G_n(p) for p in ANTENNAS]);


  # define source brightness B0 (unprojected)
  ns.B0 << 0.5 * Meq.Matrix22(I+Q,Meq.ToComplex(U,V),Meq.ToComplex(U,-V),I-Q)

  # now define predicted visibilities, and attach to sinks for writing out
  # to the measurement set. We just calculate the measurement equation
  # for each source and interferometer pair though the MatrixMultiply
  # node 
  for p,q in IFRS:
    # first make a predict that includes the time-variable randomized G Jones 
    predict = ns.predict(p,q) << Meq.MatrixMultiply(ns.G_n(p),ns.K(p),ns.B0,ns.Kt(q),ns.Gt_n(q));
    # and a predict based on noise-free weighted gains
    predict_ok = ns.predict_ok(p,q) << Meq.MatrixMultiply(ns.G(p),ns.K(p),ns.B0,ns.Kt(q),ns.Gt(q));
    # and take the difference between the above two predicts
    ns.predict_diff(p,q) << Meq.Subtract(ns.predict(p,q), ns.predict_ok(p,q))

    # now we write out visibilities which are the differences between
    # bad (noisey gain) and good (noise-free gain)
    ns.sink(p,q) << Meq.Sink(ns.predict_diff(p,q),station_1_index=p-1,station_2_index=q-1,output_col='DATA');
#   ns.sink(p,q) << Meq.Sink(predict,station_1_index=p-1,station_2_index=q-1,output_col='DATA');
#   ns.sink(p,q) << Meq.Sink(predict_ok,station_1_index=p-1,station_2_index=q-1,output_col='DATA');

  # node to show visibilities for the output predicts
  ns.inspect_predicts << Meq.Composer(
     dims=[0],
     plot_label=["%s-%s"%(p,q) for p,q in IFRS],
     *[ns.predict_diff(p,q) for p,q in IFRS]
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
      ms_name          = 'TEST_XNTD_30_960.MS',
      tile_size        = 200,
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
 else:
  Timba.TDL._dbg.set_verbose(5);
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())

