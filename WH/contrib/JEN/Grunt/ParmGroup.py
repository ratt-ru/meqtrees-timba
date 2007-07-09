# file: ../Grunt/ParmGroup.py

# History:
# - 09jul2007: creation (from ParameterizationPlus.py)

# Description:

# The Grunt ParmGroup class is derived from the Meow Parameterization class.
# It adds some extra functionality for a group of similar parms, which may
# find their way into the more official Meow system eventually.
# The ParmGroup class is used by the Grunt.ParameterizationPlus class.

# Compatibility:
# - The Grunt.ParmGroup class is derived from Meow.Parameterization


#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

import Meow

from Timba.Contrib.JEN.Grunt import NodeList
from Timba.Contrib.JEN.Grunt import display
from Timba.Contrib.JEN.Expression import Expression

from copy import deepcopy

#======================================================================================

class ParmGroup (Meow.Parameterization):
    """The Grunt ParmGroup class is derived from the Meow Parameterization class.
    It adds some extra functionality for a group of similar parms, which may find
    their way into the more official Meow system eventually."""

    def __init__(self, ns=None, name=None, quals=[], kwquals={}, namespace=None,
                 tags=None,
                 descr='<descr>', unit=None,
                 default=0.0, constraint=None,
                 simul=False, deviation=None,
                 tiling=None, time_deg=0, freq_deg=0,
                 # constrain_min=0.1, constrain_max=10.0,
                 rider=None, override=None,
                 **kw):

        # Scopify ns, if necessary:
        if is_node(ns):
            ns = ns.QualScope()        

        # Make sure that there is a nodescope (Required by Meow.Parameterization)
        if ns==None:
            ns = NodeScope()

        self.tdloption_namespace = namespace       # just how standard is this name?
        self._TDLCompileOptionsMenu = None   
        self._TDLCompileOption = dict()   

        #------------------------------------
        # NB: What about dropping quals/kwquals completely, since these may be
        #     introduced by passing ns as a node, rather than a nodescope.
        #     See also the function .nodescope()
        # Eventually.... (perverse coupling)? 
        #------------------------------------

        name = str(name)                           # just in case....

        # Make a little more robust 
        quals = self.quals2list(quals)

        # Avoid duplication of qualifiers:
        if ns:
            qq = ns['dummy'].name.split(':')       # make a list (qq) of qualifiers
            for q in qq:
                if q in quals: quals.remove(q)
            if name in quals: quals.remove(name)

        Meow.Parameterization.__init__(self, ns, name,
                                       quals=quals,
                                       kwquals=kwquals)
        # Initialize local data:
        self._NodeList = None

        #------------------------------------------------------------------

        # The node tags may be used for finding nodes in ns:
        tags = self.tags2list(tags)
        if True:
            if not self.name in tags: tags.append(self.name)      # <----- ??
        # NB: What about a qualifier like '3c84'?
        # qnode = self.ns0[key]

        # If simul==True, the deviation from the default value
        # (e.g. as a function of time [t] and/or freq [f]), is
        # given by a math Expression:
        if not isinstance(deviation, str):
            # deviation = '{0.01~0.001}*sin(2*pi*([t]/{500~50}+{0~1}))'
            deviation = self.deviation_expr(ampl='{0.01~10%}', Psec='{500~10%}', PHz=None)

        # It is possible to override values via this dict.....
        # This requires a little thought....
        if isinstance(override, dict):
            pass

        # Create the group definition:
        self._default = default
        self._tags = tags
        self._simul = simul
        self._deviation = deviation
        self._constraint = constraint
        self._descr = descr
        self._unit = unit
        self._tiling = tiling
        self._time_deg = time_deg
        self._freq_deg = freq_deg
        self._rider = rider
        self._nodes = []
        self._solvable = []
        self._plot_labels = []

        return None


    #---------------------------------------------------------------

    def len(self):
        """Return the number of group members (nodes)"""
        return len(self._nodes)

    #---------------------------------------------------------------

    def nodescope (self, ns=None):
        """Get/set the internal nodescope (can also be a node)"""
        if is_node(ns):
            self.ns = ns.QualScope()        
        elif ns:
            self.ns = ns
        return self.ns


    def namespace(self, prepend=None, append=None):
        """Return the namespace string (used for TDL options etc).
        If either prepend or apendd strings are defined, attach them.
        NB: Move to the ParmGroup class?
        """
        if prepend==None and append==None:
            return self.tdloption_namespace                    # just return the namespace
        # Include the namespace in a string:
        ss = ''
        if isinstance(prepend, str): ss = prepend+' '
        if self.tdloption_namespace:
            ss += '{'+str(self.tdloption_namespace)+'}'
        if isinstance(append, str): ss += ' '+append
        return ss
    
    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = 'Grunt.ParmGroup:'
        ss += ' '+str(self.name)
        ss += '  ('+str(self.ns['<>'].name)+')'
        ss += '  (n='+str(self.len())+')'
        return ss


    def display(self, txt=None, full=False, recurse=3):
        """Print a summary of this object"""
        print ' '
        print '** '+self.oneliner()
        if txt: print '  * (txt='+str(txt)+')'
        rr = dict(default=self._default,
                  tags=self._tags,
                  simul=self._simul,
                  constraint=self._constraint,
                  descr=self._descr,
                  unit=self._unit,
                  tiling=self._tiling,
                  time_deg=self._time_deg,
                  freq_deg=self._freq_deg)
        print '  * '+str(rr)
        #...............................................................
        print '  * group members ('+str(len(self._nodes))+'): (solvable, plot_label, node)'
        for k in range(self.len()):
            s = ''
            s += '  '+str(self._solvable[k])
            s += '  '+str(self._plot_labels[k])
            s += '  '+str(self._nodes[k])
            print '    - '+s
        print '  * Deviation: '+str(self._deviation)
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
        if self._NodeList:
            print '  * NodeList object: '+self._NodeList.oneliner()
        else:
            print '  * NodeList object: '+str(self._NodeList) 
        #...............................................................
        print '  * TDLCompileOptionsMenu: '+str(self._TDLCompileOptionsMenu)
        for key in self._TDLCompileOption.keys():
            oo = self._TDLCompileOption[key]
            if getattr(oo, 'value', None):
                print '    - '+str(key)+' = '+str(self._TDLCompileOption[key].value)
            else:
                print '    - '+str(key)+': '+str(self._TDLCompileOption[key])
       #...............................................................
        print '**\n'
        return True



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


    def create_member (self, quals=[], kwquals={},
                       value=None, tags=[], solvable=True,            # may override
                       simul=None, default=None, deviation=None,      # may override
                       tiling=None, time_deg=0, freq_deg=0):          # may override for Meow.Parm
        """Create the specified (quals, kwquals) member of the parmgroup.
        By default, the common attrbutes of the group will be used
        to create the relevant Meow.Parm or simulation subtree, but some of
        these attributes may be overridden here...."""

        # Make the qualified node (qnode) for the new group member,
        # and check whether it already exists: 
        quals = self.quals2list(quals)
        if not isinstance(simul, bool):                # simul not explicitly specfied
             simul = self._simul                       # use the group default

        # Make qnode and nodename
        if simul:
            # s = (self.ns.dummy).name.split(':')        # make a list of current qualifiers
            # if not 'simul' in s:                       #   if necessary
            #     quals.append('simul')                  #     add 'simul' qualifier
            # qnode = self.ns[self.name](*quals)(**kwquals)    # qualified node (stub)       
            qnode = self.ns['simul'](*quals)(**kwquals)    # qualified node (stub)       
            nodename = qnode.name                      # used in ._add_parm()
        else:
            # qnode = self.ns0[self.name](*quals)(**kwquals)   # qualified node (stub)       
            # nodename = self.ns[self.name](*quals)(**kwquals).name
            qnode = self.ns0['parm'](*quals)(**kwquals)   # qualified node (stub)       
            nodename = self.ns['parm'](*quals)(**kwquals).name

        if qnode.initialized():
            s = '** parmgroup member already exists: '+str(qnode)
            raise ValueError,s

        # Make the plot_label:
        plot_label = self.name
        for q in quals: plot_label += '_'+str(q)
        # kwquals too?

        # Any extra tags are appended to the default (rr) ones.....?!
        ptags = self.tags2list(tags)
        ptags.extend(self._tags)

        # Use the Meow Parm/Parameterization mechanism as much as possible:
        node = None
        if simul:
            # Return the root node of a subtree that simulates the MeqParm
            # NB: The default (rr) default and deviation may be overridden here
            rootnode = self._simul_subtree(qnode, default=default,
                                           deviation=deviation, tags=ptags)
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
            mparm = Meow.Parm(value=(value or self._default),
                              tiling=(tiling or self._tiling),
                              time_deg=(time_deg or self._time_deg),
                              freq_deg=(freq_deg or self._freq_deg),
                              tags=[])
            self._add_parm(nodename, mparm, tags=ptags, solvable=solvable)
            node = self._parm(nodename, nodename=qnode.name)

        # Update the parmgroup with the new member node:
        self._nodes.append(node)
        self._plot_labels.append(plot_label)
        self._solvable.append(solvable)

        # Return the new member node:
        return node


    #-------------------------------------------------------------------

    def deviation_expr (self, ampl='{0.01~10%}', Psec='{500~10%}', PHz=None):
        """Helper function to make a standard deviation expression.
        All arguments must be strings of the form {<value>~<stddev>}.
        The <stddev> is used to generate different values around <value>
        for each member of the group (see .group_create_member())."""
        s = ampl
        if isinstance(Psec,str):
            s += ' * sin(2*pi*([t]/'+Psec+'+{0~1}))'
        if isinstance(PHz,str):
            s += ' * sin(2*pi*([f]/'+PHz+'+{0~1}))'
        return s

    #--------------------------------------------------------------------

    def _simul_subtree (self, qnode, default=None, deviation=None,
                        tags=[], show=False, trace=False):
        """Return the root node of a subtree that simulates the
        behaviour of a MeqParm."""

        if trace: print '\n** _simul_subtree(',str(qnode),'):'
        
        # The deviation from the default value is described by a math expression.
        # The default (rr) values may be overridden.
        simexpr = str(default or self._default)+'+'+(deviation or self._deviation)
        if trace: print '    ',simexpr
    
        # Make a MeqFunctional node from the given expression
        Ekey = Expression.Expression(qnode, qnode.basename, expr=simexpr)
        node = Ekey.MeqFunctional()

        if trace: print '  -> node =',str(node)

        # Make a root node with the correct name (qnode) and tags:
        ptags = deepcopy(tags)
        if not 'simul' in ptags: ptags.append('simul')
        qnode << Meq.Identity(node, tags=ptags)
        if trace: print '  -> qnode =',str(qnode)
        if show: display.subtree(qnode)
        return qnode



    #===================================================================
    # TDLOptions:
    #===================================================================

    def TDLCompileOptionsMenu (self, show=True):
        """Generic function for interaction with its TDLCompileOptions menu.
        The latter is created (once), by calling the specific function.
        .TDLCompileOptions(), which may be re-implemented by derived classes.
        The 'show' argument may be used to show or hide the menu. This can be done
        repeatedly, without duplicating the menu.
        """
        if not self._TDLCompileOptionsMenu:        # create the menu only once
            oolist = self.TDLCompileOptions()
            prompt = self.namespace(prepend='options for ParmGroup: '+self.name)
            self._TDLCompileOptionsMenu = TDLCompileMenu(prompt, *oolist)

        # Show/hide the menu as required (can be done repeatedly):
        self._TDLCompileOptionsMenu.show(show)
        return self._TDLCompileOptionsMenu

    #..................................................................


    def TDLCompileOptions (self):
        """Define a list of TDL options that control the group parameters.
        """
        oolist = []

        #---------------------------------
        # Solving options (simul=False):

        key = '_default'
        if not self._TDLCompileOption.has_key(key):
            doc = 'MeqParm default value'
            self._TDLCompileOption[key] = TDLOption(key, 'default value',
                                                    [getattr(self, key)],
                                                    more=float, doc=doc, namespace=self)
        oolist.append(self._TDLCompileOption[key])

        key = '_tiling'
        if not self._TDLCompileOption.has_key(key):
            doc = 'Nr of time-slots per subtile solution. None means all.'
            self._TDLCompileOption[key] = TDLOption(key, '(time) sub-tile size',
                                                    [getattr(self, key),1,2,4,8,16,None],
                                                    more=int, doc=doc, namespace=self)
        oolist.append(self._TDLCompileOption[key])

        key = '_time_deg'
        if not self._TDLCompileOption.has_key(key):
            doc = 'Degree of time-polynomial to be solved for.'
            self._TDLCompileOption[key] = TDLOption(key, 'time deg. of sol.',
                                                    [getattr(self, key),0,1,2,3,4],
                                                    more=int, doc=doc, namespace=self)
        oolist.append(self._TDLCompileOption[key])

        key = '_freq_deg'
        if not self._TDLCompileOption.has_key(key):
            doc = 'Degree of freq-polynomial to be solved for.'
            self._TDLCompileOption[key] = TDLOption(key, 'freq deg. of sol.',
                                                    [getattr(self, key),0,1,2,3,4],
                                                    more=int, doc=doc, namespace=self)
        oolist.append(self._TDLCompileOption[key])

        if False:
            key = '_constraint'
            if not self._TDLCompileOption.has_key(key):
                doc = 'Constraint to be used for the solution.'
                opt = [getattr(self, key), 'sum=0.0', 'prod=1.0', None],
                self._TDLCompileOption[key] = TDLOption(key, 'sol. constraint', opt,
                                                        more=str, doc=doc, namespace=self)
            oolist.append(self._TDLCompileOption[key])

        #---------------------------------
        # Simulation options (simul=True):

        key = '_deviation'
        if not self._TDLCompileOption.has_key(key):
            doc = '(simul) deviation from default value'
            self._TDLCompileOption[key] = TDLOption(key, 'deviation',
                                                    [getattr(self, key)],
                                                    more=str, doc=doc, namespace=self)
            self._TDLCompileOption[key].set_custom_value(getattr(self, key),
                                                         select=True, save=True)
        oolist.append(self._TDLCompileOption[key])

        #---------------------------------
        # Do this one last (because of the .when_changed() callback):
        key = '_simul'
        if not self._TDLCompileOption.has_key(key):
            doc = 'If True, replace the MeqParms with subtrees that simulate them'
            opt = [self._simul, not self._simul]
            opt = self._simul
            self._TDLCompileOption[key] = TDLOption(key, 'simulate MeqParms',
                                                    opt, doc=doc, namespace=self)
            self._TDLCompileOption[key].when_changed(self._callback_simul)
        oolist.append(self._TDLCompileOption[key])


        #---------------------------------
        # Read the (saved) value from the .tdl.conf file: 
        self._read_TDLCompileOptions(trace=True)

        # Finished: Return a list of options:
        return oolist


    #.....................................................................

    def _callback_simul(self, simul):
        """Function called whenever TDLOption simul changes"""
        # If simul, show the similation options
        self._TDLCompileOption['_deviation'].show(simul)
        # If not simul, show the solving options:
        self._TDLCompileOption['_default'].show(not simul)
        self._TDLCompileOption['_tiling'].show(not simul)
        self._TDLCompileOption['_time_deg'].show(not simul)
        self._TDLCompileOption['_freq_deg'].show(not simul)
        # self._TDLCompileOption['_constraint'].show(not simul)
        return True
        

    #.....................................................................

    def _read_TDLCompileOptions(self, trace=True):
        """Helper function to read TDLCompileOptions"""
        if trace:
            print '\n** _read_TDLCompileOptions:'
        keys = self._TDLCompileOption.keys()
        for key in keys:
            was = getattr(self,key)
            new = self._TDLCompileOption[key].value
            setattr(self, key, new)
            if trace: print ' -',key,':',was,'->',getattr(self,key)
        if trace: print
        return True
        


    #===============================================================
    # Convenient access to a list of nodes/subtrees, e.g. for solving
    #===============================================================

    def solvable (self, tags=None, return_NodeList=True, trace=False):
        """Return a list with the specified selection of solvable MeqParm nodes.
        The nodes may be specified by their tags (n.search) or by parmgroups."""
        return self.find_nodes (tags=tags, solvable=True,
                                return_NodeList=return_NodeList,
                                trace=trace)


    #----------------------------------------------------------------

    def find_nodes (self, tags=None, solvable=None,
                      return_NodeList=True, trace=False):
        """Return a list with the specified selection of the nodes (names)
        that are known to this parmgroup. The nodes may be specified by their
        tags (n.search) or by parmgroups. The defaults are
        tags=None and groups='*', but tags are checked first."""

        if trace:
            print '\n** find_nodes(tags=',tags,', solvable=',solvable,'):'
        nodes = []
        labels = []
        name = 'parms'

        if tags:
            # A tags specification has precedence:
            tags = self.tags2list(tags)
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

        elif not isinstance(solvable, bool):            # solvable not specified
                nodes.extend(self._nodes)               # include all nodes
                labels.extend(self._plot_labels)        # include all 

        else:
            for k,node in enumerate(self._nodes):
                if self._solvable[k]==solvable:         # the specified kind
                    nodes.append(node)                  # selected nodes only
                    labels.append(self._plot_labels[k])       

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



    #===============================================================
    # Methods using NodeList objects:
    #===============================================================

    def NodeList (self, color='blue', style='diamond'):
        """Helper function to get a NodeList object for the members of the parmgroup.
        In order to avoid duplication, an already created NodeList objects is
        reused....(!?)"""
        if not self._NodeList:
            nn = NodeList.NodeList(self.ns, self.name,
                                   nodes=self._nodes,
                                   labels=self._plot_labels,
                                   color=color, style=style)
            self._NodeList = nn
        return self._NodeList

    #---------------------------------------------------------------

    def compare (self, other, show=False):
        """Compare the nodes of this parmgroup with the corresponding ones
        of the given (and assumedly commensurate) parmgroup (other).
        The results are visualized in various helpful ways.
        The rootnode of the comparison subtree is returned.
        """
        nn1 = self.NodeList()
        nn2 = other.NodeList()
        qnode = nn1.compare(nn2, bookpage=True, show=show)
        return qnode


    #---------------------------------------------------------------

    def bundle (self, combine='Composer',
                bookpage=True, folder=None, show=False):
        """Bundle the nodes in the specified parmgroup by applying the
        specified combine-operation (default='Add') to them. Return the
        root node of the resulting subtree. Make a bookpage if required.
        """
        nn = self.NodeList()
        bundle = nn.bundle(combine=combine,
                           bookpage=bookpage, folder=folder,
                           show=show)
        return bundle


    #---------------------------------------------------------------

    def plot_rvsi (self, bookpage=True, folder=None, show=False):
        """Make a rvsi plot of the parmgroup. Return the root node of
        the resulting subtree. Make a bookpage if required."""
        if bookpage:
            if not isinstance(bookpage, str):
                bookpage = 'plot_rvsi_'+self.name
        nn = self.NodeList()
        rvsi = nn.plot_rvsi(bookpage=bookpage, folder=folder,
                            xlabel=self.name, ylabel='stddev',
                            show=show)
        return rvsi
    
    #---------------------------------------------------------------

    def plot_spectra (self, bookpage=True, folder=None, show=False):
        """Make a spectra plot of the parmgroup. Return the root node of
        the resulting subtree. Make a bookpage if required."""
        if bookpage:
            if not isinstance(bookpage, str):
                bookpage = 'plot_spectra_'+self.name
        nn = self.NodeList()
        spectra = nn.plot_spectra(bookpage=bookpage, folder=folder,
                                  xlabel=self.name, ylabel='stddev',
                                  show=show)
        return spectra
    
    #---------------------------------------------------------------

    def plot_timetracks (self, bookpage=True, folder=None, show=False):
        """Visualize the nodes in the parmgroup in an 'inspector' plot
        (time-tracks). Return the root node of the resulting subtree.
        Make a bookpages if required."""
        if bookpage:
            if not isinstance(bookpage, str):
                bookpage = 'plot_timetracks_'+self.name
        nn = self.NodeList()
        tt = nn.plot_timetracks (bookpage=bookpage, folder=folder,
                                 show=show)
        return tt


    #===============================================================
    # Some useful helper functions (available to all derived classes)
    #===============================================================

    def tags2list (self, tags):
        """Helper function to make sure that the given tags are a list"""
        if tags==None: return []
        if isinstance(tags, (list, tuple)): return list(tags)
        if isinstance(tags, str): return tags.split(' ')
        s = '** cannot convert tag(s) to list: '+str(type(tags))+' '+str(tags)
        raise TypeError, s

    def quals2list (self, quals):
        """Helper function to make sure that the given quals are a list"""
        if quals==None: return []
        if isinstance(quals, (list,tuple)): return list(quals)
        if isinstance(quals, str): return quals.split(' ')
        return [str(quals)]

    #----------------------------------------------------------------

    def get_quals (self, merge=None, remove=None):
        """Helper function to get a list of the current nodescope qualifiers"""
        quals = (self.ns.dummy).name.split(':')
        quals.remove(quals[0])
        if isinstance(merge,list):
            for q in merge:
                if not q in quals:
                    quals.append(q)
        if isinstance(remove,list):
            for q in remove:
                if q in quals:
                    quals.remove(q)
        return quals



    #===============================================================
    # Some extra functionality for Meow.Parameterization 
    #===============================================================

    def modify_default (self, key):
        """Modify the default value of the specified (key) parm"""
        # Not yet implemented..... See Expression.py
        return False







    
      
    
    





