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
from Timba.Contrib.OMS.SkyComponent import create_polc 
from Timba.Contrib.OMS.PointSource import PointSource 
from Timba.Contrib.OMS.GaussianSource import GaussianSource 
from Timba.Contrib.OMS import Jones
from Timba.Contrib.OMS import Bookmarks


# MS name
TDLRuntimeOption('msname',"MS",[
      "TEST.MS",
      "TEST-lim.MS",
      "TEST-grid.MS"]);

TDLRuntimeOption('input_column',"Input MS column",["DATA","MODEL_DATA","CORRECTED_DATA"],default=0);
TDLRuntimeOption('output_column',"Output corrected data to MS column",[None,"DATA","MODEL_DATA","CORRECTED_DATA"],default=3);
TDLRuntimeOption('tile_size',"Tile size (timeslots)",[1,5,10,20,30,60]);

# how much to perturb starting values of solvables
TDLRuntimeMenu('Parameter options',
  TDLOption('flux_perturbation',"Perturb fluxes by (rel.)",["random",.1,.2,-.1,-.2]),
  TDLOption('pos_perturbation',"Perturb positions by (arcsec)",[.1,.25,1,2]),
  TDLOption('use_previous',"Reuse solution from previous time interval",False,
  doc="""If True, solutions for successive time domains will start with
the solution for a previous domain. Normally this speeds up convergence; you
may turn it off to re-test convergence at each domain."""),
  TDLOption('use_mep',"Reuse solutions from MEP table",False,
  doc="""If True, solutions from the MEP table (presumably, from a previous
run) will be used as starting points. Turn this off to solve from scratch.""")
);

# solver runtime options
TDLRuntimeMenu("Solver options",
  TDLOption('solver_debug_level',"Solver debug level",[0,1,10]),
  TDLOption('solver_lm_factor',"Initial solver LM factor",[1,.1,.01,.001]),
  TDLOption('solver_epsilon',"Solver convergence threshold",[.01,.001,.0001,1e-5,1e-6]),
  TDLOption('solver_num_iter',"Max number of solver iterations",[30,50,100,1000])
);

# source model
TDLCompileOption('source_model',"Source model",[
    models.cps,
    models.cps_plus_faint_extended,
    models.two_point_sources,
    models.two_bright_one_faint_point_source
  ],default=0);
  
# fitting options
TDLCompileMenu("Fitting options",
  TDLOption('fringe_deg_time',"Polc degree (time) for fringe fitting",[0,1,2,3,4]),
  TDLOption('fringe_deg_freq',"Polc degree (freq) for fringe fitting",[0,1,2,3,4]),
  TDLOption('flux_constraint',"Lower boundary for flux constraint",[None,0,.1,.5,.8,.99]),
  TDLOption('constraint_weight',"Weight of flux constraint",["intrinsic",100,1000,10000])
);

TDLCompileOption('output_type',"Output visiblities",["corrected","residual"]);

# number of stations
TDLCompileOption('num_stations',"Number of stations",[27,14,3]);


source_table = "sources.mep";
mep_table = "calib.mep";

def get_source_table ():
  return msname+"/"+source_table;

def get_mep_table ():
  return msname+"/"+mep_table;


# number of timeslots to use at once
TDLRuntimeOption('imaging_mode',"Imaging mode",["mfs","channel"]);
  
### MS input queue size -- must be at least equal to the no. of ifrs
ms_queue_size = 500

ms_selection = None
#or record(channel_start_index=0,
#          channel_end_index=0,
#          channel_increment=1,
#          selection_string='')

ms_output = True     # if True, outputs to MS, else to BOIO dump   Tony

# MEP table for various derived quantities 
mep_uvws = 'UVW-480.mep';

### MEP table for fitted parameters
### If set to a table name, results of solution will be stored and reused
### in future runs. This is usually not what we want for testing, so we can 
### set it to None to solve from scratch every time.
mep_sources = None;
# mep_sources = 'CLAR.mep';



