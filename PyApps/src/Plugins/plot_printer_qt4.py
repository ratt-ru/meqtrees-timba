#!/usr/bin/python


#% $Id: plot_printer.py 6837 2009-03-05 19:00:25Z twillis $ 

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

from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt
import printfilter_qt4

class plot_printer:
  def __init__(self, plotter, colorbar=None):

    self.plotter = plotter
    self.colorbar = colorbar
  
# The following 3 functions are adapted from the 'scicraft'
# visualization package

  def _get_qpainter(self, qprinter, hor_widgets, vert_widgets):
    """Returns a qpainter using the given qprinter and geometry."""
    qpainter = Qt.QPainter(qprinter)
    paint_device = qpainter.device()
    width = paint_device.width()
    height = (width / hor_widgets) * vert_widgets
#   qpainter.setClipRect(0, 0, width, height, qpainter.CoordPainter)
    qpainter.setClipRect(0, 0, width, height)
    return qpainter

  def _print_plots(self, qprinter, filter, hor_widgets, vert_widgets, is_complex):
    """Prints all plots with the given qprinter.
    """
    qpainter = self._get_qpainter(qprinter, hor_widgets, vert_widgets)
    # get width and height for each plot 
    paint_device = qpainter.device()
    if hor_widgets > 1:
      if paint_device.width() > paint_device.height():
        # width of plots in x-direction is the largest (wrt. paintdevice)
        width = paint_device.width() / hor_widgets
        height = width # quadratically sized plots
      else:
        # height of plots in x-direction is the largest (wrt. paintdevice)
        height = paint_device.height() / hor_widgets
        width = height # quadratically sized plots
      if not self.colorbar is None:
        try:
          self.colorbar[0].print_(qpainter,
            Qt.QRect(0.02*width, 0, 0.12 * width, height), filter)
#         print 'colorbar plot succeeded'
        except:
          self.colorbar[0].printPlot(qpainter,
            Qt.QRect(0, 0, 0.12 * width, height), filter)
          print 'colorbar plot excepted'
        if is_complex:
          try:
            self.colorbar[1].print_(qpainter,
              Qt.QRect(1.6* width, 0, 0.12 * width, height), filter)
          except:
            self.colorbar[1].printPlot(qpainter,
              Qt.QRect(1.6* width, 0, 0.12 * width, height), filter)
      try:
        self.plotter.print_(qpainter,
          Qt.QRect(0.16 * width, 0, 1.4 * width, height), filter)
#       print 'main plot succeeded'
      except:
        self.plotter.printPlot(qpainter,
          Qt.QRect(0.16 * width, 0, 1.4 * width, height), filter)
        print 'main plot excepted'
    else:
      width = paint_device.width()
      if width > paint_device.height():
        width =  paint_device.height()
      height = width
      try:
        self.plotter.print_(qpainter,
          Qt.QRect(0, 0, width, height), filter)
      except:
        self.plotter.printPlot(qpainter,
          Qt.QRect(0, 0, width, height), filter)
    qpainter.end()

  def do_print(self, is_single=True, is_complex=False):
    """Sends plots in this window to the printer.
    """
    printer = Qt.QPrinter(Qt.QPrinter.HighResolution)

    printer.setOutputFileName('image-plot-%s.ps' % Qt.qVersion())

#   printer.setCreator('Bode example')
    printer.setOrientation(Qt.QPrinter.Landscape)
    printer.setColorMode(Qt.QPrinter.Color)

    docName = self.plotter.title().text()
    if not docName.isEmpty():
#       docName.replace(Qt.QRegExp(Qt.QString.fromLatin1('\n')), self.tr(' -- '))
        printer.setDocName(docName)

    dialog = Qt.QPrintDialog(printer)
    if dialog.exec_():
        filter = printfilter_qt4.PrintFilter()
        if (Qt.QPrinter.GrayScale == printer.colorMode()):
            filter.setOptions(
                Qwt.QwtPlotPrintFilter.PrintAll
                & ~Qwt.QwtPlotPrintFilter.PrintBackground
                | Qwt.QwtPlotPrintFilter.PrintFrameWithScales)
            filter.setOptions(Qwt.QwtPlotPrintFilter.PrintAll)
# we have 'two' horizontal widgets - colorbar(s) and the display area
        hor_widgets = 2
        if is_single:
          hor_widgets = 1
        self._print_plots(printer, filter, hor_widgets, 1, is_complex)

  def add_colorbar(self, colorbar):
    self.colorbar = colorbar

# class plot_printer
