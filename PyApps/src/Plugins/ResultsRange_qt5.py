#usr/bin/env python
# -*- coding: utf-8 -*-

# a class to generate control buttons etc for use in controlling N-dimensional
# displays

#% $Id: ResultsRange.py 6836 2009-03-05 18:55:17Z twillis $ 

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
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys

from qwt.qt.QtGui import (QApplication, QMainWindow, QDialog, QGridLayout,QHBoxLayout,
         QLabel, QSizePolicy, QSlider, QPushButton, QVBoxLayout, QSpinBox, QSpacerItem, QTabWidget,QDoubleSpinBox)
from qwt.qt.QtGui import QPen, QColor,QWidget, QImage, qRgba, QFont, QFontInfo, QMenu, QActionGroup, QAction
from qwt.qt.QtCore import Qt, QSize, QObject, pyqtSignal

from Timba.Plugins.BufferSizeDialog_qt5 import BufferSizeDialog


# The ResultsRange class is directly adapted from the Qt/PyQt 
# tutorial code examples.
#
# It creates a simple spinbox and slider that is used to select a data
# set for display with the result plotter. It is rather similar to the
# AxisRange class used with the ND-Controller, but the layout is
# different.

results_range_help = \
'''
This widget displays a spinbox and a slider. The spinbox and the slider both have the same value. Changing one or the other causes an event to be sent to the visualization system with a request to change the array index of the displayed data. The visualization display is then updated. The spinbox is wrapped around so that one can go directly from the highest index to the lowest.<br><br>

When you click in the area of the widget with the right mouse button a context menu will be shown. In the case of the <b>3-dimensional display</b>, this context menu will allow you to select a new active plane - one of the X, Y or Z axes. It also gives you the possibility of switching back to the 2-dimensional display. In the case of the results <b>history sequence</b> display, the menu offers you the single option of changing the number of sequential records that can be stored. If you select this option, a small dialog will appear that allows you to modify the allowable number of records that can be stored. The default is 10.<br><br> 
'''

class ResultsRange(QWidget):

#   result_index = pyqtSignal(float)
    result_index = pyqtSignal('PyQt_PyObject')
    X_axis_selected = pyqtSignal()
    Y_axis_selected = pyqtSignal()
    Z_axis_selected = pyqtSignal()
    align_camera = pyqtSignal()
    twoD_display_requested = pyqtSignal()
    save_display = pyqtSignal()
    postscript_requested = pyqtSignal()
    doubleValueChanged = pyqtSignal(float)
    update_requested = pyqtSignal()
    show_ND_Controller = pyqtSignal()
    update_scale = pyqtSignal()
    set_auto_scaling = pyqtSignal()
    adjust_results_buffer_size = pyqtSignal(int)
    display_summary_plot = pyqtSignal()


    def __init__(self, parent=None, name="",horizontal=False,draw_scale=True,hide_slider=False, use_int=False, add_spacer=True):
