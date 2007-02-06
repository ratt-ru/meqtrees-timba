from Timba.TDL import *
from Timba.Meq import meq
from numarray import *
import os
import random

import Meow

from Meow import Jones
from Meow import Bookmarks
from Meow import Utils
import Meow.StdTrees

# number of stations
TDLCompileOption('num_stations',"Number of stations",[14,3],more=int);

import models343
# source model -- note how list is formed up on-the-fly from 
# contents of the models343 module
TDLCompileOption('source_model',"Source model",
  [ getattr(models343,func) for func in dir(models343) if callable(getattr(models343,func)) and func.startswith('m343_')],
 );
TDLCompileOption('make_residuals',"Subtract model sources in output",True);
  
TDLCompileMenu("G Jones",
  TDLOption('gp_tiling',"G phase solution subtiling",[None,1,2,5],more=int),
  TDLOption('gp_freq_deg',"G phase freq degree",[0,1,2],more=int),
  TDLOption('ga_freq_deg',"G ampl freq degree",[0,1,2],more=int)
);
TDLCompileMenu("E Jones",
  TDLOption('include_E_jones',"Include E Jones (differential gains)",False),
  TDLOption('ep_tiling',"E phase solution subtiling",[None,1,2,5],more=int),
  TDLOption('ep_freq_deg',"E phase freq degree",[0,1,2],more=int),
  TDLOption('ea_freq_deg',"E ampl freq degree",[0,1,2],more=int)
);
  
 

def _define_forest(ns):
  # enable standard MS options from Meow
  Utils.include_ms_options(
    tile_sizes=None,
    channels=[[15,40,1],[15,40,2]]
  );

  # create array model
  array = Meow.IfrArray.WSRT(ns,num_stations);
  observation = Meow.Observation(ns);
  # setup Meow global context
  Meow.Context.set(array=array,observation=observation);
  
  # create 343 source model
  source_list = source_model(ns,Utils.get_source_table());
  
  # create all-sky patch for source model
  allsky = Meow.Patch(ns,'all',observation.phase_centre);
  
  # definitions for ampl/phase parameters
  g_ampl_def = Meow.Parm(1,freq_deg=ga_freq_deg,table_name=Utils.get_mep_table());
  g_phase_def = Meow.Parm(0,freq_deg=gp_freq_deg,tiling=gp_tiling,table_name=Utils.get_mep_table());

  # differential corrections present? 
  if include_E_jones:
    # first source is presumably at phase center, so only G itelf will aplly
    allsky.add(source_list[0]);
    # apply E to all other sources
    e_ampl_def = Meow.Parm(1,freq_deg=ea_freq_deg,table_name=Utils.get_mep_table());
    e_phase_def = Meow.Parm(0,freq_deg=ep_freq_deg,tiling=ep_tiling,table_name=Utils.get_mep_table());
    for src in source_list[1:]:
      Ejones = Jones.gain_ap_matrix(ns.E(src.name),e_ampl_def,e_phase_def,
                                    tags="E",series=array.stations());
      # add corrupted source to patch
      allsky.add(src.corrupt(Ejones));
  else:
    allsky.add(*source_list);
  # apply G to whole sky
  Gjones = Jones.gain_ap_matrix(ns.G,g_ampl_def,g_phase_def,
                                tags="G",series=array.stations());
  allsky = allsky.corrupt(Gjones);

  # create simulated visibilities for the sky
  predict = allsky.visibilities();

  # create solve tree.
  solve_tree = Meow.StdTrees.SolveTree(ns,predict,residuals=make_residuals);
  solve_output = solve_tree.outputs(array.spigots());
  
  # output of solve tree is either input data, or residuals.
  # apply correction for G
  corrected = Jones.apply_correction(ns.corrected,solve_output,Gjones);

  # create some visualizers
  visualizers = [
    Meow.StdTrees.vis_inspector(ns.inspect('spigots'),array.spigots(),bookmark=False),
    Meow.StdTrees.vis_inspector(ns.inspect('residuals'),corrected,bookmark=False),
    Meow.StdTrees.jones_inspector(ns.inspect('G'),Gjones)
  ];
  if include_E_jones:
    visualizers.append( Meow.StdTrees.jones_inspector(ns.inspect('E'),Ejones) );
    
  # finally, make the sinks and vdm. Visualizers will be executed
  # after ("post") all sinks
  Meow.Context.vdm = Meow.StdTrees.make_sinks(ns,corrected,post=visualizers);
                                           
  # now define some runtime solve jobs
  solve_tree.define_solve_job("Calibrate source fluxes","flux",
                              predict.search(tags="(flux|spectrum) solvable"));
                                  
  GPs = predict.search(tags="G phase");
  solve_tree.define_solve_job("Calibrate G phases","g_phase",GPs);
  
  GAs = predict.search(tags="G ampl");
  solve_tree.define_solve_job("Calibrate G amplitudes","g_ampl",GAs);
  
  if include_E_jones:
    EPs = predict.search(tags="E phase");
    solve_tree.define_solve_job("Calibrate E phases","e_phase",EPs);
    solve_tree.define_solve_job("Calibrate GE phases","ge_phase",GPs+EPs);
    EAs = predict.search(tags="E ampl");
    solve_tree.define_solve_job("Calibrate E amplitudes","e_ampl",EAs);
    solve_tree.define_solve_job("Calibrate GE amplitudes","ge_ampl",GAs+EAs);

  # insert standard imaging options from Meow
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
  
  # add some useful bookmarks
  Bookmarks.Page("Fluxes and coherencies") \
    .add(source_list[0].stokes("I")) \
    .add(source_list[1].stokes("I")) \
    .add(source_list[0].stokes("Q")) \
    .add(source_list[1].stokes("Q")) \
    .add(source_list[0].coherency()) \
    .add(solve_tree.solver());
  
  pg = Bookmarks.Page("G Jones",3,3);
  for p in array.stations():
    pg.add(Gjones(p));
  
  if include_E_jones:
    pg = Bookmarks.Page("E Jones",3,3);
    for p in array.stations():
      pg.add(Ejones(p));
  
  Bookmarks.Page("Vis Inspectors",1,2) \
    .add(ns.inspect('spigots'),viewer="Collections Plotter") \
    .add(ns.inspect('residuals'),viewer="Collections Plotter");
  
  
  


Settings.forest_state.cache_policy = 1  # -1 for minimal, 1 for smart caching, 100 for full caching


if __name__ == '__main__':
    Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);
    ns.Resolve();
    pass
              
