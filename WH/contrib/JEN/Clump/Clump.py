"""
Clump.py: Base-class for an entire zoo of derived classes that
represent 'clumps' of trees, i.e. sets of similar nodes.
Examples are ParmClump, JonesClump and VisClump.
A strong emphasis is on the possibilities for linking Clump-nodes
(and their option menus!) together in various ways. To a large
extent, the Clump configuration of the Clumps may be controlled
by the user via the menus. 
"""

# file: ../JEN/Clump/Clump.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 25 oct 2008: creation
#   - 03 nov 2008: added class LeafClump
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

clump_counter = -1          # used in Clump.__init__()

#******************************************************************************** 

class Clump (object):
   """
   Base-class for an entire zoo of derived classes that
   represent 'clumps' of trees, i.e. sets of similar nodes.
   Examples are ParmClump, JonesClump and VisClump.
   """

   def __init__(self, clump=None, **kwargs):
      """
      Initialize the Clump object, according to its type (see .init()).
      If another Clump of the same class is specified (use), use its
      defining characteristics (in self._datadesc etc)
      """

      # These need a little more thought:
      kwargs.setdefault('select', None)                 # <------- !!?
      trace = kwargs.get('trace',False)                 # <------- !!?

      self._slaveof = kwargs.get('slaveof',None)        # <------- !!?

      self._input_kwargs = kwargs

      # Make a short version of the actual type name (e.g. Clump)
      self._typename = str(type(self)).split('.')[-1].split("'")[0]

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
      self.unique_nodestub()

      #......................................................................
      # Fill self._nodes (the Clump tree nodes) etc.
      #......................................................................

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

      # The tree nodes may be 'composed' into a single tensor node.
      # In that case, the following node qualifier will be used.
      # self._tensor_qual = 'tensor'+str(self.size())
      self._tensor_qual = 'tensor'

      # Execute the main function of the Clump object.
      # This function is re-implemented in derived Clump classes.
      self._object_is_selected = False           # see .execute_body()     
      self.initexec(**kwargs)

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

   #==========================================================================
   # Placeholder for the initexec function of the Clump object.
   # (to be re-implemented in derived classes)
   #==========================================================================

   def initexec (self, **kwargs):
      """
      The initexec function of this object, called from Clump.__init__().
      It is a placeholder, to be re-implemented by derived classes. 
      It has standard structure that is recommended for all such functions,
      which has services like making a submenu for this Clump object,
      which can be used for selecting it.
      Actual re-implementations in derived classes may have a menu with options,
      they usually have statements in the 'body' that generate nodes, and they
      may return some result.
      See also templateClump.py and templateLeafClump.py
      """

      # This placeholder function contains the regular structure
      # because it may be required to generate a menu in on_entry()
      
      ctrl = self.on_entry(self.initexec, **kwargs)
      if self.execute_body():
         # Do not do anything in the body of this placeholder!
         self.end_of_body(ctrl)
      return self.on_exit(ctrl, result=None)

   #-------------------------------------------------------------------------

   def newinstance(self, **kwargs):
      """Make a new instance of this class. Called by .link().
      This function should be re-implemented in derived classes.
      """
      return Clump(clump=self, **kwargs)


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

   #--------------------------------------------------------------------
         
   def compare (self, clump, **kwargs):
      """
      Compare (Subtract, Divide) its nodes with the corresponding
      nodes of another Clump. Return a new Clump object with the result.
      """
      kwargs['select'] = True
      binop = kwargs.get('binop','Subtract')
      prompt = '.compare('+binop+')'
      help = clump.oneliner()
      ctrl = self.on_entry(self.compare, prompt, help, **kwargs)

      new = None
      if self.execute_body():
         new = self.copy()                                    # <-----!!
         new.apply_binop(binop, clump, **kwargs)              # <-----!!
         self._orphans.extend(new._orphans)                   # <---- !!
         self.end_of_body(ctrl)

      return self.on_exit(ctrl, result=new)



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
         ss += '  (composed: '+self._tensor_qual+')'
      return ss

   #--------------------------------------------------------------------------

   def show (self, txt=None, full=True, doprint=True):
      """
      Format a summary of the contents of the object.
      If doprint=True, print it also.  
      """
      ss = '\n'
      ss += '\n** '+self.oneliner()
      if txt:
         ss += '   ('+str(txt)+')'

      #.....................................................
      if isinstance(self._input_clump, list):
         ss += '\n > self._input_clump: list of '+str(len(self._input_clump))+' nodes'
      elif self._input_clump:
         ss += '\n > self._input_clump: '+str(self._input_clump.oneliner())
      else:
         ss += '\n > self._input_clump = '+str(self._input_clump)

      ss += '\n > self._input_kwargs = '+str(self._input_kwargs)
      ss += '\n > self._override = '+str(self._override)

      #.....................................................

      ss += '\n * Generic (baseclass Clump):'
      ss += '\n * self._object_is_selected: '+str(self._object_is_selected)    
      ss += '\n * self._name = '+str(self._name)
      ss += '\n * self._qual = '+str(self._qual)
      ss += '\n * self._kwqual = '+str(self._kwqual)

      ss += '\n * self._slaveof: '+str(self._slaveof)

      ss += '\n * self._stage = '+str(self._stage)
      
      ss += '\n * self._datadesc:'
      dd = self._datadesc
      for key in dd.keys():
         ss += '\n   - '+str(key)+' = '+str(dd[key])

      #.....................................................

      ss += '\n * self._nodes (.len()='+str(self.len())+', .size()='+str(self.size())+'):'
      n = len(self._nodes)
      if full:
         nmax = 2
         for i in range(min(nmax,n)):
            ss += '\n   - '+str(self[i])
         if n>nmax:
            if n>nmax+1:
               ss += '\n       ...'
            ss += '\n   - '+str(self[-1])
      else:
         ss += '\n   - node[0] = '+str(self[0])
         ss += '\n   - node[-1]= '+str(self[-1])
                                       
      #.....................................................
      ss += '\n * self._ParmClumps (n='+str(len(self._ParmClumps))+'):'
      for i,pc in enumerate(self._ParmClumps):
         ss += '\n   - '+str(pc.oneliner())

      #.....................................................
      ss += '\n * (rootnode of) self._stubtree: '+str(self._stubtree)
      ss += '\n * self._orphans (n='+str(len(self._orphans))+'):'
      for i,node in enumerate(self._orphans):
         ss += '\n   - '+str(node)
      #.....................................................

      ss += '\n * self._ns: '+str(self._ns)
      if self._TCM:
         ss += '\n * self._TCM: '+str(self._TCM.oneliner())
      else:
         ss += '\n * self._TCM = '+str(self._TCM)
      #.....................................................

      ss += '\n * self._ctrl: '+str(self._ctrl)
      ss += self.history(format=True, prefix='   | ')

      #.....................................................
      ss += self.show_specific()
      ss += '\n % self._rider (user-defined information):'
      rr = self._rider
      for key in rr.keys():
         if getattr(rr[key],'oneliner',None):
            ss += '\n   - '+str(key)+' = '+str(rr[key].oneliner())
         else:
            ss += '\n   - '+str(key)+' = '+str(EF.format_value(rr[key]))

      #.....................................................
      ss += '\n**\n'
      if doprint:
         print ss
      return ss

   #-------------------------------------------------------------------------

   def show_specific(self):
      """
      Format the specific (non-generic) contents of the class.
      Placeholder for re-implementation in derived class.
      """
      ss = '\n + Specific (derived class '+str(self._typename)+'):'
      ss += '\n + ...'
      return ss

   #-------------------------------------------------------------------------

   def show_tree (self, index=-1, full=True):
      """Show the specified (index) subtree.
      """
      node = self._nodes[index]
      print EN.format_tree(node, full=full)
      return True

   #-------------------------------------------------------------------------
   #-------------------------------------------------------------------------

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

   def history (self, append=None,
                show_node=False,
                prefix='', format=False, 
                clear=False, show=False, trace=False):
      """Interact with the object history (a list of strings).
      """
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
      if show_node:
         ilast = self.len()-1
         s = '   -> '+str(self[ilast])
         self._history[-1] += s
         if trace:
            print '   >> .history(show_node): ',self._history[-1]

      # Format the history into a multi-line string (ss):
      if show or format:
         ss = ''
         for line in self._history:
            ss += '\n'+prefix+line
         ss += '\n'+prefix+'** Current oneliner(): '+str(self.oneliner())
         ss += '\n   |'
         if show:
            print ss
         if format:
            return ss

      # Always return the currently accumulated history (except when format=True)
      return self._history

   #--------------------------------------------------------------------------
   #--------------------------------------------------------------------------

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
   # Some general helper functions
   #=========================================================================

   def len(self):
      """Return the number of tree nodes in the Clump (=1 if composed)
      """
      return len(self._nodes)

   #--------------------------------------------------------------------------

   def indices(self):
      """Return the list of indices [0,1,2,...] of the actual tree nodes.
      If composed, this will be [0] (referring to a single tensor node).
      """
      return range(self.len())

   #--------------------------------------------------------------------------

   def size(self):
      """Return the number of trees in the Clump (even if in a tensor)
      """
      return len(self._datadesc['treequals'])

   #--------------------------------------------------------------------------

   def __getitem__(self, index):
      """Get the specified (index) node. Syntax: node = clump[i]
      """
      return self._nodes[index]

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

   #-------------------------------------------------------------------------

   def graft_to_stubtree(self, node):
      """Helper function to graft the given node (usually the rootnode
      of the stubtree of another clump) to its own self._stubtree.
      """
      stub = self.unique_nodestub()
      self._stubtree = stub('graft_to_stubtree') << Meq.Add(self._stubtree,node)
      return True
      

   #=========================================================================
   # Functions dealing with subsets (of the tree nodes):
   #=========================================================================

   def get_indices(self, subset='*', severe=True, trace=False):
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


   #-------------------------------------------------------------------------

   def get_nodes(self, subset='*', trace=False):
      """Return the specified (subset) subset of the tree nodes.
      """
      ii = self.get_indices(subset, trace=trace)
      nodes = []
      for i in ii:
         nodes.append(self[i])
         if trace:
            print '-',str(nodes[-1])
      return nodes


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

   def bundle (self, **kwargs):
      """Return a single node that bundles the Clump nodes, using the
      specified combining node (default: combine='Composer').
      The internal state of the object is not changed.
      """
      combine = kwargs.get('combine','Composer')
      name = kwargs.get('name',combine)
      wgt = kwargs.get('weights',None)                 # for WSum,WMean

      stub = self.unique_nodestub(name)
      qual = 'n='+str(self.size())
      if not self._composed:
         cc = self._nodes
         if wgt:
            node = stub(qual) << getattr(Meq,combine)(children=cc,
                                                      weights=wgt)
         else:
            node = stub(qual) << getattr(Meq,combine)(*cc)
      elif combine=='Composer':
         node = stub('tensor') << Meq.Identity(self[0]) 
      else:
         self.ERROR(hist+' Clump is in composed state **')
      
      hist = '.bundle('+str(combine)+')'
      # self.history(hist, trace=kwargs.get('trace',False))
      return node

   #-------------------------------------------------------------------------

   def compose (self, **kwargs):
      """
      Make sure that the Clump object is in the 'composed' state,
      i.e. self._nodes contains a single tensor node.
      which has all the tree nodes as its children.
      Returns the single tensor node. The reverse of .decompose().
      """
      node = self._nodes[0]
      if self._composed:                   # already in composed state
         pass                              #   do nothing (history()?)
      elif self.size()==1:                 # only one tree in the Clump
         self._composed = True             #   just set the switch
      else:
         stub = self.unique_nodestub(self._tensor_qual)
         node = stub('composed') << Meq.Composer(*self._nodes)
         self._nodes = [node]              # a list of a single node
         self._composed = True             # set the switch
         self._nodequals = [self._tensor_qual]
         self.history('.compose()', show_node=True,
                      trace=kwargs.get('trace',False))
      return node

   #-------------------------------------------------------------------------

   def decompose (self, **kwargs):
      """
      Make sure that the Clump object is in the 'decomposed' state,
      i.e. self._nodes contains separate tree nodes.
      The reverse of .compose().
      Always returns the list of separate tree nodes.
      """
      nodes = self._nodes[0]
      if not self._composed:               # already in de-composed state
         pass                              #   do nothing (history()?)
      elif self.size()==1:                 # only one tree in the Clump
         self._composed = False            #   just set the switch
      else:             
         tensor = self._nodes[0]
         nodes = []
         stub = self.unique_nodestub('decomposed')
         for index,qual in enumerate(self._datadesc['treequals']):
            node = stub(qual) << Meq.Selector(tensor, index=index)
            nodes.append(node)
         self._nodes = nodes
         self._composed = False            # set the switch
         self._nodequals = self._datadesc['treequals']
         self.history('.decompose()', show_node=True,
                      trace=kwargs.get('trace',False))
      return self._nodes

   #-------------------------------------------------------------------------

   #-------------------------------------------------------------------------

   #-------------------------------------------------------------------------

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

   def get_solvable(self, trace=False):
      """Get all the solvable parameters from the entries of self._ParmClumps.
      """
      solvable = []
      for pc in self._ParmClumps:
         ss = pc.solspec(select=True)
         solvable.extend(ss)
         s = 'Got '+str(len(ss))+' (total='+str(len(solvable))+') '
         s += 'solvable MeqParms from: '+pc.oneliner()
         self.history(s)

      if len(solvable)==0:
         self.WARNING('No solvable MeqParms specified! (using defaults)')
         ss = self._ParmClumps[0].solspec(always=True)
         solvable = ss
         s = 'Got '+str(len(ss))+' (total='+str(len(solvable))+') '
         s += '(default!) solvable MeqParms from: '+pc.oneliner()
         self.history(s)
         
      # Return list of solvable MeqParms:
      return solvable   

   #=========================================================================
   # Apply arbitrary unary (unops) or binary (binops) operaions to the nodes:
   #=========================================================================

   def check_unops(self, unops):
      """Helper function to make sure that the given unops is a list
      of unary operations, e.g. ['Sin','Cos'].
      """
      if isinstance(unops,str):
         unops = unops.split(' ')                    # 'Cos Sin' -> ['Cos','Sin']
      elif not isinstance(unops,(list,tuple)):
         self.ERROR('** invalid unops: '+str(unops))
      return unops

   #-------------------------------------------------------------------------

   def apply_unops (self, unops, **kwargs):
      """
      Apply one or more unary operation(s) (e.g. Cos(..)) on its nodes.
      Multiple unops may be specified as a list, or string with blanks
      between the operations (e.g. 'Sin Cos Exp').
      The operations are applied in the order of specification
      (i.e. the reverse of the usual scientific notation!)
      If replace==False, do NOT replace 
      Always return the list of nodes.
      """
      # First make sure that unops is a list:
      unops = self.check_unops(unops)
      replace = kwargs.get('replace',True)

      # Apply in order of specification:
      cc = []
      for i,qual in enumerate(self._nodequals):
         cc.append(self[i])

      sunops = '..'
      for unop in unops:
         if not isinstance(unop,str):
            self.ERROR('unop is not a string: '+str(type(unop)+str(unop)))
         unop = unop.replace('Meq','')               # just in case....
         sunops = unop+'('+sunops+')'
         stub = self.unique_nodestub(unop+'()', **kwargs)
         for i,qual in enumerate(self._nodequals):
            cc[i] = stub(qual) << getattr(Meq,unop)(cc[i],**kwargs))

      if replace:
         self._nodes = cc                  # replace self._nodes
         # Make a history entry:
         hist = '.apply_unops('+str(unops)
         for key in kwargs.keys():
            hist += ', '+str(key)+'='+str(kwargs[key])
         hist += '): '
         if len(unops)>1:
            hist += sunops
         self.history(hist, show_node=True)

      # Always return the list of nodes
      return cc

   #-------------------------------------------------------------------------

   def apply_binop (self, binop, rhs, **kwargs):
      """Apply a binary operation (binop, e.g. 'Add') between its nodes
      and the given right-hand-side (rhs). The latter may be various
      things: a Clump, a node, a number etc.
      """
      if not isinstance(binop,str):
         self.ERROR('binop is not a string: '+str(type(binop)+str(binop)))
      binop = binop.replace('Meq','')            # just in case....

      hist = None
      if isinstance(rhs,(int,float,complex)):    # rhs is a number
         srhs = EF.format_value(rhs)
         hist = 'rhs='+srhs
         stub = self.unique_nodestub(binop, srhs)
         for i,qual in enumerate(self._nodequals):
            self._nodes[i] = stub(qual) << getattr(Meq,binop)(self[i],rhs)
         
      elif is_node(rhs):                         # rhs is a node
         hist = 'rhs='+str(rhs.name)
         stub = self.unique_nodestub(binop, rhs.classname)
         for i,qual in enumerate(self._nodequals):
            self._nodes[i] = stub(qual) << getattr(Meq,binop)(self[i],rhs)

      elif isinstance(rhs,type(self)):           # rhs is a Clump object
         if self.commensurate(rhs, severe=True):
            hist = 'rhs='+rhs.oneliner()
            stub = self.unique_nodestub(binop, rhs._typename)
            for i,qual in enumerate(self._nodequals):
               self._nodes[i] = stub(qual) << getattr(Meq,binop)(self[i],rhs[i])

      hist = '.apply_binop('+str(binop)+', '+str(hist)+')'
      self.history(hist, show_node=True)
      return True


   #=========================================================================
   # Visualization:
   #=========================================================================

   def make_bookmark (self, nodes, name=None,
                      bookpage=None, folder=None,
                      recurse=0,
                      viewer='Result Plotter', ):
      """Make a bookmark for the specified nodes, with the specified
      bookpage[=None], folder[=None] and viewer[='Result Plotter']
      """
      if not isinstance(folder,str):
         folder = self._name
      JEN_bookmarks.create(nodes,
                           name=(name or bookpage),
                           folder=folder,
                           recurse=recurse,
                           viewer=viewer)
      # Alternative: Meow bookmarks.....
      return True

   #--------------------------------------------------------------------

   def make_bookmark_help(self, node, help=None, bookmark=True, trace=False):
      """Attach the given help to the quickref_help field of the given node
      and make a bookmark with the QuickRef Viewer.
      If bookmark=False, just attach the help, but do not make the bookmark.
      """
      # trace = True
      initrec = node.initrec()
      if trace:
         print '\n** make_bookmark_help(',str(node),'): initrec =',initrec
      initrec.quickref_help = str(help)
      if trace:
         print '   -> ',node.initrec(),'\n'
      if bookmark:
         self.make_bookmark(node, viewer='QuickRef Display')
      return node

   #---------------------------------------------------------------------------

   def initrec2help (self, node, help=[], ignore=[], prefix='', trace=False):
      """Helper function to add the contents of node.initrec() to
      the given help-string. It returns the new help string.
      """
      if is_node(node):
         if not isinstance(ignore,list):
            ignore = []
         for key in ['class']:
            if not key in ignore:
               ignore.append(key)
         indent = '\n'+str(prefix)+'      '
         help += indent+'| node.initrec() of:   '+str(node)+':'
         rr = node.initrec() 
         for key in rr.keys():
            if not key in ignore:
               help += indent+'|   - '+key+' = '+str(rr[key])
         help += indent+'| (ignored: '+str(ignore)+')'
      return help

   #---------------------------------------------------------------------
   #---------------------------------------------------------------------

   def visualize (self, **kwargs):
      """Choice of various forms of visualization.
      """
      kwargs['select']=True
      bookpage = kwargs.get('bookpage', None)
      folder = kwargs.get('folder', None)

      prompt = '.visualize()'
      help = 'Select various forms of Clump visualization'
      # print '\n**',help,'\n'
      ctrl = self.on_entry(self.visualize, prompt, help, **kwargs)

      if self.execute_body():
         self.inspector(**kwargs)
         self.plot_node_results(**kwargs)
         self.plot_node_family(**kwargs)
         self.plot_node_bundle(**kwargs)
         self.plot_summary(**kwargs)
         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl)

   #---------------------------------------------------------------------

   def inspector (self, **kwargs):
      """Make an inspector node for its nodes, and make a bookmark.
      """
      kwargs['select'] = True
      bookpage = kwargs.get('bookpage', None)
      folder = kwargs.get('folder', None)

      prompt = '.inspector()'
      help = 'make an inspector-plot (Collections Plotter) of the tree nodes'
      ctrl = self.on_entry(self.inspector, prompt, help, **kwargs)

      if self.execute_body(hist=False):
         bundle = self.bundle(name='inspector')
         bundle.initrec().plot_label = self._datadesc['treelabels']     # list of strings!
         self._orphans.append(bundle)
         self.make_bookmark(bundle,
                            name=bookpage, folder=folder,
                            viewer='Collections Plotter')
         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl)


   #---------------------------------------------------------------------

   def plot_summary (self, **kwargs):
      """Plot a summary of its nodes
      """
      kwargs['select'] = True

      prompt = '.plot_summary()'
      help = 'make a summary plot of the tree nodes'
      ctrl = self.on_entry(self.plot_summary, prompt, help, **kwargs)

      if self.execute_body(hist=False):
         bookpage = kwargs.get('bookpage', None)
         folder = kwargs.get('folder', None)
         name = kwargs.get('name', None)
         if not isinstance(name,str):
            name = 'summary'

         node = self[0]
         if self.size()>1:
            cc = self.apply_unops('Abs', replace=False)
            stub = self.unique_nodestub()
            sumabs = stub('sumabs') << Meq.Add(*cc)
            cc = self.get_nodes(prepend=sumabs)
            node = stub(name) << Meq.Composer(*cc)
            self.make_bookmark(node, name=bookpage, folder=folder)
         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl)

   #---------------------------------------------------------------------

   def get_nodes(self, append=None, prepend=None):
      """Helper function to get a list (copy) of its nodes.
      """
      cc = []
      for node in self._nodes:
         cc.append(node)
      if is_node(append):
         cc.append(append)
      if isinstance(append,list)):
         cc.extend(append)
      if is_node(prepend):
         cc.insert(0,prepend)
      return cc

   #---------------------------------------------------------------------

   def plot_node_bundle (self, **kwargs):
      """Make a plot for the bundle (Composer) of its nodes, and make a bookmark.
      """
      bookpage = kwargs.get('bookpage', None)
      folder = kwargs.get('folder', None)

      prompt = '.plot_node_bundle()'
      help = 'plot the bundle (MeqComposer) of all tree nodes'
      ctrl = self.on_entry(self.plot_node_bundle, prompt, help, **kwargs)

      if self.execute_body(hist=False):
         bundle = self.bundle()
         self._orphans.append(bundle)
         self.make_bookmark(bundle, name=bookpage, folder=folder)
         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl)

   #---------------------------------------------------------------------

   def plot_node_results (self, **kwargs):
      """Plot the specified (index) subset of the members of self._nodes
      with the specified viewer [=Result Plotter=],
      on the specified bookpage and folder.
      """
      index = kwargs.get('index', '*')
      bookpage = kwargs.get('bookpage', None)
      folder = kwargs.get('folder', None)
      viewer = kwargs.get('viewer', 'Result Plotter')

      prompt = '.plot_node_results()'
      help = 'plot the results of the tree nodes on the same page' 
      ctrl = self.on_entry(self.plot_node_results, prompt, help, **kwargs)

      if self.execute_body(hist=False):
         if not isinstance(bookpage,str):
            bookpage = self[0].basename
            bookpage += '['+str(index)+']'
         nodes = []
         for node in self._nodes:
            nodes.append(node)
         if not isinstance(folder,str):
            folder = self._name
         self.make_bookmark(nodes,
                            name=bookpage, folder=folder,
                            viewer=viewer)
         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl)

   #---------------------------------------------------------------------

   def plot_node_family (self, **kwargs):
      """Plot the plot_node_family (parent, child(ren), etc) of the specified (index) tree node
      down to the specified recursion level [=2]
      with the specified viewer [=Result Plotter=],
      on the specified bookpage and folder.
      """
      index = kwargs.get('index', 0)
      recurse = kwargs.get('recurse', 2)
      bookpage = kwargs.get('bookpage', None)
      folder = kwargs.get('folder', None)
      viewer = kwargs.get('viewer', 'Result Plotter')

      prompt = '.plot_node_family()'
      help = """Plot the family (itself, its children etc) of the specified [=0] tree node,
      to the specified [=2] recursion depth"""
      ctrl = self.on_entry(self.plot_node_family, prompt, help, **kwargs)

      if self.execute_body(hist=False):
         if not isinstance(bookpage,str):
            bookpage = (recurse*'+')
            bookpage += self[0].basename
            nodequal = self._nodequals[index]
            bookpage += '['+str(nodequal)+']'
         if not isinstance(folder,str):
            folder = self._name
            self.make_bookmark(self[index],
                               recurse=recurse,
                               name=bookpage, folder=folder,
                               viewer=viewer)
         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl)


   #=========================================================================
   # Interaction with the (user-defined) rider:
   #=========================================================================

   def rider (self, key=None, **kwargs):
      """The rider contains arbitrary user-defined information.
      """
      trace = kwargs.get('trace',False)
      severe = kwargs.get('severe',True)
      rr = self._rider                     # convenience

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


















