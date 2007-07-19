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
import clar_model
import sky_models

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[16,32,48,96]);
TDLRuntimeMenu("Imaging options",
    *Meow.Utils.imaging_options(npix=256,arcmin=sky_models.imagesize(),channels=[[32,1,1]]));

def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray.VLA(ns);
  # create an Observation object
  observation = Meow.Observation(ns);
  # set global context
  Meow.Context.set(array=array,observation=observation);
    
  # create a Patch for the "precise" sim
  allsky = Meow.Patch(ns,'all',observation.phase_centre);
  # and for the for the "average" sim
  avgsky = Meow.Patch(ns,'avg',observation.phase_centre);
  
  # create a source model
  source_list = sky_models.make_model(ns,"S");

  # create CLAR EJones terms
  Ej = clar_model.EJones(ns,array,observation,source_list);
  
  for src in source_list:
    dirname = src.direction.name;
    # corrupt source by its own E and add to 'allsky' patch
    corrupt_src = src.corrupt(Ej(dirname));
    allsky.add(corrupt_src);
    
    # compute source by the average E and add to 'avgsky' patch
    Eavg = ns.Eavg(src.direction.name) << Meq.Mean(*[Ej(dirname,sta) for sta in array.stations()]);
    corrupt_src = src.corrupt(Eavg,per_station=False);
    avgsky.add(corrupt_src);
    
  # create set of nodes to compute visibilities and deltas
  predict1 = allsky.visibilities();
  predict2 = avgsky.visibilities();

  for p,q in array.ifrs():
    ns.diff(p,q) << predict1(p,q) - predict2(p,q);

  # make some useful inspectors. Collect them into a list, since we need
  # to give a list of 'post' nodes to make_sinks() below
  inspectors = [
    Meow.StdTrees.vis_inspector(ns.inspect_diff,ns.diff),
  ];

  # make sinks and vdm. Note that we don't want to make any spigots...
  # The list of inspectors comes in handy here
  Meow.StdTrees.make_sinks(ns,ns.diff,spigots=False,post=inspectors);
  
  

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
