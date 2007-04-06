# file: ../Grunt/NodeGroup.py

# History:
# - 02jan2007: creation (from ParmGroup)
# - 26mar2007: adapted to QualScope.py

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

from Timba.Contrib.JEN.Grunt import display
import Meow

from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect

from copy import deepcopy



#==========================================================================

class NodeGroup (object):
    """Class that represents a group of (somehow related) nodes"""

    def __init__(self, ns, label='<ng>', quals=[],
                 basename=None,
                 descr='<descr>', tags=[], 
                 nodelist=[],
                 color='green', style='diamond', size=8, pen=2,
                 rider=None):

        self._label = str(label)
        self._descr = descr                   # brief description 

        # The basename of the nodes created by create_member():
        self._basename = basename
        if not isinstance(self._basename,str):
            self._basename = self._label
        
        # Node-name qualifiers:
        self._ns = Meow.QualScope(ns, quals=quals)

        self._nodelist = []                   # initialise the internal nodelist
        if len(nodelist)>0:
            for node in nodelist:
                self.append_member(node)

        # A NodeGroup carries a rider (dict), which contains user-defined info:
        self._rider = dict()
        if isinstance(rider, dict): self._rider = rider

        # Node tags (for searching the nodescope)
        self._tags = deepcopy(tags)
        if not isinstance(self._tags,(list,tuple)):
            self._tags = [self._tags]

        # Plotting:
        self._dcoll = None
        self._coll = None
        self._plotinfo = dict(color=color, style=style, size=size, pen=pen)
        self._plot_labels = []

        return None
                
    #-------------------------------------------------------------------

    def tabulate (self, ss='', header=False):
        """Make a one-line summary to be used as an entry (row) in a table.
        To be used to make a summary table of NodeGroups (e.g. ParmGroups).
        This is a placeholder, to be re-implemented by derived classes."""
        if header:
            ss += '   Header of a NodeGroup table:'
            ss += '\n'
        ss += ' - '+str(self.oneliner())
        ss += '\n'
        return ss

    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = '<NodeGroup>'
        ss += ' %14s'%(self.label())
        ss += ' (n='+str(self.len())+')'
        if not self._basename==self._label:
            ss += ' ('+str(self._basename)+')'
        ss += '  quals='+str(self._ns._qualstring())
        ss += '  tags='+str(self._tags)
        # if self._rider: ss += ' rider:'+str(self._rider.keys())
        return ss

    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        # NB: This function is called in .display().
        #     It should be re-implemented in a derived class.
        return True

    def display(self, txt=None, full=False, nmax=10):
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
        n = self.len()
        print ' * The first '+str(min(n,nmax))+' nodes in current nodelist (len='+str(n)+'): '
        for i in range(min(nmax,n)):
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
        print ' * plot_labels: '+str(self.plot_labels())
        print '**\n'
        return True


    #-------------------------------------------------------------------

    def label(self):
        """Return the label (name) of this NodeGroup""" 
        return self._label

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

    def plot_labels(self):
        """Return a list with plot-labels"""
        return self._plot_labels

    def len(self):
        """Return the length of the nodelist"""
        return len(self._nodelist)

    def nodelist(self):
        """Return a copy of the list of (MeqParm or other) nodes"""
        nodelist = []
        nodelist.extend(self._nodelist)           # Do NOT modify self._nodelist!!
        return nodelist

    def group (self):
        """Return a list of itself (for consistency with NodeGog.group()"""
        return [self]

    #-------------------------------------------------------------------

    def append_member(self, node, plot_label=None):
        """Append the given entry (node) to the internal nodelist."""
        # Check whether it is a valid node....?
        self._nodelist.append(node)
        # Make sure that there is a plot-label:
        if plot_label==None:
            plot_label = str(self.len())
        self._plot_labels.append(str(plot_label))
        return len(self._nodelist)

    def create_member (self, quals=None):
        """Virtual method for creating a new entry. The NodeGroup does not have
        enough information to do this, but specialisations of this class do."""
        return None

    #-------------------------------------------------------------------

    def compare(self, other, quals=None):
        """Compare its nodes with the corresponding nodes of another NodeGroup object,
        for instance simulated and the actual values. It is assumed that the two sets
        of nodes have the same order."""
        ns = self._ns._merge(other._ns)
        ns = ns._derive(append=quals)
        # ns = ns._derive(append=self.label())
        nn1 = self.nodelist()
        nn2 = other.nodelist()
        self.match(other, 'compare()')
        node = ns['ng_compare_'+str(len(nn1))]
        if not node.initialized():
            absdiff = []
            for i in range(len(nn1)):
                diff = node('diff')(i) << Meq.Subtract(nn1[i],nn2[i])
                absdiff.append(node('absdiff')(i) << Meq.Abs(diff))
            node << Meq.Add(children=absdiff)
        return node


    def match(self, other, origin):
        """Helper function to check whether the other group is a match (length etc)"""
        nn1 = self.nodelist()
        nn2 = other.nodelist()
        if not len(nn2)==len(nn1):
            ss = self.label()+'('+str(len(nn1))+') '
            ss += other.label()+'('+str(len(nn2))+')'
            raise ValueError, '** NodeGroup.'+str(origin)+': length mismatch: '+ss
        return True

    #----------------------------------------------------------------------

    def binop(self, binop=None, other=None, quals=None, replace=False):
        """Do an (item-by-item) binary operation (e.g. Subtract)
        between its own nodes and those of another NodeGroup object.
        If replace==True, replace the group nodes with the results."""
        ns = self._ns._merge(other._ns)
        ns = ns._derive(append=quals)
        # ns = ns._derive(append=self.label())
        self.match(other, 'binop()')
        unode = ns['ng_'+str(binop)]
        cc = []
        for i in range(len(self._nodelist)):
            cc.append(unode(i) << getattr(Meq,binop)(self._nodelist[i],
                                                     other._nodelist[i]))
        if replace:
            self._nodelist = cc
        return cc


    def unop(self, unop=None, quals=None, replace=False):
        """Do an (item-by-item) unary operation (e.g. Abs) on its nodes"""
        ns = self._ns._derive(append=quals)
        # ns = ns._derive(append=self.label())
        unode = ns['ng_'+str(unop)]
        cc = []
        for i in range(len(self._nodelist)):
            cc.append(unode(i) << getattr(Meq,unop)(self._nodelist[i]))
        if replace:
            self._nodelist = cc
        return cc

    #----------------------------------------------------------------------

    def bundle(self, oper='Composer', quals=None):
        """Bundle its nodes, using an operation like Compose, Add, Multiply etc"""
        ns = self._ns._derive(append=quals, prepend=oper)
        ns = ns._derive(append=self.label())
        node = ns['ng_bundle_'+str(self.len())]
        if not node.initialized():
            node << getattr(Meq,oper)(children=self.nodelist())
        return node


    #-----------------------------------------------------------------------

    def visualize (self, quals=None, bookpage='NodeGroup', folder=None):
        """Visualise all the NodeGroup entries in a single real-vs-imag plot."""
        if not self._dcoll:
            ns = self._ns._derive(append=quals)
            ns = ns._derive(append=self.label())
            cc = self.nodelist() 
            rr = MG_JEN_dataCollect.dcoll (ns, cc, 
                                           scope='', tag='',
                                           color=self._plotinfo['color'],
                                           style=self._plotinfo['style'],
                                           size=self._plotinfo['size'],
                                           pen=self._plotinfo['pen'],
                                           type='realvsimag', errorbars=True)
            self._dcoll = rr['dcoll']
            JEN_bookmarks.create(self._dcoll, self.label(),
                                 page=bookpage, folder=folder)
        return self._dcoll


    #-----------------------------------------------------------------------

    def collector (self, quals=None, bookpage='NodeGroup', folder=None):
        """Visualise all the NodeGroup entries in a single plot"""
        if not self._coll:
            ns = self._ns._derive(append=quals)
            ns = ns._derive(append=self.label())
            cc = self.nodelist()
            if len(cc)==0: return None
            coll = ns.ng_coll
            for i in range(len(cc)):
                cc[i] = coll('freqmean')(i) << Meq.Mean (cc[i], reduction_axes="freq")
            coll << Meq.Composer(dims=[len(cc)], plot_label=self.plot_labels(),
                                 children=cc)
            self._coll = coll
            JEN_bookmarks.create(self._coll, self.label(),
                                 viewer='Collections Plotter',
                                 page=bookpage, folder=folder)
        return self._coll



    #===================================================================
    # The following functions are just for convenience.....(kludge)
    # NB: They are called in various other Grunt modules....
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
                         skip_line_before=False,
                         skip_line_after=True,
                         show_initrec=True,
                         recurse=1000):
        """Helper function to display a subtree recursively"""
        return display.subtree (node, txt=txt, level=level,
                                skip_line_before=skip_line_before,
                                skip_line_after=skip_line_after,
                                show_initrec=show_initrec,
                                recurse=recurse)

    #======================================================================

    def test(self, n=4, offset=0, quals=None):
        """Helper function to put in some standard entries for testing"""
        ns = self._ns._derive(append=quals)
        name = 'test'
        # name = self.label()
        for i in range(n):
            self.append_member(ns[name](i) << Meq.Constant(i+offset, dims=[1]))
        return True















