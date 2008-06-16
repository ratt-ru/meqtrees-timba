"""
QuickRef module: QR_solving.py
Demonstration(s) of solving for MeqParm values in MeqTrees.
It may be called from the module QuickRef.py.
But it may also be used stand-alone.
-- Load the TDL script into the meqbrowser.
-- Using TDL Options, select categories to be included,
.    and customize parameters and input children.
-- Compile: The tree will appear in the left panel.
.    (NB: the state record of each node has a quickref_help field)
-- Use the bookmarks to select one or more views.
-- Use TDL Exec to execute the tree: The views will come alive.
-- Use TDL Exec to show or print or save the hierarchical help
.    for the selected categories.
"""

# file: ../JEN/demo/QR_solving.py:
#
# Author: J.E.Noordam
#
# Short description:
#   Demonstration(s) of solving for MeqParm values in MeqTrees.
#
# History:
#   - 11 jun 2008: creation (from QR_MeqNodes.py)
#
# Description:
#
# Remarks:
#
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

import QuickRefUtil as QR
import EasyTwig as ET

# import math
# import random
import numpy


#******************************************************************************** 
# TDLCompileMenu (included in QuickRef menu):
#********************************************************************************


TDLCompileMenu("QR_solving topics:",
               TDLOption('opt_alltopics',"all",True),
               TDLMenu("basic",
                       TDLOption('opt_basic_twig',"input twig (lhs of condeq)",
                                 ET.twig_names(['gaussian'],first='gaussian_ft'),
                                 more=str),
                       TDLOption('opt_basic_tiling_time',"size (time-cells) of solving subtile",
                                 [None,1,2,3,4,5,10], more=int),
                       TDLOption('opt_basic_tiling_freq',"size (freq-cells) of solving subtile",
                                 [None,1,2,3,4,5,10], more=int),
                       TDLOption('opt_basic_mepfile',"name of mep table file",
                                 [None,'QR_solving'], more=str),
                       TDLMenu("basic_polyparm",
                               TDLOption('opt_basic_polyparm_poly',"polynomial to be fitted (rhs)",
                                         ET.twig_names(['polyparm']), more=str),
                               toggle='opt_basic_polyparm'),
                       TDLMenu("basic_Expression",
                               TDLOption('opt_basic_Expression_expr',"Expression to be fitted (rhs)",
                                         ET.twig_names(['Expression']), more=str),
                               toggle='opt_basic_Expression'),
                       TDLMenu("basic_onepolc",
                               TDLOption('opt_basic_onepolc_tdeg',"time deg of MeqParm polc",
                                         range(6), more=int),
                               TDLOption('opt_basic_onepolc_fdeg',"freq deg of MeqParm polc",
                                         range(6), more=int),
                               toggle='opt_basic_onepolc'),
                       toggle='opt_basic'),

               TDLMenu("help",
                       TDLOption('opt_helpnode_twig',"help on EasyTwig.twig()", False),
                       toggle='opt_helpnodes'),

               toggle='opt_QR_solving')



#********************************************************************************
# Top-level function, called from QuickRef.py:
#********************************************************************************


def QR_solving (ns, path, rider):
   """
   Solving...
   """
   rr = QR.on_entry(QR_solving, path, rider)
   cc = []
   if opt_alltopics or opt_basic:
      cc.append(basic (ns, rr.path, rider))

   if opt_helpnodes:
      cc.append(make_helpnodes (ns, rr.path, rider))

   return QR.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)



#********************************************************************************
# 2nd tier: Functions called from the top function above:
#********************************************************************************

def make_helpnodes (ns, path, rider):
   """
   helpnodes...
   """
   rr = QR.on_entry(make_helpnodes, path, rider)
   
   cc = []
   if opt_alltopics or opt_helpnode_twig:
      cc.append(QR.helpnode (ns, rr.path, rider,
                             name='EasyTwig_twig',
                             help=ET.twig.__doc__, trace=False))

   return QR.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)


#--------------------------------------------------------------------------------

def basic (ns, path, rider):
   """
   MeqSolver
   MeqCondeq
   MeqStripper (?)
   """
   rr = QR.on_entry(basic, path, rider)
   cc = []
   cc.append(basic_ab (ns, rr.path, rider))                    # simplest, do always
   if opt_alltopics or opt_basic_polyparm:
      cc.append(basic_polyparm (ns, rr.path, rider))
   if opt_alltopics or opt_basic_onepolc:
      cc.append(basic_onepolc (ns, rr.path, rider))

   if opt_basic_Expression:
   # if opt_alltopics or opt_basic_Expression:                 # when Expression MeqParm problem solved...
      cc.append(basic_Expression (ns, rr.path, rider))

   return QR.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)




