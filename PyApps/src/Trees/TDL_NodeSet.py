# TDL_NodeSet.py
#
# Author: J.E.Noordam
#
# Short description:
#    A NodeSet object encapsulates group(s) of MeqNodes
#
# History:
#    - 03 mar 2006: creation from TDL_Parmset.py
#    - 20 mar 2006: removed .bookfolder() again
#    - 21 mar 2006: upgraded .bookmark() definition
#    - 04 apr 2006: removed self.__buffer
#    - 12 apr 2006: split .MeqNode() into .get_/.set_MeqNode()
#    - 16 apr 2006: MeqNode entries are dict(node=node, ....)
#    - 20 apr 2006: added eval-list to MeqNode entry dicts
#    - 20 apr 2006: implemented .dataCollect()
#
# Full description:
#   Many types of MeqTree nodes (e.g. MeqParms) come in groups of similar ones,
#   which are often dealt with as a group. The NodeSet object provides a convenient
#   way to define and manipulate such groups in various ways. 
#
#   A NodeSet object contains the following main components:
#   - A dict of named nodes (MeqNodes)
#     (each entry is a dict with at least a field node=node)
#   - A dict of named groups, i.e. lists of MeqNode names.
#     (each MeqNode entry belongs to ONE group only!)
#   - A dict of named gogs, i.e. lists of one or more group (or gog) names.
#     NB: A gog list may contain any combination group/gog names, or even
#     nested lists of group/gog names.
#   - A dict of named bookmark definition records. These are used to generate
#     actual bookmarks, and a means to supply them with requests.
#
#   The idea is to first define a number of named groups, which can have an
#   arbitrary number of named attributes (e.g. color, default value, etc).
#   These group attributes are stored in group_riders, and can be retrieved.
#   When an (externally created) node is put into the NodeSet, it must be
#   accompanied with the name of the group to which it belongs. The groups
#   of MeqNodes can then be manipulated as a whole. Examples of such group
#   manipulations are:
#
#   - Simple retrieval of a list of nodes (or their names) in a group.
#   - Selection of subgroups by matching substrings to their names.
#   - Bundling the nodes of a group with a MeqAdd or a MeqComposer.
#   - Making (pages/folders of) MeqBrowser bookmarks of bundled nodes. 
#   - Applying unary operations (unop) to all nodes of a group.
#   - Applying 'binary' operations, e.g. MeqSubtract, or MeqToPolar to
#     the corresponding members of two groups.
#   - Comparison (MeqSubtract) of the corresponding members in a group of the
#     same name in another NodeSet.
#   - etc, etc
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
#

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

from copy import deepcopy
from random import *
from math import *
from numarray import *

from Timba.Trees import TDL_common
from Timba.Trees import TDL_radio_conventions
from Timba.Trees import JEN_bookmarks

