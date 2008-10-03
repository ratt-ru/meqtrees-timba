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
import Meow.Utils
import Meow.StdTrees

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[16,32,48,96]);
TDLRuntimeMenu("Imaging options",
    *Meow.Utils.imaging_options(npix=256,arcmin=4,channels=[[32,1,1]]));

# useful constant: 1 deg in radians
DEG = math.pi/180.;
ARCMIN = DEG/60;

# source flux (same for all sources)
I = 1; Q = .2; U = .2; V = .2;

# we'll put the sources on a grid (positions in arc min)
LM = [(-1,-1),(-1,0),(-1,1),
      ( 0,-1),( 0,0),( 0,1), 
      ( 1,-1),( 1,0),( 1,1)];

def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray.VLA(ns);
  # create an Observation object
  observation = Meow.Observation(ns);
  # set global context
  Meow.Context.set(array=array,observation=observation);
  
  # create 10 sources
  sources = [];
  for isrc in range(len(LM)):
    l,m = LM[isrc];
    l *= ARCMIN;
    m *= ARCMIN;
    # generate an ID for direction and source
    srcname = 'S'+str(isrc);           
    # create Direction object
    src_dir = Meow.LMDirection(ns,srcname,l,m);
    # create a source with this direction, but make every 4th source
    # a gaussian
    if isrc%4:
      source = Meow.PointSource(ns,srcname,src_dir,I=I,Q=Q,U=U,V=V);
    else:
      source = Meow.GaussianSource(ns,srcname,src_dir,I=I,Q=Q,U=U,V=V,
                                    size=[.3*ARCMIN,.1*ARCMIN],
                                    phi=math.pi/(isrc+1),
                                    spi=float(isrc),freq0=8e+8);
    sources.append(source);
    
  # create a Patch for the entire observed sky
  allsky = Meow.Patch(ns,'all',observation.phase_centre);
  allsky.add(*sources);
  
  # create set of nodes to compute visibilities...
  predict = allsky.visibilities();
  
  # make some useful inspectors. Collect them into a list, since we need
  # to give a list of 'post' nodes to make_sinks() below
  inspectors = [];
  inspectors.append(
    Meow.StdTrees.vis_inspector(ns.inspect_predict,predict) );
  for i in [0,1,4,5]:
    inspectors.append( 
      Meow.StdTrees.vis_inspector(ns.inspect_predict(i),sources[i].visibilities(),bookmark=False) );
    
  # make sinks and vdm. Note that we don't want to make any spigots...
  # The list of inspectors comes in handy here
  Meow.StdTrees.make_sinks(ns,predict,spigots=False,post=inspectors);
  
  # make some bookmarks. Note that inspect_predict gets its own bookmark
  # automatically; for the others we said bookmark=False because we
  # want to put them onto a single page
  pg = Meow.Bookmarks.Page("Inspectors",2,2);
  for i in [0,1,4,5]:
    pg.add(ns.inspect_predict(i),viewer="Collections Plotter");
    
  # make a few more bookmarks
  pg = Meow.Bookmarks.Page("K Jones",2,2);
  for p in array.stations()[1:4]:      # use stations 1 through 4
    for src in sources:
      pg.add(src.direction.KJones()(p));

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
