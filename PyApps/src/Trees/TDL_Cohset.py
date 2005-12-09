# TDL_Cohset.py
#
# Author: J.E.Noordam
#
# Short description:
#    A Cohset object encapsulates a set of 2x2 cohaerency matrices for a set of ifrs.
#
# History:
#    - 02 sep 2005: creation
#    - 23 sep 2005: added MeqVisDataMux to sink()
#    - 25 nov 2005: corr_index argument for .spigots()
#    - 29 nov 2005: added method: ReSampler()
#    - 03 dec 2005: replaced MG_JEN_exec with TDL_display
#    - 09 dec 2005: added method: coll()
#
# Full description:
#    A Cohset can also be seen as a 'travelling cohaerency front': For each ifr, it
#    contains the root node of a subtree. For each operation on a Cohset, each ifr
#    node is replaced by a new root node, which has the old one as one of its children.
#    Thus, a Cohset is used to build up a forest of parallel ifr subtrees,
#    somewhat like a line of spiders that leave parallel strands of silk.
#
#    A one-line description of each operation is added to the Cohset history,
#    which is attached to the forest state record (and can thus be inspected).
#    Similarly, a summary of the state of the Cohset at various important points,
#    and the contributing Joneset and Sixpack objects, are also attached to the
#    forest state record
#
#    An important functions of the Cohset is the transfer of information about
#    groups of solvable MeqParms from Joneset objects to a solver. This is done
#    by means of named 'solvegroups', which contain lists of 'parmgroup' names.
#    The latter contain lists of MeqParm node names, e.g. 'Gphase:s1=<s1>:s2=<s2>:q=3c84'.
#    A solver is defined by a list of one or more solvegroups, and solves for its
#    associated group of MeqParms. For an example, see MG_JEN_Cohset.py



#=================================================================================
# Preamble:
#=================================================================================

from Timba.TDL import *
from copy import deepcopy

from Timba.Trees import TDL_common
from Timba.Trees import TDL_radio_conventions
from Timba.Trees import TDL_Joneset



#**************************************************************************************
# Some useful helper functions:
#**************************************************************************************

def stations2ifrs(stations=range(3)):
    """Make a list of ifrs (station-pair tuples) from the given stations"""
    ifrs  = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ];
    return ifrs

def ifrs2stations(ifrs=[(0,1)]):
    """The reverse of stations2ifrs()"""
    stations = []
    for ii in ifrs:
        for i in ii:
            if not stations.__contains__(i): stations.append(i)
    stations.sort()
    return stations



#**************************************************************************************
# Class Cohset:
#**************************************************************************************