# Temporary, until TDL_dataCollect.py:
from Timba.Contrib.JEN import MG_JEN_dataCollect
# from Timba.Contrib.JEN import MG_JEN_historyCollect



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
                    rider = TDL_common.unclutter(self.group_rider()[key])
                    ss.append(indent2+' - '+key+':     '+str(rider))
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
                rider = TDL_common.unclutter(self.gog_rider()[key])
                if len(self.gog_rider()[key])>0:
                    ss.append(indent2+' - '+key+':    '+str(rider))
                else:
                    empty.append(key)
            if len(empty)>0:
                ss.append(indent2+' empty ('+str(len(empty))+'): '+str(empty))

        #------------------------
        ss.append(indent1+' - Bundles (gogs, really) ('+str(len(self.__bundle))+'):')
        if full:
            for key in self.bundle().keys():
                ss.append(indent2+' - '+key+':    '+str(self.bundle()[key]))

        ss.append(indent1+' - Defined bookmarks ('+str(len(self.__bookmark))+'):')
        for key in self.bookmark().keys():
            bm = TDL_common.unclutter(self.bookmark()[key])
            ss.append(indent2+' - '+key+':    '+str(bm))

        #------------------------
        ss.append(indent1+' - Available MeqNode nodes ('+str(self.len())+'):')
        keys = self.keys()
        n = len(keys)
        if full or n<10:
            for key in keys:
                node = self.MeqNode(key)
                s1 = TDL_common.format_initrec(node)
                s2 = ' - '+str(node.name)+'  '+s1
                eval = self.MeqNode(key, field='eval')
                if len(eval)>0:
                    s2 += '  (eval('+str(len(eval))+'): '+str(eval[0])
                    if len(eval)>1: s2 += '...'
                    s2 += ')'
                ss.append(indent2+s2)
        else:
            node = self.MeqNode(keys[0])
            s1 = TDL_common.format_initrec(node)
            ss.append(indent2+' - first: '+str(node.name)+'  '+s1)
            ss.append(indent2+'   ....')
            node = self.MeqNode(keys[n-1])
            s1 = TDL_common.format_initrec(node)
            ss.append(indent2+' - last:  '+str(node.name)+'  '+s1)

        return TDL_common.Super.display_end (self, ss, doprint=doprint, pad=pad)



    #--------------------------------------------------------------------------------
    # Convenience (service): MeqBrowser bookmarks/pages/folders
    #--------------------------------------------------------------------------------

    def bookmark (self, key=None, group=None, page=None, folder=None):
        """Get/define the specified (key) bookmark definition (None = all).
        A definition consists of a list of groups (it is a gog, really).
        It is used to create nodes and actual bookmark(s) later.
        Default page and folder names are based on the NodeSet labels and
        the bookmark key, but they may also be specified explicitly."""
        if group:
            glist = self._extract_flat_grouplist (group, origin='.bookmark()',
                                                  must_exist=True)
            # Supply default page and folder names, if necessary:
            if folder==None:
                folder = self.tlabel()                              # always make automatic folder name
            if page==None: page = True                              # default: make automatic page name
            if isinstance(page, bool):              
                if not page:                                        # page==False (explicit)
                    page = None                                     #   no bookpage
                else:                                               # page==True
                    page = self.tlabel()+'_'+str(key)               #   make automatic page name
            self.__bookmark[key] = dict(key=key, groups=glist,
                                        created=False, panels=[],
                                        page=page, folder=folder)
        return self._fieldict (self.__bookmark, key=key, name='.bookmark()')


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
    # Functions related to MeqNodes: 
    #--------------------------------------------------------------------------------

    def set_MeqNode(self, node=None, group='<undefined>', trace=False):
        """Create a named MeqNode entry (the nodes are defined externally!)."""
        nodename = node.name
        if self.has_key(nodename):
            self.history(warning='set_MeqNode(node): already exists: '+nodename)
        elif not isinstance(group, str):
            return self.history('set_MeqNode(group='+str(type(group))+') key sould be string')
        else:
            # MeqNode entries are dicts, with the node in the field 'node'.
            # In addidition, the entry contains other fields with aux info:
            # - eval contains (a list of) nodes that are to be used for evaluation.
            #   The default is itself. Eval nodes are usually MeqCompunder nodes.
            self.__MeqNode[nodename] = dict(node=node, eval=[]) 
            if isinstance(group, str):
                self.__group.setdefault(group, [])      # make sure that group exists
                self.__group[group].append(nodename)    # append this node to the group
                self.__group_rider.setdefault(group, dict()) # make empty group rider
            s1 = 'set_MeqNode(): new entry: '+str(nodename)+' (in group: '+str(group)+')'
            self.history(s1)
            if trace: print '**',s1  
        return nodename

    #-----------------------------------------------------------------------------
 
    def append_MeqNode_eval(self, key=None, append=None, trace=False):
        """Append one or more nodes (append) to the list of eval-nodes in the
        specified (key) MeqNode entry. See also .MeqNode_eval()."""
        if not self.__MeqNode.has_key(key):
            return False                                # error message....
        if not isinstance(append, (list,tuple)): append = [append]
        for node in append:
            name = node.name                            # store the node NAME
            s1 = 'MeqNode_eval('+str(key)+'): append: '+str(name)
            if not self.__MeqNode.has_key(name):        # MeqNode entry should exist
                self.set_MeqNode(node)                  # create if necessary
            self.__MeqNode[key]['eval'].append(name)    # append to eval list
            self.history(s1)
            if trace: print s1
        return True

    #-----------------------------------------------------------------------------
 
    def MeqNode_eval(self, key=None, result='nodes', trace=False):
        """Return the node(s) that should be evaluated to get a result from the
        specified (key) MeqNode entry. Usually, this will be the node itself.
        But if the MeqNode entry has a list of eval-nodes, return those.
        The latter are usually MeqCompounder nodes that interpolate an ND MeqParm."""
        nodes = []
        names = []
        if not self.__MeqNode.has_key(key):
            return False                                # error message....
        elif len(self.__MeqNode[key]['eval'])==0:
            names = [key]
            nodes = [self.__MeqNode[key]['node']]       # a list of one node: itself
        else:
            for name in self.__MeqNode[key]['eval']:
                nodes.append(self.__MeqNode[name]['node'])
                names.append(name)
        # Return a list (!) of zero or more nodes to be evaluated.
        if trace:
            print '** MeqNode_eval(',key,'): node-names =',names
        if result=='names': return names
        return nodes

    #-----------------------------------------------------------------------------

    def MeqNode(self, key=None, field='node', trace=False):
        """Get a named (key) MeqNode entry (dict).
        If a field is specified, return that only."""
        rr = self._fieldict (self.__MeqNode, key=key, name='.MeqNode()')
        if key==None: return rr                         # return entire MeqNode dict
        if not isinstance(rr, dict): return rr          # entry (key) not found....
        if isinstance(field, str):                      # field specified
            if not rr.has_key(field): return False      # error message?
            return rr[field]                            # return the field only
        return rr                                       # return MeqNode entry dict

    #-----------------------------------------------------------------------------

    def len(self):
        """Return the total nr of MeqNode entries."""
        return len(self.__MeqNode)

    def keys(self):
        """Return the MeqNode entry keys."""
        return self.__MeqNode.keys()

    def empty(self):
        """Return True if the NodeSet is empty (has no nodes)."""
        return self.len()==0

    def has_key(self, key):
        """Check whether the specified (key) MeqNode entry exists."""
        return self.__MeqNode.has_key(key)



    #--------------------------------------------------------------------------------
    # Functions related to groups (of MeqNode-names):
    #--------------------------------------------------------------------------------

    def group (self, key=None, rider=None, **kwargs):
        """Get/define the named (key) group (flat list of MeqNode names)"""
        if rider==None:
            # Otherwise, return the specified (key) group (None = all):
            return self._fieldict (self.__group, key=key, name='.group()')
        
        # The rider usually contains the inarg record (pp) of the calling function.
        if not isinstance(rider, dict): rider = dict()  # just in case
        rider = deepcopy(rider)                         # necessary!
        if key==None:      
            return self.history(error='group(pp): no key specified')

        rider.setdefault('color', 'red')           # plot color
        rider.setdefault('style', 'circle')        # plot style
        rider.setdefault('size', 10)               # size of plotted symbol

        # The rider fields may be overridden by the keyword arguments kwargs, if any: 
        for pkey in kwargs.keys():
            rider[pkey] = kwargs[pkey]

        # Some checks and bookkeeping:
        s1 = 'group: '+str(key)
        s1 += self._format_rider_summary(rider, 'group_rider')
        if self.__group.has_key(key):
            self.history(warning='** Overwritten '+s1)
        else:
            self.history('** Defined new '+s1)

        # Create the group, with its auxiliary fields:
        self.__group[key] = []                     # initialise the group with an empty list
        self.__group_rider[key] = rider            # extra info associated with the group
        
        # Necessary?
        self.__plot_color[key] = rider['color']
        self.__plot_style[key] = rider['style']
        self.__plot_size[key] = rider['size']

        # return the actual group/gog key name
        return key

    #-----------------------------------------------------------------------

    def group_keys (self, select='*'):
        """Return the names (keys) of the available groups"""
        return self.__group.keys()

    def has_group (self, key):
        """Check whether the specified (key) group exists"""
        return self.__group.has_key(key)


    def nodes(self, group=None, select='*', eval=False, trace=False):
        """Return a list of actual MeqNodes in the specified group(s)"""
        if trace: print '** .nodes(',group,select,', eval=',eval,'):',
        names = self.nodenames(group, select=select, trace=False)
        if not names: return False
        nn = []
        for key in names:
            nn.append(self.MeqNode(key))
        if trace: print '-> (',len(nn),'):',names
        return nn

    def nodenames (self, group=None, select='*', eval=False, trace=False):
        """Return a list of the MeqNode names in the specified group(s).
        If eval==True, return the names of their eval-nodes."""
        if trace: print '** .nodenames(',group,select,', eval=',eval,'):'
        gg = self._extract_flat_grouplist(group, must_exist=True, origin='.nodes()')
        if not gg: return False
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

        # Special case: return the names of the corresponding eval-nodes:
        if eval:
            nn = []
            for name in names:
                n1 = self.MeqNode_eval(name, result='names', trace=False)
                for n in n1:
                    if not n in nn:
                        nn.append(n)         # avoid doubles
            names = nn
        if trace: print '   ->',len(names),'nodenames: ',names
        return names


    #-----------------------------------------------------------------------------------
    # Some group attributes:
    #-----------------------------------------------------------------------------------

    def group_rider(self, key=None):
        """Get the specified (key) group_rider (None = all)"""
        return self._fieldict (self.__group_rider, key=key, name='.group_rider()')

    def group_rider_item(self, item=None, key=None, default=None, trace=False):
        """Get the specified (key) item (e.g. color) from the group_rider (None = all)"""
        return self._dictitem(self.group_rider(), item=item, key=key, default=default,
                              name='.group_rider_item()', trace=trace)

    def plot_color(self, key=None, trace=False):
        """Get the specified (key) group plot_color (None = all)"""
        return self.group_rider_item ('color', key=key, default='yellow', trace=trace)

    def plot_style(self, key=None, trace=False):
        """Get the specified (key) group plot_style (None = all)"""
        return self.group_rider_item ('style', key=key, default='circle', trace=trace)

    def plot_size(self, key=None, trace=False):
        """Get the specified (key) group plot_size (None = all)"""
        return self.group_rider_item ('size', key=key, default=20, trace=trace)

    def plot_pen(self, key=None, trace=False):
        """Get the specified (key) group plot_size (None = all)"""
        return self.group_rider_item ('pen', key=key, default=1, trace=trace)

    def radio_conventions(self):
        """Some standard plot colors/styles etc"""
        self.__plot_color = TDL_radio_conventions.plot_color()
        self.__plot_style = TDL_radio_conventions.plot_style()
        self.__plot_size = TDL_radio_conventions.plot_size()
        return True

    #-----------------------------------------------------------------------------------
    # Group selection:
    #-----------------------------------------------------------------------------------

    def select_groups (self, name=None, substring=True, rider=None, trace=False):
        """Return a list of groups according to the selection criteria (None=all)"""
        if trace: print '** .select_groups(',name,substring,rider,'):'
        gg = self._extract_flat_grouplist(name, must_exist=False, origin='.select_groups()')
        # if not isinstance(gg, (list,tuple)): return False
        if not gg: return False
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
        # if not isinstance(string, (list,tuple)): string = [string]
        # if not isinstance(slist, (list,tuple)): slist = [slist]
        string = self._listuple(string)
        slist = self._listuple(slist)
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
                    if trace: print '     -',g,key,':',v,'<->',rr[key],'    ok =',ok
            if ok: cc.append(g)
        if trace: print '    ** _match_rider() ->',len(cc),'):',cc
        return cc

    #--------------------------------------------------------------------------------
    # Helper function (very useful):
    #--------------------------------------------------------------------------------

    def _extract_flat_grouplist (self, key=None, origin=None,
                                must_exist=False, level=0):
        """Make a flat list of (unique) groupnames from the specified key.
        The latter may be a string (name of group or gog) or a list/tuple
        of strings or lists/tuples, etc (recursive). Returns False if error."""

        if origin==None: origin = self.tlabel()
        s1 = '._extract_flat_grouplist('+str(level)+', '+str(key)+', '+str(origin)+'): '

        if key==None:                                               # key not specified
            return self.group_keys()                                # return all available groups
        
        # if not isinstance(key, (list,tuple)): key = [key]           # make list
        key = self._listuple(key)
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

    def gog (self, key=None, groups=None, bookpage=None, **pp):
        """Get/define the named (key) group-of-groups (gog).
        If no groups specified, just return the specified (key) gog(s)
        Otherwise create a named (key) gog for the specified groups.
        If a bookpage is specified (string or True), define a gog bookmark."""
        
        if groups:                                               # define a new gog
            if key==None:                  
                return self.history(error='gog('+str(groups)+'): no key specified')
            gg = self._extract_flat_grouplist(groups, must_exist=False, origin='.gog()')
            if not isinstance(gg, list): return False
            if not isinstance(groups, list): groups = [groups]

            s1 = 'gog: '+str(key)+':  '+str(groups)
            s1 += self._format_rider_summary(pp, 'gog_rider')
            if self.__gog.has_key(key):
                self.history(warning='** Overwritten '+s1)
            else:
                self.history('** Defined new '+s1)

            # If required, make a bookmark for this gog:
            if bookpage:
                self.bookmark(key, groups, page=bookpage)

            self.__gog[key] = groups                # list of gog groups/gogs
            self.__gog_rider[key] = pp              # extra info associated with the gog
            return key                              # return the actual gog key name
        # Otherwise, return the specified (key) group (None = all):
        return self._fieldict (self.__gog, key=key, name='.gog()')


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
        gg = self._listuple(gg)
        # if not isinstance(gg, (list,tuple)): gg = [gg]
        if trace: print '    extract: gogs(',len(gg),'):',gg

        # Match substrings in gog keys, if required:
        gg = self._match_string (gg, self.gog_keys(), substring=substring, trace=trace)

        # Select on gog_rider criteria, if specified:
        if isinstance(rider, dict):
            gg = self._match_rider (gg, rider, self.__gog_rider, trace=trace)

        # Return the list of selected gog ggs:
        if trace: print '    -> gogs(',len(gg),'):',gg
        return gg


    def gog_rider(self, key=None):
        """Get the specified (key) gog_rider (None = all)"""
        return self._fieldict (self.__gog_rider, key=key, name='.gog_rider()')

    def gog_rider_item(self, item=None, key=None, trace=False):
        """Get the specified (key) item (e.g. color) from the gog_rider (None = all)"""
        return self._dictitem(self.gog_rider(), item=item, key=key,
                              name='.gog_rider_item()', trace=trace)



    #================================================================================
    # Functions that generate new MeqNodes (i.e. that require a nodescope(ns)):
    #================================================================================

    
    def dataCollect (self, ns, group=None, name=None,
                     bookpage=None, folder=None, trace=False):
        """Return a contatenation (dconc) of dataCollect nodes for the specified group(s)"""

        funcname = 'dataCollect()'
        if trace: print '** dataCollect(',group,name,bookpage,folder,'):'
        gg = self._extract_flat_grouplist(group, must_exist=True, origin='.make_bundle()')
        if not isinstance(gg, list): return False
        if len(gg)==0: return False

        uniqual = _counter(funcname, increment=-1)

        # Make dcolls per (available) corr, and collect groups of corrs:
        dcoll = []
        for g in gg:                                         # for all groups
            # rider = self.group_rider(g)                      # the group rider
            nodes = self.nodes(g, eval=True, trace=trace)    # the eval-nodes of group g
            if isinstance(nodes, list): 
                dc = MG_JEN_dataCollect.dcoll (ns, nodes, 
                                               scope='<scope>', tag=str(g),
                                               type='realvsimag', errorbars=True,
                                               color=self.plot_color(g),
                                               # size=self.plot_size(g),
                                               # pen=self.plot_pen(g),
                                               style=self.plot_style(g))
                dcoll.append(dc)

        # Concatenate:
        dconc = MG_JEN_dataCollect.dconc(ns, dcoll, 
                                         scope='<dconc_scope>',
                                         tag='all', bookpage='NodeSet')
        # Return the root node:
        return dconc['dcoll']


    #--------------------------------------------------------------------------
    # Make a subtree of MeqNode bundles (also MeqNodes), e.g. for plotting:
    #--------------------------------------------------------------------------
    
    def make_bundle (self, ns, group=None, name=None,
                     bookpage=None, folder=None, trace=False):
        """Return a subtree of (the sum(s) of) the nodes in the specified group(s)"""

        funcname = 'make_bundle()'
        if trace: print '** make_bundle(',group,name,bookpage,folder,'):'
        gg = self._extract_flat_grouplist(group, must_exist=True, origin='.make_bundle()')
        if not isinstance(gg, list): return False
        if len(gg)==0: return False

        uniqual = _counter(funcname, increment=-1)

        # The bundles of multiple groups are 'bbundled' also:
        multiple = (len(gg)>1)                               # True if multiple
        if multiple:
            if not isinstance(name, str):
                name = self._make_bundle_name(group)
            bbname = '_bd_'+str(name)
            if self.has_key(bbname):                         # bbundle already exists
                if trace: print '  MeqNode',bbname,'already exists'
                # NB: Returning here inhibits separate bookmarks (see below)
                return self.MeqNode(bbname)                  # just return it
            if isinstance(bookpage, bool) and bookpage:      # if bookpage==True: 
                 bookpage = bbname                           #   make an automatic name
            if trace: print '  bookpage =',bbname

        cc = []
        bname = None                                         # bundle name
        for g in gg:                                         # for all groups
            nodes = self.nodes(g, eval=True, trace=trace)    # the eval-nodes of group g
            if isinstance(nodes, list): 
                n = len(nodes)
                if n>0: 
                    bname = 'sum'+str(n)+'('+str(g)+')'      # bundle name
                    if self.has_key(bname):                  # bundle exists already
                        node = self.MeqNode(bname)           # use existing
                        self.__bundle[bname] += 1            # increment counter ....?
                    elif ns==None:                           # nodescope needed
                        self.history(error='** .make_bundle(): nodescope required!')
                        return False                         # error ...
                    else:
                        node = ns[bname]
                        if not node.initialized():           # node does not exists yet
                            node << Meq.Add(children=nodes, mt_polling=True)
                            self.set_MeqNode(node, trace=trace)   
                        self.__bundle[bname] = 1             # bundle book-keeping...?
                    cc.append(node)  

                    # Make MeqBrowser bookmark(s), if required. NB: These are
                    # made irrespective of whether the bundle already exists,
                    # which allows different bookmarks for the same bundle.
                    # Existing bookmarks/pages/folders are ignored.
                    if bookpage or folder:
                        JEN_bookmarks.create (node, page=bookpage, folder=folder)

        # Return the root node of the bundle subtree:
        if not multiple:
            if bname:
                s1 = '.make_bundle('+str(bname)+') single: '+str(group)
                s1 += '   (page='+str(bookpage)+', folder='+str(folder)+')'
                if trace: print s1
                self.history (s1)
                return self.MeqNode(bname)                   # A single group bundle
        elif len(cc)==0:
            self.history(error='** .make_bundle(): len(cc)==0!')
        elif ns==None:
            self.history(error='** .make_bundle(): nodescope required!')
        else:                                                # A bundle of group bundles 
            node = ns[bbname](uniqual) << Meq.Composer(children=cc)
            self.set_MeqNode(node, trace=trace)
            s1 = '** .make_bundle('+str(bbname)+') multiple: '+str(group)
            s1 += '   (page='+str(bookpage)+', folder='+str(folder)+')'
            if trace: print s1
            self.history (s1)
            return self.MeqNode(bbname)                    

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
        gg = self._extract_flat_grouplist(group, must_exist=True, origin='.make_bundle_name()')
        name = ''
        for g in gg:
            name += g[0]
            if len(g)>1: name += g[1]
        name += '('+str(len(gg))+')'
        if trace: print name
        return name

    #------------------------------------------------------------------------

    def bundle(self, key=None):
        """Get the specified (key) bundle  (None = all)."""
        return self._fieldict (self.__bundle, key=key, name='.bundle()')



    #--------------------------------------------------------------------------
    # Making MeqBrowser bookmarks:
    #--------------------------------------------------------------------------
    
    def ensure_bookmarks(self, ns=None, override_folder=None, trace=False):
        """Make sure that all defined bookmarks have actually been created
        in the forest_state record. Make group bundles if necessary"""
        funcname = '.ensure_bookmarks()'
        if trace: print '\n**',funcname
        uniqual = _counter(funcname, increment=-1)
        for key in self.bookmark().keys():
            rr = self.bookmark(key)                           # convenience
            if trace: print '-',rr
            if not rr['created']:                             # create only once

                rr['panels'] = []
                for name in rr['groups']:
                    node = self.make_bundle(ns, name, trace=trace)
                    print '-- node =',node
                    if TDL_common.is_nodestub(node):          # result is valid node
                        rr['panels'].append(node)

                # Make a single rootnode:
                if len(rr['panels'])==0:                      # should not happen...
                    pass
                elif len(rr['panels'])==1:
                    rr['rootnode'] = rr['panels'][0]
                else:
                    name = '_bookmark_'+key
                    node = ns[name](uniqual) << Meq.Composer(children=rr['panels'])
                    rr['rootnode'] = node

                # Finished:
                rr['created'] = True                          # avoid repeat
                self.__bookmark[key] = rr                     # replace
                self._history(funcname+': created bookmark definition: '+key)

            # MeqBrowser bookmarks (always): 
            folder = rr['folder']                 
            if override_folder: folder = override_folder
            if rr['page'] or folder:
                for panel in rr['panels']:
                    JEN_bookmarks.create (panel, page=rr['page'], folder=folder)
        return True

    #----------------------------------------------------------------------------

    def bookmark_subtree(self, ns=None, folder=None, trace=False):
        """Return the rootnode of a subtree of all bookmark root nodes.
        This can be used to supply requests to these nodes."""

        # trace = True
        # First make sure that all bookmark trees have been created:
        self.ensure_bookmarks(ns, override_folder=folder, trace=trace)
        
        funcname = '.bookmark_subtree()'
        if trace: print '\n**',self.tlabel(),':',funcname,':'
        root = []
        for key in self.bookmark().keys():                  # for all bookmark definitions
            rr = self.bookmark(key)
            if trace: print '**',funcname,': key=',key,' rr=',rr
            if rr.has_key('rootnode'):                      # ....?
                root.append(rr['rootnode'])
                        
        # Return a single root node:
        if len(root)==0:                                    # no root nodes collected..?
            self._history(warning=funcname+': -> empty...')
            return False                                    # error ....
        elif len(root)==1:                                  # only one bookmark root
            rootnode = root[0]                              # 
            self._history(funcname+': -> single-bookmark rootnode: '+str(rootnode.name))
        if len(root)>1:                                     # multiple bookmarks: bundle
            name = '_bookmark_subtree'
            uniqual = _counter(funcname, increment=-1)
            rootnode = ns[name](uniqual) << Meq.Composer(children=root)
            self._history(funcname+': -> multi-bookmark rootnode: '+str(rootnode.name))
        return rootnode



    #--------------------------------------------------------------------------
    # Apply unary operations to the specified groups of MeqNodes:
    #--------------------------------------------------------------------------
    

    def apply_unop (self, ns, group=None, unop=None,
                    bookpage=None, folder=None, trace=False):
        """Apply unary operation(s) to the nodes in the specified group(s).
        The resulting nodes are put into new groups, and a new gog is defined.
        The latter's grouplist is returned."""

        if trace: print '\n** apply_unop(',group,unop,'):'
        gg = self._extract_flat_grouplist(group, must_exist=True, origin='.apply_unop()')
        if not gg: return False
        # if not isinstance(gg, list): return False
        if len(gg)==0: return False

        gog = []
        for g in gg:                                         # for all groups
            gname = self._make_unop_name(g, unop=unop)       # e.g. Cos(g)
            nodes = self.nodes(g, eval=True, trace=trace)    # the eval-nodes of group g
            if isinstance(nodes, list) and len(nodes)>0: 
                self.group(gname, rider=dict(unop=unop))     # define a new group gname
                for node in nodes:
                    node = self._apply_unop(ns, node, unop)
                    self.set_MeqNode(node, group=gname)             
                gog.append(gname)                            # groups for gog (below)

        # Make a gog for the new groups:
        if len(gog)>0:
            # The gogname is made in two stages:
            gogname = self._make_bundle_name(group, trace=False)
            gogname = self._make_unop_name(gogname, unop=unop)
            self.gog(gogname, groups=gog, unop=unop)

            # Define a bookmark, if required:
            if bookpage or folder:
                self.bookmark(gogname, self.gog(gogname),
                              page=bookpage, folder=folder)

            self.history ('.apply_unop('+str(unop)+'): '+str(group)
                          +' (bookpage='+str(bookpage)+')')

            # Return grouplist of the new gog:
            return gogname
        
        # Something wrong if got to here:
        return False

    #....................................................................

    def _apply_unop(self, ns, node=None, unop=None):
        """Recursive helper function to apply (optional) unary operation(s) to node"""
        if unop==None: return node
        unop = self._listuple(unop)
        # if not isinstance(unop, (list, tuple)): unop = [unop]
        for unop1 in unop:
            node = ns << getattr(Meq,unop1)(node)
        return node

    #....................................................................

    def _make_unop_name(self, name=None, unop=None):
        """Helper function to make a inop name"""
        if unop==None: return False
        unop = self._listuple(unop)
        # if not isinstance(unop, (list, tuple)): unop = [unop]
        name = str(name)
        for unop1 in unop:
            name = str(unop1)+'('+name+')'
        return name


    #--------------------------------------------------------------------------
    # Apply binary operations to the specified groups of MeqNodes:
    #--------------------------------------------------------------------------
    
    def apply_binop (self, ns, group=None, binop=None,
                     bookpage=None, folder=None, trace=False):
        """Apply binary operation(s) to the nodes in the specified group(s).
        The resulting nodes are put into a new group, whose name is returned"""

        # trace = True
        if trace: print '\n** apply_binop(',group,binop,'):'
        gg = self._extract_flat_grouplist(group, must_exist=True, origin='.apply_binop()')
        if not isinstance(gg, list): return False
        if not len(gg)==2: return False

        # Get two lists of nodes:
        lhs = self.nodes(gg[0], eval=True, trace=trace)          # left-hand side nodes        
        if not isinstance(lhs, list): return False 
        rhs = self.nodes(gg[1], eval=True, trace=trace)          # right-hand side nodes
        if not isinstance(rhs, list): return False 
        if not len(lhs)==len(rhs): return False
        if len(lhs)==0: return False

        # Make the new group:
        gname = self._make_binop_name(gg, binop=binop)
        self.group(gname, rider=dict(binop=binop))    # define a new group
        for i in range(len(lhs)):
            cc = [lhs[i],rhs[i]]
            node = ns << getattr(Meq,binop)(children=cc)
            self.set_MeqNode(node, group=gname)             

        # Define a bookpage, if required:
        if bookpage or folder:
            self.bookmark(gname, gname, page=bookpage, folder=folder)

        self.history ('.apply_binop('+str(binop)+'): '+str(group)
                      +' (bookpage='+str(bookpage)+')')
        
        # Return the name of the new group:
        return gname

    #....................................................................

    def _make_binop_name(self, name=None, binop=None):
        """Helper function to make a binop name"""
        return str(binop)+'('+str(name[0])+','+str(name[1])+')'




    #--------------------------------------------------------------------------
    # Compare corresponding groups in another NodeSet:
    #--------------------------------------------------------------------------
    
    def compare (self, ns, NodeSet=None, group=None, binop='Subtract',
                 bookpage=None, folder=None, trace=False):
        """Compare (binop) with corresponding nodes in another Nodeset. 
        The resulting nodes are put into new groups, and a new gog is defined."""
        if trace: print '\n** compare(',group,binop,'):'

        gg = self._extract_flat_grouplist(group, must_exist=True, origin='.compare()')
        if not isinstance(gg, list): return False

        gnames = []
        for g in gg:
            if not NodeSet.has_group(g):
                pass                                             # error...?
            else:
                # Get two lists of nodes:
                lhs = self.nodes(g, eval=True, trace=trace)      # left-hand side nodes        
                if not isinstance(lhs, list): return False 
                rhs = NodeSet.nodes(g, eval=True, trace=trace)   # right-hand side nodes
                if not isinstance(rhs, list): return False 
                if not len(lhs)==len(rhs): return False
                if len(lhs)==0: return False
                
                # Make the new group:
                gname = 'compare('+g+')'
                self.group(gname, rider=dict())
                for i in range(len(lhs)):
                    cc = [lhs[i],rhs[i]]
                    node = ns << getattr(Meq,binop)(children=cc)
                    self.set_MeqNode(node, group=gname)             
                gnames.append(gname)

        # Return the bundle root node:
        gogname = self._make_bundle_name(gnames)
        if isinstance(bookpage, bool) and bookpage:          # if bookpage==True: 
            bookpage = gogname                               #   make an automatic name
        node = self.make_bundle(ns, gnames, bookpage=bookpage, folder=folder)
        self.history ('.compare('+str(binop)+'): '+str(NodeSet.label())
                      +' '+str(group)+' '+str(bookpage)+str(folder))
        return node



    #---------------------------------------------------------------------------
    # Some organising functions:
    #---------------------------------------------------------------------------

    def cleanup(self):
      """Remove empty groups/gogs"""

      # Remove empty groups:
      removed = []
      if True:
          for key in self.__group.keys():
              if len(self.__group[key])==0:
                  self.__group.__delitem__(key)
                  self.__group_rider.__delitem__(key)
                  removed.append(key)

      # Remove gogs that have group members that do not exist:
      # NB: One might do the same for bookpages etc....
      for skey in self.__gog.keys():
          ok = True
          for key in self.__gog[skey]:
              if not self.__group.has_key(key):
                  ok = False
          if not ok:
              self.__gog.__delitem__(skey)
              self.__gog_rider.__delitem__(skey)

      # Miscellaneous:
      self.history ('.cleanup():  removed empty group(s): '+str(removed))
      return True

    #-----------------------------------------------------------------

    def update(self, NodeSet=None):
        """Update the essentials from another NodeSet object"""
        if NodeSet==None: return False
        self._updict_rider(NodeSet._rider())
        # NB: update OVERWRITES existing fields with new versions!
        self.__MeqNode.update(NodeSet.MeqNode())
        self.__group.update(NodeSet.group())
        self.__group_rider.update(NodeSet.group_rider())
        self.__plot_color.update(NodeSet.plot_color())
        self.__plot_style.update(NodeSet.plot_style())
        self.__plot_size.update(NodeSet.plot_size())
        self.__bookmark.update(NodeSet.bookmark())
        self.__bundle.update(NodeSet.bundle())
        self.__gog.update(NodeSet.gog())
        self.__gog_rider.update(NodeSet.gog_rider())
        self.history(append='updated from: '+NodeSet.oneliner())
        return True

    def updict(self, NodeSet=None):
        """Updict the essentials from another NodeSet object.
        self._updict(dict,from) is an intelligent form of dict.update(from),
        where the fields of dict are not over-written by the corresponding
        fields of from, but merged according to their type (dict, list, etc)"""
        if NodeSet==None: return False
        self._updict_rider(NodeSet._rider())
        self._updict(self.__MeqNode, NodeSet.MeqNode(), name='MeqNode')
        self._updict(self.__group, NodeSet.group(), name='group')
        self._updict(self.__group_rider, NodeSet.group_rider(), name='group_rider')
        self._updict(self.__plot_color, NodeSet.plot_color(), name='plot_color')
        self._updict(self.__plot_style, NodeSet.plot_style(), name='plot_style')
        self._updict(self.__plot_size, NodeSet.plot_size(), name='plot_size')
        self._updict(self.__bookmark, NodeSet.bookmark(), name='bookmark')
        self._updict(self.__bundle, NodeSet.bundle(), name='bundle')
        self._updict(self.__gog, NodeSet.gog(), name='gog')
        self._updict(self.__gog_rider, NodeSet.gog_rider(), name='gog_rider')
        self.history(append='updicted from: '+NodeSet.oneliner())
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
        self.__quals = dict()       
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
        # Convert MeqNode to a dict of strings:
        # NB: self.__MeqNode entries are now dicts...!
        # saved.__MeqNode = TDL_common.encode_nodestubs(self.__MeqNode)
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
        # Recreate links to NodeStubs, which have to exist in the nodescope 'ns':
        # NB: self.__MeqNode entries are now dicts...!
        # self.__MeqNode = TDL_common.decode_nodestubs(ns, saved.__MeqNode)
        self.history(append='restored: ')
        return True
 


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
    # pp = dict()
    a1 = nst.group('Ggain_X', rider=pp, a=-56, aa=1, bb=1, cc=1)
    a2 = nst.group('Ggain_Y', rider=pp, aa=1, bb=2, cc=1)
    p1 = nst.group('Gphase_X', rider=pp, aa=1, bb=3, cc=2)
    p2 = nst.group('Gphase_Y', rider=pp, aa=1, bb=4, cc=2)
    
    # Define extra gog(s) from combinations of nodegrouns:
    nst.gog('GJones', [a1, p1, a2, p2])
    nst.gog('Gpol1', [a1, p1])
    nst.gog('Gpol2', [a2, p2])
    nst.gog('Gampl', [a1, a2])
    nst.gog('Gphase', [p1, p2])
    nst.gog('grogog', [a1, p2, 'GJones'])

    dummy11 = ns.dummy_test11 << 0.1
    dummy12 = ns.dummy_test12 << 0.1

    # Make nodes themselves:
    freq = ns.freq << Meq.Freq()
    for i in range(nstat):
        for Ggain in [a1,a2]:
            node = ns[Ggain](i=i) << Meq.Multiply(i*mult,freq)
            nst.set_MeqNode(node, group=Ggain)             
         
        for Gphase in [p1,p2]:
            node = ns[Gphase](i=i) << Meq.Multiply(-i*mult,freq)
            nst.set_MeqNode(node, group=Gphase)             
            # nst.append_MeqNode_eval(node.name, append=dummy11)             
            # nst.append_MeqNode_eval(node.name, append=dummy12)             
            nst.append_MeqNode_eval(node.name, append=[dummy12,dummy11])             

    # nst.bookmark('GX', [a1,p1])
    # nst.bookmark('GY', [a2,p2])
    nst.apply_binop(ns, [a1,p1], 'Polar', bookpage='GJones')
    nst.apply_binop(ns, [a2,p2], 'Polar', bookpage='GJones')

    nst.cleanup()
    return nst


