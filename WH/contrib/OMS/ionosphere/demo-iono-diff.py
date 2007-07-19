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
import iono_model

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[5,10,30]);
Meow.Utils.include_imaging_options();

TDLCompileOption("grid_size","Grid size",[0,1,2,3,4]);
TDLCompileOption("grid_step","Grid step, in arcmin",[.1,.5,1,2,5,10,15,20,30]);
TDLCompileOption("sim_mode","Simulation mode",["corrupt","diff","singlediff","correct"]);

DEG = math.pi/180.;
ARCMIN = DEG/60;

# define antenna list
ANTENNAS = range(1,27+1);

def point_source (ns,name,l,m):
  srcdir = Meow.LMDirection(ns,name,l,m);
  return Meow.PointSource(ns,name,srcdir,I=1);
  
def grid_model (ns,basename,l0,m0,dl,dm,nsrc):
  model = [ point_source(ns,basename+"+0+0",l0,m0) ];
  for dx in range(-nsrc,nsrc+1):
    for dy in range(-nsrc,nsrc+1):
      if dx or dy:
        name = "%s%+d%+d" % (basename,dx,dy);
        model.append(point_source(ns,name,l0+dl*dx,m0+dm*dy));
  return model;

def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray(ns,ANTENNAS);
  # create an Observation object
  observation = Meow.Observation(ns);
  Meow.Context.set(array,observation);
    
  # make list of source lists for three crosses
  all_sources = grid_model(ns,'S0',0,0,grid_step*ARCMIN,grid_step*ARCMIN,grid_size);
    
  if sim_mode == "singlediff":
    # make Ejones for center position, and source #1
    Zj = iono_model.compute_zeta_jones(ns,all_sources[0:2],array,observation);
    # ...and only use source #1 throughout
    sources = [all_sources[1]]; 
  else:
    # make Ejones for all positions in master list
    Zj = iono_model.compute_zeta_jones(ns,all_sources,array,observation);
    sources = all_sources;  

  # build a "precise" model, by corrupting all sources with the Zj
  # for their direction
  prec_sky = Meow.Patch(ns,'prec',observation.phase_centre);
  for src in sources:
    corrupt_src = Meow.CorruptComponent(ns,src,label='Z',station_jones=Zj(src.direction.name));
    prec_sky.add(corrupt_src);

  # create set of nodes to compute visibilities...
  predict1 = prec_sky.visibilities(array,observation);
  
  if sim_mode == "corrupt":
    output = predict1;
  elif sim_mode == "diff" or sim_mode == "singlediff":
    # now make an approximate model using the center Zj to corrupt
    perfect_sky = Meow.Patch(ns,'approx',observation.phase_centre);
    perfect_sky.add(*sources);
    approx_sky = Meow.CorruptComponent(ns,perfect_sky,label='Z',station_jones=Zj(all_sources[0].direction.name));
    predict2 = approx_sky.visibilities(array,observation);
    output = ns.diff;
    for p,q in array.ifrs():
      output(p,q) << predict1(p,q) - predict2(p,q);
  elif sim_mode == "correct":
    # correct the predict with Zj of center
    output = ns.corrected;
    Meow.Jones.apply_correction(output,predict1,Zj(all_sources[0].direction.name),array.ifrs());

  # ...and attach them to sinks
  for p,q in array.ifrs():
    ns.sink(p,q) << Meq.Sink(output(p,q),station_1_index=p-1,station_2_index=q-1,output_col='DATA');
      
  # define VisDataMux
  ns.vdm << Meq.VisDataMux(*[ns.sink(p,q) for p,q in array.ifrs()]);
  

def _tdl_job_1_simulate_MS (mqs,parent):
  req = Meow.Utils.create_io_request();
  # execute    
  mqs.execute('vdm',req,wait=False);
  
  
def _tdl_job_2_make_image (mqs,parent):
  Meow.Utils.make_dirty_image(npix=1024,arcmin=(grid_size+1)*grid_step*2,channels=[32,1,1]);

# setup a few bookmarks
Settings.forest_state = record(bookmarks=[
  Meow.Bookmarks.PlotPage("TECS",["tec:S0+0+0:1","tec:S0+0+0:9"],
                                 ["tec:S0+1+1:1","tec:S0+1+1:9"]),
  Meow.Bookmarks.PlotPage("Z Jones",["Z:S0+0+0:1","Z:S0+0+0:9"],["Z:S0+1+1:1","Z:S1+1+1:9"])
]);


# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
