# file: ../Grunt/RedunVisset22.py

# History:
# - 26feb2007: creation

# Description:

# The RedunVisset22 class is a Visset22 in which the groups of matrices that
# represent ifrs with equal (redundant) baselines have been replaced by
# identical matrices, which may contain MeqParms.
# This can be used as the right-hand-side of a Condexet22 object.

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

from Timba.Contrib.JEN.Grunt import Visset22

from copy import deepcopy

# For testing only:
import Meow
from Timba.Contrib.JEN.Grunt import Joneset22


Settings.forest_state.cache_policy = 100

# Global counter used to generate unique node-names
# unique = -1

        
#======================================================================================

class RedunVisset22 (Visset22.Visset22):
    """The RedunVisset22 class is a Visset22 in which the groups of matrices that
    represent ifrs with equal (redundant) baselines have been replaced by
    identical matrices, which may contain MeqParms.
    This can be used as the right-hand-side of a Condexet22 object."""

    def __init__(self, ns, quals=[], label='<rv>',
                 redun=None, polar=False,
                 array=None, polrep=None):

        self._redun = redun
        self._polar = polar

        # Initialise its Matrixet22 object:
        Visset22.Visset22.__init__(self, ns, quals=quals, label=label,
                                   cohset=None, array=array, polrep=polrep)

        # Make the groups of redundant matrices:
        self.make_group_nodes (redun, polar=polar)
        return None

    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += '  '+str(self.label())
        ss += '  pols='+str(self._pols)
        ss += '  n='+str(len(self.stations()))
        ss += '  quals='+str(self.ns()._qualstring())
        ss += '  polar='+str(self._polar)
        return ss


    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        print '   - stations: '+str(self.stations())
        print '   - MS_corr_index: '+str(self._MS_corr_index)
        print '   - redun ('+str(type(self._redun))+'):'
        if isinstance(self._redun, dict):
            for key in self._redun.keys():
                print '     - '+str(key)+': '+str(self._redun[key])
        return True 


    #------------------------------------------------------------------
    
    def make_group_nodes (self, rr, polar=False, quals=None):
        """Make matrices for all redundant baselines, i.e. ifrs that have
        the same baseline as one or more others in the array. The matrices
        in each group are all identical, either a constant unit-matrix or 
        parametrized. The parameters are either ampl/phase (polar=True) or
        real/imag (polar=False), and can be solved for, using the
        ParmGroupManager. rr is a list of dicts, representing groups."""

        # First define ParmGroup objects:
        pg = self.init_group_node(polar=polar)
        
        name = 'redundant'
        qnode = self._ns[name]
        indices = []
        for gg in rr:
            # Make the (matrix) node that the redundant matrices are equated to:
            node = self.make_group_node (gg, polar=polar, pg=pg)
            for ifr in gg['group']:
                qnode(*ifr) << Meq.Identity(node)
                indices.append(ifr)
        self._matrixet = qnode
        self.indices(new=indices)
        self.pgm().define_gogs('redun')
        return True


    #.............................................................................

    def init_group_node (self, polar=False):
        """Helper function for .make_group_nodes()"""

        pname = 'redun_phase'
        aname = 'redun_ampl'
        rname = 'redun_real'
        iname = 'redun_imag'

        # efine ParmGroup objectss:
        pg = dict()
        if polar:
            pg[aname] = self.pgm().define(self._ns, aname,
                                          descr='redundant baseline amplitude',
                                          default=dict(c00=1.0,
                                                       # subtile_size=1,
                                                       tfdeg=[2,0]),
                                          rider=dict(matrel='*'),
                                          tags=[aname,'redun'])
            pg[pname] = self.pgm().define(self._ns, pname,
                                          descr='redundant baseline phase',
                                          default=dict(c00=0.0, unit='rad',
                                                       # subtile_size=1,
                                                       tfdeg=[2,0]),
                                          rider=dict(matrel='*'),
                                          tags=[pname,'redun'])
        else:
            pg[rname] = self.pgm().define(self._ns, rname,
                                          descr='redundant baseline real part',
                                          default=dict(c00=1.0,
                                                       # subtile_size=1,
                                                       tfdeg=[2,0]),
                                          rider=dict(matrel='*'),
                                          tags=[rname,'redun'])
            pg[iname] = self.pgm().define(self._ns, iname,
                                          descr='redundant baseline imag part',
                                          default=dict(c00=0.0,
                                                       # subtile_size=1,
                                                       tfdeg=[2,0]),
                                          rider=dict(matrel='*'),
                                          tags=[iname,'redun'])
        # Finished: Return the dict with ParmGroup objects:
        return pg

    #.............................................................................

    def make_group_node (self, rr=None, polar=False, pg=None):
        """Helper function for .make_group_nodes()"""

        # Prepare:
        pname = 'redun_phase'
        aname = 'redun_ampl'
        rname = 'redun_real'
        iname = 'redun_imag'
        pols = self.pols()                        # e.g. ['X','Y']
        mm = dict(m11=complex(1.0,0.0), m12=complex(0.0,0.0),
                  m21=complex(0.0,0.0), m22=complex(1.0,0.0))
        pp = dict(m11=str(pols[0])+str(pols[0]),
                  m12=str(pols[0])+str(pols[1]),
                  m21=str(pols[1])+str(pols[0]),
                  m22=str(pols[1])+str(pols[1]))
        key = rr['key']
        rhs = rr['rhs']

        # Deal with the various (but always return a Matrix22 node):
        if not isinstance(rhs, str):
            # Assume that rhs is a node already:
            return rhs
        elif rhs=='constant':
            name = 'redun_unity'
            return self._ns[name](key) << Meq.Matrix22(mm['m11'],mm['m12'],
                                                       mm['m21'],mm['m22'])
        elif rhs=='diagonal':
            # The off-diagonal elements are zero:
            name = 'redun_diag'
            name = 'redun'
            mms = ['m11','m22']
        else:
            # All 4 elements are solvable:
            name = 'redun_all4'
            name = 'redun'
            mms = mm.keys()

        # Make a parametrized Matrix22:
        qnode = self._ns[name](key)
        if polar:
            # Solve for ampl/phase per matrix element:
            for m in mms:
                phase = pg[pname].create_member((key,pp[m]))
                ampl = pg[aname].create_member((key,pp[m]))
                mm[m] = qnode(pp[m]) << Meq.Polar(ampl,phase)
        else:
            # Solve for real/imag per matrix element:
            for m in mms:
                real = pg[rname].create_member((key,pp[m]))
                imag = pg[iname].create_member((key,pp[m]))
                mm[m] = qnode(pp[m]) << Meq.ToComplex(real,imag)
        qnode << Meq.Matrix22(mm['m11'],mm['m12'],
                              mm['m21'],mm['m22'])
        # Finished:
        return qnode





