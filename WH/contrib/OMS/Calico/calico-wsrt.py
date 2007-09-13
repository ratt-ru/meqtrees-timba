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

 # standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

import Meow
import Meow.StdTrees
from Meow import Context

# MS options first
mssel = Context.mssel = Meow.MSUtils.MSSelector(has_input=True,tile_sizes=[8,16,32],flags=True);
# MS compile-time options
TDLCompileOptions(*mssel.compile_options());
# MS run-time options
TDLRuntimeOptions(*mssel.runtime_options());
## also possible:

# output mode menu
TDLCompileMenu("What do we do with the data",
  TDLOption('do_solve',"Calibrate",True),
  TDLOption('do_subtract',"Subtract sky model and generate residuals",True),
  TDLOption('do_correct',"Correct the data or residuals",True),
  TDLOption('do_correct_sky',"...include sky-Jones correction for first source in model",True));

# now load optional modules for the ME maker
from Meow import MeqMaker
meqmaker = MeqMaker.MeqMaker();

# specify available sky models
# these will show up in the menu automatically
import central_point_source
import Meow.LSM
lsm = Meow.LSM.MeowLSM(include_options=False);

meqmaker.add_sky_models([lsm,central_point_source]);

# now add optional Jones terms
# these will show up in the menu automatically

# E - beam
import wsrt_beams
meqmaker.add_sky_jones('E','beam',[wsrt_beams]);

# G - solvable gain/phases
import solvable_gain_phase
meqmaker.add_uv_jones('G','gains/phases',solvable_gain_phase);

# very important -- insert meqmaker's options properly
TDLCompileOptions(*meqmaker.compile_options());


def _define_forest (ns):
  ANTENNAS = mssel.get_antenna_set(range(1,28));
  array = Meow.IfrArray(ns,ANTENNAS,mirror_uvw=mirror_uvw);
  observation = Meow.Observation(ns);
  Meow.Context.set(array,observation);
  stas = array.stations();

  # setup imaging options 
  imsel = mssel.imaging_selector(npix=512,arcmin=meqmaker.estimate_image_size());
  TDLRuntimeMenu("Imaging options",*imsel.option_list());
  
  # make spigot nodes
  spigots = outputs = array.spigots();
  # make a predict tree using the MeqMaker
  if do_solve or do_subtract:
    predict = meqmaker.make_tree(ns);
  
  # make nodes to compute residuals 
  if do_subtract:
    residuals = ns.residuals;
    for p,q in array.ifrs():
      residuals(p,q) << spigots(p,q) - predict(p,q);
    outputs = residuals;

  # make solve trees
  if do_solve:
    solve_tree = Meow.StdTrees.SolveTree(ns,predict);
    # the output of the sequencer is either the residuals or the spigots,
    # according to what has been set above 
    outputs = solve_tree.sequencers(inputs=spigots,outputs=outputs);
    
  # and now we may need to correct the outputs
  if do_correct:
    if do_correct_sky:
      sky_correct = meqmaker.get_source_list(ns)[0];
    else:
      sky_correct = None;
    outputs = meqmaker.correct_uv_data(ns,outputs,sky_correct=sky_correct);
    
  # make sinks and vdm.
  # The list of inspectors comes in handy here
  Meow.StdTrees.make_sinks(ns,outputs,spigots=spigots,post=meqmaker.get_inspectors());


def _tdl_job_1_run_calibration (mqs,parent,wait=False):
  mqs.execute('VisDataMux',mssel.create_io_request(),wait=wait);
