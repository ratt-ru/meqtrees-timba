# file: ../JEN/Grow/TwigLeaf.py

# History:
# - 15sep2007: creation (from Leaf.py)

# Description:

"""The TwigLeaf class is derived from Twig, so it deals with
single-node input/result. It makes makes a node/subtree that has no
children, i.e. it resides at the tip of a branch.
It is a base-class for specialised classes like TwigLeafConstant,
TwigLeafParm etc, and is itself derived from the Twig base-class.
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

class TwigLeaf(Twig.Twig):
    """Base-class for TwigLeafSomething classes, itself derived from Twig"""

    def __init__(self, quals=None,
                 name='TwigLeaf',
                 submenu='compile',
                 xtor=None, dims=None,  
                 OM=None, namespace=None,
                 **kwargs):

        # The list of available dimensions may set externally:
        self._available_dims = dims                    # default dims

        # The list of available dimensions may also be obtained
        # from an external Executor object (if supplied):
        self._xtor = xtor
        if self._xtor:
            self._available_dims = self._xtor.dims()   # dims from xtor

        # But make sure that it is a list:
        if not isinstance(self._available_dims, list):
            self._available_dims = ['freq','time']
        self._dims = []                                # selected dims

        Twig.Twig.__init__(self, quals=quals,
                           name=name,
                           submenu=submenu,
                           OM=OM, namespace=namespace,
                           **kwargs)
        self._has_input = False
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
    

    def display(self, txt=None, full=False, recurse=3,
                OM=True, level=0):
        """Print a summary of this object"""
        prefix = self.display_preamble('TwigLeaf', level=level, txt=txt)
        #...............................................................
        if self._xtor:
            print prefix,'  * '+self._xtor.oneliner()
        print prefix,'  * dims (available) ='+str(self._available_dims)
        print prefix,'  * dims (selected)  ='+str(self._dims)
            
        #...............................................................
        Twig.Twig.display(self, full=full,
                              recurse=recurse,
                              OM=OM, level=level+1)
        #...............................................................
        return self.display_postamble(prefix, level=level)

    

    #=====================================================================
    # Generic dimension handling (optional):
    #=====================================================================


    def _define_dims_options(self):
        """Define the optional dims handling options
        """
        # Selection of dimensions:
        opt = ['freq','time',['freq','time'],'ft','*']
        self.defopt('dims', '*',
                    opt=opt, more=str,
                    prompt='select dimension(s)',
                    callback=self._callback_dims,
                    doc = """Select dimensions to be be used.
                    """)

        # Submenus for all available dimensions:
        for dim in self._available_dims:
            opt = ['Sqr','Sin','Cos','Exp','Abs','Negate','Pow3']    # safe always
            opt.extend(['Sqrt','Log','Invert'])                      # problems <=0
            self.defopt(dim+'.unop', None,
                        prompt='apply unary()', opt=opt,
                        doc="""apply unary operation
                        """)
            self._OM.set_menurec (self._submenu+'.'+dim,
                                  prompt='modif. of node: MeqGrid(axis='+dim+')') 

        return True


    #.................................................................

    def _callback_dims (self, dims):
        """Function called whenever option 'dims' changes."""

        trace = False
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
            self.bookmark(node)
            unop = self.optval(dim+'.unop')
            if unop:
                # Optionally, apply a unary operation:
                node = self.ns[unop] << getattr(Meq,unop)(node)
                self.bookmark(node)
            rr[dim] = dict(node=node, unop=unop)
            if trace:
                print '--',dim,'(',unop,') ->',str(node)
        return rr


    #==================================================================
    # Combining the MeqGrid nodes to a single node:
    #==================================================================


    def _define_combine_options(self):
        """Define the options for combining MeqGrid nodes
        """
        opt = ['Add','Multiply','ToComplex','ToPolar']
        self.defopt ('combine', 'Add', opt=opt, more=str,
                     prompt='combine the MeqGrid nodes with',
                     doc = """The various MeqGrid nodes must be
                     combined to a single node with this operation.
                     """)
        return True
        
    #-------------------------------------------------------------------

    def extract_list_of_MeqGrid_nodes (self, rr, trace=False):
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

    #-------------------------------------------------------------------

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
    # (These must be re-implemented in derived TwigLeaf classes) 
    #====================================================================

    def define_compile_options(self, trace=False):
        """Specific: Define the compile options in the OptionManager.
        This function must be re-implemented in derived TwigLeaf classes. 
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        # Optional (depends on the kind of TwigLeaf): 
        self._define_dims_options()
        self._define_combine_options()

        #..............................................
        return self.on_exit(trace=trace)



    #--------------------------------------------------------------------
    #--------------------------------------------------------------------

    def grow (self, ns, test=None, trace=False):
        """The TwigLeaf class is derived from the Twig class. It is the
        base-class for a family of 'twig-tips', i.e. nodes/subtrees that
        have no children, like a MeqConstant, a MeqParm, or a litte subtree
        of MeqGrid nodes. Since they are Twigs, the result is a single node.
        (NB: The TwigLeaf class contains the interaction with dimensions,
        which are used by the TwigLeafDimGrids class, but also by others.) 
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        # Optional (depends on the kind of TwigLeaf): 
        rr = self.make_MeqGrid_nodes (trace=trace)
        node = self.combine_MeqGrid_nodes (rr, trace=trace)

        #..............................................
        # Finishing touches:
        return self.on_output (node, trace=trace)


    



#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


plf = None
if 0:
    xtor = Executor.Executor()
    xtor.add_dimension('l', unit='rad')
    xtor.add_dimension('m', unit='rad')
    # xtor.add_dimension('x', unit='m')
    # xtor.add_dimension('y', unit='m')

    plf = TwigLeaf(xtor=xtor)
    plf.make_TDLCompileOptionMenu()
    # plf.display('outside')


def _define_forest(ns):

    global plf,xtor
    if not plf:
        xtor = Executor.Executor()
        plf = TwigLeaf(xtor=xtor)
        plf.make_TDLCompileOptionMenu()

    cc = []

    rootnode = plf.grow(ns)
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
    """Just display the current contents of the object"""
    plf.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the object"""
    plf.display('_tdl_job', full=True)
       


       



#===============================================================
# Test routine (without meqbrowser):
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    xtor = None
    if 0:
        xtor = Executor.Executor()
        xtor.add_dimension('l', unit='rad')
        xtor.add_dimension('m', unit='rad')
        # xtor.add_dimension('x', unit='m')
        # xtor.add_dimension('y', unit='m')

    if 1:
        plf = TwigLeaf(xtor=xtor)
    else:
        dims = ['x','y']
        plf = TwigLeaf(xtor=xtor, dims=dims)
    plf.display('initial')

    if 1:
        plf.make_TDLCompileOptionMenu()

    if 1:
        test = dict()
        plf.grow(ns, test=test, trace=False)

    if 1:
        plf.display('final', OM=True, full=True)



#===============================================================
