# file: ../Grunt/Joneset22.py

# History:
# - 25dec2006: creation
# - 14jan2007: keep only generic G/J/FJones
# - 29jan2007: added BJones

# Description:

# The Joneset22 class is a base-class for classes that define and
# encapsulate a set of 2x2 station Jones matrices.

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

from Timba.Contrib.JEN.Grunt import Matrixet22

from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect

from copy import deepcopy

#======================================================================================

class Joneset22 (Matrixet22.Matrixet22):
    """Base class that represents a set of 2x2 Jones matrices.
    Derived from the class Matrixet22."""

    def __init__(self, ns, quals=[], label='<j>', descr='<descr>',
                 stations=None, polrep=None,
                 telescope=None, band=None,
                 simulate=False):

        # List of (array) station indices:
        indices = deepcopy(stations)
        if indices==None:
            indices = range(1,4)                     # for testing convenience....

        # Some specific information about the target instrument:
        self._telescope = telescope
        self._band = band

        # Initialise its Matrixet22 object:
        Matrixet22.Matrixet22.__init__(self, ns, quals=quals, label=label, descr=descr,
                                       polrep=polrep, 
                                       indices=indices, simulate=simulate)

        # Some telescope-specific information:
        self._telescope = telescope                  # e.g. WSRT or VLA
        self._band = band                            # e.g. 21cm or LFFE
        if self._telescope:
            self._quals.append(self._telescope)
            self._pgm._quals.append(self._telescope) # kludge....
            if self._band:
                self._quals.append(self._band)
                self._pgm._quals.append(self._band)  # kludge....

        # Finished:
        return None

    #-------------------------------------------------------------------

    def stations(self):
        """Return a list of (array) stations"""
        return self.indices()                        # kept in Matrixet22

    #-------------------------------------------------------------------

    def telescope(self):
        """Return the name of the telescope (if any) for which this Jones matrix is valid"""
        return self._telescope                

    def band(self):
        """Return the name of the freq band (if any) for which this Jones matrix is valid"""
        return self._band                

    #-------------------------------------------------------------------

    def _pols_matrel(self):
        """Convenience function to make a dict with pols as field-names,
        which gives the relevant Matrixet22 elements for the 2 pols.
        Used e.g. in GJones to indicate that only the diagonal matrix
        elements should be used to solve for Ggain and Gphase."""
        pols = self.pols()
        matrel = dict()
        matrel[pols[0]] = 'm11'
        matrel[pols[1]] = 'm22'
        return matrel

    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += '  '+str(self.label())
        if self._telescope:
            ss += ' '+str(self._telescope)
            if self._band:
                ss += ' '+str(self._band)
        else:
            ss += '  pols='+str(self._pols)
        ss += '  n='+str(len(self.stations()))
        ss += '  quals='+str(self.quals())
        return ss


    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        print '   - stations ('+str(len(self.stations()))+'): '+str(self.stations())
        return True



#=================================================================================================
# Make a Joneset22 object that is a sequence (matrix multiplication) of Jones matrices
#=================================================================================================

def Joneseq22 (joneslist=None, qual=None):
    """Return a Jones22 object that contains an (item-by-item) matrix multiplication
    of the matrices of the list (joneslist) of two or more Joneset22 objects."""

    if len(joneslist)==0:
        raise ValueError, 'joneslist should have at least one item'
    
    elif len(joneslist)==1:
        jnew = joneslist[0]
        return jnew
    
    # First create a new Jonset22 object with label/quals/descr that are
    # suitable combinations of those of the contributing Joneset22 objects: 
    ns = joneslist[0]._ns
    label = joneslist[0].label()
    quals = joneslist[0].quals()
    quals.remove(label)
    descr = joneslist[0].label()+': '+joneslist[0].descr()
    stations = joneslist[0].stations()
    for jones in joneslist[1:]:
        label += jones.label()
        descr += '\n '+jones.label()+': '+jones.descr()
        qq = jones.quals()
        qq.remove(jones.label())
        for q in qq:
            if not q in quals: quals.append(q)
    quals.insert(0,label)
    jnew = Joneset22 (ns, quals=quals, label=label, stations=stations) 
        
    # Then create the new Jones matrices by matrix-multiplication:
    name = 'Joneseq'
    for i in jnew.list_indices():
        cc = []
        for jones in joneslist:
            cc.append(jones._matrixet(*i))
        ns[name](*quals)(*i) << Meq.MatrixMultiply(*cc)
    jnew.matrixet(new=ns[name](*quals))
    
    # Merge the parmgroups of the various Jones matrices:
    for jones in joneslist:
        jnew._pgm.merge(jones._pgm)

    # Return the new Joneset22 object:
    return jnew







