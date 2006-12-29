# file: ../Grunt/Jones.py

# History:
# - 25dec2006: creation

# Description:

# The Jones class is a base-class for classes that define and
# encapsulate groups of 2x2 station Jones matrices.


from Timba.TDL import *
# from Timba.Contrib.JEN.Grunt import ParmGroup
from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect
from ParmGroup import *
from copy import deepcopy

#======================================================================================

class Jones (object):
    """Class that represents a set of 2x2 Jones matrices"""

    def __init__(self, ns, scope=[], letter='<j>',
                 telescope=None, stations=None, polrep=None,
                 simulate=False):

        # Telescope-specific information:
        self._telescope = telescope                  # e.g. WSRT
        self._stations = deepcopy(stations)          # list of (array) stations
        self._polrep = polrep                        # polarization representation (linear, circular)
        self._mount = None                           # Antenna mount (equatotial, altaz, None, ...)
        self._diam = None                            # antenna diameter (m)

        if self._telescope=='WSRT':
            if self._stations==None: self._stations = range(1,15)
            self._polrep = 'linear'
            self._mount = 'equatorial'
            self._diam = 25
        elif self._telescope=='LOFAR':
            if self._stations==None: self._stations = range(1,31)
            self._polrep = 'linear'
            self._mount = 'horizontal'
            self._diam = 60
        elif self._telescope=='VLA':
            if self._stations==None: self._stations = range(1,28)
            self._polrep = 'circular'
            self._mount = 'altaz'
            self._diam = 25
        elif self._telescope=='ATCA':
            if self._stations==None: self._stations = range(1,7)
            self._polrep = 'linear'
            self._mount = 'altaz'
            self._diam = 25
        elif self._telescope=='GMRT':
            if self._stations==None: self._stations = range(1,31)
            self._polrep = 'linear'
            self._mount = 'altaz'
            self._diam = 45
        elif self._stations==None:
            self._stations = range(1,4)              # for testing convenience....

        self._pols = ['A','B']
        if self._polrep == 'linear':
            self._pols = ['X','Y']
        elif self._polrep == 'circular':
            self._pols = ['R','L']

        self._ns = ns                                # node-scope (required)
        self._letter = letter                        # letter(s) of the Jones matrix (e.g. G) 
        self._scope = scope                          # scope, e.g. (peeling)source-name
        if not isinstance(self._scope,(list,tuple)):
            self._scope = [self._scope]
        self._simulate = simulate                    # if True, use simulation subtrees (i.s.o. MeqParms)
        if self._simulate:
            self._scope.append('simul')
        self._matrix = None                          # the actual Jones matrices (contract!)
        self._matrel = dict(J11=None, J12=None, J21=None, J22=None)  # Jones matrix elements (contract!)
        self._parmgroup = dict()                     # available parameter group objects
        self._composite = dict()                     # see define_composite_parmgroups()
        self._dummyParmGroup = ParmGroup('dummy')
        self._dcoll = None
        return None

    def telescope(self):
        """Return the name of the relevant telescope (e.g. WSRT)"""
        return self._telescope

    def stations(self):
        """Return a list of (array) stations"""
        return self._stations

    def polrep(self):
        """Return the polarization representation (linear, circular, None)"""
        return self._polrep

    def pols(self):
        """Return the list of 2 polarization names (e.g. ['X','Y'])"""
        return self._pols

    def letter(self):
        """Return the Jones object name-letter (e.g. G)""" 
        return self._letter

    def scope(self, append=None):
        """Return the object scope (e.g. the peeling source name).
        Optionally, append the given qualifiers to the returned scope.
        The scope is translated into nodename qualifiers. It can be a list.""" 
        scope = deepcopy(self._scope)
        if not append==None:
            if not isinstance(scope,(list,tuple)):
                scope = [scope]
            if isinstance(append,(list,tuple)):
                scope.extend(append)
            else:
                scope.append(append)
        return scope

    def matrix(self):
        """Return the 2x2 Jones matrices themselves""" 
        return self._matrix

    def matrel(self, key='J11', return_nodes=False):
        """Return the specified matrix element(s) only"""
        if not self._matrel.has_key(key):
            return False                                # invalid key.....
        if not self._matrel[key]:
            # Not yet extracted: do so: 
            scope = self.scope()
            name = self.letter()+'Jones_'+key[1:]
            index = dict(J11=[1,1], J12=[1,2], J21=[2,1], J22=[2,2])
            print '\n** matrel(',key,') index=',index[key],':'
            for s in self.stations():
                node = self._ns[name](*scope)(s) << Meq.Selector(self._matrix(s),
                                                                 index=index[key])
                print '-',s,':',node
            self._matrel[key] = self._ns[name](*scope)
        # Return a list of nodes, if required:
        if return_nodes:
            nodes = []
            for s in self.stations():
                nodes.append(self._matrel[key](s))
            for node in nodes: print '-',node 
            return nodes
        # Otherwise, return the 'contract':
        return self._matrel[key] 

    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += '  '+str(self._letter)
        if self._telescope:
            ss += '  '+str(self._telescope)
        else:
            ss += '  pols='+str(self._pols)
        ss += '  n='+str(len(self._stations))
        ss += '  scope='+str(self._scope)
        # if self._simulate: ss += ' (simulate)'
        return ss

    def display(self, txt=None, full=False):
        """Print a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print ' * (txt='+str(txt)+')'
        print ' * stations ('+str(len(self.stations()))+'): '+str(self.stations())
        print ' * polrep: '+str(self._polrep)+', pols='+str(self._pols)
        print ' * Antenna mount: '+str(self._mount)+', diam='+str(self._diam)+'(m)'
        if not self._matrix:
            print '** self._matrix not defined (yet)....'
        else:
            print ' * Station Jones matrices: '
            for s in self.stations():
                print '  - '+str(s)+': '+str(self.matrix()(s))
            print ' * The first two station Jones matrices:'
            for i in range(len(self.stations())):
                if i<2:
                    node = self.matrix()(self.stations()[i])
                    self._dummyParmGroup.display_subtree(node, txt=str(i), recurse=2)
        print ' * Extracted Jones matrix elements: '
        for key in self._matrel.keys():
            print '  - '+str(key)+': '+str(self._matrel[key])
        print ' * Available ParmGroup objects: '
        for key in self.parmgroups():
            if not self._parmgroup[key]._composite:
                print '  - '+str(self._parmgroup[key].oneliner())
                # if full: self._parmgroup[key].display_node (index=0)
        for key in self.parmgroups():
            if self._parmgroup[key]._composite:
                print '  - '+str(self._parmgroup[key].oneliner())
        if self._dcoll:
            print ' * Visualization subtree (dcoll): '
            self._dummyParmGroup.display_subtree(self._dcoll, txt='dcoll', recurse=1)
        print '**\n'
        return True

    #-------------------------------------------------------------------

    def define_parmgroup(self, name, descr=None,
                         default=0.0, tags=[],
                         Tsec=1000.0, Tstddev=0.1,
                         scale=1.0, stddev=0.1,
                         pg=None):
        """Helper function to define a named ParmGroup object"""

        # ....
        node_groups = ['Parm']
        # node_groups.extend(self._scope)               # <---------- !!!

        # Make sure that the group name is in the list of node tags:
        if not isinstance(tags,(list,tuple)): tags = [tags]
        if not name in tags: tags.append(name)

        # OK, define the ParmGroup:
        self._parmgroup[name] = ParmGroup (self._ns, name=name, scope=self._scope,
                                           descr=descr, default=default,
                                           tags=tags, node_groups=node_groups,
                                           simulate=self._simulate,
                                           Tsec=Tsec, Tstddev=Tstddev,
                                           scale=scale, stddev=stddev,
                                           pg=pg)

        # Collect information for define_composite_parmgroups():
        for tag in tags:
            if not tag in [name]:
                self._composite.setdefault(tag, [])
                self._composite[tag].append(self._parmgroup[name])

        # Finished:
        return self._parmgroup[name]

    #.....................................................................................

    def define_composite_parmgroups(self, name='GJones'):
        """Helper function to define composite ParmGroups.
        It uses the information gleaned from the tags in define_ParmGroup()"""
        print '\n** define_composite_parmgroups(',name,'):'
        # First collect the primary ParmGroups in pg:
        pg = []
        for key in self._parmgroup.keys():
            pg.append(self._parmgroup[key])
            print '-',name,key
        # Then make separate composites, as defined by the tags above:
        for key in self._composite.keys():
            print '-',key,len(self._composite[key])
            self.define_parmgroup(key, descr='<descr>', pg=self._composite[key])
        self.define_parmgroup(name, descr='all '+name+' parameters', pg=pg)
        return None

    #.....................................................................................

    def parmgroups(self):
        """Return the available parmgroup names""" 
        return self._parmgroup.keys()
    
    def parmgroup(self, key=None):
        """Return the specified parmgroup (object)""" 
        return self._parmgroup[key]

    def parmlist(self, keys='*'):
        """Return the list of nodes from the specified parmgroup(s)"""
        if keys=='*': keys = self._parmgroup.keys()
        if not isinstance(keys,(list,tuple)): keys = [keys]
        nodelist = []
        for key in keys:
            if self._parmgroup.has_key(key):
                nodelist.extend(self._parmgroup[key].nodelist())
            else:
                print '** parmgroup not recognised:',key
                return None
        print '\n** parmlist(',keys,'):'
        for node in nodelist: print ' -',node
        print 
        return nodelist

    #-------------------------------------------------------------------

    def multiply(self, jones):
        """Multiply with the given Jones object"""
        name = self.letter()+jones.letter()+'Jones'
        scope = self.scope()
        for s in self._stations:
            self._ns[name](*scope)(s) << Meq.MatrixMultiply(self._matrix(s),
                                                            jones._matrix(s))
        # Update the Jones object attributes:
        self._matrix = self._ns[name](*scope)
        self._letter += jones._letter
        self._parmgroup.update(jones._parmgroup)
        return True

    #-------------------------------------------------------------------

    def compare(self, jones):
        """Compare with the given Jones object"""
        return True

    #-------------------------------------------------------------------

    def visualize (self):
        """Visualise the 4 complex matrix elements of all station
        Jones matrices in a single real-vs-imag plot. Different
        matrix elements (J11,J12,J21,J22) have different styles
        and colors, which are the same for all Jones matrices."""
        if not self._dcoll:
            style = dict(J11='circle', J12='xcross', J21='xcross', J22='circle')
            color = dict(J11='red', J12='magenta', J21='darkCyan', J22='blue')
            scope = self.scope()
            dcoll_scope = self.letter()
            for s in scope: dcoll_scope += '_'+s 
            dcolls = []
            for key in self._matrel.keys():
                cc = self.matrel(key, return_nodes=True) 
                rr = MG_JEN_dataCollect.dcoll (self._ns, cc, 
                                               scope=dcoll_scope, tag=key,
                                               color=color[key], style=style[key],
                                               size=8, pen=2,
                                               type='realvsimag', errorbars=True)
                dcolls.append(rr)
                # Make a combined plot of all the matrix elements:
                # NB: nodename -> dconc_scope_tag
            rr = MG_JEN_dataCollect.dconc(self._ns, dcolls,
                                          scope=dcoll_scope,
                                          tag=key, bookpage=None)
        # Return the dataConcat node:
        self._dcoll = rr['dcoll']
        return self._dcoll











#=================================================================================================
# Example of an actual Jones matrix
#=================================================================================================

class GJones (Jones):
    """Class that represents a set of 2x2 GJones matrices,
    which model the (complex) gains due to electronics
    and (optionally) the tropospheric phase (a.k.a. TJones).
    GJones is a uv-plane effect, i.e. it is valid for the entire FOV.
    GJones is the same for linear and circular polarizations."""

    def __init__(self, ns, scope=[], letter='G',
                 telescope=None, stations=None, polrep='linear',
                 simulate=False):
        Jones.__init__(self, ns, scope=scope, letter=letter,
                       telescope=telescope, stations=stations, polrep=polrep,
                       simulate=simulate)
        pols = self._pols
        scope = self._scope
        pname = self._letter+'phase'
        gname = self._letter+'gain'
        jname = self._letter+'Jones'
        # Define the various primary ParmGroups:
        for pol in pols:
            self.define_parmgroup(pname+pol, descr=pol+'-dipole phases',
                                  tags=[pname,jname], Tsec=200)
            self.define_parmgroup(gname+pol, descr=pol+'-dipole gains',
                                  tags=[gname,jname], default=1.0)
        # Make the Jones matrices per station:
        for s in self._stations:
            mm = dict()
            for pol in pols:
                phase = self._parmgroup[pname+pol].create(s)
                gain = self._parmgroup[gname+pol].create(s)
                mm[pol] = self._ns[jname+pol](*scope)(s) << Meq.Polar(gain,phase)
            self._ns[jname](*scope)(s) << Meq.Matrix22(mm[pols[0]],0.0,
                                                       0.0,mm[pols[1]])
        self._matrix = self._ns[jname](*scope)
        # Make some secondary (derived) ParmGroups:
        self.define_composite_parmgroups(jname)
        return None

#--------------------------------------------------------------------------------------------

class EJones (Jones):
    """Class that represents a set of 2x2 EJones matrices,
    which model the station beamshapes.
    EJones is an image-plane effect."""

    def __init__(self, ns, scope=[], letter='E',
                 telescope=None, stations=None, polrep='linear',
                 simulate=False):
        Jones.__init__(self, ns, scope=scope, letter=letter,
                       telescope=telescope, stations=stations, polrep=polrep,
                       simulate=simulate)
        pols = self._pols
        scope = self._scope
        pname = self._letter+'phase'
        gname = self._letter+'gain'
        jname = self._letter+'Jones'
        # Define the various primary ParmGroups:
        for pol in pols:
            self.define_parmgroup(pname+pol, descr=pol+'-dipole phases',
                                  tags=[pname,jname], Tsec=200)
            self.define_parmgroup(gname+pol, descr=pol+'-dipole gains',
                                  tags=[gname,jname], default=1.0)
        # Make the Jones matrices per station:
        for s in self._stations:
            mm = dict()
            for pol in pols:
                phase = self._parmgroup[pname+pol].create(s)
                gain = self._parmgroup[gname+pol].create(s)
                mm[pol] = self._ns[jname+pol](*scope)(s) << Meq.Polar(gain,phase)
            self._ns[jname](*scope)(s) << Meq.Matrix22(mm[pols[0]],0.0,
                                                       0.0,mm[pols[1]])
        self._matrix = self._ns[jname](*scope)
        # Make some secondary (derived) ParmGroups:
        self.define_composite_parmgroups(jname)
        return None



#--------------------------------------------------------------------------------------------
class FJones (Jones):
    """Class that represents a set of 2x2 FJones matrices,
    for both polarization representations (linear and circular).
    For the moment, the ionospheric Faraday rotation is assumen
    to be the same for all stations, and the entire FOV."""

    def __init__(self, ns, scope=[], letter='F',
                 telescope=None, stations=None, polrep='linear',
                 simulate=False):
        Jones.__init__(self, ns, scope=scope, letter=letter,
                       telescope=telescope, stations=stations, polrep=polrep,
                       simulate=simulate)
        scope = self.scope()
        polrep = self.polrep()
        rname = self._letter+'rm'       
        jname = self._letter+'Jones'

        # Define the primary ParmGroup:
        self.define_parmgroup(rname, descr='Faraday Rotation Measure (rad/m2)',
                              tags=[rname,jname])

        RM = self._parmgroup[rname].create()                  # Rotation Measure (rad/m2)
        wvl = self._ns << Meq.Divide(3e8, self._ns << Meq.Freq())
        wvl2 = self._ns << Meq.Sqr(wvl)                       # lambda squared
        farot = self._ns.farot(*scope) << (RM * wvl2)         # Faraday rotation angle
        
        # Make the (overall) 2x2 Fjones matrix:
        if polrep=='circular':
            # Circular pol: The Faraday rotation is just a phase effect:
            farot2 = self._ns << farot/2
            farot2neg = self._ns << Meq.Negate(farot2)
            fmat = self._ns[jname](*scope)(polrep) << Meq.Matrix22(farot2,0.0,0.0,farot2neg)

        else:
            # Linear pol: The Faraday rotation is a (dipole) rotation:
            cos = self._ns << Meq.Cos(farot)
            sin = self._ns << Meq.Sin(farot)
            sinneg = self._ns << Meq.Negate(sin)
            fmat = self._ns[jname](*scope)(polrep) << Meq.Matrix22(cos,sin,sinneg,cos)

        # The station Jones matrices are all the same (fmat):  
        for s in self._stations:
            self._ns[jname](*scope)(polrep)(s) << Meq.Identity(fmat)
            
        self._matrix = self._ns[jname](*scope)(polrep)
        # Make some secondary (derived) ParmGroups:
        self.define_composite_parmgroups(jname)
        return None



#--------------------------------------------------------------------------------------------

class DJones (Jones):
    """Class that represents a set of 2x2 DJones matrices"""

    def __init__(self, ns, scope=[], letter='D',
                 telescope=None, stations=None, polrep='linear',
                 coupled_dang=True, coupled_dell=True,
                 simulate=False):
        Jones.__init__(self, ns, scope=scope, letter=letter,
                       telescope=telescope, stations=stations, polrep=polrep,
                       simulate=simulate)
        pols = self._pols
        scope = self._scope
        dname = self._letter+'dang'
        ename = self._letter+'dell'
        pname = self._letter+'pzd'
        jname = self._letter+'Jones'

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
        pzd = self._parmgroup[pname].create()
        pzd2 = self._ns << pzd/2
        pzd2neg = self._ns << Meq.Negate(pzd2)
        pmat = self._ns[pname](*scope) << Meq.Matrix22(pzd2,0.0,0.0,pzd2neg)

        # Make the Jones matrices per station:
        for s in self._stations:

            # Dipole rotation angles:
            if coupled_dang:
                dang = self._parmgroup[dname].create(s)
                cos = self._ns << Meq.Cos(dang)
                sin = self._ns << Meq.Sin(dang)
                sinneg = self._ns << Meq.Negate(sin)
                dmat = self._ns[dname](*scope)(s) << Meq.Matrix22(cos,sin,sinneg,cos)
            else:
                dang1 = self._parmgroup[dname+pols[0]].create(s)
                dang2 = self._parmgroup[dname+pols[1]].create(s)
                cos1 = self._ns << Meq.Cos(dang1)
                cos2 = self._ns << Meq.Cos(dang2)
                sin1 = self._ns << Meq.Negate(self._ns << Meq.Sin(dang1))
                sin2 = self._ns << Meq.Sin(dang2)
                dmat = self._ns[dname](*scope)(s) << Meq.Matrix22(cos1,sin1,sin2,cos2)


            # Dipole ellipticities:
            if coupled_dell:
                dell = self._parmgroup[ename].create(s)
                cos = self._ns << Meq.Cos(dell)
                sin = self._ns << Meq.Sin(dell)
                isin = self._ns << Meq.ToComplex(0.0, sin)
                emat = self._ns[ename](*scope)(s) << Meq.Matrix22(cos,isin,isin,cos)
            else:
                dell1 = self._parmgroup[ename+pols[0]].create(s)
                dell2 = self._parmgroup[ename+pols[1]].create(s)
                cos1 = self._ns << Meq.Cos(dell1)
                cos2 = self._ns << Meq.Cos(dell2)
                isin1 = self._ns << Meq.ToComplex(0, self._ns << Meq.Sin(dell1))
                isin2 = self._ns << Meq.ToComplex(0, self._ns << Meq.Sin(dell2))
                isin2 = self._ns << Meq.Conj(isin2)
                emat = self._ns[ename](*scope)(s) << Meq.Matrix22(cos1,isin1,isin2,cos2)

            # Make the station Jones matrix by multiplying the sub-matrices:
            self._ns[jname](*scope)(s) << Meq.MatrixMultiply (dmat, emat, pmat)

        self._matrix = self._ns[jname](*scope)
        # Make some secondary (derived) ParmGroups:
        self.define_composite_parmgroups(jname)
        return None



#--------------------------------------------------------------------------------------------

class JJones (Jones):
    """Class that represents a set of 2x2 JJones matrices.
    Each of the 4 complex elements of a station Jones matrix
    is assumed to be independent. The parameters are their real
    and imaginary parts (i.e. 8 real parameters per station).
    JJones is the same for linear and circular polarizations."""

    def __init__(self, ns, scope=[], letter='J',
                 diagonal=False,
                 telescope=None, stations=None,
                 simulate=False):
        Jones.__init__(self, ns, scope=scope, letter=letter,
                       telescope=telescope, stations=stations,
                       simulate=simulate)
        scope = self._scope
        jname = self._letter+'Jones'
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
        for s in self._stations:
            mm = dict(J12=0.0, J21=0.0)
            for ename in ee:
                real = self._parmgroup[ename+'real'].create(s)
                imag = self._parmgroup[ename+'imag'].create(s)
                mm[ename] = self._ns[ename](*scope)(s) << Meq.ToComplex(real,imag)
            self._ns[jname](*scope)(s) << Meq.Matrix22(mm[enames[0]],mm[enames[1]],
                                                       mm[enames[2]],mm[enames[3]])
        self._matrix = self._ns[jname](*scope)
        # Make some secondary (derived) ParmGroups:
        self.define_composite_parmgroups(jname)
        return None





     
#===============================================================

#===============================================================

if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        Gjones = GJones(ns, scope=['3c84','xxx'], simulate=True)
        Gjones.visualize()
        Gjones.display(full=True)

    if 0:
        Gjones.parmlist()
        Gjones.parmlist('Gphase')
        Gjones.parmlist('GphaseX')

    if 0:
        nn = Gjones.matrel(return_nodes=False)
        Gjones.display(full=True)
        print '\n** matrel result:'
        for s in Gjones.stations():
            print '--',s,':',nn(s)
        print '-- (',6,'):',nn(6)     # !!
        print
        nn = Gjones.matrel(return_nodes=True)

    if 0:
        Gjones.matrel('J11')
        Gjones.matrel('J12')
        Gjones.matrel('J21')
        Gjones.matrel('J22')
        Gjones.display(full=True)

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
            Gjones = GJones(ns, scope=['3c84','xxx'], simulate=True)
            Gjones.display(full=True)
            Gjones.multiply(Jjones)
            Gjones.display(full=True)

    if 0:
        Djones = DJones(ns)
        Djones.display()
        Gjones.multiply(Djones)
        Gjones.display()

#===============================================================
    
