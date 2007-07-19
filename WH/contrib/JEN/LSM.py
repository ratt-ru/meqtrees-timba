# LSM.py


#!/usr/bin/python

# import modules for visualization
#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
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
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import sys
from qt import *
from qttable import QTable
from qtcanvas import *

#############################################
class Source:
 """Source object in source table
 Attributes are
 name=Source name - String
 treeType=type of Template tree - string
 tableName=MeqParm table Name - string"""

 # Constructor
 def __init__(self,name,treeType='Point1',tableName='Table1'):
   # Check source name to be a string
   if type(name) != type(""):
    raise TypeError,"Name must be a string, not %s"  % type(name).__name__
   self.name=name
   self.treeType=treeType
   self.tableName=tableName

 # set template tree type
 def setTemplateTree(self,treeType):
   self.treeType=treeType
 
 # Print
 def __str__(self):
   temp_str="Source name: "+self.name
   temp_str+=" Template tree: "+self.treeType
   temp_str+=" MeqParm Table: "+self.tableName
   return temp_str
###############################################
class SixPack:
 """the sextuple: Stokes I,Q,U,V, and RA, Dec
 """
 
 # Constructor
 def __init__(self,sI,sQ,sU,sV,RA,Dec):
  self.sI=sI
  self.sQ=sQ
  self.sU=sU
  self.sV=sV
  self.RA=RA
  self.Dec=Dec

 # traditional getter and setter methods
 # for the moment, assume IQUV are numerical values.
 # but once template trees are in place, the request/response
 # methods will be used
 def setI(self,I):
  self.sI=I
 def getI(self):
  return self.sI
 def setQ(self,Q):
  self.sQ=Q
 def getQ(self):
  return self.sQ
 def setU(self,U):
  self.sU=U
 def getU(self):
  return self.sU
 def setV(self,V):
  self.sV=V
 def getV(self):
  return self.sV
 def setRA(self,RA):
  self.RA=RA
 def getRA(self):
  return self.RA
 def setDec(self,Dec):
  self.Dec=Dec 
 def getDec(self):
  return self.Dec

 # method to calculate (l,m) from RA,Dec ?

 # Print
 def __str__(self):
   temp_str="SixPack: {I="+str(self.getI())
   temp_str+=",Q="+str(self.getQ())
   temp_str+=",U="+str(self.getU())
   temp_str+=",V="+str(self.getV())
   temp_str+=",RA="+str(self.getRA())
   temp_str+=",Dec="+str(self.getDec())
   temp_str+="}"
   return temp_str

###############################################
class TemTree:
 """Template tree object"""
 
 # Constructor
 def __init__(self,id):
  self.id=id 

###############################################
class PUnit:
 """p-Unit object 
 Attributes are
  name: will be a unique string like "3C48" or "patch#23". Note source 
    names are also stored in source table.
  type: point soure/ patch - integer, 0 - point soure, 1 - patch
  s_list: source list - list of sources in the source table
  cat1: 1 - source is Cat.I, 0 - not Cat.I
  app_brightness: apparent brightness - used in sorting and peeling
  sp: the sextuple SixPack object:
   {sI: sQ: sU: sV: RA: Dec: }
  FOV_distance: relative OBSWIN size
  """
 # Constructor
 def __init__(self,name):
  # p-Unit name has to be a string
  if type(name) != type(""):
    raise TypeError,"Name must be a string, not %s"  % type(name).__name__
  self.name=name
  self.type=0
  self.s_list=[]
  self.cat1=1
  self.app_brightness=1
  self.sp=SixPack(0,0,0,0,0,0)
  self.FOV_distance=0
 
 # change type (point: flag=0, patch: flag=1)
 def setType(self,flag):
  self.type=flag
 # return type
 def getType(self):
  return self.type
  
 # add a source to the source list, s = source name
 def addSource(self,s):
  self.s_list.append(s)
 # return the source list
 def getSources(self):
  return self.s_list
 
 # change Cat.I switch flag=0/1
 def setCatI(self,flag):
  self.cat1=flag
 # return cat.I
 def getCatI(self):
  return self.cat1

 # change apparent brightness
 def setBrightness(self,brightness):
  self.app_brightness=brightness
 def getBrightness(self):
  return self.app_brightness

 # change FOV distance
 def setFOVDist(self,distance):
  self.FOV_distance=distance
 def getFOVDist(self):
  return self.FOV_distance

 # Print
 def __str__(self):
   temp_str="P-Unit: | Name="+str(self.name)
   temp_str+=", type="+str(self.type)
   temp_str+=",source_list="+str(self.s_list)
   temp_str+=",catI="+str(self.cat1)
   temp_str+=",Brightness="+str(self.getBrightness())
   temp_str+=",sp="+str(self.sp)
   temp_str+=",FOV="+str(self.FOV_distance)
   temp_str+=" |"
   return temp_str



