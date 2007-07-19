# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'buffersizedialog.ui'
#
# Created: Wed Jan 25 11:40:15 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.13
#
# WARNING! All changes made in this file will be lost!



#% $Id$ 

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

from qt import *
import sys


class BufferSizeDialog(QDialog):
    def __init__(self, buffersize = 0, parent = None,name = None,modal = True,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("BufferSizeDialog")


        BufferSizeDialogLayout = QVBoxLayout(self,11,6,"BufferSizeDialogLayout")

        layout1 = QHBoxLayout(None,0,6,"layout1")

        self.label = QLabel(self,"label")
        layout1.addWidget(self.label)

        self.spinBox1 = QSpinBox(self,"spinBox1")
        self.spinBox1.setMinValue(0)
        self.spinBox1.setWrapping(True)
        self.spinBox1.setValue(buffersize)
        self.value = buffersize

        layout1.addWidget(self.spinBox1)
        BufferSizeDialogLayout.addLayout(layout1)

        layout3 = QHBoxLayout(None,0,6,"layout3")
        spacer1 = QSpacerItem(71,31,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout3.addItem(spacer1)

        self.okButton = QPushButton(self,"okButton")
        layout3.addWidget(self.okButton)

        self.cancelButton = QPushButton(self,"cancelButton")
        layout3.addWidget(self.cancelButton)
        BufferSizeDialogLayout.addLayout(layout3)

        self.languageChange()

        self.resize(QSize(267,84).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okButton,SIGNAL("clicked()"),self.runDone)
        self.connect(self.cancelButton,SIGNAL("clicked()"),self.runCancel)
        self.connect(self.spinBox1,SIGNAL("valueChanged(int)"),self.updateValue)

        self.label.setBuddy(self.spinBox1)


    def languageChange(self):
        self.setCaption(self.__tr("Specify Buffer Size"))
        self.label.setText(self.__tr("Buffer Size"))
        self.okButton.setText(self.__tr("OK"))
        self.cancelButton.setText(self.__tr("Cancel"))


    def updateValue(self,a0):
        self.value = a0

    def runDone(self):
        self.emit(PYSIGNAL("return_value"),(self.value,))
        self.done(self.value)

    def runCancel(self):
        self.value = -1
        self.runDone()

    def __tr(self,s,c = None):
        return qApp.translate("BufferSizeDialog",s,c)


def main(args):
    app = QApplication(args)
    demo = BufferSizeDialog(10)
    demo.show()
    app.setMainWidget(demo)
    app.exec_loop()

# main()

# Admire
if __name__ == '__main__':
    main(sys.argv)

