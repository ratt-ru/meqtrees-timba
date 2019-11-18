# -*- coding: utf-8 -*-
#/usr/bin/env python

#% $Id: display_image.py 6838 2009-03-08 06:21:51Z twillis $ 

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
#  (c) 2013.                                 (c) 2011.
#  National Research Council                 Conseil national de recherches
#  Ottawa, Canada, K1A 0R6                  Ottawa, Canada, K1A 0R6
#
#  This software is free software;         Ce logiciel est libre, vous
#  you can redistribute it and/or         pouvez le redistribuer et/ou le
#  modify it under the terms of                 modifier selon les termes de la
#  the GNU General Public License         Licence Publique Generale GNU
#  as published by the Free                 publiee par la Free Software
#  Software Foundation; either                  Foundation (version 3 ou bien
#  version 2 of the License, or                  toute autre version ulterieure
#  (at your option) any later                  choisie par vous).
#  version.
#
#  This software is distributed in         Ce logiciel est distribue car
#  the hope that it will be                 potentiellement utile, mais
#  useful, but WITHOUT ANY                 SANS AUCUNE GARANTIE, ni
#  WARRANTY; without even the                  explicite ni implicite, y
#  implied warranty of                         compris les garanties de
#  MERCHANTABILITY or FITNESS FOR         commercialisation ou
#  A PARTICULAR PURPOSE.  See the         d'adaptation dans un but
#  GNU General Public License for         specifique. Reportez-vous a la
#  more details.                         Licence Publique Generale GNU
#                                           pour plus de details.
#
#  You should have received a copy         Vous devez avoir recu une copie
#  of the GNU General Public                 de la Licence Publique Generale
#  License along with this                 GNU en meme temps que ce
#  software; if not, contact the         logiciel ; si ce n'est pas le
#  Free Software Foundation, Inc.         cas, communiquez avec la Free
#  at http://www.fsf.org.                 Software Foundation, Inc. au
#                                                 http://www.fsf.org.
#
#  email:                                 courriel:
#  business@hia-iha.nrc-cnrc.gc.ca         business@hia-iha.nrc-cnrc.gc.ca
#
#  National Research Council                 Conseil national de recherches
#      Canada                                    Canada
#  Herzberg Institute of Astrophysics         Institut Herzberg d'astrophysique
#  5071 West Saanich Rd.                 5071 West Saanich Rd.
#  Victoria BC V9E 2E7                         Victoria BC V9E 2E7
#  CANADA                                         CANADA
#
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys
import random
import traceback
import numpy
import math



from qwt.qt.QtGui import (QApplication, QDialog, QGridLayout,QHBoxLayout,QToolTip,QPrinter,QPrintDialog, QFrame,
         QLabel, QSizePolicy, QSlider, QPushButton, QVBoxLayout, QSpinBox, QSpacerItem)
from qwt.qt.QtGui import QBrush, QPen, QColor,QWidget, QImage, qRgba, QFont, QFontInfo, QMenu, QActionGroup, QAction, QMessageBox, QBrush
from qwt.qt.QtCore import Qt, QSize, QObject, pyqtSignal, QTimer, QPoint
from qwt import (QwtPlot, QwtPlotMarker, QwtPlotGrid, QwtPlotCurve,QwtPlotRenderer,
                 QwtPlotItem, QwtText, QwtLinearColorMap, QwtSymbol,
                 QwtInterval, QwtScaleMap, QwtScaleDraw, QwtScaleDiv, toQImage)
from qwt import  QwtLogScaleEngine, QwtLinearScaleEngine



HAS_TIMBA = False
try:
  from Timba.GUI.pixmaps import pixmaps
  from Timba.Plugins.QwtSpy_qt5 import Spy
  from Timba.Plugins.ComplexScaleDraw_qt5 import ComplexScaleDraw
  from Timba.Plugins.QwtPlotCurveSizes_qt5 import QwtPlotCurveSizes
  from Timba.Plugins.QwtPlotImage_qt5 import QwtPlotImage
  from Timba.Plugins.VellsTree_qt5 import VellsView, VellsElement
  from Timba.utils import verbosity
  _dbg = verbosity(0,name='displayimage');
  _dprint = _dbg.dprint;
  _dprintf = _dbg.dprintf;
  HAS_TIMBA = True
except:
  pass
 
global has_vtk
has_vtk = False

def linearX(nx, ny):
    return repeat(numpy.arange(nx, typecode = numpy.float32)[:, numpy.newaxis], ny, -1)

def linearY(nx, ny):
    return repeat(numpy.arange(ny, typecode = numpy.float32)[numpy.newaxis, :], nx, 0)

def rectangle(nx, ny, scale):
    # swap axes in the fromfunction call
    s = scale//(nx+ny)
    x0 = nx//2
    y0 = ny//2
    
    def test(y, x):
        return cos(s*(x-x0))*sin(s*(y-y0))

    result = numpy.fromfunction(test, (ny, nx))
    return result

#  distance from (5,5) squared
def dist(x,y):
  return (x-15)**2+(y-5)**2  
def imag_dist(x,y):
  return (x-10)**2+(y-10)**2  
def RealDist(x,y):
  return (x)**2  
def ImagDist(x,y):
  return (x-29)**2  
#m = numpy.fromfunction(dist, (10,10))


    
display_image_instructions = \
'''This plot basically shows the contents of one or two-dimensional arrays. Most decision making takes place behind the scenes, so to speak, as the system uses the dimensionality of the data and the source of the data to decide how the data will be displayed. However, once a display appears, you can interact with it in certain standardized ways.<br><br>
Button 1 (Left): If you click the <b>left</b> mouse button on a location inside a two-dimensional array plot, the x and y coordinates of this location, and its value, will appear near the position of the cursor. This information is shown until you release the mouse button. If you click the left mouse button down and then drag it, a rectangular square will be seen. Then when you release the left mouse button, the plot will 'zoom in' on the area defined inside the rectangle.<br><br>
Button 2 (Middle): If you click the <b>middle</b> mouse button on a location inside a <b>two-dimensional</b> array plot, then X and Y cross-sections centred on this location are overlaid on the display. A continuous black line marks the location of the X cross-section and the black dotted line shows the cross section values, which are tied to the right hand scale for real numbers. In the case of an X-axis display of complex numbers the real or amplitude scale is shown in the left hand scale and imaginary or phase values are shown in the right hand scale. The white lines show corresponding information for the Y cross section, whose values are tied to the top scale of the plot. You can remove the X,Y cross sections from the display by selecting the appropriate option from the context menu (see Button 3 below). If the <b>Legends</b> display has been selected to ON,  then a supplementary window will appear on the right hand side of the display giving more details about the symbols used in individual plots.<br><br>
Button 3 (Right):Click the <b>right</b> mouse button in a display window to get a context menu with many options. If you click on the 'Reset zoomer' icon  in a window where you had zoomed in on a selected region, then the original entire array is re-displayed. Data sets may contain multiple arrays. Only one of these arrays can be displayed at any one time. If additional data are available for viewing then a <b>Data element selector</b> option will appear. Selecting this option will cause a small Element selector widget to pop up and show the data elements you can select. If you are working with two-dimensional arrays, then additional options to toggle the ON or OFF display of a colorbar showing the range of intensities and to switch between GrayScale and Color representations of the pixels will be shown. If you have switched on the cross-section display in a complex-valued data set, then a <b>Plot which cross-sections</b> option will be present. This option allows you to select which sub component of complex data is displayed.  The <b>Rotate axes 90deg counterclockwise</b> option is meant to be used mainly for image displays where the axes are the L and M direction cosines. The MeqTrees array handler orients the L axis in the vertical direction and the M axis in the horizontal direction. This option will turn the display so that it is placed in the usual astronomical orientation. (Note that there is an unsolved bug that may be cause part of the display to be blacked out if non-square arrays are rotated).  The meanings of other options in the context menu are hopefully fairly obvious.<br><br>
By default, colorbars are turned ON while Legends are turned OFF when a plot is first produced. <br><br> 
You can obtain more information about the behavior of the colorbar by using the QWhatsThis facility associated with the colorbar.'''

chi_sq_instructions = \
'''This plot shows three different chi_square surface tracks. The red plot shows the norm of the vector sum of the incremental solutions from 1 to i,  the blue plot shows the the sum of the norms of the incremental solutions from 1 to i and the green plot shows the norm of incremental solution i. Once a display appears, you can interact with it in certain standardized ways.<br><br>
Button 1 (Left): If you click the <b>left</b> mouse button on a location inside the plot, and do not move the mouse, a pop-up window appears that gives all the solver metrics for the nearest point in the display. If you click the left mouse button down and then drag it, a rectangular square will be seen. Then when you release the left mouse button, the plot will 'zoom in' on the area defined inside the rectangle.<br><br>
Button 3 (Right):Click the <b>right</b> mouse button in the window to get a context menu with options for printing, resetting the zoom, toggling a <b>Legends</b> display or returning to the incremental solutions display. If you select the 'Reset zoomer' option in a window where you had zoomed in on a selected region, then the original display reappears. If you select the Print option from the menu, the standard Qt printer widget will appear. That widget will enable you print out a copy of your plot, or save the plot in Postscript format to a file. By default a <b>Legends</b> display associated with the three curves is not displayed. You can toggle the <b>Legends</b> display ON or OFF by selecting the Toggle Plot Legend option from the context menu.''' 

class QwtImageDisplay(QwtPlot):
    """ A general purpose class to plot data arrays. The arrays can
        be of any dimension (>= 1). If the dimension is greater than
        two, selection is employed to display a 2-dimensional
        sub-array on the screen.
    """
    max_image_range = pyqtSignal('PyQt_PyObject', int, bool,bool)
    show_colorbar_display = pyqtSignal(int,int)
    winpaused = pyqtSignal(bool)
    compare = pyqtSignal(bool)
    display_type = pyqtSignal(str)
    colorbar_needed = pyqtSignal(int)
    save_display = pyqtSignal(str)
    handle_menu_id = pyqtSignal('PyQt_PyObject')
    handle_spectrum_menu_id = pyqtSignal(int)
    show_ND_Controller = pyqtSignal(int)
    show_3D_Display = pyqtSignal(int)
    show_results_selector = pyqtSignal(bool)
    full_vells_image = pyqtSignal(bool)
    itemAttached =  pyqtSignal('PyQt_PyObject',bool)

    display_table = {
        'hippo': 'hippo',
        'grayscale': 'grayscale',
        'brentjens': 'brentjens',
        }

    menu_table = {
        'show flagged data for plane ': 200,
        'blink flagged data for plane ': 201,
        'Set display range to that of unflagged data for plane ': 202,
        'Modify Plot Parameters': 299,
        'Toggle Plot Legend': 300,
        'Show ColorBar': 301,
        'Show GrayScale Display': 302,
        'Hide ND Controller': 303, 
        'Reset zoomer': 304,
        'Delete X-Section Display': 305,
        'Toggle real/imag or ampl/phase Display': 306,
        'Interchange axes': 307,
        'Show logarithmic range for data': 308,
        'Show results history': 309,
        'Toggle Metrics Display': 310,
        'Show logarithmic range for chi_0': 311,
        'Show logarithmic range for solution vector': 312,
        'Toggle chi-square surfaces display': 313,
        'Change Vells': 314,
        'Toggle 3D Display': 315,
        'Toggle Warp Display': 316,
        'Toggle Pause': 317,
        'Toggle Comparison': 318,
        'Drag Amplitude Scale': 319,
        'Undo Last Zoom': 320,
        'Save Display in pdf Format': 321,
        'Select X-Section Display': 322,
        'Show Full Data Range': 323,
        'Toggle axis rotate': 324,
        'Show coordinate tracking display': 325,
        }

    xsection_menu_table = {
        'Select imaginary cross-section': 200,
        'Select real cross-section': 201,
        'Select amplitude cross-section': 202,
        'Select phase cross-section': 203,
        'Select both cross-sections': 204,
        }

    complex_menu_table = {
        'Show Data as Amplitude and Phase': 400,
        'Show Data as Real and Imaginary': 401,
        }


    _start_spectrum_menu_id = 0

    def __init__(self, parent=None):
        QwtPlot.__init__(self, parent)
        self.parent = parent
        self._mainwin = parent and parent.topLevelWidget();

# a relic from the past which we have to keep for the moment
        self.plot_key = 'spectra'


# set default display type to 'hippo'
        self._display_type = None

        self._vells_plot = False
        self._flags_array = None
        self._nan_flags_array = None
        self.flag_toggle = None
        self.flag_blink = False
        self.full_data_range = False
        self._zoom_display = False
        self._do_pause = False
        self._compare_max = False

        self.solver_display = None
        self.x_array = None
        self.y_array = None
        self.x_index = None
        self._x_title = None
        self._y_title = None
        self._window_title = None
        self._x_auto_scale = True
        self._y_auto_scale = True
        self.axis_xmin = None
        self.axis_xmax = None
        self.axis_ymin = None
        self.axis_ymax = None
        self.previous_shape = None
        self._menu = None
        self.menu_labels_big = None
        self._vells_menu = self._vells_menu_window = None
        self.num_possible_ND_axes = None
        self._plot_type = None
        self.colorbar_requested = False
        self.is_combined_image = False
        self.active_image_index = None
        self.y_marker_step = None
        self.imag_flag_vector = None
        self.real_flag_vector = None
        self.real_xsection_selected = True
        self.imag_xsection_selected = True
        self.array_parms = None
        self.metrics_rank = None
        self.solver_offsets = None
        self.condition_numbers = None
        self.CN_chi = None
        self.chi_vectors = None
        self.eigenvectors = None
        self.sum_incr_soln_norm = None
        self.incr_soln_norm = None
        self.chi_zeros = None
        self.iteration_number = None
        self.solver_labels = None
        self.scalar_display = False
        self.ampl_phase = False
        self.log_switch_set = False
        self._active_perturb = None
        self.first_axis_inc = None
        self.second_axis_inc = None
        self.x_arrayloc = None
        self.y_arrayloc = None
        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None
        self.xsect_xpos = None
        self.xsect_ypos = None
        self.zoomState = None
        self.split_axis = None
        self.adjust_color_bar = True
        self.toggle_metrics = True
        self.array_selector = None
        self.original_flag_array = None
        self.show_x_sections = False
        self.show_coordinates = False
        self.flag_range = True
        self.axes_flip = False
        self.axes_rotate = False
        self.setResults = True
        self.y_solver_offset = []
        self.metrics_plot = {}
        self.chis_plot = {}
        # make a QwtPlot widget
        self.plotLayout().setCanvasMargin(0)
        self.plotLayout().setAlignCanvasToScales(1)
#       self.setTitle('QwtImageDisplay')

        self.label = ''
        self.vells_menu_items = 0
        self.zooming = True
        self.log_offset = 0.0
        self.current_width = 0

        # set fonts for titles
        # first create copy of standard application font..
        self.title_font = QFont(QApplication.font())
        fi = QFontInfo(self.title_font);
        # and scale it down to 70%
        self.title_font.setPointSize(fi.pointSize()*0.7);
        self.xBottom_title = QwtText('Array/Channel Number')
        self.xBottom_title.setFont(self.title_font)
        self.yLeft_title = QwtText('Array/Sequence Number')
        self.yLeft_title.setFont(self.title_font)
        self.xTop_title = QwtText('Array/Channel Number')
        self.xTop_title.setFont(self.title_font)
        self.yRight_title = QwtText(' ')
        self.yRight_title.setFont(self.title_font)
        self.plot_title = QwtText('  ')
        self.plot_title.setFont(self.title_font)

        self.setAxisTitle(QwtPlot.xBottom, self.xBottom_title)
        self.setAxisTitle(QwtPlot.yLeft, self.yLeft_title)

# set fonts for scales
        self.x_bottom_scale = self.axisWidget(QwtPlot.xBottom)
        self.x_bottom_scale.setFont(self.title_font)
        self.x_top_scale = self.axisWidget(QwtPlot.xTop)
        self.x_top_scale.setFont(self.title_font)
        self.y_left_scale = self.axisWidget(QwtPlot.yLeft)
        self.y_left_scale.setFont(self.title_font)
        self.y_right_scale = self.axisWidget(QwtPlot.yRight)
        self.y_right_scale.setFont(self.title_font)

        self.enableAxis(QwtPlot.yRight, False)
        self.enableAxis(QwtPlot.xTop, False)
        self.xrCrossSection = None
        self.xrCrossSection_flag = None
        self.xiCrossSection = None
        self.yCrossSection = None
        self.yCrossSection_flag = None
        self.myXScale = None
        self.myYScale = None
        self.active_image = False
        self.info_marker = None
        self.log_marker = None
        self.source_marker = None
        self.array_tuple = None

        self.plotImage = QwtPlotImage(self)
        self.plotImage.attach(self)

        self.zoomStack = []
        self.xzoom_loc = None
        self.yzoom_loc = None

    # create a grid
        self.grid = QwtPlotGrid()
        self.grid.setPen(QPen(Qt.black, 0, Qt.DotLine))
    

    # create Spy object to track mouse events 
        self.spy = Spy(self.canvas())
        self.prev_xpos = None
        self.prev_ypos = None
        self.zoom_outline = QwtPlotCurve()


        self.spy.MouseMove.connect(self.setPosition)
        self.spy.MousePress.connect(self.onMousePressed)
        self.spy.MouseRelease.connect(self.onMouseReleased)

        self.mouse_pressed = False
        self.index = 1
        self.is_vector = False
        self.old_plot_data_rank = -1
        self.xpos = 0
        self.ypos = 0
        self.complex_type = False
        self.original_data_rank = 1
        self.toggle_color_bar = 1
        self.toggle_ND_Controller = 1
        self.toggle_log_display = False
        self.toggle_gray_scale = 0
        self._toggle_flag_label = None
        self._toggle_blink_label = None
        self._drag_amplitude_scale = False
        self._vells_menu_data = None
        self.has_nans_infs = False
#       self.nan_inf_value = -32767.0
        self.nan_inf_value = -0.1e-6

        self.first_chi_test = True
        self.log_axis_chi_0 = False
        self.log_axis_solution_vector = False
        self.display_solution_distances = False
        self.store_solver_array = False
        self.curve_info = ""
        self.curves = {}
        self.markers = {}
        self.curve_data = {}
        self.metrics_index = 0

        self.setWhatsThis(display_image_instructions)

# Finally, over-ride default QWT Plot size policy of MinimumExpanding
# Otherwise minimum size of plots is too large when embedded in a
# QGridlayout
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

# set up pop up text
        self.white = QColor(255,255,255)
        font = QFont("Helvetica",10)
        self._popup_text = QLabel(self)
        self._popup_text.setFont(font)
        self._popup_text.setStyleSheet("QWidget { background-color: %s }" % self.white.name())
        self._popup_text.setFrameStyle(QFrame.Box | QFrame.Plain)
        # start the text off hidden at 0,0
        self._popup_text.hide()

# for drag & drop stuff ...
        self.setAcceptDrops(True)

#       self.__init__

    def toggleVisibility(self, plotItem):
        """Toggle the visibility of a plot item
        """
        plotItem.setVisible(not plotItem.isVisible())
        self.replot()

    # toggleVisibility()


    def dragEnterEvent(self, event):
      """ drag & drop event callback entered when we move out of or
          in to a widget
      """
      try:
        if event.mimeData().hasText():
          event.acceptProposedAction()
      except:
        pass


    def dropEvent(self, event):
        """ callback that handles a drop event from drag & drop """
        if event.source() == self:
          return
        if event.mimeData().hasText():
          command_str = str(event.mimeData().text())
          if command_str.find('copyPlotParms') > -1:
            parms = event.source().getPlotParms();
            self.setPlotParms(parms,True)
        else:
          message= 'QwtImageDisplay dropEvent decode failure'
          mb_reporter = QMessageBox.information(self, "QwtImageDisplay", message)

    def startDrag(self):
      """ operations done when we start a drag event """
      drag = Qt.QDrag(self)
      mimedata = Qt.QMimeData()
      passed_string = 'copyPlotParms'
      mimedata.setText(passed_string)
      drag.setMimeData(mimedata)
      drag.exec_()
      event.accept()
    
    def clear_metrics(self):
