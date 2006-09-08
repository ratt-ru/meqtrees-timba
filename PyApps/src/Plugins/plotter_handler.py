#!/usr/bin/python

#
# Copyright (C) 2006
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

from numarray import *
from qt import *
from qwt import *

from Timba.utils import verbosity
_dbg = verbosity(0,name='plotter_handler');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

from Timba.Plugins.QwtColorBar import *
from Timba.Plugins.ND_Controller import *
from Timba.Plugins.plot_printer import *
from Timba.Plugins.display_image import *
from Timba.Plugins.vtk_qt_3d_display import *
from Timba.Plugins.ResultsRange import *

class PlotHandler:
  """ Handles changes between 2D Qwt-based displays and 3D VTK display """

  def __init__(self, dataitem,layout_parent):

    self.layout_parent = layout_parent

    self.ND_Controls = None
    self._plotter = QwtImageDisplay('spectra',parent= self.layout_parent)
    self.construction_done = False
    self.plot_2D = True
    self.vells_plot = False
    self.array_selector = None
    self.results_selector = None
    self.spectrum_node_selector = None

    self.array_shape = None 
    self.array_rank = None 
    self.actual_rank = None
    self.colorbar = {}
    self.layout = QGridLayout(self.layout_parent)

    try:
      if dataitem and dataitem.data is not None:
        self.array_shape = dataitem.data.shape
        self.array_rank = dataitem.data.rank
        self.actual_rank = 0
        for i in range(len(self.array_shape)):
          if self.array_shape[i] > 1:
            self.actual_rank = self.actual_rank + 1
        print 'self.actual_rank ', self.actual_rank
# initially, construct 'standard' 2-D display
        self.construct_2D_Display(dataitem.data)
        self.set_data(dataitem);
    except:
      self.addResultsSelector()
      self.addSpectrumSelector()

  def construct_3D_Display(self, make_ND_Controller=True):
    self._plotter = vtk_qt_3d_display(self.layout_parent)
    self._plotter.Add2DButton()
    self.layout.addMultiCellWidget(self._plotter,0,0,0,2)
    self.addResultsSelector()
    QObject.connect(self._plotter, PYSIGNAL('show_2D_Display'), self.change_display_type)
    self._plotter.show()
    if make_ND_Controller:
      self.set_ND_controls(num_axes=3)

    self.addResultsSelector()
    self.addSpectrumSelector()

    self.display_3D_data()

  def display_3D_data(self):
    if self.array_rank > 3:
# pass array to the plotter
      third_axis = None
      second_axis = None
      first_axis = None
      print 'self.array_rank ', self.array_rank
      print 'self.data shape ', self.data.shape
      if self.array_selector is None:
        for i in range(self.array_rank-1,-1,-1):
          if self.data.shape[i] > 1:
            print 'i self.data.shape[i] ', i, ' ', self.data.shape[i]
            if third_axis is None:
              third_axis = i
              print 'third axis ', third_axis
            elif second_axis is None:
              second_axis = i
              print 'second axis ', second_axis
            else:
              if first_axis is None:
                first_axis = i
                print 'first axis ', first_axis
        if not first_axis is None and not second_axis is None:
          self.array_selector = []
          for i in range(self.array_rank):
            if i == first_axis:
              axis_slice = slice(0,self.data.shape[first_axis])
              self.array_selector.append(axis_slice)
            elif i == second_axis:
              axis_slice = slice(0,self.data.shape[second_axis])
              self.array_selector.append(axis_slice)
            elif i == third_axis:
              axis_slice = slice(0,self.data.shape[third_axis])
              self.array_selector.append(axis_slice)
            else:
              self.array_selector.append(0)
      self.array_tuple = tuple(self.array_selector)
      self._plotter.array_plot('data', self.data[self.array_tuple])
      self._plotter.UpdateLabels("first", "second", "third")
    else:
      self._plotter.array_plot('data', self.data)
      self._plotter.UpdateLabels("first", "second", "third")

  def construct_2D_Display(self, data):
    """ Construct 'standard' 2-D plot display using QwtPlot widget """
    if self._plotter is None:
      self._plotter = QwtImageDisplay('spectra',parent= self.layout_parent)
    self.layout.addWidget(self._plotter, 0, 1)
    if self.actual_rank  > 1:
      if data.type() == Complex32 or data.type() == Complex64:
        self.num_colorbars = 2
      else:
        self.num_colorbars = 1
      for i in range(self.num_colorbars):
        self.colorbar[i] =  QwtColorBar(colorbar_number=i,parent=self.layout_parent)
        if i == 0:
          self.layout.addWidget(self.colorbar[i], 0, i)
        else:
          self.layout.addWidget(self.colorbar[i], 0, 2)
        self.colorbar[i].setRange(-1,1,colorbar_number=i)
        self.colorbar[i].show()
        QObject.connect(self._plotter, PYSIGNAL('max_image_range'), self.colorbar[i].setMaxRange) 
        QObject.connect(self._plotter, PYSIGNAL('display_type'), self.colorbar[i].setDisplayType) 
        QObject.connect(self._plotter, PYSIGNAL('show_colorbar_display'), self.colorbar[i].showDisplay)
        QObject.connect(self.colorbar[i], PYSIGNAL('set_image_range'), self._plotter.setImageRange)
        QObject.connect(self._plotter, PYSIGNAL('show_3D_Display'), self.change_display_type)

      if self.actual_rank > 2:
        _dprint(3,' array_plotter: array has actual rank and shape: ', self.actual_rank, ' ', self.array_shape)
        _dprint(3,' array_plotter: so an ND Controller GUI is needed')
        self._plotter.set_original_array_rank(self.actual_rank)
        self.set_ND_controls(num_axes=2)

    self.plotPrinter = plot_printer(self._plotter, self.colorbar)
    QObject.connect(self._plotter, PYSIGNAL('do_print'), self.plotPrinter.do_print)
    self._plotter.show()

    self.addResultsSelector()
    self.addSpectrumSelector()

    self.construction_done = True

  def get_plotter (self):
    return self._plotter

  def set_data (self,dataitem):
    """ this function is the callback interface to the meqbrowser and
        handles new incoming data """
