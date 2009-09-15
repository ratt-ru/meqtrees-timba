
# modules that are imported

#% $Id: histogram_plotter.py 6837 2009-03-05 19:00:25Z twillis $ 

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

#from Timba.dmi import *
#from Timba import utils
#from Timba.GUI.pixmaps import pixmaps
#from Timba.GUI import widgets
#from Timba.GUI.browsers import *
#from Timba import Grid

import sys
from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt
from QwtSpy_qt4 import *
import numpy
import random

import printfilter_qt4

from Timba.utils import verbosity
_dbg = verbosity(0,name='histogramplot');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;


#  distance from (15,5) squared
def dist(x,y):
  return (x-15)**2+(y-5)**2
def imag_dist(x,y):
  return (x-10)**2+(y-10)**2
def RealDist(x,y):
  return (x)**2
def ImagDist(x,y):
  return (x-29)**2
#m = fromfunction(dist, (10,10))

# A class to plot simple histograms of the intensity distributions
# from incoming arrays

display_histogram_instructions = \
'''This plot basically shows histograms of the intensity / data distributions in n-dimensional arrays. At present the number of bins in the histogram is fixed at 10. Most decision making takes place behind the scenes, so to speak, as the system uses the dimensionality of the data and the source of the data to decide how the data will be displayed. However, once a display appears, you can interact with it in certain standardized ways.<br><br>
Button 1 (Left): If you hold the <b>left</b> mouse button down on a location inside a plot and then drag it, a rectangular square will be seen. Then when you release the left mouse button, the plot will 'zoom in' on the area defined inside the rectangle.<br><br>
Button 2 (Right):Click the <b>right</b> mouse button in a display window to get get a context menu with options for printing, resetting the zoom, or toggling a <b>Legends</b> display. If you click on the 'Disable zoomer ' icon  in a window where you had zoomed in on a selected region, then the original entire array is re-displayed. If you select the Print option from the menu, the standard Qt printer widget will appear. That widget will enable you print out a copy of your plot, or save the plot in Postscript format to a file. When the histogram plot first appears, a <b>Legends</b> display associating a push button with the histogram is shown at the right hand side of the display. You can toggle the display of this push button ON or OFF by selecting the Toggle Legend option from the context menu. Clicking on a <b>Legends</b> push button will cause the corresponding histogram to appear or disappear, depending on the current state.<br><br>
'''


class QwtHistogramPlotter(Qwt.QwtPlot):

    def __init__(self, plot_key="", parent=None):
      Qwt.QwtPlot.__init__(self, parent)

      self.mainwin = parent and parent.topLevelWidget()

      # make a QwtPlot widget
      self.plotLayout().setMargin(0)
      self.plotLayout().setCanvasMargin(0)
      self.plotLayout().setAlignCanvasToScales(1)
      self.setlegend = 1
#     self.setAutoLegend(self.setlegend)
#     self.enableLegend(True)
#     self.setLegendPos(Qwt.Right)
# set fonts for titles
      # first create copy of standard application font..
      self.title_font = Qt.QFont(Qt.QApplication.font());
      fi = Qt.QFontInfo(self.title_font);
      # and scale it down to 70%
      self.title_font.setPointSize(fi.pointSize()*0.7);

      # set axis titles
      self.title = None
      text = Qwt.QwtText('Histogram')
      text.setFont(self.title_font)
      self.setTitle(text)
      text = Qwt.QwtText('number in bin')
      text.setFont(self.title_font)
      self.setTitle(text)
      self.setAxisTitle(Qwt.QwtPlot.yLeft, text)
#     self.zoomStack = []

# set default background to  whatever QApplication sez it should be!
#     self.setCanvasBackground(Qt.QApplication.palette().active().base())

      #create a context menu to over-ride the one from Oleg
      if self.mainwin:
        self.menu = Qt.QMenu(self.mainwin);
      else:
        self.menu = Qt.QMenu(self);
      self._toggle_legend = Qt.QAction('Toggle Legend',self)
      self.menu.addAction(self._toggle_legend)
      self.connect(self._toggle_legend,Qt.SIGNAL("triggered()"),self.handle_toggle_legend);

      self._disable_zoomer = Qt.QAction('Disable Zoomer',self)
      self.menu.addAction(self._disable_zoomer)
      self.connect(self._disable_zoomer,Qt.SIGNAL("triggered()"),self.handle_disable_zoomer);

      printer = Qt.QAction('Print plot',self);
#     printer.setIconSet(pixmaps.fileprint.iconset());
      self.connect(printer,Qt.SIGNAL("triggered()"),self.printplot);
      self.menu.addAction(printer)


      self.spy = Spy(self.canvas())
      self.zoom_outline = Qwt.QwtPlotCurve()

