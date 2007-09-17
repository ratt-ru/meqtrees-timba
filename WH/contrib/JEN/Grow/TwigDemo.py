# file: ../JEN/Grow/TwigDemo.py

# History:
# - 14sep2007: creation (from TwigDemo.py)

# Description:

"""The TwigDemo class makes makes a node/subtree that demonstrates
a particular feature of MeqTrees. It does this in a side-branch,
so the output result is equal to the input.
It is a base-class for specialised classes like TwigDemoSolver,
TwigDemoModRes etc, and is itself derived from the Plugin base-class.
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

from Timba.Contrib.JEN.Grow import Twig
from Timba.Contrib.JEN.control import Executor

# import math
# import random



#=============================================================================
#=============================================================================

class TwigDemo(Twig.Twig):
    """Base-class for TwigDemoSomething classes, itself derived from Twig"""

    def __init__(self, quals=None,
                 name='TwigDemo',
                 submenu='compile',
                 OM=None, namespace=None,
                 **kwargs):

        Twig.Twig.__init__(self, quals=quals,
                           name=name,
                           submenu=submenu,
                           toggle=True,
                           OM=OM, namespace=namespace,
                           **kwargs)

        return None


    #====================================================================

    def derivation_tree (self, ss, level=1):
        """Append the formatted derivation tree of this object to the string ss. 
        """
        ss += self.help_format(Twig.Twig.grow.__doc__, level=level)
        ss = Twig.Twig.derivation_tree(self, ss, level=level+1)
        return ss

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = Twig.Twig.oneliner(self)
        return ss
    

    def display (self, txt=None, full=False, recurse=3, OM=True, level=0):
        """Print a summary of this object"""
        prefix = self.display_preamble(self.name, level=level, txt=txt)
        #...............................................................
        #...............................................................
        Twig.Twig.display(self, full=full,
                          recurse=recurse,
                          OM=OM, level=level+1)
        #...............................................................
        return self.display_postamble(prefix, level=level)



    
    #====================================================================
    # Specific part: Placeholders for specific functions:
    # (These must be re-implemented in derived TwigDemo classes) 
    #====================================================================

    def define_compile_options(self, trace=False):
        """Specific: Define the compile options in the OptionManager.
        This function must be re-implemented in derived TwigDemo classes. 
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................


        #..............................................
        return self.on_exit(trace=trace)



    #--------------------------------------------------------------------
    #--------------------------------------------------------------------

    def grow (self, ns, node, test=None, trace=False):
        """The TwigDemo class is derived from the Twig class.
        It is the baseclass for a family of classes that demonstrate the
        working of some of the more advanced MeqTree node classes, like
        the Solver, the ModRes and Resampler, the Compounder etc.
        A TwigDemo is implemented as a side-branch, so it does NOT change
        the input result (although the output node will have the name of
        the ReqSeq node that is used to issue requests to the side-branch).
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, node, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        result = node

        #..............................................
        # Finishing touches:
        return self.on_output (result, trace=trace)


    



#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


plf = None
if 0:
    xtor = Executor.Executor()
    # xtor.add_dimension('l', unit='rad')
    # xtor.add_dimension('m', unit='rad')
    # xtor.add_dimension('x', unit='m')
    # xtor.add_dimension('y', unit='m')
    plf = TwigDemo()
    plf.make_TDLCompileOptionMenu()
    # plf.display('outside')


def _define_forest(ns):

    global plf,xtor
    if not plf:
        xtor = Executor.Executor()
        plf = TwigDemo()
        plf.make_TDLCompileOptionMenu()

    cc = []

    node = ns << 1.2
    rootnode = plf.grow(ns, node)
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
    """Just display the current contents of the Twig object"""
    plf.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the Twig object"""
    plf.display('_tdl_job', full=True)
       


       



#===============================================================
# Test routine (without meqbrowser):
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        plf = TwigDemo()
        plf.display('initial')

    if 1:
        plf.make_TDLCompileOptionMenu()

    if 1:
        node = ns << 1.2
        test = dict()
        plf.grow(ns, node, test=test, trace=False)

    if 1:
        plf.display('final', OM=True, full=True)



#===============================================================

