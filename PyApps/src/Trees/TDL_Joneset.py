# TDL_Joneset.py
#
# Author: J.E.Noordam
#
# Short description:
#    A Joneset object encapsulates 2x2 instrumental jones matrices for a set of stations.
#
# History:
#    - 02 sep 2005: creation
#    - 10 sep 2005: more or less stable
#    - 23 sep 2005: MeqParm: use_previous==True, self.parmtable
#
# Full description:
#



#=================================================================================
# Preamble:
#=================================================================================

from Timba.TDL import *
from copy import deepcopy

from Timba.Trees import TDL_common




#=================================================================================
# Class Joneset
#=================================================================================


class Joneset (TDL_common.Super):
    """A Joneset object encapsulates 2x2 instrumental jones matrices for a set of stations"""

    def __init__(self, **pp):

        # Input arguments:
        pp.setdefault('scope', '<jscope>')           # used in visualisation etc
        pp.setdefault('jchar', None)                 # single-character identifier (e.g. 'G') 
        pp.setdefault('polrep', 'linear')
        pp.setdefault('punit', 'uvp')                # name of predict-unit (source/patch)
        pp.setdefault('solvable', True)              # if False, do not store parmgroup info
        pp.setdefault('parmtable', None)             # name of MeqParm table (AIPS++)

        self.__scope = pp['scope']
        self.__punit = pp['punit']
        self.__solvable = pp['solvable']
        self.__parmtable = pp['parmtable']
        self.check_parmtable_extension()

        TDL_common.Super.__init__(self, type='Joneset', **pp)

        self.__jchar = pp['jchar']
        if not isinstance(self.__jchar, str): self.__jchar = self.label()[0]
        self.__jchar = self.__jchar[0]               # single character

        self.clear()

        # Polarisation representation
        self.__polrep = pp['polrep']
        self.__pols = ['X', 'Y']
        if self.__polrep == 'circular':
            self.__pols = ['R', 'L']
        return None

    def clear(self):
        self.__jones = dict()
        self.__parmgroup = dict()
        self.__solvegroup = dict()
        self.__condeq_corrs = dict()
        self.__plot_color = TDL_common.plot_color()
        self.__plot_style = TDL_common.plot_style()
        self.__plot_size = TDL_common.plot_size()
        self.__MeqParm = dict()
        self.__node_groups = ['Parm']

    def __getitem__(self, key):
        # This allows indexing by key and by index nr:
        if isinstance(key, int): key = self.__jones.keys()[key]
        return self.__jones[key]

    def __setitem__(self, key, value):
        self.__jones[key] = value
        return self.__jones[key]

    def register(self, key=None, ipol=None, color=None, style='circle', size=10, corrs=None):
        # Register a parameter group
        if isinstance(ipol, int): key = key+'_'+self.pols(ipol)     # append (X,Y,R,L) if requirec
        self.__parmgroup[key] = []
        self.__plot_color[key] = color
        self.__plot_style[key] = style
        self.__plot_size[key] = size
        if corrs=='all': corrs = self.corrs_all()
        if corrs=='paral': corrs = self.corrs_paral()
        if corrs=='paral1': corrs = self.corrs_paral1()
        if corrs=='paral2': corrs = self.corrs_paral2()
        if corrs=='cross': corrs = self.corrs_cross()
        # if self.corrs_all().__contains__(corrs): corrs = corrs      # single corr (e.g. 'RR')
        self.__condeq_corrs[key] = corrs
        s = 'Register parmgroup: '+key+': '+str(color)+' '+str(style)+' '+str(size)+' '+str(corrs)+' '
        self.history(s)
        self.define_solvegroup(key, parmgroup=[key])
        return key                                                  # return the actual key name


    def define_solvegroup(self, key=None, parmgroup=None):
      print '\n** .define_solvegroup(',key,parmgroup,'):'
      # Derive a new solvegroup by combining existing parmgroups:
      # These are used when defining a solver downstream (see Cohset)
      if not self.solvable(): return False                          # only if Joneset is solvable
      if not isinstance(parmgroup, list): parmgroup = [parmgroup]
      self.__solvegroup[key] = parmgroup                            # list of existing parmgroup keys
      # Each solvegroup has a list of condeq_corrs, which allows the
      # solver to have only condeqs for the relevant corrs:
      corrs = []
      for pg in self.__solvegroup[key]:
          for corr in self.__condeq_corrs[pg]:
              if not corrs.__contains__(corr): corrs.append(corr)
              print '   pg=',pg,' corr=',corr,'   corrs=',corrs
      self.__condeq_corrs[key] = corrs
      return True


    def cleanup(self):
      # Remove empty parmgroups/solvegroups:
      removed = []
      for key in self.__parmgroup.keys():
        if len(self.__parmgroup[key])==0:
          self.__parmgroup.__delitem__(key)
          removed.append(key)
      # Remove solvegroups that have parmgroup members that do not exist:
      for skey in self.__solvegroup.keys():
        ok = True
        for key in self.__solvegroup[skey]:
          if not self.__parmgroup.has_key(key):
            ok = False
        if not ok: self.__solvegroup.__delitem__(skey)
      self.history ('.cleanup(): removed parmgroup(s): '+str(removed))
      # Remove condeq_corrs that have no solvegroup counterpart:
      for key in self.__condeq_corrs.keys():
        if not self.__solvegroup.has_key(key):
          self.__condeq_corrs.__delitem__(key)
      return True

    def node_groups(self, new=None):
      if not new==None:
        if not isinstance(new, (tuple, list)): new = [new]
        for png in new:
          if not self.__node_groups.__contains__(png):
            self.__node_groups.append(png)
      return self.__node_groups

    def append(self, key=None, node=None):
        """Append a named (key) 2x2 jones matrix node to the internal jones set"""
        key = str(key)          # potential __getitem__() problems if key is integer!! 
        self.__jones[key] = node
        return self.len()

    def define_MeqParm(self, ns, key=None, station=None, default=0,
                       node_groups='Parm', use_previous=True, tile_size=None):
        """Convenience function to create a MeqParm node"""
        # NB: If use_previous==True, the MeqParm will use its current funklet (if any)
        #     as starting point for the next snippet solution, unless a suitable funklet
        #     was found in the MeqParm table. If False, it will use the default funklet first.
        tiling = record()
        if tile_size: tiling.time = tile_size
        quals = dict(q=self.punit());
        if station is not None:
            quals['s'] = station;
        node = ns[key](**quals) << Meq.Parm(default,
                                            node_groups=self.node_groups(),
                                            use_previous=use_previous,
                                            tiling=tiling,
                                            table_name=self.parmtable())
        # Put the node into the internal MeqParm buffer for later use:
        self.__MeqParm[key] = node
        return node

    def MeqParm(self, update=False, reset=False):
        if update:
          # Append the accumulated MeqParm node names to their respective parmgroups:
            for key in self.__MeqParm.keys():
              nodename = self.__MeqParm[key].name
              self.__parmgroup[key].append(nodename)
        if reset:
          # Reset the MeqParm buffer:
          ss = self.__MeqParm
          self.__MeqParm = dict()
          # Always return self.__MeqParm as it was before reset:
          return ss
        return self.__MeqParm

    # Access functions:
    def scope(self, new=None):
        if isinstance(new, str): self.__scope = new
        return self.__scope
    def jchar(self): return self.__jchar
    def punit(self): return self.__punit
    def solvable(self): return self.__solvable
    def polrep(self): return self.__polrep
    def pols(self, ipol=None):
        if ipol==None: return self.__pols
        return self.__pols[ipol-1]

    def parmtable(self, new=None):
        if isinstance(new, str):
            self.__parmtable = new
            self.check_parmtable_extension()
        return self.__parmtable
    def check_parmtable_extension(self):
        if isinstance(self.__parmtable, str):
            ss = self.__parmtable.split('.')
            if len(ss)==1: self.__parmtable += '.mep'
            return self.__parmtable.split('.')[1]
        return True

    def condeq_corrs(self): return self.__condeq_corrs
    def corrs_paral(self):
      return [self.pols(1)+self.pols(1), self.pols(2)+self.pols(2)]
    def corrs_paral1(self): return [self.pols(1)+self.pols(1)]
    def corrs_paral2(self): return [self.pols(2)+self.pols(2)]
    def corrs_cross(self):
      return [self.pols(1)+self.pols(2), self.pols(2)+self.pols(1)]
    def corrs_all(self):
      return [self.pols(1)+self.pols(1), self.pols(1)+self.pols(1),
              self.pols(2)+self.pols(2), self.pols(2)+self.pols(2)]

    def jones(self): return self.__jones
    def len(self): return len(self.__jones)
    def keys(self): return self.__jones.keys()
    def has_key(self, key): return self.keys().__contains__(key)

    def parmgroup(self): return self.__parmgroup
    def solvegroup(self): return self.__solvegroup
    def plot_color(self): return self.__plot_color
    def plot_style(self): return self.__plot_style
    def plot_size(self): return self.__plot_size
            
    def nodenames(self, select='all'):
        # Return the names of the jones matrix node names:
        nn = []
        for key in self.keys():
            if isinstance(self.__jones[key], str):
                nn.append(self.__jones[key])
            else:
                nn.append(self.__jones[key].name)
        if len(nn)==0: return '<empty>'
        if select=='first': return nn[0]
        if select=='last': return nn[len(nn)-1]
        return nn

    def oneliner(self):
        s = TDL_common.Super.oneliner(self)
        s = s+' ('+str(self.jchar())+')'
        s = s+' punit='+str(self.punit())
        s = s+' '+str(self.pols())
        s = s+' '+str(self.node_groups())
        s = s+' solvable='+str(self.solvable())
        s = s+' parmtable='+str(self.parmtable())
        s = s+' len='+str(self.len())
        s = s+' ('+str(self.nodenames('first'))+',...)'
        return s

    def display(self, txt=None, full=False):
        ss = TDL_common.Super.display (self, txt=txt, end=False)
        indent1 = 2*' '
        indent2 = 6*' '

        ss.append(indent1+' - Registered parmgroups:')
        for key in self.parmgroup().keys():
          pgk = self.parmgroup()[key]
          n = len(pgk)
          if full or n<3:
            ss.append(indent2+' - '+key+' ( '+str(n)+' ): '+str(pgk))
          else:
            ss.append(indent2+' - '+key+' ( '+str(n)+' ): '+pgk[0]+' ... '+pgk[n-1])

        ss.append(indent1+' - solvegroups ( solvable = '+str(self.solvable())+' , node_groups = '+str(self.node_groups())+' ):')
        for key in self.solvegroup().keys():
            ss.append(indent2+' - '+key+' : parmgroups: '+str(self.solvegroup()[key])+' , corrs: '+str(self.condeq_corrs()[key]))

        ss.append(indent1+' - Station jones matrix nodes ( '+str(self.len())+' ):')
        if full or self.len()<15:
            for key in self.keys():
                ss.append(indent2+' - '+key+' : '+str(self.__jones[key]))
        else:
            keys = self.keys()
            n = len(keys)-1
            ss.append(indent2+' - first: '+keys[0]+' : '+str(self.__jones[keys[0]]))
            ss.append(indent2+'   ....')
            ss.append(indent2+' - last:  '+keys[n]+' : '+str(self.__jones[keys[n]]))
        return TDL_common.Super.display_end (self, ss)


    def update(self, Joneset=None):
        # Update the internal info from another Joneset object:
        # (used in Joneseq.make_Joneset())
        if Joneset==None: return False
        self.__jchar += Joneset.jchar()
        if not self.solvable():
            self.history(append='updated (not solvable) from: '+Joneset.oneliner())
        elif Joneset.solvable():
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



