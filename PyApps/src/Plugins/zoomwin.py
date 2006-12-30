#!/usr/bin/env python

#
# Copyright (C) 2007
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

#widget to show a zoomed chanel of the plot

class ZoomPopup(QWidget):

  menu_table = {
        'Zoom ': 200,
        'Close ': 201,
        'Print ': 202,
        'Pause ': 203,
        'Comparison ': 204,
        'Linear Scale ': 206,
        'Fixed Scale ': 207,
        }


  def __init__(self, CurveNumber, x_values, y_values , pen, parent=None, name=None):
    """ Initialises all the variables.  
        creates bottom frame and the main zoom plot
        Do all the connections
    """
    QWidget.__init__(self, parent, name, Qt.WType_TopLevel)

    self._d_zoomActive = self._d_zoom = False
    self._curve_number = CurveNumber

    self._do_close = False   # disable closing by window manager
    self._do_pause = False   # pause mode is False at startup
    self._compare_max = False
    self._do_linear_scale = True  # linear Y axis scale by default
    self._do_fixed_scale = False  # auto scaling by default
 
    #Create the plot for selected curve to zoom
    self._plotzoom = QwtPlot(self)

    #######Set all the parameters for the plot####/
    self._crv = self._plotzoom.insertCurve("Zoomed curve")

    self._plotzoom.enableGridXMin()

#  plotzoom,enableAxis(QwtPlot.yRight)
 
    self._zoom_plot_label = "Channel " + str(self._curve_number) + " Sequence (oldest to most recent)"
    self._plotzoom.setAxisTitle(QwtPlot.xBottom, self._zoom_plot_label)
    self._plotzoom.setAxisTitle(QwtPlot.yLeft, "Signal")
    self._plotzoom.setGridMajPen(QPen(Qt.white, 0, Qt.DotLine))

    self._plotzoom.setGridMinPen(QPen(Qt.gray, 0 , Qt.DotLine))
    self._plotzoom.setCurvePen(self._crv, QPen(pen))

    label_char = 'G'
    label_prec = 5
    self._plotzoom.setAxisLabelFormat(QwtPlot.yLeft, label_char, label_prec)

    self._plotzoom.setCanvasBackground(Qt.blue)
  
    self._max_crv = -1  # negative value used to indicate that this display
    self._min_crv = -1  # is not being used

    self._plotzoom.enableOutline(True)
#    self.setOutlinePen(Qt.green)
  #####end of parameters setted for the plot#######/

    # we seem to need a layout for PyQt
    vbox_left = QVBoxLayout( self )
    vbox_left.setSpacing(10)
    box1 = QHBoxLayout( vbox_left )
    box1.addWidget(self._plotzoom)

    self._x_values = x_values
    self._y_values = y_values
    self._plotzoom.setCurveData(self._crv, self._x_values, self._y_values)

