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
  # enable standard MS options from Meow
  Utils.include_ms_options(
    tile_sizes=None,
    channels=[[15,40,1]]
  );

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
  _vdm = Meow.CaliTrees.define_solve_correct_tree(ns,predict,corrections=[Gjones]);
                                           
  # now define some runtime solve jobs
  Meow.CaliTrees.define_solve_job("Calibrate source fluxes","flux",
                                  predict.search(tags="(flux|spectrum) solvable"));
                                  
  GPs = predict.search(tags="G phase");
  Meow.CaliTrees.define_solve_job("Calibrate G phases","g_phase",GPs);
  GAs = predict.search(tags="G ampl");
  Meow.CaliTrees.define_solve_job("Calibrate G amplitudes","g_ampl",GAs);

  if include_E_jones:
    EPs = predict.search(tags="E phase");
    Meow.CaliTrees.define_solve_job("Calibrate GE phases","ge_phase",GPs+EPs);
    EAs = predict.search(tags="E ampl");
    Meow.CaliTrees.define_solve_job("Calibrate GE amplitudes","ge_ampl",GAs+EAs);

  # standard imaging options from Meow
  TDLRuntimeMenu("Make image",*Utils.imaging_options(npix=512,arcmin=72));

  # and finally a helper function to clear solutions
  def job_clear_out_all_previous_solutions (mqs,parent,**kw):
    from qt import QMessageBox
    if QMessageBox.warning(parent,"Clearing solutions","This will clear out <b>all</b> previously obtained calibrations. Are you sure?",
          QMessageBox.Yes,QMessageBox.No|QMessageBox.Default|QMessageBox.Escape) == QMessageBox.Yes:
      try:    os.system("rm -fr "+Utils.get_source_table());
      except: pass;
      try:    os.system("rm -fr "+Utils.get_mep_table());
      except: pass;
  TDLJob(job_clear_out_all_previous_solutions,"Clear out all solutions");



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
              
