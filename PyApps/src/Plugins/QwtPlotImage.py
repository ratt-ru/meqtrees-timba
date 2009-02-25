#!/usr/bin/env python

#
# The QwtPlotImage class is just a straightforward adaption of 
# the same class in PyQwt-4.2/examples/QwtImagePlotDemo.py.
# The class has been modified to work with the color maps
# used for MeqTrees and also to display flagged arrays.
# The coordinate functions have also been modified to give
# increased accuracy for zooming, etc.


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

import numpy
import math

#from UVPAxis import *
#from ComplexColorMap import *
from ImageScaler import *

from Timba.utils import verbosity
_dbg = verbosity(0,name='QwtPlotImage');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;


# from scipy.pilutil
# note: low is set to 2, so that we can save a value of 0 for a flagged pixel
# and 1 for a pixel with NaNs or Infs
def bytescale(data, limits, high=255, low=2):
    if data.dtype == numpy.uint8:
        return data
    high = high - low
    if limits[0] is None:
        limits[0] = data.min()
    if limits[1] is None:
        limits[1] = data.max()
    scale = high *1.0 / (limits[1]-limits[0] or 1)
    internal_data = data.copy()
    temp1 = numpy.less_equal(data,limits[1])
    temp2 = numpy.greater(data,limits[1])
    internal_data = data * temp1 + temp2 * limits[1]
    temp1 = numpy.greater_equal(internal_data,limits[0])
    temp2 = numpy.less(internal_data,limits[0])
    internal_data = internal_data * temp1 + temp2 * limits[0]
    bytedata = ((internal_data*1.0-limits[0])*scale + 0.4999).astype(numpy.uint8) + numpy.asarray(low).astype(numpy.uint8)
    return bytedata

# called by the QwtImagePlot class
def square(n, min, max):
    t = numpy.arange(min, max, float(max-min)/(n-1))
    #return outer(cos(t), sin(t))
    return numpy.cos(t)*numpy.sin(t)[:,numpy.newaxis]
# square()


class QwtPlotImage(QwtPlotMappedItem):

    def __init__(self, parent):
        QwtPlotItem.__init__(self, parent)
        self.plot = parent
        self.display_type = "hippo"
        self.ValueAxis =  None
        self.ComplexColorMap = None
	self._flags_array = None
	self._nan_flags_array = None
        self._image_for_display = None
	self._display_flags = False
        self.Qimage = None
        self.r_cmax = None
        self.r_cmin = None
        self.i_cmax = None
        self.i_cmin = None
        self.dimap = None
        self.complex = False
        self.log_scale = False
        self.log_y_scale = False
        self.transform_offset = 0.0
        self.flag_colour = 0
        self.nan_colour = 255
        self.lock_image_real = False
        self.lock_image_imag = False
    # __init__()
    
    def setDisplayType(self, display_type):
      self.display_type = display_type