class Cohset (TDL_common.Super):
    """A Cohset object encapsulates a set of 2x2 cohaerency matrices for a set of ifrs"""
    
    def __init__(self, **pp):
        
        pp.setdefault('scope', '<scope>')
        pp.setdefault('punit', 'uvp')                   # prediction unit (source/patch)
        pp.setdefault('stations', range(0,3))
        pp.setdefault('ifrs', None)
        pp.setdefault('polrep', 'linear')
        pp.setdefault('MS_corr_index', [0,1,2,3])          # default: all 4 corrs
        pp.setdefault('phase_centre', '<radec>')

        self.__punit = pp['punit']
        self.__scope = pp['scope']

        TDL_common.Super.__init__(self, type='Cohset', **pp)


        # Make a record/dict of ifr-slots to hold the 2x2 coherency matrices:
        if isinstance(pp['ifrs'], list):
            # Assume that pp.ifrs has been given explicitly
            self.history('input: len(ifrs)='+str(len(pp['ifrs'])))
        elif isinstance(pp['stations'], list):
            self.history('input: stations='+str(pp['stations']))
            pp['ifrs'] = [ (s1,s2) for s1 in pp['stations'] for s2 in pp['stations'] if s1<s2 ]
        else:
            self.history(error=hist+'neither stations/ifrs specified')
            return F

        # The station_indexes are integers, used in spigot/sink:
        self.__station_index = {}
        for station in pp['stations']:
            key = TDL_radio_conventions.station_key(station)
            self.__station_index[key] = TDL_radio_conventions.station_index(station)


        # This is the ONLY place where the self.__coh field-keys are determined
        self.__stations = {}                     # integer tuples (s1,s2)
        self.__coh = {}
        for (st1,st2) in pp['ifrs']:
            key = TDL_radio_conventions.ifr_key(st1,st2)
            skey1 = TDL_radio_conventions.station_key(st1)
            skey2 = TDL_radio_conventions.station_key(st2)
            self.__stations[key] = (skey1,skey2)  
            self.__coh[key] = 'coh['+key+'] (placeholder for nodestub)'
            print key,self.__coh[key]
        self.__dims = [1]                        # shape of coh tensor nodes

        # Polarisation representation and available correlations:
        # A Cohset ALWAYS has 2x2 coherency matrices, but some of the elements may be invalid.
        # The latter is recognised by a negative value of the corresponding element(s)
        #   of the 4-element (2x2?) vector self.__MS_corr_index
        # See also self._corrs_derived() below
        self.__polrep = pp['polrep']
        self.__MS_corr_index = pp['MS_corr_index']     # e.g. [0,1,2,3] 
        self._corrs_derived()                          # derived from MS_corr_index

        # The Cohset contains the position (RA, Dec) of the current phase centre:
        self.__phase_centre = pp['phase_centre']

        # The Cohset may carry Joneset information for solvers:
        self.__parmgroup = dict()
        self.__solvegroup = dict()
        self.__condeq_corrs = dict()

        # The Cohset collects data/historyCollect nodes:
        self.__coll = []

        # Plot information (standard, but extended from Jonesets):
        self.__plot_color = TDL_radio_conventions.plot_color()
        self.__plot_style = TDL_radio_conventions.plot_style()
        self.__plot_size = TDL_radio_conventions.plot_size()
        self.__plot_pen = TDL_radio_conventions.plot_pen()



    #----------------------------------------------------------------------------
    # start of corrs-related functions
    #----------------------------------------------------------------------------

    def polrep(self):
        """The Cohset polarisation representation (linear/circular)"""
        return self.__polrep
    def MS_corr_index(self):
        """Return a list of 4 indices for the different correlations (XX etc).
        These are used by spigots and sinks to access corrs in the MS.
        Each index refers to the corr position in the MS storage array.
        A negative index means that the corr is not available in the MS"""
        return self.__MS_corr_index


    def _corrs_derived(self):
        """Calculate corrs-related quantities from polrep and MS_corr_index"""

        # NB: polrep and MS_corr_index apply to ALL ifrs. This is OK for the moment,
        #     but we should look ahead to Cohsets for dissimilar stations, where
        #     each ifr should have its own description (can of worms....)

        self.__corrnames = ['XX','XY','YX','YY']
        if self.__polrep == 'circular':
            self.__corrnames = ['RR','RL','LR','LL']
            
        self.__corrs = []                            # list of AVAILABLE corrs
        for i in range(len(self.__MS_corr_index)):
            icorr = self.__MS_corr_index[i]
            if icorr<0:                              # not available
                pass                                 # ignore....
            elif self.__polrep == 'circular':
                if i==0: self.__corrs.append('RR')
                if i==1: self.__corrs.append('RL')
                if i==2: self.__corrs.append('LR')
                if i==3: self.__corrs.append('LL')
            else:                                    # assume linear....
                self.__polrep == 'linear'            # just in case...
                if i==0: self.__corrs.append('XX')
                if i==1: self.__corrs.append('XY')
                if i==2: self.__corrs.append('YX')
                if i==3: self.__corrs.append('YY')
                
        self.__paral = []                            # list of AVAILABLE 'parallel' corrs
        self.__cross = []                            # list of AVAILABLE cross-corrs
        for corr in self.__corrs:
            if ['XX','YY','RR','LL'].__contains__(corr): self.__paral.append(corr)
            if ['XY','YX','RL','LR'].__contains__(corr): self.__cross.append(corr)
        return True

    def corrs(self):
        """Return a list of AVAILABLE correlation names (XX, RL etc)"""
        return self.__corrs
    def corrnames(self):
        """Return a list of polrep-related correlation names"""
        return self.__corrnames
    def cross(self):
        """Return a list of AVAILABLE cross-correlation names (XY, RL, etc)"""
        return self.__cross
    def paral(self):
        """Return a list of AVAILABLE parallel correlation names (XX, LL, etc)"""
        return self.__paral


    def corr_index(self, corrs='*'):
        """Get the index nrs of the AVAILABLE specified corr names."""
        corrsin = corrs                           # used for message only
        if isinstance(corrs, str):
            if corrs=='*': corrs = self.corrs()
            if corrs=='paral': corrs = self.paral()
            if corrs=='cross': corrs = self.cross()
        if not isinstance(corrs, (tuple,list)): corrs = [corrs]

        corrnames = self.corrnames()              # 4 corr names
        available = self.corrs()                  # 0-4 available corrs
        selected = []                             # selected corrs
        icorr = []
        for corr in corrs:
            if not available.__contains__(corr):
                print '**** corr',corr,'not available in:',available
                # return []                                          # escape...?
            else:
                index = corrnames.index(corr)     # index in 4-vector!
                icorr.append(index)
                selected.append(corr)
        # print '** Cohset.corr_index(',corrsin,'):',corrs,'->',icorr,' (from',available,'select',selected,')'
        return icorr

    #----------------------------------------------------------------------------
    # end of corrs-related functions
    #----------------------------------------------------------------------------


    def __getitem__(self, key):
        """Get a Cohset item by key or by index nr"""
        if isinstance(key, int): key = self.__coh.keys()[key]
        return self.__coh[key]

    def __setitem__(self, key, value):
        """Replace the named (key) item with value (usually a node)"""
        self.__coh[key] = value
        return self.__coh[key]

    def plot_color(self): return self.__plot_color
    def plot_style(self): return self.__plot_style
    def plot_size(self): return self.__plot_size
    def plot_pen(self): return self.__plot_pen

    def parmgroup(self):
        """Return a list of available MeqParm group names"""
        return self.__parmgroup
    def solvegroup(self):
        """Return a dict of named solvegroups"""
        return self.__solvegroup
    def condeq_corrs(self): return self.__condeq_corrs

    def phase_centre(self):
        """Return the current Cohset phase-centre (RA, DEC)"""
        return self.__phase_centre

    def scope(self, new=None):
        if isinstance(new, str): self.__scope = new
        return self.__scope
    def punit(self):
        """Return the predict-unit (source/patch) name"""
        return self.__punit
    def stations(self):
        """Return a list of available stations"""
        return self.__stations
    def station_index(self):
        """Return a list of station indices (used in spigots/sinks)"""
        return self.__station_index

    def keys(self):
        """Return a list of keys to the Cohset items"""
        return self.__coh.keys()
    def has_key(self, key, warning=None):
        """Check whether there is an item with the given key"""
        result = self.keys().__contains__(key)
        if not result and warning:
            print str(warning),': key not recognised:',key
        return result
    def len(self):
        """Return the nr of Cohset items"""
        return len(self.__coh)
    def dims(self):
        """Return the dimensions of the Cohset matrices (usually [2,2])""" 
        return self.__dims

    def nodenames(self, select='*'):
        """Return a list of the names of the current nodes in the Cohset"""
        nn = []
        for key in self.keys():
            if isinstance(self.__coh[key], str):
                nn.append(self.__coh[key])
            else:
                nn.append(self.__coh[key].name)
        if len(nn)==0: return '<empty>'
        if select=='first': return nn[0]
        if select=='last': return nn[len(nn)-1]
        return nn

    def oneliner(self):
        """Return a one-line summary of the Cohset"""
        s = TDL_common.Super.oneliner(self)
        # s = s+' scope='+str(self.scope())
        # s = s+' punit='+str(self.punit())
        # s = s+' dims='+str(self.dims())
        s = s+' '+str(self.scope())
        # s = s+' '+str(self.dims())
        s = s+' '+str(self.punit())
        s = s+' '+str(self.corrs())
        # s = s+' len='+str(self.len())
        s = s+' ['+str(self.len())+']'
        s = s+' ('+str(self.nodenames('first'))+',...)'
        return s

    def display(self, txt=None, full=False):
        """Display (print) the contents of the Cohset"""
        ss = TDL_common.Super.display(self, txt=txt, end=False)
        indent1 = 2*' '
        indent2 = 6*' '
        ss.append(indent1+' - phase_centre:    '+self.phase_centre())
        polrep = self.polrep()+'  '+str(self.corrnames())
        polrep += '   (MS_corr_index='+str(self.MS_corr_index())+')'
        ss.append(indent1+' - polrep:          '+polrep)
        corrs = str(self.corrs())
        corrs += '   paral='+str(self.paral())
        corrs += '   cross='+str(self.cross())
        ss.append(indent1+' - available corrs: '+corrs)
        ss.append(indent1+' - station_index:   '+str(self.station_index()))
        ss.append(indent1+' - plot_color:      '+str(self.plot_color()))
        ss.append(indent1+' - plot_style:      '+str(self.plot_style()))
        ss.append(indent1+' - plot_size:       '+str(self.plot_size()))
        ss.append(indent1+' - plot_pen:        '+str(self.plot_pen()))
        ss.append(indent1+' - Parmgroups:      '+str(self.parmgroup().keys()))
        ss.append(indent1+' - Solvegroups:     '+str(self.solvegroup().keys()))
        ss.append(indent1+' - Condeq_corrs:    '+str(self.condeq_corrs().keys()))
        ss.append(indent1+' - Available 2x2 cohaerency matrices ( '+str(self.len())+' ):')
        if full or self.len()<10:
            for key in self.__coh.keys():
                s12 = self.__stations[key]
                ss.append(indent2+' - '+key+str(s12)+' : '+str(self.__coh[key]))
        else:
            keys = self.__coh.keys()
            n = len(keys)-1
            ss.append(indent2+' - first: '+keys[0]+' : '+str(self.__coh[keys[0]]))
            ss.append(indent2+'   ....')
            ss.append(indent2+' - last:  '+keys[n]+' : '+str(self.__coh[keys[n]]))
        ss.append(indent1+' - Collected dcoll/hcoll nodes ( '+str(len(self.__coll))+' ):')
        for coll in self.coll():
            ss.append(indent2+' - '+str(coll))       
        return TDL_common.Super.display_end(self, ss)


    def coll(self, new=None, clear=False):
        """Interaction with collected hcoll/dcoll nodes"""
        if clear: self.__coll = []  # clear the collection
        if new:                     # add new item(s) to the collection
            if isinstance(new, (tuple, list)):
                self.__coll.extend(new)
            else:
                self.__coll.append(new)
        return self.__coll          # Return a list of the current collection


    #--------------------------------------------------------------
    # Methods that generate new nodes (and thus require nodescope):
    #--------------------------------------------------------------

    def nodes(self, select='*'):
        """Return a list of the current cohearency nodes in the Cohset"""
        # Used in MG_JEN_Cohset.spigots() and .sinks()
        # Consider merging with self.coh() below
        nn = []
        for key in self.keys():
            nn.append(self.__coh[key])
        if len(nn)==0: return '<empty>'
        if select=='first': return nn[0]
        if select=='last': return nn[len(nn)-1]
        return nn

    def coh (self, key=None, corrs='*', ns=None, name=None):
        """Get a named (key) cohearency node (tensor), optionally for selected corrs""" 
        funcname = '::coh():'

        # Unfinished: Return list of cohs, e.g. key='*'
        # See also self.nodes() above....
        # if False:
            # keys = key
            # if isinstance(keys, str):
                # if keys=='*': keys = self.keys()
            # if not isinstance(keys, (list, tuple)): keys = [keys]
            
        # Check the specified key(s) (name):
        if not self.has_key(key, warning=funcname): return False

        # Check the specified corr selection:
        if isinstance(corrs, str):
            if corrs=='*': return self.__coh[key]  # no selection needed
        icorr = self.corr_index(corrs)
        if len(icorr)==4: return self.__coh[key]     # no selection needed
        if len(icorr)==0: return False               # none specified/available (error)

        # Make MeqSelector nodes that select the specified corrs:
        multi = (len(icorr)>1)                       # Kludge, to tell MeqSelector that icorr is multiple... 
        uniqual = _counter(funcname, increment=-1)
        s12 = self.__stations[key]
        if not isinstance(name, str):
            name = 'selcorr_'+self.scope()             
        coh = ns[name](uniqual)(corrs)(s1=s12[0], s2=s12[1]) << Meq.Selector(self.__coh[key],
                                                                             index=icorr, multi=multi)
        return coh                                   # return the node

    def zero(self, ns):
        """Make zero coherency matrices for all ifrs"""
        funcname = '::zero():'
        c0 = complex(0)
        zz = array([c0,c0,c0,c0])
        for key in self.keys():
            s12 = self.__stations[key]
            self.__coh[key] = ns.cxzero22(s1=s12[0], s2=s12[1]) << Meq.Constant(zz, dims=[2,2])
        self.__dims = [2,2]
        self.history(append=funcname+' -> '+self.oneliner())

    def unity(self, ns):
        """Make unit coherency matrices for all ifrs"""
        funcname = '::unity():'
        c0 = complex(0.0)
        c1 = complex(1.0)
        zz = array([c1,c0,c0,c1])
        for key in self.keys():
            s12 = self.__stations[key]
            self.__coh[key] = ns.cxunity22(s1=s12[0], s2=s12[1]) << Meq.Constant(zz, dims=[2,2])
        self.__dims = [2,2]
        self.history(append=funcname+' -> '+self.oneliner())

    def uniform(self, ns, coh22):
        """Uniform coherency matrices (coh22) for all ifrs(qual)"""
        funcname = '::uniform():'
        uniqual = _counter(funcname, increment=-1)
        for key in self.keys():
            s12 = self.__stations[key]
            self.__coh[key] = ns.uniform(uniqual)(s1=s12[0], s2=s12[1]) << Meq.Selector(coh22)
        self.__dims = [2,2]
        self.history(append=funcname+' -> '+self.oneliner())


    def graft(self, ns, node, name=None, key='*', stepchild=False):
        """Graft the specified node(s) onto the streams of the specified ifr(s).
        By default, this is done by means of a MeqReqSeq, which obly uses the result
        of its LAST (main-stream) child. This synchronises the ifr-streams if the
        same node (e.g. a solver or a dcoll) is grafted on all ifr-streams.
        If stepchild=True, make the node(s) step-children of a MeqSelector
        node that is inserted before the specified (key) coherency node"""
        funcname = '::graft():'

        # Names and qualifiers:
        uniqual = _counter(funcname, increment=-1)
        if stepchild:
            gname = 'graft_stepchild'
        else:
            gname = 'graft_reqseq'
        if isinstance(name, str): gname += '_'+name

        # Deal with the input node(s) that are to be grafted on:
        # Make a deepcopy to avoid the risk of modifying the input node.
        gg = deepcopy(node)                                 # necessary....??
        if not isinstance(gg, (tuple, list)): gg = [gg]
        self.history(funcname+' '+gname+': len(gg)='+str(len(gg)))
        if False:
            # To improve tree readability, bundle the input nodes...
            # NB: This assumes that the order is not important
            if len(gg)>1:
                gg = [ns[gname+'_bundle'](uniqual) << Meq.Composer(children=gg)]

        
        # NB: Consider new options: add_children(...) or add_stepchildren(...)
        #     See also PyApps/test/tdl_tutorial.py

        # OK, graft onto all ifr-branches:
        keys = self.keys()
        if key=='first': keys = keys[0]                     # use the first ifr only
        if key=='last': keys = keys[len(keys)-1]            # use the last ifr only
        for key in keys:
            if stepchild:
                self[key] = ns[gname].qmerge(self[key])(uniqual) << Meq.Selector(self[key], stepchildren=gg)
            else:
                # children = gg                               # first the grafted node(s) (e.g. dcoll)
                children = deepcopy(gg)                     # NECESSARY (for some reason I do not understand)
                children.append(self[key])                  # the main stream node is last (result_index)
                rix = len(children)-1                       # use only the result of the last (main stream) child
                self[key] = ns[gname].qmerge(self[key])(uniqual) << Meq.ReqSeq(children=children, result_index=rix)

        self.history(funcname+' -> '+self.oneliner())
        return True

        

    def unop(self, ns, unop=None, right2left=False):
        """Perform the specified (sequence of) unary operations (in place)"""
        funcname = '::unop('+str(unop)+'):'
        if Cohset == None: return False
        if unop == None: return False
        if isinstance(unop, bool): return False
        if isinstance(unop, str): unop = [unop]
        if not isinstance(unop, (tuple,list)): return False
        if len(unop)==0: return False
        unops = unop                      # avoid mutation of unop
        if right2left: unops.reverse()    # perform in right2left order (more intuitive?)
        for key in self.keys():
            for unop1 in unops:       
                if isinstance(unop1, str):
                    self.__coh[key] = ns << getattr(Meq, unop1)(self.__coh[key])
        self.history(append=funcname+' -> '+self.oneliner())
        return True


    def binop(self, ns, binop='Subtract', Cohset=None):
        """Perform the specified binary operation on two Cohsets (in place)"""
        if Cohset == None: return False
        funcname = '::binop('+str(binop)+','+Cohset.label()+'):'
        if not isinstance(binop, str): return False
        for key in self.keys():
            self.__coh[key] = ns << getattr(Meq, binop)(self.__coh[key], Cohset[key])
        self.history(append=funcname+' -> '+self.oneliner())
        return True


    def subtract(self, ns, Cohset=None):
        """Subtract the cohaerencies of the given Cohset from the corresponding internal ones"""
        # NB: Check whether punit is the same for both?
        funcname = '::subtract():'
        self.scope('subtracted')
        return self.binop(ns, binop='Subtract', Cohset=Cohset)


    def add(self, ns, Cohset=[], exclude_itself=False):
        """Add the cohaerencies of the given (list of) Cohset(s)"""
        funcname = '::add():'
        if not isinstance(Cohset, (tuple,list)): Cohset = [Cohset]
        if len(Cohset)==0: return True                 # no change

        # Modify the internal cohaerencies:
        uniqual = _counter(funcname, increment=-1)
        for key in self.keys():
            cc = [self.__coh[key]]                     # include itself (default)
            if exclude_itself: cc = []                 # exclude itself
            for cs in Cohset: cc.append(cs[key])       # collect corresponding (key) nodes
            if len(cc)==1:
                self.__coh[key] = cc[0][key]           # just use the first
            else:
                self.__coh[key] = ns.cohsum.qmerge(self.__coh[key])(uniqual) << Meq.Add(children=cc)

        # Reporting and book-keeping
        n = len(Cohset)
        if exclude_itself:
            self.scope('cohsum')
            self.label('cohsum')                
            self.history(append=funcname+' replace by sum of '+str(n)+' Cohsets:')
        else:
            self.scope('added')
            self.history(append=funcname+' add '+str(n)+' Cohset(s) to itself:')
        for cs in Cohset:
            self.history(append=funcname+' ...... '+cs.oneliner())
        self.history(append=funcname+' -> '+self.oneliner())
        return True


    def shift_phase_centre(self, ns, punit=None):
        """Shift the phase centre from the current position to the position (RA, DEC)
        of the given punit (sixpack?, twopack?, other?)"""
        self.__punit = punit
        self.scope('shifted_to_'+punit)
        pass


    def correct(self, ns, Joneset=None):
        """Correct the Cohset by matrix multiplication with the INVERSE of the given Joneset"""
        funcname = '::correct():'
        uniqual = _counter(funcname, increment=-1)
        self.__punit = Joneset.punit()
        scope = 'corrected_'+Joneset.jchar()
        for key in self.keys():
            s12 = self.__stations[key]
            coh = ns[scope](uniqual)(s1=s12[0], s2=s12[1], q=self.punit()) << Meq.MatrixMultiply(
                Meq.MatrixInvert22(Joneset[s12[0]]),
                self.__coh[key],
                ns << Meq.MatrixInvert22(ns << Meq.ConjTranspose(Joneset[s12[1]]))) 
            self.__coh[key] = coh 
        self.update_from_Joneset(Joneset)
        self.scope(scope)
        self.history(append='corrected by: '+Joneset.oneliner())
        self.history(append=funcname+' -> '+self.oneliner())
        return True

    def corrupt(self, ns, Joneset=None):
        """Corrupt the Cohset by matrix multiplication with the given Joneset"""
        funcname = '::corrupt():'
        uniqual = _counter(funcname, increment=-1)
        self.__punit = Joneset.punit()
        scope = 'corrupted_'+Joneset.jchar()
        for key in self.keys():
            s12 = self.__stations[key]
            coh = ns[scope](uniqual)(s1=s12[0], s2=s12[1], q=self.punit()) << Meq.MatrixMultiply(
                Joneset[s12[0]],
                self.__coh[key],
                ns << Meq.ConjTranspose(Joneset[s12[1]]))   
            self.__coh[key] = coh
        self.scope(scope)
        self.update_from_Joneset(Joneset)
        self.history(append='corrupted by: '+Joneset.oneliner())
        self.history(append=funcname+' -> '+self.oneliner())
        return True


    def ReSampler (self, ns, **pp):
        """Insert a ReSampler node that ignores the result cells of its child,
        but resamples them onto the cells of the request domain"""
        funcname = '::ReSampler():'
        pp.setdefault('flag_bit', 4)                     # .....
        pp.setdefault('flag_mask', 3)                    # .....
        pp.setdefault('flag_density', 0.1)               # .....
        pp = record(pp)
        uniqual = _counter(funcname, increment=-1)
        scope = 'ReSampled'
        for key in self.keys():
            s12 = self.__stations[key]
            coh = ns[scope](uniqual)(s1=s12[0], s2=s12[1], q=self.punit()) << Meq.ReSampler(
                self.__coh[key],
                flag_mask=pp['flag_mask'],
                flag_bit=pp['flag_bit'],
                flag_density=pp['flag_density'])
            self.__coh[key] = coh
        self.scope(scope)
        self.history(append=funcname+' inarg = '+str(pp))
        self.history(append=funcname+' -> '+self.oneliner())
        return True


    def update_from_Joneset(self, Joneset=None):
        """Update the internal info from another Joneset object"""
        # (see Joneseq.Joneset())
        if Joneset==None: return False
        if Joneset.solvable():
            self.__parmgroup.update(Joneset.parmgroup())
            self.__solvegroup.update(Joneset.solvegroup())
            self.__condeq_corrs.update(Joneset.condeq_corrs())
            self.__plot_color.update(Joneset.plot_color())
            self.__plot_style.update(Joneset.plot_style())
            self.__plot_size.update(Joneset.plot_size())
            self.history(append='updated from (solvable): '+Joneset.oneliner())
        else:
            # A Joneset that is not solvable has no solvegroups.
            # However, its parmgroups might interfere with parmgroups
            # of the same name (e.g. Gphase) from solvable Jonesets.
            # Therefore, its parm info should not be copied here.
            self.history(append='updated from (not solvable): '+Joneset.oneliner())
        return True


    def update_from_Cohset(self, Cohset=None):
        """Update the internal info from another Cohset object"""
        if Cohset==None: return False
        self.__parmgroup.update(Cohset.parmgroup())
        self.__solvegroup.update(Cohset.solvegroup())
        self.__condeq_corrs.update(Cohset.condeq_corrs())
        self.__plot_color.update(Cohset.plot_color())
        self.__plot_style.update(Cohset.plot_style())
        self.__plot_size.update(Cohset.plot_size())
        self.history(append='updated from: '+Cohset.oneliner())
        return True



