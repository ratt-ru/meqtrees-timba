
#% $Id$ 

#
# Copyright (C) 2002-2007
# ASTRON (Netherlands Foundation for Research in Astronomy)
# and The MeqTree Foundation
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *
from Timba.Meq import meq
from numarray import *
import os
import random

import clar_model 
from Meow.IfrArray import IfrArray
from Meow.Observation import Observation
from Meow.Patch import Patch
from Meow.CorruptComponent import CorruptComponent 
from Meow import Bookmarks,Utils


# MS name
Utils.include_ms_options(tile_sizes=[30,48,60,96,480,960]);
Utils.include_imaging_options();

# how much to perturb starting values of solvables
parm_options = [
  TDLOption('perturbation',"Perturb solvables by (rel.)",["random",.1,.2,-.1,-.2]),
] + Utils.parameter_options();

TDLRuntimeMenu("Parameter options",*parm_options);
# solver runtime options
TDLRuntimeMenu("Solver options",*Utils.solver_options());

# number of stations
TDLCompileOption('num_stations',"Number of stations",[27,14,3]);

# which source model to use
# source_model = clar_model.point_and_extended_sources;
TDLCompileOption('source_model',"Source model",[
    clar_model.solve_point_and_extended_sources,
    clar_model.solve_point_sources_only,
    clar_model.radio_galaxy
  ],default=0);

### MEP table for derived quantities 
mep_derived = 'CLAR_DQ_27-480.mep';

### MEP table for fitted parameters
### If set to a table name, results of solution will be stored and reused
### in future runs. This is usually not what we want for testing, so we can 
### set it to None to solve from scratch every time.
Utils.source_table = None;
# mep_sources = 'CLAR.mep';



# bookmarks
Settings.forest_state = record(bookmarks=[
  record(name='Predicted visibilities',page=Bookmarks.PlotPage(
      ["visibility:all:1:2","spigot:1:2","residual:1:2"],
      ["visibility:all:1:9","spigot:1:9","residual:1:9"],
      ["visibility:all:18:27","spigot:18:27","residual:18:27"],
      ["visibility:all:26:27","spigot:26:27","residual:26:27"]
  )), 
  record(name='Solutions',page=Bookmarks.PlotPage(
      ["I:S1","I:S2","I:S3"],
      ["I:S4","I:S5","I:S6"],
      ["I:S7","I:S8","I:S9"],
      ["I:S10","hpbw","solver"]
  )) 
]);


def _define_forest(ns):
  # create array model
  stations = range(1,num_stations+1);
  array = IfrArray(ns,stations,uvw_table=mep_derived,mirror_uvw=True);
  observation = Observation(ns);
  
  # create CLAR source model
  # create nominal CLAR source model by calling the specified
  # function
  clar_model.init_directions(ns);
  global source_list;
  source_list = source_model(ns);
  
  Ej = clar_model.EJones(ns,array,source_list);
  corrupt_list = [ 
    CorruptComponent(ns,src,label='E',station_jones=Ej(src.name))
    for src in source_list
  ];
                     
  # create all-sky patch for CLAR source model
  allsky = Patch(ns,'all',observation.phase_centre);
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
    reqseq = Meq.ReqSeq(ns.solver,ns.residual(sta1,sta2),
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
  
  
def _tdl_job_1_solve_for_fluxes_and_beam_width (mqs,parent,**kw):
  solvables = Utils.perturb_parameters(mqs,['I0:'+src.name for src in source_list]);
  solvables += Utils.reset_parameters(mqs,[ 'spi:'+src.name for src in source_list],0);
  solvables += Utils.reset_parameters(mqs,["hpbw0"],7);
  Utils.run_solve_job(mqs,solvables);
  

def _tdl_job_2_solve_for_fluxes_with_fixed_beam_width (mqs,parent,**kw):
  solvables = Utils.perturb_parameters(mqs,['I0:'+src.name for src in source_list]);
  solvables += Utils.reset_parameters(mqs,[ 'spi:'+src.name for src in source_list],0);
  Utils.run_solve_job(mqs,solvables);
  
  
def _tdl_job_3_solve_for_beam_width_with_fixed_fluxes (mqs,parent,**kw):
  solvables = Utils.reset_parameters(mqs,["hpbw0"],7);
  Utils.run_solve_job(mqs,solvables);
  

def _tdl_job_4_reset_parameters_to_true_values (mqs,parent,**kw):
  Utils.reset_parameters(mqs,['I0:'+src.name for src in source_list]);
  Utils.reset_parameters(mqs,[ 'spi:'+src.name for src in source_list]);
  Utils.reset_parameters(mqs,["hpbw0"]);

def _tdl_job_5_solve_for_gaussian_parameters (mqs,parent,**kw):
  solvables = Utils.reset_parameters(mqs,["I0:S1"],1.36)
  solvables += Utils.reset_parameters(mqs,["I0:S2"],1.77)
  solvables += Utils.reset_parameters(mqs,["I0:S3"],0.35)
  solvables += Utils.reset_parameters(mqs,["I0:S4"],1.12)
  solvables += Utils.reset_parameters(mqs,["I0:S5"],3.66)
  solvables += Utils.reset_parameters(mqs,["sigma1:S1"],0.0001)
  solvables += Utils.reset_parameters(mqs,["sigma2:S1"],0.0001)
  solvables += Utils.reset_parameters(mqs,["sigma1:S2"],0.0001)
  solvables += Utils.reset_parameters(mqs,["sigma2:S2"],0.0001)
  solvables += Utils.reset_parameters(mqs,["sigma1:S4"],0.0001)
  solvables += Utils.reset_parameters(mqs,["sigma2:S4"],0.0001)
  Utils.run_solve_job(mqs,solvables);

def _tdl_job_6_make_image (mqs,parent):
  Utils.make_dirty_image(npix=1024,cellsize='.25arcsec',channels=[32,1,1]);

Settings.forest_state.cache_policy = 1  # -1 for minimal, 1 for smart caching, 100 for full caching
Settings.orphans_are_roots = True

if __name__ == '__main__':


    Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);


    ns.Resolve();
    pass
              
