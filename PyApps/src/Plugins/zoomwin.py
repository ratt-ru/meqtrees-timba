#!/usr/bin/env python

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

# this is a python translation of the ACSIS c++ zoomwin.cc program

import sys
from qt import *
try:
  from Qwt4 import *
except:
  from qwt import *
from numarray import *
import printfilter
import plot_printer
from display_image import *

#widget to show a zoomed chanel of the plot

class ZoomPopup(QWidget):

  def __init__(self, CurveNumber, x_values, y_values , flags, pen, parent=None, name=None):
    """ Initialises all the variables.  
        creates the main zoom plot
        connects the qt signals
    """
    fl = Qt.WType_TopLevel|Qt.WStyle_Customize;
    fl |= Qt.WStyle_DialogBorder|Qt.WStyle_Title;
    QWidget.__init__(self, parent, name, fl)
    self.setCaption('Channel ' + str(CurveNumber))
    self.setCaption('Hi hi')
    self._parent = parent
    self._d_zoomActive = self._d_zoom = False
    self._curve_number = CurveNumber

    self._do_close = True   # enable closing by window manager
    self._do_pause = False   # pause mode is False at startup
    self._compare_max = False
    self._do_linear_scale = True  # linear Y axis scale by default
    self._do_fixed_scale = False  # auto scaling by default
    self._array_label = "Channel "
 
    #Create the plot for selected curve to zoom
    self._plotter = QwtImageDisplay(parent=self)
    self._plotter. setZoomDisplay()

    self._zoom_plot_label = self._array_label + str(self._curve_number) + " Sequence (oldest to most recent)"
#   self._plotter.setAxisTitle(QwtPlot.xBottom, self._zoom_plot_label)
#   self._plotter.setAxisTitle(QwtPlot.yLeft, "Signal")
#   self._plotter.setGridMajPen(QPen(Qt.white, 0, Qt.DotLine))

#   self._plotter.setGridMinPen(QPen(Qt.gray, 0 , Qt.DotLine))

#   label_char = 'G'
#   label_prec = 5
#   self._plotter.setAxisLabelFormat(QwtPlot.yLeft, label_char, label_prec)

    self._max_crv = -1  # negative value used to indicate that this display
    self._min_crv = -1  # is not being used

  #####end of parameters set for the plot#######/

    # we seem to need a layout for PyQt
    vbox_left = QVBoxLayout( self )
    vbox_left.setSpacing(10)
    box1 = QHBoxLayout( vbox_left )
    box1.addWidget(self._plotter)
    self.plotPrinter = plot_printer.plot_printer(self._plotter)

    self.connect(self._plotter,PYSIGNAL('winpaused'), self.Pausing)
    self.connect(self._plotter,PYSIGNAL('compare'), self.do_compare)
    self.connect(self._plotter,PYSIGNAL('do_print'), self.plotPrinter.do_print)

    self._x_values = x_values
    # insert flags ?   
    self._plotter.initVellsContextMenu()
    self.update_plot(y_values, flags)
    self.show()

  def do_compare_max(self, x_values):
    ### instantiate the envelop that will show min/max deviations
    self._max_envelop = self._y_values
    self._min_envelop = self._y_values
    self._max_crv =self._plotter.insertCurve("Zoomed max curve")
    self._min_crv = self._plotter.insertCurve("Zoomed min curve")
    self._plotter.setCurveData(self._max_crv,x_values,self._max_envelop)
    self._plotter.setCurveData(self._min_crv,x_values,self._min_envelop)
    self._compare_max = True

  def do_compare(self):
    print 'in zoomwin do_compare'
    if self._compare_max:
      self.stop_compare_max()
      self._compare_max = False
    else:
      self._max_envelop = self._y_values
      self._min_envelop = self._y_values
      self._max_crv = self._plotter.insertCurve("Zoomed max curve")
      self._min_crv = self._plotter.insertCurve("Zoomed min curve")
      self._plotter.setCurveData(self._max_crv,self._x_values,self._max_envelop)
      self._plotter.setCurveData(self._min_crv,self._x_values,self._min_envelop)
      self._compare_max = True
    self.reset_max()

  def stop_compare_max(self):
    if self._compare_max:
      self._max_envelop = 0.0
      self._min_envelop = 0.0
      self._plotter.removeCurve(self._max_crv)
      self._plotter.removeCurve(self._min_crv)
      self._compare_max = False
      self._max_crv = -1
      self._min_crv = -1

  def get_max(self):
    if self._compare_max:
      self._max_envelop = self.max(self._max_envelop, self._y_values)
      self._min_envelop = self.min(self._min_envelop, self._y_values)

  def max(self, array1, array2):
     shape = array1.shape
     max_envelop = array1
     for i in range(shape[0]):
       if array2[i] > array1[i]:
         max_envelop[i] = array2[i]
     return max_envelop

  def min(self, array1, array2):
     shape = array1.shape
     min_envelop = array1
     for i in range(shape[0]):
       if array2[i] < array1[i]:
         min_envelop[i] = array2[i]
     return min_envelop

  def reset_max(self):
    if self._compare_max:
      self._max_envelop = self._y_values
      self._min_envelop = self._y_values

  def test_max(self):
    if self._compare_max: 
      return True
    else:
      return False

  def pause_mode(self):
    if self._do_pause: 
      return True
    else:
      return False

  def exec_close(self):
    self.close()

  def Pausing(self):
    self.emit(PYSIGNAL("winpaused"),(self._curve_number,))

  def change_scale_type(self):
