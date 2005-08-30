#!/usr/bin/python

#########################################################
### The main Window and the Tabs
#########################################################

import sys
import math
from qt import *
from qttable import QTable
from qtcanvas import *

from LSM import *
from common_utils import *

from OptionsDialog import *
from FTDialog import *
from MyCanvasView import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x00" \
    "\x77\x49\x44\x41\x54\x38\x8d\x63\x60\xa0\x11\x60" \
    "\xc4\x22\xf6\x9f\x02\xbd\x70\xc0\x84\x4d\xf0\xff" \
    "\xff\xff\x38\x31\x03\x03\x03\x83\xa6\x8e\x26\x41" \
    "\x07\x60\x35\x98\x10\x30\x34\x34\x24\x68\x38\x0b" \
    "\x39\x06\x6b\x6a\x68\xc2\xd9\xd7\xaf\x5c\xff\xcf" \
    "\x80\x25\x58\xc8\x32\xd8\xc9\xd6\x09\x85\x8f\xcd" \
    "\x70\xb2\x0c\xb6\xb2\xb5\xc2\x10\x43\x37\x9c\x2c" \
    "\x83\x19\x19\xf1\x26\x08\xf2\x0c\x86\xa5\x0c\x42" \
    "\x96\x91\x95\x2a\x88\x01\xa3\x06\x8f\x1a\x3c\x6a" \
    "\x30\x1e\x40\x49\x0d\x42\xac\x79\x43\x04\x00\x00" \
    "\x25\x19\x2a\x1c\x1c\xcc\x28\x4a\x00\x00\x00\x00" \
    "\x49\x45\x4e\x44\xae\x42\x60\x82"
image1_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x00" \
    "\x99\x49\x44\x41\x54\x38\x8d\xed\x94\x41\x0e\x85" \
    "\x20\x0c\x44\x5f\x89\xd7\x36\x3f\xc6\x83\xd7\x85" \
    "\x82\x44\x8a\x02\xf6\xef\x9c\x4d\xb5\xe8\xeb\x38" \
    "\x41\xe0\xd3\x21\x19\x78\x47\x1f\x18\x3a\xc2\xbd" \
    "\x42\x63\x4f\xaf\xd7\x23\x8e\x5b\x86\x4a\xf8\x03" \
    "\x14\x80\xa9\xb2\xd0\xf3\x25\x56\x3c\x08\xa0\xaa" \
    "\x71\x5d\x00\x45\xa4\x99\x5b\x7d\x70\x3a\x87\x4a" \
    "\xaa\xfb\x24\x29\xfa\x3d\xc3\x43\x66\xbc\xb3\xde" \
    "\x2b\x58\x8e\xdb\xea\xbd\xcc\x8c\x07\xb2\x2e\x64" \
    "\x66\x9c\x43\xd7\xa5\x0f\x38\xff\xf6\x6a\x66\xfc" \
    "\x16\xca\xf9\x83\xf8\x42\x0b\xc7\x5e\xd0\x0c\xec" \
    "\x0b\x8d\x37\x69\xef\x78\x41\x21\x39\xf6\x85\xc6" \
    "\xe6\xf3\x6e\xaf\xcb\xf3\xd8\x6d\xd3\x06\xc2\x20" \
    "\x45\x2c\xdf\x60\xc8\xbd\x00\x00\x00\x00\x49\x45" \
    "\x4e\x44\xae\x42\x60\x82"
image2_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x00" \
    "\xa2\x49\x44\x41\x54\x38\x8d\x63\x60\xa0\x11\x60" \
    "\x84\xd2\xff\xa9\x6d\x2e\x0b\x8c\xd5\xdc\x08\xa1" \
    "\x6b\xeb\x19\x18\x8e\x1e\x3a\x4a\x92\x29\xd6\x76" \
    "\xd6\x70\x3d\xd6\x76\xd6\x0c\x0c\x0c\x0c\x0c\x4c" \
    "\x54\x72\x21\x06\x60\x21\xac\x04\x3b\xe0\xf8\x22" \
    "\xc0\xf0\x83\xe7\x03\x9c\x0f\x73\x29\x0c\x10\x74" \
    "\x31\xc7\x17\x01\x06\x8e\x2f\x02\x18\xe2\xc8\x86" \
    "\x32\x30\x40\x82\x12\x16\x9c\x44\x19\x4c\x2e\x20" \
    "\x18\x14\xe8\x2e\x23\x16\xd0\xcc\xc5\x43\xcf\x60" \
    "\x8c\x30\x6e\x6e\xc4\x4c\x3a\x84\x00\x72\x6a\xc0" \
    "\x69\x30\x2e\x85\xa4\x02\xfa\x26\xb7\xda\x7a\xd2" \
    "\x0d\x42\xf7\x25\xd9\x59\x1a\xb9\xa0\xc2\x16\x27" \
    "\x43\x2f\xb9\x0d\x3d\x83\x19\x91\xd8\xd4\xaa\x9e" \
    "\x18\x09\x2b\xa1\x00\x00\x00\x1a\x6d\x1e\xb1\xec" \
    "\x51\x25\x55\x00\x00\x00\x00\x49\x45\x4e\x44\xae" \
    "\x42\x60\x82"
