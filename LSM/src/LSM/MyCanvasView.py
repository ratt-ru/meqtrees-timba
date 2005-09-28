#!/usr/bin/python

##########################################################
########### The image displayer. Everything is done here
########### including communicating with the meqtrees
##########################################################

import sys
import math
from qt import *
from qtcanvas import *

from LSM import *
from SDialog import *
from PatchDialog import *
from PatchGLDialog import *

from common_utils import *

import numarray

##########################################################################



class MyCanvasView(QCanvasView):
  def __init__(self,canvas,parent,name,xlabel,ylabel,zlabel,sliderlabel,lsm_object,parent_window):
    QCanvasView.__init__(self,canvas,parent,name)
    ############ initialize attributes
    
    # number of divisions in axes
    self.xdivs=5
    self.ydivs=5
    self.grid_on=0
    self.legend_on=0
    self.display_point_sources='pcross' #cross,point,pcross

    self.canvas().setDoubleBuffering(True) 
    self.viewport().setMouseTracking(1) 

    self.default_freq_index=0
    self.default_time_index=0
    # display A, I, Q, U, V
    # A : Apparent brightness
    self.default_mode='A'

    # display coordinates in Radians (rad) or degrees (deg)
    self.default_coords='rad' 

    self.font=QFont(QApplication.font())
    self.font.setPointSize(10)
    # get boundaries (using ObsWin  ?)
    # 1. create Cell using ObsWin, 2. send request to meqserver, 
    # 3. scan the result set to determine boundaries of
    #    RA, Dec, I, Q, U, V 

    self.lsm=lsm_object
    self.parent=parent_window
    self.max_brightness=self.lsm.getMaxBrightness()
    self.min_brightness=self.lsm.getMinBrightness()
    bounds=self.lsm.getBounds()
    # boundaries
    #    +-----------------+
    #    |         d3      |
    #    | d1 |---------|d2|
    #    .    .         .  .
    #    .    .         .  .
    #    |    +---------+  |
    #    +_____ d4_________+

    [char_w,char_h]=self.getTextDims("%8.3f")
    print char_w
    self.d1=char_w+15+20 # 20 for the axis label
    self.d3=30
    self.d4=30+20 # 20 for the axis label
    self.d2=5 # more pixels for the legend

    # limits in real coordinates
    self.x_min=bounds['min_RA']
    self.x_max=bounds['max_RA']
    self.y_min=bounds['min_Dec']
    self.y_max=bounds['max_Dec']
    # canvas size
    H=self.canvas().height()
    W=self.canvas().width()
    # scales
    if (self.x_max != self.x_min):
     self.x_scale=(W-self.d1-self.d2)/(self.x_max-self.x_min)
    else: 
     self.x_scale=1.0

    if (self.y_max != self.y_min):
     self.y_scale=(H-self.d3-self.d4)/(self.y_max-self.y_min)
    else:
     self.y_scale=1.0

    # Tool Tip
    self.tooltip=DynamicTip(self)
    # printer
    self.printer=QPrinter()

    ############ create p-unit list
    # table for all p-units plots on canvas
    self.p_tab={}
    # plot all p-units/sources
    for sname in self.lsm.p_table.keys():
     punit=self.lsm.p_table[sname]
     if punit.getType()==POINT_TYPE:
      xys=self.globalToLocal(punit.sp.getRA(),punit.sp.getDec())
      self.p_tab[sname]=PointSource(sname,self)
     else:
      # we have a patch
      retval=punit.getLimits()
      self.p_tab[sname]=Patch(sname,self,retval[0],retval[1],\
                 retval[2],retval[3])


    ############ create axes/grid
    self.axes=Axes(self,bounds,self.xdivs,self.ydivs)
    self.axes.gridOff()

    ############ create legend
    self.legend=None

    ############ create zoom-window
    self.zwindow=ZWindow(self.canvas())
    #self.zwindow.hide()
    self.zoom_status=GUI_ZOOM_NONE
    # store transformation matrices zoom in/out
    self.tmstack=None



    ############ create slider
    # done by the parent

    ############ create x,y,z labels
    self.xlabel=xlabel
    self.ylabel=ylabel
    self.zlabel=zlabel
    self.resetFTindices()
    #head=self.lsm.getCurrentFreqTime(self.default_freq_index,self.default_time_index)

    #tmpval=stdForm(head[0],'%3.4f')
    #headstr="("+tmpval[0]+tmpval[1]+"Hz,"
    #tmpval=stdForm(head[1],'%3.4f')
    #headstr=headstr+tmpval[0]+tmpval[1]+"s)"
    #self.zlabel.setText("<font color=\"blue\">"+headstr+"</font>")


    self.slabel=sliderlabel
 
    
  def contentsMouseMoveEvent(self,e):
    point = self.inverseWorldMatrix().map(e.pos())
    xys=self.localToGlobal(point.x(),point.y())

    if self.default_coords=='rad':
     x_val='%2.6f'%xys[0]
     y_val='%2.6f'%xys[1]
     self.xlabel.setText("<font color=\"blue\">"+str(x_val)+"</font>")
     self.ylabel.setText("<font color=\"blue\">"+str(y_val)+"</font>")
    else: # degrees
     tmpval=radToRA(xys[0])
     self.xlabel.setText("<font color=\"blue\">"+str(tmpval[0])+"<sup>o</sup>"+str(tmpval[1])+"<sup>'</sup>"+str(tmpval[2])+"<sup>''</sup>""</font>")
     tmpval=radToDec(xys[1])
     self.ylabel.setText("<font color=\"blue\">"+str(tmpval[0])+"<sup>o</sup>"+str(tmpval[1])+"<sup>'</sup>"+str(tmpval[2])+"<sup>''</sup>""</font>")

    # move zoom window
    if self.zoom_status==GUI_ZOOM_START or\
       self.zoom_status==GUI_SELECT_START:
     self.zwindow.setLowerRight(point.x(),point.y())
     self.zwindow.show()
     self.canvas().update()
    return
   
  def contentsMousePressEvent(self,e):
   point = self.inverseWorldMatrix().map(e.pos())
   
   if self.zoom_status==GUI_ZOOM_NONE:
    ilist = self.canvas().collisions(point) #QCanvasItemList ilist
    head=self.lsm.getCurrentFreqTime(self.default_freq_index,self.default_time_index)
    tmpstr=stdForm(head[0],'%3.4f')
    headstr="<font color=\"blue\">("+tmpstr[0]+tmpstr[1]+"Hz, "
    tmpstr=stdForm(head[1],'%3.4f')
    headstr=headstr+tmpstr[0]+tmpstr[1]+"s)</font><br/>Sources:<br/>"
    tmp_str=headstr+"<ul>"
    found_anything=0
    #print ilist
    for each_item in ilist:
     if each_item.rtti()==POINT_SOURCE_RTTI:
      # set flag
      found_anything=1
      tmp_str=tmp_str+"<li>Label : "+each_item.name+" "
      # print brightness value as well
      punit=self.lsm.p_table[each_item.name]
      br=""
      if punit != None:
       br="At [%5.4f, %5.4f]<br/>App. Brightness: %5.3f "%(punit.sp.getRA(),punit.sp.getDec(),punit.getBrightness(self.default_mode,self.default_freq_index, self.default_time_index))
      tmp_str+=br
      if punit._patch_name !=None:
       tmp_str+="<br/>patch <font color=\"blue\">"+punit._patch_name+"</font></li>"
      else:
       tmp_str+="</li>"
 

    if found_anything != 0: # not empty
     tmp_str=tmp_str+"</ul>"
     dialog=SDialog(self)
     dialog.setInfoText(tmp_str)
     dialog.show()
    else: # list is empty, no point sources, may be patches
     # re-scan the list for patches 
     found_anything=0
     tmp_str=""
     for each_item in ilist:
      if each_item.rtti()==PATCH_IMAGE_RTTI:
       #print "Found a Patch name %s"%each_item.parent.name
       #print each_item.image
       found_anything=1
       mimes=QMimeSourceFactory()
       patch_img=each_item.image.scale(100,100,QImage.ScaleMin)
       patch_img.invertPixels()
       mimes.setImage("img"+each_item.parent.name,patch_img)
       tmp_str+="<p><u>"+each_item.parent.name+"</u><br/>"
       tmp_str+="Image: <img source=\"img"+each_item.parent.name+"\" alt=\"image\""
       tmp_str+=" title=\"Image Title\" border=\"1\" style=\"width: 262px; height: 300px;\"/>"
       tmp_str+="<br/><br/></p>"
       #print tmp_str
     if found_anything !=0: 
      dialog=SDialog(self)
      dialog.textEdit.setMimeSourceFactory(mimes)
      dialog.setInfoText(tmp_str)
      dialog.setTitle("Patch Info")
      dialog.show()
     """try:
        # get vellsets if any
        punit=self.lsm.p_table[each_item.parent.name]
        lims=punit.sp.getValueSize(self.default_mode,\
         self.default_freq_index,\
         self.default_time_index)
        # the return type should be a numarray
        my_arr=punit.sp.getValue(self.default_mode,\
         self.default_freq_index,\
         self.default_time_index)
        # create GL window
        #wn=PatchGLDialog(self,"Patch",1,0,my_arr,lims)
        #wn.show()
       except:
        pass
     """

   if self.zoom_status==GUI_ZOOM_WINDOW:
    self.zoom_status=GUI_ZOOM_START
    self.zwindow.setUpperLeft(point.x(),point.y())
    self.zwindow.setLowerRight(point.x(),point.y())
    self.zwindow.show()
    self.canvas().update()
   # select window
   if self.zoom_status==GUI_SELECT_WINDOW:
    self.zoom_status=GUI_SELECT_START
    self.zwindow.setUpperLeft(point.x(),point.y())
    self.zwindow.setLowerRight(point.x(),point.y())
    self.zwindow.show()
    self.canvas().update()
   return

  def contentsMouseReleaseEvent(self,e):
   point = self.inverseWorldMatrix().map(e.pos())
   #cpoint=self.contentsToViewport(point)
   if self.zoom_status==GUI_ZOOM_START:
    self.zoom_status=GUI_ZOOM_WINDOW
    self.zwindow.hide()
    # zoom window
    mm=QWMatrix()
    if point.x()!=self.zwindow.left_x:
     xsc=float(self.visibleWidth())/(point.x()-self.zwindow.left_x)
    else:
     xsc=1
    if point.y()!=self.zwindow.left_y:
     ysc=float(self.visibleHeight())/(point.y()-self.zwindow.left_y)
    else:
     ysc=1
    if xsc<ysc:
      ysc=xsc
    else:
      xsc=ysc
    mm.scale(xsc,ysc)
    mm.translate(-self.zwindow.left_x,-self.zwindow.left_y)
    #mm*=self.worldMatrix()
    # store old matrix 
    #g = self.worldMatrix()
    g=QWMatrix()
    #print "inverse translation ",self.zwindow.left_x,self.zwindow.left_y
    g.translate(self.zwindow.left_x,self.zwindow.left_y)
    #print "inverse scaling ",1/xsc, 1/ysc
    g.scale( 1/xsc, 1/ysc)
    #g*=self.worldMatrix()

    self.tmstack=g
    self.setWorldMatrix(mm)
    self.canvas().update()

   if self.zoom_status==GUI_SELECT_START:
    self.zoom_status=GUI_ZOOM_NONE
    self.zwindow.hide()
    ilist = self.canvas().collisions(self.zwindow.getRect()) #QCanvasItemList ilist
    tmp_str=""
    # create a list of point source names,
    # if a patch is created
    psource_list=[]
    for each_item in ilist:
     if each_item.rtti()==POINT_SOURCE_RTTI:
      tmp_str+=" "+each_item.name+"<br>"
      psource_list.append(each_item.name)
    # if empty, do nothing
    if len(psource_list)==0:
     return
    dialog=PatchDialog(self)
    dialog.setInfoText(tmp_str)
    if dialog.exec_loop() == QDialog.Accepted:
     # create a patch
     retval=self.lsm.createPatch(psource_list)
     if retval != None:
      # successfully created patch
      #print "created patch %s"%retval[0]
      # remove these sources from PUnit table on main window
      self.parent.removePUnitRows(psource_list)
      # update the GUI
      self.p_tab[retval[0]]=Patch(retval[0],self,retval[1],retval[2],\
                 retval[3],retval[4])
      # update PUnit table on main window
      self.parent.insertPUnitRow(retval[0])
    self.canvas().update()
   return


  # return local coordinates for given global coordinates
  def localToGlobal(self,x,y):
   #l=[(x-self.d1)/self.x_scale+self.x_min,-(y-self.d3)/self.y_scale+self.y_max]
   l=[-(x-self.d1)/self.x_scale+self.x_max,-(y-self.d3)/self.y_scale+self.y_max]
   return l
  # return global coordinates for given local coordinates
  def globalToLocal(self,x,y):
   #l=[(x-self.x_min)*self.x_scale+self.d1,(self.y_max-y)*self.y_scale+self.d3]
   l=[(-x+self.x_max)*self.x_scale+self.d1,(self.y_max-y)*self.y_scale+self.d3]
   return l

  # return a colour according to brightness
  def getColor(self,z):
    if self.max_brightness==0:
     return QColor(1,1,1) # no color : when Q,U,V is zero

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
   tmp_str=""
   for each_item in ilist:
     if each_item.rtti()==POINT_SOURCE_RTTI:
      tmp_str+=" "+each_item.name+" "
      # see if it belongs to a patch
      punit=self.lsm.p_table[each_item.name]
      if punit._patch_name!=None:
       tmp_str+="("+punit._patch_name+")"

   cr=QRect(self.contentsToViewport(self.worldMatrix().map(point)),QSize(len(tmp_str),2))
   return [cr,tmp_str]

  # Explicitly delete the tooltip
  def __del__(self):
    del self.tooltip
    self.tooltip=None


  def display(self):
   #print self.parent.slider1.value()
   for sname in self.lsm.p_table.keys():
     punit=self.lsm.p_table[sname]
     #if punit.getBrightness()/self.max_brightness*500 <self.parent.slider1.value():
     if punit.getType()==POINT_TYPE and\
       math.log(punit.getBrightness(self.default_mode,self.default_freq_index, self.default_time_index)/self.min_brightness)/math.log(self.max_brightness/self.min_brightness) <self.parent.sliderCut.value()/100.0: 
      self.p_tab[sname].hide()
     else:
      self.p_tab[sname].show()
 
   tmpstr="%4.3f"%(math.pow(math.e,math.log(self.max_brightness/self.min_brightness)*self.parent.sliderCut.value()/100.0)*self.min_brightness)
   self.slabel.setText(tmpstr) 
   self.canvas().update()  

  # update axes
  def updateAxes(self,x_count,y_count):
    bounds=self.lsm.getBounds()
    if self.axes != None:
     self.axes.gridOff()
     self.axes.hide()
     del self.axes
    self.axes=Axes(self,bounds,x_count,y_count)
    self.xdivs=x_count
    self.ydivs=y_count
 
    if self.grid_on==0:
     self.axes.gridOff()

  # display a new (f,t) with a new I,Q,U,V or app_brightness
  # value
  # type='I','Q','U','V', or 'A' for app_brightness
  def updateDisplay(self,type='A',f_index=0,t_index=0):
   self.default_freq_index=f_index
   self.default_time_index=t_index
   self.default_mode=type
   #print "Update display ",type
   # first, set min,max limits for
   # brightness
   #print "Current limits [%f,%f]"%(self.max_brightness,self.min_brightness)
   self.max_brightness=self.lsm.getMaxBrightness(type,f_index,t_index)
   self.min_brightness=self.lsm.getMinBrightness(type,f_index,t_index)
   
   #print "Updated limits [%f,%f]"%(self.max_brightness,self.min_brightness)
   # next update p-unit table (colours)
   for sname in self.lsm.p_table.keys():
    punit=self.lsm.p_table[sname]
    if punit.getType()==POINT_TYPE:
     # update size and colour both, if pcrosses are displayed 
     self.p_tab[sname].updateDisplayProperties(self.getColor(punit.getBrightness(type,f_index,t_index)), punit.getBrightness(type,f_index,t_index))
    else: #PATCH_TYPE
     self.p_tab[sname].updateDisplayProperties()

   # update indicator
   head=self.lsm.getCurrentFreqTime(self.default_freq_index,self.default_time_index)
   tmpval=stdForm(head[0],'%3.4f')
   headstr="("+tmpval[0]+tmpval[1]+"Hz,"
   tmpval=stdForm(head[1],'%3.4f')
   headstr=headstr+tmpval[0]+tmpval[1]+"s)"
   #headstr="f=%5.4f GHz,t=%5.4f s"%(head[0]/1.0e9,head[1])
   self.zlabel.setText("<font color=\"blue\">"+headstr+"</font>")
   # update legend
   if self.legend!=None:
    self.legend.hide()
    self.showLegend(1)

   self.canvas().update()  

  def showPointSources(self,flag):
    # flag:0==circle(point),1==cross
    if flag==0:
     self.display_point_sources='point'
    elif flag==1:
     self.display_point_sources='cross'
    else:
     self.display_point_sources='pcross'
    for sname in self.lsm.p_table.keys():
      self.p_tab[sname].showType(flag)

  # resets F,T back to 0,0
  # needed when the cells are updated
  def resetFTindices(self):
    self.default_freq_index=0
    self.default_time_index=0
    head=self.lsm.getCurrentFreqTime(self.default_freq_index,self.default_time_index)

    tmpval=stdForm(head[0],'%3.4f')
    headstr="("+tmpval[0]+tmpval[1]+"Hz,"
    tmpval=stdForm(head[1],'%3.4f')
    headstr=headstr+tmpval[0]+tmpval[1]+"s)"
    self.zlabel.setText("<font color=\"blue\">"+headstr+"</font>")


  # create patches from the grid, only if the grid is ON
  def createPatchesFromGrid(self,min_bright=0.0,max_bright=10.0,min_sources=1):
   # create two arrays for x divisions
   # and y divisions and send to the LSM to create 
   # patches
   if self.grid_on==1:
    #print "creating patches from grid"
    stp=(self.x_max-self.x_min)/self.xdivs
    x_array=[self.x_min]
    for ii in range(self.xdivs):
     x_array.append(self.x_min+(ii+1)*stp)
    stp=(self.y_max-self.y_min)/self.ydivs
    y_array=[self.y_min]
    for ii in range(self.ydivs):
     y_array.append(self.y_min+(ii+1)*stp)

    retval_arr=self.lsm.createPatchesFromGrid(x_array,y_array,min_bright,max_bright,min_sources)
    #print retval_arr
    if retval_arr != None:
      for retval in retval_arr:
       if retval !=None:
        # successfully created patch
        #print "created patch",retval
        # get the sources of this patch
        punit=self.lsm.getPUnit(retval[0])
        psource_list=punit.getSources()
        # remove these sources from PUnit table on main window
        self.parent.removePUnitRows(psource_list)
        # update the GUI
        self.p_tab[retval[0]]=Patch(retval[0],self,retval[1],retval[2],\
                 retval[3],retval[4])
        # update PUnit table on main window
        self.parent.insertPUnitRow(retval[0])
      self.canvas().update()

  def showLegend(self,flag):
   """if flag==1, show legend, else hide legend"""
   # get dimensions needed
   [char_w,char_h]=self.getTextDims("%8.3f")
   if flag==1:
    self.canvas().resize(self.canvas().width()+30+char_w,self.canvas().height())
    # get limits from the boundary of main plot
    qp=self.axes.rect.rect()
    print qp.right(),qp.bottom(),qp.top()
    #rr=QCanvasRectangle(qp.right()+self.d2+5,qp.top(),24,qp.bottom()-qp.top(),self.canvas())
    self.legend=Legend(qp.right()+self.d2+5,qp.top(),24,qp.bottom()-qp.top(),\
        self.canvas(),self,"%8.3f")
    self.legend.show()
    self.legend_on=1
   elif flag==0 and self.legend_on==1:
    self.canvas().resize(self.canvas().width()-30-char_w,self.canvas().height())
    self.legend_on=0
    if self.legend !=None:
     self.legend.hide()
     self.legend=None

  # give the text width,height in pixels using the default font
  def getTextDims(self,format):
    myfont=self.font
    fm=QFontMetrics(myfont)
    # find width in pixels
    label=QString(format%0.0)
    char_width=fm.width(label)
    char_height=fm.height()
    return (char_width,char_height)

  #select new font
  def chooseFont( self ) :
   ok = 0
   oldfont = QFont( self.font )
   newfont, ok = QFontDialog.getFont(oldfont,self)
   if ok:
    self.font=newfont
    self.axes.updateFont(newfont)
    if self.legend !=None:
     self.legend.updateFont(newfont)


  # save the canvas as a pixmap
  def getPixmap(self):
    pm=QPixmap(self.canvas().width(),self.canvas().height())
    pn=QPainter(pm)
    self.canvas().drawArea(self.canvas().rect(),pn)
    return pm
  # return label as a pixmap
  def createLabel(self,label):
    pmap=QPixmap(len(label)+5,20) 
    painter=QPainter(pmap)
    m=QWMatrix()
    m.rotate(90)
    #painter.begin(pmap)
    painter.setWorldMatrix(m)
    painter.drawText(0,0,label)
    #painter.end() 
    return pmap


