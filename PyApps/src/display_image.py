#!/usr/bin/env python

import sys
from qt import *
from qwt import *
from numarray import *
from UVPAxis import *
from ComplexColorMap import *
import random

from dmitypes import verbosity
_dbg = verbosity(0,name='realvsimag');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;


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

    # __init__()
    
    def setDisplayType(self, display_type):
        self.display_type = display_type
        _dprint(2,'display type set to ', self.display_type)
        if self.display_type == "brentjens" and self.ValueAxis == None:
          self.ValueAxis =  UVPAxis()
          self.ComplexColorMap = ComplexColorMap(256)
    # setDisplayType

    def setImage(self, image):
        byte_image = bytescale(image)
        byte_range = 1.0 * (byte_image.max() - byte_image.min())
        byte_min = 1.0 * (byte_image.min())
        self.image = toQImage(byte_image).mirror(0, 1)

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
              g = 4 * (v - vmin) / dv;
            elif (v < (vmin + 0.5 * dv)):
              r = 0;
              b = 1 + 4 * (vmin + 0.25 * dv - v) / dv;
            elif (v < (vmin + 0.75 * dv)):
              r = 4 * (v - vmin - 0.5 * dv) / dv;
              b = 0;
            else: 
              g = 1 + 4 * (vmin + 0.75 * dv - v) / dv;
              b = 0;
            red   = int ( r * 255. )
            green = int ( g * 255. )
            blue  = int ( b * 255. )
# the following call will use the previosu computations to
# set up a hippo-like color display
            self.image.setColor(i, qRgb(red, green, blue))

# the following call will set up gray scale
        if self.display_type == "grayscale":
          for i in range(0, 256):
            self.image.setColor(i, qRgb(i, i, i))

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
              _dprint(2, "*************************************") 
              _dprint(2, "colre: ", colre)
              _dprint(2, "colim: ", colim) 
              _dprint(2, "real : ", real_image[i,j])
              _dprint(2, "imag : ", imag_image[i,j])
              _dprint(2, "Ncol: ", Ncol)
              _dprint(2, "*************************************") 
        self.image.mirror(0,1)

    def setData(self, xyzs, xScale = None, yScale = None):
        shape = xyzs.shape
        if xScale:
            self.xMap = QwtDiMap(0, shape[0], xScale[0], xScale[1])
            self.plot.setAxisScale(QwtPlot.xBottom, *xScale)
        else:
            self.xMap = QwtDiMap(0, shape[0], 0, shape[0] )
            self.plot.setAxisScale(QwtPlot.xBottom, 0, shape[0])
        if yScale:
            self.yMap = QwtDiMap(0, shape[1], yScale[0], yScale[1])
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
        # calculate y1, y2
        y1 = y2 = self.image.height()
        y1 *= (self.yMap.d2() - yMap.d2())
        y1 /= (self.yMap.d2() - self.yMap.d1())
        y1 = max(0, int(y1-0.5))
        y2 *= (self.yMap.d2() - yMap.d1())
        y2 /= (self.yMap.d2() - self.yMap.d1())
        y2 = min(self.image.height(), int(y2+0.5))
        # calculate x1, x1
        x1 = x2 = self.image.width()
        x1 *= (xMap.d1() - self.xMap.d1())
        x1 /= (self.xMap.d2() - self.xMap.d1())
        x1 = max(0, int(x1-0.5))
        x2 *= (xMap.d2() - self.xMap.d1())
        x2 /= (self.xMap.d2() - self.xMap.d1())
        x2 = min(self.image.width(), int(x2+0.5))
        # copy
        image = self.image.copy(x1, y1, x2-x1, y2-y1)
        # zoom
        image = image.smoothScale(xMap.i2()-xMap.i1()+1, yMap.i1()-yMap.i2()+1)
        # draw
        painter.drawImage(xMap.i1(), yMap.i2(), image)

    # drawImage()

# QwtPlotImage()
    
