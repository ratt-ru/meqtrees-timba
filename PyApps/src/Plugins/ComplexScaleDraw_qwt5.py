#% $Id: ComplexScaleDraw.py 5418 2007-07-19 16:49:13Z oms $ 

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

import sys
from qt import *
import Qwt5 as Qwt
import numpy

class ComplexScaleDraw(Qwt.QwtScaleDraw):
    """ override default behaviour of QwtScaleDraw class """
    def __init__(self,start_value=None,end_value=None, divisor=None):
        Qwt.QwtScaleDraw.__init__(self)
        self.do_separator = True
        self.start_value = start_value
        self.end_value = end_value
        self.divisor = divisor
        if not self.start_value is None and not self.end_value is None:
          self.delta = self.end_value - self.start_value
          self.separator = self.end_value
          self.divisor = None
        else:
          self.separator = self.divisor
          self.delta = None
          self.start_value = None
          self.end_value = None

    # __init__()

    def label(self, v):
        """ Override default QwtScaleDraw generation of labels along axis """
        if not self.end_value is None:
          if v >= self.end_value:
              v = v - self.delta
        else:
          if not self.divisor is None:
            v = v % self.divisor
        return Qwt.QwtScaleDraw.label(self, v)

    def draw_separator(self, separator_flag=True):
        """ test to draw major tick mark at separation location """
        self.do_separator = separator_flag

    def draw(self, painter, dummy):
        # for some reason, in qwt 5 an extra parameter is needed
        # in the above function definition. The corresponding
        # C++ code offers several possibilities, but just a 'dummy'
        # seems adequate ....
        # 1. paint real value ticks as done in C++ code
        # 2. paint imag value ticks with the shift depending on
        #    the dimension and tick spacing
        # 3. draw backbone, if needed

        step_eps = 1.0e-6    # constant value in the c++ equivalent
        majLen = Qwt.QwtScaleDraw.tickLength(self,Qwt.QwtScaleDiv.MajorTick)
        medLen = Qwt.QwtScaleDraw.tickLength(self,Qwt.QwtScaleDiv.MediumTick)
        minLen = Qwt.QwtScaleDraw.tickLength(self,Qwt.QwtScaleDiv.MinorTick)
#       print 'majLen medLen ', majLen, ' ', medLen, ' ', minLen
#       print 'lengths ', majLen,' ', medLen,' ', minLen
#       minLen = Qwt.QwtScaleDraw.tickLength(self)
        self.offset = 0
        scldiv = Qwt.QwtScaleDraw.scaleDiv(self)
        # plot major ticks
        major_ticks = scldiv.ticks(Qwt.QwtScaleDiv.MajorTick)
        major_step = major_ticks[1] - major_ticks[0]
        major_count = len(major_ticks)
        for i in range(major_count):
            val = major_ticks[i]
#           print 'initial major val = ', val
            if not self.end_value is None:
              v = val
              if val >= self.end_value:
                v = val - self.delta
            else:
              if not self.divisor is None:
                v = val % self.divisor
            if self.offset == 0 and v != val:
                self.offset = major_step - v % major_step
            val = val + self.offset
#           print 'final major val = ', val
            Qwt.QwtScaleDraw.drawTick(self, painter, val, minLen)
            Qwt.QwtScaleDraw.drawLabel(self, painter, val)

        # also, optionally plot a major tick at the dividing point
        if self.do_separator:
          Qwt.QwtScaleDraw.drawTick(self,painter, self.separator, majLen)
          Qwt.QwtScaleDraw.drawLabel(self,painter,self.separator)

        # plot medium ticks
#       medium_ticks = scldiv.ticks(Qwt.QwtScaleDiv.MediumTick)
#       medium_step = medium_ticks[1] - medium_ticks[0]
#       medium_count = len(medium_ticks)
#       self.offset = 0
#       print '\n\n'
#       for i in range(medium_count):
#           val = medium_ticks[i]
#           print 'initial medium val = ', val
#           v = val 
#           if val >= self.end_value:
#               v = val - self.delta 
#           if self.offset == 0 and v != val:
#               self.offset = medium_step - v % medium_step
#           val = val + self.offset
#           print 'final medium val = ', val
#           Qwt.QwtScaleDraw.drawTick(self, painter, val, medLen)
#           Qwt.QwtScaleDraw.drawLabel(self, painter, val)

        minor_ticks = scldiv.ticks(Qwt.QwtScaleDiv.MinorTick)
        minor_step = minor_ticks[1] - minor_ticks[0]
        minor_count = len(minor_ticks)
