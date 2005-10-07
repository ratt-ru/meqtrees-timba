#!/usr/bin/env python

#
# The QwtPlotImage class is just a straightforward adaption of 
# the same class in PyQwt-4.2/examples/QwtImagePlotDemo.py.
# The class has been modified to work with the color maps
# used for MeqTrees and also to display flagged arrays.
# The coordinate functions have also been modified to give
# increased accuracy for zooming, etc.

import sys
from qt import *
from qwt import *
from numarray import *
from UVPAxis import *
from ComplexColorMap import *

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
	self._display_flags = False
        self.image = None
        self.cmax = None
        self.cmin = None
    # __init__()
    
    def setDisplayType(self, display_type):
        self.display_type = display_type
#       _dprint(2,'display type set to ', self.display_type);
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

    def getImageRange(self):
        return (self.cmin, self.cmax)
    # getImageRange

    def setImageRange(self, limits):
        self.cmin = limits[0]
        self.cmax = limits[1]
    # setImageRange

    def setFlaggedImageRange(self, limits):
      print 'flagged limits are ', limits[0], limits[1]
      self.cmin = limits[0]
      self.cmax = limits[1]
    # setImageRange

    def setImage(self, image):
# turn image into a QImage	
        limits = [self.cmin,self.cmax]
        byte_image = bytescale(image,limits)
        self.image = toQImage(byte_image).mirror(0, 1)
        self.flags_image = None

# set color scale a la HippoDraw Scale
        if self.display_type == "hippo":
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
            self.image.setColor(i, qRgb(red, green, blue))

# the following call will set up gray scale
        if self.display_type == "grayscale":
          for i in range(0, 256):
            self.image.setColor(i, qRgb(i, i, i))

# compute flagged image
        if not self._flags_array is None:
 	  self.flags_image =  self.image.copy()
          n_rows = self._flags_array.shape[0]
          n_cols = self._flags_array.shape[1]
	  for j in range(0, n_rows ) :
	    for i in range(0, n_cols) :
# display is mirrored in vertical direction	    
	      mirror_col = n_cols-1-i
	      if self._flags_array[j][i] > 0:
 	        self.flags_image.setPixel(j,mirror_col,0)
# display flag image pixels in black 
          self.flags_image.setColor(0, qRgb(0, 0, 0))

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
#           self.plot.setAxisScale(QwtPlot.xBottom, *xScale)
            temp_scale = (xScale[0],xScale[1])
            self.plot.setAxisScale(QwtPlot.xBottom, *temp_scale)
        else:
            self.xMap = QwtDiMap(0, shape[0], 0, shape[0] )
            self.plot.setAxisScale(QwtPlot.xBottom, 0, shape[0])
        if yScale:
#           self.yMap = QwtDiMap(0, shape[1], yScale[0], yScale[1])
            self.yMap = QwtDiMap(0, shape[1]-1, yScale[0], yScale[1])
#           self.plot.setAxisScale(QwtPlot.yLeft, *yScale)
            temp_scale = (yScale[0],yScale[1])
            self.plot.setAxisScale(QwtPlot.yLeft, *temp_scale)
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

#       print 'in drawImage'
#       print 'incoming x map ranges ',xMap.d1(), ' ', xMap.d2()
#       print 'incoming y map ranges ',yMap.d1(), ' ', yMap.d2()
        # calculate y1, y2
        y1 = y2 = self.image.height()
#       print 'image height ', self.image.height()
#        y1 = y2 = self.image.height() - 1
#        print 'starting image height ', y1
        y1 *= (self.yMap.d2() - yMap.d2())
        y1 /= (self.yMap.d2() - self.yMap.d1())
#       y1 = max(0, int(y1-0.5))
        y1 = max(0, (y1-0.5))
#       print 'float y1 ', y1
        y1 = int(y1 + 0.5)
        y2 *= (self.yMap.d2() - yMap.d1())
        y2 /= (self.yMap.d2() - self.yMap.d1())
#       print 'float y2 ', y2
#       y2 = min(self.image.height(), int(y2+0.5))
        y2 = min(self.image.height(), (y2+0.5))
        y2 = int(y2)
#       print 'int y1, y2 ', y1, ' ', y2
        # calculate x1, x2 - these are OK
        x1 = x2 = self.image.width() 
#       print 'starting image width ', x1
        x1 *= (xMap.d1() - self.xMap.d1())
        x1 /= (self.xMap.d2() - self.xMap.d1())
#       print 'float x1 ', x1
#       x1 = max(0, int(x1-0.5))
        x1 = max(0, int(x1))
        x2 *= (xMap.d2() - self.xMap.d1())
        x2 /= (self.xMap.d2() - self.xMap.d1())
#       print 'float x2 ', x2
        x2 = min(self.image.width(), int(x2+0.5))
#       print 'x1, x2 ', x1, ' ', x2
        # copy
	image = None
	if self._display_flags:
          image = self.flags_image.copy(x1, y1, x2-x1, y2-y1)
	else:
          image = self.image.copy(x1, y1, x2-x1, y2-y1)
        # zoom
        image = image.smoothScale(xMap.i2()-xMap.i1()+1, yMap.i1()-yMap.i2()+1)
        # draw
        painter.drawImage(xMap.i1(), yMap.i2(), image)

    # drawImage()

# QwtPlotImage()
