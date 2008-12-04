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
#   - 21 nov 2008: split off coreclump.py
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

from Timba.Contrib.JEN.Clump import clumpcore
from Timba.Contrib.JEN.control import TDLOptionManager as TOM

from Timba.Contrib.JEN.Easy import EasyNode as EN
from Timba.Contrib.JEN.Easy import EasyFormat as EF

import Meow.Bookmarks
from Timba.Contrib.JEN.util import JEN_bookmarks

import math                 # support math.cos() etc
import numpy                # support numpy.prod() etc
import random               # e.g. random.gauss()
import copy

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
      If another Clump of the same class is specified (use), transfer its
      defining characteristics (datadesc etc), and possibly its nodes.
      """
      # Every Clump object has a clumpcore object:
      typename = str(type(self)).split('.')[-1].split("'")[0]
      self.core = clumpcore.clumpcore (clump,
                                       typename=typename,
                                       **kwargs)

      # Initialise self.core._stubtree:
      self.unique_nodestub()

      # Execute the required function, if required:
      if kwargs.get('execute_initexec',True):
          self.initexec(**kwargs)

      # Finished:
      return None

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


   #==========================================================================
   #==========================================================================

   def connect_grafted_clump (self, clump, trace=False):
      """Connect the loose ends (orphans, stubtree, ParmClumps) of the given
      clump, e.g. when JonesClumps are used to correct VisClumps.
      This is similar to, but slightly different from, what is done in the
      function self.transfer_clump_nodes(), which merely continues the mainstream.
      """
      self.core.graft_to_stubtree(clump.core._stubtree)
      self.core._orphans.extend(clump.core._orphans)             # group them first?
      self.core._ParmClumps.extend(clump.core._ParmClumps)       
      self.core.copy_history(clump)
      self.history('.connect_grafted_clump(): '+str(clump))
      return True

   #--------------------------------------------------------------------------

   def connect_loose_ends (self, clump=None, full=True, trace=False):
      """Connect the loose ends (orphans, stubtree, but NO ParmClumps!) of the
      current clump to another one, e.g. the input clump (=default).
      This is the reverse of .connect_grafted_clump().
      """
      if clump==None:
         clump = self.core._input_clump
      clump.core.graft_to_stubtree(self.core._stubtree)
      clump.core._orphans.extend(self.core._orphans)         # group them first?
      if full:
         clump.core.copy_history(self)
         self.history('.connect_loose_ends() to: '+str(clump))
         clump.history('.connected loose ends of: '+str(self))
      return True

   #--------------------------------------------------------------------------

   def copy(self, name=None, **kwargs):
       """Return a 'working copy' of itself, i.e. a copy that may be modified
       without changing this clump itself. See e.g. SolverUnit.py.
       """
       if not isinstance(name,str):
           name = 'copy('+self.name()+')'
       clump = Clump.Clump(self, name=name,
                           hide=True, makemenu=False)
       clump.history('.copy() of: '+str(self))
       # self.history('copied to: '+str(clump))
       return clump
   
   #==========================================================================
   # Fuctions that depend on whether or not the Clump has been selected:
   #==========================================================================

   def append_if_selected(self, clist=[], notsel=None, trace=False):
      """If selected, append the object to the input list (clist).
      Otherwise, append it to the 'not-selected' (notsel) list, if supplied.
      Syntax:  clist = Clump(cp).append_if_selected(clist=[], notsel=[])
      """
      selected = self.core._object_is_selected
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
      """Return the object itself, or its self.core._input_clump.
      The latter if it has a menu, but is NOT selected by the user.
      This is useful for making daisy-chains of Clump objects, where
      the user determines whether a particular Clump is included.
      Syntax:  cp = Clump(cp).daisy_chain()
      """
      selected = self.core._object_is_selected
      if trace:
         print '\n ** .daisy_chain(selected=',selected,'): ',self.oneliner()
         print '     self.core._input_clump =',self.core._input_clump
      if self.core._input_clump and (not selected):
         if trace:
            print '     -> input clump: ',self.core._input_clump.oneliner()
         return self.core._input_clump
      if trace:
         print '     -> itself'
      return self



   #==========================================================================
   # Various text display functions:
   #==========================================================================

   def oneliner (self):
      ss = self.core.oneliner()
      # ss += '...'
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
      prefix = '\n     '

      #.....................................................
      ss += self.core.show(full=full, doprint=False)

      #.....................................................
      ss += prefix+'++ Specific (derived class '+str(self.typename())+'):'
      ss += self.show_specific()

      #.....................................................
      ss += prefix+' + Local attributes (start with self._):'
      cc = dir(self)
      for s in cc:
          a = getattr(self,s,None)
          if s[0:2]=='__':
              # ss += prefix+'   - '+s
              pass  
          elif not s[0]=='_':
              # ss += prefix+'   - '+s
              pass
          elif getattr(a,'oneliner',None):
              ss += prefix+'   - '+s+' = '+str(a.oneliner())
          elif isinstance(a,dict):
              ss += prefix+'   - '+s+':'
              for key in a.keys():
                  v = a[key]
                  if getattr(v,'oneliner',None):
                      ss += prefix+'     - '+str(key)+' = '+str(v.oneliner())
                  else:
                      ss += prefix+'     - '+str(key)+' = '+str(EF.format_value(v))
          elif isinstance(a,list):
              if is_node(a[0]):
                  ss += prefix+'   - '+s+' (list of '+str(len(a))+' nodes):'
                  for i,node in enumerate(a):
                      ss += prefix+'     - '+str(i)+': '+str(node)
              else:
                  ss += prefix+'   - '+s+' = '+str(EF.format_value(a))
          else:
              ss += prefix+'   - '+s+' = '+str(EF.format_value(a))
      
      #.....................................................
      ss += prefix+' + self.rider(): (carries user-defined information):'
      rr = self.rider()
      ss += ' (len='+str(len(rr))+')'
      for key in rr.keys():
         if getattr(rr[key],'oneliner',None):
            ss += prefix+'   - '+str(key)+' = '+str(rr[key].oneliner())
         else:
            ss += prefix+'   - '+str(key)+' = '+str(EF.format_value(rr[key]))

      #.....................................................
      ss += '\n**\n'
      if doprint:
         print ss
      return ss

   #-------------------------------------------------------------------------
   #-------------------------------------------------------------------------

   def show_specific(self):
      """
      Format the specific (non-generic) contents of the class.
      Placeholder for re-implementation in derived class.
      """
      ss = ''
      ss += '\n      + ...'
      return ss


   #=========================================================================

   def rider (self, key=None, **kwargs):
      """The rider contains arbitrary user-defined information.
      """
      return self.core.rider(key, **kwargs)

   #=========================================================================

   def history (self, append=None, **kwargs):
      """Interact with the object history (a list of strings).
      """
      return self.core.history(append=append, **kwargs)
   
   #=========================================================================

   def datadesc (self, **kwargs):
      """Interact with the data description record.
      """
      return self.core.datadesc(**kwargs)
   
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

   def name (self):
       """Return the object name.
       """
       return self.core._name

   #--------------------------------------------------------------------------

   def typename (self):
       """Return a short version of the object type name.
       """
       return self.core._typename

   #--------------------------------------------------------------------------

   def indices(self):
      """Return the list of indices [0,1,2,...] of the actual tree nodes.
      If composed, this will be [0] (referring to a single tensor node).
      """
      return self.core.indices()

   #--------------------------------------------------------------------------

   def size(self):
      """Return the number of trees in the Clump (even if in a tensor)
      """
      return self.core.size()

   #--------------------------------------------------------------------------

   def __len__(self):
      """Get the nr of nodes. Syntax: len = len(clump)
      """
      return len(self.core._nodes)

   #--------------------------------------------------------------------------

   def clear(self):
       """Clear the internal node-list [].
       """
       self.core._nodes = []
       self._nodequals = []
       return True

   #--------------------------------------------------------------------------

   def append(self, node=None, clear=False):
       """Append the given node(s) to the internal list.
       If clear=True, set the internal list to [] first.
       NB: the user should keep track of treequals/nodequals!!
       Still, this is safer than using .__add__() below.
       """
       if clear:
           self.clear()
       if is_node(node):
           self.core._nodes.append(node)
       elif isinstance(node,list):
           self.core._nodes.extend(node)
       else:
           self.ERROR('the node is not a node, but: '+str(type(node)))
       return len(self)

   #--------------------------------------------------------------------------

   def __add__(self, node):
      """Add (append) the given node(s) to the list self.core._nodes.
      Syntax: clump + node   or: clump + [node1,node2,...]
      NB: Not recommended, because it requires: self.core._nodes = []
      Better to have self.core._nodes to be a list of the correct length always.
      """
      was = len(self)
      if True:
          self.WARNING('\n** Use of clump.__add__(node) is disabled!!\n')
      else:
          nodes = []
          if is_node(node):
              self.core._nodes += [node]
          elif isinstance(node,list):
              self.core._nodes += node
          elif isinstance(node,tuple):
              self.core._nodes += list(node)
          else:
              self.ERROR('** not a node(list), but: '+str(type(node))) 
      # print '\n** __add__(): ',was,'->',len(self)
      return len(self)

   #--------------------------------------------------------------------------

   def __getitem__(self, index):
      """Get the specified (index) node. Syntax: node = clump[i]
      NB: This is a VERY important function, with many uses.
      See 'Learning Python', pp 329-330.
      """
      if not getattr(self.core,'_nodes',None):     # does not exist yet
          self.core._nodes = self.size()*[None]
      elif index<0 or index>=len(self):
          self.ERROR('node index out of range: '+str(index)+'/'+str(len(self)))
      node = self.core._nodes[index]
      if not is_node(node):
          self.history('.__getitem__('+str(index)+'): node = '+str(node), trace=True)
      return node

   #--------------------------------------------------------------------------

   def __setitem__(self, index, node):
      """Replace the specified (index) node. Syntax: clump[i] = node
      Make sure that self.core._nodes is a list of the right length.
      """
      if not getattr(self.core,'_nodes',None):     # does not exist yet
          self.core._nodes = self.size()*[None]
      elif len(self)==0:                          # has zero length
          self.core._nodes = self.size()*[None]
      elif index<0 or index>=len(self):
          self.ERROR('node index out of range: '+str(index)+'/'+str(len(self)))
      self.core._nodes[index] = node
      return None

   #--------------------------------------------------------------------------

   def __str__(self):
      """Print-conversion. Syntax: print clump, prints clump.oneliner().
      """
      return self.oneliner()

   #-------------------------------------------------------------------------

   def treequals (self):
       """Return the list of Clump tree qualifiers.
       """
       return self.core._datadesc['treequals']

   #-------------------------------------------------------------------------

   def nodequals (self):
       """Return the list of actual node qualifiers.
       """
       return self.core._nodequals

   
   #-------------------------------------------------------------------------

   def input_clump (self):
       """Return the input Clump object
       """
       return self.core._input_clump

   #-------------------------------------------------------------------------

   def ns (self):
       """Return the internal nodescope
       """
       return self.core._ns

   #-------------------------------------------------------------------------

   def TCM (self):
       """Return the internal TDLOptionManager object.
       """
       return self.core._TCM

   
   #=========================================================================
   # Helper functions for node generation:
   #=========================================================================

   def unique_nodestub (self, *qual, **kwqual):
      """
      Convenience function to generate a (unique) nodestub for tree nodes.
      The stub is then initialized (which helps the uniqueness determination!)
      and attached to the internal subtree of stub-nodes, which would otherwise
      be orphaned. They are used to carry quickref-help information, which
      can be used in the various bookmark pages.
      """
      return self.core.unique_nodestub (*qual, **kwqual)


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
      self.core._kwargs = kwargs                          # temporary
      self.core._override_keys = []
      self.core._override = dict()

      # Make the menu for the calling function:
      # NB: if any options are defined in this module, always makemenu=True,
      # otherwise there is a high probablility of option name clashes!
      if makemenu:
         # Make a unique submenu name:
         self.core._stage['isubmenu'] += 1                # increment
         self.core._stage['count'] += 1                   # increment
         self.core._stage['ops'] = -1                     # reset
         name = fname
         name += '_'+str(self.core._stage['isubmenu'])
         name += str(self.core._stage['count'])
         name += str(self.core._stage['ops'])
         name += str(self.core._stage['ncopy'])

         if not isinstance(prompt,str):
            prompt = fname+'()'
            if fname=='initexec':                    # special case
               prompt = self.name()+':'
         if not isinstance(help,str):
            help = fname+'()'
            if fname=='intexec':                     # special case
               help = 'in/exclude: '+self.oneliner()
         ctrl['submenu'] = self.core._TCM.start_of_submenu(name,
                                                      prompt=prompt,
                                                      help=help,
                                                      default=select,
                                                      hide=hide,
                                                      slaveof=self.core._slaveof,
                                                      fixture=fixture,
                                                      qual=self.core._qual)

      # The ctrl record used by other control functions downstream.
      # The opening ones use self.core._ctrl, but the closing ones have to use
      # the ctrl argument (since self.core._ctrl may be overwritten by other
      # functions that are called in the function body (AFTER all .getopt() calls!)
      self.core._ctrl = ctrl
      return ctrl

   #--------------------------------------------------------------------------

   def add_option (self, relkey, choice=None, **kwargs):
      """Add an option to the current menu. The purpose of this function
      is mainly to hide the use of 'self.core._TCM' to the Clump user/developer.
      In the future it might be useful to put some extra features here...
      """
      self.core._override_keys.append(relkey)          # see .execute_body()
      if True:
         # The option choice may be overridden via the input kwargs:
         if self.core._input_kwargs.has_key(relkey):
            v = self.core._input_kwargs[relkey]
            was = copy.copy(choice)
            if isinstance(v,list):                # e.g. [2,3]
               choice = v                         # replace choice
               kwargs['more'] = None              # do not allow other values 
            else:                                 # e.g. 2
               choice.insert(0,v)                 # make it the default
            print '\n** add_option(',relkey+'):',was,'->',choice,'\n'
      return self.core._TCM.add_option(relkey, choice, **kwargs)

   #--------------------------------------------------------------------------

   def execute_body(self, always=False, hist=False):
      """To be called at the start of the 'body' of a Clump stage-method,
      i.e. AFTER any self.core._TCM menu and option definitions.
      Its (mandatory!) counterpart is self.end_of_body(ctrl)
      It uses the record self.core._ctrl, defined in .on_entr()
      """

      self.check_for_overrides()

      fname = self.core._ctrl['funcname']                 # convenience

      execute = True                      
      if not always:                        
         if isinstance(self.core._ctrl['submenu'],str):
            execute = self.core._TCM.submenu_is_selected(trace=False)

      if self.core._ctrl['trace']:
         print '** .execute_body(always=',always,'): fname=',fname,' execute=',execute

      if not execute:
         if fname=='initexec':                       # a special case
            self.core._object_is_selected = False         # see .__init__() and .daisy_chain()
      else:
         if fname=='initexec':                       # a special case
            self.core._object_is_selected = True          # see .__init__() and .daisy_chain()
         self.core._stage['count'] += 1                   # increment
         self.core._stage['ops'] = -1                     # reset
         self.core._stage['name'] = fname                 # .....?
         if hist:
            s = '.'+fname+'(): '                     # note the ':'
            if isinstance(hist,str):
               s += '('+hist+')  '
            self.history(append=s, trace=self.core._ctrl['trace'])
      return execute

   #--------------------------------------------------------------------------

   def check_for_overrides (self):
      """Check whether self.core._kwargs (see .on_entry(**kwargs)) contains
      any of the option (rel)keys accumulated in .add_option(key),
      and put these override values in the dict self.core._override.
      The latter is then used in .getopt(key) to return the override value
      rather than the option value.
      """
      ovr = dict()
      for key in self.core._override_keys:
         if self.core._kwargs.has_key(key):
            ovr[key] = self.core._kwargs[key]
      if len(ovr)>0:
         self.history('.override: '+str(ovr))
      self.core._override = ovr                    # see .getopt()
      self.core._override_keys = []                # reset
      self.core._kwargs = None                     # reset
      return True


   #..........................................................................

   def getopt (self, relkey, trace=False):
      """Get the specified (relkey) TDL option value.
      This function is ONLY called AFTER self.execute_body()==True.
      It use the record self.core._ctrl that is defined in .on_entry()
      """
      # trace = True
      override = self.core._override.has_key(relkey)
      if override:
         value = self.core._TCM.getopt(relkey, self.core._ctrl['submenu'],
                                  override=self.core._override[relkey])
      else:
         value = self.core._TCM.getopt(relkey, self.core._ctrl['submenu'])

      if trace or self.core._ctrl['trace']:
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
         self.core._TCM.end_of_submenu()
      if ctrl['trace']:
         print '** .on_exit(ctrl, result=',result,'): fname=',fname,'\n'
      return result


   #=========================================================================
   # Functions dealing with subsets (of the tree nodes):
   #=========================================================================

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
         # ii = self.core.indices(subset=subset, nodelist=nodelist, trace=trace)   # <----??
         for i,node in enumerate(nodelist):
            # Test whether node is a node (or a number?)
            cc.append(node)
      else:
         ii = self.core.indices(subset=subset, trace=trace)
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
         print '\n** get_nodes(',subset,str(append),str(prepend),nodelist,'):',self
         for i,node in enumerate(cc):
            print '  -',i,':',str(node)
         print
      return cc


   #=========================================================================
   # To and from tensor nodes:
   #=========================================================================

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
      elif not self.core._composed:                         # not in composed state
         cc = self.get_nodelist()                      #   bundle self.core._nodes
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

      cc = self.get_nodelist()
      if self.core._composed:                   # already in composed state
         node = cc[0]                           # return node
         replace = False
      else:
         stub = self.unique_nodestub('composed')
         node = stub(n=self.size()) << Meq.Composer(*cc)

      if replace:
         self.core._nodes = [node]              # a list of a single node
         self.core._composed = True             # set the switch
         self.core._nodequals = [0]
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
      cc = self.get_nodelist()        
      if not self.core._composed:               # already in de-composed state
         replace = False
      else:             
         tensor = cc[0]                         # the single tensor node
         stub = self.unique_nodestub('decomposed')
         cc = []
         for index,qual in enumerate(self.treequals()):
            node = stub(qual) << Meq.Selector(tensor, index=index)
            cc.append(node)

      if replace:
         self.core._nodes = cc
         self.core._composed = False            # set the switch
         self.core._nodequals = self.treequals()
         self.history('.decompose()', show_node=True,
                      trace=kwargs.get('trace',False))
      # Always return the list of decomposed nodes:
      return cc


   #=========================================================================

   def commensurate(self, other, severe=False, trace=False):
      """Return True if the given (other) Clump is commensurate,
      i.e. it has the same self._nodequals (NOT self._datadesc['treequals']!)
      """
      cms = True
      if not self.size()==other.size():
         cms = False
      else:
         snq = self.nodequals()
         onq = other.nodequals()
         for i,qual in enumerate(snq):
            if not qual==onq[i]:
               cms = False
               break
      if not cms:
         s = '\n** '+self.oneliner()+'   ** NOT COMMENSURATE ** with:'
         s += '  '+other.oneliner()+'\n'
         if severe:
            self.ERROR(s)
         if trace:
            self.history(s)
            print s
      return cms

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
         for i,qual in enumerate(self.nodequals()):
            self[i] = stub(qual) << Meq.ReqSeq(node, self[i],
                                               result_index=1,
                                               cache_num_active_parents=1)
         self.history('.insert_reqseqs('+str(node)+')', show_node=True)
      return True

   #-------------------------------------------------------------------------

   def ParmClumps(self, append=None, trace=False):
      """Access to the internal list of ParmClumps
      """
      if isinstance(append,list):
         self.core._ParmClumps.extend(append)
      elif append:
         self.core._ParmClumps.append(append)
      if trace:
         print '\n** ParmClumps'+len(self.core._ParmClumps)+':'+self.oneliner()
         for i,pc in enumerate(self.core._ParmClumps):
            print '-',i,':',str(pc)
         print
      return self.core._ParmClumps

   #-------------------------------------------------------------------------

   def get_solvable(self, trace=False):
      """Get all the solvable parameters from the entries of self.core._ParmClumps.
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

   #------------------------------------------------------------------------

   def search_nodescope (self, class_name=None,
                         name=None, tags=None,
                         return_names=False,
                         trace=False):
      """Search the nodescope for the specified nodes, starting at the
      tree nodes of this clump (subtree=nodelist). Possible arguments
      are class_name[=None], name[=None] (can have wildcards: a.*) or
      tags[=None] (str or list). If more are specified, only the nodes
      that have all the specs are returned (i.e. AND).
      NB: Without any arguments, ALL the nodes in the subtrees are found!
      Returns a list of zero or more nodes (default: return_names=False)
      or node-names (if return_names==True).
      """
      nodes = self.ns().Search(class_name=class_name,
                               name=name, tags=tags,
                               subtree=self.get_nodelist(),
                               return_names=return_names)
      s = '.search_nodescope('+str(class_name)+','+str(name)+','+str(tags)+'):'
      s += ' found '+str(len(nodes))+' nodes'
      self.history(s, trace=trace)
      if trace:
          for i,node in enumerate(nodes):
              print '-',i,str(node)
          print
      return nodes


   #=========================================================================
   # Apply arbitrary unary (unops) or binary (binops) operaions to the nodes:
   #=========================================================================

   def check_unops(self, unops):
      """Helper function to make sure that the given unops is a list
      of unary operations, e.g. ['Sin','Cos'].
      """
      if unops==None:
          unops = []
      elif isinstance(unops,str):
         unops = unops.split(' ')                    # 'Cos Sin' -> ['Cos','Sin']
      elif not isinstance(unops,(list,tuple)):
         self.ERROR('** invalid unops: '+str(unops))
      return unops

   #------------------------------------------------------------------------

   def assure_list(self, x, append=None, prepend=None, trace=False):
      """Helper function to make sure that the given variable (x) is a list.
      Optionally, prepend/append other list elements.
      """
      if x==None:
          x = []
      elif isinstance(x,tuple):
          x =list(x)
      elif not isinstance(x,list):
          x = [x]
          
      if not append==None:
          if isinstance(append,list):
              x.extend(append)
          else:
              x.append(append)

      if not prepend==None:
          x.insert(0,prepend)

      return x

   #-------------------------------------------------------------------------

   def apply_unops (self, unops, nodelist=None, replace=True, **kwargs):
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

      # Get the list of nodes on which to apply unops:
      cc = self.get_nodelist(nodelist=nodelist)
      # This can also be an external nodelist, in which case the
      # internal self.core._nodes are ignored and unaffected (replace=False)
      if isinstance(nodelist,(list,tuple)):
         replace = False

      # Apply unops in order of specification:
      sunops = '..'
      for unop in unops:
         if not isinstance(unop,str):
            self.ERROR('unop is not a string: '+str(type(unop)+str(unop)))
         unop = unop.replace('Meq','')               # just in case....
         sunops = unop+'('+sunops+')'
         stub = self.unique_nodestub(unop+'()', **kwargs)
         for i,qual in enumerate(self.nodequals()):
            cc[i] = stub(qual) << getattr(Meq,unop)(cc[i],**kwargs)

      # Replace self.core._nodes, if required (default):
      if replace:
         self.core._nodes = cc  
         # Make an  object history entry (only if replaced):
         hist = '.apply_unops('+str(unops)
         for key in kwargs.keys():
            hist += ', '+str(key)+'='+str(kwargs[key])
         hist += '): '
         if len(unops)>1:
            hist += sunops
         self.history(hist, show_node=True)

      # Always return the resulting list of nodes
      return cc

   #-------------------------------------------------------------------------

   def apply_binop (self, binop, rhs, replace=True, **kwargs):
      """Apply a binary operation (binop, e.g. 'Add') between its nodes
      and the given right-hand-side (rhs). The latter may be various
      things: a Clump, a node, a number, a list, etc.
      Always return the resulting list of nodes.
      If replace=False, do not replace self.core._nodes with new nodes.
      """
      if not isinstance(binop,str):
         self.ERROR('binop is not a string: '+str(type(binop)+str(binop)))

      binop = binop.replace('Meq','')            # just in case....
      hist = None
      cc = []
      if isinstance(rhs,(int,float,complex)):    # rhs is a number
         srhs = EF.format_value(rhs)
         hist = 'rhs='+srhs
         stub = self.unique_nodestub(binop, srhs)
         for i,qual in enumerate(self.nodequals()):
            cc.append(stub(qual) << getattr(Meq,binop)(self[i],rhs))
         
      elif isinstance(rhs,list):                 # rhs is a list
         if not len(rhs)==self.size():
            self.ERROR('length mismatch: '+str(len(rhs))+'!='+str(self.size()))
         elif is_node(rhs[0]):                     # a list of nodes
            hist = 'rhs is list, rhs[0]='+str(rhs[0].name)
            stub = self.unique_nodestub(binop)
            for i,qual in enumerate(self.nodequals()):
               cc.append(stub(qual)(str(rhs[i].name)) << getattr(Meq,binop)(self[i],rhs[i]))
         elif isinstance(rhs[0],(int,float,complex)): # a list of numbers
            srhs = EF.format_value(rhs[0])
            hist = 'rhs is list, rhs[0]='+srhs
            stub = self.unique_nodestub(binop)
            for i,qual in enumerate(self.nodequals()):
               srhs = EF.format_value(rhs[i])
               cc.append(stub(qual)(srhs) << getattr(Meq,binop)(self[i],rhs[i]))
         else:
            self.ERROR('** type of rhs[0] not recognised: '+str(type(rhs[0])))

      elif is_node(rhs):                         # rhs is a node
         hist = 'rhs='+str(rhs.name)
         stub = self.unique_nodestub(binop, rhs.classname)
         for i,qual in enumerate(self.nodequals()):
            cc.append(stub(qual) << getattr(Meq,binop)(self[i],rhs))

      elif isinstance(rhs,type(self)):           # rhs is a Clump object
         if self.commensurate(rhs, severe=True):
            hist = 'rhs='+rhs.oneliner()
            stub = self.unique_nodestub(binop, rhs.typename())
            for i,qual in enumerate(self.nodequals()):
               cc.append(stub(qual) << getattr(Meq,binop)(self[i],rhs[i]))
      else:
         self.ERROR('** type of rhs not recognised: '+str(type(rhs)))

      # Replace self.core._nodes, if required (default):
      if replace:
         self.core._nodes = cc                        # replace self.core._nodes
         # Make an  object history entry (only if replaced):
         hist = '.apply_binop('+str(binop)+', '+str(hist)+')'
         self.history(hist, show_node=True)

      # Always return the resulting list of nodes:
      return cc


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
         folder = self.name()
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


   #=====================================================================

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
         self.plot_sumabs(**kwargs)
         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl)

   #---------------------------------------------------------------------

   def inspector (self, nodelist=None, **kwargs):
      """Make an inspector node for its nodes, and make a bookmark.
      """
      kwargs['select'] = True
      bookpage = kwargs.get('bookpage', None)
      folder = kwargs.get('folder', None)

      prompt = '.inspector()'
      help = 'make an inspector-plot (Collections Plotter) of the tree nodes'
      ctrl = self.on_entry(self.inspector, prompt, help, **kwargs)

      node = self[0]
      if self.execute_body(hist=False):
         cc = self.get_nodelist(nodelist=nodelist)
         node = self.bundle(name='inspector', nodelist=cc)
         node.initrec().plot_label = self.core._datadesc['treelabels']     # list of strings!
         self.core._orphans.append(node)
         self.make_bookmark(node,
                            name=bookpage, folder=folder,
                            viewer='Collections Plotter')
         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl, result=node)


   #---------------------------------------------------------------------

   def plot_sumabs (self, nodelist=None, **kwargs):
      """Plot a summary of its nodes
      """
      kwargs['select'] = True

      prompt = '.plot_sumabs()'
      help = 'make a sum(abs()) plot of the tree nodes'
      ctrl = self.on_entry(self.plot_sumabs, prompt, help, **kwargs)

      node = self[0]
      if self.execute_body(hist=False):
         bookpage = kwargs.get('bookpage', None)
         folder = kwargs.get('folder', None)
         name = kwargs.get('name', None)
         if not isinstance(name,str):
            name = 'sumabs'

         unops = ['Stripper','Abs']
         cc = self.get_nodelist(nodelist=nodelist, unops=unops)
         stub = self.unique_nodestub()
         sumabs = stub('sum(abs())') << Meq.Add(*cc)
         cc = self.get_nodelist(prepend=sumabs)
         node = stub(name) << Meq.Composer(*cc)
         self.core._orphans.append(node)
         self.make_bookmark(node, name=bookpage, folder=folder)
         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl, result=node)


   #---------------------------------------------------------------------
         
   def compare (self, clump, **kwargs):
      """
      Compare (Subtract, Divide) its nodes with the corresponding
      nodes of another Clump, or list of nodes, or list of numbers.
      Make a plot_sumabs() plot.
      Return the list of resulting nodes.
      """
      kwargs['select'] = True
      binop = kwargs.get('binop','Subtract')
      prompt = '.compare('+binop+')'
      help = clump.oneliner()
      ctrl = self.on_entry(self.compare, prompt, help, **kwargs)

      node = self[0]
      if self.execute_body():
         cc = self.apply_binop(binop, clump, replace=False)
         node = self.plot_sumabs(nodelist=cc)
         self.core._orphans.append(node)              
         self.end_of_body(ctrl)

      return self.on_exit(ctrl, result=node)

   #---------------------------------------------------------------------

   def plot_node_results (self, **kwargs):
      """Plot the specified (index) subset of the members of self.core._nodes
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
         nodes = self.get_nodelist()
         if not isinstance(folder,str):
            folder = self.name()
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
            nodequal = self.nodequals()[index]
            bookpage += '['+str(nodequal)+']'
         if not isinstance(folder,str):
            folder = self.name()
            self.make_bookmark(self[index],
                               recurse=recurse,
                               name=bookpage, folder=folder,
                               viewer=viewer)
         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl)



















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

   def __init__(self, clump=None, nodelist=None, **kwargs):
      """
      Derived from class Clump.
      """
      if nodelist:
          # Check the input nodelist:
          nn = []
          if is_node(nodelist):                    # A single node
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
          self._input_nodelist = nn            
          kwargs['treequals'] = range(len(nn))
          kwargs['execute_initexec'] = False

      #...................................................................
      # The following (among many other things) executes the function
      # self.initexec(**kwargs), which is re-implemented below.
      kwargs['select'] = True                           # always make a clump selection menu
      kwargs['transfer_clump_nodes'] = False            # see Clump.__init___()
      Clump.__init__(self, clump=clump, **kwargs)
      #...................................................................

      if nodelist:
          # Fill the Clump with the input nodelist: 
          self.core._nodes = []
          self.core._nodequals = []
          for i,node in enumerate(self._input_nodelist):
              self.core._nodes.append(node)
              self.core._nodequals.append(i)
          self.core._composed = False
          self.history('Created from list of nodes', show_node=True)
          
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
         stub = self.unique_nodestub('const', name='dummy')
         for i,qual in enumerate(self.nodequals()):
            cc = []
            for k,elem in enumerate(dd['elems']):
               if dd['complex']:
                  v = complex(k+i,i/10.)
               else:
                  v = float(k+i)
               if nelem==1:
                  node = stub(c=v)(qual) << Meq.Constant(v, tags=['leaf',str(i)])
               else:
                  node = stub(c=v)(qual)(elem) << Meq.Constant(v)
               cc.append(node)
            if nelem>1:
               node = stub(nelem=nelem)(qual) << Meq.Composer(*cc)
            self[i] = node
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

   if 0:
      clump = Clump(trace=True)

   if 0:
      c1 = None 
      if 0:
          c1 = Clump(treequals=range(5))
          c1.show()
      clump = LeafClump(c1, trace=True)
      if 1:
          clump.search_nodescope(trace=True)
          clump.search_nodescope(tags='leaf', trace=True)
          clump.search_nodescope(tags=['leaf','1'], trace=True)
          clump.search_nodescope(tags='lef', trace=True)
          clump.search_nodescope(name='d*', trace=True)
          clump.search_nodescope(name='d.*', trace=True)
          clump.search_nodescope(class_name='MeqParm', trace=True)
          clump.search_nodescope(class_name='MeqParm', tags='leaf', trace=True)

   if 1:
      cc = []
      for i in range(4):
          node = ns.ddd(i) << Meq.Constant(i)
          cc.append(node)
      clump = LeafClump(nodelist=cc, ns=ns, trace=True)

   if 1:
      clump.show('creation', full=True)

   if 0:
       node = ns << 4.5
       clump + node 
       clump + [node] 
       clump + [node,node,node] 

   if 0:
       print '\n** len(clump) -> ',len(clump)

   if 0:
      clump.rider('aa', new=56)
      clump.rider('bb', new='56')
      clump.rider('clump', new=clump)

   if 0:
      print '** print str(clump) ->',str(clump)
      print '** print repr(clump) ->',repr(clump)
      print '** print clump ->',clump

   if 0:
      for node in clump:
          print str(node)

   if 0:
      for index in [0,1,-1]:
          print '-- clump[',index,'] -> ',str(clump[index])
      # print '-- clump[78] -> ',str(clump[78])

   if 0:
       for index in clump.indices():
           print '-- clump[',index,'] =',str(clump[index])
           clump[index] = 2*clump[index]
           print '-- clump[',index,'] -> ',str(clump[index])

   if 0:
      # clump.get_nodelist(subset=0, trace=True)
      cc = clump.get_nodelist(trace=True)
      cc = clump.get_nodelist(nodelist=range(3), trace=True)
      cc = clump.get_nodelist(append=(ns<<4), prepend=(ns<<4), trace=True)
      print '-> cc=',len(cc),' cc[0]: ',str(cc[0])
      
   if 0:
      clump.show_tree(-1, full=True)

   if 0:
      print '.compose() ->',clump.compose()
      clump.show('.compose()')
      if 1:
         print '.decompose() ->',clump.decompose()
         clump.show('.decompose()')

   if 0:
      unops = 'Cos'
      unops = ['Cos','Cos','Cos']
      unops = 'Cos Sin'
      # unops = 'MeqCos'
      # unops = ['Cos','Sin']
      clump.apply_unops(unops)    
      cc = clump.apply_unops(unops, replace=False)    
      cc = clump.apply_unops('Exp', nodelist=cc)    
      # clump.apply_unops('Resampler', mode=2)    
      # clump.apply_unops()                       # error
      print '-> cc=',len(cc),' cc[0]: ',str(cc[0])

   if 0:
      clump.apply_binop('Add', math.pi)
      clump.apply_binop('Add', clump)
      clump.apply_binop('Add', ns<<3.4)
      clump.apply_binop('Add', clump.indices())
      cc = clump.apply_unops('Exp')    
      clump.apply_binop('Add', cc)
      clump.apply_binop('Add', 4.5, replace=False)
      print '-> cc=',len(cc),' cc[0]: ',str(cc[0])

   if 0:
      treequals = range(5)
      treequals = ['a','b','c']
      clump3 = LeafClump(treequals=treequals)
      clump.commensurate(clump3, severe=False)
      clump3.show('.commensurate()')

   if 0:
      if True:
         node = clump.compose()
         clump.show('.compose() -> '+str(node))
      node = clump.bundle(combine='Add')
      clump.show('.bundle() -> '+str(node))

   if 0:
      node = ns.dummysolver << Meq.Constant(67)
      clump.insert_reqseqs(node, trace=True)
      clump.show('.insert_reqseqs()')

   if 0:
      node = clump.inspector()
      clump.show('.inspector()')
      print '->',str(node)

   if 0:
      node = clump.plot_sumabs()
      clump.show('.plot_sumabs()')
      print '->',str(node)

   if 0:
      node = clump.compare(clump)
      clump.show('.compare(itself)')
      print '->',str(node)

   if 0:
      clump1 = Clump(clump, select=True)
      clump1.show('clump1 = Clump(clump)', full=True)

   if 0:
      clump = Clump(clump, select=True).daisy_chain(trace=True)
      clump.show('daisy_chain()', full=True)

   if 0:
      clump.show('final', full=True)

   #-------------------------------------------------------------------
   # Some lower-level tests:
   #-------------------------------------------------------------------


   if 0:
      print getattr(clump,'oneline',None)

   if 0:
      clump.execute_body(None, a=6, b=7)

   
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





