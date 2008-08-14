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

from Timba.Contrib.JEN.QuickRef import QuickRefUtil as QRU
from Timba.Contrib.JEN.QuickRef import EasyTwig as ET
from Timba.Contrib.JEN.QuickRef import EasyNode as EN


# import math
# import random
import numpy


#******************************************************************************** 
# TDLCompileMenu (included in QuickRef menu):
#********************************************************************************


oo = TDLCompileMenu("QR_TreeDefinition topics:",
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

# Assign the menu to an attribute, for outside visibility:
itsTDLCompileMenu = oo


#********************************************************************************
# Top-level function, called from QuickRef.py:
#********************************************************************************


def QR_TreeDefinition (ns, rider):
   """
   """
   stub = QRU.on_entry(ns, rider, QR_TreeDefinition)
   cc = []
   override = opt_alltopics
   if override or opt_nodenames:
      cc.append(nodenames (ns, rider))
   if override or opt_TDL:
      cc.append(TDL (ns, rider))
   if override or opt_TDLOptions:
      cc.append(TDLOptions (ns, rider))
   if override or opt_bookmarks:
      cc.append(bookmarks (ns, rider))

   if opt_helpnodes:
      cc.append(make_helpnodes (ns, rider))

   return QRU.on_exit (ns, rider, cc, mode='group')



#********************************************************************************
# 2nd tier: Functions called from the top function above:
#********************************************************************************

def make_helpnodes (ns, rider):
   """
   It is possible to define nodes that have no other function than to carry
   a help-text. The latter may be consulted in the quickref_help field in the
   state record of this node (a bookmark is generated automatically). It is
   also added to the subset of documentation that is accumulated by the rider.
   """
   stub = QRU.on_entry(ns, rider, make_helpnodes)
   override = opt_alltopics
   
   cc = []
   if override or opt_helpnode_twig:
      cc.append(QRU.helpnode (ns, rider, func=ET.twig))

   return QRU.on_exit (ns, rider, cc, mode='group')


#--------------------------------------------------------------------------------

def nodenames (ns, rider):
   """
   """
   stub = QRU.on_entry(ns, rider, nodenames)
   cc = []
   override = opt_alltopics
   # if override or opt_nodenames_xxx:
   #    cc.append(nodenames_xxx (ns, rider))
   return QRU.on_exit (ns, rider, cc, mode='group')


#--------------------------------------------------------------------------------

def TDL (ns, rider):
   """
   """
   stub = QRU.on_entry(ns, rider, TDL)
   cc = []
   override = opt_alltopics
   # if override or opt_TDL_xxx:
   #    cc.append(TDL_xxx (ns, rider))
   return QRU.on_exit (ns, rider, cc, mode='group')


#--------------------------------------------------------------------------------

def TDLOptions (ns, rider):
   """
   """
   stub = QRU.on_entry(ns, rider, TDLOptions)
   cc = []
   override = opt_alltopics
   # if override or opt_TDLOptions_xxx:
   #    cc.append(TDLOptions_xxx (ns, rider))
   return QRU.on_exit (ns, rider, cc, mode='group')


#--------------------------------------------------------------------------------

def bookmarks (ns, rider):
   """
   """
   stub = QRU.on_entry(ns, rider, bookmarks)
   cc = []
   override = opt_alltopics
   # if override or opt_bookmarks_xxx:
   #    cc.append(bookmarks_xxx (ns, rider))
   return QRU.on_exit (ns, rider, cc, mode='group')




#********************************************************************************
#********************************************************************************
#********************************************************************************
# 3rd tier: Functions called from functions at the 2nd tier above
#********************************************************************************
#********************************************************************************


#================================================================================
# nodenames_... 
#================================================================================

def nodenames_xxx (ns, rider):
   """
   """
   stub = QRU.on_entry(ns, rider, nodenames_xxx)
   cc = []
   override = opt_alltopics
   return QRU.on_exit (ns, rider, cc, mode='group')











#================================================================================
#================================================================================
#================================================================================
#================================================================================
# It is possible to define a standalone forest (i.e. not part of QuickRef.py) of
# this QR_module. Just load it into the browser, and compile/execute it.
#================================================================================

def _define_forest (ns, **kwargs):
   """Define a standalone forest for standalone use of this QR module"""

   TDLRuntimeMenu(":")
   TDLRuntimeMenu("QR_TreeDefinition runtime options:", QRU)
   TDLRuntimeMenu(":")

   global rootnodename
   rootnodename = 'QR_TreeDefinition'           # The name of the node to be executed...
   global rider                                 # global because it is used in tdl_jobs
   rider = QRU.create_rider(rootnodename)       # the rider is a CollatedHelpRecord object
   QRU.on_exit (ns, rider,
                nodes=[QR_TreeDefinition(ns, rider)],
                mode='group')

   # Finished:
   return True


#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
   """Execute the tree, starting at the specified rootnode,
   with the ND request-domain (axes) specified in the
   TDLRuntimeOptions (see QuickRefUtils.py)"""
   return QRU._tdl_job_execute (mqs, parent, rootnode=rootnodename)

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





