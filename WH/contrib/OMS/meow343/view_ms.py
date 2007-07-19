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
from numarray import *
import os
import random

import Meow

from Meow import Bookmarks
from Meow import Utils

# number of stations
TDLCompileOption('num_stations',"Number of stations",[14,3],more=int);

def _define_forest(ns):
  # enable standard MS options from Meow
  Utils.include_ms_options(
    channels=[[15,40,1]],
    has_output=False,
  );

  array = Meow.IfrArray.WSRT(ns,num_stations);
  observation = Meow.Observation(ns);
  
  spigot = array.spigots();
  ns.inspector << \
      Meq.Composer(
        dims=(len(array.ifrs()),2,2),mt_polling=True,
        plot_label=[ "%s-%s"%(p,q) for p,q in array.ifrs() ],
        *[ ns.inspector(p,q) << Meq.Mean(spigot(p,q),reduction_axes="freq")
          for p,q in array.ifrs() ]
      );
  
  vdm = ns.VisDataMux << Meq.VisDataMux(post=ns.inspector);
  vdm.add_stepchildren(*[spigot(p,q) for p,q in array.ifrs()]);
  

def _test_forest (mqs,parent,**kw):
  req = Meow.Utils.create_io_request();
  mqs.execute('VisDataMux',req,wait=False);


Settings.forest_state = record(bookmarks=[
  record(name="Spigot inspector",viewer="Collections Plotter",udi="/node/inspector")
]);




Settings.forest_state.cache_policy = 1  # -1 for minimal, 1 for smart caching, 100 for full caching
Settings.orphans_are_roots = True

if __name__ == '__main__':


    Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);


    ns.Resolve();
    pass
              
