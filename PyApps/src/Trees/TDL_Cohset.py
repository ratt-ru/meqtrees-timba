# file: .../Timba/PyApps/src/Trees/TDL_Cohset.py
#
# Author: J.E.Noordam
#
# Short description:
#    A Cohset encapsulates a set of 2x2 cohaerency matrices for a specific set of ifrs.
#
# History:
#    - 02 sep 2005: creation
#
# Remarks:
#    A Cohset can also be seen as a 'travelling cohaerency front': For each ifr, it
#    contains the root node of a subtree. For each operation on a Cohset, each ifr
#    node is replaced by a new root node, which has the old one as one of its children.
#    A one-line description of the operation is added to the Cohset history.
#    Thus, a Cohset is used to build up a forest of parallel subtrees.
#

from Timba.TDL import *
from copy import deepcopy

from Timba.Trees import TDL_common
from Timba.Trees import TDL_Joneset


#**************************************************************************************
# Some useful helper functions:
#**************************************************************************************

def stations2ifrs(stations=range(3)):
    # Make a list of ifrs (station-pair tuples) from the given stations:
    ifrs  = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ];
    return ifrs

def ifrs2stations(ifrs=[(0,1)]):
    # The reverse of stations2ifrs()
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

    def __init__(self, **pp):
        
        pp.setdefault('scope', '<cscope>')
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
            key = str(station)
            self.__station_index[key] = station


        # This is the ONLY place where the self.__coh field-keys are determined
        self.__stations = {}                     # integer tuples (s1,s2)
        self.__coh = {}
        for (st1,st2) in pp['ifrs']:
            key = str(st1)+'_'+str(st2)          # NB: key should ALWAYS be string!!
            self.__stations[key] = (str(st1),str(st2))  
            self.__coh[key] = 'coh['+key+'] (placeholder for nodestub)'
        self.__dims = [1]                        # shape of coh tensor nodes

        # Polarisation representation
        self.__polrep = pp['polrep']
        self.__corrs = ['XX', 'XY', 'YX', 'YY']
        if self.__polrep == 'circular':
            self.__corrs = ['RR', 'RL', 'LR', 'LL']

        # The Cohset contains the position (RA, Dec) of the current phase centre:
        self.__phase_centre = pp['phase_centre']

        # The Cohset may carry Joneset information for solvers:
        self.__parmgroup = dict()
        self.__solvegroup = dict()
        self.__condeq_corrs = dict()

        # Plot information (standard, but extended from Jonesets):
        self.__plot_color = TDL_common.plot_color()
        self.__plot_style = TDL_common.plot_style()
        self.__plot_size = TDL_common.plot_size()

        # Calculate derived values from primary ones
        self.calc_derived()

    def calc_derived(self):
        # Calculate derived values from primary ones
        self.__paral = []
        self.__cross = []
        for corr in self.__corrs:
            if ['XX','YY','RR','LL'].__contains__(corr): self.__paral.append(corr)
            if ['XY','YX','RL','LR'].__contains__(corr): self.__cross.append(corr)
        return True

    def __getitem__(self, key):
        # This allows indexing by key and by index nr:
        if isinstance(key, int): key = self.__coh.keys()[key]
        return self.__coh[key]

    def __setitem__(self, key, value):
        self.__coh[key] = value
        return self.__coh[key]

    # Access to class attribites:
    def plot_color(self): return self.__plot_color
    def plot_style(self): return self.__plot_style
    def plot_size(self): return self.__plot_size
    def parmgroup(self): return self.__parmgroup
    def solvegroup(self): return self.__solvegroup
    def condeq_corrs(self): return self.__condeq_corrs

    # Access to instance attribites:
    def polrep(self): return self.__polrep
    def corrs(self): return self.__corrs
    def cross(self): return self.__cross
    def paral(self): return self.__paral
    def phase_centre(self): return self.__phase_centre

    def scope(self, new=None):
        if isinstance(new, str): self.__scope = new
        return self.__scope
    def punit(self): return self.__punit
    def coh(self): return self.__coh
    def stations(self): return self.__stations
    def station_index(self): return self.__station_index

    # Some derived values:
    def keys(self): return self.__coh.keys()
    def has_key(self, key): return self.keys().__contains__(key)
    def len(self): return len(self.__coh)
    def dims(self): return self.__dims

    def nodenames(self, select='all'):
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
        s = TDL_common.Super.oneliner(self)
        s = s+' punit='+str(self.punit())
        s = s+' dims='+str(self.dims())
        s = s+' '+str(self.corrs())
        s = s+' len='+str(self.len())
        s = s+' ('+str(self.nodenames('first'))+',...)'
        return s

    def display(self, txt=None, full=False):
        s = TDL_common.Super.display(self, txt=txt, end=False)
        indent1 = 2*' '
        indent2 = 6*' '
        print indent1,'- phase_centre:   ',self.phase_centre()
        print indent1,'- polrep:         ',self.polrep(),self.corrs(),' paral=',self.paral(),' cross=',self.cross()
        print indent1,'- station_index:  ',self.station_index()
        # print indent1,'- plot_color:     ',self.plot_color()
        # print indent1,'- plot_style:     ',self.plot_style()
        # print indent1,'- plot_size:      ',self.plot_size()
        print indent1,'- Parmgroups:     ',self.parmgroup().keys()
        print indent1,'- Solvegroups:    ',self.solvegroup().keys()
        print indent1,'- Condeq_corrs:   ',self.condeq_corrs().keys()
        print indent1,'- Available 2x2 cohaerency matrices (',self.len(),'):'
        if full or self.len()<10:
            for key in self.__coh.keys():
                s12 = self.__stations[key]
                print indent2,'-',key,s12,':',self.__coh[key]
        else:
            keys = self.__coh.keys()
            n = len(keys)-1
            print indent2,'- first:',keys[0],':',self.__coh[keys[0]]
            print indent2,'  ....'
            print indent2,'- last: ',keys[n],':',self.__coh[keys[n]]
        TDL_common.Super.display_end(self)



    #--------------------------------------------------------------
    # Methods that generate new nodes (and thus require nodescope):
    #--------------------------------------------------------------

    def nominal(self, ns, coh0):
        # Make a record/dict of identical coherency matrices for all ifrs:
        funcname = '::nominal():'
        unique = _counter(funcname, increment=1)
        for key in self.keys():
            s12 = self.__stations[key]
            self.__coh[key] = ns.nominal(unique)(s1=s12[0], s2=s12[1]) << Meq.Selector(coh0)
        self.__dims = [2,2]
        self.history(append=funcname+' -> '+self.oneliner())


    def graft(self, ns, node, key='first', stepchild=True):
        # Insert the specified node at the specified ifr
        # If stepchild=True, make the node(s) step-children of a MeqSelector
        # node that is inserted before the specified (key) coherency node:
        funcname = '::graft():'
        if not isinstance(node, (tuple, list)): node = [node]
        key = self.keys()[0]
        unique = _counter(funcname, increment=1)
        if stepchild:
            self[key] = ns.step_graft.qmerge(self[key])(unique) << Meq.Selector(self[key], stepchildren=node)
        else:
            children = [self[key]]
            children.extend(node)
            self[key] = ns.graft.qmerge(self[key])(unique) << Meq.Selector(*children)
        self.history(funcname+' -> '+self.oneliner())
        return True

        

    def unop(self, ns, unop=None, right2left=False):
        # Perform the specified (sequence of) unary operations (in place)
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
        # Perform the specified binary operation on two Cohsets (in place)
        if Cohset == None: return False
        funcname = '::binop('+str(binop)+','+Cohset.label()+'):'
        if not isinstance(binop, str): return False
        for key in self.keys():
            self.__coh[key] = ns << getattr(Meq, binop)(self.__coh[key], Cohset[key])
        self.history(append=funcname+' -> '+self.oneliner())
        return True


    def subtract(self, ns, Cohset=None):
        # Subtract the cohaerencies in the two cohsets.
        # NB: Check whether punit is the same for both?
        self.scope('subtracted')
        return self.binop(ns, binop='Subtract', Cohset=Cohset)


    def shift_phase_centre(self, ns, punit=None):
        # Shift the phase centre from the current position to the position (RA, DEC)
        # of the given punit (sixpack?, twopack?, other?):
        self.__punit = punit
        self.scope('shifted_to_'+punit)
        pass


    def correct(self, ns, Joneset=None):
        # Correct the Cohset by matrix multiplication with the INVERSE of the given Joneset:
        funcname = '::correct():'
        unique = _counter(funcname, increment=1)
        self.__punit = Joneset.punit()
        for key in self.keys():
            s12 = self.__stations[key]
            coh = ns.corrected(unique)(s1=s12[0], s2=s12[1], q=self.punit()) << Meq.MatrixMultiply(
                Meq.MatrixInvert22(Joneset[s12[0]]),
                self.__coh[key],
                ns << Meq.MatrixInvert22(ns << Meq.ConjTranspose(Joneset[s12[1]])))
            self.__coh[key] = coh 
        self.update_from_Joneset(Joneset)
        self.scope('corrected')
        self.history(append=funcname+' -> '+self.oneliner())
        return True

    def corrupt(self, ns, Joneset=None):
        # Corrupt the Cohset by matrix multiplication with the given Joneset:
        funcname = '::corrupt():'
        unique = _counter(funcname, increment=1)
        self.__punit = Joneset.punit()
        for key in self.keys():
            s12 = self.__stations[key]
            coh = ns.corrupted(unique)(s1=s12[0], s2=s12[1], q=self.punit()) << Meq.MatrixMultiply(
                Joneset[s12[0]],
                self.__coh[key],
                ns << Meq.ConjTranspose(Joneset[s12[1]]))
            self.__coh[key] = coh
        self.scope('corrupted')
        self.update_from_Joneset(Joneset)
        self.history(append=funcname+' -> '+self.oneliner())
        return True


    def update_from_Joneset(self, Joneset=None):
        # Update the internal info from another Joneset object:
        # (see Joneseq.Joneset())
        if Joneset==None: return False
        self.__parmgroup.update(Joneset.parmgroup())
        self.__solvegroup.update(Joneset.solvegroup())
        self.__condeq_corrs.update(Joneset.condeq_corrs())
        self.__plot_color.update(Joneset.plot_color())
        self.__plot_style.update(Joneset.plot_style())
        self.__plot_size.update(Joneset.plot_size())
        self.history(append='updated from: '+Joneset.oneliner())
        return True

    def update_from_Cohset(self, Cohset=None):
        # Update the internal info from another Cohset object:
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
        # Get the index nrs (in self.__corr) of the specified corrs:
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


    def select(self, ns, corrs=None):
        # Select a subset of the available corrs: 
        funcname = '::select():'
        if corrs==None: return False
        icorr = self.icorr(corrs)
        if len(icorr)==0: return False

        # Adjust the corrs info vectors:
        newcorrs = []
        for i in icorr: newcorrs.append(self.__corrs[i])
        self.__corrs = newcorrs
        self.calc_derived()
        print '** .select(',corrs,copy,') ->',self.corrs(),self.paral(),self.cross()

        # Make MeqSelector nodes that select the specified corrs:
        unique = _counter(funcname, increment=1)
        multi = (len(icorr)>1)
        for key in self.keys():
            s12 = self.__stations[key]
            coh = ns.select(unique)(s1=s12[0], s2=s12[1]) << Meq.Selector(self.__coh[key], index=icorr, multi=multi)
            self.__coh[key] = coh
        # Adjust the coherence shape, if necessary:  
        if len(icorr)<4: self.__dims = [len(icorr)]            #...shape...??
        self.scope('selected_corrs')
        self.history(append=funcname+' -> '+self.oneliner())
        return True


