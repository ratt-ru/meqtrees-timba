# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'buffersizedialog.ui'
#
# Created: Wed Jan 25 11:40:15 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.13
#
# WARNING! All changes made in this file will be lost!


#% $Id: BufferSizeDialog.py 5418 2007-07-19 16:49:13Z oms $ 

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
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys

from qwt.qt.QtGui import (QApplication, QDialog, QHBoxLayout,
         QLabel, QSizePolicy, QSlider, QPushButton, QVBoxLayout, QSpinBox, QSpacerItem)
from qwt.qt.QtCore import Qt, QSize, QObject, pyqtSignal
from qwt.qt.QtGui import QWidget, QFont, QFontInfo


class BufferSizeDialog(QDialog):

    return_value = pyqtSignal(int)

    def __init__(self, buffersize = 0, parent = None,name = None,modal = True,fl = 0):
        QDialog.__init__(self,parent)

        self.setModal(modal)

        BufferSizeDialogLayout = QVBoxLayout(self)

        layout1 = QHBoxLayout(None)

        self.label = QLabel(self)
        layout1.addWidget(self.label)

        self.spinBox1 = QSpinBox(self)
        self.spinBox1.setMinimum(0)
        self.spinBox1.setWrapping(True)
        self.spinBox1.setValue(buffersize)
        self.value = buffersize

        layout1.addWidget(self.spinBox1)
        BufferSizeDialogLayout.addLayout(layout1)

        layout3 = QHBoxLayout(None)
        spacer1 = QSpacerItem(71,31,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout3.addItem(spacer1)

        self.okButton = QPushButton("okButton",self)
        layout3.addWidget(self.okButton)

        self.cancelButton = QPushButton("cancelButton",self)
        layout3.addWidget(self.cancelButton)
        BufferSizeDialogLayout.addLayout(layout3)

        self.resize(QSize(267,84).expandedTo(self.minimumSizeHint()))

        self.okButton.clicked.connect(self.runDone)
        self.cancelButton.clicked.connect(self.runCancel)
        self.spinBox1.valueChanged.connect(self.updateValue)

        self.label.setBuddy(self.spinBox1)



    def updateValue(self,a0):
        self.value = a0

    def runDone(self):
        self.return_value.emit(self.value)
        self.done(self.value)

    def runCancel(self):
        self.value = -1
        self.runDone()

def main(args):
    app = QApplication(args)
    demo = BufferSizeDialog(10)
    demo.show()
    app.exec_()

# main()

# Admire
if __name__ == '__main__':
    main(sys.argv)

