#!/usr/bin/env python2
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

import sys
#from qt import *
from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt

#from Timba.GUI.pixmaps import pixmaps
from .BufferSizeDialog_qt4 import *

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

class ResultsRange(Qt.QWidget):
    def __init__(self, parent=None, name="",horizontal=True,draw_scale=True):
#     Qt.QWidget.__init__(self, parent, name)
      Qt.QWidget.__init__(self, parent)

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
      'Toggle VTK Scale': 311,
      'Reset Auto Scaling': 312,
      'Save Display in PNG Format': 313,
      }

      self.horizontal = horizontal
      self.allow_emit = False
      self.allow_summary = False
      self.summary_request = True
      self.toggle_ND_Controller = 1
      self.toggle_scale_display = False
      self.menu = None
      self.maxVal = 10
      self.minVal = 0
      self.label_info = Qt.QLabel('', self)
      self.string_info =  ' '
      self.offset_index = -1
      if self.horizontal:
        self.spinbox = Qt.QSpinBox(self)
      else:
        self.spinbox = Qt.QDoubleSpinBox(self)
        self.spinbox.setSingleStep(0.1)
      self.spinbox.setMinimum(self.minVal)
      self.spinbox.setMaximum(self.maxVal)
      self.spinbox.setWrapping(True)

      if self.horizontal:
        self.slider = Qt.QSlider(Qt.Qt.Horizontal, self)
        if draw_scale:
          self.slider.setTickPosition(Qt.QSlider.TicksBelow)
          self.slider.setTickInterval(self.minVal)
        self.slider.setRange(self.minVal, self.maxVal)
        self.connect(self.slider, Qt.SIGNAL("valueChanged(int)"), self.update_slider)
        self.connect(self.spinbox, Qt.SIGNAL("valueChanged(int)"), self.update_spinbox)
      else:
        # There seems to be occasional problems with some PyQwt versions not
        # handling the QwtSlider.BgSlot parameter
        try:
          self.slider = Qwt.QwtSlider(self, Qt.Qt.Vertical,Qwt.QwtSlider.RightScale if draw_scale else Qwt.QwtSlider.NoScale,
                          Qwt.QwtSlider.BgSlot)
        except:
          self.slider = Qwt.QwtSlider(self, Qt.Qt.Vertical,Qwt.QwtSlider.RightScale if draw_scale else Qwt.QwtSlider.NoScale)
        self.slider.setRange(self.minVal, self.maxVal)
        self.slider.setStep(self.minVal)
        self.connect(self.slider, Qt.SIGNAL("valueChanged(double)"), self.update_slider)
        self.connect(self.spinbox, Qt.SIGNAL("valueChanged(double)"), self.update_spinbox)


      if self.horizontal:
        self.label_info1 = Qt.QLabel('          ', self)
        self.layout = Qt.QHBoxLayout(self)
        spacer = Qt.QSpacerItem(22,9,Qt.QSizePolicy.Expanding,Qt.QSizePolicy.Minimum)
        self.layout.addItem(spacer)
        self.layout.addWidget(self.label_info)
        self.layout.addWidget(self.spinbox)
        self.layout.addWidget(self.label_info1)
        self.layout.addWidget(self.slider)
        self.setValue()
      else:
        self.layout = Qt.QVBoxLayout(self)
        self.layout.addWidget(self.label_info)
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.spinbox)
        spacer = Qt.QSpacerItem(9,22,Qt.QSizePolicy.Minimum,Qt.QSizePolicy.Expanding)
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
      self.minVal = min_value
      if self.horizontal:
        self.spinbox.setMinimum(self.minVal)
      else:
        step = (self.maxVal-self.minVal)/20.0
        self.set_decimals(step)
        self.spinbox.setSingleStep(step)
        self.spinbox.setRange(self.minVal,self.maxVal)
      self.slider.setRange(self.minVal, self.maxVal)

    def setMaxValue(self, max_value= 0, allow_shrink=True):
      """ reset allowed maximum value for spinbox and slider """
      if max_value < self.maxVal: 
        if allow_shrink:
          self.maxVal = max_value
          self.slider.setRange(self.minVal, self.maxVal)
          if self.horizontal:
            self.spinbox.setMaximum(self.maxVal)
          else:
            self.spinbox.setSingleStep((self.maxVal-self.minVal)/20.0)
            self.spinbox.setRange(self.minVal, self.maxVal)
      else:
        if max_value > self.maxVal:
          self.maxVal = max_value
          self.slider.setRange(self.minVal, self.maxVal)
          if self.horizontal:
            self.spinbox.setMaximum(self.maxVal)
          else:
            step = (self.maxVal-self.minVal)/20.0
            self.set_decimals(step)
            self.spinbox.setSingleStep(step)
            self.spinbox.setRange(self.minVal, self.maxVal)
      self.slider.setValue(max_value)
      self.spinbox.setValue(max_value)

    def setValue(self, value= 0, reset_auto=False):
      """ set current values shown in spinbox and slider """
      self.slider.setValue(value)
      self.spinbox.setValue(value)
      self.initContextmenu(reset_auto)

    def setRange(self, range_value, update_value = True):
      """ define range of values shown with slider """
      if range_value <= self.maxVal:
        self.slider.setRange(self.minVal, range_value)
        if self.horizontal:
          self.spinbox.setMaximum(range_value)
        else:
          step = (range_value-self.minVal)/20.0
          self.set_decimals(step)
          self.spinbox.setSingleStep(step)
          self.spinbox.setRange(self.minVal,range_value)
        if update_value:
          self.setValue(range_value)

    def update_slider(self, slider_value):
      """ update spinbox value as function of slider value """
      if self.horizontal:
        self.spinbox.setValue(int(slider_value))
      else:
        self.spinbox.setValue(slider_value)

    def update_spinbox(self, spin_value):
      """ update displayed contents of spinbox """
      self.slider.setValue(spin_value)
      if self.allow_emit:
        self.emit(Qt.SIGNAL("result_index"),spin_value + self.offset_index)

    def set_emit(self, permission=True):
      """ flag to allow emitting of Qt signals """
      self.allow_emit = permission

    def X_Axis_Selected(self):
      """ emit signal to select X Axis for 3D display """
      if self.allow_emit:
