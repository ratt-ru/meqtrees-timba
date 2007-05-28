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
from Timba.Contrib.JEN.Grunt import display
from Timba.Contrib.JEN.Expression import Expression

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
        quals = _quals2list(quals)

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
            rr['solvable'] = '<'+str(len(rr['solvable']))+'>'
            rr['plot_labels'] = '<'+str(len(rr['plot_labels']))+'>'
            if not rr['simul']:
                rr['deviation'] = '<NA>'
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


    def p_groups (self):
        """Return a list of names of the available parmgroups"""
        return self._parmgroups.keys()

    #---------------------------------------------------------------

    def p_group_define (self, key, tags=None, descr='<descr>',
                        default=0.0, 
                        simul=False, deviation=None,
                        tiling=None, time_deg=0, freq_deg=0, **kw):
        """Define a named (key) group of similar parameters"""

        # Check whether the group exists already:
        if self._parmgroups.has_key(key):
            s = '** duplicate parmgroup definition: '+str(key)
            raise ValueError,s

        # The node tags may be used for finding nodes in ns:
        tags = _tags2list(tags)
        if not key in tags: tags.append(key)
        if not self.name in tags: tags.append(self.name)
        # NB: What about a qualifier like '3c84'?
        # qnode = self.ns0[key]

        # If simul==True, the deviation from the default value
        # (e.g. as a function of time [t] and/or freq [f]), is
        # given by a math Expression:
        if not isinstance(deviation, str):
            deviation = '{0.01~0.001}*sin(2*pi*([t]/{500~50}+{0~1}))'

        # Create the group definition:
        rr = dict(default=default, 
                  simul=simul, deviation=deviation,
                  descr=descr, tags=tags,
                  tiling=tiling,
                  time_deg=time_deg,
                  freq_deg=freq_deg,
                  nodes=[], solvable=[], plot_labels=[])
        self._parmgroups[key] = rr
        return self._parmgroups[key]

    #-----------------------------------------------------------------

    def p_group_create_member (self, key, quals=[], kwquals={},
                               value=None, tags=[], solvable=True,            # ....??
                               simul=None, default=None, deviation=None,      # may override
                               tiling=None, time_deg=0, freq_deg=0):          # may override for Meow.Parm
        """Create the specified (quals, kwquals) member of the specified (key)
        parmgroup. By default, the common attrbutes of the group will be used
        to create the relevant Meow.Parm or simulation subtree, but some of
        these attributes may be overridden here...."""

        # Check whether the parmgroup (key) exists:
        if not self._parmgroups.has_key(key):
            s = '** parmgroup not recognised: '+str(key)
            raise ValueError,s
        rr = self._parmgroups[key]

        # Make the qualified node (qnode) for the new group member,
        # and check whether it already exists: 
        quals = _quals2list(quals)
        if not isinstance(simul, bool):            # simul not explicitly specfied
            simul = rr['simul']                    # use the group default
        if simul:
            quals.append('simul')                  # add 'simul' qualifier
        qnode = self.ns[key](*quals)(**kwquals)    # qualified node (stub)       
        if qnode.initialized():
            s = '** parmgroup member already exists: '+str(qnode)
            raise ValueError,s
        nodename = qnode.name                      # used in ._add_parm()

        # Any extra tags are appended to the default (rr) ones.....?!
        ptags = _tags2list(tags)
        ptags.append(rr['tags'])

        # Use the Meow Parm/Parameterization mechanism as much as possible:
        if simul:
            # Return the root node of a subtree that simulates the MeqParm
            # NB: The default (rr) default and deviation may be overridden here
            rootnode = _simul_subtree(rr, qnode,
                                      default=default, deviation=deviation,
                                      tags=ptags)
            solvable = False
            self._add_parm(nodename, rootnode, tags=tags, solvable=solvable)

        elif isinstance(value, Meow.Parm):
            self._add_parm(nodename, value, tags=ptags, solvable=solvable)

        elif is_node(value):
            self._add_parm(nodename, value, tags=ptags, solvable=solvable)

        else:
            # NB: Check the exact working of or/and etc on lists, dicts.......!!
            mparm = Meow.Parm(value=(value or rr['default']),
                              tiling=(tiling or rr['tiling']),
                              time_deg=(time_deg or rr['time_deg']),
                              freq_deg=(freq_deg or rr['freq_deg']),
                              tags=[])
            self._add_parm(nodename, mparm, tags=ptags, solvable=solvable)

        # Update the parmgroup with the new member node:
        node = self._parm(nodename)
        rr['nodes'].append(node)
        rr['plot_labels'].append(nodename)
        rr['solvable'].append(solvable)

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
    # Convenient access to a list of nodes/subtrees, e.g. for solving
    #===============================================================

    def p_solvable (self, tags=None, parmgroups='*'):
        """Return a list with the specified selection of solvable MeqParm nodes.
        The nodes may be specified by their tags (n.search) or by parmgroups."""
        return self.p_find_nodes (tags=tags, parmgroups=parmgroups, solvable=True)

    #----------------------------------------------------------------

    def p_find_nodes (self, tags=None, parmgroups='*',
                      solvable=None, trace=True):
        """Return a list with the specified selection of the nodes (names)
        that are known to this Parameterization object. The nodes may be
        specified by their tags (n.search) or by parmgroups. The defaults are
        tags=None and parmgroups='*', but tags are checked first."""

        if trace: print '\n** p_find_nodes(tags=',tags,', pg=',parmgroups,', solvable=',solvable,'):'
        nodes = []
        if tags:
            tags = _tags2list(tags)
            class_name = None
            if solvable:
                tags.append('solvable')
                class_name = 'MeqParm'
            print '\n-- self.ns.Search(',class_name,' tags=',tags,')'
            nodes = self.ns.Search(tags=tags, class_name=class_name)

        elif parmgroups:
            pg = parmgroups                             # convenience
            if isinstance(pg, str): pg = pg.split(' ')
            pg = list(pg)
            if pg[0]=='*': pg = self._parmgroups.keys() # all parmgroups
            for key in pg:
                if not self._parmgroups.has_key(key):
                    raise ValueError,'** parmgroup not recognised: '+key
                rr = self._parmgroups[key]              # convenience
                if not isinstance(solvable, bool):      # solvable not speified
                    nodes.extend(rr['nodes'])           # include all nodes
                else:
                    for k,node in enumerate(rr['nodes']):
                        if rr['solvable'][k]==solvable: # the specified kind
                            nodes.append(node)          # selected nodes only

        if trace:
            for node in nodes: print '  -',str(node)
            print '  ->',len(nodes),'nodes\n'
        return nodes


    #===============================================================
    # Visualization:
    #===============================================================

    def p_inspector (self, tags=None, parmgroups=None, bookpage=None):
        """Visualize the specialized parms"""
        return node

    def p_rvsi (self, tags=None, parmgroups=None, vertical=None, bookpage=None):
        """Visualize the specialized parms in a real-vs-imaginary plot."""
        return node


    #===============================================================
    # Some extra functionality for Meow.Parameterization 
    #===============================================================

    def p_modify_default (self, name):
        """Modify the default value of the specified parm"""
        # See Expression.py
        return False






