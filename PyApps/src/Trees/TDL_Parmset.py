# TDL_Parmset.py
#
# Author: J.E.Noordam
#
# Short description:
#    A Parmset object encapsulates group(s) of MeqParms
#
# History:
#    - 20 dec 2005: creation, from TDL_Joneset.py
#    - 02 jan 2006: replaced the functions in TDL_Joneset.py (etc)
#
# Full description:
#   The (many) MeqParms of a Measurement Equation are usually solved in groups
#   (e.g. GJones phases for all stations, etc). The Parmset object provides a
#   convenient way to define and use such groups in various ways. 
#   A Joneset object contains a Parmset, which is used when solvers are defined.
#
#   A Parmset object contains the following main components:
#   - A list of named parmgroups, i.e. lists of MeqParm node names. 
#   - A list of named solvegroups, i.e. lists of one or more parmgroup names.
#
#   A Parmset object contains the following services:
#   - Creation of a named parmgroup, and addition of members.
#   - Definition of a new MeqParm node (with all its various options)
#     (this function may be used by itself too)
#   - Definition of a solvegroup as a list of parmgroup names
#   - Creation of MeqCondeq nodes for standard condition equations
#     (e.g. to equate the sum of the GJones phases to zero)
#   - A buffer to temporarily hold new MeqParms by their 'root' name
#     (this is useful where simular MeqParms are defined with different
#     qualifiers, e.g. for the different stations in a Joneset)
#   - etc


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
    """A Parmset object encapsulates an (arbitrary) set of MeqParm nodes"""

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
        self.__pg_rider = dict()
        self.__condeq = dict()
        self.__solvegroup = dict()
        self.__plot_color = TDL_radio_conventions.plot_color()
        self.__plot_style = TDL_radio_conventions.plot_style()
        self.__plot_size = TDL_radio_conventions.plot_size()
        self.__parm = dict()
        self.__buffer = dict()
        self.__constrain = dict()
        self.__node_groups = ['Parm']

    def scope(self, new=None):
        if isinstance(new, str): self.__scope = new
        return self.__scope
    def punit(self): return self.__punit
    def unsolvable(self): return self.__unsolvable

        
#--------------------------------------------------------------------------------
            
    def oneliner(self):
        """Make a one-line summary of this Parmset object"""
        s = TDL_common.Super.oneliner(self)
        s += ' punit='+str(self.punit())
        s += ' pg:'+str(len(self.parmgroup()))
        s += ' sg:'+str(len(self.solvegroup()))
        s += ' cq:'+str(len(self.condeq()))
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

        ss.append(indent1+' - parmgroup riders (pg_rider):')
        for key in self.parmgroup().keys():
            if len(self.pg_rider()[key])>0:
                ss.append(indent2+' - '+key+': '+str(self.pg_rider()[key]))
 
        ss.append(indent1+' - parmgroup condeq definitions:')
        for key in self.__condeq.keys():
            ss.append(indent2+' - '+key+': '+str(self.__condeq[key]))
 
        ss.append(indent1+' - unsolvable  = '+str(self.unsolvable()))
        ss.append(indent1+' - node_groups = '+str(self.node_groups()))
        ss.append(indent1+' - Defined solvegroups:')
        for key in self.solvegroup().keys():
            ss.append(indent2+' - '+key+' :  parmgroups: '+str(self.solvegroup()[key]))

        ss.append(indent1+' - Contents of temporary buffer:')
        for key in self.buffer().keys():
            ss.append(indent2+' - '+key+': '+str(self.buffer()[key]))

        ss.append(indent1+' - Available MeqParm nodes ( '+str(self.len())+' ):')
        if full or self.len()<10:
            for key in self.keys():
                ss.append(indent2+' - '+key+' : '+str(self.__parm[key]))
        else:
            keys = self.keys()
            n = len(keys)-1
            ss.append(indent2+' - first: '+keys[0]+' : '+str(self.__parm[keys[0]]))
            ss.append(indent2+'   ....')
            ss.append(indent2+' - last:  '+keys[n]+' : '+str(self.__parm[keys[n]]))
        return TDL_common.Super.display_end (self, ss)




