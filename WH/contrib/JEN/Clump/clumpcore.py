"""
clumpcore.py: Contains the generic state of Clump classes.
"""

# file: ../JEN/Clump/clumpcore.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 21 nov 2008: creation (split from Clump.py)
#
# Description:
#
# Remarks:
#
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

from Timba.Contrib.JEN.control import TDLOptionManager as TOM

from Timba.Contrib.JEN.Easy import EasyNode as EN
from Timba.Contrib.JEN.Easy import EasyFormat as EF

import Meow.Bookmarks
from Timba.Contrib.JEN.util import JEN_bookmarks

import math                 # support math.cos() etc
import numpy                # support numpy.prod() etc
import random               # e.g. random.gauss()
import copy

clump_counter = -1          # used in clumpcore.__init__()

#******************************************************************************** 

class clumpcore (object):
   """
   Helper class. Every Clump object has one (self.core)
   """

   def __init__(self, clump=None, typename='<typename>', **kwargs):
      """
      """
      # Keep the inputs for later reference:
      self._input_clump = clump
      self._typename = typename
      self._input_kwargs = kwargs

      # These need a little more thought:
      kwargs.setdefault('select', None)                 # <------- !!?
      trace = kwargs.get('trace',False)                 # <------- !!?
      self._slaveof = kwargs.get('slaveof',None)        # <------- !!?

      # The Clump node names are derived from name and qualifier:
      self._name = kwargs.get('name',None)       
      self._name = kwargs.get('name', self._typename)   # better...?     
      self._qual = kwargs.get('qual',None)  
      self._kwqual = kwargs.get('kwqual',dict())

      # Organising principles:
      self._ns = kwargs.get('ns',None)
      self._TCM = kwargs.get('TCM',None)

      # A Clump objects operates in successive named/counted 'stages'.
      # This is used to generate nodenames: See self.unique_nodestub().
      # Some of this information is passed from clump to clump.
      self._stage = dict(name=None, count=-1, ops=-1, ncopy=0, isubmenu=-1) 

      # A Clump object maintains a history of itself:
      self._history = None                  # see self.history()

      # Nodes without parents (e.g. visualisation) are collected on the way:
      self._orphans = []                    # see self.rootnode()

      # Any ParmClumps are passed along (e.g. see SolverUnit.py)
      self._ParmClumps = []

      # See .on_entry(), .execute_body(), .end_of_body(), .on_exit() 
      self._ctrl = None

      # This is used to override option values by means of arguments:
      self._override = dict()

      # A Clump object has a "rider", i.e. a dict that contains user-defined
      # information, and is passed on from Clump to Clump.
      # All interactions with the rider should use the function self.rider()
      self._rider = dict()


      #......................................................................
      # Transfer Clump definition information from the input Clump (if supplied).
      # This includes self._datadesc etc 
      # Then supply local defaults for some attributes that have not been
      # defined yet (i.e. in the case that there is no input Clump):
      #......................................................................

      self.transfer_clump_definition(trace=False)

      if not isinstance(self._name,str):    # Generate an automatic object name, if necessary      
         self._name = self._typename        # e.g. 'Clump'     
         global clump_counter
         clump_counter += 1
         self._name += str(clump_counter)

      if not self._TCM:               
         ident = self._typename+'_'+self._name
         self._TCM = TOM.TDLOptionManager(ident)

      if not self._ns:
         self._ns = NodeScope()      

      # Initialise self._stubtree (see .unique_nodestub()):
      self._stubtree = None

      #......................................................................
      # Fill self._nodes (the Clump tree nodes) etc.
      #......................................................................

      self._nodes = []
      self._composed = False
      self._nodequals = []
      if self._input_clump:
         if kwargs.get('transfer_clump_nodes',True):
            self.transfer_clump_nodes()
         else:
            self._nodequals = self._datadesc['treequals']
            self._composed = False

      # The data description record controls the behaviour of Clump-functions
      # that perform 'generic' operations (like add_noise()).
      # It is passed from Clump to Clump, and modified when appropriate.
      # If an input clump is specified (see above) its datadesc will be copied.
      # If not, the datadesc (e.g. see LeafClump or ListClump in this module),
      # the datadesc will usually have been created in the derived class.
      # If there still is no datadesc at this point, create a default one:
            
      if not getattr(self,'_datadesc',None):     # does not exist yet
         self._datadesc = dict()
         self.datadesc(complex=kwargs.get('complex',False),
                       treequals=kwargs.get('treequals',range(3)), 
                       plotcolor=kwargs.get('plotcolor','red'),
                       plotsymbol=kwargs.get('plotsymbol','cross'),
                       plotsize=kwargs.get('plotsize',1),
                       dims=kwargs.get('dims',1))

      self._object_is_selected = False           # see .execute_body()

      # Finished:
      return None

   #--------------------------------------------------------------------------
   #--------------------------------------------------------------------------

   def datadesc (self, **kwargs):
      """Return self._datadesc, after calculating all the derived values,
      and checking for consistency. 
      """
      tqs = kwargs.get('treequals',None) 
      is_complex = kwargs.get('complex',None) 
      dims = kwargs.get('dims',None) 
      plotcolor = kwargs.get('plotcolor',None) 
      plotsymbol = kwargs.get('plotsymbol',None) 
      plotsize = kwargs.get('plotsize',None) 

      if not getattr(self,'_datadesc',None):       # does not exist yet
         self._datadesc = dict()
      dd = self._datadesc                     # convenience

      #..........................................................
      if isinstance(is_complex,bool):              # data type
         dd['complex'] = is_complex            

      #..........................................................
      if dims:                                     # tensor dimensions
         if isinstance(dims,int):                 
            dd['dims'] = [dims]
         elif isinstance(dims,(list,tuple)):   
            dd['dims'] = list(dims)
         else:
            self.ERROR('** dims should be integer or list')

      #..........................................................
      if not tqs==None:                            # Clump tree qualifiers
         if isinstance(tqs,str):                   # string 
            dd['treequals'] = list(tqs)            # -> list of chars (..?)
         elif isinstance(tqs,tuple):               # tuple -> list
            dd['treequals'] = list(tqs)
         elif not isinstance(tqs,list):            # assume str or numeric?
            self._tqs = [tqs]                      # make a list of one
         else:                                     # tqs is a list
            dd['treequals'] = tqs                  # just copy the list
         # Make a list of (string) tree labels from treequals:
         # (e.g. inspector-labels give require this).
         dd['treelabels'] = []
         for i,qual in enumerate(dd['treequals']):
            dd['treelabels'].append(str(qual))

         # The nodes are generated using self._nodequals
         self._nodequals = dd['treequals']         # node qualifiers
         self._composed = False                    # see .compose() and .decompose()
         self._nodes = len(self._nodequals)*[None] # make a list of the correct length

      #..........................................................
      # Plotting information:
      if plotcolor:
         dd['plotcolor'] = plotcolor
      if plotsymbol:
         dd['plotsymbol'] = plotsymbol
      if plotsize:
         dd['plotsize'] = max(1,plotsize)

      #..........................................................
      # Derived attributes:
      dims = dd['dims']
      dd['nelem'] = numpy.prod(dims)               # nr of tensor elements
      dd['elems'] = range(dd['nelem'])
      for i,elem in enumerate(dd['elems']):
         dd['elems'][i] = str(elem)

      # Some special cases:
      if len(dims)==2:                             # e.g. [2,2]
         dd['elems'] = []
         for i in range(dims[0]):
            for j in range(dims[1]):
               dd['elems'].append(str(i)+str(j))

      #..........................................................
      # Check the internal consistency:

      if not getattr(self,'_composed',None):
          self._composed = False

      tqs = dd['treequals']
      if not getattr(self,'_nodequals',None):
          self._nodequals = tqs
          self._composed = False
      elif not isinstance(self._nodequals,list):
          self._nodequals = tqs
          self._composed = False
      elif not len(self._nodequals)==len(tqs):
          self._nodequals = tqs
          self._composed = False

      nqs = self._nodequals
      if not getattr(self,'_nodes',None):
         self._nodes = len(nqs)*[None]
      elif not isinstance(self._nodes,list):
         self._nodes = len(nqs)*[None]
      elif not len(self._nodes)==len(nqs):
         self._nodes = len(nqs)*[None]


      #..........................................................
      # Always return a copy (!) of the self-consistent datadesc:
      return self._datadesc


   #==========================================================================
   # Functions that deal with the input Clump (if any)
   #==========================================================================

   def transfer_clump_definition(self, trace=False):
      """Transfer the clump definition information from the given Clump.
      Most attributes are transferred ONLY if not yet defined
      Some attributes (like self._datadesc) are transferred always(!)
      """
      clump = self._input_clump              # convenience

      # trace = True
      if trace:
         print '\n** transfer_clump_definition(): clump=',type(clump),clump
         
      if not clump==None:
         # Most attributes are transferred ONLY if not yet defined
         # (e.g. by means of the input **kwargs (see .__init__())
         if not isinstance(self._name,str):
            self._name = '('+clump.core._name+')'
         if self._qual==None:
            self._qual = clump.core._qual
         if self._kwqual==None:
            self._kwqual = clump.core._kwqual
         if self._ns==None:
            self._ns = clump.core._ns
         if self._TCM==None:
            self._TCM = clump.core._TCM

         # Some attributes are transferred always(!):
         self._datadesc = clump.datadesc().copy()               # .... copy()!
         self.datadesc()
         self._stage['count'] = 1+clump.core._stage['count']         # <--------!!
         self._stage['ops'] = -1                                # reset
         self._stage['name'] = clump.core._stage['name']             # <--------!!
         clump.core._stage['ncopy'] += 1
         self._stage['ncopy'] = clump.core._stage['ncopy']           # <--------!!
         self._rider.update(clump.core._rider)                       # .update()?
         # self._rider.update(clump.rider())                      # .update()?
      return True

   #--------------------------------------------------------------------------

   def transfer_clump_nodes(self):
      """Transfer the clump nodes (etc) from the given input Clump.
      Called from self.__init__() only.
      """
      clump = self._input_clump                 # convenience
      if not clump:
         self.ERROR('** Clump: An input Clump should have been provided!')

      elif getattr(clump,'_nodes',None):
         # Make sure that self._nodes is a COPY of clump._nodes
         # (so clump._nodes is not modified when self._nodes is).
         self._nodes = []
         for i,node in enumerate(clump._nodes):
            self._nodes.append(node)
         self._composed = clump._composed
         self._nodequals = clump._nodequals

         # Connect orphans, stubtrees, history, ParmClumps etc
         self.graft_to_stubtree(clump._stubtree)
         self._orphans = clump._orphans
         self._ParmClumps = clump._ParmClumps
         self.copy_history(clump, clear=True)
      return True


   #========================================================================

   def graft_to_stubtree(self, node):
      """Helper function to graft the given node (usually the rootnode
      of the stubtree of another clump) to its own self._stubtree.
      """
      stub = self.unique_nodestub()
      self._stubtree = stub('graft_to_stubtree') << Meq.Add(self._stubtree,node)
      return True
      

   #=========================================================================

   def unique_nodestub (self, *qual, **kwqual):
      """
      Convenience function to generate a (unique) nodestub for tree nodes.
      The stub is then initialized (which helps the uniqueness determination!)
      and attached to the internal subtree of stub-nodes, which would otherwise
      be orphaned. They are used to carry quickref-help information, which
      can be used in the various bookmark pages.
      """
      trace = False
      # trace = True

      # Make a list of qualifiers:
      qual = list(qual)
      self._stage['ops'] += 1

      if False:
         # NB: This pollutes Parm names etc...
         at = '@'+str(self._stage['count'])
         at += '-'+str(self._stage['ops'])
         qual.insert(0, at)

      if not self._qual==None:
         if isinstance(self._qual,list):
            qual.extend(self._qual)
         else:
            qual.append(self._qual)

      # Deal with the node name:
      name = self._name                            # default name
      if kwqual.has_key('name'):                   # specified explicitly
         if isinstance(kwqual['name'],str):
            name += ':'+kwqual['name']             # use if string
         kwqual.__delitem__('name')                # delete from kwqual

      # Make the unique nodestub:
      stub = EN.unique_stub(self._ns, name, *qual, **kwqual)

      # Initialize the stub (uniqueness criterion!):
      if not self._stubtree:                       # the first one
         node = stub << Meq.Constant(-0.1223456789)
      else:                                        # subsequent ones
         node = stub << Meq.Identity(self._stubtree)
         
      # Attach the help (view with QuickRef viewer)
      # format, and attach some extra info....?
         ## help = rider.format_html(path=rider.path())
      # node.initrec().quickref_help = help

      # Replace the rootnode of the stub-tree:
      self._stubtree = node

      if trace:
         print '\n** .unique_nodestub(',qual,') ->',str(stub)
      return stub


   #=========================================================================
   # Some general helper functions
   #=========================================================================

   def size(self):
      """Return the number of trees in the Clump (even if in a tensor)
      """
      return len(self._datadesc['treequals'])

   #--------------------------------------------------------------------------

   def __len__(self):
      """Get the nr of nodes. Syntax: len = len(clump)
      """
      return len(self._nodes)

   #--------------------------------------------------------------------------

   def __getitem__(self, index):
      """Get the specified (index) node. Syntax: node = clump[i]
      """
      return self._nodes[index]

   #--------------------------------------------------------------------------

   def __setitem__(self, index, node):
      """Replace the specified (index) node. Syntax: clump[i] = node
      """
      self._nodes[index] = node
      return None

   #--------------------------------------------------------------------------

   def __str__(self):
      """Print-conversion. Syntax: print str(clump) prints clump.oneliner().
      """
      return self.oneliner()

   #--------------------------------------------------------------------------

   # See Learning Python pp 327-328:
   # def __add__(self):     Operator '+'  X+Y, X+=Y
   # def __or__(self):     Operator '|'  X|Y, X|=Y       (?) (bitwise OR)
   # def __call__(self):     X()
   # def __len__(self):     len(X)
   # def __cmp__(self):     X==Y, X<Y
   # def __lt__(self):     X<Y
   # def __eq__(self):     X==Y
   # def __radd__(self):    right-side operator '+'  Noninstance + X
   # def __iadd__(self):     X+=Y
   # def __iter__(self):     for loops, in tests, others
   
   


   #==========================================================================
   # Various text display functions:
   #==========================================================================

   def oneliner (self):
      ss = self._typename+': '
      ss += ' '+str(self._name)
      if not self._qual==None:
         ss += ' qual='+str(self._qual)
      ss += '  size='+str(self.size())
      ss += '  len()='+str(len(self))
      if self._composed:
         ss += '(composed)'
      if self._slaveof:
         ss += '  slaved'
      return ss

   #--------------------------------------------------------------------------

   def show (self, full=True, prefix='\n   ', doprint=True):
      """
      Format a summary of the contents of the object.
      If doprint=True, print it also.  
      """
      if not prefix[0]=='\n':
          prefix = '\n'+prefix
      ss = prefix+' Generic (all Clump classes):'
      
      #.....................................................
      if isinstance(self._input_clump, list):
         ss += prefix+' > self.core._input_clump: list of '+str(len(self._input_clump))+' nodes'
      elif self._input_clump:
         ss += prefix+' > self.core._input_clump: '+str(self._input_clump.oneliner())
      else:
         ss += prefix+' > self.core._input_clump = '+str(self._input_clump)

      ss += prefix+' > self.core._input_kwargs = '+str(self._input_kwargs)
      ss += prefix+' > self.core._override = '+str(self._override)

      #.....................................................

      ss += prefix+' * self.core._object_is_selected: '+str(self._object_is_selected)    
      ss += prefix+' * self.core._name = '+str(self._name)
      ss += prefix+' * self.core._qual = '+str(self._qual)
      ss += prefix+' * self.core._kwqual = '+str(self._kwqual)

      ss += prefix+' * self.core._slaveof: '+str(self._slaveof)

      ss += prefix+' * self.core._stage = '+str(self._stage)
      
      ss += prefix+' * self.core._datadesc:'
      dd = self._datadesc
      for key in dd.keys():
         ss += prefix+'   - '+str(key)+' = '+str(dd[key])

      ss += prefix+' * self.core._composed: '+str(self._composed)
      ss += prefix+' * self.core._nodequals: '+str(self._nodequals)

      #.....................................................

      ss += prefix+' * self.core._nodes '
      ss += ' (len='+str(len(self))
      ss += ', .size()='+str(self.size())+'):'
      n = len(self._nodes)
      if full:
         nmax = 2
         for i in range(min(nmax,n)):
            ss += prefix+'   - '+str(self[i])
         if n>nmax:
            if n>nmax+1:
               ss += prefix+'       ...'
            ss += prefix+'   - '+str(self[-1])
      else:
         ss += prefix+'   - node[0] = '+str(self[0])
         ss += prefix+'   - node[-1]= '+str(self[-1])
                                       
      #.....................................................
      ss += prefix+' * self.core._ParmClumps (n='+str(len(self._ParmClumps))+'):'
      for i,pc in enumerate(self._ParmClumps):
         ss += prefix+'   - '+str(pc.oneliner())

      #.....................................................
      ss += prefix+' * (rootnode of) self._stubtree: '+str(self._stubtree)
      ss += prefix+' * self.core._orphans (n='+str(len(self._orphans))+'):'
      for i,node in enumerate(self._orphans):
         ss += prefix+'   - '+str(node)
      #.....................................................

      ss += prefix+' * self.core._ns: '+str(self._ns)
      if self._TCM:
         ss += prefix+' * self.core._TCM: '+str(self._TCM.oneliner())
      else:
         ss += prefix+' * self.core._TCM = '+str(self._TCM)
      #.....................................................

      ss += prefix+' * self.core._ctrl: '+str(self._ctrl)
      ss += self.history(format=True, prefix='   | ')

      #.....................................................
      # ss += prefix+'**'
      if doprint:
         print ss
      return ss


   #=========================================================================
   # Object history:
   #=========================================================================

   def copy_history(self, clump, clear=False, trace=False):
      """Copy the history of the given clump in an organised way:
      """
      if clear:
         self.history(clear=clear)
      for s in clump.history():
         ss = s.split('}')
         s1 = ss[-1]
         self.history('|....'+s1)
      return True

   #--------------------------------------------------------------------------

   def history (self, append=None, **kwargs):
      """Interact with the object history (a list of strings).
      """
      show_node = kwargs.get('show_node', False)
      prefix = kwargs.get('prefix', '')
      format = kwargs.get('format', False)
      clear = kwargs.get('clear', False)
      show = kwargs.get('show', False)
      trace = kwargs.get('trace', False)

      # trace = True
      level = self._TCM.current_menu_level()

      clear |= (self._history==None)             # the first time
      if clear:
         self._history = []
         self._history.append('')
         s = '** Object history of: '+self.oneliner()
         self._history.append(s)
         if trace:
            print '   >> .history(clear)'

      # Append a new list item to self._history()
      if isinstance(append,str):
         s = ' -- '
         s += self._name+':    '
         s += (level*'-')
         s += '{'+str(level)+'} '
         s += str(append)
         self._history.append(s)
         if trace:
            print '   >> .history(append): ',self._history[-1]
      elif show_node:
         # self._history.append(' --   (append=None) ')
         # self.history('(append=None)')
         self.history('last Clump tree node:', level=level)

      # Append the current node to the last line/item: 
      if show_node and len(self)>0:
         ilast = len(self)-1
         s = '   -> '+str(self[ilast])
         self._history[-1] += s
         if trace:
            print '   >> .history(show_node): ',self._history[-1]

      # Format the history into a multi-line string (ss):
      if show or format:
         ss = ''
         for line in self._history:
            ss += '\n'+prefix+''+prefix+line
         ss += '\n'+prefix+''+prefix+'** Current oneliner(): '+str(self.oneliner())
         ss += '\n'+prefix+'   |'
         if show:
            print ss
         if format:
            return ss

      # Always return the currently accumulated history (except when format=True)
      return self._history

   #=========================================================================
   #=========================================================================

   def rider (self, key=None, **kwargs):
      """The rider contains arbitrary user-defined information.
      """
      trace = kwargs.get('trace',False)
      severe = kwargs.get('severe',True)
      rr = self._rider                # convenience
      if isinstance(key,str):
         if kwargs.has_key('new'):
            self._rider[key] = kwargs['new']
         elif not rr.has_key(key):
            if severe:
               self.ERROR('** rider does not have key: '+str(key))
            else:
               return None                 # .....?
         return self._rider[key]
      return self._rider

   #=========================================================================
   #=========================================================================

   def ERROR (self, s):
      """Raise a ValueError in an organised way, i.e. while giving
      information that may help in its solution. The program is stopped.
      """
      s1 = '** ERROR ** '+str(s)
      print '\n',s1,'\n'
      self.history(s1, trace=True)
      self.show(s1)
      raise ValueError,s1

   #--------------------------------------------------------------------------

   def WARNING (self, s):
      """Issue a warning in an organised way: Print it conspiciously and
      put it in the object history.
      """
      s1 = '** WARNING ** '+str(s)
      self.history(s1, trace=True)
      print '\n            ',s1,'\n'
      return s1

   #--------------------------------------------------------------------------

   def REMARK (self, s):
      """Make a remark in an organised way:
      Print it, and put it in the object history.
      """
      s1 = '-- REMARK: '+str(s)
      self.history(s1, trace=True)
      return s1


   #=========================================================================
   #=========================================================================

   def indices(self, subset='*', severe=True, nodelist=None, trace=False):
      """Return a list of valid tree (node) indices, according to subset[='*'].
      NB: In the 'composed' state, the result will be [0].
      If subset is an integer, return that many (regularly spaced) indices.
      If subset is a list, check their validity.
      If subset is a string (e.g. '*'), decode it.
      """
      trace = True
      s = '.indices('+str(subset)+'):'

      # Turn subset into a list:
      if isinstance(subset,str):
         if subset=='*':
            ii = range(len(self))
         else:
            self.ERROR(s)
      elif isinstance(subset,int):
         ii = range(min(subset,len(self)))  
      elif not isinstance(subset,(list,tuple)):
         self.ERROR(s)
      else:
         ii = list(subset)

      # Check the list elements:
      imax = len(self)
      for i in ii:
         if not isinstance(i,int):
            self.ERROR(s)
         elif i<0 or i>imax:
            self.ERROR(s)

      # Finished:
      if trace:
         print s,'->',ii
      return ii


   #=========================================================================
   #=========================================================================

   def rootnode (self, **kwargs):
      """Return a single node with the specified name [='rootnode'] which has all
      the internal nodes (self._nodes, self._stubtree and self._orphans)
      as its children. The internal state of the object is not changed.
      """
      name = kwargs.get('name','rootnode')
      hist = '.rootnode('+str(name)+'): '
      nodes = []
      for node in self._nodes:              # the Clump tree nodes
         nodes.append(node)
      hist += str(len(nodes))+' tree nodes '

      stub = self._ns.rootnode
      if is_node(self._stubtree):
         node = stub('stubtree') << Meq.Identity(self._stubtree) 
         nodes.append(node)                 # include the tree of stubs
         hist += '+ stubtree root '

      if len(self._orphans)>0:
         node = stub('orphans') << Meq.Composer(*self._orphans) 
         nodes.append(node)                 # include any orphans
         hist += '+ '+str(len(self._orphans))+' orphans '

      # use MeqComposer? or MeqReqSeq? or stepchildren?
      rootnode = self._ns[name] << Meq.Composer(children=nodes)

      hist += '-> '+str(rootnode)
      self.history(hist, trace=kwargs.get('trace',False))
      return rootnode


   #=========================================================================




#********************************************************************************
#********************************************************************************
# Standalone test (without the browser):
#********************************************************************************
#********************************************************************************

if __name__ == '__main__':

   print '\n****************************************************'
   print '** Start of standalone test of: clumpcore.py:'
   print '****************************************************\n' 

   ns = NodeScope()

   if 1:
      core = clumpcore(trace=True)

   if 1:
      core.show(full=True)

   if 1:
      node = core.rootnode() 
      core.show('.rootnode()')
      print '->',str(node)

   #-------------------------------------------------------------------
   # Some lower-level tests:
   #-------------------------------------------------------------------

   if 0:
      clump.get_indices(trace=True)
      clump.get_indices('*',trace=True)
      clump.get_indices(2, trace=True)
      clump.get_indices([2],trace=True)

   if 0:
      ss = dir(core)
      print ss
      for s in ss:
         a = getattr(core,s,None)
         if not isinstance(s,str):
            print '-',s,type(a)
         elif s[0]=='_':
            if s[1]=='_':
               print '*',s
            else:
               print '-',s,type(a)
         else:
            print '-',s
               
   print '\n** End of standalone test of: clumpcore.py:\n' 


#=====================================================================================
# Things to be done:
#
#=====================================================================================





