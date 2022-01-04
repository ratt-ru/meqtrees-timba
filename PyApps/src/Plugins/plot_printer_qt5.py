#!/usr/bin/env python3


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

import printfilter_qt5

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
    height = (width // hor_widgets) * vert_widgets
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
        width = paint_device.width() // hor_widgets
        height = width # quadratically sized plots
      else:
        # height of plots in x-direction is the largest (wrt. paintdevice)
        height = paint_device.height() // hor_widgets
        width = height # quadratically sized plots
      if not self.colorbar is None:
        try:
          self.colorbar[0].print_(qpainter,
            Qt.QRect(0.02*width, 0, 0.12 * width, height), filter)
#         print 'colorbar plot succeeded'
        except:
          self.colorbar[0].printPlot(qpainter,
            Qt.QRect(0, 0, 0.12 * width, height), filter)
          print('colorbar plot excepted')
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
        print('main plot excepted')
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
