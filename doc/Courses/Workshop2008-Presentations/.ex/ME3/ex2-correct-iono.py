# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

import Meow
import iono_model

# some GUI options
Meow.Utils.include_ms_options(has_input=True,tile_sizes=[8,16,32]);
TDLRuntimeMenu("Imaging options",
    *Meow.Utils.imaging_options(npix=512,arcmin=15,channels=[[32,1,1]]));

DEG = math.pi/180.;
ARCMIN = DEG/60;

# define antenna list
ANTENNAS = range(1,27+1);

def point_source (ns,name,l,m):
  srcdir = Meow.LMDirection(ns,name,l,m);
  return Meow.PointSource(ns,name,srcdir,I=1);
  
def grid_model (ns,basename,l0,m0,dl,dm,nsrc):
  # Returns grid of sources
  model = [ point_source(ns,basename+"+0+0",l0,m0) ];
  for dx in range(-nsrc,nsrc+1):
    for dy in range(-nsrc,nsrc+1):
      if dx or dy:
        name = "%s%+d%+d" % (basename,dx,dy);
        model.append(point_source(ns,name,l0+dl*dx,m0+dm*dy));
  return model;

def _define_forest (ns):
  array = Meow.IfrArray(ns,ANTENNAS);
  observation = Meow.Observation(ns);
  Meow.Context.set(array,observation);
    
  # dummy source at phase center
  sources = [ point_source(ns,"0",0,0) ];
    
  # make Zjones for source center
  Zj = iono_model.compute_zeta_jones(ns,sources);
  # this now just needs an antenna qualifier
  Zj = Zj("0");
  
  # create inverted Zs
  for p in array.stations():
    ns.Zinv(p) << Meq.MatrixInvert22(Zj(p));
    ns.Zinvt(p) << Meq.ConjTranspose(ns.Zinv(p));
  
  # now define spigots, corrections, attach to sinks
  for p,q in array.ifrs():
    spig = ns.spigot(p,q) << Meq.Spigot(station_1_index=p-1,station_2_index=q-1);
    correct = ns.correct(p,q) << \
      Meq.MatrixMultiply(ns.Zinv(p),spig,ns.Zinvt(q));
    ns.sink(p,q) << Meq.Sink(correct,station_1_index=p-1,station_2_index=q-1,output_col='DATA');
      
  # define VisDataMux
  ns.vdm << Meq.VisDataMux(*[ns.sink(p,q) for p,q in array.ifrs()]);
  
  


def _tdl_job_1_correct_MS (mqs,parent):
  req = Meow.Utils.create_io_request();
  # execute    
  mqs.execute('vdm',req,wait=False);
  
  
def _tdl_job_2_make_image (mqs,parent):
  Meow.Utils.make_dirty_image(npix=1024,arcmin=25,channels=[32,1,1]);


# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
