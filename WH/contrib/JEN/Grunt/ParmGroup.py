# file: ../Grunt/ParmGroup.py

# History:
# - 25dec2006: creation

# Description:

# The ParmGroup class encapsulates a named group of MeqParm nodes,
# or subtrees that generate simulated values for MeqParm nodes.
# ParmGroups are created in modules that implement bits of a
# Measurement Equation that contain parameters, e.g. instrumental
# Jones matrices, or LSM source models. They may be used for
# solving or visualization. They are also useful for generating
# user interfaces that offer a choice of solvers, etc.

from Timba.TDL import *
from Timba.Contrib.JEN.util import TDL_display
from copy import deepcopy
import random
import math

class ParmGroup (object):
    """Class that represents a group of MeqParm nodes"""

    def __init__(self, ns, name='<pg>', scope=[], descr=None, 
                 default=0.0, scale=None, node_groups=[], tags=[],
                 simulate=False, stddev=0.1, Tsec=1000.0, Tstddev=0.1, 
                 pg=None):
        self._ns = ns                         # node-scope (required)
        self._name = name                     # name of the parameter group 
        self._descr = descr                   # brief description 
        self._nodelist = []                   # initialise the internal nodelist

        # Information needed to create MeqParm nodes (see create())
        self._tags = deepcopy(tags)
        if not isinstance(self._tags,(list,tuple)):
            self._tags = [self._tags]
        self._scope = deepcopy(scope)         # scope -> nodename qualifier(s)
        if not isinstance(self._scope,(list,tuple)):
            self._scope = [self._scope]
        if simulate:
            self._tags.append('simul')        # ....??
            if not 'simul' in self._scope:
                self._scope.append('simul')  
        self._default = default
        self._node_groups = deepcopy(node_groups)
        if not isinstance(self._node_groups,(list,tuple)):
            self._node_groups = [self._node_groups]
        if not 'Parm' in self._node_groups:
            self._node_groups.append('Parm')

        # Information to create a simulation subtree (see create())
        self._simulate = simulate
        self._scale = scale                   # the scale of the MeqParm value
        if self._scale==None:                 # if not specified:
            self._scale = abs(self._default)  #   use the (non-zero!) default value
            if self._scale==0.0: self._scale = 1.0
        self._stddev = stddev                 # relative to scale, but w.r.t. default 
        self._Tsec = Tsec                     # period of cosinusoidal variation(time) 
        self._Tstddev = Tstddev               # variation of the period

        # Optional: If a (list of) ParmGroup objects is specified,
        # use their contents to fill the nodelist (etc).
        # This is used to create composite ParmGroups
        self._composite = False
        if pg:
            if not isinstance(pg, (list,tuple)): pg = [pg]
            self._composite = []
            for g in pg:
                self._composite.append(g.name())
                self._nodelist.extend(g.nodelist())
        return None

    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += ' '+str(self._name)
        ss += ' (n='+str(len(self._nodelist))+')'
        ss += ' scope='+str(self._scope)
        if self._composite:
            ss += ' (composite of '+str(self._composite)+')'
        return ss

    def display(self, txt=None, full=True):
        """Print a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print ' * (txt='+str(txt)+')'
        print ' * descr: '+self.descr()
        print ' * default: '+str(self._default)
        if self._composite:
            print ' * composite: '+str(self._composite)
        else:
            if self._simulate:
                print ' * simulation mode: '
                print '  - sttdev (relative, w.r.t. default) = '+str(self._stddev)
                print '  - scale: '+str(self._scale)+' -> stddev = '+str(self._scale*self._stddev)
                print '  - period Tsec = '+str(self._Tsec)+'  Tstddev ='+str(self._Tstddev)
            else:
                print ' * MeqParm definition:'
                print '  - node tags: '+str(self._tags)
                print '  - node_groups: '+str(self._node_groups)
        print ' * Its nodelist: '
        for i in range(len(self._nodelist)):
            node = self._nodelist[i]
            if full:
                self.display_subtree(node, txt=str(i))
            else:
                print '  - '+str(node)
        if not full:
            print ' *Tthe first node/subtree:'
            self.display_node (index=0)
        print '**\n'
        return True

    #............................................................................

    def display_node (self, index=0):
        """Helper function to dispay the specified node(s)/subtree(s)"""
        if index=='*': index = range(len(self._nodelist))
        if not isinstance(index,(list,tuple)): index=[index]
        for i in index:
            if i<len(self._nodelist):
                node = self._nodelist[i]
                # TDL_display.subtree (node, txt='1st node', full=True)
                self.display_subtree(node, txt=str(i))
        return True

    def display_subtree (self, node, txt=None, level=1):
        """Helper function to display a subtree recursively"""
        prefix = '  '
        if txt: prefix += ' ('+str(txt)+')'
        prefix += level*'..'
        s = prefix
        s += ' '+str(node.classname)+' '+str(node.name)
        if True:
            initrec = deepcopy(node.initrec())
            # if len(initrec.keys()) > 1:
            hide = ['name','class','defined_at','children','stepchildren','step_children']
            for field in hide:
                if initrec.has_key(field): initrec.__delitem__(field)
                if initrec.has_key('default_funklet'):
                    coeff = initrec.default_funklet.coeff
                    initrec.default_funklet.coeff = [coeff.shape,coeff.flat]
            if len(initrec)>0: s += ' '+str(initrec)
        print s
        for child in node.children:
            self.display_subtree (child[1], txt=txt, level=level+1)
        return True

    #-------------------------------------------------------------------

    def name(self):
        """Return the group name""" 
        return self._name

    def descr(self):
        """Return the group description""" 
        return str(self._descr)

    def append(self, node):
        """Append the given node to the nodelist"""
        self._composite = True                    # ......!!
        self._nodelist.append(node)
        return len(self._nodelist)

    def nodelist(self, trace=False):
        """Return a copy of the list of (MeqParm) nodes"""
        nodelist = []
        nodelist.extend(self._nodelist)           # Do NOT modify self._nodelist!!
        if trace:
            print '\n** nodelist():'
            for node in nodelist: print '-',node
            print
        return nodelist

    #-------------------------------------------------------------------
    
    def create(self, index):
        """Create a MeqParm node, or a simulation subtree,
        and append it to the nodelist"""
        name = self._name
        scope = self._scope
        
        if self._simulate:
            node = self.simulation_subtree(index)
        else:
            node = self._ns[name](*scope)(index) << Meq.Parm(self._default,
                                                             node_groups=self._node_groups,
                                                             tags=self._tags)
        # Append the new node to the internal nodelist:
        self._nodelist.append(node)
        return node

    #....................................................................

    def simulation_subtree(self, index):
        """Create a subtree that simulates a MeqParm node"""
        name = self._name
        scope = self._scope

        # default += ampl*cos(2pi*time/Tsec),
        # where both ampl and Tsec may vary from node to node.
        ampl = 0.0
        if self._stddev:                                # default variation
            stddev = self._stddev*self._scale           # NB: self._stddev is relative
            ampl = random.gauss(ampl, stddev)
            print '-',name,index,' (',self._default,stddev,') -> ampl=',ampl
        ampl = self._ns.ampl(name)(*scope)(index) << Meq.Constant(ampl)
        
        Tsec = self._Tsec                               # variation period (sec)
        if self._Tstddev:
            stddev = self._Tstddev*self._Tsec           # NB: self._Tstddev is relative
            Tsec = random.gauss(self._Tsec, stddev) 
            print '                (',self._Tsec,stddev,') -> Tsec=',Tsec
        Tsec = self._ns.Tsec(name)(*scope)(index) << Meq.Constant(Tsec)
        time = self._ns << Meq.Time()
        pi2 = 2*math.pi
        costime = self._ns << Meq.Cos(pi2*time/Tsec)
        variation = self._ns.variation(*scope)(index) << Meq.Multiply(ampl,costime)

        default = self._ns.default(name)(*scope)(index) << Meq.Constant(self._default)
        node = self._ns[name](*scope)(index) << Meq.Add(default, variation,
                                                        tags=self._tags)
        return node


    #-------------------------------------------------------------------

    def compare(self, pg):
        """Compare with the given ParmGroup object"""
        return True



#===============================================================

if __name__ == '__main__':
    ns = NodeScope()
    pg1 = ParmGroup(ns, 'pg1', simulate=True)
    nn = pg1.nodelist(trace=True)
    pg1.display()


    if 1:
        pg1.create(5)
        pg1.create(6)
        pg1.display()

    if 0:
        pg2 = ParmGroup(ns, 'pg2')
        pg2.append(ss << 1.0)
        pg2.append(ss << 2.0)
        nn = pg2.nodelist(trace=True)
        pg2.display()
        if 1:
            pg12 = ParmGroup(ns, 'pg12', pg=[pg1,pg2], descr='combination')
            pg12.display()

#===============================================================
    
