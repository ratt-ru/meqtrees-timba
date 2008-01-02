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
# We read in a group of focal plane array beams, 
# and form a combined, weighted beam to optimize the
# gaussian beam shape.
# The weights are found by getting complex values at specified
# L,M location in the X (|| poln) beams and then
# taking the conjugate transpose. These weights are then used as
# initial guesses to get weights for the gaussian beam.

# We then pretend that we are observing with an AzEl mounted telescope
# at the VLA site and calculate the change in phased-up beam
# shape as we track a specific off-boresight RA/DEC point over
# an 8 hr 'VLA' observation. 

# We use the phased up beam as the E-Jones to observe an array
# of sources at specific L,M locations offset with respect to the
# centre of the phased-up beam.

# History:
# - 07 Mar 2007: creation:

#=======================================================================
# Import of Python / TDL modules:

# Get TDL and Meq for the Kernel
from numarray import *
from Timba.TDL import * 
from Timba.Meq import meqds
from Timba.Meq import meq
from Meow import Utils
from handle_beams import *

import Meow.Bookmarks

import os
import math
Settings.forest_state = record(bookmarks=[
  Meow.Bookmarks.PlotPage("Beams",["I_real","resampler_I"],["gaussian","condeq"],["lmn_prime_beam","resampler_E_beam"]),
  Meow.Bookmarks.PlotPage("Sinks",["sink:1:2","sink:2:4"],["sink:19:25","sink:20:27"])
]);

# to force caching put 100
Settings.forest_state.cache_policy = 100

# define pseudo-VLA antenna list
ANTENNAS = range(1,28);
# derive interferometer list
IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ];

# source flux (same for all sources)
#I = 1; Q = .2; U = .2; V = .2;
I = 1; Q = .0; U = .0; V = .0;

# location of 'phased up' beam
#BEAM_LM = [(0.032620,0.0)]           # 1.5 x FWHM offset in L, 0 in M
BEAM_LM = [(0.021747,0.0)]

# we'll put the sources on a grid (positions relative to beam centre in radians)
#LM_OFF = [(-0.0108735,-0.0108735),(-0.0108735,0),(-0.0108735,0.0108735),
#      ( 0,-0.0108735),( 0,0),( 0,0.0108735),
#      ( 0.0108735,-0.0108735),( 0.0108735,0),( 0.0108735,0.0108735)];

LM_OFF = [(0.0108735,0.0)]      # add 0.5 FWHM offset to beam position
SOURCES = range(len(LM_OFF));       # 0...N-1

# to force caching put 100
#Settings.forest_state.cache_policy = 100

def create_polc(c00=0.0,degree_f=0,degree_t=0):
  """helper function to create a t/f polc with the given c00 coefficient,
  and with given order in t/f""";
  polc = meq.polc(zeros((degree_t+1, degree_f+1))*0.0);
  polc.coeff[0,0] = c00;
  return polc;

def tpolc (tdeg,c00=0.0):
  return Meq.Parm(create_polc(degree_f=0,degree_t=tdeg,c00=c00),
                  node_groups='Parm')

########################################################
def _define_forest(ns):  

  # constant for half-intensity determination
  ns.ln_16 << Meq.Constant(-2.7725887)

  # define desired half-intensity width of power pattern (HPBW)
  # as we are fitting total intensity I pattern (here 74.8 arcmin)
  ns.width << Meq.Constant(0.021747)

 # set up nodes for telescope array
 # first do phase center
  ns.radec0 = Meq.Composer(ns.ra<<0,ns.dec<<0);

  # nodes for array reference position
  ns.xyz0 = Meq.Composer(ns.x0<<0,ns.y0<<0,ns.z0<<0);

  # parallactic angle node for boresight tracking position
  ns.ParAngle << Meq.ParAngle(radec=ns.radec0, xyz=ns.xyz0)

  # now define per-station stuff: XYZs and UVWs
  for p in ANTENNAS:
    # positions and uvw
    ns.xyz(p) << Meq.Composer(ns.x(p)<<0,ns.y(p)<<0,ns.z(p)<<0);
    ns.uvw(p) << Meq.Negate(Meq.UVW(radec=ns.radec0,xyz_0=ns.xyz0,xyz=ns.xyz(p)));