#       print 'emitting X_axis_selected signal'
        self.emit(Qt.SIGNAL("X_axis_selected"),True)

    def Y_Axis_Selected(self):
      """ emit signal to select Y Axis for 3D display """
      if self.allow_emit:
        self.emit(Qt.SIGNAL("Y_axis_selected"),True)

    def Z_Axis_Selected(self):
      """ emit signal to select Z Axis for 3D display """
      if self.allow_emit:
        self.emit(Qt.SIGNAL("Z_axis_selected"),True)

    def align_camera(self):
      """ emit signal to align camera to current axis """
      print('in align_camara')
      if self.allow_emit:
        self.emit(Qt.SIGNAL("align_camera"),True)


    def request_2D_display(self):
      """ emit signal to request 2D display """
      if self.allow_emit:
        self.emit(Qt.SIGNAL("twoD_display_requested"),True)

    def request_PNG_file(self):
      """ emit signal to request PNG printout """
      if self.allow_emit:
        self.emit(Qt.SIGNAL("save_display"),True)

    def request_postscript(self):
      """ emit signal to request Postscript printout """
      if self.allow_emit:
        self.emit(Qt.SIGNAL("postscript_requested"),True)

    def requestUpdate(self):
      """ emit signal to request update to array (for testing) """
      if self.allow_emit:
        self.emit(Qt.SIGNAL("update_requested"),True)

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
        self.emit(Qt.SIGNAL("show_ND_Controller"),self.toggle_ND_Controller)

    def toggle_scale(self):
      """ emit signal to toggle VTK display of scales """
      toggle_id = self.menu_table['Toggle VTK Scale']
      if self.toggle_scale_display:
        self.toggle_scale_display = False
        self._toggle_vtk_scale.setText('Apply Scaling to VTK Display')
      else:
        self.toggle_scale_display = True
        self._toggle_vtk_scale.setText('Remove Scaling from VTK Display')
      if self.allow_emit:
        self.emit(Qt.SIGNAL("update_scale"),self.toggle_scale_display)

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
      if self.horizontal:
        self.slider.setTickInterval(tick_interval)
      else:
        self.slider.setStep(tick_interval)

    def handleAutoScaling(self):
      """ emit signal to request 2D display """
      if self.allow_emit:
        self.emit(Qt.SIGNAL("set_auto_scaling"),True)
        self.setValue(self.maxVal,reset_auto=True)

    def handle_menu_request(self, menuid):
      """ handle requested menu option """
      print(' handling menu request with id ', menuid)
      if menuid == self.menu_table['Reset Auto Scaling']:
        self.handleAutoScaling()
      elif menuid == self.menu_table['Display summary plot']:
        self.requestSummary()

    def reset_scale_toggle(self):
      """ reset options for toggling VTK scales to defaults """
      self.toggle_scale_display = False
      self._toggle_vtk_scale.setText('Apply Scaling to VTK Display')

    def initContextmenu(self, reset_auto = False):
      """Initialize the result buffer context menu """
      if self.menu is None:
        self.menu = Qt.QMenu(self)
        Qt.QObject.connect(self.menu,Qt.SIGNAL("triggered()"),self.handle_menu_request);
        toggle_id = self.menu_table['Reset Auto Scaling']
        self._reset_auto_scaling = Qt.QAction('Reset Auto Scaling',self)
        self._reset_auto_scaling.setData(Qt.QVariant(toggle_id))
        self.menu.addAction(self._reset_auto_scaling)
        if reset_auto:
          self._reset_auto_scaling.setVisible(True)
        else:
          self._reset_auto_scaling.setVisible(False)

        toggle_id = self.menu_table['Adjust results buffer size']
        self._adjust_results_buffer_size = Qt.QAction('Adjust results buffer size',self)
        self._adjust_results_buffer_size.setData(Qt.QVariant(toggle_id))
        self.menu.addAction(self._adjust_results_buffer_size)
        self.connect(self._adjust_results_buffer_size, Qt.SIGNAL('triggered()'), self.handleBufferSize)
        if reset_auto:
          self._adjust_results_buffer_size.setVisible(False)
        else:
          self._adjust_results_buffer_size.setVisible(True)

