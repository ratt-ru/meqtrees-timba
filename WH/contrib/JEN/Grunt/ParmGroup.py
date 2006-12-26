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
# from copy import deepcopy

class ParmGroup (object):
    """Class that represents a group of MeqParm nodes"""

    def __init__(self, ns, name='<pg>', descr=None, 
                 default=0.0, node_groups=[], tags=[],
                 simulate=False, Tsec=[1000.0,0.0], stddev=0.0,
                 pg=None):
        self._ns = ns                   # node-scope (required)
        self._name = name               # name of the parameter group 
        self._descr = descr             # brief description 
        self._nodelist = []             # initialise

        # Information needed to create MeqParm nodes (see create())
        self._default = default
        self._tags = tags
        if not isinstance(node_groups,(list,tuple)):
            node_groups = [node_groups]
        if not 'Parm' in node_groups:
            node_groups.append('Parm')
        self._node_groups = node_groups

        # Information to create a simulation subtree (see create())
        self._simulate = simulate
        self._Tsec = Tsec
        self._stddev = stddev

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

    def display(self, txt=None):
        """Return a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print '** (txt='+str(txt)+')'
        print '** descr: '+self.descr()
        if self._composite:
            print '** composite: '+str(self._composite)
        else:
            if self._simulate:
                print '** simulation mode: '
                print '  - period Tsec (mean,stddev) = '+str(self._Tsec)
                print '  - sttdev (w.r.t. default) = '+str(self._stddev)
            else:
                print '** MeqParm definition:'
                print '  - node tags: '+str(self._tags)
                print '  - node_groups: '+str(self._node_groups)
        print '** nodelist: '
        for node in self._nodelist:
            print '  - '+str(node)
        print ' '
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
            node = self._ns[name]('simul')(index) << Meq.Constant(self._default,
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
    
