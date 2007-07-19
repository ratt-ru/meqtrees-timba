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

# setup a bookmark for display of results with a 'Collections Plotter'
Settings.forest_state = record(bookmarks=[
  record(name='Collector',page=[
    record(udi="/node/collector",viewer="Collections Plotter",pos=(0,0)),
    record(udi="/node/inspect_predicts",viewer="Collections Plotter",pos=(1,0))])]);
# to force caching put 100
Settings.forest_state.cache_policy = 100

# define antenna list
ANTENNAS = range(1,11);
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
delta = 0.0035
l = -3.0 * delta
#l = 3.0 * delta
# define request
for i in range(5):
  m = -0.0105
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
# define location for phase-up
offset = 0.01414214

mep_beam_weights = 'beam_weights.mep'

def create_gain_invariable_beams(ns):
# read in beam images
  BEAMS = range(0,30)
  home_dir = os.environ['HOME']
  for k in BEAMS:
  # read in beam data - y dipole
    infile_name_re_yx = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa/fpa_pat_' + str(k+30) + '_Re_x.fits'
    infile_name_im_yx = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa/fpa_pat_' + str(k+30) +'_Im_x.fits'
    infile_name_re_yy = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa/fpa_pat_' + str(k+30) +'_Re_y.fits'
    infile_name_im_yy = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa/fpa_pat_' + str(k+30) +'_Im_y.fits' 
    ns.image_re_yx(k) << Meq.FITSImage(filename=infile_name_re_yx,cutoff=1.0,mode=2)
    ns.image_im_yx(k) << Meq.FITSImage(filename=infile_name_im_yx,cutoff=1.0,mode=2)
    ns.image_re_yy(k) << Meq.FITSImage(filename=infile_name_re_yy,cutoff=1.0,mode=2)
    ns.image_im_yy(k) << Meq.FITSImage(filename=infile_name_im_yy,cutoff=1.0,mode=2)
    # normalize
    ns.y_im_sq(k) << ns.image_re_yy(k) * ns.image_re_yy(k) + ns.image_im_yy(k) * ns.image_im_yy(k) +\
                  ns.image_re_yx(k) * ns.image_re_yx(k) + ns.image_im_yx(k) * ns.image_im_yx(k)
    ns.y_im(k) <<Meq.Sqrt(ns.y_im_sq(k))
    ns.y_im_max(k) <<Meq.Max(ns.y_im(k))
    ns.norm_image_re_yy(k) << ns.image_re_yy(k) / ns.y_im_max(k)
    ns.norm_image_im_yy(k) << ns.image_im_yy(k) / ns.y_im_max(k)
    ns.norm_image_re_yx(k) << ns.image_re_yx(k) / ns.y_im_max(k)
    ns.norm_image_im_yx(k) << ns.image_im_yx(k) / ns.y_im_max(k)

    ns.beam_wt_re_y(k) << Meq.Parm(table_name =  mep_beam_weights)
    ns.beam_wt_im_y(k) << Meq.Parm(table_name =  mep_beam_weights)

    ns.beam_weight_y(k) << Meq.ToComplex(ns.beam_wt_re_y(k), ns.beam_wt_im_y(k))

    ns.beam_yx(k) << Meq.ToComplex(ns.norm_image_re_yx(k), ns.norm_image_im_yx(k)) 
    ns.beam_yy(k) << Meq.ToComplex(ns.norm_image_re_yy(k), ns.norm_image_im_yy(k))
    ns.wt_beam_yx(k) << ns.beam_yx(k) * ns.beam_weight_y(k)
    ns.wt_beam_yy(k) << ns.beam_yy(k) * ns.beam_weight_y(k)

  # read in beam data - x dipole
    infile_name_re_xx = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa/fpa_pat_' + str(k) + '_Re_x.fits'
    infile_name_im_xx = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa/fpa_pat_' + str(k) +'_Im_x.fits'
    infile_name_re_xy = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa/fpa_pat_' + str(k) +'_Re_y.fits'
    infile_name_im_xy = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa/fpa_pat_' + str(k) +'_Im_y.fits' 
    ns.image_re_xy(k) << Meq.FITSImage(filename=infile_name_re_xy,cutoff=1.0,mode=2)
    ns.image_im_xy(k) << Meq.FITSImage(filename=infile_name_im_xy,cutoff=1.0,mode=2)
    ns.image_re_xx(k) << Meq.FITSImage(filename=infile_name_re_xx,cutoff=1.0,mode=2)
    ns.image_im_xx(k) << Meq.FITSImage(filename=infile_name_im_xx,cutoff=1.0,mode=2)

    # normalize
    ns.x_im_sq(k) << ns.image_re_xx(k) * ns.image_re_xx(k) + ns.image_im_xx(k) * ns.image_im_xx(k) +\
                  ns.image_re_xy(k) * ns.image_re_xy(k) + ns.image_im_xy(k) * ns.image_im_xy(k)
    ns.x_im(k) <<Meq.Sqrt(ns.x_im_sq(k))
    ns.x_im_max(k) <<Meq.Max(ns.x_im(k))
    ns.norm_image_re_xx(k) << ns.image_re_xx(k) / ns.x_im_max(k)
    ns.norm_image_im_xx(k) << ns.image_im_xx(k) / ns.x_im_max(k)
    ns.norm_image_re_xy(k) << ns.image_re_xy(k) / ns.x_im_max(k)
    ns.norm_image_im_xy(k) << ns.image_im_xy(k) / ns.x_im_max(k)

    ns.beam_wt_re_x(k) << Meq.Parm(table_name =  mep_beam_weights)
    ns.beam_wt_im_x(k) << Meq.Parm(table_name =  mep_beam_weights)

    ns.beam_weight_x(k) << Meq.ToComplex(ns.beam_wt_re_x(k), ns.beam_wt_im_x(k))

    ns.beam_xy(k) << Meq.ToComplex(ns.norm_image_re_xy(k), ns.norm_image_im_xy(k)) 
    ns.beam_xx(k) << Meq.ToComplex(ns.norm_image_re_xx(k), ns.norm_image_im_xx(k))
    ns.wt_beam_xy(k) << ns.beam_xy(k) * ns.beam_weight_x(k)
    ns.wt_beam_xx(k) << ns.beam_xx(k) * ns.beam_weight_x(k)

  ns.voltage_sum_xx << Meq.Add(*[ns.wt_beam_xx(k) for k in BEAMS])
  ns.voltage_sum_xy << Meq.Add(*[ns.wt_beam_xy(k) for k in BEAMS])
  ns.voltage_sum_yx << Meq.Add(*[ns.wt_beam_yx(k) for k in BEAMS])
  ns.voltage_sum_yy << Meq.Add(*[ns.wt_beam_yy(k) for k in BEAMS])

  # normalize beam to peak response
  ns.voltage_sum_xx_r << Meq.Real(ns.voltage_sum_xx)
  ns.voltage_sum_xx_i << Meq.Imag(ns.voltage_sum_xx)
  ns.voltage_sum_xy_r << Meq.Real(ns.voltage_sum_xy)
  ns.voltage_sum_xy_i << Meq.Imag(ns.voltage_sum_xy)

  ns.im_sq_x << ns.voltage_sum_xx_r * ns.voltage_sum_xx_r + ns.voltage_sum_xx_i * ns.voltage_sum_xx_i +\
                  ns.voltage_sum_xy_r * ns.voltage_sum_xy_r + ns.voltage_sum_xy_i * ns.voltage_sum_xy_i
  ns.im_x <<Meq.Sqrt(ns.im_sq_x)
  ns.im_x_max <<Meq.Max(ns.im_x)

  ns.voltage_sum_yy_r << Meq.Real(ns.voltage_sum_yy)
  ns.voltage_sum_yy_i << Meq.Imag(ns.voltage_sum_yy)
  ns.voltage_sum_yx_r << Meq.Real(ns.voltage_sum_yx)
  ns.voltage_sum_yx_i << Meq.Imag(ns.voltage_sum_yx)
  ns.im_sq_y << ns.voltage_sum_yy_r * ns.voltage_sum_yy_r + ns.voltage_sum_yy_i * ns.voltage_sum_yy_i +\
                  ns.voltage_sum_yx_r * ns.voltage_sum_yx_r + ns.voltage_sum_yx_i * ns.voltage_sum_yx_i
  ns.im_y <<Meq.Sqrt(ns.im_sq_y)
  ns.im_y_max <<Meq.Max(ns.im_y)

  ns.voltage_sum_yy_norm << ns.voltage_sum_yy / ns.im_y_max
  ns.voltage_sum_yx_norm << ns.voltage_sum_yx / ns.im_y_max

  ns.voltage_sum_xx_norm << ns.voltage_sum_xx / ns.im_x_max
  ns.voltage_sum_xy_norm << ns.voltage_sum_xy / ns.im_x_max


  #  We have E_Jones with no time dependent gain variation
  ns.E << Meq.Matrix22(ns.voltage_sum_xx_norm, ns.voltage_sum_yx_norm,ns.voltage_sum_xy_norm, ns.voltage_sum_yy_norm)
  # we will need a resampler for the beam in order to extract the
  # actual E-Jones in the directions of each of the sources. The dep_mask
  # flag is yet another of those mysterious thingys needed by Sarod ...
  ns.resampler_E << Meq.Resampler(ns.E, dep_mask=0xff)

