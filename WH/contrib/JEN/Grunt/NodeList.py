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

    def __init__(self, ns, name, nodes=[], labels=None):

        # The name of this group of nodes:
        self._name = str(name)
        
        self._nodes = []
        self._labels = []
        self.append(nodes, labels)

        # Scopify ns, if necessary:
        self._ns0 = ns
        if is_node(ns):
            self._ns = ns.QualScope(self._name)
        else:
            self._ns = ns(self._name)


        return None


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
        print '**\n'
        return True


    #===============================================================
    # Math operations on the nodes:
    #===============================================================

    def unop(self, unop, replace=False):
        """Apply one or more unary operations (e.g. Cos()) to all nodes.
        If replace==True, replace the nodes with the new ones.
        Otherwise, return a NodeList with the new nodes."""

        if isinstance(unop, str): unop = [unop]
        unop.reverse()
        nodes = deepcopy(self._nodes)
        labels = deepcopy(self._labels)
        name = self._name
        for unop1 in unop:
            name = unop1+'('+name+')'
            for k,node in enumerate(nodes):
                nodes[k] = self._ns << getattr(Meq,unop1)(node)
                labels[k] = '('+labels[k]+')'
                if replace:
                    self._name = name
                    self._nodes[k] = nodes[k]
                    self._labels[k] = labels[k]
        if not replace:
            return NodeList(self._ns0, name, nodes=nodes, labels=labels)
        return True
        

    #===============================================================
    # subtrees:
    #===============================================================

    def bundle (self, combine='Add', bookpage=True, show=False):
        """Bundle the nodes by applying the specified combine-operation
        (default='Add') to them. Return the root node of the resulting
        subtree. If bookpage is specified, make a bookmark."""

        nodes = self._nodes
        quals = [combine,str(len(nodes))]
        qnode = self._ns['bundle'](*quals)
        if not qnode.initialized():
            qnode << getattr(Meq,combine)(children=nodes)
        if bookpage:
            page = self._name
            if isinstance(bookpage, str): page = bookpage
            JEN_bookmarks.create(qnode, qnode.name, recurse=1, page=page)

        # Finished: Return the root-node of the bundle subtree:
        if show: display.subtree(qnode, show_initrec=False)
        return qnode


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

    if 1:
        node = nn1.bundle(show=True)
        cc.append(node)

    if 1:
        unop = 'Cos'
        unop = ['Cos','Sin']
        nn2 = nn1.unop(unop, replace=False)
        cc.append(nn2.bundle(show=True))

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
        nn1.bundle(show=True)

    if 1:
        replace = False
        unop = 'Cos'
        unop = ['Cos','Sin']
        nn2 = nn1.unop(unop, replace=replace)
        if not replace: nn2.display('unop')

    nn1.display('final', full=True)



#===============================================================

