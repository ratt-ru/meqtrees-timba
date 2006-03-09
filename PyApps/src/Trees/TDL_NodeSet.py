# TDL_NodeSet.py
#
# Author: J.E.Noordam
#
# Short description:
#    A NodeSet object encapsulates group(s) of MeqNodes
#
# History:
#    - 03 mar 2006: creation from TDL_Parmset.py
#
# Full description:
#   Many types of MeqTree nodes (e.g. MeqParms) come in groups of similar ones,
#   which are dealt with as a group. The NodeSet object provides a convenient
#   way to define and manipulate such groups in various ways. 
#
#   A NodeSet object contains the following main components:
#   - A dict of named nodes (MeqNodes)
#   - A dict of named groups, i.e. lists of MeqNode names. 
#   - A dict of named gogs, i.e. lists of one or more group (or gog) names.
#     NB: A gog list may contain any combination group/gog names, or even
#     nested lists of group/gog names.     
#
#   The idea is to first define a number of named groups. When an (externally
#   created) node is put into the NodeSet, it must be accompanied with the name
#   of one or more groups to which it belongs. The groups of MeqNodes can then be
#   manipulated as a whole. Examples of such group manipulations are:
#
#   - Simple retrieval of a list of nodes (or their names) in a group.
#   - Selection of subgroups by matching substrings to their names.
#   - Bundling the nodes of a group with a MeqAdd or a MeqComposer.
#   - Applying unary operations (unop) to all nodes of a group.
#   - Applying 'binary' operations, e.g. MeqSubtract, or MeqToPolar to
#     the corresponding members of two groups.
#   - Comparison (MeqSubtract) of the corresponding members in a group of the
#     same name in another NodeSet.
#   - etc, etc
#
#   NB: When new nodes are created, the result is an (aptly named) new group,
#   which contains a list of the new MeqNodes.
#  
#   NB: Since the members of a group have a fixed order (it is a list), this
#   defines the concept of 'corresponding' members of two or more groups. 
#
#   When defining a group/gog, it may be accompanied by a 'rider' dict, which can
#   contain arbitrary information about the group/gog. The rider may be simply
#   retrieved by (group/gog) name, or it may be used to select specific groups/gogs.
#
#   MeqNodes, groups and gogs may all be selected by matching substrings to
#   their names.

#=================================================================================
# Preamble:
#=================================================================================

from Timba.TDL import *

from copy import deepcopy
from random import *
from math import *
from numarray import *

from Timba.Trees import TDL_common
from Timba.Trees import TDL_radio_conventions
from Timba.Trees import JEN_bookmarks




#=================================================================================
# Class NodeSet
#=================================================================================


