#!/usr/bin/python

# modules that are imported
import gridded_workspace
from app_browsers import *
from qt import *
from dmitypes import *
import sihippo
print "HippoDraw version " + sihippo.__version__
from sihippo import *
from numarray import *

class HippoArrayPlotter(BrowserPlugin):
  """ a class to plot raw arrays contained within a Meq tree """

  _icon = pixmaps.bars3d
  viewer_name = "Hippo Plotter";
  def is_viewable (data):
    return len(data) > 0;
  is_viewable = staticmethod(is_viewable);

  def __init__(self,parent,dataitem=None,**opts):
    """ instantiate various HippoDraw objects that are needed to
        control various aspects of plotting """

    self._ntuple_controller = NTupleController.instance()
    self._window_controller = WindowController.instance()
    self._window_controller.createInspector ()

# used for 'standalone display'
    self._window = CanvasWindow(None, "MeqDisplay",0)
    self._wtop = self._window

# have Hippo window close without asking permission to discard etc
    self._window.setAllowClose()
    self._window.show()
    self._display_controller = DisplayController.instance()
    self._canvas = None
    self._image_ntuple = None
    self._simple_ntuple = None

    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

  def __del__(self):
#    print "in destructor"
    self._window_controller.closeAllWindows()
                                                                                           
  def wtop (self):
    return self._wtop

  def display_data (self, plot_array):
    """ figure out shape, rank etc of an incoming array and
        plot it with an appropriate HippoDraw plot type """
# figure out type and rank of incoming array
    is_vector = False;
    array_dim = len(plot_array.shape)
    array_rank = plot_array.rank
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
        self._image_ntuple = self._ntuple_controller.createNTuple()
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
#        print "called self._canvas.addDisplay(xyz_plot)"
                                                                                
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
      real_array = dataitem.data.getreal()
      self._label = "real data value"
      self.display_data(real_array)
#extract imaginary component
      imag_array = dataitem.data.getimag()
      self._label = "imag data value"
      self.display_data(imag_array)
    else:
      self._label = "real data value"
      self.display_data(dataitem.data)
    
gridded_workspace.registerViewer(array_class,HippoArrayPlotter,priority=-10)