image3_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x02" \
    "\xb9\x49\x44\x41\x54\x38\x8d\x8d\x94\xbd\x6f\x13" \
    "\x4d\x10\xc6\x7f\x46\x2e\x66\x25\x8a\xbd\xee\x22" \
    "\x51\xd8\x1d\xee\xe2\x54\x90\x8e\xd0\x59\xa1\x09" \
    "\x69\x00\xd1\xbc\xe1\x7d\x25\x3e\xfe\x01\x24\xf3" \
    "\x17\xd0\x52\x92\x0a\x10\x05\x21\x0d\x28\x14\x08" \
    "\x28\x10\x4e\x45\x68\x5e\xe2\x74\x9b\x02\x61\x57" \
    "\xdc\x76\x37\xdd\x52\xec\xdd\xe5\xce\x1f\x82\x69" \
    "\xf6\x6e\x76\xf6\x99\x67\x66\x9e\xdd\x16\x4b\xec" \
    "\xed\xc1\xdb\x60\xc4\x60\xad\x6d\xf8\x55\xb5\xb1" \
    "\x66\x3e\x23\xb1\x09\x57\x37\xae\xb6\xea\x71\xed" \
    "\x65\xc0\x46\x0c\xfd\xd5\x7e\x05\x50\x37\x11\xa9" \
    "\xbe\xbd\xf7\xb8\x53\x37\x17\xb3\x14\x18\x60\x7c" \
    "\x32\x9e\x03\x9b\x4d\xa4\xaa\x8d\x44\x7f\x04\xce" \
    "\x35\x9f\x03\xc8\x35\xc7\x88\x69\xec\xab\x2a\x89" \
    "\x4d\xe6\xce\x9f\x5b\x04\xfa\x65\xf4\x25\xd4\x99" \
    "\x88\x08\x22\xd2\x00\x30\x62\x48\x6c\x82\x88\xcc" \
    "\xf5\x77\x29\xe3\x92\x45\xe6\x33\x8c\x98\x3f\xf6" \
    "\x79\x91\x2d\x64\x0c\xb1\xd4\x45\x25\x96\xa0\xb3" \
    "\xea\xf8\x2b\xc6\xcb\x06\x55\x5a\x1d\x74\x19\xf3" \
    "\xb9\xde\x00\xec\xed\xef\x85\x6e\xa7\xcb\x4a\xba" \
    "\xb2\x14\xbc\x1c\xe4\xe8\x70\x14\xc9\x18\xcb\xf6" \
    "\xd6\x66\x85\xd7\x60\xfc\xe1\xe3\x87\xe0\x9c\xe3" \
    "\xf0\xfd\x21\x72\x4d\xaa\x92\x17\xad\xa5\x3a\xfc" \
    "\xd4\x33\xfa\x3c\x62\xe2\x27\xdc\xbb\x7b\x2f\x0c" \
    "\xae\x0d\xd8\x1c\x6c\xb6\x5a\x75\xd0\xf1\xd8\x91" \
    "\xfd\x98\x10\x49\x2e\x66\x0a\x20\x62\x11\x0c\x9c" \
    "\x07\xf7\xc3\xf1\xed\xdb\x11\x93\xe9\x14\xd5\x9c" \
    "\xde\xc5\x2e\x3b\xff\xee\xc4\x56\x94\x4c\x37\x2e" \
    "\x6f\x20\xd6\xc6\xf2\x55\xc9\x67\x11\x35\x07\x0c" \
    "\x87\x8c\xf8\xc8\x01\xeb\xba\x8e\x1d\x5b\x76\x9f" \
    "\xed\xe2\x4e\xe2\xed\x53\x55\xba\x17\x7b\x11\xf4" \
    "\xe9\xee\xf3\xf0\xeb\xe7\xaf\xf0\x37\xf6\x3d\x7c" \
    "\x0f\xbd\xd0\x0b\x12\x24\xf4\x42\x2f\x7c\x3d\xfa" \
    "\x1a\x1e\x3f\x7c\x12\xfa\xab\xfd\x90\xa6\x9d\x60" \
    "\xad\x0d\x9d\xb4\x13\xda\xd9\x24\xe3\xe6\x8d\x2d" \
    "\x8c\x31\x4b\x4b\xaf\x5b\x42\xc2\x15\x2e\x23\x08" \
    "\x03\x06\xac\xf5\xd7\x48\x64\x05\xaf\x13\x76\x5f" \
    "\xbe\xc0\x7b\x8f\x4d\x2d\x6d\x05\xdc\x69\xec\x0f" \
    "\xaa\x20\x42\x54\x50\x4c\x64\x04\x04\x89\x1d\x2f" \
    "\xf6\xef\xeb\x90\xeb\x38\x52\x4d\x39\xe2\x18\x54" \
    "\xb1\x17\x56\xa0\x94\x21\xd0\xf6\xd3\x29\xee\xe4" \
    "\x38\x1e\xcc\x95\x6a\x6e\x52\x00\x51\xe8\x54\x14" \
    "\x54\xaa\x4d\x01\x9c\x4e\x50\x94\x5c\x15\xf7\xff" \
    "\x71\x35\x6e\xa1\x90\x5b\xe9\x38\xc3\xd1\xca\xa9" \
    "\xe8\x59\x8e\xb3\xc8\xea\x5f\x22\x9f\xe6\x8c\x51" \
    "\xda\x08\x68\xd6\x3c\x20\x34\xc5\x16\x13\xd6\x19" \
    "\x97\x26\xa8\x7a\x4a\xfd\x94\x77\x70\x6d\x75\x9d" \
    "\x73\xd4\x59\x56\x64\x0b\xc6\x5a\xac\x33\x6d\x28" \
    "\xa3\x55\x3d\x79\xe9\x11\x83\x02\x69\x9a\xf2\xcf" \
    "\x7f\x37\x23\x63\x77\xea\x8a\x70\x03\x92\x83\x37" \
    "\x40\x06\x62\x0a\xba\x79\xfc\x06\x4c\xc1\xcf\x54" \
    "\x1c\x35\xfe\x69\x8e\x08\x0c\x1f\x0d\xd9\xde\xda" \
    "\x6e\xb5\x3b\xdd\x0e\xee\xcd\x27\x5e\xbf\x3b\x40" \
    "\x8b\x4d\x30\x34\xc4\x27\x52\x95\x49\xf9\x46\x57" \
    "\xcd\xa3\x52\xcb\xf0\xd1\x90\x07\xf7\x1f\xb4\xa0" \
    "\xf6\x08\xed\xed\xef\x85\xfd\x57\x07\x4c\x9c\xab" \
    "\x06\x30\x7b\xb5\xcb\x07\x29\x57\x50\xcd\xa2\xcf" \
    "\x2b\xfd\x4b\x7d\x6e\xdd\xbe\xc5\x9d\x9d\x3b\x15" \
    "\xde\x6f\xf6\x3c\x9e\x4e\x2a\x0d\x25\x44\x00\x00" \
    "\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82"

