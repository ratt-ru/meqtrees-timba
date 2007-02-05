from Timba.TDL import *

import Meow
import Meow.StdTrees
from Meow import Utils

# number of stations
TDLCompileOption('num_stations',"Number of stations",[14,3],more=int);

def _define_forest(ns):
  # enable standard MS options from Meow
  Utils.include_ms_options(
    channels=[[15,40,1]],tile_sizes=[100],
    has_output=False,
  );

  array = Meow.IfrArray.WSRT(ns,num_stations);
  observation = Meow.Observation(ns);
  Meow.Context.set(array,observation);
  
  spigots = array.spigots();

  inspectors = [
    Meow.StdTrees.vis_inspector(ns.inspect_spigots,spigots)
  ];
  
  # make sinks and vdm
  Meow.StdTrees.make_sinks(ns,spigots,post=inspectors);
  

def _tdl_job_view_MS (mqs,parent,**kw):
  req = Meow.Utils.create_io_request();
  mqs.execute('VisDataMux',req,wait=False);





Settings.forest_state.cache_policy = 1  # -1 for minimal, 1 for smart caching, 100 for full caching
Settings.orphans_are_roots = True

if __name__ == '__main__':


    Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);


    ns.Resolve();
    pass
              
