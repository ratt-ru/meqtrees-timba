#!/usr/bin/env python

# Contributed by Tomaz Curk in a bug report showing that the stack order of the
# curves was dependent on the number of curves. This has been fixed in Qwt.
#
# QwtBarCurve is an idea of Tomaz Curk.
#
# Beautified and expanded by Gerard Vermeulen.

import math
import random
import sys
from qt import *
from qwt import *
from numarray import *
from app_pixmaps import pixmaps

from math import sin
from math import cos
from math import pow
from math import sqrt

# local python Error Bar class
from ErrorBar import *

from dmitypes import verbosity
_dbg = verbosity(0,name='realvsimag');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class PrintFilter(QwtPlotPrintFilter):
    def __init__(self):
        QwtPlotPrintFilter.__init__(self)

    # __init___()
    
    def color(self, c, item, i):
        if not (self.options() & QwtPlotPrintFilter.PrintCanvasBackground):
            if item == QwtPlotPrintFilter.MajorGrid:
                return Qt.darkGray
            elif item == QwtPlotPrintFilter.MinorGrid:
                return Qt.gray
        if item == QwtPlotPrintFilter.Title:
            return Qt.red
        elif item == QwtPlotPrintFilter.AxisScale:
            return Qt.green
        elif item == QwtPlotPrintFilter.AxisTitle:
            return Qt.blue
        return c

    # color()

    def font(self, f, item, i):
        result = QFont(f)
        result.setPointSize(int(f.pointSize()*1.25))
        return result

    # font()

# class PrintFilter

class realvsimag_plotter(object):

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
        }

    symbol_table = {
        'none': QwtSymbol.None,
        'rectangle': QwtSymbol.Rect,
        'ellipse': QwtSymbol.Ellipse,
        'circle': QwtSymbol.Ellipse,
	'xcross': QwtSymbol.XCross,
	'cross': QwtSymbol.Cross,
	'triangle': QwtSymbol.Triangle,
	'diamond': QwtSymbol.Diamond,
        }
    
    def __init__(self, plot_key=None, parent=None):
        # QWidget.__init__(self, parent)

        self.plot_key = plot_key

        # Initialize a QwPlot central widget
        self.plot = QwtPlot('', parent)
        self.plot.plotLayout().setCanvasMargin(0)
        self.plot.plotLayout().setAlignCanvasToScales(True)
        
        self._mainwin = parent and parent.topLevelWidget();
        # get status bar
        self._statusbar = self._mainwin and self._mainwin.statusBar();

        self.__initTracking()
        self.__initZooming()
        # forget the toolbar for now -- too much trouble when we're dealing with 
        # multiple windows. Do a context menu instead
        # self.__initToolBar()
        self.__initContextMenu()

        # initialize internal variables for plot
        self._circle_dict = {}
        self._line_dict = {}
        self._xy_plot_dict = {}
        self.plot_circles = False
        self._angle = 0.0
        self._radius = 20.0
        self._x_min = 0.0;
        self._x_max = 0.0;
        self._y_min = 0.0;
        self._y_max = 0.0;

        self.plot.setAxisTitle(QwtPlot.xBottom, 'Real Axis')
        self.plot.setAxisTitle(QwtPlot.yLeft, 'Imaginary Axis')
        self._plot_title = None
        self.index = -1

# used for plotting MeqParm solutions
        self.x_list = []
        self.y_list = []
        self.x_data = None
        self.y_data = None
        self.value = 100

# used for errors plotting 
        self.errors_plot = False
