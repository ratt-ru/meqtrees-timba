# file: ../twigs/LeafGrids.py

# History:
# - 07sep2007: creation (from Plugin.py)

# Description:

"""The LeafGrids class makes makes a subtree that represents a
combination (e.g. sum) of MeqGrid nodes for the selected
dimensions (e.g. freq. time, l, m, etc).
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
from Timba.Contrib.JEN.control import OptionManager
from Timba.Contrib.JEN.control import Executor

# import math
# import random



#=============================================================================
#=============================================================================

class LeafGrids(Plugin.Plugin):
    """Class derived from Plugin"""

    def __init__(self,
                 quals=None, kwquals=None,
                 submenu='compile',
                 xtor=None,
                 OM=None, namespace=None,
                 **kwargs):

        Plugin.Plugin.__init__(self, name='LeafGrids',
                               quals=quals, kwquals=kwquals,
                               submenu=submenu,
                               is_demo=False,
                               is_leaf=True,
                               OM=OM, namespace=namespace,
                               **kwargs)

        # The list of available dimensions may be obtained
        # from an external Executor object (if supplied):
        self._xtor = xtor
        self._available_dims = ['freq','time']         # default available dims
        if self._xtor:
            self._available_dims = self._xtor.dims()   # dims from xtor
        self._dims = []
        return None

    
    #====================================================================

    def define_compile_options(self, trace=True):
        """Specific: Define the compile options in the OptionManager.
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        # Selection of dimensions:
        opt = ['freq','time',['freq','time'],'ft','*']
        self._OM.define(self.optname('dims'), '*',
                        opt=opt, more=str,
                        prompt='dimension(s)',
                        callback=self._callback_dims,
                        doc = """Select dimensions to be be used.
                        """)

        # Submenus for all available dimensions:
        if False:
        # for dim in self._available_dims:
            opt = ['Sqr','Sin','Cos','Exp','Abs','Negate','Pow3']    # safe always
            opt.extend(['Sqrt','Log','Invert'])                      # problems <=0
            self._OM.define(self.optname(dim+'.unop'), None,
                            prompt='apply unary()', opt=opt,
                            doc="""apply unary operation
                            """)
            self._OM.define(self.optname(dim+'.stddev'), None,
                            prompt='add stddev noise',
                            opt=[0.1,1.0], more=float,
                            doc="""add gaussian noise (if stddev>0)
                            """)

        # Node combination:
        opt = ['Add','Multiply','ToComplex','ToPolar']
        self._OM.define(self.optname('combine'), 'Add',
                        opt=opt,                         # more=str,
                        prompt='combine with',
                        doc = """The various MeqGrid nodes must be
                        combined to a single node with this operation.
                        """)

        #..............................................
        return self.on_exit(trace=trace)


    #....................................................................

    def _callback_dims (self, dims):
        """Called whenever 'dims' changes"""
        print '** _callback_dims(',dims,type(dims),'):'
        if dims=='*':
            self._dims = self._available_dims
        elif dims in self._available_dims:
            self._dims = [dims]
        elif isinstance(dims, list):
            self._dims = dims
        else:
            s = '** dims not recognised: '+str(dims)
            print s;
            raise ValueError,s
        return True
    

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
        # dims = self.optval('dims')          # use self._dims
        combine = self.optval('combine')

        # Make the subtree:
        cc = []
        for dim in self._dims:
            cc.append(self.ns[dim] << Meq.Grid(axis=dim))

        if combine in ['ToComplex','ToPolar']:
            # NB: Make provisions for len(cc)!=2.....!
            node = self.ns[combine] << getattr(Meq,combine)(*cc)
        else:
            node = self.ns[combine] << getattr(Meq,combine)(*cc)

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
    xtor = Executor.Executor('Executor', namespace='test',
                             parentclass='test')
    xtor.add_dimension('l', unit='rad')
    xtor.add_dimension('m', unit='rad')
    xtor.make_TDLCompileOptionMenu()
    plf = LeafGrids(xtor=xtor)
    plf.make_TDLCompileOptionMenu()
    # plf.display('outside')


def _define_forest(ns):

    global plf,xtor
    if not plf:
        xtor = Executor.Executor()
        xtor.make_TDLCompileOptionMenu()
        plf = LeafGrids(xtor=xtor)
        plf.make_TDLCompileOptionMenu()

    cc = []

    # node = xtor.leafnode(ns)
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
        plf = LeafGrids()
        plf.display('initial')

    if 1:
        plf.make_TDLCompileOptionMenu()

    if 1:
        plf.make_subtree(ns, trace=True)

    if 1:
        plf.display('final', OM=True, full=True)



#===============================================================

