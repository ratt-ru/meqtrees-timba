# file: ../Grunt/Joneset22.py

# History:
# - 25dec2006: creation
# - 14jan2007: keep only generic G/J/FJones
# - 29jan2007: added BJones
# - 30mar2007: adapted to QualScope etc
# - 07jun2007: adapted to NodeList/ParameterizationPlus

# Description:

# The Joneset22 class is a base-class for classes that define and
# encapsulate a set of 2x2 station Jones matrices.

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

import Meow

from Timba.Contrib.JEN.Grunt import Matrixet22

from copy import deepcopy

#======================================================================================

class Joneset22 (Matrixet22.Matrixet22):
    """Base class that represents a set of 2x2 Jones matrices.
    Derived from the class Matrixet22."""

    def __init__(self, ns, name='<j>', quals=[], kwquals={},
                 descr='<descr>',
                 stations=None, polrep=None,
                 telescope=None, band=None,
                 simulate=False):

        # List of (array) station indices:
        indices = deepcopy(stations)
        if indices==None:
            indices = range(1,4)                               # for testing convenience....

        # If simulate, use subtrees that simulate MeqParm behaviour:
        self._simulate = simulate

        # Some telescope-specific information:
        self._telescope = telescope                            # e.g. WSRT or VLA
        self._band = band                                      # e.g. 21cm or LFFE

        # Add some qualifiers, if necessary:
        quals = self.p_quals2list(quals)
        if self._simulate: quals.append('simul')
        if self._telescope: quals.append(self._telescope)
        if self._band: quals.append(self._band)

        # Initialise its Matrixet22 object:
        Matrixet22.Matrixet22.__init__(self, ns, name,
                                       quals=quals, kwquals=kwquals,
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
        matrel[pols[0]] = self._matrix_elements['name'][0]
        matrel[pols[1]] = self._matrix_elements['name'][3]
        return matrel

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
        ss += '  ('+str(self.ns['<nodename>'].name)+')'
        return ss


    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        print '   - stations ('+str(len(self.stations()))+'): '+str(self.stations())
        return True



#=================================================================================================
# Make a Joneset22 object that is a sequence (matrix multiplication) of Jones matrices
#=================================================================================================

def Joneseq22 (joneslist=None, quals=None):
    """Return a Jones22 object that contains an (item-by-item) matrix multiplication
    of the matrices of the list (joneslist) of two or more Joneset22 objects."""

    if len(joneslist)==0:
        raise ValueError, 'joneslist should have at least one item'
    
    elif len(joneslist)==1:
        jnew = joneslist[0]
        return jnew
    
    # First create a new Jonset22 object with name/quals/descr that are
    # suitable combinations of those of the contributing Joneset22 objects: 
    name = joneslist[0].name
    descr = joneslist[0].name+': '+joneslist[0].descr()
    stations = joneslist[0].stations()
    qq = joneslist[0].p_get_quals(remove=[joneslist[0].name])
    for jones in joneslist[1:]:
        name += jones.name
        descr += '\n '+jones.name+': '+jones.descr()
        qq = jones.p_get_quals(merge=qq, remove=[jones.name])
    qq.extend(joneslist[0].p_quals2list(quals))
    jnew = Joneset22 (ns, name=name, quals=qq, stations=stations) 

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
        jnew.p_merge(jones)
        jnew.history(subappend=jones.history())

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


    def __init__(self, ns, name='G', quals=[], 
                 polrep=None,
                 telescope=None, band=None,
                 override=None,
                 stations=None, simulate=False):
        
        Joneset22.__init__(self, ns, quals=quals, name=name,
                           polrep=polrep,
                           telescope=telescope, band=band,
                           stations=stations, simulate=simulate)

        self.history(override)
        pols = self.pols()                        # e.g. ['X','Y']
        pname = 'Gphase'
        gname = 'Ggain'
        jname = 'GJones'

        # Define the various primary ParmGroups:
        pg = dict()
        for pol in pols:
            pg[pol] = dict()
            rider = dict(use_matrix_element=self._pols_matrel()[pol])

            dev = self.p_deviation_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz=None)
            pg[pol][pname] = self.p_group_define(pname+pol,
                                                 descr=pol+'-dipole phases',
                                                 default=0.0, unit='rad',
                                                 tiling=1, time_deg=0, freq_deg=0,
                                                 constraint=dict(sum=0.0, first=0.0),
                                                 simul=simulate, deviation=dev,
                                                 override=override,
                                                 rider=rider,
                                                 tags=[pname,jname])

            dev = self.p_deviation_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz='{1000e6~10%}')
            pg[pol][gname]= self.p_group_define(gname+pol,
                                                descr=pol+'-dipole gains',
                                                default=1.0,
                                                tiling=None, time_deg=2, freq_deg=0,
                                                # constrain_min=0.1, constrain_max=10.0,
                                                constraint=dict(product=1.0),
                                                simul=simulate, deviation=dev,
                                                override=override,
                                                rider=rider,
                                                tags=[gname,jname])

        # Make the Jones matrices per station:
        qnode = self.ns[jname]
        if not qnode.must_define_here(self):
            raise ValueError,'** nodename clash'
        for s in self.stations():
            mm = dict()
            for pol in pols:
                phase = self.p_group_create_member (pg[pol][pname], quals=s)
                gain = self.p_group_create_member (pg[pol][gname], quals=s)
                # mm[pol] = self.ns[jname+pol](s) << Meq.Polar(gain,phase)
                mm[pol] = qnode(pol)(s) << Meq.Polar(gain,phase)
            qnode(s) << Meq.Matrix22(mm[pols[0]],0.0, 0.0,mm[pols[1]])
        self.matrixet(new=qnode)
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

    def __init__(self, ns, name='B', quals=[], 
                 polrep=None, telescope=None, band=None,
                 tfdeg=[0,5],
                 override=None,
                 stations=None, simulate=False):
        
        Joneset22.__init__(self, ns, quals=quals, name=name,
                           polrep=polrep, telescope=telescope, band=band,
                           stations=stations, simulate=simulate)

        self.history(override)
        pols = self.pols()                                # e.g. ['X','Y']
        iname = 'Bimag'
        rname = 'Breal'
        jname = 'BJones'

        # Define the various primary ParmGroups:
        pg = dict()
        for pol in pols:
            pg[pol] = dict()
            rider = dict(use_matrix_element=self._pols_matrel()[pol])
            dev = self.p_deviation_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz='{10e6~10%}')

            pg[pol][iname] = self.p_group_define(iname+pol,
                                                 descr=pol+'-IF bandpass imag.part',
                                                 default=0.0, unit='Jy',
                                                 tiling=1, time_deg=tfdeg[0], freq_deg=tfdeg[1],
                                                 simul=simulate, deviation=dev,
                                                 override=override,
                                                 rider=rider,
                                                 tags=[iname,jname])

            pg[pol][rname] = self.p_group_define(rname+pol,
                                                 descr=pol+'-IF bandpass real.part',
                                                 default=1.0, unit='Jy',
                                                 tiling=None, time_deg=tfdeg[0], freq_deg=tfdeg[1],
                                                 simul=simulate, deviation=dev,
                                                 override=override,
                                                 rider=rider,
                                                 tags=[rname,jname])

        # Make the Jones matrices per station:
        qnode = self.ns[jname]                   
        if not qnode.must_define_here(self):
            raise ValueError,'** nodename clash'
        for s in self.stations():
            mm = dict()
            for pol in pols:
                real = self.p_group_create_member (pg[pol][rname], quals=s)
                imag = self.p_group_create_member (pg[pol][iname], quals=s)
                mm[pol] = qnode(pol)(s) << Meq.ToComplex(real,imag)
            qnode(s) << Meq.Matrix22(mm[pols[0]],0.0, 0.0,mm[pols[1]])
        self.matrixet(new=qnode)
        return None







