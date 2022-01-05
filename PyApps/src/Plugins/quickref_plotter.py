#!/usr/bin/env python3

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

# modules that are imported
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from qwt.qt.QtGui import QApplication, QGridLayout, QWidget
from qwt.qt.QtCore import Qt, QObject, pyqtSignal

# modules that are imported

HAS_TIMBA = False
try:
  from Timba import utils
  from Timba.Meq import meqds
  from Timba.Meq.meqds import mqs
  from Timba.GUI.pixmaps import pixmaps
  from Timba.GUI import widgets
  from Timba.GUI.browsers import *
  from Timba import Grid
  from Timba.utils import verbosity
  _dbg = verbosity(0,name='quickref_plotter');
  _dprint = _dbg.dprint;
  _dprintf = _dbg.dprintf;
  HAS_TIMBA = True
except:
  pass

#print('HAS_TIMBA = ', HAS_TIMBA)

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
    """ This callback receives data from the meqbrowser, when the
    user has requested a QuickRef display . If there is a 
    'quickref_help' field (string) it will be shown via a
    QTextEdit widget in the browser.
    """

    if HAS_TIMBA: _dprint(3, '** in quickref_plotter:set_data callback')
    self._rec = dataitem.data;
    if HAS_TIMBA: _dprint(3, 'set_data: initial self._rec ', self._rec)
    if not isinstance(self._rec,record):
      # print '\n** self.rec not a record, but:',type(self._rec)
      pass
    elif "quickref_help" not in self._rec:
      # print '\n** self.rec does not have quickref_help field'
      pass
    else:
      qh = self._rec.quickref_help
      # print '\n** self.rec.quickref_help:',type(qh)
      if isinstance(qh,str):
        self.create_layout_stuff()
        self.QTextEdit.setText(qh)
        self.QTextEdit.show()
    return

Grid.Services.registerViewer(meqds.NodeClass(),QuickRefPlotter,priority=40)