#===========================================================================================
#===========================================================================================
#===========================================================================================


class NodeGog (object):
    """Class that represents a group of NodeGroup objects"""

    def __init__(self, ns, label='<gog>', quals=[],
                 group=[],
                 descr=None, rider=None):

        self._label = label                   # label of the parameter group 
        self._descr = descr                   # brief description 

        # Node-name qualifiers:
        self._ns = Meow.QualScope(ns, quals=quals)
        # self._ns = self._ns._derive(append=self._label)

        self._group = []                      # initialise the internal group
        if len(group)>0:                      # group supplied externally
            for g in group:
                self.append_member(g)

        # A NodeGog carries a rider (dict), which contains user-defined info:
        self._rider = dict()
        if isinstance(rider, dict): self._rider = rider

        # Merge the riders of the constituent groups into its own....
        self.merge_riders()                   # ................!!

        # Plotting:
        self._dcoll = None                           # visualization
        self._dummyNodeGroup = NodeGroup(ns,'dummy')    # used for its printing functions...
        return None
                
    #-------------------------------------------------------------------

    def tabulate (self, ss=''):
        """Print a tabulated summary of the NodeGroups."""
        ss += ' -- Tabulated: '+str(self.oneliner())
        ss += '\n'
        for k,ng in enumerate(self._group):
            ss = ng.tabulate(ss, header=(k==0))
        return ss

    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = '<NodeGog>'
        ss += ' %10s'%(self.label())
        n = self.len()
        ss += ' (n='+str(n)+'):'
        gg = self.labels()
        nmax = 5
        if n>nmax:
            gg = gg[0:nmax]
            gg.extend(['...',self.labels()[n-1]])
        ss += '   '+str(gg)
        # ss += ' quals='+str(self._ns._qualstring())
        # if self._rider: ss += ' rider:'+str(self._rider.keys())
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

    #-------------------------------------------------------------------

    def append_member(self, group, trace=False):
        """Append the given entry (group) to the internal group.
        NB: If group is a list (of NodeGroups), all its elements are appended."""
        was = self.len()
        if not isinstance(group,(list,tuple)):
            group = [group]
        for g in group:
            # NB: Check whether group is a valid NodeGroup....?
            test = (type(g)==NodeGroup)
            # test = (type(g)==ParmGroup.ParmGroup)
            self._group.append(g)
            if trace:
                print '----- append_member(',self.label(),g.label(),test,'):',was,'->',self.len()
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

    def len (self):
        """Return the length of the internal group (list of NodeGroup objects)"""
        return len(self._group)

    def labels(self):
        """Return a list of the labels (name) of its NodeGroups""" 
        ll = []
        for ng in self._group:
            ll.append(ng.label())
        return ll

    #----------------------------------------------------------------------------

    def bundle(self, oper='Composer', quals=None):
        """Bundle its bundled NodeGroups, using an operation like
        Compose, Add, Multiply etc"""
        ns = self._ns._derive(append=quals, prepend=oper)
        ns = ns._derive(append=self.label())
        cc = []
        for ng in self._group:
            cc.append(ng.bundle(oper=oper))
        node = ns['gog_bundle_'+str(len(cc))]
        if not node.initialized():
            node << getattr(Meq,oper)(children=cc)
        return node

    def collector (self, quals=None, bookpage='NodeGog', folder=None):
        """Visualize its group of NodeGroups. Return a single node."""
        cc = []
        for ng in self._group:
            coll = ng.collector(bookpage=bookpage, folder=folder)
            if not coll==None: cc.append(coll)
        if len(cc)==0: return False
        if len(cc)==1: return cc[0]
        ns = self._ns._derive(append=quals) 
        ns = ns._derive(append=self.label())
        coll = ns.gog_coll
        if not coll.initialized():
            coll << Meq.Composer(children=cc)
        return coll

    #----------------------------------------------------------------------------

    def constraint_condeq (self):
        """Make a list of constraint-condeqs from its ParmGroups"""
        cc = []
        for ng in self._group:
            condeq = ng.constraint_condeq()
            if condeq:
                if isinstance(condeq,list):
                    cc.extend(condeq)
                else:
                    cc.append(condeq)
        return cc

    #-----------------------------------------------------------------------------

    def rider(self, key=None):
        """Return (a field of) the rider (dict), with user-defined info""" 
        if key==None: return self._rider
        if self._rider.has_key(key):
            return self._rider[key]
        print '\n** NodeGog.rider(',key,'): key not recognised in:',self._rider.keys(),'\n' 
        return None


    def merge_riders(self, trace=False):
        """Merge the riders of the constituent groups into the group rider.
        This is a bit of a kludge....."""
        rr = self.rider()
        for ng in self.group():
            rg = ng.rider()
            for key in rg.keys():
                v = rg[key]
                if not rr.has_key(key):
                    rr[key] = v
                elif isinstance(rr[key],dict):
                    rr[key][ng.label()] = v
                elif rr[key]=='*':
                    pass
                elif v=='*':
                    rr[key] = v
                else:
                    old = rr[key]
                    if not isinstance(old,(list,tuple)): old = [old]
                    if not isinstance(v,(list,tuple)): v = [v] 
                    for v1 in v:
                        if not v1 in old: 
                            old.append(v1)
                    rr[key] = old
        self._rider = rr
        return rr



    #----------------------------------------------------------------------
    #----------------------------------------------------------------------

    def visualize (self, quals=None, bookpage='NodeGog', folder=None):
        """Visualise all the nodes of the various NodeGroups in
        a single (realvsimag) plot, each with its own plot-style"""
        if not self._dcoll:
            ns = self._ns._derive(append=quals)
            ns = ns._derive(append=self.label())
            dcolls = []
            for ng in self._group:
                cc = ng.nodelist()
                rr = MG_JEN_dataCollect.dcoll (ns, cc, 
                                               scope='', tag='',
                                               color=ng._plotinfo['color'],
                                               style=ng._plotinfo['style'],
                                               size=ng._plotinfo['size'],
                                               pen=ng._plotinfo['pen'],
                                               type='realvsimag', errorbars=True)
                dcolls.append(rr)
            # Make a combined plot of all the matrix elements:
            # NB: nodename -> dconc_scope_tag
            rr = MG_JEN_dataCollect.dconc(ns, dcolls,
                                          scope='', tag='', bookpage=None)
            # Return the dataConcat node:
            self._dcoll = rr['dcoll']
            JEN_bookmarks.create(self._dcoll, self.label(),
                                 page=bookpage, folder=folder)
        return self._dcoll


    #======================================================================

    def test(self):
        """Helper function to put in some standard entries for testing"""

        ng = NodeGroup(self._ns, 'first', color='red')
        ng.test(5, offset=0.1)
        ng.display()
        self.append_member(ng)

        ng = NodeGroup(self._ns, 'second', color='blue')
        ng.test(7, offset=0.2)
        ng.display()
        self.append_member(ng)
        
        return True