# used for errors plot testing 
        self.gain = 1.0

    # __init__()

    def set_compute_circles (self, do_compute_circles=True):
        self.plot_circles = do_compute_circles


    def __initTracking(self):
        """Initialize tracking
        """        
        QObject.connect(self.plot,
                     SIGNAL('plotMouseMoved(const QMouseEvent&)'),
                     self.onMouseMoved)
        QObject.connect(self.plot, SIGNAL("plotMousePressed(const QMouseEvent&)"),
                        self.slotMousePressed)

        self.plot.canvas().setMouseTracking(True)
        if self._statusbar:
          self._statusbar.message(
            'Plot cursor movements are tracked in the status bar',2000)

    # __initTracking()

    def onMouseMoved(self, e):
        if self._statusbar:
          self._statusbar.message(
            'x = %+.6g, y = %.6g'
            % (self.plot.invTransform(QwtPlot.xBottom, e.pos().x()),
               self.plot.invTransform(QwtPlot.yLeft, e.pos().y())),2000)

    # onMouseMoved()
    
    def __initZooming(self):
        """Initialize zooming
        """
        self.zoomer = QwtPlotZoomer(QwtPlot.xBottom,
                                    QwtPlot.yLeft,
                                    QwtPicker.DragSelection,
                                    QwtPicker.AlwaysOff,
                                    self.plot.canvas())
        self.zoomer.setRubberBandPen(QPen(Qt.black))

        self.picker = QwtPlotPicker(
            QwtPlot.xBottom,
            QwtPlot.yLeft,
            QwtPicker.PointSelection | QwtPicker.DragSelection,
            QwtPlotPicker.CrossRubberBand,
            QwtPicker.AlwaysOn,
            self.plot.canvas())
        self.picker.setRubberBandPen(QPen(Qt.green))
        QObject.connect(self.picker, SIGNAL('selected(const QPointArray &)'),
                     self.selected)



    # __initZooming()
       
    def setZoomerMousePattern(self, index):
        """Set the mouse zoomer pattern.
        """
        if index == 0:
            pattern = [
                QwtEventPattern.MousePattern(Qt.LeftButton, Qt.NoButton),
                QwtEventPattern.MousePattern(Qt.RightButton, Qt.NoButton),
#                QwtEventPattern.MousePattern(Qt.MidButton, Qt.NoButton),
                QwtEventPattern.MousePattern(Qt.LeftButton, Qt.ShiftButton),
                QwtEventPattern.MousePattern(Qt.RightButton, Qt.ShiftButton),
#                QwtEventPattern.MousePattern(Qt.MidButton, Qt.ShiftButton),
                ]
            self.zoomer.setMousePattern(pattern)
        elif index in (1, 2, 3):
            self.zoomer.initMousePattern(index)
        else:
            raise ValueError, 'index must be in (0, 1, 2, 3)'

    # setZoomerMousePattern()
    def __initContextMenu(self):
        """Initialize the toolbar
        """
        # skip if no main window
        if not self._mainwin:
          return;
          
        self._menu = QPopupMenu(self._mainwin);
        
        zoom = QAction(self.plot);
        zoom.setIconSet(pixmaps.viewmag.iconset());
        zoom.setText("Enable zoomer");
        zoom.setToggleAction(True);
        # zoom.setAccel() can set keyboard accelerator
        QObject.connect(zoom,SIGNAL("toggled(bool)"),self.zoom);
        zoom.addTo(self._menu);
        
        printer = QAction(self.plot);
        printer.setIconSet(pixmaps.fileprint.iconset());
        printer.setText("Print plot");
        QObject.connect(printer,SIGNAL("activated()"),self.printPlot);
        printer.addTo(self._menu);
        
        self.zoom(False);
        self.setZoomerMousePattern(0);