#=============================================================================
#=============================================================================
#=============================================================================
# Some helper functions (standalone, so they do not clog up the object):
#=============================================================================

def _tags2list (tags):
    """Helper function to make sure that the given tags are a list"""
    if isinstance(tags, (list, tuple)): return list(tags)
    if tags==None: return []
    if isinstance(tags, str): return tags.split(' ')
    s = '** cannot convert to list: '+str(type(tags))+' '+str(tags)
    raise TypeError, s

def _quals2list (quals):
    """Helper function to make sure that the given quals are a list"""
    if isinstance(quals, (list,tuple)): return list(quals)
    if quals==None: return []
    if isinstance(quals, str): return quals.split(' ')
    return [str(quals)]

#----------------------------------------------------------------------------
    
def _simul_subtree(rr, qnode,
                   default=None, deviation=None,
                   tags=[], show=True):
    """Return the root node of a subtree that simulates the
    behaviour of a MeqParm."""
    
    # The deviation from the default value is described by a math expression.
    # The default (rr) values may be overridden.
    simexpr = str(default or rr['default'])+'+'+(deviation or rr['deviation'])
    
    # Make a MeqFunctional node from the given expression
    Ekey = Expression.Expression(qnode, ' ', expr=simexpr)
    node = Ekey.MeqFunctional()

    # Make a root node with the correct name (qnode) and tags:
    ptags = tags
    if not 'simul' in tags: tags.append('simul')
    qnode << Meq.Identity(node, tags=ptags)
    if show: display.subtree(qnode)
    return qnode

#----------------------------------------------------------------------------
      
    
    








#===============================================================
# Test routine:
#===============================================================

if __name__ == '__main__':
    ns = NodeScope()


    if 1:
        pp1 = ParameterizationPlus(ns, 'GJones',
                                   # kwquals=dict(tel='WSRT', band='21cm'),
                                   quals='3c84')
        pp1.p_display('initial')

    if 1:
        pp1.p_group_define('Gphase', tiling=3, simul=False)
        pp1.p_group_define('Ggain', default=1.0, freq_deg=2)

    if 0:
        pp1.p_group_create_member('Gphase', 1)
        pp1.p_group_create_member('Gphase', 2.1, value=(ns << -89))
        pp1.p_group_create_member('Gphase', 2, value=34)
        pp1.p_group_create_member('Gphase', 3, tiling=5, simul=False)
        pp1.p_group_create_member('Gphase', 7, freq_deg=2)

    if 1:
        pp1.p_group_create_member('Ggain', 7, freq_deg=6)
        pp1.p_group_create_member('Ggain', 4, time_deg=3)

    pp1.p_display('final', full=True)


    if 1:
        print 'ns.Search(tags=Gphase):',ns.Search(tags='Gphase')
        print 'pp1.ns.Search(tags=Gphase):',pp1.ns.Search(tags='Gphase')



    if 0:
        pp1.p_solvable()
        pp1.p_solvable(parmgroups='Gphase')
        pp1.p_solvable(parmgroups=['Ggain'])
        pp1.p_solvable(parmgroups=['Gphase','Ggain'])
        pp1.p_solvable(parmgroups=pp1.p_groups())
        # pp1.p_solvable(parmgroups=['Gphase','xxx'])

    if 0:
        pp1.p_solvable(tags='Gphase')

    if 0:
        pp1.p_find_nodes(solvable=True)

    if 0:
        pp2 = ParameterizationPlus(ns, 'GJones', quals='CasA')
        pp2.p_group_define('Gphase')
        pp2.p_group_create_member('Gphase', 1)
        pp2.p_group_create_member('Gphase', 7)
        pp2.p_display(full=True)


#===============================================================

