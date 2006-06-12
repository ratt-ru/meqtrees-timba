from numarray import *
import os
import random

from Timba.TDL import *
from Timba.Meq import meq

from Timba.Contrib.OMS.IfrArray import IfrArray
from Timba.Contrib.OMS.Observation import Observation
from Timba.Contrib.OMS.Utils import create_polc 
from Timba.Contrib.OMS.Patch import Patch
from Timba.Contrib.OMS.CorruptComponent import CorruptComponent 
from Timba.Contrib.OMS.GaussianSource import GaussianSource 
from Timba.Contrib.OMS import Jones
from Timba.Contrib.OMS import Bookmarks

from Timba.Contrib.OMS.Calibration import StandardModels

from Timba.Contrib.OMS.Calibration import fringe_fit_settings

StandardModels.ref_frequency = fringe_fit_settings.source_ref_frequency;

#
#============ CONSTRUCT STANDARD MENUS
#


# compile-time options
#
full_station_list = range(1,fringe_fit_settings.num_stations+1);

# this creates variables enable_sta_1, _2, _3, etc. and associates them with options
TDLCompileMenu("Enable/disable stations",
  *[ TDLOption('enable_sta_'+str(sta),str(sta),True) for sta in full_station_list ] );
TDLCompileOption('fit_phases_only',"Build trees for phase fit only",False);
TDLCompileOption('fit_sta1_only',"Fit station 1 baselines only, no closures",False);
TDLCompileOption('source_model',"Source model",[
    StandardModels.cps,
    StandardModels.cgs
  ] + fringe_fit_settings.extra_source_models,default=0);
TDLCompileOption('phase_model',"Feed phase model",{"ind":"independent","pa":"with p/a"});
TDLCompileMenu("Fitting options",
  TDLOption('fringe_deg_time',"Polc degree (time) for phase fits",
    range(fringe_fit_settings.max_phase_deg_time+1)),
  TDLOption('fringe_deg_freq',"Polc degree (freq) for phase fits",
    range(fringe_fit_settings.max_phase_deg_freq+1)),
  TDLOption('subtile_phase',"Subtiling for phase solutions",[None,10,20,30,60,90,120]),
  fringe_fit_settings.gain_fitting and TDLOption('gain_deg_time',"Polc degree (time) for gain fits",[0,1,2,3,4]),
  fringe_fit_settings.gain_fitting and TDLOption('gain_deg_freq',"Polc degree (freq) for gain fits",[0,1,2,3,4]),
  TDLOption('flux_constraint',"Flux constraint",[None,[0.0,10.0],[1.,10.0],[2.,10.],[4.,10.]]),
);

TDLCompileOption('output_type',"Output visiblities",["corrected","residual"]);



# MS name
# get all MS in current dir
ms_list = filter(lambda name:name.endswith('.ms') or name.endswith('.MS'),os.listdir('.'));
TDLRuntimeOption('msname',"MS",ms_list);

TDLRuntimeOption('input_column',"Input MS column",["DATA","MODEL_DATA","CORRECTED_DATA"],default=0);
TDLRuntimeOption('output_column',"Output corrected data to MS column",[None,"DATA","MODEL_DATA","CORRECTED_DATA"],default=3);
TDLRuntimeOption('tiling_phase',"Tiling for local solutions (e.g. phase)",
                  fringe_fit_settings.local_solution_tilings);
TDLRuntimeOption('tiling_source',"Tiling for global solutions",
                  fringe_fit_settings.global_solution_tilings);

selection_string = '';

