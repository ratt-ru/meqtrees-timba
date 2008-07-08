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
from Timba.Contrib.JEN.QuickRef import EasyBundle as EB
from Timba.Contrib.JEN.QuickRef import EasyTwig as ET
from Timba.Contrib.JEN.QuickRef import EasyNode as EN

from Timba.Contrib.JEN.pylab import PyNodeNamedGroups as PNNG
from Timba.Contrib.JEN.pylab import PyNodePlot as PNP
from Timba.Contrib.JEN.pylab import PyNodePlotVis22 as PNPVis22
from Timba.Contrib.JEN.pylab import PyNodePlotXY as PNPXY

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
                       TDLMenu("basic",
                               toggle='opt_PyNodePlot_basic'),
                       TDLMenu("scalars",
                               toggle='opt_PyNodePlot_scalars'),
                       TDLMenu("complex",
                               toggle='opt_PyNodePlot_complex'),
                       TDLMenu("tensors",
                               toggle='opt_PyNodePlot_tensors'),
                       TDLMenu("concat",
                               toggle='opt_PyNodePlot_concat'),
                       toggle='opt_PyNodePlot'),

               TDLMenu("PlotVis22",
                       toggle='opt_PlotVis22'),

               TDLMenu("PyNodeNamedGroups",
                       toggle='opt_PyNodeNamedGroups'),

               TDLMenu("help",
                       # TDLOption('opt_helpnode_bundle',"help on EasyBundle.bundle()", False),
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
   if opt_alltopics or opt_helpnode_bundle:
      cc.append(QRU.helpnode (ns, rr.path, rider, name='EasyBundle_bundle',
                             help=ET.bundle.__doc__, trace=False))
   if opt_alltopics or opt_helpnode_twig:
      cc.append(QRU.helpnode (ns, rr.path, rider, name='EasyTwig_twig',
                             help=ET.twig.__doc__, trace=False))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)





#================================================================================
# PyNodePlot:
#================================================================================

def PyNodePlot (ns, path, rider):
   """
   Basic plotting, using the convenience function PNP.pynode_PyNodePlot(),
   which creates a MeqPyNode of class PyNodePlot, which is derived
   from PyNodeNamedGroups.

   In order to make things easy, standard plots may be specified by means
   of a string (e.g. 'XXYY'), and customized by means of keyword arguments.
   This should take care of the vast majority of plots. More advanced use
   requires the input of valid groupspecs/plotspecs records.

   In the examples shown here, the MeqPyNode state record is often shown next
   to the plot itself, because it contains a lot of detailed information:
   - pynode_help:   the __doc__ string of the PyNodePlot class
   - groupspecs:    the input group specification record
   - plotspecs:     the input plot specification record
   - quickref_help: the actual call used to create this MeqPyNode,
   .                including the values of the custimizing keyword arguments.
   - cache.result (available after execution):
   .    - namedgroups: The detailed list of available named groups
   .    - plotdefs:    The detailed list of (sub)plot definitions
   """
   rr = QRU.on_entry(PyNodePlot, path, rider)
   cc = []
   if opt_alltopics or opt_PyNodePlot_basic:
      cc.append(PyNodePlot_basic (ns, rr.path, rider))
   if opt_alltopics or opt_PyNodePlot_scalars:
      cc.append(PyNodePlot_scalars (ns, rr.path, rider))
   if opt_alltopics or opt_PyNodePlot_complex:
      cc.append(PyNodePlot_complex (ns, rr.path, rider))
   if opt_alltopics or opt_PyNodePlot_tensors:
      cc.append(PyNodePlot_tensors (ns, rr.path, rider))
   if opt_alltopics or opt_PyNodePlot_concat:
      cc.append(PyNodePlot_concat (ns, rr.path, rider))
   cc.append(QRU.helpnode (ns, rr.path, rider, func=PNP.PyNodePlot))
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      bookmark=cc[0], viewer='Pylab Plotter',
                      parentclass='ReqSeq', result_index=0)



#================================================================================

def PyNodePlot_basic (ns, path, rider):
   """
   There are various ways to plot groups of scalar nodes, i.e. nodes with a single vellset.
   """
   rr = QRU.on_entry(PyNodePlot_basic, path, rider)
   cc = []
   viewer = []
   ynodes = EB.bundle(ns,'cloud_n6s1')
   cc.append(PNP.pynode_Plot(ns, ynodes, title='simplest', color='red'))
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      viewer=viewer)

#================================================================================

