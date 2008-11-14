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
      solver_help = kwargs.get('help','SolverUnit')
      ctrl = self.on_entry(self.initexec, **kwargs)  

      self.add_option('num_iter',[3,5,10,20,1,2],
                      help='(max) nr of solver iterations')
      help = 'if True(=1), make bookpage () in foder: '+str(self._name)
      self.add_option('make_bookmark', [True], help=help)

      solver = None
      if self.execute_body():

         # Connect orphans, stubtree etc, and transfer ParmClumps!
         # But ONLY if this clump is actually executed (i.e. selected) 
         self.connect_grafted_clump (self._other)

         # Get option values:
         num_iter = self.getopt('num_iter')
         make_bookmark = self.getopt('make_bookmark')

         # Make MeqCondeqs:
         stub = self.unique_nodestub()
         condeqs = []
         # print self._other.oneliner()
         for i,qual in enumerate(self._nodequals):
            node = stub('condeq')(qual) << Meq.Condeq(self[i],
                                                      self._other[i]) 
            self._nodes[i] = node
            condeqs.append(node)

         # Make MeqSolver:
         solvable = []
         for pc in self._ParmClumps:
            ss = pc.solspec(select=True)
            solvable.extend(ss)
            s = 'Got '+str(len(ss))+' (total='+str(len(solvable))+') '
            s += 'solvable MeqParms from: '+pc.oneliner()
            self.history(s)
         solver = stub('solver') << Meq.Solver(children=condeqs,
                                               num_iter=num_iter,
                                               solvable=solvable)

         # Optionally, make a ReqSeq for solver visualization:
         reqseq_node = solver
         if make_bookmark:
            reqseq_node = self.make_solver_bookpage(stub, solver=solver,
                                                    condeqs=condeqs,
                                                    solvable=solvable,
                                                    help=solver_help)

         # Insert ReqSeq node(s) in the trees of the input clump.
         # These will issue a request first to the solver,
         # but pass on the result of the trees (result_index=1).
         self._input_clump.insert_reqseqs(reqseq_node)
         self.end_of_body(ctrl)

      # Mandatory counterpart of self.on_entry()
      return self.on_exit(ctrl, result=solver)


   #======================================================================
   #======================================================================

   def make_solver_bookpage(self, stub, solver,
                            condeqs=None, solvable=None,
                            help=None, trace=False):
      """Make a bookpage for this solver, showing the solver itself,
      the MeqCondeqs, the solvable MeqParms, and QuickRef help
      """
      nodes = [solver]                              # should be first!
      viewer = ['Result Plotter']
      help = str(help)                              # just in case

      if condeqs:
         nn = len(condeqs)
         help += '\n\n** MeqCondeq node(s):'
         for i,c in enumerate(condeqs):
            help += '\n  - '+str(i)+': '+str(c)
         if nn==1:
            node = stub('condeq') << Meq.Identity(condeqs[0])
         elif nn>1:
            node = stub('condeqs') << Meq.Composer(*condeqs)
            if True:
               # Make a quick-view: sum(abs(condeq))
               cc = []
               for c in condeqs:
                  cc.append(Meq.Abs(c))
               sumabs = stub('sum(abs(condeq))') << Meq.Add(*cc)
               nodes.append(sumabs)
               viewer.append('Result Plotter')
         else:
            node = stub('no_condeqs') << Meq.Constant(-0.123456789)
         nodes.append(node)
         viewer.append('Result Plotter')

      if solvable:
         nn = len(solvable)
         help += '\n\n** Solvable MeqParm node name(s):'
         for i,c in enumerate(solvable):
            help += '\n  - '+str(i)+': '+str(c)
         if nn==0:
            node = stub('no_solvable_parms') << Meq.Constant(-0.123456789)
         elif nn==1:
            node = stub('solvable_parm') << Meq.Identity(solvable[0])
         else:
            node = stub('solvable_parms') << Meq.Composer(*solvable)
         nodes.append(node)
         viewer.append('Result Plotter')

      if help:
         nodes.append(self.make_bookmark_help(solver, help, bookmark=False))
         viewer.append('QuickRef Display')

      # Make the bookpage:
      print len(nodes)
      print len(viewer)
      for i,node in enumerate(nodes):
         print '-',str(node),viewer[i]
      self.make_bookmark(nodes, viewer=viewer)
      reqseq_node = stub('reqseq') << Meq.ReqSeq(children=nodes) 
      return reqseq_node
            




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

   help = '<help>'
   TCM.add_option('test', ['straight','twig'], more=False,
                  prompt='select a test', help=help)
   
   clump = None
   if TCM.submenu_is_selected():
      test = TCM.getopt('test', submenu)
      if test=='twig':
         clump = TwigClump.Twig(ns=ns, TCM=TCM, trace=True)
      else:
         clump = Clump.LeafClump(ns=ns, TCM=TCM, trace=True)
      other = ParmClump.ParmClump(clump, trace=True)
      help = test
      su = SolverUnit(clump, other, help=help, trace=True)

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
      other = ParmClump.ParmClump(clump, name='other', trace=True)
      other.show('other', full=True)
      sc = SolverUnit(clump, other, trace=True)
      sc.show('SolverUnit', full=True)

   if 1:
      clump.show('final', full=True)

   
      
   print '\n** End of standalone test of: SolverUnit.py:\n' 

#=====================================================================================





