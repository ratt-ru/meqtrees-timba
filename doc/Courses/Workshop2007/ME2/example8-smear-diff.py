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

  # create two Patches and two sets of sources
  # for the entire observed sky -- one will be computed via a resampler, the other one directly
  sources1 = sky_models.make_model(ns,"R");
  sources2 = sky_models.make_model(ns,"S");
    
  # create two Patches for the entire observed sky -- one
  allsky1 = Meow.Patch(ns,'all',observation.phase_centre);
  allsky2 = Meow.Patch(ns,'all0',observation.phase_centre);
  allsky1.add(*sources1);
  allsky2.add(*sources2);
    
  # create set of nodes to compute visibilities...
  predict1 = allsky1.visibilities();
  predict2 = allsky2.visibilities();
  
  # ...and attach them to resamplers and sinks
  for p,q in array.ifrs():
    modres = ns.modres(p,q) << Meq.ModRes(predict1(p,q),upsample=[5,5]);
    resamp = ns.resampled(p,q) << Meq.Resampler(modres,mode=2);
    ns.diff(p,q) << resamp - predict2(p,q);

  # make some useful inspectors. Collect them into a list, since we need
  # to give a list of 'post' nodes to make_sinks() below
  inspectors = [
    Meow.StdTrees.vis_inspector(ns.inspect_resampled,ns.resampled,bookmark=False),
    Meow.StdTrees.vis_inspector(ns.inspect_orig,predict2,bookmark=False)
  ];
    
  # make sinks and vdm. Note that we don't want to make any spigots...
  # The list of inspectors comes in handy here
  Meow.StdTrees.make_sinks(ns,ns.diff,spigots=False,post=inspectors);
  
  # make a few more bookmarks
  Meow.Bookmarks.Page("Inspectors",1,2) \
    .add(ns.inspect_resampled,viewer="Collections Plotter") \
    .add(ns.inspect_orig,viewer="Collections Plotter");
  
  pg = Meow.Bookmarks.Page("K Jones, source 0",2,2);
  for p in array.stations()[1:3]:      # use stations 1,2
    pg.add(sources1[0].direction.KJones()(p));
    pg.add(sources2[0].direction.KJones()(p));
  

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