#       self.offset = 0
#       print '\n\n'
#       for i in range(minor_count):
#           val = minor_ticks[i]
#           print 'initial minor val = ', val
#           v = val 
#           if val >= self.end_value:
#               v = val - self.delta 
#           if self.offset == 0 and v != val:
#               self.offset = minor_step - v % minor_step
#           val = val + self.offset
#           print 'final minor val = ', val
#           Qwt.QwtScaleDraw.drawTick(self, painter, val, majLen)
#           Qwt.QwtScaleDraw.drawLabel(self, painter, val)

        # can't handle logs properly, but so what?
#       if scldiv.logScale():
#           pass
#           for i in range(scldiv.minCnt()):
#               Qwt.QwtScaleDraw.drawTick(
#                   self, painter, scldiv.minMark(i), minLen)
#       else:
        if True:
            minor_ticks = scldiv.ticks(Qwt.QwtScaleDiv.MinorTick)
#           print 'minor ticks ', minor_ticks
            medium_ticks = scldiv.ticks(Qwt.QwtScaleDiv.MediumTick)
#           print 'medium ticks ', medium_ticks
            kmax = major_count - 1
            if kmax > 0:
                majTick = major_ticks[0]
                hval = majTick - 0.5 * major_step
                k = 0
                for i in range(minor_count):
                    val = minor_ticks[i]
                    if  val > majTick:
                        if k < kmax:
                            k = k + 1
                            majTick = major_ticks[k]
                        else:
                            majTick += (major_ticks[kmax]
                                        + major_step)
                        hval = majTick - 0.5 * major_step
                    if abs(val-hval) < step_eps * major_step:
                        Qwt.QwtScaleDraw.drawTick(self,painter, val, medLen)
                    else:
                        Qwt.QwtScaleDraw.drawTick(self, painter, val, minLen)

#       if Qwt.QwtScaleDraw.options(self) & Qwt.QwtScaleDraw.Backbone:
        if Qwt.QwtScaleDraw.Backbone:
            Qwt.QwtScaleDraw.drawBackbone(self, painter)
    # draw()
# class ComplexScaleDraw()

# stuff for testing
def main(args):
    app = QApplication(args)
    demo = Qwt.QwtPlot()
    grid = Qwt.QwtPlotGrid()
    grid.attach(demo)
    grid.setPen(QPen(Qt.black, 0, Qt.DotLine))
    grid.enableX(True)
    grid.enableY(True)
    complex_divider = 50.0

    myXScale = ComplexScaleDraw(start_value=0.0, end_value=complex_divider)
    demo.setAxisScaleDraw(Qwt.QwtPlot.xBottom, myXScale)

    m = Qwt.QwtPlotMarker()
    m.attach(demo)
    m.setValue(complex_divider, 0.0)
    m.setLineStyle(Qwt.QwtPlotMarker.VLine)
    m.setLabelAlignment(Qt.AlignRight | Qt.AlignBottom)
    m.setLinePen(QPen(Qt.black, 2, Qt.SolidLine))

    vector_array = numpy.zeros((100,), numpy.float32)
    for i in range(100):
      vector_array[i] = i

    curve = Qwt.QwtPlotCurve()
    curve.attach(demo)
    x_array = numpy.zeros(100, numpy.float32)
    y_array = numpy.zeros(100, numpy.float32)
    for i in range(100):
      x_array[i] = 1.0 * i
      y_array[i] = 2.0 * i
    curve.setData(x_array,y_array)

    demo.resize(600, 400)
    demo.replot()
    demo.show()
    app.setMainWidget(demo)
    app.exec_loop()
# main()

if __name__ == '__main__':
    main(sys.argv)
