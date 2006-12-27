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

class ParmGroup (object):
    """Class that represents a group of MeqParm nodes"""

    def __init__(self, ns, name='<pg>', descr=None, 
                 default=0.0, scale=None, node_groups=[], tags=[],
                 simulate=False, Tsec=[1000.0,0.1], stddev=0.1,
                 pg=None):
        self._ns = ns                   # node-scope (required)
        self._name = name               # name of the parameter group 
        self._descr = descr             # brief description 
        self._nodelist = []             # initialise the internal nodelist

        # Information needed to create MeqParm nodes (see create())
        if not isinstance(tags,(list,tuple)):
            tags = [tags]
        if simulate:
            tags.append('simul')
        self._tags = tags
        self._default = default
        if not isinstance(node_groups,(list,tuple)):
            node_groups = [node_groups]
        if not 'Parm' in node_groups:
            node_groups.append('Parm')
        self._node_groups = node_groups

        # Information to create a simulation subtree (see create())
        self._simulate = simulate
        self._Tsec = Tsec
        self._stddev = stddev
        if scale==None:
            scale = abs(self._default)
            if scale==0.0: scale = 1.0
        self._scale = scale

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
        if self._composite:
            ss += ' '+str(self._composite)
        elif self._simulate:
            ss += ' (simulate)'
        return ss

    def display(self, txt=None, full=True):
        """Return a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print ' * (txt='+str(txt)+')'
        print ' * descr: '+self.descr()
        if self._composite:
            print ' * composite: '+str(self._composite)
        else:
            if self._simulate:
                print ' * simulation mode: '
                print '  - period Tsec (mean,stddev) = '+str(self._Tsec)
                print '  - sttdev (w.r.t. default) = '+str(self._stddev)
            else:
                print ' * MeqParm definition:'
                print '  - node tags: '+str(self._tags)
                print '  - node_groups: '+str(self._node_groups)
        print ' * its nodelist: '
        for node in self._nodelist:
            if full:
                self.display_subtree(node)
            else:
                print '  - '+str(node)
        if not full:
            print ' * the first node/subtree:'
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
                self.display_subtree(node)
        return True

    def display_subtree (self, node, level=1):
        """Helper function to display a subtree recursively"""
        prefix = '    '+level*'..'
        initrec = deepcopy(node.initrec())
        if len(initrec.keys()) > 1:
            hide = ['name','class','defined_at','children','stepchildren','step_children']
            for field in hide:
                if initrec.has_key(field): initrec.__delitem__(field)
                if initrec.has_key('default_funklet'):
                    coeff = initrec.default_funklet.coeff
                    initrec.default_funklet.coeff = [coeff.shape,coeff.flat]
        print prefix+' '+str(node.classname)+' '+str(node.name)+' '+str(initrec)
        for child in node.children:
            self.display_subtree (child[1], level=level+1)
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

        if self._simulate:
            # Simulation mode:
            value = self._default
            if self._stddev:
                stddev = self._stddev*self._scale      # self._stddev is relative
                value = random.gauss(self._default, stddev)
                print '-',name,index,' (',self._default,stddev,') ->',value
            node = self._ns[name](index)('simul') << Meq.Constant(value,
                                                                  tags=self._tags) 

        else:
            # Normal mode:
            # print 'name=',name,index,self._ns
            node = self._ns[name](index) << Meq.Parm(self._default,
                                                     node_groups=self._node_groups,
                                                     tags=self._tags)
            
        # Append the new node to the internal nodelist:
        self._nodelist.append(node)
        return node


    #-------------------------------------------------------------------

    def compare(self, pg):
        """Compare with the given ParmGroup object"""
        return True



#===============================================================

if __name__ == '__main__':
    ns = NodeScope()
    ss = ns.Subscope('subscope')
    pg1 = ParmGroup(ss, 'pg1')
    nn = pg1.nodelist(trace=True)
    pg1.display()

    if 1:
        pg1.create(5)
        pg1.create(6)
        pg1.display()

    if 1:
        pg2 = ParmGroup(ss, 'pg2')
        pg2.append(ss << 1.0)
        pg2.append(ss << 2.0)
        nn = pg2.nodelist(trace=True)
        pg2.display()
        if 1:
            pg12 = ParmGroup(ss, 'pg12', pg=[pg1,pg2], descr='combination')
            pg12.display()

#===============================================================
    