##    def __initToolBar(self):
##        """Initialize the toolbar
##        """
##        # skip if no main window
##        if not self._mainwin:
##          return;
##        if not self.toolBar:
##          self.toolBar = QToolBar(self._mainwin);
##
##          self.__class__.btnZoom = btnZoom = QToolButton(self.toolBar)
##          btnZoom.setTextLabel("Zoom")
##          btnZoom.setPixmap(QPixmap(zoom_xpm))
##          btnZoom.setToggleButton(True)
##          btnZoom.setUsesTextLabel(True)
##
##          self.__class__.btnPrint = btnPrint = QToolButton(self.toolBar)
##          btnPrint.setTextLabel("Print")
##          btnPrint.setPixmap(QPixmap(print_xpm))
##          btnPrint.setUsesTextLabel(True)
##
##          QWhatsThis.whatsThisButton(self.toolBar)
##
##          QWhatsThis.add(
##              self.plot.canvas(),
##              'A QwtPlotZoomer lets you zoom infinitely deep\n'
##              'by saving the zoom states on a stack.\n\n'
##              'You can:\n'
##              '- select a zoom region\n'
##              '- unzoom all\n'
##              '- walk down the stack\n'
##              '- walk up the stack.\n\n'
##              )
##        
##        self.zoom(False)
##
##        self.setZoomerMousePattern(0)
##
##        QObject.connect(self.btnPrint, SIGNAL('clicked()'),
##                     self.printPlot)
##        QObject.connect(self.btnZoom, SIGNAL('toggled(bool)'),
##                     self.zoom)

    # __initToolBar()

    def slotMousePressed(self, e):
        "Mouse press processing instructions go here"
        _dprint(2,' in slotMousePressed');
        _dprint(3,' slotMousePressed event:',e);
        if e.button() == QMouseEvent.MidButton:
            _dprint(2,'button is mid button');
            xPos = e.pos().x()
            yPos = e.pos().y()
            _dprint(2,'xPos yPos ', xPos, ' ', yPos);
            key, distance, xVal, yVal, index = self.plot.closestCurve(xPos, yPos)
            _dprint(2,' key, distance, xVal, yVal, index ', key, ' ', distance,' ', xVal, ' ', yVal, ' ', index);
            message = 'point belongs to curve ' + str(key) + ' at sequence ' + str(index) 
            if self._statusbar:
              self._statusbar.message(message,2000)
        elif e.button() == QMouseEvent.RightButton:
          e.accept();  # accept even so that parent widget won't get it
          # popup the menu
          self._menu.popup(e.globalPos());
            
    # slotMousePressed


# compute points for two circles
    def compute_circles (self, item_label, avg_r, avg_i):
      """ compute values for circle running through specified
          point and a line pointing to the point """

      # compute circle that will run through average value
      x_sq = pow(avg_r, 2)
      y_sq = pow(avg_i, 2)
      radius = sqrt(x_sq + y_sq)
      x_pos = zeros((73,),Float64)
      y_pos = zeros((73,),Float64)
      angle = -5.0
      for j in range(0, 73 ) :
        angle = angle + 5.0
        x_pos[j] = radius * cos(angle/57.2957795)
        y_pos[j] = radius * sin(angle/57.2957795)
      x_pos_min  = x_pos.min()
      x_pos_max  = x_pos.max()
      y_pos_min  = y_pos.min()
      y_pos_max  = y_pos.max()

      self._x_min = min(self._x_min, x_pos_min)
      self._x_max = max(self._x_max, x_pos_max)
      self._y_min = min(self._y_min, y_pos_min)
      self._y_max = max(self._y_max, y_pos_max)

      # compute line that will go from centre of circle to 
      # position of average value
      x1_pos = zeros((2,),Float64)
      y1_pos = zeros((2,),Float64)
      x1_pos[0] = 0.0
      y1_pos[0] = 0.0
      x1_pos[1] = avg_r
      y1_pos[1] = avg_i

      # if this is a new item_label, add a new circle,
      # otherwise, replace old one
      circle_key = item_label + '_circle'
      line_key = item_label + '_line'
      if self._circle_dict.has_key(circle_key) == False: 
        key_circle = self.plot.insertCurve(circle_key)
        self._circle_dict[circle_key] = key_circle
        self.plot.setCurvePen(key_circle, QPen(self._plot_color))
        self.plot.setCurveData(key_circle, x_pos, y_pos)
        key_line = self.plot.insertCurve(line_key)
        self._line_dict[line_key] = key_line
        self.plot.setCurvePen(key_line, QPen(self._plot_color))
        self.plot.setCurveData(key_line, x1_pos, y1_pos)
      else:
        key_circle = self._circle_dict[circle_key] 
        key_line = self._line_dict[line_key]
        self.plot.setCurveData(key_circle, x_pos, y_pos)
        self.plot.setCurveData(key_line, x1_pos, y1_pos)

    def plot_data(self, item_label, visu_record):
      """ process incoming data and attributes into the
          appropriate type of plot """
      _dprint(2,'****** in plot_data');