#     _dprint(2,'display type set to ', self.display_type);
      if self.display_type == "brentjens" and self.ValueAxis == None:
        self.ValueAxis =  UVPAxis()
        self.ComplexColorMap = ComplexColorMap(256)
    # setDisplayType

    def setFlagColour(self, flag_colour):
      self.flag_colour = flag_colour

    def setLockImage(self, real = True, lock_image=False):
      if real:
        self.lock_image_real = lock_image
      else:
        self.lock_image_imag = lock_image

    # When set to True, the log_scale parameter will cause
    # the displayed image to be scaled logarithmically.
    def setLogScale(self, log_scale = True):
      self.log_scale = log_scale
      if self.log_scale == False:
        self.dimap = None
        self.transform_offset = 0.0

    # When set to True, the log_y_scale parameter will cause
    # the output Y coordinate axis to be scaled properly for a Log plot
    # (used by QwtColorBar.py)
    def setLogYScale(self, log_y_scale = True):
      self.log_y_scale = log_y_scale

    def setFlagsArray(self, flags_array):
      self._flags_array = flags_array

    def setNanFlagsArray(self, flags_array):
      self._nan_flags_array = flags_array
      
      
    def setDisplayFlag(self, display_flags):
        self._display_flags = display_flags
    # setDisplayFlag

    def removeFlags(self):
      self._flags_array = None
      self._nan_flags_array = None
    # removeFlags

    def getRealImageRange(self):
        return (self.r_cmin, self.r_cmax)
    # getRealImageRange

    def getImagImageRange(self):
        return (self.i_cmin, self.i_cmax)
    # getRealImageRange
    
    def defineImageRange(self, limits, real=True):
       min = limits[0]
       max = limits[1]
       if abs(max - min) < 0.00005:
         if max == 0.0 or min == 0.0:
           min = -0.1
           max = 0.1
         else:
           min = 0.9 * min
           max = 1.1 * max
       if min > max:
         temp = max
         max = min
         min = temp
       if real:
         if not self.lock_image_real:
           self.r_cmin = min
           self.r_cmax = max
       else:
         if not self.lock_image_imag:
           self.i_cmin = min
           self.i_cmax = max

    def setImageRange(self, image):
      if image.dtype == numpy.complex64 or image.dtype == numpy.complex128:
        self.complex = True
        imag_array =  image.imag
        real_array =  image.real
        min = real_array.min()
        max = real_array.max()
        if abs(max - min) < 0.00005:
          if max == 0.0 or min == 0.0:
            min = -0.1
            max = 0.1
          else:
            min = 0.9 * min
            max = 1.1 * max
        if min > max:
          temp = max
          max = min
          min = temp
        if not self.lock_image_real:
          self.r_cmin = min
          self.r_cmax = max

        min = imag_array.min()
        max = imag_array.max()
        if abs(max - min) < 0.00005:
          if max == 0.0 or min == 0.0:
            min = -0.1
            max = 0.1
          else:
            min = 0.9 * min
            max = 1.1 * max
        if min > max:
          temp = max
          max = min
          min = temp
        if not self.lock_image_imag:
          self.i_cmin = min
          self.i_cmax = max
      else:
        self.complex = False
        min = image.min()
        max = image.max()
        if abs(max - min) < 0.00005:
          if max == 0.0 or min == 0.0:
            min = -0.1
            max = 0.1
          else:
            min = 0.9 * min
            max = 1.1 * max
        if min > max:
          temp = max
          max = min
          min = temp
        if not self.lock_image_real:
          self.r_cmin = min
          self.r_cmax = max
    # setImageRange

    def updateImage(self, image):
        self.setImage(image)
        self.raw_image = image

    def setFlaggedImageRange(self):
      (nx,ny) = self.raw_image.shape
      num_elements = nx * ny
      flags_array = self._flags_array.copy()
      if not self._nan_flags_array is None:
        flags_array = flags_array + self._nan_flags_array
      flattened_flags = numpy.reshape(flags_array,(num_elements,))
      if self.raw_image.dtype == numpy.complex64 or self.raw_image.dtype == numpy.complex128:
        real_array =  self.raw_image.real
        imag_array =  self.raw_image.imag
        flattened_real_array = numpy.reshape(real_array.copy(),(num_elements,))
        flattened_imag_array = numpy.reshape(imag_array.copy(),(num_elements,))
        real_flagged_array = numpy.compress(flattened_flags == 0, flattened_real_array)
        imag_flagged_array = numpy.compress(flattened_flags == 0, flattened_imag_array)
        flagged_image = numpy.zeros(shape=real_flagged_array.shape,dtype=self.raw_image.dtype)
        flagged_image.real = real_flagged_array
        flagged_image.imag = imag_flagged_array
      else:
        flattened_array = numpy.reshape(self.raw_image.copy(),(num_elements,))
        flagged_image = numpy.compress(flattened_flags == 0, flattened_array)
      self.setImageRange(flagged_image)
    # setFlaggedImageRange

    def convert_to_log(self, incoming_image):
      self.transform_offset = 0.0
      transform_image = incoming_image
      image_min = incoming_image.min()
      if image_min <= 0.0:
        image_min = -1.0 * image_min
        self.transform_offset = 0.001 + image_min
        transform_image = self.transform_offset + incoming_image
      scale_min = transform_image.min()
      scale_max = transform_image.max()
      if scale_min == scale_max:
       scale_min = scale_min - 0.5 * scale_min
       scale_max = scale_max + 0.5 * scale_min
      scaler = ImageScaler(1, 256, scale_min, scale_max, True)
      self.dimap = QwtDiMap(1, 256, scale_min, scale_max, True)
      _dprint(3, 'doing log transform of ', transform_image)
      temp_image = scaler.iTransform(transform_image)
      _dprint(3, 'log transformed image ', temp_image)
      return temp_image

    def getTransformOffset(self):
      return self.transform_offset

    def convert_limits(self, limits):
      if not self.dimap is None:
        first_limit = self.dimap.transform(self.transform_offset + limits[0])
        second_limit = self.dimap.transform(self.transform_offset + limits[1])
      else:
        first_limit = None
        second_limit = None
      return [first_limit, second_limit]

    def to_QImage(self, image):
