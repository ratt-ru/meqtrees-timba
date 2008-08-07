"""
QuickRef module: QR_UserNodes.py:

User-defined nodes:

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

# file: ../JEN/demo/QR_UserNodes.py:
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

from Timba.Contrib.JEN.QuickRef import QuickRefUtil as QRU
from Timba.Contrib.JEN.QuickRef import EasyTwig as ET
from Timba.Contrib.JEN.QuickRef import EasyNode as EN

# import math
# import random
import numpy


#******************************************************************************** 
# TDLCompileMenu (included in QuickRef menu):
#********************************************************************************


oo = TDLCompileMenu("QR_UserNodes topics:",
                    TDLOption('opt_alltopics',"override: include all topics",True),
                    
                    TDLOption('opt_input_twig',"input twig",
                              ET.twig_names(), more=str),
                    
                    TDLMenu("Functional",
                            toggle='opt_Functional'),
                    TDLMenu("PrivateFunction",
                            toggle='opt_PrivateFunction'),
                    TDLMenu("PyNode",
                            toggle='opt_PyNode'),
                    
                    TDLMenu("help",
                            TDLOption('opt_helpnode_twig',"help on EasyTwig.twig()", False),
                            toggle='opt_helpnodes'),
                    
                    toggle='opt_QR_UserNodes')

# Assign the menu to an attribute, for outside visibility:
itsTDLCompileMenu = oo


#********************************************************************************
# Top-level function, called from QuickRef.py:
#********************************************************************************


def QR_UserNodes (ns, rider):
   """
   """
   stub = QRU.on_entry(ns, rider, QR_UserNodes)
   override = opt_alltopics
 
   cc = []
   if override or opt_Functional:
      cc.append(Functional (ns, rider))

   if opt_helpnodes:
      cc.append(make_helpnodes (ns, rider))

   return QRU.on_exit (ns, rider, cc, mode='group')


#********************************************************************************

def make_helpnodes (ns, rider):
   """
   It is possible to define nodes that have no other function than to carry
   a help-text. The latter may be consulted in the quickref_help field in the
   state record of this node (a bookmark is generated automatically). It is
   also added to the subset of documentation that is accumulated by the rider.
   """
   stub = QRU.on_entry(ns, rider, make_helpnodes)
   
   cc = []
   override = opt_alltopics
   if override or opt_helpnode_twig:
      cc.append(QRU.helpnode (ns, rider, name='EasyTwig_twig',
                             help=ET.twig.__doc__, trace=False))

   return QRU.on_exit (ns, rider, cc, mode='group')



#================================================================================
# Functional:
#================================================================================

def Functional (ns, rider):
   """
   """
   stub = QRU.on_entry(ns, rider, Functional)
   cc = []
   override = opt_alltopics
   # if override or opt_Functional_subtopic:
   #    cc.append(Functional_subtopic (ns, rider))
   return QRU.on_exit (ns, rider, cc, mode='group')


#================================================================================

def Functional_subtopic (ns, rider):
   """
   """
   stub = QRU.on_entry(ns, rider, Functional_subtopic)
   override = opt_alltopics
   cc = []
   return QRU.on_exit (ns, rider, cc, mode='group')



#================================================================================
# PrivateFunction:
#================================================================================

def PrivateFunction (ns, rider):
   """
   """
   stub = QRU.on_entry(ns, rider, PrivateFunction)
   override = opt_alltopics
   cc = []
   # if override or opt_PrivateFunction_subtopic:
   #    cc.append(PrivateFunction_subtopic (ns, rider))
   return QRU.on_exit (ns, rider, cc, mode='group')


#================================================================================

def PrivateFunction_subtopic (ns, rider):
   """
   """
   stub = QRU.on_entry(ns, rider, PrivateFunction_subtopic)
   override = opt_alltopics
   cc = []
   return QRU.on_exit (ns, rider, cc, mode='group')



#================================================================================
# PyNode:
#================================================================================

def PyNode (ns, rider):
   """
   """
   stub = QRU.on_entry(ns, rider, PyNode)
   override = opt_alltopics
   cc = []
   # if override or opt_PyNode_subtopic:
   #    cc.append(PyNode_subtopic (ns, rider))
   return QRU.on_exit (ns, rider, cc, mode='group')


#================================================================================

def PyNode_subtopic (ns, rider):
   """
   """
   stub = QRU.on_entry(ns, rider, PyNode_subtopic)
   override = opt_alltopics
   cc = []
   return QRU.on_exit (ns, rider, cc, mode='group')









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


#********************************************************************************
#********************************************************************************
# Standalone forest (i.e. not part of QuickRef.py) of this QR_module.
# Just load it into the browser, and compile/execute it.
#********************************************************************************
#********************************************************************************

def _define_forest (ns, **kwargs):
   """Define a standalone forest for standalone use of this QR module"""

   TDLRuntimeMenu(":")
   TDLRuntimeMenu("QR_UserNodes runtime options:", QRU)
   TDLRuntimeMenu(":")

   global rootnodename
   rootnodename = 'QR_UserNodes'                 # The name of the node to be executed...
   global rider                                  # global because it is used in tdl_jobs
   rider = QRU.create_rider(rootnodename)        # the rider is a CollatedHelpRecord object
   QRU.on_exit (ns, rider,
                nodes=[QR_UserNodes(ns, rider)],
                mode='group')

   # Finished:
   return True


#--------------------------------------------------------------------------------
# Functions that execute the demo tree of this module with different requests.
# Many such functions are defined in QuickRefUtil.py (QRU).
# Make a selection that is suitable for this particular QR module.
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
# Some functions to dispose of the specified subset of the documentation:
#--------------------------------------------------------------------------------

def _tdl_job_m (mqs, parent):
   """Dummy tdl job that acts as separator in the TDL exec menu.""" 
   return QRU._tdl_job_m (mqs, parent)

def _tdl_job_print_doc (mqs, parent):
   """Print the specified subset of the help doc on the screen"""
   return QRU._tdl_job_print_doc (mqs, parent, rider, header='QR_UserNodes')

def _tdl_job_print_hardcopy (mqs, parent):
   """Print a hardcopy of the specified subset of the help doc on the printer.
   NB: The printer may be customized with the runtime options."""
   return QRU._tdl_job_print_hardcopy (mqs, parent, rider, header='QR_UserNodes')

def _tdl_job_show_doc (mqs, parent):
   """Show the specified subset of the help doc in a popup"""
   return QRU._tdl_job_show_doc (mqs, parent, rider, header='QR_UserNodes')

def _tdl_job_save_doc (mqs, parent):
   """Save the specified subset of the help doc in a file"""
   return QRU._tdl_job_save_doc (mqs, parent, rider, filename='QR_UserNodes')




#********************************************************************************
#********************************************************************************
# Standalone test (without the browser):
#********************************************************************************
#********************************************************************************

if __name__ == '__main__':

   print '\n** Start of standalone test of: QR_UserNodes.py:\n' 

   ns = NodeScope()

   rider = QRU.create_rider()             # CollatedHelpRecord object
   if 1:
      QR_UserNodes(ns, 'test', rider=rider)
      if 1:
         print rider.format()
            
   print '\n** End of standalone test of: QR_UserNodes.py:\n' 

#=====================================================================================





