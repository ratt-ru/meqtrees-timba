# TDL_Leafset.py
#
# Author: J.E.Noordam
#
# Short description:
#    A Leafset object encapsulates group(s) of leaf nodes
#
# History:
#    - 24 feb 2006: creation, starting from TDL_Parmset.py
#
# Full description:
#   Leaf nodes have no children. They have their own ways to satisfy requests.
#   Examples are MeqParm, MeqConstant, MeqFreq, MeqSpigot, MeqDetector, etc
#   Leaf nodes may be used for providing simulated values for MeqParms.
#   The Leafset object has methods to make that simpler to implement.
#   For this reason, a Leafset is closely modelled on the Parmset.
#   But a Leafset may be used for other things as well.
#
#   A Leafset object contains the following main components:
#   - A list of named leafgroups, i.e. lists of MeqParm node names. 
#
#   A Leafset object contains the following services:
#   - Creation of a named leafgroup, and addition of members.
#   - Definition of a new MeqLeaf node (with all its various options)
#     (this function may be used by itself too)
#   - A buffer to temporarily hold new MeqLeafs by their 'root' name
#     (this is useful where simular MeqLeafs are defined with different
#     qualifiers, e.g. for the different stations in a Joneset)
#   - etc


#=================================================================================
# Preamble:
#=================================================================================

from Timba.TDL import *

from copy import deepcopy
from random import *
from math import *
from numarray import *

from Timba.Trees import TDL_common
from Timba.Trees import TDL_radio_conventions
from Timba.Trees import JEN_inarg
from Timba.Trees import TDL_Leaf




#=================================================================================
# Class Leafset
#=================================================================================


class Leafset (TDL_common.Super):
    """A Leafset object encapsulates an (arbitrary) set of MeqLeaf nodes"""

    def __init__(self, **pp):

        # Input arguments:

        TDL_common.Super.__init__(self, type='Leafset', **pp)

        self.clear()
        return None



    def clear(self):
        """Clear the object"""
        self.__quals = dict()                        # record of default node-name qualifiers
        self.__leafgroup = dict()
        self.__default_value = dict()
        self.__plot_color = TDL_radio_conventions.plot_color()
        self.__plot_style = TDL_radio_conventions.plot_style()
        self.__plot_size = TDL_radio_conventions.plot_size()
        self.__MeqLeaf = dict()
        self.__buffer = dict()

    def quals(self, new=None, clear=False):
        """Get/set the default MeqLeaf node-name qualifier(s)"""
        if clear:
            self.__quals = dict()
        if isinstance(new, dict):
            for key in new.keys():
                self.__quals[key] = str(new[key])
        return self.__quals
        
    def buffer(self):
        """Get the temporary helper record self.__buffer"""
        return self.__buffer

    #--------------------------------------------------------------------------------
            
    def oneliner(self):
        """Make a one-line summary of this Leafset object"""
        s = TDL_common.Super.oneliner(self)
        # if len(self.quals())>0:
        s += ' quals='+str(self.quals())
        s += ' pg:'+str(len(self.leafgroup()))
        return s


    def display(self, txt=None, full=False):
        """Display a description of the contents of this Leafset object"""
        ss = TDL_common.Super.display (self, txt=txt, end=False)
        indent1 = 2*' '
        indent2 = 6*' '
 
        ss.append(indent1+' - Registered leafgroups ('+str(len(self.leafgroup()))+'):')
        for key in self.leafgroup().keys():
          pgk = self.leafgroup()[key]
          n = len(pgk)
          if full or n<3:
            ss.append(indent2+' - '+key+' ( '+str(n)+' ): '+str(pgk))
          else:
            ss.append(indent2+' - '+key+' ( '+str(n)+' ): '+pgk[0]+' ... '+pgk[n-1])

        if full:
            ss.append(indent1+' - Contents of temporary buffer:')
            for key in self.buffer().keys():
                ss.append(indent2+' - '+key+': '+str(self.buffer()[key]))

        ss.append(indent1+' - Available MeqLeaf nodes ( '+str(self.len())+' ):')
        if full or self.len()<10:
            for key in self.keys():
                ss.append(indent2+' - '+key+' : '+str(self.__MeqLeaf[key]))
        else:
            keys = self.keys()
            n = len(keys)-1
            ss.append(indent2+' - first: '+keys[0]+' : '+str(self.__MeqLeaf[keys[0]]))
            ss.append(indent2+'   ....')
            ss.append(indent2+' - last:  '+keys[n]+' : '+str(self.__MeqLeaf[keys[n]]))
        return TDL_common.Super.display_end (self, ss)




