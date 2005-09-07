#!/usr/bin/python

###################################
### Class to display selected sources 
### and ask user if a patch should be created
###################################
from qt import *

import sys

class PatchDialog(QDialog):
    def __init__(self,parent = None,name = "Sources",modal = 1,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("Sources")


        FormLayout = QVBoxLayout(self,11,6,"FormLayout")

        self.textEdit = QTextEdit(self,"textEdit")
        self.textEdit.setReadOnly(1)
        FormLayout.addWidget(self.textEdit)

        ButtonLayout=QHBoxLayout(None,0,6,"ButtonLayout")
        self.OKButton = QPushButton(self,"OKButton")
        ButtonLayout.addWidget(self.OKButton)
        self.CancelButton = QPushButton(self,"CancelButton")
        ButtonLayout.addWidget(self.CancelButton)
  
        FormLayout.addLayout(ButtonLayout)
        self.connect(self.OKButton,SIGNAL("clicked()"),self.accept)
        self.connect(self.CancelButton,SIGNAL("clicked()"),self.reject)

        self.languageChange()

        #self.resize(QSize(600,480).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

    def setInfoText(self,text):
        self.textEdit.setText(self.__tr(text))

    def languageChange(self):
        self.setCaption(self.__tr("Sources"))
        self.textEdit.setText(self.__tr("Source is <u>Foo</u> <tt>Bar </tt>kdlkfjs lsdk <h1>name</h1> name"))
        self.OKButton.setText(self.__tr("OK"))
        self.CancelButton.setText(self.__tr("Cancel"))


    def __tr(self,s,c = None):
        return qApp.translate("PatchDialog",s,c)


def main(args):
  app=QApplication(args)
  win=PatchDialog(None)
  win.show()
  app.connect(app,SIGNAL("lastWindowClosed()"),
               app,SLOT("quit()"))
  app.exec_loop()

if __name__=="__main__":
   main(sys.argv)
