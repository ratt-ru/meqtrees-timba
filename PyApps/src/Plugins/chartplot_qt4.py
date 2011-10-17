# -*- coding: utf-8 -*-
##!/usr/bin/env python
# -*- coding: utf-8 -*-

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

# This is a python translation of the ACSIS chartplt.cc code

import sys

from Timba.GUI.pixmaps import pixmaps
from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt

from QwtSpy_qt4 import *
import numpy

import zoomwin_qt4
import plot_printer_qt4
import printfilter_qt4
import random

class ChartPlot(Qt.QWidget):
  def __init__(self,control_menu,num_curves=None,parent=None,name=None):
    """ Collects information about timing from setup_parameters dict.
        Resizes and initialises all the variables.  
        creates bottom frame and the chart plot
        Does all the connections
    """
    Qt.QWidget.__init__(self, parent)

    self.setMouseTracking(True)
    #Constant strings
    self._zoomInfo = "Zoom: Press mouse button and drag"
    self._cursorInfo = "Cursor Pos: Press middle mouse button in plot region"

    self._auto_offset = True
    self._ref_chan= 0
    self._offset = 0
    self._source = None
    self._max_range = -10000
    self._data_label = None
    self.info_marker = None
    self._plot_label = None
    self._complex_marker = None
    self._zoom_png_number = 0
    self.has_nans_infs = False
    
    # menu is a ControlMenu object from DataDisplayMainWindow
    self._menu = control_menu;
    
    # constants for complex coponents
    self.AMP = self._menu.AMP;
    self.PHASE = self._menu.PHASE;
    self.REAL = self._menu.REAL;
    self.IMAG = self._menu.IMAG;
    self._complex_component = self._menu.complex_component;

# create plotter
    self._plotter = Qwt.QwtPlot(self)

# set plotter fonts to same size as in display_image.py code
    self.title_font = Qt.QFont(Qt.QApplication.font());
    fi = Qt.QFontInfo(self.title_font);
    # and scale it down to 70%
    self.title_font.setPointSize(fi.pointSize()*0.7);

    #Create the plot widget
    self._y_title = Qwt.QwtText("Value (Relative Scale)")
    self._y_title.setFont(self.title_font)
    self._x_title = Qwt.QwtText("Time Sequence (Relative Scale)")
    self._x_title.setFont(self.title_font)
    self._plotter.setAxisTitle(Qwt.QwtPlot.yLeft, self._y_title)
    self._plotter.setAxisTitle(Qwt.QwtPlot.xBottom, self._x_title)


    #Set the background color
    self._plotter.setCanvasBackground(Qt.Qt.white)
    
    # we seem to need a layout for PyQt
    self.box1 = Qt.QHBoxLayout(self)
    self.box1.addWidget(self._plotter)

    # set a printer facility
    self.plotPrinter = plot_printer_qt4.plot_printer(self._plotter)

    #Number of curves/beams
    if not num_curves is None:
      self._nbcrv = num_curves
      # make sure _nbcrv is a multiple of four
      nbcrv_bin = 4
      divis = self._nbcrv / nbcrv_bin
      if divis * nbcrv_bin < self._nbcrv:
        divis = divis + 1
        self._nbcrv = divis * nbcrv_bin
    else:
      self._nbcrv = 16

    #Initialization of the size of the arrays to put the curve in
    self._ArraySize = 6
    self._x_displacement = self._ArraySize / 6 
    self.set_x_axis_sizes()

    # this is the label of the vells that is being displayed
    self._data_index = None;
    
    # Initialize all the arrays containing the curve data 
    # code for this?

    self._closezoom = False
    self._mainpause = False
    
    #initialize the mainplot zoom variables
    self._d_zoomActive = self._d_zoom = False
    self._is_vector = False
    self.source_marker = None
	    
    #initialize zoomcount.  Count the number of zoom windows opened
    self._zoomcount = 0

    # set up pop up text
    font = Qt.QFont("Helvetica",10)
    self.white = Qt.QColor(255,255,255)
    self._popup_text = Qt.QLabel(self)
    self._popup_text.setFont(font)
    self._popup_text.setStyleSheet("QWidget { background-color: %s }" % self.white.name())
    self._popup_text.setFrameStyle(Qt.QFrame.Box | Qt.QFrame.Plain)
    # start the text off hidden at 0,0
    self._popup_text.hide()


    # timer to allow redisplay
    self._display_interval_ms = 2000
    self._display_refresh = Qt.QTimer(self)
    self._display_refresh.start(self._display_interval_ms)
    self._refresh_flag = True
    self._complex_component = self.AMP;
    

    self._mainwin = parent and parent.topLevelWidget()

    # connect menu actions
    
    Qt.QObject.connect(self._menu.close_window,Qt.SIGNAL("triggered()"),self.quit);
    
    Qt.QObject.connect(self._menu.reset_zoomer,Qt.SIGNAL("triggered()"),self.reset_zoom);

