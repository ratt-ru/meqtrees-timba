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
#  A script to implement the MODCAL algorithm (AGW, 1999)

# History:
# - 7 FEB 2007: creation:

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
    record(udi="/node/E_beam",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/collector",viewer="Collections Plotter",pos=(1,0)),
    record(udi="/node/inspect_predicts",viewer="Collections Plotter",pos=(2,0))])]);
# to force caching put 100
Settings.forest_state.cache_policy = 100

# define antenna list
ANTENNAS = range(1,31);

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
ant_phase_day_x = []
ant_phase_hour_x = []
for p in ANTENNAS:
  sample_day = random.random()
  ant_phase_day_x.append(sample_day * seconds_day)
  sample_hour = random.random()
  ant_phase_hour_x.append(sample_hour * seconds_hour)

ant_phase_day_y = []
ant_phase_hour_y = []
for p in ANTENNAS:
  sample_day = random.random()
  ant_phase_day_y.append(sample_day * seconds_day)
  sample_hour = random.random()
  ant_phase_hour_y.append(sample_hour * seconds_hour)

# we want a single test source
LM = []
LM.append((0.015,0.000,10.0)) # source we want to remove -is in a sidelobe
LM.append((0.001,0.001,0.05)) # following sources represent 'field rumble'
LM.append((-0.0005,0.0005,0.09)) 
test_flux = 1.25

#for i in range(25):
#  l = random.uniform(-0.007,0.007)
#  m = random.uniform(-0.007,0.007)
# flux = random.randint(1,100)
# source_parms = (l,m,float(flux))
#  source_parms = (l,m)
#  LM.append(source_parms)

#print 'LM ', LM

SOURCES = range(len(LM));       # 0...N-1

def setup_beams(ns):
  # read in beam images and assign to nodes

  # first read in beam images from FITS files - one file for each 
  # dipole component, so eight files in total
  home_dir = os.environ['HOME'] + '/Timba/WH/contrib/AGW'

  # first do Y dipole
  infile_name_re_yx = home_dir + '/veidt_stuff/yx_real.fits'
  infile_name_im_yx = home_dir + '/veidt_stuff/yx_imag.fits'
  infile_name_re_yy = home_dir + '/veidt_stuff/yy_real.fits'
  infile_name_im_yy = home_dir + '/veidt_stuff/yy_imag.fits' 

  # note: cutoff=1.0,mode=2 flags are mysterious thingys needed by
  # Sarod's FITSImage node to read in the GRASP generated FITS files.
  ns.image_re_yx << Meq.FITSImage(filename=infile_name_re_yx,cutoff=1.0,mode=2)
  ns.image_im_yx << Meq.FITSImage(filename=infile_name_im_yx,cutoff=1.0,mode=2)
  ns.image_re_yy << Meq.FITSImage(filename=infile_name_re_yy,cutoff=1.0,mode=2)
  ns.image_im_yy << Meq.FITSImage(filename=infile_name_im_yy,cutoff=1.0,mode=2)

  # get sum of squares for Y dipole beam
  ns.im_sq_y << ns.image_re_yy * ns.image_re_yy + ns.image_im_yy * ns.image_im_yy + ns.image_re_yx * ns.image_re_yx + ns.image_im_yx * ns.image_im_yx

  # then take square root
  ns.im_y << Meq.Sqrt(ns.im_sq_y)

  # get the maximum of this beam for normalization
  ns.im_y_max << Meq.Max(ns.im_y)

  # normalize each beam separately
  ns.beam_re_yx_norm = ns.image_re_yx / ns.im_x_max
  ns.beam_im_yx_norm = ns.image_im_yx / ns.im_x_max
  ns.beam_re_yy_norm = ns.image_re_yy / ns.im_x_max
  ns.beam_im_yy_norm = ns.image_im_yy / ns.im_x_max

  # we will need a resampler for the beams in order to extract the
  # actual E-Jones in the directions of each of the sources. The dep_mask
  # flag is yet another of those mysterious thingys needed by Sarod ...
  ns.resampler_re_yx << Meq.Resampler(ns.beam_re_yx_norm, dep_mask=0xff)
  ns.resampler_im_yx << Meq.Resampler(ns.beam_im_yx_norm, dep_mask=0xff)
  ns.resampler_re_yy << Meq.Resampler(ns.beam_re_yy_norm, dep_mask=0xff)
  ns.resampler_im_yy << Meq.Resampler(ns.beam_im_yy_norm, dep_mask=0xff)


  # do a similar sequence of operations for X dipole
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
  ns.im_x_max << Meq.Max(ns.im_x)

  ns.beam_re_xx_norm = ns.image_re_xx / ns.im_x_max
  ns.beam_im_xx_norm = ns.image_im_xx / ns.im_x_max
  ns.beam_re_xy_norm = ns.image_re_xy / ns.im_x_max
  ns.beam_im_xy_norm = ns.image_im_xy / ns.im_x_max

  ns.resampler_re_xx << Meq.Resampler(ns.beam_re_xx_norm, dep_mask=0xff)
  ns.resampler_im_xx << Meq.Resampler(ns.beam_im_xx_norm, dep_mask=0xff)
  ns.resampler_re_xy << Meq.Resampler(ns.beam_re_xy_norm, dep_mask=0xff)
  ns.resampler_im_xy << Meq.Resampler(ns.beam_im_xy_norm, dep_mask=0xff)