TDLRuntimeMenu('Data selection options',
  TDLOption('field_index',"Field ID",fringe_fit_settings.field_list),
  TDLOption('ddid_index',"Data description ID (band)",fringe_fit_settings.ddid_list),
  TDLOption('channel_select',"Channel selection",[None]+fringe_fit_settings.channel_selections),
  TDLOption('max_input_tiles',"Restrict number of input tiles",[None,1,2,3,5]),
  fringe_fit_settings.data_selection_strings and 
    TDLOption('selection_string',"Additional selection",[None]+fringe_fit_settings.data_selection_strings),
);
# how much to perturb starting values of solvables
TDLRuntimeMenu('Fitting options',
  not fit_phases_only and TDLOption('fit_polarization',"Fit polarized source",False),
  not fit_phases_only and TDLOption('flux_perturbation',"Perturb fluxes by (rel.)",["random",.1,.2,-.1,-.2]),
  TDLOption('use_previous',"Reuse solution from previous time interval",False,
      doc="""If True, solutions for successive time domains will start with
the solution for a previous domain. Normally this speeds up convergence; you
may turn it off to re-test convergence at each domain."""),
  TDLOption('use_mep',"Reuse solutions from MEP table",False,
      doc="""If True, solutions from the MEP table (presumably, from a previous
run) will be used as starting points. Turn this off to solve from scratch."""),
  TDLOption('solver_debug_level',"Solver debug level",[0,1,10]),
  TDLOption('solver_lm_factor',"Initial solver LM factor",[1,.1,.01,.001]),
  TDLOption('solver_epsilon',"Solver convergence threshold",[.01,.001,.0001,1e-5,1e-6]),
  TDLOption('solver_num_iter',"Max number of solver iterations",[30,50,100,1000]),
  TDLOption('solver_balanced_equations',"Assume equations are balanced",False),
  TDLOption('solver_save_funklets',"Save parms even if not converged",False)
);
TDLRuntimeOption('imaging_mode',"Imaging mode",["mfs","channel"]);
  
source_table = "sources.mep";
mep_table = "calib.mep";

def get_source_table ():
  return msname+"/"+source_table;

def get_mep_table ():
  return msname+"/"+mep_table;


### MS input queue size -- must be at least equal to the no. of ifrs
ms_queue_size = 500

ms_output = True     # if True, outputs to MS, else to BOIO dump   Tony