# first find out what kind of plot we are making
      plot_types = None
      if visu_record.has_key('attrib'):
        self._attrib_parms = visu_record['attrib']
        _dprint(2,'self._attrib_parms ', self._attrib_parms);
        self.data_type = self._attrib_parms.get('data_type','')
        plot_types = self._attrib_parms.get('plot_type')

# convert to a tuple if necessary
        if isinstance(plot_types, str):
          plot_types = (plot_types,)

      if visu_record.has_key('value'):
        self._data_values = visu_record['value']
        _dprint(2,'self._data_values ', self._data_values);

# extract and define labels for this data item
      self._label_r = item_label + "_r"
      self._label_i = item_label + "_i"
      for j in range(len(plot_types)):
        self._plot_type = plot_types[j]
     # now generate  particular plot type
        if  self._plot_type == 'realvsimag':
          self.plot_circles = True
          self.x_vs_y_plot(item_label)
        if  self._plot_type == 'errors':
          self.errors_plot = True
          self.x_vs_y_plot(item_label)
  
    def x_vs_y_plot (self,item_label):
      """ plot real vs imaginary values together with circles
          indicating average values """
 
# get and combine all plot array data together into one array
      num_plot_arrays = len(self._data_values)
      _dprint(2,' num_plot_arrays ', num_plot_arrays);
      data_r = []
      data_i = []
      sum_r = 0.0
      sum_i = 0.0
      for i in range(0, num_plot_arrays):
# make sure we are using a numarray
        array_representation = inputarray(self._data_values[i])
        xx_r = None
        xx_i = None
        if array_representation.type() == Complex64:
          xx_r = array_representation.getreal()
          xx_i = array_representation.getimag()
        else:
          xx_r = array_representation
        array_dim = len(xx_r.shape)
        num_elements = 1
        for j in range(0, array_dim):
          num_elements = num_elements * xx_r.shape[j]
        flattened_array_r = reshape(xx_r,(num_elements,))
        self._x_min = min(self._x_min, flattened_array_r.min())
        self._x_max = max(self._x_max, flattened_array_r.max())
       
        for j in range(0, num_elements): 
# note - remove following test in final production system and get rid of
# abs stuff
          if self.data_type.find('err') >= 0:
            data_r.append(abs(flattened_array_r[j]))
          else:
            data_r.append(flattened_array_r[j])
          sum_r = sum_r + flattened_array_r[j]
        if xx_i != None:
          flattened_array_i = reshape(xx_i,(num_elements,))
          self._y_min = min(self._y_min, flattened_array_i.min())
          self._y_max = max(self._y_max, flattened_array_i.max())
          for j in range(0, num_elements): 
            if self.data_type.find('err') >= 0:
              data_i.append(abs(flattened_array_i[j]))
              self.imag_error = True
            else:
              data_i.append(flattened_array_i[j])
              self.imag_error = False
            sum_i = sum_i + flattened_array_i[j]
        else:
          for j in range(0, num_elements): 
            data_i.append(0.0)
          sum_i = 0.0

# add data to set of curves
      num_rows = len(data_r)
      if num_rows == 0:
        print 'nothing to update!'
        return
      if self.errors_plot:
