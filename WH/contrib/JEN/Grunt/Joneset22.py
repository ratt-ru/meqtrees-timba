# file: ../Grunt/Joneset22.py

# History:
# - 25dec2006: creation
# - 14jan2007: keep only generic G/J/FJones
# - 29jan2007: added BJones
# - 30mar2007: adapted to QualScope etc
# - 07jun2007: adapted to ParameterizationPlus
# - 02jul2007: adapted to Jones Contract
# - 16jul2007: changed simul to mode
# - 17jul2007: adaptation to ._pgm.

# Description:

# The Joneset22 class is a base-class for classes that define and
# encapsulate a set of 2x2 station Jones matrices.

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

from Timba.Contrib.JEN.Grunt import Matrixet22

from copy import deepcopy

#======================================================================================

class Joneset22 (Matrixet22.Matrixet22):
    """Base class that represents a set of 2x2 Jones matrices.
    Derived from the class Matrixet22."""

    def __init__(self, ns=None, name='<j>',
                 quals=[], kwquals={},
                 namespace=None,                               # <---- !!
                 descr='<descr>',
                 stations=None,
                 polrep='linear',
                 telescope=None, band=None,
                 mode='nosolve'):

        # List of (array) station indices:
        indices = deepcopy(stations)
        if indices==None:
            indices = range(1,4)                               # for testing convenience....

        # Modes can be solve, nosolve, simulate:
        self._mode = mode                                      # passed on to parmgroups

        # Some telescope-specific information:
        self._telescope = telescope                            # e.g. WSRT or VLA
        self._band = band                                      # e.g. 21cm or LFFE

        # Add some qualifiers, if necessary:
        quals = self.quals2list(quals)
        ## if self._mode=='simulate': quals.append('simul')      # NOT a good idea...
        if self._telescope: quals.append(self._telescope)
        if self._band: quals.append(self._band)

        # Initialise its Matrixet22 object:
        Matrixet22.Matrixet22.__init__(self, ns, name,
                                       quals=quals, kwquals=kwquals,
                                       namespace=namespace,
                                       descr=descr,
                                       polrep=polrep, indices=indices)

        # Re-define Matrixet22 element names and plotting instructions:
        matrix_elements = [self._pols[0], self._pols[0]+self._pols[1],
                           self._pols[1]+self._pols[0],self._pols[1]]
        self._matrix_elements['name'] = matrix_elements
        # self._matrix_elements['color'] = ['red','magenta','darkCyan','blue']
        # self._matrix_elements['style'] = ['circle','xcross','xcross','circle']
        # self._matrix_elements['size'] = [10,10,10,10]
        # self._matrix_elements['pen'] = [2,2,2,2])

        # The parmgroup definitions are carried in a dict:
        # (if self._pg==None, .define_parmgroups will be called)
        self._pg = None

        self.define_parmgroups()

        # Finished:
        return None

    #-------------------------------------------------------------------

    def stations(self):
        """Return a list of (array) stations"""
        self._stations = self.indices()                        # kept in Matrixet22
        return self._stations

    def telescope(self):
        """Return the name of the telescope (if any) for which this Jones matrix is valid"""
        return self._telescope                

    def band(self):
        """Return the name of the freq band (if any) for which this Jones matrix is valid"""
        return self._band                

    #-------------------------------------------------------------------

    def compatible (self, jones, severe=True):
        """Check whether the given jones matrix is compatible"""
        s = 'jonesets not compatible: '
        if not self.stations()==jones.stations():
            s += 'stations = '+str(self.stations())+' '+str(jones.stations())
            raise ValueError,s
        if not self.polrep()==jones.polrep():
            s += 'polrep = '+str(self.polrep())+' '+str(jones.polrep())
            raise ValueError,s
        return True

    #-------------------------------------------------------------------

    def _pols_matrel(self):
        """Convenience function to make a dict with pols as field-names,
        which gives the relevant Matrixet22 elements for the 2 pols.
        Used e.g. in GJones to indicate that only the diagonal matrix
        elements should be used to solve for Ggain and Gphase."""
        pols = self.pols()
        matrel = dict()
        matrel[pols[0]] = self._matrix_elements['name'][0]
        matrel[pols[1]] = self._matrix_elements['name'][3]
        return matrel


    #-------------------------------------------------------------------
    # Display:
    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += '  '+str(self.name)
        if self._telescope:
            ss += ' '+str(self._telescope)
            if self._band:
                ss += ' '+str(self._band)
        else:
            ss += '  pols='+str(self._pols)
        ss += '  n='+str(len(self.stations()))
        ss += '  ('+str(self.ns['<>'].name)+')'
        return ss


    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        print '   - stations ('+str(len(self.stations()))+'): '+str(self.stations())
        if isinstance(self._pg, dict):
            print '   - parmgroups: '+str(self._pg.keys())
        else:
            print '   - parmgroups (pg): '+str(self._pg)
        return True



    #-------------------------------------------------------------------
    # The Jones Contract:
    #-------------------------------------------------------------------

    def __call__(self, station=None):
        """Implementation of the Jones contract: J is a Station Jones if,
        for a given station index p, J(p) returns a valid 2x2 matrix node.
        The node/subtree is created if necessary."""
        if station==None:
            return self._matrixet
        if not self._matrixet:
            if not self._pg:
                self.define_parmgroups()
            j22 = self.make_jones_matrix(station)
        else:
            j22 = self._matrixet([station])
            if not j22.initialized(): 
                if not self._pg:
                    self.define_parmgroups()
                j22 = self.make_jones_matrix(station)
        return j22

    #----------------------------------------------------------------------

    def define_parmgroups(self):
        """Placeholder for specific function in derived classes."""
        self.define_parmgroups_preamble()
        self._pg = dict()
        return True

    def define_parmgroups_preamble(self):
        """Generic function that should be called at the start of a specific
        re-implementation of .define_parmgroups() by a derived class."""
        return True

    #----------------------------------------------------------------------

    def make_jones_matrices (self, ns=None, trace=False):
        """Make Jones matrices for all the stations. The argument ns is either
        a nodescope, or a node (which will be scopified)."""
        if trace: print '\n** .make_jones_matrices():',self.oneliner()
        self.nodescope(ns)
        for station in self.stations():
            qnode = self(station)
            if trace: print ' -',station,'->',str(qnode)
        if trace: return '**\n'
        return True

    #----------------------------------------------------------------------

    def make_jones_matrix (self, station, ns=None):
        """Make the Jones matrix for the specified station.
        This is a place-holder, to be re-implemented by a derived class."""
        self.nodescope(ns)
        qnode = self.ns[self.name]                   
        if not qnode.must_define_here(self):
            s = '** '+str(self.name)+': nodename clash: '+str(qnode)
            raise ValueError, s
        self._matrixet = qnode
        qnode(station) << Meq.Matrix22(1.0,0.0,0.0,1.0)
        return qnode(station)





