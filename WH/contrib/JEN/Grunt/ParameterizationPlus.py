# file: ../Grunt/ParameterizationPlus.py

# History:
# - 26may2007: creation
# - 07jun2007: allow {100~10%}
# - 07jun2007: p_deviation_expr()

# Description:

# The Grunt ParameterizationPlus class is derived from the
# Meow Parameterization class. It adds some extra functionality
# for groups of similar parms, which may find their way into the
# more official Meow system eventually.

# Compatibility:
# - The Grunt.ParameterizationPlus class is derived from Meow.Parameterization
# - Convert an object derived from Meow.Parameterization. Its parmdefs are
#   copied into a single parmgroup.

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

import Meow

from Timba.Contrib.JEN.Grunt import NodeList
from Timba.Contrib.JEN.Grunt import display
from Timba.Contrib.JEN.Expression import Expression

from copy import deepcopy

#======================================================================================

class ParameterizationPlus (Meow.Parameterization):
    """The Grunt ParameterizationPlus class is derived from the
    Meow Parameterization class. It adds some extra functionality
    for groups of similar parms, which may find their way into the
    more official Meow system eventually."""

    def __init__(self, ns, name, quals=[], kwquals={}, merge=None):

        # Scopify ns, if necessary:
        if is_node(ns):
            ns = ns.QualScope()        

        # Make a little more robust 
        quals = _quals2list(quals)

        Meow.Parameterization.__init__(self, ns, str(name),
                                       quals=quals, kwquals=kwquals)
        # Initialize local data:
        self._parmgroups = dict()
        self._parmNodeList = dict()
        self._parmgogs = dict()

        # Optional: Copy the parametrization of another object:
        if merge:
            self.p_merge(merge, trace=False)
        
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
            print key,rr
            rr['nodes'] = '<'+str(len(rr['nodes']))+'>'
            rr['solvable'] = '<'+str(len(rr['solvable']))+'>'
            rr['plot_labels'] = '<'+str(len(rr['plot_labels']))+'>'
            if not rr['simul']:
                rr['deviation'] = '<NA>'
            print '    - ('+key+'): '+str(rr)
        #...............................................................
        print '  * Grunt _parmgogs (groups of parmgroups, derived from their tags):'
        for key in self.p_gogs():
            print '    - ('+key+'): '+str(self._parmgogs[key])
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
        print '  * NodeList objects ('+str(len(self._parmNodeList))+'):'
        for key in self._parmNodeList:
            s = self._parmNodeList[key].oneliner()
            print '    - ('+key+'): '+s
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

    def p_has_group (self, key, severe=True):
        """Test whether it has a parmgroup of this name (key).
        If severe==True, raise a ValueError if it does not"""
        if self._parmgroups.has_key(key): return True
        if severe:
            s = '** parmgroup not recognized: '+str(key)
            raise ValueError, s
        return False

    #---------------------------------------------------------------

    def p_group_define (self, key, tags=None,
                        descr='<descr>', unit=None,
                        default=0.0, constraint=None,
                        simul=False, deviation=None,
                        tiling=None, time_deg=0, freq_deg=0,
                        # constrain_min=0.1, constrain_max=10.0,
                        rider=None, override=None,
                        **kw):
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

        # It is possible to override values via this dict.....
        # This requires a little thought....
        if isinstance(override, dict):
            pass

        # Create the group definition:
        rr = dict(default=default, tags=tags,
                  simul=simul, deviation=deviation,
                  constraint=constraint,
                  descr=descr, unit=unit,
                  tiling=tiling,
                  time_deg=time_deg,
                  freq_deg=freq_deg,
                  rider=rider,
                  nodes=[], solvable=[], plot_labels=[])
        self._parmgroups[key] = rr
        # return self._parmgroups[key]
        return key


    #-----------------------------------------------------------------

    def p_group_create_member (self, key, quals=[], kwquals={},
                               value=None, tags=[], solvable=True,            # may override
                               simul=None, default=None, deviation=None,      # may override
                               tiling=None, time_deg=0, freq_deg=0):          # may override for Meow.Parm
        """Create the specified (quals, kwquals) member of the specified (key)
        parmgroup. By default, the common attrbutes of the group will be used
        to create the relevant Meow.Parm or simulation subtree, but some of
        these attributes may be overridden here...."""

        # Check whether the parmgroup (key) exists:
        self.p_has_group (key, severe=True)
        rr = self._parmgroups[key]

        # Make the qualified node (qnode) for the new group member,
        # and check whether it already exists: 
        quals = _quals2list(quals)
        if not isinstance(simul, bool):                # simul not explicitly specfied
            simul = rr['simul']                        # use the group default

        if simul:
            quals.append('simul')                      # add 'simul' qualifier
            qnode = self.ns[key](*quals)(**kwquals)    # qualified node (stub)       
            nodename = qnode.name                      # used in ._add_parm()
        else:
            qnode = self.ns0[key](*quals)(**kwquals)   # qualified node (stub)       
            nodename = self.ns[key](*quals)(**kwquals).name

        if qnode.initialized():
            s = '** parmgroup member already exists: '+str(qnode)
            raise ValueError,s

        # Any extra tags are appended to the default (rr) ones.....?!
        ptags = _tags2list(tags)
        ptags.extend(rr['tags'])

        # Use the Meow Parm/Parameterization mechanism as much as possible:
        node = None
        if simul:
            # Return the root node of a subtree that simulates the MeqParm
            # NB: The default (rr) default and deviation may be overridden here
            rootnode = _simul_subtree(rr, qnode,
                                      default=default, deviation=deviation,
                                      tags=ptags)
            solvable = False                           # used below also!
            self._add_parm(nodename, rootnode, tags=['<NA>'], solvable=solvable)
            node = self._parm(nodename)

        elif isinstance(value, Meow.Parm):
            self._add_parm(nodename, value, tags=ptags, solvable=solvable)
            node = self._parm(nodename)

        elif is_node(value):
            self._add_parm(nodename, value, tags=ptags, solvable=solvable)
            node = self._parm(nodename)

        else:
            # NB: Check the exact working of or/and etc on lists, dicts.......!!
            mparm = Meow.Parm(value=(value or rr['default']),
                              tiling=(tiling or rr['tiling']),
                              time_deg=(time_deg or rr['time_deg']),
                              freq_deg=(freq_deg or rr['freq_deg']),
                              tags=[])
            self._add_parm(nodename, mparm, tags=ptags, solvable=solvable)
            node = self._parm(nodename, nodename=qnode.name)

        # Update the parmgroup with the new member node:
        rr['nodes'].append(node)
        rr['plot_labels'].append(nodename)
        rr['solvable'].append(solvable)

        # Return the new member node:
        return node


    #-------------------------------------------------------------------

    def p_deviation_expr (self, ampl='{0.01~10%}', Psec='{500~10%}', PHz=None):
        """Helper function to make a standard deviation expression.
        All arguments must be strings of the form {<value>~<stddev>}.
        The <stddev> is used to generate different values around <value>
        for each member of the group (see .p_group_create_member())."""
        s = ampl
        if isinstance(Psec,str):
            s += '* sin(2*pi*([t]/'+Psec+'+{0~1}))'
        if isinstance(PHz,str):
            s += '* sin(2*pi*([f]/'+PHz+'+{0~1}))'
        return s



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
    #===============================================================

    # NB: One should be careful with this since it has merit to keep 
    #     parameter sets with the same names but different qualifies apart.
    #     But it is useful for merging parametrizations in the same subtree.
    #     For instance, a JJones object, which is the multiplication of 
    #     multiple Jones matrices, with DIFFERENT parmgroup names.

    def p_merge (self, other, trace=False):
        """Merge the parm contents with those of another object.
        The latter must be derived of Meow.Parametrization, but
        it may or may not be derived from Grunt.ParameterizationPlus.
        If not, it will copy the parmdefs, but not any parmgroups."""
        
        if trace:
            self.p_display('before p_merge()', full=True)
            ff = getattr(other, 'p_display', None)
            if ff: other.p_display('other', full=True)

        # Merging depends on the parameterization of 'other':
        rr = getattr(other, '_parmdefs', None)
        if isinstance(rr, dict):
            # The other object is derived from Meow.Parameterization

            # Check whether it is derived from Grunt.ParameterizationPlus
            rr = getattr(other, '_parmgroups', None)
            if isinstance(rr, dict):
                # The other object is derived from Grunt.ParameterizationPlus

                # First update the Meow.Parameterization attributes.
                # (This allows a mix between the two frameworks)
                qq = getattr(other, '_parmdefs', None)
                self._parmdefs.update(qq)
                qq = getattr(other, '_parmnodes', dict())
                self._parmnodes.update(qq)

                # Then copy the Grunt.ParameterizationPlus parmgroups:
                # NB: Avoid duplicate parmgroups (solvable and simulated versions
                # of the same Joneset should be compared, rather than merged!).
                for key in rr:
                    if self._parmgroups.has_key(key):
                        s = '** cannot merge duplicate parmgroups: '+key 
                        raise ValueError, s
                    self._parmgroups[key] = rr[key]

            else:
                # The other object is NOT derived from Grunt.ParameterizationPlus
                # Make a single parmgroup from its parmnodes
                # Copy the parmdefs with slightly different names
                self.p_group_define (other.name, tags=None,
                                     descr='copied from Meow.Parameterization')
                rr = self._parmgroups[other.name]
                for key in other._parmdefs:
                    pd = other._parmdefs[key]                 # assume: (value, tags, solvable)
                    newkey = other.name+'_'+key
                    self._parmdefs[newkey] = pd
                    rr['nodes'].append(self._parm(newkey))    # generate a node in self, not other!
                    rr['solvable'].append(pd[2])              # boolean
                    rr['plot_labels'].append(newkey)          # ....?



        if trace:
            self.p_display('after p_merge()', full=True)
        return True



    #===============================================================
    # Convenient access to a list of nodes/subtrees, e.g. for solving
    #===============================================================

    def p_solvable (self, tags=None, groups='*', return_NodeList=True, trace=False):
        """Return a list with the specified selection of solvable MeqParm nodes.
        The nodes may be specified by their tags (n.search) or by parmgroups."""
        return self.p_find_nodes (tags=tags, groups=groups,
                                  return_NodeList=return_NodeList,
                                  solvable=True, trace=trace)


    #----------------------------------------------------------------

    def p_find_nodes (self, tags=None, groups='*', solvable=None,
                      return_NodeList=True, trace=False):
        """Return a list with the specified selection of the nodes (names)
        that are known to this Parameterization object. The nodes may be
        specified by their tags (n.search) or by parmgroups. The defaults are
        tags=None and groups='*', but tags are checked first."""

        if trace:
            print '\n** p_find_nodes(tags=',tags,', groups=',groups,', solvable=',solvable,'):'
        nodes = []
        labels = []
        name = 'parms'

        if tags:
            # A tags specification has precedence:
            tags = _tags2list(tags)
            name = 'tags'
            for k,tag in enumerate(tags):
                name += str(tag)
            if trace:
                print ' -- tags =',tags,' (name=',name,')'
            class_name = None
            if solvable:
                tags.append('solvable')
                class_name = 'MeqParm'
            if trace:
                print ' -- self.ns.Search(',class_name,' tags=',tags,')'
            nodes = self.ns.Search(tags=tags, class_name=class_name)
            for node in nodes:
                labels.append(node.name)

        elif groups:
            # Use the groups specification:
            pg = self.p_find_parmgroups (groups, severe=True)
            name = 'gogs'
            if isinstance(groups,str):
                name += groups
            elif isinstance(groups,(list,tuple)):
                for k,group in enumerate(groups):
                    name += str(group)
            if trace:
                print ' -- groups =',groups,'(name=',name,') -> pg =',pg
            for key in pg:
                rr = self._parmgroups[key]              # convenience
                if not isinstance(solvable, bool):      # solvable not speified
                    nodes.extend(rr['nodes'])           # include all nodes
                    labels.extend(rr['plot_labels'])    # include all 
                else:
                    for k,node in enumerate(rr['nodes']):
                        if rr['solvable'][k]==solvable: # the specified kind
                            nodes.append(node)          # selected nodes only
                            labels.append(rr['plot_labels'][k])       

        if trace:
            for k,node in enumerate(nodes):
                print '  - (',labels[k],'):',str(node)
            print ' ->',len(nodes),'nodes, ',len(labels),'labels'

        # Optionally, return a NodeList object of the selected nodes and their labels
        if return_NodeList:
            nn = NodeList.NodeList(self.ns, name, nodes=nodes, labels=labels)
            if trace: print ' ->',nn.oneliner(),'\n'
            return nn
        else:
            # Otherwise, just return a list of nodes:
            return nodes


    #------------------------------------------------------------------------

    def p_find_parmgroups (self, groups, severe=True, trace=False):
        """Helper function to covert the specified groups (parmgroups or gogs)
        into a list of existing parmgroup names. If severe==True, stop if error.
        """
        # First make sure that the selection is a list (of names):
        if isinstance(groups, str):
            groups = groups.split(' ')                 # make a list from string
        groups = list(groups)                          # make sure of list
        if groups[0]=='*':
            groups = self._parmgroups.keys()           # all parmgroups

        # Make a (unique) list pg of valid parmgroups from the gogs: 
        self._p_make_gogs()
        pg = []
        for key in groups:
            if self._parmgogs.has_key(key):
                for g in self._parmgogs[key]:
                    if not g in pg: pg.append(g)
            elif severe:
                raise ValueError,'** parmgroup not recognised: '+key
        return pg


    #===============================================================
    # Parmgogs: Groups of parmgroups
    #===============================================================

    def p_gogs (self):
        """Return the list of available groups of parmgroups (gogs).
        These are used in finding groups, e.g. for solving."""
        return self._p_make_gogs().keys()

    def _p_make_gogs (self):
        """Derive a dict of named groups of parmgroups from the tags
        of the various parmgroups. These may be used to select groups,
        e.g. in .solvable()."""
        gg = dict()
        keys = self._parmgroups.keys()
        for key in keys:
            tags = self._parmgroups[key]['tags']
            for tag in tags:
                gg.setdefault(tag,[])
                if not key in gg[tag]:
                    gg[tag].append(key)
        self._parmgogs = gg
        return self._parmgogs



    #===============================================================
    # Methods using NodeLists:
    #===============================================================

    def p_NodeList (self, parmgroup):
        """Helper function to get a NodeList object for the specified parmgroup.
        In order to avoid duplication, the created NodeList object are reused.
        """
        key = self.p_find_parmgroups (parmgroup, severe=True)[0]
        print 'key=',key,key[0]
        if not self._parmNodeList.has_key(key):
            nodes = self._parmgroups[key]['nodes']
            labels = self._parmgroups[key]['plot_labels']
            nn = NodeList.NodeList(self.ns, key, nodes=nodes, labels=labels)
            self._parmNodeList[key] = nn
        return self._parmNodeList[key]

    #---------------------------------------------------------------

    def _p_bundle_of_bundles (self, bb, name=None, qual=None, show=False):
        """Helper function to bundle a list of parmgroup bundles"""

        if len(bb)==0:
            return None
        elif len(bb)==1:
            qnode = bb[0]
        else:
            qnode = self.ns[name](qual)
            if not qnode.initialized():                        #......!!?
                qnode << Meq.Composer(children=bb)

        # Finished: Return the root-node of the bundle subtree:
        if show: display.subtree(qnode, show_initrec=False)
        return qnode


    #---------------------------------------------------------------

    def p_bundle (self, parmgroup='*', combine='Add',
                  bookpage=True, folder=None, show=False):
        """Bundle the nodes in the specified parmgroup(s) by applying the
        specified combine-operation (default='Add') to them. Return the
        root node of the resulting subtree. Make bookpages for each parmgroup.
        """
        pg = self.p_find_parmgroups (parmgroup, severe=True)
        if folder==None:
            if len(pg)>1: folder = 'params_'+self.name
        
        bb = []
        for key in pg:
            nn = self.p_NodeList(key)
            bb.append(nn.bundle(combine=combine, bookpage=bookpage, folder=folder))
        return self._p_bundle_of_bundles (bb, name='p_bundle',
                                          qual=parmgroup, show=show)

    #---------------------------------------------------------------

    def p_inspector (self, parmgroup='*', show=False):
        """Visualize the nodes in the specified parmgroup(s) in a separate
        'inspector' per parmgroup. Return the root node of the resulting subtree.
        Make bookpages for each parmgroup.
        """
        pg = self.p_find_parmgroups (parmgroup, severe=True)
        bb = []
        for key in pg:
            print 'key=',key
            nn = self.p_NodeList(key)
            bb.append(nn.inspector(bookpage=True))
        return self._p_bundle_of_bundles (bb, name='p_inspector',
                                          qual=parmgroup, show=show)

    #---------------------------------------------------------------

    def p_compare (self, parmgroup, other, show=False):
        """Compare the nodes of a parmgroup with the corresponding ones
        of the given (and assumedly commensurate) parmgroup (other).
        The results are visualized in various helpful ways.
        The rootnode of the comparison subtree is returned.
        """
        self.p_has_group (parmgroup, severe=True)
        self.p_has_group (other, severe=True)
        nn1 = self.p_NodeList(parmgroup)
        nn2 = self.p_NodeList(other)
        qnode = nn1.compare(nn2, bookpage=True, show=show)
        return qnode




    #===============================================================
    # Some extra functionality for Meow.Parameterization 
    #===============================================================

    def p_modify_default (self, name):
        """Modify the default value of the specified parm"""
        # Not yet implemented..... See Expression.py
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
    
