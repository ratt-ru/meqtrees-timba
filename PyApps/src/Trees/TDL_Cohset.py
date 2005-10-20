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
        pp.setdefault('punit', 'uvp')             # prediction unit (source/patch)
        pp.setdefault('stations', range(0,3))
        pp.setdefault('ifrs', None)
        pp.setdefault('polrep', 'linear')
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

        # Polarisation representation
        self.__polrep = pp['polrep']
        self.__corrs = ['XX', 'XY', 'YX', 'YY']
        self.__corr_index = [0,1,2,3]            # used in spigot/sink 
        if self.__polrep == 'circular':
            self.__corrs = ['RR', 'RL', 'LR', 'LL']

        # The Cohset contains the position (RA, Dec) of the current phase centre:
        self.__phase_centre = pp['phase_centre']

        # The Cohset may carry Joneset information for solvers:
        self.__parmgroup = dict()
        self.__solvegroup = dict()
        self.__condeq_corrs = dict()

        # Plot information (standard, but extended from Jonesets):
        self.__plot_color = TDL_radio_conventions.plot_color()
        self.__plot_style = TDL_radio_conventions.plot_style()
        self.__plot_size = TDL_radio_conventions.plot_size()
        self.__plot_pen = TDL_radio_conventions.plot_pen()

        # Calculate derived values from primary ones
        self.calc_derived()



    def calc_derived(self):
        """Calculate derived values from primary ones"""
        self.__paral = []
        self.__cross = []
        for corr in self.__corrs:
            if ['XX','YY','RR','LL'].__contains__(corr): self.__paral.append(corr)
            if ['XY','YX','RL','LR'].__contains__(corr): self.__cross.append(corr)
        return True

    def __getitem__(self, key):
        """Get a Cohset item by key or by index nr"""
        if isinstance(key, int): key = self.__coh.keys()[key]
        return self.__coh[key]

    def __setitem__(self, key, value):
        """Replace the named (key) item with value (usually a node)"""
        self.__coh[key] = value
        return self.__coh[key]

    # Access to class attribites:
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

    # Access to instance attribites:
    def polrep(self):
        """The Cohset polarisation representation (linear/circular)"""
        return self.__polrep
    def corrs(self):
        """Return a list of correlation names (XX, RL etc)"""
        return self.__corrs
    def corr_index(self):
        """Return a list of correlation indices for spigot/sink"""
        return self.__corr_index
    def cross(self):
        """Return a list of cross-correlation names (XY, RL, etc)"""
        return self.__cross
    def paral(self):
        """Return a list of parallel correlation names (XX, LL, etc)"""
        return self.__paral
    def phase_centre(self):
        """Return the current Cohset phase-centre (RA, DEC)"""
        return self.__phase_centre

    def scope(self, new=None):
        if isinstance(new, str): self.__scope = new
        return self.__scope
    def punit(self):
        """Return the predict-unit (source/patch) name"""
        return self.__punit
    def coh(self):
        """Access to the Cohset itself"""
        return self.__coh
    def stations(self):
        """Return a list of available stations"""
        return self.__stations
    def station_index(self):
        """Return a list of station indices (used in spigots/sinks)"""
        return self.__station_index

    # Some derived values:
    def keys(self):
        """Return a list of keys to the Cohset items"""
        return self.__coh.keys()
    def has_key(self, key):
        """Check whether there is an item with the given key"""
        return self.keys().__contains__(key)
    def len(self):
        """Return the nr of Cohset items"""
        return len(self.__coh)
    def dims(self):
        """Return the dimensions of the Cohset matrices (usually [2,2])""" 
        return self.__dims

    def nodenames(self, select='all'):
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

    def nodes(self, select='all'):
        """Return a list of the current nodes in the Cohset"""
        nn = []
        for key in self.keys():
            nn.append(self.__coh[key])
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
        s = s+' '+str(self.dims())
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
        polrep = self.polrep()+str(self.corrs())
        polrep += ' paral='+str(self.paral())
        polrep += ' cross='+str(self.cross())
        ss.append(indent1+' - polrep:          '+polrep)
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
        return TDL_common.Super.display_end(self, ss)



    #--------------------------------------------------------------
    # Methods that generate new nodes (and thus require nodescope):
    #--------------------------------------------------------------

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


    def graft(self, ns, node, name=None, key='all', stepchild=False):
        """Graft the specified node(s) onto the streams of the specified ifr(s).
        By default, this is done by means of a MeqReqSeq, which obly uses the result
        of its LAST (main-stream) child. This synchronises the ifr-streams if the
        same node (e.g. a solver or a dcoll) is grafted on all ifr-streams.
        If stepchild=True, make the node(s) step-children of a MeqSelector
        node that is inserted before the specified (key) coherency node"""
        funcname = '::graft():'
        gg = deepcopy(node)                                 # necessary....??
        if not isinstance(gg, (tuple, list)): gg = [gg]
        keys = self.keys()
        if key=='first': keys = keys[0]                     # use the first ifr only
        if key=='last': keys = keys[len(keys)-1]            # use the last ifr only
        uniqual = _counter(funcname, increment=-1)
        if stepchild:
            gname = 'graft_stepchild'
        else:
            gname = 'graft_reqseq'
        if isinstance(name, str): gname += '_'+name
        self.history(funcname+' '+gname+': len(gg)='+str(len(gg)))
        
        # NB: Consider new options: add_children(...) or add_stepchildren(...)
        #     See also PyApps/test/tdl_tutorial.py

        for key in keys:
            if stepchild:
                self[key] = ns[gname].qmerge(self[key])(uniqual) << Meq.Selector(self[key], stepchildren=gg)
            else:
                children = deepcopy(gg)                     # first the grafted node(s) (e.g. dcoll)
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


    def icorr(self, corrs='all'):
        """Get the index nrs (in self.__corr) of the specified corrs"""
        if isinstance(corrs, str) and corrs=='all': corrs = self.corrs()
        if not isinstance(corrs, (tuple,list)): corrs = [corrs]
        icorr = []
        newcorrs = []
        oldcorrs = self.corrs()
        for corr in corrs:
            if oldcorrs.__contains__(corr):
                icorr.append(oldcorrs.index(corr))
                newcorrs.append(corr)
            else:
                print '** corr not recognised:',corr
        print '** .icorr(',corrs,'):->',icorr,' (',oldcorrs,'->',newcorrs,')'
        return icorr


    def selcorr(self, ns, corrs=None):
        """Select a subset of the available corrs""" 
        funcname = '::selcorr():'
        if corrs==None: return False
        icorr = self.icorr(corrs)
        if len(icorr)==0: return False

        # Adjust the corrs info vectors:
        newcorrs = []
        for i in icorr: newcorrs.append(self.__corrs[i])
        self.__corrs = newcorrs
        self.calc_derived()
        print '** .selcorr(',corrs,copy,') ->',self.corrs(),self.paral(),self.cross()

        # Make MeqSelector nodes that select the specified corrs:
        uniqual = _counter(funcname, increment=-1)
        multi = (len(icorr)>1)       # Kludge, to tell MeqSelector that icorr is multiple... 
        for key in self.keys():
            s12 = self.__stations[key]
            coh = ns.selcorr(uniqual)(corrs)(s1=s12[0], s2=s12[1]) << Meq.Selector(self.__coh[key], index=icorr, multi=multi)
            self.__coh[key] = coh
        # Adjust the coherence shape, if necessary:  
        if len(icorr)<4: self.__dims = [len(icorr)]            #...shape...??
        self.scope('selcorr'+'_'+self.scope())
        self.history(append=funcname+' -> '+self.oneliner())
        return True