class NodeSet (TDL_common.Super):
    """A NodeSet object encapsulates an (arbitrary) set of MeqNode nodes"""

    def __init__(self, **pp):

        TDL_common.Super.__init__(self, type='NodeSet', **pp)
        self.clear()
        return None


    #--------------------------------------------------------------------------------
    # Display functions:
    #--------------------------------------------------------------------------------
            
    def oneliner(self):
        """Make a one-line summary of this NodeSet object"""
        s = TDL_common.Super.oneliner(self)
        if len(self.quals())>0:
            s += ' quals='+str(self.quals())
        s += ' g:'+str(len(self.group()))
        s += ' gog:'+str(len(self.gog()))
        return s


    def display(self, txt=None, full=False, doprint=True, pad=True):
        """Display a description of the contents of this NodeSet object"""
        ss = TDL_common.Super.display (self, txt=txt, end=False, full=full)
        indent1 = 2*' '
        indent2 = 6*' '
 
        #------------------------
        ss.append(indent1+' - Registered groups ('+str(len(self.group()))+'):')
        for key in self.group().keys():
            group = self.group(key)
            n = len(group)
            s1 = indent2+' - '+key+' (n='+str(n)+')'
            s1 += ' (rider:'+str(len(self.group_rider(key)))+'):  '
            if full or n<3:
                ss.append(s1+str(group))
            else:
                ss.append(s1+group[0]+' ... '+group[n-1])

        #------------------------
        ss.append(indent1+' - group riders ('+str(len(self.group_rider()))+'):')
        if full:  
            empty = []
            for key in self.group_rider().keys():
                if len(self.group_rider()[key])>0:
                    ss.append(indent2+' - '+key+':     '+str(self.group_rider()[key]))
                else:
                    empty.append(key)
            if len(empty)>0:
                ss.append(indent2+' empty ('+str(len(empty))+'): '+str(empty))

        #------------------------
        ss.append(indent1+' - Defined gogs ('+str(len(self.gog()))+'):')
        for key in self.gog().keys():
            s1 = ' (rider:'+str(len(self.gog_rider(key)))+')'
            ss.append(indent2+' - '+key+s1+':     group(s): '+str(self.gog(key)))

        #------------------------
        ss.append(indent1+' - gog riders ('+str(len(self.gog_rider()))+'):')
        if full:
            empty = []
            for key in self.gog_rider().keys():
                if len(self.gog_rider()[key])>0:
                    ss.append(indent2+' - '+key+':    '+str(self.gog_rider()[key]))
                else:
                    empty.append(key)
            if len(empty)>0:
                ss.append(indent2+' empty ('+str(len(empty))+'): '+str(empty))

        #------------------------
        ss.append(indent1+' - Bundles (gogs, really) ('+str(len(self.__bundle))+'):')
        if full:
            for key in self.bundle().keys():
                ss.append(indent2+' - '+key+':    '+str(self.bundle()[key]))

        #------------------------
        ss.append(indent1+' - Contents of temporary buffer ('+str(len(self.__buffer))+'):')
        if full:
            for key in self.buffer().keys():
                ss.append(indent2+' - '+key+':    '+str(self.buffer()[key]))

        ss.append(indent1+' - Defined bookpages ('+str(len(self.__bookpage))+'):')
        for key in self.bookpage().keys():
            exists = JEN_bookmarks.get_bookpage(key)
            if exists: exists = True
            ss.append(indent2+' - '+key+' ('+str(exists)+'):    '+str(self.bookpage()[key]))

        ss.append(indent1+' - Defined bookfolders ('+str(len(self.__bookfolder))+'):')
        for key in self.bookfolder().keys():
            ss.append(indent2+' - '+key+':    '+str(self.bookfolder()[key]))

        #------------------------
        ss.append(indent1+' - Accumulated bookmarks ('+str(len(self.__bookmark))+'):')
        if full:
            for key in self.bookmark().keys():
                ss.append(indent2+' - '+key+':    '+str(self.bookmark()[key]))

        #------------------------
        ss.append(indent1+' - Available MeqNode nodes ('+str(len(self.__MeqNode))+'):')
        keys = self.__MeqNode.keys()
        n = len(keys)
        if full or n<10:
            for key in keys:
                s1 = TDL_common.format_initrec(self.__MeqNode[key])
                ss.append(indent2+' - '+str(self.__MeqNode[key])+'  '+s1)
        else:
            s1 = TDL_common.format_initrec(self.__MeqNode[keys[0]])
            ss.append(indent2+' - first: '+str(self.__MeqNode[keys[0]])+'  '+s1)
            ss.append(indent2+'   ....')
            s1 = TDL_common.format_initrec(self.__MeqNode[keys[n-1]])
            ss.append(indent2+' - last:  '+str(self.__MeqNode[keys[n-1]])+'  '+s1)

        return TDL_common.Super.display_end (self, ss, doprint=doprint, pad=pad)


    #--------------------------------------------------------------------------------
    # Functions related to MeqNodes: 
    #--------------------------------------------------------------------------------

    def MeqNode(self, key=None, node=None, trace=False):
        """Get/create a named MeqNode entry (the nodes are defined externally!).
        If a node is supplied, key is assumed to be a list of group-names to
        which the new node belongs. Otherwise, key is the name of a MeqNode."""
        if node:                                  # Create a new MeqNode entry
            nodename = node.name
            if self.__MeqNode.has_key(nodename):
                self.history(warning='MeqNode(node): already exists: '+nodename)
            else:
                self.__MeqNode[nodename] = node 
                # Assume that key indicates group-name(s):
                if not isinstance(key, (list,tuple)): key = [key]
                for groupname in key:
                    print 'nodename =',nodename,' key=',key,':',groupname
                    self.__group[groupname].append(nodename)  
                    self.__buffer[groupname] = node   # see .buffer() service
                if trace:
                    print '\n** MeqNode(): new entry:',node,key 
            return nodename
        # Otherwise, return the specified (key) group (None = all):
        return self._fieldict (self.__MeqNode, key=key, name='.MeqNode()')


    #---------------------------------------------------------------------------
    
    if False:
        # To be removed eventually:
        
        def __getitem__(self, key):
            """Get a named (key) MeqNode node"""
            # This allows indexing by key and by index nr:
            if isinstance(key, int): key = self.__MeqNode.keys()[key]
            return self.__MeqNode[key]

        def __setitem__(self, key, value):
            """Set a named (key) MeqNode node"""
            self.__MeqNode[key] = value
            return self.__MeqNode[key]

        def len(self):
            """The number of MeqNode entries in MeqNode"""
            return len(self.__MeqNode)
        
        def keys(self):
            """The list of MeqNode keys (names)"""
            return self.__MeqNode.keys()

        def has_key(self, key):
            """Test whether MeqNode contains an item with the specified key"""
            return self.keys().__contains__(key)


    #--------------------------------------------------------------------------------
    # Convenience (service): MeqBrowser bookmarks/pages/folders
    #--------------------------------------------------------------------------------

    def bookmark(self, key=None):
        """Get the specified (key) bookmark definition (None = all).
        A definition is a record as in the forest_state bookmark record"""
        return self._fieldict (self.__bookmark, key=key, name='.bookmark()')

    def bookpage(self, key=None, new=None):
        """Get/define the specified (key) bookpage definition (None = all).
        A definition consists of a list of MeqNodes (a gog, really)"""
        if new:
            if not isinstance(new, (list,tuple)): new = [new]
            self.__bookpage[key] = new
        return self._fieldict (self.__bookpage, key=key, name='.bookpage()')

    def bookfolder(self, key=None, new=None):
        """Get/define the specified (key) bookfolder definition (None = all).
        A definition consists of a list of MeqNodes (a gog, really)"""
        if new:
            if not isinstance(new, (list,tuple)): new = [new]
            self.__bookpage[key] = new
        return self._fieldict (self.__bookfolder, key=key, name='.bookfolder()')

    #------------------------------------------------------------------------

    def make_bookpage (self, ns, group=None, pagename=None, trace=False):
        """Make a bookpage of bundles of the specified group(s)"""
        if trace: print '** .make_bookpage(',group,pagename,'):'
        if not isinstance(pagename, str):
            pagename = self._make_bundle_name(group)
        rootnode = self.make_bundle (ns, group, bookpage=pagename)
        return rootnode


    def ensure_bookpages(self, ns=None, trace=False):
        """Make sure that all defined bookpages have actually been created
        in the forest_state record"""
        print '\n** .ensure_bookpages(): '
        for key in self.bookpage().keys():
            # pagename = 'bp_'+key              # NOT a good idea!
            pagename = key
            if not JEN_bookmarks.get_bookpage(pagename):
                if trace: print '- create: ',pagename
                for name in self.bookpage(key):
                    node = self.make_bundle(ns, name)
                    bms = JEN_bookmarks.bookmark(node, page=pagename)
                    # self.__bookmark[bms.name] = bms
                    if trace: print '  -',name,':',bms
            elif trace:
                print '- exists already: ',pagename
        return True

    #--------------------------------------------------------------------------------
    # Convenience (service): temporary buffer
    #--------------------------------------------------------------------------------

    # When a new MeqNode entry is made (see .MeqNode(), the node stub is put into the
    # internal buffer for later use. This is a convenience service that allows access
    # to the most recently defined MeqNodes by means of their group name, rather than
    # their full name (e.g. see MG_JEN_Joneset.py) 

    def buffer(self, clear=False):
        """Get/clear the temporary helper record self.__buffer"""
        if clear: self.__buffer = dict()
        return self.__buffer


    #--------------------------------------------------------------------------------
    # Convenience (service): quals
    #--------------------------------------------------------------------------------

    # The NodeSet object may remember node-name qualifiers. These are then used by the
    # parent object (e.g. a Parmset) when making new nodes for the NodeSet.

    def quals(self, new=None, clear=False):
        """Get/set the default MeqNode node-name qualifier(s)"""
        if clear:
            self.__quals = dict()
        if isinstance(new, dict):
            for key in new.keys():
                self.__quals[key] = str(new[key])
        return self.__quals


    #--------------------------------------------------------------------------------
    # Functions related to groups (of MeqNode-names):
    #--------------------------------------------------------------------------------

    def group (self, key=None, **pp):
        """Get/define the named (key) group (flat list of MeqNode names)"""
        if len(pp)>0:                               # define a new group
            if key==None:      
                return self.history(error='group(pp): no key specified')

            pp.setdefault('color', 'red')           # plot color
            pp.setdefault('style', 'circle')        # plot style
            pp.setdefault('size', 10)               # size of plotted symbol

            s1 = 'group: '+str(key)
            s1 += self.format_rider_summary(pp)
            if self.__group.has_key(key):
                self.history(warning='** Overwritten '+s1)
            else:
                self.history('** Defined new '+s1)

            self.__group[key] = []                  # initialise the group with an empty list
            self.__group_rider[key] = pp            # extra info associated with the group
            self.__plot_color[key] = pp['color']
            self.__plot_style[key] = pp['style']
            self.__plot_size[key] = pp['size']

            return key                              # return the actual group/gog key name
        # Otherwise, return the specified (key) group (None = all):
        return self._fieldict (self.__group, key=key, name='.group()')


    def group_rider(self, key=None):
        """Get the specified (key) group_rider (None = all)"""
        return self._fieldict (self.__group_rider, key=key, name='.group_rider()')

    def plot_color(self, key=None):
        """Get the specified (key) group plot_color (None = all)"""
        return self._fieldict (self.__plot_color, key=key, name='.plot_color()')

    def plot_style(self, key=None):
        """Get the specified (key) group plot_style (None = all)"""
        return self._fieldict (self.__plot_style, key=key, name='.plot_style()')

    def plot_size(self, key=None):
        """Get the specified (key) group plot_size (None = all)"""
        return self._fieldict (self.__plot_size, key=key, name='.plot_size()')

    def radio_conventions(self):
        self.__plot_color = TDL_radio_conventions.plot_color()
        self.__plot_style = TDL_radio_conventions.plot_style()
        self.__plot_size = TDL_radio_conventions.plot_size()
        return True

    def group_keys (self, select='*'):
        """Return the names (keys) of the available groups"""
        return self.__group.keys()

    def has_group (self, key):
        """Check whether the specified (key) group exists"""
        return self.__group.has_key(key)


    def nodes(self, group=None, select='*', trace=False):
        """Return a list of actual MeqNodes in the specified group(s)"""
        if trace: print '\n** .nodes(',group,select,'):'
        names = self.nodenames(group, select=select, trace=False)
        if not isinstance(names, (list,tuple)): return False
        nn = []
        for name in names:
            nn.append(self.__MeqNode[name])
        if trace: print '(',len(nn),'):',nn,'\n'
        return nn

    def nodenames (self, group=None, select='*', trace=False):
        """Return a list of the MeqNode names in the specified group(s)"""
        if trace: print '** .nodenames(',group,select,'):'
        gg = self._extract_flat_grouplist(group, must_exist=True, origin='.nodes()')
        if not isinstance(gg, (list,tuple)): return False
        if trace: print '    -> groupnames(',len(gg),'):',gg
        names = []
        for key in gg:
            nn = self.__group[key]           # list of node-names for group 'key'
            if select=='first':
                name = nn[0]
                if not name in names:        # avoid doubles
                    names.append(name)       # take the first one only
            elif select=='last':
                name = nn[len(nn)-1]
                if not name in names:        # avoid doubles
                    names.append(name)       # take ths last one only
            else:
                for name in nn:
                    if not name in names:    # avoid doubles
                        names.append(name)   # take them all
        if trace: print '    -> nodenames(',len(names),'):',names
        return names

    #-----------------------------------------------------------------------------------
    # Group selection:
    #-----------------------------------------------------------------------------------

    def select_groups (self, name=None, substring=True, rider=None, trace=False):
        """Return a list of groups according to the selection criteria"""
        if trace: print '** .select_groups(',name,substring,rider,'):'
        gg = self._extract_flat_grouplist(name, must_exist=False, origin='.select_groups()')
        if not isinstance(gg, (list,tuple)): return False
        if trace: print '    extract: groups(',len(gg),'):',gg

        # Match substrings in group keys, if required:
        gg = self._match_string (gg, self.group_keys(), substring=substring, trace=trace)

        # Select on group_rider criteria, if specified:
        if isinstance(rider, dict):
            gg = self._match_rider (gg, rider, self.__group_rider, trace=trace)

        # Return the list of selected group names:
        if trace: print '    -> groups(',len(gg),'):',gg
        return gg


    #-----------------------------------------------------------------------

    def _match_string (self, string, slist=[], substring=True, trace=False):
        """Select the strings in slist that match the given (sub)string(s)"""
        if not isinstance(string, (list,tuple)): string = [string]
        if not isinstance(slist, (list,tuple)): slist = [slist]
        cc = []
        for ss in string:
            for s in slist:                         # e.g. self.group_keys()
                if substring:                       # match substring
                    if s.rfind(ss)>=0: cc.append(s)
                else:                               # match entire string
                    if s==ss: cc.append(s)
        if trace: print '    ** _match_string() ->',len(cc),'):',cc
        return cc

    #-----------------------------------------------------------------------

    def _match_rider (self, gg, rider=None, ridict=None, trace=False):
        """Select groups/gogs (gg) on rider criteria, if specified"""
        if not isinstance(rider, dict): return gg
        if not isinstance(ridict, dict): return False
        cc = []
        for g in gg:
            ok = True
            rr = ridict[g]
            for key in rider.keys():
                if rr.has_key(key):
                    v = rider[key]
                    if isinstance(v, (list, tuple)):
                        if not v.__contains__(rr[key]): ok = False
                    else:
                        if (not v==rr[key]): ok = False
                    print '     -',g,key,':',v,'<->',rr[key],'    ok =',ok
            if ok: cc.append(g)
        if trace: print '    ** _match_rider() ->',len(cc),'):',cc
        return cc

    #--------------------------------------------------------------------------------
    # Helper function (very useful):
    #--------------------------------------------------------------------------------

    def _extract_flat_grouplist (self, key=None, origin='<origin>',
                                must_exist=False, level=0):
        """Make a flat list of (unique) groupnames from the specified key.
        The latter may be a string (name of group or gog) or a list/tuple
        of strings or lists/tuples, etc (recursive). Returns False if error."""  
        s1 = '._extract_flat_group('+str(level)+','+str(origin)+'): '

        if key==None:                                               # key not specified
            return self.group_keys()                                # return all available groups
        
        if not isinstance(key, (list,tuple)): key = [key]           # make list
        gg = []
        for g in key:
            if isinstance(g, (list,tuple)):                         # recursive
                gg1 = self._extract_flat_grouplist(g, origin=origin,
                                                  must_exist=must_exist, level=level+1)
                if not isinstance(gg1, list): return False
                for g1 in gg1:
                    if not gg.__contains__(g1): gg.append(g1)
            elif not isinstance(g, str):                            # 
                return self.history(error=s1+'not a valid name: '+str(type(g))+': '+str(g))
            elif self.__group.has_key(g):                           # group exists  
                if not gg.__contains__(g): gg.append(g)             # avoid doubles
            elif self.__gog.has_key(g):                             # gog exists
                gg1 = self._extract_flat_grouplist(self.__gog[g], origin=origin,
                                                  must_exist=must_exist, level=level+1)
                if not isinstance(gg1, list): return False
                for g1 in gg1:
                    if not gg.__contains__(g1): gg.append(g1)       # avoid doubles
            elif must_exist:                                        # must exist
                return self.history(error=s1+'group not available: '+g)
            else:                                                   # does not have to exist
                if not gg.__contains__(g): gg.append(g)             # avoid doubles
        return gg


    #================================================================================
    # Functions related to group-of-groups (gogs):
    #================================================================================

    def gog (self, key=None, groups=None, **pp):
        """Get/define the named (key) group-of-groups (gog).
        If groups specified, create a new gog (named key) for the specified groups.
        Otherwise, just return the specified (key) gog(s)"""
        if groups:                                  # define a new gog
            if key==None:                  
                return self.history(error='gog('+str(groups)+'): no key specified')
            gg = self._extract_flat_grouplist(groups, must_exist=False)
            if not isinstance(gg, list): return False
            if not isinstance(groups, list): groups = [groups]

            s1 = 'gog: '+str(key)+':  '+str(groups)
            s1 += self.format_rider_summary(pp)
            if self.__gog.has_key(key):
                self.history(warning='** Overwritten '+s1)
            else:
                self.history('** Defined new '+s1)

            self.__gog[key] = groups                # list of gog groups/gogs
            self.__gog_rider[key] = pp              # extra info associated with the gog
            return key                              # return the actual gog key name
        # Otherwise, return the specified (key) group (None = all):
        return self._fieldict (self.__gog, key=key, name='.gog()')


    def format_rider_summary (self, pp):
        """Format a summary of the given rider record pp"""
        if not isinstance(pp, dict):
            return 'rider='+str(type(pp)) 
        elif len(pp)==0:
            return ''
        elif len(pp)<3:
            qq = TDL_common.unclutter_inarg(pp)
            return ',  rider = '+str(qq)
        return ',  rider length = '+str(len(pp))

                
    def gog_rider(self, key=None):
        """Get the specified (key) gog_rider (None = all)"""
        return self._fieldict (self.__gog_rider, key=key, name='.gog_rider()')

    def gog_keys (self, select='*'):
        """Return the names (keys) of the available gogs"""
        return self.__gog.keys()

    def has_gog (self, key=None):
        """Check whether the specified (key) gog exists"""
        return self.__gog.has_key(key)

    def select_gogs (self, name=None, substring=True, rider=None, trace=False):
        """Return a list of gogs according to the selection criteria"""
        if trace: print '** .select_gogs(',name,substring,rider,'):'

        # NB: Eventually we might need self._extract_flat_goglist()....
        gg = name
        if name==None: gg = self.gog_keys()
        if not isinstance(gg, (list,tuple)): gg = [gg]
        if trace: print '    extract: gogs(',len(gg),'):',gg

        # Match substrings in gog keys, if required:
        gg = self._match_string (gg, self.gog_keys(), substring=substring, trace=trace)

        # Select on gog_rider criteria, if specified:
        if isinstance(rider, dict):
            gg = self._match_rider (gg, rider, self.__gog_rider, trace=trace)

        # Return the list of selected gog ggs:
        if trace: print '    -> gogs(',len(gg),'):',gg
        return gg





    #================================================================================
    # Functions that generate new (groups of derived) MeqNodes
    #================================================================================



    #--------------------------------------------------------------------------
    # Make a subtree of MeqNode bundles (also MeqNodes), e.g. for plotting:
    #--------------------------------------------------------------------------
    
    def make_bundle (self, ns, group=None, name=None, bookpage=None):
        """Return a subtree of (the sum(s) of) the nodes in the specified group(s)"""
        if trace: print '\n** make_bundle(',group,name,bookpage,'):'
        gg = self._extract_flat_grouplist(group, must_exist=True)
        if not isinstance(gg, list): return False
        if len(gg)==0: return False

        # The bundles of multiple groups are 'bbundled' also:
        multiple = (len(gg)>1)                               # True if multiple
        if multiple:
            if not isinstance(name, str):
                name = self._make_bundle_name(group)
            bbname = '_bd_'+str(name)
            if self.__MeqNode.has_key(bbname):               # bbundle already exists
                return self.__MeqNode[bbname]                # just return it

        cc = []
        bname = None                                         # bundle name
        for g in gg:                                         # for all groups
            nodes = self.nodes(g, trace=trace)               # their nodes
            if isinstance(nodes, list): 
                n = len(nodes)
                if n>0: 
                    bname = 'sum'+str(n)+'('+str(g)+')'    # bundle name
                    if self.__MeqNode.has_key(bname):        # bundle exists already
                        node = self.__MeqNode[bname]         # use existing
                        self.__bundle[bname] += 1            # increment counter ....?
                    elif ns==None:                           # nodescope needed
                        self.history(error='** .make_bundle(): nodescope required!')
                        return False                         # error ...
                    else:
                        node = ns[bname] << Meq.Add(children=nodes)
                        self.__MeqNode[bname] = node
                        self.__bundle[bname] = 1             # create
                    cc.append(node)  
                    if isinstance(bookpage, str):            # MeqBrowser bookpage specified 
                        bms = JEN_bookmarks.bookmark(node, page=bookpage)
                        self.__bookmark[bms.name] = bms
                        self.bookpage(bookpage, bname)       # append

        # Return the root node of a subtree:
        if not multiple:
            if bname:
                self.history ('.make_bundle('+str(bname)+'): '+str(group)+' '+str(bookpage))
                return self.__MeqNode[bname]                 # A single group bundle
        elif len(cc)==0:
            self.history(error='** .make_bundle(): len(cc)==0!')
        elif ns==None:
            self.history(error='** .make_bundle(): nodescope required!')
        else:                                                # A bundle of group bundles 
            self.__MeqNode[bbname] = ns[bbname] << Meq.Composer(children=cc)
            self.history ('.make_bundle('+str(bbname)+'): '+str(group)+' '+str(bookpage))
            return self.__MeqNode[bbname]

        # Something wrong if got to here:
        return False


    #------------------------------------------------------------------------

    def _make_bundle_name (self, group, trace=False):
        """Make a decriptive bundle name of a flat list of groupnames"""
        if trace: print '** ._make_bundle_name(',group,'): ->',
        if isinstance(group, str):
            if self.__gog.has_key(group):
                name = 'gog:'+group
                if trace: print '(str,exist):',name
                return name
            if trace: print '(str,!exist):',group
            return group
        elif isinstance(group, (list, tuple)):
            if len(group)==1:
                if trace: print '(list[0]):',group[0]
                return group[0]
        gg = self._extract_flat_grouplist(group, must_exist=True)
        name = ''
        for g in gg:
            name += g[0]
            if len(g)>1: name += g[1]
        name += '('+str(len(gg))+')'
        if trace: print name
        return name


    def bundle(self, key=None):
        """Get the specified (key) bundle  (None = all)."""
        return self._fieldict (self.__bundle, key=key, name='.bundle()')


    #--------------------------------------------------------------------------
    # Apply unary operations to the specified groups of MeqNodes:
    #--------------------------------------------------------------------------
    

    def apply_unop (self, ns, group=None, unop=None, bookpage=None):
        """Apply unary operation(s) to the nodes in the specified group(s).
        The resulting nodes are put into new groups, and a new gog is defined"""
        if trace: print '\n** apply_unop(',group,unop,'):'
        gg = self._extract_flat_grouplist(group, must_exist=True)
        if not isinstance(gg, list): return False
        if len(gg)==0: return False
        gog = []
        for g in gg:                                         # for all groups
            gname = self._make_unop_name(g, unop=unop)            # e.g. Cos(g)
            nodes = self.nodes(g, trace=trace)               # the nodes of group g
            if isinstance(nodes, list) and len(nodes)>0: 
                self.group(gname, unop=unop)                 # define a new group gname
                for node in nodes:
                    node = self._apply_unop(ns, node, unop)
                    self.MeqNode(gname, node)             
                gog.append(gname)                            # groups for gog (below)

        # Make a gog for the new groups:
        if len(gog)>0:
            # The gogname is made in two stages:
            gogname = self._make_bundle_name(group, trace=False)
            gogname = self._make_unop_name(gogname, unop=unop)
            self.gog(gogname, groups=gog, unop=unop)
            # Return the bundle root node:
            if isinstance(bookpage, bool): bookpage = gogname
            node = self.make_bundle(ns, gogname, bookpage=bookpage)
            self.history ('.apply_unop('+str(unop)+'): '+str(group)+' '+str(bookpage))
            return node
        # Something wrong if got to here:
        return False


    def _apply_unop(self, ns, node=None, unop=None):
        """Recursive helper function to apply (optional) unary operation(s) to node"""
        if unop==None: return node
        if not isinstance(unop, (list, tuple)): unop = [unop]
        for unop1 in unop:
            node = ns << getattr(Meq,unop1)(node)
        return node

    def _make_unop_name(self, name=None, unop=None):
        """Helper function to make a inop name"""
        if unop==None: return False
        if not isinstance(unop, (list, tuple)): unop = [unop]
        name = str(name)
        for unop1 in unop:
            name = str(unop1)+'('+name+')'
        return name


    #--------------------------------------------------------------------------
    # Apply binary operations to the specified groups of MeqNodes:
    #--------------------------------------------------------------------------
    
    def apply_binop (self, ns, group=None, binop=None, bookpage=None):
        """Apply binary operation(s) to the nodes in the specified group(s).
        The resulting nodes are put into new groups, and a new gog is defined"""
        if trace: print '\n** apply_binop(',group,binop,'):'
        gg = self._extract_flat_grouplist(group, must_exist=True)
        print 'gg =',gg
        if not isinstance(gg, list): return False
        print 'gg =',gg
        if not len(gg)==2: return False
        print 'gg =',gg

        # Get two lists of nodes:
        lhs = self.nodes(gg[0], trace=trace)          # left-hand side nodes        
        if not isinstance(lhs, list): return False 
        rhs = self.nodes(gg[1], trace=trace)          # right-hand side nodes
        if not isinstance(rhs, list): return False 
        if not len(lhs)==len(rhs): return False
        if len(lhs)==0: return False

        # Make the new group:
        gname = self._make_binop_name(gg, binop=binop)
        self.group(gname, binop=binop)
        for i in range(len(lhs)):
            cc = [lhs[i],rhs[i]]
            node = ns << getattr(Meq,binop)(children=cc)
            self.MeqNode(gname, node)

        # Return the bundle root node:
        if isinstance(bookpage, bool): bookpage = gname
        node = self.make_bundle(ns, gname, bookpage=bookpage)
        self.history ('.apply_binop('+str(binop)+'): '+str(group)+' '+str(bookpage))
        return node


    def _make_binop_name(self, name=None, binop=None):
        """Helper function to make a binop name"""
        return str(binop)+'('+str(name[0])+','+str(name[1])+')'


    #--------------------------------------------------------------------------
    # Compare corresponding groups in another NodeSet:
    #--------------------------------------------------------------------------
    
    def compare (self, ns, NodeSet=None, group=None, binop='Subtract', bookpage=None):
        """Compare (binop) with corresponding nodes in another Nodeset. 
        The resulting nodes are put into new groups, and a new gog is defined."""
        if trace: print '\n** compare(',group,binop,'):'

        gg = self._extract_flat_grouplist(group, must_exist=True)
        if not isinstance(gg, list): return False

        gnames = []
        for g in gg:
            if not NodeSet.has_group(g):
                pass                           # error...?
            else:
                # Get two lists of nodes:
                lhs = self.nodes(g, trace=trace)             # left-hand side nodes        
                if not isinstance(lhs, list): return False 
                rhs = NodeSet.nodes(g, trace=trace)          # right-hand side nodes
                if not isinstance(rhs, list): return False 
                if not len(lhs)==len(rhs): return False
                if len(lhs)==0: return False
                
                # Make the new group:
                gname = 'compare('+g+')'
                self.group(gname, binop=binop)
                for i in range(len(lhs)):
                    cc = [lhs[i],rhs[i]]
                    node = ns << getattr(Meq,binop)(children=cc)
                    self.MeqNode(gname, node)
                gnames.append(gname)

        # Return the bundle root node:
        gogname = self._make_bundle_name(gnames)
        if isinstance(bookpage, bool): bookpage = gogname
        node = self.make_bundle(ns, gnames, bookpage=bookpage)
        self.history ('.compare('+str(binop)+'): '+str(NodeSet.label())+' '+str(group)+' '+str(bookpage))
        return node



    #---------------------------------------------------------------------------
    # Some organising functions:
    #---------------------------------------------------------------------------

    def cleanup(self, ns=None):
      """Remove empty groups/gogs"""

      # Remove empty groups:
      removed = []
      for key in self.__group.keys():
        if len(self.__group[key])==0:
          self.__group.__delitem__(key)
          removed.append(key)

      # Remove gogs that have group members that do not exist:
      for skey in self.__gog.keys():
        ok = True
        for key in self.__gog[skey]:
          if not self.__group.has_key(key):
            ok = False
        if not ok: self.__gog.__delitem__(skey)

      # Miscellaneous:
      self.ensure_bookpages(ns)                 # Make bookmarks if necessary
      self.buffer(clear=True)                   # Clear the temporary buffer
      self.history ('.cleanup(): removed group(s): '+str(removed))
      return True

    #-----------------------------------------------------------------

    def update(self, NodeSet=None):
        """Update the essentials from another NodeSet object"""
        if NodeSet==None: return False
        # NB: update OVERWRITES existing fields with new versions!
        self.__MeqNode.update(NodeSet.MeqNode())
        self.__group.update(NodeSet.group())
        self.__group_rider.update(NodeSet.group_rider())
        self.__plot_color.update(NodeSet.plot_color())
        self.__plot_style.update(NodeSet.plot_style())
        self.__plot_size.update(NodeSet.plot_size())
        self.__bookmark.update(NodeSet.bookmark())
        self.__bookpage.update(NodeSet.bookpage())
        self.__bookfolder.update(NodeSet.bookfolder())
        self.__bundle.update(NodeSet.bundle())
        self.__gog.update(NodeSet.gog())
        self.__gog_rider.update(NodeSet.gog_rider())
        self.history(append='updated from: '+NodeSet.oneliner())
        return True

    #------------------------------------------------------------------
    
    def clear(self):
        """Clear the object"""
        self.__MeqNode = dict()
        self.__group = dict()
        self.__group_rider = dict()
        self.__plot_color = dict()
        self.__plot_style = dict()
        self.__plot_size = dict()
        self.__gog = dict()
        self.__gog_rider = dict()
        self.__bundle = dict()
        self.__bookmark = dict()
        self.__bookpage = dict()
        self.__bookfolder = dict()
        self.__quals = dict()       
        self.buffer(clear=True)
        return True

