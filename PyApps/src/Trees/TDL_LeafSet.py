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
#    - 07 apr 2006: added MeqLeaf compounder_children
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
from Timba.Meq import meq

from copy import deepcopy
from random import *
from math import *
from numarray import *

from Timba.Trees import TDL_common
from Timba.Trees import TDL_NodeSet
# from Timba.Contrib.MXM import TDL_Functional 
# from Timba.Trees import TDL_Functional 
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
                compounder_children=None, common_axes=None, qual2=None,
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

        # Make the new MeqLeaf subtree (if necessary):
        node = ns[key](**quals)
        if node.initialized():                           # node already exists
            return node

        elif rider['simul_funklet']:
            # A simulation funklet (expression) has been specified
            # The funklet coeff have a probability distribution:
            expr = rider['simul_funklet']
            coeff = []
            for k in range(10):
                s1 = 'p'+str(k)
                if expr.rfind(s1)<0: break
                ms = rider[s1+'_mean_stddev']
                coeff.append(gauss(ms[0], ms[1]))
                # print '-',k,s1,ms,coeff
            if True:
                init_funklet = meq.polc(coeff=coeff, subclass=meq._funklet_type)
                init_funklet.function = rider['simul_funklet']
            else:
                # init_funklet = TDL_Functional(rider['simul_funklet'], coeff)
                pass
            node << Meq.Parm(init_funklet=init_funklet)


        elif compounder_children:
            # Special case: Make a MeqCompounder node with a ND funklet.
            # Used for interpolatable Jones matrices like EJones or MIM etc
            parm = ns[key](**quals)('funklet')
            if not parm.initialized():
                parm << Meq.Parm(init_funklet=init_funklet)
                self.NodeSet.set_MeqNode(parm, group=leafgroup)
            cc = compounder_children
            if not isinstance(cc, (list, tuple)): cc = [cc]
            cc.append(parm)
            ## cc.insert(0,parm)                           # temporary: prepend
            # The Compounder has more qualifiers than the Parm.
            # E.g. EJones_X is per station, but the compounder and its
            # children (l,m) are for a specific source (q=3c84)
            if isinstance(qual2, dict):
                for qkey in qual2.keys():
                    quals[qkey] = str(qual2[qkey])
            node = ns[key](**quals)
            node << Meq.Compounder(children=cc, common_axes=common_axes)
            # Special case, return from here:
            return node
        
        elif init_funklet:
            # Special case: Make a MeqParm node with an ND funklet.....(?)
            node << Meq.Parm(init_funklet=init_funklet)

        else:
            # Error?
            pass

        # Store the new node in the NodeSet:
        self.NodeSet.set_MeqNode(node, group=leafgroup)
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

        rider.setdefault('simul_funklet', None)
        rider.setdefault('p0_mean_stddev', [0.0,0.0])
        rider.setdefault('p1_mean_stddev', [0.0,0.0])
        rider.setdefault('p2_mean_stddev', [0.0,0.0])
        rider.setdefault('p3_mean_stddev', [0.0,0.0])
        rider.setdefault('p4_mean_stddev', [0.0,0.0])
        rider.setdefault('p5_mean_stddev', [0.0,0.0])
        rider.setdefault('p6_mean_stddev', [0.0,0.0])
        rider.setdefault('p7_mean_stddev', [0.0,0.0])
        rider.setdefault('p8_mean_stddev', [0.0,0.0])
        rider.setdefault('p9_mean_stddev', [0.0,0.0])
        return True


    def inarg_group_rider (self, pp, **kwargs):
        """Definition of LeafSet input arguments (see e.g. MG_JEN_Joneset.py)"""
        self.group_rider_defaults(kwargs)
            
        # Hidden:
        JEN_inarg.define(pp, 'descr', kwargs, hide=True,
                         help='brief description')
        JEN_inarg.define(pp, 'unit', kwargs, hide=True,
                         help='unit')
        JEN_inarg.define(pp, 'color', kwargs, hide=True,
                         help='plot_color')
        JEN_inarg.define(pp, 'style', kwargs, hide=True,
                         help='plot_style')
        JEN_inarg.define(pp, 'size', kwargs, hide=True,
                         help='size of plotted symbol')

        # Specification of funklet and its coeff:
        JEN_inarg.define(pp, 'simul_funklet', kwargs, hide=True,
                         choice=['p0*cos(0.1*x0/p1)',None],
                         help='(x0=time, x1=freq)')
        JEN_inarg.define(pp, 'p0_mean_stddev', kwargs, hide=True,
                         help='[mean, stddev] of funklet coeff p0')
        JEN_inarg.define(pp, 'p1_mean_stddev', kwargs, hide=True,
                         help='[mean, stddev] of funklet coeff p1')
        JEN_inarg.define(pp, 'p2_mean_stddev', kwargs, hide=True,
                         help='[mean, stddev] of funklet coeff p2')
        JEN_inarg.define(pp, 'p3_mean_stddev', kwargs, hide=True,
                         help='[mean, stddev] of funklet coeff p3')
        JEN_inarg.define(pp, 'p4_mean_stddev', kwargs, hide=True,
                         help='[mean, stddev] of funklet coeff p4')
        JEN_inarg.define(pp, 'p5_mean_stddev', kwargs, hide=True,
                         help='[mean, stddev] of funklet coeff p5')
        JEN_inarg.define(pp, 'p6_mean_stddev', kwargs, hide=True,
                         help='[mean, stddev] of funklet coeff p6')
        JEN_inarg.define(pp, 'p7_mean_stddev', kwargs, hide=True,
                         help='[mean, stddev] of funklet coeff p7')
        JEN_inarg.define(pp, 'p8_mean_stddev', kwargs, hide=True,
                         help='[mean, stddev] of funklet coeff p8')
        JEN_inarg.define(pp, 'p9_mean_stddev', kwargs, hide=True,
                         help='[mean, stddev] of funklet coeff p9')

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








 

