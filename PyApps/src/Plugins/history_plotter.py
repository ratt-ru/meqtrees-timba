#!/usr/bin/python

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

from math import sin
from math import cos
from math import pow
from math import sqrt

# modules that are imported
from Timba.dmi import *
from Timba import utils
from Timba.Meq import meqds
from Timba.Meq.meqds import mqs
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI import widgets
from Timba.GUI.browsers import *
from Timba import Grid

import numpy
from qt import *
from Timba.Plugins.display_image import *
from Timba.Plugins.realvsimag import *
from Timba.Plugins.plotting_functions import *
from QwtPlotImage import *
from QwtColorBar import *
from ND_Controller import *
from plot_printer import *

from Timba.utils import verbosity
_dbg = verbosity(0,name='history_plotter');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

# The HistoryPlotter plots the contents of a MeqHistoryCollect node
class HistoryPlotter(GriddedPlugin):
  """ a class to plot the history of some parameter. It can be
      a scalar or an array """

  _icon = pixmaps.bars3d
  viewer_name = "History Plotter";
  def is_viewable (data):
    return len(data) > 0;
  is_viewable = staticmethod(is_viewable);

# the following global tables replicate similar tables found in the
# realvsimag plotter. The idea is that the system first checks the
# contents of 'history' plot records against these tables here 
# during tree traversal. Otherwise every leaf node would issue
# warnings about the same unacceptable parameters - which would
# really irritate the user. The 'check_attributes' function defined
# below does the work.
  color_table = {
        'none': None,
        'black': Qt.black,
        'blue': Qt.blue,
        'cyan': Qt.cyan,
        'gray': Qt.gray,
        'green': Qt.green,
        'magenta': Qt.magenta,
        'red': Qt.red,
        'white': Qt.white,
        'yellow': Qt.yellow,
        'darkBlue' : Qt.darkBlue,
        'darkCyan' : Qt.darkCyan,
        'darkGray' : Qt.darkGray,
        'darkGreen' : Qt.darkGreen,
        'darkMagenta' : Qt.darkMagenta,
        'darkRed' : Qt.darkRed,
        'darkYellow' : Qt.darkYellow,
        'lightGray' : Qt.lightGray,
        }

  symbol_table = {
#       'none': Qwt.QwtSymbol.None,
        'rectangle': Qwt.QwtSymbol.Rect,
        'square': Qwt.QwtSymbol.Rect,
        'ellipse': Qwt.QwtSymbol.Ellipse,
        'dot': Qwt.QwtSymbol.Ellipse,
        'circle': Qwt.QwtSymbol.Ellipse,
	'xcross': Qwt.QwtSymbol.XCross,
	'cross': Qwt.QwtSymbol.Cross,
	'triangle': Qwt.QwtSymbol.Triangle,
	'diamond': Qwt.QwtSymbol.Diamond,
        }

  line_style_table = {
        'none': Qwt.QwtPlotCurve.NoCurve,
        'lines' : Qwt.QwtPlotCurve.Lines,
        'dots' : Qwt.QwtPlotCurve.Dots,
        'SolidLine' : Qt.SolidLine,
        'DashLine' : Qt.DashLine,
        'DotLine' : Qt.DotLine,
        'DashDotLine' : Qt.DashDotLine,
        'DashDotDotLine' : Qt.DashDotDotLine,
        'solidline' : Qt.SolidLine,
        'dashline' : Qt.DashLine,
        'dotline' : Qt.DotLine,
        'dashdotline' : Qt.DashDotLine,
        'dashdotdotline' : Qt.DashDotDotLine,
        }
  
  def __init__(self,gw,dataitem,cellspec={},**opts):
    GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);
    """ Instantiate HippoDraw objects that are used to control
        various aspects of plotting, if the hippo plotter
        is instantiated.
    """
    self._rec = None;
    self._plot_type = None
    self._wtop = None;
    self.label = '';
    self.dataitem = dataitem
    self._attributes_checked = False
    self.displayed_invalid = False
    self.array_selector = None
    self.ND_plotter = None
    self.reset_plot_stuff()

    self._window_controller = None
    _dprint(3, 'at end of init: self._plotter = ', self._plotter)