# the following is commented out until postscript/pdf printing works 
# properly with Qt 4 widgets
#   self._print = menu.addAction("Print",self.plotPrinter.do_print)

    Qt.QObject.connect(self._menu.clear_plot,Qt.SIGNAL("triggered()"),self.clear_plot);

    Qt.QObject.connect(self._menu.close_popups,Qt.SIGNAL("triggered()"),self.closezoomfun)

    Qt.QObject.connect(self._menu.show_flagged_data,Qt.SIGNAL("triggered(bool)"),self.change_flag_parms)

    #***** add Fixed scale vs Offset scale submenu
    Qt.QObject.connect(self._menu.autoscale,Qt.SIGNAL("triggered(bool)"),self.change_scale_type);

    Qt.QObject.connect(self._menu.offset_value,Qt.SIGNAL("triggered()"),self.change_offset_value);
    
    Qt.QObject.connect(self._menu.show_labels,Qt.SIGNAL("triggered(bool)"),self.enable_labels);

    Qt.QObject.connect(self._menu,Qt.SIGNAL("changeComplexComponent"),self.update_complex_selector);
    Qt.QObject.connect(self._menu,Qt.SIGNAL("changeVellsComponent"),self.update_vells_selector);
    
    Qt.QObject.connect(self._menu.save_display,Qt.SIGNAL("triggered()"),self.save_display)


    self.spy = Spy(self._plotter.canvas())
    self.prev_xpos = None
    self.prev_ypos = None
    self.xzoom_loc = None
    self.yzoom_loc = None
    self.zoomStack = []
    self.zoom_outline = Qwt.QwtPlotCurve()


    ########### Connections for Signals ############
    self.connect(self.spy, Qt.SIGNAL("MouseMove"), self.plotMouseMoved)
    self.connect(self.spy, Qt.SIGNAL("MousePress"), self.plotMousePressed)
    self.connect(self.spy, Qt.SIGNAL("MouseRelease"), self.plotMouseReleased)

#   self.connect(self._menu,Qt.SIGNAL("activated(int)"),self.emit_menu_signal);
#   self.connect(self._complex_submenu,Qt.SIGNAL("activated(int)"),self.emit_complex_selector);

    # redisplay
    self.connect(self._display_refresh, Qt.SIGNAL("timeout()"), self.refresh_event)

    # construct plot / array storage structures etc
    self.createplot(True)
    
  def setSource(self, source_string):
    self._source = source_string

  def set_x_axis_sizes(self):
    """ changes sizes and values of arrays used to store x-axis 
        values for plot
    """
    self._x1 = numpy.zeros((self._ArraySize,), numpy.float32)
    self._x2 = numpy.zeros((self._ArraySize,), numpy.float32)
    self._x3 = numpy.zeros((self._ArraySize,), numpy.float32)
    self._x4 = numpy.zeros((self._ArraySize,), numpy.float32)

    # layout parameter for x_axis offsets 
    if self._ArraySize > 6 * self._x_displacement:
      self._x_displacement = self._ArraySize / 6
    for i in range(self._ArraySize):
      self._x1[i] = float(i)
      self._x2[i] = self._ArraySize + self._x_displacement +i
      self._x3[i] = 2 * (self._ArraySize + self._x_displacement) + i
      self._x4[i] = 3 * (self._ArraySize + self._x_displacement) + i

  def save_display (self):
    self.emit(Qt.SIGNAL("save_display"),self._data_label)

  def closestCurve(self, pos):
        """ from Gerard Vermeulen's EventFilterDemo.py example """
        found, distance, point, index = None, 1e100, -1, -1
        counter = -1
        for curve in self._plotter.itemList():
            try:
              if isinstance(curve, Qwt.QwtPlotCurve):
                counter = counter + 1
                i, d = curve.closestPoint(pos)
                if i >= 0 and d < distance:
                  index = counter 
                  found = curve
                  point = i
                  distance = d
            except:
              pass

        if found is None:
          return (None, None, None)
        else:
          x = found.x(point)
          y = found.y(point)
          #print 'closest curve is ', index, ' ', x, ' ', y
          return (index, x, y, point)
    # closestCurve

  def refresh_plot (self):
    """ causes entire plot to be redone -- called from methods that change the plotted data""";
    self._auto_offset = True
    self._offset = 0
    self._max_range = -10000
    for channel in range(self._nbcrv):
      self._updated_data[channel] = True
    self.reset_zoom()
    self._refresh_flag = True
    self.refresh_event()


  def update_complex_selector (self,label):
    """ callback to handle events from the complex data selection
        sub-context menu 
    """
    self._complex_component = label;
    self._y_title.setText("%s (Relative Scale)"%label);
    self._plotter.setAxisTitle(Qwt.QwtPlot.yLeft, self._y_title)
    for channel in range(self._nbcrv):
      self._start_offset_test[channel][self._data_index] = 0
    self.refresh_plot();
    return True

  def update_vells_selector (self,label):
    self._data_index = label;
    for channel in range(self._nbcrv):
      self._crv_key[channel].detach()
    self.refresh_plot();

  def change_scale_type (self,autoscale):
    # click means change to fixed scale
    if autoscale:
      self._plotter.setAxisAutoScale(Qwt.QwtPlot.yLeft)
    else: 
      # find current data min and max
      scale_max = self._spec_grid_offset.max()
      scale_min = self._spec_grid_offset.min()

      scale_diff = scale_max - scale_min
      scale_max = scale_max + 0.2 * scale_diff
      scale_min = scale_min - 0.2 * scale_diff 

      AxisParms = ScaleSelector(scale_max, scale_min, self)
      self.connect(AxisParms, Qt.SIGNAL("scale_values"), self.set_scale_values)
      self.connect(AxisParms, Qt.SIGNAL("cancel"), self.cancel_scale_request)

  def change_offset_value (self):
    OffSetParam = OffsetSelector(self)
    self.connect(OffSetParam, Qt.SIGNAL("offset_value"), self.set_offset_value)
    self.connect(OffSetParam, Qt.SIGNAL("cancel_offset"), self.cancel_offset_request)

  def enable_labels (self,enable):
    for channel in range(self._nbcrv):
      self._start_offset_test[channel][self._data_index] = 0
    self.refresh_plot();

  def set_scale_values(self, max_value, min_value):
    if not self._menu.autoscale.isChecked():
      self._plotter.setAxisScale(Qwt.QwtPlot.yLeft, min_value, max_value)
      self._plotter.replot()

  def cancel_scale_request(self):
    self._menu.autoscale.setChecked(False);
    self._plotter.setAxisAutoScale(Qwt.QwtPlot.yLeft)

  def set_offset_value(self, offset_value):
    self._offset = offset_value
    self._refresh_flag = True
    if self._offset < 0.0:
      self._auto_offset = True
      self._offset = 0
      self._max_range = -10000
    else: 
      self._auto_offset = False

  def change_flag_parms (self,*dum):
    self._menu.autoscale.setChecked(True);
    for channel in range(self._nbcrv):
      self._start_offset_test[channel][self._data_index] = 0
    self.refresh_plot();
    
  def reset_zoom (self):
    """ resets data display so all data are visible """
    self._plotter.setAxisAutoScale(Qwt.QwtPlot.yLeft)
    self._plotter.setAxisAutoScale(Qwt.QwtPlot.xBottom)
    self._plotter.replot()
    self._menu.reset_zoomer.setVisible(False)

  def clear_plot(self):
    """ clear the plot of all displayed data """
    # remove any markers
    for i in self._plotter.itemList():
        if isinstance(i, Qwt.QwtPlotMarker):
          i.detach()
    # remove current curves
    for i in self._plotter.itemList():
        if isinstance(i, Qwt.QwtPlotCurve):
          i.detach()
    # undo any zooming
    self.reset_zoom()
