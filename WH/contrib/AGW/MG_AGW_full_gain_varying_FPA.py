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
#  A script to simulate daily variations in the gains of a focal plane array

# History:
# - 23 Jan 2007: creation:

#=======================================================================
# Import of Python / TDL modules:

import math
import random
import numarray
import os

from numarray import *

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meqds
from Timba.Meq import meq

from handle_beams import * 
from MG_AGW_read_separate_table_weights import *

# get directory with GRASP focal plane array beams
#TDLCompileOption('fpa_directory','directory with focal plane array files',['gauss_array_pats','gauss_array_pats_offset','gauss_array_pats_defocus','veidt_fpa_180', 'veidt_fpa_30'],more=str)

fpa_directory = 'veidt_fpa_30'

# setup a bookmark for display of results with a 'Collections Plotter'
Settings.forest_state = record(bookmarks=[
  record(name='Collector',page=[
#   record(udi="/node/collector",viewer="Collections Plotter",pos=(0,0)),
    record(udi="/node/inspect_predicts",viewer="Collections Plotter",pos=(1,0))])]);
# to force caching put 100
#Settings.forest_state.cache_policy = 100

l_beam = 0
m_beam = 0
use_gauss = True

# define antenna list
ANTENNAS = range(1,31);
BEAMS = range(0,30)

# derive interferometer list
IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ];

# default flux
I = 1; Q = .0; U = .0; V = .0

# create pseudo-gain phase offsets for individual antennas and dipoles
full_seconds_day = 86400 # number of seconds in day
seconds_hour = 3600 # number of seconds in hour - for hourly cycle
seconds_day = 2 * seconds_hour# simulate daily cycle offset 
                              # from first two hours of the observation -
                              # I have no idea at the moment how
                              # to easily get local time of an observation
                              # from an MS ...
ant_phase_day_x = numarray.zeros((30,30),numarray.Float32)
ant_phase_hour_x = numarray.zeros((30,30),numarray.Float32)
for p in ANTENNAS:
  for k in BEAMS:
    sample_day = random.random()
    ant_phase_day_x[p-1,k] = sample_day * seconds_day
    sample_hour = random.random()
    ant_phase_hour_x[p-1,k] = sample_hour * seconds_hour

ant_phase_day_y = numarray.zeros((30,30),numarray.Float32)
ant_phase_hour_y = numarray.zeros((30,30),numarray.Float32)
for p in ANTENNAS:
  for k in BEAMS:
    sample_day = random.random()
    ant_phase_day_y[p-1,k] = sample_day * seconds_day
    sample_hour = random.random()
    ant_phase_hour_y[p-1,k] = sample_hour * seconds_hour

# we'll put the sources on a 5x5 grid (positions relative to 
# the phase centre, in radians)

LM = []
delta = 0.02081 * 0.5
l = -3.0 * delta
#l = 0
#m = -3.0 * delta
# define request
for i in range(5):
  m = -3.0 * delta 
  l = l + delta
  for j in range(5):
    m = m + delta
    LM.append((l,m))


#for i in range(25):
#  l = random.uniform(-0.007,0.007)
#  m = random.uniform(-0.007,0.007)
# flux = random.randint(1,100)
# source_parms = (l,m,float(flux))
#  source_parms = (l,m)
#  LM.append(source_parms)

#print 'LM ', LM

SOURCES = range(len(LM));       # 0...N-1

def create_gain_invariable_beams(num_beams, I_parm_max_x,I_parm_max_y,weight_re,weight_im, ns):

  BEAMS = range(0,num_beams)

# get complex weights for beams
  for k in BEAMS:
    ns.beam_wt_re_x(k) << Meq.Constant(weight_re['beam_wt_re_x:'+ str(k)])
    ns.beam_wt_im_x(k) << Meq.Constant(weight_im['beam_wt_im_x:'+ str(k)])
    ns.beam_weight_x(k) << Meq.ToComplex(ns.beam_wt_re_x(k), ns.beam_wt_im_x(k))

  for k in BEAMS:
    ns.beam_wt_re_y(k) << Meq.Constant(weight_re['beam_wt_re_y:'+ str(k)])
    ns.beam_wt_im_y(k) << Meq.Constant(weight_im['beam_wt_im_y:'+ str(k)])
    ns.beam_weight_y(k) << Meq.ToComplex(ns.beam_wt_re_y(k), ns.beam_wt_im_y(k))

