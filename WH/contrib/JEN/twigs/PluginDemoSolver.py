# file: ../twigs/PluginDemoSolver.py

# History:
# - 07sep2007: creation (from Plugin.py)

# Description:

"""The PluginDemoSolver class makes makes a subtree that takes an input node and
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

from Timba.Contrib.JEN.twigs import Plugin
from Timba.Contrib.JEN.control import OptionManager
from Timba.Contrib.JEN.control import Executor

import math



#=============================================================================
#=============================================================================

class PluginDemoSolver(Plugin.Plugin):
    """Class derived from Plugin"""

    def __init__(self,
                 quals=None, kwquals=None,
                 submenu='compile',
                 OM=None, namespace=None,
                 **kwargs):

        Plugin.Plugin.__init__(self, name='PluginDemoSolver',
                               quals=quals, kwquals=kwquals,
                               submenu=submenu,
                               is_demo=True,
                               OM=OM, namespace=namespace,
                               **kwargs)
        return None

    
    #====================================================================

    def define_compile_options(self, trace=True):
        """Specific: Define the compile options in the OptionManager.
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................
        self._OM.define(self.optname('niter'), None,
                        prompt='nr of iterations',
                        opt=[None,1,2,3,5,10,20,30,50,100],
                        doc="""Nr of solver iterations.
                        """)
        #..............................................
        return self.on_exit(trace=trace)

    #--------------------------------------------------------------------

    def make_subtree (self, ns, node, trace=True):
        """Specific: Make the plugin subtree.
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, node, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        # Read the specified options:
        niter = self.optval('niter')
        if niter==None or niter<1:
            return self.bypass (trace=trace)

        # Make the subtree:

        # Temporary:
        if True:
            time_deg = 2
            freq_deg = 2
            mparm = Meow.Parm(value=1.0,   
                              tiling=None,  
                              time_deg=time_deg,  
                              freq_deg=freq_deg,  
                              tags=['solvable'])   
            nodename = 'Meow.Parm[t'+str(time_deg)+',f'+str(freq_deg)+']'
            lhs = self.ns[nodename] << mparm.make()

        
        condeq = self.ns['condeq'] << Meq.Condeq(lhs,node)
        parm = ns.Search(tags='solvable', class_name='MeqParm')
        solver = self.ns['solver'] << Meq.Solver(condeq, num_iter=niter,
                                                 solvable=parm)
        node = self.ns['reqseq'] << Meq.ReqSeq(children=[solver,node],
                                               result_index=1)
 
        #..............................................
        # Check the new rootnode:
        return self.on_output (node, internodes=[parm[0], lhs, condeq, solver],
                               trace=trace)






    #====================================================================
    #====================================================================

    def submenu_demo_solver(self):
        """Define the options for an operation on the twig result"""
        name = 'solver'
        submenu = 'compile.demo.'+name
        self._OM.define(submenu+'.niter', None,
                        prompt='nr of iterations',
                        opt=[None,1,2,3,5,10,20,30,50,100],
                        doc="""Nr of solver iterations.
                        """)
        opt = ['demo_'+name, None]
        self._OM.define(submenu+'.bookpage', opt[0],
                        prompt='demo bookpage', opt=opt,
                        doc="""Make a 'local bookpage' for this demo.
                        """)
        self._OM.set_menu_prompt(submenu, 'solve for MeqParm coeff')
        self._demo[name] = dict(user_level=2)
        return True


    #--------------------------------------------------------------------
    # NB: This does not work. The MeqParm should not be in the twig,
    # but in the lhs....
    #--------------------------------------------------------------------

    def demo_solver (self, ns, node, trace=False):
        """Optionally, insert a solver to generate some flags"""
        name = 'solver'
        if not self._proceed_with_demo (ns, node, name): return node
        submenu = 'compile.demo.'+name+'.'
        niter = self._OM[submenu+'niter']
        if niter==None or niter<1:
            return node                               # not required

        qnode = ns['solver']
        lhs = self._make_xtor_hypercube(ns)           # left-hand side
        condeq = qnode('condeq') << Meq.Condeq(lhs,node)
        parm = ns.Search(tags='solvable', class_name='MeqParm')
        print '** parm =',str(parm[0])
        solver = qnode('solver') << Meq.Solver(condeq, num_iter=niter,
                                               solvable=parm)
        node = qnode('reqseq') << Meq.ReqSeq(children=[solver,node],
                                             result_index=1)
        
        # Optionally, bookmark the various relevant nodes.
        bookpage = self._OM[submenu+'bookpage']
        if bookpage:
            cc = [parm[0], lhs, condeq, solver]
            JEN_bookmarks.create(cc, page=bookpage, folder=self._folder())
        return self._check_node (node, submenu)




#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


pgt = None
if 0:
    xtor = Executor.Executor('Executor', namespace='test',
                             parentclass='test')
    # xtor.add_dimension('l', unit='rad')
    # xtor.add_dimension('m', unit='rad')
    xtor.make_TDLCompileOptionMenu()
    pgt = PluginDemoSolver()
    pgt.make_TDLCompileOptionMenu()
    # pgt.display()


def _define_forest(ns):

    global pgt,xtor
    if not pgt:
        xtor = Executor.Executor()
        xtor.make_TDLCompileOptionMenu()
        pgt = PluginDemoSolver()
        pgt.make_TDLCompileOptionMenu()

    cc = []

    node = xtor.leafnode(ns)
    rootnode = pgt.make_subtree(ns, node)
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
    pgt.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the Plugin object"""
    pgt.display('_tdl_job', full=True)
       


       



#===============================================================
# Test routine (without meqbrowser):
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        pgt = PluginDemoSolver()
        pgt.display('initial')

    if 1:
        pgt.make_TDLCompileOptionMenu()

    if 1:
        node = ns << 1.0
        pgt.make_subtree(ns, node, trace=True)

    if 1:
        pgt.display('final', OM=True, full=True)



#===============================================================

