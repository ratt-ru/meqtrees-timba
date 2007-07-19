#!/usr/bin/python

#% $Id: MG_AGW_project2a.py 3929 2006-09-01 20:17:51Z twillis $ 

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

# script_name = 'MG_AGW_project2a.py'

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

# to force caching put 100
Settings.forest_state.cache_policy = 100

# define antenna list
ANTENNAS = range(1,28);
# derive interferometer list
IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ];

# MEP table for derived quantities fitted in this script
mep_beam_locations = 'beam_locations.mep';

# source flux (same for all sources)
I = 1; Q = .2; U = .2; V = .2;

# location of 'phased up' beam
#BEAM_LM = [(-0.001,-0.001)]
#BEAM_LM = [(0.001,0.0)]
BEAM_LM = [(-0.001,0.0)]
# we'll put the sources on a grid (positions relative to beam centre in radians)
LM = [(-0.0005,-0.0005),(-0.0005,0),(-0.0005,0.0005),
      ( 0,-0.0005),( 0,0),( 0,0.0005),
      ( 0.0005,-0.0005),( 0.0005,0),( 0.0005,0.0005)];
SOURCES = range(len(LM));       # 0...N-1

########################################################
def _define_forest(ns):  

# read in beam images
  BEAMS = range(1,101)
  home_dir = os.environ['HOME']
  for k in BEAMS:
    infile_name = ""
    if k <= 25:
      fits_num = k
      infile_name = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + '.fits'
    elif k > 25 and k <= 50:
      fits_num = k - 25
      infile_name = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + '_90.fits'
    elif k > 50 and k <= 75:
      fits_num = k - 50
      infile_name = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + '_180.fits'
    elif k > 75:
      fits_num = k - 75
      infile_name = home_dir + '/brisken_stuff/311MHz/311MHz_beam_' + str(fits_num) + '_270.fits'
    ns.image(k) << Meq.FITSImage(filename=infile_name,cutoff=1.0,mode=2)
    ns.resampler(k) << Meq.Resampler(ns.image(k), dep_mask=0xff)

# get positions of beam peaks from mep table
    ns.l0(k)<< Meq.Parm(table_name=mep_beam_locations)
    ns.m0(k)<< Meq.Parm(table_name=mep_beam_locations)
    ns.lm(k)<<Meq.Composer(ns.l0(k),ns.m0(k))

# now create a source and observe it
 # nodes for phase center
  ns.radec0 = Meq.Composer(ns.ra<<0,ns.dec<<0);

  # nodes for array reference position
  ns.xyz0 = Meq.Composer(ns.x0<<0,ns.y0<<0,ns.z0<<0);

  # now define per-station stuff: XYZs and UVWs
  for p in ANTENNAS:
    # positions and uvw
    ns.xyz(p) << Meq.Composer(ns.x(p)<<0,ns.y(p)<<0,ns.z(p)<<0);
    ns.uvw(p) << Meq.UVW(radec=ns.radec0,xyz_0=ns.xyz0,xyz=ns.xyz(p));

# now compute the weighted beam response here
  l_beam,m_beam = BEAM_LM[0]
  ns.l_beam  << Meq.Parm(l_beam,node_groups='Parm')
  ns.m_beam  << Meq.Parm(m_beam,node_groups='Parm')
  for k in BEAMS:
    ns.l_offset(k) << ns.l0(k) - ns.l_beam
    ns.m_offset(k) << ns.m0(k) - ns.m_beam
    ns.beam_weight(k) << 1.0 / Meq.Sqrt(Meq.Sqr(ns.l_offset(k)) + Meq.Sqr(ns.m_offset(k)))
  ns.weighted_mean << Meq.Add(*[ns.beam_weight(k) for k in BEAMS]) 


  # define source brightness B0 (unprojected, same for all sources)
  ns.B0 << 0.5 * Meq.Matrix22(I+Q,Meq.ToComplex(U,V),Meq.ToComplex(U,-V),I-Q);

  # source l,m,n-1 vectors
  for src in SOURCES:
    l_off,m_off = LM[src];
    print 'l_off m_off ', l_off, ' ', m_off
    l = l_beam - l_off
    m = m_beam - m_off
    n = math.sqrt(1-l*l-m*m);
    ns.lmn_minus1(src) << Meq.Composer(l,m,n-1);
    # and the projected brightness...
# don't really need to use the following for a point source
    ns.B(src) << ns.B0 / n;

# create L,M offset of source with respect to 'phased' beam centre
    ns.l_pos(src) << l - ns.l_beam 
    ns.m_pos(src) << m - ns.m_beam 

# now compute the mean beam gain here
    for k in BEAMS:
      ns.source_beam_l(src,k) << ns.l0(k) + ns.l_pos(src)
      ns.source_beam_m(src,k) << ns.m0(k) + ns.m_pos(src)
      ns.lm_offset(src,k) << Meq.Composer(ns.source_beam_l(src,k),ns.source_beam_m(src,k))
      ns.beam_gain(src,k)<<Meq.Compounder(children=[ns.lm_offset(src,k),ns.resampler(k)],common_axes=[hiid('l'),hiid('m')]) * ns.beam_weight(k)
    ns.E(src) << Meq.Sqrt(Meq.Add(*[ns.beam_gain(src,k) for k in BEAMS]) / ns.weighted_mean)
    ns.Et(src) << Meq.ConjTranspose(ns.E(src));

 # define K-jones matrices
  for p in ANTENNAS:
    for src in SOURCES:
      ns.K(p,src) << Meq.VisPhaseShift(lmn=ns.lmn_minus1(src),uvw=ns.uvw(p));
      ns.Kt(p,src) << Meq.ConjTranspose(ns.K(p,src));
    # reset gains
    ns.G(p) << 1;
    ns.Gt(p) << Meq.ConjTranspose(ns.G(p));

  # now define predicted visibilities, attach to sinks
  for p,q in IFRS:
    # make per-source predicted visibilities
    for src in SOURCES:
      ns.predict(p,q,src) << \
        Meq.MatrixMultiply(ns.E(src),ns.K(p,src),ns.B(src),ns.Kt(q,src),ns.Et(src));
#       Meq.MatrixMultiply(ns.K(p,src),ns.B(src),ns.Kt(q,src));
    # and sum them up via an Add node
    predict = ns.predict(p,q) << Meq.MatrixMultiply(
                ns.G(p),
                Meq.Add(*[ns.predict(p,q,src) for src in SOURCES]),
                ns.Gt(q));
    ns.sink(p,q) << Meq.Sink(predict,station_1_index=p-1,station_2_index=q-1,output_col='DATA');

  # define VisDataMux
  ns.vdm << Meq.VisDataMux(*[ns.sink(p,q) for p,q in IFRS]);

########################################################################

def _test_forest(mqs,parent):

# now observe sources
  req = meq.request();
  req.input = record(
    ms = record(
      ms_name          = 'TEST_XNTD_30_640.MS',
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
  
