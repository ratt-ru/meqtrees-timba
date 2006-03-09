# TDL_Leafset.py
#
# Author: J.E.Noordam
#
# Short description:
#    A Leafset object encapsulates group(s) of leaf nodes
#
# History:
#    - 24 feb 2006: creation, starting from TDL_Parmset.py
#    - 09 mar 2006: recreated from TDL_ParmSet.py
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
        # s += ' pg:'+str(len(self.parmgroup()))
        # s += ' sg:'+str(len(self.solvegroup()))
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


    def MeqLeaf(self, ns, key=None, qual=None,
                leafgroup=None, default=None, **pp):
        """Convenience function to create a MeqLeaf node"""

        # uniqual = _counter (leafgroup, increment=True)

        # The node-name qualifiers are the superset of the default ones
        # and the ones specified in this function call:
        quals = deepcopy(self.NodeSet.quals())  # just in case.....
        if isinstance(qual, dict):
            for qkey in qual.keys():
                quals[qkey] = str(qual[qkey])

        # Start with the default value for this leafgroup:
        if leafgroup==None:
            leafgroup = key

        # Get the associated leafparms fron the NodeSet rider record:
        lgp = self.NodeSet.group_rider(key)

        # Start with the MeqParm default value (funklet?) for this leafgroup:
        if default==None:
            default = lgp['c00_default']
        aa = []
        aa.append(ns['default'](leafgroup)(value=str(default)) << Meq.Constant(default))

        # Make the (additive) time-variation function:
        # For the moment: A cos(MeqTime) with a certain period
        mm = []
        mean_sec = lgp['timescale_min']*60*pp['mean_period']
        stddev_sec = lgp['timescale_min']*60*pp['stddev_period']
        T_sec = ceil(gauss(mean_sec, stddev_sec))
        if T_sec<10: T_sec = 10
        mm.append(ns['2pi/T'](leafgroup)(**quals)(T=str(T_sec)+'sec') << Meq.Constant(2*pi/T_sec))
        mm.append(ns['MeqTime'](leafgroup)(**quals) << Meq.Time())
        node = ns['targ'](leafgroup)(**quals) << Meq.Multiply(children=mm)

        mm = []
        mm.append(ns << Meq.Cos(node))
        mean = lgp['c00_scale']*pp['mean_c00']
        stddev = lgp['c00_scale']*pp['stddev_c00']
        ampl = gauss(mean, stddev)
        mm.append(ns['tampl'](leafgroup)(**quals)(ampl=str(ampl)) << Meq.Constant(ampl))
        aa.append(ns['tvar'](leafgroup)(**quals) << Meq.Multiply(children=mm))

        # Combine the various components into a leaf with the desired name:
        node = ns[key](**quals) << Meq.Add(children=aa)

        # Store the new node in the NodeSet:
        self.NodeSet.MeqNode(leafgroup, node)
        return node


    #------------------------------------------------------------------------

    def inarg (self, pp, **kwargs):
        """Definition of Leafset input arguments (see e.g. MG_JEN_Joneset.py)"""
        kwargs.setdefault('mean_c00', 0.1)
        kwargs.setdefault('stddev_c00', 0.01)
        kwargs.setdefault('mean_period', 1.0)
        kwargs.setdefault('stddev_period', 0.1)
        JEN_inarg.define(pp, 'mean_c00', kwargs,
                         choice=[0,0.1,0.2,0.5,-0.1],  
                         help='mean of EXTRA c00 (fraction of c00_scale)')
        JEN_inarg.define(pp, 'stddev_c00', kwargs,
                         choice=[0,0.0001,0.001,0.01,0.1,1],  
                         help='scatter in EXTRA c00 (fraction of c00_scale')
        JEN_inarg.define(pp, 'mean_period', kwargs,
                         choice=[0.3,0.5,1,2,3],  
                         help='mean period T (fraction of timescale_min)')
        JEN_inarg.define(pp, 'stddev_period', kwargs,
                         choice=[0,0.01,0.1,0.2,0.5],  
                         help='scatter in period T (fraction of timescale_min)')
        JEN_inarg.define(pp, 'unop', 'Cos', hide=False,
                         choice=['Cos','Sin',['Cos','Sin'],None],  
                         help='time-variability function')
        return True


    #--------------------------------------------------------------------------------
    # Functions related to leafgroups:
    #--------------------------------------------------------------------------------

    def leafgroup (self, key=None, **pp):
        """Get/define the named (key) leafgroup"""
        # First the LeafSet-specific part:
        if len(pp)>0:
            # leafgroup does not exist yet: Create it:
            # pp.setdefault('default', 1.0)       # default value (usually c00)
            pp.setdefault('color', 'red')       # plot color
            pp.setdefault('style', 'triangle')  # plot style
            pp.setdefault('size', 5)            # size of plotted symbol
            pp.setdefault('c00_default', 1.0)   # default c00 of the members of this leafgroup 
            pp.setdefault('c00_scale', 1.0)     # scale of typical parameter value
            pp.setdefault('timescale_min', 20)  # typical timescale (sec) of variation 
            pp.setdefault('fdeg', 0)            # degree of freq-variation (polynomial)
            qq = TDL_common.unclutter_inarg(pp)
            self.history('** Created leafgroup: '+str(key)+':   ')
            return self.NodeSet.group(key, **qq)
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
        self.NodeSet.update(LeafSet.NodeSet)
        self.history(append='updated from: '+LeafSet.oneliner())
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
        # Display the final result:
        # k = 0 ; TDL_display.subtree(ls[k], 'ls['+str(k)+']', full=True, recurse=3)
        ls.display('final result', full=True)
        # ls.display('final result')

    print '\n*******************\n** End of local test of: TDL_LeafSet.py:\n'




#============================================================================================

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


#============================================================================








 