# if we have actual data, need to save it
        if self.data_type.find('err') < 0:
          self.x_data = data_r
          self.y_data = data_i
        
      # if this is a new item_label, add a new plot,
      # otherwise, replace old one
      plot_key = self._attrib_parms.get('label','') + '_plot'
#      plot_key = item_label + '_plot'
      if self._xy_plot_dict.has_key(plot_key) == False: 
        string_color = self._attrib_parms.get('color', 'blue')
        self._plot_color = self.color_table[string_color]
        if self._plot_title is None:
          self._plot_title = self._plot_type +':'
        self._plot_title = self._plot_title + ' ' + self._attrib_parms.get('label','')
        self._plot_title = self._plot_title + ' ' + string_color
        self.plot.setTitle(self._plot_title)

# if we have x, y data
        if self.data_type.find('err') < 0:
          key_plot = self.plot.insertCurve(plot_key)
          self._xy_plot_dict[plot_key] = key_plot
          self.plot.setCurvePen(key_plot, QPen(self._plot_color))
          self.plot.setCurveData(key_plot, data_r, data_i)
          self.plot.setCurveStyle(key_plot, QwtCurve.Dots)
          plot_curve = self.plot.curve(key_plot)
          plot_symbol = self.symbol_table["circle"]
          plot_curve.setSymbol(QwtSymbol(plot_symbol, QBrush(self._plot_color),
                     QPen(self._plot_color), QSize(10, 10)))

# do we have error data
        if self.data_type.find('err') >= 0:
          self.x_errors = QwtErrorPlotCurve(self.plot,self._plot_color,2);
# add in positions of data to the error curve
          if not self.x_data is None:
            self.x_errors.setData(self.x_data,self.y_data);
          else:
            print 'no data to accompany errors so nothing to plot!'
            return
# add in x errors to the error curve
          self.x_errors.setXErrors(True)
          self.x_errors.setErrors(data_r);
          key_plot = self.plot.insertCurve(self.x_errors);
          self._xy_plot_dict[plot_key] = key_plot
          if self.imag_error:
# add in y errors to the error curve
            self.y_errors = QwtErrorPlotCurve(self.plot,self._plot_color,2);
            if not self.x_data is None:
              self.y_errors.setData(self.x_data,self.y_data);
            else:
              print 'no data to accompany errors so nothing to plot!'
              return
            self.y_errors.setErrors(data_i);
            key_plot = self.plot.insertCurve(self.y_errors);
            self._xy_plot_dict[plot_key] = key_plot
      else:
        if self.data_type.find('err') < 0:
          key_plot = self._xy_plot_dict[plot_key] 
          self.plot.setCurveData(key_plot, data_r, data_i)
        if self.data_type.find('err') >= 0:
          self.x_errors.setData(self.x_data,self.y_data);
          self.x_errors.setErrors(data_r);
          if self.imag_error:
            self.y_errors.setData(self.x_data,self.y_data);
            self.y_errors.setErrors(data_i);

      if self.plot_circles:
        avg_i = sum_i / num_rows
        avg_r = sum_r / num_rows
        self.compute_circles (plot_key, avg_r, avg_i)

# at end of x_vs_y_plot function, plot data for a particular node in 
# plot tree has been updated. Replot will be done in calling routine 
# after all nodes in plot tree have been traversed

    # end of x_vs_y_plot 

    def go(self, counter):
      """Create and plot some garbage data
      """
      item_label = 'test'
      xx = self._radius * cos(self._angle/57.2957795)
      yy = self._radius * sin(self._angle/57.2957795)

      x_pos = zeros((20,),Float64)
      y_pos = zeros((20,),Float64)
      for j in range(0,20) :
        x_pos[j] = xx + random.random()
        y_pos[j] = yy + random.random()