#=================================================================================================
# Make a Joneset22 object that is a sequence (matrix multiplication) of Jones matrices
# Semi-obsolete..... certainly not uptodate, or consistent with TDLOptions....
#=================================================================================================

def Joneseq22 (ns, joneslist=None, quals=None):
    """Return a Jones22 object that contains an (item-by-item) matrix multiplication
    of the matrices of the list (joneslist) of two or more Joneset22 objects."""

    if len(joneslist)==0:
        raise ValueError, 'joneslist should have at least one item'
    
    elif len(joneslist)==1:
        jnew = joneslist[0]
        return jnew
    
    # First create a new Jonset22 object with name/quals/descr that are
    # suitable combinations of those of the contributing Joneset22 objects: 
    first = joneslist[0]
    name = first.name[0]
    descr = first.name+': '+first.descr()
    stations = first.stations()
    qq = first._pgm.get_quals(remove=[first.name])
    for jones in joneslist[1:]:
        name += jones.name[0]
        descr += '\n '+jones.name+': '+jones.descr()
        qq = jones._pgm.get_quals(merge=qq, remove=[jones.name])
    qq.extend(first.quals2list(quals))
    jnew = Joneset22(ns, name=name+'Jones',
                     polrep=first.polrep(),
                     quals=qq, stations=stations) 

    # Then create the new Jones matrices by matrix-multiplication:
    jnew.history('.Joneseq22(): Matrix multiplication of '+str(len(joneslist))+' Jones matrices')
    qnode = jnew.ns.Joneseq
    for i in jnew.list_indices():
        cc = []
        for jones in joneslist:
            cc.append(jones._matrixet(*i))
        qnode(*i) << Meq.MatrixMultiply(*cc)
    jnew.matrixet(new=qnode)
    
    # Merge the parmgroups of the various Jones matrices:
    for jones in joneslist:
        jnew._pgm.merge(jones)
        jnew.history(subappend=jones.history())

    # Return the new Joneset22 object:
    return jnew







