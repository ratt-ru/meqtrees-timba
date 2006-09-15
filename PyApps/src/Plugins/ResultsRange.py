#!/usr/bin/env python

# a class to generate control buttons etc for use in controlling N-dimensional
# displays

# modules that are imported

#% $Id$ 

#
# Copyright (C) 2006
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

import sys
from qt import *
from BufferSizeDialog import *

# The ResultsRange class is directly adapted from the Qt/PyQt 
# tutorial code examples.
#
# It creates a simple spinbox and slider that is used to select a data
# set for display with the result plotter. It is rather similar to the
# AxisRange class used with the ND-Controller, but the layout is
# different.

class ResultsRange(QWidget):
    def __init__(self, parent=None, name=""):
      QWidget.__init__(self, parent, name)

      self. menu_table = {
      'Adjust results buffer size': 301,
      'Display summary plot': 302,
      }

      self.allow_emit = False
      self.allow_summary = False
      self.summary_request = True
      self.menu = None
      self.maxVal = 10
      self.minVal = 1
      self.label_info = QLabel('', self)
      self.label_info1 = QLabel('    ', self)
      self.string_info =  ' '
      self.offset_index = -1
      self.spinbox = QSpinBox(self)
      self.spinbox.setMinValue(self.minVal)
      self.spinbox.setMaxValue(self.maxVal)
      self.spinbox.setWrapping(True)

      self.slider = QSlider(Qt.Horizontal, self, "slider")
      self.slider.setTickmarks(QSlider.Below)
      self.slider.setTickInterval(self.minVal)
      self.slider.setRange(self.minVal, self.maxVal)


      self.setValue()

      self.connect(self.slider, SIGNAL("valueChanged(int)"), self.update_slider)
      self.connect(self.spinbox, SIGNAL("valueChanged(int)"), self.update_spinbox)

      self.layout = QHBoxLayout(self)
      spacer = QSpacerItem(22,9,QSizePolicy.Expanding,QSizePolicy.Minimum)
      self.layout.addItem(spacer)
      self.layout.addWidget(self.label_info)
      self.layout.addWidget(self.spinbox)
      self.layout.addWidget(self.label_info1)
      self.layout.addWidget(self.slider)

    def setLabel(self, string_value= ''):
      """ set current displayed label """
      self.label_info.setText(string_value + self.string_info) 

    def setStringInfo(self, string_value= ''):
      """ assign a default leading string """
      self.string_info = string_value

    def setMinValue(self, min_value=0):
      """ reset allowed minimum value for spinbox and slider """
      self.minVal = min_value
      self.spinbox.setMinValue(self.minVal)
      self.slider.setRange(self.minVal, self.maxVal)

    def setMaxValue(self, max_value= 0, allow_shrink=True):
      """ reset allowed maximum value for spinbox and slider """
      if max_value < self.maxVal: 
        if allow_shrink:
          self.maxVal = max_value
          self.slider.setRange(self.minVal, self.maxVal)
          self.spinbox.setMaxValue(self.maxVal)
      else:
        if max_value > self.maxVal:
          self.maxVal = max_value
          self.slider.setRange(self.minVal, self.maxVal)
          self.spinbox.setMaxValue(self.maxVal)

    def setValue(self, value= 0):
      """ set current values shown in spinbox and slider """
      self.slider.setValue(value)
      self.spinbox.setValue(value)
      self.initContextmenu()

    def setRange(self, range_value, update_value = True):
      """ define range of values shown with slider """
      if range_value <= self.maxVal:
        self.slider.setRange(self.minVal, range_value)
        self.spinbox.setMaxValue(range_value)
        if update_value:
          self.setValue(range_value)

    def update_slider(self, slider_value):
      """ update spinbox value as function of slider value """
      self.spinbox.setValue(slider_value)

    def update_spinbox(self, spin_value):
      """ update displayed contents of spinbox """
      self.slider.setValue(spin_value)
      if self.allow_emit:
        self.emit(PYSIGNAL("result_index"),(spin_value + self.offset_index,))

    def set_emit(self, permission=True):
      """ flag to allow emitting of Qt signals """
      self.allow_emit = permission

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
      self.slider.setTickInterval(tick_interval)

    def initContextmenu(self):
      """Initialize the result buffer context menu """
      if self.menu is None:
        self.menu = QPopupMenu(self)
        toggle_id = self.menu_table['Adjust results buffer size']
        self.menu.insertItem("Adjust results buffer size", toggle_id)
        QObject.connect(self.menu,SIGNAL("activated(int)"),self.handleBufferSize)

        toggle_id = self.menu_table['Display summary plot']
        self.menu.insertItem("Display summary plot", toggle_id)
        QObject.connect(self.menu,SIGNAL("activated(int)"),self.requestSummary)
        self.menu.setItemVisible(toggle_id, False)

    def disableContextmenu(self):
      """delete the result buffer context menu """
      if not self.menu is None:
          self.menu.reparent(QWidget(), 0, QPoint())
          self.menu = None


    def setResultsBuffer(self, result_value):
      """ redefine the allowable maximum number of values """
      if result_value < 0:
        return
      self.maxVal = result_value
      self.slider.setRange(self.minVal, self.maxVal)
      self.spinbox.setMaxValue(self.maxVal)
      self.emit(PYSIGNAL("adjust_results_buffer_size"),(result_value,))

    def handleBufferSize(self, menuid):
      """ callback to handle 'Adjust buffer' request from the context menu """
      if menuid == self.menu_table['Adjust results buffer size']:
        results_dialog = BufferSizeDialog(self.maxVal, self)
        QObject.connect(results_dialog,PYSIGNAL("return_value"),self.setResultsBuffer)
        results_dialog.show()

    def requestSummary(self, menuid):
      """ callback to handle 'summary plot' request from the context menu """
      if menuid == self.menu_table['Display summary plot']:
        self.emit(PYSIGNAL("display_summary_plot"),(self.summary_request,))
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

# the following tests the ResultsRange class
def make():
    demo = ResultsRange()
    demo.setRange(5)
    demo.show()
    return demo

# make()

def main(args):
    app = QApplication(args)
    demo = make()
    app.setMainWidget(demo)
    app.exec_loop()

# main()

# Admire
if __name__ == '__main__':
    main(sys.argv)