#################################################################
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

  def updateColor(self,color):
   self.color=color
   self.setBrush(QBrush(self.color))


##################################################################
class Cross(QCanvasPolygon):
  def __init__(self,center_x,center_y,w,l,color,name,canvas):
    QCanvasPolygon.__init__(self,canvas)
    self.name=name
    self.canvas=canvas
    self.color=color
    self.setBrush(QBrush(self.color))
    self.myRTTI=POINT_SOURCE_RTTI
    pa=QPointArray(12)
    pa.setPoint(0, QPoint(w,w))
    pa.setPoint(1, QPoint(w,l))
    pa.setPoint(2, QPoint(-w,l))
    pa.setPoint(3, QPoint(-w,w))
    pa.setPoint(4, QPoint(-l,w))
    pa.setPoint(5, QPoint(-l,-w))
    pa.setPoint(6, QPoint(-w,-w))
    pa.setPoint(7, QPoint(-w,-l))
    pa.setPoint(8, QPoint(w,-l))
    pa.setPoint(9, QPoint(w,-w))
    pa.setPoint(10, QPoint(l,-w))
    pa.setPoint(11, QPoint(l,w))
    self.setPoints(pa)
    self.myRTTI=POINT_SOURCE_RTTI
    self.setBrush(QBrush(color))
    self.move(center_x,center_y)

  def rtti(self):
    return self.myRTTI
 
  def updateColor(self,color):
   self.color=color
   self.setBrush(QBrush(self.color))