# keep track of maxima and minima if we want to zoom
      self._x_min = min(self._x_min, x_pos.min())
      self._x_max = max(self._x_max, x_pos.max())
      self._y_min = min(self._y_min, y_pos.min())
      self._y_max = max(self._y_max, y_pos.max())

      # if this is a new item_label, add a new plot,
      # otherwise, replace old one
      plot_key = item_label + '_plot'
      self._plot_color = self.color_table["red"]
      if self._xy_plot_dict.has_key(plot_key) == False: 
        key_plot = self.plot.insertCurve(plot_key)
        self._xy_plot_dict[plot_key] = key_plot
        self.plot.setCurvePen(key_plot, QPen(self._plot_color))
        self.plot.setCurveData(key_plot, x_pos, y_pos)
        self.plot.setCurveStyle(key_plot, QwtCurve.Dots)
        self.plot.setTitle("Real vs Imaginary Demo")
        plot_curve = self.plot.curve(key_plot)
        plot_symbol = self.symbol_table["circle"]
        plot_curve.setSymbol(QwtSymbol(plot_symbol, QBrush(self._plot_color),
                     QPen(self._plot_color), QSize(10, 10)))
      else:
        key_plot = self._xy_plot_dict[plot_key] 
        self.plot.setCurveData(key_plot, x_pos, y_pos)

      avg_r = x_pos.mean()
      avg_i = y_pos.mean()
      if self.plot_circles:
        self.compute_circles (item_label, avg_r, avg_i)
      if counter == 0:
        self.clearZoomStack()
      else:
        self.plot.replot()

    # go()

    def go_errors(self, counter):
      """Create and plot some garbage error data
      """
      item_label = 'test'
      self._radius = 0.9 * self._radius

      self.gain = 0.95 * self.gain
      num_points = 10
      x_pos = zeros((num_points,),Float64)
      y_pos = zeros((num_points,),Float64)
      x_err = zeros((num_points,),Float64)
      y_err = zeros((num_points,),Float64)
      for j in range(0,num_points) :
        x_pos[j] = self._radius + 3 * random.random()
        y_pos[j] = self._radius + 2 * random.random()
        x_err[j] = self.gain * 3 * random.random()
        y_err[j] = self.gain * 2 * random.random()

# keep track of maxima and minima if we want to zoom
      self._x_min = min(self._x_min, x_pos.min())
      self._x_max = max(self._x_max, x_pos.max())
      self._y_min = min(self._y_min, y_pos.min())
      self._y_max = max(self._y_max, y_pos.max())

      # if this is a new item_label, add a new plot,
      # otherwise, replace old one
      plot_key = item_label + '_plot'
      self._plot_color = self.color_table["red"]
      if self._xy_plot_dict.has_key(plot_key) == False: 
        key_plot = self.plot.insertCurve(plot_key)
        self._xy_plot_dict[plot_key] = key_plot
        self.plot.setCurvePen(key_plot, QPen(self._plot_color))
        self.plot.setCurveData(key_plot, x_pos, y_pos)
        self.plot.setCurveStyle(key_plot, QwtCurve.Dots)
        self.plot.setTitle("Errors Demo")
        plot_curve = self.plot.curve(key_plot)
        plot_symbol = self.symbol_table["circle"]
#        plot_curve.setSymbol(QwtSymbol(plot_symbol, QBrush(self._plot_color),
#                     QPen(self._plot_color), QSize(10, 10)))
        plot_curve.setSymbol(QwtSymbol(
            QwtSymbol.Cross, QBrush(), QPen(Qt.yellow, 2), QSize(7, 7)))


        self.x_errors = QwtErrorPlotCurve(self.plot,Qt.blue,2);
# add in positions of data to the error curve
        self.x_errors.setData(x_pos,y_pos);