# obtain the RA, DEC of the beam at transit
  l_beam,m_beam = BEAM_LM[0]
  ns.l_beam  << Meq.Parm(l_beam,node_groups='Parm')
  ns.m_beam  << Meq.Parm(m_beam,node_groups='Parm')
  ns.lm_beam << Meq.Composer(ns.l_beam,ns.m_beam);
  ns.RaDec_beam << Meq.LMRaDec(radec_0=ns.radec0, lm=ns.lm_beam)

# compute corresponding 'apparent' L,M position of feed in AzEl
# system as function of parallactic angle
  ns.lmn_prime_beam << Meq.LMN(ns.radec0, ns.RaDec_beam, ns.ParAngle)

# freeze beam position over 'tile' interval by getting the mean over interval
  ns.lmn_mean_beam << Meq.Mean(ns.lmn_prime_beam)
  ns.l_mean_prime_beam << Meq.Selector(ns.lmn_mean_beam, index=0)
  ns.m_mean_prime_beam << Meq.Selector(ns.lmn_mean_beam, index=1)
  ns.lm_mean_beam << Meq.Composer(ns.l_mean_prime_beam,ns.m_mean_prime_beam);

  laxis = ns.laxis << Meq.Grid(axis=2);
  maxis = ns.maxis << Meq.Grid(axis=3);

  # gaussian to which we want to optimize beams
  ns.lm_x_sq << Meq.Sqr(laxis - ns.l_mean_prime_beam) + Meq.Sqr(maxis - ns.m_mean_prime_beam)
  ns.gaussian << Meq.Exp((ns.lm_x_sq * ns.ln_16)/Meq.Sqr(ns.width));


  fpa_directory = 'veidt_fpa'
  num_beams = read_in_FPA_beams(ns,fpa_directory)
  BEAMS = range(0,num_beams)

  beam_solvables = []
  parm_solvers = []
  for k in BEAMS:
    # normalize - y dipole
    ns.y_im_sq(k) << ns.image_re_yy(k) * ns.image_re_yy(k) + ns.image_im_yy(k) * ns.image_im_yy(k) +\
                  ns.image_re_yx(k) * ns.image_re_yx(k) + ns.image_im_yx(k) * ns.image_im_yx(k)
    ns.y_im(k) <<Meq.Sqrt(ns.y_im_sq(k))
    ns.y_im_max(k) <<Meq.Max(ns.y_im(k))
    ns.norm_image_re_yy(k) << ns.image_re_yy(k) / ns.y_im_max(k)
    ns.norm_image_im_yy(k) << ns.image_im_yy(k) / ns.y_im_max(k)
    ns.norm_image_re_yx(k) << ns.image_re_yx(k) / ns.y_im_max(k)
    ns.norm_image_im_yx(k) << ns.image_im_yx(k) / ns.y_im_max(k)

    ns.resampler_image_re_yy(k) << Meq.Resampler(ns.norm_image_re_yy(k),dep_mask = 0xff)
    ns.resampler_image_im_yy(k) << Meq.Resampler(ns.norm_image_im_yy(k),dep_mask = 0xff)
    ns.sample_wt_re_y(k) << Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_re_yy(k)],common_axes=[hiid('l'),hiid('m')])
    ns.sample_wt_im_y(k) << -1.0 * Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_im_yy(k)],common_axes=[hiid('l'),hiid('m')])
    # I want to solve for these parameters
    ns.beam_wt_re_y(k) << tpolc(0)
    ns.beam_wt_im_y(k) << tpolc(0)
    beam_solvables.append(ns.beam_wt_re_y(k))
    beam_solvables.append(ns.beam_wt_im_y(k))
    # we need to assign the weights we've extracted as initial guesses
    # to the Parm - can only be done by solving
    ns.condeq_wt_re_y(k) << Meq.Condeq(children=(ns.sample_wt_re_y(k), ns.beam_wt_re_y(k)))
    ns.condeq_wt_im_y(k) << Meq.Condeq(children=(-1.0 * ns.sample_wt_im_y(k), ns.beam_wt_im_y(k)))
    ns.solver_wt_re_y(k)<<Meq.Solver(ns.condeq_wt_re_y(k),num_iter=50,epsilon=1e-4,solvable=ns.beam_wt_re_y(k),save_funklets=True,last_update=True)
    ns.solver_wt_im_y(k)<<Meq.Solver(ns.condeq_wt_im_y(k),num_iter=50,epsilon=1e-4,solvable=ns.beam_wt_im_y(k),save_funklets=True,last_update=True)
    parm_solvers.append(ns.solver_wt_re_y(k))
    parm_solvers.append(ns.solver_wt_im_y(k))

    ns.beam_weight_y(k) << Meq.ToComplex(ns.beam_wt_re_y(k), ns.beam_wt_im_y(k))

    ns.beam_yx(k) << Meq.ToComplex(ns.norm_image_re_yx(k), ns.norm_image_im_yx(k)) 
    ns.beam_yy(k) << Meq.ToComplex(ns.norm_image_re_yy(k), ns.norm_image_im_yy(k))
    ns.wt_beam_yx(k) << ns.beam_yx(k) * ns.beam_weight_y(k)
    ns.wt_beam_yy(k) << ns.beam_yy(k) * ns.beam_weight_y(k)

    # normalize - x dipole
    ns.x_im_sq(k) << ns.image_re_xx(k) * ns.image_re_xx(k) + ns.image_im_xx(k) * ns.image_im_xx(k) +\
                  ns.image_re_xy(k) * ns.image_re_xy(k) + ns.image_im_xy(k) * ns.image_im_xy(k)
    ns.x_im(k) <<Meq.Sqrt(ns.x_im_sq(k))
    ns.x_im_max(k) <<Meq.Max(ns.x_im(k))
    ns.norm_image_re_xx(k) << ns.image_re_xx(k) / ns.x_im_max(k)
    ns.norm_image_im_xx(k) << ns.image_im_xx(k) / ns.x_im_max(k)
    ns.norm_image_re_xy(k) << ns.image_re_xy(k) / ns.x_im_max(k)
    ns.norm_image_im_xy(k) << ns.image_im_xy(k) / ns.x_im_max(k)
    ns.resampler_image_re_xx(k) << Meq.Resampler(ns.norm_image_re_xx(k),dep_mask = 0xff)
    ns.resampler_image_im_xx(k) << Meq.Resampler(ns.norm_image_im_xx(k),dep_mask = 0xff)
    ns.sample_wt_re_x(k) << Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_re_xx(k)],common_axes=[hiid('l'),hiid('m')])
    ns.sample_wt_im_x(k) << Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_im_xx(k)],common_axes=[hiid('l'),hiid('m')])
    # I want to solve for these parameters
    ns.beam_wt_re_x(k) << tpolc(0)
    ns.beam_wt_im_x(k) << tpolc(0)
    beam_solvables.append(ns.beam_wt_re_x(k))
    beam_solvables.append(ns.beam_wt_im_x(k))
    ns.condeq_wt_re_x(k) << Meq.Condeq(children=(ns.sample_wt_re_x(k), ns.beam_wt_re_x(k)))
    ns.condeq_wt_im_x(k) << Meq.Condeq(children=(-1.0 * ns.sample_wt_im_x(k), ns.beam_wt_im_x(k)))
    ns.solver_wt_re_x(k)<<Meq.Solver(ns.condeq_wt_re_x(k),num_iter=50,epsilon=1e-4,solvable=ns.beam_wt_re_x(k),save_funklets=True,last_update=True)
    ns.solver_wt_im_x(k)<<Meq.Solver(ns.condeq_wt_im_x(k),num_iter=50,epsilon=1e-4,solvable=ns.beam_wt_im_x(k),save_funklets=True,last_update=True)
    parm_solvers.append(ns.solver_wt_re_x(k))
    parm_solvers.append(ns.solver_wt_im_x(k))

    ns.beam_weight_x(k) << Meq.ToComplex(ns.beam_wt_re_x(k), ns.beam_wt_im_x(k))

    ns.beam_xy(k) << Meq.ToComplex(ns.norm_image_re_xy(k), ns.norm_image_im_xy(k)) 
    ns.beam_xx(k) << Meq.ToComplex(ns.norm_image_re_xx(k), ns.norm_image_im_xx(k))
    ns.wt_beam_xy(k) << ns.beam_xy(k) * ns.beam_weight_x(k)
    ns.wt_beam_xx(k) << ns.beam_xx(k) * ns.beam_weight_x(k)

  # solver to 'copy' resampled beam locations to parms as
  # first guess
  ns.parms_req_mux<<Meq.ReqMux(children=parm_solvers)

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
  ns.im_x_norm << ns.im_x / ns.im_x_max

  ns.voltage_sum_yy_r << Meq.Real(ns.voltage_sum_yy)
  ns.voltage_sum_yy_i << Meq.Imag(ns.voltage_sum_yy)
  ns.voltage_sum_yx_r << Meq.Real(ns.voltage_sum_yx)
  ns.voltage_sum_yx_i << Meq.Imag(ns.voltage_sum_yx)
  ns.im_sq_y << ns.voltage_sum_yy_r * ns.voltage_sum_yy_r + ns.voltage_sum_yy_i * ns.voltage_sum_yy_i +\
                  ns.voltage_sum_yx_r * ns.voltage_sum_yx_r + ns.voltage_sum_yx_i * ns.voltage_sum_yx_i
  ns.im_y <<Meq.Sqrt(ns.im_sq_y)
  ns.im_y_max <<Meq.Max(ns.im_y)
  ns.im_y_norm << ns.im_y / ns.im_y_max

  ns.voltage_sum_yy_norm << ns.voltage_sum_yy / ns.im_y_max
  ns.voltage_sum_yx_norm << ns.voltage_sum_yx / ns.im_y_max

  ns.voltage_sum_xx_norm << ns.voltage_sum_xx / ns.im_x_max
  ns.voltage_sum_xy_norm << ns.voltage_sum_xy / ns.im_x_max


  ns.E_beam << Meq.Matrix22(ns.voltage_sum_xx_norm, ns.voltage_sum_yx_norm,ns.voltage_sum_xy_norm, ns.voltage_sum_yy_norm)
  ns.E_beam_t << Meq.ConjTranspose(ns.E_beam)

 # sky brightness
  ns.B0 << 0.5 * Meq.Matrix22(1.0, 0.0, 0.0, 1.0)

  # observe!
  ns.observed << Meq.MatrixMultiply(ns.E_beam, ns.B0, ns.E_beam_t)

  # extract I
  ns.IpQ << Meq.Selector(ns.observed,index=0)        # XX = (I+Q)/2
  ns.ImQ << Meq.Selector(ns.observed,index=3)        # YY = (I-Q)/2
  ns.I << Meq.Add(ns.IpQ,ns.ImQ)                     # I = XX + YY

  # join together into one node in order to make a single request
  ns.I_real << Meq.Real(ns.I)

  ns.resampler_I << Meq.Resampler(ns.I_real)

  ns.condeq<<Meq.Condeq(children=(ns.resampler_I, ns.gaussian))
  ns.solver<<Meq.Solver(ns.condeq,num_iter=20,mt_polling=False,epsilon=1e-4,solvable=beam_solvables,save_funklets=True,last_update=True)

  ns.E_req_seq<<Meq.ReqSeq(ns.parms_req_mux, ns.solver, ns.E_beam, result_index=2)

  # Note: we are observing with linearly-polarized dipoles. If we
  # want the aips++ imager to generate images in the sequence I,Q,U,V
  # make sure that the newsimulator setspwindow method uses
  # stokes='XX XY YX YY' and not stokes='RR RL LR LL'. If you
  # do the latter you will get the images rolled out in the
  # order I,U,V,Q!

  ns.resampler_E_beam << Meq.Resampler(ns.E_req_seq, dep_mask=0xff)

 # set up source l,m,n-1 vectors with respect to boresight (phase tracking
 # location
  for src in SOURCES:
    l_off,m_off = LM_OFF[src];
    l = l_beam + l_off
    m = m_beam + m_off
    n = math.sqrt(1-l*l-m*m);
    ns.lmn_minus1(src) << Meq.Composer(l,m,n-1);
    # get intrinsic RA, DEC of sources
    ns.lm_src(src) << Meq.Composer(l,m);
    ns.RaDec(src) << Meq.LMRaDec(radec_0=ns.radec0, lm=ns.lm_src(src))
    # and the projected brightness...
