# JEN_introduction.py:

# Demonstrates the following MeqTree features:
# - A simple tree 
# - Basic use of the meqbrowser
# - NB: This is all you need to get started!




 
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

Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []



#********************************************************************************
# The function under the 'blue button':
#********************************************************************************

def _define_forest (ns, **kwargs):
   """Definition of a 'forest' of one or more trees"""

   # Make two 'leaf' nodes that have some variation over freq/time. 
   a = ns.time << Meq.Time()
   b = ns.f_Hz << Meq.Freq()

   # Apply some math operations to get a more interesting result:
   b = ns << b*b/10
   a = ns << Meq.Cos(a)

   # The root node of the tree can have any name, but in this example it
   # should be named 'result', because this name is used in the execute
   # command (see below), and the bookmark.
   result = ns.result << Meq.Add(a,b)

   # Make a bookmark of the result node, for easy viewing:
   bm = record(name='result', viewer='Result Plotter',
               udi='/node/result', publish=True)
   Settings.forest_state.bookmarks.append(bm)

   # Finished:
   return True



#********************************************************************************
# The function under the TDL Exec button:
#********************************************************************************

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1,10,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=100, num_time=101)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       

#********************************************************************************
# Comments:
#********************************************************************************

# - Generate the tree nodes:
#   - Press the 'blue button' in the 'Tabbed Tools' panel

# - Explore the tree in the Trees panel:
#   - Expand 'Root nodes' into the full tree
#   - Click on any node in the tree, and notice its status record
#   - Relate the nodes to the Python code in _define_forest()
#     - Notice the node-names
#   - Expand the alternate views of 'All nodes' and 'By class'

# - Execute the tree:
#   - Click on TDL Exec item 'execute'
#   - Click 'result' in the Bookmarks menu
#     - Middle-click on the plot, to get cross-sections
#       Try to understand the four axes annotations
#     - Right-click on the plot and try the various plotting options
#     - Left-click on the plot and zoom in
#     - Play with the options in the top-left menu of the plot
#   - Click on the '?What's This' item in the meqbrowser Help menu,
#     and then on the plot. This gives a more complete description.    
#   - Study the code in _tdl_job_execute()
#     - Check the number of domain cells in the plot

# - Study the node status record:
#   - Open a new page in the Gridded Viewers panel (right)
#   - Left-click on any node in the tree -> its status record
#   - Right-click on the same node, and NEW Display with Result Plotter
#   - Relate the numbers in the cache result with the plot
#   - Guess at the meaning of the other fields in the status record.

# - Advanced features:
#   - Click on 'Forest State' in the Trees panel, and study the result
#   - Guess at the meaning of the fields in the forest state record

# - Experiment a little:
#   - The code in middle panel of the the browser may be edited
#     - Use a copy of this demo script
#   - Edit _tdl_job_execute() to change the request cells
#   - Edit _define_forest() to add a few nodes of your own  

#********************************************************************************
#********************************************************************************