def gain_parm (tdeg,fdeg):
  """helper function to create a t/f parm for gain.
  """;
  polc = meq.polc(zeros((tdeg+1,fdeg+1))*0.0);
  polc.coeff[0,0] = 1;
  return Meq.Parm(polc,shape=shape,real_polc=polc,node_groups='Parm',
                  table_name=get_mep_table());


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
  # compose list of "enabled" stations
  global stations_list;
  stations_list = [ sta for sta in full_station_list 
        if globals()['enable_sta_'+str(sta)] ];
  # create array model
  array = IfrArray(ns,stations_list);
  observation = Observation(ns,circular=True);
  
  # create source model
  global source_list;
  source_list = source_model(ns,observation,get_source_table());
  # create all-sky patch for source model
  allsky = Patch(ns,'all',observation.phase_centre);
  allsky.add(*source_list);
  
  # Add solvable G jones terms
  for station in array.stations():
    if fringe_fit_settings.gain_fitting:
      gr = ns.gain('R',station) << gain_parm(gain_deg_time,gain_deg_freq);
      gl = ns.gain('L',station) << gain_parm(gain_deg_time,gain_deg_freq);
    else:
      gr = ns.gain('R',station) << 1.0;
      gl = ns.gain('L',station) << 1.0;
    # phase model: independent feed phases
    if phase_model == "ind":
      pr = ns.phase('R',station) << phase_parm(fringe_deg_time,fringe_deg_freq);
      pl = ns.phase('L',station) << phase_parm(fringe_deg_time,fringe_deg_freq);
    # phase model: one common phase + parallactic angle
    else:
      ph0 = ns.phase(station) << phase_parm(fringe_deg_time,fringe_deg_freq);
      pa = ns.phase('pa',station) << phase_parm(0,0);  # parallactic angle
      pr = ns.phase('R',station) << Meq.Identity(ph0);
      pl = ns.phase('L',station) << ph0 + pa;
    ns.G(station) << Meq.Matrix22(Meq.Polar(gr,pr),0,0,Meq.Polar(gl,pl));
    
  # attach the G Jones series to the all-sky patch
  corrupt_sky = CorruptComponent(ns,allsky,label='G',station_jones=ns.G);

  # create simulated visibilities for the sky
  predict = corrupt_sky.visibilities(array,observation);
  
  # create a "clean" predict for the sky
  # clean_predict = allsky.visibilities(array,observation);
  
  # these are used to select the appropriate coherency from a Spigot's
  # 2x2 output
  cohs = ( 'RR','LL' );
  coh_index = { 'RR':(0,0),'LL':(1,1) };
  condeqs = [];
  # create spigots
  for sta1,sta2 in array.ifrs():
    spigot = ns.spigot(sta1,sta2) << Meq.Spigot( station_1_index=sta1-1,
                                                 station_2_index=sta2-1,
                                                 flag_bit=4,
                                                 input_col='DATA');
    weight = ns.weight(sta1,sta2) << Meq.Spigot( station_1_index=sta1-1,
                                               station_2_index=sta2-1,
                                               flag_mask=0,
                                               input_col='WEIGHT');
    pred = predict(sta1,sta2);
    # create rr/ll spigots -- we need them for direct phase fitting, and also
    # for visualizing baseline phases. Also create nodes for observed 
    # and fitted baseline phases.
    spig = {}; obs = {}; fit = {};
    for coh in cohs:
      spig[coh] = ns.spigot(coh,sta1,sta2) << Meq.Selector(spigot,index=coh_index[coh]);
      obs[coh] = ns.obs_phase(coh,sta1,sta2) << Meq.Arg(spig[coh]);
      fit[coh] = ns.phase(coh,sta1,sta2) << ns.phase(coh[0],sta1)-ns.phase(coh[1],sta2);
    # create condeqs
    if sta1 == 1 or not fit_sta1_only:
      # create condeqs for direct phase fits, weighted by |vis|^2
      if fit_phases_only:
        for coh in cohs:
          amp2 = ns.amp2(coh,sta1,sta2) << Meq.Sqr(Meq.Abs(spig[coh]));
          condeqs.append(ns.ce(coh,sta1,sta2) << \
            Meq.Condeq(fit[coh],obs[coh],ns.weight(sta1,sta2)*amp2,modulo=2*math.pi));
      # else create condeqs for direct fitting of visibilities
      else:
        condeqs.append(ns.ce(sta1,sta2) << Meq.Condeq(spigot,pred,weight));
    # create subtract nodes to compute residuals
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
  # for i in range(array.num_stations()/2):
  #   (sta1,sta2) = array.stations()[i*2:(i+1)*2];
  #   cpo.append(ns.ce(sta1,sta2).name);
      
  # create summary visualizations
  phases = [];
#  ffts = [];
  for sta1,sta2 in array.ifrs():
    for pol in ('RR','LL'):
#       ffts.append( ns.fft(pol,sta1,sta2) << \
#             Meq.FFTBrick(ns.spigot(pol,sta1,sta2),
#                     axes_in=(hiid('time'),hiid('freq')),
#                     axes_out=(hiid('time'),hiid('freq'))) );
      phases += [
        ns.phase('time',pol,sta1,sta2) << \
            Meq.Mean(ns.phase(pol,sta1,sta2),reduction_axes='freq'),
        ns.obs_phase('time',pol,sta1,sta2) << \
            Meq.Mean(ns.obs_phase(pol,sta1,sta2),reduction_axes='freq')
      ];
  gains = []
  for sta in array.stations():
    for pol in ('R','L'):
      gains.append(ns.gain(pol,sta));
  closures = [];
  sta1,sta2,sta3 = array.stations()[0:3];
  for pol in ('RR','LL'):
    closures.append(ns.closure(pol,sta1,sta2,sta3) << \
        ns.spigot(pol,sta1,sta2) + ns.spigot(pol,sta2,sta3) - ns.spigot(pol,sta1,sta3));
  ns.summary << Meq.ReqMux(
    ns.summary_phases << Meq.ReqMux(*phases),
    ns.summary_gains  << Meq.ReqMux(*gains),
    ns.summary_closures << Meq.ReqMux(*closures),
#    ns.summary_ffts << Meq.ReqMux(*ffts)
  );
    
  # create solver node
  ns.solver << Meq.Solver(children=condeqs);
  
  # create sinks and reqseqs 
  for sta1,sta2 in array.ifrs():
    reqseq = Meq.ReqSeq(ns.solver,ns.summary,ns.corrected(sta1,sta2),
                  result_index=2,cache_num_active_parents=1);
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
  ns.VisDataMux.add_stepchildren(*[ns.weight(*ifr) for ifr in array.ifrs()]);
  
  
