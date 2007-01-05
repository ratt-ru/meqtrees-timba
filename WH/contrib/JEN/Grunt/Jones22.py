# file: ../Grunt/Jones22.py

# History:
# - 25dec2006: creation

# Description:

# The Jones22 class is a base-class for classes that define and
# encapsulate groups of 2x2 station Jones matrices.

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

from Qualifiers import *
from ParmGroup import *
from Matrix22 import *

# from Timba.Contrib.JEN.Grunt import ParmGroup
from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect

from copy import deepcopy

#======================================================================================

class Jones22 (Matrix22):
    """Class that represents a set of 2x2 Jones matrices"""

    def __init__(self, ns, quals=[], label='<j>',
                 telescope=None, stations=None, polrep=None,
                 simulate=False):

        # Telescope-specific information:
        self._telescope = telescope                  # e.g. WSRT
        indices = deepcopy(stations)                 # list of (array) station indices
        self._polrep = polrep                        # polarization representation (linear, circular)
        self._mount = None                           # Antenna mount (equatotial, altaz, None, ...)
        self._diam = None                            # antenna diameter (m)

        if self._telescope=='WSRT':
            if indices==None: indices = range(1,15)
            self._polrep = 'linear'
            self._mount = 'equatorial'
            self._diam = 25
        elif self._telescope=='LOFAR':
            if indices==None: indices = range(1,31)
            self._polrep = 'linear'
            self._mount = 'horizontal'
            self._diam = 60
        elif self._telescope=='VLA':
            if indices==None: indices = range(1,28)
            self._polrep = 'circular'
            self._mount = 'altaz'
            self._diam = 25
        elif self._telescope=='ATCA':
            if indices==None: indices = range(1,7)
            self._polrep = 'linear'
            self._mount = 'altaz'
            self._diam = 25
        elif self._telescope=='GMRT':
            if indices==None: indices = range(1,31)
            self._polrep = 'linear'
            self._mount = 'altaz'
            self._diam = 45
        elif indices==None:
            indices = range(1,4)              # for testing convenience....

        self._pols = ['A','B']
        if self._polrep == 'linear':
            self._pols = ['X','Y']
        elif self._polrep == 'circular':
            self._pols = ['R','L']

        # Initialise its Matrix22 object:
        Matrix22.__init__(self, ns, quals=quals, label=label,
                          indices=indices, simulate=simulate)

        return None

    #-------------------------------------------------------------------

    def stations(self):
        """Return a list of (array) stations"""
        return self.indices()                        # kept in Matrix22

    #-------------------------------------------------------------------

    def telescope(self):
        """Return the name of the relevant telescope (e.g. WSRT)"""
        return self._telescope

    def polrep(self):
        """Return the polarization representation (linear, circular, None)"""
        return self._polrep

    def pols(self):
        """Return the list of 2 polarization names (e.g. ['X','Y'])"""
        return self._pols

    def _pols_matrel(self):
        """Helper function to make a dict of Matrix22 elements for the 2 pols"""
        matrel = dict()
        pols = self.pols()
        matrel[pols[0]] = 'm11'
        matrel[pols[1]] = 'm22'
        return matrel

    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += '  '+str(self.label())
        if self._telescope:
            ss += '  '+str(self._telescope)
        else:
            ss += '  pols='+str(self._pols)
        ss += '  n='+str(len(self.stations()))
        ss += '  quals='+str(self.quals())
        return ss


    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        print '   - stations ('+str(len(self.stations()))+'): '+str(self.stations())
        print '   - polrep: '+str(self._polrep)+', pols='+str(self._pols)
        print '   - Antenna mount: '+str(self._mount)+', diam='+str(self._diam)+'(m)'
        return True


    #-------------------------------------------------------------------










#=================================================================================================
# Example of an actual Jones22 matrix
#=================================================================================================