# bookmarks
Settings.forest_state = record(bookmarks=[
  record(name='Predicted visibilities',page=Bookmarks.PlotPage(
      ["visibility:all:1:2","spigot:1:2","residual:1:2"],
      ["visibility:all:1:9","spigot:1:9","residual:1:9"],
      ["visibility:all:18:27","spigot:18:27","residual:18:27"],
      ["visibility:all:26:27","spigot:26:27","residual:26:27"]
  )), 
  record(name='Phase solutions',page=Bookmarks.PlotPage(
      ["phase:1","phase:2","phase:3"],
      ["phase:4","phase:5","phase:6"],
      ["phase:7","phase:8","phase:9"],
      ["phase:10","phase:11","solver"]
  )),
  record(name='Flux and phase solutions',page=Bookmarks.PlotPage(
      ["I:S1","I:S5","phase:1"],
      ["phase:2","phase:3","phase:4"],
      ["phase:5","phase:6","phase:7"],
      ["phase:8","phase:9","solver"]
  )),
  record(name='Flux solutions only',page=Bookmarks.PlotPage(
      ["I:S1"],
      ["I:S5"]
  )) 
]);




def phase_parm (tdeg,fdeg):
  """helper function to create a t/f parm for phase, including constraints.
  Placeholder until Maaijke implements periodic constraints.
  """;
  polc = meq.polc(zeros((tdeg+1,fdeg+1))*0.0,
            scale=array([3600.,8e+8,0,0,0,0,0,0]));
  shape = [tdeg+1,fdeg+1];
  # work out constraints on coefficients
  # maximum excursion in freq is pi/2
  # max excursion in time is pi/2
  dt = .2;
  df = .5;
  cmin = [];
  cmax = [];
  for it in range(tdeg+1):
    for jf in range(fdeg+1):
      mm = math.pi/(dt**it * df**jf );
      cmin.append(-mm);
      cmax.append(mm);
  cmin[0] = -1e+9;
  cmax[0] = 1e+9;
  return Meq.Parm(polc,shape=shape,real_polc=polc,node_groups='Parm',
                  constrain_min=cmin,constrain_max=cmax,
                  table_name=get_mep_table());


def _define_forest(ns):
  # create array model
  stations = range(1,num_stations+1);
  array = IfrArray(ns,stations,mirror_uvw=True);
  observation = Observation(ns);
  
  # create CLAR source model
  # create nominal CLAR source model by calling the specified
  # function
  global source_list;
  source_list = source_model(ns,get_source_table());
  
  # create all-sky patch for CLAR source model
  allsky = Patch(ns,'all');
  allsky.add(*source_list);
  
  # Add solvable G jones terms
  for station in array.stations():
    ns.phase(station) << phase_parm(fringe_deg_time,fringe_deg_freq);
    diag = ns.Gdiag(station) << Meq.Polar(1,ns.phase(station));
    ns.G(station) << Meq.Matrix22(diag,0,0,diag);
    
  # attach the G Jones series to the all-sky patch
  corrupt_sky = CorruptComponent(ns,allsky,label='G',station_jones=ns.G);

  # create simulated visibilities for the sky
  predict = corrupt_sky.visibilities(array,observation);
  
  # create a "clean" predict for the sky
  # clean_predict = allsky.visibilities(array,observation);
  
  # now create spigots, condeqs and residuals
  condeqs = [];
  for sta1,sta2 in array.ifrs():
    spigot = ns.spigot(sta1,sta2) << Meq.Spigot( station_1_index=sta1-1,
                                                 station_2_index=sta2-1,
                                                 flag_bit=4,
                                                 input_col='DATA');
    pred = predict(sta1,sta2);
    ce = ns.ce(sta1,sta2) << Meq.Condeq(spigot,pred);
    condeqs.append(ce);
    # subtract nodes compute residuals
    if output_type == "residual":
      ns.residual(sta1,sta2) << spigot - pred;
      
  # now create nodes to apply correction
  # in residual mode we apply it to the residual data only
  # in corrected mode, apply directly to spigot
  if output_type == "residual":
    Jones.apply_correction(ns.corrected,ns.residual,ns.G,array.ifrs());
  else:
    Jones.apply_correction(ns.corrected,ns.spigot,ns.G,array.ifrs());
    
  # set up a non-default condeq poll order for efficient parallelization 
  # (i.e. poll child 1:2, 3:4, 5:6, ..., 25:26, then the rest)
  cpo = [];
  for i in range(array.num_stations()/2):
    (sta1,sta2) = array.stations()[i*2:(i+1)*2];
    cpo.append(ns.ce(sta1,sta2).name);
  if constraint_weight != "intrinsic":
    ns.flux_constraint << flux_constraint;
    # create boundary constraints for fluxes
    for src in source_list:
      sti = src.stokes("I");
      base = ns.base_constr("I",src.name) << \
        (src.stokes("I") - ns.flux_constraint)*constraint_weight;
      bound = ns.constraint(src.name) << Meq.Condeq(
        Meq.Sqr(base) - Meq.Abs(base)*base,0
      );
      condeqs.append(bound);
    
  # create solver node
  ns.solver << Meq.Solver(children=condeqs,child_poll_order=cpo);
  
  # create sinks and reqseqs 
  for sta1,sta2 in array.ifrs():
    reqseq = Meq.ReqSeq(ns.solver,ns.corrected(sta1,sta2),
                  result_index=1,cache_num_active_parents=1);
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
  
  
def create_solver_defaults(num_iter=60,convergence_quota=0.9,solvable=[]):
  solver_defaults=record()
  solver_defaults.num_iter      = solver_num_iter
  solver_defaults.epsilon       = solver_epsilon
  solver_defaults.epsilon_deriv = solver_epsilon
  solver_defaults.lm_factor     = solver_lm_factor
  solver_defaults.convergence_quota = convergence_quota
  solver_defaults.balanced_equations = False
  solver_defaults.debug_level = solver_debug_level;
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
  