#   self._plotter.replot()
    self._ArraySize = 6
    self._x_displacement = self._ArraySize / 6 
    self.set_x_axis_sizes()
    self.createplot()

  def setDataLabel(self, data_label):
    self._data_label = data_label
#    title = self._data_label + " " + self._x_title.text()
#    self._x_title.setText(title)
    self._plotter.setAxisTitle(Qwt.QwtPlot.xBottom, self._x_title)

  def setPlotLabel(self, plot_label):
    self._plot_label = plot_label

  def destruct_chartplot(self):
    """	turn off global mouse tracking """
    QApplication.setGlobalMouseTracking(False)	
    QWidget.setMouseTracking(False) 
			
  def createplot(self,first_time=False):
    """ Sets all the desired parameters for the chart plot """
    if first_time:
      self._chart_data = {}
      self._flag_data = {}
      self._start_offset_test = {}
      self._updated_data = {}
      self._pause = {}
      self._mrk = {}
      self._position = {}
      self._Zoom = {}
      self._zoom_title = {}
      self._zoom_pen = {}
      self._main_pen = {}
      self._indexzoom = {}
      self._crv_key = {}
      self._source_marker = {}
      for i in range (self._nbcrv):
          self._updated_data[i] = False
          self._indexzoom[i] = False
          self._pause[i] = False
          self._Zoom[i] = None
          self._source_marker[i] = None
          self._mrk[i] = 0
          self._position[i] = ""
          self._zoom_title[i] = "Data for Chart " + str(i)
          self._zoom_pen[i] = Qt.Qt.yellow
          self._main_pen[i] = Qt.Qt.black
    	  self._crv_key[i] = Qwt.QwtPlotCurve("Chart " + str(i))
    	  self._crv_key[i].setPen(Qt.QPen(self._main_pen[i]))
    	  self._crv_key[i].attach(self._plotter)
          
          self._chart_data[i] = {}
          self._flag_data[i] = {}
          self._start_offset_test[i] = {}
    else:
      for i in range (self._nbcrv):
          self._updated_data[i] = False
          self._pause[i] = False
          self._source_marker[i] = None
          self._mrk[i] = 0
          self._position[i] = ""
          self._main_pen[i] = Qt.Qt.black
    	  self._crv_key[i] = Qwt.QwtPlotCurve("Chart " + str(i))
    	  self._crv_key[i].setPen(Qt.QPen(self._main_pen[i]))
    	  self._crv_key[i].attach(self._plotter)
          self._chart_data[i] = {}
          self._flag_data[i] = {}
          self._start_offset_test[i] = {}

  def infoDisplay(self):
    """ Display text under cursor in plot
        Figures out where the cursor is, generates the appropriate text, 
        and puts it on the screen.
    """
    closest_curve, xVal, yVal, data_point = self.closestCurve(self.position_raw)

    #get value of where the mouse was released
    p2x = self._plotter.invTransform(Qwt.QwtPlot.xBottom, self.xpos_raw)

