# file: ../Grunting/WSRT_Joneset.py

# History:
# - 14jan2007: creation (from Grunt/Joneset22.py)
# - 29jan2007: split into uv-plane and image-plane effects

# Description:

# Definition of a set of WSRT-specific Jones matrices, implemented as Joneset22 objects.
# In addition there are a number of functions that streamline the use of Jones matrices
# from scripts that define WSRT data-reduction trees (e.g. Grunting/WSRT_cps_simul.py).
# Ideally, there should be a (large) choice of modules like this one, defining Jones
# matrices for other telescopes (VLA, LOFAR), and even alternative ones for the WSRT.

# The various XJones() functions in this module produce Joneset22 objects. They contain
# a set of 2x2 Jones matrices (subtrees), a separate one for each of the specifies stations. 

# Copyright: The MeqTree Foundation


#======================================================================================
# Preamble:
#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

from Timba.Contrib.JEN.Grunt import Joneset22


#=================================================================================================
# Functions to streamline the use of WSRT Jones matrices: 
#=================================================================================================

def help ():
    ss = 'help on WSRT Jones matrices'
    return ss


def parmgroups_uvp(full=False):
    """Return the available groups of MeqParms from the (uv-plane) Jones matrices
    in this Jones module"""
    pg = ['*']
    pg.extend(GJones_parmgroups(full=full)) 
    pg.extend(DJones_parmgroups(full=full)) 
    pg.extend(FJones_parmgroups(full=full)) 
    pg.extend(JJones_parmgroups(full=full)) 
    pg.extend(BJones_parmgroups(full=full))
    pg.append(['GJones','BJones'])
    pg.append(['GJones','DJones'])
    pg.append(['GJones','DJones','FJones'])
    pg.append(['DJones','FJones'])
    return pg



def include_TDL_options_uvp(prompt='instr.model'):
    """Definition of variables that control the generation of Jones matrices
    for uv-plane effects. The user may set these in the browser TDL options menu.
    These values are picked up by the function .Joneseq22_uvp() in this module."""
    joneseq = ['G','GD','GB','D','GDF','J','B']
    Btfdeg = [[0,5],[0,2],[0,3],[0,4],[0,6],[1,5],[2,5]]
    menuname = 'WSRT_Jones_uvp ('+str(prompt)+')'
    TDLCompileMenu(menuname,
                   TDLOption('TDL_joneseq', 'Sequence of Jones matrices', joneseq, more=str),
                   TDLOption('TDL_D_coupled_dang',"DJones: coupled (dangX=dangY)", [True, False]),
                   TDLOption('TDL_D_coupled_dell',"DJones: coupled (dellX=-dellY)", [True, False]),
                   TDLOption('TDL_J_diagonal',"JJones: diagonal matrix", [False, True]),
                   TDLOption('TDL_B_tfdeg',"BJones: time-freq polynomial degree", Btfdeg),
                   )
    return True


#------------------------------------------------------------------------------------------

def Joneseq22_uvp(ns, stations, simulate=False, override=None, **pp):
    """Return a Jonest22 object that contains a set of Jones matrices for
    the given stations. This function deals with uv-plane effects only.
    The Jones matrices are the matrix product of a
    sequence of WSRT Jones matrices that are defined in this module.
    - The 'TDL_' arguments in this function are user-defined in the meqbrowser,
    via the TDLOptions defined in the function .include_TDL_options() in this module.
    - The sequence is defined by the letters (e.g. 'GD') of the string TDL_joneseq.
    - If simulate==True, the Jones matrices do not contain MeqParms,
    but subtrees that simulate MeqParm values that change with time etc."""

    if not isinstance(pp, dict): pp = dict()
    pp.setdefault('joneseq',TDL_joneseq)
    pp.setdefault('D_coupled_dell',TDL_D_coupled_dell)
    pp.setdefault('D_coupled_dang',TDL_D_coupled_dang)
    pp.setdefault('J_diagonal',TDL_J_diagonal)
    pp.setdefault('B_tfdeg',TDL_B_tfdeg)

    # First make a sequence (list) of Joneset22 objects:
    jseq = []
    for c in pp['joneseq']:
        if c=='G':
            jseq.append(GJones(ns, stations=stations,
                               override=override,
                               simulate=simulate))
        elif c=='D':
            jseq.append(DJones(ns, stations=stations,
                               coupled_dell=pp['D_coupled_dell'],
                               coupled_dang=pp['D_coupled_dang'],
                               override=override,
                               simulate=simulate))
        elif c=='F':
            jseq.append(FJones(ns, stations=stations,
                               override=override,
                               simulate=simulate))
        elif c=='J':
            jseq.append(JJones(ns, stations=stations,
                               diagonal=pp['J_diagonal'],
                               override=override,
                               simulate=simulate))
        elif c=='B':
            jseq.append(BJones(ns, stations=stations,
                               tfdeg=pp['B_tfdeg'],
                               override=override,
                               simulate=simulate))
        else:
            raise ValueError,'WSRT jones matrix not recognised: '+str(c)

    # Then matrix-multiply them into a single Joneset22 object:
    # NB: Its ParmGroupManager will contain all information (parmgroups)
    #     from those of the contributing Joneset22 objects.
    jones = Joneset22.Joneseq22(jseq)
    return jones




