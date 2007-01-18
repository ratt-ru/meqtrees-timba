from Timba.TDL import *
from Timba.Meq import meq
from numarray import *
import os
import random

import Meow

from Meow import Bookmarks
from Meow import Utils

# number of stations
TDLCompileOption('num_stations',"Number of stations",[14,3],more=int);

def _define_forest(ns):
  # enable standard MS options from Meow
  Utils.include_ms_options(
    channels=[[15,40,1]],
    has_output=False,
  );

  array = Meow.IfrArray.WSRT(ns,num_stations);
  observation = Meow.Observation(ns);
  
  spigot = array.spigots();
  ns.inspector << \
      Meq.Composer(
        dims=(len(array.ifrs()),2,2),
#        plot_label=[ "%s-%s"%(p,q) for p,q in array.ifrs() ],
        *[ ns.inspector(p,q) << Meq.Mean(spigot(p,q),reduction_axes="freq")
          for p,q in array.ifrs() ]
      );
  
  vdm = ns.VisDataMux << Meq.VisDataMux(post=ns.inspector);
  vdm.add_stepchildren(*[spigot(p,q) for p,q in array.ifrs()]);
  

def _test_forest (mqs,parent,**kw):
  req = Meow.Utils.create_io_request();
  mqs.execute('VisDataMux',req,wait=False);


Settings.forest_state = record(bookmarks=[
  record(name="Output inspector",viewer="Collections Plotter",udi="/node/inspector")
]);


Settings.forest_state.cache_policy = 1  # -1 for minimal, 1 for smart caching, 100 for full caching
Settings.orphans_are_roots = True

if __name__ == '__main__':


    Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);


    ns.Resolve();
    pass
              