#################################################################
class DynamicTip( QToolTip ):
    def __init__( self, parent ):
        QToolTip.__init__( self, parent )

    def maybeTip( self, pos ):
        rs =QToolTip(self).parentWidget().anythingToTip(pos)
        if rs[0]==None:
          return
        
        QToolTip(self).tip( rs[0], rs[1] )
        self.parentWidget().canvas().update()

####################################################
# class for zoom window
class ZWindow(QCanvasRectangle):
  def __init__(self,canvas):
    QCanvasRectangle.__init__(self,canvas) 
    self.left_x=0
    self.left_y=0
    self.right_x=0
    self.right_y=0
  def setUpperLeft(self,left_x,left_y):
    self.left_x=left_x
    self.left_y=left_y
    # move to this place
    self.move(left_x,left_y)
    # set size to zero
    self.setSize(0,0)
  def setLowerRight(self,right_x,right_y):
    self.right_x=right_x
    self.right_y=right_y
    # resize the rectangle to get correct size
    self.setSize(right_x-self.left_x,right_y-self.left_y)

  def getRect(self):
   return QRect(QPoint(self.left_x,self.left_y),QPoint(self.right_x,self.right_y))



##########################################################
class Axes:
  """ canvas_view: QCanvasview object
      bounds: dict with min_RA,max_RA,min_Dec,max_Dec values
      x_ticks,y_ticks: number of division in x and y direction
  """
  def __init__(self,canvas_view,bounds,x_ticks,y_ticks):
    self.cview=canvas_view
    # draw boundary
    xys=self.cview.globalToLocal(bounds['max_RA'],bounds['max_Dec'])
    self.rect=QCanvasRectangle(xys[0],xys[1],float(bounds['max_RA']-bounds['min_RA'])*self.cview.x_scale,float(bounds['max_Dec']-bounds['min_Dec'])*self.cview.y_scale,self.cview.canvas())
    #ff=QCanvasRectangle(xys[0],xys[1],float(self.x_max-self.x_min)*self.x_scale,float(self.y_max-self.y_min)*self.y_scale,self.canvas())
    self.rect.show()

    # grid
    self.grid=[]

    # font for axes ticks
    self.axfont=QFont(canvas_view.font)
    #self.axfont.setPointSize(10)
    #self.axfont.setWeight( QFont.Bold )
    #self.axfont.setUnderline( True )


    # draw X axis
    self.xax=[]
    self.xax_text=[]
    self.xax_degtext=[]
    ll=self.getTicks(bounds['min_RA'],bounds['max_RA'],x_ticks,'%1.3f')
    for tck in ll:
     xval=tck[0]
     xstr=tck[1]
     degstr=tck[2]+":"+tck[3]+":"+tck[4]
     # draw line
     ff=QCanvasLine(self.cview.canvas())
     xys=self.cview.globalToLocal(xval,self.cview.y_min)
     ff.setPoints(xys[0],xys[1],xys[0],xys[1]+10)
     ff.show()
     self.xax.append(ff)
     # text in radians 
     rt=QCanvasText(self.cview.canvas())
     rt.setText(xstr)
     rt.setFont( self.axfont )
     rt.move(xys[0]-25,xys[1]+9)
     rt.setZ(0)
     rt.hide()
     self.xax_text.append(rt)
     # text in degrees
     dt=QCanvasText(self.cview.canvas())
     dt.setText(degstr)
     dt.setFont( self.axfont )
     dt.move(xys[0]-25,xys[1]+9)
     dt.setZ(0)
     dt.hide()
     self.xax_degtext.append(dt)
     if self.cview.default_coords=='rad':
      rt.show()
     else:
      dt.show()

     # draw grid lines
     ff=QCanvasLine(self.cview.canvas())
     xys=self.cview.globalToLocal(xval,self.cview.y_min)
     xys1=self.cview.globalToLocal(xval,self.cview.y_max)
     ff.setPoints(xys[0],xys[1],xys1[0],xys1[1])
     ff.show()
     self.grid.append(ff)

    # draw Y axis
    self.yax=[]
    self.yax_text=[]
    self.yax_degtext=[]
    ll=self.getTicks(bounds['min_Dec'],bounds['max_Dec'],y_ticks,'%1.4f','y')
    for tck in ll:
     yval=tck[0]
     xstr=tck[1]
     degstr=tck[2]+"."+tck[3]+"."+tck[4]
     # draw line
     ff=QCanvasLine(self.cview.canvas())
     xys=self.cview.globalToLocal(self.cview.x_max,yval)
     ff.setPoints(xys[0],xys[1],xys[0]-10,xys[1])
     ff.show()
     self.yax.append(ff)
     # text in radians 
     rt=QCanvasText(self.cview.canvas())
     rt.setText(xstr)
     rt.setFont( self.axfont )
     rt.move(xys[0]-60,xys[1]-9)
     rt.setZ(0)
     rt.hide()
     self.yax_text.append(rt)
     # text in degrees
     dt=QCanvasText(self.cview.canvas())
     dt.setText(degstr)
     dt.setFont( self.axfont )
     dt.move(xys[0]-60,xys[1]-9)
     dt.setZ(0)
     dt.hide()
     self.yax_degtext.append(dt)
     if self.cview.default_coords=='rad':
      rt.show()
     else:
      dt.show()

     # draw grid lines
     ff=QCanvasLine(self.cview.canvas())
     xys=self.cview.globalToLocal(self.cview.x_min, yval)
     xys1=self.cview.globalToLocal(self.cview.x_max, yval)
     ff.setPoints(xys[0],xys[1],xys1[0],xys1[1])
     ff.show()
     self.grid.append(ff)

    # draw axes labels
    self.ylabel=FontVertImage("Declination",self.cview.canvas())
    xys=self.cview.globalToLocal(self.cview.x_max, self.cview.y_min)
    self.ylabel.move(xys[0]-self.cview.d1,xys[1]-(self.cview.canvas().height()-self.cview.d3-self.cview.d4)/2-self.ylabel.height()/2)
    self.ylabel.setZ(0)
    self.ylabel.show()

    self.xlabel=FontHorizImage("Right Ascension",self.cview.canvas())
    self.xlabel.move(xys[0]+(self.cview.canvas().width()-self.cview.d1-self.cview.d2)/2-self.xlabel.width()/2,xys[1]+self.cview.d4-20)
    #self.xlabel.move(xys[0],xys[1])
    self.xlabel.setZ(0)
    self.xlabel.show()

  # return tickmarks for the axis
  # returns [coordinate value, rad_value, hr, min, sec]
  def getTicks(self,start_x,end_x,divisions=10,format='%e',axis='x'):
     inc=(end_x-start_x)/float(divisions)
     output=[]
     # start point
     st=format%start_x
     # degrees
     if axis=='x':
      tmpval=radToRA(start_x)
     else:
      tmpval=radToDec(start_x)
     output.append([start_x, st, str(tmpval[0]), str(tmpval[1]), str(tmpval[2])])
     for i in range(divisions):
      val=start_x+(i+1)*inc
      st=format%val
      if axis=='x':
       tmpval=radToRA(val)
      else:
       tmpval=radToDec(val)
      output.append([val, st, str(tmpval[0]), str(tmpval[1]), str(tmpval[2])])
      #output.append([val,st])

     return output

  # hide axes 
  def hide(self):
   for i in range(len(self.xax)):
    self.xax[i].hide()
   for i in range(len(self.xax_text)):
    self.xax_text[i].hide()
    self.xax_degtext[i].hide()
   for i in range(len(self.yax)):
    self.yax[i].hide()
   for i in range(len(self.yax_text)):
    self.yax_text[i].hide()
    self.yax_degtext[i].hide()

  # show axes 
  def show(self):
   for i in range(len(self.xax)):
    self.xax[i].show()
   for i in range(len(self.xax_text)):
    self.xax_text[i].show()
    self.xax_degtext[i].show()
   for i in range(len(self.yax)):
    self.yax[i].show()
   for i in range(len(self.yax_text)):
    self.yax_text[i].show()
    self.yax_degtext[i].show()


  # hide the grid
  def gridOff(self):
    for i in range(len(self.grid)):
      self.grid[i].hide()
  # show the grid
  def gridOn(self):
    for i in range(len(self.grid)):
      self.grid[i].show()

  def updateFont(self,newfont):
    self.axfont=newfont
    for i in range(len(self.xax_text)):
     self.xax_text[i].setFont( self.axfont )
     self.xax_degtext[i].setFont( self.axfont )
    for i in range(len(self.yax_text)):
     self.yax_text[i].setFont( self.axfont )
     self.yax_degtext[i].setFont( self.axfont )

  # display coords either in radians (rad) or in degrees (deg)
  def switchCoords(self,coords='rad'):
   if coords=='rad':
    for i in range(len(self.xax_text)):
     self.xax_text[i].show()
     self.xax_degtext[i].hide()
    for i in range(len(self.yax_text)):
     self.yax_text[i].show()
     self.yax_degtext[i].hide()
   else:
    for i in range(len(self.xax_text)):
     self.xax_text[i].hide()
     self.xax_degtext[i].show()
    for i in range(len(self.yax_text)):
     self.yax_text[i].hide()
     self.yax_degtext[i].show()
   