###############################################
class LSM:
 """LSM Object:
 Attributes are
  s_table: Source table
  m_table: MeqParm table
  tmpl_table: Template tree table
  p_table: p-Unit table

  helper attributes:
  __barr: array of p-Units sorted by brightness - private attribute
 """
 # Constructor
 # Does pretty much nothing so far
 def __init__(self):
  self.s_table={}
  self.m_table={}
  self.tmpl_table={}
  self.p_table={}
  self.__barr=[] 



 # Much more important method
 # Inserts a source to source table
 def insertSource(self,s, **kw):
  """This will insert source s to stable,
    and search the MeqParm table for the params of the source
    (using the source name). Then will add relevent params from
    the mtable (row numbers) to the source param list
    Arguments:
    s: Source object
    **kw=variable list of keyword arguments such as
     brightness=10
     type='point' / 'patch'
     sI=1.00
     sQ=10
     sU=100
     sV=100
     RA=100
     Dec=100
  """ 
  # Source names have to be unique
  if self.s_table.has_key(s.name):
   # Print error
   raise NameError, 'Source '+s.name+' is already present'
  self.s_table[s.name]=s
  """ After inserting the source to source table,
      search the  MeqParm table if it has any parms of the source.
     Add these params to the source param list."""

  """Now create a p-unit object for this (point) source.
      the p-unit object will link to the template trees.
      Note that p-unit table has to be sorted by brightness.
      so the insertion has to done in a sorted way.
  """
  # Use the p-unit name to be the source name (point source) 
  p=PUnit(s.name)
  # add the source to the source list of the p-unit
  p.addSource(s.name)
  
  # all other p-Unit parameters are given be key-word argument list
  if kw.has_key('brightness'):
   p.setBrightness(kw['brightness'])
  else:
   p.setBrightness(0)

  if kw.has_key('type'):
   if kw['type']=='point':
    p.setType(0) # 0 - point source
  else:
   p.setType(1) # 1 - patch
 
  if kw.has_key('sI'):
   p.sp.setI(kw['sI'])
  if kw.has_key('sQ'):
   p.sp.setQ(kw['sQ'])
  if kw.has_key('sU'):
   p.sp.setU(kw['sU'])
  if kw.has_key('sV'):
   p.sp.setV(kw['sV'])
  if kw.has_key('RA'):
   p.sp.setRA(kw['RA'])
  if kw.has_key('Dec'):
   p.sp.setDec(kw['Dec'])

  # finally, insert p-Unit to p-Unit table
  self.insertPUnit(p)

 # Helper method 
 # inserts a p-unit into the p-Unit table, and 
 # orders according to the brightness
 def insertPUnit(self,p):
  if self.p_table.has_key(p.name):
   raise NameError, 'PUnit '+p.name+' is already present'
  else:
   self.p_table[p.name]=p
  # now do the sorting of the brightness array
  tmp_brightness=p.getBrightness() 
  if (len(self.__barr)==0):
   self.__barr.insert(0,p.name)
  else: # list is not empty
   for i in range(len(self.__barr)):
    if self.p_table[self.__barr[i]].getBrightness() < tmp_brightness:
     #print "DEBUG compare %f with %f " % (self.p_table[self.__barr[i]].getBrightness() , tmp_brightness)
     break


   # special check for end of list
   if i==0: 
    if self.p_table[self.__barr[i]].getBrightness() < tmp_brightness:
      self.__barr.insert(0,p.name)
    else:
      self.__barr.append(p.name)
   elif i==len(self.__barr)-1:
    if self.p_table[self.__barr[i]].getBrightness() < tmp_brightness:
     self.__barr.insert(i,p.name)
    else:
     self.__barr.append(p.name)
   else:
    self.__barr.insert(i,p.name)
  #print self.__barr

 # method for printing to screen
 def dump(self):
  print "---------------------------------"
  print "Source Table:"
  for s in self.s_table.keys():
   print self.s_table[s]
  print "\n\n"
  print "P-Unit Table:\n"
  for p in self.p_table.keys():
   print self.p_table[p]
  print "\n\n"

  print "P-Units sorted in Brightness:\n"
  for p in self.__barr:
   print p, self.p_table[p].getBrightness()

  print "---------------------------------"



 # method for visualization
 def display(self):
  d=Dummy(self,sys.argv)
  d.display()



 # return number of sources
 def getSources(self):
  return len(self.s_table)
 # return no of columes in source table
 def getSourceColumns(self):
  return 3
 # return number of p-Units in the p-Unit table 
 def getPUnits(self):
  return len(self.p_table)
 # return no of columes in p-Unit table
 def getPUnitColumns(self):
  return 12
 # return max,min values of RA and Dec
 def getBounds(self):
  max_RA=-100
  min_RA=100
  max_Dec=-100
  min_Dec=100

  for p in self.p_table.keys():
   punit=self.p_table[p]
   tmpval=punit.sp.getRA()
   if tmpval > max_RA:
    max_RA=tmpval
   if tmpval <  min_RA:
    min_RA=tmpval
   tmpval=punit.sp.getDec()
   if tmpval > max_Dec:
    max_Dec=tmpval
   if tmpval <  min_Dec:
    min_Dec=tmpval
  result={}
  result['min_RA']=min_RA 
  result['max_RA']=max_RA 
  result['min_Dec']=min_Dec
  result['max_Dec']=max_Dec

  return result

 # return max value of brightness (min value is 0)
 def getMaxBrightness(self):
   if len(self.__barr)==0:
    return 0
   pname=self.__barr[0]
   return self.p_table[pname].getBrightness()



