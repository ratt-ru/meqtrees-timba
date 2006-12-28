#!/usr/bin/env python

#
# Copyright (C) 2007
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

# This is a python translation of the ACSIS zoomwarn.cc code

import sys
from qt import *

class zoomwarn(QDialog):
  """ Indicates the user should close all zoom windows
      before using binning or channel separation
  """
  def __init__(self, parent=None, name=None):
    QDialog.__init__(self, parent, name, Qt.WType_Popup)

    self.setMinimumSize(0,0)
    self._Popwin = QGroupBox(self,"NoName")
    self._Popwin.setGeometry(10,10,330,200)
    self._Popwin.setMinimumSize(0,0)
    self._Popwin.setTitle("")

    self._Line1 = QLabel(self._Popwin,"NoName")
    self._Line1.setGeometry(20,30,290,30)
    self._Line1.setMinimumSize(0,0)
    self._Line1.setText("All zoom windows should be closed before\nusing binning or channel separation")

    self._Closebut= QPushButton(self,"NoName")
    self._Closebut.setGeometry(120,170,130,30)
    self._Closebut.setMinimumSize(0,0)
    self._Closebut.setText("Close all zoom")

    self._Continue = QPushButton(self,"NoName")
    self._Continue.setGeometry(130,120,110,30)
    self._Continue.setMinimumSize(0,0)
    self._Continue.setText("Continue")
  
    self.connect(self._Closebut, SIGNAL("clicked()"),parent.self.closezoomfun)
    self.connect(self._Closebut, SIGNAL("clicked()"), self.closewarn)
    self.connect(self._Continue, SIGNAL("clicked()"), self.closewarn)

  def closewarn(self):
    self.close()

  def set_warning(self, warning):
    self._Line1.setText(warning)