class QwtImagePlot(QwtPlot):

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

    display_table = {
        'hippo': 'hippo',
        'grayscale': 'grayscale',
        'brentjens': 'brentjens',
        }

    def __init__(self, plot_key=None, parent=None):
        QwtPlot.__init__(self, plot_key, parent)

# set default display type to 'hippo'
        self.display_type = "hippo"

# save raw data
        self.plot_key = plot_key
        self.x_array = None
        self.y_array = None
        self.x_index = None
	# make a QwtPlot widget
        self.plotLayout().setMargin(0)
        self.plotLayout().setCanvasMargin(0)
        self.plotLayout().setAlignCanvasToScales(1)
	self.setTitle('QwtImagePlot: demo')
#        self.setAutoLegend(1)
#        self.setLegendPos(Qwt.Right)
	# set default axis titles
	self.setAxisTitle(QwtPlot.xBottom, 'Channel Number')
	self.setAxisTitle(QwtPlot.yLeft, 'time (s)')
        self.x_axis_title_set_in_plot_data = False
	# insert a few curves
	self.xCrossSection = self.insertCurve('xCrossSection')
	self.yCrossSection = self.insertCurve('yCrossSection')
        self.enableAxis(QwtPlot.yRight)
        self.setAxisTitle(QwtPlot.yRight, 'signal')
	# set curve styles
	self.setCurvePen(self.xCrossSection, QPen(Qt.black, 2))
	self.setCurvePen(self.yCrossSection, QPen(Qt.red, 2))
        self.setCurveYAxis(self.xCrossSection, QwtPlot.yRight)
        self.setAxisAutoScale(QwtPlot.yRight)

	# insert a horizontal marker at y = 0
#	mY = self.insertLineMarker('y = 0', QwtPlot.yLeft)
#	self.setMarkerYPos(mY, 0.0)
	# insert a vertical marker at x = pi
#	mX = self.insertLineMarker('x = pi', QwtPlot.xBottom)
#	self.setMarkerXPos(mX, pi)

#        self.connect(
#            self.__colorBar, PYSIGNAL("colorSelected"), self.setCanvasColor)

        self.plotImage = QwtPlotImage(self)

#        scale = self.axis(QwtPlot.yLeft)
#        scale.setBaselineDist(10)
#        self.__colorBar = ColorBar(Qt.Vertical, scale)
#        self.__colorBar.setRange(Qt.red, Qt.darkBlue)
#        self.__colorBar.setFocusPolicy(QWidget.TabFocus)
#        QWhatsThis.add(
#            self.__colorBar,
#            'Selecting a color will change the background of the plot.')
        #self.plotImage.setData(bytescale(linearX(512, 512)+linearY(512, 512)))

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
        self.first_plot = True
        self.is_vector = False
        self.x_dim = 0
        self.y_dim = 0

    def drawCanvasItems(self, painter, rectangle, maps, filter):
        if self.first_plot == False:
          if self.is_vector == False:
            self.plotImage.drawImage(
              painter, maps[QwtPlot.xBottom], maps[QwtPlot.yLeft])
          QwtPlot.drawCanvasItems(self, painter, rectangle, maps, filter)
        else:
          self.first_plot = False


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
        elif Qt.MidButton == e.button():
            xpos = e.pos().x()
            ypos = e.pos().y()
            xpos = self.invTransform(QwtPlot.xBottom, xpos)
            ypos = self.invTransform(QwtPlot.yLeft, ypos)
            xpos = int(xpos)
            ypos = int(ypos)
            shape = self.raw_image.shape
            if self.x_array is None:
              self.x_array = zeros(shape[0], Float32)
              self.x_index = arange(shape[0])
              self.x_index = self.x_index + 0.5

            for i in range(shape[0]):
              self.x_array[i] = self.raw_image[i,ypos]
	    self.setCurveData(self.xCrossSection, self.x_index, self.x_array)
            self.replot()
           
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
        elif Qt.MidButton == e.button():
          return

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

    def setDisplayType(self, display_type):
      self.display_type = display_type
      self.plotImage.setDisplayType(display_type)
    # setDisplayType

    def display_image(self, image):
      if self.set_data_called == False:
        self.plotImage.setData(image)
        self.set_data_called = True
      self.raw_image = image
      if self.display_type == "brentjens":
        self.plotImage.setBrentjensImage(image)
      else:
        self.plotImage.setImage(image)
      self.replot()
    # display_image()

    def plot_data(self, item_label, visu_record):
      """ process incoming data and attributes into the
          appropriate type of plot """
      _dprint(2, 'in plot data')

