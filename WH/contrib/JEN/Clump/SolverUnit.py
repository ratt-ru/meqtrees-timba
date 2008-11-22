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

   def __init__(self, clump=None, rhs=None, **kwargs):
      """
      Derived from class Clump. The required inputs are two Clumps,
      representing the left-hand side (lhs) and right-hand side (rhs)
      of the MeqCondeq nodes that generate equations. The lhs is the
      input clump, i.e. its nodes are copied into the SolverUnit Clump.
      A new clump (self._rhs) is creates so that its trees may be grown
      without affecting the input Clump itself.
      """
      self._rhs = rhs.copy()
      Clump.Clump.__init__(self, clump=clump, **kwargs)
      return None


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

      help = 'if True/1, make bookpage () in foder: '+str(self.name())
      self.add_option('make_bookmark', [True,False], help=help, hide=True,
                      prompt='make solver bookmark')

      help = """If True/1, compose lhs and rhs into a single tensor node first
      using a MeqComposer. This unclutters the tree, and may be more efficient(?)
      """
      self.add_option('compose', [False,True], hide=True, help=help,
                      prompt='compose first')

      help = """If specified, apply unary operation(s) to the input first.
      For instance, convert complex numbers into phases, or log(ampl).
      """
      self.add_option('unops', [None, 'Arg','Log','Cos'],
                      more=str, hide=True, help=help)

      help = """If specified, change the freq/time resolution (nr of cells)
      of the domain, so that fewer equations have to be generated (with higher S/N)."""
      self.add_option('resample_time', [None,5,4,3,2,1],
                      more=int, hide=True, help=help)
      self.add_option('resample_freq', [None,5,4,3,2,1],
                      more=int, hide=True, help=help)

      solver = None
      if self.execute_body():

         # Connect orphans, stubtree etc, and transfer ParmClumps!
         # NB: This should be done INSIDE the function body.
         # NB: This should be done BEFORE getting MeqParms.
         self.connect_grafted_clump (self._rhs)
         
         # Get option values etc (first):
         compose = self.getopt('compose')
         unops = self.getopt('unops')
         resample_time = self.getopt('resample_time')
         resample_freq = self.getopt('resample_freq')
         num_iter = self.getopt('num_iter')
         make_bookmark = self.getopt('make_bookmark')
         solver_help = kwargs.get('help',self.oneliner())

         if compose:
            # Make sure that both inputs (lhs and rhs) are composed,
            # i.e. consist of a single (tensor) node. This unclutters
            # the tree, and opens the way to more efficient processing.
            self.compose()
            self._rhs.compose()

         num_cells = [resample_time, resample_freq]
         resample = (not num_cells==[None,None])
         if resample:
            # Resample the result, so that it has the same nr of cells as
            # the request generated by Meq.ModRes(solver,num_cells) below. 
            self.apply_unops('Resampler', mode=1)

         if unops:
            # Optionally, apply unary operation(s) to both lhs and rhs:
            self.apply_unops(unops)
            self._rhs.apply_unops(unops)  

         # Make the MeqCondeq(s):
         stub = self.unique_nodestub()
         condeqs = []
         # print self._rhs.oneliner()
         for i,qual in enumerate(self.nodequals()):
            node = stub('condeq')(qual) << Meq.Condeq(self[i],self._rhs[i]) 
            self[i] = node
            condeqs.append(node)

         # Get solvable MeqParms (from its ParmClumps, if any):
         solvable = self.get_solvable()

         # Make MeqSolver:
         solver = stub('solver') << Meq.Solver(children=condeqs,
                                               num_iter=num_iter,
                                               solvable=solvable)

         #..............................................................
         # Optionally, make a ReqSeq for solver visualization:
         node = solver
         if make_bookmark:
            node = self.make_solver_bookpage(stub, solver=solver,
                                             condeqs=condeqs,
                                             solvable=solvable,
                                             help=solver_help)
            
         if resample:
            # Optionally, change the nr of cells in the REQUEST: All subsequent
            # nodes (solver, condeqs, rhs, lhs (up to the resamples node)) will be
            # executed with the reduced nr of (larger) cells (efficient, higher S/N)
            node = stub('ModRes')(num_cells) << Meq.ModRes(node, num_cells=num_cells)

         # Insert ReqSeq node(s) in the trees of the input clump.
         # These will issue a request first to the solver,
         # but pass on the result of the trees (result_index=1).
         self.input_clump().insert_reqseqs(node, 'solver_graft:'+self.name())

         # Clear up some loose ends:
         self.connect_loose_ends()
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
      nodes = []
      viewer = []
      help = str(help)                              # just in case
      if not isinstance(condeqs,list):
         condeqs = []
      if not isinstance(solvable,list):
         solvable = []
      nc = len(condeqs)
      ns = len(solvable)

      #............................
      if ns==0:
         self.ERROR('** no solvable MeqParms')

      if nc==0:
         self.ERROR('** no MeqCondeqs')

      #............................
      help += '\n\n** MeqSolver settings:'
      help = self.initrec2help(solver, help, ignore=['solvable'])

      #............................
      help += """\n\n** MeqParm nodes ("""+str(ns)+"""):
      The results of individual MeqParms may be inspected.
      - Right-click on the panel, and use 'Change Selected Vells'.
      - Use the full list of relevant MeqParm nodes below for key.
      """
      if ns>0:
         help += '\n MeqParm settings (initrec):'
         help = self.initrec2help(solvable[0], help, ignore=[])
         help += '\n NB: The first MeqParm only (the others are assumed to be the same...)'

      #............................
      help += """\n\n** MeqCondeq nodes ("""+str(nc)+"""):
      The results of individual MeqCondeqs may be inspected.
      - Right-click on the panel, and use 'Change Selected Vells'.
      - Use the full list of relevant MeqCondeq nodes below for key.
      If there is more than one MeqCondeq, the quality of the fit
      may be rapidly assessed by means of the sum(abs(condeq)) node.
      """
      if nc>0:
         help += '\n MeqCondeqs have two children (lhs and rhs):'
         cc = condeqs[0].children
         help += '\n     - lhs:  '+str(cc[0][1])
         help += '\n     - rhs:  '+str(cc[1][1])

      #............................
      help += '\n\n** Full list of '+str(ns)+' solvable MeqParm nodes:'
      for i,c in enumerate(solvable):
         help += '\n  - '+str(i)+': '+str(c)

      #............................
      help += '\n\n** Full list of '+str(nc)+' MeqCondeq nodes:'
      for i,c in enumerate(condeqs):
         help += '\n  - '+str(i)+': '+str(c)

      #............................
      if ns==0:
         help += '\n\n********* NO SOLVABLE MeqParms *********\n\n'
      else:
         if ns==1:
            node = stub('solvable_parm') << Meq.Identity(solvable[0])
         else:
            node = stub('solvable_parms') << Meq.Composer(*solvable)
         nodes.append(node)
         viewer.append('Result Plotter')

      #............................
      if nc==0:
         help += '\n\n********* NO MeqCondeqs *********\n\n'
      else:
         if nc==1:
            node = stub('condeq') << Meq.Identity(condeqs[0])
         elif True:
            node = self.plot_summary (nodelist=condeqs)
         else:
            node = stub('condeqs') << Meq.Composer(*condeqs)
            cc = []
            for c in condeqs:
               cc.append(Meq.Abs(c))
            sumabs = stub('sum(abs(condeq))') << Meq.Add(*cc)
            nodes.append(sumabs)
            viewer.append('Result Plotter')
         nodes.append(node)
         viewer.append('Result Plotter')

      #............................
      # Make the reqseq BEFOFE the solver is appended to nodes (below):
      visu_node = stub('solver_bookpage') << Meq.ReqSeq(*nodes) 
      branch_node = stub('solver_branch') << Meq.ReqSeq(solver, visu_node) 

      #............................
      # Make the bookpage (last):
      nodes.append(solver)
      viewer.append('Result Plotter')
      help += self.history(format=True)
      solver = self.make_bookmark_help(solver, help, bookmark=False)
      nodes.append(solver)
      viewer.append('QuickRef Display')
      self.make_bookmark(nodes, name=self.name(), viewer=viewer)

      # Return:
      return branch_node



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
   TCM.add_option('test', ['straight','twig','polyparm'],
                  more=False, help=help,
                  prompt='select a test')
   
   clump = None
   if TCM.submenu_is_selected():
      test = TCM.getopt('test', submenu)
      help = test
      if test=='twig':
         clump = TwigClump.Twig(ns=ns, TCM=TCM, name='LHS', trace=True)
         rhs = ParmClump.ParmClump(clump, name='RHS', trace=True)
      elif test=='polyparm':
         rhs = TwigClump.Polynomial(ns=ns, TCM=TCM, name='RHS', trace=True)
         clump = Clump.LeafClump(rhs, name='LHS', trace=True)
      else:
         clump = Clump.LeafClump(ns=ns, TCM=TCM, name='LHS', trace=True)
         rhs = ParmClump.ParmClump(clump, name='RHS', trace=True)
      clump.show('creation', full=True)
      rhs.show('before SolverUnit', full=True)
      su = SolverUnit(clump, rhs, help=help, trace=True)
      su.show('creation', full=True)
      rhs.show('after SolverUnit', full=True)

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
      rhs = ParmClump.ParmClump(clump, name='rhs', trace=True)
      rhs.show('rhs', full=True)
      sc = SolverUnit(clump, rhs, trace=True)
      sc.show('SolverUnit', full=True)

   if 1:
      clump.show('final', full=True)

   
      
   print '\n** End of standalone test of: SolverUnit.py:\n' 

#=====================================================================================





