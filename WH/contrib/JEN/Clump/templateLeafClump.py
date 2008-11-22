"""
templateLeafClump.py: Base-class for an entire zoo of derived classes that
represent Clumps in which the nodes are leaf nodes.
Examples are ParmClump, JonesClump and SpigotClump.
"""

# file: ../JEN/Clump/templateLeafClump.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 11 nov 2008: creation (from template_LeafClump.py)
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

class templateLeafClump(Clump.LeafClump):
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
      # The data-description may be defined by means of kwargs: 
      treequals = range(3)           # default list of tree qualifiers
      dd = self.datadesc(complex=kwargs.get('complex',False),
                         treequals=kwargs.get('treequals',treequals),
                         dims=kwargs.get('dims',[1]))

      help = 'make leaf nodes for: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, help=help, **kwargs)
      
      self.add_option('leaftype', ['const_real','const_complex',
                                   'parm',
                                   'freq','time','freq+time'],
                      prompt='leaf node type')

      # Execute always (always=True) , to ensure that the leaf Clump has nodes!
      if self.execute_body(always=True):           
         leaftype = self.getopt('leaftype')
         stub = self.unique_nodestub(leaftype)
         for i,qual in enumerate(self.nodequals()):
            if leaftype=='parm':
               self[i] = stub(qual) << Meq.Parm(i)
            elif leaftype=='freq':
               self[i] = stub(qual) << Meq.Freq()
            elif leaftype=='time':
               self[i] = stub(qual) << Meq.Time()
            elif leaftype=='freq+time':
               self[i] = stub(qual) << Meq.Add(self.ns() << Meq.Freq(),
                                            self.ns() << Meq.Time())
            else:
               self[i] = stub(qual) << Meq.Constant(i)
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
      clump = templateLeafClump(ns=ns, TCM=TCM,
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
   print '** Start of standalone test of: templateLeafClump.py:'
   print '****************************************************\n' 

   ns = NodeScope()

   if 0:
      clump = templateLeafClump(trace=True)
   else:
      tqs = range(10) + list('ABCD')
      clump = templateLeafClump(treequals=tqs,
                                name='test',
                                trace=True)

   if 1:
      clump.show('creation', full=True)

   if 0:
      clump.compose()

   if 0:
      clump.show('final', full=True)

   
      
   print '\n** End of standalone test of: templateLeafClump.py:\n' 

#=====================================================================================





