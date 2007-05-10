# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

import Meow
import Meow.StdTrees

TDLCompileOption('grid_step',"Grid stepping (in arcmin)",[1,2,10,60],more=float);

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[16,32,48,96]);
TDLRuntimeMenu("Imaging options",
    *Meow.Utils.imaging_options(npix=256,arcmin=grid_step*5));

from NaughtyDirection import NaughtyDirection

# define antenna list
ANTENNAS = range(1,28);

# useful constant: 1 deg in radians
DEG = math.pi/180.;
ARCMIN = DEG/60;

# source flux (same for all sources)
I = 1; Q = 0; U = 0; V = .0;

def point_source (ns,name,l,m):
  srcdir = Meow.LMDirection(ns,name,l,m);
  return Meow.PointSource(ns,name,srcdir,I=1);

def naughty_source (ns,name,l,m):
  srcdir = NaughtyDirection(ns,name,l,m);
  return Meow.PointSource(ns,name,srcdir,I=1);
  
def cross_model (ns,basename,l0,m0,dl,dm,nsrc,kind=point_source):
  model = [ point_source(ns,basename+"+0+0",l0,m0) ];
  for n in range(1,nsrc+1):
    for dx,dy in ((n,0),(-n,0),(0,n),(0,-n)):
      name = "%s%+d%+d" % (basename,dx,dy);
      model.append(kind(ns,name,l0+dl*dx,m0+dm*dy));
  return model;

def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray.VLA(ns);
  # create an Observation object
  observation = Meow.Observation(ns);
  # set global context
  Meow.Context.set(array=array,observation=observation);
  
  # create a Patch for the entire observed sky
  allsky = Meow.Patch(ns,'all',observation.phase_centre);
  allsky1 = Meow.Patch(ns,'naughty',observation.phase_centre);

  # create "cross" of point sources
  ps_list = cross_model(ns,"S",0,0,grid_step*ARCMIN,grid_step*ARCMIN,2,kind=point_source);
  
  # create same "cross" of naughty sources
  ns_list = cross_model(ns,"N",0,0,grid_step*ARCMIN,grid_step*ARCMIN,2,kind=naughty_source);

  allsky.add(*ps_list);
  allsky1.add(*ns_list);

  # create set of nodes to compute visibilities...
  predict = allsky.visibilities();
  predict1 = allsky1.visibilities();
  
  # ...and attach them to resamplers and sinks
  for p,q in array.ifrs():
    ns.diff(p,q) << predict(p,q)-predict1(p,q);

  # make sinks and vdm. Note that we don't want to make any spigots...
  # The list of inspectors comes in handy here
  Meow.StdTrees.make_sinks(ns,ns.diff,spigots=False);
  

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