#======================================================================================

    def spigots (self, ns=0, **pp):
        """Fill the Cohset with spigot nodes for all its ifrs"""
        funcname = '::spigots():'

        # Input arguments:
        pp.setdefault('flag_bit', 4)                     # .....
        pp.setdefault('MS_corr_index', [0,1,2,3])           # default: all 4 corr
        pp.setdefault('input_column', 'DATA')            # .....
        pp = record(pp)

        # Deal with available/wanted correlations:
        # For XX/YY only, use:
        # - If only XX/YY available: pp['MS_corr_index'] = [0,-1,-1,1]
        # - If all 4 corr available: pp['MS_corr_index'] = [0,-1,-1,3]
        # - etc
        # Still returns a 2x2 tensor node, but with empty results {} for missing corrs
        # Empty results {} are interpreted as zeroes, e.g. in matrix multiplication.
        # NB: after that, the results ar no longer empty, so that cannot be used
        #   detecting missing corrs!! Use the Cohset field: ....
        # NB: Empty results are ignored by condeqs etc
        # See also the wiki-pages...
        
        # Make a record/dict of spigots that produce 2x2 coherency matrices:
        for key in self.keys():
            s12 = self.__stations[key]
            i1 = self.station_index()[str(s12[0])]              # integer
            i2 = self.station_index()[str(s12[1])]              # integer
            self.__coh[key] = ns.spigot(s1=s12[0],s2=s12[1]) << Meq.Spigot(station_1_index=i1,
                                                                           station_2_index=i2,
                                                                           corr_index=pp['MS_corr_index'],
                                                                           flag_bit=pp['flag_bit'],
                                                                           input_column=pp['input_column'])
            # print funcname, key,s12,i1,i2,i1+i2,self.__coh[key]

        # Update Cohset control fields:
        self.__MS_corr_index = pp['MS_corr_index']              # 
        self.__dims = [2,2]                                     # 
        self._corrs_derived()                                   # derived from MS_corr_index

        self.label('spigot')
        self.scope('spigot')
        self.history(append=funcname+' inarg = '+str(pp))
        self.history(append=funcname+' -> '+self.oneliner())
        return True