######################################################
######################################################
# Helper classes and methods for the GUI
#Singleton Class to make sure there is only one 
# instance of QApplication class
class Singleton:
  __single=None
  app=None # both these are class attributes, not instance attributes
  def __init__(self,args):
   if Singleton.__single:
     raise Singleton.__single
   Singleton.__single=self
   Singleton.app=QApplication(args)

def Handle(args,x=Singleton):
 try:
  single=x(args)
 except Singleton,s:
  single=s
 return single.app

class Dummy:
    def __init__(self,lsm_object,args):
     self.lsm=lsm_object
     self.myargs=args
     self.app=None
     self.win=None
    def display(self):
     self.app=Handle(self.myargs)
     self.win=LSMWindow(self.lsm) 
     self.win.show()
     self.app.connect(self.app,SIGNAL("lastWindowClosed()"),
        self.app, SLOT("quit()"))
     self.app.exec_loop()


#######################################################
#######################################################
# Window class
class LSMWindow(QDialog):
    def __init__(self,lsm_object,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)
        if not name:
            self.setName("LSM")
        self.lsm=lsm_object
        if self.lsm==None:
          raise NameError, "LSM object not defined"

        self.setSizeGripEnabled(1)

        MyLSMWinLayout = QVBoxLayout(self,11,6,"MyLSMWinLayout")

        self.tabWidget = QTabWidget(self,"tabWidget")

#### Tab 1 #########################
        self.sourceTab = QWidget(self.tabWidget,"sourceTab")

        # layout for table1
        sourceLayout=QVBoxLayout(self.sourceTab)
        
        self.table1 = QTable(self.sourceTab,"table1")
        self.table1.setGeometry(QRect(-3,7,510,260))
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

        self.tabWidget.insertTab(self.sourceTab,QString.fromLatin1(""))
        sourceLayout.addWidget(self.table1)

