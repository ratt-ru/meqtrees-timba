# file: ../JEN/Grow/J22.py

# History:
# - 11oct2007: creation (from V22.py)

# Description:

"""The J22 class encapsulates the Grunt.Joneset22 class.
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
from Timba.Contrib.JEN.Grunt import Joneset22
from Timba.Contrib.JEN.control import ParmGroupManager
from Timba.Contrib.JEN.control import Executor

import Meow



#=============================================================================
#=============================================================================

class J22(M22.M22):
    """
    Base-class for J22Something classes, itself derived from M22.
    """

    def __init__(self, quals=None,
                 name='J22',
                 submenu='compile',
                 solvermenu=None,
                 OM=None, namespace=None,
                 stations=None,
                 polrep='linear',
                 telescope=None,
                 freqband=None,
                 **kwargs):

        self._solvermenu = solvermenu
        
        self._stations = stations
        self._polrep = polrep
        self._telescope = telescope
        self._freqband = freqband

        M22.M22.__init__(self, quals=quals,
                         name=name,
                         submenu=submenu,
                         has_input=False,
                         OM=OM, namespace=namespace,
                         **kwargs)

        self._PGM = ParmGroupManager.ParmGroupManager(ns=None,
                                                      name=self._OMI.name,
                                                      # quals=quals,
                                                      OM=self._OMI._OM,
                                                      namespace=namespace,
                                                      submenu=self._OMI._submenu,
                                                      solvermenu=solvermenu)
        self.define_ParmGroups()
        return None


    #====================================================================
    # J22-specific re-implementations of some generic functions in
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
        self._PGM.display(full=False, OM=False, level=level+1)
        #...............................................................
        M22.M22.display(self, full=full,
                              recurse=recurse,
                              OM=OM, level=level+1)
        #...............................................................
        return self.display_postamble(prefix, level=level)





    #---------------------------------------------------------------------
    # J22-specific checking:
    #--------------------------------------------------------------------


    def check_result (self, result=None, severe=True, trace=False):
        """Function called by the generic function .on_result()
        (see M22.py) to check the result of .grow().
        It checks whether the result is a Joneset22 object.
        """

        # Default: the Joneset22 object is passed on:
        if result==None:
            result = self._input
            if isinstance(result, list):
                result = result[0]
        
        if not isinstance(result, Joneset22.Joneset22): 
            s = 'result is not a valid Joneset22'
            print s,'\n'
            if severe:
                raise ValueError,s
            else:
                return False
        # If OK, just pass on the valid result:
        return result

    #--------------------------------------------------------------------

    def pols (self):
        """Return the names of the two polairizations, depending on self._polrep
        """
        if not self._polrep:
            self._polrep = self._OMI.optval('polrep', test=test)
        if self._polrep=='circular':
            return ['R','L']
        return ['X','Y']



    
    #====================================================================
    # Specific part: Placeholders for specific functions:
    # (These must be re-implemented in derived J22 classes) 
    #====================================================================

    def define_compile_options(self, trace=False):
        """Specific: Define the compile options in the OptionManager.
        This function must be re-implemented in derived J22 classes. 
        """
        if not self.on_entry (trace=trace):
            return self.bypass (trace=trace)
        #..............................................


        if not self._stations:
            self._OMI.defopt('num_stations', 3, opt=[3,4,5,8,14],
                             prompt='nr of stations')

        if not self._polrep:
            self._OMI.defopt('polrep', 'linear', opt=['linear','circular'],
                             prompt='polarization representation to be used')

        if not self._telescope:
            self._OMI.defopt('telescope', None, opt=[None,'WSRT','VLA','CS1'],
                             prompt='telescope')

        if not self._freqband:
            self._OMI.defopt('freqband', None, opt=[None,'21cm'],
                             prompt='observing frequency band')

            
        #..............................................
        return self.on_exit(trace=trace)


    #--------------------------------------------------------------------

    def grow (self, ns, test=None, trace=False):
        """The J22 class is derived from the M22 class.
        It is a layer around the Grunt.Joneset22 class, which encapsulates
        a set of 2x2 complex cohaerency matrices (i.e. visibilities).
        """
        # Check the node, and make self.ns:
        if not self.on_input (ns, trace=trace):
            return self.bypass (trace=trace)
        #..............................................

        if not self._stations:
            num_stations = self._OMI.optval('num_stations', test=test)
            self._stations = range(1,num_stations+1)

        if not self._polrep:
            self._polrep = self._OMI.optval('polrep', test=test)

        if not self._telescope:
            self._telescope = self._OMI.optval('telescope', test=test)
        if not self._freqband:
            self._freqband = self._OMI.optval('freqband', test=test)

        
        result = Joneset22.Joneset22(ns, self._OMI.name,
                                     # quals=self._OMI._quals,
                                     stations=self._stations,
                                     polrep=self._polrep,
                                     telescope=self._telescope,
                                     band=self._freqband)

        # mm = self.make_jones_matrices(ns)
        # result.set_parmgroups(self._PG)        # <---- !
        # result.set_jones_matrices(mm)          # <---- !
        result.display(full=True)

        #..............................................
        # Finishing touches:
        return self.on_output (result, trace=trace)



#=============================================================================
# Really Specific part for classes derived from J22
#=============================================================================

    def define_ParmGroups(self, trace=False):
        """
        Define all ParmGroup objects, for all parameterization modes.
        Called by .define_compile_options().
        Placeholder, to be re-implemented by classes derived from J22.
        """
        self._pg = dict()
        self._jname = 'GJones'
        self._pname = 'Gphase'
        self._gname = 'Ggain'
        self._rname = 'Greal'
        self._iname = 'Gimag'
        for pol in self.pols():                       # e.g. ['X','Y']
            self._pg[pol] = dict()
            # rider = dict(use_matrix_element=self._pols_matrel()[pol])

            simuldev = self._PGM.simuldev_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz=None)
            pg = self._PGM.add_ParmGroup(self._pname+pol, mode='amphas',
                                         descr=pol+'-dipole phases',
                                         default=0.0, unit='rad',
                                         simuldev=simuldev,
                                         time_tiling=1, freq_tiling=None,
                                         time_deg=0, freq_deg=0,
                                         tags=[self._pname,self._jname])
            self._pg[pol][self._pname] = pg


            simuldev = self._PGM.simuldev_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz='{1000e6~10%}')
            pg = self._PGM.add_ParmGroup(self._gname+pol, mode='amphas',
                                         descr=pol+'-dipole gains (real)',
                                         default=1.0,
                                         simuldev=simuldev,
                                         time_tiling=1, freq_tiling=None,
                                         time_deg=2, freq_deg=0,
                                         tags=[self._gname,self._jname])
            self._pg[pol][self._gname] = pg


            simuldev = self._PGM.simuldev_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz='{1000e6~10%}')
            pg = self._PGM.add_ParmGroup(self._rname+pol, mode='realimag',
                                         descr=pol+'-dipole gain (real part)',
                                         default=1.0,
                                         simuldev=simuldev,
                                         time_tiling=1, freq_tiling=None,
                                         time_deg=2, freq_deg=0,
                                         tags=[self._rname,self._jname])
            self._pg[pol][self._rname] = pg


            simuldev = self._PGM.simuldev_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz='{1000e6~10%}')
            pg = self._PGM.add_ParmGroup(self._iname+pol, mode='realimag',
                                         descr=pol+'-dipole gain (imag.part)',
                                         default=1.0,
                                         simuldev=simuldev,
                                         time_tiling=1, freq_tiling=None,
                                         time_deg=2, freq_deg=0,
                                         tags=[self._iname,self._jname])
            self._pg[pol][self._iname] = pg

        # Finished:
        doc = """The complex gains may have different parameterizations:
        - mode=amphas:   parameters are the phases and gains
        - mode=realimag: parameters are the real and imaginary parts
        """
        self._PGM.define_mode_option(doc)
        return True


    #--------------------------------------------------------------------

    def make_jones_matrices(self, ns=None, trace=False):
        """
        Make the Jones matrices. Called by .grow().
        Placeholder, to be re-implemented by classes derived from J22.
        """
        """Make Jones matrices for all the stations. The argument ns is either
        a nodescope, or a node (which will be scopified)."""
        if trace: print '\n** .make_jones_matrices():',self.oneliner()
        self.nodescope(ns)
        for station in self.stations():
            qnode = self(station)
            if trace: print ' -',station,'->',str(qnode)
        if trace: return '**\n'
        return True


    def make_jones_matrix (self, station):
        """Make the Jones matrix for the specified station"""
        qnode = self.ns[self._jname]                   
        if not qnode.must_define_here(self):
            s = '** '+str(self.name)+': nodename clash: '+str(qnode)
            raise ValueError, s
        self._matrixet = qnode
        pols = self.pols()
        mm = dict()
        for pol in pols:
            phase = self._PGM[self._pg[pol][self._pname]].create_member (quals=station)
            gain = self._PGM[self._pg[pol][self._gname]].create_member (quals=station)
            mm[pol] = qnode(pol)(station) << Meq.Polar(gain,phase)
        qnode(station) << Meq.Matrix22(mm[pols[0]],0.0, 0.0,mm[pols[1]])
        return qnode(station)





#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


v22 = None
if 1:
    xtor = Executor.Executor()
    # xtor.add_dimension('l', unit='rad')
    # xtor.add_dimension('m', unit='rad')
    # xtor.add_dimension('x', unit='m')
    # xtor.add_dimension('y', unit='m')
    v22 = J22(quals='xyv')
    v22.make_TDLCompileOptionMenu()
    # v22.display('outside')


def _define_forest(ns):

    global v22,xtor
    if not v22:
        xtor = Executor.Executor()
        v22 = J22()
        v22.make_TDLCompileOptionMenu()

    cc = []

    if False:
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
    """Just display the current contents of the J22 object"""
    v22.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the J22 object"""
    v22.display('_tdl_job', full=True)
       
       



#===============================================================
# Test routine (without meqbrowser):
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        v22 = J22()
        v22.display('initial')

    if 1:
        v22.make_TDLCompileOptionMenu()

    if 1:
        test = dict()
        v22.grow(ns, test=test, trace=False)

    if 1:
        v22.display('final', OM=True, full=True)



#===============================================================

