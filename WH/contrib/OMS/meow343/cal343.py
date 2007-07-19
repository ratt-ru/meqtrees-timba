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

from Timba.TDL import *
from Timba.Meq import meq
from Timba.LSM.LSM import LSM
from numarray import *
import os
import random

import Meow

from Meow import Jones
from Meow import Bookmarks
from Meow import Utils
import Meow.StdTrees
import lsm_model

# number of stations
TDLCompileOption('num_stations',"Number of stations",[14,3],more=int);

TDLCompileMenu("What do we want to do",
  TDLOption('do_solve',"Calibrate",True),
  TDLOption('do_subtract',"Subtract sky model",True),
  TDLOption('do_correct',"Correct",True));
  

import models343
import wsrt_beam
# source model -- note how list is formed up on-the-fly from 
# contents of the models343 module
TDLCompileOption('source_model',"Source model",
  [ getattr(models343,func) for func in dir(models343) if callable(getattr(models343,func)) and func.startswith('m343_')],
 );

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
TDLCompileOption('include_sawtooth',"Include sawtooth ripple effect",False),
TDLCompileMenu("LSM options",
  TDLOption('lsm_count',"Include how many LSM sources",[None,10,20,100],more=int),
  TDLOption('lsm_gui',"Display LSM GUI",False),
  TDLOption('lsm_i_freq_deg',"I freq degree",[0,1],more=int),
  TDLOption('lsm_q_freq_deg',"Q freq degree",[0,1],more=int),
  TDLOption('lsm_beam_model',"Beam model for LSM sources",
      [None,wsrt_beam.wsrt_beam,wsrt_beam.wsrt_pol_beam,
      wsrt_beam.wsrt_pol_beam_with_pointing_errors]),
);

  
from Timba import pynode

class PySawtooth (pynode.PyNode):
  def __init__ (self,*args):
    pynode.PyNode.__init__(self,*args);

  def get_result (self,children,request):
    if len(children):
      raise TypeError,"this is a leaf node, no children expected!";
    # make value of same shape as cells
    nfreq = len(request.cells.grid.freq);
    shape = meq.shape(freq=nfreq);
    value = meq.vells(shape);
    # fill with -1/+1 sawtooth
    flat = value.getflat();   # 'flat' reference to array data
    for i in range(len(flat)):
      flat[i] = (i%2)*2-1;
    return meq.result(meq.vellset(value),request.cells);