def create_gain_variable_beams(ns):
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
    # 24 hr daily cycle
      ns.daily_gain_x(p,k) << 1.0 + 0.005 * Meq.Cos(ns.phase_offset_day_x(p,k))

    # then, calculate phase and then hourly gain fluctuation 
    # for the 0.1 % hourly cycle
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

      ns.wt_beam_yx(p,k) << ns.wt_beam_yx(k) * ns.Gy(p,k)
      ns.wt_beam_yy(p,k) << ns.wt_beam_yy(k) * ns.Gy(p,k)

      ns.wt_beam_xy(p,k) << ns.wt_beam_xy(k) * ns.Gx(p,k)
      ns.wt_beam_xx(p,k) << ns.wt_beam_xx(k) * ns.Gx(p,k)

    # first, daily variation for x dipole
    ns.voltage_sum_xx(p) << Meq.Add(*[ns.wt_beam_xx(p,k) for k in BEAMS])
    ns.voltage_sum_xy(p) << Meq.Add(*[ns.wt_beam_xy(p,k) for k in BEAMS])
    ns.voltage_sum_yx(p) << Meq.Add(*[ns.wt_beam_yx(p,k) for k in BEAMS])
    ns.voltage_sum_yy(p) << Meq.Add(*[ns.wt_beam_yy(p,k) for k in BEAMS])

  # normalize beam to peak response
    ns.voltage_sum_xx_r(p) << Meq.Real(ns.voltage_sum_xx(p))
    ns.voltage_sum_xx_i(p) << Meq.Imag(ns.voltage_sum_xx(p))
    ns.voltage_sum_xy_r(p) << Meq.Real(ns.voltage_sum_xy(p))
    ns.voltage_sum_xy_i(p) << Meq.Imag(ns.voltage_sum_xy(p))

    ns.im_sq_x(p) << ns.voltage_sum_xx_r(p) * ns.voltage_sum_xx_r(p) + ns.voltage_sum_xx_i(p) * ns.voltage_sum_xx_i(p) +\
                  ns.voltage_sum_xy_r(p) * ns.voltage_sum_xy_r(p) + ns.voltage_sum_xy_i(p) * ns.voltage_sum_xy_i(p)
    ns.im_x(p) <<Meq.Sqrt(ns.im_sq_x(p))
    ns.im_x_max(p) <<Meq.Max(ns.im_x(p))

    ns.voltage_sum_yy_r(p) << Meq.Real(ns.voltage_sum_yy(p))
    ns.voltage_sum_yy_i(p) << Meq.Imag(ns.voltage_sum_yy(p))
    ns.voltage_sum_yx_r(p) << Meq.Real(ns.voltage_sum_yx(p))
    ns.voltage_sum_yx_i(p) << Meq.Imag(ns.voltage_sum_yx(p))
    ns.im_sq_y(p) << ns.voltage_sum_yy_r(p) * ns.voltage_sum_yy_r(p) + ns.voltage_sum_yy_i(p) * ns.voltage_sum_yy_i(p) +\
                  ns.voltage_sum_yx_r(p) * ns.voltage_sum_yx_r(p) + ns.voltage_sum_yx_i(p) * ns.voltage_sum_yx_i(p)
    ns.im_y(p) <<Meq.Sqrt(ns.im_sq_y(p))
    ns.im_y_max(p) <<Meq.Max(ns.im_y(p))

    ns.voltage_sum_yy_norm(p) << ns.voltage_sum_yy(p) / ns.im_y_max(p)
    ns.voltage_sum_yx_norm(p) << ns.voltage_sum_yx(p) / ns.im_y_max(p)

    ns.voltage_sum_xx_norm(p) << ns.voltage_sum_xx(p) / ns.im_x_max(p)
    ns.voltage_sum_xy_norm(p) << ns.voltage_sum_xy(p) / ns.im_x_max(p)

  #  We have E_Jones with time dependent gain variation
    ns.E(p) << Meq.Matrix22(ns.voltage_sum_xx_norm(p), ns.voltage_sum_yx_norm(p),ns.voltage_sum_xy_norm(p), ns.voltage_sum_yy_norm(p))
  # we will need a resampler for the beam in order to extract the
  # actual E-Jones in the directions of each of the sources. The dep_mask
  # flag is yet another of those mysterious thingys needed by Sarod ...
    ns.resampler_E(p) << Meq.Resampler(ns.E(p), dep_mask=0xff)

########################################################
def _define_forest(ns):  
  create_gain_invariable_beams(ns)
  create_gain_variable_beams(ns)
 
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
    l0,m0 = LM[src];
    l = l0 + offset
    m = m0 + offset
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

# define K-jones matrices - just derive the phase shift, and the
# its complex conjugate for each antenna  / source combination
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

def _test_forest(mqs,parent):

# now observe sources - tells the system which MS to use and
# which column is to be used to write out our simulated observation
  req = meq.request();
  req.input = record(
    ms = record(
      ms_name          = 'TEST_XNTD_30_960.MS',
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
  mqs.execute('vdm',req,wait=False);


if __name__=='__main__':
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
  
