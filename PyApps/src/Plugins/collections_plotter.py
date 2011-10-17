#!/usr/bin/python
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

from math import sin
from math import cos
from math import pow
from math import sqrt

# modules that are imported
from Timba.dmi import *
from Timba import utils
from Timba.Meq import meqds
from Timba.Meq.meqds import mqs
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI import widgets
from Timba.GUI.browsers import *
from Timba import Grid

from PyQt4 import Qt
from Timba.Plugins.DataDisplayMainWindow_qt4 import *

from VellsData import *
from ResultsRange_qt4 import *
from BufferSizeDialog_qt4 import *
from plot_printer_qt4 import *

import itertools

from Timba.utils import verbosity
_dbg = verbosity(0,name='collections_plotter');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class CollectionsPlotter(GriddedPlugin):
  """ a class to visualize data, VellSets or visu data, that is 
      contained within a node's cache_result record. Objects of 
      this class are launched from the meqbrowser GUI """

  _icon = pixmaps.bars3d
  viewer_name = "Collections Plotter";
  def is_viewable (data):
    return len(data) > 0;
  is_viewable = staticmethod(is_viewable);

  def __init__(self,gw,dataitem,cellspec={},**opts):
    GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);
    """ Instantiate plotter object that is used to display plots
    """
    self.set_init_parameters()
# back to 'real' work
    self.dataitem = dataitem
    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

  def set_init_parameters(self):
    self._rec = None;
    self._plot_type = None
    self._wtop = None;
    self._vells_data = None
    self.layout_created = False
    self.layout_parent = None
    self.layout = None
    self._visu_plotter = None
    self.counter = 0
    self.max_range = 0
    self._node_name = None
    self._prev_rq_id = -1
    self._plot_label = None
    self._tab_label = 'Page'
    self.prev_label = "===="

  def wtop (self):
    """ function needed by Oleg for reasons known only to him! """
    return self._wtop;

  def create_layout_stuff(self):
    """ create grid layouts into which plotter widgets are inserted """
    if self.layout_parent is None or not self.layout_created:
      self.layout_parent = Qt.QWidget(self.wparent())
      self.layout = Qt.QHBoxLayout(self.layout_parent)
      self.set_widgets(self.layout_parent,self.dataitem.caption,icon=self.icon())
      self.layout_created = True
    self._wtop = self.layout_parent;       
    self.create_2D_plotter()


  def create_2D_plotter(self):
    if self._visu_plotter is None:
      self._visu_plotter = DisplayMainWindow(parent=None,name=" ", num_curves=self._max_per_display, plot_label=self._plot_label)
      self.layout.addWidget(self._visu_plotter,100)
      lo0 = QVBoxLayout();
      lo0.setContentsMargins(0,0,0,0);
      self.layout.addLayout(lo0,0);
      lo1 = QHBoxLayout();
      lo1.setContentsMargins(0,0,0,0);
      lo0.addLayout(lo1);
      lo1.addStretch(1);
      self._results_range = ResultsRange(parent=self.layout_parent, name="", horizontal=False)
      lo1.addStretch(1);
      lo1.addWidget(self._results_range)
      # add data selectors 
      self._visu_plotter.createDataSelectorWidgets(self.layout_parent,lo0);
      #
      self._visu_plotter.show()
      self._results_range.set_offset_index(0)
      Qt.QObject.connect(self._visu_plotter, Qt.SIGNAL("auto_offset_value"), self.set_range_selector)
      Qt.QObject.connect(self._results_range, Qt.SIGNAL("result_index"), self._visu_plotter.set_range_selector)
      Qt.QObject.connect(self._results_range, Qt.SIGNAL("set_auto_scaling"), self._visu_plotter.set_auto_scaling)
  # create_2D_plotter

  
  def set_range_selector(self, max_range):
    """ set or update maximum range for slider controller """
    self.max_range = max_range
    self._results_range.set_emit(False)
    self._results_range.setMinValue(0)
    self._results_range.setMaxValue(max_range,False)
    self._results_range.setTickInterval( max_range / 10 )
    self._results_range.setRange(max_range, False)
    self._results_range.setLabel('offset:',align=Qt.Qt.AlignHCenter)
    self._results_range.hideNDControllerOption()
    self._results_range.reset_scale_toggle()
    self._results_range.set_emit(True)
    self._results_range.show()

  def set_data (self,dataitem,default_open=None,**opts):
    """ this callback receives data from the meqbrowser, when the
        user has requested a plot. It decides whether the data is
        from a VellSet or visu data record, and  after any
        necessary preprocssing forwards the data to one of
        the functions which does the actual plotting """

    _dprint(3, '** in collections_plotter:set_data callback')
    self._rec = dataitem.data;
    _dprint(3, 'set_data: initial self._rec ', self._rec)
    _dprint(3, 'incoming record has keys ', self._rec.keys())
