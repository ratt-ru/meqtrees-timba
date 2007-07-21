# file: ../Grunt/JonesSequence22.py

# History:
# - 30jun2007: creation (from Joneset22.py)

# Description:

# The JonesSequence22 class is derived from the class Joneset22
# It encapsulates a sequence (matrix product) of 2x2 Jones matrices.

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

import Meow

from Timba.Contrib.JEN.Grunt import Joneset22

from copy import deepcopy

#======================================================================================

class JonesSequence22 (Joneset22.Joneset22):
    """A JonesSequence22 that is a station-by-station matrix multiplication of
    one or more Joneset22 matrices (or other matrices that obey the Jones contract)."""

    def __init__(self, ns=None, name='',
                 quals=[], kwquals={},
                 namespace=None,
                 descr='Sequence (product) of Jones matrices',
                 mode='solve'):

        # Mode can be solve, nosolve, simulate:
        self._mode = mode

        # Initialise its Matrixet22 object:
        Joneset22.Joneset22.__init__(self, ns=ns, name=name,
                                     namespace=namespace)

        # The constituent Jones matrices are kept in a dict.
        # These may be objects that obeys the Jones contract.
        self._jones = dict()           # available jones objects
        self._jorder = []              # order in which they are added
        self._locked = False           # blocks further jones addition
        self._selseq = []              # selected jones sequence
        self._jseq_options = [None]    # used in TDLOption

        # Finished:
        return None

    #-------------------------------------------------------------------

    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        print '   - stations ('+str(len(self.stations()))+'): '+str(self.stations())
        print '   - locked: '+str(self._locked)
        print '   - constituent jones objects:'
        for key in self._jorder:
            jones = self._jones[key]
            print '     - '+str(key)+':  '+str(jones.oneliner())
        print '   - jorder: '+str(self._jorder)
        print '   - jseq_options: '+str(self._jseq_options)
        print '   - selected joneseq: '+str(self._selseq)
        return True


    #------------------------------------------------------------------------
    # Add a new Jones matrix object to the internal list:
    #------------------------------------------------------------------------

    def add_jones (self, jones, jchar=None):
        """Add a Jones matrix to the internal record.
        Do some checks, and condition it."""
        if self._locked:
            raise ValueError,'** JonesSequence22 is locked'
        if jchar==None:
            jchar = jones.name[0]                       # e.g. 'G'
        if jchar in self._jorder:
            raise ValueError,'** Duplicate Jones matrix in sequence'

        if len(self._jones)==0:
            # Initialise the underlying Joneset22 object with the
            # essential information of the FIRST jones matrix
            Joneset22.Joneset22.__init__(self, ns=self.ns, name=self.name,                 
                                         namespace=self.namespace(),
                                         descr=self.descr(), 
                                         stations=jones.stations(),
                                         polrep=jones.polrep())

        elif not self.compatible(jones, severe=True):
            # Check whether subsequent jones matrices are compatible
            raise ValueError,'jonesets not compatible'

        # OK, accept and update: 
        self._jones[jchar] = jones 
        self._jorder.append(jchar)
        self._jseq_options.append(jchar)
        jjchar = ''
        for k,jchar in enumerate(self._jorder):
            if k==0: jjchar = jchar
            if k>0: jjchar += '*'+jchar
        self.name = 'jseq_'+jjchar              
        if len(self._jorder)>1:
            self._jseq_options.append(jjchar)
        self._descr = self.descr() + '\n  - '+str(jones.descr())
        self.history(subappend=jones.history())
        return True


    #-------------------------------------------------------------------
    # TDLOptions (re-implementations):
    #-------------------------------------------------------------------

    def TDLCompileOptions (self):
        """Re-implementation of the Joneset22 function for interaction
        with its TDLCompileOptions menu.
        The 'show' argument may be used to show or hide the menu.
        This can be done repeatedly, without duplicating the menu.
        """
        oolist = []

        key = 'jseq'
        if not self._TDLCompileOption.has_key(key):
            opt = self._jseq_options
            oo = TDLCompileOption(key, 'Selected Jones matrix sequence', 
                                  opt, more=str, namespace=self)
            self._TDLCompileOption[key] = oo
            oo.when_changed(self._callback_jseq)
            self.tdloption_reset = opt[0]
        oolist.append(self._TDLCompileOption[key])
        
        for jchar in self._jorder:
            jones = self._jones[jchar]
            om = jones.TDLCompileOptionsMenu()
            self._TDLCompileOption[jchar] = om
            oolist.append(om)
        return oolist

    #..................................................................

    def _callback_jseq (self, jseq=False):
        """Callback function used whenever jseq is changed by the user
        """
        # Convert jseq into a list jj:
        jj = jseq
        if isinstance(jj, bool):                 # i.e. if called without argument ()
            jj = self._TDLCompileOption['jseq'].value
        if jj==None:
            jj = [] 
        else:
            jj = jj.split('*')                   # e.g. G*D*F

        # Renew some variables according to the selected jseq:
        self._selseq = []
        self.name = ''
        for k,jchar in enumerate(jj):
            if not jchar in self._jorder:
                raise ValueError,'jones matrix not recognised'
            self._selseq.append(jchar)
            if k==0: self.name = jchar       
            if k>0: self.name += '*'+jchar  

        # Show/hide TDLOptions according to the selected jseq:
        for jchar in self._jorder:
            if self._TDLCompileOption.has_key(jchar):
                self._TDLCompileOption[jchar].show(jchar in jj)
        self.TDL_tobesolved (trace=False)         # ....temporary....?
        return True

    #..................................................................

    def TDL_tobesolved (self, trace=False):
        """Get a list of the selected parmgroups (or tags?) of MeqParms
        that have been selected for solving."""
        if trace:
            print '\n** TDL_tobesolved(): selseq =',self._selseq
            print '--',self.oneliner()
        slist = []
        for jchar in self._selseq:
            if trace: print ' - jchar:',jchar,
            jones = self._jones[jchar]
            ss = jones.TDL_tobesolved()
            if trace: print ': ss =',ss,'->',
            if isinstance(ss, str):
                slist.append(ss)
            elif isinstance(ss, (list,tuple)):
                slist.extend(ss)
            if trace: print '  slist =',slist
        if trace: print '** TDL_tobesolved(): selseq =',self._selseq,'->',slist,'\n'
        return slist



    #------------------------------------------------------------------------
    # The Jones contract (called by Joneset22.__call__())
    #------------------------------------------------------------------------

    def make_jones_matrix (self, station):
        """Make the Jones matrix for the specified station, by multiplying
        the corresponding matrices from the selected jonesets, if necessary."""
        self._locked = True              # lock the object from here onwards...
        jj = self._selseq                # list of selected jones matrices
        # jj = self._jorder                                 # ....temporary (for testing).....
        if len(jj)==0:
            raise ValueError, '** joneseq is empty'

        # If only one Jones matrix, multiplication is not necessary:
        if len(jj)==1:
            jones = self._jones[jj[0]]
            jones.nodescope(self.ns)                        # ....!
            snode = jones(station)
            self._matrixet = jones._matrixet 
            self._pgm.merge(jones)                             # parmgroups
            return snode

        # Multiply two or more Jones matrices:
        qnode = self.ns[self.name]                   
        if not qnode.must_define_here(self):
            s = '** '+str(self.name)+': nodename clash: '+str(qnode)
            raise ValueError, s
        cc = []
        for j in jj:
            jones = self._jones[j]
            jones.nodescope(self.ns)                        # ....!
            cc.append(jones(station))
            self._pgm.merge(jones)                             # parmgroups
        qnode(station) << Meq.MatrixMultiply(*cc)
        self._matrixet = qnode
        return qnode(station)










     