#       self.detachItems(QwtPlotItem.Rtti_PlotItem,True)
#       self.detachItems(QwtPlotItem.Rtti_PlotMarker,True)
        keys = list(self.metrics_plot.keys())
        if len(keys) > 0:
          for key in keys:
            self.metrics_plot[key].detach()
        self.y_solver_offset = []
        self.metrics_plot = {}
        self.chis_plot = {}

    def setZoomDisplay(self):
      self._zoom_display = True

    def setFlagColour(self, flag_colour):
      self.plotImage.setFlagColour(flag_colour)

    def getPlotParms(self):
        """ Obtain current plot parameters for modification """
        plot_parms = {}
        if self._window_title is None:
          plot_parms['window_title'] = 'window title'
        else:
          plot_parms['window_title'] = self._window_title
        if self._x_title is None:
          plot_parms['x_title'] = 'x_title'
        else:
          plot_parms['x_title'] = self._x_title
        if self._y_title is None:
          plot_parms['y_title'] = 'y_title'
        else:
          plot_parms['y_title'] = self._y_title
        plot_parms['x_auto_scale'] = self._x_auto_scale
        plot_parms['y_auto_scale'] = self._y_auto_scale
        plot_parms['axis_xmin'] = self.axis_xmin
        plot_parms['axis_xmax'] = self.axis_xmax
        plot_parms['axis_ymin'] = self.axis_ymin
        plot_parms['axis_ymax'] = self.axis_ymax
     
        return plot_parms

    def setPlotParms(self, plot_parms,copy_axes=False):
        """ Set modified plot parameters """
        if not copy_axes: 
          self._window_title = plot_parms['window_title'] 
          self._x_title = plot_parms['x_title']
          self._y_title = plot_parms['y_title'] 

          self.xBottom_title.setText(self._x_title)
          self.yLeft_title.setText(self._y_title)
          self.setAxisTitle(QwtPlot.xBottom, self.xBottom_title)
          self.setAxisTitle(QwtPlot.yLeft, self.yLeft_title)
          self.plot_title.setText(self._window_title)
          self.setTitle(self.plot_title)

        if self.zoomStack == []:
          try:
                self.zoomState = (
                    self.axisScaleDiv(QwtPlot.xBottom).lBound(),
                    self.axisScaleDiv(QwtPlot.xBottom).hBound(),
                    self.axisScaleDiv(QwtPlot.yLeft).lBound(),
                    self.axisScaleDiv(QwtPlot.yLeft).hBound(), True
                    )
          except:
                self.zoomState = (
                    self.axisScaleDiv(QwtPlot.xBottom).lowerBound(),
                    self.axisScaleDiv(QwtPlot.xBottom).upperBound(),
                    self.axisScaleDiv(QwtPlot.yLeft).lowerBound(),
                    self.axisScaleDiv(QwtPlot.yLeft).upperBound(), True
                    )
        self.zoomStack.append(self.zoomState)
        self._x_auto_scale = plot_parms['x_auto_scale']
        self._y_auto_scale = plot_parms['y_auto_scale']
        if self._x_auto_scale == '0':
          self._x_auto_scale = False
        if self._x_auto_scale == '1':
          self._x_auto_scale = True
        if self._y_auto_scale == '0':
          self._y_auto_scale = False
        if self._y_auto_scale == '1':
          self._y_auto_scale = True
        display_zoom_menu = False
        if not self._x_auto_scale: 
          if float(plot_parms['axis_xmin']) > self.zoomStack[0][0] or float(plot_parms['axis_xmax']) < self.zoomStack[0][1]:
            self.axis_xmin = float(plot_parms['axis_xmin'])
            self.axis_xmax = float(plot_parms['axis_xmax'])
            display_zoom_menu = True
          else:
            self.axis_xmin =  self.zoomStack[0][0]
            self.axis_xmax =  self.zoomStack[0][1]
          self.setAxisScale(QwtPlot.xBottom, self.axis_xmin, self.axis_xmax)
          if not self.is_vector:
            self.plotImage.update_xMap_draw(self.axis_xmin,self.axis_xmax)
        else:
          self.setAxisAutoScale(QwtPlot.xBottom)
        if not self._y_auto_scale: 
          if float(plot_parms['axis_ymin']) > self.zoomStack[0][2] or float(plot_parms['axis_ymax']) < self.zoomStack[0][3]:
            self.axis_ymin = float(plot_parms['axis_ymin'])
            self.axis_ymax = float(plot_parms['axis_ymax'])
            display_zoom_menu = True
          else:
            self.axis_ymin =  self.zoomStack[0][2]
            self.axis_ymax =  self.zoomStack[0][3]
          self.setAxisScale(QwtPlot.yLeft, self.axis_ymin, self.axis_ymax)
          if not self.is_vector:
            self.plotImage.update_yMap_draw(self.axis_ymin,self.axis_ymax)
        else:
          self.setAxisAutoScale(QwtPlot.yLeft)
        if display_zoom_menu:
          self.zoomState = (self.axis_xmin, self.axis_xmax, self.axis_ymin, self.axis_ymax, True)
          self._reset_zoomer.setVisible(True)
          if self.is_vector and self.complex_type:
            self._undo_last_zoom.setVisible(False)
          else:
            self._undo_last_zoom.setVisible(True)
        else:
          self._reset_zoomer.setVisible(False)
          self._undo_last_zoom.setVisible(False)
        self.replot()
        #print'called replot in setPlotParms'
        if HAS_TIMBA:_dprint(3, 'called replot in setPlotParms')

    def initSpectrumContextMenu(self):
        """Initialize the spectrum context menu """
        # skip if no main window
        if not self._mainwin:
          return;

        if self._menu is None:
          self._menu = QMenu(self._mainwin);
          self.add_basic_menu_items()
#         self.connect(self._menu,Qt.SIGNAL("activated(int)"),self.update_spectrum_display);
#         self.connect(self._menu,Qt.SIGNAL("triggered(QAction)"),self.update_spectrum_display);
          self._menu.triggered.connect(self.update_spectrum_display)
          self.spectrum_menu_items = 0

        if self.spectrum_menu_items > 1:
         menu_id = self._start_spectrum_menu_id
         for i in range(self.spectrum_menu_items):
           self._menu.removeItem(menu_id)
           menu_id = menu_id + 1

    def delete_cross_sections(self):
      """ delete any displayed cross section plots """
      if self.show_x_sections:
# delete any previous curves
        self.removeCurves()
        self.removeMarkers()
        self.xrCrossSection = None
        self.xrCrossSection_flag = None
        self.xiCrossSection = None
        self.yCrossSection = None
        self.x_index = None
        self.x_arrayloc = None
        self.y_arrayloc = None
        self.enableAxis(QwtPlot.yRight, False)
        self.enableAxis(QwtPlot.xTop, False)
        self.xsect_xpos = None
        self.xsect_ypos = None
        self.show_x_sections = False
        self._delete_x_section_display.setVisible(False)
        self._delete_cx_section_display.setVisible(False)
        self._select_x_section_display.setVisible(False)

# add solver metrics info back in?
        if self.toggle_metrics and not self.metrics_rank is None:
          self.add_solver_metrics()

        if not self.scalar_display:
          self.refresh_marker_display()

    def setResultsSelector(self):
      """ add option to toggle ResultsRange selector to context menu """
      self._toggle_results_history.setVisible(True)
      self._toggle_results_history.setChecked(self.setResults)

    # following function is taken directly from the PythonQwt BodeDemo.py example
    def print_(self):
       printer = QPrinter(QPrinter.HighResolution)

       printer.setCreator('plotting example')
       printer.setOrientation(QPrinter.Landscape)
       printer.setColorMode(QPrinter.Color)

       if self._window_title is None:
          docName = 'plot_display'
       else:
          docName = self._window_title 

       if not docName:
           docName.replace('\n', ' -- ')

       printer.setDocName(docName)
       dialog = QPrintDialog(printer)
       if dialog.exec_():
           renderer = QwtPlotRenderer()
           if (QPrinter.GrayScale == printer.colorMode()):
               renderer.setDiscardFlag(QwtPlotRenderer.DiscardBackground)
               renderer.setDiscardFlag(QwtPlotRenderer.DiscardCanvasBackground)
               renderer.setDiscardFlag(QwtPlotRenderer.DiscardCanvasFrame)
               renderer.setLayoutFlag(QwtPlotRenderer.FrameWithScales)
           renderer.renderTo(self, printer)

    def handle_basic_menu_id(self):
      """ callback to handle most common basic context menu selections """
# should not be any such menuid that we need to handle here
# (print signal is handled by printplot function) so ignore
#     print('in handle basic menu')
      action = QObject.sender(self)
      try:
        result, flag = action.data().toInt()
      except:
        pass

    def toggleMetrics(self):
      """ callback to make Solver Metrics plots visible or invisible """
      self.clear_metrics()
      if self.toggle_metrics and not self.metrics_rank is None:
        self.add_solver_metrics()

# toggle flags display        
    def handle_toggle_flagged_data_for_plane(self):
      self.handleFlagToggle(self.flag_toggle)
      # this has really become convoluted
      if self.is_vector:
        self._toggle_flagged_data_for_plane.setChecked(True)
      else:
        self._toggle_flagged_data_for_plane.setChecked(not self.flag_toggle)
      self.replot()

    def handle_toggle_blink_of_flagged_data(self):
      """ callback to handle or modify displays of flagged data """
      if self.flag_blink == False:
        self.flag_blink = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerEvent_blink)
        self.timer.start(2000)
      else:
        self.flag_blink = False
      self._toggle_blink_of_flagged_data.setChecked(self.flag_blink)

    def handle_set_display_range_to_unflagged_data(self):
      if self.flag_range:
        self.setFlagRange(False)
      else:
        self.setFlagRange(True)
      self._set_display_range_to_unflagged_data.setChecked(self.flag_range)
      self.handleFlagRange()

    def handleFlagToggle(self, flag_toggle):
      """ callback to make flagged data visible or invisible """
      if flag_toggle == False:
        self.flag_toggle = True
      else:
        self.flag_toggle = False
      if self.real_flag_vector is None:
        if self.show_x_sections:
          self.calculate_cross_sections()
        self.plotImage.setDisplayFlag(self.flag_toggle)
      else:
        self.real_flag_vector.setVisible(self.flag_toggle)
        if not self.imag_flag_vector is None:
          self.imag_flag_vector.setVisible(self.flag_toggle)
        if not self.yCrossSection_flag is None:
          self.yCrossSection_flag.setVisible(self.flag_toggle)
        if not self.xrCrossSection_flag is None:
          self.xrCrossSection_flag.setVisible(self.flag_toggle)
        if not self.yCrossSection is None:
          if self.flag_toggle:
            self.yCrossSection.setVisible(False)
          else:
            self.yCrossSection.setVisible(True)
        if not self.xrCrossSection is None:
          if self.flag_toggle:
            self.xrCrossSection.setVisible(False)
          else:
            self.xrCrossSection.setVisible(True)

    def setFlagRange(self,flag_range=True):
      """ callback to adjust flag_range """
      self.flag_range = flag_range
      return

    def handleFlagRange(self):
      """ callback to adjust display range of flagged data """
      if self.is_vector:
        return
      if self._flags_array is None and self._nan_flags_array is None:
        self.replot()
        #print 'called replot in handleFlagRange'
        return
      if self.flag_range:
        self.plotImage.setFlaggedImageRange()
        self.plotImage.updateImage(self.raw_image)
        flag_image_limits = self.plotImage.getRealImageRange()
        self.max_image_range.emit(flag_image_limits, 0, self.toggle_log_display,self.ampl_phase)
        if self.complex_type:
          flag_image_limits = self.plotImage.getImagImageRange()
          self.max_image_range.emit(flag_image_limits, 1, self.toggle_log_display,self.ampl_phase)
      else:
        self.plotImage.setImageRange(self.raw_image)
        self.plotImage.updateImage(self.raw_image)
        image_limits = self.plotImage.getRealImageRange()
        self.max_image_range.emit(image_limits, 0, self.toggle_log_display,self.ampl_phase)
        if self.complex_type:
          image_limits = self.plotImage.getImagImageRange()
          self.max_image_range.emit(image_limits, 1, self.toggle_log_display,self.ampl_phase)
      # finally, replot
      self.replot()
      #print 'called second replot in handleFlagRange'

    def setAxisParms(self, axis_parms):
      self.first_axis_parm = axis_parms[0]
      self.second_axis_parm = axis_parms[1]
      if HAS_TIMBA:_dprint(3, 'axis parms set to ', self.first_axis_parm, ' ', self.second_axis_parm)

    def set_condition_numbers(self, numbers):
      """ set covariance matrix condition numbers """
      self.condition_numbers = numbers[0]
      self.CN_chi = numbers[1]

    def set_eigenvectors(self, eigens):
      """ store eigenvalues and eigenvectors from the covariance matrix """
      self.eigenvectors = eigens

    def set_solver_labels(self, labels):
      """ set solver labels for display reporting """
      self.solver_labels = labels


    def update_spectrum_display(self, menuid):
      """ callback to handle signal from SpectrumContextMenu """
      if self.handle_basic_menu_id():
        return

      if self.is_combined_image:
        self.removeMarkers()
        self.info_marker = None
        self.log_marker = None
        self.source_marker = None
        self.is_combined_image = False

# if we got here, emit signal up to result_plotter 
# NOTE: for python3/Qwt6 we see to get here in ways I do NOT understand
# and I handle this with an exception. Maybe some day I'll figure this out :) 
      try:
# menuid is a python object in python3  so how can I be doing 
# arithmetic on it? # how did this ever work in python2?
        menuid = self.spectrum_menu_items - 1 - menuid
        self.handle_spectrum_menu_id.emit(menuid)
      except:
        return 
#       traceback.print_exc();

    def set_flag_toggles(self, flag_plane=None, flag_setting=False):
      """ creates context menus for selecting flagged Vells data """
      if flag_plane is None:
        self._toggle_flagged_data_for_plane.setText(self._toggle_flag_label)
        self._toggle_blink_of_flagged_data.setText(self._toggle_blink_label)
        self._set_display_range_to_unflagged_data.setText(self._toggle_range_label)
      else:
        self._toggle_flagged_data_for_plane.setText(self._toggle_flag_label+str(flag_plane))
        self._toggle_blink_of_flagged_data.setText(self._toggle_blink_label+str(flag_plane))
        self._set_display_range_to_unflagged_data.setText(self._toggle_range_label+str(flag_plane))

      self._toggle_flagged_data_for_plane.setEnabled(flag_setting)
      self._toggle_flagged_data_for_plane.setVisible(flag_setting)

      self._toggle_blink_of_flagged_data.setEnabled(flag_setting)
      self._toggle_blink_of_flagged_data.setVisible(flag_setting)

      self._set_display_range_to_unflagged_data.setEnabled(flag_setting)
      self._set_display_range_to_unflagged_data.setVisible(flag_setting)
      self._set_display_range_to_unflagged_data.setChecked(self.flag_range)

    def set_flag_toggles_active(self, flag_setting=False,image_display=True):
      """ sets menu options for flagging to visible """
# add flag toggling for vells but make hidden by default
      toggle_flag_label = "show flagged data for plane "
      if self.has_nans_infs and self.is_vector == False:
        info_label = "Flagged data has NaNs or Infs and cannot be shown explicitly"
        self._toggle_flagged_data_for_plane.setText(info_label)
        self._toggle_flagged_data_for_plane.setEnabled(flag_setting)
        self._toggle_flagged_data_for_plane.setVisible(flag_setting)
      else:
        info_label = toggle_flag_label
        self._toggle_flagged_data_for_plane.setText(info_label)
        self._toggle_flagged_data_for_plane.setEnabled(flag_setting)
        self._toggle_flagged_data_for_plane.setVisible(flag_setting)
        self._toggle_blink_of_flagged_data.setEnabled(flag_setting)
        self._toggle_blink_of_flagged_data.setVisible(flag_setting)

        if image_display:
          toggle_range_label = "Set display range to that of unflagged data for plane "
          self._set_display_range_to_unflagged_data.setEnabled(flag_setting)
          self._set_display_range_to_unflagged_data.setVisible(flag_setting)
          self._set_display_range_to_unflagged_data.setChecked(self.flag_range)

    def initVellsContextMenu (self):
      """ intitialize context menu for selection of Vells data """
      # skip if no main window
      if not self._mainwin:
        return;
      self.log_switch_set = False
      if self._menu is None:
        self._menu = QMenu(self._mainwin);
#       self.connect(self._menu,Qt.SIGNAL("activated(int)"),self.update_vells_display);
        self._menu.aboutToShow.connect(self.addVellsMenu)
        self.add_basic_menu_items()
    # end initVellsContextMenu()

    def setMenuItems(self, menu_data):
      """ add items specific to selection of Vells to context menu """
      self._vells_menu_data = menu_data
      
    def setBigArrays(self, big_data_index):
      if not big_data_index is None:
        self.menu_labels_big = big_data_index
        keys = list(self.menu_labels_big.keys())
        if len(keys) > 0:
          for i in range(len(keys)):
            if self.menu_labels_big[keys[i]]:
              self._show_full_data_range.setVisible(True)

    def addVellsMenu(self):
      """ add vells options to context menu """
      if self._vells_menu_data is None:
        return
      if not self._vells_menu_window is None:
        self._vells_menu_window.setParent(QWidget())
        self._change_vells.setVisible(False)
        self._vells_menu_window = None

      if self._vells_menu_window is None:
        self._vells_menu_window = QDialog(self,Qt.Tool);
        self._vells_menu_window.setWindowTitle("Element selector");
        lo = QVBoxLayout(self._vells_menu_window);
        lo.setContentsMargins(0,0,0,0);
        self._vells_menu = VellsView(self._vells_menu_window);
        lo.addWidget(self._vells_menu);
        self._vells_menu.setRootIsDecorated(False);
        vells_root = VellsElement(self._vells_menu, "Data elements:")
        vells_root.setExpanded(True)
        self._vells_menu.selected_vells_id.connect(self.update_vells_display)
        self._vells_menu_window.hide()
        self._change_vells.setVisible(True)
        self._show_full_data_range.setVisible(False)
      menu_labels = self._vells_menu_data[0]
      perturbations = self._vells_menu_data[1]
      planes_index = self._vells_menu_data[2]
      menu_dims = self._vells_menu_data[3]
      vells_menu_items = len(menu_labels)
      num_planes = len(planes_index)
      previous = None
      if vells_menu_items > 1:
        menu_step = 40
        menu_vells_inc = 10
        menu_delta = 1
        if not menu_dims is None:
          length = len(menu_dims)
          if length > 2:
            menu_delta = menu_dims[length-2] * menu_dims[length-1] 
            menu_step = menu_vells_inc * menu_delta 
        if num_planes < menu_step:
          previous = None
          for i in range(num_planes):
            id = planes_index[i]
            if previous is None:
              node = VellsElement(vells_root)
            else:
              node = VellsElement(vells_root)
#             node = VellsElement(vells_root, previous)
            node.setText(0,menu_labels[id])
            node.setKey(id)
            previous = node
            perturbations_key = str(id) + ' perturbations'
            if perturbations_key in perturbations:
              perturbations_index = perturbations[perturbations_key]
              self.createPerturbationsMenu(self._vells_menu,menu_labels,perturbations_index,node) 
            if not self.menu_labels_big is None and id in self.menu_labels_big:
              if self.menu_labels_big[id]:
                self._show_full_data_range.setVisible(True)
              
        else:
          if int(num_planes/menu_step) * menu_step == num_planes:
            num_sub_menus = int(num_planes/menu_step)
          else:
            num_sub_menus = 1 + int(num_planes/menu_step)
          start_range = 0
          end_range = menu_step
          for k in range(num_sub_menus):
            start_str = None
            end_str = None
            for i in range(start_range, end_range):
              id = planes_index[i]
              if start_str is None:
                start_str = menu_labels[id]
            end_str = menu_labels[id]
            menu_string = 'Vells ' + start_str + ' to ' + end_str + '  '
            if previous is None:
              node = VellsElement(vells_root)
            else:
              node = VellsElement(vells_root)
#             node = VellsElement(vells_root, previous)
            node.setText(0,menu_string)
            previous = node
            previous_node = None
            for i in range(start_range, end_range):
              id = planes_index[i]
              if previous_node is None:
                sub_node = VellsElement(node)
              else:
                sub_node = VellsElement(node)
#               sub_node = VellsElement(node, previous_node)
              sub_node.setText(0,menu_labels[id])
              sub_node.setKey(id)
              previous_node = sub_node
              perturbations_key = str(id) + ' perturbations'
              if perturbations_key in perturbations:
                perturbations_index = perturbations[perturbations_key]
                submenu = self.createPerturbationsMenu(self._vells_menu,menu_labels,perturbations_index,sub_node) 
              if not self.menu_labels_big is None and id in self.menu_labels_big:
                if self.menu_labels_big[id]:
                  self._show_full_data_range.setVisible(True)
              
            end_str = menu_labels[id]
            start_range = start_range + menu_step
            end_range = end_range + menu_step
            if end_range > vells_menu_items:
              end_range = vells_menu_items

#     self._vells_menu.show()
# add Vells menu to context menu

    def createPerturbationsMenu(self, parent_menu, menu_labels, perturbations_index,node):
      """ create context menu for selection of perturbations """
      num_perturbs = len(perturbations_index)
      menu_step = 30
      previous = None
      if num_perturbs < menu_step:
        for j in range(len(perturbations_index)):
          id = perturbations_index[j]
          if previous is None:
            pert_node = VellsElement(node)
          else:
            pert_node = VellsElement(node)
#           pert_node = VellsElement(node, previous)
          pert_node.setText(0,menu_labels[id])
          pert_node.setKey(id)
          previous = pert_node
      else:
        if int(num_perturbs/menu_step) * menu_step == num_perturbs:
          num_sub_menus = int(num_perturbs/menu_step)
        else:
          num_sub_menus = 1 + int(num_perturbs/menu_step)
        start_range = 0
        end_range = menu_step
        for k in range(num_sub_menus):
          start_str = str(start_range)
          end_str = str(end_range - 1 )
          menu_string = 'perturbations ' + start_str + ' to ' + end_str + '  '
          if previous is None:
            pert_node = VellsElement(node)
          else:
            pert_node = VellsElement(node)
#           pert_node = VellsElement(node, previous)
          pert_node.setText(0,menu_string)
          previous = pert_node
          prev_node = None
          for j in range(start_range, end_range):
            id = perturbations_index[j]
            if prev_node is None:
              pert_subnode = VellsElement(pert_node)
            else:
              pert_subnode = VellsElement(pert_node)
#             pert_subnode = VellsElement(pert_node, prev_node)
            prev_node = pert_subnode
            pert_subnode.setText(0,menu_labels[id])
            pert_subnode.setKey(id)
          start_range = start_range + menu_step
          end_range = end_range + menu_step
          if end_range > num_perturbs:
            end_range = num_perturbs

    def setSpectrumMenuItems(self, menu_labels):
      """ add items specific to selection of Spectra to context menu """
      self.spectrum_menu_items = len(menu_labels)
      if self.spectrum_menu_items > 1:
        menu_id = self._start_spectrum_menu_id
        menu_index = self.spectrum_menu_items - 1
        for i in range(self.spectrum_menu_items):
          self._menu.insertItem(menu_labels[menu_index], menu_id)
          menu_id = menu_id + 1
          menu_index = menu_index - 1

      self._toggle_axis_flip.setVisible(False)
      self._toggle_axis_rotate.setVisible(False)

    def setSpectrumMarkers(self, marker_parms, marker_labels):
      """ inserts marker lines between 'combined image' spectra """
      if self.spectrum_menu_items > 2: 
        self.num_y_markers = marker_parms[0]
        self.y_marker_step = marker_parms[1]
        labels_length = len(marker_labels)
        labels_index = labels_length -1
        self.marker_labels = []
        for i in range(labels_length):
          self.marker_labels.append(marker_labels[labels_index])
          labels_index = labels_index-1

    def getSpectrumTags(self):
       return (self._data_labels, self._string_tag) 
    
    def reset_zoom(self, replot=False, undo_last_zoom = False):
      """ resets data display so all data are visible """
      do_replot = False
#     self.enableOutline(0) # make sure outline is disabled
      if len(self.zoomStack):
        while len(self.zoomStack):
          axis_parms = self.zoomStack.pop()
          xmin = axis_parms[0]
          xmax = axis_parms[1]
          ymin = axis_parms[2]
          ymax = axis_parms[3]
          self.zoomState = axis_parms
          try:
            do_replot = axis_parms[4]
          except:
            pass
          if len(self.zoomStack) == 0:
            self.zoomState = None
          if undo_last_zoom:
            break
        self.setAxisScale(QwtPlot.xBottom, xmin, xmax)
        self.setAxisScale(QwtPlot.yLeft, ymin, ymax)
        if not self.is_vector:
          self.plotImage.update_xMap_draw(xmin,xmax)
          self.plotImage.update_yMap_draw(ymin,ymax)

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
        self.test_plot_array_sizes()
        if self.show_x_sections:
          self.calculate_cross_sections()
        self.refresh_marker_display()
        if not len (self.zoomStack):
          self._reset_zoomer.setVisible(False)
          self._undo_last_zoom.setVisible(False)
      else:
        self.zoomState = None

