# script_name = 'MG_AGW_history.py'

#% $Id: MG_AGW_history.py 4050 2006-10-02 21:20:50Z twillis $ 

#
# Copyright (C) 2006
# ASTRON (Netherlands Foundation for Research in Astronomy)
# and The MeqTree Foundation
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# Short description:
#   Demos the HistoryCollect Node

# Keywords: ....

# Author: Tony Willis (AGW), DRAO

# History:
# - 04 oct 2006: first version checked in

# Copyright: The MeqTree Foundation

# standard preamble

from Timba.TDL import *
from Timba.Meq import meq
from Timba.Meq import meqds
from Timba.Contrib.JEN.util import JEN_bookmarks
from numarray import *
 
# Timba.TDL.Settings.forest_state is a standard TDL name. 
# This is a record passed to Set.Forest.State. 
Settings.forest_state.cache_policy = 100;

# Make sure our solver root node is not cleaned up
Settings.orphans_are_roots = True;

global counter , request_number
counter = 1.0
request_number = 1

def _define_forest (ns):
  """define_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, this method is automatically called to
  define the forest. The 'ns' argument is a NodeScope object in which
  the forest is to be defined, usually this is simply the global scope.
  """;
  global counter
 
# first create GaussNoise node
  ns['noise'] <<Meq.GaussNoise(stddev=1.0)
  amplified_noise = ns << ns['noise'] * counter
  JEN_bookmarks.create (amplified_noise, viewer='Result Plotter', page="demo")
  input_index = hiid('VellSets/0/Value')
  ns['history'] <<Meq.HistoryCollect(amplified_noise,  verbose=True,
                         input_index=input_index, top_label=hiid('history'))
  JEN_bookmarks.create (ns['history'], viewer='History Plotter', page="demo")

def _test_forest (mqs,parent):
  """test_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, and the "test" option is set to true,
  this method is automatically called after define_forest() to run a 
  test on the forest. The 'mqs' argument is a meqserver proxy object.
  """;
  global counter, request_number
# we create a time-frequency 'domain' with range 0 to 2 in frequency and
# 0 to 1 in time.
# Split the domain into a 16 x 8 "cells' array in time and
# frequency. The frequency range will be split into 16 increments,
# while the time range will be split into 8 increments
# time
  cells = meq.cells(meq.domain(0,2,0,1),num_freq=16,num_time=8);
  for i in range(5):
    rqid = meq.requestid(domain_id=request_number)
    request = meq.request(cells,rqtype='ev',rqid=rqid)
    a = mqs.meq('Node.Execute',record(name='history',request=request),wait=True);
    counter = counter * 2
    request_number = request_number + 1


# The following is the testing branch, executed when the script is run directly
# via 'python script.py'

if __name__ == '__main__':
#  from Timba.Meq import meqds 
  Timba.TDL._dbg.set_verbose(5);
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();
