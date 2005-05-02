#!/usr/bin/env python

import sys
from qt import *
from qwt import *
from numarray import *
import numarray.nd_image
from UVPAxis import *
from printfilter import *
from ComplexColorMap import *
from ComplexScaleDraw import *
#from app_browsers import *
from Timba.GUI.pixmaps import pixmaps
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
    temp_array_conj = (abs_array * abs_array) / temp_array
    temp_array = temp_array * temp_array_conj
    mean = temp_array.mean()
    std_dev = sqrt(mean)
    std_dev = abs(std_dev)
    return std_dev
  else:
    return incoming_array.stddev()

# from scipy.pilutil
def bytescale(data, cmin=None, cmax=None, high=255, low=0):
    if data.type() == UInt8:
        return data
    high = high - low
    if cmin is None:
        cmin = data.min()
    if cmax is None:
        cmax = data.max()
    scale = high *1.0 / (cmax-cmin or 1)
    bytedata = ((data*1.0-cmin)*scale + 0.4999).astype(UInt8) + asarray(low).astype(UInt8)
    return bytedata 

def flagbytescale(data, flags_array,cmin=None, cmax=None, high=255, low=0):
    if data.type() == UInt8:
        return data
    high = high - low
    n_rows = flags_array.shape[0]
    n_cols = flags_array.shape[1]
    byte_flags_max = 0.0
    byte_flags_min = 0.0
    for j in range(0, n_rows ) :
      for i in range(0, n_cols) :
        if not flags_array[j][i] > 0:
          byte_flags_max = max(byte_flags_max, data[j][i])
          byte_flags_min = min(byte_flags_min, data[j][i])
    if cmin is None:
        cmin = byte_flags_min
    if cmax is None:
        cmax = byte_flags_max
    scale = high *1.0 / (cmax-cmin or 1)
#    print 'starting conversion to bytedata'
    bytedata = ((data*1.0-cmin)*scale + 0.4999).astype(UInt8) + asarray(low).astype(UInt8)
#    print 'exiting flagbytescale'
    return bytedata 

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


class ColorBar(QWidget):
    def __init__(self, orientation, *args):
        QWidget.__init__(self, *args)
        self.__orientation = orientation
        self.__light = Qt.white
        self.__dark = Qt.black
        self.setCursor(Qt.pointingHandCursor)

    def setOrientation(self, orientation):
        self.__orientation = orientation
        self.update()

    def orientation(self):
        return self.__orientation

    def setRange(self, light, dark):
        self.__light = light
        self.__dark = dark
        self.update()

    def setLight(self, color):
        self.__light = color
        self.update()

    def setDark(self, color):
        self.__dark = color
        self.update()

    def light(self):
        return self.__light

    def dark(self):
        return self.__dark

    def mousePressEvent(self, event):
        if event.button() ==  Qt.LeftButton:
            pm = QPixmap.grabWidget(self)
            color = QColor()
            color.setRgb(pm.convertToImage().pixel(event.x(), event.y()))
            self.emit(PYSIGNAL("colorSelected"), (color,))
        if qVersion() >= '3.0.0':
            event.accept()

    def paintEvent(self, _):
        painter = QPainter(self)
        self.drawColorBar(painter, self.rect())

    def drawColorBar(self, painter, rect):
        h1, s1, v1 = self.__light.getHsv()
        h2, s2, v2 = self.__dark.getHsv()
        painter.save()
        painter.setClipRect(rect)
        painter.setClipping(True)
        painter.fillRect(rect, QBrush(self.__dark))
        sectionSize = 2
        if (self.__orientation == Qt.Horizontal):
            numIntervalls = rect.width()/sectionSize
        else:
            numIntervalls = rect.height()/sectionSize
        section = QRect()
        for i in range(numIntervalls):
            if self.__orientation == Qt.Horizontal:
                section.setRect(rect.x() + i*sectionSize, rect.y(),
                                sectionSize, rect.heigh())
            else:
                section.setRect(rect.x(), rect.y() + i*sectionSize,
                                rect.width(), sectionSize)
            ratio = float(i)/float(numIntervalls)
            painter.fillRect(section,
                             QBrush(QColor(h1 + int(ratio*(h2-h1) + 0.5),
                                           s1 + int(ratio*(s2-s1) + 0.5),
                                           v1 + int(ratio*(v2-v1) + 0.5),
                                           QColor.Hsv)))
        painter.restore()


class QwtPlotImage(QwtPlotMappedItem):

    def __init__(self, parent):
        QwtPlotItem.__init__(self, parent)
        self.plot = parent
        self.display_type = "hippo"
        self.ValueAxis =  None
        self.ComplexColorMap = None
	self._flags_array = None
	self._display_flags = False
        self.image = None

    # __init__()
    
    def setDisplayType(self, display_type):
        self.display_type = display_type
        _dprint(2,'display type set to ', self.display_type);
        if self.display_type == "brentjens" and self.ValueAxis == None:
          self.ValueAxis =  UVPAxis()
          self.ComplexColorMap = ComplexColorMap(256)
    # setDisplayType

    def setFlagsArray(self, flags_array):
        self._flags_array = flags_array
    # setFlagsArray

    def setDisplayFlag(self, display_flags):
        self._display_flags = display_flags
    # setDisplayFlag

    def setImage(self, image):
# turm image into a QImage	
        byte_image = bytescale(image)
	flags_image = None
	byte_flags_min = 0
	byte_flags_max = 0
	byte_flags_range = 0
	if not self._flags_array is None:
	  temp_image = image.copy()
# call the flagbytesscale function with low = 1, so that we avoid having
# any actual data points with a byte value of 0.
          flags_image = flagbytescale(temp_image, self._flags_array, None, None, 255, 1)
          n_rows = self._flags_array.shape[0]
          n_cols = self._flags_array.shape[1]
	  for j in range(0, n_rows ) :
	    for i in range(0, n_cols) :
	      if not self._flags_array[j][i] > 0:
	        byte_flags_max = max(byte_flags_max, flags_image[j][i])
	        byte_flags_min = min(byte_flags_min, flags_image[j][i])
	  byte_flags_range = byte_flags_max - byte_flags_min

        byte_range = 1.0 * (byte_image.max() - byte_image.min())
        byte_min = 1.0 * (byte_image.min())
        self.image = toQImage(byte_image).mirror(0, 1)
	if not flags_image is None:
          self.byte_flags_image = toQImage(flags_image).mirror(0, 1)

# set color scale a la HippoDraw Scale
        if self.display_type == "hippo":
          dv = byte_range
          vmin = byte_min
          for i in range(0, 256):
            r = 1.0
            g = 1.0
            b = 1.0
            v = 1.0 * i
            if (v < (vmin + 0.25 * dv)):
              r = 0;
              if dv != 0:
                g = 4 * (v - vmin) / dv;
            elif (v < (vmin + 0.5 * dv)):
              r = 0;
              if dv != 0:
                b = 1 + 4 * (vmin + 0.25 * dv - v) / dv;
            elif (v < (vmin + 0.75 * dv)):
              b = 0;
              if dv != 0:
                r = 4 * (v - vmin - 0.5 * dv) / dv;
            else: 
              b = 0;
              if dv != 0:
                g = 1 + 4 * (vmin + 0.75 * dv - v) / dv;
              else:
                r = 0
            red   = int ( r * 255. )
            green = int ( g * 255. )
            blue  = int ( b * 255. )
