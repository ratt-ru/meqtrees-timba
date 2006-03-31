# TDL_LeafSet.py
#
# Author: J.E.Noordam
#
# Short description:
#    A LeafSet object encapsulates group(s) of 'leaf' nodes
#
# History:
#    - 24 feb 2006: creation, starting from TDL_Parmset.py
#    - 09 mar 2006: recreated from TDL_ParmSet.py
#    - 31 mar 2006: added MeqLeaf(init_funklet=...)
#
# Full description:
#   A LeafSet contains 'leaf' nodes in named groups.
#   Leaf nodes may be used for providing simulated values for MeqParms.
#   The LeafSet object has methods to make that simpler to implement.
#   For this reason, a LeafSet is closely modelled on the Parmset.
#   But a LeafSet may be used for other things as well.
#
#   A LeafSet object contains the following main components:
#   - A NodeSet object to adminster its groups/gogs of MeqLeaf nodes.
#
#   A LeafSet object contains the following services:
#   - Creation of a named leafgroup, and addition of members.
#   - Definition of a new MeqLeaf node (with all its various options)
#     (this function may be used by itself too)



#=================================================================================
# Preamble:
#=================================================================================

from Timba.TDL import *

from copy import deepcopy
from random import *
from math import *
from numarray import *

from Timba.Trees import TDL_common
from Timba.Trees import TDL_NodeSet
from Timba.Trees import JEN_inarg




#=================================================================================
# Class LeafSet
#=================================================================================


