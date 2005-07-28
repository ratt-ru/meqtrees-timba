#!/usr/bin/python

# modules that are imported
from Timba.dmi import *
from Timba import utils
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI import widgets
from Timba.GUI.browsers import *
from Timba import Grid

from Timba.Plugins.display_image import *

from numarray import *
from qt import *
from qwt import *
from QwtPlotImage import *
from QwtColorBar import *

from vtk_qt_3d_display import *


class ArrayPlotter(GriddedPlugin):
  """ a class to plot raw arrays contained within a Meq tree """

  _icon = pixmaps.bars3d
  viewer_name = "Array Plotter";
  def is_viewable (data):
    return len(data) > 0;
  is_viewable = staticmethod(is_viewable);

  def __init__(self,gw,dataitem,cellspec={},**opts):
    GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);

# now create plotter and colorbar

# first figure out the actual rank of the array we are plotting
    self.rank = 0
    shape = dataitem.data.shape
    for i in range(len(shape)):
      if shape[i] > 1:
        self.rank = self.rank + 1
    self.layout = None
    if self.rank < 3:
      if self.rank == 2:
        self.layout = QHBox(self.wparent())
        self.colorbar =  QwtColorBar(parent=self.layout)
        self.colorbar.setRange(-1,1)
        self.colorbar.hide()
        self._plotter = QwtImageDisplay('spectra',parent=self.layout)
        QObject.connect(self._plotter, PYSIGNAL('image_range'), self.colorbar.setRange) 
        QObject.connect(self._plotter, PYSIGNAL('max_image_range'), self.colorbar.setMaxRange) 
        QObject.connect(self._plotter, PYSIGNAL('display_type'), self.colorbar.setDisplayType) 
        QObject.connect(self._plotter, PYSIGNAL('show_colorbar_display'), self.colorbar.showDisplay)
        QObject.connect(self.colorbar, PYSIGNAL('set_image_range'), self._plotter.setImageRange)

      else:
        self._plotter = QwtImageDisplay('spectra',parent=self.wparent())
    else:
      self._plotter = vtk_qt_3d_display(self.wparent())
    self._plotter.show()
    if self.layout is None:
      self.set_widgets(self._plotter,dataitem.caption,icon=self.icon());
    else:
      self.set_widgets(self.layout,dataitem.caption,icon=self.icon());

    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

#  def __del__(self):
#    print "in destructor"
                                                                                           
  def wtop (self):
    return self.layout

  def set_data (self,dataitem,default_open=None,**opts):
    """ this function is the callback interface to the meqbrowser and
        handles new incoming data """

# pass array to the plotter
    self._plotter.array_plot('data', dataitem.data)

# enable & highlight the cell
    self.enable();
    self.flash_refresh();
    
Grid.Services.registerViewer(array_class,ArrayPlotter,priority=10)
