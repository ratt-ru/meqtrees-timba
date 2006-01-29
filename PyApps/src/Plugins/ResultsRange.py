#!/usr/bin/env python

# a class to generate control buttons etc for use in controlling N-dimensional
# displays

# modules that are imported
from qt import *
import sys

# The ResultsRange class is directly adapted from the Qt/PyQt 
# tutorial code examples.
# It creates a simple spinbox and slider that is used to select a data
# set for display with the result plotter.

class ResultsRange(QWidget):
    def __init__(self, parent=None, name=None):
        QWidget.__init__(self, parent, name)

        self.maxVal = 9
        self.spinbox = QSpinBox(self)
        self.spinbox.setMinValue(0)
        self.spinbox.setMaxValue(self.maxVal)
        self.spinbox.setWrapping(True)

        self.slider = QSlider(Qt.Horizontal, self, "slider")
        self.slider.setTickmarks(QSlider.Below)
        self.slider.setTickInterval(1)
        self.slider.setRange(0, self.maxVal)

        self.setValue()

        self.connect(self.slider, SIGNAL("valueChanged(int)"), self.update_slider)
        self.connect(self.spinbox, SIGNAL("valueChanged(int)"), self.update_spinbox)

        self.layout = QGridLayout(self)
        self.layout.addWidget(self.spinbox, 0,0)
        self.layout.addWidget(self.slider, 1,0)

    def setValue(self, value= 0):
        self.slider.setValue(value)
        self.spinbox.setValue(value)

    def setRange(self, max_range):
        self.maxVal = max_range-1
        self.slider.setRange(0, self.maxVal)
        self.spinbox.setMaxValue(self.maxVal)
        self.setValue(self.maxVal)

    def update_slider(self, slider_value):
        self.spinbox.setValue(slider_value)
        self.emit(PYSIGNAL("result_index"),(slider_value,))

    def update_spinbox(self, spin_value):
        self.slider.setValue(spin_value)
        self.emit(PYSIGNAL("result_index"),(spin_value,))

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

