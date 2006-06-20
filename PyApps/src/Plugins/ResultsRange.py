#!/usr/bin/env python

# a class to generate control buttons etc for use in controlling N-dimensional
# displays

# modules that are imported
import sys
from qt import *
from BufferSizeDialog import *

# The ResultsRange class is directly adapted from the Qt/PyQt 
# tutorial code examples.
# It creates a simple spinbox and slider that is used to select a data
# set for display with the result plotter.

class ResultsRange(QWidget):
    def __init__(self, parent=None, name=""):
      QWidget.__init__(self, parent, name)

      self. menu_table = {
      'Adjust results buffer size': 301,
      }

      self.allow_emit = False
      self.menu = None
      self.maxVal = 10
      self.label_info = QLabel('', self)
      self.label_info1 = QLabel('    ', self)
      self.string_info =  ' '
      self.spinbox = QSpinBox(self)
      self.spinbox.setMinValue(1)
      self.spinbox.setMaxValue(self.maxVal)
      self.spinbox.setWrapping(True)

      self.slider = QSlider(Qt.Horizontal, self, "slider")
      self.slider.setTickmarks(QSlider.Below)
      self.slider.setTickInterval(1)
      self.slider.setRange(1, self.maxVal)


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
      self.label_info.setText(string_value + self.string_info) 

    def setStringInfo(self, string_value= ''):
      self.string_info = string_value

    def setMaxValue(self, max_value= 0, allow_shrink=True):
      if max_value < self.maxVal: 
        if allow_shrink:
          self.maxVal = max_value
          self.slider.setRange(1, self.maxVal)
          self.spinbox.setMaxValue(self.maxVal)
      else:
        if max_value > self.maxVal:
          self.maxVal = max_value
          self.slider.setRange(1, self.maxVal)
          self.spinbox.setMaxValue(self.maxVal)

    def setValue(self, value= 0):
      self.slider.setValue(value)
      self.spinbox.setValue(value)
      self.initContextmenu()

    def setRange(self, range_value, update_value = True):
      if range_value <= self.maxVal:
        self.slider.setRange(1, range_value)
        self.spinbox.setMaxValue(range_value)
        if update_value:
          self.setValue(range_value)

    def update_slider(self, slider_value):
      self.spinbox.setValue(slider_value)

    def update_spinbox(self, spin_value):
      self.slider.setValue(spin_value)
      if self.allow_emit:
        self.emit(PYSIGNAL("result_index"),(spin_value-1,))

    def set_emit(self, permission):
      self.allow_emit = permission

    def initContextmenu(self):
      """Initialize the result buffer context menu
      """
      if self.menu is None:
        self.menu = QPopupMenu(self)
        toggle_id = self.menu_table['Adjust results buffer size']
        self.menu.insertItem("Adjust results buffer size", toggle_id)
        QObject.connect(self.menu,SIGNAL("activated(int)"),self.handleMenu)

    def disableContextmenu(self):
      self.menu = None

    def setResultsBuffer(self, result_value):
      if result_value < 0:
        return
      self.maxVal = result_value
      self.slider.setRange(1, self.maxVal)
      self.spinbox.setMaxValue(self.maxVal)
      self.emit(PYSIGNAL("adjust_results_buffer_size"),(result_value,))

    def handleMenu(self, menuid):
        if menuid == self.menu_table['Adjust results buffer size']:
          results_dialog = BufferSizeDialog(self.maxVal, self)
          QObject.connect(results_dialog,PYSIGNAL("return_value"),self.setResultsBuffer)

          results_dialog.show()

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

