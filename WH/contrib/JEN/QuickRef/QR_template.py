"""
QuickRef module: QR_template.py:

Template for the generation of QR_... modules.

Click on the top bookmark ('help_on__how_to_use_this_module')

Instructions for using this template:
- make a copy to a file with a new name (e.g. QR_<name>.py)
- open this file
- replace the word QR_template with QR_<name>
- remove the parts that are marked 'remove'
.   (they generate the general template documentation)
- remove these instructions
- add content.

"""

# file: ../JEN/QuickRef/QR_template.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 01 oct 2008: creation (from QR-template.py)
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
# Start the TDLCompileMenu (TCM): It is added to throughout.
#********************************************************************************

QR_module = 'QR_template'
TCM = QRU.TDLOptionManager.TDLOptionManager(QR_module, prompt=QR_module+' topics')


# Start the file/doc header to be used in exec functions at the bottom.
# It may be modified, depending on the selection of topics.
QR_header = QR_module




#********************************************************************************
# Top-level function, called from QuickRef.py:
#********************************************************************************

TCM.add_option('arg1', range(3))
TCM.add_option('arg2', [-0.1,0.001])
TCM.add_option('arg3', [12,-4.5,complex(3,4),'aa',None], more=False)


#--------------------------------------------------------------------------------

def QR_template (ns, rider):
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
   # global QR_header

   # Remove this part:
   arg1 = TCM.getopt(QR_module+'_arg1', rider) 
   arg2 = TCM.getopt(QR_module+'_arg2', rider) 
   arg3 = TCM.getopt(QR_module+'_arg3', rider) 
   
   # Edit this part:
   if TCM.getopt(QR_module+'_topic1'):
      cc.append(topic1 (ns, rider))
   if TCM.getopt(QR_module+'_topic2'):
      cc.append(topic2 (ns, rider))
   if TCM.getopt(QR_module+'_help'):
      cc.append(HELP (ns, rider))
      
   return QRU.on_exit (ns, rider, cc, mode='group')



#================================================================================
# topic1:
#================================================================================

# Add to the TDLCompileMenu:
TCM.start_of_submenu('topic1')
TCM.add_option('twig', ET.twig_names())
TCM.add_option('arg1', range(2))
TCM.add_option('arg2', range(3))

TCM.start_of_submenu('subtopic1')
TCM.add_option('arg1', range(2))
TCM.add_option('arg2', range(5))
TCM.end_of_submenu()

TCM.end_of_submenu()

#--------------------------------------------------------------------------------

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

   # Remove this part:
   twig = TCM.getopt('_topic1_twig', rider)
   arg1 = TCM.getopt('_topic1_arg1', rider) 
   arg2 = TCM.getopt('_topic1_arg2', rider) 

   if TCM.getopt('topic1_subtopic1'):
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

   # Remove this part:
   arg1 = TCM.getopt('topic1_subtopic1_arg1', rider) 
   arg2 = TCM.getopt('topic1_subtopic1_arg2', rider) 

   return QRU.on_exit (ns, rider, cc)




#================================================================================
# topic2:
#================================================================================

# Add to the TDLCompileMenu:
TCM.start_of_submenu('topic2')
TCM.add_option('arg1', range(2))
TCM.add_option('arg2', range(3), more=False)
TCM.add_option('subtopic1')
TCM.add_option('subtopic2')
TCM.end_of_submenu()

#--------------------------------------------------------------------------------

def topic2 (ns, rider):
   """
   topic2 covers ....
   """
   stub = QRU.on_entry(ns, rider, topic2)
   cc = []

   # Remove this part:
   arg1 = TCM.getopt('topic2_arg1', rider) 
   arg2 = TCM.getopt('topic2_arg2', rider) 

   # Replace this part:
   if TCM.getopt('topic2_subtopic1'):
      cc.append(topic2_subtopic1 (ns, rider))
   if TCM.getopt('topic2_subtopic2'):
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
   ... text enclosed in html 'warning' tags is rendered like this ...
   </warning>

   <error>
   ... text enclosed in html 'error' tags is rendered like this ...
   </error>

   <remark>
   ... text enclosed in html 'remark' tags is rendered like this ...
   </remark>

   <tip>
   ... text enclosed in html 'tip' tags is rendered like this ...
   </tip>

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
# Recommended: some general help(nodes) for this module
#********************************************************************************

