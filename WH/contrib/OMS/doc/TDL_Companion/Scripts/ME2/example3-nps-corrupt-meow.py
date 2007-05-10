# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

import Meow
import Meow.StdTrees

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[16,32,48,96]);
TDLRuntimeMenu("Imaging options",
    *Meow.Utils.imaging_options(npix=256,arcmin=4,channels=[[32,1,1]]));

# useful constant: 1 deg in radians
DEG = math.pi/180.;
ARCMIN = DEG/60;

# source flux (same for all sources)
I = 1; Q = .2; U = .2; V = .2;

# we'll put the sources on a grid (positions in arc min)
LM = [(-1,-1),(-1,0),(-1,1),
      ( 0,-1),( 0,0),( 0,1), 
      ( 1,-1),( 1,0),( 1,1)];

def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray.VLA(ns);
  # create an Observation object
  observation = Meow.Observation(ns);
  # set global context
  Meow.Context.set(array=array,observation=observation);
  
  sources = [];
  # create 10 sources
  for isrc in range(len(LM)):
    l,m = LM[isrc];
    l *= ARCMIN;
    m *= ARCMIN;
    # generate an ID for direction and source
    srcname = 'S'+str(isrc);           
    # create Direction object
    src_dir = Meow.LMDirection(ns,srcname,l,m);
    # create point source with this direction
    source = Meow.PointSource(ns,srcname,src_dir,I=I,Q=Q,U=U,V=V);
    # create beam gain Jones for source
    ns.E(srcname) << Meq.Pow(Meq.Cos(math.sqrt(l*l+m*m)*2e-6*Meq.Freq()),3)
    # create corrupted source
    corrupted_source = source.corrupt(ns.E(srcname),per_station=False);
    sources.append(corrupted_source);

  # add all corrupted sources to patch
  allsky = Meow.Patch(ns,'all',observation.phase_centre);
  allsky.add(*sources);
  
  # create G terms 
  for p in array.stations():
    ns.G(p) << 1;   # trivial G term for now
  # and corrupt patch with the G term
  corrupt_sky = Meow.CorruptComponent(ns,allsky,'G',station_jones=ns.G);  
  
  # create set of nodes to compute visibilities...
  predict = corrupt_sky.visibilities();

  # make some useful inspectors. Collect them into a list, since we need
  # to give a list of 'post' nodes to make_sinks() below
  inspectors = [];
  inspectors.append(
    Meow.StdTrees.vis_inspector(ns.inspect_predict,predict) );
  for i in [0,1,4,5]:
    inspectors.append( 
      Meow.StdTrees.vis_inspector(ns.inspect_predict(i),sources[i].visibilities(),bookmark=False) );
    
  # make sinks and vdm. Note that we don't want to make any spigots...
  # The list of inspectors comes in handy here
  Meow.StdTrees.make_sinks(ns,predict,spigots=False,post=inspectors);
  
  # make some bookmarks. Note that inspect_predict gets its own bookmark
  # automatically; for the others we said bookmark=False because we
  # want to put them onto a single page
  pg = Meow.Bookmarks.Page("Inspectors",2,2);
  for i in [0,1,4,5]:
    pg.add(ns.inspect_predict(i),viewer="Collections Plotter");
    
  # make a few more bookmarks
  pg = Meow.Bookmarks.Page("K Jones",2,2);
  for p in array.stations()[1:4]:      # use stations 1 through 3
    for src in sources[:4]:            # use sources 0 through 3
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