# create context menu
    self._parent = parent
    self._mainwin = parent and parent.topLevelWidget()
    self._menu = QPopupMenu(self._mainwin)
    toggle_id = self.menu_table['Close ']
    self._menu.insertItem("Close Window", toggle_id)
    toggle_id = self.menu_table['Zoom ']
    self._menu.insertItem("Zoom", toggle_id)
    toggle_id = self.menu_table['Print ']
    self._menu.insertItem("Print", toggle_id)
    toggle_id = self.menu_table['Pause ']
    self._menu.insertItem("Pause", toggle_id)
    toggle_id = self.menu_table['Comparison ']
    self._menu.insertItem("Do Comparison", toggle_id)
    self._menu.setItemVisible(toggle_id, False)
    toggle_id = self.menu_table['Linear Scale ']
    self._menu.insertItem("Log Scale", toggle_id)
    toggle_id = self.menu_table['Fixed Scale ']
    self._menu.insertItem("Fixed Scale", toggle_id)
    self._menu.setItemVisible(toggle_id, False)

    ########### Connections for Signals ############
    self.connect(self._menu,SIGNAL("activated(int)"),self.process_menu);

    #Signal when the mouse is moved on the plot
    self.connect(self._plotzoom,SIGNAL('plotMouseMoved(const QMouseEvent&)'),
	  self.plotMouseMoved)
  
    #Signal when mouse is pressed on the plot
    self.connect(self._plotzoom,SIGNAL('plotMousePressed(const QMouseEvent&)'),
	  self.plotMousePressed)

    #Signal when the mouse is released on the plot
    self.connect(self._plotzoom,SIGNAL('plotMouseReleased(const QMouseEvent&)'),
	  self.plotMouseReleased)
    self._plotzoom.replot()
    self.show()

  def process_menu(self, menuid):
    if menuid < 0:
      return
    if menuid == self.menu_table['Zoom ']:
      self.zoom()
      return True
    if menuid == self.menu_table['Close ']:
      self.Closing()
      if not self._parent is None:
  	self._parent.zoomCountmin()
      return True
    if menuid == self.menu_table['Print ']:
      self.Printzoom()
      return True
    if menuid == self.menu_table['Pause ']:
      self.Pausing()
      return True
    if menuid == self.menu_table['Comparison ']:
      self.do_compare()
      return True
    if menuid == self.menu_table['Linear Scale ']:
      self.change_scale()
      return True
    if menuid == self.menu_table['Fixed Scale ']:
      self.change_scale_type()
      return True

  def do_compare_max(self, x_values):
    ### instantiate the envelop that will show min/max deviations
    self._max_envelop = self._y_values
    self._min_envelop = self._y_values
    self._max_crv =self._plotzoom.insertCurve("Zoomed max curve")
    self._min_crv = self._plotzoom.insertCurve("Zoomed min curve")
    self._plotzoom.setCurveData(self._max_crv,x_values,self._max_envelop)
    self._plotzoom.setCurveData(self._min_crv,x_values,self._min_envelop)
    self._compare_max = True

  def do_compare(self):
    toggle_id = self.menu_table['Comparison ']
    if self._compare_max:
      self.stop_compare_max()
      self._compare_max = False
      self._menu.changeItem(toggle_id, 'Do Comparison')
    else:
      self._max_envelop = self._y_values
      self._min_envelop = self._y_values
      self._max_crv = self._plotzoom.insertCurve("Zoomed max curve")
      self._min_crv = self._plotzoom.insertCurve("Zoomed min curve")
      self._plotzoom.setCurveData(self._max_crv,self._x_values,self._max_envelop)
      self._plotzoom.setCurveData(self._min_crv,self._x_values,self._min_envelop)
      self._compare_max = True
      self._menu.changeItem(toggle_id, 'Stop Comparison')
    self.reset_max()

  def stop_compare_max(self):
    if self._compare_max:
      self._max_envelop = 0.0
      self._min_envelop = 0.0
      self._plotzoom.removeCurve(self._max_crv)
      self._plotzoom.removeCurve(self._min_crv)
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

  def Closing(self):
    """ Closes the zoom window
        Get the number of the curve to close
        emit a signal to set the flag of the deleted curve to 0
    """ 
    self._do_close = True
    self.emit(PYSIGNAL("winclosed"),(self._curve_number,))

  def exec_close(self):
    self.close()

  def Pausing(self):
    toggle_id = self.menu_table['Pause ']
    if self._do_pause:
        self._menu.changeItem(toggle_id, 'Pause')
	self._do_pause = False
    else:
        self._menu.changeItem(toggle_id, 'Resume')
   	self._do_pause = True
    self.emit(PYSIGNAL("winpaused"),(self._curve_number,))

  def change_scale(self):
    toggle_id = self.menu_table['Linear Scale ']
    if self._do_linear_scale:
# click means change to log scale
      self._do_linear_scale = False
      self._menu.changeItem(toggle_id, 'Linear Scale')
      self._plotzoom.setAxisOptions(QwtPlot.yLeft, QwtAutoScale.Logarithmic)
      self._plotzoom.replot()
    else:
      self._do_linear_scale = True
      self._menu.changeItem(toggle_id, 'Log Scale')
      self._plotzoom.setAxisOptions(QwtPlot.yLeft, QwtAutoScale.None)
      self._plotzoom.replot()

  def change_scale_type(self):
# click means change to fixed scale
    toggle_id = self.menu_table['Fixed Scale ']
    if self._do_fixed_scale:
      self._do_fixed_scale = False
      self._menu.changeItem(toggle_id, 'Fixed Scale')
      self._plotzoom.setAxisAutoScale(QwtPlot.yLeft)
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
      self._plotzoom.setAxisScale(QwtPlot.yLeft, min_value, max_value)
      self._plotzoom.replot()

  def cancel_scale_request(self):
    if self._do_fixed_scale:
      toggle_id = self.menu_table['Fixed Scale ']
      self._menu.changeItem(toggle_id, 'Fixed Scale')
      self._plotzoom.setAxisAutoScale(QwtPlot.yLeft)
      self._do_fixed_scale = False
  
  def update_plot(self,y_values):
    if not self._do_pause:
      self._y_values = y_values
      self._plotzoom.setCurveData(self._crv, self._x_values, self._y_values)
      self.get_max()
      self._plotzoom.replot()

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
      self._plotzoom.print_(printer, filter)

  def setDataLabel(self, data_label):
    self._data_label = data_label
    self._zoom_plot_label = self._data_label + ": Channel " + str(self._curve_number) + " Sequence (oldest to most recent)"
    self._plotzoom.setAxisTitle(QwtPlot.xBottom, self._zoom_plot_label)


  def zoom(self):
    """ Zoom the curve in the main plot
        if unzoom is clicked
        disable zooming and put zooming flag back to FALSE
        else 
        put zooming flag to opposite of what it was
        See value of _d_zoom
        set corresponding text on the zoom button
    """ 
    if self._d_zoomActive:
      # Disable Zooming.
      self._plotzoom.setAxisAutoScale(QwtPlot.yLeft)
      self._plotzoom.setAxisAutoScale(QwtPlot.xBottom)
      self._plotzoom.replot()
      self._d_zoom = False
      self._d_zoomActive = 0
    else:
      if self._d_zoom:
        self._d_zoom = False
      else:
        self._d_zoom =  True
    
    toggle_id = self.menu_table['Zoom ']
    if self._d_zoom:
      self._menu.changeItem(toggle_id, 'Unzoom')
    else:
      self._menu.changeItem(toggle_id, 'Zoom')


  def plotMouseMoved(self, e):
    """	Gets x and y position of the mouse on the plot according to axis' value
        set right text on the button and underneath the plot
    """