#----------------------------------------------------------------------
#   methods used in saving/restoring the NodeSet
#----------------------------------------------------------------------

    def clone(self):
        """Clone self such that no NodeStubs are present.
        This is needed to save the NodeSet."""
        saved = NodeSet()
        saved.__quals = self.__quals
        saved.__group = self.__group
        saved.__group_rider = self.__group_rider
        saved.__gog = self.__gog
        saved.__gog_rider = self.__gog_rider
        saved.__plot_color = self.__plot_color
        saved.__plot_style = self.__plot_style
        saved.__plot_size = self.__plot_size
        saved.__bundle = self.__bundle
        saved.__bookmark = self.__bookmark
        saved.__bookpage = self.__bookpage
        saved.__bookfolder = self.__bookfolder
        # Convert MeqNode to a dict of strings:
        saved.__MeqNode = TDL_common.encode_nodestubs(self.__MeqNode)
        self.history(append='cloned: ')
        return saved

    #-------------------------------------------------------------------------

    def restore(self, ns=None, saved=None):
        """ recreate the NodeSet from a saved version 'saved'"""
        self.__quals = saved.__quals
        self.__group = saved.__group
        self.__group_rider = saved.__group_rider
        self.__gog = saved.__gog
        self.__gog_rider = saved.__gog_rider
        self.__plot_color = saved.__plot_color
        self.__plot_style = saved.__plot_style
        self.__plot_size = saved.__plot_size
        self.__bundle = saved.__bundle
        self.__bookmark = saved.__bookmark
        self.__bookpage = saved.__bookpage
        self.__bookfolder = saved.__bookfolder
        # Recreate links to NodeStubs, which have to exist in the nodescope 'ns':
        self.__MeqNode = TDL_common.decode_nodestubs(ns, saved.__MeqNode)
        self.history(append='restored: ')
        return True
 


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
    if trace: print '** NodeSet: _counters(',key,') =',_counters[key]
    return _counters[key]