#=================================================================================================
# Definition of WSRT Jones matrices:
#=================================================================================================

def GJones_parmgroups(full=False):
    """Return the available groups of MeqParms"""
    pg = ['GJones','Gphase','Ggain'] 
    if full: pg.extend(['GphaseX','GgainX','GphaseY','GgainY']) 
    return pg


class GJones (Joneset22.GJones):
    """Class that represents a set of 2x2 WSRT GJones matrices,
    which model the (complex) gains due to electronics
    and (optionally) the tropospheric phase (a.k.a. TJones).
    GJones is a uv-plane effect, i.e. it is valid for the entire FOV."""

    def __init__(self, ns, quals=[], label='G',
                 override=None,
                 stations=None, simulate=False):
        
        # Just use the generic GJones in Grunt/Joneset22.py
        Joneset22.GJones.__init__(self, ns, quals=quals, label=label,
                                  telescope='WSRT', polrep='linear',
                                  override=override,
                                  stations=stations, simulate=simulate)
        return None


#--------------------------------------------------------------------------------------------

def JJones_parmgroups(full=False):
    """Return the available groups of MeqParms"""
    pg = ['JJones','Jdiag','Joffdiag']
    return pg


class JJones (Joneset22.JJones):
    """Class that represents a set of 2x2 WSRT JJones matrices.
    Each of the 4 complex elements of a station Jones matrix
    is assumed to be independent. The parameters are their real
    and imaginary parts (i.e. 8 real parameters per station)."""

    def __init__(self, ns, quals=[], label='J',
                 diagonal=False,
                 override=None,
                 stations=None, simulate=False):

        # Just use the generic JJones in Grunt/Joneset22.py
        Joneset22.JJones.__init__(self, ns, quals=quals, label=label,
                                  polrep='linear', telescope='WSRT',
                                  diagonal=diagonal,
                                  override=override,
                                  stations=stations, simulate=simulate)
        return None


#--------------------------------------------------------------------------------------------

def FJones_parmgroups(full=False):
    """Return the available groups of MeqParms"""
    pg = ['FJones','Frm']
    return pg



class FJones (Joneset22.FJones):
    """Class that represents a set of 2x2 WSRT FJones matrices.
    For the moment, the ionospheric Faraday rotation is assumed
    to be the same for all stations, and the entire FOV."""

    def __init__(self, ns, quals=[], label='F',
                 override=None,
                 stations=None, simulate=False):
        
        # Just use the generic FJones in Grunt/Joneset22.py
        Joneset22.FJones.__init__(self, ns, quals=quals, label=label,
                                  telescope='WSRT', polrep='linear',
                                  override=override,
                                  stations=stations, simulate=simulate)
        return None




#--------------------------------------------------------------------------------------------

def BJones_parmgroups(full=False):
    """Return the available groups of MeqParms"""
    pg = ['BJones'] 
    return pg


class BJones (Joneset22.BJones):
    """Class that represents a set of 2x2 WSRT BJones matrices.
    In principle, BJones models on the electronic IF bandpass,
    but in practice it usually absorbs other frequency effects as well"""

    def __init__(self, ns, quals=[], label='B',
                 tfdeg=[0,5],
                 override=None,
                 stations=None, simulate=False):
        
        # Just use the generic BJones in Grunt/Joneset22.py
        Joneset22.BJones.__init__(self, ns, quals=quals, label=label,
                                  telescope='WSRT', polrep='linear',
                                  tfdeg=tfdeg,
                                  override=override,
                                  stations=stations, simulate=simulate)
        return None