#=================================================================================================
# Some generic Joneset22 classes (to separate modules?):
#=================================================================================================

class GJones (Joneset22):
    """Class that represents a set of 2x2 GJones matrices,
    which model the (complex) gains due to electronics
    and (optionally) the tropospheric phase (a.k.a. TJones).
    Gjones matrix elements:
    - G_11 = Polar(GgainA,GphaseG)
    - G_12 = 0
    - G_21 = 0
    - G_22 = Polar(GgainA,GphaseG)
    GJones is a uv-plane effect, i.e. it is valid for the entire FOV.
    GJones is the same for linear and circular polarizations."""


    def __init__(self, ns=None, name='GJones', quals=[],
                 namespace=None,
                 polrep='linear',
                 telescope=None, band=None,
                 override=None,
                 stations=None,
                 mode='nosolve'):
        
        self._jname = 'GJones'
        Joneset22.__init__(self, ns=ns, quals=quals, name=name,
                           namespace=namespace,
                           polrep=polrep,
                           telescope=telescope, band=band,
                           stations=stations,
                           mode=mode)

        # Define the list of (groups of) parmgroups to be used in the TDL menu: 
        self._TDLCompileOption_tobesolved = [None, self._jname, 'Gphase', 'Ggain'] 

        # Finished:
        self.history(override)
        return None

    #------------------------------------------------------------------------------

    def define_parmgroups(self):
        """Define the various primary ParmGroups"""
        self.define_parmgroups_preamble()
        self._pg = dict()
        self._pname = 'Gphase'
        self._gname = 'Ggain'
        for pol in self.pols():                       # e.g. ['X','Y']
            self._pg[pol] = dict()
            rider = dict(use_matrix_element=self._pols_matrel()[pol])

            dev = self._pgm.simuldev_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz=None)
            pg = self._pgm.define_parmgroup(self._pname+pol,
                                            descr=pol+'-dipole phases',
                                            default=0.0, unit='rad',
                                            tiling=1, time_deg=0, freq_deg=0,
                                            constraint=dict(sum=0.0, first=0.0),
                                            mode=self._mode,
                                            simuldev=dev,
                                            # override=override,
                                            # rider=rider,
                                            tags=[self._pname,self._jname])
            self._pg[pol][self._pname] = pg

            dev = self._pgm.simuldev_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz='{1000e6~10%}')
            pg = self._pgm.define_parmgroup(self._gname+pol,
                                            descr=pol+'-dipole gains',
                                            default=1.0,
                                            tiling=None, time_deg=2, freq_deg=0,
                                            # constrain_min=0.1, constrain_max=10.0,
                                            constraint=dict(product=1.0),
                                            mode=self._mode,
                                            simuldev=dev,
                                            # override=override,
                                            # rider=rider,
                                            tags=[self._gname,self._jname])
            self._pg[pol][self._gname] = pg

        return True

    #------------------------------------------------------------------------------

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
            phase = self._pgm[self._pg[pol][self._pname]].create_member (quals=station)
            gain = self._pgm[self._pg[pol][self._gname]].create_member (quals=station)
            mm[pol] = qnode(pol)(station) << Meq.Polar(gain,phase)
        qnode(station) << Meq.Matrix22(mm[pols[0]],0.0, 0.0,mm[pols[1]])
        return qnode(station)