# form a beam
  for k in BEAMS:
    ns.beam_xy(k) << Meq.ToComplex(ns.image_re_xy(k), ns.image_im_xy(k))
    ns.beam_xx(k) << Meq.ToComplex(ns.image_re_xx(k), ns.image_im_xx(k))
    ns.wt_beam_xy(k) << ns.beam_xy(k) * ns.beam_weight_x(k)
    ns.wt_beam_xx(k) << ns.beam_xx(k) * ns.beam_weight_x(k)

    ns.beam_yx(k) << Meq.ToComplex(ns.image_re_yx(k), ns.image_im_yx(k))
    ns.beam_yy(k) << Meq.ToComplex(ns.image_re_yy(k), ns.image_im_yy(k))
    ns.wt_beam_yx(k) << ns.beam_yx(k) * ns.beam_weight_y(k)
    ns.wt_beam_yy(k) << ns.beam_yy(k) * ns.beam_weight_y(k)

  # sum up the weights
  ns.wt_sum_x << Meq.Add(*[ns.beam_weight_x(k) for k in BEAMS])
  ns.wt_sum_y << Meq.Add(*[ns.beam_weight_y(k) for k in BEAMS])

  # sum beams up and normalize by the summed weights
  ns.voltage_sum_xx_norm << Meq.Add(*[ns.wt_beam_xx(k) for k in BEAMS]) / (ns.wt_sum_x * I_parm_max_x) 
  ns.voltage_sum_xy_norm << Meq.Add(*[ns.wt_beam_xy(k) for k in BEAMS]) / (ns.wt_sum_x * I_parm_max_x) 
  ns.voltage_sum_yx_norm << Meq.Add(*[ns.wt_beam_yx(k) for k in BEAMS]) / (ns.wt_sum_y * I_parm_max_y)
  ns.voltage_sum_yy_norm << Meq.Add(*[ns.wt_beam_yy(k) for k in BEAMS]) / (ns.wt_sum_y * I_parm_max_y)

  ns.E << Meq.Matrix22(ns.voltage_sum_xx_norm, ns.voltage_sum_xy_norm, ns.voltage_sum_yx_norm, ns.voltage_sum_yy_norm)

  # we will need a resampler for the beam in order to extract the
  # actual E-Jones in the directions of each of the sources. The dep_mask
  # flag is yet another of those mysterious thingys needed by Sarod ...
  ns.resampler_E << Meq.Resampler(ns.E, dep_mask=0xff)