#--------------------------------------------------------------------------------
# Functions related to MeqLeaf nodes: 
#--------------------------------------------------------------------------------

    def __getitem__(self, key):
        """Get a named (key) MeqLeaf node"""
        # This allows indexing by key and by index nr:
        if isinstance(key, int): key = self.__MeqLeaf.keys()[key]
        return self.__MeqLeaf[key]

    def __setitem__(self, key, value):
        """Set a named (key) MeqLeaf node"""
        self.__MeqLeaf[key] = value
        return self.__MeqLeaf[key]

    def MeqLeaf(self):
        """The list of MeqLeaf nodes"""
        return self.__MeqLeaf
    def len(self):
        """The number of MeqLeaf nodes in MeqLeaf"""
        return len(self.__MeqLeaf)
    def keys(self):
        """The list of MeqLeaf keys (names)"""
        return self.__MeqLeaf.keys()
    def has_key(self, key):
        """Test whether MeqLeaf contains an item with the specified key"""
        return self.keys().__contains__(key)


    #-------------------------------------------------------------------------------------
    # MeqLeaf definition:
    #-------------------------------------------------------------------------------------

    def inarg (self, pp, **kwargs):
        """Definition of Leafset input arguments (see e.g. MG_JEN_Joneset.py)"""
        kwargs.setdefault('mean_tampl', 0.1)
        kwargs.setdefault('stddev_tampl', 0.01)
        kwargs.setdefault('mean_period_s', 100)
        kwargs.setdefault('stddev_period_s', 10)
        JEN_inarg.define(pp, 'mean_tampl', kwargs,
                         choice=[0,0.001,0.01,0.1,1,10],  
                         help='mean amplitude of the time-variation')
        JEN_inarg.define(pp, 'stddev_tampl', kwargs,
                         choice=[0,0.0001,0.001,0.01,0.1,1],  
                         help='scatter of the tvar amplitude')
        JEN_inarg.define(pp, 'mean_period_s', kwargs,
                         choice=[10,20,50,100,200,500,1000],  
                         help='mean period (s) of the time-variation')
        JEN_inarg.define(pp, 'stddev_period_s', kwargs,
                         choice=[10,20,50,100],  
                         help='scatter (s) of the tvar period')
        JEN_inarg.define(pp, 'unop', 'Cos', hide=False,
                         choice=['Cos','Sin',['Cos','Sin'],None],  
                         help='time-variability function(s)')
        return True

    #------------------------------------------------------------------------

    def define_MeqLeaf(self, ns, key=None, qual=None,
                       leafgroup=None, default=None, **pp):
        """Convenience function to create a MeqLeaf node"""
        
        # The node-name qualifiers are the superset of the default ones
        # and the ones specified in this function call:
        quals = deepcopy(self.quals())
        if isinstance(qual, dict):
            for qkey in qual.keys():
                quals[qkey] = str(qual[qkey])

        # Start with the default value for this leafgroup:
        if leafgroup==None:
            leafgroup = key
        if default==None:
            default = self.__default_value[leafgroup]
        aa = []
        aa.append(ns['default'](leafgroup)(value=str(default)) << Meq.Constant(default))


        # Make the (additive) time-variation function:
        # For the moment: A cos(MeqTime) with a certain period
        # uniqual = _counter (leafgroup, increment=True)
        mm = []
        T_sec = ceil(gauss(pp['mean_period_s'], pp['stddev_period_s']))
        if T_sec<10: T_sec = 10
        mm.append(ns['2pi/T'](leafgroup)(**quals)(T=str(T_sec)+'sec') << Meq.Constant(T_sec))
        mm.append(ns['MeqTime'](leafgroup)(**quals) << Meq.Time())
        node = ns['targ'](leafgroup)(**quals) << Meq.Multiply(children=mm)

        mm = []
        mm.append(ns << Meq.Cos(node))
        ampl = gauss(pp['mean_tampl'], pp['stddev_tampl'])
        if ampl<0: ampl = 0
        mm.append(ns['tampl'](leafgroup)(**quals)(ampl=str(ampl)) << Meq.Constant(ampl))
        aa.append(ns['tvar'](leafgroup)(**quals) << Meq.Multiply(children=mm))

        # Combine the various components into a leaf with the desired name:
        node = ns[key](**quals) << Meq.Add(children=aa)

        # Store the new node:
        nodename = node.name
        self.__MeqLeaf[nodename] = node                 # record of named nodes 
        self.__leafgroup[leafgroup].append(nodename)    # 
        # print '\n** MeqLeaf[',nodename,'] ->',node 

        # Put the node stub into the internal MeqLeaf buffer for later use:
        # This buffer is a service that allows access to the most recently
        # defined MeqLeafs by means of their leafgroup name, rather than
        # their full name:
        self.__buffer[leafgroup] = node
        return node



