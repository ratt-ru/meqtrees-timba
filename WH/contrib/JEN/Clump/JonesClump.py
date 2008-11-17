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
      Derived from class LeafClump.
      """
      # This should be in every JonesClump class:
      self.datadesc(complex=True, dims=[2,2])

      # This bit is instrument-specific:
      treequals = range(8,10)+list('AB')          # default treequals (WSRT)
      treequals = ['RT8','RT9','RTA','RTB']       # default treequals (WSRT)
      self.datadesc(treequals=kwargs.get('treequals', treequals))

      # This needs a little thought...:
      rr = dict()
      for key in ['use_previous','table_name']:
         rr['use_previous'] = kwargs.get('use_previous', True)
      self._MeqParm_parms = rr
      Clump.LeafClump.__init__(self, clump=clump, **kwargs)
      return None

   #-------------------------------------------------------------------------

   def show_specific(self):
      """
      Format the specific (non-generic) contents of the class.
      Placeholder for re-implementation in derived class.
      """
      ss = '\n + Specific (derived class '+str(self._typename)+'):'
      ss += '\n + self._MeqParm_parms: '
      rr = self._MeqParm_parms
      for key in rr.keys():
         ss += '\n   - '+str(key)+' = '+str(rr[key])
      return ss

   #==========================================================================
   # The function .initexec() must be re-implemented for 'leaf' Clumps,
   # i.e. Clump classes that contain leaf nodes. An example is given below,
   # and may be canibalized for derived (leaf) Clump clases.
   #==========================================================================

   def initexec (self, **kwargs):
      """Fill the LeafClump object with suitable leaf nodes.
      Re-implemented version of the function in the baseclass (LeafClump).
      """
      prompt = 'Jones: '+self._name
      help = 'define Jones matrix: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, prompt=prompt, help=help, **kwargs)

      self.add_option('mode',['amphas','realimag'])

      # Execute always (always=True) , to ensure that the leaf Clump has nodes!
      # if self.execute_body(always=True):
      if self.execute_body():
         mode = self.getopt('mode')

         # Create ParmClumps:
         if mode=='amphas':
            gerrX = self.ParmClump(name='gerrX', default=1.0)
            perrX = self.ParmClump(name='perrX', default=0.0)
            gerrY = self.ParmClump(name='gerrY', default=1.0)
            perrY = self.ParmClump(name='perrY', default=0.0)
         elif mode=='realimag':
            rerrX = self.ParmClump(name='rerrX', default=1.0)
            ierrX = self.ParmClump(name='ierrX', default=0.0)
            rerrY = self.ParmClump(name='rerrY', default=1.0)
            ierrY = self.ParmClump(name='ierrY', default=0.0)

         # Generate nodes:
         self._nodes = []
         stub = self.unique_nodestub()
         for i,qual in enumerate(self._nodequals):
            elem00 = complex(1,0)
            elem01 = complex(0,0)
            elem10 = complex(0,0)
            elem11 = complex(1,0)
            if mode=='amphas':                
               elem00 = stub(qual)('00') << Meq.Polar(gerrX[i],perrX[i])
               elem11 = stub(qual)('11') << Meq.Polar(gerrY[i],perrY[i])
            elif mode=='realimag':
               elem00 = stub(qual)('00') << Meq.ToComplex(rerrX[i],ierrX[i])
               elem11 = stub(qual)('11') << Meq.ToComplex(rerrY[i],ierrY[i])
            node = stub(qual) << Meq.Matrix22(elem00, elem01,
                                              elem10, elem11)
            self._nodes.append(node)
         # Mandatory counterpart of self.execute_body()
         self.end_of_body(ctrl)

      # Mandatory counterpart of self.on_entry()
      return self.on_exit(ctrl)

   #--------------------------------------------------------------------------
   #--------------------------------------------------------------------------

   def ParmClump(self, name, default=0.0):
      """Helper function to create a ParmClump in an organised way.
      """
      clump = ParmClump.ParmClump(self, name=name,
                                  default=default,
                                  hide=True,
                                  **self._MeqParm_parms)
      # self._ParmClumps.append(clump)
      self.connect_grafted_clump(clump)
      return clump



#********************************************************************************
# JonesClump.XXXJones is a multiplication of Jones Clumps
#********************************************************************************

class XXXJones(JonesClump):
   """
   Baseclass for classes like WSRTJones, VLAJones etc.
   Just replace .initexec() with your own sequence of JonesClumps.
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
      To be re-implemented in instrument-specific XXXJones classes.
      """
      prompt = 'Jones: '+str(self._name)
      help = """Specify a sequence (product) of zero or more Jones matrices.
      If zero are selected, a placeholder 2x2 (constant) unit-matrix is used.
      """
      ctrl = self.on_entry(self.initexec, prompt=prompt, help=help, **kwargs)

      self.add_option('use_previous', True,
                      hide=True,
                      help='if True, use the previous solution',
                      prompt='use_previous')
      self.add_option('table_name', [None,'test.mep'], more=str,
                      hide=True,
                      help='name of the file that contains the parmtable',
                      prompt='.mep file')
      
      if self.execute_body(always=True):
         for key in ['use_previous','table_name']:
            self._MeqParm_parms[key] = self.getopt(key)
         treequals = range(8,10)+list('AB')          # default treequals (WSRT)
         self.datadesc(treequals=kwargs.get('treequals', treequals))
         jj = []
         notsel = []
         JonesClump(self, name='AJones').append_if_selected(jj, notsel)
         JonesClump(self, name='BJones').append_if_selected(jj, notsel)
         JonesClump(self, name='CJones').append_if_selected(jj, notsel)
         self.make_single_jones(jj, notsel)
         self.end_of_body(ctrl)

      # Mandatory counterpart of self.on_entry()
      return self.on_exit(ctrl)


   #----------------------------------------------------------------------------
   #----------------------------------------------------------------------------

   def make_single_jones(self, jj, notsel=None):
      """Make a single Jones matrix from the ones collected in .initexex()
      This function is generic, i.e. it should NOT be re-implemented in
      classes that are derived from XXXJones. It contains more specialist code,
      which should not be seen by the uninitiated.
      """
      
      self._nodes = []
      if len(jj)==0:
         self.history('empty Jones list: make a 2x2 complex unit matrix')
         stub = self.unique_nodestub('unitmatrix')
         for i,qual in enumerate(self._nodequals):
            node = stub(qual) << Meq.Matrix22(complex(1,0), complex(0,0),
                                              complex(0,0), complex(1,0))
            self._nodes.append(node)

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
         
      # Connect orphans, stubtree etc, and add the ParmClumps to
      # its own list of ParmClumps (self._ParmClumps).
      for jones in jj:
         # self.history('include Jones: '+jones.oneliner())
         # jones.show('make_single_jones()')
         self.connect_grafted_clump(jones)

      # Deal with the Jones matrices that were NOT selected:
      if isinstance(notsel,list):
         for jones in notsel:
            # print '- not selected:',jones.oneliner()
            jones.connect_loose_ends (self, full=False)
            

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
      if 0:
         clump = JonesClump(ns=ns, TCM=TCM)
      else:
         clump = XXXJones(ns=ns, TCM=TCM)
         
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