#############################################################
class PointSource:
 def __init__(self,name,parent):
  self.name=name
  self.cview=parent
  # get corresponding PUnit
  punit=self.cview.lsm.p_table[self.name]
  # get coords 
  xys=self.cview.globalToLocal(punit.sp.getRA(),punit.sp.getDec())
  self.x=xys[0]
  self.y=xys[1]
  self.cross=self.addCross(xys[0],xys[1],1,5,self.cview.getColor(punit.getBrightness()),self.name,punit.getBrightness())
  length=int(math.log(punit.getBrightness()/self.cview.min_brightness)/math.log( self.cview.max_brightness/self.cview.min_brightness)*10)
  self.pcross=self.addCross(xys[0],xys[1],1,length,self.cview.getColor(punit.getBrightness()),self.name,punit.getBrightness())
  self.circle=self.addCircle(xys[0],xys[1],2,self.cview.getColor(punit.getBrightness()),self.name,punit.getBrightness())

  self.show()

 # circle
 def addCircle(self,center_x,center_y,radius,color,name,z_value):
  i = Circle(center_x,center_y,radius,color,name,self.cview.canvas())
  i.setZ(z_value)
  return i

 # cross - polygon
 def addCross(self,center_x,center_y,w,l,color,name,z_value):
  c=Cross(center_x,center_y,w,l,color,name,self.cview.canvas())
  c.setZ(z_value)
  return c

 def show(self):
  if self.cview.display_point_sources=='cross':
   self.cross.show()
  elif self.cview.display_point_sources=='point':
   self.circle.show()
  else:
   self.pcross.show()


 def hide(self):
  if self.cview.display_point_sources=='cross':
   self.cross.hide()
  elif self.cview.display_point_sources=='point':
   self.circle.hide()
  else:
   self.pcross.hide()

 def hideAll(self):
  self.cross.hide()
  self.circle.hide()
  self.pcross.hide()

 def showType(self,flag):
  if flag==0:
   self.cross.hide()
   self.pcross.hide()
   self.circle.show()
  elif flag==1:
   self.circle.hide()
   self.pcross.hide()
   self.cross.show()
  elif flag==2:
   self.circle.hide()
   self.pcross.show()
   self.cross.hide()


 def updateDisplayProperties(self,newcolor,new_value):
  self.circle.updateColor(newcolor)
  self.cross.updateColor(newcolor)
  # Neet to adjust the size of pcross as well
  # instead of adjusting current pcross, recreate a new one
  # self.pcross.updateColor(newcolor)
  self.pcross.hide()
  del self.pcross
  if new_value==0 or\
    self.cview.max_brightness==0:
   length=0
  else:
   length=int(math.log(new_value/self.cview.min_brightness)/math.log(self.cview.max_brightness/self.cview.min_brightness)*10)
  self.pcross=self.addCross(self.x,self.y,1,length,newcolor,self.name,new_value)
 
  if self.cview.display_point_sources=='cross':
   self.cross.show()
  elif self.cview.display_point_sources=='point':
   self.circle.show()
  else:
   self.pcross.show()

