"""
QuickRef module: QR_TreeDefinition.py:

This module may be called from the module QuickRef.py.
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

# file: ../JEN/demo/QR_TreeDefinition.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 11 jun 2008: creation (from QR-template.py)
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

import QuickRefUtil as QRU
import EasyTwig as ET

# import math
# import random
import numpy


#******************************************************************************** 
# TDLCompileMenu (included in QuickRef menu):
#********************************************************************************


TDLCompileMenu("QR_TreeDefinition topics:",
               TDLOption('opt_alltopics',"override: include all topics",True),
               TDLOption('opt_input_twig',"input twig",
                         ET.twig_names(), more=str),

               TDLMenu("nodenames",
                       toggle='opt_nodenames'),
               TDLMenu("TDL",
                       toggle='opt_TDL'),
               TDLMenu("TDLOptions",
                       toggle='opt_TDLOptions'),
               TDLMenu("bookmarks",
                       toggle='opt_bookmarks'),

               TDLMenu("help",
                       TDLOption('opt_helpnode_twig',"help on EasyTwig.twig()", False),
                       toggle='opt_helpnodes'),

               toggle='opt_QR_TreeDefinition')



#********************************************************************************
# Top-level function, called from QuickRef.py:
#********************************************************************************


def QR_TreeDefinition (ns, path, rider):
   """
   """
   rr = QRU.on_entry(QR_TreeDefinition, path, rider)
 
   cc = []
   if opt_alltopics or opt_nodenames:
      cc.append(nodenames (ns, rr.path, rider))
   if opt_alltopics or opt_TDL:
      cc.append(TDL (ns, rr.path, rider))
   if opt_alltopics or opt_TDLOptions:
      cc.append(TDLOptions (ns, rr.path, rider))
   if opt_alltopics or opt_bookmarks:
      cc.append(bookmarks (ns, rr.path, rider))

   if opt_helpnodes:
      cc.append(make_helpnodes (ns, rr.path, rider))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)



#********************************************************************************
# 2nd tier: Functions called from the top function above:
#********************************************************************************

def make_helpnodes (ns, path, rider):
   """
   It is possible to define nodes that have no other function than to carry
   a help-text. The latter may be consulted in the quickref_help field in the
   state record of this node (a bookmark is generated automatically). It is
   also added to the subset of documentation that is accumulated by the rider.
   """
   rr = QRU.on_entry(make_helpnodes, path, rider)
   
   cc = []
   if opt_alltopics or opt_helpnode_twig:
      cc.append(QRU.helpnode (ns, rr.path, rider, name='EasyTwig_twig',
                             help=ET.twig.__doc__, trace=False))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)


#--------------------------------------------------------------------------------

def nodenames (ns, path, rider):
   """
   """
   rr = QRU.on_entry(nodenames, path, rider)
   cc = []
   if opt_alltopics or opt_nodenames_xxx:
      cc.append(nodenames_xxx (ns, rr.path, rider))
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)


#--------------------------------------------------------------------------------

def TDL (ns, path, rider):
   """
   """
   rr = QRU.on_entry(TDL, path, rider)
   cc = []
   if opt_alltopics or opt_TDL_xxx:
      cc.append(TDL_xxx (ns, rr.path, rider))
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)


#--------------------------------------------------------------------------------

def TDLOptions (ns, path, rider):
   """
   """
   rr = QRU.on_entry(TDLOptions, path, rider)
   cc = []
   if opt_alltopics or opt_TDLOptions_xxx:
      cc.append(TDLOptions_xxx (ns, rr.path, rider))
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)


#--------------------------------------------------------------------------------

def bookmarks (ns, path, rider):
   """
   """
   rr = QRU.on_entry(bookmarks, path, rider)
   cc = []
   if opt_alltopics or opt_bookmarks_xxx:
      cc.append(bookmarks_xxx (ns, rr.path, rider))
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)




#********************************************************************************
#********************************************************************************
#********************************************************************************
# 3rd tier: Functions called from functions at the 2nd tier above
#********************************************************************************
#********************************************************************************


#================================================================================
# topic1_... 
#================================================================================

def topic1_xxx (ns, path, rider):
   """
   """
   rr = QRU.on_entry(topic1_xxx, path, rider)
   
   a = ET.unique_stub(ns, 'a') << Meq.Parm(0)
   b = ET.unique_stub(ns, 'b') << Meq.Parm(0)
   p = ET.unique_stub(ns, 'p') << Meq.Constant(10)
   q = ET.unique_stub(ns, 'q') << Meq.Constant(2)
   sum_ab = ns << Meq.Add(a,b) 
   diff_ab = ns << Meq.Subtract(a,b)
   drivers = ET.unique_stub(ns, 'driving_values_p_q') << Meq.Composer(p,q)
   parmset = ET.unique_stub(ns, 'solved_parameters_a_b') << Meq.Composer(a,b)

   condeqs = []
   condeqs.append(QRU.MeqNode (ns, rr.path, rider,
                               meqclass='Condeq',name='Condeq(a+b,p)',
                              help='Represents equation: a + b = p (=10)',
                              children=[sum_ab, p]))
   condeqs.append(QRU.MeqNode (ns, rr.path, rider,
                               meqclass='Condeq',name='Condeq(a-b,q)',
                              help='Represents equation: a - b = q (=2)',
                              children=[diff_ab, q]))

   solver = QRU.MeqNode (ns, rr.path, rider, meqclass='Solver',
                        name='Solver(*condeqs, solvable=[a,b])',
                        help='Solver', show_recurse=True,
                        children=condeqs,
                        solvable=[a,b])  
   residuals = QRU.MeqNode (ns, rr.path, rider,
                            meqclass='Add', name='residuals',
                           help='The sum of the (abs) condeq residuals',
                           children=condeqs, unop='Abs')
   cc = [solver,residuals,drivers,parmset]
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      parentclass='ReqSeq', result_index=0)











#================================================================================
#================================================================================
#================================================================================
#================================================================================
# It is possible to define a standalone forest (i.e. not part of QuickRef.py) of
# this QR_module. Just load it into the browser, and compile/execute it.
#================================================================================

def _define_forest (ns, **kwargs):
   """Define a standalone forest for standalone use of this QR module"""

   global rider                                 # global because it is used in tdl_jobs
   rider = QRU.create_rider()                   # the rider is a CollatedHelpRecord object
   rootnodename = 'QR_TreeDefinition'                 # The name of the node to be executed...
   path = rootnodename                          # Root of the path-string
   QRU.bundle (ns, path, rider,
              nodes=[QR_TreeDefinition(ns, path, rider)],
              help=__doc__)

   # Finished:
   return True


#--------------------------------------------------------------------------------

# A 'universal TDLRuntimeMenu is defined in QuickRefUtil.py (QRU):

TDLRuntimeMenu(":")
TDLRuntimeMenu("QuickRef runtime options:", QRU)
TDLRuntimeMenu(":")

# For the TDLCompileMenu, see the top of this module


#--------------------------------------------------------------------------------
# Functions that execute the demo tree of this module with different requests.
# Many such functions are defined in QuickRefUtil.py (QRU).
# Make a selection that is suitable for this particular QR module.
#--------------------------------------------------------------------------------

def _tdl_job_execute_1D (mqs, parent):
   return QRU._tdl_job_execute_1D (mqs, parent, rootnode='QR_TreeDefinition')

def _tdl_job_execute_2D (mqs, parent):
   return QRU._tdl_job_execute_2D (mqs, parent, rootnode='QR_TreeDefinition')

def _tdl_job_execute_3D (mqs, parent):
   return QRU._tdl_job_execute_3D (mqs, parent, rootnode='QR_TreeDefinition')

def _tdl_job_execute_4D (mqs, parent):
   return QRU._tdl_job_execute_4D (mqs, parent, rootnode='QR_TreeDefinition')

def _tdl_job_execute_sequence (mqs, parent):
   return QRU._tdl_job_execute_sequence (mqs, parent, rootnode='QR_TreeDefinition')

#--------------------------------------------------------------------------------
# Some functions to dispose of the specified subset of the documentation:
#--------------------------------------------------------------------------------

def _tdl_job_m (mqs, parent):
   """Dummy tdl job that acts as separator in the TDL exec menu.""" 
   return QRU._tdl_job_m (mqs, parent)

def _tdl_job_print_doc (mqs, parent):
   """Print the specified subset of the help doc on the screen"""
   return QRU._tdl_job_print_doc (mqs, parent, rider, header='QR_TreeDefinition')

def _tdl_job_print_hardcopy (mqs, parent):
   """Print a hardcopy of the specified subset of the help doc on the printer.
   NB: The printer may be customized with the runtime options."""
   return QRU._tdl_job_print_hardcopy (mqs, parent, rider, header='QR_TreeDefinition')

def _tdl_job_show_doc (mqs, parent):
   """Show the specified subset of the help doc in a popup"""
   return QRU._tdl_job_show_doc (mqs, parent, rider, header='QR_TreeDefinition')

def _tdl_job_save_doc (mqs, parent):
   """Save the specified subset of the help doc in a file"""
   return QRU._tdl_job_save_doc (mqs, parent, rider, filename='QR_TreeDefinition')



#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

   print '\n** Start of standalone test of: QR_TreeDefinition.py:\n' 

   ns = NodeScope()

   rider = QRU.create_rider()             # CollatedHelpRecord object
   if 1:
      QR_TreeDefinition(ns, 'test', rider=rider)
      if 1:
         print rider.format()
            
   print '\n** End of standalone test of: QR_TreeDefinition.py:\n' 

#=====================================================================================





