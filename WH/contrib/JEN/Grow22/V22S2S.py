# file: ../JEN/Grow/V22S2S.py

# History:
# - 06oct2007: creation (from V22.py)

# Description:

"""The V22S2S class encapsulates the Grunt.Visset22 class.
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

from Timba.Contrib.JEN.Grow22 import V22Inspect

import Meow
from Meow import Context
# from Meow import MeqMaker



#=============================================================================
#=============================================================================

class V22S2S(V22.V22):
    """Base-class for V22S2SSomething classes, itself derived from V22"""

    def __init__(self, quals=None,
                 name='V22S2S',
                 submenu='compile',
                 OM=None, namespace=None,
                 **kwargs):

        V22.V22.__init__(self, quals=quals,
                         name=name,
                         submenu=submenu,
                         has_input=False,             # <-------- !!
                         defer_compile_options=True,  # <-------- !!
                         OM=OM, namespace=namespace,
                         **kwargs)


        # Initialize the V22 plugin sequence:
        self._plugin_order = []
        self._plugin = dict()

        return None


    #====================================================================
    # V22S2S-specific re-implementations of some generic functions in
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
        prefix = self.display_preamble('V22S2S', level=level, txt=txt)
        #...............................................................
        V22.V22.display(self, full=full,
                              recurse=recurse,
                              OM=OM, level=level+1)
        #...............................................................
        print prefix,'  * Plugin sequence (+ is selected):'
        for key in self._plugin_order:
            rr = self._plugin[key]
            if rr['plugin']._OMI.is_selected():
                print prefix,'    + '+key+': '+str(rr['plugin'].oneliner())
            else:
                print prefix,'    - '+key+': '+str(rr['plugin'].oneliner())
        #...............................................................
        print prefix,'  * Resulting (root) node name: '+str(self._result)
        #...............................................................
        return self.display_postamble(prefix, level=level)



    #====================================================================
    # Generic functions for class V22S2S (V22Spigot2Sink)
    #====================================================================


    def check_result (self, result, severe=True, trace=False):
        """Function called by the generic function .on_result()
        (see V22.py) to check the result of .grow().
        It checks whether the result is a (root)nodename.
        """
        print '\n** .check_result(',type(result),')'
        if not isinstance(result, str): 
            s = 'result is not a valid (root) nodename'
            print s,'\n'
            if severe:
                raise ValueError,s
            else:
                return False
        # If OK, just pass on the valid result:
        return result

    
    #-------------------------------------------------------------------

    def add_plugin(self, plugin, modes=None, trace=False):
        """
        Check the given V22 object, and add it to self._plugin.
        """
        
        if trace:
           print '\n** .add_plugin(',type(plugin),modes,'):'
            
        # OK, add the valid plugin to the list:
        name = plugin.name
        self._plugin[name] = dict(plugin=plugin, modes=modes) 
        self._plugin_order.append(name)

        if trace:
            print '   ->',plugin.oneliner()
        return True


    #---------------------------------------------------------------------------

    def create_Growth_objects (self, trace=False):
        """Re-implementation of the generic Growth function.
        """

        submenu = self._OMI._submenu
        # submenu = self._OMI._submenu+'.V22plugin'
        print '** create_Growth_objects(submenu=',submenu,'):'
        self.define_plugin_sequence (submenu, trace=False)
        self._OMI.set_menurec(submenu, prompt='select a V22 plugin sequence')

        # Execute the deferred function:
        self.define_compile_options()
        return True
        

    
    #====================================================================
    # Specific part: Placeholders for specific functions:
    # (These must be re-implemented in derived V22S2S classes) 
    #====================================================================

    def define_compile_options(self, trace=False):
        """Specific: Define the compile options in the OptionManager.
        This function must be re-implemented in derived V22S2S classes. 
        """
        # trace = True
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        self._OMI.defopt('V22S2S_option', 56)

        #..............................................
        return self.on_exit(trace=trace)



    #--------------------------------------------------------------------

    def make_TDLCompileOptionMenu (self, **kwargs):
        """Make the actual TDL menu of compile-time options.
        Re-implementation of the Growth function.
        """

        # MS options:
        self._mssel = Meow.MSUtils.MSSelector(has_input=True,
                                              tile_sizes=None,
                                              flags=False,
                                              hanning=True)
        Context.mssel = self._mssel
        
        # MS compile-time options
        TDLCompileOptions(*self._mssel.compile_options())

        # The plugin objects define compile options too!
        # NB: Review this function in Growth.py (wobbly logic!)
        if not self._created_Growth_objects:
            self.create_Growth_objects()
            self._created_Growth_objects = True

        # MS run-time options (...?)
        TDLRuntimeMenu("MS/data selection options",*self._mssel.runtime_options());

        self._OMI.make_TDLCompileOptionMenu(**kwargs)
        return True
    

    #--------------------------------------------------------------------

    def grow (self, ns, test=None, trace=False):
        """The V22S2S (V22Spigot2Sink) class is derived from the V22 class.
        It encapsulates the Visset22 class, which contains the parallel trees
        for all ifrs (2x2 cohaerency matrices), and is passed between a sequence
        of V22 objects (i.e. objects derived from the V22 class). The Visset22
        is created and filled with spigots from an AIPS++ Measurement Set (MS).
        The Visset22 is then processed by a specific sequence of V22 objects,
        which make it add nodes (grow) to the ifr-trees. Finally, the ifr-trees
        are terminated with a sink nodes, and the name of the VisDataMux rootnode
        is returned. This is to be used as rootnode in _tdl_job_execute().
        
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

        # Make the Visset22 object and fill it with spigots:
        visset22 = Visset22.Visset22(ns, self._OMI.name,
                                   # quals=self._OMI._quals,
                                     polrep='linear',
                                   array=array, cohset=None)

        visset22.make_spigots (input_col='DATA',
                             # MS_corr_index=[0,1,2,3], flag_bit=4,
                             visu=False)

        # Plug in the selected plugin-sequence:
        for key in self._plugin_order:
            rr = self._plugin[key]
            print '\n -',key,':',rr['plugin'].oneliner()
            visset22 = rr['plugin'].grow(ns, visset22, trace=False)
            print '    -> visset22 =',visset22.oneliner()

        # Make the sinks. The result is the name of the VisDataMux node:
        result = visset22.make_sinks(vdm='vdm', visu=False)

        # Show the result (optional, debugging):
        visset22.history().display(full=True)
        # visset22.display(full=True)

        # Run-time options:
        if True:
            TDLRuntimeOptions(*self._mssel.runtime_options())
            # Alternative:
            # TDLRuntimeMenu("MS selection options", open=True,
            #                *self._mssel.runtime_options())
            
            # note how we set default image size from our current sky model
            self._imsel = mssel.imaging_selector(npix=512,arcmin=10);
            # self._imsel = self._mssel.imaging_selector(npix=512,arcmin=sky_models.imagesize());
            TDLRuntimeMenu("Imaging options",*self._imsel.option_list())
  
        #..............................................
        # Finishing touches:
        return self.on_output (result, trace=trace)




    #===========================================================================
    #===========================================================================
    # Truly specific for classes derived from V22S2S :
    #===========================================================================

    def define_plugin_sequence (self, submenu, trace=False):
        """
        Define a specific sequence of V22 plugins, to be selected by the user.
        """


        # Recommended: This should be the last one in any V22S2S class:
        if True:
            self.add_plugin (V22Inspect.V22Inspect('final', submenu=submenu,
                                                   OM=self._OMI._OM,
                                                   toggle_box=True))
        return True




    



