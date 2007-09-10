# file: ../twigs/Demo.py

# History:
# - 10sep2007: creation (from LeafGrids.py)

# Description:

"""The Demo class makes makes a node/subtree that demonstrates
a particular feature of MeqTrees. It does this in a side-branch,
so the output result is equal to the input.
It is a base-class for specialised classes like DemoSolver,
DemoModRes etc, and is itself derived from the Plugin base-class.
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

from Timba.Contrib.JEN.twigs import Plugin
from Timba.Contrib.JEN.control import Executor

# import math
# import random



#=============================================================================
#=============================================================================

class Demo(Plugin.Plugin):
    """Base-class for DemoSomething classes, itself derived from Plugin"""

    def __init__(self, quals=None,
                 name='Demo',
                 submenu='compile',
                 OM=None, namespace=None,
                 **kwargs):

        Plugin.Plugin.__init__(self, quals=quals,
                               name=name,
                               submenu=submenu,
                               is_demo=True,
                               OM=OM, namespace=namespace,
                               **kwargs)

        return None



    
    #====================================================================
    # Specific part: Placeholders for specific functions:
    # (These must be re-implemented in derived Demo classes) 
    #====================================================================

    def define_compile_options(self, trace=True):
        """Specific: Define the compile options in the OptionManager.
        This function must be re-implemented in derived Demo classes. 
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        # Placeholder:
        self._OM.define(self.optname('xxx'), 45)

        #..............................................
        return self.on_exit(trace=trace)



    #--------------------------------------------------------------------
    #--------------------------------------------------------------------

    def make_subtree (self, ns, test=None, trace=True):
        """Specific: Make the plugin subtree.
        This function must be re-implemented in derived Demo classes. 
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, trace=trace):
            return self.bypass (trace=trace)
        #..............................................


        #..............................................
        # Finishing touches:
        return self.on_output (node, allnodes=cc, trace=trace)


    



#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


plf = None
if 1:
    xtor = Executor.Executor()
    # xtor.add_dimension('l', unit='rad')
    # xtor.add_dimension('m', unit='rad')
    # xtor.add_dimension('x', unit='m')
    # xtor.add_dimension('y', unit='m')

    plf = Demo(xtor=xtor)
    plf.make_TDLCompileOptionMenu()
    # plf.display('outside')


def _define_forest(ns):

    global plf,xtor
    if not plf:
        xtor = Executor.Executor()
        plf = Demo(xtor=xtor)
        plf.make_TDLCompileOptionMenu()

    cc = []

    rootnode = plf.make_subtree(ns)
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

    if 1:
        plf = Demo()
        plf.display('initial')

    if 1:
        plf.make_TDLCompileOptionMenu()

    if 1:
        test = dict()
        plf.make_subtree(ns, test=test, trace=True)

    if 1:
        plf.display('final', OM=True, full=True)



#===============================================================

