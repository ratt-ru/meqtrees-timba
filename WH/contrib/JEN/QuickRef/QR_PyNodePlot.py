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
               TDLOption('opt_alltopics',"override: include all topics",False),

               TDLOption('opt_input_twig',"input twig",
                         ET.twig_names(), more=str),

               TDLMenu("PyNodePlot",
                       TDLOption('opt_PNP_alltopics',
                                 "override: include all PyNodePlot sub-topics",False),
                       TDLMenu("basic",
                               toggle='opt_PNP_basic'),
                       TDLMenu("scalars",
                               toggle='opt_PNP_scalars'),
                       TDLMenu("complex",
                               toggle='opt_PNP_complex'),
                       TDLMenu("tensors",
                               toggle='opt_PNP_tensors'),
                       TDLMenu("concat",
                               toggle='opt_PNP_concat'),
                       TDLMenu("customize",
                               toggle='opt_PNP_customize'),
                       TDLMenu("hotrod",
                               toggle='opt_PNP_hotrod'),
                       toggle='opt_PyNodePlot'),

               TDLMenu("PlotVIS22",
                       TDLOption('opt_PlotVIS22_alltopics',
                                 "override: include all PlotVIS22 sub-topics",False),
                       TDLMenu("linear",
                               toggle='opt_PlotVIS22_linear'),
                       TDLMenu("circular",
                               toggle='opt_PlotVIS22_circular'),
                       TDLMenu("old",
                               toggle='opt_PlotVIS22_old'),
                       toggle='opt_PlotVIS22'),

               TDLMenu("PyNodeNamedGroups",
                       TDLOption('opt_PNNG_alltopics',
                                 "override: include all PyNodeNamedGroups sub-topics",False),
                       TDLMenu("basic",
                               toggle='opt_PNNG_basic'),
                       TDLMenu("concat",
                               toggle='opt_PNNG_concat'),
                       toggle='opt_PyNodeNamedGroups'),

               TDLMenu("help",
                       TDLOption('opt_helpnode_alltopics',
                                 "override: include all helpnodes",False),
                       TDLOption('opt_helpnode_bundle',"help on EasyBundle.bundle()", False),
                       TDLOption('opt_helpnode_twig',"help on EasyTwig.twig()", False),
                       TDLOption('opt_helpnode_PNP',"help on class PyNodePlot", False),
                       TDLOption('opt_helpnode_pynode_PNP',"help on pynode_Plot()", False),
                       TDLOption('opt_helpnode_PNNG',"help on class PyNodeNodeGroups", False),
                       TDLOption('opt_helpnode_pynode_PNNG',"help on pynode_NamedGroup()", False),
                       toggle='opt_helpnodes'),

               toggle='opt_QR_PyNodePlot')



#********************************************************************************
# Top-level function, called from QuickRef.py:
#********************************************************************************

header = 'QR_PyNodePlot'

def QR_PyNodePlot (ns, path, rider):
   """
   """
   rr = QRU.on_entry(QR_PyNodePlot, path, rider)
 
   cc = []
   override = opt_alltopics
   global header
   
   if override or opt_PyNodePlot:
      header += '_PNP'
      cc.append(PyNodePlot (ns, rr.path, rider))

   if override or opt_PlotVIS22:
      cc.append(PlotVIS22 (ns, rr.path, rider))

   if override or opt_PyNodeNamedGroups:
      header += '_PNNG'
      cc.append(PyNodeNamedGroups (ns, rr.path, rider))

   if override or opt_helpnodes:
      header += '_help'
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
   override = (opt_alltopics or opt_helpnode_alltopics)

   if override or opt_helpnode_bundle:
      cc.append(QRU.helpnode (ns, rr.path, rider, func=EB.bundle))
   if override or opt_helpnode_twig:
      cc.append(QRU.helpnode (ns, rr.path, rider, func=ET.twig))

   if override or opt_helpnode_PNP:
      cc.append(QRU.helpnode (ns, rr.path, rider, func=PNP.PyNodePlot))
   if override or opt_helpnode_pynode_PNP:
      cc.append(QRU.helpnode (ns, rr.path, rider, func=PNP.pynode_Plot))
      cc.append(QRU.helpnode(ns, rr.path, rider, func=PNP.string2plotspecs))
      cc.append(QRU.helpnode(ns, rr.path, rider, func=PNP.string2plotspecs_VIS22))

   if override or opt_helpnode_PNNG:
      cc.append(QRU.helpnode (ns, rr.path, rider, func=PNNG.PyNodeNamedGroups))
   if override or opt_helpnode_pynode_PNNG:
      cc.append(QRU.helpnode (ns, rr.path, rider, func=PNNG.pynode_NamedGroup))
      cc.append(QRU.helpnode(ns, rr.path, rider, func=PNNG.string2groupspecs))
      cc.append(QRU.helpnode(ns, rr.path, rider, func=PNNG.string2record_VIS22))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)





#================================================================================
# PyNodePlot:
#================================================================================