# if we are single stepping through requests, Oleg may reset the
# cache, so check for a non-data record situation
    if self._rec is None:
      return
    if isinstance(self._rec, bool):
      return

    try:
      self._node_name = self._rec.name
    except:
      pass
    _dprint(3, 'node name is ', self._node_name)

    if hasattr(self._rec,'plot_label'):
      self._plot_label = self._rec.plot_label;
    if hasattr(self._rec,'tab_label'):
      self._tab_label = self._rec.tab_label;
    self._vells_label = getattr(self._rec,'vells_label',[]);
    if not isinstance(self._vells_label,(list,tuple)):
      self._vells_label = [];
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
            rq_id_found = True
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
        cache_message = Qt.QLabel(Message,self.wparent())
        cache_message.setTextFormat(Qt.Qt.RichText)
        self._wtop = cache_message
        self.set_widgets(cache_message)
        self.set_init_parameters()
        return
      _dprint(3, 'collections: request id ', self.label)
      end_str = len(self.label)
      self._rq_id_end = int(self.label[end_str-1:end_str])
      if self._rq_id_end == self._prev_rq_id:
        new_plot = False
      else:
        new_plot = True
        self._prev_rq_id = self._rq_id_end
      
      if self.label.find(self.prev_label) >= 0:
# we have already plotted this stuff, so return
        return
      else:
        self.prev_label = self.label

# are we dealing with Vellsets?
    self.counter = self.counter + 1
    self._max_per_display = 64
    if self._rec.has_key("dims"):
      _dprint(3, '*** dims field exists ', self._rec.dims)
      self.dims = list(self._rec.dims)
    else:
      self.dims = None
    if self._rec.has_key("vellsets"):
      self._number_of_planes = len(self._rec["vellsets"])
      self.dims_per_group = 1
      if not self.dims is None:
        # in collections plotter, assume that first 'dims' 
        # corresponds to tracks that are displayed , so determine
        # size of group from second dimension and up
        if len(self.dims) > 1:
          dims_start = 1
          for i in range(dims_start,len(self.dims)):
            self.dims_per_group = self.dims_per_group * self.dims[i]
          if self.dims_per_group == len(self._vells_label):
            index_labels = self._vells_label;
          else:
            # setup index array -- this makes a list such as [1,1],[1,2],[2,1],[2,2] (for e.g. a 2x2 array)
            indices = numpy.ndindex(*self.dims[dims_start:]);
            # sep = "," if any([dim>9 for dim in self.dims[dims_start:]]) else "";
            index_labels = [ ",".join([str(x+1) for x in ind]) for ind in indices ];
        else:
          index_labels = self._vells_label[0:1] if self._vells_label else [0];
      # replace index labels with vells labels
      if self._visu_plotter is None:
        self.create_layout_stuff()
      if new_plot: 
        self._visu_plotter.setNewPlot()
      data_dict = {}
      self._visu_plotter.setDataElementLabels(index_labels,list(self.dims[1:]) if self.dims is not None else (1,));
      for i in range(self._number_of_planes):
        channel = int(i / self.dims_per_group)
        if self._node_name is None:
          data_dict['source'] = "Channel " + str(channel)
        else:
          data_dict['source'] = self._node_name
        data_dict['channel'] = channel
        data_dict['sequence_number'] = self.counter
        screen_num = channel / self._max_per_display
        data_dict['data_type'] = self._tab_label + ' ' + str(screen_num+1)
        index = i - channel * self.dims_per_group
        if index == 0:
          data_dict['value'] = {}
          data_dict['flags'] = {}
        datakey = index_labels[index];
#       if channel == 100:
#         data_dict['value'][index] = 100.0 * self._rec.vellsets[i].value
#       else:

# hopefully handle cases with non-existent results
        try:
          if  self._rec.vellsets[i].has_key("value"):
            data_dict['value'][datakey] = self._rec.vellsets[i].value
          else:
            data_dict['value'][datakey] = None
        except:
            data_dict['value'][datakey] = None
# for test purposes
#       if index == 2:
#           data_dict['value'][datakey] = None
        try:
          if  self._rec.vellsets[i].has_key("flags"):
            data_dict['flags'][datakey] = self._rec.vellsets[i].flags
          else:
            data_dict['flags'][datakey] = None
        except:
            data_dict['flags'][datakey] = None
        if index == self.dims_per_group-1:
          self._visu_plotter.updateEvent(data_dict)
          data_dict = {}

# enable & highlight the cell
    self.enable();
    self.flash_refresh();
    _dprint(3, 'exiting process_data')

Grid.Services.registerViewer(meqds.NodeClass(),CollectionsPlotter,priority=30)