# first find out what kind of plot we are making
      plot_types = None
      if visu_record.has_key('attrib'):
        self._attrib_parms = visu_record['attrib']
        plot_types = self._attrib_parms.get('plot_type')

# convert to a tuple if necessary
        if isinstance(plot_types, str):
          plot_types = (plot_types,)

      if visu_record.has_key('value'):
        self._data_values = visu_record['value']

# extract and define labels for this data item
      self._label_r = item_label + "_r"
      self._label_i = item_label + "_i"
      for j in range(len(plot_types)):
        self._plot_type = plot_types[j]
     # now generate  particular plot type
      if  self._plot_type == 'spectra':
        plot_label = self._attrib_parms.get('label','')
        num_plot_arrays = len(self._data_values)
        for i in range(0, num_plot_arrays):
          complex_type = False;
          if self._data_values[i].type() == Complex64:
            complex_type = True;
          _dprint(2, 'complex type is ', complex_type)
          if complex_type:
            data_label = plot_label +  "_" +str(i) +  "_complex" 
            if self.display_type != "brentjens":
              real_array =  self._data_values[i].getreal()
              imag_array =  self._data_values[i].getimag()
              shape = real_array.shape
              temp_array = zeros((2*shape[0],shape[1]), Float32)
              for k in range(shape[0]):
                for j in range(shape[1]):
                  temp_array[k,j] = real_array[k,j]
                  temp_array[k+shape[0],j] = imag_array[k,j]
	      self.setAxisTitle(QwtPlot.xBottom, 'Channel Number (real followed by imaginary)')
              self.x_axis_title_set_in_plot_data = True
              self.array_plot(data_label, temp_array)
            else:
              _dprint(2, "calling array_plot with complex array")
              self.array_plot(data_label, self._data_values[i])
          else:
            data_label = plot_label +  "_" +str(i) +  "_real" 
            self.array_plot(data_label, self._data_values[i])

    def array_plot (self, data_label, plot_array):
      """ figure out shape, rank etc of a spectrum array and
          plot it with an appropriate hippoDraw plot type """
# figure out type and rank of incoming array
      self.setTitle(data_label)
      self.is_vector = False;
      array_dim = len(plot_array.shape)
      array_rank = plot_array.rank
      if array_rank == 1:
        self.is_vector = True;
      n_rows = plot_array.shape[0]
      if n_rows == 1:
        self.is_vector = True
      n_cols = 1
      if array_rank == 2:
        n_cols = plot_array.shape[1]
        if n_cols == 1:
          self.is_vector = True

# test for real or complex
      complex_type = False;
      if plot_array.type() == Complex32:
        complex_type = True;
      if plot_array.type() == Complex64:
        complex_type = True;

# test if we have a 2-D array
      if self.is_vector == False:
	self.setAxisTitle(QwtPlot.yLeft, 'time (s)')
        if not self.x_axis_title_set_in_plot_data:
	  if complex_type and self.display_type != "brentjens":
	    self.setAxisTitle(QwtPlot.xBottom, 'Channel Number (real followed by imaginary)')
          else:
	    self.setAxisTitle(QwtPlot.xBottom, 'Channel Number')
        if self.x_dim != plot_array.shape[0]: 
          self.x_dim = plot_array.shape[0]
          self.set_data_called = False
        if self.y_dim != plot_array.shape[1]: 
          self.y_dim = plot_array.shape[1]
          self.set_data_called = False
        self.display_image(plot_array)

      if self.is_vector == True:
        flattened_array = None
        if not self.x_axis_title_set_in_plot_data:
	  self.setAxisTitle(QwtPlot.xBottom, 'Channel Number')