#=================================================================================
# Class Joneseq: Holds (and multiplies) a sequence of Joneset objects 
#=================================================================================


class Joneseq (TDL_common.Super):

    def __init__(self, **pp):
        pp.setdefault('label', 'JJones')
        TDL_common.Super.__init__(self, type='Joneseq', **pp)
        self.clear()
        return None

    def __getitem__(self, index):
        return self.__sequence[index]

    def clear(self):
        self.__scope = '<scope>'
        self.__sequence = []
        self.__polrep = '<polrep>'
        self.__punit = '<punit>'

    def sequence(self): return self.__sequence
    def keys(self): return self.__sequence.keys()
    def len(self): return len(self.__sequence)
    def empty(self): return (len(self.__sequence)==0)
    def polrep(self): return self.__polrep
    def scope(self): return self.__scope
    def punit(self): return self.__punit

    def oneliner(self):
        s = TDL_common.Super.oneliner(self)
        s = s+' punit='+str(self.punit())
        s = s+' polrep='+str(self.polrep())
        s = s+' len='+str(self.len())
        return s

    def display(self, txt=None, full=False):
        ss = TDL_common.Super.display (self, txt=txt, end=False)
        indent1 = 2*' '
        indent2 = 6*' '
        ss.append(indent1+' - Available Joneset sequence (.len() -> '+str(self.len())+' ):')
        for i in range(self.len()):
            ss.append(indent2+' - '+str(i)+' : '+self.__sequence[i].oneliner())
        return TDL_common.Super.display_end (self, ss)

    def append(self, Joneset=None):
        # Append a Joneset object to the internal sequence, after some checks:
        funcname = '.append():'
        jtype = Joneset.type()
        if not jtype=='Joneset':
            self.history(error=funcname+'not a Joneset, but'+jtype)
            return False

        # The Jonesets in the sequence should be consistent with each other: 
        if self.empty():
            # Collect information from the first one:
            self.__punit = Joneset.punit()
            self.__polrep = Joneset.polrep()
            self.__scope = Joneset.scope()
        else:
            # Compare with the info from the first one:
            if not Joneset.punit()==self.punit():
                self.history(error=funcname+'conflicting punit')
                return False
            if not Joneset.polrep()==self.polrep():
                self.history(error=funcname+'conflicting polrep')
                return False
            if not Joneset.scope()==self.scope():
                self.history(error=funcname+'conflicting scope')
                return False

        # OK, append to the internal sequence:
        self.__sequence.append(Joneset)
        self.history(str(self.len())+': '+funcname+Joneset.label())
        return self.len()


    def make_Joneset(self, ns):
        # Obtain a combined Joneset from the internal Joneset sequence:
        funcname = '.make_Joneset():'

        # Some checks:
        if not self.ok():
            self.history(error=funcname+'problems (not ok())')
            return False
        elif self.empty():
            self.history(error=funcname+'empty sequence')
            return False
        elif self.len()==1:
            # The internal sequence has only one member:
            self.__sequence[0].history('Extracted single item from: '+self.oneliner())
            return self.__sequence[0]              # just return the single one

        # The internal sequence has multiple Jonesets:
        # For each station (key), make a list cc[key] of input jones matrix nodes:
        keys = self.__sequence[0].keys()           # the stations (keys) of the first Joneset
        cc = dict() ;
        kwquals = dict()
        quals = dict()
        for key in keys:
            cc[key] = []
            kwquals[key] = dict()
            quals[key] = []
        punits = []
        labels = []
        for js in self.__sequence:                 # for all Jonesets in the sequence
            js_jones = js.jones()                  # get its set of jones matrices
            for key in keys:
                kwquals[key].update(js_jones[key].kwquals)
                quals[key].extend(list(js_jones[key].quals))
                cc[key].append(js_jones[key])
            punits.append(js.punit())              # should all be the same...!!            
            labels.append(js.label())           
            
        # Make new 2x2 jones matrices by matrix multiplication: 
        # Create a new Joneset
        newJoneset = Joneset(label=self.label(), punit=self.punit(),
                             polrep=self.polrep(), scope=self.scope())
        newJoneset.history('Matrix multiplication of: '+self.oneliner())
        for key in keys:
            newJoneset[key] = ns.JJones(**kwquals[key])(*quals[key]) << Meq.MatrixMultiply(children=cc[key])
        newJoneset.history('input sequence: '+str(labels))
        newJoneset.history('input punits (should be the same!): '+str(punits))

        # Update the parmgroup info from Joneset to Joneset:
        for js in self.sequence():
            newJoneset.update(js)

        return newJoneset




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
    if trace: print '** Joneset: _counters(',key,') =',_counters[key]
    return _counters[key]






