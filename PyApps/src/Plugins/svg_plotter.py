#!/usr/bin/python

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

# modules that are imported
from Timba.dmi import *
from Timba import utils
from Timba.Meq import meqds
from Timba.Meq.meqds import mqs
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI import widgets
from Timba.GUI.browsers import *
from Timba import Grid

from qt import *
from numarray import *
from Timba.Plugins.plotting_functions import *

from ResultsRange import *
from BufferSizeDialog import *
from plot_printer import *
import os

from Timba.utils import verbosity
_dbg = verbosity(0,name='svg_plotter');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class PictureDisplay(QWidget):

  def __init__( self, *args ):
    QWidget.__init__(self, *args)
    self.pict = QPicture()
    self.name = None

  def loadPicture(self,filename):
    self.name = filename
    if not self.pict.load(self.name, "svg"):
      self.pict = None
      print "Not able to load picture ", self.name

  def paintEvent(self, QPaintEvent):
    paint = QPainter(self)
    if self.pict:
      paint.drawPicture(self.pict)

class SvgPlotter(GriddedPlugin):
  """ a class to visualize data from Scalable Vector Graphics files """

  _icon = pixmaps.bars3d
  viewer_name = "Svg Plotter";
  def is_viewable (data):
    return len(data) > 0;
  is_viewable = staticmethod(is_viewable);

  def __init__(self,gw,dataitem,cellspec={},**opts):
    GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);
    """ a plugin for showing svg plots """
    self._rec = None;
    self._wtop = None;
    self.dataitem = dataitem
    self.png_number = 0
    self.data_list = []
    self.data_list_labels = []
    self.data_list_length = 0
    self.max_list_length = 50
    self._window_controller = None
    self.layout_created = False

    self.reset_plot_stuff()

# back to 'real' work
    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

  def reset_plot_stuff(self):
    """ resets widgets to None. Needed if we have been putting
        out a message about Cache not containing results, etc
    """
    self._svg_plotter = None
    self.results_selector = None
    self.status_label = None
    self.layout_parent = None
    self.layout = None

  def __del__(self):
    if self._window_controller:
      self._window_controller.closeAllWindows()

  def wtop (self):
    """ function needed by Oleg for reasons known only to him! """
    return self._wtop;

  def create_layout_stuff(self):
    """ create grid layouts into which plotter widgets are inserted """
    if self.layout_parent is None or not self.layout_created:
      self.layout_parent = QWidget(self.wparent())
      self.layout = QGridLayout(self.layout_parent)
      self.set_widgets(self.layout_parent,self.dataitem.caption,icon=self.icon())
      self.layout_created = True
    self._wtop = self.layout_parent;       

  def update_status(self, status):
     if not status is None:
       self.status_label.setText(status)

  def grab_display(self, title):
    self.png_number = self.png_number + 1
    png_str = str(self.png_number)
    if title is None:
      save_file = './meqbrowser' + png_str + '.png'
    else:
      save_file = title + png_str + '.png'
    save_file_no_space= save_file.replace(' ','_')
    result = QPixmap.grabWidget(self.layout_parent).save(save_file_no_space, "PNG")
    
  def set_data (self,dataitem,default_open=None,**opts):
    """ this callback receives data from the meqbrowser, when the
        user has requested a plot. It decides whether the data is
        from a VellSet or visu data record, and  after any
        necessary preprocssing forwards the data to one of
        the functions which does the actual plotting """

    _dprint(3, '** in svg_plotter:set_data callback')
    self._rec = dataitem.data;
    _dprint(3, 'set_data: initial self._rec ', self._rec)
# if we are single stepping through requests, Oleg may reset the
# cache, so check for a non-data record situation
    if self._rec is None:
      return
    if isinstance(self._rec, bool):
      return

    self.label = '';  # extra label, filled in if possible
# there's a problem here somewhere ...
    if dmi_typename(self._rec) != 'MeqResult': # data is not already a result?
      # try to put request ID in label
      rq_id_found = False
      data_failure = False
      try:
        if self._rec.cache.has_key("request_id"):
          self.label = "rq " + str(self._rec.cache.request_id);
          rq_id_found = True
        if self._rec.cache.has_key("result"):
          self._rec = self._rec.cache.result; # look for cache.result record
          if not rq_id_found and self._rec.has_key("request_id"):
            self.label = "rq " + str(self._rec.request_id);
        else:
          data_failure = True
        _dprint(3, 'we have req id ', self.label)
      except:
        data_failure = True
      if data_failure:
        _dprint(3, ' we have a data failure')