class LeafSet (TDL_common.Super):
    """A LeafSet object encapsulates an (arbitrary) set of MeqParm nodes"""

    def __init__(self, **pp):

        # Input arguments:

        TDL_common.Super.__init__(self, type='LeafSet', **pp)

        # Define its NodeSet object:
        self.NodeSet = TDL_NodeSet.NodeSet(label=self.tlabel())
        # self.NodeSet = TDL_NodeSet.NodeSet(label=self.label(), **pp)

        self.clear()
        return None


    def clear(self):
        """Clear the LeafSet object"""
        self.NodeSet.clear()
        self.NodeSet.radio_conventions()


    #--------------------------------------------------------------------------------
    # Some overall quantities:
    #--------------------------------------------------------------------------------


    def quals(self, new=None, clear=False):
        """Get/set the default MeqParm node-name qualifier(s)"""
        return self.NodeSet.quals(new=new, clear=clear)
        
    def buffer(self, clear=False):
        """Get the temporary helper record self.__buffer"""
        return self.NodeSet.buffer(clear=clear)

    #--------------------------------------------------------------------------------
            
    def oneliner(self):
        """Make a one-line summary of this LeafSet object"""
        s = TDL_common.Super.oneliner(self)
        s += ' quals='+str(self.quals())
        s += ' lg:'+str(len(self.leafgroup()))
        return s


    def display(self, txt=None, full=False):
        """Display a description of the contents of this LeafSet object"""
        ss = TDL_common.Super.display (self, txt=txt, end=False, full=full)
        indent1 = 2*' '
        indent2 = 6*' '
 
        ss = TDL_common.Super.display_insert_object (self, ss, self.NodeSet, full=full)
        
        return TDL_common.Super.display_end (self, ss)


    #-------------------------------------------------------------------------------------
    # MeqLeaf definition:
    #-------------------------------------------------------------------------------------


    def MeqLeaf(self, ns, key=None, qual=None, leafgroup=None,
                init_funklet=None, **pp):
        """Convenience function to create a MeqLeaf node"""

        # Get the associated leafparms from the NodeSet rider record:
        if leafgroup==None:
            leafgroup = key
        rider = self.NodeSet.group_rider(leafgroup)

        # The rider fields may be overridden by the keyword arguments kwargs, if any: 
        for pkey in pp.keys():
            rider[pkey] = pp[pkey]

        # The node-name qualifiers are the superset of the default ones
        # and the ones specified in this function call:
        quals = deepcopy(self.NodeSet.quals())  # just in case.....
        if isinstance(qual, dict):
            for qkey in qual.keys():
                quals[qkey] = str(qual[qkey])

        # uniqual = _counter (leafgroup, increment=True)

        if init_funklet:
            # Special case: Make a MeqParm node.
            # Used for interpolatable Jones matrices like EJones or MIM etc
            node = ns[key](**quals) << Meq.Parm(init_funklet=init_funklet)

        else:
            #--------------------------------------------------------------
            # Make the (additive) time-variation function:
            # For the moment: A cos(MeqTime) with a certain period
            mm = []
            mean_sec = rider['timescale_min']*60*rider['mean_period']
            stddev_sec = rider['timescale_min']*60*rider['stddev_period']
            T_sec = ceil(gauss(mean_sec, stddev_sec))
            if T_sec<10: T_sec = 10
            mm.append(ns['2pi/T'](leafgroup)(**quals)(T=str(T_sec)+'sec') << Meq.Constant(2*pi/T_sec))
            mm.append(ns['MeqTime'](leafgroup)(**quals) << Meq.Time())
            node = ns['targ'](leafgroup)(**quals) << Meq.Multiply(children=mm)
            
            mm = []
            mm.append(ns << Meq.Cos(node))
            mean = rider['c00_scale']*rider['mean_c00']
            stddev = rider['c00_scale']*rider['stddev_c00']
            ampl = gauss(mean, stddev)
            mm.append(ns['tampl'](leafgroup)(**quals)(ampl=str(ampl)) << Meq.Constant(ampl))
            tvar = ns['tvar'](leafgroup)(**quals) << Meq.Multiply(children=mm)

            #----------------------------------------------------------------------
            # The simulated variations tvar (t,f) are added to the MeqParm default value.
            default = rider['c00_default']
            c00 = ns['default'](leafgroup)(value=str(default)) << Meq.Constant(default)
            node = ns[key](**quals) << Meq.Add(c00, tvar)

        # Store the new node in the NodeSet:
        self.NodeSet.MeqNode(leafgroup, node)
        return node


    #--------------------------------------------------------------------------------
    # Functions related to leafgroups:
    #--------------------------------------------------------------------------------

    def group_rider_defaults (self, rider):
        """Default values for a leafgroup rider (see self.inarg() etc)"""
        rider.setdefault('descr', '<descr>')
        rider.setdefault('unit', None)
        rider.setdefault('color', 'yellow')
        rider.setdefault('style', 'triangle')
        rider.setdefault('size', 5)
        rider.setdefault('c00_default', 1.0)
        rider.setdefault('c00_scale', 1.0)
        rider.setdefault('timescale_min', 20)
        rider.setdefault('fdeg', 0)
        rider.setdefault('mean_c00', 0.1)
        rider.setdefault('stddev_c00', 0.01)
        rider.setdefault('mean_period', 1.0)
        rider.setdefault('stddev_period', 0.1)
        rider.setdefault('unop', 'Cos')
        return True


    def inarg_group_rider (self, pp, **kwargs):
        """Definition of LeafSet input arguments (see e.g. MG_JEN_Joneset.py)"""
        self.group_rider_defaults(kwargs)
        JEN_inarg.define(pp, 'mean_c00', kwargs,
                         choice=[0,0.1,0.2,0.5,-0.1],  
                         help='mean of EXTRA c00 (fraction of c00_scale)')
        JEN_inarg.define(pp, 'stddev_c00', kwargs,
                         choice=[0,0.0001,0.001,0.01,0.1,1],  
                         help='scatter in EXTRA c00 (fraction of c00_scale')
        JEN_inarg.define(pp, 'mean_period', kwargs,
                         choice=[0.3,0.5,1,2,3],  
                         help='mean time-period T (fraction of timescale_min)')
        JEN_inarg.define(pp, 'stddev_period', kwargs,
                         choice=[0,0.01,0.1,0.2,0.5],  
                         help='scatter in period T (fraction of timescale_min)')
        JEN_inarg.define(pp, 'unop', 'Cos', hide=False,
                         choice=['Cos','Sin',['Cos','Sin'],None],  
                         help='time-variability function')
        # Hidden:
        JEN_inarg.define(pp, 'timescale_min', kwargs, hide=True,
                         help='group timescale in minutes')
        JEN_inarg.define(pp, 'fdeg', kwargs, hide=True,
                         help='degree of freq polynomial')
        JEN_inarg.define(pp, 'color', kwargs, hide=True,
                         help='plot_color')
        JEN_inarg.define(pp, 'style', kwargs, hide=True,
                         help='plot_style')
        JEN_inarg.define(pp, 'size', kwargs, hide=True,
                         help='size of plotted symbol')
        JEN_inarg.define(pp, 'c00_default', kwargs, hide=True,
                         help='default value of c00')
        JEN_inarg.define(pp, 'c00_scale', kwargs, hide=True,
                         help='scale of c00')
        JEN_inarg.define(pp, 'descr', kwargs, hide=True,
                         help='brief description')
        JEN_inarg.define(pp, 'unit', kwargs, hide=True,
                         help='unit')

        # Attach any other kwarg fields to pp also:
        for key in kwargs.keys():
            if not pp.has_key(key):
                pp[key] = kwargs[key]
                
        return True


    def leafgroup (self, key=None, rider=None, **kwargs):
        """Get/define the named (key) leafgroup"""
        if not rider==None:
        # if not rider==None or len(kwargs)>0:
            # The rider usually contains the inarg record (pp) of the calling function.
            if not isinstance(rider, dict): rider = dict()  # just in case
            rider = deepcopy(rider)                         # necessary!
            rider = TDL_common.unclutter_inarg(rider)

            self.group_rider_defaults(rider)

            # The rider fields may be overridden by the keyword arguments kwargs, if any: 
            for pkey in kwargs.keys():
                rider[pkey] = kwargs[pkey]
            self._history('Created leafgroup: '+str(key)+' (rider:'+str(len(rider))+')')
            result = self.NodeSet.group(key, rider=rider)      
            return result
        # Then the generic NodeSet part:
        return self.NodeSet.group(key)


    def leafgroup_keys (self):
        """Return the keys (names) of the available leafgroups"""
        return self.NodeSet.group_keys()

    def subtree_leafgroups(ns, bookpage=True):
        """Make a subtree of the available leafgroups, and return its root node"""
        node = self.NodeSet.make_bundle (ns, group=None, name=None, bookpage=bookpage)
        return rootnode


    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------

    def cleanup(self):
      """Remove empty leafgroups etc"""
      self.NodeSet.cleanup()
      return True


    def update(self, LeafSet=None):
        """Update the leafgroup info etc from another LeafSet object"""
        if LeafSet==None: return False
        self._updict_rider(LeafSet._rider())
        self.NodeSet.update(LeafSet.NodeSet)
        self.history(append='updated from: '+LeafSet.oneliner())
        return True

    def updict(self, LeafSet=None):
        """Updict the leafgroup info etc from another LeafSet object"""
        if LeafSet==None: return False
        self._updict_rider(LeafSet._rider())
        self.NodeSet.updict(LeafSet.NodeSet)
        self.history(append='updicted from: '+LeafSet.oneliner())
        return True


    #----------------------------------------------------------------------
    #   methods used in saving/restoring the LeafSet
    #----------------------------------------------------------------------

    def clone(self):
        """clone self such that no NodeStubs are present.
        This is needed to save the LeafSet."""
        newp = LeafSet()
        newp.NodeSet = self.NodeSet.clone()        # object!
        return newp

    def restore(self, oldp, ns):
        """ recreate the LeafSet from a saved version 'oldp'"""
        self.NodeSet.restore(ns, oldp.NodeSet)     # object
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
    if trace: print '** LeafSet: _counters(',key,') =',_counters[key]
    return _counters[key]






