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


### MS name
# msname = "TEST_CLAR_27-4800.MS";         # Oleg
msname = "TEST_CLAR_27-480.MS";          # Tony
### number of timeslots to use at once
tile_size = 30       

### MS input queue size -- must be at least equal to the no. of ifrs
ms_queue_size = 500

num_stations = 27

ms_selection = None
#or record(channel_start_index=0,
#          channel_end_index=0,
#          channel_increment=1,
#          selection_string='')

write_output = False  # if False, disables output completely       Oleg
ms_output = False    # if True, outputs to MS, else to BOIO dump  Oleg

# write_output = True  # if False, disables output completely        Tony
# ms_output = True     # if True, outputs to MS, else to BOIO dump   Tony


### MEP table for derived quantities 
mep_derived = 'CLAR_DQ_27-480.mep';

### MEP table for fitted parameters
### If set to a table name, results of solution will be stored and reused
### in future runs. This is usually not what we want for testing, so we can 
### set it to None to solve from scratch every time.
mep_sources = None;
# mep_sources = 'CLAR.mep';

### which source model to use
# source_model = clar_model.point_and_extended_sources;
source_model = clar_model.point_sources_only

### if True, previous solutions will be reused for successive time domains.
### This speeds up convergence (especially when solvables have no variation 
### in time), but makes the process less "educational".
reuse_solutions = False


# bookmarks
Settings.forest_state = record(bookmarks=[
  record(name='Predicted visibilities',page=Bookmarks.PlotPage(
      ["I:S1","I:S2","I:S3"],
      ["I:S4","I:S5","ihpbw"],
      ["visibility:all:1:2","spigot:1:2","residual:1:2"],
      ["visibility:all:1:9","spigot:1:9","residual:1:9"]
  )), 
  record(name='Source fluxes',page=Bookmarks.PlotPage(
      ["I:S1","I:S2","I:S3"],
      ["I:S4","I:S5","I:S6"],
      ["I:S7","I:S8","I:S9"],
      ["I:S10","ihpbw"]
  )) 
]);


def _define_forest(ns):
  # create array model
  stations = range(1,num_stations+1);
  array = IfrArray(ns,stations,uvw_table=mep_derived);
  observation = Observation(ns);
  
  # create CLAR source model
  # create nominal CLAR source model by calling the specified
  # function
  global source_list;
  source_list = source_model(ns);
  
  Ej = clar_model.EJones(ns,array,source_list);
  corrupt_list = [ 
    CorruptComponent(ns,src,label='E',station_jones=Ej(src.name))
    for src in source_list
  ];
                     
  # create all-sky patch for CLAR source model
  allsky = Patch(ns,'all');
  allsky.add(*corrupt_list);
  
  # For now, there are no G jones in the fitted model

  # create simulated visibilities for sky
  predict = allsky.visibilities(array,observation);
  
  # now create spigots, condeqs and residuals
  for sta1,sta2 in array.ifrs():
    spigot = ns.spigot(sta1,sta2) << Meq.Spigot( station_1_index=sta1-1,
                                                 station_2_index=sta2-1,
                                                 flag_bit=4,
                                                 input_col='DATA');
    pred = predict(sta1,sta2);
    ns.ce(sta1,sta2) << Meq.Condeq(spigot,pred);
    # residual is data-model, we're not applying any correction since we
    # don't have a G Jones in the model. 
    ns.residual(sta1,sta2) << spigot - pred;
    
  # set up a non-default condeq poll order for efficient parallelization 
  # (i.e. poll child 1:2, 3:4, 5:6, ..., 25:26, then the rest)
  cpo = [];
  for i in range(array.num_stations()/2):
    (sta1,sta2) = array.stations()[i*2:(i+1)*2];
    cpo.append(ns.ce(sta1,sta2).name);
  # create solver node
  ns.solver << Meq.Solver(children=[ns.ce(*ifr) for ifr in array.ifrs()],child_poll_order=cpo);
  
  # create sinks and reqseqs 
  for sta1,sta2 in array.ifrs():
    reqseq = Meq.ReqSeq(ns.solver,ns.residual(sta1,sta2),result_index=1);
    ns.sink(sta1,sta2) << Meq.Sink(station_1_index=sta1-1,
                                   station_2_index=sta2-1,
                                   flag_bit=4,
                                   corr_index=[0,1,2,3],
                                   flag_mask=-1,
                                   output_col='PREDICT',
                                   children=reqseq
                                   );
                                   
  # create visdatamux
  global _vdm;
  _vdm = ns.VisDataMux << Meq.VisDataMux;
  ns.VisDataMux.add_children(*[ns.sink(*ifr) for ifr in array.ifrs()]);
  ns.VisDataMux.add_stepchildren(*[ns.spigot(*ifr) for ifr in array.ifrs()]);
  
  
