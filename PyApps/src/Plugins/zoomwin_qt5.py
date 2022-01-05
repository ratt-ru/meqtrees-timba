#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
#  (c) 2013.				 (c) 2011.
#  National Research Council		 Conseil national de recherches
#  Ottawa, Canada, K1A 0R6 		 Ottawa, Canada, K1A 0R6
#
#  This software is free software;	 Ce logiciel est libre, vous
#  you can redistribute it and/or	 pouvez le redistribuer et/ou le
#  modify it under the terms of	         modifier selon les termes de la
#  the GNU General Public License	 Licence Publique Generale GNU
#  as published by the Free		 publiee par la Free Software
#  Software Foundation; either	 	 Foundation (version 3 ou bien
#  version 2 of the License, or	 	 toute autre version ulterieure
#  (at your option) any later	 	 choisie par vous).
#  version.
#
#  This software is distributed in	 Ce logiciel est distribue car
#  the hope that it will be		 potentiellement utile, mais
#  useful, but WITHOUT ANY		 SANS AUCUNE GARANTIE, ni
#  WARRANTY; without even the	 	 explicite ni implicite, y
#  implied warranty of			 compris les garanties de
#  MERCHANTABILITY or FITNESS FOR	 commercialisation ou
#  A PARTICULAR PURPOSE.  See the	 d'adaptation dans un but
#  GNU General Public License for	 specifique. Reportez-vous a la
#  more details.			 Licence Publique Generale GNU
#  					 pour plus de details.
#
#  You should have received a copy	 Vous devez avoir recu une copie
#  of the GNU General Public		 de la Licence Publique Generale
#  License along with this		 GNU en meme temps que ce
#  software; if not, contact the	 logiciel ; si ce n'est pas le
#  Free Software Foundation, Inc.	 cas, communiquez avec la Free
#  at http://www.fsf.org.		 Software Foundation, Inc. au
#						 http://www.fsf.org.
#
#  email:				 courriel:
#  business@hia-iha.nrc-cnrc.gc.ca	 business@hia-iha.nrc-cnrc.gc.ca
#
#  National Research Council		 Conseil national de recherches
#      Canada				    Canada
#  Herzberg Institute of Astrophysics	 Institut Herzberg d'astrophysique
#  5071 West Saanich Rd.		 5071 West Saanich Rd.
#  Victoria BC V9E 2E7			 Victoria BC V9E 2E7
#  CANADA					 CANADA
#

# this is a python translation of the ACSIS c++ zoomwin.cc program
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys
import numpy
import numpy

from qwt.qt.QtGui import QApplication, QHBoxLayout, QWidget
from qwt.qt.QtCore import Qt, pyqtSignal
from qwt import QwtPlot, QwtPlotCurve

from Timba.Plugins.display_image_qt5 import QwtImageDisplay

#widget to show a zoomed chanel of the plot

class ZoomPopup(QWidget):

  winclosed = pyqtSignal(int)
  winpaused = pyqtSignal(int)
  save_zoom_display = pyqtSignal(str,int)
  image_auto_scale = pyqtSignal(int)
  image_scale_values = pyqtSignal(float, float)
 

  def __init__(self, CurveNumber, x_values, y_values , flags, pen, parent=None, name=None):
    """ Initialises all the variables.  
        creates the main zoom plot
        connects the qt signals
    """


    QWidget.__init__(self, parent)
    self.setWindowTitle('Channel ' + str(CurveNumber))
    self._parent = parent
    self._d_zoomActive = self._d_zoom = False
    self._curve_number = CurveNumber
    self.curves = {}

    self._do_close = True   # enable closing by window manager
    self._do_pause = False   # pause mode is False at startup
    self._compare_max = False
    self._do_linear_scale = True  # linear Y axis scale by default
    self._do_fixed_scale = False  # auto scaling by default
    self._array_label = "Channel "
 
    #Create the plot for selected curve to zoom
    self._plotter = QwtImageDisplay(self)
    self._plotter.setZoomDisplay()

    self._zoom_plot_label = self._array_label + str(self._curve_number) + " Sequence (oldest to most recent)"

    self._max_crv = -1  # negative value used to indicate that this display
    self._min_crv = -1  # is not being used

  #####end of parameters set for the plot#######/

    # we seem to need a layout for PyQt
    box1 = QHBoxLayout( self )
    box1.addWidget(self._plotter)