#       self.connect(self, SIGNAL("legendClicked(QwtPlotItem*)"),
#                    self.toggleVisibility)

      self.connect(self.spy,
                     Qt.SIGNAL("MouseMove"),
                     self.setPosition)
      self.connect(self.spy,
                     Qt.SIGNAL("MousePress"),
                     self.onMousePressed)
      self.connect(self.spy,
                     Qt.SIGNAL("MouseRelease"),
                     self.onMouseReleased)

      
      # add help facility
#     QWhatsThis.add(self, display_histogram_instructions)
        
    # __init__()

    def histogram_plot (self, data_label, input_array, num_bins=10):
      """ plot histogram of array or vector """

# set title
      if self.title is None:
        self.setTitle(data_label)

# figure out type and rank of incoming array
      complex_type = False
      if input_array.dtype == numpy.complex64:
            complex_type = True;
      if input_array.dtype == numpy.complex128:
            complex_type = True;
      histogram_in = None
      if complex_type:
        histogram_in = input_array.real
        text =Qwt.QwtText('array value (real=black, red=imag)')
      else:
        histogram_in = input_array
        text =Qwt.QwtText('array value')
      text.setFont(self.title_font)
      self.setAxisTitle(Qwt.QwtPlot.xBottom, text)
      array_min = histogram_in.min()
      array_max = histogram_in.max()
      histogram_array = numpy.histogram(histogram_in, bins=num_bins)

# remove any previous curves
      self.removeCurves()
# make sure we are autoscaling in case a previous plot is being over-written
      self.setAxisAutoScale(Qwt.QwtPlot.xBottom)
      self.setAxisAutoScale(Qwt.QwtPlot.yLeft)

# we have created bins, now generate a Qwt curve for each bin
      histogram_curve_x = numpy.zeros(4 * num_bins, numpy.float32) 
      histogram_curve_y = numpy.zeros(4 * num_bins, numpy.float32) 
      bin_incr = (array_max - array_min) / num_bins
      curve_index = 0
      for i in range(num_bins):
        bin_start = array_min + i * bin_incr
        bin_end = bin_start + bin_incr
        histogram_curve_x[curve_index] = bin_start
        histogram_curve_y[curve_index] = 0
        histogram_curve_x[curve_index+1] = bin_start
        histogram_curve_y[curve_index+1] = histogram_array[0][i]
        histogram_curve_x[curve_index+2] = bin_end
        histogram_curve_y[curve_index+2] = histogram_array[0][i]
        histogram_curve_x[curve_index+3] = bin_end
        histogram_curve_y[curve_index+3] = 0
        curve_index = curve_index + 4
      curve_key = 'histogram_curve'
      histo_curve = Qwt.QwtPlotCurve(curve_key)
      histo_curve.setPen(Qt.QPen(Qt.Qt.black, 2))
      histo_curve.setData(histogram_curve_x, histogram_curve_y)
      histo_curve.attach(self)

# add in histogram for imaginary stuff if we have a complex array
      if complex_type:
#        real_array_max = array_max
        histogram_in = input_array.imag
        array_min = histogram_in.min()
        array_max = histogram_in.max()
        histogram_array = numpy.histogram(histogram_in, bins=num_bins)
        histogram_curve_x_im = numpy.zeros(4 * num_bins, numpy.float32) 
        histogram_curve_y_im = numpy.zeros(4 * num_bins, numpy.float32) 
        bin_incr = (array_max - array_min) / num_bins
        curve_index = 0