#========================================================================
# Definition of some NodeSets, for testing:
#========================================================================


def test1(ns, nstat=2, mult=1.0):
    """Definition of a NodeSet for testing"""

    nst = NodeSet(label='test1')

    # Register the nodegroups:
    pp = dict(a=10, b=11)
    a1 = nst.group('Ggain_X', aa=1, bb=1, cc=1, **pp)
    a2 = nst.group('Ggain_Y', aa=1, bb=2, cc=1)
    p1 = nst.group('Gphase_X', aa=1, bb=3, cc=2)
    p2 = nst.group('Gphase_Y', aa=1, bb=4, cc=2)
    
    # Define extra gog(s) from combinations of nodegrouns:
    nst.gog('GJones', [a1, p1, a2, p2])
    nst.gog('Gpol1', [a1, p1])
    nst.gog('Gpol2', [a2, p2])
    nst.gog('Gampl', [a1, a2])
    nst.gog('Gphase', [p1, p2])
    nst.gog('grogog', [a1, p2, 'GJones'])

    # Make nodes themselves:
    freq = ns.freq << Meq.Freq()
    for i in range(nstat):
        for Ggain in [a1,a2]:
            node = ns[Ggain](i=i) << Meq.Multiply(i*mult,freq)
            nst.MeqNode (Ggain, node=node)
         
        for Gphase in [p1,p2]:
            node = ns[Gphase](i=i) << Meq.Multiply(-i*mult,freq)
            nst.MeqNode (Gphase, node=node)

    nst.bookpage('GX', [a1,p1])
    nst.bookpage('GY', [a2,p2])

    nst.cleanup(ns)
    return nst