# convert to 8 bit image
      image_for_display = None
      if image.dtype == numpy.complex64 or image.dtype == numpy.complex128:
        self.complex = True
        real_array =  image.real
        if self.log_scale:
          temp_array = self.convert_to_log(real_array)
          if not self.r_cmin is None and not self.r_cmax is None:
            limits = self.convert_limits([self.r_cmin,self.r_cmax])
          else:
            limits = [self.r_cmin, self.r_cmax] 
          byte_image = bytescale(temp_array,limits)
        else:
          limits = [self.r_cmin,self.r_cmax]
          byte_image = bytescale(real_array,limits)
        (nx,ny) = real_array.shape
        image_for_display = numpy.empty(shape=(nx*2,ny),dtype=byte_image.dtype);
        image_for_display[:nx,:] = byte_image
        imag_array =  image.imag
        if self.log_scale:
          temp_array = self.convert_to_log(imag_array)
          if not self.i_cmin is None and not self.i_cmax is None:
            limits = self.convert_limits([self.i_cmin,self.i_cmax])
          else:
            limits = [self.i_cmin, self.i_cmax] 
          byte_image = bytescale(temp_array,limits)
        else:
          limits = [self.i_cmin,self.i_cmax]
          byte_image = bytescale(imag_array,limits)
        image_for_display[nx:,:] = byte_image
      else:
        if self.log_scale:
          temp_array = self.convert_to_log(image)
          if not self.r_cmin is None and not self.r_cmax is None:
            limits = self.convert_limits([self.r_cmin,self.r_cmax])
          else:
            limits = [self.r_cmin, self.r_cmax] 
          image_for_display = bytescale(temp_array,limits)
        else:
          limits = [self.r_cmin,self.r_cmax]
          image_for_display = bytescale(image,limits)
# turn image into a QImage, and return result	
      if not self._nan_flags_array is None:
        if self.complex:
          image_for_display[:nx,:] = numpy.where(self._nan_flags_array,1,image_for_display[:nx,:])
          image_for_display[nx:,:] = numpy.where(self._nan_flags_array,1,image_for_display[nx:,:])
        else:
          image_for_display = numpy.where(self._nan_flags_array,1,image_for_display)
      self._image_for_display = image_for_display
      result = toQImage(image_for_display).mirror(0, 1)
      if not self._nan_flags_array is None:
        result.setColor(1, qRgb(self.nan_colour, self.nan_colour, self.nan_colour))
      return result

    def toGrayScale(self, Qimage):
      for i in range(0, 256):
        Qimage.setColor(i, qRgb(i, i, i))

    def toHippo(self, Qimage):
      dv = 255.0
      vmin = 1.0
      for i in range(2, 256):
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
        Qimage.setColor(i, qRgb(red, green, blue))

    def setImage(self, image):
# convert to QImage
      self.Qimage = self.to_QImage(image)
# set color scale a la HippoDraw Scale
      if self.display_type == "hippo":
        self.toHippo(self.Qimage)