class GJones (Jones22):
    """Class that represents a set of 2x2 GJones matrices,
    which model the (complex) gains due to electronics
    and (optionally) the tropospheric phase (a.k.a. TJones).
    GJones is a uv-plane effect, i.e. it is valid for the entire FOV.
    GJones is the same for linear and circular polarizations."""

    def __init__(self, ns, quals=[], label='G',
                 telescope=None, stations=None, polrep='linear',
                 simulate=False):
        Jones22.__init__(self, ns, quals=quals, label=label,
                       telescope=telescope, stations=stations, polrep=polrep,
                       simulate=simulate)
        pols = self.pols()                        # e.g. ['X','Y']
        quals = self.quals()
        pname = self.label()+'phase'
        gname = self.label()+'gain'
        jname = self.label()+'Jones'
        # Define the various primary ParmGroups:
        for pol in pols:
            matrel = self._pols_matrel()[pol]     # i.e. 'm11' or 'm22'
            self.define_parmgroup(pname+pol, descr=pol+'-dipole phases',
                                  Tsec=200,
                                  matrel=matrel, tags=[pname,jname])
            self.define_parmgroup(gname+pol, descr=pol+'-dipole gains',
                                  default=1.0,
                                  matrel=matrel, tags=[gname,jname])
        # Make the Jones matrices per station:
        for s in self.stations():
            mm = dict()
            for pol in pols:
                phase = self.create_parmgroup_entry(pname+pol, s)
                gain = self.create_parmgroup_entry(gname+pol, s)
                mm[pol] = self._ns[jname+pol](*quals)(s) << Meq.Polar(gain,phase)
            self._ns[jname](*quals)(s) << Meq.Matrix22(mm[pols[0]],0.0,
                                                       0.0,mm[pols[1]])
        self._matrix = self._ns[jname](*quals)
        # Make some secondary (composite) ParmGroups:
        self.define_gogs(jname)
        return None

#--------------------------------------------------------------------------------------------

class EJones (Jones22):
    """Class that represents a set of 2x2 EJones matrices,
    which model the station beamshapes.
    EJones is an image-plane effect."""

    def __init__(self, ns, quals=[], label='E',
                 telescope=None, stations=None, polrep='linear',
                 simulate=False):
        Jones22.__init__(self, ns, quals=quals, label=label,
                       telescope=telescope, stations=stations, polrep=polrep,
                       simulate=simulate)
        pols = self._pols
        quals = self.quals()
        pname = self.label()+'phase'
        gname = self.label()+'gain'
        jname = self.label()+'Jones'
        # Define the various primary ParmGroups:
        for pol in pols:
            matrel = self._pols_matrel()[pol]     # i.e. 'm11' or 'm22'
            self.define_parmgroup(pname+pol, descr=pol+'-dipole phases',
                                  Tsec=200,
                                  matrel=matrel, tags=[pname,jname])
            self.define_parmgroup(gname+pol, descr=pol+'-dipole gains',
                                  default=1.0,
                                  matrel=matrel, tags=[gname,jname])
        # Make the Jones matrices per station:
        for s in self.stations():
            mm = dict()
            for pol in pols:
                phase = self.create_parmgroup_entry(pname+pol, s)
                gain = self.create_parmgroup_entry(gname+pol, s)
                mm[pol] = self._ns[jname+pol](*quals)(s) << Meq.Polar(gain,phase)
            self._ns[jname](*quals)(s) << Meq.Matrix22(mm[pols[0]],0.0,
                                                       0.0,mm[pols[1]])
        self._matrix = self._ns[jname](*quals)
        # Make some secondary (composite) ParmGroups:
        self.define_gogs(jname)
        return None



#--------------------------------------------------------------------------------------------
class FJones (Jones22):
    """Class that represents a set of 2x2 FJones matrices,
    for both polarization representations (linear and circular).
    For the moment, the ionospheric Faraday rotation is assumen
    to be the same for all stations, and the entire FOV."""

    def __init__(self, ns, quals=[], label='F',
                 telescope=None, stations=None, polrep='linear',
                 simulate=False):
        Jones22.__init__(self, ns, quals=quals, label=label,
                       telescope=telescope, stations=stations, polrep=polrep,
                       simulate=simulate)
        quals = self.quals()
        polrep = self.polrep()
        rname = self.label()+'rm'       
        jname = self.label()+'Jones'

        # Define the primary ParmGroup:
        self.define_parmgroup(rname, descr='Faraday Rotation Measure (rad/m2)',
                              tags=[rname,jname])

        RM = self.create_parmgroup_entry(rname)               # Rotation Measure (rad/m2)
        wvl = self._ns << Meq.Divide(3e8, self._ns << Meq.Freq())
        wvl2 = self._ns << Meq.Sqr(wvl)                       # lambda squared
        farot = self._ns.farot(*quals) << (RM * wvl2)         # Faraday rotation angle
        
        # Make the (overall) 2x2 Fjones matrix:
        if polrep=='circular':
            # Circular pol: The Faraday rotation is just a phase effect:
            farot2 = self._ns << farot/2
            F11 = self._ns << Meq.Polar(1.0, farot2)
            F22 = self._ns << Meq.Polar(1.0, self._ns << Meq.Negate(farot2))
            fmat = self._ns[jname](*quals)(polrep) << Meq.Matrix22(F11,0.0,0.0,F22)

        else:
            # Linear pol: The Faraday rotation is a (dipole) rotation:
            cos = self._ns << Meq.Cos(farot)
            sin = self._ns << Meq.Sin(farot)
            sinneg = self._ns << Meq.Negate(sin)
            fmat = self._ns[jname](*quals)(polrep) << Meq.Matrix22(cos,sin,sinneg,cos)

        # The station Jones matrices are all the same (fmat):  
        for s in self.stations():
            self._ns[jname](*quals)(polrep)(s) << Meq.Identity(fmat)
            
        self._matrix = self._ns[jname](*quals)(polrep)
        # Make some secondary (composite) ParmGroups:
        self.define_gogs(jname)
        return None



