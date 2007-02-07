from Timba.TDL import *
from Timba.Meq import meq
from numarray import *

import Meow
import Meow.StdTrees

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[16,32,48,96]);
TDLRuntimeMenu("Imaging options",
    *Meow.Utils.imaging_options(npix=256,arcmin=15));

TDLCompileOption('flux_scale',"Rescale image flux",[1.],more=float);


def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray.VLA(ns);
  # create an Observation object
  observation = Meow.Observation(ns);
  # set global context
  Meow.Context.set(array=array,observation=observation);
  
  img = Meow.FITSImageComponent(ns,'IMG',filename="image.fits",
          fluxscale=flux_scale,
          # doesn't like to be at center...
          direction=Meow.LMDirection(ns,"IMG",1e-9,1e-9));
  img.set_options(fft_pad_factor=2);
  
  # create simulated visibilities for sky
  predict = img.visibilities();
  
  # make sinks and vdm. Note that we don't want to make any spigots...
  # The list of inspectors comes in handy here
  Meow.StdTrees.make_sinks(ns,predict,spigots=False);
  

def _tdl_job_1_simulate_MS (mqs,parent):
  req = Meow.Utils.create_io_request();
  # execute    
  mqs.execute('VisDataMux',req,wait=False);

Settings.forest_state.cache_policy = 1;  # 1 for smart caching, 100 for full caching

Settings.orphans_are_roots = False;


def _test_compilation ():
  ns = NodeScope();
  _define_forest(ns);
  ns.Resolve();

if __name__ == '__main__':
  if '-prof' in sys.argv:
    import profile
    profile.run('_test_compilation()','clar_fast_predict.prof');
  else:
#    Timba.TDL._dbg.set_verbose(5);
    _test_compilation();
              