#========================================================================
# Test routine:
#========================================================================

if __name__ == '__main__':
    from numarray import *
    from Timba.Contrib.JEN import MG_JEN_exec
    ns = NodeScope()
    nsim = ns.Subscope('_')
    
    # stations = range(3)
    js = Joneset(label='initial', polrep='circular')
    js.display('initial')

    if 0:
        print '** dir(js) ->',dir(js)
        print '** js.__doc__ ->',js.__doc__
        print '** js.__str__() ->',js.__str__()
        print '** js.__module__ ->',js.__module__
        print

    if 0:
        js.parmtable('xxx')

    if 0:
        js = Joneset(label='GJones', polrep='circular')
        p1 = js.register('Gphase', ipol=1, color='red', corrs=js.corrs_paral1())
        a2 = js.register('Gampl', ipol=2, color='blue', corrs=js.corrs_paral2())
        a1 = js.register('Gampl', ipol=1, color='blue', corrs=js.corrs_paral1())
        d12 = js.register('Ddang', color='blue', corrs=js.corrs_cross())
        d2 = js.register('Ddang', ipol=2, color='blue', corrs=js.corrs_cross())
        js.node_groups(['G','QQ'])
        js.node_groups(['G'])

        for station in range(14):
          js.MeqParm(reset=True)
          js.define_MeqParm(ns, p1, station=station, default=0)
          js.define_MeqParm(ns, a2, station=station, default=1)
          js.define_MeqParm(ns, a1, station=station, default=1)
          js.define_MeqParm(ns, d2, station=station, default=0)
          js.define_MeqParm(ns, d12, station=station, default=0)
          ss = js.MeqParm(update=True)
          js.append(station, '<jones_matrix for station '+str(station)+'>')

        js.define_solvegroup('p1_a2', [p1, a2])
        js.define_solvegroup('a1_a2', [a1, a2])
        js.define_solvegroup('all', js.parmgroup().keys())

    if 0:
        # Access to jones etc
        print
        print 'js.jones()[key]:'
        for key in js.keys(): print '-',key, js.jones()[key]
        print 'js[key]:'
        for key in js.keys(): print '-',key, js[key]
        print 'item in js:'
        for item in js: print '- item:',item
        print

    if 0:
        jones0 = ns << Meq.Constant(array([[11,12],[21,22]]), dim=[2,2])
        MG_JEN_exec.display_subtree(jones0, 'jones0', full=True)
        print '\n** jones0=',jones0
        print type(jones0),isinstance(jones0,type(ns<<0))
        js.nominal(ns, jones0)
        js.display('.nominal()')
        print '** .nodenames() -> (',len(js.nodenames()),'):',js.nodenames()
    
    if 0:
        Gjones = MG_JEN_Joneset.GJones (ns, stations=stations)
        Bjones = MG_JEN_Joneset.BJones (ns, stations=stations)

    if 0:
        # Joneseq object:
        jseq = Joneseq(label='initial')
        jseq.display('empty')
        jseq.append(js)
        jseq.append(js)
        jseq.append(js)
        jseq.display('filled')

    if 1:
        print js.parmtable('cal_BJones')
        print js.check_parmtable_extension()

    if 1:
        # Display the final result:
        # k = 0 ; MG_JEN_exec.display_subtree(js[k], 'js['+str(k)+']', full=True, recurse=3)
        js.display('final result')





#============================================================================================









 