#============================================================================================
#============================================================================================

class BJones (Joneset22):
    """Class that represents a set of 2x2 BJones matrices,
    which model the (complex) bandpass due to electronics.
    Bjones matrix elements:
    - B_11 = (BrealA,BimagB)
    - B_12 = 0
    - B_21 = 0
    - B_22 = (BrealA,BimagB)
    NB: The main differences with Gjones are:
    - the higher-order (~5) freq-polynomial
    - solving for real/imag rather than gain/phase 
    BJones is a uv-plane effect, i.e. it is valid for the entire FOV.
    BJones is the same for linear and circular polarizations."""

    def __init__(self, ns=None, name='BJones', quals=[], 
                 namespace=None,
                 polrep='linear',
                 telescope=None, band=None,
                 tfdeg=[0,5],
                 override=None,
                 stations=None,
                 mode='nosolve'):
        
        self._jname = 'BJones'
        self._tfdeg = tfdeg
        Joneset22.__init__(self, ns=ns, quals=quals, name=name,
                           namespace=namespace,
                           polrep=polrep, telescope=telescope, band=band,
                           stations=stations,
                           mode=mode)

        # Define the list of (groups of) parmgroups to be used in the TDL menu: 
        self._TDLCompileOption_tobesolved = [None, self._jname, 'Breal', 'Bimag']

        self.history(override)
        return None


    #------------------------------------------------------------------------------

    def TDLCompileOptions (self):
        """Define a list of TDL option objects that control the structure
        of the Jones matrix."""
        oolist = []

        key = '_tfdeg'
        if not self._TDLCompileOption.has_key(key):
            opt = [[0,5],[0,4],[1,4]]
            self._TDLCompileOption[key] = TDLOption(key, 'tfdeg', opt,
                                                    doc='rank of time/freq polynomial',
                                                    namespace=self)
            self.tdloption_reset[key] = opt[0]
        oolist.append(self._TDLCompileOption[key])

        # Finished: Return a list of option objects:
        return oolist


    #------------------------------------------------------------------------------

    def define_parmgroups(self):
        """Define the various primary ParmGroups"""
        self.define_parmgroups_preamble()
        self._pg = dict()
        pols = self.pols()                                # e.g. ['X','Y']
        self._iname = 'Bimag'
        self._rname = 'Breal'
        for pol in pols:
            self._pg[pol] = dict()
            rider = dict(use_matrix_element=self._pols_matrel()[pol])
            dev = self._pgm.simuldev_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz='{10e6~10%}')

            pg = self._pgm.define_parmgroup(self._iname+pol,
                                            descr=pol+'-IF bandpass imag.part',
                                            default=0.0, unit='Jy',
                                            tiling=1,
                                            time_deg=self._tfdeg[0],
                                            freq_deg=self._tfdeg[1],
                                            mode=self._mode,
                                            simuldev=dev,
                                            # override=override,
                                            # rider=rider,
                                            tags=[self._iname,self._jname])
            self._pg[pol][self._iname] = pg

            pg = self._pgm.define_parmgroup(self._rname+pol,
                                            descr=pol+'-IF bandpass real.part',
                                            default=1.0, unit='Jy',
                                            tiling=None,
                                            time_deg=self._tfdeg[0],
                                            freq_deg=self._tfdeg[1],
                                            mode=self._mode,
                                            simuldev=dev,
                                            # override=override,
                                            # rider=rider,
                                            tags=[self._rname,self._jname])
            self._pg[pol][self._rname] = pg

        return True

    #------------------------------------------------------------------------------

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
            real = self._pgm[self._pg[pol][self._rname]].create_member (quals=station)
            imag = self._pgm[self._pg[pol][self._iname]].create_member (quals=station)
            mm[pol] = qnode(pol)(station) << Meq.ToComplex(real,imag)
        qnode(station) << Meq.Matrix22(mm[pols[0]],0.0, 0.0,mm[pols[1]])
        return qnode(station)







