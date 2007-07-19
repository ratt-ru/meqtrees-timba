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
from numarray import *
from UVPAxis import *
from ImageScaler import *
from ComplexColorMap import *

from Timba.utils import verbosity
_dbg = verbosity(0,name='QwtPlotImage');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;


# from scipy.pilutil
# note: low is set to 1, so that we can save a value of 0 for a flagged pixel
def bytescale(data, limits, high=255, low=1):
    if data.type() == UInt8:
        return data
    high = high - low
    if limits[0] is None:
        limits[0] = data.min()
    if limits[1] is None:
        limits[1] = data.max()
    scale = high *1.0 / (limits[1]-limits[0] or 1)
    internal_data = data.copy()
    temp1 = less_equal(data,limits[1])
    temp2 = greater(data,limits[1])
    internal_data = data * temp1 + temp2 * limits[1]
    temp1 = greater_equal(internal_data,limits[0])
    temp2 = less(internal_data,limits[0])
    internal_data = internal_data * temp1 + temp2 * limits[0]
    bytedata = ((internal_data*1.0-limits[0])*scale + 0.4999).astype(UInt8) + asarray(low).astype(UInt8)
    return bytedata

class QwtPlotImage(QwtPlotMappedItem):

    def __init__(self, parent):
        QwtPlotItem.__init__(self, parent)
        self.plot = parent
        self.display_type = "hippo"
        self.ValueAxis =  None
        self.ComplexColorMap = None
	self._flags_array = None
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
    # __init__()
    
    def setDisplayType(self, display_type):
      self.display_type = display_type
#     _dprint(2,'display type set to ', self.display_type);
      if self.display_type == "brentjens" and self.ValueAxis == None:
        self.ValueAxis =  UVPAxis()
        self.ComplexColorMap = ComplexColorMap(256)
    # setDisplayType

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
      
    def setDisplayFlag(self, display_flags):
        self._display_flags = display_flags
    # setDisplayFlag

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
         self.r_cmin = min
         self.r_cmax = max
       else:
         self.i_cmin = min
         self.i_cmax = max

    def setImageRange(self, image):
      if image.type() == Complex32 or image.type() == Complex64:
        self.complex = True
        imag_array =  image.getimag()
        real_array =  image.getreal()
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
        self.r_cmin = min
        self.r_cmax = max
    # setImageRange

    def updateImage(self, image):
        self.setImage(image)
        self.raw_image = image

    def setFlaggedImageRange(self):
      if self.raw_image.type() == Complex32 or self.raw_image.type() == Complex64:
        (nx,ny) = self.raw_image.shape
        real_array =  self.raw_image.getreal()
        imag_array =  self.raw_image.getimag()
        real_flagged_array = real_array - self._flags_array * real_array
        imag_flagged_array = imag_array - self._flags_array * imag_array
        flagged_image = array(shape=(nx,ny),type=self.raw_image.type())
        flagged_image.setreal(real_flagged_array)
        flagged_image.setimag(imag_flagged_array)
      else:
        flagged_image = self.raw_image - self._flags_array * self.raw_image
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
      if image.type() == Complex32 or image.type() == Complex64:
        self.complex = True
        real_array =  image.getreal()
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
        image_for_display = array(shape=(nx*2,ny),type=byte_image.type());
        image_for_display[:nx,:] = byte_image
        imag_array =  image.getimag()
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
      self._image_for_display = image_for_display
      return toQImage(image_for_display).mirror(0, 1)

    def toGrayScale(self, Qimage):
      for i in range(0, 256):
        Qimage.setColor(i, qRgb(i, i, i))

    def toHippo(self, Qimage):
      dv = 255.0
      vmin = 1.0
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
      if not self._flags_array is None:
        self.setFlagQimage()

    def setFlagQimage(self):
      (nx,ny) = self._image_for_display.shape
      image_for_display = array(shape=(nx,ny),type=self._image_for_display.type())
      if self.complex:
        image_for_display[:nx/2,:] = where(self._flags_array,0,self._image_for_display[:nx/2,:])
        image_for_display[nx/2:,:] = where(self._flags_array,0,self._image_for_display[nx/2:,:])
      else:
        image_for_display = where(self._flags_array,0,self._image_for_display)

      self.flags_Qimage = toQImage(image_for_display).mirror(0, 1)

# set color scale a la HippoDraw Scale
      if self.display_type == "hippo":
        self.toHippo(self.flags_Qimage)

# set color scale to Grayscale
      if self.display_type == "grayscale":
        self.toGrayScale(self.flags_Qimage)

# set zero to black to display flag image pixels in black 
      self.flags_Qimage.setColor(0, qRgb(0, 0, 0))

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
        if data_array.type() == Complex32 or data_array.type() == Complex64:
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
