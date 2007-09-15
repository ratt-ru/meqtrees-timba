# file: ../JEN/Grow/TwigLeafDimGrids.py

# History:
# - 14sep2007: creation (from Growth.py)

# Description:

"""The TwigLeafDimGrids class makes a subtree that represents a
combination (e.g. sum) of MeqGrid nodes for the selected
dimensions (e.g. freq. time, l, m, etc).
"""


#======================================================================================

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

# import Meow

from Timba.Contrib.JEN.Grow import TwigLeaf
from Timba.Contrib.JEN.control import OptionManager
from Timba.Contrib.JEN.control import Executor

# import math
# import random



#=============================================================================
#=============================================================================

class TwigLeafDimGrids(TwigLeaf.TwigLeaf):
    """Class derived from Plugin"""

    def __init__(self, quals=None,
                 submenu='compile',
                 xtor=None, dims=None,
                 OM=None, namespace=None,
                 **kwargs):

        TwigLeaf.TwigLeaf.__init__(self, quals=quals,
                           name='TwigLeafDimGrids',
                           submenu=submenu,
                           xtor=xtor, dims=dims,
                           OM=OM, namespace=namespace,
                           **kwargs)

        return None

    
    #====================================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = TwigLeaf.TwigLeaf.oneliner(self)
        return ss
    

    def display (self, txt=None, full=False, recurse=3, OM=True, level=0):
        """Print a summary of this object"""
        prefix = self.display_preamble(self.name, level=level, txt=txt)
        #...............................................................
        print prefix,'  * xxx'
        #...............................................................
        TwigLeaf.TwigLeaf.display(self, full=full,
                          recurse=recurse,
                          OM=OM, level=level+1)
        #...............................................................
        return self.display_postamble(prefix, level=level)

    
    #====================================================================


    def define_compile_options(self, trace=True):
        """Specific: Define the compile options in the OptionManager.
        This function must be re-implemented in derived TwigLeaf classes. 
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        # Optional (depends on the kind of TwigLeaf): 
        self._define_dims_options()
        self._define_combine_options()

        #..............................................
        return self.on_exit(trace=trace)



    #--------------------------------------------------------------------
    #--------------------------------------------------------------------

    def grow (self, ns, test=None, trace=True):
        """Specific: Make the plugin subtree.
        This function must be re-implemented in derived TwigLeaf classes. 
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        # Placeholder, to be replaced:
        rr = self.make_MeqGrid_nodes (trace=trace)
        node = self.combine_MeqGrid_nodes (rr, trace=trace)

        #..............................................
        # Finishing touches:
        return self.on_output (node, trace=trace)



    



#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


plf = None
if 0:
    xtor = Executor.Executor()
    xtor.add_dimension('l', unit='rad')
    xtor.add_dimension('m', unit='rad')
    plf = TwigLeafDimGrids(xtor=xtor)
    plf.make_TDLCompileOptionMenu()
    # plf.display('outside')


def _define_forest(ns):

    global plf,xtor
    if not plf:
        xtor = Executor.Executor()
        plf = TwigLeafDimGrids(xtor=xtor)
        plf.make_TDLCompileOptionMenu()

    cc = []

    # node = xtor.leafnode(ns)
    rootnode = plf.grow(ns)
    cc.append(rootnode)

    if len(cc)==0: cc.append(ns.dummy<<1.1)
    ns.result << Meq.Composer(children=cc)
    xtor.make_TDLRuntimeOptionMenu(node=ns.result)
    return True



#---------------------------------------------------------------

Settings.forest_state.cache_policy = 100

def _tdl_job_execute (mqs, parent):
    """Execute the forest with the specified options (domain etc),
    starting at the named node"""
    return xtor.execute(mqs, parent)
    
def _tdl_job_display (mqs, parent):
    """Just display the current contents of the Plugin object"""
    plf.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the Plugin object"""
    plf.display('_tdl_job', full=True)
       


       



#===============================================================
# Test routine (without meqbrowser):
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    xtor = None
    if 1:
        xtor = Executor.Executor()
        xtor.add_dimension('l', unit='rad')
        xtor.add_dimension('m', unit='rad')

    if 1:
        plf = TwigLeafDimGrids(xtor=xtor)
        plf.display('initial')

    if 1:
        plf.make_TDLCompileOptionMenu()

    if 1:
        test = dict()
        plf.grow(ns, test=test, trace=True)

    if 1:
        plf.display('final', OM=True, full=True)



#===============================================================

