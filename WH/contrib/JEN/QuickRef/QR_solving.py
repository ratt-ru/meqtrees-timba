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

from Timba.Contrib.JEN.QuickRef import QuickRefUtil as QRU
from Timba.Contrib.JEN.QuickRef import EasyTwig as ET
from Timba.Contrib.JEN.QuickRef import EasyNode as EN

# Import QR_MeqNodes.py to use its .solving_ab()
# Its compile options appear in the menu, but have no effect.... (can we hide it?)
# Its runtime options also appear in the runtime menu...
# Is it a good idea for quick-reference to make this actually work?
from Timba.Contrib.JEN.QuickRef import QR_MeqNodes
QR_MeqNodes.itsTDLCompileMenu.hide()

from Timba.Contrib.JEN.Expression import Expression

# import math
# import random
import numpy


#******************************************************************************** 
# TDLCompileMenu (included in QuickRef menu):
#********************************************************************************


oo = TDLCompileMenu("QR_solving topics:",
                    TDLOption('opt_alltopics',"override: include all topics",True),
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
                                              ['{ampl}*exp(-({af}*[f]**2+{at}*[t]**2))'], more=str),
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

# Assign the menu to an attribute, for outside visibility:
itsTDLCompileMenu = oo


#********************************************************************************
# Top-level function, called from QuickRef.py:
#********************************************************************************

def QR_solving (ns, rider):
   """
   Solving...
   """
   stub = QRU.on_entry(ns, rider, QR_solving)
   cc = []
   if opt_alltopics or opt_basic:
      cc.append(basic (ns, rider))

   if opt_helpnodes:
      cc.append(make_helpnodes (ns, rider))

   return QRU.on_exit (ns, rider, cc, mode='group')



#********************************************************************************
# 2nd tier: Functions called from the top function above:
#********************************************************************************

def make_helpnodes (ns, rider):
   """
   helpnodes...
   """
   stub = QRU.on_entry(ns, rider, make_helpnodes)
   
   cc = []
   if opt_alltopics or opt_helpnode_twig:
      cc.append(QRU.helpnode (ns, rider,
                              name='EasyTwig_twig',
                              help=ET.twig.__doc__, trace=False))

   return QRU.on_exit (ns, rider, cc, mode='group')


#--------------------------------------------------------------------------------

def basic (ns, rider):
   """
   MeqSolver
   MeqCondeq
   MeqStripper (?)
   """
   stub = QRU.on_entry(ns, rider, basic)
   cc = []

   override =  opt_alltopics

   if True:
      # Use the one from the central module QR_MeqNodes:
      cc.append(QR_MeqNodes.solving_ab (ns, rider))    

   if override or opt_basic_polyparm:
      cc.append(basic_polyparm (ns, rider))
   if override or opt_basic_onepolc:
      cc.append(basic_onepolc (ns, rider))

   if opt_basic_Expression:
   # if override or opt_basic_Expression:                 # when Expression MeqParm problem solved...
      cc.append(basic_Expression (ns, rider))

   return QRU.on_exit (ns, rider, cc, mode='group')




#********************************************************************************
#********************************************************************************
#********************************************************************************
# 3rd tier: Functions called from functions at the 2nd tier above
#********************************************************************************
#********************************************************************************


#================================================================================
# basic_... 
#================================================================================


