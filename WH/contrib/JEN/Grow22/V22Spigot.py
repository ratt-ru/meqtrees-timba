# file: ../JEN/Grow/V22Spigot.py

# History:
# - 06oct2007: creation (from V22.py)

# Description:

"""The V22Spigot class encapsulates the Grunt.Visset22 class.
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
from Timba.Contrib.JEN.Grunt import Visset22
# from Timba.Contrib.JEN.control import Executor

import Meow
from Meow import Context
# from Meow import MeqMaker



#=============================================================================
#=============================================================================

class V22Spigot(V22.V22):
    """Base-class for V22SpigotSomething classes, itself derived from V22"""

    def __init__(self, quals=None,
                 name='V22Spigot',
                 submenu='compile',
                 OM=None, namespace=None,
                 **kwargs):

        V22.V22.__init__(self, quals=quals,
                         name=name,
                         submenu=submenu,
                         has_input=False,             # <-------- !!
                         OM=OM, namespace=namespace,
                         **kwargs)

        return None


    #====================================================================
    # V22Spigot-specific re-implementations of some generic functions in
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
        #...............................................................
        V22.V22.display(self, full=full,
                              recurse=recurse,
                              OM=OM, level=level+1)
        #...............................................................
        if self._result:
            self._result.display(full=False)
        #...............................................................
        return self.display_postamble(prefix, level=level)



    
    #====================================================================
    # Specific part: Placeholders for specific functions:
    # (These must be re-implemented in derived V22Spigot classes) 
    #====================================================================

    def define_compile_options(self, trace=False):
        """Specific: Define the compile options in the OptionManager.
        This function must be re-implemented in derived V22Spigot classes. 
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        # MS options first
        self._mssel = Meow.MSUtils.MSSelector(has_input=True,
                                              tile_sizes=None,
                                              flags=False,
                                              hanning=True)
        Context.mssel = self._mssel
        

        #..............................................
        return self.on_exit(trace=trace)



    #--------------------------------------------------------------------

    def make_TDLCompileOptionMenu (self, **kwargs):
        """Make the actual TDL menu of compile-time options.
        Re-implementation of the Growth function.
        """

        # MS compile-time options
        TDLCompileOptions(*self._mssel.compile_options());

        # MS run-time options (...?)
        TDLRuntimeMenu("MS/data selection options",*self._mssel.runtime_options());

        self._OMI.make_TDLCompileOptionMenu(**kwargs)
        return True
    

    #--------------------------------------------------------------------

    def grow (self, ns, test=None, trace=False):
        """The V22Spigot class is derived from the V22 class.
        It interfaces with the MS.
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        ANTENNAS = self._mssel.get_antenna_set()
        # ANTENNAS = range(1,4)                      # temporary....
        print '** ANTENNAS =',ANTENNAS
        array = Meow.IfrArray(ns, ANTENNAS, mirror_uvw=False)
        print '** array =',str(array)
        print '** array.stations() =',array.stations()
                                               
        observation = Meow.Observation(ns)
        print '** observation =',str(observation)
        Meow.Context.set(array, observation)
        center = Meow.LMApproxDirection(ns, 'cps', l=0.0, m=0.0)

        if True:
            # MS run-time options
            TDLRuntimeOptions(*self._mssel.runtime_options())
            # Alternative:
            # TDLRuntimeMenu("MS selection options", open=True,
            #                *self._mssel.runtime_options())
            
            # note how we set default image size from our current sky model
            self._imsel = mssel.imaging_selector(npix=512,arcmin=10);
            # self._imsel = self._mssel.imaging_selector(npix=512,arcmin=sky_models.imagesize());
            TDLRuntimeMenu("Imaging options",*self._imsel.option_list())
  

        result = Visset22.Visset22(ns, self._OMI.name,
                                   # quals=self._OMI._quals,
                                   array=array, cohset=None)

        result.make_spigots (input_col='DATA',
                             # MS_corr_index=[0,1,2,3], flag_bit=4,
                             visu=True)

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
if 1:
    v22 = V22Spigot(quals='xyv')
    v22.make_TDLCompileOptionMenu()
    mssel = v22._mssel            # used in _tdl_job_execute() below
    # v22.display('outside')


def _define_forest(ns):

    global v22
    if not v22:
        v22 = V22Spigot()
        v22.make_TDLCompileOptionMenu()

    cc = []
    vis = v22.grow(ns)
    print '** vis =',str(vis)

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
    """Just display the current contents of the V22Spigot object"""
    v22.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the V22Spigot object"""
    v22.display('_tdl_job', full=True)
       
       



#===============================================================
# Test routine (without meqbrowser):
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        v22 = V22Spigot(has_input=False)
        v22.display('initial')

    if 1:
        v22.make_TDLCompileOptionMenu()

    if 1:
        test = dict()
        v22.grow(ns, test=test, trace=False)

    if 1:
        v22.display('final', OM=True, full=True)



#===============================================================