#--------------------------------------------------------------------------------
# Functions related to MeqParm nodes: 
#--------------------------------------------------------------------------------

    def __getitem__(self, key):
        """Get a named (key) MeqParm node"""
        # This allows indexing by key and by index nr:
        if isinstance(key, int): key = self.__parm.keys()[key]
        return self.__parm[key]

    def __setitem__(self, key, value):
        """Set a named (key) MeqParm node"""
        self.__parm[key] = value
        return self.__parm[key]

    def parm(self): return self.__parm
    def len(self): return len(self.__parm)
    def keys(self): return self.__parm.keys()
    def has_key(self, key): return self.keys().__contains__(key)

    def node_groups(self, new=None):
        """Get/set node_groups (input for MeqParm definition)"""  
        if not new==None:
            if not isinstance(new, (tuple, list)): new = [new]
            for png in new:
                if not self.__node_groups.__contains__(png):
                    self.__node_groups.append(png)
        return self.__node_groups


    def parmtable(self, new=None):
        """Get/set the parmtable (MeqParm table) name""" 
        if isinstance(new, str):
            self.__parmtable = new
            self.check_parmtable_extension()
        return self.__parmtable

    def check_parmtable_extension(self):
        """Helper function for .parmtable()"""
        if isinstance(self.__parmtable, str):
            ss = self.__parmtable.split('.')
            if len(ss)==1: self.__parmtable += '.mep'
            return self.__parmtable.split('.')[1]
        return True


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

        quals = dict(q=self.punit())
        if station:
            quals['s'] = station
        node = ns[key](**quals) << Meq.Parm(default,
                                            node_groups=self.node_groups(),
                                            use_previous=use_previous,
                                            tiling=tiling,
                                            table_name=self.parmtable())

        # Put the node stub into the internal MeqParm buffer for later use:
        # See .buffer() below
        self.__buffer[key] = node
        self.__constrain[key] = constrain    # governs solution constraints.....
        return node

    def buffer(self, update=False, reset=False):
        """Get/update/reset the temporary helper record self.__buffer"""
        if update:
            # Append the accumulated MeqParm node names to their respective parmgroups:
            for key in self.__buffer.keys():
                if not self.__constrain[key]:
                    # If constrain=True, leave the MeqParm out of the parmgroup
                    # It will then NOT be included into the solvable MeqParms
                    nodename = self.__buffer[key].name
                    self.__parm[nodename] = self.__buffer[key]
                    self.__parmgroup[key].append(nodename)
        if reset:
            # Always return self.__buffer as it was BEFORE reset:
            ss = self.__buffer                # return value
            # Reset the buffer and related:
            self.__buffer = dict()
            self.__constrain = dict()
            return ss
        return self.__buffer




#--------------------------------------------------------------------------------
# Functions related to parmgroups:
#--------------------------------------------------------------------------------

    def parmgroup (self, key=None):
        """Get the named (key) parmgroup"""
        if key==None:
            return self.__parmgroup
        if self.__parmgroup.has_key(key):
            return self.__parmgroup[key]
        print '\n** parmgroup name not recognised:',sgname
        print '     choose from:',self.parmgroup().keys(),'\n'
        return None

    def pg_rider(self): return self.__pg_rider
    def plot_color(self): return self.__plot_color
    def plot_style(self): return self.__plot_style
    def plot_size(self): return self.__plot_size


    def register(self, key=None, **pp):
        # def register(self, key=None, ipol=None, color=None, style='circle', size=10, corrs=None):
        """Register a parameter (MeqParm) group"""

        pp.setdefault('color', None)        # plot color
        pp.setdefault('style', 'circle')    # plot style
        pp.setdefault('size', 10)           # size of plotted symbol
        pp.setdefault('rider', dict())      # optional: record with named extra information
        
        self.__parmgroup[key] = []
        self.__pg_rider[key] = pp['rider']
        self.__plot_color[key] = pp['color']
        self.__plot_style[key] = pp['style']
        self.__plot_size[key] = pp['size']

        self.history('** Register parmgroup: '+key+':   '+str(pp))
        self.define_solvegroup(key, parmgroup=[key])
        return key                                                  # return the actual key name

    def parm_names(self, parmgroup=None, select='*', trace=False):
        """Return a list of parmgroup MeqParm node names"""
        if trace: print '\n** .parm_names(',parmgroup,select,'):'
        node_names = self.parmgroup(parmgroup) # list of MeqParm node-names
        parms = []
        n = len(node_names)
        if select=='first':                 # select the first of each parmgroup
            parms.append(node_names[0])     # append a single node name
        elif select=='last':                # select the last of each parmgroup
            parms.append(node_names[n-1])   # append a single node name
        else:
            parms.extend(node_names)        # append entire parmgroup
        # Return a list of solvable MeqParm node names:
        if trace: print '  ->',len(parms),':',parms,'\n'
        return parms


    def parm_nodes(self, parmgroup=None, select='*', trace=False):
        """Return a list of parmgroup MeqParm nodes"""
        if trace: print '\n** .parm_nodes(',parmgroup,select,'):'
        node_names = self.parm_names(parmgroup=parmgroup, select=select, trace=False)
        if not isinstance(node_names, list): return False
        nodes = []
        for name in node_names:
            nodes.append(self.__parm[name])
        # Return a list of solvable MeqParm nodes:
        if trace: print '  ->',len(nodes),':',nodes,'\n'
        return nodes

