#!/usr/bin/python

# modules that are imported
import gridded_workspace
from app_browsers import *
from qt import *
from dmitypes import *
from numarray import *
from display_image import *

class ArrayPlotter(BrowserPlugin):
  """ a class to plot raw arrays contained within a Meq tree """

  _icon = pixmaps.bars3d
  viewer_name = "Array Plotter";
  def is_viewable (data):
    return len(data) > 0;
  is_viewable = staticmethod(is_viewable);

  def __init__(self,parent,dataitem=None,**opts):
    """ instantiate various HippoDraw objects that are needed to
        control various aspects of plotting """

# create the plotter
    self._plotter = QwtImagePlot('plot_key', parent)
    self._plotter.show()

    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

#  def __del__(self):
#    print "in destructor"
                                                                                           
  def wtop (self):
    return self._plotter

  def set_data (self,dataitem,default_open=None,**opts):
    """ this function is the callback interface to the meqbrowser and
        handles new incoming data """

    self._plotter.array_plot('data', dataitem.data)
    
gridded_workspace.registerViewer(array_class,ArrayPlotter,priority=-10)
