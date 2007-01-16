from Timba.TDL import *
from Timba.Meq import meq
from numarray import *
import os
import random

import Meow

from Meow import Jones
from Meow import Bookmarks
from Meow import Utils
import Meow.CaliTrees

# number of stations
TDLCompileOption('num_stations',"Number of stations",[14,3],more=int);

import models343
# source model -- note how list is formed up on-the-fly from 
# contents of the models343 module
TDLCompileOption('source_model',"Source model",
  [ getattr(models343,func) for func in dir(models343) if callable(getattr(models343,func)) and func.startswith('m343_')],
 );
  
TDLCompileOption('g_tiling',"G phase solution subtiling",[None,1,2,5],more=int);
TDLCompileOption('include_E_jones',"Include E Jones (differential gains)",False);
TDLCompileOption('e_tiling',"E phase solution subtiling",[None,1,2,5],more=int);
  
 

def _define_forest(ns):
  # create array model
  stations = range(1,num_stations+1);
  array = Meow.IfrArray(ns,stations);
  observation = Meow.Observation(ns);
  # setup Meow global context
  Meow.Context.set(array=array,observation=observation);
  
  # create 343 source model
  source_list = source_model(ns,Utils.get_source_table());
  
  # create all-sky patch for source model
  allsky = Meow.Patch(ns,'all',observation.phase_centre);
  
  # definitions for ampl/phase parameters
  g_ampl_def = Meow.Parm(1,table_name=Utils.get_mep_table());
  g_phase_def = Meow.Parm(0,tiling=g_tiling,table_name=Utils.get_mep_table());

  # differential corrections present? 
  if include_E_jones:
    # first source is presumably at phase center, so only G itelf will aplly
    allsky.add(source_list[0]);
    # apply E to all other sources
    e_ampl_def = Meow.Parm(1,freq_deg=1,table_name=Utils.get_mep_table());
    e_phase_def = Meow.Parm(0,tiling=e_tiling,table_name=Utils.get_mep_table());
    for src in source_list[1:]:
      Ejones = Jones.gain_ap_matrix(ns.E(src.name),e_ampl_def,e_phase_def,
                                    tags="E",series=array.stations());
      src = Meow.CorruptComponent(ns,src,label='E',station_jones=Ejones);
      # add corrupted (or original) source to patch
      allsky.add(src);
  else:
    allsky.add(*source_list);
  # apply G to whole sky
  Gjones = Jones.gain_ap_matrix(ns.G,g_ampl_def,g_phase_def,
                                tags="G",series=array.stations());
  allsky = Meow.CorruptComponent(ns,allsky,label='G',station_jones=Gjones);

  # create simulated visibilities for the sky
  predict = allsky.visibilities();

  # create overall solve-correct tree
  global _vdm;
  _vdm = Meow.CaliTrees.make_solve_correct_tree(ns,predict,corrections=[Gjones]);
                                           
  # now extract lists of solvable parameters
  global solve_set;
  solve_set = {};
  solve_set['flux'] = predict.search(tags="flux solvable",return_names=True) + \
                      predict.search(tags="spectrum solvable",return_names=True);
  solve_set['e_ampl'] = predict.search(tags="E ampl",return_names=True);
  solve_set['e_phase'] = predict.search(tags="E phase",return_names=True);
  solve_set['g_ampl'] = predict.search(tags="G ampl",return_names=True);
  solve_set['g_phase'] = predict.search(tags="G phase",return_names=True);
  print solve_set;


# standard MS options from Meow
Utils.include_ms_options(
  tile_sizes=None,
  channels=[[15,40,1]]
);

TDLRuntimeMenu("Calibration options",
  TDLOption('tiling_flux',"Tile size when solving for source fluxes",[1,15,30,60,300,1500],more=int),
  TDLOption('tiling_g_phase',"Tile size when solving for phases",[1,15,30,60,300],more=int),
  TDLOption('tiling_g_ampl',"Tile size when solving for amplitudes",[1,15,30,60,300],more=int)
);

# standard parameter options from Meow
TDLRuntimeMenu("Parameter options",*Utils.parameter_options());
# solver runtime options from  Meow
TDLRuntimeMenu("Solver options",*Utils.solver_options());
# standard imaging options from Meow
TDLRuntimeMenu("Imager options",*Utils.imaging_options(npix=256,arcmin=5));


def _tdl_job_1_solve_for_source_fluxes (mqs,parent,**kw):
  # put together list of enabled solvables
  Utils.run_solve_job(mqs,solve_set['flux'],tiling=tiling_flux);

def _tdl_job_2_solve_for_G_phases (mqs,parent,**kw):
  # put together list of enabled solvables
  Utils.run_solve_job(mqs,solve_set['g_phase'],tiling=tiling_g_phase);

def _tdl_job_3_solve_for_G_amplitudes (mqs,parent,**kw):
  # put together list of enabled solvables
  Utils.run_solve_job(mqs,solve_set['g_ampl'],tiling=tiling_g_ampl);

if include_E_jones:
  def _tdl_job_4_solve_for_GE_phases (mqs,parent,**kw):
    # put together list of enabled solvables
    Utils.run_solve_job(mqs,solve_set['g_phase']+solve_set['e_phase'],
            tiling=tiling_g_phase);

  def _tdl_job_5_solve_for_GE_amplitudes (mqs,parent,**kw):
    # put together list of enabled solvables
    Utils.run_solve_job(mqs,solve_set['g_ampl']+solve_set['e_ampl'],
             tiling=tiling_g_ampl);
  
def _tdl_job_8_clear_out_all_previous_solutions (mqs,parent,**kw):
  try:    os.system("rm -fr "+Utils.get_source_table());
  except: pass;
  try:    os.system("rm -fr "+Utils.get_mep_table());
  except: pass;

def _tdl_job_9_make_dirty_image (mqs,parent,**kw):
  Utils.make_dirty_image();
  

Settings.forest_state = record(bookmarks=[
  record(name='Fluxes and coherencies',page=[
    record(viewer="Result Plotter",udi="/node/I:3C343",pos=(0,0)),
    record(viewer="Result Plotter",udi="/node/I:3C343.1",pos=(0,1)),
    record(viewer="Result Plotter",udi="/node/coherency:3C343",pos=(1,0)),
    record(viewer="Result Plotter",udi="/node/coherency:3C343.1",pos=(1,1)),
    record(viewer="Result Plotter",udi="/node/solver",pos=(2,1)),
  ]), \
  record(name='G solutions',page=[
    record(viewer="Result Plotter",udi="/node/G:1",pos=(0,0)),
    record(viewer="Result Plotter",udi="/node/G:2",pos=(0,1)),
    record(viewer="Result Plotter",udi="/node/G:10",pos=(1,0)),
    record(viewer="Result Plotter",udi="/node/solver",pos=(1,1)),
  ]),
  record(name='E solutions',page=[
    record(viewer="Result Plotter",udi="/node/E:3C343:1",pos=(0,0)),
    record(viewer="Result Plotter",udi="/node/E:3C343:2",pos=(0,1)),
    record(viewer="Result Plotter",udi="/node/E:3C343:10",pos=(0,1)),
    record(viewer="Result Plotter",udi="/node/solver",pos=(1,1)),
  ])
]);


Settings.forest_state.cache_policy = 1  # -1 for minimal, 1 for smart caching, 100 for full caching
Settings.orphans_are_roots = True

if __name__ == '__main__':


    Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);


    ns.Resolve();
    pass
              
