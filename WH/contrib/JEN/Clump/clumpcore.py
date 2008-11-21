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

      # These need a little more thought:
      kwargs.setdefault('select', None)                 # <------- !!?
      trace = kwargs.get('trace',False)                 # <------- !!?

      self._slaveof = kwargs.get('slaveof',None)        # <------- !!?

      self._input_kwargs = kwargs

      # Make a short version of the actual type name (e.g. Clump)
      self._typename = typename

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

      self.transfer_clump_definition(clump, trace=False)

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
         self.datadesc(complex=False, dims=[1], treequals=range(3),
                       plotcolor='red', plotsymbol='cross', plotzize=1)

      self._object_is_selected = False           # see .execute_body()

      # Finished:
      return None

   #--------------------------------------------------------------------------
   #--------------------------------------------------------------------------

   def datadesc (self, **kwargs):
      """Return self._datadesc, after calculating all the derived values,
      and checking for consistency. 
      """
      is_complex = kwargs.get('complex',None) 
      dims = kwargs.get('dims',None) 
      color = kwargs.get('plotcolor',None) 
      symbol = kwargs.get('plotsymbol',None) 
      size = kwargs.get('plotsize',None) 
      tqs = kwargs.get('treequals',None) 

      if not getattr(self,'_datadesc',None):       # does not exist yet
         self._datadesc = dict()
      dd = self._datadesc                          # convenience

      if isinstance(is_complex,bool):              # data type
         dd['complex'] = is_complex            

      if dims:                                     # tensor dimensions
         if isinstance(dims,int):                 
            dd['dims'] = [dims]
         elif isinstance(dims,(list,tuple)):   
            dd['dims'] = list(dims)
         else:
            self.ERROR('** dims should be integer or list')

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

      # Plotting information:
      if color:
         dd['plotcolor'] = color
      if symbol:
         dd['plotsymbol'] = symbol
      if size:
         dd['plotsize'] = size

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
      # Always return a copy (!) of the self-consistent datadesc:
      return self._datadesc


   #==========================================================================
   # Functions that deal with the input Clump (if any)
   #==========================================================================

   def transfer_clump_definition(self, clump, trace=False):
      """Transfer the clump definition information from the given Clump.
      Most attributes are transferred ONLY if not yet defined
      Some attributes (like self._datadesc) are transferred always(!)
      """
      # trace = True
      if trace:
         print '\n** transfer_clump_definition(): clump=',type(clump)

      self._input_clump = clump

      if clump:
         # Most attributes are transferred ONLY if not yet defined
         # (e.g. by means of the input **kwargs (see .__init__())
         if not isinstance(self._name,str):
            self._name = '('+clump._name+')'
         if self._qual==None:
            self._qual = clump._qual
         if self._kwqual==None:
            self._kwqual = clump._kwqual
         if self._ns==None:
            self._ns = clump._ns
         if self._TCM==None:
            self._TCM = clump._TCM

         # Some attributes are transferred always(!):
         self._datadesc = clump.datadesc().copy()               # .... copy()!
         self._stage['count'] = 1+clump._stage['count']         # <--------!!
         self._stage['ops'] = -1                                # reset
         self._stage['name'] = clump._stage['name']             # <--------!!
         clump._stage['ncopy'] += 1
         self._stage['ncopy'] = clump._stage['ncopy']           # <--------!!
         self._rider.update(clump._rider)                       # .update()?
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

   #--------------------------------------------------------------------------

   def connect_grafted_clump (self, clump, trace=False):
      """Connect the loose ends (orphans, stubtree, ParmClumps) of the given
      clump, e.g. when JonesClumps are used to correct VisClumps.
      This is similar to, but slightly different from, what is done in the
      function self.transfer_clump_nodes(), which merely continues the mainstream.
      """
      self.graft_to_stubtree(clump._stubtree)
      self._orphans.extend(clump._orphans)                 # group them first?
      self._ParmClumps.extend(clump._ParmClumps)       
      self.copy_history(clump)
      self.history('.connect_grafted_clump(): '+str(clump.oneliner()))
      return True

   #-------------------------------------------------------------------------

   def graft_to_stubtree(self, node):
      """Helper function to graft the given node (usually the rootnode
      of the stubtree of another clump) to its own self._stubtree.
      """
      stub = self.unique_nodestub()
      self._stubtree = stub('graft_to_stubtree') << Meq.Add(self._stubtree,node)
      return True
      
   #--------------------------------------------------------------------------

   def connect_loose_ends (self, clump=None, full=True, trace=False):
      """Connect the loose ends (orphans, stubtree, but NO ParmClumps!) of the
      current clump to another one, e.g. the input clump (=default).
      This is the reverse of .connect_grafted_clump().
      """
      if clump==None:
         clump = self._input_clump
      clump.graft_to_stubtree(self._stubtree)
      clump._orphans.extend(self._orphans)                 # group them first?
      if full:
         clump.copy_history(self)
         self.history('.connect_loose_ends() to: '+str(clump.oneliner()))
         clump.history('.connected loose ends of: '+str(self.oneliner()))
      return True

   
   #==========================================================================
   # Fuctions that depend on whether or not the Clump has been selected:
   #==========================================================================

   def append_if_selected(self, clist=[], notsel=None, trace=False):
      """If selected, append the object to the input list (clist).
      Otherwise, append it to the 'not-selected' (notsel) list, if supplied.
      Syntax:  clist = Clump(cp).append_if_selected(clist=[], notsel=[])
      """
      selected = self._object_is_selected
      if not isinstance(clist,list):
         clist = []
      s = '\n ** .append_if_selected('+str(len(clist))+') (selected='+str(selected)+')'
      if selected:
         clist.append(self)
         if trace:
            s += ' append: '+self.oneliner()
            self.history(s)
      else:
         if isinstance(notsel,list):
            notsel.append(self)
         if trace:
            s += ' not appended'
            self.history(s)
      # Always return the list:
      return clist

   #--------------------------------------------------------------------------

   def daisy_chain(self, trace=False):
      """Return the object itself, or its self._input_clump.
      The latter if it has a menu, but is NOT selected by the user.
      This is useful for making daisy-chains of Clump objects, where
      the user determines whether a particular Clump is included.
      Syntax:  cp = Clump(cp).daisy_chain()
      """
      selected = self._object_is_selected
      if trace:
         print '\n ** .daisy_chain(selected=',selected,'): ',self.oneliner()
         print '     self._input_clump =',self._input_clump
      if self._input_clump and (not selected):
         if trace:
            print '     -> input clump: ',self._input_clump.oneliner()
         return self._input_clump
      if trace:
         print '     -> itself'
      return self


   #=========================================================================
   # Functions for comparison with another Clump object
   #=========================================================================

   def commensurate(self, other, severe=False, trace=False):
      """Return True if the given (other) Clump is commensurate,
      i.e. it has the same self._nodequals (NOT self._datadesc['treequals']!)
      """
      cms = True
      if not self.size()==other.size():
         cms = False
      else:
         snq = self._nodequals
         onq = other._nodequals
         for i,qual in enumerate(snq):
            if not qual==onq[i]:
               cms = False
               break
      if not cms:
         s = '\n** '+self.oneliner()+'   ** NOT COMMENSURATE ** with:'
         s += '\n   '+other.oneliner()+'\n'
         if severe:
            self.ERROR(s)
         if trace:
            print s
      return cms

   #=========================================================================
   # Some general helper functions
   #=========================================================================

   def indices(self):
      """Return the list of indices [0,1,2,...] of the actual tree nodes.
      If composed, this will be [0] (referring to a single tensor node).
      """
      return range(len(self))

   #--------------------------------------------------------------------------

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
      if self._slaveof:
         ss += '  slaved'
      if self._composed:
         ss += '  (composed)'
      return ss

   #--------------------------------------------------------------------------

   def show (self, full=True, prefix='\n   ', doprint=True):
      """
      Format a summary of the contents of the object.
      If doprint=True, print it also.  
      """
      ss = ''
      if not prefix[0]=='\n':
          prefix = '\n'+prefix
      
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

      ss += prefix+' * Generic (baseclass Clump):'
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
      ss += prefix+'**\n'
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
   # Interaction with the (user-defined) rider:
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
   # Standard ontrol functions for use in Clump (stage) methods.
   #=========================================================================

   def on_entry (self, func=None, prompt=None, help=None, **kwargs):
      """To be called at the start of a Clump stage-method,
      Its (mandatory!) counterpart is .on_exit()
      Syntax: ctrl = self.on_entry(func, prompt, help, **kwargs)
      """
      if func==None:
         func = self.start_of_body                   # for testing only

      trace = kwargs.get('trace',False)
      hide = kwargs.get('hide',False)
      makemenu = kwargs.get('makemenu',True)
      select = kwargs.get('select',True)
      fixture = kwargs.get('fixture',False)
      ctrl = dict(funcname=str(func.func_name),
                  submenu=None,
                  trace=trace)
      fname = ctrl['funcname']                       # convenience

      # The kwargs information is used for option overrides in
      # the functions .add_option() and .execute_body()
      self._kwargs = kwargs                          # temporary
      self._override_keys = []
      self._override = dict()

      # Make the menu for the calling function:
      # NB: if any options are defined in this module, always makemenu=True,
      # otherwise there is a high probablility of option name clashes!
      if makemenu:
         # Make a unique submenu name:
         self._stage['isubmenu'] += 1                # increment
         self._stage['count'] += 1                   # increment
         self._stage['ops'] = -1                     # reset
         name = fname
         # if fname=='intexec':                        # special case
         #    name += '_'+str(self._typename)          # 'initexec' is very common 
         name += '_'+str(self._stage['isubmenu'])
         name += str(self._stage['count'])
         name += str(self._stage['ops'])
         name += str(self._stage['ncopy'])

         if not isinstance(prompt,str):
            prompt = fname+'()'
            if fname=='initexec':                    # special case
               prompt = self._name+':'
         if not isinstance(help,str):
            help = fname+'()'
            if fname=='intexec':                     # special case
               help = 'in/exclude: '+self.oneliner()
         ctrl['submenu'] = self._TCM.start_of_submenu(name,
                                                      prompt=prompt,
                                                      help=help,
                                                      default=select,
                                                      hide=hide,
                                                      slaveof=self._slaveof,
                                                      fixture=fixture,
                                                      qual=self._qual)

      # The ctrl record used by other control functions downstream.
      # The opening ones use self._ctrl, but the closing ones have to use
      # the ctrl argument (since self._ctrl may be overwritten by other
      # functions that are called in the function body (AFTER all .getopt() calls!)
      self._ctrl = ctrl
      return ctrl

   #--------------------------------------------------------------------------

   def add_option (self, relkey, choice=None, **kwargs):
      """Add an option to the current menu. The purpose of this function
      is mainly to hide the use of 'self._TCM' to the Clump user/developer.
      In the future it might be useful to put some extra features here...
      """
      self._override_keys.append(relkey)          # see .execute_body()
      if True:
         # The option choice may be overridden via the input kwargs:
         if self._input_kwargs.has_key(relkey):
            v = self._input_kwargs[relkey]
            was = copy.copy(choice)
            if isinstance(v,list):                # e.g. [2,3]
               choice = v                         # replace choice
               kwargs['more'] = None              # do not allow other values 
            else:                                 # e.g. 2
               choice.insert(0,v)                 # make it the default
            print '\n** add_option(',relkey+'):',was,'->',choice,'\n'
      return self._TCM.add_option(relkey, choice, **kwargs)

   #--------------------------------------------------------------------------

   def execute_body(self, always=False, hist=False):
      """To be called at the start of the 'body' of a Clump stage-method,
      i.e. AFTER any self._TCM menu and option definitions.
      Its (mandatory!) counterpart is self.end_of_body(ctrl)
      It uses the record self._ctrl, defined in .on_entr()
      """

      self.check_for_overrides()

      fname = self._ctrl['funcname']                 # convenience

      execute = True                      
      if not always:                        
         if isinstance(self._ctrl['submenu'],str):
            execute = self._TCM.submenu_is_selected(trace=False)

      if self._ctrl['trace']:
         print '** .execute_body(always=',always,'): fname=',fname,' execute=',execute

      if not execute:
         if fname=='initexec':                       # a special case
            self._object_is_selected = False         # see .__init__() and .daisy_chain()
      else:
         if fname=='initexec':                       # a special case
            self._object_is_selected = True          # see .__init__() and .daisy_chain()
         self._stage['count'] += 1                   # increment
         self._stage['ops'] = -1                     # reset
         self._stage['name'] = fname                 # .....?
         if hist:
            s = '.'+fname+'(): '                     # note the ':'
            if isinstance(hist,str):
               s += '('+hist+')  '
            self.history(append=s, trace=self._ctrl['trace'])
      return execute

   #--------------------------------------------------------------------------

   def check_for_overrides (self):
      """Check whether self._kwargs (see .on_entry(**kwargs)) contains
      any of the option (rel)keys accumulated in .add_option(key),
      and put these override values in the dict self._override.
      The latter is then used in .getopt(key) to return the override value
      rather than the option value.
      """
      ovr = dict()
      for key in self._override_keys:
         if self._kwargs.has_key(key):
            ovr[key] = self._kwargs[key]
      if len(ovr)>0:
         self.history('.override: '+str(ovr))
      self._override = ovr                    # see .getopt()
      self._override_keys = []                # reset
      self._kwargs = None                     # reset
      return True


   #..........................................................................

   def getopt (self, relkey, trace=False):
      """Get the specified (relkey) TDL option value.
      This function is ONLY called AFTER self.execute_body()==True.
      It use the record self._ctrl that is defined in .on_entry()
      """
      # trace = True
      override = self._override.has_key(relkey)
      if override:
         value = self._TCM.getopt(relkey, self._ctrl['submenu'],
                                  override=self._override[relkey])
      else:
         value = self._TCM.getopt(relkey, self._ctrl['submenu'])

      if trace or self._ctrl['trace']:
         s = '.getopt(\''+str(relkey)+'\') ->'
         # s += ' '+str(type(value))
         s += ' '+str(value)
         if override:
            s += ' (overridden by kwarg)'
         print s
         self.history(s)
      return value

   #--------------------------------------------------------------------------

   def end_of_body(self, ctrl, hist=True):
      """
      To be called at the end of the body of a Clump stage-method.
      Counterpart of .execute_body()
      """
      fname = ctrl['funcname']                       # convenience
      if hist:
         s = '.'+fname+'()'
         if isinstance(hist,str):
            s += ' ('+hist+')  '
         self.history(s, show_node=True, trace=ctrl['trace'])
      if ctrl['trace']:
         print '** .end_of_body(ctrl): fname=',fname
      return True

   #..........................................................................

   def on_exit(self, ctrl, result=None):
      """
      To be called at the end of a Clump stage-method.
      Counterpart of ctrl = self.on_entry(func, **kwargs)
      Syntax: return self.on_exit(ctrl, result[=None])
      """
      fname = ctrl['funcname']                       # convenience
      if ctrl['submenu']:
         self._TCM.end_of_submenu()
      if ctrl['trace']:
         print '** .on_exit(ctrl, result=',result,'): fname=',fname,'\n'
      return result


   #--------------------------------------------------------------------------
   #--------------------------------------------------------------------------


   #=========================================================================
   # Functions dealing with subsets (of the tree nodes):
   #=========================================================================

   def get_indices(self, subset='*', severe=True, nodelist=None, trace=False):
      """Return a list of valid tree indices, according to subset[='*'].
      If subset is an integer, return that many (regularly spaced) indices.
      If subset is a list, check their validity.
      If subset is a string (e.g. '*'), decode it.
      """
      s = '.indices('+str(subset)+'):'

      # Turn subset into a list:
      if isinstance(subset,str):
         if subset=='*':
            ii = range(self.size())
         else:
            self.ERROR(s)
      elif isinstance(subset,int):
         ii = range(min(subset,self.size()))      # ..../??
      elif not isinstance(subset,(list,tuple)):
         self.ERROR(s)
      else:
         ii = list(subset)

      # Check the list elements:
      imax = self.size()
      for i in ii:
         if not isinstance(i,int):
            self.ERROR(s)
         elif i<0 or i>imax:
            self.ERROR(s)

      # Finished:
      if trace:
         print s,'->',ii
      return ii

   #---------------------------------------------------------------------

   def get_nodelist(self, subset='*',
                    unops=None, 
                    append=None, prepend=None,
                    nodelist=None, trace=False):
      """Helper function to get a list (copy) of (a subset of) its nodes.
      If nodelist is supplied, use that instead (multi-purpos function).
      If unops is specified, apply one or more unary operations.
      If append or prepend are nodes, append/prepend them to the list.
      """
      cc = []
      if isinstance(nodelist,(list,tuple)):
         # ii = self.get_indices(subset, nodelist=nodelist, trace=trace)   # <----??
         for i,node in enumerate(nodelist):
            # Test whether node is a node (or a number?)
            cc.append(node)
      else:
         ii = self.get_indices(subset, trace=trace)
         for i in ii:
            cc.append(self[i])

      if unops:
         # Optionally, apply one or more unary operations:
         cc = self.apply_unops (unops, nodelist=cc, replace=False)

      # Optionally, append/prepend nodes:
      if is_node(append):
         cc.append(append)
      if isinstance(append,list):
         cc.extend(append)
      if is_node(prepend):
         cc.insert(0,prepend)

      if trace:
         print '\n** get_nodes(',subset,str(append),str(prepend),nodelist,'):',self.oneliner()
         for i,node in enumerate(cc):
            print '  -',i,':',str(node)
         print
      return cc


   #=========================================================================
   # To and from tensor nodes:
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

      stub = self.unique_nodestub('rootnode')
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

   #-------------------------------------------------------------------------

   def bundle (self, nodelist=None, **kwargs):
      """Return a single node that bundles the Clump nodes, using the
      specified combining node (default: combine='Composer').
      The internal state of the object is not changed.
      """
      combine = kwargs.get('combine','Composer')
      name = kwargs.get('name',combine)
      wgt = kwargs.get('weights',None)                 # for WSum,WMean

      node = None
      hist = '.bundle('+str(combine)+') '
      if isinstance(nodelist,list):                    # external list
         cc = self.get_nodelist(nodelist=nodelist)     #   bundle it
         hist += 'external, n='+str(len(cc))
      elif not self._composed:                         # not in composed state
         cc = self.get_nodelist()                      #   bundle self._nodes
      elif combine=='Composer':                        # already the desired bundle
         node = self[0]                                #   just return it
      else:                                            # wrong bundle
         cc = self.decompose(replace=False)            #   decompose it first
         hist += 'rebundled'

      # Make the bundle node:
      if node==None:
         stub = self.unique_nodestub(name)
         qual = 'n='+str(self.size())
         if wgt:                                       # assume WSum or WMean
            node = stub(qual) << getattr(Meq,combine)(children=cc,
                                                      weights=wgt)
         else:
            node = stub(qual) << getattr(Meq,combine)(*cc)
         hist += ' [0]='+str(cc[0])
         hist += ' -> '+str(node)
         self.history(hist)
         
      # Always return the single bundle node:
      return node

   #-------------------------------------------------------------------------

   def compose (self, replace=True, **kwargs):
      """
      Compose the list of clump nodes into a single tensor node.
      If replace=False, do Not change the state of the Clump object itself.
      Always return the single tensor node. See also .decompose().
      """

      if self._composed:                   # already in composed state
         node = self._nodes[0]             # return node
         replace = False
      else:
         qual = 'composed'+str(self.size())
         stub = self.unique_nodestub(qual)
         node = stub('composed') << Meq.Composer(*self._nodes)

      if replace:
         self._nodes = [node]              # a list of a single node
         self._composed = True             # set the switch
         self._nodequals = [qual]
         self.history('.compose()', show_node=True,
                      trace=kwargs.get('trace',False))
      # Always return the single tensor node:
      return node

   #-------------------------------------------------------------------------

   def decompose (self, replace=True, **kwargs):
      """
      The reverse of .compose(). Decompose the single tensor node of the
      'composed' state into a list of separate tree nodes.
      If replace=False, do not change the state of the Clump object itself.
      Always returns the list of separate tree nodes.
      """
      if not self._composed:               # already in de-composed state
         cc = self.get_nodelist()          # return list 
         replace = False
      else:             
         tensor = self._nodes[0]           # the single tensor node
         stub = self.unique_nodestub('decomposed')
         cc = []
         for index,qual in enumerate(self._datadesc['treequals']):
            node = stub(qual) << Meq.Selector(tensor, index=index)
            cc.append(node)

      if replace:
         self._nodes = cc
         cc = self.get_nodelist()          # return list 
         self._composed = False            # set the switch
         self._nodequals = self._datadesc['treequals']
         self.history('.decompose()', show_node=True,
                      trace=kwargs.get('trace',False))
      # Always return the list of decomposed nodes:
      return cc



   #=========================================================================
   # Solver support functions:
   #=========================================================================

   def insert_reqseqs (self, node, name=None, trace=False):
      """ Insert a ReqSeq (in every tree!) that issues a request first to
      the given node (e.g. a solver node), and then to the current tree node.
      NB: The fact that there is a ReqSeq in every tree seems wasteful, but
      it synchronises the processing in the different trees of the Clump....
      """
      if is_node(node):
         stub = self.unique_nodestub(name=name)
         for i,qual in enumerate(self._nodequals):
            self._nodes[i] = stub(qual) << Meq.ReqSeq(node, self[i],
                                                           result_index=1,
                                                           cache_num_active_parents=1)
         self.history('.insert_reqseqs('+str(node)+')', show_node=True)
      return True

   #-------------------------------------------------------------------------

   def ParmClumps(self, append=None, trace=False):
      """Access to the internal list of ParmClumps
      """
      if isinstance(append,list):
         self._ParmClumps.extend(append)
      elif append:
         self._ParmClumps.append(append)
      if trace:
         print '\n** ParmClumps'+len(self._ParmClumps)+':'+self.oneliner()
         for i,pc in enumerate(self._ParmClumps):
            print '-',i,':',str(pc)
         print
      return self._ParmClumps

   #-------------------------------------------------------------------------

   def get_solvable(self, trace=False):
      """Get all the solvable parameters from the entries of self._ParmClumps.
      """
      solvable = []
      for pc in self.ParmClumps():
         ss = pc.solspec(select=True)
         solvable.extend(ss)
         s = 'Got '+str(len(ss))+' (total='+str(len(solvable))+') '
         s += 'solvable MeqParms from: '+pc.oneliner()
         self.history(s)

      if len(solvable)==0:
         self.WARNING('No solvable MeqParms specified! (using defaults)')
         ss = self.ParmClumps()[0].solspec(always=True)
         solvable = ss
         s = 'Got '+str(len(ss))+' (total='+str(len(solvable))+') '
         s += '(default!) solvable MeqParms from: '+pc.oneliner()
         self.history(s)
         
      # Return list of solvable MeqParms:
      if trace:
         print '\n** .solvable():'
         for i,node in enumerate(solvable):
            print '-',i,':',str(node)
         print
      return solvable   





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