def create_solver_defaults(num_iter=60,convergence_quota=0.9,solvable=[]):
  solver_defaults=record()
  solver_defaults.num_iter      = solver_num_iter;
  solver_defaults.epsilon       = solver_epsilon;
  solver_defaults.epsilon_deriv = solver_epsilon;
  solver_defaults.lm_factor     = solver_lm_factor;
  solver_defaults.convergence_quota = convergence_quota;
  solver_defaults.balanced_equations = solver_balanced_equations;
  solver_defaults.debug_level   = solver_debug_level;
  solver_defaults.save_funklets = solver_save_funklets;
  solver_defaults.last_update   = True;
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
  

def create_inputrec (tiling=(1,None)):
  rec = record();
  rec.ms_name          = msname
  rec.data_column_name = input_column;
  (tile_segments,tile_size) = tiling;
  if tile_segments is not None:
    rec.tile_segments    = tile_segments;
  if tile_size is not None:
    rec.tile_size        = tile_size;
  rec.selection =  record();
  rec.selection.ddid_index       = ddid_index;
  rec.selection.field_index      = field_index;
  rec.selection.selection_string = selection_string or '';
  if channel_select is not None:
    rec.selection.channel_start_index = channel_select[0];
    rec.selection.channel_end_index = channel_select[1];
  rec = record(ms=rec);
  if max_input_tiles is not None:
    rec.max_tiles = max_input_tiles;
  rec.python_init='Timba.Contrib.OMS.ReadVisHeader';
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


def _run_solve_job (mqs,solvables,tiling):
  """common helper method to run a solution with a bunch of solvables""";
  req = meq.request();
  req.input  = create_inputrec(tiling);
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
    print name,parmstate;
    set_node_state(mqs,name,parmstate);
  return solvables;
    
def _reset_parameters (mqs,solvables,value=None,use_table=False,
                       constrain=None,constrain_min=None,constrain_max=None,reset=False,subtile=None):
  for name in solvables:
    polc = mqs.getnodestate(name).real_polc;
    if value is not None:
      polc.coeff[()] = 0;
      polc.coeff[0,0] = value;
    reset_funklet = reset or not (use_table or use_mep);
    parmstate = record(init_funklet=polc, \
                use_previous=use_previous,reset_funklet=reset_funklet);
    for var in ("constrain","constrain_min","constrain_max"):
      value = locals()[var];
      if value is not None:
        parmstate[var] = value;
    if subtile is None:
      parmstate.tiling = record();
    else:
      parmstate.tiling = record(time=subtile);
    set_node_state(mqs,name,parmstate);
  return solvables;

arcsec_to_rad = math.pi/(180*3600);

def _solvable_source (mqs,src):
  constrain = flux_constraint;
  # note that "constrain" overrides "constrain_min/max", so only use the latter
  if constrain is not None:
    cmin = [constrain[0],-10.,-10.,-10.,-10.];
    cmax = [constrain[1],10.,10.,10.,10.];
  else:
    cmin = cmax = None;
  solvables = _reset_parameters(mqs,['I0:'+src.name],
      constrain_min=cmin,constrain_max=cmax);
  spol =  _reset_parameters(mqs,['Q:'+src.name for src in source_list],constrain=[0.,.5]);
  spol += _reset_parameters(mqs,['U:'+src.name for src in source_list],constrain=[0.,.5]);
  spol += _reset_parameters(mqs,['V:'+src.name for src in source_list],constrain=[0.,.5]);
  if fit_polarization:
    solvables += spol;
  if isinstance(src,GaussianSource):
    solvables += _reset_parameters(mqs,['sigma1:'+src.name]);
    solvables += _reset_parameters(mqs,['sigma2:'+src.name]);
    solvables += _reset_parameters(mqs,['phi:'+src.name]);
  return solvables;
    
