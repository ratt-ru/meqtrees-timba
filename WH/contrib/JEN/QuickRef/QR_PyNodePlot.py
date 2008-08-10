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
from Timba.Contrib.JEN.pylab import PlotStyle as PPS

import math
# import random
import numpy


#******************************************************************************** 
# TDLCompileMenu (included in QuickRef menu):
#********************************************************************************


oo = TDLCompileMenu("QR_PyNodePlot topics:",
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
                            TDLMenu("advanced",
                                    toggle='opt_PNP_advanced'),
                            TDLMenu("nonodes",
                                    toggle='opt_PNP_nonodes'),
                            toggle='opt_PyNodePlot'),
                    
                    TDLMenu("PlotVIS22",
                            TDLOption('opt_PlotVIS22_alltopics',
                                      "override: include all PlotVIS22 sub-topics",False),
                            TDLMenu("linear",
                                    toggle='opt_PlotVIS22_linear'),
                            TDLMenu("circular",
                                    toggle='opt_PlotVIS22_circular'),
                            TDLMenu("play",
                                    TDLOption('opt_PlotVIS22_play_polrep',
                                              "polarization representation",
                                              ['linear','circular']),
                                    TDLOption('opt_PlotVIS22_play_nuv',"nr of uv-points",
                                              [10,20,40,91,351], more=int),
                                    TDLOption('opt_PlotVIS22_play_L',"source pos l (deg)",
                                              [0.0,0.01,0.1,1.0], more=float),
                                    TDLOption('opt_PlotVIS22_play_M',"source pos m (deg)",
                                              [0.0,0.01,0.1,1.0], more=float),
                                    TDLOption('opt_PlotVIS22_play_IQUV',"cps IQUV spec-string",
                                              ['I','V0.01','U0.1','Q0.1','Q0.1U0.1','Q0.1U0.1V0.01'], more=str),
                                    TDLOption('opt_PlotVIS22_play_PZD',"XY/RL phase zero diff PZD (rad)",
                                              [0.0,0.1,1.0], more=float),
                                    toggle='opt_PlotVIS22_play'),
                            toggle='opt_PlotVIS22'),


                    TDLMenu("PyNodeNamedGroups",
                            TDLOption('opt_PNNG_alltopics',
                                      "override: include all PyNodeNamedGroups sub-topics",False),
                            TDLMenu("basic",
                                    toggle='opt_PNNG_basic'),
                            TDLMenu("nonodes",
                                    toggle='opt_PNNG_nonodes'),
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
                            TDLOption('opt_helpnode_PNP_plotstyles',"help on PNP (pylab) plot-styles", False),
                            TDLOption('opt_helpnode_PNNG',"help on class PyNodeNodeGroups", False),
                            TDLOption('opt_helpnode_pynode_PNNG',"help on pynode_NamedGroup()", False),
                            toggle='opt_helpnodes'),

                    toggle='opt_QR_PyNodePlot')

# Assign the menu to an attribute, for outside visibility:
itsTDLCompileMenu = oo


#********************************************************************************
# Top-level function, called from QuickRef.py:
#********************************************************************************

header = 'QR_PyNodePlot'

def QR_PyNodePlot (ns, rider):
   """
   """
   stub = QRU.on_entry(ns, rider, QR_PyNodePlot)
 
   cc = []
   override = opt_alltopics
   global header
   
   if override or opt_PyNodePlot:
      header += '_PNP'
      cc.append(PyNodePlot (ns, rider))

   if override or opt_PlotVIS22:
      cc.append(PlotVIS22 (ns, rider))

   if override or opt_PyNodeNamedGroups:
      header += '_PNNG'
      cc.append(PyNodeNamedGroups (ns, rider))

   if override or opt_helpnodes:
      header += '_help'
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
   override = (opt_alltopics or opt_helpnode_alltopics)

   if override or opt_helpnode_bundle:
      cc.append(QRU.helpnode (ns, rider, func=EB.bundle))
   if override or opt_helpnode_twig:
      cc.append(QRU.helpnode (ns, rider, func=ET.twig))

   if override or opt_helpnode_PNP:
      cc.append(QRU.helpnode (ns, rider, func=PNP.PyNodePlot))
   if override or opt_helpnode_pynode_PNP:
      cc.append(QRU.helpnode (ns, rider, func=PNP.pynode_Plot))
      cc.append(QRU.helpnode(ns, rider, func=PNP.string2plotspecs))
      cc.append(QRU.helpnode(ns, rider, func=PNP.string2plotspecs_VIS22))
   if override or opt_helpnode_PNP_plotstyles:
      cc.append(QRU.helpnode (ns, rider, func=PPS.PlotStyle))

   if override or opt_helpnode_PNNG:
      cc.append(QRU.helpnode (ns, rider, func=PNNG.PyNodeNamedGroups))
   if override or opt_helpnode_pynode_PNNG:
      cc.append(QRU.helpnode (ns, rider, func=PNNG.pynode_NamedGroup))
      cc.append(QRU.helpnode(ns, rider, func=PNNG.string2groupspecs))
      cc.append(QRU.helpnode(ns, rider, func=PNNG.string2record_VIS22))

   return QRU.on_exit (ns, rider, cc, mode='group')





