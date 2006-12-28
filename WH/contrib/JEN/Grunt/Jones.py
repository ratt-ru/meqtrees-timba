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

    def __init__(self, ns, scope=[], name='<Jones>',
                 stations=None, polrep=None,
                 simulate=False):
        if stations==None: stations = range(1,4)     # for testing convenience....
        self._ns = ns                # node-scope (required)
        self._name = name            # name of the Jones matrix (e.g. G) 
        self._scope = scope          # scope, e.g. (peeling)source-name
        if not isinstance(self._scope,(list,tuple)):
            self._scope = [self._scope]
        self._simulate = simulate    # if True, use simulation subtrees (i.s.o. MeqParms)
        if self._simulate:
            self._scope.append('simul')
        self._stations = stations    # list of (array) stations
        self._polrep = polrep        # polarization representation (linear, circular)
        self._pols = ['A','B']
        if self._polrep == 'linear':
            self._pols = ['X','Y']
        elif self._polrep == 'circular':
            self._pols = ['R','L']
        self._matrix = None          # the actual jones matrices
        self._parmgroup = dict()     # available parameter group objects
        self._composite = dict()     # see define_composite_parmgroups()
        return None

    def stations(self):
        """Return a list of (array) stations"""
        return self._stations

    def polrep(self):
        """Return the polarization representation (linear, circular, None)"""
        return self._polrep

    def pols(self):
        """Return the list of 2 polarization names (e.g. ['X','Y'])"""
        return self._pols

    def name(self):
        """Return the object name (e.g. G)""" 
        return self._name

    def scope(self):
        """Return the object scope (e.g. the peeling source name).
        The scope is translated into nodename qualifiers. It can be a list.""" 
        return self._scope

    def matrix(self):
        """Return the 2x2 Jones matrices themselves""" 
        return self._matrix

    def matrel(self, index=[1,1]):
        """Return the specified matrix element(s) only""" 
        name = self.name()
        scope = self.scope()
        sindex = str(index[0])+str(index[1])
        print '\n** matrel(index=',index,'):'
        for s in self.stations():
            node = self._ns.matrel(name)(*scope)(sindex)(s) << Meq.Selector(self._matrix(s),
                                                                            index=index)
            print '-',s,':',node
        return self._ns.matrel(name)(sindex)

    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += ' '+str(self._name)
        ss += ' scope='+str(self._scope)
        if self._simulate: ss += ' (simulate)'
        return ss

    def display(self, txt=None, full=True):
        """Print a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print ' * (txt='+str(txt)+')'
        print ' * stations: '+str(self.stations())
        print ' * polrep: '+str(self._polrep)+' '+str(self._pols)
        print ' * Station Jones matrices: '
        for s in self.stations():
            print '  - '+str(s)+': '+str(self.matrix()(s))
        print ' * Elements of the first Jones matrix:'
        node = self.matrix()(self.stations()[0])
        ii = ['11','12','21','22']
        for i in range(len(node.children)):
            c = node.children[i]
            if full:
                key = self.parmgroups()[0]
                self._parmgroup[key].display_subtree(c[1], txt=ii[i])
            else:
                print '  - '+str(c[1])
        print ' * Available ParmGroup objects: '
        for key in self.parmgroups():
            print '  - '+str(self._parmgroup[key].oneliner())
            if full and not self._parmgroup[key]._composite:
                self._parmgroup[key].display_node (index=0)
        print '**\n'
        return True

    #-------------------------------------------------------------------

    def define_parmgroup(self, name, descr=None,
                         default=0.0, tags=[],
                         Tsec=[1000.0,0.1], scale=None, stddev=0.1,
                         pg=None):
        """Helper function to define a named ParmGroup object"""

        # The ParmGroup objects use a subscope:
        subscope = self._ns
        node_groups = ['Parm']
        node_groups.extend(self._scope)

        # Make sure that the group name is in the list of node tags:
        if not isinstance(tags,(list,tuple)): tags = [tags]
        if not name in tags: tags.append(name)
            
        # OK, define the ParmGroup:
        self._parmgroup[name] = ParmGroup (self._ns, name=name, scope=self._scope,
                                           descr=descr, default=default,
                                           tags=tags, node_groups=node_groups,
                                           simulate=self._simulate, Tsec=Tsec,
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
        name = self.name()+jones.name()
        # NB: Check whether both have the same scope...?
        scope = self.scope()
        for s in self._stations:
            self._ns[name](*scope)(s) << Meq.MatrixMultiply(self._matrix(s),
                                                            jones._matrix(s))
        # Update the Jones object attributes:
        self._matrix = self._ns[name]
        self._name = name
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

    def __init__(self, ns, scope=None, name='GJones',
                 stations=None, simulate=False):
        Jones.__init__(self, ns, scope=scope, name=name,
                       stations=stations, simulate=simulate)
        pols = self._pols
        scope = self._scope
        jname = self._name
        # Define the various primary ParmGroups:
        for pol in pols:
            self.define_parmgroup('Gphase'+pol, descr=pol+'-dipole phases',
                                  tags=['Gphase',jname], scale=1.0)
            self.define_parmgroup('Ggain'+pol, descr=pol+'-dipole gains',
                                  tags=['Ggain',jname], default=1.0)
        # Make the Jones matrices per station:
        for s in self._stations:
            elem = dict()
            for pol in pols:
                phase = self._parmgroup['Gphase'+pol].create(s)
                gain = self._parmgroup['Ggain'+pol].create(s)
                elem[pol] = self._ns[jname+pol](*scope)(s) << Meq.Polar(gain,phase)
            self._ns[self._name](*scope)(s) << Meq.Matrix22(elem[pols[0]],0.0,
                                                            0.0,elem[pols[1]])
        self._matrix = self._ns[name](*scope)
        # Make some secondary (derived) ParmGroups:
        self.define_composite_parmgroups(jname)
        return None



#--------------------------------------------------------------------------------------------
class JJones (Jones):
    """Class that represents a set of 2x2 JJones matrices"""

    def __init__(self, ns, scope='<scope>', name='J', diagonal=False):
        Jones.__init__(self, ns, name, scope)
        mels = ['J11','J22']
        r11 = self.define_parmgroup('J11real', descr='Real part of matrix element 11')
        i11 = self.define_parmgroup('J11imag', descr='Imag part of matrix element 11')
        r22 = self.define_parmgroup('J22real', descr='Real part of matrix element 22')
        i22 = self.define_parmgroup('J22imag', descr='Imag part of matrix element 22')
        if not diagonal:
            mels = ['J11','J12','J21','J22']
            r12 = self.define_parmgroup('J12real', descr='Real part of matrix element 12')
            i12 = self.define_parmgroup('J12imag', descr='Imag part of matrix element 12')
            r21 = self.define_parmgroup('J21real', descr='Real part of matrix element 21')
            i21 = self.define_parmgroup('J21imag', descr='Imag part of matrix element 21')
        scope = self.scope()
        node_groups = ['Parm',scope]
        for s in self._stations:
            elem = dict(J11=0.0, J12=0.0, J21=0.0, J22=0.0)
            for mel in mels:
                pname = mel+'real'
                v = 0.0
                if mel in ['11','22']: v = 1.0
                real = self._ns[pname](s) << Meq.Parm(v, node_groups=node_groups,
                                                             tags=[pname,mel,'JJones'])
                self._parmgroup[pname].append(real)
                pname = mel+'imag'
                imag = self._ns[pname](s) << Meq.Parm(0.0, node_groups=node_groups,
                                                             tags=[pname,mel,'JJones'])
                self._parmgroup[pname].append(imag)
                elem[mel] = self._ns[mel](s) << Meq.ToComplex(real,imag)
            self._ns[self._name](s) << Meq.Matrix22(elem['J11'],elem['J12'],
                                                           elem['J21'],elem['J22'])
        self._matrix = self._ns[name]
        # Make some derived parmgroups:
        # self.define_parmgroup('JJones', descr='all JJones parameters', pg='*')
        # self.define_parmgroup('Jdiag', descr='diagonal elements (11,22)', pg=[r11,i11,r22,i22])
        return None

#--------------------------------------------------------------------------------------------

class DJones (Jones):
    """Class that represents a set of 2x2 WSRT DJones matrices"""

    def __init__(self, ns, scope='<scope>', name='D'):
        Jones.__init__(self, ns, name, scope)
        self.define_parmgroup('Dell', descr='dipole ellipticity')
        self.define_parmgroup('Dang', descr='dipole angle error')
        name = self.name()
        scope = self.scope()
        node_groups = ['Parm',scope]
        for s in self._stations:
            dell = self._ns.Dell(s) << Meq.Parm(0.0, node_groups=node_groups,
                                                       tags=['Dell','DJones'])
            self._parmgroup['Dell'].append(dell)
            dang = self._ns.Dang(s) << Meq.Parm(0.0, node_groups=node_groups,
                                                       tags=['Dang','DJones'])
            self._parmgroup['Dang'].append(dang)
            self._ns[name](s) << Meq.ToComplex(dang,dell)
        self._matrix = self._ns[name]
        return None

     
#===============================================================

#===============================================================

if __name__ == '__main__':
    ns = NodeScope()
    Gjones = GJones(ns, scope=['3c84','xxx'], simulate=True)
    Gjones.display()

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

    if 0:
        Jjones = JJones(ns)
        Jjones.display()
        Gjones.multiply(Jjones)
        Gjones.display()

    if 0:
        Djones = DJones(ns)
        Djones.display()
        Gjones.multiply(Djones)
        Gjones.display()

#===============================================================
    
