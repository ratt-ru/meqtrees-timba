# file: ../Grunt/Matrixet22.py

# History:
# - 29dec2006: creation (extracted from Jones.py) 

# Description:

# The Matrixet22 class encapsulates a set of 2x2 matrices,
# e.g. Jones matrices, or cohaerency matrices. 

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

from ParmGroupManager import *
from Qualifiers import *

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
        self._quals = Qualifiers(quals, prepend=label)

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
            self._pgm = ParmGroupManager(ns, label=self.label(),quals=self.quals(),
                                         simulate=self._simulate)

        self._dummyParmGroup = ParmGroup('dummy')    # used for its printing functions...
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

    #-------------------------------------------------------------------

    def label(self):
        """Return the object label""" 
        return self._label

    def descr(self):
        """Return the object description""" 
        return self._descr

    def quals(self, append=None, prepend=None, exclude=None):
        """Return the nodename qualifier(s), with temporary modifications"""
        return self._quals.get(append=append, prepend=prepend, exclude=exclude)

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

    #-------------------------------------------------------------------

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

    #-------------------------------------------------------------------

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
                                                 recurse=2)
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
        print '**\n'
        return True




    #=====================================================================================
    # Math operations: 
    #=====================================================================================

    def binop(self, binop=None, other=None, qual=None):
        """Do an (item-by-item) binary operation (e.g. Subtract)
        between itself and another Matrixet22 object."""
        quals = self.quals(append=qual)
        qother = other._quals.concat()        # -> one string, with _ between quals
        for i in self.list_indices():
            self._ns[binop](*quals)(qother)(*i) << getattr(Meq,binop)(self._matrixet(*i),
                                                                     other._matrixet(*i))
        self.matrixet(new=self._ns[binop](*quals)(qother))     # replace
        self._pgm.merge(other._pgm)           # ...........!!?
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

    def visualize (self, qual=None, matrel='*', bookpage='Matrixet22', folder=None):
        """Visualise (a subset of) the 4 complex matrix elements of all 
        Matrixet22 matrices in a single real-vs-imag plot. Different
        matrix elements (m11,m12,m21,m22) have different styles
        and colors, which are the same for all Matrixet22 matrices."""
        dcoll_quals = self._quals.concat(append=qual)
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
        # Return the dataConcat node:
        return self._dcoll

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
        quals = self.quals(append=qual)
        qother = other._quals.concat()        # -> one string, with _ between quals

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
                c = self._ns.condeq(*quals)(qother)(*i) << Meq.Condeq(self._matrixet(*i),
                                                                      other._matrixet(*i))
                condeqs.append(c)
            if replace: self._matrixet = self._ns.condeq(*quals)(qother)   # replace 

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
                c = self._ns[name](*quals)(qother)(*i) << Meq.Condeq(node1, node2)
                condeqs.append(c)
        # Return a list of condeq nodes:
        return condeqs

    #----------------------------------------------------------------------------------

    def make_solver (self, other=None, parmgroup='*', qual=None, compare=None):
        """Make a solver that solves for the specified parmgroup, by comparing its
        matrices with the corresponding matrices of another Matrixet22 object."""
        quals = self.quals(append=qual)
        qother = other._quals.concat()        # -> one string, with _ between quals

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

        # Create the solver
        cc = []
        solver = self._ns.solver(*quals)(qother) << Meq.Solver(children=condeqs,
                                                         solvable=pg.nodelist())
        cc.append(solver)
        JEN_bookmarks.create(solver, page='solver')

        # Visualize the condeqs and the solvable MeqParms:
        cc.append(condeq_copy.visualize('solver', matrel=matrel))

        # Return the ReqSeq node that bundles solving and visualisation: 
        reqseq = self._ns.reqseq_solver(*quals)(qother) << Meq.ReqSeq(children=cc)
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
        for key in keys:
            index += 1
            indices.append(index)
            self._pgm.define_parmgroup(key, descr='matrix element: '+key,
                                       default=index/10.0,
                                       # stddev=0.01,
                                       tags=['test'])
            mm = dict(m11=0.0, m12=0.0, m21=0.0, m22=0.0)
            mm[key] = self._pgm.create_parmgroup_entry(key, index)
            mm[key] = self._ns << Meq.Polar(1.0,mm[key])
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
    cc.append(mat1.visualize())
    mat1.display(full=True)

    mat2 = Matrixet22(ns, quals=[], simulate=False)
    mat2.test()
    cc.append(mat2.visualize())
    mat2.display(full=True)

    if True:
        reqseq = mat1.make_solver(mat2)
        cc.append(reqseq)

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
        mc = m1.copy()
        mc.display('copy', full=True)

    if 0:
        m1.unop('Cos')
        m1.display('after unop', full=True)
        
    if 1:
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
    
