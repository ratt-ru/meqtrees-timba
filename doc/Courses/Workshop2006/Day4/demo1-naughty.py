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
import Meow.Bookmarks

from NaughtyDirection import NaughtyDirection

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[5,10]);
Meow.Utils.include_imaging_options();

TDLCompileOption('grid_step',"Grid stepping (in arcmin)",[1,2,10,60]);

# define antenna list
ANTENNAS = range(1,28);

# useful constant: 1 deg in radians
DEG = math.pi/180.;
ARCMIN = DEG/60;

# source flux (same for all sources)
I = 1; Q = 0; U = 0; V = .0;

def point_source (ns,name,l,m):
  srcdir = Meow.LMDirection(ns,name,l,m);
  return Meow.PointSource(ns,name,srcdir,I=1);

def naughty_source (ns,name,l,m):
  srcdir = NaughtyDirection(ns,name,l,m);
  return Meow.PointSource(ns,name,srcdir,I=1);
  
def cross_model (ns,basename,l0,m0,dl,dm,nsrc,kind=point_source):
  model = [ point_source(ns,basename+"+0+0",l0,m0) ];
  for n in range(1,nsrc+1):
    for dx,dy in ((n,0),(-n,0),(0,n),(0,-n)):
      name = "%s%+d%+d" % (basename,dx,dy);
      model.append(kind(ns,name,l0+dl*dx,m0+dm*dy));
  return model;

def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray(ns,ANTENNAS);
  # create an Observation object
  observation = Meow.Observation(ns);
  
  # create a Patch for the entire observed sky
  allsky = Meow.Patch(ns,'all',observation.phase_centre);
  allsky1 = Meow.Patch(ns,'naughty',observation.phase_centre);

  # create "cross" of point sources
  ps_list = cross_model(ns,"S",0,0,grid_step*ARCMIN,grid_step*ARCMIN,2,kind=point_source);
  
  # create same "cross" of naughty sources
  ns_list = cross_model(ns,"N",0,0,grid_step*ARCMIN,grid_step*ARCMIN,2,kind=naughty_source);

  allsky.add(*ps_list);
  allsky1.add(*ns_list);

  # create set of nodes to compute visibilities...
  predict = allsky.visibilities(array,observation);
  predict1 = allsky1.visibilities(array,observation);
  
  # ...and attach them to resamplers and sinks
  for p,q in array.ifrs():
    ns.sink(p,q) << Meq.Sink(predict(p,q)-predict1(p,q),station_1_index=p-1,station_2_index=q-1,output_col='DATA');

  # define VisDataMux
  ns.vdm << Meq.VisDataMux(*[ns.sink(p,q) for p,q in array.ifrs()]);
  

def _tdl_job_1_simulate_MS (mqs,parent):
  req = Meow.Utils.create_io_request();
  # execute    
  mqs.execute('vdm',req,wait=False);
  
  
def _tdl_job_2_make_image (mqs,parent):
  # image "radius" in arcseconds
  image_radius = grid_step*2.5*60;  
  # corresponds to this cellsize
  cellsize = str(image_radius/256)+"arcsec";
  Meow.Utils.make_dirty_image(npix=512,cellsize=cellsize,channels=[32,1,1]);



# setup a few bookmarks
Settings.forest_state = record(bookmarks=[
  Meow.Bookmarks.PlotPage("K Jones",["K:S0:1","K:S0:9"],["K:S1:2","K:S1:9"])
]);



# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