#********************************************************************************
#********************************************************************************
#********************************************************************************
# 3rd tier: Functions called from functions at the 2nd tier above
#********************************************************************************
#********************************************************************************


#================================================================================
# basic_... 
#================================================================================

def basic_ab (ns, path, rider):
   """
   Demonstration of solving for two unknown parameters (a,b),
   using two linear equations (one condeq child each):
   - condeq 0:  a + b = p (=10)
   - condeq 1:  a - b = q (=2)
   The result should be: a = (p+q)/2 (=6), and b = (p-q)/2 (=4)
   Condeq Results are the solution residuals, which should be small.
   """
   rr = QR.on_entry(basic_ab, path, rider)
   a = ET.unique_stub(ns, 'a') << Meq.Parm(0)
   b = ET.unique_stub(ns, 'b') << Meq.Parm(0)
   p = ET.unique_stub(ns, 'p') << Meq.Constant(10)
   q = ET.unique_stub(ns, 'q') << Meq.Constant(2)
   sum_ab = ns << Meq.Add(a,b) 
   diff_ab = ns << Meq.Subtract(a,b)
   drivers = ET.unique_stub(ns, 'driving_values_p_q') << Meq.Composer(p,q)
   parmset = ET.unique_stub(ns, 'solved_parameters_a_b') << Meq.Composer(a,b)

   condeqs = []
   condeqs.append(QR.MeqNode (ns, rr.path, rider, meqclass='Condeq',name='Condeq(a+b,p)',
                              help='Represents equation: a + b = p (=10)',
                              children=[sum_ab, p]))
   condeqs.append(QR.MeqNode (ns, rr.path, rider, meqclass='Condeq',name='Condeq(a-b,q)',
                              help='Represents equation: a - b = q (=2)',
                              children=[diff_ab, q]))

   solver = QR.MeqNode (ns, rr.path, rider, meqclass='Solver',
                        name='Solver(*condeqs, solvable=[a,b])',
                        help='Solver', show_recurse=True,
                        children=condeqs,
                        solvable=[a,b])  
   residuals = QR.MeqNode (ns, rr.path, rider, meqclass='Add', name='residuals',
                           help='The sum of the (abs) condeq residuals',
                           children=condeqs, unop='Abs')
   cc = [solver,residuals,drivers,parmset]
   return QR.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                     parentclass='ReqSeq', result_index=0)

#--------------------------------------------------------------------------------

def basic_polyparm (ns, path, rider):
   """
   Demonstration of solving for the coefficients of a freq-time polynomial.
   It is fitted to the specified twig (e.g. a 2D gaussian).
   A separate equation is generated for each cell of the Request domain.

   The number of cells should be greater than the number of unknowns.
   In this case, this is the number of MeqParms, which have polcs with only
   a single coefficient (c00). NB: Try solving for freq-time polcs....)

   If the input (twig) function does not vary much over the domain, there
   is not enough information to solve for higher-order polynomial coeff.
   In this case, the solution will 'lose rank', which is indicated in the
   solver plot: the black line on the right leaves the right edge. 
   """
   rr = QR.on_entry(basic_polyparm, path, rider)
   twig = ET.twig(ns, opt_basic_twig)                       # move to solving()?
   poly = ET.twig(ns, opt_basic_polyparm_poly)
   parms = ET.find_parms(poly, trace=False)
   parmset = ET.unique_stub(ns,'solved_parms') << Meq.Composer(*parms)
   condeq = ns << Meq.Condeq(poly, twig)
   solver = QR.MeqNode (ns, rr.path, rider, meqclass='Solver',
                        name='Solver(condeq, solvable=parms)',
                        help='Solver', show_recurse=True,
                        children=[condeq],
                        solvable=parms)  
   cc = [solver,condeq,poly,twig,parmset]
   return QR.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                     parentclass='ReqSeq', result_index=0)

#--------------------------------------------------------------------------------

def basic_Expression (ns, path, rider):
   """
   """
   rr = QR.on_entry(basic_Expression, path, rider)
   lhs = ET.twig(ns, opt_basic_twig)              
   print '** expr =',opt_basic_Expression_expr
   rhs = ET.twig(ns, opt_basic_Expression_expr)
   print '** rhs =',str(rhs)
   parms = ET.find_parms(rhs, trace=True)
   if len(parms)==0:
      s = '** the Expression: '+opt_basic_Expression_expr
      s += '\n  should have at least one {parm}...'
      raise ValueError,s
   elif len(parms)==1:
      parmset = parms[0]
   else:
      parmset = ET.unique_stub(ns,'solved_parms') << Meq.Composer(*parms)
   condeq = ns << Meq.Condeq(lhs,rhs)
   solver = QR.MeqNode (ns, rr.path, rider, meqclass='Solver',
                        name='Solver(condeq, solvable=parms)',
                        help='Solver', show_recurse=True,
                        children=[condeq],
                        solvable=parms)  
   cc = [solver,condeq,lhs,rhs,parmset]
   return QR.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                     parentclass='ReqSeq', result_index=0)

