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
  
  # create set of nodes to compute visibilities...
  predict = allsky.visibilities();
  
  # create resamplers
  for p,q in array.ifrs():
    modres = ns.modres(p,q) << Meq.ModRes(predict(p,q),upsample=[5,5]);
    ns.resampled(p,q) << Meq.Resampler(modres,mode=2);
    
  # make some useful inspectors. Collect them into a list, since we need
  # to give a list of 'post' nodes to make_sinks() below
  inspectors = [
    Meow.StdTrees.vis_inspector(ns.inspect_predict,ns.resampled)
  ];
    
  # make sinks and vdm. Note that we don't want to make any spigots...
  # The list of inspectors comes in handy here
  Meow.StdTrees.make_sinks(ns,ns.resampled,spigots=False,post=inspectors);
  
  # make a few more bookmarks
  pg = Meow.Bookmarks.Page("K Jones",2,2);
  for p in array.stations()[1:4]:      # use stations 1 through 4
    for src in sources:
      pg.add(src.direction.KJones()(p));
  

def _tdl_job_1_simulate_MS (mqs,parent):
  req = Meow.Utils.create_io_request();
  # execute    
  mqs.execute('VisDataMux',req,wait=False);
  




# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
