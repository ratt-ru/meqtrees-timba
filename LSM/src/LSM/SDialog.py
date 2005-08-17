#!/usr/bin/python

###################################
### Class to display information on
### anything user has clicked on.
###################################
from qt import *

import sys

class SDialog(QDialog):
    def __init__(self,parent = None,name = "Source Info",modal = 1,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("Source Info")


        FormLayout = QVBoxLayout(self,11,6,"FormLayout")

        self.textEdit = QTextEdit(self,"textEdit")
        self.textEdit.setReadOnly(1)
        FormLayout.addWidget(self.textEdit)

        self.pushButton = QPushButton(self,"pushButton")
        FormLayout.addWidget(self.pushButton)
        self.connect(self.pushButton,SIGNAL("clicked()"),self.accept)

        self.languageChange()

        #self.resize(QSize(600,480).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

    def setInfoText(self,text):
        self.textEdit.setText(self.__tr(text))

    def languageChange(self):
        self.setCaption(self.__tr("Source Info"))
        self.textEdit.setText(self.__tr("Source is <u>Foo</u> <tt>Bar </tt>kdlkfjs lsdk <h1>name</h1> name"))
        self.pushButton.setText(self.__tr("OK"))


    def __tr(self,s,c = None):
        return qApp.translate("SDialog",s,c)


def main(args):
  app=QApplication(args)
  win=SDialog(None)
  win.show()
  app.connect(app,SIGNAL("lastWindowClosed()"),
               app,SLOT("quit()"))
  app.exec_loop()

if __name__=="__main__":
   main(sys.argv)
