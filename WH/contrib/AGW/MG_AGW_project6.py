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

# script_name = 'MG_AGW_project6.py'

# Short description:
# Tests MeqTrees computation of source phases


# History:
# - 4 Nov 2006: creation:

#=======================================================================
# Import of Python / TDL modules:

import math

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meq

# to force caching put 100
Settings.forest_state.cache_policy = 100

# define antenna list with 30 antennas
ANTENNAS = range(1,31);
# derive interferometer list
IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ];

# source flux (same for all sources)
I = 1; Q = .0; U = .0; V = .0;

BEAM_LM = [(0.0,0.0523598283761181)]  # offset of +3 deg in M

# we'll put the sources on a grid (positions relative to beam centre)
LM = [(-0.0087266463,-0.0087266463),(-0.0087266463,0),(-0.0087266463,0.0087266463),
      ( 0,-0.0087266463),( 0,0),( 0,0.0087266463),
      ( 0.0087266463,-0.0087266463),( 0.0087266463,0),( 0.0087266463,0.0087266463)];
SOURCES = range(len(LM));       # 0...N-1

########################################################
def _define_forest(ns):  

# nodes for phase center
  ns.radec0 = Meq.Composer(ns.ra<<0,ns.dec<<0);
# nodes for array reference position
  ns.xyz0 = Meq.Composer(ns.x0<<0,ns.y0<<0,ns.z0<<0);
# now define per-station stuff: XYZs and UVWs
  for p in ANTENNAS:
    ns.xyz(p) << Meq.Composer(ns.x(p)<<0,ns.y(p)<<0,ns.z(p)<<0);
    ns.uvw(p) << Meq.Negate(Meq.UVW(radec=ns.radec0,xyz_0=ns.xyz0,xyz=ns.xyz(p)));
  
  # define source brightness B0 (unprojected, same for all sources)
  ns.B0 << 0.5 * Meq.Matrix22(I+Q,Meq.ToComplex(U,V),Meq.ToComplex(U,-V),I-Q);

  l_beam,m_beam = BEAM_LM[0]

  # source l,m,n-1 vectors
  for src in SOURCES:
    l_src,m_src = LM[src];
    l = l_beam + l_src
    m = m_beam + m_src
    n = math.sqrt(1-l*l-m*m);
    ns.lmn_minus1(src) << Meq.Composer(l,m,n-1);
    ns.coherency(src) << ns.B0 / n;

 # define K-jones  and G-jones matrices
  for station in ANTENNAS:
    for src in SOURCES:
      ns.dft(station,src) << Meq.VisPhaseShift(lmn=ns.lmn_minus1(src),uvw=ns.uvw(station));
      ns.conjdft(station,src) << Meq.ConjTranspose(ns.dft(station,src));

  # now define predicted visibilities, attach to sinks
  for p,q in IFRS:
    # make per-source predicted visibilities
    for src in SOURCES:
      ns.predict(p,q,src) << \
        Meq.MatrixMultiply(ns.dft(p,src),ns.coherency(src),ns.conjdft(q,src));
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
  
