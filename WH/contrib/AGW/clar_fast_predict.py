
#% $Id$ 

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

from Timba.TDL import *
from Timba.Meq import meq
from numarray import *
import os
import random

import clar_model 
import Meow
from Meow.IfrArray import IfrArray
from Meow.Observation import Observation
from Meow.Patch import Patch
from Meow.CorruptComponent import CorruptComponent
from Meow import Bookmarks,Utils

Utils.include_ms_options(has_input=False,
  tile_sizes=[30,48,60,96,480,960,2400]);
Utils.include_imaging_options();

# number of stations
TDLCompileOption('num_stations',"Number of stations",[27,14,3]);

# if true, a G Jones simulating phase and gain errors will be inserted
TDLCompileOption('add_g_jones',"Simulate G Jones",False);

# if true, an E Jones simulating beam effects will be inserted
TDLCompileOption('add_e_jones',"Simulate E Jones",True);

# if not None, a per-ifr noise term with the given stddev will be added
TDLCompileOption('noise_stddev',"Noise level",[None,0.05,0.1,1.0,10.0]);

# which source model to use
# source_model = clar_model.point_and_extended_sources;
TDLCompileOption('source_model',"Source model",[
    clar_model.point_and_extended_sources,
    clar_model.point_sources_only,
    clar_model.radio_galaxy,
    clar_model.faint_source
  ],default=0);
  
# MEP table for various derived quantities 
mep_derived = 'CLAR_DQ_27-480.mep';

# bookmarks
Settings.forest_state = record(bookmarks=[
  record(name='Predicted visibilities',page=Bookmarks.PlotPage(
      ["visibility:S1:1:2",
       "visibility:S1:1:6","visibility:S1:9:%d"%num_stations ],
      ["visibility:S1:E:1:2",
       "visibility:S1:E:1:6","visibility:S1:E:9:%d"%num_stations ],
      ["E:S1:1","E:S1:%d"%num_stations,"G:1"],
      ["visibility:all:1:2",
       "visibility:all:18:27","visibility:all:9:%d"%num_stations]
  )),
  record(name='Beams',page=Bookmarks.PlotPage(
      ["E:S1:1","E:S2:1","E:S3:1"],
      ["E:S6:1","E:S9:1","E:S10:1"],
      ["E:S1:%d"%num_stations,"E:S2:%d"%num_stations,"E:S3:%d"%num_stations],
      ["E:S6:%d"%num_stations,"E:S9:%d"%num_stations,"E:S10:%d"%num_stations]
  )),
  record(name='G Jones',page=Bookmarks.PlotPage(
      ["G:1","G:2","G:3"],
      ["G:4","G:5","G:6"],
      ["G:7","G:8","G:9"],
      ["G:10","G:11","G:12"]
  )),
  record(name='Source fluxes',page=Bookmarks.PlotPage(
      ["I:S1","I:S2","I:S3"],
      ["I:S4","I:S5","I:S6"],
      ["I:S7","I:S8","I:S9"],
      ["I:S10","hpbw"]
  )),
  record(name="Sources 1/2",page=Bookmarks.PlotPage(
      ["visibility:S1:1:2",
       "visibility:S1:1:6","visibility:S1:9:%d"%num_stations ],
      ["visibility:S2p:1:2",
       "visibility:S2p:1:6","visibility:S2p:9:%d"%num_stations ],
      ["visibility:S2e:1:2",
       "visibility:S2e:1:6","visibility:S2e:9:%d"%num_stations ]
  )),
]);


    
def noise_matrix (stddev=0.1):
  """helper function to create a 2x2 complex gaussian noise matrix""";
  noise = Meq.GaussNoise(stddev=stddev);
  return Meq.Matrix22(
    Meq.ToComplex(noise,noise),Meq.ToComplex(noise,noise),
    Meq.ToComplex(noise,noise),Meq.ToComplex(noise,noise)
  );



def _define_forest(ns):
  # create array model
  stations = range(1,num_stations+1);
  array = IfrArray(ns,stations,uvw_table=mep_derived,mirror_uvw=True);
  observation = Observation(ns);
  
  clar_model.init_directions(ns);
  # create nominal CLAR source model by calling the specified
  # function
  source_list = source_model(ns);
  
  if add_e_jones:
    Ej = clar_model.EJones(ns,array,observation,source_list);
    corrupt_list = [ 
      CorruptComponent(ns,src,label='E',station_jones=Ej(src.direction.name))
      for src in source_list
    ];
  else:
    corrupt_list = source_list;
                     
  # create all-sky patch for CLAR source model
  allsky = Patch(ns,'all',observation.phase_centre);
  allsky.add(*corrupt_list);
  
  if add_g_jones:
    # Now, create a series of G Jones for simulated phase and gain errors
    ns.time << Meq.Time;
    for station in array.stations():
      # create a random station phase 
      phase = Meq.GaussNoise(stddev=0.1);
      # create sinusoidal gain errors with random period and amplitude of 2-5%
      ns.Gx(station) << 1 + Meq.Sin(ns.time/random.uniform(500,2000)) * random.uniform(-.05,.05);
      ns.Gy(station) << 1 + Meq.Sin(ns.time/random.uniform(500,2000)) * random.uniform(-.05,.05);
      # put them together into a G matrix
      ns.G(station) << Meq.Matrix22(
        Meq.Polar(ns.Gx(station),phase),0,0,Meq.Polar(ns.Gy(station),phase));
    # attach the G Jones series to the all-sky patch
    allsky = CorruptComponent(ns,allsky,label='G',station_jones=ns.G);

  # create simulated visibilities for sky
  visibilities = allsky.visibilities(array,observation);
  
  # create the sinks and attach predicts to them, adding in a noise term
  for sta1,sta2 in array.ifrs():
    if noise_stddev is not None:
      predict = ns.noisy_predict(sta1,sta2) << \
        visibilities(sta1,sta2) + (ns.noise(sta1,sta2) << noise_matrix(noise_stddev));
    else:
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


def _tdl_job_1_clar_predict(mqs,parent,write=True):
  req = Utils.create_io_request();
  mqs.execute('VisDataMux',req,wait=False);
  pass

def _tdl_job_2_make_image (mqs,parent):
  Utils.make_dirty_image(npix=1024,cellsize='.25arcsec',channels=[32,1,1]);



Settings.forest_state.cache_policy = 1;  # 1 for smart caching, 100 for full caching

Settings.orphans_are_roots = True;


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
              
