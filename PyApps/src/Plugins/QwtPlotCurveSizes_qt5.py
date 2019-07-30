# -*- coding: utf-8 -*-
#
# Licensed under the terms of the PyQwt License
# Copyright (C) 2003-2009 Gerard Vermeulen, for the original PyQwt example
# Copyright (c) 2015 Pierre Raybaut, for the PyQt5/PySide port and further 
# developments (e.g. ported to PythonQwt API)
# (see LICENSE file for more details)

import sys
import numpy

from qwt.qt.QtGui import QApplication, QPen, QBrush
from qwt.qt.QtCore import QSize, QSizeF, QRect, QRectF, QPoint, QPointF
from qwt.qt.QtCore import Qt
from qwt import QwtPlot, QwtSymbol, QwtPlotGrid, QwtPlotCurve, QwtText

class QwtPlotCurveSizes(QwtPlotCurve):
    def __init__(self, x=[], y=[], symbolSizes=None):

        QwtPlotCurve.__init__(self)
        
        self.symbolSizes = symbolSizes
        self.symbolList = None
        self.setData(x, y, symbolSizes)

    def setData(self, *args):
        if len(args) == 1:
            QwtPlotCurve.setData(self, *args)
            return
        x, y = args[:2]
        if len(args) > 2:
            self.symbolSizes = args[2]
        
        self.__x = numpy.asarray(x, numpy.float)
        if len(self.__x.shape) != 1:
            raise RuntimeError('len(asarray(x).shape) != 1')
        self.__y = numpy.asarray(y, numpy.float)
        if len(self.__y.shape) != 1:
            raise RuntimeError('len(asarray(y).shape) != 1')
        if len(self.__x) != len(self.__y):
            raise RuntimeError('len(asarray(x)) != len(asarray(y))')
        QwtPlotCurve.setData(self, self.__x, self.__y)

    def setSymbolList(self, symbolList):
      """ Override default QwtCurve symbols """
      self.symbolList = symbolList

    def drawSymbols(self, painter, symbol, xMap, yMap, canvasRect,from_, to):
      if self.symbolList is None and self.symbolSizes is None:
        print('QwtPlotCurveSizes fail: you must specify a symbol list or an array of symbol sizes')
        return
      painter.setBrush(symbol.brush());
      painter.setPen(symbol.pen())
      for i in range(from_, to+1):
        if not self.symbolList is None:
          painter.setBrush(self.symbolList[i].brush());
          painter.setPen(self.symbolList[i].pen())
        xi = xMap.transform(self.__x[i]);
        yi = yMap.transform(self.__y[i]);
        position = QPointF(float(xi), float(yi))
        if not self.symbolList is None:
          self.symbolList[i].drawSymbol(painter, position);
        else:
          symbol.setSize(QSize(self.symbolSizes[i],self.symbolSizes[i]))
          symbol.drawSymbol(painter, position);
    # drawSymbols()

# class QwtPlotCurveSizes()

def make():
    # create a plot with a white canvas
    demo = QwtPlot(QwtText("Curve Demonstation"))
#   demo.setCanvasBackground(Qt.white)
#   demo.plotLayout().setAlignCanvasToScales(True)

#   grid = QwtPlotGrid()
#   grid.attach(demo)
#   grid.setPen(QPen(Qt.black, 0, Qt.DotLine))
    
    # calculate data and errors for a curve with error bars
    x = numpy.zeros(20, numpy.float32)
    y = numpy.zeros(20, numpy.float32)
    symbol_sizes = numpy.zeros(20, numpy.int32)
    symbolList=[]
    for i in range(20):
      x[i] = 1.0 * i
      y[i] = 2.0 * i
      symbol_sizes[i] = 3 + i
      if i%2 == 0:
        symbolList.append(QwtSymbol(QwtSymbol.UTriangle,
             QBrush(Qt.black), QPen(Qt.black), QSize(3+i,3+i)))
      else:
        symbolList.append(QwtSymbol(QwtSymbol.DTriangle,
             QBrush(Qt.red), QPen(Qt.red), QSize(3+i,3+i)))

    curve = QwtPlotCurveSizes(x = x, y = y, symbolSizes = symbol_sizes)
    x = x + 10
    curve1 = QwtPlotCurveSizes(x= x, y = y, symbolSizes = symbol_sizes)
    curve.setSymbol(QwtSymbol(QwtSymbol.Ellipse,
             QBrush(Qt.black), QPen(Qt.black), QSize(5,5)))
    curve.setPen(QPen(Qt.blue, 2))
    curve1.setSymbol(QwtSymbol(QwtSymbol.Ellipse,
             QBrush(Qt.red), QPen(Qt.red), QSize(10,10)))
    curve1.setPen(QPen(Qt.blue, 2))
    curve1.setSymbolList(symbolList)

    curve.attach(demo)
    curve1.attach(demo)
    demo.resize(640, 480)
    demo.show()
    return demo


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = make()
    sys.exit(app.exec_())