# determine 'actual' x-axis position
    ref_point=0
    if (p2x >= 0) and (p2x < self._ArraySize):
      ref_point = int(p2x)
    elif p2x >= self._ArraySize + self._x_displacement and p2x < (2*self._ArraySize) + self._x_displacement: 
      ref_point = int(p2x - self._ArraySize - self._x_displacement)
    elif p2x >= 2*(self._ArraySize + self._x_displacement) and p2x < (3*self._ArraySize)+(2*self._x_displacement):
      ref_point = int(p2x - (2*(self._ArraySize + self._x_displacement)))
    elif p2x >= 3*(self._ArraySize+self._x_displacement) and p2x < (4*self._ArraySize) + 3*self._x_displacement: 
      ref_point = int(p2x - (3*(self._ArraySize+self._x_displacement)))

    if self._complex_component is self.PHASE:
      temp_off = ((closest_curve) % (self._nbcrv/4) + 0.5 ) * self._offset
    else:
      temp_off = ((closest_curve) % (self._nbcrv/4)) * self._offset
    ref_value = yVal - temp_off

    message = self.reportCoordinates(ref_point, ref_value, closest_curve)
    message = message +', data point: ' + str(data_point)

    self._popup_text.setText(message)
    self._popup_text.adjustSize()
    try:
      yhb = self._plotter.transform(Qwt.QwtPlot.yLeft, self._plotter.axisScaleDiv(Qwt.QwtPlot.yLeft).hBound())
      ylb = self._plotter.transform(Qwt.QwtPlot.yLeft, self._plotter.axisScaleDiv(Qwt.QwtPlot.yLeft).lBound())
      xhb = self._plotter.transform(Qwt.QwtPlot.xBottom, self._plotter.axisScaleDiv(Qwt.QwtPlot.xBottom).hBound())
      xlb = self._plotter.transform(Qwt.QwtPlot.xBottom, self._plotter.axisScaleDiv(Qwt.QwtPlot.xBottom).lBound())
    except:
      yhb = self._plotter.transform(Qwt.QwtPlot.yLeft, self._plotter.axisScaleDiv(Qwt.QwtPlot.yLeft).upperBound())
      ylb = self._plotter.transform(Qwt.QwtPlot.yLeft, self._plotter.axisScaleDiv(Qwt.QwtPlot.yLeft).lowerBound())
      xhb = self._plotter.transform(Qwt.QwtPlot.xBottom, self._plotter.axisScaleDiv(Qwt.QwtPlot.xBottom).upperBound())
      xlb = self._plotter.transform(Qwt.QwtPlot.xBottom, self._plotter.axisScaleDiv(Qwt.QwtPlot.xBottom).lowerBound())
    height = self._popup_text.height()
    if self.ypos + height > ylb:
      ymove = self.ypos - 1.5 * height
    else:
      ymove = self.ypos + 0.5 * height
    width = self._popup_text.width()
    if self.xpos + width > xhb:
      xmove = xhb - width
    else:
      xmove = self.xpos
    self._popup_text.move(xmove, ymove)
    if not self._popup_text.isVisible():
      self._popup_text.show()
    

  def closezoomfun(self):

    """ Set closezoom flag active to close all the zoom windows 
        once the user clicked
        the close_all_zoom button from the warning
        put closezoom to 1 and replot
    """
    self._closezoom = True
    self.ReplotZoom()

# close any zoom pop up windows
  def quit(self):
   for curve_no in range(self._nbcrv):
     if self._indexzoom[curve_no]:  
       if not self._Zoom[curve_no] is None:
         self._Zoom[curve_no].Closing()
   self.close()

  def ReplotZoom(self):
    """ If no zoom window opened, sets the flag back to 0
        Looks in the array to see which zooms are opened
        if the closezoom is set to 1
        Close the zoom
        set the flag in the array to 0
        removes 1 from the number of zoom opened
        else
        replot the zoom
    """

    #If no zoom window opened, sets the flag back to 0
    if self._zoomcount==0:
      self._closezoom = False
      
    #Looks in the array to see which zooms are opened
    for curve_no in range(self._nbcrv):
      if self._indexzoom[curve_no] and not self._Zoom[curve_no] is None:
        if self._closezoom:
          #Close the zoom
          self._Zoom[curve_no].close()
          #set the flag in the array to 0
          self._indexzoom[curve_no] = False
          #removes 1 from the number of zoom opened
          self._zoomcount = self._zoomcount - 1
        elif not self._pause[curve_no]:  #replot the zoom
          chart = numpy.array(self._chart_data[curve_no][self._data_index])
          flags = numpy.array(self._flag_data[curve_no][self._data_index])
          self._Zoom[curve_no].update_plot(chart,flags)
          self._Zoom[curve_no]._plotter.replot()

    if self._closezoom:
      self._menu.close_popups.setVisible(False)

  def plotMouseMoved(self, e):
    position = e.pos()
    if self._popup_text.isVisible():
      self._popup_text.hide()
    self.xpos_raw = position.x()
    self.ypos_raw = position.y()
    self.xpos = self._plotter.invTransform(Qwt.QwtPlot.xBottom, self.xpos_raw)
    self.ypos = self._plotter.invTransform(Qwt.QwtPlot.yLeft, self.ypos_raw)

    self.position_raw = Qt.QPoint(self.xpos_raw,self.ypos_raw)
    if not self.xzoom_loc is None:
      self.xzoom_loc = [self.press_xpos, self.press_xpos,  self.xpos, self.xpos,self.press_xpos]
      self.yzoom_loc = [self.press_ypos, self.ypos,  self.ypos, self.press_ypos,self.press_ypos]
      self.zoom_outline.setData(self.xzoom_loc,self.yzoom_loc)
      self._plotter.replot()

  def mapMouseButtons (self,e):
      """Maps a mouse event to one of three buttons.
      To support victims of Jobs, Shift-LeftClick maps to MidClick, and Ctrl+LeftClick maps to RightClick""";
      if e.button() == Qt.Qt.LeftButton:
        if e.modifiers()&Qt.Qt.ShiftModifier:
          return Qt.Qt.MidButton;
        elif e.modifiers()&Qt.Qt.ControlModifier:
          return Qt.Qt.RightButton;
      return e.button();

  def plotMousePressed(self, e):
      """ callback to handle MousePressed event """
      self._mouse_press = self.mapMouseButtons(e);
      if self._mouse_press == Qt.Qt.LeftButton:
        self.infoDisplay();
        self.press_xpos = self.xpos
        self.press_ypos = self.ypos
        self.press_xpos_raw = e.pos().x()
        self.press_ypos_raw = e.pos().y()
        self.xzoom_loc = [self.press_xpos]
        self.yzoom_loc = [self.press_ypos]
        self.zoom_outline.attach(self._plotter)
        if self.zoomStack == []:
          try:
            self.zoomState = (
              self._plotter.axisScaleDiv(Qwt.QwtPlot.xBottom).lBound(),
              self._plotter.axisScaleDiv(Qwt.QwtPlot.xBottom).hBound(),
              self._plotter.axisScaleDiv(Qwt.QwtPlot.yLeft).lBound(),
              self._plotter.axisScaleDiv(Qwt.QwtPlot.yLeft).hBound(),
              )
          except:
            self.zoomState = (
              self._plotter.axisScaleDiv(Qwt.QwtPlot.xBottom).lowerBound(),
              self._plotter.axisScaleDiv(Qwt.QwtPlot.xBottom).upperBound(),
              self._plotter.axisScaleDiv(Qwt.QwtPlot.yLeft).lowerBound(),
              self._plotter.axisScaleDiv(Qwt.QwtPlot.yLeft).upperBound(),
              )
      elif self._mouse_press == Qt.Qt.RightButton:
        e.accept()
        self._menu.popup(e.globalPos());
    # plotMousePressed()

  def plotMouseReleased(self, e):
      """ callback to handle MouseReleased event """
      if self._mouse_press == Qt.Qt.MidButton:
        closest_curve, xVal, yVal, data_point = self.closestCurve(self.position_raw)
        self.zoomcrv(closest_curve)
 #     elif self._mouse_press == Qt.Qt.RightButton:
 #       print "accepting release event";
 #       e.accept()
 #       self._menu.popup(e.globalPos());
      elif self._mouse_press == Qt.Qt.LeftButton:
        if self._popup_text.isVisible():
          self._popup_text.hide()