# don't really need to use the following for a point source
    ns.B(src) << ns.B0 / n;

# create L,M offset of source with respect to 'phased' beam centre
# compute corresponding 'apparent' L,M position of feed in AzEl
# system as function of parallactic angle

    ns.lm_prime(src) << Meq.LMN(ns.radec0, ns.RaDec(src), ns.ParAngle)
    ns.l_prime(src) << Meq.Selector(ns.lm_prime(src), index=0)
    ns.m_prime(src) << Meq.Selector(ns.lm_prime(src), index=1)
    ns.lm_offset(src) << Meq.Composer(ns.l_prime(src), ns.m_prime(src))
 
    # now compute the E-Jones voltage gains
    ns.E(src)<<Meq.Compounder(children=[ns.lm_offset(src),ns.resampler_E_beam],common_axes=[hiid('l'),hiid('m')])
    ns.Et(src) << Meq.ConjTranspose(ns.E(src))

# define K-jones matrices
  for p in ANTENNAS:
    for src in SOURCES:
      ns.K(p,src) << Meq.VisPhaseShift(lmn=ns.lmn_minus1(src),uvw=ns.uvw(p));
      ns.Kt(p,src) << Meq.ConjTranspose(ns.K(p,src));


 # now define predicted visibilities, attach to sinks
  for p,q in IFRS:
    # make per-source predicted visibilities
    for src in SOURCES:
      if p == 1 and q == 2 and src == 0: 
        ns.predict(p,q,src) << \
          Meq.MatrixMultiply(ns.E(src),ns.K(p,src),ns.B(src),ns.Kt(q,src),ns.Et(src),log_policy=100);
      else:
        ns.predict(p,q,src) << \
          Meq.MatrixMultiply(ns.E(src),ns.K(p,src),ns.B(src),ns.Kt(q,src),ns.Et(src));
    predict = ns.predict(p,q) << Meq.Add(*[ns.predict(p,q,src) for src in SOURCES]);
    ns.sink(p,q) << Meq.Sink(predict,station_1_index=p-1,station_2_index=q-1,output_col='DATA');

  # define VisDataMux
  ns.vdm << Meq.VisDataMux(*[ns.sink(p,q) for p,q in IFRS]);



########################################################################
def _test_forest(mqs,parent):

# now observe sources
  req = meq.request();
  req.input = record(
    ms = record(
#     ms_name          = 'TEST_XNTD_30_960.MS',
      ms_name          = 'TEST_CLAR_27-960.MS',
      tile_size        = 96,
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

#####################################################################

if __name__=='__main__':
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())

