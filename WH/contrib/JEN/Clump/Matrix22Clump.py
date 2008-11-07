"""
Matrix22Clump.py: Base-class Clump classes that deal with 2x2 matrices
e.g. Jones matrices and cohaerency matrices
"""

# file: ../JEN/Clump/Matrix22Clump.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 07 nov 2008: creation (from templateLeafClump.py)
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

class Matrix22Clump(Clump.LeafClump):
   """
   Derived class
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class LeafClump.
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
      Make a new instance of this derived class (Matrix22Clump).
      """
      return Matrix22Clump(clump=self, **kwargs)


   #==========================================================================
   # The function .initexec() must be re-implemented for 'leaf' Clumps,
   # i.e. Clump classes that contain leaf nodes. An example is given below,
   # and may be canibalized for derived (leaf) Clump clases.
   #==========================================================================

   def initexec (self, **kwargs):
      """
      Fill the LeafClump object with suitable leaf nodes.
      Re-implemented version of the function in the baseclass (LeafClump).
      """
      help = 'make leaf nodes for: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, help=help, **kwargs)
      
      # Execute always (always=True) , to ensure that the leaf Clump has nodes!
      if self.execute_body(always=True):           
         self._nodes = []
         stub = self.unique_nodestub()
         for i,qual in enumerate(self._nodequals):
            node = stub(qual) << Meq.Matrix22(complex(1.0,0.0),
                                              complex(0.0,0.0),
                                              complex(0.0,0.0),
                                              complex(1.0,0.0))
            self._nodes.append(node)
         # Mandatory counterpart of self.execute_body()
         self.end_of_body(ctrl)

      # Mandatory counterpart of self.on_entry()
      return self.on_exit(ctrl)



   #=========================================================================
   #=========================================================================

   def add_noise (self, **kwargs):
      """
      Add Gaussian noise with the specified stddev.
      """
      prompt = '.add_noise()'
      help = 'Add Gaussian noise'
      ctrl = self.on_entry(self.add_noise, prompt, help, **kwargs)

      self._TCM.add_option('stddev', [0.001,0.01,0.1,1.0,10.0,0.0])
      self._TCM.add_option('unops', [None,'Exp',['Exp','Exp']], more=False)

      if self.execute_body():
         stddev = self.getopt('stddev')
         unops = self.getopt('unops')
         if stddev>0.0:
            stub = self.unique_nodestub('add_noise','stddev='+str(stddev))
            for i,qual in enumerate(self._nodequals):
               cc = []
               for elem in ['00','10','01','11']:
                  real = stub('real')(qual)(elem) << Meq.GaussNoise(stddev=stddev)
                  imag = stub('imag')(qual)(elem) << Meq.GaussNoise(stddev=stddev)
                  noise = stub('noise')(qual)(elem) << Meq.ToComplex(real,imag)
                  cc.append(noise)
               noise = stub('noise')(qual) << Meq.Matrix22(*cc)
               self._nodes[i] = stub(qual) << Meq.Add(self._nodes[i],noise)
            if unops:
               self.apply_unops(unops=unops)
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
   submenu = TCM.start_of_submenu(do_define_forest,
                                  prompt=__file__.split('/')[-1],
                                  help=__file__)
   clump = None
   if TCM.submenu_is_selected():
      clump = Matrix22Clump(ns=ns, TCM=TCM,
                            name='GJones',
                            treequals=range(10)+list('ABCD'),         # WSRT
                            trace=True)
      clump.add_noise(select=True)
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
   print '** Start of standalone test of: Matrix22Clump.py:'
   print '****************************************************\n' 

   ns = NodeScope()

   if 0:
      clump = Matrix22Clump(trace=True)
   else:
      tqs = range(10) + list('ABCD')
      clump = Matrix22Clump(treequals=tqs,
                            name='GJones',
                            trace=True)

      clump = Matrix22Clump(treequals=tqs, trace=True)

   if 1:
      clump.show('creation', full=True)

   if 0:
      clump.compose()

   if 0:
      clump.show('final', full=True)

   
      
   print '\n** End of standalone test of: Matrix22Clump.py:\n' 

#=====================================================================================





