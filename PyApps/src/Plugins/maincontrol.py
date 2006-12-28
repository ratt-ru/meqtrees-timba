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

# This is a python translation of the ACSIS mainbot.cc code

import sys
from qt import *

class MainControl(QFrame):
  """ pass the parent and the name of the widget created.  
      Puts all the push buttons in place for nice looking bottom frame.
  """

  def __init__(self, parent=None, name=None):
    QFrame.__init__(self, parent, name)

    font = QFont("Helvetica",10)
    cursorInfo = "Cursor Pos: Press mouse button in plot region"
    self._lblInfo = QLabel(cursorInfo, self)
    self._lblInfo.setFont(font)
    self._lblInfo.setMinimumSize(self._lblInfo.sizeHint() )

    vbox_left = QVBoxLayout( self )
    vbox_left.setSpacing(10)
    box1 = QHBoxLayout( vbox_left )
    box1.addWidget(self._lblInfo)

    self._btnZoom = QPushButton("Zoom", self)
    self._btnZoom.setFont(font)
    self._btnZoom.setMinimumSize(self._btnZoom.sizeHint() )
    QToolTip.add(self._btnZoom, "enable zooming with left mouse button")
    QWhatsThis.add(self._btnZoom, "Use this button to select a region of the plot that you wish to study in more detail. After clicking on the `Zoom' button, move your mouse into the plot area and trace out a rectangle while holding the left mouse button down. When you release the left mouse button the plot will just display the selected region in detail. At the same time the text on the button will change to `Unzoom'. Clicking on the button will now cause the plot to revert to showing everything. The text will then change back to `Zoom' so that you can select another area if you wish.")

    self._btnPrint = QPushButton("Print", self)
    self._btnPrint.setFont(font)
    self._btnPrint.setMinimumSize(self._btnPrint.sizeHint() )
    QToolTip.add(self._btnPrint, "get a postscript printout of the display")
    QWhatsThis.add(self._btnPrint, "Click on this button to get a printout of the current plot. The Qt print selection widget will appear and you can use it to specify if you would like the plot sent directly to a printer or stored as a file in Postscript format.")

    self._btnQuit = QPushButton("Close", self)
    self._btnQuit.setFont(font)
    self._btnQuit.setMinimumSize(self._btnQuit.sizeHint() )
    QToolTip.add(self._btnQuit, "close this window")
    QWhatsThis.add(self._btnQuit, "Click on this button if you want the plot to close down and disappear.")

    self._btnPause = QPushButton("Pause",self)
    self._btnPause.setFont(font)
    QToolTip.add(self._btnPause, "pause the display of data")
    QWhatsThis.add(self._btnPause, "Click on this button if you want the plot to pause. The plot will stop updating the display and you can examine the current plot in detail. At the same time the text on the button will change from `Pause' to `Resume'. Clicking on `Resume' will cause the plot to start updating at the current event.")

    self._btnSetScale = QPushButton("Fixed Scale", self)
    self._btnSetScale.setMinimumSize(self._btnSetScale.sizeHint() )
    QToolTip.add(self._btnSetScale, "switch between auto and fixed scaling")
    QWhatsThis.add(self._btnSetScale, "Click on this button if you want to switch between automatic and fixed scaling of the Y axis.")

    self._btnSetOffset = QPushButton("Offset Value", self)
    self._btnSetOffset.setMinimumSize(self._btnSetOffset.sizeHint() )
    QToolTip.add(self._btnSetOffset, "specify offset value between plots")
    QWhatsThis.add(self._btnSetOffset, "Click on this button if you want to specify an offset value between plots. A negative value for the offset implies auto scale offset.")

    self._progressBar = QProgressBar(self)
    self._progressBar.setPercentageVisible(False)
    self._progressBar.setMinimumSize(self._progressBar.sizeHint() )
    self._progressBar.hide()
    QWhatsThis.add(self._progressBar, "This progress bar pops up to show the amount of work that has been done for operations such as averaging.")

    blank = ""
    self._progressLabel = QLabel(blank, self)
    self._progressLabel.setFont(font)
    self._progressLabel.setMinimumSize(self._progressLabel.sizeHint() )

    spacer = QSpacerItem( 0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum )

    box2 = QHBoxLayout( vbox_left )
    box2.addWidget(self._btnZoom)
    box2.addWidget(self._btnPrint)
    box2.addWidget(self._btnPause)
    box2.addWidget(self._btnQuit)
    box2.addWidget(self._btnSetScale)
    box2.addWidget(self._btnSetOffset)
    box2.addWidget(self._progressBar)
    box2.addWidget(self._progressLabel)
    box2.addItem( spacer )
    box2.setSpacing(10)
    box2.addStretch(1)
