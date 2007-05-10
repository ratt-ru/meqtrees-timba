from Timba.TDL import *

import Meow
import Meow.StdTrees
import Meow.Utils

def _define_forest(ns):
  # enable standard MS options from Meow
  Meow.Utils.include_ms_options(
    channels=[[15,40,1]],tile_sizes=[100],
    has_output=False
  );
  TDLRuntimeMenu("Make image",
    *Meow.Utils.imaging_options(npix=256,arcmin=72));
  
  array = Meow.IfrArray.WSRT(ns);
  observation = Meow.Observation(ns);
  Meow.Context.set(array,observation);
  
  spigots = array.spigots();

  inspectors = [
    Meow.StdTrees.vis_inspector(ns.inspect_spigots,spigots)
  ];
  
  # make sinks and vdm
  Meow.StdTrees.make_sinks(ns,spigots,post=inspectors);
  

def _tdl_job_inspect_MS (mqs,parent,**kw):
  req = Meow.Utils.create_io_request();
  mqs.execute('VisDataMux',req,wait=False);





if __name__ == '__main__':
    Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);
    ns.Resolve();
    pass
              