# Add to the TDLCompileMenu:
TCM.start_of_submenu('help')
TCM.add_option('on_entry', prompt='help on QRU.on_entry()')
TCM.add_option('on_exit', prompt='help on QRU.on_exit()')
TCM.add_option('helpnode', prompt='help on QRU.helpnode()')
TCM.add_option('twig', prompt='help on ET.twig()')
TCM.radio_buttons(trace=True)
TCM.end_of_submenu()


#--------------------------------------------------------------------------------

def HELP (ns, rider):
   """
   It is possible to define nodes that have no other function than to carry
   a help-text in the quickref_help field of its state record. A bookmark is
   generated automatically, with the 'QuickRef Display' viewer.
   The help-text is also added to the subset of documentation that is accumulated
   by the rider.
   """
   # NB: Avoid the string 'help' in the function name....!!
   stub = QRU.on_entry(ns, rider, HELP)
   cc = []

   # Replace this part:
   if TCM.getopt('_help_on_entry'):
      cc.append(QRU.helpnode (ns, rider, func=QRU.on_entry))
   if TCM.getopt('_help_on_exit'):
      cc.append(QRU.helpnode (ns, rider, func=QRU.on_exit))
   if TCM.getopt('_help_helpnode'):
      cc.append(QRU.helpnode (ns, rider, func=QRU.helpnode))
   if TCM.getopt('_help_twig'):
      cc.append(QRU.helpnode (ns, rider, func=ET.twig))

   return QRU.on_exit (ns, rider, cc, mode='group')








#********************************************************************************
#********************************************************************************
# Standalone forest (i.e. not part of QuickRef.py) of this QR_module.
# Just load it into the browser, and compile/execute it.
#********************************************************************************
#********************************************************************************

# Make the accumulated TDLCompileMenu:
itsTDLCompileMenu = TCM.TDLMenu()

#--------------------------------------------------------------------------------

def _define_forest (ns, **kwargs):
   """Define a standalone forest for standalone use of this QR module"""

   TDLRuntimeMenu(":")
   TDLRuntimeMenu("QR_template runtime options:", QRU)
   TDLRuntimeMenu(":")

   global rootnodename
   rootnodename = 'QR_template'                 # The name of the node to be executed...
   global rider                                 # global because it is used in tdl_jobs
   rider = QRU.create_rider(rootnodename)       # the rider is a CollatedHelpRecord object

   # Make a 'how-to' help-node for the top bookmark:
   QRU.how_to_use_this_module (ns, rider, name='QR_template',
                               topic='template for QR modules')

   # Execute the top-level function, and dispose of the resulting tree:
   QRU.on_exit (ns, rider,
                nodes=[QR_template(ns, rider)],
                mode='group', finished=True)

   # Finished:
   return True


#--------------------------------------------------------------------------------
# Functions for executing the tree:
#--------------------------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
   """Execute the tree, starting at the specified rootnode,
   with the ND request-domain (axes) specified in the
   TDLRuntimeOptions (see QuickRefUtils.py)"""
   return QRU._tdl_job_execute (mqs, parent, rootnode=rootnodename)


def _tdl_job_execute_sequence (mqs, parent):
   return QRU._tdl_job_execute_sequence (mqs, parent, rootnode=rootnodename)


if False:
   def _tdl_job_execute_MS (mqs, parent):
      """Execute a Measurement Set (MS)""" 
      return QRU._tdl_job_execute_MS (mqs, parent, vdm_node='VisDataMux')

#--------------------------------------------------------------------------------
# Some functions to dispose of the specified subset of the documentation:
#--------------------------------------------------------------------------------

def _tdl_job_m (mqs, parent):
   """Dummy tdl job that acts as separator in the TDL exec menu.""" 
   return QRU._tdl_job_m (mqs, parent)



def _tdl_job_print_hardcopy (mqs, parent):
   """
   Print a hardcopy of the specified subset of the help doc on the printer.
   NB: The printer may be customized with the runtime options.
   NB: As an alternative, the file QuickRef.html may be printed from the
   html browser (assuming that the file is updated automatically).
   """
   return QRU._tdl_job_print_hardcopy (mqs, parent, rider, header=QR_header)



def _tdl_job_save_doc_to_QuickRef_html (mqs, parent):
   """
   NB: This should be done automatically in all QR_ modules...
   """
   return QRU.save_to_QuickRef_html (rider, filename=None)



def _tdl_job_show_doc (mqs, parent):
   """
   Show the specified subset of the help doc in a popup.
   Obselete...?
   """
   return QRU._tdl_job_show_doc (mqs, parent, rider, header=QR_header)




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