#------------------------------------------------------------------------------------

    def sinks (self, ns, **pp):
        """Attaches the Cohset coherency matrices to MeqSink nodes""" 
        funcname = '::sinks():'

        # Input arguments:
        pp.setdefault('output_col', 'PREDICT')          # name of MS output column (NONE means inhibited)
        pp.setdefault('start', None)                    # optional child of MeqVisDataMux
        pp.setdefault('pre', None)                      # optional child of MeqVisDataMux
        pp.setdefault('post', None)                     # optional child of MeqVisDataMux
        # pp = record(pp)                  # ...record(pp) drops the None fields....!  Seem OK now...
        # print funcname,' pp=\n',pp,'\n'
        # print 'pp[post] =',type(pp['post'])

        # Mapping to MS correlations (see self.spigots() above)
        # MS_corr_index = [0,1,2,3]                        # default
        MS_corr_index = self.MS_corr_index()                  # defined in self.spigots()

        # Make separate sinks for each ifr:
        for key in self.keys():
            s12 = self.__stations[key]
            i1 = self.station_index()[str(s12[0])]              # integer
            i2 = self.station_index()[str(s12[1])]              # integer
            self.__coh[key] = ns.MeqSink(s1=s12[0], s2=s12[1]) << Meq.Sink(self.__coh[key],
                                                                           station_1_index=i1,
                                                                           station_2_index=i2,
                                                                           corr_index=MS_corr_index,
                                                                           output_col=pp['output_col'])
            # print funcname, key,s12,i1,i2,i1+i2,self.__coh[key]

        # Explicitly create a MeqVisDataMux node that issues requests to MeqSinks
        # (NB: If omitted, it is created implicitly by the system)
        # It has three optional children:
        # - child 'start' gets a request before the spigots are filled
        # - child 'pre' gets a request before the MeqSinks
        #   (may be used to attach a MeqSolver, or its MeqReqSeq)
        # - child 'post' gets a request after the MeqSinks have returned a result 
        #   (may be used to attach all MeqDataCollect nodes)
        if True:
            for key in ['start','pre','post']:
                if isinstance(pp[key], (list,tuple)):
                    if len(pp[key])>0:
                        pp[key] = ns[key+'_VisDataMux'] << Meq.ReqSeq(children=pp[key])
                        # pp[key] = ns[key+'_VisDataMux'] << Meq.Add(children=pp[key])
            root = ns.VisDataMux << Meq.VisDataMux(start=pp['start'],
                                                   pre=pp['pre'], post=pp['post'])
        

        self.scope('sink')
        self.history(append=funcname+' inarg = '+str(pp))
        self.history(append=funcname+' MS_corr_index = '+str(MS_corr_index))
        self.history(append=funcname+' -> '+self.oneliner())
        return True

