# file: ../JEN/Grow/TwigLeafConstant.py

# History:
# - 09sep2007: creation (from Growth.py)

# Description:

"""The TwigLeafConstant class makes makes a subtree that represents either
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

from Timba.Contrib.JEN.Grow import TwigLeaf
from Timba.Contrib.JEN.control import OptionManager
from Timba.Contrib.JEN.control import Executor

import math
import random



#=============================================================================
#=============================================================================

class TwigLeafConstant(TwigLeaf.TwigLeaf):
    """Class derived from TwigLeaf"""

    def __init__(self, quals=None,
                 submenu='compile',
                 OM=None, namespace=None,
                 **kwargs):

        TwigLeaf.TwigLeaf.__init__(self, quals=quals,
                                   name='TwigLeafConstant',
                                   submenu=submenu,
                                   OM=OM, namespace=namespace,
                                   **kwargs)
        return None

    
    #====================================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = TwigLeaf.TwigLeaf.oneliner(self)
        return ss
    

    def display (self, txt=None, full=False, recurse=3, OM=True, level=0):
        """Print a summary of this object"""
        prefix = self.display_preamble(self.name, level=level, txt=txt)
        #...............................................................
        print prefix,'  * xxx'
        #...............................................................
        TwigLeaf.TwigLeaf.display(self, full=full,
                          recurse=recurse,
                          OM=OM, level=level+1)
        #...............................................................
        return self.display_postamble(prefix, level=level)

    
    #====================================================================

    def define_compile_options(self, trace=False):
        """Specific: Define the compile options in the OptionManager.
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................
        opt = [0.0,1.0,1+0j,1+1j,'pi','pi/2','pi/4','clight','e','echarge','k','G','h']
        self.defopt('value', 1.0,
                    prompt='value',
                    opt=opt, more=str,
                    doc="""The value of the MeqConstant.
                    """)
        opt = [1,2,3,4,5,8,16,[2,2],[3,3],[4,4],[2,3],[1,2],[4,3,2]]
        self.defopt('dims', 3,
                    prompt='(tensor) dims',
                    opt=opt, more=str,
                    doc="""Make a 'tensor' node with the specified
                    dimensions, with all different elements.
                    """)
        self.defopt('stddev', 0.1,
                    prompt='scatter (stddev)',
                    opt=[0.0,0.1,1.0], more=float,
                    doc="""Add a random number (with gaussian distr) to
                    each tensor element (even if there is only one!),
                    around the nominal element value.
                    """)
        self.defopt('unop', 'Negate',
                    prompt='apply unary',
                    opt=[None,'Negate'], more=str,
                    doc="""Apply an unary operation to the result.
                    """)
        #..............................................
        return self.on_exit(trace=trace)

    #--------------------------------------------------------------------

    def _read_value (self, test=None, trace=False):
        """Make sure that value is a number (float or complex)
        """
        value = self.optval('value', test=test)
        if isinstance(value,str):
            if value=='e':
                value = math.e
            elif value=='pi':
                value = math.pi
            elif value=='pi/2':
                value = math.pi/2.0
            elif value=='pi/4':
                value = math.pi/4.0
            elif value=='clight':
                value = math.floor(2.99725e8)
                value = int(2.99725e8)
            elif value=='kBoltzmann':
                value = 1.38054e-23
            elif value=='G':
                value = 6.670e-11
            elif value=='h':
                value = 6.6256e-34
            elif value=='hslash':
                value = 1.05450e-34
            elif value=='echarge':
                value = 1.60210e-19
            else:
                s = '** value not recognised: '+str(value)
                print s
                raise ValueError,s
        # Update the data-descriptor:
        self.datadesc(is_complex=isinstance(value, complex))
        return value

    #--------------------------------------------------------------------

    def grow (self, ns, test=None, trace=False):
        """The TwigLeafConstant class is derived from the TwigLeaf class.
        In principle, it is just a MeqConstant (scalar or tensor) node.
        A number of mathematical and physical constants may be selected,
        and also the stddev of a 'scatter' deviation from the nominal value.
        Finally, a unary operation (e.g. Negate) may be applied to the result.
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        # Read the specified options:
        value = self._read_value(test=test, trace=trace)
        dims = self._read_dims(test=test, trace=trace)
        stddev = self.optval('stddev', test=test)
        unop = self.optval('unop', test=test)

        # Determine the number of 'tensor' elements:
        nelem = 1
        for dim in dims:
            nelem *= dim
        # print '** dims =',dims,' nelem=',nelem

        # Make the scalar/tensor node:
        if nelem<=0:
            s = '** invalid nelem ('+str(nelem)+')  dims='+str(dims)
            raise ValueError,s
        elif nelem==1:
            scat = self._scatter_value(value,stddev)
            node = self.ns['scalar'] << Meq.Constant(scat)
        else:
            vv = []
            for i in range(nelem):
                vv.append(self._scatter_value(value,stddev))
            name = 'tensor'
            if len(dims)==1:
                name += str(dims)
            else:
                name += str(dims)
            node = self.ns[name] << Meq.Composer(children=vv, dims=dims)

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

    def _read_dims (self, test=None, trace=False):
        """Make sure that dims is a list of integers
        """
        dims = self.optval('dims', test=test)
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
        # Update the data-descriptor record:
        self.datadesc(dims=dims, trace=False)
        return dims



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
    plf = TwigLeafConstant()
    plf.make_TDLCompileOptionMenu()
    # plf.display()


def _define_forest(ns):

    global plf,xtor
    if not plf:
        xtor = Executor.Executor()
        plf = TwigLeafConstant()
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
        plf = TwigLeafConstant()
        plf.display('initial')

    if 1:
        plf.make_TDLCompileOptionMenu()

    if 1:
        test = dict(value=1+1j)
        test = dict(value='clight')
        plf.grow(ns, test=test, trace=True)

    if 1:
        plf.display('final', OM=True, full=True)



#===============================================================

