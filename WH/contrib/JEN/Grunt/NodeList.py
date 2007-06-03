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
from numarray import array

#======================================================================================

class NodeList (object):
    """The Grunt NodeList class encapsulates an arbitrary list of nodes"""

    def __init__(self, ns, name, nodes=[], labels=None, **pp):

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

        # Miscellaneous settings:
        self._pp = pp
        if not isinstance(pp, dict): pp = dict()
        # Plotting instructions:
        pp.setdefault('color','red')
        pp.setdefault('style','circle')
        pp.setdefault('size',5)
        pp.setdefault('pen',2)
        # Tensor information:
        pp.setdefault('dims',None)
        pp.setdefault('elements',None)       # e.g. ['XX','XY','YX','YY']

        # Misc initializations:
        self._counter = dict(copy=0)
        return None


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
        #...............................................................
        print '  * settings (pp): '+str(self._pp)
        print '  * counter(s): '+str(self._counter)
        print '**\n'
        return True


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

    def copy (self, select='*'):
        """Make a copy of this object, optionally selecting nodes."""
        # Most of the NodeList operations work on copies. Among

        # Make an empty new NodeList with a unique name. This greatly reduces
        # the danger of nodename clashes, or inadvertent branch cross-overs.
        # (The only danger is with NodeList objects that have the same name,
        # e.g. generated automatically in widely separated branches of the tree...)
        
        self._counter['copy'] += 1                 # increment copy-counter
        name = '('+self._name+'|'+str(self._counter['copy'])+')'     
        new = NodeList(self._ns0, name)            # note self._ns0....!

        # Transfer the (selection of) nodes and their labels:
        ii = self._selection (select)
        for i in ii:
            new._nodes.append(self._nodes[i])
            new._labels.append(self._labels[i])
        new._pp = deepcopy(self._pp)
        return new

    #----------------------------------------------------------------

    def _dispose(self, copy, replace=False):
        """Dispose of the (modified) copy of itself."""
        if replace:
            self._nodes = deepcopy(copy._nodes)
            self._labels = deepcopy(copy._labels)
            self._pp = deepcopy(copy._pp)
            return True
        copy._ns = copy._ns0(copy._name)
        return copy

    #----------------------------------------------------------------

    def _is_commensurate(self, other, severe=True):
        """Check whether the other Nodelist is commensurate with self.
        If severe==True, raise an error if not commensurate."""
        if other.len()==self.len(): return True
        if severe:
            s = '** NodeLists not commensurate'
            raise ValueError,s
        return False

    #----------------------------------------------------------------

    def _selection (self, select='*'):
        """Return a list of valid indices for node selection.
        The following possibilities are available:
        - select='*': select all available nodes
        - select=[list]: return one or more specific (but valid) node indices.
        - select=int: specifies the size of a regular subset of the available nodes.
        """
        n = self.len()
        ii = []
        if isinstance(select,str):
            if select=='*': ii = range(n)

        elif isinstance(select,int) and select>0:
            # Select a regular subset of nreg items:
            jj = array(range(0,n,max(1,(n+1)/select)))
            jj = jj[range(min(select,n))]
            if select>1: jj[len(jj)-1] = n-1
            ii.extend(jj)

        elif isinstance(select,(list,tuple)):
            # Select specific node(s):
            for i in select:
                if i>=0 and i<n:
                    if not i in ii: ii.append(i)
        ii.sort()
        # print '** _selection(',select,' (n=',n,')) -> ',ii
        return ii

    #----------------------------------------------------------------

    def extract (self, elem=0, replace=False):
        """Extract the specified elements (elem, may be a list) from the
        (assumedly tensor) nodes in the NodeList. The elem may be integer(s),
        or element name(s). In the latter case, a list of element names must
        be supplied at NodeList creation. (e.g. , elements=['XX','XY','YX','YY'])
        If replace==True, replace the nodes with the new ones.
        Otherwise, return a new NodeList with the new nodes."""

        ii = deepcopy(elem)
        if not isinstance(ii, (list,tuple)): ii = [ii]
        ppel = self._pp['elements']
        elems = []
        for k,i in enumerate(ii):
            if isinstance(i,int):           # e.g. 1
                if isinstance(ppel,list):
                    elems.append(ppel[i])   # e.g. 'XX'
                else:
                    elems.append(str(i))
            elif isinstance(i,str):         # e.g. 'XX'
                ii[k] = ppel.index(i)       # index must be integer
                elems.append(i)

        # NB: MeqSelector only supports a single integer index....!?
        # That is why we offer a workaround by re-composing multiple ones.

        copy = self.copy()
        copy._pp['elements'] = elems 
        copy._pp['dims'] = len(elems)       # .....?
        for k,node in enumerate(copy._nodes):
            cc = []
            selems = elems[0]
            for m,i in enumerate(ii):       # extract nodes one-by-one
                name = 'selector('+copy._labels[k]+')['+str(elems[m])+']'
                node = copy._ns[name] << Meq.Selector(copy._nodes[k], index=i)
                cc.append(node)
                if m>0: selems += ','+elems[m]
            if len(cc)==1:                  # extracted one only
                copy._nodes[k] = cc[0]
            else:                           # extracted more: recompose
                name = 'selector('+copy._labels[k]+')['+selems+']'
                copy._nodes[k] = copy._ns[name] << Meq.Composer(*cc)
            copy._labels[k] = name
        return self._dispose(copy, replace)


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
                copy._nodes[k] = copy._ns << getattr(Meq,unop1)(node)
                copy._labels[k] = '('+copy._labels[k]+')'
        return self._dispose(copy, replace)

    #---------------------------------------------------------------

    def binop(self, binop, other, replace=False):
        """Apply the specified binary operations (e.g. '+') on 
        a node-by-node basis between itself and another NodeList.
        If replace==True, replace the nodes with the new ones.
        Otherwise, return a new NodeList with the new nodes."""

        self._is_commensurate(other, severe=True)
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
            copy._nodes[k] = copy._ns << getattr(Meq,binop)(lhs, rhs)
            copy._labels[k] = '('+copy._labels[k]+'_'+binopin+'_'+other._labels[k]+')'
        return self._dispose(copy, replace)
        
    #---------------------------------------------------------------

    def compare (self, other, bookpage=True, show=False):
        """Compare the nodes of a NodeList with the corresponding ones
        of another NodeList."""
        diff = self.binop('-', other)
        qnode = diff.bundle(unop='Abs', combine='Add',
                            bookpage=bookpage, recurse=None)
        if show: display.subtree(qnode, show_initrec=False)
        return qnode


    #===============================================================
    # subtrees:
    #===============================================================

    def bundle (self, combine='Add',
                bookpage=True, recurse=1,
                select='*', unop=None, show=False):
        """Bundle the (selection of) nodes by applying the specified
        combine-operation (default='Add') to them.
        If unary operation(s) specified, apply it/them first.
        Return the root node of the resulting subtree.
        If bookpage is specified, make a bookmark."""

        copy = self.copy(select=select)
        quals = [combine,str(copy.len())]
        if unop: quals.insert(0,unop)      
        qnode = copy._ns['bundle'](*quals)
        if qnode.must_define_here(self):
            nodes = copy._nodes
            if unop:
                nodes = copy.unop(unop)._nodes
            qnode << getattr(Meq,combine)(children=nodes)
        if bookpage:
            page = self._name
            if isinstance(bookpage, str): page = bookpage
            JEN_bookmarks.create(qnode, qnode.name, recurse=recurse, page=page)

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

    def inspector (self, select='*', bookpage=True):
        """Visualize the (selected) nodes with an 'inspector' (Collections Viewer).
        Return the root node of the resulting subtree. Make a bookmark, if required."""

        copy = self.copy(select=select)
        qnode = copy._ns['inspector']
        if qnode.must_define_here(self):
            qnode << Meq.Composer(children=copy._nodes,
                                  plot_label=copy._labels)
        if bookpage:
            JEN_bookmarks.create(qnode, self.name,
                                 # page='inspector_'+self.name,
                                 viewer='Collections Plotter')
        return qnode

    #--------------------------------------------------------------

    def rvsi (self, select='*', other=None, bookpage=True):
        """Visualize the (selected) nodes with a 'real-vs-imaginary' plot.
        If another (commensurate) NodeList is specified, make complex numbers with
        (real,imag) is (self,other). This misuses the rvsi plot to plot one agains
        the other....
        Return the root node of the resulting subtree. Make a bookmark, if required."""

        copy = self.copy(select=select)
        if other:
            copy = self.binop('ToComplex', other.copy(select=select)) 
        rr = MG_JEN_dataCollect.dcoll (copy._ns, copy._nodes, 
                                       scope='', tag='',
                                       color=self._pp['color'],
                                       style=self._pp['style'],
                                       size=self._pp['size'],
                                       pen=self._pp['pen'],
                                       type='realvsimag', errorbars=True)
        qnode = rr['dcoll']
        if bookpage:
            if not isinstance(bookpage, str):
                bookpage = 'rvsi_'+copy._name
            JEN_bookmarks.create(qnode, self._name,
                                 page=bookpage, folder=None)
        return qnode



    #================================================================
    # Fill the NodeList with some test-nodes:
    #================================================================

    def test(self, n=8):
        """Fill the NodeList with n test-nodes"""
        freq = self._ns << Meq.Freq()
        time = self._ns << Meq.time()
        self._pp['elements'] = ['s','c','cs','cx']             # tensor element names
        self._pp['dims'] = [2,2]                               # tensor dims....
        k = 0
        for i in range(10):
            first = True
            for j in range(1,3):
                label = 'T'+str(i)+str(j)
                qnode = self._ns[label]
                if first:
                    c = qnode('cos')(i) << Meq.Cos(i*time)
                    first = False
                s = qnode('sin')(j) << Meq.Sin(j*freq)
                cs = qnode('cs') << Meq.Multiply(c,s)
                cx = qnode('cx') << Meq.ToComplex(c,s)
                qnode << Meq.Composer(s,c,cs,cx, dims=[2,2])   # make tensor node
                self.append(qnode, label)
                k += 1
                if k>=n: break
            if k>=n: break
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
    nn1.test(3)
    nn1.display('initial')

    if 1:
        unop = None
        # unop = 'Cos Sin'
        node = nn1.bundle(select='*', unop=unop, show=True)
        cc.append(node)

    if 1:
        # nn2 = nn1.extract(elem=[2,3])
        nn2 = nn1.extract(elem=['cx','c','c'])
        nn2.display('extracted')
        node = nn2.bundle(show=True)
        cc.append(node)

    if 0:
        node = nn1.inspector()
        cc.append(node)

    if 0:
        node = nn1.rvsi(other=nn1)
        cc.append(node)

    if 0:
        node = nn1.compare(other=nn1)
        cc.append(node)

    nn1.display('final', full=True)

    ns.result << Meq.Composer(children=cc)
    return True



