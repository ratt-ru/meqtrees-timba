#!/usr/bin/env python

import sys
from qt import *
from qwt import *
from numarray import *
from UVPAxis import *
from printfilter import *
from ComplexColorMap import *
from ComplexScaleDraw import *
from app_browsers import *
import random

from dmitypes import verbosity
_dbg = verbosity(0,name='displayimage');
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
        _dprint(2,'display type set to ', self.display_type);
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
        print 'in drawImage'
        print 'incoming x map ranges ',xMap.d1(), ' ', xMap.d2()
        print 'incoming y map ranges ',yMap.d1(), ' ', yMap.d2()
        # calculate y1, y2
        y1 = y2 = self.image.height()
#        y1 = y2 = self.image.height() - 1
        print 'starting image height ', y1
        y1 *= (self.yMap.d2() - yMap.d2())
        y1 /= (self.yMap.d2() - self.yMap.d1())
        print 'float y1 ', y1
        y1 = max(0, int(y1-0.5))
#        y1 = max(0, (y1-0.5))
        y2 *= (self.yMap.d2() - yMap.d1())
        y2 /= (self.yMap.d2() - self.yMap.d1())
        print 'float y2 ', y2
        y2 = min(self.image.height(), int(y2+0.5))
#        y2 = min(self.image.height(), (y2+0.5))
        print 'y1, y2 ', y1, ' ', y2
        # calculate x1, x1
        x1 = x2 = self.image.width() 
#        x1 = x2 = self.image.width() - 1
        print 'starting image width ', x1
        x1 *= (xMap.d1() - self.xMap.d1())
        x1 /= (self.xMap.d2() - self.xMap.d1())
        print 'float x1 ', x1
        x1 = max(0, int(x1-0.5))
#        x1 = max(0, (x1-0.5))
        x2 *= (xMap.d2() - self.xMap.d1())
        x2 /= (self.xMap.d2() - self.xMap.d1())
        print 'float x2 ', x2
        x2 = min(self.image.width(), int(x2+0.5))
#        x2 = min(self.image.width(), (x2+0.5))
        print 'x1, x2 ', x1, ' ', x2
        # copy
        image = self.image.copy(x1, y1, x2-x1, y2-y1)
        # zoom
        image = image.smoothScale(xMap.i2()-xMap.i1()+1, yMap.i1()-yMap.i2()+1)
        # draw
        painter.drawImage(xMap.i1(), yMap.i2(), image)

    # drawImage()

# QwtPlotImage()
    
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

        self._first_plot = True
        self._vells_plot = False

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
        self.setAxisTitle(QwtPlot.xBottom, 'Channel Number')
        self.setAxisTitle(QwtPlot.yLeft, 'value')
        
        self.dummy_xCrossSection = None
        self.xCrossSection = None
        self.yCrossSection = None
        self.myXScale = None
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


