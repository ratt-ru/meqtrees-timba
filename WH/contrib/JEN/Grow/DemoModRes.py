# file: ../Grow/DemoModRes.py

# History:
# - 07sep2007: creation (from Plugin.py)

# Description:

"""The DemoModRes class makes makes a subtree that takes an input node and
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

class DemoModRes(TwigDemo.TwigDemo):
    """Class derived from TwigDemo"""

    def __init__(self,
                 quals=None,
                 submenu='compile',
                 OM=None, namespace=None,
                 **kwargs):

        TwigDemo.TwigDemo.__init__(self, name='DemoModRes',
                           quals=quals,
                           submenu=submenu,
                           OM=OM, namespace=namespace,
                           **kwargs)
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
        opt = [[2,3],[3,2],[3,4],[4,5]]
        self._OM.define(self.optname('num_cells'), opt[0],
                        prompt='nr of cells [nt,nf]',
                        opt=opt, more=str,
                        doc="""Covert the REQUEST to a lower a resolution.
                        """)
        self._OM.define(self.optname('resamp_mode'), 1,
                        prompt='resampler mode',
                        opt=[1,2],
                        doc="""Mode 2 only works with time,freq domains.
                        """)
        #..............................................
        return self.on_exit(trace=trace)

    #--------------------------------------------------------------------

    def grow (self, ns, node, test=None, trace=True):
        """The DemoModRes class is derived from the TwigDemo class.
        It demonstrates ....
        Clicking on the DemoModRes bookmark produces a page that shows the
        results of all the relevant nodes.
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, node, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        # Read the specified options:
        num_cells = self.optval('num_cells', test=test)
        num_cells = self._OM._string2list(num_cells, length=None)
        rmode = self.optval('resamp_mode', test=test)

        # Make a side-branch that first lowers the resolution (modres),
        # by simply lowering the resolution of the request
        # then resamples the result to the the original resolution,
        # and then takes the difference with the original input to
        # check the quality of the two operations.
        original = self.ns['original'] << Meq.Identity(node) 
        modres = self.ns['modres'] << Meq.ModRes(node, num_cells=num_cells) 
        resampled = self.ns['resampled'] << Meq.Resampler(modres, mode=rmode) 
        diff = self.ns['diff'] << Meq.Subtract(resampled,original) 

        # The reqseq issues a (full-resolution) request first to the
        # branch that changes the resolution back and forth, and then to the
        # branch that holds the original resolution. Since it
        # is only a demonstration, the original result (1) is passed on.
        node = self.ns['reqseq'] << Meq.ReqSeq(diff,original,
                                               result_index=1)
        self.bookmark([modres,resampled,diff]) 
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
    pgt = DemoModRes()
    pgt.make_TDLCompileOptionMenu()
    # pgt.display()


def _define_forest(ns):

    global pgt,xtor
    if not pgt:
        xtor = Executor.Executor()
        pgt = DemoModRes()
        pgt.make_TDLCompileOptionMenu()

    cc = []

    node = ns << 1.0
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
        pgt = DemoModRes()
        pgt.display('initial')

    if 1:
        pgt.make_TDLCompileOptionMenu()

    if 1:
        node = ns << 1.0
        test = dict(num_cells=[2,4])
        pgt.grow(ns, node, test=test, trace=True)

    if 1:
        pgt.display('final', OM=True, full=True)



#===============================================================