#--------------------------------------------------------------------------------------------

class DJones (Jones22):
    """Class that represents a set of 2x2 DJones matrices"""

    def __init__(self, ns, quals=[], label='D',
                 telescope=None, stations=None, polrep='linear',
                 coupled_dang=True, coupled_dell=True,
                 simulate=False):
        Jones22.__init__(self, ns, quals=quals, label=label,
                       telescope=telescope, stations=stations, polrep=polrep,
                       simulate=simulate)
        pols = self._pols
        quals = self.quals()
        dname = self.label()+'dang'
        ename = self.label()+'dell'
        pname = self.label()+'pzd'
        jname = self.label()+'Jones'

        # Define the various primary ParmGroups:
        if coupled_dang:
            self.define_parmgroup(dname, descr='dipole angle error',
                                  tags=[dname,jname])
        else:
            for pol in pols:
                self.define_parmgroup(dname+pol, descr=pol+'-dipole angle error',
                                      tags=[dname,jname])
        if coupled_dell:
            self.define_parmgroup(ename, descr='dipole ellipticity',
                                  tags=[ename,jname])
        else:
            for pol in pols:
                self.define_parmgroup(ename+pol, descr=pol+'-dipole ellipticity',
                                      tags=[ename,jname])
        self.define_parmgroup(pname, descr='XY/RL phase-zero difference',
                              tags=[pname,jname])

        # Make the (overall) 2x2 PZD jones matrix:
        pzd = self.create_parmgroup_entry(pname)
        pzd2 = self._ns << pzd/2
        pzd2neg = self._ns << Meq.Negate(pzd2)
        pmat = self._ns[pname](*quals) << Meq.Matrix22(pzd2,0.0,0.0,pzd2neg)

        # Make the Jones matrices per station:
        for s in self.stations():

            # Dipole rotation angles:
            if coupled_dang:
                dang = self.create_parmgroup_entry(dname, s)
                cos = self._ns << Meq.Cos(dang)
                sin = self._ns << Meq.Sin(dang)
                sinneg = self._ns << Meq.Negate(sin)
                dmat = self._ns[dname](*quals)(s) << Meq.Matrix22(cos,sin,sinneg,cos)
            else:
                dang1 = self.create_parmgroup_entry(dname+pols[0], s)
                dang2 = self.create_parmgroup_entry(dname+pols[1], s)
                cos1 = self._ns << Meq.Cos(dang1)
                cos2 = self._ns << Meq.Cos(dang2)
                sin1 = self._ns << Meq.Negate(self._ns << Meq.Sin(dang1))
                sin2 = self._ns << Meq.Sin(dang2)
                dmat = self._ns[dname](*quals)(s) << Meq.Matrix22(cos1,sin1,sin2,cos2)


            # Dipole ellipticities:
            if coupled_dell:
                dell = self.create_parmgroup_entry(ename, s)
                cos = self._ns << Meq.Cos(dell)
                sin = self._ns << Meq.Sin(dell)
                isin = self._ns << Meq.ToComplex(0.0, sin)
                emat = self._ns[ename](*quals)(s) << Meq.Matrix22(cos,isin,isin,cos)
            else:
                dell1 = self.create_parmgroup_entry(ename+pols[0], s)
                dell2 = self.create_parmgroup_entry(ename+pols[1], s)
                cos1 = self._ns << Meq.Cos(dell1)
                cos2 = self._ns << Meq.Cos(dell2)
                isin1 = self._ns << Meq.ToComplex(0.0, self._ns << Meq.Sin(dell1))
                isin2 = self._ns << Meq.ToComplex(0.0, self._ns << Meq.Sin(dell2))
                isin2 = self._ns << Meq.Conj(isin2)
                emat = self._ns[ename](*quals)(s) << Meq.Matrix22(cos1,isin1,isin2,cos2)

            # Make the station Jones matrix by multiplying the sub-matrices:
            self._ns[jname](*quals)(s) << Meq.MatrixMultiply (dmat, emat, pmat)

        self._matrix = self._ns[jname](*quals)
        # Make some secondary (composite) ParmGroups:
        self.define_gogs(jname)
        return None



