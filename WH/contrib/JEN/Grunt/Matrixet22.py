# file: ../Grunt/Matrixet22.py

# History:
# - 29dec2006: creation (extracted from Jones.py)
# - 12jan2007: added .show_timetracks() visualization
# - 19jan2007: removed make_condeqs() and make_solver()
# - 21jan2007: re-implemented .extract_matrel_nodes()
# - 23feb2007: allow key list in .extract_matrel_nodes()
# - 26mar2007: adapted for QualScope.py

# Description:

# The Matrixet22 class encapsulates a set of 2x2 matrices,
# e.g. Jones matrices, or cohaerency matrices. 

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

from Timba.Contrib.JEN.Grunt import Qualifiers
from Timba.Contrib.JEN.Grunt import ParmGroup
from Timba.Contrib.JEN.Grunt import ParmGroupManager
from Timba.Contrib.JEN.Grunt import ObjectHistory

import Meow

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
                 polrep=None):
        
        self._label = label                          # label of the matrixet 
        self._descr = descr                          # decription of the matrixet 

        self._polrep = polrep                        # polarization representation (linear, circular)
        self._pols = ['A','B']
        if self._polrep == 'linear':
            self._pols = ['X','Y']
        elif self._polrep == 'circular':
            self._pols = ['R','L']

        # Make a nodescope that carries the given node-name qualifiers:
        # NB: kwquals are forbidden, because they ruin the qualification scheme...
        self._ns = Meow.QualScope(ns, quals=quals)    

        self._matrixet = None                        # the actual matrices (contract!)
        self._indices = []                           # list of matrixet 'indices' (e.g. stations)
        self._list_indices = []                      # version where each item is a list
        self.matrixet(new=matrixet)                  # initialise, if matrixet specified
        self.indices(new=indices)                    # initialize, if indices specified

        # Access to Matrixet22 matrix elements:
        self._matrel = dict(m11=None, m12=None, m21=None, m22=None)
        self._matrel_index = dict(m11=[0,0], m12=[0,1], m21=[1,0], m22=[1,1])

        # Visualization:
        self._dcoll = None
        self._matrel_style = dict(m11='circle', m12='xcross', m21='xcross', m22='circle')
        self._matrel_color = dict(m11='red', m12='magenta', m21='darkCyan', m22='blue')

        # The (solvable and simulated) MeqParms are handled in named groups,
        # by a ParmGroupManager object. The latter may be supplied externally,
        # e.g. when interfacing with visibilities produced by the Meow system. 
        self._pgm = pgm
        if not self._pgm:
            parent = str(type(self))+'  '+str(self.label())
            self._pgm = ParmGroupManager.ParmGroupManager(self._ns, label=self.label(),
                                                          parent=parent)

        # Service: It is possible to accumulate lists of things (nodes, usually),
        # that are carried along by the object until needed downstream.
        self._accumulist = dict()

        # Attach an object to collect the object history:
        self._hist = ObjectHistory.ObjectHistory(self.label(), parent=self.oneliner())

        # Kludge: used for its printing functions...
        self._dummyParmGroup = ParmGroup.ParmGroup(ns,'dummy')
        return None

    #-------------------------------------------------------------------

    def copy(self):
        """Return a (limited) copy of the current Matrixet22 object.
        For the moment, for limited use only."""
        raise ValueError,'.....copy() not really implemented...'
        # return deepcopy(self)..........................does not work...
        # self.display('copy(), before')
        new = Matrixet22(self._ns,
                         label='copy('+self.label()+')',
                         descr=self.descr(),
                         matrixet=self.matrixet(),
                         indices=self.indices())
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

    def hist(self, full=False):
        """Print/return the object description""" 
        self._hist.display(full=full)
        return self._hist

    def ns(self, new=None):
        """Return/replace the object NodeScope/QualScope"""
        if new:
            self._ns = new
        return self._ns

    #-------------------------------------------------------------------

    def polrep(self):
        """Return the polarization representation (linear, circular, None)"""
        return self._polrep

    def pols(self):
        """Return the list of 2 polarization names (e.g. ['X','Y'])"""
        return self._pols

    #-------------------------------------------------------------------

    def ParmGroupManager (self, merge=None):
        """Return its ParmGroupManager object.
        If merge is another object (with a pgm), merge the latter with it"""
        if merge:
            self._pgm.merge(merge.ParmGroupManager())
        return self._pgm

    def pgm (self):
        """Return its ParmGroupManager object."""
        return self._pgm

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

    def plot_labels(self):
        """Return a list of plot-labels, one per matrix. See show_timetracks()."""
        ss = []
        for i in self.list_indices():
            if len(i)==1:
                ss.append(str(i[0]))                             # e.g. station nrs (4)
            elif len(i)==2:
                ss.append(str(i[0])+'-'+str(i[1]))               # e.g. ifrs (4-7)
            elif len(i)==3:
                ss.append(str(i[0])+'-'+str(i[1])+'-'+str(i[2])) # ....?
            else:
                ss.append(str(i))                                # the list itself: ([5,6,89,3])
        return ss

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
        ss += '  '+str(self.label())
        ss += '  n='+str(len(self.indices()))
        # ss += '  quals='+str(self.quals())
        return ss

    def display_ParmGroupManager(self, full=False):
        """Print a summary of the ParmGroupManager of this object"""
        self._pgm.display()
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
        print ' * Available indices ('+str(self.len())+'): ',
        if self.len()<30:
            print str(self.indices())
        else:
            print '\n   '+str(self.indices())
        print ' * Available list_indices ('+str(self.len())+'): ',
        if self.len()<30:
            print str(self.list_indices())
            print ' * Plot_labels: '+str(self.plot_labels())
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
            print ' * The first matrix of the set:'
            node = self.firstnode()
            self._dummyParmGroup.display_subtree(node, txt=str(0),
                                                 show_initrec=False,
                                                 recurse=recurse)
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
        self._pgm.display(full=full)
        #...............................................................
        print '**\n'
        return True

    #........................................................................

    def show_matrix_subtree (self, index='*', recurse=2, show_initrec=False):
        """Helper function for closer inspection of the specified matrix(es)"""
        print '\n** matrix subtrees of: ',self.oneliner(),'\n'
        if index=='*': index = self.list_indices()
        for ii in index:
            node = self._matrixet(*ii)
            self._dummyParmGroup.display_subtree(node, txt=str(ii),
                                                 show_initrec=show_initrec,
                                                 recurse=recurse)
            print
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

    #---------------------------------------------------------------------

    def bundle_accumulist(self, qual=None):
        """Bundle the nodes in self._accumulist with a reqseq"""
        cc = self.accumulist(clear=False)
        n = len(cc)
        if n==0: return None
        if n==1: return cc[0]
        ns = self._ns._derive(append=qual)
        if not ns.bundle_accumulist.initialized():
            ns.bundle_accumulist << Meq.ReqSeq(children=cc,
                                               result_index=n-1)
        return ns.bundle_accumulist

    #---------------------------------------------------------------------------

    def merge_accumulist (self, other):
        """Merge the accumulist of another Matrix22 object with its own."""
        olist = other._accumulist
        for key in olist.keys():
            if not key=='*':
                self.accumulist(olist[key], key=key, flat=True)
        return True


    #=====================================================================================
    # Access to individual matrix elements within the 2x2 matrices:
    #=====================================================================================

    def matrel_keys (self):
        """Return the list of the (4) matrix element names:
        i.e. ['m11','m12','m21','m22']"""
        return self._matrel.keys()


    def extract_matrix_element(self, key='m11', qual=None, unop=None):
        """Extract the specified matrix element(s) from the 2x2 matrices,
        and return a list of nodes. The key must be one of the strings
        'm11', 'm12', 'm21' or 'm22', or a list of these. If key='*', all
        4 elements will be extracted from all matrices.  
        If unop is specified (str), apply an unary operation to the nodes."""

        keys = deepcopy(key)                                    # just in case
        if keys=='*': keys = self.matrel_keys()                 # all elements
        if keys=='diag': keys = ['m11','m22']                   # diagonal elements
        if keys=='nondiag': keys = ['m12','m21']                # non-diagonal elements
        if not isinstance(keys,(list,tuple)): keys = [keys]

        nodes = []
        for key in keys:
            if not self._matrel.has_key(key):
                raise ValueError,'key='+key+', not in '+str(self.matrel_keys())

            name = self.basename()+'_'+key
            # quals = self.quals(append=qual)
            ns = self._ns._derive(append=qual)
            if not ns[name].initialized():                      # avoid duplication....!
                for i in self.list_indices():
                    index = self._matrel_index[key]             # index in tensor node, e.g. (0,1)
                    node = ns[name](*i) << Meq.Selector(self._matrixet(*i),
                                                        index=index) 
                self._matrel[key] = ns[name]                    # keep for inspection etc

            # Optionally, apply a unary operation (unop) to the extracted node:
            if unop:
                # quals = self.quals(append=qual, prepend=unop)
                ns = self._ns._derive(append=qual, prepend=unop)
                if not ns[name].initialized():                  # avoid duplication....!
                    for i in self.list_indices():
                        ns[name](*i) << getattr(Meq, unop)(self._matrel[key](*i))
                self._matrel[key] = ns[name]                    # keep for inspection etc

            # Append to the list of nodes:
            for i in self.list_indices():
                nodes.append(self._matrel[key](*i))
                
        # Finished: return the accumulated list of nodes:
        return nodes


    


    #=====================================================================================
    # Math operations: 
    #=====================================================================================

    def binop(self, binop=None, other=None, qual=None, visu=False):
        """Do an (item-by-item) binary operation (e.g. Subtract)
        between itself and another Matrixet22 object."""
        # quals = self.quals(append=qual, merge=other.quals())
        ns = self._ns._derive(append=qual)
        ns = ns._merge(other._ns)
        for i in self.list_indices():
            ns[binop](*i) << getattr(Meq,binop)(self._matrixet(*i),
                                                other._matrixet(*i))
        self.matrixet(new=ns[binop])                                 # replace
        # self._pgm.merge(other._pgm)                                # ...........!!?
        if visu: self.visualize(qual=qual, visu=visu)
        return True


    def unop(self, unop=None, qual=None):
        """Do an (item-by-item) unary operation on itself (e.g. Abs)"""
        # quals = self.quals(append=qual)
        ns = self._ns._derive(append=qual)
        for i in self.list_indices():
            ns[unop](*i) << getattr(Meq,unop)(self._matrixet(*i))
        self.matrixet(new=ns[unop])                                  # replace
        return True

    #---------------------------------------------------------------------

    def bundle(self, oper='Composer', qual=None):
        """Bundle its matrices, using an operation like Composer, Add, Multiply etc"""
        # quals = self.quals(append=qual)
        ns = self._ns._derive(append=qual)
        if not ns.bundle(oper).initialized():
            cc = []
            for i in self.list_indices():
                cc.append(self._matrixet(*i))
            if oper=='Composer':
                # Append a reqseq of self._accumulist nodes (if any):
                accuroot = self.bundle_accumulist(qual=qual)
                if accuroot: cc.append(accuroot)
            ns.bundle(oper) << getattr(Meq,oper)(children=cc)
        return ns.bundle(oper)



    #=====================================================================
    # Visualization:
    #=====================================================================


    def visualize (self, qual=None, visu='rvsi', accu=True,
                   matrel='*', separate=False,
                   bookpage='Matrixet22', folder=None):
        """Generic visualisation, controlled by visu. The latter may be:
        - timetracks: show timetracks for all matrices, averaged over freq.
        - spectra:    show spectra (not implemented yet)
        - rvsi:       show a real-vs-imag plot, refreshed per timeslot
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

        dcolls = []
        for visual in visu:
            if visual=='timetracks':
                dc = self.show_timetracks (qual=qual, accu=False, separate=separate,
                                           bookpage=bookpage, folder=folder)
                dcolls.append(dc)
            elif visual=='straight':
                return self.show_straight (qual=qual, accu=False, relative=True,
                                           bookpage=bookpage, folder=folder)
            elif visual=='spectra':
                pass                         # not implemented yet
            else:
                dc = self.show_rvsi (qual=qual, matrel=matrel, accu=False,
                                     bookpage=bookpage, folder=folder)
                dcolls.append(dc)
                
        # Return a single node (bundle them if necessary):
        if len(dcolls)==0: return False
        if len(dcolls)==1:
            if accu: self.accumulist(dcolls[0])
            return dcolls[0]
        ns = self._ns._derive(append=qual)
        bundle = ns._unique('visu_bundle') << Meq.Composer(children=dcolls)
        if accu: self.accumulist(bundle)
        return bundle


    #.......................................................................

    def show_rvsi (self, qual=None, matrel='*', accu=True,
                   bookpage='Matrixet22', folder=None):

        """Visualise (a subset of) the 4 complex matrix elements of all 
        Matrixet22 matrices in a single real-vs-imag plot. Different
        matrix elements (m11,m12,m21,m22) have different styles
        and colors, which are the same for all Matrixet22 matrices.
        A bookmark item is made for the resulting dataCollect node.
        The resulting dataCollect node is returned, but if accu=True (default)
        it is also stored in self.accumulist(key=None) for later retrieval."""

        ns = self._ns._derive(append=qual)

        dcolls = []
        keys = deepcopy(matrel)
        if keys=='*': keys = self._matrel.keys()              # i.e. ['m11','m12','m21','m22']
        if not isinstance(keys,(list,tuple)): keys = [keys]
        for key in keys:  
            cc = self.extract_matrix_element(key, qual=qual) 
            rr = MG_JEN_dataCollect.dcoll (ns, cc, 
                                           scope=ns._qualstring(),
                                           tag=key,
                                           color=self._matrel_color[key],
                                           style=self._matrel_style[key],
                                           size=8, pen=2,
                                           type='realvsimag', errorbars=True)
            # print 'key:',key,rr
            dcolls.append(rr)

        # Make a combined plot of all the matrix elements:
        # NB: nodename -> dconc_scope_tag
        rr = MG_JEN_dataCollect.dconc(ns, dcolls,
                                      scope=ns._qualstring(),
                                      tag=' ', bookpage=None)
        self._dcoll = rr['dcoll']
        JEN_bookmarks.create(self._dcoll, self.label(),
                             page=bookpage, folder=folder)
        # Keep the dcoll node for later retrieval (e.g. attachment to reqseq):
        if accu: self.accumulist(self._dcoll)
        # Return the dataConcat node:
        return self._dcoll


    #--------------------------------------------------------------------------

    def show_straight (self, qual=None, accu=True, relative=True,
                       bookpage='straight22', folder=None):

        """Make separate plots of all matrices (assumed interpolatable...).
        - A bookmark item is made for the resulting node, which is also returned.
        - If accu=True (default) it is also stored in self.accumulist(key=None)
        for later retrieval.
        """
        ns = self._ns._derive(append=qual)
        cc = self.nodelist()
        if relative:
            mean = ns.mean(self.label()) << Meq.WMean(*cc)
            for i,c in enumerate(cc):
                cc[i] = ns.wrt_mean.qmerge(mean,cc[i]) << Meq.Subtract(cc[i],mean)
            cc.insert(0,mean)

        JEN_bookmarks.create(cc, self.label(),
                             page=bookpage, folder=folder)
        if relative:
            return ns.show_straight(self.label()) << Meq.Composer(*cc)
        return True


    #--------------------------------------------------------------------------

    def show_timetracks (self, qual=None, accu=True, separate=False,
                         bookpage='timetracks22', folder=None):

        """Make time-track plots of the complex matrix elements of all matrices.
        - A bookmark item is made for the resulting node, which is also returned.
        - If accu=True (default) it is also stored in self.accumulist(key=None)
        for later retrieval.
        - If separate=True (default=False), make separate plots for the 4 elements.
        """

        #............................................................................
        if separate:
            return self.show_timetracks_separate (qual=qual, matrel='*', accu=accu,
                                                  bookpage=bookpage, folder=folder)
        #............................................................................

        ns = self._ns._derive(append=qual)

        cc = self.nodelist()
        for i in range(len(cc)):
            cc[i] = ns << Meq.Mean (cc[i], reduction_axes="freq")
        name = 'timetracks'
        coll = ns[name] << Meq.Composer(dims=[self.len(),2,2],
                                        plot_label=self.plot_labels(),
                                        children=cc)
        JEN_bookmarks.create(coll, self.label(),
                             viewer='Collections Plotter',
                             page=bookpage, folder=folder)
        # Keep the dcoll node for later retrieval (e.g. attachment to reqseq):
        if accu: self.accumulist(coll)
        # Return the timetracks node:
        return coll


    #--------------------------------------------------------------------------

    def show_timetracks_separate (self, qual=None, matrel='*', accu=True,
                                  bookpage='timetracks22', folder=None):

        """Make separate time-track plots for each of the 4 matrix elements
        of the complex matrix elements of all matrices.
        - A bookmark item is made for the resulting timetracks nodes.
        - If accu=True (default) they are also stored in self.accumulist(key=None)
        for later retrieval.
        - A list of timetracks nodes is returned."""

        ns = self._ns._derive(append=qual)

        colls = []
        keys = deepcopy(matrel)
        if keys=='*': keys = self._matrel.keys()              # i.e. ['m11','m12','m21','m22']
        if not isinstance(keys,(list,tuple)): keys = [keys]
        plot_labels = self.plot_labels()
        for key in keys:  
            cc = self.extract_matrix_element(key, qual=qual)
            for i in range(len(cc)):
                cc[i] = ns.mean << Meq.Mean (cc[i], reduction_axes="freq")
            name = 'timetracks_'+key
            coll = self._ns[name] << Meq.Composer(dims=[len(cc)],
                                                  plot_label=plot_labels,
                                                  children=cc)
            JEN_bookmarks.create(coll, self.label()+key,
                                 viewer='Collections Plotter',
                                 page=bookpage, folder=folder)
            # Keep the dcoll node for later retrieval (e.g. attachment to reqseq):
            if accu: self.accumulist(coll)
            colls.append(coll)
            
        # Bundle the list of timetracks nodes:
        name = 'timetracks'
        coll = ns[name] << Meq.Composer(children=colls)
        return coll



    #=====================================================================
    # Fill the object with some test data:
    #=====================================================================

    def test (self, qual=None, simulate=False):
        """Helper function to make some test-matrices"""
        ns = self._ns._derive(append=qual)
        name = 'matrix22'
        keys = self._matrel.keys()
        index = 0
        indices = []
        # Make 4 matrices in which all but one of the elements is zero (real).
        # The one non-zero element is a different one in each matrix.
        for key in keys:                           # keys=['m11','m12','m21','m22']
            index += 1
            indices.append(index)
            qkey = self.pgm().define_parmgroup(self._ns, key,
                                               # quals='xxx',
                                               descr='matrix element: '+key,
                                               default=dict(value=index/10.0),
                                               # simul=dict(stddev=0.01),
                                               simulate=simulate,
                                               rider=dict(matrel='*'),
                                               tags=['testing'])
            mm = dict(m11=0.0, m12=0.0, m21=0.0, m22=0.0)
            for elem in keys:
                mm[elem] = ns.polar(elem)(key) << Meq.Polar(1.0, 0.0)
            # The one non-zero element is complex, with amplitude=1.0,
            # and phase equal to index/10 radians (plus variation if simulate=True):
            phase = self.pgm().create_parmgroup_entry(qkey, index)
            mm[key] = ns.polar(key) << Meq.Polar(1.0, phase)
            mat = ns[name](index) << Meq.Matrix22(mm['m11'],mm['m12'],
                                                  mm['m21'],mm['m22'])
        # Store the matrices and the list if indices:
        self.indices(new=indices)
        self.matrixet(new=ns[name])

        # Make some secondary (composite) ParmGroups:
        self.pgm().define_gogs('test')
        return True







     
#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    mat1 = Matrixet22(ns, quals=[])
    mat1.test(simulate=False)
    mat1.visualize()
    mat1.show_timetracks()
    mat1.show_timetracks(separate=True)
    mat1.display(full=True)

    mat2 = Matrixet22(ns, quals=[])
    mat2.test()
    mat2.visualize()
    mat2.display(full=True)

    aa = mat1.accumulist()
    aa.extend(mat2.accumulist())
    print 'aa=',aa
    node = ns.accu << Meq.Composer(children=aa)
    cc.append(node)

    # ns.result << Meq.ReqSeq(children=cc)
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
        m1 = Matrixet22(ns, quals=['3c84'], label='HH')
        m1.test(simulate=True)
        # m1.visualize()
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
        m2 = Matrixet22(ns, quals=['yyy'], label='TT')
        m2.test(simulate=False)
        m2.display('m2',full=True)
        if 1:
            m1.binop('Subtract',m2)
            m1.display('after binop', full=True)        

    if 0:
        m1.extract_matrix_element('m11')
        m1.extract_matrix_element('m12', unop='Abs')
        m1.extract_matrix_element('m12', unop='Cos')
        m1.extract_matrix_element('m12', unop='Abs')
        m1.extract_matrix_element('m21')
        m1.extract_matrix_element('m22')
        m1.display(full=True)

    if 0:
        node = m1.bundle(qual='bbb')
        print 'bundle() ->',str(node)

    if 0:
        matrel = 'm11'
        matrel = '*'
        matrel = 'diag'
        matrel = 'nondiag'
        # matrel = ['m21','m22']
        unop = None
        # unop = 'Abs'
        nodes = m1.extract_matrix_element(matrel, unop=unop)
        for k,node in enumerate(nodes):
            print k,':',node 
        m1.display(full=True)

#===============================================================

