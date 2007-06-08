# file: ../Grunt/Matrixet22.py

# History:
# - 29dec2006: creation (extracted from Jones.py)
# - 12jan2007: added .show_timetracks() visualization
# - 19jan2007: removed make_condeqs() and make_solver()
# - 21jan2007: re-implemented .extract_matrel_nodes()
# - 23feb2007: allow key list in .extract_matrel_nodes()
# - 26mar2007: adapted for QualScope.py
# - 04jun2007: adapt for NodeList.py
# - 04jun2007: derive from ParameterizationPlus.py

# Description:

# The Matrixet22 class encapsulates a set of 2x2 matrices,
# e.g. Jones matrices, or cohaerency matrices. 

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

from Timba.Contrib.JEN.Grunt import NodeList
from Timba.Contrib.JEN.Grunt import ParameterizationPlus
from Timba.Contrib.JEN.Grunt import display
from Timba.Contrib.JEN.Grunt import ObjectHistory

import Meow

# from Timba.Contrib.JEN.util import JEN_bookmarks
# from Timba.Contrib.JEN import MG_JEN_dataCollect

from copy import deepcopy

#======================================================================================

class Matrixet22 (ParameterizationPlus.ParameterizationPlus):
    """Class that represents a set of 2x2 matrices.
    It is inherited by the Jones22 class and the Vis22 class.  
    It is derived from the ParameterizationPlus class, which
    encapsulates groups of MeqParm nodes (or their simulation subtrees).
    """

    def __init__(self, ns, name='M', quals=[], kwquals={},
                 descr='<descr>',
                 matrixet=None, indices=[],
                 polrep=None):
        
        ParameterizationPlus.ParameterizationPlus.__init__(self, ns, name,
                                                           quals=quals,
                                                           kwquals=kwquals)

        self._descr = descr                          # decription of the matrixet 

        # Polarization representation (linear, circular)
        self._polrep = polrep
        self._pols = ['A','B']
        matrix_elements = ['AA','AB','BA','BB']
        if self._polrep == 'linear':
            self._pols = ['X','Y']
            matrix_elements = ['XX','XY','YX','YY']
        elif self._polrep == 'circular':
            self._pols = ['R','L']
            matrix_elements = ['RR','RL','LR','LL']

        # Define matrix element names and plotting instructions (see make_NodeList()):
        self._matrix_elements = dict(name=matrix_elements,
                                     color=['red','magenta','darkCyan','blue'],
                                     style=['circle','xcross','xcross','circle'],
                                     size=[10,10,10,10], pen=[2,2,2,2])

        # Various counters, e.g. for unique name generation:                               
        self._counter = dict()

        # At each stage, all matrix nodes are replaced by a parent.
        # The stage naming information is kept in a dict():
        self._stage = dict(char='@', count=-1)
        self._nextstage(self.name)

        # The actual 2x2 matrixes:
        self._matrixet = None                        # the actual matrices (contract!)
        self._indices = []                           # list of matrixet 'indices' (e.g. stations)
        self._list_indices = []                      # version where each item is a list
        self.matrixet(new=matrixet)                  # initialise, if matrixet specified
        self.indices(new=indices)                    # initialize, if indices specified

        # Visualization:
        self._dcoll = None

        # Service: It is possible to accumulate lists of things (nodes, usually),
        # that are carried along by the object until needed downstream.
        self._accumulist = dict()

        # Attach an object to collect the object history:
        self._hist = ObjectHistory.ObjectHistory(self.name, parent=self.oneliner())

        return None

    #-------------------------------------------------------------------

    def copy(self):
        """Return a (limited) copy of the current Matrixet22 object.
        For the moment, for limited use only."""
        raise ValueError,'.....copy() not really implemented...'
        # return deepcopy(self)..........................does not work...
        # self.display('copy(), before')
        new = Matrixet22(self.ns,
                         name='copy('+self.name+')',
                         descr=self.descr(),
                         matrixet=self.matrixet(),
                         indices=self.indices())
        # Not complete!!
        # new._pgm.merge(self._pgm)                           # ...........!!?
        # self.display('copy(), after')
        # new.display('copy()')
        return new


    #=====================================================================================
    # Access to basic attributes:
    #=====================================================================================

    def descr(self):
        """Return the object description""" 
        return self._descr

    def history(self, append=None, subappend=None, subsubappend=None, ns=None):
        """Return its ObjectHistory object. Optionally, append an item.
        The sub and subsub prefixes offer some standard indentation.
        If a nodescope/qualscope is specified, its qualifiers will be shown.""" 
        if ns==None: ns = self.ns
        if append: self._hist.append(append, ns=ns)
        if subappend: self._hist.subappend(subappend, ns=ns)
        if subsubappend: self._hist.subsubappend(subsubappend, ns=ns)
        # Return the ObjectHistory object:
        return self._hist

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

    #-------------------------------------------------------------------------

    def make_NodeList(self, quals=None, trace=False):
        """Put the current matrix nodes into a NodeList object"""
        # First make lists of nodes and labels:
        nodes = []
        labels = []
        for i in self.list_indices():
            nodes.append(self._matrixet(*i))
            label = str(i[0])
            if len(i)>1: label += '_'+str(i[1])
            labels.append(label)

        # Then make the NodeList object with automatic names/quals
        ss = self._stage
        qq = ss['quals']
        if quals:
            # Some extra quals specified:
            if isinstance(quals,(list,tuple)):
                qq.extend(quals)
            else:
                qq.append(quals)
        name = self.name
        if ss['name'][0]==ss['char']:
            name += '_'+ss['name']
        nn = NodeList.NodeList(self.ns, name,
                               quals=qq, kwquals=ss['kwquals'],
                               nodes=nodes, labels=labels)

        # Provide information about the 4 matrix elements (for plotting etc):
        rr = self._matrix_elements
        nn.tensor_elements(rr['name'], color=rr['color'], style=rr['style'],
                           size=rr['size'], pen=rr['pen'])
        if trace: nn.display('make_NodeList()')
        return nn

    #-------------------------------------------------------------------------

    def _nextstage (self, name=None, quals=None, kwquals=None, other=None):
        """Helper function to increment the stage information."""

        # Make sure that (kw)quals have the correct type: 
        if quals==None: quals = []
        if isinstance(quals,str): quals = quals.split(' ')
        quals = list(quals)
        if not isinstance(kwquals,dict): kwquals = dict()

        # Whenever the matrix nodes are replaced by a new parent,
        # this is called a stage. This is part of the node names.
        self._stage['count'] += 1
        self._stage['stage'] = self._stage['char']+str(self._stage['count'])  # e.g. 'M3'

        # If another Matrixet22 object is involved:
        if isinstance(other, Matrixet22):
            # Merge its ns qualifiers?
            quals.append(other.name)

        # Add the stage-string to the name or the quals:
        # This avoids inadvertent node-name clashes.
        if not isinstance(name,str):
            name = 'stage_'+self._stage['stage']
        elif self._stage['count']>0:
            quals.append(self._stage['stage'])
        self._stage['qnode'] = self.ns[name](*quals,**kwquals)
        self._stage['sqnode'] = str(self._stage['qnode'])

        # Keep the stage information for later reference:
        self._stage['name'] = name
        self._stage['quals'] = quals
        self._stage['kwquals'] = kwquals

        # Return the stage-dict:
        return self._stage

    #-------------------------------------------------------------------------

    def nodelist(self):
        """Get/set a list of matrix nodes"""
        nodes = []
        for i in self.list_indices():
            nodes.append(self._matrixet(*i))
        return nodes

    def firstnode(self):
        """Return the first of the matrixet nodes"""
        if not self._matrixet: return None
        node = self.matrixet()(*self.list_indices()[0])
        return node

    def basename(self):
        """Return the basename (i.e. nodename without qualifiers) of the matrixet nodes"""
        if not self._matrixet: return None
        return self.firstnode().basename


    #=====================================================================================
    # Display of the contents of this object:
    #=====================================================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += '  '+str(self.name)
        ss += '  n='+str(len(self.indices()))
        ss += '  ('+str(self.ns['<nodename>'].name)+')'
        return ss

    def display_ParmGroupManager(self, full=False):
        """Print a summary of the ParmGroupManager of this object"""
        self.p_display()
        return True 

    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        # NB: This function is called in .display().
        #     It should be re-implemented in a derived class.
        return True

    def display(self, txt=None, full=False, recurse=3):
        """Print a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print ' * (txt='+str(txt)+')'
        self.display_specific(full=full)
        print '** Generic (class Matrixet22):'
        print ' * descr: '+str(self.descr())
        print ' * polrep: '+str(self._polrep)+', pols='+str(self._pols)
        print ' * stage: '+str(self._stage)
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
        print ' * Available matrices (matrixet='+str(self._matrixet)+'):'
        if self._matrixet:
            ii = self.list_indices()
            if len(ii)<10:
                for i in ii:
                    print '  - '+str(i)+': '+str(self.matrixet()(*i))
            else:                                             # too many matrices
                for i in ii[:2]:                              # show the first two
                    print '  - '+str(i)+': '+str(self.matrixet()(*i))
                print '         ......'
                i = ii[len(ii)-1]                             # and the last one
                print '  - '+str(i)+': '+str(self.matrixet()(*i))
            print ' * The first matrix22 of the set:'
            node = self.firstnode()
            display.subtree(node, txt='first',
                            recurse=recurse,
                            show_initrec=False,
                            skip_line_before=False,
                            skip_line_after=False)
        #...............................................................
        print ' * The (last) result of .visualize() ('+str(self._dcoll)+'):'
        if self._dcoll:
            display.subtree(self._dcoll, txt='visual',
                            show_initrec=False,
                            skip_line_before=False,
                            skip_line_after=False,
                            recurse=1)
        #...............................................................
        print ' * Accumulist entries: '
        for key in self._accumulist.keys():
            vv = self._accumulist[key]
            print '  - '+str(key)+' ('+str(len(vv))+'):'
            if full:
                for v in vv: print '    - '+str(type(v))+' '+str(v)
        #...............................................................
        print ' * Matrix_elements: '+str(self._matrix_elements)
        if self._counter:
            print ' * Counter(s): '+str(self._counter)
        self.p_display(full=full)
        #...............................................................
        print '**\n'
        return True


    #--------------------------------------------------------------------------

    def show_matrix_subtree (self, index='*', recurse=2, show_initrec=False):
        """Helper function for closer inspection of the specified matrix(es)"""
        print '\n** matrix subtrees of: ',self.oneliner(),'\n'
        if index=='*': index = self.list_indices()
        for ii in index:
            node = self._matrixet(*ii)
            display.subtree(node, txt=str(ii),
                            show_initrec=show_initrec,
                            recurse=recurse)
            print
        return True
        


    #=====================================================================================
    # Accumulist service (separate class?):
    #=====================================================================================

    def accumulist (self, item=None, key=None, flat=False, clear=False):
        """Interact with the internal service for accumulating named (key) lists of
        items (nodes, usually), for later retrieval downstream.
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

    #---------------------------------------------------------------------

    def bundle_accumulist(self, quals=None):
        """Bundle the nodes in self._accumulist with a reqseq"""
        cc = self.accumulist(clear=False)
        n = len(cc)
        if n==0: return None
        if n==1: return cc[0]
        ns = self.ns._derive(append=quals)
        self.history('.bundle_accumulist()', ns=ns)
        if not ns.bundle_accumulist.initialized():
            ns.bundle_accumulist << Meq.ReqSeq(children=cc,
                                               result_index=n-1)
        return ns.bundle_accumulist

    #---------------------------------------------------------------------------

    def merge_accumulist (self, other):
        """Merge the accumulist of another Matrix22 object with its own."""
        self.history('.merge_accumulist()')
        olist = other._accumulist
        for key in olist.keys():
            if not key=='*':
                self.accumulist(olist[key], key=key, flat=True)
        return True


    #=====================================================================================
    # Math operations: 
    #=====================================================================================

    def binop(self, binop=None, other=None, quals=None, visu=False):
        """Do an (item-by-item) binary operation (e.g. Subtract)
        between itself and another Matrixet22 object."""
        qnode = self._nextstage(name=binop, quals=quals, other=other)['qnode']
        for i in self.list_indices():
            qnode(*i) << getattr(Meq,binop)(self._matrixet(*i),
                                            other._matrixet(*i))
        self.matrixet(new=qnode)                                     # replace
        # Transfer any parmgroups from other:
        # self.p_merge(other)
        if visu: self.visualize(['binop',binop], quals=quals, visu=visu)
        return True


    def unop(self, unop=None, quals=None, visu=False):
        """Do an (item-by-item) unary operation on itself (e.g. Abs)"""
        qnode = self._nextstage(name=unop, quals=quals)['qnode']
        self.history('.unop('+str(unop)+')')
        for i in self.list_indices():
            qnode(*i) << getattr(Meq,unop)(self._matrixet(*i))
        self.matrixet(new=qnode)                                     # replace
        if visu: self.visualize(['unop',unop], quals=quals, visu=visu)
        return True

    #---------------------------------------------------------------------

    def bundle(self, oper='Composer', quals=[]):
        """Bundle its matrices, using an operation like Composer, Add,
        Multiply, WMean, etc."""
        nn = self.make_NodeList(quals=quals)
        bundle = nn.bundle(oper)
        # if oper=='Composer':
            # Append a reqseq of self._accumulist nodes (if any):
        #    accuroot = self.bundle_accumulist(quals=quals)
        #    if accuroot: cc.append(accuroot)
        return bundle

    #---------------------------------------------------------------------

    def mean(self, quals=None):
        """Return a single node with the mean of all 2x2 matrices"""
        return self.bundle('WMean', quals=quals)


    #=====================================================================
    # Visualization:
    #=====================================================================


    def visualize (self, visu='rvsi', quals=None,
                   accu=True, separate=False,
                   bookpage='Matrixet22', folder=None):
        """Generic visualisation, controlled by visu. The latter may be:
        - timetracks: show timetracks for all matrices, averaged over freq.
        - spectra:    show spectra (not implemented yet)
        - rvsi:       show a real-vs-imag plot, refreshed per timeslot
        - straight:   show a selection of the matrices....
        visu==True means visu=='rvsi'
        visu may also be a list (of strings)
        """
        
        # Decode visu:
        if isinstance(visu, bool):
            if visu==False: return False
            visu = ['rvsi']
        elif isinstance(visu, str):
            if visu=='*':
                visu = ['rvsi','spectra','timetracks']
            else:
                visu = [visu]
        elif not isinstance(visu,(list,tuple)):
            return False

        # Make a NodeList object:
        nn = self.make_NodeList(quals=quals)

        dcolls = []
        for visual in visu:
            if visual=='timetracks':
                dc = nn.inspector()
                dcolls.append(dc)
            elif visual=='straight':
                nn.bookpage(4)
            elif visual=='spectra':
                dc = nn.spectra()
                dcolls.append(dc)
            else:
                dc = nn.rvsi()
                dcolls.append(dc)
                
        # Return a single node (bundle if necessary):
        if len(dcolls)==0:
            self._dcoll = None
            return False
        elif len(dcolls)==1:
            if accu: self.accumulist(dcolls[0])
            self._dcoll = dcolls[0]                  # for .display() only
            return dcolls[0]
        else:
            bundle = self.ns['visu_bundle'] << Meq.Composer(children=dcolls)
            if accu: self.accumulist(bundle)
            self._dcoll = bundle                     # for .display() only
            return bundle

    #-------------------------------------------------------------------------

    def bookpage (self, select=9, page=None, folder=None):
        """Make a page of bookmarks for (a selection of) the nodes of
        this NodeList object. Nothing is returned, because the bookmarks
        just publish the selected nodes as they are doing their thing."""
        nn = self.make_NodeList()
        nn.bookpage (select=select, page=page, folder=folder)
        nn.display('Matrixet22.bookpage()')
        return True


    def bookmark (self, select=[0], page=None, folder=None):
        """Make bookmark(s) for a specific selection of the nodes of
        this NodeList object. Nothing is returned, because the bookmarks
        just publish the selected nodes as they are doing their thing."""
        nn = self.make_NodeList()
        nn.bookmark (select=select, page=page, folder=folder)
        return True

    #=====================================================================
    # Fill the object with some test data:
    #=====================================================================

    def test (self, quals=None, simulate=False):
        """Helper function to make some test-matrices"""
        # self.history('.test('+str(simulate)+')')
        name = 'matrix22'
        keys = ['m11','m12','m21','m22']
        index = 0
        indices = []
        # Make 4 matrices in which all but one of the elements is zero (real).
        # The one non-zero element is a different one in each matrix.
        for key in keys:                           # keys=['m11','m12','m21','m22']
            index += 1
            indices.append(index)
            mm = dict(m11=0.0, m12=0.0, m21=0.0, m22=0.0)
            for elem in keys:
                phase = 0.0
                if elem==key:
                    phase = self.ns['phase'](elem)(index) << Meq.Parm(index)
                mm[elem] = self.ns.polar(elem)(index) << Meq.Polar(1.0, phase)
                # print key,elem,' phase =',str(phase)
            mat = self.ns[name](index) << Meq.Matrix22(mm['m11'],mm['m12'],
                                                       mm['m21'],mm['m22'])
        # Store the matrices and the list if indices:
        self.indices(new=indices)
        self.matrixet(new=self.ns[name])
        return True







     