# cached_result not found, display an empty viewer with a "no result
# in this node record" message (the user can then use the Display with
# menu to switch to a different viewer)
        Message = "No cache result record was found for this node, so no plot can be made."
        cache_message = QLabel(Message,self.wparent())
        cache_message.setTextFormat(Qt.RichText)
        self._wtop = cache_message
        self.set_widgets(cache_message)
        self.reset_plot_stuff()

        return
    
# update display with current data
    process_result = self.process_data()

# add this data set to internal list for later replay
    if process_result:
      if self.max_list_length > 0:
        self.data_list.append(self._rec)
        self.data_list_labels.append(self.label)
        if len(self.data_list_labels) > self.max_list_length:
          del self.data_list_labels[0]
          del self.data_list[0]
        if len(self.data_list) != self.data_list_length:
          self.data_list_length = len(self.data_list)
        if self.data_list_length > 1:
          _dprint(3, 'calling adjust_selector')
          self.adjust_selector()

  def process_data (self):
    """ process the actual record structure associated with a Cache result """
    process_result = False
# are we dealing with an svg result?

    if self._rec.has_key("svg_plot"):
      self.create_layout_stuff()
      self.show_svg_plot()
      process_result = True

# enable & highlight the cell
    self.enable();
    self.flash_refresh();
    _dprint(3, 'exiting process_data')
    return process_result

  def replay_data (self, data_index):
    """ callback to redisplay contents of a result record stored in 
        a results history buffer
    """
    if data_index < len(self.data_list):
      self._rec = self.data_list[data_index]
      self.label = self.data_list_labels[data_index]
      self.results_selector.setLabel(self.label)
      process_result = self.process_data()

  def show_svg_plot(self, store_rec=True):
    """ process incoming vells data and attributes into the
        appropriate type of plot """

# if we are single stepping through requests, Oleg may reset the
# cache, so check for a non-data record situation
    if store_rec and isinstance(self._rec, bool):
      return

    svg_plot = self._rec.svg_plot
    file_name = '/tmp/svg_descriptor.svg'
    file = open(file_name,'w')
    result = file.writelines(svg_plot)
    file.close()

    if self._svg_plotter is None:
      self._svg_plotter = PictureDisplay(self.layout_parent)
      self.layout.addWidget(self._svg_plotter, 0, 0)
    self._svg_plotter.loadPicture(file_name)
    self._svg_plotter.show()
    try:
      os.system("rm -fr "+ file_name);
    except:   pass
    # end show_svg_plot()

  def set_results_buffer (self, result_value):
    """ callback to set the number of results records that can be
        stored in a results history buffer 
    """ 
    if result_value < 0:
      return
    self.max_list_length = result_value
    if len(self.data_list_labels) > self.max_list_length:
      differ = len(self.data_list_labels) - self.max_list_length
      for i in range(differ):
        del self.data_list_labels[0]
        del self.data_list[0]

    if len(self.data_list) != self.data_list_length:
      self.data_list_length = len(self.data_list)

    self.plot_vells_data(store_rec=False)

  def adjust_selector (self):
    """ instantiate and/or adjust contents of ResultsRange object """
    if self.results_selector is None:
      self.results_selector = ResultsRange(self.layout_parent)
      self.results_selector.setMaxValue(self.max_list_length)
      self.results_selector.set_offset_index(0)
      self.layout.addWidget(self.results_selector, 3,1,Qt.AlignHCenter)
      self.results_selector.show()
      QObject.connect(self.results_selector, PYSIGNAL('result_index'), self.replay_data)
      QObject.connect(self.results_selector, PYSIGNAL('adjust_results_buffer_size'), self.set_results_buffer)
      if not self._svg_plotter is None:
        self._svg_plotter.setResultsSelector()
    self.results_selector.set_emit(False)
    self.results_selector.setRange(self.data_list_length-1)
    self.results_selector.setLabel(self.label)
    self.results_selector.set_emit(True)

  def show_selector (self, do_show_selector):
    """ callback to show or hide a ResultsRange object """
    if do_show_selector:
      self.results_selector.show()
    else:
      self.results_selector.hide()

Grid.Services.registerViewer(dmi_type('MeqResult',record),SvgPlotter,priority=10)
Grid.Services.registerViewer(meqds.NodeClass(),SvgPlotter,priority=22)

