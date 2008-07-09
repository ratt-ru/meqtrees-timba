"""
QuickRef module: QR_template.py:

Template for the generation of QR_... modules.
Just:
- make a copy with a new name (e.g. QR_<name>.py),
- replace the word QR_template with QR_<newname>,
- remove the 'template' help-texts from the functions,
- remove any help=... from the QRU.on_entry(..., help=...) functions
and add content.

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

# file: ../JEN/demo/QR_template.py:
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


TDLCompileMenu("QR_template topics:",
               TDLOption('opt_alltopics',"override: include all topics",True),

               TDLOption('opt_input_twig',"input twig",
                         ET.twig_names(), more=str),

               TDLMenu("topic1",
                       toggle='opt_topic1'),
               TDLMenu("topic2",
                       toggle='opt_topic2'),

               TDLMenu("help",
                       TDLOption('opt_helpnode_twig',"help on EasyTwig.twig()", False),
                       toggle='opt_helpnodes'),

               toggle='opt_QR_template')



#********************************************************************************
# Top-level function, called from QuickRef.py:
#********************************************************************************

header = 'QR_template'                    # used in exec functions at the bottom

def QR_template (ns, path, rider):
   """
   NB: This text should be replaced with an overall explanation of the
   MeqTree functionality that is covered in this QR module.
   
   This top-level function has the same name as the module. Its role is to
   include the user-specified parts (topics) of QuickRef documentation by calling
   lower-level functions according to the TDLCompileMenu options.
   This function may be called from QuickRef.py, but also from its standalone
   _define_forest() below, or from the local testing function (without the browser).

   The functions in a QR module use utility functions in QuickRefUtil.py (QRU),
   which do the main work of collecting and organising the hierarchical help,
   and of creating and bundling the nodes of the demonstration trees.

   All functions in a QR module have the following general structure:

   .   def funcname (ns, path, rider [,optional arguments]):
   .      <help-text for this function enclosed in triple-quotes>
   .      rr = QRU.on_entry(funcname, path, rider)
   .      cc = []
   .      <function body, in which nodes are appended to the list cc>
   .      return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)

   The first argument of QRU.on_entry() is the function itself, without ().
   It returns a record rr, the fields of which (rr.path and rr.help) are
   used in the function (or rather, passed to other QRU functions).
   
   The last statement (return QRU.bundle()) bundles the nodes (cc) in a
   convenient way, and returns the resulting parent node of the bundle.
   Its syntax is given below.
   """
   rr = QRU.on_entry(QR_template, path, rider)
   cc = []
   override = opt_alltopics
   global header

   # Remove this part:
   cc.append(QRU.helpnode (ns, rr.path, rider, func=QRU.bundle))

   # Edit this part:
   if override or opt_topic1:
      cc.append(topic1 (ns, rr.path, rider))
   if override or opt_topic2:
      cc.append(topic2 (ns, rr.path, rider))

   if opt_helpnodes:
      cc.append(make_helpnodes (ns, rr.path, rider))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)


#********************************************************************************

def make_helpnodes (ns, path, rider):
   """
   It is possible to define nodes that have no other function than to carry
   a help-text. The latter may be consulted in the quickref_help field in the
   state record of this node (a bookmark is generated automatically). It is
   also added to the subset of documentation that is accumulated by the rider.
   """
   rr = QRU.on_entry(make_helpnodes, path, rider)
   
   override = opt_alltopics
   cc = []

   if override or opt_helpnode_twig:
      cc.append(QRU.helpnode (ns, rr.path, rider, func=ET.twig))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)



#================================================================================
# topic1:
#================================================================================

def topic1 (ns, path, rider):
   """
   NB: This text should be replaced with an overall explanation of this 'topic'
   of this QR module.

   The topic functions are '2nd-tier' functions, i.e. they are called from the
   top-level function QR_template() above. They usually call one or more functions
   that represent different 'views' (e.g. demonstration trees of particular aspects)
   of this topic. The general structure is:

   .   def topic1 (ns, path, rider):
   .       rr = QRU.on_entry(topic1, path, rider)
   .       cc = []
   .       if override or opt_topic1_subtopic:
   .           cc.append(topic1_subtopic (ns, rr.path, rider))
   .       return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)

   It is sometimes useful to read some general TDLCompileOptions here, and pass
   them to the lower-level functions as extra arguments.
   """
   rr = QRU.on_entry(topic1, path, rider)
   cc = []
   override = opt_alltopics

   if override or opt_topic1_subtopic:
      cc.append(topic1_subtopic (ns, rr.path, rider))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)


#================================================================================

def topic1_subtopic (ns, path, rider):
   """
   NB: This text should be replaced with an overall explanation of this subtopic of
   this topic of this QR module.

   A subtopic (<topic>_<subtopic>()) demonstrates a particular aspect of a given topic.
   It usually generates a group of 4-9 related nodes that may be displayed on a
   single bookmark page.

   In addition to the mandatory QRU.on_entry() and QRU.bundle(), a function maye call
   the function QRU.MeqNode() zero or more times. This function creates the specified
   MeqNode, with help attached to the quickref_help field of its state record.
   The syntax of QRU.MeqNode() is given below.

   NB: Nodes for a subtopic subtree may also be defined directly (i.e. without using the
   function QRU.MeqNode(). For those cases, the EasyNode (EN) module provides some useful
   services to generate unique (i.e. non-clashing) or reusable nodestubs/names. Their
   syntax is given below.

   The EasyTwig (ET) module may also be used to generate small standard subtrees (twigs)
   that may serve as (user-defined) inputs to a demonstration subtree. Its syntax is
   given as a separate 'helpnode' item above. 
   """
   rr = QRU.on_entry(topic1_subtopic, path, rider)
   cc = []

   # Remove this part: 
   cc.append(QRU.helpnode (ns, rr.path, rider, func=QRU.MeqNode))
   cc.append(QRU.helpnode (ns, rr.path, rider, func=EN.nodestub))
   cc.append(QRU.helpnode (ns, rr.path, rider, func=EN.unique_stub))
   cc.append(QRU.helpnode (ns, rr.path, rider, func=EN.unique_node))
   cc.append(QRU.helpnode (ns, rr.path, rider, func=EN.reusenode))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      parentclass='ReqSeq', result_index=0)




#================================================================================
# topic2:
#================================================================================

def topic2 (ns, path, rider):
   """
   topic2 covers ....
   """
   rr = QRU.on_entry(topic2, path, rider)
   cc = []
   override = opt_alltopics

   # if override or opt_topic2_subtopic:
   #    cc.append(topic2_subtopic (ns, rr.path, rider))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)


#================================================================================

def topic2_subtopic (ns, path, rider):
   """
   topic2_subtopic treats ....
   """
   rr = QRU.on_entry(topic2_subtopic, path, rider)
   cc = []
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)











#********************************************************************************
#********************************************************************************
# Standalone forest (i.e. not part of QuickRef.py) of this QR_module.
# Just load it into the browser, and compile/execute it.
#********************************************************************************
#********************************************************************************

def _define_forest (ns, **kwargs):
   """Define a standalone forest for standalone use of this QR module"""

   global rider                                 # global because it is used in tdl_jobs
   rider = QRU.create_rider()                   # the rider is a CollatedHelpRecord object
   rootnodename = 'QR_template'                 # The name of the node to be executed...
   path = rootnodename                          # Root of the path-string
   QRU.bundle (ns, path, rider,
               nodes=[QR_template(ns, path, rider)],
               help=__doc__)

   # Finished:
   QRU.ET.EN.bundle_orphans(ns)
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

def _tdl_job_execute_1D_f (mqs, parent):
   return QRU._tdl_job_execute_1D (mqs, parent, rootnode='QR_template')

def _tdl_job_execute_2D_ft (mqs, parent):
   return QRU._tdl_job_execute_ft (mqs, parent, rootnode='QR_template')

def _tdl_job_execute_3D_ftL (mqs, parent):
   return QRU._tdl_job_execute_ftL (mqs, parent, rootnode='QR_template')

def _tdl_job_execute_4D_ftLM (mqs, parent):
   return QRU._tdl_job_execute_ftLM (mqs, parent, rootnode='QR_template')

def _tdl_job_execute_sequence (mqs, parent):
   return QRU._tdl_job_execute_sequence (mqs, parent, rootnode='QR_template')

#--------------------------------------------------------------------------------
# Some functions to dispose of the specified subset of the documentation:
#--------------------------------------------------------------------------------

def _tdl_job_m (mqs, parent):
   """Dummy tdl job that acts as separator in the TDL exec menu.""" 
   return QRU._tdl_job_m (mqs, parent)

def _tdl_job_print_doc (mqs, parent):
   """Print the specified subset of the help doc on the screen"""
   return QRU._tdl_job_print_doc (mqs, parent, rider, header=header)

def _tdl_job_print_hardcopy (mqs, parent):
   """Print a hardcopy of the specified subset of the help doc on the printer.
   NB: The printer may be customized with the runtime options."""
   return QRU._tdl_job_print_hardcopy (mqs, parent, rider, header=header)

def _tdl_job_show_doc (mqs, parent):
   """Show the specified subset of the help doc in a popup"""
   return QRU._tdl_job_show_doc (mqs, parent, rider, header=header)

def _tdl_job_save_doc (mqs, parent):
   """Save the specified subset of the help doc in a file"""
   return QRU._tdl_job_save_doc (mqs, parent, rider, filename=header)




#********************************************************************************
#********************************************************************************
# Standalone test (without the browser):
#********************************************************************************
#********************************************************************************

if __name__ == '__main__':

   print '\n** Start of standalone test of: QR_template.py:\n' 

   ns = NodeScope()

   rider = QRU.create_rider()             # CollatedHelpRecord object
   if 1:
      QR_template(ns, 'test', rider=rider)
      if 1:
         print rider.format()
            
   print '\n** End of standalone test of: QR_template.py:\n' 

#=====================================================================================





