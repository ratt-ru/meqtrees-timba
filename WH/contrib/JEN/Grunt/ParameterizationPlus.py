# file: ../Grunt/ParameterizationPlus.py

# History:
# - 26may2007: creation 

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

    def p_has_group (self, key, severe=True):
        """Test whether it has a parmgroup of this name (key).
        If severe==True, raise a ValueError if it does not"""
        if self._parmgroups.has_key(key): return True
        if severe:
            s = '** parmgroup not recognized: '+str(key)
            raise ValueError, s
        return False

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
                rr = getattr(other, '_parmdefs', None)
                self._parmdefs.update(rr)
                rr = getattr(other, '_parmnodes', dict())
                self._parmnodes.update(rr)

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

    def p_solvable (self, tags=None, parmgroups='*', trace=False):
        """Return a list with the specified selection of solvable MeqParm nodes.
        The nodes may be specified by their tags (n.search) or by parmgroups."""
        return self.p_find_nodes (tags=tags, parmgroups=parmgroups,
                                  solvable=True, trace=trace)


    #----------------------------------------------------------------

    def p_find_nodes (self, tags=None, parmgroups='*',
                      solvable=None, trace=False):
        """Return a list with the specified selection of the nodes (names)
        that are known to this Parameterization object. The nodes may be
        specified by their tags (n.search) or by parmgroups. The defaults are
        tags=None and parmgroups='*', but tags are checked first."""

        if trace: print '\n** p_find_nodes(tags=',tags,', pg=',parmgroups,', solvable=',solvable,'):'
        nodes = []
        labels = []
        if tags:
            tags = _tags2list(tags)
            class_name = None
            if solvable:
                tags.append('solvable')
                class_name = 'MeqParm'
            if trace:
                print ' -- self.ns.Search(',class_name,' tags=',tags,')'
            nodes = self.ns.Search(tags=tags, class_name=class_name)
            for node in nodes:
                labels.append(node.name)

        elif parmgroups:
            pg = self.p_check_parmgroups (parmgroups, severe=True)
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
            print ' ->',len(nodes),'nodes, ',len(labels),'labels\n'
        return nodes

    #------------------------------------------------------------------------

    def p_check_parmgroups (self, select, severe=True, trace=False):
        """Helper function to covert the selection (parmgroups) into a list of
        existing parmgroup names. If severe==True, stop if error."""
        # First make sure that the selection is a list (of parmgroup names):
        if isinstance(select, str):
            select = select.split(' ')                 # make a list from string
        select = list(select)                          # make sure of list
        if select[0]=='*':
            select = self._parmgroups.keys()           # all parmgroups
        # Check the existence of the selected parmgroups:
        pg = []
        for key in select:
            if self._parmgroups.has_key(key):
                pg.append(key)
            elif severe:
                raise ValueError,'** parmgroup not recognised: '+key
        return pg


    #===============================================================
    # Parmgroup subtrees:
    #===============================================================

    def p_bundle (self, parmgroup='*', combine='Add',
                  bookpage=True, show=False):
        """Bundle the nodes in the specified parmgroup(s) by applying the
        specified combine-operation (default='Add') to them. Return the
        root node of the resulting subtree. Make bookpages for each parmgroup."""

        pg = self.p_check_parmgroups (parmgroup, severe=True)
        bb = []
        for key in pg:
            nodes = self._parmgroups[key]['nodes']
            quals = [combine+'_'+str(len(nodes)),key]
            qnode = self.ns['p_bundle'](*quals)
            if not qnode.initialized():
                qnode << getattr(Meq,combine)(children=nodes)
            bb.append(qnode)
            if bookpage:
                JEN_bookmarks.create(qnode, recurse=1, page=qnode.name)

        # Bundle the parmgroup bundles, if necessary:
        if len(bb)==0:
            return None
        elif len(bb)==1:
            qnode = bb[0]
        else:
            qnode = self.ns['p_bundle'](parmgroup)
            if not qnode.initialized():
                qnode << Meq.Composer(children=bb)

        # Finished: Return the root-node of the bundle subtree:
        if show: display.subtree(qnode, show_initrec=False)
        return qnode


    #===============================================================
    # Visualization:
    #===============================================================

    def p_inspector (self, parmgroup='*'):
        """Visualize the nodes in the specified parmgroup(s) in a separate
        'inspector' per parmgroup. Return the root node of the resulting subtree.
        Make bookpages for each parmgroup."""

        pg = self.p_check_parmgroups (parmgroup, severe=True)
        bb = []
        for key in pg:
            quals = [key]
            qnode = self.ns['p_inspector'](*quals)
            if not qnode.initialized():
                nodes = self._parmgroups[key]['nodes']
                labels = self._parmgroups[key]['plot_labels']
                qnode << Meq.Composer(children=nodes,
                                      plot_label=labels)
            bb.append(qnode)
            JEN_bookmarks.create(qnode, key, page='p_inspector_'+self.name,
                                 viewer='Collections Plotter')

        # Make a subtree of inspectors, and return the root node:
        if len(bb)==0:
            return None
        elif len(bb)==1:
            qnode = bb[0]
        else:
            qnode = self.ns['p_inspector'](parmgroup)
            if not qnode.initialized():
                qnode << Meq.Composer(children=bb)
        return qnode

    #---------------------------------------------------------------

    def p_compare (self, parmgroup, with, trace=False):
        """Compare the nodes of a parmgroup with the corresponding ones
        of the given parmgroup (with)."""

        self.p_has_group (parmgroup, severe=True)
        # .... unfinished ....
        
        return True




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
      
    
    





#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================

def _define_forest(ns):

    # cc = [ns.dummy<<45]
    cc = []

    pp1 = ParameterizationPlus(ns, 'G',
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
        pp1.p_solvable(parmgroups='Gphase')
        pp1.p_solvable(parmgroups=['Ggain'])
        pp1.p_solvable(parmgroups=['Gphase','Ggain'])
        pp1.p_solvable(parmgroups=pp1.p_groups())
        # pp1.p_solvable(parmgroups=['Gphase','xxx'])

    if 0:
        pp1.p_solvable(tags='Gphase', trace=True)
        pp1.p_solvable(tags=['Gphase','Ggain'], trace=True)
        pp1.p_solvable(tags=['Gphase','GJones'], trace=True)
        pp1.p_solvable(tags=['Gphase','Dgain'], trace=True)

    if 0:
        pp1.p_find_nodes(solvable=True)

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