#--------------------------------------------------------------------

def test2(ns, nstat=2, mult=1.1):
    """Definition of a NodeSet for testing"""

    nst = NodeSet(label='test2')

    # Register the nodegroups:
    pp = dict(a=10, b=11)
    a1 = nst.group('Ggain_X', aa=1, bb=1, cc=1, **pp)
    a2 = nst.group('Ggain_Y', aa=1, bb=2, cc=1)
    p1 = nst.group('Gphase_X', aa=1, bb=3, cc=2)
    p2 = nst.group('Gphase_Y', aa=1, bb=4, cc=2)
    t2 = nst.group('test2', aa=1, bb=4, cc=2)
    
    # Define extra gog(s) from combinations of nodegrouns:
    nst.gog('GJones', [a1, p1, a2, p2])
    nst.gog('Gpol1', [a1, p1])
    nst.gog('Gpol2', [a2, p2])
    nst.gog('Gampl', [a1, a2])
    nst.gog('Gphase', [p1, p2])
    nst.gog('test2', [t2, a2])

    # Make nodes themselves:
    freq = ns.freq << Meq.Freq()
    for i in range(nstat):
        for Ggain in [a1,a2]:
            node = ns[Ggain](i=i) << Meq.Multiply(i*mult,freq)
            nst.MeqNode (Ggain, node=node)
         
        for Gphase in [p1,p2]:
            node = ns[Gphase](i=i) << Meq.Multiply(-i*mult,freq)
            nst.MeqNode ([Gphase,t2], node=node)

    nst.bookpage('GX', [a1,p1])
    nst.bookpage('GY', [a2,p2])

    nst.cleanup(ns)
    return nst