#     QWidget.__init__(self, parent, name)
      QWidget.__init__(self, parent)

      self.menu_table = {
      'Adjust results buffer size': 301,
      'Display summary plot': 302,
      'X Axis': 303,
      'Y Axis': 304,
      'Z Axis': 305,
      'Show 2D Display': 306,
      'Update': 307,
      'Toggle ND Controller': 308,
      'Print to Postscript file': 309,
      'Align Camera': 310,
      'Reset Auto Scaling': 312,
      'Save Display in PNG Format': 313,
      }

      self.horizontal = horizontal
      self.hide_slider = hide_slider
      self.use_int = use_int
      self.add_spacer = add_spacer
      self.allow_emit = False
      self.allow_summary = False
      self.summary_request = True
      self.toggle_ND_Controller = 1
      self.toggle_scale_display = False
      self.draw_scale = draw_scale
      self.menu = None
      self.maxVal = 100
      self.minVal = 0
      self.scaler = 1
      self.label_info = QLabel('', self)
      self.string_info =  ' '
      self.offset_index = -1
      if self.horizontal or self.use_int:
        self.spinbox = QSpinBox(self)
      else:
        self.spinbox = QDoubleSpinBox(self)
        self.spinbox.setSingleStep(0.1)
      self.spinbox.setMinimum(self.minVal)
      self.spinbox.setMaximum(self.maxVal)

      if self.horizontal:
        self.slider = QSlider(Qt.Horizontal, self)
        if self.draw_scale:
          self.slider.setTickPosition(QSlider.TicksBelow)
          self.slider.setTickInterval(self.minVal)
        self.slider.setRange(self.minVal, self.maxVal)
        self.slider.valueChanged[int].connect(self.update_slider)
        self.spinbox.valueChanged[int].connect(self.update_spinbox)
      else:
         #print('creating standard vertical QSlider')
         self.slider = QSlider(Qt.Vertical, self)
         if not self.use_int:
           self.scaler = 10000000
         min = self.scaler * self.minVal
         max = self.scaler * self.maxVal
         if self.draw_scale:
           self.slider.setTickPosition(QSlider.TicksRight)
           step = int((max-min) /20)
           #print('slider step should me ', step)
           self.slider.setTickInterval(step)
         #print('slider min and max', min,max)
         self.slider.setRange(min, max)
         self.slider.valueChanged[int].connect(self.update_slider)

        # we may not want a slider - e.g. when selecion tab pages in collections plotter
      self.spinbox.setWrapping(True)
      #print('wrapping should be set')

      if self.hide_slider:
        self.slider.hide()

      if self.horizontal or self.use_int:
        self.spinbox.valueChanged[int].connect(self.update_spinbox)
      else:
        self.spinbox.valueChanged[float].connect(self.update_spinbox)

      if self.horizontal:
        self.label_info1 = QLabel('          ', self)
        self.layout = QHBoxLayout(self)
        if self.add_spacer:
          spacer = QSpacerItem(22,9,QSizePolicy.Expanding,QSizePolicy.Minimum)
          self.layout.addItem(spacer)
        self.layout.addWidget(self.label_info)
        self.layout.addWidget(self.spinbox)
        self.layout.addWidget(self.label_info1)
        self.layout.addWidget(self.slider)
        self.setValue()
      else:
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label_info)
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.spinbox)
        if self.add_spacer:
          spacer = QSpacerItem(9,22,QSizePolicy.Minimum,QSizePolicy.Expanding)
          self.layout.addItem(spacer)
        self.setValue(0,reset_auto=True)

# add on-line help
      self.setWhatsThis(results_range_help)

    def setLabel(self, string_value= '', align=None):
      """ set current displayed label """
      self.label_info.setText(string_value + self.string_info);
      if align is not None:
        self.label_info.setAlignment(align);

    def setStringInfo(self, string_value= ''):
      """ assign a default leading string """
      self.string_info = string_value

    def set_decimals(self,step):
      if step < 0.1:
        self.spinbox.setDecimals(2)
      if step < 0.01:
        self.spinbox.setDecimals(3)
      if step < 0.001:
        self.spinbox.setDecimals(4)
      if step < 0.0001:
        self.spinbox.setDecimals(5)
      if step < 0.0001:
        self.spinbox.setDecimals(5)


    def setMinValue(self, min_value=0):
      """ reset allowed minimum value for spinbox and slider """
      #print('in SetMinValue with min_value', min_value)
      self.minVal = min_value
      if self.horizontal or self.use_int:
        self.spinbox.setMinimum(self.minVal)
      else:
        step = (self.maxVal-self.minVal)/20.0
        self.set_decimals(step)
        self.spinbox.setSingleStep(step)
        self.spinbox.setRange(self.minVal,self.maxVal)
      min = self.scaler * self.minVal
      max = self.scaler * self.maxVal
      #print('in setMinValue slider range set to ', min,max)
      self.slider.setRange(min, max)

    def setMaxValue(self, max_value= 0, allow_shrink=True):
      """ reset allowed maximum value for spinbox and slider """
      #print('in setMaxValue with max_value and self.maxVal`', max_value, self.maxVal)
      #print('in setMaxValue with allow_shrink = `',allow_shrink)
      if max_value < self.maxVal: 
        if allow_shrink:
          #print('we can shrink')
          self.maxVal = max_value
          min = self.scaler * self.minVal
          max = self.scaler * self.maxVal
          #print('in setMaxValue slider range set to ', min,max)
          self.slider.setRange(min, max)
          if self.horizontal or self.use_int:
            self.spinbox.setMaximum(self.maxVal)
