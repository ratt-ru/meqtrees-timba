# TDL_Cohset.py
#
# Author: J.E.Noordam
#
# Short description:
#    A Cohset object encapsulates a set of 2x2 cohaerency matrices for a set of ifrs.
#
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
#    - 11 feb 2006: add unop argument to .Condeq() and .Condeq_redun()
#    - 11 feb 2006: added .fullDomainMux()
#    - 25 feb 2006: added .replace() and debugged .add() 
#    - 25 feb 2006: added .addNoise() 
#    - 25 feb 2006: added .Leafset
#    - 08 mar 2006: switched to ._rider()
#    - 09 mar 2006: included new TDL_ParmSet
#    - 11 mar 2006: remove TDL_Parmset and TDL_Leafset
#    - 11 mar 2006: implement .splice()
#    - 05 apr 2006: implement .punit2coh()
#    - 07 apr 2006: re-implemented .replace() and .add()
#    - 10 apr 2006: implement .bookmark()
#    - 14 apr 2006: implemented .addNoise()
#    - 26 apr 2006: make LeafSet part of ParmSet object
#    - 28 apr 2006: called updict from update routines
#    - 28 apr 2006: implemented .TDLRuntimeOption()
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

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *
from copy import deepcopy
from numarray import *
# from math import *
from random import *

from Timba.Trees import TDL_common
from Timba.Trees import TDL_radio_conventions
from Timba.Trees import TDL_Joneset
from Timba.Trees import TDL_ParmSet
# from Timba.Trees import TDL_Sixpack

from Timba.Trees import JEN_bookmarks
# JEN_bookmarks.create (node, page=page_name, folder=folder_name)



#**************************************************************************************
# Some useful helper functions:
#**************************************************************************************

