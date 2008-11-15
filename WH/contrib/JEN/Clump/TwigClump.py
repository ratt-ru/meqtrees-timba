"""
TwigClump.py: Make (one-tree?) Clumps from EasyTwigs 
"""

# file: ../JEN/Clump/TwigClump.py:
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
from Timba.Contrib.JEN.Clump import ParmClump
from Timba.Contrib.JEN.Easy import EasyTwig as ET

import math                 # support math.cos() etc
# from math import *          # support cos() etc
# import numpy                # support numpy.cos() etc



#********************************************************************************
# Class Twig:
#********************************************************************************

class Twig(Clump.LeafClump):
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
      dd = self.datadesc(treequals=['twig']),

      help = 'make twig (leaf) node for: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, help=help, **kwargs)
      
      self.add_option('twig', ET.twig_names(first='t'),
                      prompt='EasyTwig')

      # Execute always (always=True) , to ensure that the leaf Clump has nodes!
      if self.execute_body(always=True):           
         twig = self.getopt('twig')
         self._nodes = []
         # stub = self.unique_nodestub(twig)
         for i,qual in enumerate(self._nodequals):
            node = ET.twig(self._ns, twig)
            self._nodes.append(node)
         self.visualize()
         self.end_of_body(ctrl)

      # Mandatory counterpart of self.on_entry()
      return self.on_exit(ctrl)



 #********************************************************************************
# Class Polynomial:
#********************************************************************************

class Polynomial(Clump.LeafClump):
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
      dd = self.datadesc(treequals=['polytwig'])

      prompt = None
      help = 'make polynomial twig (leaf) node for: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, prompt=prompt, help=help, **kwargs)

      choice = ['f','t','ft','f2','t2','f2t','ft2','f2t2']
      self.add_option('poly', choice,
                      prompt='EasyTwig.polyparm')

      # Execute always (always=True) , to ensure that the leaf Clump has nodes!
      if self.execute_body(always=True):           
         poly = self.getopt('poly')
         self._nodes = []
         for i,qual in enumerate(self._nodequals):
            node = ET.twig(self._ns, 'polyparm_'+poly)
            self._nodes.append(node)

         # Make a ParmClump object from its MeqParms: 
         parms = self._ns.Search(tags='polyparm')
         for parm in parms:
            self.history('--> parm: '+str(parm))
         plc = ParmClump.ParmListClump(parms,
                                       ns=self._ns, TCM=self._TCM,
                                       name='polyparm')
         self._ParmClumps = [plc]

         self.visualize()
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
   TCM.add_option('class',['TwigClump','Polynomial'],
                  prompt='test TwigClump class')
   
   clump = None
   if TCM.submenu_is_selected():
      test_class = TCM.getopt('class', submenu)
      if test_class=='Polynomial':
         clump = Polynomial(ns=ns, TCM=TCM, trace=True)
      else:
         clump = Twig(ns=ns, TCM=TCM, trace=True)

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
   print '** Start of standalone test of: TwigClump.py:'
   print '****************************************************\n' 

   ns = NodeScope()

   if 0:
      clump = Twig(twig='f+t', trace=True)

   if 1:
      clump = Polynomial(poly='f2', trace=True)

   if 1:
      clump.show('creation', full=True)

   if 0:
      clump.compose()

   if 0:
      clump.show('final', full=True)

   
      
   print '\n** End of standalone test of: TwigClump.py:\n' 

#=====================================================================================