def PyNodePlot_scalars (ns, path, rider):
   """
   Groups of scalar nodes can be plotted against each other by arranging them
   in a single list, and specifying groupspecs='XXYY'. The results of the nodes in
   the first half of the list will be used as x-coordinates, and those in the second
   half as y-coordinates:
   .    import PyNodePlot as PNP
   .    pynode = PNP.pynode_Plot(ns, xnodes+ynodes, 'XXYY')
   The plot may be customised with keyword arguments (e.g. color='green' etc).

   Simple (x,y,z) plots may be made in a similar way. The x,y and z groups are
   the 1st, 2nd and 3rd third of the input node list:
   .    pynode = PNP.pynode_Plot(ns, xnodes+ynodes+znodes, 'XXYYZZ')
   In this case, the z-values are indicated by the size of their markers.
   """
   rr = QRU.on_entry(PyNodePlot_scalars, path, rider)
   xnodes = EB.bundle(ns,'cloud_n6s1', nodename='xxx')
   ynodes = EB.bundle(ns,'cloud_n6s1', nodename='yyy')
   znodes = EB.bundle(ns,'cloud_n6s1')
   cc = []
   viewer = []

   node = PNP.pynode_Plot(ns, xnodes+ynodes, groupspecs='XXYY',
                          xlabel='xlabel', color='green')
   cc.extend([node,node])
   viewer.extend(['Pylab Plotter','Record Browser'])

   node = PNP.pynode_Plot(ns, xnodes+ynodes+znodes, groupspecs='XXYYZZ')
   cc.extend([node,node])
   viewer.extend(['Pylab Plotter','Record Browser'])

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      viewer=viewer)


#================================================================================

def PyNodePlot_complex (ns, path, rider):
   """
   Complex vellsets may be plotted in various ways. The simplest is to use the
   real parts of vellsets[0] as x-coordinates, and their imaginary parts as
   y-coordinates:
   .    import PyNodePlot as PNP
   .    pynode = PNP.pynode_Plot(ns, xnodes+ynodes, 'CY')
   In this case, the named group 'y' contains complex numbers. They are split into
   real and imaginary parts by plotspecs expressions x={y}.real and y={y}.imag.
   """
   rr = QRU.on_entry(PyNodePlot_complex, path, rider)
   cc = []
   cxnodes = EB.bundle(ns,'cloud_n6r1')
   cc.append(PNP.pynode_Plot(ns, cxnodes, groupspecs='CY'))
   if False:
      # NB: This does not work (yet), see string2groupspecs()
      cc.append(PNP.pynode_Plot(ns, cxnodes, groupspecs='CXY'))
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      viewer='Pylab Plotter')


#================================================================================

def PyNodePlot_tensors (ns, path, rider):
   """
   Tensor nodes are nodes with a multiple vellsets in their results (scalars have one).
   In a group of related tensor nodes (e.g. containing pairs (u,v) of coordinates),
   the groups of corresponding vellsets may be extracted as named groups, and plotted
   against each other: 
   .    import PyNodePlot as PNP
   .    pynode = PNP.pynode_Plot(ns, nodes, 'XY')
   This extracts all vellsets[0] as group 'x', and all vellsets[1] as group 'y',
   and uses them as horizontal and vertical coordinates.
   The plot may be customised with keyword arguments (e.g. color='green' etc).

   Simple (x,y,z) plots may be made in a similar way from vellsets 0,1,2 of
   the input nodes.
   .    pynode = PNP.pynode_Plot(ns, nodes, 'XYZ')
   Again, the z-values are indicated by the size of their markers.

   """
   rr = QRU.on_entry(PyNodePlot_tensors, path, rider)
   cc = []
   nodes = EB.bundle(ns,'range_4', n=5, nodename='range', stddev=1.0)
   cc = []
   cc.append(PNP.pynode_Plot(ns, nodes, groupspecs='XY'))
   cc.append(PNP.pynode_Plot(ns, nodes, groupspecs='XYZ'))
   cc.append(PNP.pynode_Plot(ns, nodes, groupspecs='Vells_32'))
   cc.append(PNP.pynode_Plot(ns, nodes, groupspecs='Vells_213'))
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      viewer='Pylab Plotter')


#================================================================================

def PyNodePlot_concat (ns, path, rider):
   """
   It is possible to concatenate pynodes of class PyNodePlot/PyNodeNamedGroups.
   Children of these classes are ignored for plotting, but their groups definitions
   and plot definitions are copied into the new pynode. This is very powerful.
   """
   rr = QRU.on_entry(PyNodePlot_concat, path, rider)
   cc = []
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      viewer='Pylab Plotter')



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
   lcn = EN.largest_common_name(coh, trace=True)
   labels = EN.get_plot_labels(coh, lcn=lcn, trace=True)
   ps = record()
   ps.legend = lcn                                # ....is not passed on....
   ps.title = lcn                                 # ....ok....
   pynode = ns['PlotVis22'] << Meq.PyNode(children=coh,
                                          child_labels=labels,
                                          class_name='PlotVis22',
                                          # groupspecs=gs,
                                          plotspecs=ps,
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
   return QRU._tdl_job_execute_f (mqs, parent, rootnode='QR_PyNodePlot')

def _tdl_job_execute_2D_ft (mqs, parent):
   return QRU._tdl_job_execute_ft (mqs, parent, rootnode='QR_PyNodePlot')

def _tdl_job_execute_3D_ftL (mqs, parent):
   return QRU._tdl_job_execute_ftL (mqs, parent, rootnode='QR_PyNodePlot')

def _tdl_job_execute_4D_ftLM (mqs, parent):
   return QRU._tdl_job_execute_ftLM (mqs, parent, rootnode='QR_PyNodePlot')

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





