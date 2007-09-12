# file: ../twigs/Branch.py

# History:
# - 11sep2007: creation (from LeafDimGrids.py)

# Description:

"""The Branch class is derived from the Plugin. It allows the user to construct
a subtree that represents an entire branch, consisting an end-point (Leaf) and
an arbitrary sequence of modiying subtrees (Plugins). It can also have side
Branches, of course.
By sharing the same OptionManager, a Branch in all its arbitray complexity of
Plugins and side Branches, may be specified in full detail. Because of the large
number of options involved, a hierarchical system of 'modes' is supported.
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

from Timba.Contrib.JEN.twigs import Plugin
from Timba.Contrib.JEN.twigs import Leaf
from Timba.Contrib.JEN.twigs import Demo
# from Timba.Contrib.JEN.control import OptionManager
from Timba.Contrib.JEN.control import Executor

# import math
# import random



#=============================================================================
#=============================================================================

class Branch(Plugin.Plugin):
    """Class derived from Plugin"""

    def __init__(self, quals=None,
                 submenu='compile',
                 xtor=None, dims=None,
                 OM=None, namespace=None,
                 **kwargs):

        Plugin.Plugin.__init__(self, quals=quals,
                               name='Branch',
                               submenu=submenu,
                               is_Branch=True,
                               OM=OM, namespace=namespace,
                               defer_compile_options=True,
                               **kwargs)

        # Define the choice of Leaves:
        self._leaf = dict()
        self._dims = dims
        self._xtor = xtor
        submenu = self._submenu+'.Leaf'
        self._optname_selected_Leaf = 'Leaf.selected_Leaf'
        self.define_leaves (submenu, trace=True)
        self._OM.set_menu_prompt(submenu, 'customize the selected Leaf')

        # Define the Plugin sequence:
        self._plugin_order = []
        self._plugin = dict()
        submenu = self._submenu+'.Plugin'
        self.define_plugin_sequence (submenu, trace=True)
        self._OM.set_menu_prompt(submenu, 'customize the Plugin sequence')

        # This function needs self._leaf.keys() etc:
        self._define_generic_compile_options()

        # Execute the deferred function:
        self.define_compile_options()

        return None




    #====================================================================
    # Generic part (base-class):
    #====================================================================


    def add_plugin(self, plugin, modes=None, trace=True):
        """
        Check the given Plugin object, and add it to self._plugin.
        """
        
        if trace:
            print '\n** .add_plugin(',type(plugin),modes,'):'
            
        print '** type Plugin: ',isinstance(plugin, Plugin.Plugin)
        print '** type Demo: ',isinstance(plugin, Demo.Demo)
            
        # OK, add the valid plugin to the list:
        name = plugin.name
        self._plugin[name] = dict(plugin=plugin, modes=modes) 
        self._plugin_order.append(name)

        if trace:
            print '   ->',plugin.oneliner()
        return True


    #---------------------------------------------------------------------------

    def add_leaf(self, leaf, modes=None, trace=True):
        """
        Check the given Leaf object, and add it to self._leaf.
        """
        
        if trace:
            print '\n** .add_leaf(',type(leaf),modes,'):'
            
        print '** type Plugin: ',isinstance(leaf, Plugin.Plugin)
        print '** type Leaf: ',isinstance(leaf, Leaf.Leaf)
            
        # OK, add the valid leaf to the list:
        name = leaf.name
        self._leaf[name] = dict(leaf=leaf, modes=modes) 

        if trace:
            print '   ->',leaf.oneliner()
        return True


    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------

    def _define_generic_compile_options(self, trace=True):
        """Define some generic compile options for Branch.
        """
        opt = self._leaf.keys()
        self._OM.define(self.optname(self._optname_selected_Leaf),
                        opt[0], opt=opt,
                        prompt='select a Leaf',
                        callback=self._callback_leaf,
                        doc="""The tip of the Branch is a Leaf subtree.
                        """)

        return True


    #...................................................................

    def _callback_leaf (self, leaf):
        """Called whenever option 'Leaf' changes"""
        for key in self._leaf.keys():
            do_ignore = (not leaf==key)
            print '-- ignore leaf',key,':',do_ignore
            self._leaf[key]['leaf'].ignore(do_ignore)
        return True


    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------

    def make_leaf_subtree (self, ns, trace=False):
        """Make the subtree for the specified (see .define_leaves()) Leaf.
        """
        if trace:
            print '\n** .make_leaf_subtree():'

        key = self.optval(self._optname_selected_Leaf)
        rr = self._leaf[key]
        print '\n -',key,':',rr['leaf'].oneliner()
        node = rr['leaf'].make_subtree(ns, trace=trace)
        print '    -> node =',str(node)

        if trace:
            print
        return node


    #---------------------------------------------------------------------------

    def append_plugin_sequence (self, ns, node=None, trace=False):
        """Append the specified (see .define_plugin_sequence()) sequence of Plugin
        subtrees to the given node.
        """
        if trace:
            print '\n** .insert_plugin_chain(',str(node),'):'

        for key in self._plugin_order:
            rr = self._plugin[key]
            print '\n -',key,':',rr['plugin'].oneliner()
            node = rr['plugin'].make_subtree(ns, node, trace=False)
            print '    -> node =',str(node)

        if trace:
            print
        return node


    

    #====================================================================
    # Specific part (derived classes):
    #====================================================================


    def define_compile_options(self, trace=True):
        """Specific: Define the compile options in the OptionManager.
        This function must be re-implemented in derived Leaf classes. 
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................


        #..............................................
        return self.on_exit(trace=trace)


    #--------------------------------------------------------------------

    def make_subtree (self, ns, test=None, trace=True):
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

    def define_leaves (self, submenu, trace=True):
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

    def define_plugin_sequence (self, submenu, trace=True):
        """
        Define a specific sequence of plugins, to be used (or ignored)
        """
        if False:                                       # for testing only
            from Timba.Contrib.JEN.twigs import Plugin
            self.add_plugin (Plugin.PluginTest(submenu=submenu, OM=self._OM))

            from Timba.Contrib.JEN.twigs import PluginTemplate
            self.add_plugin (PluginTemplate.PluginTemplate(submenu=submenu, OM=self._OM))

        from Timba.Contrib.JEN.twigs import PluginAddNoise
        self.add_plugin (PluginAddNoise.PluginAddNoise(submenu=submenu, OM=self._OM))
        
        from Timba.Contrib.JEN.twigs import PluginApplyUnary
        self.add_plugin (PluginApplyUnary.PluginApplyUnary(submenu=submenu, OM=self._OM))

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
    xtor.add_dimension('l', unit='rad')
    xtor.add_dimension('m', unit='rad')
    brn = Branch(xtor=xtor)
    brn.make_TDLCompileOptionMenu()
    # brn.display('outside')


def _define_forest(ns):

    global brn,xtor
    if not brn:
        xtor = Executor.Executor()
        brn = Branch(xtor=xtor)
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
        brn = Branch()
        brn.display('initial')

    if 1:
        brn.make_TDLCompileOptionMenu()

    if 1:
        test = dict()
        brn.make_subtree(ns, test=test, trace=True)

    if 1:
        brn.display('final', OM=True, full=True)



#===============================================================

