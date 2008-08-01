"""
QuickRef module: QR_template.py:

Template for the generation of QR_... modules.

Just:
- make a copy with a new name (e.g. QR_<name>.py),
- replace the word QR_template with QR_<newname>,
- remove the parts that are marked 'remove'
.   (they generate the general template documentation)
and add content.

This module may be called from the module QuickRef.py.
But it may also be used stand-alone.
-- Load the TDL script into the meqbrowser.
-- Using TDL Options, select categories to be included,
.    and customize parameters and input (nodes).
-- Compile: The tree will appear in the leftmost panel.
-- Use the bookmarks menu to select one or more views.
-- Use TDL Exec to execute the tree: The views will come alive.
-- Use TDL Exec to show or print or save the hierarchical help
.    for the selected categories.
"""

# file: ../JEN/QuickRef/QR_template.py:
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
from Timba.Contrib.JEN.QuickRef import EasyFormat as EF

from Timba.Contrib.JEN.pylab import PyNodeNamedGroups as PNNG
from Timba.Contrib.JEN.pylab import PyNodePlot as PNP

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
                       TDLOption('opt_topic1_alltopics',
                                 "override: include all topic1 sub-topics",False),
                       TDLOption('opt_topic1_subtopic1', "topic1 subtopic1",False),
                       toggle='opt_topic1'),

               TDLMenu("topic2",
                       TDLOption('opt_topic2_alltopics',
                                 "override: include all topic2 sub-topics",False),
                       TDLOption('opt_topic2_subtopic1', "topic2 subtopic1",False),
                       toggle='opt_topic2'),

               TDLMenu("help",
                       TDLOption('opt_allhelpnodes',"override: include all helpnodes",False),
                       TDLOption('opt_helpnode_on_entry',"help on QuickRefUtil.on_entry()", False),
                       TDLOption('opt_helpnode_on_exit',"help on QuickRefUtil.on_exit()", False),
                       TDLOption('opt_helpnode_helpnode',"help on QuickRefUtil.helpnode()", False),
                       TDLOption('opt_helpnode_twig',"help on EasyTwig.twig()", False),
                       toggle='opt_helpnodes'),

               toggle='opt_QR_template')



#********************************************************************************
# Top-level function, called from QuickRef.py:
#********************************************************************************

header = 'QR_template'                    # used in exec functions at the bottom

