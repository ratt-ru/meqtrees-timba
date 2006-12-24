# file: ../Grunt/Jones.py

from Timba.TDL import *
# from Timba.Contrib.JEN.Grunt import ParmGroup
from ParmGroup import *

class Jones (object):
    """Class that represents a set of 2x2 Jones matrices"""

    def __init__(self, ns, name='jones', scope=None, stations=range(1,5),
                 tags=[], polrep=None):
        self._ns = ns                # node-scope (required)
        self._name = name            # name of the Jones matrix (e.g. G) 
        self._scope = scope          # scope, e.g. (peeling)source-name
        self._tags = tags            # default node tags
        self._polrep = polrep        # polarization representation (linear, circular)
        self._stations = stations    # list of (array) stations
        self._matrix = None          # the actual jones matrices
        self._ParmGroup = dict()     # available parameter group objects
        # self._elements = dict(j11=[],j12=[],j21=[],j22=[])
        return None

    def stations(self):
        """Return a list of (array) stations"""
        return self._stations

    def name(self):
        """Return the object name (e.g. G)""" 
        return self._name

    def scope(self):
        """Return the object scope (e.g. peeling source name)""" 
        return self._scope

    def tags(self):
        """Return the default node tags""" 
        return self._tags

    def matrix(self):
        """Return the 2x2 Jones matrices themselves""" 
        return self._matrix

    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += ' '+str(self._name)
        ss += ' scope='+str(self._scope)
        return ss

    def display(self, txt=None):
        """Return a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print '** (txt='+str(txt)+')'
        print '** stations: '+str(self.stations())
        print '** default node tags: '+str(self.tags())
        print '** 2x2 Jones matrices: '
        for s in self.stations():
            print '  - '+str(s)+': '+str(self.matrix()(s))
        print '** available ParmGroup objects: '
        for key in self.ParmGroups():
            print '  - '+str(key)+': '+str(self._ParmGroup[key].oneliner())
        print ' '
        return True

    #-------------------------------------------------------------------
    
    def define_ParmGroup(self, name, descr=None):
        """Define a parameter-group (can be solved for)""" 
        tags = [self._name,self._scope,name]
        self._ParmGroup[name] = ParmGroup (name, tags=tags, descr=descr)
        return True

    def ParmGroups(self):
        """Return the available parmgroup names""" 
        return self._ParmGroup.keys()
    
    def ParmGroup(self, key=None):
        """Return the specified parmgroup (object)""" 
        return self._ParmGroup[key]

    #-------------------------------------------------------------------

    def multiply(self, jones):
        """Multiply with the given Jones object"""
        name = self.name()+jones.name()
        # NB: Check whether both have the same scope...?
        scope = self.scope()
        for s in self._stations:
            self._ns[name](scope)(s) << Meq.MatrixMultiply(self._matrix(s),
                                                           jones._matrix(s))
        # Update the Jones object attributes:
        self._matrix = self._ns[name](scope)
        self._name = name
        self._ParmGroup.update(jones._ParmGroup)
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

    def __init__(self, ns, name=None, scope='<scope>'):
        if not name: name = 'G'
        Jones.__init__(self, ns, name, scope, tags=['GJones'])
        self.define_ParmGroup('Gphase', descr='uvp phases')
        self.define_ParmGroup('Ggain', descr='uvp gains')
        node_groups = ['Parm',scope]
        name = self.name()
        scope = self.scope()
        for s in self._stations:
            phase = self._ns.Gphase(scope)(s) << Meq.Parm(0.0, node_groups=node_groups,
                                                          tags=['Gphase','GJones']);
            self._ParmGroup['Gphase'].append(phase)
            gain = self._ns.Ggain(scope)(s) << Meq.Parm(1.0, node_groups=node_groups,
                                                        tags=['Ggain','GJones']);
            self._ParmGroup['Ggain'].append(gain)
            self._ns[name](scope)(s) << Meq.Polar(gain,phase);
        self._matrix = self._ns[name](scope)
        return None

class DJones (Jones):
    """Class that represents a set of 2x2 WSRT DJones matrices"""

    def __init__(self, ns, name=None, scope='<scope>'):
        if not name: name = 'D'
        Jones.__init__(self, ns, name, scope, tags=['DJones'])
        self.define_ParmGroup('Dell', descr='dipole ellipticity')
        self.define_ParmGroup('Dang', descr='dipole angle error')
        node_groups = ['Parm',scope]
        name = self.name()
        scope = self.scope()
        for s in self._stations:
            dell = self._ns.Dell(scope)(s) << Meq.Parm(0.0, node_groups=node_groups,
                                                       tags=['Dell','DJones']);
            self._ParmGroup['Dell'].append(dell)
            dang = self._ns.Dang(scope)(s) << Meq.Parm(0.0, node_groups=node_groups,
                                                       tags=['Dang','DJones']);
            self._ParmGroup['Dang'].append(dang)
            self._ns[name](scope)(s) << Meq.ToComplex(dang,dell)
        self._matrix = self._ns[name](scope)
        return None

     
#===============================================================

#===============================================================

if __name__ == '__main__':
    ns = NodeScope()
    jones = Jones(ns, 'test')
    print jones.oneliner()
    Gjones = GJones(ns)
    print Gjones.oneliner()
    print Gjones.display()
    Djones = DJones(ns)
    print Djones.display()
    Gjones.multiply(Djones)
    print Gjones.display()
    for key in Gjones.ParmGroups():
        print '-',key,':',Gjones.ParmGroup(key).oneliner()

#===============================================================
    