# adding  this next line
            #print('resetting spinbox range to ', min, max)
            self.spinbox.setRange(min, max)
          else:
            self.spinbox.setSingleStep((self.maxVal-self.minVal)/20.0)
            self.spinbox.setRange(self.minVal, self.maxVal)
      else:
        if max_value > self.maxVal:
          self.maxVal = max_value
          min = self.scaler * self.minVal
          max = self.scaler * self.maxVal
          self.slider.setRange(min , max)
          #print('in setMaxValue slider range set to ', min,max)
          if self.horizontal or self.use_int:
            self.spinbox.setMaximum(self.maxVal)
          else:
            step = (self.maxVal-self.minVal)/20.0
            self.set_decimals(step)
            self.spinbox.setSingleStep(step)
            self.spinbox.setRange(self.minVal, self.maxVal)
      self.slider.setValue(self.scaler*max_value)
      self.spinbox.setValue(max_value)

    def setValue(self, value= 0, reset_auto=False):
      """ set current values shown in spinbox and slider """
      #print('in setValue raw value is  ', value)
      max = self.scaler*value
      self.slider.setValue(max)
      #print('in setValue spinbox value set to ', max)
      self.spinbox.setValue(value)
      self.initContextmenu(reset_auto)

    def setRange(self, range_value, update_value = True):
      """ define range of values shown with slider """
      #print('in setRange range value is  ', range_value)
      if range_value <= self.maxVal:
        min = self.scaler * self.minVal
        max = self.scaler * range_value
        #print('in setRange slider range set to ', max)
        self.slider.setRange(min, max)
        if self.draw_scale:
          step = int((max-min) /20)
          #print('slider step should me ', step)
          self.slider.setTickInterval(step)
        if self.horizontal or self.use_int:
          #print('spinbox max range should be', range_value)
          self.spinbox.setMaximum(range_value)
        else:
          step = (range_value-self.minVal)/20.0
          self.set_decimals(step)
          self.spinbox.setSingleStep(step)
          self.spinbox.setRange(self.minVal,range_value)
        if update_value:
          self.setValue(range_value)

    def update_slider(self, raw_slider_value):
      """ update spinbox value as function of slider value """
      #print('raw incoming slider value', raw_slider_value)
      if self.horizontal or self.use_int:
        slider_value = raw_slider_value 
        self.spinbox.setValue(int(slider_value))
      else:
        slider_value = float(raw_slider_value) / self.scaler  
        #print('update slider value', slider_value)
        self.spinbox.setValue(slider_value)

    def update_spinbox(self, spin_value):
      """ update displayed contents of spinbox """
      #print('incoming spin value', spin_value)
      self.slider.setValue(int(self.scaler* spin_value))
      if self.allow_emit:
        #print 'emitting result_index signal ', spin_value + self.offset_index
        self.result_index.emit(spin_value + self.offset_index)

    def set_emit(self, permission=True):
      """ flag to allow emitting of Qt signals """
      self.allow_emit = permission

    def X_Axis_Selected(self):
      """ emit signal to select X Axis for 3D display """
      if self.allow_emit:
#       print 'emitting X_axis_selected signal'
        self.X_axis_selected.emit(True)

    def Y_Axis_Selected(self):
      """ emit signal to select Y Axis for 3D display """
      if self.allow_emit:
        self.Y_axis_selected.emit(True)

    def Z_Axis_Selected(self):
      """ emit signal to select Z Axis for 3D display """
      if self.allow_emit:
        self.Z_axis_selected.emit(True)

    def align_camera(self):
      """ emit signal to align camera to current axis """
      #print('in align_camara')
      if self.allow_emit:
        self.align_camera.emit(True)


    def request_2D_display(self):
      """ emit signal to request 2D display """
      if self.allow_emit:
        self.twoD_display_requested.emit(True)

    def request_PNG_file(self):
      """ emit signal to request PNG printout """
      if self.allow_emit:
        self.save_display.emit(True)

    def request_postscript(self):
      """ emit signal to request Postscript printout """
      if self.allow_emit:
        self.postscript_requested.emit(True)

    def requestUpdate(self):
      """ emit signal to request update to array (for testing) """
      if self.allow_emit:
        self.update_requested.emit(True)

    def toggle_ND_controller(self):
      """ emit signal to toggle ND Controller on or off """
      toggle_id = self.menu_table['Toggle ND Controller']
      if self.toggle_ND_Controller == 1:
        self.toggle_ND_Controller = 0
        self._toggle_nd_controller.setText('Show ND Controller')
      else:
        self.toggle_ND_Controller = 1
        self._toggle_nd_controller.setText('Hide ND Controller')
      if self.allow_emit:
        self.show_ND_Controller.emit(self.toggle_ND_Controller)

    def set_summary(self, summary=True):
      """ override default value for allowing summary plot """
      self.allow_summary = summary
      toggle_id = self.menu_table['Display summary plot']
      self.menu.setItemVisible(toggle_id, self.allow_summary)

    def set_offset_index(self, offset):
      """ override default value for offset index """
      self.offset_index = offset

    def setTickInterval(self, tick_interval):
      """ override default tick interval for slider """
      if self.horizontal or self.use_int:
        self.slider.setTickInterval(tick_interval)
      else:
        self.slider.setTickInterval(self.scaler*tick_interval)

    def handleAutoScaling(self):
      """ emit signal to request 2D display """
      if self.allow_emit:
        self.set_auto_scaling.emit(True)
        self.setValue(self.maxVal,reset_auto=True)

    def handle_menu_request(self, menuid):
      """ handle requested menu option """
      #print(' handling menu request with id ', menuid)
      if menuid == self.menu_table['Reset Auto Scaling']:
        self.handleAutoScaling()
      elif menuid == self.menu_table['Display summary plot']:
        self.requestSummary()

    def initContextmenu(self, reset_auto = False):
      """Initialize the result buffer context menu """
      if self.menu is None:
        self.menu = QMenu(self)
        self.menu.triggered.connect(self.handle_menu_request)
        toggle_id = self.menu_table['Reset Auto Scaling']
        self._reset_auto_scaling = QAction('Reset Auto Scaling',self)
        self._reset_auto_scaling.setData(toggle_id)
        self.menu.addAction(self._reset_auto_scaling)
        if reset_auto:
          self._reset_auto_scaling.setVisible(True)
        else:
          self._reset_auto_scaling.setVisible(False)

        toggle_id = self.menu_table['Adjust results buffer size']
        self._adjust_results_buffer_size = QAction('Adjust results buffer size',self)
        self._adjust_results_buffer_size.setData(toggle_id)
        self.menu.addAction(self._adjust_results_buffer_size)
        self._adjust_results_buffer_size.triggered.connect(self.handleBufferSize)
        if reset_auto:
          self._adjust_results_buffer_size.setVisible(False)
        else:
          self._adjust_results_buffer_size.setVisible(True)