# set this flag in case an image follows
        self.set_data_called = False
# make sure we are autoscaling in case an image was previous
        self.setAxisAutoScale(QwtPlot.xBottom)
        self.setAxisAutoScale(QwtPlot.yLeft)
        self.setAxisAutoScale(QwtPlot.yRight)
        num_elements = n_rows*n_cols
        flattened_array = reshape(plot_array,(num_elements,))
# we have a complex vector
	if complex_type:
	  self.setAxisTitle(QwtPlot.yLeft, 'Signal: real(black) imaginary(red)')
          if self.display_type == "brentjens":
            self.x_array =  flattened_array.getreal()
            self.y_array =  flattened_array.getimag()
            if self.x_index is None:
              self.x_index = arange(num_elements)
              self.x_index = self.x_index + 0.5
          else:
            num_elements = num_elements / 2
            if self.x_array is None:
              self.x_array = zeros(num_elements, Float32)
              self.y_array = zeros(num_elements, Float32)
              self.x_index = arange(num_elements)
              self.x_index = self.x_index + 0.5
            for i in range(num_elements):
              self.x_array[i] =  flattened_array[i]
              self.y_array[i] =  flattened_array[i+num_elements]
          self.setCurveData(self.xCrossSection, self.x_index, self.x_array)
          self.setCurveData(self.yCrossSection, self.x_index, self.y_array)
        else:
	  self.setAxisTitle(QwtPlot.yLeft, 'Signal')
          if self.x_array is None:
            self.x_array = zeros(num_elements, Float32)
            self.y_array = zeros(num_elements, Float32)
            self.x_index = arange(num_elements)
            self.x_index = self.x_index + 0.5
          self.x_array =  flattened_array
          self.setCurveData(self.xCrossSection, self.x_index, self.x_array)
        self.replot()

    def start_timer(self, time, test_complex, display_type):
      self.test_complex = test_complex
      self.setDisplayType(display_type)
      self.startTimer(time)
     # start_timer()
                                                                                
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
          _dprint(2, 'plotting vector')
          if self.display_type != "brentjens":
            real_array =  vector_array.getreal()
            imag_array =  vector_array.getimag()
            shape = real_array.shape
            temp_array = zeros((2*shape[0],shape[1]), Float32)
            for k in range(shape[0]):
              for j in range(shape[1]):
                temp_array[k,j] = real_array[k,j]
                temp_array[k+shape[0],j] = imag_array[k,j]
            self.array_plot('test_vector_complex',temp_array)
          else:
            self.array_plot('test_vector_complex', vector_array)
        else:
          if self.display_type != "brentjens":
            real_array =  m
            imag_array =  n
            shape = real_array.shape
            temp_array = zeros((2*shape[0],shape[1]), Float32)
            for k in range(shape[0]):
              for j in range(shape[1]):
                temp_array[k,j] = real_array[k,j]
                temp_array[k+shape[0],j] = imag_array[k,j]
            self.array_plot('test_image_complex',temp_array)
          else:
            self.array_plot('test_image_complex',a)
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
	  _dprint(2, 'plotting vector')
          self.array_plot('test_vector', vector_array)
        else:
	  _dprint(2, 'plotting array')
          self.array_plot('test_image',m)

      self.index = self.index + 1
    # timerEvent()


def make():
    demo = QwtImagePlot('plot_key')
    demo.resize(500, 300)
    demo.show()
# uncomment the following
    demo.start_timer(1000, True, "grayscale")

# or
# uncomment the following three lines
#    import pyfits
#    m51 = pyfits.open('./m51.fits')
#    demo.array_plot('m51', m51[0].data)

    return demo

def main(args):
    app = QApplication(args)
    demo = make()
    app.setMainWidget(demo)
    app.exec_loop()


# Admire
if __name__ == '__main__':
    main(sys.argv)




