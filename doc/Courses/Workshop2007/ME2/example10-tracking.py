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
import random

import Meow
import Meow.StdTrees
import sky_models

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[16,32,48,96]);
TDLRuntimeMenu("Imaging options",
    *Meow.Utils.imaging_options(npix=256,arcmin=sky_models.imagesize(),channels=[[32,1,1]]));

# useful constant: 1 deg in radians
DEG = math.pi/180.;
ARCMIN = DEG/60;


def pseudo_wsrt_beam (E,lm):
  """This makes the nodes to compute the beam gain, E, given an lm position.
  'lm' is an input node
  'E' is an output node to which the gain will be assigned""";
  lmsq = E('lmsq') << Meq.Sqr(lm);
  lsq = E('lsq') << Meq.Selector(lmsq,index=0);
  msq = E('msq') << Meq.Selector(lmsq,index=1);
  E << Meq.Pow(Meq.Cos(Meq.Sqrt(lsq+msq)*2e-6*Meq.Freq()),3);
  
  return E;
  
TDLCompileOption("beam_model","Beam model",[pseudo_wsrt_beam]);
TDLCompileOption("max_tr_error","Max tracking error, arcsec",[1,2,5],more=float);
TDLCompileOption("min_tr_period","Min time scale for tracking variation, hours",[0,1],more=float);
TDLCompileOption("max_tr_period","Max time scale for tracking variation, hours",[2,4],more=float);

def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray.VLA(ns);
  # create an Observation object
  observation = Meow.Observation(ns);
  # set global context
  Meow.Context.set(array=array,observation=observation);
 
  ampl = max_tr_error*DEG/3600; 
  # create nodes to compute tracking errors per antenna
  for p in array.stations():
    # pick random periods of dl/dm variation, in seconds
    dlp = random.uniform(min_tr_period*3600,max_tr_period*3600);
    dmp = random.uniform(min_tr_period*3600,max_tr_period*3600);
    # pick a random starting phase for the variations
    dlp_0 = random.uniform(0,2*math.pi); 
    dmp_0 = random.uniform(0,2*math.pi);
    ns.dl(p) << ampl*Meq.Sin(Meq.Time()*(2*math.pi/dlp)+dlp_0);
    ns.dm(p) << ampl*Meq.Sin(Meq.Time()*(2*math.pi/dmp)+dmp_0);
    ns.dlm(p) << Meq.Composer(ns.dl(p),ns.dm(p));
  
  # create a source model and make list of corrupted sources
  allsky = Meow.Patch(ns,'all',observation.phase_centre);
  sources = sky_models.make_model(ns,"S");
  for src in sources:
    lm = src.direction.lm();
    E = ns.E(src.name);
    for p in array.stations():
      # compute "apparent" position of source per each antenna
      lm1 = ns.lm1(src.name,p) << lm + ns.dlm(p);
      # compute E for apparent position
      beam_model(E(p),lm1);
    allsky.add(src.corrupt(E));

  predict = allsky.visibilities();

  # make some useful inspectors. Collect them into a list, since we need
  # to give a list of 'post' nodes to make_sinks() below
  inspectors = [];
  inspectors.append(
    Meow.StdTrees.vis_inspector(ns.inspect_predict,predict) );
  for src in sources[:5]:
    inspectors.append( 
      Meow.StdTrees.jones_inspector(ns.inspect_E(src.name),ns.E(src.name)) );
    inspectors.append( 
      Meow.StdTrees.jones_inspector(ns.inspect_lm1(src.name),ns.lm1(src.name)) );
    
  # make sinks and vdm. Note that we don't want to make any spigots...
  # The list of inspectors comes in handy here
  Meow.StdTrees.make_sinks(ns,predict,spigots=False,post=inspectors);
  
  # make a few more bookmarks
  pg = Meow.Bookmarks.Page("K Jones",2,2);
  for p in array.stations()[1:4]:      # use stations 1 through 3
    for src in sources[:4]:            # use sources 0 through 3
      pg.add(src.direction.KJones()(p));
      
  # make a few more bookmarks
  pg = Meow.Bookmarks.Page("E Jones",2,2);
  for p in array.stations()[1:4]:      # use stations 1 through 3
    for src in sources[:4]:            # use sources 0 through 3
      pg.add(ns.E(src.name,p));

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