# the following call will use the previous computations to
# set up a hippo-like color display
            self.image.setColor(i, qRgb(red, green, blue))
	  if not self._flags_array is None:
            dv = byte_flags_range
            vmin = byte_flags_min
            for i in range(0, 256):
              r = 1.0
              g = 1.0
              b = 1.0
              v = 1.0 * i
              if (v < (vmin + 0.25 * dv)):
                r = 0;
                if dv != 0:
                  g = 4 * (v - vmin) / dv;
              elif (v < (vmin + 0.5 * dv)):
                r = 0;
                if dv != 0:
                  b = 1 + 4 * (vmin + 0.25 * dv - v) / dv;
              elif (v < (vmin + 0.75 * dv)):
                b = 0;
                if dv != 0:
                  r = 4 * (v - vmin - 0.5 * dv) / dv;
              else: 
                b = 0;
                if dv != 0:
                  g = 1 + 4 * (vmin + 0.75 * dv - v) / dv;
                else:
                  r = 0
              red   = int ( r * 255. )
              green = int ( g * 255. )
              blue  = int ( b * 255. )
# the following call will use the previous computations to
# set up a hippo-like color display
              self.byte_flags_image.setColor(i, qRgb(red, green, blue))

# the following call will set up gray scale
        if self.display_type == "grayscale":
          for i in range(0, 256):
            self.image.setColor(i, qRgb(i, i, i))

# compute flagged array
        if not self._flags_array is None:
          n_rows = self._flags_array.shape[0]
          n_cols = self._flags_array.shape[1]
	  for j in range(0, n_rows ) :
	    for i in range(0, n_cols) :
# display is mirrored in vertical direction	    
	      mirror_col = n_cols-1-i
	      if self._flags_array[j][i] > 0:
 	        self.byte_flags_image.setPixel(j,mirror_col,0)
# display flag image pixels in black 
          self.byte_flags_image.setColor(0, qRgb(0, 0, 0))

#for testing only
# 	  self.image = self.flag_image

    def setBrentjensImage(self, image):
      absmin = abs(image.min())
      MaxAbs = abs(image.max())
      if (absmin > MaxAbs):
        MaxAbs = absmin
      self.ValueAxis.calcTransferFunction(-MaxAbs, MaxAbs, 0, self.ComplexColorMap.getNumberOfColors()-1)

      if image.min() != image.max():
# get real and imaginary arrays
        real_image = image.getreal()
        imag_image = image.getimag()
        shape = image.shape
        Ncol = self.ComplexColorMap.getNumberOfColors()
        bits_per_pixel = 32
        self.image = QImage(shape[0], shape[1], bits_per_pixel, Ncol)
        for i in range(shape[0]):
          for j in range(shape[1]):
            colre = int(self.ValueAxis.worldToAxis(real_image[i,j]))
            colim = int(self.ValueAxis.worldToAxis(imag_image[i,j]))
            if(colre < Ncol and colim < Ncol): 
              value = self.ComplexColorMap.get_color_value(colre,colim)
              self.image.setPixel(i,j,value)
            else:
              _dprint(2, "*************************************");
              _dprint(2, "colre: ", colre);
              _dprint(2, "colim: ", colim);
              _dprint(2, "real : ", real_image[i,j]);
              _dprint(2, "imag : ", imag_image[i,j]);
              _dprint(2, "Ncol: ", Ncol);
              _dprint(2, "*************************************");
        self.image.mirror(0,1)

    def setData(self, xyzs, xScale = None, yScale = None):
        shape = xyzs.shape
        if xScale:
#           self.xMap = QwtDiMap(0, shape[0], xScale[0], xScale[1])
            self.xMap = QwtDiMap(0, shape[0]-1, xScale[0], xScale[1])
            self.plot.setAxisScale(QwtPlot.xBottom, *xScale)
        else:
            self.xMap = QwtDiMap(0, shape[0], 0, shape[0] )
            self.plot.setAxisScale(QwtPlot.xBottom, 0, shape[0])
        if yScale:
#           self.yMap = QwtDiMap(0, shape[1], yScale[0], yScale[1])
            self.yMap = QwtDiMap(0, shape[1]-1, yScale[0], yScale[1])
            self.plot.setAxisScale(QwtPlot.yLeft, *yScale)
        else:
            self.yMap = QwtDiMap(0, shape[1], 0, shape[1])
            self.plot.setAxisScale(QwtPlot.yLeft, 0, shape[1])
        if self.display_type == "brentjens":
          self.setBrentjensImage(xyzs)
        else:
          self.setImage(xyzs)
    # setData()    

    def drawImage(self, painter, xMap, yMap):
        """Paint image to zooming to xMap, yMap

        Calculate (x1, y1, x2, y2) so that it contains at least 1 pixel,
        and copy the visible region to scale it to the canvas.
        """
        if self.image is None:
          return

#        print 'in drawImage'
#        print 'incoming x map ranges ',xMap.d1(), ' ', xMap.d2()
#        print 'incoming y map ranges ',yMap.d1(), ' ', yMap.d2()
        # calculate y1, y2
        y1 = y2 = self.image.height()
#        y1 = y2 = self.image.height() - 1
#        print 'starting image height ', y1
        y1 *= (self.yMap.d2() - yMap.d2())
        y1 /= (self.yMap.d2() - self.yMap.d1())
#        print 'float y1 ', y1
        y1 = max(0, int(y1-0.5))
#        y1 = max(0, (y1-0.5))
        y2 *= (self.yMap.d2() - yMap.d1())
        y2 /= (self.yMap.d2() - self.yMap.d1())
#        print 'float y2 ', y2
        y2 = min(self.image.height(), int(y2+0.5))
#        y2 = min(self.image.height(), (y2+0.5))
#        print 'y1, y2 ', y1, ' ', y2
        # calculate x1, x1
        x1 = x2 = self.image.width() 
#        x1 = x2 = self.image.width() - 1
#        print 'starting image width ', x1
        x1 *= (xMap.d1() - self.xMap.d1())
        x1 /= (self.xMap.d2() - self.xMap.d1())
#        print 'float x1 ', x1
        x1 = max(0, int(x1-0.5))
#        x1 = max(0, (x1-0.5))
        x2 *= (xMap.d2() - self.xMap.d1())
        x2 /= (self.xMap.d2() - self.xMap.d1())
#        print 'float x2 ', x2
        x2 = min(self.image.width(), int(x2+0.5))