def create_inputrec ():
  boioname = "boio."+msname+".predict."+str(tile_size);
  # if boio dump for this tiling exists, use it to save time
  if not ms_selection and os.access(boioname,os.R_OK):
    rec = record(boio=record(boio_file_name=boioname,boio_file_mode="r"));
  # else use MS, but tell the event channel to record itself to boio file
  else:
    rec = record();
    rec.ms_name          = msname
    rec.data_column_name = input_column;
    rec.tile_size        = tile_size
    rec.selection = ms_selection or record();
    rec = record(ms=rec);
  rec.python_init='read_msvis_header.py';
  rec.mt_queue_size = ms_queue_size;
  return rec;


def create_outputrec (outcol):
  rec=record()
  rec.mt_queue_size = ms_queue_size;
  if ms_output:
    rec.write_flags=False
    rec.predict_column=outcol;
    return record(ms=rec);
  else:
    rec.boio_file_name = "boio."+msname+".solve."+str(tile_size);
    rec.boio_file_mode = 'W';
    return record(boio=rec);


def _run_solve_job (mqs,solvables):
  """common helper method to run a solution with a bunch of solvables""";
  req = meq.request();
  req.input  = create_inputrec();
  if output_column is not None:
    req.output = create_outputrec(output_column);

  # set solvables list in solver
  solver_defaults = create_solver_defaults(solvable=solvables)
  set_node_state(mqs,'solver',solver_defaults)

  # req.input.max_tiles = 1;  # this can be used to shorten the processing, for testing
  mqs.execute('VisDataMux',req,wait=False);
  pass

def _perturb_parameters (mqs,solvables,pert="random",
                        absolute=False,random_range=[0.2,0.3],constrain=None):
  global perturbation;
  for name in solvables:
    polc = mqs.getnodestate(name).real_polc;
    if absolute:  # absolute pert value given
      polc.coeff[0,0] += pert;
    elif pert == "random":  # else random pert
      polc.coeff[0,0] *= 1 + random.uniform(*random_range)*random.choice([-1,1]);
    else: # else perturb in relative terms
      polc.coeff[0,0] *= (1 + pert);
    parmstate = record(init_funklet=polc,
      use_previous=use_previous,reset_funklet=not use_mep);
    if constrain is not None:
      parmstate.constrain = constrain;
    set_node_state(mqs,name,parmstate);
  return solvables;
    
