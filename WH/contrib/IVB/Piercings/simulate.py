# standard preamble
#import sys
#sys.path.insert(0,'')

from Timba.TDL import *
from Timba.Meq import meq
import math

import Meow
import Meow.StdTrees
import Meow.LSM
from Meow import MeqMaker
from Meow import Context
meqmaker = MeqMaker.MeqMaker(solvable=False)
lsm = Meow.LSM.MeowLSM(include_options=False)
meqmaker.add_sky_models([lsm])

#import sky_models
import pierce_points
import iono_model
import NodeList

# Oude versie
# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[4,8,16,32]);
# note how we set default image size based on grid size/step
TDLRuntimeMenu("Imaging options",
    *Meow.Utils.imaging_options(npix=512,arcmin=180,channels=[[1,1,1]]));

# Nieuwe versie
# MS options first
#mssel = Context.mssel = Meow.MSUtils.MSSelector(has_input=True,tile_sizes=None,flags=False,hanning=True);
## MS compile-time options
#TDLCompileOptions(*mssel.compile_options());
## MS run-time options
#TDLRuntimeMenu("MS/data selection options",*mssel.runtime_options());
# very important -- insert meqmaker's options properly
TDLCompileOptions(*meqmaker.compile_options());

# define antenna list
ANTENNAS = range(1,25);

def _define_forest (ns):
  # setup the objects for the simulated observation
  # the phase_center is hardcoded in the MS
  array = Meow.IfrArray(ns,ANTENNAS);
  observation = Meow.Observation(ns);
  Meow.Context.set(array=array,observation=observation);
    
  # create source list
  #sources = sky_models.make_model(ns,"S0");
  sources = meqmaker.get_source_list(ns);

  # now that we have the stations and the sources, the pierce points can be calculated
  # this returns the pierce point coordinates in ENU, each of class PointSource
  positions = pierce_points.compute_pierce_points(ns,sources)
  # calculate the tec value at each pp and make the Z-jones
  tecs = iono_model.sine_tid_model(ns,positions.pp_enu,sources)
  Zj = iono_model.make_zeta_jones(ns,tecs,sources)

  # corrupt all sources with the Zj for their direction
  allsky = Meow.Patch(ns,'sky',observation.phase_centre);
  #allsky.add(*sources);
  for src in sources:
    allsky.add(src.corrupt(Zj(src.direction.name)));
  # get predicted visibilities
  predict = allsky.visibilities();


#***************Make a bunch of plots***********************************
##  # All the nodes used here are defined in pierce_points.compress_nodes
##  # First for the array
  array_long = NodeList.NodeList(ns, 'array_long', nodes=[positions.arr_long,positions.pp_long])
  array_lat = NodeList.NodeList(ns, 'array_lat', nodes=[positions.arr_lat,positions.pp_lat])
  plot_array_ll = array_lat.plot_xy(xx=array_long, bookpage='Array and PP (longlat)')

##  # Plot the array ENU coordinates
  array_east = NodeList.NodeList(ns, 'array_east', nodes=[positions.arr_east])
  array_north = NodeList.NodeList(ns, 'array_north', nodes=[positions.arr_north])
  array_up = NodeList.NodeList(ns, 'array_up', nodes=[positions.arr_up])
  plot_array_enu = array_north.plot_xy(xx=array_east, bookpage='Array (enu)')  

  # Now for the pierce points
  pp_long = NodeList.NodeList(ns, 'pp_long', nodes=[positions.pp_long])
  pp_lat = NodeList.NodeList(ns, 'pp_lat', nodes=[positions.pp_lat])
  plot_pp_ll = pp_lat.plot_xy(xx=pp_long, color='green', bookpage='PP (longlat)', style='diamond')

  # Plot the pierce points in ENU coordinates
  pp_east = NodeList.NodeList(ns, 'pp_east', nodes=[positions.pp_east])
  pp_north = NodeList.NodeList(ns, 'pp_north', nodes=[positions.pp_north])
  pp_up = NodeList.NodeList(ns, 'pp_up', nodes=[positions.pp_up])
  plot_pp_enu = pp_north.plot_xy(xx=pp_east, bookpage='PP (enu)', color='green', style='diamond')

  # put the TEC nodes into the inspectors, otherwise they will not be executed.
  inspectors = [plot_array_ll,
                plot_array_enu,
                plot_pp_ll,
                plot_pp_enu]
  inspectors.append(
    Meow.StdTrees.vis_inspector(ns.inspect_predict,predict));
  # make sinks and vdm. Note that we don't want to make any spigots...
  # The list of inspectors comes in handy here
  Meow.StdTrees.make_sinks(ns,predict,spigots=False,post=inspectors);

  Meow.Bookmarks.Page("TECs",2,2) \
                                       .add(ns.inspect_predict(1)) \
                                       .add(ns.tec1) \
                                       .add(ns.tec2) \
                                       .add(ns.tec);

#  imsel = mssel.imaging_selector(npix=512,arcmin=meqmaker.estimate_image_size());
#  TDLRuntimeMenu("Imaging options",*imsel.option_list());


# cache everything for now
Settings.forest_state.cache_policy=100

def _tdl_job_1_simulate_MS (mqs,parent):
  req = Meow.Utils.create_io_request();
  mqs.execute('VisDataMux',req,wait=False);

# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