#        x2 = min(self.image.width(), (x2+0.5))
#        print 'x1, x2 ', x1, ' ', x2
        # copy
	image = None
	if self._display_flags:
          image = self.byte_flags_image.copy(x1, y1, x2-x1, y2-y1)
	else:
          image = self.image.copy(x1, y1, x2-x1, y2-y1)
        # zoom
        image = image.smoothScale(xMap.i2()-xMap.i1()+1, yMap.i1()-yMap.i2()+1)
        # draw
        painter.drawImage(xMap.i1(), yMap.i2(), image)

    # drawImage()

# QwtPlotImage()
    
display_image_instructions = \
'''Click the <b>left</b> mouse button in a spectrum display window to get the value of the pixel at this position.<br><br>
Click the <b>middle</b> mouse button in a spectrum display window to get a cross section through the imagein the X and Y directions.<br><br>
Click the <b>right</b> mouse button in a spectrum display window to get get a context menu with options for printing, plotting, and selecting another image.'''

class QwtImagePlot(QwtPlot):

    display_table = {
        'hippo': 'hippo',
        'grayscale': 'grayscale',
        'brentjens': 'brentjens',
        }

    def __init__(self, plot_key=None, parent=None):
        QwtPlot.__init__(self, plot_key, parent)

        self._mainwin = parent and parent.topLevelWidget();

# set default display type to 'hippo'
        self._display_type = "hippo"

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
	self._x_axis = None
	self._y_axis = None
	self._title = None
	self._menu = None
        self._plot_type = None
	self._plot_dict_size = None
	self.created_combined_image = False
	self._combined_image_id = None
	self.is_combined_image = False
        self.active_image_index = None
        self.y_marker_step = None
        self.imag_flag_vector = None
        self.real_flag_vector = None
        self.array_parms = None
        self.metrics_rank = None
        self.iteration_number = None
        # make a QwtPlot widget
        self.plotLayout().setMargin(0)
        self.plotLayout().setCanvasMargin(0)
        self.plotLayout().setAlignCanvasToScales(1)
        self.setTitle('QwtImagePlot: demo')
        self.setAxisTitle(QwtPlot.xBottom, 'Channel Number')
        self.setAxisTitle(QwtPlot.yLeft, 'value')
        
        self.enableAxis(QwtPlot.yRight, False)
        self.enableAxis(QwtPlot.xTop, False)
        self.dummy_xCrossSection = None
        self.xCrossSection = None
        self.yCrossSection = None
        self.myXScale = None
        self.myYScale = None
        self.active_image = False

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

        QWhatsThis.add(self, display_image_instructions)


#        self.__initContextMenu()

    def initSpectrumContextMenu(self):
        """Initialize the spectra context menu
        """
        # skip if no main window
        if not self._mainwin:
          return;

        if self._menu is None:
          self._menu = QPopupMenu(self._mainwin);
          zoom = QAction(self);
          zoom.setIconSet(pixmaps.viewmag.iconset());
          zoom.setText("Disable zoomer");
          zoom.addTo(self._menu);
          printer = QAction(self);
          printer.setIconSet(pixmaps.fileprint.iconset());
          printer.setText("Print plot");
          QObject.connect(printer,SIGNAL("activated()"),self.printplot);
          printer.addTo(self._menu);
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

    def update_spectrum_display(self, menuid):
      if menuid < 0:
        self.unzoom()
        return
      self.active_image_index = menuid
      self.is_combined_image = False
      if not self._combined_image_id is None:
        if self._combined_image_id == menuid:
	  self.is_combined_image = True
      self.array_plot(self._plot_label[menuid], self._plot_dict[menuid], False)

    def initVellsContextMenu (self):
        # skip if no main window
        if not self._mainwin:
          return;
        self._menu = QPopupMenu(self._mainwin);
        QObject.connect(self._menu,SIGNAL("activated(int)"),self.update_vells_display);
        id = -1
        perturb_index = -1
# are we dealing with Vellsets?
        number_of_planes = len(self._vells_rec["vellsets"])
        _dprint(3, 'number of planes ', number_of_planes)
        self._next_plot = {}
        self._perturb_menu = {}
        for i in range(number_of_planes):
          id = id + 1
          if self._vells_rec.vellsets[i].has_key("value"):
            self._label = "go to plane " + str(i) + " value" 
            self._next_plot[id] = self._label
            self._menu.insertItem(self._label,id)
          if self._vells_rec.vellsets[i].has_key("perturbed_value"):
            try:
              number_of_perturbed_arrays = len(self._vells_rec.vellsets[i].perturbed_value)
              perturb_index  = perturb_index  + 1
              self._perturb_menu[perturb_index] = QPopupMenu(self._mainwin);
              for j in range(number_of_perturbed_arrays):
                id = id + 1
                key = " perturbed_value "
                self._label =  "   -> go to plane " + str(i) + key + str(j) 
                self._next_plot[id] = self._label 
                self._menu.insertItem(self._label,id)
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
          if self._vells_rec.vellsets[i].has_key("flags"):
            self._label = "toggle flagged data for plane " + str(i) 
	    toggle_id = 200
            self._menu.insertItem(self._label,toggle_id)
            self._label = "toggle blink of flagged data for plane " + str(i) 
            toggle_id = 201
            self._menu.insertItem(self._label,toggle_id)

        zoom = QAction(self);
        zoom.setIconSet(pixmaps.viewmag.iconset());
        zoom.setText("Disable zoomer");
        zoom.addTo(self._menu);
        printer = QAction(self);
        printer.setIconSet(pixmaps.fileprint.iconset());
        printer.setText("Print plot");
        QObject.connect(printer,SIGNAL("activated()"),self.printplot);
        printer.addTo(self._menu);
    # end initVellsContextMenu()

    def unzoom(self):
        self.zooming = 0
        if len(self.zoomStack):
          xmin, xmax, ymin, ymax = self.zoomStack.pop()
          self.setAxisScale(QwtPlot.xBottom, xmin, xmax)
          self.setAxisScale(QwtPlot.yLeft, ymin, ymax)
          self.refresh_marker_display()
          self.replot()
          _dprint(3, 'called replot in unzoom')
        else:
          return

    def timerEvent_blink(self):
# stop blinking     
      if not self.flag_blink:
        self.timer.stop()
        self.flag_toggle = False
        if self.real_flag_vector is None:
          self.plotImage.setDisplayFlag(self.flag_toggle)
        else:
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
        self.unzoom()
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
# get the shape tuple - useful if the Vells have been compressed down to
# a constant
      self._shape = self._vells_rec.vellsets[plane]["shape"]
# handle "value" first
      if perturb < 0 and self._vells_rec.vellsets[plane].has_key("value"):
        complex_type = False;
