#!/usr/bin/python

# modules that are imported
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

from qt import *
from numarray import *
from Timba.Plugins.display_image import *
from Timba.Plugins.realvsimag import *
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
        'none': QwtSymbol.None,
        'rectangle': QwtSymbol.Rect,
        'square': QwtSymbol.Rect,
        'ellipse': QwtSymbol.Ellipse,
        'dot': QwtSymbol.Ellipse,
        'circle': QwtSymbol.Ellipse,
	'xcross': QwtSymbol.XCross,
	'cross': QwtSymbol.Cross,
	'triangle': QwtSymbol.Triangle,
	'diamond': QwtSymbol.Diamond,
        }

  line_style_table = {
        'none': QwtCurve.NoCurve,
        'lines' : QwtCurve.Lines,
        'dots' : QwtCurve.Dots,
#        'none': Qt.NoPen,
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
    self._plotter = None
    self.colorbar = None
    self._window_controller = None
    self._plot_type = None
    self.array_selector = None
    self._wtop = None;
    self.label = '';
    self.dataitem = dataitem
    self._attributes_checked = False
    self.first_spectrum_plot = True
    self.displayed_invalid = False
    self.layout_parent = None
    self.layout = None
    self.ND_Controls = None
    _dprint(3, 'at end of init: self._plotter = ', self._plotter)

# back to 'real' work
    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

  def __del__(self):
    if self._window_controller:
      self._window_controller.closeAllWindows()
                                                                                           
# function needed by Oleg for reasons known only to him!
  def wtop (self):
    return self._wtop;

  def display_history_data (self):
    """ extract 'value' data from incoming history data record and
      create a plotter object to plot the data 
    """
    _dprint(3, ' ')
#   _dprint(3, 'analyzing incoming record ', self._rec.history)
#   _dprint(3, 'analyzing incoming record keys', self._rec.history.keys())
    if self._rec.history.has_key('value'):
      self._plot_array = self.create_plot_array(self._rec.history['value'])
      try:
        _dprint(3, 'plot_array rank and shape ', self._plot_array.rank, ' ', self._plot_array.shape)
      except: pass;
      if self._plot_array is None:
        return
      if self._plotter is None:
        self.create_image_plotters()
      else:
        if self._plot_array.rank > 2:
         self.array_selector = None
         self.ND_Controls = None
         self.set_ND_controls()

      if self._plot_array.rank >= 2:
        self.set_data_range(self._plot_array)
      if self._plot_array.rank > 2:
        if self.array_selector is None:
          second_axis = None
          first_axis = None
          for i in range(self._plot_array.rank-1,-1,-1):
            if self._plot_array.shape[i] > 1:
              if second_axis is None:
                second_axis = i
              else:
                if first_axis is None:
                  first_axis = i
          if not first_axis is None and not second_axis is None:
            self.array_selector = []
            for i in range(self._plot_array.rank):
              if i == first_axis:
                axis_slice = slice(0,self._plot_array.shape[first_axis])
                self.array_selector.append(axis_slice)
              elif i == second_axis:
                axis_slice = slice(0,self._plot_array.shape[second_axis])
                self.array_selector.append(axis_slice)
              else:
                self.array_selector.append(0)
        self.array_tuple = tuple(self.array_selector)
        self._plotter.array_plot(self.label +'data', self._plot_array[self.array_tuple])
      else:
        self._plotter.array_plot(self.label+ 'data', self._plot_array)

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
        Message = "Invalid Sequence of Data - Inconsistent Array Lengths!"
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
        self.displayed_invalid = True

  def create_plot_array(self,history_list):
# first try to figure out what we have ...
#     print 'incoming list is ', history_list
      plot_array = None
      list_length = len(history_list)
      for i in range(list_length):
        data_array = history_list[i]
        _dprint(3, 'iteration ', i, 'data_array ', data_array)
        shape = None
        try:
          shape = data_array.shape
          _dprint(3, 'this array has shape ', shape)
      
        except:
          _dprint(3, 'shape function call fails here' )
          try:
            shape = data_array[0].shape
            _dprint(3, 'array has shape ', shape)
# we have a scalar - expand the scalar to fill the plot array
          except:
            _dprint(3, 'I think I have a scalar')
            if plot_array is None:
              temp_array = asarray(data_array)
              plot_array = resize(temp_array,list_length)
            try:
              plot_array[i] = data_array[0]
            except:
              self.invalid_array_sequence()
              return
            continue
        if len(shape) == 1:
          if shape[0] == 1:
            _dprint(3, 'I think I have a scalar')
 # again, we essentially have a scalar
            if plot_array is None:
              temp_array = asarray(data_array)
              plot_array = resize(temp_array,list_length)
            try:
              plot_array[i] = data_array[0]
            except:
              self.invalid_array_sequence()
              return
            continue
          else:
# we can assume we have a conformant array along the first axis (I think)
            _dprint(3, 'we should be here ')
            if plot_array is None:
              temp_array = asarray(data_array)
              dimensions = (list_length, shape[0])
              plot_array = resize(temp_array,dimensions)
            try:
              for j in range(shape[0]):
                plot_array[i,j] = data_array[j]
            except:
              self.invalid_array_sequence()
              return
            continue
# otherwise we had a 2-D or greater shape
        else:
          _dprint(3, '*** we should be here ')
          _dprint(3, 'array has shape ', shape)
          if len(shape) == 2 and shape[0] == 1 and shape[1] == 1:
            _dprint(3, '**** we should be here ')
# we essentially have a scalar yet again
            if plot_array is None:
              temp_array = asarray(data_array)
              plot_array = resize(temp_array,list_length)
            try:
              plot_array[i] = data_array[0,0]
            except:
              self.invalid_array_sequence()
              return
            continue
# we need to expand the data to fill the vells dimension
# easy if fastest changing index == shape of vector which will
# be replicated
          if len(shape) == 2 and shape[0] == 1 and shape[1]  > 1:
            _dprint(3, '***** we should be here ')
            if plot_array is None:
	      dimensions = (list_length, shape[1])
              _dprint(3, '**** dimensions are ', dimensions)
              temp_array = asarray(data_array[0][0])
              plot_array = resize(temp_array,dimensions)
            try:
              for j in range(shape[1]):
                plot_array[i,j] = history_list[i][0][j]
            except:
              self.invalid_array_sequence()
              return
            continue
          if len(shape) == 2 and shape[0] > 1 and shape[1] == 1:
            if plot_array is None:
	      dimensions = (list_length, shape[0])
              plot_array = resize(data_array,dimensions)
            _dprint(3, 'array is ', history_list[i])
            try:
              for j in range(shape[0]):
                plot_array[i,j] = data_array[j][0]
            except:
              self.invalid_array_sequence()
              return
            continue
          else:
# otherwise
            _dprint(3, '****** we should be here at last possibility ')
            if plot_array is None:
              new_shape = []
              new_shape.append(list_length)
              for i in range(len(shape)):
                new_shape.append(shape[i])
              dimensions = tuple(new_shape)
              temp_array = asarray(data_array[0,0])
              plot_array = resize(temp_array,dimensions)
              _dprint(3, '****** plot_array has shape ', plot_array.shape)
              _dprint(3, '****** data_array has shape ', data_array.shape)
            try:
              if list_length > 1:
                plot_array[i] = data_array
              else:
                plot_array = None
                plot_array = data_array
            except:
              self.invalid_array_sequence()
              return
            continue
      return plot_array

  def setArraySelector (self,lcd_number, slider_value, display_string):
    self.array_selector[lcd_number] = slider_value
    self.array_tuple = tuple(self.array_selector)
    self._plotter.array_plot(self.label + 'data ', self._plot_array[self.array_tuple])

  def setSelectedAxes (self,first_axis, second_axis):
    self.array_selector = []
    for i in range(self._plot_array.rank):
      if i == first_axis: 
        axis_slice = slice(0,self._plot_array.shape[first_axis])
        self.array_selector.append(axis_slice)
      elif i == second_axis:
        axis_slice = slice(0,self._plot_array.shape[second_axis])
        self.array_selector.append(axis_slice)
      else:
        self.array_selector.append(0)
    self.array_tuple = tuple(self.array_selector)
    self._plotter.array_plot(self.label+ 'data', self._plot_array[self.array_tuple])

  def set_data_range(self, data_array):
    """ figure out global minima and maxima of array to be plotted """
# now figure out global min and max of the complete ND array
    if data_array.type() == Complex32 or data_array.type() == Complex64:
      real_array = data_array.getreal()
      imag_array = data_array.getimag()
      real_min = real_array.min()
      real_max = real_array.max()
      imag_min = imag_array.min()
      imag_max = imag_array.max()
      if real_min < imag_min:
        self.data_min = real_min
      else:
        self.data_min = imag_min
      if real_max > imag_max:
        self.data_max = real_max
      else:
        self.data_max = imag_max
    else:
      self.data_min = data_array.min()
      self.data_max = data_array.max()
#   print 'data min and max ', self.data_min, ' ', self.data_max
    if self.colorbar is None:
      self.set_ColorBar(self.data_min,self.data_max)

    self.colorbar.setRange(self.data_min,self.data_max)
    self.colorbar.setMaxRange(self.data_min,self.data_max)
    self._plotter.plotImage.setImageRange((self.data_min,self.data_max))
    self._plotter.reset_color_bar(reset_value = False)

  def create_image_plotters(self):
    _dprint(3,'starting create_image_plotters')
    self.layout_parent = QWidget(self.wparent())
    self.layout = QGridLayout(self.layout_parent)
    self._plotter = QwtImageDisplay('spectra',parent=self.layout_parent)
    _dprint(3,'self._plotter = ', self._plotter)

    self.layout.addWidget(self._plotter, 0, 1)
#   QObject.connect(self._plotter, PYSIGNAL('colorbar_needed'), self.set_ColorBar) 

    self.plotPrinter = plot_printer(self._plotter)
    QObject.connect(self._plotter, PYSIGNAL('do_print'), self.plotPrinter.do_print) 

    self.set_widgets(self.layout_parent,self.dataitem.caption,icon=self.icon())
    self._wtop = self.layout_parent;       
    _dprint(3,'array has rank and shape: ', self._plot_array.rank, ' ', self._plot_array.shape)
    if self._plot_array.rank > 2:
      _dprint(3,'array has rank and shape: ', self._plot_array.rank, ' ', self._plot_array.shape)
      _dprint(3,'so an ND Controller GUI is needed')
      self._plotter.set_toggle_array_rank(self._plot_array.rank)
      self.set_ND_controls()
  # create_image_plotters

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
#   try to put request ID ^Sin label
      try: self.label = "rq " + str(self._rec.cache.request_id);
      except: pass;
      try: self._rec = self._rec.cache.result; # look for cache.result record
      except:
        Message = "No result record was found in the cache, so no plot can be made with the <b>history plotter</b>! You may wish to select another type of display."
        cache_message = QLabel(Message,self.wparent())
        cache_message.setTextFormat(Qt.RichText)
        self._wtop = cache_message
        self.set_widgets(cache_message)
        return

    if self._rec.has_key("history"):
# do plotting of visualization data
      self.display_history_data()
    else:
      Message = "Result record does not contain history key, so no plot can be made with the <b>history plotter</b>! You may wish to select another type of display."
      cache_message = QLabel(Message,self.wparent())
      cache_message.setTextFormat(Qt.RichText)
      self._wtop = cache_message
      self.set_widgets(cache_message)
      return

# enable & highlight the cell
    self.enable();
    self.flash_refresh();

    _dprint(3, 'exiting set_data')

  def set_ND_controls (self):
    """ this function adds the extra GUI control buttons etc if we are
        displaying data for a numarray of dimension 3 or greater """

    labels = None
    parms = None
    _dprint(3, 'plot_array shape ', self._plot_array.shape)
    self.ND_Controls = ND_Controller(self._plot_array.shape, labels, parms, self.layout_parent)
    QObject.connect(self.ND_Controls, PYSIGNAL('sliderValueChanged'), self.setArraySelector)
    QObject.connect(self.ND_Controls, PYSIGNAL('defineSelectedAxes'), self.setSelectedAxes)
    QObject.connect(self._plotter, PYSIGNAL('show_ND_Controller'), self.ND_Controls.showDisplay) 
    QObject.connect(self._plotter, PYSIGNAL('reset_axes_labels'), self.ND_Controls.redefineAxes) 
    self.layout.addMultiCellWidget(self.ND_Controls,2,2,0,1)
    self.ND_Controls.show()

  def set_ColorBar (self, min, max):
    """ this function adds a colorbar for 2 Ddisplays """
    _dprint(3,' set_ColorBar parms = ', min, ' ', max)
    self.colorbar =  QwtColorBar(parent=self.layout_parent)
    self.colorbar.setRange(min, max)
    self.layout.addWidget(self.colorbar, 0, 0)
#   QObject.connect(self._plotter, PYSIGNAL('image_range'), self.colorbar.setRange) 
#   QObject.connect(self._plotter, PYSIGNAL('max_image_range'), self.colorbar.setMaxRange) 
    QObject.connect(self._plotter, PYSIGNAL('display_type'), self.colorbar.setDisplayType) 
    QObject.connect(self._plotter, PYSIGNAL('show_colorbar_display'), self.colorbar.showDisplay) 
    QObject.connect(self.colorbar, PYSIGNAL('set_image_range'), self._plotter.setImageRange) 
    self.plotPrinter.add_colorbar(self.colorbar)
    self.colorbar.show()

Grid.Services.registerViewer(dmi_type('MeqResult',record),HistoryPlotter,priority=40)
Grid.Services.registerViewer(meqds.NodeClass('MeqHistoryCollect'),HistoryPlotter,priority=10)