#======================================================================================
#======================================================================================
#======================================================================================
# Stand-alone helper routines:
#======================================================================================

def get_WSRT_1D_station_pos(sep9A=36):
    """Helper function to get 1D WSRT station positions (m), depending on
    separation 9-A (m). Used for redundant-spacing calibration.""" 
    xx = range(14)
    for i in range(10): xx[i] = i*144.0
    xx[10] = xx[9]+sep9A                     # A = 9 + sep9A
    xx[11] = xx[10]+72                       # B = A + 72
    xx[12] = xx[10]+(xx[9]-xx[0])            # C = A + (9-0)
    xx[13] = xx[12]+72                       # D = C + 72
    return xx

#-------------------------------------------------------------------------------------

def make_WSRT_redun_groups (ifrs=None, sep9A=36, rhs='diagonal',
                            reference=True, select='all'):
    """Create a dict of named groups of redundant WSRT ifrs""" 

    # Make named (key) groups of baselines with the same length: 
    xx = get_WSRT_1D_station_pos(sep9A=sep9A)
    
    rr = dict()
    for i in range(len(ifrs)):
        ifr = ifrs[i]
        b = xx[ifr[1]-1] - xx[ifr[0]-1]               # ifr stations are 1-relative!
        key = str(int(b))
        rr.setdefault(key, dict(group=[], rhs=rhs, key=key, basel=int(b)))
        rr[key]['group'].append(ifr)


    # Remove the groups with only a single member:
    basel = []
    nmax = 0
    keymax = None
    for key in rr.keys():
        n = len(rr[key]['group'])
        if n==1:
            rr.__delitem__(key)
        else:
            # order.append(key)
            basel.append(rr[key]['basel'])
            if n>nmax:
                nmax = n                                  # size of largest group
                keymax = key                              # name of largest group

    # Use the largest group (e.g. 144m) as a reference:
    if reference:
        rr[keymax]['rhs'] = 'constant'

    # Determine the order of the groups (increasing baseline length):
    order = []
    for k1 in range(len(basel)-1):
        for k2 in range(k1+1,len(basel)):
            if basel[k2]<basel[k1]:
                b = basel[k1]
                basel[k1] = basel[k2]
                basel[k2] = b
        order.append(str(basel[k1]))
    order.append(str(basel[k2]))

    # Return an ordered list of dicts:
    aa = []
    for key in order:
        aa.append(rr[key])
        print rr[key]
    return aa








#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    num_stations = 5
    ANTENNAS = range(1,num_stations+1)
    array = Meow.IfrArray(ns,ANTENNAS)
    # observation = Meow.Observation(ns)
    redun = make_WSRT_redun_groups (ifrs=array.ifrs(), sep9A=36, select='all')
    rvs = RedunVisset22(ns, label='rvis', array=array,
                        redun=redun, polar=True)
    rvs.display('initial', recurse=4)
    # rvs.show_matrix_subtree(recurse=3)

    rvs.visualize (quals=None, visu='rvsi', accu=True,
                   matrel='*', separate=False,
                   bookpage='Matrixet22', folder=None)

    if True:
        jones = Joneset22.JJones(ns, stations=array.stations(), simulate=True)
        rvs.corrupt(jones, visu=True)
        rvs.display('corrupted', recurse=2)

    # Finished:
    if True:
        rvs.insert_accumulist_reqseq()
    cc.append(rvs.bundle())
    ns.result << Meq.Composer(children=cc)
    return True

#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       



#=======================================================================
# Test program (standalone):
#=======================================================================

if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        num_stations = 14
        ANTENNAS = range(1,num_stations+1)
        array = Meow.IfrArray(ns,ANTENNAS)
        # observation = Meow.Observation(ns)
        rr = make_WSRT_redun_groups (ifrs=array.ifrs(), sep9A=36, rhs='all4', select='all')
        rvs = RedunVisset22(ns, label='rvis', redun=rr, polar=False, array=array)
        rvs.display(recurse=4)

    if 0:
        rvs.show_matrix_subtree(recurse=3)

    if 0:
        jones = Joneset22.JJones(ns, stations=array.stations(), simulate=False)
        rvs.corrupt(jones, visu=False)
        rvs.display('corrupted', recurse=2)


#=======================================================================
# Remarks:

#=======================================================================
