# standard preamble
#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *
from Timba.Meq import meq
import math

import Meow
import Meow.StdTrees
from Meow import Jones
from Meow import Bookmarks

import iono_geometry
import sky_models

import mims
TDLCompileOption("ionospheric_model","Ionospheric model",
            [ mims.mim_poly,
              mims.center_tecs_only,
              mims.per_direction_tecs,
            ]);
TDLCompileOption('make_residuals',"Subtract model sources in output",True);

# define antenna list
ANTENNAS = range(1,28);

def _define_forest (ns):
  # enable standard MS options from Meow
  Meow.Utils.include_ms_options(tile_sizes=None);

  # create array & observation, add them to Context
  array = Meow.IfrArray(ns,ANTENNAS);
  observation = Meow.Observation(ns);
  Meow.Context.set(array=array,observation=observation);

  # create source model
  sources = sky_models.make_model(ns,"S0");
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
