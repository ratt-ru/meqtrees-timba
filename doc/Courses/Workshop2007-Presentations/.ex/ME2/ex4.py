# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

import Meow
import clar_model

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[5,10,30]);
Meow.Utils.include_imaging_options();

DEG = math.pi/180.;
ARCMIN = DEG/60;

# define antenna list
ANTENNAS = range(1,28);

def point_source (ns,name,l,m):
  srcdir = Meow.LMDirection(ns,name,l,m);
  return Meow.PointSource(ns,name,srcdir,I=1);
  
def cross_model (ns,basename,l0,m0,dl,dm,nsrc):
  model = [ point_source(ns,basename+"+0+0",l0,m0) ];
  for n in range(1,nsrc+1):
    for dx,dy in ((n,0),(-n,0),(0,n),(0,-n)):
      name = "%s%+d%+d" % (basename,dx,dy);
      model.append(point_source(ns,name,l0+dl*dx,m0+dm*dy));
  return model;

def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray(ns,ANTENNAS);
  # create an Observation object
  observation = Meow.Observation(ns);
    
  # make list of source lists for three crosses
  src_lists = [ 
    cross_model(ns,'S0',0       ,0       ,.5*ARCMIN,.5*ARCMIN,2),
    cross_model(ns,'S2',2*ARCMIN,2*ARCMIN,.5*ARCMIN,.5*ARCMIN,2),
    cross_model(ns,'S4',4*ARCMIN,4*ARCMIN,.5*ARCMIN,.5*ARCMIN,2)
  ];
    
  # make master source list
  all_sources = src_lists[0]+src_lists[1]+src_lists[2];
  
  # make Ejones for all positions in master list
  Ej = clar_model.EJones(ns,array,observation,all_sources);

  # build a "precise" model, by corrupting all sources with the Ej
  # for their direction
  prec_sky = Meow.Patch(ns,'prec',observation.phase_centre);
  for src in all_sources:
    corrupt_src = Meow.CorruptComponent(ns,src,label='E',station_jones=Ej(src.direction.name));
    prec_sky.add(corrupt_src);
    
  # now make an approximate model
  approx_sky = Meow.Patch(ns,'approx',observation.phase_centre);
  # loop over all patches
  for (n,srclist) in enumerate(src_lists):
    # we know that first source in list is patch centre
    src0 = srclist[0];  
    # make the patch
    patch = Meow.Patch(ns,'patch'+str(n),src0.direction);
    patch.add(*srclist);
    # corrupt whole patch with Ej for patch centre
    corrupt_patch = Meow.CorruptComponent(ns,patch,label='E',station_jones=Ej(src0.direction.name));
    # add to the "approx" patch
    approx_sky.add(corrupt_patch);
    
  # create set of nodes to compute visibilities...
  predict1 = prec_sky.visibilities(array,observation);
  predict2 = approx_sky.visibilities(array,observation);

  # ...and attach them to sinks
  for p,q in array.ifrs():
    ns.sink(p,q) << Meq.Sink(predict1(p,q)-predict2(p,q),station_1_index=p-1,station_2_index=q-1,output_col='DATA');

  # define VisDataMux
  ns.vdm << Meq.VisDataMux(*[ns.sink(p,q) for p,q in array.ifrs()]);
  

def _tdl_job_1_simulate_MS (mqs,parent):
  req = Meow.Utils.create_io_request();
  # execute    
  mqs.execute('vdm',req,wait=False);
  
  
def _tdl_job_2_make_image (mqs,parent):
  Meow.Utils.make_dirty_image(npix=330,cellsize='2arcsec',channels=[32,1,1]);



# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
