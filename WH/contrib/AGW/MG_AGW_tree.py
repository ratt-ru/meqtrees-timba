# script_name = 'MG_AGW_tree.py'

# Short description:
#   Creates a very basic MeqTree with a Solver

# Keywords: ....

# Author: Tony Willis (AGW), DRAO

# History:
# - 10 jan 2006: added copyright
# - 04 jan 2006: first version checked in

# Copyright: The MeqTree Foundation

# standard preamble

#% $Id$ 

#
# Copyright (C) 2002-2007
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

from Timba.TDL import *
from Timba.Meq import meq
from Timba.Meq import meqds
from numarray import *
 
# Timba.TDL.Settings.forest_state is a standard TDL name. 
# This is a record passed to Set.Forest.State. 
Settings.forest_state.cache_policy = 100;

# Make sure our solver root node is not cleaned up
Settings.orphans_are_roots = True;

def _define_forest (ns):
  """define_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, this method is automatically called to
  define the forest. The 'ns' argument is a NodeScope object in which
  the forest is to be defined, usually this is simply the global scope.
  """;
  
# This an adaption of the glish script agw_tree.g, originally 
# written for the 'Meqs for Dummys' document, into a corresponding
# python 'tdl' script
 
# first create 2x2 polc
# The 'polc' array will be used to store the coefficients a,b,c,d
# for the polynomial fit in x and y (a +bx +cy +dxy) that we will do below
  polc_array = zeros((2,2), Float64)
# initially we guess the coefficients a=1, and b,c,d = 0
  polc_array[0,0] = 1.0

# we now create a leaf called 'coeff' which is of type MeqParm and contains
# the polc_array we created previously. 
  ns['coeff'] << Meq.Parm(polc_array,node_groups='Parm')

# now create a leaf MeqFreq node called 'freq' which has no children
  ns['freq'] << Meq.Freq()

# create a leaf MeqTime node called 'time' which has no children
  ns['time'] << Meq.Time()

# create a MeqAdd node called 'add' which has the children 'freq' and
# 'time'. As its name indicates it will add the contents of 'freq' and
# 'time' together.
  ns['add'] << Meq.Add(ns['freq'],ns['time'])

# create a MeqCondeq node called 'condeq'. A MeqCondeq compares the
# contents of the 'add' and 'coeff' nodes
  ns['condeq'] <<Meq.Condeq(ns['add'],ns['coeff'])

# finally create a solver
  ns['solver'] << Meq.Solver(
      num_iter=3,debug_level=10,solvable="coeff", children = ns['condeq'])

def _test_forest (mqs,parent,wait=False):
  """test_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, and the "test" option is set to true,
  this method is automatically called after define_forest() to run a 
  test on the forest. The 'mqs' argument is a meqserver proxy object.
  """;
# we create a time-frequency 'domain' with range 0 to 2 in frequency and
# 0 to 1 in time.
# Split the domain into a 8 x 4 "cells' array in time and
# frequency. The frequency range will be split into 8 increments,
# while the time range will be split into 4 increments
# time
  cells = meq.cells(meq.domain(0,2,0,1),num_freq=8,num_time=4);
  # execute request on solver
  request = meq.request(cells,rqtype='e1')
#  mqs.meq('Node.Set.Breakpoint',record(name='solver'));
#  mqs.meq('Debug.Set.Level',record(debug_level=100));
  a = mqs.meq('Node.Execute',record(name='solver',request=request),wait=wait);


# The following is the testing branch, executed when the script is run directly
# via 'python script.py'

if __name__ == '__main__':
 # run in batch mode?
 if '-run' in sys.argv:
   from Timba.Apps import meqserver
   from Timba.TDL import Compile

   # this starts a kernel.
   mqs = meqserver.default_mqs(wait_init=10);

   # This compiles a script as a TDL module. Any errors will be thrown as
   # an exception, so this always returns successfully. We pass in
   # __file__ so as to compile ourselves.
   (mod,ns,msg) = Compile.compile_file(mqs,__file__);

   # this runs the _test_forest job.
   mod._test_forest(mqs,None,wait=True);
 else:
  Timba.TDL._dbg.set_verbose(5);
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())

