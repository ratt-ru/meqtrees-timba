# file: ../JEN/util/JEN_SolverChain.py
# An object to help constructing a solver sequence with visualisation


from Timba.TDL import *
from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect
from Timba.Contrib.JEN import MG_JEN_historyCollect

# Global counter used to generate unique node-names
unique = -1

class SolverChain (object):
    
    def __init__(self, ns, label=None, array=None):
        self._ns = ns                          # nodescope
        self._array = array                    # Meow array object
        self._label = label
        self._scope = '<scope>'
        self._cohset = None                    # 
        self._clear()

    def _clear(self):
        """Clear the object"""
        self._reqseq_children = []
        self._bookmark = dict()
        self._cxparm = dict()
        self._visumap = dict()
        return True

    #--------------------------------------------------------------------------

    def scope(self, new=None):
        """Get/set the scope (string) that is used to generate node-names"""
        if new: self._scope = new
        return self._scope

    def ifrs (self, select='all'):
        """Get a selection of self._array.ifrs()"""
        ifrs = self._array.ifrs()
        return ifrs

    def cohset (self, new=None):
        """Access to the internal self._cohset"""
        if new:
            self._cohset = new
            self._scope = 'input'
            if self.visumap('input'):
                self.visualize_cohset (tag='input',plot_type='spectra')
                self.visualize_cohset (tag='input', errorbars=True)
        return self._cohset

    #--------------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of the object"""
        ss = str(type(self))
        ss += ' label='+str(self._label)
        ss += ' scope='+str(self._scope)
        return ss

    def display(self, txt=None):
        """Print a summary of the contents/state of the object"""
        ss = self.oneliner()
        if txt: ss += ' ('+str(txt)+')'
        print '\n**',ss
        n = len(self._reqseq_children)
        print '** _reqseq_children ('+str(n)+'):'
        for i in range(n):
            node = self._reqseq_children[i]
            print '  - '+str(i)+': '+str(node)
        print '** _cxparm:'
        for key in self._cxparm.keys():
            print '  - '+key+': '+str(len(self._cxparm[key]))
        print '** _bookmarks:'
        for key in self._bookmark.keys():
            print '  - '+key+': '+str(len(self._bookmark[key]))
        print '** _visumap:'
        for key in self._visumap.keys():
            print '  - '+key+': '+str(self._visumap[key])
        print '** _ns: '+str(type(self._ns))
        print '** _array: '+str(type(self._array))
        print '** _cohset: '+str(type(self._cohset))
        print 

    #--------------------------------------------------------------------------

    def cxparm(self, cx=None, scope=None):
        """Append the given complex 'parm' to an internal list (scope),
        to be used for later visualisation (see make_solver)"""
        scope = self.scope(scope)
        self._cxparm.setdefault(scope,[])
        self._cxparm[scope].append(cx)
        return True

    def append (self, node, scope=None):
        """Append a node to the internal list of reqseq children"""
        if isinstance(node, (list,tuple)):
            self._reqseq_children.extend(node)
        else:
            self._reqseq_children.append(node)
        return True


    def insert_reqseq (self):
        """Make the reqseq node(s) and insert it in the cohset (...).
        The reqseq that executes the solvers in order of creation,
        and then passes on the final residuals (in new cohset)."""
        n = len(self._reqseq_children)
        self._reqseq_children.append(0)               # placeholder 
        cohset = self.cohset()
        for ifr in self.ifrs():
            self._reqseq_children[n] = cohset(*ifr)   # fill in the placeholder
            self._ns.reqseq_SolverChain(*ifr) << Meq.ReqSeq(children=self._reqseq_children,
                                                            result_index=n,
                                                            cache_num_active_parents=1)
        if True: self.display('insert_reqseq')

        # Make the new cohset, and return it:
        self._cohset = self._ns.reqseq_SolverChain
        self.make_bookmarks()
        self._clear()                                 # ....??
        return self.cohset()

    def bookmark(self, node, page):
        """Append the given node to the specified bookpage"""
        self._bookmark.setdefault(page, [])
        self._bookmark[page].append(node)
        return True

    def make_bookmarks(self):
        """Make the actual bookmarks from the accumulated info"""
        for key in self._bookmark.keys():
            JEN_bookmarks.create(self._bookmark[key], 'sc_'+key)
        return True

    #--------------------------------------------------------------------------
    # Visualisation map
    #--------------------------------------------------------------------------

    def visumap(self, key=None, value=None):
        """Interaction with the 'visualisation map', which enables the
        various inbuilt visualisation possibilities of this object"""
        if len(self._visumap)==0:
            self._visumap = dict(mode='off', input=False, peeled=False, unpeeled=False,
                                 condeqs=False, solvables=False, solvers=False, ifr=[]) 
        if not isinstance(key, str):
            return self._visumap
        if key=='mode':
            if value=='full':
                ifr1 = (1,3)
                ifr2 = (2,4)
                self._visumap = dict(mode=value, input=True, peeled=True, unpeeled=True,
                                     addnoise=True, corrupted=True, corrected=True,
                                     condeqs=True, solvables=True, solvers=True,
                                     ifr=[ifr1,ifr2]) 
            elif value=='off':
                self._visumap = dict(mode=value, input=False, peeled=False, unpeeled=False,
                                     addnoise=False, corrupted=False, corrected=False,
                                     condeqs=False, solvables=False, solvers=False, ifr=[]) 
            else:
                self._visumap = dict(mode='min', input=False, peeled=False, unpeeled=False,
                                     addnoise=True, corrupted=False, corrected=True,
                                     condeqs=True, solvables=False, solvers=True, ifr=[]) 
            print '\n** visumap (mode):',self._visumap,'\n'
        elif not value==None:
            if key=='ifr' and not isinstance(value,list): value = [value]
            self._visumap[key] = value
            print '\n** visumap (',key,'):',self._visumap,'\n'
        if self._visumap.has_key(key):
            return self._visumap[key]
        print '\n** .visumap(): key not recognised:',key,'\n'
        return None
        

    def visumap_bookmark(self, node=None, key='ifr', value=None, page=None):
        """Make a bookmark of the node if value is in _visumap[key]"""
        if self._visumap.has_key(key):
            if isinstance(self._visumap[key], (list,tuple)):
                if value in self._visumap[key]:
                    if not isinstance(page,str):
                        page = key+'_'+str(value)
                    self.bookmark(node, page)
        return page


    #--------------------------------------------------------------------------
    # solver-related methods:
    #--------------------------------------------------------------------------

    def make_solver (self, scope=None,
                     parm_tags=None, parm_group='Parm',
                     measured=None, predicted=None,
                     num_iter=3):
        """Create a solver node for the specified (parm_tags) MeqParms,
        making condeqs from the given cohsets (measured and predicted),
        and append it to the list of reqseq children"""

        scope = self.scope(scope)

        if predicted:
            # Compare measured visibilities with predicted values:
            condeqs = self.make_condeqs (measured=measured, predicted=predicted,
                                         select='all')
        else:
            # No predicted cohset: compare redundant spacings:
            condeqs = self.make_redun_condeqs (measured=measured, select='all')

        # Get a list of names of MeqParms to be solved for:
        solvables = self._ns.Search(tags=parm_tags, class_name='MeqParm',
                                    return_names=False)

        # The solver writes (the stddev of) its condeq resunts as ascii
        # into a debug-file (SBY), for later visualisation.
        # - all lines start with the number of entries (one per condeq)
        # - the first line has the condeq names (solver children)
        # - the rest of the lines have one ascii number per condeq
        # - Q: the solver writes a line at each iteration...? 
        # NB: the extension can be chosen at will, for identification
        debug_file = 'debug_'+scope+'.ext'

        solver = False
        if len(condeqs)>0 and len(solvables)>0:
            solver = self._ns.solver(scope) << Meq.Solver(children=condeqs,
                                                         solvable=solvables,
                                                         debug_file=debug_file,
                                                         parm_group=hiid(parm_group),
                                                         # child_poll_order=cpo,
                                                         num_iter=num_iter)

            # Append the solver to the internal list of reqseq children: 
            self.append(solver)

            # Visualization (controlled by the 'visualization map'):
            if self.visumap('solvers'):
                self.bookmark(solver, 'solvers')
                self.hcoll_solver_metrics(solver)
            if self.visumap('condeqs'):
                dcoll = self.dataConcat(condeqs, tag='condeqs', errorbars=True)
                self.bookmark(dcoll, 'condeqs')
            if self.visumap('solvables'):
                if self._cxparm.has_key(scope):
                    solvables = self._cxparm[scope] 
                dcoll = self.dataCollect(solvables, tag='solvables')
                self.bookmark(dcoll, 'solvables')
        return solver

    #...........................................................................

    def make_condeqs (self, measured=None, predicted=None, select='all'):
        """Create a list of (selected) condeq nodes from the given cohsets
        (measured and predicted)"""
        cc = []
        scope = self.scope()
        if not measured: measured = self.cohset()
        for ifr in self.ifrs():
            condeq = self._ns.condeq(scope)(*ifr) << Meq.Condeq(predicted(*ifr),
                                                                measured(*ifr))
            cc.append(condeq)
            self.visumap_bookmark(condeq, key='ifr', value=ifr)
            # self.selected_hcoll(condeq, key='ifr', value=ifr)
        # Return a list of zero or more condeq nodes:
        return cc

    #...........................................................................

    def make_redun_condeqs (self, measured=None, select='all'):
        """Create a list of (selected) condeq nodes by comparing redundant
        spacings (WSRT only) in the given cohset (measured)"""
        cc = []
        scope = self.scope()
        if not measured: measured = self.cohset()
        ifrs = self.ifrs()
        for i in range(len(ifrs)-1):
            ifr1 = ifrs[i]
            b1 = ifr1[1] - ifr1[0]
            # print '-',i,ifr1,b1
            for j in range(i+1,len(ifrs)):
                ifr2 = ifrs[j]
                b2 = ifr2[1] - ifr2[0]
                # print '  -',j,ifr2,b2
                if b2==b1:
                # if b2==b1 and (not ifr2[0]==ifr1[1]):
                    condeq = self._ns.condeq(scope)(*ifr1)(*ifr2) << Meq.Condeq(measured(*ifr1),
                                                                                measured(*ifr2))
                    cc.append(condeq)
                    page = self.visumap_bookmark(condeq, key='ifr', value=ifr1)
                    self.visumap_bookmark(measured(*ifr1), key='ifr', value=ifr1, page=page)
                    self.visumap_bookmark(measured(*ifr2), key='ifr', value=ifr2, page=page)
                    # self.visumap_hcoll(condeq, key='ifr', value=ifr1)
                    # print '     redundant condeq:',condeq,':',b1,b2,ifr1,ifr2
                    break
        # Return a list of zero or more condeq nodes:
        return cc



    #--------------------------------------------------------------------------
    # Operations on the internal self._cohset:
    #--------------------------------------------------------------------------

    def addnoise (self, rms=0.1):
        """Add gaussian noise with given rms to the internal cohset"""
        scope = self.scope()
        cohset = self.cohset()
        for ifr in self.ifrs():
            rnoise = self._ns.rnoise(scope)(*ifr) << Meq.GaussNoise(stddev=rms)
            inoise = self._ns.inoise(scope)(*ifr) << Meq.GaussNoise(stddev=rms)
            noise = self._ns.noise(scope)(*ifr) << Meq.ToComplex(rnoise,inoise)
            node = self._ns.addnoise(scope)(*ifr) << Meq.Add(cohset(*ifr),noise)
            self.visumap_bookmark(node, key='ifr', value=ifr)
        self._cohset = self._ns.addnoise(scope)           
        if self.visumap('addnoise'):
            self.visualize_cohset (tag='addnoise', errorbars=True)
        return self.cohset()

    #...........................................................................

    def peel (self, subtract=None):
        """Subtract (peel) a cohset (e.g. a source) from the internal cohset"""
        scope = self.scope()
        cohset = self.cohset()
        for ifr in self.ifrs():
            node = self._ns.peeled(scope)(*ifr) << Meq.Subtract(cohset(*ifr),subtract(*ifr))
            self.visumap_bookmark(node, key='ifr', value=ifr)
        self._cohset = self._ns.peeled(scope)           
        if self.visumap('peeled'):
            self.visualize_cohset (tag='peeled', errorbars=True)
        return self.cohset()

    #...........................................................................

    def unpeel (self, scope=None, add=None):
        """Add (unpeel/restore) a cohset (e.g. a source) to the internal cohset"""
        scope = self.scope(scope)
        cohset = self.cohset()
        for ifr in self.ifrs():
            unpeel = self._ns << Meq.Stripper(add(*ifr))
            node = self._ns.unpeeled(scope)(*ifr) << Meq.Add(cohset(*ifr), unpeel)
            self.visumap_bookmark(node, key='ifr', value=ifr)
        self._cohset = self._ns.unpeeled(scope)              
        if self.visumap('unpeeled'):
            self.visualize_cohset (tag='unpeeled', errorbars=True)
        return self.cohset()

    #...........................................................................

    def corrupt (self, jones=None, rms=0.0, scope=None):
        """Corrupt the internal cohset with the given Jones matrices"""
        scope = self.scope(scope)
        cohset = self.cohset()
        for ifr in self.ifrs():
            j1 = jones(ifr[0])
            j2c = jones(ifr[1])('conj') ** Meq.ConjTranspose(jones(ifr[1])) 
            node = self._ns.corrupted(scope)(*ifr) << Meq.MatrixMultiply(j1,cohset(*ifr),j2c)
            self.visumap_bookmark(node, key='ifr', value=ifr)
        self._cohset = self._ns.corrupted(scope)              
        if self.visumap('corrupted'):
            self.visualize_cohset (tag='corrupted', errorbars=True)
        if rms>0.0:
            # Optional: add gaussian noise (AFTER corruption, of course):
            self.addnoise(rms)
        return self.cohset()

    #...........................................................................

    def correct (self, jones=None, scope=None):
        """Correct the internal cohset with the given Jones matrices"""
        scope = self.scope(scope)
        cohset = self.cohset()
        for ifr in self.ifrs():
            j1i = jones(ifr[0])('inv') ** Meq.MatrixInvert22(jones(ifr[0]))
            j2c = jones(ifr[1])('conj') ** Meq.ConjTranspose(jones(ifr[1])) 
            j2ci = j2c('inv') ** Meq.MatrixInvert22(j2c)
            node = self._ns.corrected(scope)(*ifr) << Meq.MatrixMultiply(j1i,cohset(*ifr),j2ci)
            self.visumap_bookmark(node, key='ifr', value=ifr)
        self._cohset = self._ns.corrected(scope)              
        if self.visumap('corrected'):
            self.visualize_cohset (tag='corrected', errorbars=True)
        return self.cohset()


    #--------------------------------------------------------------------------
    # Visualisation:
    #--------------------------------------------------------------------------

    def visualize_cohset (self, tag='cohset',
                          plot_type='realvsimag', errorbars=False):
        """Visualise the given cohset"""
        # scope = self.scope()
        nodelist = self.cohset_list (self._cohset, ifrs=self.ifrs())
        dcoll = self.dataConcat (nodelist, tag=tag,
                                 plot_type=plot_type, errorbars=errorbars)
        self.bookmark(dcoll, tag)
        return dcoll

    def visualize_cxparm(self):
        """Visualize the accumulated cxparm values"""
        for scope in self._cxparm.keys():
            dcoll = self.dataCollect(self._cxparm[scope], tag='cxparm_'+scope)
            self.bookmark(dcoll, 'cxparm')
        return True

    #........................................................................
    # From TDL_radioconventions.py
    # rr = dict(XX='circle', XY='xcross', YX='xcross', YY='circle')
    # rr = dict(XX='red', XY='magenta', YX='darkCyan', YY='blue')

    def dataConcat (self, nodelist=None, tag='allcorrs',  
                    corrs=['XX','XY','YX','YY'],
                    style=['circle','xcross','xcross','circle'],
                    color=['red','magenta','darkCyan','blue'],
                    plot_type='realvsimag', errorbars=False):
        """Visualise the 4 correlations in a nodelist.
        If ifrs is given, the nodelist is assumed to be a cohset,
        and the nodelist is extracted from it."""
        scope = self.scope()
        dcolls = []
        for i in range(len(corrs)):
            cc = self.select_index (nodelist, index=i, tag=corrs[i])
            rr = MG_JEN_dataCollect.dcoll (self._ns, cc, 
                                           scope=scope, tag=corrs[i],
                                           color=color[i], style=style[i],
                                           size=8, pen=2,
                                           type=plot_type, errorbars=errorbars)
            dcolls.append(rr)
        # Make a combined plot of all the corrs:
        rr = MG_JEN_dataCollect.dconc(self._ns, dcolls, scope=scope,
                                      tag=tag, bookpage=None)
        # Append the dataConcat node to the reqseq, and return it
        dcoll = rr['dcoll']
        self.append(dcoll)
        return dcoll
        
    #--------------------------------------------------------------------------

    def dataCollect (self, nodelist=None, tag=None,
                     index=None, corrs=['XX','XY','YX','YY'],
                     plot_type='realvsimag', errorbars=True,
                     color='red', style=None, size=1, pen=1):
        """Create a dataCollect node for the specified nodelist, and append"""
        scope = self.scope()
        if index:
            # If index is specified, extract a single correlation: 
            cc = self.select_index (nodelist, index=index, tag=corrs[i])
            tag += '_'+corrs[index]
        rr = MG_JEN_dataCollect.dcoll (self._ns, nodelist, 
                                       scope=scope, tag=tag,
                                       color=color,
                                       type=plot_type, errorbars=errorbars)
        # Append the dataCollect node to the reqseq, and return it
        dcoll = rr['dcoll']
        self.append(dcoll)   
        return dcoll

    #--------------------------------------------------------------------------

    def historyCollect (self, nodelist):
        """Create a historyCollect node for the specified nodelist, and append"""
        return True

    def selected_hcoll(self, node=None, key='ifr', value=None):
        """Make a historyCollect of the node if value is in _visumap[key]"""
        if self._visumap.has_key(key):
            if value in self._visumap[key]:
                hcoll = MG_JEN_historyCollect.insert_hcoll(self._ns, node,
                                                           graft=False)
                self.bookmark(hcoll, key+'_'+str(value))
                self.append(hcoll)
        return True

    def hcoll_solver_metrics(self, solver):
        """Make historyCollect nodes for the specified solver"""
        scope = self.scope()
        hcoll = MG_JEN_historyCollect.make_hcoll_solver_metrics (self._ns, solver,
                                                                 name='solver_'+scope,
                                                                 bookfolder='solver_hcoll',
                                                                 debug=False,
                                                                 firstonly=False)
        self.append(hcoll)
        return hcoll

    #--------------------------------------------------------------------------
    # Some helper functions:
    #--------------------------------------------------------------------------

    def cohset_list (self, cohset, ifrs, select='all'):
        """Get the list of (selected) nodes in the given cohset"""
        cc = []
        for ifr in ifrs:
            node = cohset(*ifr)
            # print '- cohset node:',ifr,':',node
            cc.append(node)
        return cc


    def select_index (self, node, index=0, tag='XX'):
        """Extract the node with the given index from the given tensor node(s)"""
        if not isinstance(node, (list,tuple)): node = [node]
        global unique
        increment = False
        ss = []
        for i in range(len(node)):
            if self._ns.select(tag).qadd(node[i]).initialized():
                increment = True
                s = self._ns.select(tag).qadd(node[i])(unique) << Meq.Selector(node[i], index=index)
            else:
                s = self._ns.select(tag).qadd(node[i]) << Meq.Selector(node[i], index=index)
            ss.append(s)
            # print '- selected:',i,':',s
        if increment: unique += -1
        if len(node)==1:
            node = node[0]
            ss = ss[0]
        return ss



