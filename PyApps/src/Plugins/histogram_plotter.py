#!/usr/bin/python

# modules that are imported
from Timba.dmi import *
from Timba import utils
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI import widgets
from Timba.GUI.browsers import *
from Timba import Grid

from Timba.Plugins.display_image import *

from qt import *
from numarray import *


class HistogramPlotter(GriddedPlugin):
  """ a class to plot very simple histograms of array data distributions """

  _icon = pixmaps.bars3d
  viewer_name = "Histogram Plotter";
  def is_viewable (data):
    return len(data) > 0;
  is_viewable = staticmethod(is_viewable);

  def __init__(self,gw,dataitem,cellspec={},**opts):
    GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);

# create the plotter
    self._plotter = QwtImagePlot('histogram', self.wparent())
    self._plotter.show()
    self.set_widgets(self._plotter,dataitem.caption,icon=self.icon());

    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

#  def __del__(self):
#    print "in destructor"
                                                                                           
  def wtop (self):
    return self._plotter

  def set_data (self,dataitem,default_open=None,**opts):
    """ this function is the callback interface to the meqbrowser and
        handles new incoming data for the histogram """

    self._plotter.histogram_plot('data', dataitem.data)

# enable & highlight the cell
    self.enable();
    self.flash_refresh();
    
Grid.Services.registerViewer(array_class,HistogramPlotter,priority=15)
