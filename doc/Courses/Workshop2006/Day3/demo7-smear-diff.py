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

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[5,10]);
Meow.Utils.include_imaging_options();


# define antenna list
ANTENNAS = range(1,28);

# useful constant: 1 deg in radians
DEG = math.pi/180.;
ARCMIN = DEG/60;

# source flux (same for all sources)
I = 1; Q = .2; U = .2; V = .2;

# we'll put the sources on a cross (positions in arc min)
LM = [(-4, 0),(-2, 0),(0,0),(2,0),(4,0),
      ( 0,-4),( 0,-2),      (0,2),(0,4) ]; 

def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray(ns,ANTENNAS);
  # create an Observation object
  observation = Meow.Observation(ns);
  
  # create a Patch for the entire observed sky
  allsky = Meow.Patch(ns,'all',observation.phase_centre);
  allsky0 = Meow.Patch(ns,'all0',observation.phase_centre);

  # create 10 sources
  for isrc in range(len(LM)):
    l,m = LM[isrc];
    l *= ARCMIN;
    m *= ARCMIN;
    # generate an ID for direction and source
    src = 'S'+str(isrc);           
    src0 = 'S-'+str(isrc);           
    # create Direction object
    src_dir = Meow.LMDirection(ns,src,l,m);
    src_dir0 = Meow.LMDirection(ns,src0,l,m);
    # create point source with this direction
    source = Meow.PointSource(ns,src,src_dir,I=I,Q=Q,U=U,V=V);
    source0 = Meow.PointSource(ns,src+"0",src_dir0,I=I,Q=Q,U=U,V=V);
    # add to patch
    allsky.add(source);
    allsky0.add(source0);
  
  # create set of nodes to compute visibilities...
  predict = allsky.visibilities(array,observation);
  predict0 = allsky0.visibilities(array,observation);
  
  # ...and attach them to resamplers and sinks
  for p,q in array.ifrs():
    modres = ns.modres(p,q) << Meq.ModRes(predict(p,q),upsample=[5,5]);
    resamp = ns.resampler(p,q) << Meq.Resampler(modres,mode=2);
    ns.sink(p,q) << Meq.Sink(resamp-predict0(p,q),station_1_index=p-1,station_2_index=q-1,output_col='DATA');

  # define VisDataMux
  ns.vdm << Meq.VisDataMux(*[ns.sink(p,q) for p,q in array.ifrs()]);
  

def _tdl_job_1_simulate_MS (mqs,parent):
  req = Meow.Utils.create_io_request();
  # execute    
  mqs.execute('vdm',req,wait=False);
  
  
def _tdl_job_2_make_image (mqs,parent):
  Meow.Utils.make_dirty_image(npix=512,cellsize='1arcsec',channels=[32,1,1]);



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
