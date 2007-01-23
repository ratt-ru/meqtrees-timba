# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

import Meow
import Meow.StdTrees
from Meow import Jones
from Meow import Bookmarks
import iono_geometry

DEG = math.pi/180.;
ARCMIN = DEG/60;

# define antenna list
ANTENNAS = range(1,27+1);

TDLCompileOption("grid_size","Grid size",[0,1,2,3,4]);
TDLCompileOption("grid_step","Grid step, in arcmin",[.1,.5,1,2,5,10,15,20,30]);
import mims
TDLCompileOption("ionospheric_model","Ionospheric model",
            [ mims.mim_poly,
              mims.center_tecs_only,
              mims.per_direction_tecs,
            ]);
TDLCompileOption('make_residuals',"Subtract model sources in output",True);

# define antenna list
ANTENNAS = range(1,28);

# useful constant: 1 deg in radians
DEG = math.pi/180.;
ARCMIN = DEG/60;

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
  # enable standard MS options from Meow
  Meow.Utils.include_ms_options(tile_sizes=None);

  # create array & observation, add them to Context
  array = Meow.IfrArray(ns,ANTENNAS);
  observation = Meow.Observation(ns);
  Meow.Context.set(array=array,observation=observation);

  # create source model
  sources = grid_model(ns,'S0',0,0,grid_step*ARCMIN,grid_step*ARCMIN,grid_size);
  # create a Patch for the entire observed sky
  allsky = Meow.Patch(ns,'all',observation.phase_centre);

  # create ionospheric model -- the particular function (in mims) that
  # we end up calling is set by CompileOption above. The function
  # is expected to return an unqualified Zeta-Jones, which we qualify
  # with source name and station
  Zjones = ionospheric_model(ns,sources);

  # corrupt sources and add to patch  
  for src in sources:
    allsky.add(src.corrupt(Zjones(src.name)));
  
  # create set of nodes to compute visibilities...
  predict = allsky.visibilities();

  # create solve tree.
  solve_tree = Meow.StdTrees.SolveTree(ns,predict,residuals=make_residuals);
  solve_output = solve_tree.outputs(array.spigots());
  
  # correct output for Zj of center source (which we know is the first in the list)
  Zj0 = Zjones(sources[0].name);
  corrected = Jones.apply_correction(ns.corrected,solve_output,Zj0);

  # create some visualizers
  visualizers = [
    Meow.StdTrees.vis_inspector(ns.inspect('spigots'),array.spigots(),bookmark=False),
    Meow.StdTrees.vis_inspector(ns.inspect('residuals'),corrected,bookmark=False),
    Meow.StdTrees.jones_inspector(ns.inspect('Z0'),Zj0,bookmark=False),
    Meow.StdTrees.inspector(ns.inspect('TECs'),Zjones.search(tags="mim tec")),
  ];

  # finally, make the sinks and vdm. Visualizers will be executed
  # after ("post") all sinks
  Meow.Context.vdm = Meow.StdTrees.make_sinks(ns,corrected,post=visualizers);
  
  # now define some runtime solve jobs
  solve_tree.define_solve_job("Calibrate iononosphere","iono",
                              Zjones.search(tags="mim solvable"));
                                  
  # insert standard imaging options from Meow
  TDLRuntimeMenu("Make image",*Meow.Utils.imaging_options(npix=512,arcmin=12));

  # and finally a helper function to clear solutions
  def job_clear_out_all_previous_solutions (mqs,parent,**kw):
    from qt import QMessageBox
    if QMessageBox.warning(parent,"Clearing solutions","This will clear out <b>all</b> previously obtained calibrations. Are you sure?",
          QMessageBox.Yes,QMessageBox.No|QMessageBox.Default|QMessageBox.Escape) == QMessageBox.Yes:
      try:    os.system("rm -fr "+mims.get_mep_table());
      except: pass;
  TDLJob(job_clear_out_all_previous_solutions,"Clear out all solutions");
  
  # make some nice bookmarks
  Bookmarks.Page("ZJones",1,2) \
    .add(ns.inspect('Z0'),viewer="Collections Plotter") \
    .add(solve_tree.solver());
  
  Bookmarks.Page("Vis Inspectors",1,2) \
    .add(ns.inspect('spigots'),viewer="Collections Plotter") \
    .add(ns.inspect('residuals'),viewer="Collections Plotter");
  


  
# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
