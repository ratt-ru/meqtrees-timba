#!/usr/bin/python
# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
from Timba import pynode
from Timba.TDL import *
from Timba.Meq import meq
from Timba import mequtils
from Timba import dmi
from Timba.dmi import *

import read_gps
import MyPyNodes
import Meow
from Meow import Bookmarks
from Meow import Utils
import Meow.StdTrees

TDLCompileOption('mim_rank',"Rank of MIM",[1,2,3],more=int);
TDLCompileOption('sat_start',"start number for satellites(min=1)",[1,2,3],more=int);
TDLCompileOption('sat_end',"end number for satellites (max =150)",[2,3,150],more=int);
TDLCompileOption('stat_start',"start number for stations (min=1)",[1,2,3],more=int);
TDLCompileOption('stat_end',"end number for stations (max =72)",[2,3,72],more=int);
TDLCompileOption('g_tiling',"time solution subtiling",[None,1,2,5],more=int);
TDLCompileOption('rank_time',"time solution rank",[1,2,5],more=int);
TDLCompileOption('solve_h',"solve h",True);
TDLCompileOption('solve_offs',"solve bias",True);

Settings.forest_state.cache_policy = 1  # -1 for minimal, 1 for smart caching, 100 for full caching

def _define_forest(ns,**kwargs):
  """define_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, this method is automatically called to
  define the forest. The 'ns' argument is a NodeScope object in which
  the forest is to be defined, usually this is simply the global scope.
  """;
  tot_stat_list = ['azu1', 'bgis', 'bkms', 'bran', 'btdm', 'cbhs', 'ccco', 'cgdm', 'chil', 'cit1', 'clar', 'cmp9', 'crhs', 'csdh', 'csn1', 'cvhs', 'dam2', 'dam3', 'dshs', 'dvpb', 'dyhs', 'elsc', 'fxhs', 'gvrs', 'hbco', 'hol3', 'holp', 'jplm', 'lapc', 'lasc', 'lbc1', 'lbc2', 'lbch', 'leep', 'lfrs', 'long', 'lors','mhms', 'mrdm', 'mta1', 'nopk', 'oxyc', 'pbpp', 'pkrd', 'pmhs', 'psdm', 'pve3', 'pvhs', 'pvrs', 'rhcl', 'sgdm', 'sghs', 'silk', 'skyb', 'spk1', 'spms', 'torp', 'twms', 'uclp', 'usc1', 'vdcy', 'vimt', 'vncx', 'vnps', 'vtis', 'vyas', 'wchs', 'whc1', 'wlsn', 'wmap', 'wnra', 'wrhs'];
  sat_list = range(sat_start-1,sat_end);
  stat_list = tot_stat_list[stat_start-1:stat_end];
  TEC_UNIT = 1./1e16;

  print sat_list,stat_list;

  #create source model
  h = ns.h << Meq.Parm(300000.,table_name="mim.mep",save_all=True);  #parameter h
  rot_matrix = read_gps.create_ref_stat_pos(ns,stat_list);
  bias_solvables = []; #add to solvables
  for sat in sat_list:
    xyz = ns.pos(sat) << Meq.MatrixMultiply(rot_matrix,Meq.PyNode(class_name="PyNodeSatPos",module_name='MyPyNodes',sat_nr=sat));
##    y = ns.pos('y',sat) << Meq.PyNode(class_name="PyNodeSatPos",module_name='MyPyNodes',sat_nr=sat,coord_index=1);
##    z = ns.pos('z',sat) << Meq.PyNode(class_name="PyNodeSatPos",module_name='MyPyNodes',sat_nr=sat,coord_index=2);
##    xyz = ns.pos(sat) << Meq.Composer(x,y,z);
    for stat in stat_list:
      offs = ns.offset(stat) << Meq.Parm(0.,table_name="mim.mep",save_all=True);
      ns.tec(sat,stat) << Meq.PyNode(class_name="PyNodeTec",module_name='MyPyNodes',sat_nr=sat,station = stat)*TEC_UNIT +offs;
      bias_solvables.append(offs);
  read_gps.create_long_lat(ns,stat_list,sat_list,ns.pos,h);
  mimpar=[];
  #MIM  parameters
  solvables = [];
  for xi in range(mim_rank):
    mimpar.append([]);
    for yi in range(mim_rank):
      if xi +yi >= mim_rank:
        continue;
      mimpar[xi].append(0)
      mimpar[xi][yi]= ns.p(xi,yi)<<Meq.Parm(0,shape=[rank_time],save_all=True,tiling =record(time = g_tiling),table_name="mim.mep");
      solvables.append(mimpar[xi][yi]);
      # get_mim
  cdqs=();
  for sat in sat_list:
    for stat in stat_list:
      x = ns.lon(sat,stat);
      y = ns.lat(sat,stat);
      mim =0;
      for xi in range(mim_rank-1,-1,-1):
        if mim!=0:
          mim = ns.mim(sat,stat,xi)<<mim *x;
        smim=0;
        for yi in range(mim_rank-1,0,-1):
          if xi +yi >= mim_rank:
            smim = 0 ;
            continue ;
          if smim !=0:
            smim =  smim + mimpar[xi][yi];
          else:
            smim  = mimpar[xi][yi];
          smim =  ns.mim(sat,stat,xi,yi)<<smim * y;
          
        if smim !=0:
          smim =  smim + mimpar[xi][0];
        else:
          smim  = mimpar[xi][0];
        if mim !=0:
          mim = mim +smim;
        else:
          mim =smim;

      #mim = ns.mim(sat,stat) << mim;
      condeq = ns.condeq(sat,stat) << Meq.Condeq(mim,ns.tec(sat,stat));
      cdqs = cdqs + (condeq,);

  
  TDLRuntimeMenu("Solve Mim",
                 TDLOption('nr_times',"nr timeslots",[1,2,60,24*60],more=int),
                 TDLJob(job_test_mim,"Go")
                 );
  if solve_h:
    solvables.append(h);
  if solve_offs:
    solvables = solvables +bias_solvables;
  solver = ns.solver<< Meq.Solver(children = cdqs,
                                  solvable = solvables,
                                  num_iter = 10,       #max number of iterations
                                  epsilon = 1e-4       #convergence limit, good default
                                  );

  # create some visualizers
  ns.inspect('condeqs')<<Meq.Composer(children = cdqs,plot_label=[ node.name for node in cdqs ]);
  ns.inspect('solvables')<<Meq.Composer(children = [node for node in solvables],
                                        plot_label=[ node.name for node in solvables ]);
    
  
  reqseq = ns.reqseq<<Meq.ReqSeq(solver, ns.inspect('condeqs'), ns.inspect('solvables'));

def job_test_mim (mqs,parent,**kwargs):
  """test_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, and the "test" option is set to true,
  this method is automatically called after define_forest() to run a
  test on the forest. The 'mqs' argument is a meqserver proxy object.
  """;
  from Timba.Meq import meq
  # run tests on the forest
  #nr_times = 24*60*2;
 # nr_times = 24*60*2;
  #nr_times = 60*2;
  dom = meq.domain(0,3,-15,nr_times*30-15);
  cells = meq.cells(dom,num_freq=6,num_time=nr_times);
  request = meq.request(cells,rqtype='ev');
  a = mqs.meq('Node.Execute',record(name='reqseq',request=request),wait=False);
  #a = mqs.meq('Node.Execute',record(name='tec:5:bgis',request=request),wait=False);