################################################################
#############################################################
class Patch:
 def __init__(self,name,parent,x_min,y_min,x_max,y_max):
  self.name=name
  self.cview=parent
  self.x_min=x_min
  self.x_max=x_max
  self.y_min=y_min
  self.y_max=y_max
  # create a rectangle
  xys=self.cview.globalToLocal(self.x_max,self.y_max)
  topLeft=QPoint(xys[0],xys[1])
  xys=self.cview.globalToLocal(self.x_min,self.y_min)
  bottomRight=QPoint(xys[0],xys[1])
  rectangle=QRect(topLeft,bottomRight)
  self.rect=QCanvasRectangle(rectangle,self.cview.canvas())
  self.rect.setPen(QPen(QColor(255,0,0)))
  self.rect.setZ(0)

  try:
   # get vellsets if any
   punit=self.cview.lsm.p_table[self.name]
   lims=punit.sp.getValueSize(self.cview.default_mode,\
    self.cview.default_freq_index,\
    self.cview.default_time_index)
 
   # the return type should be a numarray
   byarr=punit.sp.getValue(self.cview.default_mode,\
    self.cview.default_freq_index,\
    self.cview.default_time_index)
   # create an image
   self.image=ImageItem(self.createArrayImage(byarr,lims[0],lims[1]),\
           self.cview.canvas(),self)
   self.image.move(self.rect.x(),self.rect.y())
   self.image.setZ(-1)
   # change RTTI to a custom value
   self.image.setRTTI(PATCH_IMAGE_RTTI)
  except:
   self.image=None
   pass
  self.show()

 def hide(self):
  self.rect.hide()

 def show(self):
  self.rect.show()
  if self.image !=None:
   self.image.show()

 def hideAll(self):
  self.rect.hide()

 def showAll(self):
  self.rect.show()
  if self.image !=None:
   self.image.show()

 def showType(self,flag):
  self.show()

 def updateDisplayProperties(self):
  try:
   punit=self.cview.lsm.p_table[self.name]
   lims=punit.sp.getValueSize(self.cview.default_mode,\
    self.cview.default_freq_index,\
    self.cview.default_time_index)
 
   # the return type should be a numarray
   byarr=punit.sp.getValue(self.cview.default_mode,\
    self.cview.default_freq_index,\
    self.cview.default_time_index)
   # create an image
   self.image=ImageItem(self.createArrayImage(byarr,lims[0],lims[1]),\
           self.cview.canvas())
   self.image.move(self.rect.x(),self.rect.y())
   self.image.setZ(-1)
  except:
   pass

  # create an Image from the given numarray
 # size x_dim by y_dim
 def createArrayImage(self,narray,x_dim,y_dim):
   # first find min,max values
   minval=narray.min()
   maxval=narray.max()
   #print "array size is %d,%d with values %f,%f"%(x_dim,y_dim,minval,maxval)
   # create an Image of the size of this array
   # create image from this array, 32 bits depth, 2^24 colours
   im=QImage(x_dim,y_dim,32)
   # fill image with White
   im.fill(qRgb(255,255,255))
   # set pixel values for only non-zero elements
   [nz_x,nz_y]=numarray.nonzero(narray)
   for ci in range(len(nz_x)):
     cl=self.getRGB(narray[nz_x[ci]][nz_y[ci]]-minval,maxval)
     # flip the image in the y direction
     im.setPixel(nz_x[ci],y_dim-1-nz_y[ci],cl)
     #print "value %f at %d,%d"%(narray[nz_x[ci]][nz_y[ci]],nz_x[ci],nz_y[ci])

   # resize image to fit the rectangle
   im2=im.smoothScale(self.rect.width(),self.rect.height())
   #print "created image size %d,%d"%(im2.width(),im2.height())
   return im2




 # return a colour (RGB) according to brightness
 def getRGB(self,z,max_brightness):
  if max_brightness==0:
    return qRgb(1,1,1) # no color : when Q,U,V is zero

  cl=z/max_brightness # normalized in [0,1] 
  if cl < 0.25:
    return qRgb(0,int(cl*256*4),255)
  elif cl < 0.5:
    return qRgb(0,255,int((2-cl*4)*256))
  elif cl < 0.75:
    return qRgb(int((4*cl-2)*256),255,0)
  else:
    return qRgb(255,int((4-4*cl)*256),0)


