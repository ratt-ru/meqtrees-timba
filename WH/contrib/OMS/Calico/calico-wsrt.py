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
from Meow import ParmGroup

# MS options first
mssel = Context.mssel = Meow.MSUtils.MSSelector(has_input=True,tile_sizes=None,flags=True);
# MS compile-time options
TDLCompileOptions(*mssel.compile_options());
# MS run-time options
TDLRuntimeMenu("MS/data selection options",*mssel.runtime_options());
## also possible:

# output mode menu
TDLCompileMenu("What do we want to do",
  TDLMenu("Calibrate",
     TDLOption('cal_vis',"Calibrate visibilities",True),
     TDLOption('cal_ampl',"Calibrate amplitudes",False),
     TDLOption('cal_log_ampl',"Calibrate log-amplitudes",False),
     TDLOption('cal_phase',"Calibrate phases",False),
     toggle='do_solve',open=True,exclusive='solve_type'
  ),
  TDLOption('do_subtract',"Subtract sky model and generate residuals",True),
  TDLOption('do_correct',"Correct the data or residuals",True),
   );
do_correct_sky = False;
  #TDLOption('do_correct_sky',"...include sky-Jones correction for first source in model",True));

# now load optional modules for the ME maker
from Meow import MeqMaker
meqmaker = MeqMaker.MeqMaker(solvable=True);

# specify available sky models
# these will show up in the menu automatically
import central_point_source
import model_3C343
import Meow.LSM
lsm = Meow.LSM.MeowLSM(include_options=False);

meqmaker.add_sky_models([central_point_source,model_3C343,lsm]);

# now add optional Jones terms
# these will show up in the menu automatically

# E - beam
import wsrt_beams
meqmaker.add_sky_jones('E','beam',[wsrt_beams]);

# G - solvable gain/phases
from solvable_gain_phase import AmplPhaseJones
B = AmplPhaseJones();
G = AmplPhaseJones();
meqmaker.add_uv_jones('B','bandpass',B);
meqmaker.add_uv_jones('G','receiver gains/phases',G);

# very important -- insert meqmaker's options properly
TDLCompileOptions(*meqmaker.compile_options());


def _define_forest (ns):
  ANTENNAS = mssel.get_antenna_set(range(1,15));
  array = Meow.IfrArray(ns,ANTENNAS,mirror_uvw=False);
  observation = Meow.Observation(ns);
  Meow.Context.set(array,observation);
  stas = array.stations();

  # make a ParmGroup and solve jobs for source fluxes
  srcs = meqmaker.get_source_list(ns);
  if srcs:
    parms = [];
    for src in srcs:
      parms += src.coherency().search(tags="solvable");
    if parms:
      pg_src = ParmGroup.ParmGroup("source",parms,
                  table_name="sources.mep",
                  individual=True,bookmark=True);
      # now make a solvejobs for the source
      ParmGroup.SolveJob("cal_source","Calibrate source model",pg_src);

  # make spigot nodes
  spigots = outputs = array.spigots();
  # ...and an inspector for them
  Meow.StdTrees.vis_inspector(ns.inspector('input'),spigots);
  inspectors = [ ns.inspector('input') ];

  # make a predict tree using the MeqMaker
  if do_solve or do_subtract:
    predict = meqmaker.make_tree(ns);

  # make nodes to compute residuals
  if do_subtract:
    residuals = ns.residuals;
    for p,q in array.ifrs():
      residuals(p,q) << spigots(p,q) - predict(p,q);
    outputs = residuals;

  # and now we may need to correct the outputs
  if do_correct:
    if do_correct_sky:
      srcs = meqmaker.get_source_list(ns);
      sky_correct = srcs and srcs[0];
    else:
      sky_correct = None;
    outputs = meqmaker.correct_uv_data(ns,outputs,sky_correct=sky_correct);

  # make solve trees
  if do_solve:
    # inputs to the solver are based on calibration type
    # if calibrating visibilities, feed them to condeq directly
    print solve_type;
    if solve_type == 'cal_vis':
      observed = spigots;
      model    = predict;
    # else take ampl/phase component
    else:
      model = ns.model;
      observed = ns.observed;
      if solve_type == 'cal_ampl':
        for p,q in array.ifrs():
          observed(p,q) << Meq.Abs(spigots(p,q));
          model(p,q)  << Meq.Abs(predict(p,q));
      elif solve_type == 'cal_log_ampl':
        for p,q in array.ifrs():
          observed(p,q) << Meq.Log(Meq.Abs(spigots(p,q)));
          model(p,q)  << Meq.Log(Meq.Abs(predict(p,q)));
      elif solve_type == 'cal_phase':
        for p,q in array.ifrs():
          observed(p,q) << 0;
          model(p,q)  << Meq.Abs(predict(p,q))*Meq.FMod(Meq.Arg(spigots(p,q))-Meq.Arg(predict(p,q)),2*math.pi);
      else:
        raise ValueError,"unknown solve_type setting: "+solve_type;
    # make a solve tree
    solve_tree = Meow.StdTrees.SolveTree(ns,model);
    # the output of the sequencer is either the residuals or the spigots,
    # according to what has been set above
    outputs = solve_tree.sequencers(inputs=observed,outputs=outputs);

  # make sinks and vdm.
  # The list of inspectors must be supplied here
  inspectors += meqmaker.get_inspectors();
  Meow.StdTrees.make_sinks(ns,outputs,spigots=spigots,post=inspectors);

  # very important -- insert meqmaker's runtime options properly
  # this should come last, since runtime options may be built up during compilation.
  TDLRuntimeOptions(*meqmaker.runtime_options(nest=False));
  # and insert all solvejobs
  TDLRuntimeOptions(*ParmGroup.get_solvejob_options());
  # finally, setup imaging options
  imsel = mssel.imaging_selector(npix=512,arcmin=meqmaker.estimate_image_size());
  TDLRuntimeMenu("Imaging options",*imsel.option_list());


