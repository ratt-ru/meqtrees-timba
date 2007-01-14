# file: ../Grunting/WSRT_Joneset.py

# History:
# - 14jan2007: creation (from Grunt/Joneset22.py)

# Description:

# WSRT-specific set of Jones matrices, implemented as Joneset22 objects.


#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

from Timba.Contrib.JEN.Grunt import Joneset22



#=================================================================================================
#=================================================================================================

class GJones (Joneset22.GJones):
    """Class that represents a set of 2x2 WSRT GJones matrices,
    which model the (complex) gains due to electronics
    and (optionally) the tropospheric phase (a.k.a. TJones).
    GJones is a uv-plane effect, i.e. it is valid for the entire FOV."""

    def __init__(self, ns, quals=[], label='G',
                 stations=None, simulate=False):
        
        # Just use the generic GJones in Grunt/Joneset22.py
        Joneset22.GJones.__init__(self, ns, quals=quals, label=label,
                                  stations=stations, polrep='linear',
                                  simulate=simulate)
        return None


#--------------------------------------------------------------------------------------------

class JJones (Joneset22.JJones):
    """Class that represents a set of 2x2 WSRT JJones matrices.
    Each of the 4 complex elements of a station Jones matrix
    is assumed to be independent. The parameters are their real
    and imaginary parts (i.e. 8 real parameters per station)."""

    def __init__(self, ns, quals=[], label='J',
                 diagonal=False, stations=None, 
                 simulate=False):

        # Just use the generic JJones in Grunt/Joneset22.py
        Joneset22.JJones.__init__(self, ns, quals=quals, label=label,
                                  stations=stations, polrep='linear',
                                  simulate=simulate)
        return None


#--------------------------------------------------------------------------------------------
class FJones (Joneset22.FJones):
    """Class that represents a set of 2x2 WSRT FJones matrices.
    For the moment, the ionospheric Faraday rotation is assumed
    to be the same for all stations, and the entire FOV."""

    def __init__(self, ns, quals=[], label='F',
                 stations=None, simulate=False):
        
        # Just use the generic FJones in Grunt/Joneset22.py
        Joneset22.FJones.__init__(self, ns, quals=quals, label=label,
                                  stations=stations, polrep='linear',
                                  simulate=simulate)
        return None




#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------

class DJones (Joneset22.Joneset22):
    """Class that represents a set of 2x2 WSRT DJones matrices.
    They model the (on-axis) leakage if signal between the two dipoles,
    caused by small errors in dipole position angle (dang) and in dipole
    ellipticity (dell), and by the X/Y phase-zero-difference (PZD).
    - If coupled_dang=True (default), it is assumed that the dipole unit of
    a telescope is rotated as a whole (e.g. because of structural bending),
    so dang is the same for both dipoles (X and Y).
    - If coupled_dell=True (default), it is assumed that dellX=-dellY
    per telescope.
    - A non-zero PZD converts StokesU into StokesV."""

    def __init__(self, ns, quals=[], label='D',
                 stations=None, 
                 coupled_dang=True, coupled_dell=True,
                 simulate=False):
        
        Joneset22.Joneset22.__init__(self, ns, quals=quals, label=label,
                                     stations=stations, polrep='linear',
                                     simulate=simulate)
        pols = self._pols
        quals = self.quals()
        dname = self.label()+'dang'
        ename = self.label()+'dell'
        pname = self.label()+'pzd'
        jname = self.label()+'Jones'

        # Define the various primary ParmGroups:
        if coupled_dang:
            self._pgm.define_parmgroup(dname, descr='dipole angle error',
                                       tags=[dname,jname])
        else:
            for pol in pols:
                self._pgm.define_parmgroup(dname+pol, descr=pol+'-dipole angle error',
                                           tags=[dname,jname])
        if coupled_dell:
            self._pgm.define_parmgroup(ename, descr='dipole ellipticity',
                                       tags=[ename,jname])
        else:
            for pol in pols:
                self._pgm.define_parmgroup(ename+pol, descr=pol+'-dipole ellipticity',
                                           tags=[ename,jname])
        self._pgm.define_parmgroup(pname, descr='XY/RL phase-zero difference',
                                   tags=[pname,jname])

        # Make the (overall) 2x2 PZD jones matrix:
        pzd = self._pgm.create_parmgroup_entry(pname)
        pzd2 = self._ns << pzd/2
        m11 = self._ns << Meq.Polar(1.0, pzd2)
        m22 = self._ns << Meq.Polar(1.0, self._ns << Meq.Negate(pzd2))
        pmat = self._ns[pname](*quals) << Meq.Matrix22(m11,0.0,0.0,m22)


        # Make the Jones matrices per station:
        for s in self.stations():

            # Dipole rotation angles:
            if coupled_dang:
                dang = self._pgm.create_parmgroup_entry(dname, s)
                cos = self._ns << Meq.Cos(dang)
                sin = self._ns << Meq.Sin(dang)
                sinneg = self._ns << Meq.Negate(sin)
                dmat = self._ns[dname](*quals)(s) << Meq.Matrix22(cos,sin,sinneg,cos)
            else:
                dang1 = self._pgm.create_parmgroup_entry(dname+pols[0], s)
                dang2 = self._pgm.create_parmgroup_entry(dname+pols[1], s)
                cos1 = self._ns << Meq.Cos(dang1)
                cos2 = self._ns << Meq.Cos(dang2)
                sin1 = self._ns << Meq.Negate(self._ns << Meq.Sin(dang1))
                sin2 = self._ns << Meq.Sin(dang2)
                dmat = self._ns[dname](*quals)(s) << Meq.Matrix22(cos1,sin1,sin2,cos2)


            # Dipole ellipticities:
            if coupled_dell:
                dell = self._pgm.create_parmgroup_entry(ename, s)
                cos = self._ns << Meq.Cos(dell)
                sin = self._ns << Meq.Sin(dell)
                isin = self._ns << Meq.ToComplex(0.0, sin)
                emat = self._ns[ename](*quals)(s) << Meq.Matrix22(cos,isin,isin,cos)
            else:
                dell1 = self._pgm.create_parmgroup_entry(ename+pols[0], s)
                dell2 = self._pgm.create_parmgroup_entry(ename+pols[1], s)
                cos1 = self._ns << Meq.Cos(dell1)
                cos2 = self._ns << Meq.Cos(dell2)
                isin1 = self._ns << Meq.ToComplex(0.0, self._ns << Meq.Sin(dell1))
                isin2 = self._ns << Meq.ToComplex(0.0, self._ns << Meq.Sin(dell2))
                isin2 = self._ns << Meq.Conj(isin2)
                emat = self._ns[ename](*quals)(s) << Meq.Matrix22(cos1,isin1,isin2,cos2)

            # Make the station Jones matrix by multiplying the sub-matrices:
            self._ns[jname](*quals)(s) << Meq.MatrixMultiply (dmat, emat, pmat)

        self.matrixet(new=self._ns[jname](*quals))
        # Make some secondary (composite) ParmGroups:
        self._pgm.define_gogs(jname)
        return None