#********************************************************************************
#********************************************************************************
#********************************************************************************
#********************************************************************************
#********************************************************************************
# Derived class LeafClump:
#********************************************************************************

class LeafClump(Clump):
   """
   Derived from class Clump. It is itself a base-class for all Clump-classes
   that start with leaf-nodes, i.e. nodes that have no children.
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class Clump.
      """
      # Make sure that a visible option/selection menu is generated
      # for all LeafClump classes.
      kwargs['select'] = True                           # always make a clump selection menu
      kwargs['transfer_clump_nodes'] = False            # see Clump.__init___()

      # The data-description may be (re-)defined by means of kwargs:
      if not getattr(self,'_datadesc',None):
         self.datadesc(complex=kwargs.get('complex',False),
                       treequals=kwargs.get('treequals',range(3)),
                       dims=kwargs.get('dims',1))

      # The following executes the function self.initexec(**kwargs),
      # which is re-implemented below.
      Clump.__init__(self, clump=clump, **kwargs)
      
      return None


   #-------------------------------------------------------------------------
   # Re-implementation of its initexec function (called from Clump.__init__())
   #-------------------------------------------------------------------------

   def initexec (self, **kwargs):
      """
      Re-implementation of the place-holder function in class Clump.
      It is itself a place-holder, to be re-implemented in classse derived
      from LeafClump, to generate suitable leaf nodes.
      This function is called in Clump.__init__().
      See also templateLeafClump.py
      """
      kwargs['fixture'] = True              # this clump is always selected

      help = 'make leaf nodes for: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, help=help, **kwargs)

      # Execute always (always=True), to ensure that the leaf Clump has nodes:
      if self.execute_body(always=True):
         dd = self.datadesc()
         nelem = dd['nelem']
         self._nodes = []
         stub = self.unique_nodestub('const')
         for i,qual in enumerate(self._nodequals):
            cc = []
            for k,elem in enumerate(dd['elems']):
               if dd['complex']:
                  v = complex(k+i,i/10.)
               else:
                  v = float(k+i)
               if nelem==1:
                  node = stub(c=v)(qual) << Meq.Constant(v)
               else:
                  node = stub(c=v)(qual)(elem) << Meq.Constant(v)
               cc.append(node)
            if nelem>1:
               node = stub(nelem=nelem)(qual) << Meq.Composer(*cc)
            self._nodes.append(node)
         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl)




