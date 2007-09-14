# file: ../JEN/Grow/Branch.py

# History:
# - 14sep2007: creation (from Branch.py)

# Description:

"""The Branch class is derived from the Growth class. It allows the user to construct
a subtree that represents an entire branch, consisting an end-point (Leaf) and
an arbitrary sequence of modiying subtrees. It can also have side Branches, of course.
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

from Timba.Contrib.JEN.Grow import Growth
# from Timba.Contrib.JEN.Grow import Leaf
# from Timba.Contrib.JEN.Grow import Demo
# from Timba.Contrib.JEN.Grow import Twig
from Timba.Contrib.JEN.control import Executor

from Timba.Contrib.JEN.Grow import LeafConstant
from Timba.Contrib.JEN.Grow import LeafDimGrids
        
from Timba.Contrib.JEN.Grow import TwigApplyUnary
from Timba.Contrib.JEN.Grow import TwigAddNoise
from Timba.Contrib.JEN.Grow import TwigFlagger

from Timba.Contrib.JEN.Grow import DemoModRes
from Timba.Contrib.JEN.Grow import DemoRedaxes
from Timba.Contrib.JEN.Grow import DemoSolver

# import math
# import random



#=============================================================================
#=============================================================================

class Branch(Growth.Growth):
    """Class derived from Growth"""

    def __init__(self, quals=None,
                 name='Branch',
                 submenu='compile',
                 xtor=None, dims=None,
                 OM=None, namespace=None,
                 **kwargs):

        Growth.Growth.__init__(self, quals=quals,
                               name=name,
                               submenu=submenu,
                               has_input=False,
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
        self._OM.set_menurec(submenu, prompt='customize the selected Leaf')

        # Define the Growth sequence:
        self._plugin_order = []
        self._plugin = dict()
        submenu = self._submenu+'.Twig'
        self.define_plugin_sequence (submenu, trace=True)
        self._OM.set_menurec(submenu, prompt='customize the Growth sequence')

        # This function needs self._leaf.keys() etc:
        self._define_Branch_compile_options()

        # Execute the deferred function:
        self.define_compile_options()

        return None


    #====================================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = Growth.Growth.oneliner(self)
        return ss
    

    def display (self, txt=None, full=False, recurse=3, OM=True, level=0):
        """Print a summary of this object"""
        prefix = self.display_preamble(self.name, level=level, txt=txt)
        #...............................................................
        print prefix,'  * Choice of Leaves:'
        for key in self._leaf.keys():
            rr = self._leaf[key]
            print prefix,'    - '+key+': '+str(rr['leaf'].oneliner())
        #...............................................................
        print prefix,'  * Plugin sequence:'
        for key in self._plugin_order:
            rr = self._plugin[key]
            print prefix,'    - '+key+': '+str(rr['plugin'].oneliner())
        #...............................................................
        Growth.Growth.display(self, full=full,
                              recurse=recurse,
                              OM=OM, level=level+1)
        #...............................................................
        return self.display_postamble(prefix, level=level)


    #====================================================================
    # Generic part (base-class):
    #====================================================================


    def add_plugin(self, plugin, modes=None, trace=True):
        """
        Check the given Growth object, and add it to self._plugin.
        """
        
        if trace:
            print '\n** .add_plugin(',type(plugin),modes,'):'
            
        # print '** type Growth: ',isinstance(plugin, Growth.Growth)
        # print '** type Demo: ',isinstance(plugin, Demo.Demo)
            
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
            
        # print '** type Growth: ',isinstance(leaf, Growth.Growth)
        # print '** type Leaf: ',isinstance(leaf, Leaf.Leaf)
            
        # OK, add the valid leaf to the list:
        name = leaf.name
        self._leaf[name] = dict(leaf=leaf, modes=modes) 

        if trace:
            print '   ->',leaf.oneliner()
        return True


    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------

    def _define_Branch_compile_options(self, trace=True):
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
        node = rr['leaf'].grow(ns, trace=trace)
        print '    -> node =',str(node)

        if trace:
            print
        return node


    #---------------------------------------------------------------------------

    def append_plugin_sequence (self, ns, node=None, trace=False):
        """Append the specified (see .define_plugin_sequence()) sequence of Growth
        subtrees to the given node.
        """
        if trace:
            print '\n** .insert_plugin_chain(',str(node),'):'

        for key in self._plugin_order:
            rr = self._plugin[key]
            print '\n -',key,':',rr['plugin'].oneliner()
            node = rr['plugin'].grow(ns, node, trace=False)
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

    def grow (self, ns, test=None, trace=True):
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
        self.add_leaf (LeafConstant.LeafConstant(submenu=submenu, OM=self._OM))

        self.add_leaf (LeafDimGrids.LeafDimGrids(submenu=submenu, OM=self._OM,
                                                 xtor=self._xtor, dims=self._dims))
        return True


    #---------------------------------------------------------------------------

    def define_plugin_sequence (self, submenu, trace=True):
        """
        Define a specific sequence of plugins, to be used (or ignored)
        """
        self.add_plugin (TwigAddNoise.TwigAddNoise(submenu=submenu, OM=self._OM))
        self.add_plugin (TwigFlagger.TwigFlagger(submenu=submenu, OM=self._OM))
        self.add_plugin (TwigApplyUnary.TwigApplyUnary(submenu=submenu, OM=self._OM))
        
        self.add_plugin (DemoModRes.DemoModRes(submenu=submenu, OM=self._OM))
        self.add_plugin (DemoRedaxes.DemoRedaxes(submenu=submenu, OM=self._OM))
        self.add_plugin (DemoSolver.DemoSolver(submenu=submenu, OM=self._OM))

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
    rootnode = brn.grow(ns)
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
    """Just display the current contents of the Growth object"""
    brn.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the Growth object"""
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
        brn.grow(ns, test=test, trace=False)

    if 1:
        brn.display('final', OM=True, full=True)



#===============================================================