#--------------------------------------------------------------------------------

def basic_onepolc (ns, path, rider):
   """
   Solving for the coeff of the polc of a single MeqParm.
   The single MeqCondeq child of the MeqSolver has two children:
   - The left-hand side (lhs) is the input twig node (e.g. a gaussian_ft)
   - The right-hand side (rhs) is a MeqParm:
   .      rhs = ns['MeqParm'] << Meq.Parm(meq.polc(coeff=numpy.zeros([tdeg+1,fdeg+1])))
   """
   rr = QR.on_entry(basic_onepolc, path, rider)
   lhs = ET.twig(ns, opt_basic_twig)
   tiling = record(freq=opt_basic_tiling_freq,
                   time=opt_basic_tiling_time)
   fdeg = opt_basic_onepolc_fdeg
   tdeg = opt_basic_onepolc_tdeg
   mepfile = opt_basic_mepfile
   pname = 'MeqParm(shape=[1+'+str(tdeg)+',1+'+str(fdeg)+'])'
   help = 'help'
   rhs = ET.unique_stub(ns,pname) << Meq.Parm(0.0,
                                              tags=['tag1','tag2'],
                                              shape=[tdeg+1,fdeg+1],
                                              tiling=tiling,
                                              table_name=mepfile,
                                              use_previous=True,
                                              quickref_help='...help...',
                                              node_groups='Parm')
   condeq = ns << Meq.Condeq(lhs,rhs)
   solver = QR.MeqNode (ns, rr.path, rider, meqclass='Solver',
                        name='Solver(condeq, solvable=MeqParm)',
                        help='Solver', show_recurse=True,
                        children=[condeq],
                        niter=10,
                        solvable=rhs)  
   cc = [solver,condeq,lhs,rhs]
   QR.helpnode(ns, path, rider, node=rhs)
   return QR.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                     parentclass='ReqSeq', result_index=0)


#--------------------------------------------------------------------------------










#================================================================================
#================================================================================
#================================================================================
#================================================================================
# Local testing forest:
#================================================================================

TDLRuntimeMenu(":")
TDLRuntimeMenu("QuickRef runtime options:", QR)
TDLRuntimeMenu(":")

# For TDLCompileMenu, see the top of this module


#--------------------------------------------------------------------------------

def _define_forest (ns, **kwargs):
   """Definition of a 'forest' of one or more trees"""

   global rider                                 # used in tdl_jobs
   rider = QR.create_rider()                    # CollatedHelpRecord object
   rootnodename = 'QR_solving'                  # The name of the node to be executed...
   path = rootnodename                          # Root of the path-string
   QR.bundle (ns, path, rider,
              nodes=[QR_solving(ns, path, rider)],
              help=__doc__)

   # Finished:
   return True
   


#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------

def _tdl_job_execute_1D (mqs, parent):
   return QR._tdl_job_execute_1D (mqs, parent, rootnode='QR_solving')

def _tdl_job_execute_2D (mqs, parent):
   return QR._tdl_job_execute_2D (mqs, parent, rootnode='QR_solving')

def _tdl_job_execute_3D (mqs, parent):
   return QR._tdl_job_execute_3D (mqs, parent, rootnode='QR_solving')

def _tdl_job_execute_4D (mqs, parent):
   return QR._tdl_job_execute_4D (mqs, parent, rootnode='QR_solving')

def _tdl_job_execute_sequence (mqs, parent):
   return QR._tdl_job_execute_sequence (mqs, parent, rootnode='QR_solving')

#--------------------------------------------------------------------------------

def _tdl_job_m (mqs, parent):
   return QR._tdl_job_m (mqs, parent)

def _tdl_job_print_doc (mqs, parent):
   return QR._tdl_job_print_doc (mqs, parent, rider, header='QR_solving')

def _tdl_job_print_hardcopy (mqs, parent):
   return QR._tdl_job_print_hardcopy (mqs, parent, rider, header='QR_solving')

def _tdl_job_show_doc (mqs, parent):
   return QR._tdl_job_show_doc (mqs, parent, rider, header='QR_solving')

def _tdl_job_save_doc (mqs, parent):
   return QR._tdl_job_save_doc (mqs, parent, rider, filename='QR_solving')



#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

   print '\n** Start of standalone test of: QR_solving.py:\n' 

   ns = NodeScope()

   rider = QR.create_rider()             # CollatedHelpRecord object
   if 1:
      QR_solving(ns, 'test', rider)
      if 1:
         print rider.format()
            
   print '\n** End of standalone test of: QR_solving.py:\n' 

#=====================================================================================





