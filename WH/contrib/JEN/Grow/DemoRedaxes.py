# file: ../Grow/DemoRedaxes.py

# History:
# - 07sep2007: creation (from Plugin.py)

# Description:

"""The DemoRedaxes class makes makes a subtree that takes an input node and
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

from Timba.Contrib.JEN.Grow import TwigDemo
from Timba.Contrib.JEN.control import OptionManager
from Timba.Contrib.JEN.control import Executor

import math



#=============================================================================
#=============================================================================

class DemoRedaxes(TwigDemo.TwigDemo):
    """Class derived from Demo"""

    def __init__(self,
                 quals=None,
                 submenu='compile',
                 OM=None, namespace=None,
                 **kwargs):

        TwigDemo.TwigDemo.__init__(self, name='DemoRedaxes',
                                   quals=quals,
                                   submenu=submenu,
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
        opt = ['Sum','Product','StdDev','Rms','Mean','Max','Min','*']
        self._OM.define(self.optname('oper'), opt[0],
                        prompt='select a math operation',
                        opt=opt, more=str,
                        doc="""Select the math oper.
                        """)
        opt = ['*','time','freq',['time','freq'],None]
        self._OM.define(self.optname('redaxes'), '*',
                        prompt='reduction axes',
                        opt=opt, more=str,
                        doc="""The reduction axes:
                        """)
        #..............................................
        return self.on_exit(trace=trace)

    #--------------------------------------------------------------------

    def grow (self, ns, node, test=None, trace=True):
        """Specific: Make the plugin subtree.
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, node, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        # Read the specified options:
        oper = self.optval('oper', test=test)
        redaxes = self.optval('redaxes', test=test)

        # Make the subtree:
        qnode = self.ns[oper]
        cc = []
        cc.append(qnode('reduce_all') << getattr(Meq,oper)(node))
        cc.append(qnode('reduce_time') << getattr(Meq,oper)(node, reduction_axes=['time']))
        cc.append(qnode('reduce_freq') << getattr(Meq,oper)(node, reduction_axes=['freq']))
        node = qnode('reqseq') << Meq.ReqSeq(children=[node]+cc, result_index=0)

        self.bookmark(cc)
        #..............................................
        # Finishing touches:
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
    pgt = DemoRedaxes()
    pgt.make_TDLCompileOptionMenu()
    # pgt.display()


def _define_forest(ns):

    global pgt,xtor
    if not pgt:
        xtor = Executor.Executor()
        pgt = DemoRedaxes()
        pgt.make_TDLCompileOptionMenu()

    cc = []

    node = ns << 1
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
        pgt = DemoRedaxes()
        pgt.display('initial')

    if 1:
        pgt.make_TDLCompileOptionMenu()

    if 1:
        node = ns << 1.0
        test = dict(oper='Mean')
        pgt.grow(ns, node, test=test, trace=True)

    if 1:
        pgt.display('final', OM=True, full=True)



#===============================================================