#---------------------------------------------------------------

def _tdl_job_2D_tf (mqs, parent):
    """Execute the forest with a 2D request (freq,time), starting at the named node"""
    domain = meq.domain(1,5,0,6)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=100, num_time=100)
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

    if 1:
        nn1 = NodeList(ns, 'nt1')
        nn1.test(8)
        nn1.display('test')

    if 0:
        for nreg in range(10):
            nn1._selection(nreg)
        nn1._selection([6])
        nn1._selection([6,9])
        nn1._selection('*')
        nn1._selection(3.4)

    if 0:
        nn2 = nn1.copy(select=[1,2])
        nn2.append(range(2))
        nn2._pp = 'new'
        nn1._pp = 'old'
        nn1.append(140, 'labell')
        nn2.display('copy')

    if 0:
        for index in range(5):
            print index, nn1[index] 

    if 1:
        unop = 'Cos'
        unop = 'Cos Sin'
        unop = ['Cos','Sin']
        unop = None
        print nn1.bundle(unop=unop, select=3, show=True)

    if 0:
        replace = False
        unop = 'Cos'
        # unop = ['Cos','Sin']
        unop = 'Cos Sin'
        nn2 = nn1.unop(unop, replace=replace)
        if not replace: nn2.display('unop')

    if 0:
        print nn1.maxabs(show=True)

    if 0:
        nn2 = nn1.copy()
        nn3 = nn1.binop('*', nn2)
        nn3.display('binop')

    nn1.display('final', full=True)



#===============================================================

