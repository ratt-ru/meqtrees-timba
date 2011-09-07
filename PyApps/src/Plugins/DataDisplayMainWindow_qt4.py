#!/usr/bin/env python

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

# This is a translation to python of the ACSIS IfDisplayMainWindow.cc code

import sys
from PyQt4 import Qt
import random
import traceback
import numpy

import chartplot_qt4

class DisplayMainWindow(Qt.QMainWindow):
  """ This class enables the display of a collection
      of ChartPlot widgets contained within a tabwidget
  """
  def __init__(self, parent=None, name=None,num_curves=16,plot_label=None):
#   Qt.QMainWindow.__init__(self, parent, name, Qt.WDestructiveClose)
    Qt.QMainWindow.__init__(self, parent)

# ChartPlot strip charts will be displayed via a tab widget
    self._tabwidget = Qt.QTabWidget(self)
    self._tab_resized = False
    self._num_curves = num_curves
    self._plot_label = plot_label
    self._result_range = None
    self._png_number = 0
    self._grab_name = ''

# create a dictionary of chart plot objects
    self._ChartPlot = {}
    self._click_on = "If you click on an individual stripchart with the <b>middle</b> mouse button, a popup window will appear that gives a more detailed plot of the data from that particular object. <br><br> Clicking with the <b>left</b> mouse button will cause a small popup to appear. The popup gives the actual X and Y values, corrected for offset, of the data point nearest to the location of the mouse.<br><br> Clicking with the <b>right</b> mouse button will cause a context menu to appear. The <b>Accumulate data tracks</b> option means that data in each tile will be appended to the previous data. If this option is unchecked, data will be displayed for just each individual tile. The <b>Data element selector</b> option works similarly to that associated with the standard 2-D plot display. Clicking on it causes a small submenu to appear that allows you to select different data elements for display."

  def updateEvent(self, data_dict):
    data_type = data_dict['data_type']
    try:
      self._grab_name = data_dict['source'] + '_'
    except:
      self._grab_name = ''
    if not self._ChartPlot.has_key(data_type):
      self._ChartPlot[data_type] = chartplot_qt4.ChartPlot(num_curves=self._num_curves, parent=self)
      self._ChartPlot[data_type].setDataLabel(data_type)
      index = self._tabwidget.addTab(self._ChartPlot[data_type], data_type)
      self._tabwidget.setCurrentWidget(self._ChartPlot[data_type])
      self._tabwidget.resize(self._tabwidget.minimumSizeHint())
      self.resize(self._tabwidget.minimumSizeHint())
#     dcm_sn_descriptor = "This window shows stripcharts of " + data_type + " as a function of time."
      dcm_sn_descriptor = "This window shows stripcharts of data as a function of time. The display is mostly used to show radio interferometer data where the frequency data have been averaged together. Each tab window can show up to 64 interferometer baselines. The antenna pair associated with each baseline is shown with a yellow background.<br><br>"
      dcm_sn_descriptor = dcm_sn_descriptor + self._click_on
      self._ChartPlot[data_type].setWhatsThis(dcm_sn_descriptor)
      self.connect(self._ChartPlot[data_type], Qt.SIGNAL("quit_event"), self.quit_event)
      self.connect(self._ChartPlot[data_type], Qt.SIGNAL("menu_command"), self.process_menu)
      self.connect(self._ChartPlot[data_type], Qt.SIGNAL("complex_selector_command"), self.process_complex_selector)
      self.connect(self._ChartPlot[data_type], Qt.SIGNAL("vells_selector"), self. update_vells_selector)
      self.connect(self._ChartPlot[data_type], Qt.SIGNAL("auto_offset_value"), self.report_auto_value)
      self.connect(self._ChartPlot[data_type], Qt.SIGNAL("save_display"), self.grab_display)
      if not self._plot_label is None:
        self._ChartPlot[data_type].setPlotLabel(self._plot_label)
      self._ChartPlot[data_type].show()
    self._ChartPlot[data_type].updateEvent(data_dict)
    self._ChartPlot[data_type].setSource(self._grab_name)

  def report_auto_value(self, auto_offset_value):
    self.emit(Qt.SIGNAL("auto_offset_value"),auto_offset_value)

  def set_range_selector(self, new_range):
    """ set or update maximum range for slider controller """
    try:
      keys = self._ChartPlot.keys()
      for i in range(len(keys)):
        self._ChartPlot[keys[i]].set_offset_scale(new_range)
    except:
      pass

  def set_auto_scaling(self):
    """ set or update maximum range for slider controller """
    try:
      keys = self._ChartPlot.keys()
      for i in range(len(keys)):
        self._ChartPlot[keys[i]].set_auto_scaling()
    except:
      pass

  def process_menu(self,menuid):
#   try:
      keys = self._ChartPlot.keys()
      for i in range(len(keys)):
        self._ChartPlot[keys[i]].process_menu(menuid)