def QR_template (ns, rider):
# def toplevel (ns, rider):
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

   <function_code>
      def func (ns, rider):
         ... function doc-string enclosed in triple-quotes
         stub = QRU.on_entry(ns, rider, func)
         cc = []
         ... function body, in which nodes are appended to the list cc ...
         return QRU.on_exit (ns, rider, cc)
   </function_code>

   The first argument of QRU.on_entry() is the function itself, without ().
   It returns a record rr, the fields of which (rr.path and rr.help) are
   used in the function (or rather, passed to other QRU functions).
   
   The last statement (return QRU.on_exit()) bundles the nodes (cc) in a
   convenient way, and returns the resulting parent node of the bundle.
   Its syntax is given below.
   """
   stub = QRU.on_entry(ns, rider, QR_template)
   cc = []
   override = opt_alltopics
   global header

   # Edit this part:
   if override or opt_topic1:
      cc.append(topic1 (ns, rider))
   if override or opt_topic2:
      cc.append(topic2 (ns, rider))

   if opt_helpnodes:
      cc.append(make_helpnodes (ns, rider))

   return QRU.on_exit (ns, rider, cc, mode='group')


#********************************************************************************

def make_helpnodes (ns, rider):
   """
   It is possible to define nodes that have no other function than to carry
   a help-text in the quickref_help field of its state record. A bookmark is
   generated automatically, with the 'QuickRef Display' viewer.
   The help-text is also added to the subset of documentation that is accumulated
   by the rider.
   """
   stub = QRU.on_entry(ns, rider, make_helpnodes)
   
   override = opt_alltopics or opt_allhelpnodes
   cc = []

   # Replace this part:
   if override or opt_helpnode_on_entry:
      cc.append(QRU.helpnode (ns, rider, func=QRU.on_entry))
   if override or opt_helpnode_on_exit:
      cc.append(QRU.helpnode (ns, rider, func=QRU.on_exit))
   if override or opt_helpnode_helpnode:
      cc.append(QRU.helpnode (ns, rider, func=QRU.helpnode))
   if override or opt_helpnode_twig:
      cc.append(QRU.helpnode (ns, rider, func=ET.twig))

   return QRU.on_exit (ns, rider, cc, mode='group')



#================================================================================
# topic1:
#================================================================================

def topic1 (ns, rider):
   """
   NB: This text should be replaced with an overall explanation of this 'topic'
   of this QR module.

   The 'topic' functions are '2nd-tier' functions, i.e. they are called from the
   top-level function QR_template() above. They usually call one or more functions
   that represent different 'views' (e.g. demonstration trees of particular aspects)
   of this topic. The general structure is:

   <function_code>
     def topic1 (ns, rider):
          stub = QRU.on_entry(ns, rider, topic1)
          cc = []
          override = opt_topic1_alltopics
          if override or opt_topic1_subtopic:
              cc.append(topic1_subtopic (ns, rider))
          return QRU.on_exit (ns, rider, cc)
   </function_code>

   It is sometimes useful to read some general TDLCompileOptions here, and pass
   them to the subtopic functions as extra arguments.
   """
   stub = QRU.on_entry(ns, rider, topic1)
   cc = []
   override = opt_alltopics

   if override or opt_topic1_subtopic1:
      cc.append(topic1_subtopic1 (ns, rider))

   return QRU.on_exit (ns, rider, cc, mode='group')


#================================================================================

def topic1_subtopic1 (ns, rider):
   """
   NB: This text should be replaced with an overall explanation of this subtopic of
   this topic of this QR module.

   A subtopic (topic_subtopic()) demonstrates a particular aspect of a given topic.
   It usually generates a group of 4-9 related nodes that may be displayed on a
   single bookmark page.

   The EasyTwig (ET) module may be used to generate small standard subtrees (twigs)
   that may serve as (user-defined) inputs to a demonstration subtree. Its syntax is
   given as a separate 'helpnode' item above. 
   """
   stub = QRU.on_entry(ns, rider, topic1_subtopic1)
   cc = []

   return QRU.on_exit (ns, rider, cc)




#================================================================================
# topic2:
#================================================================================

def topic2 (ns, rider):
   """
   topic2 covers ....
   """
   stub = QRU.on_entry(ns, rider, topic2)
   cc = []
   override = opt_alltopics

   if override or opt_topic2_subtopic1:
      cc.append(topic2_subtopic1 (ns, rider))
   if override or opt_topic2_subtopic2:
      cc.append(topic2_subtopic2 (ns, rider))

   return QRU.on_exit (ns, rider, cc, mode='group')


#================================================================================

def topic2_subtopic1 (ns, rider):
   """
   topic2_subtopic1 treats ....
   """
   stub = QRU.on_entry(ns, rider, topic2_subtopic1)
   cc = []

   return QRU.on_exit (ns, rider, cc)

#================================================================================

def topic2_subtopic2 (ns, rider):
   """
   topic2_subtopic2 treats ....

   <warning>
   ... text enclosed in 'html' warning tags is rendered like this ...
   </warning>

   <error>
   ... text enclosed in 'html' error tags is rendered like this ...
   </error>

   <remark>
   ... text enclosed in 'html' remark tags is rendered like this ...
   </remark>

   Text enclosed in 'html' function_code tags may be used to include the function body in the help.
   Just copy the entire function body between the tags in the function doc-string (making sure that
   it does not contain any double-quotes). When the function body is modified, just re-copy it.
   (NB: it would be nice if there were a python function that turned the function body into s atring...)

   <function_code>
   stub = QRU.on_entry(ns, rider, topic2_subtopic2)
   cc = []

   twig = ET.twig(ns,'f')

   for q in ['Sin','Cos','Tan']:
      cc.append(stub(q) << getattr(Meq,q)(twig))
      cc.append('** inserted extra help on '+q+' as string items in nodes (cc) **')

   for q in ['Asin','Acos','Atan']:
      cc.append(dict(node=stub(q) << getattr(Meq,q)(twig)))

   bhelp = \"\"\"
   It is also possible to append extra bundle help
   via the .on_exit() help argument.
   \"\"\"
   return QRU.on_exit (ns, rider, cc, help=bhelp)
   </function_code>


   """

   stub = QRU.on_entry(ns, rider, topic2_subtopic2)
   cc = []

   twig = ET.twig(ns,'f')

   for q in ['Sin','Cos','Tan']:
      cc.append(stub(q) << getattr(Meq,q)(twig))
      cc.append('** inserted extra help on '+q+' as string items in nodes (cc) **')

   for q in ['Asin','Acos','Atan']:
      cc.append(dict(node=stub(q) << getattr(Meq,q)(twig)))

   bhelp = """
   It is also possible to append extra bundle help
   via the .on_exit() help argument.
   """
   return QRU.on_exit (ns, rider, cc, help=bhelp)











#********************************************************************************
#********************************************************************************
# Standalone forest (i.e. not part of QuickRef.py) of this QR_module.
# Just load it into the browser, and compile/execute it.
#********************************************************************************
#********************************************************************************

def _define_forest (ns, **kwargs):
   """Define a standalone forest for standalone use of this QR module"""

   global rootnodename
   rootnodename = 'QuickRef'                 # The name of the node to be executed...
   global rider                                 # global because it is used in tdl_jobs
   rider = QRU.create_rider(rootnodename)       # the rider is a CollatedHelpRecord object
   QRU.on_exit (ns, rider,
                nodes=[QR_template(ns, rider)],
                mode='group')

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
   return QRU._tdl_job_execute_1D (mqs, parent, rootnode=rootnodename)

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





