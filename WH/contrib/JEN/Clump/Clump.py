"""
Clump.py: Base-class for an entire zoo of derived classes that
represent 'clumps' of trees, i.e. sets of similar nodes.
Examples are ParmClump, JonesClump and VisClump.
"""

# file: ../JEN/Clump/Clump.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 25 oct 2008: creation
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
# from math import *          # support cos() etc
# import numpy                # support numpy.cos() etc

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

      kwargs.setdefault('name', None)
      kwargs.setdefault('qual', None)
      kwargs.setdefault('kwqual', dict())
      kwargs.setdefault('treequals', None)
      kwargs.setdefault('ns', None)
      kwargs.setdefault('TCM', None)
      kwargs.setdefault('select', None)
      kwargs.setdefault('trace', False)

      self._kwargs = kwargs
      trace = kwargs['trace']

      # Make a short version of the type name (e.g. Clump)
      self._typename = str(type(self)).split('.')[1].split("'")[0]

      # The Clump node names are derived from name and qualifier:
      self._name = kwargs['name']       
      self._qual = kwargs['qual']  
      self._kwqual = kwargs['kwqual']

      # The 'size' of the Clump (i.e. the number of its trees)
      # is defined by the list of tree qualifiers:
      # NB: This is NOT necessarily the number of nodes.
      tqs = kwargs['treequals']
      if tqs==None:                      # not specified
         self._treequals = None    
      elif isinstance(tqs,tuple):        # tuple -> list
         self._treequals = list(tqs)
      elif not isinstance(tqs,list):     # assume str or numeric?
         self._tqs = [tqs]               # make a list of one
      else:                              # tqs is a list
         self._treequals = tqs           # just copy the list

      # Organising principles:
      self._ns = kwargs['ns']
      self._TCM = kwargs['TCM']

      #......................................................................
      # Make sure of the Clump node definition attributes:
      #......................................................................

      # Transfer information from the input Clump (if any).
      self.transfer_clump_definition(clump, trace=trace)

      # In the case that there is no input Clump, supply local defaults
      # for some attributes that have not been defined yet.

      if not isinstance(self._name,str):       
         self._name = self._typename           # e.g. 'Clump'    
         global clump_counter
         clump_counter += 1
         self._name += str(clump_counter)      # automatic name

      if not ns:
         self._ns = NodeScope()      

      if not self._TCM:               
         self._TCM = TOM.TDLOptionManager(self._name)

      if self._treequals==None:
         self._treequals = range(3)            # for testing
      #......................................................................


      # Each Clump object has a special submenu, which is
      # started in .start_of_object_submenu(), which may be called
      # from .init() if that function defines any options,
      # or from another function (which one?)
      # In any case, any function that calls .start_of_submenu()
      # must end with: self.end_of_object_submenu()
      self._object_submenu = None   
      self._slavemaster = None
      if isinstance(kwargs,dict):
         if kwargs.has_key('master'):
            self._slavemaster = kwargs['master']

      # A Clump object maintains a history of itself:
      self._history = None                  # see self.history()

      # Nodes without parents (e.g. visualisation) are collected on the way:
      self._orphans = []                    # see self.rootnode()

      # See self.unique_nodestub()
      self._stubtree = None

      # See .on_entry(), .execute_body(), .end_of_body(), .on_exit() 
      self._ctrl = None

      # A Clump objects operates in 'stages'. See self.unique_nodestub().
      self._stagename = None                # name of the current stage 
      self._stagecounter = -1               # number of the current stage
      self._submenucounter = -1

      #......................................................................
      # Make sure of the Clump nodes themselves:
      #......................................................................

      # The list of actual Clump tree nodes, and their qualifiers:
      # (if self._composed, both lists have length one.)
      self._nodequals = self._treequals
      self._nodes = []

      # The nodes may be composed into a single tensor node.
      # In that case, the following qualifier will be used.
      # The list self._nodequals always has the same length as self._nodes.
      self._tensor_qual = 'tensor'+str(len(self._treequals))
      self._composed = False            # see .compose() and .decompose()

      # Finally: Initialize the Clump with suitable nodes
      # This function is re-implemented in derived classes 
      self.initial_nodes(**kwargs)
      #......................................................................

      return None


   #--------------------------------------------------------------------------
   # Functions that transfer information from an input Clump:
   #--------------------------------------------------------------------------

   def transfer_clump_definition(self, clump, trace=False):
      """Transfer the clump definition information from the given Clump.
      Most attributes are transferred ONLY if not yet defined
      (e.g. by means of the input **kwargs (see .__init__())
      Some attributes (like self._treequals) are transferred always(!)
      """
      self._input_clump = clump
      if isinstance(clump,type(self)):
         # Most attributes are transferred ONLY if not yet defined
         # (e.g. by means of the input **kwargs (see .__init__())
         if self._ns==None:
            self._ns = clump._ns
         if self._TCM==None:
            self._TCM = clump._TCM
         if not isinstance(self._name,str):
            self._name = '('+clump._name+')'
         if self._qual==None:
            self._qual = clump._qual
         if self._kwqual==None:
            self._kwqual = clump._kwqual
         # Some attributes are transferred always(!):
         self._treequals = clump._treequals
      return True

   #--------------------------------------------------------------------------

   def transfer_clump_nodes(self, trace=False):
      """Transfer the clump nodes (etc) from the given Clump.
      Called from self.initial_nodes() in most defived classes.
      """
      clump = self._input_clump
      self._composed = clump._composed
      self._nodes = clump._nodes
      self._nodequals = clump._nodequals
      self._stubtree = clump._stubtree
      self._orphans = clump._orphans
      return True

   #--------------------------------------------------------------------------
   # Initial Clump nodes:
   #--------------------------------------------------------------------------

   def initial_nodes (self, **kwargs):
      """Fill self._nodes with initial nodes.
      Called from __init__() only
      Place-holder: To be re-implemented for derived 'leaf' Clump classes.
      """
      # If an input Clump has been defined, use its nodes,
      # unless it is explicitly specified that this object
      # is a 'leaf' Clump (used for testing only)
      kwargs.setdefault('leaf', False)
      if self._input_clump:
         if not kwargs['leaf']:
            return self.transfer_clump_nodes()
      # elif not kwargs['leaf']:
      #    s = '** An input Clump should be provided!'
      #    raise ValueError,s

      # Otherwise, just fill it with simple Constant nodes:
      self._nodes = []
      stub = self.unique_nodestub()
      for i,qual in enumerate(self._nodequals):
         node = stub(qual) << Meq.Constant(i)
         self._nodes.append(node)

      return True


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
         
   def compare (self, clump, binop='Subtract', **kwargs):
      """
      Compare (Subtract, Divide) its nodes with the corresponding
      nodes of another Clump. Return a new Clump object with the result.
      """
      prompt = '.compare('+binop+')'
      help = clump.oneliner()
      ctrl = self.on_entry(self.compare, prompt, help, **kwargs)

      new = None
      if self.execute_body():
         new = self.copy(binop)                         # <-----!!
         new.apply_binop(binop, rhs=clump, **kwargs)    # <-----!!
         self._orphans.extend(new._orphans)             # <---- !!
         self.end_of_body(ctrl)

      return self.on_exit(ctrl, result=new)


   #=========================================================================
   # Clump connection operations (very important for building complex structures)
   # Obviously, all this requires some thought....
   # def insert/append/chain(self, other)
   #=========================================================================

   def link (self, name=None, qual=None, unops=None, trace=False):
      """
      Return a new instance of this class, with the same size, treequals, ns and TCM.
      If no name is specified, derive a new name by enclosing self._name in brackets.
      The nodes are copied, possibly after applying one or more unary operations
      (unops) on them.
      NB: It does NOT matter whether the clump is 'composed' (i.e. a single tensor node)
      """
      if not isinstance(name, str):
         name = 'link('+self._name+')'

      # Create a new Clump of the same (possibly derived) type:
      new = self.newinstance(name=name, qual=qual, init=False)

      # Copy the nodes:
      new._nodes = []
      stub = new.unique_nodestub()
      for i,qual in enumerate(self._nodequals):
         node = self._nodes[i]
         new._nodes.append(node)

      new.history('link(unop='+str(unops)+')', trace=trace)
      new.history('| copied from: '+self.oneliner(), trace=trace)
      if unops:
         # Optionally, apply one or more unary operations
         new.apply_unops(unops=unops, trace=trace)
      return new

   #-------------------------------------------------------------------------

   def newinstance(self, name=None, qual=None, init=False):
      """Make a new instance of this class. Called by .link().
      This function should be re-implemented in derived classes.
      """
      return Clump(name=name, qual=qual, clump=self, init=init)

   #-------------------------------------------------------------------------

   def deepcopy (self, name=None, qual=None, trace=False):
      """Version of .link(), in which an Identity operation is applied
      to the nodes of the new object. This may not be very useful....?
      """
      return self.link (name=name, qual=qual, unops='Identity', trace=trace)


   #==========================================================================
   # Various text display functions:
   #==========================================================================

   def oneliner (self):
      ss = self._typename+': '
      ss += ' '+str(self._name)
      if not self._qual==None:
         ss += ' qual='+str(self._qual)
      ss += '  size='+str(self.size())
      ss += '  treequals=['+str(self._treequals[0])+'..'+str(self._treequals[-1])+']'
      if self._slavemaster:
         ss += '  slaved'
      if self._composed:
         ss += '  (composed: '+self._tensor_qual+')'
      ss += ' stage'+str(self._stagecounter)+':'+str(self._stagename)
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
      ss += '\n > self._kwargs (input): '+str(self._kwargs.keys())
      if full:
         for key in self._kwargs.keys():
            ss += '\n   - '+key+' = '+str(self._kwargs[key])
      ss += '\n > self._clump (input): '+str(self._clump)
      #.....................................................

      ss += '\n * Generic (baseclass Clump):'
      ss += '\n * self._name: '+str(self._name)
      ss += '\n * self._qual: '+str(self._qual)
      ss += '\n * self._kwqual: '+str(self._kwqual)
      nmax = 20
      qq = self._treequals
      ss += '\n * self._treequals(n='+str(len(qq))+'): '
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
      ss += '\n * self._orphans (n='+str(len(self._orphans))+'):'
      for i,node in enumerate(self._orphans):
         ss += '\n   - '+str(node)
      #.....................................................

      ss += '\n * self._ns: '+str(self._ns)
      if self._TCM:
         ss += '\n * self._TCM: '+str(self._TCM.oneliner())
      else:
         ss += '\n * self._TCM = '+str(self._TCM)
      ss += '\n * self._object_submenu = '+str(self._object_submenu)
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

   def history (self, append=None, show_node=False,
                prefix='', format=False, 
                clear=False, show=False, trace=False):
      """Interact with the object history (a list of strings).
      """
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
         self._history.append(' -- '+str(append))
         if trace:
            print '   >> .history(append): ',self._history[-1]

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

      kwargs.setdefault('trace', False)
      ctrl = dict(funcname=str(func.func_name),
                  submenu=None, trace=kwargs['trace'],
                  kwargs=kwargs)

      if kwargs.has_key('select'):
         self._submenucounter += 1
         name = ctrl['funcname']+'_'+str(self._submenucounter)
         if not isinstance(help,str):
            help = ''
            ignore = ['trace','select']
            for key in kwargs.keys():
               if not key in ignore:
                  help += '_'+str(key)+'='+str(kwargs[key])
         if not isinstance(prompt,str):
            prompt = ctrl['funcname']+'()'
         ctrl['submenu'] = self._TCM.start_of_submenu(name,
                                                      prompt=prompt,
                                                      help=help,
                                                      default=kwargs['select'],
                                                      master=self._slavemaster,
                                                      qual=self._qual)

      # The ctrl record used by other control functions downstream.
      # The opening ones use self._ctrl, but the closing ones have to use
      # the ctrl argument (since self._ctrl may be overwritten by other
      # functions that are called in the function body (AFTER all .getopt() calls!)
      self._ctrl = ctrl
      if self._ctrl['trace']:
         print '\n ** .on_entry(func, **kwargs): \n   ctrl =',ctrl
      return ctrl

   #--------------------------------------------------------------------------

   def execute_body(self):
      """To be called at the start of the 'body' of a Clump stage-method,
      i.e. AFTER any self._TCM menu and option definitions.
      Its (mandatory!) counterpart is self.end_of_body(ctrl)
      It uses the record self._ctrl, defined in .on_entr()
      """
      execute = True
      if isinstance(self._ctrl['submenu'],str):
         execute = self._TCM.submenu_is_selected(trace=False)
      if self._ctrl['trace']:
         print '** .execute_body(): funcname=',self._ctrl['funcname'],' execute=',execute
      if execute:
         self._stagecounter += 1
         self._stagename = self._ctrl['funcname']
         s = '{stage='+str(self._stagecounter)+','+str(self._stagename)+'}:  '
         s += self._ctrl['funcname']+'()'
         self.history(append=s, trace=self._ctrl['trace'])
      return execute

   #..........................................................................

   def getopt (self, name):
      """Get the specified (name) TDL option value.
      This function is ONLY called AFTER self.execute_body()==True.
      It use the record self._ctrl that is defined in .on_entry()
      """
      value = self._TCM.getopt(name, self._ctrl['submenu'])
      if self._ctrl['trace']:
         print '    - .getopt(',name,self._ctrl['submenu'],') -> ',type(value),value
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

   def unique_nodestub (self, qual=None, enclose=None,
                        help=None, trace=False):
      """
      Convenience function to generate a (unique) nodestub.
      The stub is then initialized (which helps the uniqueness determination!)
      and attached to the internal subtree of stub-nodes, which would otherwise
      be orphaned. They are used to carry quickref-help information, which
      can be used in the various bookmark pages.
      """
      name = self._name
      if enclose:                                  # e.g. ['Cos(',')']
         name = self._nodes[0].basename
         name = enclose[0]+name+enclose[1]
      stub = EN.unique_stub(self._ns, name, self._qual, qual)
      if not self._stubtree:                       # the first one
         node = stub << Meq.Constant(-0.123456789)
      else:                                        # subsequent ones
         node = stub << Meq.Identity(self._stubtree)
      # node.initrec().quickref_help = rider.format_html(path=rider.path())
      self._stubtree = node
         
      if trace:
         print '\n** .unique_nodestub(',qual,') ->',str(stub)
      return stub



   #=========================================================================
   # To and from tensor nodes:
   #=========================================================================

   def rootnode (self, name='rootnode', trace=False):
      """Return a single node with the specified name [='rootnode'] which has all
      the internal nodes (self._nodes, self._stubtree and self._orphans)
      as its children. The internal state of the object is not changed.
      """
      nodes = self._nodes                   # the Clump tree nodes
      nodes.append(self._stubtree)          # the tree of stubs
      if len(self._orphans)>0:
         nodes.extend(self._orphans)        # any orphans
      # use MeqComposer? or MeqReqSeq? or stepchildren?
      rootnode = self._ns[name] << Meq.Composer(children=nodes)
      self.history('.rootnode('+str(name)+')', trace=trace)
      return rootnode

   #-------------------------------------------------------------------------

   def bundle (self, name=None, qual=None, combine='Composer', trace=False):
      """Return a single node that bundles the Clump nodes, using the
      specified combining node (default: combine='Composer').
      The internal state of the object is not changed.
      """
      if not isinstance(name,str):
         name = 'bundle_'+str(self._name)
      hist = '.bundle('+str(name)+','+str(qual)+','+str(combine)+'): '

      stub = EN.unique_stub(self._ns, name, self._qual, qual)
      if not self._composed:                              
         node = stub << getattr(Meq,combine)(*self._nodes)
      elif combine=='Composer':
         node = stub << Meq.Identity(self._nodes[0]) 
      else:
         pass        # decompose first....?

      self.history(hist, trace=trace)
      return node

   #-------------------------------------------------------------------------

   def compose (self, replace=True, trace=False):
      """Return a single tensor node, which has all the tree nodes as its children.
      If replace=True (default), make sure that the Clump object is in
      the 'composed' state, i.e. self._nodes contains a single tensor node.
      See also .decompose() and .bundle()
      """
      node = self._nodes[0]
      if not self._composed:               # Only if in 'decomposed' state
         stub = self.unique_nodestub('composed')(self._tensor_qual)
         node = stub << Meq.Composer(*self._nodes)
         if replace:
            self._nodes = [node]              # a list of a single node
            self._composed = True             # set the switch
            self._nodequals = [self._tensor_qual]
            self.history('.compose()', trace=trace)
      return node

   #-------------------------------------------------------------------------

   def decompose (self, replace=True, trace=False):
      """
      The reverse of .compose(). Return a list of separate tree nodes.
      If replace=True (default), make sure that the Clump object is in
      the 'decomposed' state, i.e. self._nodes contains separate tree nodes.
      """
      nodes = self._nodes[0]
      if self._composed:                   # ONLY if in 'composed' state
         tensor = self._nodes[0]
         nodes = []
         stub = self.unique_nodestub('decomposed')
         for index,qual in enumerate(self._nodequals):
            node = stub(qual) << Meq.Selector(tensor, index=index)
            nodes.append(node)
         if replace:
            self._nodes = nodes
            self._composed = False            # set the switch
            self._nodequals = self._treequals
            self.history('.decompose()', trace=trace)
      return nodes

   #-------------------------------------------------------------------------

   #-------------------------------------------------------------------------

   #-------------------------------------------------------------------------


   #=========================================================================
   # Apply arbitrary unary (unops) or binary (binops) operaions to the nodes:
   #=========================================================================

   def apply_unops (self, unops, **kwargs):
      """
      Apply one or more unary operation(s) (e.g. MeqCos) on its nodes.
      """
      prompt = '.apply_unops('+str(unops)+')'
      help = prompt
      ctrl = self.on_entry(self.apply_unops, prompt, help, **kwargs)

      if self.execute_body():
         # Make sure that unops is a list:
         if isinstance(unops,tuple):
            unops = list(unops)
         elif isinstance(unops,str):
            unops = [unops]

         # Apply in order of specification:
         for unop in unops:
            stub = self.unique_nodestub(enclose=[unop+'(',')'])
            for i,qual in enumerate(self._nodequals):
               self._nodes[i] = stub(qual) << getattr(Meq,unop)(self._nodes[i])
         self.end_of_body(ctrl)

      return self.on_exit(ctrl)

   #-------------------------------------------------------------------------

   def apply_binop (self, binop, rhs, **kwargs):
      """Apply a binary operation (binop, e.g. 'Add') between its nodes
      and the given right-hand-side (rhs). The latter may be various
      things: a Clump, a node, a number etc.
      """
      prompt = 'apply_binop('+str(binop)+')'
      if isinstance(rhs,(int,float,complex)):       # rhs is a number
         help = str(rhs)+' '
      elif is_node(rhs):                            # rhs is a node
         help = 'node '+str(rhs.name)
      elif isinstance(rhs,type(self)):              # rhs is a Clump object
         help = rhs.oneliner()
      ctrl = self.on_entry(self.apply_binop, prompt, help, **kwargs)

      if self.execute_body():
         binop = kwargs['binop']                    # error if binop not specified
         rhs = kwargs['rhs']                        # error if rhs not specified

         if isinstance(rhs,(int,float,complex)):    # rhs is a number
            rhs = self._ns << Meq.Constant(rhs)     # convert to MeqConstant
         
         if is_node(rhs):                           # rhs is a node
            stub = self.unique_nodestub(binop)(rhs.name)
            for i,qual in enumerate(self._nodequals):
               self._nodes[i] = stub(qual) << getattr(Meq,binop)(self._nodes[i],rhs)

         elif isinstance(rhs,type(self)):           # rhs is a Clump object
            if self.commensurate(rhs, severe=True):
               stub = self.unique_nodestub(binop)(rhs._name)
               for i,qual in enumerate(self._nodequals):
                  self._nodes[i] = stub(qual) << getattr(Meq,binop)(self._nodes[i],rhs._nodes[i])
         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl)


   #=========================================================================
   # Visualization:
   #=========================================================================

   def inspector (self, bookpage=None, folder=None, **kwargs):
      """Make an inspector node for its nodes, and make a bookmark.
      """
      prompt = 'inspector()'
      help = None
      ctrl = self.on_entry(self.inspector, prompt, help, **kwargs)

      if self.execute_body():
         bundle = self.bundle (name='inspector', qual=None,
                               combine='Composer', trace=False)
         bundle.initrec().plot_label = self._treequals
         self._orphans.append(bundle)
         if not isinstance(bookpage,str):
            bookpage = self._name
         JEN_bookmarks.create(bundle,
                              name=bookpage, folder=folder,
                              viewer='Collections Plotter')
         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl)




