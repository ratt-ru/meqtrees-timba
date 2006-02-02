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
#    - 08 dec 2005: added method: coll()
#    - 09 dec 2005: added methods: cohs(), Condeq(), DataCollect()
#    - 13 dec 2005: repaired construction with ifrs (rather than stations)
#    - 15 dec 2005: included self.__Joneset (see .corrupt())
#    - 19 dec 2005: included .update_from_Sixpack() (place-holder)
#    - 25 dec 2005: included .redundancy() features
#    - 26 dec 2005: retired .nodes(): use .cohs() instead
#    - 28 dec 2005: introduced .select() and .delete() -> .keys()
#    - 31 dec 2005: introduced .Condeq_redun() and .merge()
#    - 31 dec 2005: removed self.__dims (cohs are ALWAYS [2,2])
#    - 31 dec 2005: generalised .coll() to .rider()
#    - 01 jan 2006: extended .graft() with chain_solvers argument
#    - 03 jan 2006: introduced .chain_solvers() function
#    - 04 jan 2006: cleanup(): collection of orphans to avoid browser clutter
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
from numarray import *
# from math import *

from Timba.Trees import TDL_common
from Timba.Trees import TDL_radio_conventions
from Timba.Trees import TDL_Joneset
from Timba.Trees import TDL_Parmset
# from Timba.Trees import TDL_Sixpack



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
            pp['stations'] = ifrs2stations(pp['ifrs'])
            self.history('input: len(ifrs)='+str(len(pp['ifrs'])))
        elif isinstance(pp['stations'], list):
            # Assume that pp.stations has been given explicitly
            pp['ifrs'] = stations2ifrs(pp['stations'])
            self.history('input: stations='+str(pp['stations']))
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
            # print key,self.__coh[key]
        # self.__dims = [1]                              # shape of coh tensor nodes
        self.select(init=True)                         # define self.__selected

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

        # Define its Parmset object
        self.Parmset = TDL_Parmset.Parmset(**pp)

        # The Cohset may remember the Joneset with which it has been corrupted:
        self.__Joneset = None
        # self.__Joneset = dict(correct_with=None, corrected_by=None,
        #                       corrupt_with=None, corrupted_by=None)

        # The Cohset may collect various bits of information along the way:
        self.__rider = {}

        # Plot information (standard, but extended from Jonesets):
        self.__plot_color = TDL_radio_conventions.plot_color()
        self.__plot_style = TDL_radio_conventions.plot_style()
        self.__plot_size = TDL_radio_conventions.plot_size()
        self.__plot_pen = TDL_radio_conventions.plot_pen()

        # Make default __station_xyz (for dxyz calculation): 
        self.station_xyz(sep9A=72)

        return None


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
        self.__corrI = []                            # list of AVAILABLE corrs for stokesI
        self.__corrQ = []                            # list of AVAILABLE corrs for stokesQ
        self.__corrU = []                            # list of AVAILABLE corrs for stokesU
        self.__corrV = []                            # list of AVAILABLE corrs for stokesV
        for corr in self.__corrs:
            if ['XX','YY','RR','LL'].__contains__(corr):
                self.__paral.append(corr)
                self.__corrI.append(corr)
            if ['XY','YX','RL','LR'].__contains__(corr):
                self.__cross.append(corr)
                self.__corrU.append(corr)
            if ['XX','YY','RL','LR'].__contains__(corr):
                self.__corrQ.append(corr)
            if ['XY','YX','RR','LL'].__contains__(corr):
                self.__corrV.append(corr)
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
    def corrI(self):
        """Return a list of AVAILABLE corrs relevant for stokesI"""
        return self.__corrI
    def corrQ(self):
        """Return a list of AVAILABLE corrs relevant for stokesQ"""
        return self.__corrQ
    def corrU(self):
        """Return a list of AVAILABLE corrs relevant for stokesU"""
        return self.__corrU
    def corrV(self):
        """Return a list of AVAILABLE corrs relevant for stokesV"""
        return self.__corrV


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
        if isinstance(key, int):
            key = self.__coh.keys()[key]
        if self.__coh.has_key(key):
            return self.__coh[key]
        keys = self.__coh.keys()
        print '** TDL_Cohset.__getitem(',key,'): not recognised in (',len(keys),'):',keys
        return False

    def __setitem__(self, key, value):
        """Replace the named (key) item with value (usually a node)"""
        self.__coh[key] = value
        return self.__coh[key]

    def plot_color(self): return self.__plot_color
    def plot_style(self): return self.__plot_style
    def plot_size(self): return self.__plot_size
    def plot_pen(self): return self.__plot_pen

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
        """Return the list of station pairs (tuples)"""
        return self.__stations
    def station_index(self):
        """Return a list of station indices (used in spigots/sinks)"""
        return self.__station_index


    def has_key(self, key, warning=None):
        """Check whether there is an item with the given key"""
        result = self.__coh.keys().__contains__(key)
        if not result and warning:
            print str(warning),': key not recognised:',key
        return result

    # def dims(self):
    #    """Return the dimensions of the Cohset matrices (usually [2,2])""" 
    #    return self.__dims

    def len(self):
        """Return the nr of Cohset items"""
        return len(self.__coh)
    def ndeleted(self):
        """Return the nr of deleted Cohset items"""
        return len(self.keys(deleted=True))
    def nselected(self):
        """Return the nr of selected Cohset items"""
        return len(self.keys(selected=True))
    def ndeselected(self):
        """Return the nr of deselected Cohset items (excluding deleted ones)"""
        return len(self.keys(selected=False))

    def nodenames(self, selected=True, deleted=False, trace=False):
        """Return a list of the names of the current nodes in the Cohset"""
        keys = self.keys(selected=selected, deleted=deleted, trace=trace)
        nn = []
        for key in keys:
            if self.__coh[key]==None:
                nn.append(str(self.__coh[key]))
            elif isinstance(self.__coh[key], str):
                nn.append(self.__coh[key])
            else:
                nn.append(self.__coh[key].name)
        if len(nn)==0: return '<empty>'
        return nn

    def oneliner(self):
        """Return a one-line summary of the Cohset"""
        s = TDL_common.Super.oneliner(self)
        s = s+' '+str(self.scope())
        s = s+' '+str(self.punit())
        s = s+' '+str(self.corrs())
        ndel = self.ndeleted()
        nsel = self.nselected()
        ndesel = self.ndeselected()
        ntot = ndel + nsel + ndesel
        s = s+' ['+str(self.len())+'='+str(ntot)+'='+str(nsel)+'+'+str(ndesel)+'+'+str(ndel)+']'
        s = s+' ('+str(self.nodenames()[0])+',...)'
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
        ss.append(indent1+' - parmgroups:      '+str(self.Parmset.parmgroup().keys()))
        ss.append(indent1+' - solvegroups:     '+str(self.Parmset.solvegroup().keys()))

        #.................................................................................
        ss.append(indent1+' - Available 2x2 cohaerency matrices ( '+str(self.len())+' ):')
        if full or self.len()<10:
            for key in self.__coh.keys():
                s12 = self.__stations[key]
                coh = key+str(s12)+' : '+str(self.__coh[key])
                coh += '  sel='+str(self.__selected[key])
                if len(self.redun()[key])>0:
                    coh += '  rxyz='+str(self.rxyz()[key])+'m'
                    coh += '  redun='+str(self.redun()[key])
                ss.append(indent2+' - '+coh)
        else:
            keys = self.__coh.keys()
            n = len(keys)-1
            ss.append(indent2+' - first: '+keys[0]+' : '+str(self.__coh[keys[0]]))
            ss.append(indent2+'   ....')
            ss.append(indent2+' - last:  '+keys[n]+' : '+str(self.__coh[keys[n]]))
        deleted = self.keys(deleted=True)
        ss.append(indent1+' - Deleted:( '+str(len(deleted))+' ): '+str(deleted))
        selected = self.keys(selected=True)
        ss.append(indent1+' - Selected:( '+str(len(selected))+' ): '+str(selected))
        deselected = self.keys(selected=False)
        ss.append(indent1+' - Deselected:( '+str(len(deselected))+' ): '+str(deselected))
        #.................................................................................

        if full:
            ss.append(indent1+' - station_xyz:     '+str(self.station_xyz().keys()))
            for key in self.__station_xyz.keys():
                ss.append(indent2+' - '+key+' : '+str(self.__station_xyz[key]))

        ss.append(indent1+' - Redundant (rxyz) baselines:')
        for key in self.rxyz_redun().keys():
            n = len(self.__rxyz_redun[key])
            ss.append(indent2+' - '+key+'m ('+str(n)+'): '+str(self.__rxyz_redun[key]))

        if self.Joneset():
            ss.append(indent1+' - Joneset (applied by .corrupt():')
            ss.append(indent2+' - '+str(self.__Joneset.oneliner()))

        ss.append(indent1+' - rider (things collected along the way):')
        for key in self.__rider.keys():
            n = len(self.__rider[key])
            ss.append(indent2+' - '+key+'('+str(n)+'):'+str(self.__rider[key]))       

        return TDL_common.Super.display_end(self, ss)


    def Joneset(self, clear=False):
        """Return the Joneset (if any) with which this Cohset has been corrupted"""
        if clear: self.__Joneset = None
        return self.__Joneset


    def rider(self, key=None, append=None, clear=False, report=False):
        """Interaction with rider info (lists) of various types (key)"""
        if not isinstance(key, str):                  # no key specified
            if clear: self.__rider = {}               # clear the entire rider dict
            return self.__rider                       # return the entire rider dict

        # A append item has been specified:
        if append:                                    # append item(s) to the specified rider
            if clear:
                self.__rider[key] = []                # clear the rider BEFORE appending item(s)
                clear = False                         # do not clear afterwards, of course
            self.__rider.setdefault(key,[])           # create the rider (key) if necessary
            if isinstance(append, (tuple, list)):     # assume list of items
                self.__rider[key].extend(append)
            else:                                     # assume single item
                self.__rider[key].append(append)

        # Prepare the return value:
        if self.__rider.has_key(key):
            cc = self.__rider[key]                    # copy the existing rider BEFORE clearing
            if clear: self.__rider[key] = []          # clear the rider, if required
            return cc                                 # Return a list (as it was before clearing)

        # Not found, but always return a list:
        if report: print '\n** Cohset.rider(',key,'): not recognised in:',self.__rider.keys()
        return []

    #----------------------------------------------------------------
    # Methods that deal with selecting/deleting subsets of coh items:
    #----------------------------------------------------------------

    def select (self, **pp):
        """Select/deselect a subset of coh items. Used by .keys() and .delete()"""
        funcname = '::select():'
        pp.setdefault('key', '*')          # affected key(s)
        pp.setdefault('s1', '*')           # station 1 selection
        pp.setdefault('s2', '*')           # station 2 selection
        pp.setdefault('rmin', None)        # min baseline length (rxyz) to be selected    
        pp.setdefault('rmax', None)        # max baseline length (rxyz) to be selected
        pp.setdefault('select', True)      # if False, deselect rather than select
        pp.setdefault('save', False)       # if True, save the current selection first
        pp.setdefault('restore', False)    # if True, restore the saved selection first
        pp.setdefault('init', False)       # if True, initialise
        pp.setdefault('trace', False)      # if True, print messages

        trace = False
        if trace: print '\n**',funcname,pp

        # Initial call (from self.__init__())
        if pp['init']:
            self.__selected = {}                   # create
            self.__saved_selection = {}            # create
            for key in self.__coh.keys():
                self.__selected[key] = pp['select']
            return True

        # Interact with saved_selection first (if required)
        if pp['restore']:
            self.__selected = self.__saved_selection
        if pp['save']:
            self.__saved_selection = self.__selected

        # Make a list (keys) of affected coh item keys:
        cohkeys = self.__coh.keys()
        affected = []
        if len(cohkeys)==0:                        # none available
            pass
        elif not pp['key']:                        # none selected
            pass
        elif isinstance(pp['key'], str):           # string
            if pp['key']=='*':
                affected = cohkeys                 # all available keys
            elif pp['key']=='first':
                affected = cohkeys[0]              # first key
            else:                                  # Assume specific key name
                affected = [pp['key']]             # a list with one element
        elif isinstance(pp['key'], (list, tuple)): # list
            affected = pp['key']                   # existence checked below
        else:                                      # neither string nor list...?
            pass                                   # error?
        # if trace: print 'affected =',len(affected),':',affected
        if len(affected)==0:
            return False                           # do nothing....?

        # Make a list (keys) of existing coh items to be processed:
        keys = []
        for key in affected:
            if trace: s0 = '- '+key+': '
            if not key in cohkeys:                 # key does not exist
                print s0,'does not exist in:',cohkeys
                pass                               # error...?
            else:
                if not self.__coh[key]:              # item has been deleted
                    if trace: print s0,'was deleted:',self.__coh[key]
                    pass                               # 
                elif isinstance(self.__coh[key], str):          
                    if trace: print s0,'not a node:',self.__coh[key]
                    pass
                else:
                    keys.append(key)                   # OK, include in keys
        if trace: print 'keys = ',len(keys),':',keys

        # Do the actual (de-)selection:
        for key in keys:
            if trace: s0 = '- '+key+' ('+str(around(self.__rxyz[key]))+'): '
            was = self.__selected[key]
            if pp['rmin'] and self.__rxyz[key]<pp['rmin']:      
                if trace: print '  baseline =',self.__rxyz[key],'<',pp['rmin']
                self.__selected[key] = not pp['select']    
            elif pp['rmax'] and self.__rxyz[key]>pp['rmax']:   
                if trace: print '  baseline =',self.__rxyz[key],'>',pp['rmax']
                self.__selected[key] = not pp['select']    
            else:
                self.__selected[key] = pp['select'] 
            if trace: print s0,was,'->',self.__selected[key],':',self.__coh[key]

        # Some bookkeeping and cleaning up:
        for key in self.__coh.keys():
            if not self.__coh[key]:
                # Make sure that the deleted items are not selected (overkill?):
                self.__selected[key] = False
            elif isinstance(self.__coh[key], str):
                pass
                # Should not happen, really....
                # self.__selected[key] = False         
            elif not self.__selected[key]:
                # Assume that a de-selected item will eventually be an orphan node.
                # NB: Attaching it to an orphan root node is safe, even if the node
                #     is eventually used after all (see .sinks())
                self.rider('selection_orphans', append=self.__coh[key])

        # Finished:
        self.history(append=funcname+' inarg = '+str(pp))
        self.history(append=funcname+' -> '+str(pp['select'])+': '+str(len(keys))+': '+str(keys))
        if trace: self.keys(trace=True)
        return True

    #............................................................................

    def keys (self, selected=True, deleted=False, trace=False):
        """Return a list of keys for the (de-)selected coh items.
        If deleted==True, include any deleted items""" 
        funcname = '::keys():'
        if trace: print '\n** .keys(',selected,deleted,'):'
        if not isinstance(selected, bool):
            print '\n**',funcname,': selected should be bool, not',type(selected),selected
            return False
        kk = []
        for key in self.__coh.keys():                   # all keys
            if deleted:                                 # Look for deleted items only
                if self.__coh[key]==None:
                    kk.append(key)                      # include
            elif self.__coh[key]:                       # valid item (i.e. not deleted) 
                if self.__selected[key]==selected:      # (de-)seleced as specified
                    kk.append(key)                      # include
            if trace: print '--',key,self.__coh[key],(self.__coh[key]==None),': kk =',kk
        if trace: print '** .keys(',selected,deleted,') ->',len(kk),':',kk
        return kk


    def delete (self, selected=True, trace=False):
        """Delete (set to None) the (de-)selected coh items"""
        funcname = '::delete():'
        if trace: print '\n**',funcname,'(',selected,'):'
        kk = []
        for key in self.keys(selected=selected, trace=False):
            if trace: print '-',funcname,key,':',self.__coh[key],'-> None'
            if self.__coh[key]:
                self.rider('deletion_orphans', append=self.__coh[key])
                self.__coh[key] = None
            kk.append(key)
        self.history(append=funcname+' ('+str(len(kk))+'): '+str(kk))
        if trace: print '**',funcname,'\n'
        return True
    

    #--------------------------------------------------------------
    # Methods that generate new nodes (and thus require nodescope):
    #--------------------------------------------------------------

    def coh (self, key=None, corrs='*', ns=None, name=None, uniqual=None):
        """Get a named (key) cohearency node (tensor), optionally for selected corrs""" 
        funcname = '::coh():'

        # Check the specified key(s) (name):
        if not self.has_key(key, warning=funcname): return False

        # The cohaerency may be deleted (None):
        if self.__coh[key]==None: return None

        # Check the specified corr selection:
        if isinstance(corrs, str):
            if corrs=='*': return self.__coh[key]    # no selection needed
        icorr = self.corr_index(corrs)
        if len(icorr)==4: return self.__coh[key]     # no selection needed
        if len(icorr)==0: return False               # none specified/available (error)

        # Make MeqSelector nodes that select the specified corrs:
        multi = (len(icorr)>1)                       # Kludge, to tell MeqSelector that icorr is multiple... 
        if not uniqual: uniqual = _counter(funcname, increment=-1)
        s12 = self.__stations[key]
        if not isinstance(name, str):
            name = 'selcorr_'+self.scope()             
        coh = ns[name](uniqual)(corrs)(s1=s12[0], s2=s12[1]) << Meq.Selector(self.__coh[key],
                                                                             index=icorr, multi=multi)
        return coh                                   # return the node


    def cohs (self, selected=True, corrs='*', ns=None, name=None, trace=False):
        """Get a vector/list of (de-)selected cohearency nodes.
        Optionally, make MeqSelector nodes for a subset of correlations""" 
        funcname = '::cohs():'

        # Make a unique qualifier (and pass it to self.coh())
        uniqual = _counter(funcname, increment=-1)

        # Make the vector/list (cohs) of coh nodes:
        cohs = []
        for key in self.keys(selected=selected):
            coh = self.coh(key, corrs=corrs, ns=ns, uniqual=uniqual, name=name)
            cohs.append(coh)
            if trace: print s1,len(cohs),': coh =',coh
        return cohs

    #------------------------------------------------------------------------------------

    def zero(self, ns):
        """Make zero coherency matrices for all ifrs"""
        funcname = '::zero():'
        c0 = complex(0)
        zz = array([c0,c0,c0,c0])
        for key in self.keys():
            s12 = self.__stations[key]
            self.__coh[key] = ns.cxzero22(s1=s12[0], s2=s12[1]) << Meq.Constant(zz, dims=[2,2])
        # self.__dims = [2,2]
        self.history(append=funcname+' -> '+self.oneliner())

    def unity(self, ns):
        """Make unit coherency matrices for all ifrs"""
        funcname = '::unity():'
        c0 = complex(0.0)
        c1 = complex(1.0)
        zz = array([c1,c0,c0,c1])
        coh22 = ns.cxunity22 << Meq.Constant(zz, dims=[2,2])
        for key in self.keys():
            s12 = self.__stations[key]
            # self.__coh[key] = ns.cxunity22(s1=s12[0], s2=s12[1]) << Meq.Constant(zz, dims=[2,2])
            self.__coh[key] = coh22
        # self.__dims = [2,2]
        self.history(append=funcname+' -> '+self.oneliner())

    def uniform(self, ns, coh22):
        """Uniform coherency matrices (coh22) for all ifrs(qual)"""
        funcname = '::uniform():'
        uniqual = _counter(funcname, increment=-1)
        for key in self.keys():
            s12 = self.__stations[key]
            # self.__coh[key] = ns.uniform(uniqual)(s1=s12[0], s2=s12[1]) << Meq.Selector(coh22)
            self.__coh[key] = coh22
        # self.__dims = [2,2]
        self.history(append=funcname+' -> '+self.oneliner())


    def chain_solvers(self, ns, node, name=None):
        """Chain the solver subtrees (node), parallel to the main data-stream"""
        funcname = '::chain_solvers():'
        # First check for a previous solver subtree:
        previous = self.rider('chain_solvers', clear=True)
        if len(previous)>0:
            if not name: name = 'reqseq_chain_solvers'
            uniqual = _counter('chain_solvers', increment=-1)
            node = ns[name](uniqual) << Meq.ReqSeq(children=[previous[0], node])
        # Keep the solver subtree for future chaining:
        self.rider('chain_solvers', append=node)
        self.history(append=funcname+': '+str(node))
        return True


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
        
        # OK, graft onto all ifr-branches (has synchronising effect!):
        for key in self.keys():
            if stepchild:
                self[key] = ns[gname].qmerge(self[key])(uniqual) << Meq.Selector(self[key], stepchildren=gg)
            else:
                children = []
                # NB: deepcopy is NECESSARY (for some reason I do not understand....)
                children.extend(deepcopy(gg))               # 
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
        self.__Joneset = Joneset                     
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
        self.__Joneset = Joneset                     
        self.history(append='corrupted by: '+Joneset.oneliner())
        self.history(append=funcname+' -> '+self.oneliner())
        return True

    def update_from_Sixpack(self, Sixpack=None):
        """Update the internal info from a Sixpack object
        (NB: Not yet implemented in Sixpack....)"""
        if Sixpack==None: return False
        if not Sixpack.Parmset.unsolvable():
            # self.__plot_color.update(Sixpack.plot_color())
            # self.__plot_style.update(Sixpack.plot_style())
            # self.__plot_size.update(Sixpack.plot_size())
            self.update_from_Parmset(Sixpack.Parmset)
            self.history(append='updated from (not unsolvable): '+Sixpack.oneliner())
        else:
            # A Sixpack that is 'unsolvable' has no solvegroups.
            # However, its parmgroups might interfere with parmgroups
            # of the same name (e.g. Gphase) from 'not unsolvable' Sixpacks.
            # Therefore, its parm info should not be copied here.
            self.history(append='not updated from (unsolvable): '+Sixpack.oneliner())
        return True

    def update_from_Joneset(self, Joneset=None):
        """Update the internal info from a (corrupting) Joneset object"""
        # (see Joneseq.Joneset())
        if Joneset==None: return False
        if not Joneset.Parmset.unsolvable():
            self.__plot_color.update(Joneset.plot_color())
            self.__plot_style.update(Joneset.plot_style())
            self.__plot_size.update(Joneset.plot_size())
            self.update_from_Parmset(Joneset.Parmset)
            self.history(append='updated from (not unsolvable): '+Joneset.oneliner())
        else:
            # A Joneset that is 'unsolvable' has no solvegroups.
            # However, its parmgroups might interfere with parmgroups
            # of the same name (e.g. Gphase) from 'not unsolvable' Jonesets.
            # Therefore, its parm info should not be copied here.
            self.history(append='not updated from (unsolvable): '+Joneset.oneliner())
        return True

    def update_from_Cohset(self, Cohset=None):
        """Update the internal info from another Cohset object"""
        if Cohset==None: return False
        self.__plot_color.update(Cohset.plot_color())
        self.__plot_style.update(Cohset.plot_style())
        self.__plot_size.update(Cohset.plot_size())
        self.update_from_Parmset(Cohset.Parmset)
        self.history(append='updated from: '+Cohset.oneliner())
        return True

    def update_from_Parmset(self, Parmset=None):
        """Update the internal info from a given Parmset"""
        if Parmset:
            self.Parmset.update(Parmset)
            self.history(append='updated from: '+Parmset.oneliner())
        self.__plot_color.update(self.Parmset.plot_color())
        self.__plot_style.update(self.Parmset.plot_style())
        self.__plot_size.update(self.Parmset.plot_size())
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


    def merge (self, ns, Cohset=None, **pp):
        """Replace any deleted coherencies with the corresponding ones from
        the given Cohset, provided that these are selected"""
        funcname = '::merge():'
        for key in self.__coh.keys():
            if not self.__cok[key]:            # if deleted
                self.__coh[key] = Cohset[key]  # use the one from Cohset
        # The input Cohset may contain parmgroup/solvegroup info:
        self.update_from_Joneset(Cohset.Joneset())
        self.scope('merged')
        self.history(append=funcname+' -> '+self.oneliner())
        return True


    def Condeq (self, ns, Cohset=None, **pp):
        """Make (2x2) MeqCondeq nodes, using Cohset as the other input"""
        funcname = '::Condeq():'
        uniqual = _counter(funcname, increment=-1)
        punit = self.punit()
        scope = 'Condeq'

        # Make condeq nodes for the selected keys:
        coh = dict()                       # use temporary dict for new nodes
        for key in self.keys():
            s12 = self.__stations[key]
            basel = str(around(self.__rxyz[key]))+'m'
            coh[key] = ns[scope+'_'+basel](uniqual)(s1=s12[0], s2=s12[1], q=punit) << Meq.Condeq(
                self.__coh[key], Cohset[key])
            print '-',key,':',coh[key]

        # Copy the new condeq nodes to self.__coh, deleting the rest:
        for key in self.__coh.keys():
            if coh.has_key(key):
                self.__coh[key] = coh[key]
            elif self.__coh[key]:          # existing node
                self.rider('deletion_orphans', append=self.__coh[key])
                self.__coh[key] = None     # delete

        # The input Cohset may contain parmgroup/solvegroup info:
        self.update_from_Joneset(Cohset.Joneset())
        self.update_from_Parmset(Cohset.Parmset)
        self.scope(scope)
        self.history(append=funcname+' -> '+self.oneliner())
        return True


    def Condeq_redun (self, ns=None):
        """Make (2x2) MeqCondeq nodes, using Cohset as the other input.
        If no other Cohset given, make MeqCondeqs for redundant spacings"""
        funcname = '::Condeq_redun():'
        uniqual = _counter(funcname, increment=-1)
        punit = self.punit()
        scope = 'Condeq_redun'
        coh = dict()                       # use temporary dict for new nodes
        for key in self.keys():
            s12 = self.__stations[key]
            basel = str(around(self.__rxyz[key]))+'m'
            print '-',key,basel,s12
            print '---',self.__redun[key]
            coh[key] = None
            redun = self.__redun[key]      # list of zero or more keys of redundant ifrs
            if len(redun)>0:
                # Assume that the first ifr in the list is the most suitable
                # (preferably, redundant ifrs should share a station, see .redn() below)
                key2 = redun[0]            # key of the other ifr
                ss = self.__stations[key2]
                coh[key] = ns[scope+'_'+basel](uniqual)(s1=s12[0], s2=s12[1], q=punit) << Meq.Condeq(
                    self.__coh[key], self.__coh[key2])

        # Copy the new condeq nodes to self.__coh, deleting the rest:
        for key in self.__coh.keys():
            if coh.has_key(key):
                self.__coh[key] = coh[key]
            elif self.__coh[key]:          # existing node
                self.rider('deletion_orphans', append=self.__coh[key])
                self.__coh[key] = None     # delete

        self.scope(scope)
        self.history(append=funcname+' -> '+self.oneliner())
        return True



    def Condeq_redun_old (self, ns, **pp):
        """Make (2x2) MeqCondeq nodes, using Cohset as the other input.
        If no other Cohset given, make MeqCondeqs for redundant spacings"""
        funcname = '::Condeq_redun_old():'
        pp.setdefault('minimum',False)      # If True, use the minimum nr of ifrs (Does not work!!)
        uniqual = _counter(funcname, increment=-1)
        punit = self.punit()
        coh = dict()                       # use temporary dict for new nodes
        stocc = dict()                     # nr of occurences per station
        for key in self.keys():
            s12 = self.__stations[key]
            stocc.setdefault(s12[0], 0)
            stocc.setdefault(s12[1], 0)
            basel = str(around(self.__rxyz[key]))+'m'
            coh[key] = None
            if Cohset:                     # Use the supplied Cohset 
                scope = 'Condeq'
                stocc[s12[0]] += 1
                stocc[s12[1]] += 1
                add_new = (stocc[s12[0]]==1 or stocc[s12[1]]==1)
                if (not pp['minimum']) or add_new: 
                    coh[key] = ns[scope+'_'+basel](uniqual)(s1=s12[0], s2=s12[1], q=punit) << Meq.Condeq(
                        self.__coh[key], Cohset[key])
            elif len(self.__redun[key])>0: # Redundant spacing(s) available
                scope = 'Condeq_redun'
                stocc[s12[0]] += 1
                stocc[s12[1]] += 1
                # Assume that the first ifr in the list is the most suitable
                # (preferably, redundant ifrs should share a station, see .redn() below)
                key2 = self.__redun[key][0] # key of the other ifr
                ss = self.__stations[key2]
                stocc[ss[0]] += 1
                stocc[ss[1]] += 1
                add_new = (stocc[s12[0]]==1 or stocc[s12[1]]==1 or stocc[ss[0]]==1 or stocc[ss[1]]==1)
                if (not pp['minimum']) or add_new: 
                    coh[key] = ns[scope+'_'+basel](uniqual)(s1=s12[0], s2=s12[1], q=punit) << Meq.Condeq(
                        self.__coh[key], self.__coh[key2])

        print '\n** stocc =',stocc,'\n'

        # Copy the new nodes from the temporary dict (coh):
        for key in coh:
            self.__coh[key] = coh[key]

        # The input Cohset may contain parmgroup/solvegroup info:
        if Cohset:
            self.update_from_Joneset(Cohset.Joneset())

        self.scope(scope)
        self.history(append=funcname+' -> '+self.oneliner())
        return True