#======================================================================================

    def spigots (self, ns=0, **pp):
        """Fill the Cohset with spigot nodes for all its ifrs"""
        funcname = '::spigots():'
        # Input arguments:
        pp.setdefault('flag_bit', 4)                     # .....
        pp.setdefault('corr_index', [0,1,2,3])           # .........??
        pp.setdefault('input_column', 'DATA')            # .....
        pp = record(pp)

        corr_index = pp['corr_index']
        # For XX/YY only, use:
        # corr_index = [0,-1,-1,3]
        # Still returns a 2x2 tensor node, but with complex zeroes for -1 (?)
        # See wiki-pages...
        
        # Make a record/dict of spigots that produce 2x2 coherency matrices:
        for key in self.keys():
            s12 = self.__stations[key]
            i1 = self.station_index()[str(s12[0])]              # integer
            i2 = self.station_index()[str(s12[1])]              # integer
            self.__coh[key] = ns.spigot(s1=s12[0],s2=s12[1]) << Meq.Spigot(station_1_index=i1,
                                                                           station_2_index=i2,
                                                                           corr_index=corr_index,
                                                                           flag_bit=pp['flag_bit'],
                                                                           input_column=pp['input_column'])
            # print funcname, key,s12,i1,i2,i1+i2,self.__coh[key]

        self.__dims = [2,2]
        self.label('spigots')
        self.scope('spigots')
        self.history(append=funcname+' -> '+self.oneliner())
        return True

