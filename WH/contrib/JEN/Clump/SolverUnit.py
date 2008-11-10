"""
SolverUnit.py: A processing unit with a MeqSolver
"""

# file: ../JEN/Clump/SolverUnit.py:
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
from Timba.Contrib.JEN.Clump import ParmClump
from Timba.Contrib.JEN.Clump import TwigClump

import Meow.Bookmarks
from Timba.Contrib.JEN.util import JEN_bookmarks

import math                 # support math.cos() etc
# from math import *          # support cos() etc
# import numpy                # support numpy.cos() etc


#********************************************************************************
#********************************************************************************

class SolverUnit(Clump.Clump):
   """
   A processing unit with a MeqSolver
   """

   def __init__(self, clump=None, other=None, **kwargs):
      """
      Derived from class Clump. The required inputs are two Clumps,
      representing 'Measured' and 'Predicted' (in some order),
      whose tree nodes provide the inputs for the Condeq(s). 
      """
      self._other = other
      self._solver = None
      Clump.Clump.__init__(self, clump=clump, **kwargs)
      return None

   #-------------------------------------------------------------------------

   def show_specific(self):
      """
      Format the specific (non-generic) contents of the derived class.
      Re-implementation of function in baseclass Clump.
      """
      ss = '\n + Specific (derived class '+str(self._typename)+'):'
      ss += '\n + other = '+other.oneliner()
      ss += '\n + self._solver = '+str(self._solver)
      return ss


   #=========================================================================
   # Re-implementation of its initexec function (called from Clump.__init__())
   #=========================================================================

   def initexec (self, **kwargs):
      """
      Implement the solver tree.
      """
      kwargs['select'] = True          # optional: makes the function selectable     
      ctrl = self.on_entry(self.initexec, **kwargs)

      self.add_option('num_iter',[3,5,10,20,1,2],
                      help='(max) nr of solver iterations')

      solver = None
      if self.execute_body():
         num_iter = self.getopt('num_iter')
         
         stub = self.unique_nodestub()
         condeqs = []
         # print self._other.oneliner()
         for i,qual in enumerate(self._nodequals):
            node = stub('condeq')(qual) << Meq.Condeq(self[i],
                                                      self._other[i]) 
            self._nodes[i] = node
            condeqs.append(node)

         solvable = self.solvable_parms()
         solvable.extend(self._other.solvable_parms())
         solver = stub('solver') << Meq.Solver(children=condeqs,
                                               num_iter=num_iter,
                                               solvable=solvable)
         self._solver = solver
         # Insert ReqSeq node(s) in the trees of the input clump.
         # These will issue a request first to the solver,
         # but pass on the result of the trees.
         self._input_clump.insert_reqseqs(solver)
         ## self._orphans.append(solver)               # alternative...?

         # Mandatory counterpart of self.execute_body()
         self.end_of_body(ctrl)

      # Mandatory counterpart of self.on_entry()
      return self.on_exit(ctrl, result=solver)


   #======================================================================
   # Visualization:
   #======================================================================
      
   def visualize (self, **kwargs):
      """Choice of various forms of visualization.
      Reimplementation of Clump function.
      """
      kwargs['select'] = True
      bookpage = kwargs.get('bookpage', None)
      folder = kwargs.get('folder', None)

      prompt = '.visualize()'
      help = 'Select various forms of SolverUnit (Clump) visualization'
      print '\n**',help,'\n'
      ctrl = self.on_entry(self.visualize, prompt, help, **kwargs)

      if self.execute_body():
         self.inspector(**kwargs)
         self.plot_node_results(**kwargs)
         self.plot_node_family(**kwargs)
         self.plot_node_bundle(**kwargs)
         self.plot_solver(**kwargs)
         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl)


   #---------------------------------------------------------------------

   def plot_solver (self, **kwargs):
      """Plot the result of its solver node, and make a bookmark.
      """
      kwargs['select'] = True
      bookpage = kwargs.get('bookpage', None)
      folder = kwargs.get('folder', None)

      prompt = '.plot_solver()'
      help = 'make a plot (Result Plotter) of its solver node'
      print '\n**',help,'\n'
      ctrl = self.on_entry(self.plot_solver, prompt, help, **kwargs)

      if self.execute_body():
         if is_node(self._solver):
            JEN_bookmarks.create(self._solver, name=bookpage, folder=folder)
         else:
            self.history('self._solver is not a node, but: '+str(self._solver))
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
      # clump = Clump.LeafClump(ns=ns, TCM=TCM, trace=True)
      clump = TwigClump.Twig(ns=ns, TCM=TCM, trace=True)
      other = ParmClump.ParmClump(clump, trace=True)
      su = SolverUnit(clump, other, trace=True)
      su.visualize()

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
   print '** Start of standalone test of: SolverUnit.py:'
   print '****************************************************\n' 

   ns = NodeScope()

   if 1:
      # clump = Clump.LeafClump(trace=True)
      clump = TwigClump.Twig(twig='f+t', trace=True)
      clump.show('creation', full=True)
      other = ParmClump.ParmClump(clump, trace=True)
      other.show('other', full=True)
      sc = SolverUnit(clump, other, trace=True)
      sc.show('SolverUnit', full=True)

   if 1:
      clump.show('final', full=True)

   
      
   print '\n** End of standalone test of: SolverUnit.py:\n' 

#=====================================================================================