#================================================================================
# topic PyNodePlot:
#================================================================================

def PyNodePlot (ns, rider):
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
   <li> pynode_help:   the __doc__ string of the PyNodePlot class
   <li> groupspecs:    the input group specification record
   <li> plotspecs:     the input plot specification record
   <li> quickref_help: the actual call used to create this MeqPyNode,
               including the values of the custimizing keyword arguments.
   <li> cache.result (available after execution):
   <li> namedgroups: The detailed list of available named groups
   <li> plotdefs:    The detailed list of (sub)plot definitions
   """
   stub = QRU.on_entry(ns, rider, PyNodePlot)
   cc = []
   override = (opt_alltopics or opt_PNP_alltopics)

   if override or opt_PNP_basic:
      cc.append(PyNodePlot_basic (ns, rider))
   if override or opt_PNP_advanced:
      cc.append(PyNodePlot_advanced (ns, rider))
   if override or opt_PNP_scalars:
      cc.append(PyNodePlot_scalars (ns, rider))
   if override or opt_PNP_complex:
      cc.append(PyNodePlot_complex (ns, rider))
   if override or opt_PNP_tensors:
      cc.append(PyNodePlot_tensors (ns, rider))
   if override or opt_PNP_concat:
      cc.append(PyNodePlot_concat (ns, rider))
   if override or opt_PNP_nonodes:
      cc.append(PyNodePlot_nonodes (ns, rider))

   bookmark = cc
   if len(cc)>0:
      bookmark = cc[0]

   return QRU.on_exit (ns, rider, cc, 
                       # bookmark=bookmark,
                       viewer='Pylab Plotter',
                       parentclass='ReqSeq', result_index=0)



#================================================================================

def PyNodePlot_basic (ns, rider):
   """
   The simplest possible plot plots vells[0] of its children against child no:
   <code_lines>
   import PyNodePlot as PNP
   pynode = PNP.pynode_Plot(ns, nodes)
   </code_lines>

   The other 3 plots show how things may be customized by means of keyword args, e.g.:
   <code_lines>
   pynode = PNP.pynode_Plot(ns, nodes, title='basic', ylabel='ylabel', ...)
   </code_lines>
   The utilized customization keywords are shown in the plot legends. They can be
   used in any combination, of course.
   """
   stub = QRU.on_entry(ns, rider, PyNodePlot_basic)
   cc = []

   nodes = EB.bundle(ns,'cloud_n6s1')
   qhelp = """The simplest possible call (node = PNP.pynode_Plot(ns, nodes))
   produces a plot with default settings."""
   cc.append(PNP.pynode_Plot(ns, nodes, qhelp=qhelp))
   
   kwargs = dict(title='custom_title',ylabel='custom_ylabel',
                 xlabel='custom_xlabel', legend=['line1','line2'])
   qhelp = """Demonstrates custom labels and legend"""
   cc.append(PNP.pynode_Plot(ns, nodes, qhelp=qhelp, **PNP.kwargs2legend(**kwargs)))
                             
   kwargs = dict(color='red', marker='triangle', markersize=10, fontsize=15)
   qhelp = """Demonstrates custom markers"""
   cc.append(PNP.pynode_Plot(ns, nodes, qhelp=qhelp, **PNP.kwargs2legend(**kwargs)))

   kwargs = dict(annotate=False, xmin=-5, xmax=4, ymin=-10, ymax=10,
                 plot_ellipse_stddev=True, plot_circle_mean=True)
   qhelp = """Demonstrates mean/stddev indications, and plot-window"""
   cc.append(PNP.pynode_Plot(ns, nodes, qhelp=qhelp, **PNP.kwargs2legend(**kwargs)))

   return QRU.on_exit (ns, rider, cc,
                       viewer='Pylab Plotter')

#================================================================================

def PyNodePlot_advanced (ns, rider):
   """
   In this more advanced example, a single plot contains graphics that represent
   different mathematical expressions in which the the available named groups
   are arguments (e.g. y={a}*{b}, x={b}-{c} etc). This is done by filling an
   external plotspecs record with a list of one or more subplot definitions.
   (NB: In the standard plots, which are specified by strings like 'XXYY' etc,
   standard plotspecs records are generated internally)

   This example has two steps. First a PyNodeNamedGroups pynode_1 is created,
   which extracts named groups of values ({u},{v},{w}) from the results of
   groups of nodes. In addition, a derived group {ruv} is created with a math
   expression (string), in which the other groups are variables {..}.

   <code_lines>
   import PyNodeNamedGroups as PNNG
   gs = record(ruv='sqrt(abs(({u}**2+{v}**2)))')
   pynode_1 = PNNG.pynode_NamedGroup(ns, 
                                     [PNNG.pynode_NamedGroup(ns, unodes, 'u'),
                                      PNNG.pynode_NamedGroup(ns, vnodes, 'v'),
                                      PNNG.pynode_NamedGroup(ns, wnodes, 'w')],
                                     groupspecs=gs))
   </code_lines>

   The actual plot(s) are made by another pynode of class PyNodePlot, which has
   pynode_1 as its child. The (graphics) plots are specified as math expressions
   of the named groups, which it copies from the result of its child.
   The second plot is specified in the following way:
   
   <code_lines>
   import PyNodePlot as PNP
   psg = []
   psg.append(record(x='{u}', y='{v}', z='{w}', color='green'))
   psg.append(record(x='{u}', y='{ruv}', color='blue'))
   pynode_2 = PNP.pynode_Plot(ns, pynode_1,
                             plotspecs=record(graphics=psg),
                             **kwargs)
   </code_lines>

   Any number of plots may be specified, and appended to the list of graphics
   plotspecs. (NB: Only plots of type graphics are supported for the moment,
   but there will be others in the future.)
   
   As shown in subtopic 'PyNodePlot_basic' above, the keywords arguments
   can be used to customize the plot with titla, axes labels etc.

   For the third graph, two extra groups produv and sumuv are defined,
   and plotted against each other in the same plot in two different ways:

   <code_lines>
   gs = record(produv='{u}*{v}', sumuv='{u}+{v}')                                                            
   psg = []
   psg.append(record(x='{produv}', y='{sumuv}', color='magenta',
                    legend='sumuv vs produv'))
   psg.append(record(x='{sumuv}', y='{produv}', color='cyan',
                    legend='produv vs sumuv'))
   pynode_3 = PNP.pynode_Plot(ns, pynode_1,
                             groupspecs=gs,
                             plotspecs=record(graphics=psg),
                             **kwargs)
   </code_lines>

   The state-record of pynode_3 is bookmarked too, for easy inspection. Check the
   namedgroups in the result, and the plotdefs.
   
   Etc, etc. The possibilities are endless.
   """
   stub = QRU.on_entry(ns, rider, PyNodePlot_advanced)
   cc = []

   unodes = EB.bundle(ns,'cloud_n6s1', nodename='u')
   vnodes = EB.bundle(ns,'cloud_n6s1', nodename='v')
   wnodes = EB.bundle(ns,'cloud_n6s0.01', nodename='w')

   ruv_expr = 'sqrt(abs(({u}**2+{v}**2)))'
   gs = record(ruv=ruv_expr)
   cc.append(PNNG.pynode_NamedGroup(ns, 
                                    [PNNG.pynode_NamedGroup(ns, unodes, 'u'),
                                     PNNG.pynode_NamedGroup(ns, vnodes, 'v'),
                                     PNNG.pynode_NamedGroup(ns, wnodes, 'w')],
                                    qviewer='Record Browser',
                                    groupspecs=gs))

   psg = []
   psg.append(record(x='{u}', y='{v}', z='{w}', color='green'))
   psg.append(record(x='{u}', y='{ruv}', color='blue'))
   kwargs = dict(title='uvw-coverage(green) and ruv(blue)',
                 zlabel='w (wavelengths)',
                 ylabel='v/ruv (wavelengths)',
                 xlabel='u (wavelengths)')
   cc.append(PNP.pynode_Plot(ns, [cc[0]], plotspecs=record(graphics=psg),
                             **PNP.kwargs2legend(**kwargs)))

   psg = []
   psg.append(record(x='{produv}', y='{sumuv}', color='magenta', legend='sumuv vs produv'))
   psg.append(record(x='{sumuv}', y='{produv}', color='cyan', legend='produv vs sumuv'))
   kwargs = dict(title='produv (u*v) and sumuv (u+v)',
                 ylabel='produv/sumuv',
                 xlabel='sumuv/produv')
   gs = record(produv='{u}*{v}', sumuv='{u}+{v}')                                                            
   cc.append(PNP.pynode_Plot(ns, [cc[0]],
                             groupspecs=gs,
                             qviewer=[True,'Record Browser'],
                             plotspecs=record(graphics=psg),
                             **PNP.kwargs2legend(**kwargs)))
                                
   return QRU.on_exit (ns, rider, cc, node_help=True,
                       show_recurse=True,
                       viewer='Pylab Plotter')

#================================================================================

def PyNodePlot_scalars (ns, rider):
   """
   Groups of scalar nodes can be plotted against each other by arranging them
   in a single list, and specifying groupspecs='XXYY'. The results of the nodes in
   the first half of the list will be used as x-coordinates, and those in the second
   half as y-coordinates:
   <code_lines>
   import PyNodePlot as PNP
   pynode = PNP.pynode_Plot(ns, xnodes+ynodes, 'XXYY')
   </code_lines>
   The plot may be customised with keyword arguments (e.g. color='green' etc).

   Simple (x,y,z) plots may be made in a similar way. The x,y and z groups are
   the 1st, 2nd and 3rd third of the input node list:
   <code_lines>
   pynode = PNP.pynode_Plot(ns, xnodes+ynodes+znodes, 'XXYYZZ')
   </code_lines>
   In this case, the z-values are indicated by the size of their markers.
   """
   stub = QRU.on_entry(ns, rider, PyNodePlot_scalars)
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

   return QRU.on_exit (ns, rider, cc,
                       viewer='Pylab Plotter')


#================================================================================

def PyNodePlot_complex (ns, rider):
   """
   Complex vellsets may be plotted in various ways. The simplest is to use the
   real parts of vellsets[0] as x-coordinates, and their imaginary parts as
   y-coordinates:
   <code_lines>
   import PyNodePlot as PNP
   pynode = PNP.pynode_Plot(ns, xnodes+ynodes, 'CY')
   </code_lines>
   In this case, the named group 'y' contains complex numbers. They are split into
   real and imaginary parts by plotspecs expressions x={y}.real and y={y}.imag.
   """
   stub = QRU.on_entry(ns, rider, PyNodePlot_complex)
   cc = []
   cxnodes = EB.bundle(ns,'cloud_n6r1')
   cc.append(PNP.pynode_Plot(ns, cxnodes, groupspecs='CY'))
   if False:
      # NB: This does not work (yet), see string2groupspecs()
      cc.append(PNP.pynode_Plot(ns, cxnodes, groupspecs='CXY'))
   return QRU.on_exit (ns, rider, cc,
                       viewer='Pylab Plotter')


#================================================================================

def PyNodePlot_tensors (ns, rider):
   """
   Tensor nodes are nodes with a multiple vellsets in their results (scalars have one).
   In a group of related tensor nodes (e.g. containing pairs (u,v) of coordinates),
   the groups of corresponding vellsets may be extracted as named groups, and plotted
   against each other: 
   <code_lines>
   import PyNodePlot as PNP
   pynode = PNP.pynode_Plot(ns, nodes, 'XY')
   </code_lines>
   This extracts all vellsets[0] as group 'x', and all vellsets[1] as group 'y',
   and uses them as horizontal and vertical coordinates.
   The plot may be customised with keyword arguments (e.g. color='green' etc).

   Simple (x,y,z) plots may be made in a similar way from vellsets 0,1,2 of
   the input nodes.
   <code_lines>
   pynode = PNP.pynode_Plot(ns, nodes, 'XYZ')
   </code_lines>
   Again, the z-values are indicated by the size of their markers.

   The following plots vellset[0] as a function of child nr:
   <code_lines>
   pynode = PNP.pynode_Plot(ns, nodes, 'YY')
   </code_lines>

   Arbitrary vellsets may be plotted against each other in the following way:
   <code_lines>
   pynode = PNP.pynode_Plot(ns, nodes, 'VELLS_1')
   pynode = PNP.pynode_Plot(ns, nodes, 'VELLS_32')
   pynode = PNP.pynode_Plot(ns, nodes, 'VELLS_213')
   </code_lines>
   The integers following 'VELLS_' are vellset indices, of course.

   """
   stub = QRU.on_entry(ns, rider, PyNodePlot_tensors)
   cc = []
   nodes = EB.bundle(ns,'range_4', n=5, nodename='range', stddev=1.0)
   cc = []
   cc.append(PNP.pynode_Plot(ns, nodes, groupspecs='YY'))
   cc.append(PNP.pynode_Plot(ns, nodes, groupspecs='XY'))
   cc.append(PNP.pynode_Plot(ns, nodes, groupspecs='XYZ'))
   cc.append(PNP.pynode_Plot(ns, nodes, groupspecs='VELLS_1'))
   cc.append(PNP.pynode_Plot(ns, nodes, groupspecs='VELLS_32'))
   cc.append(PNP.pynode_Plot(ns, nodes, groupspecs='VELLS_213'))
   return QRU.on_exit (ns, rider, cc,
                       viewer='Pylab Plotter')


#================================================================================

def PyNodePlot_concat (ns, rider):
   """
   It is possible to concatenate pynodes of class PyNodePlot/PyNodeNamedGroups.
   Children of these types are ignored for plotting, but their group definitions
   and plot definitions are copied into the new MeqPyNode. This is very powerful.
   
   <code_lines>
   import PyNodeNamedGroups as PNNG
   pynode_XX = PNP.pynode_NamedGroup(ns, xnodes, 'XX')
   pynode_YY = PNP.pynode_NamedGroup(ns, ynodes, 'YY')
   
   import PyNodePlot as PNP
   pynode = PNP.pynode_Plot(ns, [pynode_XX, pynode_YY], plotspecs='XY')
   </code_lines>

   Note that in this case, no groupspecs is specified (as 3rd argument), but a
   keyword argument plotspecs. The reason is of course that the groups (x and y)
   have been copied from its pynode children, but we still have to specify how
   to plot these groups.

   An (x,y,z) plot can be made by adding a 3rd pynode child (pynode_ZZ),
   and specifying a suitable plotspecs:
   pynode_ZZ = PNP.pynode_NamedGroup(ns, znodes, 'ZZ')
   pynode = PNP.pynode_Plot(ns, [pynode_XX, pynode_YY, pynode_ZZ],
                            plotspecs='XYZ')

   Etc, etc. See also the more elaborate concatenation examples below....
   """
   stub = QRU.on_entry(ns, rider, PyNodePlot_concat)
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

   return QRU.on_exit (ns, rider, cc,
                      viewer='Pylab Plotter')

#================================================================================

def PyNodePlot_nonodes (ns, rider):
   """
   It is also possible to plot 'named groups' that do not contain the
   results of child-nodes, but (lists of) values given directly. This opens
   many new possibilities, from inserting explanatory plots into the
   meqbrowser, to inserting support information into node-result plots.

   In this example, four named groups (x,y,a,b) are specified via the
   groupspecs record:
   <code_lines>
   gs = record(x=range(2,8), y=range(2,8), a=range(2,8), b=range(2,8))
   pynode_xyab = PNNG.pynode_NamedGroup(ns, groupspecs=gs)
   </code_lines>

   NB: For simplicity, the python range() function is used to generate lists
   of numbers: range(2,8) -> [0,1,2,3,4,5].

   The actual plots are specified by means of the plotspecs record:
   <code_lines>
   psg = [record(x='{x}',y='{y}', color='red', legend='yexpr'),
          record(x='{x}',y='{y}+{x}-2*({b}+{a}/2)', color='blue', legend='yexpr'),
          record(x='{x}',y='sin({a}*2)', color='green', legend='yexpr')]
   ps = record(graphics=psg,
               xlabel='x-group', ylabel='y (see legend)',
               include_origin=True,
               title='nonodes')
   </code_lines>

   Finally, the PyNode is created without any nodes, but with gs and ps:
   <code_lines>
   import PyNodePlot as PNP
   pynode = PNP.pynode_Plot(ns, groupspecs=gs, plotspecs=ps)
   </code_lines>

   See also the PyNodeNamedGroups topic 'nonodes' below. 
   """
   stub = QRU.on_entry(ns, rider, PyNodePlot_nonodes)
   cc = []
   viewer = []

   gs = record(x=range(2,8), y=range(2,8), a=range(2,8), b=range(2,8))
   
   psg = [record(x='{x}',y='{y}',
                 linestyle='-',
                 color='red', legend='yexpr'),
          record(x='{x}',y='{y}+{x}-2*({b}+{a}/2)',
                 linestyle='--', marker='+',
                 color='blue', legend='yexpr'),
          record(x='{x}',y='sin({a}*2)',
                 linestyle=':', marker='triangle',
                 color='green', legend='yexpr')]
   ps = record(graphics=psg, xlabel='x-group', ylabel='y (see legend)',
               include_origin=True,
               title='nonodes')

   pynode = PNP.pynode_Plot(ns, groupspecs=gs, plotspecs=ps)
   cc.append(pynode)
   viewer.append('Record Browser')
   cc.append(pynode)
   viewer.append('Pylab Plotter')

   return QRU.on_exit (ns, rider, cc,
                       viewer='Pylab Plotter')





#================================================================================
#================================================================================
# PlotVIS22:
#================================================================================
#================================================================================

def PlotVIS22 (ns, rider):
   """
   Standard plot of the 4 elements (visibilities) of 2x2 cohaerency matrices.
   """
   stub = QRU.on_entry(ns, rider, PlotVIS22)
   cc = []

   override = (opt_alltopics or opt_PlotVIS22_alltopics)
   if override or opt_PlotVIS22_linear:
      cc.append(PlotVIS22_linear (ns, rider))
   if override or opt_PlotVIS22_circular:
      cc.append(PlotVIS22_circular (ns, rider))
   if override or opt_PlotVIS22_play:
      cc.append(PlotVIS22_play (ns, rider))

   cc.append(QRU.helpnode(ns, rider, func=PNNG.string2record_VIS22))

   return QRU.on_exit (ns, rider, cc,
                       viewer='Pylab Plotter')


#================================================================================

def PlotVIS22_linear (ns, rider):
   """
   Four plots of the complex visibilities (XX,XY,YX,YY) of a point source,
   assuming linearly polarized receptors (like WSRT or ATCA). 
   """
   stub = QRU.on_entry(ns, rider, PlotVIS22_linear)
   cc = []

   IQUV = 'Q0.1U-0.2'
   L = 1.0
   M = 0.0
   coh = EB.vis22 (ns, IQUV=IQUV, nuv=10, L=L, M=M, urms=1.0, vrms=1.0)
   legend = ['IQUV='+str(IQUV)]
   legend.append('L='+str(L)+', M='+str(M))

   cc.append(PNP.pynode_Plot(ns, coh, 'VIS22L', legend=legend))
   cc.append(PNP.pynode_Plot(ns, coh, 'VIS22L_OFFDIAG_annotate'))
   cc.append(PNP.pynode_Plot(ns, coh, 'VIS22L_IQUV'))
   cc.append(PNP.pynode_Plot(ns, coh, 'VIS22L_QUV'))

   return QRU.on_exit (ns, rider, cc,
                       viewer='Pylab Plotter')


#================================================================================

def PlotVIS22_circular (ns, rider):
   """
   Four plots of the complex visibilities (RR,RL,LR,LL) of a point source,
   assuming cirularly polarized receptors (like VLA or VLBI).
   """
   stub = QRU.on_entry(ns, rider, PlotVIS22_circular)
   cc = []

   IQUV = 'Q0.1U-0.2'
   L = 1.0
   M = 0.0
   coh = EB.vis22 (ns, IQUV=IQUV, nuv=10, L=L, M=M, urms=1.0, vrms=1.0)
   legend = ['IQUV='+str(IQUV)]
   legend.append('L='+str(L)+', M='+str(M))

   cc.append(PNP.pynode_Plot(ns, coh, 'VIS22C'))
   cc.append(PNP.pynode_Plot(ns, coh, 'VIS22C_OFFDIAG_annotate'))
   cc.append(PNP.pynode_Plot(ns, coh, 'VIS22C_IQUV'))
   cc.append(PNP.pynode_Plot(ns, coh, 'VIS22C_QUV'))

   return QRU.on_exit (ns, rider, cc,
                       viewer='Pylab Plotter')


#================================================================================

def PlotVIS22_play (ns, rider):
   """
   Play with the visibility/stokes plots for sources of different polarisations,
   at different positions (l,m) w.r.t. the phase centre. Note how much information
   can be gleaned from the single plot with all four corrs:
   <li> Because it is a single point source, all corrs lie on circles, i.e. the
   different baselines only affect the phases, not the amplitides. 
   <li> If the source is in the field centre (l=0,m=0), all visibilities are real.
   <li> If outside the field centre, the phase increases with baseline length.
   <li> Since XX=I+Q and YY=I-Q, Stokes I and Q can be estimated from the separation
   between the XX and YY circles. Similarly: RR=I+V and LL=I-V
   <li> Since XY=U+iV and YX=U-iV....   Similarly: RL=Q+iU and LR=Q-iU 

   Cookies (some instrumental effects): 
   <li> A non-zero X-Y (R-L) phase-zero-difference (PZD) does not affect the parallel corrs,
   (XX,YY,RR,LL) but changes the phase of the perpendicular corrs (XY,YX,RL,LR).
   <li> Faraday rotation (not implemented yet)
   """
   stub = QRU.on_entry(ns, rider, PlotVIS22_play)
   cc = []

   polrep = opt_PlotVIS22_play_polrep
   nuv = opt_PlotVIS22_play_nuv
   IQUV = opt_PlotVIS22_play_IQUV
   L = opt_PlotVIS22_play_L
   M = opt_PlotVIS22_play_M
   pzd = opt_PlotVIS22_play_PZD

   legend = ['IQUV='+str(IQUV)+' PZD='+str(pzd)+'rad']
   legend.append('source pos (l,m) = ('+str(L)+','+str(M)+') deg')

   rad2deg = 180.0/math.pi                    
   coh = EB.vis22 (ns, IQUV=IQUV, nuv=nuv,
                   L=L/rad2deg, M=M/rad2deg,
                   urms=1.0*rad2deg, vrms=1.0*rad2deg,
                   pzd=pzd, polrep=polrep)

   if polrep=='circular':
      cc.append(PNP.pynode_Plot(ns, coh, 'VIS22C', legend=legend))
      cc.append(PNP.pynode_Plot(ns, coh, 'VIS22C_IQUV', legend=legend))
   else:
      cc.append(PNP.pynode_Plot(ns, coh, 'VIS22', legend=legend))
      cc.append(PNP.pynode_Plot(ns, coh, 'VIS22_IQUV', legend=legend))

   uu = ns.Search(tags='ucoord', subtree=coh)
   vv = ns.Search(tags='vcoord', subtree=coh)
   cc.append(PNP.pynode_Plot(ns, uu+vv, 'XXYY', color='cyan',
                             xlabel='u (wavelengths)',
                             ylabel='v (wavelengths)',
                             title='uv-coverage', legend=legend))

   ll = ns.Search(tags='lpos', subtree=coh)
   mm = ns.Search(tags='mpos', subtree=coh)
   # ll += [ns<<0.0]
   # mm += [ns<<0.0]
   cc.append(PNP.pynode_Plot(ns, ll+mm, 'XXYY', color='green',
                             include_origin=True,
                             # xmin=min(0.0,1.1*L), xmax=max(0.0,1.1*L),
                             # ymin=min(0.0,1.1*M), ymax=max(0.0,1.1*M),
                             xlabel='l (deg w.r.t. phase centre)',
                             ylabel='m (deg w.r.t. phase centre)',
                             title='point source ('+str(IQUV)+')'))

   return QRU.on_exit (ns, rider, cc,
                       viewer='Pylab Plotter')






#================================================================================
#================================================================================
# PyNodeNamedGroups:
#================================================================================

def PyNodeNamedGroups (ns, rider):
   """
   PyNodes of class PyNodeNamedGroups manipulate 'named groups' of values,
   e.g. for plotting. The values are extracted from the results of its
   children, or supplied directly as a list of numbers.
   Classes like PyNodePlot are derived from PyNodeNamedGroups.
   """
   stub = QRU.on_entry(ns, rider, PyNodeNamedGroups)
   cc = []
   override = (opt_alltopics or opt_PNNG_alltopics)

   if override or opt_PNNG_basic:
      cc.append(PyNodeNamedGroups_basic (ns, rider))
   if override or opt_PNNG_nonodes:
      cc.append(PyNodeNamedGroups_nonodes (ns, rider))
   if override or opt_PNNG_concat:
      cc.append(PyNodeNamedGroups_concat (ns, rider))

   cc.append(QRU.helpnode(ns, rider, func=PNNG.string2groupspecs))
   # cc.append(QRU.helpnode(ns, rider, func=PNNG.string2record_VIS22))

   return QRU.on_exit (ns, rider, cc,
                       viewer='Record Browser')


#================================================================================

def PyNodeNamedGroups_basic (ns, rider):
   """
   """
   stub = QRU.on_entry(ns, rider, PyNodeNamedGroups_basic)
   cc = []

   anodes = EB.bundle(ns,'cloud_n6s1', nodename='aa')
   cc.append(PNNG.pynode_NamedGroup(ns, anodes, groupspecs='a'))
   
   return QRU.on_exit (ns, rider, cc,
                       viewer='Record Browser')


#================================================================================

def PyNodeNamedGroups_nonodes (ns, rider):
   """
   While the 'normal' use of named groups is to extract and manipulate groups of
   node results, it is also possible to fill a group directly with a list (vector)
   of values. This opens many new possibilities, especially for plotting (see
   PyNodePlot topic 'nonodes' in this module).

   There are two ways to specify a named group from a list of values:
   <li> via a groupspecs record:
   gs = record(a=range(6), b=range(7), c=range(3))
   pynode_abc = PNNG.pynode_NamedGroup(ns, groupspecs=gs)
   <li> directly:
   pynode_p = PNNG.pynode_NamedGroup(ns, range(9), 'p')
   pynode_q = PNNG.pynode_NamedGroup(ns, range(8), 'q')

   The last method has the simplest syntax, but the first one allows multiple
   groups to be specified. The result may be inspected in the state records of
   the resulting PyNode.

   All groups may be in a single pynode by pynode-concatenation (see below):
   <code_lines>
   cc = [pynode_abc, pynode_q, pynode_p]
   pynode = PNNG.pynode_NamedGroup(ns, cc)
   </code_lines>
   
   """
   stub = QRU.on_entry(ns, rider, PyNodeNamedGroups_nonodes)
   cc = []

   gs = record(a=range(6), b=range(7), c=range(3))
   cc.append(PNNG.pynode_NamedGroup(ns, groupspecs=gs))
   cc.append(PNNG.pynode_NamedGroup(ns, range(9), groupspecs='p'))
   cc.append(PNNG.pynode_NamedGroup(ns, range(8), groupspecs='q'))
   cc.append(PNNG.pynode_NamedGroup(ns, cc))

   return QRU.on_exit (ns, rider, cc,
                       viewer='Record Browser')

#================================================================================

def PyNodeNamedGroups_concat (ns, rider):
   """
   It is possible to concatenate pynodes of class PyNodeNamedGroups.
   Children of these types are ignored for extracting results, but their
   group definitions are copied into the new MeqPyNode. This is very powerful.
   (see also PyNodePlot above).

   <code_lines>
   import PyNodeNamedGroups as PNNG
   pynode_a = PNNG.pynode_NamedGroup(ns, xnodes, 'a')
   pynode_b = PNNG.pynode_NamedGroup(ns, ynodes, 'b')
   pynode_ab = PNNG.pynode_NamedGroup(ns, [pynode_a, pynode_b])
   </code_lines>

   Note that in this case, no groupspecs (name) is specified (as 3rd argument),
   because there are no extra children to extract new groups from (although that
   would be entirely legal, of course).

   More groups, with arbitrary names can be added
   <code_lines>
   pynode_c = PNNG.pynode_NamedGroup(ns, znodes, 'c')
   pynode_abc = PNNG.pynode_NamedGroup(ns, [pynode_ab, pynode_c])
   </code_lines>

   In this experiment, we show the state-records of the resulting pynodes.
   T=Inspect their cache_results, to see how the named groups (a,b,c) are
   extracted from input nodes, and passed from one pynode to another.
   
   Etc, etc. See also the more elaborate concatenation examples below....
   """
   stub = QRU.on_entry(ns, rider, PyNodePlot_concat)
   cc = []
   anodes = EB.bundle(ns,'cloud_n6s1', nodename='aa')
   bnodes = EB.bundle(ns,'cloud_n6s1', nodename='bb')
   cnodes = EB.bundle(ns,'cloud_n6s1', nodename='cc')

   cc.append(PNNG.pynode_NamedGroup(ns, anodes, groupspecs='a'))  # cc[0]
   cc.append(PNNG.pynode_NamedGroup(ns, bnodes, groupspecs='b'))  # cc[1]
   cc.append(PNNG.pynode_NamedGroup(ns, cnodes, groupspecs='c'))  # cc[2]

   cc.append(PNNG.pynode_NamedGroup(ns, [cc[0],cc[1]], nodename='ab'))     # cc[3]: (a,b) -> ab
   cc.append(PNNG.pynode_NamedGroup(ns, [cc[2],cc[3]], nodename='abc'))    # cc[4]: (c,ab) -> abc

   return QRU.on_exit (ns, rider, cc,
                       viewer='Record Browser')








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
   TDLRuntimeMenu("QR_PyNodePlot runtime options:", QRU)
   TDLRuntimeMenu(":")

   global rootnodename
   rootnodename = 'QR_PyNodePlot'               # The name of the node to be executed...
   global rider                                 # global because it is used in tdl_jobs
   rider = QRU.create_rider(rootnodename)       # the rider is a CollatedHelpRecord object
   QRU.on_exit (ns, rider,
                nodes=[QR_PyNodePlot(ns, rider)],
                mode='group')

   # Finished:
   QRU.ET.EN.bundle_orphans(ns)
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