#        self.__initContextMenu()

    def initSpectrumContextMenu(self):
        """Initialize the spectra context menu
        """
        # skip if no main window
        if not self._mainwin:
          return;

        self._menu = QPopupMenu(self._mainwin);
        QObject.connect(self._menu,SIGNAL("activated(int)"),self.update_spectrum_display);
        id = -1
        self._next_plot = {}
        plot_label = 'spectra:' + self._string_tag
        self.num_plot_arrays = len(self._data_values)
        _dprint(2,' number of arrays to plot ', self.num_plot_arrays)
        data_label = ''
        for i in range(self.num_plot_arrays):
          id = id + 1
          data_label = ''
          if isinstance(self._data_labels, tuple):
            data_label = 'go to ' + self._string_tag  +  " " +self._data_labels[i] + ' ?'
          else:
            data_label = 'go to ' + self._string_tag  +  " " +self._data_labels +' ?'
          self._menu.insertItem(data_label,id)
          self._next_plot[id] = data_label + ' ' + str(id)
        zoom = QAction(self);
        zoom.setIconSet(pixmaps.viewmag.iconset());
        zoom.setText("Disable zoomer");
        zoom.addTo(self._menu);
        printer = QAction(self);
        printer.setIconSet(pixmaps.fileprint.iconset());
        printer.setText("Print plot");
        QObject.connect(printer,SIGNAL("activated()"),self.printplot);
        printer.addTo(self._menu);


    def update_spectrum_display(self, menuid):
      if menuid < 0:
        self.unzoom()
        return
      id_string = self._next_plot[menuid]
      plane = 0
      plane_loc = len(id_string) -2
      if plane_loc >= 0:
        plane = int( id_string[plane_loc:len(id_string)])
      if isinstance(self._data_labels, tuple):
        self.data_label = 'spectra:' + self._string_tag  +  " " +self._data_labels[plane]
      else:
        self.data_label = 'spectra:' + self._string_tag  +  " " +self._data_labels
      self.array_plot(self.data_label, self._data_values[plane])


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
            key = " value"
            self._label = "go to plane " + str(i) + key 
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
              Message =  'It would appear that there is a problem with perturbed values.\nThey cannot be displayed.'
              mb_msg = QMessageBox("display_image.py",
                               Message,
                               QMessageBox.Warning,
                               QMessageBox.Ok | QMessageBox.Default,
                               QMessageBox.NoButton,
                               QMessageBox.NoButton)
              mb_msg.exec_loop()

        zoom = QAction(self);
        zoom.setIconSet(pixmaps.viewmag.iconset());
        zoom.setText("Disable zoomer");
        zoom.addTo(self._menu);
        printer = QAction(self);
        printer.setIconSet(pixmaps.fileprint.iconset());
        printer.setText("Print plot");
        QObject.connect(printer,SIGNAL("activated()"),self.printplot);
        printer.addTo(self._menu);
    # end plot_vells_data()

    def unzoom(self):
        self.zooming = 0
        if len(self.zoomStack):
          xmin, xmax, ymin, ymax = self.zoomStack.pop()
          self.setAxisScale(QwtPlot.xBottom, xmin, xmax)
          self.setAxisScale(QwtPlot.yLeft, ymin, ymax)
          self.replot()
        else:
          return

    def update_vells_display(self, menuid):
      if menuid < 0:
        self.unzoom()
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
        key = " value "
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
          self.array_plot(self._label, self._value_array)
        else:
#we have a real array
          _dprint(3,'handling real array')
          self._label = "plane " + str(plane) + key 
          self._z_real_min = self._value_array.min()
          self._z_real_max = self._value_array.max()
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
        if self.is_vector == False:
          self.plotImage.drawImage(
            painter, maps[QwtPlot.xBottom], maps[QwtPlot.yLeft])
        QwtPlot.drawCanvasItems(self, painter, rectangle, maps, filter)


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
            e.accept()
            self._menu.popup(e.globalPos());

        elif Qt.MidButton == e.button():
            if self._vells_plot:
              print 'cross sections for vells are a work in progress!'
#              return
            if self.active_image:
              xpos = e.pos().x()
              ypos = e.pos().y()
              print 'raw mouse positions ', xpos, ' ', ypos
              xpos = self.invTransform(QwtPlot.xBottom, xpos)
              ypos = self.invTransform(QwtPlot.yLeft, ypos)
              print 'inverted mouse positions ', xpos, ' ', ypos
              if self._vells_plot:
                xpos = self.plotImage.xMap.limTransform(xpos)
                ypos = self.plotImage.yMap.limTransform(ypos)
              else:
                xpos = int(xpos)
                ypos = int(ypos)
              print 'image mouse positions ', xpos, ' ', ypos
              shape = self.raw_image.shape
              self.x_array = zeros(shape[0], Float32)
              self.x_index = arange(shape[0])
              self.x_index = self.x_index + 0.5
              for i in range(shape[0]):
                self.x_array[i] = self.raw_image[i,ypos]
              self.setAxisAutoScale(QwtPlot.yRight)
              if self.xCrossSection is None:
                self.xCrossSection = self.insertCurve('xCrossSection')
                self.setCurvePen(self.xCrossSection, QPen(Qt.black, 2))
                plot_curve=self.curve(self.xCrossSection)
                plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, 
                   QBrush(Qt.red), QPen(Qt.red), QSize(5,5)))
              self.enableAxis(QwtPlot.yRight)
              self.setAxisTitle(QwtPlot.yRight, 'cross-section value')
              self.setCurveYAxis(self.xCrossSection, QwtPlot.yRight)
              if self._vells_plot:
                self.setCurveXAxis(self.xCrossSection, QwtPlot.xTop)