# test if we have a numarray
        try:
          if self._vells_rec.vellsets[plane].value.type() == Complex32:
            complex_type = True;
          if self._vells_rec.vellsets[plane].value.type() == Complex64:
            complex_type = True;
          self._value_array = self._vells_rec.vellsets[plane].value
          _dprint(3, 'self._value_array ', self._value_array)
          array_shape = self._value_array.shape
          if len(array_shape) == 1 and array_shape[0] == 1:
            temp_value = self._value_array[0]
            temp_array = numarray.asarray(temp_value)
            self._value_array = numarray.resize(temp_array,self._shape)
        except:
          temp_array = numarray.asarray(self._vells_rec.vellsets[i].value)
          self._value_array = numarray.resize(temp_array,self._shape)
          if self._value_array.type() == Complex32:
            complex_type = True;
          if self._value_array.type() == Complex64:
            complex_type = True;

        key = " value "
        if complex_type:
          _dprint(3,'handling complex array')
#extract real component
          self._value_real_array = self._value_array.getreal()
          self._z_real_min = self._value_real_array.min()
          self._z_real_max = self._value_real_array.max()
#extract imaginary component
          self._value_imag_array = self._value_array.getimag()
          self._z_imag_min = self._value_imag_array.min()
          self._z_imag_max = self._value_imag_array.max()
          self._label = "plane " + str(plane) + key 
          if self._solver_flag:
            self.array_plot(self._label, self._value_array, False)
          else:
            self.array_plot(self._label, self._value_array)
        else:
#we have a real array
          _dprint(3,'handling real array')
          self._label = "plane " + str(plane) + key 
          self._z_real_min = self._value_array.min()
          self._z_real_max = self._value_array.max()
          if self._solver_flag:
            self.array_plot(self._label, self._value_array, False)
          else:
            self.array_plot(self._label, self._value_array)

      else:
# handle "perturbed_value"
        if self._vells_rec.vellsets[plane].has_key("perturbed_value"):
# test if we have a numarray
          complex_type = False;
          perturbed_array_diff = None
          try:
            if self._vells_rec.vellsets[plane].perturbed_value[perturb].type() == Complex32:
              complex_type = True;
            if self._vells_rec.vellsets[plane].perturbed_value[perturb].type() == Complex64:
              complex_type = True;
            perturbed_array_diff = self._vells_rec.vellsets[plane].perturbed_value[perturb]
          except:
            temp_array = numarray.asarray(self._vells_rec.vellsets[plane].perturbed_value[perturb])
            perturbed_array_diff = numarray.resize(temp_array,self._shape)
            if perturbed_array_diff.type() == Complex32:
              complex_type = True;
            if perturbed_array_diff.type() == Complex64:
              complex_type = True;

          key = " perturbed_value "
          self._label =  "plane " + str(plane) + key + str(perturb)
          if self._solver_flag:
            self.array_plot(self._label, perturbed_array_diff, False)
          else:
            self.array_plot(self._label, perturbed_array_diff)
        
    def printplot(self):
        try:
            printer = QPrinter(QPrinter.HighResolution)
        except AttributeError:
            printer = QPrinter()
        printer.setOrientation(QPrinter.Landscape)
        printer.setColorMode(QPrinter.Color)
        printer.setOutputToFile(True)
        printer.setOutputFileName('image_plot.ps')
        if printer.setup():
            filter = PrintFilter()
            if (QPrinter.GrayScale == printer.colorMode()):
                filter.setOptions(QwtPlotPrintFilter.PrintAll
                                  & ~QwtPlotPrintFilter.PrintCanvasBackground)
            self.printPlot(printer, filter)
    # printplot()


    def drawCanvasItems(self, painter, rectangle, maps, filter):
        if not self.is_vector:
          self.plotImage.drawImage(
            painter, maps[QwtPlot.xBottom], maps[QwtPlot.yLeft])
        QwtPlot.drawCanvasItems(self, painter, rectangle, maps, filter)


    def formatCoordinates(self, x, y, value = None):
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
	      xpos1 = xpos1 % self.split_axis
          temp_str = result + "x =%+.2g" % xpos1
          result = temp_str
          temp_str = result + " y =%+.2g" % ypos
          result = temp_str
          xpos = self.plotImage.xMap.limTransform(xpos)
          ypos = self.plotImage.yMap.limTransform(ypos)
        else:
          xpos = int(xpos)
	  xpos1 = xpos
	  if not self.split_axis is None:
	    if xpos1 >  self.split_axis:
	      xpos1 = xpos1 % self.split_axis
          temp_str = result + "x =%+.2g" % xpos1
          result = temp_str
          ypos = int(ypos)
	  ypos1 = ypos
	  if not self.y_marker_step is None:
	    if ypos1 >  self.y_marker_step:
	      marker_index = ypos1 / self.y_marker_step
	      ypos1 = ypos1 % self.y_marker_step
	    else:
	      marker_index = 0
          temp_str = result + " y =%+.2g" % ypos1
          result = temp_str
        if value is None:
          value = self.raw_image[xpos,ypos]
	message = None
        temp_str = " value: %-.3g" % value
	if not marker_index is None:
          message = result + temp_str + '\nsource: ' + self.marker_labels[marker_index]
	else:
          message = result + temp_str
    
#        if not self.array_parms is None:
#          message = message + "\n" + self.array_parms

# alias
        fn = self.fontInfo().family()

# text marker giving source of point that was clicked
        self.marker = self.insertMarker()
        ylb = self.axisScale(QwtPlot.yLeft).lBound()
        xlb = self.axisScale(QwtPlot.xBottom).lBound()
        self.setMarkerPos(self.marker, xlb, ylb)
        self.setMarkerLabelAlign(self.marker, Qt.AlignRight | Qt.AlignTop)
        self.setMarkerLabel( self.marker, message,
          QFont(fn, 9, QFont.Bold, False),
          Qt.blue, QPen(Qt.red, 2), QBrush(Qt.yellow))

# insert array info if available
        self.insert_array_info()
        self.replot()
        _dprint(3, 'called replot in formatCoordinates ')
#        timer = QTimer(self)
#        timer.connect(timer, SIGNAL('timeout()'), self.refresh_marker_display)
#        timer.start(2000, True)
            
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
        self.marker = self.insertMarker()
        ylb = self.axisScale(QwtPlot.yLeft).lBound()
        xlb = self.axisScale(QwtPlot.xBottom).lBound()
        self.setMarkerPos(self.marker, xlb, ylb)
        self.setMarkerLabelAlign(self.marker, Qt.AlignRight | Qt.AlignTop)
        self.setMarkerLabel( self.marker, message,
          QFont(fn, 9, QFont.Bold, False),
          Qt.blue, QPen(Qt.red, 2), QBrush(Qt.yellow))

# insert array info if available
        self.insert_array_info()
        self.replot()
        _dprint(3, 'called replot in reportCoordinates ')
    # reportCoordinates()

    def refresh_marker_display(self):
      self.removeMarkers()
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
#        self.setMarkerLabelAlign(mY, Qt.AlignRight | Qt.AlignBottom)
#        self.setMarkerLabel(mY, '',  QFont(fn, 12, QFont.Bold),
#                Qt.white, QPen(Qt.NoPen), QBrush(Qt.black))
#        self.setMarkerLabelText(mY, label)
        y = y + self.y_marker_step
        self.setMarkerYPos(mY, y)
    
    def onMouseMoved(self, e):
       if self._plot_type == 'histogram':
          return
       if self.is_vector:
          return
