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

# a small class used to get mouse events to work in Qwt5 in basically
# the same way we had things working with Qwt4

# Adapted from a PyQwt example - thanks Gerard!

#from qt import *
from PyQt4 import Qt

class Spy(Qt.QObject):

    def __init__(self, parent):
        Qt.QObject.__init__(self, parent)
        parent.setMouseTracking(True)
        parent.installEventFilter(self)

    # __init__()

    def eventFilter(self, _, event):
        if event.type() == Qt.QEvent.MouseMove:
#           self.emit(Qt.SIGNAL("MouseMove"), event.pos())
            self.emit(Qt.SIGNAL("MouseMove"), event)
        if event.type() == Qt.QEvent.MouseButtonPress:
            self.emit(Qt.SIGNAL("MousePress"), event)
        if event.type() == Qt.QEvent.MouseButtonRelease:
            self.emit(Qt.SIGNAL("MouseRelease"), event)
        return False

    # eventFilter()

# class Spy

