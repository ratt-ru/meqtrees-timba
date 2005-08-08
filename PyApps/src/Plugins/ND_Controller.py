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

        self.slider = QSlider(Qt.Horizontal, self, "slider")
        self.slider.setTickmarks(QSlider.Below)
        self.slider.setTickInterval(10)
        self.slider.setRange(0, 99)
        self.slider.setValue(0)

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
#       print 'lcd slider value ', self.lcd_number, ' ',slider_value
        self.emit(PYSIGNAL("sliderValueChanged"), (self.lcd_number, slider_value))
        
        return self.slider.value()


controller_instructions = \
'''The colorbar displays the current range of intensities in the corresponding image display. You can interact with the colorbar to change the range of intensities displayed in the image.<br><br>
Button 1 (Left): If you click the <b>left</b> mouse button on a location inside the colorbar and then drag it, a rectangular square will be seen. When you release the left mouse button, the range of intensity defined in the vertical (Y) direction will now specify the maximum range of intensity that will be shown in the image display. Image pixels with values greater or less than the selected range will be plotted with the maximum or minimum allowed values. The color rainbow or grayscale will always cover the specified range of pixels, so you can obtain increased detail by zooming in on an intensity range.<br><br>
Button 2 (Right):Clicking the <b>right</b> mouse button in the colorbar window will cause a context menu with the option to 'unzoom intensity range' to appear. If you click on this menu item, then the colorbar scale (and the image scale) is reset to the intrinsic range associated with the current image.'''

class ND_Controller(QWidget):
    def __init__(self, array_shape=1, parent=None, name=None):
      QWidget.__init__(self, parent, name)

# create grid layout
      self.layout = QGridLayout(self)

# create button group
      self.buttonGroup = QButtonGroup(self)
      QObject.connect(self.buttonGroup, SIGNAL("clicked(int)"),self.defineAxes)

# add control buttons and LCD Displays
      self.buttons = []
      self.lcd_ranges = []
      row = 0
      col = 0
      self.num_axes = len(array_shape)
      self.active_axes = 0
      for i in range(self.num_axes):
# add buttons
        button_label = 'axis ' + str(i)
        button = QPushButton(button_label, self);
        self.buttons.append(button)
        self.buttons[i].setToggleButton(True)
        if i <= self.num_axes -3:
          self.buttons[i].setOn(False)
          self.buttons[i].setPaletteForegroundColor(Qt.red)
        else:
          self.buttons[i].setOn(True)
          self.buttons[i].setPaletteForegroundColor(Qt.green)
          self.active_axes = self.active_axes + 1
        self.layout.addWidget(self.buttons[i], row, col)
        self.buttonGroup.insert(self.buttons[i],i)

# add lcd ranges
        col = col + 1;
        self.lcd_ranges.append (LCDRange(i, self))
        QObject.connect(self.lcd_ranges[i], PYSIGNAL("sliderValueChanged"),self.update)
        self.layout.addWidget(self.lcd_ranges[i], row, col);
        if i <= self.num_axes -3:
          self.lcd_ranges[i].setLCDColor(Qt.green)
        else:
          self.lcd_ranges[i].setLCDColor(Qt.red)
        self.lcd_ranges[i].setRange(0, array_shape[i]-1)
        if col >= 3:
          col = 0
          row = row + 1
        else:
          col = col + 1

# add reset button
#     self.reset_button = QPushButton('RESET', self);
#     row = row + 1
#     col = 0
#     self.layout.addWidget(self.reset_button, row, col)
#     QObject.connect(self.reset_button, SIGNAL("clicked()"),self.resetAxes)

# lcd_ranges

    # __init__()

    def showDisplay(self, show_self):
        if show_self > 0:
          self.show()
        else:
          self.hide()
        self.replot()
    # showDisplay

    def defineAxes(self, button_id):
        if self.active_axes == 2:
          self.resetAxes()
          self.buttons[button_id].setOn(True)
        if self.buttons[button_id].isOn():
          self.buttons[button_id].setPaletteForegroundColor(Qt.green)
          self.lcd_ranges[button_id].setLCDColor(Qt.red)
          self.active_axes = self.active_axes + 1
          self.axes_list.append(button_id)
          if self.active_axes == 2:
            first_axis = None
            second_axis = None
            for i in range(self.num_axes):
              if self.buttons[i].isOn():
                if first_axis is None:
                  first_axis = i
                else:
                  second_axis = i
              else:
                self.lcd_ranges[i].setLCDColor(Qt.green)
              self.lcd_ranges[i].setValue(0)
            self.emit(PYSIGNAL("defineSelectedAxes"), (first_axis, second_axis))
        else:
          self.buttons[button_id].setPaletteForegroundColor(Qt.red)
          self.lcd_ranges[button_id].setLCDColor(Qt.green)
    # defineAxes

    def resetAxes(self):
        for i in range(self.num_axes):
          self.buttons[i].setOn(False)
          self.buttons[i].setPaletteForegroundColor(Qt.red)
          self.lcd_ranges[i].setLCDColor(Qt.red)
          self.active_axes = 0
          self.axes_list = []
    # resetAxes

    def update(self, lcd_number, slider_value):
      if self.active_axes == 2:
        if not self.buttons[lcd_number].isOn():
          self.emit(PYSIGNAL("sliderValueChanged"), (lcd_number, slider_value))
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