#********************************************************************************
#********************************************************************************
#********************************************************************************
# Derived class ListClump:
#********************************************************************************

class ListClump(Clump):
   """
   A Clump may also be created from a list of nodes.
   """

   def __init__(self, nodelist, **kwargs):
      """
      Derived from class Clump.
      """
      # Check the input nodelist:
      nn = []
      if is_node(nodelist):                  # A single node
         nn = [nodelist]                     
      elif not isinstance(nodelist,(list,tuple)):
         self.ERROR('** nodelist should be a list, tuple or node')
      else:
         for i,node in enumerate(nodelist):
            if not is_node(node):
               self.ERROR('** not a node, but: '+str(type(node)))
            nn.append(node)

      if len(nn)==0:
         self.ERROR('** nodelist is empty')

      # The data-description may be defined by means of kwargs:
      self.datadesc(complex=kwargs.get('complex',False),
                    treequals=range(len(nn)), 
                    dims=kwargs.get('dims',1))

      # Fill the Clump with the nodes from nn: 
      self._nodes = []
      self._nodequals = []
      for i,node in enumerate(nn):
         self._nodes.append(node)
         self._nodequals.append(i)
      self._composed = False

      #...................................................
      # Create the Clump:
      kwargs['transfer_clump_nodes'] = False            # see Clump.__init___()
      Clump.__init__(self, **kwargs)
      #...................................................

      self.history('Created from list of nodes', show_node=True)
      return None


   #------------------------------------------------------------------------

   def initexec (self, **kwargs):
      """
      Re-implementation of the function in class Clump. It does even less.
      """
      return None