# assume a change of <= 2 screen pixels is just due to clicking
# left mouse button for no good reason
        if abs(self.press_xpos_raw - e.pos().x()) > 2 and abs(self.press_ypos_raw - e.pos().y()) > 2:
          xmin = min(self.xpos, self.press_xpos)
          xmax = max(self.xpos, self.press_xpos)
          ymin = min(self.ypos, self.press_ypos)
          ymax = max(self.ypos, self.press_ypos)
          if xmin == xmax or ymin == ymax:
              return
          self.zoomStack.append(self.zoomState)
          self.zoomState = (xmin, xmax, ymin, ymax)
          self._plotter.setAxisScale(Qwt.QwtPlot.xBottom, xmin, xmax)
          self._plotter.setAxisScale(Qwt.QwtPlot.yLeft, ymin, ymax)
          self._menu.reset_zoomer.setVisible(True)
          self._plotter.replot()
        if not self.xzoom_loc is None:
          self.zoom_outline.detach()
          self.xzoom_loc = None
          self.yzoom_loc = None

    # plotMouseReleased()

  def reportCoordinates(self, x, y, crv):
    """Format mouse coordinates as real world plot coordinates.
    """
    if not self._plot_label is None:
      plot_label = self._plot_label[crv+self._ref_chan] + ': '
    else:
      plot_label = str(crv+self._ref_chan) + ': '
    temp_str = "nearest x=%-.3g" % x
    temp_str1 = " y=%-.3g" % y
    message = plot_label + temp_str + temp_str1 
    return message
    # reportCoordinates()

  def zoomcrv(self, crv):
    """ If one tries to open a zoom of a curve that is already opened
        open a warning
        Increase the count of the number of curve opened
        Put a flag to indicate wich zoom is opened
        Open a zoompopup of the chosen curve
    """
    if self._indexzoom[crv]:
      if not self._Zoom[crv] is None:
        self._Zoom[crv].show()
        Message = "A zoom of this curve is already opened"
        zoom_message = Qt.QMessageBox.warning(self, "ChartPlot", Message)
#       self._Zoom[crv].raise()
    else:
      #To know how many zoom windows opened (so +1)
      self._zoomcount = self._zoomcount + 1
  
      #Get the color of the curve
      pen = self._crv_key[crv].pen()
  
      #Put a flag to indicate wich zoom is open (for reploting)
      self._indexzoom[crv] = True

      #open a zoom of the selected curve
      PlotArraySize = self._x1.size
      chart = numpy.array(self._chart_data[crv][self._data_index])
      flags = numpy.array(self._flag_data[crv][self._data_index])
      
      self._Zoom[crv] = zoomwin_qt4.ZoomPopup(crv+self._ref_chan, self._x1, chart, flags, pen)
      if not self._source is None:
        self._Zoom[crv].setWindowTitle(self._source)
        
      if not self._data_label is None:
        if not self._plot_label is None:
          plot_label = self._plot_label[crv+self._ref_chan]
        else:
          plot_label = None
        self._Zoom[crv].setDataLabel(self._data_label, plot_label, self._is_vector)
      self._pause[crv] = False
      self.connect(self._Zoom[crv], Qt.SIGNAL("winclosed"), self.myindex)
      self.connect(self._Zoom[crv], Qt.SIGNAL("winpaused"), self.zoomPaused)
      self.connect(self._Zoom[crv], Qt.SIGNAL('save_zoom_display'), self.grab_zoom_display)

      # make sure option to close all Popup windows is seen
      self._menu.close_popups.setVisible(True)


  def grab_zoom_display(self, title, crvtemp):
    self._zoom_png_number = self._zoom_png_number + 1
    png_str = '_' + str(self._zoom_png_number)
    if not self._source is None:
      if title is None:
        save_file = self._source + '_' + './meqbrowser.png'
      else:
        save_file = self._source + '_' + title + png_str + '.png'
    else:
      if title is None:
        save_file = './meqbrowser.png'
      else:
        save_file = title + png_str + '.png'
    save_file_no_space= save_file.replace(' ','_')
    result = Qt.QPixmap.grabWidget(self._Zoom[crvtemp-self._ref_chan]).save(save_file_no_space, "PNG")

  def set_offset(self,parameters=None):
    """ Update the display offset.
    """
    if not parameters is None:
      if parameters.haskey("default_offset"):
        self._offset = parameters.get("default_offset")
        self._refresh_flag = True
        if self._offset < 0.0:
          self._auto_offset = True
          self._offset = 0
          self._max_range = -10000
        else:
          self._auto_offset = False

  def set_offset_scale(self,new_scale):
    """ Update the display offset.
    """
    self._offset = new_scale
    self._refresh_flag = True
    if self._offset < 0.0:
      self._auto_offset = True
      self._offset = 0
      self._max_range = -10000
    else:
      self._auto_offset = False

    for channel in range(self._nbcrv):
      self._updated_data[channel] = True
      self._start_offset_test[channel][self._data_index] = 0
    self.reset_zoom()

  def set_auto_scaling(self):
    """ Update the display offset.
    """
    self._auto_offset = True
    self._offset = 0
    self._refresh_flag = True
    self._max_range = -10000
    for channel in range(self._nbcrv):
      self._updated_data[channel] = True
      self._start_offset_test[channel][self._data_index] = 0
    self.reset_zoom()

  def ChartControlData(self):
    """ Resize array if no zoom windows are open.
    """
    #Works if no zoom windows are open
    if self._zoomcount == 0:
      resizex(self._ArraySize)
    else:
      Message = "All zoom windows should be closed\nto perform action."
      zoom_message = Qt.QMessageBox.warning(self, "ChartPlot", Message)

