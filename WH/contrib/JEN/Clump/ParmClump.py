"""
ParmClump.py: A Clump of MeqParms, e.g. Ggain:0...D
"""

# file: ../JEN/Clump/ParmClump.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 07 nov 2008: creation (from templateClump.py)
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

class ParmClump(Clump.LeafClump):
   """
   Derived class
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class Clump.
      """
      self._default = kwargs.get('default',0.0)
      Clump.LeafClump.__init__(self, clump=clump, **kwargs)
      return None

   #-------------------------------------------------------------------------

   def show_specific(self):
      """
      Format the specific (non-generic) contents of the derived class.
      Re-implementation of function in baseclass Clump.
      """
      ss = '\n + Specific (derived class '+str(self._typename)+'):'
      ss += '\n + self._default = '+str(self._default)
      ss += '\n + self._solvable = '+str(self._solvable)
      return ss

   #-------------------------------------------------------------------------

   def newinstance(self, **kwargs):
      """Reimplementation of placeholder function in base-class Clump.
      Make a new instance of this derived class (ParmClump).
      """
      return ParmClump(clump=self, **kwargs)


   #==========================================================================
   # The function .initexec() must be re-implemented for 'leaf' Clumps,
   # i.e. Clump classes that contain leaf nodes. An example is given below,
   # and may be canibalized for derived (leaf) Clump clases.
   #==========================================================================

   def initexec (self, **kwargs):
      """Fill the LeafClump object with suitable leaf nodes.
      Re-implemented version of the function in the baseclass (LeafClump).
      """
      help = 'definition of a set of similar MeqParms: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, help=help, **kwargs)
      
      self._TCM.add_option('fdeg', range(6),
                           help='freq deg of polc',
                           prompt='freq deg')
      self._TCM.add_option('tdeg', range(6),
                           help='time deg of polc',
                           prompt='time deg')

      self._TCM.add_option('nftile', [None,1,2,3,4,5,10], more=int,
                           help="size (freq-cells) of solving subtile")
      self._TCM.add_option('nttile', [None,1,2,3,4,5,10], more=int,
                           help="size (time-cells) of solving subtile")

      self._TCM.add_option('solvable', False,
                           prompt='solvable')
      
      self._TCM.add_option('use_previous', True, hide=True,
                           help='if True, use the previous solution',
                           prompt='use_previous')
      self._TCM.add_option('mepfile', [None,'test.mep'], more=str, hide=True,
                           help='name of the file that contains the parmtable',
                           prompt='.mep file')

      # Execute always (always=True) , to ensure that the leaf Clump has nodes!
      if self.execute_body(always=True):           

         tdeg = self.getopt('tdeg')
         fdeg = self.getopt('fdeg')
         mepfile = self.getopt('mepfile')
         use_previous = self.getopt('use_previous')
         nt = self.getopt('nttile')
         nf = self.getopt('nftile')
         tiling = record(freq=nf, time=nt)

         # See .__init__()
         default = self._default   

         # See self.solvable_parms()
         self._solvable = self.getopt('solvable')

         self._nodes = []
         self._parmnames = []
         stub = self.unique_nodestub()
         for i,qual in enumerate(self._nodequals):
            node = stub(qual) << Meq.Parm(default,
                                          shape=[tdeg+1,fdeg+1],
                                          tiling=tiling,
                                          table_name=mepfile,
                                          use_previous=use_previous,
                                          # tags=['tag1','tag2'],
                                          node_groups='Parm')
            self._nodes.append(node)
            self._parmnames.append(node.name)
            # print '\n -',str(node),' initrec: ',node.initrec()

         # Mandatory counterpart of self.execute_body()
         self.end_of_body(ctrl)

      # Mandatory counterpart of self.on_entry()
      return self.on_exit(ctrl)


   #============================================================================

   def solvable_parms (self, trace=False):
      """
      Re-implementation of the Clump placeholder function.
      If solvable: Return a list of solvable parm-names.
      Otherwise, return an empty list.
      """
      # trace = True
      # self._solvable = True                    # for testing
      result = []
      if self._solvable:
         result = self._parmnames
      if trace:
         print '\n ** .solvable_parms(): '+str(self._solvable)+','+str(len(result))+'/'+str(self.size())+':'
         if result: print '    ->',result
      return result





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
   submenu = TCM.start_of_submenu(do_define_forest,
                                  prompt=__file__.split('/')[-1],
                                  help=__file__)
   clump = None
   if TCM.submenu_is_selected():
      clump = ParmClump(ns=ns, TCM=TCM,
                        name='GgainY', default=2.3,
                        treequals=range(10)+list('ABCD'),         # WSRT
                        trace=True)
      clump.visualize()

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
   print '** Start of standalone test of: ParmClump.py:'
   print '****************************************************\n' 

   ns = NodeScope()

   if 0:
      clump = ParmClump(trace=True)
   else:
      tqs = range(10) + list('ABCD')
      clump = ParmClump(treequals=tqs,
                        name='GgainX',
                        default=1.0,
                        trace=True)

   if 1:
      clump.solvable_parms(trace=True)

   if 1:
      clump.show('creation', full=True)

   if 0:
      clump.compose()

   if 0:
      clump.show('final', full=True)

   
      
   print '\n** End of standalone test of: ParmClump.py:\n' 

#=====================================================================================





