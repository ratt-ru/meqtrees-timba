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

#==========================================================================

from Timba.TDL import *
from Timba.Meq import meq

from Qualifiers import *

from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect

from copy import deepcopy
import random
import math

#==========================================================================

class ParmGroup (object):
    """Class that represents a group of MeqParm nodes"""

    def __init__(self, ns, label='<pg>', quals=[], descr=None, 
                 default=0.0, scale=1.0, node_groups=[], tags=[],
                 simulate=False, stddev=0.1, Tsec=1000.0, Tstddev=0.1, 
                 pg=None):
        self._ns = ns                         # node-scope (required)
        self._label = label                   # label of the parameter group 
        self._descr = descr                   # brief description 
        self._nodelist = []                   # initialise the internal nodelist

        # Information needed to create MeqParm nodes (see create_entry())
        self._default = default               # default value

        # Node-name qualifiers:
        self._quals = Qualifiers(quals, prepend=label)

        # Node tags (for searching the nodescope)
        self._tags = deepcopy(tags)
        if not isinstance(self._tags,(list,tuple)):
            self._tags = [self._tags]

        self._node_groups = deepcopy(node_groups)
        if not isinstance(self._node_groups,(list,tuple)):
            self._node_groups = [self._node_groups]
        if not 'Parm' in self._node_groups:
            self._node_groups.append('Parm')

        if simulate:
            self._tags.append('simul')        # ....??
            self._quals.append('simul')

        # Information to create a simulation subtree (see create_entry())
        self._simulate = simulate
        self._scale = scale                   # the scale of the MeqParm value
        if not self._scale:                   # if not specified (or zero):
            self._scale = abs(self._default)  #   use the (non-zero!) default value
            if self._scale==0.0: self._scale = 1.0
        self._stddev = stddev                 # relative to scale, but w.r.t. default 
        self._Tsec = Tsec                     # period of cosinusoidal variation(time) 
        self._Tstddev = Tstddev               # variation of the period

        # Plotting:
        self._dcoll = None
        self._color = 'green'
        self._style = 'diamond'

        # Optional: If a (list of) ParmGroup objects (pg) is specified:
        self._make_composite(pg) 
        return None

    #....................................................................

    def _make_composite (self, pg): 
        """Helper function: If a (list of) ParmGroup objects is
        specified (pg), make a composite ParmGroup from them."""
        self._composite = False
        if pg:
            if not isinstance(pg, (list,tuple)): pg = [pg]
            self._composite = []
            for g in pg:
                self._composite.append(g.label())
                self._nodelist.extend(g.nodelist())
        return True
                
    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += ' '+str(self._label)
        ss += ' (n='+str(len(self._nodelist))+')'
        ss += ' quals='+str(self._quals.get())
        if self._composite:
            ss += ' (composite of '+str(self._composite)+')'
        return ss

    def display(self, txt=None, full=False):
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
                print '  - scale: '+str(self._scale)+' -> stddev (abs) = '+str(self._scale*self._stddev)
                print '  - period Tsec = '+str(self._Tsec)+'  Tstddev ='+str(self._Tstddev)
            else:
                print ' * MeqParm definition:'
                print '  - node tags: '+str(self._tags)
                print '  - node_groups: '+str(self._node_groups)
        print ' * The internal nodelist: '
        for i in range(len(self._nodelist)):
            node = self._nodelist[i]
            if full:
                self.display_subtree(node, txt=str(i))
            else:
                print '  - '+str(node)
        if not full:
            print ' * The first node/subtree:'
            self.display_node (index=0)
            if True:
                print ' * The second node/subtree:'
                self.display_node (index=1)
        print '**\n'
        return True


    #-------------------------------------------------------------------

    def label(self):
        """Return the group label""" 
        return self._label

    def quals(self, append=None, prepend=None, exclude=None):
        """Return the nodename qualifier(s), with temporary modifications"""
        return self._quals.get(append=append, prepend=prepend, exclude=exclude)

    def descr(self):
        """Return the group description""" 
        return str(self._descr)

    def nodelist(self):
        """Return a copy of the list of (MeqParm) nodes"""
        nodelist = []
        nodelist.extend(self._nodelist)           # Do NOT modify self._nodelist!!
        return nodelist

    #-------------------------------------------------------------------

    def append_entry(self, node):
        """Append the given entry (node) to the nodelist."""
        self._composite = True                    # ......!!
        self._nodelist.append(node)
        return len(self._nodelist)


    def create_entry (self, qual=None):
        """Create an entry, i.e. MeqParm node, or a simulation subtree,
        and append it to the nodelist"""

        # If in a qualifier (qual) is specified, append it to the temporary quals list: 
        quals = self._quals.get(append=qual)
            
        if self._simulate:
            node = self._make_simulation_subtree(quals)
        else:
            node = self._ns.parm(*quals) << Meq.Parm(self._default,
                                                     node_groups=self._node_groups,
                                                     tags=self._tags)
        # Append the new node to the internal nodelist:
        self._nodelist.append(node)
        return node

    #....................................................................

    def _make_simulation_subtree(self, quals=quals):
        """Helper function to create a subtree that simulates a MeqParm node"""

        # default += ampl*cos(2pi*time/Tsec),
        # where both ampl and Tsec may vary from node to node.
        
        ampl = 0.0
        if self._stddev:                                # default variation
            stddev = self._stddev*self._scale           # NB: self._stddev is relative
            ampl = random.gauss(ampl, stddev)
            # print '-',label,index,' (',self._default,stddev,') -> ampl=',ampl
        ampl = self._ns.ampl(*quals) << Meq.Constant(ampl)
        
        Tsec = self._Tsec                               # variation period (sec)
        if self._Tstddev:
            stddev = self._Tstddev*self._Tsec           # NB: self._Tstddev is relative
            Tsec = random.gauss(self._Tsec, stddev) 
            # print '                (',self._Tsec,stddev,') -> Tsec=',Tsec
        Tsec = self._ns.Tsec(*quals) << Meq.Constant(Tsec)
        time = self._ns << Meq.Time()
        pi2 = 2*math.pi
        costime = self._ns << Meq.Cos(pi2*time/Tsec)
        variation = self._ns.variation(*quals) << Meq.Multiply(ampl,costime)

        # Finally, add the variation to the default value:
        default = self._ns.default(*quals) << Meq.Constant(self._default)
        node = self._ns.parm(*quals) << Meq.Add(default, variation, tags=self._tags)
        return node


    #-------------------------------------------------------------------

    def compare(self, other):
        """Compare with the given ParmGroup object"""
        quals = self.quals()
        name = 'absdiff'
        if not self._ns[name](*quals).initialized():
            nn1 = self.nodelist()
            nn2 = other.nodelist()
            diff = []
            absdiff = []
            for i in range(len(nn1)):
                node = self._ns << Meq.Subtract(nn1[i],nn2[i])
                diff.append(node)
                node = self._ns << Meq.Abs(node)
                absdiff.append(node)
            self._ns[name](*quals) << Meq.Add(children=absdiff)
        return self._ns[name](*quals)

    def sum(self):
        """Return the sum (node) of its nodes (used for solver constraints)"""
        quals = self.quals()
        name = 'sum'
        # name = 'sum_'+self.label()
        if not self._ns[name](*quals).initialized():
            self._ns[name](*quals) << Meq.Add(children=self._nodelist)
        return self._ns[name](*quals)

    def product(self):
        """Return the product (node) of its nodes (used for solver constraints)"""
        quals = self.quals()
        name = 'product'
        # name = 'product_'+self.label()
        if not self._ns[name](*quals).initialized():
            self._ns[name](*quals) << Meq.Multiply(children=self._nodelist)
        return self._ns[name](*quals)


    #----------------------------------------------------------------------

    def visualize (self, bookpage='ParmGroup', folder=None):
        """Visualise all the entries (MeqParms or their simulated subtrees)
        in a single real-vs-imag plot."""
        if self._dcoll:
            return self._dcoll
        # quals = self.quals()
        dcoll_quals = self._quals.concat()
        cc = self.nodelist() 
        rr = MG_JEN_dataCollect.dcoll (self._ns, cc, 
                                       scope=dcoll_quals,
                                       tag='',
                                       color=self._color,
                                       style=self._style,
                                       size=8, pen=2,
                                       type='realvsimag', errorbars=True)
        # Return the dataConcat node:
        self._dcoll = rr['dcoll']
        JEN_bookmarks.create(self._dcoll, self.label(),
                             page=bookpage, folder=folder)
        return self._dcoll



    #===================================================================
    # The following functions are just for convenience.....
    #===================================================================

    def display_node (self, index=0):
        """Helper function to dispay the specified node(s)/subtree(s)"""
        if index=='*': index = range(len(self._nodelist))
        if not isinstance(index,(list,tuple)): index=[index]
        for i in index:
            if i<len(self._nodelist):
                node = self._nodelist[i]
                self.display_subtree(node, txt=str(i))
        return True

    def display_subtree (self, node, txt=None, level=1,
                         show_initrec=True, recurse=1000):
        """Helper function to display a subtree recursively"""
        prefix = '  '
        if txt: prefix += ' ('+str(txt)+')'
        prefix += level*'..'
        s = prefix
        s += ' '+str(node.classname)+' '+str(node.name)
        if show_initrec:
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
        if recurse>0:
            for child in node.children:
                self.display_subtree (child[1], txt=txt, level=level+1,
                                      show_initrec=show_initrec, recurse=recurse-1)
        return True

    #======================================================================

    def test(self):
        """Helper function to put in some standard entries for testing"""
        self.create_entry()
        self.create_entry(5)
        self.create_entry(6)
        return True