def define_E_Jones(ns,src):
  # the following operation extracts the value of the actual e-Jones
  # in the direction of the individual sources through use of a
  # Compounder node: it has as children the position of the 
  # source and the resampler node mentioned above. The actual
  # operation is a bit mysterious to me - yet another Sarod thingy 

  ns.E_re_xx(src)<<Meq.Compounder(children=[ns.lm(src),ns.resampler_re_xx],common_axes=[hiid('l'),hiid('m')],default_cell_size=0.01) 
  ns.E_im_xx(src)<<Meq.Compounder(children=[ns.lm(src),ns.resampler_im_xx],common_axes=[hiid('l'),hiid('m')],default_cell_size=0.01) 
  ns.E_re_xy(src)<<Meq.Compounder(children=[ns.lm(src),ns.resampler_re_xy],common_axes=[hiid('l'),hiid('m')],default_cell_size=0.01) 
  ns.E_im_xy(src)<<Meq.Compounder(children=[ns.lm(src),ns.resampler_im_xy],common_axes=[hiid('l'),hiid('m')],default_cell_size=0.01) 

  ns.E_re_yx(src)<<Meq.Compounder(children=[ns.lm(src),ns.resampler_re_yx],common_axes=[hiid('l'),hiid('m')],default_cell_size=0.01) 
  ns.E_im_yx(src)<<Meq.Compounder(children=[ns.lm(src),ns.resampler_im_yx],common_axes=[hiid('l'),hiid('m')],default_cell_size=0.01) 
  ns.E_re_yy(src)<<Meq.Compounder(children=[ns.lm(src),ns.resampler_re_yy],common_axes=[hiid('l'),hiid('m')],default_cell_size=0.01) 
  ns.E_im_yy(src)<<Meq.Compounder(children=[ns.lm(src),ns.resampler_im_yy],common_axes=[hiid('l'),hiid('m')],default_cell_size=0.01) 

  ns.beam_xx(src) << Meq.ToComplex(ns.E_re_xx(src), ns.E_im_xx(src)) 
  ns.beam_xy(src) << Meq.ToComplex(ns.E_re_xy(src), ns.E_im_xy(src)) 
  ns.beam_yx(src) << Meq.ToComplex(ns.E_re_yx(src), ns.E_im_yx(src)) 
  ns.beam_yy(src) << Meq.ToComplex(ns.E_re_yy(src), ns.E_im_yy(src)) 

  # E Jones for the source
  ns.E(src) << Meq.Matrix22(ns.beam_xx(src), ns.beam_yx(src),ns.beam_xy(src), ns.beam_yy(src))

  # and get the complex conjugate
  ns.Et(src) << Meq.ConjTranspose(ns.E(src)) 

########################################################
def _define_forest(ns):  

  # first define beams
  setup_beams(ns)

