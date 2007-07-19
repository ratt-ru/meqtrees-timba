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

from Timba.Contrib.OMS.IfrArray import IfrArray
from Timba.Contrib.OMS.Observation import Observation
from Timba.Contrib.OMS.Patch import Patch
from Timba.Contrib.OMS import Bookmarks
from Timba.Contrib.OMS.FITSImageComponent import FITSImageComponent

# MS name
TDLRuntimeOption('msname',"MS",[
      "TEST.MS",
      "TEST-lim.MS",
      "TEST-grid.MS"]);

# ms_output = False  # if True, outputs to MS, else to BOIO dump   
TDLRuntimeOption('output_column',"Output MS column",
  [None,"DATA","MODEL_DATA","CORRECTED_DATA","MODEL_DATA_NJY"],default=1);

# number of timeslots to use at once
TDLRuntimeOption('tile_size',"Tile size",[30,48,60,96,480,960,2400]);

# number of stations
TDLCompileOption('num_stations',"Number of stations",[27,14,3]);

# number of timeslots to use at once
TDLRuntimeOption('imaging_mode',"Imaging mode",["mfs","channel"]);
  
# selection  applied to MS, None for full MS
#ms_selection = None
# or e.g.: 
ms_selection = record(channel_start_index=15,
                      channel_end_index=15);
#                      channel_increment=1,
#                      selection_string='')


# MS input queue size -- should be at least equal to the no. of ifrs
ms_queue_size = 500

# if False, BOIO dump will be generated instead of MS. Useful for benchmarking
ms_output = True;

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
  array = IfrArray(ns,stations); # ,mirror_uvw=True);
  observation = Observation(ns);
  
  # create nominal CLAR source model by calling the specified
  # function
#  img = FITSImageComponent(ns,'IMG',filename='sky-JohnCleeseBLKonGOLD.fits',
  img = FITSImageComponent(ns,'IMG',filename='sky-mpfoot-1024.fits',
        direction=observation.phase_centre);
  img.set_options(fft_pad_factor=2);
        
  source_list = [ img ];
  
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
                                   corr_index=[0,-1,-1,3],
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

def create_inputrec():
  boioname = "boio."+msname+".empty."+str(tile_size);
  # if boio dump for this tiling exists, use it to save time
  # but watch out if you change the visibility data set!
  if False: # not ms_selection and os.access(boioname,os.R_OK):
    rec = record(boio=record(boio_file_name=boioname,boio_file_mode="r"));
  # else use MS, but tell the event channel to record itself to boio file
  else:
    rec = record();
    rec.ms_name          = msname
    rec.data_column_name = 'DATA'
    rec.tile_size        = tile_size
    rec.selection        = ms_selection or record();
#      if not ms_selection:
#        rec.record_input     = boioname;
    rec = record(ms=rec);
  rec.python_init = 'Timba.Contrib.OMS.ReadVisHeader';
  rec.mt_queue_size = ms_queue_size;
  return rec;

def create_outputrec (outcol):
  rec = record();
  rec.mt_queue_size = ms_queue_size;
  if ms_selection or ms_output:
    rec.write_flags = False;
    rec.data_column = outcol;
    return record(ms=rec);
  else:
    rec.boio_file_name = "boio."+msname+".predict."+str(tile_size);
    rec.boio_file_mode = 'W';
    return record(boio=rec);



def _tdl_job_1_write_simulated_ms (mqs,parent,write=True):
  req = meq.request();
  req.input  = create_inputrec();
  if write and output_column:
    req.output = create_outputrec(output_column);
  print 'VisDataMux request is ', req
  mqs.clearcache('VisDataMux',recursive=False);
  mqs.execute('VisDataMux',req,wait=(parent is None));
  pass

def _tdl_job_2_make_dirty_image (mqs,parent,**kw):
  os.spawnvp(os.P_NOWAIT,'glish',['glish','-l','make_image.g',output_column,
      'ms='+msname,'mode='+imaging_mode]);



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
              
