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

# this a python translation of the ACSIS zoomwarn2.cc code

import sys
from qt import *

class zoomwarn2(QDialog):
  """ Indicates the user should put the offset to its
      maximum value before zooming on a curve
  """
  def __init__(self, parent=None, name=None):
    QDialog.__init__(self, parent, name, Qt.WType_Popup)

    self.setMinimumSize(0,0)
    self._Popwin = QGroupBox(self,"NoName")
    self._Popwin.setGeometry(10,10,330,200)
    self._Popwin.setMinimumSize(0,0)
    self._Popwin.setTitle("")

    self._Linea= QLabel(self._Popwin,"NoName")
    self._Linea.setGeometry(20,30,290,30)
    self._Linea.setMinimumSize(0,0)
    self._Linea.setText("Please put the offset at its maximum value")

    self._Lineb= QLabel(self,"NoName")
    self._Lineb.setGeometry(50,80,250,30)
    self._Lineb.setMinimumSize(0,0)
    self._Lineb.setText("before zooming by a click on the plot")
  
    self._Closebut= QPushButton(self,"NoName")
    self._Closebut.setGeometry(130,150,100,30)
    self._Closebut.setMinimumSize(0,0)
    self._Closebut.setText("Close")
  
    self.connect(self._Closebut, SIGNAL("clicked()"), self.closewarn)

  def closewarn(self):
    self.close()

  def set_warnings(self, warning1, warning2):
    self._Linea.setText(warning1)
    self._Lineb.setText(warning2)