#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------

class EJones (Joneset22.Joneset22):
    """Class that represents a set of 2x2 WSRT EJones matrices,
    which model the WSRT telescope beamshapes (for the specified freq band).
    EJones is an image-plane effect."""

    def __init__(self, ns, quals=[], label='E',
                 stations=None, band='21cm',
                 simulate=False):

        # There are different EJones matrices for different freq bands:
        if band=='90cm':
            pass                                 # not yet implemented

        elif band=='LFFE':
            pass                                 # not yet implemented
        
        else:                                    # default
            EJones_21cm.__init__(self, ns, quals=quals, label=label,
                                 stations=stations, simulate=simulate)
        return None


#--------------------------------------------------------------------------------------------

class EJones_21cm (Joneset22.Joneset22):
    """Class that represents a set of 2x2 WSRT 21cm EJones matrices,
    which model the WSRT telescope beamshapes with the 21cm MFFE receivers.
    EJones is an image-plane effect."""

    def __init__(self, ns, quals=[], label='E',
                 stations=None, simulate=False):
        
        Joneset22.Joneset22.__init__(self, ns, quals=quals, label=label,
                                     stations=stations, polrep='linear',
                                     simulate=simulate)
        pols = self._pols
        quals = self.quals()
        pname = self.label()+'phase'
        gname = self.label()+'gain'
        jname = self.label()+'Jones'
        # Define the various primary ParmGroups:
        for pol in pols:
            matrel = self._pols_matrel()[pol]     # i.e. 'm11' or 'm22'
            self._pgm.define_parmgroup(pname+pol, descr=pol+'-dipole phases',
                                  Tsec=200,
                                  matrel=matrel, tags=[pname,jname])
            self._pgm.define_parmgroup(gname+pol, descr=pol+'-dipole gains',
                                  default=1.0,
                                  matrel=matrel, tags=[gname,jname])
        # Make the Jones matrices per station:
        for s in self.stations():
            mm = dict()
            for pol in pols:
                phase = self._pgm.create_parmgroup_entry(pname+pol, s)
                gain = self._pgm.create_parmgroup_entry(gname+pol, s)
                mm[pol] = self._ns[jname+pol](*quals)(s) << Meq.Polar(gain,phase)
            self._ns[jname](*quals)(s) << Meq.Matrix22(mm[pols[0]],0.0,
                                                       0.0,mm[pols[1]])
        self.matrixet(new=self._ns[jname](*quals))
        # Make some secondary (composite) ParmGroups:
        self._pgm.define_gogs(jname)
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
        reqseq = jones.make_solver(j2)
        cc.append(reqseq)


    jones = JJones(ns, quals=[], simulate=simulate)
    cc.append(jones.visualize())
    # jones.display(full=True)

    jones = DJones(ns, quals=[], simulate=simulate)
    cc.append(jones.visualize())
    # jones.display(full=True)

    jones = FJones(ns, quals=['L'], simulate=simulate)
    cc.append(jones.visualize())
    jones.display(full=True)
    # jones.display_parmgroups(full=False)

    jones = Joneset22.FJones(ns, quals=['C'], simulate=simulate, polrep='circular')
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

    if 0:
        J = JJones(ns, quals=['xxx'], diagonal=False)
        jj.append(J)
        J.display(full=True)


    if 0:
        D = DJones(ns, coupled_dang=True, coupled_dell=True, simulate=True)
        # D = DJones(ns, coupled_dang=False, coupled_dell=False)
        jj.append(D)
        D.display(full=True)
        D._pgm.display_NodeGroups()


    if 0:
        # F = FJones(ns, polrep='linear')
        F = FJones(ns, polrep='circular')
        jj.append(F)
        F.display(full=True)

    if 0:
        jseq = Joneset22.Joneseq22 (jj)
        jseq.display(full=True)

#===============================================================
    
