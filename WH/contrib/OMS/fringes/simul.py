from Timba.TDL import *
from Timba.Meq import meq
from numarray import *
import os
import random

import models
from Timba.Contrib.OMS.IfrArray import IfrArray
from Timba.Contrib.OMS.Observation import Observation
from Timba.Contrib.OMS.Patch import Patch
from Timba.Contrib.OMS.CorruptComponent import CorruptComponent
from Timba.Contrib.OMS import Bookmarks

# MS name
TDLRuntimeOption('msname',"MS",["TEST_CLAR_27-480.MS","TEST_CLAR_27-480-cps.MS"],inline=True);

# ms_output = False  # if True, outputs to MS, else to BOIO dump   
TDLRuntimeOption('output_column',"Output MS column",[None,"DATA","MODEL_DATA","CORRECTED_DATA"],default=1);

# number of timeslots to use at once
TDLRuntimeOption('tile_size',"Tile size",[30,48,60,96,480,960,2400]);

# number of stations
TDLCompileOption('num_stations',"Number of stations",[27,14,3]);

# if true, a G Jones simulating phase and gain errors will be inserted
TDLCompileOption('add_g_jones',"Simulate G Jones",False);

TDLCompileOption('phase_scale_time',"Max. phase variation in time (deg)",[30,60,90,180]);
TDLCompileOption('phase_scale_freq',"Max. phase variation in freq (deg)",[30,60,90,180]);
# phase noise
TDLCompileOption('phase_stddev',"Add phase noise (deg)",[None,0.5,1,2,5,10]);

# if not None, a per-ifr noise term with the given stddev will be added
TDLCompileOption('noise_stddev',"Add background noise (Jy)",[0,0.05,0.1,0.2,0.5]);

# which source model to use
TDLCompileOption('source_model',"Source model",[
    models.two_point_sources,
    models.two_point_sources_plus_faint_extended,
    models.cps,
    models.cps_plus_faint_extended
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


# MEP table for various derived quantities 
mep_uvws = 'UVW-480.mep';

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
      ["noisy_predict:1:2",
       "noisy_predict:1:6","noisy_predict:9:%d"%num_stations]
  )),
  record(name='Phases',page=Bookmarks.PlotPage(
      ["phase:1","phase:2","phase:3"],
      ["phase:4","phase:5","phase:6"],
      ["phase:7","phase:8","phase:9"],
      ["phase:10","phase:11","phase:12"]
  )),
  record(name='Source fluxes',page=Bookmarks.PlotPage(
      ["I:S1","I:S5"],
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
#  array = IfrArray(ns,stations,uvw_table=mep_derived,mirror_uvw=True);
  array = IfrArray(ns,stations,mirror_uvw=True);
  observation = Observation(ns);
  
  # create nominal CLAR source model by calling the specified
  # function
  source_list = source_model(ns);
  
  # create all-sky patch for source model
  allsky = Patch(ns,'all');
  allsky.add(*source_list);
  
  if add_g_jones:
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
    allsky = CorruptComponent(ns,allsky,label='G',station_jones=ns.G);

  # create simulated visibilities for sky
  visibilities = allsky.visibilities(array,observation);
  
  # create the sinks and attach predicts to them, adding in a noise term
  for sta1,sta2 in array.ifrs():
    if noise_stddev is not None:
      predict = ns.noisy_predict(sta1,sta2) << \
        visibilities(sta1,sta2) + (ns.noise(sta1,sta2) << noise_matrix(noise_stddev/2));
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



def _tdl_job_1_simulate_sky (mqs,parent,write=True):
  req = meq.request();
  req.input  = create_inputrec();
  if write and output_column:
    req.output = create_outputrec(output_column);
  print 'VisDataMux request is ', req
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
              
