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
import os, re
import random

import Meow
from Meow import PointSource
from Meow import IfrArray
from Meow import Observation
from Meow import Patch
from Meow import CorruptComponent 
from Meow import Bookmarks

from Meow import Jones


import global_model 
from Timba.LSM.LSM import LSM

# MS name
TDLRuntimeOption('msname',"MS",["L2007_01576_SB4-5.MS", "L2007_01576_SB2-copy.MS", "L2007_01061_SB4-5.MS"],inline=True);


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
TDLRuntimeOption('tile_size',"Tile size",[1,10,30,48,60,96,480,960,2400]);

# number of stations
TDLCompileOption('num_stations',"Number of stations",[16,14,15,3,27]);

# which source model to use
# source_model = clar_model.point_and_extended_sources;
TDLCompileOption('source_model',"Source model",[
    global_model.point_and_extended_sources_abs, # absolute
  ],default=0);
  
 
### MS input queue size -- must be at least equal to the no. of ifrs
ms_queue_size = 500

ms_output = True     # if True, outputs to MS, else to BOIO dump   Tony


### MEP table for fitted parameters
### If set to a table name, results of solution will be stored and reused
### in future runs. This is usually not what we want for testing, so we can 
### set it to None to solve from scratch every time.
mep_sources = None;
# mep_sources = 'CLAR.mep';