# add in errors to the error curve
        self.x_errors.setXErrors(True)
        self.x_errors.setErrors(x_err);
        self.plot.insertCurve(self.x_errors);
        self.y_errors = QwtErrorPlotCurve(self.plot,Qt.blue,2);
        self.y_errors.setData(x_pos,y_pos);
        self.y_errors.setErrors(y_err);
        self.plot.insertCurve(self.y_errors);
      else:
        key_plot = self._xy_plot_dict[plot_key] 
        self.plot.setCurveData(key_plot, x_pos, y_pos)

        self.x_errors.setData(x_pos,y_pos);
        self.x_errors.setErrors(x_err);
        self.y_errors.setData(x_pos,y_pos);
        self.y_errors.setErrors(y_err);

      if counter == 0:
        self.clearZoomStack()
      else:
        self.plot.replot()
    # go_errors()

    def clearZoomStack(self):
        """Auto scale and clear the zoom stack
        """
        self.plot.replot()
        self.zoomer.setZoomBase()
    # clearZoomStack()

    def start_timer(self, time):
        timer = QTimer(self.plot)
        timer.connect(timer, SIGNAL('timeout()'), self.timerEvent)
        timer.start(time)

    # start_timer()

    def timerEvent(self):
      self._angle = self._angle + 5;
      self._radius = 5.0 + 2.0 * random.random()
      self.index = self.index + 1
#      self.go(self.index)
# for testing error plotting
      self.go_errors(self.index)
    # timerEvent()

    def zoom(self,on):
        self.zoomer.setEnabled(on)
        self.zoomer.zoom(0)
        if on:
          self.picker.setRubberBand(QwtPicker.NoRubberBand)
# set fixed scales - zooming doesn't work well with autoscaling!!
          _dprint(2,'setting x fixed scale: ', self._x_min, ' ', self._x_max);
          _dprint(2,'setting y fixed scale: ', self._y_min, ' ', self._y_max);
          x_diff = (self._x_max - self._x_min) / 10.0
          x_max = self._x_max + x_diff
          x_min = self._x_min - x_diff
          y_diff = (self._y_max - self._y_min) / 10.0
          y_max = self._y_max + y_diff
          y_min = self._y_min - y_diff
          
          self.plot.setAxisScale(QwtPlot.xBottom, x_min, x_max)
          self.plot.setAxisScale(QwtPlot.yLeft, y_min, y_max)
          self.clearZoomStack()
        else:
          self.picker.setRubberBand(QwtPicker.CrossRubberBand)
          self.plot.setAxisAutoScale(QwtPlot.xBottom)
          self.plot.setAxisAutoScale(QwtPlot.yLeft)
          self.plot.replot()
    # zoom()


    def printPlot(self):
        try:
            printer = QPrinter(QPrinter.HighResolution)
        except AttributeError:
            printer = QPrinter()
        printer.setOrientation(QPrinter.Landscape)
        printer.setColorMode(QPrinter.Color)
        printer.setOutputToFile(True)
        printer.setOutputFileName('plot-%s.ps' % qVersion())
        if printer.setup():
            filter = PrintFilter()
            if (QPrinter.GrayScale == printer.colorMode()):
                filter.setOptions(QwtPlotPrintFilter.PrintAll
                                  & ~QwtPlotPrintFilter.PrintCanvasBackground)
            self.plot.printPlot(printer, filter)
    # printPlot()

    def selected(self, points):
        point = points.point(0)
# this gives the position in pixels!!
        xPos = point[0]
        yPos = point[1]
        _dprint(2,'selected: xPos yPos ', xPos, ' ', yPos);
    # selected()


    
# class realvsimag_plotter


def main(args):
    app = QApplication(args)
    demo = make()
    app.setMainWidget(demo.plot)
    app.exec_loop()

# main()

def make():
    demo = realvsimag_plotter('plot_key')
# for real vs imaginary plot with circles
#    demo.set_compute_circles(True)
    demo.start_timer(1000)
    demo.plot.show()
    return demo

# make()

# Admire!
if __name__ == '__main__':
    main(sys.argv)

