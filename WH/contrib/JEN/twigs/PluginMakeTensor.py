# file: ../twigs/PluginMakeTensor.py

# History:
# - 07sep2007: creation (from Plugin.py)

# Description:

"""The PluginMakeTensor class makes makes a subtree that takes an input node and
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

from Timba.Contrib.JEN.twigs import Plugin
from Timba.Contrib.JEN.control import OptionManager
from Timba.Contrib.JEN.control import Executor

import math



#=============================================================================
#=============================================================================

class PluginMakeTensor(Plugin.Plugin):
    """Class derived from Plugin"""

    def __init__(self,
                 quals=None, kwquals=None,
                 submenu='compile',
                 OM=None, namespace=None,
                 **kwargs):

        Plugin.Plugin.__init__(self, name='PluginMakeTensor',
                               quals=quals, kwquals=kwquals,
                               submenu=submenu,
                               OM=OM, namespace=namespace,
                               **kwargs)
        return None

    
    #====================================================================

    def define_compile_options(self, trace=True):
        """Specific: Define the compile options in the OptionManager.
        This placeholder function should be reimplemented by a derived class.
        """
        if not self.on_entry (trace=trace):
            return node
        #..............................................
        self._OM.define(self.optname('unop'), 'Cos',
                        prompt='unary',
                        opt=['Sin','Cos'], more=str,
                        doc="""apply an unary operation.
                        """)
        #..............................................
        return self.on_exit(trace=trace)

    #--------------------------------------------------------------------

    def make_subtree (self, ns, node, trace=True):
        """Specific: Make the plugin subtree.
        This placeholder function should be reimplemented by a derived class.
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, node, trace=trace):
            return node
        #..............................................

        # Read the specified options:
        unop = self.optval('unop')
        if not unop:
            return node                           # do nothing

        # Make the subtree:
        node = self.ns['result'] << getattr(Meq,unop)(node)

        #..............................................
        # Check the new rootnode:
        return self.on_output (node, trace=trace)


    def submenu_modify_make_tensor(self):
        """Define the options for an operation on the twig result"""
        name = 'make_tensor'
        submenu = 'compile.modify.'+name+'.'
        opt = [None,'2','3','4','2x2']
        self._OM.define(submenu+'dims', None,
                        prompt='dims',
                        opt=opt, more=str,
                        doc="""duplicate scalar into a tensor node
                        """)
        self._modify[name] = dict(user_level=3)
        return True


    #--------------------------------------------------------------------

    def modify_make_tensor (self, ns, node, trace=False):
        """Optionally, make a tensor node from the given node"""
        name = 'make_tensor'
        if not self._proceed_with_modify (ns, node, name): return node
        submenu = 'compile.modify.'+name+'.'
        dims = self._OM[submenu+'dims']
        if dims==None:                  # not required
            return node
        try:                            # check for integer value
            dd = eval(dims)
        except:
            if 'x' in dims:             # check for nxm (or more)
                nelem = 1
                dd = dims.split('x')
                for i in range(len(dd)):
                    dd[i] = eval(dd[i])
                    nelem *= dd[i]
                nodename = 'tensor'+str(dd)
            else:                       # dims not recognised
                print 'dims =',dims
                raise ValueError,'invalid dims'
        else:                           # dims is integer 
            nelem = dd
            nodename = 'tensor['+str(nelem)+']'

        # OK, duplicate the input node and make the tensor:
        if nelem>1:
            self._data['tensor'] = (nelem>1)                     # used downstream
            self._data['nelem'] = nelem                          # used downstream
            self._data['dims'] = dims                            # used downstream
            nodes = []
            for i in range(nelem):
                nodes.append(ns['elem_'+str(i)] << Meq.Identity(node))
            node = ns[nodename] << Meq.Composer(children=nodes, dims=dd) 
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
    pgt = PluginMakeTensor()
    pgt.make_TDLCompileOptionMenu()
    # pgt.display()


def _define_forest(ns):

    global pgt,xtor
    if not pgt:
        xtor = Executor.Executor()
        xtor.make_TDLCompileOptionMenu()
        pgt = PluginMakeTensor()
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
        pgt = PluginMakeTensor()
        pgt.display('initial')

    if 1:
        pgt.make_TDLCompileOptionMenu()

    if 1:
        node = ns << 1.0
        pgt.make_subtree(ns, node, trace=True)

    if 1:
        pgt.display('final', OM=True, full=True)



#===============================================================