#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================

if 0:
    pg = ParmGroup (name='Gphase', tiling=3, simul=True, namespace='fff')
    pg.TDLCompileOptionsMenu()


def _define_forest(ns):

    cc = []

    pg.nodescope(ns)                          # <---------- !!

    if 1:
        pg.create_member(1)
        pg.create_member(2.1, value=(ns << -89))
        pg.create_member(2, value=34)
        pg.create_member(3, tiling=5, simul=False)
        pg.create_member(7, freq_deg=2)

    if 1:
        cc.append(pg.bundle(show=True))
        cc.append(pg.plot_timetracks(show=True))
        cc.append(pg.plot_rvsi(show=True))
        cc.append(pg.plot_spectra(show=True))

    if 0:
        nn = pg.solvable(tags='GJones')
        nn.display('solvable')
        nn.bookpage(select=4)
        

    pg.display('final', full=True)

    print '\n** cc =',cc
    for c in cc:
        print '  - ',str(c)
    if len(cc)==0: cc.append(ns.dummy<<1.1)
    ns.result << Meq.Composer(children=cc)
    print '->',str(ns.result)
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
        pg = ParmGroup(ns, 'Gphase', tiling=3, simul=False)
        # pg = ParmGroup(ns, 'Ggain', default=1.0, freq_deg=2, simul=False)
        pg.display('initial')

    if 1:
        pg.create_member(1)
        pg.create_member(2.1, value=(ns << -89))
        pg.create_member(2, value=34)
        pg.create_member(3, tiling=5, simul=False)
        pg.create_member(7, freq_deg=2)

    if 0:
        pg.bundle(show=True)

    if 0:
        pg.plot_rvsi(show=True)

    if 0:
        pg.plot_spectra(show=True)

    if 0:
        pg.plot_timetracks(show=True)

    if 1:
        pg.display('final', full=True)

    if 0:
        print dir(pg)
        print getattr(pg,'_parmgroup',None)

    if 0:
        print 'ns.Search(tags=Gphase):',ns.Search(tags='Gphase')
        print 'pg.ns.Search(tags=Gphase):',pg.ns.Search(tags='Gphase')

    if 0:
        pg.solvable(trace=True)
        pg.find_nodes(trace=True)
        pg.find_nodes(solvable=False, trace=True)
        pg.find_nodes(solvable=True, trace=True)

    if 0:
        pg.solvable(tags='Gphase', trace=True)
        pg.solvable(tags=['Gphase','Ggain'], trace=True)



#===============================================================

