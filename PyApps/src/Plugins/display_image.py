#!/usr/bin/env python

import sys
from qt import *
from qwt import *
from numarray import *
from UVPAxis import *
from ComplexColorMap import *
from ComplexScaleDraw import *
from QwtPlotImage import *
from Timba.GUI.pixmaps import pixmaps
from guiplot2dnodesettings import *
#from tabdialog import *
import random

from Timba.utils import verbosity
_dbg = verbosity(0,name='displayimage');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

# compute standard deviation of a complex or real array
# the std_dev given here was computed according to the
# formula given by Oleg (It should work for real or complex array)
def standard_deviation(incoming_array,complex_type):
#  return incoming_array.stddev()
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
Button 2 (Middle): If you click the <b>middle</b> mouse button on a location inside a <b>two-dimensional</b> array plot, then X and Y cross-sections centred on this location are overlaid on the display. A continuous black line marks the location of the X cross-section and the black dotted line shows the cross section values, which are tied to the right hand scale. The white lines show corresponding information for the Y cross section, whose values are tied to the top scale of the plot. You can remove the X,Y cross sections from the display by hitting the 'refresh' icon (the two arrows circling each other) in the upper left corner of the plot window.(NOTE: There is presently a bug here - if the plot panel is floated free of the browser, the refresh option does not work.) If the <b>Legends</b> display has been toggled to ON (see Button 3 below), then a sequence of push buttons will appear along the right hand edge of the display. Each of the push buttons is associated with one of the cross-section plots. Clicking on a push button will cause the corresponding plot to appear or disappear, depending on the current state.<br><br>
Button 3 (Right):Click the <b>right</b> mouse button in a spectrum display window to get get a context menu with options for printing, resetting the zoom, selecting another image, or toggling a <b>Legends</b> display. If you click on the 'Disable zoomer ' icon  in a window where you had zoomed in on a selected region, then the original entire array is re-displayed. Vellsets or <b>visu</b> data sets may contain multiple arrays. Only one of these arrays can be displayed at any one time. If additional images are available for viewing, they will be listed in the context menu. If you move the right mouse button to the desired image name in the menu and then release the button, the requested image will now appear in the display. If you select the Print option from the menu, the standard Qt printer widget will appear. That widget will enable you print out a copy of your plot, or save the plot in Postscript format to a file. Note that at present one cannot print out the Colorbar display associated with a two-dimensional array plot. This will be worked on. If you make cross-section plots (see Button 2 above), by default a <b>Legends</b> display associating push buttons with these plots is not shown. You can toggle the display of these push buttons ON or OFF by selecting the Toggle Cross-Section Legend option from the context menu. If you are working with two-dimensional arrays, then additional options to toggle the ON or OFF display of a colorbar showing the range of intensities and to switch between GrayScale and Color representations of the pixels will be shown.<br><br>
By default, colorbars are turned ON while Legends are turned OFF when a plot is first produced. <br><br> 
You can obtain more information about the behavior of the colorbar by using the QWhatsThis facility associated with the colorbar.'''

class QwtImageDisplay(QwtPlot):

    display_table = {
        'hippo': 'hippo',
        'grayscale': 'grayscale',
        'brentjens': 'brentjens',
        }

    def __init__(self, plot_key=None, parent=None):
        QwtPlot.__init__(self, plot_key, parent)
        # create copy of standard application font..
        font = QFont(QApplication.font());
        fi = QFontInfo(font);
        # and scale it down to 50%
        font.setPointSize(fi.pointSize()*0.5);
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
	self.flag_toggle = False
	self.flag_blink = False
        self._solver_flag = False

# save raw data
        self.plot_key = plot_key
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
        self._plot_type = None
	self._plot_dict_size = None
	self.created_combined_image = False
        self.dimensions_tested = False
	self._combined_image_id = None
        self.colorbar_requested = False
	self.is_combined_image = False
        self.active_image_index = None
        self.y_marker_step = None
        self.imag_flag_vector = None
        self.real_flag_vector = None
        self.array_parms = None
        self.metrics_rank = None
        self.toggles_not_set = True
        self.iteration_number = None
        self._active_plane = None
        self._active_perturb = None
        self.first_axis_inc = None
        self.second_axis_inc = None
        self.context_menu_done = None
        self._mhz = False
        self._khz = False
        self.image_min = None
        self.image_max = None
        self.image_shape = None
        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None
        self.adjust_color_bar = True
        self.do_calc_vells_range = True
        self.array_selector = None
        self.show_x_sections = False
        # make a QwtPlot widget
        self.plotLayout().setMargin(0)
        self.plotLayout().setCanvasMargin(0)
        self.plotLayout().setAlignCanvasToScales(1)
        self.setTitle('QwtImageDisplay')

        self.label = ''
        self.zooming = 0
        self.setlegend = 0
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
        self.dummy_xCrossSection = None
        self.xCrossSection = None
        self.yCrossSection = None
        self.myXScale = None
        self.myYScale = None
        self.active_image = False
        self.info_marker = None
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
        self.xpos = 0
        self.ypos = 0
        self.toggle_array_rank = 1
        self.toggle_color_bar = 1
        self.toggle_ND_Controller = 1
        self.toggle_gray_scale = 0
        self._toggle_flag_label = None
        self._toggle_blink_label = None
        QWhatsThis.add(self, display_image_instructions)

# Finally, over-ride default QWT Plot size policy of MinimumExpanding
# Otherwise minimum size of plots is too large when embedded in a
# QGridlayout
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

#       self.__init__

    def getPlotParms(self):
        plot_parms = {}
        plot_parms['window_title'] = self._window_title
        plot_parms['x_title'] = self._x_title
        plot_parms['y_title'] = self._y_title
        plot_parms['x_auto_scale'] = self._x_auto_scale
        plot_parms['y_auto_scale'] = self._y_auto_scale
        plot_parms['axis_xmin'] = self.axis_xmin
        plot_parms['axis_xmax'] = self.axis_xmax
        plot_parms['axis_ymin'] = self.axis_ymin
        plot_parms['axis_ymax'] = self.axis_ymax
     
        return plot_parms

    def setPlotParms(self, plot_parms):
#       print 'in setPlotParms with plot_parms ', plot_parms
        self._window_title = plot_parms['window_title'] 
        self._x_title = plot_parms['x_title']
        self._y_title = plot_parms['y_title'] 

        self.setTitle(self._window_title)
        self.setAxisTitle(QwtPlot.xBottom, self._x_title)
        self.setAxisTitle(QwtPlot.yLeft, self._y_title)

        self._x_auto_scale = plot_parms['x_axis_auto_scale']
        if self._x_auto_scale == '1':
          self._x_auto_scale = True
        else:
          self._x_auto_scale = False
        self._y_auto_scale = plot_parms['y_axis_auto_scale']
        if self._y_auto_scale == '1':
          self._y_auto_scale = True
        else:
          self._y_auto_scale = False
        if not self._x_auto_scale: 
          self.axis_xmin = plot_parms['x_axis_min']
          self.axis_xmax = plot_parms['x_axis_max']
#         self.setAxisScale(QwtPlot.xBottom, float(self.axis_xmin), float(self.axis_xmax))
        if not self._y_auto_scale: 
          self.axis_ymin = plot_parms['y_axis_min']
          self.axis_ymax = plot_parms['y_axis_max']
#         self.setAxisScale(QwtPlot.yLeft, float(self.axis_ymin), float(self.axis_ymax))
        self.axis_ratio = plot_parms['ratio']
        self.aspect_ratio = plot_parms['aspect_ratio']
        self.replot()

    def initSpectrumContextMenu(self):
        """Initialize the spectra context menu
        """
        # skip if no main window
        if not self._mainwin:
          return;


        if self._menu is None:
          self._menu = QPopupMenu(self._mainwin);
          self.add_basic_menu_items()
          QObject.connect(self._menu,SIGNAL("activated(int)"),self.update_spectrum_display);
          self._signal_id = -1
          self._plot_dict = {}
          self._plot_label = {}
          self._combined_label_dict = {}

        num_plot_arrays = len(self._data_values)
        _dprint(2,' number of arrays to plot ', num_plot_arrays)
        for i in range(num_plot_arrays):
          data_label = ''
	  plot_label = ''
          combined_display_label = ''
          if isinstance(self._data_labels, tuple):
            data_label = 'go to ' + self._string_tag  +  " " +self._data_labels[i] + ' ?'
            combined_display_label = self._string_tag  +  " " + self._data_labels[i]
            plot_label = 'spectra:' + combined_display_label
          else:
            data_label = 'go to ' + self._string_tag  +  " " +self._data_labels +' ?'
            combined_display_label = self._string_tag  +  " " + self._data_labels
            plot_label = 'spectra:' + combined_display_label
	  plot_label_not_found = True


# use hack below instead
#          plot_array = self._data_values[i].copy()

# hack to get array display correct until forest.state
# record is available
          axes = arange(self._data_values[i].rank)[::-1]
          plot_array = transpose(self._data_values[i], axes)


	  for j in range(len(self._plot_label)):
	    if self._plot_label[j] == plot_label:
	      plot_label_not_found =False
# if we are finding repeat plot labels, then we have cycled
# through the plot tree at least once, and we have
# the maximum size of the plot_dict
              self._plot_dict_size = len(self._plot_dict)
              _dprint(2,' plot_dict_size: ', self._plot_dict_size)
	      self._plot_dict[j] = plot_array
	      break

# if no plot label found, then add array into plot_dict and
# update selection menu
          if plot_label_not_found:
            self._signal_id = self._signal_id + 1
            self._menu.insertItem(data_label,self._signal_id)
	    self._plot_dict[self._signal_id] = plot_array
            self._plot_dict_size = len(self._plot_dict)
	    self._plot_label[self._signal_id] = plot_label
            self._combined_label_dict[self._signal_id] = combined_display_label
# otherwise create or update the combined image
	  else:
	    if self._plot_dict_size > 1 and not self.created_combined_image:
	      self.create_combined_array()
	    else: 
	      if self.created_combined_image:
	        self.update_combined_array()

    def create_combined_array(self):
# create combined array from contents of plot_dict
      shape = self._plot_dict[0].shape
      self.y_marker_step = shape[1]
      self.num_y_markers = self._plot_dict_size 
      temp_array = zeros((shape[0],self._plot_dict_size* shape[1]), self._plot_dict[0].type())
      self.marker_labels = []
      for l in range(self._plot_dict_size ):
#        dummy_array =  self._plot_dict[l].copy()
        dummy_array =  self._plot_dict[l]
        for k in range(shape[0]):
          for j in range(shape[1]):
            j_index = l * shape[1] + j
            temp_array[k,j_index] = dummy_array[k,j]
        self.marker_labels.append(self._combined_label_dict[l])
      self.created_combined_image = True
      self._signal_id = self._signal_id + 1
      self._combined_image_id = self._signal_id
      self._menu.insertItem('go to combined image',self._signal_id)
      self._plot_dict[self._signal_id] = temp_array
      self._plot_label[self._signal_id] = 'spectra: combined image'

    def update_combined_array(self):
# remember that the size of the plot_dict includes the combined array    
      data_dict_size = self._plot_dict_size - 1
# create combined array from contents of plot_dict
      shape = self._plot_dict[0].shape
      self.y_marker_step = shape[1]
      temp_array = zeros((shape[0], data_dict_size* shape[1]), self._plot_dict[0].type())
      self.marker_labels = []
      for l in range(data_dict_size ):
        dummy_array =  self._plot_dict[l]
        shape_array = dummy_array.shape
        for k in range(shape_array[0]):
          for j in range(shape_array[1]):
            j_index = l * shape[1] + j
            if j_index <data_dict_size* shape[1]:
              temp_array[k,j_index] = dummy_array[k,j]
        self.marker_labels.append(self._combined_label_dict[l])
      self._plot_dict[self._combined_image_id] = temp_array

    def delete_cross_sections(self):
      if self.show_x_sections:
# delete any previous curves
        self.removeCurves()
        self.xCrossSection = None
        self.yCrossSection = None
        self.enableAxis(QwtPlot.yRight, False)
        self.enableAxis(QwtPlot.xTop, False)
        self.xCrossSectionLoc = None
        self.yCrossSectionLoc = None
        self.dummy_xCrossSection = None
        toggle_id = 305
        self.show_x_sections = False
        self._menu.setItemVisible(toggle_id, False)
# add solver metrics info back in?
        if not self.metrics_rank is None:
          self.metrics_plot = self.insertCurve('metrics')
          self.setCurvePen(self.metrics_plot, QPen(Qt.black, 2))
          self.setCurveStyle(self.metrics_plot,Qt.SolidLine)
          self.setCurveYAxis(self.metrics_plot, QwtPlot.yLeft)
          self.setCurveXAxis(self.metrics_plot, QwtPlot.xBottom)
          plot_curve=self.curve(self.metrics_plot)
          plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.black),
                     QPen(Qt.black), QSize(10,10)))
          self.setCurveData(self.metrics_plot, self.metrics_rank, self.iteration_number)
        self.replot()

    def update_spectrum_display(self, menuid):
      if menuid < 0:
        self.zoom()
        return
      if menuid == 304:
        self.reset_zoom()
        return
      if menuid == 305:
        self.delete_cross_sections()
        return
      if menuid == 299:
        self.updatePlotParameters()
        return
      if menuid == 300:
        self.toggleLegend()
        return
      if menuid == 301:
        if self.toggle_color_bar == 1:
          self.toggle_color_bar = 0
        else:
          self.toggle_color_bar = 1
        self.emit(PYSIGNAL("show_colorbar_display"),(self.toggle_color_bar,))
        return
      if menuid == 302:
        if self.toggle_gray_scale == 1:
          self.setDisplayType('hippo')
        else:
          self.setDisplayType('grayscale')
        self.defineData()
        self.replot()
        return
      if menuid == 303:
        if self.toggle_ND_Controller == 1:
          self.toggle_ND_Controller = 0
        else:
          self.toggle_ND_Controller = 1
        self.emit(PYSIGNAL("show_ND_Controller"),(self.toggle_ND_Controller,))
        return
      self.active_image_index = menuid
      if self.is_combined_image:
        self.removeMarkers()
        self.info_marker = None
        self.source_marker = None
      self.is_combined_image = False
      if not self._combined_image_id is None:
        if self._combined_image_id == menuid:
	  self.is_combined_image = True
          self.reset_color_bar(True)
      self.array_plot(self._plot_label[menuid], self._plot_dict[menuid], False)

    def defineData(self):
       if self._vells_plot:
         if self.complex_type:
           temp_x_axis_parms = self.vells_axis_parms[self.x_parm]
           begin = temp_x_axis_parms[0]
           end = begin + 2.0 * self.delta_vells 
           x_range = (begin, end)
           self.plotImage.setData(self.raw_image, x_range, self.vells_axis_parms[self.y_parm])
         else:
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

    def initVellsContextMenu (self):
        # skip if no main window
        if not self._mainwin:
          return;
        if self.context_menu_done:
          return;
        if self._menu is None:
          self._menu = QPopupMenu(self._mainwin);
          QObject.connect(self._menu,SIGNAL("activated(int)"),self.update_vells_display);
          self.add_basic_menu_items()

        id = -1
        perturb_index = -1
# are we dealing with Vellsets?
        number_of_planes = len(self._vells_rec["vellsets"])
        _dprint(3, 'number of planes ', number_of_planes)
        self._next_plot = {}
        flag_plane = -1
        initial_plane = None
        for i in range(number_of_planes):
          id = id + 1
          if self._vells_rec.vellsets[i].has_key("value"):
            if initial_plane is None:
              initial_plane = i
            menu_label = "go to plane " + str(i) + " value" 
            self._next_plot[id] = menu_label
            self._menu.insertItem(menu_label,id)
          if self._vells_rec.vellsets[i].has_key("perturbed_value"):
            try:
              number_of_perturbed_arrays = len(self._vells_rec.vellsets[i].perturbed_value)
              perturb_index  = perturb_index  + 1
              for j in range(number_of_perturbed_arrays):
                id = id + 1
                key = " perturbed_value "
                menu_label =  "   -> go to plane " + str(i) + key + str(j) 
                self._next_plot[id] = menu_label 
                self._menu.insertItem(menu_label,id)
            except:
              _dprint(3, 'The perturbed values cannot be displayed.')
# don't display message for the time being
#              Message =  'It would appear that there is a problem with perturbed values.\nThey cannot be displayed.'
#              mb_msg = QMessageBox("display_image.py",
#                               Message,
#                               QMessageBox.Warning,
#                               QMessageBox.Ok | QMessageBox.Default,
#                               QMessageBox.NoButton,
#                               QMessageBox.NoButton)
#              mb_msg.exec_loop()
          if self.toggles_not_set and self._vells_rec.vellsets[i].has_key("flags"):
            flag_plane = i
            self.toggles_not_set = False
        if flag_plane > -1:
          self._toggle_flag_label = "toggle flagged data for plane " + str(flag_plane) 
	  toggle_id = 200
          self._menu.insertItem(self._toggle_flag_label,toggle_id)
          if flag_plane == initial_plane:
            self._menu.setItemEnabled(toggle_id, True)
            self._menu.setItemVisible(toggle_id, True)
          else:
            self._menu.setItemEnabled(toggle_id, False)
            self._menu.setItemVisible(toggle_id, False)
          self._toggle_blink_label = "toggle blink of flagged data for plane " + str(flag_plane)
          toggle_id = 201
          self._menu.insertItem(self._toggle_blink_label,toggle_id)
          if flag_plane == initial_plane:
            self._menu.setItemEnabled(toggle_id, True)
            self._menu.setItemVisible(toggle_id, True)
          else:
            self._menu.setItemEnabled(toggle_id, False)
            self._menu.setItemVisible(toggle_id, False)
        if perturb_index == -1 and number_of_planes == 1:
            self._menu.removeItem(0)
        self.context_menu_done = True
    # end initVellsContextMenu()

    def zoom(self):
      if self.zooming == 0:
        self.zooming = 1
        self.zoom_button.setText("Disable zoomer");
      else:
        self.zooming = 0
        self.zoom_button.setText("Enable zoomer");

    def reset_zoom(self):
        if len(self.zoomStack):
          while len(self.zoomStack):
            xmin, xmax, ymin, ymax = self.zoomStack.pop()
          self.setAxisScale(QwtPlot.xBottom, xmin, xmax)
          self.setAxisScale(QwtPlot.yLeft, ymin, ymax)
          self._x_auto_scale = False
          self._y_auto_scale = False
          self.axis_xmin = xmin
          self.axis_xmax = xmax
          self.axis_ymin = ymin
          self.axis_ymax = ymax
          self.xmin = None
          self.xmax = None
          self.ymin = None
          self.ymax = None
          self.refresh_marker_display()
          self.replot()
          _dprint(3, 'called replot in unzoom')
        else:
          return

    def toggleLegend(self):
      if self.setlegend == 1:
        self.setlegend = 0
        self.enableLegend(False)
      else:
        self.setlegend = 1
        self.enableLegend(True)
      self.setAutoLegend(self.setlegend)
      self.replot()

    # toggleLegend()

    def updatePlotParameters(self):
      parms_interface = WidgetSettingsDialog(actual_parent=self, gui_parent=self)

    def setImageRange(self, min, max):
      image_min = min * 1.0
      image_max = max * 1.0
      if image_min > image_max:
        temp = image_max
        image_max = image_min
        image_min = temp
      self.plotImage.setImageRange((image_min, image_max))
      self.defineData()
      self.image_min = image_min
      self.image_max = image_max
      self.replot()
    # setImageRange
	

    def timerEvent_blink(self):
# stop blinking     
      if not self.flag_blink:
        self.timer.stop()
        self.flag_toggle = False
        if self.real_flag_vector is None:
          self.plotImage.setDisplayFlag(self.flag_toggle)
        else:
          if not self.real_flag_vector is None:
            self.curve(self.real_flag_vector).setEnabled(self.flag_toggle)
          if not self.imag_flag_vector is None:
            self.curve(self.imag_flag_vector).setEnabled(self.flag_toggle)
        self.replot()
        _dprint(3, 'called replot in timerEvent_blink')
      else:
        if self.flag_toggle == False:
          self.flag_toggle = True
        else:
          self.flag_toggle = False
        if self.real_flag_vector is None:
          self.plotImage.setDisplayFlag(self.flag_toggle)
        else:
          self.curve(self.real_flag_vector).setEnabled(self.flag_toggle)
          if not self.imag_flag_vector is None:
            self.curve(self.imag_flag_vector).setEnabled(self.flag_toggle)
        self.replot()
        _dprint(3, 'called replot in timerEvent_blink')

    def update_vells_display(self, menuid):
      if menuid < 0:
        self.zoom()
        return
      if menuid == 304:
        self.reset_zoom()
        return
      if menuid == 305:
        self.delete_cross_sections()
        return
      if menuid == 299:
        self.updatePlotParameters()
        return
      if menuid == 300:
        self.toggleLegend()
        return
      if menuid == 301:
        if self.toggle_color_bar == 1:
          self.toggle_color_bar = 0
        else:
          self.toggle_color_bar = 1
        self.emit(PYSIGNAL("show_colorbar_display"),(self.toggle_color_bar,))
        return
      if menuid == 302:
        if self.toggle_gray_scale == 1:
          self.setDisplayType('hippo')
        else:
          self.setDisplayType('grayscale')
        self.defineData()
        self.replot()
        return
      if menuid == 303:
        if self.toggle_ND_Controller == 1:
          self.toggle_ND_Controller = 0
        else:
          self.toggle_ND_Controller = 1
        self.emit(PYSIGNAL("show_ND_Controller"),(self.toggle_ND_Controller,))
        return

# toggle flags display	
      if menuid == 200:
        if self.flag_toggle == False:
          self.flag_toggle = True
        else:
          self.flag_toggle = False
        if self.real_flag_vector is None:
          self.plotImage.setDisplayFlag(self.flag_toggle)
        else:
          self.curve(self.real_flag_vector).setEnabled(self.flag_toggle)
          if not self.imag_flag_vector is None:
            self.curve(self.imag_flag_vector).setEnabled(self.flag_toggle)
        self.replot()
        _dprint(3, 'called replot in update_vells_display')
	return

      if menuid == 201:
        if self.flag_blink == False:
          self.flag_blink = True
	  self.timer = QTimer(self)
          self.timer.connect(self.timer, SIGNAL('timeout()'), self.timerEvent_blink)
          self.timer.start(2000)
        else:
          self.flag_blink = False
	return

      id_string = self._next_plot[menuid]
      perturb = -1
      plane = 0
      perturb_loc = id_string.find("perturbed_value")
      str_len = len(id_string)
      if perturb_loc >= 0:
        perturb = int(id_string[perturb_loc+15:str_len])
      plane_loc = id_string.find("go to plane")
      if plane_loc >= 0:
        plane = int( id_string[plane_loc+12:plane_loc+14])
        self._active_plane = plane
        self._active_perturb = None
# do we have flags for data	  
	self._flags_array = None
        if self._vells_rec.vellsets[self._active_plane].has_key("flags"):
# test if we have a numarray
          try:
            self._flags_array = self._vells_rec.vellsets[self._active_plane].flags
            _dprint(3, 'self._flags_array ', self._flags_array)
            array_shape = self._flags_array.shape
            if len(array_shape) == 1 and array_shape[0] == 1:
              temp_value = self._flags_array[0]
              temp_array = asarray(temp_value)
              self._flags_array = resize(temp_array,self._shape)
          except:
            temp_array = asarray(self._vells_rec.vellsets[self._active_plane].flags)
            self._flags_array = resize(temp_array,self._shape)

          if self.array_tuple is None:
            self.setFlagsData(self._flags_array)
          else:
            self.setFlagsData(self._flags_array[self.array_tuple])

          self._toggle_flag_label = "toggle flagged data for plane " + str(plane) 
	  toggle_id = 200
          self._menu.changeItem(toggle_id,self._toggle_flag_label)
          self._menu.setItemEnabled(toggle_id, True)
          self._menu.setItemVisible(toggle_id, True)
          self._toggle_blink_label = "toggle blink of flagged data for plane " + str(plane)
          toggle_id = 201
          self._menu.changeItem(toggle_id,self._toggle_blink_label)
          self._menu.setItemEnabled(toggle_id, True)
          self._menu.setItemVisible(toggle_id, True)
        else:
	  toggle_id = 200
          self._menu.setItemEnabled(toggle_id, False)
          self._menu.setItemVisible(toggle_id, False)
          self.flag_toggle = False
          if not self.real_flag_vector is None:
            self.removeCurve(self.real_flag_vector)
            self.real_flag_vector = None
          if not self.imag_flag_vector is None:
            self.removeCurve(self.imag_flag_vector)
            self.imag_flag_vector = None
          toggle_id = 201
          self._menu.setItemEnabled(toggle_id, False)
          self._menu.setItemVisible(toggle_id, False)
          self.flag_blink = False
       
# get the shape tuple - useful if the Vells have been compressed down to
# a constant
      try:
        self._shape = self._vells_rec.vellsets[plane]["shape"]
      except:
        shape_list = []
        for i in range(len(self.axis_labels)):
          dimension = self.axis_shape[self.axis_labels[i]] 
          shape_list.append(dimension)
        self._shape = tuple(shape_list)
# handle "value" first
      if perturb < 0 and self._vells_rec.vellsets[plane].has_key("value"):
# test if we have a numarray
        self._value_array = self._vells_rec.vellsets[plane].value
        key = " value "
        if self.number_of_planes > 1:
          self._label =  "plane " + str(plane) + key 
        else:
          self._label =  "plane " + key 
        if self._solver_flag:
          self.array_plot(self._label, self._value_array, False)
        else:
          self.set_data_range(self._value_array)
          self.plot_vells_array(self._value_array)
      else:
# handle "perturbed_value"
        if self._vells_rec.vellsets[plane].has_key("perturbed_value"):
# test if we have a numarray
          perturbed_array_diff = None
          self._active_perturb = perturb
          perturbed_array_diff = self._vells_rec.vellsets[plane].perturbed_value[perturb]

          key = " perturbed_value "
          if self.number_of_planes > 1:
            self._label =  "plane " + str(plane) + key + str(perturb)
          else:
            self._label =  key + str(perturb)
          if self._solver_flag:
            self.array_plot(self._label, perturbed_array_diff, False)
          else:
            self.set_data_range(perturbed_array_diff)
            self.plot_vells_array(perturbed_array_diff)
        
    def printplot(self):
      self.emit(PYSIGNAL("do_print"),(self.is_vector,))
    # printplot()


    def drawCanvasItems(self, painter, rectangle, maps, filter):
        if not self.is_vector:
          self.plotImage.drawImage(
            painter, maps[QwtPlot.xBottom], maps[QwtPlot.yLeft])
        QwtPlot.drawCanvasItems(self, painter, rectangle, maps, filter)


    def formatCoordinates(self, x, y):
        """Format mouse coordinates as real world plot coordinates.
        """
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
	  if not self.y_marker_step is None:
	    if ypos1 >  self.y_marker_step:
	      marker_index = int(ypos1 / self.y_marker_step)
	      ypos1 = int(ypos1 % self.y_marker_step)
	    else:
	      marker_index = 0
          temp_str = result + " y =%+.2g" % ypos
          result = temp_str
        value = self.raw_image[xpos,ypos]
	message = None
        temp_str = " value: %-.3g" % value
	if not marker_index is None:
          message = result + temp_str + '\nsource: ' + self.marker_labels[marker_index]
	else:
          message = result + temp_str
    
# alias
        fn = self.fontInfo().family()

# text marker giving source of point that was clicked
        if not self.source_marker is None:
          self.removeMarker(self.source_marker)
        self.source_marker = self.insertMarker()
        ylb = self.axisScale(QwtPlot.yLeft).lBound()
        xlb = self.axisScale(QwtPlot.xBottom).lBound()
        self.setMarkerPos(self.source_marker, xlb, ylb)
        self.setMarkerLabelAlign(self.source_marker, Qt.AlignRight | Qt.AlignTop)
        self.setMarkerLabel( self.source_marker, message,
          QFont(fn, 7, QFont.Bold, False),
          Qt.blue, QPen(Qt.red, 2), QBrush(Qt.yellow))

# insert array info if available
        self.insert_array_info()
        self.replot()
        _dprint(3, 'called replot in formatCoordinates ')
            
    # formatCoordinates()

    def reportCoordinates(self, x, y):
        """Format mouse coordinates as real world plot coordinates.
        """
        result = ''
        xpos = x
        ypos = y
        temp_str = "nearest x=%-.3g" % x
        temp_str1 = " y=%-.3g" % y
	message = temp_str + temp_str1 
# alias
        fn = self.fontInfo().family()

# text marker giving source of point that was clicked
        if not self.source_marker is None:
          self.removeMarker(self.source_marker);
        self.source_marker = self.insertMarker()
        ylb = self.axisScale(QwtPlot.yLeft).lBound()
        xlb = self.axisScale(QwtPlot.xBottom).lBound()
        self.setMarkerPos(self.source_marker, xlb, ylb)
        self.setMarkerLabelAlign(self.source_marker, Qt.AlignRight | Qt.AlignTop)
        self.setMarkerLabel( self.source_marker, message,
          QFont(fn, 7, QFont.Bold, False),
          Qt.blue, QPen(Qt.red, 2), QBrush(Qt.yellow))

# insert array info if available
        self.insert_array_info()
        self.replot()
        _dprint(3, 'called replot in reportCoordinates ')
    # reportCoordinates()


    def refresh_marker_display(self):
      self.removeMarkers()
      self.info_marker = None
      self.source_marker = None
      if self.is_combined_image:
        self.insert_marker_lines()
      self.insert_array_info()
      self.replot()
      _dprint(3, 'called replot in refresh_marker_display ')
    # refresh_marker_display()

    def insert_marker_lines(self):
      _dprint(2, 'refresh_marker_display inserting markers')
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
       if self.is_vector:
          return

    # onMouseMoved()

    def onMousePressed(self, e):
        if Qt.LeftButton == e.button():
            if self.is_vector:
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
              self.reportCoordinates(xVal, yVal)

            else:
              self.formatCoordinates(e.pos().x(), e.pos().y())
            if self.zooming == 1:
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

        elif Qt.MidButton == e.button():
            if self.active_image:
              xpos = e.pos().x()
              ypos = e.pos().y()
              xpos = self.invTransform(QwtPlot.xBottom, xpos)
              ypos = self.invTransform(QwtPlot.yLeft, ypos)
              temp_array = asarray(ypos)
              shape = self.raw_image.shape
              self.x_arrayloc = resize(temp_array,shape[0])
              temp_array = asarray(xpos)
              self.y_arrayloc = resize(temp_array,shape[1])
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
#               xpos = self.plotImage.xMap.limTransform(xpos)
#               ypos = self.plotImage.yMap.limTransform(ypos)
              else:
                xpos = int(xpos)
                ypos = int(ypos)
              self.xsect_xpos = xpos
              self.xsect_ypos = ypos
              self.show_x_sections = True
              self.calculate_cross_sections()
              self.replot()
              _dprint(2, 'called replot in onMousePressed');
           
# fake a mouse move to show the cursor position
        self.onMouseMoved(e)

    # onMousePressed()

    def onMouseReleased(self, e):
        if Qt.LeftButton == e.button():
            self.refresh_marker_display()
            if self.zooming == 1:
              xmin = min(self.xpos, e.pos().x())
              xmax = max(self.xpos, e.pos().x())
              ymin = min(self.ypos, e.pos().y())
              ymax = max(self.ypos, e.pos().y())
              self.setOutlineStyle(Qwt.Cross)
              xmin = self.invTransform(QwtPlot.xBottom, xmin)
              xmax = self.invTransform(QwtPlot.xBottom, xmax)
              ymin = self.invTransform(QwtPlot.yLeft, ymin)
              ymax = self.invTransform(QwtPlot.yLeft, ymax)
            #print 'raw xmin xmax ymin ymax ', xmin, ' ', xmax, ' ', ymin, ' ', ymax
              if not self.is_vector:
# if we have a vells plot, adjust bounds of image display to be an integer
# number of pixels
                if self._vells_plot:
                  if not self.first_axis_inc is None:
                    xmin = int((xmin + 0.5 * self.first_axis_inc) / self.first_axis_inc)
                    xmax = int((xmax + 0.5 * self.first_axis_inc) / self.first_axis_inc)
                    xmin = xmin * self.first_axis_inc
                    xmax = xmax * self.first_axis_inc
                  if not self.second_axis_inc is None:
                    ymin = int((ymin + 0.5 * self.second_axis_inc) / self.second_axis_inc)
                    ymax = int((ymax + 0.5 * self.second_axis_inc) / self.second_axis_inc)
                    ymin = ymin * self.second_axis_inc
                    ymax = ymax * self.second_axis_inc
                else:
                    ymax = int (ymax)
                    ymin = int (ymin + 0.5)
                    xmax = int (xmax + 0.5)
                    xmin = int (xmin)
            #print 'final xmin xmax ymin ymax ', xmin, ' ', xmax, ' ', ymin, ' ', ymax
              if xmin == xmax or ymin == ymax:
                return
              self.zoomStack.append(self.zoomState)
              self.zoomState = (xmin, xmax, ymin, ymax)
              self.enableOutline(0)
        elif Qt.RightButton == e.button():
            if self.zooming == 1:
              if len(self.zoomStack):
                 xmin, xmax, ymin, ymax = self.zoomStack.pop()
              else:
                return
            else:
              return
        elif Qt.MidButton == e.button():
          return
        if self.zooming == 1:
          self.setAxisScale(QwtPlot.xBottom, xmin, xmax)
          self.setAxisScale(QwtPlot.yLeft, ymin, ymax)
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
        self.replot()
        _dprint(2, 'called replot in onMouseReleased');

    # onMouseReleased()


    def calculate_cross_sections(self):
        shape = self.raw_image.shape
        self.x_array = zeros(shape[0], Float32)
        self.x_index = arange(shape[0])
        self.x_index = self.x_index + 0.5
        for i in range(shape[0]):
          self.x_array[i] = self.raw_image[i,self.xsect_ypos]
        self.setAxisAutoScale(QwtPlot.yRight)
        self.y_array = zeros(shape[1], Float32)
        self.y_index = arange(shape[1])
        self.y_index = self.y_index + 0.5
        for i in range(shape[1]):
          self.y_array[i] = self.raw_image[self.xsect_xpos,i]
        self.setAxisAutoScale(QwtPlot.xTop)
        if self.xCrossSection is None:
          self.xCrossSection = self.insertCurve('xCrossSection')
          self.setCurvePen(self.xCrossSection, QPen(Qt.black, 2))
          plot_curve=self.curve(self.xCrossSection)
          plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, 
             QBrush(Qt.black), QPen(Qt.black), QSize(5,5)))
        self.enableAxis(QwtPlot.yRight)
        self.setAxisTitle(QwtPlot.yRight, 'x cross-section value')
        self.setCurveYAxis(self.xCrossSection, QwtPlot.yRight)
# nope!
#              self.setCurveStyle(self.xCrossSection, QwtCurve.Steps)
        if self.yCrossSection is None:
          self.yCrossSection = self.insertCurve('yCrossSection')
          self.setCurvePen(self.yCrossSection, QPen(Qt.white, 2))
          plot_curve=self.curve(self.yCrossSection)
          plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, 
             QBrush(Qt.white), QPen(Qt.white), QSize(5,5)))
        self.enableAxis(QwtPlot.xTop)
        self.setAxisTitle(QwtPlot.xTop, 'y cross-section value')
        self.setCurveYAxis(self.yCrossSection, QwtPlot.yLeft)
        self.setCurveXAxis(self.yCrossSection, QwtPlot.xTop)
#        self.setAxisOptions(QwtPlot.xTop,QwtAutoScale.Inverted)
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
        self.setCurveData(self.xCrossSection, self.x_index, self.x_array)
        self.setCurveData(self.yCrossSection, self.y_array, self.y_index)

# put in a line where cross sections are selected
        if self.xCrossSectionLoc is None:
          self.xCrossSectionLoc = self.insertCurve('xCrossSectionLocation')
          self.setCurvePen(self.xCrossSectionLoc, QPen(Qt.black, 2))
          self.setCurveYAxis(self.xCrossSectionLoc, QwtPlot.yLeft)
        self.setCurveData(self.xCrossSectionLoc, self.x_index, self.x_arrayloc)
        if self.yCrossSectionLoc is None:
          self.yCrossSectionLoc = self.insertCurve('yCrossSectionLocation')
          self.setCurvePen(self.yCrossSectionLoc, QPen(Qt.white, 2))
          self.setCurveYAxis(self.yCrossSectionLoc, QwtPlot.yLeft)
          self.setCurveXAxis(self.yCrossSectionLoc, QwtPlot.xBottom)
        self.setCurveData(self.yCrossSectionLoc, self.y_arrayloc, self.y_index)
        if self.is_combined_image:
          self.removeMarkers()
          self.info_marker = None
          self.source_marker = None
          self.insert_marker_lines()
        self.show_x_sections = True
        toggle_id = 305
        self._menu.setItemVisible(toggle_id, True)

    def toggleCurve(self, key):
      curve = self.curve(key)
      if curve:
        curve.setEnabled(not curve.enabled())
        self.replot()
        _dprint(2, 'called replot in toggleCurve');
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
      image_for_display = None
      if image.type() == Complex32 or image.type() == Complex64:
# if incoming array is complex, create array of reals followed by imaginaries
        real_array =  image.getreal()
        imag_array =  image.getimag()
        shape = real_array.shape
        image_for_display = zeros((2*shape[0],shape[1]), Float32)
        for k in range(shape[0]):
          for j in range(shape[1]):
            image_for_display[k,j] = real_array[k,j]
            image_for_display[k+shape[0],j] = imag_array[k,j]


      else:
        image_for_display = image
      if self.image_min is None or  self.adjust_color_bar:
        self.image_min = image_for_display.min()
      if self.image_max is None or  self.adjust_color_bar:
        self.image_max = image_for_display.max()

# have we requested a colorbar?
      if not self.colorbar_requested:
        #print 'emitting colorbar_needed signal'
        self.emit(PYSIGNAL("colorbar_needed"),(image_for_display.min(),image_for_display.max()))
        self.colorbar_requested = True
      
      # emit range for the color bar
      if self.adjust_color_bar:
        # just in case we have a uniform image
        # not yet sure if the following is the best test ...
        if abs(image_for_display.max() - image_for_display.min()) < 0.00005:
          if image_for_display.max() == 0 or image_for_display.min() == 0.0:
            image_min = -0.1
            image_max = 0.1 
          else:
            image_min = 0.9 * image_for_display.min()
            image_max = 1.1 * image_for_display.max()
          if image_min > image_max:
            temp = image_min
            image_min = image_max
            image_max = temp
          self.plotImage.setImageRange((image_min, image_max))
          self.emit(PYSIGNAL("max_image_range"),(image_min, image_max))
          #print 'display_image emitted max_image_range ', image_min, ' ', image_max
        else:
          self.plotImage.setImageRange((image_for_display.min(), image_for_display.max()))
          self.emit(PYSIGNAL("max_image_range"),(image_for_display.min(), image_for_display.max()))
          #print 'display_image emitted max_image_range ', image_for_display.min(), ' ', image_for_display.max()

        if abs(self.image_max - self.image_min) < 0.00005:
          if self.image_max == 0 or self.image_min == 0.0:
            image_min = -0.1
            image_max = 0.1 
          else:
            image_min = 0.9 * self.image_min
            image_max = 1.1 * self.image_max
          if image_min > image_max:
            temp = image_min
            image_min = image_max
            image_max = temp
          self.plotImage.setImageRange((image_min,image_max))
          self.emit(PYSIGNAL("image_range"),(image_min, image_max))
          #print 'display_image emitted image_range ', image_min, ' ', image_max
        else:
          self.plotImage.setImageRange((self.image_min,self.image_max))
          self.emit(PYSIGNAL("image_range"),(self.image_min, self.image_max))
          #print 'display_image emitted image_range ', self.image_min, ' ', self.image_max
        self.adjust_color_bar = False

      self.raw_image = image_for_display
      if self.image_shape is None:
        self.image_shape = self.raw_image.shape 
      else:
        if not self.image_shape == self.raw_image.shape:
          self.delete_cross_sections()
          self.image_shape = self.raw_image.shape 

      self.defineData()

      if self.is_combined_image:
         _dprint(2, 'display_image inserting markers')
         self.removeMarkers()
         self.info_marker = None
         self.source_marker = None
	 self.insert_marker_lines()
      self.insert_array_info()

# add solver metrics info?
      if not self.metrics_rank is None:
        self.metrics_plot = self.insertCurve('metrics')
        self.setCurvePen(self.metrics_plot, QPen(Qt.black, 2))
        self.setCurveStyle(self.metrics_plot,Qt.SolidLine)
        self.setCurveYAxis(self.metrics_plot, QwtPlot.yLeft)
        self.setCurveXAxis(self.metrics_plot, QwtPlot.xBottom)
        plot_curve=self.curve(self.metrics_plot)
        plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.black),
                   QPen(Qt.black), QSize(10,10)))
        self.setCurveData(self.metrics_plot, self.metrics_rank, self.iteration_number)
      if self.show_x_sections:
        self.calculate_cross_sections()
      self.replot()
      _dprint(2, 'called replot in display_image');
    # display_image()

    def insert_array_info(self):
# insert mean and standard deviation
      if not self.array_parms is None:
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
        self.setMarkerLabel( self.info_marker, self.array_parms,
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
              self.setTitle(self.label+self._window_title)
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

      if visu_record.has_key('label'):
        self._data_labels = visu_record['label']
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
      if  self._plot_type == 'spectra':
# ensure that menu for display is updated if required
        self.initSpectrumContextMenu()
# plot first instance of array
        if not self.active_image_index is None:
          if self.active_image_index == self._combined_image_id:
	    self.is_combined_image = True
            self.reset_color_bar(True)
          self.array_plot(self._plot_label[self.active_image_index], self._plot_dict[self.active_image_index],False)
          if self.is_combined_image:
	    self.is_combined_image = True
            self.removeMarkers()
            self.info_marker = None
            self.source_marker = None
	    self.insert_marker_lines()
        elif not self._combined_image_id is None:
	  self.is_combined_image = True
          self.reset_color_bar(True)
          self.array_plot(self._plot_label[ self._combined_image_id], self._plot_dict[ self._combined_image_id],False)
          self.removeMarkers()
          self.info_marker = None
          self.source_marker = None
          self.insert_marker_lines()
	else:
          if not self._plot_dict_size is None:
            data_label = ''
            if isinstance(self._data_labels, tuple):
              data_label = 'spectra:' + self._string_tag +  " " +self._data_labels[0]
            else:
              data_label = 'spectra:' + self._string_tag +  " " +self._data_labels
            _dprint(3, 'plotting array with label ', data_label)
            self.array_plot(data_label, self._data_values[0])
      _dprint(2, 'exiting plot_data');

    # end plot_data()

    def calc_vells_ranges(self):
      """ get vells data ranges for use 
          with other functions """
                                                                                
      self.do_calc_vells_range = False
      axis_map = self._vells_rec.cells.domain.get('axis_map',['time','freq'])
      self.axis_labels = []
      self.vells_axis_parms = {}
      self.axis_shape = {}
      num_possible_ND_axes = 0
      for i in range(len(axis_map)):
        # convert from Hiid to string
        self.axis_labels.append(str(axis_map[i]).lower())
        current_label = self.axis_labels[i]
        begin = 0
        end = 0
        title = current_label
        if self._vells_rec.cells.domain.has_key(current_label):
          begin = self._vells_rec.cells.domain.get(current_label)[0]
	  end = self._vells_rec.cells.domain.get(current_label)[1]
          title = current_label
          if current_label == 'time':
            end = end - begin
            begin = 0
            title = 'Relative Time(sec)'
          if current_label == 'freq':
            if end >  1.0e6:
              begin = begin / 1.0e6
              end = end / 1.0e6
              title = 'Frequency(MHz)'
              self._mhz = True
            elif end >  1.0e3:
              begin = begin / 1.0e3
              end = end / 1.0e3
              title = 'Frequency(KHz)'
              self._khz = True
            else:
              title = 'Frequency(Hz)'
        if self._vells_rec.cells.grid.has_key(current_label):
          grid_array = self._vells_rec.cells.grid.get(current_label)
          _dprint(3, 'in calc_vells_ranges: examining cells.grid for label ', current_label)
          _dprint(3, 'in calc_vells_ranges: grid_array is ', grid_array)
          try:
            self.axis_shape[current_label] = grid_array.shape[0]
            _dprint(3, 'in calc_vells_ranges: grid_array shape is ', grid_array.shape)
            num_possible_ND_axes = num_possible_ND_axes + 1
            _dprint(3, 'in calc_vells_ranges: incrementing ND axes to ', num_possible_ND_axes)
          except:
            self.axis_shape[current_label] = 1
        else:
          self.axis_shape[current_label] = 1
        self.vells_axis_parms[current_label] = (begin, end, title, self.axis_shape[current_label])

      # do we request a ND GUI?
      if not self.dimensions_tested:
        if len(self.vells_axis_parms) > 2 and num_possible_ND_axes > 2:
          _dprint(3, '** in calc_vells_ranges:')
          _dprint(3, 'I think I need a ND GUI as number of valid plot axes is ',num_possible_ND_axes)
          _dprint(3, 'length of self.vells_axis_parms is ', len(self.vells_axis_parms))
          _dprint(3, 'self.vells_axis_parms is ', self.vells_axis_parms)
          _dprint(3, 'I am emitting a vells_axes_labels signal which will cause the ND GUI to be constructed')
          # emitting the following signal will cause the ND Controller GUI  
          # to be constructed 
          self.emit(PYSIGNAL("vells_axes_labels"),(self.axis_labels, self.vells_axis_parms))
        self.dimensions_tested = True

# set default axis parameters - needed in a simple 2-D plot
      self.first_axis_parm = self.axis_labels[0]
      self.second_axis_parm = self.axis_labels[1]

      _dprint(3, 'self.vells_axis_parms is ', self.vells_axis_parms)

    # calc-vells_ranges

    def plot_vells_data (self, vells_record,label=''):
      """ process incoming vells data and attributes into the
          appropriate type of plot """

      _dprint(2, 'in plot_vells_data');
      self.metrics_rank = None
      self._vells_rec = vells_record;
# if we are single stepping through requests, Oleg may reset the
# cache, so check for a non-data record situation
      if isinstance(self._vells_rec, bool):
        return

# are we dealing with 'solver' results?
      if self._vells_rec.has_key("solver_result"):
        if self._vells_rec.solver_result.has_key("incremental_solutions"):
          self._solver_flag = True
          self._value_array = self._vells_rec.solver_result.incremental_solutions
          if self._vells_rec.solver_result.has_key("metrics"):
            metrics = self._vells_rec.solver_result.metrics
            self.metrics_rank = zeros(len(metrics), Int32)
            self.iteration_number = zeros(len(metrics), Int32)
            for i in range(len(metrics)):
               self.metrics_rank[i] = metrics[i].rank
               self.iteration_number[i] = i+1
          shape = self._value_array.shape
          if shape[1] > 1:
            self._x_title = 'Solvable Coeffs'
            self._y_title = 'Iteration Nr'
            self.array_plot("Solver Incremental Solutions", self._value_array, True)
          else:
            self._y_title = 'Value'
            self._x_title = 'Iteration Nr'
            self.array_plot("Solver Incremental Solution", self._value_array, True)

# are we dealing with Vellsets?
      if self._vells_rec.has_key("vellsets") and not self._solver_flag:
        self._vells_plot = True
#       if self.do_calc_vells_range:
        self.calc_vells_ranges()
        _dprint(3, 'handling vellsets')


# how many VellSet planes (e.g. I, Q, U, V would each be a plane) are there?
        if self._active_plane is None:
          self._active_plane = 0
        self.number_of_planes = len(self._vells_rec["vellsets"])
        _dprint(3, 'number of planes ', self.number_of_planes)
        if self._vells_rec.vellsets[self._active_plane].has_key("shape"):
          self._shape = self._vells_rec.vellsets[self._active_plane]["shape"]

# do we have flags for data	  
	self._flags_array = None
        if self._vells_rec.vellsets[self._active_plane].has_key("flags"):
# test if we have a numarray
          try:
            self._flags_array = self._vells_rec.vellsets[self._active_plane].flags
            _dprint(3, 'self._flags_array ', self._flags_array)
            array_shape = self._flags_array.shape
            if len(array_shape) == 1 and array_shape[0] == 1:
              temp_value = self._flags_array[0]
              temp_array = asarray(temp_value)
              self._flags_array = resize(temp_array,self._shape)
          except:
            temp_array = asarray(self._vells_rec.vellsets[self._active_plane].flags)
            self._flags_array = resize(temp_array,self._shape)

          if self.array_tuple is None:
            self.setFlagsData(self._flags_array)
          else:
            self.setFlagsData(self._flags_array[self.array_tuple])


	
# plot the appropriate plane / perturbed value
        if not self._active_perturb is None:
          self._value_array = self._vells_rec.vellsets[self._active_plane].perturbed_value[self._active_perturb]
        else:
          if self._vells_rec.vellsets[self._active_plane].has_key("value"):
            self._value_array = self._vells_rec.vellsets[self._active_plane].value
        key = ""
        if self._active_perturb is None:
          key = " main value "
          if self.number_of_planes > 1:
            self._label =  label + " plane " + str(self._active_plane) + key 
          else:
            self._label =  label + key 
        else:
          key = " perturbed_value "
          if self.number_of_planes > 1:
            self._label =  label + "plane " + str(self._active_plane) + key + str(self._active_perturb)
          else:
            self._label =  label + key + str(self._active_perturb)
        if self._solver_flag:
          self.array_plot(self._label, self._value_array, flip_axes=False)
        else:
          if self._vells_plot:
            if self.context_menu_done is None:
               self.initVellsContextMenu()
            self.set_data_range(self._value_array)
            self.plot_vells_array(self._value_array)

    # end plot_vells_data()

    def set_data_range(self, data_array):
# make sure we're dealing with an array
      try:
        array_shape = data_array.shape
      except:
        temp_array = asarray(data_array)
        shape = (1,1)
        data_array = resize(temp_array,shape)

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

      # just in case we have a uniform image
      # not yet sure if the following is the best test ...
      if abs(self.data_max - self.data_min) < 0.00005:
        if self.data_min == 0 or self.data_min == 0.0:
          self.data_min = -0.1
          self.data_max = 0.1 
        else:
          self.data_min = 0.9 * self.data_min
          self.data_max = 1.1 * self.data_max
        if self.data_min > self.data_max:
          temp = self.data_min
          self.data_min = self.data_max
          self.data_max = temp

      #print 'set_data_range: image range being set to : ', self.data_min, ' ', self.data_max
      self.plotImage.setImageRange((self.data_min,self.data_max))
      self.reset_color_bar(reset_value = False)
# have we requested a colorbar?
      if not self.colorbar_requested:
        #print 'emitting colorbar_needed signal'
        self.emit(PYSIGNAL("colorbar_needed"),(self.data_min, self.data_max))
        self.colorbar_requested = True
      
      self.emit(PYSIGNAL("max_image_range"),(self.data_min, self.data_max))
      self.emit(PYSIGNAL("image_range"),(self.data_min, self.data_max))
      #print 'set_data_range: should have emitted max_image_range and image_range signals of ', self.data_min, ' ', self.data_max

    def setArraySelector (self,lcd_number, slider_value, display_string):
#     #print 'in setArraySelector lcd_number, slider_value ', lcd_number, slider_value
      if self.array_selector is None or len(self.array_selector) == 0:
        if self._vells_plot:
          plot_array = self.check_dimensions(self._value_array)
          self.array_plot('data: '+ display_string, plot_array)
        else:
          self.array_plot('data: '+ display_string, self._value_array)
          
      else:
#       #print 'array selector ', self.array_selector
        self.array_selector[lcd_number] = slider_value
        self.array_tuple = tuple(self.array_selector)
        if self._vells_plot:
          plot_array = self.check_dimensions(self._value_array[self.array_tuple])
          self.array_plot('data: '+ display_string, plot_array)
        else:
          self.array_plot('data: '+ display_string, self._value_array[self.array_tuple])

    def plot_vells_array (self, data_array):
      self.array_shape = None
      self.array_rank = data_array.rank
      if data_array.rank > 2: 
        self.array_shape =  data_array.shape
        if self.array_selector is None or len(self.array_selector) == 0:
          self.array_selector = []
          self.first_axis = None
          self.second_axis = None
          for i in range(data_array.rank-1,-1,-1):
            if data_array.shape[i] > 1:
              if self.second_axis is None:
                self.second_axis = i
              else:
                if self.first_axis is None:
                  self.first_axis = i
          if not self.first_axis is None and not self.second_axis is None:
            for i in range(data_array.rank):
              if i == self.first_axis:
                axis_slice = slice(0,data_array.shape[self.first_axis])
                self.array_selector.append(axis_slice)
                first_plot_dimension = self.vells_axis_parms[self.axis_labels[i]][3]
              elif i == self.second_axis:
                axis_slice = slice(0,data_array.shape[self.second_axis])
                self.array_selector.append(axis_slice)
                second_plot_dimension = self.vells_axis_parms[self.axis_labels[i]][3]
              else:
                self.array_selector.append(0)
            self.emit(PYSIGNAL("reset_axes_labels"),(self.axis_labels, self.vells_axis_parms))
          else:
            first_plot_dimension = self.vells_axis_parms[self.axis_labels[self.first_axis]][3]
            second_plot_dimension = self.vells_axis_parms[self.axis_labels[self.second_axis]][3]
        else:
          first_plot_dimension = self.vells_axis_parms[self.axis_labels[self.first_axis]][3]
          second_plot_dimension = self.vells_axis_parms[self.axis_labels[self.second_axis]][3]
#       print 'plot_vells_array: self.array_selector is ', self.array_selector
        self.array_tuple = tuple(self.array_selector)
        self.first_axis_parm = self.axis_labels[self.first_axis]
        self.second_axis_parm = self.axis_labels[self.second_axis]
        self.plot_vells_dimensions = (first_plot_dimension, second_plot_dimension)
        plot_array = self.check_dimensions(data_array[self.array_tuple])
        self.array_plot(self._label, plot_array)
          
      else:
        if len(self.axis_labels) > 2:
          self.array_selector = None
          self.second_axis = None
          self.first_axis = None
          first_plot_dimension = 1
          second_plot_dimension = 1
          for i in range(len(self.axis_labels)-1,-1,-1):
           if self.vells_axis_parms[self.axis_labels[i]][3] > 1:
             if self.second_axis is None:
               self.second_axis = i
               second_plot_dimension = self.vells_axis_parms[self.axis_labels[self.second_axis]][3]
               self.second_axis_parm = self.axis_labels[self.second_axis]
             else:
               if self.first_axis is None:
                 self.first_axis = i
                 first_plot_dimension = self.vells_axis_parms[self.axis_labels[self.first_axis]][3]
                 self.first_axis_parm = self.axis_labels[self.first_axis]
        else:
          first_plot_dimension = self.vells_axis_parms[self.axis_labels[0]][3]
          second_plot_dimension = self.vells_axis_parms[self.axis_labels[1]][3]
          self.first_axis_parm = self.axis_labels[0]
          self.second_axis_parm = self.axis_labels[1]
        self.plot_vells_dimensions = (first_plot_dimension, second_plot_dimension)
        plot_array = self.check_dimensions(data_array)
        self.array_plot(self._label, plot_array)

 
    def check_dimensions(self,data_array):
      try:
        shape = data_array.shape
      except:
# we have a scalar - expand the scalar to fill the grid
        temp_array = asarray(data_array)
        new_array = resize(temp_array,self.plot_vells_dimensions)
        return new_array
      if len(shape) == 1:
        if shape[0] == 1:
# we essentially have a scalar
          temp_array = asarray(data_array)
          new_array = resize(temp_array,self.plot_vells_dimensions)
          return new_array
        else:
# we can assume we have a conformant array along the first axis (I think)
          temp_array = asarray(data_array)
          new_array = resize(temp_array,self.plot_vells_dimensions)
          for i in range(self.plot_vells_dimensions[0]):
            for j in range(self.plot_vells_dimensions[1]):
              new_array[i,j] = data_array[i,0]
          return new_array
# otherwise we had a 2-D shape
      else:
# simplest case: incoming array has dimensions of vell
        if shape[0] == self.plot_vells_dimensions[0] and shape[1] ==  self.plot_vells_dimensions[1]:
          return data_array
        if shape[0] == 1 and shape[1] == 1:
# we essentially have a scalar
          temp_array = asarray(data_array)
          new_array = resize(temp_array,self.plot_vells_dimensions)
          return new_array
# we need to expand the data to fill the vells dimension
# easy if fastest changing index == shape of vector which will
# be replicated
        if shape[0] == 1 and shape[1] ==  self.plot_vells_dimensions[1]:
          new_array = resize(data_array,self.plot_vells_dimensions)
        else:
# otherwise
          temp_array = asarray(data_array[0,0])
          new_array = resize(temp_array,self.plot_vells_dimensions)
          for i in range(self.plot_vells_dimensions[0]):
            for j in range(self.plot_vells_dimensions[1]):
              new_array[i,j] = data_array[i,0]
        return new_array

    def setSelectedAxes (self,first_axis, second_axis):
      self.delete_cross_sections()
      if self._vells_plot:
        self.first_axis = first_axis
        self.second_axis = second_axis
        self.first_axis_parm = self.axis_labels[first_axis]
        self.second_axis_parm = self.axis_labels[second_axis]
        first_plot_dimension = self.vells_axis_parms[self.axis_labels[first_axis]][3]
        second_plot_dimension = self.vells_axis_parms[self.axis_labels[second_axis]][3]
        self.plot_vells_dimensions = (first_plot_dimension, second_plot_dimension)
      if not self.array_shape is None: 
        self.array_selector = []
        for i in range(len(self.array_shape)):
          if i == first_axis:
            axis_slice = slice(0,self.array_shape[first_axis])
            self.array_selector.append(axis_slice)
          elif i == second_axis:
            axis_slice = slice(0,self.array_shape[second_axis])
            self.array_selector.append(axis_slice)
          else:
            self.array_selector.append(0)
        self.array_tuple = tuple(self.array_selector)
        if self._vells_plot:
          if self._value_array.rank > 2:
            plot_array = self.check_dimensions(self._value_array[self.array_tuple])
          else:
            plot_array = self.check_dimensions(self._value_array)
          self.array_plot(self._label, plot_array)
        else:
          self.array_plot(self._label, self._value_array[self.array_tuple])
      else:
        if self._vells_plot:
          plot_array = self.check_dimensions(self._value_array)
          self.array_plot(self._label, plot_array)
        else:
          self.array_plot(self._label, self._value_array)

    def handle_finished (self):
      print 'in handle_finished'

    def reset_color_bar(self, reset_value=True):
      self.adjust_color_bar = reset_value
#     print 'self.adjust_color_bar = ', self.adjust_color_bar

    def array_plot (self, data_label, incoming_plot_array, flip_axes=True):
      """ figure out shape, rank etc of a spectrum array and
          plot it  """

# delete any previous curves
      self.removeCurves()
      self.xCrossSection = None
      self.yCrossSection = None
      self.enableAxis(QwtPlot.yLeft, False)
      self.enableAxis(QwtPlot.xBottom, False)
      self.enableAxis(QwtPlot.yRight, False)
      self.enableAxis(QwtPlot.xTop, False)
      self.xCrossSectionLoc = None
      self.yCrossSectionLoc = None
      self.dummy_xCrossSection = None
      self.myXScale = None
      self.myYScale = None
      self.split_axis = None
      self.array_parms = None

# pop up menu for printing
      if self._menu is None:
        self._menu = QPopupMenu(self._mainwin);
        self.add_basic_menu_items()
        QObject.connect(self._menu,SIGNAL("activated(int)"),self.update_spectrum_display);


# set title
      self._window_title = data_label  
      self.setTitle(self.label+self._window_title)

# hack to get array display correct until forest.state
# record is available
      plot_array = incoming_plot_array
      axes = None
      if flip_axes:
        axes = arange(incoming_plot_array.rank)[::-1]
        plot_array = transpose(incoming_plot_array, axes)

# figure out type and rank of incoming array
# for vectors, this is a pain as e.g. (8,) and (8,1) have
# different 'formal' ranks but really are the same 1-D vectors
# I'm not sure that the following covers all bases, but we are getting close
      self.is_vector = False;
      actual_array_rank = 0
      second_is_first_axis = False
      num_elements = 1
      for i in range(len(plot_array.shape)):
        num_elements = num_elements * plot_array.shape[i]
        if plot_array.shape[i] > 1:
          actual_array_rank = actual_array_rank + 1
      if actual_array_rank == 1:
        self.is_vector = True;
# check if grid frequency/time layout gives extra info
        if len(plot_array.shape) > 1:
          if flip_axes and plot_array.shape[1] == 1:
            second_is_first_axis = True


# test for real or complex
      complex_type = False;
      if plot_array.type() == Complex32:
        complex_type = True;
      if plot_array.type() == Complex64:
        complex_type = True;
      self.complex_type = complex_type

# test if we have a 2-D array
      if self.is_vector == False:
        self.enableAxis(QwtPlot.yLeft)
        self.enableAxis(QwtPlot.xBottom)
# if there are flags associated with this array, we need to copy flags for complex array
        if self.complex_type and not self._flags_array is None:
          if self.array_tuple is None:
            temp_array = self._flags_array
          else:
            temp_array= self._flags_array[self.array_tuple]
          if flip_axes:
            flipped_temp_array = transpose(temp_array, axes)
            temp_array = flipped_temp_array
          flag_shape = temp_array.shape
          flag_array = zeros((2*flag_shape[0],flag_shape[1]), temp_array.type())
          for k in range(flag_shape[0]):
            for j in range(flag_shape[1]):
              flag_array[k,j] = temp_array[k,j]
              flag_array[k+flag_shape[0],j] = temp_array[k,j]
          flags_flip = True
          if flip_axes:
            flags_flip = False
          self.setFlagsData(flag_array, flags_flip)

# don't use grid markings for 2-D 'image' arrays
        self.enableGridX(False)
        self.enableGridY(False)

# make sure color bar is shown
#       self.emit(PYSIGNAL("show_colorbar_display"),(1,)) 
# make sure options relating to color bar are in context menu
        toggle_id = 301
        self._menu.setItemVisible(toggle_id, True)
        toggle_id = 302
        self._menu.setItemVisible(toggle_id, True)

        self.active_image = True

# get mean and standard deviation of array
        temp_str = ""
        if complex_type:
          if plot_array.mean().imag < 0:
            temp_str = "m: %-.3g %-.3gj" % (plot_array.mean().real,plot_array.mean().imag)
          else:
            temp_str = "m: %-.3g+ %-.3gj" % (plot_array.mean().real,plot_array.mean().imag)
        else:
          temp_str = "m: %-.3g" % plot_array.mean()
        temp_str1 = "sd: %-.3g" % standard_deviation(plot_array,complex_type )
        self.array_parms = temp_str + " " + temp_str1

        self.setAxisTitle(QwtPlot.yLeft, 'sequence')
        if complex_type and self._display_type != "brentjens":
          if self._vells_plot:
            self.x_parm = self.first_axis_parm
            self.y_parm = self.second_axis_parm
            if flip_axes:
              self.x_parm = self.second_axis_parm
              self.y_parm = self.first_axis_parm
            self.myXScale = ComplexScaleSeparate(self.vells_axis_parms[self.x_parm][0], self.vells_axis_parms[self.x_parm][1])
            self.setAxisScaleDraw(QwtPlot.xBottom, self.myXScale)
            self.split_axis = self.vells_axis_parms[self.x_parm][1] 
            delta_vells = self.vells_axis_parms[self.x_parm][1] - self.vells_axis_parms[self.x_parm][0]
            self.delta_vells = delta_vells
            self.first_axis_inc = delta_vells / plot_array.shape[0] 
            delta_vells = self.vells_axis_parms[self.y_parm][1] - self.vells_axis_parms[self.y_parm][0]
            self.second_axis_inc = delta_vells / plot_array.shape[1] 
            title_addition = ': (real followed by imaginary)'
            self._x_title = self.vells_axis_parms[self.x_parm][2] + title_addition
            self.setAxisTitle(QwtPlot.xBottom, self._x_title)
            self._y_title = self.vells_axis_parms[self.y_parm][2]
            self.setAxisTitle(QwtPlot.yLeft, self._y_title)
          else:
            self._x_title = 'Array/Channel Number (real followed by imaginary)'
            self.setAxisTitle(QwtPlot.xBottom, self._x_title)
            self._y_title = 'Array/Sequence Number'
            self.setAxisTitle(QwtPlot.yLeft, self._y_title)
            self.myXScale = ComplexScaleDraw(plot_array.shape[0])
            self.setAxisScaleDraw(QwtPlot.xBottom, self.myXScale)
	    self.split_axis = plot_array.shape[0]
	    if not self.y_marker_step is None:
              self.myYScale = ComplexScaleDraw(self.y_marker_step)
              self.setAxisScaleDraw(QwtPlot.yLeft, self.myYScale)

          self.display_image(plot_array)

        else:
          if self._vells_plot:
            self.x_parm = self.first_axis_parm
            self.y_parm = self.second_axis_parm
            if flip_axes:
              self.x_parm = self.second_axis_parm
              self.y_parm = self.first_axis_parm
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
            self._x_title = 'Array/Channel Number'
            self.setAxisTitle(QwtPlot.xBottom, self._x_title)
            self._y_title = 'Array/Sequence Number'
            self.setAxisTitle(QwtPlot.yLeft, self._y_title)
          self.display_image(plot_array)

      if self.is_vector == True:

# make sure color bar is hidden
        self.emit(PYSIGNAL("show_colorbar_display"),(0,)) 
# make sure options relating to color bar are not in context menu
        toggle_id = 301
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = 302
        self._menu.setItemVisible(toggle_id, False)

# make sure we are autoscaling in case an image was previous
        self.setAxisAutoScale(QwtPlot.xBottom)
        self.setAxisAutoScale(QwtPlot.xTop)
        self.setAxisAutoScale(QwtPlot.yLeft)
        self.setAxisAutoScale(QwtPlot.yRight)
#       self.setAxisScaleDraw(QwtPlot.xBottom, None)
#       self.setAxisScaleDraw(QwtPlot.yLeft, None)
        self._x_auto_scale = True
        self._y_auto_scale = True

# make sure grid markings are on in case an image was previously displayed
        self.enableGridX(True)
        self.enableGridY(True)

        if not self._flags_array is None:
          self.flags_x_index = []
          self.flags_r_values = []
          self.flags_i_values = []
        self.active_image = False


        if self._vells_plot:
          self.x_parm = self.first_axis_parm
          self.y_parm = self.second_axis_parm
          if flip_axes:
            self.x_parm = self.second_axis_parm
            self.y_parm = self.first_axis_parm
          delta_vells = self.vells_axis_parms[self.x_parm][1] - self.vells_axis_parms[self.x_parm][0]
          x_step = delta_vells / num_elements 
          start_x = self.vells_axis_parms[self.x_parm][0] + 0.5 * x_step
          self.x_index = zeros(num_elements, Float32)
          for j in range(num_elements):
            self.x_index[j] = start_x + j * x_step
          self._x_title = self.vells_axis_parms[self.x_parm][2]
          self.setAxisTitle(QwtPlot.xBottom, self._x_title)
        else:
          self._x_title = 'Array/Channel Number'
          self.setAxisTitle(QwtPlot.xBottom, self._x_title)
          self.x_index = arange(num_elements)
          self.x_index = self.x_index + 0.5
# if we are plotting a single iteration solver solution
# plot on 'locations' of solver parameters. Use 'self.metrics_rank'
# as test, but don't plot metrics in this case
          if not self.metrics_rank is None:
            self.x_index = self.x_index + 0.5
        flattened_array = reshape(plot_array,(num_elements,))
        if not self._flags_array is None:
          if complex_type:
            x_array =  flattened_array.getreal()
            y_array =  flattened_array.getimag()
            for j in range(num_elements):
              if self._flags_array[j] > 0:
                self.flags_x_index.append(self.x_index[j])
                self.flags_r_values.append(x_array[j])
                self.flags_i_values.append(y_array[j])
          else:
            for j in range(num_elements):
              if self._flags_array[j] > 0:
                self.flags_x_index.append(self.x_index[j])
                self.flags_r_values.append(flattened_array[j])
# we have a complex vector
        if complex_type:
          self.enableAxis(QwtPlot.yRight)
          self.enableAxis(QwtPlot.yLeft)
          self.enableAxis(QwtPlot.xBottom)
          self.enableAxis(QwtPlot.xTop)
          self.setAxisTitle(QwtPlot.yLeft, 'Value: real (black line / red dots)')
          self.setAxisTitle(QwtPlot.yRight, 'Value: imaginary (blue line / green dots)')
          self.xCrossSection = self.insertCurve('xCrossSection')
          self.yCrossSection = self.insertCurve('yCrossSection')
          self.setCurvePen(self.xCrossSection, QPen(Qt.black, 2))
          self.setCurvePen(self.yCrossSection, QPen(Qt.blue, 2))
          self.setCurveYAxis(self.xCrossSection, QwtPlot.yLeft)
          self.setCurveYAxis(self.yCrossSection, QwtPlot.yRight)
          plot_curve=self.curve(self.xCrossSection)
          plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.red),
                     QPen(Qt.red), QSize(5,5)))
          plot_curve=self.curve(self.yCrossSection)
          plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.green),
                     QPen(Qt.green), QSize(5,5)))
          self.x_array =  flattened_array.getreal()
          self.y_array =  flattened_array.getimag()
          self.setCurveData(self.xCrossSection, self.x_index, self.x_array)
          self.setCurveData(self.yCrossSection, self.x_index, self.y_array)
          if not self.dummy_xCrossSection is None:
            self.removeCurve(self.dummy_xCrossSection)
            self.dummy_xCrossSection = None

# stuff for flags
          if not self._flags_array is None:
            self.real_flag_vector = self.insertCurve('real_flags')
            self.setCurvePen(self.real_flag_vector, QPen(Qt.black))
            self.setCurveStyle(self.real_flag_vector, QwtCurve.Dots)
            self.setCurveYAxis(self.real_flag_vector, QwtPlot.yLeft)
            plot_flag_curve = self.curve(self.real_flag_vector)
            plot_flag_curve.setSymbol(QwtSymbol(QwtSymbol.XCross, QBrush(Qt.black),
                     QPen(Qt.black), QSize(20, 20)))
            self.setCurveData(self.real_flag_vector, self.flags_x_index, self.flags_r_values)
# Note: We don't show the flag data in the initial display
# but toggle it on or off (ditto for imaginary data flags).
            self.curve(self.real_flag_vector).setEnabled(False)
            self.imag_flag_vector = self.insertCurve('imag_flags')
            self.setCurvePen(self.imag_flag_vector, QPen(Qt.black))
            self.setCurveStyle(self.imag_flag_vector, QwtCurve.Dots)
            self.setCurveYAxis(self.imag_flag_vector, QwtPlot.yRight)
            plot_flag_curve = self.curve(self.imag_flag_vector)
            plot_flag_curve.setSymbol(QwtSymbol(QwtSymbol.XCross, QBrush(Qt.black),
                     QPen(Qt.black), QSize(20, 20)))
            self.setCurveData(self.imag_flag_vector, self.flags_x_index, self.flags_i_values)
            self.curve(self.imag_flag_vector).setEnabled(False)

        else:
          self.enableAxis(QwtPlot.yLeft)
          self.enableAxis(QwtPlot.xBottom)
          self.setAxisTitle(QwtPlot.yLeft, 'Value')
          self.enableAxis(QwtPlot.yRight, False)
          self.x_array = zeros(num_elements, Float32)
          self.y_array = zeros(num_elements, Float32)
          self.x_array =  flattened_array
          self.xCrossSection = self.insertCurve('xCrossSection')
          self.setCurvePen(self.xCrossSection, QPen(Qt.black, 2))
          self.setCurveStyle(self.xCrossSection,Qt.SolidLine)
          self.setCurveYAxis(self.xCrossSection, QwtPlot.yLeft)
          plot_curve=self.curve(self.xCrossSection)
          plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.red),
                     QPen(Qt.red), QSize(5,5)))
          self.setCurveData(self.xCrossSection, self.x_index, self.x_array)
          if not self.dummy_xCrossSection is None:
            self.removeCurve(self.dummy_xCrossSection)
            self.dummy_xCrossSection = None
# stuff for flags
          if not self._flags_array is None:
            self.real_flag_vector = self.insertCurve('real_flags')
            self.setCurvePen(self.real_flag_vector, QPen(Qt.black))
            self.setCurveStyle(self.real_flag_vector, QwtCurve.Dots)
            self.setCurveYAxis(self.real_flag_vector, QwtPlot.yLeft)
            plot_flag_curve = self.curve(self.real_flag_vector)
            plot_flag_curve.setSymbol(QwtSymbol(QwtSymbol.XCross, QBrush(Qt.black),
                     QPen(Qt.black), QSize(20, 20)))
            self.setCurveData(self.real_flag_vector, self.flags_x_index, self.flags_r_values)
            self.curve(self.real_flag_vector).setEnabled(False)

# do the replot
        self.replot()
        _dprint(2, 'called replot in array_plot');
    # array_plot()

    def setFlagsData (self, incoming_flag_array, flip_axes=True):
      """ figure out shape, rank etc of a flag array and
          plot it  """

# hack to get array display correct until forest.state
# record is available
      flag_array = incoming_flag_array
      if flip_axes:
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
      else:
        num_elements = n_rows*n_cols
        self._flags_array = reshape(flag_array,(num_elements,))

    # setFlagsData()

    def add_basic_menu_items(self):
        toggle_id = 299
        self._menu.insertItem("Modify Plot Parameters", toggle_id)
        toggle_id = 300
        self._menu.insertItem("Toggle Cross-Section Legend", toggle_id)
        toggle_id = 301
        self._menu.insertItem("Toggle ColorBar", toggle_id)
        toggle_id = 302
        self._menu.insertItem("Toggle Color/GrayScale Display", toggle_id)
        if self.toggle_array_rank > 2: 
          toggle_id = 303
          self._menu.insertItem("Toggle ND Controller", toggle_id)
        self.zoom_button = QAction(self);
        self.zoom_button.setIconSet(pixmaps.viewmag.iconset());
        self.zoom_button.setText("Enable zoomer");
        self.zoom_button.addTo(self._menu);
        QObject.connect(self.zoom_button,SIGNAL("toggled(bool)"),self.zoom);
        toggle_id = 304
        self._menu.insertItem("Reset zoomer", toggle_id)
        toggle_id = 305
        self._menu.insertItem("Delete X-Section Display", toggle_id)
        self._menu.setItemVisible(toggle_id, False)
        printer = QAction(self);
        printer.setIconSet(pixmaps.fileprint.iconset());
        printer.setText("Print plot");
        QObject.connect(printer,SIGNAL("activated()"),self.printplot);
        printer.addTo(self._menu);

    def set_toggle_array_rank(self, toggle_array_rank):
      self.toggle_array_rank = toggle_array_rank

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
          _dprint(2, 'plotting complex vector');
          self.array_plot('test_vector_complex', vector_array)
        else:
          _dprint(2, 'plotting complex array');
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
          _dprint(2, 'plotting real array');
          self.array_plot('test_image',m)
        else:
          _dprint(2, 'plotting real vector');
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
#   import pyfits
#   image = pyfits.open('./3C236.FITS')
#   demo.array_plot('3C236', image[0].data)

    return demo

def main(args):
    app = QApplication(args)
    demo = make()
    app.setMainWidget(demo)
    app.exec_loop()


# Admire
if __name__ == '__main__':
    main(sys.argv)

