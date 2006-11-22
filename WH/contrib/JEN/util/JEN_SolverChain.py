# file: ../JEN/util/JEN_SolverChain.py
# An object to help constructing a solver sequence with visualisation


from Timba.TDL import *
from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect
from Timba.Contrib.JEN import MG_JEN_historyCollect

# Global counter used to generate unique node-names
unique = -1

class SolverChain (object):
    
    def __init__(self, ns, label=None):
        self.ns = ns
        self._clear(label=label)

    def _clear(self, label=None):
        """Clear the object"""
        self._label = label
        self._scope = None
        self._reqseq_children = []
        self._bookmark = dict()
        self._cxparm = dict()
        self._visumap = dict()
        # self.display('cleared')
        return True

    def scope(self, new=None):
        """Get/set the scope (string) that is used to generate node-names"""
        if new: self._scope = new
        return self._scope

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


    def insert_into_cohset (self, cohset=None, ifrs=None, clear=True):
        """Make the reqseq node(s) and insert in the cohset (...).
        The reqseq that executes the solvers in order of creation,
        and then passes on the final residuals (in new cohset).
        NB: ifrs = array.ifrs()"""
        n = len(self._reqseq_children)
        self._reqseq_children.append(0)               # placeholder 
        for ifr in ifrs:
            self._reqseq_children[n] = cohset(*ifr)   # fill in the placeholder
            self.ns.reqseq_SolverChain(*ifr) << Meq.ReqSeq(children=self._reqseq_children,
                                                           result_index=n,
                                                           cache_num_active_parents=1)
        if True: self.display('insert_into_cohset')

        # Make the new cohset, and return it:
        cohset = self.ns.reqseq_SolverChain
        self.make_bookmarks()
        if clear: self._clear()                       # ....??
        return cohset

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

    def visumap(self, key=None, value=None, mode=None, clear=True):
        """Interaction with the 'visualisation map', which enables the
        various inbuilt visualisation possibilities of this object"""
        if len(self._visumap)==0:
            self._visumap['mode'] = 'off' 
            self._visumap['peel'] = False 
            self._visumap['unpeel'] = False 
            self._visumap['condeq'] = False 
            self._visumap['solver'] = False 
            self._visumap['ifr'] = [] 
        if not isinstance(key, str):
            if clear: self._visumap = dict()
            return self._visumap
        if not value:
            if self._visumap.has_key(key):
                return self._visumap[key]
            else:
                return False
        self._visumap.setdefault(key, [])
        if clear: self._visumap[key] = []
        self._visumap[key].append(value)
        

    def visumap_bookmark(self, node=None, key='ifr', value=None):
        """Make a bookmark of the node if value is in _visumap[key]"""
        if self._visumap.has_key(key):
            if isinstance(self._visumap[key], (list,tuple)):
                if value in self._visumap[key]:
                    self.bookmark(node, key+'_'+str(value))
        return True


    #--------------------------------------------------------------------------
    # solver-related methods:
    #--------------------------------------------------------------------------

    def make_solver (self, scope=None,
                     parm_tags=None, parm_group='Parm',
                     ifrs=None, measured=None, predicted=None,
                     num_iter=3):
        """Create a solver node for the specified (parm_tags) MeqParms,
        making condeqs from the given cohsets (measured and predicted),
        and append it to the list of reqseq children"""
        scope = self.scope(scope)
        condeqs = self.make_condeqs (ifrs=ifrs, measured=measured,
                                     predicted=predicted,
                                     select='all')
        solvables = self.ns.Search(tags=parm_tags, class_name='MeqParm',
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
            solver = self.ns.solver(scope) << Meq.Solver(children=condeqs,
                                                         solvable=solvables,
                                                         debug_file=debug_file,
                                                         parm_group=hiid(parm_group),
                                                         # child_poll_order=cpo,
                                                         num_iter=num_iter)

            # Append the solver to the internal list of reqseq children: 
            self.append(solver)
            self.bookmark(solver, 'solvers')
            self.hcoll_solver_metrics(solver)
            
            # Visualisation:
            dcoll = self.dataConcat(condeqs, tag='condeqs', errorbars=True)
            self.bookmark(dcoll, 'condeqs')
            if self._cxparm.has_key(scope):
                solvables = self._cxparm[scope] 
            dcoll = self.dataCollect(solvables, tag='solvables')
            self.bookmark(dcoll, 'solvables')
        return solver

    #...........................................................................

    def make_condeqs (self, ifrs=None, measured=None, predicted=None, select='all'):
        """Create a list of (selected) condeq nodes from the given cohsets
        (measured and predicted)"""
        cc = []
        scope = self.scope()
        for ifr in ifrs:
            condeq = self.ns.condeq(scope)(*ifr) << Meq.Condeq(predicted(*ifr),
                                                               measured(*ifr))
            cc.append(condeq)
            self.visumap_bookmark(condeq, key='ifr', value=ifr)
            # self.selected_hcoll(condeq, key='ifr', value=ifr)
        # Return a list of zero or more condeq nodes:
        return cc

    #...........................................................................

    def peel (self, ifrs=None, cohset=None, subtract=None):
        """Subtract (peel) a cohset (e.g. a source) from the given cohset"""
        scope = self.scope()
        for ifr in ifrs:
            node = self.ns.peeled(scope)(*ifr) << Meq.Subtract(cohset(*ifr),subtract(*ifr))
            self.visumap_bookmark(node, key='ifr', value=ifr)
        cohset = self.ns.peeled(scope)           
        self.visualize_cohset (cohset, ifrs, tag='peeled',
                               plot_type='spectra', errorbars=True)
        return cohset

    #...........................................................................

    def unpeel (self, scope=None, ifrs=None, cohset=None, add=None):
        """Add (unpeel/restore) a cohset (e.g. a source) to the given cohset"""
        scope = self.scope(scope)
        for ifr in ifrs:
            unpeel = self.ns << Meq.Stripper(add(*ifr))
            node = self.ns.unpeeled(scope)(*ifr) << Meq.Add(cohset(*ifr), unpeel)
            self.visumap_bookmark(node, key='ifr', value=ifr)
        cohset = self.ns.unpeeled(scope)              
        self.visualize_cohset (cohset, ifrs, tag='unpeeled', errorbars=True)
        return cohset


    #--------------------------------------------------------------------------
    # Visualisation:
    #--------------------------------------------------------------------------

    def visualize_cohset (self, cohset=None, ifrs=None, tag='cohset',
                          plot_type='realvsimag', errorbars=False):
        """Visualise the given cohset"""
        # scope = self.scope()
        nodelist = self.cohset_list (cohset, ifrs, select='all')
        dcoll = self.dataConcat (nodelist, tag=tag,
                                 plot_type=plot_type, errorbars=errorbars)
        self.bookmark(dcoll, tag)
        return dcoll


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
            rr = MG_JEN_dataCollect.dcoll (self.ns, cc, 
                                           scope=scope, tag=corrs[i],
                                           color=color[i], style=style[i],
                                           size=8, pen=2,
                                           type=plot_type, errorbars=errorbars)
            dcolls.append(rr)
        # Make a combined plot of all the corrs:
        rr = MG_JEN_dataCollect.dconc(self.ns, dcolls, scope=scope,
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
        rr = MG_JEN_dataCollect.dcoll (self.ns, nodelist, 
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
                hcoll = MG_JEN_historyCollect.insert_hcoll(self.ns, node,
                                                           graft=False)
                self.bookmark(hcoll, key+'_'+str(value))
                self.append(hcoll)
        return True

    def hcoll_solver_metrics(self, solver):
        """Make historyCollect nodes for the specified solver"""
        scope = self.scope()
        hcoll = MG_JEN_historyCollect.make_hcoll_solver_metrics (self.ns, solver,
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
            if self.ns.select(tag).qadd(node[i]).initialized():
                increment = True
                s = self.ns.select(tag).qadd(node[i])(unique) << Meq.Selector(node[i], index=index)
            else:
                s = self.ns.select(tag).qadd(node[i]) << Meq.Selector(node[i], index=index)
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

    if 1:
        sc.append(ns << Meq.Parm(0, tags='tag0'))
        sc.append(ns << Meq.Parm(1, tags='tag0'))
        sc.display()
        # ss = ns.Search(tags='tag0', return_names=True)
        # print ss

    if 1:
        import Meow
        num_stations = 3
        ANTENNAS = range(1,num_stations+1)
        array = Meow.IfrArray(ns,ANTENNAS)
        observation = Meow.Observation(ns)
        allsky = Meow.Patch(ns,'nominall',observation.phase_centre)
        cohset = allsky.visibilities(array, observation)
        sc.cohset_list (cohset, ifrs=array.ifrs())

    if 1:
        cc = sc.make_condeqs(ifrs=array.ifrs(), scope='tag0',
                             measured=cohset, predicted=cohset)
        # sc.select_index (cc, index=0, tag='XX')
        dcoll = sc.dataConcat(cc)

    if 0:
        solver = sc.make_solver(scope='tag0', parm_tags='tag0',
                                ifrs=array.ifrs(), 
                                measured=cohset, predicted=cohset)

    if 0:
        cs = sc.insert_into_cohset (cohset, array.ifrs())
        for ifr in array.ifrs():
            print ifr,':',cs(*ifr)

    if 1:
        sc.display()


#=======================================================================
# Remarks:

#=======================================================================