def stations2ifrs(stations=range(3)):
    """Make a list of ifrs (station-pair tuples) from the given stations"""
    ifrs  = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ]
    # The following is temporary, to deal with a CS10-related bug...
    # ifrs.append((1,0))
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
            self._history('input: len(ifrs)='+str(len(pp['ifrs'])))
        elif isinstance(pp['stations'], list):
            # Assume that pp.stations has been given explicitly
            pp['ifrs'] = stations2ifrs(pp['stations'])
            self._history('input: stations='+str(pp['stations']))
        else:
            self._history(error=hist+'neither stations/ifrs specified')
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

        # Define its ParmSet and LeafSet objects:
        self.ParmSet = TDL_ParmSet.ParmSet(**pp)

        # The Cohset may remember the Joneset with which it has been corrupted:
        self.__Joneset = None
        # self.__Joneset = dict(correct_with=None, corrected_by=None,
        #                       corrupt_with=None, corrupted_by=None)

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
        self.__paral11 = []                          # list of AVAILABLE 'parallel' corrs with pol 1
        self.__paral22 = []                          # list of AVAILABLE 'parallel' corrs with pol 2
        self.__cross = []                            # list of AVAILABLE cross-corrs
        self.__cross12 = []                          # list of AVAILABLE cross-corrs 12
        self.__cross21 = []                          # list of AVAILABLE cross-corrs 21
        self.__corrI = []                            # list of AVAILABLE corrs for stokesI
        self.__corrQ = []                            # list of AVAILABLE corrs for stokesQ
        self.__corrU = []                            # list of AVAILABLE corrs for stokesU
        self.__corrV = []                            # list of AVAILABLE corrs for stokesV
        for corr in self.__corrs:
            if ['XX','YY','RR','LL'].__contains__(corr):
                self.__paral.append(corr)
                self.__corrI.append(corr)
            if ['XX','RR'].__contains__(corr):
                self.__paral11.append(corr)
            if ['YY','LL'].__contains__(corr):
                self.__paral22.append(corr)
            if ['XY','YX','RL','LR'].__contains__(corr):
                self.__cross.append(corr)
                self.__corrU.append(corr)
            if ['XX','YY','RL','LR'].__contains__(corr):
                self.__corrQ.append(corr)
            if ['XY','YX','RR','LL'].__contains__(corr):
                self.__corrV.append(corr)
            if ['XY','RL'].__contains__(corr):
                self.__cross12.append(corr)
            if ['YX','LR'].__contains__(corr):
                self.__cross21.append(corr)
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
    def cross12(self):
        """Return a list of AVAILABLE cross-correlation names 12 (XY, RL)"""
        return self.__cross12
    def cross21(self):
        """Return a list of AVAILABLE cross-correlation names 21 (YX, LR)"""
        return self.__cross21
    def paral(self):
        """Return a list of AVAILABLE parallel correlation names (XX, LL, etc)"""
        return self.__paral
    def paral11(self):
        """Return a list of AVAILABLE parallel correlation names (XX, LL) for pol 1"""
        return self.__paral11
    def paral22(self):
        """Return a list of AVAILABLE parallel correlation names (XX, LL) for pol 2"""
        return self.__paral22
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
        if True:
            try:
                return self.__coh[key]
            except:
                print sys.exc_info()
                keys = self.__coh.keys()
                print '** TDL_Cohset.__getitem(',key,'): not recognised in (',len(keys),'):',keys
                return False
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
        ss = TDL_common.Super.display(self, txt=txt, end=False, full=full)
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
        ss.append(indent1+' - leafgroups:      '+str(self.ParmSet.LeafSet.leafgroup().keys()))
        ss.append(indent1+' - parmgroups:      '+str(self.ParmSet.parmgroup_keys()))
        ss.append(indent1+' - solvegroups:     '+str(self.ParmSet.solvegroup_keys()))

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

        ss.append(indent2+' - '+str(self.ParmSet.oneliner()))
        ss.append(indent2+' - '+str(self.ParmSet.LeafSet.oneliner()))

        return TDL_common.Super.display_end(self, ss)


    def Joneset(self, clear=False):
        """Return the Joneset (if any) with which this Cohset has been corrupted"""
        if clear: self.__Joneset = None
        return self.__Joneset



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

        trace = pp['trace']
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

        # Get a list of keys specified by pp['key']:
        keys = self.find_keys (pp['key'], trace=trace)

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
                self._rider('selection_orphans', append=self.__coh[key])

        # Finished:
        self._history(append=funcname+' inarg = '+str(pp))
        self._history(append=funcname+' -> '+str(pp['select'])+': '+str(len(keys))+': '+str(keys))
        return keys

    #............................................................................

    def find_keys (self, key=None, trace=False):
        """Get a list of keys, specified by key"""
        keyin = key
        cohkeys = self.__coh.keys()
        affected = []
        if len(cohkeys)==0:                        # none available
            pass
        elif not key:                              # none selected
            pass
        elif isinstance(key, (list, tuple)):       # list
            affected = key                         # existence checked below
        elif isinstance(key, str):                 # string
            if key=='*':
                affected = cohkeys                 # all available keys
            elif key=='first':
                affected = [cohkeys[0]]            # first key
            elif key=='last':
                affected = [cohkeys[len(cohkeys)-1]] # last key
            elif key=='shortest':                  # key of shortest baseline
                rmin = 100000000
                for key in cohkeys:
                    if self.__rxyz[key]<rmin:
                        rmin = self.__rxyz[key]
                        affected = [key]           # one key only!
            elif key=='longest':                   # key of longest baseline
                rmax = 0
                for key in cohkeys:
                    if self.__rxyz[key]>rmax:
                        rmax = self.__rxyz[key]
                        affected = [key]           # one key only!
            else:                                  # Assume specific key name
                affected = [key]                   # a list with one element
        else:                                      # neither string nor list...?
            pass                                   # error?

        # Make a list (keys) of existing coh items to be processed:
        keys = []
        for key in affected:
            s0 = '- '+key+': '
            if not key in cohkeys:                 # key does not exist
                print s0,'does not exist in:',cohkeys
            else:
                if not self.__coh[key]:            # item has been deleted
                    if trace: print s0,'was deleted:',self.__coh[key]
                elif isinstance(self.__coh[key], str):          
                    if trace: print s0,'not a node:',self.__coh[key]
                else:
                    keys.append(key)               # OK, include in keys
        if trace: print '** .find_keys(',keyin,') ->',len(keys),':',keys
        return keys


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


    def bookmark (self, key='*', page=None, folder=None, trace=False):
        """Make bookmark(s) of the selected node(s)"""
        keys = self.keys()
        if len(keys)==0: return False
        cc = []
        for key1 in keys: cc.append(self.__coh[key1])
        return JEN_bookmarks.create (cc, page=page, folder=folder)


    def delete (self, selected=True, trace=False):
        """Delete (set to None) the (de-)selected coh items"""
        funcname = '::delete():'
        if trace: print '\n**',funcname,'(',selected,'):'
        kk = []
        for key in self.keys(selected=selected, trace=False):
            if trace: print '-',funcname,key,':',self.__coh[key],'-> None'
            if self.__coh[key]:
                self._rider('deletion_orphans', append=self.__coh[key])
                self.__coh[key] = None
            kk.append(key)
        self._history(append=funcname+' ('+str(len(kk))+'): '+str(kk))
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

    def zero_coh (self, ns):
        """Make a 'zero' cohaerency, i.e. one that produces a complex vellset with
        some freq dependence. This is needed until MeqSinks are upgraded (mar 2006)"""
        if not self.has_key('__zero_coh'):
            MeqFreq = ns.zero_coh_MeqFreq << Meq.Freq() 
            self.__zero_coh = ns.zero_coh << complex(1e-20)*MeqFreq
        return self.__zero_coh

    def zero(self, ns):
        """Make zero coherency matrices for all ifrs"""
        funcname = '::zero():'
        # c0 = complex(0)
        # zz = array([c0,c0,c0,c0])
        c0 = self.zero_coh(ns)
        zz = [c0,c0,c0,c0]
        for key in self.keys():
            s12 = self.__stations[key]
            self.__coh[key] = ns.cxzero22(s1=s12[0], s2=s12[1]) << Meq.Composer(dims=[2,2], *zz)
        self._history(append=funcname+' -> '+self.oneliner())

    def unity(self, ns):
        """Make unit coherency matrices for all ifrs"""
        funcname = '::unity():'
        c0 = complex(0.0)
        c1 = complex(1.0)
        zz = array([c1,c0,c0,c1])
        coh22 = ns.cxunity22 << Meq.Constant(value=zz, dims=[2,2])
        for key in self.keys():
            s12 = self.__stations[key]
            # self.__coh[key] = ns.cxunity22(s1=s12[0], s2=s12[1]) << Meq.Constant(value=zz, dims=[2,2])
            self.__coh[key] = coh22
        self._history(append=funcname+' -> '+self.oneliner())

    def uniform(self, ns, coh22):
        """Uniform coherency matrices (coh22) for all ifrs(qual)"""
        funcname = '::uniform():'
        uniqual = _counter(funcname, increment=-1)
        for key in self.keys():
            s12 = self.__stations[key]
            # self.__coh[key] = ns.uniform(uniqual)(s1=s12[0], s2=s12[1]) << Meq.Selector(coh22)
            self.__coh[key] = coh22
        self._history(append=funcname+' -> '+self.oneliner())


    def chain_solvers(self, ns, node, name=None):
        """Chain the solver subtrees (node), parallel to the main data-stream"""
        funcname = '::chain_solvers():'
        # First check for a previous solver subtree:
        previous = self._rider('chain_solvers', clear=True)
        if len(previous)>0:
            if not name: name = 'reqseq_chain_solvers'
            uniqual = _counter('chain_solvers', increment=-1)
            node = ns[name](uniqual) << Meq.ReqSeq(children=[previous[0], node])
        # Keep the solver subtree for future chaining:
        self._rider('chain_solvers', append=node)
        self._history(append=funcname+': '+str(node))
        return True


    def graft(self, ns, node, name=None, key='*', stepchild=False):
        """Graft the specified node(s) onto the streams of the specified ifr(s).
        By default, this is done by means of a MeqReqSeq, which only uses the result
        of its LAST (main-stream) child. This synchronises the ifr-streams if the
        same node (e.g. a solver or a dcoll) is grafted on all ifr-streams.
        If stepchild=True, make the node(s) step-children of a MeqSelector
        node that is inserted before the specified (key) coherency node.
        NB: This method is (only?) used for grafting a solver chain to a Cohset"""
        
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
        self._history(funcname+' '+gname+': len(gg)='+str(len(gg)))
        
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

        self._history(funcname+' -> '+self.oneliner())
        return True


    def splice(self, ns, Cohset, name=None):
        """Splice the specified Cohset into the current one (self), ifr-by-ifr.
        (it is assumed that both Cohsets have the same ifrs).
        This is done by means of a MeqReqSeq, which only uses the result
        of its LAST (main-stream) child."""
        funcname = '::splice():'

        # Names and qualifiers:
        uniqual = _counter(funcname, increment=-1)
        gname = 'splice'
        if isinstance(name, str): gname += '_'+name

        # Make ReqSeqs for all ifrs:
        for key in self.keys():
            children = [Cohset[key], self[key]]     # put its own child LAST
            rix = len(children)-1                   # use only the result of the last child
            self[key] = ns[gname].qmerge(self[key])(uniqual) << Meq.ReqSeq(children=children,
                                                                           result_index=rix)
        # Bookkeeping:
        self.updict_from_Cohset(Cohset)
        self._history(funcname+': '+Cohset.oneliner())
        self._history(funcname+' -> '+self.oneliner())
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
        self._history(append=funcname+' -> '+self.oneliner())
        return True


    def binop(self, ns, binop='Subtract', Cohset=None):
        """Perform the specified binary operation on two Cohsets (in place)"""
        if Cohset == None: return False
        funcname = '::binop('+str(binop)+','+Cohset.label()+'):'
        if not isinstance(binop, str): return False
        for key in self.keys():
            self.__coh[key] = ns << getattr(Meq, binop)(self.__coh[key], Cohset[key])
        self._history(append=funcname+' -> '+self.oneliner())
        return True


    def subtract(self, ns, Cohset=None):
        """Subtract the cohaerencies of the given Cohset from the corresponding internal ones"""
        # NB: Check whether punit is the same for both?
        funcname = '::subtract():'
        self.scope('subtracted')
        return self.binop(ns, binop='Subtract', Cohset=Cohset)


    def addNoise(self, ns, stddev=0.0, mean=0):
        """Add (gaussian) noise to the Cohset cohaerencies"""
        funcname = '::addNoise():'
        self.scope('addNoise')
        if not isinstance(mean, complex): mean = complex(mean) 
        uniqual = _counter(funcname, increment=-1)
        for key in self.keys():
            cc = []
            for i in range(4):
		real = ns.real(uniqual)(i) << Meq.GaussNoise(stddev=stddev)
		imag = ns.imag(uniqual)(i) << Meq.GaussNoise(stddev=stddev)
		cc.append(ns.gaussnoise(uniqual)(i) << Meq.ToComplex(children=[real, imag]))
            noise = ns['noise'].qmerge(self.__coh[key])(uniqual) << Meq.Matrix22(cc[0],cc[1],cc[2],cc[3])
            # Optional: Add the specified mean (not very useful...?):
            if abs(mean)>0:
                noise = ns << noise + mean
            self.__coh[key] = ns['addNoise'].qmerge(self.__coh[key])(uniqual) << Meq.Add(self.__coh[key], noise)
        self._history(append=funcname+': stddev='+str(stddev)+'Jy  (mean='+str(mean)+')')
        self._history(append=funcname+' -> '+self.oneliner())
        return True


    def replace(self, ns, Cohset=[]):
        """Replace with the (sum of the) cohaerencies of the given (list of) Cohset(s)"""
        funcname = '::replace():'
        if not isinstance(Cohset, (tuple,list)): Cohset = [Cohset]
        if len(Cohset)==0:
            return True                                # no change....?
        elif len(Cohset)>1:                            # more than one Cohset:
            Cohset[0].add(ns, Cohset[1:])              #   add them all in Cohset[0]
        # Replace the internal cohaerencies with those of Cohset[0]:
        for key in self.keys():
            self.__coh[key] = Cohset[0][key]
        # Reporting and book-keeping
        self.scope('replaced')
        self.updict_from_Cohset(Cohset[0])
        self._history(append=funcname+' -> '+self.oneliner())
        return True

    def common_quals(self, trace=False):
        """Find the common qualifiers of the Cohset cohaerencies"""
        funcname = '::common_quals():'
        cc = []
        for key in self.keys():
            cc.append(self.__coh[key])
        return TDL_common.common_quals(cc, trace=trace)


    def add(self, ns, Cohset=[]):
        """Add the cohaerencies of the given (list of) Cohset(s) to itself"""
        funcname = '::add():'
        if not isinstance(Cohset, (tuple,list)): Cohset = [Cohset]
        if len(Cohset)==0: return True                 # no change
        # Modify the internal cohaerencies:
        uniqual = _counter(funcname, increment=-1)
        for key in self.keys():
            itself = self.__coh[key]                   # its own node
            if isinstance(itself, str):                # e.g. nodestub placeholder....
                print funcname,': itself =',itself
                return False                           # problem
            cc = [itself]                              # make a list of children for MeqAdd
            for cs in Cohset:
                cc.append(cs[key])                     # collect corresponding (key) nodes
            cq = TDL_common.common_quals(cc)           # find their common qualifiers
            self.__coh[key] = ns['sum'](uniqual)(**cq) << Meq.Add(children=cc)
        # Reporting and book-keeping:
        self.scope('added')
        for cs in Cohset:
            self.updict_from_Cohset(cs)
        self._history(append=funcname+' -> '+self.oneliner())
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
        self.updict_from_Joneset(Joneset)
        self.__Joneset = Joneset                     
        self.scope(scope)
        self._history(append='corrected by: '+Joneset.oneliner())
        self._history(append=funcname+' -> '+self.oneliner())
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
        self.updict_from_Joneset(Joneset)
        self.__Joneset = Joneset                     
        self._history(append='corrupted by: '+Joneset.oneliner())
        self._history(append=funcname+' -> '+self.oneliner())
        return True

    #=================================================================================
    # Insertion of source visibilities:
    #=================================================================================

    def punit2coh(self, ns=None, Sixpack=None, Joneset=None, MSauxinfo=None):
        """Convert a prediction unit (punit, Sixpack) to source cohaerencies
        (visibilities) for all ifrs. If Joneset is specified, corrupt them with
        instrumental effects."""
        funcname = '::punit2coh():'
        uniqual = _counter(funcname, increment=-1)
        punit_name = str(Sixpack.label())

        # Information about source shape may be passed via the ParmSet rider:
        # See MG_JEN_Sixpack.py
        shapelist = Sixpack.ParmSet._rider('shape')      # -> list: [] or [shape-dict]

        if Sixpack.ispoint():                            # point source (or ell.gauss) 
            if len(shapelist)==0:                        # no shape parameters ([])
                # Put the same 'nominal' (i.e. uncorrupted) visibilities into all ifr-slots of cs1:
                nominal = Sixpack.coh22(ns, self.polrep())
                self.uniform(ns, nominal)
            else:
                # Put in an extra subtree for an elliptic gaussian extended source
                # rider (dict) fields: ['shape','major','minor','pa']
                # they contain node names, of nodes that should be in ns....
                self.elliptic_gaussian(ns, Sixpack, MSauxinfo=MSauxinfo)

            # Optionally, corrupt the visibilities with instrumental effects:
            if Joneset:
                self.corrupt (ns, Joneset)
        else:                                          # patch
            # Not yet implemented....
            node = Sixpack.root()

        # Finished: bookkeeping:
        self.updict_from_Sixpack(Sixpack)
        self._history(append=funcname+' -> '+self.oneliner())
        return True

    #----------------------------------------------------------------------------------

    def elliptic_gaussian(self, ns, Sixpack=None, MSauxinfo=None):
        """Make cohaerencies for an elliptic gaussian source, by multplying the nominal
        2x2 cohaerency matrix with a baseline-dependent factor."""
        funcname = '::elliptic_gaussian():'
        uniqual = _counter(funcname, increment=-1)
        nominal = Sixpack.coh22(ns, self.polrep())
        punit = str(Sixpack.label())
        scope = 'ellgauss'
        # Information about source shape may be passed via the ParmSet rider:
        # See MG_JEN_Sixpack.py
        shapelist = Sixpack.ParmSet._rider('shape')        # -> list: [] or [shape-dict]
        rider = shapelist[0]                               # assume dict (see below)
        # Put in extra subtrees for an elliptic gaussian extended source
        # rider (dict) fields: ['shape','major','minor','pa']
        # they contain node names, of nodes that should be in ns....
        for key in self.keys():
            s12 = self.__stations[key]
            uvw = MSauxinfo.node_uvw(s12[0], s12[1], ns=ns)
            u = ns << Meq.Selector(uvw, index=0)
            v = ns << Meq.Selector(uvw, index=1)
            if False:
                # Counter-rotate (u,v) with the source position angle:
                cospa = ns << Meq.Cos(rider['pa'])
                sinpa = ns << Meq.Sin(rider['pa'])
                urot = ns << (cospa*u - sinpa*v) 
                v = ns << (sinpa*u + cospa*v)
                u = urot
            umajor2 = ns << -(u*rider['major'])**2 
            vminor2 = ns << -(v*rider['minor'])**2
            factor = ns << Meq.Exp(ns << (umajor2 + vminor2))
            coh = ns[scope](uniqual)(s1=s12[0], s2=s12[1], q=punit) << Meq.Multiply(nominal,factor)
            self.__coh[key] = coh
        self.scope(scope)
        self._history(append=funcname+' -> '+self.oneliner())
        return True

    #=================================================================================
    # Update/updict from various objects
    #=================================================================================


    def update_from_Sixpack(self, Sixpack=None):
        """Update the internal info from a Sixpack object
        (NB: Not yet implemented in Sixpack....)"""
        #=======================================
        return self.updict_from_Sixpack(Sixpack)
        #=======================================
        if Sixpack==None: return False
        if not Sixpack.ParmSet.unsolvable():
            self.update_from_ParmSet(Sixpack.ParmSet)    
            self._history(append='updated from (not unsolvable): '+Sixpack.oneliner())
        else:
            self.update_from_LeafSet(Sixpack.ParmSet.LeafSet)    
            # A Sixpack that is 'unsolvable' has no solvegroups.
            # However, its parmgroups might interfere with parmgroups
            # of the same name (e.g. Gphase) from 'not unsolvable' Sixpacks.
            # Therefore, its parm info should not be copied here.
            self._history(append='not updated from (unsolvable): '+Sixpack.oneliner())
        return True

    def updict_from_Sixpack(self, Sixpack=None):
        """Updict the internal info from a Sixpack object
        (NB: Not yet implemented in Sixpack....)"""
        if Sixpack==None: return False
        if not Sixpack.ParmSet.unsolvable():
            self.updict_from_ParmSet(Sixpack.ParmSet)    
            self._history(append='updicted from (not unsolvable): '+Sixpack.oneliner())
        else: 
            self.updict_from_LeafSet(Sixpack.ParmSet.LeafSet)    
            # A Sixpack that is 'unsolvable' has no solvegroups.
            # However, its parmgroups might interfere with parmgroups
            # of the same name (e.g. Gphase) from 'not unsolvable' Sixpacks.
            # Therefore, its parm info should not be copied here.
            self._history(append='not updicted from (unsolvable): '+Sixpack.oneliner())
        return True

    def update_from_Joneset(self, Joneset=None):
        """Update the internal info from a (corrupting) Joneset object"""
        #=======================================
        return self.updict_from_Joneset(Joneset)
        #=======================================
        # (see Joneseq.Joneset())
        if Joneset==None: return False
        if not Joneset.ParmSet.unsolvable():
            self.__plot_color.update(Joneset.plot_color())
            self.__plot_style.update(Joneset.plot_style())
            self.__plot_size.update(Joneset.plot_size())
            self.update_from_ParmSet(Joneset.ParmSet)
            self._history(append='updated from (not unsolvable): '+Joneset.oneliner())
        else:
            self.update_from_LeafSet(Joneset.ParmSet.LeafSet)
            # A Joneset that is 'unsolvable' has no solvegroups.
            # However, its parmgroups might interfere with parmgroups
            # of the same name (e.g. Gphase) from 'not unsolvable' Jonesets.
            # Therefore, its parm info should not be copied here.
            self._history(append='not updated from (unsolvable): '+Joneset.oneliner())
        return True

    def updict_from_Joneset(self, Joneset=None):
        """Updict the internal info from a (corrupting) Joneset object"""
        # (see Joneseq.Joneset())
        if Joneset==None: return False
        if not Joneset.ParmSet.unsolvable():
            self._updict(self.__plot_color, Joneset.plot_color())
            self._updict(self.__plot_style, Joneset.plot_style())
            self._updict(self.__plot_size, Joneset.plot_size())
            self.updict_from_ParmSet(Joneset.ParmSet)
            self._history(append='updicted from (not unsolvable): '+Joneset.oneliner())
        else:
            self.updict_from_LeafSet(Joneset.ParmSet.LeafSet)
            # A Joneset that is 'unsolvable' has no solvegroups.
            # However, its parmgroups might interfere with parmgroups
            # of the same name (e.g. Gphase) from 'not unsolvable' Jonesets.
            # Therefore, its parm info should not be copied here.
            self._history(append='not updicted from (unsolvable): '+Joneset.oneliner())
        return True

    def update_from_Cohset(self, Cohset=None):
        """Update the internal info from another Cohset object"""
        #=======================================
        return self.updict_from_Cohset(Cohset)
        #=======================================
        if Cohset==None: return False
        self._updict_rider(Cohset._rider())
        # NB: use self._updict(self.__plot_color, Cohset.plot_color()).....
        # or rather self.updict_from_ParmSet(CohSet.ParmSet)...
        # NB: use JEN_PlotAttrib objects (default and named attributes...)
        self.__plot_color.update(Cohset.plot_color())
        self.__plot_style.update(Cohset.plot_style())
        self.__plot_size.update(Cohset.plot_size())
        self.update_from_ParmSet(Cohset.ParmSet)
        # self.update_from_LeafSet(Cohset.LeafSet)
        self._history(append='updated from: '+Cohset.oneliner())
        return True

    def updict_from_Cohset(self, Cohset=None):
        """Updict the internal info from another Cohset object"""
        if Cohset==None: return False
        self._updict_rider(Cohset._rider())
        self._updict( self.__plot_color, Cohset.plot_color())
        self._updict(self.__plot_style, Cohset.plot_style())
        self._updict(self.__plot_size, Cohset.plot_size())
        self.updict_from_ParmSet(Cohset.ParmSet)
        # self.updict_from_LeafSet(Cohset.LeafSet)
        self._history(append='updicted from: '+Cohset.oneliner())
        return True

    def update_from_ParmSet(self, ParmSet=None):
        """Update the internal info from a given ParmSet"""
        #=======================================
        return self.updict_from_ParmSet(ParmSet)
        #=======================================
        if ParmSet:
            self.ParmSet.update(ParmSet)
            self.ParmSet.LeafSet.update(ParmSet.LeafSet)
            self._history(append='updated from: '+ParmSet.oneliner())
        return True

    def updict_from_ParmSet(self, ParmSet=None):
        """Updict the internal info from a given ParmSet"""
        if ParmSet:
            self.ParmSet.updict(ParmSet)
            self.ParmSet.LeafSet.updict(ParmSet.LeafSet)
            self._history(append='updicted from: '+ParmSet.oneliner())
        return True

    def update_from_LeafSet(self, LeafSet=None):
        """Update the internal info from a given LeafSet"""
        #=======================================
        return self.updict_from_LeafSet(LeafSet)
        #=======================================
        if LeafSet:
            self.ParmSet.LeafSet.update(LeafSet)
            self._history(append='updated from: '+LeafSet.oneliner())
        return True

    def updict_from_LeafSet(self, LeafSet=None):
        """Updict the internal info from a given LeafSet"""
        if LeafSet:
            self.ParmSet.LeafSet.updict(LeafSet)
            self._history(append='updicted from: '+LeafSet.oneliner())
        return True

    #---------------------------------------------------------------------------

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
        self._history(append=funcname+' inarg = '+str(pp))
        self._history(append=funcname+' -> '+self.oneliner())
        return True


    def merge (self, ns, Cohset=None, **pp):
        """Replace any deleted coherencies with the corresponding ones from
        the given Cohset, provided that these are selected"""
        funcname = '::merge():'
        for key in self.__coh.keys():
            if not self.__cok[key]:            # if deleted
                self.__coh[key] = Cohset[key]  # use the one from Cohset
        # The input Cohset may contain parmgroup/solvegroup info:
        self.updict_from_Joneset(Cohset.Joneset())
        self.scope('merged')
        self._history(append=funcname+' -> '+self.oneliner())
        return True


    def Condeq (self, ns, Cohset=None, **pp):
        """Make (2x2) MeqCondeq nodes, using Cohset as the other input"""
        funcname = '::Condeq():'
        uniqual = _counter(funcname, increment=-1)
        punit = self.punit()
        scope = 'Condeq'

        # Optional: apply a unary operation to the Condeq inputs:
        pp.setdefault('unop', None)            # e.g. 'Abs'
        if isinstance(pp['unop'], str):
            Cohset.unop(ns, pp['unop'])
            self.unop(ns, pp['unop'])

        # Make condeq nodes for the selected keys:
        coh = dict()                       # use temporary dict for new nodes
        for key in self.keys():
            s12 = self.__stations[key]
            basel = str(around(self.__rxyz[key]))+'m'
            coh[key] = ns[scope+'_'+basel](uniqual)(s1=s12[0], s2=s12[1], q=punit) << Meq.Condeq(
                self.__coh[key], Cohset[key])
            # print '-',key,':',coh[key]

        # Copy the new condeq nodes to self.__coh, deleting the rest:
        for key in self.__coh.keys():
            if coh.has_key(key):
                self.__coh[key] = coh[key]
            elif self.__coh[key]:          # existing node
                self._rider('deletion_orphans', append=self.__coh[key])
                self.__coh[key] = None     # delete

        # The input Cohset may contain parmgroup/solvegroup info:
        self.updict_from_Joneset(Cohset.Joneset())
        self.updict_from_ParmSet(Cohset.ParmSet)
        self.scope(scope)
        self._history(append=funcname+' -> '+self.oneliner())
        return True


    def Condeq_redun (self, ns=None):
        """Make (2x2) MeqCondeq nodes, using Cohset as the other input.
        If no other Cohset given, make MeqCondeqs for redundant spacings"""
        funcname = '::Condeq_redun():'
        uniqual = _counter(funcname, increment=-1)
        punit = self.punit()
        scope = 'Condeq_redun'

        # Optional: apply a unary operation to the Condeq inputs:
        pp.setdefault('unop', None)        # e.g. 'Abs'
        if isinstance(pp['unop'], str):
            self.unop(ns, pp['unop'])

        coh = dict()                       # use temporary dict for new nodes
        for key in self.keys():
            s12 = self.__stations[key]
            basel = str(around(self.__rxyz[key]))+'m'
            # print '-',key,basel,s12
            # print '---',self.__redun[key]
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
                self._rider('deletion_orphans', append=self.__coh[key])
                self.__coh[key] = None     # delete

        self.scope(scope)
        self._history(append=funcname+' -> '+self.oneliner())
        return True


    def condeq_corrs (self, solvegroup, trace=False):
        """Return a (unique) list of correlations (corrs, e.g. ['XX','YY'])
        for the specified solvegroup. See also MG_JEN_Cohset.py"""
        pcorrs = self.ParmSet.condeq_corrs(solvegroup, trace=trace)
        if not isinstance(pcorrs, (list, tuple)): pcorrs = [pcorrs]
        # NB: This is VERY clumsy, but it works:
        cc = []
        for pc in pcorrs:
            if pc=='*': cc.extend(self.corrs())
            if pc=='paral': cc.extend(self.paral())
            if pc=='paral11': cc.extend(self.paral11())
            if pc=='paral22': cc.extend(self.paral22())
            if pc=='cross': cc.extend(self.cross())
            if pc=='cross12': cc.extend(self.cross12())
            if pc=='cross21': cc.extend(self.cross21())
            if pc=='corrI': cc.extend(self.corrI())
            if pc=='corrQ': cc.extend(self.corrQ())
            if pc=='corrU': cc.extend(self.corrU())
            if pc=='corrV': cc.extend(self.corrV())
        # Make unique list of corrs:
        corrs = []
        for c in cc:
            if not corrs.__contains__(c):
                corrs.append(c)
        # print '** condeq_corrs: ',pcorrs,'->',corrs
        return corrs


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
        self._history(append=funcname+' inarg = '+str(pp))
        self._history(append=funcname+' -> '+self.oneliner())
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
        # MS_corr_index = [0,1,2,3]                     # default
        MS_corr_index = self.MS_corr_index()            # defined in self.spigots()

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
            # for key in ['start','post']:           # ignore 'pre' for the moment....
                if isinstance(pp[key], (list,tuple)):
                    # for node in pp[key]: print '  -',node
                    if len(pp[key])==0:
                        pp[key] = None             # empty list gives an error....!
                    else:
                        # pp[key] = ns[key+'_VisDataMux'] << Meq.ReqSeq(children=pp[key])
                        pp[key] = ns[key+'_VisDataMux'] << Meq.ReqMux(children=pp[key]) 
                        # pp[key] = ns[key+'_VisDataMux'] << Meq.Add(children=pp[key])
            root = ns['Cohset_VisDataMux'] << Meq.VisDataMux(start=pp['start'],
                                                             pre=pp['pre'],
                                                             post=pp['post'])
            
        # Bookkeeping:
        self.cleanup(ns)
        self.scope('sink')
        self._history(append=funcname+' inarg = '+str(pp))
        self._history(append=funcname+' MS_corr_index = '+str(MS_corr_index))
        self._history(append=funcname+' -> '+self.oneliner())
        # print '** End of: TDL_Cohset.sinks()\n'
        return True

    #------------------------------------------------------------------------------------

    def cleanup(self, ns=None):
        """Clean up the current Cohset"""
        # Bundle the collected orphans (minimise browser clutter)
        for key in ['deletion_orphans','selection_orphans']:
            orphans = self._rider(key, clear=False, report=True)
            # print '\n** .cleanup():',key,'-> orphans(',len(orphans),'):',orphans
            if len(orphans)>0:
                uniqual = _counter(key, increment=-1)
                root_node = ns[key](uniqual) << Meq.Composer(children=orphans)
                # print '   ->',root_node
        return True


    #------------------------------------------------------------------------------------

    def fullDomainMux (self, ns, **pp):
        """Optionally, create another VisDataMux with a fixed name (fullDomainMux),
        to issue a request with a large domain to selected nodes.
        For instance: solved MeqParms for the entire observation.
        """
        funcname = '::fullDomainMux():'

        # Input arguments:
        pp.setdefault('start', None)                    # optional child of MeqVisDataMux
        pp.setdefault('pre', None)                      # optional child of MeqVisDataMux
        pp.setdefault('post', None)                     # optional child of MeqVisDataMux

        if True:
            for key in ['start','pre','post']:
                if isinstance(pp[key], (list,tuple)):
                    # print '-',key,':',type(pp[key]),len(pp[key])
                    # for node in pp[key]: print '  -',node
                    if len(pp[key])==0:
                        pp[key] = None                  # empty list gives an error....!
                    else:
                        pp[key] = ns[key+'_fullDomainMux'] << Meq.ReqMux(children=pp[key]) 
                    # print '-',key,':',pp[key]
                # print '-',key,':',pp[key]
            root = ns['Cohset_fullDomainMux'] << Meq.VisDataMux(start=pp['start'],
                                                                pre=pp['pre'],
                                                                post=pp['post'])

        # Bookkeeping:
        qq = TDL_common.unclutter_inarg(pp)
        self._history(append=funcname+' inarg = '+str(qq))
        self._history(append=funcname+' -> '+self.oneliner())
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


    #------------------------------------------------------------------------------------

    def TDLRuntimeOption (self, key=None, value=None, trace=True):
        """Change the state of existing node(s) before execution"""
        s1 = '** Cohset.TDLRuntimeOption('+str(key)+'='+str(value)+'): '
        solvers = self._rider('solver')
        if key=='num_iter':
            print '\n',s1,' solvers=',solvers,'\n'
            for solver in solvers:
                # set_state(solver.name, num_iter=value)
                print '** set_state() not available (Timba.meqkernel error)'
        else:
            print '\n',s1,'not recognised\n'
        return True


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

    if 1:
        cs.find_keys('longest', trace=True)
        cs.find_keys('shortest', trace=True)
        cs.find_keys('first', trace=True)
        cs.find_keys('last', trace=True)
        cs.find_keys('xxx', trace=True)

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


    if 0:
        coll = cs._rider('dcoll', ns << Meq.DataCollect())
        coll = cs._rider('hcoll', ns << Meq.historyCollect())
        coll = cs._rider('hcoll', ns << Meq.historyCollect())
        # cs._rider(clear=True)
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









 

