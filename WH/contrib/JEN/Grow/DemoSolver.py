# file: ../Grow/DemoSolver.py

# History:
# - 07sep2007: creation (from Plugin.py)

# Description:

"""The DemoSolver class makes makes a subtree that takes an input node and
produces a new rootnode by .....
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

import Meow

from Timba.Contrib.JEN.Grow import TwigDemo
from Timba.Contrib.JEN.Grow import TwigLeafParm
from Timba.Contrib.JEN.control import OptionManager
from Timba.Contrib.JEN.control import Executor

import math



#=============================================================================
#=============================================================================

class DemoSolver(TwigDemo.TwigDemo):
    """Class derived from TwigDemo"""

    def __init__(self, quals=None,
                 submenu='compile',
                 OM=None, namespace=None,
                 **kwargs):

        TwigDemo.TwigDemo.__init__(self,
                           quals=quals,
                           name='DemoSolver',
                           submenu=submenu,
                           OM=OM, namespace=namespace,
                           **kwargs)

        # Use the TwigLeafParm Plugin as the 'left-hand-side' of the equation(s).
        # It shares the OptionManager (OM), so the LeafParm menu is nested
        # in the TwigDemo menu by giving the correct subsub menu name.
        subsubmenu = submenu+'.'+self.name
        self._lhs = TwigLeafParm.TwigLeafParm (self._shortname,
                                               submenu=subsubmenu, OM=self._OM)
        return None


    #====================================================================

    def derivation_tree (self, ss, level=1):
        """Append the formatted derivation tree of this object to the string ss. 
        """
        ss += self.help_format(TwigDemo.TwigDemo.grow.__doc__, level=level)
        ss = TwigDemo.TwigDemo.derivation_tree(self, ss, level=level+1)
        return ss


    
    #====================================================================

    def define_compile_options(self, trace=True):
        """Specific: Define the compile options in the OptionManager.
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................
        self._OM.define(self.optname('niter'), 5,
                        prompt='nr of iterations',
                        opt=[1,2,3,5,10,20,30,50,100],
                        doc="""Nr of solver iterations.
                        """)
        # self._lhs.define_compile_options(trace=trace)
        #..............................................
        return self.on_exit(trace=trace)


    #--------------------------------------------------------------------

    def grow (self, ns, node, test=None, trace=True):
        """The DemoSolver class is derived from the TwigDemo class.
        It demonstrates the use of the MeqSolver node. Such a node has
        one or more MeqCondeq children, which generate condition equations
        for it by comparing 'measured' and 'predicted' inputs. The Solver
        then tries to minimise the differences (residuals) by varying the
        coefficients of one or more MeqParm parameter nodes, which are
        usually (but not necessarily) somewhere up the prediction branch.
        In this demo, the Solver has a single Condeq node, which compares
        the input node to a single MeqParm node.
        Clicking on the DemoSolver bookmark produces a page that shows the
        results of all the relevant nodes.
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, node, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        # Read the specified options:
        niter = self.optval('niter', test=test)

        # Make the subtree:
        lhs = self._lhs.grow(self.ns, trace=trace)
        condeq = self.ns['condeq'] << Meq.Condeq(lhs,node)
        parm = ns.Search(tags='solvable', class_name='MeqParm')
        solver = self.ns['solver'] << Meq.Solver(condeq,
                                                 num_iter=niter,
                                                 solvable=parm)
        node = self.ns['reqseq'] << Meq.ReqSeq(children=[solver,node],
                                               result_index=1)

        self.bookmark([parm[0], lhs, condeq, solver])

        #..............................................
        # Check the new rootnode:
        return self.on_output (node, trace=trace)





#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


pgt = None
if 0:
    xtor = Executor.Executor()
    # xtor.add_dimension('l', unit='rad')
    # xtor.add_dimension('m', unit='rad')
    pgt = DemoSolver()
    pgt.make_TDLCompileOptionMenu()
    # pgt.display()


def _define_forest(ns):

    global pgt,xtor
    if not pgt:
        xtor = Executor.Executor()
        pgt = DemoSolver()
        pgt.make_TDLCompileOptionMenu()

    cc = []

    # node = xtor.leafnode(ns)
    node = ns << Meq.Time() + Meq.Freq()
    rootnode = pgt.grow(ns, node)
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
    """Just display the current contents of the Demo object"""
    pgt.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the Demo object"""
    pgt.display('_tdl_job', full=True)
       


       



#===============================================================
# Test routine (without meqbrowser):
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        pgt = DemoSolver()
        pgt.display('initial')

    if 1:
        pgt.make_TDLCompileOptionMenu()

    if 1:
        node = ns << 1.0
        test = dict(niter=3)
        pgt.grow(ns, node, test=test, trace=True)

    if 1:
        pgt.display('final', OM=True, full=True)



#===============================================================

