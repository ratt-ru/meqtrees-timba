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
    for dx in (0,n):
      for dy in (0,n):
        if dx or dy:
          name = "%s%+d%+d" % (basename,dx,dy);
          model.append(point_source(ns,name,l0+dl*dx,m0+dm*dy));
  return model;

def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray(ns,ANTENNAS);
  # create an Observation object
  observation = Meow.Observation(ns);
    
  # create a Patch for the "precise" sim
  allsky = Meow.Patch(ns,'all',observation.phase_centre);
  # and for the for the "average" sim
  avgsky = Meow.Patch(ns,'avg',observation.phase_centre);
  
  # create a cross model
  source_list = cross_model(ns,'S',0,0,2*ARCMIN,2*ARCMIN,2);
  
  # create CLAR EJones terms
  Ej = clar_model.EJones(ns,array,observation,source_list);
  
  for src in source_list:
    dirname = src.direction.name;
    # corrupt source by its own E and add to 'allsky' patch
    corrupt_src = Meow.CorruptComponent(ns,src,label='E',station_jones=Ej(dirname));
    allsky.add(corrupt_src);
    
    # compute source by the average E and add to 'avgsky' patch
    Eavg = ns.Eavg(src.direction.name) << Meq.Mean(*[Ej(dirname,sta) for sta in array.stations()]);
    corrupt_src = Meow.CorruptComponent(ns,src,label='Eavg',jones=Eavg);
    avgsky.add(corrupt_src);
    
  # create set of nodes to compute visibilities...
  predict1 = allsky.visibilities(array,observation);
  predict2 = avgsky.visibilities(array,observation);

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
  Meow.Utils.make_dirty_image(npix=1200,cellsize='.5arcsec',channels=[32,1,1]);



# setup a few bookmarks
Settings.forest_state = record(bookmarks=[
  Meow.Bookmarks.PlotPage("K Jones",["K:S+0+1:2","K:S+0+1:9"],["K:S+0-1:2","K:S+0-1:9"]),
  Meow.Bookmarks.PlotPage("E Jones",["E:S+0+1:1","E:S+0+1:9"],["Eavg:S+0+1","Eavg:S+1+1"]),
]);


# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