# option for summary plot
        toggle_id = self.menu_table['Display summary plot']
        self._display_summary_plot = QAction('Display summary plot',self)
        self.menu.addAction(self._display_summary_plot)
        self._display_summary_plot.setVisible(False)
        self._display_summary_plot.setData(toggle_id)

# options for 3D Display
        toggle_id = self.menu_table['X Axis']
        self._x_axis = QAction('X Axis',self)
        self.menu.addAction(self._x_axis)
        self._x_axis.setVisible(False)
        self._x_axis.setData(toggle_id)
        self._x_axis.triggered.connect(self.X_Axis_Selected)

        toggle_id = self.menu_table['Y Axis']
        self._y_axis = QAction('Y Axis',self)
        self.menu.addAction(self._y_axis)
        self._y_axis.setVisible(False)
        self._y_axis.setData(toggle_id)
        self._y_axis.triggered.connect(self.Y_Axis_Selected)

        toggle_id = self.menu_table['Z Axis']
        self._z_axis = QAction('Z Axis',self)
        self.menu.addAction(self._z_axis)
        self._z_axis.setVisible(False)
        self._z_axis.setData(toggle_id)
        self._z_axis.triggered.connect(self.Z_Axis_Selected)

        toggle_id = self.menu_table['Align Camera']
        self._align_camera = QAction('Align Camera',self)
        self.menu.addAction(self._align_camera)
        self._align_camera.setVisible(False)
        self._align_camera.setData(toggle_id)
        self._align_camera.setText('Align Camera to Current Axis')
        self._align_camera.triggered.connect(self.align_camera)

        toggle_id = self.menu_table['Show 2D Display']
        self._show_2d_display = QAction('Show 2D Display',self)
        self.menu.addAction(self._show_2d_display)
        self._show_2d_display.setVisible(False)
        self._show_2d_display.setData(toggle_id)
        self._show_2d_display.triggered.connect(self.request_2D_display)

        toggle_id = self.menu_table['Toggle ND Controller']
        self._toggle_nd_controller = QAction('Toggle ND Controller',self)
        self.menu.addAction(self._toggle_nd_controller)
        self._toggle_nd_controller.setVisible(False)
        self._toggle_nd_controller.setData(toggle_id)
        self._toggle_nd_controller.setText('Hide ND Controller')
        self._toggle_nd_controller.triggered.connect(self.toggle_ND_controller)

        toggle_id = self.menu_table['Update']
        self._update = QAction('Update',self)
        self.menu.addAction(self._update)
        self._update.setVisible(False)
        self._update.setData(toggle_id)
        self._update.triggered.connect(self.requestUpdate)

        toggle_id = self.menu_table['Print to Postscript file']
        self._print_to_postscript_file = QAction('Print to Postscript file',self)
        self.menu.addAction(self._print_to_postscript_file)
        self._print_to_postscript_file.setVisible(False)
        self._print_to_postscript_file.setData(toggle_id)
        self._print_to_postscript_file.triggered.connect(self.request_postscript)

        toggle_id = self.menu_table['Save Display in PNG Format']
        self._save_display_in_png_format = QAction('Save Display in PNG Format',self)
        self.menu.addAction(self._save_display_in_png_format)
        self._save_display_in_png_format.setVisible(False)
        self._save_display_in_png_format.setData(toggle_id)
        self._save_display_in_png_format.triggered.connect(self.request_PNG_file)

    def hideNDControllerOption(self):
      """ do not allow the user to toggle ND Controller """
      self._toggle_nd_controller.setVisible(False)

    def setXMenuLabel(self, text):
      """ update X axis context menu label """
      self._x_axis.setText(text)

    def setYMenuLabel(self, text):
      """ update Y axis context menu label """
      self._y_axis.setText(text)

    def setZMenuLabel(self, text):
      """ update Z axis context menu label """
      self._z_axis.setText(text)

    def disableContextmenu(self):
      """ delete the result buffer context menu """
      if not self.menu is None:
          self.menu.setParent(QWidget())
          self.menu = None

    def init3DContextmenu(self):
      """add 3D options to context menu """
      if self.menu is None:
        self.initContextmenu()
