#!/usr/bin/python


#% $Id$ 

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

from qt import *
try:
  from Qwt4 import *
except:
  from qwt import *
import printfilter

class plot_printer:
  def __init__(self, plotter, colorbar=None):

    self.plotter = plotter
    self.colorbar = colorbar
  
# The following 3 functions are adapted from the 'scicraft'
# visualization package

  def _get_qpainter(self, qprinter, hor_widgets, vert_widgets):
    """Returns a qpainter using the given qprinter and geometry."""
    qpainter = QPainter(qprinter)
    metrics = QPaintDeviceMetrics(qpainter.device())
    width = metrics.width()
    height = (width / hor_widgets) * vert_widgets
    qpainter.setClipRect(0, 0, width, height, qpainter.CoordPainter)
    return qpainter

  def _print_plots(self, qprinter, filter, hor_widgets, vert_widgets, is_complex):
    """Prints all plots with the given qprinter.
    """
    qpainter = self._get_qpainter(qprinter, hor_widgets, vert_widgets)
    # get width and height for each plot 
    metrics = QPaintDeviceMetrics(qpainter.device())
    if hor_widgets > 1:
      if metrics.width() > metrics.height():
        # width of plots in x-direction is the largest (wrt. paintdevice)
        width = metrics.width() / hor_widgets
        height = width # quadratically sized plots
      else:
        # height of plots in x-direction is the largest (wrt. paintdevice)
        height = metrics.height() / hor_widgets
        width = height # quadratically sized plots
      if not self.colorbar is None:
        try:
          self.colorbar[0].print_(qpainter,
            QRect(0, 0, 0.12 * width, height), filter)
        except:
          self.colorbar[0].printPlot(qpainter,
            QRect(0, 0, 0.12 * width, height), filter)
        if is_complex:
          try:
            self.colorbar[1].print_(qpainter,
              QRect(1.6* width, 0, 0.12 * width, height), filter)
          except:
            self.colorbar[1].printPlot(qpainter,
              QRect(1.6* width, 0, 0.12 * width, height), filter)
      try:
        self.plotter.print_(qpainter,
          QRect(0.16 * width, 0, 1.4 * width, height), filter)
      except:
        self.plotter.printPlot(qpainter,
          QRect(0.16 * width, 0, 1.4 * width, height), filter)
    else:
      width = metrics.width()
      if metrics.width() > metrics.height():
        width =  metrics.height()
      height = width
      try:
        self.plotter.print_(qpainter,
          QRect(0, 0, width, height), filter)
      except:
        self.plotter.printPlot(qpainter,
          QRect(0, 0, width, height), filter)
    qpainter.end()

  def do_print(self, is_single, is_complex):
    """Sends plots in this window to the printer.
    """
    try:
        qprinter = QPrinter(QPrinter.HighResolution)
    except AttributeError:
        qprinter = QPrinter()
    qprinter.setOrientation(QPrinter.Landscape)
    qprinter.setColorMode(QPrinter.Color)
    qprinter.setOutputToFile(True)
    qprinter.setOutputFileName('image_plot.ps')
    if qprinter.setup():
        filter = printfilter.PrintFilter()
        if (QPrinter.GrayScale == qprinter.colorMode()):
            filter.setOptions(QwtPlotPrintFilter.PrintAll
                  & ~QwtPlotPrintFilter.PrintCanvasBackground)
# we have 'two' horizontal widgets - colorbar(s) and the display area
        hor_widgets = 2
        if is_single:
          hor_widgets = 1
        self._print_plots(qprinter, filter, hor_widgets, 1, is_complex)

  def add_colorbar(self, colorbar):
    self.colorbar = colorbar

# class plot_printer
