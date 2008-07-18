#!/usr/bin/python

# modules that are imported

#% $Id: quickref_plotter.py 6250 2008-07-11 05:55:05Z twillis $ 

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
from plot_printer import *

from Timba.utils import verbosity
_dbg = verbosity(0,name='quickref_plotter');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class QuickRefPlotter(GriddedPlugin):
  """ a class to display quickref_help contents of a node in the browser """ 

  _icon = pixmaps.bars3d
  viewer_name = "QuickRef Display";
  def is_viewable (data):
    return len(data) > 0;
  is_viewable = staticmethod(is_viewable);

  def __init__(self,gw,dataitem,cellspec={},**opts):
    GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);
    """ Instantiate HippoDraw objects that are used to control
        various aspects of plotting, if the hippo plotter
        is instantiated.
    """
    self._rec = None;
    self._wtop = None;
    self.dataitem = dataitem
    self.layout_created = False
    self.reset_plot_stuff()

# back to 'real' work
    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

  def reset_plot_stuff(self):
    """ resets widgets to None. Needed if we have been putting
        out a message about Cache not containing results, etc
    """
    self.QTextEdit = None
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
      self.QTextEdit = QTextEdit(self.layout_parent)
      self.layout.addWidget(self.QTextEdit, 0, 1)
      self.QTextEdit.hide()
      self.QTextEdit.setReadOnly(True)
      self.set_widgets(self.layout_parent,self.dataitem.caption,icon=self.icon())
      self.layout_created = True
    self._wtop = self.layout_parent;       

  def update_status(self, status):
     if not status is None:
       self.status_label.setText(status)

  def set_data (self,dataitem,default_open=None,**opts):
    """ this callback receives data from the meqbrowser, when the
        user has requested a QuickRef display . If there is a 
        'quickref_help' record it will be shown via a QTextEdit 
        widget in the browser """

    _dprint(3, '** in quickref_plotter:set_data callback')
    self._rec = dataitem.data;
    _dprint(3, 'set_data: initial self._rec ', self._rec)
    if self._rec is None:
      return
    if isinstance(self._rec, bool):
      return
    if self._rec.has_key("quickref_help"):
      self.create_layout_stuff()
      Message = ""
      try:
        for i in range(len(self._rec.quickref_help)):
          text = str(self._rec.quickref_help[i])
          if not text is None:
            Message = Message + text +"\n"
      except:
          pass
      if len(Message) > 0:
        self.QTextEdit.setText(Message)
        self.QTextEdit.show()
      return

Grid.Services.registerViewer(dmi_type('MeqResult',record),QuickRefPlotter,priority=10)
Grid.Services.registerViewer(meqds.NodeClass(),QuickRefPlotter,priority=22)

