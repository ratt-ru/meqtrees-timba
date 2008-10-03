
# modules that are imported

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

from Timba.dmi import *
from Timba import utils
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI import widgets
from Timba.GUI.browsers import *
from Timba import Grid

import sys
from qt import *
try:
  from Qwt4 import *
except:
  from qwt import *

import numpy

from plot_printer import *

import random

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


class QwtHistogramPlotter(QwtPlot):

    def __init__(self, parent=None):
      QwtPlot.__init__(self, parent)

      self.mainwin = parent and parent.topLevelWidget()

      # make a QwtPlot widget
      self.plotLayout().setMargin(0)
      self.plotLayout().setCanvasMargin(0)
      self.plotLayout().setAlignCanvasToScales(1)
      self.setlegend = 1
      self.setAutoLegend(self.setlegend)
      self.enableLegend(True)
      self.setLegendPos(Qwt.Right)
      # set axis titles
      self.title = None
      self.source_marker = None
      self.setTitle('Histogram')
      self.setAxisTitle(QwtPlot.yLeft, 'number in bin')
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

# set default background to  whatever QApplication sez it should be!
      self.setCanvasBackground(QApplication.palette().active().base())

      #create a context menu to over-ride the one from Oleg
      if self.mainwin:
        self.menu = QPopupMenu(self.mainwin);
      else:
        self.menu = QPopupMenu(self);
      toggle_id = 200
      self.menu.insertItem("Toggle Legend", toggle_id)

      zoom = QAction(self);
      zoom.setIconSet(pixmaps.viewmag.iconset());
      zoom.setText("Disable zoomer");
      zoom.addTo(self.menu);
      printer = QAction(self);
      printer.setIconSet(pixmaps.fileprint.iconset());
      printer.setText("Print plot");
      QObject.connect(printer,SIGNAL("activated()"),self.printplot);
      printer.addTo(self.menu);
      QObject.connect(self.menu,SIGNAL("activated(int)"),self.update_display);
      
      # add help facility
      QWhatsThis.add(self, display_histogram_instructions)

        
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
#        histogram_in = abs(input_array)
        histogram_in = input_array.real
        self.setAxisTitle(QwtPlot.xBottom, 'array value (real=black, red=imag) ')
      else:
        self.setAxisTitle(QwtPlot.xBottom, 'array value ')
        histogram_in = input_array
      array_min = histogram_in.min()
      array_max = histogram_in.max()
      histogram_array = numpy.histogram(histogram_in, bins=num_bins)

# remove any previous curves
      self.removeCurves()