#--------------------------------------------------------------------------------------------

class JJones (Joneset22):
    """Class that represents a set of 2x2 JJones matrices.
    Each of the 4 complex elements of a station Jones matrix
    is assumed to be independent. The parameters are their real
    and imaginary parts (i.e. 8 real parameters per station).
    JJones is the same for linear and circular polarizations."""

    def __init__(self, ns, name='J', quals=[],
                 diagonal=False,
                 polrep=None, telescope=None, band=None,
                 override=None,
                 stations=None, simulate=False):

        Joneset22.__init__(self, ns, quals=quals, name=name,
                           polrep=polrep, telescope=telescope, band=band,
                           stations=stations, simulate=simulate)
        
        self.history(override)
        jname = 'JJones'
        enames = ['J11','J12','J21','J22']

        # Define the various primary ParmGroups:
        pg = dict()
        dev = self.p_deviation_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz='{10e6~10%}')
        for ename in ['J11','J22']:
            pg[ename] = dict()
            for rim in ['real','imag']:
                default = 0.0
                constraint = dict(sum=0.0)
                if rim=='real':
                    default = 1.0
                    constraint = dict(product=1.0)
                pg[ename][rim] = self.p_group_define(ename+rim,
                                                     descr=rim+' part of matrix element '+ename,
                                                     default=default, unit='Jy',
                                                     tiling=None, time_deg=0, freq_deg=0,
                                                     simul=simulate, deviation=dev,
                                                     constraint=constraint,
                                                     override=override,
                                                     tags=[jname,'Jdiag'])
        if not diagonal:
            for ename in ['J12','J21']:
                pg[ename] = dict()
                for rim in ['real','imag']:
                    pg[ename][rim] = self.p_group_define(ename+rim, 
                                                         descr=rim+' part of matrix element '+ename,
                                                         default=0.0, unit='Jy',
                                                         tiling=None, time_deg=0, freq_deg=0,
                                                         simul=simulate, deviation=dev,
                                                         constraint=dict(sum=0.0),
                                                         override=override,
                                                         tags=[jname,'Joffdiag'])
            
                    
        # Make the Jones matrices per station:
        qnode = self.ns[jname]                   
        if not qnode.must_define_here(self):
            raise ValueError,'** nodename clash'
        for s in self.stations():
            mm = dict(J12=0.0, J21=0.0)
            for ename in pg.keys():
                real = self.p_group_create_member (pg[ename]['real'], quals=s)
                imag = self.p_group_create_member (pg[ename]['imag'], quals=s)
                mm[ename] = self.ns[ename](s) << Meq.ToComplex(real,imag)
            qnode(s) << Meq.Matrix22(mm[enames[0]],mm[enames[1]],
                                     mm[enames[2]],mm[enames[3]])
        self.matrixet(new=qnode)
        return None



