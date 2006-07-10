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

from qt import *
import sys

from Timba.utils import verbosity
_dbg = verbosity(0,name='ND');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;


# the Axis Range class is directly adapted from the Qt/PyQt tutorial code examples
class AxisRange(QWidget):
    def __init__(self, axis_number=1, axis_parms=None,parent=None, name=""):
        QWidget.__init__(self, parent, name)

        self.button = QPushButton(' ', self)
        self.axis_number = axis_number

        self.axis_parms=axis_parms
        self.button_label = None

        self.spinbox = QSpinBox(self)
        self.spinbox.setMinValue(0)
        self.spinbox.setMaxValue(99)
        self.spinbox.setWrapping(True)
        self.maxVal = 99

        self.slider = QSlider(Qt.Horizontal, self, "slider")
        self.slider.setTickmarks(QSlider.Below)
        self.slider.setTickInterval(10)
        self.slider.setRange(0, 99)
        self.maxVal = 99
        self.active = False

        self.label_info = QLabel(' ', self)

        self.resetValue()

        self.connect(self.slider, SIGNAL("valueChanged(int)"), self.update_slider)
        self.connect(self.spinbox, SIGNAL("valueChanged(int)"), self.update_spinbox)

        self.layout = QGridLayout(self)
        self.layout.addWidget(self.label_info,0,0)
        self.layout.addWidget(self.button,1,0)
        self.layout.addMultiCellWidget(QLabel(' ', self),0,1,1,1)
        self.layout.addWidget(self.spinbox, 0,2)
        self.layout.addWidget(self.slider, 1,2)
        self.layout.addMultiCellWidget(QLabel(' ', self),0,1,3,3)

    def getButton(self):
      return self.button

    def setLabel(self, label):
        self.button_label = label
        self.button.setText(label)

    def value(self):
        return self.slider.value()

    def resetValue(self):
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
      self.emit(PYSIGNAL("ValueChanged"), (self.axis_number, value, display_str))

    def setRange(self, array_shape):
        self.slider.setRange(0, array_shape-1)
        self.spinbox.setMaxValue(array_shape-1)
        self.maxVal = array_shape

    def setSliderColor(self, color):
        self.slider.setPaletteBackgroundColor(color)

    def setActive(self, active):
        self.active = active

    def text(self):
        return self.label.text()

    def setText(self, s):
        self.label.setText(s)

    def update_slider(self, slider_value):
        if self.active:
          self.spinbox.setValue(slider_value)
          self.setDisplayString(slider_value)
        else:
          self.resetValue()

    def update_spinbox(self, spin_value):
        if self.active:
          self.slider.setValue(spin_value)
          self.setDisplayString(spin_value)
        else:
          self.spinbox.setValue(0)


controller_instructions = \
'''This control GUI allows you to select a 2-dimensional sub-array for on-screen display from a larger N-dimensional array. When you select an array for plotting that has 3 or more dimensions, the default start-up plot will show the last two dimensions with the indices into the previous dimensions all initialized to zero. <br><br>
So, for example, if we select a 5-d array for display, the last two dimensions (axes 3 and 4 in current notation) are shown with red sliders  and you will not be able to move the sliders under them. The remaining axes have sliders shown in green and indexes for those dimensions initialized to zero. By moving the sliders associated with these axes, you change the indices for the first three dimensions. Alternatively you may change the index associated with a dimension by clicking the spinbox up or down. Note that spinboxes have wrapping turned on: this means that if you have an index with a maximum value of 99, clicking on a spinbox's up arrow will cause the index to wrap around back to zero. You may also jump to a given dimension index by typing the value of that index in the spinbox. Note that if you are displaying a Vellset, the first value displayed in a spinbox is the value of the Vells at the given index (the second number - separated from the first one by blanks).  <br><br> 
You can change the two axes you wish to see displayed on the screen by clicking on any two of the pushbuttons. These pushbuttons will then have their corresponding sliders displayed in red and are frozen. The other axes will have their sliders shown in green - you can move the sliders (and set spinbox contents) to change the array indices for these dimensions.'''

class ND_Controller(QWidget):
    def __init__(self, array_shape=None, axis_label=None, axis_parms = None, parent=None, name=""):
      QWidget.__init__(self, parent, name)

      QWhatsThis.add(self, controller_instructions)

# create grid layout
      self.layout = QGridLayout(self)
      self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Minimum)

      self.axis_parms = axis_parms

# create button group
      self.buttonGroup = QButtonGroup(self)
      QObject.connect(self.buttonGroup, SIGNAL("clicked(int)"),self.defineAxes)