#                self.setAxisAutoScale(QwtPlot.xTop)
              self.setAxisAutoScale(QwtPlot.yRight)
              self.setCurveData(self.xCrossSection, self.x_index, self.x_array)
              self.replot()
              _dprint(2, 'called replot in onMousePressed');
           
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
        print ' vells ranges ', self.vells_freq, ' ', self.vells_time
        print ' corresponding image shape ', image.shape
        self.plotImage.setData(image, self.vells_freq, self.vells_time)
      else:
        self.plotImage.setData(image)

      self.raw_image = image
      if self._display_type == "brentjens":
        self.plotImage.setBrentjensImage(image)
      else:
        self.plotImage.setImage(image)
      self.replot()
      _dprint(2, 'called replot in display_image');
    # display_image()

    def plot_data(self, visu_record, attribute_list=None):
      """ process incoming data and attributes into the
          appropriate type of plot """
      _dprint(2, 'in plot data');
#      _dprint(2, 'visu_record ', visu_record)

# first find out what kind of plot we are making
      self._plot_type = None
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
        self.initSpectrumContextMenu()
        plot_label = 'spectra:' + self._string_tag
        self.num_plot_arrays = len(self._data_values)
        _dprint(2,' number of arrays to plot ', self.num_plot_arrays)
        self.data_label = ''
        if isinstance(self._data_labels, tuple):
          self.data_label = 'spectra:' + self._string_tag +  " " +self._data_labels[0]
        else:
          self.data_label = 'spectra:' + self._string_tag +  " " +self._data_labels
# plot first instance of array
        self.array_plot(self.data_label, self._data_values[0])
        if isinstance(self._data_labels, tuple):
          if len(self._data_labels) > 1:
            self.data_label = 'spectra:' + self._string_tag +  " " +self._data_labels[1]
          else:
            self.data_label = 'spectra:' + self._string_tag +  " " +self._data_labels[0]
        else:
          self.data_label = 'spectra:' + self._string_tag +  " " +self._data_labels
        Message = 'Continue to plot of ' + self.data_label + '?'
        self.plot_counter = 0

      self._first_plot = False

    # end plot_data()

    def calc_vells_ranges(self):
                                                                                
      vells_start_freq = self._vells_rec.cells.domain.freq[0] 
      vells_end_freq  =  self._vells_rec.cells.domain.freq[1]
      vells_start_time = self._vells_rec.cells.domain.time[0] 
      vells_end_time  =  self._vells_rec.cells.domain.time[1]

      self.vells_freq = (vells_start_freq,vells_end_freq)
      self.vells_time = (vells_start_time,vells_end_time)

                                                                                
    def plot_vells_data (self, vells_record):
      """ process incoming data and attributes into the
          appropriate type of plot """
      _dprint(2, 'in plot_vells_data');
      self._vells_rec = vells_record;
# if we are single stepping through requests, Oleg may reset the
# cache, so check for a non-data record situation
      if isinstance(self._vells_rec, bool):
        return

# are we dealing with Vellsets?
      if self._vells_rec.has_key("vellsets"):
        self._vells_plot = True
        self.calc_vells_ranges()
        self. initVellsContextMenu()
        _dprint(3, 'handling vellsets')
# how many VellSet planes (e.g. I, Q, U, V would each be a plane) are there?
        number_of_planes = len(self._vells_rec["vellsets"])
        _dprint(3, 'number of planes ', number_of_planes)
        if self._vells_rec.vellsets[0].has_key("shape"):
          self._shape = self._vells_rec.vellsets[0]["shape"]