# do a complete replot in the following situation
# as both axes will have changed even if nothing to unzoom.
      if do_replot:
        self.replot()
        #print 'called replot in reset_zoom'
    
      if replot:
        self.array_plot(self.complex_image,data_label=self._window_title, flip_axes=False)
      if HAS_TIMBA:_dprint(3, 'exiting reset_zoom')
      return

    def handle_toggle_nd_controller(self):
      if self.toggle_ND_Controller == 1:
        self.toggle_ND_Controller = 0
      else:
        self.toggle_ND_Controller = 1
      self._toggle_nd_controller.setChecked(not self.toggle_ND_Controller)
      self.show_ND_Controller.emit(self.toggle_ND_Controller)

    def handle_toggle_3d_display(self):
      self.show_3D_Display.emit(True)

    def handle_toggle_warp_display(self):
      self.show_3D_Display.emit(False)

    def handle_toggle_results_history(self):
      if self.setResults:
        self.setResults = False
      else:
        self.setResults = True
      self._toggle_results_history.setChecked(self.setResults)
      self.show_results_selector.emit(self.setResults)

    def handle_toggle_metrics_display(self):
      if self.toggle_metrics == False:
        self.toggle_metrics = True
      else:
        self.toggle_metrics = False
      self._toggle_metrics_display.setChecked(self.toggle_metrics)
      self.toggleMetrics()
      self.replot()

    def handle_toggle_log_axis_for_chi_0(self):
      if self.log_axis_chi_0 is False:
        self.log_axis_chi_0 = True
        self._toggle_log_axis_for_chi_0.setChecked(True)
      else:
        self.log_axis_chi_0 = False
        self._toggle_log_axis_for_chi_0.setChecked(False)
      self.clear_metrics()
      self.add_solver_metrics()
      self.test_plot_array_sizes()
      self.replot()

    def handle_toggle_log_axis_for_solution_vector(self):
      if self.log_axis_solution_vector is False:
        self.log_axis_solution_vector = True
        self._toggle_log_axis_for_solution_vector.setChecked(True)
      else:
        self.log_axis_solution_vector = False
        self._toggle_log_axis_for_solution_vector.setChecked(False)
      self.clear_metrics()
      self.add_solver_metrics()
      self.test_plot_array_sizes()
      self.replot()

    def handle_toggle_chi_square_surfaces_display(self):
      if self.display_solution_distances is False:
        self.display_solution_distances = True
        self.setWhatsThis(chi_sq_instructions)
        self._toggle_chi_square_surfaces_display.setText('Show Solver Solutions')
        self._toggle_metrics_display.setVisible(False)
        self._toggle_log_range_for_data.setVisible(False)
        self._toggle_coordinates.setVisible(False)
      else:
        self.display_solution_distances = False
        self.setWhatsThis(display_image_instructions)
        self._toggle_chi_square_surfaces_display.setText('Show chi-square surfaces')
        self._toggle_metrics_display.setVisible(True)
        self._toggle_log_range_for_data.setVisible(False)
        self._toggle_log_range_for_data.setVisible(True)
        self._toggle_coordinates.setVisible(True)
        self.cleanup()
        self.enable_axes()
      self.reset_zoom()
      self.array_plot(self.solver_array,data_label=self.solver_title)
      if not self.display_solution_distances: 
        self.add_solver_metrics()
        self.toggleMetrics()
      self.replot()

    def handle_toggle_pause(self):
      if self._do_pause:
          self._do_pause = False
      else:
          self._do_pause = True
      self._toggle_pause.setChecked(self._do_pause)
      self.winpaused.emit(self._do_pause)

    def handle_toggle_comparison(self):
      if self._compare_max:
        self._compare_max = False
      else:
        self._compare_max = True
      self._toggle_comparison.setChecked(self._compare_max)
      self.compare.emit(self._compare_max)


    def handle_change_vells(self):
      # figure out a good size
      width = 180;
      # count the number of root and second-level items
      nitems = self._vells_menu.topLevelItemCount();
      for i in range(nitems):
        nitems += self._vells_menu.topLevelItem(i).childCount();
      # work out height of one item, and total height based on that
      item_height = self._vells_menu.visualItemRect(self._vells_menu.topLevelItem(0)).height();
      height = item_height*min(nitems,12)+32;
      # set
      self._vells_menu_window.resize(width,height);
      # figure out position for popup
      globalPos = self.mapToGlobal(self.rect().topLeft())
      # seems to put this widget in a good position IMHO
      self._vells_menu_window.move(globalPos - QPoint(0.9*width,0.9*height))
      self._vells_menu_window.show()

    def handle_show_full_data_range(self):
      if self.full_data_range == False:
        self.full_data_range = True
      else:
        self.full_data_range = False
        self.plotImage.setFlagsArray(None)
      self._show_full_data_range.setChecked(self.full_data_range)
      self.full_vells_image.emit(self.full_data_range, )

    def handle_toggle_coordinates(self):
      if self.show_coordinates == False:
        self.show_coordinates = True
      else:
        self.show_coordinates = False
      
      self._toggle_coordinates.setChecked(self.show_coordinates)

    def handle_toggle_axis_flip(self):
      """ sets flag to reverse orientation of image displays """
      if self.axes_flip:
        self.axes_flip = False
      else:
        self.axes_flip = True

# delete any cross sections
      self.delete_cross_sections()

      if self._vells_plot:
        if not self.original_flag_array is None:
          self.setFlagsData (self.original_flag_array)
        self.plot_vells_array(self.original_array, self.original_label)
      if not self._vells_plot and self._plot_type is None:
        self.array_plot(self.original_array,data_label=self.original_label)

      self._toggle_axis_flip.setChecked(self.axes_flip)

    def handle_toggle_axis_rotate(self):
      """ sets flag to rotate image displays by 90 deg counterclockwise"""
      if self.axes_rotate:
        self.axes_rotate = False
      else:
        self.axes_rotate = True

# delete any cross sections
      self.delete_cross_sections()

      if self._vells_plot:
        if not self.original_flag_array is None:
          self.setFlagsData (self.original_flag_array)
        self.plot_vells_array(self.original_array, self.original_label)
      if not self._vells_plot and self._plot_type is None:
        self.array_plot(self.original_array, data_label=self.original_label)
      self._toggle_axis_rotate.setChecked(self.axes_rotate)
      
    def handle_toggle_log_range_for_data(self):
      if self.toggle_log_display == False:
        self.toggle_log_display = True
        self.plotImage.setLogScale()
      else:
        self.toggle_log_display = False
        self.plotImage.setLogScale(False)
        self.plotImage.setImageRange(self.raw_image)
      self._toggle_log_range_for_data.setChecked(self.toggle_log_display)
      self.plotImage.updateImage(self.raw_image)
      image_limits = self.plotImage.getRealImageRange()
      self.max_image_range.emit(image_limits, 0, self.toggle_log_display,self.ampl_phase)
      if self.complex_type:
        image_limits = self.plotImage.getImagImageRange()
        self.max_image_range.emit(image_limits, 1,self.toggle_log_display,self.ampl_phase)
      self.log_offset = 0.0
      if self.toggle_log_display:
        self.log_offset = self.plotImage.getTransformOffset()
      self.insert_array_info()
      if self.show_x_sections:
        self.calculate_cross_sections()
      self.handleFlagRange()

    def handle_toggle_ap_display(self):
      self.ampl_phase = True
      self._select_real_imaginary.setChecked(False)
      self._select_amplitude_phase.setChecked(self.ampl_phase)
      if self._vells_plot and not self.is_vector:
          title_addition = ': (amplitude followed by phase)'
          title = self._x_title = self.vells_axis_parms[self.x_parm][2] + title_addition
      else:
          if self.is_vector:
            title = self._x_title;
          else:
            title = self._x_title + ' (amplitude followed by phase)'
      self.xBottom_title.setText(title)
      self.setAxisTitle(QwtPlot.xBottom, self.xBottom_title)

      if self.is_vector:
        # make sure we unzoom as axes will probably change drastically
        self.reset_zoom(True)
      else:
        self.adjust_color_bar = True
        ampl_phase_image = self.convert_to_AP(self.complex_image)
        self.display_image(ampl_phase_image)
        self.handleFlagRange()

    def handle_toggle_ri_display(self):
      self.ampl_phase = False
      self._select_real_imaginary.setChecked(True)
      self._select_amplitude_phase.setChecked(self.ampl_phase)
      if self._vells_plot and not self.is_vector:
        title_addition = ': (real followed by imaginary)'
        title = self._x_title = self.vells_axis_parms[self.x_parm][2] + title_addition
      else:
        if self.is_vector:
          title = self._x_title;
        else:
          title = self._x_title + ' (real followed by imaginary)'
      self.xBottom_title.setText(title)
      self.setAxisTitle(QwtPlot.xBottom, self.xBottom_title)

      if self.is_vector:
        # make sure we unzoom as axes will probably change drastically
        self.reset_zoom(True)
      else:
        self.adjust_color_bar = True
        self.display_image(self.complex_image)
        self.handleFlagRange()

    def handle_delete_x_section_display(self):
        self.delete_cross_sections()

    def handle_toggle_colorbar(self):
      if self.toggle_color_bar == 1:
        self.toggle_color_bar = 0
      else:
        self.toggle_color_bar = 1
      self.show_colorbar_display.emit(self.toggle_color_bar, 0)
      if self.complex_type:
        self.show_colorbar_display.emit(self.toggle_color_bar, 1)
      self._toggle_colorbar.setChecked(self.toggle_color_bar)
      return True

    def handle_toggle_color_gray_display(self):
      if self.toggle_gray_scale == 1:
        self.setDisplayType('hippo')
        self._toggle_color_gray_display.setChecked(False)
      else:
        self.setDisplayType('grayscale')
        self._toggle_color_gray_display.setChecked(True)
      self.plotImage.updateImage(self.raw_image)
      self.replot()

    def updatePlotParameters(self):
      """ create a GUI for user to modify plot parameters """
      parms_interface = WidgetSettingsDialog(actual_parent=self, gui_parent=self)

    def setImageRange(self, min, max, colorbar=0,image_lock=False):
      """ callback to set allowable range of array intensity display """
      if HAS_TIMBA:_dprint(3, 'received request for min and max of ', min, ' ', max)
      if colorbar == 0:
        self.plotImage.setLockImage(True, image_lock)
        self.plotImage.defineImageRange((min, max), True)
      else:
        self.plotImage.setLockImage(False, image_lock)
        self.plotImage.defineImageRange((min, max), False)
      self.plotImage.updateImage(self.raw_image)
      self.replot()
      if HAS_TIMBA:_dprint(3, 'called replot in setImageRange')
      #print 'called replot in setImageRange'
    # setImageRange
        

    def timerEvent_blink(self):
# stop blinking     
      if not self.flag_blink:
        self.timer.stop()
        self.handleFlagToggle(True)
      else:
        self.handleFlagToggle(self.flag_toggle)
      self.replot()
      if HAS_TIMBA:_dprint(3, 'called replot in timerEvent_blink')
      #print 'called replot in timerEvent_blink'

    def update_vells_display(self, menuid):
      self.handle_menu_id.emit(menuid)

    def setVellsPlot(self, do_vells_plot=True):
      self._vells_plot = do_vells_plot

    def report_scalar_value(self, data_label, scalar_data=None):
      """ report a scalar value in case where a vells plot has
          already been initiated
      """

      # delete any flag arrays
      self.unsetFlagsData()

      self._vells_plot = False
      self.reset_zoom()
      dummy_array = numpy.zeros(shape=(2,2),dtype=numpy.float32)
      self.array_plot(dummy_array,data_label=data_label)
      self.removeCurves()
      self.removeMarkers()
      self.zooming = False
      self.set_xaxis_title(' ')
      self.set_yaxis_title(' ')
      self.scalar_display = True
      self.setAxisAutoScale(QwtPlot.xBottom)
      self.setAxisAutoScale(QwtPlot.xTop)
      self.setAxisAutoScale(QwtPlot.yLeft)
      self.setAxisAutoScale(QwtPlot.yRight)
      self.enableAxis(QwtPlot.yLeft, False)
      self.enableAxis(QwtPlot.xBottom, False)
      self.grid.detach()

      self._x_auto_scale = True
      self._y_auto_scale = True
      if scalar_data is None:
        Message = data_label
      else:
        Message = data_label + ' is a scalar\n with value: ' + str(scalar_data)
      if HAS_TIMBA:_dprint(3,' scalar message ', Message)
      
      text = QwtText(Message)
      text.setColor(Qt.blue)
      text.setBackgroundBrush(QBrush(Qt.yellow))
      fn = self.fontInfo().family()
      text.setFont(QFont(fn, 8, QFont.Bold))
      self.source_marker = QwtPlotMarker()
      self.source_marker.setLabelAlignment(Qt.AlignRight | Qt.AlignTop)
      self.source_marker.setLabel(text)
      if not self.is_vector:
        xlb, xhb = self.plotImage.get_xMap_draw_coords()
        ylb, yhb = self.plotImage.get_yMap_draw_coords()
      else:
        try:
          ylb = self.axisScaleDiv(QwtPlot.yLeft).lBound()
          xlb = self.axisScaleDiv(QwtPlot.xBottom).lBound()
        except:
          ylb = self.axisScaleDiv(QwtPlot.yLeft).lowerBound()
          xlb = self.axisScaleDiv(QwtPlot.xBottom).upperBound()
      self.source_marker.setValue(xlb+0.1, ylb+1.0)
      self.source_marker.attach(self)


# make sure we cannot try to show ND Controller
      self.toggle_ND_Controller = 0
      self._toggle_nd_controller.setVisible(False)
      self._toggle_3d_display.setVisible(False)
      self._toggle_warp_display.setVisible(False)

# make sure any color bar from array plot of other Vells member is hidden
      self.show_colorbar_display.emit(0, 0)
      if self.complex_type:
        self.show_colorbar_display.emit(0, 1)
# make sure options relating to color bar are not in context menu
      self._toggle_colorbar.setVisible(False)
      self._toggle_color_gray_display.setVisible(False)
      self._toggle_log_range_for_data.setVisible(False)
      self.log_switch_set = False

# a scalar has no legends or cross-sections!
      self.delete_cross_sections()

# can't flip axes with a scalar!
      self._toggle_axis_flip.setVisible(False)
      self._toggle_axis_rotate.setVisible(False)

      self.replot()
      if HAS_TIMBA:_dprint(3,'called replot in report_scalar_value')
      self._vells_plot = True

    def printplot(self):
      """ make a hardcopy of current displayed plot """
      self.do_print.emit(self.is_vector, self.complex_type)
    # printplot()

    def drawCanvasItems(self, painter, rectangle, maps, filter):
        if not self.is_vector:
          self.plotImage.drawImage(
            painter, maps[QwtPlot.xBottom], maps[QwtPlot.yLeft])
        QwtPlot.drawCanvasItems(self, painter, rectangle, maps, filter)


    def formatCoordinates(self, x, y):
        """Format mouse coordinates as real world plot coordinates.
        """
        if self.scalar_display:
          return
        result = ''
        xpos = self.invTransform(QwtPlot.xBottom, x)
        ypos = self.invTransform(QwtPlot.yLeft, y)
        marker_index = None
        if self._vells_plot:
          xpos1 = xpos
          if not self.split_axis is None:
            if xpos1 >  self.split_axis:
                xpos1 = xpos1 - self.delta_vells
          temp_str_x_rel = "x =%+.2g" % xpos1
          temp_str_y_rel = "y =%+.2g" % ypos 
          temp_str_y_rel1 = " =%+.2g" % ypos 
          result = temp_str_x_rel + " " + temp_str_y_rel + " "
          xpos_value = None
          ypos_value = None
          if not self.first_axis_inc is None:
            if self.axes_rotate:
              xpos = int((self.vells_axis_parms[self.x_parm][1]- xpos) / self.first_axis_inc)
            else:
              xpos = int((xpos -self.vells_axis_parms[self.x_parm][0]) / self.first_axis_inc)
            xpos_loc = xpos
            if not self.split_axis is None:
              xpos_offset = int(xpos - self.delta_vells / self.first_axis_inc)
              if xpos_offset >= 0:
                xpos_loc = xpos_offset
            vells_axis_grids = self.vells_axis_parms[self.x_parm][4]
            if not vells_axis_grids is None:
              xpos1 = int((xpos1 -self.vells_axis_parms[self.x_parm][0]) / self.first_axis_inc)
              try:
                xpos_value = vells_axis_grids[xpos1]
                units = ""
                axis = "x "
                if self.x_parm.find('u') >= 0:
                  axis = "u "
                  units = " lambda "
                if self.x_parm.find('v') >= 0:
                  axis = "v "
                  units = " lambda "
                if self.x_parm.find('l') >= 0:
                  axis = "l "
                  units = " rad "
                if self.x_parm.find('time') >= 0:
                  axis = "time "
                  units = " sec "
                else:
                  if self.x_parm.find('m') >= 0:
                    axis = "m "
                    units = " rad "
                if self.x_parm.find('freq') >= 0:
                  axis = "freq "
                  units = " Hz "
                if self.vells_axis_parms[self.x_parm][2].find('MHz') >= 0:
                  xpos_value = xpos_value * 1.0e-6
                  units = " MHz "
                if self.vells_axis_parms[self.x_parm][2].find('KHz') >= 0:
                  xpos_value = xpos_value * 1.0e-3
                  units = " KHz "
                temp_str_x_abs = axis +" =%+.3g" % xpos_value + units
              except:
                temp_str_x_abs = temp_str_x_rel
          else:
# this inversion does not seem to work properly for scaled
# (vellsets) data, so use the above if possible
            xpos = self.plotImage.xMap.limTransform(xpos)
          if not self.second_axis_inc is None:
            ypos = int((ypos - self.vells_axis_parms[self.y_parm][0]) / self.second_axis_inc)
            vells_axis_grids = self.vells_axis_parms[self.y_parm][4]
            if not vells_axis_grids is None:
              try:
                ypos_value = vells_axis_grids[ypos]
                axis = "y "
                units = ""
                if self.y_parm.find('u') >= 0:
                  axis = "u "
                  units = " lambda "
                if self.y_parm.find('v') >= 0:
                  axis = "v "
                  units = " lambda "
                if self.y_parm.find('l') >= 0:
                  axis = "l "
                  units = " rad "
                if self.y_parm.find('time') >= 0:
                  axis = "time "
                  units = " sec "
                else:
                  if self.y_parm.find('m') >= 0:
                    axis = "m "
                    units = " rad "
                if self.y_parm.find('freq') >= 0:
                  axis = "freq "
                  units = " Hz "
                if self.vells_axis_parms[self.y_parm][2].find('MHz') >= 0:
                  ypos_value = ypos_value * 1.0e-6
                  units = " MHz "
                if self.vells_axis_parms[self.y_parm][2].find('KHz') >= 0:
                  ypos_value = ypos_value * 1.0e-3
                  units = " KHz "
                temp_str_y_abs = "y =%+.3g" % ypos_value + units 
                result = temp_str_x_abs + " " + axis + temp_str_y_rel1 + units
              except:
                result = temp_str_x_abs + " " + temp_str_y_rel + " "
          else:
            ypos = self.plotImage.yMap.limTransform(ypos)
        else:
          xpos = int(xpos)
          xpos_loc = xpos
          xpos1 = xpos
          if not self.split_axis is None:
            if xpos1 >=  self.split_axis:
              xpos1 = xpos1 % self.split_axis
              xpos_loc = xpos1
          temp_str = "x =%+.2g" % xpos1
          result = temp_str
          ypos1 = ypos
          ypos = int(ypos1)
          ypos2 = ypos
          if not self.y_marker_step is None:
            if ypos1 >  self.y_marker_step:
              marker_index = int(ypos1 / self.y_marker_step)
              ypos2 = int(ypos1 % self.y_marker_step)
            else:
              marker_index = 0
          temp_str = result + " y =%+.2g" % ypos2 + " "
          result = temp_str
        message = None
        array_location = None
        try:
          value = self.raw_array[xpos,ypos]
        except:
          return message
        array_location = '\nx: ' + str(xpos_loc) + ' y: ' + str(ypos)
        if self.has_nans_infs and value == self.nan_inf_value:
          temp_str = "value: NaN or Inf"
        else:
          temp_str = "value: %-.3g" % value
        if not marker_index is None:  
          if self.is_combined_image:
            length = len(self.marker_labels)
            marker_index = length -1 - marker_index
            message = result + temp_str + '\nsource: ' + self.marker_labels[marker_index]
          else:
            title_pos = self._window_title.find('spectra:')
            if title_pos >= 0:
              source = self._window_title[title_pos+8:]
            
              message = result + temp_str + '\nsource: ' + source
            else:
              message = result + temp_str
        else:
          title_pos = self._window_title.find('spectra:')
          if title_pos >= 0:
            source = self._window_title[title_pos+8:]
            
            message = result + temp_str + '\nsource: ' + source
          else:
            message = result + temp_str
        if not message is None and not array_location is None:
          message = message + array_location

        if self.solver_display:
          if not self.solver_labels is None:
            label = self.solver_labels[xpos]
            message = label + ': ' + message
    
        return message
            
    # formatCoordinates()

    def reportCoordinates(self, x, y):
        """Format mouse coordinates as real world plot coordinates.
        """
        if self.scalar_display:
          return
        result = ''
        if self.display_solution_distances:
          metrics_rank = "rank: " + str(self.metrics_rank[self.array_index,self.metrics_index]) + "\n"
          metrics_fit = "fit: " + str(self.metrics_fit[self.array_index,self.metrics_index]) + "\n"
          metrics_chi = "chi: " + str(self.metrics_chi[self.array_index,self.metrics_index]) + "\n"
          metrics_mu = "mu: " + str(self.metrics_mu[self.array_index,self.metrics_index]) + "\n"
          metrics_flag = "flag: " + str(self.metrics_flag[self.array_index,self.metrics_index]) + "\n"
          metrics_stddev = "stddev: " + str(self.metrics_stddev[self.array_index,self.metrics_index]) + "\n"
          metrics_unknowns = "unknowns: " + str(self.metrics_unknowns[self.array_index,self.metrics_index])
          metrics_iteration = "iteration: " + str(self.array_index+1) + "\n"
          message = metrics_iteration + self.curve_info + str(x) +  "\nchi_0: " + str(y) +"\n" + metrics_rank + metrics_fit + metrics_chi + metrics_mu + metrics_flag + metrics_stddev + metrics_unknowns  
#         mb_reporter = QMessageBox.information(self, "QwtImageDisplay", Message)
        else:
          if self._vells_plot:
            units = ""
            axis = "x "
            if self.x_parm.find('l') >= 0:
              axis = "l "
              units = " rad "
            if self.x_parm.find('time') >= 0:
              axis = "time "
              units = " sec "
            else:
              if self.x_parm.find('m') >= 0:
                axis = "m "
                units = " rad "
            if self.x_parm.find('freq') >= 0:
              axis = "freq "
              units = " Hz "
            if self.vells_axis_parms[self.x_parm][2].find('MHz') >= 0:
              units = " MHz "
            if self.vells_axis_parms[self.x_parm][2].find('KHz') >= 0:
              units = " KHz "
            temp_str = "nearest " + axis +" =%+.3g" % x + units
          else:
            temp_str = "nearest x=%-.3g" % x
          
          if self.has_nans_infs and y == self.nan_inf_value:
            temp_str1 = " value: NaN or Inf"
          else:
            temp_str1 = " value: %-.3g" % y
