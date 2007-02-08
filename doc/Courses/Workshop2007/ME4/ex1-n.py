# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

import Meow
import Meow.StdTrees

import sky_models

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[16,32,48,96]);
TDLRuntimeMenu("Imaging options",
    *Meow.Utils.imaging_options(npix=256,arcmin=sky_models.imagesize(),channels=[[32,1,1]]));


# define antenna list
ANTENNAS = range(1,28);

def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray.VLA(ns);
  # create an Observation object
  observation = Meow.Observation(ns);
  # set global context
  Meow.Context.set(array=array,observation=observation);

  sources = sky_models.make_model(ns,"S");
    
  # create a Patch for the entire observed sky
  allsky = Meow.Patch(ns,'all',observation.phase_centre);
  allsky.add(*sources);
  
  nsky = Meow.Patch(ns,'naughty',observation.phase_centre);
  
  for p in array.stations():
    ns.w(p) << Meq.Selector(array.uvw(observation.phase_centre)(p),index=2);
  
  for src in sources:
    n1 = 2*math.pi*(src.direction.n()-1);
    for p in array.stations():
      ns.N(src.name,p) << Meq.Polar(1.,n1*ns.w(p));
    nsky.add(src.corrupt(ns.N(src.name)));
  
  # create set of nodes to compute visibilities...
  predict1 = allsky.visibilities();
  predict2 = nsky.visibilities();
  
  for p,q in array.ifrs():
    ns.diff(p,q) << predict1(p,q) - predict2(p,q);
    
  # make some useful inspectors. Collect them into a list, since we need
  # to give a list of 'post' nodes to make_sinks() below
  inspectors = [
    Meow.StdTrees.vis_inspector(ns.inspect_predict,ns.diff)
  ];
    
  # make sinks and vdm. Note that we don't want to make any spigots...
  # The list of inspectors comes in handy here
  Meow.StdTrees.make_sinks(ns,ns.diff,spigots=False,post=inspectors);
  
  # make a few more bookmarks
  pg = Meow.Bookmarks.Page("K Jones",2,2);
  for p in array.stations()[1:4]:      # use stations 1 through 4
    for src in sources:
      pg.add(src.direction.KJones()(p));
  

def _tdl_job_1_simulate_MS (mqs,parent):
  req = Meow.Utils.create_io_request();
  # execute    
  mqs.execute('VisDataMux',req,wait=False);
  
  


# setup a few bookmarks
Settings.forest_state = record(bookmarks=[
  Meow.Bookmarks.PlotPage("K Jones",["K:S0:1","K:S0:9"],["K:S1:2","K:S1:9"])
]);



# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