# this is the equivalent of zoomwarn2.py - use this instead if and when ...
#   Message = "Please put the offset at its maximum value\nbefore zooming by a click on the plot"
#   mb_reporter = Qt.QMessageBox.information(self, "ChartPlot", Message)

  def resizex(self, size):
    """ Get the size the arrays should have
        reinitialize the arrays
    """
      
    for i in range(self._nbcrv):
      if self._indexzoom[i] and not self._Zoom[i] is None:
        self._Zoom[i].resize_x_axis(self._ArraySize)
    # y data with offset for plotting on the main display
    self._spec_grid_offset.resize(self._ArraySize, self._nbcrv+1)
    self._spec_grid_offset = 0
    self._spec_ptr.resize(self._nbcrv+1)
    for i in range(self._nbcrv):
      self._spec_ptr[i] = dtemp + self._ArraySize * i 

    # the y values for zoom pop up windows without the offset
    self._spec_grid.resize(self._ArraySize,self._nbcrv+1)
    self._spec_grid = 0
    self._spec_ptr_actual.resize(self._nbcrv+1)
    for i in range(self._nbcrv):
      self._spec_ptr_actual[i] = dtemp + self._ArraySize * i 

  def zoomCountmin(self):
    """ Reduces the count of zoom windows opened
    """
    self._zoomcount = self._zoomcount - 1

  def zoomPaused(self, crvtemp):
    self._pause[crvtemp-self._ref_chan] = not self._pause[crvtemp-self._ref_chan]


  def myindex(self, crvtemp):
    """ Sets the indexzoom flag of the curve that just closed to False
    """
    self._indexzoom[crvtemp-self._ref_chan] = False
    self._Zoom[crvtemp-self._ref_chan].exec_close()

  def updateEvent(self, data_dict):
    """ Update the curve data for the given channel
    """
    # in updateEvent, channel goes from 0 to _nbcrv - 1
    # ---
    # if necessary, first remove old data from front of queue
    # add new data to end of queue

    # do we have an incoming dictionary?
    q_pos_str = "Sequence Number " + str( data_dict['sequence_number'])
    new_chart_flags = None
    try:
      self._source = data_dict['source']
      new_chart_flags = data_dict['flags']
    except:
      self._source = None
      pass
    channel_no = data_dict['channel']
    new_chart_val = data_dict['value']
    has_keys = True
    add_vells_menu = False
    try:
      data_keys = new_chart_val.keys()
      add_vells_menu = True
    except:
      has_keys = False
      data_keys = []
      data_keys.append(0)
#    print "Data keys",data_keys;
      
    # set current index to first vells, if not initialized
    self._data_index = self._menu.vells_component;
    if self._data_index is None:
      self._data_index = data_keys[0];

    if channel_no >=  self._nbcrv:
      factor = int (channel_no / self._nbcrv)
      self._ref_chan = factor * self._nbcrv
      channel = channel_no - self._ref_chan
    else:
      channel = channel_no
      
    for keys in data_keys: 
      if not self._chart_data[channel].has_key(keys):
        self._chart_data[channel][keys] = []
        self._flag_data[channel][keys] = []
        self._start_offset_test[channel][keys] = 0
#        if len(data_keys) > 1:
#          self._menu.add_vells_key(keys);

      incoming_data = None
      incoming_flags = None
      if has_keys:
        try:
          incoming_data = new_chart_val[keys]
          incoming_flags = new_chart_flags[keys]
        except:
          pass
      else:
        incoming_data = new_chart_val
        incoming_flags = new_chart_flags

      # skip rest of processing if incoming_data is non-existent
      if incoming_data is None:
        continue
      else:
        self._refresh_flag = True

      #print 'incoming flags ', incoming_flags
# first, do we have a scalar?
      is_scalar = False
      scalar_data = 0.0
      flag_data = 0
      try:
        shape = incoming_data.shape
# note: if shape is 1 x N : 1 time point with N freq points
# note: if shape is N x 1 or (N,) : N time points with 1 freq point
#     _dprint(3,'data_array shape is ', shape)
      except:
        is_scalar = True
        scalar_data = incoming_data
        if not incoming_flags is None:
          flag_data = incoming_flags
      if not is_scalar and len(shape) == 1:
        if shape[0] == 1:
          is_scalar = True
          scalar_data = incoming_data[0]
          if not incoming_flags is None:
            flag_data = incoming_flags[0]
          
      if is_scalar:
        #print 'scalar is ', scalar_data