#--------------------------------------------------------------------------------
# Functions related to condeqs:
#--------------------------------------------------------------------------------

    def define_condeq(self, parmgroup=None, unop='Add', value=0.0, select='*', trace=True):
        """Provide information for named (key) condeq equations"""
        if not self.__parmgroup.has_key(parmgroup):
            print '\n** parmgroup not recognised in:',self.__parmgroup.keys(),'\n'
            return False
        # Make the name (key) of the condeq defnition:
        key = parmgroup
        if select=='first':
            key += '_first'
            if unop=='Add': unop = None
            if unop=='Multiply': unop = None
        elif select=='last':
            key += '_last'
            if unop=='Add': unop = None
            if unop=='Multiply': unop = None
        elif unop=='Add':
            key += '_sum'
        elif unop=='Multiply':
            key += '_prod'
            if value==0: value = 1.0
        key += '='+str(value)
        if self.__condeq.has_key(key): key += '_2'
        if self.__condeq.has_key(key): key += '_2'
        if self.__condeq.has_key(key): key += '_2'
        # Look ahead to the possibility of a unop sequence:
        if unop:
            if not isinstance(unop,(list,tuple)): unop = [unop]
        # Make the dict that defines the condition equation (see .condeq())
        self.__condeq[key] = dict(parmgroup=parmgroup, select=select, unop=unop, value=value)
        if trace: print '\n** .define_condeq(',key,'):',self.__condeq[key],'\n'
        return key

 
    def condeq(self, key=None):
       """Access to condeq definitions"""
       if not key: return self.__condeq
       if self.__condeq.has_key(key):
           return self.__condeq[key]
       return False
   
        
    def make_condeq(self, ns=None, key=None):
       """Make a condeq node, using the specified (key) condeq definition"""
       funcname = '::make_condeq()'
       if not self.__condeq.has_key(key):
           return False
       rr = self.condeq(key)
       nodes = self.parm_nodes(rr['parmgroup'], select=rr['select'])
       uniqual = _counter(funcname, increment=-1)
       node = nodes[0]
       if rr['unop']:
           unop = rr['unop'][0]                    # for the moment
           if unop in ['Add','Multiply']:
               name = key.split('=')[0]
               node = ns[name](uniqual) << getattr(Meq, unop)(children=nodes)
       condeq = ns['Condeq_'+key](uniqual) << Meq.Condeq(node, rr['value'])
       return condeq