#       pass

#      self.statusBar().message(
#            ' -- '.join(self.formatCoordinates(e.pos().x(), e.pos().y())))
#       if Qt.LeftButton == e.button():
#         self.formatCoordinates(e.pos().x(), e.pos().y())

    # onMouseMoved()

    def onMousePressed(self, e):
        if self._plot_type == 'histogram':
            return
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
#             print ' curve_number, distance, xVal, yVal, index ', curve_number, ' ', distance,' ', xVal, ' ', yVal, ' ', index;
              self.reportCoordinates(xVal, yVal)
#             return

            else:
              self.formatCoordinates(e.pos().x(), e.pos().y())
            self.xpos = e.pos().x()
            self.ypos = e.pos().y()
            self.enableOutline(1)
            self.setOutlinePen(QPen(Qt.black))
            self.setOutlineStyle(Qwt.Rect)
            self.zooming = 1
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
              shape = self.raw_image.shape
#              print 'raw mouse positions ', xpos, ' ', ypos
              xpos = self.invTransform(QwtPlot.xBottom, xpos)
              ypos = self.invTransform(QwtPlot.yLeft, ypos)
#              print 'inverted mouse positions ', xpos, ' ', ypos
              temp_array = asarray(ypos)
              self.x_arrayloc = resize(temp_array,shape[0])
              temp_array = asarray(xpos)
              self.y_arrayloc = resize(temp_array,shape[1])
              if self._vells_plot:
                xpos = self.plotImage.xMap.limTransform(xpos)
                ypos = self.plotImage.yMap.limTransform(ypos)
              else:
                xpos = int(xpos)
                ypos = int(ypos)
#              print 'image mouse positions ', xpos, ' ', ypos
              self.x_array = zeros(shape[0], Float32)
              self.x_index = arange(shape[0])
              self.x_index = self.x_index + 0.5
              for i in range(shape[0]):
                self.x_array[i] = self.raw_image[i,ypos]
              self.setAxisAutoScale(QwtPlot.yRight)
              self.y_array = zeros(shape[1], Float32)
              self.y_index = arange(shape[1])
              self.y_index = self.y_index + 0.5
              for i in range(shape[1]):
                self.y_array[i] = self.raw_image[xpos,i]
              self.setAxisAutoScale(QwtPlot.xTop)
              if self.xCrossSection is None:
                self.xCrossSection = self.insertCurve('xCrossSection')
                self.setCurvePen(self.xCrossSection, QPen(Qt.black, 2))
                plot_curve=self.curve(self.xCrossSection)
                plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, 
                   QBrush(Qt.black), QPen(Qt.black), QSize(10,10)))
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
                   QBrush(Qt.white), QPen(Qt.white), QSize(10,10)))
              self.enableAxis(QwtPlot.xTop)
              self.setAxisTitle(QwtPlot.xTop, 'y cross-section value')
              self.setCurveYAxis(self.yCrossSection, QwtPlot.yLeft)
              self.setCurveXAxis(self.yCrossSection, QwtPlot.xTop)
#              self.setAxisOptions(QwtPlot.xTop,QwtAutoScale.Inverted)
              if self._vells_plot:
                delta_vells = self.vells_end_freq - self.vells_start_freq
                x_step = delta_vells / shape[0] 
                start_freq = self.vells_start_freq + 0.5 * x_step
                for i in range(shape[0]):
                  self.x_index[i] = start_freq + i * x_step
                delta_vells = self.vells_end_time - self.vells_start_time
                y_step = delta_vells / shape[1] 
                start_time = self.vells_start_time + 0.5 * y_step
                for i in range(shape[1]):
                  self.y_index[i] = start_time + i * y_step
              self.setCurveData(self.xCrossSection, self.x_index, self.x_array)
              self.setCurveData(self.yCrossSection, self.y_array, self.y_index)

# put in a line where cross sections are selected
              if self.xCrossSectionLoc is None:
                self.xCrossSectionLoc = self.insertCurve('xCrossSectionLoc')
                self.setCurvePen(self.xCrossSectionLoc, QPen(Qt.black, 2))
                self.setCurveYAxis(self.xCrossSectionLoc, QwtPlot.yLeft)
              self.setCurveData(self.xCrossSectionLoc, self.x_index, self.x_arrayloc)
              if self.yCrossSectionLoc is None:
                self.yCrossSectionLoc = self.insertCurve('yCrossSectionLoc')
                self.setCurvePen(self.yCrossSectionLoc, QPen(Qt.white, 2))
                self.setCurveYAxis(self.yCrossSectionLoc, QwtPlot.yLeft)
                self.setCurveXAxis(self.yCrossSectionLoc, QwtPlot.xBottom)
              self.setCurveData(self.yCrossSectionLoc, self.y_arrayloc, self.y_index)
              if self.is_combined_image:
                self.removeMarkers()
	        self.insert_marker_lines()
              self.replot()
              _dprint(2, 'called replot in onMousePressed');
           
# fake a mouse move to show the cursor position
        self.onMouseMoved(e)

    # onMousePressed()

    def onMouseReleased(self, e):
        if self._plot_type == 'histogram':
            return
#       if self.is_vector:
#           return
        if Qt.LeftButton == e.button():
            self.refresh_marker_display()
            xmin = min(self.xpos, e.pos().x())
            xmax = max(self.xpos, e.pos().x())
            ymin = min(self.ypos, e.pos().y())
            ymax = max(self.ypos, e.pos().y())
            self.setOutlineStyle(Qwt.Cross)
            xmin = self.invTransform(QwtPlot.xBottom, xmin)
            xmax = self.invTransform(QwtPlot.xBottom, xmax)
            ymin = self.invTransform(QwtPlot.yLeft, ymin)
            ymax = self.invTransform(QwtPlot.yLeft, ymax)
            if xmin == xmax or ymin == ymax:
                return
            self.zoomStack.append(self.zoomState)
            self.zoomState = (xmin, xmax, ymin, ymax)
            self.enableOutline(0)
        elif Qt.RightButton == e.button():
            if len(self.zoomStack):
                xmin, xmax, ymin, ymax = self.zoomStack.pop()
            else:
                return
        elif Qt.MidButton == e.button():
          return

        self.setAxisScale(QwtPlot.xBottom, xmin, xmax)
        self.setAxisScale(QwtPlot.yLeft, ymin, ymax)
        self.replot()
        _dprint(2, 'called replot in onMouseReleased');

    # onMouseReleased()

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
    # setDisplayType

    def display_image(self, image):
      if self._vells_plot:
        self.plotImage.setData(image, self.vells_freq, self.vells_time)
      else:
        self.plotImage.setData(image)

      self.raw_image = image
      if self._display_type == "brentjens":
        self.plotImage.setBrentjensImage(image)
      else:
        self.plotImage.setImage(image)
      if self.is_combined_image:
         _dprint(2, 'display_image inserting markers')
         self.removeMarkers()
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
      self.replot()
      _dprint(2, 'called replot in display_image');
    # display_image()

    def insert_array_info(self):
