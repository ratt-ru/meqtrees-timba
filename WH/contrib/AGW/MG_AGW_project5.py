#!/usr/bin/python

#% $Id: MG_AGW_project5.py 3929 2006-09-01 20:17:51Z twillis $ 

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

# script_name = 'MG_AGW_project5.py'

# Short description:
# We read in a 3 x 3 grid of sources, and essentially observe them
# with a single 'phased up' beam located at the BEAM_LM position.
# We simulate the xntd array with observation nominally centred at
# -45 deg. In this project we simulate an AzEl observation and
# can either simulate the observation or the error pattern if we
# only update the beamformer once per tile.

# History:
# - 3 Nov 2006: creation:

#=======================================================================
# Import of Python / TDL modules:

import math
import random

from string import split, strip
from numarray import *

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meq
import Meow.Bookmarks


# setup a few bookmarks
Settings.forest_state = record(bookmarks=[
  Meow.Bookmarks.PlotPage("E Jones",["sink:1:30","sink:12:25"],["image:1","image:25"])
]);


# to force caching put 100
Settings.forest_state.cache_policy = 100

# define antenna list
ANTENNAS = range(1,31);
# derive interferometer list
IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ];

# MEP table for derived quantities fitted in this script
mep_beam_locations = 'beam_locations.mep';

# source flux (same for all sources)
#I = 1; Q = .2; U = .2; V = .2;
I = 1; Q = .0; U = .0; V = .0;

# location of 'phased up' beam
#BEAM_LM = [(0.0,0.0087266463)]  # offset of 0.5 deg in DEC
#BEAM_LM = [(0.0,0.017453293)]  # offset of 1 deg in DEC
#BEAM_LM = [(0.0,0.052359879)]  # offset of 3 deg in DEC
#`BEAM_LM = [(0.052359879,0.0)]  # offset of 3 deg in L
BEAM_LM = [(0.024682684,0.024682684)]  # offset of 2 deg on diagonal

# we'll put the sources on a grid (positions relative to beam centre in radians)
#LM = [(-0.0087266463,-0.0087266463),(-0.0087266463,0),(-0.0087266463,0.0087266463),
#      ( 0,-0.0087266463),( 0,0),( 0,0.0087266463),
#      ( 0.0087266463,-0.0087266463),( 0.0087266463,0),( 0.0087266463,0.0087266463)];
LM = [(0,0)]
SOURCES = range(len(LM));       # 0...N-1


########################################################
def _define_forest(ns):  

# read in beam images
  BEAMS = range(1,181)
  home_dir = os.environ['HOME']
  for k in BEAMS:
    infile_name = ""
    if k <= 90:
      fits_num = k
      infile_name = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + 'y.fits'
    else:
      fits_num = k - 90
      infile_name = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + 'x.fits'

    ns.image(k) << Meq.FITSImage(filename=infile_name,cutoff=1.0,mode=2)
    ns.resampler(k) << Meq.Resampler(ns.image(k), dep_mask=0xff)
#   ns.resampler(k) << Meq.Resampler(ns.image(k))

# get positions of beam peaks from mep table
# scale factor of 17 used to increase size of beam offsets
# proportional to beam multiplication done from brisken stuff
    ns.scale_factor << Meq.Constant(1.0)
    ns.l0(k)<< Meq.Parm(table_name=mep_beam_locations)
    ns.m0(k)<< Meq.Parm(table_name=mep_beam_locations)
    ns.l00(k)<< ns.l0(k) * ns.scale_factor 
    ns.m00(k)<< ns.m0(k) * ns.scale_factor 

# now create a source and observe it
 # nodes for phase center
  ns.radec0 = Meq.Composer(ns.ra<<0,ns.dec<<0);

  # nodes for array reference position
  ns.xyz0 = Meq.Composer(ns.x0<<0,ns.y0<<0,ns.z0<<0);

  # parallactic angle node
  ns.ParAngle << Meq.ParAngle(radec=ns.radec0, xyz=ns.xyz0)

  # now define per-station stuff: XYZs and UVWs
  for p in ANTENNAS:
    # positions and uvw
    ns.xyz(p) << Meq.Composer(ns.x(p)<<0,ns.y(p)<<0,ns.z(p)<<0);
    ns.uvw(p) << Meq.Negate(Meq.UVW(radec=ns.radec0,xyz_0=ns.xyz0,xyz=ns.xyz(p)));

# now compute the RA, DEC of the beam at transit
  l_beam,m_beam = BEAM_LM[0]
  ns.l_beam  << Meq.Parm(l_beam,node_groups='Parm')
  ns.m_beam  << Meq.Parm(m_beam,node_groups='Parm')
  ns.lm_beam << Meq.Composer(ns.l_beam,ns.m_beam);
  ns.RaDec_beam << Meq.LMRaDec(radec_0=ns.radec0, lm=ns.lm_beam)

# compute corresponding 'apparent' L,M position of feed in AzEl
# system as function of parallactic angle

  ns.lm_prime_beam << Meq.LMN(ns.radec0, ns.RaDec_beam, ns.ParAngle)
  ns.l_prime_beam << Meq.Selector(ns.lm_prime_beam, index=0)
  ns.m_prime_beam << Meq.Selector(ns.lm_prime_beam, index=1)

