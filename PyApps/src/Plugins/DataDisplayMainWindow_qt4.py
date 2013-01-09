#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

# This is a translation to python of the ACSIS IfDisplayMainWindow.cc code

import sys
from PyQt4 import Qt
import random
import traceback
import numpy

import chartplot_qt4


class ControlMenu (Qt.QMenu):
  """TThis is the control menu common to all the ChartPlot widgets"""
  AMP = "Amplitude";
  PHASE = "Phase";
  REAL = "Real";
  IMAG = "Imaginary";
  ComplexComponents = (AMP,PHASE,REAL,IMAG);
  ComplexComponentLabels = {AMP:"ampl",PHASE:"ph",REAL:"re",IMAG:"im"};
  
  def __init__ (self,parent):
    Qt.QMenu.__init__(self,parent);
    self.close_window = self.addAction('Close Window');
    self.close_window.setVisible(False)

    self.reset_zoomer = self.addAction('Reset zoomer');
    self.reset_zoomer.setVisible(False)

# the following is commented out until postscript/pdf printing works 
# properly with Qt 4 widgets
#   self._print = self.addAction("Print",self.plotPrinter.do_print)

    self.clear_plot = self.addAction('Clear plot');

    self.close_popups = self.addAction('Close popups')
    self.close_popups.setVisible(False)

    self.show_flagged_data = self.addAction('Show flagged data')
    self.show_flagged_data.setCheckable(True)
    self.show_flagged_data.setChecked(False)

    self.autoscale = self.addAction('Automatic scaling');
    self.autoscale.setCheckable(True)
    self.autoscale.setChecked(False)
    self.autoscale.setVisible(False) # not sure why, but this is never set to visible -- perhaps fixed scaling doesn't work at all

    self.offset_value = self.addAction('Offset Value');
    self.offset_value.setVisible(False); # not sure why, but this is never set to visible -- perhaps it no longer works at all
    
    self.show_labels = self.addAction('Show labels');
    self.show_labels.setCheckable(True)
    self.show_labels.setChecked(True)

    self.append = self.addAction('Accumulate data tracks')
    self.append.setCheckable(True)
    self.append.setChecked(True)

    # create submenu for complex data
    self.complex_menu = self.addMenu("Plot complex values as...");
    qag = Qt.QActionGroup(self.complex_menu);
    self._qas_complex = dict();
    self._tbs_complex = dict();
    for label in self.ComplexComponents:
      qa = self.complex_menu.addAction(label);
      qa.setCheckable(True);
      qag.addAction(qa);
      self._qas_complex[label] = qa;
    self._qas_complex[self.AMP].setChecked(True); 
    Qt.QObject.connect(qag,Qt.SIGNAL("triggered(QAction*)"),self._change_complex);
    self.complex_menu.menuAction().setVisible(False);
    # current complex component
    self.complex_component = self.AMP;
    
    self.vells_menu = self.addMenu('Data element selector...')
    # menu and action group will be filled when the first updateEvent occurs
    self._qag_vells = Qt.QActionGroup(self.vells_menu);
    self._qas_vells = dict();
    self._tbs_vells = dict();
    Qt.QObject.connect(self._qag_vells,Qt.SIGNAL("triggered(QAction*)"),self._change_vells);
    self.vells_menu.menuAction().setVisible(False);
    self.vells_component = None;

    self.save_this = self.addAction('Save this plot page in PNG format');
    self.save_all = self.addAction('Save all pages in PNG format');

  def createDataSelectorWidgets (self,parent,parent_layout):
    """Creates toolbuttons for complex values and Vells selection""";
    self._ds_top = top = Qt.QWidget(parent);
    parent_layout.addWidget(top);
    self._ds_lo = lotop = Qt.QVBoxLayout(top);
    lotop.setContentsMargins(0,0,0,0);
    self._ds_complex = Qt.QWidget(top);
    self._ds_complex.setVisible(False);
    lotop.addWidget(self._ds_complex);
    lo = Qt.QVBoxLayout(self._ds_complex);
    lo.setContentsMargins(0,0,0,0);
    lab = Qt.QLabel("complex:");
    lab.setAlignment(Qt.Qt.AlignHCenter);
    lo.addWidget(lab);
    # add complex selector
    lo0 = Qt.QHBoxLayout();
    lo0.setContentsMargins(0,0,0,0);
    lo.addLayout(lo0);
    lo1 = Qt.QGridLayout()
    lo1.setContentsMargins(0,0,0,0);
    lo1.setHorizontalSpacing(0);
    lo1.setVerticalSpacing(0);
    lo0.addStretch(1);
    lo0.addLayout(lo1);
    lo0.addStretch(1);
    bgrp = Qt.QButtonGroup(self._ds_complex);
    tbdesc = { self.AMP:(u"\u007Ca\u007C",0,0),self.PHASE:(u"\u03D5",0,1),self.REAL:("Re",1,0),self.IMAG:("Im",1,1) };
    for label,qa in self._qas_complex.iteritems():
      tbtext,row,col = tbdesc[label];
      tb = Qt.QToolButton(self._ds_complex);
      lo1.addWidget(tb,row,col);
      bgrp.addButton(tb);
      tb.setText(tbtext);
      tb.setToolButtonStyle(Qt.Qt.ToolButtonTextOnly);
      tb.setSizePolicy(Qt.QSizePolicy.MinimumExpanding,Qt.QSizePolicy.Minimum);
      tb.setCheckable(True);
      tb.setChecked(label is self.complex_component);
      tb.setMinimumWidth(32);
      Qt.QObject.connect(tb,Qt.SIGNAL("clicked(bool)"),qa.setChecked);
      Qt.QObject.connect(tb,Qt.SIGNAL("clicked(bool)"),self._change_complex);
      Qt.QObject.connect(qa,Qt.SIGNAL("triggered(bool)"),tb.setChecked);
      self._tbs_complex[label] = tb;

  def setVellsElementLabels(self,labels,dims):
    # do nothing when only one label, or when already set
    if len(labels)<2 or self._qas_vells:
      return;
    # make menu items
    for label in labels:
      # make menu action
      self._qas_vells[label] = va = self._qag_vells.addAction(str(label));
      va.setCheckable(True);
      # if first QAction, then check it
      if len(self._qas_vells) == 1:
        va.setChecked(True)
        self.vells_component = label;
      self.vells_menu.addAction(va);
    self.vells_menu.menuAction().setVisible(True);
    # make grid of selector buttons, if dims are not too big
    if len(dims) == 1:
      dims = (1,dims[0]);
    if len(dims) == 2 and min(*dims)>=2 and max(*dims)<=6:
      # for dims=1, make it 1xN 
      # add vells selector 
      self._ds_lo.addSpacing(16);
      self._ds_vells = Qt.QWidget(self._ds_top);
      self._ds_lo.addWidget(self._ds_vells);
      lo = Qt.QVBoxLayout(self._ds_vells);
      lo.setContentsMargins(0,0,0,0);
      lab = Qt.QLabel("element:");
      lab.setAlignment(Qt.Qt.AlignHCenter);
      lo.addWidget(lab);
      # add complex selector
      lo0 = Qt.QHBoxLayout();
      lo0.setContentsMargins(0,0,0,0);
      lo.addLayout(lo0);
      lo1 = Qt.QGridLayout()
      lo1.setContentsMargins(0,0,0,0);
      lo1.setHorizontalSpacing(0);
      lo1.setVerticalSpacing(0);
      lo0.addStretch(1);
      lo0.addLayout(lo1);
      lo0.addStretch(1);
      bgrp = Qt.QButtonGroup(self._ds_vells);
      # make the labels
      for ilabel,label in enumerate(labels):
        # make toolbutton
        tb = Qt.QToolButton(self._ds_vells);
        bgrp.addButton(tb);
        self._tbs_vells[label] = tb;
        tb.setText(str(label));
        tb.setToolButtonStyle(Qt.Qt.ToolButtonTextOnly);
        tb.setCheckable(True);
        tb.setChecked(label is self.vells_component);
        tb.setSizePolicy(Qt.QSizePolicy.MinimumExpanding,Qt.QSizePolicy.Minimum);
  #      tb.setMinimumWidth(32);
        qa = self._qas_vells[label];
        Qt.QObject.connect(tb,Qt.SIGNAL("clicked(bool)"),qa.setChecked);
        Qt.QObject.connect(tb,Qt.SIGNAL("clicked(bool)"),self._change_vells);
        Qt.QObject.connect(qa,Qt.SIGNAL("triggered(bool)"),tb.setChecked);
        # add to layout in correct place
        row,col = divmod(ilabel,dims[1]);
        if dims[1] > 3:
          col,row = row,col;
        lo1.addWidget(tb,row,col);
      # show/hide controls
      self._ds_vells.setVisible(len(labels) > 1);

  def isComplexControlVisible (self):
    return self.complex_menu.menuAction().isVisible();
    
  def isVellsControlVisible (self):
    return self.vells_menu.menuAction().isVisible();

  def showComplexControls (self,show=True):
    """Enables complex controls. If called at least once, they become enabled and stay visible.""";
    if show:
      self.complex_menu.menuAction().setVisible(True);
      self._ds_complex and self._ds_complex.setVisible(True);

  def _change_complex (self,*dum):
    for label,qa in self._qas_complex.iteritems():
      if qa.isChecked():
        self.complex_component = label;
        break;
    self.autoscale.setChecked(True);
    self.emit(Qt.SIGNAL("changeComplexComponent"),self.complex_component);
    
  def _change_vells (self,*dum):
    for label,qa in self._qas_vells.iteritems():
      if qa.isChecked():
        self.vells_component = label;
        if label in self._tbs_vells:
          self._tbs_vells[label].setChecked(True);
        break;
    self.autoscale.setChecked(True);
    self.emit(Qt.SIGNAL("changeVellsComponent"),self.vells_component);


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