#======================================================================================
# Functions related to redundant-spacing calibration:
#======================================================================================

    def station_xyz(self, sep9A=None):
        """Station positions (x,y,z), used for dxyz baseline calculation"""
        if sep9A:
            # If separation RT9-RTA is specified, assume WSRT:
            xpos = range(15)
            ypos = range(15)
            zpos = range(15)
            for i in range(len(xpos)):
                xpos[i] = 0.0
                ypos[i] = i*144.0
                zpos[i] = 0.0
            ypos[10] = ypos[9] + sep9A                 # RTA: RT9+sep9A
            ypos[11] = ypos[10] + 72                   # RTB: RTA+72m
            ypos[12] = ypos[9] + (ypos[10]-ypos[0])    # RTC: OA=9C
            ypos[13] = ypos[12] + 72                   # RTD: RTC+72m
            ypos[14] = -1                              # WHAT
            # Fill the dict:
            self.__station_xyz = {}
            for key in self.__station_index.keys():
                i = self.__station_index[key]
                self.__station_xyz[key] = array([xpos[i],ypos[i],zpos[i]])
            # Update the baseline lengths in self.__dxyz:
            self.calc_baselines_xyz()
        return self.__station_xyz

#-------------------------------------------------------------------------------------

    def calc_baselines_xyz(self):
        """Calculate baseline-lengths (m) in xyz-space"""
        self.__dxyz = {}
        self.__rxyz = {}
        for key in self.__coh.keys():
            s12 = self.__stations[key]
            # Make the vector (array) dx,dy,dz:
            self.__dxyz[key] = self.__station_xyz[s12[1]] - self.__station_xyz[s12[0]]
            # Make the (scalar) distance between stations in xyz-space:
            r2 = self.__dxyz[key][0]*self.__dxyz[key][0]
            r2 += self.__dxyz[key][1]*self.__dxyz[key][1]
            r2 += self.__dxyz[key][2]*self.__dxyz[key][2]
            self.__rxyz[key] = sqrt(r2)
        self.find_strong_redundancy()
        return True