#     if len(self._chart_data[channel]) > self._ArraySize-1:
#       differ = len(self._chart_data[channel]) - (self._ArraySize-1)
#       for i in range(differ):
#         del self._chart_data[channel][0]

        if scalar_data == numpy.inf or scalar_data == numpy.nan:
          flag_data = 10  
        self._chart_data[channel][keys].append(scalar_data)
        self._flag_data[channel][keys].append(flag_data)
        self._updated_data[channel] = True

        # take care of position string
        self._position[channel] = q_pos_str
  
      # otherwise we have an array (assumed to be 1D for the moment), 
      # so we add to the stored chart data in its entirety
      else:
        self._is_vector = True
        num_elements = 1
        for i in range(len(incoming_data.shape)):
          num_elements = num_elements * incoming_data.shape[i]

        flattened_array = incoming_data.copy()
        flattened_array.shape = (num_elements,)
        if num_elements > 1 and incoming_data.shape[0] == 1:
          if  self._data_label is None:
            self._x_title.setText("Frequency Spectrum per Tile Block (Relative Scale)")
          else:
            self._x_title.setText(self._data_label + " Frequency Spectrum per Tile Block (Relative Scale)")
          self._plotter.setAxisTitle(Qwt.QwtPlot.xBottom, self._x_title)
        # check for NaNs and Infs
        self.has_nans_infs = False
        nan_test = numpy.isnan(flattened_array)
        inf_test = numpy.isinf(flattened_array)
        if nan_test.max() > 0 or inf_test.max() > 0:
          delete = nan_test | inf_test
          keep = ~nan_test & ~inf_test
          self.has_nans_infs = True

        append = self._menu.append.isChecked();
        if append: 
          for i in range(len(flattened_array)):
            self._chart_data[channel][keys].append(flattened_array[i])
        else:
          self._chart_data[channel][keys] = flattened_array
        self._updated_data[channel] = True

        if incoming_flags is None:
          flattened_array = numpy.zeros((num_elements,), numpy.int32)
        else:
          flattened_array = numpy.reshape(incoming_flags.copy(),(num_elements,))
        if self.has_nans_infs:
          flattened_array[delete] = 10
        if append: 
          for i in range(len(flattened_array)):
            self._flag_data[channel][keys].append(flattened_array[i])
        else:
          self._flag_data[channel][keys] = flattened_array
          self._start_offset_test[channel][keys] = 0

      if self._ArraySize < len(self._chart_data[channel][keys]):
        self._ArraySize = len(self._chart_data[channel][keys])
        self.set_x_axis_sizes()

  def refresh_event(self):
    """ redisplay plot and zoom
        if refresh flag is true (new data exists)
        call replots
        set refresh flag False
    """

    # if no changes have been made, just return
    if not self._refresh_flag:
      return

    # first determine offsets
    if self._auto_offset:
      for channel in range(self._nbcrv):
        if self._updated_data[channel] and self._chart_data[channel].has_key(self._data_index):
          try:
            chart = numpy.array(self._chart_data[channel][self._data_index])
            #print 'shape chart ', chart.shape, ' ', chart
          except:
            self._updated_data[channel] = False
            pass
          try:
            flags = numpy.array(self._flag_data[channel][self._data_index])
          except:
            self._updated_data[channel] = False
            pass
          # no actual data?
          if chart.shape[0] < 1:
            self._updated_data[channel] = False
          if self._updated_data[channel]:
            test_chart = numpy.compress(flags==0,chart)
            if test_chart.shape[0] > 0:
              if chart.dtype == numpy.complex64 or chart.dtype == numpy.complex128:
                self._menu.showComplexControls(True)
                complex_chart = test_chart.copy()
                self._y_title.setText("%s (Relative Scale)"%self._complex_component)
                self._plotter.setAxisTitle(Qwt.QwtPlot.yLeft, self._y_title)
                if self._complex_component is self.AMP:
                  cplx_chart = abs(complex_chart)
                elif self._complex_component is self.REAL:
                  cplx_chart = complex_chart.real
                elif self._complex_component is self.IMAG:
                  cplx_chart = complex_chart.imag
                elif self._complex_component is self.PHASE:
                  cplx_chart = numpy.angle(complex_chart)
                tmp_max = cplx_chart.max()
                tmp_min = cplx_chart.min()
              else:
                self._menu.showComplexControls(False)
                tmp_max = test_chart.max()
                tmp_min = test_chart.min()
              chart_range = abs(tmp_max - tmp_min)
              # Check if we break any highest or lowest limits
              # this is important for offset reasons.
              # If a chart range is zero, we still need to create
              # an offset so ...
              if chart_range < 1.0e-6:
                chart_range = 1.0e-6
              if chart_range > self._max_range:
                self._max_range = chart_range
              self._start_offset_test[channel][self._data_index] = chart.shape[0]

      #set the max value of the offset
      if 1.1 * self._max_range > self._offset:
        self._offset = 1.1 * self._max_range

        if self._offset < 0.001:
          self._offset = 0.001
        self.emit(Qt.SIGNAL("auto_offset_value"),self._offset)

    # -----------
    # now update data
    # -----------

    for channel in range(self._nbcrv):
      if self._updated_data[channel] and self._chart_data[channel].has_key(self._data_index):
        index = channel+1
        #Set the values and size with the curves
        if index >= 1 and index <= self._nbcrv/4:
          temp_x = self._x1
        elif index >= (self._nbcrv/4)+1 and index <= self._nbcrv/2:
          temp_x = self._x2
        elif index >= (self._nbcrv/2)+1 and index <= 3*(self._nbcrv/4):
          temp_x = self._x3
        elif index >= (3*(self._nbcrv/4))+1 and index <= self._nbcrv:
          temp_x = self._x4

        if self._complex_component is self.PHASE:
          temp_off = (channel % (self._nbcrv/4) + 0.5 ) * self._offset
        else:
          temp_off = (channel % (self._nbcrv/4)) * self._offset

        chart = numpy.array(self._chart_data[channel][self._data_index])
        flags = numpy.array(self._flag_data[channel][self._data_index])
        if chart.dtype == numpy.complex64 or chart.dtype == numpy.complex128:
          complex_chart = chart.copy()
          if self._complex_component is self.AMP:
            self._crv_key[channel].setPen(Qt.QPen(Qt.Qt.red))
            cplx_chart = abs(complex_chart)
          elif self._complex_component is self.REAL:
            self._crv_key[channel].setPen(Qt.QPen(Qt.Qt.blue))
            cplx_chart = complex_chart.real
          elif self._complex_component is self.IMAG:
            self._crv_key[channel].setPen(Qt.QPen(Qt.Qt.gray))
            cplx_chart = complex_chart.imag
          elif self._complex_component is self.PHASE:
            self._crv_key[channel].setPen(Qt.QPen(Qt.Qt.green))
            cplx_chart = numpy.angle(complex_chart)
          # don't display flagged data
          if not self._menu.show_flagged_data.isChecked():
            x_plot_values = numpy.compress(flags==0,temp_x)
            y_plot_values = numpy.compress(flags==0,cplx_chart)
            if y_plot_values.shape[0] == 0:
              y_plot_values = None
          else:
            # can't display NaNs
            if flags.max() == 10:
              x_plot_values = numpy.compress(flags<10,temp_x)
              y_plot_values = numpy.compress(flags<10,cplx_chart)
            else:
              x_plot_values = temp_x
              y_plot_values = cplx_chart

          if not y_plot_values is None: 
            self._crv_key[channel].setData(x_plot_values , y_plot_values+temp_off)
            self._crv_key[channel].attach(self._plotter)
            ylb = y_plot_values[0] + temp_off 
        else:
          self._crv_key[channel].setPen(Qt.QPen(Qt.Qt.black))
          # don't display flagged data
          if not self._menu.show_flagged_data.isChecked():
            x_plot_values = numpy.compress(flags==0,temp_x)
            y_plot_values = numpy.compress(flags==0,chart)
            if y_plot_values.shape[0] == 0:
              y_plot_values = None
          else:
            # can't display NaNs
            if flags.max() == 10:
              x_plot_values = numpy.compress(flags<10,temp_x)
              y_plot_values = numpy.compress(flags<10,chart)
            else:
              x_plot_values = temp_x
              y_plot_values = chart

          if not y_plot_values is None: 
            self._crv_key[channel].setData( x_plot_values , y_plot_values+temp_off)
            self._crv_key[channel].attach(self._plotter)
            ylb = y_plot_values[0] + temp_off 

        # update marker with info about the plot
        if not self._source_marker[channel] is None:
          self._source_marker[channel].detach()
        if not y_plot_values is None and self._menu.show_labels.isChecked():
          if not self._plot_label is None:
            message = self._plot_label[channel + self._ref_chan]
          else:
            message =  str(channel + self._ref_chan)
