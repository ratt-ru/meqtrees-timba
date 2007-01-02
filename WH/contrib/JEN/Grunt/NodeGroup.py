# file: ../Grunt/NodeGroup.py

# History:
# - 02jan2007: creation (from ParmGroup)

# Description:

# The NodeGroup class encapsulates a named group of nodes,
# that have some kind of ralation to each other.
# A specialisation is the ParmGroup object, which contains a
# group of MeqParm nodes, e.g. for a Jones matrix.
# The nodes may be plotted together, with the same symbol and color.

# The NodeGog class encapsulates a named group of NodeGroup objects.

#==========================================================================

from Timba.TDL import *
from Timba.Meq import meq

from Qualifiers import *

from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect

from copy import deepcopy

#==========================================================================

class NodeGroup (object):
    """Class that represents a group of (somehow related) nodes"""

    def __init__(self, ns, label='<ng>', nodelist=[],
                 color='green', style='diamond', size=8, pen=2,
                 quals=[], descr=None, tags=[], rider=dict()):
        self._ns = ns                         # node-scope (required)
        self._label = label                   # label of the parameter group 
        self._descr = descr                   # brief description 

        self._nodelist = []                   # initialise the internal nodelist
        if len(nodelist)>0:
            for node in nodelist:
                self.append_entry(node)

        # A NodeGroup carries a rider (dict), which contains user-defined info:
        self._rider = dict()
        if isinstance(rider, dict): self._rider = rider

        # Node-name qualifiers:
        self._quals = Qualifiers(quals, prepend=label)

        # Node tags (for searching the nodescope)
        self._tags = deepcopy(tags)
        if not isinstance(self._tags,(list,tuple)):
            self._tags = [self._tags]

        # Plotting:
        self._dcoll = None
        self._plot = dict(color=color, style=style, size=size, pen=pen)

        return None
                
    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += ' '+str(self.label())
        ss += ' (n='+str(self.len())+')'
        ss += ' quals='+str(self._quals.get())
        return ss

    def display(self, txt=None, full=False):
        """Print a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print ' * (txt='+str(txt)+')'
        print ' * descr: '+self.descr()
        print ' * plot: '+str(self._plot)
        print ' * node tags: '+str(self._tags)
        print ' * rider ('+str(len(self.rider()))+'):'
        for key in self._rider.keys():
            print '  - '+key+': '+str(self._rider[key])
        print ' * nodelist: '
        for i in range(self.len()):
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
        """Return the label (name) of this NodeGroup""" 
        return self._label

    def quals(self, append=None, prepend=None, exclude=None):
        """Return the nodename qualifier(s), with temporary modifications"""
        return self._quals.get(append=append, prepend=prepend, exclude=exclude)

    def descr(self):
        """Return the group description""" 
        return str(self._descr)

    def rider(self, key=None):
        """Return (a field of) the rider (dict), with user-defined info""" 
        if key==None: return self._rider
        if self._rider.has_key(key):
            return self._rider[key]
        print '\n** NodeGroup.rider(',key,'): key not recognised in:',self._rider.keys(),'\n' 
        return None

    def len(self):
        """Return the length of the nodelist"""
        return len(self._nodelist)

    def nodelist(self):
        """Return a copy of the list of (MeqParm or other) nodes"""
        nodelist = []
        nodelist.extend(self._nodelist)           # Do NOT modify self._nodelist!!
        return nodelist

    #-------------------------------------------------------------------

    def append_entry(self, node):
        """Append the given entry (node) to the internal nodelist."""
        # Check whether it is a valid node....?
        self._nodelist.append(node)
        return len(self._nodelist)

    def create_entry (self, qual=None):
        """Virtual method for creating a new entry. The NodeGroup does not have
        enough information to do this, but specilisations of this class do."""
        return None

    #-------------------------------------------------------------------

    def compare(self, other):
        """Compare its nodes with the corresponding nodes of another NodeGroup object,
        for instance simulated and the actual values. It is assumed that the two sets
        of nodes have the same order."""
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
        if not self._ns[name](*quals).initialized():
            self._ns[name](*quals) << Meq.Add(children=self._nodelist)
        return self._ns[name](*quals)

    def product(self):
        """Return the product (node) of its nodes (used for solver constraints)"""
        quals = self.quals()
        name = 'product'
        if not self._ns[name](*quals).initialized():
            self._ns[name](*quals) << Meq.Multiply(children=self._nodelist)
        return self._ns[name](*quals)


    #----------------------------------------------------------------------

    def visualize (self, bookpage='NodeGroup', folder=None):
        """Visualise all the entries (MeqParms or their simulated subtrees)
        in a single real-vs-imag plot."""
        if not self._dcoll:
            dcoll_quals = self._quals.concat()
            cc = self.nodelist() 
            rr = MG_JEN_dataCollect.dcoll (self._ns, cc, 
                                           scope=dcoll_quals,
                                           tag='',
                                           color=self._plot['color'],
                                           style=self._plot['style'],
                                           size=self._plot['size'],
                                           pen=self._plot['pen'],
                                           type='realvsimag', errorbars=True)
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

    def test(self, n=4):
        """Helper function to put in some standard entries for testing"""
        for i in range(n):
            self.append_entry(self._ns.entry(i) << Meq.Constant(i))
        return True




#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    ng1 = NodeGroup(ns, 'ng1')
    ng1.test()
    cc.append(ng1.visualize())
    nn1 = ng1.nodelist()
    print 'nn1 =',nn1

    ng2 = NodeGroup(ns, 'ng2', color='red')
    ng2.test()
    cc.append(ng2.visualize())
    nn2 = ng2.nodelist()
    print 'nn2 =',nn2

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
    ng1 = NodeGroup(ns, 'ng1')
    ng1.test()
    ng1.display()

    if 0:
        cc = []
        cc = [ns << 45]
        ng2 = NodeGroup(ns, 'ng2', nodelist=cc, color='red')
        # ng2.test(6)
        ng2.display()

    if 1:
        dcoll = ng1.visualize()
        ng1.display_subtree (dcoll, txt='dcoll')

    if 0:
        node = ng1.sum()
        node = ng1.product()
        ng1.display_subtree (node, txt='test')

    if 0:
        ng2 = NodeGroup(ns, 'ng2')
        ng2.append_entry(ss << 1.0)
        ng2.append_entry(ss << 2.0)
        nn = ng2.nodelist(trace=True)
        ng2.display()
        if 1:
            ng12 = NodeGroup(ns, 'ng12', ng=[ng1,ng2], descr='combination')
            ng12.display()

#===============================================================
    