#        array_min = array_min + real_array_max
        for i in range(num_bins):
          bin_start = array_min + i * bin_incr
          bin_end = bin_start + bin_incr
          histogram_curve_x_im[curve_index] = bin_start
          histogram_curve_y_im[curve_index] = 0
          histogram_curve_x_im[curve_index+1] = bin_start
          histogram_curve_y_im[curve_index+1] = histogram_array[0][i]
          histogram_curve_x_im[curve_index+2] = bin_end
          histogram_curve_y_im[curve_index+2] = histogram_array[0][i]
          histogram_curve_x_im[curve_index+3] = bin_end
          histogram_curve_y[curve_index+3] = 0
          curve_index = curve_index + 4
        curve_key = 'histogram_curve_imag'
        imag_curve = Qwt.QwtPlotCurve(curve_key)
        imag_curve.setPen(Qt.QPen(Qt.Qt.red, 2))
        imag_curve.setData(histogram_curve_x_im, histogram_curve_y_im)
        imag_curve.attach(self)
      self.replot()
     
    # histogram_plot()


    def removeCurves(self):
      for i in self.itemList():
        if isinstance(i, Qwt.QwtPlotCurve):
          i.detach()

    def report_scalar_value(self, data_label, scalar_data):
      """ report a scalar value in case where a vells plot has
          already been initiated
      """
      Message = data_label + ' is a scalar\n with value: ' + str(scalar_data)
      _dprint(3,' scalar message ', Message)
      
      text = Qwt.QwtText(Message)
      fn = self.fontInfo().family()
      text.setFont(Qt.QFont(fn, 10, Qt.QFont.Bold))
      text.setColor(Qt.Qt.blue)
      text.setBackgroundBrush(Qt.QBrush(Qt.Qt.yellow))

      if not self.source_marker is None:
        self.source_marker.detach()
      self.source_marker = Qwt.QwtPlotMarker()
      self.source_marker.setLabelAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignTop)
      self.source_marker.setLabel(text)

      ylb = self.axisScale(Qwt.QwtPlot.yLeft).lBound()
      xlb = self.axisScale(Qwt.QwtPlot.xBottom).lBound()
      yhb = self.axisScale(Qwt.QwtPlot.yLeft).hBound()
      xhb = self.axisScale(Qwt.QwtPlot.xBottom).hBound()

      self.source_marker.setValue( xlb+0.1, ylb+1.0)
      self.source_marker.attach(self)
      self.replot()
      _dprint(3,'called replot in report_scalar_value')

    def printplot(self):
      # taken from PyQwt Bode demo

      printer = Qt.QPrinter(Qt.QPrinter.HighResolution)

      printer.setOutputFileName('histogram-example-%s.ps' % Qt.qVersion())

      printer.setOrientation(Qt.QPrinter.Landscape)
      printer.setColorMode(Qt.QPrinter.Color)

      dialog = Qt.QPrintDialog(printer)
      if dialog.exec_():
          filter = printfilter_qt4.PrintFilter()
          if (Qt.QPrinter.GrayScale == printer.colorMode()):
              filter.setOptions(
                  QwtPlotPrintFilter.PrintAll
                  & ~QwtPlotPrintFilter.PrintBackground
                  | QwtPlotPrintFilter.PrintFrameWithScales)
          self.print_(printer, filter)

    def setPosition(self, e):
        pass

    # onMouseMoved()

    def onMousePressed(self, e):
        if Qt.Qt.LeftButton == e.button():
            # Python semantics: self.pos = e.pos() does not work; force a copy
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
        elif Qt.Qt.RightButton == e.button():
            e.accept()
            self.menu.popup(e.globalPos())
        # fake a mouse move to show the cursor position
        self.setPosition(e)

    # onMousePressed()

    def onMouseReleased(self, e):
        if Qt.Qt.LeftButton == e.button():
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
        elif Qt.Qt.RightButton == e.button():
            if len(self.zoomStack):
                xmin, xmax, ymin, ymax = self.zoomStack.pop()
            else:
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

    def update_display(self, menuid):
      if menuid < 0:
        self.unzoom()
        return
    # update_display


    def handle_disable_zoomer(self):
      if len(self.zoomStack):
        xmin, xmax, ymin, ymax = self.zoomStack.pop()
        self.setAxisScale(QwtPlot.xBottom, xmin, xmax)
        self.setAxisScale(QwtPlot.yLeft, ymin, ymax)
        self.replot()
        _dprint(3, 'called replot in unzoom')
      else:
        return
    # unzoom()

    def handle_toggle_legend(self):
      if self.setlegend == 1:
        self.setlegend = 0
        self.enableLegend(False)
      else:
        self.setlegend = 1
        self.enableLegend(True)
      self.setAutoLegend(self.setlegend)
      self.replot()
    # toggleLegend()
    

    # functions for testing the plotting
    def start_test_timer(self, time, test_complex):
      self.test_complex = test_complex
      self.startTimer(time)
      self.index = 0
      self.num_bins = 10
    # start_test_timer()
                                                                                
    def timerEvent(self, e):
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
          _dprint(2, 'plotting array');
          self.histogram_plot ('histogram of complex array', a, self.num_bins)
          self.test_complex = False
        else:
          _dprint(2, 'plotting vector');
          self.histogram_plot ('histogram of complex vector', vector_array, self.num_bins)
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
          _dprint(2, 'plotting array');
          self.histogram_plot ('histogram of real array', m, self.num_bins)
          self.test_complex = True
        else:
          _dprint(2, 'plotting vector');
          self.histogram_plot ('histogram of real vector', vector_array, self.num_bins)

      self.index = self.index + 1
      self.num_bins = self.num_bins + 1
    # timerEvent()

# class QwtHistogramPlotter

    
def make():
    demo = QwtHistogramPlotter('demo')
    demo.start_test_timer(10000, False)
    demo.show()
    return demo

def main(args):
    app = Qt.QApplication(args)
    demo = make()
    app.exec_()


# Admire
if __name__ == '__main__':
    main(sys.argv)