#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================



s2s = None
if 1:
    s2s = V22S2S(quals='xyv')
    s2s.make_TDLCompileOptionMenu()
    mssel = s2s._mssel            # used in _tdl_job_execute() below
    # s2s.display('outside')


def _define_forest(ns):

    global s2s
    if not s2s:
        s2s = V22S2S()
        s2s.make_TDLCompileOptionMenu()

    global vdm_nodename
    vdm_nodename = s2s.grow(ns)
    return True



#---------------------------------------------------------------

Settings.forest_state.cache_policy = 100

def _tdl_job_execute (mqs, parent, wait=False):
    # mqs.meq('Set.Forest.State', record(state=record(cache_policy=TDL_cache_policy)))
    mqs.execute(vdm_nodename, mssel.create_io_request(), wait=wait);
    return True
    
def _tdl_job_display (mqs, parent):
    """Just display the current contents of the V22S2S object"""
    s2s.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the V22S2S object"""
    s2s.display('_tdl_job', full=True)
       
       



#===============================================================
# Test routine (without meqbrowser):
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        s2s = V22S2S(has_input=False)
        s2s.display('initial')

    if 1:
        s2s.make_TDLCompileOptionMenu()

    if 1:
        test = dict()
        s2s.grow(ns, test=test, trace=False)

    if 1:
        s2s.display('final', OM=True, full=True)



#===============================================================

