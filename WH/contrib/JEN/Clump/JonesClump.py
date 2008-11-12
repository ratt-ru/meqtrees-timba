"""
JonesClump.py: Base-class for an entire zoo of derived classes that
represent 2x2 Jones matrices (hhich describe instrumental effects)
"""

# file: ../JEN/Clump/JonesClump.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 11 nov 2008: creation (from templateLeafClump.py)
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
from Timba.Contrib.JEN.Clump import ParmClump
from Timba.Contrib.JEN.Clump import CorruptClump

import math                 # support math.cos() etc
# from math import *          # support cos() etc
# import numpy                # support numpy.cos() etc



#********************************************************************************
# JonesClump.JonesClump is the baseclass of all Jones Clumps, and the template
#********************************************************************************

class JonesClump(Clump.LeafClump):
   """
   Derived class
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class Clump.
      """
      Clump.LeafClump.__init__(self, clump=clump, **kwargs)
      return None


   #==========================================================================
   # The function .initexec() must be re-implemented for 'leaf' Clumps,
   # i.e. Clump classes that contain leaf nodes. An example is given below,
   # and may be canibalized for derived (leaf) Clump clases.
   #==========================================================================

   def initexec (self, **kwargs):
      """Fill the LeafClump object with suitable leaf nodes.
      Re-implemented version of the function in the baseclass (LeafClump).
      """
      treequals = range(8,10)+list('AB')          # default treequals (WSRT)
      dd = self.datadesc(complex=True, dims=[2,2],
                         treequals=kwargs.get('treequals', treequals))
      prompt = None
      help = 'define Jones matrix: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, prompt=prompt, help=help, **kwargs)

      self.add_option('elemtype',['amphas','realimag'])
      
      # Execute always (always=True) , to ensure that the leaf Clump has nodes!
      if self.execute_body(always=True):
         elemtype = self.getopt('elemtype')

         # Create ParmClumps:
         if elemtype=='amphas':
            gerrX = ParmClump.ParmClump(self, name='gerrX', default=1.0)
            perrX = ParmClump.ParmClump(self, name='perrX', default=0.0)
            gerrY = ParmClump.ParmClump(self, name='gerrY', default=1.0)
            perrY = ParmClump.ParmClump(self, name='perrY', default=0.0)
            self._ParmClumps.extend([gerrX,perrX,gerrY,perrY])
         elif elemtype=='realimag':
            rerrX = ParmClump.ParmClump(self, name='rerrX', default=1.0)
            ierrX = ParmClump.ParmClump(self, name='ierrX', default=0.0)
            rerrY = ParmClump.ParmClump(self, name='rerrY', default=1.0)
            ierrY = ParmClump.ParmClump(self, name='ierrY', default=0.0)
            self._ParmClumps.extend([rerrX,ierrX,rerrY,ierrY])

         # Generate nodes:
         self._nodes = []
         stub = self.unique_nodestub()
         for i,qual in enumerate(self._nodequals):
            elem00 = complex(1,0)
            elem01 = complex(0,0)
            elem10 = complex(0,0)
            elem11 = complex(1,0)
            if elemtype=='amphas':                
               elem00 = stub(qual)('00') << Meq.Polar(gerrX[i],perrX[i])
               elem11 = stub(qual)('11') << Meq.Polar(gerrY[i],perrY[i])
            elif elemtype=='realimag':
               elem00 = stub(qual)('00') << Meq.ToComplex(rerrX[i],ierrX[i])
               elem11 = stub(qual)('11') << Meq.ToComplex(rerrY[i],ierrY[i])
            node = stub(qual) << Meq.Matrix22(elem00, elem01,
                                              elem10, elem11)
            self._nodes.append(node)
         # Mandatory counterpart of self.execute_body()
         self.end_of_body(ctrl)

      # Mandatory counterpart of self.on_entry()
      return self.on_exit(ctrl)



#********************************************************************************
# JonesClump.XXXJones is a multiplication of Jones Clumps
#********************************************************************************

class XXXJones(JonesClump):
   """
   Baseclass for classes like WSRTJones, VLAJones etc.
   Just replace .initexec() with your own seqience of JonesClumps.
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class Clump.
      """
      JonesClump.__init__(self, clump=clump, **kwargs)
      return None


   #==========================================================================
   # The function .initexec() must be re-implemented for 'leaf' Clumps,
   # i.e. Clump classes that contain leaf nodes. An example is given below,
   # and may be canibalized for derived (leaf) Clump clases.
   #==========================================================================

   def initexec (self, **kwargs):
      """Fill the LeafClump object with suitable leaf nodes.
      Re-implemented version of the function in the baseclass (LeafClump).
      """
      treequals = range(8,10)+list('AB')          # default treequals (WSRT)
      dd = self.datadesc(complex=True, dims=[2,2],
                         treequals=kwargs.get('treequals', treequals))
      prompt = None
      help = 'define product of zero or more Jones matrices: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, prompt=prompt, help=help, **kwargs)

      self.add_option('AJones', True)
      self.add_option('BJones', True)
      self.add_option('CJones', True)

      if self.execute_body(always=True):
         jj = []
         if self.getopt('AJones'):
            jj.append(JonesClump(self, name='AJones'))
         if self.getopt('BJones'):
            jj.append(JonesClump(self, name='BJones'))
         if self.getopt('CJones'):
            jj.append(JonesClump(self, name='CJones'))

         self.make_single_jones(jj)
         self.end_of_body(ctrl)

      # Mandatory counterpart of self.on_entry()
      return self.on_exit(ctrl)


   #----------------------------------------------------------------------------

   def make_single_jones(self, jj):
      """Make a single Jones matrix from the ones collected in .initexex()
      """
      self._nodes = []
      if len(jj)==0:
         s = '** At least ONE JonesClump should be selected'
         raise ValueError,s

      elif len(jj)==1:
         # one only: copy its nodes
         for i,qual in enumerate(self._nodequals):
            self._nodes.append(jj[0][i])
      
      else:
         # more than one: MatrixMyultiply
         stub = self.unique_nodestub()
         for i,qual in enumerate(self._nodequals):
            cc = []
            for jones in jj:
               cc.append(jones[i])
            node = stub(qual) << Meq.MatrixMultiply(*cc)
            self._nodes.append(node)
         
      # Copy all the ParmClumps into a single list:
      for jones in jj:
         jones.show('make_single_jones()')
         self._ParmClumps.extend(jones._ParmClumps)
      return True
      


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
      if 1:
         clump = JonesClump(ns=ns, TCM=TCM,
                            trace=True)
      else:
         clump = XXXJones(ns=ns, TCM=TCM, trace=True)
         
      # clump = CorruptClump.AddNoise(clump).daisy_chain()
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
   print '** Start of standalone test of: JonesClump.py:'
   print '****************************************************\n' 

   ns = NodeScope()

   if 0:
      clump = JonesClump(trace=True)
   else:
      clump = XXXJones(trace=True)

   if 1:
      clump.show('creation', full=True)

   if 0:
      clump.compose()

   if 0:
      clump.show('final', full=True)

   
      
   print '\n** End of standalone test of: JonesClump.py:\n' 

#=====================================================================================





