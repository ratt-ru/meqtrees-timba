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

import Meow
import Meow.StdTrees
import Meow.Utils

def _define_forest(ns):
  # enable standard MS options from Meow
  Meow.Utils.include_ms_options(
    channels=[[15,40,1]],tile_sizes=[100],
    has_output=False
  );
  TDLRuntimeMenu("Make image",
    *Meow.Utils.imaging_options(npix=256,arcmin=72));
  
  array = Meow.IfrArray.WSRT(ns);
  observation = Meow.Observation(ns);
  Meow.Context.set(array,observation);
  
  spigots = array.spigots();

  inspectors = [
    Meow.StdTrees.vis_inspector(ns.inspect_spigots,spigots)
  ];
  
  # make sinks and vdm
  Meow.StdTrees.make_sinks(ns,spigots,post=inspectors);
  

def _tdl_job_inspect_MS (mqs,parent,**kw):
  req = Meow.Utils.create_io_request();
  mqs.execute('VisDataMux',req,wait=False);





if __name__ == '__main__':
    Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);
    ns.Resolve();
    pass
              