#============================================================================================
#============================================================================================

class JJones (Joneset22):
    """Class that represents a set of 2x2 JJones matrices.
    Each of the 4 complex elements of a station Jones matrix
    is assumed to be independent. The parameters are their real
    and imaginary parts (i.e. 8 real parameters per station).
    JJones is the same for linear and circular polarizations."""

    def __init__(self, ns=None, name='JJones', quals=[],
                 namespace=None,
                 diagonal=False,
                 polrep='linear',
                 telescope=None, band=None,
                 override=None,
                 stations=None,
                 mode='nosolve'):

        self._jname = 'JJones'
        self._diagonal = diagonal
        Joneset22.__init__(self, ns=ns, quals=quals, name=name,
                           namespace=namespace,
                           polrep=polrep, telescope=telescope, band=band,
                           stations=stations,
                           mode=mode)
        
        # Define the list of (groups of) parmgroups to be used in the TDL menu: 
        self._TDLCompileOption_tobesolved = [None, self._jname, 'Jdiag']

        self.history(override)
        return None

    #------------------------------------------------------------------------------

    def TDLCompileOptions (self):
        """Define a list of TDL options that control the structure of the
        Jones matrix."""
        oolist = []

        key = '_diagonal'
        if not self._TDLCompileOption.has_key(key):
            doc = 'If True, the JJones matrix is diagonal'
            opt = [self._diagonal, not self._diagonal]
            oo = TDLOption(key, 'diagonal elements only', opt,
                           doc=doc, namespace=self)
            self._TDLCompileOption[key] = oo
            oo.when_changed(self._callback_diagonal)
            self._callback_diagonal(self._diagonal)
            self.tdloption_reset[key] = opt[0]
        oolist.append(self._TDLCompileOption[key])
        
        # Finished: Return a list of option objects:
        return oolist
    

    def _callback_diagonal (self, diagonal):
        """Called when TDLOPtion _diagonal is changed"""
        active = ['J11real','J11imag','J22real','J22imag']
        if not diagonal:
            active.extend(['J12real','J12imag','J21real','J21imag']) 
        return self._pgm.active_groups(new=active)


    #------------------------------------------------------------------------------

    def define_parmgroups(self):
        """Define the various primary ParmGroups"""
        self.define_parmgroups_preamble()
        self._pg = dict()
        dev = self._pgm.simuldev_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz='{10e6~10%}')

        for ename in ['J11','J22']:
            self._pg[ename] = dict()
            for rim in ['real','imag']:
                default = 0.0
                constraint = dict(sum=0.0)
                if rim=='real':
                    default = 1.0
                    constraint = dict(product=1.0)
                pg = self._pgm.define_parmgroup(ename+rim,
                                                descr=rim+' part of matrix element '+ename,
                                                default=default, unit='Jy',
                                                tiling=None, time_deg=0, freq_deg=0,
                                                mode=self._mode,
                                                simuldev=dev,
                                                constraint=constraint,
                                                # override=override,
                                                tags=[self._jname,'Jdiag'])
                self._pg[ename][rim] = pg

        # if not self._diagonal:
        if True:
            for ename in ['J12','J21']:
                self._pg[ename] = dict()
                for rim in ['real','imag']:
                    pg = self._pgm.define_parmgroup(ename+rim, 
                                                    descr=rim+' part of matrix element '+ename,
                                                    default=0.0, unit='Jy',
                                                    tiling=None, time_deg=0, freq_deg=0,
                                                    mode=self._mode,
                                                    simuldev=dev,
                                                    constraint=dict(sum=0.0),
                                                    # override=override,
                                                    tags=[self._jname,'Joffdiag'])
                    self._pg[ename][rim] = pg 

        return True

    #------------------------------------------------------------------------------

    def make_jones_matrix (self, station):
        """Make the Jones matrix for the specified station"""
        qnode = self.ns[self._jname]                   
        if not qnode.must_define_here(self):
            s = '** '+str(self.name)+': nodename clash: '+str(qnode)
            raise ValueError, s
        self._matrixet = qnode
        enames = ['J11','J12','J21','J22']
        mm = dict(J12=0.0, J21=0.0)
        for ename in self._pg.keys():
            real = self._pgm[self._pg[ename]['real']].create_member (quals=station)
            imag = self._pgm[self._pg[ename]['imag']].create_member (quals=station)
            mm[ename] = self.ns[ename](station) << Meq.ToComplex(real,imag)
        qnode(station) << Meq.Matrix22(mm[enames[0]],mm[enames[1]],
                                 mm[enames[2]],mm[enames[3]])
        return qnode(station)