# text marker giving source of point that was clicked
          if self._source_marker[channel] is None:
            self._source_marker[channel] = Qwt.QwtPlotMarker()
          xlb = temp_x[0]
          self._source_marker[channel].setValue(xlb, ylb)
          self._source_marker[channel].setLabelAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignTop)
          fn = self._plotter.fontInfo().family()
          text = Qwt.QwtText(message)
          text.setColor(Qt.Qt.blue)
          text.setBackgroundBrush(Qt.QBrush(Qt.Qt.yellow))
          text.setFont(Qt.QFont(fn,7,Qt.QFont.Bold,False))
          self._source_marker[channel].setLabel(text)
          self._source_marker[channel].attach(self._plotter)
	 
# need to update any corresponding Zoom window     
#        self._Zoom[channel].resize_x_axis(len(self._chart_data[channel]))
        # Wait that all the channels are modified before 
        # plotting with the new x array


        if not self._mainpause:
          self._refresh_flag = True
	
        #Put the integration number back to 1 for next time
        self._updated_data[channel] = False
      # --------------
      # refresh screen
      # --------------
    if self._refresh_flag: 
      self._plotter.replot()
      self.ReplotZoom()
      self._refresh_flag = False


  def cancel_offset_request(self):
    return        # do nothing

  def start_test_timer(self, time):
    self.counter = 0
    # stuff for tests
    self.startTimer(time)

  def timerEvent(self, e):
    self.counter = self.counter + 1
    test_array = numpy.zeros((128,), numpy.float32)
    data_dict = {}
    data_dict['source'] = 'abc'
    data_dict['sequence_number'] = self.counter
    data_dict['value'] = test_array

    for i in range(test_array.shape[0]):
      test_array[i] = 0.05 * random.random()
    data_dict['channel'] = 1
    self.updateEvent(data_dict)

    for i in range(test_array.shape[0]):
      test_array[i] = 3 * random.random()
    data_dict['channel'] = 3
    self.updateEvent(data_dict)

    for i in range(test_array.shape[0]):
      test_array[i] = 11 * random.random()
    data_dict['channel'] = 11
    self.updateEvent(data_dict)

    return

def make():
    demo = ChartPlot()
    demo.show()
    demo.start_test_timer(500)
    return demo

def main(args):
    app = Qt.QApplication(args)
    demo = make()
    app.exec_()


# Admire
if __name__ == '__main__':
    main(sys.argv)