#--------------------------------------------------------------------------------
# Functions related to leafgroups:
#--------------------------------------------------------------------------------


    def leafgroup (self, key=None, **pp):
        """Get/create the named (key) leafgroup"""
        if key==None:                       # no leafgroup specified
            return self.__leafgroup         #   return the entire record
        elif self.__leafgroup.has_key(key): # leafgroup already exists
            return self.__leafgroup[key]    #   return it
        else:
            # Leafgroup does not exist yet: Create it:
            pp.setdefault('color', 'red')       # plot color
            pp.setdefault('style', 'triangle')  # plot style
            pp.setdefault('size', 5)            # size of plotted symbol
            pp.setdefault('default', 1.0)       # default value of this leafgroup 
            pp.setdefault('rider', dict())      # optional: record with named extra information
            self.__leafgroup[key] = []
            self.__default_value[key] = pp['default']
            self.__plot_color[key] = pp['color']
            self.__plot_style[key] = pp['style']
            self.__plot_size[key] = pp['size']
            qq = TDL_common.unclutter_inarg(pp)
            self.history('** Created leafgroup: '+key+':   '+str(qq))
            return key                          # return the actual key name


    def plot_color(self): return self.__plot_color
    def plot_style(self): return self.__plot_style
    def plot_size(self): return self.__plot_size
    def default_value(self): return self.__default_value


    def leaf_names(self, leafgroup=None, select='*', trace=False):
        """Return a list of leafgroup MeqLeaf node names"""
        if trace: print '\n** .leaf_names(',leafgroup,select,'):'
        node_names = self.leafgroup(leafgroup) # list of MeqLeaf node-names
        leafs = []
        n = len(node_names)
        if n==0:
            pass
        elif select=='first':               # select the first of each leafgroup
            leafs.append(node_names[0])     # append a single node name
        elif select=='last':                # select the last of each leafgroup
            leafs.append(node_names[n-1])   # append a single node name
        else:
            leafs.extend(node_names)        # append entire leafgroup
        if trace: print '  ->',len(leafs),':',leafs,'\n'
        return leafs


    def leaf_nodes(self, leafgroup=None, select='*', trace=False):
        """Return a list of leafgroup MeqLeaf nodes"""
        trace = True
        if trace: print '\n** .leaf_nodes(',leafgroup,select,'):'
        node_names = self.leaf_names(leafgroup=leafgroup, select=select, trace=True)
        if not isinstance(node_names, list): return False
        nodes = []
        for name in node_names:
            print '- leaf_nodes():',name,self.__MeqLeaf.has_key(name)
            nodes.append(self.__MeqLeaf[name])
        # Return a list of solvable MeqLeaf nodes:
        if trace: print '  ->',len(nodes),':',nodes,'\n'
        return nodes



#---------------------------------------------------------------------------

    def cleanup(self):
      """Remove empty leafgroups"""
      removed = []
      for key in self.__leafgroup.keys():
        if len(self.__leafgroup[key])==0:
          self.__leafgroup.__delitem__(key)
          removed.append(key)
      self.history ('.cleanup(): removed leafgroup(s): '+str(removed))
      return True


    def update(self, Leafset=None):
        """Update the leafgroup info from another Leafset object"""
        if Leafset==None: return False

        # NB: update OVERWRITES existing fields with new versions!
        print 'Leafset.update(): self.__leafgroup:\n    ',self.__leafgroup
        if True:
            self.__leafgroup.update(Leafset.leafgroup())
            print '    ',self.__leafgroup,'\n'    
        self.__MeqLeaf.update(Leafset.MeqLeaf())
        self.__plot_color.update(Leafset.plot_color())
        self.__plot_style.update(Leafset.plot_style())
        self.__plot_size.update(Leafset.plot_size())
        self.__default_value.update(Leafset.default_value())
        self.history(append='updated from (not unsolvable): '+Leafset.oneliner())
        return True


 