# pass array to the plotter
    self.data = dataitem.data
    self.display_2D_data()

  def display_2D_data (self):
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
        if not first_axis is None and not second_axis is None:
          self.array_selector = []
          for i in range(self.array_rank):
            if i == first_axis:
              axis_slice = slice(0,self.data.shape[first_axis])
              self.array_selector.append(axis_slice)
            elif i == second_axis:
              axis_slice = slice(0,self.data.shape[second_axis])
              self.array_selector.append(axis_slice)
            else:
              self.array_selector.append(0)
      self.array_tuple = tuple(self.array_selector)
      self._plotter.array_plot('data', self.data[self.array_tuple], set_ND_selectors = True)
    else:
      self._plotter.array_plot('data', dataitem.data)

# will need more set up parameters eventually
  def set_ND_controls (self, labels=None,parms=None,num_axes=2):
    """ this function adds the extra GUI control buttons etc if we are
        displaying data for a numarray of dimension 3 or greater """
    if not self.ND_Controls is None:
      self.ND_Controls.reparent(QWidget(), 0, QPoint())
      self.ND_Controls = None
    if self.actual_rank == num_axes:
      return
    self.ND_Controls = ND_Controller(self.array_shape, labels, parms, num_axes, self.layout_parent) 
    if not self.vells_plot:
      QObject.connect(self.ND_Controls, PYSIGNAL('sliderValueChanged'), self.setArraySelector)
      QObject.connect(self.ND_Controls, PYSIGNAL('defineSelectedAxes'), self.setSelectedAxes)
    QObject.connect(self._plotter, PYSIGNAL('show_ND_Controller'), self.ND_Controls.showDisplay)

    self.layout.addMultiCellWidget(self.ND_Controls,1,1,0,2)
    self.ND_Controls.showDisplay(1)

  def change_display_type (self, toggle_ND_Display):
    print 'display request value ', toggle_ND_Display
    if toggle_ND_Display > 0:
      self._plotter.reparent(QWidget(), 0, QPoint())
      self._plotter = None
      print 'self.num_colorbars ', self.num_colorbars
      for i in range(self.num_colorbars):
        self.colorbar[i].reparent(QWidget(), 0, QPoint())
      # create the 3D plotter
      self.plot_2D = False
      self.array_selector = None
      self.construct_3D_Display()

    if toggle_ND_Display == 0:
      self._plotter.reparent(QWidget(), 0, QPoint())
      self._plotter = None
      # create the 3D plotter
      self.plot_2D = True
      self.construct_2D_Display(self.data)
      self.array_selector = None
      self.display_2D_data()


  def setArraySelector (self,lcd_number, slider_value, display_string):
    """ update the subsection of an N-dimensional array 
        and display the selected subarray.
    """
    print 'setArraySelector initial self.array_tuple ', self.array_tuple
    print 'setArraySelector lcd_number slider_value ', lcd_number, ' ', slider_value
    self.array_selector[lcd_number] = slider_value
    self.array_tuple = tuple(self.array_selector)
    print 'setArraySelector: self.array_tuple ', self.array_tuple
    self._plotter.array_plot('data: '+ display_string, self.data[self.array_tuple], set_ND_selectors=True)

  def setSelectedAxes (self,first_axis, second_axis, third_axis=-1):
    """ update the selected axes of an N-dimensional array
        and display the selected sub-array.
    """
    try:
      self._plotter.delete_cross_sections()
    except:
      pass
    self.array_selector = []
    for i in range(self.array_rank):
      if i == first_axis: 
        axis_slice = slice(0,self.array_shape[first_axis])
        self.array_selector.append(axis_slice)
      elif i == second_axis:
        axis_slice = slice(0,self.array_shape[second_axis])
        self.array_selector.append(axis_slice)
      elif i == third_axis:
        axis_slice = slice(0,self.array_shape[third_axis])
        self.array_selector.append(axis_slice)
        self._plotter.reparent(QWidget(), 0, QPoint())
      else:
        self.array_selector.append(0)
    self.array_tuple = tuple(self.array_selector)
    print 'setSelectedAxes self.array_tuple ', self.array_tuple
    if not self.plot_2D:
      self.construct_3D_Display(make_ND_Controller=False)
    else:
      self._plotter.array_plot('data', self.data[self.array_tuple])

  def setPlotVellsFlag(self, flag = True):
    self.vells_plot = flag

  def addResultsSelector(self):
    if self.results_selector is None:
      self.results_selector = ResultsRange(self.layout_parent)
      self.layout.addWidget(self.results_selector, 1,1, Qt.AlignHCenter)
      self.results_selector.hide()

  def addSpectrumSelector(self):
    if self.spectrum_node_selector is None:
      self.spectrum_node_selector = ResultsRange(self.layout_parent)
      self.spectrum_node_selector.setStringInfo(' spectrum ')
      self.layout.addWidget(self.spectrum_node_selector, 2,1,Qt.AlignHCenter)
      self.spectrum_node_selector.hide()