# create control menu
    self._menu = ControlMenu(self);
# create a dictionary of chart plot objects
    self._ChartPlot = {}
    self._click_on = "If you click on an individual stripchart with the <b>middle</b> mouse button, a popup window will appear that gives a more detailed plot of the data from that particular object. <br><br> Clicking with the <b>left</b> mouse button will cause a small popup to appear. The popup gives the actual X and Y values, corrected for offset, of the data point nearest to the location of the mouse.<br><br> Clicking with the <b>right</b> mouse button will cause a context menu to appear. The <b>Accumulate data tracks</b> option means that data in each tile will be appended to the previous data. If this option is unchecked, data will be displayed for just each individual tile. The <b>Data element selector</b> option works similarly to that associated with the standard 2-D plot display. Clicking on it causes a small submenu to appear that allows you to select different data elements for display."

    # connect menu signals
    Qt.QObject.connect(self._menu.save_this,Qt.SIGNAL("triggered()"),self.save_current_display)
    Qt.QObject.connect(self._menu.save_all,Qt.SIGNAL("triggered()"),self.save_all_displays)

  def createDataSelectorWidgets (self,parent,layout):
    self._menu.createDataSelectorWidgets(parent,layout);
    
  def setDataElementLabels (self,labels,dims):
    self._menu.setVellsElementLabels(labels,dims);

  def updateEvent(self, data_dict):
    data_type = data_dict['data_type']
    try:
      self._grab_name = data_dict['source']
    except:
      self._grab_name = ''
    if not self._ChartPlot.has_key(data_type):
      self._ChartPlot[data_type] = chartplot_qt4.ChartPlot(self._menu,num_curves=self._num_curves,parent=self)
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
      self.connect(self._ChartPlot[data_type], Qt.SIGNAL("auto_offset_value"), self.report_auto_value)
      if not self._plot_label is None:
        self._ChartPlot[data_type].setPlotLabel(self._plot_label)
      self._ChartPlot[data_type].show()
      # make "Save all" visibile if multiple pages
      self._menu.save_all.setVisible(len(self._ChartPlot) > 1);
      
    self._ChartPlot[data_type].updateEvent(data_dict)
    self._ChartPlot[data_type].setSource(self._grab_name)

  def report_auto_value(self, auto_offset_value):
    self.emit(Qt.SIGNAL("auto_offset_value"),auto_offset_value)

  def set_range_selector(self, new_range):
    """ set or update maximum range for slider controller """
    for plot in self._ChartPlot.itervalues():
      plot.set_offset_scale(new_range)

  def set_auto_scaling(self):
    """ set or update maximum range for slider controller """
    for plot in self._ChartPlot.itervalues():
      plot.set_auto_scaling()

  def resizeEvent(self, event):
    for plot in self._ChartPlot.itervalues():
      plot.resize(event.size())
    self._tabwidget.resize(event.size())

  def setNewPlot(self):
    for plot in self._ChartPlot.itervalues():
      plot.clear_plot()

  def save_current_display (self):
    filename,error = self._save_display(self._tabwidget.currentWidget());
    if error:
      self.emit(Qt.SIGNAL("showMessage"),"error writing file %s"%filename,True);
    else:
      self.emit(Qt.SIGNAL("showMessage"),"saved plot to %s"%filename);
    
  def save_all_displays (self):
    good_files = [];
    bad_files = [];
    for key in sorted(self._ChartPlot.keys()):
      filename,error = self._save_display(self._ChartPlot[key]);
      (bad_files if error else good_files).append(filename);
    if good_files:
      self.emit(Qt.SIGNAL("showMessage"),"saved plots to %s"%(", ".join(good_files)));
    if bad_files:
      self.emit(Qt.SIGNAL("showMessage"),"error writing files %s"%(", ".join(bad_files)),True);
    
  def _save_display (self,chartplot):
    self._png_number += 1;
    # put together filename components
    name_components = [];
    if self._grab_name:
      name_components.append(self._grab_name);
    if self._menu.isVellsControlVisible():
      name_components.append(str(self._menu.vells_component));
    if self._menu.isComplexControlVisible():
      name_components.append(str(self._menu.ComplexComponentLabels[self._menu.complex_component]));
    if len(self._ChartPlot) > 1:
      name_components.append(chartplot.dataLabel());
    name_components.append(str(self._png_number));
    save_file = "_".join(name_components).replace(' ','_')+".png";
    try:
      pm = Qt.QPixmap.grabWidget(chartplot);
      pm.save(save_file, "PNG");
      return save_file,None;
    except:
      traceback.print_exc();
      print 'failed to grab or save pixmap';
      return save_file,True;
 


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

