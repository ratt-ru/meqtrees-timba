#!/usr/bin/env python3

# a class to generate control buttons etc for use in controlling N-dimensional
# displays


#% $Id: ND_Controller.py 5418 2007-07-19 16:49:13Z oms $ 

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

# modules that are imported
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys

from qwt.qt.QtGui import (QApplication, QGridLayout,QHBoxLayout,
         QLabel, QSizePolicy, QSlider, QPushButton, QVBoxLayout, QSpinBox, QSpacerItem)
from qwt.qt.QtGui import QPen, QColor,QWidget, QImage, qRgba
from qwt.qt.QtCore import Qt, QObject, pyqtSignal


# the AxisRange class is directly adapted from the Qt/PyQt 
# tutorial code examples

class AxisRange(QWidget):
    """ a spinbox and a slider, either of which can be used to specify
        a value from within an allowed range
    """
    axis_number = pyqtSignal('int')
    Value_Changed = pyqtSignal(int, int, str)

    def __init__(self, ax_number=1, axis_parms=None,parent=None, name=""):
        """ specify the layout of the spinbox and the slider """
        QWidget.__init__(self, parent)

        self.button = QPushButton(' ', self)
        self.ax_number = ax_number
        self.is_on = False
        self.axis_parms=axis_parms
        self.button_label = None

        self.spinbox = QSpinBox(self)
        self.spinbox.setMinimum(0)
        self.spinbox.setMaximum(99)
        self.spinbox.setWrapping(True)
        self.maxVal = 99

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.setRange(0, 99)
        self.maxVal = 99
        self.active = False

        self.label_info = QLabel(' ', self)

        self.resetValue()

        self.button.clicked.connect(self.emit_axis_number)
        self.slider.valueChanged.connect(self.update_slider)
        self.spinbox.valueChanged.connect(self.update_spinbox)

        self.layout = QGridLayout(self)
        self.layout.addWidget(self.label_info,0,0)
        self.layout.addWidget(self.button,1,0)
        self.layout.addWidget(self.spinbox, 0,2)
        self.layout.addWidget(self.slider, 1,2)

    def emit_axis_number(self):
#     print 'emitting signal ', self.ax_number
      self.axis_number.emit(self.ax_number)

    def isOn(self):
      return self.is_on

    def setOn(self,value):
      self.is_on = value

    def getButton(self):
      return self.button

    def setLabel(self, label):
        """ set label on a button """
        self.button_label = label
        self.button.setText(label)

    def value(self):
        """ return current value of the slider """
        return self.slider.value()

    def hide_display(self):
        self.spinbox.hide()
        self.slider.hide()
        self.label_info.hide()

    def show_display(self):
        self.spinbox.show()
        self.slider.show()
        self.label_info.show()


    def resetValue(self):
        """ resets displayed values to zero """
        display_str = None
        if self.axis_parms is None or not self.active:
          display_str = ''
        else:
          delta_vells = (self.axis_parms[1] - self.axis_parms[0]) / self.maxVal
          index = self.axis_parms[0] + 0.5 * delta_vells 
          if abs(index) < 0.0000001:
            index = 0.0
          display_str = "%-.4g" % index
        self.slider.setValue(0)
        self.spinbox.setValue(0)
        self.label_info.setText(' ' + display_str)

    def setDisplayString(self, value ):
      """ define current display string from Vells parameters """
      display_str = ''
      if not self.axis_parms is None:
        delta_vells = (self.axis_parms[1] - self.axis_parms[0]) / self.maxVal
        index = self.axis_parms[0] + (value + 0.5) * delta_vells 
        if abs(index) < 0.0000001:
          index = 0.0
        display_str = "%-.4g" % index
        self.label_info.setText(' ' + display_str)
      if not self.button_label is None:
        display_str = self.button_label + ' ' + display_str
      
      print('parms', self.ax_number, value, display_str)
      self.Value_Changed.emit(self.ax_number, value, display_str)

    def setRange(self, array_shape):
        """ make sure slider and spinbox both have same allowable range """
        self.slider.setRange(0, array_shape-1)
        self.spinbox.setMaximum(array_shape-1)
        self.maxVal = array_shape

    def setSliderColor(self, color):
        """ set color of slider - red or green """
        self.slider.setStyleSheet("QWidget { background-color: %s }" % color.name())

    def setActive(self, active):
        self.active = active

    def text(self):
        return self.label.text()

    def setText(self, s):
        self.label.setText(s)

    def update_slider(self, slider_value):
        """ synchronize spinbox value to current slider value """
        if self.active:
          self.spinbox.setValue(slider_value)
          self.setDisplayString(slider_value)
        else:
          self.resetValue()

    def update_spinbox(self, spin_value):
        """ synchronize slider value to current spinbox value """
        if self.active:
          self.slider.setValue(spin_value)
          self.setDisplayString(spin_value)
        else:
          self.spinbox.setValue(0)