def PyNodePlot (ns, path, rider):
   """
   Basic plotting, using the convenience function PNP.pynode_PyNodePlot(),
   (import PyNodePlot as PNP) which creates a MeqPyNode of class PyNodePlot,
   which is derived from PyNodeNamedGroups (see elsewhere in this module).

   In order to make things easy, standard plots may be specified by means
   of a string (e.g. 'XXYY'), and customized by means of keyword arguments.
   This should take care of the vast majority of plots. More advanced use
   requires the input of valid groupspecs/plotspecs records.

   In the examples shown below, the MeqPyNode state record is often shown next
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
   override = (opt_alltopics or opt_PNP_alltopics)

   if override or opt_PNP_basic:
      cc.append(PyNodePlot_basic (ns, rr.path, rider))
   if override or opt_PNP_scalars:
      cc.append(PyNodePlot_scalars (ns, rr.path, rider))
   if override or opt_PNP_complex:
      cc.append(PyNodePlot_complex (ns, rr.path, rider))
   if override or opt_PNP_tensors:
      cc.append(PyNodePlot_tensors (ns, rr.path, rider))
   if override or opt_PNP_concat:
      cc.append(PyNodePlot_concat (ns, rr.path, rider))

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
   viewer = 'Pylab Plotter'
   ynodes = EB.bundle(ns,'cloud_n6s1')
   cc.append(PNP.pynode_Plot(ns, ynodes))                    # title='simplest', color='red'))
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

   The following plots vellset[0] as a function of child nr:
   .    pynode = PNP.pynode_Plot(ns, nodes, 'YY')

   Arbitrary vellsets may be plotted against each other in the following way:
   .    pynode = PNP.pynode_Plot(ns, nodes, 'VELLS_1')
   .    pynode = PNP.pynode_Plot(ns, nodes, 'VELLS_32')
   .    pynode = PNP.pynode_Plot(ns, nodes, 'VELLS_213')
   The integers following 'VELLS_' are vellset indices, of course.

   """
   rr = QRU.on_entry(PyNodePlot_tensors, path, rider)
   cc = []
   nodes = EB.bundle(ns,'range_4', n=5, nodename='range', stddev=1.0)
   cc = []
   cc.append(PNP.pynode_Plot(ns, nodes, groupspecs='YY'))
   cc.append(PNP.pynode_Plot(ns, nodes, groupspecs='XY'))
   cc.append(PNP.pynode_Plot(ns, nodes, groupspecs='XYZ'))
   cc.append(PNP.pynode_Plot(ns, nodes, groupspecs='VELLS_1'))
   cc.append(PNP.pynode_Plot(ns, nodes, groupspecs='VELLS_32'))
   cc.append(PNP.pynode_Plot(ns, nodes, groupspecs='VELLS_213'))
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      viewer='Pylab Plotter')


#================================================================================

def PyNodePlot_concat (ns, path, rider):
   """
   It is possible to concatenate pynodes of class PyNodePlot/PyNodeNamedGroups.
   Children of these types are ignored for plotting, but their group definitions
   and plot definitions are copied into the new MeqPyNode. This is very powerful.
   
   .    import PyNodeNamedGroups as PNNG
   .    pynode_XX = PNP.pynode_NamedGroup(ns, xnodes, 'XX')
   .    pynode_YY = PNP.pynode_NamedGroup(ns, ynodes, 'YY')
   
   .    import PyNodePlot as PNP
   .    pynode = PNP.pynode_Plot(ns, [pynode_XX, pynode_YY], plotspecs='XY')

   Note that in this case, no groupspecs is specified (as 3rd argument), but a
   keyword argument plotspecs. The reason is of course that the groups (x and y)
   have been copied from its pynode children, but we still have to specify how
   to plot these groups.

   An (x,y,z) plot can be made by adding a 3rd pynode child (pynode_ZZ),
   and specifying a suitable plotspecs:
   .    pynode_ZZ = PNP.pynode_NamedGroup(ns, znodes, 'ZZ')
   .    pynode = PNP.pynode_Plot(ns, [pynode_XX, pynode_YY, pynode_ZZ],
   .                             plotspecs='XYZ')

   Etc, etc. See also the more elaborate concatenation examples below....
   """
   rr = QRU.on_entry(PyNodePlot_concat, path, rider)
   cc = []
   viewer = []
   xnodes = EB.bundle(ns,'cloud_n6s1', nodename='xxx')
   ynodes = EB.bundle(ns,'cloud_n6s1', nodename='yyy')
   # znodes = EB.bundle(ns,'cloud_n6s1')

   cc.append(PNNG.pynode_NamedGroup(ns, xnodes, groupspecs='XX'))
   viewer.append('Record Browser')

   cc.append(PNNG.pynode_NamedGroup(ns, ynodes, groupspecs='YY'))
   viewer.append('Record Browser')

   node = PNP.pynode_Plot(ns, cc, plotspecs='XY',
                          xlabel='from pynode_XX',
                          ylabel='from pynode_YY')
   cc.extend([node,node])
   viewer.extend(['Pylab Plotter','Record Browser'])

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      viewer=viewer)



