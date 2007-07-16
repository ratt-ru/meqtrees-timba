# file: ../Grunt/ParameterizationPlus.py

# History:
# - 26may2007: creation
# - 07jun2007: allow {100~10%}
# - 07jun2007: p_deviation_expr()
# - 08jun2007: p_quals2list() and p_tags2list()
# - 03jul2007: added .nodescope(new=None)
# - 09jul2007: introduced ParmGroup class

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

from Timba.Contrib.JEN.Grunt import ParmGroup
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

    def __init__(self, ns=None, name=None,
                 quals=[], kwquals={},
                 namespace=None,
                 merge=None):

        # Scopify ns, if necessary:
        if is_node(ns):
            ns = ns.QualScope()        

        # Make sure that there is a nodescope (Required by Meow.Parameterization)
        if ns==None:
            ns = NodeScope()

        # TDL Options:
        self.tdloption_namespace = namespace    
        self._TDLCompileOptionsMenu = None   
        self._TDLCompileOption = dict()

        # Local values for options (for use without TDLOptions)
        self._opt = dict()


        #------------------------------------
        # NB: What about dropping quals/kwquals completely, since these may be
        #     introduced by passing ns as a node, rather than a nodescope.
        #     See also the function .nodescope()
        # Eventually.... (perverse coupling)? 
        #------------------------------------

        name = str(name)                           # just in case....

        # Make a little more robust 
        quals = self.p_quals2list(quals)

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
        self.p_clear()

        # Optional: Copy the parametrization of another object:
        if merge:
            self.p_merge(merge, trace=False)
        
        return None


    #---------------------------------------------------------------

    def p_clear (self):
        """Helper function to clear the parameter-part of the object"""
        self._parmgroups = dict()
        self._parmgogs = dict()
        self._pmerged = []
        self._accumulist = dict()
        return True


    def _p_active_groups (self, new=None):
        """Get/set the list of (names of) 'active' parmgroups"""
        active = []
        for key in self._parmgroups.keys():
            pg = self._parmgroups[key]
            if isinstance(new, (list,tuple)):
                pg.active(key in new)
            if pg.active():
                active.append(key)
        if new:
            self.p_TDLShowActive()

        # Make a new set of parmgogs (of active groups):
        gogs = self.p_gogs()

        # Finished:
        return active

    #---------------------------------------------------------------

    def nodescope (self, ns=None):
        """Get/set the internal nodescope (can also be a node)"""
        if ns:
            if is_node(ns):
                self.ns = ns.QualScope()        
            else:
                self.ns = ns
            # Pass the new nodescope on to its parmgroup(s):
            for key in self._parmgroups.keys():
                # self._parmgroups[key].ns = self.ns[key](key).QualScope()    # <---- !!
                self._parmgroups[key].nodescope(self.ns)                    # <---- !!
        # Always return the current nodescope:
        return self.ns


    def namespace(self, prepend=None, append=None):
        """Return the namespace string (used for TDL options etc).
        If either prepend or apendd strings are defined, attach them.
        NB: Move to the ParameterizationPlus class?
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

    def p_oneliner(self):
        """Return a one-line summary of this object"""
        ss = 'Grunt.ParameterizationPlus:'
        ss += ' '+str(self.name)
        ss += '  ('+str(self.ns['<>'].name)+')'
        return ss


    def p_display(self, txt=None, full=False, recurse=3):
        """Print a summary of this object"""
        print ' '
        print '** '+self.p_oneliner()
        if txt: print '  * (txt='+str(txt)+')'
        #...............................................................
        print '  * Grunt _parmgroups ('+str(len(self._parmgroups))+'):'
        for key in self._parmgroups:
            pg = self._parmgroups[key]
            if pg.active():
                print '    - ('+key+'): '+str(pg.oneliner())
            else:
                print '    - ('+key+'):   ... not active ...'
        #...............................................................
        print '  * Deviation expressions (mode==simulate only):'
        for key in self._parmgroups:
            pg = self._parmgroups[key]
            if pg.get_mode()=='simulate':
                print '    - ('+key+'): '+pg._deviation
        #...............................................................
        print '  * Grunt _parmgogs (groups of parmgroups, derived from their node tags):'
        for key in self.p_gogs():
            print '    - ('+key+'): '+str(self._parmgogs[key])
        #...............................................................
        print '  * TDLCompileOptionsMenu: '+str(self._TDLCompileOptionsMenu)
        for key in self._TDLCompileOption.keys():
            oo = self._TDLCompileOption[key]
            noexist = -1.23456789
            if getattr(oo, 'value', noexist)==noexist:
                print '    - '+str(key)+': '+str(self._TDLCompileOption[key])
            else:
                tdlvalue = self._TDLCompileOption[key].value
                selfvalue = getattr(self, key, noexist)
                if tdlvalue==selfvalue:
                    print '    - '+str(key)+' = '+str(tdlvalue)
                else:
                    print '    - '+str(key)+' = '+str(tdlvalue)+' != '+str(selfvalue)
        #...............................................................
        print '  * Accumulist entries: '
        for key in self._accumulist.keys():
            vv = self._accumulist[key]
            print '    - '+str(key)+' ('+str(len(vv))+'):'
            if full:
                for v in vv: print '    - '+str(type(v))+' '+str(v)
        #...............................................................
        if self._parmdefs:
            print '  * Meow _parmdefs ('+str(len(self._parmdefs))+') (value,tags,solvable):'
            if full:
                for key in self._parmdefs:
                    rr = list(deepcopy(self._parmdefs[key]))
                    rr[0] = str(rr[0])
                    print '    - ('+key+'): '+str(rr)
            print '  * Meow.Parm options (in _parmdefs):'
            if full:
                for key in self._parmdefs:
                    value = self._parmdefs[key][0]
                    if isinstance(value, Meow.Parm):
                        print '    - ('+key+'): (='+str(value.value)+') '+str(value.options)
            print '  * Meow _parmnodes ('+str(len(self._parmnodes))+'):'
            if full:
                for key in self._parmnodes:
                    rr = self._parmnodes[key]
                    print '    - ('+key+'): '+str(rr)
        #...............................................................
        print '**\n'
        return True

    #---------------------------------------------------------------

    def pg_display(self, full=False):
        """Display summaries of its parmgroups"""
        for key in self._parmgroups.keys():
            self._parmgroups[key].display(full=full)
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
                        deviation=None,
                        tiling=None, time_deg=0, freq_deg=0,
                        mode='nosolve'):
        
                        # constrain_min=0.1, constrain_max=10.0,
                        # rider=None, override=None,
                        # **kw):
        """Define a named (key) group of similar parameters"""

        # Check whether the group exists already:
        if self._parmgroups.has_key(key):
            s = '** duplicate parmgroup definition: '+str(key)
            raise ValueError,s

        # Some added value:
        tags = self.p_tags2list(tags)
        if True:
            if not self.name in tags: tags.append(self.name)          # <----- ??

        # Create the ParmGroup:
        pg = ParmGroup.ParmGroup (self.ns, key, tags=tags,
                                  namespace=self.name,
                                  descr=descr, unit=unit,
                                  default=default, constraint=constraint,
                                  deviation=deviation,
                                  tiling=tiling, time_deg=time_deg, freq_deg=freq_deg,
                                  mode=mode)
        
                                  # constrain_min=0.1, constrain_max=10.0,
                                  # rider=rider, override=override,
                                  # **kw)
        self._parmgroups[key] = pg
        return key


    #-----------------------------------------------------------------

    def p_group_create_member (self, key,
                               quals=[], kwquals={},
                               value=None, tags=[], solvable=True,            # may override
                               mode=None,
                               default=None, deviation=None,      # may override
                               tiling=None, time_deg=0, freq_deg=0):          # may override for Meow.Parm
        """Create the specified (quals, kwquals) member of the specified (key)
        parmgroup. By default, the common attrbutes of the group will be used
        to create the relevant Meow.Parm or simulation subtree, but some of
        these attributes may be overridden here...."""

        # Check whether the parmgroup (key) exists:
        self.p_has_group (key, severe=True)
        pg = self._parmgroups[key]
        return pg.create_member (quals=quals, kwquals=kwquals,
                                 value=value, tags=tags, solvable=solvable,        
                                 mode=mode,
                                 default=default, deviation=deviation,  
                                 tiling=tiling, time_deg=time_deg, freq_deg=freq_deg)    


    #-------------------------------------------------------------------

    def p_deviation_expr (self, ampl='{0.01~10%}', Psec='{500~10%}', PHz=None):
        """Helper function to make a standard deviation expression.
        All arguments must be strings of the form {<value>~<stddev>}.
        The <stddev> is used to generate different values around <value>
        for each member of the group (see .p_group_create_member())."""
        s = ampl
        if isinstance(Psec,str):
            s += ' * sin(2*pi*([t]/'+Psec+'+{0~1}))'
        if isinstance(PHz,str):
            s += ' * sin(2*pi*([f]/'+PHz+'+{0~1}))'
        return s




    #===================================================================
    # TDLOptions (general):
    #===================================================================

    def TDLCompileOptionsMenu (self, show=True):
        """Generic function for interaction with its TDLCompileOptions menu.
        The latter is created (once), by calling the specific function(s)
        .TDLCompileOptions(), which should be re-implemented by derived classes.
        The 'show' argument may be used to show or hide the menu. This can be done
        repeatedly, without duplicating the menu.
        """

        # print '\n**',self.oneliner(),self._TDLCompileOptionsMenu,'\n'
        
        # if not self._TDLCompileOptionsMenu:        # create the menu only once
        if True or not self._TDLCompileOptionsMenu:
            prompt = self.namespace(prepend='options for Joneset22: '+self.name)
            oolist = self.TDLCompileOptions()
            oolist.extend(self.p_TDLCompileOptions())
            self._read_TDLCompileOptions(trace=False)
            # print '\n** oolist(in menu):',self.oneliner(),'\n       ',oolist
            self._TDLCompileOptionsMenu = TDLCompileMenu(prompt, *oolist)
        else:
            print '\n** menu not recreated:',self.oneliner(),'\n'

        # Show/hide the menu as required (can be done repeatedly):
        self._TDLCompileOptionsMenu.show(show)
        return self._TDLCompileOptionsMenu

    #..................................................................

    def TDLCompileOptions (self):
        """Define a list of TDL options that control the structure of the
        Jones matrix.
        This function should be re-implemented by derived classes."""
        oolist = []

        if False:                    # temporary, just for testing
            key = 'xxx'
            if not self._TDLCompileOption.has_key(key):
                self._TDLCompileOption[key] = TDLOption(key, 'prompt_xxx',
                                                        range(3), more=int,
                                                        doc='explanation for xxx....',
                                                        namespace=self)
            oolist.append(self._TDLCompileOption[key])

        # Finished: Return a list of options:
        return oolist

    #.....................................................................

    def _read_TDLCompileOptions(self, trace=True):
        """Helper function to read TDLCompileOptions into local variables
        with the same name: e.g. opt['_default'] -> self._default
        """
        if trace: print '\n** _read_TDLCompileOptions:'
        noexist = -1.23456789
        for key in self._TDLCompileOption.keys():
            was = getattr(self, key, noexist)
            if not was==noexist:
                new = self._TDLCompileOption[key].value
                setattr(self, key, new)
                new = getattr(self,key)
                if trace: print ' -',key,':',was,'->',new
        if trace: print
        return True
        

    #.....................................................................

    def _reset_TDLCompileOptions(self, trace=True):
        """Helper function to reset the saved TDLCompileOptions to
        the current values of their local variable counterparts.
        The latter are the values that the designer put in,
        so this is a way to the saved values into a known state.
        """
        if trace: print '\n** _reset_TDLCompileOptions:'
        for key in self._TDLCompileOption.keys():
            was = self._TDLCompileOption[key].value
            new = getattr(self,key)
            self._TDLCompileOption[key].set_value(new, save=True)
            new = self._TDLCompileOption[key].value
            if trace: print ' -',key,':',was,'->',new
        if trace: print
        return True
        


    #===================================================================
    # TDLOptions (ParmGroups):
    #===================================================================

    def p_TDLCompileOptionsMenu (self, show=True):
        """Generic function for interaction with its TDLCompileOptions menu.
        The latter is created (once), by calling the specific function.
        .TDLCompileOptions(), which may be re-implemented by derived classes.
        The 'show' argument may be used to show or hide the menu. This can be done
        repeatedly, without duplicating the menu.
        """
        if not self._TDLCompileOptionsMenu:        # create the menu only once
            oolist = self.p_TDLCompileOptions()
            prompt = self.namespace(prepend='ParmGroup options for: '+self.name)
            self._TDLCompileOptionsMenu = TDLCompileMenu(prompt, *oolist)

        # Show/hide the menu as required (can be done repeatedly):
        self._TDLCompileOptionsMenu.show(show)
        return self._TDLCompileOptionsMenu

    #.........................................................................

    def p_TDLCompileOptions (self):
        """Define a list of TDL options that control the parameters
        of the various ParmGroups"""
        oolist = []

        opt = [None]
        opt.extend(self._parmgogs.keys())
        opt.extend(self._p_active_groups())
        doc = 'the selected groups will be solved simultaneously'
        prompt = 'solve for parmgroup(s)/parmgog(s)'
        key = '_tobesolved'
        oo = TDLOption(key, prompt, opt, more=str,
                       doc=doc, namespace=self)
        self._TDLCompileOption[key] = oo
        oo.when_changed(self._callback_tobesolved)
        oolist.append(self._TDLCompileOption[key])

        # Add the options menus of the various parmgroups:
        for key in self._parmgroups.keys():
            pg = self._parmgroups[key]
            self._TDLCompileOption[key] = pg.TDLCompileOptionsMenu()
            oolist.append(self._TDLCompileOption[key])
        self.p_TDLShowActive()

        # Finished:
        return oolist

    #.........................................................................

    def _callback_tobesolved (self, tobs):
        """Called whenever option '_tobesolved' is changed"""
        keys = self.p_find_parmgroups(tobs, severe=True)

        # Set the mode of selected groups (is this the desired behaviour...?)
        for key in self._parmgroups.keys():
            pg = self._parmgroups[key]
            if pg.active():
                if key in keys:
                    pg.set_TDLOption('_mode', 'solve')
                else:
                    pg.set_TDLOption('_mode', 'nosolve')

        # NB: How does self._tobesolved get its value from TDL.....???
        self.p_tobesolved(trace=True)                    # temporary, for testing only
        return True

    #.........................................................................

    def p_TDLShowActive (self):
        """Show the TDL options for the 'active' parmgroup(s), and hide the rest.
        Also redefine the parmgogs, and update the relevant TDL options."""

        # First show/hide the parmgroups:
        for key in self._parmgroups.keys():
            if self._TDLCompileOption.has_key(key):
                pg = self._parmgroups[key]
                self._TDLCompileOption[key].show(pg.active())
                
        # Then update the option list of option '_tobesolved':
        self._p_make_gogs()
        key = '_tobesolved'
        if self._TDLCompileOption.has_key(key):
            oo = self._TDLCompileOption[key]
            value = oo.value
            newopt = [None]
            newopt.extend(self._parmgogs.keys())
            if False:
                for key in self._parmgogs.keys():
                    if len(self._parmgogs[key])>1:
                        newopt.append(key)
                newopt.extend(self._p_active_groups())
            if value in newopt:
                oo.set_option_list(newopt, conserve_selection=True)
            else:
                index = 0         # index of first value (None)
                oo.set_option_list(newopt, select=index)

        # Finished:
        return True



    #===============================================================
    # Merge the parametrization of another object in its own.
    #===============================================================

    # NB: One should be careful with this since it has merit to keep 
    #     parameter sets with the same names but different qualifiers apart.
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

        if other in self._pmerged:
            # print '\n** p_merge(): skipped (merged before): ',str(other),'\n'
            return True

        # Merging depends on the parameterization of 'other':
        rr = getattr(other, '_parmdefs', None)
        if isinstance(rr, dict):
            # The other object is derived from Meow.Parameterization
            self._pmerged.append(other)               # avoid duplicate merging....

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

                # Then copy the Grunt.ParameterizationPlus parmgroups (objects):
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
                descr = 'copied from Meow.Parameterization of: '
                if getattr(other,'oneliner',None):
                    descr += str(other.oneliner())
                else:
                    descr += str(other.name)
                self.p_group_define (other.name, tags=None, descr=descr)
                pg = self._parmgroups[other.name]
                for key in other._parmdefs:
                    pd = other._parmdefs[key]               # assume: (value, tags, solvable)
                    newkey = other.name+'_'+key
                    # self._parmdefs[newkey] = pd
                    pg._parmdefs[newkey] = pd
                    # pg._nodes.append(self._parm(newkey))      # generate a node in self, not other!
                    pg._nodes.append(pg._parm(newkey))      # generate a node in pg, not other!
                    pg._solvable.append(pd[2])              # 3rd element: solvable (boolean)
                    pg._plot_labels.append(newkey)          # ....?



        if trace:
            self.p_display('after p_merge()', full=True)
        return True



    #===============================================================
    # Convenient access to a list of nodes/subtrees, e.g. for solving
    #===============================================================


    def p_tobesolved (self, return_nodes=True, return_NodeList=False, trace=False):
        """Get a list of the parmgroups (or tags?) that have been selected for solving.
        If return_nodes or return_NodeList (object), do that."""
        pgs = self._tobesolved
        if return_nodes or return_NodeList:
            return self.p_solvable(groups=pgs, trace=trace,
                                    return_NodeList=return_NodeList)
        elif trace:
            print '\n** p_tobesolved: ',pgs,'\n'
        return pgs


    #----------------------------------------------------------------

    def p_solvable (self, tags=None, groups='*', return_NodeList=False, trace=False):
        """Return a list with the specified selection of solvable MeqParm nodes.
        The nodes may be specified by their tags (n.search) or by parmgroups."""
        return self.p_find_nodes (tags=tags, groups=groups,
                                  return_NodeList=return_NodeList,
                                  solvable=True, trace=trace)


    #----------------------------------------------------------------

    def p_find_nodes (self, tags=None, groups='*', solvable=None,
                      return_NodeList=False, trace=False):
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
            # NB: Should we search the nodescopes of its parmgroups?
            #     (assuming that those have been derived from self.ns...?)
            tags = self.p_tags2list(tags)
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
            pgs = self.p_find_parmgroups (groups, severe=True)
            for key in pgs:
                pg = self._parmgroups[key]              # convenience
                if not isinstance(solvable, bool):      # solvable not specified
                    nodes.extend(pg._nodes)             # include all nodes
                    labels.extend(pg._plot_labels)      # include all 
                else:
                    for k,node in enumerate(pg._nodes):
                        if pg._solvable[k]==solvable:   # the specified kind
                            nodes.append(node)          # selected nodes only
                            labels.append(pg._plot_labels[k])

        # Report the found nodes (if any):
        if trace:
            for k,node in enumerate(nodes):
                print '  - (',labels[k],'):',str(node)
            print ' ->',len(nodes),'nodes, ',len(labels),'labels'

        # Optionally, return a NodeList object of the selected nodes and their labels
        if return_NodeList:
            if tags:
                name = 'tags'
                for k,tag in enumerate(tags):
                    name += str(tag)
                if trace:
                    print ' -- tags =',tags,' (name=',name,')'
            else:
                name = 'gogs'
                if isinstance(groups,str):
                    name += groups
                elif isinstance(groups,(list,tuple)):
                    for k,group in enumerate(groups):
                        name += str(group)
                if trace:
                    print ' -- groups =',groups,'(name=',name,') -> pgs =',pgs
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
        if groups==None:
            return []
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
        """Derive a dict of named groups of (active) parmgroups from the tags
        of the various (active) parmgroups. These may be used to select groups,
        e.g. in .solvable()."""
        gg = dict()
        keys = self._parmgroups.keys()
        for key in keys:
            pg = self._parmgroups[key]
            if pg.active():                # active groups only!
                tags = pg._tags
                for tag in tags:
                    gg.setdefault(tag,[])
                    if not key in gg[tag]:
                        gg[tag].append(key)
        self._parmgogs = gg
        return self._parmgogs



    #===============================================================
    # Methods using NodeLists:
    #===============================================================

    def p_compare (self, parmgroup, other, show=False):
        """Compare the nodes of a parmgroup with the corresponding ones
        of the given (and assumedly commensurate) parmgroup (other).
        The results are visualized in various helpful ways.
        The rootnode of the comparison subtree is returned.
        """
        self.p_has_group (parmgroup, severe=True)
        self.p_has_group (other, severe=True)
        pg1 = self._parmgroups[parmgroup]
        pg2 = self._parmgroups[other]
        return pg1.compare(pg2, show=show)


    #---------------------------------------------------------------

    def p_bundle (self, parmgroup='*', combine='Composer',
                  bookpage=True, folder=None, show=False):
        """Bundle the nodes in the specified parmgroup(s) by applying the
        specified combine-operation (default='Add') to them. Return the
        root node of the resulting subtree. Make bookpages for each parmgroup.
        """
        pgs = self.p_find_parmgroups (parmgroup, severe=True)
        if folder==None:
            if len(pgs)>1: folder = 'p_bundle_'+self.name
        bb = []
        for key in pgs:
            pg = self._parmgroups[key]
            bb.append(pg.bundle(bookpage=bookpage, folder=folder))
        return self._p_bundle_of_bundles (bb, name='p_bundle',
                                          qual=parmgroup,
                                          accu=True, show=show)

    #---------------------------------------------------------------

    def p_plot_rvsi (self, parmgroup='*',
                     bookpage=True, folder=None, show=False):
        """Make separate rvsi plots of the specified parmgroup(s). Return the
        root node of the resulting subtree. Make bookpages for each parmgroup.
        """
        pgs = self.p_find_parmgroups (parmgroup, severe=True)
        if bookpage:
            if not isinstance(bookpage, str):
                bookpage = 'p_plot_rvsi_'+self.name
        bb = []
        for key in pgs:
            pg = self._parmgroups[key]
            bb.append(pg.plot_rvsi(bookpage=bookpage, folder=folder))
        return self._p_bundle_of_bundles (bb, name='p_plot_rvsi',
                                          qual=parmgroup,
                                          accu=True, show=show)
    
    #---------------------------------------------------------------

    def p_plot_timetracks (self, parmgroup='*', 
                           bookpage=True, folder=None, show=False):
        """Visualize the nodes in the specified parmgroup(s) in a separate
        'inspector' (time-tracks) per parmgroup. Return the root node of
        the resulting subtree. Make bookpages for each parmgroup.
        """
        pgs = self.p_find_parmgroups (parmgroup, severe=True)
        if bookpage:
            if not isinstance(bookpage, str):
                bookpage = 'p_plot_timetracks_'+self.name
        bb = []
        for key in pgs:
            pg = self._parmgroups[key]
            bb.append(pg.plot_timetracks (bookpage=bookpage, folder=folder))
        return self._p_bundle_of_bundles (bb, name='p_plot_timetracks',
                                          qual=parmgroup,
                                          accu=True, show=show)


    #---------------------------------------------------------------

    def p_plot_spectra (self, parmgroup='*', 
                           bookpage=True, folder=None, show=False):
        """Visualize the nodes in the specified parmgroup(s) in a separate
        'inspector' (time-tracks) per parmgroup. Return the root node of
        the resulting subtree. Make bookpages for each parmgroup.
        """
        pgs = self.p_find_parmgroups (parmgroup, severe=True)
        if bookpage:
            if not isinstance(bookpage, str):
                bookpage = 'p_plot_spectra_'+self.name
        bb = []
        for key in pgs:
            pg = self._parmgroups[key]
            bb.append(pg.plot_spectra (bookpage=bookpage, folder=folder))
        return self._p_bundle_of_bundles (bb, name='p_plot_spectra',
                                          qual=parmgroup,
                                          accu=True, show=show)


    
    #---------------------------------------------------------------
    # Helper function:
    #---------------------------------------------------------------

    def _p_bundle_of_bundles (self, bb, name=None, qual=None,
                              accu=False, show=False):
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
        if accu: self.p_accumulist(qnode)
        if show: display.subtree(qnode, show_initrec=False)
        return qnode


    #===============================================================
    # Some useful helper functions (available to all derived classes)
    #===============================================================

    def p_tags2list (self, tags):
        """Helper function to make sure that the given tags are a list"""
        if tags==None: return []
        if isinstance(tags, (list, tuple)): return list(tags)
        if isinstance(tags, str): return tags.split(' ')
        s = '** cannot convert tag(s) to list: '+str(type(tags))+' '+str(tags)
        raise TypeError, s

    def p_quals2list (self, quals):
        """Helper function to make sure that the given quals are a list"""
        if quals==None: return []
        if isinstance(quals, (list,tuple)): return list(quals)
        if isinstance(quals, str): return quals.split(' ')
        return [str(quals)]

    #----------------------------------------------------------------

    def p_get_quals (self, merge=None, remove=None):
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

    def p_modify_default (self, key):
        """Modify the default value of the specified (key) parm"""
        # Not yet implemented..... See Expression.py
        return False





    #=====================================================================================
    #=====================================================================================
    # Accumulist service:
    # NB: This service does not really belong here, but is convenient.
    #=====================================================================================

    def p_accumulist (self, item=None, key=None, flat=False, clear=False):
        """Interact with the internal service for accumulating named (key) lists of
        items (nodes, usually), for later retrieval downstream.
        If flat=True, flatten make a flat list by extending the list with a new item
        rather than appending it.
        An extra list with key=* contains all items of all lists"""

        print '\n** p_accumulist(',str(item),')\n'
        
        if key==None: key = '_default_'
        if not isinstance(key, str):
            print '\n** .p_accumulist(): key is wrong type:',type(key),'\n'
            return False      
        self._accumulist.setdefault(key, [])           # Make sure that the list exists
        self._accumulist.setdefault('*', [])           # The list of ALL entries
        if item:
            if not flat:                                                                  
                self._accumulist[key].append(item)
                self._accumulist['*'].append(item)
            elif isinstance(item, (list,tuple)):
                self._accumulist[key].extend(item)
                self._accumulist['*'].extend(item)
            else:
                self._accumulist[key].append(item)
                self._accumulist['*'].append(item)
        # Always return the current value of the specified (key) list:
        keylist = self._accumulist[key]           
        if clear:
            # Optional: clear the entry (NB: What happens to '*' list??)
            self._accumulist[key] = []
            # self._accumulist['*'] = []
        # Enhancement: If flat=True, flatten the keylist....?
        return keylist

    #---------------------------------------------------------------------

    def p_bundle_accumulist(self, quals=None):
        """Bundle the nodes in self._accumulist with a reqseq"""
        cc = self.p_accumulist(clear=False)
        n = len(cc)
        if n==0: return None
        if n==1: return cc[0]
        # self.p_history('.p_bundle_accumulist()')
        qnode = self.ns['p_bundle_accumulist']
        if quals: qnode = qnode(quals)
        if not qnode.initialized():
            qnode << Meq.ReqSeq(children=cc, result_index=n-1)
        return qnode

    #---------------------------------------------------------------------------

    def p_merge_accumulist (self, other):
        """Merge the accumulist of another Matrix22 object with its own."""
        # self.history('.p_merge_accumulist()')
        olist = other._accumulist
        for key in olist.keys():
            if not key=='*':
                self.p_accumulist(olist[key], key=key, flat=True)
        return True





#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================


if 1:
    pp1 = ParameterizationPlus(name='GJones', quals='3c84')
    pp1.p_group_define('Gphase', tiling=3, mode='nosolve')
    pp1.p_group_define('Ggain', default=1.0, freq_deg=2)
    pp1.p_TDLCompileOptionsMenu()
    pp1.p_display('initial')



def _define_forest(ns):

    cc = []
    pp1.nodescope(ns)

    if 1:
        pp1.p_group_create_member('Gphase', 1)
        pp1.p_group_create_member('Gphase', 2.1, value=(ns << -89))
        pp1.p_group_create_member('Gphase', 2, value=34)
        pp1.p_group_create_member('Gphase', 3, tiling=5, mode='simulate')
        pp1.p_group_create_member('Gphase', 7, freq_deg=2)

    if 1:
        pp1.p_group_create_member('Ggain', 7, freq_deg=6)
        pp1.p_group_create_member('Ggain', 4, time_deg=3)

    if 0:
        cc.append(pp1.p_bundle(show=True))
        cc.append(pp1.p_plot_timetracks())
        cc.append(pp1.p_plot_spectra())

    if 0:
        nn = pp1.p_solvable(groups='GJones', return_NodeList=True)
        nn.display('solvable')
        nn.bookpage(select=4)
        

    pp1.p_display('final', full=True)

    if len(cc)==0: cc.append(ns.dummy<<1.1)
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
        pp1 = ParameterizationPlus(ns, name='GJones',
                                   # kwquals=dict(tel='WSRT', band='21cm'),
                                   quals='3c84')
        pp1.p_group_define('Gphase', tiling=3, mode='nosolve')
        pp1.p_group_define('Ggain', default=1.0, freq_deg=2)
        # pp1.p_TDLCompileOptionsMenu()
        pp1.p_display('initial')

    if 1:
        pp1.p_group_create_member('Gphase', 1)
        pp1.p_group_create_member('Gphase', 2.1, value=(ns << -89))
        pp1.p_group_create_member('Gphase', 2, value=34)
        pp1.p_group_create_member('Gphase', 3, tiling=5, mode='solve')
        pp1.p_group_create_member('Gphase', 7, freq_deg=2)

    if 1:
        pp1.p_group_create_member('Ggain', 7, freq_deg=6)
        pp1.p_group_create_member('Ggain', 4, time_deg=3)

    if 0:
        pp1.p_bundle(show=True)
    if 0:
        pp1.p_plot_rvsi(show=True)
    if 0:
        pp1.p_plot_spectra(show=True)
    if 0:
        pp1.p_plot_timetracks(show=True)

    pp1.p_display('final', full=True)


    #------------------------------------------------------------------

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

    if 0:
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
            pp1.p_find_nodes(groups=['GJones','DJones'], solvable=True, trace=True)
            pp1.p_find_nodes(groups=['GJones','DJones'], solvable=False, trace=True)
        pp1.p_display('after merge', full=True)

    if 1:
        e0 = Expression.Expression(ns, 'e0', '{a}+{b}*[t]-{e}**{f}+{100~10}', simul=False)
        e0.display()
        if 0:
            pp3 = ParameterizationPlus(ns, 'e0', merge=e0)
            pp3.p_display('after merge', full=True)
        if 1:
            pp1.p_merge(e0, trace=True)
            pp1.p_display('after merge', full=True)
            pp1.pg_display(full=True)

    if 0:
        pp1.p_accumulist('aa')
        pp1.p_accumulist('2')
        pp1.p_accumulist(range(3), flat=True)
        pp1.p_accumulist('bb', key='extra')
        pp1.p_display(full=True)
        print '1st time:',pp1.p_accumulist()
        print '1st time*:',pp1.p_accumulist(key='*')
        print '2nd time:',pp1.p_accumulist(clear=True)
        print '3rd time:',pp1.p_accumulist()


#===============================================================

