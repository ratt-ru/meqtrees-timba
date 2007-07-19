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

from numarray import *
import os
import random

from Timba.TDL import *
from Timba.Meq import meq
import Meow

from Meow.IfrArray import IfrArray
from Meow.Observation import Observation
from Meow.Parameterization import create_polc 
from Meow.Patch import Patch
from Meow.CorruptComponent import CorruptComponent 
from Meow.GaussianSource import GaussianSource 
from Meow import Jones,Bookmarks,Utils

import StandardModels

import fringe_fit_settings

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

TDLCompileOption('output_type',"Output visiblities",["corrected","residual"]);



# MS name and i/o column options
# excluse the standard tile size option, provide our own instead
Utils.include_ms_options(tile_sizes=None);
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

# solvable parameter options
parm_options = [
  TDLOption('override_phase_deg',"Override explicit polc degrees",False),
  TDLOption('phase_deg_time',"Polc degree (time) for phase fits",
    range(fringe_fit_settings.max_phase_deg_time+1)),
  TDLOption('phase_deg_freq',"Polc degree (freq) for phase fits",
    range(fringe_fit_settings.max_phase_deg_freq+1)),
  TDLOption('subtile_phase',"Subtiling for phase solutions",[None,10,20,30,60,90,120]),
  fringe_fit_settings.gain_fitting and TDLOption('gain_deg_time',"Polc degree (time) for gain fits",[0,1,2,3,4]),
  fringe_fit_settings.gain_fitting and TDLOption('gain_deg_freq',"Polc degree (freq) for gain fits",[0,1,2,3,4]),
  not fit_phases_only and TDLOption('flux_constraint',"Flux constraint",[None,[0.0,10.0],[1.,10.0],[2.,10.],[4.,10.]]),
  not fit_phases_only and TDLOption('fit_polarization',"Fit polarized source",False),
] + Utils.parameter_options();
TDLRuntimeMenu("Parameter options",*parm_options);

# solver runtime options
TDLRuntimeMenu("Solver options",*Utils.solver_options());

# imaging mode
TDLRuntimeOption('imaging_mode',"Imaging mode",["mfs","channel"]);
  
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
  for it in range(fringe_fit_settings.max_phase_deg_time+1):
    for jf in range(fringe_fit_settings.max_phase_deg_freq+1):
      mm = math.pi/(dt**it * df**jf );
      cmin.append(-mm);
      cmax.append(mm);
  cmin[0] = -1e+9;
  cmax[0] = 1e+9;
  return Meq.Parm(polc,shape=shape,real_polc=polc,node_groups='Parm',
                  constrain_min=cmin,constrain_max=cmax,
                  table_name=Utils.get_mep_table());


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
  source_list = source_model(ns,observation,Utils.get_source_table());
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
      pr = ns.phase('R',station) << phase_parm(0,0);
      pl = ns.phase('L',station) << phase_parm(0,0);
    # phase model: one common phase + parallactic angle
    else:
      ph0 = ns.phase(station) << phase_parm(0,0);
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
  
  

def _reset_parameters (mqs,solvables,value=None,use_table=False,
                       constrain=None,constrain_min=None,constrain_max=None,
                       reset=False,subtile=None,shape=None):
  for name in solvables:
    if isinstance(value,meq._polc_type):
      polc = value;
    elif value is not None:
      polc = mqs.getnodestate(name).real_polc;
      polc.coeff[()] = 0;
      polc.coeff[0,0] = value;
    print 'solvable',name,'polc is',polc;
    reset_funklet = reset or not (use_table or Utils.use_mep);
    parmstate = record(init_funklet=polc, \
                use_previous=Utils.use_previous,reset_funklet=reset_funklet);
    for var in ("constrain","constrain_min","constrain_max"):
      value = locals()[var];
      if value is not None:
        parmstate[var] = value;
    if subtile is None:
      parmstate.tiling = record();
    else:
      parmstate.tiling = record(time=subtile);
    if shape is not None:
      parmstate.shape = shape;
    Utils.set_node_state(mqs,name,parmstate);
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
  solvables = [];
  for sta in stations_list:
    subtiling = fringe_fit_settings.phase_subtiling.get(sta,None) or subtile_phase;
    value = fringe_fit_settings.fringe_guesses.get(sta,0);
    shape = fringe_fit_settings.phase_polc_degrees.get(sta,None);
    if shape is None or override_phase_deg:
      shape = (phase_deg_time+1,phase_deg_freq+1);
    print "Initial guess for phase ",sta,": ",value;
    if phase_model == "ind":
      solvables += _reset_parameters(mqs,["phase:%s:%s"%(pol,sta) for pol in ("R","L") ],
                                     value=value,subtile=subtiling,shape=shape);
    else:
      solvables += _reset_parameters(mqs,["phase:%s"%sta],value=value,subtile=subtiling,shape=shape);
      solvables += _reset_parameters(mqs,["phase:pa:%s"%sta],0);
  return solvables;

if not fit_phases_only:
  def _tdl_job_1_solve_for_flux_and_phases (mqs,parent,**kw):
    solvables = [];
    for src in source_list:
      solvables += _solvable_source(mqs,src);
    _reset_gains(mqs);  
    solvables += _solvable_phases(mqs);
    Utils.run_solve_job(mqs,solvables,tiling_phase);

def _tdl_job_1a_solve_for_phases_only (mqs,parent,**kw):
  solvables = [];
  _reset_gains(mqs);  
  solvables += _solvable_phases(mqs);
  Utils.run_solve_job(mqs,solvables,tiling_phase);

if not fit_phases_only:
  def _tdl_job_1b_solve_for_source_parameters (mqs,parent,**kw):
    solvables = [];
    for src in source_list:
      solvables += _solvable_source(mqs,src);
    _reset_gains(mqs);  
    Utils.run_solve_job(mqs,solvables,tiling_source);

  if fringe_fit_settings.gain_fitting:
    def _tdl_job_2_solve_for_flux_and_phases_and_gains (mqs,parent,**kw):
      solvables = [];
      for src in source_list:
        solvables += _solvable_source(mqs,src);
      solvables += _solvable_gains(mqs);
      solvables += _solvable_phases(mqs);
      Utils.run_solve_job(mqs,solvables,tiling_phase);

def _tdl_job_8a_clear_out_source_solutions (mqs,parent,**kw):
  os.system("rm -fr "+Utils.get_source_table());

def _tdl_job_8b_clear_out_instrumental_solutions (mqs,parent,**kw):
  os.system("rm -fr "+Utils.get_mep_table());

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
              
