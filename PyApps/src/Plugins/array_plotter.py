#!/usr/bin/env python3

# modules that are imported

#% $Id$ 

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
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import numpy

from qwt.qt.QtGui import QApplication, QGridLayout, QLabel, QWidget, QFont
from qwt.qt.QtCore import Qt

HAS_TIMBA = False
try:
  from Timba import utils
  from Timba.Meq import meqds
  from Timba.Meq.meqds import mqs
  from Timba.GUI.pixmaps import pixmaps
  from Timba.GUI import widgets
  from Timba.GUI.browsers import *
  from Timba import Grid

  from Timba.Plugins.display_image_qt5 import QwtImageDisplay
  from Timba.Plugins.QwtPlotImage_qt5 import QwtPlotImage
  from Timba.Plugins.QwtColorBar_qt5 import QwtColorBar
  from Timba.Plugins.ND_Controller_qt5 import ND_Controller
  import Timba.Plugins.plotting_functions_qt5 as plot_func
  #from Timba.Plugins.plot_printer_qt5 import *


  from Timba.utils import verbosity
  _dbg = verbosity(0,name='array_plotter');
  _dprint = _dbg.dprint;
  _dprintf = _dbg.dprintf;
  HAS_TIMBA = True
except:
  pass

global has_vtk
has_vtk = False

class ArrayPlotter(GriddedPlugin):
  """ a class to plot raw arrays contained within a Meq tree """

  _icon = pixmaps.bars3d
  viewer_name = "Array Plotter";
  def is_viewable (data):
    return len(data) > 0;
  is_viewable = staticmethod(is_viewable);

  def __init__(self,gw,dataitem,cellspec={},**opts):
    GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);
    if HAS_TIMBA: _dprint(3,'** array_plotter: starting init')
    self.layout_parent = None
    self.layout_created = False
    self.twoD_plotter = None
    self.status_label = None
    self.ND_plotter = None
    self.ND_Controls = None
    self.png_number = 0

    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

#  def __del__(self):
#    print "in destructor"

  def create_2D_plotter(self):
    if not self.ND_plotter is None:
      self.ND_plotter.close()
      self.ND_plotter = None
    self.twoD_plotter, self.plotPrinter = plot_func.create_2D_Plotters(self.layout, self.layout_parent)
    self.twoD_plotter.colorbar_needed.connect(self.set_ColorBar)
    self.twoD_plotter.show_ND_Controller.connect(self.ND_controller_showDisplay)
    self.twoD_plotter.show_3D_Display.connect(self.show_3D_Display)
    self.twoD_plotter.do_print.connect(self.plotPrinter.do_print)
    self.twoD_plotter.save_display.connect(self.grab_display)
    # create status label display
    self.status_label = Qt.QLabel(self.layout_parent)
    sansFont = QFont( "Helvetica [Cronyx]", 8 )
    self.status_label.setFont(sansFont)
#   self.layout.addMultiCellWidget(self.status_label,1,1,0,2)
    self.layout.addWidget(self.status_label,1,0,1,2)
    self.status_label.setText("Move the mouse within the plot canvas"
                            " to show the cursor position.")
    self.status_label.show()
    self.twoD_plotter.status_update.connect(self.update_status)
  # create_2D_plotter

  def update_status(self, status):
     if not status is None:
       self.status_label.setText(str(status))

  def grab_display(self, title):
    self.png_number = self.png_number + 1
    png_str = str(self.png_number)
    if title is None:
      save_file = './meqbrowser' + png_str + '.png'
    else:
      save_file = title + png_str + '.png'
    save_file_no_space= save_file.replace(' ','_')
    result = Qt.QPixmap.grabWidget(self.layout_parent).save(save_file_no_space, "PNG")

  def create_layout_stuff(self):
    """ create grid layouts into which plotter widgets are inserted """
    if self.layout_parent is None or not self.layout_created:
      self.layout_parent = Qt.QWidget(self.wparent())
      self.layout = Qt.QGridLayout(self.layout_parent)
      self.set_widgets(self.layout_parent,self.dataitem.caption,icon=self.icon())
      self.layout_created = True
    self._wtop = self.layout_parent;

  def wtop (self):
    return self._wtop

  def set_data (self,dataitem,default_open=None,**opts):
    """ this function is the callback interface to the meqbrowser and
        handles new incoming data """

    self.dataitem = dataitem