def basic_polyparm (ns, rider):
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

   <function_code>
   def basic_polyparm (ns, rider):
   stub = QRU.on_entry(ns, rider, basic_polyparm)
   rhs = ET.twig(ns, opt_basic_twig, nodestub=stub('rhs'))              
   lhs = ET.twig(ns, opt_basic_polyparm_poly, nodestub=stub('lhs'))
   parms = stub.search(tags='polyparm')
   parmset = stub('solved_parms') << Meq.Composer(*parms)
   condeq = stub('condeq') << Meq.Condeq(lhs, rhs)
   solver = stub('solver') << Meq.Solver(condeq, solvable=parms)
   return QRU.on_exit (ns, rider, [solver,condeq,lhs,rhs,parmset],
                       node_help=True,
                       show_recurse=solver, 
                       parentclass='ReqSeq', result_index=0)
   </function_code>
   """
   stub = QRU.on_entry(ns, rider, basic_polyparm)

   rhs = ET.twig(ns, opt_basic_twig, nodestub=stub('rhs'))              
   lhs = ET.twig(ns, opt_basic_polyparm_poly, nodestub=stub('lhs'))
   parms = stub.search(tags='polyparm')
   parmset = stub('solved_parms') << Meq.Composer(*parms)
   condeq = stub('condeq') << Meq.Condeq(lhs, rhs)
   solver = stub('solver') << Meq.Solver(condeq, solvable=parms)

   return QRU.on_exit (ns, rider, [solver,condeq,lhs,rhs,parmset],
                       node_help=True,
                       show_recurse=solver, 
                       parentclass='ReqSeq', result_index=0)

#--------------------------------------------------------------------------------

def basic_Expression (ns, rider):
   """
   Solve for the parameters {p} in a mathematical expression, specified with the
   Expression class (module contrib/JEN/Expression/Expression.py)

   The single condeq represents an equation that equates the expression (rhs) with
   some other function (lhs). The solver finds those values of the Expression
   parameters that satisfy the equation.

   The <b>python</b> expression may be modified by the user here, for experimentation.
   <li> Parameters should be enclosed in {}. They are replaced by MeqParm nodes.
   <li> Variables in [] (e.g. [t] or [m]). They are replaced by MeqTime or MeqGrid nodes etc.
   """
   stub = QRU.on_entry(ns, rider, basic_Expression)

   lhs = ET.twig(ns, opt_basic_twig, nodestub=stub('lhs'))              

   ## rhs = ET.twig(ns, opt_basic_Expression_expr, nodename='rhs')      # nodestub=stub('rhs'))
   expr = Expression.Expression(ns, 'rhs', expr=opt_basic_Expression_expr)
   # expr.display('QR_solving.basic_Expression()')
   rhs = expr.MeqFunctional()

   parms = EN.find_parms(rhs, trace=True)
   # The following alternatives only work when rhs is below the stub....
   # parms = stub.search(tags='solvable')       
   # parms = stub.search(tags='MeqFunctional')       
   if len(parms)==0:
      s = '** the Expression: '+opt_basic_Expression_expr
      s += '\n  should have at least one {parm}...'
      raise ValueError,s
   elif len(parms)==1:
      parmset = parms[0]
   else:
      parmset = stub('solved_parms') << Meq.Composer(*parms)
   qhelp = """The condeq represents the equation: """
   qhelp += opt_basic_Expression_expr+' = '+opt_basic_twig
   condeq = stub('condeq') << Meq.Condeq(lhs,rhs, qhelp=qhelp)
   solver = stub('solver') << Meq.Solver(condeq, solvable=parms)  

   return QRU.on_exit (ns, rider, [solver,condeq,lhs,rhs,parmset],
                       node_help=True,
                       show_recurse=solver, 
                       parentclass='ReqSeq', result_index=0)

#--------------------------------------------------------------------------------

def basic_onepolc (ns, rider):
   """
   Solving for the coeff of the polc of a single MeqParm.
   The single MeqCondeq child of the MeqSolver has two children:
   <li> The left-hand side (lhs): is the input twig node (e.g. a gaussian_ft)
   <li> The right-hand side (rhs): is a MeqParm:
   """
   stub = QRU.on_entry(ns, rider, basic_onepolc)

   lhs = ET.twig(ns, getopt('opt_basic_twig', rider),
                 nodestub=stub('lhs'))
   tiling = record(freq=getopt('opt_basic_tiling_freq', rider),
                   time=getopt('opt_basic_tiling_time', rider))
   fdeg = getopt('opt_basic_onepolc_fdeg', rider)
   tdeg = getopt('opt_basic_onepolc_tdeg', rider)
   mepfile = getopt('opt_basic_onepolc_mepfile', rider)
   rhs = stub('rhs') << Meq.Parm(0.0,
                                 tags=['tag1','tag2'],
                                 shape=[tdeg+1,fdeg+1],
                                 tiling=tiling,
                                 table_name=mepfile,
                                 use_previous=True,
                                 node_groups='Parm')
   condeq = stub('condeq') << Meq.Condeq(lhs,rhs)
   solver = stub('solver') << Meq.Solver(condeq,
                                         niter=10,
                                         qviewer=[True,'Record Browser'],
                                         solvable=rhs)  

   return QRU.on_exit (ns, rider, [solver,condeq,lhs,rhs],
                       node_help=True,
                       show_recurse=solver,
                       parentclass='ReqSeq', result_index=0)


#--------------------------------------------------------------------------------








#********************************************************************************
#********************************************************************************
# Helper functions: 
#********************************************************************************

def getopt (name, rider=None, trace=False):
   """
   Standard helper function to read the named TDL option in an organized way.
   """
   value = globals().get(name)                  # gives an error if it does not exist
   return QRU.getopt(name, value, rider=rider, trace=trace)




#================================================================================
#================================================================================
#================================================================================
#================================================================================
# Forest for standalone operation:
#================================================================================

def _define_forest (ns, **kwargs):
   """Definition of a 'forest' of one or more trees"""

   TDLRuntimeMenu(":")
   TDLRuntimeMenu("QR_solving runtime options:", QRU)
   TDLRuntimeMenu(":")

   global rootnodename
   rootnodename = 'QR_solving'                  # The name of the node to be executed...
   global rider                                 # used in tdl_jobs
   rider = QRU.create_rider(rootnodename)       # CollatedHelpRecord object
   QRU.on_exit (ns, rider,
               nodes=[QR_solving(ns, rider)])

   # Finished:
   return True
   
#--------------------------------------------------------------------------------

def _tdl_job_execute_1D_f (mqs, parent):
   return QRU._tdl_job_execute_f (mqs, parent, rootnode=rootnodename)

def _tdl_job_execute_2D_ft (mqs, parent):
   return QRU._tdl_job_execute_ft (mqs, parent, rootnode=rootnodename)

def _tdl_job_execute_3D_ftL (mqs, parent):
   return QRU._tdl_job_execute_ftL (mqs, parent, rootnode=rootnodename)

def _tdl_job_execute_4D_ftLM (mqs, parent):
   return QRU._tdl_job_execute_ftLM (mqs, parent, rootnode=rootnodename)

def _tdl_job_execute_sequence (mqs, parent):
   return QRU._tdl_job_execute_sequence (mqs, parent, rootnode=rootnodename)

#--------------------------------------------------------------------------------

def _tdl_job_m (mqs, parent):
   return QRU._tdl_job_m (mqs, parent)

def _tdl_job_print_doc (mqs, parent):
   return QRU._tdl_job_print_doc (mqs, parent, rider, header='QR_solving')

def _tdl_job_print_hardcopy (mqs, parent):
   return QRU._tdl_job_print_hardcopy (mqs, parent, rider, header='QR_solving')

def _tdl_job_show_doc (mqs, parent):
   return QRU._tdl_job_show_doc (mqs, parent, rider, header='QR_solving')

def _tdl_job_save_doc (mqs, parent):
   return QRU._tdl_job_save_doc (mqs, parent, rider, filename='QR_solving')



#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

   print '\n** Start of standalone test of: QR_solving.py:\n' 

   ns = NodeScope()

   rider = QRU.create_rider()             # CollatedHelpRecord object
   if 0:
      QR_solving(ns, 'test')
      if 1:
         print rider.format()
            
   print '\n** End of standalone test of: QR_solving.py:\n' 

#=====================================================================================