# (I) e (QMouseEvent) Mouse event
    lbl = QString("Event=")
    lbl2 = QString("")
    lbl2.setNum(self._plotzoom.invTransform(QwtPlot.xBottom, e.pos().x() ), 'g', 3)
    lbl += lbl2 + ",  Signal="
    lbl2.setNum(self._plotzoom.invTransform(QwtPlot.yLeft, e.pos().y() ), 'g', 3)
    lbl += lbl2
#   self._ControlFrame._lblInfo.setText(lbl)

  def plotMousePressed(self, e):
    """ Gets position of the mouse on the main plot
        puts the mouse where it goes on the plot
        Depending on the position of the zoom button
        if _d_zoom
        draws a rectangle
        if not
        the mouse pointer appears as a cross
    """
    if Qt.RightButton == e.button():
      e.accept()
      self._menu.popup(e.globalPos());     
    else:
      # store position
      self._p1 = e.pos()

      # update cursor pos display
      self.plotMouseMoved(e)
    
      if self._d_zoom and not self._d_zoomActive:
        self._plotzoom.setOutlineStyle(Qwt.Rect) 
      else:
        self._plotzoom.setOutlineStyle(Qwt.Cross)

  def plotMouseReleased(self, e):
    """ If the zoom button is pressed 
        get the coordinates of the rectangle to zoom
        set the axis
        else
        if the offset is placed to its max value
        find to what curve the click corresponds
        call function to create the zoom in a new window
    """
    if self._d_zoom and not self._d_zoomActive:
      self._d_zoomActive = 1
      x1 = min(self._p1.x(), e.pos().x())
      x2 = max(self._p1.x(), e.pos().x())
      y1 = min(self._p1.y(), e.pos().y())
      y2 = max(self._p1.y(), e.pos().y())
      # Set fixed scales
      self._plotzoom.setAxisScale(QwtPlot.yLeft,self._plotzoom.invTransform(QwtPlot.yLeft,y1),self._plotzoom.invTransform(QwtPlot.yLeft,y2))
# unfortunately, if self._plotzoom.invTransform(QwtPlot.xBottom,x2) is
# less than self._plotzoom.invTransform(QwtPlot.xBottom,x1), 
# the QWT plotter will invert the X axis direction .... sigh
# this may affect zoom in on e.g. velocity plots
      self._plotzoom.setAxisScale(QwtPlot.xBottom,self._plotzoom.invTransform(QwtPlot.xBottom,x1),self._plotzoom.invTransform(QwtPlot.xBottom,x2))
      self._plotzoom.replot()
#     self._ControlFrame._lblInfo.setText(_cursorInfo)
      self._plotzoom.setOutlineStyle(Qwt.Triangle)

  def closeEvent(self, ce):
    if self._do_close:
      ce.accept()
    else:
      ce.ignore()
    #---------------------------------------------
    # Don't call the base function because
    # we want to ignore the close event
    #---------------------------------------------

  def update_display_axis(self):
    """ Extract X-axis type from incoming GlishRecord Structure
        Calculate X-axis parameters
        Replot the current spectrum
    """
# undo a zoom if zooming is active
    if self._d_zoomActive:
      self._plotzoom.setAxisAutoScale(QwtPlot.yLeft)
      self._plotzoom.setAxisAutoScale(QwtPlot.xBottom)
      self._d_zoom = FALSE
      self._d_zoomActive = 0
      toggle_id = self.menu_table['Zoom ']
      self._menu.changeItem(toggle_id, 'Zoom')
      if self._max_crv >= 0:
        self._plotzoom.setCurveData(self._max_crv, self._x_values, self._max_envelop)
      if self._min_crv >= 0:
        self._plotzoom.setCurveData(self._min_crv, self._x_values,self._min_envelop)
      self._plotzoom.setCurveData(self._crv, self._x_values, self._y_values)
      self._plotzoom.replot()

  def resize_x_axis(self):
    if self._max_crv >= 0:
      self._plotzoom.setCurveData(self._max_crv, self._x_values, self._max_envelop)
    if self._min_crv >= 0:
      self._plotzoom.setCurveData(self._min_crv, self._x_values, self._min_envelop)
    self._plotzoom.setCurveData(self._crv, self._x_values, self._y_values)

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