# display options for 3D Display
      self._x_axis.setVisible(True)
      self._y_axis.setVisible(True)
      self._z_axis.setVisible(True)
      self._align_camera.setVisible(True)
      self._show_2d_display.setVisible(True)
      self._toggle_nd_controller.setVisible(True)
      self._print_to_postscript_file.setVisible(True)
      self._save_display_in_png_format.setVisible(True)
      self._adjust_results_buffer_size.setVisible(False)

    def initWarpContextmenu(self):
      """add options for warped surface to context menu """
      if self.menu is None:
        self.initContextmenu()
# display options for 3D Display
      self._x_axis.setVisible(False)
      self._y_axis.setVisible(False)
      self._z_axis.setVisible(False)
      self._align_camera.setVisible(False)
      self._show_2d_display.setVisible(True)
      self._toggle_nd_controller.setVisible(True)
      self._print_to_postscript_file.setVisible(True)
      self._save_display_in_png_format.setVisible(True)
      self._toggle_vtk_scale.setVisible(True)

      self._adjust_results_buffer_size.setVisible(False)

    def displayUpdateItem(self):
      self._update.setVisible(True)

    def setResultsBuffer(self, result_value):
      """ redefine the allowable maximum number of values """
      if result_value < 0:
        return
      self.maxVal = result_value
      self.slider.setRange(self.minVal, self.maxVal)
      if self.horizontal or self.use_int:
        self.slider.setTickInterval((self.maxVal - self.minVal) / 10)
      else:
        self.slider.setStep((self.maxVal - self.minVal) / 10)
      self.spinbox.setMaximum(self.maxVal)
      self.adjust_results_buffer_size.emit(result_value)

    def handleBufferSize(self):
      """ callback to handle 'Adjust buffer' request from the context menu """
      results_dialog = BufferSizeDialog(self.maxVal, self)
      results_dialog.return_value.connect(self.setResultsBuffer)
      results_dialog.show()

    def requestSummary(self, menuid):
      """ callback to handle 'summary plot' request from the context menu """
      if menuid == self.menu_table['Display summary plot']:
        self.display_summary_plot.emit(self.summary_request)
        if self.summary_request:
          self.summary_request = False
          self.menu.changeItem(menuid, 'Discard summary plot')
        else:
          self.summary_request = True
          self.menu.changeItem(menuid, 'Display summary plot')

    def mousePressEvent(self, e):
      if Qt.RightButton == e.button():
        e.accept()
        self.menu.popup(e.globalPos());

#   def contextMenuEvent(self,ev):
#     """ The existence of this function should cause any 
#         higher-level context menu to be ignored when the 
#         right mouse button is clicked inside the widget.
#     """
#     ev.accept()



# the following tests the ResultsRange class
def make():
    demo = ResultsRange(horizontal=False, hide_slider=False)
#   demo = ResultsRange(horizontal=True, use_int=True,hide_slider=False)
    demo.setRange(0.005)
#   demo = ResultsRange()
#   demo.setRange(20)
    demo.show()
    demo.init3DContextmenu()
    return demo

# make()

def main(args):
    app = QApplication(args)
    demo = make()
#   app.setMainWidget(demo)
    app.exec_()

# main()

# Admire
if __name__ == '__main__':
    main(sys.argv)

