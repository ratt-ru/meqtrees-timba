# TDL_Nodeset.py
#
# Author: J.E.Noordam
#
# Short description:
#    A Nodeset object encapsulates group(s) of MeqNodes
#
# History:
#    - 03 mar 2006: creation from TDL_Parmset.py
#
# Full description:
#   Many types of MeqTree nodes (e.g. MeqParms) come in groups of similar ones,
#   which are dealt with as a group. The Nodeset object provides a
#   convenient way to define and use such groups in various ways. 
#
#   A Nodeset object contains the following main components:
#   - A list of named groups, i.e. lists of MeqNode names. 
#   - A list of named gogs, i.e. lists of one or more group (or gog) names.


#=================================================================================
# Preamble:
#=================================================================================

from Timba.TDL import *

from copy import deepcopy
from random import *
from math import *
from numarray import *

from Timba.Trees import TDL_common
# from Timba.Trees import TDL_radio_conventions
from Timba.Trees import JEN_bookmarks




#=================================================================================
# Class Nodeset
#=================================================================================


class Nodeset (TDL_common.Super):
    """A Nodeset object encapsulates an (arbitrary) set of MeqNode nodes"""

    def __init__(self, **pp):

        TDL_common.Super.__init__(self, type='Nodeset', **pp)
        self.clear()
        return None

    def clear(self):
        """Clear the object"""
        self.__quals = dict()                # record of default node-name qualifiers
        self.__MeqNode = dict()
        self.__group = dict()
        self.__group_rider = dict()
        self.__plot_color = dict()
        self.__plot_style = dict()
        self.__plot_size = dict()
        self.__buffer = dict()
        self.__gog = dict()
        self.__gog_rider = dict()

    #--------------------------------------------------------------------------------
    # Convenience (service)
    #--------------------------------------------------------------------------------

    def quals(self, new=None, clear=False):
        """Get/set the default MeqNode node-name qualifier(s)"""
        if clear:
            self.__quals = dict()
        if isinstance(new, dict):
            for key in new.keys():
                self.__quals[key] = str(new[key])
        return self.__quals

    #--------------------------------------------------------------------------------
    # Display functions:
    #--------------------------------------------------------------------------------
            
    def oneliner(self):
        """Make a one-line summary of this Nodeset object"""
        s = TDL_common.Super.oneliner(self)
        # if len(self.quals())>0:
        s += ' quals='+str(self.quals())
        s += ' pg:'+str(len(self.group()))
        s += ' sg:'+str(len(self.gog()))
        # s += ' '+str(self.node_groups())
        return s


    def display(self, txt=None, full=False):
        """Display a description of the contents of this Nodeset object"""
        ss = TDL_common.Super.display (self, txt=txt, end=False, full=full)
        indent1 = 2*' '
        indent2 = 6*' '
 
        #------------------------
        ss.append(indent1+' - Registered groups ('+str(len(self.group()))+'):')
        for key in self.group().keys():
            group = self.group(key)
            n = len(group)
            if full or n<3:
                ss.append(indent2+' - '+key+' ( '+str(n)+' ): '+str(group))
            else:
                ss.append(indent2+' - '+key+' ( '+str(n)+' ): '+group[0]+' ... '+group[n-1])

        #------------------------
        if full:  
            ss.append(indent1+' - group riders ('+str(len(self.group_rider()))+'):')
            for key in self.group_rider().keys():
                if len(self.group_rider()[key])>0:
                    ss.append(indent2+' - '+key+': '+str(self.group_rider()[key]))

        #------------------------
        ss.append(indent1+' - Defined gogs ('+str(len(self.gog()))+'):')
        for key in self.gog().keys():
            ss.append(indent2+' - '+key+' :     groups: '+str(self.gog(key)))

        #------------------------
        if full:
            ss.append(indent1+' - gog riders ('+str(len(self.gog_rider()))+'):')
            for key in self.gog_rider().keys():
                if len(self.gog_rider()[key])>0:
                    ss.append(indent2+' - '+key+': '+str(self.gog_rider()[key]))

        #------------------------
        if full:
            ss.append(indent1+' - Contents of temporary buffer:')
            for key in self.buffer().keys():
                ss.append(indent2+' - '+key+': '+str(self.buffer()[key]))

        #------------------------
        ss.append(indent1+' - Available MeqNode nodes ( '+str(len(self.__MeqNode))+' ):')
        keys = self.__MeqNode.keys()
        n = len(keys)
        if full or n<10:
            for key in keys:
                ss.append(indent2+' - '+key+' : '+str(self.__MeqNode[key]))
        else:
            ss.append(indent2+' - first: '+keys[0]+' : '+str(self.__MeqNode[keys[0]]))
            ss.append(indent2+'   ....')
            ss.append(indent2+' - last:  '+keys[n-1]+' : '+str(self.__MeqNode[keys[n-1]]))

        return TDL_common.Super.display_end (self, ss)



    #--------------------------------------------------------------------------------
    # Functions related to MeqNode nodes: 
    #--------------------------------------------------------------------------------

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

    #-------------------------------------------------------------------------------------

    def MeqNode(self, key=None, node=None, trace=True):
        """Get/create a named MeqNode entry"""
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


    #--------------------------------------------------------------------------------
    # Convenience (service)
    #--------------------------------------------------------------------------------

    # When a new MeqNode entry is made (see .MeqNode(), the node stub is put into the
    # internal buffer for later use. This is a convenience service that allows access
    # to the most recently defined MeqNodes by means of their group name, rather than
    # their full name (e.g. see MG_JEN_Joneset.py) 

    def buffer(self):
        """Get the temporary helper record self.__buffer"""
        return self.__buffer


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

            self.__group[key] = []                  # initialise the group with an empty list
            self.__group_rider[key] = pp            # extra info associated with the group
            self.__plot_color[key] = pp['color']
            self.__plot_style[key] = pp['style']
            self.__plot_size[key] = pp['size']

            # Automatically create a gog of the same name...:
            self.gog(key, groups=key, automatic=True) 

            qq = TDL_common.unclutter_inarg(pp)
            # self.history('** Defined group: '+key+':  rider = '+str(qq))
            self.history('** Defined group: '+key+':  rider keys: '+str(qq.keys()))
            return key                              # return the actual group key name
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

    def group_keys (self, select='*'):
        """Return the names (keys) of the available groups"""
        return self.__group.keys()

    def is_group (self, key):
        """Check whether the specified (key) group exists"""
        return self.__group.has_key(key)


    def nodes(self, group=None, select='*', trace=False):
        """Return a list of actual MeqNodes in the specified group(s)"""
        if trace: print '\n** .nodes(',group,'):'
        names = self.nodenames(group, select=select, trace=trace)
        if not isinstance(names, (list,tuple)): return False
        nn = []
        for name in names:
            nn.append(self.__MeqNode[name])
        if trace: print '(',len(nn),'):',nn,'\n'
        return nn

    def nodenames (self, group=None, select='*', trace=False):
        """Return a list of the MeqNode names in the specified group(s)"""
        if trace: print '** .nodenames(',group,'):'
        gg = self._extract_flat_grouplist(group, must_exist=True, origin='.nodes()')
        if not isinstance(gg, (list,tuple)): return False
        if trace: print '    -> groupnames(',len(gg),'):',gg
        names = []
        for key in gg:
            names.extend(self.__group[key])
        if trace: print '    -> nodenames(',len(names),'):',names
        return names

    def select_groups (self, name=None, substring=True, rider=None, trace=False):
        """Return a list of groups according to the selection criteria"""
        if trace: print '** .select_groups(',name,substring,rider,'):'
        gg = self._extract_flat_grouplist(name, must_exist=False, origin='.select_groups()')
        if not isinstance(gg, (list,tuple)): return False
        if trace: print '    extract: groups(',len(gg),'):',gg

        # Match substrings in group keys, if required:
        if substring:
            cc = []
            for g in gg:
                for key in self.group_keys():
                    if key.rfind(g)>=0:
                        cc.append(key)
            gg = cc
            if trace: print '    substring: groups(',len(gg),'):',gg

        # Select on group_rider criteria, if specified:
        if isinstance(rider, dict):
            cc = []
            for g in gg:
                ok = True
                rr = self.__group_rider[g]
                for key in rider.keys():
                    if rr.has_key(key):
                        v = rider[key]
                        if isinstance(v, (list, tuple)):
                            if not v.__contains__(rr[key]): ok = False
                        else:
                            if (not v==rr[key]): ok = False
                        print '     -',g,key,':',v,'<->',rr[key],'    ok =',ok
                if ok: cc.append(g)
            gg = cc
            if trace: print '    rider: groups(',len(gg),'):',gg

        # Return the list of selected group names:
        if trace: print '    -> groups(',len(gg),'):',gg
        return gg

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
                if not self.is_group(g):
                    return self.history(error=s1+'group available but invalid: '+g)
                if not gg.__contains__(g): gg.append(g)
            elif self.__gog.has_key(g):                             # gog exists
                gg1 = self._extract_flat_grouplist(self.__gog[g], origin=origin,
                                                  must_exist=must_exist, level=level+1)
                if not isinstance(gg1, list): return False
                for g1 in gg1:
                    if not gg.__contains__(g1): gg.append(g1)
            elif must_exist:                                        # must exist
                return self.history(error=s1+'group not available: '+g)
            else:                                                   # does not have to exist
                if not gg.__contains__(g): gg.append(g)
        return gg


    #--------------------------------------------------------------------------------
    # Functions related to group-of-groups (gogs):
    #--------------------------------------------------------------------------------

    def gog (self, key=None, groups=None, **pp):
        """Get/define the named (key) group-of-groups (gog)"""
        if groups:                                  # define a new gog
            if key==None:                  
                return self.history(error='gog('+str(groups)+'): no key specified')
            gg = self._extract_flat_grouplist(groups, must_exist=False)
            if not isinstance(gg, list): return False
                
            if not isinstance(groups, list): groups = [groups]
            self.__gog[key] = groups                # list of gog groups/gogs
            self.__gog_rider[key] = pp              # extra info associated with the gog

            qq = TDL_common.unclutter_inarg(pp)
            # self.history('** Defined gog: '+key+':  '+str(groups)+',  rider = '+str(qq))
            self.history('** Defined gog: '+key+':  '+str(groups)+',  rider keys:'+str(qq.keys()))
            return key                              # return the actual gog key name
        # Otherwise, return the specified (key) group (None = all):
        return self._fieldict (self.__gog, key=key, name='.gog()')


    def gog_rider(self, key=None):
        """Get the specified (key) gog_rider (None = all)"""
        return self._fieldict (self.__gog_rider, key=key, name='.gog_rider()')

    def gog_keys (self, select='*'):
        """Return the names (keys) of the available gogs"""
        return self.__gog.keys()

    def is_gog (self, key=None):
        """Check whether the specified (key) gog exists"""
        return self.__gog.has_key(key)


    #--------------------------------------------------------------------------
    # Make a subtree of MeqNode bundles (also MeqNodes), e.g. for plotting:
    #--------------------------------------------------------------------------
    
    def bundle (self, ns, group=None, name=None, bookpage='NodeSet.groups'):
        """Return a subtree of (the sum(s) of) the nodes in the specified group(s)"""
        if trace: print '\n** bundle(',group,name,bookpage,'):'
        gg = self._extract_flat_grouplist(group, must_exist=True)
        if not isinstance(gg, list): return False
        if len(gg)==0: return False

        # The bundles of multiple groups are bundled:
        multiple = (len(gg)>1)               
        if multiple:
            if not isinstance(name, str):
                name = self.bundle_name(group)
            bname = 'NodeSet_bundle_'+str(name)
            if self.__MeqNode.has_key(bname):                # bundle already exists
                return self.__MeqNode[bname]                 # just return it

        # Make (a bundle of) group bundle(s): 
        cc = []
        gname = None
        for g in gg:                                         # for all groups
            nodes = self.nodes(g, trace=trace)               # their nodes
            if isinstance(nodes, list): 
                n = len(nodes)
                if n>0: 
                    gname = 'sum_'+str(g)+'('+str(n)+')'
                    if not self.__MeqNode.has_key(gname):    # does not exist yet
                        node = ns[gname] << Meq.Add(children=nodes)
                        self.__MeqNode[gname] = node
                        if isinstance(bookpage, str): 
                            JEN_bookmarks.bookmark(node, page=bookpage)
                    cc.append(self.__MeqNode[gname])  

        # Return the root node of the subtree:
        if not multiple:
            if gname: return self.__MeqNode[gname]           # single group
        elif len(cc)>0:
            self.__MeqNode[bname] = ns[bname] << Meq.Composer(children=cc)
            return self.__MeqNode[bname]
        # Something wrong if got to here:
        return False


    #------------------------------------------------------------------------

    def bundle_name (self, group):
        """Make a decriptive bundle name of a flat list of groupnames"""
        if isinstance(group, str):
            if self.__gog.has_key(group): return 'gog:'+group
            return group
        elif isinstance(group, (list, tuple)):
            if len(group)==1: return group[0]
        gg = self._extract_flat_grouplist(group, must_exist=True)
        name = ''
        for g in gg:
            name += g[0]
            if len(g)>1: name += g[1]
        name += '('+str(len(gg))+')'
        return name


    #--------------------------------------------------------------------------
    # Apply unary operations to the specified groups of MeqNodes:
    #--------------------------------------------------------------------------
    

    def apply_unop (self, ns, group=None, unop=None):
        """Apply unary operation(s) to the nodes in the specified group(s).
        The resulting nodes are put into new groups, and a new gog is defined"""
        if trace: print '\n** apply_unop(',group,unop,'):'
        gg = self._extract_flat_grouplist(group, must_exist=True)
        if not isinstance(gg, list): return False
        if len(gg)==0: return False
        gog = []
        for g in gg:                                         # for all groups
            gname = self._unop_name(g, unop=unop)
            nodes = self.nodes(g, trace=trace)               # their nodes
            if isinstance(nodes, list): 
                gog.append(gname)
                self.group(gname, unop=unop)
                for node in nodes:
                    node = self._apply_unop(ns, node, unop)
                    self.MeqNode(gname, node)

        # Make a gog for the new groups:
        if len(gog)>0:
            gogname = self.bundle_name(group)
            gogname = self._unop_name(gogname, unop=unop)
            self.gog(gogname, unop=unop)
            return gogname
        # Something wrong if got to here:
        return False


    def _apply_unop(self, ns, node=None, unop=None):
        """Helper function to apply (optional) unary operation(s) to node"""
        if unop==None: return node
        if not isinstance(unop, (list, tuple)): unop = [unop]
        for unop1 in unop:
            node = ns << getattr(Meq,unop1)(node)
        return node

    def _unop_name(self, name=None, unop=None):
        """Helper function to make a inop name"""
        if unop==None: return False
        if not isinstance(unop, (list, tuple)): unop = [unop]
        name = str(name)
        for unop1 in unop:
            name = str(unop1)+'('+name+')'
        return name