def _define_forest(ns):
  if not ( do_solve or do_subtract or do_correct ):
    raise ValueError,"Nothing to do, please enable something in the Options|What to do menu";

  # enable standard MS options from Meow
  if do_solve:
    tile_sizes = None;            # solve jobs will provide their own tiling
  else:
    tile_sizes = [100,200,500];   # no solve jobs, provide global tiling
    
  Utils.include_ms_options(
    tile_sizes=tile_sizes,
    channels=[[15,40,1],[15,40,2]]
  );

  # create array model
  array = Meow.IfrArray.WSRT(ns,num_stations);
  observation = Meow.Observation(ns);
  # setup Meow global context
  Meow.Context.set(array=array,observation=observation);
  
  # create all-sky patch for source model
  allsky = Meow.Patch(ns,'all',observation.phase_centre);
  
  # create 343 source model
  source_list = source_model(ns,Utils.get_source_table());
    
  lsm_beam_parms = [];
  # add LSM sources
  if lsm_count is not None:
    lsm = LSM();
    lsm.build_from_catalog("3c343-nvss.txt",ns);
    if lsm_gui:
      lsm.display()
    Idef = Meow.Parm(1e-2,freq_deg=lsm_i_freq_deg,tags="lsm",table_name=Meow.Utils.get_source_table());
    Qdef = Meow.Parm(0,freq_deg=lsm_q_freq_deg,tags="lsm",table_name=Meow.Utils.get_source_table());
    lsm_list = lsm_model.LSMToMeowList(ns,lsm,count=lsm_count,I=Idef,Q=Qdef);
    
    pg = Bookmarks.Page("LSM fluxes",3,3);
    for src in lsm_list:
      pg.add(src.stokes("I"));
      pg.add(src.stokes("Q"));
        
    # corrupt with LSM beams, if a model is specified
    if lsm_beam_model:
      lsm_list = lsm_beam_model(ns,ns.E1,lsm_list);
      lsm_beam_parms = ns.E1.search(tags="beam solvable");
      pg = Bookmarks.Page("LSM beams",3,3);
      for p in lsm_beam_parms:
        pg.add(p);
      for src in lsm_list:
        pg.add(ns.E1(src.direction.name));
    else:
      lsm_beam_parms = [];
    
    source_list += lsm_list;
  
  # definitions for ampl/phase parameters
  g_ampl_def = Meow.Parm(1,freq_deg=ga_freq_deg,table_name=Utils.get_mep_table());
  g_phase_def = Meow.Parm(0,freq_deg=gp_freq_deg,tiling=gp_tiling,table_name=Utils.get_mep_table());

  # differential corrections present? 
  if include_E_jones:
    # first source is presumably at phase center, so only G itelf will aplly
    allsky.add(source_list[0]);
    # apply E to second source
    e_ampl_def = Meow.Parm(1,freq_deg=ea_freq_deg,table_name=Utils.get_mep_table());
    e_phase_def = Meow.Parm(0,freq_deg=ep_freq_deg,tiling=ep_tiling,table_name=Utils.get_mep_table());
    Ejones = Jones.gain_ap_matrix(ns.E(source_list[1].name),e_ampl_def,e_phase_def,
                                  tags="E",series=array.stations());
    # add corrupted source to patch
    allsky.add(source_list[1].corrupt(Ejones));
    allsky.add(*source_list[2:]);
  else:
    allsky.add(*source_list);
  # apply G to whole sky
  Gjones = Jones.gain_ap_matrix(ns.G,g_ampl_def,g_phase_def,
                                tags="G",series=array.stations());
  allsky = allsky.corrupt(Gjones);

  # only a G Jones correction will be applied
  correct_for_jones = [Gjones];

  # create simulated visibilities for the sky
  predict = allsky.visibilities();
  
  # apply sawtooth to visiblities
  if include_sawtooth:
    ns.sawtooth0 << Meq.PyNode(class_name="PySawtooth",module_name=__file__);
    ns.sta << Meq.Parm(0,table_name=Meow.Utils.get_mep_table());
    ns.sawtooth << 1 + ns.sawtooth0*ns.sta;
    
    for p,q in array.ifrs():
      ns.predict_st(p,q) << predict(p,q)*ns.sawtooth;
    predict = ns.predict_st;
    
    Bookmarks.Page("Sawtooth solution",1,2) \
        .add(ns.sawtooth) \
        .add(ns.solver);

  # select main tree type, and generate pre-correction nodes
  if do_solve or do_subtract:
    solve_tree = Meow.StdTrees.SolveTree(ns,predict);
    if do_subtract:
      outputs = solve_tree.residuals(array.spigots());
    else:
      outputs = array.spigots();
  # no solve/subtract, so outputs are just spigots
  else:
    outputs = array.spigots();
  
  # now insert corrections
  if do_correct:
    outputs = Jones.apply_correction(ns.corrected,outputs,correct_for_jones);
    # apply correction for sawtooth
    if include_sawtooth:
      ns.inv_sawtooth = 1/ns.sawtooth;
      for p,q in array.ifrs():
        ns.corrected_st(p,q) << outputs(p,q)*ns.inv_sawtooth;
      outputs = ns.corrected_st;
      
  # finally, make solve/sequencer tree from spigots and outputs
  if do_solve:
    outputs = solve_tree.sequencers(array.spigots(),outputs);

  # create some visualizers
  visualizers = [
    Meow.StdTrees.vis_inspector(ns.inspect('spigots'),array.spigots(),bookmark=False),
    Meow.StdTrees.vis_inspector(ns.inspect('outputs'),outputs,bookmark=False),
    Meow.StdTrees.jones_inspector(ns.inspect('G'),Gjones)
  ];
  if include_E_jones:
    visualizers.append( Meow.StdTrees.jones_inspector(ns.inspect('E'),Ejones) );
    
  # finally, make the sinks and vdm. Visualizers will be executed
  # after ("post") all sinks
  Meow.Context.vdm = Meow.StdTrees.make_sinks(ns,outputs,post=visualizers);
                                           
  # now define some runtime solve jobs
  if do_solve:
    solve_tree.define_solve_job("Calibrate bright sources","flux",
         predict.search(tags="bright (flux|spectrum) solvable"));

    if lsm_count is not None:
      solve_tree.define_solve_job("Calibrate LSM sources","flux_lsm",
           predict.search(tags="lsm (flux|spectrum) solvable")+lsm_beam_parms);

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

    if include_sawtooth:
      solve_tree.define_solve_job("Calibrate sawtooth amplitude","st_ampl",[ns.sta]);
  else:
    # include job for subtract/correct
    def job_subtract_correct (mqs,parent,**kw):
      req = Meow.Utils.create_io_request();
      mqs.execute('VisDataMux',req,wait=False);
    TDLRuntimeJob(job_subtract_correct,"Subtract and/or correct");

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
  TDLRuntimeJob(job_clear_out_all_previous_solutions,"Clear out all solutions");
  
  # add some useful bookmarks
  pg = Bookmarks.Page("Fluxes and coherencies") \
    .add(source_list[0].stokes("I")) \
    .add(source_list[1].stokes("I")) \
    .add(source_list[0].stokes("Q")) \
    .add(source_list[1].stokes("Q")) \
    .add(source_list[0].coherency());
  if do_solve:
    pg.add(solve_tree.solver());
  
  
  Bookmarks.Page("Vis Inspectors",1,2) \
    .add(ns.inspect('inputs'),viewer="Collections Plotter") \
    .add(ns.inspect('outputs'),viewer="Collections Plotter");


Settings.forest_state.cache_policy = 1  # -1 for minimal, 1 for smart caching, 100 for full caching


if __name__ == '__main__':
    Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);
    ns.Resolve();
    pass
              
