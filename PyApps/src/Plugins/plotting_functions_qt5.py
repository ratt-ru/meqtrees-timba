#!/usr/bin/env python3

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
#
#  (c) 2013.				 (c) 2011.
#  National Research Council		 Conseil national de recherches
#  Ottawa, Canada, K1A 0R6 		 Ottawa, Canada, K1A 0R6
#
#  This software is free software;	 Ce logiciel est libre, vous
#  you can redistribute it and/or	 pouvez le redistribuer et/ou le
#  modify it under the terms of	         modifier selon les termes de la
#  the GNU General Public License	 Licence Publique Generale GNU
#  as published by the Free		 publiee par la Free Software
#  Software Foundation; either	 	 Foundation (version 3 ou bien
#  version 2 of the License, or	 	 toute autre version ulterieure
#  (at your option) any later	 	 choisie par vous).
#  version.
#
#  This software is distributed in	 Ce logiciel est distribue car
#  the hope that it will be		 potentiellement utile, mais
#  useful, but WITHOUT ANY		 SANS AUCUNE GARANTIE, ni
#  WARRANTY; without even the	 	 explicite ni implicite, y
#  implied warranty of			 compris les garanties de
#  MERCHANTABILITY or FITNESS FOR	 commercialisation ou
#  A PARTICULAR PURPOSE.  See the	 d'adaptation dans un but
#  GNU General Public License for	 specifique. Reportez-vous a la
#  more details.			 Licence Publique Generale GNU
#  					 pour plus de details.
#
#  You should have received a copy	 Vous devez avoir recu une copie
#  of the GNU General Public		 de la Licence Publique Generale
#  License along with this		 GNU en meme temps que ce
#  software; if not, contact the	 logiciel ; si ce n'est pas le
#  Free Software Foundation, Inc.	 cas, communiquez avec la Free
#  at http://www.fsf.org.		 Software Foundation, Inc. au
#						 http://www.fsf.org.
#
#  email:				 courriel:
#  business@hia-iha.nrc-cnrc.gc.ca	 business@hia-iha.nrc-cnrc.gc.ca
#
#  National Research Council		 Conseil national de recherches
#      Canada				    Canada
#  Herzberg Institute of Astrophysics	 Institut Herzberg d'astrophysique
#  5071 West Saanich Rd.		 5071 West Saanich Rd.
#  Victoria BC V9E 2E7			 Victoria BC V9E 2E7
#  CANADA					 CANADA
#

# these functions create / delete various widgets related
# to plotting. I've tried to collect all such operations
# into one file so that maintenance is easy.

from qwt.qt.QtGui import QApplication,QWidget
from qwt.qt.QtCore import Qt

import numpy

# modules that are imported

HAS_TIMBA = False
try:
  from Timba import utils
  from Timba.GUI import widgets
  from Timba.Plugins.display_image_qt5 import QwtImageDisplay
  from Timba.Plugins.QwtColorBar_qt5 import QwtColorBar
  from Timba.Plugins.ND_Controller_qt5 import ND_Controller

  from Timba.utils import verbosity
  _dbg = verbosity(0,name='plotting_functions');
  _dprint = _dbg.dprint;
  _dprintf = _dbg.dprintf;
  HAS_TIMBA = True
except:
  pass

def create_ColorBar (layout,layout_parent, plotter, plotPrinter):
  """ this function adds a colorbar for 2-D displays """

  # create two color bars in case we are displaying complex arrays
  colorbar = {}
  for i in range(2):
    colorbar[i] =  QwtColorBar(colorbar_number= i, parent=layout_parent)
    colorbar[i].setMaxRange((-1, 1))
    plotter.max_image_range.connect(colorbar[i].handleRangeParms)
    plotter.display_type.connect(colorbar[i].setDisplayType)
    plotter.show_colorbar_display.connect(colorbar[i].showDisplay)
    colorbar[i].set_image_range.connect(plotter.setImageRange)
    if i == 0:
      layout.addWidget(colorbar[i], 0, i)
      colorbar[i].show()
    else:
      layout.addWidget(colorbar[i], 0, 2)
      colorbar[i].hide()
# plotPrinter.add_colorbar(colorbar)
  return colorbar

def delete_2D_Plotters(colorbar, visu_plotter):
  """ delete 2D plotter and associated colorbars """
  if HAS_TIMBA:
    _dprint(3, 'got 3d plot request, deleting 2-d stuff')
  colorbar[0].setParent(QWidget())
  colorbar[1].setParent(QWidget())
  colorbar = {}
  visu_plotter.setParent(QWidget())
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

def create_2D_Plotters(layout, layout_parent):
  """ create 2D plotter """
  twoD_plotter = QwtImageDisplay(layout_parent)
  layout.addWidget(twoD_plotter, 0, 1)
  twoD_plotter.show()
  return twoD_plotter

def create_ND_Plotter (layout, layout_parent):
  """ create a new ND plotter """
  ND_plotter = vtk_qt_3d_display(layout_parent)
  layout.addWidget(ND_plotter,0,0,1,2)
  ND_plotter.show()
  if HAS_TIMBA:
    _dprint(3, 'issued show call to ND_plotter')
  return ND_plotter

def create_ND_Controls (layout, layout_parent, array_shape, ND_Controls, ND_plotter, labels=None, parms=None, num_axes=2):
  """ this function adds the extra GUI control buttons etc if we are
        displaying data for a Timba.array of dimension 3 or greater 
  """
  if not ND_Controls is None:
    ND_Controls.setParent(QWidget())
    ND_Controls = None
  ND_Controls = ND_Controller(array_shape, labels, parms, num_axes,layout_parent)
  layout.addWidget(ND_Controls,2,0,1,2)
  if ND_Controls.get_num_selectors() > num_axes:
    ND_Controls.showDisplay(1)
  else:
    ND_Controls.showDisplay(0)
    if not ND_plotter is None:
      ND_plotter.HideNDButton()
  if HAS_TIMBA:
    _dprint(3, 'ND_Controls object should appear ', ND_Controls)
  return ND_Controls