#   except:
#     pass

  def process_complex_selector(self,menuid):
#   try:
      keys = self._ChartPlot.keys()
      for i in range(len(keys)):
        self._ChartPlot[keys[i]].process_complex_selector(menuid)
#   except:
#     pass

  def  update_vells_selector(self,menuid):
#   try:
      keys = self._ChartPlot.keys()
      for i in range(len(keys)):
        self._ChartPlot[keys[i]].update_vells_selector(menuid)
#   except:
#     pass

  def resizeEvent(self, event):
    keys = self._ChartPlot.keys()
    for i in range(len(keys)):
      self._ChartPlot[keys[i]].resize(event.size())
    self._tabwidget.resize(event.size())

  def setNewPlot(self):
    try:
      keys = self._ChartPlot.keys()
      for i in range(len(keys)):
        self._ChartPlot[keys[i]].clear_plot()
    except:
      pass

  def grab_display(self, data_type):
    self._png_number = self._png_number + 1
    png_str = str(self._png_number)
    save_file = self._grab_name + data_type + ' '+ png_str + '.png'
    save_file_no_space= save_file.replace(' ','_')
    try:
      pm = Qt.QPixmap.grabWidget(self._ChartPlot[data_type]);
      pm.save(save_file_no_space, "PNG");
    except:
      traceback.print_exc();
      print 'failed to grab or save pixmap';
 


#void IfDisplayMainWindow.set_data_flag(Int channel, Bool flag_value)
#{
#	_ChartPlot(0).set_data_flag(channel,flag_value)
#
## if flag_value == False, we have bad data!
#	if (!flag_value) {
#    		QColor col
#		col.setNamedColor("IndianRed")
#    		statusBar().setPaletteBackgroundColor(col)
#		QString channel_number
#		channel_number.setNum(channel)
#		QString Message = "Bad TSYS detected for channel "+ channel_number 
#    		statusBar().message( Message)
#        	QTimer *timer = new QTimer(this)
#        	connect( timer, SIGNAL(timeout()), this, SLOT(resetStatus()) )
## TRUE means that this will be a one-shot timer
#        	timer.start(500, TRUE)
#	}
#}

#void IfDisplayMainWindow.resetStatus()
#{
#    		QColor col
#    		col.setNamedColor("LightYellow")
#    		statusBar().setPaletteBackgroundColor(col)
#		QString Message = " "
#    		statusBar().message( Message)
#}
#
  def quit_event(self):
    self.close()

  def start_test_timer(self, time):
    # stuff for tests
    self.seq_num = 0
    self._gain = 0
    self._array = numpy.zeros((128,), numpy.float32)
    self._array_imag = numpy.zeros((128,), numpy.float32)
    self._array_complex = numpy.zeros((128,), numpy.complex64)
    self.startTimer(time)

  def timerEvent(self, e):
    self.seq_num = self.seq_num + 1
    self._gain = self._gain + 0.5
    data_dict = {}
    data_dict['sequence_number'] = self.seq_num

    for i in range(16):
      data_dict['channel'] = i

      data_dict['data_type'] = 'scalar'
      data_dict['value'] = (i+1) * random.random()
      self.updateEvent(data_dict)

      data_dict['data_type'] = 'another scalar'
      data_dict['value'] = self._gain + (i+1) * random.random()
      self.updateEvent(data_dict)

      data_dict['data_type'] = 'arrays'
      if i == 13:
        for j in range(self._array.shape[0]):
          self._array[j] = 11 * random.random()
          self._array_imag[j] = 6 * random.random()
        self._array_complex.real = self._array
        self._array_complex.imag = self._array_imag
        data_dict['value'] = self._array_complex
      else:
        for j in range(self._array.shape[0]):
          self._array[j] = (i+1) * random.random()
        data_dict['value'] = self._array
      self.updateEvent(data_dict)

      data_dict['data_type'] = 'tensor demo'
      data_dict['value'] = {}
      for j in range(4):
        if j == 0 or j == 3:
          gain = 1.0
          for k in range(self._array.shape[0]):
            self._array[k] = gain * random.random()
          data_dict['value'][j] = self._array.copy()
        else:
          gain = 0.1
          for k in range(self._array.shape[0]):
            self._array[k] = gain * random.random()
            self._array_imag[k] = gain * random.random()
          self._array_complex.real = self._array
          self._array_complex.imag = self._array_imag
          data_dict['value'][j] = self._array_complex.copy()
      self.updateEvent(data_dict)

    return

def make():
    demo = DisplayMainWindow()
    demo.show()
    demo.start_test_timer(1000)
    return demo

def main(args):
    app = Qt.QApplication(args)
    demo = make()
    app.exec_()


# Admire
if __name__ == '__main__':
    main(sys.argv)

