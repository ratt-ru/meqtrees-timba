# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

import Meow
import Meow.StdTrees
import clar_model

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[16,32,48,96]);
TDLRuntimeMenu("Imaging options",
    *Meow.Utils.imaging_options(npix=256,arcmin=5,channels=[[32,1,1]]));

# GUI option for selecting a source model
TDLCompileOption('source_model',"Source model",[
    clar_model.point_sources_only,
    clar_model.point_and_extended_sources,
    clar_model.radio_galaxy,
    clar_model.faint_source
  ],default=0);

TDLCompileOption('apply_clar_beam',"Apply CLAR beam",False);

def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray.VLA(ns);
  # create an Observation object
  observation = Meow.Observation(ns);
  # set global context
  Meow.Context.set(array=array,observation=observation);
    
  # create a Patch for the entire observed sky
  allsky = Meow.Patch(ns,'all',observation.phase_centre);
  
  # create nominal CLAR source model by calling the specified
  # model function
  clar_model.init_directions(ns);
  sources = source_model(ns);
  
  if apply_clar_beam:
    # create CLAR EJones terms
    Ej = clar_model.EJones_pretab(ns,array,sources);

    # corrupt sources with CLAR beam and add to allsky patch
    for src in sources:
      corrupt_src = src.corrupt(Ej(src.direction.name));
      allsky.add(corrupt_src);
  else:
    allsky.add(*sources);
  
  # create set of nodes to compute visibilities...
  predict = allsky.visibilities();
  
  # make some useful inspectors. Collect them into a list, since we need
  # to give a list of 'post' nodes to make_sinks() below
  inspectors = [];
  inspectors.append(
    Meow.StdTrees.vis_inspector(ns.inspect_predict,predict) );
  if apply_clar_beam:
    for src in sources[0:4]:  # for four sources...
      inspectors.append( 
        Meow.StdTrees.jones_inspector(ns.inspect_E(src.name),Ej(src.name),bookmark=False) );
    
  # make sinks and vdm. Note that we don't want to make any spigots...
  # The list of inspectors comes in handy here
  Meow.StdTrees.make_sinks(ns,predict,spigots=False,post=inspectors);
  
  # make some bookmarks. Note that inspect_predict gets its own bookmark
  # automatically; for the others we said bookmark=False because we
  # want to put them onto a single page
  if apply_clar_beam:
    pg = Meow.Bookmarks.Page("E Inspectors",2,2);
    for src in sources[0:4]:
      pg.add(ns.inspect_E(src.name),viewer="Collections Plotter");

    pg = Meow.Bookmarks.Page("E Jones",2,2);
    for p in array.stations()[1:4]:      # use stations 1 through 4
      for src in sources[:4]:            # use first 4 sources
        pg.add(Ej(src.direction.name,p));
  

def _tdl_job_1_simulate_MS (mqs,parent):
  req = Meow.Utils.create_io_request();
  # execute    
  mqs.execute('VisDataMux',req,wait=False);
  
  


# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
