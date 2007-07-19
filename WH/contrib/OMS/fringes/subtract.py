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
from numarray import *
import os
import random
import models

import Meow

from Meow.IfrArray import IfrArray
from Meow.Observation import Observation
from Meow.Patch import Patch
from Meow import Jones
from Meow import Bookmarks
from Meow import Utils

# MS name
Utils.include_ms_options(
  tile_sizes=[30,48,60,96,480,960,2400]);

# number of stations
TDLCompileOption('num_stations',"Number of stations",[27,14,3]);

TDLCompileOption('apply_g_jones',"Apply G Jones corrections",False);

# source model
TDLCompileOption('source_model',"Source model",[
    models.cps,
    models.cps_plus_faint_extended,
    models.two_point_sources,
    models.two_bright_one_faint_point_source
  ],default=0);

# number of timeslots to use at once
TDLRuntimeOption('imaging_mode',"Imaging mode",["mfs","channel"]);

# bookmarks
Settings.forest_state = record(bookmarks=[
  record(name='Visibilities',page=Bookmarks.PlotPage(
      ["spigot:1:2",
       "spigot:1:6","spigot:9:%d"%num_stations],
      ["visibility:all:1:2","visibility:all:1:6",
       "visibility:all:9:%d"%num_stations],
      ["subtract:1:2",
       "subtract:1:6","subtract:9:%d"%num_stations]
  )),
  record(name='Phases',page=Bookmarks.PlotPage(
      ["phase:1","phase:2","phase:3"],
      ["phase:4","phase:5","phase:6"],
      ["phase:7","phase:8","phase:9"],
      ["phase:10","phase:11","phase:12"]
  ))
]);


    
def _define_forest(ns):
  # create array model
  stations = range(1,num_stations+1);
  array = IfrArray(ns,stations);
  observation = Observation(ns);
  
  # create ource model
  # create nominal source model by calling the specified function
  global source_list;
  source_list = source_model(ns,Utils.get_source_table());
  allsky = Patch(ns,'all',observation.phase_centre);
  allsky.add(*source_list);
  
  # ns.time << Meq.Time;
  # ns.freq << Meq.Freq;

  if apply_g_jones:
    for station in array.stations():
      # take a random starting phase for this station
      ns.phase(station) << Meq.Parm(0,table_name=Utils.get_mep_table());
      diag = ns.Gdiag(station) << Meq.Polar(1,ns.phase(station));
      ns.G(station) << Meq.Matrix22(diag,0,0,diag);

  predict = allsky.visibilities(array,observation);
  
  # create spigots
  for sta1,sta2 in array.ifrs():
    ns.spigot(sta1,sta2) << Meq.Spigot( station_1_index=sta1-1,
                                        station_2_index=sta2-1,
                                        flag_bit=4,
                                        input_col='DATA');
                                        
  # create corrected visibilities if needed
  if apply_g_jones:
    corrected = ns.corrected;
    Jones.apply_correction(ns.corrected,ns.spigot,ns.G,array.ifrs());
  else:
    corrected = ns.spigot;
  
  # create sinks, subtract model and write out
  for sta1,sta2 in array.ifrs():
    subtract = ns.subtract(sta1,sta2) << corrected(sta1,sta2) - predict(sta1,sta2);
    ns.sink(sta1,sta2) << Meq.Sink(station_1_index=sta1-1,
                                   station_2_index=sta2-1,
                                   flag_bit=4,
                                   corr_index=[0,1,2,3],
                                   flag_mask=-1,
                                   output_col='DATA',
                                   children=subtract
                                   );
  # set a good sink poll order for optimal parallelization
  # this is an optional step
  cpo = [];
  for i in range(array.num_stations()/2):
    (ant1,ant2) = array.stations()[i*2:(i+1)*2];
    cpo.append(ns.sink(ant1,ant2).name);
  # create visdata mux
  ns.VisDataMux << Meq.VisDataMux(child_poll_order=cpo);
  ns.VisDataMux.add_children(*[ns.sink(ant1,ant2) for (ant1, ant2) in array.ifrs()]);


def _tdl_job_1_subtract_model_from_data (mqs,parent,write=True):
  req = Utils.create_io_request();
  mqs.clearcache('VisDataMux',recursive=False);
  mqs.execute('VisDataMux',req,wait=(parent is None));
  pass

def _tdl_job_2_make_dirty_image (mqs,parent,**kw):
  os.spawnvp(os.P_NOWAIT,'glish',['glish','-l','make_image.g',Utils.output_column,
      'ms='+Utils.msname,'mode='+imaging_mode]);


Settings.forest_state.cache_policy = 100;  # 1 for smart caching, 100 for full caching

Settings.orphans_are_roots = False;


def _test_compilation ():
  ns = NodeScope();
  _define_forest(ns);
  ns.Resolve();

if __name__ == '__main__':
  if '-prof' in sys.argv:
    import profile
    profile.run('_test_compilation()','clar_fast_predict.prof');
  else:
#    Timba.TDL._dbg.set_verbose(5);
    _test_compilation();
              
