#!/usr/bin/env python


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

import sys
from qt import *
try:
  from Qwt4 import *
except:
  from qwt import *
from numarray import *
import numarray.ieeespecial as ieee
from UVPAxis import *
from ComplexColorMap import *
from ComplexScaleDraw import *
from QwtPlotCurveSizes import *
from QwtPlotImage import *
from VellsTree import *
from Timba.GUI.pixmaps import pixmaps
from guiplot2dnodesettings import *
#from tabdialog import *
import random
import traceback

from Timba.utils import verbosity
_dbg = verbosity(0,name='displayimage');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

# is vtk available?
global has_vtk
has_vtk = False
try:
  import vtk
  has_vtk = True
except:
  print 'Exception while importing vtk module:'
  traceback.print_exc();
  print ' '
  print '*** VTK not found! ***'
  print 'If you know that VTK has been installed on your system'
  print 'make sure that your LD_LIBRARY_PATH includes the VTK  '
  print 'libraries.'
  print ' '


# compute standard deviation of a complex or real array
# the std_dev given here was computed according to the
# formula given by Oleg (It should work for real or complex array)
def standard_deviation(incoming_array,complex_type):
# first sanity check of array size
  num_elements = 1
  for i in range(len(incoming_array.shape)):
    num_elements = num_elements * incoming_array.shape[i]
# if we only have one element, return zero
  if num_elements <= 1:
    return 0.0
  else:
    if complex_type:
      incoming_mean = incoming_array.mean()
      temp_array = incoming_array - incoming_mean
      abs_array = abs(temp_array)
# get the conjugate of temp_array ...
# note: we need to add a test if temp_array has a value 0+0j somewhere,
# so do the following:
      temp1 = less_equal(abs_array,0.0)
      temp_array = temp_array + temp1
      temp_array_conj = (abs_array * abs_array) / temp_array
      temp_array = temp_array * temp_array_conj
      mean = temp_array.mean()
      std_dev = sqrt(mean)
      std_dev = abs(std_dev)
      return std_dev
    else:
      return incoming_array.stddev()

def linearX(nx, ny):
    return repeat(arange(nx, typecode = Float32)[:, NewAxis], ny, -1)

def linearY(nx, ny):
    return repeat(arange(ny, typecode = Float32)[NewAxis, :], nx, 0)

