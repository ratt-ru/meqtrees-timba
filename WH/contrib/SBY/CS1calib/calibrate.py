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

import Meow
from Meow import IfrArray
from Meow import Observation
from Meow import Patch
from Meow import CorruptComponent
from Meow import Bookmarks
from Meow import Jones


import global_model 
from Timba.LSM.LSM import LSM

# MS name
TDLRuntimeOption('msname',"MS",["L2007_01384_SB4-5.MS", "L2007_00769_S6.MS", "L2007_00770_S6.MS", "L2006_00658.MS","L2006_00659.MS"],inline=True);


TDLRuntimeOption('input_column',"Input MS column",["DATA","MODEL_DATA","CORRECTED_DATA"],default=0);

# ms_output = False  # if True, outputs to MS, else to BOIO dump   
TDLRuntimeOption('output_column',"Output MS column",[None,"MODEL_DATA","CORRECTED_DATA"],default=0);

# how much to perturb starting values of solvables
TDLRuntimeOption('perturbation',"Perturb solvables",["random",.1,.2,-.1,-.2]);

# solver debug level
TDLRuntimeOption('solver_debug_level',"Solver debug level",[0,1,10]);

# solver debug level
TDLRuntimeOption('solver_lm_factor',"Initial solver LM factor",[1,.1,.01,.001]);


# number of timeslots to use at once
TDLRuntimeOption('tile_size',"Tile size",[1,5,30,48,60,96,480,960,2400]);

# number of stations
TDLCompileOption('num_stations',"Number of stations",[16,14,15,3,27]);

# which source model to use
# source_model = clar_model.point_and_extended_sources;
TDLCompileOption('source_model',"Source model",[
    global_model.point_and_extended_sources_abs, # absolute
  ],default=0);
  
# selection  applied to MS, None for full MS
ms_selection = None
# or e.g.: 
ms_selection = record(channel_start_index=0,
                      channel_end_index=511,
                      channel_increment=1,
                      selection_string='',
                      ddid_index=5)

ms_selection = None

# MS input queue size -- should be at least equal to the no. of ifrs
ms_queue_size = 500

# if False, BOIO dump will be generated instead of MS. Useful for benchmarking
ms_output = True;



    
def _define_forest(ns):
  # create array model
  stations = range(1,num_stations+1);
  #array = IfrArray(ns,stations,uvw_table=mep_derived,mirror_uvw=True);
  array = IfrArray(ns,stations,mirror_uvw=False);
  # we have phase tracking
  observation = Observation(ns);
  
  # create nominal CLAR source model by calling the specified
  # function
  lsm=LSM()
 
  ## without phase tracking
  #lsm.build_from_catalog("global1.txt",ns) # NVSS catalog
  lsm.build_from_extlist("global.txt",ns) # by hand

  lsm.display()

  source_list = source_model(ns,lsm);

  # add EJones
  beam_parms=[];
  #Ej = global_model.EJones(ns,array,source_list,observation.phase_centre.radec(),meptable='Ejones.mep',solvables=beam_parms,solvable=False);
  Ej = global_model.EJones_P(ns,array,source_list,observation.phase_centre.radec(),meptable='',solvables=beam_parms,solvable=False);
  print beam_parms
  corrupt_list = [
      CorruptComponent(ns,src,label='E',station_jones=Ej(src.direction.name))
      for src in source_list
  ];

  allsky = Patch(ns,'all',observation.phase_centre);
  allsky.add(*corrupt_list);
 
  # create simulated visibilities for sky
  visibilities = allsky.visibilities(array,observation);
  

  aasave=True;
  # Jones
  for station in array.stations():
    ns.Jreal11(station)<<Meq.Parm(1,node_groups='Parm',solvable=1,table_name="what.mep", use_previous=2,save_all=aasave)
    ns.Jimag11(station)<<Meq.Parm(0,node_groups='Parm',solvable=1,table_name="what.mep", use_previous=2,save_all=aasave)
    ns.J11(station)<<Meq.ToComplex(ns.Jreal11(station),ns.Jimag11(station))
    ns.Jreal22(station)<<Meq.Parm(1,node_groups='Parm',solvable=1,table_name="what.mep", use_previous=2,save_all=aasave)
    ns.Jimag22(station)<<Meq.Parm(0,node_groups='Parm',solvable=1,table_name="what.mep", use_previous=2,save_all=aasave)
    ns.J22(station)<<Meq.ToComplex(ns.Jreal22(station),ns.Jimag22(station))
    ns.Jreal12(station)<<Meq.Parm(0,node_groups='Parm',solvable=1,table_name="what.mep", use_previous=2,save_all=aasave)
    ns.Jimag12(station)<<Meq.Parm(0,node_groups='Parm',solvable=1,table_name="what.mep", use_previous=2,save_all=aasave)
    ns.J12(station)<<Meq.ToComplex(ns.Jreal12(station),ns.Jimag12(station))
    ns.Jreal21(station)<<Meq.Parm(0,node_groups='Parm',solvable=1,table_name="what.mep", use_previous=2,save_all=aasave)
    ns.Jimag21(station)<<Meq.Parm(0,node_groups='Parm',solvable=1,table_name="what.mep", use_previous=2,save_all=aasave)
    ns.J21(station)<<Meq.ToComplex(ns.Jreal21(station),ns.Jimag21(station))

    ns.G(station)<<Meq.Matrix22(ns.J11(station), ns.J12(station), ns.J21(station), ns.J22(station))


  allsky = CorruptComponent(ns,allsky,label='G',station_jones=ns.G);

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

  ###
  Jones.apply_correction(ns.corrected,ns.spigot,ns.G,array.ifrs());

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

  # create visdata mux
  ns.VisDataMux.add_children(*[ns.sink(*ifr) for ifr in array.ifrs()]);
  ns.VisDataMux.add_stepchildren(*[ns.spigot(*ifr) for ifr in array.ifrs()]);


