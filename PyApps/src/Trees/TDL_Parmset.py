# TDL_Parmset.py
#
# Author: J.E.Noordam
#
# Short description:
#    A Parmset object encapsulates group(s) of MeqParms
#
# History:
#    - 20 dec 2005: creation, from TDL_Joneset.py
#
# Full description:
#



#=================================================================================
# Preamble:
#=================================================================================

from Timba.TDL import *
from copy import deepcopy

from Timba.Trees import TDL_common
from Timba.Trees import TDL_radio_conventions




#=================================================================================
# Class Parmset
#=================================================================================


class Parmset (TDL_common.Super):
    """A Parmset object encapsulates a set of MeqParms"""

    def __init__(self, **pp):

        # Input arguments:
        pp.setdefault('scope', '<pscope>')           # used in visualisation etc
        pp.setdefault('punit', None)                 # punit (source/patch) ..............??
        pp.setdefault('unsolvable', False)           # if True, do NOT store parmgroup/solvegroup info
        pp.setdefault('parmtable', None)             # name of MeqParm table (AIPS++)

        self.__scope = pp['scope']
        self.__punit = pp['punit']
        self.__unsolvable = pp['unsolvable']
        self.__parmtable = pp['parmtable']
        self.check_parmtable_extension()

        TDL_common.Super.__init__(self, type='Parmset', **pp)


        self.clear()

        return None

    def clear(self):
        self.__parmgroup = dict()
        self.__solvegroup = dict()
        self.__condeq_corrs = dict()
        self.__plot_color = TDL_radio_conventions.plot_color()
        self.__plot_style = TDL_radio_conventions.plot_style()
        self.__plot_size = TDL_radio_conventions.plot_size()
        self.__MeqParm = dict()
        self.__constrain = dict()
        self.__node_groups = ['Parm']

    def register(self, key=None, **pp):
    # def register(self, key=None, ipol=None, color=None, style='circle', size=10, corrs=None):
        """Register a parameter (MeqParm) group"""

        pp.setdefault('color', None)
        pp.setdefault('style', 'circle')
        pp.setdefault('size', 10)
        
        self.__parmgroup[key] = []
        self.__plot_color[key] = pp['color']
        self.__plot_style[key] = pp['style']
        self.__plot_size[key] = pp['size']

        # Policy! Put them into Joneset.register()?
        # if isinstance(ipol, int): key = key+'_'+self.pols(ipol)     # append (X,Y,R,L) if requirec
        # if corrs=='*': corrs = self.corrs_all()
        # if corrs=='paral': corrs = self.corrs_paral()
        # if corrs=='paral1': corrs = self.corrs_paral1()
        # if corrs=='paral2': corrs = self.corrs_paral2()
        # if corrs=='cross': corrs = self.corrs_cross()
        # if self.corrs_all().__contains__(corrs): corrs = corrs      # single corr (e.g. 'RR')

        corrs = '<corrs>'
        if pp.has_key('corrs'): corrs = pp['corrs']                   # Policy!
        self.__condeq_corrs[key] = corrs

        s = 'Register parmgroup: '+key+': '+str(pp['color'])+' '+str(pp['style'])+' '+str(pp['size'])+' '+str(corrs)+' '
        self.history(s)
        self.define_solvegroup(key, parmgroup=[key])
        return key                                                  # return the actual key name


    def define_solvegroup(self, key=None, parmgroup=None):
      """Derive a new solvegroup by combining existing parmgroups:
      These are used when defining a solver downstream (see Cohset)"""
      trace = False
      if trace: print '\n** .define_solvegroup(',key,parmgroup,'):'

      # NB: This is inhibited if Parmset is set 'unsolvable' (e.g. for simulated uv-data) 
      if self.unsolvable(): return False

      if not isinstance(parmgroup, list): parmgroup = [parmgroup]
      self.__solvegroup[key] = parmgroup                            # list of existing parmgroup keys

      # Each solvegroup has a list of condeq_corrs, which allows the
      # solver to have only condeqs for the relevant corrs:
      corrs = []
      for pg in self.__solvegroup[key]:
          for corr in self.__condeq_corrs[pg]:
              if not corrs.__contains__(corr): corrs.append(corr)
              if trace: print '   pg=',pg,' corr=',corr,'   corrs=',corrs
      self.__condeq_corrs[key] = corrs
      return True


    def cleanup(self):
      """Remove empty parmgroups/solvegroups"""
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
        """Get/set node_groups (input for MeqParm definition)"""  
        if not new==None:
            if not isinstance(new, (tuple, list)): new = [new]
            for png in new:
                if not self.__node_groups.__contains__(png):
                    self.__node_groups.append(png)
        return self.__node_groups

    def define_MeqParm(self, ns, key=None, station=None,
                       default=0,
                       node_groups='Parm', constrain=False,
                       use_previous=True, tile_size=None):
        """Convenience function to create a MeqParm node"""
        # NB: If use_previous==True, the MeqParm will use its current funklet (if any)
        #     as starting point for the next snippet solution, unless a suitable funklet
        #     was found in the MeqParm table. If False, it will use the default funklet first.

        # If tile_size is specified (i.e. nonzero and not None), assume an integer.
        # This specifies the size (nr of cells) of the solution-tile in the time-direction.
        # This means that separate solutions are made for these tiles, which tile the domain.
        # Tiled solutions are efficient, because they reduce the node overhead
        # For the moment, only time-tiling is enabled...

        tiling = record()
        if tile_size:
            tiling.time = tile_size

        quals = dict(q=self.punit());
        if station:
            quals['s'] = station;
        node = ns[key](**quals) << Meq.Parm(default,
                                            node_groups=self.node_groups(),
                                            use_previous=use_previous,
                                            tiling=tiling,
                                            table_name=self.parmtable())

        # Put the node stub into the internal MeqParm buffer for later use:
        # See .MeqParm() below
        self.__MeqParm[key] = node
        self.__constrain[key] = constrain    # governs solution constraints.....
        return node


    def MeqParm(self, update=False, reset=False):
        """Get/update/reset the temporary helper record self.__MeqParm"""
        if update:
            # Append the accumulated MeqParm node names to their respective parmgroups:
            for key in self.__MeqParm.keys():
                if not self.__constrain[key]:
                    # If constrain=True, leave the MeqParm out of the parmgroup
                    # It will then NOT be included into the solvable MeqParms
                    nodename = self.__MeqParm[key].name
                    self.__parmgroup[key].append(nodename)
        if reset:
            # Always return self.__MeqParm as it was BEFORE reset:
            ss = self.__MeqParm                # return value
            # Reset the MeqParm buffer and related:
            self.__MeqParm = dict()
            self.__constrain = dict()
            return ss
        return self.__MeqParm


    # Access functions:
    def scope(self, new=None):
        if isinstance(new, str): self.__scope = new
        return self.__scope
    def punit(self): return self.__punit
    def unsolvable(self): return self.__unsolvable

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
    def parmgroup(self): return self.__parmgroup
    def solvegroup(self): return self.__solvegroup
    def plot_color(self): return self.__plot_color
    def plot_style(self): return self.__plot_style
    def plot_size(self): return self.__plot_size
            
    def oneliner(self):
        """Make a one-line summary of this Parmset object"""
        s = TDL_common.Super.oneliner(self)
        s += ' punit='+str(self.punit())
        s += ' '+str(self.node_groups())
        if self.unsolvable():
            s += ' unsolvable'
        else:
            s += ' parmtable='+str(self.parmtable())
        return s

    def display(self, txt=None, full=False):
        """Display a description of the contents of this Parmset object"""
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

        ss.append(indent1+' - solvegroups ( unsolvable = '+str(self.unsolvable())+' , node_groups = '+str(self.node_groups())+' ):')
        for key in self.solvegroup().keys():
            ss.append(indent2+' - '+key+' : parmgroups: '+str(self.solvegroup()[key])+' , corrs: '+str(self.condeq_corrs()[key]))
        return TDL_common.Super.display_end (self, ss)


    def update(self, Parmset=None):
        """Update the internal info from another Parmset object"""
        if Parmset==None: return False
        if self.unsolvable():
            self.history(append='not updated from (unsolvable): '+Parmset.oneliner())
        elif not Parmset.unsolvable():
            self.__parmgroup.update(Parmset.parmgroup())
            self.__solvegroup.update(Parmset.solvegroup())
            self.__condeq_corrs.update(Parmset.condeq_corrs())
            self.__plot_color.update(Parmset.plot_color())
            self.__plot_style.update(Parmset.plot_style())
            self.__plot_size.update(Parmset.plot_size())
            self.history(append='updated from (not unsolvable): '+Parmset.oneliner())
        else:
            # A Parmset that is 'unsolvable' has no solvegroups.
            # However, its parmgroups might interfere with parmgroups
            # of the same name (e.g. Gphase) from solvable Parmsets.
            # Therefore, its parm info should NOT be copied here.
            self.history(append='not updated from (unsolvable): '+Parmset.oneliner())
        return True




    def solvecorrs(self, solvegroup=None):
        """Collect a list of names of corrs to be used for solving"""
        corrs = []
        for sgname in solvegroup:
            if not self.solvegroup().has_key(sgname):
                print '\n** solvegroup name not recognised:',sgname
                print '     choose from:',self.solvegroup().keys()
                print
                return
            corrs.extend(self.condeq_corrs()[sgname])
        return corrs

    def solveparms(self, solvegroup=None, select='*'):
        """Collect a list of names of solvable MeqParms"""
        parms = []                                  # list of solvable node-names
        for sgname in solvegroup:
            if not self.solvegroup().has_key(sgname):
                print '\n** solvegroup name not recognised:',sgname
                print '     choose from:',self.solvegroup().keys()
                print
                return
            solvegroup = self.solvegroup()[sgname]  # list of one or more parmgroups
            for key in solvegroup:
                pgnames = self.parmgroup()[key]     # list of parmgroup node-names
                n = len(pgnames)
                if select=='first':                 # select the first of each parmgroup
                    parms.append(pgnames[0])        # append
                elif select=='last':                # select the last of each parmgroup
                    parms.append(pgnames[n-1])      # append
                else:
                    parms.extend(pgnames)           # append entire parmgroup
        # Return a list of solvable MeqParm names:
        return parms







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
    if trace: print '** Parmset: _counters(',key,') =',_counters[key]
    return _counters[key]






