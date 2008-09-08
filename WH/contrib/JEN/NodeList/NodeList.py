# file: ../JEN/NodeList/NodeList.py

# History:
# - 31may2007: creation
# - 20jul2007: improved .plot_xy()

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

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *
from Timba.Meq import meq


from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect
from Timba.Contrib.JEN.Grunt import display

from copy import deepcopy
from numpy import array

#======================================================================================

class NodeList (object):
    """The Grunt NodeList class encapsulates an arbitrary list of nodes"""

    def __init__(self, ns, name, quals=[], kwquals={},
                 nodes=[], labels=None, **pp):

        # The name of this group of nodes:
        self._name = str(name)
        
        self._nodes = []
        self._labels = []
        self.append(nodes, labels)

        # Scopify, if necessary:
        if is_node(ns):
            self.ns = ns.QualScope()
            self.ns0 = ns.QualScope()
        else:
            qq = ns.dummy.name.split(':')
            if self._name in qq:
                self.ns = ns.QualScope()
            else:
                self.ns = ns.QualScope(self._name)
            self.ns0 = ns

        # Attach qualifiers, if required:
        self._quals = _quals2list(quals)
        self._kwquals = kwquals
        if not isinstance(self._kwquals,dict): self._kwquals = dict()
        if self._quals or self._kwquals:
            self.ns = self.ns.QualScope(*self._quals, **self._kwquals)        

        # Miscellaneous settings:
        self._pp = pp
        if not isinstance(pp, dict): pp = dict()
        # Plotting instructions:
        pp.setdefault('color','red')
        pp.setdefault('style','circle')
        pp.setdefault('size',10)
        pp.setdefault('pen',2)
        pp.setdefault('unit',None)
        # Tensor information (see .tensor_elements()):
        pp['tensor'] = dict(elems=None, color=None, style=None,
                            size=None, pen=None)

        # Misc initializations:
        self._counter = dict(copy=0)
        return None

    #---------------------------------------------------------------

    def append(self, node, label=None):
        """Append one or more nodes to the list. Optionally provide label(s).
        If node is another NodeList object, append its nodes.
        """
        if isinstance(node, NodeList):
            for k,nd in enumerate(node._nodes):
                self._nodes.append(nd)
                self._labels.append(node._labels[k])
            self._name = '('+self.name()+','+node.name()+')'
            # NB: Update self._opt....?
        else:
            if not isinstance(node,(list,tuple)): node = [node]
            node = list(node)
            k = self.len()
            for i,nd in enumerate(node): 
                self._nodes.append(nd)
                k += 1
                if label==None:                # Give automatic node label, e.g. for plotting
                    self._labels.append(self.name()+'_'+str(k))
                elif isinstance(label,(list,tuple)):
                    self._labels.append(str(label[i]))   # assume (node,label) equal length
                else:              
                    self._labels.append(str(label))      # assume len(node)==1...
        return True


    #----------------------------------------------------------------

    def tensor_elements (self, elems=None, color=None, style=None,
                         size=None, pen=None):
        """Set the names/colors/etc of tensor elements, so that they may
        be extracted by name (see .extract()), or plotted (see .plot_rvsi())
        with different colors/styles. If no arguments are given, the
        tensor-element definition is reset to None."""

        if isinstance(elems,str): elems = elems.split(' ')
        if not isinstance(elems,list): elems = None
        
        tt = self._pp['tensor']      # convenience
        tt['elems'] = elems          # tensor element names (e.g. ['XX','XY','YX','YY'])
        tt['color'] = color          # their plot colors (rvsi)
        tt['style'] = style          # their plot symbol styles
        tt['size'] = size            # their plot symbol sizes
        tt['pen'] = pen              # their plot pen widths

        # Check the internal consistency:
        if isinstance(elems, list):
            n = len(elems)
            for key in ['color','style','size','pen']:
                if not isinstance(tt[key],list) or not len(tt[key])==n:
                    tt[key] = []
                    for i in range(n):
                        tt[key].append(self._pp[key])
        return True



    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = 'Grunt.NodeList:'
        ss += ' '+str(self._name)
        ss += '  (len='+str(self.len())+')'
        ss += '  ('+str(self.ns['<>'].name)+')'
        return ss


    def display(self, txt=None, full=False, recurse=3):
        """Print a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print '  * (txt='+str(txt)+')'
        print '  * quals = '+str(self._quals)+'   kwquals = '+str(self._kwquals)
        print '  * ns = '+str(self.ns)+' -> '+str(self.ns << 1)
        print '  * ns0 = '+str(self.ns0)+ ' -> '+str(self.ns0 << 1)
        #...............................................................
        print '  * Nodes ('+str(len(self._nodes))+'):'
        for k,node in enumerate(self._nodes):
            print '   - ('+self._labels[k]+'): '+str(node)
        #...............................................................
        rr = deepcopy(self._pp)
        rr['tensor'] = '<see below>'
        print '  * settings (pp): '+str(rr)
        print '  * pp.tensor: '+str(self._pp['tensor'])
        print '  * counter(s): '+str(self._counter)
        print '**\n'
        return True


    #===============================================================
    # Basic access functions:
    #===============================================================

    def len (self):
        """Return the length of its list of nodes"""
        return len(self._nodes)

    def name (self, strip=True):
        """Return the name of this object. If strip==True, remove the
        bits after (|) that make this name unique (for readability)."""
        if strip:
            return self._name.split('|')[0]
        return self._name

    def nodes (self):
        """Return the list of nodes"""
        return self._nodes

    def __getitem__(self, index):
        """Get the speciified (index) node from the NodeList"""
        if not isinstance(index, int):
            raise TypeError,' index not an int'
        elif index<0 or index>=self.len():
            raise TypeError,' index out of range'
        else:
            return self._nodes[index]
            

    #===============================================================
    # Some local helper functions:
    #===============================================================

    def copy (self, quals=None, select='*', trace=False):
        """Make a copy of this object, with (a selection of) its nodes.
        The new object will be qualified with any quals that are specified
        in this call.
        """

        # Make an empty new NodeList with a unique name. This greatly reduces
        # the danger of nodename clashes, or inadvertent branch cross-overs.
        # (The only danger is with NodeList objects that have the same name,
        # e.g. generated automatically in widely separated branches of the tree...)
        
        name = self._name

        self._counter['copy'] += 1                   # increment kopie-counter
        quals = _quals2list(quals)
        quals.append('C'+str(self._counter['copy']))

        # Avoid duplication of qualifiers:
        qq = self.ns['dummy'].name.split(':')
        for q in qq:
            if q in quals: quals.remove(q)
        if name in quals: quals.remove(name)

        new = NodeList(self.ns, name, quals=quals)

        # Transfer the (selection of) nodes and their labels:
        ii = self._selection (select)
        for i in ii:
            new._nodes.append(self._nodes[i])
            new._labels.append(self._labels[i])
        new._pp = deepcopy(self._pp)

        if trace: new.display('from inside .copy()')
        return new

    #----------------------------------------------------------------

    def _dispose(self, kopie, replace=False):
        """Dispose of the (modified) copy of itself. Either return
        the given copy, or replace its own internals with the copy."""
        if replace:
            self._nodes = deepcopy(kopie._nodes)
            self._labels = deepcopy(kopie._labels)
            self._pp = deepcopy(kopie._pp)
            return True
        kopie.ns = kopie.ns0(kopie._name)
        return kopie

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

    def _selection (self, select='*', return_nodes=False):
        """Return a list of valid indices for node selection.
        If return_nodes==True, return a list of selected nodes.
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

        if return_nodes:
            cc = []
            for i in ii:
                cc.append(self._nodes[i])
            return cc
        return ii

    #----------------------------------------------------------------

    def extract (self, elem=0, replace=False):
        """Extract the specified tensor element(s) (may be a list) from the
        (assumedly tensor) nodes in the NodeList. The elem may be integer(s),
        or element name(s). In the latter case, a list of element names must
        be supplied at NodeList creation. (e.g. , elements=['XX','XY','YX','YY']).
        The result will contain a reduced list of element names.
        If replace==True, replace the nodes with the new ones.
        Otherwise, return a new NodeList with the new nodes."""

        ii = deepcopy(elem)
        if not isinstance(ii, (list,tuple)): ii = [ii]
        ppel = self._pp['tensor']['elems']
        elems = []
        first = True
        for k,i in enumerate(ii):
            if isinstance(i,int):           # e.g. 1
                if isinstance(ppel,list):
                    elems.append(ppel[i])   # e.g. 'XX'
                else:
                    elems.append(str(i))
            elif isinstance(i,str):         # e.g. 'XX'
                ii[k] = ppel.index(i)       # index must be integer
                elems.append(i)

        if len(elems)==0:
            raise ValueError, 'no tensor elements to be extracted'

        selems = '['+elems[0]
        for m,i in enumerate(ii):  
            if m>0: selems += ','+elems[m]
        selems += ']'

        # NB: MeqSelector only supports a single integer index....!?
        # That is why we offer a workaround by re-composing multiple ones.

        kopie = self.copy()
        kopie.tensor_elements(elems)        # adjust nr of tensor elements
        for k,node in enumerate(kopie._nodes):
            cc = []
            for m,i in enumerate(ii):       # extract elements one-by-one
                name = 'extract['+str(elems[m])+']'
                qnode = kopie.ns[name](k)
                if not qnode.initialized():
                    qnode << Meq.Selector(kopie._nodes[k], index=i)
                cc.append(qnode)

            if len(cc)==1:                  # extracted one only element
                kopie._nodes[k] = cc[0]
                kopie._labels[k] += ' ['+str(elems[m])+']'
            else:                           # more: recompose into new tensor
                name = 'extract'+selems
                qnode = kopie.ns[name](k)
                if not qnode.initialized():
                    qnode << Meq.Composer(*cc)
                kopie._nodes[k] = qnode
                kopie._labels[k] += selems
        return self._dispose(kopie, replace)


    #===============================================================
    # Math operations on the nodes:
    #===============================================================

    def unop(self, unop, replace=False, **pp):
        """Apply one or more unary operations (e.g. Cos()) to all nodes.
        NB: The ops are applied from right to left, i.e. like a math expr.
        If replace==True, replace the nodes with the new ones.
        Otherwise, return a new NodeList with the new nodes."""

        if isinstance(unop, str): unop = unop.split(' ')
        unop = list(unop)
        unop.reverse()
        kopie = self.copy()
        for unop1 in unop:
            raxes = None
            if unop1 in ['Sum','Product','StdDev','Rms','Mean','Max','Min']:
                if not isinstance(pp,dict): pp = dict()
                pp.setdefault('reduction_axes',None)        # written correctly?
                raxes = pp['reduction_axes']                # e.g. ['time']
            kopie._name = unop1+'('+kopie._name+')'
            for k,node in enumerate(kopie._nodes):
                if raxes:
                    unode = kopie.ns << getattr(Meq,unop1)(node, reduction_axes=raxes)
                else:
                    unode = kopie.ns << getattr(Meq,unop1)(node)
                kopie._nodes[k] = unode
                kopie._labels[k] = '('+kopie._labels[k]+')'
        return self._dispose(kopie, replace)

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

        kopie = self.copy()
        if len(binopin)==1:
            kopie._name = '('+kopie._name+binopin+other._name+')'
        else:
            kopie._name = '('+kopie._name+'|'+binopin+'|'+other._name+')'

        for k,lhs in enumerate(kopie._nodes):
            if len(binopin)==1:
                kopie._labels[k] = '('+kopie._labels[k]+binopin+other._labels[k]+')'
            else:
                kopie._labels[k] = '('+kopie._labels[k]+'|'+binopin+'|'+other._labels[k]+')'
            name = kopie._labels[k]
            rhs = other._nodes[k]
            kopie._nodes[k] = kopie.ns[name].qmerge(rhs) << getattr(Meq,binop)(lhs, rhs)
        return self._dispose(kopie, replace)
        
    #---------------------------------------------------------------

    def compare (self, other, bookpage=True, show=False):
        """Compare the nodes of a NodeList with the corresponding ones
        of another NodeList."""
        diff = self.binop('-', other)
        qnode = diff.bundle(unop='Abs', combine='Add',
                            bookpage=bookpage)
        if show: display.subtree(qnode, show_initrec=False)
        return qnode


    #===============================================================
    # subtrees:
    #===============================================================

    def bundle (self, combine='Add', wgt=None,
                bookpage=True, subset=8, folder=None, 
                select='*', unop=None, show=False):
        """Bundle the (selection of) nodes by applying the specified
        combine-operation (default='Add') to them.
        The (optional) wgt vector is used for WMean and WSum only. 
        If unary operation(s) specified (unop), apply it/them first.
        Return the root node of the resulting subtree.
        If bookpage is specified, make a bookmark on the specified page
        and folder. Show the bundle, and a subset (display) of nodes. 
        """

        kopie = self.copy(select=select)
        quals = []
        if unop: quals.append(unop)      
        quals.append(combine+str(kopie.len()))
        qnode = kopie.ns['bundle'](*quals)
        if qnode.must_define_here(self):
            nodes = kopie._nodes
            if unop:
                nodes = kopie.unop(unop)._nodes
            if combine in ['WSum','WMean']:
                if not isinstance(wgt,list): wgt = []
                if not len(wgt)==len(nodes):
                    wgt = []
                    for node in nodes: wgt.append(1.0)
                qnode << getattr(Meq,combine)(children=nodes, weights=wgt)
            else:
                qnode << getattr(Meq,combine)(children=nodes)

        if bookpage:
            # Make a page with the bundle and a subset of the list nodes:
            nodes = [qnode]
            n = subset
            if False and not combine=='Composer':
                # Always include a Composer, since it gives access to all nodes
                xnode = kopie.ns['extra'](*quals)
                extra = xnode << Meq.Composer(children=nodes)
                nodes.append(extra)
                n = min(8,n-1)
            cc = self._selection (select=n, return_nodes=True)
            nodes.extend(cc)
            page = self.name()
            if isinstance(bookpage, str): page = bookpage
            JEN_bookmarks.create(nodes, 'bundle_'+self._name,
                                 page=page, folder=folder)

        # Finished: Return the root-node of the bundle subtree:
        if show: display.subtree(qnode, show_initrec=False)
        return qnode

    #---------------------------------------------------------------

    def max (self, unop=None, bookpage=True, show=False):
        """Return a node that returns the maximum CELL value of the list nodes"""
        return self.bundle('Max', unop=unop, bookpage=bookpage, show=show)

    def maxabs (self, bookpage=True, show=False):
        """Return a node that returns the maximum CELL value of the list nodes"""
        return self.bundle('Max', unop='Abs', bookpage=bookpage, show=show)

    def min (self, unop=None, bookpage=True, show=False):
        """Return a node that returns the minimum CELL value of the list nodes"""
        return self.bundle('Min', unop=unop, bookpage=bookpage, show=show)

    #---------------------------------------------------------------

    def mean (self, unop=None, bookpage=True, show=False):
        """Return a node that returns the cell-by-cell mean of the list nodes"""
        return self.bundle('WMean', unop=unop, bookpage=bookpage, show=show)


    #===============================================================
    # Visualization:
    #===============================================================


    def bookpage (self, select=9, page=None, folder=None):
        """Make a page of bookmarks for (a selection of) the nodes of
        this NodeList object. Nothing is returned, because the bookmarks
        just publish the selected nodes as they are doing their thing."""
        cc = self._selection(select, return_nodes=True)
        if not isinstance(page, str): page = self.name()
        JEN_bookmarks.create(cc, self.name()+'_select='+str(select),
                             page=page, folder=folder)
        return True


    def bookmark (self, select=[0], page=None, folder=None):
        """Make bookmark(s) for a specific selection of the nodes of
        this NodeList object. Nothing is returned, because the bookmarks
        just publish the selected nodes as they are doing their thing."""
        cc = self._selection(select, return_nodes=True)
        JEN_bookmarks.create(cc, self.name()+'_select='+str(select),
                             page=page, folder=folder)
        return True

    #--------------------------------------------------------------

    def plot_xy (self, xx=None,
                 xlabel=None, ylabel=None,
                 color=None, style=None, size=None, pen=None,
                 bookpage=True, folder=None):
        """Misuse the rvsi plotter to plot the node-values of this NodeList
        as y-values against the x-values of another (commensurate) one (xx).
        If xx is not specified, a commensurate one with integers will be
        generated."""
        if not xx:
            qnode = self.ns['xx']
            xx = NodeList(qnode, 'xaxis')
            for x in range(self.len()):
                label = str(x)
                node = qnode(x) << Meq.Constant(x)
                xx.append(node, label)
        if not isinstance(xlabel, str):
            xlabel = xx.name()+'  (unit='+str(xx._pp['unit'])+')'
        if not isinstance(ylabel, str):
            ylabel = self.name()+'  (unit='+str(self._pp['unit'])+')'
        if not isinstance(bookpage, str):
            bookpage = 'plot_xy_'+self.name()
        return xx.plot_rvsi (other=self,
                             color=color, style=style, size=size, pen=pen,
                             bookpage=bookpage, folder=folder,
                             mean_circle=False, errorbars=False,
                             xlabel=xlabel, ylabel=ylabel)
        
    #--------------------------------------------------------------

    def plot_rvsi (self, select='*', other=None, quals=None,
                   bookpage=True, folder=None,
                   color=None, style=None, size=None, pen=None,
                   xlabel='xx', ylabel='yy',
                   tag='', concat=False,
                   mean_circle=False, errorbars=True,
                   show=False):
        """Visualize the (selected) nodes with a 'real-vs-imaginary' plot.
        If another (commensurate) NodeList is specified, make complex numbers with
        (real,imag) is (self,other). This misuses the rvsi plot to plot one agains
        the other....
        Return the root node of the resulting subtree. Make a bookmark, if required."""

        kopie = self.copy(select=select, quals=quals)
        if other:
            kopie = self.binop('ToComplex', other.copy(select=select, quals=quals)) 

        tt = kopie._pp['tensor']
        if isinstance(tt['elems'],list) and len(tt['elems'])>1:
            # Special case: Tensor elements are plotted with different colors/styles
            dcolls = []
            for k,elem in enumerate(tt['elems']):
                nn = kopie.extract(elem)
                nn.tensor_elements()                 # reset...
                for key in ['color','style','size','pen']:
                    nn._pp[key] = tt[key][k]
                rr = nn.plot_rvsi(bookpage=False, concat=True, tag=elem)
                dcolls.append(rr)
            # Concatenate the dcolls of the various tensor elements:
            rr = MG_JEN_dataCollect.dconc(kopie.ns, dcolls,
                                          scope='plot_rvsi', tag='',
                                          bookpage=None)
        else:
            # Normal case: All nodes are plotted in the same color/style
            rr = MG_JEN_dataCollect.dcoll (kopie.ns, kopie._nodes, 
                                           scope='plot_rvsi', tag=tag,
                                           color=(color or kopie._pp['color']),
                                           style=(style or kopie._pp['style']),
                                           size=(size or kopie._pp['size']),
                                           pen=(pen or kopie._pp['pen']),
                                           xlabel=xlabel, ylabel=ylabel,
                                           errorbars=errorbars,
                                           mean_circle=mean_circle,
                                           type='realvsimag')
                                           
        qnode = rr['dcoll']
        if bookpage:
            if not isinstance(bookpage, str):
                bookpage = 'plot_rvsi_'+kopie.name()
            JEN_bookmarks.create(qnode, kopie.name(),
                                 page=bookpage, folder=folder)
        if concat: return rr
        if show: display.subtree(qnode, show_initrec=True)
        return qnode


    #--------------------------------------------------------------

    def plot_spectra (self, select='*', quals=None,
                      bookpage=True, folder=None,
                      xlabel='xx', ylabel='yy',
                      tag='', concat=False,
                      show=False):
        """Visualize the (selected) nodes with a dataCollect 'spectra' plot.
        Return the root node of the resulting subtree. Make a bookmark, if required."""

        kopie = self.copy(select=select, quals=quals)
        tt = kopie._pp['tensor']
        if isinstance(tt['elems'],list) and len(tt['elems'])>1:
            # Special case: Tensor elements are plotted separately
            dcolls = []
            for k,elem in enumerate(tt['elems']):
                nn = kopie.extract(elem)
                nn.tensor_elements()             
                rr = nn.plot_spectra(bookpage=False, concat=True, tag=elem)
                dcolls.append(rr)
            # Concatenate the dcolls of the various tensor elements:
            rr = MG_JEN_dataCollect.dconc(kopie.ns, dcolls,
                                          scope='plot_spectra', tag='',
                                          bookpage=None)
        else:
            # Normal case: All nodes are plotted in the same color/style
            rr = MG_JEN_dataCollect.dcoll (kopie.ns, kopie._nodes, 
                                           scope='plot_spectra', tag=tag,
                                           xlabel=xlabel, ylabel=ylabel,
                                           type='spectra')
                                           
        qnode = rr['dcoll']
        if bookpage:
            # kopie.display('inside NodeList.plot_spectra()')
            if not isinstance(bookpage, str):
                bookpage = 'plot_spectra_'+kopie.name()
            JEN_bookmarks.create(qnode, kopie.name(),
                                 page=bookpage, folder=folder)
        if concat: return rr
        if show: display.subtree(qnode, show_initrec=True)
        return qnode


    #--------------------------------------------------------------

    def plot_timetracks (self, select='*', quals=None,
                         bookpage=True, folder=None,
                         show=False):
        """Visualize the (selected) nodes with timetrack plots (Collections Viewer).
        Return the root node of the resulting subtree. Make a bookmark, if required."""

        if bookpage:
            if not isinstance(bookpage, str):
                bookpage = 'plot_timetracks_'+kopie.name()

        kopie = self.copy(select=select, quals=quals)
        tt = kopie._pp['tensor']
        qnode = kopie.ns['timetracks']

        if not qnode.must_define_here(self):
            pass
        
        elif isinstance(tt['elems'],list) and len(tt['elems'])>1:
            # Special case: Tensor elements are plotted separately
            cc = []
            for k,elem in enumerate(tt['elems']):
                nn = kopie.extract(elem)
                nn.tensor_elements()             
                node = nn.plot_timetracks(quals=elem, bookpage=bookpage,
                                          folder=folder, show=False)
                cc.append(node)
            qnode << Meq.Composer(children=cc)

        else:
            # Scalar case:
            kopie = kopie.unop('Mean', reduction_axes='freq')  
            qnode << Meq.Composer(children=kopie._nodes,
                                  plot_label=kopie._labels)
            JEN_bookmarks.create(qnode, 'plot_timetracks_'+kopie.name(),
                                 page=bookpage, folder=folder,
                                 viewer='Collections Plotter')

        # Finished, return the root node:
        if show: display.subtree(qnode, show_initrec=True)
        return qnode




    #================================================================
    # Fill the NodeList with some test-nodes:
    #================================================================

    def test(self, n=8):
        """Fill the NodeList with n test-nodes"""
        freq = self.ns << Meq.Freq()
        time = self.ns << Meq.time()
        for i in range(n):
            label = 'T'+str(i)
            node = self.ns['test'](i) << Meq.Cos((1+i/3)*(time+freq))
            self.append(node, label)
        return True


    #----------------------------------------------------------------

    def test22(self, n=8):
        """Fill the NodeList with n 2x2 tensor-nodes"""
        freq = self.ns << Meq.Freq()
        time = self.ns << Meq.time()
        self.tensor_elements (['s','c','cs','cx'],
                              style=['circle','cross','cross','circle'],
                              color=['red','cyan','green','blue'])
        k = 0
        for i in range(10):
            first = True
            for j in range(1,3):
                label = 'T'+str(i)+str(j)
                qnode = self.ns[label]
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
# Standalone helper function(s):
#=============================================================================