######################################################

#######################################################

class LSMWindow(QMainWindow):
    def __init__(self,lsm_object,parent = None,name = None,fl = 0):
        QMainWindow.__init__(self,parent,name,fl)
        self.statusBar()

        #self.image0 = QPixmap()  # FILE - New
        #self.image0.loadFromData(image0_data,"PNG")
        self.image1 = QPixmap()
        self.image1.loadFromData(image1_data,"PNG")
        self.image2 = QPixmap()
        self.image2.loadFromData(image2_data,"PNG")
        self.image3 = QPixmap()
        self.image3.loadFromData(image3_data,"PNG")
        if not name:
            self.setName("LSM")

        self.lsm=lsm_object
        self.savefile=None # file to save the LSM
        if self.lsm==None:
          raise NameError, "LSM object not defined"

        self.setCentralWidget(QWidget(self,"qt_central_widget"))
        MainLayout = QVBoxLayout(self.centralWidget(),11,6,"MainLayout")

        self.tabWidget = QTabWidget(self.centralWidget(),"tabWidget")
###################### Tab 1
        self.sourceTab = QWidget(self.tabWidget,"sourceTab")

        # layout for table1
        sourceLayout=QVBoxLayout(self.sourceTab)
        
        self.table1 = QTable(self.sourceTab,"table1")
        self.table1.setGeometry(QRect(-3,7,410,460))
        self.table1.setNumRows(self.lsm.getSources())
        self.table1.setNumCols(self.lsm.getSourceColumns())
        self.table1.horizontalHeader().setLabel(0,self.tr("Source Name"))
        self.table1.horizontalHeader().setLabel(1,self.tr("Template Tree Type"))
        self.table1.horizontalHeader().setLabel(2,self.tr("MeqParm Table"))
        row=0
        for sname in self.lsm.s_table.keys():
         source=self.lsm.s_table[sname]
         self.table1.setText(row,0,QString(source.name))
         self.table1.setText(row,1,QString(source.treeType))
         self.table1.setText(row,2,QString(source.tableName))
         row+=1
        self.table1.adjustColumn(0)
        self.table1.adjustColumn(1)
        self.table1.adjustColumn(2)
        self.table1.setReadOnly(1)
        self.table1.setSorting(0)

        self.tabWidget.insertTab(self.sourceTab,QString.fromLatin1(""))
        sourceLayout.addWidget(self.table1)