#--------------------------------------------------------------------------------------------

class FJones (Joneset22):
    """Class that represents a set of 2x2 FJones matrices,
    which model the ionospheric Faraday rotation, 
    for either polarization representations (linear or circular).
    This FJones is assumed to be large-scale compared to the array size,
    i.e. it is the same for all stations, and the entire FOV."""

    def __init__(self, ns, name='F', quals=[], 
                 polrep='linear', telescope=None, band=None,
                 override=None,
                 stations=None, simulate=False):
        
        Joneset22.__init__(self, ns, quals=quals, name=name,
                           polrep=polrep, telescope=telescope, band=band,
                           stations=stations, simulate=simulate)
        
        self.history(override)
        polrep = self.polrep()
        rname = 'RM'       
        jname = 'FJones'

        # Define the primary ParmGroup:
        pg = dict()
        dev = self.p_deviation_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz=None)
        pg[rname] = self.p_group_define(rname,  
                                        descr='Faraday Rotation Measure (rad/m2)',
                                        default=0.0, unit='rad/m2',
                                        simul=simulate, deviation=dev,
                                        override=override,
                                        tags=[rname,jname])

        qnode = self.ns[jname](polrep)                   
        if not qnode.must_define_here(self):
            raise ValueError,'** nodename clash'
            
        RM = self.p_group_create_member (pg[rname])
        # wvl = qnode('lambda') << Meq.Divide(3e8, qnode('freq') << Meq.Freq())
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

        # The station Jones matrices are all the same:  
        for s in self.stations():
            qnode(s) << Meq.Identity(qnode)
        self.matrixet(new=qnode)
        return None




     
#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []
    simulate = True

    jones = GJones(ns, quals=[], simulate=simulate)
    jones.p_bundle()
    jones.bookpage(4)
    cc.append(jones.visualize())
    cc.append(jones.visualize('timetracks'))
    # jones.display(full=True)

    if False:
        j2 = GJones(ns, quals=[], simulate=False)
        cc.append(j2.visualize())
        # j2.display(full=True)

    if False:
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
        jones = GJones(ns, quals='3c84', simulate=True)
        jj.append(jones)
        jones.visualize()
        jones.display(full=True, recurse=10)

    if 1:
        jones = BJones(ns, quals=['3c84'], simulate=False, telescope='WSRT', band='21cm')
        jj.append(jones)
        jones.visualize()
        jones.display(full=True)

    if 1:
        jones = FJones(ns, polrep='linear',simulate=True )
        # jones = FJones(ns, polrep='circular', quals='3c89', simulate=True)
        jj.append(jones)
        jones.visualize()
        jones.display(full=True, recurse=12)

    if 1:
        jones = JJones(ns, quals=['3c84'], diagonal=True, simulate=True)
        jj.append(jones)
        jones.display(full=True)

    if 1:
        jones.history().display(full=True)

    if 1:
        jseq = Joneseq22 (jj, quals='mmm')
        jseq.display(full=True)
        jseq.history().display(full=True)


#===============================================================
    