#         temp_str1 = " y=%-.3g" % y
          message = temp_str + temp_str1 
        return message

    # reportCoordinates()


    def refresh_marker_display(self):
      """ update all markers after new plot data has been displayed or
          modified 
      """ 
      if self.scalar_display:
        return
      self.removeMarkers()
      self.info_marker = None
      self.log_marker = None
      self.source_marker = None
      if self.is_combined_image:
        self.insert_marker_lines()
# draw dividing lines for complex array, cross_sections, solver_offsets, etc
      self.insert_array_info()
      self.replot()
      if HAS_TIMBA:_dprint(3, 'called replot in refresh_marker_display ')
      #print 'called replot in refresh_marker_display '
    # refresh_marker_display()

    def insert_marker_lines(self):
      if HAS_TIMBA:_dprint(2, 'starting insert_marker_lines')
# alias
      fn = self.fontInfo().family()
      y = 0
      for i in range(self.num_y_markers):
        label = self.marker_labels[i]

    def removeCurves(self):
      keys = list(self.curves.keys())
      if len(keys) > 0:
        for key in keys:
          self.curves[key].detach()
      self.curves = {}
      self.xrCrossSection = None
      self.xrCrossSection_flag = None
      self.xiCrossSection = None
      self.yCrossSection = None
      return

    def removeMarkers(self):
      keys = list(self.markers.keys())
      if len(keys) > 0:
        for key in keys:
          self.markers[key].detach()
      self.markers = {}
      return

    def closestCurve(self, pos):
        """ from Gerard Vermeulen's EventFilterDemo.py example """
        found, distance, point, index = None, 1e100, -1, -1
        counter = -1
        for curve in self.itemList():
            try:
              if isinstance(curve, QwtPlotCurve):
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
          s = found.sample(point)
          x = s.x()
          y = s.y()
          #print 'closest curve is ', index, ' ', x, ' ', y
          return (index, x, y, point)
    # closestCurve


    def infoDisplay(self, message, xpos, ypos):
      """ Display text under cursor in plot
          Figures out where the cursor is, generates the appropriate text, 
          and puts it on the screen.
      """
      self._popup_text.setText(message)
      self._popup_text.adjustSize()
      try:
        yhb = self.transform(QwtPlot.yLeft, self.axisScaleDiv(QwtPlot.yLeft).hBound())
        ylb = self.transform(QwtPlot.yLeft, self.axisScaleDiv(QwtPlot.yLeft).lBound())
        xhb = self.transform(QwtPlot.xBottom, self.axisScaleDiv(QwtPlot.xBottom).hBound())
        xlb = self.transform(QwtPlot.xBottom, self.axisScaleDiv(QwtPlot.xBottom).lBound())
      except:
        yhb = self.transform(QwtPlot.yLeft, self.axisScaleDiv(QwtPlot.yLeft).upperBound())
        ylb = self.transform(QwtPlot.yLeft, self.axisScaleDiv(QwtPlot.yLeft).lowerBound())
        xhb = self.transform(QwtPlot.xBottom, self.axisScaleDiv(QwtPlot.xBottom).upperBound())
        xlb = self.transform(QwtPlot.xBottom, self.axisScaleDiv(QwtPlot.xBottom).lowerBound())
      # muck around with position of pop-up to make sure it does not
      # disappear over edge of plot ...
      height = self._popup_text.height()
      ymove = ypos - 0.5 * height
      if ymove - height < yhb:
        ymove = yhb + height 
      if ymove + height > ylb:
        ymove = ylb - height 
      if ymove < yhb:
        ymove = yhb
      width = self._popup_text.width()

      xmove = xpos
      if xpos + width > xhb:
        xmove = xhb - width
      if xpos - width < xlb:
        xmove = xlb 
      self._popup_text.move(xmove, ymove)
      if not self._popup_text.isVisible():
        self._popup_text.show()

    def getBounds(self):
      try:
        self.yhb = self.transform(QwtPlot.yLeft, self.axisScaleDiv(QwtPlot.yLeft).hBound())
        self.ylb = self.transform(QwtPlot.yLeft, self.axisScaleDiv(QwtPlot.yLeft).lBound())
        self.xhb = self.transform(QwtPlot.xBottom, self.axisScaleDiv(QwtPlot.xBottom).hBound())
        self.xlb = self.transform(QwtPlot.xBottom, self.axisScaleDiv(QwtPlot.xBottom).lBound())
      except:
        self.yhb = self.transform(QwtPlot.yLeft, self.axisScaleDiv(QwtPlot.yLeft).upperBound())
        self.ylb = self.transform(QwtPlot.yLeft, self.axisScaleDiv(QwtPlot.yLeft).lowerBound())
        self.xhb = self.transform(QwtPlot.xBottom, self.axisScaleDiv(QwtPlot.xBottom).upperBound())
        self.xlb = self.transform(QwtPlot.xBottom, self.axisScaleDiv(QwtPlot.xBottom).lowerBound())

    def setPosition(self, e):
      """ callback to handle MouseMoved event """ 
      if self.scalar_display:
        return
      position = e.pos()
#     print('move position ', position.x(), position.y())
      self.raw_xpos = xPos = position.x()
      self.raw_ypos = yPos = position.y()
#     print 'display_image raw xpos ypos ',xPos, ' ', yPos
      self.xpos = self.invTransform(QwtPlot.xBottom, xPos)
      self.ypos = self.invTransform(QwtPlot.yLeft, yPos)
#     print 'mouse move position ', self.xpos,self.ypos
      
#     print 'display_image image xpos ypos ',self.xpos, ' ', self.ypos
      if not self.xzoom_loc is None:
        self.xzoom_loc = [self.press_xpos, self.press_xpos,  self.xpos, self.xpos,self.press_xpos]
        self.yzoom_loc = [self.press_ypos, self.ypos,  self.ypos, self.press_ypos,self.press_ypos]
        self.zoom_outline.setData(self.xzoom_loc,self.yzoom_loc)
        self.replot()

      try:
        self.getBounds()
        if xPos < self.xlb-10 or xPos > self.xhb+10 or yPos > self.ylb+10 or yPos < self.yhb-10:
          if self.mouse_pressed and not self.display_solution_distances:
            if not self.xzoom_loc is None:
              self.zoom_outline.detach()
              self.xzoom_loc = None
              self.yzoom_loc = None
              self.replot()
            self.mouse_pressed = False
            self.startDrag()
          return
        else:
          if self.is_vector: 
            curve_number, xVal, yVal, self.array_index = self.closestCurve(QPoint(self.raw_xpos, self.raw_ypos))
            message = self.reportCoordinates(xVal, yVal)
            message = message + ', data point: ' + str(self.array_index)
          else:
            message = self.formatCoordinates(xPos, yPos)
          if not self.display_solution_distances:
            if self.show_coordinates:
              # adding 40 and 45 pixels seems to give about the right offset
              location = QPoint(self.xlb+40,self.ylb+45)
              # QToolTip seems to need to be mapped to global coord system
              location = self.mapToGlobal(location)
              QToolTip.showText(location,message);
      except:
        return

      # remove any 'source' descriptor if we are zooming
      if abs(self.xpos - xPos) > 2 and abs(self.ypos - yPos)>2:
        if self._popup_text.isVisible():
          self._popup_text.hide()
        if not self.source_marker is None:
#         self.removeMarker(self.source_marker)
          self.source_marker = None
          self.replot()
          #print 'called replot in onMouseMoved'

    def mapMouseButtons (self,e):
        """Maps a mouse event to one of three buttons.
        To support victims of Jobs, Shift-LeftClick maps to MidClick, and Ctrl+LeftClick maps to RightClick""";
        if e.button() == Qt.LeftButton:
          if e.modifiers()&Qt.ShiftModifier:
            return Qt.MidButton;
          elif e.modifiers()&Qt.ControlModifier:
            return Qt.RightButton;
        return e.button();

    def onMousePressed(self, e):
        """ callback to handle MousePressed event """ 
        button = self.mapMouseButtons(e);
        if button == Qt.LeftButton:
            message = None
            self.mouse_pressed = True
            if self.is_vector: 
              if self.display_solution_distances:
            # Python semantics: self.pos = e.pos() does not work; force a copy
# We get information about the qwt plot curve that is
# closest to the location of this mouse pressed event.
# We are interested in the nearest curve_number and the index, or
# sequence number of the nearest point in that curve.
                  array_curve_number, xVal, yVal, self.array_index = self.closestCurve(QPoint(self.raw_xpos, self.raw_ypos))
                  if HAS_TIMBA:_dprint(2,'array_curve_number, xVal, yVal ', array_curve_number, ' ',  xVal, ' ', yVal)
                  shape = self.metrics_rank.shape
                  self.metrics_index = 0 
                  if shape[1] > 1:
                    self.metrics_index = numpy.array_curve_number % shape[1]
                    array_curve_number = int(array_curve_number / shape[1])
                  if array_curve_number == 0:
                    self.curve_info = "vector sum " 
                  if array_curve_number == 1:
                    self.curve_info = "sum of norms "
                  if array_curve_number == 2:
                    self.curve_info = "norms "
                  if array_curve_number <= 2:
                    message = self.reportCoordinates(xVal, yVal)
                  else:
                    temp_str = "nearest x=%-.3g" % xVal
                    temp_str1 = " y=%-.3g" % yVal
                    message = temp_str + temp_str1
                    message = message + ', data point: ' + str(self.array_index)
              else:
            # Python semantics: self.pos = e.pos() does not work; force a copy
# We get information about the qwt plot curve that is
# closest to the location of this mouse pressed event.
# We are interested in the nearest curve_number and the index, or
# sequence number of the nearest point in that curve.
                curve_number, xVal, yVal, self.array_index = self.closestCurve(QPoint(self.raw_xpos, self.raw_ypos))
                if HAS_TIMBA:_dprint(2,' curve_number, xVal, yVal ', curve_number, ' ', xVal, ' ', yVal );
                message = self.reportCoordinates(xVal, yVal)
                message = message + ', data point: ' + str(self.array_index)
            else:
              message = self.formatCoordinates(self.raw_xpos, self.raw_ypos)
            if not message is None:
              self.infoDisplay(message, self.raw_xpos, self.raw_ypos)
            if self.zooming:
              self.press_xpos = self.xpos
              self.press_ypos = self.ypos
              self.raw_press_xpos = self.raw_xpos
              self.raw_press_ypos = self.raw_ypos
              self.xzoom_loc = [self.press_xpos]
              self.yzoom_loc = [self.press_ypos]
              self.zoom_outline.attach(self)
              if self.zoomStack == []:
                try:
                  self.zoomState = (
                    self.axisScaleDiv(QwtPlot.xBottom).lBound(),
                    self.axisScaleDiv(QwtPlot.xBottom).hBound(),
                    self.axisScaleDiv(QwtPlot.yLeft).lBound(),
                    self.axisScaleDiv(QwtPlot.yLeft).hBound(),
                    )
                except:
                  self.zoomState = (
                    self.axisScaleDiv(QwtPlot.xBottom).lowerBound(),
                    self.axisScaleDiv(QwtPlot.xBottom).upperBound(),
                    self.axisScaleDiv(QwtPlot.yLeft).lowerBound(),
                    self.axisScaleDiv(QwtPlot.yLeft).upperBound(),
                    )
        elif button == Qt.RightButton:
            e.accept()
            self._menu.popup(e.globalPos());
            if self.scalar_display:
              return

        elif button == Qt.MidButton:
            if self.active_image:
              if self.scalar_display:
                return
              self.x_arrayloc = self.ypos
              self.y_arrayloc = self.xpos
              if self._vells_plot:
                if not self.first_axis_inc is None:
                  if self.axes_rotate:
                    xpos = int((self.vells_axis_parms[self.x_parm][1]- self.xpos) / self.first_axis_inc)
                  else:
                    xpos = int((self.xpos -self.vells_axis_parms[self.x_parm][0]) / self.first_axis_inc)
                else:
# this inversion does not seem to work properly for scaled
# (vellsets) data, so use the above if possible
                  xpos = self.plotImage.xMap.limTransform(self.xpos)
                if not self.second_axis_inc is None:
                  ypos = int((self.ypos - self.vells_axis_parms[self.y_parm][0]) / self.second_axis_inc)
                else:
                  ypos = self.plotImage.yMap.limTransform(self.ypos)
              else:
                xpos = int(self.xpos)
                ypos = int(self.ypos)
              self.xsect_xpos = xpos
              self.xsect_ypos = ypos
              self.show_x_sections = True
              self.calculate_cross_sections()
           
    # onMousePressed()

    def onMouseReleased(self, e):
#       print 'Release raw xpos ypos ',e.x(), ' ', e.y()
#       self.enableOutline(0)

# if mouse_pressed=True only if left button was pressed w/o modifiers, so check for this here
        if Qt.LeftButton == e.button() and self.mouse_pressed:
            if not self.xzoom_loc is None:
              self.zoom_outline.detach()
              self.xzoom_loc = None
              self.yzoom_loc = None
 
            self.mouse_pressed = False
            if self._popup_text.isVisible():
              self._popup_text.hide()
            self.refresh_marker_display()
# assume a change of <= 2 screen pixels is just due to clicking
# left mouse button for coordinate values

            if self.zooming and abs(self.raw_xpos - self.raw_press_xpos) > 2 and abs(self.raw_ypos - self.raw_press_ypos) > 2:
              xmin = min(self.raw_xpos, self.raw_press_xpos)
              xmax = max(self.raw_xpos, self.raw_press_xpos)
              ymin = min(self.raw_ypos, self.raw_press_ypos)
              ymax = max(self.raw_ypos, self.raw_press_ypos)

              if self.axisEnabled(QwtPlot.xTop):
                xmin_t = self.invTransform(QwtPlot.xTop, xmin)
                xmax_t = self.invTransform(QwtPlot.xTop, xmax)
              if self.axisEnabled(QwtPlot.yRight):
                ymin_r = self.invTransform(QwtPlot.yRight, ymin)
                ymax_r = self.invTransform(QwtPlot.yRight, ymax)
                if ymin_r > ymax_r:
                  temp = ymax_r
                  ymax_r = ymin_r
                  ymin_r = temp
              xmin = self.invTransform(QwtPlot.xBottom, xmin)
              xmax = self.invTransform(QwtPlot.xBottom, xmax)
              ymin = self.invTransform(QwtPlot.yLeft, ymin)
              ymax = self.invTransform(QwtPlot.yLeft, ymax)
              #print 'ymin ymax ', ymin, ymax
              #print 'xmin xmax ', xmin, xmax
              if not self.is_vector:
# if we have a vells plot, adjust bounds of image display to be an integer
# number of pixels
                if self._vells_plot:
                  if not self.first_axis_inc is None:
                    offset = int((xmin - self.vells_axis_parms[self.x_parm][0])/self.first_axis_inc)
                    xmin = self.vells_axis_parms[self.x_parm][0] + offset * self.first_axis_inc
                    offset = int((xmax + (0.5 * self.first_axis_inc) - self.vells_axis_parms[self.x_parm][0])/self.first_axis_inc)

                    xmax = self.vells_axis_parms[self.x_parm][0] + offset * self.first_axis_inc

                  if not self.second_axis_inc is None:
                    offset = int((ymin + (0.5 * self.second_axis_inc) - self.vells_axis_parms[self.y_parm][0])/self.second_axis_inc)
                    ymin = self.vells_axis_parms[self.y_parm][0] + offset * self.second_axis_inc
                    offset = int((ymax - self.vells_axis_parms[self.y_parm][0])//self.second_axis_inc)
                    ymax = self.vells_axis_parms[self.y_parm][0] + offset * self.second_axis_inc
                    #print 'vells ymin ymax ', ymin, ymax
                    #print 'vells xmin xmax ', xmin, xmax
                else:
                  ymax = int (ymax)
                  ymin = int (ymin + 0.5)
                  xmax = int (xmax + 0.5)
                  xmin = int (xmin)
                  #print 'array ymin ymax ', ymin, ymax
                  #print 'array xmin xmax ', xmin, xmax

              if ymin > ymax:
                temp = ymax
                ymax = ymin
                ymin = temp
              if xmin == xmax or ymin == ymax:
                return
              if not self.zoomState is None:
                self.zoomStack.append(self.zoomState)
              self.zoomState = (xmin, xmax, ymin, ymax)
        
              self.setAxisScale(QwtPlot.xBottom, xmin, xmax)
              self.setAxisScale(QwtPlot.yLeft, ymin, ymax)
              if not self.is_vector:
                self.plotImage.update_xMap_draw(xmin,xmax)
                self.plotImage.update_yMap_draw(ymin,ymax)

              if self.axisEnabled(QwtPlot.yRight):
                self.setAxisScale(QwtPlot.yRight, ymin_r, ymax_r)
              if self.axisEnabled(QwtPlot.xTop):
                self.setAxisScale(QwtPlot.xTop, xmin_t, xmax_t)
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
              self._reset_zoomer.setVisible(True)
              if self.is_vector and self.complex_type:
                self._undo_last_zoom.setVisible(False)
              else:
                self._undo_last_zoom.setVisible(True)
              self.test_plot_array_sizes()
            self.replot()
            if HAS_TIMBA:_dprint(3, 'called replot in onMouseReleased');
            #print 'called replot in onMouseReleased'
    # onMouseReleased()

    def resizeEvent(self, event):
      self.current_width = event.size().width()
      self.test_plot_array_sizes(event.size().width())
      self.updateLayout();

    # resizeEvent()


    def test_plot_array_sizes(self, width=None):

# if we have a solver plot 
      if len(list(self.chis_plot.keys())) > 0:
        zoom = False
        if len(self.zoomStack):
          zoom = True
        if not zoom:
          self.setAxisAutoScale(QwtPlot.xTop)
          self.setAxisAutoScale(QwtPlot.yRight)
          if self.log_axis_chi_0:
            self._toggle_log_axis_for_chi_0.setChecked(True)
          else:
            self._toggle_log_axis_for_chi_0.setChecked(False)
          if self.log_axis_solution_vector:
            self._toggle_log_axis_for_solution_vector.setChecked(True)
          else:
            self._toggle_log_axis_for_solution_vector.setChecked(False)

# adjust symbol sizes for any real / imaginary plots
      if not self.x_index is None:
        zoom = False
        if len(self.zoomStack):
          zoom = True
        if width is None:
          if self.current_width == 0:
            width = 300
          else:
            width = self.current_width
        q_line_size = 2
        q_symbol_size = 5
        q_flag_size = 20

        if not zoom:
          num_valid_points = len(self.x_index)
        else:
          num_valid_points = 0
          for i in range(len(self.x_index)):
            if self.x_index[i] >= self.xmin and self.x_index[i]<= self.xmax:
              num_valid_points = num_valid_points + 1

        if num_valid_points > width:
          q_line_size = 1
          q_symbol_size = 3
          q_flag_size = 10
          
        if self.axisEnabled(QwtPlot.yRight) and not zoom and not self.complex_type:
          self.setAxisAutoScale(QwtPlot.yRight)
        if self.axisEnabled(QwtPlot.xTop) and not zoom:
          self.setAxisAutoScale(QwtPlot.xTop)
        keys = list(self.curves.keys())
        for j in range(len(keys)):
          plot_curve=self.curves[keys[j]]
          if keys[j] == 'imaginaries' or keys[j] == 'phase':
            plot_curve.setPen(QPen(Qt.blue, q_line_size))
            plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.green),
                  QPen(Qt.green), QSize(q_symbol_size,q_symbol_size)))
          if keys[j] == 'reals' or keys[j] == 'amplitude':
            plot_curve.setPen(QPen(Qt.black, q_line_size))
            plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.red),
                  QPen(Qt.red), QSize(q_symbol_size,q_symbol_size)))
          if keys[j] == 'xCrossSection' or keys[j] == 'xrCrossSection' or keys[j] == 'xiCrossSection':
            plot_curve.setPen(QPen(Qt.black, q_line_size))
            plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.black),
                  QPen(Qt.black), QSize(q_symbol_size,q_symbol_size)))
          if keys[j] == 'yCrossSection':
            plot_curve.setPen(QPen(Qt.white, q_line_size))
            plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse,QBrush(Qt.white), 
                  QPen(Qt.white), QSize(q_symbol_size,q_symbol_size)))

    def modify_xsection_display(self, signal_id):
        """ select and display complex cross section display """
        if self.show_x_sections:
          if signal_id == 201 or signal_id == 202:
            self.xiCrossSection.detach()
            self.xiCrossSection = None
            self.real_xsection_selected = True
            self.imag_xsection_selected = False
            if self.xrCrossSection is None:
              self.calculate_cross_sections()
          if signal_id == 200 or signal_id == 203:
            self.xrCrossSection.detach()
            self.xrCrossSection = None
            self.real_xsection_selected = False
            self.imag_xsection_selected = True
            if self.xiCrossSection is None:
              self.calculate_cross_sections()
          if signal_id == 204:
            self.real_xsection_selected = True
            self.imag_xsection_selected = True
            if self.xrCrossSection is None or self.xiCrossSection is None:
              self.calculate_cross_sections()
          self.replot()
          #print 'called replot in modify_xsection_display' 
        return

    def calculate_cross_sections(self):
        """ calculate and display cross sections at specified location """
        if HAS_TIMBA:_dprint(3, 'calculating cross-sections')
        # can't plot cross sections and chi display together
        keys = list(self.chis_plot.keys())
        if len(keys) > 0:
          for key in keys:
            self.chis_plot[key].detach()
        self.chis_plot = {}

        shape = self.raw_array.shape
        if HAS_TIMBA:_dprint(3, 'shape is ', shape)
        no_flags = True
        if not self._flags_array is None:
          if self.flag_toggle:
            no_flags = False
        q_line_size = 2
        q_symbol_size = 5
        q_flag_size = 20
        q_size_split = 300
        if shape[0] > q_size_split:
          q_line_size = 1
          q_symbol_size = 3
          q_flag_size = 10

# create x_index defaults for array plots 
        self.x_array = numpy.zeros(shape[0], numpy.float32)
        if self.complex_type:
          self.x_index = numpy.arange(2* shape[0])
        else:
          self.x_index = numpy.arange(shape[0])
        self.x_index = self.x_index + 0.5

        if HAS_TIMBA:_dprint(3, 'self.xsect_ypos is ', self.xsect_ypos)