# OK - we have assigned beam data - now observe sources

 # first set up nodes for phase center
  ns.radec0 = Meq.Composer(ns.ra<<0,ns.dec<<0);

  # nodes for array reference position
  ns.xyz0 = Meq.Composer(ns.x0<<0,ns.y0<<0,ns.z0<<0);

  # parallactic angle node
  ns.ParAngle << Meq.ParAngle(radec=ns.radec0, xyz=ns.xyz0)

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
    
    # Now, create antenna-based time-dependent gain variations
    # first, daily variation for x dipole
    # the Time node will give us the time of each of the sequence of
    # data points we are working with.

    # first calculate the phase at this moment in time
    ns.offset_day_x(p) << Meq.Time() - ant_phase_day_x[p-1]
    ns.phase_offset_day_x(p) << (ns.offset_day_x(p) *2* math.pi) / full_seconds_day 
    # now compute the actual gain variation of an antenna for the 
    # 24 hr daily cycle
    ns.daily_gain_x(p) << 1.0 + 0.005 * Meq.Cos(ns.phase_offset_day_x(p))

    # then, calculate phase and then hourly gain fluctuation 
    # for the 0.1 % hourly cycle
    ns.offset_hour_x(p) << Meq.Time() - ant_phase_hour_x[p-1]
    ns.phase_offset_hr_x(p) << (ns.offset_hour_x(p) *2* math.pi) /  seconds_hour
    ns.hourly_gain_x(p) << 0.0005 * Meq.Cos(ns.phase_offset_hr_x(p))

    # G Jones for x dipole = sum of daily and hourly gain
    ns.Gx(p) << ns.daily_gain_x(p) + ns.hourly_gain_x(p) 

    # now do the same sequence of calculations for the y dipole
    # first, daily cycle
    ns.offset_day_y(p) << Meq.Time() - ant_phase_day_y[p-1]
    ns.phase_offset_day_y(p) << (ns.offset_day_y(p) *2* math.pi) / full_seconds_day 
    ns.daily_gain_y(p) << 1.0 + 0.005 * Meq.Cos(ns.phase_offset_day_y(p))

    # then, hourly fluctuation 
    ns.offset_hour_y(p) << Meq.Time() - ant_phase_hour_y[p-1]
    ns.phase_offset_hr_y(p) << (ns.offset_hour_y(p) *2* math.pi) /  seconds_hour
    ns.hourly_gain_y(p) << 0.0005 * Meq.Cos(ns.phase_offset_hr_y(p))

    # G Jones for y dipole = sum of daily and hourly gain
    ns.Gy(p) << ns.daily_gain_y(p) + ns.hourly_gain_y(p) 

    # so we can now create the full 2 x 2 G Jones and its
    # complex conjugate
    ns.G(p) << Meq.Matrix22(ns.Gx(p), 0.0, 0.0, ns.Gy(p))
    ns.Gt(p) << Meq.ConjTranspose(ns.G(p))

  # gains display - the Composer node collects data for the
  # gains of the individual antennas together for display as
  # a function of time by the Collections Plotter - see the
  # bookmark set up near the beginning of the script
  ns.collector << Meq.Composer(dims=[0], tab_label = 'XNTD',
                  *[ns.G(p) for p in ANTENNAS]);

  # define modcal test signal
  ns.B1 << 0.5 * Meq.Matrix22(test_flux+Q,Meq.ToComplex(U,V),Meq.ToComplex(U,-V),test_flux-Q)

  # Now, define individual source e-Jones matrices
  for src in SOURCES:
    l,m,flux = LM[src];
    n = math.sqrt(1-l*l-m*m);
    ns.lmn_minus1(src) << Meq.Composer(l,m,n-1);
    # define source brightness B0 (unprojected)
    ns.B0(src) << 0.5 * Meq.Matrix22(flux+Q,Meq.ToComplex(U,V),Meq.ToComplex(U,-V),flux-Q)
    # don't really need to use the following for a point source
    ns.B(src) << ns.B0(src) / n;
    # here we pretend we're observing with an AZ_EL mounted dish
    # so that especially the first source is moving through a
    # sidelobe as a function of time.
    if src == 0:
      ns.lm0(src) << Meq.Composer(l,m)
      ns.RaDec(src) << Meq.LMRaDec(radec_0=ns.radec0, lm=ns.lm0(src))
      ns.lmn(src) << Meq.LMN(ns.radec0, ns.RaDec(src), ns.ParAngle)
      ns.ls(src) << Meq.Selector(ns.lmn(src),index=0)
      ns.ms(src) << Meq.Selector(ns.lmn(src),index=1)
      ns.lm(src) << Meq.Composer(ns.ls(src), ns.ms(src))
    else:
      ns.lm(src) << Meq.Composer(l,m)

    # now calculate E-Jones for a source
    define_E_Jones(ns,src)