#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    mat1 = Matrixet22(ns, quals=[])
    mat1.test(simulate=False)
    mat1.visualize(visu='rvsi')
    mat1.visualize(visu='straight')
    mat1.visualize(visu='timetracks', separate=False)
    mat1.display(full=True)
    aa = mat1.accumulist()

    if False:
        mat1.unop('Cos', visu=True)
        mat1.display('unop', full=True)

    if True:
        node = mat1.mean()
        cc.append(node)

    if False:
        mat2 = Matrixet22(ns, quals=[])
        mat2.test()
        mat2.visualize()
        mat2.display(full=True)
        aa.extend(mat2.accumulist())

    node = ns.accu << Meq.Composer(children=aa)
    print 'node=',str(node)
    cc.append(node)
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
       
def _tdl_job_sequence (mqs, parent):
    """Execute the forest, starting at the named node"""
    for t0 in range(10):
        domain = meq.domain(1.0e8,1.1e8,t0+1,t0+10)                  # (f1,f2,t1,t2)
        cells = meq.cells(domain, num_freq=10, num_time=11)
        request = meq.request(cells, rqtype='ev')
        result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       


if False:
    # This one comes from ../JEN/demo/JEN_leaves.py
    def _tdl_job_sequence (mqs, parent):
        """Execute the forest with the SAME domain a number of times"""
        domain = meq.domain(1,10,-100,100)                            # (f1,f2,t1,t2)
        cells = meq.cells(domain, num_freq=19, num_time=19)
        for domain_id in range(10):
            rqid = meq.requestid(domain_id=domain_id)
            request = meq.request(cells, rqtype='ev', rqid=rqid)
            result = mqs.meq('Node.Execute',record(name='result', request=request))
        return result


#===============================================================
# Test routine:
#===============================================================

if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        m1 = Matrixet22(ns, 'HHH', quals=['3c84'])
        m1.test(simulate=True)
        m1.visualize(visu='*',separate=True)
        m1.display(full=True)

    if 1:
        m1.make_NodeList()

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
        m2 = Matrixet22(ns, 'TTT', quals=['yyy'])
        m2.test(simulate=False)
        m2.display('m2',full=True)
        if 1:
            m1.binop('Subtract',m2)
            m1.display('after binop', full=True)        

    if 0:
        node = m1.bundle(quals='bbb')
        print 'bundle() ->',str(node)

    if 1:
        m1.history().display(full=True)

#===============================================================

