# file: ../JEN/Grow/V22.py

# History:
# - 06oct2007: creation (from M22.py)

# Description:

"""The V22 class encapsulates the Grunt.Matrixt22 class.
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

from Timba.Contrib.JEN.Grow22 import M22
from Timba.Contrib.JEN.Grunt import Visset22
from Timba.Contrib.JEN.control import Executor

import Meow



#=============================================================================
#=============================================================================

class V22(M22.M22):
    """Base-class for V22Something classes, itself derived from M22"""

    def __init__(self, quals=None,
                 name='V22',
                 submenu='compile',
                 OM=None, namespace=None,
                 **kwargs):

        M22.M22.__init__(self, quals=quals,
                         name=name,
                         submenu=submenu,
                         OM=OM, namespace=namespace,
                         **kwargs)

        return None


    #====================================================================
    # V22-specific re-implementations of some generic functions in
    # the base-class M22.py
    #====================================================================

    def derivation_tree (self, ss, level=1):
        """Append the formatted derivation tree of this object to the string ss. 
        """
        ss += self.help_format(M22.M22.grow.__doc__, level=level)
        ss = M22.M22.derivation_tree(self, ss, level=level+1)
        return ss

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = M22.M22.oneliner(self)
        return ss
    

    def display (self, txt=None, full=False, recurse=3, OM=True, level=0):
        """Print a summary of this object"""
        prefix = self.display_preamble(self.name, level=level, txt=txt)
        #...............................................................
        M22.M22.display(self, full=full,
                              recurse=recurse,
                              OM=OM, level=level+1)
        #...............................................................
        return self.display_postamble(prefix, level=level)





    #---------------------------------------------------------------------
    # V22-specific checking (assumes single-node input/result):
    #--------------------------------------------------------------------

    def check_input (self, input, severe=True, trace=False):
        """Function called by the generic function .on_input()
        (see M22.py) to check the input to .grow().
        It checks whether self._input is a Visset22 object.
        This routine should return True (OK) or False (not OK).
        """
        if not isinstance(input, Visset22.Visset22):
            s = 'input is not a Visset22, but: '+str(type(input))
            if severe:
                raise ValueError,s
            else:
                return False                          
        return True

    #--------------------------------------------------------------------

    def check_result (self, result=None, severe=True, trace=False):
        """Function called by the generic function .on_result()
        (see M22.py) to check the result of .grow().
        It checks whether the result is a Visset22 object.
        """

        # Default: the Visset22 object is passed on:
        if result==None:
            result = self._input
            if isinstance(result, list):
                result = result[0]
        
        if not isinstance(result, Visset22.Visset22): 
            s = 'result is not a valid Visset22'
            print s,'\n'
            if severe:
                raise ValueError,s
            else:
                return False
        # If OK, just pass on the valid result:
        return result





    
    #====================================================================
    # Specific part: Placeholders for specific functions:
    # (These must be re-implemented in derived V22 classes) 
    #====================================================================

    def define_compile_options(self, trace=False):
        """Specific: Define the compile options in the OptionManager.
        This function must be re-implemented in derived V22 classes. 
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        self._OMI.defopt('num_stations', 3, opt=[3,4,5,8,14],
                         prompt='nr of stations')
        self._OMI.defopt('stddev', 0.1, opt=[0.1,0.0,1.0],
                         prompt='stddev noise')
        #..............................................
        return self.on_exit(trace=trace)



    #--------------------------------------------------------------------

    def grow (self, ns, test=None, trace=False):
        """The V22 class is derived from the M22 class.
        It is a layer around the Grunt.Visset22 class, which encapsulates
        a set of 2x2 complex cohaerency matrices (i.e. visibilities).
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, trace=trace):
            return self.bypass (trace=trace)
        #..............................................


        num_stations = self._OMI.optval('num_stations', test=test)
        stddev = self._OMI.optval('stddev', test=test)
        
        ANTENNAS = range(1,num_stations+1)
        array = Meow.IfrArray(ns,ANTENNAS)
        print '** array =',str(array)
        observation = Meow.Observation(ns)
        print '** observation =',str(observation)
        Meow.Context.set(array, observation)
        
        result = Visset22.Visset22(ns, self._OMI.name,
                                   # quals=self._OMI._quals,
                                   polrep='linear',
                                   array=array, cohset=None)
        print '** result =',str(result)

        result.fill_with_identical_matrices()
        result.addGaussianNoise(stddev=stddev, visu=False)
                   
        result.display(full=True)

        #..............................................
        # Finishing touches:
        return self.on_output (result, trace=trace)


    



#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


v22 = None
if 0:
    xtor = Executor.Executor()
    # xtor.add_dimension('l', unit='rad')
    # xtor.add_dimension('m', unit='rad')
    # xtor.add_dimension('x', unit='m')
    # xtor.add_dimension('y', unit='m')
    v22 = V22(quals='xyv', has_input=False)
    v22.make_TDLCompileOptionMenu()
    # v22.display('outside')


def _define_forest(ns):

    global v22,xtor
    if not v22:
        xtor = Executor.Executor()
        v22 = V22(has_input=False)
        v22.make_TDLCompileOptionMenu()

    cc = []
    mx = v22.grow(ns)
    print '** mx =',str(mx)
    
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
    """Just display the current contents of the V22 object"""
    v22.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the V22 object"""
    v22.display('_tdl_job', full=True)
       
       



#===============================================================
# Test routine (without meqbrowser):
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        v22 = V22(has_input=False)
        v22.display('initial')

    if 1:
        v22.make_TDLCompileOptionMenu()

    if 1:
        test = dict()
        v22.grow(ns, test=test, trace=False)

    if 1:
        v22.display('final', OM=True, full=True)



#===============================================================