# freeze beam position over interval by getting the mean over interval
  ns.lm_mean_prime_beam << Meq.Mean(ns.lm_prime_beam)
  ns.l_mean_prime_beam << Meq.Selector(ns.lm_mean_prime_beam, index=0)
  ns.m_mean_prime_beam << Meq.Selector(ns.lm_mean_prime_beam, index=1)
  
  for k in BEAMS:
    ns.l_offset(k) << ns.l00(k) - ns.l_prime_beam
    ns.m_offset(k) << ns.m00(k) - ns.m_prime_beam
    ns.beam_weight(k) << 1.0 / Meq.Sqrt(Meq.Sqr(ns.l_offset(k)) + Meq.Sqr(ns.m_offset(k)))

    ns.l_mean_offset(k) << ns.l00(k) - ns.l_mean_prime_beam
    ns.m_mean_offset(k) << ns.m00(k) - ns.m_mean_prime_beam
    ns.beam_mean_weight(k) << 1.0 / Meq.Sqrt(Meq.Sqr(ns.l_mean_offset(k)) + Meq.Sqr(ns.m_mean_offset(k)))

  ns.weighted_mean << Meq.Add(*[ns.beam_weight(k) for k in BEAMS]) 
  ns.weighted_mean_mean << Meq.Add(*[ns.beam_mean_weight(k) for k in BEAMS]) 


  # define source brightness B0 (unprojected, same for all sources)
  ns.B0 << 0.5 * Meq.Matrix22(I+Q,Meq.ToComplex(U,V),Meq.ToComplex(U,-V),I-Q);

  # source l,m,n-1 vectors
  for src in SOURCES:
    l_off,m_off = LM[src];
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
    ns.l_pos(src) << ns.l_prime(src) - ns.l_prime_beam 
    ns.m_pos(src) << ns.m_prime(src) - ns.m_prime_beam
    ns.l_mean_pos(src) << ns.l_prime(src) - ns.l_mean_prime_beam
    ns.m_mean_pos(src) << ns.m_prime(src) - ns.m_mean_prime_beam


# now compute the beam gains
    for k in BEAMS:
      ns.source_beam_l(src,k) << ns.l00(k) + ns.l_pos(src)
      ns.source_beam_m(src,k) << ns.m00(k) + ns.m_pos(src)
      ns.lm_offset(src,k) << Meq.Composer(ns.source_beam_l(src,k),ns.source_beam_m(src,k))
      ns.beam_gain(src,k)<<Meq.Compounder(children=[ns.lm_offset(src,k),ns.resampler(k)],common_axes=[hiid('l'),hiid('m')]) * ns.beam_weight(k)

      ns.source_beam_mean_l(src,k) << ns.l00(k) + ns.l_mean_pos(src)
      ns.source_beam_mean_m(src,k) << ns.m00(k) + ns.m_mean_pos(src)
      ns.lm_mean_offset(src,k) << Meq.Composer(ns.source_beam_mean_l(src,k),ns.source_beam_mean_m(src,k))
      ns.beam_mean_gain(src,k)<<Meq.Compounder(children=[ns.lm_mean_offset(src,k),ns.resampler(k)],common_axes=[hiid('l'),hiid('m')]) * ns.beam_mean_weight(k)

    ns.E(src) << Meq.Sqrt(Meq.Add(*[ns.beam_gain(src,k) for k in BEAMS]) / ns.weighted_mean)
    ns.E_mean(src) << Meq.Sqrt(Meq.Add(*[ns.beam_mean_gain(src,k) for k in BEAMS]) / ns.weighted_mean_mean)
    ns.Et(src) << Meq.ConjTranspose(ns.E(src));
    ns.E_diff(src) <<  ns.E(src) - ns.E_mean(src)
    ns.Et_diff(src) << Meq.ConjTranspose(ns.E_diff(src));
    ns.E_div(src) << Meq.Divide( ns.E_diff(src), ns.E(src)) 
    ns.Et_div(src) << Meq.ConjTranspose(ns.E_div(src))

 # define K-jones matrices
  for p in ANTENNAS:
    for src in SOURCES:
      ns.K(p,src) << Meq.VisPhaseShift(lmn=ns.lmn_minus1(src),uvw=ns.uvw(p));
      ns.Kt(p,src) << Meq.ConjTranspose(ns.K(p,src));

  # now define predicted visibilities, attach to sinks
  for p,q in IFRS:
    # make per-source predicted visibilities
    for src in SOURCES:
      ns.predict(p,q,src) << \
        Meq.MatrixMultiply(ns.E_diff(src),ns.K(p,src),ns.B(src),ns.Kt(q,src),ns.Et_diff(src));
#       Meq.MatrixMultiply(ns.E_div(src),ns.K(p,src),ns.B(src),ns.Kt(q,src),ns.Et_div(src)) * 100.0;
#       Meq.MatrixMultiply(ns.E(src),ns.K(p,src),ns.B(src),ns.Kt(q,src),ns.Et(src));
    # and sum them up via an Add node
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
      ms_name          = 'TEST_XNTD_30_960.MS',
      tile_size        = 40,
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
  
