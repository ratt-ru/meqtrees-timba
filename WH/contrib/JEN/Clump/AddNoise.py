"""
AddNoise.py: Add various types of noise to Clump tree nodes.

"""

# file: ../JEN/Clump/AddNoise.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 80 nov 2008: creation (from templateClump.py)
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

class AddNoise(Clump.Clump):
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
      return ss

   #-------------------------------------------------------------------------

   def newinstance(self, **kwargs):
      """Reimplementation of placeholder function in base-class Clump.
      Make a new instance of this derived class (AddNoise).
      """
      return AddNoise(clump=self, **kwargs)


   #==========================================================================
   # The function .initexec() must be re-implemented for 'leaf' Clumps,
   # i.e. Clump classes that contain leaf nodes. An example is given below,
   # and may be canibalized for derived (leaf) Clump clases.
   #==========================================================================

   def initexec (self, **kwargs):
      """
      Add Gaussian noise with the specified stddev.
      """
      prompt = '.add_noise()'
      help = 'Add Gaussian noise'
      ctrl = self.on_entry(self.add_noise, prompt, help, **kwargs)

      dd = self._datadesc                 # data description record
      if dd['complex']:
         pass
      

      self._TCM.add_option('stddev', [0.001,0.01,0.1,1.0,10.0,0.0])
      self._TCM.add_option('unops', [None,'Exp',['Exp','Exp']], more=False)

      if self.execute_body():

         if dd['complex']:
            pass

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
      clump = Clump.LeafClump(trace=True)
      clump = AddNoise(clump, select=True, trace=True)
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
   print '** Start of standalone test of: AddNoise.py:'
   print '****************************************************\n' 

   ns = NodeScope()

   if 0:
      tqs = range(10) + list('ABCD')
      clump = Clump.LeafClump(trace=True)
      clump = AddNoise(clump, trace=True)
      clump.show('creation', full=True)

   if 0:
      clump.compose()

   if 0:
      clump.show('final', full=True)

   
      
   print '\n** End of standalone test of: AddNoise.py:\n' 

#=====================================================================================





