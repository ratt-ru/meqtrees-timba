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
import os.path

import models
import Meow
from Meow.IfrArray import IfrArray
from Meow.Observation import Observation
from Meow.Patch import Patch
from Meow import Bookmarks
from Meow.FITSImageComponent import FITSImageComponent
from Meow import Utils

Utils.include_ms_options(has_input=False,
  tile_sizes=[30,48,60,96,480,960,2400]);

# number of stations
TDLCompileOption('num_stations',"Number of stations",[27,14,3]);

# which source model to use
TDLCompileOption('source_model',"Source model",[
    models.two_point_sources,
    models.two_point_sources_plus_faint_extended,
    models.cps,
    models.cps_plus_faint_extended,
    models.two_bright_one_faint_point_source,
    models.two_point_sources_plus_grid,
    models.two_point_sources_plus_random,
    models.two_point_sources_plus_random_uJy,
    models.two_point_sources_plus_random_nJy
  ],default=0);

TDLCompileOption('background_image',"Background sky image",[None,'sky-image.fits']);
TDLCompileOption('background_flux_scale',"Rescale background flux",[None,1e-3,1e-6,1e-9,1e-10]);

# number of timeslots to use at once
TDLRuntimeOption('imaging_mode',"Imaging mode",["mfs","channel"]);
  
# bookmarks
Settings.forest_state = record(bookmarks=[
  record(name='Predicted visibilities',page=Bookmarks.PlotPage(
      ["visibility:S1:1:2",
       "visibility:S1:1:6","visibility:S1:9:%d"%num_stations ],
      ["visibility:S5:1:2",
       "visibility:S5:1:6","visibility:S5:9:%d"%num_stations ],
      ["visibility:all:1:2",
       "visibility:all:1:6","visibility:all:9:%d"%num_stations]
  ))
]);


    
def _define_forest(ns):
  # create array model
  stations = range(1,num_stations+1);
#  array = IfrArray(ns,stations,uvw_table=mep_derived,mirror_uvw=True);
  array = IfrArray(ns,stations);
  observation = Observation(ns);
  
  # create nominal source model by calling the specified function
  source_list = source_model(ns);
  
  # add background image if needed
  if background_image:
    img = FITSImageComponent(ns,'IMG',filename=background_image,
          fluxscale=background_flux_scale,
          direction=observation.phase_centre);
    img.set_options(fft_pad_factor=2);
    source_list.append(img);
   
  # create all-sky patch for source model
  allsky = Patch(ns,'all',observation.phase_centre);
  allsky.add(*source_list);
  
  # create simulated visibilities for sky
  visibilities = allsky.visibilities(array,observation);
  
  # create the sinks and attach predicts to them, adding in a noise term
  for sta1,sta2 in array.ifrs():
    predict = visibilities(sta1,sta2);
    ns.sink(sta1,sta2) << Meq.Sink(station_1_index=sta1-1,
                                   station_2_index=sta2-1,
                                   flag_bit=4,
                                   corr_index=[0,1,2,3],
                                   flag_mask=-1,
                                   output_col='DATA',
                                   children=predict
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

def _tdl_job_1_write_simulated_ms (mqs,parent,write=True):
  req = Utils.create_io_request();
  mqs.clearcache('VisDataMux',recursive=False);
  mqs.execute('VisDataMux',req,wait=(parent is None));
  pass

def _tdl_job_2_make_dirty_image (mqs,parent,**kw):
  os.spawnvp(os.P_NOWAIT,'glish',['glish','-l','make_image.g',Utils.output_column,
      'ms='+Utils.msname,'mode='+imaging_mode]);


Settings.forest_state.cache_policy = 1;  # 1 for smart caching, 100 for full caching

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
              
