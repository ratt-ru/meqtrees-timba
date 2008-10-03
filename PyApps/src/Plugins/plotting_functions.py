#!/usr/bin/python

#
# Copyright (C) 2002-2007
# ASTRON (Netherlands Foundation for Research in Astronomy)
# and The MeqTree Foundation
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# these functions create / delete various widgets related
# to plotting. I've tried to collect all such operations
# into one file so that maintenance is easy.


# modules that are imported
from Timba import utils
from Timba.GUI import widgets

from qt import *

global has_vtk
has_vtk = False
try:
  from Timba.Plugins.vtk_qt_3d_display import *
  has_vtk = True
except:
  pass

from display_image import *
from QwtColorBar import *
from ND_Controller import *
from plot_printer import *

from Timba.utils import verbosity
_dbg = verbosity(0,name='plotting_functions');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

def create_ColorBar (layout,layout_parent, plotter, plotPrinter):
  """ this function adds a colorbar for 2-D displays """

  # create two color bars in case we are displaying complex arrays
  colorbar = {}
  for i in range(2):
    colorbar[i] =  QwtColorBar(colorbar_number= i, parent=layout_parent)
    colorbar[i].setMaxRange((-1, 1))
    QObject.connect(plotter, PYSIGNAL('max_image_range'), colorbar[i].setMaxRange) 
    QObject.connect(plotter, PYSIGNAL('display_type'), colorbar[i].setDisplayType) 
    QObject.connect(plotter, PYSIGNAL('show_colorbar_display'), colorbar[i].showDisplay)
    QObject.connect(colorbar[i], PYSIGNAL('set_image_range'), plotter.setImageRange) 
    if i == 0:
      layout.addWidget(colorbar[i], 0, i)
      colorbar[i].show()
    else:
      layout.addWidget(colorbar[i], 0, 2)
      colorbar[i].hide()
  plotPrinter.add_colorbar(colorbar)
  return colorbar

def delete_2D_Plotters(colorbar, visu_plotter):
  """ delete 2D plotter and associated colorbars """
  _dprint(3, 'got 3d plot request, deleting 2-d stuff')
  colorbar[0].reparent(QWidget(), 0, QPoint())
  colorbar[1].reparent(QWidget(), 0, QPoint())
  colorbar = {}
  visu_plotter.reparent(QWidget(), 0, QPoint())
  visu_plotter = None
  return visu_plotter

def create_array_selector(plotter, rank, shape, first_axis,second_axis,third_axis=-1):
  """ create subarray selection to be extracted from ND array for display """
  if not plotter is None:
    plotter.delete_cross_sections()
  if first_axis is None:
    first_axis = -1
  if third_axis is None:
    third_axis = -1
  array_selector = []
  for i in range(rank):
    if i == first_axis:
      axis_slice = slice(0,shape[first_axis])
      array_selector.append(axis_slice)
    elif i == second_axis:
      axis_slice = slice(0,shape[second_axis])
      array_selector.append(axis_slice)
    elif i == third_axis:
      axis_slice = slice(0,shape[third_axis])
      array_selector.append(axis_slice)
    else:
      array_selector.append(0)
  return array_selector

def create_2D_Plotters(layout, layout_parent, ND_plotter):
  """ create 2D plotter """
  if not ND_plotter is None:
    ND_plotter.delete_vtk_renderer()
    ND_plotter.hide_vtk_controls()
  twoD_plotter = QwtImageDisplay('spectra',parent=layout_parent)
  layout.addWidget(twoD_plotter, 0, 1)
  twoD_plotter.show()
  plotPrinter = plot_printer(twoD_plotter)
  return twoD_plotter, plotPrinter

def create_ND_Plotter (layout, layout_parent):
  """ create a new ND plotter """
  ND_plotter = vtk_qt_3d_display(layout_parent)
  layout.addMultiCellWidget(ND_plotter,0,0,0,2)
  ND_plotter.show()
  _dprint(3, 'issued show call to ND_plotter')
  return ND_plotter

def create_ND_Controls (layout, layout_parent, array_shape, ND_Controls, ND_plotter, labels=None, parms=None, num_axes=2):
  """ this function adds the extra GUI control buttons etc if we are
        displaying data for a Timba.array of dimension 3 or greater 
  """
  if not ND_Controls is None:
    ND_Controls.reparent(QWidget(), 0, QPoint())
    ND_Controls = None
  ND_Controls = ND_Controller(array_shape, labels, parms, num_axes,layout_parent)
  layout.addMultiCellWidget(ND_Controls,2,2,0,2)
  if ND_Controls.get_num_selectors() > num_axes:
    ND_Controls.showDisplay(1)
  else:
    ND_Controls.showDisplay(0)
    if not ND_plotter is None:
      ND_plotter.HideNDButton()
  _dprint(3, 'ND_Controls object should appear ', ND_Controls)
  return ND_Controls


