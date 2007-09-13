# file: ../twigs/BranchTemplate.py

# History:
# - 12sep2007: creation (from Branch.py)

# Description:

"""The BranchTemplate class can be used as a starting point for quickly making
classes that are derived from the Branch class.
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

from Timba.Contrib.JEN.twigs import Branch
from Timba.Contrib.JEN.twigs import Plugin
from Timba.Contrib.JEN.twigs import Leaf
from Timba.Contrib.JEN.twigs import Demo
from Timba.Contrib.JEN.control import Executor

# import math
# import random



#=============================================================================
#=============================================================================

class BranchTemplate(Branch.Branch):
    """Class derived from Branch"""

    def __init__(self, quals=None,
                 submenu='compile',
                 xtor=None, dims=None,
                 OM=None, namespace=None,
                 **kwargs):

        Branch.Branch.__init__(self, quals=quals,
                               name='BranchTemplate',
                               submenu=submenu,
                               OM=OM, namespace=namespace,
                               **kwargs)

        return None




    #====================================================================
    # Specific part (derived classes):
    #====================================================================


    def define_compile_options(self, trace=False):
        """Specific: Define the compile options in the OptionManager.
        This function must be re-implemented in derived Leaf classes. 
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        #..............................................
        return self.on_exit(trace=trace)


    #--------------------------------------------------------------------

    def make_subtree (self, ns, test=None, trace=False):
        """Specific: Make the plugin subtree.
        This function must be re-implemented in derived Leaf classes. 
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        node = self.make_leaf_subtree (ns, trace=trace)
        node = self.append_plugin_sequence (ns, node, trace=trace)

        #..............................................
        # Finishing touches:
        return self.on_output (node, trace=trace)


    #---------------------------------------------------------------------------

    def define_leaves (self, submenu, trace=False):
        """
        Define a choice of Leaf classe, to be used at the tip of the Branch.
        """
        if False:                                            # for testing only
            from Timba.Contrib.JEN.twigs import LeafTemplate
            self.add_leaf (LeafTemplate.LeafTemplate(submenu=submenu, OM=self._OM))

        from Timba.Contrib.JEN.twigs import LeafConstant
        self.add_leaf (LeafConstant.LeafConstant(submenu=submenu, OM=self._OM))

        from Timba.Contrib.JEN.twigs import LeafParm
        self.add_leaf (LeafParm.LeafParm(submenu=submenu, OM=self._OM))

        from Timba.Contrib.JEN.twigs import LeafDimGrids
        self.add_leaf (LeafDimGrids.LeafDimGrids(submenu=submenu, OM=self._OM,
                                                 xtor=self._xtor, dims=self._dims))
        return True


    #---------------------------------------------------------------------------

    def define_plugin_sequence (self, submenu, trace=False):
        """
        Define a specific sequence of plugins, to be used (or ignored)
        """
        if False:                                       # for testing only
            from Timba.Contrib.JEN.twigs import Plugin
            self.add_plugin (Plugin.PluginTest(submenu=submenu, OM=self._OM))

            from Timba.Contrib.JEN.twigs import PluginTemplate
            self.add_plugin (PluginTemplate.PluginTemplate(submenu=submenu, OM=self._OM))

        from Timba.Contrib.JEN.twigs import PluginApplyUnary
        self.add_plugin (PluginApplyUnary.PluginApplyUnary(submenu=submenu, OM=self._OM))

        from Timba.Contrib.JEN.twigs import PluginAddNoise
        self.add_plugin (PluginAddNoise.PluginAddNoise(submenu=submenu, OM=self._OM))
        
        from Timba.Contrib.JEN.twigs import PluginFlagger
        self.add_plugin (PluginFlagger.PluginFlagger(submenu=submenu, OM=self._OM))

        from Timba.Contrib.JEN.twigs import DemoSolver
        self.add_plugin (DemoSolver.DemoSolver(submenu=submenu, OM=self._OM))

        from Timba.Contrib.JEN.twigs import DemoModRes
        self.add_plugin (DemoModRes.DemoModRes(submenu=submenu, OM=self._OM))

        from Timba.Contrib.JEN.twigs import DemoRedaxes
        self.add_plugin (DemoRedaxes.DemoRedaxes(submenu=submenu, OM=self._OM))

        return True



    



#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


brn = None
if 1:
    xtor = Executor.Executor()
    # xtor.add_dimension('l', unit='rad')
    # xtor.add_dimension('m', unit='rad')
    brn = BranchTemplate(xtor=xtor)
    brn.make_TDLCompileOptionMenu()
    # brn.display('outside')


def _define_forest(ns):

    global brn,xtor
    if not brn:
        xtor = Executor.Executor()
        brn = BranchTemplate(xtor=xtor)
        brn.make_TDLCompileOptionMenu()

    cc = []

    # node = xtor.leafnode(ns)
    rootnode = brn.make_subtree(ns)
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
    brn.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the Plugin object"""
    brn.display('_tdl_job', full=True)
       


       



#===============================================================
# Test routine (without meqbrowser):
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        brn = BranchTemplate()
        brn.display('initial')

    if 1:
        brn.make_TDLCompileOptionMenu()

    if 1:
        test = dict()
        brn.make_subtree(ns, test=test, trace=False)

    if 1:
        brn.display('final', OM=True, full=True)



#===============================================================