def create_gain_variable_beams(I_parm_max_x, I_parm_max_y, ns):
  for p in ANTENNAS:
    # Now, create antenna-based time-dependent gain variations
    # first, daily variation for x dipole
    # the Time node will give us the time of each of the sequence of
    # data points we are working with.
    for k in BEAMS:

    # first calculate the phase at this moment in time
      ns.offset_day_x(p,k) << Meq.Time() - ant_phase_day_x[p-1,k]
      ns.phase_offset_day_x(p,k) << (ns.offset_day_x(p,k) *2* math.pi) / full_seconds_day 
    # now compute the actual gain variation of an antenna for the 
    # 0.5% 24 hr daily cycle
      ns.daily_gain_x(p,k) << 1.0 + 0.005 * Meq.Cos(ns.phase_offset_day_x(p,k))

    # then, calculate phase and then hourly gain fluctuation 
    # for the 0.05% hourly cycle
      ns.offset_hour_x(p,k) << Meq.Time() - ant_phase_hour_x[p-1,k]
      ns.phase_offset_hr_x(p,k) << (ns.offset_hour_x(p,k) *2* math.pi) /  seconds_hour
      ns.hourly_gain_x(p,k) << 0.0005 * Meq.Cos(ns.phase_offset_hr_x(p,k))

    # G Jones for x dipole = sum of daily and hourly gain
      ns.Gx(p,k) << ns.daily_gain_x(p,k) + ns.hourly_gain_x(p,k) 

    # now do the same sequence of calculations for the y dipole
    # first, daily cycle
      ns.offset_day_y(p,k) << Meq.Time() - ant_phase_day_y[p-1,k]
      ns.phase_offset_day_y(p,k) << (ns.offset_day_y(p,k) *2* math.pi) / full_seconds_day 
      ns.daily_gain_y(p,k) << 1.0 + 0.005 * Meq.Cos(ns.phase_offset_day_y(p,k))

    # then, hourly fluctuation 
      ns.offset_hour_y(p,k) << Meq.Time() - ant_phase_hour_y[p-1,k]
      ns.phase_offset_hr_y(p,k) << (ns.offset_hour_y(p,k) *2* math.pi) /  seconds_hour
      ns.hourly_gain_y(p,k) << 0.0005 * Meq.Cos(ns.phase_offset_hr_y(p,k))

    # G Jones for y dipole = sum of daily and hourly gain
      ns.Gy(p,k) << ns.daily_gain_y(p,k) + ns.hourly_gain_y(p,k) 

      ns.wt_beam_yx_vary(p,k) << ns.wt_beam_yx(k) * ns.Gy(p,k)
      ns.wt_beam_yy_vary(p,k) << ns.wt_beam_yy(k) * ns.Gy(p,k)

      ns.wt_beam_xy_vary(p,k) << ns.wt_beam_xy(k) * ns.Gx(p,k)
      ns.wt_beam_xx_vary(p,k) << ns.wt_beam_xx(k) * ns.Gx(p,k)

    # first, daily variation for x dipole
    # sum beams up and normalize by the summed weights
    ns.voltage_sum_xx_norm_vary(p) << Meq.Add(*[ns.wt_beam_xx_vary(p,k) for k in BEAMS]) / (ns.wt_sum_x * I_parm_max_x) 
    ns.voltage_sum_xy_norm_vary(p) << Meq.Add(*[ns.wt_beam_xy_vary(p,k) for k in BEAMS]) / (ns.wt_sum_x * I_parm_max_x) 
    ns.voltage_sum_yx_norm_vary(p) << Meq.Add(*[ns.wt_beam_yx_vary(p,k) for k in BEAMS]) / (ns.wt_sum_y * I_parm_max_y)
    ns.voltage_sum_yy_norm_vary(p) << Meq.Add(*[ns.wt_beam_yy_vary(p,k) for k in BEAMS]) / (ns.wt_sum_y * I_parm_max_y)

    ns.E(p) << Meq.Matrix22(ns.voltage_sum_xx_norm_vary(p), ns.voltage_sum_xy_norm_vary(p), ns.voltage_sum_yx_norm_vary(p), ns.voltage_sum_yy_norm_vary(p))

    ns.resampler_E(p) << Meq.Resampler(ns.E(p), dep_mask=0xff)

########################################################
def _define_forest(ns):  

# read in beam images
# number of beams is 30 or 90
  num_beams = read_in_FPA_beams(ns,fpa_directory)
  print 'num_beams = ', num_beams

#read in weights for system
  I_parm_max_x,I_parm_max_y,weight_re,weight_im = read_separate_table_weights(l_beam, m_beam, use_gauss)

  create_gain_invariable_beams(num_beams,I_parm_max_x,I_parm_max_y,weight_re,weight_im,ns)
  create_gain_variable_beams(I_parm_max_x, I_parm_max_y, ns)
 