##### Tab 2 ########################
        self.punitTab= QWidget(self.tabWidget,"punitTab")

        # layout for table2
        sourceLayout=QVBoxLayout(self.punitTab)

        self.table2 = QTable(self.punitTab,"table2")
        self.table2.setGeometry(QRect(-3,-3,501,271))
        self.table2.setNumRows(self.lsm.getPUnits())
        self.table2.setNumCols(self.lsm.getPUnitColumns())
        self.tabWidget.insertTab(self.punitTab,QString.fromLatin1(""))

        self.table2.horizontalHeader().setLabel(0,self.tr("PUnit Name"))
        self.table2.horizontalHeader().setLabel(1,self.tr("Type"))
        self.table2.horizontalHeader().setLabel(2,self.tr("Source List"))
        self.table2.horizontalHeader().setLabel(3,self.tr("Cat. I"))
        self.table2.horizontalHeader().setLabel(4,self.tr("Brightness"))
        self.table2.horizontalHeader().setLabel(5,self.tr("FOV Distance"))
        self.table2.horizontalHeader().setLabel(6,self.tr("I"))
        self.table2.horizontalHeader().setLabel(7,self.tr("Q"))
        self.table2.horizontalHeader().setLabel(8,self.tr("U"))
        self.table2.horizontalHeader().setLabel(9,self.tr("V"))
        self.table2.horizontalHeader().setLabel(10,self.tr("RA"))
        self.table2.horizontalHeader().setLabel(11,self.tr("Dec"))
        row=0
        for sname in self.lsm.p_table.keys():
         punit=self.lsm.p_table[sname]
         self.table2.setText(row,0,QString(punit.name))
         self.table2.setText(row,1,QString(str(punit.getType())))
         self.table2.setText(row,2,QString(str(punit.getSources())))
         self.table2.setText(row,3,QString(str(punit.getCatI())))
         self.table2.setText(row,4,QString(str(punit.getBrightness())))
         self.table2.setText(row,5,QString(str(punit.getFOVDist())))
         self.table2.setText(row,6,QString(str(punit.sp.getI())))
         self.table2.setText(row,7,QString(str(punit.sp.getQ())))
         self.table2.setText(row,8,QString(str(punit.sp.getU())))
         self.table2.setText(row,9,QString(str(punit.sp.getV())))
         self.table2.setText(row,10,QString(str(punit.sp.getRA())))
         self.table2.setText(row,11,QString(str(punit.sp.getDec())))
         row+=1
        for i in range(self.table2.numCols()):
         self.table2.adjustColumn(i)
        sourceLayout.addWidget(self.table2)

####### Tab 3 ############################
        self.imageTab= QWidget(self.tabWidget,"imageTab")
        sourceLayout=QVBoxLayout(self.imageTab)
        self.canvas=QCanvas(400,400)
        # to-do use TextEdit class in future
        self.clabel=QLabel(self.imageTab,"clabel")
        self.cview=MyCanvasView(self.canvas,self.imageTab,"canvas",self.clabel,self.lsm)
        sourceLayout.addWidget(self.cview)
        sourceLayout.addWidget(self.clabel)
        self.tabWidget.insertTab(self.imageTab,QString.fromLatin1(""))

######## End of Tabs #####################
        MyLSMWinLayout.addWidget(self.tabWidget)

        Layout1 = QHBoxLayout(None,0,6,"Layout1")

        self.buttonHelp = QPushButton(self,"buttonHelp")
        self.buttonHelp.setAutoDefault(1)
        Layout1.addWidget(self.buttonHelp)
        Horizontal_Spacing2 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        Layout1.addItem(Horizontal_Spacing2)

        self.buttonOk = QPushButton(self,"buttonOk")
        self.buttonOk.setAutoDefault(1)
        self.buttonOk.setDefault(1)
        Layout1.addWidget(self.buttonOk)

        self.buttonCancel = QPushButton(self,"buttonCancel")
        self.buttonCancel.setAutoDefault(1)
        Layout1.addWidget(self.buttonCancel)
        MyLSMWinLayout.addLayout(Layout1)

        self.languageChange()

        self.resize(QSize(528,368).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.buttonOk,SIGNAL("clicked()"),self.accept)
        self.connect(self.buttonCancel,SIGNAL("clicked()"),self.reject)


    def languageChange(self):
        self.setCaption(self.__tr("LSM"))
        self.tabWidget.changeTab(self.sourceTab,self.__tr("Source Table"))
        self.tabWidget.changeTab(self.punitTab,self.__tr("P-Unit Table"))
        self.tabWidget.changeTab(self.imageTab,self.__tr("Image"))
        self.buttonHelp.setText(self.__tr("&Help"))
        self.buttonHelp.setAccel(self.__tr("F1"))
        self.buttonOk.setText(self.__tr("&OK"))
        self.buttonOk.setAccel(QString.null)
        self.buttonCancel.setText(self.__tr("&Cancel"))
        self.buttonCancel.setAccel(QString.null)


    def __tr(self,s,c = None):
        return qApp.translate("LSM",s,c)

##########################################################################
##########################################################################

# define constants for RTTI values of special canvasview objects
POINT_SOURCE_RTTI=1001

