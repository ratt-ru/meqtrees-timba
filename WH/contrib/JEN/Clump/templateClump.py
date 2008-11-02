"""
templateClump.py: Base-class for an entire zoo of derived classes that
represent 'clumps' of trees, i.e. sets of similar nodes.
Examples are ParmtemplateClump, JonestemplateClump and VistemplateClump.
"""

# file: ../JEN/Clump/templateClump.py:
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

from Timba.Contrib.JEN.Clump import Clump
# from Timba.Contrib.JEN.control import TDLOptionManager as TOM

import math                 # support math.cos() etc
# from math import *          # support cos() etc
# import numpy                # support numpy.cos() etc


#********************************************************************************
#********************************************************************************

class templateClump(Clump.Clump):
   """
   Derived class
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class Clump.
      """
      Clump.Clump.__init__(self, clump=clump, **kwargs)
      return None

   #-------------------------------------------------------------------------

   def show_specific(self):
      """
      Format the specific (non-generic) contents of the derived class.
      Re-implementation of function in baseclass Clump.
      """
      ss = '\n + Specific (derived class '+str(self._typename)+'):'
      ss += '\n + cc'
      ss += '\n + dd'
      return ss

   #-------------------------------------------------------------------------

   def newinstance(self, name=None, qual=None):
      """Reimplementation of placeholder function in base-class Clump.
      Make a new instance of this derived class (templateClump).
      """
      return templateClump(clump=self, name=name, qual=qual)


   #--------------------------------------------------------------------------
   # The function .make_leaf_nodes() must be re-implemented for 'leaf' Clumps,
   # i.e. Clump classes that contain leaf nodes. An example is given below,
   # and may be canibalized for derived (leaf) Clump clases.
   # However, this is not necessary for 'non-leaf' Clump classes, which read
   # their nodes from an input Clump. So just delete the re-implementation below.
   #--------------------------------------------------------------------------

   def make_leaf_nodes (self, **kwargs):
      """Fill the Clump object with nodes.
      Re-implemented version of the function in the baseclass (Clump).
      """
      kwargs['select'] = True     # Enforce menu if a user-choice is needed
      prompt = self._typename+' '+self._name
      help = 'make leaf nodes for: '+self.oneliner()
      ctrl = self.on_entry(self.init, prompt, help, **kwargs)
      
      self._TCM.add_option('initype', ['const_real','const_complex',
                                       'parm',
                                       'freq','time','freq+time'],
                           prompt='init node type')

      if self.execute_body():
         initype = self.getopt('initype')
         self._nodes = []
         stub = self.unique_nodestub()
         for i,qual in enumerate(self._nodequals):
            if initype=='parm':
               node = stub(qual) << Meq.Parm(i)
            elif initype=='freq':
               node = stub(qual) << Meq.Freq()
            elif initype=='time':
               node = stub(qual) << Meq.Time()
            elif initype=='freq+time':
               node = stub(qual) << Meq.Add(self._ns << Meq.Freq(),
                                            self._ns << Meq.Time())
            else:
               node = stub(qual) << Meq.Constant(i)
            self._nodes.append(node)
         # Mandatory counterpart of self.execute_body()
         self.end_of_body(ctrl)

      # Mandatory counterpart of self.on_entry()
      return self.on_exit(ctrl)



      
   #=========================================================================
   # Some example-functions (to be removed or canibalized):
   #=========================================================================

   def example1 (self, **kwargs):
      """
      Example1: A method without an explicit menu.
      """
      # kwargs['select'] = True          # optional: makes the function selectable     
      prompt = 'example1()'
      help = None
      ctrl = self.on_entry(self.example1, prompt, help, **kwargs)

      if self.execute_body():
         self._ns.example1 << Meq.Constant(1.9)
         # Generate some nodes:
         node1 = self._ns.example1_opt1 << Meq.Constant(1.1)
         node2 = self._ns.example1_opt2 << Meq.Constant(2.2)
         # Mandatory counterpart of self.execute_body()
         self.end_of_body(ctrl)

      # Mandatory counterpart of self.on_entry()
      return self.on_exit(ctrl)

   #--------------------------------------------------------------------

   def example2 (self, **kwargs):
      """
      Example2: A method with a menu and options
      """
      kwargs['select'] = True    # mandatory if it contains a menu.....!?                   
      prompt = 'example2()'
      help = None
      ctrl = self.on_entry(self.example2, prompt, help, **kwargs)

      self._TCM.add_option('opt1', range(3))
      self._TCM.add_option('opt2', range(3))

      if self.execute_body():
         # Read the option valies:
         opt1 = self.getopt('opt1')
         opt2 = self.getopt('opt2')
         # Generate some nodes:
         node1 = self._ns.example2_opt1 << Meq.Constant(opt1)
         node2 = self._ns.example2_opt2 << Meq.Constant(opt2)
         # Mandatory counterpart of self.execute_body()
         self.end_of_body(ctrl)

      # Mandatory counterpart of self.on_entry()
      return self.on_exit(ctrl)

   #--------------------------------------------------------------------

   def example3 (self, **kwargs):
      """
      Example3: Master-slaves
      """
      kwargs['select'] = False     # mandatory if it contains a menu.....!?                   
      prompt = 'example3()'
      help = None
      ctrl = self.on_entry(self.example3, prompt, help, **kwargs)

      self._TCM.add_option('slaves', range(3),
                           prompt='nr of slaved ojects')

      if self.execute_body():
         slaves = self.getopt('slaves')
         for i in range(slaves):
            cp = Clump('slave', qual=i,
                       master=ctrl['submenu'],
                       ns=self._ns, TCM=self._TCM)
         # Mandatory counterpart of self.execute_body()
         self.end_of_body(ctrl)

      # Mandatory counterpart of self.on_entry()
      return self.on_exit(ctrl)