#--------------------------------------------------------------------------------------------

class JJones (Jones22):
    """Class that represents a set of 2x2 JJones matrices.
    Each of the 4 complex elements of a station Jones matrix
    is assumed to be independent. The parameters are their real
    and imaginary parts (i.e. 8 real parameters per station).
    JJones is the same for linear and circular polarizations."""

    def __init__(self, ns, quals=[], label='J',
                 diagonal=False,
                 telescope=None, stations=None,
                 simulate=False):
        Jones22.__init__(self, ns, quals=quals, label=label,
                       telescope=telescope, stations=stations,
                       simulate=simulate)
        quals = self.quals()
        jname = self.label()+'Jones'
        enames = ['J11','J12','J21','J22']
        ee = []
        # Define the various primary ParmGroups:
        for ename in ['J11','J22']:
            ee.append(ename)
            for rim in ['real','imag']:
                default = 0.0
                if rim=='real': default = 1.0
                self.define_parmgroup(ename+rim, default=default, Tsec=200,
                                      descr=rim+' part of matrix element '+ename,
                                      tags=[jname,'Jdiag'])
        if not diagonal:
            for ename in ['J12','J21']:
                ee.append(ename)
                for rim in ['real','imag']:
                    self.define_parmgroup(ename+rim, Tsec=200,
                                          descr=rim+' part of matrix element '+ename,
                                          tags=[jname,'Joffdiag'])

        # Make the Jones matrices per station:
        for s in self.stations():
            mm = dict(J12=0.0, J21=0.0)
            for ename in ee:
                real = self.create_parmgroup_entry(ename+'real', s)
                imag = self.create_parmgroup_entry(ename+'imag', s)
                mm[ename] = self._ns[ename](*quals)(s) << Meq.ToComplex(real,imag)
            self._ns[jname](*quals)(s) << Meq.Matrix22(mm[enames[0]],mm[enames[1]],
                                                       mm[enames[2]],mm[enames[3]])
        self._matrix = self._ns[jname](*quals)
        # Make some secondary (composite) ParmGroups:
        self.define_gogs(jname)
        return None





     
#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    dcolls = []
    simulate = True

    jones = GJones(ns, quals=[], simulate=simulate)
    dcolls.append(jones.visualize())
    # jones.display(full=True)

    jones = JJones(ns, quals=[], simulate=simulate)
    dcolls.append(jones.visualize())
    # jones.display(full=True)

    jones = DJones(ns, quals=[], simulate=simulate)
    dcolls.append(jones.visualize())
    # jones.display(full=True)

    jones = FJones(ns, quals=['L'], simulate=simulate, polrep='linear')
    dcolls.append(jones.visualize())
    jones.display(full=True)
    jones.display_parmgroups(full=False, composite=False)

    jones = FJones(ns, quals=['C'], simulate=simulate, polrep='circular')
    dcolls.append(jones.visualize())
    jones.display(full=True)

    ns.result << Meq.Composer(children=dcolls)
    return True

#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       


#===============================================================
# Test routine:
#===============================================================

if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        Gjones = GJones(ns, quals=['3c84','xxx'], simulate=False)
        Gjones.visualize()
        Gjones.display(full=True)
        # Gjones.display_parmgroups()

    if 0:
        # Djones = DJones(ns, coupled_dang=True, coupled_dell=True)
        Djones = DJones(ns, coupled_dang=False, coupled_dell=False)
        Djones.display(full=True)

    if 0:
        # Fjones = FJones(ns, polrep='linear')
        Fjones = FJones(ns, polrep='circular')
        Fjones.display(full=True)

    if 0:
        Jjones = JJones(ns, diagonal=False)
        Jjones.display(full=True)
        if 1:
            Gjones = GJones(ns, quals=['3c84','xxx'], simulate=True)
            Gjones.display(full=True)
            Gjones.multiply(Jjones)
            Gjones.display(full=True)

    if 0:
        Djones = DJones(ns)
        Djones.display()
        Gjones.multiply(Djones)
        Gjones.display()

#===============================================================
    