# first create layout stuff
    self.create_layout_stuff()

# now create plotter and colorbar
    if self.twoD_plotter is None:
      self.create_2D_plotter()
    self.plot_2D_array()

  def test_scalar_value (self, data_array, data_label):
    """ test if incoming 'array' contains only a scalar value """
# do we have a scalar?
    is_scalar = False
    scalar_data = 0.0
    try:
      shape = data_array.shape
      if HAS_TIMBA: _dprint(3,'data_array shape is ', shape)
    except:
      is_scalar = True
      scalar_data = data_array
    if not is_scalar and len(shape) == 1:
      if shape[0] == 1:
        is_scalar = True
        scalar_data = data_array[0]
    if not is_scalar:
      test_scalar = True
      for i in range(len(shape)):
        if shape[i] > 1:
          test_scalar = False
      is_scalar = test_scalar
      if is_scalar:
        scalar_data = data_array
    if is_scalar:
      self.twoD_plotter.report_scalar_value(data_label, scalar_data)
      return True
    else:
      return False
# enable & highlight the cell
    self.enable();
    self.flash_refresh();

  def plot_2D_array (self):

    self.data = self.dataitem.data

# do we have a scalar?
    if self.test_scalar_value(self.data, 'incoming data'):
      return 

# first figure out the actual rank of the array we are plotting

    self.actual_rank = 0
    self.array_shape = self.dataitem.data.shape
    self.array_rank = self.dataitem.data.ndim
    for i in range(len(self.array_shape)):
      if self.array_shape[i] > 1:
        self.actual_rank = self.actual_rank + 1
    self.array_selector = None
    if self.actual_rank > 2:
      self.twoD_plotter.set_original_array_rank(self.actual_rank)
      self.set_ND_controls()

# reset colorbar just in case
    if self.actual_rank >= 2:
      self.twoD_plotter.reset_color_bar(True)

# pass array to the plotter
    if self.array_rank > 2:
      if self.array_selector is None:
        second_axis = None
        first_axis = None
        for i in range(self.array_rank-1,-1,-1):
          if self.data.shape[i] > 1:
            if second_axis is None:
              second_axis = i
            else:
              if first_axis is None:
                first_axis = i
        if not second_axis is None:
          self.array_selector = plot_func.create_array_selector(None, self.array_rank, self.data.shape, first_axis,second_axis, -1)
      self.array_tuple = tuple(self.array_selector)
      self.twoD_plotter.array_plot(self.data[self.array_tuple],data_label='data')
    else:
      self.twoD_plotter.array_plot(self.data,data_label='data')


  def plot_3D_array (self, display_flag_3D):
# first figure out the actual rank of the array we are plotting
    self.actual_rank = 0
    self.array_shape = self.dataitem.data.shape
    self.array_rank = self.dataitem.data.ndim
    for i in range(len(self.array_shape)):
      if self.array_shape[i] > 1:
        self.actual_rank = self.actual_rank + 1
    if display_flag_3D and self.actual_rank > 2:
      self.set_ND_controls(None, None, num_axes=3)
      self.array_selector = None
    else:
      if not self.ND_Controls is None:
        self.ND_Controls.setParent(Qt.QWidget())
        self.ND_Controls = None
# pass initial array to the plotter
    if self.array_rank > 2:
      self.data = self.dataitem.data
      if self.array_selector is None:
        third_axis = None
        second_axis = None
        first_axis = None
        for i in range(self.array_rank-1,-1,-1):
          if self.data.shape[i] > 1:
            if third_axis is None:
              third_axis = i
            elif second_axis is None:
              second_axis = i
            else:
              if first_axis is None:
                first_axis = i
        if not first_axis is None and not second_axis is None and not third_axis is None:
          self.array_selector = plot_func.create_array_selector(None, self.array_rank, self.data.shape, first_axis,second_axis,third_axis)
      self.array_tuple = tuple(self.array_selector)
      plot_array =  self.data[self.array_tuple]
    else:
      plot_array = self.data
    if plot_array.min() == plot_array.max():
      return
    else:
      self.ND_plotter.array_plot(plot_array, data_label='data ')