#============================================================================================
#============================================================================================

class FJones (Joneset22):
    """Class that represents a set of 2x2 FJones matrices,
    which model the ionospheric Faraday rotation, 
    for either polarization representations (linear or circular).
    This FJones is assumed to be large-scale compared to the array size,
    i.e. it is the same for all stations, and the entire FOV."""

    def __init__(self, ns=None, name='FJones', quals=[], 
                 namespace=None,
                 polrep='linear', telescope=None, band=None,
                 override=None,
                 stations=None,
                 mode='nosolve'):
        
        self._jname = 'FJones'
        Joneset22.__init__(self, ns=ns, quals=quals, name=name,
                           namespace=namespace,
                           polrep=polrep, telescope=telescope, band=band,
                           stations=stations,
                           mode=mode)
        
        # Define the list of (groups of) parmgroups to be used in the TDL menu: 
        self._TDLCompileOption_tobesolved = [None, self._jname, 'RM'] 

        self.history(override)
        return None

    #------------------------------------------------------------------------------

    def define_parmgroups(self):
        """Define the various primary ParmGroups"""
        self.define_parmgroups_preamble()
        self._pg = dict()
        self._rname = 'RM'       
        dev = self._pgm.simuldev_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz=None)
        pg = self._pgm.define_parmgroup(self._rname,  
                                        descr='Faraday Rotation Measure (rad/m2)',
                                        default=0.0, unit='rad/m2',
                                        mode=self._mode,
                                        simuldev=dev,
                                        # override=override,
                                        tags=[self._rname,self._jname])
        self._pg[self._rname] = pg
        return True

    #------------------------------------------------------------------------------

    def make_jones_matrix (self, station):
        """Make the Jones matrix for the specified station"""
        polrep = self.polrep()
        qnode = self.ns[self._jname](polrep)                   

        # Since FJones is assumed to be the same for all stations (...?),
        # all station Jones matrices qnode(station) are the same (i.e. qnode).
        # So, define the qnode subtree only once.
        
        if not qnode.initialized():
            self._matrixet = qnode
            
            RM = self._pgm[self._pg[self._rname]].create_member()
            wvl = qnode('lambda') << Meq.Divide(3e8, Meq.Freq)
            wvl2 = qnode('lambda2') << Meq.Sqr(wvl)               # lambda squared
            farot = qnode('farot') << (RM * wvl2)                 # Faraday rotation angle
        
            # Make the (overall) 2x2 Fjones matrix:
            if polrep=='circular':
                # Circular pol: The Faraday rotation is just a phase effect:
                farot2 = qnode('farot2') << farot/2
                F11 = qnode('F11') << Meq.Polar(1.0, farot2)
                F22 = qnode('F22') << Meq.Polar(1.0, qnode('negate') << Meq.Negate(farot2))
                qnode << Meq.Matrix22(F11,0.0,0.0,F22)

            else:
                # Linear pol: The Faraday rotation is a (dipole) rotation:
                cos = qnode('cos') << Meq.Cos(farot)
                sin = qnode('sin') << Meq.Sin(farot)
                sinneg = qnode('sinneg') << Meq.Negate(sin)
                qnode << Meq.Matrix22(cos,sin,sinneg,cos)

        qnode(station) << Meq.Identity(qnode)
        return qnode(station)










     