#********************************************************************************
#********************************************************************************
# Standalone forest (i.e. not part of QuickRef.py) of this QR_module.
# Just load it into the browser, and compile/execute it.
#********************************************************************************
#********************************************************************************


def _define_forest (ns, **kwargs):
   """
   The expected function just calls do_define_forest().
   The latter is used outside _define_forest() also (see below)
   """
   if not enable_testing:
      print '\n**************************************************************'
      print '** TDLOptionManager _define_forest(): testing not enabled yet!!'
      print '**************************************************************\n'
      return False

   # Execute the function that does the actual work. It is the same
   # function that was called outside _define_forest(), where the
   # TDLOptions/Menus were configured (in TCM) and generated.
   # This second run uses the existing option values, which are
   # transferred by means of diskfiles (.TCM and .TRM)
   # It also re-defines the options/menus in a dummy TDLOptionManager,
   # but these are NOT converted into TDLOption/Menu objects. 

   do_define_forest (ns, TCM=TOM.TDLOptionManager(TCM))       

   # Generate at least one node:
   node = ns.dummy << 1.0

   return True


#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the node named 'rootnode'
    """
    domain = meq.domain(1,10,-10,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=11, num_time=21)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='rootnode', request=request))
    return result
       
#------------------------------------------------------------------------------


def do_define_forest (ns, TCM):
   """
   The function that does the actual work for _define_forest()
   It is used twice, outside and inside _define_forest() 
   """
   # Definition of menus and options:
   submenu = TCM.start_of_submenu(do_define_forest)

   # The function body:
   if TCM.submenu_is_selected():
      cp = Clump(ns=ns, TCM=TCM, trace=True)
      cp.apply_unops('Cos', select=False, trace=True)
      # cp.apply_unops('Sin', select=True, trace=True)
      # cp.apply_unops('Exp', trace=True)
      # cp.apply_binop('Add', 2.3, select=True, trace=True)
      cp.inspector()
      cp.rootnode()
      cp.show('do_define_forest()', full=True)

   # The LAST statement:
   TCM.end_of_submenu()
   return True

#------------------------------------------------------------------------------

# This bit is executed whenever the module is imported (blue button etc)

itsTDLCompileMenu = None
TCM = TOM.TDLOptionManager(__file__)
enable_testing = False


# enable_testing = True        # normally, this statement will be commented out
if enable_testing:
   ns = NodeScope()
   cp = do_define_forest (ns, TCM=TCM)
   itsTDLCompileMenu = TCM.TDLMenu(trace=False)

   



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
      cp = Clump(trace=True)
      cp.show('creation', full=True)

   if 0:
      print '** print str(cp) ->',str(cp)
      print '** print cp ->',cp

   if 0:
      for node in cp:
         print str(node)
   if 0:
      for index in [0,1,-1,5]:
         print '-- cp[',index,'] -> ',str(cp[index])
   if 0:
      cp.show_tree(-1, full=True)

   if 0:
      cp.compose()
      cp.show('.compose()')
      if 0:
         cp.decompose()
         cp.show('.decompose()')

   if 0:
      unops = 'Cos'
      # unops = ['Cos','Cos','Cos']
      unops = ['Cos','Sin']
      cp.apply_unops(unops, trace=True)    
      # cp.apply_unops()                       # error
      # cp.apply_unops(unops=unops, trace=True)
      # cp.apply_unops(unops=unops, select=True, trace=True)

   if 0:
      rhs = math.pi
      # rhs = ns.rhs << Meq.Constant(2.3)
      # rhs = Clump('RHS', clump=cp)
      cp.apply_binop(binop='Add', rhs=rhs, trace=True)

   if 0:
      unops = None
      unops = 'Identity'
      cp2 = cp.link(unops=unops)
      cp2.show('.link('+str(unops)+')', full=True)

   if 0:
      treequals = range(5)
      treequals = ['a','b','c']
      cp3 = Clump(treequals=treequals)
      cp.commensurate(cp3, severe=False, trace=True)
      cp3.show('.commensurate()')

   if 0:
      node = cp.inspector()
      cp.show('.inspector()')
      print '->',str(node)

   if 0:
      node = cp.rootnode() 
      cp.show('.rootnode()')
      print '->',str(node)

   if 1:
      cp.show('final', full=True)

   #-------------------------------------------------------------------

   if 0:
      cp.execute_body(None, a=6, b=7)
   
      
   print '\n** End of standalone test of: Clump.py:\n' 

#=====================================================================================





