# file: ../Grunt/Jones.py

# History:
# - 25dec2006: creation

# Description:

# The Jones class is a base-class for classes that define and
# encapsulate groups of 2x2 station Jones matrices.


from Timba.TDL import *
# from Timba.Contrib.JEN.Grunt import ParmGroup
from ParmGroup import *
from copy import deepcopy

#======================================================================================

class Jones (object):
    """Class that represents a set of 2x2 Jones matrices"""

    def __init__(self, ns, scope=[], letter='<j>',
                 telescope=None, stations=None, polrep=None,
                 simulate=False):

        # Telescope-specific information:
        self._telescope = telescope
        self._stations = deepcopy(stations)          # list of (array) stations
        self._polrep = polrep                        # polarization representation (linear, circular)
        if self._telescope=='WSRT':
            if self._stations==None: self._stations = range(1,15)
            self._polrep = 'linear'
        elif self._telescope=='VLA':
            if self._stations==None: self._stations = range(1,28)
            self._polrep = 'circular'
        elif self._telescope=='ATCA':
            if self._stations==None: self._stations = range(1,7)
            self._polrep = 'linear'
        elif self._telescope=='GMRT':
            if self._stations==None: self._stations = range(1,31)
            self._polrep = 'linear'
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
        self._matrix = None                          # the actual jones matrices (contract!)
        self._parmgroup = dict()                     # available parameter group objects
        self._composite = dict()                     # see define_composite_parmgroups()
        self._dummyParmGroup = ParmGroup('dummy')
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

    def scope(self):
        """Return the object scope (e.g. the peeling source name).
        The scope is translated into nodename qualifiers. It can be a list.""" 
        return self._scope

    def matrix(self):
        """Return the 2x2 Jones matrices themselves""" 
        return self._matrix

    def matrel(self, index=[1,1]):
        """Return the specified matrix element(s) only""" 
        scope = self.scope()
        name = self.letter()+'jones'+str(index[0])+str(index[1])
        print '\n** matrel(index=',index,'):'
        for s in self.stations():
            node = self._ns[name](*scope)(s) << Meq.Selector(self._matrix(s),
                                                             index=index)
            print '-',s,':',node
        return self._ns[name](*scope)

    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += ' '+str(self._letter)
        if self._telescope: ss += ' '+str(self._telescope)
        ss += ' (n='+str(len(self._stations))+')'
        ss += ' scope='+str(self._scope)
        # if self._simulate: ss += ' (simulate)'
        return ss

    def display(self, txt=None, full=False):
        """Print a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print ' * (txt='+str(txt)+')'
        print ' * stations: '+str(self.stations())
        print ' * polrep: '+str(self._polrep)+' '+str(self._pols)
        if not self._matrix:
            print '** self._matrix not defined (yet)....'
        else:
            print ' * Station Jones matrices: '
            for s in self.stations():
                print '  - '+str(s)+': '+str(self.matrix()(s))
            print ' * The first Jones matrix:'
            node = self.matrix()(self.stations()[0])
            self._dummyParmGroup.display_subtree(node, txt=str(0), recurse=2)
        print ' * Available ParmGroup objects: '
        for key in self.parmgroups():
            if not self._parmgroup[key]._composite:
                print '  - '+str(self._parmgroup[key].oneliner())
                # if full: self._parmgroup[key].display_node (index=0)
        for key in self.parmgroups():
            if self._parmgroup[key]._composite:
                print '  - '+str(self._parmgroup[key].oneliner())
        print '**\n'
        return True

    #-------------------------------------------------------------------

    def define_parmgroup(self, name, descr=None,
                         default=0.0, tags=[],
                         Tsec=1000.0, Tstddev=0.1,
                         scale=None, stddev=0.1,
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


#===============================================================
# Example of an actual Jones matrix
#===============================================================

class GJones (Jones):
    """Class that represents a set of 2x2 GJones matrices"""

    def __init__(self, ns, scope=[], letter='G',
                 telescope=None, stations=None,
                 simulate=False):
        Jones.__init__(self, ns, scope=scope, letter=letter,
                       telescope=telescope, stations=stations,
                       simulate=simulate)
        pols = self._pols
        scope = self._scope
        pname = self._letter+'phase'
        gname = self._letter+'gain'
        jname = self._letter+'Jones'
        # Define the various primary ParmGroups:
        for pol in pols:
            self.define_parmgroup(pname+pol, descr=pol+'-dipole phases',
                                  tags=[pname,jname], scale=1.0, Tsec=200)
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

class JJones (Jones):
    """Class that represents a set of 2x2 JJones matrices"""

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
                self.define_parmgroup(ename+rim, default=default, scale=1.0, Tsec=200,
                                      descr=rim+' part of matrix element '+ename,
                                      tags=[jname,'Jdiag'])
        if not diagonal:
            for ename in ['J12','J21']:
                ee.append(ename)
                for rim in ['real','imag']:
                    self.define_parmgroup(ename+rim, scale=1.0, Tsec=200,
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




#--------------------------------------------------------------------------------------------

class DJones (Jones):
    """Class that represents a set of 2x2 WSRT DJones matrices"""

    def __init__(self, ns, scope='<scope>', letter='D'):
        Jones.__init__(self, ns, letter, scope)
        self.define_parmgroup('Dell', descr='dipole ellipticity')
        self.define_parmgroup('Dang', descr='dipole angle error')
        letter = self.letter()
        scope = self.scope()
        node_groups = ['Parm',scope]
        for s in self._stations:
            dell = self._ns.Dell(s) << Meq.Parm(0.0, node_groups=node_groups,
                                                       tags=['Dell','DJones'])
            self._parmgroup['Dell'].append(dell)
            dang = self._ns.Dang(s) << Meq.Parm(0.0, node_groups=node_groups,
                                                       tags=['Dang','DJones'])
            self._parmgroup['Dang'].append(dang)
            self._ns[letter](s) << Meq.ToComplex(dang,dell)
        self._matrix = self._ns[letter]
        return None

     
#===============================================================

#===============================================================

if __name__ == '__main__':
    ns = NodeScope()

    if 0:
        Gjones = GJones(ns, scope=['3c84','xxx'], simulate=True)
        Gjones.display(full=True)

    if 0:
        Gjones.parmlist()
        Gjones.parmlist('Gphase')
        Gjones.parmlist('GphaseX')

    if 0:
        nn = Gjones.matrel()
        print '\n** matrel result:'
        for s in Gjones.stations():
            print '--',s,':',nn(s)
        print '-- (',6,'):',nn(6)     # !!

    if 0:
        Gjones.matrel([1,2])
        Gjones.matrel([2,1])
        Gjones.matrel([2,2])
        Gjones.matrel([3,2])          # !!

    if 1:
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
    