#       try:
        x_values = []
        x_index = []
        if self.complex_type:
          divider = int(shape[0] / 2)
          for i in range(divider):
            if self.raw_array[i,self.xsect_ypos] != self.nan_inf_value:
              if no_flags:
                x_values.append(self.raw_array[i,self.xsect_ypos])
                x_index.append(i+0.5)
              else:
                if self._flags_array[i,self.xsect_ypos] == 0:
                  x_values.append(self.raw_array[i,self.xsect_ypos])
                  x_index.append(i+0.5)
          for i in range(divider, shape[0] ):
            if self.raw_array[i - divider,self.xsect_ypos] != self.nan_inf_value:
              if no_flags:
                x_values.append(self.raw_array[i,self.xsect_ypos])
                x_index.append(i+0.5)
              else:
                if self._flags_array[i- divider,self.xsect_ypos] == 0:
                  x_values.append(self.raw_array[i,self.xsect_ypos])
                  x_index.append(i+0.5)
        else:
          for i in range(shape[0]):
            if self.raw_array[i,self.xsect_ypos] != self.nan_inf_value:
              if no_flags:
                x_values.append(self.raw_array[i,self.xsect_ypos])
                x_index.append(i+0.5)
              else:
                if self._flags_array[i,self.xsect_ypos] == 0:
                  x_values.append(self.raw_array[i,self.xsect_ypos])
                  x_index.append(i+0.5)
        self.x_array = numpy.array(x_values)
        self.x_index = numpy.array(x_index)
        self.setAxisAutoScale(QwtPlot.yRight)
        if self.toggle_log_display:
          self.setAxisAutoScale(QwtPlot.yRight)
          self.setAxisScaleEngine(QwtPlot.yRight, QwtLogScaleEngine())
        else:
          self.setAxisAutoScale(QwtPlot.yRight)
          self.setAxisScaleEngine(QwtPlot.yRight, QwtLinearScaleEngine())

# create x_index defaults for array plots 
        if HAS_TIMBA:_dprint(3, 'self.xsect_xpos is ', self.xsect_xpos)
        y_values = []
        y_index = []
        for i in range(shape[1]):
          if self.raw_array[self.xsect_xpos,i] != self.nan_inf_value:
            if no_flags:
              y_values.append(self.raw_array[self.xsect_xpos,i])
              y_index.append(i+0.5)
            else:
              if self.complex_type:
                flag_loc = self.xsect_xpos - shape[0]//2
              else:
                flag_loc =  self.xsect_xpos
              if self._flags_array[flag_loc,i] == 0:
                y_values.append(self.raw_array[self.xsect_xpos,i])
                y_index.append(i+0.5)
        self.y_array = numpy.array(y_values)
        self.y_index = numpy.array(y_index)
        self.setAxisAutoScale(QwtPlot.xTop)
        if self.toggle_log_display:
          self.setAxisAutoScale(QwtPlot.xTop)
          self.setAxisScaleEngine(QwtPlot.xTop, QwtLogScaleEngine())
        else:
          self.setAxisAutoScale(QwtPlot.xTop)
          self.setAxisScaleEngine(QwtPlot.xTop, QwtLinearScaleEngine())
        if self.xrCrossSection is None and self.real_xsection_selected:
          if self.complex_type:
            self.xrCrossSection = QwtPlotCurve('xrCrossSection')
            self.curves['xrCrossSection'] = self.xrCrossSection
          else:
            self.xrCrossSection = QwtPlotCurve('xCrossSection')
            self.curves['xCrossSection'] = self.xrCrossSection
          self.xrCrossSection.attach(self)

          self.xrCrossSection.setPen(QPen(Qt.black,q_line_size))
          self.xrCrossSection.setStyle(QwtPlotCurve.Lines)
          self.xrCrossSection.setYAxis(QwtPlot.yLeft)
          self.xrCrossSection.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.black),
                  QPen(Qt.black), QSize(q_symbol_size,q_symbol_size)))

        self.enableAxis(QwtPlot.yRight, True)
        self.yRight_title = QwtText('x cross-section value')
        self.yRight_title.setFont(self.title_font)
        self.setAxisTitle(QwtPlot.yRight, self.yRight_title)
        if self.real_xsection_selected:
          self.xrCrossSection.setYAxis(QwtPlot.yRight)
        if self.complex_type:
          if self.xiCrossSection is None and self.imag_xsection_selected:
            self.xiCrossSection = QwtPlotCurve('xiCrossSection')
            self.curves['xiCrossSection'] = self.xiCrossSection
            self.xiCrossSection.attach(self)
            self.xiCrossSection.setPen(QPen(Qt.black, q_line_size))
            self.xiCrossSection.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.black),
                  QPen(Qt.black), QSize(q_symbol_size,q_symbol_size)))
            self.xiCrossSection.setYAxis(QwtPlot.yRight)
            self.setAxisAutoScale(QwtPlot.yRight)
        if self.yCrossSection is None:
          self.yCrossSection = QwtPlotCurve('yCrossSection')
          self.curves['yCrossSection'] = self.yCrossSection
          self.yCrossSection.attach(self)
          self.yCrossSection.setYAxis(QwtPlot.yLeft)
          self.yCrossSection.setXAxis(QwtPlot.xTop)
          self.yCrossSection.setPen(QPen(Qt.white, q_line_size))
          self.yCrossSection.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.white),
                  QPen(Qt.white), QSize(q_symbol_size,q_symbol_size)))
        self.enableAxis(QwtPlot.xTop, True)
        self.xTop_title = QwtText('y cross-section value')
        self.xTop_title.setFont(self.title_font)
        self.setAxisTitle(QwtPlot.xTop, self.xTop_title)
        if self._vells_plot:
          delta_vells = self.vells_axis_parms[self.x_parm][1] - self.vells_axis_parms[self.x_parm][0]
          if self.complex_type:
            delta_vells = 2.0 * delta_vells
          x_step = delta_vells // shape[0] 
          if self.axes_rotate:
            start_x = self.vells_axis_parms[self.x_parm][1] - 0.5 * x_step
          else:
            start_x = self.vells_axis_parms[self.x_parm][0] + 0.5 * x_step
          x_indices = []
          if self.complex_type:
            for i in range(shape[0] // 2 ):
              if self.raw_array[i,self.xsect_ypos] != self.nan_inf_value:
                if no_flags:
                  x_indices.append(start_x + i * x_step)
                else:
                  if self._flags_array[i,self.xsect_ypos] == 0:
                    x_indices.append(start_x + i * x_step)
            for i in range(shape[0] // 2, shape[0] ):
              if self.raw_array[i - shape[0]//2 ,self.xsect_ypos] != self.nan_inf_value:
                if no_flags:
                  if self.axes_rotate:
                    x_indices.append(start_x - i * x_step)
                  else:
                    x_indices.append(start_x + i * x_step)
                else:
                  if self._flags_array[i- shape[0]//2,self.xsect_ypos] == 0:
                    if self.axes_rotate:
                      x_indices.append(start_x - i * x_step)
                    else:
                      x_indices.append(start_x + i * x_step)
          else:
            for i in range(shape[0]):
              if self.raw_array[i,self.xsect_ypos] != self.nan_inf_value:
                if no_flags:
                  if self.axes_rotate:
                    x_indices.append(start_x - i * x_step)
                  else:
                    x_indices.append(start_x + i * x_step)
                else:
                  if self._flags_array[i,self.xsect_ypos] == 0:
                    if self.axes_rotate:
                      x_indices.append(start_x - i * x_step)
                    else:
                      x_indices.append(start_x + i * x_step)
          self.x_index = numpy.array(x_indices)
          delta_vells = self.vells_axis_parms[self.y_parm][1] - self.vells_axis_parms[self.y_parm][0]
          y_step = delta_vells // shape[1] 
          start_y = self.vells_axis_parms[self.y_parm][0] + 0.5 * y_step
          y_indices = []
          for i in range(shape[1]):
            if self.raw_array[self.xsect_xpos,i] != self.nan_inf_value:
              if no_flags:
                y_indices.append(start_y + i * y_step)
              else:
                if self.complex_type:
                 flag_loc = self.xsect_xpos - shape[0]//2
                else:
                  flag_loc =  self.xsect_xpos
                if self._flags_array[flag_loc,i] == 0:
                  y_indices.append(start_y + i * y_step)
          self.y_index = numpy.array(y_indices)

        self.log_offset = 0.0
        if self.toggle_log_display:
          self.log_offset = self.plotImage.getTransformOffset()
        if self.complex_type:
          axis_shape = self.x_index.shape
          limit = axis_shape[0] // 2
          if not self.xrCrossSection is None:
            self.xrCrossSection.setData(self.x_index[:limit], self.x_array[:limit] + self.log_offset)
          if not self.xiCrossSection is None:
            self.xiCrossSection.setData(self.x_index[limit:], self.x_array[limit:] + self.log_offset)
        else:
          self.xrCrossSection.setData(self.x_index, self.x_array + self.log_offset)
        self.yCrossSection.setData(self.y_array + self.log_offset, self.y_index)

        self.test_plot_array_sizes()

        self.refresh_marker_display()
        self.show_x_sections = True
        if self.complex_type:
          self._delete_x_section_display.setVisible(False)
          self._delete_cx_section_display.setVisible(True)
          self._select_x_section_display.setVisible(True)
          self._select_both_cross_sections.setVisible(True)
          if self.ampl_phase:
            self._select_real_cross_section.setVisible(False)
            self._select_imaginary_cross_section.setVisible(False)
            self._select_amplitude_cross_section.setVisible(True)
            self._select_phase_cross_section.setVisible(True)
            self._select_amplitude_cross_section.setChecked(self.real_xsection_selected);
            self._select_phase_cross_section.setChecked(self.imag_xsection_selected);
          else:
            self._select_real_cross_section.setVisible(True)
            self._select_imaginary_cross_section.setVisible(True)
            self._select_amplitude_cross_section.setVisible(False)
            self._select_phase_cross_section.setVisible(False)
            self._select_real_cross_section.setChecked(self.real_xsection_selected);
            self._select_imaginary_cross_section.setChecked(self.imag_xsection_selected);
          self._select_both_cross_sections.setChecked(self.real_xsection_selected and self.imag_xsection_selected);
        else:
          self._delete_x_section_display.setVisible(True)
          self._delete_cx_section_display.setVisible(False)
          self._select_x_section_display.setVisible(False)
          self._select_both_cross_sections.setVisible(False)
          self._select_amplitude_cross_section.setVisible(False)
          self._select_phase_cross_section.setVisible(False)
          self._select_real_cross_section.setVisible(False)
          self._select_imaginary_cross_section.setVisible(False)


    def setDisplayType(self, display_type):
      self._display_type = display_type
      self.plotImage.setDisplayType(display_type)
      self.display_type.emit(self._display_type)
      if display_type.find('grayscale') == -1:
        self.toggle_gray_scale = 0
      else:
        self.toggle_gray_scale = 1
    # setDisplayType

    def display_image(self, image):
      if self.complex_type:
        (nx,ny) = image.shape
        real_array =  image.real
        self.raw_array = numpy.empty(shape=(nx*2,ny),dtype=real_array.dtype);
        self.raw_array[:nx,:] = real_array
        self.raw_array[nx:,:] = image.imag
      else:
        self.raw_array = image
      self.raw_image = image

      if HAS_TIMBA:_dprint(3, 'self.adjust_color_bar ', self.adjust_color_bar)
      if not self.colorbar_requested:
        if HAS_TIMBA:_dprint(3, 'emitting colorbar_needed signal')
        self.colorbar_needed.emit((1,))
        self.colorbar_requested = True
      
      # emit range for the color bar
      if self.adjust_color_bar:
        self.plotImage.setImageRange(image)
        image_limits = self.plotImage.getRealImageRange()
        self.max_image_range.emit(image_limits, 0, self.toggle_log_display,self.ampl_phase)
        if self.complex_type:
          image_limits = self.plotImage.getImagImageRange()
          self.max_image_range.emit(image_limits, 1, self.toggle_log_display,self.ampl_phase)
        self.adjust_color_bar = False

      if self._vells_plot:
        if self.complex_type:
          temp_x_axis_parms = self.vells_axis_parms[self.x_parm]
          begin = temp_x_axis_parms[0]
          end = begin + 2.0 * self.delta_vells 
          x_range = (begin, end)
          self.plotImage.setData(self.raw_image, x_range, self.vells_axis_parms[self.y_parm])
        else:
          if HAS_TIMBA:_dprint(3, 'calling self.plotImage.setData with self.vells_axis_parms[self.x_parm], self.vells_axis_parms[self.y_parm] ', self.vells_axis_parms[self.x_parm], ' ', self.vells_axis_parms[self.y_parm])

          if self.axes_rotate:
            temp_x_axis_parms = self.vells_axis_parms[self.x_parm]
            begin = temp_x_axis_parms[1]
            end = temp_x_axis_parms[0]
            x_range = (begin, end)
            self.plotImage.setData(self.raw_image, x_range, self.vells_axis_parms[self.y_parm])
          else:
            self.plotImage.setData(self.raw_image, self.vells_axis_parms[self.x_parm], self.vells_axis_parms[self.y_parm])
      else:
        self.plotImage.setData(self.raw_image)

# adjust image range because zoomState is set?
      if not self.zoomState is None:
        xmin = self.zoomState[0]
        xmax = self.zoomState[1]
        ymin = self.zoomState[2]
        ymax = self.zoomState[3]
        self.plotImage.update_xMap_draw(xmin,xmax)
        self.plotImage.update_yMap_draw(ymin,ymax)

# the following is used to make sure same image is kept on display if
# colorbar intensity range is toggled or color/grayscale is toggled
      if not self.xmin is None and not self.xmax is None and not self.ymin is None and not self.ymax is None:
        self.setAxisScale(QwtPlot.xBottom, self.xmin, self.xmax)
        self.setAxisScale(QwtPlot.yLeft, self.ymin, self.ymax)
        self._x_auto_scale = False
        self._y_auto_scale = False
        self.axis_xmin = self.xmin
        self.axis_xmax = self.xmax
        self.axis_ymin = self.ymin
        self.axis_ymax = self.ymax

      if self.toggle_metrics and not self.metrics_rank is None:
        self.add_solver_metrics()

      if self.show_x_sections:
        self.calculate_cross_sections()
      else:
        self.refresh_marker_display()      
    # display_image()

    def add_solver_metrics(self):
      #solver metrics
      if not self.display_solution_distances:
        try:
          keys = list(self.chis_plot.keys())
          if len(keys) > 0:
            for key in keys:
              self.chis_plot[key].detach()
            self.chis_plot = {}
        except:
          pass 
        try:
          keys = list(self.metrics_plot.keys())
          if len(keys) > 0:
            for key in keys:
              self.metrics_plot[key].detach()
            self.metrics_plot = {}
        except:
          pass
        shape = self.metrics_rank.shape
        for i in range(shape[1]):
          plot_data= numpy.zeros(shape[0], numpy.int32)
          for j in range(shape[0]):
            plot_data[j] = self.metrics_rank[j,i]
# add solver metrics info?
          metrics_title = 'metrics rank ' + str(i)

          metrics_curve = QwtPlotCurve(metrics_title)
          self.metrics_plot[metrics_title] = metrics_curve
          self.metrics_plot[metrics_title].attach(self)
          metrics_curve.setPen(QPen(Qt.black, 2))
          metrics_curve.setStyle(QwtPlotCurve.Lines)
          metrics_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.black),
                 QPen(Qt.black), QSize(10,10)))
        
          if self.array_flip:
            metrics_curve.setYAxis(QwtPlot.yLeft)
            metrics_curve.setXAxis(QwtPlot.xBottom)
            metrics_curve.setData(plot_data, self.iteration_number)
          else:
            metrics_curve.setYAxis(QwtPlot.xBottom)
            metrics_curve.setXAxis(QwtPlot.yLeft)
            metrics_curve.setData(self.iteration_number, plot_data)

      #chi_sq surfaces  - first remove any previous versions?
      #the following should work but seems to be causing problems
      shape = self.metrics_rank.shape
      self.enableAxis(QwtPlot.yRight, True)
      self.enableAxis(QwtPlot.xTop, True)
        
      self.yRight_title = QwtText('chi_0')
      self.yRight_title.setFont(self.title_font)
      self.xTop_title = QwtText('amplitude of solution vector')
      self.xTop_title.setFont(self.title_font)
      self.setAxisTitle(QwtPlot.xTop, self.xTop_title)
      self.setAxisTitle(QwtPlot.yRight, self.yRight_title)

      if self.first_chi_test:
        self.log_axis_solution_vector = False
        self.log_axis_chi_0 = False
        if self.chi_vectors.min() != 0.0 and self.chi_vectors.max() / self.chi_vectors.min() > 1000.0:
          self.log_axis_solution_vector = True
        if self.chi_zeros.min() != 0.0 and self.chi_zeros.max() / self.chi_zeros.min() > 1000.0:
           self.log_axis_chi_0 = True
        self.first_chi_test = False

      self.setAxisAutoScale(QwtPlot.yRight)
      self.setAxisAutoScale(QwtPlot.xTop)
      if self.log_axis_chi_0:
        self.setAxisScaleEngine(QwtPlot.yRight, QwtLogScaleEngine())
      else:
        self.setAxisScaleEngine(QwtPlot.yRight, QwtLinearScaleEngine())
      if self.log_axis_solution_vector:
        self.setAxisScaleEngine(QwtPlot.xTop, QwtLogScaleEngine())
      else:
        self.setAxisScaleEngine(QwtPlot.xTop, QwtLinearScaleEngine())
      for i in range(shape[1]):
        plot_data= numpy.zeros(shape[0], numpy.float32)
        chi_data= numpy.zeros(shape[0], numpy.float32)
        for j in range(shape[0]):
          plot_data[j] = self.chi_vectors[j,i]
          chi_data[j] = self.chi_zeros[j,i]
        curve = QwtPlotCurveSizes()
        title_key = 'vector sum of incremental solutions '
        curve.setTitle(title_key)
        self.chis_plot[title_key+str(i)] = curve
        self.chis_plot[title_key+str(i)].attach(self)
        curve.setPen(QPen(Qt.red, 2))
        curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse,
             QBrush(Qt.red), QPen(Qt.red), QSize(10,10)))
        curve.setStyle(QwtPlotCurve.Lines)
        if self.array_flip:
          curve.setYAxis(QwtPlot.yRight)
          curve.setXAxis(QwtPlot.xTop)
          curve.setData(plot_data,chi_data)
        else:
          curve.setYAxis(QwtPlot.xTop)
          curve.setXAxis(QwtPlot.yRight)
          curve.setData(chi_data,plot_data)
        symbolList=[]
        for j in range(len(chi_data)):
          if j == 0:
            # first symbol is rectangle
            symbolList.append(QwtSymbol(QwtSymbol.Rect, QBrush(Qt.red),
                 QPen(Qt.red),QSize(10,10)))
          else:
            if self.nonlin is None:
              symbolList.append(QwtSymbol(QwtSymbol.Diamond,
                  QBrush(Qt.red), QPen(Qt.red), QSize(10,10)))
            else:
              if self.nonlin[j,i] >= self.nonlin[j-1,i]:
                symbolList.append(QwtSymbol(QwtSymbol.UTriangle,
                  QBrush(Qt.red), QPen(Qt.red), QSize(10,10)))
              else:
                symbolList.append(QwtSymbol(QwtSymbol.DTriangle,
                  QBrush(Qt.red), QPen(Qt.red), QSize(10,10)))
        curve.setSymbolList(symbolList)

      # add additional solution surfaces here
      if self.display_solution_distances:
        self._toggle_metrics_display.setVisible(False)
        for i in range(shape[1]):
          plot_data1= numpy.zeros(shape[0], numpy.float32)
          chi_data1= numpy.zeros(shape[0], numpy.float32)
          for j in range(shape[0]):
            plot_data1[j] = self.sum_incr_soln_norm[j,i]
            chi_data1[j] = self.chi_zeros[j,i]
          curve = QwtPlotCurveSizes()
          title_key = 'sum of the norms of incremental solutions '
          self.chis_plot[title_key+str(i)] = curve
          self.chis_plot[title_key+str(i)].attach(self)
          curve.setTitle(title_key)
          curve.setPen(QPen(Qt.blue, 2))
          curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse,
             QBrush(Qt.blue), QPen(Qt.blue), QSize(10,10)))
          curve.setStyle(QwtPlotCurve.Lines)
          if self.array_flip:
            curve.setYAxis(QwtPlot.yRight)
            curve.setXAxis(QwtPlot.xTop)
            curve.setData(plot_data1,chi_data1)
          else:
            curve.setYAxis(QwtPlot.xTop)
            curve.setXAxis(QwtPlot.yRight)
            curve.setData(chi_data1,plot_data1)
          symbolList=[]
          for j in range(len(chi_data1)):
            if j == 0:
              # first symbol is rectangle
              symbolList.append(QwtSymbol(QwtSymbol.Rect, QBrush(Qt.blue),
                 QPen(Qt.blue),QSize(10,10)))
            else:
              if self.nonlin is None:
                symbolList.append(QwtSymbol(QwtSymbol.Diamond,
                  QBrush(Qt.blue), QPen(Qt.blue), QSize(10,10)))
              else:
                if self.nonlin[j,i] >= self.nonlin[j-1,i]:
                  symbolList.append(QwtSymbol(QwtSymbol.UTriangle,
                    QBrush(Qt.blue), QPen(Qt.blue), QSize(10,10)))
                else:
                  symbolList.append(QwtSymbol(QwtSymbol.DTriangle,
                    QBrush(Qt.blue), QPen(Qt.blue), QSize(10,10)))
          curve.setSymbolList(symbolList)

        for i in range(shape[1]):
          plot_data2= numpy.zeros(shape[0], numpy.float32)
          chi_data2= numpy.zeros(shape[0], numpy.float32)
          for j in range(shape[0]):
            plot_data2[j] = self.incr_soln_norm[j,i]
            chi_data2[j] = self.chi_zeros[j,i]
          curve = QwtPlotCurveSizes()
          title_key = 'norms of incremental solutions '
          self.chis_plot[title_key+str(i)] = curve
          self.chis_plot[title_key+str(i)].attach(self)
          curve.setTitle(title_key)
          curve.setPen(QPen(Qt.green, 2))
          curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse,
             QBrush(Qt.green), QPen(Qt.green), QSize(10,10)))
          curve.setStyle(QwtPlotCurve.Lines)
          if self.array_flip:
            curve.setYAxis(QwtPlot.yRight)
            curve.setXAxis(QwtPlot.xTop)
            curve.setData(plot_data2,chi_data2)
          else:
            curve.setYAxis(QwtPlot.xTop)
            curve.setXAxis(QwtPlot.yRight)
            curve.setData(chi_data2,plot_data2)
          symbolList=[]
          for j in range(len(chi_data2)):
            if j == 0:
              # first symbol is rectangle
              symbolList.append(QwtSymbol(QwtSymbol.Rect, QBrush(Qt.green),
                 QPen(Qt.green),QSize(10,10)))
            else:
              if self.nonlin is None:
                symbolList.append(QwtSymbol(QwtSymbol.Diamond,
                  QBrush(Qt.green), QPen(Qt.green), QSize(10,10)))
              else:
                if self.nonlin[j,i] >= self.nonlin[j-1,i]:
                  symbolList.append(QwtSymbol(QwtSymbol.UTriangle,
                    QBrush(Qt.green), QPen(Qt.green), QSize(10,10)))
                else:
                  symbolList.append(QwtSymbol(QwtSymbol.DTriangle,
                    QBrush(Qt.green), QPen(Qt.green), QSize(10,10)))
