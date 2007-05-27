# file: ../Grunt/ParameterizationPlus.py

# History:
# - 26may2007: creation 

# Description:

# The Grunt ParameterizationPlus class is derived from the
# Meow Parameterization class. It adds some extra functionality
# for groups of similar parms, which may find their way into the
# more official Meow system eventually.

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

import Meow

from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect

from copy import deepcopy

#======================================================================================

class ParameterizationPlus (Meow.Parameterization):
    """The Grunt ParameterizationPlus class is derived from the
    Meow Parameterization class. It adds some extra functionality
    for groups of similar parms, which may find their way into the
    more official Meow system eventually."""

    def __init__(self, ns, name, quals=[], kwquals={}):

        if is_node(ns): ns = ns.QualScope()

        # Make a little more robust 
        if quals==None: quals = []
        if not isinstance(quals, (list,tuple)): quals = [quals]

        Meow.Parameterization.__init__(self, ns, str(name),
                                       quals=quals, kwquals=kwquals)

        self._parmgroups = dict()
        return None

      

    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def p_oneliner(self):
        """Return a one-line summary of this object"""
        ss = 'Grunt.ParameterizationPlus:'
        ss += ' '+str(self.name)
        ss += '  ('+str(self.ns['<nodename>'].name)+')'
        return ss


    def p_display(self, txt=None, full=False, recurse=3):
        """Print a summary of this object"""
        print ' '
        print '** '+self.p_oneliner()
        if txt: print '  * (txt='+str(txt)+')'
        #...............................................................
        print '  * Grunt _parmgroups ('+str(len(self._parmgroups))+'):'
        for key in self._parmgroups:
            rr = deepcopy(self._parmgroups[key])
            rr['nodes'] = '<'+str(len(rr['nodes']))+'>'
            rr['plot_labels'] = '<'+str(len(rr['plot_labels']))+'>'
            print '    - ('+key+'): '+str(rr)
        #...............................................................
        print '  * Meow _parmdefs ('+str(len(self._parmdefs))+') (value,tags,solvable):'
        if full:
            for key in self._parmdefs:
                rr = list(deepcopy(self._parmdefs[key]))
                rr[0] = str(rr[0])
                print '    - ('+key+'): '+str(rr)
        #...............................................................
        print '  * Meow.Parm options (in _parmdefs):'
        if full:
            for key in self._parmdefs:
                value = self._parmdefs[key][0]
                if isinstance(value, Meow.Parm):
                    print '    - ('+key+'): (='+str(value.value)+') '+str(value.options)
        #...............................................................
        print '  * Meow _parmnodes ('+str(len(self._parmnodes))+'):'
        if full:
            for key in self._parmnodes:
                rr = self._parmnodes[key]
                print '    - ('+key+'): '+str(rr)
        #...............................................................
        print '**\n'
        return True


    #===============================================================
    # - Parmgroups are designed for the common case of
    # groups of similar parameters, like the station phases of a set
    # of Jones matrices. The latter are encapsulated in a Joneset22
    # object, which is derived (via the class Matrixett22) from
    # ParameterizationPlus.
    # - A parmgroup (e.g. Gphase) must first be defined, together with
    # the various attributes (tags, default value, etc) that its members
    # have in common. Individual members (MeqParm nodes or subtrees that
    # simulate their behaviour) of such a group are created with extra
    # nodename qualifier(s).
    # - The members (nodes/subtrees) of a parmgroup may be obtained
    # (e.g. for solving) and/or manipulated (e.g. visualized) as a group.
    #===============================================================

    def p_group_define (self, key, tags=None, descr='<descr>',
                        default=0.0, 
                        simul=False, simex=None,
                        tiling=None, time_deg=0, freq_deg=0, **kw):
        """Define a named (key) group of similar parameters"""

        # Check whether the group exists already:
        if self._parmgroups.has_key(key):
            s = '** duplicate parmgroup definition: '+str(key)
            raise ValueError,s

        # The node tags may be used for finding nodes in ns:
        if tags==None: tags = []
        if isinstance(tags, str): tags = tags.split(" ")
        tags = list(tags)
        if not key in tags: tags.append(key)
        if not self.name in tags: tags.append(self.name)
        # NB: What about a qualifier like '3c84'?
        # qnode = self.ns0[key]

        # Create the group definition:
        rr = dict(default=default, 
                  simul=simul, simex=simex,
                  descr=descr, tags=tags,
                  tiling=tiling,
                  time_deg=time_deg,
                  freq_deg=freq_deg,
                  nodes=[], plot_labels=[])
        self._parmgroups[key] = rr
        return self._parmgroups[key]

    #-----------------------------------------------------------------

    def p_group_create_member (self, key, quals=[], kwquals={},
                               value=None, tags=[], solvable=True,            # ....??
                               tiling=None, time_deg=0, freq_deg=0):          # override for Meow.Parm
        """Create the specified (quals, kwquals) member of the specified (key)
        parmgroup. By default, the common attrbutes of the group will be used
        to create the relevant Meow.Parm or simulation subtree, but some of
        these attributes may be overridden here...."""

        # Check whether the parmgroup (key) exists:
        if not self._parmgroups.has_key(key):
            s = '** parmgroup not recognised: '+str(key)
            raise ValueError,s
        rr = self._parmgroups[key]

        # Make the member nodename, and check whether it already exists: 
        if quals==None: quals = []
        if not isinstance(quals, (list,tuple)): quals = [quals]
        qnode = self.ns0[key](*quals)
        # qnode = self.ns0[key](*quals)(**kwquals)                           # <---!
        if qnode.initialized():
            s = '** parmgroup member already exists: '+str(qnode)
            raise ValueError,s
        nodename = qnode.name

        tags = rr['tags']

        # Use the Meow Parm/Parameterization mechanism as much as possible:
        if isinstance(value, Meow.Parm):
            self._add_parm(nodename, value, tags=tags, solvable=solvable)

        elif is_node(value):
            self._add_parm(nodename, value, tags=tags, solvable=solvable)

        elif rr['simul']:
            # node = Expression(self.ns0, rr['simex'],....)
            self._add_parm(nodename, node, tags=tags, solvable=False)

        else:
            mparm = Meow.Parm(value=(value or rr['default']),
                              tiling=(tiling or rr['tiling']),
                              time_deg=(time_deg or rr['time_deg']),
                              freq_deg=(freq_deg or rr['freq_deg']),
                              tags=[])
            self._add_parm(nodename, mparm, tags=tags, solvable=solvable)

        # Update the parmgroup with the new member node:
        node = self._parm(nodename)
        rr['nodes'].append(node)
        rr['plot_labels'].append(nodename)

        # Return the new member node:
        return node


    #===============================================================
    # Meow.Parametrization methods
    #===============================================================

    # def _add_parm (self,name,value,tags=[],solvable=True):
    # """Adds an entry for parameter named 'name'. No nodes are created yet;
    # they will only be created when self._parm(name) is called later. This
    # is useful because a Meow component can pre-define all necessary 
    # parameters at construction time with _add_parm(), but then make nodes
    # only for the ones that are actually in use with _parm().
    #     self._parmdefs[name] = (value,tags,solvable); 

    # def _parm (self,name,value=None,tags=[],nodename=None,solvable=True):
    # """Returns node representing parameter 'name'.
    # If 'nodename' is None, node is named after parm, else
    # another name may be given.
    # If value is not supplied, then the parameter should have been previously
    # defined via _add_parm(). Otherwise, you can define and create a parm 
    # on-the-fly by suppying a value and tags as to _add_parm.
    #    self._parmnodes[name] = resolve_parameter(name,self.ns[nodename],
    #                                              value,tags,solvable);
    #    return self._parmnodes[name];

    # 
    # Meow.Parm: (value=0,tags=[],tiling=None,time_deg=0,freq_deg=0,**kw):


    #===============================================================
    # Merge the parametrization of another object in its own.
    # NB: One should be careful with this since there is merit to keep 
    #     parameter sets with the same names but different qualifies apart.
    #     But it is useful for merging parametrizations in the same subtree.
    #     For instance, a JJones object, which is the multiplication of 
    #     multiple Jones matrices, with DIFFERENT parmgroup names, but with
    #     the same qualifiers (e.g. '3c84')
    #===============================================================

    def p_merge (self, other):
        """Merge the parm contents with those of another object.
        The latter must be derived of Meow.Parametrization, but
        it may or may not be derived from Grunt.ParametriZationPlus.
        If not, it will copy the parmdefs, but not any parmgroups."""
        return True



    #===============================================================
    # Convenient access to groups of solvable parms, for solving
    #===============================================================

    def p_solvable (self, tags=None, parmgroup=None):
        """Return the specified list of solvable MeqParm nodes"""
        return []


    #===============================================================
    # Visualization:
    #===============================================================

    def p_inspector (self, tags=None, parmgroup=None, bookpage=None):
        """Visualize the specialized parms"""
        return node

    def p_rvsi (self, tags=None, parmgroup=None, vertical=None, bookpage=None):
        """Visualize the specialized parms in a real-vs-imaginary plot."""
        return node


    #===============================================================
    # Some extra functionality for Meow.Parameterization 
    #===============================================================

    def p_modify_default (self, name):
        """Modify the default value of the specified parm"""
        # See Expression.py
        return False

    
    








#===============================================================
# Test routine:
#===============================================================

if __name__ == '__main__':
    ns = NodeScope()

    pp1 = ParameterizationPlus(ns, 'pp1', quals=5)
    pp1.p_display('initial')

    if 1:
        pp1.p_group_define('Gphase', tiling=3)
        pp1.p_group_define('Ggain', default=1.0, freq_deg=2)

    if 1:
        pp1.p_group_create_member('Gphase', 1)
        pp1.p_group_create_member('Gphase', 2.1, value=(ns << -89))
        pp1.p_group_create_member('Gphase', 2, value=34)
        pp1.p_group_create_member('Gphase', 3, tiling=5)
        pp1.p_group_create_member('Gphase', 7, freq_deg=2)
        pp1.p_group_create_member('Ggain', 7, freq_deg=6)
        pp1.p_group_create_member('Ggain', 4, time_deg=3)

    pp1.p_display('final', full=True)

    if 0:
        pp2 = ParameterizationPlus(ns, 'pp2')
        pp2.p_group_define('Gphase')
        pp2.p_group_create_member('Gphase', 1)
        pp2.p_group_create_member('Gphase', 7)
        pp2.p_display(full=True)



#===============================================================