def _reset_gains (mqs):
  if fringe_fit_settings.gain_fitting:
    _reset_parameters(mqs,['gain:L:'+str(sta) for sta in stations_list],1);
    _reset_parameters(mqs,['gain:R:'+str(sta) for sta in stations_list],1);

def _solvable_gains (mqs):
  if fringe_fit_settings.gain_fitting:
    # gain of station 1 is fixed
    _reset_parameters(mqs,['gain:L:'+str(stations_list[0])],1);
    _reset_parameters(mqs,['gain:R:'+str(stations_list[0])],1);
    # other gains solvable
    solvables = _reset_parameters(mqs,['gain:L:'+str(sta) for sta in stations_list[1:]],1);
    solvables += _reset_parameters(mqs,['gain:R:'+str(sta) for sta in stations_list[1:]],1);
    return solvables;

def _solvable_phases (mqs):
  if phase_model == "ind":
    parms = ('phase:R:','phase:L:');
  else:
    parms = ('phase:','phase:pa:');
  solvables = [];
  for p in parms:
    solvables += _reset_parameters(mqs,[p+str(sta) for sta in stations_list],
                                  0,subtile=subtile_phase);
  return solvables;

if not fit_phases_only:
  def _tdl_job_1_solve_for_flux_and_phases (mqs,parent,**kw):
    solvables = [];
    for src in source_list:
      solvables += _solvable_source(mqs,src);
    _reset_gains(mqs);  
    solvables += _solvable_phases(mqs);
    _run_solve_job(mqs,solvables,tiling_phase);

def _tdl_job_1a_solve_for_phases_only (mqs,parent,**kw):
  solvables = [];
  _reset_gains(mqs);  
  solvables += _solvable_phases(mqs);
  _run_solve_job(mqs,solvables,tiling_phase);

if not fit_phases_only:
  def _tdl_job_1b_solve_for_source_parameters (mqs,parent,**kw):
    solvables = [];
    for src in source_list:
      solvables += _solvable_source(mqs,src);
    _reset_gains(mqs);  
    _run_solve_job(mqs,solvables,tiling_source);

  if fringe_fit_settings.gain_fitting:
    def _tdl_job_2_solve_for_flux_and_phases_and_gains (mqs,parent,**kw):
      solvables = [];
      for src in source_list:
        solvables += _solvable_source(mqs,src);
      solvables += _solvable_gains(mqs);
      solvables += _solvable_phases(mqs);
      _run_solve_job(mqs,solvables);

def _tdl_job_8a_clear_out_source_solutions (mqs,parent,**kw):
  os.system("rm -fr "+get_source_table());

def _tdl_job_8b_clear_out_instrumental_solutions (mqs,parent,**kw):
  os.system("rm -fr "+get_mep_table());

def _tdl_job_9a_make_corrected_image (mqs,parent,**kw):
  os.spawnvp(os.P_NOWAIT,'glish',['glish','-l','make_image.g',output_column,
      'ms='+msname,             
      'mode='+imaging_mode,     
      'field='+str(field_index), 
      'ddid='+str(ddid_index) 
  ]);
  pass
  
def _tdl_job_9b_make_residual_image (mqs,parent,**kw):
  os.spawnvp(os.P_NOWAIT,'glish',['glish','-l','make_image.g','RESIDUAL',   \
      'ms='+msname,             
      'mode='+imaging_mode,     
      'field='+str(field_index), 
      'ddid='+str(ddid_index) 
  ]);
  pass


# export external symbols
globs = list(globals().keys());
tdljobs = [ name for name in globs if name.startswith('_tdl_job') ]

__all__ = [ '_define_forest' ] + tdljobs;

if __name__ == '__main__':


    Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);


    ns.Resolve();
    pass
              