# following only works for QwtPlotCurvesSizes
          curve.setSymbolList(symbolList)

        # plot eigenvalues of the covariance matrix?
        if self.eigenvectors is None:
          self.enableAxis(QwtPlot.yLeft, False)
          self.enableAxis(QwtPlot.xBottom, False)
        else:
          self.enableAxis(QwtPlot.yLeft, True)
          self.enableAxis(QwtPlot.xBottom, True)
        
          self.setAxisTitle(QwtPlot.yLeft, 'Eigenvalue (black)')
          self.setAxisTitle(QwtPlot.xBottom, 'Eigenvalue number')

          for i in range (len(self.eigenvectors)):
            eigens = self.eigenvectors[i]
            eigenvalues = eigens[0]
            eigenlist = list(eigenvalues)
            eigenlist.sort(reverse=True)
            sorted_eigenvalues = numpy.array(eigenlist)
            shape = eigenvalues.shape
            x_data = numpy.arange(shape[0])
# we really need a QWtPlotCurveSizes object here
            curve = QwtPlotCurve()
            title_key = 'eigenvalues ' 
            curve.setTitle(title_key)
            self.chis_plot[title_key+str(i)] = curve
            self.chis_plot[title_key+str(i)].attach(self)
            curve.setPen(QPen(Qt.black, 2))
            curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse,
               QBrush(Qt.black), QPen(Qt.black), QSize(10,10)))
            curve.setStyle(QwtPlotCurve.Lines)
            if self.array_flip:
              curve.setYAxis(QwtPlot.yLeft)
              curve.setXAxis(QwtPlot.xBottom)
              curve.setData(x_data,sorted_eigenvalues)
            else:
              curve.setYAxis(QwtPlot.xBottom)
              curve.setXAxis(QwtPlot.yLeft)
              curve.setData(sorted_eigenvalues,x_data)
            symbolList=[]
            for j in range(shape[0]):
              if j == 0:
                # first symbol is rectangle
                symbolList.append(QwtSymbol(QwtSymbol.Rect, QBrush(Qt.black),
                   QPen(Qt.black),QSize(10,10)))
              else:
                symbolList.append(QwtSymbol(QwtSymbol.Diamond,
                   QBrush(Qt.black), QPen(Qt.black), QSize(10,10)))
            curve.setSymbolList(symbolList)

      if self.display_solution_distances:
        keys = list(self.metrics_plot.keys())
        if len(keys) > 0:
          for key in keys:
            self.metrics_plot[key].detach()
          self.metrics_plot = {}

    def insert_array_info(self):
      if self.is_vector:
        return

# draw dividing line for complex array
      if self.complex_type:  
          self.complex_marker = cm = QwtPlotMarker()
          cm.setLinePen(QPen(Qt.black, 2, Qt.SolidLine))
          cm.setValue(self.complex_divider,0.0)
          cm.setLineStyle(QwtPlotMarker.VLine)
          cm.attach(self)

# put in a line where cross sections are selected
      if not self.x_arrayloc is None:
          self.x_sect_marker = QwtPlotMarker()
          self.x_sect_marker.setLineStyle(QwtPlotMarker.HLine)
          self.x_sect_marker.setValue(0.0,self.x_arrayloc)
          self.markers['x_sect_marker'] = self.x_sect_marker
          self.markers['x_sect_marker'].attach(self)

      if not self.y_arrayloc is None:
          self.y_sect_marker = QwtPlotMarker()
          self.y_sect_marker.setLineStyle(QwtPlotMarker.VLine)
          self.y_sect_marker.setLinePen(QPen(Qt.white, 3, Qt.SolidLine))
          self.y_sect_marker.setValue(self.y_arrayloc,0.0)
          self.markers['y_sect_marker'] = self.y_sect_marker
          self.markers['y_sect_marker'].attach(self)

# insert markers for solver metrics?
      if self.toggle_metrics and not self.solver_offsets is None:
       shape = self.solver_offsets.shape 
       if shape[0] > 1:
         self.y_solver_offset = []

# insert mean and standard deviation
      text_string = ''
      if not self.array_parms is None:
        text_string = self.array_parms
# insert Condition Number Info if we have a solver with this information
      if not self.condition_numbers is None:
        cn_string = 'CN: ' + str(self.condition_numbers) + '\n' + 'CN * chi: ' + str(self.CN_chi)
        if len(text_string) > 0:
          text_string = text_string + '\n'+ cn_string
        else:
          text_string = cn_string
      if len(text_string) > 0:
        text = QwtText(text_string)
        text.setColor(Qt.red)
        text.setBackgroundBrush(QBrush(Qt.white))
        fn = self.fontInfo().family()
        text.setFont(QFont(fn, 7, QFont.Bold))
        self.info_marker = m = QwtPlotMarker()
        m.setLabelAlignment(Qt.AlignLeft | Qt.AlignBottom)
        m.setLabel(text)
        if not self.is_vector:
          xlb, xhb = self.plotImage.get_xMap_draw_coords()
          ylb, yhb = self.plotImage.get_yMap_draw_coords()
        m.setValue(xhb, yhb)
        m.attach(self)

      if self.log_offset > 0.0:
        temp_str = "Log offset: %-.3g" % self.log_offset
        text = QwtText(temp_str)
        text.setColor(Qt.red)
        text.setBackgroundBrush(QBrush(Qt.white))
        text.setFont(QFont(fn, 7, QFont.Bold))
        self.log_marker = l = QwtPlotMarker()
        if not self.is_vector:
          xlb, xhb = self.plotImage.get_xMap_draw_coords()
          ylb, yhb = self.plotImage.get_yMap_draw_coords()
        l.setValue(xhb,ylb)
        l.setLabelAlignment(Qt.AlignLeft | Qt.AlignTop)
        l.setLabel(text)
        l.attach(self)

    # insert_array_info()

    def plot_data(self, visu_record, attribute_list=None, label=''):
      """ process incoming data and attributes into the
          appropriate type of plot """
      if HAS_TIMBA:_dprint(2, 'in plot data');
#      if HAS_TIMBA:_dprint(2, 'visu_record ', visu_record)

# first find out what kind of plot we are making
      self.label = label
      self._plot_type = None
      self._window_title = None
      self._x_title = None
      self._y_title = None
      self._string_tag = None
      self._data_labels = None
      self._tag_plot_attrib={}
      if attribute_list is None: 
        if 'attrib' in visu_record:
          self._attrib_parms = visu_record['attrib']
          if HAS_TIMBA:_dprint(2,'self._attrib_parms ', self._attrib_parms);
          plot_parms = self._attrib_parms.get('plot')
          if 'tag_attrib' in plot_parms:
            temp_parms = plot_parms.get('tag_attrib')
            tag = temp_parms.get('tag')
            self._tag_plot_attrib[tag] = temp_parms
          if 'attrib' in plot_parms:
            temp_parms = plot_parms.get('attrib')
            plot_parms = temp_parms
          if self._plot_type is None and 'plot_type' in plot_parms:
            self._plot_type = plot_parms.get('plot_type')
          if self._display_type is None and 'spectrum_color' in plot_parms:
            self.setDisplayType(plot_parms.get('spectrum_color'))
          if 'tag' in self._attrib_parms:
            tag = self._attrib_parms.get('tag')
        else:
          self._plot_type = self.plot_key
      else:
# first get plot_type at first possible point in list - nearest root
        list_length = len(attribute_list)
        for i in range(list_length):
          self._attrib_parms = attribute_list[i]
          if 'plot' in self._attrib_parms:
            plot_parms = self._attrib_parms.get('plot')
            if 'tag_attrib' in plot_parms:
              temp_parms = plot_parms.get('tag_attrib')
              tag = temp_parms.get('tag')
              self._tag_plot_attrib[tag] = temp_parms
            if 'attrib' in plot_parms:
              temp_parms = plot_parms.get('attrib')
              plot_parms = temp_parms
            if self._plot_type is None and 'plot_type' in plot_parms:
              self._plot_type = plot_parms.get('plot_type')
            if self._window_title is None and 'title' in plot_parms:
              self.plot_title.setText(self.label+ ' '+ plot_parms.get('title'))
              self.setTitle(self.plot_title)
            if self._x_title is None and 'x_axis' in plot_parms:
              self._x_title = plot_parms.get('x_axis')
            if self._y_title is None and 'y_axis' in plot_parms:
              self._y_title = plot_parms.get('y_axis')
            if self._display_type is None and 'spectrum_color' in plot_parms:
              self.setDisplayType(plot_parms.get('spectrum_color'))
          if 'tag' in self._attrib_parms:
            tag = self._attrib_parms.get('tag')
            if self._string_tag is None:
              self._string_tag = ''
            if isinstance(tag, tuple):
              if HAS_TIMBA:_dprint(2,'tuple tag ', tag);
              for i in range(0, len(tag)):
                if self._string_tag.find(tag[i]) < 0:
                  temp_tag = self._string_tag + ' ' + tag[i]
                  self._string_tag = temp_tag
              if HAS_TIMBA:_dprint(2,'self._string_tag ', self._string_tag);
            else:
              if HAS_TIMBA:_dprint(2,'non tuple tag ', tag);
              if self._string_tag is None:
                self._string_tag = ''
              if self._string_tag.find(tag) < 0:
                temp_tag = self._string_tag + ' ' + tag
                self._string_tag = temp_tag

      if 'plot_label' in visu_record:
        self._data_labels = visu_record['plot_label']
        if HAS_TIMBA:_dprint(2,'insert_array_info: self._data_labels ', self._data_labels);
      else:
        self._data_labels = ''

# set defaults for anything that is not specified
      if self._string_tag is None:
        self._string_tag = ''
      if self._display_type is None:
        self.setDisplayType('hippo')
      if self._plot_type is None:
        self._plot_type = 'spectra'

      if 'value' in visu_record:
        self._data_values = visu_record['value']

      if len(self._tag_plot_attrib) > 0:
        if HAS_TIMBA:_dprint(3, 'self._tag_plot_attrib has keys ', list(self._tag_plot_attrib.keys()))

# extract and define labels for this data item
     # now generate  particular plot type
      if self._plot_type == 'spectra':
        self.num_y_markers = 0
        self.y_marker_step = None
# ensure that menu for display is updated if required
        self.initSpectrumContextMenu()
    # end plot_data()

    def plot_vells_array (self, data_array, data_label=''):
      """ plot a Vells data array """

#     if not self.source_marker is None:
#       self.removeMarker(self.source_marker)
      self.source_marker  = None
      self.array_plot(data_array, data_label=data_label)
      self.handleFlagRange()

    def setVellsParms(self, vells_axis_parms, axis_labels):
      self.vells_axis_parms = vells_axis_parms
      if HAS_TIMBA:_dprint(3, 'self.vells_axis_parms = ', self.vells_axis_parms)
      self.axis_labels = axis_labels

    def reset_color_bar(self, reset_value=True):
      self.adjust_color_bar = reset_value

    def set_xaxis_title(self, title=''):
      self._x_title = title
      self.setAxisTitle(QwtPlot.xBottom, self._x_title)

    def set_yaxis_title(self, title=''):
      self._y_title = title
      self.setAxisTitle(QwtPlot.yLeft, self._y_title)

    def enable_axes(self):
      self.enableAxis(QwtPlot.yLeft, True)
      self.enableAxis(QwtPlot.xBottom, True)
      self.enableAxis(QwtPlot.yRight, False)
      self.enableAxis(QwtPlot.xTop, False)

    def cleanup(self):
      self.removeCurves()        # removes all curves and markers
      self.removeMarkers()        # removes all curves and markers
      self.xrCrossSection = None
      self.xrCrossSection_flag = None
      self.xiCrossSection = None
      self.yCrossSection = None
      self.myXScale = None
      self.myYScale = None
      self.split_axis = None
      self.array_parms = None
      self.scalar_display = False
      self.zooming = True
      self.adjust_color_bar = True

    def array_plot (self, incoming_plot_array, data_label='', flip_axes=True):
      """ Figure out shape, rank dimension etc of an array and
          plot it. This is perhaps the main method of this class. """

      # test for shape change
      if incoming_plot_array.shape != self.previous_shape:
        self.previous_shape = incoming_plot_array.shape
        self.cleanup()
        self.enable_axes()

      if self.store_solver_array:
        self.solver_array = incoming_plot_array
        self.solver_title = data_label
         
# pop up menu for printing
      if self._menu is None:
        self._menu = QMenu(self._mainwin);
        self.add_basic_menu_items()
#       self.connect(self._menu,Qt.SIGNAL("activated(int)"),self.update_spectrum_display);
#       self.connect(self._menu,Qt.SIGNAL("triggered(QAction)"),self.update_spectrum_display);
        self._menu.triggered.connect(self.update_spectrum_display)


# set title
      self._window_title = data_label  
      if self.label == '' and  self._window_title == '':
        pass
      else:
        self.plot_title.setText(self.label+ ' ' + self._window_title)
        self.setTitle(self.plot_title)

# do we have solver data?
      if self._window_title.find('Solver Incremental') >= 0:
        self.solver_display = True
        self._toggle_metrics_display.setVisible(True)

        if self._window_title.find('Solver Incremental Solutions') >= 0:
            self._x_title = 'Solvable Coefficients'
            self._y_title = 'Iteration Nr'
        else:
            self._y_title = 'Value'
            self._x_title = 'Iteration Nr'

      if data_label == 'spectra: combined image':
        self.removeMarkers()
        self.info_marker = None
        self.log_marker = None
        self.source_marker = None
        self.is_combined_image = True
        self.reset_color_bar(True)
#       self.refresh_marker_display()

      self.original_array = incoming_plot_array
      self.original_label = data_label

# hack to get array display correct until forest.state
# record is available
      plot_array = incoming_plot_array
      axes = None
      self.array_flip = None
      if flip_axes:
        self.array_flip = flip_axes and not self.axes_flip
      else:
        self.array_flip = self.axes_flip
      if self.array_flip:
        axes = numpy.arange(incoming_plot_array.ndim)[::-1]
        plot_array = numpy.transpose(incoming_plot_array, axes)
#       if HAS_TIMBA:_dprint(3, 'transposed plot array ', plot_array, ' has shape ', plot_array.shape)

# figure out type and rank of incoming array
# for vectors, this is a pain as e.g. (8,) and (8,1) have
# different 'formal' ranks but really are the same 1-D vectors
# I'm not sure that the following covers all bases, but we are getting close

# first test for real or complex
      self.complex_type = False
      if plot_array.dtype == numpy.complex64:
        self.complex_type = True;
      if plot_array.dtype == numpy.complex128:
        self.complex_type = True;
      if self.complex_type:
        self._toggle_axis_rotate.setVisible(False)
#       self.show_colorbar_display.emit(1, 1)

# do an image rotation?
      if not self.complex_type and self.axes_rotate:
        plot_array = numpy.rot90(plot_array, 1)

      self.is_vector = False;
      actual_array_rank = 0
      num_elements = 1
      for i in range(len(plot_array.shape)):
        num_elements = num_elements * plot_array.shape[i]
        if plot_array.shape[i] > 1:
          actual_array_rank = actual_array_rank + 1
      if HAS_TIMBA:_dprint(3, 'actual array rank ', actual_array_rank)
      if actual_array_rank <= 1:
        self.is_vector = True;
        self.plotImage.detach()
      else:
        self.plotImage.attach(self)
      
# if we've doing a solver plot and we want to just display
# chi-square surfaces
      if self.display_solution_distances:
        self.is_vector = True
        self.plotImage.detach()

# check for NaNs and Infs etc
      self.has_nans_infs = False
      self.nan_inf_value = -0.1e-6
      nan_test = numpy.isnan(plot_array)
      inf_test = numpy.isinf(plot_array)
      if nan_test.max() > 0 or inf_test.max() > 0:
        self.has_nans_infs = True
        self.set_flag_toggles_active(True)
        delete = nan_test | inf_test
        keep = ~nan_test & ~inf_test
        self.setNanFlagsData(delete,False)
#       self.nan_inf_value = abs(plot_array[keep].mean() + -0.1e-6)
        if self.complex_type:
          plot_array[delete] = complex(self.nan_inf_value,self.nan_inf_value)
        else:
          plot_array[delete] = self.nan_inf_value


# I don't think we should ever see the N-D controller in the vector case.
# If self.original_data_rank > 2 that means that the cells dimensions are
# greater than the vector being plotted so we can turn off any ND Controller.
        if self.original_data_rank > 2: 
          self.toggle_ND_Controller = 0
          self._toggle_nd_controller.setVisible(False)
          self.show_ND_Controller.emit((self.toggle_ND_Controller,))

      if self.complex_type: 
        self.complex_image = plot_array

# add possibility to switch between real/imag and ampl/phase
      if self.complex_type:
        if self.ampl_phase is None:
#         self._toggle_ri_or_ap_display.setText('Show Data as Amplitude and Phase')
          self.ampl_phase = False
        self._toggle_ri_or_ap_display.setVisible(True)
        self._select_real_imaginary.setVisible(True)
        self._select_amplitude_phase.setVisible(True)
      else:
        self._toggle_ri_or_ap_display.setVisible(False)
        self._select_real_imaginary.setVisible(False)
        self._select_amplitude_phase.setVisible(False)

# test if we have a 2-D array
      if self.is_vector:
        self._toggle_log_range_for_data.setVisible(False)

      if self.is_vector == False and not self.log_switch_set:
        self._toggle_log_range_for_data.setVisible(True)
        self.log_switch_set = True

      if self.is_vector == False:
        if self.original_data_rank > 2: 
          self.toggle_ND_Controller = 1
          self._toggle_nd_controller.setVisible(True)
        if self.complex_type: 
          self.complex_divider = plot_array.shape[0]

# don't use grid markings for 2-D 'image' arrays
        self.grid.detach()

# make sure options relating to color bar are in context menu
        self._toggle_colorbar.setVisible(True)
        self._toggle_color_gray_display.setVisible(True)

# is zoom active?
        if len(self.zoomStack):
          self._reset_zoomer.setVisible(True)
          if self.is_vector and self.complex_type:
            self._undo_last_zoom.setVisible(False)
          else:
            self._undo_last_zoom.setVisible(True)

        self.active_image = True

# get mean and standard deviation of array
        temp_str = ""
        if self.complex_type:
          if plot_array.mean().imag < 0:
            temp_str = "m: %-.3g %-.3gj" % (plot_array.mean().real,plot_array.mean().imag)
          else:
            temp_str = "m: %-.3g+ %-.3gj" % (plot_array.mean().real,plot_array.mean().imag)
          #temp_str1 = "sd: %-.3g" % plot_array.std(dtype=numpy.complex128);
          temp_str1 = "sd: %-.3g" % plot_array.std();
        else:
          temp_str = "m: %-.3g" % plot_array.mean()
        temp_str1 = "sd: %-.3g" % plot_array.std(dtype=numpy.float64);
        self.array_parms = temp_str + " " + temp_str1
        if self.solver_display:
          self.array_parms = 'red: vector sum of incr solns\nblack: metrics rank 0\nblue:sum of the norms of incr solns\nyellow: norms of incr solns'
        self.setAxisTitle(QwtPlot.yLeft, 'sequence')
        if self.complex_type and self._display_type != "brentjens":
          ampl_phase_image = None
          if self.ampl_phase:
            ampl_phase_image = self.convert_to_AP(self.complex_image)
          if self._vells_plot:
            if HAS_TIMBA:_dprint(3, 'complex type: self._vells_plot ', self._vells_plot)
            self.x_parm = self.first_axis_parm
            self.y_parm = self.second_axis_parm
            if self.array_flip:
              self.x_parm = self.second_axis_parm
              self.y_parm = self.first_axis_parm
            self.myXScale = ComplexScaleDraw(start_value=self.vells_axis_parms[self.x_parm][0], end_value=self.vells_axis_parms[self.x_parm][1])
            self.complex_divider = self.vells_axis_parms[self.x_parm][1]

            self.setAxisScaleDraw(QwtPlot.xBottom, self.myXScale)
            self.split_axis = self.vells_axis_parms[self.x_parm][1] 
            delta_vells = self.vells_axis_parms[self.x_parm][1] - self.vells_axis_parms[self.x_parm][0]
            self.delta_vells = delta_vells
            self.first_axis_inc = delta_vells / plot_array.shape[0] 
            delta_vells = self.vells_axis_parms[self.y_parm][1] - self.vells_axis_parms[self.y_parm][0]
            self.second_axis_inc = delta_vells / plot_array.shape[1] 
            if self.ampl_phase:
              title_addition = ': (amplitude followed by phase)'
            else:
              title_addition = ': (real followed by imaginary)'
            self._x_title = self.vells_axis_parms[self.x_parm][2] + title_addition
            # reverse direction of x coordinates?
            if self.axes_rotate:
              self.setAxisAutoScale(QwtPlot.xBottom)
              scale_engine = self.axisScaleEngine(QwtPlot.xBottom)
              scale_engine.setAttributes(Qwt.QwtScaleEngine.Inverted)
            self.setAxisAutoScale(QwtPlot.xBottom)
            self.setAxisTitle(QwtPlot.xBottom, self._x_title)
            self._y_title = self.vells_axis_parms[self.y_parm][2]
            self.setAxisTitle(QwtPlot.yLeft, self._y_title)
          else:
            if self.ampl_phase:
              if self.array_flip:
                self._x_title = 'Array/Channel Number (amplitude followed by phase)'
              else:
                self._x_title = 'Array/Sequence Number (amplitude followed by phase)'
            else:
              if self.array_flip:
                self._x_title = 'Array/Channel Number (real followed by imaginary)'
              else:
                self._x_title = 'Array/Sequence Number (real followed by imaginary)'
            self.setAxisTitle(QwtPlot.xBottom, self._x_title)
            if self.array_flip:
              self._y_title = 'Array/Sequence Number'
            else:
              self._y_title = 'Array/Channel Number'
            self.setAxisTitle(QwtPlot.yLeft, self._y_title)
            self.myXScale = ComplexScaleDraw(divisor=plot_array.shape[0])
            self.setAxisScaleDraw(QwtPlot.xBottom, self.myXScale)

            self.split_axis = plot_array.shape[0]
            if HAS_TIMBA:_dprint(3,'testing self.y_marker_step ', self.y_marker_step)
            if not self.y_marker_step is None:
              if HAS_TIMBA:_dprint(3, 'creating split Y scale for Y axis')
              self.myYScale = ComplexScaleDraw(divisor=self.y_marker_step)
              self.setAxisScaleDraw(QwtPlot.yLeft, self.myYScale)

          if self.ampl_phase:
            self.display_image(ampl_phase_image)
          else:
            self.display_image(plot_array)

        else:
          if self._vells_plot:
            if HAS_TIMBA:_dprint(3, 'not complex type: self._vells_plot ', self._vells_plot)
            if HAS_TIMBA:_dprint(3, 'self.vells_axis_parms ',self.vells_axis_parms)
            self.x_parm = self.first_axis_parm
            self.y_parm = self.second_axis_parm
            if self.array_flip:
              self.x_parm = self.second_axis_parm
              self.y_parm = self.first_axis_parm
            if self.axes_rotate:
              temp = self.x_parm
              self.x_parm = self.y_parm
              self.y_parm = temp
            if HAS_TIMBA:_dprint(3, 'self.x_parm self.y_parm ', self.x_parm, ' ', self.y_parm)
            delta_vells = self.vells_axis_parms[self.x_parm][1] - self.vells_axis_parms[self.x_parm][0]
            self.delta_vells = delta_vells
            self.first_axis_inc = delta_vells // plot_array.shape[0] 
            delta_vells = self.vells_axis_parms[self.y_parm][1] - self.vells_axis_parms[self.y_parm][0]
            self.second_axis_inc = delta_vells // plot_array.shape[1] 
            self._x_title = self.vells_axis_parms[self.x_parm][2]
            self.setAxisTitle(QwtPlot.xBottom, self._x_title)
            self._y_title = self.vells_axis_parms[self.y_parm][2]
            self.setAxisTitle(QwtPlot.yLeft, self._y_title)
            # reverse direction of x coordinates?