#--------------------------------------------------------------------

def test2(ns, nstat=3, mult=1.1):
    """Definition of a NodeSet for testing"""

    nst = NodeSet(label='test2')

    # Register the nodegroups:
    pp = dict(a=-10, b=-11)
    a1 = nst.group('Ggain_X', rider=pp, aa=1, bb=1, cc=1)
    a2 = nst.group('Ggain_Y', rider=pp, aa=1, bb=2, cc=1)
    p1 = nst.group('Gphase_X', rider=pp, aa=1, bb=3, cc=2)
    p2 = nst.group('Gphase_Y', rider=pp, aa=1, bb=4, cc=2)
    t2 = nst.group('test2', rider=pp, aa=1, bb=4, cc=2)
    
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
            nst.set_MeqNode(node, group=Ggain)             
         
        for Gphase in [p1,p2]:
            node = ns[Gphase](i=i) << Meq.Multiply(-i*mult,freq)
            nst.set_MeqNode(node, group=Gphase)             

    nst.bookmark('GX', [a1,p1], folder='test2')
    nst.bookmark('GY', [a2,p2], folder='test2')

    nst.cleanup()
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

    if 1:
        rootnode = nst.dataCollect(ns)
        TDL_display.subtree(rootnode, 'dataCollect')

    if 0:
        for key in nst.keys():
            nst.MeqNode_eval(key, trace=True)
        nst.nodenames(trace=True)
        nst.nodenames(eval=True, trace=True)

    if 0:
        gg = nst.group_keys()
        # gg.append('xxx')
        gg = 'GJones'                      
        gg = ['GJones',['Gampl','Gpol1',['Gpol2']]]                      
        # gg = ['GJones',['Gampl','Gpol1',['xxx']]]                      
        select = '*'
        # select = 'first'
        nn = nst.nodenames (gg, select=select, trace=True)
        # nn = nst.nodes (gg, select=select, trace=True)

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
        bb = nst.make_bundle(ns, 'grogog', bookpage=True)
        TDL_display.subtree(bb, 'bundle', full=True, recurse=3)
        
    if 0:
        kk = nst.group_keys()
        r = nst.group_rider_item(item='color', key=None, trace=True)
        r = nst.group_rider_item(item='color', key=kk[0], trace=True)
        r = nst.group_rider_item(item='color', key=[kk[0],kk[1]], trace=True)

    if 0:
        kk = nst.group_keys()
        r = nst.plot_color(key=None, trace=True)
        r = nst.plot_color(key=kk[0], trace=True)
        r = nst.plot_color(key=[kk[0],kk[1]], trace=True)
        r = nst.plot_style(key=[kk[0],kk[1]], trace=True)
        r = nst.plot_size(key=[kk[0],kk[1]], trace=True)

    if 1:
        nst.apply_unop(ns, 'GJones', 'Cos', bookpage=True)

    if 0:
        nst.apply_binop(ns, [a1,p1], 'Polar', bookpage=True)

    if 0:
        nst.ensure_bookmarks(ns)
        JEN_bookmarks.current_settings(trace=True)

    if 0:
        root = nst.bookmark_subtree(ns, trace=True)
        TDL_display.subtree(root, 'bookpage_subtree', full=True, recurse=3)

    #--------------------------------------------------------------------------
    # Functions involving a second NodeSet:
    #--------------------------------------------------------------------------
    
    if 0:
        nst2 = test2(ns)
        nst2.display('nst2', full=True)

    if 0:
        nst.compare(ns, nst2, 'GJones', bookpage=True)

    if 0:
        # nst.update(nst2)
        nst.updict(nst2)

    #--------------------------------------------------------------------------

    if 0:
        nst.display(full=True)
        # nst.display()

    if 1:
        # Display the final result:
        # k = 0 ; TDL_display.subtree(ns[k], 'ns['+str(k)+']', full=True, recurse=3)
        nst.display('final result', full=True)

    print '\n*******************\n** End of local test of: TDL_NodeSet.py:\n'




#============================================================================================









 

