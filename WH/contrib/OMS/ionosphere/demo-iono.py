# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

import Meow
import iono_model
import sky_models

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[1,2,5,30,48,96]);
Meow.Utils.include_imaging_options();

TDLCompileOption("sky_model","Sky model",
            [sky_models.Grid9,
             sky_models.PerleyGates,
             sky_models.PerleyGates_ps]);
TDLCompileOption("grid_stepping","Grid step, in minutes",[1,5,10,30,60,120,240]);
TDLCompileOption("apply_iono","Apply ionospheric corruption",False);

# define antenna list
ANTENNAS = range(1,28);

# useful constant: 1 deg in radians
DEG = math.pi/180.;
ARCMIN = DEG/60;

# source flux (same for all sources)
I = 1; Q = .2; U = .2; V = .2;

# we'll put the sources on a grid (positions in arc min)
#LM = [(0,0)];
LM = [(-1.1,-1.03),(-1,0.05),(-1.2,1.07),
     ( 0.01,-.9),( 0,0),( 0.05,.93), 
     ( .97,-.96),( 1.04,0.0399999991011),( 1.001,.999997)];

def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray(ns,ANTENNAS);
  # create an Observation object
  observation = Meow.Observation(ns);
  
  # create a Patch for the entire observed sky
  allsky = Meow.Patch(ns,'all',observation.phase_centre);

  # create sources
  sources = [];
  global maxrad;
  maxrad = 0;
  for i,srctuple in enumerate(sky_model()):  # sky_model comes from GUI option
    l = srctuple[0]*grid_stepping; 
    m = srctuple[1]*grid_stepping;
    # figure out max image radius in arcmin
    maxrad = max(abs(l)+.5,abs(m)+.5,maxrad);
    # convert to radians
    l *= ARCMIN;
    m *= ARCMIN;
    # generate an ID for direction and source
    src = 'S'+str(i);
    # create Direction object
    src_dir = Meow.LMDirection(ns,src,l,m);
    # create source with this direction, depending on tuple type
    if len(srctuple) == 2:
      sources.append(Meow.PointSource(ns,src,src_dir,I=I,Q=Q,U=U,V=V));
    else:
      l,m,iflux,sx,sy,pa = srctuple;
      sources.append(Meow.GaussianSource(ns,src,src_dir,I=iflux,
                                         size=[sx*ARCMIN,sy*ARCMIN],phi=pa));
                                         
  if apply_iono:
   zetas = iono_model.compute_zeta_jones(ns,sources,array,observation);
   for src in sources:
     # create corrupted source
     corrupt = Meow.CorruptComponent(ns,src,'Z',station_jones=zetas(src.name));
     # add to patch
     allsky.add(corrupt);
  # no corruption, just take all the sources directly
  else:
    allsky.add(*sources);

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
  imsize_pixels = 1024;
  imsize_seconds = maxrad*2*60;
  cellsize = str(imsize_seconds/imsize_pixels)+'arcsec';
  Meow.Utils.make_dirty_image(npix=imsize_pixels,cellsize=cellsize,channels=[32,1,1]);



# setup a few bookmarks
Settings.forest_state = record(bookmarks=[
  Meow.Bookmarks.PlotPage("TECS",["tec:S0:1","tec:S0:9"],["tec:S1:1","solver"]),
  Meow.Bookmarks.PlotPage("Z Jones",["Z:S0:1","Z:S0:9"],["Z:S8:1","Z:S8:9"])
]);


# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