#********************************************************************************
#********************************************************************************
# Standalone forest (i.e. not part of QuickRef.py) of this QR_module.
# Just load it into the browser, and compile/execute it.
#********************************************************************************
#********************************************************************************


def _define_forest (ns, **kwargs):
   """The expected function just calls do_define_forest() for its second pass.
   For the first pass, see elsewhere in this module.
   """
   if not enable_testing:
      print '\n**************************************************************'
      print '** templateClump: _define_forest(): testing not enabled yet!!'
      print '**************************************************************\n'
      return False

   # Remove any bookmarks that were generated in the first pass:
   Settings.forest_state.bookmarks = []

   # The second pass through do_define_forest():
   # NB: NO TDLOptions are generated after this pass.
   do_define_forest (ns, TCM=Clump.TOM.TDLOptionManager(TCM))       

   # Generate at least one node (just in case):
   node = ns.dummy << 1.0

   return True

#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the node 'rootnode'
    """
    # domain = meq.domain(1.0e8,1.1e8,1,10)                            # (f1,f2,t1,t2)
    domain = meq.domain(1,10,-10,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=11, num_time=21)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='rootnode', request=request))
    return result
       
#------------------------------------------------------------------------------


def do_define_forest (ns, TCM):
   """The function that does the actual work for _define_forest()
   It is used twice, outside and inside _define_forest() 
   """
   submenu = TCM.start_of_submenu(do_define_forest)
   TCM.add_option('opt1',[1,2,3])
   TCM.add_option('opt2',[1,2,3])

   if TCM.submenu_is_selected():
      cp = templateClump(ns=ns, TCM=TCM, trace=True)
      opt1 = TCM.getopt('opt1', submenu, trace=True)
      opt2 = TCM.getopt('opt2', submenu, trace=True)
      cp.example1(select=True)
      cp.example2(select=False)
      cp.example3()
      cp.inspector()
      cp.rootnode()
      # cp.show('do_define_forest', full=True)

   # The LAST statement:
   TCM.end_of_submenu()
   return True

#------------------------------------------------------------------------------

# This bit is executed whenever the module is imported (blue button etc)

itsTDLCompileMenu = None
TCM = Clump.TOM.TDLOptionManager(__file__)
enable_testing = False

# enable_testing = True        # normally, this statement will be commented out
if enable_testing:
   cp = do_define_forest (NodeScope(), TCM=TCM)
   itsTDLCompileMenu = TCM.TDLMenu(trace=False)

   

#********************************************************************************
#********************************************************************************
# Standalone test (without the browser):
#********************************************************************************
#********************************************************************************

if __name__ == '__main__':

   print '\n****************************************************'
   print '** Start of standalone test of: templateClump.py:'
   print '****************************************************\n' 

   ns = NodeScope()

   if 1:
      tc = templateClump()
      tc.show('creation', full=True)

   if 1:
      tc.compose()

   if 1:
      tc.show('final', full=True)

   
      
   print '\n** End of standalone test of: templateClump.py:\n' 

#=====================================================================================





