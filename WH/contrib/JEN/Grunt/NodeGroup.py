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

from Timba.Contrib.JEN.Grunt import Qualifiers

from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect

from copy import deepcopy



#==========================================================================

class NodeGroup (object):
    """Class that represents a group of (somehow related) nodes"""

    def __init__(self, ns, label='<ng>', nodelist=[],
                 quals=[], descr='<descr>',tags=[], 
                 color='green', style='diamond', size=8, pen=2,
                 rider=None):

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
        self._quals = Qualifiers.Qualifiers(quals, prepend=label)

        # Node tags (for searching the nodescope)
        self._tags = deepcopy(tags)
        if not isinstance(self._tags,(list,tuple)):
            self._tags = [self._tags]

        # Plotting:
        self._dcoll = None
        self._plotinfo = dict(color=color, style=style, size=size, pen=pen)

        return None
                
    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += ' '+str(self.label())
        ss += ' (n='+str(self.len())+')'
        ss += ' quals='+str(self._quals.get())
        if True and len(self._rider)>0:
            for key in self._rider.keys():
                ss += ' ('+key+'='+str(self._rider[key])+')'
        return ss

    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        # NB: This function is called in .display().
        #     It should be re-implemented in a derived class.
        return True

    def display(self, txt=None, full=False):
        """Print a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print ' * (txt='+str(txt)+')'
        self.display_specific(full=full)
        print '** Generic (class NodeGroup):'
        print ' * descr: '+self.descr()
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
            if False:
                print ' * The second node/subtree:'
                self.display_node (index=1)
        #...............................................................
        print ' * Visualization subtree: '
        if self._dcoll:
            self.display_subtree(self._dcoll, txt=':',
                                 show_initrec=False, recurse=1)
        print ' * plot: '+str(self._plotinfo)
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

    def plotinfo(self):
        """Return its dict with plot instructions"""
        return self._plotinfo

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

    #----------------------------------------------------------------------

    def binop(self, binop=None, other=None, replace=False):
        """Do an (item-by-item) binary operation (e.g. Subtract)
        between its own nodes and those another NodeGroup object."""
        cc = []
        for i in range(len(self._nodelist)):
            cc.append(self._ns << getattr(Meq,binop)(self._nodelist(i),
                                                     other._nodelist(i)))
        if replace:
            self._nodelist = cc
        return cc


    def unop(self, unop=None, replace=False):
        """Do an (item-by-item) unary operation (e.g. Abs) on its nodes"""
        cc = []
        for i in range(len(self._nodelist)):
            cc.append(self._ns << getattr(Meq,unop)(self._nodelist[i]))
        if replace:
            self._nodelist = cc
        return cc

    #----------------------------------------------------------------------

    def bundle(self, oper='Composer'):
        """Bundle its nodes, using an operation like Compose, Add, Multiply etc"""
        quals = self.quals()
        if not self._ns[oper](*quals).initialized():
            cc = self.nodelist()
            self._ns[oper](*quals) << getattr(Meq,oper)(children=cc)
        return self._ns[oper](*quals)


    #-----------------------------------------------------------------------

    def visualize (self, bookpage='NodeGroup', folder=None):
        """Visualise all the entries (MeqParms or their simulated subtrees)
        in a single real-vs-imag plot."""
        if not self._dcoll:
            dcoll_quals = self._quals.concat()
            cc = self.nodelist() 
            rr = MG_JEN_dataCollect.dcoll (self._ns, cc, 
                                           scope=dcoll_quals,
                                           tag='',
                                           color=self._plotinfo['color'],
                                           style=self._plotinfo['style'],
                                           size=self._plotinfo['size'],
                                           pen=self._plotinfo['pen'],
                                           type='realvsimag', errorbars=True)
            self._dcoll = rr['dcoll']
            JEN_bookmarks.create(self._dcoll, self.label(),
                                 page=bookpage, folder=folder)
        return self._dcoll



    #===================================================================
    # The following functions are just for convenience.....
    #===================================================================

    def display_node (self, index=0, recurse=1000):
        """Helper function to dispay the specified node(s)/subtree(s)"""
        if index=='*': index = range(len(self._nodelist))
        if not isinstance(index,(list,tuple)): index=[index]
        for i in index:
            if i<len(self._nodelist):
                node = self._nodelist[i]
                self.display_subtree(node, txt=str(i),
                                     show_initrec=True, 
                                     recurse=recurse)
        return True

    #...................................................................

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
                if initrec.has_key('value'):
                    value = initrec.value
                    # if isinstance(value,(list,tuple)):
                    #     initrec.value = value.flat
                if initrec.has_key('default_funklet'):
                    coeff = initrec.default_funklet.coeff
                    initrec.default_funklet.coeff = [coeff.shape,coeff.flat]
            if len(initrec)>0: s += ' '+str(initrec)
        print s
        if recurse>0:
            # print dir(node)
            # print node.__doc__
            if node.initialized():
                for child in node.children:
                    self.display_subtree (child[1], txt=txt, level=level+1,
                                          show_initrec=show_initrec, recurse=recurse-1)
        return True


    #======================================================================

    def test(self, n=4, offset=0):
        """Helper function to put in some standard entries for testing"""
        for i in range(n):
            self.append_entry(self._ns << (i+offset))
        return True




#==========================================================================
#==========================================================================
#==========================================================================
#==========================================================================


class NodeGog (object):
    """Class that represents a group of NodeGroup objects"""

    def __init__(self, ns, label='<gog>', group=[],
                 descr=None, rider=None):
        self._ns = ns                         # node-scope (required)
        self._label = label                   # label of the parameter group 
        self._descr = descr                   # brief description 

        self._group = []                      # initialise the internal group
        if len(group)>0:
            for g in group:
                self.append_entry(g)

        # A NodeGog carries a rider (dict), which contains user-defined info:
        self._rider = dict()
        if isinstance(rider, dict): self._rider = rider

        # Plotting:
        self._dcoll = None                           # visualization
        self._dummyNodeGroup = NodeGroup('dummy')    # used for its printing functions...
        return None
                
    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += ' '+str(self.label())
        ss += ' (n='+str(len(self._group))+')'
        ss += ' '+str(self.labels())
        if True and len(self._rider)>0:
            for key in self._rider.keys():
                ss += ' ('+key+'='+str(self._rider[key])+')'
        return ss

    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        # NB: This function is called in .display().
        #     It should be re-implemented in a derived class.
        return True

    def display(self, txt=None, full=False):
        """Print a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print ' * (txt='+str(txt)+')'
        self.display_specific(full=full)
        print '** Generic (class NodeGog):'
        print ' * descr: '+self.descr()
        print ' * rider ('+str(len(self.rider()))+'):'
        for key in self._rider.keys():
            print '  - '+key+': '+str(self._rider[key])
        print ' * group: '
        for ng in self._group:
            print '  - '+str(ng.oneliner())
        #...............................................................
        print ' * Visualization subtree: '
        if self._dcoll:
            self._dummyNodeGroup.display_subtree(self._dcoll, txt=':',
                                                 show_initrec=False, recurse=1)
        print '**\n'
        return True


    #-------------------------------------------------------------------

    def label(self):
        """Return the label (name) of this NodeGog""" 
        return self._label

    def descr(self):
        """Return the group description""" 
        return str(self._descr)

    def rider(self, key=None):
        """Return (a field of) the rider (dict), with user-defined info""" 
        if key==None: return self._rider
        if self._rider.has_key(key):
            return self._rider[key]
        print '\n** NodeGog.rider(',key,'): key not recognised in:',self._rider.keys(),'\n' 
        return None

    #-------------------------------------------------------------------

    def append_entry(self, group):
        """Append the given entry (group) to the internal group."""
        # Check whether group is a valid NodeGroup....?
        self._group.append(group)
        return len(self._group)

    #----------------------------------------------------------------------

    def nodelist(self):
        """Return a copy of the (combined) list of nodes"""
        nodelist = []
        for ng in self._group:
            nodelist.extend(ng.nodelist())  
        return nodelist

    def group (self):
        """Return the internal group (list of NodeGroup objects)"""
        return self._group

    def labels(self):
        """Return a list of the labels (name) of its NodeGroups""" 
        ll = []
        for ng in self._group:
            ll.append(ng.label())
        return ll

    def bundle(self, oper='Composer'):
        """Bundle its bundled NodeGroups, using an operation like
        Compose, Add, Multiply etc"""
        cc = []
        for ng in self._group:
            cc.append(ng.bundle(oper=oper))
        return self._ns << getattr(Meq,oper)(children=cc)

    #----------------------------------------------------------------------

    def visualize (self, bookpage='NodeGog', folder=None):
        """Visualise all the nodes of the various NodeGroups in
        a single (realvsimag) plot, each with its own plot-style"""
        if not self._dcoll:
            # dcoll_quals = self._quals.concat()
            dcolls = []
            for ng in self._group:
                cc = ng.nodelist()
                rr = MG_JEN_dataCollect.dcoll (self._ns, cc, 
                                               # scope=dcoll_quals,
                                               tag=ng.label(),
                                               color=ng._plotinfo['color'],
                                               style=ng._plotinfo['style'],
                                               size=ng._plotinfo['size'],
                                               pen=ng._plotinfo['pen'],
                                               type='realvsimag', errorbars=True)
                dcolls.append(rr)
            # Make a combined plot of all the matrix elements:
            # NB: nodename -> dconc_scope_tag
            rr = MG_JEN_dataCollect.dconc(self._ns, dcolls,
                                          # scope=dcoll_quals,
                                          tag=self.label(), bookpage=None)
            # Return the dataConcat node:
            self._dcoll = rr['dcoll']
            JEN_bookmarks.create(self._dcoll, self.label(),
                                 page=bookpage, folder=folder)
        return self._dcoll


    #======================================================================

    def test(self):
        """Helper function to put in some standard entries for testing"""

        ng = NodeGroup(self._ns, 'first', color='red')
        ng.test(4)
        self.append_entry(ng)

        ng = NodeGroup(self._ns, 'second', color='blue')
        ng.test(7, offset=0.2)
        self.append_entry(ng)
        
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
    ng2.test(offset=0.2)
    cc.append(ng2.visualize())
    nn2 = ng2.nodelist()
    print 'nn2 =',nn2

    gog = NodeGog(ns, 'gog', group=[ng1,ng2])
    cc.append(gog.visualize())

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

    if 1:
        ng1 = NodeGroup(ns, 'ng1')
        ng1.test()
        ng1.display()
        
        if 0:
            dcoll = ng1.visualize()
            ng1.display_subtree (dcoll, txt='dcoll')

        if 0:
            node = ng1.sum()
            node = ng1.product()
            ng1.display_subtree (node, txt='test')

    if 0:
        cc = []
        cc = [ns << 45]
        ng2 = NodeGroup(ns, 'ng2', nodelist=cc, color='red')
        # ng2.test(6)
        ng2.display()

        if 0:
            ng2 = NodeGroup(ns, 'ng2')
            ng2.append_entry(ss << 1.0)
            ng2.append_entry(ss << 2.0)
            nn = ng2.nodelist(trace=True)
            ng2.display()
            if 1:
                ng12 = NodeGroup(ns, 'ng12', ng=[ng1,ng2], descr='combination')
                ng12.display()

    #------------------------------------------------------------

    if 1:
        gog1 = NodeGog(ns, 'gog1')
        gog1.test()
        gog1.display()

        if 0:
            gog1.visualize()
            gog1.display()

        if 0:
            node = gog1.bundle()
            gog1._dummyNodeGroup.display_subtree (node, txt='bundle')



#===============================================================
    