# OK - we have E Jones - now observe sources

 # first set up nodes for phase center
  ns.radec0 = Meq.Composer(ns.ra<<0,ns.dec<<0);

  # nodes for array reference position
  ns.xyz0 = Meq.Composer(ns.x0<<0,ns.y0<<0,ns.z0<<0);

  # now define per-station stuff: XYZs and UVWs
  for p in ANTENNAS:
    # set up individual positions and uvw
    ns.xyz(p) << Meq.Composer(ns.x(p)<<0,ns.y(p)<<0,ns.z(p)<<0);
    ns.uvw(p) << Meq.Negate(Meq.UVW(radec=ns.radec0,xyz_0=ns.xyz0,xyz=ns.xyz(p)));

  # Now, define individual source e-Jones matrices
  for src in SOURCES:
    l,m = LM[src]
    n = math.sqrt(1-l*l-m*m);
    ns.lmn_minus1(src) << Meq.Composer(l,m,n-1);
    # define source brightness B0 (unprojected)
    ns.B0(src) << 0.5 * Meq.Matrix22(I+Q,Meq.ToComplex(U,V),Meq.ToComplex(U,-V),I-Q)
    # don't really need to use the following for a point source
    ns.B(src) << ns.B0(src) / n;
    ns.lm(src) << Meq.Composer(l,m)

    # the following operation extracts the value of the actual e-Jones
    # in the direction of the individual sources through use of a
    # Compounder node: it has as children the position of the 
    # source and the resampler node mentioned above. The actual
    # operation is a bit mysterious to me - yet another Sarod thingy 
    ns.Es(src)<<Meq.Compounder(children=[ns.lm(src),ns.resampler_E],common_axes=[hiid('l'),hiid('m')],default_cell_size=0.01) 
    # and get the complex conjugate
    ns.Est(src) << Meq.ConjTranspose(ns.Es(src)) 

# Define K-jones matrices - just derive the phase shift, and 
# its complex conjugate for each antenna  / source combination.
# And define antnna-based time variable E-Jones for FPA-based system.
  for p in ANTENNAS:
    for src in SOURCES:
      ns.K(p,src) << Meq.VisPhaseShift(lmn=ns.lmn_minus1(src),uvw=ns.uvw(p));
      ns.Kt(p,src) << Meq.ConjTranspose(ns.K(p,src));
      ns.E(p,src)<<Meq.Compounder(children=[ns.lm(src),ns.resampler_E(p)],common_axes=[hiid('l'),hiid('m')],default_cell_size=0.01) 
    # and get the complex conjugate
      ns.Et(p,src) << Meq.ConjTranspose(ns.E(p,src)) 


  # now define predicted visibilities, and attach to sinks for writing out
  # to the measurement set. We just calculate the measurement equation
  # for each source and interferometer pair though the MatrixMultiply
  # node 
  for p,q in IFRS:
    for src in SOURCES:
      # first make a predict that includes the time-variable G Jones 
      ns.predict(p,q,src) << \
        Meq.MatrixMultiply(ns.E(p,src),ns.K(p,src),ns.B(src),ns.Kt(q,src),ns.Et(q,src));
      # and make a separate predict that has no G Jones, so it is implicitly
      # unity
      ns.predict_ok(p,q,src) << \
        Meq.MatrixMultiply(ns.Es(src),ns.K(p,src),ns.B(src),ns.Kt(q,src),ns.Est(src));
    # and sum up the separate predicts via Add nodes
    predict = ns.predict(p,q) << Meq.Add(*[ns.predict(p,q,src) for src in SOURCES]);
    predict_ok = ns.predict_ok(p,q) << Meq.Add(*[ns.predict_ok(p,q,src) for src in SOURCES]);

    # now we write out visibilities which are the differences between
    # bad (time variable gain and good (no gain error)
    ns.sink(p,q) << Meq.Sink(predict-predict_ok,station_1_index=p-1,station_2_index=q-1,output_col='DATA');
#   ns.sink(p,q) << Meq.Sink(predict,station_1_index=p-1,station_2_index=q-1,output_col='DATA');
#   ns.sink(p,q) << Meq.Sink(predict_ok,station_1_index=p-1,station_2_index=q-1,output_col='DATA');

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
  ns.vdm << Meq.VisDataMux(post=ns.inspect_predicts,*[ns.sink(p,q) for p,q in IFRS]);


########################################################################

def _test_forest(mqs,parent,wait=False):

# now observe sources - tells the system which MS to use and
# which column is to be used to write out our simulated observation
  req = meq.request();
  req.input = record(
    ms = record(
      ms_name          = 'TEST_XNTD_60_480.MS',
      tile_size        = 20,
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
  mqs.execute('vdm',req,wait=wait);


  
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