# add control buttons and LCD Displays
      self.buttons = []
      self.button_number = []
      self.axis_controllers = []
      row = 0
      col = 0
      self.rank = 0
      _dprint(3, 'incoming array shape ', array_shape)

      if array_shape is None:
        array_shape = []
        for i in range(len(axis_label)):
          array_shape.append(axis_parms[axis_label[i]][3])
      _dprint(3, 'final array shape ', array_shape)
      for i in range(len(array_shape)):
        if array_shape[i] > 1:
          self.rank = self.rank + 1
      self.active_axes = {}
      self.num_selectors = -1
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
            if self.axis_parms.has_key(axis_label[i]):
              parms = self.axis_parms[axis_label[i]]
            else:
              parms = None
          self.axis_controllers.append(AxisRange(axis_number=self.num_selectors, axis_parms=parms, parent=self))
          self.axis_controllers[self.num_selectors].setLabel(button_label)
          self.axis_controllers[self.num_selectors].setRange(array_shape[i])
          if self.num_selectors <= self.rank -3:
            self.axis_controllers[self.num_selectors].setSliderColor(Qt.green)
            self.axis_controllers[self.num_selectors].setActive(True)
            self.axis_controllers[self.num_selectors].resetValue()
          else:
            self.axis_controllers[self.num_selectors].setSliderColor(Qt.red)

          QObject.connect(self.axis_controllers[self.num_selectors], PYSIGNAL("ValueChanged"),self.update)
          self.layout.addWidget(self.axis_controllers[self.num_selectors], row, col);

          self.buttons.append(self.axis_controllers[self.num_selectors].getButton())
          self.button_number.append(i)
          self.buttons[self.num_selectors].setToggleButton(True)
          if self.num_selectors <= self.rank -3:
            self.buttons[self.num_selectors].setOn(False)
          else:
            self.buttons[self.num_selectors].setOn(True)
            self.active_axes[self.num_selectors] = True
          self.buttonGroup.insert(self.buttons[self.num_selectors],self.num_selectors)
          if col >= 1:
            col = 0
            row = row + 1
          else:
            col = col + 1

# add one to get number of active selector buttons
      self.num_selectors = self.num_selectors + 1

    # __init__()

    def showDisplay(self, show_self):
        if show_self > 0:
          self.show()
        else:
          self.hide()
    # showDisplay

    def defineAxes(self, button_id, do_on=False):
        if not self.active_axes is None and len(self.active_axes) == 2:
          self.resetAxes()
          self.buttons[button_id].setOn(True)
        if do_on:
          self.buttons[button_id].setOn(True)
        if self.buttons[button_id].isOn():
          self.axis_controllers[button_id].setSliderColor(Qt.red)
          self.active_axes[button_id] = True
          if len(self.active_axes) == 2:
            first_axis = None
            second_axis = None
            for i in range(self.num_selectors):
              if self.active_axes.has_key(i):
                if first_axis is None:
                  first_axis = self.button_number[i]
                else:
                  second_axis = self.button_number[i]
                self.axis_controllers[i].setSliderColor(Qt.red)
                self.axis_controllers[i].setActive(False)
              else:
                self.axis_controllers[i].setSliderColor(Qt.green)
                self.axis_controllers[i].setActive(True)
              self.axis_controllers[i].resetValue()
            self.emit(PYSIGNAL("defineSelectedAxes"), (first_axis, second_axis))
        else:
          if self.active_axes.has_key(button_id):
            del self.active_axes[button_id]
          self.axis_controllers[button_id].setSliderColor(Qt.red)
    # defineAxes

    def redefineAxes(self):
        self.defineAxes(self.num_selectors-1, True)
        self.defineAxes(self.num_selectors-2, True)
    # resetAxes

    def resetAxes(self):
        for i in range(self.num_selectors):
          self.buttons[i].setOn(False)
          self.axis_controllers[i].setSliderColor(Qt.red)
          self.axis_controllers[i].setActive(False)
          self.axis_controllers[i].resetValue()
        self.active_axes = {}
    # resetAxes

    def update(self, axis_number, slider_value, display_string):
      if not self.active_axes.has_key(axis_number):
        if not self.buttons[axis_number].isOn():
          self.emit(PYSIGNAL("sliderValueChanged"), (self.button_number[axis_number], slider_value, display_string))
        else:
          self.axis_controllers[axis_number].resetValue()
      else:
        self.axis_controllers[axis_number].resetValue()

# class ND_Controller

# the following tests the ND_Controller class
def make():
    axes = (3,4,5,6,7,8,9,10,11)
    demo = ND_Controller(axes)
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




