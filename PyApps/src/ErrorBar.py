#!/usr/bin/env python

# This is a direct translation to python of Ion Vaslief's 
# ErrorBar.cpp code from his 'qtiplot' package

import math
import random
import sys
from numarray import *
from qt import *
from qwt import *

class QwtErrorPlotCurve (QwtPlotCurve):

    def __init__(self, parent, penColor=Qt.black, lineThickness=2, lineStyle=Qt.SolidLine):
        QwtPlotCurve.__init__(self, parent)
        self.pen = QPen(penColor,lineThickness,lineStyle)
        self.cap = 10
        self.type = 1
        self.size = QSize(1,1)
        self.plus = True
        self.minus = True
        self.through = False
        # to prevent surprises when doing max(self.err) in boundingRect
        self.err = [0.0]
    # __init__()

    def boundingRect(self):
        # poor man's boundingRect(). Feeling too lazy to loop or think
        # about negative errors ...
        # Errors are assumed to be all 'absolute', or positive 
        # look at the C++ implementation of QwtCurve::boundingRect()

        # print min(self.err), max(self.err)
        result = QwtCurve.boundingRect(self)
        if self.type == 1:
          result.setY1(result.y1() - max(self.err))
          result.setY2(result.y2() + max(self.err))
        else:
          result.setX1(result.x1() - max(self.err))
          result.setX2(result.x2() + max(self.err))
        return result
    # boundingRect()
        
    def draw(self, painter, xMap, yMap, ffrom, to):

      if ( not painter or self.dataSize() <= 0):
        return

      if (to < 0):
        to = self.dataSize() - 1

      if ( self.verifyRange(ffrom, to) > 0 ):
        painter.save()
        painter.setPen(self.pen)
	self.drawErrorBars(painter, xMap, yMap, ffrom, to)
        painter.restore()
    # draw()

    def drawErrorBars(self, painter, xMap, yMap, ffrom, to):
      sh = int(self.size.height())
      sw = int(self.size.width())

      for i in range(ffrom, to+1):
	xi = int(xMap.transform(self.x(i)))
	yi = int(yMap.transform(self.y(i)))

	if (self.type==1):
	  yh = int(yMap.transform(self.y(i)+self.err[i]))
	  yl = int(yMap.transform(self.y(i)-self.err[i]))
	  yhl = int((yh+yl-sh)/2-self.pen.width())
	  ylh = int((yh+yl+sh)/2+self.pen.width())

	  if ((yl-yh)>sh):
	    if self.plus:
	      painter.drawLine(xi,yhl,xi,yh)
	      painter.drawLine(xi-self.cap/2,yh,xi+self.cap/2,yh)
	    if self.minus:
	      painter.drawLine(xi,ylh,xi,yl)
	      painter.drawLine(xi-self.cap/2,yl,xi+self.cap/2,yl)
	    if self.through:
              painter.drawLine(xi,yhl,xi,ylh)
	elif (self.type==0):
	  xp = int(xMap.transform(self.x(i)+self.err[i]))
	  xm = int(xMap.transform(self.x(i)-self.err[i]))
	  xpm = int((xp+xm+sw)/2+self.pen.width())
	  xmp = int((xp+xm-sw)/2-self.pen.width())

	  if (xp-xm)>sw:
            if self.plus:
		painter.drawLine(xp,yi,xpm,yi)
		painter.drawLine(xp,yi-self.cap/2,xp,yi+self.cap/2)
	    if self.minus:
		painter.drawLine(xm,yi,xmp,yi)
		painter.drawLine(xm,yi-self.cap/2,xm,yi+self.cap/2)
	    if self.through:
		painter.drawLine(xmp,yi,xpm,yi)
    # drawErrorBars()


    def throughSymbol(self):
      return self.through

    def drawThroughSymbol(self,yes=True):
      self.through=yes

    def minusSide(self):
      return self.minus

    def drawMinusSide(self,yes=False):
      self.minus=yes

    def plusSide(self):
      return self.plus

    def drawPlusSide(self,yes=False):
      self.plus=yes

    def errors(self):
      return self.err

    def setErrors(self, data):
      self.err=data

    def setSymbolSize(self, sz):
      self.size=sz

    def direction(self):
      return self.type

    def setXErrors(self,yes):
      if yes: 
        self.type=0   # error bars to be plotted along X Axis
      else:
        self.type=1   # error bars to be plotted along Y Axis

    def capLength(self):
      return self.cap

    def setCapLength(self, t):
      self.cap=t

    def width(self):
      return self.pen.width()


    def setWidth(self, w):
      self.pen.setWidth(w)

    def color(self):
      return self.pen.color()

    def setColor(self, c):
      self.pen.setColor(c)

# class QwtErrorPlotCurve 


# stuff below this is for testing
def main(args):
    app = QApplication(args)
    demo = make()
    app.setMainWidget(demo)
    app.exec_loop()

def make():

# use numarray to create demo arrays 
    num_points = 50
    x = zeros((num_points,), Float32)  
    y = zeros((num_points,), Float32)  
    err = zeros((num_points,), Float32)  
    for i in range(0, num_points) :
        x[i] = 0.1*i;
        y[i] = sin(x[i]);
        err[i] = abs(0.5 * y[i])

# create a QwtPlot object
    demo = QwtPlot()

# create std plot curve
    plot = QwtPlotCurve(demo);
# following line actually hides pen!
    plot.setStyle(QwtCurve.NoCurve)
# following gives blue line joining points
#    plot.setPen(QPen(QColor(150, 150, 200), 2, Qt.SolidLine))
    plot.setSymbol(QwtSymbol(
            QwtSymbol.Cross, QBrush(), QPen(Qt.yellow, 2), QSize(7, 7)))
    plot.setData(x,y);
    demo.insertCurve(plot);
# the standard plot data does get plotted!!

# create error curve: error bars are plotted in red 
# with line thickness 2
#    errors = QwtErrorPlotCurve(demo,Qt.blue,2);
#    errors = QwtErrorPlotCurve(demo);
    errors = QwtErrorPlotCurve(demo,Qt.red,2);
# add in positions of data to the error curve
    errors.setData(x,y);
# add in errors to the error curve
    errors.setErrors(err);
    demo.insertCurve(errors);
#    errors.setXErrors(True)
#    errors.drawThroughSymbol()
    demo.resize(600, 600)
    demo.replot();
    demo.show()
    return demo
# make()

# Admire!
if __name__ == '__main__':
    main(sys.argv)