#---------------------------------------------------------------------------
#---------------------------------------------------------------------------

    def cleanup(self):
      """Remove empty groups/gogs"""
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
      self.history ('.cleanup(): removed group(s): '+str(removed))
      return True


    def update(self, Nodeset=None):
        """Update the essentials from another Nodeset object"""
        if Nodeset==None: return False
        # NB: update OVERWRITES existing fields with new versions!
        self.__MeqNode.update(Nodeset.MeqNode())
        self.__group.update(Nodeset.group())
        self.__group_rider.update(Nodeset.group_rider())
        self.__plot_color.update(Nodeset.plot_color())
        self.__plot_style.update(Nodeset.plot_style())
        self.__plot_size.update(Nodeset.plot_size())
        self.__gog.update(Nodeset.gog())
        self.__gog_rider.update(Nodeset.gog_rider())
        self.history(append='updated from: '+Nodeset.oneliner())
        return True


#----------------------------------------------------------------------
#   methods used in saving/restoring the Nodeset
#----------------------------------------------------------------------

    def clone(self):
        """clone self such that no NodeStubs are present. This 
           is needed to save the Nodeset."""
        
        #create new Nodeset
        newp=Nodeset()
        newp.__quals=self.__quals
        newp.__group=self.__group
        newp.__group_rider=self.__group_rider
        newp.__gog=self.__gog
        newp.__plot_color=self.__plot_color
        newp.__plot_style = self.__plot_style
        newp.__plot_size = self.__plot_size
        # convert MeqNode to a dict of strings
        newp.__MeqNode={}
        for key in self.__MeqNode.keys():
             pgk=self.__MeqNode[key]
             if isinstance(pgk,Timba.TDL.TDLimpl._NodeStub):
               newp.__MeqNode[key]={'__type__':'nodestub','name':pgk.name}
             else:
               newp.__MeqNode[key]=pgk

        return newp

    def restore(self,oldp,ns):
        """ recreate the Nodeset from a saved version 'oldp'"""
        self.__quals=oldp.__quals
        self.__group=oldp.__group
        self.__group_rider=oldp.__group_rider
        self.__gog=oldp.__gog
        self.__plot_color=oldp.__plot_color
        self.__plot_style = oldp.__plot_style
        self.__plot_size = oldp.__plot_size
        # recreate links to NodeStubs, which have to exist in the 
        # nodescope 'ns'
        self.__MeqNode={}
        mydict=oldp.__MeqNode
        for key in mydict.keys():
           pgk=mydict[key]
           if isinstance(pgk,dict):
               if pgk.has_key('__type__') and pgk['__type__']=='nodestub':
                   # look for canonical name
                   alist=string.split(pgk['name'],":q=")
                   #print alist
                   nodestub=None
                   if len(alist)==1:
                      nodestub=ns[alist[0]]
                      self.__MeqNode[pgk['name']]=nodestub
                   else:
                      wstr="nodestub=ns."+alist[0]+"(q='"+alist[1]+"')"
                      exec wstr
                      self.__MeqNode[pgk['name']]=nodestub

 



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
    if trace: print '** Nodeset: _counters(',key,') =',_counters[key]
    return _counters[key]






