# file: ../Grunt/NodeList.py

# History:
# - 31may2007: creation 

# Description:

# The Grunt NodeList class encapsulate an arbitrary list of nodes.
# Usually, these will be groups of nodes that are related for some
# reason, e.g. a group of simular M.E. parameters for different stations,
# or the group of Condeq nodes fed to a solver.

# The NodeList class has a number of methods for operating on the list
# as a whole, e.g. various ways of visualisation, applying unary operations
# applying binary math operations with another (commensurate) NodeList, etc.

# This class should take take of most of the combersome routine operations
# that tend to clutter up trees.


#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

import Meow

from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect
from Timba.Contrib.JEN.Grunt import display
# from Timba.Contrib.JEN.Expression import Expression

from copy import deepcopy

#======================================================================================

class NodeList (object):
    """The Grunt NodeList class encapsulates an arbitrary list of nodes"""

    def __init__(self, ns, name, nodes=[], labels=None, **opt):

        # The name of this group of nodes:
        self._name = str(name)
        
        self._nodes = []
        self._labels = []
        self.append(nodes, labels)

        # Scopify ns, if necessary:
        if is_node(ns):
            self._ns = ns.QualScope(self._name)
            self._ns0 = ns.QualScope()
        else:
            self._ns = ns(self._name)
            self._ns0 = ns

        # Miscellaneous options:
        self._opt = opt
        if not isinstance(opt, dict): opt = dict()
        opt.setdefault('color','red')
        opt.setdefault('style','circle')
        return None


    #===============================================================
    # Basic access functions:
    #===============================================================

    def len (self):
        """Return the name of the object"""
        return len(self._nodes)

    def name (self):
        """Return the length of the list of nodes"""
        return self._name

    def append(self, node, label=None):
        """Append one or more nodes to the list. Optionally provide label(s)""" 
        if not isinstance(node,(list,tuple)): node = [node]
        node = list(node)
        k = self.len()
        for i,nd in enumerate(node): 
            self._nodes.append(nd)
            k += 1
            if label==None:      # Give automatic node label, e.g. for plotting
                self._labels.append(self._name+'_'+str(k))
            elif isinstance(label,(list,tuple)):
                self._labels.append(str(label[i]))   # assume (node,label) equal length
            else:              
                self._labels.append(str(label))      # assume len(node)==1...
        return True

    def __getitem__(self, index):
        """Get the speciified (index) item from the NodeList"""
        if not isinstance(index, int):
            raise TypeError,' index not an int'
        elif index<0 or index>=self.len():
            raise TypeError,' index out of range'
        else:
            return self._nodes[index]
            

    #===============================================================
    # Some local helper functions:
    #===============================================================

    def copy (self):
        """Make a copy of this object"""
        new = NodeList(self._ns0, self._name)
        new._nodes = deepcopy(self._nodes)
        new._labels = deepcopy(self._labels)
        new._opt = deepcopy(self._opt)
        return new

    def _dispose(self, copy, replace=False):
        """Dispose of the (modified) copy of itself."""
        if replace:
            self._nodes = deepcopy(copy._nodes)
            self._labels = deepcopy(copy._labels)
            self._opt = deepcopy(copy._opt)
            return True
        copy._ns = copy._ns0(copy._name)
        return copy

    def _is_commensurate(self, other, severe=True):
        """Check whether the other Nodelist is commensurate with self.
        If severe==True, raise an error if not commensurate."""
        if other.len()==self.len(): return True
        if severe:
            s = '** NodeLists not commensurate'
            raise ValueError,s
        return False
        

    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = 'Grunt.NodeList:'
        ss += ' '+str(self._name)
        ss += '  (len='+str(self.len())+')'
        return ss


    def display(self, txt=None, full=False, recurse=3):
        """Print a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print '  * (txt='+str(txt)+')'
        #...............................................................
        print '  * Nodes ('+str(len(self._nodes))+'):'
        for k,node in enumerate(self._nodes):
            print '   - ('+self._labels[k]+'): '+str(node)
        print '  * opt: '+str(self._opt)
        print '**\n'
        return True


    #===============================================================
    # Math operations on the nodes:
    #===============================================================

    def unop(self, unop, replace=False):
        """Apply one or more unary operations (e.g. Cos()) to all nodes.
        NB: The ops are applied from right to left, i.e. like a math expr.
        If replace==True, replace the nodes with the new ones.
        Otherwise, return a new NodeList with the new nodes."""

        if isinstance(unop, str): unop = unop.split(' ')
        unop = list(unop)
        unop.reverse()
        copy = self.copy()
        for unop1 in unop:
            copy._name = unop1+'('+copy._name+')'
            for k,node in enumerate(copy._nodes):
                copy._nodes[k] = self._ns << getattr(Meq,unop1)(node)
                copy._labels[k] = '('+copy._labels[k]+')'
        return self._dispose(copy, replace)

    #---------------------------------------------------------------

    def binop(self, binop, other, replace=False):
        """Apply the specified binary operations (e.g. '+') on 
        a node-by-node basis between itself and another NodeList.
        If replace==True, replace the nodes with the new ones.
        Otherwise, return a new NodeList with the new nodes."""

        binopin = binop
        if binop=='+': binop = 'Add'
        if binop=='-': binop = 'Subtract'
        if binop=='*': binop = 'Multiply'
        if binop=='/': binop = 'Divide'
        if binop=='^': binop = 'Pow'
        if binop=='%': binop = 'Mod'
        copy = self.copy()
        copy._name = '('+copy._name+'_'+binopin+'_'+other._name+')'
        for k,lhs in enumerate(copy._nodes):
            rhs = other._nodes[k]
            copy._nodes[k] = self._ns << getattr(Meq,binop)(lhs, rhs)
            copy._labels[k] = '('+copy._labels[k]+'_'+binopin+'_'+other._labels[k]+')'
        return self._dispose(copy, replace)
        

    #===============================================================
    # subtrees:
    #===============================================================

    def bundle (self, combine='Add', unop=None, bookpage=True, show=False):
        """Bundle the nodes by applying the specified combine-operation
        (default='Add') to them.
        If unary operation(s) specified, apply it/them first.
        Return the root node of the resulting subtree.
        If bookpage is specified, make a bookmark."""

        nodes = self._nodes
        quals = [combine,str(self.len())]
        if unop: quals.insert(0,unop)      
        qnode = self._ns['bundle'](*quals)
        if not qnode.initialized():
            if unop:
                nodes = self.unop(unop)._nodes
            qnode << getattr(Meq,combine)(children=nodes)
        if bookpage:
            page = self._name
            if isinstance(bookpage, str): page = bookpage
            JEN_bookmarks.create(qnode, qnode.name, recurse=1, page=page)

        # Finished: Return the root-node of the bundle subtree:
        if show: display.subtree(qnode, show_initrec=False)
        return qnode

    #---------------------------------------------------------------

    def max (self, unop=None, bookpage=True, show=False):
        """Return a node that returns the maximum cell value of the list nodes"""
        return self.bundle('Max', unop=unop, bookpage=bookpage, show=show)

    def maxabs (self, bookpage=True, show=False):
        """Return a node that returns the maximum cell value of the list nodes"""
        return self.bundle('Max', unop='Abs', bookpage=bookpage, show=show)

    def min (self, unop=None, bookpage=True, show=False):
        """Return a node that returns the minimum cell value of the list nodes"""
        return self.bundle('Min', unop=unop, bookpage=bookpage, show=show)


    #===============================================================
    # Visualization:
    #===============================================================

    def inspector (self, parmgroup='*'):
        """Visualize the nodes in the specified parmgroup(s) in a separate
        'inspector' per parmgroup. Return the root node of the resulting subtree.
        Make bookpages for each parmgroup."""

        pg = self.check_parmgroups (parmgroup, severe=True)
        bb = []
        for key in pg:
            quals = [key]
            qnode = self._ns['inspector'](*quals)
            if not qnode.initialized():
                nodes = self._parmgroups[key]['nodes']
                labels = self._parmgroups[key]['plot_labels']
                qnode << Meq.Composer(children=nodes,
                                      plot_label=labels)
            bb.append(qnode)
            JEN_bookmarks.create(qnode, key, page='inspector_'+self.name,
                                 viewer='Collections Plotter')

        # Make a subtree of inspectors, and return the root node:
        if len(bb)==0:
            return None
        elif len(bb)==1:
            qnode = bb[0]
        else:
            qnode = self._ns['inspector'](parmgroup)
            if not qnode.initialized():
                qnode << Meq.Composer(children=bb)
        return qnode

    #---------------------------------------------------------------

    def compare (self, parmgroup, with, trace=False):
        """Compare the nodes of a parmgroup with the corresponding ones
        of the given parmgroup (with)."""

        self.has_group (parmgroup, severe=True)
        # .... unfinished ....
        
        return True












#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================



def _define_forest(ns):

    # cc = [ns.dummy<<45]
    cc = []

    nn1 = NodeList(ns, 'nn1')
    nn1.display('initial')
    if 1:
        for k in range(4):
            nn1.append(ns << k)
    nn1.display('initial')

    if 0:
        unop = None
        unop = 'Cos Sin'
        node = nn1.bundle(unop=unop, show=True)
        cc.append(node)

    if 1:
        unop = 'Cos'
        unop = ['Cos','Sin']
        unop = 'Cos Sin'
        nn2 = nn1.unop(unop, replace=False)
        cc.append(nn2.bundle(show=True))
        if 1:
            nn3 = nn1.unop(unop, replace=False)
            cc.append(nn3.bundle(show=True))

    if 0:
        node = nn1.inspector()
        cc.append(node)

    nn1.display('final', full=True)

    ns.result << Meq.Composer(children=cc)
    return True



#---------------------------------------------------------------

def _tdl_job_2D_tf (mqs, parent):
    """Execute the forest with a 2D request (freq,time), starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,0,2000)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=100)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       










#===============================================================
# Test routine:
#===============================================================

if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        nn1 = NodeList(ns, 'nn1')
        nn1.display('initial')
    if 1:
        for k in range(4):
            nn1.append(ns << k)

    if 0:
        nn1.append('node')
        nn1.append(14, 'label')
        nn1.append(range(2))

    if 0:
        nn2 = nn1.copy()
        nn2.append(range(2))
        nn2._opt = 'new'
        nn1._opt = 'old'
        nn1.append(140, 'labell')
        nn2.display('copy')

    if 0:
        for index in range(5):
            print index, nn1[index] 

    if 0:
        unop = None
        unop = 'Cos'
        unop = 'Cos Sin'
        unop = ['Cos','Sin']
        print nn1.bundle(unop=unop, show=True)

    if 0:
        replace = False
        unop = 'Cos'
        # unop = ['Cos','Sin']
        unop = 'Cos Sin'
        nn2 = nn1.unop(unop, replace=replace)
        if not replace: nn2.display('unop')

    if 0:
        print nn1.maxabs(show=True)

    if 1:
        nn2 = nn1.copy()
        nn3 = nn1.binop('*', nn2)
        nn3.display('binop')

    nn1.display('final', full=True)



#===============================================================