# define K-jones matrices - just derive the phase shift, and the
# its complex conjugate for each antenna  / source combination
  for p in ANTENNAS:
    for src in SOURCES:
      ns.K(p,src) << Meq.VisPhaseShift(lmn=ns.lmn_minus1(src),uvw=ns.uvw(p));
      ns.Kt(p,src) << Meq.ConjTranspose(ns.K(p,src));

  # now define predicted visibilities, and attach to sinks for writing out
  # to the measurement set. We just calculate the measurement equation
  # for each source and interferometer pair though the MatrixMultiply
  # node 
  for p,q in IFRS:
    for src in SOURCES:
      # first make a predict that includes the time-variable G Jones 
      ns.predict(p,q,src) << \
        Meq.MatrixMultiply(ns.G(p),ns.E(src),ns.K(p,src),ns.B(src),ns.Kt(q,src),ns.Et(src),ns.Gt(q));
    # and sum up the separate predicts via Add nodes
    ns.predict(p,q) << Meq.Add(*[ns.predict(p,q,src) for src in SOURCES]);

  # and make a separate predict that has no G Jones or E Jones 
  # for our test source
  for p,q in IFRS:
      ns.predict_ok(p,q) << \
        Meq.MatrixMultiply(ns.K(p,0),ns.B1,ns.Kt(q,0));
      ns.predict_ok_conj(p,q) << Meq.Conj(ns.predict_ok(p,q))
    
  # ok - we have our observed and predicted fluxes - set up
  # modcal matrices. First define constant needed to get 
  # total number of points in the tile
  ns.unity << Meq.Constant(1.0)
  ns.elements << Meq.Sum(ns.unity)

  for p,q in IFRS:
    ns.sum_comb(p,q) << Meq.Sum(ns.predict_ok(p,q) * ns.predict_ok_conj(p,q))
    ns.sum_conj(p,q) << Meq.Sum(ns.predict_ok_conj(p,q))
    ns.sum(p,q) << Meq.Sum(ns.predict_ok(p,q))
    ns.sum_pred(p,q) << Meq.Sum(ns.predict(p,q))
    ns.sum_comb_pred(p,q) << Meq.Sum(ns.predict(p,q) * ns.predict_ok_conj(p,q))
    for i in range(4):
      ns.a11(p,q,i) << Meq.Selector(ns.sum_comb(p,q), index=i)
      ns.a12(p,q,i) << Meq.Selector(ns.sum_conj(p,q), index= i)
      ns.a21(p,q,i) << Meq.Selector(ns.sum(p,q),index=i)
      ns.components(p,q,i)<< Meq.Matrix22(ns.a11(p,q,i),ns.a12(p,q,i), ns.a21(p,q,i),ns.elements)
      ns.invert(p,q,i) << Meq.MatrixInvert22(ns.components(p,q,i))

      ns.h1(p,q,i) << Meq.Selector(ns.sum_comb_pred(p,q), index=i)
      ns.h2(p,q,i) << Meq.Selector(ns.sum_pred(p,q), index=i)
      ns.h_vector(p,q,i) << Meq.Composer(ns.h1(p,q,i), ns.h2(p,q,i))
      ns.gains(p,q,i) << Meq.MatrixMultiply(ns.invert(p,q,i), ns.h_vector(p,q,i))
    # we're only interested in the first of the two members of the solution vector
#   ns.gains(p,q) << Meq.Composer(dims=(2,2), children=(Meq.Selector(ns.gains(p,q,0),index=0), Meq.Selector(ns.gains(p,q,1),index=0), Meq.Selector(ns.gains(p,q,2),index=0), Meq.Selector(ns.gains(p,q,3),index=0)))
    ns.gains(p,q) << Meq.Composer(dims=(2,2), children=(Meq.Selector(ns.gains(p,q,0),index=0), 0.0, 0.0, Meq.Selector(ns.gains(p,q,3),index=0)))
    ns.diff(p,q) << ns.predict(p,q) - ns.gains(p,q) * ns.predict_ok(p,q)
    ns.sink(p,q) << Meq.Sink(ns.diff(p,q),station_1_index=p-1,station_2_index=q-1,output_col='DATA');
#   ns.sink(p,q) << Meq.Sink(ns.predict(p,q),station_1_index=p-1,station_2_index=q-1,output_col='DATA');

  ns.inspect_predicts << Meq.Composer(
    dims=[0],
    plot_label=["%s-%s"%(p,q) for p,q in IFRS],
    *[ns.gains(p,q) for p,q in IFRS]
  );

  # and thats it. Finally we define a VisDataMux node which essentially
  # has the sinks as implicit children. When we send a request
  # to the VisDataMux node in the _test_forest function below, it
  # sends requests to the sinks, which then propagate requests through
  # the tree ....
  ns.vdm << Meq.VisDataMux(pre=ns.collector,post=ns.inspect_predicts,*[ns.sink(p,q) for p,q in IFRS]);

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
  
