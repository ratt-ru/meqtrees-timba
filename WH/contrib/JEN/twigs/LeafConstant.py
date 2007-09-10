# file: ../twigs/LeafConstant.py

# History:
# - 09sep2007: creation (from Plugin.py)

# Description:

"""The LeafConstant class makes makes a subtree that represents either
a single MeqConstant (scalar node), or a 'tensor' node of constant
values.
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
from Timba.Contrib.JEN.control import OptionManager
from Timba.Contrib.JEN.control import Executor

import math
import random



#=============================================================================
#=============================================================================

class LeafConstant(Plugin.Plugin):
    """Class derived from Plugin"""

    def __init__(self,
                 quals=None, kwquals=None,
                 submenu='compile',
                 OM=None, namespace=None,
                 **kwargs):

        Plugin.Plugin.__init__(self, name='LeafConstant',
                               quals=quals, kwquals=kwquals,
                               submenu=submenu,
                               is_demo=False,
                               is_leaf=True,
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
        opt = [0.0,1.0,1+0j,1+1j,'pi','pi/2','c','e','k','G']
        self._OM.define(self.optname('value'), 1.0,
                        prompt='value',
                        opt=opt, more=str,
                        doc="""The value of the MeqConstant.
                        """)
        opt = [1,2,3,4,5,8,16,[2,2],[3,3],[4,4],[2,3],[1,2],[4,3,2]]
        self._OM.define(self.optname('dims'), 3,
                        prompt='(tensor) dims',
                        opt=opt, more=str,
                        doc="""Make a 'tensor' node with the specified
                        dimensions, with all different elements.
                        """)
        self._OM.define(self.optname('stddev'), 0.1,
                        prompt='scatter (stddev)',
                        opt=[0.0,0.1,1.0], more=float,
                        doc="""Add a random number (with gaussian distr) to
                        each tensor element (even if there is only one!),
                        around the nominal element value.
                        """)
        self._OM.define(self.optname('unop'), 'Negate',
                        prompt='apply unary',
                        opt=[None,'Negate'], more=str,
                        doc="""Apply an unary operation to the result.
                        """)
        #..............................................
        return self.on_exit(trace=trace)

    #--------------------------------------------------------------------
    #--------------------------------------------------------------------

    def make_subtree (self, ns, trace=True):
        """Specific: Make the plugin subtree.
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        # Read the specified options:
        value = self._read_value(trace=trace)
        dims = self._read_dims(trace=trace)
        stddev = self.optval('stddev')
        unop = self.optval('unop')

        # Determine the number of 'tensor' elements:
        nelem = 1
        for dim in dims:
            nelem *= dim
        print '** dims =',dims,' nelem=',nelem

        # Make the scalar/tensor node:
        if nelem<=0:
            s = '** invalid nelem ('+str(nelem)+')  dims='+str(dims)
            raise ValueError,s
        elif nelem==1:
            scat == self._scatter_value(value,stddev)
            node = self.ns['scalar'] << Meq.Constant(scat)
        else:
            vv = []
            for i in range(nelem):
                vv.append(self._scatter_value(value,stddev))
            node = ns['tensor'] << Meq.Composer(children=vv, dims=dims)

        # Optionally, apply a unary operation (e.g. Negate):
        if unop:
            node = self.ns << getattr(Meq,unop)(node)

        #..............................................
        # Finishing touches:
        return self.on_output (node, trace=trace)


    
    #------------------------------------------------------------------
    # Helper functions:
    #------------------------------------------------------------------

    def _scatter_value (self, value, stddev, trace=False):
        """Make a scattered value"""
        if stddev<=0.0:
            return value
        elif isinstance(value, complex):
            dr = random.gauss(0.0, stddev)
            di = random.gauss(0.0, stddev)
            return value+complex(dr,di)
        else:
            return random.gauss(value,stddev)

    #------------------------------------------------------------------

    def _read_value (self, trace=False):
        """Make sure that value is a number (float or complex)
        """
        value = self.optval('value')
        if isinstance(value,str):
            if value=='c':
                value = 3.0e8
            else:
                s = '** value not recognised: '+str(value)
                print s
                raise ValueError,s
        return value

    #------------------------------------------------------------------

    def _read_dims (self, trace=False):
        """Make sure that dims is a list of integers
        """
        dims = self.optval('dims')
        if isinstance(dims,int):
            dims = [dims]                 # e.g. [3]
        elif isinstance(dims,list):
            pass                          # already a list
        elif isinstance(dims,str):
            dims = self._OM._string2list (dims, length=None, trace=trace)
        else:
            s = '** dims type not recognised: '+str(type(dims))
            print s
            raise ValueError,s
        return dims



#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


plf = None
if 0:
    xtor = Executor.Executor('Executor', namespace='test',
                             parentclass='test')
    # xtor.add_dimension('l', unit='rad')
    # xtor.add_dimension('m', unit='rad')
    xtor.make_TDLCompileOptionMenu()
    plf = LeafConstant()
    plf.make_TDLCompileOptionMenu()
    # plf.display()


def _define_forest(ns):

    global plf,xtor
    if not plf:
        xtor = Executor.Executor()
        xtor.make_TDLCompileOptionMenu()
        plf = LeafConstant()
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
        plf = LeafConstant()
        plf.display('initial')

    if 1:
        plf.make_TDLCompileOptionMenu()

    if 1:
        plf.make_subtree(ns, trace=True)

    if 1:
        plf.display('final', OM=True, full=True)



#===============================================================