def _simul_subtree(rr, qnode, default=None, deviation=None,
                   tags=[], show=False, trace=False):
    """Return the root node of a subtree that simulates the
    behaviour of a MeqParm."""

    if trace: print '\n** _simul_subtree(',str(qnode),'):'
    
    # The deviation from the default value is described by a math expression.
    # The default (rr) values may be overridden.
    simexpr = str(default or rr['default'])+'+'+(deviation or rr['deviation'])
    if trace: print '    ',simexpr
    
    # Make a MeqFunctional node from the given expression
    Ekey = Expression.Expression(qnode, qnode.name, expr=simexpr)
    node = Ekey.MeqFunctional()

    if trace: print '  -> node =',str(node)

    # Make a root node with the correct name (qnode) and tags:
    ptags = deepcopy(tags)
    if not 'simul' in ptags: ptags.append('simul')
    qnode << Meq.Identity(node, tags=ptags)
    if trace: print '  -> qnode =',str(qnode)
    if show: display.subtree(qnode)
    return qnode

#----------------------------------------------------------------------------
      
    
    





#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================

def _define_forest(ns):

    # cc = [ns.dummy<<45]
    cc = []

    pp1 = ParameterizationPlus(ns, 'GJones',
                               # kwquals=dict(tel='WSRT', band='21cm'),
                               quals='3c84')
    pp1.p_display('initial')

    if 1:
        pp1.p_group_define('Gphase', tiling=3, simul=True)
        pp1.p_group_define('Ggain', default=1.0, freq_deg=2)

    if 1:
        pp1.p_group_create_member('Gphase', 1)
        pp1.p_group_create_member('Gphase', 2.1, value=(ns << -89))
        pp1.p_group_create_member('Gphase', 2, value=34)
        pp1.p_group_create_member('Gphase', 3, tiling=5, simul=False)
        pp1.p_group_create_member('Gphase', 7, freq_deg=2)

    if 1:
        pp1.p_group_create_member('Ggain', 7, freq_deg=6)
        pp1.p_group_create_member('Ggain', 4, time_deg=3)

    if 0:
        node = pp1.p_bundle(show=True)
        cc.append(node)

    if 1:
        node = pp1.p_inspector()
        cc.append(node)

    if 1:
        nn = pp1.p_solvable(groups='GJones')
        nn.display('solvable')
        nn.bookpage(select=4)
        

    pp1.p_display('final', full=True)

    ns.result << Meq.Composer(children=cc)
    return True