#-------------------------------------------------------------------------------------

    def dxyz(self): return self.__dxyz
    def rxyz(self): return self.__rxyz
    def rxyz_redun(self): return self.__rxyz_redun
    def redun(self): return self.__redun

#-------------------------------------------------------------------------------------

    def find_strong_redundancy(self, margin=0.001):
        """For each ifr, find the baselines that are 'exactly' the same"""
        self.__redun = {}                              # per ifr
        self.__rxyz_redun = {}                         # per length (rxyz)
        for key in self.__coh.keys():
            self.__redun[key] = []
            rxyz = self.__rxyz[key]                    # baseline length (m) in xyz-space
            s12 = self.__stations[key]                 # participating stations
            i1 = self.__station_index[s12[0]]          # integer 
            i2 = self.__station_index[s12[1]]          # integer 
            for key2 in self.__coh.keys():
                if key2==key:
                    pass                               # exclude itself
                elif abs(self.__rxyz[key2]-rxyz)>margin:
                    pass                               # too different
                elif abs(self.__dxyz[key2][0]-self.__dxyz[key][0])>margin:
                    pass                               # dx too large
                elif abs(self.__dxyz[key2][1]-self.__dxyz[key][1])>margin:
                    pass                               # dy too large
                elif abs(self.__dxyz[key2][2]-self.__dxyz[key][2])>margin:
                    pass                               # dz too large
                else:                                  # OK, strongly redundant

                    # Collect all ifrs per baseline length (rxyz):
                    rkey = str(around(rxyz))
                    self.__rxyz_redun.setdefault(rkey,[])
                    if not key in self.__rxyz_redun[rkey]:
                        self.__rxyz_redun[rkey].append(key)
                    if not key2 in self.__rxyz_redun[rkey]:
                        self.__rxyz_redun[rkey].append(key2)

                    # Collect redundant ifrs per ifr: 
                    ss = self.__stations[key2]         # participating stations
                    if ss[0]==s12[1]:                  # (key,key2) share a station
                        # Make this the first (preferred) one in the list
                        new = [key2]
                        new.extend(self.__redun[key])
                        self.__redun[key] = new
                    elif self.__station_index[ss[0]]<i1: # one direction only
                        pass
                    else:
                        self.__redun[key].append(key2)
                    
        return True


