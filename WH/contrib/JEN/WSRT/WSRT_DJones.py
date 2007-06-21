# file: ../WSRT/WSRT_DJones.py

# History:
# - 15jun2007: creation (from Grunting/WSRT_Joneset.py)

# Description:

# WSRT DJones matrix module, derived from Grunt.Joneset22, with TDLOptions

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


def TDL_parmgroups(full=False):
    """Return the available groups of MeqParms"""
    pg = [None,'DJones','Ddang','Ddell','Dpzd']
    return TDLCompileOption('TDL_DJones_solvable', 'groups of solvable DJones parms',pg,
                            doc='select group(s) of solvable DJones parms ...')


#--------------------------------------------------------------------------------------------

TDLCompileOption('TDL_coupled_dang',"coupled_dang",[True,False],
                 doc='if coupled, ...')
TDLCompileOption('TDL_coupled_dell',"coupled_dell",[True,False],
                 doc='if coupled, ...')

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

    def __init__(self, ns, name='DJones', quals=[], 
                 coupled_dang=None,
                 coupled_dell=None,
                 override=None,
                 stations=None, simulate=False):
        
        Joneset22.Joneset22.__init__(self, ns, name=name, quals=quals, 
                                     telescope='WSRT',
                                     polrep='linear',
                                     stations=stations,
                                     simulate=simulate)

        if coupled_dang==None: coupled_dang = TDL_coupled_dang 
        if coupled_dell==None: coupled_dell = TDL_coupled_dell 
        
        self.history(override)
        self.history('coupled_dang='+str(coupled_dang)+' coupled_dell='+str(coupled_dell))
        
        pols = self._pols
        dname = 'Ddang'
        ename = 'Ddell'
        pname = 'PZD'
        jname = 'DJones'

        # Define the various primary ParmGroups:
        pg = dict()
        rider = dict(use_matrix_element=['XY','YX'])
        dev = self.p_deviation_expr (ampl='{0.001~10%}', Psec='{1500~10%}', PHz=None)

        # Dipole angle errors (dang):
        if coupled_dang:
            pg[dname] = self.p_group_define (dname, 
                                             descr='dipole angle error',
                                             default=0.0, unit='rad',
                                             # tiling=None, time_deg=0, freq_deg=0,
                                             simul=simulate, deviation=dev,
                                             override=override,
                                             rider=rider,
                                             tags=[dname,jname])
        else:
            pg[dname] = dict()
            for pol in pols:
                pg[dname][pol] = self.p_group_define (dname+pol, 
                                                      descr=pol+'-dipole angle error',
                                                      default=0.0, unit='rad',
                                                      # tiling=None, time_deg=0, freq_deg=0,
                                                      simul=simulate, deviation=dev,
                                                      override=override,
                                                      rider=rider,
                                                      tags=[dname,jname])
        # Dipole ellipticities (dell):
        if coupled_dell:
            pg[ename] = self.p_group_define (ename, 
                                             descr='dipole ellipticity',
                                             default=0.0, unit='rad',
                                             # tiling=None, time_deg=0, freq_deg=0,
                                             constraint=dict(sum=0.0, first=0.0),
                                             simul=simulate, deviation=dev,
                                             override=override,
                                             rider=rider,
                                             tags=[ename,jname])
        else:
            pg[ename] = dict()
            for pol in pols:
                pg[ename][pol] = self.p_group_define (ename+pol,
                                                      descr=pol+'-dipole ellipticity',
                                                      default=0.0, unit='rad',
                                                      # tiling=None, time_deg=0, freq_deg=0,
                                                      constraint=dict(sum=0.0, first=0.0),
                                                      simul=simulate, deviation=dev,
                                                      override=override,
                                                      rider=rider,
                                                      tags=[ename,jname])

        # Phase-zero difference (PZD) between X and Y systems:
        dev = self.p_deviation_expr (ampl='{0.1~10%}', Psec='{500~10%}', PHz=None)
        pg[pname] = self.p_group_define (pname,
                                         descr='XY phase-zero difference',
                                         override=override,
                                         simul=simulate, deviation=dev,
                                         rider=rider,
                                         tags=[pname,jname])

        # Make and check the qualifiable base-node (qnode):
        qnode = self.ns[jname]
        if not qnode.must_define_here(self):
            raise ValueError,'** nodename clash'

        # Make the (overall) 2x2 PZD jones matrix:
        pmat = self.ns.pmat 
        pmat = qnode('pmat')
        pzd = self.p_group_create_member (pg[pname])
        # pzd = pg[pname].create_member()
        pzd2 = pmat('pzd2') << pzd/2
        m11 = pmat('11') << Meq.Polar(1.0, pzd2)
        m22 = pmat('22') << Meq.Polar(1.0, pmat('npzd2') << Meq.Negate(pzd2))
        pmat << Meq.Matrix22(m11,0.0,0.0,m22)


        # Make the Jones matrices per station:
        for s in self.stations():

            # Dipole rotation angles:
            dmat = self.ns.dmat(s)
            dmat = qnode('dmat')(s)
            if coupled_dang:
                dang = self.p_group_create_member (pg[dname], quals=s)
                # dang = pg[dname].create_member(s)
                cos = dmat('cos') << Meq.Cos(dang)
                sin = dmat('sin') << Meq.Sin(dang)
                sinneg = dmat('nsin') << Meq.Negate(sin)
                dmat << Meq.Matrix22(cos,sin,sinneg,cos)
            else:
                dang1 = self.p_group_create_member (pg[dname][pols[0]], quals=s)
                dang2 = self.p_group_create_member (pg[dname][pols[1]], quals=s)
                # dang1 = pg[dname][pols[0]].create_member(s)
                # dang2 = pg[dname][pols[1]].create_member(s)
                cos1 = dmat('cos1') << Meq.Cos(dang1)
                cos2 = dmat('cos2') << Meq.Cos(dang2)
                sin1 = dmat('nsin1') << Meq.Negate(dmat('sin1') << Meq.Sin(dang1))
                sin2 = dmat('sin2') << Meq.Sin(dang2)
                dmat << Meq.Matrix22(cos1,sin1,sin2,cos2)


            # Dipole ellipticities:
            emat = self.ns.emat(s)
            emat = qnode('emat')(s)
            if coupled_dell:
                dell = self.p_group_create_member (pg[ename], quals=s)
                # dell = pg[ename].create_member(s)
                cos = emat('cos') << Meq.Cos(dell)
                sin = emat('sin') << Meq.Sin(dell)
                isin = emat('isin') << Meq.ToComplex(0.0, sin)
                emat << Meq.Matrix22(cos,isin,isin,cos)
            else:
                dell1 = self.p_group_create_member (pg[ename][pols[0]], quals=s)
                dell2 = self.p_group_create_member (pg[ename][pols[1]], quals=s)
                # dell1 = pg[ename][pols[0]].create_member(s)
                # dell2 = pg[ename][pols[1]].create_member(s)
                cos1 = emat('cos1') << Meq.Cos(dell1)
                cos2 = emat('cos2') << Meq.Cos(dell2)
                isin1 = emat('isin1') << Meq.ToComplex(0.0, emat('sin1') << Meq.Sin(dell1))
                isin2 = emat('isin2') << Meq.ToComplex(0.0, emat('sin2') << Meq.Sin(dell2))
                isin2 = emat('cisin2') << Meq.Conj(isin2)
                emat << Meq.Matrix22(cos1,isin1,isin2,cos2)

            # Make the station Jones matrix by multiplying the sub-matrices:
            qnode(s) << Meq.MatrixMultiply (dmat, emat, pmat)

        self.matrixet(new=qnode)
        return None




     
#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []
    simulate = True

    jones = DJones(ns, quals=[], simulate=simulate,
                   coupled_dang=TDL_coupled_dang,
                   coupled_dell=TDL_coupled_dell)
    cc.append(jones.visualize())
    jones.display(full=True)
        
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
# Test routine (standalone):
#===============================================================

if __name__ == '__main__':
    ns = NodeScope()


    if 1:
        J = DJones(ns, quals=['xxx'],
                   coupled_dang=TDL_coupled_dang,
                   coupled_dell=TDL_coupled_dell)
        J.display(full=True)


#===============================================================
    
