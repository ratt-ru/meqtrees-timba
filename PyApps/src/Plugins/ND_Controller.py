#!/usr/bin/env python

# a class to generate control buttons etc for use in controlling N-dimensional
# displays

# modules that are imported
from qt import *
import sys

# the LCD Range class is directly adapted from the Qt/PyQt tutorial code examples
class LCDRange(QWidget):
    def __init__(self, lcd_number=1, parent=None, name=None):
        QWidget.__init__(self, parent, name)

        self.lcd_number = lcd_number
        self.lcd = QLCDNumber(3, self, "lcd")
        self.lcd.setSegmentStyle(QLCDNumber.Filled)
        self.lcd.setPaletteBackgroundColor(Qt.red)
        self.lcd.setMaximumWidth(200)
        self.lcd.setMaximumHeight(50)

        self.slider = QSlider(Qt.Horizontal, self, "slider")
        self.slider.setTickmarks(QSlider.Below)
        self.slider.setTickInterval(10)
        self.slider.setRange(0, 99)
        self.slider.setValue(0)
        self.slider.setMaximumWidth(200)

        self.connect(self.slider, SIGNAL("valueChanged(int)"), self.lcd, SLOT("display(int)"))
        self.connect(self.slider, SIGNAL("valueChanged(int)"), self, PYSIGNAL("valueChanged(int)"))
        self.connect(self.slider, SIGNAL("valueChanged(int)"), self.update)


        self.setFocusProxy(self.slider)

        l = QVBoxLayout(self)
        l.addWidget(self.lcd, 1)
        l.addWidget(self.slider)

    def value(self):
        return self.slider.value()

    def setValue(self, value):
        self.slider.setValue(value)

    def setRange(self, minVal, maxVal):
        if minVal < 0 or minVal > maxVal:
           raise ValueError, "LCDRange.setRange(): invalid range"

        self.slider.setRange(minVal, maxVal)

    def setLCDColor(self, color):
        self.lcd.setPaletteBackgroundColor(color)

    def text(self):
        return self.label.text()

    def setText(self, s):
        self.label.setText(s)

    def update(self, slider_value):
        self.emit(PYSIGNAL("sliderValueChanged"), (self.lcd_number, slider_value))
        
        return self.slider.value()


controller_instructions = \
'''This control GUI allows you to select a 2-dimensional sub-array for on-screen display from a larger N-dimensional array. When you select an array for plotting that has 3 or more dimensions, the default start-up plot will show the last two dimensions with the indices into the previous dimensions all initialized to zero. <br><br>
So, for example, if we select a 5-d array for display, the last two dimensions (axes 3 and 4 in current notation) are shown with green push buttons, but the corresponding sliders are shown in red and you will not be able to move the sliders.The remaining axes have sliders shown in green and indexes for those dimensions initialized to zero. By moving the sliders associated with these axes, you change the indices for the first three dimensions. <br><br> 
You can change the two axes you wish to see displayed on the screen by clicking on any two of the pushbuttons. These pushbuttons will then have their labels displayed in green and their sliders will be displayed in red and are frozen. The other axes will have live sliders shown in green - you can move the sliders to change the array indices for these dimensions.'''

class ND_Controller(QWidget):
    def __init__(self, array_shape=1, axis_record=None, parent=None, name=None):
      QWidget.__init__(self, parent, name)

      QWhatsThis.add(self, controller_instructions)

# create grid layout
      self.layout = QGridLayout(self)

# create button group
      self.buttonGroup = QButtonGroup(self)
      QObject.connect(self.buttonGroup, SIGNAL("clicked(int)"),self.defineAxes)

# add control buttons and LCD Displays
      self.buttons = []
      self.button_number = []
      self.lcd_ranges = []
      row = 0
      col = 0
      self.rank = 0
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
          if not axis_record == None:
            button_label = axis_record[i]
          else:
            button_label = 'axis ' + str(i)
          button = QPushButton(button_label, self);
          self.buttons.append(button)
          self.button_number.append(i)
          self.buttons[self.num_selectors].setToggleButton(True)
          if self.num_selectors <= self.rank -3:
            self.buttons[self.num_selectors].setOn(False)
            self.buttons[self.num_selectors].setPaletteForegroundColor(Qt.red)
          else:
            self.buttons[self.num_selectors].setOn(True)
            self.buttons[self.num_selectors].setPaletteForegroundColor(Qt.green)
            self.active_axes[self.num_selectors] = True
          self.layout.addWidget(self.buttons[self.num_selectors], row, col)
          self.buttonGroup.insert(self.buttons[self.num_selectors],self.num_selectors)

# add lcd ranges
          col = col + 1;
          self.lcd_ranges.append (LCDRange(self.num_selectors, self))
          QObject.connect(self.lcd_ranges[self.num_selectors], PYSIGNAL("sliderValueChanged"),self.update)
          self.layout.addWidget(self.lcd_ranges[self.num_selectors], row, col);
          if self.num_selectors <= self.rank -3:
            self.lcd_ranges[self.num_selectors].setLCDColor(Qt.green)
          else:
            self.lcd_ranges[self.num_selectors].setLCDColor(Qt.red)
          self.lcd_ranges[self.num_selectors].setRange(0, array_shape[i]-1)
          if col >= 3:
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

    def defineAxes(self, button_id):
        if not self.active_axes is None and len(self.active_axes) == 2:
          self.resetAxes()
          self.buttons[button_id].setOn(True)
        if self.buttons[button_id].isOn():
          self.buttons[button_id].setPaletteForegroundColor(Qt.green)
          self.lcd_ranges[button_id].setLCDColor(Qt.red)
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
                self.lcd_ranges[i].setLCDColor(Qt.red)
              else:
                self.lcd_ranges[i].setLCDColor(Qt.green)
              self.lcd_ranges[i].setValue(0)
            self.emit(PYSIGNAL("defineSelectedAxes"), (first_axis, second_axis))
        else:
          if self.active_axes.has_key(button_id):
            del self.active_axes[button_id]
          self.buttons[button_id].setPaletteForegroundColor(Qt.red)
          self.lcd_ranges[button_id].setLCDColor(Qt.red)
    # defineAxes

    def resetAxes(self):
        for i in range(self.num_selectors):
          self.buttons[i].setOn(False)
          self.buttons[i].setPaletteForegroundColor(Qt.red)
          self.lcd_ranges[i].setLCDColor(Qt.red)
        self.active_axes = {}
    # resetAxes

    def update(self, lcd_number, slider_value):
      if not self.active_axes.has_key(lcd_number):
        if not self.buttons[lcd_number].isOn():
          self.emit(PYSIGNAL("sliderValueChanged"), (self.button_number[lcd_number], slider_value))
        else:
          self.lcd_ranges[lcd_number].setValue(0)
      else:
        self.lcd_ranges[lcd_number].setValue(0)

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




