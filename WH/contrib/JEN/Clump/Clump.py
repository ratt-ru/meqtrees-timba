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

   def __init__(self, name='clump', qual=None, quals=None,
                ns=None, TCM=None, copy=None):
      """
      Inialise the Clump object.
      """

      # If another Clump object is given (copy), copy its contents
      if not isinstance(copy,type(self)):
         copy = None
      
      # The Clum node names are derived from name and qualifier:
      self._name = str(name)       
      self._qual = qual  
      if copy:
         if not isinstance(name,str):
            self._name = '('+copy._name+')'
         if qual==None:
            self._qual = copy._qual

      # The nr of Clump nodes is defined by the list of qualifiers:
      if copy:
         self._quals = copy._quals
      elif quals==None:
         self._quals = range(3)                # for testing
      elif isinstance(quals,tuple):
         self._quals = list(quals)
      elif not isinstance(quals,list):         # assume Clump of one
         self._quals = [quals]                 #

      # Initialize the object history:
      self.history(clear=True)

      # Make sure that it has a nodescope (ns):
      self._ns = ns
      if copy:
         self._ns = copy._ns
      elif not ns:
         # If not supplied, make a local one.
         self._ns = NodeScope()

      # Make sure that it has an TDLOptionManager (TCM):
      self._TCM = TCM
      if copy:
         self._TCM = copy._TCM
      elif not self._TCM:
         # If not supplied, make a local one.
         self._TCM = TOM.TDLOptionManager(self._name)

      # Initialize with suitable nodes:
      if not copy:
         self._init()
         self._composed = False        # see .compose() and .decompose()

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
      for i,qual in enumerate(self._quals):
         node = stub(qual) << Meq.Constant(i)
         self._nodes.append(node)
      if trace:
         print self.show('.clear()')
      self.history('.init()', trace=trace)

      # The LAST statement:
      self._TCM.end_of_submenu()
      return True

   #-------------------------------------------------------------------------

   def copy (self, trace=False):
      """Return a copy of this clump.
      """
      new = Clump(copy=self)

      # Copy the nodes:
      self._nodes = []
      stub = self.nodestub()
      for i,qual in enumerate(self._quals):
         node = stub(qual) << Meq.Identity(self._nodes[i])
         new._node.append(node)
         
      # Copy state information:
      new._composed = self._composed

      self.history('.copy()', trace=trace)
      clump.history('.copy()', trace=trace)
      return clump


   #==========================================================================
   # Various text display functions:
   #==========================================================================

   def oneliner (self):
      ss = 'Clump: '+str(self._name)
      return ss

   #--------------------------------------------------------------------------

   def show (self, txt=None, full=True):
      """
      """
      ss = '\n'
      ss += '\n** '+self.oneliner()
      if txt:
         ss += '   ('+str(txt)+')'
      if self._TCM:
         ss += '\n * self._TCM: '+str(self._TCM.oneliner())
      ss += self.history(format=True, prefix=' | ')
      ss += '\n**\n'
      print ss
      return ss

   #-------------------------------------------------------------------------

   def history (self, append=None, clear=False,
                format=False, prefix='',
                show=False, trace=False):
      """Interact with the object history (a list of strings).
      """
      if clear:
         self._history = []
         s = '** Object history of: '
         s += str(type(self))+':'
         s += ' '+str(self._name)
         s += ' '+str(self._qual)
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
      if qual:
         stub = EN.unique_stub(self._ns, self._name, self._qual, qual)
      else:
         stub = EN.unique_stub(self._ns, self._name, self._qual)
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
      if True:
         print '.__getitem__(',index,') ->',str(self._nodes[index])
      return self._nodes[index]


   #=========================================================================
   # To and from tensor nodes:
   #=========================================================================

   def compose (self, trace=True):
      """Compose the Clump nodes into a single tensor node.
      See also .decompose()
      """
      if not self._composed:               # Only if in 'decomposed' state
         stub = self.nodestub('compose')
         node = stub << Meq.Composer(*self._nodes)
         self._nodes = [node]              # a list of a single node
         self._composed = True             # set the switch
         self.history('.compose()', trace=trace)
      return True

   #-------------------------------------------------------------------------

   def decompose (self, trace=True):
      """Decompose the single tensor node into separate nodes again.
      The reverse of .compose()
      """
      if self._composed:                   # ONLY if in 'composed' state
         tensor = self._nodes[0]
         self._nodes = []
         stub = self.nodestub('decompose')
         for index,qual in enumerate(self._quals):
            node = stub(qual) << Meq.Selector(tensor, index=index)
            self._nodes.append(node)
         self._composed = False            # set the switch
         self.history('.decompose()', trace=trace)
      return True

   #-------------------------------------------------------------------------

   #-------------------------------------------------------------------------

   #-------------------------------------------------------------------------

   #-------------------------------------------------------------------------


   #=========================================================================
   # Unops and binops:
   #=========================================================================

   def apply_unops (self, unops, trace=False):
      """
      Apply one or more unary operation(s) (e.g. MeqCos()) on its nodes.
      """
      # First condition the list of unary operations:
      if isinstance(unops,tuple):
         unops = list(unops)
      elif isinstance(unops,str):
         unops = [unops]

      # Then apply in order of specification:
      for unop in unops:
         stub = self.nodestub(unop)
         if self._composed:
            self._nodes[0] = stub('tensor') << getattr(Meq,unop)(self._nodes[0])
         else:
            for i,qual in enumerate(self._quals):
               self._nodes[i] = stub(qual) << getattr(Meq,unop)(self._nodes[i])
         self.history('.unops('+unop+')', trace=trace)

      return True

   #-------------------------------------------------------------------------


   def apply_binops (self, rhs=None, trace=False):
      """Apply zero or more unary operations (e.g. MeqCos()) on its nodes.
      """
      stub = self.nodestub()
      self.history('.binops()', trace=trace)

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
   if not enabled_testing:
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
enabled_testing = False
# enabled_testing = True        # normally, this statement will be commented out
if enabled_testing:
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
      cp = Clump('testing')
      cp.show('creation', full=True)
      if 1:
         for index in [0,1,-1,5]:
            print '-- cp[',index,'] -> ',cp[index]

   if 0:
      cp.apply_unops('Cos')
      cp.apply_binops()
            
   print '\n** End of standalone test of: Clump.py:\n' 

#=====================================================================================