#--------------------------------------------------------------------------------
# Functions related to solvegroups:
#--------------------------------------------------------------------------------

    def define_solvegroup(self, key=None, parmgroup=None):
      """Derive a new solvegroup by combining existing parmgroups:
      These are used when defining a solver downstream (see Cohset)."""
      trace = False
      if trace: print '\n** .define_solvegroup(',key,parmgroup,'):'
      if parmgroup==None: return False                              # error?

      # NB: This is inhibited if Parmset is set 'unsolvable' (e.g. for simulated uv-data) 
      if self.unsolvable(): return False

      if not isinstance(parmgroup, list): parmgroup = [parmgroup]   
      self.__solvegroup[key] = parmgroup                            # list of existing parmgroup keys
      return True


    def solvegroup (self, key=None):
        """Get the named (key) solvegroup"""
        if key==None:
            return self.__solvegroup
        if self.__solvegroup.has_key(key):
            return self.__solvegroup[key]
        print '\n** solvegroup name not recognised:',sgname
        print '     choose from:',self.solvegroup().keys(),'\n'
        return None

#--------------------------------------------------------------------------------

    def sg_rider(self, solvegroup=None, key=None, trace=False):
        """Collect (merge) the specified (key) rider info for the specified solvegroup(s)"""
        if not isinstance(solvegroup, (list, tuple)): solvegroup = [solvegroup]
        if trace: print '\n** .sg_rider(',solvegroup,key,'):'
        cc = []                                     # assume list items(...!!?) 
        for sgname in solvegroup:                   # solvegroup may be multiple
            sg = self.solvegroup(sgname)
            if not sg: return False                 # solvegroup not found
            for pgname in sg:                       # parmgroup name
                pg_rider = self.pg_rider()[pgname]  # parmgroup rider dict
                if not pg_rider.has_key(key): return False
                items = pg_rider[key]               # assume that items is a list...!!?
                if not isinstance(items,(list,tuple)): items = [items]
                for item in items:
                    if not item in cc: cc.append(item)  # merge into unique list.....!!?
        # Return a merged list of unique items of the 
        if trace: print '  ->',len(cc),':',cc,'\n'
        return cc

    def solveparm_names(self, solvegroup=None, select='*', trace=False):
        """Collect a list of (names of) solvable MeqParms"""
        if not isinstance(solvegroup, (list, tuple)): solvegroup = [solvegroup]
        if trace: print '\n** .solveparm_names(',solvegroup,select,'):'
        parms = []                                  # list of solvable node-names
        for sgname in solvegroup:                   # solvegroup may be multiple
            sg = self.solvegroup(sgname)
            if not sg: return False                 # solvegroup not found
            for pgname in sg:                       # parmgroup name
                node_names = self.parmgroup(pgname) # list of MeqParm node-names
                n = len(node_names)
                if select=='first':                 # select the first of each parmgroup
                    parms.append(node_names[0])     # append a single node name
                elif select=='last':                # select the last of each parmgroup
                    parms.append(node_names[n-1])   # append a single node name
                else:
                    parms.extend(node_names)        # append entire parmgroup
        # Return a list of solvable MeqParm node names:
        if trace: print '  ->',len(parms),':',parms,'\n'
        return parms


    def solveparm_nodes(self, solvegroup=None, select='*', trace=False):
        if trace: print '\n** .solveparm_nodes(',solvegroup,select,'):'
        names = self.solveparm_names(solvegroup=solvegroup, select=select, trace=False)
        if not isinstance(names, list): return False
        nodes = []
        for name in names:
            nodes.append(self.__parm[name])
        # Return a list of solvable MeqParm nodes:
        if trace: print '  ->',len(nodes),':',nodes,'\n'
        return nodes