# click means change to fixed scale
    toggle_id = self.menu_table['Fixed Scale ']
    if self._do_fixed_scale:
      self._do_fixed_scale = False
      self._menu.changeItem(toggle_id, 'Fixed Scale')
      self._plotter.setAxisAutoScale(QwtPlot.yLeft)
      self.emit(PYSIGNAL("image_auto_scale"),(0,))
    else:
      self._do_fixed_scale = True
      self._menu.changeItem(toggle_id, 'Auto Scale')
# find current data min and max
      scale_max = self._y_values.max()
      scale_min = self._y_values.min()
#     AxisParms = ScaleSelector(scale_max, scale_min, self)
#     self.connect(AxisParms, SIGNAL(scale_values(double,double)), this, SLOT(set_scale_values(double, double)))
#     self.connect(AxisParms, SIGNAL(cancel()), this, SLOT(cancel_scale_request()))

  def set_scale_values(self,max_value,min_value):
    if self._do_fixed_scale:
      self.emit(PYSIGNAL("image_scale_values"),(max_value,min_value))
      self._plotter.setAxisScale(QwtPlot.yLeft, min_value, max_value)
      self._plotter.replot()

  def cancel_scale_request(self):
    if self._do_fixed_scale:
      toggle_id = self.menu_table['Fixed Scale ']
      self._menu.changeItem(toggle_id, 'Fixed Scale')
      self._plotter.setAxisAutoScale(QwtPlot.yLeft)
      self._do_fixed_scale = False
  
  def update_plot(self,y_values, flags):
    if not self._do_pause:
      self._plotter.unsetFlagsData()
      self._y_values = y_values
      abs_flags = abs(flags)
      if abs_flags.max() > 0:
        if len(flags) == len(self._y_values):
          self._plotter.setFlagsData(flags,flip_axes=True)
          self._plotter.set_flag_toggles_active(True,False)
      else:
        self._plotter.set_flag_toggles_active(False,False)
      self._plotter.array_plot (self._zoom_plot_label, self._y_values, flip_axes=True)

#     self.get_max()
      self._plotter.replot()

  def Printzoom(self):
    # taken from PyQwt Bode demo
    try:
      printer = QPrinter(QPrinter.HighResolution)
    except AttributeError:
      printer = QPrinter()
    printer.setOrientation(QPrinter.Landscape)
    printer.setColorMode(QPrinter.Color)
    printer.setOutputToFile(True)
    printer.setOutputFileName('screen_plot-%s.ps' % qVersion())
    if printer.setup():
      filter = printfilter.PrintFilter()
      if (QPrinter.GrayScale == printer.colorMode()):
        filter.setOptions(QwtPlotPrintFilter.PrintAll
                  & ~QwtPlotPrintFilter.PrintCanvasBackground)
      try:
        self._plotter.print_(printer, filter)
      except:
        try:
          self._plotter.printPlot(printer, filter)
        except:
          print 'printing is unavailable'

  def setDataLabel(self, data_label, array_label, is_array=False):
    self._data_label = data_label
    if array_label is None:
      self._array_label = 'Ch ' + str(self._curve_number)
    else:
      self._array_label = array_label
    if is_array:
      self._zoom_plot_label = self._data_label + ": " + self._array_label  
    else:
      self._zoom_plot_label = self._data_label + ": " + self._array_label + " Sequence (oldest to most recent)"
    self._plotter.setAxisTitle(QwtPlot.xBottom, self._zoom_plot_label)

  def plotMouseMoved(self, e):
    """	Gets x and y position of the mouse on the plot according to axis' value
        set right text on the button and underneath the plot
    """
# (I) e (QMouseEvent) Mouse event
    lbl = QString("Event=")
    lbl2 = QString("")
    lbl2.setNum(self._plotter.invTransform(QwtPlot.xBottom, e.pos().x() ), 'g', 3)
    lbl += lbl2 + ",  Signal="
    lbl2.setNum(self._plotter.invTransform(QwtPlot.yLeft, e.pos().y() ), 'g', 3)
    lbl += lbl2
#   self._ControlFrame._lblInfo.setText(lbl)

  def closeEvent(self, ce):
    if self._do_close:
      self.emit(PYSIGNAL("winclosed"),(self._curve_number,))
      ce.accept()
    else:
      ce.ignore()
    #---------------------------------------------
    # Don't call the base function because
    # we want to ignore the close event
    #---------------------------------------------

def main(args):
    app = QApplication(args)
    x_values = array([1.0,2.0,3.0,4.0])
    y_values = array([15.0,25.0,35.0,45.0])
    demo = ZoomPopup(1, x_values, y_values,Qt.yellow,None, None )
    demo.show()
    app.setMainWidget(demo)
    app.exec_loop()


# Admire
if __name__ == '__main__':
    main(sys.argv)