#=================================================================================================
# Some generic (telescope-independent) Joneset22 objects
# (for telescope-specific ones, see e.g. Grunting/WSRT_Jones.py)
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


    def __init__(self, ns, quals=[], label='G',
                 polrep=None, telescope=None, band=None,
                 override=None,
                 stations=None, simulate=False):
        
        Joneset22.__init__(self, ns, quals=quals, label=label,
                           polrep=polrep, telescope=telescope, band=band,
                           stations=stations, simulate=simulate)

        # Parameter group names:
        quals = self.quals()               
        pols = self.pols()                        # e.g. ['X','Y']
        pname = self.label()+'phase'
        gname = self.label()+'gain'
        jname = self.label()+'Jones'

        # Define the various primary ParmGroups:
        for pol in pols:
            matrel = self._pols_matrel()[pol]     # i.e. 'm11' or 'm22'
            self.define_parmgroup(pname+pol, descr=pol+'-dipole phases',
                                  quals=quals,
                                  default=dict(c00=0.0, unit='rad', tfdeg=[0,0],
                                               subtile_size=1),
                                  constraint=dict(sum=0.0, first=0.0),
                                  simul=dict(Psec=200),
                                  override=override,
                                  rider=dict(matrel=matrel),
                                  tags=[pname,jname])
            self.define_parmgroup(gname+pol, descr=pol+'-dipole gains',
                                  quals=quals,
                                  default=dict(c00=1.0,
                                               tfdeg=[2,0],
                                               # constrain_min=0.1, constrain_max=10.0,
                                               unit=None),
                                  constraint=dict(product=1.0),
                                  simul=dict(Psec=500),
                                  override=override,
                                  rider=dict(matrel=matrel),
                                  tags=[gname,jname])

        # Make the Jones matrices per station:
        quals = self.quals()               
        for s in self.stations():
            mm = dict()
            for pol in pols:
                phase = self.create_parmgroup_entry(pname+pol, s, quals=quals)
                gain = self.create_parmgroup_entry(gname+pol, s, quals=quals)
                mm[pol] = self._ns[jname+pol](*quals)(s) << Meq.Polar(gain,phase)
            self._ns[jname](*quals)(s) << Meq.Matrix22(mm[pols[0]],0.0,
                                                       0.0,mm[pols[1]])
        self.matrixet(new=self._ns[jname](*quals))
        # Make some secondary (composite) ParmGroups:
        self.define_gogs(jname)
        return None


#--------------------------------------------------------------------------------------------

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

    def __init__(self, ns, quals=[], label='B',
                 polrep=None, telescope=None, band=None,
                 tfdeg=[0,5],
                 override=None,
                 stations=None, simulate=False):
        
        Joneset22.__init__(self, ns, quals=quals, label=label,
                           polrep=polrep, telescope=telescope, band=band,
                           stations=stations, simulate=simulate)

        pols = self.pols()                                # e.g. ['X','Y']
        quals = self.quals()
        iname = self.label()+'imag'
        rname = self.label()+'real'
        jname = self.label()+'Jones'

        # Define the various primary ParmGroups:
        for pol in pols:
            matrel = self._pols_matrel()[pol]             # i.e. 'm11' or 'm22'
            self.define_parmgroup(iname+pol, descr=pol+'-IF bandpass imag.part',
                                  quals=quals,
                                  default=dict(c00=0.0, unit=None, tfdeg=tfdeg,
                                               subtile_size=1),
                                  simul=dict(PMHz=10),
                                  override=override,
                                  rider=dict(matrel=matrel),
                                  tags=[iname,jname])
            self.define_parmgroup(rname+pol, descr=pol+'-IF bandpass real.part',
                                  quals=quals,
                                  default=dict(c00=1.0, unit=None, tfdeg=tfdeg),
                                  simul=dict(PMHz=10),
                                  override=override,
                                  rider=dict(matrel=matrel),
                                  tags=[rname,jname])
        # Make the Jones matrices per station:
        for s in self.stations():
            mm = dict()
            for pol in pols:
                imag = self.create_parmgroup_entry(iname+pol, s, quals=quals)
                real = self.create_parmgroup_entry(rname+pol, s, quals=quals)
                mm[pol] = self._ns[jname+pol](*quals)(s) << Meq.ToComplex(real,imag)
            self._ns[jname](*quals)(s) << Meq.Matrix22(mm[pols[0]],0.0,
                                                       0.0,mm[pols[1]])
        self.matrixet(new=self._ns[jname](*quals))
        # Make some secondary (composite) ParmGroups:
        self.define_gogs(jname)
        return None







#--------------------------------------------------------------------------------------------