# set color scale to Grayscale
      if self.display_type == "grayscale":
        self.toGrayScale(self.Qimage)

# compute flagged image if required
      if not self._flags_array is None or not self._nan_flags_array is None:
        self.setFlagQimage()

    def setFlagQimage(self):
      (nx,ny) = self._image_for_display.shape
      image_for_display = self._image_for_display.copy()
      if not self._flags_array is None:
        if self.complex:
          image_for_display[:nx/2,:] = numpy.where(self._flags_array,0,self._image_for_display[:nx/2,:])
          image_for_display[nx/2:,:] = numpy.where(self._flags_array,0,self._image_for_display[nx/2:,:])
        else:
          image_for_display = numpy.where(self._flags_array,0,self._image_for_display)
      if not self._nan_flags_array is None:
        if self.complex:
          image_for_display[:nx/2,:] = numpy.where(self._nan_flags_array,1,image_for_display[:nx/2,:])
          image_for_display[nx/2:,:] = numpy.where(self._nan_flags_array,1,image_for_display[nx/2:,:])
        else:
          image_for_display = numpy.where(self._nan_flags_array,1,image_for_display)

      self.flags_Qimage = toQImage(image_for_display).mirror(0, 1)

# set color scale a la HippoDraw Scale
      if self.display_type == "hippo":
        self.toHippo(self.flags_Qimage)

# set color scale to Grayscale
      if self.display_type == "grayscale":
        self.toGrayScale(self.flags_Qimage)

# set zero to black to display flag image pixels in black 
      self.flags_Qimage.setColor(0, qRgb(self.flag_colour, self.flag_colour, self.flag_colour))
      self.flags_Qimage.setColor(1, qRgb(self.nan_colour, self.nan_colour, self.nan_colour))

    def setBrentjensImage(self, image):
      absmin = abs(image.min())
      MaxAbs = abs(image.max())
      if (absmin > MaxAbs):
        MaxAbs = absmin
      self.ValueAxis.calcTransferFunction(-MaxAbs, MaxAbs, 0, self.ComplexColorMap.getNumberOfColors()-1)

      if image.min() != image.max():
# get real and imaginary arrays
        real_image = image.real
        imag_image = image.imag
        shape = image.shape
        Ncol = self.ComplexColorMap.getNumberOfColors()
        bits_per_pixel = 32
        self.Qimage = QImage(shape[0], shape[1], bits_per_pixel, Ncol)
        for i in range(shape[0]):
          for j in range(shape[1]):
            colre = int(self.ValueAxis.worldToAxis(real_image[i,j]))
            colim = int(self.ValueAxis.worldToAxis(imag_image[i,j]))
            if(colre < Ncol and colim < Ncol): 
              value = self.ComplexColorMap.get_color_value(colre,colim)
              self.Qimage.setPixel(i,j,value)
            else:
              _dprint(2, "*************************************");
              _dprint(2, "colre: ", colre);
              _dprint(2, "colim: ", colim);
              _dprint(2, "real : ", real_image[i,j]);
              _dprint(2, "imag : ", imag_image[i,j]);
              _dprint(2, "Ncol: ", Ncol);
              _dprint(2, "*************************************");
        self.Qimage.mirror(0,1)

    def setData(self, data_array, xScale = None, yScale = None):
        self.complex = False
        shape = data_array.shape
        _dprint(3, 'array shape is ', shape)
        shape0 = shape[0]
        if data_array.dtype == numpy.complex64 or data_array.dtype == numpy.complex128:
          self.complex = True
          shape0 = 2 * shape[0]
        if xScale:
#           self.xMap = QwtDiMap(0, shape0, xScale[0], xScale[1])
            self.xMap = QwtDiMap(0, shape0 - 1, xScale[0], xScale[1])