#=======================================================================
# Test program:
#=======================================================================

if __name__ == '__main__':
    ns = NodeScope()
    sc = SolverChain(ns)

    if 0:
        import Meow
        num_stations = 3
        ANTENNAS = range(1,num_stations+1)
        array = Meow.IfrArray(ns,ANTENNAS)
        observation = Meow.Observation(ns)
        allsky = Meow.Patch(ns,'nominall',observation.phase_centre)
        cohset = allsky.visibilities(array, observation)
        sc = SolverChain(ns, label='test', array=array)
        sc.cohset(cohset)
        sc.cohset_list (cohset, ifrs=array.ifrs())

    if 1:
        sc.visumap('mode')
        sc.visumap('mode', 'off')
        sc.visumap('mode', 'full')
        sc.visumap('mode', 'min')
        sc.visumap('ifr', [(1,4)])
        sc.visumap('ifr', (1,4))

    if 0:
        sc.append(ns << Meq.Parm(0, tags='tag0'))
        sc.append(ns << Meq.Parm(1, tags='tag0'))
        sc.display()
        # ss = ns.Search(tags='tag0', return_names=True)
        # print ss

    if 0:
        cc = sc.make_condeqs(measured=None, predicted=cohset)
        # sc.select_index (cc, index=0, tag='XX')
        # dcoll = sc.dataConcat(cc)

    if 0:
        solver = sc.make_solver(scope='tag0', parm_tags='tag0',
                                measured=None, predicted=cohset)

    if 0:
        cs = sc.insert_reqseq ()
        for ifr in array.ifrs():
            print ifr,':',cs(*ifr)

    if 1:
        sc.display()


#=======================================================================
# Remarks:

#=======================================================================