def _quals2list (quals):
    """Helper function to make sure that the given quals are a list"""
    if quals==None: return []
    if isinstance(quals, (list,tuple)): return list(quals)
    if isinstance(quals, str): return quals.split(' ')
    return [str(quals)]





#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================



def _define_forest(ns):

    # cc = [ns.dummy<<45]
    cc = []

    nn1 = NodeList(ns, 'nn1')
    nn1.test(8)                       # simple nodes
    # nn1.test22(8)                   # tensor nodes
    nn1.display('initial')


    if 0:
        nn1.bookpage(4)

    if 0:
        unop = None
        # unop = 'Cos Sin'
        node = nn1.bundle('WSum', select='*', unop=unop, show=True)
        node = nn1.bundle('Composer', select='*', unop=unop, show=True)
        cc.append(node)

    if 0:
        # nn2 = nn1.extract(elem=[2,3])
        nn2 = nn1.extract(elem=['cx','c','c'])
        nn2.display('extracted')
        node = nn2.bundle(show=True)
        cc.append(node)

    if 0:
        node = nn1.plot_timetracks()
        cc.append(node)

    if 0:
        # node = nn1.plot_rvsi(other=nn1)
        # nn1.tensor_elements()      # reset
        node = nn1.plot_rvsi()
        cc.append(node)

    if 1:
        node = nn1.plot_xy()
        cc.append(node)

    if 0:
        nns = nn1.extract(elem='s')
        nnc = nn1.extract(elem='c')
        node = nns.plot_xy(nnc)
        cc.append(node)
        node = nnc.plot_xy(nns)
        cc.append(node)

    if 0:
        node = nn1.compare(other=nn1)
        cc.append(node)

    nn1.display('final', full=True)

    if len(cc)==0: cc.append(ns.dummy << 1.1)
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
        # nn1 = NodeList(ns, 'nn1', quals='qual', kwquals=dict(b=5))
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
        nn2 = NodeList(ns, 'nn2')
        nn2.test(3)
        nn1.append(nn2)
        nn2.display('appended')
        nn1.display('append')

    if 0:
        nn1 = NodeList(ns, 'nt1')
        nn1.test(8)
        nn1.tensor_elements()
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

    if 0:
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
        nn2 = nn1.copy(trace=True)
        nn3 = nn1.binop('*', nn2)
        nn3.display('binop')

    if 1:
        nn1.plot_timetracks(show=True)

    nn1.display('final', full=True)



#===============================================================

