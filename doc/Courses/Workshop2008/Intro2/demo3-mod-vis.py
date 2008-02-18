# standard preamble
#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
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
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *
from Timba.Meq import meq
import cmath

# define antenna list
ANTENNAS = range(1,28);
# derive interferometer list
IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ];

TDLRuntimeOption('tile_size',"Tile size",[5,10,20,30,100]);


def _define_forest (ns):
  # loop over all baselines
  for p,q in IFRS:
    spigot = ns.spigot(p,q) << Meq.Spigot(input_column='DATA',station_1_index=p-1,station_2_index=q-1);
    gain = (1+p/10.)*cmath.exp(complex(0,1)*q/3.*2*cmath.pi); 
    modvis = ns.mod_vis(p,q) << spigot*gain;
    ns.sink(p,q) << Meq.Sink(modvis,station_1_index=p-1,station_2_index=q-1,output_col='DATA');

  # define a couple of inspector nodes
  ns.inspect_input << Meq.Composer(
    dims=[0],   # compose in tensor mode
    plot_label=["%s-%s"%(p,q) for p,q in IFRS],
    *[Meq.Mean(ns.spigot(p,q),reduction_axes="freq") for p,q in IFRS]
  );
  ns.inspect_output << Meq.Composer(
    dims=[0],   # compose in tensor mode
    plot_label=["%s-%s"%(p,q) for p,q in IFRS],
    *[Meq.Mean(ns.mod_vis(p,q),reduction_axes="freq") for p,q in IFRS]
  );
  ns.inspectors = Meq.ReqMux(ns.inspect_input,ns.inspect_output);
  
  # create VDM and attach inspectors
  ns.VisDataMux = Meq.VisDataMux(post=ns.inspectors);


def _test_forest (mqs,parent):
  # create an I/O request
  req = meq.request();
  req.input = record( 
    ms = record(  
      ms_name          = 'demo.MS',
      tile_size        = tile_size,
      data_column_name = 'DATA',
    ),
  );
  req.output = record( 
    ms = record(  
      data_column = 'MODEL_DATA',
    ),
  );
  # execute    
  mqs.execute('VisDataMux',req,wait=False);


# setup a few bookmarks
Settings.forest_state = record(bookmarks=[
  record(name='Spigots',page=[
    record(udi="/node/spigot:1:2",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/spigot:9:27",viewer="Result Plotter",pos=(0,1)),
    record(udi="/node/mod_vis:1:2",viewer="Result Plotter",pos=(1,0)),
    record(udi="/node/mod_vis:9:27",viewer="Result Plotter",pos=(1,1)) \
  ]),
  record(name='Inspectors',page=[
    record(udi="/node/inspect_input",viewer="Collections Plotter",pos=(0,0)),
    record(udi="/node/inspect_output",viewer="Collections Plotter",pos=(1,0))
  ]),
]);





# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