#------------------------------------------------------------------------------------

    def sinks (self, ns, **pp):
        """Attaches the Cohset coherency matrices to MeqSink nodes""" 
        funcname = '::sinks():'

        # Input arguments:
        pp.setdefault('output_col', 'RESIDUALS')        # name of MS output column (NONE means inhibited)
        pp.setdefault('start', None)                    # optional child of MeqVisDataMux
        pp.setdefault('pre', None)                      # optional child of MeqVisDataMux
        pp.setdefault('post', None)                     # optional child of MeqVisDataMux
        # pp = record(pp)                  # ...record(pp) drops the None fields....!
        print funcname,' pp=\n',pp,'\n'
        print 'pp[post] =',type(pp['post'])

        corr_index = self.corr_index()
        corr_index = [0,1,2,3]

        # Make separate sinks for each ifr:
        for key in self.keys():
            s12 = self.__stations[key]
            i1 = self.station_index()[str(s12[0])]              # integer
            i2 = self.station_index()[str(s12[1])]              # integer
            self.__coh[key] = ns.MeqSink(s1=s12[0], s2=s12[1]) << Meq.Sink(self.__coh[key],
                                                                           station_1_index=i1,
                                                                           station_2_index=i2,
                                                                           corr_index=corr_index,
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
                    pp[key] = ns[key+'_VisDataMux'] << Meq.ReqSeq(children=pp[key])
                    # pp[key] = ns[key+'_VisDataMux'] << Meq.Add(children=pp[key])
            root = ns.VisDataMux << Meq.VisDataMux(start=pp['start'],
                                                   pre=pp['pre'], post=pp['post'])
        

        self.scope('sinks')
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

def _counter (key, increment=0, reset=False, trace=True):
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
    from Timba.Contrib.JEN import MG_JEN_exec
    ns = NodeScope()
    nsim = ns.Subscope('_')
    
    stations = range(4)
    ifrs = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ]
    cs = Cohset(label='initial', polrep='circular', stations=stations)
    cs.display('initial')

    if 0:
        cs.zero(ns)
        cs.display('zero')

    if 0:
        print '** dir(cs) ->',dir(cs)
        print '** cs.__doc__ ->',cs.__doc__
        print '** cs.__module__ ->',cs.__module__
        print


    if 0:
        cs.spigots(ns)
        cs.display('spigots')

    if 0:
        zero = ns.zero << 0.0
        minus = ns.minus << -1
        cs.graft(ns, [zero, minus], name='test', key='all', stepchild=False)
        cs.display('graft')

    if 1:
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
        if 1:
            sink = cs.simul_sink(ns)
            MG_JEN_exec.display_subtree(sink, 'simul_sink', full=True, recurse=5)
        
    if 0:
        # Display the final result:
        k = 0 ; MG_JEN_exec.display_subtree(cs[k], 'cs['+str(k)+']', full=True, recurse=5)
        cs.display('final result')
    print '\n*******************\n** End of local test of: TDL_Cohset.py:\n'



#============================================================================================









 