#   self.plotPrinter = plot_printer_qt5.plot_printer(self._plotter)

    self._plotter.winpaused.connect(self.Pausing)
    self._plotter.compare.connect(self.do_compare)
#   self._plotter.do_print.connnect(self.plotPrinter.do_print)
    self._plotter.save_display.connect(self.handle_save_display)


    # insert flags ?   
    self._plotter.initVellsContextMenu()
    self.update_plot(y_values, flags)
    self.show()

  def handle_save_display(self, title):
    self.save_zoom_display.emit(self._zoom_plot_label, self._curve_number)

  def do_compare_max(self, x_values):
    ### instantiate the envelop that will show min/max deviations
    self._max_envelop = self._y_values
    self._min_envelop = self._y_values
    self._max_crv = QwtPlotCurve('Zoomed max curve')
    self._max_crv.attach(self._plotter)
    self._min_crv = QwtPlotCurve('Zoomed min curve')
    self._min_crv.attach(self._plotter)
    self._max_crv.setData(x_values,self._max_envelop)
    self._min_crv.setData(x_values,self._min_envelop)
    self._compare_max = True

  def do_compare(self):
    print('in zoomwin do_compare')
    if self._compare_max:
      self.stop_compare_max()
      self._compare_max = False
    else:
      self._max_envelop = self._y_values
      self._min_envelop = self._y_values
      self._max_crv = QwtPlotCurve('Zoomed max curve')
      self._max_crv.attach(self._plotter)
      self._min_crv = QwtPlotCurve('Zoomed min curve')
      self._min_crv.attach(self._plotter)
      self._max_crv.setData(x_values,self._max_envelop)
      self._min_crv.setData(x_values,self._min_envelop)
      self._compare_max = True
    self.reset_max()

  def stop_compare_max(self):
    if self._compare_max:
      self._max_envelop = 0.0
      self._min_envelop = 0.0
      self._max_crv.detach()
      self._min_crv.detach()
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
    self.winpaused.emit(self._curve_number)

  def change_scale_type(self):
# click means change to fixed scale
    toggle_id = self.menu_table['Fixed Scale ']
    if self._do_fixed_scale:
      self._do_fixed_scale = False
      self._menu.changeItem(toggle_id, 'Fixed Scale')
      self._plotter.setAxisAutoScale(QwtPlot.yLeft)
      self.image_auto_scale.emit(0)
    else:
      self._do_fixed_scale = True
      self._menu.changeItem(toggle_id, 'Auto Scale')
# find current data min and max
      scale_max = self._y_values.max()
      scale_min = self._y_values.min()

  def set_scale_values(self,max_value,min_value):
    if self._do_fixed_scale:
      self.image_scale_values.emit(max_value,min_value)
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
      abs_flags = numpy.absolute(flags)
      if abs_flags.max() > 0:
        if len(flags) == len(self._y_values):
          self._plotter.setFlagsData(flags,flip_axes=True)
          self._plotter.set_flag_toggles_active(True,False)
      else:
        self._plotter.set_flag_toggles_active(False,False)
      self._plotter.array_plot(incoming_plot_array=self._y_values, flip_axes=True)

#     self.get_max()
      self._plotter.replot()

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
    self._plotter._x_title = self._zoom_plot_label;
    self.setWindowTitle(self._zoom_plot_label)

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
      self.winclosed.emit(self._curve_number)
      ce.accept()
    else:
      ce.ignore()
    #---------------------------------------------
    # Don't call the base function because
    # we want to ignore the close event
    #---------------------------------------------

def main(args):
    app = QApplication(args)
    x_values = numpy.array([1.0,2.0,3.0,4.0])
    y_values = numpy.array([15.0,25.0,35.0,45.0])
    flags = numpy.array([0.0,0.0,0.0,0.0])
    demo = ZoomPopup(1, x_values, y_values,flags, Qt.yellow,None, None )
    demo.show()
    app.exec_()


# Admire
if __name__ == '__main__':
    main(sys.argv)

