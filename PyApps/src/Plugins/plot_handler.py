#!/usr/bin/python

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

# these functions create / delete various widgets related
# to plotting. I've tried to collect all such operations
# into one file so that maintenance is easy.


# modules that are imported
from Timba import utils
from Timba.GUI import widgets

from qt import *

global has_vtk
has_vtk = False
try:
  from Timba.Plugins.vtk_qt_3d_display import *
  has_vtk = True
except:
  pass

from display_image import *
from QwtColorBar import *
from ND_Controller import *
from plot_printer import *

from Timba.utils import verbosity
_dbg = verbosity(0,name='plot_handler');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class plot_handler:

  def __init__(self):
    self.colorbar = None
    self.visu_plotter = None
    self.twoD_plotter = None
    self.plotPrinter = None
    self.ND_plotter = None
    self.layout = None
    self.layout_parent = None
    self.ND_Controls_2D = None  # used to select surfaces for 2D display
    self.ND_Controls_3D = None  # used to select cube for 3D display
    self.array_selector_2D = None
    self.array_selector_3D = None

  def store_layout_info(self, layout,layout_parent):
    self.layout = layout
    self.layout_parent  = layout_parent 

  def create_ColorBar (self):
    """ this function adds a colorbar for 2-D displays. 
        We create two color bars in case we are displaying complex arrays. 
    """
    if self.colorbar is None:
      self.colorbar = {}
      for i in range(2):
        self.colorbar[i] =  QwtColorBar(colorbar_number= i, parent=self.layout_parent)
        self.colorbar[i].setMaxRange((-1, 1))
        QObject.connect(self.twoD_plotter, PYSIGNAL('max_image_range'), self.colorbar[i].setMaxRange) 
        QObject.connect(self.twoD_plotter, PYSIGNAL('display_type'), self.colorbar[i].setDisplayType) 
        QObject.connect(self.twoD_plotter, PYSIGNAL('show_colorbar_display'), self.colorbar[i].showDisplay)
        QObject.connect(self.colorbar[i], PYSIGNAL('set_image_range'), self.twoD_plotter.setImageRange) 
        if i == 0:
          self.layout.addWidget(self.colorbar[i], 0, i)
          self.colorbar[i].show()
        else:
          self.layout.addWidget(self.colorbar[i], 0, 2)
          self.colorbar[i].hide()
      if not self.plotPrinter is None:
        self.plotPrinter.add_colorbar(self.colorbar)
      return self.colorbar

  def hide_2D_Plotters(self):
    """ delete 2D plotter and associated colorbars """
    _dprint(3, 'got 3d plot request, deleting 2-d stuff')
    if not self.colorbar is None:
      self.colorbar[0].hide()
      self.colorbar[1].hide()
      print 'issued hide command to colorbars'
    if not self.twoD_plotter is None:
      self.twoD_plotter.hide()
    if not self.ND_Controls_2D is None:
      self.ND_Controls_2D.hide()
      print 'issued hide command to twoD_plotter'

  def show_2D_Plotters(self):
    """ show 2D plotter and associated colorbars """
    if not self.ND_plotter is None:
      self.ND_plotter.delete_vtk_renderer()
      self.ND_plotter.hide_vtk_controls()
    if not self.ND_Controls_3D is None:
      self.ND_Controls_3D.hide()

    if not self.colorbar is None:
      self.colorbar[0].unHide()
      self.colorbar[1].unHide()
      print 'issued show command to colorbars'
    if not self.twoD_plotter is None:
      self.twoD_plotter.show()
    print 'issued show command to twoD_plotter'

  def create_array_selector(self, rank, shape, first_axis,second_axis,third_axis=-1,selector_2D=True):
    """ create subarray selection to be extracted from ND array for display """
    if not self.twoD_plotter is None:
      self.twoD_plotter.delete_cross_sections()
    if first_axis is None:
      first_axis = -1
    if third_axis is None:
      third_axis = -1
    array_selector = []
    for i in range(rank):
      if i == first_axis:
        axis_slice = slice(0,shape[first_axis])
        array_selector.append(axis_slice)
      elif i == second_axis:
        axis_slice = slice(0,shape[second_axis])
        array_selector.append(axis_slice)
      elif i == third_axis:
        axis_slice = slice(0,shape[third_axis])
        array_selector.append(axis_slice)
      else:
        array_selector.append(0)
    if selector_2D:
      self.array_selector_2D = array_selector
    else:
      self.array_selector_3D = array_selector
    return array_selector

  def create_2D_Plotters(self):
    """ create 2D plotter """
    if not self.ND_plotter is None:
      self.ND_plotter.delete_vtk_renderer()
      self.ND_plotter.hide_vtk_controls()
    if self.twoD_plotter is None:
      self.twoD_plotter = QwtImageDisplay('spectra',parent=self.layout_parent)
      self.layout.addWidget(self.twoD_plotter, 0, 1)
      self.plotPrinter = plot_printer(self.twoD_plotter)
      QObject.connect(self.twoD_plotter, PYSIGNAL('show_ND_Controller'), self.ND_controller_2D_showDisplay)
      QObject.connect(self.twoD_plotter, PYSIGNAL('do_print'), self.plotPrinter.do_print)
      QObject.connect(self.twoD_plotter, PYSIGNAL('colorbar_needed'), self.create_ColorBar)
      self.twoD_plotter.show()
    return self.twoD_plotter, self.plotPrinter

  def create_ND_Plotter (self):
    """ create a new ND plotter """

    if self.ND_plotter is None:
      self.ND_plotter = vtk_qt_3d_display(self.layout_parent)
      QObject.connect(self.ND_plotter, PYSIGNAL('show_ND_Controller'), self.ND_controller_3D_showDisplay)

      self.layout.addMultiCellWidget(self.ND_plotter,1,1,0,2)
      self.ND_plotter.show()
      _dprint(3, 'issued show call to ND_plotter')
      return self.ND_plotter

  def create_array_selector(self, rank, shape, first_axis,second_axis,third_axis=-1):
    """ create subarray selection to be extracted from ND array for display """
    if not self.twoD_plotter is None:
      self.twoD_plotter.delete_cross_sections()
    if first_axis is None:
      first_axis = -1
    if third_axis is None:
      third_axis = -1
    array_selector = []
    for i in range(rank):
      if i == first_axis:
        axis_slice = slice(0,shape[first_axis])
        array_selector.append(axis_slice)
      elif i == second_axis:
        axis_slice = slice(0,shape[second_axis])
        array_selector.append(axis_slice)
      elif i == third_axis:
        axis_slice = slice(0,shape[third_axis])
        array_selector.append(axis_slice)
      else:
        array_selector.append(0)
    return array_selector

  def create_ND_Controls(self, array_shape, labels=None, parms=None, num_axes=2):
    """ this function adds the extra GUI control buttons etc if we are
        displaying data for a numpy array of dimension 3 or greater 
    """
    if num_axes == 2:
      if not self.ND_Controls_3D is None:
        self.ND_Controls_3D.hide()
      if self.ND_Controls_2D is None:
        self.ND_Controls_2D = ND_Controller(array_shape, labels, parms, num_axes,self.layout_parent)
        self.layout.addMultiCellWidget(self.ND_Controls_2D,2,2,0,2)
        if self.ND_Controls_2D.get_num_selectors() > num_axes:
          self.ND_Controls_2D.showDisplay(1)
        else:
          self.ND_Controls_2D.showDisplay(0)
        print 'created self.ND_Controls_2D ', self.ND_Controls_2D
      return self.ND_Controls_2D

    if num_axes == 3: 
      if not self.ND_Controls_2D is None:
        self.ND_Controls_2D.hide()
        print 'should have hidden self.ND_Controls_2D '
      if self.ND_Controls_3D is None:
        self.ND_Controls_3D = ND_Controller(array_shape, labels, parms, num_axes,self.layout_parent)
        self.layout.addMultiCellWidget(self.ND_Controls_3D,3,3,0,2)
        if self.ND_Controls_3D.get_num_selectors() > num_axes:
          self.ND_Controls_3D.showDisplay(1)
        else:
          self.ND_Controls_3D.showDisplay(0)
        if not self.ND_plotter is None:
          self.ND_plotter.HideNDButton()
      return self.ND_Controls_3D

  def ND_controller_3D_showDisplay(self, show_self):
    """ tells ND_Controller to show or hide itself """
    if not self.ND_Controls_3D is None:
      self.ND_Controls_3D.showDisplay(show_self)

  def ND_controller_2D_showDisplay(self, show_self):
    """ tells ND_Controller to show or hide itself """
    if not self.ND_Controls_2D is None:
      self.ND_Controls_2D.showDisplay(show_self)

def main(args):
  return
# main()

# test
if __name__ == '__main__':
    main(sys.argv)