#--------------------------------------------------------------------------------------------


def DJones_parmgroups(full=False):
    """Return the available groups of MeqParms"""
    pg = ['DJones','Ddang','Ddell','Dpzd']
    return pg


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
                 coupled_dang=True, coupled_dell=True,
                 override=None,
                 stations=None, simulate=False):
        
        Joneset22.Joneset22.__init__(self, ns, quals=quals, label=label,
                                     telescope='WSRT', polrep='linear',
                                     stations=stations, simulate=simulate)
        pols = self._pols
        quals = self.quals()
        dname = self.label()+'dang'
        ename = self.label()+'dell'
        pname = self.label()+'pzd'
        jname = self.label()+'Jones'
        matrel = ['m12','m21']

        # Define the various primary ParmGroups:
        if coupled_dang:
            self.define_parmgroup(dname, descr='dipole angle error',
                                  quals=quals,
                                  default=dict(c00=0.0),
                                  simul=dict(),
                                  override=override,
                                  rider=dict(matrel=matrel),
                                  tags=[dname,jname])
        else:
            for pol in pols:
                self.define_parmgroup(dname+pol, descr=pol+'-dipole angle error',
                                      quals=quals,
                                      default=dict(c00=0.0),
                                      simul=dict(),
                                      override=override,
                                      rider=dict(matrel=matrel),
                                      tags=[dname,jname])
        if coupled_dell:
            self.define_parmgroup(ename, descr='dipole ellipticity',
                                  quals=quals,
                                  default=dict(c00=0.0),
                                  simul=dict(),
                                  override=override,
                                  rider=dict(matrel=matrel),
                                  tags=[ename,jname])
        else:
            for pol in pols:
                self.define_parmgroup(ename+pol, descr=pol+'-dipole ellipticity',
                                      quals=quals,
                                      default=dict(c00=0.0),
                                      simul=dict(),
                                      override=override,
                                      rider=dict(matrel=matrel),
                                      tags=[ename,jname])
        self.define_parmgroup(pname, descr='XY/RL phase-zero difference',
                              quals=quals,
                              override=override,
                              rider=dict(matrel=matrel),
                              tags=[pname,jname])

        # Make the (overall) 2x2 PZD jones matrix:
        pzd = self.create_parmgroup_entry(pname, quals=quals)
        pzd2 = self._ns << pzd/2
        m11 = self._ns << Meq.Polar(1.0, pzd2)
        m22 = self._ns << Meq.Polar(1.0, self._ns << Meq.Negate(pzd2))
        pmat = self._ns[pname](*quals) << Meq.Matrix22(m11,0.0,0.0,m22)


        # Make the Jones matrices per station:
        for s in self.stations():

            # Dipole rotation angles:
            if coupled_dang:
                dang = self.create_parmgroup_entry(dname, s, quals=quals)
                cos = self._ns << Meq.Cos(dang)
                sin = self._ns << Meq.Sin(dang)
                sinneg = self._ns << Meq.Negate(sin)
                dmat = self._ns[dname](*quals)(s) << Meq.Matrix22(cos,sin,sinneg,cos)
            else:
                dang1 = self.create_parmgroup_entry(dname+pols[0], s, quals=quals)
                dang2 = self.create_parmgroup_entry(dname+pols[1], s, quals=quals)
                cos1 = self._ns << Meq.Cos(dang1)
                cos2 = self._ns << Meq.Cos(dang2)
                sin1 = self._ns << Meq.Negate(self._ns << Meq.Sin(dang1))
                sin2 = self._ns << Meq.Sin(dang2)
                dmat = self._ns[dname](*quals)(s) << Meq.Matrix22(cos1,sin1,sin2,cos2)


            # Dipole ellipticities:
            if coupled_dell:
                dell = self.create_parmgroup_entry(ename, s, quals=quals)
                cos = self._ns << Meq.Cos(dell)
                sin = self._ns << Meq.Sin(dell)
                isin = self._ns << Meq.ToComplex(0.0, sin)
                emat = self._ns[ename](*quals)(s) << Meq.Matrix22(cos,isin,isin,cos)
            else:
                dell1 = self.create_parmgroup_entry(ename+pols[0], s, quals=quals)
                dell2 = self.create_parmgroup_entry(ename+pols[1], s, quals=quals)
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
        self.define_gogs(jname)
        return None




