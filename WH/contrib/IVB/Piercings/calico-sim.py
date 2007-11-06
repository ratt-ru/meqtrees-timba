# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

import Meow
import Meow.StdTrees
from Meow import Context,ParmGroup,Bookmarks
from Meow.Parameterization import resolve_parameter

do_sim=True

# MS options first
mssel = Context.mssel = Meow.MSUtils.MSSelector(has_input=True,tile_sizes=None,flags=False,hanning=True);
# MS compile-time options
TDLCompileOptions(*mssel.compile_options());
# MS run-time options
TDLRuntimeMenu("MS/data selection options",*mssel.runtime_options());

# now load optional modules for the ME maker
from Meow import MeqMaker
meqmaker = MeqMaker.MeqMaker(solvable=True);

# specify available sky models
# these will show up in the menu automatically
import Meow.LSM
lsm = Meow.LSM.MeowLSM(include_options=False);

meqmaker.add_sky_models([lsm]);

# very important -- insert meqmaker's options properly
TDLCompileOptions(*meqmaker.compile_options());

def _define_forest (ns):
  ANTENNAS = mssel.get_antenna_set(range(1,15));
  array = Meow.IfrArray(ns,ANTENNAS,mirror_uvw=False);
  observation = Meow.Observation(ns);
  Meow.Context.set(array,observation);
  stas = array.stations();
  srcs = meqmaker.get_source_list(ns);
  
  # make spigot nodes
  spigots = spigots0 = outputs = array.spigots();

  # ...and an inspector for them
  Meow.StdTrees.vis_inspector(ns.inspector('input'),spigots,
                              bookmark="Inspect input visibilities");
  inspectors = [ ns.inspector('input') ];
  Bookmarks.make_node_folder("Input visibilities by baseline",
    [ spigots(p,q) for p,q in array.ifrs() ],sorted=True,ncol=2,nrow=2);

  # make a predict tree using the MeqMaker
  if do_sim:
      predict = meqmaker.make_tree(ns);

  # make sinks and vdm.
  # The list of inspectors must be supplied here
  inspectors += meqmaker.get_inspectors() or [];
  Meow.StdTrees.make_sinks(ns,outputs,spigots=spigots0,post=inspectors);
  Bookmarks.make_node_folder("Corrected/residual visibilities by baseline",
    [ outputs(p,q) for p,q in array.ifrs() ],sorted=True,ncol=2,nrow=2);
    
  if not do_sim:
    global _run_tree;

  # very important -- insert meqmaker's runtime options properly
  # this should come last, since runtime options may be built up during compilation.
  TDLRuntimeOptions(*meqmaker.runtime_options(nest=False));
  # finally, setup imaging options
  imsel = mssel.imaging_selector(npix=512,arcmin=meqmaker.estimate_image_size());
  TDLRuntimeMenu("Imaging options",*imsel.option_list());

# runs the tree
def _run_tree (mqs,parent,tiling=240,**kw):
  mqs.execute(Context.vdm.name,mssel.create_io_request(tiling),wait=False);
