#!/usr/bin/python

#% $Id: MG_AGW_project2a.py 3929 2006-09-01 20:17:51Z twillis $ 

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

script_name = 'MG_AGW_project2a.py'

# Short description:
# We read in a 3 x 3 grid of sources, and essentially observe them
# with a single 'phased up' beam located at the BEAM_LM position


# History:
# - 24 Oct 2006: creation:

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

# setup a few boomars
Settings.forest_state = record(bookmarks=[
  Meow.Bookmarks.PlotPage("EJones",["E:0"]),
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

# location of 'phased up' beam - put at field centre
BEAM_LM = [(0.0,0.0)]
# we'll put the sources on a grid (positions relative to beam centre in radians)
#LM = [(0.01, 0.0)]   # using this LM works
LM = [(0.0, 0.0)]     # using this LM causes crash
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
  BEAMS_1 = range(1,91)
  BEAMS_2 = range(91,181)
  home_dir = os.environ['HOME']
  # read in beam data

  infile_name_re_x = './demo_beam.fits'
  infile_name_im_x = './demo_beam.fits'
  infile_name_re_y = './demo_beam.fits'
  infile_name_im_y = './demo_beam.fits'
  ns.image_re_x << Meq.FITSImage(filename=infile_name_re_x,cutoff=1.0,mode=2)
  ns.image_im_x << Meq.FITSImage(filename=infile_name_im_x,cutoff=1.0,mode=2)
  ns.image_re_y << Meq.FITSImage(filename=infile_name_re_y,cutoff=1.0,mode=2)
  ns.image_im_y << Meq.FITSImage(filename=infile_name_im_y,cutoff=1.0,mode=2)

  ns.beam_squared << ns.image_re_x * ns.image_re_x + ns.image_im_x * ns.image_im_x + ns.image_re_y * ns.image_re_y + ns.image_im_y * ns.image_im_y
  ns.beam_sqrt << Meq.Sqrt(ns.beam_squared)
  ns.normalize << Meq.Max(ns.beam_sqrt)
  ns.beam_re_x << ns.image_re_x() / ns.normalize
  ns.beam_im_x << ns.image_im_x() / ns.normalize
  ns.beam_re_y << ns.image_re_y() / ns.normalize
  ns.beam_im_y << ns.image_im_y() / ns.normalize
  ns.beam_x << Meq.ToComplex(ns.beam_re_x, ns.beam_im_x)
  ns.beam_y << Meq.ToComplex(ns.beam_re_y, ns.beam_im_y)
  ns.resampler_x << Meq.Resampler(ns.beam_x, dep_mas=0xff)
  ns.resampler_y << Meq.Resampler(ns.beam_y, dep_mas=0xff)
  ns.beam_response_x <<Meq.Compounder(children=[ns.beam_pos,ns.resampler_x],common_axes=[hiid('l'),hiid('m')])

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
    ns.source_beam_l(src) << l 
    ns.source_beam_m(src) << m
    ns.lm_offset(src) << Meq.Composer(ns.source_beam_l(src),ns.source_beam_m(src))
    ns.voltage_x(src) <<Meq.Compounder(children=[ns.lm_offset(src),ns.resampler_x],common_axes=[hiid('l'),hiid('m')])
    ns.voltage_y(src) <<Meq.Compounder(children=[ns.lm_offset(src),ns.resampler_y],common_axes=[hiid('l'),hiid('m')])
    ns.E(src)<< Meq.Matrix22(ns.voltage_x(src), 0.0+0.0j, 0.0+0.0j,ns.voltage_y(src))
  
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
      tile_size        = 960
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
  