#========================================================================
# Test routine:
#========================================================================

if __name__ == '__main__':
    print '\n*******************\n** Local test of: TDL_LeafSet.py:\n'
    from numarray import *
    from Timba.Trees import TDL_display
    # from Timba.Contrib.JEN import MG_JEN_funklet
    ns = NodeScope()
    # nsim = ns.Subscope('_')
    
    ls = LeafSet(label='initial', polrep='circular')
    ls.display('initial')

    if 0:
        print '** dir(ls) ->',dir(ls)
        print '** ls.__doc__ ->',ls.__doc__
        print '** ls.__str__() ->',ls.__str__()
        print '** ls.__module__ ->',ls.__module__
        print


    if 1:
        pp = dict(aa=6, bb=7)
        ls.group_rider_defaults(pp)
        g1 = ls.leafgroup('group_1', rider=pp, aa=89)
        g2 = ls.leafgroup('group_2', rider=pp)
        ls.MeqLeaf(ns, g1, qual=dict(s=7), **pp)
        nodes = ls.NodeSet.nodes(g1)
        print nodes
        TDL_display.subtree(nodes[0], 'g1', full=True, recurse=3)

    if 1:
        # Display the final result:
        ls.display('final result', full=True)
        # ls.display('final result')

    print '\n*******************\n** End of local test of: TDL_LeafSet.py:\n'




#============================================================================================

#============================================================================================

# .leafgroup():
# - register with:
#   - color, style,etc
#   - stddev,mean
# - do via Joneset object (contains Parmset and LeafSet)
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


#============================================================================








 

