# standard preamble
#import sys
#sys.path.insert(0,'')

from Timba.TDL import *
from Timba.Meq import meq
from Timba.Contrib.JEN.Grunt import NodeList
import math

import Meow
import Meow.StdTrees

#import iono_model
import sky_models
import pierce_points
import iono_model
#import NodeList

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[4,8,16,32]);
# note how we set default image size based on grid size/step
TDLRuntimeMenu("Imaging options",
    *Meow.Utils.imaging_options(npix=512,arcmin=sky_models.imagesize(),channels=[[1,1,1]]));

# define antenna list
ANTENNAS = range(1,27+1);

def _define_forest (ns):
  # setup the objects for the simulated observation
  # the phase_center is hardcoded in the MS
  array = Meow.IfrArray(ns,ANTENNAS);
  observation = Meow.Observation(ns);
  Meow.Context.set(array=array,observation=observation);
    
  # create source list
  sources = sky_models.make_model(ns,"S0");

  # ************** section is obsolete, for visualization ONLY *************
  # setup a long-lat grid to plot TEC values, for now use x and y
  xy = ns.xy << Meq.Composer(Meq.Grid(axis='y'),Meq.Grid(axis='x'));
  # redefine time to use it in math equations
  ns.time ** Meq.Time
  # use x and y to setup the TEC 2D field
  x = ns.x << Meq.Selector(xy,index=0)
  y = ns.y << Meq.Selector(xy,index=1)
  ns.tec1 << Meq.Sin(math.pi*(x/100 + ns.time/720));
  ns.tec2 << Meq.Sin(math.pi*(y/50 + ns.time/360));
  ns.tec << ns.tec1 + ns.tec2;
  # ************************************************************************
                        
  # now that we have the stations and the sources, the piercing points can be calculated
  # this returns the pierce point coordinates in ECEF, each of class PointSource
  # the position values look OK to me, need to plot them on X-Y projection with stations
  positions = pierce_points.get_pp(ns,sources)
  # tecs all return zero values, this shouldn't happen
  # For now leave out the Zj generation
  tecs = iono_model.sine_tid_model(ns,positions,sources)
  Zj = iono_model.make_zeta_jones(ns,tecs,sources)

  # corrupt all sources with the Zj for their direction
  allsky = Meow.Patch(ns,'sky',observation.phase_centre);
  #allsky.add(*sources);
  for src in sources:
    allsky.add(src.corrupt(Zj(src.direction.name)));
  # get predicted visibilities
  predict = allsky.visibilities();

  #***************Make a bunch of plots***********************************
  # All the nodes used here are defined in pierce_points.compress_nodes
  # First for the array
  array_long = NodeList.NodeList(ns, 'array_long', nodes=[ns.long_all,ns.pp_long])
  array_lat = NodeList.NodeList(ns, 'array_lat', nodes=[ns.lat_all,ns.pp_lat])
  plot_array = array_lat.plot_xy(xx=array_long, bookpage='Array (longlat)',color=['red','green'])

  # Plot the array ENU coordinates
  array_east = NodeList.NodeList(ns, 'array_east', nodes=[ns.arr_east,ns.pp_east])
  array_north = NodeList.NodeList(ns, 'array_north', nodes=[ns.arr_north,ns.pp_north])
  array_up = NodeList.NodeList(ns, 'array_up', nodes=[ns.arr_up,ns.pp_up])
  plot_array_en = array_north.plot_xy(xx=array_east, bookpage='Array (enu)')
  #plot_array_eu = array_up.plot_xy(xx=array_east, bookpage='Array (enu)')
  #plot_array_nu = array_up.plot_xy(xx=array_north, bookpage='Array (enu)')

  # Plot the array ECEF coordinates
  array_X = NodeList.NodeList(ns, 'array_X', nodes=[ns.arr_X_ecef])
  array_Y = NodeList.NodeList(ns, 'array_Y', nodes=[ns.arr_Y_ecef])
  array_Z = NodeList.NodeList(ns, 'array_Z', nodes=[ns.arr_Z_ecef])
  plot_array_XYecef = array_Y.plot_xy(xx=array_X, bookpage='Array (ecef)')
  plot_array_XZecef = array_Z.plot_xy(xx=array_X, bookpage='Array (ecef)')
  plot_array_YZecef = array_Z.plot_xy(xx=array_Y, bookpage='Array (ecef)')

  # Now for the pierce points
  pp_long = NodeList.NodeList(ns, 'pp_long', nodes=[ns.pp_long])
  pp_lat = NodeList.NodeList(ns, 'pp_lat', nodes=[ns.pp_lat])
  plot_longlat = pp_lat.plot_xy(xx=pp_long, color='green', bookpage='PP (longlat)', style='diamond')

  # Plot the pierce points in ENU coordinates
  pp_east = NodeList.NodeList(ns, 'pp_east', nodes=[ns.pp_east])
  pp_north = NodeList.NodeList(ns, 'pp_north', nodes=[ns.pp_north])
  pp_up = NodeList.NodeList(ns, 'pp_up', nodes=[ns.pp_up])
  plot_en = pp_north.plot_xy(xx=pp_east, bookpage='PP (enu)', color='green', style='diamond')
  #plot_eu = pp_up.plot_xy(xx=pp_east, bookpage='PP (enu)', color='green', style='diamond')
  #plot_nu = pp_up.plot_xy(xx=pp_north, bookpage='PP (enu)', color='green', style='diamond')

  # Plot the pierce points in ECEF xy coordinates
  pp_X_ecef = NodeList.NodeList(ns, 'pp_X', nodes=[ns.pp_X_ecef])
  pp_Y_ecef = NodeList.NodeList(ns, 'pp_Y', nodes=[ns.pp_Y_ecef])
  pp_Z_ecef = NodeList.NodeList(ns, 'pp_Z', nodes=[ns.pp_Z_ecef])
  plot_ecef = pp_Y_ecef.plot_xy(xx=pp_X_ecef, bookpage='PP (ecef)', color='green', style='diamond')

  # Test the output of the Meq.Azel node by plotting El vs Az
  test_az = NodeList.NodeList(ns, 'azimuth', nodes=[ns.pp_az])
  test_el = NodeList.NodeList(ns, 'elevation', nodes=[ns.pp_el])
  plot_azel = test_az.plot_xy(xx=test_el, bookpage='PP (azel)', color='green', style='diamond')               

  # put the TEC nodes into the inspectors, otherwise they will not be executed.
  # FUNNY: without setting the xy domain the TEC nodes still get assigned values...
  inspectors = [Meow.StdTrees.inspector(ns.inspect_tecpos,nodes=[ns.tec]),
                plot_array,
                plot_array_en,
  #              plot_array_eu,
  #              plot_array_nu,
                plot_array_XYecef,
                plot_array_XZecef,
                plot_array_YZecef,
                plot_longlat,
                plot_en,
  #              plot_eu,
  #              plot_nu,
                plot_ecef,
                plot_azel]
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