# back to 'real' work
    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

  def reset_plot_stuff (self):
    self._plotter = None
    self.colorbar = None
    self.layout_parent = None
    self.layout = None
    self.ND_Controls = None

  def __del__(self):
    if self._window_controller:
      self._window_controller.closeAllWindows()
                                                                                           
# function needed by Oleg for reasons known only to him!
  def wtop (self):
    return self._wtop;

  def set_data (self,dataitem,default_open=None,**opts):
    """ this callback receives data from the meqbrowser, when the
        user has requested a plot. It decides whether the data is
        from a history data record, and  after any
        necessary preprocssing forwards the data to one of
        the functions which does the actual plotting """

    self._rec = dataitem.data;
# if we are single stepping through requests, Oleg may reset the
# cache, so check for a non-data record situation
    if isinstance(self._rec, bool):
      return

    self.label = '';  # extra label, filled in if possible
    if dmi_typename(self._rec) != 'MeqResult': # data is not already a result?
#   try to put request ID^S in label
      rq_id_found = False
      if "request_id" in self._rec.cache:
        self.label = "rq " + str(self._rec.cache.request_id);
        rq_id_found = True
      if "result" in self._rec.cache:
        self._rec = self._rec.cache.result; # look for cache.result record
        if not rq_id_found and "request_id" in self._rec:
          self.label = "rq " + str(self._rec.request_id);
      else:
        Message = "No result record was found in the cache, so no plot can be made with the <b>history plotter</b>! You may wish to select another type of display."
        cache_message = QLabel(Message,self.wparent())
        cache_message.setTextFormat(Qt.RichText)
        self._wtop = cache_message
        self.set_widgets(cache_message)
        self.reset_plot_stuff()
        return

    if "history" in self._rec:
# do plotting of visualization data
      self.display_history_data()
    else:
      Message = "Result record does not contain history key, so no plot can be made with the <b>history plotter</b>! You may wish to select another type of display."
      cache_message = QLabel(Message,self.wparent())
      cache_message.setTextFormat(Qt.RichText)
      self._wtop = cache_message
      self.set_widgets(cache_message)
      self.reset_plot_stuff()
      return