# wrapper functions needed for result_plotter

  def getResultsSelector(self):
    return self.results_selector 

  def getSpectrumNodeSelector(self):
    return self.spectrum_node_selector

  def getSpectrumTags(self):
    return self._plotter.getSpectrumTags()

  def setResultsSelector(self):
    self.results_selector.show()
    self._plotter.setResultsSelector()

  def setSpectrumMenuItems(self, plot_menus): 
    self._plotter.setSpectrumMenuItems(plot_menus)

  def setSpectrumMarkers(self, marker_parms, marker_labels):
    self._plotter.setSpectrumMarkers(marker_parms, marker_labels)

  def array_plot (self, data_label, incoming_plot_array, flip_axes=True, set_ND_selectors = False):
    self.array_shape = incoming_plot_array.shape
    self.array_rank =  incoming_plot_array.rank
    self.actual_rank = 0
    for i in range(len(self.array_shape)):
      if self.array_shape[i] > 1:
        self.actual_rank = self.actual_rank + 1
    if not self.construction_done:
      self.construct_2D_Display(incoming_plot_array)
    self._plotter.array_plot(data_label, incoming_plot_array, flip_axes, set_ND_selectors)

  def plot_data(self, visu_record, attribute_list=None, label=''):
    self._plotter.plot_data(visu_record, attribute_list, label)

  def delete_cross_sections(self):
    self._plotter.delete_cross_sections()

  def setVellsPlot(self, do_vells_plot=True):
    self._plotter.setVellsPlot(do_vells_plot)

  def setAxisParms(self, axis_parms):
    self._plotter.setAxisParms(axis_parms)

  def initVellsContextMenu (self):
    self._plotter.initVellsContextMenu()

  def set_flag_toggles(self, flag_plane=None, flag_setting=False):
    self._plotter.set_flag_toggles(flag_plane, flag_setting)

  def setFlagsData (self, incoming_flag_array, flip_axes=True):
    self._plotter.setFlagsData(incoming_flag_array, flip_axes)

  def setMenuItems(self, menu_data):
    self._plotter.setMenuItems(menu_data)

  def plot_vells_array (self, data_array, data_label=" "):
    self.array_shape = data_array.shape
    self.array_rank =  data_array.rank
    self.actual_rank = 0
    for i in range(len(self.array_shape)):
      if self.array_shape[i] > 1:
        self.actual_rank = self.actual_rank + 1
    if not self.construction_done:
      self.construct_2D_Display(data_array)
    self._plotter.plot_vells_array(data_array, data_label)

  def setVellsParms(self, vells_axis_parms, axis_labels):
    self._plotter.setVellsParms(vells_axis_parms, axis_labels)

  def set_solver_metrics(self,metrics_tuple):
    self._plotter.set_solver_metrics(metrics_tuple)

  def report_scalar_value(self, data_label, scalar_data):
    self._plotter.report_scalar_value(data_label, scalar_data)

  def set_toggle_array_rank(self, toggle_array_rank):
    self._plotter.set_original_array_rank(toggle_array_rank)

  def reset_color_bar(self, reset_value=True):
    self._plotter.reset_color_bar(reset_value)

  def getLayout(self):
    return self.layout
