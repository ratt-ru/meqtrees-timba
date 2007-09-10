# file: ../twigs/PluginLeaf.py

# History:
# - 10sep2007: creation (from LeafGrids.py)

# Description:

"""The PluginLeaf class makes makes a node/subtree that has no
children, i.e. it resides at the tip of a MeqTree branch.
It is a base-class for specialised classes like LeafConstant,
LeafParm etc, and is itself derived from the Plugin base-class.
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
# from Timba.Contrib.JEN.control import OptionManager
from Timba.Contrib.JEN.control import Executor
# from Timba.Contrib.JEN.Grunt import display

# import math
# import random



#=============================================================================
#=============================================================================

class PluginLeaf(Plugin.Plugin):
    """Base-class for LeafSomething classes, itself derived from Plugin"""

    def __init__(self,
                 quals=None, kwquals=None,
                 submenu='compile',
                 xtor=None, dims=['freq','time'],  
                 OM=None, namespace=None,
                 **kwargs):

        # The list of available dimensions may be obtained
        # from an external Executor object (if supplied):
        self._available_dims = dims                    # default dims
        self._xtor = xtor
        if self._xtor:
            self._available_dims = self._xtor.dims()   # dims from xtor
        self._dims = []


        Plugin.Plugin.__init__(self, name='PluginLeaf',
                               quals=quals, kwquals=kwquals,
                               submenu=submenu,
                               is_leaf=True,
                               OM=OM, namespace=namespace,
                               **kwargs)

        return None


    #=====================================================================
    # Generic dimension handling (optional):
    #=====================================================================


    def _define_dims_options(self):
        """Define the optional dims handling options
        """
        # Selection of dimensions:
        opt = ['freq','time',['freq','time'],'ft','*']
        self._OM.define(self.optname('dims'), '*',
                        opt=opt, more=str,
                        prompt='select dimension(s)',
                        callback=self._callback_dims,
                        doc = """Select dimensions to be be used.
                        """)

        # Submenus for all available dimensions:
        for dim in self._available_dims:
            self._OM.define(self.optname(dim+'.stddev'), None,
                            prompt='add stddev noise',
                            opt=[0.1,1.0], more=float,
                            doc="""add gaussian noise (if stddev>0)
                            """)
            opt = ['Sqr','Sin','Cos','Exp','Abs','Negate','Pow3']    # safe always
            opt.extend(['Sqrt','Log','Invert'])                      # problems <=0
            self._OM.define(self.optname(dim+'.unop'), None,
                            prompt='apply unary()', opt=opt,
                            doc="""apply unary operation
                            """)
            self._OM.set_menu_prompt(self._submenu+'.'+dim,
                                     'modif. of node: MeqGrid(axis='+dim+')') 

        return True


    #.................................................................

    def _callback_dims (self, dims):
        """Function called whenever option 'dims' changes."""

        trace = True
        if trace:
            print '\n** ._callback_dims(',dims,'):'

        # First hide/inactivate all dimensions:
        alldims = ''
        for dim in self._available_dims:
            alldims += dim[0]
            self._OM.hide(self._submenu+'.'+dim)
        if dims=='*':
            dims = alldims
        self._dims = []

        # Then show/activate the selected ones:
        if isinstance(dims, list):                 # e.g. dims=['freq','time']
            for dim in dims:
                if dim in self._available_dims: 
                    self._OM.show(self._submenu+'.'+dim)
                    self._dims.append(dim)

        elif dims in self._available_dims:         # e.g. dims='freq'
            self._OM.show(self._submenu+'.'+dims)
            self._dims.append(dims)

        else:
            for char in dims:                      # e.g. dims='ftlm'
                for dim in self._available_dims:  
                    if dim[0]==char:
                        self._OM.show(self._submenu+'.'+dim)
                        self._dims.append(dim)

        menu = self._OM.TDLMenu(self._submenu)
        if menu:
            menu.set_summary('(dims='+str(dims)+')')

        if trace: print ' -> self._dims =',self._dims
        return True


    #==================================================================
    # Make a record of MeqGrid nodes:
    #==================================================================

    def make_MeqGrid_nodes (self, trace=False):
        """Make a dict with MeqGrid nodes for the selected dimensions.
        Optionally, Modify the MeqGrid nodes as specified by the options.
        """
        rr = dict()
        for dim in self._dims:
            node = self.ns[dim] << Meq.Grid(axis=dim)
            stddev = self.optval(dim+'.stddev')
            node = self.add_noise (node, stddev, trace=True)
            unop = self.optval(dim+'.unop')
            node = self.apply_unary (node, unop, trace=True)
            rr[dim] = dict(node=node, stddev=stddev, unop=unop)
            if trace:
                print '--',dim,'(',stddev,unop,') ->',str(node)
        return rr


    #==================================================================
    # Combining the MeqGrid nodes to a single node:
    #==================================================================


    def _define_combine_options(self):
        """Define the options for combining MeqGrid nodes
        """
        opt = ['Add','Multiply','ToComplex','ToPolar']
        self._OM.define(self.optname('combine'), 'Add',
                        opt=opt, more=str,
                        prompt='combine the MeqGrid nodes with',
                        doc = """The various MeqGrid nodes must be
                        combined to a single node with this operation.
                        """)
        return True
        
    #-------------------------------------------------------------------

    def extract_list_of_MeqGrid_nodes (rr, trace=False):
        """Extract a list of MeqGrid nodes from the given dict rr
        (see .make_MeqGrid_nodes()):
        """
        cc = []
        # for dim in rr.keys():               # Do not use: The order of dict keys can vary! 
        for dim in self._dims:                # This is the CORRECT order of dims      
            node = rr[dim]['node']
            if trace:
                print '-',dim,':',str(node)
            cc.append(node)
        return cc


    def combine_MeqGrid_nodes (self, rr, trace=False):
        """Combine the given dict (rr) of MeqGrid nodes
        """
        if trace:
            print '\n** combine_MeqGrid_nodes():'
            
        # First make a list of MeqGrid nodes
        cc = self.extract_list_of_MeqGrid_nodes (rr, trace=trace)

        # Then combine these to a single node:
        combine = self.optval('combine')
        name = combine+'_MeqGrids'
        if len(cc)==1:                                   # one node only
            node = cc[0]                                 # just pass it on
        elif combine in ['ToComplex','ToPolar']:
            if len(cc)==2:
                node = self.ns[name] << getattr(Meq,combine)(*cc)
            else:
                s = '** nr of dims should be 2 for '+combine
                print s
                raise ValueError,s
        else:
            node = self.ns[name] << getattr(Meq,combine)(*cc)

        # Return the single node:
        if trace:
            self.display_subtree(node)
        return node








    
    #====================================================================
    # Specific part: Placeholders for specific functions:
    # (These must be re-implemented in derived Leaf classes) 
    #====================================================================

    def define_compile_options(self, trace=True):
        """Specific: Define the compile options in the OptionManager.
        This function must be re-implemented in derived Leaf classes. 
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        # Optional (depends on the kind of Leaf): 
        self._define_dims_options()
        self._define_combine_options()

        #..............................................
        return self.on_exit(trace=trace)



    #--------------------------------------------------------------------
    #--------------------------------------------------------------------

    def make_subtree (self, ns, trace=True):
        """Specific: Make the plugin subtree.
        This function must be re-implemented in derived Leaf classes. 
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        # Placeholder, to be replaced:
        rr = self.make_MeqGrid_nodes (trace=trace)
        node = self.combine_MeqGrid_nodes (rr, trace=trace)

        cc = self.extract_list_MeqGrid_nodes (rr, trace=trace)

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
    # xtor.add_dimension('l', unit='rad')
    # xtor.add_dimension('m', unit='rad')
    # xtor.add_dimension('x', unit='m')
    # xtor.add_dimension('y', unit='m')
    ## xtor.make_TDLCompileOptionMenu()      # NOT neede (just for testing)

    plf = PluginLeaf(xtor=xtor)
    plf.make_TDLCompileOptionMenu()
    # plf.display('outside')


def _define_forest(ns):

    global plf,xtor
    if not plf:
        xtor = Executor.Executor()
        plf = PluginLeaf(xtor=xtor)
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
        plf = PluginLeaf()
        plf.display('initial')

    if 0:
        plf.make_TDLCompileOptionMenu()

    if 0:
        plf.make_subtree(ns, trace=True)

    if 0:
        plf.display('final', OM=True, full=True)



#===============================================================