#           self.setAxisOptions(QwtPlot.xBottom, QwtAutoScale.None)
            self.setAxisAutoScale(QwtPlot.xBottom)
            if self.axes_rotate:
              self.setAxisAutoScale(QwtPlot.xBottom)
              scale_engine = self.axisScaleEngine(QwtPlot.xBottom)
              scale_engine.setAttributes(Qwt.QwtScaleEngine.Inverted)
          else:
            if self.solver_display is True:
              if not self.array_flip:
                self._y_title = 'Solvable Coefficients'
                self._x_title = 'Iteration Nr'
            if self._x_title is None:
              if self.array_flip:
                self._x_title = 'Array/Channel Number'
              else:
                self._x_title = 'Array/Sequence Number'
            self.setAxisTitle(QwtPlot.xBottom, self._x_title)
            if self._y_title is None:
              if self.array_flip:
                self._y_title = 'Array/Sequence Number'
              else:
                self._y_title = 'Array/Channel Number'
            self.setAxisTitle(QwtPlot.yLeft, self._y_title)
            if not self.y_marker_step is None:
              if HAS_TIMBA:_dprint(3, 'creating split Y scale for Y axis ', self.y_marker_step)
              self.myYScale = ComplexScaleDraw(divisor=self.y_marker_step)
              self.setAxisScaleDraw(QwtPlot.yLeft, self.myYScale)
          self.display_image(plot_array)

      if self.is_vector == True:
        if HAS_TIMBA:_dprint(3, ' we are plotting a vector')

# remove any markers and reset curves
        if not self.scalar_display:
          self.cleanup()
          self.enable_axes()
          self.removeMarkers()
# make sure color bar is hidden
        self.show_colorbar_display.emit(0, 0)
        if self.complex_type:
          self.show_colorbar_display.emit(0, 1)

# make sure options relating to 2-D stuff are not visible in context menu
        self._toggle_colorbar.setVisible(False)
        self._toggle_color_gray_display.setVisible(False)
        self._toggle_nd_controller.setVisible(False)
        self._toggle_3d_display.setVisible(False)
        self._toggle_warp_display.setVisible(False)
        self._toggle_axis_flip.setVisible(False)
        self._toggle_axis_rotate.setVisible(False)

# make sure we are autoscaling in case an image was previous
# this will automagically do an unzoom, but just in case first
# call reset_zoom ...
        self.reset_zoom()

        self.setAxisAutoScale(QwtPlot.xBottom)
        self.setAxisAutoScale(QwtPlot.xTop)
        self.setAxisAutoScale(QwtPlot.yLeft)
        self.setAxisAutoScale(QwtPlot.yRight)
        self._x_auto_scale = True
        self._y_auto_scale = True

        q_line_size = 2
        q_symbol_size = 5
        q_flag_size = 20
        q_size_split = 300
        if num_elements > q_size_split:
          q_line_size = 1
          q_symbol_size = 3
          q_flag_size = 10
        

# make sure grid markings are on in case an image was previously displayed
        self.grid.attach(self)

        if not self._flags_array is None:
          self.flags_x_index = []
          self.flags_r_values = []
          self.flags_i_values = []
        self.active_image = False


# are we displaying chi-square surfaces?
        if self.display_solution_distances:
          if not self.metrics_rank is None:
            self.add_solver_metrics()
            self.replot()
            #print 'called first replot in array_plot' 
            return

        if self._vells_plot:
# we have a vector so figure out which axis we are plotting
          self.x_parm = self.first_axis_parm
          self.y_parm = self.second_axis_parm
          if self.array_flip:
            self.x_parm = self.second_axis_parm
            self.y_parm = self.first_axis_parm
# now do a check in case we have selected the wrong plot axis
          if  self.x_parm is None:
            self.x_parm = self.y_parm
          delta_vells = self.vells_axis_parms[self.x_parm][1] - self.vells_axis_parms[self.x_parm][0]
          x_step = delta_vells // num_elements 
          start_x = self.vells_axis_parms[self.x_parm][0] + 0.5 * x_step
          self.x_index = numpy.zeros(num_elements, numpy.float32)
          for j in range(num_elements):
            self.x_index[j] = start_x + j * x_step
          self._x_title = self.vells_axis_parms[self.x_parm][2]
          self.setAxisTitle(QwtPlot.xBottom, self._x_title)
        else:
          if self._x_title is None:
            self._x_title = 'Array/Channel/Sequence Number'
          self.setAxisTitle(QwtPlot.xBottom, self._x_title)
          self.x_index = numpy.arange(num_elements)
          self.x_index = self.x_index + 0.5
# if we are plotting a single iteration solver solution
# plot on 'locations' of solver parameters. Use 'self.metrics_rank'
# as test, but don't plot metrics in this case
          if not self.metrics_rank is None:
            self.x_index = self.x_index + 0.5
        flattened_array = numpy.reshape(plot_array,(num_elements,))

# we have a complex vector
        if self.complex_type:
          self.enableAxis(QwtPlot.yRight, True)
          self.enableAxis(QwtPlot.yLeft, True)
          self.enableAxis(QwtPlot.xBottom, True)
          if self.ampl_phase:
            text =QwtText('Value: Amplitude (black line / red dots)')
            text.setFont(self.title_font)
            self.setAxisTitle(QwtPlot.yLeft, text)
            text.setText('Value: Phase (blue line / green dots)')
            self.setAxisTitle(QwtPlot.yRight, text)
            self.yCrossSection = QwtPlotCurve('phase')
            self.xrCrossSection = QwtPlotCurve('amplitude')
            self.curves['phase'] = self.yCrossSection 
            self.curves['amplitude'] = self.xrCrossSection 
          else:
            text =QwtText('Value: real (black line / red dots)')
            text.setFont(self.title_font)
            self.setAxisTitle(QwtPlot.yLeft, text)
            text.setText('Value: imaginary (blue line / green dots)')
            self.setAxisTitle(QwtPlot.yRight, text)
            self.yCrossSection = QwtPlotCurve('imaginaries')
            self.xrCrossSection = QwtPlotCurve('reals')
            self.curves['imaginaries'] = self.yCrossSection 
            self.curves['reals'] = self.xrCrossSection 
          self.yCrossSection.attach(self)
          self.xrCrossSection.attach(self)
          self.xrCrossSection.setPen(QPen(Qt.black, q_line_size))
          self.yCrossSection.setPen(QPen(Qt.blue, q_line_size))
          self.yCrossSection.setYAxis(QwtPlot.yRight)
          self.yCrossSection.setXAxis(QwtPlot.xBottom)
          self.setAxisAutoScale(QwtPlot.xTop)
          self.setAxisAutoScale(QwtPlot.yLeft)
          self.xrCrossSection.setAxes(QwtPlot.xBottom, QwtPlot.yLeft)
          self.xrCrossSection.setYAxis(QwtPlot.yLeft)
          self.xrCrossSection.setXAxis(QwtPlot.xBottom)
          self.xrCrossSection.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.red),
                     QPen(Qt.red), QSize(q_symbol_size,q_symbol_size)))
          self.yCrossSection.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.green),
                     QPen(Qt.green), QSize(q_symbol_size,q_symbol_size)))
          self.x_array =  flattened_array.real
          self.y_array =  flattened_array.imag
          # never show NaNs
          if not self._nan_flags_array is None:
            if  self._flags_array is None:
              self._flags_array = self._nan_flags_array
            else:
              self._flags_array = self._nan_flags_array + self._flags_array
          if not self._flags_array is None:
            if self.ampl_phase:
              self.yCrossSection_flag = QwtPlotCurve('flag_phase')
              self.xrCrossSection_flag = QwtPlotCurve('flag_amplitude')
              self.curves['flag_phase'] = self.yCrossSection 
              self.curves['flag_amplitude'] = self.xrCrossSection 
            else:
              self.yCrossSection_flag = QwtPlotCurve('flag_imaginaries')
              self.xrCrossSection_flag = QwtPlotCurve('flag_reals')
              self.curves['flag_imaginaries'] = self.yCrossSection 
              self.curves['flag_reals'] = self.xrCrossSection 
            self.yCrossSection_flag.attach(self)
            self.xrCrossSection_flag.attach(self)
            self.xrCrossSection_flag.setPen(QPen(Qt.black, q_line_size))
            self.yCrossSection_flag.setPen(QPen(Qt.blue, q_line_size))
            self.xrCrossSection_flag.setAxes(QwtPlot.xBottom, QwtPlot.yLeft)
#           self.yCrossSection_flag.setYAxis(QwtPlot.yRight)
#           self.yCrossSection_flag.setXAxis(QwtPlot.xTop)
            self.yCrossSection_flag.setAxes(QwtPlot.xBottom, QwtPlot.yRight)
            self.xrCrossSection_flag.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.red),
                     QPen(Qt.red), QSize(q_symbol_size,q_symbol_size)))
            self.yCrossSection_flag.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.green),
                     QPen(Qt.green), QSize(q_symbol_size,q_symbol_size)))
          if self.ampl_phase:
            abs_array = abs(flattened_array)
            phase_array = numpy.arctan2(self.y_array,self.x_array)
            self.x_array = abs_array
            self.y_array = phase_array
          if not self._flags_array is None:
            flags_x_array = numpy.compress(self._flags_array==0,self.x_array)
            flags_y_array = numpy.compress(self._flags_array==0,self.y_array)
            self.yCrossSection_flag.setData(self.x_index, self.y_array)
            self.xrCrossSection_flag.setData(self.x_index, self.x_array)
            flags_x_index = numpy.compress(self._flags_array==0,self.x_index)
            self.yCrossSection.setData(flags_x_index, flags_y_array)
            self.xrCrossSection.setData(flags_x_index, flags_x_array)
            axis_diff = abs(flags_y_array.max() - flags_y_array.min())
          else:
            axis_diff = abs(self.y_array.max() - self.y_array.min())
            self.yCrossSection.setData(self.x_index, self.y_array)
            self.xrCrossSection.setData(self.x_index, self.x_array)
          # the following is not the best test, but ...
          axis_subt = 0.01 * axis_diff
          if axis_diff <0.00001:
            axis_diff = 0.005
            axis_subt = 0.002
          if not self._flags_array is None:
            min_val = flags_y_array.min() - axis_subt
            max_val = flags_y_array.max() + axis_diff
            if self.has_nans_infs:
              if flags_y_array.min() > self.nan_inf_value: 
                min_val = self.nan_inf_value - axis_subt
              if flags_y_array.max() < self.nan_inf_value: 
                max_val = self.nan_inf_value + axis_diff
            self.setAxisScale(QwtPlot.yRight, min_val, max_val)
          else:
            self.setAxisScale(QwtPlot.yRight, self.y_array.min() - axis_subt, self.y_array.max() + axis_diff)
          if not self._flags_array is None:
            axis_diff = abs(flags_x_array.max() - flags_x_array.min())
          else:
            axis_diff = abs(self.x_array.max() - self.x_array.min())
          axis_add = 0.01 * axis_diff
          if axis_diff <0.00001:
            axis_diff = 0.005
            axis_add = 0.002
          if not self._flags_array is None:
            min_val = flags_x_array.min() - axis_diff
            max_val = flags_x_array.max() + axis_add
            if self.has_nans_infs:
              if flags_x_array.min() > self.nan_inf_value: 
                min_val = self.nan_inf_value - axis_diff
              if flags_x_array.max() < self.nan_inf_value: 
                max_val = self.nan_inf_value + axis_add
            self.setAxisScale(QwtPlot.yLeft, min_val, max_val)
          else:
            self.setAxisScale(QwtPlot.yLeft, self.x_array.min() - axis_diff, self.x_array.max() + axis_add)
          if HAS_TIMBA:
            _dprint(3, 'plotting complex array with x values ', self.x_index)
            _dprint(3, 'plotting complex array with real values ', self.x_array)
            _dprint(3, 'plotting complex array with imag values ', self.y_array)

# stuff for flags
          if not self._flags_array is None:
            self.flags_x_index = numpy.compress(self._flags_array!=0,self.x_index)
            self.flags_r_values = numpy.compress(self._flags_array!=0,self.x_array)
            self.flags_i_values = numpy.compress(self._flags_array!=0,self.y_array)

            self.real_flag_vector = QwtPlotCurve('real_flags')
            self.curves['real_flags'] = self.real_flag_vector 
            self.real_flag_vector.attach(self)
            self.real_flag_vector.setPen(QPen(Qt.black))
            self.real_flag_vector.setStyle(QwtPlotCurve.Dots)
            self.real_flag_vector.setYAxis(QwtPlot.yLeft)
            self.real_flag_vector.setSymbol(QwtSymbol(QwtSymbol.XCross, QBrush(Qt.black),
                     QPen(Qt.black), QSize(q_flag_size, q_flag_size)))
            self.real_flag_vector.setData(self.flags_x_index, self.flags_r_values)
            self.imag_flag_vector = QwtPlotCurve('imag_flags')
            self.curves['imag_flags'] = self.imag_flag_vector 
            self.imag_flag_vector.attach(self)
            self.imag_flag_vector.setPen(QPen(Qt.black))
            self.imag_flag_vector.setStyle(QwtPlotCurve.Dots)
            self.imag_flag_vector.setYAxis(QwtPlot.yRight)
            self.imag_flag_vector.setSymbol(QwtSymbol(QwtSymbol.XCross, QBrush(Qt.black),
                     QPen(Qt.black), QSize(q_flag_size, q_flag_size)))
            self.imag_flag_vector.setData(self.flags_x_index, self.flags_i_values)
            
            if self.flag_toggle:
              self.real_flag_vector.show()
              self.imag_flag_vector.show()
              self.yCrossSection_flag.show()
              self.xrCrossSection_flag.show()
              self.yCrossSection.hide()
              self.xrCrossSection.hide()
            else:
              self.real_flag_vector.hide()
              self.imag_flag_vector.hide()
              self.yCrossSection_flag.hide()
              self.xrCrossSection_flag.hide()
              self.yCrossSection.show()
              self.xrCrossSection.show()

        else:
          self.enableAxis(QwtPlot.yLeft, True)
          self.enableAxis(QwtPlot.xBottom, True)
          self.enableAxis(QwtPlot.yRight, False)
          self.setAxisTitle(QwtPlot.yLeft, 'Value')
          self.x_array =  flattened_array
          self.xrCrossSection = QwtPlotCurve('reals')
          self.curves['reals'] = self.xrCrossSection 
          self.xrCrossSection.attach(self)
          self.xrCrossSection.setPen(QPen(Qt.black, q_line_size))
          self.xrCrossSection.setStyle(QwtPlotCurve.Lines)
          self.xrCrossSection.setAxes(QwtPlot.xBottom,QwtPlot.yLeft)
          self.xrCrossSection.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.red),
                     QPen(Qt.red), QSize(q_symbol_size,q_symbol_size)))
          # never show NaNs
          if not self._nan_flags_array is None:
            if  self._flags_array is None:
              self._flags_array = self._nan_flags_array
            else:
              self._flags_array = self._nan_flags_array + self._flags_array
          if not self._flags_array is None:
            self.xrCrossSection_flag = QwtPlotCurve('flag_reals')
            self.curves['flag_reals'] = self.xrCrossSection 
            self.xrCrossSection_flag.attach(self)
            self.xrCrossSection_flag.setPen(QPen(Qt.black, q_line_size))
            self.xrCrossSection_flag.setStyle(QwtPlotCurve.Lines)
            self.xrCrossSection_flag.setAxes(QwtPlot.xBottom,QwtPlot.yLeft)
            self.xrCrossSection_flag.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.red),
                     QPen(Qt.red), QSize(q_symbol_size,q_symbol_size)))
            flags_x_array = numpy.compress(self._flags_array==0,self.x_array)
            flags_x_index = numpy.compress(self._flags_array==0,self.x_index)
            axis_diff = abs(flags_x_array.max() - flags_x_array.min())
            self.xrCrossSection_flag.setData( self.x_index, self.x_array)
            self.xrCrossSection.setData(flags_x_index, flags_x_array)

# stuff for flags
            self.flags_x_index = numpy.compress(self._flags_array!= 0, self.x_index)
            self.flags_r_values = numpy.compress(self._flags_array!= 0, self.x_array)
            self.real_flag_vector = QwtPlotCurve('real_flags')
            self.curves['real_reals'] = self.xrCrossSection 
            self.real_flag_vector.attach(self)
            self.real_flag_vector.setPen( QPen(Qt.black))
            self.real_flag_vector.setStyle(QwtPlotCurve.Dots)
            self.real_flag_vector.setAxes(QwtPlot.xBottom, QwtPlot.yLeft)
            self.real_flag_vector.setSymbol(QwtSymbol(QwtSymbol.XCross, QBrush(Qt.black),
                     QPen(Qt.black), QSize(q_flag_size, q_flag_size)))
            self.real_flag_vector.setData(self.flags_x_index, self.flags_r_values)
            if self.flag_toggle:
              self.real_flag_vector.show()
              self.xrCrossSection_flag.show()
              self.xrCrossSection.hide()
            else:
              self.real_flag_vector.hide()
              self.xrCrossSection_flag.hide()
              self.xrCrossSection.show()
            axis_add = abs(0.01 * axis_diff)
            if axis_diff <0.00001:
              axis_add = 0.002
            min_val = flags_x_array.min() - axis_add
            max_val = flags_x_array.max() + axis_add
            if self.has_nans_infs:
              if flags_x_array.min() > self.nan_inf_value: 
                min_val = self.nan_inf_value - axis_add
              if flags_x_array.max() < self.nan_inf_value: 
                max_val = self.nan_inf_value + axis_add
            self.setAxisScale(QwtPlot.yLeft, min_val, max_val)
          else:
            self.xrCrossSection.setData(self.x_index, self.x_array)

        self.replot()
        if HAS_TIMBA:_dprint(3, 'called replot in array_plot');
        #print 'called final replot in array_plot'

    # array_plot()

    def set_solver_metrics(self,metrics_tuple):
      """ store Solver data for later plotting """
      self.metrics_rank = metrics_tuple[0]
      self.iteration_number = metrics_tuple[1]
      self.solver_offsets = metrics_tuple[2]
      self.chi_vectors = metrics_tuple[3]
      self.chi_zeros = metrics_tuple[4]
      self.nonlin = metrics_tuple[5]
      self.sum_incr_soln_norm = metrics_tuple[6]
      self.incr_soln_norm = metrics_tuple[7]
      self.metrics_fit = metrics_tuple[8]
      self.metrics_chi = metrics_tuple[9]
      self.metrics_mu = metrics_tuple[10]
      self.metrics_flag = metrics_tuple[11]
      self.metrics_stddev = metrics_tuple[12]
      self.metrics_unknowns = metrics_tuple[13]
      self.store_solver_array = True
      self.solver_array = None
      self.solver_title = None

    def convert_to_AP(self, real_imag_image):
      """ convert real/imag complex array to amplitude/phase equivalent """
      a_p_image = real_imag_image.copy()
      real_array = a_p_image.real
      imag_array = a_p_image.imag
      abs_array = numpy.abs(a_p_image)
      phase_array = numpy.arctan2(imag_array,real_array)
      a_p_image.real = abs_array
      a_p_image.imag = phase_array
      return a_p_image

    def setFlagsData (self, incoming_flag_array, flip_axes=True):
      """ figure out shape, rank etc of a flag array and plot it  """
      flag_array = incoming_flag_array
      self.original_flag_array = incoming_flag_array
      if flip_axes and not self.axes_flip:
        axes = numpy.arange(incoming_flag_array.ndim)[::-1]
        flag_array = numpy.transpose(incoming_flag_array, axes)
        if not self.complex_type and self.axes_rotate:
          temp_flag_array = flag_array.copy()
          flag_array = numpy.rot90(temp_flag_array, 1)

# figure out type and rank of incoming array
      flag_is_vector = False;
      actual_array_rank = 0
      for i in range(len(flag_array.shape)):
        if flag_array.shape[i] > 1:
          actual_array_rank = actual_array_rank + 1
      if actual_array_rank == 1:
        flag_is_vector = True;

      n_rows = 1
      n_cols = 1
      if actual_array_rank == 1:
        n_rows = flag_array.shape[0]
        if len(flag_array.shape) > 1:
          n_cols = flag_array.shape[1]

      if flag_is_vector == False:
        self._flags_array = flag_array
        self.plotImage.setFlagsArray(flag_array)
        if self.flag_toggle is None:
          self.flag_toggle = True
          self.plotImage.setDisplayFlag(self.flag_toggle)
          self._toggle_flagged_data_for_plane.setChecked(not self.flag_toggle)
      else:
        num_elements = n_rows*n_cols
        self._flags_array = flag_array.reshape(num_elements);
        if self.flag_toggle is None:
          self.flag_toggle = False
          self._toggle_flagged_data_for_plane.setChecked(self.flag_toggle)

    # setFlagsData()

    def setNanFlagsData (self, incoming_nan_flag_array, flip_axes=True):
      """ figure out shape, rank etc of a flag array and plot it  """
      nan_flag_array = incoming_nan_flag_array * 10 
      self.original_nan_flag_array = incoming_nan_flag_array
      if flip_axes and not self.axes_flip:
        axes = numpy.arange(incoming_nan_flag_array.ndim)[::-1]
        nan_flag_array = numpy.transpose(incoming_nan_flag_array, axes)
        if not self.complex_type and self.axes_rotate:
          temp_flag_array = nan_flag_array.copy()
          nan_flag_array = numpy.rot90(temp_flag_array, 1)