def _reset_parameters (mqs,solvables,value=None,use_table=False,reset=False):
  for name in solvables:
    polc = mqs.getnodestate(name).real_polc;
    if value is not None:
      polc.coeff[()] = value;
    reset_funklet = reset or not (use_table or use_mep);
    set_node_state(mqs,name,record(init_funklet=polc,
      use_previous=use_previous,reset_funklet=reset_funklet));
  return solvables;

arcsec_to_rad = math.pi/(180*3600);

def _tdl_job_1_solve_for_all_source_parameters (mqs,parent,**kw):
  solvables = [];
  for src in source_list:
    pert_ra = random.uniform(-pos_perturbation,pos_perturbation);
    solvables += _perturb_parameters(mqs,['ra:'+src.name],
                  pert=arcsec_to_rad*pert_ra,absolute=True);
    pert_dec = random.uniform(-pos_perturbation,pos_perturbation);
    solvables += _perturb_parameters(mqs,['dec:'+src.name],
                  pert=arcsec_to_rad*pert_dec,absolute=True);
    if src.has_spectral_index():
      solvables += _perturb_parameters(mqs,['I0:'+src.name],
                    pert=flux_perturbation,absolute=False);
      solvables += _reset_parameters(mqs,[src.spectral_index().name],0);
    else:
      solvables += _perturb_parameters(mqs,['I:'+src.name],
                    pert=flux_perturbation,absolute=False);
    if isinstance(src,GaussianSource):
      solvables += _perturb_parameters(mqs,['sigma1:'+src.name]);
      solvables += _perturb_parameters(mqs,['sigma2:'+src.name]);
      solvables += _reset_parameters(mqs,['phi:'+src.name],0);
  _run_solve_job(mqs,solvables);
  
def _tdl_job_2_solve_for_phases_and_fluxes (mqs,parent,**kw):
  if constraint_weight == "intrinsic":
    constrain = [flux_constraint,2.];
  else:
    constrain = None;
  solvables = _perturb_parameters(mqs,['I0:'+src.name for src in source_list],
               pert=flux_perturbation,absolute=False,
               constrain=constrain);
  solvables += _reset_parameters(mqs,['phase:'+str(sta) for sta in range(1,num_stations+1)],0);
  _run_solve_job(mqs,solvables);

def _tdl_job_2a_solve_for_phases_with_fixed_fluxes (mqs,parent,**kw):
  _reset_parameters(mqs,['I0:'+src.name for src in source_list],reset=True);
  solvables = _reset_parameters(mqs,['phase:'+str(sta) for sta in range(1,num_stations+1)],0);
  _run_solve_job(mqs,solvables);

def _tdl_job_2b_solve_for_phases_with_fixed_fluxes_14_27 (mqs,parent,**kw):
  _reset_parameters(mqs,['I0:'+src.name for src in source_list],reset=True);
  solvables = _reset_parameters(mqs,['phase:'+str(sta) for sta in range(15,num_stations+1)],0);
  _run_solve_job(mqs,solvables);

def _tdl_job_8_clear_out_all_previous_solutions (mqs,parent,**kw):
  os.system("rm -fr "+get_source_table());
  os.system("rm -fr "+get_mep_table());

def _tdl_job_9a_make_corrected_image (mqs,parent,**kw):
  os.spawnvp(os.P_NOWAIT,'glish',['glish','-l','make_image.g',output_column,
      'ms='+msname,'mode='+imaging_mode]);
  pass
  
def _tdl_job_9b_make_residual_image (mqs,parent,**kw):
  os.spawnvp(os.P_NOWAIT,'glish',['glish','-l','make_image.g','RESIDUAL',
      'ms='+msname,'mode='+imaging_mode]);
  pass


Settings.forest_state.cache_policy = 1  # -1 for minimal, 1 for smart caching, 100 for full caching
Settings.orphans_are_roots = True

if __name__ == '__main__':


    Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);


    ns.Resolve();
    pass
              