class JJones (Joneset22):
    """Class that represents a set of 2x2 JJones matrices.
    Each of the 4 complex elements of a station Jones matrix
    is assumed to be independent. The parameters are their real
    and imaginary parts (i.e. 8 real parameters per station).
    JJones is the same for linear and circular polarizations."""

    def __init__(self, ns, quals=[], label='J',
                 diagonal=False,
                 polrep=None, telescope=None, band=None,
                 override=None,
                 stations=None, simulate=False):

        Joneset22.__init__(self, ns, quals=quals, label=label,
                           polrep=polrep, telescope=telescope, band=band,
                           stations=stations, simulate=simulate)
        
        quals = self.quals()
        jname = self.label()+'Jones'
        enames = ['J11','J12','J21','J22']

        # Define the various primary ParmGroups:
        ee = []
        for ename in ['J11','J22']:
            ee.append(ename)
            for rim in ['real','imag']:
                default = 0.0
                constraint = dict(sum=0.0)
                if rim=='real':
                    default = 1.0
                    constraint = dict(product=1.0)
                self.define_parmgroup(ename+rim,
                                      quals=quals,
                                      descr=rim+' part of matrix element '+ename,
                                      default=dict(c00=default),
                                      constraint=constraint,
                                      simul=dict(Psec=200),
                                      override=override,
                                      tags=[jname,'Jdiag'])
        if not diagonal:
            for ename in ['J12','J21']:
                ee.append(ename)
                for rim in ['real','imag']:
                    self.define_parmgroup(ename+rim,
                                          quals=quals,
                                          descr=rim+' part of matrix element '+ename,
                                          default=dict(c00=0.0),
                                          constraint=dict(sum=0.0),
                                          simul=dict(Psec=200),
                                          override=override,
                                          tags=[jname,'Joffdiag'])

        # Make the Jones matrices per station:
        for s in self.stations():
            mm = dict(J12=0.0, J21=0.0)
            for ename in ee:
                real = self.create_parmgroup_entry(ename+'real', s, quals=quals)
                imag = self.create_parmgroup_entry(ename+'imag', s, quals=quals)
                mm[ename] = self._ns[ename](*quals)(s) << Meq.ToComplex(real,imag)
            self._ns[jname](*quals)(s) << Meq.Matrix22(mm[enames[0]],mm[enames[1]],
                                                       mm[enames[2]],mm[enames[3]])
        self.matrixet(new=self._ns[jname](*quals))
        # Make some secondary (composite) ParmGroups:
        self.define_gogs(jname)
        return None



#--------------------------------------------------------------------------------------------

class FJones (Joneset22):
    """Class that represents a set of 2x2 FJones matrices,
    which model the ionospheric Faraday rotation, 
    for either polarization representations (linear or circular).
    This FJones is assumed to be large-scale compared to the array size,
    i.e. it is the same for all stations, and the entire FOV."""

    def __init__(self, ns, quals=[], label='F',
                 polrep='linear', telescope=None, band=None,
                 override=None,
                 stations=None, simulate=False):
        
        Joneset22.__init__(self, ns, quals=quals, label=label,
                           polrep=polrep, telescope=telescope, band=band,
                           stations=stations, simulate=simulate)
        
        quals = self.quals()
        polrep = self.polrep()
        rname = self.label()+'rm'       
        jname = self.label()+'Jones'

        # Define the primary ParmGroup:
        self.define_parmgroup(rname, descr='Faraday Rotation Measure (rad/m2)',
                              quals=quals,
                              default=dict(c00=0.0),
                              simul=dict(),
                              override=override,
                              tags=[rname,jname])

        RM = self.create_parmgroup_entry(rname, quals=quals)  # Rotation Measure (rad/m2)
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
            
        self.matrixet(new=self._ns[jname](*quals)(polrep))
        # Make some secondary (composite) ParmGroups:
        self.define_gogs(jname)
        return None




     
#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []
    simulate = True

    jones = GJones(ns, quals=[], simulate=simulate)
    cc.append(jones.visualize())
    # jones.display(full=True)
    if True:
        j2 = GJones(ns, quals=[], simulate=False)
        cc.append(j2.visualize())
        # j2.display(full=True)


    jones = BJones(ns, quals=[], simulate=simulate)
    cc.append(jones.visualize())
    # jones.display(full=True)

    jones = JJones(ns, quals=[], simulate=simulate)
    cc.append(jones.visualize())
    # jones.display(full=True)

    jones = FJones(ns, quals=['L'], simulate=simulate, polrep='linear')
    cc.append(jones.visualize())
    jones.display(full=True)
    # jones.display_parmgroups(full=False)

    jones = FJones(ns, quals=['C'], simulate=simulate, polrep='circular')
    cc.append(jones.visualize())
    jones.display(full=True)

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
       


#===============================================================
# Test routine:
#===============================================================

if __name__ == '__main__':
    ns = NodeScope()

    jj = []

    if 1:
        G = GJones(ns, quals=['3c84','xxx'], simulate=False)
        jj.append(G)
        G.visualize()
        G.display(full=True)
        # G.display_NodeGroups()

    if 1:
        J = BJones(ns, quals=['xxx'])
        jj.append(J)
        J.display(full=True)

    if 0:
        # F = FJones(ns, polrep='linear')
        F = FJones(ns, polrep='circular')
        jj.append(F)
        F.display(full=True)

    if 0:
        J = JJones(ns, quals=['xxx'], diagonal=False)
        jj.append(J)
        J.display(full=True)

    if 1:
        jseq = Joneseq22 (jj)
        jseq.display(full=True)

#===============================================================
    