#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    ng1 = NodeGroup(ns, 'ng1')
    ng1.test()
    cc.append(ng1.visualize())
    cc.append(ng1.collector())
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
    domain = meq.domain(1.0e8,1.1e8,1,10)                          # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       
def _tdl_job_sequence (mqs, parent):
    """Execute the forest, starting at the named node"""
    for t0 in range(10):
        domain = meq.domain(1.0e8,1.1e8,t0+1,t0+10)                # (f1,f2,t1,t2)
        # print '- t0 =',t0,': domain =',domain
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
        ng1 = NodeGroup(ns, 'ng1', rider=dict(matrel='m22'))
        ng1.test()
        ng1.display()
        # print ng1.tabulate()
        if 0:
            dcoll = ng1.visualize()
            ng1.display_subtree (dcoll, txt='dcoll')

    if 0:
        ng2 = NodeGroup(ns, 'ng2', rider=dict(matrel=['m11','m21']))
        ng3 = NodeGroup(ns, 'ng3', rider=dict(matrel='m11'))
        gog = NodeGog(ns, 'gog', group=[ng1,ng2,ng3])
        gog.display()
        gog.merge_riders()
        gog.display()

    if 0:
        ng1.unop('Cos', replace=True)
        ng1.unop('Sin', replace=True)
        ng1.display()

    if 0:
        node = ng1.bundle()
        ng1.display_subtree (node, txt='bundle')

    if 1:
        node = ng1.collector()
        ng1.display_subtree (node, txt='coll')

    if 0:
        node = ng1.visualize()
        ng1.display_subtree (node, txt='visu')

    if 0:
        ng2 = NodeGroup(ns, 'ng2')
        ng2.test()
        if 1:
            ng2.binop('Divide', ng1, quals=['xxx','yy'], replace=True)
            ng2.display()
        if 0:
            node = ng2.compare(ng1, quals='888')
            ng1.display_subtree (node, txt='compare')
        

    if 0:
        cc = []
        cc = [ns << 45]
        ng2 = NodeGroup(ns, 'ng2', nodelist=cc, color='red')
        # ng2.test(6)
        ng2.display()

        if 0:
            ng2 = NodeGroup(ns, 'ng2')
            ng2.append_member(ss << 1.0)
            ng2.append_member(ss << 2.0)
            nn = ng2.nodelist(trace=True)
            ng2.display()

    #------------------------------------------------------------

    if 0:
        gog1 = NodeGog(ns, 'gog1')
        gog1.test()
        gog1.display()
        # print gog1.tabulate()

        if 1:
            gog1.visualize()
            gog1.display()

        if 0:
            node = gog1.bundle()
            gog1._dummyNodeGroup.display_subtree (node, txt='bundle')



#===============================================================
    
