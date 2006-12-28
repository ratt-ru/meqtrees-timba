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

# this is a python translation of the ACSIS zoomcontrol.cc code

import sys
from qt import *

class ZoomControlFrame(QFrame):

  def __init__(self, parent=None, name=None):
    QFrame.__init__(self, parent, name)

    cursorInfo2 = "Cursor Pos: Press mouse button in plot region"
    self._lblInfo = QLabel(cursorInfo2, self)
    self._lblInfo.setFont(QFont("Helvetica", 12))
    self._lblInfo.setMinimumSize(self._lblInfo.sizeHint() )

    self._btnZoom = QPushButton("Zoom", self)
    self._btnZoom.setMinimumSize(self._btnZoom.sizeHint() )
    QToolTip.add(self._btnZoom, "enable zooming with left mouse button")
    QWhatsThis.add(self._btnZoom, "Use self button to select a region of the plot that you wish to study in more detail. After clicking on the `Zoom' button, move your mouse into the plot area and trace out a rectangle while holding the left mouse button down. When you release the left mouse button the plot will just display the selected region in detail. At the same time the text on the button will change to `Unzoom'. Clicking on the button will now cause the plot to revert to showing everything. The text will then change back to `Zoom' so that you can select another area if you wish.")

    self._btnPrint = QPushButton("Print", self)
    self._btnPrint.setMinimumSize(self._btnPrint.sizeHint() )
    QToolTip.add(self._btnPrint, "get a postscript print of plot")
    QWhatsThis.add(self._btnPrint, "Click on self button to get a printout of the current plot. The Qt print selection widget will appear and you can use it to specify if you would like the plot sent directly to a printer or stored as a file in Postscript format.")

    self._btnClose = QPushButton("Close", self)
    self._btnClose.setMinimumSize(self._btnClose.sizeHint() )
    QToolTip.add(self._btnClose, "close self window")
    QWhatsThis.add(self._btnClose, "Click on self button if you want the plot to close down and disappear.")

    self._lblchan = QLabel("Channel ", self)
    self._lblchan.setFont(QFont("Helvetica", 16))
    self._lblchan.setMinimumSize(self._lblchan.sizeHint() )


    self._lblchno = QLabel("0", self)
    self._lblchno.setFont(QFont("Helvetica", 16))
    self._lblchno.setMinimumSize(self._lblchno.sizeHint() )

# stick above buttons into a layout
    vbox_left = QVBoxLayout( self )
    vbox_left.setSpacing(10)
    box1 = QHBoxLayout( vbox_left )
    box1.addWidget(self._lblInfo)
    box2 = QHBoxLayout(vbox_left)
    box2.addWidget(self._btnZoom)
    box2.addWidget(self._btnPrint)
    box2.addWidget(self._btnClose)
    box2.addWidget(self._lblchan)
    box2.addWidget(self._lblchno)
    box2.setSpacing(10)
    box2.addStretch(1)
 
    self._btnPause = QPushButton("Pause", self)
    self._btnPause.setMinimumSize(self._btnPause.sizeHint() )
    QToolTip.add(self._btnPause, "pause the display")
    QWhatsThis.add(self._btnPause, "Click on self button if you want the plot to pause. The plot will stop updating the display and you can examine the current plot in detail. At the same time the text on the button will change from `Pause' to `Resume'. Clicking on `Resume' will cause the plot to start updating at the current event.")

    self._btnStartCompare = QPushButton("DoComparison", self)
    self._btnStartCompare.setMinimumSize(self._btnStartCompare.sizeHint() )
    QToolTip.add(self._btnStartCompare, "show maxima and minima")
    QWhatsThis.add(self._btnStartCompare, "Click on self button if you want a plot of the current maxima and minima of all spectra to be displayed along with the current spectrum. At the same time the text on the button will change from `DoComparison' to `StopComparison'. Clicking on `StopComparison' will then cause the plot of the current maxima to disappear.")

    self._btnReset = QPushButton("ResetComparison", self)
    self._btnReset.setMinimumSize(self._btnReset.sizeHint() )
    QToolTip.add(self._btnReset, "resets the comparison of maxima and minima")
    QWhatsThis.add(self._btnReset, "Click on self button if you want to start a new comparison vector of current maxima. This button will only do anything useful if you had the `DoComparison' flag on.")

    self._btnScale = QPushButton("Log Scale", self)
    self._btnScale.setMinimumSize(self._btnScale.sizeHint() )
    QToolTip.add(self._btnScale, "switch between log and linear scales")
    QWhatsThis.add(self._btnScale, "Click on self button if you want to switch the scale of the Y axis between linear and logarithmic.")

    self._btnSetScale = QPushButton("Fixed Scale", self)
    self._btnSetScale.setMinimumSize(self._btnSetScale.sizeHint() )
    QToolTip.add(self._btnSetScale, "switch between auto and fixed scales")
    QWhatsThis.add(self._btnSetScale, "Click on self button if you want to switch between automatic and fixed scaling of the Y axis.")

    spacer = QSpacerItem( 0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum )

    box3 = QHBoxLayout( vbox_left )
    box3.addWidget(self._btnPause)
    box3.addWidget(self._btnStartCompare)
    box3.addWidget(self._btnReset)
    box3.addWidget(self._btnScale)
    box3.addWidget(self._btnSetScale)
    box3.addItem( spacer )
    box3.setSpacing(10)
    box2.addStretch(1)

def main(args):
    app = QApplication(args)
    demo = ZoomControlFrame()
    demo.show()
    app.setMainWidget(demo)
    app.exec_loop()

# Admire
if __name__ == '__main__':
    main(sys.argv)