# insert mean and standard deviation
      if not self.array_parms is None:
# alias
        fn = self.fontInfo().family()

# text marker giving mean and std deviation of array
        self.info_marker = self.insertMarker()
        ylb = self.axisScale(QwtPlot.yLeft).hBound()
        xlb = self.axisScale(QwtPlot.xBottom).hBound()
        self.setMarkerPos(self.info_marker, xlb, ylb)
        self.setMarkerLabelAlign(self.info_marker, Qt.AlignLeft | Qt.AlignBottom)
        self.setMarkerLabel( self.info_marker, self.array_parms,
          QFont(fn, 9, QFont.Bold, False),
          Qt.blue, QPen(Qt.red, 2), QBrush(Qt.white))
    # insert_array_info()

    def plot_data(self, visu_record, attribute_list=None):
      """ process incoming data and attributes into the
          appropriate type of plot """
      _dprint(2, 'in plot data');
#      _dprint(2, 'visu_record ', visu_record)

# first find out what kind of plot we are making
      self._plot_type = None
      self._title = None
      self._x_axis = None
      self._y_axis = None
      self._display_type = None
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
            self._display_type = plot_parms.get('spectrum_color')
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
            if self._title is None and plot_parms.has_key('title'):
              self._title = plot_parms.get('title')
              self.setTitle(self._title)
            if self._x_axis is None and plot_parms.has_key('x_axis'):
              self._x_axis = plot_parms.get('x_axis')
            if self._y_axis is None and plot_parms.has_key('y_axis'):
              self._y_axis = plot_parms.get('y_axis')
            if self._display_type is None and plot_parms.has_key('spectrum_color'):
              self._display_type = plot_parms.get('spectrum_color')
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
        _dprint(2,'display_image: self._data_labels ', self._data_labels);
      else:
        self._data_labels = ''

# set defaults for anything that is not specified
      if self._string_tag is None:
        self._string_tag = ''
      if self._display_type is None:
        self._display_type = 'hippo'
      if self._plot_type is None:
        self._plot_type = 'spectra'

# set the display color type in the low level QwtPlotImage class
      self.setDisplayType(self._display_type)

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
          self.array_plot(self._plot_label[self.active_image_index], self._plot_dict[self.active_image_index],False)
          if self.active_image_index == self._combined_image_id:
	    self.is_combined_image = True
            self.removeMarkers()
	    self.insert_marker_lines()
        elif not self._combined_image_id is None:
          self.array_plot(self._plot_label[ self._combined_image_id], self._plot_dict[ self._combined_image_id],False)
	  self.is_combined_image = True
          self.removeMarkers()
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
      """ get vells frequency and time ranges for use 
          with other functions """
                                                                                
      self.vells_start_freq = self._vells_rec.cells.domain.freq[0] 
      self.vells_end_freq  =  self._vells_rec.cells.domain.freq[1]
      self.vells_start_time = self._vells_rec.cells.domain.time[0] 
      self.vells_end_time  =  self._vells_rec.cells.domain.time[1]

      self.vells_freq = (self.vells_start_freq,self.vells_end_freq)
      self.vells_time = (self.vells_start_time,self.vells_end_time)

                                                                                
    def plot_vells_data (self, vells_record):
      """ process incoming vells data and attributes into the
          appropriate type of plot """

      _dprint(2, 'in plot_vells_data');
      self.metrics_rank = None
      self.iteration_number = None
      self._vells_rec = vells_record;
# if we are single stepping through requests, Oleg may reset the
# cache, so check for a non-data record situation
      if isinstance(self._vells_rec, bool):
        return

# are we dealing with 'solver' results?
      if self._vells_rec.has_key("solver_result"):
        if self._vells_rec.solver_result.has_key("incremental_solutions"):
          self._solver_flag = True
          self._x_axis = 'Solvable Coeffs'
          self._y_axis = 'Iteration Nr'
          complex_type = False;
          if self._vells_rec.solver_result.incremental_solutions.type() == Complex32:
            complex_type = True;
          if self._vells_rec.solver_result.incremental_solutions.type() == Complex64:
            complex_type = True;
          self._value_array = self._vells_rec.solver_result.incremental_solutions
          if self._vells_rec.solver_result.has_key("metrics"):
            metrics = self._vells_rec.solver_result.metrics
            self.metrics_rank = zeros(len(metrics), Int32)
            self.iteration_number = zeros(len(metrics), Int32)
            for i in range(len(metrics)):
               self.metrics_rank[i] = metrics[i].rank
               self.iteration_number[i] = i+1
          self.array_plot("Solver Incremental Solutions", self._value_array, True)

# are we dealing with Vellsets?
      if self._vells_rec.has_key("vellsets") and not self._solver_flag:
        self._vells_plot = True
        self.calc_vells_ranges()
        self. initVellsContextMenu()
        _dprint(3, 'handling vellsets')


# how many VellSet planes (e.g. I, Q, U, V would each be a plane) are there?
        number_of_planes = len(self._vells_rec["vellsets"])
        _dprint(3, 'number of planes ', number_of_planes)
        if self._vells_rec.vellsets[0].has_key("shape"):
          self._shape = self._vells_rec.vellsets[0]["shape"]

# do we have flags for data	  
        if self._vells_rec.vellsets[0].has_key("flags"):
# test if we have a numarray
          try:
            self._flags_array = self._vells_rec.vellsets[0].flags
            _dprint(3, 'self._flags_array ', self._flags_array)
            array_shape = self._flags_array.shape
            if len(array_shape) == 1 and array_shape[0] == 1:
              temp_value = self._flags_array[0]
              temp_array = asarray(temp_value)
              self._flags_array = resize(temp_array,self._shape)
          except:
            temp_array = asarray(self._vells_rec.vellsets[0].flags)
            self._flags_array = resize(temp_array,self._shape)

          self.setFlagsData(self._flags_array)

# plot the first plane member
        if self._vells_rec.vellsets[0].has_key("value"):
          complex_type = False;
# test if we have a numarray
          try:
            if self._vells_rec.vellsets[0].value.type() == Complex32:
              complex_type = True;
            if self._vells_rec.vellsets[0].value.type() == Complex64:
              complex_type = True;
            self._value_array = self._vells_rec.vellsets[0].value
            _dprint(3, 'self._value_array ', self._value_array)
            array_shape = self._value_array.shape
            if len(array_shape) == 1 and array_shape[0] == 1:
              temp_value = self._value_array[0]
              temp_array = asarray(temp_value)
              self._value_array = resize(temp_array,self._shape)

          except:
            temp_array = asarray(self._vells_rec.vellsets[0].value)
            self._shape = self._vells_rec.vellsets[0]["shape"]
            self._value_array = resize(temp_array,self._shape)
            if self._value_array.type() == Complex32:
              complex_type = True;
            if self._value_array.type() == Complex64:
              complex_type = True;

