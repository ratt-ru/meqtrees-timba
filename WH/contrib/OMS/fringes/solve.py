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
from numarray import *
import os
import random

import models

import Meow


from Meow.IfrArray import IfrArray
from Meow.Observation import Observation
from Meow.Patch import Patch
from Meow.CorruptComponent import CorruptComponent 
from Meow.SkyComponent import create_polc 
from Meow.PointSource import PointSource 
from Meow.GaussianSource import GaussianSource 
from Meow import Jones
from Meow import Bookmarks
from Meow import Utils


# MS name
Utils.include_ms_options();
Utils.include_imaging_options();

# how much to perturb starting values of solvables
parm_options = [
  TDLOption('flux_perturbation',"Perturb fluxes by (rel.)",["random",.1,.2,-.1,-.2]),
  TDLOption('pos_perturbation',"Perturb positions by (arcsec)",[.1,.25,1,2])
] + Utils.parameter_options();

TDLRuntimeMenu("Parameter options",*parm_options);
# solver runtime options
TDLRuntimeMenu("Solver options",*Utils.solver_options());

# imaging mode for imager script
TDLRuntimeOption('imaging_mode',"Imaging mode",["mfs","channel"]);
  
# source model
TDLCompileOption('source_model',"Source model",[
    models.cps,
    models.cps_plus_faint_extended,
    models.two_point_sources,
    models.two_bright_one_faint_point_source
  ],default=0);
  
# fitting options
TDLCompileMenu("Fitting options",
  TDLOption('fringe_deg_time',"Polc degree (time) for fringe fitting",[0,1,2,3,4,5]),
  TDLOption('fringe_deg_freq',"Polc degree (freq) for fringe fitting",[0,1,2,3,4,5]),
  TDLOption('flux_constraint',"Lower boundary for flux constraint",[None,0,.1,.5,.8,.99]),
  TDLOption('constraint_weight',"Weight of flux constraint",["intrinsic",100,1000,10000])
);

TDLCompileOption('output_type',"Output visibilities",["corrected","residual"]);

# number of stations
TDLCompileOption('num_stations',"Number of stations",[27,14,3]);

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




def _define_forest(ns):
  # create array model
  stations = range(1,num_stations+1);
  array = IfrArray(ns,stations);
  observation = Observation(ns);
  
  # create CLAR source model
  # create nominal CLAR source model by calling the specified
  # function
  global source_list;
  source_list = source_model(ns,Utils.get_source_table());
  
  # create all-sky patch for CLAR source model
  allsky = Patch(ns,'all',observation.phase_centre);
  allsky.add(*source_list);
  
  # Add solvable G jones terms
  for station in array.stations():
    ns.phase(station) << Utils.phase_parm(fringe_deg_time,fringe_deg_freq);
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
                                   output_col='DATA',
                                   children=reqseq
                                   );
                                   
  # create visdatamux
  global _vdm;
  _vdm = ns.VisDataMux << Meq.VisDataMux;
  ns.VisDataMux.add_children(*[ns.sink(*ifr) for ifr in array.ifrs()]);
  ns.VisDataMux.add_stepchildren(*[ns.spigot(*ifr) for ifr in array.ifrs()]);
  

arcsec_to_rad = math.pi/(180*3600);

def _tdl_job_1_solve_for_all_source_parameters (mqs,parent,**kw):
  solvables = [];
  for src in source_list:
    pert_ra = random.uniform(-pos_perturbation,pos_perturbation);
    solvables += Utils.perturb_parameters(mqs,['ra:'+src.name],
                  pert=arcsec_to_rad*pert_ra,absolute=True);
    pert_dec = random.uniform(-pos_perturbation,pos_perturbation);
    solvables += Utils.perturb_parameters(mqs,['dec:'+src.name],
                  pert=arcsec_to_rad*pert_dec,absolute=True);
    if src.has_spectral_index():
      solvables += Utils.perturb_parameters(mqs,['I0:'+src.name],
                    pert=flux_perturbation,absolute=False);
      solvables += Utils.reset_parameters(mqs,[src.spectral_index().name],0);
    else:
      solvables += Utils.perturb_parameters(mqs,['I:'+src.name],
                    pert=flux_perturbation,absolute=False);
    if isinstance(src,GaussianSource):
      solvables += Utils.perturb_parameters(mqs,['sigma1:'+src.name]);
      solvables += Utils.perturb_parameters(mqs,['sigma2:'+src.name]);
      solvables += Utils.reset_parameters(mqs,['phi:'+src.name],0);
  Utils.run_solve_job(mqs,solvables);
  
def _tdl_job_2_solve_for_phases_and_fluxes (mqs,parent,**kw):
  if constraint_weight == "intrinsic":
    constrain = [flux_constraint,2.];
  else:
    constrain = None;
  solvables = Utils.perturb_parameters(mqs,['I0:'+src.name for src in source_list],
               pert=flux_perturbation,absolute=False,
               constrain=constrain);
  solvables += Utils.reset_parameters(mqs,['phase:'+str(sta) for sta in range(1,num_stations+1)],0);
  Utils.run_solve_job(mqs,solvables);

def _tdl_job_2a_solve_for_phases_with_fixed_fluxes (mqs,parent,**kw):
  Utils.reset_parameters(mqs,['I0:'+src.name for src in source_list],reset=True);
  solvables = Utils.reset_parameters(mqs,['phase:'+str(sta) for sta in range(1,num_stations+1)],0);
  Utils.run_solve_job(mqs,solvables);

def _tdl_job_2b_solve_for_phases_with_fixed_fluxes_14_27 (mqs,parent,**kw):
  Utils.reset_parameters(mqs,['I0:'+src.name for src in source_list],reset=True);
  solvables = Utils.reset_parameters(mqs,['phase:'+str(sta) for sta in range(15,num_stations+1)],0);
  Utils.run_solve_job(mqs,solvables);

def _tdl_job_8_clear_out_all_previous_solutions (mqs,parent,**kw):
  os.system("rm -fr "+Utils.get_source_table());
  os.system("rm -fr "+Utils.get_mep_table());

def _tdl_job_9a_make_dirty_image (mqs,parent,**kw):
  Utils.make_dirty_image(npix=512,cellsize='.5arcsec',channels=[32,1,1]);

Settings.forest_state.cache_policy = 1  # -1 for minimal, 1 for smart caching, 100 for full caching
Settings.orphans_are_roots = True

if __name__ == '__main__':


    Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);


    ns.Resolve();
    pass
              