#======================================================================================
# Interface with MS (spigots, sinks):
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
        # self.__dims = [2,2]                                     # 
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
                    print '-',key,':',type(pp[key]),len(pp[key])
                    for node in pp[key]:
                        print '  -',node
                    if len(pp[key])==0:
                        pp[key] = None          # empty list gives an error....!
                    else:
                        # pp[key] = ns[key+'_VisDataMux'] << Meq.ReqSeq(children=pp[key])
                        pp[key] = ns[key+'_VisDataMux'] << Meq.ReqMux(children=pp[key]) 
                        # pp[key] = ns[key+'_VisDataMux'] << Meq.Add(children=pp[key])
                    print '-',key,':',pp[key]
                print '-',key,':',pp[key]
            root = ns.VisDataMux << Meq.VisDataMux(start=pp['start'],
                                                   pre=pp['pre'],
                                                   post=pp['post'])

        
        # Bookkeeping:
        self.cleanup(ns)
        self.scope('sink')
        self.history(append=funcname+' inarg = '+str(pp))
        self.history(append=funcname+' MS_corr_index = '+str(MS_corr_index))
        self.history(append=funcname+' -> '+self.oneliner())
        return True


    def cleanup(self, ns=None):
        """Clean up the current Cohset"""
        # Bundle the collected orphans (minimise browser clutter)
        for key in ['deletion_orphans','selection_orphans']:
            orphans = self.rider(key, clear=False, report=True)
            print '\n** .cleanup():',key,'-> orphans(',len(orphans),'):',orphans
            if len(orphans)>0:
                uniqual = _counter(key, increment=-1)
                root_node = ns[key](uniqual) << Meq.Composer(children=orphans)
                print '   ->',root_node
        return True

