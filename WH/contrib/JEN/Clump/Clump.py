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
      defining characteristics (self._treequals etc)
      """

      # These need a little more thought:
      kwargs.setdefault('select', None)                 # <------- !!?
      trace = kwargs.get('trace',False)                 # <------- !!?
      self._slavemaster = kwargs.get('master',None)   # <------- !!?

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

      # The data description controls the behaviour of Clump-functions
      # that perform 'generic' operations (like add_noise().
      # It is passed from Clump to Clump, and modified when appropriate.
      self._datadesc = dict(complex=False, dims=[1])

      #......................................................................


      # A Clump object maintains a history of itself:
      self._history = None                  # see self.history()

      # Nodes without parents (e.g. visualisation) are collected on the way:
      self._orphans = []                    # see self.rootnode()

      # See self.unique_nodestub()
      self._stubtree = None

      # See .on_entry(), .execute_body(), .end_of_body(), .on_exit() 
      self._ctrl = None

      # A Clump objects operates in successive named/counted 'stages'.
      # This is used to generate nodenames: See self.unique_nodestub().
      # Some of this information is passed from clump to clump.
      self._stage = dict(name=None, count=-1, ops=-1, ncopy=0, isubmenu=-1) 

      #......................................................................
      # Transfer definition information from the input Clump (if supplied).
      # This includes self._datadesc and self._treequals etc 
      # Then supply local defaults for some attributes that have not been
      # defined yet (i.e. in the case that there is no input Clump):
      #......................................................................

      self.transfer_clump_definition(clump, trace=False)

      if not isinstance(self._name,str):    # Generate an automatic name, if necessary      
         self._name = self._typename        # e.g. 'Clump'     
         global clump_counter
         clump_counter += 1
         self._name += str(clump_counter)

      if not self._TCM:               
         ident = self._typename+'_'+self._name
         self._TCM = TOM.TDLOptionManager(ident)

      if not self._ns:
         self._ns = NodeScope()      

      #......................................................................
      # Fill self._nodes (the Clump tree nodes) etc.
      #......................................................................

      # The list of actual Clump tree nodes, and their qualifiers:
      # (if self._composed, both lists have length one.)
      if self._input_clump:
         self.transfer_clump_nodes()
      else:
         self._nodes = []                       # nodes (separate or composed)
         self._nodequals = self._treequals      # node qualifiers
         self._composed = False                 # see .compose() and .decompose()

      # The tree nodes may be 'composed' into a single tensor node.
      # In that case, the following node qualifier will be used.
      self._tensor_qual = 'tensor'+str(self.size())

      # Execute the main function of the Clump object.
      # This function is re-implemented in derived Clump classes.
      self._object_is_selected = True           # default: selected (..?)     
      self.initexec(**kwargs)

      # Some final checks:
      if len(self._nodes)==0:
         s = '\n** No tree nodes in: '+self.oneliner(),'\n'
         raise ValueError,s

      # Finished:
      return None

   #--------------------------------------------------------------------------

   def datadesc (self):
      """Return self._datadesc, after calculating all the derived values,
      and checking for consistency. 
      """
      dd = self._datadesc
      if isinstance(dd['dims'],int):               # tensor dimensions
         dd['dims'] = [dd['dims']]

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

      # Always return the self-consistent datadesc:
      return self._datadesc

   #==========================================================================
   # Functions that deal with the input Clump (if any)
   #==========================================================================

   def transfer_clump_definition(self, clump, trace=False):
      """Transfer the clump definition information from the given Clump.
      Most attributes are transferred ONLY if not yet defined
      Some attributes (like self._treequals) are transferred always(!)
      """
      # trace = True
      if trace:
         print '\n** transfer_clump_definition(): clump=',type(clump)

      self._input_clump = clump

      # if isinstance(clump,type(self)):    # too restrictive! type==Clump would be OK...
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
            # self._TCM.current_menu_key(trace=trace)
            # self._TCM.current_menu_level(trace=trace)

         # Some attributes are transferred always(!):
         self._datadesc = clump.datadesc()                      # note the function!
         self._treequals = clump._treequals                     # ..include in datadesc?
         self._treelabels = clump._treelabels                   # ..include in datadesc?
         self._stage['count'] = 1+clump._stage['count']         # <--------!!
         self._stage['ops'] = -1                                # reset
         self._stage['name'] = clump._stage['name']             # <--------!!
         clump._stage['ncopy'] += 1
         self._stage['ncopy'] = clump._stage['ncopy']           # <--------!!
      return True

   #--------------------------------------------------------------------------

   def transfer_clump_nodes(self):
      """Transfer the clump nodes (etc) from the given input Clump.
      Called from self.__init__() only.
      """
      clump = self._input_clump                 # convenience
      if not clump:
         s = '** Clump: An input Clump should have been provided!'
         raise ValueError,s

      # Make sure that self._nodes is a COPY of clump._nodes
      # (so clump._nodes is not modified when self._nodes is).
      self._nodes = []
      for i,node in enumerate(clump._nodes):
         self._nodes.append(node)

      self._composed = clump._composed
      self._nodequals = clump._nodequals
      self._stubtree = clump._stubtree
      self._orphans = clump._orphans
      
      self._history = clump.history()          # note the use of the function
      self.history('The end of the pre-history copied from: '+clump.oneliner())
      self.history('....................................')
      return True

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
      kwargs['select'] = False
      ctrl = self.on_entry(self.initexec, **kwargs)
      self._object_is_selected = False                          # <---- !!
      if self.execute_body():
         # NB: .execute_body() makes the menu, controlled by kwargs['select']
         self._object_is_selected = True
         if True:
            # As an illustration, add some operation:
            self.apply_unops(unops='Cos', select=False)
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
      i.e. it has the same self._nodequals (NOT self._treequals!)
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
            raise ValueError,s
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
         new.apply_binop(binop=binop, rhs=clump, **kwargs)    # <-----!!
         self._orphans.extend(new._orphans)                   # <---- !!
         self.end_of_body(ctrl)

      return self.on_exit(ctrl, result=new)


   #=========================================================================
   # copy()
   #=========================================================================

   def copy (self, **kwargs):
      """
      Return a new instance of this class, with the same size, treequals, ns and TCM.
      If no name is specified, derive a new name by enclosing self._name in brackets.
      The nodes are copied, possibly after applying one or more unary operations
      (unops) on them.
      NB: It does NOT matter whether the clump is 'composed' (i.e. a single tensor node)
      """
      name = kwargs.get('name',None)
      unops = kwargs.get('unops',None)
      if not isinstance('name',str):
         name = 'copy('+self._name+')'

      # Create a new Clump of the same (possibly derived) type:
      new = self.newinstance(**kwargs)
      if unops:
         new.apply_unops(unops=unops)
      return new


   #==========================================================================
   # Various text display functions:
   #==========================================================================

   def oneliner (self):
      ss = self._typename+': '
      ss += ' '+str(self._name)
      if not self._qual==None:
         ss += ' qual='+str(self._qual)
      ss += '  size='+str(self.size())
      # ss += '  treequals=['+str(self._treequals[0])+'..'+str(self._treequals[-1])+']'
      if self._slavemaster:
         ss += '  slaved'
      if self._composed:
         ss += '  (composed: '+self._tensor_qual+')'
      # ss += ' stage'+str(self._stage['count'])+':'+str(self._stage['name'])
      # ss += ' (copied:'+str(self._stage['ncopy'])+')'
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

      if self._input_clump:
         ss += '\n > self._input_clump: '+str(self._input_clump.oneliner())
      else:
         ss += '\n > self._input_clump = '+str(self._input_clump)
      #.....................................................

      ss += '\n * Generic (baseclass Clump):'
      ss += '\n * self._object_is_selected: '+str(self._object_is_selected)    
      ss += '\n * self._name = '+str(self._name)
      ss += '\n * self._qual = '+str(self._qual)
      ss += '\n * self._kwqual = '+str(self._kwqual)

      ss += '\n * self._stage = '+str(self._stage)
      ss += '\n * self._datadesc = '+str(self.datadesc())

      nmax = 20
      qq = self._treequals
      ss += '\n * self._treequals(n='+str(len(qq))+','+str(len(self._treelabels))+'): '
      if len(qq)<=nmax:
         ss += str(qq)
      else:
         ss += str(qq[:nmax])+'...'+str(qq[-1])
      #.....................................................

      ss += '\n * self._nodes (.len()='+str(self.len())+', .size()='+str(self.size())+'):'
      n = len(self._nodes)
      if full:
         nmax = 2
         for i in range(min(nmax,n)):
            ss += '\n   - '+str(self._nodes[i])
         if n>nmax:
            if n>nmax+1:
               ss += '\n       ...'
            ss += '\n   - '+str(self._nodes[-1])
      else:
         ss += '\n   - node[0] = '+str(self._nodes[0])
         ss += '\n   - node[-1]= '+str(self._nodes[-1])
                                       
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
      ss += '\n * self._slavemaster = '+str(self._slavemaster)
      #.....................................................

      ss += '\n * self._ctrl: '+str(self._ctrl)
      ss += self.history(format=True, prefix='   | ')
      ss += self.show_specific()
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
      ss += '\n + aa'
      ss += '\n + bb'
      return ss

   #-------------------------------------------------------------------------

   def show_tree (self, index=-1, full=True):
      """Show the specified (index) subtree.
      """
      node = self._nodes[index]
      print EN.format_tree(node, full=full)
      return True

   #-------------------------------------------------------------------------

   def history (self, append=None,
                show_node=False,
                prefix='', format=False, 
                clear=False, show=False, trace=False):
      """Interact with the object history (a list of strings).
      """
      # trace = True
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
         s += str(append)
         self._history.append(s)
         if trace:
            print '   >> .history(append): ',self._history[-1]
      elif show_node:
         # self._history.append(' --   (append=None) ')
         # self.history('(append=None)')
         self.history('last Clump tree node:')

      # Append the current node to the last line/item: 
      if show_node:
         ilast = self.len()-1
         s = '   -> '+str(self._nodes[ilast])
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


   #=========================================================================
   # Some general helper functions
   #=========================================================================

   def len(self):
      """Return the number of nodes in the Clump (=1 if a tensor)
      """
      return len(self._nodes)

   #--------------------------------------------------------------------------

   def size(self):
      """Return the number of trees in the Clump (even if in a tensor)
      """
      return len(self._treequals)

   #--------------------------------------------------------------------------
   #--------------------------------------------------------------------------

   def __getitem__(self, index):
      """Get the specified (index) node.
      """
      return self._nodes[index]

   #--------------------------------------------------------------------------

   def __str__(self):
      """Print conversion. Return the object oneliner().
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
      select = kwargs.get('select',None)
      fixture = kwargs.get('fixture',False)
      ctrl = dict(funcname=str(func.func_name),
                  submenu=None,
                  trace=trace)

      # The kwargs information is used for option overrides in
      # the functions .add_option() and .execute_body()
      self._kwargs = kwargs                          # temporary
      self._override_keys = []
      self._override = dict()

      # Make the menu for the calling function:
      if isinstance(select,bool):
         self._stage['isubmenu'] += 1                # increment
         self._stage['count'] += 1                   # increment
         self._stage['ops'] = -1                     # reset
         fname = ctrl['funcname']                    # convenience
         name = fname
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
         # help + = '  (clump: '+self._name+')'        # ..?
         ctrl['submenu'] = self._TCM.start_of_submenu(name,
                                                      prompt=prompt,
                                                      help=help,
                                                      default=select,
                                                      slaveof=self._slavemaster,
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

   def execute_body(self, always=False):
      """To be called at the start of the 'body' of a Clump stage-method,
      i.e. AFTER any self._TCM menu and option definitions.
      Its (mandatory!) counterpart is self.end_of_body(ctrl)
      It uses the record self._ctrl, defined in .on_entr()
      """
      self.check_for_overrides()
      execute = True
      if isinstance(self._ctrl['submenu'],str):
         execute = self._TCM.submenu_is_selected(trace=False)
      if always:                        
         execute = True                              # override (e.g. leaf nodes)
      if self._ctrl['trace']:
         print '** .execute_body(always=',always,'): funcname=',self._ctrl['funcname'],' execute=',execute
      if execute:
         self._stage['count'] += 1                     # increment
         self._stage['ops'] = -1                       # reset
         self._stage['name'] = self._ctrl['funcname']
         s = '{@'+str(self._stage['count'])
         s += ':'+str(self._stage['name'])+'}:  '
         s += self._ctrl['funcname']+'()'
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
      trace = True
      override = self._override.has_key(relkey)
      if override:
         value = self._TCM.getopt(relkey, self._ctrl['submenu'],
                                  override=self._override[relkey])
      else:
         value = self._TCM.getopt(relkey, self._ctrl['submenu'])

      if trace or self._ctrl['trace']:
         s = '.getopt('+str(relkey)+') -> '+str(type(value))+' '+str(value)
         if override:
            s += ' (overridden by kwarg)'
         print s
         self.history(s)
      return value

   #--------------------------------------------------------------------------

   def end_of_body(self, ctrl):
      """
      To be called at the end of the body of a Clump stage-method.
      Counterpart of .execute_body()
      """
      self.history(show_node=True, trace=ctrl['trace'])
      if ctrl['trace']:
         print '** .end_of_body(ctrl): funcname=',ctrl['funcname']
      return True

   #..........................................................................

   def on_exit(self, ctrl, result=None):
      """
      To be called at the end of a Clump stage-method.
      Counterpart of ctrl = self.on_entry(func, **kwargs)
      Syntax: return self.on_exit(ctrl, result[=None])
      """
      if ctrl['submenu']:
         self._TCM.end_of_submenu()
      if ctrl['trace']:
         print '** .on_exit(ctrl, result=',result,'): funcname=',ctrl['funcname'],'\n'
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
      at = '@'+str(self._stage['count'])
      at += '-'+str(self._stage['ops'])
      # qual.insert(0, at)                   # NB: This pollutes Parm names etc...
      if not self._qual==None:
         if isinstance(self._qual,list):
            qual.extend(self._qual)
         else:
            qual.append(self._qual)

      # Make the unique nodestub:
      # NB: Note that kwquals are not yet supported here.......!!
      stub = EN.unique_stub(self._ns, self._name, *qual)

      # Initialize the stub (uniqueness criterion!):
      if not self._stubtree:                       # the first one
         node = stub << Meq.Constant(-0.123456789)
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
            raise ValueError,s
      elif isinstance(subset,int):
         ii = range(min(subset,self.size()))      # ..../??
      elif not isinstance(subset,(list,tuple)):
         raise ValueError,s
      else:
         ii = list(subset)

      # Check the list elements:
      imax = self.size()
      for i in ii:
         if not isinstance(i,int):
            raise ValueError,s
         elif i<0 or i>imax:
            raise ValueError,s

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
         nodes.append(self._nodes[i])
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
      wgt = kwargs.get('weights',None)                 # for WSum,WMean

      stub = self.unique_nodestub(combine)
      qual = 'bundle'+str(len(self._nodes))
      if not self._composed:                              
         if wgt:
            node = stub(qual) << getattr(Meq,combine)(children=self._nodes,
                                                      weights=wgt)
         else:
            node = stub(qual) << getattr(Meq,combine)(*self._nodes)
      elif combine=='Composer':
         node = stub('tensor') << Meq.Identity(self._nodes[0]) 
      else:
         s = hist+' Clump is in composed state **'
         raise ValueError,s
      
      hist = '.bundle('+str(combine)+'): '
      self.history(hist, trace=kwargs.get('trace',False))
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
      if not self._composed:               # ONLY if in 'decomposed' state
         stub = self.unique_nodestub(self._tensor_qual)
         node = stub('composed') << Meq.Composer(*self._nodes)
         self._nodes = [node]              # a list of a single node
         self._composed = True             # set the switch
         self._nodequals = [self._tensor_qual]
         self.history('.compose()', trace=kwargs.get('trace',False))
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
      if self._composed:                   # ONLY if in 'composed' state
         tensor = self._nodes[0]
         nodes = []
         stub = self.unique_nodestub('decomposed')
         for index,qual in enumerate(self._treequals):
            node = stub(qual) << Meq.Selector(tensor, index=index)
            nodes.append(node)
         self._nodes = nodes
         self._composed = False            # set the switch
         self._nodequals = self._treequals
         self.history('.decompose()', trace=kwargs.get('trace',False))
      return self._nodes

   #-------------------------------------------------------------------------

   #-------------------------------------------------------------------------

   #-------------------------------------------------------------------------

   #============================================================================
   # Solver support functions:
   #=========================================================================

   def solvable_parms (self, trace=False):
      """
      Place-holder function, expected in all Clump classes.
      This version always return an emply list.
      See also ParmClump.py
      """
      return []

   #--------------------------------------------------------------------------

   def insert_reqseqs (self, node, trace=False):
      """ Insert a ReqSeq (in every tree!) that issues a request first to
      the given node (e.g. a solver node), and then to the current tree node.
      NB: The fact that there is a ReqSeq in every tree seems wasteful, but
      it synchronises the processing in the different trees of the Clump....
      """
      if is_node(node):
         stub = self.unique_nodestub('reqseq')
         for i,qual in enumerate(self._nodequals):
            self._nodes[i] = stub(qual) << Meq.ReqSeq(node, self[i],
                                                      result_index=1,
                                                      cache_num_active_parents=1)
         self.history('.insert_reqseqs('+str(node)+')', show_node=True)
      return True

   #=========================================================================
   # Apply arbitrary unary (unops) or binary (binops) operaions to the nodes:
   #=========================================================================

   def apply_unops (self, **kwargs):
      """
      Apply one or more unary operation(s) (e.g. MeqCos) on its nodes.
      """
      if not kwargs.has_key('unops'):
         pass                               # error?
      unops = kwargs['unops']
      prompt = '.apply_unops('+str(unops)+')'
      help = None
      ctrl = self.on_entry(self.apply_unops, prompt, help, **kwargs)

      if self.execute_body():
         # Make sure that unops is a list:
         if isinstance(unops,tuple):
            unops = list(unops)
         elif isinstance(unops,str):
            unops = [unops]

         # Apply in order of specification:
         for unop in unops:
            stub = self.unique_nodestub(unop+'()')
            for i,qual in enumerate(self._nodequals):
               self._nodes[i] = stub(qual) << getattr(Meq,unop)(self._nodes[i])
         self.end_of_body(ctrl)

      return self.on_exit(ctrl)

   #-------------------------------------------------------------------------

   def apply_binop (self, **kwargs):
      """Apply a binary operation (binop, e.g. 'Add') between its nodes
      and the given right-hand-side (rhs). The latter may be various
      things: a Clump, a node, a number etc.
      """
      binop = kwargs['binop']
      rhs = kwargs['rhs']                           # 'other'?
      prompt = '.apply_binop('+str(binop)+')'
      if isinstance(rhs,(int,float,complex)):       # rhs is a number
         help = 'rhs = constant = '+str(rhs)
      elif is_node(rhs):                            # rhs is a node
         help = 'rhs = node: '+str(rhs.name)
      elif isinstance(rhs,type(self)):              # rhs is a Clump object
         help = 'rhs = '+rhs.oneliner()
      ctrl = self.on_entry(self.apply_binop, prompt, help, **kwargs)

      if self.execute_body():
         if isinstance(rhs,(int,float,complex)):    # rhs is a number
            stub = self.unique_nodestub('constant')
            rhs = stub('='+str(rhs)) << Meq.Constant(rhs) # convert to MeqConstant
         
         if is_node(rhs):                           # rhs is a node
            stub = self.unique_nodestub(binop, 'samenode')
            for i,qual in enumerate(self._nodequals):
               self._nodes[i] = stub(qual) << getattr(Meq,binop)(self._nodes[i],rhs)

         elif isinstance(rhs,type(self)):           # rhs is a Clump object
            if self.commensurate(rhs, severe=True):
               stub = self.unique_nodestub(binop, rhs._typename)
               for i,qual in enumerate(self._nodequals):
                  self._nodes[i] = stub(qual) << getattr(Meq,binop)(self._nodes[i],
                                                                    rhs._nodes[i])
         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl)

   #-------------------------------------------------------------------------

   def add_noise (self, **kwargs):
      """Add Gaussian noise with the specified stddev.
      To be re-implemented in derived classes like Matrix22Clump etc.
      """
      # This is an example of an (as yet unexplored) feature: 
      # NB: Should we allow for the external specification of stddev,
      # which would then avoid the menu (kwargs['select']=None),
      # but execute always (with the specified stddev)
      # stddev = kwargs.get('stddev', None) 

      prompt = '.add_noise()'
      help = 'Add Gaussian noise'
      ctrl = self.on_entry(self.add_noise, prompt, help, **kwargs)

      self.add_option('stddev', [0.001,0.01,0.1,1.0,10.0,0.0])

      if self.execute_body():
         stddev = self.getopt('stddev')
         if stddev>0.0:
            stub = self.unique_nodestub('add_noise','stddev='+str(stddev))
            for i,qual in enumerate(self._nodequals):
               noise = stub('noise')(qual) << Meq.GaussNoise(stddev=stddev)
               self._nodes[i] = stub(qual) << Meq.Add(self._nodes[i],noise)
         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl)

   #-------------------------------------------------------------------------

   def scatter (self, **kwargs):
      """Add different random (stddev) constants to the tree nodes.
      If stddev is complex, the scatter constants are complex too.
      """
      prompt = '.scatter()'
      help = 'Add different (stddev) constants to the tree nodes'
      ctrl = self.on_entry(self.scatter, prompt, help, **kwargs)

      self.add_option('stddev_real', [0.1,1.0,10.0,0.0])
      self.add_option('stddev_imag', [0.0,0.1,1.0,10.0])

      if self.execute_body():
         real = max(0.0,self.getopt('stddev_real'))
         imag = max(0.0,self.getopt('stddev_imag'))
         if real>0.0 or imag>0.0:
            if imag>0.0:
               stddev = complex(real,imag)
               stub = self.unique_nodestub('scatter','stddev='+str(stddev))
            else:
               stub = self.unique_nodestub('scatter','stddev='+str(real))
            for i,qual in enumerate(self._nodequals):
               rscat = random.gauss(0.0, real)
               if imag>0.0:
                  iscat = random.gauss(0.0, imag)
                  scat = EF.format_value(complex(rscat,iscat), nsig=2)
                  scat = stub('scat='+scat)(qual) << Meq.ToComplex(rscat,iscat)
               else:
                  scat = EF.format_value(rscat, nsig=2)
                  scat = stub('scat='+scat)(qual) << Meq.Constant(rscat)
               self._nodes[i] = stub(qual) << Meq.Add(self._nodes[i],scat)
         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl)


   #=========================================================================
   # Visualization:
   #=========================================================================

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

      if self.execute_body():
         bundle = self.bundle()
         bundle.initrec().plot_label = self._treelabels     # list of strings!
         self._orphans.append(bundle)
         JEN_bookmarks.create(bundle,
                              name=bookpage, folder=folder,
                              viewer='Collections Plotter')
         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl)

   #---------------------------------------------------------------------

   def plot_node_bundle (self, **kwargs):
      """Make a plot for the bundle (Composer) of its nodes, and make a bookmark.
      """
      bookpage = kwargs.get('bookpage', None)
      folder = kwargs.get('folder', None)

      prompt = '.plot_node_bundle()'
      help = 'plot the bundle (MeqComposer) of all tree nodes'
      ctrl = self.on_entry(self.plot_node_bundle, prompt, help, **kwargs)

      if self.execute_body():
         bundle = self.bundle()
         self._orphans.append(bundle)
         JEN_bookmarks.create(bundle, name=bookpage, folder=folder)
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

      if self.execute_body():
         if not isinstance(bookpage,str):
            bookpage = 'Clump['+str(index)+']'
         nodes = []
         for node in self._nodes:
            nodes.append(node)
         if not isinstance(folder,str):
            folder = self._name
         JEN_bookmarks.create(nodes,
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

      if self.execute_body():
         if not isinstance(bookpage,str):
            nodequal = self._nodequals[index]
            bookpage = 'Family['+str(nodequal)+']'
         if not isinstance(folder,str):
            folder = self._name
         JEN_bookmarks.create(self._nodes[index],
                              recurse=recurse,
                              name=bookpage, folder=folder,
                              viewer=viewer)
         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl)







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
      kwargs['select'] = True
      kwargs['fixture'] = True

      # The 'size' of the Clump (i.e. the number of its trees, which
      # is NOT necessarily the number of nodes, see self._composed)
      # is defined by self._treequals, the list of tree qualifiers.
      # If an input Clump is supplied (clump), the treequals list is
      # copied from it. But if not, it may be specified by means of
      # a keyword kwargs[treequals].
      
      # kwargs.setdefault('treequals', None)
      tqs = kwargs.get('treequals',None)  
      if tqs==None:                      # treequals not specified
         self._treequals = range(3)      # for testing
      elif isinstance(tqs,str):          # string -> list of chars (..?)
         self._treequals = list(tqs)  
      elif isinstance(tqs,tuple):        # tuple -> list
         self._treequals = list(tqs)
      elif not isinstance(tqs,list):     # assume str or numeric?
         self._tqs = [tqs]               # make a list of one
      else:                              # tqs is a list
         self._treequals = tqs           # just copy the list

      # Make a list of (string) tree labels from treequals:
      # (e.g. inspector-labels give require this).
      self._treelabels = []
      for i,qual in enumerate(self._treequals):
         self._treelabels.append(str(qual))
         
      # The following executes the function self.initexec(**kwargs),
      # which is re-implemented below.
      Clump.__init__(self, clump=clump, **kwargs)
      return None

   #-------------------------------------------------------------------------
   # Specific re-implementations of some Clump functions.
   #-------------------------------------------------------------------------

   def show_specific(self):
      """
      Format the specific (non-generic) contents of the derived class.
      Re-implementation of function in baseclass Clump.
      """
      ss = '\n + Specific (derived class '+str(self._typename)+'):'
      return ss

   #-------------------------------------------------------------------------

   def newinstance(self, **kwargs):
      """Reimplementation of placeholder function in base-class Clump.
      Make a new instance of this derived class (templateClump).
      NB: For a LeafClump, this might not be very useful....
      """
      return LeafClump(clump=self, **kwargs)

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
      help = 'make leaf nodes for: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, help=help, **kwargs)

      self._datadesc['complex'] = kwargs.get('complex',False)
      self._datadesc['dims'] = kwargs.get('dims',1)
      dd = self.datadesc()

      # Execute always (always=True), to ensure that the leaf Clump has nodes:
      if self.execute_body(always=True):              
         self._nodes = []
         stub = self.unique_nodestub('const')
         for i,qual in enumerate(self._nodequals):
            cc = []
            for k,elem in enumerate(dd['elems']):
               if dd['complex']:
                  v = complex(k+i,i/10.)
               else:
                  v = float(k+i)
               node = stub(c=v)(qual)(elem) << Meq.Constant(v)
               cc.append(node)
            node = stub(nelem=dd['nelem'])(qual) << Meq.Composer(*cc)
            self._nodes.append(node)
         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl)









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
      ## clump.add_noise(stddev=0.0, trace=True)
      # clump.add_noise(select=True, trace=True)
      clump.scatter(select=True, trace=True)
      # clump.apply_unops(unops='Cos', select=False, trace=True)
      # clump.apply_unops(unops='Sin', select=True, trace=True)
      # clump.apply_unops(unops='Exp', trace=True)
      # clump.apply_binop(binop='Add', rhs=2.3, select=True, trace=True)
      # clump = Clump(clump, select=True).daisy_chain()
      # clump = Clump(clump, select=True).daisy_chain()
      # clump.inspector()
      # clump.plot_node_results()
      # clump.plot_node_family()
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
      clump.show('creation', full=True)

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

   if 0:
      new = clump.copy(unops='Cos')
      new.show('new', full=True)

   if 0:
      unops = 'Cos'
      # unops = ['Cos','Cos','Cos']
      unops = ['Cos','Sin']
      clump.apply_unops(unops=unops, trace=True)    
      # clump.apply_unops()                       # error
      # clump.apply_unops(unops=unops, trace=True)
      # clump.apply_unops(unops=unops, select=True, trace=True)

   if 0:
      rhs = math.pi
      # rhs = ns.rhs << Meq.Constant(2.3)
      # rhs = Clump('RHS', clump=clump)
      clump.apply_binop(binop='Add', rhs=rhs, trace=True)

   if 0:
      treequals = range(5)
      treequals = ['a','b','c']
      clump3 = LeafClump(treequals=treequals)
      clump.commensurate(clump3, severe=False, trace=True)
      clump3.show('.commensurate()')

   if 0:
      print clump.bundle()
      clump.show('.bundle()')

   if 1:
      node = ns.dummysolver << Meq.Constant(67)
      clump.insert_reqseqs(node, trace=True)
      clump.show('.insert_reqseqs()')

   if 0:
      clump.add_noise(trace=True)
      # clump.add_noise(stddev=0.1, trace=True)   <---!
      clump.show('.add_noise()')

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





