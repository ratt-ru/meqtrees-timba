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

# import math                 # support math.cos() etc
# from math import *          # support cos() etc
import numpy                # support numpy.cos() etc


#******************************************************************************** 

class Clump (object):
   """
   Base-class for an entire zoo of derived classes that
   represent 'clumps' of trees, i.e. sets of similar nodes.
   Examples are ParmClump, JonesClump and VisClump.
   """

   def __init__(self, name='Clump', qual=None,
                quals=None, ns=None, TCM=None,
                use=None, init=True):
      """
      Initialize the Clump object, according to its type (see .init()).
      If another Clump of the same class is specified (use), use its
      defining characteristics (self._quals etc)
      """

      # If another Clump object is given (use), use its contents
      if not isinstance(use,type(self)):
         use = None
      
      # The Clum node names are derived from name and qualifier:
      self._name = str(name)       
      self._qual = qual  
      if use:
         if not isinstance(name,str):
            self._name = '('+use._name+')'
         if qual==None:
            self._qual = use._qual

      # The 'size' of the Clump is defined by the list of qualifiers:
      if use:
         self._quals = use._quals
      elif quals==None:
         self._quals = range(3)                # for testing
      elif isinstance(quals,tuple):
         self._quals = list(quals)
      elif not isinstance(quals,list):         # assume Clump of one
         self._quals = [quals]                 #

      # Make sure that it has a nodescope (ns):
      self._ns = ns
      if use:
         self._ns = use._ns
      elif not ns:
         # If not supplied, make a local one.
         self._ns = NodeScope()

      # Make sure that it has an TDLOptionManager (TCM):
      self._TCM = TCM
      if use:
         self._TCM = use._TCM
      elif not self._TCM:
         # If not supplied, make a local one.
         self._TCM = TOM.TDLOptionManager(self._name)

      # The nodes may be composed into a single tensor node.
      # In that case, the following qualifier will be used.
      # The list self._nodequals always has the same length as self._nodes.
      self._tensor_qual = 'tensor'+str(len(self._quals))
      self._composed = False            # see .compose() and .decompose()
      self._nodequals = self._quals     # self._nodequals is used for node generation

      # Initialize the object history:
      self.history(clear=True)

      # Finally: Initialize with suitable nodes (if required):
      # The function .init() is re-implemented in derived classes.
      # NB: See .copy() for an example where init=False.
      if init:
         self._init()

      return None

   #--------------------------------------------------------------------------

   def _init (self, trace=False):
      """Initialize the object with suitable nodes.
      Called from __init__() only
      Place-holder: To be re-implemented for derived classes.
      """
      submenu = self._TCM.start_of_submenu(self._init)
      self._TCM.add_option('aa')
      self._TCM.add_option('bb')

      self._TCM.getopt('aa', submenu)
      self._TCM.getopt('bb', submenu)

      self._nodes = []
      stub = self.nodestub()
      for i,qual in enumerate(self._nodequals):
         node = stub(qual) << Meq.Constant(i)
         self._nodes.append(node)

      self.history('.init()', trace=trace)

      # The LAST statement:
      self._TCM.end_of_submenu()
      return True

   #-------------------------------------------------------------------------

   def copy (self, trace=False):
      """Return a copy of this clump.
      """
      # Create a new Clump of the same type(!)..........
      # Do NOT initialize, because we will copy the nodes.
      new = Clump(use=self, init=False)

      # Copy the nodes:
      new._nodes = []
      stub = new.nodestub()
      for i,qual in enumerate(self._nodequals):
         node = stub(qual) << Meq.Identity(self._nodes[i])
         new._nodes.append(node)
      s = 'copied from: '+self.oneliner()
      new.history(s, trace=trace)
      return new


   #==========================================================================
   # Various text display functions:
   #==========================================================================

   def oneliner (self):
      ss = str(type(self)).split('.')[1].split("'")[0]+':'
      ss += ' '+str(self._name)
      if self._qual:
         ss += ' qual='+str(self._qual)
      ss += '  size='+str(self.size())
      if self._composed:
         ss += '  (composed: '+self._tensor_qual+')'
      return ss

   #--------------------------------------------------------------------------

   def show (self, txt=None, full=True):
      """
      """
      ss = '\n'
      ss += '\n** '+self.oneliner()
      if txt:
         ss += '   ('+str(txt)+')'
      ss += '\n * nodes (.len()='+str(self.len())+', .size()='+str(self.size())+'):'
      if full:
         for node in self:
            ss += '\n   - '+str(node)
      if self._TCM:
         ss += '\n * self._TCM: '+str(self._TCM.oneliner())
      ss += self.history(format=True, prefix='   | ')
      ss += '\n**\n'
      print ss
      return ss

   #-------------------------------------------------------------------------

   def show_tree (self, index=-1, full=True):
      """Show the specified (index) subtree.
      """
      node = self._nodes[index]
      print EN.format_tree(node, full=full)
      return True

   #-------------------------------------------------------------------------

   def history (self, append=None, clear=False,
                format=False, prefix='',
                show=False, trace=False):
      """Interact with the object history (a list of strings).
      """
      if clear:
         self._history = []
         s = '** Object history of: '
         s += self.oneliner()
         self._history.append(s)
         if trace:
            print '** .history(clear)'
      if append:
         s = ' -- '+str(append)
         s += '   -> node[0]: '+str(self._nodes[0])
         self._history.append(s)
         if trace:
            print '** .history(append): ',self._history[-1]
      if show or format:
         ss = ''
         for line in self._history:
            ss += '\n'+prefix+line
         ss += '\n'+prefix+'** Current oneliner(): '+str(self.oneliner())+'\n'
         if show:
            print ss
         if format:
            return ss
      return self._history


   #=========================================================================
   # Some general helper functions
   #=========================================================================

   def nodestub (self, qual=None, trace=False):
      """Convenience function to generate a (unique) nodestub.
      """
      stub = EN.unique_stub(self._ns, self._name, self._qual, qual)
      if trace:
         print '\n** .nodestub(',qual,') ->',str(stub)
      return stub

   #--------------------------------------------------------------------------

   def len(self):
      """Return the number of nodes in the Clump (one if a tensor)
      """
      return len(self._nodes)

   #--------------------------------------------------------------------------

   def size(self):
      """Return the number of trees in the Clump (even if in a tensor)
      """
      return len(self._quals)

   #--------------------------------------------------------------------------

   def __getitem__(self, index):
      """Get the specified (index) node.
      """
      return self._nodes[index]


   #=========================================================================
   # To and from tensor nodes:
   #=========================================================================

   def compose (self, trace=True):
      """Compose the Clump nodes into a single tensor node.
      See also .decompose()
      """
      if not self._composed:               # Only if in 'decomposed' state
         stub = self.nodestub('composed')(self._tensor_qual)
         node = stub << Meq.Composer(*self._nodes)
         self._nodes = [node]              # a list of a single node
         self._composed = True             # set the switch
         self._nodequals = [self._tensor_qual]
         self.history('.compose()', trace=trace)
      return True

   #-------------------------------------------------------------------------

   def decompose (self, trace=True):
      """Decompose the single tensor node into separate nodes again.
      The reverse of .compose()
      """
      if self._composed:                   # ONLY if in 'composed' state
         self._composed = False            # set the switch
         self._nodequals = self._quals
         tensor = self._nodes[0]
         self._nodes = []
         stub = self.nodestub('decomposed')
         for index,qual in enumerate(self._nodequals):
            node = stub(qual) << Meq.Selector(tensor, index=index)
            self._nodes.append(node)
         self.history('.decompose()', trace=trace)
      return True

   #-------------------------------------------------------------------------

   def bundle (self, name=None, combine='Composer', trace=False):
      """Return a single node that bundles the Clump nodes,
      using the specified bundling mechanism (e.g. MeqComposer).
      """
      hist = '.bundle('+str(name)+','+str(combine)+'): '
      if not self._composed:
         stub = self.nodestub('bundle')
         node = stub << getattr(Meq,combine)(*self._nodes)
      elif combine=='Composer':
         node = self._nodes[0]         # OK
      else:
         pass                          # decompose first....?
      self.history(hist, trace=trace)
      return node

   #-------------------------------------------------------------------------

   #-------------------------------------------------------------------------

   #-------------------------------------------------------------------------


   #=========================================================================
   # Unops and binops:
   #=========================================================================

   def apply_unop (self, unops, trace=False):
      """
      Apply one or more unary operation(s) (e.g. MeqCos) on its nodes.
      """
      # First condition the list of unary operations:
      if isinstance(unops,tuple):
         unops = list(unops)
      elif isinstance(unops,str):
         unops = [unops]

      # Then apply in order of specification:
      for unop in unops:
         stub = self.nodestub(unop)
         for i,qual in enumerate(self._nodequals):
            self._nodes[i] = stub(qual) << getattr(Meq,unop)(self._nodes[i])
         self.history('.unops('+unop+')', trace=trace)

      return True

   #-------------------------------------------------------------------------

   def apply_binop (self, binop=None, rhs=None, trace=False):
      """Apply a binary operation (e.g. MeqAdd) between its nodes
      and the given right-hand-side (rhs). The latter may be various
      things: a Clump, a node, a number etc.
      """
      hist = '.binop('+str(binop)+') '
      if is_node(rhs):
         hist += 'node '+rhs.name
         stub = self.nodestub(binop)(rhs.name)
         for i,qual in enumerate(self._nodequals):
            self._nodes[i] = stub(qual) << getattr(Meq,binop)(self._nodes[i],rhs)
      self.history(hist, trace=trace)
      return True

      
   #=========================================================================
   # Some test-function that define options (TCM):
   #=========================================================================

   def testopt1 (self, trace=True):
      """
      Test-function
      """
      submenu = self._TCM.start_of_submenu(self.testopt1)
      self._TCM.add_option('aa')
      self._TCM.add_option('bb')

      self._TCM.getopt('aa', submenu)
      self._TCM.getopt('bb', submenu)

      self.history('.testopt1()', trace=trace)

      # The LAST statement:
      self._TCM.end_of_submenu()
      return True

   #-------------------------------------------------------------------------
      
   def testopt2 (self, trace=True):
      """
      Test-function
      """
      submenu = self._TCM.start_of_submenu(self.testopt2)
      self._TCM.add_option('aa')
      self._TCM.add_option('bb')

      self._TCM.getopt('aa', submenu)
      self._TCM.getopt('bb', submenu)

      self.history('.testopt2()', trace=trace)

      # The LAST statement:
      self._TCM.end_of_submenu()
      return True

      



