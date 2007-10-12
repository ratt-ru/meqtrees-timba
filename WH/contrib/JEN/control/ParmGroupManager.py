# file: ../control/ParmGroupManager.py

# History:
# - 17jul2007: creation (from ParameterizationPlus.py)
# - 24jul2007: adapted to OptionManager
# - 17sep2007: get OptionManager from /control/
# - 24sep2007: move to ../JEN/control/
# - 05oct2007: adapt to OMInterface
# - 11oct2007: remove ParameterizationPlus inheritance

# Description:

# This class encapsulates a collection of ParmGroup objects.


#======================================================================================

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

# import Meow

from Timba.Contrib.JEN.control import OMInterface
from Timba.Contrib.JEN.control import ParmGroup
from Timba.Contrib.JEN.NodeList import NodeList
from Timba.Contrib.JEN.Grunt import display

# from copy import deepcopy

#======================================================================================

class ParmGroupManager (object):
    """The Grunt ParmGroupManager class encapsulates a group of ParmGroups.
    """

    def __init__(self, ns=None,
                 name='<PGM>',
                 quals=None,
                 # kwquals=None,
                 OM=None, namespace=None,
                 submenu='compile',
                 solvermenu=None,
                 **kwargs):

        self.name = name
        self.ns = ns

        # Scopify ns, if necessary:
        if is_node(ns):
            self.ns = ns.QualScope()        

        # Make sure that there is a nodescope (Required by Meow.Parameterization)
        if ns==None:
            ns = NodeScope()
        
        self._submenu = submenu
        self._solvermenu = solvermenu

        self._frameclass = 'control.ParmGroupManager'       # for reporting

        # Initialize local data:
        self._parmgroups = dict()
        self._order = []

        self._mode = None
        self._modes = dict()
        self._modes_order = []

        self._parmgogs = dict()

        self._pmerged = []

        self._accumulist = dict()                           # ....?

        #------------------------------------------------------------------
        # Options management:

        self._solvermenu = solvermenu

        self._OMI = OMInterface.OMInterface(quals,
                                            name=self.name,
                                            submenu=submenu,
                                            OM=OM, namespace=namespace,
                                            **kwargs)

        return None


    #---------------------------------------------------------------

    def nodescope (self, ns=None):
        """Get/set the internal nodescope (can also be a node)"""
        if ns:
            if is_node(ns):
                self.ns = ns.QualScope()        
            else:
                self.ns = ns
            key = self.name
            self.ns = self.ns[key](key).QualScope()            #.....!!?
        return self.ns

    #---------------------------------------------------------------

    def __getitem__ (self, key):
        """Get (a reference to) the specified parmgroup"""
        if not isinstance(key, str):
            s = 'invalid key: '+str(key)
            raise ValueError,s
        elif not key in self._parmgroups:
            s = 'key not recognized: '+str(key)
            raise ValueError,s
        return self._parmgroups[key]


    def active_groups (self, new=None):
        """Get/set the list of (names of) 'active' parmgroups.
        Reimplementation of the square-brackets call: pg = PGM[key]"""
        active = []
        for key in self._parmgroups.keys():
            pg = self._parmgroups[key]
            if isinstance(new, (list,tuple)):
                pg.active(key in new)
            if pg.active():
                active.append(key)
        if new:
            self.TDLShowActive()

        # Make a new set of parmgogs (of active groups):
        gogs = self.gogs()

        # Finished:
        return active

    #-------------------------------------------------------------------

    def cleanup (self):
        """Remove the inactive (unused) ParmGroups"""
        return True


    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = 'Grunt.ParmGroupManager:'
        ss += '  (name='+str(self.name)+')'
        if self._solvermenu:
            ss += '  (solvermenu='+str(self._solvermenu)+')'
        # ss += '  ('+str(self.ns['<>'].name)+')'
        return ss


    def display(self, txt=None, full=False, recurse=3, OM=False, pg=False, level=0):
        """Print a summary of this object"""
        prefix = '  '+(level*'  ')+'PGM'
        if level==0: print
        print prefix,' '
        print prefix,'** '+self.oneliner()
        if txt: print prefix,'  * (txt='+str(txt)+')'
        #...............................................................
        print prefix,'  * Grunt parmgroups ('+str(len(self._parmgroups))+'):'
        for key in self._order:
            pg = self._parmgroups[key]
            if pg.active():
                print prefix,'    - ('+key+'): '+str(pg.oneliner())
            else:
                print prefix,'    - ('+key+'):   ... not active ...'
        #...............................................................
        print prefix,'  * mode(s) (mode='+str(self._mode)+'):'
        for key in self._modes_order:
            print prefix,'    - ('+str(key)+'): '+str(self._modes[key])
        #...............................................................
        print prefix,'  * Grunt _parmgogs (groups of parmgroups, derived from their node tags):'
        for key in self.gogs():
            print prefix,'    - ('+str(key)+'): '+str(self._parmgogs[key])
        #...............................................................
        print prefix,'  * Accumulist entries: '
        for key in self._accumulist.keys():
            vv = self._accumulist[key]
            print prefix,'    - '+str(key)+' ('+str(len(vv))+'):'
            if full:
                for v in vv: print prefix,'    - '+str(type(v))+' '+str(v)
        #...............................................................
        print prefix,'  * '+self._OMI.oneliner()
        if OM: self._OMI.display(full=False, level=level+1)
        #...............................................................
        if pg: self.pg_display(OM=OM, level=level+1)
        #...............................................................
        print prefix,'**'
        if level==0: print
        return True

    #---------------------------------------------------------------

    def pg_display(self, full=False, OM=False, level=0):
        """Display summaries of its parmgroups"""
        for key in self._parmgroups.keys():
            self._parmgroups[key].display(full=full, OM=OM, level=level)
        return True



    #===============================================================
    # Its TDL options:
    #===============================================================

    def make_TDLCompileOptionMenu (self, **kwargs):
        """Make the TDL menu of Compile-time options.
        NB: the ParmGroup options will be included automatically
        """
        return self._OMI._OM.make_TDLCompileOptionMenu(**kwargs)
    
    #---------------------------------------------------------------

    def define_mode_option(self, doc='<no help available>',
                           prompt='select parameterization mode'):
        """Define TDL option that selects the parameterization mode (if any).
        NB: This function should be called AFTER all ParmGroups
        have been defined (see .add_ParmGroup())
        """
        modes = self._modes_order
        if len(modes)>0:
            self._OMI.defopt('mode', modes[0], opt=modes,
                             callback=self._callback_mode,
                             prompt=prompt, doc=doc)
        return True

    #...............................................................

    def _callback_mode (self, mode):
        """Called whenever option 'mode' changes"""
        self._mode = mode
        for key in self._order:
            self._parmgroups[key].hide()
        for key in self._modes[self._mode]:
            self._parmgroups[key].hide(hide=False)
        return True

    #-------------------------------------------------------------------

    def modes_order(self):
        """Get an ordered list of the available modes"""
        return self._modes_order

    def mode(self):
        """Get the current mode..."""
        return self._mode


    #===============================================================
    # ParmGroups:
    #===============================================================

    def parmgroups (self):
        """Return a list of names of the available parmgroups"""
        return self._parmgroups.keys()

    def has_parmgroup (self, key, severe=False):
        """Test whether it has a parmgroup of this name (key).
        If severe==True, raise a ValueError if it does not"""
        if self._parmgroups.has_key(key): return True
        if severe:
            s = '** parmgroup not recognized: '+str(key)
            raise ValueError, s
        return False


    #---------------------------------------------------------------

    def add_ParmGroup (self, key, mode=None,
                       submenu=None, solvermenu=None,
                       **kwargs):
        """Create a ParmGroup with the specified arguments,
        and add it to the internal repository"""

        # Check whether the group exists already:
        if self._parmgroups.has_key(key):
            s = '** duplicate parmgroup definition: '+str(key)
            raise ValueError,s

        # If not supplied explicitly, use the solvermenu that was
        # specified by the constructor (which may also be None):
        if not isinstance(solvermenu, str):
            solvermenu = self._solvermenu

        if not isinstance(kwargs, dict):
            kwargs = dict()
        kwargs.setdefault('tags', [])

        if True:
            # Some added value:
            tags = self.tags2list(kwargs['tags'])
            if True:
                if self.name:
                    if not self.name in tags:
                        tags.append(self.name)    
            kwargs['tags'] = tags

        # Create the ParmGroup:
        pg = ParmGroup.ParmGroup (self.ns, key,
                                  submenu=self._OMI._submenu,
                                  solvermenu=self._solvermenu,
                                  OM=self._OMI._OM,
                                  namespace=None,
                                  **kwargs)

        # Add the new ParmGroup to the repository:
        self._order.append(key)
        self._parmgroups[key] = pg

        # A ParmGroup may belong to one or more 'modes':
        if isinstance(mode,str):
            mode = [mode]
        if isinstance(mode, (list,tuple)):
            for m1 in mode:
                if isinstance(m1,str):
                    if not self._modes.has_key(m1):
                        self._modes[m1] = []
                        self._modes_order.append(m1)
                    self._modes[m1].append(key)

        # Finished:
        return key

    #-------------------------------------------------------------------

    def order(self, active=True):
        """Get an ordered list of the available parmgroup keys"""
        return self._order

    #-------------------------------------------------------------------

    def simuldev_expr (self, ampl='{0.01~10%}', Psec='{500~10%}', PHz=None):
        """Helper function to make a standard simuldev expression.
        All arguments must be strings of the form {<value>~<stddev>}.
        The <stddev> is used to generate different values around <value>
        for each member of the group (see .group_create_member())."""
        s = ampl
        if isinstance(Psec,str):
            s += ' * sin(2*pi*([t]/'+Psec+'+{0~1}))'
        if isinstance(PHz,str):
            s += ' * sin(2*pi*([f]/'+PHz+'+{0~1}))'
        return s


    #===============================================================
    # Merge the parametrization of another object in its own.
    #===============================================================

    # NB: One should be careful with this since it has merit to keep 
    #     parameter sets with the same names but different qualifiers apart.
    #     But it is useful for merging parametrizations in the same subtree.
    #     For instance, a JJones object, which is the multiplication of 
    #     multiple Jones matrices, with DIFFERENT parmgroup names.

    def merge (self, other, trace=False):
        """Merge the parm contents with those of another object.
        The latter must be derived of Meow.Parametrization, but
        it may or may not be derived from Grunt.ParmGroupManager.
        If not, it will copy the parmdefs, but not any parmgroups."""
        
        if trace:
            self.display('before PGM.merge()', full=True)
            ff = getattr(other, 'display', None)
            if ff: other.display('other', full=True)

        if other in self._pmerged:
            # print '\n** merge(): skipped (merged before): ',str(other),'\n'
            return True


        # Check whether the other object has a Grunt.ParmGroupManager
        PGM = getattr(other, '_PGM', None)
        print '\n** PGM =',type(PGM), isinstance(PGM, ParmGroupManager),'\n'
        if isinstance(PGM, ParmGroupManager):
            # The other object DOES have a Grunt.ParmGroupManager
            self._pmerged.append(other)               # Avoid duplicate merging....
            
            # Copy its ParmGroup(s) (objects):
            # NB: Avoid duplicate parmgroups (solvable and simulated versions
            # of the same Joneset should be compared, rather than merged!).
            pgs = PGM._parmgroups
            for key in pgs:
                if not pgs[key].active():
                    print '** skipping inactive parmgroup:',key
                else:
                    if self._parmgroups.has_key(key):
                        if self._parmgroups[key].active():
                            s = '** cannot merge duplicate parmgroups: '+key 
                            raise ValueError, s
                        print '** overwriting inactive parmgroup:',key
                    self._parmgroups[key] = pgs[key]


        # Check whether the other object is derived from Meow.Parameterization
        elif isinstance(rr, getattr(other, '_parmdefs', None)):
            rr = getattr(other, '_parmdefs', None)
            # The other object IS derived from Meow.Parameterization
            self._pmerged.append(other)               # avoid duplicate merging....

            # Make a single parmgroup from its parmnodes
            # Copy the parmdefs with slightly different names
            descr = 'copied from Meow.Parameterization of: '
            if getattr(other,'oneliner',None):
                descr += str(other.oneliner())
            else:
                descr += str(other.name)
            self.define_parmgroup (other.name, tags=None, descr=descr)
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


        else:
            # Error?
            pass

        if trace:
            self.display('after PGM.merge()', full=True)
        return True



    #===============================================================
    # Convenient access to a list of nodes/subtrees, e.g. for solving
    #===============================================================


    def tobesolved (self, return_nodes=True, return_NodeList=False, trace=False):
        """Get a list of the parmgroups (or tags?) that have been selected for solving.
        If return_nodes or return_NodeList (object), do that."""
        pgs = self._tobesolved
        if return_nodes or return_NodeList:
            return self.solvable(groups=pgs, trace=trace,
                                    return_NodeList=return_NodeList)
        elif trace:
            print '\n** tobesolved: ',pgs,'\n'
        return pgs


    #----------------------------------------------------------------

    def solvable (self, tags=None, groups='*', return_NodeList=False, trace=False):
        """Return a list with the specified selection of solvable MeqParm nodes.
        The nodes may be specified by their tags (n.search) or by parmgroups."""
        return self.find_nodes (tags=tags, groups=groups,
                                  return_NodeList=return_NodeList,
                                  solvable=True, trace=trace)


    #----------------------------------------------------------------

    def find_nodes (self, tags=None, groups='*', solvable=None,
                    return_NodeList=False, trace=False):
        """Return a list with the specified selection of the nodes (names)
        that are known to this Parameterization object. The nodes may be
        specified by their tags (n.search) or by parmgroups. The defaults are
        tags=None and groups='*', but tags are checked first."""

        if trace:
            print '\n** find_nodes(tags=',tags,', groups=',groups,', solvable=',solvable,'):'
        nodes = []
        labels = []
        name = 'parms'

        if tags:
            # A tags specification has precedence:
            # NB: Should we search the nodescopes of its parmgroups?
            #     (assuming that those have been derived from self.ns...?)
            tags = self.tags2list(tags)
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
            pgs = self.find_parmgroups (groups, severe=True)
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

    def find_parmgroups (self, groups, severe=True, trace=False):
        """
        Helper function to covert the specified groups (parmgroups or gogs)
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
        self._make_gogs()
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

    def gogs (self):
        """Return the list of available groups of parmgroups (gogs).
        These are used in finding groups, e.g. for solving."""
        return self._make_gogs().keys()


    def _make_gogs (self):
        """Derive a dict of named groups of (active) parmgroups from the tags
        of the various (active) parmgroups. These may be used to select groups,
        e.g. in .solvable()."""
        gg = dict()
        gg.setdefault('*',[])
        keys = self._parmgroups.keys()
        for key in keys:
            pg = self._parmgroups[key]
            if pg.active():                # active groups only!
                tags = pg._tags
                for tag in tags:
                    gg.setdefault(tag,[])
                    if not key in gg[tag]:
                        gg[tag].append(key)
                if not key in gg['*']:     # all active groups (*)
                    gg['*'].append(key)
        self._parmgogs = gg
        return self._parmgogs



    #===============================================================
    # Methods using NodeList(s):
    #===============================================================

    def compare (self, parmgroup, other, show=False):
        """Compare the nodes of a parmgroup with the corresponding ones
        of the given (and assumedly commensurate) parmgroup (other).
        The results are visualized in various helpful ways.
        The rootnode of the comparison subtree is returned.
        """
        self.has_group (parmgroup, severe=True)
        self.has_group (other, severe=True)
        pg1 = self._parmgroups[parmgroup]
        pg2 = self._parmgroups[other]
        return pg1.compare(pg2, show=show)


    #---------------------------------------------------------------

    def bundle (self, parmgroup='*', combine='Composer',
                  bookpage=True, folder=None, show=False):
        """Bundle the nodes in the specified parmgroup(s) by applying the
        specified combine-operation (default='Add') to them. Return the
        root node of the resulting subtree. Make bookpages for each parmgroup.
        """
        pgs = self.find_parmgroups (parmgroup, severe=True)
        if folder==None:
            if len(pgs)>1: folder = 'bundle_'+self.name
        bb = []
        for key in pgs:
            pg = self._parmgroups[key]
            bb.append(pg.bundle(bookpage=bookpage, folder=folder))
        return self._bundle_of_bundles (bb, name='bundle',
                                          qual=parmgroup,
                                          accu=True, show=show)

    #---------------------------------------------------------------

    def plot_rvsi (self, parmgroup='*',
                     bookpage=True, folder=None, show=False):
        """Make separate rvsi plots of the specified parmgroup(s). Return the
        root node of the resulting subtree. Make bookpages for each parmgroup.
        """
        pgs = self.find_parmgroups (parmgroup, severe=True)
        if bookpage:
            if not isinstance(bookpage, str):
                bookpage = 'plot_rvsi_'+self.name
        bb = []
        for key in pgs:
            pg = self._parmgroups[key]
            bb.append(pg.plot_rvsi(bookpage=bookpage, folder=folder))
        return self._bundle_of_bundles (bb, name='plot_rvsi',
                                          qual=parmgroup,
                                          accu=True, show=show)
    
    #---------------------------------------------------------------

    def plot_timetracks (self, parmgroup='*', 
                           bookpage=True, folder=None, show=False):
        """Visualize the nodes in the specified parmgroup(s) in a separate
        'inspector' (time-tracks) per parmgroup. Return the root node of
        the resulting subtree. Make bookpages for each parmgroup.
        """
        pgs = self.find_parmgroups (parmgroup, severe=True)
        if bookpage:
            if not isinstance(bookpage, str):
                bookpage = 'plot_timetracks_'+self.name
        bb = []
        for key in pgs:
            pg = self._parmgroups[key]
            bb.append(pg.plot_timetracks (bookpage=bookpage, folder=folder))
        return self._bundle_of_bundles (bb, name='plot_timetracks',
                                          qual=parmgroup,
                                          accu=True, show=show)


    #---------------------------------------------------------------

    def plot_spectra (self, parmgroup='*', 
                           bookpage=True, folder=None, show=False):
        """Visualize the nodes in the specified parmgroup(s) in a separate
        'inspector' (time-tracks) per parmgroup. Return the root node of
        the resulting subtree. Make bookpages for each parmgroup.
        """
        pgs = self.find_parmgroups (parmgroup, severe=True)
        if bookpage:
            if not isinstance(bookpage, str):
                bookpage = 'plot_spectra_'+self.name
        bb = []
        for key in pgs:
            pg = self._parmgroups[key]
            bb.append(pg.plot_spectra (bookpage=bookpage, folder=folder))
        return self._bundle_of_bundles (bb, name='plot_spectra',
                                          qual=parmgroup,
                                          accu=True, show=show)


    
    #---------------------------------------------------------------
    # Helper function:
    #---------------------------------------------------------------

    def _bundle_of_bundles (self, bb, name=None, qual=None,
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
        if accu: self.accumulist(qnode)
        if show: display.subtree(qnode, show_initrec=False)
        return qnode


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





    #=====================================================================================
    #=====================================================================================
    # Accumulist service:
    # NB: This service does not really belong here, but is convenient.
    #=====================================================================================

    def accumulist (self, item=None, key=None, flat=False, clear=False):
        """Interact with the internal service for accumulating named (key) lists of
        items (nodes, usually), for later retrieval downstream.
        If flat=True, flatten make a flat list by extending the list with a new item
        rather than appending it.
        An extra list with key=* contains all items of all lists"""

        print '\n** accumulist(',str(item),')\n'
        
        if key==None: key = '_default_'
        if not isinstance(key, str):
            print '\n** .accumulist(): key is wrong type:',type(key),'\n'
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

    def bundle_accumulist(self, quals=None):
        """Bundle the nodes in self._accumulist with a reqseq"""
        cc = self.accumulist(clear=False)
        n = len(cc)
        if n==0: return None
        if n==1: return cc[0]
        # self.history('.bundle_accumulist()')
        qnode = self.ns['bundle_accumulist']
        if quals: qnode = qnode(quals)
        if not qnode.initialized():
            qnode << Meq.ReqSeq(children=cc, result_index=n-1)
        return qnode

    #---------------------------------------------------------------------------

    def merge_accumulist (self, other):
        """Merge the accumulist of another Matrix22 object with its own."""
        # self.history('.merge_accumulist()')
        olist = other._accumulist
        for key in olist.keys():
            if not key=='*':
                self.accumulist(olist[key], key=key, flat=True)
        return True





#=============================================================================
#=============================================================================
#=============================================================================
# Test routine (with meqbrowser):
#=============================================================================

PGM = None
if 0:
    PGM = ParmGroupManager(name='GJones',
                           solvermenu='compile.something.solver',
                           namespace='PGMN')
    PGM.add_ParmGroup('Gphase', mode='amphas', time_tiling=3, freq_tiling=6, sum=0.1)
    PGM.add_ParmGroup('Ggain', mode='amphas', default=1.0, freq_deg=2, product=0.9)
    PGM.add_ParmGroup('Greal', mode=['realimag','special'], default=1.0)
    PGM.add_ParmGroup('Gimag', mode='realimag')
    PGM.define_mode_option()
    PGM.make_TDLCompileOptionMenu()
    PGM.display('outside')



def _define_forest(ns):


    global PGM
    if not PGM:
        PGM = ParmGroupManager(name='GJones',
                               namespace='PGMN')
        PGM.add_ParmGroup('Gphase', time_tiling=3)
        PGM.add_ParmGroup('Ggain', default=1.0, freq_deg=2)
        PGM.make_TDLCompileOptionMenu()
        PGM.display('initial')
        
    cc = []
    PGM.nodescope(ns)

    if 1:
        PGM['Gphase'].create_member(1)
        PGM['Gphase'].create_member(2.1, value=(ns << -89))
        PGM['Gphase'].create_member(2, value=34)
        PGM['Gphase'].create_member(3, time_tiling=5)
        PGM['Gphase'].create_member(7, freq_deg=2)

    if 1:
        PGM['Ggain'].create_member(7, freq_deg=6)
        PGM['Ggain'].create_member(4, time_deg=3)

    if 0:
        cc.append(PGM.bundle(show=True))
        cc.append(PGM.plot_timetracks())
        cc.append(PGM.plot_spectra())

    if 0:
        nn = PGM.solvable(groups='GJones', return_NodeList=True)
        nn.display('solvable')
        nn.bookpage(select=4)
        

    PGM.display('final', full=False)
    if 0:
        PGM.pg_display(full=True)

    if len(cc)==0: cc.append(ns.dummy<<1.1)
    ns.result << Meq.Composer(children=cc)
    # PGM.make_TDLRuntimeOptionMenu()
    return True



#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
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
    from Timba.Contrib.JEN.Expression import Expression
    ns = NodeScope()

    if 1:
        PGM = ParmGroupManager(ns, 'GJones')
        PGM.add_ParmGroup('Gphase', mode='amphas')
        PGM.add_ParmGroup('Ggain', mode='amphas')
        PGM.add_ParmGroup('Greal', mode='realimag')
        PGM.add_ParmGroup('Gimag', mode='realimag')
        PGM.display('initial')

    if 1:
        for mode in PGM.mode_order():
            PGM.select_mode(mode, trace=True)
        PGM.select_mode(trace=True)

    if 0:
        print PGM['Gphase'].oneliner()
        print PGM['Ggain'].oneliner()

    if 0:
        PGM['Gphase'].create_member(1)
        PGM['Gphase'].create_member(2.1, value=(ns << -89))
        PGM['Gphase'].create_member(2, value=34)
        PGM['Gphase'].create_member(3, time_tiling=5)
        PGM['Gphase'].create_member(7, freq_deg=2)

    if 0:
        PGM['Ggain'].create_member(7, freq_deg=6)
        PGM['Ggain'].create_member(4, time_deg=3)


    if 0:
        PGM.bundle(show=True)
    if 0:
        PGM.plot_rvsi(show=True)
    if 0:
        PGM.plot_spectra(show=True)
    if 0:
        PGM.plot_timetracks(show=True)

    if 0:
        PGM.display('final', full=True, om=True)


    #------------------------------------------------------------------

    if 0:
        print dir(PGM)
        print getattr(PGM,'_parmgroup',None)

    if 0:
        print 'ns.Search(tags=Gphase):',ns.Search(tags='Gphase')
        print 'PGM.ns.Search(tags=Gphase):',PGM.ns.Search(tags='Gphase')

    if 0:
        PGM.solvable()
        PGM.solvable(groups='Gphase', trace=True)
        PGM.solvable(groups=['Ggain'], trace=True)
        PGM.solvable(groups=['GJones'], trace=True)
        PGM.solvable(groups=['Gphase','Ggain'], trace=True)
        PGM.solvable(groups=PGM.groups(), trace=True)
        PGM.solvable(groups=PGM.gogs(), trace=True)
        # PGM.solvable(groups=['Gphase','xxx'], trace=True)

    if 0:
        PGM.solvable(tags='Gphase', trace=True)
        PGM.solvable(tags=['Gphase','Ggain'], trace=True)
        PGM.solvable(tags=['Gphase','GJones'], trace=True)
        PGM.solvable(tags=['Gphase','Dgain'], trace=True)

    if 0:
        solvable = True
        PGM.find_nodes(groups='GJones', solvable=solvable, trace=True)
        PGM.find_nodes(groups=PGM.gogs(), solvable=solvable, trace=True)

    if 0:
        pp2 = ParmGroupManager(ns, 'DJones')
        pp2.define_parmgroup('Ddell')
        pp2.define_parmgroup('Ddang')
        pp2.group_create_member('Ddang', 1)
        pp2.group_create_member('Ddell', 7)
        pp2.display(full=True)
        if 1:
            PGM.merge(pp2, trace=True)
            PGM.find_nodes(groups=['GJones','DJones'], solvable=True, trace=True)
            PGM.find_nodes(groups=['GJones','DJones'], solvable=False, trace=True)
        PGM.display('after merge', full=True)

    if 0:
        e0 = Expression.Expression(ns, 'e0', '{a}+{b}*[t]-{e}**{f}+{100~10}', simul=False)
        e0.display()
        if 0:
            pp3 = ParmGroupManager(ns, 'e0', merge=e0)
            pp3.display('after merge', full=True)
        if 1:
            PGM.merge(e0, trace=True)
            PGM.display('after merge', full=True)
            PGM.pg_display(full=True)

    if 0:
        PGM.accumulist('aa')
        PGM.accumulist('2')
        PGM.accumulist(range(3), flat=True)
        PGM.accumulist('bb', key='extra')
        PGM.display(full=True)
        print '1st time:',PGM.accumulist()
        print '1st time*:',PGM.accumulist(key='*')
        print '2nd time:',PGM.accumulist(clear=True)
        print '3rd time:',PGM.accumulist()


#===============================================================