def rectangle(nx, ny, scale):
    # swap axes in the fromfunction call
    s = scale/(nx+ny)
    x0 = nx/2
    y0 = ny/2
    
    def test(y, x):
        return cos(s*(x-x0))*sin(s*(y-y0))

    result = fromfunction(test, (ny, nx))
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
#m = fromfunction(dist, (10,10))


    
display_image_instructions = \
'''This plot basically shows the contents of one or two-dimensional arrays. Most decision making takes place behind the scenes, so to speak, as the system uses the dimensionality of the data and the source of the data to decide how the data will be displayed. However, once a display appears, you can interact with it in certain standardized ways.<br><br>
Button 1 (Left): If you click the <b>left</b> mouse button on a location inside a two-dimensional array plot, the x and y coordinates of this location, and its value, will appear at the lower left hand corner of the display. This information is shown until you release the mouse button. If you click the left mouse button down and then drag it, a rectangular square will be seen. Then when you release the left mouse button, the plot will 'zoom in' on the area defined inside the rectangle.<br><br>
Button 2 (Middle): If you click the <b>middle</b> mouse button on a location inside a <b>two-dimensional</b> array plot, then X and Y cross-sections centred on this location are overlaid on the display. A continuous black line marks the location of the X cross-section and the black dotted line shows the cross section values, which are tied to the right hand scale. The white lines show corresponding information for the Y cross section, whose values are tied to the top scale of the plot. You can remove the X,Y cross sections from the display by selecting the appropriate option from the context menu (see Button 3 below). If the <b>Legends</b> display has been toggled to ON (see Button 3 below), then a sequence of push buttons will appear along the right hand edge of the display. Each of the push buttons is associated with one of the cross-section plots. Clicking on a push button will cause the corresponding plot to appear or disappear, depending on the current state.<br><br>
Button 3 (Right):Click the <b>right</b> mouse button in a spectrum display window to get get a context menu with options for printing, resetting the zoom, selecting another image, or toggling a <b>Legends</b> display. If you click on the 'Reset zoomer' icon  in a window where you had zoomed in on a selected region, then the original entire array is re-displayed. Vellsets or <b>visu</b> data sets may contain multiple arrays. Only one of these arrays can be displayed at any one time. If additional images are available for viewing, they will be listed in the context menu. If you move the right mouse button to the desired image name in the menu and then release the button, the requested image will now appear in the display. If you select the Print option from the menu, the standard Qt printer widget will appear. That widget will enable you print out a copy of your plot, or save the plot in Postscript format to a file. If you make cross-section plots (see Button 2 above), by default a <b>Legends</b> display associating push buttons with these plots is not shown. You can toggle the display of these push buttons ON or OFF by selecting the Toggle Plot Legend option from the context menu. If you are working with two-dimensional arrays, then additional options to toggle the ON or OFF display of a colorbar showing the range of intensities and to switch between GrayScale and Color representations of the pixels will be shown.<br><br>
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

    display_table = {
        'hippo': 'hippo',
        'grayscale': 'grayscale',
        'brentjens': 'brentjens',
        }

    menu_table = {
        'toggle flagged data for plane ': 200,
        'toggle blink of flagged data for plane ': 201,
        'Toggle display range to that of flagged image for plane ': 202,
        'Modify Plot Parameters': 299,
        'Toggle Plot Legend': 300,
        'Toggle ColorBar': 301,
        'Toggle Color/GrayScale Display': 302,
        'Toggle ND Controller': 303, 
        'Reset zoomer': 304,
        'Delete X-Section Display': 305,
        'Toggle real/imag or ampl/phase Display': 306,
        'Toggle axis flip': 307,
        'Toggle logarithmic range for data': 308,
        'Toggle results history': 309,
        'Toggle Metrics Display': 310,
        'Toggle log axis for chi_0': 311,
        'Toggle log axis for solution vector': 312,
        'Toggle chi-square surfaces display': 313,
        'Change Vells': 314,
        'Toggle 3D Display': 315,
        'Toggle Warp Display': 316,
        'Toggle Pause': 317,
        'Toggle Comparison': 318,
        'Drag Amplitude Scale': 319,
        'Undo Last Zoom': 320,
        'Save Display in PNG Format': 321,
        }

    _start_spectrum_menu_id = 0

    def __init__(self, plot_key="", parent=None):
        QwtPlot.__init__(self, parent)
        self.parent = parent
        # create copy of standard application font..
        font = QFont(QApplication.font());
        fi = QFontInfo(font);
        # and scale it down to 70%
        font.setPointSize(fi.pointSize()*0.7);
        # apply font to QwtPlot
        self.setTitleFont(font);
        for axis in range(0,4):
          self.setAxisFont(axis,font);
          self.setAxisTitleFont(axis,font);
          
        self._mainwin = parent and parent.topLevelWidget();

# set default display type to 'hippo'
        self._display_type = None

        self._vells_plot = False
	self._flags_array = None
	self.flag_toggle = None
	self.flag_blink = False
        self._zoom_display = False
        self._do_pause = False
        self._compare_max = False

# save raw data
        self.plot_key = plot_key
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
	self._menu = None
        self._vells_menu = None
        self.num_possible_ND_axes = None
        self._plot_type = None
        self.colorbar_requested = False
	self.is_combined_image = False
        self.active_image_index = None
        self.y_marker_step = None
        self.imag_flag_vector = None
        self.real_flag_vector = None
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
        self.ampl_phase = None
        self.added_metrics_menu = False
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
        self.adjust_color_bar = True
        self.toggle_metrics = True
        self.array_selector = None
        self.original_flag_array = None
        self.show_x_sections = False
        self.flag_range = False
        self.axes_flip = False
        self.setResults = True
        self.y_solver_offset = []
        self.metrics_plot = []
        self.chis_plot = []
        # make a QwtPlot widget
        self.plotLayout().setMargin(0)
        self.plotLayout().setCanvasMargin(0)
        self.plotLayout().setAlignCanvasToScales(1)
        self.setTitle('QwtImageDisplay')

        self.label = ''
        self.vells_menu_items = 0
        self.zooming = True
        self.setlegend = 0
        self.log_offset = 0.0
        self.current_width = 0
        self.setAutoLegend(self.setlegend)
        self.enableLegend(False)
        self.setLegendFont(font)
        self.setLegendPos(Qwt.Right)
        self.setAxisTitle(QwtPlot.xBottom, 'Array/Channel Number')
        self.setAxisTitle(QwtPlot.yLeft, 'Array/Sequence Number')

# set default background to  whatever QApplication sez it should be!
        self.setCanvasBackground(QApplication.palette().active().base())


        
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

        self.zoomStack = []
        self.connect(self,
                     SIGNAL('plotMouseMoved(const QMouseEvent&)'),
                     self.onMouseMoved)
        self.connect(self,
                     SIGNAL('plotMousePressed(const QMouseEvent&)'),
                     self.onMousePressed)
        self.connect(self,
                     SIGNAL('plotMouseReleased(const QMouseEvent&)'),
                     self.onMouseReleased)
        self.connect(self, SIGNAL("legendClicked(long)"), self.toggleCurve)
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

        self.first_chi_test = True
        self.log_axis_chi_0 = False
        self.log_axis_solution_vector = False
        self.display_solution_distances = False
        self.store_solver_array = False
        self.curve_info = ""
        self.metrics_index = 0

#add a printer
        self.printer = QAction(self);
        self.printer.setIconSet(pixmaps.fileprint.iconset());
        self.printer.setText("Print plot");
        QObject.connect(self.printer,SIGNAL("activated()"),self.printplot);

        QWhatsThis.add(self, display_image_instructions)

# Finally, over-ride default QWT Plot size policy of MinimumExpanding
# Otherwise minimum size of plots is too large when embedded in a
# QGridlayout
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

# set up pop up text
        font = QFont("Helvetica",10)
        self._popup_text = QLabel(self)
        self._popup_text.setFont(font)
        self._popup_text.setFrameStyle(QFrame.Box | QFrame.Plain)
        # start the text off hidden at 0,0
        self._popup_text.hide()

# for drag & drop stuff ...
        self.setAcceptDrops(True)

#       self.__init__

    def dragEnterEvent(self, event):
      """ drag & drop event callback entered when we move out of or
          in to a widget
      """
      try:
        event.accept(QTextDrag.canDecode(event))
      except:
        pass

    def dropEvent(self, event):
      """ callback that handles a drop event from drag & drop """
      try:
        command= QString()
        if QTextDrag.decode(event, command): # fills 'command' with decoded text
          if str(command) == "copyPlotParms":
            if event.source() != self:
              parms = event.source().getPlotParms();
              self.setPlotParms(parms,True)
#           else:
#             print 'dropping into same widget'
#       else:
#         print 'decode failure'
      except:
        pass

    def startDrag(self):
      """ operations done when we start a drag event """
      d = QTextDrag('copyPlotParms', self)
      d.dragCopy()

    def setZoomDisplay(self):
      self._zoom_display = True

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

          self.setTitle(self._window_title)
          self.setAxisTitle(QwtPlot.xBottom, self._x_title)
          self.setAxisTitle(QwtPlot.yLeft, self._y_title)

        if self.zoomStack == []:
                self.zoomState = (
                    self.axisScale(QwtPlot.xBottom).lBound(),
                    self.axisScale(QwtPlot.xBottom).hBound(),
                    self.axisScale(QwtPlot.yLeft).lBound(),
                    self.axisScale(QwtPlot.yLeft).hBound(), True
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
        else:
          self.setAxisAutoScale(QwtPlot.yLeft)
        if display_zoom_menu:
          self.zoomState = (self.axis_xmin, self.axis_xmax, self.axis_ymin, self.axis_ymax, True)
          toggle_id = self.menu_table['Reset zoomer']
          self._menu.setItemVisible(toggle_id, True)
          toggle_id = self.menu_table['Undo Last Zoom']
          if self.is_vector and self.complex_type:
            self._menu.setItemVisible(toggle_id, False)
          else:
            self._menu.setItemVisible(toggle_id, True)
        else:
          toggle_id = self.menu_table['Reset zoomer']
          self._menu.setItemVisible(toggle_id, False)
          toggle_id = self.menu_table['Undo Last Zoom']
          self._menu.setItemVisible(toggle_id, False)
        self.replot()
        _dprint(3, 'called replot in setPlotParms')

    def initSpectrumContextMenu(self):
        """Initialize the spectrum context menu """
        # skip if no main window
        if not self._mainwin:
          return;

        if self._menu is None:
          self._menu = QPopupMenu(self._mainwin);
          self.add_basic_menu_items()
          QObject.connect(self._menu,SIGNAL("activated(int)"),self.update_spectrum_display);
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
        toggle_id = self.menu_table['Delete X-Section Display']
        self.show_x_sections = False
        self._menu.setItemVisible(toggle_id, False)

        toggle_id = self.menu_table['Toggle Plot Legend']
        self._menu.setItemVisible(toggle_id, False)

# add solver metrics info back in?
        if self.toggle_metrics and not self.metrics_rank is None:
          self.add_solver_metrics()

        if not self.scalar_display:
	  self.refresh_marker_display()

    def setResultsSelector(self):
      """ add option to toggle ResultsRange selector to context menu """
      toggle_id = self.menu_table['Toggle results history']
      self._menu.setItemVisible(toggle_id, True)

    def handle_basic_menu_id(self, menuid):
      """ callback to handle most common basic context menu selections """
      if menuid < 0:
# should not be any such menuid that we need to handle here
# (print signal is handled by printplot function) so ignore
        return True
      if menuid == self.menu_table['Reset zoomer']:
        if self.is_vector and self.complex_type:
          replot = True
        else:
          replot = False
        self.reset_zoom(replot)
        return True
      if menuid == self.menu_table['Undo Last Zoom']:
        replot = False
        self.reset_zoom(replot, True)
        return True
      if menuid == self.menu_table['Delete X-Section Display']:
        self.delete_cross_sections()
        return True
      if menuid == self.menu_table['Modify Plot Parameters']:
        self.updatePlotParameters()
        return True
      if menuid == self.menu_table['Toggle Plot Legend']:
        self.toggleLegend(menuid)
        return True
      if menuid == self.menu_table['Toggle axis flip']:
        self.toggleAxis()
        self._menu.setItemChecked(menuid,self.axes_flip)
        return True
      if menuid == self.menu_table['Toggle ColorBar']:
        if self.toggle_color_bar == 1:
          self.toggle_color_bar = 0
          self._menu.changeItem(menuid, 'Show ColorBar')
        else:
          self.toggle_color_bar = 1
          self._menu.changeItem(menuid, 'Hide ColorBar')
        self.emit(PYSIGNAL("show_colorbar_display"),(self.toggle_color_bar,0))
        if self.complex_type:
          self.emit(PYSIGNAL("show_colorbar_display"),(self.toggle_color_bar,1))
        return True
      if menuid == self.menu_table['Toggle Color/GrayScale Display']:
        if self.toggle_gray_scale == 1:
          self.setDisplayType('hippo')
          self._menu.changeItem(menuid, 'Show GrayScale Display')
        else:
          self.setDisplayType('grayscale')
          self._menu.changeItem(menuid, 'Show Color Display')
        self.plotImage.updateImage(self.raw_image)
        self.replot()
        _dprint(3, 'called replot in handle_basic_menu_id')
        return True
      if menuid == self.menu_table['Toggle ND Controller']:
        if self.toggle_ND_Controller == 1:
          self.toggle_ND_Controller = 0
          self._menu.changeItem(menuid, 'Show ND Controller')
        else:
          self.toggle_ND_Controller = 1
          self._menu.changeItem(menuid, 'Hide ND Controller')
        self.emit(PYSIGNAL("show_ND_Controller"),(self.toggle_ND_Controller,))
        return True
      if menuid == self.menu_table['Toggle 3D Display']:
        self.emit(PYSIGNAL("show_3D_Display"),(True,))
        return True
      if menuid == self.menu_table['Toggle Warp Display']:
        self.emit(PYSIGNAL("show_3D_Display"),(False,))
        return True
      if menuid == self.menu_table['Toggle results history']:
        if self.setResults:
          self.setResults = False
          self._menu.setItemChecked(menuid, False)
        else:
          self.setResults = True
          self._menu.setItemChecked(menuid, True)
        self.emit(PYSIGNAL("show_results_selector"),(self.setResults,))
        return True
      if menuid == self.menu_table['Toggle real/imag or ampl/phase Display']:
        if self.ampl_phase:
          self._menu.changeItem(menuid, 'Show Data as Amplitude and Phase')
          self.ampl_phase = False
          if self._vells_plot and not self.is_vector:
            title_addition = ': (real followed by imaginary)'
            self._x_title = self.vells_axis_parms[self.x_parm][2] + title_addition
          else:
            if self.is_vector:
              self._x_title = 'Array/Channel Number '
            else:
              self._x_title = 'Array/Channel Number (real followed by imaginary)'
          self.setAxisTitle(QwtPlot.xBottom, self._x_title)
        else:
          self._menu.changeItem(menuid, 'Show Data as Real and Imaginary')
          self.ampl_phase = True
          if self._vells_plot and not self.is_vector:
            title_addition = ': (amplitude followed by phase)'
            self._x_title = self.vells_axis_parms[self.x_parm][2] + title_addition
          else:
            if self.is_vector:
              self._x_title = 'Array/Channel Number '
            else:
              self._x_title = 'Array/Channel Number (amplitude followed by phase)'
          self.setAxisTitle(QwtPlot.xBottom, self._x_title)

        if self.is_vector:
          # make sure we unzoom as axes will probably change drastically
          self.reset_zoom(True)
        else:
          self.adjust_color_bar = True
          if self.ampl_phase:
            ampl_phase_image = self.convert_to_AP(self.complex_image)
            self.display_image(ampl_phase_image)
          else:
            self.display_image(self.complex_image)
        return True
      if menuid == self.menu_table['Toggle logarithmic range for data']:
        if self.toggle_log_display == False:
          self._menu.changeItem(menuid, 'Show Data with linear scale')
          self.toggle_log_display = True
          self.plotImage.setLogScale()
        else:
          self.toggle_log_display = False
          self._menu.changeItem(menuid, 'Show Data with logarithmic scale')
          self.plotImage.setLogScale(False)
          self.plotImage.setImageRange(self.raw_image)
        self.plotImage.updateImage(self.raw_image)
        image_limits = self.plotImage.getRealImageRange()
        self.emit(PYSIGNAL("max_image_range"),(image_limits, 0, self.toggle_log_display,self.ampl_phase))
        if self.complex_type:
          image_limits = self.plotImage.getImagImageRange()
          self.emit(PYSIGNAL("max_image_range"),(image_limits, 1,self.toggle_log_display,self.ampl_phase) )
        self.log_offset = 0.0
        if self.toggle_log_display:
          self.log_offset = self.plotImage.getTransformOffset()
        self.insert_array_info()
        if self.show_x_sections:
          self.calculate_cross_sections()
        self.replot()
        _dprint(3, 'called replot in handle_basic_menu_id')
        return True

      if menuid == self.menu_table['Toggle Metrics Display']:
        if self.toggle_metrics == False:
          self.toggle_metrics = True
          self._menu.changeItem(menuid, 'Hide Solver Metrics')
        else:
          self.toggle_metrics = False
          self._menu.changeItem(menuid, 'Show Solver Metrics')
        self.toggleMetrics()
        self.replot()
        _dprint(3, 'called replot in handle_basic_menu_id')
        return True

      if menuid == self.menu_table['Toggle log axis for chi_0']:
        if self.log_axis_chi_0 is False:
          self.log_axis_chi_0 = True
          self._menu.setItemChecked(menuid, True)
        else:
          self.log_axis_chi_0 = False
          self._menu.setItemChecked(menuid, False)
        self.test_plot_array_sizes()
        self.replot()
        return True

      if menuid == self.menu_table['Toggle log axis for solution vector']:
        if self.log_axis_solution_vector is False:
          self.log_axis_solution_vector = True
          self._menu.setItemChecked(menuid, True)
        else:
          self.log_axis_solution_vector = False
          self._menu.setItemChecked(menuid, False)
        self.test_plot_array_sizes()
        self.replot()
        return True

      if menuid == self.menu_table['Toggle chi-square surfaces display']:
        if self.display_solution_distances is False:
          self.display_solution_distances = True
          QWhatsThis.remove(self)
          QWhatsThis.add(self, chi_sq_instructions)
          self._menu.changeItem(menuid, 'Show Solver Solutions')
          toggle_id = self.menu_table['Toggle Metrics Display']
          self._menu.setItemVisible(toggle_id, False)
          toggle_id = self.menu_table['Toggle logarithmic range for data']
          self._menu.setItemVisible(toggle_id, False)
          toggle_id = self.menu_table['Toggle Plot Legend']
          self._menu.setItemVisible(toggle_id, True)
        else:
          self.display_solution_distances = False
          QWhatsThis.remove(self)
          QWhatsThis.add(self, display_image_instructions)
          self._menu.changeItem(menuid, 'Show chi-square surfaces')
          toggle_id = self.menu_table['Toggle Metrics Display']
          self._menu.setItemVisible(toggle_id, True)
          toggle_id = self.menu_table['Toggle logarithmic range for data']
          self._menu.setItemVisible(toggle_id, True)
          toggle_id = self.menu_table['Toggle Plot Legend']
          self._menu.setItemVisible(toggle_id, True)
        self.reset_zoom()
        self.array_plot(self.solver_title, self.solver_array)
        if not self.display_solution_distances: 
          self.add_solver_metrics()
          self.toggleMetrics()
        self.replot()
        return True

      if menuid == self.menu_table['Toggle Pause']:
        self.Pausing()
        return True
      if menuid == self.menu_table['Toggle Comparison']:
        self.do_compare()
        return True

      if menuid == self.menu_table['Change Vells']:
        self._vells_menu.show()
        return True

      if menuid == self.menu_table['Save Display in PNG Format']:
        self.emit(PYSIGNAL("save_display"),(self._window_title,))
        return True

# if we get here ...
      return False

    def Pausing(self):
      toggle_id = self.menu_table['Toggle Pause']
      if self._do_pause:
          self._menu.changeItem(toggle_id, 'Pause')
          self._do_pause = False
      else:
          self._menu.changeItem(toggle_id, 'Resume')
          self._do_pause = True
      self.emit(PYSIGNAL("winpaused"),(self._do_pause,))

    def do_compare(self):
      toggle_id = self.menu_table['Toggle Comparison']
      if self._compare_max:
        self._compare_max = False
        self._menu.changeItem(toggle_id, 'Do Comparison')
      else:
        self._compare_max = True
        self._menu.changeItem(toggle_id, 'Stop Comparison')
      self.emit(PYSIGNAL("compare"),(self._compare_max,))


    def toggleMetrics(self):
      """ callback to make Solver Metrics plots visible or invisible """
      if self.toggle_metrics and not self.metrics_rank is None:
        self.add_solver_metrics()
      if not self.toggle_metrics:
        if len(self.y_solver_offset) > 0:
          for i in range(len(self.y_solver_offset)):
            self.removeMarker(self.y_solver_offset[i])
          self.y_solver_offset = []
        if len(self.metrics_plot) > 0:
          for i in range(len(self.metrics_plot)):
            self.removeCurve(self.metrics_plot[i])
          self.metrics_plot = []

    def handle_flag_toggles(self, menuid):
      """ callback to handle or modify displays of flagged data """
# toggle flags display	
      if menuid == self.menu_table['toggle flagged data for plane ']:
        self.handleFlagToggle(self.flag_toggle)
        self._menu.setItemChecked(menuid, self.flag_toggle)
        self.replot()
        _dprint(3, 'called replot in handle_flag_toggles')
	return True

      if menuid == self.menu_table['toggle blink of flagged data for plane ']:
        if self.flag_blink == False:
          self.flag_blink = True
	  self.timer = QTimer(self)
          self.timer.connect(self.timer, SIGNAL('timeout()'), self.timerEvent_blink)
          self.timer.start(2000)
        else:
          self.flag_blink = False
        self._menu.setItemChecked(menuid,self.flag_blink)
	return True

      if menuid == self.menu_table['Toggle display range to that of flagged image for plane ']:
        self.handleFlagRange(self.flag_range)
        self._menu.setItemChecked(menuid,self.flag_range)
        self.replot()
        _dprint(3, 'called replot in handle_flag_toggles')
	return True

# if we get here ...
      return False

    def handleFlagToggle(self, flag_toggle):
      """ callback to make flagged data visible or invisible """
      if flag_toggle == False:
        self.flag_toggle = True
      else:
        self.flag_toggle = False
      if self.real_flag_vector is None:
        self.plotImage.setDisplayFlag(self.flag_toggle)
      else:
        self.curve(self.real_flag_vector).setEnabled(self.flag_toggle)
        if not self.imag_flag_vector is None:
          self.curve(self.imag_flag_vector).setEnabled(self.flag_toggle)
        if not self.yCrossSection_flag is None:
          self.curve(self.yCrossSection_flag).setEnabled(self.flag_toggle)
        if not self.xrCrossSection_flag is None:
          self.curve(self.xrCrossSection_flag).setEnabled(self.flag_toggle)
        if not self.yCrossSection is None:
          if self.flag_toggle:
            self.curve(self.yCrossSection).setEnabled(False)
          else:
            self.curve(self.yCrossSection).setEnabled(True)
        if not self.xrCrossSection is None:
          if self.flag_toggle:
            self.curve(self.xrCrossSection).setEnabled(False)
          else:
            self.curve(self.xrCrossSection).setEnabled(True)

    def handleFlagRange(self, flag_range):
      """ callback to adjust display range of flagged data """
      if self.is_vector:
        return
      if flag_range == False:
        self.flag_range = True
        self.plotImage.setFlaggedImageRange()
        self.plotImage.updateImage(self.raw_image)
        flag_image_limits = self.plotImage.getRealImageRange()
        self.emit(PYSIGNAL("max_image_range"),(flag_image_limits, 0, self.toggle_log_display,self.ampl_phase))
        if self.complex_type:
          flag_image_limits = self.plotImage.getImagImageRange()
          self.emit(PYSIGNAL("max_image_range"),(flag_image_limits, 1, self.toggle_log_display,self.ampl_phase))
      else:
        self.flag_range = False
        self.plotImage.setImageRange(self.raw_image)
        self.plotImage.updateImage(self.raw_image)
        image_limits = self.plotImage.getRealImageRange()
        self.emit(PYSIGNAL("max_image_range"),(image_limits, 0, self.toggle_log_display,self.ampl_phase))
        if self.complex_type:
          image_limits = self.plotImage.getImagImageRange()
          self.emit(PYSIGNAL("max_image_range"),(image_limits, 1, self.toggle_log_display,self.ampl_phase))

    def setAxisParms(self, axis_parms):
      self.first_axis_parm = axis_parms[0]
      self.second_axis_parm = axis_parms[1]
      _dprint(3, 'axis parms set to ', self.first_axis_parm, ' ', self.second_axis_parm)

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
      if self.handle_basic_menu_id(menuid):
        return

      if self.is_combined_image:
        self.removeMarkers()
        self.info_marker = None
        self.log_marker = None
        self.source_marker = None
        self.is_combined_image = False

# if we got here, emit signal up to result_plotter here
      menuid = self.spectrum_menu_items - 1 - menuid
      self.emit(PYSIGNAL("handle_spectrum_menu_id"),(menuid,))

    def set_flag_toggles(self, flag_plane=None, flag_setting=False):
      """ creates context menus for selecting flagged Vells data """
# add flag toggling for vells but make hidden by default
      self._toggle_flag_label = "toggle flagged data for plane "
      toggle_id = self.menu_table[self._toggle_flag_label]
      if flag_plane is None:
        self._menu.insertItem(self._toggle_flag_label,toggle_id)
      else:
        self._menu.changeItem(toggle_id,self._toggle_flag_label+str(flag_plane))
      self._menu.setItemEnabled(toggle_id, flag_setting)
      self._menu.setItemVisible(toggle_id, flag_setting)

      self._toggle_blink_label = "toggle blink of flagged data for plane "
      toggle_id = self.menu_table[self._toggle_blink_label]
      if flag_plane is None:
        self._menu.insertItem(self._toggle_blink_label,toggle_id)
      else:
        self._menu.changeItem(toggle_id,self._toggle_blink_label+str(flag_plane))
      self._menu.setItemEnabled(toggle_id, flag_setting)
      self._menu.setItemVisible(toggle_id, flag_setting)

      self._toggle_range_label = "Toggle display range to that of flagged image for plane "
      toggle_id = self.menu_table[self._toggle_range_label]
      if flag_plane is None:
        self._menu.insertItem(self._toggle_range_label,toggle_id)
      else:
        self._menu.changeItem(toggle_id, self._toggle_range_label+str(flag_plane))
      self._menu.setItemEnabled(toggle_id, flag_setting)
      self._menu.setItemVisible(toggle_id, flag_setting)

    def set_flag_toggles_active(self, flag_setting=False,image_display=True):
      """ sets menu options for flagging to visible """
# add flag toggling for vells but make hidden by default
      toggle_flag_label = "toggle flagged data for plane "
      toggle_id = self.menu_table[toggle_flag_label]
      self._menu.setItemEnabled(toggle_id, flag_setting)
      self._menu.setItemVisible(toggle_id, flag_setting)

      toggle_blink_label = "toggle blink of flagged data for plane "
      toggle_id = self.menu_table[toggle_blink_label]
      self._menu.setItemEnabled(toggle_id, flag_setting)
      self._menu.setItemVisible(toggle_id, flag_setting)

      if image_display:
        toggle_range_label = "Toggle display range to that of flagged image for plane "
        toggle_id = self.menu_table[toggle_range_label]
        self._menu.setItemEnabled(toggle_id, flag_setting)
        self._menu.setItemVisible(toggle_id, flag_setting)

    def initVellsContextMenu (self):
      """ intitialize context menu for selection of Vells data """
      # skip if no main window
      if not self._mainwin:
        return;
      self.log_switch_set = False
      if self._menu is None:
        self._menu = QPopupMenu(self._mainwin);
        QObject.connect(self._menu,SIGNAL("activated(int)"),self.update_vells_display);
        QObject.connect(self._menu,SIGNAL("aboutToShow()"),self.addVellsMenu);
        self.add_basic_menu_items()
    # end initVellsContextMenu()

    def setMenuItems(self, menu_data):
      """ add items specific to selection of Vells to context menu """
      self._vells_menu_data = menu_data

    def addVellsMenu(self):
      """ add vells options to context menu """

      if self._vells_menu_data is None:
        return
      if not self._vells_menu is None:
        self._vells_menu.reparent(QWidget(), 0, QPoint())
        toggle_id = self.menu_table['Change Vells']
        self._menu.setItemVisible(toggle_id, False)
        self._vells_menu = None

      if self._vells_menu is None:
        self._vells_menu =  VellsView()
        vells_root = VellsElement( self._vells_menu, "result" )
        QObject.connect(self._vells_menu,PYSIGNAL("selected_vells_id"),self.update_vells_display);
        self._vells_menu.hide()
        toggle_id = self.menu_table['Change Vells']
        self._menu.setItemVisible(toggle_id, True)
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
              node = VellsElement(vells_root, previous)
            node.setText(0,menu_labels[id])
            node.setKey(id)
            previous = node
            perturbations_key = str(id) + ' perturbations'
            if perturbations.has_key(perturbations_key):
              perturbations_index = perturbations[perturbations_key]
              submenu = self.createPerturbationsMenu(self._vells_menu,menu_labels,perturbations_index,node) 
#             self._vells_menu.insertItem(pixmaps.slick_redo.iconset(), 'perturbed values ', submenu)
        else:
          if int(num_planes/menu_step) * menu_step == num_planes:
            num_sub_menus = int(num_planes/menu_step)
          else:
            num_sub_menus = 1 + int(num_planes/menu_step)
          start_range = 0
          end_range = menu_step
          for k in range(num_sub_menus):
#           step_submenu = QPopupMenu(self._vells_menu)
#           QObject.connect(step_submenu,SIGNAL("activated(int)"),self.update_vells_display);
            start_str = None
            end_str = None
            for i in range(start_range, end_range):
              id = planes_index[i]
              if start_str is None:
                start_str = menu_labels[id]
            end_str = menu_labels[id]
            menu_string = 'Vells ' + start_str + ' to ' + end_str + '  '
#           self._vells_menu.insertItem(menu_string,step_submenu)
            if previous is None:
              node = VellsElement(vells_root)
            else:
              node = VellsElement(vells_root, previous)
            node.setText(0,menu_string)
            previous = node
            previous_node = None
            for i in range(start_range, end_range):
              id = planes_index[i]
              if previous_node is None:
                sub_node = VellsElement(node)
              else:
                sub_node = VellsElement(node, previous_node)
              sub_node.setText(0,menu_labels[id])
              sub_node.setKey(id)
              previous_node = sub_node
              perturbations_key = str(id) + ' perturbations'
              if perturbations.has_key(perturbations_key):
                perturbations_index = perturbations[perturbations_key]
                submenu = self.createPerturbationsMenu(self._vells_menu,menu_labels,perturbations_index,sub_node) 
#               step_submenu.insertItem(pixmaps.slick_redo.iconset(), 'perturbed values ', submenu)
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
      submenu = None
      if num_perturbs < menu_step:
#       QObject.connect(submenu,SIGNAL("activated(int)"),self.update_vells_display);
        for j in range(len(perturbations_index)):
          id = perturbations_index[j]
#         submenu.insertItem(menu_labels[id], id)
          if previous is None:
            pert_node = VellsElement(node)
          else:
            pert_node = VellsElement(node, previous)
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
#         print menu_string
          if previous is None:
            pert_node = VellsElement(node)
          else:
            pert_node = VellsElement(node, previous)
          pert_node.setText(0,menu_string)
          previous = pert_node
#         perturb_submenu = QPopupMenu(submenu)
#         QObject.connect(perturb_submenu,SIGNAL("activated(int)"),self.update_vells_display);
          prev_node = None
          for j in range(start_range, end_range):
            id = perturbations_index[j]
            if prev_node is None:
              pert_subnode = VellsElement(pert_node)
            else:
              pert_subnode = VellsElement(pert_node, prev_node)
            prev_node = pert_subnode
            pert_subnode.setText(0,menu_labels[id])
            pert_subnode.setKey(id)
          start_range = start_range + menu_step
          end_range = end_range + menu_step
          if end_range > num_perturbs:
            end_range = num_perturbs
      return submenu

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

      toggle_id = self.menu_table['Toggle axis flip']
      self._menu.setItemVisible(toggle_id, False)

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
#     print 'stack length ', len(self.zoomStack)
      if len(self.zoomStack):
        while len(self.zoomStack):
          axis_parms = self.zoomStack.pop()
          xmin = axis_parms[0]
          xmax = axis_parms[1]
          ymin = axis_parms[2]
          ymax = axis_parms[3]
          try:
            do_replot = axis_parms[4]
          except:
            pass
          if undo_last_zoom:
#           print 'popped range ', axis_parms
            break
        self.setAxisScale(QwtPlot.xBottom, xmin, xmax)
        self.setAxisScale(QwtPlot.yLeft, ymin, ymax)
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
        self.refresh_marker_display()
        if not len (self.zoomStack):
          toggle_id = self.menu_table['Reset zoomer']
          self._menu.setItemVisible(toggle_id, False)
          toggle_id = self.menu_table['Undo Last Zoom']
          self._menu.setItemVisible(toggle_id, False)
# do a complete replot in the following situation
# as both axes will have changed even if nothing to unzoom.
      if do_replot:
        self.replot()
    
      if replot:
        self.array_plot(self._window_title, self.complex_image, False)
      _dprint(3, 'exiting reset_zoom')
      return

    def toggleLegend(self, menuid):
      """ sets legends display for cross section plots to visible/invisible """
      if self.setlegend == 1:
        self.setlegend = 0
        self.enableLegend(False)
        self._menu.changeItem(menuid, 'Show Plot Legends')
      else:
        self.setlegend = 1
        self.enableLegend(True)
        self._menu.changeItem(menuid, 'Hide Plot Legends')
      self.setAutoLegend(self.setlegend)
      self.replot()
      _dprint(3, 'called replot in toggleLegend')
    # toggleLegend()

    def toggleAxis(self):
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
        self.array_plot(self.original_label, self.original_array)
    # toggleAxis()

    def updatePlotParameters(self):
      """ create a GUI for user to modify plot parameters """
      parms_interface = WidgetSettingsDialog(actual_parent=self, gui_parent=self)

    def setImageRange(self, min, max, colorbar=0):
      """ callback to set allowable range of array intensity display """
      _dprint(3, 'received request for min and max of ', min, ' ', max)
      if colorbar == 0:
        self.plotImage.defineImageRange((min, max), True)
      else:
        self.plotImage.defineImageRange((min, max), False)
      self.plotImage.updateImage(self.raw_image)
      self.replot()
      _dprint(3, 'called replot in setImageRange')
    # setImageRange
	

    def timerEvent_blink(self):
# stop blinking     
      if not self.flag_blink:
        self.timer.stop()
        self.handleFlagToggle(True)
      else:
        self.handleFlagToggle(self.flag_toggle)
      self.replot()
      _dprint(3, 'called replot in timerEvent_blink')

    def update_vells_display(self, menuid):
      if self.handle_basic_menu_id(menuid):
        return
# are we toggling something with flags?
      if self.handle_flag_toggles(menuid):
        return
# if we got here, emit signal up to result_plotter here
      self.emit(PYSIGNAL("handle_menu_id"),(menuid,))

    def setVellsPlot(self, do_vells_plot=True):
      self._vells_plot = do_vells_plot

    def report_scalar_value(self, data_label, scalar_data=None):
      """ report a scalar value in case where a vells plot has
          already been initiated
      """
      self._vells_plot = False
      self.reset_zoom()
      dummy_array = zeros(shape=(2,2),type=Float32)
      self.array_plot(data_label, dummy_array)
      self.zooming = False
      self.set_xaxis_title(' ')
      self.set_yaxis_title(' ')
      self.removeMarkers()
      self.scalar_display = True
      self.setAxisAutoScale(QwtPlot.xBottom)
      self.setAxisAutoScale(QwtPlot.xTop)
      self.setAxisAutoScale(QwtPlot.yLeft)
      self.setAxisAutoScale(QwtPlot.yRight)
      self.enableAxis(QwtPlot.yLeft, False)
      self.enableAxis(QwtPlot.xBottom, False)
      self._x_auto_scale = True
      self._y_auto_scale = True
      if scalar_data is None:
        Message = data_label
      else:
        Message = data_label + ' is a scalar\n with value: ' + str(scalar_data)
      _dprint(3,' scalar message ', Message)
      
# text marker giving source of point that was clicked
      if not self.source_marker is None:
        self.removeMarker(self.source_marker)
      self.source_marker = self.insertMarker()
      ylb = self.axisScale(QwtPlot.yLeft).lBound()
      xlb = self.axisScale(QwtPlot.xBottom).lBound()
      yhb = self.axisScale(QwtPlot.yLeft).hBound()
      xhb = self.axisScale(QwtPlot.xBottom).hBound()
      self.setMarkerPos(self.source_marker, xlb+0.1, ylb+1.0)
      self.setMarkerLabelAlign(self.source_marker, Qt.AlignRight | Qt.AlignTop)
      fn = self.fontInfo().family()
      self.setMarkerLabel( self.source_marker, Message,
         QFont(fn, 8, QFont.Bold, False),
         Qt.blue, QPen(Qt.red, 2), QBrush(Qt.yellow))

# make sure we cannot try to show ND Controller
      self.toggle_ND_Controller = 0
      toggle_id = self.menu_table['Toggle ND Controller']
      self._menu.setItemVisible(toggle_id, False)
      toggle_id = self.menu_table['Toggle 3D Display']
      self._menu.setItemVisible(toggle_id, False)
      toggle_id = self.menu_table['Toggle Warp Display']
      self._menu.setItemVisible(toggle_id, False)

# make sure any color bar from array plot of other Vells member is hidden
      self.emit(PYSIGNAL("show_colorbar_display"),(0,0)) 
      if self.complex_type:
        self.emit(PYSIGNAL("show_colorbar_display"),(0,1)) 
# make sure options relating to color bar are not in context menu
      toggle_id = self.menu_table['Toggle ColorBar']
      self._menu.setItemVisible(toggle_id, False)
      toggle_id = self.menu_table['Toggle Color/GrayScale Display']
      self._menu.setItemVisible(toggle_id, False)
      toggle_id = self.menu_table['Toggle logarithmic range for data']
      self._menu.setItemVisible(toggle_id, False)
      self.log_switch_set = False

# a scalar has no legends or cross-sections!
      toggle_id = self.menu_table['Toggle Plot Legend']
      self._menu.setItemVisible(toggle_id, False)
      self.delete_cross_sections()

# can't flip axes with a scalar!
      toggle_id = self.menu_table['Toggle axis flip']
      self._menu.setItemVisible(toggle_id, False)

      self.replot()
      _dprint(3,'called replot in report_scalar_value')
      self._vells_plot = True

    def printplot(self):
      """ make a hardcopy of current displayed plot """
      self.emit(PYSIGNAL("do_print"),(self.is_vector,self.complex_type))
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
          temp_str = result + "x =%+.2g" % xpos1
          result = temp_str
          temp_str = result + " y =%+.2g" % ypos
          result = temp_str
          if not self.first_axis_inc is None:
            xpos = int((xpos -self.vells_axis_parms[self.x_parm][0]) / self.first_axis_inc)
          else:
# this inversion does not seem to work properly for scaled
# (vellsets) data, so use the above if possible
            xpos = self.plotImage.xMap.limTransform(xpos)
          if not self.second_axis_inc is None:
            ypos = int((ypos - self.vells_axis_parms[self.y_parm][0]) / self.second_axis_inc)
          else:
            ypos = self.plotImage.yMap.limTransform(ypos)
        else:
          xpos = int(xpos)
	  xpos1 = xpos
	  if not self.split_axis is None:
	    if xpos1 >=  self.split_axis:
	      xpos1 = xpos1 % self.split_axis
          temp_str = result + "x =%+.2g" % xpos1
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
          temp_str = result + " y =%+.2g" % ypos2
          result = temp_str
        value = self.raw_array[xpos,ypos]
	message = None
        temp_str = " value: %-.3g" % value
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

        if self.solver_display:
          if not self.solver_labels is None:
            label = self.solver_labels[xpos]
            message = label + ': ' + message
    
        return message
            
    # formatCoordinates()

    def reportCoordinates(self, x, y):
        """Format mouse coordinates as real world plot coordinates.
        """
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
#         mb_color = QMessageBox("metrics data",
#                     message,
#                     QMessageBox.Information,
#                     QMessageBox.Ok | QMessageBox.Default,
#                     QMessageBox.NoButton,
#                     QMessageBox.NoButton)
#         mb_color.exec_loop()
        else:
          temp_str = "nearest x=%-.3g" % x
          temp_str1 = " y=%-.3g" % y
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
      _dprint(3, 'called replot in refresh_marker_display ')
    # refresh_marker_display()

    def insert_marker_lines(self):
      _dprint(2, 'starting insert_marker_lines')
# alias
      fn = self.fontInfo().family()
      y = 0
      for i in range(self.num_y_markers):
        label = self.marker_labels[i]
        mY = self.insertLineMarker('', QwtPlot.yLeft)
        self.setMarkerLinePen(mY, QPen(Qt.white, 2, Qt.DashDotLine))
        y = y + self.y_marker_step
        self.setMarkerYPos(mY, y)

    def onMouseMoved(self, e):
      """ callback to handle MouseMoved event """ 
      if self.scalar_display:
        return

      xPos = e.pos().x()
      yPos = e.pos().y()
      if xPos < self.xlb-10 or xPos > self.xhb+10 or yPos > self.ylb+10 or yPos < self.yhb-10:
        if not self.display_solution_distances:
          self.enableOutline(0)
          self.startDrag()
        return

      # remove any 'source' descriptor if we are zooming
      if abs(self.xpos - xPos) > 2 and abs(self.ypos - yPos)>2:
        if self._popup_text.isVisible():
          self._popup_text.hide()
        if not self.source_marker is None:
          self.removeMarker(self.source_marker)
          self.source_marker = None
          self.replot()

    def infoDisplay(self, message, xpos, ypos):
      """ Display text under cursor in plot
          Figures out where the cursor is, generates the appropriate text, 
          and puts it on the screen.
      """
      self._popup_text.setText(message)
      self._popup_text.adjustSize()
      yhb = self.transform(QwtPlot.yLeft, self.axisScale(QwtPlot.yLeft).hBound())
      ylb = self.transform(QwtPlot.yLeft, self.axisScale(QwtPlot.yLeft).lBound())
      xhb = self.transform(QwtPlot.xBottom, self.axisScale(QwtPlot.xBottom).hBound())
      xlb = self.transform(QwtPlot.xBottom, self.axisScale(QwtPlot.xBottom).lBound())
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

    def onMousePressed(self, e):
        """ callback to handle MousePressed event """ 
        self.yhb = self.transform(QwtPlot.yLeft, self.axisScale(QwtPlot.yLeft).hBound())
        self.ylb = self.transform(QwtPlot.yLeft, self.axisScale(QwtPlot.yLeft).lBound())
        self.xhb = self.transform(QwtPlot.xBottom, self.axisScale(QwtPlot.xBottom).hBound())
        self.xlb = self.transform(QwtPlot.xBottom, self.axisScale(QwtPlot.xBottom).lBound())

        if Qt.LeftButton == e.button():
            message = None
            if self.is_vector: 
              if self.display_solution_distances:
            # Python semantics: self.pos = e.pos() does not work; force a copy
                  xPos = e.pos().x()
                  yPos = e.pos().y()
                  _dprint(2,'xPos yPos ', xPos, ' ', yPos);
# We get information about the qwt plot curve that is
# closest to the location of this mouse pressed event.
# We are interested in the nearest curve_number and the index, or
# sequence number of the nearest point in that curve.
                  self.array_curve_number, distance, xVal, yVal, self.array_index = self.closestCurve(xPos, yPos)
                  _dprint(2,' self.array_curve_number, distance, xVal, yVal, aelf.array_index ', self.array_curve_number, ' ', distance,' ', xVal, ' ', yVal, ' ', self.array_index);
                  shape = self.metrics_rank.shape
                  array_curve_number = self.array_curve_number - 1
                  self.metrics_index = 0 
                  if shape[1] > 1:
                    self.metrics_index = array_curve_number % shape[1]
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
              else:
            # Python semantics: self.pos = e.pos() does not work; force a copy
                xPos = e.pos().x()
                yPos = e.pos().y()
                _dprint(2,'xPos yPos ', xPos, ' ', yPos);
# We get information about the qwt plot curve that is
# closest to the location of this mouse pressed event.
# We are interested in the nearest curve_number and the index, or
# sequence number of the nearest point in that curve.
                curve_number, distance, xVal, yVal, index = self.closestCurve(xPos, yPos)
                _dprint(2,' curve_number, distance, xVal, yVal, index ', curve_number, ' ', distance,' ', xVal, ' ', yVal, ' ', index);
                message = self.reportCoordinates(xVal, yVal)
            else:
              message = self.formatCoordinates(e.pos().x(), e.pos().y())
            if not message is None:
              self.infoDisplay(message, e.pos().x(), e.pos().y())
            if self.zooming:
              self.xpos = e.pos().x()
              self.ypos = e.pos().y()
              self.enableOutline(1)
              self.setOutlinePen(QPen(Qt.black))
              self.setOutlineStyle(Qwt.Rect)
              if self.zoomStack == []:
                self.zoomState = (
                    self.axisScale(QwtPlot.xBottom).lBound(),
                    self.axisScale(QwtPlot.xBottom).hBound(),
                    self.axisScale(QwtPlot.yLeft).lBound(),
                    self.axisScale(QwtPlot.yLeft).hBound(),
                    )
        elif Qt.RightButton == e.button():
            e.accept()
            self._menu.popup(e.globalPos());
            if self.scalar_display:
              return

        elif Qt.MidButton == e.button():
            if self.active_image:
              if self.scalar_display:
                return
              xpos = e.pos().x()
              ypos = e.pos().y()
              xpos = self.invTransform(QwtPlot.xBottom, xpos)
              ypos = self.invTransform(QwtPlot.yLeft, ypos)
              self.x_arrayloc = ypos
              self.y_arrayloc = xpos
              if self._vells_plot:
                if not self.first_axis_inc is None:
                  xpos = int((xpos -self.vells_axis_parms[self.x_parm][0]) / self.first_axis_inc)
                else:
# this inversion does not seem to work properly for scaled
# (vellsets) data, so use the above if possible
                  xpos = self.plotImage.xMap.limTransform(xpos)
                if not self.second_axis_inc is None:
                  ypos = int((ypos - self.vells_axis_parms[self.y_parm][0]) / self.second_axis_inc)
                else:
                  ypos = self.plotImage.yMap.limTransform(ypos)
              else:
                xpos = int(xpos)
                ypos = int(ypos)
              self.xsect_xpos = xpos
              self.xsect_ypos = ypos
              self.show_x_sections = True
              self.calculate_cross_sections()
           
# fake a mouse move to show the cursor position
        if not self.scalar_display:
          self.onMouseMoved(e)

    # onMousePressed()

    def onMouseReleased(self, e):
        if Qt.LeftButton == e.button():
            if self._popup_text.isVisible():
              self._popup_text.hide()
            self.refresh_marker_display()
# assume a change of <= 2 screen pixels is just due to clicking
# left mouse button for coordinate values
            if self.zooming and abs(self.xpos - e.pos().x()) > 2 and abs(self.ypos - e.pos().y()) > 2:
              self.setOutlineStyle(Qwt.Cross)
              xmin = min(self.xpos, e.pos().x())
              xmax = max(self.xpos, e.pos().x())
              ymin = min(self.ypos, e.pos().y())
              ymax = max(self.ypos, e.pos().y())
              #print 'zoom: raw xmin xmax ymin ymax ', xmin, ' ', xmax, ' ', ymin, ' ', ymax
              if self.xTopAxisEnabled():
                xmin_t = self.invTransform(QwtPlot.xTop, xmin)
                xmax_t = self.invTransform(QwtPlot.xTop, xmax)
              if self.yRightAxisEnabled():
                ymin_r = self.invTransform(QwtPlot.yRight, ymin)
                ymax_r = self.invTransform(QwtPlot.yRight, ymax)
              xmin = self.invTransform(QwtPlot.xBottom, xmin)
              xmax = self.invTransform(QwtPlot.xBottom, xmax)
              ymin = self.invTransform(QwtPlot.yLeft, ymin)
              ymax = self.invTransform(QwtPlot.yLeft, ymax)
              #print 'zoom: transformed xmin xmax ymin ymax ', xmin, ' ', xmax, ' ', ymin, ' ', ymax
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
                else:
                  ymax = int (ymax)
                  ymin = int (ymin + 0.5)
                  xmax = int (xmax + 0.5)
                  xmin = int (xmin)
              if xmin == xmax or ymin == ymax:
                return
              if not self.zoomState is None:
                self.zoomStack.append(self.zoomState)
              self.zoomState = (xmin, xmax, ymin, ymax)
              self.enableOutline(0)
        
              self.setAxisScale(QwtPlot.xBottom, xmin, xmax)
              self.setAxisScale(QwtPlot.yLeft, ymin, ymax)
              if self.yRightAxisEnabled():
                self.setAxisScale(QwtPlot.yRight, ymin_r, ymax_r)
              if self.xTopAxisEnabled():
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
              toggle_id = self.menu_table['Reset zoomer']
              self._menu.setItemVisible(toggle_id, True)
              toggle_id = self.menu_table['Undo Last Zoom']
              if self.is_vector and self.complex_type:
                self._menu.setItemVisible(toggle_id, False)
              else:
                self._menu.setItemVisible(toggle_id, True)
              self.test_plot_array_sizes()
            self.replot()
            _dprint(3, 'called replot in onMouseReleased');
    # onMouseReleased()

    def resizeEvent(self, event):
      self.current_width = event.size().width()
      self.test_plot_array_sizes(event.size().width())
      self.updateLayout();

    # resizeEvent()


    def test_plot_array_sizes(self, width=None):

# if we have a solver plot 
      if len(self.chis_plot) > 0:
        zoom = False
        if len(self.zoomStack):
          zoom = True
        if not zoom:
          self.setAxisAutoScale(QwtPlot.yRight)
          self.setAxisAutoScale(QwtPlot.xTop)
        
          menuid = self.menu_table['Toggle log axis for chi_0']
          if self.log_axis_chi_0:
            self._menu.setItemChecked(menuid, True)
            self.setAxisOptions(QwtPlot.yRight, QwtAutoScale.Logarithmic)
          else:
            self._menu.setItemChecked(menuid, False)
            self.setAxisOptions(QwtPlot.yRight, QwtAutoScale.None)

          menuid = self.menu_table['Toggle log axis for solution vector']
          if self.log_axis_solution_vector:
            self._menu.setItemChecked(menuid, True)
            self.setAxisOptions(QwtPlot.xTop, QwtAutoScale.Logarithmic)
          else:
            self._menu.setItemChecked(menuid, False)
            self.setAxisOptions(QwtPlot.xTop, QwtAutoScale.None)

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
          
        if self.yRightAxisEnabled() and not zoom and not self.complex_type:
          self.setAxisAutoScale(QwtPlot.yRight)
        if self.xTopAxisEnabled() and not zoom:
          self.setAxisAutoScale(QwtPlot.xTop)
        keys = self.curveKeys()
        for j in range(len(keys)):
          plot_curve=self.curve(keys[j])
          if self.curveTitle(keys[j]) == 'imaginaries':
            self.setCurvePen(keys[j], QPen(Qt.blue, q_line_size))
            plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.green),
                  QPen(Qt.green), QSize(q_symbol_size,q_symbol_size)))
          if self.curveTitle(keys[j]) == 'reals':
            self.setCurvePen(keys[j], QPen(Qt.black, q_line_size))
            plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.red),
                  QPen(Qt.red), QSize(q_symbol_size,q_symbol_size)))
          if self.curveTitle(keys[j]) == 'xCrossSection' or self.curveTitle(keys[j]) == 'xrCrossSection' or self.curveTitle(keys[j]) == 'xiCrossSection':
            self.setCurvePen(keys[j], QPen(Qt.black, q_line_size))
            plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.black),
                  QPen(Qt.black), QSize(q_symbol_size,q_symbol_size)))
          if self.curveTitle(keys[j]) == 'yCrossSection':
            self.setCurvePen(keys[j], QPen(Qt.white, q_line_size))
            plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse,QBrush(Qt.white), 
                  QPen(Qt.white), QSize(q_symbol_size,q_symbol_size)))

    def calculate_cross_sections(self):
        """ calculate and display cross sections at specified location """
        _dprint(3, 'calculating cross-sections')
        # can't plot cross sections and chi display together
        if len(self.chis_plot) > 0:
          for i in range(len(self.chis_plot)):
            self.removeCurve(self.chis_plot[i])
          self.chis_plot = []

        shape = self.raw_array.shape
        _dprint(3, 'shape is ', shape)
        q_line_size = 2
        q_symbol_size = 5
        q_flag_size = 20
        q_size_split = 300
        if shape[0] > q_size_split:
          q_line_size = 1
          q_symbol_size = 3
          q_flag_size = 10
        self.x_array = zeros(shape[0], Float32)
        self.x_index = arange(shape[0])
        self.x_index = self.x_index + 0.5
        _dprint(3, 'self.xsect_ypos is ', self.xsect_ypos)
        try:
          for i in range(shape[0]):
            self.x_array[i] = self.raw_array[i,self.xsect_ypos]
        except:
          self.delete_cross_sections()
          return
        self.setAxisAutoScale(QwtPlot.yRight)
        if self.toggle_log_display:
          self.setAxisOptions(QwtPlot.yRight, QwtAutoScale.Logarithmic)
        else:
          self.setAxisOptions(QwtPlot.yRight, QwtAutoScale.None)
        self.y_array = zeros(shape[1], Float32)
        self.y_index = arange(shape[1])
        self.y_index = self.y_index + 0.5
        _dprint(3, 'self.xsect_xpos is ', self.xsect_xpos)
        try:
          for i in range(shape[1]):
            self.y_array[i] = self.raw_array[self.xsect_xpos,i]
        except:
          self.delete_cross_sections()
          return
        self.setAxisAutoScale(QwtPlot.xTop)
        if self.toggle_log_display:
          self.setAxisOptions(QwtPlot.xTop, QwtAutoScale.Logarithmic)
        else:
          self.setAxisOptions(QwtPlot.xTop, QwtAutoScale.None)
        if self.xrCrossSection is None:
          if self.complex_type:
            self.xrCrossSection = self.insertCurve('xrCrossSection')
          else:
            self.xrCrossSection = self.insertCurve('xCrossSection')
          self.setCurvePen(self.xrCrossSection, QPen(Qt.black, q_line_size))
          plot_curve=self.curve(self.xrCrossSection)
          plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, 
             QBrush(Qt.black), QPen(Qt.black), QSize(q_symbol_size,q_symbol_size)))
        self.enableAxis(QwtPlot.yRight)
        self.setAxisTitle(QwtPlot.yRight, 'x cross-section value')
        self.setCurveYAxis(self.xrCrossSection, QwtPlot.yRight)
        if self.complex_type:
          if self.xiCrossSection is None:
            self.xiCrossSection = self.insertCurve('xiCrossSection')
            self.setCurvePen(self.xiCrossSection, QPen(Qt.black, q_line_size))
            plot_curve=self.curve(self.xiCrossSection)
            plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, 
               QBrush(Qt.black), QPen(Qt.black), QSize(q_symbol_size,q_symbol_size)))
            self.setCurveYAxis(self.xiCrossSection, QwtPlot.yRight)
        if self.yCrossSection is None:
          self.yCrossSection = self.insertCurve('yCrossSection')
          self.setCurvePen(self.yCrossSection, QPen(Qt.white, q_line_size))
          plot_curve=self.curve(self.yCrossSection)
          plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, 
             QBrush(Qt.white), QPen(Qt.white), QSize(q_symbol_size,q_symbol_size)))
        self.enableAxis(QwtPlot.xTop)
        self.setAxisTitle(QwtPlot.xTop, 'y cross-section value')
        self.setCurveYAxis(self.yCrossSection, QwtPlot.yLeft)
        self.setCurveXAxis(self.yCrossSection, QwtPlot.xTop)
        if self._vells_plot:
          delta_vells = self.vells_axis_parms[self.x_parm][1] - self.vells_axis_parms[self.x_parm][0]
          if self.complex_type:
            delta_vells = 2.0 * delta_vells
          x_step = delta_vells / shape[0] 
          start_x = self.vells_axis_parms[self.x_parm][0] + 0.5 * x_step
          for i in range(shape[0]):
            self.x_index[i] = start_x + i * x_step
          delta_vells = self.vells_axis_parms[self.y_parm][1] - self.vells_axis_parms[self.y_parm][0]
          y_step = delta_vells / shape[1] 
          start_y = self.vells_axis_parms[self.y_parm][0] + 0.5 * y_step
          for i in range(shape[1]):
            self.y_index[i] = start_y + i * y_step

        self.log_offset = 0.0
        if self.toggle_log_display:
          self.log_offset = self.plotImage.getTransformOffset()
        if self.complex_type:
          limit = shape[0] / 2
          self.setCurveData(self.xrCrossSection, self.x_index[:limit], self.x_array[:limit] + self.log_offset)
          self.setCurveData(self.xiCrossSection, self.x_index[limit:], self.x_array[limit:] + self.log_offset)
        else:
          self.setCurveData(self.xrCrossSection, self.x_index, self.x_array + self.log_offset)
        self.setCurveData(self.yCrossSection, self.y_array + self.log_offset, self.y_index)

        self.test_plot_array_sizes()

        self.refresh_marker_display()
        self.show_x_sections = True
        toggle_id = self.menu_table['Delete X-Section Display']
        self._menu.setItemVisible(toggle_id, True)
        toggle_id = self.menu_table['Toggle Plot Legend']
        self._menu.setItemVisible(toggle_id, True)

    def toggleCurve(self, key):
      curve = self.curve(key)
      if curve:
        curve.setEnabled(not curve.enabled())
        self.replot()
        _dprint(3, 'called replot in toggleCurve');
    # toggleCurve()

    def setDisplayType(self, display_type):
      self._display_type = display_type
      self.plotImage.setDisplayType(display_type)
      self.emit(PYSIGNAL("display_type"),(self._display_type,))
      if display_type.find('grayscale') == -1:
        self.toggle_gray_scale = 0
      else:
        self.toggle_gray_scale = 1
    # setDisplayType

    def display_image(self, image):
      if self.complex_type:
        (nx,ny) = image.shape
        real_array =  image.getreal()
        self.raw_array = array(shape=(nx*2,ny),type=real_array.type());
        self.raw_array[:nx,:] = real_array
        self.raw_array[nx:,:] = image.getimag()
      else:
        self.raw_array = image
      self.raw_image = image

      _dprint(3, 'self.adjust_color_bar ', self.adjust_color_bar)
      if not self.colorbar_requested:
        _dprint(3, 'emitting colorbar_needed signal')
        self.emit(PYSIGNAL("colorbar_needed"), (1,))
        self.colorbar_requested = True
      
      # emit range for the color bar
      if self.adjust_color_bar:
        self.plotImage.setImageRange(image)
        image_limits = self.plotImage.getRealImageRange()
        self.emit(PYSIGNAL("max_image_range"),(image_limits, 0, self.toggle_log_display,self.ampl_phase))
        if self.complex_type:
          image_limits = self.plotImage.getImagImageRange()
          self.emit(PYSIGNAL("max_image_range"),(image_limits, 1, self.toggle_log_display,self.ampl_phase))
        self.adjust_color_bar = False

      if self._vells_plot:
        if self.complex_type:
          temp_x_axis_parms = self.vells_axis_parms[self.x_parm]
          begin = temp_x_axis_parms[0]
          end = begin + 2.0 * self.delta_vells 
          x_range = (begin, end)
          self.plotImage.setData(self.raw_image, x_range, self.vells_axis_parms[self.y_parm])
        else:
          _dprint(3, 'calling self.plotImage.setData with self.vells_axis_parms[self.x_parm], self.vells_axis_parms[self.y_parm] ', self.vells_axis_parms[self.x_parm], ' ', self.vells_axis_parms[self.y_parm])

          self.plotImage.setData(self.raw_image, self.vells_axis_parms[self.x_parm], self.vells_axis_parms[self.y_parm])
      else:
        self.plotImage.setData(self.raw_image)

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
        if len(self.metrics_plot) > 0:
          for i in range(len(self.metrics_plot)):
            self.removeCurve(self.metrics_plot[i])
        self.metrics_plot = []
        shape = self.metrics_rank.shape
        for i in range(shape[1]):
          plot_data= zeros(shape[0], Int32)
          for j in range(shape[0]):
            plot_data[j] = self.metrics_rank[j,i]
# add solver metrics info?
          metrics_title = 'metrics rank ' + str(i)
          key = self.insertCurve(metrics_title)
          self.metrics_plot.append(key)
          self.setCurvePen(key, QPen(Qt.black, 2))
          self.setCurveStyle(key,Qt.SolidLine)
        
          if self.array_flip:
            self.setCurveYAxis(key, QwtPlot.yLeft)
            self.setCurveXAxis(key, QwtPlot.xBottom)
            self.setCurveData(key, plot_data, self.iteration_number)
          else:
            self.setCurveYAxis(key, QwtPlot.xBottom)
            self.setCurveXAxis(key, QwtPlot.yLeft)
            self.setCurveData(key, self.iteration_number, plot_data)
          plot_curve=self.curve(key)
          plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.black),
                 QPen(Qt.black), QSize(10,10)))

      #chi_sq surfaces  - first remove any previous versions?
      #the following should work but seems to be causing problems
#     if len(self.chis_plot) > 0:
#       for i in range(len(self.chis_plot)):
#         self.removeCurve(self.chis_plot[i])
#         print 'removed chis_plot curve with key ', self.chis_plot[i]

      self.chis_plot = []
      shape = self.metrics_rank.shape
      self.enableAxis(QwtPlot.yRight, True)
      self.enableAxis(QwtPlot.xTop, True)
        
      self.setAxisTitle(QwtPlot.yRight, 'chi_0')
      self.setAxisTitle(QwtPlot.xTop, 'amplitude of solution vector')

      if self.first_chi_test:
        self.log_axis_solution_vector = False
        self.log_axis_chi_0 = False
        if self.chi_vectors.min() != 0.0 and self.chi_vectors.max() / self.chi_vectors.min() > 1000.0:
          self.log_axis_solution_vector = True
        if self.chi_zeros.min() != 0.0 and self.chi_zeros.max() / self.chi_zeros.min() > 1000.0:
           self.log_axis_chi_0 = True
        self.first_chi_test = False

      if self.log_axis_chi_0:
        self.setAxisOptions(QwtPlot.yRight, QwtAutoScale.Logarithmic)
      else:
        self.setAxisOptions(QwtPlot.yRight, QwtAutoScale.None)
      if self.log_axis_solution_vector:
        self.setAxisOptions(QwtPlot.xTop, QwtAutoScale.Logarithmic)
      else:
        self.setAxisOptions(QwtPlot.xTop, QwtAutoScale.None)

      for i in range(shape[1]):
        plot_data= zeros(shape[0], Float32)
        chi_data= zeros(shape[0], Float32)
        for j in range(shape[0]):
          plot_data[j] = self.chi_vectors[j,i]
          chi_data[j] = self.chi_zeros[j,i]
        curve = QwtPlotCurveSizes(self)
        curve.setTitle('vector sum of incremental solutions')
        curve.setPen(QPen(Qt.red, 2))
        curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse,
             QBrush(Qt.red), QPen(Qt.red), QSize(10,10)))
        curve.setStyle(Qt.SolidLine)
        key = self.insertCurve(curve)
        self.chis_plot.append(key)
        if self.array_flip:
          self.setCurveYAxis(key, QwtPlot.yRight)
          self.setCurveXAxis(key, QwtPlot.xTop)
          curve.setData(plot_data,chi_data)
        else:
          self.setCurveYAxis(key, QwtPlot.xTop)
          self.setCurveXAxis(key, QwtPlot.yRight)
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
        toggle_id = self.menu_table['Toggle Metrics Display']
        self._menu.setItemVisible(toggle_id, False)
        for i in range(shape[1]):
          plot_data1= zeros(shape[0], Float32)
          chi_data1= zeros(shape[0], Float32)
          for j in range(shape[0]):
            plot_data1[j] = self.sum_incr_soln_norm[j,i]
            chi_data1[j] = self.chi_zeros[j,i]
          curve = QwtPlotCurveSizes(self)
          curve.setTitle('sum of the norms of incremental solutions')
          curve.setPen(QPen(Qt.blue, 2))
          curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse,
             QBrush(Qt.blue), QPen(Qt.blue), QSize(10,10)))
          curve.setStyle(Qt.SolidLine)
          key = self.insertCurve(curve)
          self.chis_plot.append(key)
          if self.array_flip:
            self.setCurveYAxis(key, QwtPlot.yRight)
            self.setCurveXAxis(key, QwtPlot.xTop)
            curve.setData(plot_data1,chi_data1)
          else:
            self.setCurveYAxis(key, QwtPlot.xTop)
            self.setCurveXAxis(key, QwtPlot.yRight)
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
          plot_data2= zeros(shape[0], Float32)
          chi_data2= zeros(shape[0], Float32)
          for j in range(shape[0]):
            plot_data2[j] = self.incr_soln_norm[j,i]
            chi_data2[j] = self.chi_zeros[j,i]
          curve = QwtPlotCurveSizes(self)
          curve.setTitle('norms of incremental solutions')
          curve.setPen(QPen(Qt.green, 2))
          curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse,
             QBrush(Qt.green), QPen(Qt.green), QSize(10,10)))
          curve.setStyle(Qt.SolidLine)
          key = self.insertCurve(curve)
          self.chis_plot.append(key)
          if self.array_flip:
            self.setCurveYAxis(key, QwtPlot.yRight)
            self.setCurveXAxis(key, QwtPlot.xTop)
            curve.setData(plot_data2,chi_data2)
          else:
            self.setCurveYAxis(key, QwtPlot.xTop)
            self.setCurveXAxis(key, QwtPlot.yRight)
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
          curve.setSymbolList(symbolList)

        # plot eigenvalues of the covariance matrix?
        if not self.eigenvectors is None:
          self.enableAxis(QwtPlot.yLeft, True)
          self.enableAxis(QwtPlot.xBottom, True)
        
          self.setAxisTitle(QwtPlot.yLeft, 'Eigenvalue (black)')
          self.setAxisTitle(QwtPlot.xBottom, 'Eigenvalue number')

          for i in range (len(self.eigenvectors)):
            eigens = self.eigenvectors[i]
            eigenvalues = eigens[0]
            eigenlist = list(eigenvalues)
            eigenlist.sort(reverse=True)
            sorted_eigenvalues = array(eigenlist)
            shape = eigenvalues.shape
            x_data = arange(shape[0])
            curve = QwtPlotCurveSizes(self)
            curve.setPen(QPen(Qt.black, 2))
            curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse,
               QBrush(Qt.black), QPen(Qt.black), QSize(10,10)))
            curve.setStyle(Qt.SolidLine)
            key = self.insertCurve(curve)
            self.chis_plot.append(key)
            if self.array_flip:
              self.setCurveYAxis(key, QwtPlot.yLeft)
              self.setCurveXAxis(key, QwtPlot.xBottom)
              curve.setData(x_data,sorted_eigenvalues)
            else:
              self.setCurveYAxis(key, QwtPlot.xBottom)
              self.setCurveXAxis(key, QwtPlot.yLeft)
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

    def insert_array_info(self):
      if self.is_vector:
        return

# draw dividing line for complex array
      if self.complex_type:  
          self.complex_marker = self.insertLineMarker('', QwtPlot.xBottom)
          self.setMarkerLinePen(self.complex_marker, QPen(Qt.black, 2, Qt.SolidLine))
          self.setMarkerXPos(self.complex_marker, self.complex_divider)

# put in a line where cross sections are selected
      if not self.x_arrayloc is None:
          self.x_sect_marker = self.insertLineMarker('', QwtPlot.yLeft)
          self.setMarkerLinePen(self.x_sect_marker, QPen(Qt.black, 3, Qt.SolidLine))
          self.setMarkerYPos(self.x_sect_marker, self.x_arrayloc)

      if not self.y_arrayloc is None:
          self.y_sect_marker = self.insertLineMarker('', QwtPlot.xBottom)
          self.setMarkerLinePen(self.y_sect_marker, QPen(Qt.white, 3, Qt.SolidLine))
          self.setMarkerXPos(self.y_sect_marker, self.y_arrayloc)

# insert markers for solver metrics?
      if self.toggle_metrics and not self.solver_offsets is None:
       shape = self.solver_offsets.shape 
       if shape[0] > 1:
         self.y_solver_offset = []
         for i in range(shape[0] - 1):
           self.y_solver_offset.append(self.insertLineMarker('', QwtPlot.xBottom))
           self.setMarkerLinePen(self.y_solver_offset[i], QPen(Qt.black, 1, Qt.SolidLine))
           self.setMarkerXPos(self.y_solver_offset[i], self.solver_offsets[i])

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
# alias
        fn = self.fontInfo().family()
# text marker giving mean and std deviation of array
        if not self.info_marker is None:
          self.removeMarker(self.info_marker)
        self.info_marker = self.insertMarker()
        ylb = self.axisScale(QwtPlot.yLeft).hBound()
        xlb = self.axisScale(QwtPlot.xBottom).hBound()
        self.setMarkerPos(self.info_marker, xlb, ylb)
        self.setMarkerLabelAlign(self.info_marker, Qt.AlignLeft | Qt.AlignBottom)
        self.setMarkerLabel( self.info_marker, text_string,
          QFont(fn, 7, QFont.Bold, False),
          Qt.blue, QPen(Qt.red, 2), QBrush(Qt.white))

      if not self.log_marker is None:
        self.removeMarker(self.log_marker)
      if self.log_offset > 0.0:
        temp_str = "Log offset: %-.3g" % self.log_offset
        self.log_marker = self.insertMarker()
        ylb = self.axisScale(QwtPlot.yLeft).lBound()
        xlb = self.axisScale(QwtPlot.xBottom).hBound()
        self.setMarkerPos(self.log_marker, xlb, ylb)
        self.setMarkerLabelAlign(self.log_marker, Qt.AlignLeft | Qt.AlignTop)
        self.setMarkerLabel( self.log_marker, temp_str,
          QFont(fn, 7, QFont.Bold, False),
          Qt.blue, QPen(Qt.red, 2), QBrush(Qt.white))
      

    # insert_array_info()

    def plot_data(self, visu_record, attribute_list=None, label=''):
      """ process incoming data and attributes into the
          appropriate type of plot """
      _dprint(2, 'in plot data');
#      _dprint(2, 'visu_record ', visu_record)

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
        if visu_record.has_key('attrib'):
          self._attrib_parms = visu_record['attrib']
          _dprint(2,'self._attrib_parms ', self._attrib_parms);
          plot_parms = self._attrib_parms.get('plot')
          if plot_parms.has_key('tag_attrib'):
            temp_parms = plot_parms.get('tag_attrib')
            tag = temp_parms.get('tag')
            self._tag_plot_attrib[tag] = temp_parms
          if plot_parms.has_key('attrib'):
            temp_parms = plot_parms.get('attrib')
            plot_parms = temp_parms
          if self._plot_type is None and plot_parms.has_key('plot_type'):
            self._plot_type = plot_parms.get('plot_type')
          if self._display_type is None and plot_parms.has_key('spectrum_color'):
            self.setDisplayType(plot_parms.get('spectrum_color'))
          if self._attrib_parms.has_key('tag'):
            tag = self._attrib_parms.get('tag')
        else:
          self._plot_type = self.plot_key
      else:
# first get plot_type at first possible point in list - nearest root
        list_length = len(attribute_list)
        for i in range(list_length):
          self._attrib_parms = attribute_list[i]
          if self._attrib_parms.has_key('plot'):
            plot_parms = self._attrib_parms.get('plot')
            if plot_parms.has_key('tag_attrib'):
              temp_parms = plot_parms.get('tag_attrib')
              tag = temp_parms.get('tag')
              self._tag_plot_attrib[tag] = temp_parms
            if plot_parms.has_key('attrib'):
              temp_parms = plot_parms.get('attrib')
              plot_parms = temp_parms
            if self._plot_type is None and plot_parms.has_key('plot_type'):
              self._plot_type = plot_parms.get('plot_type')
            if self._window_title is None and plot_parms.has_key('title'):
              self._window_title = plot_parms.get('title')
              self.setTitle(self.label+ ' ' + self._window_title)
            if self._x_title is None and plot_parms.has_key('x_axis'):
              self._x_title = plot_parms.get('x_axis')
            if self._y_title is None and plot_parms.has_key('y_axis'):
              self._y_title = plot_parms.get('y_axis')
            if self._display_type is None and plot_parms.has_key('spectrum_color'):
              self.setDisplayType(plot_parms.get('spectrum_color'))
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
            else:
              _dprint(2,'non tuple tag ', tag);
              if self._string_tag is None:
                self._string_tag = ''
              if self._string_tag.find(tag) < 0:
                temp_tag = self._string_tag + ' ' + tag
                self._string_tag = temp_tag

      if visu_record.has_key('plot_label'):
        self._data_labels = visu_record['plot_label']
        _dprint(2,'insert_array_info: self._data_labels ', self._data_labels);
      else:
        self._data_labels = ''

# set defaults for anything that is not specified
      if self._string_tag is None:
        self._string_tag = ''
      if self._display_type is None:
        self.setDisplayType('hippo')
      if self._plot_type is None:
        self._plot_type = 'spectra'

      if visu_record.has_key('value'):
        self._data_values = visu_record['value']

      if len(self._tag_plot_attrib) > 0:
        _dprint(3, 'self._tag_plot_attrib has keys ', self._tag_plot_attrib.keys())

# extract and define labels for this data item
     # now generate  particular plot type
      if self._plot_type == 'spectra':
        self.num_y_markers = 0
        self.y_marker_step = None
# ensure that menu for display is updated if required
        self.initSpectrumContextMenu()
    # end plot_data()

    def plot_vells_array (self, data_array, data_label=" "):
      """ plot a Vells data array """
# no legends by default
      toggle_id = self.menu_table['Toggle Plot Legend']
      self._menu.setItemVisible(toggle_id, False)

      if not self.source_marker is None:
        self.removeMarker(self.source_marker)
      self.source_marker  = None
      self.array_plot(data_label, data_array)

    def setVellsParms(self, vells_axis_parms, axis_labels):
      self.vells_axis_parms = vells_axis_parms
      _dprint(3, 'self.vells_axis_parms = ', self.vells_axis_parms)
      self.axis_labels = axis_labels

    def reset_color_bar(self, reset_value=True):
      self.adjust_color_bar = reset_value

    def set_xaxis_title(self, title=''):
      self._x_title = title
      self.setAxisTitle(QwtPlot.xBottom, self._x_title)

    def set_yaxis_title(self, title=''):
      self._y_title = title
      self.setAxisTitle(QwtPlot.yLeft, self._y_title)

    def array_plot (self, data_label, incoming_plot_array, flip_axes=True):
      """ Figure out shape, rank dimension etc of an array and
          plot it. This is perhaps the main method of this class. """

# delete any previous curves
      self.removeCurves()
      self.xrCrossSection = None
      self.xrCrossSection_flag = None
      self.xiCrossSection = None
      self.yCrossSection = None
      self.enableAxis(QwtPlot.yLeft, False)
      self.enableAxis(QwtPlot.xBottom, False)
      self.enableAxis(QwtPlot.yRight, False)
      self.enableAxis(QwtPlot.xTop, False)
      self.myXScale = None
      self.myYScale = None
      self.split_axis = None
      self.array_parms = None
      self.scalar_display = False
      self.zooming = True
      self.adjust_color_bar = True
      if self.store_solver_array:
        self.solver_array = incoming_plot_array
        self.solver_title = data_label
         
        

# pop up menu for printing
      if self._menu is None:
        self._menu = QPopupMenu(self._mainwin);
        self.add_basic_menu_items()
        QObject.connect(self._menu,SIGNAL("activated(int)"),self.update_spectrum_display);


# set title
      self._window_title = data_label  
      self.setTitle(self.label+ ' ' + self._window_title)

# do we have solver data?
      if self._window_title.find('Solver Incremental') >= 0:
        self.solver_display = True

        toggle_id = self.menu_table['Toggle Metrics Display']
        self._menu.setItemVisible(toggle_id, True)

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
        axes = arange(incoming_plot_array.rank)[::-1]
        plot_array = transpose(incoming_plot_array, axes)
#       _dprint(3, 'transposed plot array ', plot_array, ' has shape ', plot_array.shape)

# check for NaNs and Infs etc

      nan_test = ieee.isnan(plot_array)
      if nan_test.max() > 0:
        plot_array[ieee.isnan(plot_array)] = -0.0123456789
        self.set_flag_toggles_active(True)
        self.setFlagsData(nan_test,False)

      inf_test = ieee.isinf(plot_array)
      if inf_test.max() > 0:
        plot_array[ieee.isinf(plot_array)] = -0.0123456789
        self.set_flag_toggles_active(True)
        self.setFlagsData(inf_test,False)

# figure out type and rank of incoming array
# for vectors, this is a pain as e.g. (8,) and (8,1) have
# different 'formal' ranks but really are the same 1-D vectors
# I'm not sure that the following covers all bases, but we are getting close
      self.is_vector = False;
      actual_array_rank = 0
      num_elements = 1
      for i in range(len(plot_array.shape)):
        num_elements = num_elements * plot_array.shape[i]
        if plot_array.shape[i] > 1:
          actual_array_rank = actual_array_rank + 1
      _dprint(3, 'actual array rank ', actual_array_rank)
      if actual_array_rank <= 1:
        self.is_vector = True;
      
# if we've doing a solver plot and we want to just display
# chi-square surfaces
      if self.display_solution_distances:
        self.is_vector = True

# I don't think we should ever see the N-D controller in the vector case.
# If self.original_data_rank > 2 that means that the cells dimensions are
# greater than the vector being plotted so we can turn off any ND Controller.
        if self.original_data_rank > 2: 
          self.toggle_ND_Controller = 0
          toggle_id = self.menu_table['Toggle ND Controller']
          self._menu.setItemVisible(toggle_id, False)
          self.emit(PYSIGNAL("show_ND_Controller"),(self.toggle_ND_Controller,))

# test for real or complex
      self.complex_type = False
      complex_type = False;
      if plot_array.type() == Complex32:
        complex_type = True;
      if plot_array.type() == Complex64:
        complex_type = True;
      self.complex_type = complex_type
      if self.complex_type: 
        self.complex_image = plot_array

# add possibility to switch between real/imag and ampl/phase
      toggle_id = self.menu_table['Toggle real/imag or ampl/phase Display']
      if self.complex_type:
        if self.ampl_phase is None:
          self._menu.changeItem(toggle_id, 'Show Data as Amplitude and Phase')
          self.ampl_phase = False
        else:
          if self.ampl_phase:
            self._menu.changeItem(toggle_id, 'Show Data as Real and Imaginary')
          else:
            self._menu.changeItem(toggle_id, 'Show Data as Amplitude and Phase')
        self._menu.setItemVisible(toggle_id, True)
      else:
        self._menu.setItemVisible(toggle_id, False)

# test if we have a 2-D array
      if self.is_vector == False and not self.log_switch_set:
        toggle_id = self.menu_table['Toggle logarithmic range for data']
        if self.toggle_log_display:
          self._menu.changeItem(toggle_id, 'Show Data with linear scale')
        else:
          self._menu.changeItem(toggle_id, 'Show Data with logarithmic scale')
        self._menu.setItemVisible(toggle_id, True)
        self.log_switch_set = True

      if self.is_vector == False:
        if has_vtk:
          toggle_id = self.menu_table['Toggle Warp Display']
          self._menu.setItemVisible(toggle_id, True)

        if self.original_data_rank > 2: 
          self.toggle_ND_Controller = 1
          toggle_id = self.menu_table['Toggle ND Controller']
          self._menu.setItemVisible(toggle_id, True)
          if has_vtk:
            toggle_id = self.menu_table['Toggle 3D Display']
            self._menu.setItemVisible(toggle_id, True)

        if self.complex_type: 
          self.complex_divider = plot_array.shape[0]
        self.enableAxis(QwtPlot.yLeft)
        self.enableAxis(QwtPlot.xBottom)

# don't use grid markings for 2-D 'image' arrays
        self.enableGridX(False)
        self.enableGridY(False)

# make sure options relating to color bar are in context menu
        toggle_id = self.menu_table['Toggle ColorBar']
        self._menu.setItemVisible(toggle_id, True)
        toggle_id = self.menu_table['Toggle Color/GrayScale Display']
        self._menu.setItemVisible(toggle_id, True)


# is zoom active?
        if len(self.zoomStack):
          toggle_id = self.menu_table['Reset zoomer']
          self._menu.setItemVisible(toggle_id, True)
          toggle_id = self.menu_table['Undo Last Zoom']
          if self.is_vector and self.complex_type:
            self._menu.setItemVisible(toggle_id, False)
          else:
            self._menu.setItemVisible(toggle_id, True)

        self.active_image = True

# get mean and standard deviation of array
        temp_str = ""
        if self.complex_type:
          if plot_array.mean().imag < 0:
            temp_str = "m: %-.3g %-.3gj" % (plot_array.mean().real,plot_array.mean().imag)
          else:
            temp_str = "m: %-.3g+ %-.3gj" % (plot_array.mean().real,plot_array.mean().imag)
        else:
          temp_str = "m: %-.3g" % plot_array.mean()
        temp_str1 = "sd: %-.3g" % standard_deviation(plot_array,complex_type )
        self.array_parms = temp_str + " " + temp_str1

        self.setAxisTitle(QwtPlot.yLeft, 'sequence')
        if self.complex_type and self._display_type != "brentjens":
          ampl_phase_image = None
          if self.ampl_phase:
            ampl_phase_image = self.convert_to_AP(self.complex_image)
          if self._vells_plot:
            _dprint(3, 'complex type: self._vells_plot ', self._vells_plot)
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
            _dprint(3,'testing self.y_marker_step ', self.y_marker_step)
	    if not self.y_marker_step is None:
              _dprint(3, 'creating split Y scale for Y axis')
              self.myYScale = ComplexScaleDraw(divisor=self.y_marker_step)
              self.setAxisScaleDraw(QwtPlot.yLeft, self.myYScale)

          if self.ampl_phase:
            self.display_image(ampl_phase_image)
          else:
            self.display_image(plot_array)

        else:
          if self._vells_plot:
            _dprint(3, 'not complex type: self._vells_plot ', self._vells_plot)
            _dprint(3, 'self.vells_axis_parms ',self.vells_axis_parms)
            self.x_parm = self.first_axis_parm
            self.y_parm = self.second_axis_parm
            if self.array_flip:
              self.x_parm = self.second_axis_parm
              self.y_parm = self.first_axis_parm
            _dprint(3, 'self.x_parm self.y_parm ', self.x_parm, ' ', self.y_parm)
            delta_vells = self.vells_axis_parms[self.x_parm][1] - self.vells_axis_parms[self.x_parm][0]
            self.delta_vells = delta_vells
            self.first_axis_inc = delta_vells / plot_array.shape[0] 
            delta_vells = self.vells_axis_parms[self.y_parm][1] - self.vells_axis_parms[self.y_parm][0]
            self.second_axis_inc = delta_vells / plot_array.shape[1] 
            self._x_title = self.vells_axis_parms[self.x_parm][2]
            self.setAxisTitle(QwtPlot.xBottom, self._x_title)
            self._y_title = self.vells_axis_parms[self.y_parm][2]
            self.setAxisTitle(QwtPlot.yLeft, self._y_title)
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
              _dprint(3, 'creating split Y scale for Y axis ', self.y_marker_step)
              self.myYScale = ComplexScaleDraw(divisor=self.y_marker_step)
              self.setAxisScaleDraw(QwtPlot.yLeft, self.myYScale)
          self.display_image(plot_array)

      if self.is_vector == True:
        _dprint(3, ' we are plotting a vector')

# remove any markers
        if not self.scalar_display:
          self.removeMarkers()
# make sure color bar is hidden
        self.emit(PYSIGNAL("show_colorbar_display"),(0,0)) 
        if self.complex_type:
          self.emit(PYSIGNAL("show_colorbar_display"),(0,1)) 
# make sure options relating to 2-D stuff are not visible in context menu
        toggle_id = self.menu_table['Toggle ColorBar']
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = self.menu_table['Toggle Color/GrayScale Display']
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = self.menu_table['Toggle ND Controller']
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = self.menu_table['Toggle 3D Display']
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = self.menu_table['Toggle Warp Display']
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = self.menu_table['Toggle axis flip']
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = self.menu_table['Toggle Plot Legend']
        self._menu.setItemVisible(toggle_id, True)

# make sure we are autoscaling in case an image was previous
# this will automagically do an unzoom, but just in case first
# call reset_zoom ...
        self.reset_zoom()

        self.setAxisAutoScale(QwtPlot.xBottom)
        self.setAxisAutoScale(QwtPlot.xTop)
        self.setAxisAutoScale(QwtPlot.yLeft)
        self.setAxisAutoScale(QwtPlot.yRight)
        self.setAxisScaleDraw(QwtPlot.xBottom, QwtScaleDraw())
        self.setAxisScaleDraw(QwtPlot.yLeft, QwtScaleDraw())
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
        self.enableGridX(True)
        self.enableGridY(True)

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
          x_step = delta_vells / num_elements 
          start_x = self.vells_axis_parms[self.x_parm][0] + 0.5 * x_step
          self.x_index = zeros(num_elements, Float32)
          for j in range(num_elements):
            self.x_index[j] = start_x + j * x_step
          self._x_title = self.vells_axis_parms[self.x_parm][2]
          self.setAxisTitle(QwtPlot.xBottom, self._x_title)
        else:
          if self._x_title is None:
            self._x_title = 'Array/Channel/Sequence Number'
          self.setAxisTitle(QwtPlot.xBottom, self._x_title)
          self.x_index = arange(num_elements)
          self.x_index = self.x_index + 0.5
# if we are plotting a single iteration solver solution
# plot on 'locations' of solver parameters. Use 'self.metrics_rank'
# as test, but don't plot metrics in this case
          if not self.metrics_rank is None:
            self.x_index = self.x_index + 0.5
        flattened_array = reshape(plot_array,(num_elements,))
#       _dprint(3, 'plotting flattened array ', flattened_array)

# we have a complex vector
        if self.complex_type:
          self.enableAxis(QwtPlot.yRight)
          self.enableAxis(QwtPlot.yLeft)
          self.enableAxis(QwtPlot.xBottom)
          if self.ampl_phase:
            self.setAxisTitle(QwtPlot.yLeft, 'Value: Amplitude (black line / red dots)')
            self.setAxisTitle(QwtPlot.yRight, 'Value: Phase (blue line / green dots)')
          else:
            self.setAxisTitle(QwtPlot.yLeft, 'Value: real (black line / red dots)')
            self.setAxisTitle(QwtPlot.yRight, 'Value: imaginary (blue line / green dots)')
          self.yCrossSection = self.insertCurve('imaginaries')
          self.xrCrossSection = self.insertCurve('reals')
          self.setCurvePen(self.xrCrossSection, QPen(Qt.black, q_line_size))
          self.setCurvePen(self.yCrossSection, QPen(Qt.blue, q_line_size))
          self.setCurveYAxis(self.xrCrossSection, QwtPlot.yLeft)
          self.setCurveYAxis(self.yCrossSection, QwtPlot.yRight)
          plot_curve=self.curve(self.xrCrossSection)
          plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.red),
                     QPen(Qt.red), QSize(q_symbol_size,q_symbol_size)))
          plot_curve=self.curve(self.yCrossSection)
          plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.green),
                     QPen(Qt.green), QSize(q_symbol_size,q_symbol_size)))
          self.x_array =  flattened_array.getreal()
          self.y_array =  flattened_array.getimag()
          if not self._flags_array is None:
            self.yCrossSection_flag = self.insertCurve('flag_imaginaries')
            self.xrCrossSection_flag = self.insertCurve('flag_reals')
            self.setCurvePen(self.xrCrossSection_flag, QPen(Qt.black, q_line_size))
            self.setCurvePen(self.yCrossSection_flag, QPen(Qt.blue, q_line_size))
            self.setCurveYAxis(self.xrCrossSection_flag, QwtPlot.yLeft)
            self.setCurveYAxis(self.yCrossSection_flag, QwtPlot.yRight)
            plot_curve=self.curve(self.xrCrossSection_flag)
            plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.red),
                     QPen(Qt.red), QSize(q_symbol_size,q_symbol_size)))
            plot_curve=self.curve(self.yCrossSection_flag)
            plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.green),
                     QPen(Qt.green), QSize(q_symbol_size,q_symbol_size)))
          if self.ampl_phase:
            abs_array = abs(flattened_array)
            phase_array = arctan2(self.y_array,self.x_array)
            self.x_array = abs_array
            self.y_array = phase_array
          if not self._flags_array is None:
            flags_x_array = compress(self._flags_array==0,self.x_array)
            flags_y_array = compress(self._flags_array==0,self.y_array)
            self.setCurveData(self.yCrossSection_flag, self.x_index, self.y_array)
            self.setCurveData(self.xrCrossSection_flag, self.x_index, self.x_array)
            flags_x_index = compress(self._flags_array==0,self.x_index)
            self.setCurveData(self.yCrossSection, flags_x_index, flags_y_array)
            self.setCurveData(self.xrCrossSection, flags_x_index, flags_x_array)
            axis_diff = abs(flags_y_array.max() - flags_y_array.min())
          else:
            axis_diff = abs(self.y_array.max() - self.y_array.min())
            self.setCurveData(self.yCrossSection, self.x_index, self.y_array)
            self.setCurveData(self.xrCrossSection, self.x_index, self.x_array)
          # the following is not the best test, but ...
          axis_subt = 0.01 * axis_diff
          if axis_diff <0.00001:
            axis_diff = 0.005
            axis_subt = 0.002
          if not self._flags_array is None:
            self.setAxisScale(QwtPlot.yRight, flags_y_array.min() - axis_subt, flags_y_array.max() + axis_diff)
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
            self.setAxisScale(QwtPlot.yLeft, flags_x_array.min() - axis_diff, flags_x_array.max() + axis_add)
          else:
            self.setAxisScale(QwtPlot.yLeft, self.x_array.min() - axis_diff, self.x_array.max() + axis_add)
          _dprint(3, 'plotting complex array with x values ', self.x_index)
          _dprint(3, 'plotting complex array with real values ', self.x_array)
          _dprint(3, 'plotting complex array with imag values ', self.y_array)

# stuff for flags
          if not self._flags_array is None:
            self.flags_x_index = compress(self._flags_array!=0,self.x_index)
            self.flags_r_values = compress(self._flags_array!=0,self.x_array)
            self.flags_i_values = compress(self._flags_array!=0,self.y_array)
            self.real_flag_vector = self.insertCurve('real_flags')
            self.setCurvePen(self.real_flag_vector, QPen(Qt.black))
            self.setCurveStyle(self.real_flag_vector, QwtCurve.Dots)
            self.setCurveYAxis(self.real_flag_vector, QwtPlot.yLeft)
            plot_flag_curve = self.curve(self.real_flag_vector)
            plot_flag_curve.setSymbol(QwtSymbol(QwtSymbol.XCross, QBrush(Qt.black),
                     QPen(Qt.black), QSize(q_flag_size, q_flag_size)))
            self.setCurveData(self.real_flag_vector, self.flags_x_index, self.flags_r_values)
            self.imag_flag_vector = self.insertCurve('imag_flags')
            self.setCurvePen(self.imag_flag_vector, QPen(Qt.black))
            self.setCurveStyle(self.imag_flag_vector, QwtCurve.Dots)
            self.setCurveYAxis(self.imag_flag_vector, QwtPlot.yRight)
            plot_flag_curve = self.curve(self.imag_flag_vector)
            plot_flag_curve.setSymbol(QwtSymbol(QwtSymbol.XCross, QBrush(Qt.black),
                     QPen(Qt.black), QSize(q_flag_size, q_flag_size)))
            self.setCurveData(self.imag_flag_vector, self.flags_x_index, self.flags_i_values)
            if self.flag_toggle:
              self.curve(self.real_flag_vector).setEnabled(True)
              self.curve(self.imag_flag_vector).setEnabled(True)
              self.curve(self.yCrossSection_flag).setEnabled(True)
              self.curve(self.xrCrossSection_flag).setEnabled(True)
              self.curve(self.yCrossSection).setEnabled(False)
              self.curve(self.xrCrossSection).setEnabled(False)
            else:
              self.curve(self.real_flag_vector).setEnabled(False)
              self.curve(self.imag_flag_vector).setEnabled(False)
              self.curve(self.yCrossSection_flag).setEnabled(False)
              self.curve(self.xrCrossSection_flag).setEnabled(False)
              self.curve(self.yCrossSection).setEnabled(True)
              self.curve(self.xrCrossSection).setEnabled(True)

        else:
          self.enableAxis(QwtPlot.yLeft)
          self.enableAxis(QwtPlot.xBottom)
          self.setAxisTitle(QwtPlot.yLeft, 'Value')
          self.enableAxis(QwtPlot.yRight, False)
          self.x_array =  flattened_array
          self.xrCrossSection = self.insertCurve('reals')
          self.setCurvePen(self.xrCrossSection, QPen(Qt.black, q_line_size))
          self.setCurveStyle(self.xrCrossSection,Qt.SolidLine)
          self.setCurveYAxis(self.xrCrossSection, QwtPlot.yLeft)
          plot_curve=self.curve(self.xrCrossSection)
          plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.red),
                     QPen(Qt.red), QSize(q_symbol_size,q_symbol_size)))
          if not self._flags_array is None:
            self.xrCrossSection_flag = self.insertCurve('flag_reals')
            self.setCurvePen(self.xrCrossSection_flag, QPen(Qt.black, q_line_size))
            self.setCurveStyle(self.xrCrossSection_flag,Qt.SolidLine)
            self.setCurveYAxis(self.xrCrossSection_flag, QwtPlot.yLeft)
            plot_curve=self.curve(self.xrCrossSection_flag)
            plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.red),
                     QPen(Qt.red), QSize(q_symbol_size,q_symbol_size)))
            flags_x_array = compress(self._flags_array==0,self.x_array)
            flags_x_index = compress(self._flags_array==0,self.x_index)
            axis_diff = abs(flags_x_array.max() - flags_x_array.min())
            self.setCurveData(self.xrCrossSection_flag, self.x_index, self.x_array)
            self.setCurveData(self.xrCrossSection, flags_x_index, flags_x_array)

# stuff for flags
            self.flags_x_index = compress(self._flags_array!= 0, self.x_index)
            self.flags_r_values = compress(self._flags_array!= 0, self.x_array)
            self.real_flag_vector = self.insertCurve('real_flags')
            self.setCurvePen(self.real_flag_vector, QPen(Qt.black))
            self.setCurveStyle(self.real_flag_vector, QwtCurve.Dots)
            self.setCurveYAxis(self.real_flag_vector, QwtPlot.yLeft)
            plot_flag_curve = self.curve(self.real_flag_vector)
            plot_flag_curve.setSymbol(QwtSymbol(QwtSymbol.XCross, QBrush(Qt.black),
                     QPen(Qt.black), QSize(q_flag_size, q_flag_size)))
            self.setCurveData(self.real_flag_vector, self.flags_x_index, self.flags_r_values)
            if self.flag_toggle:
              self.curve(self.real_flag_vector).setEnabled(True)
              self.curve(self.xrCrossSection_flag).setEnabled(True)
              self.curve(self.xrCrossSection).setEnabled(False)
            else:
              self.curve(self.real_flag_vector).setEnabled(False)
              self.curve(self.xrCrossSection_flag).setEnabled(False)
              self.curve(self.xrCrossSection).setEnabled(True)
            axis_add = abs(0.01 * axis_diff)
            if axis_diff <0.00001:
              axis_add = 0.002
            self.setAxisScale(QwtPlot.yLeft, flags_x_array.min() - axis_add, flags_x_array.max() + axis_add)
          else:
            self.setCurveData(self.xrCrossSection, self.x_index, self.x_array)

# do the replot
        self.replot()
        _dprint(3, 'called replot in array_plot');
    # array_plot()

#   def set_solver_metrics(self,metrics_rank, iteration_number, solver_offsets):
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
      real_array = a_p_image.getreal()
      imag_array = a_p_image.getimag()
      abs_array = abs(a_p_image)
      phase_array = arctan2(imag_array,real_array)
      a_p_image.setreal(abs_array)
      a_p_image.setimag(phase_array)
      return a_p_image

    def setFlagsData (self, incoming_flag_array, flip_axes=True):
      """ figure out shape, rank etc of a flag array and plot it  """
      flag_array = incoming_flag_array
      self.original_flag_array = incoming_flag_array
      if flip_axes and not self.axes_flip:
        axes = arange(incoming_flag_array.rank)[::-1]
        flag_array = transpose(incoming_flag_array, axes)

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
        self.plotImage.setFlagsArray(flag_array)
        if self.flag_toggle is None:
          self.flag_toggle = True
          self.plotImage.setDisplayFlag(self.flag_toggle)
          toggle_id = self.menu_table['toggle flagged data for plane ']
          self._menu.setItemChecked(toggle_id, self.flag_toggle)
      else:
        num_elements = n_rows*n_cols
        self._flags_array = reshape(flag_array,(num_elements,))
        if self.flag_toggle is None:
          self.flag_toggle = True
          toggle_id = self.menu_table['toggle flagged data for plane ']
          self._menu.setItemChecked(toggle_id, self.flag_toggle)

    # setFlagsData()

    def unsetFlagsData(self):
      self._flags_array = None
      self.flags_x_index = []
      self.flags_r_values = []
      self.flags_i_values = []
      self.plotImage.setDisplayFlag(False)
      self.flag_toggle = None

    def add_basic_menu_items(self):
        """ add standard options to context menu """
        toggle_id = self.menu_table['Modify Plot Parameters']
        self._menu.insertItem("Modify Plot Parameters", toggle_id)
        toggle_id = self.menu_table['Toggle Plot Legend']
        self._menu.insertItem("Toggle Plot Legend", toggle_id)
        self._menu.changeItem(toggle_id, 'Show Plot Legends')
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = self.menu_table['Toggle ColorBar']
        self._menu.insertItem("Toggle ColorBar", toggle_id)
        self._menu.changeItem(toggle_id, 'Hide ColorBar')
        toggle_id = self.menu_table['Toggle Color/GrayScale Display']
        self._menu.insertItem("Toggle Color/GrayScale Display", toggle_id)
        self._menu.changeItem(toggle_id, 'Show GrayScale Display')
        toggle_id = self.menu_table['Toggle 3D Display']
        self._menu.insertItem("Toggle 3D Display", toggle_id)
        self._menu.changeItem(toggle_id, 'Show 3D Display')         
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = self.menu_table['Toggle Warp Display']
        self._menu.insertItem("Toggle Warp Display", toggle_id)
        self._menu.changeItem(toggle_id, 'Show Warped Surface Display')         
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = self.menu_table['Toggle ND Controller']
        self._menu.insertItem("Toggle ND Controller", toggle_id)
        self._menu.changeItem(toggle_id, 'Hide ND Controller')
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = self.menu_table['Toggle results history']
        self._menu.insertItem("Toggle results history", toggle_id)
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = self.menu_table['Delete X-Section Display']
        self._menu.insertItem("Delete X-Section Display", toggle_id)
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = self.menu_table['Toggle axis flip']
        self._menu.insertItem("Toggle axis flip", toggle_id)
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = self.menu_table['Toggle log axis for chi_0']
        self._menu.insertItem("Toggle log axis for chi_0", toggle_id)
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = self.menu_table['Toggle log axis for solution vector']
        self._menu.insertItem("Toggle log axis for solution vector", toggle_id)
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = self.menu_table['Toggle chi-square surfaces display']
        self._menu.insertItem("Toggle chi-square surfaces display", toggle_id)
        self._menu.changeItem(toggle_id, 'Show chi-square surfaces')
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = self.menu_table['Toggle Metrics Display']
        self._menu.insertItem("Toggle Metrics Display", toggle_id)
        self._menu.changeItem(toggle_id, 'Hide Solver Metrics')
        self._menu.setItemVisible(toggle_id, False)

        toggle_id = self.menu_table['Toggle real/imag or ampl/phase Display']
        self._menu.insertItem("Toggle real/imag or ampl/phase Display", toggle_id)
        self._menu.setItemVisible(toggle_id, False)

        toggle_id = self.menu_table['Toggle logarithmic range for data']
        self._menu.insertItem("Toggle logarithmic range for data", toggle_id)
        self._menu.setItemVisible(toggle_id, False)
        self.log_switch_set = False

        toggle_id = self.menu_table['Change Vells']
        self._menu.insertItem(pixmaps.slick_redo.iconset(),'Change Selected Vells ', toggle_id)
        self._menu.setItemVisible(toggle_id, False)

# add potential menu for flagged data
        self.set_flag_toggles()

# add zoomer and printer stuff
        toggle_id = self.menu_table['Reset zoomer']
        self._menu.insertItem(pixmaps.viewmag.iconset(), "Reset zoomer", toggle_id)
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = self.menu_table['Undo Last Zoom']
        self._menu.insertItem(pixmaps.viewmag.iconset(), "Undo latest zoom", toggle_id)
        self._menu.setItemVisible(toggle_id, False)

# add the printer to the menu
        self.printer.addTo(self._menu);

# add option to save in PNG format
        toggle_id = self.menu_table['Save Display in PNG Format']
        self._menu.insertItem("Save Display in PNG Format", toggle_id)
        self._menu.setItemVisible(toggle_id, True)

# do this here?
        if self.chi_zeros is None:
          toggle_id = self.menu_table['Toggle axis flip']
          self._menu.setItemVisible(toggle_id, True)
        else:
          toggle_id = self.menu_table['Toggle log axis for chi_0']
          self._menu.setItemVisible(toggle_id, True)
          toggle_id = self.menu_table['Toggle log axis for solution vector']
          self._menu.setItemVisible(toggle_id, True)
          toggle_id = self.menu_table['Toggle chi-square surfaces display']
          self._menu.setItemVisible(toggle_id, True)

        if self._zoom_display:
          toggle_id = self.menu_table['Toggle Pause']
          self._menu.insertItem("Pause", toggle_id)
          toggle_id = self.menu_table['Toggle Comparison']
          self._menu.insertItem("Do Comparison", toggle_id)
          self._menu.setItemVisible(toggle_id, False)

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
      if self.test_complex:
        m = fromfunction(RealDist, (30,20))
        n = fromfunction(ImagDist, (30,20))
        vector_array = zeros((30,1), Complex64)
        shape = m.shape
        for i in range(shape[0]):
          for j in range(shape[1]):
            m[i,j] = m[i,j] + self.index * random.random()
            n[i,j] = n[i,j] + 3 * self.index * random.random()
        a = zeros((shape[0],shape[1]), Complex64)
        a.setreal(m)
        a.setimag(n)         
        for i in range(shape[0]):
          vector_array[i,0] = a[i,0]
        if self.index % 2 == 0:
          _dprint(2, 'plotting complex vector with shape ',vector_array.shape);
          self.array_plot('test_vector_complex', vector_array)
        else:
          _dprint(2, 'plotting complex array with shape ',a.shape);
          self.array_plot('test_image_complex',a)
          self.test_complex = False
      else:
        vector_array = zeros((30,1), Float32)
        m = fromfunction(dist, (30,20))
        shape = m.shape
        for i in range(shape[0]):
          for j in range(shape[1]):
            m[i,j] = m[i,j] + self.index * random.random()
        for i in range(shape[0]):
          vector_array[i,0] = m[i,0]
        if self.index % 2 == 0:
          _dprint(2, 'plotting real array with shape ',m.shape);
          self.array_plot('test_image',m)
        else:
          _dprint(2, 'plotting real vector with shape ', vector_array.shape);
          self.array_plot('test_vector', vector_array)
          self.test_complex = True

      self.index = self.index + 1
    # timerEvent()

def make():
    demo = QwtImageDisplay('plot_key')
    demo.resize(500, 300)
    demo.show()
# uncomment the following
    demo.start_test_timer(5000, True, "hippo")

# or
# uncomment the following three lines
#    try:
#      import pyfits
#      image = pyfits.open('./m51_32.fits')
#   image = pyfits.open('./WN30080H.fits')
#      demo.array_plot('M51', image[0].data)
#    except:
#      print 'Exception while importing pyfits module:'
#      traceback.print_exc();
#      return

    return demo

def main(args):
    app = QApplication(args)
    demo = make()
    app.setMainWidget(demo)
    app.exec_loop()


# Admire
if __name__ == '__main__':
    main(sys.argv)

