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

import iono_model
import sky_models

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[8,16,32]);
# note how we set default image size based on grid size/step
TDLRuntimeMenu("Imaging options",
    *Meow.Utils.imaging_options(npix=512,arcmin=sky_models.imagesize(),channels=[[32,1,1]]));

TDLCompileOption("noise_stddev","Add noise, Jy",[None,1e-6,1e-3],more=float);


# define antenna list
ANTENNAS = range(1,27+1);

def noise_matrix (stddev=0.1):
  """helper function to create a 2x2 complex gaussian noise matrix""";
  noise = Meq.GaussNoise(stddev=stddev);
  return Meq.Matrix22(
    Meq.ToComplex(noise,noise),Meq.ToComplex(noise,noise),
    Meq.ToComplex(noise,noise),Meq.ToComplex(noise,noise)
  );

def _define_forest (ns):
  array = Meow.IfrArray(ns,ANTENNAS);
  observation = Meow.Observation(ns);
  Meow.Context.set(array,observation);
    
  # create source list
  sources = sky_models.make_model(ns,"S0");
    
  # make Zjones for all positions in source list (and all stations)
  # this returns Zj which sould be qualified as Zj(srcname,station)
  # Therefore we can use Zj(srcname) as a per-stations Jones series.
  Zj = iono_model.compute_zeta_jones(ns,sources);

  # corrupt all sources with the Zj for their direction
  allsky = Meow.Patch(ns,'sky',observation.phase_centre);
  for src in sources:
    allsky.add(src.corrupt(Zj(src.direction.name)));

  # get predicted visibilities
  predict = allsky.visibilities();
  
  # throw in a bit of noise
  if noise_stddev:
    for p,q in array.ifrs():
      ns.noisy_predict(p,q) << predict(p,q) + noise_matrix(noise_stddev); 
    predict = ns.noisy_predict;
      
  # Make some inspectors.
  # These are the "interesting" stations:
  # 10 is center of array, 9, 18 and 27 are at the end of the arms.
  # Make composers for them
  stas = [ 10,9,18,27 ];
  # make a couple of composers, for visualizations
  inspectors = [
    ns.inspect_tecs << \
      Meq.Composer(
        plot_label = [ "%s:%s"%(p,src.name) for src in sources for p in stas ],
        *[ ns.tec(src.name,p) for src in sources for p in stas ]
      ),
    ns.inspect_Z << \
      Meq.Composer(
        plot_label = [ "%s:%s"%(p,src.name) for src in sources for p in stas ],
        *[ Meq.Mean(Meq.Arg(ns.Z(src.name,p),reduction_axes="freq")) for src in sources for p in stas ]
      )
  ];
  
  # make sinks and vdm. Note that we don't want to make any spigots...
  # The list of inspectors comes in handy here
  Meow.StdTrees.make_sinks(ns,predict,spigots=False,post=inspectors);
  
  # and make some more interesting bookmarks
  Meow.Bookmarks.Page("Inspect TECs").add(ns.inspect_tecs,viewer="Collections Plotter");
  Meow.Bookmarks.Page("Inspect Z").add(ns.inspect_Z,viewer="Collections Plotter");
  
  # 10 is center of array, 9, 18 and 27 are at the end of the arms
  stas = [10,9,18,27 ];
  for p in stas:
    pg = Meow.Bookmarks.Page("TECs, station "+str(p),2,2);
    for src in sources[:4]:
      pg.add(ns.tec(src.name,p));
  for p in stas:
    pg = Meow.Bookmarks.Page("Z Jones, station "+str(p),2,2);
    for src in sources[:4]:
      pg.add(ns.Z(src.name,p));
  


def _tdl_job_1_simulate_MS (mqs,parent,wait=False):
  req = Meow.Utils.create_io_request();
  # execute    
  mqs.execute('VisDataMux',req,wait=wait);
  
  
# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