#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    pg1 = ParmGroup(ns, 'pg1', simulate=False)
    pg1.test()
    cc.append(pg1.visualize())
    nn1 = pg1.nodelist()
    print 'nn1 =',nn1

    pg2 = ParmGroup(ns, 'pg2', simulate=True)
    pg2.test()
    cc.append(pg2.visualize())
    nn2 = pg2.nodelist()
    print 'nn2 =',nn2

    condeqs = []
    for i in range(len(nn1)):
        print '- i =',i
        condeqs.append(ns.condeq(i) << Meq.Condeq(nn1[i],nn2[i]))
    solver = ns.solver << Meq.Solver(children=condeqs, solvable=nn1)
    JEN_bookmarks.create(solver, page='solver')
    cc.append(solver)
        



    ns.result << Meq.Composer(children=cc)
    return True

#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       


#===============================================================
# Test routine:
#===============================================================

if __name__ == '__main__':
    ns = NodeScope()
    pg1 = ParmGroup(ns, 'pg1', simulate=False)
    pg1.test()
    pg1.display()

    if 1:
        pg2 = ParmGroup(ns, 'pg1', simulate=True)
        pg2.test()
        pg2.display()

    if 0:
        dcoll = pg1.visualize()
        pg1.display_subtree (dcoll, txt='dcoll')

    if 0:
        node = pg1.sum()
        node = pg1.product()
        pg1.display_subtree (node, txt='test')

    if 0:
        pg2 = ParmGroup(ns, 'pg2')
        pg2.append_entry(ss << 1.0)
        pg2.append_entry(ss << 2.0)
        nn = pg2.nodelist(trace=True)
        pg2.display()
        if 1:
            pg12 = ParmGroup(ns, 'pg12', pg=[pg1,pg2], descr='combination')
            pg12.display()

#===============================================================
    