#===============================================================
# Test routine (with meqbrowser):
#===============================================================


if False:
    j22 = Joneset22(quals=[], mode='simulate')
    j22.TDLCompileOptionsMenu()
    j22.display()
    
if False:
    TDLCompileMenu('Jones options',
                   GJones().TDLCompileOptionsMenu(),
                   BJones().TDLCompileOptionsMenu(),
                   JJones().TDLCompileOptionsMenu(),
                   FJones().TDLCompileOptionsMenu(),
                   );
if False:
    TDLCompileMenu('Jones options',
                   BJones().TDLCompileOptionsMenu(),
                   BJones(namespace='xxx').TDLCompileOptionsMenu(),
                   JJones(namespace='yyy').TDLCompileOptionsMenu(),
                   );

def _define_forest(ns):

    cc = []
    jj = []
    mode = 'simulate'

    j22.nodescope(ns)

    if 0:
        jones = GJones(ns, quals=[], mode=mode)
        jj.append(jones)
        # cc.append(jones._pgm.bundle(combine='Composer'))
        # cc.append(jones._pgm.plot_rvsi())
        # jones.bookpage(4)
        # cc.append(jones.visualize('rvsi'))          # default is rvsi
        # cc.append(jones.visualize('timetracks'))
        # cc.append(jones.visualize('spectra'))
        # jones.display(full=True)

    if 0:
        j2 = GJones(ns, quals=[], mode='nosolve')
        cc.append(j2.visualize())
        # j2.display(full=True)

    if 0:
        jones = BJones(ns, quals=[], simulate=simulate)
        jj.append(jones)
        # cc.append(jones.visualize())
        # cc.append(jones.visualize('spectra'))
        # jones.display(full=True)

    if 0:
        jones = JJones(ns, quals=[], simulate=simulate)
        jj.append(jones)
        # cc.append(jones.visualize())
        # jones.display(full=True)

    if 0:
        jones = FJones(ns, quals=['L'], simulate=simulate, polrep='linear')
        jj.append(jones)
        # cc.append(jones.visualize())
        jones.display(full=True)
        # jones.display_parmgroups(full=False)

    if 0:
        jones = FJones(ns, quals=['C'], simulate=simulate, polrep='circular')
        jj.append(jones)
        # cc.append(jones.visualize())
        jones.display(full=True)

    if 0:
        jseq = Joneseq22 (ns, jj, quals='mmm')
        cc.append(jseq._pgm.bundle())
        cc.append(jseq._pgm.compare('GphaseA','GphaseB'))
        cc.append(jseq._pgm.plot_rvsi())
        cc.append(jseq.visualize('*'))
        jseq.display(full=True)
        jseq.history().display(full=True)

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
        jones = GJones(ns, quals='3c84', mode='simulate')
        jones.make_jones_matrices()
        jj.append(jones)
        # jones.visualize()
        jones.TDLCompileOptionsMenu()
        jones.display(full=True, recurse=10)

    if 0:
        j22 = jones()
        j22 = jones(1)
        j22 = jones([2])
        j22 = jones(5)

    if 1:
        jones = BJones(ns, quals=['3c84'], mode='nosolve', telescope='WSRT', band='21cm')
        jj.append(jones)
        # jones.visualize()
        jones.display(full=True)

    if 1:
        jones = JJones(ns, quals=['3c84'], diagonal=True, mode='simulate')
        jj.append(jones)
        jones.display(full=True)

    if 1:
        jones = FJones(ns, polrep='linear',mode='simulate' )
        # jones = FJones(ns, polrep='circular', quals='3c89', mode='simulate')
        jj.append(jones)
        # jones.visualize()
        jones.display(full=True, recurse=12)

    if 1:
        jones.history().display(full=True)

    #..........................................................

    if 0:
        jseq = Joneseq22 (ns, jj, quals='mmm')
        jseq.display(full=True)
        jseq.history().display(full=True)


#===============================================================
    