#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------

def EJones_parmgroups(full=False):
    """Return the available groups of MeqParms"""
    pg = ['EJones'] 
    return pg


class EJones (Joneset22.Joneset22):
    """Class that represents a set of 2x2 WSRT EJones matrices,
    which model the WSRT telescope beamshapes with the 21cm MFFE receivers.
    EJones is an image-plane effect."""

    def __init__(self, ns, quals=[], label='E',
                 override=None,
                 stations=None, simulate=False):
        
        Joneset22.Joneset22.__init__(self, ns, quals=quals, label=label,
                                     polrep='linear', telescope='WSRT', band='21cm',
                                     stations=stations, simulate=simulate)
        pols = self._pols
        quals = self.quals()
        pname = self.label()+'phase'
        gname = self.label()+'gain'
        jname = self.label()+'Jones'

        # Define the various primary ParmGroups:
        for pol in pols:
            matrel = self._pols_matrel()[pol]     # i.e. 'm11' or 'm22'
            self.define_parmgroup(pname+pol, descr=pol+'-dipole phases',
                                  quals=quals,
                                  default=dict(c00=0.0),
                                  simul=dict(Tsec=200),
                                  override=override,
                                  rider=dict(matrel=matrel),
                                  tags=[pname,jname])
            self.define_parmgroup(gname+pol, descr=pol+'-dipole gains',
                                  quals=quals,
                                  default=dict(c00=1.0),
                                  simul=dict(),
                                  override=override,
                                  rider=dict(matrel=matrel),
                                  tags=[gname,jname])

        # Make the Jones matrices per station:
        for s in self.stations():
            mm = dict()
            for pol in pols:
                phase = self.create_parmgroup_entry(pname+pol, s, quals=quals)
                gain = self.create_parmgroup_entry(gname+pol, s, quals=quals)
                mm[pol] = self._ns[jname+pol](*quals)(s) << Meq.Polar(gain,phase)
                if False:
                    Xbeam = Expression('[l]**2+[m]**2', label='Xbeam')
                    # Xbeam.display(full=True)
                    # Xbeam.expanded().display(full=True)
                    node = Xbeam.MeqParm (ns, trace=True)
                    Xbeam.display('MeqParm', full=True)
                    TDL_display.subtree(node, 'MeqParm', full=True, recurse=5)
            self._ns[jname](*quals)(s) << Meq.Matrix22(mm[pols[0]],0.0,
                                                       0.0,mm[pols[1]])
        self.matrixet(new=self._ns[jname](*quals))

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
        reqseq = jones.make_solver(j2)
        cc.append(reqseq)

    jones = JJones(ns, quals=[], simulate=simulate)
    cc.append(jones.visualize())
    # jones.display(full=True)

    jones = FJones(ns, quals=['L'], simulate=simulate)
    cc.append(jones.visualize())
    jones.display(full=True)
    # jones.display_parmgroups(full=False)

    jones = DJones(ns, quals=[], simulate=simulate)
    cc.append(jones.visualize())
    # jones.display(full=True)

    if False:
        jones = EJones(ns, quals=[], simulate=simulate)
        cc.append(jones.visualize())
        # jones.display(full=True)


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

    if 0:
        G = GJones(ns, quals=['3c84','xxx'], simulate=False)
        jj.append(G)
        G.visualize()
        G.display(full=True)
        # G.display_NodeGroups()

    if 1:
        J = EJones(ns, simulate=False)
        jj.append(J)
        J.display(full=True)

    if 0:
        J = JJones(ns, quals=['xxx'], diagonal=False)
        jj.append(J)
        J.display(full=True)


    if 0:
        J = BJones(ns, quals=['xxx'])
        jj.append(J)
        J.display(full=True)


    if 0:
        D = DJones(ns, coupled_dang=True, coupled_dell=True, simulate=True)
        # D = DJones(ns, coupled_dang=False, coupled_dell=False)
        jj.append(D)
        D.display(full=True)
        # D._pgm.display_NodeGroups()


    if 0:
        # F = FJones(ns, polrep='linear')
        F = FJones(ns, polrep='circular')
        jj.append(F)
        F.display(full=True)

    if 0:
        jseq = Joneset22.Joneseq22 (jj)
        jseq.display(full=True)

#===============================================================
    