##################### Tab 2
        self.punitTab = QWidget(self.tabWidget,"punitTab")

        # layout for table2
        sourceLayout=QVBoxLayout(self.punitTab)

        self.table2 = QTable(self.punitTab,"table2")
        self.table2.setGeometry(QRect(-3,-3,401,471))
        self.table2.setNumRows(self.lsm.getPUnits())
        self.table2.setNumCols(self.lsm.getPUnitColumns())
        self.tabWidget.insertTab(self.punitTab,QString.fromLatin1(""))

        self.table2.horizontalHeader().setLabel(0,self.tr("PUnit Name"))
        self.table2.horizontalHeader().setLabel(1,self.tr("Type"))
        self.table2.horizontalHeader().setLabel(2,self.tr("Source List"))
        self.table2.horizontalHeader().setLabel(3,self.tr("Category"))
        self.table2.horizontalHeader().setLabel(4,self.tr("Brightness"))
        self.table2.horizontalHeader().setLabel(5,self.tr("FOV Distance"))
        self.table2.horizontalHeader().setLabel(6,self.tr("I"))
        self.table2.horizontalHeader().setLabel(7,self.tr("Q"))
        self.table2.horizontalHeader().setLabel(8,self.tr("U"))
        self.table2.horizontalHeader().setLabel(9,self.tr("V"))
        self.table2.horizontalHeader().setLabel(10,self.tr("RA"))
        self.table2.horizontalHeader().setLabel(11,self.tr("Dec"))
        row=0
        # use a hash table to match row number to name
        self.table2_names={}
        for sname in self.lsm.p_table.keys():
         punit=self.lsm.p_table[sname]
         if punit._patch_name==None:
          self.table2.setText(row,0,QString(punit.name))
          mytype=punit.getType()
          if mytype==POINT_TYPE:
           self.table2.setText(row,1,self.tr("Point"))
          else:
           self.table2.setText(row,1,self.tr("Patch"))
          # do not print all the source names in case of a patch
          if mytype==POINT_TYPE:
           self.table2.setText(row,2,QString(str(punit.getSources())))
          else: #patch
           srclist=punit.getSources()
           self.table2.setText(row,2,QString(str(srclist[0])+"...."))

          self.table2.setText(row,3,QString(str(punit.getCat())))
          self.table2.setText(row,4,QString(str(punit.getBrightness())))
          self.table2.setText(row,5,QString(str(punit.getFOVDist())))
         # self.table2.setText(row,6,QString(str(punit.sp.getI())))
         # self.table2.setText(row,7,QString(str(punit.sp.getQ())))
         # self.table2.setText(row,8,QString(str(punit.sp.getU())))
         # self.table2.setText(row,9,QString(str(punit.sp.getV())))
         # self.table2.setText(row,10,QString(str(punit.sp.getRA())))
         # self.table2.setText(row,11,QString(str(punit.sp.getDec())))
          self.table2.setText(row,6,QString("MeqTree"))
          self.table2.setText(row,7,QString("MeqTree"))
          self.table2.setText(row,8,QString("MeqTree"))
          self.table2.setText(row,9,QString("MeqTree"))
          self.table2.setText(row,10,QString("MeqTree"))
          self.table2.setText(row,11,QString("MeqTree"))
          # rememeber the name
          self.table2_names[sname]=row
          row+=1
         else:
          print "This belongs to a patch"

        for i in range(self.table2.numCols()):
         self.table2.adjustColumn(i)
        sourceLayout.addWidget(self.table2)
        self.table2.setSorting(0)
        self.table2.setReadOnly(1)
