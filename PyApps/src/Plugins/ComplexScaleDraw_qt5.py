# -*- coding: utf-8 -*-
#/usr/bin/env python

#% $Id: display_image.py 6838 2009-03-08 06:21:51Z twillis $


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
#  You should have received a copy	 Vous devez avoir recu une copie
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
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys
import numpy

from qwt.qt.QtGui import QApplication, QPen
from qwt.qt.QtCore import Qt
from qwt import (QwtPlot, QwtPlotMarker, QwtPlotGrid, QwtPlotCurve,
                 QwtScaleMap, QwtScaleDraw, QwtScaleDiv)


class ComplexScaleDraw(QwtScaleDraw):
    """ override default behaviour of QwtScaleDraw class """
    def __init__(self,start_value=None,end_value=None, divisor=None):
        QwtScaleDraw.__init__(self)
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
        return QwtScaleDraw.label(self, v)

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
        majLen = QwtScaleDraw.tickLength(self,QwtScaleDiv.MajorTick)
        medLen = QwtScaleDraw.tickLength(self,QwtScaleDiv.MediumTick)
        minLen = QwtScaleDraw.tickLength(self,QwtScaleDiv.MinorTick)
        #print('majLen medLen ', majLen, ' ', medLen, ' ', minLen)
        #print('lengths ', majLen,' ', medLen,' ', minLen)
        self.offset = 0
        scldiv = QwtScaleDraw.scaleDiv(self)
        # plot major ticks
        # Sometimes, for reasons deep inside Qwt, major_ticks seems to be 
        # returned as a null list for reasons I don't understand
        major_ticks = scldiv.ticks(QwtScaleDiv.MajorTick)
        #print('major ticks ', major_ticks)
        major_step = 0.0
        try:
          major_step = major_ticks[1] - major_ticks[0]
        except:
          pass
        major_count = len(major_ticks)
        for i in range(major_count):
            val = major_ticks[i]
            #print('initial major val = ', val)
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
            #print('final major val = ', val)
            QwtScaleDraw.drawTick(self, painter, val, minLen)
            QwtScaleDraw.drawLabel(self, painter, val)

        # also, optionally plot a major tick at the dividing point
        if self.do_separator:
          QwtScaleDraw.drawTick(self,painter, self.separator, majLen)
          QwtScaleDraw.drawLabel(self,painter,self.separator)


        # Sometimes, for reasons deep inside Qwt, minor_ticks seems to be 
        # returned as a null list for reasons I don't understand
        minor_ticks = scldiv.ticks(QwtScaleDiv.MinorTick)
        minor_step = 0.0
        try:
          minor_step = minor_ticks[1] - minor_ticks[0]
        except:
          pass
        minor_count = len(minor_ticks)

        # can't handle logs properly, but so what?
#       if scldiv.logScale():
#           pass
#           for i in range(scldiv.minCnt()):
#               QwtScaleDraw.drawTick(
#                   self, painter, scldiv.minMark(i), minLen)
#       else:
        if True:
            minor_ticks = scldiv.ticks(QwtScaleDiv.MinorTick)
            #print('minor ticks ', minor_ticks)
            medium_ticks = scldiv.ticks(QwtScaleDiv.MediumTick)
            #print('medium ticks ', medium_ticks)
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
                        QwtScaleDraw.drawTick(self,painter, val, medLen)
                    else:
                        QwtScaleDraw.drawTick(self, painter, val, minLen)

        if QwtScaleDraw.Backbone:
            QwtScaleDraw.drawBackbone(self, painter)
    # draw()
# class ComplexScaleDraw()

# stuff for testing
def main(args):
    app = QApplication(args)
    demo = QwtPlot()
    grid = QwtPlotGrid()
    grid.attach(demo)
    grid.setPen(QPen(Qt.black, 0,Qt.DotLine))
    grid.enableX(True)
    grid.enableY(True)
    complex_divider = 50.0

    myXScale = ComplexScaleDraw(start_value=0.0, end_value=complex_divider)
    #print('myXScale', myXScale)
    demo.setAxisScaleDraw(QwtPlot.xBottom, myXScale)

    m = QwtPlotMarker()
    m.attach(demo)
    m.setValue(complex_divider, 0.0)
    m.setLineStyle(QwtPlotMarker.VLine)
    m.setLabelAlignment(Qt.AlignRight | Qt.AlignBottom)
    m.setLinePen(QPen(Qt.black, 2, Qt.SolidLine))

    vector_array = numpy.zeros((100,), numpy.float32)
    for i in range(100):
      vector_array[i] = i

    curve = QwtPlotCurve('example data')
    curve.attach(demo)
    x_array = numpy.zeros(100, numpy.float32)
    y_array = numpy.zeros(100, numpy.float32)
    for i in range(100):
      x_array[i] = 1.0 * i
      y_array[i] = 2.0 * i
    curve.setSamples(x_array,y_array)

    demo.resize(600, 400)
    demo.replot()
    demo.show()
#   app.setMainWidget(demo)
    app.exec_()
# main()

if __name__ == '__main__':
    main(sys.argv)