def create_solver_defaults(num_iter=15,epsilon=1e-4,convergence_quota=0.9,solvable=[]):
  solver_defaults=record()
  solver_defaults.num_iter      = num_iter
  solver_defaults.epsilon       = epsilon
  solver_defaults.epsilon_deriv = epsilon
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
  

def _perturb_solvables (mqs,solvables,rng=[0.2,0.3]):
  global perturbation;
  for name in solvables:
    polc = mqs.getnodestate(name).real_polc;
    if perturbation == "random":
      polc.coeff[0,0] *= 1 + random.uniform(*rng)*random.choice([-1,1]);
    else:
      polc.coeff[0,0] *= 1+perturbation;
    set_node_state(mqs,name,record(init_funklet=polc));
  return solvables;
    
def _reset_solvables (mqs,solvables,value=None):
  for name in solvables:
    polc = mqs.getnodestate(name).real_polc;
    if value is not None:
      polc.coeff[0,0] = value;
    set_node_state(mqs,name,record(init_funklet=polc));
  return solvables;


def create_inputrec (_ms_selection):
  boioname = "boio."+msname+".predict."+str(tile_size);
  # if boio dump for this tiling exists, use it to save time
  if not _ms_selection and os.access(boioname,os.R_OK):
    rec = record(boio=record(boio_file_name=boioname,boio_file_mode="r"));
  # else use MS, but tell the event channel to record itself to boio file
  else:
    rec = record();
    rec.ms_name          = msname
    rec.data_column_name = input_column;
    rec.tile_size        = tile_size
    rec.selection = _ms_selection or record();
    rec = record(ms=rec);
  rec.python_init = 'Meow.ReadVisHeader';
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


def _run_solve_job (mqs,solvables,_ms_selection,wait=False):
  """common helper method to run a solution with a bunch of solvables""";
  req = meq.request();
  req.input  = create_inputrec(_ms_selection);
  if output_column is not None:
    req.output = create_outputrec(output_column);

  # set solvables list in solver
  solver_defaults = create_solver_defaults(solvable=solvables)
  set_node_state(mqs,'solver',solver_defaults)

  # req.input.max_tiles = 1;  # this can be used to shorten the processing, for testing
  mqs.execute('VisDataMux',req,wait=wait);
  pass

ms_selection=record(channel_start_index=99,
          channel_end_index=109,
          channel_increment=1,
          ddid_index=1,
          selection_string='sumsqr(UVW[1:2]) > 100')

#ms_selection = None

def _tdl_job_0_solve_for_GJones(mqs,parent,**kw):
  solvables = ['Jreal11:'+str(station) for station in range(1,num_stations+1)];
  solvables += ['Jimag11:'+str(station) for station in range(1,num_stations+1)];
  solvables += ['Jreal12:'+str(station) for station in range(1,num_stations+1)];
  solvables += ['Jimag12:'+str(station) for station in range(1,num_stations+1)];
  solvables += ['Jreal21:'+str(station) for station in range(1,num_stations+1)];
  solvables += ['Jimag21:'+str(station) for station in range(1,num_stations+1)];
  solvables += ['Jreal22:'+str(station) for station in range(1,num_stations+1)];
  solvables += ['Jimag22:'+str(station) for station in range(1,num_stations+1)];

  #solvables += ['sigma1:S1','sigma2:S1','phi:S1']
  #solvables += ['I0:S6','Q:S6','U:S6','V:S6']
  
  _run_solve_job(mqs,solvables,ms_selection);
 
def _tdl_job_0_solve_for_GJones_Batch(mqs,parent,**kw):
  solvables = ['Jreal11:'+str(station) for station in range(1,num_stations+1)];
  solvables += ['Jimag11:'+str(station) for station in range(1,num_stations+1)];
  solvables += ['Jreal12:'+str(station) for station in range(1,num_stations+1)];
  solvables += ['Jimag12:'+str(station) for station in range(1,num_stations+1)];
  solvables += ['Jreal21:'+str(station) for station in range(1,num_stations+1)];
  solvables += ['Jimag21:'+str(station) for station in range(1,num_stations+1)];
  solvables += ['Jreal22:'+str(station) for station in range(1,num_stations+1)];
  solvables += ['Jimag22:'+str(station) for station in range(1,num_stations+1)];

  step=8;
  for schan in range(31,223,step):
    ms_selection=record(channel_start_index=schan,
          channel_end_index=schan+step-1,
          channel_increment=1,
          ddid_index=1,
          selection_string='sumsqr(UVW[1:2]) > 100')
    parmtablename="E"+str(schan)+"_.mep";
    # update parmtablename
    for sname in solvables:
       set_node_state(mqs,sname,record(table_name=parmtablename))
    _run_solve_job(mqs,solvables,ms_selection,wait=True);


  


Settings.forest_state.cache_policy = 1;  # 1 for smart caching, 100 for full caching

Settings.orphans_are_roots = False;


def _test_compilation ():
  ns = NodeScope();
  _define_forest(ns);
  ns.Resolve();

if __name__ == '__main__':
  if '-prof' in sys.argv:
    import profile
    profile.run('_test_compilation()','clar_fast_predict.prof');
  else:
#    Timba.TDL._dbg.set_verbose(5);
    _test_compilation();
              
