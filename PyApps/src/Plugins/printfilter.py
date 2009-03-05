#!/usr/bin/python


#% $Id: printfilter.py 4329 2006-12-14 17:27:23Z twillis $ 

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

# this code is taken from the PyQwt BodeDemo.py example

from qt import *
import Qwt5 as Qwt

class PrintFilter(Qwt.QwtPlotPrintFilter):
    def __init__(self):
        Qwt.QwtPlotPrintFilter.__init__(self)

    # __init___()
    
#   def color(self, c, item, i):
    def color(self, c, item):
        if not (self.options() & Qwt.QwtPlotPrintFilter.PrintCanvasBackground):
            if item == Qwt.QwtPlotPrintFilter.MajorGrid:
                return Qt.darkGray
            elif item == Qwt.QwtPlotPrintFilter.MinorGrid:
                return Qt.gray
        if item == Qwt.QwtPlotPrintFilter.Title:
            return Qt.red
        elif item == Qwt.QwtPlotPrintFilter.AxisScale:
            return Qt.green
        elif item == Qwt.QwtPlotPrintFilter.AxisTitle:
            return Qt.blue
        return c

    # color()

#   def font(self, f, item, i):
    def font(self, f, item):
        result = QFont(f)
        result.setPointSize(int(f.pointSize()*1.25))
        return result

    # font()

# class PrintFilter