# make sure we are autoscaling in case a previous plot is being over-written
      self.setAxisAutoScale(QwtPlot.xBottom)
      self.setAxisAutoScale(QwtPlot.yLeft)

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
      curve_index = self.insertCurve(curve_key)
      self.setCurvePen(curve_index, QPen(Qt.black, 2))
      self.setCurveData(curve_index, histogram_curve_x, histogram_curve_y)

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
        curve_index_imag = self.insertCurve(curve_key)
        self.setCurvePen(curve_index_imag, QPen(Qt.red, 2))
        self.setCurveData(curve_index_imag, histogram_curve_x_im, histogram_curve_y_im)
      self.replot()
     
    # histogram_plot()


    def report_scalar_value(self, data_label, scalar_data):
      """ report a scalar value in case where a vells plot has
          already been initiated
      """
      Message = data_label + ' is a scalar\n with value: ' + str(scalar_data)
      _dprint(3,' scalar message ', Message)
      
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
         QFont(fn, 10, QFont.Bold, False),
         Qt.blue, QPen(Qt.red, 2), QBrush(Qt.yellow))
      self.replot()
      _dprint(3,'called replot in report_scalar_value')

    def printplot(self):
      try:
          printer = QPrinter(QPrinter.HighResolution)
      except AttributeError:
          printer = QPrinter()
      printer.setOrientation(QPrinter.Landscape)
      printer.setColorMode(QPrinter.Color)
      printer.setOutputToFile(True)
      printer.setOutputFileName('histogram_plot.ps')
      if printer.setup():
          filter = printfilter.PrintFilter()
          if (QPrinter.GrayScale == printer.colorMode()):
              filter.setOptions(QwtPlotPrintFilter.PrintAll
                                & ~QwtPlotPrintFilter.PrintCanvasBackground)
          try:
            self.print_(printer, filter)
          except:
            self.printPlot(printer, filter)
    # printplot()


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
            if self.zoomStack == []:
                self.zoomState = (
                    self.axisScale(QwtPlot.xBottom).lBound(),
                    self.axisScale(QwtPlot.xBottom).hBound(),
                    self.axisScale(QwtPlot.yLeft).lBound(),
                    self.axisScale(QwtPlot.yLeft).hBound(),
                    )
        elif Qt.RightButton == e.button():
            e.accept()
            self.menu.popup(e.globalPos())
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
      if menuid == 200:
        self.toggleLegend()
        return
    # update_display


    def unzoom(self):
      if len(self.zoomStack):
        xmin, xmax, ymin, ymax = self.zoomStack.pop()
        self.setAxisScale(QwtPlot.xBottom, xmin, xmax)
        self.setAxisScale(QwtPlot.yLeft, ymin, ymax)
        self.replot()
        _dprint(3, 'called replot in unzoom')
      else:
        return
    # unzoom()

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
    

    # functions for testing the plotting
    def start_test_timer(self, time, test_complex):
      self.test_complex = test_complex
      self.startTimer(time)
      self.index = 0
      self.num_bins = 10
    # start_test_timer()
                                                                                
    def timerEvent(self, e):
      if self.test_complex:
        m = fromfunction(RealDist, (30,20))
        n = fromfunction(ImagDist, (30,20))
        vector_array = numpy.zeros((30,1), numpy.complex128)
        shape = m.shape
        for i in range(shape[0]):
          for j in range(shape[1]):
            m[i,j] = m[i,j] + self.index * random.random()
            n[i,j] = n[i,j] + 3 * self.index * random.random()
        a = zeros((shape[0],shape[1]), complex128)
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
        m = fromfunction(dist, (30,20))
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

class HistogramPlotter(GriddedPlugin):
  """ a class to plot very simple histograms of array data distributions """

  _icon = pixmaps.bars3d
  viewer_name = "Histogram Plotter";
  def is_viewable (data):
    return len(data) > 0;
  is_viewable = staticmethod(is_viewable);

  def __init__(self,gw,dataitem,cellspec={},**opts):
    GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);

# create the plotter
    self._plotter = QwtHistogramPlotter(parent=self.wparent())
    self._plotter.show()
    self.set_widgets(self._plotter,dataitem.caption,icon=self.icon());

    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

#  def __del__(self):
#    print "in destructor"
                                                                                           
  def wtop (self):
    return self._plotter

  def set_data (self,dataitem,default_open=None,**opts):
    """ this function is the callback interface to the meqbrowser and
        handles new incoming data for the histogram """

    if not self.test_scalar_value (dataitem.data, 'data'):
      self._plotter.histogram_plot('data', dataitem.data)

# enable & highlight the cell
    self.enable();
    self.flash_refresh();

  def test_scalar_value (self, data_array, data_label):
    """ test if incoming 'array' contains only a scalar value """
# do we have a scalar?
    is_scalar = False
    scalar_data = 0.0
    try:
      shape = data_array.shape
      _dprint(3,'data_array shape is ', shape)
    except:
      is_scalar = True
      scalar_data = data_array
    if not is_scalar and len(shape) == 1:
      if shape[0] == 1:
        is_scalar = True
        scalar_data = data_array[0]
    if is_scalar:
      self._plotter.report_scalar_value(data_label, scalar_data)
      return True
    else:
      return False

# class HistogramPlotter

    
def make():
    demo = QwtHistogramPlotter('demo')
    demo.start_test_timer(10000, False)
    demo.show()
    return demo

def main(args):
    app = QApplication(args)
    demo = make()
    app.setMainWidget(demo)
    app.exec_loop()


# Admire
if __name__ == '__main__':
    main(sys.argv)
else:
    Grid.Services.registerViewer(array_class,HistogramPlotter,priority=15)