# option for summary plot
        toggle_id = self.menu_table['Display summary plot']
        self._display_summary_plot = Qt.QAction('Display summary plot',self)
        self.menu.addAction(self._display_summary_plot)
        self._display_summary_plot.setVisible(False)
        self._display_summary_plot.setData(Qt.QVariant(toggle_id))

# options for 3D Display
        toggle_id = self.menu_table['X Axis']
        self._x_axis = Qt.QAction('X Axis',self)
        self.menu.addAction(self._x_axis)
        self._x_axis.setVisible(False)
        self._x_axis.setData(Qt.QVariant(toggle_id))
        self.connect(self._x_axis, Qt.SIGNAL('triggered()'), self.X_Axis_Selected)

        toggle_id = self.menu_table['Y Axis']
        self._y_axis = Qt.QAction('Y Axis',self)
        self.menu.addAction(self._y_axis)
        self._y_axis.setVisible(False)
        self._y_axis.setData(Qt.QVariant(toggle_id))
        self.connect(self._y_axis, Qt.SIGNAL('triggered()'), self.Y_Axis_Selected)

        toggle_id = self.menu_table['Z Axis']
        self._z_axis = Qt.QAction('Z Axis',self)
        self.menu.addAction(self._z_axis)
        self._z_axis.setVisible(False)
        self._z_axis.setData(Qt.QVariant(toggle_id))
        self.connect(self._z_axis, Qt.SIGNAL('triggered()'), self.Z_Axis_Selected)

        toggle_id = self.menu_table['Align Camera']
        self._align_camera = Qt.QAction('Align Camera',self)
        self.menu.addAction(self._align_camera)
        self._align_camera.setVisible(False)
        self._align_camera.setData(Qt.QVariant(toggle_id))
        self._align_camera.setText('Align Camera to Current Axis')
        self.connect(self._align_camera, Qt.SIGNAL('triggered()'), self.align_camera)

        toggle_id = self.menu_table['Show 2D Display']
        self._show_2d_display = Qt.QAction('Show 2D Display',self)
        self.menu.addAction(self._show_2d_display)
        self._show_2d_display.setVisible(False)
        self._show_2d_display.setData(Qt.QVariant(toggle_id))
        self.connect(self._show_2d_display, Qt.SIGNAL('triggered()'), self.request_2D_display)

        toggle_id = self.menu_table['Toggle ND Controller']
        self._toggle_nd_controller = Qt.QAction('Toggle ND Controller',self)
        self.menu.addAction(self._toggle_nd_controller)
        self._toggle_nd_controller.setVisible(False)
        self._toggle_nd_controller.setData(Qt.QVariant(toggle_id))
        self._toggle_nd_controller.setText('Hide ND Controller')
        self.connect(self._toggle_nd_controller, Qt.SIGNAL('triggered()'), self.toggle_ND_controller)

        toggle_id = self.menu_table['Toggle VTK Scale']
        self._toggle_vtk_scale = Qt.QAction('Toggle VTK Scale',self)
        self.menu.addAction(self._toggle_vtk_scale)
        self._toggle_vtk_scale.setVisible(False)
        self._toggle_vtk_scale.setData(Qt.QVariant(toggle_id))
        self._toggle_vtk_scale.setText('Apply Scaling to VTK Display')
        self.connect(self._toggle_vtk_scale, Qt.SIGNAL('triggered()'), self.toggle_scale)

        toggle_id = self.menu_table['Update']
        self._update = Qt.QAction('Update',self)
        self.menu.addAction(self._update)
        self._update.setVisible(False)
        self._update.setData(Qt.QVariant(toggle_id))
        self.connect(self._update, Qt.SIGNAL('triggered()'), self.requestUpdate)

        toggle_id = self.menu_table['Print to Postscript file']
        self._print_to_postscript_file = Qt.QAction('Print to Postscript file',self)
        self.menu.addAction(self._print_to_postscript_file)
        self._print_to_postscript_file.setVisible(False)
        self._print_to_postscript_file.setData(Qt.QVariant(toggle_id))
        self.connect(self._print_to_postscript_file, Qt.SIGNAL('triggered()'), self.request_postscript)

        toggle_id = self.menu_table['Save Display in PNG Format']
        self._save_display_in_png_format = Qt.QAction('Save Display in PNG Format',self)
        self.menu.addAction(self._save_display_in_png_format)
        self._save_display_in_png_format.setVisible(False)
        self._save_display_in_png_format.setData(Qt.QVariant(toggle_id))
        self.connect(self._save_display_in_png_format, Qt.SIGNAL('triggered()'), self.request_PNG_file)

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
          self.menu.setParent(Qt.QWidget())
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
      self._toggle_vtk_scale.setVisible(True)

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
      if self.horizontal:
        self.slider.setTickInterval((self.maxVal - self.minVal) / 10)
      else:
        self.slider.setStep((self.maxVal - self.minVal) / 10)
      self.spinbox.setMaximum(self.maxVal)
      self.emit(Qt.SIGNAL("adjust_results_buffer_size"),result_value)

    def handleBufferSize(self):
      """ callback to handle 'Adjust buffer' request from the context menu """
      results_dialog = BufferSizeDialog(self.maxVal, self)
      Qt.QObject.connect(results_dialog,Qt.SIGNAL("return_value"),self.setResultsBuffer)
      results_dialog.show()

    def requestSummary(self, menuid):
      """ callback to handle 'summary plot' request from the context menu """
      if menuid == self.menu_table['Display summary plot']:
        self.emit(Qt.SIGNAL("display_summary_plot"),self.summary_request)
        if self.summary_request:
          self.summary_request = False
          self.menu.changeItem(menuid, 'Discard summary plot')
        else:
          self.summary_request = True
          self.menu.changeItem(menuid, 'Display summary plot')

    def mousePressEvent(self, e):
      if Qt.Qt.RightButton == e.button():
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
    demo = ResultsRange(horizontal=False)
    demo.setRange(0.005)
#   demo = ResultsRange()
#   demo.setRange(20)
    demo.show()
    demo.init3DContextmenu()
    return demo

# make()

def main(args):
    app = Qt.QApplication(args)
    demo = make()
#   app.setMainWidget(demo)
    app.exec_()

# main()

# Admire
if __name__ == '__main__':
    main(sys.argv)

