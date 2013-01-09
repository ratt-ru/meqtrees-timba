
#% $Id: QwtPlotCurveSizes.py 6836 2009-03-05 18:55:17Z twillis $ 

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
#
#  (c) 2013.				 (c) 2011.
#  National Research Council		 Conseil national de recherches
#  Ottawa, Canada, K1A 0R6 		 Ottawa, Canada, K1A 0R6
#
#  This software is free software;	 Ce logiciel est libre, vous
#  you can redistribute it and/or	 pouvez le redistribuer et/ou le
#  modify it under the terms of	         modifier selon les termes de la
#  the GNU General Public License	 Licence Publique Generale GNU
#  as published by the Free		 publiee par la Free Software
#  Software Foundation; either	 	 Foundation (version 3 ou bien
#  version 2 of the License, or	 	 toute autre version ulterieure
#  (at your option) any later	 	 choisie par vous).
#  version.
#
#  This software is distributed in	 Ce logiciel est distribue car
#  the hope that it will be		 potentiellement utile, mais
#  useful, but WITHOUT ANY		 SANS AUCUNE GARANTIE, ni
#  WARRANTY; without even the	 	 explicite ni implicite, y
#  implied warranty of			 compris les garanties de
#  MERCHANTABILITY or FITNESS FOR	 commercialisation ou
#  A PARTICULAR PURPOSE.  See the	 d'adaptation dans un but
#  GNU General Public License for	 specifique. Reportez-vous a la
#  more details.			 Licence Publique Generale GNU
#  					 pour plus de details.
#
#  You should have received a copy	 Vous devez avoir reçu une copie
#  of the GNU General Public		 de la Licence Publique Generale
#  License along with this		 GNU en meme temps que ce
#  software; if not, contact the	 logiciel ; si ce n'est pas le
#  Free Software Foundation, Inc.	 cas, communiquez avec la Free
#  at http://www.fsf.org.		 Software Foundation, Inc. au
#						 http://www.fsf.org.
#
#  email:				 courriel:
#  business@hia-iha.nrc-cnrc.gc.ca	 business@hia-iha.nrc-cnrc.gc.ca
#
#  National Research Council		 Conseil national de recherches
#      Canada				    Canada
#  Herzberg Institute of Astrophysics	 Institut Herzberg d'astrophysique
#  5071 West Saanich Rd.		 5071 West Saanich Rd.
#  Victoria BC V9E 2E7			 Victoria BC V9E 2E7
#  CANADA					 CANADA
#

import numpy
import sys
from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt




class QwtPlotCurveSizes(Qwt.QwtPlotCurve):
    """ A QwtCurve with adjustable Symbols """

    def __init__(self):
      Qwt.QwtPlotCurve.__init__(self)
      self.symbolSizes = None
      self.symbolList = None

    # __init__()

    def setData(self, xData, yData, symbolSizes=None):
      """ Override default QwtCurve setData method """
      self.symbolSizes = symbolSizes
      Qwt.QwtPlotCurve.setData(self,xData,yData)
#     Qwt.QwtPlotCurve.curveChanged(self)

    def setSymbolList(self, symbolList):
      """ Override default QwtCurve symbols """
      self.symbolList = symbolList

    def drawSymbols(self, painter, symbol, xMap, yMap, start, to):
      if self.symbolList is None and self.symbolSizes is None:
        print 'QwtPlotCurveSizes fail: you must specify a symbol list or an array of symbol sizes'
        return
      painter.setBrush(symbol.brush());
      painter.setPen(symbol.pen())
      rect = Qt.QRect()
      for i in range(start, to+1):
        if not self.symbolList is None:
          painter.setBrush(self.symbolList[i].brush());
          painter.setPen(self.symbolList[i].pen())
# the following screenToLayout call should work but does not
#       symbol_size = QSize(self.symbolSizes[i], self.symbolSizes[i])
#       rect.setSize(QwtPainter.metricsMap().screenToLayout(symbol_size));

# so we do the following 
        if not self.symbolList is None:
          width = self.symbolList[i].size().width()
          height = self.symbolList[i].size().height()
          sizex = Qwt.QwtPainter.metricsMap().screenToLayoutX(width)
          sizey = Qwt.QwtPainter.metricsMap().screenToLayoutY(height)
        else:
          sizex = Qwt.QwtPainter.metricsMap().screenToLayoutX(self.symbolSizes[i])
          sizey = Qwt.QwtPainter.metricsMap().screenToLayoutY(self.symbolSizes[i])
        rect.setSize(Qt.QSize(sizex, sizey))

        xi = xMap.transform(self.x(i));
        yi = yMap.transform(self.y(i));
        rect.moveCenter(Qt.QPoint(xi, yi));
        if not self.symbolList is None:
          self.symbolList[i].draw(painter, rect);
        else:
          symbol.draw(painter, rect);
    # drawSymbols()

# class QwtPlotCurveSizes()

def make():
    demo = Qwt.QwtPlot()
    demo.setTitle('Symbols Demo')
    curve = QwtPlotCurveSizes()
    curve.attach(demo)
    curve_a = QwtPlotCurveSizes()
    curve_a.attach(demo)
    # need to create a default symbol for the curves due to inner
    # workings of QwtCurve 
    curve.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
             Qt.QBrush(Qt.Qt.black), Qt.QPen(Qt.Qt.black), Qt.QSize(5,5)))
    curve.setPen(Qt.QPen(Qt.Qt.blue, 2))
    curve_a.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
             Qt.QBrush(Qt.Qt.black), Qt.QPen(Qt.Qt.black), Qt.QSize(5,5)))
    curve_a.setPen(Qt.QPen(Qt.Qt.blue, 2))

    # create some data
    x_array = numpy.zeros(20, numpy.float32)
    y_array = numpy.zeros(20, numpy.float32)
    symbol_sizes = numpy.zeros(20, numpy.int32)
    symbolList=[]
    for i in range(20):
      x_array[i] = 1.0 * i
      y_array[i] = 2.0 * i
      symbol_sizes[i] = 3 + i
      if i%2 == 0:
        symbolList.append(Qwt.QwtSymbol(Qwt.QwtSymbol.UTriangle,
             Qt.QBrush(Qt.Qt.black), Qt.QPen(Qt.Qt.black), Qt.QSize(3+i,3+i)))
      else:
        symbolList.append(Qwt.QwtSymbol(Qwt.QwtSymbol.DTriangle,
             Qt.QBrush(Qt.Qt.red), Qt.QPen(Qt.Qt.red), Qt.QSize(3+i,3+i)))
    curve.setData(x_array,y_array,symbol_sizes)
    x_array = x_array + 10
    curve_a.setData(x_array,y_array)
    curve_a.setSymbolList(symbolList)
    grid = Qwt.QwtPlotGrid()
    grid.setMajPen(Qt.QPen(Qt.Qt.black, 0, Qt.Qt.DotLine))
    grid.setMinPen(Qt.QPen(Qt.Qt.gray, 0 , Qt.Qt.DotLine))

    grid.attach(demo)
    demo.replot()
    return demo

def main(args):
    app = Qt.QApplication(args)
    demo = make()
    demo.show()
#   app.setMainWidget(demo)
    app.exec_()

# Admire
if __name__ == '__main__':
    main(sys.argv)
