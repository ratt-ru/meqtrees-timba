# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

import Meow
import iono_model

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[5,10,30]);
Meow.Utils.include_imaging_options();

TDLCompileOption("grid_size","Grid size",[0,1,2,3,4]);
TDLCompileOption("grid_step","Grid step, in arcmin",[.1,.5,1,2,5,10,15,20,30]);
TDLCompileOption("noise_stddev","Add noise (Jy)",[0,1e-6,1e-3],more=float);

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
  
def noise_matrix (stddev=0.1):
  """helper function to create a 2x2 complex gaussian noise matrix""";
  noise = Meq.GaussNoise(stddev=stddev);
  return Meq.Matrix22(
    Meq.ToComplex(noise,noise),Meq.ToComplex(noise,noise),
    Meq.ToComplex(noise,noise),Meq.ToComplex(noise,noise)
  );

def _define_forest (ns):
  array = Meow.IfrArray(ns,ANTENNAS);
  observation = Meow.Observation(ns);
  Meow.Context.set(array,observation);
    
  # make list of source lists for three crosses
  sources = grid_model(ns,'S0',0,0,grid_step*ARCMIN,grid_step*ARCMIN,grid_size);
    
  # make Zjones for all positions in source list
  Zj = iono_model.compute_zeta_jones(ns,sources);

  # corrupt all sources with the Zj for their direction
  allsky = Meow.Patch(ns,'sky',observation.phase_centre);
  for src in sources:
    corrupt_src = Meow.CorruptComponent(ns,src,label='Z',station_jones=Zj(src.direction.name));
    allsky.add(corrupt_src);

  # get predicted visibilities
  predict = allsky.visibilities();
  
  # ..and attach them to sinks, with a bit of noise thrown in
  for p,q in array.ifrs():
    output = predict(p,q);
    if noise_stddev:
      output = ns.noisy_predict(p,q) << output + noise_matrix(noise_stddev); 
    ns.sink(p,q) << Meq.Sink(output,station_1_index=p-1,station_2_index=q-1,output_col='DATA');
      
  # These are the "interesting" stations:
  # 10 is center of array, 9, 18 and 27 are at the end of the arms
  stas = [10,9,18,27 ];
  # make a couple of composers, for visualizations
  ns.visualize = Meq.ReqMux(
    ns.inspect_tecs << \
      Meq.Composer(
        plot_label = [ "%s-%s"%(p,src.name) for src in sources for p in stas ],
        *[ ns.tec(src.name,p) for src in sources for p in stas ]
      ),
    ns.inspect_Z << \
      Meq.Composer(
        plot_label = [ "%s-%s"%(p,src.name) for src in sources for p in stas ],
        *[ ns.Z(src.name,p) for src in sources for p in stas ]
      )
  );
  
  # define VisDataMux
  ns.vdm << Meq.VisDataMux(post=ns.visualize,*[ns.sink(p,q) for p,q in array.ifrs()]);
  
  # and make some more interesting bookmarks
  Meow.Bookmarks.Page("Inspect TECs").add(ns.inspect_tecs,viewer="Collections Plotter");
  Meow.Bookmarks.Page("Inspect Z").add(ns.inspect_Z,viewer="Collections Plotter");
  
  # 10 is center of array, 9, 18 and 27 are at the end of the arms
  stas = [10,9,18,27 ];
  for p in stas:
    pg = Meow.Bookmarks.Page("TECs, station "+str(p),3,3);
    for src in sources[:9]:
      pg.add(ns.tec(src.name,p));
  for p in stas:
    pg = Meow.Bookmarks.Page("Z Jones, station "+str(p),3,3);
    for src in sources[:9]:
      pg.add(ns.Z(src.name,p));
  


def _tdl_job_1_simulate_MS (mqs,parent):
  req = Meow.Utils.create_io_request();
  # execute    
  mqs.execute('vdm',req,wait=False);
  
  
# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';