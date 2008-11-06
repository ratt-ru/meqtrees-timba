"""
templateClump.py: Base-class for an entire zoo of derived classes that
represent Clumps in which the nodes are leaf nodes.
Examples are ParmClump, JonesClump and SpigotClump.
"""

# file: ../JEN/Clump/templateClump.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 03 nov 2008: creation (from templateClump.py)
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

import math                 # support math.cos() etc
# from math import *          # support cos() etc
# import numpy                # support numpy.cos() etc


#********************************************************************************
#********************************************************************************

class templateClump(Clump.LeafClump):
   """
   Derived class
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class Clump.
      """
      Clump.LeafClump.__init__(self, clump=clump, **kwargs)
      return None

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
      """
      return templateClump(clump=self, **kwargs)


   #=========================================================================
   # Re-implementation of its initexec function (called from Clump.__init__())
   #=========================================================================

   def initexec (self, **kwargs):
      """Re-implementation of the place-holder function in class Clump.
      It is itself a place-holder, to be re-implemented in derived classes.
      This function is called in Clump.__init__().
      """
      # kwargs['select'] = True          # optional: makes the function selectable     
      prompt = 'prompt'
      help = 'help'
      ctrl = self.on_entry(self.initexec, prompt, help, **kwargs)

      if self.execute_body():
         self._ns.example1 << Meq.Constant(1.9)
         # Generate some nodes:
         node1 = self._ns.example1_opt1 << Meq.Constant(1.1)
         node2 = self._ns.example1_opt2 << Meq.Constant(2.2)
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
# Function called from _define_forest() in ClumpExec.py
#********************************************************************************
#********************************************************************************

def do_define_forest (ns, TCM):
   """
   Testing function for the class(es) in this module.
   It is called by ClumpExec.py
   """
   submenu = TCM.start_of_submenu(do_define_forest)
   TCM.add_option('opt1',[1,2,3])
   TCM.add_option('opt2',[1,2,3])

   cp = None
   if TCM.submenu_is_selected():
      cp = Clump.LeafClump(ns=ns, TCM=TCM, trace=True)
      cp = templateClump(cp, trace=True)
      opt1 = TCM.getopt('opt1', submenu, trace=True)
      opt2 = TCM.getopt('opt2', submenu, trace=True)
      cp.example1(select=True)
      cp.example2(select=False)
      cp.example3()
      cp.inspector()

   # The LAST statement:
   TCM.end_of_submenu()
   return cp

   




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
      cp = Clump.LeafClump(trace=True)
      cp = templateClump(cp, trace=True)
      cp.show('creation', full=True)

   if 0:
      cp.compose()

   if 0:
      cp.show('final', full=True)

   
      
   print '\n** End of standalone test of: templateClump.py:\n' 

#=====================================================================================





