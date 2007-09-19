# file: ../JEN/Grow/GJ22.py

# History:
# - 17sep2007: creation (from Twig.py)

# Description:

"""The GJ22 class encapsulates the Grunt.Matrixt22 class.
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

from Timba.Contrib.JEN.Grow import J22
from Timba.Contrib.JEN.Grunt import Joneset22
from Timba.Contrib.JEN.control import Executor




#=============================================================================
#=============================================================================

class GJ22(J22.J22):
    """Base-class for GJ22Something classes, itself derived from Growth"""

    def __init__(self, quals=None,
                 name='GJ22',
                 submenu='compile',
                 has_input=False,
                 OM=None, namespace=None,
                 **kwargs):

        J22.J22.__init__(self, quals=quals,
                         name=name,
                         submenu=submenu,
                         has_input=has_input,
                         OM=OM, namespace=namespace,
                         **kwargs)

        self._j22 = Joneset22.GJones(mode='simulate')
        return None


    #====================================================================
    # GJ22-specific re-implementations of some generic functions in
    # the base-class Growth.py
    #====================================================================

    def derivation_tree (self, ss, level=1):
        """Append the formatted derivation tree of this object to the string ss. 
        """
        ss += self.help_format(J22.J22.grow.__doc__, level=level)
        ss = J22.J22.derivation_tree(self, ss, level=level+1)
        return ss

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = J22.J22.oneliner(self)
        return ss
    

    def display (self, txt=None, full=False, recurse=3, OM=True, level=0):
        """Print a summary of this object"""
        prefix = self.display_preamble(self.name, level=level, txt=txt)
        #...............................................................
        #...............................................................
        J22.J22.display(self, full=full,
                              recurse=recurse,
                              OM=OM, level=level+1)
        #...............................................................
        self._j22.display(full=False)
        #...............................................................
        return self.display_postamble(prefix, level=level)




    
    #====================================================================
    # Specific part: Placeholders for specific functions:
    # (These must be re-implemented in derived GJ22 classes) 
    #====================================================================

    def define_compile_options(self, trace=False):
        """Specific: Define the compile options in the OptionManager.
        This function must be re-implemented in derived GJ22 classes. 
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................


        #..............................................
        return self.on_exit(trace=trace)



    #--------------------------------------------------------------------

    def grow (self, ns, test=None, trace=False):
        """The GJ22 class is derived from the Growth class.
        It encapsulates the Grunt.Matrixt22 class.
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        self._j22.make_jones_matrices(ns=ns)
        result = self._j22

        #..............................................
        # Finishing touches:
        return self.on_output (result, trace=trace)


    



#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


j22 = None
if 1:
    xtor = Executor.Executor()
    # xtor.add_dimension('l', unit='rad')
    # xtor.add_dimension('m', unit='rad')
    # xtor.add_dimension('x', unit='m')
    # xtor.add_dimension('y', unit='m')
    j22 = GJ22()
    j22.make_TDLCompileOptionMenu()
    # j22.display('outside')


def _define_forest(ns):

    global j22,xtor
    if not j22:
        xtor = Executor.Executor()
        j22 = GJ22()
        j22.make_TDLCompileOptionMenu()

    cc = []
    mx = j22.grow(ns)
    rootnode = mx.bundle(oper='Composer', quals=[], accu=True)
    cc.append(rootnode)

    aa = mx._PGM.accumulist()
    cc.extend(aa)
    
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
    """Just display the current contents of the Growth object"""
    j22.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the Growth object"""
    j22.display('_tdl_job', full=True)
       


       



#===============================================================
# Test routine (without meqbrowser):
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        j22 = GJ22()
        j22.display('initial')

    if 1:
        j22.make_TDLCompileOptionMenu()

    if 1:
        test = dict()
        j22.grow(ns, test=test, trace=False)

    if 1:
        j22.display('final', OM=True, full=True)



#===============================================================

