# JEN_zerotest. py:


#********************************************************************************
# Initialisation:
#********************************************************************************

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

from Timba.Contrib.JEN.util import JEN_bookmarks

Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []


#********************************************************************************
# The function under the 'blue button':
#********************************************************************************

def _define_forest (ns, **kwargs):
   """Test of zerotest(node) function"""

   # Make a node that produces some variation in two dimensions(f,t):
   y = ns.y << Meq.Time()
   x = ns.x << Meq.Freq()
   xy = ns.xy << Meq.Add(x,y)

   # Apply zerotest() to various nodes whose result should be zero.
   # Collect these nodes into a vector cc (to be added below)
   cc = []
   cc.append(zerotest(ns, ns << Meq.Subtract(xy,xy)), recurse=2)
   cc.append(zerotest(ns, ns << Meq.Multiply(xy,xy)), recurse=3)

   # Do a final zerotest on the sum of all zerotest nodes (in cc).
   # The name of the sum node should be used in _tdl_job_execute() below.
   zerotest(ns, ns.zerotest << Meq.Add(children=cc))

   # Finished:
   return True




#===============================================================================
# Function to be called by other zerotest functions:
#===============================================================================

def zerotest(ns, node, recurse=1):
   """This function is to be called from zerotest functions."""
   
   # Make a bookmark to plot the given node. It should be bright green(=0).
   # The argument recurse=1 causes its children to be plotted also.
   JEN_bookmarks.create(node, recurse=recurse)

   # Make a bookmark of the root node on its own:
   if node.name=='zerotest':
      JEN_bookmarks.create(node)

   # Return the input node.
   return node



#********************************************************************************
# The function under the TDL Exec button:
#********************************************************************************

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1,10,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='zerotest', request=request))
    return result
       

#********************************************************************************
#********************************************************************************