#========================================================================
# Test routine:
#========================================================================

if __name__ == '__main__':
    print '\n*******************\n** Local test of: TDL_Nodeset.py:\n'
    from numarray import *
    from Timba.Trees import TDL_display
    # from Timba.Trees import JEN_record
    ns = NodeScope()
    
    # stations = range(3)
    nst = Nodeset(label='initial')
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
        # Register the nodegrouns:
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

        for i in range(2):
            for Ggain in [a1,a2]:
                node = ns[Ggain](i=i) << 1.0
                nst.MeqNode (Ggain, node=node)
                
            for Gphase in [p1,p2]:
                node = ns[Gphase](i=i) << 0.0
                nst.MeqNode (Gphase, node=node)

    if 0:
        gg = nst.group_keys()
        # gg.append('xxx')
        gg = 'GJones'                      
        gg = ['GJones',['Gampl','Gpol1',['Gpol2']]]                      
        # gg = ['GJones',['Gampl','Gpol1',['xxx']]]                      
        nn = nst.nodenames (gg, select='*', trace=True)
        nn = nst.nodes (gg, select='*', trace=True)

    if 1:
        name = None
        name = 'Gp'
        rider = None
        rider = dict(bb=[2,3,None], aa=[1,2])
        nst.select_groups (name=name, substring=True, rider=rider, trace=True)

    if 0:
        # bb = nst.bundle(ns)
        bb = nst.bundle(ns, 'grogog')
        TDL_display.subtree(bb, 'bundle', full=True, recurse=3)
        
    if 0:
        nst.apply_unop(ns, 'GJones', 'Cos')

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
        nst.display(full=True)
        # nst.display()


    if 0:
        # Display the final result:
        # k = 0 ; TDL_display.subtree(ns[k], 'ns['+str(k)+']', full=True, recurse=3)
        nst.display('final result')

    print '\n*******************\n** End of local test of: TDL_Nodeset.py:\n'




#============================================================================================









 

