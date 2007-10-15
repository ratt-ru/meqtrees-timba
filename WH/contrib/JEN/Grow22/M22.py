# file: ../JEN/Grow/M22.py

# History:
# - 17sep2007: creation (from Twig.py)

# Description:

"""The M22 class encapsulates the Grunt.Matrixt22 class.
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

from Timba.Contrib.JEN.Grow import Growth
from Timba.Contrib.JEN.Grunt import Matrixet22
from Timba.Contrib.JEN.control import Executor




#=============================================================================
#=============================================================================

class M22(Growth.Growth):
    """Base-class for M22Something classes, itself derived from Growth"""

    def __init__(self, quals=None,
                 name='M22',
                 submenu='compile',
                 OM=None, namespace=None,
                 **kwargs):

        Growth.Growth.__init__(self, quals=quals,
                               name=name,
                               submenu=submenu,
                               OM=OM, namespace=namespace,
                               **kwargs)

        return None


    #====================================================================
    # M22-specific re-implementations of some generic functions in
    # the base-class Growth.py
    #====================================================================

    def derivation_tree (self, ss, level=1):
        """Append the formatted derivation tree of this object to the string ss. 
        """
        ss += self.help_format(Growth.Growth.grow.__doc__, level=level)
        ss = Growth.Growth.derivation_tree(self, ss, level=level+1)
        return ss

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = Growth.Growth.oneliner(self)
        return ss
    

    def display (self, txt=None, full=False, recurse=3, OM=True, level=0):
        """Print a summary of this object"""
        prefix = self.display_preamble('M22', level=level, txt=txt)
        #...............................................................
        Growth.Growth.display(self, full=full,
                              recurse=recurse,
                              OM=OM, level=level+1)
        #...............................................................
        return self.display_postamble(prefix, level=level)





    #---------------------------------------------------------------------
    # M22-specific checking (assumes single-node input/result):
    #--------------------------------------------------------------------

    def check_input (self, input, severe=True, trace=False):
        """Function called by the generic function .on_input()
        (see Growth.py) to check the input to .grow().
        It checks whether self._input is a Matrixet22 object.
        This routine should return True (OK) or False (not OK).
        """
        if not isinstance(input, Matrixet22.Matrixet22):
            s = 'input is not a Matrixet22, but: '+str(type(input))
            if severe:
                raise ValueError,s
            else:
                return False                          
        return True

    #--------------------------------------------------------------------

    def check_result (self, result=None, severe=True, trace=False):
        """Function called by the generic function .on_result()
        (see Growth.py) to check the result of .grow().
        It checks whether the result is a Matrixet22 object.
        """

        # Default: the Matrixet22 object is passed on:
        if result==None:
            result = self._input
            if isinstance(result, list):
                result = result[0]

        if not isinstance(result, Matrixet22.Matrixet22): 
            s = 'result is not a valid Matrixet22'
            print s,'\n'
            if severe:
                raise ValueError,s
            else:
                return False
        # If OK, just pass on the valid result:
        return result


    #--------------------------------------------------------------------
    # M22-specific interaction with the data-description record:
    #--------------------------------------------------------------------

    def datadesc (self, merge=None, is_complex=None, dims=None, trace=False):
        """Return the data-description record.
        If another datadesc (merge) is specified, update the local one.
        """
        rr = self._datadesc                                 # convenience
        if isinstance(merge, dict):
            if merge['is_complex']: rr['is_complex'] = True
        else:
            if isinstance(is_complex, bool):
                rr['is_complex'] = is_complex
            if dims:
                rr['dims'] = dims
        # Always update the derived quantity nelem (nr of tensor elements):
        rr['nelem'] = 1
        for nd in rr['dims']:
            rr['nelem'] *= nd
        if trace:
            print '** datadesc(',merge,is_complex,dims,'): ',str(self._datadesc)
        return self._datadesc
    

    #---------------------------------------------------------------------
    # M22-specific visualization:
    #--------------------------------------------------------------------

    def define_visu_options(self):
        """Specific function for adding visualization option(s) to the
        visualisation submenu. This version is suitable for derived
        classes that have nodes for input and result. It has to be
        re-implemented for classes with other inputs/results.
        """
        self.defopt('misc.visu.rvsi', False,
                    prompt='make rvsi plot',
                    opt=[True, False],  
                    doc="""If True, plot all matrix elements in a
                    real-vs-imaginary plot, with different colors
                    and styles for each of the 4 matrix elements.
                    """)
        self.defopt('misc.visu.inspector', None,
                    prompt='make inspector plot',
                    opt=[None, 'together', 'separate'],  
                    doc="""If not None, plot the visibilities as
                    time-tracks (a.k.a an 'inspector' plot).
                    If 'separate', make separate inspectors
                    for the 4 correlations.
                    """)
        return True

    #--------------------------------------------------------------------

    def visualize (self, result, trace=False):
        """Specific visualization, as specified in .define_visu_options().
        This default version is suitable for those cases where the input
        and the result are nodes. It has to be reimplemented by derived
        classes that have other types of input/result.
        Note that the result may be modified ('grown') in the process.
        """
        if getattr(result, 'visualize', None):
            rvsi = self.optval('misc.visu.rvsi')
            if rvsi:
                result.visualize(visu='rvsi')
            inspector = self.optval('misc.visu.inspector')
            if inspector:
                separate = (inspector=='separate')
                result.visualize(visu='timetracks', separate=separate)
            # result.visualize(visu='straight')

        # Return the (possibly grown) result: 
        return result




    
    #====================================================================
    # Specific part: Placeholders for specific functions:
    # (These must be re-implemented in derived M22 classes) 
    #====================================================================

    def define_compile_options(self, trace=False):
        """Specific: Define the compile options in the OptionManager.
        This function must be re-implemented in derived M22 classes. 
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................


        #..............................................
        return self.on_exit(trace=trace)



    #--------------------------------------------------------------------

    def grow (self, ns, test=None, trace=False):
        """The M22 class is derived from the Growth class.
        It is a layer around the Grunt.Matrixet22 class, which encapsulates
        a set of 2x2 complex matrices (e.g. visibilities, or Jones matrices).
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        # simulate = self.optval('simulate', test=test)

        result = Matrixet22.Matrixet22(ns)
        result.test(simulate=True)

        result.display(full=True)

        #..............................................
        # Finishing touches:
        return self.on_output (result, trace=trace)


    



#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


m22 = None
if 0:
    xtor = Executor.Executor()
    # xtor.add_dimension('l', unit='rad')
    # xtor.add_dimension('m', unit='rad')
    # xtor.add_dimension('x', unit='m')
    # xtor.add_dimension('y', unit='m')
    m22 = M22(has_input=False)
    m22.make_TDLCompileOptionMenu()
    # m22.display('outside')


def _define_forest(ns):

    global m22,xtor
    if not m22:
        xtor = Executor.Executor()
        m22 = M22(has_input=False)
        m22.make_TDLCompileOptionMenu()

    cc = []
    mx = m22.grow(ns)
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
    m22.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the Growth object"""
    m22.display('_tdl_job', full=True)
       


       



#===============================================================
# Test routine (without meqbrowser):
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        m22 = M22(has_input=False)
        m22.display('initial')

    if 1:
        m22.make_TDLCompileOptionMenu()

    if 1:
        test = dict()
        m22.grow(ns, test=test, trace=False)

    if 1:
        m22.display('final', OM=True, full=True)



#===============================================================

