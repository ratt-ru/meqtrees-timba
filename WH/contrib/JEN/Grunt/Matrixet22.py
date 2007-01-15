# file: ../Grunt/Matrixet22.py

# History:
# - 29dec2006: creation (extracted from Jones.py)
# - 12jan2007: added .collector() visualization 

# Description:

# The Matrixet22 class encapsulates a set of 2x2 matrices,
# e.g. Jones matrices, or cohaerency matrices. 

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

from Timba.Contrib.JEN.Grunt import Qualifiers
from Timba.Contrib.JEN.Grunt import ParmGroup
from Timba.Contrib.JEN.Grunt import ParmGroupManager

from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect

from copy import deepcopy

#======================================================================================

class Matrixet22 (object):
    """Class that represents a set of 2x2 matrices.
    It is inherited by the Jones22 class and the Vis22 class.  
    It also contains a ParmGroupManager object that encapsulates
    groups of MeqParm nodes (or their simulation subtrees)."""

    def __init__(self, ns, quals=[], label='M', descr='<descr>',
                 matrixet=None, indices=[], pgm=False,
                 polrep=None, simulate=False):
        self._ns = ns                                # node-scope (required)
        self._label = label                          # label of the matrixet 
        self._descr = descr                          # decription of the matrixet 

        self._polrep = polrep                        # polarization representation (linear, circular)
        self._pols = ['A','B']
        if self._polrep == 'linear':
            self._pols = ['X','Y']
        elif self._polrep == 'circular':
            self._pols = ['R','L']

        # Node-name qualifiers:
        self._quals = Qualifiers.Qualifiers(quals, prepend=label)

        self._simulate = simulate                    # if True, use simulation subtrees (i.s.o. MeqParms)
        if self._simulate:
            self._quals.append('simul')

        self._matrixet = None                        # the actual matrices (contract!)
        self._indices = []                           # list of matrixet 'indices' (e.g. stations)
        self._list_indices = []                      # version where each item is a list
        self.matrixet(new=matrixet)                  # initialise, if matrixet specified
        self.indices(new=indices)                    # initialize, if indices specified

        # Matrixet22 matrix elements (contract!)
        self._matrel = dict(m11=None, m12=None, m21=None, m22=None)
        self._matrel_index = dict(m11=[0,0], m12=[0,1], m21=[1,0], m22=[1,1])

        # Visualization:
        self._dcoll = None
        self._matrel_style = dict(m11='circle', m12='xcross', m21='xcross', m22='circle')
        self._matrel_color = dict(m11='red', m12='magenta', m21='darkCyan', m22='blue')
        self._boolmark = dict()                      # JEN_SolverChain legacy.....

        # The (solvable and simulated) MeqParms are handled in named groups,
        # by a ParmGroupManager object. The latter may be supplied externally,
        # e.g. when interfacing with visibilities produced by the Meow system. 
        self._pgm = pgm
        if not self._pgm:
            self._pgm = ParmGroupManager.ParmGroupManager(ns, label=self.label(),
                                                          quals=self.quals(),
                                                          simulate=self._simulate)

        # Service: It is possible to accumulate lists of things (nodes, usually),
        # that are carried along by the object until needed downstream.
        self._accumulist = dict()

        # Kludge: used for its printing functions...
        self._dummyParmGroup = ParmGroup.ParmGroup('dummy')
        return None

    #-------------------------------------------------------------------

    def copy(self):
        """Return a (limited) copy of the current Matrixet22 object.
        For the moment, for limited use only."""
        # return deepcopy(self)..........................does not work...
        # self.display('copy(), before')
        new = Matrixet22(self._ns, quals=self.quals(),
                         label='copy('+self.label()+')',
                         descr=self.descr(),
                         matrixet=self.matrixet(),
                         indices=self.indices(),
                         simulate=self._simulate)
        # Not complete!!
        new._pgm.merge(self._pgm)                           # ...........!!?
        # self.display('copy(), after')
        # new.display('copy()')
        return new


    #=====================================================================================
    # Access to basic attributes:
    #=====================================================================================

    def label(self):
        """Return the object label""" 
        return self._label

    def descr(self):
        """Return the object description""" 
        return self._descr

    def quals(self, append=None, prepend=None, exclude=None, merge=None):
        """Return the nodename qualifier(s), with temporary modifications"""
        return self._quals.get(append=append, prepend=prepend,
                               exclude=exclude, merge=merge)

    #-------------------------------------------------------------------

    def polrep(self):
        """Return the polarization representation (linear, circular, None)"""
        return self._polrep

    def pols(self):
        """Return the list of 2 polarization names (e.g. ['X','Y'])"""
        return self._pols

    #-------------------------------------------------------------------

    def indices(self, new=None):
        """Get/set the list of (matrixet) indices"""
        if new:
            self._indices = new
            ii = []
            for i in self._indices:
                if not isinstance(i,(list,tuple)): i = [i]
                ii.append(i)
            self._list_indices = ii
        return self._indices

    def list_indices(self):
        """Get the list of (matrixet) indices, but in which each index is a list.
        See self.indices() above.
        This is to create uniformity between scalar indices (i.e. for stations) and
        list/tuple indices (i.e. for ifrs). This allows node indexing by (*i)...."""
        return self._list_indices

    def len(self):
        """Return the 'length' of the object, i.e. the number of matrices"""
        return len(self._indices)

    def matrixet(self, new=None):
        """Get/set the set of 2x2 matrices"""
        if new:
            self._matrixet = new
        return self._matrixet

    def nodelist(self):
        """Get/set a list of matrix nodes"""
        cc = []
        for i in self.list_indices():
            cc.append(self._matrixet(*i))
        return cc

    #=====================================================================================
    # Display of the contents of this object:
    #=====================================================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += '  '+str(self.label())
        ss += '  n='+str(len(self.indices()))
        ss += '  quals='+str(self.quals())
        # if self._simulate: ss += ' (simulate)'
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
        print '** Generic (class Matrixet22):'
        print ' * descr: '+str(self.descr())
        print ' * polrep: '+str(self._polrep)+', pols='+str(self._pols)
        print ' * Available indices ('+str(self.len())+'): ',
        if self.len()<30:
            print str(self.indices())
        else:
            print '\n   '+str(self.indices())
        print ' * Available list_indices ('+str(self.len())+'): ',
        if self.len()<30:
            print str(self.list_indices())
        else:
            print '\n   '+str(self.list_indices())
        #...............................................................
        print ' * Available 2x2 matrices ('+str(self.len())+'): '
        if self._matrixet:
            ii = self.list_indices()
            if len(ii)<10:
                for i in ii:
                    print '  - '+str(i)+': '+str(self.matrixet()(*i))
            else:                                             # too many matrices
                for i in ii[:2]:                              # show the first two
                    print '  - '+str(i)+': '+str(self.matrixet()(*i))
                print '         ......'
                ilast = ii[len(ii)-1]                         # and the last one
                print '  - '+str(i)+': '+str(self.matrixet()(*i))
            print ' * The first matrix of the set:'
            node = self.matrixet()(*self.list_indices()[0])
            self._dummyParmGroup.display_subtree(node, txt=str(0),
                                                 show_initrec=False,
                                                 recurse=3)
        #...............................................................
        ntot = len(self._pgm._parmgroup) + len(self._pgm._simparmgroup)
        print ' * Available NodeGroup/NodeGog objects ('+str(ntot)+'): '
        for key in self._pgm._parmgroup.keys():
            print '  - '+str(self._pgm._parmgroup[key].oneliner())
        for key in self._pgm._simparmgroup.keys():
            print '  - (sim) '+str(self._pgm._simparmgroup[key].oneliner())
        #...............................................................
        print ' * Extracted (sets of) matrix elements: '
        for key in self._matrel.keys():
            print '  - '+str(key)+': '+str(self._matrel[key])
        #...............................................................
        print ' * Visualization subtree: '
        if self._dcoll:
            self._dummyParmGroup.display_subtree(self._dcoll, txt=':',
                                                 show_initrec=False, recurse=1)
        print '   - matrel_index: '+str(self._matrel_index)
        print '   - matrel_color: '+str(self._matrel_color)
        print '   - matrel_style: '+str(self._matrel_style)
        #...............................................................
        print ' * Accumulist entries: '
        for key in self._accumulist.keys():
            vv = self._accumulist[key]
            print '  - '+str(key)+' ('+str(len(vv))+'):'
            if full:
                for v in vv: print '    - '+str(type(v))+' '+str(v)
        #...............................................................
        print '**\n'
        return True


    #=====================================================================================
    # Accumulist service:
    #=====================================================================================

    def accumulist (self, item=None, key=None, flat=False, clear=False):
        """Interact with the internal service for accumulating named (key) lists of
        items (nodes, usually), for retrieval later downstream.
        If flat=True, flatten make a flat list by extending the list with a new item
        rather than appending it.
        An extra list with key=* contains all items of all lists"""
        if key==None: key = '_default_'
        if not isinstance(key, str):
            print '\n** .accumulist(): key is wrong type:',type(key),'\n'
            return False      
        self._accumulist.setdefault(key, [])           # Make sure that the list exists
        self._accumulist.setdefault('*', [])           # The list of ALL entries
        if item:
            if not flat:                                                                  
                self._accumulist[key].append(item)
                self._accumulist['*'].append(item)
            elif isinstance(item, (list,tuple)):
                self._accumulist[key].extend(item)
                self._accumulist['*'].extend(item)
            else:
                self._accumulist[key].append(item)
                self._accumulist['*'].append(item)
        # Always return the current value of the specified (key) list:
        keylist = self._accumulist[key]           
        if clear:
            # Optional: clear the entry (NB: What happens to '*' list??)
            self._accumulist[key] = []
            # self._accumulist['*'] = []
        # Enhancement: If flat=True, flatten the keylist....?
        return keylist


    def merge_accumulist (self, other):
        """Merge the accumulist of another Matrix22 object with its own."""
        olist = other._accumulist
        for key in olist.keys():
            if not key=='*':
                self.accumulist(olist[key], key=key, flat=True)
        return True

    #=====================================================================================
    # Matrix elements within the 2x2 matrices:
    #=====================================================================================

    def matrels (self):
        """Return the list of the (4) matrix element names"""
        return self._matrel.keys()


    def matrix_element(self, key='m11', qual=None, return_nodes=False, trace=False):
        """Return the specified matrix element(s)"""
        if not self._matrel.has_key(key):
            return False                                # in ['m11','m12','m21','m22']

        quals = self.quals(append=qual)
        name = self.label()+'_'+key[1:]                 # i.e. '12' rather than 'm12'
        if trace: print '\n**',key,name,quals
        if not self._ns[name](*quals).initialized():
            for i in self.list_indices():
                index = self._matrel_index[key]         # index in tensor node
                node = self._ns[name](*quals)(*i) << Meq.Selector(self._matrixet(*i),
                                                                  index=index)
                if trace: print '-+',i,index,self._matrixet(*i),'->',node
        self._matrel[key] = self._ns[name](*quals)      # keep for inspection etc

        # Return a list of nodes, if required:
        if return_nodes:
            nodes = []
            for i in self.list_indices():
                nodes.append(self._ns[name](*quals)(*i))
            return nodes
        # Otherwise, return the set of nodes:
        return self._ns[name](*quals) 


    #=====================================================================================
    # Math operations: 
    #=====================================================================================

    def binop(self, binop=None, other=None, qual=None, visu=False):
        """Do an (item-by-item) binary operation (e.g. Subtract)
        between itself and another Matrixet22 object."""
        quals = self.quals(append=qual, merge=other.quals())
        for i in self.list_indices():
            self._ns[binop](*quals)(*i) << getattr(Meq,binop)(self._matrixet(*i),
                                                              other._matrixet(*i))
        self.matrixet(new=self._ns[binop](*quals))            # replace
        # self._pgm.merge(other._pgm)           # ...........!!?
        if visu: self.visualize(qual=qual)
        return True


    def unop(self, unop=None, qual=None):
        """Do an (item-by-item) unary operation on itself (e.g. Abs)"""
        quals = self.quals(append=qual)
        for i in self.list_indices():
            self._ns[unop](*quals)(*i) << getattr(Meq,unop)(self._matrixet(*i))
        self.matrixet(new=self._ns[unop](*quals))              # replace
        return True

    #---------------------------------------------------------------------

    def bundle(self, oper='Composer', qual=None):
        """Bundle its matrices, using an operation like Composer, Add, Multiply etc"""
        quals = self.quals(append=qual)
        if not self._ns.bundle(oper)(*quals).initialized():
            cc = []
            for i in self.list_indices():
                cc.append(self._matrixet(*i))
            self._ns.bundle(oper)(*quals) << getattr(Meq,oper)(children=cc)
        return self._ns.bundle(oper)(*quals)



    #=====================================================================
    # Visualization:
    #=====================================================================

    def _dcoll_quals(self, qual=None):
        """Helper function"""
        dcoll_quals = self._quals.concat()
        if qual:
            if not isinstance(qual,(list,tuple)): qual = [qual]
            qual.reverse()
            for q in qual:
                dcoll_quals = q+'_'+dcoll_quals                 # prepend
        return dcoll_quals

    #.......................................................................

    def visualize (self, qual=None, matrel='*', accu=True,
                   bookpage='Matrixet22', folder=None):

        """Visualise (a subset of) the 4 complex matrix elements of all 
        Matrixet22 matrices in a single real-vs-imag plot. Different
        matrix elements (m11,m12,m21,m22) have different styles
        and colors, which are the same for all Matrixet22 matrices.
        A bookmark item is made for the resulting dataCollect node.
        The resulting dataCollect node is returned, but if accu=True (default)
        it is also stored in self.accumulist(key=None) for later retrieval."""

        dcoll_quals = self._dcoll_quals(qual=qual)             # temporary...

        dcolls = []
        keys = deepcopy(matrel)
        if keys=='*': keys = self._matrel.keys()              # i.e. ['m11','m12','m21','m22']
        if not isinstance(keys,(list,tuple)): keys = [keys]
        for key in keys:  
            cc = self.matrix_element(key, qual=qual, return_nodes=True) 
            rr = MG_JEN_dataCollect.dcoll (self._ns, cc, 
                                           scope=dcoll_quals,
                                           tag=key,
                                           color=self._matrel_color[key],
                                           style=self._matrel_style[key],
                                           size=8, pen=2,
                                           type='realvsimag', errorbars=True)
            dcolls.append(rr)

        # Make a combined plot of all the matrix elements:
        # NB: nodename -> dconc_scope_tag
        rr = MG_JEN_dataCollect.dconc(self._ns, dcolls, scope=dcoll_quals,
                                      tag=' ', bookpage=None)
        self._dcoll = rr['dcoll']
        JEN_bookmarks.create(self._dcoll, self.label(),
                             page=bookpage, folder=folder)
        # Keep the dcoll node for later retrieval (e.g. attachment to reqseq):
        if accu: self.accumulist(self._dcoll)
        # Return the dataConcat node:
        return self._dcoll

    #--------------------------------------------------------------------------

    def collector (self, qual=None, accu=True,
                   bookpage='Matrixet22', folder=None):

        """Visualise (a subset of) the complex matrix elements of all 
        Matrixet22 matrices in a single collector plot.
        A bookmark item is made for the resulting collector node.
        If accu=True (default) it is also stored in self.accumulist(key=None)
        for later retrieval."""

        coll_quals = self._dcoll_quals(qual=qual)             # temporary...

        cc = self.nodelist()
        for i in range(len(cc)):
            cc[i] = self._ns << Meq.Mean (cc[i], reduction_axes="freq")
        name = 'collector'
        coll = self._ns[name](coll_quals) << Meq.Composer(dims=[self.len(),2,2],
                                                          children=cc)
        JEN_bookmarks.create(coll, self.label(),
                             viewer='Collections Plotter',
                             udi='/node/collector',
                             page=bookpage, folder=folder)
        # Keep the dcoll node for later retrieval (e.g. attachment to reqseq):
        if accu: self.accumulist(coll)
        # Return the collector node:
        return coll


    #--------------------------------------------------------------------------

    def collector_separate (self, qual=None, matrel='*', accu=True,
                            bookpage='Matrixet22', folder=None):

        """Visualise (a subset of) the complex matrix elements of all 
        Matrixet22 matrices in a separate collector plot per element.
        A bookmark item is made for the resulting collector nodes.
        If accu=True (default) they are also stored in self.accumulist(key=None)
        for later retrieval. A list of collector nodes is returned."""

        coll_quals = self._dcoll_quals(qual=qual)             # temporary...

        colls = []
        keys = deepcopy(matrel)
        if keys=='*': keys = self._matrel.keys()              # i.e. ['m11','m12','m21','m22']
        if not isinstance(keys,(list,tuple)): keys = [keys]
        for key in keys:  
            cc = self.matrix_element(key, qual=qual, return_nodes=True)
            for i in range(len(cc)):
                cc[i] = self._ns << Meq.Mean (cc[i], reduction_axes="freq")
            name = 'collector_'+key
            coll = self._ns[name](coll_quals) << Meq.Composer(dims=[len(cc)], children=cc)
            JEN_bookmarks.create(coll, self.label()+key,
                                 viewer='Collections Plotter',
                                 udi='/node/collector',
                                 page=bookpage, folder=folder)
            # Keep the dcoll node for later retrieval (e.g. attachment to reqseq):
            if accu: self.accumulist(coll)
            colls.append(coll)
        # Return the list of collector nodes:
        return colls



    #............................................................................
    # Obsolete? To JEN_bookmarks?
    #............................................................................

    def append_to_bookpage(self, node, page):
        """Append the given node to the specified bookpage"""
        self._bookmark.setdefault(page, [])
        self._bookmark[page].append(node)
        return True

    def make_actual_bookmarks(self):
        """Make the actual bookmarks from the accumulated info"""
        for key in self._bookmark.keys():
            JEN_bookmarks.create(self._bookmark[key], 'sc_'+key)
        return True


    #==============================================================================
    # Solving:
    #==============================================================================

    def make_condeqs (self, other=None, matrel='*', qual=None, replace=False):
        """Make a list of condeq nodes by comparing its matrices (or -elements)
        with the corresponding matrices of another Matrixet22 object."""
        quals = self.quals(append=qual, merge=other.quals())

        # It is possible to use only a subset of the matrix elements:
        keys = self._matrel.keys()            # i.e. ['m11','m12','m21','m22']
        mel = deepcopy(matrel)
        if mel=='*': mel = keys
        if not isinstance(mel,(list,tuple)): mel = [mel]
        index = []
        postfix = ''
        for i in range(len(keys)):
            if keys[i] in mel:
                index.append(i)
                postfix += '_'+str(i)

        # First make condeq nodes for all 4 matrix elements:
        # These are used for visualisation later (if replace=True)
        if replace or (len(index)==4):
            condeqs = []
            for i in self.list_indices():
                c = self._ns.condeq(*quals)(*i) << Meq.Condeq(self._matrixet(*i),
                                                              other._matrixet(*i))
                condeqs.append(c)
            if replace: self._matrixet = self._ns.condeq(*quals)   

        # If a subset of the matrix elements is required, generate a new set of condeqs,
        # which contain the relevant selections.
        if len(index)<4:
            condeqs = []
            name = 'condeq'+postfix
            name1 = 'lhs'+postfix
            name2 = 'rhs'+postfix
            for i in self.list_indices():
                node1 = self._matrixet(*i)
                node2 = other._matrixet(*i)
                node1 = self._ns[name1].qadd(node1) << Meq.Selector(node1, index=index)
                node2 = self._ns[name2].qadd(node2) << Meq.Selector(node2, index=index)
                c = self._ns[name](*quals)(*i) << Meq.Condeq(node1, node2)
                condeqs.append(c)
        # Return a list of condeq nodes:
        return condeqs

    #----------------------------------------------------------------------------------

    def make_solver (self, other=None, parmgroup='*', qual=None, num_iter=3):
        """Make a solver that solves for the specified parmgroup, by comparing its
        matrices with the corresponding matrices of another Matrixet22 object."""

        quals = self.quals(append=qual, prepend=parmgroup, merge=other.quals())

        # Accumulate nodes to be executed sequentially later:
        self.merge_accumulist(other)

        # Get the list of solvable MeqParm nodes:
        # ONLY from the other Matrixet22 object, NOT from this one.....(?)
        # keys = other.pgm().solvable_groups()
        if not other._pgm._parmgroup.has_key(parmgroup):
            print '** parmgroup (',parmgroup,') not recognised in:',other._pgm._parmgroup.keys()
            return False
        pg = other._pgm._parmgroup[parmgroup]
        solvable = pg.nodelist()

        # Get the names of the (subset of) matrix elements to be used:
        # (e.g. for GJones, we only use ['m11','m22'], etc)
        matrel = self._matrel.keys()          # i.e. ['m11','m12','m21','m22']
        #===================================================
        if False:
            # Gives some problems: condeqs with condeq children.....?
            matrel = pg.rider('matrel')
            if matrel=='*': matrel = self._matrel.keys()
        # matrel = ['m11','m22']
        #===================================================

        # Make a list of condeq nodes:
        condeq_copy = self.copy()
        condeqs = condeq_copy.make_condeqs (other, matrel=matrel,
                                            qual=qual, replace=True)


        # Create the solver:

        # The solver writes (the stddev of) its condeq resunts as ascii
        # into a debug-file (SBY), for later visualisation.
        # - all lines start with the number of entries (one per condeq)
        # - the first line has the condeq names (solver children)
        # - the rest of the lines have one ascii number per condeq
        # - Q: the solver writes a line at each iteration...? 
        # NB: the extension can be chosen at will, for identification
        debug_file = 'debug_'+str(qual)+'.ext'

        solver = self._ns.solver(*quals) << Meq.Solver(children=condeqs,
                                                       solvable=pg.nodelist(),
                                                       # debug_file=debug_file,
                                                       # parm_group=hiid(parm_group),
                                                       # child_poll_order=cpo,
                                                       num_iter=num_iter)

        # Bundle (cc) the solver and its related visualization dcolls
        # for attachment to a reqseq (below). Also make bookmarks to
        # display the same nodes on the same bookpage in the browser.
        
        cc = []
        cc.append(solver)
        bookpage = 'solver'+parmgroup
        JEN_bookmarks.create(solver, page=bookpage)

        # Visualize the solvable MeqParms:
        
        # Visualize the condeqs:
        condequal = 'condeq'
        if isinstance(qual,(list,tuple)):
            condequal = qual
            condequal.insert(0,'condeq')
        elif isinstance(qual,str):
            condequal = ['condeq',qual]
        dcoll = condeq_copy.visualize(condequal, matrel=matrel, bookpage=bookpage)
        # JEN_bookmarks.create(dcoll, page=bookpage)
        cc.append(dcoll)

        # Bundle solving and visualisation nodes: 
        reqseq = self._ns.reqseq_solver(*quals) << Meq.ReqSeq(children=cc)
        self.accumulist(reqseq)

        # Return the solver reqseq (usually not used):
        return reqseq
        
    

    #=====================================================================
    # Test module:
    #=====================================================================

    def test (self):
        """Helper function to make some test-matrices"""
        quals = self.quals()
        name = 'matrix22'
        keys = self._matrel.keys()
        index = 0
        indices = []
        # Make 4 matrices in which all but one of the elements is zero (real).
        # The one non-zero element is a different one in each matrix.
        for key in keys:                           # keys=['m11','m12','m21','m22']
            index += 1
            indices.append(index)
            self._pgm.define_parmgroup(key, descr='matrix element: '+key,
                                       default=index/10.0,
                                       # stddev=0.01,
                                       tags=['test'])
            mm = dict(m11=0.0, m12=0.0, m21=0.0, m22=0.0)
            for elem in keys:
                mm[elem] = self._ns << Meq.Polar(1.0, 0.0)
            # The one non-zero element is complex, with amplitude=1.0,
            # and phase equal to index/10 radians (plus variation if simulate=True):
            phase = self._pgm.create_parmgroup_entry(key, index)
            mm[key] = self._ns << Meq.Polar(1.0, phase)
            mat = self._ns[name](*quals)(index) << Meq.Matrix22(mm['m11'],mm['m12'],
                                                                mm['m21'],mm['m22'])
        # Store the matrices and the list if indices:
        self.indices(new=indices)
        self.matrixet(new=self._ns[name](*quals))

        # Make some secondary (composite) ParmGroups:
        self._pgm.define_gogs()
        return True







     