#===========================================================================================
#===========================================================================================
#===========================================================================================
#===========================================================================================




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
    if trace: print '** Leafset: _counters(',key,') =',_counters[key]
    return _counters[key]






#========================================================================
# Test routine:
#========================================================================

if __name__ == '__main__':
    print '\n*******************\n** Local test of: TDL_Leafset.py:\n'
    from numarray import *
    from Timba.Trees import TDL_display
    from Timba.Trees import TDL_Joneset
    from Timba.Contrib.JEN import MG_JEN_funklet
    # from Timba.Trees import JEN_record
    ns = NodeScope()
    nsim = ns.Subscope('_')
    
    # stations = range(3)
    ls = Leafset(label='initial')
    ls.display('initial')

    if 0:
        print '** dir(ps) ->',dir(ps)
        print '** ls.__doc__ ->',ls.__doc__
        print '** ls.__str__() ->',ls.__str__()
        print '** ls.__module__ ->',ls.__module__
        print


    if 1:
        # Create a Joneset object
        pp = dict(stations=range(3), c00_Gampl=1.0, c00_Gphase=0.0)
        js = TDL_Joneset.Joneset(label='test', **pp)
        # js.display()
        # js.Parmset.display()
        # js.Leafset.display()
    
    if 0:
        # Register the leafgroups:
        a1 = js.parmgroup('Gampl', ipol=1, color='red', style='diamond', size=10, corrs='paral1', stddev=1.2)
        a2 = js.parmgroup('Gampl', ipol=2, color='blue', style='diamond', size=10, corrs='paral2')
        p1 = js.parmgroup('Gphase', ipol=1, color='magenta', style='diamond', size=10, corrs='paral1')
        p2 = js.parmgroup('Gphase', ipol=2, color='cyan', style='diamond', size=10, corrs='paral2')

        for station in pp['stations']:
            skey = TDL_radio_conventions.station_key(station)        
            # Define station MeqLeafs (in ss), and do some book-keeping:  
            qual = dict(s=skey)
            for Gampl in [a1,a2]:
                default = MG_JEN_funklet.polc_ft (c00=pp['c00_Gampl'])
                # js.Leafset.define_MeqLeaf (ns, Gampl, qual=qual, default=default)

            for Gphase in [p1,p2]:
                default = MG_JEN_funklet.polc_ft (c00=pp['c00_Gphase'])
                # js.Leafset.define_MeqLeaf (ns, Gphase, qual=qual, default=default)

        ps = js.Parmset
        ps.display(full=True)
        ls = js.Leafset
        ls.display(full=True)

    if 0:
        print
        for key in ls.leafgroup().keys():
            print '- leafgroup:',key,':',ls.leafgroup(key)
        print

    if 0:
        select = '*'
        # select = 'first'
        select = 'last'
        for key in ls.leafgroup().keys():
            ls.leaf_names(key, select=select, trace=True)
            ls.leaf_nodes(key, select=select, trace=True)
        print
        

    if 0:
        # Display the final result:
        # k = 0 ; TDL_display.subtree(ps[k], 'ps['+str(k)+']', full=True, recurse=3)
        ls.display('final result')

    print '\n*******************\n** End of local test of: TDL_Leafset.py:\n'




#============================================================================================

# .leafgroup():
# - register with:
#   - color, style,etc
#   - stddev,mean
# - do via Joneset object (contains Parmset and Leafset)
#   - minimum change in .GJones()

# leaf functions:
# - a*cos((2pi/T)(t-t0)+phi)
# - a,t0,T,phi can be lists: causes combination of cos-functions
#                            with different parameters
# - combine='Add' (allow 'Multiply')
# - unop='Cos' (allow 'Sin' etc)
# - how to deal with freq?
 
# .inarg_overall(pp)
# - insert into function preamble if function argument simul=True
# - this attaches arguments to the function inarg (not nested)

# .compare(Parmset)
# - looks for Parmset nodes with the same name
# - makes comparison (subtract/divide) subtrees

# individual treatment of a particular MeqLeaf?
# - later (should be trivial if well-designed)



#============================================================================================









 