#===============================================================
# Test routine (with meqbrowser):
#===============================================================

if 1:
    mode = 'solve'
    jseq = JonesSequence22(namespace='bbb')
    jseq.add_jones(Joneset22.GJones(mode=mode, namespace='fff'))
    jseq.add_jones(Joneset22.BJones(mode=mode))
    jseq.add_jones(Joneset22.FJones(mode=mode))
    jseq.add_jones(Joneset22.JJones(mode=mode))
    jseq.TDLCompileOptionsMenu()
    jseq.display('outside _define_forest()')



def _define_forest(ns):

    cc = []

    jseq.nodescope(ns)
    # jseq.display('after .nodescope(ns)')

    jseq.make_jones_matrices()
    jseq.display('after make_jones_matrices')
    # cc.append(jseq.bundle())

    if len(cc)==0: cc.append(ns.dummy<<1.1)
    ns.result << Meq.Composer(children=cc)
    return True


#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,1,1000)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=1, num_time=100)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       


#===============================================================
# Test routine:
#===============================================================

if __name__ == '__main__':
    ns = NodeScope()
    jj = []

    if 1:
        jseq = JonesSequence22()
        jseq.display()

    if 1:
        jones = Joneset22.GJones(ns, quals='3c84', mode='solve')
        jseq.add_jones(jones)
        jones.display(full=True, recurse=10)

    if 1:
        jones = Joneset22.BJones(ns, quals=['3c84'], mode='solve',
                                 telescope='WSRT', band='21cm')
        jseq.add_jones(jones)
        jones.display(full=True)

    if 0:
        jones = Joneset22.FJones(ns, polrep='linear',mode='simulate' )
        # jones = FJones(ns, polrep='circular', quals='3c89', mode='simulate')
        jseq.add_jones(jones)
        jones.display(full=True, recurse=12)

    if 0:
        jones = Joneset22.JJones(ns, quals=['3c84'], diagonal=True, mode='simulate')
        jseq.add_jones(jones)
        jones.display(full=True)

    #...............................................................

    if 1:
        jseq.TDLCompileOptionsMenu()
        jseq.make_jones_matrices(ns('3c844')('repeel'), trace=True)

    if 1:
        jseq.display()
        jseq.history().display(full=True)


#===============================================================
    