#------------------------------------------------------------------------------------

    def simul_sink (self, ns=None):
        """makes a common root node for all entries in Cohset""" 
        cc = []
        for key in self.keys():
            cc.append(self.__coh[key])
        node = ns.simul_sink << Meq.Add(children=cc)
        self.cleanup(ns)
        return node




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
    if trace: print '** TDL_Cohset: _counters(',key,') =',_counters[key]
    return _counters[key]






#========================================================================
# Test routine:
#========================================================================

if __name__ == '__main__':
    print '\n*******************\n** Local test of: TDL_Cohset.py:\n'
    from numarray import *
    # from Timba.Contrib.JEN import MG_JEN_Cohset
    from Timba.Trees import TDL_display
    # from Timba.Trees import JEN_record
    ns = NodeScope()
    nsim = ns.Subscope('_')
    
    stations = range(6)
    ifrs = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ]
    polrep = 'linear'
    # polrep = 'circular'
    # cs = Cohset(label='initial', polrep=polrep, stations=stations)
    cs = Cohset(label='initial', polrep=polrep, ifrs=ifrs)
    cs.display('initial')

    if 1:
        cs.zero(ns)
        # cs.display('zero', full=True)

    if 0:
        print '** dir(cs) ->',dir(cs)
        print '** cs.__doc__ ->',cs.__doc__
        print '** cs.__module__ ->',cs.__module__
        print

    if 0:
        # cs.select(trace=True)
        cs.select(rmin=150, trace=True)
        cs.delete(selected=False, trace=True)
        cs.select(select=False, rmin=150, rmax=400, trace=True)
        # cs.keys(selected=False, trace=True)
        # cs.select(select='False', trace=True)
        cs.display('select', full=True)

    if 0:
        deleted = cs.keys(deleted=True, trace=True)
        print ' - Deleted:( '+str(len(deleted))+' ): '+str(deleted)
        selected = cs.keys(selected=True, trace=True)
        print ' - Selected:( '+str(len(selected))+' ): '+str(selected)
        deselected = cs.keys(selected=False, trace=True)
        print ' - Deselected:( '+str(len(deselected))+' ): '+str(deselected)

    if 0:
        MS_corr_index = [0,1,2,3]         # all 4 available (default)
        # MS_corr_index = [-1,1,2,-1]       # all 4 available, but only XY/XY wanted
        # MS_corr_index = [0,-1,-1,1]       # only XX/YY available
        # MS_corr_index = [0,-1,-1,3]       # all 4 available, but only XX/YY wanted
        cs.spigots(ns, MS_corr_index=MS_corr_index)
        cs.display('spigots')


    if 1:
        coll = cs.rider('dcoll', ns << Meq.DataCollect())
        coll = cs.rider('hcoll', ns << Meq.HistoryCollect())
        coll = cs.rider('hcoll', ns << Meq.HistoryCollect())
        # cs.rider(clear=True)
        cs.display('rider')

    if 0:
        cs.ReSampler(ns)

    if 0:
        cs1 = Cohset(label='measured', polrep=polrep, stations=stations)
        cs1.zero(ns)
        cs.Condeq(ns, cs1)

    if 0:
        cs.Condeq(ns)
        cs.display('Condeq_redun', full=True)

    if 0:
        corrs = '*'
        # corrs = 'XX'
        # corrs = 'YX'
        # corrs = ['XX','YY']
        name = None
        name = 'NAME'
        cc = cs.cohs (corrs=corrs, ns=ns, name=name, trace=True)

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
        
        
    if 0:
        # Display the final result:
        k = 0 ; TDL_display.subtree(cs[k], 'cs['+str(k)+']', full=True, recurse=5)
        cs.display('final result')
    print '\n*******************\n** End of local test of: TDL_Cohset.py:\n'



#============================================================================================









 