#---------------------------------------------------------------------------

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
      return True


    def update(self, Parmset=None):
        """Update the solvegroup/parmgroup info from another Parmset object"""
        if Parmset==None: return False
        if self.unsolvable():
            self.history(append='not updated from (unsolvable): '+Parmset.oneliner())
        elif not Parmset.unsolvable():
            self.__parmgroup.update(Parmset.parmgroup())
            self.__pg_rider.update(Parmset.pg_rider())
            self.__solvegroup.update(Parmset.solvegroup())
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
    from Timba.Trees import TDL_Joneset
    from Timba.Contrib.JEN import MG_JEN_funklet
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

    if 0:
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
          ps.buffer(reset=True)
          ps.define_MeqParm(ns, p1, station=station, default=0)
          ps.define_MeqParm(ns, a2, station=station, default=1)
          ps.define_MeqParm(ns, a1, station=station, default=1)
          ps.define_MeqParm(ns, d2, station=station, default=0)
          ps.define_MeqParm(ns, d12, station=station, default=0)
          ss = ps.buffer(update=True)


    if 1:
        # Create a Joneset object
        pp = dict(stations=range(3), c00_Gampl=1.0, c00_Gphase=0.0, Gphase_constrain=True)
        js = TDL_Joneset.Joneset(label='test', **pp)
        js.display()
        js.Parmset.display()
    
    if 1:
        # Register the parmgroups:
        a1 = js.register('Gampl', ipol=1, color='red', style='diamond', size=10, corrs='paral1')
        a2 = js.register('Gampl', ipol=2, color='blue', style='diamond', size=10, corrs='paral2')
        p1 = js.register('Gphase', ipol=1, color='magenta', style='diamond', size=10, corrs='paral1')
        p2 = js.register('Gphase', ipol=2, color='cyan', style='diamond', size=10, corrs='paral2')

        # MeqParm node_groups: add 'G' to default 'Parm':
        js.Parmset.node_groups('G')

        # Define extra solvegroup(s) from combinations of parmgroups:
        js.Parmset.define_solvegroup('GJones', [a1, p1, a2, p2])
        js.Parmset.define_solvegroup('Gpol1', [a1, p1])
        js.Parmset.define_solvegroup('Gpol2', [a2, p2])
        js.Parmset.define_solvegroup('Gampl', [a1, a2])
        js.Parmset.define_solvegroup('Gphase', [p1, p2])
    
        first_station = True
        for station in pp['stations']:
            skey = TDL_radio_conventions.station_key(station)        
            # Define station MeqParms (in ss), and do some book-keeping:  
            js.Parmset.buffer(reset=True)
            
            for Gampl in [a1,a2]:
                default = MG_JEN_funklet.polc_ft (c00=pp['c00_Gampl'])
                js.Parmset.define_MeqParm (ns, Gampl, station=skey, default=default)

            for Gphase in [p1,p2]:
                default = MG_JEN_funklet.polc_ft (c00=pp['c00_Gphase'])
                constrain = False
                if pp['Gphase_constrain']: 
                    if first_station: constrain = True
                js.Parmset.define_MeqParm (ns, Gphase, station=skey, default=default,
                                           constrain=constrain)

            ss = js.Parmset.buffer(update=True)        # use ss[p1] etc...
            first_station = False
        ps = js.Parmset
        ps.define_condeq(p1, unop='Add', value=0.0)
        ps.define_condeq(p2, unop='Add', value=0.0)
        ps.define_condeq(p1, select='first', value=0.0)
        ps.define_condeq(a1, unop='Multiply', value=1.0)
        ps.define_condeq(a2, unop='Multiply', value=1.0)
        ps.display()

    if 1:
        for key in ps.condeq().keys():
            condeq = ps.make_condeq(ns, key)
            TDL_display.subtree(condeq, key, full=True, recurse=5)

    if 0:
        print
        for key in ps.parmgroup().keys():
            print '- parmgroup:',key,':',ps.parmgroup(key)
        print

    if 0:
        print
        for key in ps.solvegroup().keys():
            print '- solvegroup:',key,':',ps.solvegroup(key)
        print

    if 0:
        print
        for sg in ps.solvegroup().keys():
            ps.sg_rider(sg, key='condeq_corrs', trace=True)
        print

    if 0:
        select = '*'
        # select = 'first'
        # select = 'last'
        for key in ps.solvegroup().keys():
            ps.solveparm_names(key, select=select, trace=True)
            ps.solveparm_nodes(key, select=select, trace=True)
        print
        
    if 0:
        select = '*'
        # select = 'first'
        select = 'last'
        for key in ps.parmgroup().keys():
            ps.parm_names(key, select=select, trace=True)
            ps.parm_nodes(key, select=select, trace=True)
        print
        

    if 0:
        # Display the final result:
        # k = 0 ; TDL_display.subtree(ps[k], 'ps['+str(k)+']', full=True, recurse=3)
        ps.display('final result')

    print '\n*******************\n** End of local test of: TDL_Parmset.py:\n'




#============================================================================================









 