def _define_forest(ns):
  mytable=None
  # create array model
  stations = range(1,num_stations+1);
  array = IfrArray(ns,stations,mirror_uvw=False);
  observation = Observation(ns);
  
  lsm=LSM()
  lsm.build_from_extlist("global_2.txt",ns)

  lsm.display()

  global source_list;
  source_list = source_model(ns,lsm);
  
  # only add sources that you want to subtract here
  sublist0=[];
  sublist1=[];
  ordlist=[];

  for sname in source_list:
    if re.match("S0$",sname.name):
     sublist0.append(sname);
    elif re.match("S1$",sname.name):
     sublist1.append(sname);
    elif re.match("S3$",sname.name):
     sublist1.append(sname);
    elif re.match("S4$",sname.name):
     sublist1.append(sname);
    else:
     ordlist.append(sname);


  corrupt_list=sublist0;
  def_tiling=record(time=1)
  #def_tiling=None;

  for station in array.stations():
    ns.Jreal11(station,0)<<Meq.Parm(1,node_groups='Parm',solvable=1,table_name=mytable, use_previous=2, save_all=True, tiling=def_tiling)
    ns.Jimag11(station,0)<<Meq.Parm(0,node_groups='Parm',solvable=1,table_name=mytable, use_previous=2, save_all=True, tiling=def_tiling)
    ns.J11(station,0)<<Meq.ToComplex(ns.Jreal11(station,0),ns.Jimag11(station,0))
    ns.Jreal12(station,0)<<Meq.Parm(0,node_groups='Parm',solvable=1,table_name=mytable, use_previous=2, save_all=True, tiling=def_tiling)
    ns.Jimag12(station,0)<<Meq.Parm(0,node_groups='Parm',solvable=1,table_name=mytable, use_previous=2, save_all=True, tiling=def_tiling)
    ns.J12(station,0)<<Meq.ToComplex(ns.Jreal12(station,0),ns.Jimag12(station,0))
    ns.Jreal22(station,0)<<Meq.Parm(1,node_groups='Parm',solvable=1,table_name=mytable, use_previous=2, save_all=True, tiling=def_tiling)
    ns.Jimag22(station,0)<<Meq.Parm(0,node_groups='Parm',solvable=1,table_name=mytable, use_previous=2, save_all=True, tiling=def_tiling)
    ns.J22(station,0)<<Meq.ToComplex(ns.Jreal22(station,0),ns.Jimag22(station,0))

    ns.Jreal21(station,0)<<Meq.Parm(0,node_groups='Parm',solvable=1,table_name=mytable, use_previous=2, save_all=True, tiling=def_tiling)
    ns.Jimag21(station,0)<<Meq.Parm(0,node_groups='Parm',solvable=1,table_name=mytable, use_previous=2, save_all=True, tiling=def_tiling)
    ns.J21(station,0)<<Meq.ToComplex(ns.Jreal21(station,0),ns.Jimag21(station,0))


    ns.G0(station)<<Meq.Matrix22(ns.J11(station,0), ns.J12(station,0), ns.J21(station,0), ns.J22(station,0))
  # create all-sky patch for source model
  allsky = Patch(ns,'all0',observation.phase_centre);
  allsky.add(*corrupt_list);
  allskyG0 = CorruptComponent(ns,allsky,label='G0',station_jones=ns.G0);

  predictG0 = allskyG0.visibilities(array,observation);



  corrupt_list=sublist1;
  for station in array.stations():
    ns.Jreal11(station,1)<<Meq.Parm(1,node_groups='Parm',solvable=1,table_name=mytable, use_previous=2, save_all=True, tiling=def_tiling)
    ns.Jimag11(station,1)<<Meq.Parm(0,node_groups='Parm',solvable=1,table_name=mytable, use_previous=2, save_all=True, tiling=def_tiling)
    ns.J11(station,1)<<Meq.ToComplex(ns.Jreal11(station,1),ns.Jimag11(station,1))
    ns.Jreal12(station,1)<<Meq.Parm(0,node_groups='Parm',solvable=1,table_name=mytable, use_previous=2, save_all=True, tiling=def_tiling)
    ns.Jimag12(station,1)<<Meq.Parm(0,node_groups='Parm',solvable=1,table_name=mytable, use_previous=2, save_all=True, tiling=def_tiling)
    ns.J12(station,1)<<Meq.ToComplex(ns.Jreal12(station,1),ns.Jimag12(station,1))
    ns.Jreal22(station,1)<<Meq.Parm(1,node_groups='Parm',solvable=1,table_name=mytable, use_previous=2, save_all=True, tiling=def_tiling)
    ns.Jimag22(station,1)<<Meq.Parm(0,node_groups='Parm',solvable=1,table_name=mytable, use_previous=2, save_all=True, tiling=def_tiling)
    ns.J22(station,1)<<Meq.ToComplex(ns.Jreal22(station,1),ns.Jimag22(station,1))

    ns.Jreal21(station,1)<<Meq.Parm(0,node_groups='Parm',solvable=1,table_name=mytable, use_previous=2, save_all=True, tiling=def_tiling)
    ns.Jimag21(station,1)<<Meq.Parm(0,node_groups='Parm',solvable=1,table_name=mytable, use_previous=2, save_all=True, tiling=def_tiling)
    ns.J21(station,1)<<Meq.ToComplex(ns.Jreal21(station,1),ns.Jimag21(station,1))


    ns.G1(station)<<Meq.Matrix22(ns.J11(station,1), ns.J12(station,1), ns.J21(station,1), ns.J22(station,1))


  # create all-sky patch for source model
  allsky = Patch(ns,'all1',observation.phase_centre);
  allsky.add(*corrupt_list);
  allskyG1 = CorruptComponent(ns,allsky,label='G1',station_jones=ns.G1);




  # create simulated visibilities for sky
  predictG1 = allskyG1.visibilities(array,observation);
  

  # now create spigots, condeqs and residuals
  for sta1,sta2 in array.ifrs():
    spigot = ns.spigot(sta1,sta2) << Meq.Spigot( station_1_index=sta1-1,
                                                 station_2_index=sta2-1,
                                                 flag_bit=4,
                                                 input_col='DATA');
    pred = predictG0(sta1,sta2)+predictG1(sta1,sta2);
    ns.ce(sta1,sta2) << Meq.Condeq(spigot,pred);
    ns.residual(sta1,sta2) << spigot - predictG0(sta1,sta2)-predictG1(sta1,sta2)
    #ns.residual(sta1,sta2) << spigot -predictG1(sta1,sta2)


  # create MMSE equalizers
  #sigma2=1e-5; for band 4-5
  sigma2=1e-5;
  ns.I0<<Meq.Matrix22(sigma2,0,0,sigma2)
  # threshold for flagging - condition number
  fthreshold=3
  for station in array.stations():
    # get min value
    ns.Jmin(station)<<Meq.Min(Meq.Abs(ns.J11(station,0)+sigma2),Meq.Abs(ns.J22(station,0)+sigma2))
    ns.Jmax(station)<<Meq.Max(Meq.Abs(ns.J11(station,0)+sigma2),Meq.Abs(ns.J22(station,0)+sigma2))
    # catch to ignore division by zero
    ns.Jmin0(station)<<Meq.Max(ns.Jmin(station),1e-9)
    # condition number
    ns.Jcond(station)<<ns.Jmax(station)/ns.Jmin0(station)
    ns.Gc(station)<<ns.G0(station)+ns.I0
    # flag
    fc = ns.lim(station) << ns.Jcond(station) - fthreshold;
    ns.Gflagged(station) << Meq.MergeFlags(ns.Gc(station),Meq.ZeroFlagger(fc,flag_bit=2,oper="GE"))

  ## also correct the residual data by gain of Gc
  Jones.apply_correction(ns.corrected,ns.residual,ns.Gflagged,array.ifrs());

    

  ## attach a clipper too as final flagging step
  threshold_sigmas=5;
  ## also cutoff
  abs_cutoff=1e5
  for sta1,sta2 in array.ifrs():
    inp = ns.corrected(sta1,sta2);
    a = ns.flagged("abs",sta1,sta2) << Meq.Abs(inp);
    stddev_a = ns.flagged("stddev",sta1,sta2) << Meq.StdDev(a);
    delta = ns.flagged("delta",sta1,sta2) << Meq.Abs(a-Meq.Mean(a));
    fc = ns.flagged("fc",sta1,sta2) << delta - threshold_sigmas*stddev_a;
    inp=ns.flagged0(sta1,sta2) << Meq.MergeFlags(inp,Meq.ZeroFlagger(fc,flag_bit=2,oper="GE"))
    fc = ns.flagged("abscutoff",sta1,sta2) << a - abs_cutoff;
    ns.flagged(sta1,sta2) << Meq.MergeFlags(inp,Meq.ZeroFlagger(fc,flag_bit=2,oper="GE"));
 

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
    reqseq = Meq.ReqSeq(ns.solver,ns.flagged(sta1,sta2),
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
  
  
def create_solver_defaults(num_iter=10,epsilon=1e-4,convergence_quota=0.9,solvable=[]):
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
    rec.write_flags=True
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


ms_selection=record(channel_start_index=31,
          channel_end_index=39,
          channel_increment=1,
          ddid_index=1,
          selection_string='sumsqr(UVW[1:2]) > 100')


def _tdl_job_0_solve_for_GJones(mqs,parent,**kw):
  solvables = ['Jreal11:'+str(station)+':0' for station in range(1,num_stations+1)];
  solvables += ['Jimag11:'+str(station)+':0' for station in range(1,num_stations+1)];
  solvables += ['Jreal22:'+str(station)+':0' for station in range(1,num_stations+1)];
  solvables += ['Jimag22:'+str(station)+':0' for station in range(1,num_stations+1)];
  #solvables += ['Jreal12:'+str(station)+':0' for station in range(1,num_stations+1)];
  #solvables += ['Jimag12:'+str(station)+':0' for station in range(1,num_stations+1)];
  #solvables += ['Jreal21:'+str(station)+':0' for station in range(1,num_stations+1)];
  #solvables += ['Jimag21:'+str(station)+':0' for station in range(1,num_stations+1)];

  solvables += ['Jreal11:'+str(station)+':1' for station in range(1,num_stations+1)];
  solvables += ['Jimag11:'+str(station)+':1' for station in range(1,num_stations+1)];
  solvables += ['Jreal22:'+str(station)+':1' for station in range(1,num_stations+1)];
  solvables += ['Jimag22:'+str(station)+':1' for station in range(1,num_stations+1)];
  #solvables += ['Jreal12:'+str(station)+':1' for station in range(1,num_stations+1)];
  #solvables += ['Jimag12:'+str(station)+':1' for station in range(1,num_stations+1)];
  #solvables += ['Jreal21:'+str(station)+':1' for station in range(1,num_stations+1)];
  #solvables += ['Jimag21:'+str(station)+':1' for station in range(1,num_stations+1)];



  _run_solve_job(mqs,solvables,ms_selection,wait=False);

def _tdl_job_0_solve_for_GJoneBatch(mqs,parent,**kw):
  solvables = ['Jreal11:'+str(station)+':0' for station in range(1,num_stations+1)];
  solvables += ['Jimag11:'+str(station)+':0' for station in range(1,num_stations+1)];
  solvables += ['Jreal22:'+str(station)+':0' for station in range(1,num_stations+1)];
  solvables += ['Jimag22:'+str(station)+':0' for station in range(1,num_stations+1)];
  #solvables += ['Jreal12:'+str(station)+':0' for station in range(1,num_stations+1)];
  #solvables += ['Jimag12:'+str(station)+':0' for station in range(1,num_stations+1)];
  #solvables += ['Jreal21:'+str(station)+':0' for station in range(1,num_stations+1)];
  #solvables += ['Jimag21:'+str(station)+':0' for station in range(1,num_stations+1)];

  solvables += ['Jreal11:'+str(station)+':1' for station in range(1,num_stations+1)];
  solvables += ['Jimag11:'+str(station)+':1' for station in range(1,num_stations+1)];
  solvables += ['Jreal22:'+str(station)+':1' for station in range(1,num_stations+1)];
  solvables += ['Jimag22:'+str(station)+':1' for station in range(1,num_stations+1)];
  #solvables += ['Jreal12:'+str(station)+':1' for station in range(1,num_stations+1)];
  #solvables += ['Jimag12:'+str(station)+':1' for station in range(1,num_stations+1)];
  #solvables += ['Jreal21:'+str(station)+':1' for station in range(1,num_stations+1)];
  #solvables += ['Jimag21:'+str(station)+':1' for station in range(1,num_stations+1)];




  step=8;
  #for schan in range(31,223,step):
  #  ms_selection=record(channel_start_index=schan,
  #        channel_end_index=schan+step-1,
  #        channel_increment=1,
  #        ddid_index=0,
  #        selection_string='sumsqr(UVW[1:2]) > 100')
  #  #parmtablename="peelB4_"+str(schan)+"_.mep";
  #  parmtablename=None;
  #  # update parmtablename
  #  for sname in solvables:
  #     set_node_state(mqs,sname,record(table_name=parmtablename))
  #  _run_solve_job(mqs,solvables,ms_selection,wait=True);
  for schan in range(175,223,step):
    ms_selection=record(channel_start_index=schan,
          channel_end_index=schan+step-1,
          channel_increment=1,
          ddid_index=0,
          selection_string='sumsqr(UVW[1:2]) > 100')
    #parmtablename="peelB4_"+str(schan)+"_.mep";
    parmtablename=None;
    # update parmtablename
    for sname in solvables:
       set_node_state(mqs,sname,record(table_name=parmtablename))
    _run_solve_job(mqs,solvables,ms_selection,wait=True);




Settings.forest_state.cache_policy = 1  # -1 for minimal, 1 for smart caching, 100 for full caching
Settings.orphans_are_roots = True

if __name__ == '__main__':


    Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);


    ns.Resolve();
    pass
              