#---------------------------------------------------------------

def _tdl_job_2D_tf (mqs, parent):
    """Execute the forest with a 2D request (freq,time), starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,0,2000)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=100)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       










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
        pp1.p_group_define('Gphase', tiling=3, simul=True)
        pp1.p_group_define('Ggain', default=1.0, freq_deg=2, simul=False)

    if 1:
        pp1.p_group_create_member('Gphase', 1)
        pp1.p_group_create_member('Gphase', 2.1, value=(ns << -89))
        pp1.p_group_create_member('Gphase', 2, value=34)
        pp1.p_group_create_member('Gphase', 3, tiling=5, simul=False)
        pp1.p_group_create_member('Gphase', 7, freq_deg=2)

    if 1:
        pp1.p_group_create_member('Ggain', 7, freq_deg=6)
        pp1.p_group_create_member('Ggain', 4, time_deg=3)

    if 0:
        pp1.p_bundle(show=True)

    pp1.p_display('final', full=True)

    if 0:
        print dir(pp1)
        print getattr(pp1,'_parmgroup',None)

    if 0:
        print 'ns.Search(tags=Gphase):',ns.Search(tags='Gphase')
        print 'pp1.ns.Search(tags=Gphase):',pp1.ns.Search(tags='Gphase')


    if 0:
        pp1.p_solvable()
        pp1.p_solvable(groups='Gphase', trace=True)
        pp1.p_solvable(groups=['Ggain'], trace=True)
        pp1.p_solvable(groups=['GJones'], trace=True)
        pp1.p_solvable(groups=['Gphase','Ggain'], trace=True)
        pp1.p_solvable(groups=pp1.p_groups(), trace=True)
        pp1.p_solvable(groups=pp1.p_gogs(), trace=True)
        # pp1.p_solvable(groups=['Gphase','xxx'], trace=True)

    if 0:
        pp1.p_solvable(tags='Gphase', trace=True)
        pp1.p_solvable(tags=['Gphase','Ggain'], trace=True)
        pp1.p_solvable(tags=['Gphase','GJones'], trace=True)
        pp1.p_solvable(tags=['Gphase','Dgain'], trace=True)

    if 1:
        solvable = True
        pp1.p_find_nodes(groups='GJones', solvable=solvable, trace=True)
        pp1.p_find_nodes(groups=pp1.p_gogs(), solvable=solvable, trace=True)

    if 0:
        pp2 = ParameterizationPlus(ns, 'DJones', quals='CasA')
        pp2.p_group_define('Ddell')
        pp2.p_group_define('Ddang')
        pp2.p_group_create_member('Ddang', 1)
        pp2.p_group_create_member('Ddell', 7)
        pp2.p_display(full=True)
        if 1:
            pp1.p_merge(pp2, trace=True)

    if 0:
        e0 = Expression.Expression(ns, 'e0', '{a}+{b}*[t]-{e}**{f}+{100~10}', simul=False)
        e0.display()
        if 1:
            pp3 = ParameterizationPlus(ns, 'e0', merge=e0)
        if 0:
            pp1.p_merge(e0, trace=True)


#===============================================================