#           self.plot.setAxisScale(QwtPlot.xBottom, *xScale)
            temp_scale = (xScale[0],xScale[1])
            self.plot.setAxisScale(QwtPlot.xBottom, *temp_scale)
            _dprint(3, 'xScale is ', xScale)
        else:
            self.xMap = QwtDiMap(0, shape0, 0, shape0 )
            self.plot.setAxisScale(QwtPlot.xBottom, 0, shape0)
        if yScale:
            _dprint(3, 'yScale is ', yScale)
            _dprint(3, 'self.log_y_scale is ', self.log_y_scale)
#           self.yMap = QwtDiMap(0, shape[1], yScale[0], yScale[1], self.log_y_scale)
            self.yMap = QwtDiMap(0, shape[1]-1, yScale[0], yScale[1], self.log_y_scale)
#           self.plot.setAxisScale(QwtPlot.yLeft, *yScale)
            temp_scale = (yScale[0],yScale[1])
            _dprint(3, 'Called setAxisScale(QwtPlot.yLeft) with ', temp_scale)
            self.plot.setAxisScale(QwtPlot.yLeft, *temp_scale)
        else:
            self.yMap = QwtDiMap(0, shape[1], 0, shape[1])
            self.plot.setAxisScale(QwtPlot.yLeft, 0, shape[1])
        if self.display_type == "brentjens":
          self.setBrentjensImage(data_array)
        else:
          self.setImage(data_array)
        self.raw_image = data_array
    # setData()    

    def drawImage(self, painter, xMap, yMap):
        """Paint image to zooming to xMap, yMap

        Calculate (x1, y1, x2, y2) so that it contains at least 1 pixel,
        and copy the visible region to scale it to the canvas.
        """
        if self.Qimage is None:
          return

        _dprint(3, 'incoming x map ranges ',xMap.d1(), ' ', xMap.d2())
        _dprint(3, 'incoming y map ranges ',yMap.d1(), ' ', yMap.d2())
        # calculate y1, y2
        y1 = y2 = self.Qimage.height()
        _dprint(3, 'image height ', self.Qimage.height())
#        y1 = y2 = self.Qimage.height() - 1
#        print 'starting image height ', y1
        y1 *= (self.yMap.d2() - yMap.d2())
        y1 /= (self.yMap.d2() - self.yMap.d1())
#       y1 = max(0, int(y1-0.5))
        y1 = max(0, (y1-0.5))
        _dprint(3, 'float y1 ', y1)
        y1 = int(y1 + 0.5)
        y2 *= (self.yMap.d2() - yMap.d1())
        y2 /= (self.yMap.d2() - self.yMap.d1())
        _dprint(3, 'float y2 ', y2)
#       y2 = min(self.Qimage.height(), int(y2+0.5))
        y2 = min(self.Qimage.height(), (y2+0.5))
        y2 = int(y2)
        _dprint(3, 'int y1, y2 ', y1, ' ',y2)
        # calculate x1, x2 - these are OK
        x1 = x2 = self.Qimage.width() 
#       print 'starting image width ', x1
        x1 *= (xMap.d1() - self.xMap.d1())
        x1 /= (self.xMap.d2() - self.xMap.d1())
        _dprint(3, 'float x1 ', x1)
#       x1 = max(0, int(x1-0.5))
        x1 = max(0, int(x1))
        x2 *= (xMap.d2() - self.xMap.d1())
        x2 /= (self.xMap.d2() - self.xMap.d1())
        _dprint(3, 'float x2 ', x2)
        x2 = min(self.Qimage.width(), int(x2+0.5))
        _dprint(3, 'int x1, x2 ', x1, ' ',x2)
        # copy
        xdelta = x2-x1
        ydelta = y2-y1
        # these tests seem necessary for the dummy 'scalar' displays
        if xdelta < 0:
          xdelta = self.Qimage.height()
        if ydelta < 0:
          ydelta = self.Qimage.height()
	image = None
        if self._display_flags:
          image = self.flags_Qimage.copy(x1, y1, xdelta, ydelta)
        else:
          image = self.Qimage.copy(x1, y1, xdelta, ydelta)
        # zoom
        image = image.smoothScale(xMap.i2()-xMap.i1()+1, yMap.i1()-yMap.i2()+1)
        # draw
        painter.drawImage(xMap.i1(), yMap.i2(), image)

    # drawImage()

