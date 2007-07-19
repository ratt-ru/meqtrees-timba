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

# script_name = ' MG_AGW_project720.py'

# Short description:
# We read in a grid of sources, and essentially observe them
# with a single 'phased up' beam located at the BEAM_LM position.
# phases are determined by taking complex transpose at 
# location of tracking centre

# History:
# - 07 Jan 2007: creation:

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
BEAM_LM = [(0.0,0.0)]
# we'll put the sources on a grid (positions relative to 
# beam centre in radians)
LM = [(0.00001,0)]
SOURCES = range(len(LM));       # 0...N-1

########################################################
def _define_forest(ns):  

# get the position where we wish to form a beam 
  l_beam,m_beam = BEAM_LM[0]
  ns.l_beam  << Meq.Parm(l_beam,node_groups='Parm')
  ns.m_beam  << Meq.Parm(m_beam,node_groups='Parm')
  ns.beam_pos << Meq.Composer(ns.l_beam,ns.m_beam)

# read in beam images
 # fit all 180 beams
  BEAMS = range(1,181)
  home_dir = os.environ['HOME']
  # read in beam data
  for k in BEAMS:
    if k <= 90:
      fits_num = k
      infile_name_re_x = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + 'x_Re_x.fits'
      infile_name_im_x = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + 'x_Im_x.fits'
      infile_name_re_y = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + 'x_Re_y.fits'
      infile_name_im_y = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + 'x_Im_y.fits'
    else:
      fits_num = k - 90
      infile_name_re_x = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + 'y_Re_x.fits'
      infile_name_im_x = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + 'y_Im_x.fits'
      infile_name_re_y = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + 'y_Re_y.fits'
      infile_name_im_y = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + 'y_Im_y.fits'
    ns.image_re_x(k) << Meq.FITSImage(filename=infile_name_re_x,cutoff=1.0,mode=2)
    ns.image_im_x(k) << Meq.FITSImage(filename=infile_name_im_x,cutoff=1.0,mode=2)
    ns.image_re_y(k) << Meq.FITSImage(filename=infile_name_re_y,cutoff=1.0,mode=2)
    ns.image_im_y(k) << Meq.FITSImage(filename=infile_name_im_y,cutoff=1.0,mode=2)

    ns.beam_squared(k) << ns.image_re_x(k) * ns.image_re_x(k) + ns.image_im_x(k) * ns.image_im_x(k) + ns.image_re_y(k) * ns.image_re_y(k) + ns.image_im_y(k) * ns.image_im_y(k)
    ns.beam_sqrt(k) << Meq.Sqrt(ns.beam_squared(k))
    ns.normalize(k) << Meq.Max(ns.beam_sqrt(k))
    ns.beam_re_x(k) << ns.image_re_x(k) / ns.normalize(k)
    ns.beam_im_x(k) << ns.image_im_x(k) / ns.normalize(k)
    ns.beam_re_y(k) << ns.image_re_y(k) / ns.normalize(k)
    ns.beam_im_y(k) << ns.image_im_y(k) / ns.normalize(k)
    ns.beam_x(k) << Meq.ToComplex(ns.beam_re_x(k), ns.beam_im_x(k))
    ns.beam_y(k) << Meq.ToComplex(ns.beam_re_y(k), ns.beam_im_y(k))
    ns.resampler_x(k) << Meq.Resampler(ns.beam_x(k), dep_mask=0xff)
    ns.beam_response_x(k) <<Meq.Compounder(children=[ns.beam_pos,ns.resampler_x(k)],common_axes=[hiid('l'),hiid('m')])
    ns.beam_weight(k) << Meq.ConjTranspose(ns.beam_response_x(k))
    ns.wt_beam_x(k) << ns.beam_x(k) * ns.beam_weight(k)
    ns.wt_beam_y(k) << ns.beam_y(k) * ns.beam_weight(k)
    ns.resampler_wt_x(k) << Meq.Resampler(ns.wt_beam_x(k), dep_mask=0xff)
    ns.resampler_wt_y(k) << Meq.Resampler(ns.wt_beam_y(k), dep_mask=0xff)

  ns.beam_wt_sum << Meq.Add(*[ns.beam_weight(k) for k in BEAMS])

  E_JONES = range(1,91)

# now create a source and observe it
# nodes for phase center
  ns.radec0 = Meq.Composer(ns.ra<<0,ns.dec<<0);

  # nodes for array reference position
  ns.xyz0 = Meq.Composer(ns.x0<<0,ns.y0<<0,ns.z0<<0);

  # now define per-station stuff: XYZs and UVWs
  for p in ANTENNAS:
    # positions and uvw
    ns.xyz(p) << Meq.Composer(ns.x(p)<<0,ns.y(p)<<0,ns.z(p)<<0);
    ns.uvw(p) << Meq.Negate(Meq.UVW(radec=ns.radec0,xyz_0=ns.xyz0,xyz=ns.xyz(p)));

  # define source brightness B0 (unprojected, same for all sources)
  ns.B0 << 0.5 * Meq.Matrix22(I+Q,Meq.ToComplex(U,V),Meq.ToComplex(U,-V),I-Q);

  # source l,m,n-1 vectors
  for src in SOURCES:
    l_off,m_off = LM[src];
    print 'l_off m_off ', l_off, ' ', m_off
    l = l_beam + l_off
    m = m_beam + m_off
    n = math.sqrt(1-l*l-m*m);
    ns.lmn_minus1(src) << Meq.Composer(l,m,n-1);
    # and the projected brightness...
# don't really need to use the following for a point source
    ns.B(src) << ns.B0 / n;
    for k in BEAMS:
      ns.source_beam_l(src,k) << l 
      ns.source_beam_m(src,k) << m
      ns.lm_offset(src,k) << Meq.Composer(ns.source_beam_l(src,k),ns.source_beam_m(src,k))
      ns.voltage_x(src,k) <<Meq.Compounder(children=[ns.lm_offset(src,k),ns.wt_resampler_x(k)],common_axes=[hiid('l'),hiid('m')])
      ns.voltage_y(src,k) <<Meq.Compounder(children=[ns.lm_offset(src,k),ns.wt_resampler_y(k)],common_axes=[hiid('l'),hiid('m')])

    ns.voltage_sum_x(src) << Meq.Add(*[ns.voltage_x(src,k) for k in BEAMS]) / ns.beam_wt_sum
    ns.voltage_sum_y(src) << Meq.Add(*[ns.voltage_y(src,k) for k in BEAMS]) / ns.beam_wt_sum
# now define E Jones matrices
    ns.E(src) << Meq.Matrix22(ns.voltage_sum_x(src,k), ns.voltage_sum_y(src,k+90),ns.voltage_sum_y(src,k), ns.voltage_sum_x(src,k+90))
    ns.Et(src) << Meq.ConjTranspose(ns.E(src));

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
        Meq.MatrixMultiply(ns.E(src),ns.K(p,src),ns.B(src),ns.Kt(q,src),ns.Et(src));
#       Meq.MatrixMultiply(ns.K(p,src),ns.B(src),ns.Kt(q,src));
    # and sum them up via an Add node
    predict = ns.predict(p,q) << Meq.Add(*[ns.predict(p,q,src) for src in SOURCES])
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
      tile_size        = 40
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
  