# enable & highlight the cell
    self.enable();
    self.flash_refresh();

    _dprint(3, 'exiting set_data')

  def display_history_data (self):
    """ extract 'value' data from incoming history data record and
      create a plotter object to plot the data 
    """
    _dprint(3, ' ')
    if 'value' in self._rec.history:
      (self._plot_array, self._flag_plot_array) = self.create_plot_array(self._rec.history['value'])
      try:
        _dprint(3, 'plot_array rank and shape ', self._plot_array.ndim, ' ', self._plot_array.shape)
      except: pass;
      if self._plot_array is None:
        return
      self.actual_rank = 0
      shape = self._plot_array.shape
      for i in range(self._plot_array.ndim):
        if shape[i] > 1:
          self.actual_rank = self.actual_rank + 1
      _dprint(3, 'plot_array actual rank ', self.actual_rank)
      self.create_image_plotters()

      if self._plot_array.ndim > 2:
        if self.array_selector is None:
          second_axis = None
          first_axis = None
          for i in range(self._plot_array.ndim-1,-1,-1):
            if self._plot_array.shape[i] > 1:
              if second_axis is None:
                second_axis = i
              else:
                if first_axis is None:
                  first_axis = i
          self.array_selector = []
          for i in range(self._plot_array.ndim):
            if not first_axis is None and i == first_axis:
              axis_slice = slice(0,self._plot_array.shape[first_axis])
              self.array_selector.append(axis_slice)
            elif not second_axis is None and i == second_axis:
              axis_slice = slice(0,self._plot_array.shape[second_axis])
              self.array_selector.append(axis_slice)
            else:
              self.array_selector.append(0)
        self.array_tuple = tuple(self.array_selector)
        _dprint(3, 'array_selector tuple ', self.array_tuple)
        self._plotter.array_plot(self._plot_array[self.array_tuple],data_label=self.label +' data')
        self.addTupleFlags()
      else:
        if self._plot_array.ndim == 2:
          self._plotter.set_yaxis_title('Sequence Number')
          self._plotter.set_xaxis_title('Array Values')
        if self._plot_array.ndim == 1:
          self._plotter.set_yaxis_title('Values')
          self._plotter.set_xaxis_title('Sequence Number')
        self._plotter.array_plot(self._plot_array, data_label=self.label+ ' data')
        if not self._flag_plot_array is None and self._flag_plot_array.max() > 0:
          self._plotter.setFlagsData(self._flag_plot_array)
          self._plotter.handleFlagToggle(False)
          self._plotter.handleFlagRange()
        else:
          self._plotter.handleFlagToggle(True)
          self._plotter.handleFlagRange()

    else:
      Message = "MeqHistoryCollect node lacks a value field."
      mb = QMessageBox("history_plotter.py",
                     Message,
                     QMessageBox.Warning,
                     QMessageBox.Ok | QMessageBox.Default,
                     QMessageBox.NoButton,
                     QMessageBox.NoButton)
      mb.exec_loop()
      return

  def invalid_array_sequence(self):
      if not self.displayed_invalid:
        Message = "Plot not made: Sequence of Data has Varying Array Dimensions!"
#       mb = QMessageBox("history_plotter.py",
#                    Message,
#                    QMessageBox.Warning,
#                    QMessageBox.Ok | QMessageBox.Default,
#                    QMessageBox.NoButton,
#                    QMessageBox.NoButton)
#       mb.exec_loop()
        cache_message = QLabel(Message,self.wparent())
        cache_message.setTextFormat(Qt.RichText)
        self._wtop = cache_message
        self.set_widgets(cache_message)
        self.reset_plot_stuff()
        self.displayed_invalid = True

  def create_plot_array(self,history_list):
# first try to figure out what we have ...
    _dprint(3, 'history_plotter: incoming list/array is ', history_list)
    plot_array = None
    flag_plot_array = None
    list_length = len(history_list)
    prev_shape = None
    max_dims = []
    for i in range(list_length):
      data_array = history_list[i]
      try:
        shape = data_array.shape
        if not prev_shape is None:
          if len(shape) != len(prev_shape):
            self.invalid_array_sequence()
            return
        else:
          prev_shape = shape
          if len(max_dims) == 0:
            for j in range(len(shape)):
              max_dims.append(shape[j])
          else:
            for j in range(len(shape)):
              if shape[j] > max_dims[j]:
                max_dims[j] = shape[j]
      except:
        if not prev_shape is None:
          self.invalid_array_sequence()
          return
    _dprint(3, 'max dims ', max_dims)
    for i in range(list_length):
      data_array = history_list[i]
      if len(max_dims) == 0:
# we have a sequence of scalars
        if plot_array is None:
          temp_array = numpy.asarray(data_array)
          plot_array = numpy.resize(temp_array,list_length)
        else:
          plot_array[i] = data_array
      else:
