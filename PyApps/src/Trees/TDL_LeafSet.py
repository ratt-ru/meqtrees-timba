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


    def display(self, txt=None, full=False, doprint=True, pad=True):
        """Display a description of the contents of this LeafSet object"""
        ss = TDL_common.Super.display (self, txt=txt, end=False, full=full)
        indent1 = 2*' '
        indent2 = 6*' '
 
        ss = TDL_common.Super.display_insert_object (self, ss, self.NodeSet, full=full)
        
        return TDL_common.Super.display_end (self, ss, doprint=doprint, pad=pad)



    #=====================================================================================
    # MeqLeaf definition:
    #=====================================================================================

    def inarg_simul (self, pp, key='<key>', hide=False,
                     offset=0, scale=1, time_scale_min=100, fdeg=0,
                     funklet=None, MeqConstant=None,
                     expr=None, default=None, scatter=None,
                     **kwargs):
        """Specification of simulation funklet and its coeff"""

        self.inarg_leafgroup_rider(pp, hide=hide)

        # If a funklet is specified, use that:
        if funklet:
            # expr = funklet.function()
            # default = ...
            # scatter = ...
            pass

        #-----------------------------------------
        # Some default funklet expressions (the first is the default):
        if expr:
            # expr is explicitly specified: make it the first
            if not isinstance(expr, (list,tuple)): expr = [expr]
        else:  
            expr = []                          
        nexpr = len(expr)

        # A cosine(time) variation around some constant 'offset' value.
        # The variation has an amplitude (p0) and a time_scale (p1) in minutes.
        costime = 'offset+p0*cos(0.1*x0/p1)'
        expr.append(costime)

        # Various degrees of frequency dependence:
        fdeg1 = 'p2*fGHz'
        fdeg2 = fdeg1+'+p3*(fGHz**2)'
        fdeg3 = fdeg2+'+p4*(fGHz**3)'
        fdeg4 = fdeg3+'+p5*(fGHz**4)'
        expr.append('('+costime+')*('+fdeg1+')')
        expr.append('('+costime+')*('+fdeg2+')')
        expr.append('('+costime+')*('+fdeg3+')')
        expr.append('('+costime+')*('+fdeg4+')')
        if fdeg==1: expr.insert(nexpr, '('+costime+')*('+fdeg1+')')
        if fdeg==2: expr.insert(nexpr, '('+costime+')*('+fdeg2+')')
        if fdeg==3: expr.insert(nexpr, '('+costime+')*('+fdeg3+')')
        if fdeg==4: expr.insert(nexpr, '('+costime+')*('+fdeg4+')')

        #-----------------------------------------
        # The corresponding sets of default funklet values (the first is the default):
        if default:
            # default is explicitly specified: make it the first
            if not isinstance(default, (list,tuple)): default = [default]
        else:
            default=[]
        # NB: Any missing fields (p3, p4 etc) are assumed to be zero
        default.append(dict(p0=0, p1=time_scale_min, p2=1.0, p3=1.0, p4=1.0, p5=1.0))
        # NB: At this moment, dict inarg values cannot be edited, so we cannot add p's
        #     Therefore, we have to supply values for all expected p's in the default dict....
        # if fdeg==0: default.append(dict(p0=0, p1=time_scale_min))
        # if fdeg==1: default.append(dict(p0=0, p1=time_scale_min, p2=1.0))
        # if fdeg==2: default.append(dict(p0=0, p1=time_scale_min, p2=1.0, p3=0.1))
        # if fdeg==3: default.append(dict(p0=0, p1=time_scale_min, p2=1.0, p3=0.1, p4=0.03))
        # if fdeg==4: default.append(dict(p0=0, p1=time_scale_min, p2=1.0, p3=0.1, p4=0.03, p5=0.01))

        #-----------------------------------------
        # Scatter (stddev) in default values:
        if scatter:
            # scatter is explicitly specified: make it the first
            if not isinstance(scatter, (list,tuple)): scatter = [scatter]
        else:
            scatter=[]
        # NB: Any missing fields (p3, p4 etc) are assumed to be zero
        scatter.append(dict(p0=float(scale)/10, p1=float(time_scale_min)/10))

        #-----------------------------------------
        # Replace some substrings (see above): 
        for i in range(len(expr)):
            expr[i] = expr[i].replace('fGHz','(x1/1000000000)')
            expr[i] = expr[i].replace('fMHz','(x1/1000000)')
            if offset==0:
                expr[i] = expr[i].replace('offset+','')
            else:
                expr[i] = expr[i].replace('offset',str(offset))

        #-----------------------------------------
        # Define the input arguments in pp:
        JEN_inarg.define(pp, 'simul_funklet_'+key,
                         expr[0], choice=expr, hide=hide,
                         help='p1 in minutes (x0=time, x1=freq)')
        JEN_inarg.define(pp, 'simul_default_coeff_'+key,
                         default[0], choice=default, hide=hide,
                         help='default values of '+key+' funklet coeff p0,p1,etc')
        JEN_inarg.define(pp, 'simul_scatter_coeff_'+key,
                         scatter[0], choice=scatter, hide=hide,
                         help='scatter (stddev) of '+key+' funklet coeff p0,p1,etc')

        # Replace the referenced values (prepended with @) in pp:
        qq = JEN_inarg._strip(pp)                        # does a deepcopy() too
        JEN_inarg._replace_reference(qq)                 # required here....

        substrings = []
        for pkey in qq.keys():
            i = pkey.rfind(key)
            if i>0:
                ss = pkey[0:i]
                if not ss in substrings:
                    substrings.append(ss)
        # print '**',key,': substrings =',substrings

        # The parmgroup rider is a combination of the relevant keywords in qq
        # and the (override) fields of kwargs (if any):
        rider = kwargs
        rider.setdefault('MeqConstant', None)           # temporary kludge
        for pkey in qq.keys():
            found = False
            for substring in substrings:
                if pkey.rfind(substring)>-1:
                    found = True
                    if pkey.rfind(key)>-1:
                        rider[pkey] = qq[pkey]
            if not found: rider.setdefault(pkey,qq[pkey])

        # Define a named (key) parmgroup:
        return self.define_leafgroup (key, rider=rider)





    #------------------------------------------------------------------------------

    def MeqLeaf(self, ns, key=None, qual=None, leafgroup=None,
                compounder_children=None, common_axes=None, qual2=None,
                default_coeff=None, scatter_coeff=None,
                default_value=None, init_funklet=None, **pp):
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

        # Make the new MeqLeaf node/subtree (if necessary):
        node = ns[key](**quals)

        if compounder_children:
            # Special case: Make a MeqCompounder node with a ND funklet.
            # Used for interpolatable Jones matrices like EJones or MIM etc

            # The parm is the one to be used by the solver, but it cannot
            # be evaluated by itself...
            parm = ns[key](**quals)
            if not parm.initialized():
                parm << Meq.Parm(init_funklet=init_funklet)
                self.NodeSet.set_MeqNode(parm, group=leafgroup)
            
            # The Compounder has more qualifiers than the Parm.
            # E.g. EJones_X is per station, but the compounder and its
            # children (l,m) are for a specific source (q=3c84)
            group = leafgroup                            # e.g. 'EJones'
            if isinstance(qual2, dict):
                for qkey in qual2.keys():
                    s1 = str(qual2[qkey])
                    quals[qkey] = s1
                    group += '_'+s1                      # e.g. 'EJones_3c84'
            node = ns[key](**quals)
            if not node.initialized():
                cc = compounder_children
                if not isinstance(cc, (list, tuple)): cc = [cc]
                cc.append(parm)
                node << Meq.Compounder(children=cc, common_axes=common_axes)
                self.NodeSet.set_MeqNode(node, group=group)
                self.NodeSet.append_MeqNode_eval(parm.name, append=node)

        
        elif node.initialized():                         # node already exists
            # Don't do anything, but return the existing node.
            pass

        elif rider['MeqConstant']:
            if not default_value:
                default_value = rider['MeqConstant']
            node << Meq.Constant(default_value)
            self.NodeSet.set_MeqNode(node, group=leafgroup)

        elif init_funklet:
            # An init_funklet has been specified explicitly (scatter...?)
            node << Meq.Parm(init_funklet=init_funklet)
            self.NodeSet.set_MeqNode(node, group=leafgroup)

        elif not default_value==None:
            # A default_value has been specified explicitly.
            # NB: This is also a temporary kludge to avoid the
            #     use of default_funklet below (see MG_JEN_Sixpack.py)
            node << Meq.Parm(default_value)
            self.NodeSet.set_MeqNode(node, group=leafgroup)

        else:
            # Assume that a simulation funklet (expression) has been specified
            # The funklet coeff have a probability distribution (scatter):
            expr = rider['simul_funklet']
            if default_value:                            # explicit default value....
                expr = str(default_value)+'+'+expr       # ........!!
            default = rider['simul_default_coeff']
            scatter = rider['simul_scatter_coeff']
            if default==None: default = dict()           # see default.setdefault() below
            if scatter==None: scatter = dict()           # see scatter.setdefault() below
            init_funklet = self.make_init_funklet (expr, default, scatter)
            node << Meq.Parm(init_funklet=init_funklet)
            self.NodeSet.set_MeqNode(node, group=leafgroup)

        # Finished: return the node that is to be inserted in the tree.
        return node

    #--------------------------------------------------------------------------

    def make_init_funklet (self, expr, default, scatter):
        """Helper function to make an init_funklet"""
        coeff = []
        for k in range(10):                          
            s1 = 'p'+str(k)                          # search for p0,p1,p2,...
            if expr.rfind(s1)<0: break               
            default.setdefault(s1,1.0)               # default value: 1.0
            scatter.setdefault(s1,0)                 # default: zero scatter
            coeff.append(gauss(default[s1], scatter[s1]))
        if True:
            init_funklet = meq.polc(coeff=coeff, subclass=meq._funklet_type)
            init_funklet.function = expr
        else:
            # init_funklet = TDL_Functional(rider['simul_funklet'], coeff)
            pass
        return init_funklet


    #===================================================================================
    # Functions related to leafgroups:
    #===================================================================================

    def leafgroup_rider_defaults (self, rider):
        """Default values for a leafgroup rider (see self.inarg() etc)"""
        rider.setdefault('descr', '<descr>')
        rider.setdefault('unit', None)
        rider.setdefault('color', 'yellow')
        rider.setdefault('style', 'triangle')
        rider.setdefault('size', 5)
        return True


    def inarg_leafgroup_rider (self, pp, hide=True, **kwargs):
        """Definition of LeafSet input arguments (see e.g. MG_JEN_Joneset.py)"""

        # Avoid doing this twice:
        if pp.has_key('descr') and pp.has_key('unit'): return True
        
        self.leafgroup_rider_defaults(kwargs)
        JEN_inarg.define(pp, 'descr', kwargs, hide=hide,
                         help='brief description')
        JEN_inarg.define(pp, 'unit', kwargs, hide=hide,
                         help='unit')
        JEN_inarg.define(pp, 'color', kwargs, hide=hide,
                         help='plot_color')
        JEN_inarg.define(pp, 'style', kwargs, hide=hide,
                         help='plot_style')
        JEN_inarg.define(pp, 'size', kwargs, hide=hide,
                         help='size of plotted symbol')

        if False:
            # Obsolete....
            # Attach any other kwarg fields to pp also:
            for key in kwargs.keys():
                if not pp.has_key(key):
                    pp[key] = kwargs[key]
                    
        return True

    #----------------------------------------------------------------------


    def define_leafgroup (self, key=None, rider=None, **kwargs):
        """Define the named (key) parmgroup with the specified rider (with parmgroup info).
        The rider fields may be overridden with keyword arguments in kwargs.
        If simul==True, define a leafgroup (simulation)."""
        # The rider usually contains the inarg record (pp) of the calling function.
        if not isinstance(rider, dict): rider = dict()  # just in case
        trace = False
        qq = JEN_inarg._strip(rider)                      # does a deepcopy() too
        self.leafgroup_rider_defaults(qq)                 # ...necessary...?
        # Kludge, but convenient....:
        qq.setdefault('simul_funklet_'+key,None)
        qq.setdefault('simul_default_coeff_'+key,None)
        qq.setdefault('simul_scatter_coeff_'+key,None)
        qq['simul_funklet'] = qq['simul_funklet_'+key]
        qq['simul_default_coeff'] = qq['simul_default_coeff_'+key]
        qq['simul_scatter_coeff'] = qq['simul_scatter_coeff_'+key]
        # The rider fields may be overridden by the keyword arguments kwargs, if any: 
        for pkey in kwargs.keys():
            qq[pkey] = kwargs[pkey]
        result = self.NodeSet.group(key, rider=qq)      
        self._history('Created leafgroup: '+str(key)+' (rider:'+str(len(qq))+')')
        return result

    def leafgroup (self, key=None):
        """Get the named (key) leafgroup"""
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

def _counter (key, increment=0, reset=False, trace=False):
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
        ls.leafgroup_rider_defaults(pp)
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








 