controller_instructions = \
'''
This control GUI allows you to select a 2 or 3-dimensional sub-array for on-screen display from a larger N-dimensional array. When you select an array for plotting that has 3 or more dimensions, in the case of a <b>2-D</b> display the default start-up plot will show the <b>last two</b> dimensions with the indices into the other dimensions all initialized to zero. <br><br>
So, for example, if we select a 5-d array for display, the last two dimensions (axes 3 and 4 in current notation) do not have sliders associated with them and are only indicated by buttons on the display. The remaining axes have sliders shown in green and indexes for those dimensions initialized to zero. By moving the sliders associated with these axes, you change the indices for the first three dimensions. Alternatively you may change the index associated with a dimension by clicking the spinbox up or down. Note that spinboxes have wrapping turned on: this means that if you have an index with a maximum value of 99, clicking on a spinbox's up arrow will cause the index to wrap around back to zero. You may also jump to a given dimension index by typing the value of that index in the spinbox. Note that if you are displaying a Vellset, the first value displayed in a spinbox is the value of the Vells at the given index (the second number - separated from the first one by blanks).  <br><br> 
You can change the two axes you wish to see displayed on the screen by clicking on any two of the pushbuttons. The sliders associated with these two pushbuttons will then disappear. Then the other axes will have their sliders shown in green - you can move the sliders (and set spinbox contents) to change the array indices for these dimensions.<br><br>
If one is working with a <b>3-D</b> display, we can put up 3 dimensions on the screen at the same time, so the default start up plot will show the last three dimensions (and thus no sliders for them). Also, in this case, to change the axes you wish to see displayed, you must click on any three of the pushbuttons before the display will be modified.<br<br>

'''


class ND_Controller(QWidget):
    defineSelectedAxes = pyqtSignal(int,int,int)
    sliderValueChanged = pyqtSignal(int, int, str)

    def __init__(self, array_shape=None, axis_label=None, axis_parms = None, num_axes = 2, parent=None, name=""):
      QWidget.__init__(self, parent)
# set default number of selectable axes to use 2-D QWT-based display
      self.selectable_axes = num_axes
# create grid layout
      self.layout = QGridLayout(self)
      self.setWhatsThis(controller_instructions)
      self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Minimum)
      self.construct_selectors(array_shape,axis_label,axis_parms)
    # __init__()

    def construct_selectors(self,array_shape=None,axis_label=None,axis_parms=None):
      """ construct a group of AxisRange objects. These objects allow
          the user to specify which dimensions of an N-dimensional
          array are viewable in a 2 or 3-D display
      """
      self.green = QColor(0,0,0)
      self.green.setGreen(255)
      self.red = QColor(0,0,0)
      self.red.setRed(255)
     
      self.axis_parms = axis_parms

# add control buttons and AxisRange selectors
      self.buttons = []
      self.button_number = []
      self.axis_controllers = []
      
      if array_shape is None:
        array_shape = []
        for i in range(len(axis_label)):
          array_shape.append(axis_parms[axis_label[i]][3])
      self.rank = 0
      for i in range(len(array_shape)):
        if array_shape[i] > 1:
          self.rank = self.rank + 1
      self.active_axes = {}
      self.num_selectors = -1
      row = 0
      col = 0
      for i in range(len(array_shape)):
        if array_shape[i] > 1:
          self.num_selectors = self.num_selectors + 1
# add buttons
          button_label = None
          if not axis_label == None:
            button_label = axis_label[i]
          else:
            button_label = 'axis ' + str(i)
          if self.axis_parms is None:
            parms = None
          else:
            if axis_label[i] in self.axis_parms:
              parms = self.axis_parms[axis_label[i]]
            else:
              parms = None
          self.axis_controllers.append(AxisRange(ax_number=self.num_selectors, axis_parms=parms, parent=self))
          self.axis_controllers[self.num_selectors].setLabel(button_label)
          self.axis_controllers[self.num_selectors].setRange(array_shape[i])
          if self.num_selectors <= self.rank - (self.selectable_axes + 1):
            self.axis_controllers[self.num_selectors].setSliderColor(self.green)
            self.axis_controllers[self.num_selectors].setActive(True)
            self.axis_controllers[self.num_selectors].resetValue()
            self.axis_controllers[self.num_selectors].show_display()
          else:
            self.axis_controllers[self.num_selectors].setSliderColor(self.red)
            self.axis_controllers[self.num_selectors].hide_display()

          self.axis_controllers[self.num_selectors].axis_number.connect(self.defineAxes)
          self.axis_controllers[self.num_selectors].Value_Changed.connect(self.update)
          if col == 0:
            spacer = QSpacerItem(22,9, QSizePolicy.Expanding, QSizePolicy.Minimum)
            self.layout.addItem(spacer, row,col)
            col = col + 1
          self.layout.addWidget(self.axis_controllers[self.num_selectors],row,col)
          self.buttons.append(self.axis_controllers[self.num_selectors].getButton())
          self.button_number.append(i)