#======================================================================================

    def spigots (self, ns=0, **pp):
        funcname = '::spigots():'
        # Input arguments:
        pp.setdefault('flag_bit', 4)                     # .....
        pp.setdefault('input_column', 'DATA')            # .....
        pp = record(pp)
        
        # Make a record/dict of spigots that produce 2x2 coherency matrices:
        for key in self.keys():
            s12 = self.__stations[key]
            i1 = self.station_index[s12[0]]              # integer
            i2 = self.station_index[s12[1]]              # integer
            self.__coh[key] = ns.spigot(s1=s12[0],s2=s12[1]) << Meq.Spigot(station_1_index=i1,
                                                                           station_2_index=i2,
                                                                           flag_bit=pp['flag_bit'],
                                                                           input_column=pp['input_column'])
        self.__dims = [2,2]
        self.label('spigots')
        self.scope('spigots')
        self.history(append=funcname+' -> '+self.oneliner())
        return True


    def sinks (self, ns, **pp):
        """attaches the coherency matrices to MeqSink nodes""" 
        funcname = '::sinks():'

        # Input arguments:
        pp.setdefault('output_col', 'RESIDUALS')        # name of MS output column (NONE means inhibited)
        pp = record(pp)

        # Duplicate for all 4 children:
        oc = pp['output_col']
        pp['output_col'] = [oc,oc,oc,oc] 

        # Make separate sinks for each ifr:
        for key in self.keys():
            s12 = self.__stations[key]
            i1 = self.station_index[s12[0]]              # integer
            i2 = self.station_index[s12[1]]              # integer
            self.__coh[key] = ns.MeqSink(s1=s12[0], s2=s12[1]) << Meq.Sink(self.__coh[key],
                                                                           station_1_index=i1,
                                                                           station_2_index=i2,
                                                                           corr_index=[0,1,2,3],
                                                                           output_col=pp['output_col'])
        self.scope('sinks')
        self.history(append=funcname+' -> '+self.oneliner())
        return True


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
    from numarray import *
    from Timba.Contrib.JEN import MG_JEN_Joneset
    from Timba.Contrib.JEN import MG_JEN_exec
    ns = NodeScope()
    nsim = ns.Subscope('_')
    
    stations = range(3)
    ifrs = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ]
    cs = Cohset(label='initial', polrep='circular', stations=stations)
    cs.display('initial')

    if 0:
        print '** dir(cs) ->',dir(cs)
        print '** cs.__doc__ ->',cs.__doc__
        print '** cs.__module__ ->',cs.__module__
        print

    if 0:
        # Access to coh etc
        print
        print 'cs.coh()[key]:'
        for key in cs.keys(): print '-',key, cs.coh()[key]
        print 'cs[key]:'
        for key in cs.keys(): print '-',key, cs[key]
        print 'item in cs:'
        for item in cs: print '- item:',item
        print
        for corr in cs.corrs(): print '-',corr, cs.plot_color()[corr],cs.plot_style()[corr]
        print

    if 0:
        coh0 = ns << Meq.Constant(array([[11,12],[21,22]]), dim=[2,2])
        MG_JEN_exec.display_subtree(coh0, 'coh0', full=True)
        print '\n** coh0=',coh0
        print type(coh0),isinstance(coh0,type(ns<<0))
        cs.nominal(ns, coh0)
        cs.display('.nominal()')
        print '** .nodenames() -> (',len(cs.nodenames()),'):',cs.nodenames()
    
    if 0:
        if 0:
            cs.icorr()
            cs.icorr(['RR','LL'])
            cs.icorr(['LR'])
            cs.icorr(['XY'])
        cs1 = cs.copy()
        cs.display('after .copy()')
        cs1.display('after .copy()')
        cs1.select(ns, ['RR','LL'])
        # cs1.select(ns, ['LL','LR'])
        # cs1.select(ns, ['LR'])
        cs1.display('after .select()')

    if 0:
        keys = cs.keys()
        print 'cs.has_key(',keys[0],') ->',cs.has_key(keys[0])
        print 'cs.has_key(wrong) ->',cs.has_key('wrong')

    if 0:
        js = MG_JEN_Joneset.GJones (ns, stations=stations)
        cs.corrupt(ns, js)
        if False:
            js = MG_JEN_Joneset.BJones (ns, stations=stations)
            cs.correct(ns, js)

    if 0:
        node = ns << 0.3
        print dir(node)
        cs.graft(ns, node, stepchild=False)
        cs.display('after .insert()')

    if 0:
        cs.subtract(ns, cs)
        cs.unop(ns, ['Cos','Sin'], right2left=True)
        cs.unop(ns, ['Cos','Sin'])

    if 0:
        cs.spigots(ns)
        cs.sinks(ns)
        if 1:
            sink = cs.simul_sink(ns)
            MG_JEN_exec.display_subtree(sink, 'simul_sink', full=True, recurse=5)

    if 0:
        stations = range(5)
        stations = [0,4,7,2,8,-6,-7]
        stations = ['A','G','k',4]
        print 'stations =',stations
        ifrs = stations2ifrs(stations)
        print 'ifrs =',ifrs
        print 'stations =',ifrs2stations(ifrs)

    if 0:
        # Display the final result:
        k = 0 ; MG_JEN_exec.display_subtree(cs[k], 'cs['+str(k)+']', full=True, recurse=5)
        cs.display('final result')



#============================================================================================









 

