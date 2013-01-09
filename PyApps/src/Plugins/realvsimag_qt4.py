#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Browser plugin to show plots of real vs imaginary data
# or 'error' displays


#% $Id: realvsimag.py 6836 2009-03-05 18:55:17Z twillis $ 

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

import math
import random
import sys
from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt

from QwtSpy_qt4 import *

import numpy
#from Timba.GUI.pixmaps import pixmaps
#from guiplot2dnodesettings import *

# local python Error Bar class
import ErrorBar_qt4
import printfilter_qt4
import plot_printer_qt4
                                                                                
from Timba.utils import verbosity
_dbg = verbosity(0,name='realvsimag');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

# Note: using _dprintf (from Oleg)
#The function call is _dprint(N,...), where N is the "debug level". 
#This is a conditional debug-print function; 
#you enable debug-printing via the command line, e.g.:
                                                                                
# ./meqbrowser.py -drealvsimag=5
                                                                                
#which causes all _dprint() statements with N<=5 to execute (and keeps
#the screen clutter-free otherwise). Please try to use _dprint() for all
#your diagnostic printing, as this scheme keeps diagnostic messages clean
#(i.e. I don't see yours unless I enable them, and so they don't get in
#the way of mine).



realvsimag_instructions = \
'''The <b>visu</b> realvsimag and error plots plot real vs imaginary values for data points within a MeqTree. These plots are constructed from <b>visu</b>
commands set to <b>MeqDataCollect</b> nodes. A single plot may combine data from many different nodes together. You may interact with a plot by clicking on the plot with your mouse. <br><br>
Button 1 (Left): If you click the <b>left</b> mouse button on a location inside a plot, you obtain the provenance of the point nearest the location. This information will appear at the lower left hand corner of the display. The information is shown until you release the mouse button. <br><br>
Button 3 (Right):Click the <b>right</b> mouse button in a plot window to get a context menu with options for printing, or zooming the display. The zoom display option acts as a toggle between having zooming on or off. Selecting the Printer option from the Context Menu causes the standard Qt printer widget to appear. That widget will enable you print out a copy of your plot, or save the plot in Postscript format to a file.'''

class realvsimag_plotter(object):
  """ a class to plot real vs imaginary values for data points """

# definitions of global tables used to translate between externally
# specified string values and internal enumerated values
  color_table = {
        'none': None,
        'black': Qt.Qt.black,
        'blue': Qt.Qt.blue,
        'cyan': Qt.Qt.cyan,
        'gray': Qt.Qt.gray,
        'green': Qt.Qt.green,
        'magenta': Qt.Qt.magenta,
        'red': Qt.Qt.red,
        'white': Qt.Qt.white,
        'yellow': Qt.Qt.yellow,
        'darkBlue' : Qt.Qt.darkBlue,
        'darkCyan' : Qt.Qt.darkCyan,
        'darkGray' : Qt.Qt.darkGray,
        'darkGreen' : Qt.Qt.darkGreen,
        'darkMagenta' : Qt.Qt.darkMagenta,
        'darkRed' : Qt.Qt.darkRed,
        'darkYellow' : Qt.Qt.darkYellow,
        'lightGray' : Qt.Qt.lightGray,
        }

  symbol_table = {
#        'none': Qwt.QwtSymbol.None,
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
 	'sticks' : Qwt.QwtPlotCurve.Sticks,
 	'steps' : Qwt.QwtPlotCurve.Steps,
        'SolidLine' : Qt.Qt.SolidLine,
        'DashLine' : Qt.Qt.DashLine,
        'DotLine' : Qt.Qt.DotLine,
        'DashDotLine' : Qt.Qt.DashDotLine,
        'DashDotDotLine' : Qt.Qt.DashDotDotLine,
        'solidline' : Qt.Qt.SolidLine,
        'dashline' : Qt.Qt.DashLine,
        'dotline' : Qt.Qt.DotLine,
        'dashdotline' : Qt.Qt.DashDotLine,
        'dashdotdotline' : Qt.Qt.DashDotDotLine,
        }

  menu_table = {
        'Toggle flagged data': 200,
        'Toggle blink of flagged data': 201,
        'Toggle results history': 202,
        'Modify Plot Parameters': 299,
        'Reset zoomer': 300,
        'Toggle Legend': 301,
        'Undo Last Zoom': 302,
        'Save Display in PNG Format':303,
        }
    
  def __init__(self, plot_key="", parent=None):

        self.parent = parent
        self.plot_key = plot_key
        
        # Initialize a QwPlot central widget
        self.plot = Qwt.QwtPlot(parent)
        
        # create copy of standard application font..
        font = Qt.QFont(Qt.QApplication.font());
        fi = Qt.QFontInfo(font);
        # and scale it down to 70%
        font.setPointSize(fi.pointSize()*0.7);
        # apply font to QwtPlot
#       self.plot.setTitleFont(font);
#       for axis in range(0,4):
#         self.plot.setAxisFont(axis,font);
#         self.plot.setAxisTitleFont(axis,font);
        
        self.plot.plotLayout().setCanvasMargin(0)

# over-ride default QwtPlot sizePolicy
        self.plot.setSizePolicy(Qt.QSizePolicy.Expanding,Qt.QSizePolicy.Expanding)
          
# for legend ...
#        self.plot.setAutoLegend(True)
#        self.plot.enableLegend(True)
#        self.plot.setLegendPos(Qwt.Bottom)
#        self.plot.setLegendFrameStyle(Qt.QFrame.Box | Qt.QFrame.Sunken)

        self._mainwin = parent and parent.topLevelWidget();
        # get status bar
        self._statusbar = self._mainwin and self._mainwin.statusBar();

        self.__initTracking()
#       self.__initZooming()
        # forget the toolbar for now -- too much trouble when we're dealing with 
        # multiple windows. Do a context menu instead
        # self.__initToolBar()
        self.__initContextMenu()

        # initialize internal variables for plot
        self._x_auto_scale = 1
        self._y_auto_scale = 1
        self.axis_xmin = 0
        self.axis_xmax = 0
        self.axis_ymin = 0
        self.axis_ymax = 0
        self._circle_dict = {}
        self._line_dict = {}
        self._xy_plot_dict = {}
        self._x_errors_plot_dict = {}
        self._y_errors_plot_dict = {}
        self._xy_plot_color = {}
        self._plotter_dict = {}
        self._flags_dict = {}
        self._plotterlabels_dict = {}
        self._plotterlabels_start = {}
        self._x_errors_dict = {}
        self._y_errors_dict = {}
        self._flags_i_dict = {}
        self._flags_r_dict = {}
        self.flag_plot_dict={}
        self.zoomStack = []

        self.setResults = True
        self.flag_toggle = True
        self.flag_blink = False
        self.toggle_menu_added = False
        self.plot_mean_circles = False
        self.plot_stddev_circles = False
        self.plot_mean_arrows = False
        self._plot_flags = False
        self.plot_symbol = None
        self.plot_symbol_size = None
        self.plot_line_style = None
        self._plot_title = 'realvsimag'
        self._legend_plot = None
        self._legend_popup = None
        self.label = ''
        self._data_labels = None

        self._plot_x_axis_label = 'Real Axis'
        self._plot_y_axis_label = 'Imaginary Axis'
        self.plot.setAxisTitle(Qwt.QwtPlot.xBottom, self._plot_x_axis_label)
        self.plot.setAxisTitle(Qwt.QwtPlot.yLeft, self._plot_y_axis_label)
        self.index = -1
        self._angle = 0.0
        self._radius = 20.0
        self.xpos = -10000
        self.ypos = -10000

# used for plotting MeqParm solutions
        self.x_list = []
        self.y_list = []
        self.value = 100

# used for errors plotting 
        self.errors_plot = False

# used for errors plot testing 
        self.gain = 1.0

# legends
        # self.setlegend = 0
        # self.plot.setAutoLegend(self.setlegend)
        # self.plot.enableLegend(False)
        # self.plot.setLegendPos(Qwt.Right)

# set default background to  whatever QApplication sez it should be!
#       self.plot.setCanvasBackground(QApplication.palette().active().base())

# add on-line instructions
        self.plot.setWhatsThis(realvsimag_instructions)

# attach a grid
        self.grid = Qwt.QwtPlotGrid()
        self.grid.setPen(Qt.QPen(Qt.Qt.black, 0, Qt.Qt.DotLine))
        self.grid.attach(self.plot)


  # __init__()

# called from result_plotter.py
  def reset_data_collectors(self):
        self._plotter_dict = {}
        self._flags_dict = {}


# methods to initialise internal variables by means of outside
# function calls
  def set_compute_circles (self, do_compute_circles=True):
        self.plot_mean_circles = do_compute_circles

  def set_compute_std_dev_circles (self, do_compute_stddev_circles=True):
        self.plot_stddev_circles = do_compute_stddev_circles


  def __initTracking(self):
        """Initialize tracking
        """        
        self.spy = Spy(self.plot.canvas())

        Qt.QObject.connect(self.spy,
                     Qt.SIGNAL("MouseMove"),
                     self.onMouseMoved)
        Qt.QObject.connect(self.spy,
                     Qt.SIGNAL("MousePress"),
                     self.onMousePressed)
        Qt.QObject.connect(self.spy,
                     Qt.SIGNAL("MouseRelease"),
                     self.onMouseReleased)



        self.plot.canvas().setMouseTracking(True)
#       if self._statusbar:
#         self._statusbar.message(
#           'Plot cursor movements are tracked in the status bar',2000)

    # __initTracking()

  def onMouseMoved(self, e):
    position = e.pos()
    xPos = position.x()
    yPos = position.y()
    if abs(self.xpos - position.x()) > 2 and abs(self.ypos - position.y())> 2:
# we are zooming, so remove any markers
      self.timerEvent_marker()
    # onMouseMoved()
    
  def __initZooming(self):
        """Initialize zooming - not presently called
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
        QObject.connect(self.picker, Qt.SIGNAL('selected(const QPointArray &)'),
                     self.selected)



    # __initZooming()
       
  def setZoomerMousePattern(self, index):
        """Set the mouse zoomer pattern.
        """
        if index == 0:
            pattern = [
                QwtEventPattern.MousePattern(Qt.LeftButton, Qt.Qt.NoButton),
                QwtEventPattern.MousePattern(Qt.RightButton, Qt.Qt.NoButton),
#                QwtEventPattern.MousePattern(Qt.MidButton, Qt.Qt.NoButton),
                QwtEventPattern.MousePattern(Qt.LeftButton, Qt.Qt.ShiftButton),
                QwtEventPattern.MousePattern(Qt.RightButton, Qt.Qt.ShiftButton),
#                QwtEventPattern.MousePattern(Qt.MidButton, Qt.Qt.ShiftButton),
                ]
            self.zoomer.setMousePattern(pattern)
        elif index in (1, 2, 3):
            self.zoomer.initMousePattern(index)
        else:
            raise ValueError, 'index must be in (0, 1, 2, 3)'
  # setZoomerMousePattern()

  def __initContextMenu(self, Test=False):
        """Initialize the toolbar
        """
        # skip if no main window
        if not Test:
          if not self._mainwin:
            return;
          
        self._menu = Qt.QMenu(self._mainwin);

        menu_id = self.menu_table['Modify Plot Parameters']
        self._modify_plot_parameters = Qt.QAction('Modify Plot Parameters',self.plot)
        self._menu.addAction(self._modify_plot_parameters)
        self._modify_plot_parameters.setData(Qt.QVariant(str(menu_id)))
        Qt.QObject.connect(self._modify_plot_parameters,Qt.SIGNAL("triggered()"),self.update_display);


        menu_id = self.menu_table['Reset zoomer']
        self._reset_zoomer = Qt.QAction('Reset zoomer',self.plot)
        self._menu.addAction(self._reset_zoomer)
        self._reset_zoomer.setData(Qt.QVariant(str(menu_id)))
        self._reset_zoomer.setVisible(False)
        Qt.QObject.connect(self._reset_zoomer,Qt.SIGNAL("triggered()"),self.update_display);

        menu_id = self.menu_table['Undo Last Zoom']
        self._undo_last_zoom = Qt.QAction('Undo Last Zoom',self.plot)
        self._menu.addAction(self._undo_last_zoom)
        self._undo_last_zoom.setData(Qt.QVariant(str(menu_id)))
        self._undo_last_zoom.setVisible(False)
        Qt.QObject.connect(self._undo_last_zoom,Qt.SIGNAL("triggered()"),self.update_display);

        menu_id = self.menu_table['Toggle Legend']
        self._toggle_legend = Qt.QAction('Toggle Legend',self.plot)
        self._menu.addAction(self._toggle_legend)
        self._toggle_legend.setData(Qt.QVariant(str(menu_id)))
        Qt.QObject.connect(self._toggle_legend,Qt.SIGNAL("triggered()"),self.update_display);

        menu_id = self.menu_table['Save Display in PNG Format']
        self._save_display = Qt.QAction('Save Display in PNG Format',self.plot)
        self._menu.addAction(self._save_display)
        self._save_display.setData(Qt.QVariant(str(menu_id)))
        Qt.QObject.connect(self._save_display,Qt.SIGNAL("triggered()"),self.update_display);
        
        printer = Qt.QAction('Print plot',self.plot);
#       printer.setIconSet(pixmaps.fileprint.iconset());
        Qt.QObject.connect(printer,Qt.SIGNAL("triggered()"),self.printPlot);
        self._menu.addAction(printer)
  # __initContextMenu(self):

  def removeMarkers(self):
      for i in self.plot.itemList():
        if isinstance(i, Qwt.QwtPlotMarker):
          i.detach()

  def setResultsSelector(self):
    toggle_id = self.menu_table['Toggle results history']
    self._menu.insertItem("Toggle results history", toggle_id)

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
##        QObject.connect(self.btnPrint, Qt.SIGNAL('clicked()'),
##                     self.printPlot)
##        QObject.connect(self.btnZoom, Qt.SIGNAL('toggled(bool)'),
##                     self.zoom)

    # __initToolBar()

  def getPlotParms(self):
    plot_parms = {}
    plot_parms['window_title'] = self._plot_title
    plot_parms['x_title'] = self._plot_x_axis_label
    plot_parms['y_title'] = self._plot_y_axis_label
    plot_parms['x_auto_scale'] = self._x_auto_scale
    plot_parms['y_auto_scale'] = self._y_auto_scale
    plot_parms['axis_xmin'] = self.axis_xmin
    plot_parms['axis_xmax'] = self.axis_xmax
    plot_parms['axis_ymin'] = self.axis_ymin
    plot_parms['axis_ymax'] = self.axis_ymax
    return plot_parms

  def setPlotParms(self, plot_parms):
    self._plot_title = plot_parms['window_title'] 
    self._plot_x_axis_label = plot_parms['x_title']
    self._plot_y_axis_label = plot_parms['y_title'] 

    self.plot.setTitle(self._plot_title)
    self.plot.setAxisTitle(Qwt.QwtPlot.xBottom, self._plot_x_axis_label)
    self.plot.setAxisTitle(Qwt.QwtPlot.yLeft, self._plot_y_axis_label)

    self._x_auto_scale = plot_parms['x_auto_scale']
    if self._x_auto_scale == '1':
      self._x_auto_scale = True
      self.plot.setAxisAutoScale(Qwt.QwtPlot.xBottom)
    else:
      self._x_auto_scale = False
    self._y_auto_scale = plot_parms['y_auto_scale']
    if self._y_auto_scale == '1':
      self._y_auto_scale = True
      self.plot.setAxisAutoScale(Qwt.QwtPlot.yLeft)
    else:
      self._y_auto_scale = False
    if not self._x_auto_scale: 
      self.axis_xmin = float(plot_parms['axis_xmin'])
      self.axis_xmax = float(plot_parms['axis_xmax'])
      self.plot.setAxisScale(Qwt.QwtPlot.xBottom, self.axis_xmin, self.axis_xmax)
    if not self._y_auto_scale: 
      self.axis_ymin = float(plot_parms['axis_ymin'])
      self.axis_ymax = float(plot_parms['axis_ymax'])
      self.plot.setAxisScale(Qwt.QwtPlot.yLeft, self.axis_ymin, self.axis_ymax)
    self.plot.replot()

  def update_display(self):
    """ Qt slot to handle event generated by context menu """
    action = Qt.QObject.sender(self.plot)
    menuid, flag = action.data().toInt()

    if not flag:
      return

    print 'caught menuid ', menuid
    if menuid == 299:
      parms_interface = WidgetSettingsDialog(actual_parent=self, gui_parent=self.parent)
      return
    if menuid == 300:
      self.reset_zoom()
      return
    if menuid == 301:
      self.toggleLegend()
      return
    if menuid == 302:
      self.reset_zoom(True)
      return

    if menuid == self.menu_table['Toggle results history']:
      self.toggleResults()
      return

    if menuid == self.menu_table['Save Display in PNG Format']:
      self.plot.emit(Qt.SIGNAL("save_display"),self._plot_title)
      return True

# toggle flags display	
    if menuid == 200:
      if self.flag_toggle == False:
        self.flag_toggle = True
        self.plot_flags()
      else:
        self.flag_toggle = False
        self.remove_flags()
      self.plot.replot()
      return

# blink flags display	
    if menuid == 201:
      if self.flag_blink == False:
        self.flag_blink = True
        self.timer = QTimer(self.plot)
        self.timer.connect(self.timer, Qt.SIGNAL('timeout()'), self.timerEvent_blink)
        self.timer.start(2000)
      else:
        self.flag_blink = False
      return

  def timerEvent_blink(self):
    """ Qt slot to handle events from timer started above """

# start or stop blinking
    if not self.flag_blink:
      self.timer.stop()
      self.flag_toggle = False
      self.remove_flags()
    else:
      if self.flag_toggle == False:
        self.flag_toggle = True
        self.plot_flags()
      else:
        self.flag_toggle = False
        self.remove_flags()
    self.plot.replot()

  def toggleLegend(self):
    if self.setlegend == 1:
      self.setlegend = 0
      self.plot.enableLegend(False)
    else:
      self.setlegend = 1
      self.plot.enableLegend(True)
    # self.plot.setAutoLegend(self.setlegend)
    self.plot.replot()

    # toggleLegend()

  def toggleResults(self):
    if self.setResults:
      self.setResults = False
    else:
      self.setResults = True
    self.plot.emit(Qt.SIGNAL("show_results_selector"),self.setResults)

    # toggleLegend()

  def onMousePressed(self, e):
    """ Mouse press processing instructions go here"""

    _dprint(2,' in onMousePressed');
    _dprint(3,' onMousePressed event:',e);
# we use a middle mouse button pressed event to retrieve and display
# information in the lower left corner of the plot about
# the point closest to the location where the mouse was pressed
    if e.button() == Qt.Qt.LeftButton:
        _dprint(2,'button is left button');
        xPos = e.pos().x()
        yPos = e.pos().y()

#store coordinates for later zoom
        self.xpos = xPos
        self.ypos = yPos
#       self.plot.setOutlinePen(Qt.QPen(Qt.Qt.black))
#       self.plot.setOutlineStyle(Qwt.Rect)
        if self.zoomStack == []:
          try:
            self.zoomState = (
              self.plot.axisScale(Qwt.QwtPlot.xBottom).lowerBound(),
              self.plot.axisScale(Qwt.QwtPlot.xBottom).upperBound(),
              self.plot.axisScale(Qwt.QwtPlot.yLeft).lowerBound(),
              self.plot.axisScale(Qwt.QwtPlot.yLeft).upperBound(),
              )
          except:
            self.zoomState = (
              self.plot.axisScale(Qwt.QwtPlot.xBottom).lowerBound(),
              self.plot.axisScale(Qwt.QwtPlot.xBottom).upperBound(),
              self.plot.axisScale(Qwt.QwtPlot.yLeft).lowerBound(),
              self.plot.axisScale(Qwt.QwtPlot.yLeft).upperBound(),
              )

        _dprint(2,'xPos yPos ', xPos, ' ', yPos);
# We get information about the qwt plot curve that is
# closest to the location of this mouse pressed event.
# We are interested in the nearest curve_number and the index, or
# sequence number of the nearest point in that curve.
        curve_number, distance, xVal, yVal, index = self.plot.closestCurve(xPos, yPos)
        _dprint(2,' curve_number, distance, xVal, yVal, index ', curve_number, ' ', distance,' ', xVal, ' ', yVal, ' ', index);
# To determine the data source for the given curve or point
# each qwt curve has a number which can be associated
# with an individual 'string' key. We stored these keys and 
# associated curve numbers in the xy_plot_dict, the
# x_errors_plot_dict, and the y_errors_plot_dict objects
# in the x_vs_y_plot method
        message = ''
        wanted_item_tag = None
# first search _xy_plot_dict
        plot_keys = self._xy_plot_dict.keys()
        _dprint(2, 'plot_keys ', plot_keys)
        for i in range(0, len(plot_keys)):
          current_item_tag = plot_keys[i]
          plot_key = self._xy_plot_dict[current_item_tag]
          _dprint(2, 'plot_key ', plot_key, ' current item tag ', current_item_tag)
          if plot_key == curve_number:
            wanted_item_tag = current_item_tag
            break
# if nothing found then search _x_errors_plot_dict
        if self.errors_plot and wanted_item_tag is None:
          plot_keys = self._x_errors_plot_dict.keys()
          _dprint(2, 'plot_keys ', plot_keys)
          for i in range(0, len(plot_keys)):
            current_item_tag = plot_keys[i]
            plot_key = self._x_errors_plot_dict[current_item_tag]
            _dprint(2, 'plot_key ', plot_key, ' current item tag ', current_item_tag)
            if plot_key == curve_number:
# Note:if wanted_item_tag came from an error curve, need to get
# the associated x,y data curve.
# So convert to corresponding value for actual data points
              location_value =  current_item_tag.find(self.error_tag)
              wanted_item_tag = current_item_tag[:location_value] + self.value_tag + '_plot'
              break

# if nothing found then search _y_errors_plot_dict
        if self.errors_plot and wanted_item_tag is None:
          plot_keys = self._y_errors_plot_dict.keys()
          _dprint(2, 'plot_keys ', plot_keys)
          for i in range(0, len(plot_keys)):
            current_item_tag = plot_keys[i]
            plot_key = self._y_errors_plot_dict[current_item_tag]
            _dprint(2, 'plot_key ', plot_key, ' current item tag ', current_item_tag)
            if plot_key == curve_number:
# convert to corresponding value for actual data points
              location_value =  current_item_tag.find(self.error_tag)
              wanted_item_tag = current_item_tag[:location_value] + self.value_tag + '_plot'
              break

# if we have a valid result, find and display the label
        if not wanted_item_tag is None:
          data_key_index = wanted_item_tag + '_r'
# the plotterlabels_dict contains a list of labels that can
# be associated with each of the data curves
          label = self._plotterlabels_dict[data_key_index]
          _dprint(2, 'label ', label)
# The start_pos list contains the starting positions in the
# curve for each of the data labels
          start_pos =  self._plotterlabels_start[data_key_index]
# Now find out which group of points actually contains the
# specific point that was nearest our mouse-clicked position.
          label_index = None
          for j in range(0, len(start_pos)):
            if index == start_pos[j]:
              label_index = j
              break
            if index > start_pos[j]:
              continue
            else:
              label_index = j - 1
              break 
          if label_index is None:
            label_index = len(start_pos) - 1
# We should have now found the right group of points
# and can get the appropriate label.
          if not label_index is None:
            try:
              message = 'this data point comes from \n ' + label[label_index] 
            except:
              message = 'data source is not known'
          else:
            message = ''
        else:
          message = 'data source is not known'
# alias
        fn = self.plot.fontInfo().family()

# Now create text marker giving source of point that was clicked
        self.marker = self.plot.insertMarker()
        try:
          ylb = self.plot.axisScale(Qwt.QwtPlot.yLeft).lowerBound()
          xlb = self.plot.axisScale(Qwt.QwtPlot.xBottom).lowerBound()
        except:
          ylb = self.plot.axisScale(Qwt.QwtPlot.yLeft).lowerBound()
          xlb = self.plot.axisScale(Qwt.QwtPlot.xBottom).lowerBound()
        self.plot.setMarkerPos(self.marker, xlb, ylb)
        self.plot.setMarkerLabelAlign(self.marker, Qt.Qt.AlignRight | Qt.Qt.AlignTop)
        self.plot.setMarkerLabel( self.marker, message,
          Qt.QFont(fn, 7, Qt.QFont.Bold, False),
          Qt.Qt.blue, Qt.QPen(Qt.Qt.red, 2), Qt.QBrush(Qt.Qt.yellow))
# We have inserted the marker, so replot.
        self.plot.replot()

    elif e.button() == Qt.Qt.RightButton:
      e.accept();  # accept even so that parent widget won't get it
      # popup the menu
      self._menu.popup(e.globalPos());
            
  # onMousePressed

  def onMouseReleased(self, e):
    if Qt.Qt.LeftButton == e.button():
# handle completion of zooming
# assume a change of <= 2 screen pixels is just due to clicking
# left mouse button for coordinate values
      if abs(self.xpos - e.pos().x()) > 2 and abs(self.ypos - e.pos().y())> 2:
        xmin = min(self.xpos, e.pos().x())
        xmax = max(self.xpos, e.pos().x())
        ymin = min(self.ypos, e.pos().y())
        ymax = max(self.ypos, e.pos().y())
#       self.plot.setOutlineStyle(Qwt.Cross)
        xmin = self.plot.invTransform(Qwt.QwtPlot.xBottom, xmin)
        xmax = self.plot.invTransform(Qwt.QwtPlot.xBottom, xmax)
        ymin = self.plot.invTransform(Qwt.QwtPlot.yLeft, ymin)
        ymax = self.plot.invTransform(Qwt.QwtPlot.yLeft, ymax)
        self.plot.setAxisScale(Qwt.QwtPlot.xBottom, xmin, xmax)
        self.plot.setAxisScale(Qwt.QwtPlot.yLeft, ymin, ymax)
        self._x_auto_scale = False
        self._y_auto_scale = False
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.axis_xmin = xmin
        self.axis_xmax = xmax
        self.axis_ymin = ymin
        self.axis_ymax = ymax
        menu_id = self.menu_table['Reset zoomer']
        self._menu.setItemVisible(menu_id, True)
        menu_id = self.menu_table['Undo Last Zoom']
        self._menu.setItemVisible(menu_id, True)

        self.zoomStack.append(self.zoomState)
        self.zoomState = (xmin, xmax, ymin, ymax)

      self.timerEvent_marker()
  # onMouseReleased()

  def timerEvent_marker(self):
    """ remove all markers, but reinsert the legend_plot
        marker if it exists """
    self.removeMarkers()
    if not self._legend_plot is None:
      self.legend_marker = self.plot.insertMarker()
      try:
        ylb = self.plot.axisScale(Qwt.QwtPlot.yLeft).upperBound()
        xlb = self.plot.axisScale(Qwt.QwtPlot.xBottom).lowerBound()
      except:
        ylb = self.plot.axisScale(Qwt.QwtPlot.yLeft).upperBound()
        xlb = self.plot.axisScale(Qwt.QwtPlot.xBottom).lowerBound()
      self.plot.setMarkerPos(self.legend_marker, xlb, ylb)
      self.plot.setMarkerLabelAlign(self.legend_marker, Qt.AlignRight | Qt.AlignBottom)
      fn = self.plot.fontInfo().family()
      self.plot.setMarkerLabel( self.legend_marker, self._legend_plot,
        Qt.QFont(fn, 7, Qt.QFont.Bold, False),
        Qt.Qt.black, Qt.QPen(Qt.Qt.red, 2), Qt.QBrush(Qt.Qt.yellow))
    self.plot.replot()
  # timerEvent_marker()

# compute points for two circles
  def setup_circle (self, item_tag, line_style='lines'):
      """ store plotting parameters for future 
          circles plots """

# if this is a new item_tag, add a new circle
      circle_key = item_tag + '_circle'
      if self._circle_dict.has_key(circle_key) == False: 
        plot_color = None
        if item_tag.find('stddev') >= 0:
          plot_color = self._stddev_circle_color
        else:
          plot_color = self._mean_circle_color
        curve = Qwt.QwtPlotCurve(circle_key)
        self._circle_dict[circle_key] = curve
        curve.attach(self.plot)
        line_thickness = 2
        circle_line_style = None
        if self.line_style_table.has_key(line_style):
          circle_line_style = self.line_style_table[line_style]
        else:
          line_style = 'lines'
          circle_line_style = self.line_style_table[line_style]
        if line_style == 'lines' or line_style == 'dots' or line_style == 'none':
          curve.setStyle(circle_line_style)
          curve.setPen(Qt.QPen(plot_color,line_thickness))
        else:
          curve.setPen(Qt.QPen(plot_color,line_thickness))

# compute points for two circles
  def compute_circles (self, item_tag, radius, x_cen=0.0, y_cen=0.0):
      """ compute values for circle running through specified
          point and a line pointing to the point """

      # compute circle that will run through average value
      x_pos = numpy.zeros((73,),numpy.float64)
      y_pos = numpy.zeros((73,),numpy.float64)
      angle = -5.0
      for j in range(0, 73 ) :
        angle = angle + 5.0
        x_pos[j] = x_cen + radius * math.cos(angle/57.2957795)
        y_pos[j] = y_cen + radius * math.sin(angle/57.2957795)

# get the key for this circle
      circle_key = item_tag + '_circle'
      if self._circle_dict.has_key(circle_key):
        key_circle = self._circle_dict[circle_key] 
        key_circle.setData(x_pos, y_pos)

  def setup_arrow (self, item_tag, line_style='lines'):
      """ store plotting parameters for future
          arrow plots """

# if this is a new item_tag, add a new arrow
      line_key = item_tag + '_arrow'
      if self._line_dict.has_key(line_key) == False: 
        curve = Qwt.QwtPlotCurve(line_key)
        self._line_dict[line_key] = curve
        curve.attach(self.plot)
        line_thickness = 2
        arrow_line_style = None
        if self.line_style_table.has_key(line_style):
          arrow_line_style = self.line_style_table[line_style]
        else:
          line_style = 'lines'
          arrow_line_style = self.line_style_table[line_style]
        if line_style == 'lines' or line_style == 'dots' or line_style == 'none':
          curve.setStyle(arrow_line_style)
          curve.setPen(Qt.QPen(self._mean_circle_color,line_thickness))
        else:
          curve.setPen(Qt.QPen(self._mean_circle_color,line_thickness,arrow_line_style))

  def compute_arrow (self, item_tag,avg_r, avg_i, x_cen=0.0, y_cen=0.0):
      """ compute plot values for arrows """

      # compute line that will go from centre of circle to 
      # position of average value
      x1_pos = numpy.zeros((2,),numpy.float64)
      y1_pos = numpy.zeros((2,),numpy.float64)
      x1_pos[0] = x_cen
      y1_pos[0] = y_cen
      x1_pos[1] = avg_r
      y1_pos[1] = avg_i

# get the plot key for this arrow
      line_key = item_tag + '_arrow'
      if self._line_dict.has_key(line_key):
        curve = self._line_dict[line_key] 
        curve.setData(x1_pos, y1_pos)

  def plot_data(self, visu_record, attribute_list=None, label=''):
      """ process incoming data and attributes into the
          appropriate type of plot """
      _dprint(2,'****** in plot_data');

      self.label = label
      self.plot_mean_circles = False
      self.plot_stddev_circles = False
      self.plot_mean_arrows = False
      self.plot_symbol = None
      self.plot_symbol_size = None
      self.plot_line_style = None
      self._plot_title = 'realvsimag'
      self._plot_type = None
      self.value_tag = None
      self.error_tag = None
#      self._legend_plot = None
#      self._legend_popup = None
      self._plot_color = None
      self._mean_circle_color = None
      self._mean_circle_style = None
      self._stddev_circle_color = None
      self._stddev_circle_style = None
      self._string_tag = None
      self._data_flags = None
      self._x_y_data = True
      self._tag_plot_attrib={}


# first find out what kind of plot we are making
      if not self.plot_key is None:
        self._plot_type = self.plot_key
      item_tag = ''
      if attribute_list is None and visu_record.has_key('attrib'):
        self._attrib_parms = visu_record['attrib']
        _dprint(2,'self._attrib_parms ', self._attrib_parms);
        self._plot_parms = self._attrib_parms.get('plot')
        if self._plot_parms.has_key('tag_attrib'):
          temp_parms = self._plot_parms.get('tag_attrib')
          tag = temp_parms.get('tag')
          self._tag_plot_attrib[tag] = temp_parms
        if self._plot_parms.has_key('attrib'):
          temp_parms = self._plot_parms.get('attrib')
          self._plot_parms = temp_parms
        if self._plot_type is None:
          if self._plot_parms.has_key('plot_type'):
            self._plot_type = self._plot_parms.get('plot_type', 'realvsimag')
          if self._plot_parms.has_key('type'):
            self._plot_type = self._plot_parms.get('type', 'realvsimag')
        self.plot_mean_circles = self._plot_parms.get('mean_circle', False)
        self.plot_stddev_circles = self._plot_parms.get('stddev_circle', False)
        self.plot_mean_arrows = self._plot_parms.get('mean_arrow', False)
        self.plot_symbol_size = self._plot_parms.get('symbol_size', 5)
        self.plot_symbol = self._plot_parms.get('symbol', 'circle')
        self.plot_line_style = self._plot_parms.get('line_style', 'dots')
        self._plot_color = self._plot_parms.get('color', 'blue')
        if self.color_table.has_key(self._plot_color):
          self._plot_color = self.color_table[self._plot_color]
        self._mean_circle_style = self._plot_parms.get('mean_circle_style', 'lines')
        self._mean_circle_color = self._plot_parms.get('mean_circle_color', 'blue')
        if self.color_table.has_key(self._mean_circle_color):
          self._mean_circle_color = self.color_table[self._mean_circle_color]
        self._stddev_circle_style = self._plot_parms.get('stddev_circle_style', 'DotLine')
        self._stddev_circle_color = self._plot_parms.get('stddev_circle_color', 'blue')
        if self.color_table.has_key(self._stddev_circle_color):
          self._stddev_circle_color = self.color_table[self._stddev_circle_color]
        self.value_tag = self._plot_parms.get('value_tag', False)
        self.error_tag = self._plot_parms.get('error_tag', False)
        if self._plot_parms.has_key('legend'):
          legend = self._plot_parms.get('legend')
          if legend.has_key('plot'):
            self._legend_plot = legend.get('plot')
          if legend.has_key('popup'):
            self._legend_popup = legend.get('popup')
        tag = self._attrib_parms.get('tag','') 
        if isinstance(tag, tuple):
          for i in range(0, len(tag)):
            temp_key = item_tag + ' ' + tag[i]
            item_tag = temp_key
          self._string_tag = item_tag 
          item_tag = self._string_tag + '_plot'
        else:
          self._string_tag = tag 
          item_tag = self._string_tag + '_plot'

# Otherwise we have a list of attribute dicts.
# We start at the beginning of the list and 'mostly'
# fill in a value for a parameter as soon as it is
# encountered for the first time. So values defined
# near the root generally have precedence over 
# corresponding values defined at or near leaf nodes
      else:
        list_length = len(attribute_list)
        for i in range(list_length):
          self._attrib_parms = attribute_list[i]
          _dprint(2,'self._attrib_parms ', self._attrib_parms);
          if self._attrib_parms.has_key('tag'):
            tag = self._attrib_parms.get('tag')
            if self._string_tag is None:
              self._string_tag = ''
            if isinstance(tag, tuple):
              _dprint(2,'tuple tag ', tag);
              for i in range(0, len(tag)):
                if self._string_tag.find(tag[i]) < 0:
                  temp_tag = self._string_tag + ' ' + tag[i] 
                  self._string_tag = temp_tag
              _dprint(2,'self._string_tag ', self._string_tag);
              item_tag = self._string_tag + '_plot'
            else:
              _dprint(2,'non tuple tag ', tag);
              if self._string_tag is None:
                self._string_tag = ''
              if self._string_tag.find(tag) < 0:
                temp_tag = self._string_tag + ' ' + tag 
                self._string_tag = temp_tag 
                _dprint(2,'self._string_tag ', self._string_tag);
              item_tag = self._string_tag + '_plot'

          if self._attrib_parms.has_key('plot'):
            self._plot_parms = self._attrib_parms.get('plot')
            if self._plot_parms.has_key('tag_attrib'):
              temp_parms = self._plot_parms.get('tag_attrib')
              tag = temp_parms.get('tag')
              self._tag_plot_attrib[tag] = temp_parms
            if self._plot_parms.has_key('attrib'):
              temp_parms = self._plot_parms.get('attrib')
              self._plot_parms = temp_parms
            _dprint(2,'self._plot_parms ', self._plot_parms);
            if self._plot_type is None and self._plot_parms.has_key('plot_type'):
              self._plot_type = self._plot_parms.get('plot_type')
            if self._plot_type is None and self._plot_parms.has_key('type'):
              self._plot_type = self._plot_parms.get('type')
            _dprint(2,'self._plot_x_axis_label ', self._plot_x_axis_label);
            _dprint(2,'self._plot_parms ', self._plot_parms);
            _dprint(2,'self._plot_parms.has_key(x_axis) ', self._plot_parms.has_key('x_axis'));
            if self._plot_parms.has_key('x_axis'):
              self._plot_x_axis_label = self._plot_parms.get('x_axis')
            if self._plot_parms.has_key('y_axis'):
              self._plot_y_axis_label = self._plot_parms.get('y_axis')
            if self._plot_parms.has_key('title'):
              self._plot_title = self.label + ' ' +self._plot_parms.get('title')
            if self.value_tag is None and self._plot_parms.has_key('value_tag'):
              self.value_tag = self._plot_parms.get('value_tag')
            if self.error_tag is None and self._plot_parms.has_key('error_tag'):
              self.error_tag = self._plot_parms.get('error_tag')

            if not self.plot_mean_circles and self._plot_parms.has_key('mean_circle'):
              self.plot_mean_circles = self._plot_parms.get('mean_circle')
            if not self.plot_stddev_circles and self._plot_parms.has_key('stddev_circle'):
              self.plot_stddev_circles = self._plot_parms.get('stddev_circle')
            if not self.plot_mean_arrows and self._plot_parms.has_key('mean_arrow'):
              self.plot_mean_arrows = self._plot_parms.get('mean_arrow')
            if self.plot_symbol_size is None and self._plot_parms.has_key('symbol_size'):
              self.plot_symbol_size = int(self._plot_parms.get('symbol_size'))
              _dprint(3, 'plot sysmbol size set to ', self.plot_symbol_size)
            if self.plot_symbol is None and self._plot_parms.has_key('symbol'):
              self.plot_symbol = self._plot_parms.get('symbol')
            if self.plot_line_style is None and self._plot_parms.has_key('line_style'):
              self.plot_line_style = self._plot_parms.get('line_style')
            if self._plot_color is None and self._plot_parms.has_key('color'):
              self._plot_color = self._plot_parms.get('color')
              _dprint(3, 'plot color set to ', self._plot_color)
              if self.color_table.has_key(self._plot_color):
                self._plot_color = self.color_table[self._plot_color]
              else:
                Message = self._plot_color + " is not a valid color.\n Using blue by default"
                mb_reporter = Qt.QMessageBox.warning(None, "RealVsImag", Message)
                self._plot_color = "blue"
                self._plot_color = self.color_table[self._plot_color]
            if self._mean_circle_color is None and self._plot_parms.has_key('mean_circle_color'):
              self._mean_circle_color = self._plot_parms.get('mean_circle_color')
              _dprint(3, 'plot mean_circle_color set to ', self._mean_circle_color)
              if self.color_table.has_key(self._mean_circle_color):
                self._mean_circle_color = self.color_table[self._mean_circle_color]
              else:
                Message = self._plot_mean_circle_color + " is not a valid color.\n Using blue by default"
                mb_reporter = Qt.QMessageBox.warning(None, "RealVsImag", Message)
                self._mean_circle_color = "blue"
                self._mean_circle_color = self.color_table[self._mean_circle_color]
            if self._mean_circle_style is None and self._plot_parms.has_key('mean_circle_style'):
              self._mean_circle_style = self._plot_parms.get('mean_circle_style')
              _dprint(3, 'plot mean_circle_style set to ', self._mean_circle_style)
              if not self.line_style_table.has_key(self._mean_circle_style):
                Message = self._mean_circle_style + " is not a valid line style.\n Using solid line by default."
                mb_reporter = Qt.QMessageBox.warning(None, "RealVsImag", Message)
                self._mean_circle_style = "lines"
            if self._stddev_circle_color is None and self._plot_parms.has_key('stddev_circle_color'):
              self._stddev_circle_color = self._plot_parms.get('stddev_circle_color')
              _dprint(3, 'plot stddev_circle_color set to ', self._stddev_circle_color)
              if self.color_table.has_key(self._stddev_circle_color):
                self._stddev_circle_color = self.color_table[self._stddev_circle_color]
              else:
                Message = self._stddev_circle_color + " is not a valid color.\n Using blue by default"
                mb_reporter = Qt.QMessageBox.warning(None, "RealVsImag", Message)
                self._stddev_circle_color = "blue"
                self._stddev_circle_color = self.color_table[self._stddev_circle_color]
            if self._stddev_circle_style is None and self._plot_parms.has_key('stddev_circle_style'):
              self._stddev_circle_style = self._plot_parms.get('stddev_circle_style')
              _dprint(3, 'plot stddev_circle_style set to ', self._stddev_circle_style)
              if not self.line_style_table.has_key(self._stddev_circle_style):
                Message = self._stddev_circle_style + " is not a valid line style.\n Using solid line by default."
                mb_reporter = Qt.QMessageBox.warning(None, "RealVsImag", Message)
                self._stddev_circle_style = "lines"
            if self._plot_parms.has_key('legend'):
              legend = self._plot_parms.get('legend')
              _dprint(3, 'legend found is ', legend)
              if legend.has_key('plot'):
                if self._legend_plot is None:
                  self._legend_plot = ''
                legend_str = legend.get('plot')
                if self._legend_plot.find(legend_str) < 0:
                  temp_str = self._legend_plot + ' ' + legend_str
                  self._legend_plot = temp_str
              if legend.has_key('popup'):
                if self._legend_popup is None:
                  self._legend_popup = ''
                popup_str = legend.get('popup')
                if self._legend_popup.find(popup_str) < 0:
                  temp_str = self._legend_popup + ' ' + popup_str
                  self._legend_popup = temp_str

      if len(self._tag_plot_attrib) > 0:
        _dprint(3, 'self._tag_plot_attrib has keys ', self._tag_plot_attrib.keys())
# if still undefined
      if self._string_tag is None:
            self._string_tag = 'data'
            item_tag = self._string_tag + '_plot'
      if self._plot_title is None:
        self._plot_title = self.label + ' ' + self._plot_type

# define the plot title
      self.plot.setTitle(self._plot_title)

# the system knows that it is plotting 'errors' if it has
# been able to find both a value_tag and an error_tag along
# the way to this leaf node. 
      if self.value_tag is None:
        self.value_tag = False
        self.errors_plot = False
      if self.error_tag is None:
        self.error_tag = False
        self.errors_plot = False
      else:
        if not self.value_tag == False:
          _dprint(2, 'errors plot is true')
          self.errors_plot = True

# set sensible defaults for various parameters if
# they were not specified anywhere 
      if self.plot_symbol_size is None:
        self.plot_symbol_size = 5
      if self.plot_symbol is None:
        self.plot_symbol = 'circle'
      if self.plot_line_style is None:
        self.plot_line_style = 'dots'
      if self._plot_color is None:
        self._plot_color = 'blue'
        self._plot_color = self.color_table[self._plot_color]
      if self._mean_circle_style is None:
        self._mean_circle_style = 'lines'
      if self._stddev_circle_style is None:
        self._stddev_circle_style = 'DotLine'
      if self._mean_circle_color is None:
        self._mean_circle_color = 'blue'
        self._mean_circle_color = self.color_table[self._mean_circle_color]
      if self._stddev_circle_color is None:
        self._stddev_circle_color = 'blue'
        self._stddev_circle_color = self.color_table[self._stddev_circle_color]

# extract and define labels for this data item
# note: the item_tag field consists of a concatination of all
# the 'tag' fields found by the system on the way to the current
# leaf note with '_plot' appended. We now create separate
# labels for the real and imaginary data associated with
# this item_tag.
      self._label_i = item_tag + "_i"
      self._label_r = item_tag + "_r"

      if visu_record.has_key('value'):
        self._data_values = visu_record['value']
      if visu_record.has_key('flags'):
        self._data_flags = visu_record['flags']

# eventually indent the next lines?
        self._plot_flags = True

# if we have read in flagged data, need to add 
# toggle stuff to context menu
        if not self.toggle_menu_added:
          caption = "Toggle flagged data" 
          toggle_id = 200
          self._menu.insertItem(caption,toggle_id)
          caption = "Toggle blink of flagged data"
          toggle_id = 201
          self._menu.insertItem(caption,toggle_id)
          self.toggle_menu_added = True


# note: the self._data_labels field that we now extract
# was generated in the result_plotter.py script as it
# traversed the 'Visu' tree. It is a string concatination
# of all the 'Visu' 'label' fields for the path to
# this leaf node. When the user clicks on a data point
# with the middle mouse buton this string is displayed
# to show the path to the data point that was clicked on.
      if visu_record.has_key('plot_label'):
        self._data_labels = visu_record['plot_label']
        _dprint(2,'self._data_labels ', self._data_labels);

# now generate plot 
      self.x_vs_y_plot(item_tag)
  
  def x_vs_y_plot (self,item_tag):
      """ plot real vs imaginary values together with circles
          indicating average values """
 
# Get and combine all plot array data together into one python list
# We are actually converting python numarrays into a list -
# Maybe we can be more efficient if we store the numarrays in a group
# of tuples or something. To be investigated ....
      num_plot_arrays = len(self._data_values)
      _dprint(2,' num_plot_arrays ', num_plot_arrays);
      self._is_complex = True;
# we have separate lists for real, imaginary and flag data
      data_r = []
      data_i = []
      data_r_f = []
      data_i_f = []
# start_pos gives the first position of a member of an individual
# numpy array in the larger combined list
      start_pos = []
      start_flags_pos = []
      for i in range(0, num_plot_arrays):
# make sure we are using a numpy array
        array_representation = numpy.asarray(self._data_values[i])
        xx_r = None
        xx_i = None
        if i == 0:
          start_pos.append(0)
        else:
          start_pos.append(len(data_r))
        if array_representation.dtype == numpy.complex128:
          _dprint(2,'array is complex')
          xx_r = array_representation.real
          xx_i = array_representation.imag
        else:
          xx_r = array_representation
          self._is_complex = False
          _dprint(2,'array is real')
        array_dim = len(xx_r.shape)
        num_elements = 1
        for j in range(0, array_dim):
          num_elements = num_elements * xx_r.shape[j]
        flattened_array_r = numpy.reshape(xx_r,(num_elements,))

# handle flags if present
        flattened_array_f = None
#       if not self._data_flags is None:
#         xx_f = numpy.asarray(self._data_flags[i])
        if self._plot_flags:
          xx_f = numpy.zeros( (num_elements,), dtype=numpy.float32 )
          for k in range(0, num_elements):
            if k % 2 == 0:
              xx_f[k] = 1
          flag_array_dim = len(xx_f.shape)
          num_flag_elements = 1
          for j in range(0, flag_array_dim):
            num_flag_elements = num_flag_elements * xx_f.shape[j]
          flattened_array_f = numpy.reshape(xx_f,(num_elements,))
          if i == 0:
            start_flags_pos.append(0)
          else:
            start_flags_pos.append(len(data_r_f))
        for j in range(0, num_elements): 
          data_r.append(flattened_array_r[j])
          if not flattened_array_f is None:
            if flattened_array_f[j] > 0:                      
              data_r_f.append(flattened_array_r[j])
        if xx_i != None:
          flattened_array_i = numpy.reshape(xx_i,(num_elements,))
          for j in range(0, num_elements): 
            data_i.append(flattened_array_i[j])
            if not flattened_array_f is None:
              if flattened_array_f[j] > 0:                      
                data_i_f.append(flattened_array_i[j])
        else:
# since we are plotting real vs imaginary data, we must add
# imaginary values of zero, if we just receive an incoming
# real array
          if not self.errors_plot:
            for j in range(0, num_elements): 
              data_i.append(0.0)
            if not flattened_array_f is None:
              for j in range(0, num_elements): 
               if flattened_array_f[j] > 0:                      
                 data_i_f.append(0.0)
          if self.errors_plot and self._string_tag.find(self.error_tag)<0:
            for j in range(0, num_elements): 
              data_i.append(0.0)
            if not flattened_array_f is None:
              for j in range(0, num_elements): 
               if flattened_array_f[j] > 0:                      
                 data_i_f.append(0.0)

# add data to set of curves
# obviously if we didn't get any actual data for some reason
# just return
      if len(data_r) == 0:
        print 'nothing to update!'
        return
      _dprint(2, 'main key ', self._label_r)

# first store the incoming real data.

# have we previously collected data which had associated with it
# this particular self._label_r string?
      if self._plotter_dict.has_key(self._label_r) == False:
# add the new data to a 'dict' of visualization lists, where the index to
# the data is given by the self._label_r string
        self._plotter_dict[self._label_r] = data_r
        _dprint(2, 'assigned data to self._plotter_dict key ', self._label_r)
# store the string giving the path to this data in a 'dict'
# of plotterlabels where the index is again given by self._label_r
        self._plotterlabels_dict[self._label_r] = self._data_labels
# store the starting position list for the numarrays that were in the
# incoming data in a plotterlabels_start dict
        self._plotterlabels_start[self._label_r] = start_pos

# if we have flag data, store it
        if len(data_r_f) > 0:
          if self.errors_plot: 
            if self._label_r.find(self.error_tag) < 0:
              self._flags_r_dict[self._label_r] = data_r_f
          else:
             self._flags_r_dict[self._label_r] = data_r_f

# otherwise we have previously stored data with this particular index
      else:
        prev_data_length = len(self._plotter_dict[self._label_r])
# add new data to the end of the current list for this 
        self._plotter_dict[self._label_r] = self._plotter_dict[self._label_r] + data_r
# add new data label giving path to this data to the plotterlabels dict
# (hum - is this the right thing to do?)
        self._plotterlabels_dict[self._label_r] = self._plotterlabels_dict[self._label_r] + self._data_labels
# the starting positions of each of the new numarrays in the new combined data
# list are calculated in the following loop
        for i in range(0,len(start_pos)):
          start_pos[i] = start_pos[i] + prev_data_length
# this list of starting positions is then appended to the list already
# stored in the plotterlabels_start dict
        self._plotterlabels_start[self._label_r] = self._plotterlabels_start[self._label_r] + start_pos

# if we have flag data, store it
        if len(data_r_f) > 0:
          if self.errors_plot: 
            if self._label_r.find(self.error_tag) < 0:
              self._flags_r_dict[self._label_r] = self._flags_r_dict[self._label_r] + data_r_f
          else:
            self._flags_r_dict[self._label_r] = self._flags_r_dict[self._label_r] + data_r_f

# if we are doing an 'errors' plot and the tag we are working
# with contains the 'error_tag' field then we know that the
# incoming data represent errors. Errors are always real.
      if self.errors_plot and self._string_tag.find(self.error_tag)>= 0:
        self._x_y_data = False

# otherwise we are working with x,y data and need to store the imaginary data
      else:
        if self._plotter_dict.has_key(self._label_i) == False:
#add the new data to a 'dict' of visualization lists
          self._plotter_dict[self._label_i] = data_i

# if we have imaginary flag data, store it
          if len(data_i_f) > 0:
            self._flags_i_dict[self._label_i] =  data_i_f
        else:
          self._plotter_dict[self._label_i] = self._plotter_dict[self._label_i] + data_i
          if len(data_i_f) > 0:
            self._flags_i_dict[self._label_i] =  self._flags_i_dict[self._label_i] + data_i_f

# We have now stored data and some associated 'meta data' - labels
# and starting positions, flagged data etc in various python dictionaries.

# We now set up the qwt plot components for the data we have just stored

# If this is a new item_tag, add a new curve to the qwt plot.
# At the same time, construct basic plot attributes, title etc,
# if they have not previously been set. 

      _dprint(3, 'plot key is ', item_tag)
      
# qwt curves each have a number which can be associated
# with an individual 'string' key. We store these keys and 
# associated curve numbers in the xy_plot_dict
      if self._xy_plot_dict.has_key(item_tag) == False: 
        if not self._plot_y_axis_label is None:
          self.plot.setAxisTitle(Qwt.QwtPlot.yLeft, self._plot_y_axis_label)
        if not self._plot_x_axis_label is None:
          self.plot.setAxisTitle(Qwt.QwtPlot.xBottom, self._plot_x_axis_label)

# store the color for this particular plot in the 
# xy_plot_color dict using item_tag as the key
        self._xy_plot_color[item_tag] = self._plot_color

# if we have x, y data
        if self._x_y_data:
# key_plot is an integer
          curve = Qwt.QwtPlotCurve(item_tag)
          curve.attach(self.plot)
# store this integer value in the xy_plot_dict using the
# item_tag string as key
          self._xy_plot_dict[item_tag] = curve

# using the integer 'key_plot' as index, set up various
# plotting parameters for the curve - color, symbol, symbol size etc
          curve.setPen(Qt.QPen(self._plot_color))
          if not self.line_style_table.has_key(self.plot_line_style):
            Message = self.plot_line_style + " is not a valid line style.\n Using dots by default"
            mb_reporter = Qt.QMessageBox.warning(None, "RealVsImag", Message)
            self.plot_line_style = "dots"
          line_style = self.line_style_table[self.plot_line_style]
          curve.setStyle(line_style)
#         plot_curve = self.plot.curve(key_plot)
          _dprint(3, 'self.plot_symbol ', self.plot_symbol)
          if not self.symbol_table.has_key(self.plot_symbol):
            Message = self.plot_symbol + " is not a valid symbol.\n Using circle by default"
            mb_reporter = Qt.QMessageBox.warning(None, "RealVsImag", Message)
            self.plot_symbol = "circle"
          plot_symbol = self.symbol_table[self.plot_symbol]
          _dprint(3, 'self.plot_symbol_size ', self.plot_symbol_size)
#         plot_curve.setSymbol(Qwt.QwtSymbol(plot_symbol, Qt.QBrush(self._plot_color),
          curve.setSymbol(Qwt.QwtSymbol(plot_symbol, Qt.QBrush(self._plot_color),
                     Qt.QPen(self._plot_color, 2), Qt.QSize(self.plot_symbol_size, self.plot_symbol_size)))

# set up to plot circles if plot_mean_circles or plot_stddev_circles flags
# were set and we have xy data
	  if self.plot_mean_circles:
            self.setup_circle (item_tag+'mean', self._mean_circle_style)
            if self.plot_mean_arrows:
              self.setup_arrow (item_tag, self._mean_circle_style)
	  if self.plot_stddev_circles:
            self.setup_circle (item_tag+'stddev', self._stddev_circle_style)

# if we have error data
        else:
# store an integer value of -1 in the xy_plot_dict using the
# item_tag string as key. That way we we can distinguish from a
# 'normal' xy plot in the update_plot method below 
          self._xy_plot_dict[item_tag] = -1
# self.x_errors is a ErrorBarPlotCurve object
          self.x_errors = ErrorBarPlotCurve(self.plot,self._plot_color,2);
          _dprint(3, 'self.x_errors set to ', self.x_errors)
          self.x_errors.setXErrors(True)
# Insert this x error ErrorBarPlotCurve into the qwt plot
# Insert a reference to its curve number in the 
# x_errors_plot_dict. This dict is used when retrieving
# label information from middle mouse button clicks
          self._x_errors_plot_dict[item_tag] = self.plot.insertCurve(self.x_errors);
          _dprint(3, 'self.x_errors stored in self._x_errors_dict with key ', item_tag)
# store a reference to this x error curve object in
# a x_errors_dict using item_tag as key
          self._x_errors_dict[item_tag] = self.x_errors
# self.y_errors is a ErrorBarPlotCurve object
          self.y_errors = ErrorBarPlotCurve(self.plot,self._plot_color,2);
          _dprint(3, 'self.y_errors set to ', self.y_errors)
# insert this y error ErrorBarPlotCurve into the qwt plot
# Insert a reference to its curve number in the 
# y_errors_plot_dict. This dict is used when retrieving
# label information from middle mouse button clicks
          self._y_errors_plot_dict[item_tag] = self.plot.insertCurve(self.y_errors);
# store a reference to this y error curve object in
# a y_errors_dict using item_tag as key
          self._y_errors_dict[item_tag] = self.y_errors

  # end of x_vs_y_plot 

# data for plot has been gathered together after tree traversal
# now update plot curves, etc
  def update_plot(self):
      """ get plot data from various dicts and display it after all plot data 
          has been stored """
# plot_keys is just a list of the item tags that have gone into the plot
      plot_keys = self._xy_plot_dict.keys()
      _dprint(3, 'in update_plot xy_plot_dict plot_keys ', plot_keys)
      _dprint(3, 'in update_plot plotter_dict keys ', self._plotter_dict.keys())
      _dprint(3, 'in update_plot x_errors_dict keys ', self._x_errors_dict.keys())
      for i in range(0, len(plot_keys)): 
        current_item_tag = plot_keys[i]
        _dprint(3, 'iter current plot key ', i, ' ',current_item_tag)
        data_r = None
        data_i = None
        data_errors = None
# first get any imaginary data associated with this key
# data_key_i just equates to self._label_i in the 'plot_data' method
        data_key_i = current_item_tag + '_i'
        if self._plotter_dict.has_key(data_key_i):
          data_i = self._plotter_dict[data_key_i]
# Real data numbers can be 'error' data or the real numbers
# corresponding to the imaginary numbers retrieved above.
# data_key_r just equates to self._label_r in the 'plot_data' method
        data_key_r = current_item_tag + '_r'

        if self.errors_plot: 
          if data_key_r.find(self.error_tag) >= 0:
            if self._plotter_dict.has_key(data_key_r):
# if the above 3 if statements are all satisfied, we have error data
              data_errors = self._plotter_dict[data_key_r]
              if not data_errors is None:
                _dprint(3, 'data_errors assigned', data_errors)
          else:
# If data_key_r does not contain the 'error_tag' string
# then even though this is an errors plot, this data_key_r
# key points to the real numbers corresponding to the
# imaginary numbers already retrieved above.
            if self._plotter_dict.has_key(data_key_r):
              data_r = self._plotter_dict[data_key_r]
              if not data_r is None:
                _dprint(3, 'data_r assigned', data_r)
        else:
# If this is not an errors plot then the data_key_r must
# give real numbers corresponding to the imaginaries retrieved
# above
          if self._plotter_dict.has_key(data_key_r):
            data_r = self._plotter_dict[data_key_r]

# if we have found errors data, assign the errors data to the appropriate
# x and y ErrorBarPlotCurve objects. These ErrorBarPlotCurve objects
# are obtained from the x_errors_dict and y_errors_dict 
# python dicts using the current_item_tag string as the key
        if not data_errors is None:
          _dprint(3, 'data_errors current plot key ',current_item_tag)
          _dprint(3, 'x_errors_dict keys ', self._x_errors_dict.keys())
          if self._x_errors_dict.has_key(current_item_tag):
            self.x_errors = self._x_errors_dict[current_item_tag]
            _dprint(3, 'self.x_errors ', self.x_errors)
            self.x_errors.setErrors(data_errors)
            _dprint(3, 'x data errors set in plot')
          if self._y_errors_dict.has_key(current_item_tag):
            self.y_errors = self._y_errors_dict[current_item_tag]
            _dprint(3, 'self.y_errors ', self.y_errors)
            self.y_errors.setErrors(data_errors)
            _dprint(3, 'y data errors set in plot')

# Otherwise we should have retrieved a set of real and imaginary
# data elements to be plotted against each other, and, if this
# is an errors plot, we need to tell the errors plot about
# the data points associated with the errors
        else:
          _dprint(3, 'setting data values')
# get the number of the curve corresponding to this current_item_tag
# key
#         key_plot = self._xy_plot_dict[current_item_tag] 
          if data_i is None:
            data_i = []
            for i in range(len(data_r)):
              data_i.append(0.0)           
# assign the real and imaginary data to this curve
          curve= self._xy_plot_dict[current_item_tag]
          curve.setData(data_r, data_i)
          _dprint(3, 'set data values in plot')

# if we are plotting errors, we also need to assign these 
# real/imaginary values to the appropriate ErrorBarPlotCurve objects
          if self.errors_plot:
            _dprint(3, 'setting data for errors plot')
# convert real/imaginary data current_item_tag key to what
# should be the corresponding key for the error data 
            location_value =  current_item_tag.find(self.value_tag)
            error_key = current_item_tag[:location_value] + self.error_tag + '_plot'
# Assign the real/imaginary  data to the appropriate
# x and y ErrorBarPlotCurve objects. These ErrorBarPlotCurve objects
# are obtained from the x_errors_dict and y_errors_dict 
# python dicts using the 'error_key' string iwe just derived
# as the key
            if self._x_errors_dict.has_key(error_key):
              self.x_errors = self._x_errors_dict[error_key]
              self.x_errors.setData(data_r,data_i)
              _dprint(3, 'set data values for x errors')
            if self._y_errors_dict.has_key(error_key):
              self.y_errors = self._y_errors_dict[error_key]
              self.y_errors.setData(data_r,data_i)
              _dprint(3, 'set data values for y errors')

# finally plot various ancilliary stuff


# plot mean circles in real vs imaginary plot?
        if not self.errors_plot and self.plot_mean_circles:
# get means of real and imaginary numbers
          real_array = numpy.asarray(data_r)
          mean_r = real_array.mean()
          imag_array = numpy.asarray(data_i)
          mean_i = imag_array.mean()
# compute radius to mean
          x_sq = math.pow(mean_r, 2)
          y_sq = math.pow(mean_i, 2)
          radius = math.sqrt(x_sq + y_sq)
# plot the mean circle
          self.compute_circles (current_item_tag+'mean', radius, 0.0, 0.0)
# plot an 'arrow' if requested
          if self.plot_mean_arrows:
            self.compute_arrow (current_item_tag, mean_r, mean_i)

# plot standard deviation circles?
        if not self.errors_plot and self.plot_stddev_circles:
# convert lists to a complex array` and compute means
          real_array = numpy.asarray(data_r)
          mean_r = real_array.mean()
          imag_array = numpy.asarray(data_i)
          mean_i = imag_array.mean()
          complex_data = numpy.zeros( (len(data_r),), dtype=numpy.complex128 )
          complex_data.real = real_array
          complex_data.imag = imag_array
          radius = complex_data.std(dtype=numpy.float64)
# plot the stddev circle
          self.compute_circles (current_item_tag + 'stddev', radius, mean_r, mean_i)

# add in flag data to plots if requested
      if self._plot_flags and self.flag_toggle:
        self.plot_flags()

# we have inserted all data into curves etc, so as the last step
# actually update the displayed plot
      self.plot.replot()

# Need to place legend after first replot, because QwtAutoScale not
# set until initial replot; legend cannot be placed until
# scale has been set

# Put legend_plot stuff in upper left hand corner of display
# with yellow background
      if not self._legend_plot is None:
         self.legend_marker = self.plot.insertMarker()
         try:
           ylb = self.plot.axisScale(Qwt.QwtPlot.yLeft).upperBound()
           xlb = self.plot.axisScale(Qwt.QwtPlot.xBottom).lowerBound()
         except:
           ylb = self.plot.axisScale(Qwt.QwtPlot.yLeft).upperBound()
           xlb = self.plot.axisScale(Qwt.QwtPlot.xBottom).lowerBound()
         self.plot.setMarkerPos(self.legend_marker, xlb, ylb)
         self.plot.setMarkerLabelAlign(self.legend_marker, Qt.AlignRight | Qt.AlignBottom)
         fn = self.plot.fontInfo().family()
         self.plot.setMarkerLabel( self.legend_marker, self._legend_plot,
#          QFont(fn, 9, QFont.Bold, False),
           Qt.QFont(fn, 7, Qt.QFont.Bold, False),
           Qt.Qt.black, Qt.QPen(Qt.Qt.red, 2), Qt.QBrush(Qt.Qt.yellow))
         self.plot.replot()

    # end of update_plot 

  def plot_flags(self):
    """ routine to overlay flag data on top of regular xy data """

# set up and plot flags in their entirety
    if len(self._flags_r_dict) > 0:
      plot_flag_r_keys = self._flags_r_dict.keys()
      for i in range(0, len(plot_flag_r_keys)):
         key_flag_plot = -1
         flag_data_r = self._flags_r_dict[plot_flag_r_keys[i]]
         end_location = len(plot_flag_r_keys[i])
# get the equivalent for the imaginary data
         flag_data_i_string = plot_flag_r_keys[i][:end_location-2] + '_i'
         flag_data_i = self._flags_i_dict[flag_data_i_string]

         if self.flag_plot_dict.has_key(plot_flag_r_keys[i]) == False:
           curve = Qwt.QwtPlotCurve(plot_flag_r_keys[i])
           self.flag_plot_dict[plot_flag_r_keys[i]] = curve
           curve.attach(self.plot)
           curve.setPen(Qt.QPen(Qt.Qt.black))
           curve.setStyle(Qwt.QwtPlotCurve.Dots)
           curve.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.XCross, Qt.QBrush(Qt.Qt.black),
                     Qt.QPen(Qt.Qt.black), Qt.QSize(15, 15)))
         else:
           curve = self.flag_plot_dict[plot_flag_r_keys[i]]
           curve.setData(flag_data_r, flag_data_i)

  def remove_flags(self):
    """ routine to remove curves associated with flag data """

    if len(self.flag_plot_dict) > 0:
      plot_flag_keys = self.flag_plot_dict.keys()
      for i in range(0, len(plot_flag_keys)):
         curve = self.flag_plot_dict[plot_flag_keys[i]]
         curve.detach()
      self.flag_plot_dict = {}

# a test routine
  def go(self, counter):
      """Create and plot some garbage data
      """
      if counter == 0:
        self.__initContextMenu(True)
      self.set_compute_circles()
      self.set_compute_std_dev_circles()

      item_tag = 'test'
      xx = self._radius * math.cos(self._angle/57.2957795)
      yy = self._radius * math.sin(self._angle/57.2957795)

      x_pos = numpy.zeros((20,),numpy.float64)
      y_pos = numpy.zeros((20,),numpy.float64)
      for j in range(0,20) :
        x_pos[j] = xx + random.random()
        y_pos[j] = yy + random.random()

      # if this is a new item_tag, add a new plot,
      # otherwise, replace old one
      plot_key = item_tag + '_plot'
      self._plot_color = self.color_table["red"]
      self._mean_circle_color = self.color_table["blue"]
      self._stddev_circle_color = self.color_table["green"]
      if self._xy_plot_dict.has_key(plot_key) == False: 
        curve =Qwt.QwtPlotCurve(plot_key)
        self._xy_plot_dict[plot_key] = curve
        curve.attach(self.plot)
        curve.setPen(Qt.QPen(self._plot_color))
        curve.setData(x_pos, y_pos)
        curve.setStyle(Qwt.QwtPlotCurve.Dots)
        self.plot.setTitle("Real vs Imaginary Demo")
        plot_symbol = self.symbol_table["circle"]
        curve.setSymbol(Qwt.QwtSymbol(plot_symbol, Qt.QBrush(self._plot_color),
                     Qt.QPen(self._plot_color), Qt.QSize(10, 10)))
      else:
        curve = self._xy_plot_dict[plot_key] 
        curve.setData(x_pos, y_pos)

      avg_r = x_pos.mean()
      avg_i = y_pos.mean()
      if self.plot_mean_circles:
        x_sq = pow(avg_r, 2)
        y_sq = pow(avg_i, 2)
        radius = math.sqrt(x_sq + y_sq)
        self.plot_mean_arrows = True
        self.setup_arrow (item_tag)
        self.setup_circle(item_tag)
        self.compute_circles (item_tag, radius)
        self.compute_arrow (item_tag, avg_r, avg_i)
      if self.plot_stddev_circles:
        complex_data = numpy.zeros( (len(x_pos),), dtype=numpy.complex128 )
        complex_data.real = x_pos
        complex_data.imag = y_pos
        radius = complex_data.std(dtype=numpy.float64)
        self.setup_circle(item_tag + 'stddev')
        self.compute_circles (item_tag + 'stddev', radius, avg_r, avg_i)
      if counter == 0:
        self.reset_zoom()
      else:
        self.plot.replot()

    # go()

# a test routine
  def go_errors(self, counter):
      """Create and plot some garbage error data
      """
      if counter == 0:
        self.__initContextMenu(True)

      item_tag = 'test'
      self._radius = 0.9 * self._radius

      self.gain = 0.95 * self.gain
      num_points = 10
      x_pos = numpy.zeros((num_points,),numpy.float64)
      y_pos = numpy.zeros((num_points,),numpy.float64)
      x_err = numpy.zeros((num_points,),numpy.float64)
      y_err = numpy.zeros((num_points,),numpy.float64)
      for j in range(0,num_points) :
        x_pos[j] = self._radius + 3 * random.random()
        y_pos[j] = self._radius + 2 * random.random()
        x_err[j] = self.gain * 3 * random.random()

      # if this is a new item_tag, add a new plot,
      # otherwise, replace old one
      plot_key = item_tag + '_plot'
      self._plot_color = self.color_table["red"]
      if self._xy_plot_dict.has_key(plot_key):
        self._xy_plot_dict[plot_key].detach()
        
      curve = ErrorBar_qt4.ErrorBarPlotCurve(
          x = x_pos,
          y = y_pos,
          dx = x_err,
          dy = x_err,
          curvePen = Qt.QPen(self._plot_color),
          curveSymbol = Qwt.QwtSymbol(Qwt.QwtSymbol.Cross,
                                    Qt.QBrush(),
                                    Qt.QPen(Qt.Qt.yellow, 2),
                                    Qt.QSize(7, 7)),
          errorPen = Qt.QPen(Qt.Qt.blue, 2),
          errorCap = 10,
          errorOnTop = False,
          )
      curve.plotErrorsOnly()

      curve.attach(self.plot)
      self._xy_plot_dict[plot_key] = curve

      if counter == 0:
        self.reset_zoom()
      else:
        self.plot.replot()
  # go_errors()

  def go_meqparms(self, counter):
      """Create and plot some garbage data
      """
      item_label = 'MeqParm'
      self.x_list.append(counter+1)
      self.value = 0.8 * self.value + 10 * random.random() 
      self.y_list.append(self.value)

      # if this is a new item_label, add a new plot,
      # otherwise, replace old one
      plot_key = item_label + '_plot'
      self._plot_color = self.color_table["red"]
      if self._xy_plot_dict.has_key(plot_key) == False: 
        curve = Qwt.QwtPlotCurve(plot_key)
        self._xy_plot_dict[plot_key] = curve
        curve.attach(self.plot)
        curve.setPen(Qt.QPen(self._plot_color))
        curve.setData(self.x_list, self.y_list)
        curve.setStyle(Qwt.QwtPlotCurve.Dots)
        self.plot.setAxisTitle(Qwt.QwtPlot.xBottom, 'Time Sequence')
        self.plot.setAxisTitle(Qwt.QwtPlot.yLeft, 'MeqParm Fit')
        plot_symbol = self.symbol_table["circle"]
        curve.setSymbol(Qwt.QwtSymbol(plot_symbol, Qt.QBrush(self._plot_color),
                     Qt.QPen(self._plot_color), Qt.QSize(10, 10)))
      else:
        curve = self._xy_plot_dict[plot_key] 
        curve.setData(self.x_list, self.y_list)

      self.plot.replot()

  # go_meqparms()

  def clearZoomStack(self):
        """Auto scale and clear the zoom stack
        """
        self.plot.replot()
        self.zoomer.setZoomBase()
    # clearZoomStack()

  def start_timer(self, time):
        timer = Qt.QTimer(self.plot)
        timer.connect(timer, Qt.SIGNAL('timeout()'), self.timerEvent)
        timer.start(time)

    # start_timer()

  def timerEvent(self):
      self._angle = self._angle + 5;
      self._radius = 5.0 + 2.0 * random.random()
      self.index = self.index + 1
      self.go(self.index)

# for testing error plotting
#     self.go_errors(self.index)

# for testing meqparms plotting
#     self.go_meqparms(self.index)

  # timerEvent()

  def reset_zoom(self, undo_last_zoom = False):
    """ resets data display so all data are visible """
    if len(self.zoomStack):
      while len(self.zoomStack):
        axis_parms = self.zoomStack.pop()
        xmin = axis_parms[0]
        xmax = axis_parms[1]
        ymin = axis_parms[2]
        ymax = axis_parms[3]
        if undo_last_zoom:
          break
      self.plot.setAxisScale(Qwt.QwtPlot.xBottom, xmin, xmax)
      self.plot.setAxisScale(Qwt.QwtPlot.yLeft, ymin, ymax)
      self._x_auto_scale = False
      self._y_auto_scale = False
      self.axis_xmin = xmin
      self.axis_xmax = xmax
      self.axis_ymin = ymin
      self.axis_ymax = ymax
      if undo_last_zoom:
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
      else:
        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None
      if not len (self.zoomStack):
        toggle_id = self.menu_table['Reset zoomer']
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = self.menu_table['Undo Last Zoom']
        self._menu.setItemVisible(toggle_id, False)
      self.plot.replot()
      return

  def printPlot(self):
    """Sends plots in this window to the printer.
    """
    printer = Qt.QPrinter(Qt.QPrinter.HighResolution)

    printer.setOutputFileName('realvsimag-plot-%s.ps' % Qt.qVersion())

    printer.setOrientation(Qt.QPrinter.Landscape)
    printer.setColorMode(Qt.QPrinter.Color)

    docName = self.plot.title().text()
    if not docName.isEmpty():
        docName.replace(Qt.QRegExp(Qt.QString.fromLatin1('\n')), self.plot.tr(' -- '))
        printer.setDocName(docName)

    dialog = Qt.QPrintDialog(printer)
    if dialog.exec_():
        filter = printfilter_qt4.PrintFilter()
        if (Qt.QPrinter.GrayScale == printer.colorMode()):
            filter.setOptions(
                Qwt.QwtPlotPrintFilter.PrintAll
                & ~Qwt.QwtPlotPrintFilter.PrintBackground
                | Qwt.QwtPlotPrintFilter.PrintFrameWithScales)
            filter.setOptions(Qwt.QwtPlotPrintFilter.PrintAll)
            self.plot.print_(printer, filter)
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
    app = Qt.QApplication(args)
    demo = make()
    app.exec_()

# main()

def make():
    demo = realvsimag_plotter('plot_key')
    demo.start_timer(1000)
    demo.plot.show()
    return demo

# make()

# Admire!
if __name__ == '__main__':
    main(sys.argv)

