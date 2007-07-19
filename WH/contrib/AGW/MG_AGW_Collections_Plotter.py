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

# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

# define antenna list
ANTENNAS = range(1,31);
# derive interferometer list
IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ];

# useful constant: 1 deg in radians
DEG = math.pi/180.;

# source parameters
I = 1; Q = .2; U = .2; V = .2;
L = 1*(DEG/60);
M = 1*(DEG/60);
N = math.sqrt(1-L*L-M*M);


def _define_forest (ns):
  # nodes for phase center
  ns.radec0 = Meq.Composer(ns.ra<<0,ns.dec<<0);
  
  # nodes for array reference position
  ns.xyz0 = Meq.Composer(ns.x0<<0,ns.y0<<0,ns.z0<<0);
  
  # now define per-station stuff: XYZs and UVWs 
  for p in ANTENNAS:
    # positions and uvw
    ns.xyz(p) << Meq.Composer(ns.x(p)<<0,ns.y(p)<<0,ns.z(p)<<0);
    ns.uvw(p) << Meq.UVW(radec=ns.radec0,xyz_0=ns.xyz0,xyz=ns.xyz(p));
  
  # source l,m,n-1 vector
  ns.lmn_minus1 << Meq.Composer(L,M,N-1);
  
  # define K-jones matrices
  for p in ANTENNAS:
    ns.K(p) << Meq.VisPhaseShift(lmn=ns.lmn_minus1,uvw=ns.uvw(p));
    ns.Kt(p) << Meq.ConjTranspose(ns.K(p));
  
  # define source brightness, B
  ns.B << 0.5 * Meq.Matrix22(I+Q,Meq.ToComplex(U,V),Meq.ToComplex(U,-V),I-Q);
  
  # now define predicted visibilities, attach to sinks
  for p,q in IFRS:
    predict = ns.predict(p,q) << \
      Meq.MatrixMultiply(ns.K(p),ns.B,ns.Kt(q));
    ns.sink(p,q) << Meq.Sink(predict,station_1_index=p-1,station_2_index=q-1,output_col='DATA');

# use the following node to get a single visibility averaged
# over a time-frequency cell / tile
#   ns.collector(p,q) << Meq.Mean(predict,reduction_axes=["time", "freq"]);

# use the following node to show spectra coming in averaged over 
# a time block; each spectrum is appended to the streaming display
# of the Collections Plotter bookmark
#   ns.collector(p,q) << Meq.Mean(predict,reduction_axes="time");

# use the following node to show spectra averaged over frequency
# for each integration in a time block (tile) 
# this equates to getting the Collections Plotter bookmark
# to plot standard 'continuum' visibilities as a function of time. 
    ns.collector(p,q) << Meq.Mean(predict,reduction_axes="freq");
    
  ns.collector << Meq.Composer(dims=[0],
                  plot_label=[ "%s-%s"%(p,q) for p in ANTENNAS for q in ANTENNAS if p<q ],
                  tab_label = 'XNTD',
                  *[ns.collector(p,q) for p,q in IFRS]);
  # define VisDataMux
  ns.vdm << Meq.VisDataMux(post=ns.collector,*[ns.sink(p,q) for p,q in IFRS]);
  

def _tdl_job_1_show_MS (mqs,parent):
  # create an I/O request
  req = meq.request();
  req.input = record( 
    ms = record(  
      ms_name          = 'TEST_XNTD_30_960.MS',
      tile_size        = 60
    ),
    python_init = 'Meow.ReadVisHeader'
  );
  req.output = record( 
    ms = record( 
      data_column = 'MODEL_DATA' 
    )
  );
  # execute    
  mqs.execute('vdm',req,wait=False);


# setup a bookmark
Settings.forest_state = record(bookmarks=[
  record(name='Collector',page=[
    record(udi="/node/collector",viewer="Collections Plotter",pos=(0,0))])]);
Settings.forest_state.cache_policy = 100

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