# enable & highlight the cell
    self.enable();
    self.flash_refresh();

  def setSelectedAxes (self,first_axis, second_axis, third_axis=-1):
    """ update the selected axes of an N-dimensional array
        and display the selected sub-array.
    """
    self.array_selector = plot_func.create_array_selector(self.twoD_plotter, self.array_rank, self.array_shape, first_axis,second_axis,third_axis)
    self.array_tuple = tuple(self.array_selector)
    if not self.twoD_plotter is None:
      # reset various parameters and fields
      self.twoD_plotter.reset_zoom()
      self.twoD_plotter.delete_cross_sections()
      self.twoD_plotter.reset_color_bar(True)
      self.twoD_plotter.array_plot(self.data[self.array_tuple],data_label='data')
    else:
      if not self.ND_plotter is None:
        self.ND_plotter.delete_vtk_renderer()
        self.ND_plotter.array_plot(self.data[self.array_tuple],data_label='data ')
        axis_parms = []
        axis_parms.append('axis ' + str(first_axis))
        axis_parms.append('axis ' + str(second_axis))
        axis_parms.append('axis ' + str(third_axis))
        self.ND_plotter.setAxisParms(axis_parms)

  def setArraySelector (self,lcd_number, slider_value, display_string=None):
    """ update the subsection of an N-dimensional array 
        and display the selected subarray.
    """
    self.array_selector[lcd_number] = slider_value
    self.array_tuple = tuple(self.array_selector)
    if not self.twoD_plotter is None:
      # reset color bar request - just in case
      self.twoD_plotter.reset_color_bar(True)
      self.twoD_plotter.array_plot(self.data[self.array_tuple],data_label='data')
    else:
      self.ND_plotter.array_plot(self.data[self.array_tuple],data_label='data ')

  def ND_controller_showDisplay(self, show_self):
    """ tells ND_Controller to show or hide itself """
    if not self.ND_Controls is None:
      self.ND_Controls.showDisplay(show_self)

  def set_ND_controls (self, labels=None, parms=None, num_axes=2):
    """ this function adds the extra GUI control buttons etc if we are
        displaying data for a numpy array of dimension 3 or greater """

    self.ND_Controls = plot_func.create_ND_Controls(self.layout, self.layout_parent, self.array_shape, self.ND_Controls, self.ND_plotter, labels, parms, num_axes)

    self.ND_Controls.sliderValueChanged.connect(self.setArraySelector)
    self.ND_Controls.defineSelectedAxes.connect(self.setSelectedAxes)

  def show_3D_Display(self, display_flag_3D):
    if not has_vtk:
      return
    self.twoD_plotter = delete_2D_Plotters(self.colorbar, self.twoD_plotter)
    self.status_label.setParent(Qt.QWidget())
    self.status_label = None

    if self.ND_plotter is None:
      self.ND_plotter = plot_func.create_ND_Plotter (self.layout, self.layout_parent)
      self.ND_plotter.show_2D_Display.connect(self.show_2D_Display)
      self.ND_plotter.show_ND_Controller.connect(self.ND_controller_showDisplay)
    else:
      self.ND_plotter.delete_vtk_renderer()
      self.ND_plotter.show_vtk_controls()

# create 3-D Controller
    self.plot_3D_array(display_flag_3D)

  def show_2D_Display(self, display_flag):
    if HAS_TIMBA: _dprint(3, 'in show_2D_Display ')
    self.create_2D_plotter()
# create 3-D Controller appropriate for 2-D screen displays
    self.plot_2D_array()

  def set_ColorBar (self):
    """ this function adds a colorbar for 2-D displays """
    # create two color bars in case we are displaying complex arrays
    self.colorbar = plot_func.create_ColorBar(self.layout, self.layout_parent, self.twoD_plotter, self.plotPrinter)

Grid.Services.registerViewer(array_class,ArrayPlotter,priority=10)
