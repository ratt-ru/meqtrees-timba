from Timba.TDL import *
from Timba.Meq import meq
from numarray import *
import os
import random

import clar_model 
from Timba.Contrib.OMS.IfrArray import IfrArray
from Timba.Contrib.OMS.Observation import Observation
from Timba.Contrib.OMS.Patch import Patch
from Timba.Contrib.OMS.CorruptComponent import CorruptComponent
from Timba.Contrib.OMS import Bookmarks

# MS name
TDLRuntimeOption('msname',"MS",["TEST_CLAR_27-480.MS","TEST_CLAR_27-4800.MS"],inline=True);

# ms_output = False  # if True, outputs to MS, else to BOIO dump   
TDLRuntimeOption('output_column',"Output MS column",[None,"DATA","MODEL_DATA","CORRECTED_DATA"],default=1);

# number of timeslots to use at once
TDLRuntimeOption('tile_size',"Tile size",[5,30,48,60,96,480,960,2400]);

# number of stations
TDLCompileOption('num_stations',"Number of stations",[27,14,3]);

# if true, a G Jones simulating phase and gain errors will be inserted
TDLCompileOption('add_g_jones',"Simulate G Jones",False);

# if true, an E Jones simulating beam effects will be inserted
TDLCompileOption('add_e_jones',"Simulate E Jones",True);

# if not None, a per-ifr noise term with the given stddev will be added
TDLCompileOption('noise_stddev',"Noise level",[None,0.05,0.1,1.0]);

# which source model to use
# source_model = clar_model.point_and_extended_sources;
TDLCompileOption('source_model',"Source model",[
    clar_model.point_and_extended_sources,
    clar_model.point_sources_only,
    clar_model.radio_galaxy,
    clar_model.faint_source
  ],default=0);
  
# selection  applied to MS, None for full MS
ms_selection = None
# or e.g.: 
#ms_selection = record(channel_start_index=31,
#                      channel_end_index=31,
#                      channel_increment=1,
#                      selection_string='')


# MEP table for various derived quantities 
mep_derived = 'CLAR_DQ_27-480.mep';

# MS input queue size -- should be at least equal to the no. of ifrs
ms_queue_size = 500

# if False, BOIO dump will be generated instead of MS. Useful for benchmarking
ms_output = True;

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
      ["I:S10","ihpbw"]
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
  
  # create nominal CLAR source model by calling the specified
  # function
  source_list = source_model(ns);
  
  if add_e_jones:
    Ej = clar_model.EJones(ns,array,source_list);
    corrupt_list = [ 
      CorruptComponent(ns,src,label='E',station_jones=Ej(src.name))
      for src in source_list
    ];
  else:
    corrupt_list = source_list;
                     
  # create all-sky patch for CLAR source model
  allsky = Patch(ns,'all');
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
  rec.python_init = 'AGW_read_msvis_header.py';
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



def _tdl_job_clar_predict(mqs,parent,write=True):
  req = meq.request();
  req.input  = create_inputrec();
  if write and output_column:
    req.output = create_outputrec(output_column);
  print 'VisDataMux request is ', req
  mqs.execute('VisDataMux',req,wait=(parent is None));
  pass

def _tdl_job_make_dirty_image (mqs,parent,**kw):
  os.spawnvp(os.P_NOWAIT,'glish',['glish','-l','make_image.g']);
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
              
