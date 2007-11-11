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
# and form a combined, weighted beam with phase-conjugate weighting.
# The weights are found by getting complex values at specified
# L,M location in the X (|| poln) beams and then
# taking the conjugate transpose.

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
from Timba.TDL import * 
from Timba.Meq import meqds
from Timba.Meq import meq
from Meow import Utils
import Meow.Bookmarks

import os
import math
# setup a few bookmarks
Settings.forest_state = record(bookmarks=[
  Meow.Bookmarks.PlotPage("Beams",["E_beam","resampler_E_beam"],["RaDec_beam","lm_offset:0"],["lmn_prime_beam","lmn_mean_beam"],["ParAngle","E:0"]),
  Meow.Bookmarks.PlotPage("Sinks",["sink:1:2","sink:2:4"],["sink:19:25","sink:20:27"])
]);

# to force caching put 100
#Settings.forest_state.cache_policy = 100

# define pseudo-VLA antenna list
ANTENNAS = range(1,28);
# derive interferometer list
IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ];

# source flux (same for all sources)
#I = 1; Q = .2; U = .2; V = .2;
I = 1; Q = .0; U = .0; V = .0;

# location of 'phased up' beam
#BEAM_LM = [(0.032620,0.0)]           # 1.5 x FWHM offset in L, 0 in M
#BEAM_LM = [(0.021747,0.0)]
#BEAM_LM = [(0.0307549, 0.0307549)]
#BEAM_LM = [(0.043494,0.0)]
BEAM_LM = [(0.038061,0.0)]

# we'll put the sources on a grid (positions relative to beam centre in radians)
#LM_OFF = [(-0.0108735,-0.0108735),(-0.0108735,0),(-0.0108735,0.0108735),
#      ( 0,-0.0108735),( 0,0),( 0,0.0108735),
#      ( 0.0108735,-0.0108735),( 0.0108735,0),( 0.0108735,0.0108735)];

LM_OFF = [(0.0108735,0.0)]      # add 0.5 FWHM offset to beam position
#LM_OFF = [(0.0,0.0)]      # add 0.5 FWHM offset to beam position
SOURCES = range(len(LM_OFF));       # 0...N-1


########################################################
def _define_forest(ns):  

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

# read in beam images
 # fit all 180 beams
  BEAMS = range(0,90)
  home_dir = os.environ['HOME']
  # read in beam data
  for k in BEAMS:
  # read in beam data - y dipole
    infile_name_re_yx = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa_180/fpa_pat_' + str(k+90) + '_Re_x.fits'
    infile_name_im_yx = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa_180/fpa_pat_' + str(k+90) +'_Im_x.fits'
    infile_name_re_yy = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa_180/fpa_pat_' + str(k+90) +'_Re_y.fits'
    infile_name_im_yy = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa_180/fpa_pat_' + str(k+90) +'_Im_y.fits' 
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

    ns.resampler_image_re_yy(k) << Meq.Resampler(ns.norm_image_re_yy(k),dep_mask = 0xff)
    ns.resampler_image_im_yy(k) << Meq.Resampler(ns.norm_image_im_yy(k),dep_mask = 0xff)
    ns.beam_wt_re_y(k) << Meq.Compounder(children=[ns.lm_mean_beam,ns.resampler_image_re_yy(k)],common_axes=[hiid('l'),hiid('m')])
    ns.beam_wt_im_y(k) << Meq.Compounder(children=[ns.lm_mean_beam,ns.resampler_image_im_yy(k)],common_axes=[hiid('l'),hiid('m')])

    ns.beam_wt_y(k) << Meq.ToComplex(ns.beam_wt_re_y(k), ns.beam_wt_im_y(k))
    ns.beam_weight_y(k) << Meq.ConjTranspose(ns.beam_wt_y(k))

    ns.beam_yx(k) << Meq.ToComplex(ns.norm_image_re_yx(k), ns.norm_image_im_yx(k)) 
    ns.beam_yy(k) << Meq.ToComplex(ns.norm_image_re_yy(k), ns.norm_image_im_yy(k))
    ns.wt_beam_yx(k) << ns.beam_yx(k) * ns.beam_weight_y(k)
    ns.wt_beam_yy(k) << ns.beam_yy(k) * ns.beam_weight_y(k)

  # read in beam data - x dipole
    infile_name_re_xx = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa_180/fpa_pat_' + str(k) + '_Re_x.fits'
    infile_name_im_xx = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa_180/fpa_pat_' + str(k) +'_Im_x.fits'
    infile_name_re_xy = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa_180/fpa_pat_' + str(k) +'_Re_y.fits'
    infile_name_im_xy = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa_180/fpa_pat_' + str(k) +'_Im_y.fits' 
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


    ns.resampler_image_re_xx(k) << Meq.Resampler(ns.norm_image_re_xx(k),dep_mask = 0xff)
    ns.resampler_image_im_xx(k) << Meq.Resampler(ns.norm_image_im_xx(k),dep_mask = 0xff)
    ns.beam_wt_re_x(k) << Meq.Compounder(children=[ns.lm_mean_beam,ns.resampler_image_re_xx(k)],common_axes=[hiid('l'),hiid('m')])
    ns.beam_wt_im_x(k) << Meq.Compounder(children=[ns.lm_mean_beam,ns.resampler_image_im_xx(k)],common_axes=[hiid('l'),hiid('m')])

    ns.beam_wt_x(k) << Meq.ToComplex(ns.beam_wt_re_x(k), ns.beam_wt_im_x(k))
    ns.beam_weight_x(k) << Meq.ConjTranspose(ns.beam_wt_x(k))

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
  ns.voltage_sum_xx_norm << ns.voltage_sum_xx / ns.im_x_max
  ns.voltage_sum_xy_norm << ns.voltage_sum_xy / ns.im_x_max

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

  ns.E_beam << Meq.Matrix22(ns.voltage_sum_xx_norm, ns.voltage_sum_yx_norm,ns.voltage_sum_xy_norm, ns.voltage_sum_yy_norm)
  ns.resampler_E_beam << Meq.Resampler(ns.E_beam, dep_mask=0xff)
#  ns.Et << Meq.ConjTranspose(ns.E)

 # sky brightness - same for all sources
  ns.B0 << 0.5 * Meq.Matrix22(1.0, 0.0, 0.0, 1.0)

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
def _test_forest(mqs,parent,wait=False):

# now observe sources
  req = meq.request();
  req.input = record(
    ms = record(
#     ms_name          = 'TEST_XNTD_30_960.MS',
#     ms_name          = 'TEST_CLAR_27-960.MS',
      ms_name          = 'TEST_CLAR_27-1920.MS',
      tile_size        = 1,
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

#####################################################################

if __name__=='__main__':
 if '-run' in sys.argv:
   from Timba.Apps import meqserver
   from Timba.TDL import Compile

   # this starts a kernel.
#  mqs = meqserver.default_mqs(wait_init=10);
   mqs = meqserver.default_mqs(wait_init=10,extra=["-mt","2"])

   # This compiles a script as a TDL module. Any errors will be thrown as
   # an exception, so this always returns successfully. We pass in
   # __file__ so as to compile ourselves.
   (mod,ns,msg) = Compile.compile_file(mqs,__file__);

   # this runs the _test_forest job.
   mod._test_forest(mqs,None,wait=True);

 else:
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())