#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []
    simulate = True

    mat1 = Matrixet22(ns, quals=[], simulate=True)
    mat1.test()
    mat1.visualize()
    mat1.collector()
    mat1.display(full=True)

    mat2 = Matrixet22(ns, quals=[], simulate=False)
    mat2.test()
    mat2.visualize()
    mat2.display(full=True)

    if False:
        reqseq = mat1.make_solver(mat2)
        # cc.append(reqseq)

    aa = mat1.accumulist()
    aa.extend(mat2.accumulist())
    print 'aa=',aa
    node = ns.accu << Meq.Composer(children=aa)
    cc.append(node)

    ns.result << Meq.ReqSeq(children=cc)
    return True

#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       
def _tdl_job_sequence (mqs, parent):
    """Execute the forest, starting at the named node"""
    for t0 in range(10):
        domain = meq.domain(1.0e8,1.1e8,t0+1,t0+10)                  # (f1,f2,t1,t2)
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
        m1 = Matrixet22(ns, quals=['3c84','xxx'], label='HH', simulate=True)
        m1.test()
        m1.visualize()
        m1.display(full=True)

    if 0:
        m1.accumulist('aa')
        m1.accumulist('2')
        m1.accumulist(range(3), flat=True)
        m1.accumulist('bb', key='extra')
        m1.display(full=True)
        print '1st time:',m1.accumulist()
        print '1st time*:',m1.accumulist(key='*')
        print '2nd time:',m1.accumulist(clear=True)
        print '3rd time:',m1.accumulist()

    if 0:
        mc = m1.copy()
        mc.display('copy', full=True)

    if 0:
        m1.unop('Cos')
        m1.display('after unop', full=True)
        
    if 0:
        m2 = Matrixet22(ns, quals=['3c84','yyy'], label='TT', simulate=False)
        m2.test()
        m2.display('m2',full=True)

        if 0:
            m1.binop('Subtract',m2)
            m1.display('after binop', full=True)
        
        if 1:
            reqseq = m1.make_solver(m2)
            m1._dummyParmGroup.display_subtree (reqseq, txt='solver_reqseq',
                                                show_initrec=False, recurse=3)
        
        if 0:
            mc = m1.copy()
            matrel = '*'
            matrel = ['m11','m22']
            cc = mc.make_condeqs(m2, matrel=matrel, replace=True)
            print ' -> nr of condeqs:',len(cc)
            for i in range(4):
                mc._dummyParmGroup.display_subtree (cc[i], txt='condeq'+str(i), recurse=2)
            mc.visualize(matrel=matrel)
            mc.display('make_condeqs', full=True)
            # m1.display('make_condeqs', full=True)
        

    if 0:
        nn = m1.matrix_element(return_nodes=False)
        m1.display(full=True)
        print '\n** matrix_element result:'
        for s in m1.indices():
            print '--',s,':',nn(s)
        print '-- (',6,'):',nn(6)     # !!
        print
        nn = m1.matrix_element(return_nodes=True)

    if 0:
        m1.matrix_element('m11')
        m1.matrix_element('m12')
        m1.matrix_element('m21')
        m1.matrix_element('m22')
        m1.display(full=True)


#===============================================================
    
