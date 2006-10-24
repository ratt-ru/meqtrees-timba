# ../contrib/JEN/peeling/peeling.py
# copied from Day3/demo3_...

# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

import Meow

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[30,48,96]);
Meow.Utils.include_imaging_options();

# define antenna list
ANTENNAS = range(1,28);

# useful constant: 1 deg in radians
DEG = math.pi/180.;
ARCMIN = DEG/60;

# source flux (same for all sources)
I = 1; Q = .2; U = .2; V = .2;

# we'll put the sources on a grid (positions in arc min)
a = 1.0
if True:
  # LM = [(0,0)]
  LM = [(0,0),(a,a)]
else:
  LM = [(-a,-a),(-a,0),(-a,a),
        ( 0,-a),( 0,0),( 0,a), 
        ( a,-a),( a,0),( a,a)];

def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray(ns,ANTENNAS);
  # create an Observation object
  observation = Meow.Observation(ns);
  
  # create a Patch for the entire observed sky
  allsky = Meow.Patch(ns,'all',observation.phase_centre);

  # create 10 sources
  I = 1.0
  corrupt = []
  for isrc in range(len(LM)):
    l,m = LM[isrc];
    l *= ARCMIN;
    m *= ARCMIN;
    # generate an ID for direction and source
    src = 'S'+str(isrc);           
    # create Direction object
    src_dir = Meow.LMDirection(ns,src,l,m);
    # create point source with this direction
    source = Meow.PointSource(ns,src,src_dir,I=I,Q=Q,U=U,V=V);
    # create beam gain Jones for source
    # ns.E(src) << Meq.Pow(Meq.Cos(math.sqrt(l*l+m*m)*1.5e-6*Meq.Freq()),6)
    for p in ANTENNAS:
      # ns.G(src)(p) << 1;
      ns.G(src)(p) << Meq.Matrix22(1+0j,0,0,1+0j);
    # create corrupted source
    # corrupt = Meow.CorruptComponent(ns,source,'E',jones=ns.E(src));
      corrupt.append(Meow.CorruptComponent(ns,source,'G',station_jones=ns.G(src)));
    # add to patch
    allsky.add(source);
    # The next source has half the flux:
    I *= 0.5

  # Make sequence of peeling stages:
  data = allsky.visibilities(array,observation);
  resid = []
  for ifr in array.ifrs():
    resid.append(data(*ifr))
  for isrc in range(len(LM)):
    src = 'S'+str(isrc);           
    predict = corrupt[isrc].visibilities(array,observation);       # Does NOT refresh!!
    i = 0
    for ifr in array.ifrs():
      resid[i] = ns.residual(*ifr)(src) << Meq.Subtract(resid[i],predict(*ifr));
      i += 1

  # ...and attach them to sinks
  i = 0
  for p,q in array.ifrs():
    ns.sink(p,q) << Meq.Sink(resid[i],station_1_index=p-1,station_2_index=q-1,output_col='DATA');
    i += 1

  # define VisDataMux
  ns.vdm << Meq.VisDataMux(*[ns.sink(p,q) for p,q in array.ifrs()]);
  

def _tdl_job_1_simulate_MS (mqs,parent):
  req = Meow.Utils.create_io_request();
  # execute    
  mqs.execute('vdm',req,wait=False);
  
  
def _tdl_job_2_make_image (mqs,parent):
  Meow.Utils.make_dirty_image(npix=256,cellsize='1arcsec',channels=[32,1,1]);



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