# plot the first plane member
        if self._vells_rec.vellsets[0].has_key("value"):
          key = " value "
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
              temp_array = numarray.asarray(temp_value)
              self._value_array = numarray.resize(temp_array,self._shape)

          except:
            temp_array = numarray.asarray(self._vells_rec.vellsets[0].value)
            self._shape = self._vells_rec.vellsets[0]["shape"]
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
            self._label = "plane " + str(0) + key 
            self.array_plot(self._label, self._value_array)
          else:
#we have a real array
            _dprint(3,'handling real array')
            self._label = "plane " + str(0) + key 
            self._z_real_min = self._value_array.min()
            self._z_real_max = self._value_array.max()
            self.array_plot(self._label, self._value_array)

    # end plot_vells_data()

    def handle_finished (self):
      print 'in handle_finished'

    def array_plot (self, data_label, plot_array):
      """ figure out shape, rank etc of a spectrum array and
          plot it  """

# delete any previous curves
      self.removeCurves()
      self.xCrossSection = None
      self.yCrossSection = None
      self.dummy_xCrossSection = None
      self.myXScale = None

# set title
      self.setTitle(data_label)

# figure out type and rank of incoming array
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
        self.active_image = True

# create colorbar
#        scale = self.axis(QwtPlot.yLeft)
#        scale.setBaselineDist(10)
#        self.colorBar = ColorBar(Qt.Vertical, scale)
#        self.colorBar.setRange(Qt.red, Qt.darkBlue)
#        self.colorBar.setFocusPolicy(QWidget.TabFocus)

#        self.setAxisAutoScale(QwtPlot.xBottom)
        self.setAxisTitle(QwtPlot.yLeft, 'sequence')
        if complex_type and self._display_type != "brentjens":
          if self._vells_plot:
            self.setAxisTitle(QwtPlot.xBottom, 'Frequency (real followed by imaginary)')
            self.setAxisTitle(QwtPlot.yLeft, 'Time')

          else:
            self.setAxisTitle(QwtPlot.xBottom, 'Channel Number (real followed by imaginary)')
          myXScale = ComplexScaleDraw(plot_array.shape[0])
          self.setAxisScaleDraw(QwtPlot.xBottom, myXScale)

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
            self.setAxisTitle(QwtPlot.xBottom, 'Frequency')
            self.setAxisTitle(QwtPlot.yLeft, 'Time')
          else:
            self.setAxisTitle(QwtPlot.xBottom, 'Channel Number')

          self.display_image(plot_array)

      if self.is_vector == True:
        self.active_image = False
        flattened_array = None
        if self._vells_plot:
          self.setAxisTitle(QwtPlot.xBottom, 'Frequency')
        else:
          self.setAxisTitle(QwtPlot.xBottom, 'Channel Number')
# make sure we are autoscaling in case an image was previous
        self.setAxisAutoScale(QwtPlot.xBottom)
        self.setAxisAutoScale(QwtPlot.yLeft)
        self.setAxisAutoScale(QwtPlot.yRight)
        num_elements = n_rows*n_cols
        flattened_array = reshape(plot_array,(num_elements,))
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
                     QPen(Qt.red), QSize(5,5)))
          plot_curve=self.curve(self.yCrossSection)
          plot_curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.green),
                     QPen(Qt.green), QSize(5,5)))
          self.x_array =  flattened_array.getreal()
          self.y_array =  flattened_array.getimag()
          self.x_index = arange(num_elements)
          self.x_index = self.x_index + 0.5
          self.setCurveData(self.xCrossSection, self.x_index, self.x_array)
          self.setCurveData(self.yCrossSection, self.x_index, self.y_array)
          if not self.dummy_xCrossSection is None:
            self.removeCurve(self.dummy_xCrossSection)
            self.dummy_xCrossSection = None
        else:
          self.setAxisTitle(QwtPlot.yLeft, 'Value')
          self.enableAxis(QwtPlot.yRight, False)
          self.x_array = zeros(num_elements, Float32)
          self.y_array = zeros(num_elements, Float32)
          self.x_index = arange(num_elements)
          self.x_index = self.x_index + 0.5
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
        self.replot()
        _dprint(2, 'called replot in array_plot');
    # array_plot()

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
    demo.start_timer(5000, False, "grayscale")

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