# QwtPlotImage()

# we test the QwtPlotImage class with class QwtImagePlot

class QwtImagePlot(QwtPlot):
    def __init__(self, *args):
        QwtPlot.__init__(self, *args)
	# make a QwtPlot widget
        self.plotLayout().setMargin(0)
        self.plotLayout().setCanvasMargin(0)
        self.plotLayout().setAlignCanvasToScales(1)
	self.setTitle('QwtImagePlot: (un)zoom & (un)hide')
        self.setAutoLegend(0)
	# set axis titles
	self.setAxisTitle(QwtPlot.xBottom, 'time (s)')
	self.setAxisTitle(QwtPlot.yLeft, 'frequency (Hz)')
	# insert a few curves
	self.cSin = self.insertCurve('y = pi*sin(x)')
	self.cCos = self.insertCurve('y = 4*pi*sin(x)*cos(x)**2')
	# set curve styles
	self.setCurvePen(self.cSin, QPen(Qt.green, 2))
	self.setCurvePen(self.cCos, QPen(Qt.black, 2))

        # create and initialize an image display
        self.plotImage = QwtPlotImage(self)
        self.gain = 2.0
        self.updateDisplay()

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
        
        # replot

    # __init__()

    def updateDisplay(self):
      # calculate 3 NumPy arrays
      x = numpy.arange(-1.0 * self.gain*math.pi, self.gain*math.pi, 0.01)
      y = math.pi*numpy.sin(x)
      z = self.gain * self.gain*math.pi*numpy.cos(x)*numpy.cos(x)*numpy.sin(x)
      # copy the data
      self.setCurveData(self.cSin, x, y)
      self.setCurveData(self.cCos, x, z)
      # image
      self.plotImage.setData(
            square(512,-1.0 * self.gain*math.pi, self.gain*math.pi), (-1.0*self.gain*math.pi, self.gain*math.pi), (-1.0*self.gain*math.pi, self.gain*math.pi))

    def start_timer(self, time):
      """ start a timer going to update the image every 1/10 sec """
      self.timer = QTimer(self)
      self.timer.connect(self.timer, SIGNAL('timeout()'), self.testEvent)
      self.timer.start(time)

    def testEvent(self):
      """ change the gain factor and recalculate the image """
      self.gain = self.gain + 1.0
      self.updateDisplay()
      self.replot()


    def drawCanvasItems(self, painter, rectangle, maps, filter):
        self.plotImage.drawImage(
            painter, maps[QwtPlot.xBottom], maps[QwtPlot.yLeft])
        QwtPlot.drawCanvasItems(self, painter, rectangle, maps, filter)

    # drawCanvasItems()

    def onMouseMoved(self, e):
        pass

    # onMouseMoved()

    def onMousePressed(self, e):
        if Qt.LeftButton == e.button():
            # Python semantics: self.pos = e.pos() does not work; force a copy
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
            self.zooming = 0
        # fake a mouse move to show the cursor position
        self.onMouseMoved(e)

    # onMousePressed()

    def onMouseReleased(self, e):
        if Qt.LeftButton == e.button():
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

        if Qt.LeftButton == e.button() or Qt.RightButton == e.button():
          self.setAxisScale(QwtPlot.xBottom, xmin, xmax)
          self.setAxisScale(QwtPlot.yLeft, ymin, ymax)
          self.replot()

    # onMouseReleased()

    def toggleCurve(self, key):
        curve = self.curve(key)
        if curve:
            curve.setEnabled(not curve.enabled())
            self.replot()

    # toggleCurve()

# class QwtImagePlot


def make():
    demo = QwtImagePlot()
    demo.resize(500, 300)
#   demo.start_timer(500)
    demo.show()
    return demo

# make()

def main(args):
    app = QApplication(args)
    demo = make()
    app.setMainWidget(demo)
    app.exec_loop()

# main()

# Admire
if __name__ == '__main__':
    main(sys.argv)