# figure out type and rank of incoming array
      nan_flag_is_vector = False;
      actual_array_rank = 0
      for i in range(len(nan_flag_array.shape)):
        if nan_flag_array.shape[i] > 1:
          actual_array_rank = actual_array_rank + 1
      if actual_array_rank == 1:
        nan_flag_is_vector = True;

      n_rows = 1
      n_cols = 1
      if actual_array_rank == 1:
        n_rows = nan_flag_array.shape[0]
        if len(nan_flag_array.shape) > 1:
          n_cols = nan_flag_array.shape[1]

      if nan_flag_is_vector == False:
        self._nan_flags_array = nan_flag_array
        self.plotImage.setNanFlagsArray(nan_flag_array)
        self.plotImage.setDisplayFlag(True)
      else:
        num_elements = n_rows*n_cols
        self._nan_flags_array = nan_flag_array.reshape(num_elements);
    # setNanFlagsData()

    def message_reporter(self, message):
      mb_reporter = QMessageBox.information(self, "QwtImageDisplay",message)

    def unsetFlagsData(self):
      self._flags_array = None
      self._nan_flags_array = None
      self.flags_x_index = []
      self.flags_r_values = []
      self.flags_i_values = []
      self.plotImage.removeFlags()
      self.plotImage.setDisplayFlag(False)
      self.flag_toggle = None

    def handle_select_cross_section (self,*dum):
      """Called when a cross-section selection changes""";
      if self.show_x_sections:
        # set selected flag based on qaction checked states
        self.real_xsection_selected = \
            self._select_both_cross_sections.isChecked() or \
            self._select_real_cross_section.isChecked() or \
            self._select_amplitude_cross_section.isChecked();
        self.imag_xsection_selected = \
            self._select_both_cross_sections.isChecked() or \
            self._select_imaginary_cross_section.isChecked() or \
            self._select_phase_cross_section.isChecked();
        # detach old cross-sections, if they're de-selected
        if not self.real_xsection_selected:
          try:
            self.xrCrossSection.detach();
          except:
            pass;
          self.xrCrossSection = None;
        if not self.imag_xsection_selected:
          try:
            self.xiCrossSection.detach();
          except:
            pass;
          self.xiCrossSection = None;
        # calculate new cross-sections if needed, and replot
        if self.xrCrossSection is None or self.xiCrossSection is None:
          self.calculate_cross_sections()
        self.replot()

    def handle_reset_zoomer(self):
      if self.is_vector and self.complex_type:
        replot = True
      else:
        replot = False
      self.reset_zoom(replot)

    def handle_undo_last_zoom(self):
      replot = False
      self.reset_zoom(replot, True)

    def handle_save_display_in_png_format(self):
      self.save_display.emit(self._window_title)

    def handle_modify_plot_parameters(self):
      message = 'The option to modify plot parameters does not work at present'
      self.message_reporter(message)
#     self.updatePlotParameters()

    def add_basic_menu_items(self):
        """ add standard options to context menu """

# first create sub-menu for cross-section displays
        self._xsection_menu = QMenu(self._mainwin);
        qag = QActionGroup(self._xsection_menu);
        qag.setExclusive(True);

        self._select_both_cross_sections = qag.addAction('Both');
        self._select_real_cross_section = qag.addAction('Real only');
        self._select_imaginary_cross_section = qag.addAction('Imaginary only');
        self._select_amplitude_cross_section = qag.addAction('Amplitude only');
        self._select_phase_cross_section = qag.addAction('Phase only');
        
        for qa in ( self._select_both_cross_sections,
                    self._select_real_cross_section,
                    self._select_imaginary_cross_section, 
                    self._select_amplitude_cross_section, 
                    self._select_phase_cross_section ):
          qa.setCheckable(True); 
          qa.setVisible(False);
          self._xsection_menu.addAction(qa);
        qag.triggered[QAction].connect(self.handle_select_cross_section)

        self._delete_cx_section_display = self._xsection_menu.addAction('None');
        self._delete_cx_section_display.triggered.connect(self.handle_delete_x_section_display)


# create sub-menu for complex data selection
        self._complex_data_menu = QMenu(self._mainwin);

        toggle_id = self.complex_menu_table['Show Data as Real and Imaginary']
        self._select_real_imaginary = QAction('Real-imaginary',self)
        self._select_real_imaginary.setData(str(toggle_id))
        self._complex_data_menu.addAction(self._select_real_imaginary)
        self._select_real_imaginary.setVisible(False)
        self._select_real_imaginary.setCheckable(True)
        self._select_real_imaginary.setChecked(True)
        self._select_real_imaginary.triggered.connect(self.handle_toggle_ri_display)

        toggle_id = self.complex_menu_table['Show Data as Amplitude and Phase']
        self._select_amplitude_phase = QAction('Amplitude-phase',self)
        self._select_amplitude_phase.setData(str(toggle_id))
        self._complex_data_menu.addAction(self._select_amplitude_phase)
        self._select_amplitude_phase.setVisible(False)
        self._select_amplitude_phase.setCheckable(True)
        self._select_amplitude_phase.setChecked(False)
        self._select_amplitude_phase.triggered.connect(self.handle_toggle_ap_display)

        toggle_id = self.menu_table['Show coordinate tracking display']
        self._toggle_coordinates = QAction('Show coordinate tracking display',self)
        self._menu.addAction(self._toggle_coordinates)
        self._toggle_coordinates.setData(str(toggle_id))
        self._toggle_coordinates.setText('Show coordinate tracker')
        self._toggle_coordinates.setCheckable(True)
        self._toggle_coordinates.triggered.connect(self.handle_toggle_coordinates)


        toggle_id = self.menu_table['Show ColorBar']
        self._toggle_colorbar = QAction('Show ColorBar',self)
        self._menu.addAction(self._toggle_colorbar)
        self._toggle_colorbar.setData(str(toggle_id))
        self._toggle_colorbar.setText('Show colour bar')
        self._toggle_colorbar.setCheckable(True)
        self._toggle_colorbar.setChecked(True)
        self._toggle_colorbar.triggered.connect(self.handle_toggle_colorbar)

        toggle_id = self.menu_table['Show GrayScale Display']
        self._toggle_color_gray_display = QAction('Show GrayScale Display',self)
        self._menu.addAction(self._toggle_color_gray_display)
        self._toggle_color_gray_display.setData(str(toggle_id))
        self._toggle_color_gray_display.setText('Use greyscale display')
        self._toggle_color_gray_display.setCheckable(True)
        self._toggle_color_gray_display.triggered.connect(self.handle_toggle_color_gray_display)

        toggle_id = self.menu_table['Hide ND Controller']
        self._toggle_nd_controller = QAction('Hide nD controller',self)
        self._menu.addAction(self._toggle_nd_controller)
        self._toggle_nd_controller.setData(str(toggle_id))
        self._toggle_nd_controller.setText('Hide nD controller')
        self._toggle_nd_controller.setVisible(False)
        self._toggle_nd_controller.setCheckable(True)
        self._toggle_nd_controller.triggered.connect(self.handle_toggle_nd_controller)


        toggle_id = self.menu_table['Show results history']
        self._toggle_results_history = QAction('Show results history',self)
        self._menu.addAction(self._toggle_results_history)
        self._toggle_results_history.setData(str(toggle_id))
        self._toggle_results_history.setVisible(False)
        self._toggle_results_history.setCheckable(True)
        self._toggle_results_history.triggered.connect(self.handle_toggle_results_history)


        toggle_id = self.menu_table['Select X-Section Display']
        self._select_x_section_display = QAction('Plot which cross-sections',self)
        self._menu.addAction(self._select_x_section_display)
        self._select_x_section_display.setMenu(self._xsection_menu)
        self._select_x_section_display.setData(str(toggle_id))
        self._select_x_section_display.setVisible(False)
#       self.connect(self._select_x_section_display,Qt.SIGNAL("triggered()"),self.handle_select_x_section_display);


        toggle_id = self.menu_table['Interchange axes']
        self._toggle_axis_flip = QAction('Interchange x/y axes',self)
        self._menu.addAction(self._toggle_axis_flip)
        self._toggle_axis_flip.setData(str(toggle_id))
        self._toggle_axis_flip.setVisible(False)
        self._toggle_axis_flip.setCheckable(True)
        self._toggle_axis_flip.triggered.connect(self.handle_toggle_axis_flip)



        toggle_id = self.menu_table['Toggle axis rotate']
        self._toggle_axis_rotate = QAction('Toggle axis rotate',self)
        self._menu.addAction(self._toggle_axis_rotate)
        self._toggle_axis_rotate.setData(str(toggle_id))
        self._toggle_axis_rotate.setText('Rotate axes 90deg counterclockwise')
        self._toggle_axis_rotate.setVisible(False)
        self._toggle_axis_rotate.setCheckable(True)
        self._toggle_axis_rotate.triggered.connect(self.handle_toggle_axis_rotate)


        toggle_id = self.menu_table['Show logarithmic range for chi_0']
        self._toggle_log_axis_for_chi_0 = QAction('Use logarithmic range for chi_0',self)
        self._menu.addAction(self._toggle_log_axis_for_chi_0)
        self._toggle_log_axis_for_chi_0.setData(str(toggle_id))
        self._toggle_log_axis_for_chi_0.setVisible(False)
        self._toggle_log_axis_for_chi_0.setCheckable(True)
        self._toggle_log_axis_for_chi_0.triggered.connect(self.handle_toggle_log_axis_for_chi_0)


        toggle_id = self.menu_table['Show logarithmic range for solution vector']
        self._toggle_log_axis_for_solution_vector = QAction('Use logarithmic range for solution vector',self)
        self._menu.addAction(self._toggle_log_axis_for_solution_vector)
        self._toggle_log_axis_for_solution_vector.setData(str(toggle_id))
        self._toggle_log_axis_for_solution_vector.setVisible(False)
        self._toggle_log_axis_for_solution_vector.setCheckable(True)
        self._toggle_log_axis_for_solution_vector.triggered.connect(self.handle_toggle_log_axis_for_solution_vector)


        toggle_id = self.menu_table['Toggle chi-square surfaces display']
        self._toggle_chi_square_surfaces_display = QAction('Toggle chi-square surfaces display',self)
        self._menu.addAction(self._toggle_chi_square_surfaces_display)
        self._toggle_chi_square_surfaces_display.setData(str(toggle_id))
        self._toggle_chi_square_surfaces_display.setVisible(False)
        self._toggle_chi_square_surfaces_display.setText('Show chi-square surfaces')
        self._toggle_chi_square_surfaces_display.triggered.connect(self.handle_toggle_chi_square_surfaces_display)

        toggle_id = self.menu_table['Toggle Metrics Display']
        self._toggle_metrics_display = QAction('Toggle Metrics Display',self)
        self._menu.addAction(self._toggle_metrics_display)
        self._toggle_metrics_display.setData(str(toggle_id))
        self._toggle_metrics_display.setVisible(False)
        self._toggle_metrics_display.setText('Show solver metrics')
        self._toggle_metrics_display.setCheckable(True)
        self._toggle_metrics_display.setChecked(True)
        self._toggle_metrics_display.triggered.connect(self.handle_toggle_metrics_display)

        toggle_id = self.menu_table['Show logarithmic range for data']
        self._toggle_log_range_for_data = QAction('Use logarithmic range for data',self)
        self._menu.addAction(self._toggle_log_range_for_data)
        self._toggle_log_range_for_data.setData(str(toggle_id))
        self._toggle_log_range_for_data.setVisible(False)
        self._toggle_log_range_for_data.setCheckable(True)
        self.log_switch_set = False
        self._toggle_log_range_for_data.triggered.connect(self.handle_toggle_log_range_for_data)

        self._delete_x_section_display = QAction('Delete X-Section Display',self)
        self._menu.addAction(self._delete_x_section_display)
        self._delete_x_section_display.triggered.connect(self.handle_delete_x_section_display)
        self._delete_x_section_display.setVisible(False)


        toggle_id = self.menu_table['Toggle real/imag or ampl/phase Display']
        self._toggle_ri_or_ap_display = QAction('Plot complex values as',self)
        self._menu.addAction(self._toggle_ri_or_ap_display)
        self._toggle_ri_or_ap_display.setMenu(self._complex_data_menu)
        self._toggle_ri_or_ap_display.setVisible(False)

        toggle_id = self.menu_table['Show Full Data Range']
        self._show_full_data_range = QAction('Show full data range',self)
        self._menu.addAction(self._show_full_data_range)
        self._show_full_data_range.setData(str(toggle_id))
        self._show_full_data_range.setVisible(False)
        self._show_full_data_range.triggered.connect(self.handle_show_full_data_range)

        toggle_id = self.menu_table['Toggle 3D Display']
        self._toggle_3d_display = QAction('Toggle 3D display',self)
        self._menu.addAction(self._toggle_3d_display)
        self._toggle_3d_display.setData(str(toggle_id))
        self._toggle_3d_display.setText('Show 3D display')
        self._toggle_3d_display.setVisible(False)
        self._toggle_3d_display.triggered.connect(self.handle_toggle_3d_display)

        toggle_id = self.menu_table['Toggle Warp Display']
        self._toggle_warp_display = QAction('Toggle Warp Display',self)
        self._menu.addAction(self._toggle_warp_display)
        self._toggle_warp_display.setData(str(toggle_id))
        self._toggle_warp_display.setText('Show warped surface display')
        self._toggle_warp_display.setVisible(False)
        self._toggle_warp_display.triggered.connect(self.handle_toggle_warp_display)

# add potential menu for flagged data
# add flag toggling for vells but make hidden by default
        self._toggle_flag_label = "show flagged data for plane "
        toggle_id = self.menu_table[self._toggle_flag_label]
        self._toggle_flagged_data_for_plane = QAction(self._toggle_flag_label,self)
        self._menu.addAction(self._toggle_flagged_data_for_plane)
        self._toggle_flagged_data_for_plane.setData(str(toggle_id))
        self._toggle_flagged_data_for_plane.triggered.connect(self.handle_toggle_flagged_data_for_plane)
        self._toggle_flagged_data_for_plane.setEnabled(False)
        self._toggle_flagged_data_for_plane.setVisible(False)
        self._toggle_flagged_data_for_plane.setCheckable(True)


        self._toggle_blink_label = "blink flagged data for plane "
        toggle_id = self.menu_table[self._toggle_blink_label]
        self._toggle_blink_of_flagged_data = QAction(self._toggle_blink_label,self)
        self._menu.addAction(self._toggle_blink_of_flagged_data)
        self._toggle_blink_of_flagged_data.setData(str(toggle_id))
        self._toggle_blink_of_flagged_data.triggered.connect(self.handle_toggle_blink_of_flagged_data)
        self._toggle_blink_of_flagged_data.setEnabled(False)
        self._toggle_blink_of_flagged_data.setVisible(False)
        self._toggle_blink_of_flagged_data.setCheckable(True)

        self._toggle_range_label = "Set display range to that of unflagged data for plane "
        toggle_id = self.menu_table[self._toggle_range_label]
        self._set_display_range_to_unflagged_data = QAction(self._toggle_range_label,self)
        self._menu.addAction(self._set_display_range_to_unflagged_data)
        self._set_display_range_to_unflagged_data.setData(str(toggle_id))
        self._set_display_range_to_unflagged_data.triggered.connect(self.handle_set_display_range_to_unflagged_data)
        self._set_display_range_to_unflagged_data.setEnabled(False)
        self._set_display_range_to_unflagged_data.setVisible(False)
        self._set_display_range_to_unflagged_data.setCheckable(True)

        self.set_flag_toggles()

# add zoomer and printer stuff
        toggle_id = self.menu_table['Reset zoomer']
        if HAS_TIMBA:
          self._reset_zoomer = QAction(pixmaps.viewmag.iconset(),'Reset zoomer',self)
        else:
          self._reset_zoomer = QAction('Reset zoomer',self)
        self._menu.addAction(self._reset_zoomer)
        self._reset_zoomer.setData(str(toggle_id))
        self._reset_zoomer.setVisible(False)
        self._reset_zoomer.triggered.connect(self.handle_reset_zoomer)

        toggle_id = self.menu_table['Undo Last Zoom']
        if HAS_TIMBA:
          self._undo_last_zoom = QAction(pixmaps.viewmag.iconset(),'Undo last zoom',self)
        else:
          self._undo_last_zoom = QAction('Undo last zoom',self)
        self._menu.addAction(self._undo_last_zoom)
        self._undo_last_zoom.setData(str(toggle_id))
        self._undo_last_zoom.setVisible(False)
        self._undo_last_zoom.triggered.connect(self.handle_undo_last_zoom)

        toggle_id = self.menu_table['Change Vells']
        self._change_vells = QAction('Data element selector...',self)
        self._menu.addAction(self._change_vells)
        self._change_vells.setData(str(toggle_id))
        self._change_vells.setVisible(False)
        self._change_vells.triggered.connect(self.handle_change_vells)


        if self.chi_zeros is None:
          self._toggle_axis_flip.setVisible(True)
          if not self.complex_type:
            self._toggle_axis_rotate.setVisible(True)
        else:
          self._toggle_log_axis_for_chi_0.setVisible(True)
          self._toggle_log_axis_for_solution_vector.setVisible(True)
          self._toggle_chi_square_surfaces_display.setVisible(True)

        if self._zoom_display:
          toggle_id = self.menu_table['Toggle Pause']
          self._toggle_pause = QAction('Pause data display',self)
          self._menu.addAction(self._toggle_pause)
          self._toggle_pause.setData(str(toggle_id))
          self._toggle_pause.setCheckable(True)
          self._toggle_pause.setChecked(self._do_pause)
          self._toggle_pause.triggered.connect(self.handle_toggle_pause)

          # following option does nothing useful at the moment
          toggle_id = self.menu_table['Toggle Comparison']
          self._toggle_comparison = QAction('Do comparison',self)
          self._menu.addAction(self._toggle_comparison)
          self._toggle_comparison.setData(str(toggle_id))
          self._toggle_comparison.setCheckable(True)
          self._toggle_comparison.setChecked(self._compare_max)
          self._toggle_comparison.setVisible(False)
          self._toggle_comparison.triggered.connect(self.handle_toggle_comparison)
        
        toggle_id = self.menu_table['Save Display in pdf Format']
        self._save_display_in_pdf_format = QAction('Save display in pdf format',self)
        self._menu.addAction(self._save_display_in_pdf_format)
        self._save_display_in_pdf_format.setData(str(toggle_id))
        self._save_display_in_pdf_format.setVisible(True)
        self._save_display_in_pdf_format.triggered.connect(self.print_)


    def set_original_array_rank(self, original_array_rank):
      self.original_data_rank = original_array_rank

    def getActiveAxesInc(self):
     return [self.first_axis_inc, self.second_axis_inc]


    def start_test_timer(self, time, test_complex, display_type):
      self.test_complex = test_complex
      self.setDisplayType(display_type)
      self.startTimer(time)
     # start_test_timer()
                                                                                
    def timerEvent(self, e):
        m = numpy.fromfunction(RealDist, (30,20))
        n = numpy.fromfunction(ImagDist, (30,20))
        vector_array = numpy.zeros((30,1), numpy.complex128)
        shape = m.shape
        for i in range(shape[0]):
          for j in range(shape[1]):
            m[i,j] = m[i,j] + self.index * random.random()
            n[i,j] = n[i,j] + 3 * self.index * random.random()
        a = numpy.zeros((shape[0],shape[1]), numpy.complex128)
        a.real = m
        a.imag = n         
        self.array_plot(a,data_label='test_image_complex')
        self.index = self.index + 1
    # timerEvent()

    def timerEvent1(self, e):
      if self.test_complex:
        m = numpy.fromfunction(RealDist, (30,20))
        n = numpy.fromfunction(ImagDist, (30,20))
        vector_array = numpy.zeros((30,1), numpy.complex128)
        shape = m.shape
        for i in range(shape[0]):
          for j in range(shape[1]):
            m[i,j] = m[i,j] + self.index * random.random()
            n[i,j] = n[i,j] + 3 * self.index * random.random()
        a = numpy.zeros((shape[0],shape[1]), numpy.complex128)
        a.real = m
        a.imag = n         
        for i in range(shape[0]):
          vector_array[i,0] = a[i,0]
        if self.index % 2 == 0:
          if HAS_TIMBA:_dprint(2, 'plotting complex vector with shape ',vector_array.shape);
          self.array_plot(vector_array,data_label='test_vector_complex')
        else:
          if HAS_TIMBA:_dprint(2, 'plotting complex array with shape ',a.shape);
          self.array_plot(a,data_label='test_image_complex')
          self.test_complex = False
      else:
        vector_array = numpy.zeros((30,1), numpy.float32)
        m = numpy.fromfunction(dist, (30,20))
        shape = m.shape
        for i in range(shape[0]):
          for j in range(shape[1]):
            m[i,j] = m[i,j] + self.index * random.random()
        for i in range(shape[0]):
          vector_array[i,0] = m[i,0]
        if self.index % 2 == 0:
          if HAS_TIMBA:_dprint(2, 'plotting real array with shape ',m.shape);
          self.array_plot(m,data_label='test_image')
        else:
          if HAS_TIMBA:_dprint(2, 'plotting real vector with shape ', vector_array.shape);
          self.array_plot(vector_array,data_label='test_vector')
          self.test_complex = True

      self.index = self.index + 1
    # timerEvent()

def make():
    demo = QwtImageDisplay()
    demo.resize(500, 300)
    demo.show()
# uncomment the following
    demo.start_test_timer(1000, True, "hippo")

# or
# uncomment the following lines 
# (note: you must have the pyfits module installed)
#   try:
#     import pyfits
#     image = pyfits.open('./xntd_diff.fits')
#     image = pyfits.open('./m51_32.fits')
#     selector = []
#     for i in range(len(image[0].data.shape)):
#       if image[0].data.shape[i] > 1:
#         axis_slice = slice(0,image[0].data.shape[i])
#         selector.append(axis_slice)
#       else:
#         selector.append(0)
#     tuple_selector = tuple(selector)
#     plot_array = image[0].data[tuple_selector]
#     demo.array_plot(plot_array, data_label='diff')
#   except:
#     print 'Exception while importing pyfits module:'
#     traceback.print_exc();
#     return


    return demo

def main(args):
    app = QApplication(sys.argv)
    demo = make()
    sys.exit(app.exec_())


# Admire
if __name__ == '__main__':
    main(sys.argv)

