# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

import Meow
import iono_model

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[30,48,96]);
Meow.Utils.include_imaging_options();

TDLCompileOption("grid_stepping","Grid step, in minutes",[10,30,60,120,240]);

# define antenna list
ANTENNAS = range(1,28);

# useful constant: 1 deg in radians
DEG = math.pi/180.;
ARCMIN = DEG/60;

# source flux (same for all sources)
I = 1; Q = .2; U = .2; V = .2;

# we'll put the sources on a grid (positions in arc min)
#LM = [(0,0)];
LM = [(-1,-1),(-1,0),(-1,1),
     ( 0,-1),( 0,0),( 0,1), 
     ( 1,-1),( 1,0),( 1,1)];

def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray(ns,ANTENNAS);
  # create an Observation object
  observation = Meow.Observation(ns);
  
  # create a Patch for the entire observed sky
  allsky = Meow.Patch(ns,'all',observation.phase_centre);

  sources = [];
  # create 10 sources
  for isrc in range(len(LM)):
    l,m = LM[isrc];
    l *= ARCMIN*grid_stepping;
    m *= ARCMIN*grid_stepping;
    # generate an ID for direction and source
    src = 'S'+str(isrc);           
    # create Direction object
    src_dir = Meow.LMDirection(ns,src,l,m);
    # create point source with this direction
    sources.append(Meow.PointSource(ns,src,src_dir,I=I,Q=Q,U=U,V=V));

  zetas = iono_model.compute_zeta_jones(ns,sources,array,observation);
  
  for src in sources:
    # create corrupted source
    corrupt = Meow.CorruptComponent(ns,src,'Z',station_jones=zetas(src.name));
    # add to patch
    allsky.add(corrupt);
  
  # create set of nodes to compute visibilities...
  predict = allsky.visibilities(array,observation);

  # ...and attach them to sinks
  for p,q in array.ifrs():
    ns.sink(p,q) << Meq.Sink(predict(p,q),station_1_index=p-1,station_2_index=q-1,output_col='DATA');

  # define'1arcsec' VisDataMux
  ns.vdm << Meq.VisDataMux(*[ns.sink(p,q) for p,q in array.ifrs()]);
  

def _tdl_job_1_simulate_MS (mqs,parent):
  req = Meow.Utils.create_io_request();
  # execute    
  mqs.execute('vdm',req,wait=False);
  
  
def _tdl_job_2_make_image (mqs,parent):
  imsize_pixels = 512;
  imsize_seconds = grid_stepping*2.5*60;
  cellsize = str(imsize_seconds/imsize_pixels)+'arcsec';
  Meow.Utils.make_dirty_image(npix=imsize_pixels,cellsize=cellsize,channels=[32,1,1]);



# setup a few bookmarks
Settings.forest_state = record(bookmarks=[
  Meow.Bookmarks.PlotPage("K Jones",["K:S0:1","K:S0:9"],["K:S1:2","K:S1:9"]),
  Meow.Bookmarks.PlotPage("E Jones",["E:S0","E:S1"],["E:S3","E:S4"]),
  Meow.Bookmarks.PlotPage("G Jones",["G:1","G:2"],["G:3","G:3"])
]);


# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
