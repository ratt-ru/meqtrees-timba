# file: ../Grunt/Joneset22.py

# History:
# - 25dec2006: creation
# - 14jan2007: keep only generic G/J/FJones
# - 29jan2007: added BJones
# - 30mar2007: adapted to QualScope etc
# - 07jun2007: adapted to NodeList/ParameterizationPlus
# - 02jul2007: adapted to Jones Contract

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

    def __init__(self, ns=None, name='<j>',
                 quals=[], kwquals={},
                 namespace=None,                                 # <---- !!
                 descr='<descr>',
                 stations=None,
                 polrep='linear',
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

        # TDL options (move to ParameterizationPlus.py?):
        self._TDLCompileOptionsMenu = None
        self._TDLCompileOption = dict()

        self._TDLSolveOptionsMenu = None
        self._TDLSolveOption = dict()
        self._TDLSolveOption_tobesolved = [None, 'A', 'B', ['A','B']]

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
        print '   - TDLCompileOptionsMenu: '+str(self._TDLCompileOptionsMenu)
        for key in self._TDLCompileOption.keys():
            print '     - '+str(key)+' = '+str(self._TDLCompileOption[key].value)
        print '   - TDLSolveOptionsMenu: '+str(self._TDLSolveOptionsMenu)
        for key in self._TDLSolveOption.keys():
            print '     - '+str(key)+' = '+str(self._TDLSolveOption[key].value)
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
        self._pg = dict()
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


    #-------------------------------------------------------------------
    # TDLOptions (move to ParameterizationPlus.py?)
    #-------------------------------------------------------------------

    def TDLCompileOptionsMenu (self, show=True):
        """Generic function for interaction with its TDLCompileOptions menu.
        The latter is created (once), by calling the specific function(s)
        .TDLCompileOptions(), which should be re-implemented by derived classes.
        The 'show' argument may be used to show or hide the menu. This can be done
        repeatedly, without duplicating the menu.
        """
        if not self._TDLCompileOptionsMenu:        # create the menu only once
            oolist = self.TDLCompileOptions()
            prompt = self.namespace(prepend='options for: '+self.name)
            self._TDLCompileOptionsMenu = TDLCompileMenu(prompt, *oolist)

        # Show/hide the menu as required (can be done repeatedly):
        self._TDLCompileOptionsMenu.show(show)
        return self._TDLCompileOptionsMenu

    #..................................................................

    def TDLCompileOptions (self):
        """Define a list of TDL options that control the structure of the
        Jones matrix.
        This function should be re-implemented by derived classes."""
        oolist = []

        if False:                    # temporary, just for testing
            key = 'xxx'
            self._TDLCompileOption[key] = TDLOption(key, 'prompt_xxx',
                                             range(3), more=int,
                                             doc='explanation for xxx....',
                                             namespace=self)
            oolist.append(self._TDLCompileOption[key])

        # Finished: Return a list of options:
        return oolist


    #--------------------------------------------------------------------

    def TDLSolveOptionsMenu (self, show=True):
        """Generic function for interaction with its TDLSolveOptions menu.
        The latter is created (once), by calling the specific function
        .TDLSolveOptions(), which should be re-implemented by derived classes.
        The 'show' argument may be used to show or hide the menu. This can be done
        repeatedly, without duplicating the menu.
        """
        if not self._TDLSolveOptionsMenu:           # create menu only once
            oolist = self.TDLSolveOptions()
            prompt = self.namespace(prepend='solve options for: '+self.name)
            self._TDLSolveOptionsMenu = TDLCompileMenu(prompt, *oolist)

        # Show/hide the menu as required (can be done repeatedly):
        self._TDLSolveOptionsMenu.show(show)
        return self._TDLSolveOptionsMenu


    #.....................................................................

    def TDLSolveOptions (self):
        """Return a list of TDL option objects that control solving for
        parmgroup(s) of the Jones matrix.
        This function should be re-implemented by derived classes."""
        oolist = []

        solist = self._TDLSolveOption_tobesolved       # defined in derived classes
        if self._simulate:
            solist = [None]
        doc = 'the selected groups will be solved simultaneously'
        prompt = 'solve for '+self.name+' parmgroup(s)'
        key = 'tobesolved'
        self._TDLSolveOption[key] = TDLOption(key, prompt,
                                              solist, more=str, doc=doc,
                                              namespace=self)
        if self._simulate:
            self._TDLSolveOption[key].set_value(None, save=True)
        oolist.append(self._TDLSolveOption[key])

        if False:
            # For testing only...
            oolist.append(TDLOption('dummy','another option',0))

        # Finished: Return a list of option objects:
        return oolist

    #.....................................................................

    def TDL_tobesolved (self, trace=False):
        """Get a list of the selected parmgroups (or tags?) of MeqParms
        that have been selected for solving."""
        slist = []
        key = 'tobesolved'
        if self._TDLSolveOption.has_key(key):
            slist = self._TDLSolveOption[key].value
        return slist




#=================================================================================================
# Make a Joneset22 object that is a sequence (matrix multiplication) of Jones matrices
# Semi-obsolete.....
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
    qq = first.p_get_quals(remove=[first.name])
    for jones in joneslist[1:]:
        name += jones.name[0]
        descr += '\n '+jones.name+': '+jones.descr()
        qq = jones.p_get_quals(merge=qq, remove=[jones.name])
    qq.extend(first.p_quals2list(quals))
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
        jnew.p_merge(jones)
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
                 stations=None, simulate=False):
        
        self._jname = 'GJones'
        Joneset22.__init__(self, ns=ns, quals=quals, name=name,
                           namespace=namespace,
                           polrep=polrep,
                           telescope=telescope, band=band,
                           stations=stations,
                           simulate=simulate)

        # Define the list of (groups of) parmgroups to be used in the TDL menu: 
        self._TDLSolveOption_tobesolved = [None, self._jname, 'Gphase', 'Ggain'] 

        # Finished:
        self.history(override)
        return None

    #------------------------------------------------------------------------------

    def define_parmgroups(self):
        """Define the various primary ParmGroups"""
        self._pg = dict()
        self._pname = 'Gphase'
        self._gname = 'Ggain'
        for pol in self.pols():                       # e.g. ['X','Y']
            self._pg[pol] = dict()
            rider = dict(use_matrix_element=self._pols_matrel()[pol])

            dev = self.p_deviation_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz=None)
            pg = self.p_group_define(self._pname+pol,
                                     descr=pol+'-dipole phases',
                                     default=0.0, unit='rad',
                                     tiling=1, time_deg=0, freq_deg=0,
                                     constraint=dict(sum=0.0, first=0.0),
                                     simul=self._simulate, deviation=dev,
                                     # override=override,
                                     rider=rider,
                                     tags=[self._pname,self._jname])
            self._pg[pol][self._pname] = pg

            dev = self.p_deviation_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz='{1000e6~10%}')
            pg = self.p_group_define(self._gname+pol,
                                     descr=pol+'-dipole gains',
                                     default=1.0,
                                     tiling=None, time_deg=2, freq_deg=0,
                                     # constrain_min=0.1, constrain_max=10.0,
                                     constraint=dict(product=1.0),
                                     simul=self._simulate, deviation=dev,
                                     # override=override,
                                     rider=rider,
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
            phase = self.p_group_create_member (self._pg[pol][self._pname], quals=station)
            gain = self.p_group_create_member (self._pg[pol][self._gname], quals=station)
            mm[pol] = qnode(pol)(station) << Meq.Polar(gain,phase)
        qnode(station) << Meq.Matrix22(mm[pols[0]],0.0, 0.0,mm[pols[1]])
        return qnode(station)




#--------------------------------------------------------------------------------------------
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

    def __init__(self, ns=None, name='BJones', quals=[], 
                 namespace=None,
                 polrep='linear',
                 telescope=None, band=None,
                 tfdeg=[0,5],
                 override=None,
                 stations=None, simulate=False):
        
        self._jname = 'BJones'
        Joneset22.__init__(self, ns=ns, quals=quals, name=name,
                           namespace=namespace,
                           polrep=polrep, telescope=telescope, band=band,
                           stations=stations,
                           simulate=simulate)

        # Define the list of (groups of) parmgroups to be used in the TDL menu: 
        self._TDLSolveOption_tobesolved = [None, self._jname, 'Breal', 'Bimag'] 

        self.history(override)
        return None


    #------------------------------------------------------------------------------

    def TDLCompileOptions (self):
        """Define a list of TDL option objects that control the structure
        of the Jones matrix."""
        oolist = []
        key = 'tfdeg'
        self._TDLCompileOption[key] = TDLOption(key, 'tfdeg',
                                         [[0,5],[0,4],[1,4]],
                                         doc='rank of time/freq polynomial',
                                         namespace=self)
        oolist.append(self._TDLCompileOption[key])
        # Finished: Return a list of option objects:
        return oolist


    #------------------------------------------------------------------------------

    def define_parmgroups(self):
        """Define the various primary ParmGroups"""
        self._pg = dict()
        pols = self.pols()                                # e.g. ['X','Y']
        self._iname = 'Bimag'
        self._rname = 'Breal'
        tfdeg = self._TDLCompileOption['tfdeg'].value
        for pol in pols:
            self._pg[pol] = dict()
            rider = dict(use_matrix_element=self._pols_matrel()[pol])
            dev = self.p_deviation_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz='{10e6~10%}')

            pg = self.p_group_define(self._iname+pol,
                                     descr=pol+'-IF bandpass imag.part',
                                     default=0.0, unit='Jy',
                                     tiling=1,
                                     time_deg=tfdeg[0],
                                     freq_deg=tfdeg[1],
                                     simul=self._simulate, deviation=dev,
                                     # override=override,
                                     rider=rider,
                                     tags=[self._iname,self._jname])
            self._pg[pol][self._iname] = pg

            pg = self.p_group_define(self._rname+pol,
                                     descr=pol+'-IF bandpass real.part',
                                     default=1.0, unit='Jy',
                                     tiling=None,
                                     time_deg=tfdeg[0],
                                     freq_deg=tfdeg[1],
                                     simul=self._simulate, deviation=dev,
                                     # override=override,
                                     rider=rider,
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
            real = self.p_group_create_member (self._pg[pol][self._rname], quals=station)
            imag = self.p_group_create_member (self._pg[pol][self._iname], quals=station)
            mm[pol] = qnode(pol)(station) << Meq.ToComplex(real,imag)
        qnode(station) << Meq.Matrix22(mm[pols[0]],0.0, 0.0,mm[pols[1]])
        return qnode(station)







#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------

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
                 stations=None, simulate=False):

        self._jname = 'JJones'
        Joneset22.__init__(self, ns=ns, quals=quals, name=name,
                           namespace=namespace,
                           polrep=polrep, telescope=telescope, band=band,
                           stations=stations,
                           simulate=simulate)
        
        # Define the list of (groups of) parmgroups to be used in the TDL menu: 
        self._TDLSolveOption_tobesolved = [None, self._jname, 'Jdiag'] 

        self.history(override)
        return None

    #------------------------------------------------------------------------------

    def TDLCompileOptions (self):
        """Define a list of TDL options that control the structure of the
        Jones matrix."""
        oolist = []
        key = 'diagonal'
        self._TDLCompileOption[key] = TDLOption(key, 'diagonal elements only',
                                         [True, False],
                                         # doc='structure of Jones matrix',
                                         namespace=self)
        oolist.append(self._TDLCompileOption[key])
        return oolist


    #------------------------------------------------------------------------------

    def define_parmgroups(self):
        """Define the various primary ParmGroups"""
        self._pg = dict()
        dev = self.p_deviation_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz='{10e6~10%}')
        for ename in ['J11','J22']:
            self._pg[ename] = dict()
            for rim in ['real','imag']:
                default = 0.0
                constraint = dict(sum=0.0)
                if rim=='real':
                    default = 1.0
                    constraint = dict(product=1.0)
                pg = self.p_group_define(ename+rim,
                                         descr=rim+' part of matrix element '+ename,
                                         default=default, unit='Jy',
                                         tiling=None, time_deg=0, freq_deg=0,
                                         simul=self._simulate, deviation=dev,
                                         constraint=constraint,
                                         # override=override,
                                         tags=[self._jname,'Jdiag'])
                self._pg[ename][rim] = pg

        TDL_diagonal = self._TDLCompileOption['diagonal'].value
        if not TDL_diagonal:
            for ename in ['J12','J21']:
                self._pg[ename] = dict()
                for rim in ['real','imag']:
                    pg = self.p_group_define(ename+rim, 
                                             descr=rim+' part of matrix element '+ename,
                                             default=0.0, unit='Jy',
                                             tiling=None, time_deg=0, freq_deg=0,
                                             simul=self._simulate, deviation=dev,
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
            real = self.p_group_create_member (self._pg[ename]['real'], quals=station)
            imag = self.p_group_create_member (self._pg[ename]['imag'], quals=station)
            mm[ename] = self.ns[ename](station) << Meq.ToComplex(real,imag)
        qnode(station) << Meq.Matrix22(mm[enames[0]],mm[enames[1]],
                                 mm[enames[2]],mm[enames[3]])
        return qnode(station)





#--------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------

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
                 stations=None, simulate=False):
        
        self._jname = 'FJones'
        Joneset22.__init__(self, ns=ns, quals=quals, name=name,
                           namespace=namespace,
                           polrep=polrep, telescope=telescope, band=band,
                           stations=stations,
                           simulate=simulate)
        
        # Define the list of (groups of) parmgroups to be used in the TDL menu: 
        self._TDLSolveOption_tobesolved = [None, self._jname, 'RM'] 

        self.history(override)
        return None

    #------------------------------------------------------------------------------

    def define_parmgroups(self):
        """Define the various primary ParmGroups"""
        self._pg = dict()
        self._rname = 'RM'       
        dev = self.p_deviation_expr (ampl='{0.01~10%}', Psec='{500~10%}', PHz=None)
        pg = self.p_group_define(self._rname,  
                                 descr='Faraday Rotation Measure (rad/m2)',
                                 default=0.0, unit='rad/m2',
                                 simul=self._simulate, deviation=dev,
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
            
            RM = self.p_group_create_member (self._pg[self._rname])
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
    j22 = Joneset22(quals=[], simulate=True)
    j22.TDLCompileOptionsMenu()
    j22.TDLSolveOptionsMenu()
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
if False:
    TDLCompileMenu('solvable parmgroup(s)',
                   GJones().TDLSolveOptionsMenu(),
                   BJones().TDLSolveOptionsMenu(),
                   JJones().TDLSolveOptionsMenu(),
                   FJones().TDLSolveOptionsMenu(),
                   );


def _define_forest(ns):

    cc = []
    jj = []
    simulate = True

    if 0:
        jones = GJones(ns, quals=[], simulate=simulate)
        jj.append(jones)
        # cc.append(jones.p_bundle(combine='Composer'))
        # cc.append(jones.p_plot_rvsi())
        # jones.bookpage(4)
        # cc.append(jones.visualize('rvsi'))          # default is rvsi
        # cc.append(jones.visualize('timetracks'))
        # cc.append(jones.visualize('spectra'))
        # jones.display(full=True)

    if 0:
        j2 = GJones(ns, quals=[], simulate=False)
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
        cc.append(jseq.p_bundle())
        cc.append(jseq.p_compare('GphaseA','GphaseB'))
        cc.append(jseq.p_plot_rvsi())
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
        jones = GJones(ns, quals='3c84', simulate=False)
        jones.make_jones_matrices()
        jj.append(jones)
        # jones.visualize()
        jones.TDLCompileOptionsMenu()
        jones.TDLSolveOptionsMenu()
        jones.display(full=True, recurse=10)

    if 0:
        j22 = jones()
        j22 = jones(1)
        j22 = jones([2])
        j22 = jones(5)

    if 0:
        jones = BJones(ns, quals=['3c84'], simulate=False, telescope='WSRT', band='21cm')
        jj.append(jones)
        # jones.visualize()
        jones.display(full=True)

    if 0:
        jones = JJones(ns, quals=['3c84'], diagonal=True, simulate=True)
        jj.append(jones)
        jones.display(full=True)

    if 0:
        jones = FJones(ns, polrep='linear',simulate=True )
        # jones = FJones(ns, polrep='circular', quals='3c89', simulate=True)
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
    