#------------------------------------------------------------------------------------

    def simul_sink (self, ns):
        """makes a common root node for all entries in Cohset""" 
        cc = []
        for key in self.keys(): cc.append(self.__coh[key])
        return ns.simul_sink << Meq.Add(children=cc)




#========================================================================
# Helper routines:
#========================================================================

# Counter service (use to automatically generate unique node names)

_counters = {}

def _counter (key, increment=0, reset=False, trace=False):
    global _counters
    _counters.setdefault(key, 0)
    if reset: _counters[key] = 0
    _counters[key] += increment
    if trace: print '** Cohset: _counters(',key,') =',_counters[key]
    return _counters[key]






#========================================================================
# Test routine:
#========================================================================

if __name__ == '__main__':
    print '\n*******************\n** Local test of: TDL_Cohset.py:\n'
    from numarray import *
    from Timba.Contrib.JEN import MG_JEN_Cohset
    from Timba.Trees import TDL_display
    # from Timba.Trees import JEN_record
    ns = NodeScope()
    nsim = ns.Subscope('_')
    
    stations = range(4)
    ifrs = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ]
    polrep = 'linear'
    # polrep = 'circular'
    cs = Cohset(label='initial', polrep=polrep, stations=stations)
    cs.display('initial')

    if 0:
        cs.zero(ns)
        cs.display('zero')

    if 0:
        print '** dir(cs) ->',dir(cs)
        print '** cs.__doc__ ->',cs.__doc__
        print '** cs.__module__ ->',cs.__module__
        print


    if 1:
        MS_corr_index = [0,1,2,3]         # all 4 available (default)
        # MS_corr_index = [-1,1,2,-1]       # all 4 available, but only XY/XY wanted
        # MS_corr_index = [0,-1,-1,1]       # only XX/YY available
        # MS_corr_index = [0,-1,-1,3]       # all 4 available, but only XX/YY wanted
        cs.spigots(ns, MS_corr_index=MS_corr_index)
        cs.display('spigots')

    if 0:
        coll = cs.coll(ns << Meq.DataCollect())
        coll = cs.coll(ns << Meq.HistoryCollect())
        cs.coll(clear=True)

    if 0:
        cs.ReSampler(ns)

    if 0:
        print '\n** cs.corr_index():'
        cs.corr_index()
        cs.corr_index('*')
        cs.corr_index('paral')
        cs.corr_index('cross')
        cs.corr_index('XX')
        cs.corr_index('XY')
        cs.corr_index('YX')
        cs.corr_index('YY')
        cs.corr_index(['XX','YY'])
        cs.corr_index(['XY','YX'])
        cs.corr_index('RL')
        cs.corr_index(['XX','RL'])
        print

    if 0:
        corrs = '*'
        corrs = ['XX','YY']
        # corrs = ['XY','YX']
        print '\n** cs.coh(key, corrs):'
        for key in cs.keys():
            coh = cs.coh(key, corrs=corrs, ns=ns)
            print '- cs.coh(',key, corrs,') ->',coh
        TDL_display.subtree(coh, 'last coh', full=True, recurse=5)
        print

    if 0:
        zero = ns.zero << 0.0
        minus = ns.minus << -1
        cs.graft(ns, [zero, minus], name='test', key='*', stepchild=False)
        cs.display('graft')

    if 0:
        cs.zero(ns)
        cs1 = Cohset(label='other', polrep='circular', stations=stations)
        cs1.unity(ns)
        cc = [cs1,cs1,cs1]
        cs.add(ns, cc)
        cs.display('exclude_itself=False')
        cs.add(ns, cc, exclude_itself=True)
        cs.display('exclude_itself=True')
        
    if 0:
        cs.sinks(ns)
        sink = cs.simul_sink(ns)
        TDL_display.subtree(sink, 'simul_sink', full=True, recurse=5)

    if 0:
        dd = dict(aa=1, bb=2, cc=None, dd=5)
        print 'dd =',dd
        pp = record(dd)
        print 'pp =',pp
        
        
    if 1:
        # Display the final result:
        k = 0 ; TDL_display.subtree(cs[k], 'cs['+str(k)+']', full=True, recurse=5)
        cs.display('final result')
    print '\n*******************\n** End of local test of: TDL_Cohset.py:\n'



#============================================================================================









 

