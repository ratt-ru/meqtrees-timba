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

# have Hippo window close without asking permission to discard etc

    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

  def __del__(self):
    print "in destructor"
                                                                                           
  def wtop (self):
    return self._plotter

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
#extract real and imaginary components
      real_array = dataitem.data.getreal()
      imag_array = dataitem.data.getimag()
      shape = real_array.shape
      temp_array = zeros((2*shape[0],shape[1]), Float32)
      for k in range(shape[0]):
        for j in range(shape[1]):
          temp_array[k,j] = real_array[k,j]
          temp_array[k+shape[0],j] = imag_array[k,j]
      self._plotter.array_plot('complex_data', temp_array)
    else:
      self._plotter.array_plot('real_data', dataitem.data)
    
gridded_workspace.registerViewer(array_class,ArrayPlotter,priority=-10)
