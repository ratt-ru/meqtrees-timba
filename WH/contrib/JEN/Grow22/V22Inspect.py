# file: ../JEN/Grow/V22Inspect.py

# History:
# - 08oct2007: creation (from V22.py)

# Description:

"""The V22Inspect class is derived from the V22 class.
It provides some inspection of its internal Visset22.
It can be used as a template for other V22 classes.
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

from Timba.Contrib.JEN.Grow22 import V22
# from Timba.Contrib.JEN.Grunt import Visset22

# import Meow
# from Meow import Context
# from Meow import MeqMaker



#=============================================================================
#=============================================================================

class V22Inspect(V22.V22):
    """Base-class for V22InspectSomething classes, itself derived from V22"""

    def __init__(self, quals=None,
                 name='V22Inspect',
                 submenu='compile',
                 OM=None, namespace=None,
                 **kwargs):

        V22.V22.__init__(self, quals=quals,
                         name=name,
                         submenu=submenu,
                         OM=OM, namespace=namespace,
                         **kwargs)

        return None


    #====================================================================
    # V22Inspect-specific re-implementations of some generic functions in
    # the base-class V22.py
    #====================================================================

    def derivation_tree (self, ss, level=1):
        """Append the formatted derivation tree of this object to the string ss. 
        """
        ss += self.help_format(V22.V22.grow.__doc__, level=level)
        ss = V22.V22.derivation_tree(self, ss, level=level+1)
        return ss


    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = V22.V22.oneliner(self)
        return ss
    

    def display (self, txt=None, full=False, recurse=3, OM=True, level=0):
        """Print a summary of this object"""
        prefix = self.display_preamble(self.name, level=level, txt=txt)
        #...............................................................
        V22.V22.display(self, full=full,
                              recurse=recurse,
                              OM=OM, level=level+1)
        #...............................................................
        return self.display_postamble(prefix, level=level)



    
    #====================================================================
    # Specific part: Placeholders for specific functions:
    # (These must be re-implemented in derived V22Inspect classes) 
    #====================================================================

    def define_compile_options(self, trace=False):
        """Specific: Define the compile options in the OptionManager.
        This function must be re-implemented in derived V22Inspect classes. 
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        self._OMI.defopt('rvsi', False,
                         prompt='make rvsi plot',
                         opt=[True, False],  
                         doc="""If True, plot all matrix elements in a
                         real-vs-imaginary plot, with different colors
                         and styles for each of the 4 matrix elements.
                         """)
        
        self._OMI.defopt('inspector', None,
                         prompt='make inspector plot',
                         opt=[None, 'together', 'separate'],  
                         doc="""If not None, plot the visibilities as
                         time-tracks (a.k.a an 'inspector' plot).
                         If 'separate', make separate inspectors
                         for the 4 correlations.
                         """)

        #..............................................
        return self.on_exit(trace=trace)


    #--------------------------------------------------------------------

    def grow (self, ns, input, test=None, trace=False):
        """The V22Inspect class is derived from the V22 class.
        It interfaces with the MS.
        """
        
        # Check the node, and make self.ns:
        if not self.on_input (ns, input, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        result = self._input

        rvsi = self.optval('rvsi', test=test)
        if rvsi:
            result.visualize(visu='rvsi')

        inspector = self.optval('inspector', test=test)
        if inspector:
            separate = (inspector=='separate')
            result.visualize(visu='timetracks', separate=separate)

        # result.visualize(visu='straight')

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
    v22 = V22Inspect(quals='final')
    v22.make_TDLCompileOptionMenu()
    mssel = v22._mssel            # used in _tdl_job_execute() below
    # v22.display('outside')


def _define_forest(ns):

    global v22
    if not v22:
        v22 = V22Inspect()
        v22.make_TDLCompileOptionMenu()

    cc = []
    vis = v22.grow(ns)
    # print '** vis =',str(vis)

    global vdm_nodename
    vdm_nodename = vis.make_sinks(vdm='vdm', visu=False)
    vis.history().display(full=True)
    return True



#---------------------------------------------------------------

Settings.forest_state.cache_policy = 100

def _tdl_job_execute (mqs, parent, wait=False):
    # mqs.meq('Set.Forest.State', record(state=record(cache_policy=TDL_cache_policy)))
    mqs.execute(vdm_nodename, mssel.create_io_request(), wait=wait);
    return True
    
def _tdl_job_display (mqs, parent):
    """Just display the current contents of the V22Inspect object"""
    v22.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the V22Inspect object"""
    v22.display('_tdl_job', full=True)
       
       



#===============================================================
# Test routine (without meqbrowser):
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        v22 = V22Inspect(has_input=False)
        v22.display('initial')

    if 1:
        v22.make_TDLCompileOptionMenu()

    if 1:
        test = dict()
        v22.grow(ns, test=test, trace=False)

    if 1:
        v22.display('final', OM=True, full=True)



#===============================================================