#         self.buttons[self.num_selectors].setToggleButton(True)
          if self.num_selectors <= self.rank - (self.selectable_axes + 1):
            self.axis_controllers[self.num_selectors].setOn(False)
          else:
            self.axis_controllers[self.num_selectors].setOn(True)
            self.active_axes[self.num_selectors] = True
          if col >= 4:
            col = 0
            row = row + 1
          else:
            col = col + 1

# add one to get number of active selector buttons
      self.num_selectors = self.num_selectors + 1

    def showDisplay(self, show_self):
        if show_self > 0:
          self.show()
        else:
          self.hide()
    # showDisplay

    def set_num_selectable_axes(self, num_axes=2):
        self.selectable_axes = num_axes
        self.redefineAxes()

    def get_num_selectors(self):
        """ gets number of AxisRange objects in the Controller """
        return self.num_selectors

    def defineAxes(self, button_id, do_on=False):
        """ When a button is pressed, this function figures out if
            the user has selected the required number of dimensions
            for extraction. The AxisRange objects for those
            dimensions are colored red.  All data for the selected
            dimensions will be displayed. The remaining AxisRange
            objects are colored green - they enable the user to
            select a single value from their associated dimension.
        """
#       print 'defineAxes button id = ', button_id
        if not self.active_axes is None and len(self.active_axes) == self.selectable_axes:
          self.resetAxes()
        self.axis_controllers[button_id].setOn(True)
#       if do_on:
#         self.axis_controllers[button_id].setOn(True)
        if self.axis_controllers[button_id].isOn():
          self.axis_controllers[button_id].setSliderColor(self.red)
#         self.axis_controllers[button_id].hide_display()
          self.active_axes[button_id] = True
          if len(self.active_axes) == self.selectable_axes:
            first_axis = None
            second_axis = None
            third_axis = None
            for i in range(self.num_selectors):
              if i in self.active_axes:
                if first_axis is None:
                  first_axis = self.button_number[i]
                elif second_axis is None:
                  second_axis = self.button_number[i]
                else:
                  if self.selectable_axes == 3:
                    if third_axis is None:
                      third_axis = self.button_number[i]
                self.axis_controllers[i].setSliderColor(self.red)
                self.axis_controllers[i].setActive(False)
                self.axis_controllers[i].hide_display()
              else:
                self.axis_controllers[i].setSliderColor(self.green)
                self.axis_controllers[i].setActive(True)
                self.axis_controllers[i].show_display()
              self.axis_controllers[i].resetValue()
            self.defineSelectedAxes.emit(first_axis, second_axis,third_axis)
        else:
          if button_id in self.active_axes:
            del self.active_axes[button_id]
          self.axis_controllers[button_id].setSliderColor(self.red)
#         self.axis_controllers[button_id].hide_display()
    # defineAxes

    def redefineAxes(self):
        self.defineAxes(self.num_selectors-1, True)
        self.defineAxes(self.num_selectors-2, True)
    # redefineAxes

    def resetAxes(self):
        """ resets all AxisRange objects to be inactive """
        for i in range(self.num_selectors):
          self.axis_controllers[i].setOn(False)
          self.axis_controllers[i].setSliderColor(self.red)
          self.axis_controllers[i].setActive(False)
#         self.axis_controllers[i].hide_display()
          self.axis_controllers[i].resetValue()
        self.active_axes = {}
    # resetAxes

    def update(self, axis_number, slider_value, display_string):
      """ emits a signal to the data selection program giving
          the new value of an active dimension index 
      """
      print('Caught ', axis_number, slider_value, display_string)
      if not axis_number in self.active_axes:
        if not self.axis_controllers[axis_number].isOn():
          self.sliderValueChanged.emit(self.button_number[axis_number], slider_value, display_string)
        else:
          self.axis_controllers[axis_number].resetValue()
      else:
        self.axis_controllers[axis_number].resetValue()

# class ND_Controller

# the following tests the ND_Controller class
def make():
    axes = (3,4,5,6,7,8,9)
    demo = ND_Controller(axes)
#   axes = (3,4,5)
#   demo = ND_Controller(axes, num_axes=0)
    demo.show()
    return demo

# make()

def main(args):
    app = QApplication(args)
    demo = make()
    app.exec_()

# main()

# Admire
if __name__ == '__main__':
    main(sys.argv)




