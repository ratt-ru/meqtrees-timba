# ../contrib/JEN/peeling/peeling.py
# copied from Day3/demo3_...

# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

from Timba.Contrib.JEN.util import JEN_bookmarks

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
I = 1; Q = .2; U = .1; V = -0.02;

# we'll put the sources on a grid (positions in arc min)
a = 1.0
if True:
  # LM = [(0,0)]
  LM = [(0,0),(a,a),(0,1)]
else:
  LM = [(-a,-a),(-a,0),(-a,a),
        ( 0,-a),( 0,0),( 0,a), 
        ( a,-a),( a,0),( a,a)];


#===================================================================
#===================================================================

def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray(ns,ANTENNAS);
  # create an Observation object
  observation = Meow.Observation(ns);
  
  # create a Patch for the entire observed sky
  allsky = Meow.Patch(ns,'all',observation.phase_centre);

  # create 10 sources
  corrupt = []
  I = 1.0                                         # needed...?
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
    # create position-dependent 'beam' gain Jones for source
    # ns.E(src) << Meq.Pow(Meq.Cos(math.sqrt(l*l+m*m)*1.5e-6*Meq.Freq()),6)
    for p in ANTENNAS:
      # ns.E(src)(p) << 1;
      ns.E(src)(p) << Meq.Matrix22(1+0j,0,0,1+0j);
    # create corrupted source
    # corrupt = Meow.CorruptComponent(ns,source,'E',jones=ns.E(src));
    corrupt.append(Meow.CorruptComponent(ns,source,'E',station_jones=ns.E(src)));
    # add to patch
    allsky.add(source);
    # The next source has half the flux:
    I *= 0.5
    

  # Make sequence of peeling stages: 
  cohset = allsky.visibilities(array,observation);
  ifr1 = (1,12)                                   # select an ifr for bookmark
  cc = [cohset(*ifr1)]                             # start bookmark list
  for isrc in range(len(LM)):
    src = 'S'+str(isrc);           
    predict = corrupt[isrc].visibilities(array,observation);
    for ifr in array.ifrs():
      ns.residual(src)(*ifr) << Meq.Subtract(cohset(*ifr),predict(*ifr));
    cohset = ns.residual(src)

    # Optional: insert a reqseq for a solver:
    if True:
      ns.solver(src) << Meq.Solver(children=condeqs,child_poll_order=cpo);
      # ns.solver(src) << Meq.Add(*[predict(*ifr) for ifr in array.ifrs()]);
      for ifr in array.ifrs():
        ns.reqseq(src)(*ifr) << Meq.ReqSeq(ns.solver(src),cohset(*ifr),
                                           result_index=1,cache_num_active_parents=1);
      cohset = ns.reqseq(src)
      
    cc.append(cohset(*ifr1))                       # append to bookmark list

  # Make a bookmark for the chain of residuals for the same ifr:
  JEN_bookmarks.create(cc, 'peeled')

  # Finally, attach the current cohset to the sinks
  for ifr in array.ifrs():
    ns.sink(p,q) << Meq.Sink(cohset(*ifr),
                             station_1_index=p-1,
                             station_2_index=q-1,
                             output_col='DATA');

  # define VisDataMux
  ns.vdm << Meq.VisDataMux(*[ns.sink(p,q) for p,q in array.ifrs()]);




#==============================================================================
#==============================================================================

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