def create_solver_defaults(num_iter=30,epsilon=1e-4,convergence_quota=0.9,solvable=[]):
  solver_defaults=record()
  solver_defaults.num_iter     = num_iter
  solver_defaults.epsilon      = epsilon
  solver_defaults.convergence_quota = convergence_quota
  solver_defaults.save_funklets= True
  solver_defaults.last_update  = True
#See example in TDL/MeqClasses.py
  solver_defaults.solvable     = record(command_by_list=(record(name=solvable,
                                       state=record(solvable=True)),
                                       record(state=record(solvable=False))))
  return solver_defaults
  
def set_node_state (mqs,node,fields_record):
  """helper function to set the state of a node specified by name or
  nodeindex""";
  rec = record(state=fields_record);
  if isinstance(node,str):
    rec.name = node;
  elif isinstance(node,int):
    rec.nodeindex = node;
  else:
    raise TypeError,'illegal node argument';
  # pass command to kernel
  mqs.meq('Node.Set.State',rec);
  pass
  

def _perturb_solvables (mqs,solvables,rng=[0.2,0.3]):
  for name in solvables:
    polc = mqs.getnodestate(name).real_polc;
    polc.coeff[0,0] *= 1 + random.uniform(*rng)*random.choice([-1,1]);
    set_node_state(mqs,name,record(init_funklet=polc));
  return solvables;
    
def _reset_solvables (mqs,solvables,value=None):
  for name in solvables:
    polc = mqs.getnodestate(name).real_polc;
    if value is not None:
      polc.coeff[0,0] = value;
    set_node_state(mqs,name,record(init_funklet=polc));
  return solvables;


def create_inputrec ():
  boioname = "boio."+msname+".predict."+str(tile_size);
  # if boio dump for this tiling exists, use it to save time
  if not ms_selection and os.access(boioname,os.R_OK):
    rec = record(boio=record(boio_file_name=boioname,boio_file_mode="r"));
  # else use MS, but tell the event channel to record itself to boio file
  else:
    rec = record();
    rec.ms_name          = msname
    rec.data_column_name = 'DATA'
    rec.tile_size        = tile_size
    rec.selection = ms_selection or record();
    rec = record(ms=rec);
  rec.python_init='AGW_read_msvis_header.py';
  rec.mt_queue_size = ms_queue_size;
  return rec;


def create_outputrec (output_column='CORRECTED_DATA'):
  rec=record()
  rec.mt_queue_size = ms_queue_size;
  if ms_output:
    rec.write_flags=False
    rec.predict_column=output_column
    return record(ms=rec);
  else:
    rec.boio_file_name = "boio."+msname+".solve."+str(tile_size);
    rec.boio_file_mode = 'W';
    return record(boio=rec);


def _run_solve_job (mqs,solvables):
  """common helper method to run a solution with a bunch of solvables""";
  inputrec        = create_inputrec()
  outputrec       = create_outputrec()

  # set solvables list in solver
  solver_defaults = create_solver_defaults(solvable=solvables)
  set_node_state(mqs,'solver',solver_defaults)

  req = meq.request();
  req.input  = inputrec;
  # req.input.max_tiles = 1;  # this can be used to shorten the processing, for testing
  if write_output:
    req.output = outputrec;
  # mqs.clearcache('VisDataMux');
  mqs.execute('VisDataMux',req,wait=False);
  pass


def _tdl_job_1_solve_for_fluxes_and_beam_width (mqs,parent,**kw):
  solvables = _perturb_solvables(mqs,['I0:'+src.name for src in source_list]);
  solvables += _reset_solvables(mqs,[ 'spi:'+src.name for src in source_list],0);
  solvables += _reset_solvables(mqs,["ihpbw0"],400);
  _run_solve_job(mqs,solvables);
  

def _tdl_job_2_solve_for_fluxes_with_fixed_beam_width (mqs,parent,**kw):
  solvables = _perturb_solvables(mqs,['I0:'+src.name for src in source_list]);
  solvables += _reset_solvables(mqs,[ 'spi:'+src.name for src in source_list],0);
  _run_solve_job(mqs,solvables);
  
  
def _tdl_job_3_solve_for_beam_width_with_fixed_fluxes (mqs,parent,**kw):
  solvables = _reset_solvables(mqs,["ihpbw0"],400);
  _run_solve_job(mqs,solvables);
  

def _tdl_job_4_reset_parameters_to_true_values (mqs,parent,**kw):
  _reset_solvables(mqs,['I0:'+src.name for src in source_list]);
  _reset_solvables(mqs,[ 'spi:'+src.name for src in source_list]);
  _reset_solvables(mqs,["ihpbw0"]);



Settings.forest_state.cache_policy = 1  # -1 for minimal, 1 for smart caching, 100 for full caching
Settings.orphans_are_roots = True

if __name__ == '__main__':


    Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);


    ns.Resolve();
    pass
              