###############################################################
class ImageItem(QCanvasRectangle):
    def __init__(self,img,canvas,parent=None):
        QCanvasRectangle.__init__(self,canvas)
        self.imageRTTI=984376
        self.image=img
        self.parent=parent
        self.pixmap=QPixmap()
        self.setSize(self.image.width(), self.image.height())
        self.pixmap.convertFromImage(self.image, Qt.OrderedAlphaDither);

    def setRTTI(self,rtti):
     self.imageRTTI=rtti

    def rtti(self):
        return self.imageRTTI

    def hit(self,p):
        ix = p.x()-self.x()
        iy = p.y()-self.y()
        if not self.image.valid( ix , iy ):
            return False
        self.pixel = self.image.pixel( ix, iy )
        return  (qAlpha( self.pixel ) != 0)

    def drawShape(self,p):
        p.drawPixmap( self.x(), self.y(), self.pixmap )

#################################################################
#produce text rotated by 90
class FontVertImage(QCanvasRectangle):
    def __init__(self,label,canvas):
        QCanvasRectangle.__init__(self,canvas)
        self.imageRTTI=984376
        self.label=label
        self.font=QFont( QApplication.font() )
        self.font.setPointSize( 10 )
        fm=QFontMetrics(self.font)
        margin=20
        # find width in pixels
        char_width=fm.width(self.label)
        char_height=fm.height()
        self.pixmap=QPixmap(char_height,char_width+2*margin)
        self.pixmap.fill(QColor(255,255,255))
        painter=QPainter(self.pixmap)
        m=QWMatrix() 
        m.rotate(-90)
        #m.scale(2,2)
        painter.setWorldMatrix(m)
        painter.setFont(self.font)
        tmp_str=QString(self.label)
        painter.drawText(-char_width-margin,15,QString(self.label))
        painter.end()
        self.setSize(self.pixmap.width(), self.pixmap.height())

    def rtti(self):
        return self.imageRTTI

    def drawShape(self,p):
        p.drawPixmap(self.x(),self.y(), self.pixmap )

