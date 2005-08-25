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

from common_utils import *


##########################################################################



class MyCanvasView(QCanvasView):
  def __init__(self,canvas,parent,name,xlabel,ylabel,zlabel,sliderlabel,lsm_object,parent_window):
    QCanvasView.__init__(self,canvas,parent,name)
    ############ initialize attributes
    
    # number of divisions in axes
    self.xdivs=5
    self.ydivs=5
    self.grid_on=0
    self.display_point_sources='cross' #cross,point,pcross

    self.canvas().setDoubleBuffering(True) 
    self.viewport().setMouseTracking(1) 

    self.default_freq_index=0
    self.default_time_index=0
    # display A, I, Q, U, V
    self.default_mode='A'

    # display coordinates in Radians (rad) or degrees (deg)
    self.default_coords='rad' 

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
    self.d1=60
    self.d3=30
    self.d4=30
    self.d2=30 # more pixels for the legend

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
     self.xlabel.setText("<font color=\"blue\">"+str(tmpval[0])+"<sup>o</sup>"+str(tmpval[1])+"<sup>o</sup>"+str(tmpval[2])+"<sup>'</sup>""</font>")
     tmpval=radToDec(xys[1])
     self.ylabel.setText("<font color=\"blue\">"+str(tmpval[0])+"<sup>o</sup>"+str(tmpval[1])+"<sup>o</sup>"+str(tmpval[2])+"<sup>'</sup>""</font>")

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
    headstr="At ("+tmpstr[0]+tmpstr[1]+"Hz, "
    tmpstr=stdForm(head[1],'%3.4f')
    headstr=headstr+tmpstr[0]+tmpstr[1]+"s)"
    tmp_str=headstr+"<ul>"
    found_anything=0
    for each_item in ilist:
     if each_item.rtti()==POINT_SOURCE_RTTI:
      # set flag
      found_anything=1
      tmp_str=tmp_str+"<li>"+each_item.name+" "
      # print brightness value as well
      punit=self.lsm.p_table[each_item.name]
      br=""
      if punit != None:
       br="[%5.4f, %5.4f] %5.3f "%(punit.sp.getRA(),punit.sp.getDec(),punit.getBrightness(self.default_mode,self.default_freq_index, self.default_time_index))
      br+="</li>"
      tmp_str+=br
    if found_anything != 0: # not empty
     tmp_str=tmp_str+"</ul>"
     dialog=SDialog(self)
     dialog.setInfoText(tmp_str)
     dialog.show()
     #QMessageBox.information(None, headstr,
     #       tmp_str 
     #       ,"Dismiss")

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
    self.zoom_status=GUI_SELECT_WINDOW
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
    dialog=SDialog(self)
    dialog.setInfoText(tmp_str)
    dialog.show()

    # create a patch
    retval=self.lsm.createPatch(psource_list)
    if retval != None:
     # successfully created patch
     print "created patch %s"%retval[0]
     # update the GUI
     self.p_tab[retval[0]]=Patch(retval[0],self,retval[1],retval[2],\
                 retval[3],retval[4])

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
      tmp_str+="["+each_item.name+"]"
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
     if math.log(punit.getBrightness(self.default_mode,self.default_freq_index, self.default_time_index)/self.min_brightness)/math.log(self.max_brightness/self.min_brightness) <self.parent.sliderCut.value()/100.0:
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
   print "Update display ",type
   # first, set min,max limits for
   # brightness
   print "Current limits [%f,%f]"%(self.max_brightness,self.min_brightness)
   self.max_brightness=self.lsm.getMaxBrightness(type,f_index,t_index)
   self.min_brightness=self.lsm.getMinBrightness(type,f_index,t_index)
   
   print "Updated limits [%f,%f]"%(self.max_brightness,self.min_brightness)
   # next update p-unit table (colours)
   for sname in self.lsm.p_table.keys():
    punit=self.lsm.p_table[sname]
    # update size and colour both, if pcrosses are displayed 
    self.p_tab[sname].updateDisplayProperties(self.getColor(punit.getBrightness(type,f_index,t_index)), punit.getBrightness(type,f_index,t_index))
   self.canvas().update()  

   # update indicator
   head=self.lsm.getCurrentFreqTime(self.default_freq_index,self.default_time_index)
   tmpval=stdForm(head[0],'%3.4f')
   headstr="("+tmpval[0]+tmpval[1]+"Hz,"
   tmpval=stdForm(head[1],'%3.4f')
   headstr=headstr+tmpval[0]+tmpval[1]+"s)"
   #headstr="f=%5.4f GHz,t=%5.4f s"%(head[0]/1.0e9,head[1])
   self.zlabel.setText("<font color=\"blue\">"+headstr+"</font>")


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


  # save the canvas as a pixmap
  def getPixmap(self):
    pm=QPixmap(self.canvas().width(),self.canvas().height())
    pn=QPainter(pm)
    self.canvas().drawArea(self.canvas().rect(),pm)
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
    self.axfont=QFont( QApplication.font() )
    self.axfont.setPointSize( 10 )
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
     degstr=tck[2]+" "+tck[3]+" "+tck[4]
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
    ll=self.getTicks(bounds['min_Dec'],bounds['max_Dec'],y_ticks,'%1.4f')
    for tck in ll:
     yval=tck[0]
     xstr=tck[1]
     degstr=tck[2]+" "+tck[3]+" "+tck[4]
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

  def chooseFont( self ) :
   ok = 0
   oldfont = QFont( self.axfont )
   newfont, ok = QFontDialog.getFont(oldfont,self.cview)
   if ok:
    self.updateFont(newfont)

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
  xys=self.cview.globalToLocal(self.x_min,self.y_max)
  topLeft=QPoint(xys[0],xys[1])
  xys=self.cview.globalToLocal(self.x_max,self.y_min)
  bottomRight=QPoint(xys[0],xys[1])
  rectangle=QRect(topLeft,bottomRight)
  self.rect=QCanvasRectangle(rectangle,self.cview.canvas())
  self.rect.setPen(QPen(QColor(255,0,0)))
  self.show()

 def hide(self):
  self.rect.hide()

 def show(self):
  self.rect.show()

 def hideAll(self):
  self.rect.hide()

 def showAll(self):
  self.rect.show()


 def showType(self,flag):
  self.show()

 def updateDisplayProperties(self,newcolor,new_value):
  pass