class MyCanvasView(QCanvasView):
  def __init__(self,canvas,parent,name,label,lsm_object):
    QCanvasView.__init__(self,canvas,parent,name)
    self.lsm=lsm_object
    self.label=label
    self.canvas().setDoubleBuffering(True) 
    self.viewport().setMouseTracking(1) 
    self.max_brightness=self.lsm.getMaxBrightness()
    bounds=self.lsm.getBounds()
    # add a small boundary
    self.x_min=bounds['min_RA']-0.01
    self.x_max=bounds['max_RA']+0.01
    self.y_min=bounds['min_Dec']-0.01
    self.y_max=bounds['max_Dec']+0.01
    H=self.canvas().height()
    W=self.canvas().width()
    self.x_scale=W/(self.x_max-self.x_min)
    self.y_scale=H/(self.y_max-self.y_min)
    # plot all p-units/sources
    for sname in self.lsm.p_table.keys():
     punit=self.lsm.p_table[sname]
     xys=self.globalToLocal(punit.sp.getRA(),punit.sp.getDec())
     self.addCircle(xys[0],xys[1],5,self.getColor(punit.getBrightness()),punit.name,punit.getBrightness())
    # create too tip
    self.tooltip=DynamicTip(self)
   
  def contentsMouseMoveEvent(self,e):
    point = self.inverseWorldMatrix().map(e.pos())
    xys=self.localToGlobal(point.x(),point.y())
    self.label.setText("[<font color=\"blue\">"+str(xys[0])+" "+str(xys[1])+" </font>]")
    self.canvas().update()

  def contentsMousePressEvent(self,e):
   point = self.inverseWorldMatrix().map(e.pos())
   ilist = self.canvas().collisions(point) #QCanvasItemList ilist
   for each_item in ilist:
     if each_item.rtti()==POINT_SOURCE_RTTI:
      print each_item.name
   return


  def addCircle(self,center_x,center_y,radius,color,name,z_value):
   i = Circle(center_x,center_y,radius,color,name,self.canvas())
   i.setZ(z_value)
   i.show()

  # return local coordinates for given global coordinates
  def localToGlobal(self,x,y):
   l=[x/self.x_scale+self.x_min,-y/self.y_scale+self.y_max]
   return l
  # return global coordinates for given local coordinates
  def globalToLocal(self,x,y):
   l=[(x-self.x_min)*self.x_scale,(self.y_max-y)*self.y_scale]
   return l

  # return a colour according to brightness
  def getColor(self,z):
    cl=z/self.max_brightness # normalized in [0,1] 
    if cl < 0.25:
     return QColor(0,int(cl*256*4),255)
    elif cl < 0.5:
     return QColor(0,255,int((2-cl*4)*256))
    elif cl < 0.75:
     return QColor(int((4*cl-2)*256),255,0)
    else:
     return QColor(255,int((4-4*cl)*256),0)

  # if at the point there is something, return it
  def anythingToTip(self,pos):
   point = self.inverseWorldMatrix().map(self.viewportToContents(pos))
   ilist = self.canvas().collisions(point) #QCanvasItemList ilist
   if len(ilist)==0:
    return [None,None]
   for each_item in ilist:
     tmp_str=""
     if each_item.rtti()==POINT_SOURCE_RTTI:
      tmp_str+=each_item.name+" "
   cr=QRect(self.contentsToViewport(point),QSize(len(tmp_str),2))
   return [cr,tmp_str]

   # Explicitly delete the tooltip
   def __del__(self):
     del self.tooltip
     self.tooltip=None

# class for drawing point (and elliptic - extended) sources
class Circle(QCanvasEllipse):
  def __init__(self,center_x,center_y,radius,color,name,canvas):
    QCanvasEllipse.__init__(self,radius*2,radius*2,canvas)
    self.name=name
    self.canvas=canvas
    self.color=color
    self.setBrush(QBrush(self.color))
    self.setX(center_x)
    self.setY(center_y)
    self.myRTTI=POINT_SOURCE_RTTI

  def rtti(self):
    return self.myRTTI

class DynamicTip( QToolTip ):
    def __init__( self, parent ):
        QToolTip.__init__( self, parent )

    def maybeTip( self, pos ):
        rs =QToolTip(self).parentWidget().anythingToTip(pos)
        if rs[0]==None:
          return
        
        QToolTip(self).tip( rs[0], rs[1] )