# for test purposes only
#         self._flags_array = self._value_array.getreal().copy()
#         for k in range(64):
#           self._flags_array[0,k] = 0.0
#         self._flags_array[0,11] = 1.0
#         self._flags_array[0,21] = 1.0
#         self._flags_array[0,31] = 1.0
#         self.setFlagsData(self._flags_array)

          key = " value "
          if complex_type:
            _dprint(3,'handling complex array')
#extract real component
            self._value_real_array = self._value_array.getreal()
            self._z_real_min = self._value_real_array.min()
            self._z_real_max = self._value_real_array.max()
#extract imaginary component
            self._value_imag_array = self._value_array.getimag()
            self._z_imag_min = self._value_imag_array.min()
            self._z_imag_max = self._value_imag_array.max()
            self._label = "plane " + str(0) + key 
            if self._solver_flag:
              self.array_plot(self._label, self._value_array, False)
            else:
              self.array_plot(self._label, self._value_array)
          else:
#we have a real array
            _dprint(3,'handling real array')
            self._label = "plane " + str(0) + key 
            self._z_real_min = self._value_array.min()
            self._z_real_max = self._value_array.max()
            if self._solver_flag:
              self.array_plot(self._label, self._value_array, False)
            else:
              self.array_plot(self._label, self._value_array)

    # end plot_vells_data()

    def handle_finished (self):
      print 'in handle_finished'

    def array_plot (self, data_label, incoming_plot_array, flip_axes=True):
      """ figure out shape, rank etc of a spectrum array and
          plot it  """

# delete any previous curves
      self.removeCurves()
      self.xCrossSection = None
      self.yCrossSection = None
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
        zoom = QAction(self);
        zoom.setIconSet(pixmaps.viewmag.iconset());
        zoom.setText("Disable zoomer");
        zoom.addTo(self._menu);
        printer = QAction(self);
        printer.setIconSet(pixmaps.fileprint.iconset());
        printer.setText("Print plot");
        QObject.connect(printer,SIGNAL("activated()"),self.printplot);
        printer.addTo(self._menu);
        QObject.connect(self._menu,SIGNAL("activated(int)"),self.update_spectrum_display);

# set title
      if self._title is None:
        self.setTitle(data_label)

# hack to get array display correct until forest.state
# record is available
      plot_array = incoming_plot_array
      if flip_axes:
        axes = arange(incoming_plot_array.rank)[::-1]
        plot_array = transpose(incoming_plot_array, axes)

# figure out type and rank of incoming array
      is_time = False
      is_frequency = False
      self.is_vector = False;
      array_dim = len(plot_array.shape)
      array_rank = plot_array.rank
      if array_rank == 1:
        self.is_vector = True;
      n_rows = plot_array.shape[0]
      if n_rows == 1:
        self.is_vector = True
        is_time = True
      n_cols = 1
      if array_rank == 2:
        n_cols = plot_array.shape[1]
        if n_cols == 1:
          self.is_vector = True
          is_frequency = True

# test for real or complex
      complex_type = False;
      if plot_array.type() == Complex32:
        complex_type = True;
      if plot_array.type() == Complex64:
        complex_type = True;

# test if we have a 2-D array
      if self.is_vector == False:
        self.active_image = True

# create colorbar
#        scale = self.axis(QwtPlot.yLeft)
#        scale.setBaselineDist(10)
#        self.colorBar = ColorBar(Qt.Vertical, scale)
#        self.colorBar.setRange(Qt.red, Qt.darkBlue)
#        self.colorBar.setFocusPolicy(QWidget.TabFocus)

#        self.setAxisAutoScale(QwtPlot.xBottom)

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
	    if self._x_axis is None:
              self.setAxisTitle(QwtPlot.xBottom, 'Frequency (real followed by imaginary)')
	    else:  
              self.setAxisTitle(QwtPlot.xBottom, self._x_axis)
	    if self._y_axis is None:
              self.setAxisTitle(QwtPlot.yLeft, 'Time')
	    else:
              self.setAxisTitle(QwtPlot.yLeft, self._y_axis)
	    self.vells_end_freq = 2 * self.vells_end_freq
	    self.vells_freq = (self.vells_start_freq,self.vells_end_freq)
            delta_vells = self.vells_end_freq - self.vells_start_freq
            self.split_axis = self.vells_start_freq  + 0.5 * delta_vells
            self.myXScale = ComplexScaleDraw(self.split_axis)
            self.setAxisScaleDraw(QwtPlot.xBottom, self.myXScale)
          else:
	    if self._x_axis is None:
              self.setAxisTitle(QwtPlot.xBottom, 'Channel Number (real followed by imaginary)')
	    else:  
              self.setAxisTitle(QwtPlot.xBottom, self._x_axis)
	    if self._y_axis is None:
              self.setAxisTitle(QwtPlot.yLeft, 'sequence')
	    else:
              self.setAxisTitle(QwtPlot.yLeft, self._y_axis)
            self.myXScale = ComplexScaleDraw(plot_array.shape[0])
            self.setAxisScaleDraw(QwtPlot.xBottom, self.myXScale)
	    self.split_axis = plot_array.shape[0]
	    if not self.y_marker_step is None:
              self.myYScale = ComplexScaleDraw(self.y_marker_step)
              self.setAxisScaleDraw(QwtPlot.yLeft, self.myYScale)

# create array of reals followed by imaginaries
          real_array =  plot_array.getreal()
          imag_array =  plot_array.getimag()
          shape = real_array.shape
          temp_array = zeros((2*shape[0],shape[1]), Float32)
          for k in range(shape[0]):
            for j in range(shape[1]):
              temp_array[k,j] = real_array[k,j]
              temp_array[k+shape[0],j] = imag_array[k,j]

          self.display_image(temp_array)
        else:
          if self._vells_plot:
	    if self._x_axis is None:
              self.setAxisTitle(QwtPlot.xBottom, 'Frequency')
	    else:  
              self.setAxisTitle(QwtPlot.xBottom, self._x_axis)
	    if self._y_axis is None:
              self.setAxisTitle(QwtPlot.yLeft, 'Time')
	    else:
              self.setAxisTitle(QwtPlot.yLeft, self._y_axis)
          else:
	    if self._x_axis is None:
              self.setAxisTitle(QwtPlot.xBottom, 'Channel Number')
	    else:  
              self.setAxisTitle(QwtPlot.xBottom, self._x_axis)
	    if self._y_axis is None:
              self.setAxisTitle(QwtPlot.yLeft, 'sequence')
	    else:
              self.setAxisTitle(QwtPlot.yLeft, self._y_axis)
          self.display_image(plot_array)

      if self.is_vector == True:
# make sure we are autoscaling in case an image was previous
        self.setAxisAutoScale(QwtPlot.xBottom)
        self.setAxisAutoScale(QwtPlot.yLeft)
        self.setAxisAutoScale(QwtPlot.yRight)

        if not self._flags_array is None:
          self.flags_x_index = []
          self.flags_r_values = []
          self.flags_i_values = []
        self.active_image = False
        num_elements = n_rows*n_cols
        if self._vells_plot:
          if is_frequency:
            self.setAxisTitle(QwtPlot.xBottom, 'Frequency')
            delta_vells = self.vells_end_freq - self.vells_start_freq
            x_step = delta_vells / n_rows 
            start_freq = self.vells_start_freq + 0.5 * x_step
            self.x_index = zeros(num_elements, Float32)
            for j in range(n_rows):
              self.x_index[j] = start_freq + j * x_step
          else:
            self.setAxisTitle(QwtPlot.xBottom, 'Time')
            delta_vells = self.vells_end_time - self.vells_start_time
            x_step = delta_vells / n_cols 
            start_time = self.vells_start_time + 0.5 * x_step
            self.x_index = zeros(num_elements, Float32)
            for j in range(n_cols):
              self.x_index[j] = start_time + j * x_step
        else:
          self.setAxisTitle(QwtPlot.xBottom, 'Channel Number')
          self.x_index = arange(num_elements)
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
                     QPen(Qt.red), QSize(10,10)))
          plot_curve=self.curve(self.yCrossSection)
          plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.green),
                     QPen(Qt.green), QSize(10,10)))
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
                     QPen(Qt.red), QSize(10,10)))
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
      array_dim = len(flag_array.shape)
      array_rank = flag_array.rank
      if array_rank == 1:
        flag_is_vector = True;
      n_rows = flag_array.shape[0]
      if n_rows == 1:
        flag_is_vector = True
      n_cols = 1
      if array_rank == 2:
        n_cols = flag_array.shape[1]
        if n_cols == 1:
          flag_is_vector = True

      if flag_is_vector == False:
        self.plotImage.setFlagsArray(flag_array)
      else:
        num_elements = n_rows*n_cols
        self._flags_array = reshape(flag_array,(num_elements,))

    # setFlagData()

    def histogram_plot (self, data_label, input_array, num_bins=10):
      """ figure out shape, rank etc of a spectrum array and
          plot it  """

# set the plot type - used to presently suppress mouse interaction
      self._plot_type = 'histogram'

# set title
      if self._title is None:
        self.setTitle(data_label)

# figure out type and rank of incoming array
      complex_type = False
      if input_array.type() == Complex32:
            complex_type = True;
      if input_array.type() == Complex64:
            complex_type = True;
      histogram_in = None
      if complex_type:
#        histogram_in = abs(input_array)
        histogram_in = input_array.getreal()
      else:
        histogram_in = input_array
      array_min = histogram_in.min()
      array_max = histogram_in.max()
      histogram_array = numarray.nd_image.histogram(histogram_in, array_min, array_max, num_bins)

# we have created bins, now generate a Qwt curve for each bin
      histogram_curve_x = zeros(4 * num_bins, Float32) 
      histogram_curve_y = zeros(4 * num_bins, Float32) 
      bin_incr = (array_max - array_min) / num_bins
      curve_index = 0
      for i in range(num_bins):
        bin_start = array_min + i * bin_incr
        bin_end = bin_start + bin_incr
        histogram_curve_x[curve_index] = bin_start
        histogram_curve_y[curve_index] = 0
        histogram_curve_x[curve_index+1] = bin_start
        histogram_curve_y[curve_index+1] = histogram_array[i]
        histogram_curve_x[curve_index+2] = bin_end
        histogram_curve_y[curve_index+2] = histogram_array[i]
        histogram_curve_x[curve_index+3] = bin_end
        histogram_curve_y[curve_index+3] = 0
        curve_index = curve_index + 4
      curve_key = 'histogram_curve'
      curve_index = self.insertCurve(curve_key)
      self.setCurvePen(curve_index, QPen(Qt.black, 2))
      self.setCurveData(curve_index, histogram_curve_x, histogram_curve_y)
      self.setTitle('Histogram')
      self.setAxisTitle(QwtPlot.yLeft, 'number in bin')
      self.setAxisTitle(QwtPlot.xBottom, 'array value ')

# add in histogram for imaginary stuff if we have a complex array
      if complex_type:
#        real_array_max = array_max
        histogram_in = input_array.getimag()
        array_min = histogram_in.min()
        array_max = histogram_in.max()
        histogram_array = numarray.nd_image.histogram(histogram_in, array_min, array_max, num_bins)
        histogram_curve_x_im = zeros(4 * num_bins, Float32) 
        histogram_curve_y_im = zeros(4 * num_bins, Float32) 
        bin_incr = (array_max - array_min) / num_bins
        curve_index = 0
#        array_min = array_min + real_array_max
        for i in range(num_bins):
          bin_start = array_min + i * bin_incr
          bin_end = bin_start + bin_incr
          histogram_curve_x_im[curve_index] = bin_start
          histogram_curve_y_im[curve_index] = 0
          histogram_curve_x_im[curve_index+1] = bin_start
          histogram_curve_y_im[curve_index+1] = histogram_array[i]
          histogram_curve_x_im[curve_index+2] = bin_end
          histogram_curve_y_im[curve_index+2] = histogram_array[i]
          histogram_curve_x_im[curve_index+3] = bin_end
          histogram_curve_y[curve_index+3] = 0
          curve_index = curve_index + 4
        curve_key = 'histogram_curve_imag'
        curve_index_imag = self.insertCurve(curve_key)
        self.setCurvePen(curve_index_imag, QPen(Qt.red, 2))
        self.setCurveData(curve_index_imag, histogram_curve_x_im, histogram_curve_y_im)
        self.setAxisTitle(QwtPlot.xBottom, 'array value (real=black, red=imag) ')
#        self.myXScale = ComplexScaleDraw(array_min)
#        self.setAxisScaleDraw(QwtPlot.xBottom, self.myXScale)
      self.replot()
     
    # histogram_plot()

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
          _dprint(2, 'plotting array');
          self.array_plot('test_image_complex',a)
          self.test_complex = False
        else:
          _dprint(2, 'plotting vector');
          self.array_plot('test_vector_complex', vector_array)
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
          _dprint(2, 'plotting vector');
          self.array_plot('test_vector', vector_array)
          self.test_complex = True
        else:
          _dprint(2, 'plotting array');
          self.array_plot('test_image',m)

      self.index = self.index + 1
    # timerEvent()


def make():
    demo = QwtImagePlot('plot_key')
    demo.resize(500, 300)
    demo.show()
# uncomment the following
#    demo.start_test_timer(5000, False, "brentjens")

# or
# uncomment the following three lines
    import pyfits
    m51 = pyfits.open('./m51.fits')
    demo.array_plot('m51', m51[0].data)

    return demo

def main(args):
    app = QApplication(args)
    demo = make()
    app.setMainWidget(demo)
    app.exec_loop()


# Admire
if __name__ == '__main__':
    main(sys.argv)

