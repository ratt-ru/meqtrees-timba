# file: ../JEN/Grow/GJ22.py

# History:
# - 11oct2007: creation (from V22.py)

# Description:

"""The GJ22 class represents the GJones matrix.
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

from Timba.Contrib.JEN.Grow22 import J22
# from Timba.Contrib.JEN.Grunt import Joneset22
# from Timba.Contrib.JEN.control import ParmGroupManager
from Timba.Contrib.JEN.control import Executor

import Meow



#=============================================================================
#=============================================================================

class GJ22(J22.J22):
    """
    Deals with a set of GJones matrices.
    """

    def __init__(self, quals=None,
                 name='GJ22',
                 submenu='compile',
                 solvermenu=None,
                 OM=None, namespace=None,
                 stations=range(1,4),
                 polrep='linear',
                 **kwargs):

        J22.J22.__init__(self, quals=quals,
                         name=name,
                         submenu=submenu,
                         solvermenu=solvermenu,
                         OM=OM, namespace=namespace,
                         stations=stations,
                         polrep=polrep,
                         **kwargs)
        return None


    #====================================================================
    # GJ22-specific re-implementations of some generic functions in
    # the base-class J22.py
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
        prefix = self.display_preamble('GJ22', level=level, txt=txt)
        #...............................................................
        J22.J22.display(self, full=full,
                              recurse=recurse,
                              OM=OM, level=level+1)
        #...............................................................
        return self.display_postamble(prefix, level=level)





#=============================================================================
# Specific re-implementations of J22 placeholder functions:
#=============================================================================


    def define_ParmGroups(self, trace=False):
        """
        Define all ParmGroup objects, for all parameterization modes.
        Called by .define_compile_options().
        Placeholder, to be re-implemented by classes derived from GJ22.
        """
        self._jname = 'GJones'
        self._pname = 'Gphase'
        self._gname = 'Ggain'
        self._rname = 'Greal'
        self._iname = 'Gimag'
        for pol in self.pols():                       # e.g. ['X','Y']
            # rider = dict(use_matrix_element=self._pols_matrel()[pol])

            simuldev = self._PGM.simuldev_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz=None)
            self._PGM.add_ParmGroup(self._pname+pol, mode='amphas',
                                    descr=pol+'-dipole phases',
                                    default_value=0.0, unit='rad',
                                    simuldev=simuldev,
                                    time_tiling=1, freq_tiling=None,
                                    time_deg=0, freq_deg=0,
                                    tags=[self._pname,self._jname])


            simuldev = self._PGM.simuldev_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz='{1000e6~10%}')
            self._PGM.add_ParmGroup(self._gname+pol, mode='amphas',
                                    descr=pol+'-dipole gains (real)',
                                    default_value=1.0,
                                    simuldev=simuldev,
                                    time_tiling=1, freq_tiling=None,
                                    time_deg=2, freq_deg=0,
                                    tags=[self._gname,self._jname])


            simuldev = self._PGM.simuldev_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz='{1000e6~10%}')
            self._PGM.add_ParmGroup(self._rname+pol, mode='realimag',
                                    descr=pol+'-dipole gain (real part)',
                                    default_value=1.0,
                                    simuldev=simuldev,
                                    time_tiling=1, freq_tiling=None,
                                    time_deg=2, freq_deg=0,
                                    tags=[self._rname,self._jname])


            simuldev = self._PGM.simuldev_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz='{1000e6~10%}')
            self._PGM.add_ParmGroup(self._iname+pol, mode='realimag',
                                    descr=pol+'-dipole gain (imag.part)',
                                    default_value=0.0,
                                    simuldev=simuldev,
                                    time_tiling=1, freq_tiling=None,
                                    time_deg=2, freq_deg=0,
                                    tags=[self._iname,self._jname])

        # Finished:
        doc = """The complex gains may have different parameterizations:
        - mode=amphas:   parameters are the phases and gains
        - mode=realimag: parameters are the real and imaginary parts
        """
        self._PGM.define_mode_option(doc)
        return True


    #------------------------------------------------------------------
    # NB: The important bit about this specific .grow() is its __doc__
    # string, which is used in the auto-documentation process.....
    #------------------------------------------------------------------

    def grow (self, ns, test=None, trace=False):
        """The GJ22 class is derived from the J22 class.
        It deals with GJones matrices.
        """
        return J22.J22.grow(self, ns=ns, test=test, trace=trace)

    #--------------------------------------------------------------------

    def make_jones_matrix(self, qnode, station, mode=None, trace=False):
        """Make the Jones matrix (node) for the specified station,
        and the specified parameterization mode (if any).
        Called from generic J22.grow(), which is called from GJ22.grow().
        """
        pols = self.pols()                        # ['X','Y'] or ['R','L']
        mm = dict()
        for pol in pols:
            if mode=='amphas':
                phase = self._PGM[self._pname+pol].create_member (quals=station)
                gain = self._PGM[self._gname+pol].create_member (quals=station)
                mm[pol] = qnode(pol)(station) << Meq.Polar(gain,phase)
            elif mode=='realimag':
                real = self._PGM[self._rname+pol].create_member (quals=station)
                imag = self._PGM[self._iname+pol].create_member (quals=station)
                mm[pol] = qnode(pol)(station) << Meq.ToComplex(real,imag)
            else:
                s = '** mode not recognised: '+str(mode)
                raise ValueError,s
        qnode(station) << Meq.Matrix22(mm[pols[0]],0.0, 0.0,mm[pols[1]])
        return qnode(station) 





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
    v22 = GJ22(quals='xyv')
    v22.make_TDLCompileOptionMenu()
    # v22.display('outside')


def _define_forest(ns):

    global v22,xtor
    if not v22:
        xtor = Executor.Executor()
        v22 = GJ22()
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
    """Just display the current contents of the GJ22 object"""
    v22.display('_tdl_job')
       
def _tdl_job_display_full (mqs, parent):
    """Just display the current contents of the GJ22 object"""
    v22.display('_tdl_job', full=True)
       
       



#===============================================================
# Test routine (without meqbrowser):
#===============================================================


if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        v22 = GJ22('qual')
        v22.display('initial')

    if 1:
        v22.make_TDLCompileOptionMenu()

    if 1:
        test = dict()
        j22 = v22.grow(ns, test=test, trace=False)
        print '  -> j22 =',type(j22)

    if 0:
        v22.display('final', OM=True, full=True)



#===============================================================