# we have a sequence of arrays
        if plot_array is None:
          array_dims = [] 
          array_dims.append(list_length)
          for j in range(len(max_dims)):
            array_dims.append(max_dims[j])
          plot_array = numpy.zeros(array_dims,dtype=data_array.dtype) 
          flag_plot_array = numpy.zeros(array_dims, numpy.int32)
          flag_plot_array = flag_plot_array + 1 
        array_selector = []
        array_selector.append(i)
        for j in range(data_array.ndim):
          axis_slice = slice(0,data_array.shape[j])
          array_selector.append(axis_slice)
        array_tuple = tuple(array_selector)
        plot_array[array_tuple] = data_array
        flag_plot_array[array_tuple] = 0
    _dprint(3,'returned plot array has shape ', plot_array.shape)
    return (plot_array, flag_plot_array)

  def setArraySelector (self,lcd_number, slider_value, display_string):
    self.array_selector[lcd_number] = slider_value
    self.array_tuple = tuple(self.array_selector)
    self._plotter.array_plot(self._plot_array[self.array_tuple],data_label=self.label + ' data ')
    self.addTupleFlags()

  def setSelectedAxes (self,first_axis,second_axis,third_axis=-1):
    self.array_selector = create_array_selector(self._plotter, self._plot_array.ndim, self._plot_array.shape, first_axis,second_axis,third_axis)
    self.array_tuple = tuple(self.array_selector)
    _dprint(3, 'array_selector tuple ', self.array_tuple)
    self._plotter.array_plot(self._plot_array[self.array_tuple],data_label=self.label+ ' data')
    self.addTupleFlags()

  def addTupleFlags(self):
    if not self._flag_plot_array is None and self._flag_plot_array[self.array_tuple].max() > 0:
      self._plotter.setFlagsData(self._flag_plot_array[self.array_tuple])
      self._plotter.handleFlagToggle(False)
      self._plotter.handleFlagRange()
    else:
      self._plotter.handleFlagToggle(True)
      self._plotter.handleFlagRange()

  def create_image_plotters(self):
    _dprint(3,'starting create_image_plotters')
    if self._plotter is None:
      self.layout_parent = QWidget(self.wparent())
      self.layout = QGridLayout(self.layout_parent)
      self._plotter, self.plotPrinter = create_2D_Plotters(self.layout, self.layout_parent, self.ND_plotter)
      QObject.connect(self._plotter, PYSIGNAL('colorbar_needed'), self.set_ColorBar) 
      QObject.connect(self._plotter, PYSIGNAL('do_print'), self.plotPrinter.do_print) 
      self.set_widgets(self.layout_parent,self.dataitem.caption,icon=self.icon())
      self._wtop = self.layout_parent;       
    _dprint(3,'array has rank and shape: ', self._plot_array.ndim, ' ', self._plot_array.shape)
    if self.actual_rank > 2:
      _dprint(3,'array has actual rank and shape: ', self.actual_rank, ' ', self._plot_array.shape)
      _dprint(3,'so an ND Controller GUI is needed')
      self._plotter.set_original_array_rank(self._plot_array.ndim)
      self.set_ND_controls()
  # create_image_plotters


  def set_ND_controls (self, labels=None, parms=None, num_axes=2):
    """ this function adds the extra GUI control buttons etc if we are
        displaying data for a numpy array of dimension 3 or greater """

    _dprint(3, 'plot_array shape ', self._plot_array.shape)
    self.ND_Controls = create_ND_Controls(self.layout, self.layout_parent, self._plot_array.shape, self.ND_Controls, self.ND_plotter, labels, parms, num_axes)
    QObject.connect(self.ND_Controls, PYSIGNAL('sliderValueChanged'), self.setArraySelector)
    QObject.connect(self.ND_Controls, PYSIGNAL('defineSelectedAxes'), self.setSelectedAxes)
    QObject.connect(self._plotter, PYSIGNAL('show_ND_Controller'), self.ND_Controls.showDisplay) 

  def set_ColorBar (self):
    """ this function adds a colorbar for 2-D displays """
    # create two color bars in case we are displaying complex arrays
    self.colorbar = create_ColorBar(self.layout, self.layout_parent, self._plotter, self.plotPrinter)

Grid.Services.registerViewer(dmi_type('MeqResult',record),HistoryPlotter,priority=40)
Grid.Services.registerViewer(meqds.NodeClass('MeqHistoryCollect'),HistoryPlotter,priority=10)

