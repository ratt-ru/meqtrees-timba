# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

import Meow
import Meow.StdTrees
import clar_model

# mode options
TDLCompileOption("grid_size","Grid size",[1,3,5,7]);
TDLCompileOption("grid_step","Grid step, in arcmin",[.1,.5,1,2,5,10,15,20,30]);

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[8,16,32,48,96]);
# note how we set default image size based on grid size/step
TDLRuntimeMenu("Imaging options",
    *Meow.Utils.imaging_options(npix=512,arcmin=grid_size*grid_step,channels=[[32,1,1]]));


DEG = math.pi/180.;
ARCMIN = DEG/60;

def point_source (ns,name,l,m):
  srcdir = Meow.LMDirection(ns,name,l,m);
  return Meow.PointSource(ns,name,srcdir,I=1);
  
def star8_model (ns,basename,l0,m0,dl,dm,nsrc):
  # Returns sources arranged in an 8-armed star
  model = [ point_source(ns,basename+"+0+0",l0,m0) ];
  for n in range(1,nsrc+1):
    for dx in (-n,0,n):
      for dy in (-n,0,n):
        if dx or dy:
          name = "%s%+d%+d" % (basename,dx,dy);
          model.append(point_source(ns,name,l0+dl*dx,m0+dm*dy));
  return model;
  
def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray.VLA(ns);
  # create an Observation object
  observation = Meow.Observation(ns);
  # set global context
  Meow.Context.set(array=array,observation=observation);
    
  # create a Patch for the "precise" sim
  allsky = Meow.Patch(ns,'all',observation.phase_centre);
  # and for the for the "average" sim
  avgsky = Meow.Patch(ns,'avg',observation.phase_centre);
  
  # create a source model
  source_list = star8_model(ns,'S0',0,0,grid_step*ARCMIN,grid_step*ARCMIN,(grid_size-1)/2);

  # create CLAR EJones terms
  Ej = clar_model.EJones(ns,array,observation,source_list);
  
  for src in source_list:
    dirname = src.direction.name;
    # corrupt source by its own E and add to 'allsky' patch
    corrupt_src = src.corrupt(Ej(dirname));
    allsky.add(corrupt_src);
    
    # compute source by the average E and add to 'avgsky' patch
    Eavg = ns.Eavg(src.direction.name) << Meq.Mean(*[Ej(dirname,sta) for sta in array.stations()]);
    corrupt_src = src.corrupt(Eavg,per_station=False);
    avgsky.add(corrupt_src);
    
  # create set of nodes to compute visibilities and deltas
  predict1 = allsky.visibilities();
  predict2 = avgsky.visibilities();

  for p,q in array.ifrs():
    ns.diff(p,q) << predict1(p,q) - predict2(p,q);

  # make some useful inspectors. Collect them into a list, since we need
  # to give a list of 'post' nodes to make_sinks() below
  inspectors = [
    Meow.StdTrees.vis_inspector(ns.inspect_diff,ns.diff),
  ];

  # make sinks and vdm. Note that we don't want to make any spigots...
  # The list of inspectors comes in handy here
  Meow.StdTrees.make_sinks(ns,ns.diff,spigots=False,post=inspectors);
  
  

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