#========================================================================
# Test routine:
#========================================================================

if __name__ == '__main__':
    print '\n*******************\n** Local test of: TDL_Parmset.py:\n'
    from numarray import *
    from Timba.Trees import TDL_display
    # from Timba.Trees import JEN_record
    ns = NodeScope()
    nsim = ns.Subscope('_')
    
    # stations = range(3)
    ps = Parmset(label='initial', polrep='circular')
    ps.display('initial')

    if 0:
        print '** dir(ps) ->',dir(ps)
        print '** ps.__doc__ ->',ps.__doc__
        print '** ps.__str__() ->',ps.__str__()
        print '** ps.__module__ ->',ps.__module__
        print

    if 0:
        ps.parmtable('xxx')

    if 0:
        print ps.parmtable('cal_BJones')
        print ps.check_parmtable_extension()

    if 1:
        ps = Parmset(label='GJones', polrep='circular')
        p1 = ps.register('Gphase', ipol=1, color='red', corrs=['XX','YY'])
        a2 = ps.register('Gampl', ipol=2, color='blue', corrs=['XX','YY'])
        a1 = ps.register('Gampl', ipol=1, color='blue', corrs=['XX','YY'])
        d12 = ps.register('Ddang', color='blue', corrs=['XY','YX'])
        d2 = ps.register('Ddang', ipol=2, color='blue', corrs=['XY','YX'])

        ps.define_solvegroup('p1_a2', [p1, a2])
        ps.define_solvegroup('a1_a2', [a1, a2])
        ps.define_solvegroup('ALL', ps.parmgroup().keys())

        ps.node_groups(['G','QQ'])
        ps.node_groups(['G'])

        for station in range(14):
          ps.MeqParm(reset=True)
          ps.define_MeqParm(ns, p1, station=station, default=0)
          ps.define_MeqParm(ns, a2, station=station, default=1)
          ps.define_MeqParm(ns, a1, station=station, default=1)
          ps.define_MeqParm(ns, d2, station=station, default=0)
          ps.define_MeqParm(ns, d12, station=station, default=0)
          ss = ps.MeqParm(update=True)


    if 1:
        # Display the final result:
        # k = 0 ; TDL_display.subtree(ps[k], 'ps['+str(k)+']', full=True, recurse=3)
        ps.display('final result')

    print '\n*******************\n** End of local test of: TDL_Parmset.py:\n'




#============================================================================================









 