#********************************************************************************
#********************************************************************************
# Function called from _define_forest() in ClumpExec.py
#********************************************************************************
#********************************************************************************


def do_define_forest (ns, TCM):
   """
   Testing function for the class(es) in this module.
   It is called by ClumpExec.py
   """
   # Definition of menus and options:
   submenu = TCM.start_of_submenu(do_define_forest,
                                  prompt=__file__.split('/')[-1],
                                  help=__file__)

   # The function body:
   clump = None
   if TCM.submenu_is_selected():
      clump = LeafClump(ns=ns, TCM=TCM, trace=True)
      # clump.show('do_define_forest(creation)', full=True)
      clump.apply_unops('Cos')
      # clump.apply_unops('Sin')
      # clump.apply_unops('Exp')
      # clump.apply_binop('Add', 2.3, select=True, trace=True)
      # clump = Clump(clump, select=True).daisy_chain()
      # clump = Clump(clump, select=True).daisy_chain()
      clump.visualize()               # make VisualClump class....?
      # clump.compare(clump)

   # The LAST statement:
   TCM.end_of_submenu()
   return clump


#********************************************************************************
#********************************************************************************
# Standalone test (without the browser):
#********************************************************************************
#********************************************************************************

if __name__ == '__main__':

   print '\n****************************************************'
   print '** Start of standalone test of: Clump.py:'
   print '****************************************************\n' 

   ns = NodeScope()

   if 1:
      clump = LeafClump(trace=True)

   if 0:
      cc = []
      for i in range(4):
         node = ns.ddd(i) << Meq.Constant(i)
         cc.append(node)
      clump = ListClump(cc, ns=ns, trace=True)

   if 1:
      clump.show('creation', full=True)

   if 0:
      clump.rider('aa', new=56)
      clump.rider('bb', new='56')
      clump.rider('clump', new=clump)

   if 0:
      print '** print str(clump) ->',str(clump)
      print '** print clump ->',clump

   if 0:
      for node in clump:
         print str(node)
   if 0:
      for index in [0,1,-1]:
         print '-- clump[',index,'] -> ',str(clump[index])
      # print '-- clump[78] -> ',str(clump[78])

   if 0:
      clump.show_tree(-1, full=True)

   if 0:
      print '.compose() ->',clump.compose()
      clump.show('.compose()')
      if 1:
         print '.decompose() ->',clump.decompose()
         clump.show('.decompose()')

   if 1:
      unops = 'Cos'
      unops = ['Cos','Cos','Cos']
      unops = 'Cos Sin'
      unops = 'MeqCos'
      # unops = ['Cos','Sin']
      clump.apply_unops(unops)    
      clump.apply_unops('Resampler', mode=2)    
      # clump.apply_unops()                       # error

   if 1:
      rhs = math.pi
      # rhs = ns.rhs << Meq.Constant(2.3)
      # rhs = Clump('RHS', clump=clump)
      clump.apply_binop('Add', rhs)
      clump.apply_binop('Add', clump)
      clump.apply_binop('Add', ns<<3.4)

   if 0:
      treequals = range(5)
      treequals = ['a','b','c']
      clump3 = LeafClump(treequals=treequals)
      clump.commensurate(clump3, severe=False, trace=True)
      clump3.show('.commensurate()')

   if 0:
      print clump.bundle()
      clump.show('.bundle()')

   if 0:
      node = ns.dummysolver << Meq.Constant(67)
      clump.insert_reqseqs(node, trace=True)
      clump.show('.insert_reqseqs()')

   if 0:
      node = clump.inspector()
      clump.show('.inspector()')
      print '->',str(node)

   if 0:
      node = clump.rootnode() 
      clump.show('.rootnode()')
      print '->',str(node)

   if 0:
      clump1 = Clump(clump, select=True)
      clump1.show('clump1 = Clump(clump)', full=True)

   if 0:
      clump = Clump(clump, select=True).daisy_chain(trace=True)
      clump.show('daisy_chain()', full=True)

   if 1:
      clump.show('final', full=True)

   #-------------------------------------------------------------------
   # Some lower-level tests:
   #-------------------------------------------------------------------

   if 0:
      print getattr(clump,'oneline',None)

   if 0:
      clump.execute_body(None, a=6, b=7)

   if 0:
      clump.get_indices(trace=True)
      clump.get_indices('*',trace=True)
      clump.get_indices(2, trace=True)
      clump.get_indices([2],trace=True)

   if 0:
      clump.get_nodes(subset=0, trace=True)
   
   # print 'Clump.__module__ =',Clump.__module__
   # print 'Clump.__class__ =',Clump.__class__
   # print dir(Clump)
      
   print '\n** End of standalone test of: Clump.py:\n' 

#=====================================================================================
# Things to be done:
#
# .remove(subset): remove the specified subset of tree nodes
# .append(nodes)/insert(nodes)
# .(de)select(subset): temporarily (de)select a subset of tree nodes
#
# callbacks, executed from .end_of_body()
#   This would solve the daisy-chain problem of non-inclusion
#   i.e. if one wants the next daisy to work only on the last one,
#   and be ignored when the last one is not selected....
#
# make master/slave on entire clump (recurse>1): (slaveof)

#=====================================================================================





