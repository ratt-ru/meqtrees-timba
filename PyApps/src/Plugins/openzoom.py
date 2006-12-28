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

# this is a python translation of the ACSIS openzoom.cc code

import sys
from qt import *

class OpenZoom(QDialog):
  """ shows a warning that a zoom window of the same curve is already opened
  """
  def __init__(self, parent=None, name=None):
    QDialog.__init__(self, parent, name, Qt.WType_Popup)
  
    self.setMinimumSize(0,0)
    self._Popwin = QGroupBox(self,"NoName")
    self._Popwin.setGeometry(10,10,330,200)
    self._Popwin.setMinimumSize(0,0)
    self._Popwin.setTitle("")

    self._Label1= QLabel(self._Popwin,"NoName")
    self._Label1.setGeometry(20,30,290,30)
    self._Label1.setMinimumSize(0,0)
    self._Label1.setText("A zoom of this curve is already opened")

    self._Closebut= QPushButton(self,"NoName")
    self._Closebut.setGeometry(130,150,100,30)
    self._Closebut.setMinimumSize(0,0)
    self._Closebut.setText("Close")
  
    # Connection to close the warning window
    connect(self._Closebut, SIGNAL("clicked()"), self.closewarn)

  def closewarn(self):
    self.close()