#================================================================================
# PlotVIS22:
#================================================================================

def PlotVIS22 (ns, path, rider):
   """
   Standard plot of the 4 elements (visibilities) of 2x2 cohaerency matrices.
   """
   rr = QRU.on_entry(PlotVIS22, path, rider)
   cc = []

   override = (opt_alltopics or opt_PlotVIS22_alltopics)
   if override or opt_PlotVIS22_linear:
      cc.append(PlotVIS22_linear (ns, rr.path, rider))
   if override or opt_PlotVIS22_circular:
      cc.append(PlotVIS22_circular (ns, rr.path, rider))

   if True:
      # Works, but causes node clashes (should be removed anyway) 
      if override or opt_PlotVIS22_old:
         cc.append(PlotVIS22_old (ns, rr.path, rider))

   cc.append(QRU.helpnode(ns, rr.path, rider, func=PNNG.string2record_VIS22))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)


#================================================================================

def PlotVIS22_old (ns, path, rider):
   """
   """
   rr = QRU.on_entry(PlotVIS22_old, path, rider)
   cc = []

   [uu,uv,coh,labels] = PNPVis22.make_uvdata(ns, n=4)
   ss = EN.get_node_names(coh)
   lcs = EN.get_largest_common_string(ss)
   labels = EN.get_plot_labels(coh, lcs=lcs)
   ps = record()
   ps.legend = lcs                                # ....is not passed on....
   ps.title = lcs                                 # ....ok....
   pynode = ns['PlotVIS22'] << Meq.PyNode(children=coh,
                                          child_labels=labels,
                                          class_name='PlotVis22',
                                          # groupspecs=gs,
                                          plotspecs=ps,
                                          module_name=PNPVis22.__file__)
   cc.append(pynode)
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      viewer='Pylab Plotter')


#================================================================================

def PlotVIS22_linear (ns, path, rider):
   """
   """
   rr = QRU.on_entry(PlotVIS22_linear, path, rider)
   cc = []

   [uu,uv,coh,labels] = PNPVis22.make_uvdata(ns, n=4)        # temporary
   cc.append(PNP.pynode_Plot(ns, coh, 'VIS22L'))
   cc.append(PNP.pynode_Plot(ns, coh, 'VIS22L_DIAG'))
   cc.append(PNP.pynode_Plot(ns, coh, 'VIS22L_OFFDIAG'))
   cc.append(PNP.pynode_Plot(ns, coh, 'VIS22L_IQUV'))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      viewer='Pylab Plotter')


#================================================================================

def PlotVIS22_circular (ns, path, rider):
   """
   """
   rr = QRU.on_entry(PlotVIS22_circular, path, rider)
   cc = []

   [uu,uv,coh,labels] = PNPVis22.make_uvdata(ns, n=4)        # temporary
   cc.append(PNP.pynode_Plot(ns, coh, 'VIS22C'))
   cc.append(PNP.pynode_Plot(ns, coh, 'VIS22C_DIAG'))
   cc.append(PNP.pynode_Plot(ns, coh, 'VIS22C_OFFDIAG'))
   cc.append(PNP.pynode_Plot(ns, coh, 'VIS22C_IQUV'))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      viewer='Pylab Plotter')




#================================================================================
# PyNodeNamedGroups:
#================================================================================

def PyNodeNamedGroups (ns, path, rider):
   """
   """
   rr = QRU.on_entry(PyNodeNamedGroups, path, rider)
   cc = []
   override = (opt_alltopics or opt_PNNG_alltopics)

   if override or opt_PNNG_basic:
      cc.append(PyNodeNamedGroups_basic (ns, rr.path, rider))
   if override or opt_PNNG_concat:
      cc.append(PyNodeNamedGroups_concat (ns, rr.path, rider))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      bookmark=cc[0], viewer='Record Browser',
                      parentclass='ReqSeq', result_index=0)


#================================================================================

def PyNodeNamedGroups_basic (ns, path, rider):
   """
   """
   rr = QRU.on_entry(PyNodeNamedGroups_basic, path, rider)
   cc = []
   children = [ns << 0.1, ns << 1.1]
   pynode = ns['PyNodeNamedGroups'] << Meq.PyNode(children=children,
                                                  # child_labels=labels,
                                                  class_name='PyNodeNamedGroups',
                                                  # groupspecs=gs,
                                                  module_name=PNNG.__file__)
   cc.append(pynode)
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      viewer='Record Browser')

#================================================================================

def PyNodeNamedGroups_concat (ns, path, rider):
   """
   """
   rr = QRU.on_entry(PyNodeNamedGroups_concat, path, rider)
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

   print '\n** Start of standalone test of: QR_PyNodePlot.py:\n' 

   ns = NodeScope()

   if 1:
      rider = QRU.create_rider()             # CollatedHelpRecord object
      QR_PyNodePlot(ns, 'test', rider=rider)
      if 1:
         print rider.format()

   print '\n** End of standalone test of: QR_PyNodePlot.py:\n' 

#=====================================================================================