#========================================================================
# Test routine:
#========================================================================

if __name__ == '__main__':
    print '\n*******************\n** Local test of: TDL_NodeSet.py:\n'
    from numarray import *
    from Timba.Trees import TDL_display
    # from Timba.Trees import JEN_record
    ns = NodeScope()
    
    nst = NodeSet(label='initial')
    nst.display('initial')

    if 0:
        print '** dir(nst) ->',dir(nst)
        print '** nst.__doc__ ->',nst.__doc__
        print '** nst.__str__() ->',nst.__str__()
        print '** nst.__module__ ->',nst.__module__
        print

    if 0:
        gg = ['xx',['xx','yy'],['xx',['yy','zz']]]
        gg.append(None)
        gg.append(['xxx',None])
        for g in gg:
            fnl = nst._extract_flat_grouplist(g, must_exist=False)
            print '\n** g =',g,'  ->',fnl

    if 1:
        nst = test1(ns)

    if 0:
        nst.cleanup(ns)

    if 0:
        gg = nst.group_keys()
        # gg.append('xxx')
        gg = 'GJones'                      
        gg = ['GJones',['Gampl','Gpol1',['Gpol2']]]                      
        # gg = ['GJones',['Gampl','Gpol1',['xxx']]]                      
        nn = nst.nodenames (gg, select='*', trace=True)
        nn = nst.nodes (gg, select='*', trace=True)

    if 0:
        print
        for key in nst.group().keys():
            print '- group:',key,':',nst.group(key)
        print

    if 0:
        print
        for key in nst.gog().keys():
            print '- gog:',key,':',nst.gog(key)
        print

    if 0:
        name = None
        name = 'Gp'
        rider = None
        rider = dict(bb=[2,3,None], aa=[1,2])
        nst.select_groups (name=name, substring=True, rider=rider, trace=True)

    if 0:
        name = None
        name = 'Gp'
        rider = None
        rider = dict(bb=[2,3,None])
        rider = dict(automatic=True)
        nst.select_gogs (name=name, substring=True, rider=rider, trace=True)

    if 0:
        # bb = nst.make_bundle(ns)
        bb = nst.make_bundle(ns, 'grogog')
        TDL_display.subtree(bb, 'bundle', full=True, recurse=3)
        
    if 0:
        nst.make_bookpage(ns, 'grogog')
        nst.make_bookpage(ns, 'grogog')
        
    if 0:
        nst.apply_unop(ns, 'GJones', 'Cos', bookpage=True)

    if 0:
        nst.apply_binop(ns, [a1,p1], 'Polar', bookpage=True)

    if 1:
        nst2 = test2(ns)
        nst2.display('nst2', full=True)

    if 1:
        nst.compare(ns, nst2, 'GJones', bookpage=True)

    if 0:
        nst.update(nst2)

    if 1:
        nst.display(full=True)
        # nst.display()


    if 0:
        # Display the final result:
        # k = 0 ; TDL_display.subtree(ns[k], 'ns['+str(k)+']', full=True, recurse=3)
        nst.display('final result')

    print '\n*******************\n** End of local test of: TDL_NodeSet.py:\n'




#============================================================================================









 