####### Tab 3 ############################
        self.imageTab= QWidget(self.tabWidget,"imageTab")
        sourceLayout=QVBoxLayout(self.imageTab)
        self.canvas=QCanvas(500,500)

        self.xlabel=QLabel(self.imageTab,"xlabel")
        self.xlabel.setText("0.0000000")
        self.xlabel.setMinimumWidth(self.xlabel.sizeHint().width())
        self.ylabel=QLabel(self.imageTab,"ylabel")
        self.ylabel.setText("0.0000000")
        self.ylabel.setMinimumWidth(self.ylabel.sizeHint().width())
        self.zlabel=QLabel(self.imageTab,"zlabel")
        self.zlabel.setText("f=000000000 T=0000000000")
        self.zlabel.setMinimumWidth(self.zlabel.sizeHint().width())
        self.sliderLabel= QLabel(self.imageTab,"slider")
        self.sliderLabel.setText("0.000")

        self.cview=MyCanvasView(self.canvas,self.imageTab,"canvas",self.xlabel,\
         self.ylabel,self.zlabel,self.sliderLabel,self.lsm,self)
        sourceLayout.addWidget(self.cview)

        layout1 = QHBoxLayout(None,0,6,"layout1")
        layout1.addWidget(self.xlabel)
        layout1.addWidget(self.ylabel)
        layout1.addWidget(self.zlabel)

        spacer1 = QSpacerItem(11,11,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout1.addItem(spacer1)

        layout2 = QVBoxLayout(None,0,6,"layout2")
        layout2.addWidget(self.sliderLabel)

        self.sliderCut = QSlider(0,100,1,0, QSlider.Horizontal,self.imageTab,"sliderCut")
        self.connect( self.sliderCut, SIGNAL("valueChanged( int )"), 
           self.cview.display)

        layout2.addWidget(self.sliderCut)

        layout1.addLayout(layout2)
        sourceLayout.addLayout(layout1)

        self.tabWidget.insertTab(self.imageTab,QString.fromLatin1(""))
        # show the image by default
        self.tabWidget.setCurrentPage(2)
######## End of Tabs #####################

        MainLayout.addWidget(self.tabWidget)

        self.fileOpenAction = QAction(self,"fileOpenAction")
        self.fileOpenAction.setIconSet(QIconSet(self.image1))
        self.fileSaveAction = QAction(self,"fileSaveAction")
        self.fileSaveAction.setIconSet(QIconSet(self.image2))
        self.fileSaveAsAction = QAction(self,"fileSaveAsAction")
        self.filePrintAction = QAction(self,"filePrintAction")
        self.filePrintAction.setIconSet(QIconSet(self.image3))
        self.filePrintEPSAction = QAction(self,"filePrintEPSAction")
        self.filePrintEPSAction.setIconSet(QIconSet(self.image3))
        self.helpAboutAction = QAction(self,"helpAboutAction")
        self.viewZoom_WindowAction = QAction(self,"viewZoom_WindowAction")
        self.viewZoom_AllAction = QAction(self,"viewZoom_AllAction")
        self.viewZoom_CancelAction = QAction(self,"viewZoom_CancelAction")
        self.view_selectAction = QAction(self,"view_selectAction")
        self.viewZoom_OptionsAction = QAction(self,"viewZoom_OptionsAction")
        self.view_nextAction= QAction(self,"view_nextAction")




        self.MenuBar = QMenuBar(self,"MenuBar")


        self.fileMenu = QPopupMenu(self)
        self.fileOpenAction.addTo(self.fileMenu)
        self.fileSaveAction.addTo(self.fileMenu)
        self.fileSaveAsAction.addTo(self.fileMenu)
        self.fileMenu.insertSeparator()
        self.filePrintAction.addTo(self.fileMenu)
        self.filePrintEPSAction.addTo(self.fileMenu)
        self.fileMenu.insertSeparator()
        self.fileMenu.insertItem('&Quit',qApp,SLOT('closeAllWindows()'),Qt.CTRL + Qt.Key_Q)

        self.MenuBar.insertItem(QString(""),self.fileMenu,1)

        self.viewMenu = QPopupMenu(self)
        self.viewZoom_WindowAction.addTo(self.viewMenu)
        self.viewZoom_AllAction.addTo(self.viewMenu)
        self.viewZoom_CancelAction.addTo(self.viewMenu)
        self.view_selectAction.addTo(self.viewMenu)
        self.viewMenu.insertSeparator()
        self.viewZoom_OptionsAction.addTo(self.viewMenu)
        self.viewMenu.insertSeparator()
        self.view_nextAction.addTo(self.viewMenu)
        self.MenuBar.insertItem(QString(""),self.viewMenu,2)

        self.MenuBar.insertSeparator(3)

        self.helpMenu = QPopupMenu(self)
        self.helpAboutAction.addTo(self.helpMenu)
        self.MenuBar.insertItem(QString(""),self.helpMenu,4)


        self.languageChange()

        self.resize(QSize(530,670).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.fileOpenAction,SIGNAL("activated()"),self.fileOpen)
        self.connect(self.fileSaveAction,SIGNAL("activated()"),self.fileSave)
        self.connect(self.fileSaveAsAction,SIGNAL("activated()"),self.fileSaveAs)
        self.connect(self.filePrintAction,SIGNAL("activated()"),self.filePrint)
        self.connect(self.filePrintEPSAction,SIGNAL("activated()"),self.filePrintEPS)

        self.connect(self.viewZoom_WindowAction,SIGNAL("activated()"),self.zoomStart)
        self.connect(self.viewZoom_AllAction,SIGNAL("activated()"),self.zoomAll)
        self.connect(self.viewZoom_CancelAction,SIGNAL("activated()"),self.zoomCancel)
        self.connect(self.viewZoom_OptionsAction,SIGNAL("activated()"),self.changeOptions)
        self.connect(self.view_nextAction,SIGNAL("activated()"),self.viewNextMode)
        self.connect(self.view_selectAction,SIGNAL("activated()"),self.viewSelectWindow)

        self.connect(self.helpAboutAction,SIGNAL("activated()"),self.helpAbout)


    def languageChange(self):
        self.setCaption(self.__tr("LSMWindow"))
        self.tabWidget.changeTab(self.sourceTab,self.__tr("Source Table"))
        self.tabWidget.changeTab(self.punitTab,self.__tr("P-Unit Table"))
        self.tabWidget.changeTab(self.imageTab,self.__tr("Image"))
        self.fileOpenAction.setText(self.__tr("Open"))
        self.fileOpenAction.setMenuText(self.__tr("&Open..."))
        self.fileOpenAction.setAccel(self.__tr("Ctrl+O"))
        self.fileSaveAction.setText(self.__tr("Save"))
        self.fileSaveAction.setMenuText(self.__tr("&Save"))
        self.fileSaveAction.setAccel(self.__tr("Ctrl+S"))
        self.fileSaveAsAction.setText(self.__tr("Save As"))
        self.fileSaveAsAction.setMenuText(self.__tr("Save &As..."))
        self.fileSaveAsAction.setAccel(QString.null)
        self.filePrintAction.setText(self.__tr("Print"))
        self.filePrintAction.setMenuText(self.__tr("&Print..."))
        self.filePrintAction.setAccel(self.__tr("Ctrl+P"))
        self.filePrintEPSAction.setText(self.__tr("Print EPS"))
        self.filePrintEPSAction.setMenuText(self.__tr("Print &EPS..."))
        self.filePrintEPSAction.setAccel(self.__tr("Ctrl+E"))
        self.helpAboutAction.setText(self.__tr("About"))
        self.helpAboutAction.setMenuText(self.__tr("&About"))
        self.helpAboutAction.setAccel(QString.null)
        self.viewZoom_WindowAction.setText(self.__tr("Zoom Window"))
        self.viewZoom_WindowAction.setMenuText(self.__tr("&Zoom Window"))
        self.viewZoom_WindowAction.setAccel(self.__tr("Ctrl+Z"))
        self.viewZoom_AllAction.setText(self.__tr("Zoom All"))
        self.viewZoom_AllAction.setMenuText(self.__tr("Zoom &All"))
        self.viewZoom_AllAction.setAccel(self.__tr("Ctrl+A"))
        self.viewZoom_CancelAction.setText(self.__tr("Zoom Cancel"))
        self.viewZoom_CancelAction.setMenuText(self.__tr("Zoom &Cancel"))
        self.viewZoom_CancelAction.setAccel(self.__tr("Ctrl+C"))
        self.viewZoom_OptionsAction.setText(self.__tr("Change Options for Plotting"))
        self.viewZoom_OptionsAction.setMenuText(self.__tr("Change &Options"))
        self.viewZoom_OptionsAction.setAccel(self.__tr("Ctrl+O"))
        self.view_selectAction.setText(self.__tr("Select"))
        self.view_selectAction.setMenuText(self.__tr("Select &Window"))
        self.view_selectAction.setAccel(self.__tr("Ctrl+W"))
        self.view_nextAction.setText(self.__tr("Next"))
        self.view_nextAction.setMenuText(self.__tr("Next &Mode"))
        self.view_nextAction.setAccel(self.__tr("Ctrl+N"))

        if self.MenuBar.findItem(1):
            self.MenuBar.findItem(1).setText(self.__tr("&File"))
        if self.MenuBar.findItem(2):
            self.MenuBar.findItem(2).setText(self.__tr("&View"))
        if self.MenuBar.findItem(4):
            self.MenuBar.findItem(4).setText(self.__tr("&Help"))



    def fileOpen(self):
        s=QFileDialog.getOpenFileName(".","*.*",self,"Open File","Choose LSM File to Load")
        #ry:
        self.lsm.load(s.ascii())
        #except Exception:
        print "file %s is not a valid LSM file" % s.ascii()

    def fileSave(self):
        if self.savefile==None:
         s=QFileDialog.getSaveFileName(".","*.*",self,"Save File","Choose File Name to Save LSM")
         self.savefile=s.ascii()
        try:
         self.lsm.save(self.savefile)
        except Exception:
         print "Error saving to file %s" % self.savefile


    def fileSaveAs(self):
        s=QFileDialog.getSaveFileName(".","*.*",self,"Save File","Choose File Name to Save LSM")
        self.savefile=s.ascii()
        try:
         self.lsm.save(self.savefile)
        except Exception:
         print "Error saving to file %s" % self.savefile


    def filePrint(self):
        if not self.cview.printer:
            self.cview.printer = QPrinter()
        if  self.cview.printer.setup(self.cview):
            pp=QPainter(self.cview.printer)
            self.canvas.drawArea(QRect(0,0,self.canvas.width(),self.canvas.height()),pp,False)
            pp.end()
            if pp.isActive():
              pp.flush()

    # print to EPS
    def filePrintEPS(self):
      filename='./print.eps'
      # write EPS
      if not self.cview.printer:
       self.cview.printer = QPrinter()
      self.cview.printer.setColorMode(QPrinter.Color)
      self.cview.printer.setOrientation(QPrinter.Portrait)
      self.cview.printer.setOutputToFile(True)
      self.cview.printer.setOutputFileName(filename)
      self.cview.printer.setPageSize(QPrinter.A4)
      if  self.cview.printer.setup(self.cview):
       pp=QPainter(self.cview.printer)
       self.canvas.drawArea(QRect(0,0,self.canvas.width(),self.canvas.height()),pp,False)
       pp.end()
       if pp.isActive():
        pp.flush()
       if self.cview.printer.outputToFile():
         self.filePStoEPS(self.cview.printer.outputFileName().ascii())

       self.filePStoEPS(filename)
            
    # convert a PS file to an EPS file by changing the 
    # bounding box
    def filePStoEPS(self,filename):
     fn=QFile(filename)   
     if not fn.open( IO_ReadOnly ):
      print "Print EPS: file not readable"
      return
     ts = QTextStream( fn )
     
     fileContent=QString()
     while not ts.atEnd():
       fileContent.append(ts.read())
    
     fn.close()
     rx=QRegExp("%%BoundingBox:\\s*(-?[\\d\\.]+)\\s*(-?[\\d\\.]+)\\s*(-?[\\d\\.]+)\\s*(-?[\\d\\.]+)")
     pos = rx.search(fileContent)
     left = rx.cap(1).toFloat()
     top = rx.cap(4).toFloat()
     # parsed [left,bottom] [right,top]
     # replace  the margins
     # note padding is arbitrary
     padding=100 
     newstr="%%BoundingBox: "+str(left[0])+" "+str(top[0]-(self.canvas.height()-padding))+" "+str(left[0]+self.canvas.width()-padding)+" "+str(top[0])
     print "Writing "+newstr
     fileContent.replace(pos,rx.cap(0).length(),QString(newstr))
     #print "File modified",fileContent.ascii()

     newfilename=filename
     try:
       f = open(newfilename,'w+')
     except:
      print "Print EPS: file not writable"
      return

     f.write(fileContent.ascii())
     f.close()


    def zoomStart(self):
       self.cview.zoom_status=GUI_ZOOM_WINDOW

    def zoomAll(self):
       # no Zooming if image tab is not seen
       if self.tabWidget.currentPageIndex() == 2:
        if (self.cview.tmstack) != None:
         m = self.cview.tmstack
         m *=self.cview.worldMatrix()
         self.cview.setWorldMatrix( m )

    def zoomCancel(self):
      self.cview.zoom_status=GUI_ZOOM_NONE
 
    def helpAbout(self):
        QMessageBox.information(None, "LSM Browser",
            "<h3>LSM Browser</h3><hr>"
            "<p>$Date$"
            ".</p>"
            ,"Dismiss")

    def changeOptions(self):
     win=OptionsDialog(self)
     win.show()

    def viewNextMode(self):
      win=FTDialog(self,f0=self.lsm.cells.grid.freq[self.lsm.cells.segments.freq.start_index],\
       f1=self.lsm.cells.grid.freq[self.lsm.cells.segments.freq.end_index],\
       fticks=self.lsm.cells.segments.freq.end_index,\
        f=self.cview.default_freq_index,\
        t0=self.lsm.cells.grid.time[self.lsm.cells.segments.time.start_index],\
       t1=self.lsm.cells.grid.time[self.lsm.cells.segments.time.end_index],\
       tticks=self.lsm.cells.segments.time.end_index,\
        t=self.cview.default_time_index)
      win.show()

    def viewSelectWindow(self):
      self.cview.zoom_status=GUI_SELECT_WINDOW

    # remove rows from PUnit table (table2)
    # with given name
    def removePUnitRows(self,pname_list):
        # create a list of row numbers corresponding
        # to the given names
        row_list=[]
        for pname in pname_list:
         if self.table2_names.has_key(pname):
          row_list.append(self.table2_names[pname])
        row_list.sort()
 
        # remove these rows
        if len(row_list)>0:
         self.table2.removeRows(row_list)
         # recreate name map
         self.table2_names={} 
         for ci in range(self.table2.numRows()):
          self.table2_names[self.table2.text(ci,0).ascii()]=ci



    # remove one row from PUnit table (table2)
    # with given name
    def removePUnitRow(self,pname):
        if self.table2_names.has_key(pname):
         self.table2.removeRow(self.table2_names[pname])
         # recreate name map
         self.table2_names={} 
         for ci in range(self.table2.numRows()):
           self.table2_names[self.table2.text(ci,0).ascii()]=ci

    # insert row to PUnit table (table2)
    # with given name
    def insertPUnitRow(self,pname):
        if self.table2_names.has_key(pname):
          print "Key alreay exits"
        else:
         punit=self.lsm.p_table[pname]
         if punit._patch_name==None:
          row=self.table2.numRows()
          self.table2.insertRows(row,1)
          self.table2.setText(row,0,QString(punit.name))
          mytype=punit.getType()
          if mytype==POINT_TYPE:
           self.table2.setText(row,1,self.tr("Point"))
          else:
           self.table2.setText(row,1,self.tr("Patch"))
          # do not print all the source names in case of a patch
          if mytype==POINT_TYPE:
           self.table2.setText(row,2,QString(str(punit.getSources())))
          else: #patch
           srclist=punit.getSources()
           self.table2.setText(row,2,QString(str(srclist[0])+"...."))

          self.table2.setText(row,3,QString(str(punit.getCat())))
          self.table2.setText(row,4,QString(str(punit.getBrightness())))
          self.table2.setText(row,5,QString(str(punit.getFOVDist())))
          self.table2.setText(row,6,QString("MeqTree"))
          self.table2.setText(row,7,QString("MeqTree"))
          self.table2.setText(row,8,QString("MeqTree"))
          self.table2.setText(row,9,QString("MeqTree"))
          self.table2.setText(row,10,QString("MeqTree"))
          self.table2.setText(row,11,QString("MeqTree"))
          # rememeber the name
          self.table2_names[pname]=row



    def __tr(self,s,c = None):
        return qApp.translate("LSMWindow",s,c)

##########################################################################

