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
from Meow import Jones
from Meow import Bookmarks
from Meow import Utils


Utils.include_ms_options(
  tile_sizes=[30,48,60,96,480,960,2400]);

# number of stations
TDLCompileOption('num_stations',"Number of stations",[27,14,3]);

TDLCompileOption('phase_scale_time',"Max. phase variation in time (deg)",[30,60,90,180]);
TDLCompileOption('phase_scale_freq',"Max. phase variation in freq (deg)",[30,60,90,180]);
# phase noise
TDLCompileOption('phase_stddev',"Add phase noise (deg)",[None,0.5,1,2,5,10]);

# if not None, a per-ifr noise term with the given stddev will be added
TDLCompileOption('noise_stddev',"Add background noise (Jy)",[0,1e-9,1e-8,1e-6,5e-6,1e-3,0.05,0.1,0.33,0.5]);

# number of timeslots to use at once
TDLRuntimeOption('imaging_mode',"Imaging mode",["mfs","channel"]);
  

# bookmarks
Settings.forest_state = record(bookmarks=[
  record(name='Visibilities',page=Bookmarks.PlotPage(
      ["spigot:1:2",
       "spigot:1:6","spigot:9:%d"%num_stations],
      ["corrupt_vis:1:2",
       "corrupt_vis:1:6","corrupt_vis:9:%d"%num_stations],
      ["noisy_predict:1:2",
       "noisy_predict:1:6","noisy_predict:9:%d"%num_stations]
  )),
  record(name='Phases',page=Bookmarks.PlotPage(
      ["phase:1","phase:2","phase:3"],
      ["phase:4","phase:5","phase:6"],
      ["phase:7","phase:8","phase:9"],
      ["phase:10","phase:11","phase:12"]
  ))
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
  array = IfrArray(ns,stations,mirror_uvw=True);
  
  # Now, create a series of G Jones for simulated phase gradients
  ns.time << Meq.Time;
  ns.freq << Meq.Freq;

  # rel_freq is just a node whose value goes from 0 to 1 over the band
  ns.rel_freq << (ns.freq - models.ref_frequency)/models.ref_bandwidth;

  ph_scale_time_rad = phase_scale_time*(math.pi/180);
  ph_scale_freq_rad = phase_scale_freq*(math.pi/180);

  for station in array.stations():
    # take a random starting phase for this station
    phase0 = random.uniform(-math.pi,math.pi);
    # model phase evolution in time by a sine
    # we want phase to be linear over, say, 10 timeslots
    # (10 minutes), so the sine period should be hours
    time_period = random.uniform(7200,9000) / (2*math.pi);
    # in frequency, we'll use a linear phase slope
    # going from 0 to +/-PHS (where PHS is random and <phase_scale)
    #  over the whole band
    freq_slope = random.uniform(-ph_scale_freq_rad,ph_scale_freq_rad);
    # also, make the slope vary slowly in time
    freq_slope_period = random.uniform(7200,9000) / (2*math.pi);
    # so, this is the freq component of the phase
    ns.phase_fq(station) << phase0 + ns.rel_freq*freq_slope*Meq.Sin(ns.time/freq_slope_period);
    # the time component of the phase
    ns.phase_tm(station) << ph_scale_time_rad*Meq.Sin(ns.time/time_period);
    # compute actual phase as sum of two components, plus a bit of noise
    # for good measure
    if phase_stddev is not None:
      ns.phase(station) << ns.phase_fq(station)+ns.phase_tm(station) \
                    +Meq.GaussNoise(stddev=phase_stddev*math.pi/180);
    else:
      ns.phase(station) << ns.phase_fq(station)+ns.phase_tm(station);
    ns.G(station) << Meq.Polar(1,ns.phase(station));
  # attach the G Jones series to the all-sky patch

  # create per-antenna noise term
  for sta in array.stations():
    ns.noise(sta) << noise_matrix(noise_stddev/2);
    
  # create spigots
  for sta1,sta2 in array.ifrs():
    ns.spigot(sta1,sta2) << Meq.Spigot( station_1_index=sta1-1,
                                        station_2_index=sta2-1,
                                        flag_bit=4,
                                        input_col='DATA');
  # create corrupted visibilities
  Jones.apply_corruption(ns.corrupt_vis,ns.spigot,ns.G,array.ifrs());
  
  # create sinks, add in noise term
  for sta1,sta2 in array.ifrs():
    predict = ns.noisy_predict(sta1,sta2) << \
        ns.corrupt_vis(sta1,sta2) + ns.noise(sta1) + ns.noise(sta2);
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


def _tdl_job_1_corrupt_ms_data (mqs,parent,write=True):
  req = Utils.create_io_request();
  mqs.clearcache('VisDataMux',recursive=False);
  mqs.execute('VisDataMux',req,wait=(parent is None));
  pass

def _tdl_job_2_make_dirty_image (mqs,parent,**kw):
  os.spawnvp(os.P_NOWAIT,'glish',['glish','-l','make_image.g',
      Utils.output_column,'ms='+Utils.msname,'mode='+imaging_mode]);


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
              
