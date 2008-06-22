"""
QuickRef module: QR_PyNodePlot.py:

PyNodes for plotting (based on PyNodeNamedGroups class)

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

# file: ../JEN/demo/QR_PyNodePlot.py:
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

from Timba.Contrib.JEN.pylab import PyNodeNamedGroups as PNNG
from Timba.Contrib.JEN.pylab import PyNodePlot as PNP
from Timba.Contrib.JEN.pylab import PyNodePlotVis22 as PNPVis22

# import math
# import random
import numpy


#******************************************************************************** 
# TDLCompileMenu (included in QuickRef menu):
#********************************************************************************


TDLCompileMenu("QR_PyNodePlot topics:",
               TDLOption('opt_alltopics',"override: include all topics",True),

               TDLOption('opt_input_twig',"input twig",
                         ET.twig_names(), more=str),

               TDLMenu("PyNodePlot",
                       toggle='opt_PyNodePlot'),

               TDLMenu("PlotVis22",
                       toggle='opt_PlotVis22'),

               TDLMenu("PyNodeNamedGroups",
                       toggle='opt_PyNodeNamedGroups'),

               TDLMenu("help",
                       TDLOption('opt_helpnode_twig',"help on EasyTwig.twig()", False),
                       toggle='opt_helpnodes'),

               toggle='opt_QR_PyNodePlot')



#********************************************************************************
# Top-level function, called from QuickRef.py:
#********************************************************************************


def QR_PyNodePlot (ns, path, rider):
   """
   """
   rr = QRU.on_entry(QR_PyNodePlot, path, rider)
 
   cc = []
   if opt_alltopics or opt_PyNodePlot:
      cc.append(PyNodePlot (ns, rr.path, rider))
   if opt_alltopics or opt_PlotVis22:
      cc.append(PlotVis22 (ns, rr.path, rider))

   if opt_alltopics or opt_PyNodeNamedGroups:
      cc.append(PyNodeNamedGroups (ns, rr.path, rider))

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
   
   cc = []
   if opt_alltopics or opt_helpnode_twig:
      cc.append(QRU.helpnode (ns, rr.path, rider, name='EasyTwig_twig',
                             help=ET.twig.__doc__, trace=False))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)





#================================================================================
# PyNodePlot:
#================================================================================

def PyNodePlot (ns, path, rider):
   """
   """
   rr = QRU.on_entry(PyNodePlot, path, rider,
                     help=PNP.PyNodePlot.__doc__)
   cc = []
   children = [ns << 0.1, ns << 1.1]
   pynode = ns['PyNodePlot'] << Meq.PyNode(children=children,
                                                  # child_labels=labels,
                                                  class_name='PyNodePlot',
                                                  # groupspecs=gs,
                                                  module_name=PNP.__file__)
   cc.append(pynode)
   # if opt_alltopics or opt_PyNodePlot_subtopic:
      # cc.append(PyNodePlot_subtopic (ns, rr.path, rider))
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      bookmark=cc[0], viewer='Record Browser',
                      parentclass='ReqSeq', result_index=0)


#================================================================================

def PyNodePlot_subtopic (ns, path, rider):
   """
   """
   rr = QRU.on_entry(PyNodePlot_subtopic, path, rider)
   cc = []
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      parentclass='ReqSeq', result_index=0)



#================================================================================
# PlotVis22:
#================================================================================

def PlotVis22 (ns, path, rider):
   """
   """
   rr = QRU.on_entry(PlotVis22, path, rider,
                     help=PNPVis22.PlotVis22.__doc__)
   cc = []
   [uu,uv,coh,labels] = PNPVis22.make_uvdata(ns, n=4)
   pynode = ns['PlotVis22'] << Meq.PyNode(children=coh,
                                          child_labels=labels,
                                          class_name='PlotVis22',
                                          # groupspecs=gs,
                                          module_name=PNPVis22.__file__)
   cc.append(pynode)
   # if opt_alltopics or opt_PyNodePlotVis22_subtopic:
      # cc.append(PyNodePlotVis22_subtopic (ns, rr.path, rider))
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      bookmark=cc[0], viewer='Pylab Plotter',
                      parentclass='ReqSeq', result_index=0)


#================================================================================

def PyNodePlotVis22_subtopic (ns, path, rider):
   """
   """
   rr = QRU.on_entry(PyNodePlotVis22_subtopic, path, rider)
   cc = []
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      parentclass='ReqSeq', result_index=0)




#================================================================================
# PyNodeNamedGroups:
#================================================================================

def PyNodeNamedGroups (ns, path, rider):
   """
   """
   rr = QRU.on_entry(PyNodeNamedGroups, path, rider,
                     help=PNNG.PyNodeNamedGroups.__doc__)
   cc = []
   children = [ns << 0.1, ns << 1.1]
   pynode = ns['PyNodeNamedGroups'] << Meq.PyNode(children=children,
                                                  # child_labels=labels,
                                                  class_name='PyNodeNamedGroups',
                                                  # groupspecs=gs,
                                                  module_name=PNNG.__file__)
   cc.append(pynode)
   # if opt_alltopics or opt_PyNodeNamedGroups_subtopic:
      # cc.append(PyNodeNamedGroups_subtopic (ns, rr.path, rider))
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      bookmark=cc[0], viewer='Record Browser',
                      parentclass='ReqSeq', result_index=0)


#================================================================================

def PyNodeNamedGroups_subtopic (ns, path, rider):
   """
   """
   rr = QRU.on_entry(PyNodeNamedGroups_subtopic, path, rider)
   cc = []
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      parentclass='ReqSeq', result_index=0)











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
   rootnodename = 'QR_PyNodePlot'                 # The name of the node to be executed...
   path = rootnodename                          # Root of the path-string
   QRU.bundle (ns, path, rider,
              nodes=[QR_PyNodePlot(ns, path, rider)],
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
   return QRU._tdl_job_execute_1D (mqs, parent, rootnode='QR_PyNodePlot')

def _tdl_job_execute_2D (mqs, parent):
   return QRU._tdl_job_execute_2D (mqs, parent, rootnode='QR_PyNodePlot')

def _tdl_job_execute_3D (mqs, parent):
   return QRU._tdl_job_execute_3D (mqs, parent, rootnode='QR_PyNodePlot')

def _tdl_job_execute_4D (mqs, parent):
   return QRU._tdl_job_execute_4D (mqs, parent, rootnode='QR_PyNodePlot')

def _tdl_job_execute_sequence (mqs, parent):
   return QRU._tdl_job_execute_sequence (mqs, parent, rootnode='QR_PyNodePlot')

#--------------------------------------------------------------------------------
# Some functions to dispose of the specified subset of the documentation:
#--------------------------------------------------------------------------------

def _tdl_job_m (mqs, parent):
   """Dummy tdl job that acts as separator in the TDL exec menu.""" 
   return QRU._tdl_job_m (mqs, parent)

def _tdl_job_print_doc (mqs, parent):
   """Print the specified subset of the help doc on the screen"""
   return QRU._tdl_job_print_doc (mqs, parent, rider, header='QR_PyNodePlot')

def _tdl_job_print_hardcopy (mqs, parent):
   """Print a hardcopy of the specified subset of the help doc on the printer.
   NB: The printer may be customized with the runtime options."""
   return QRU._tdl_job_print_hardcopy (mqs, parent, rider, header='QR_PyNodePlot')

def _tdl_job_show_doc (mqs, parent):
   """Show the specified subset of the help doc in a popup"""
   return QRU._tdl_job_show_doc (mqs, parent, rider, header='QR_PyNodePlot')

def _tdl_job_save_doc (mqs, parent):
   """Save the specified subset of the help doc in a file"""
   return QRU._tdl_job_save_doc (mqs, parent, rider, filename='QR_PyNodePlot')




#********************************************************************************
#********************************************************************************
# Standalone test (without the browser):
#********************************************************************************
#********************************************************************************

if __name__ == '__main__':

   print '\n** Start of standalone test of: QR_PyNodePlot.py:\n' 

   ns = NodeScope()

   if 1:
      rider = QRU.create_rider()             # CollatedHelpRecord object
      QR_PyNodePlot(ns, 'test', rider=rider)
      if 1:
         print rider.format()

   print '\n** End of standalone test of: QR_PyNodePlot.py:\n' 

#=====================================================================================





