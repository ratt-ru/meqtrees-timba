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

   def __init__(self, name=None,
                qual=None, kwqual=None,
                treequals=None,
                ns=None, TCM=None,
                use=None, init=True,
                **kwargs):
      """
      Derived from class Clump.
      """
      Clump.Clump.__init__(self, name=name,
                           qual=qual, kwqual=kwqual,
                           treequals=treequals,
                           ns=ns, TCM=TCM,
                           use=use, init=init,
                           **kwargs)
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

   def newinstance(self, name=None, qual=None, init=False):
      """Reimplementation of placeholder function in base-class Clump.
      Make a new instance of this derived class (templateClump).
      """
      return templateClump(name=name, qual=qual, use=self, init=init)

   #--------------------------------------------------------------------------

   def init (self, trace=False):
      """Reimplementation of placeholder function in Clump.
      Initialize the object with suitable nodes.
      Called from __init__() only
      """
      submenu = self.start_of_object_submenu()
      self._TCM.add_option('opt1', range(1,4))
      self._TCM.add_option('opt2', range(1,4))

      self._TCM.getopt('opt1', submenu)
      self._TCM.getopt('opt2', submenu)
      
      self._nodes = []
      stub = self.unique_nodestub()
      for i,qual in enumerate(self._nodequals):
         node = stub(qual) << Meq.Parm(i)
         self._nodes.append(node)

      self.history('.init()', trace=trace)

      # The LAST statement:
      self.end_of_object_submenu()
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
      print '** templateClump: _define_forest(): testing not enabled yet!!'
      print '**************************************************************\n'
      return False

   # Execute the function that does the actual work. It is the same
   # function that was called outside _define_forest(), where the
   # TDLOptions/Menus were configured (in TCM) and generated.
   # This second run uses the existing option values, which are
   # transferred by means of diskfiles (.TCM and .TRM)
   # It also re-defines the options/menus in a dummy TDLOptionManager,
   # but these are NOT converted into TDLOption/Menu objects. 

   do_define_forest (ns, TCM=Clump.TOM.TDLOptionManager(TCM))       

   # Generate at least one node:
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
   TCM.add_option('opt',[1,2,3])

   if TCM.submenu_is_selected():
      cp = templateClump(ns=ns, TCM=TCM)
      cp.show('do_define_forest', full=True)
      opt = TCM.getopt('opt', submenu, trace=True)
      if opt==1:
         ns.testopt1 << 1.0
      elif opt==2:
         ns.testopt2 << 2.0
      elif opt==3:
         ns.testopt1 << 3.0
         ns.testopt2 << 3.0
      else:
         # Define at least one node
         ns.do_define_forest << 1.0
      cp.inspector()
      cp.rootnode()

   # The LAST statement:
   TCM.end_of_submenu()
   return True

#------------------------------------------------------------------------------

# This bit is executed whenever the module is imported (blue button etc)

itsTDLCompileMenu = None
TCM = Clump.TOM.TDLOptionManager(__file__)
enable_testing = False

enable_testing = True        # normally, this statement will be commented out
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