#################################################################
#produce normal text 
class FontHorizImage(QCanvasRectangle):
    def __init__(self,label,canvas):
        QCanvasRectangle.__init__(self,canvas)
        self.imageRTTI=984376
        self.label=label
        self.font=QFont( QApplication.font() )
        self.font.setPointSize( 10 )
        fm=QFontMetrics(self.font)
        margin=20
        # find width in pixels
        char_width=fm.width(self.label)
        char_height=fm.height()
        self.pixmap=QPixmap(char_width+2*margin, char_height)
        self.pixmap.fill(QColor(255,255,255))
        painter=QPainter(self.pixmap)
        painter.setFont(self.font)
        tmp_str=QString(self.label)
        painter.drawText(margin,10,QString(self.label))
        painter.end()
        self.setSize(self.pixmap.width(), self.pixmap.height())

    def rtti(self):
        return self.imageRTTI

    def drawShape(self,p):
        p.drawPixmap(self.x(),self.y(), self.pixmap )


##################################################################
# class to draw legend colourbar
class Legend:
    def __init__(self,left,top,width,height,canvas,cview,format="%8.3f"):
       self.cview=cview
       self.canvas=canvas
       self.rect=QCanvasRectangle(left,top,width,height,canvas)
       self.top=top
       self.left=left
       self.width=width
       self.height=height
       self.format=format
   
       # fill this with coloured rectangles
       self.ncolors=10
       # height of each rectangle
       h=height/self.ncolors
       zheight=(self.cview.max_brightness-self.cview.min_brightness)/float(self.ncolors)
       self.rts=[]
       self.txt=[]
       for ci in range(1,self.ncolors):
         y=top+height-h*ci
         rt=QCanvasRectangle(left,y,width,h,canvas)
         zlevel=zheight*ci+self.cview.min_brightness
         rt.setBrush(QBrush(self.cview.getColor(zlevel)))
         self.rts.append(rt)
         # ad label
         dt=QCanvasText(canvas)
         dt.setText(format%zlevel)
         dt.setFont(self.cview.axes.axfont)
         dt.move(left+width,y-3)
         dt.setZ(0)
         self.txt.append(dt)

 
       # the last rectangle
       h=y-top
       y=top
       rt=QCanvasRectangle(left,y,width,h,canvas)
       zlevel=zheight*(ci+1)+self.cview.min_brightness
       rt.setBrush(QBrush(self.cview.getColor(zlevel)))
       self.rts.append(rt)
       dt=QCanvasText(canvas)
       dt.setText(format%zlevel)
       dt.setFont(self.cview.axes.axfont)
       dt.move(left+width,y-3)
       dt.setZ(0)
       self.txt.append(dt)

       # last, text at zero level
       zlevel=self.cview.min_brightness
       dt=QCanvasText(canvas)
       dt.setText(format%zlevel)
       y=top+height
       dt.setFont(self.cview.axes.axfont)
       dt.move(left+width,y-3)
       dt.setZ(0)
       self.txt.append(dt)




    def show(self):
      for cr in self.rts:
         cr.show()
      self.rect.show()
      for cr in self.txt:
         cr.show()


    def hide(self):
      for cr in self.rts:
         cr.hide()
      self.rect.hide()
      for cr in self.txt:
         cr.hide()
 

    def update(self):
       # height of each rectangle
       h=self.height/self.ncolors
       zheight=(self.cview.max_brightness-self.cview.min_brightness)/float(self.ncolors)
       self.rts=[]
       self.txt=[]
       for ci in range(1,self.ncolors):
         y=self.top+self.height-h*ci
         rt=QCanvasRectangle(self.left,y,self.width,h,self.canvas)
         zlevel=zheight*ci+self.cview.min_brightness
         rt.setBrush(QBrush(self.cview.getColor(zlevel)))
         self.rts.append(rt)
         # ad label
         dt=QCanvasText(self.canvas)
         dt.setText(self.format%zlevel)
         dt.setFont(self.cview.axes.axfont)
         dt.move(self.left+self.width,y-3)
         dt.setZ(0)
         self.txt.append(dt)

 
       # the last rectangle
       h=y-self.top
       y=self.top
       rt=QCanvasRectangle(self.left,y,self.width,h,self.canvas)
       zlevel=zheight*(ci+1)+self.cview.min_brightness
       rt.setBrush(QBrush(self.cview.getColor(zlevel)))
       self.rts.append(rt)
       dt=QCanvasText(self.canvas)
       dt.setText(self.format%zlevel)
       dt.setFont(self.cview.axes.axfont)
       dt.move(self.left+self.width,y-3)
       dt.setZ(0)
       self.txt.append(dt)

       # last, text at zero level
       zlevel=self.cview.min_brightness
       dt=QCanvasText(self.canvas)
       dt.setText(self.format%zlevel)
       y=self.top+self.height
       dt.setFont(self.cview.axes.axfont)
       dt.move(self.left+self.width,y-3)
       dt.setZ(0)
       self.txt.append(dt)

    def updateFont(self,newfont):
     for i in range(len(self.txt)):
      self.txt[i].setFont(newfont)
