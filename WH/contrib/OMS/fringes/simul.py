from Timba.TDL import *
from Timba.Meq import meq
from numarray import *
import os
import os.path

import models
from Timba.Contrib.OMS.IfrArray import IfrArray
from Timba.Contrib.OMS.Observation import Observation
from Timba.Contrib.OMS.Patch import Patch
from Timba.Contrib.OMS import Bookmarks

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

# number of timeslots to use at once
TDLRuntimeOption('imaging_mode',"Imaging mode",["mfs","channel"]);
  
# selection  applied to MS, None for full MS
ms_selection = None
# or e.g.: 
#ms_selection = record(channel_start_index=31,
#                      channel_end_index=31,
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
#  array = IfrArray(ns,stations,uvw_table=mep_derived,mirror_uvw=True);
  array = IfrArray(ns,stations,mirror_uvw=True);
  observation = Observation(ns);
  
  # create nominal CLAR source model by calling the specified
  # function
  source_list = source_model(ns);
  
  # create all-sky patch for source model
  allsky = Patch(ns,'all');
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
  rec.python_init = 'read_msvis_header.py';
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
              
