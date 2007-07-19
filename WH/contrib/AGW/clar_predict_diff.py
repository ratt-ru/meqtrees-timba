
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
from Meow.IfrArray import IfrArray
from Meow.Observation import Observation
from Meow.Patch import Patch
from Meow.CorruptComponent import CorruptComponent
from Meow import Bookmarks

# MS name
# msname = "TEST_CLAR_27-4800.MS";      # Oleg ...
msname = "TEST_CLAR_27-480.MS";       # Tony ...

# number of timeslots to use at once
tile_size = 30
# MS input queue size -- should be at least equal to the no. of ifrs
ms_queue_size = 500
# number of stations
num_stations = 27
# selection  applied to MS, None for full MS
ms_selection = None
# or e.g.: 
#ms_selection = record(channel_start_index=31,
#                      channel_end_index=31,
#                      channel_increment=1,
#                      selection_string='')

# ms_output = False  # if True, outputs to MS, else to BOIO dump   
ms_output = True   # if True, outputs to MS, else to BOIO dump 

# MEP table for various derived quantities 
mep_derived = 'CLAR_DQ_27-480.mep';

# if true, a G Jones simulating phase and gain errors will be inserted
add_g_jones = False;
# add_g_jones = True;

# if true, an E Jones simulating beam effects will be inserted
add_e_jones = True;
# add_e_jones = False;

# which source model to use
# source_model = clar_model.point_and_extended_sources;
source_model = clar_model.point_sources_only

# bookmarks
Settings.forest_state = record(bookmarks=[
  record(name='Predicted residuals',page=Bookmarks.PlotPage(
      ["visibility:S1:E:1:2",
       "visibility:S1:E:1:6","visibility:S1:E:9:%d"%num_stations ],
      ["visibility:S1:E0:1:2",
       "visibility:S1:E0:1:6","visibility:S1:E0:9:%d"%num_stations ],
      ["residual:1:2",
       "residual:1:6","residual:9:%d"%num_stations ],
      ["E0:S1","E:S1:1","E:S1:%d"%num_stations,],
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
      ["I:S10","ihpbw"]
  )),
]);


def _define_forest(ns):
  # create array model
  stations = range(1,num_stations+1);
  array = IfrArray(ns,stations,uvw_table=mep_derived,mirror_uvw=True);
  observation = Observation(ns);
  
  # create nominal CLAR source model by calling the specified
  # function
  clar_model.init_directions(ns);
  source_list = source_model(ns);
  
  if add_e_jones:
    ## this uses the "true" CLAR beam with elevation broadening in
    ## effect, with a separate E per station
    Ej = clar_model.EJones(ns,array,source_list);
    corrupt_list = [ 
      CorruptComponent(ns,src,label='E',station_jones=Ej(src.name))
      for src in source_list
    ];
#     ## this uses a CLAR beam without elevation broadening
#     Ej0 = clar_model.EJones_unbroadened(ns,observation,source_list);
#     nom_list = [ 
#       CorruptComponent(ns,src,label='E0',jones=Ej0(src.direction.name))
#       for src in source_list
#     ];
    ## this uses a broadened beam, but a single "average" E for
    ## every station, rather than computing the per-station Es
    for src in source_list:
      ns.E0(src.name) << Meq.Add(*[ns.E(src.direction.name,st) for st in array.stations()])/array.num_stations();
    nom_list = [ 
      CorruptComponent(ns,src,label='E0',jones=ns.E0(src.direction.name))
      for src in source_list
    ];
  else:
    corrupt_list = nom_list = source_list;
    
  # create all-sky patch for CLAR source model
  allsky = Patch(ns,'all',observation.phase_centre);
  allsky.add(*corrupt_list);
  
  nomsky = Patch(ns,'all0',observation.phase_centre);
  nomsky.add(*nom_list);
  
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
  vis0 = allsky.visibilities(array,observation);
  vis1 = nomsky.visibilities(array,observation);
  
  # create the sinks and attach residuals to them, adding in a noise term
  for sta1,sta2 in array.ifrs():
    res = ns.residual(sta1,sta2) << vis0(sta1,sta2) - vis1(sta1,sta2);
    ns.sink(sta1,sta2) << Meq.Sink(station_1_index=sta1-1,
                                   station_2_index=sta2-1,
                                   flag_bit=4,
                                   corr_index=[0,1,2,3],
                                   flag_mask=-1,
                                   output_col='DATA',
                                   children=res
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
    if not ms_selection and os.access(boioname,os.R_OK):
      rec = record(boio=record(boio_file_name=boioname,boio_file_mode="r"));
    # else use MS, but tell the event channel to record itself to boio file
    else:
      rec = record();
      rec.ms_name          = msname
      rec.data_column_name = 'DATA'
      rec.tile_size        = tile_size
      rec.selection        = ms_selection or record();
      if not ms_selection:
        rec.record_input     = boioname;
      rec = record(ms=rec);
    rec.python_init = 'Timba.Contrib.OMS.ReadVisHeader';
    rec.mt_queue_size = ms_queue_size;
    return rec;

def create_outputrec(output_column='DATA'):
    rec=record();
    rec.mt_queue_size = ms_queue_size;
    if ms_selection or ms_output:
      rec.write_flags=False
      rec.data_column=output_column
      return record(ms=rec);
    else:
      rec.boio_file_name = "boio."+msname+".predict."+str(tile_size);
      rec.boio_file_mode = 'W';
      return record(boio=rec);



def _tdl_job_clar_predict(mqs,parent,write=True):
    inputrec        = create_inputrec()
    outputrec       = create_outputrec(output_column='DATA')
    req = meq.request();
    req.input  = inputrec;
    if write:
      req.output = outputrec;
    # mqs.clearcache('VisDataMux');
    print 'VisDataMux request is ', req
    mqs.execute('VisDataMux',req,wait=(parent is None));
    pass


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
              
