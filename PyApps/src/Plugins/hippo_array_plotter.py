#!/usr/bin/python

# modules that are imported

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

from Timba.dmi import *
from Timba import utils
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI import widgets
from Timba.GUI.browsers import *
from Timba import Grid

from qt import *
import sihippo
print "HippoDraw version " + sihippo.__version__
from sihippo import *
from Timba.array import *

from Timba.utils import verbosity
_dbg = verbosity(0,name='hippo_array_plotter');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class HippoArrayPlotter(GriddedPlugin):
  """ a class to plot raw arrays contained within a Meq tree """

  _icon = pixmaps.bars3d
  viewer_name = "Hippo Array Plotter";
  def is_viewable (data):
    return len(data) > 0;
  is_viewable = staticmethod(is_viewable);

  def __init__(self,gw,dataitem,cellspec={},**opts):
    GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);
    """ instantiate various HippoDraw objects that are needed to
        control various aspects of plotting """

    self._ntuple_controller = NTupleController.instance()
    self._window_controller = WindowController.instance()
    self._window_controller.createInspector ()

# used for 'standalone display'
    self._window = CanvasWindow(self.wparent(), "MeqDisplay",0)
    self.set_widgets(self._window,dataitem.caption,icon=self.icon())
    self._wtop = self._window

# have Hippo window close without asking permission to discard etc
    self._window.setAllowClose()
#    self._window.show()
    self._display_controller = DisplayController.instance()
    self._canvas = None
    self._image_ntuple = None
    self._simple_ntuple = None

    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

  def __del__(self):
    self._window_controller.closeAllWindows()
                                                                                           
  def wtop (self):
    return self._wtop

  def display_data (self, plot_array):
    """ figure out shape, rank etc of an incoming array and
        plot it with an appropriate HippoDraw plot type """
# figure out type and rank of incoming array
    is_vector = False;
    array_dim = len(plot_array.shape)
    array_rank = plot_array.ndim
    if array_rank == 1:
      is_vector = True;
    n_rows = plot_array.shape[0]
    if n_rows == 1:
      is_vector = True
    n_cols = 1
    if array_rank == 2:
      n_cols = plot_array.shape[1]
      if n_cols == 1:
        is_vector = True
    self._add_x_y = False;

# test if we have a 2-D array
    if is_vector == False:
# first display an image 
      if self._image_ntuple == None:
        print 'should bomb here'
        self._image_ntuple = self._ntuple_controller.createNTuple()
        print 'did not bomb'
        self._image_ntuple.setTitle ("Array Data")
        self._add_x_y = True;
      image_size = n_rows * n_cols
      image = []
      for j in range(0, n_rows ) :
        for i in range(0, n_cols) :
          image.append(plot_array[j][i])
      if self._image_ntuple.isValidLabel(self._label):
        self._image_ntuple.replaceColumn (self._label,image)
      else:
# add columns for new image data
        self._image_ntuple.addColumn (self._label,image)
# add time and frequency columns for xyz plots
# first add x column
        if self._add_x_y:
          xyz_x_label = "x"
          image = []
          for j in range(0, n_rows ) :
            for i in range(0, n_cols) :
              image.append(j)
          self._image_ntuple.addColumn (xyz_x_label, image)
# then add y column
          xyz_y_label = "y"
          image = []
          for j in range(0, n_rows ) :
            for i in range(0, n_cols) :
              image.append(i)
          self._image_ntuple.addColumn (xyz_y_label, image)
          self._add_x_y = False

# do image plot
        image_plot = self._display_controller.createDisplay( 'Z Plot', self._image_ntuple,[self._label,])
        image_plot.setLabel ( 'x', 'x' )
        image_plot.setLabel ( 'y', 'y' )
        image_plot.setNumberOfBins ( 'x', n_rows )
        image_plot.setNumberOfBins ( 'y', n_cols )
        if self._canvas == None:
          self._canvas = self._window_controller.currentCanvas()
        self._canvas.addDisplay ( image_plot ) 

# now do an XYZ plot
# comment this out for the moment ...
#        bindings = ["x", "y",  self._label ]
#        xyz_plot = self._display_controller.createDisplay ( 'XYZ Plot', self._image_ntuple, bindings )
#        xyz_plot.setLabel ( 'x', 'x' )
#        xyz_plot.setLabel ( 'y', 'y' )
#        if self._canvas == None:
#          self._canvas = self._window_controller.currentCanvas()
#        self._canvas.addDisplay ( xyz_plot )
                                                                                
    if is_vector == True:
      if self._simple_ntuple == None:
# do X-Y plot
        self._simple_ntuple = self._ntuple_controller.createNTuple()
        self._simple_ntuple.setTitle ( "Array Data" )
        self._add_x = True
      image = []
      if n_rows > 1:
        for j in range(0, n_rows) :
         if array_rank == 2:
           image.append(plot_array[j][0])
         else:
           image.append(plot_array[j])
      if n_cols > 1:
        for j in range(0, n_cols) :
         if array_rank == 2:
           image.append(plot_array[0][j])
         else:
           image.append(plot_array[j])
      if self._simple_ntuple.isValidLabel(self._label):
        self._simple_ntuple.replaceColumn (self._label,image)
      else:
# add columns for new image data
        self._simple_ntuple.addColumn (self._label,image)
# first add x column
        if self._add_x:
          image = []
          if n_cols > 1:
            for j in range(0, n_cols ) :
              image.append(j)
          if n_rows > 1:
            for j in range(0, n_rows ) :
              image.append(j)
          self._simple_ntuple.addColumn ("x", image)
          self._add_x = False
        plot = self._display_controller.createDisplay ( 'XY Plot', self._simple_ntuple, ["x",self._label] )
        if self._canvas == None:
          self._canvas = self._window_controller.currentCanvas()
        self._canvas.addDisplay ( plot )

  def set_data (self,dataitem,default_open=None,**opts):
    """ this function is the callback interface to the meqbrowser and
        handles new incoming data """

# is incoming array real or complex?
    complex_type = False;
    if dataitem.data.type() == Complex32:
      complex_type = True;
    if dataitem.data.type() == Complex64:
      complex_type = True;

    if complex_type:
#extract real component
      real_array = dataitem.data.real
      self._label = "real data value"
      self.display_data(real_array)
#extract imaginary component
      imag_array = dataitem.data.imag
      self._label = "imag data value"
      self.display_data(imag_array)
    else:
      self._label = "real data value"
      self.display_data(dataitem.data)

# enable & highlight the cell
    self.enable();
    self.flash_refresh();

Grid.Services.registerViewer(array_class,HippoArrayPlotter,priority=11)

