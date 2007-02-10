from Timba.TDL import *
from Timba.Meq import meq
from numarray import *
import os
import random

import Meow

import Meow.Bookmarks
import Meow.Utils
import Meow.StdTrees
import Meow.Context

def abs_clip (inputs,threshold):
  # flag condition is abs(x) >= threshold
  flagged = inputs("absclip");
  for p,q in Meow.Context.array.ifrs():
    inp = inputs(p,q);
    fc = flagged("fc",p,q) << Meq.Abs(inp) - threshold;
    flagged(p,q) << Meq.MergeFlags(inp,Meq.ZeroFlagger(fc,flag_bit=2,oper="GE"));
  return flagged;  

def rms_clip (inputs,threshold_sigmas):
  # flag condition is abs(x)-mean(abs(x)) >= flag_threshold*rms
  flagged = inputs("rmsclip");
  for p,q in Meow.Context.array.ifrs():
    inp = inputs(p,q);
    a = flagged("abs",p,q) << Meq.Abs(inp);
    stddev_a = flagged("stddev",p,q) << Meq.StdDev(a);
    delta = flagged("delta",p,q) << Meq.Abs(a-Meq.Mean(a));
    fc = flagged("fc",p,q) << delta - threshold_sigmas*stddev_a;
    flagged(p,q) << Meq.MergeFlags(inp,Meq.ZeroFlagger(fc,flag_bit=2,oper="GE"));
  return flagged;

TDLCompileOption('num_stations',"Number of stations",[14,3],more=int);
TDLCompileOption('clear_ms_flags',"Ignore MS flags",False);
TDLCompileOption('flag_abs',"Flag on absolute value >=",[None,1.,2.],more=float);
TDLCompileOption('flag_rms',"Flag on rms sigmas >= ",[None,3.,5.,10.],more=float);

def _define_forest(ns):
  # enable standard MS options from Meow
  Meow.Utils.include_ms_options(
    channels=[[15,40,1]],tile_sizes=[200,500],
    has_output=False,flags=True
  );

  # create array model
  array = Meow.IfrArray.WSRT(ns,num_stations);
  observation = Meow.Observation(ns);
  # setup Meow global context
  Meow.Context.set(array=array,observation=observation);
  
  # make spigots, but tell them to ignore MS flags or not via 'flag_bit'
  if clear_ms_flags:
    flag_mask = 0;
  else:
    flag_mask = -1;
  outputs = spigots = array.spigots(flag_mask=flag_mask);
  # make an inspector for spigots, we'll add more to this list
  inspectors = [
    Meow.StdTrees.vis_inspector(ns.inspect('spigots'),spigots,bookmark=False)
  ];
  
  # flag on absolute value first
  if flag_abs is not None:
    outputs = abs_clip(outputs,flag_abs);
    inspectors.append(Meow.StdTrees.vis_inspector(ns.inspect('abs'),outputs,bookmark=False));
    
  # then flag on rms
  if flag_rms is not None:
    outputs = rms_clip(outputs,flag_rms);
    inspectors.append(Meow.StdTrees.vis_inspector(ns.inspect('rms'),outputs,bookmark=False));

  # make sinks and vdm
  Meow.StdTrees.make_sinks(ns,outputs,post=inspectors);

  # put all inspectors into bookmarks  
  pg = Meow.Bookmarks.Page("Vis Inspectors",2,2);
  for node in inspectors:
    pg.add(node,viewer="Collections Plotter");
  

def _tdl_job_1_run_flagging (mqs,parent,**kw):
  req = Meow.Utils.create_io_request();
  mqs.execute('VisDataMux',req,wait=False);


Settings.forest_state.cache_policy = 1  # -1 for minimal, 1 for smart caching, 100 for full caching

if __name__ == '__main__':


    Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);


    ns.Resolve();
    pass
              