#********************************************************************************
#********************************************************************************
# Standalone forest (i.e. not part of QuickRef.py) of this QR_module.
# Just load it into the browser, and compile/execute it.
#********************************************************************************
#********************************************************************************


def _define_forest (ns, **kwargs):
   """The expected function just calls do_define_forest().
   The latter is used outside _define_forest() also (see below)
   """
   if not enable_testing:
      print '\n**************************************************************'
      print '** TDLOptionManager _define_forest(): testing not enabled yet!!'
      print '**************************************************************\n'
      return False
   return do_define_forest (ns, TCM=TOM.TDLCompileMenu(TCM), trace=False)       

#------------------------------------------------------------------------------


def do_define_forest (ns, TCM):
   """The function that does the work for _define_forest()
   It is used outside _define_forest() also (see below)
   """
   return True

#------------------------------------------------------------------------------


itsTDLCompileMenu = None
TCM = TOM.TDLOptionManager(__file__)
enable_testing = False
# enable_testing = True        # normally, this statement will be commented out
if enable_testing:
   # Only use for testing (otherwise it will appear in every menu)!
   if 0:
      # Regular (OMS) option definition
      TDLCompileMenu('TDLCompileMenu()',
                     TDLOption('xxx','XXX',range(3)),
                     TDLOption('yyy','YYY',range(3)),
                     toggle='TDLCompileMenu()')
   if 0:
      # Use of TCM to specify options OUTSIDE functions:
      TCM.start_of_submenu('TCM', help='Clump OUTSIDE functions')
      TCM.add_option('aa',range(3))
      TCM.add_option('bb',range(3))
   if 1:
      # Use of TCM to specify options INSIDE functions:
      ns = NodeScope()
      do_define_forest (ns, TCM=TCM, trace=False)
   if 0:
      TCM.TRM.start_of_submenu('TRM', help='runtime options/menus')
      TCM.TRM.add_option('aa',range(3))
      TCM.TRM.add_option('bb',range(3))
   if 1:
      itsTDLCompileMenu = TCM.TDLMenu(trace=False)
   TCM.show('finished')

   

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
   # rider = QRU.create_rider()             # CollatedHelpRecord object

   if 1:
      cp = Clump()
      cp.show('creation', full=True)

   if 1:
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
      unops = ['Cos','Sin']
      cp.apply_unop(unops)

   if 1:
      rhs = ns.rhs << Meq.Constant(2.3)
      cp.apply_binop('Add', rhs=rhs)

   if 1:
      cp.show('final', full=True)
      
   print '\n** End of standalone test of: Clump.py:\n' 

#=====================================================================================





