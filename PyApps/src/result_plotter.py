#!/usr/bin/python

# modules that are imported
from math import sin
from math import cos
from math import pow
from math import sqrt
import gridded_workspace
from app_browsers import *
from qt import *
from dmitypes import *
import sihippo
print "HippoDraw version " + sihippo.__version__
from sihippo import *
from numarray import *
from display_image import *
from realvsimag import *


_dbg = verbosity(0,name='result_plotter');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;


class ResultPlotter(BrowserPlugin):
  """ a class to visualize data, VellSets or visu data, that is 
      contained within a node's cache_result record. Objects of 
      this class are launched from the meqbrowser GUI """

  _icon = pixmaps.bars3d
  viewer_name = "Result Plotter";
  def is_viewable (data):
    return len(data) > 0;
  is_viewable = staticmethod(is_viewable);

  def __init__(self,parent,dataitem=None,default_open=None,**opts):
    """ Instantiate HippoDraw objects that are used to control
        various aspects of plotting
    """
    self._rec = None;
    self._hippo = None
# this QLabel is needed so that Oleg's browser is
# happy that a child is present
#    self._wtop = QLabel("",parent);
    self._visu_plotter = None
    self._parent = parent;
    self._wtop = None;

    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

  def __del__(self):
    self._window_controller.closeAllWindows()
                                                                                           
  def wtop (self):
    return self._wtop;
    
# used for 'embedded display'
#    return self._window

# used for 'standalone display'
#    return self._Qlabel

#
# tree traversal code adapted from the pasteur institute python 
# programming course chapter on recursive data structures at
# http://www.pasteur.fr/formation/infobio/python/ch13s03.html
#

  def do_prework(self, node):
# we check if a plotter has been constructed - 
    if isinstance(node, dict) and self._visu_plotter is None:
      if node.has_key('attrib'):
        _dprint(2,'length of attrib', len(node['attrib']));
        if len(node['attrib']) > 0:
          attrib_parms = node['attrib']
          plot_type = attrib_parms.get('plot_type')
          if plot_type == 'spectra':
            self._visu_plotter = QwtImagePlot(plot_type,parent=self._parent)
            self._wtop = self._visu_plotter;       # QwtImagePlot inherits from QwtPlot

          if plot_type == 'realvsimag':
            self._visu_plotter = realvsimag_plotter(plot_type,parent=self._parent)
            self._wtop = self._visu_plotter.plot;  # plot widget is our top widget

  def do_postwork(self, node):
    _dprint(3,"in postwork: do nothing at present");


  def is_leaf(self, node):
    if node.has_key('value'):
      candidate_leaf = node['value']
      if isinstance(candidate_leaf, list):
# check if list contents are a dict
        for i in range(len(candidate_leaf)):
           if isinstance(candidate_leaf[i], dict):
             return False
        return True
    else:
      return False

  def do_leafwork(self, leaf):
    self._visu_plotter.plot_data('item_label',leaf)

  def tree_traversal (self, node):
    _dprint(3,' ******* ');
    _dprint(3,'in tree traversal with node having length ', len(node));
    _dprint(3,' ******* ');
    if isinstance(node, dict):
      self.do_prework(node)
      if not self.is_leaf(node):
        if node.has_key('value'):
          self.tree_traversal(node['value'])
      else:
        self.do_leafwork(node)
#      self.do_postwork(node)
    if isinstance(node, list):
      for i in range(len(node)):
        if isinstance(node[i], dict):
          self.tree_traversal(node[i])

  def display_visu_data (self):
    """ extract group_label key from incoming visu data record and
      create a visu_plotter object to plot the data 
    """
# traverse the plot record tree and plot data
    self.tree_traversal( self._rec.visu)

  def display_vells_data (self, plot_array):
    """ extract parameters and data from an array that is
        part of a VellSet and plot the array """ 

# construct hippo window if it doesn't exist
    if self._hippo is None:
      self._ntuple_controller = NTupleController.instance()
      self._window_controller = WindowController.instance()
      self._window_controller.createInspector ()
      self._window = CanvasWindow(None, "MeqDisplay",0)
      self._window.setAllowClose()
      self._window.show()
      self._display_controller = DisplayController.instance()
      self._canvas = None
      self._image_ntuple = None
      self._simple_ntuple = None
      self._realvsimag_ntuple = None
      self._hippo = True

# figure out type and rank of incoming array
    array_dim = len(plot_array.shape)
    array_rank = plot_array.rank
#    print "array rank is ", array_rank
    is_vector = False;
    is_one_point_image = False;
    n_rows = plot_array.shape[0]
    if n_rows == 1:
      is_vector = True
    n_cols = 1
    if array_rank == 2:
      n_cols = plot_array.shape[1]
      if n_cols == 1:
        if n_rows == 1:
          is_vector = False
          is_one_point_image = True;
        else:
          is_vector = True
    self._add_time_freq = False;

    if is_vector == False:
# first display an image 
      if self._image_ntuple == None:
        self._image_ntuple = self._ntuple_controller.createNTuple()
        self._image_ntuple.setTitle ("VellSet Data")
        self._add_time_freq = True;
      image_size = n_rows * n_cols
      image = []
      for j in range(0, n_rows ) :
        for i in range(0, n_cols) :
#          print self._label, 'image appending ', plot_array[j][i]
          image.append(plot_array[j][i])
      if self._image_ntuple.isValidLabel(self._label):
        if len(image) != self._image_ntuple.rows():
          print "Number of rows has changed! Clearing tuple!"
          self._image_ntuple.clear()
        self._image_ntuple.replaceColumn (self._label,image)
      else:
# add columns for new image data
        self._image_ntuple.addColumn (self._label,image)
#        print "result_plotter added image column"
# add time and frequency columns for xyz plots
# first add frequency column
        if self._add_time_freq:
          xyz_x_label = "freq"
          image = []
          freq_range = self._rec.cells.domain.freq[1] - self._rec.cells.domain.freq[0]
          x_step = freq_range / n_rows
          start_freq = self._rec.cells.domain.freq[0] + 0.5 * x_step 
#          print self._label, 'image appending ', plot_array[j][i]
          for j in range(0, n_rows ) :
            for i in range(0, n_cols) :
              if n_rows == 1:
                current_freq = start_freq 
              else:
                current_freq = start_freq + j * x_step
              image.append(current_freq)
          self._image_ntuple.addColumn (xyz_x_label, image)

# now add time column
        if self._add_time_freq:
          xyz_y_label = "time"
          image = []
          time_range = self._rec.cells.domain.time[1] - self._rec.cells.domain.time[0]
          y_step = time_range / n_cols
          start_time = self._rec.cells.domain.time[0] + 0.5 * y_step 
          for j in range(0, n_rows ) :
            for i in range(0, n_cols) :
              if n_cols == 1:
                current_time = start_time 
              else:
                current_time = start_time + i * y_step
              image.append(current_time)
          self._image_ntuple.addColumn (xyz_y_label, image)
          self._add_time_freq = False

# do image plot 
        if is_one_point_image == False:
          image_plot = self._display_controller.createDisplay( 'Z Plot', self._image_ntuple,[self._label,])
          freq_range = self._rec.cells.domain.freq[1] - self._rec.cells.domain.freq[0]
          time_range = self._rec.cells.domain.time[1] - self._rec.cells.domain.time[0]
          y_step = time_range / n_cols
          x_step = freq_range / n_rows
          start_time = self._rec.cells.domain.time[0] 
          start_freq = self._rec.cells.domain.freq[0] 
          image_plot.setBinWidth ( 'x', x_step )
          image_plot.setBinWidth ( 'y', y_step )
          image_plot.setRange ( 'x', start_freq, start_freq + n_rows * x_step)
          image_plot.setRange ( 'y', start_time, start_time + n_cols * y_step)
          real_array = self._label.find("real")
          image_plot.setOffset ( 'x', start_freq )
          image_plot.setOffset ( 'y', start_time )
          image_plot.setLabel ( 'x', 'Freq' )
          image_plot.setLabel ( 'y', 'Time' )
          image_plot.setNumberOfBins ( 'x', n_rows )
          image_plot.setNumberOfBins ( 'y', n_cols )
          if self._canvas == None:
            self._canvas = self._window_controller.currentCanvas()
          self._canvas.addDisplay ( image_plot ) 

# now do an XYZ plot 
        bindings = ["freq", "time",  self._label ]
        xyz_plot = self._display_controller.createDisplay ( 'XYZ Plot', self._image_ntuple, bindings )
        xyz_plot.setLabel ( 'x', 'Freq' )
        xyz_plot.setLabel ( 'y', 'Time' )
        if self._canvas == None:
          self._canvas = self._window_controller.currentCanvas()
        self._canvas.addDisplay ( xyz_plot )
                                                                                
    if is_vector == True:
      num_elements = n_rows*n_cols
      flattened_array = numarray.reshape(plot_array,(num_elements,))
      if self._simple_ntuple == None:
# do X-Y plot
        self._simple_ntuple = self._ntuple_controller.createNTuple()
        self._simple_ntuple.setTitle ( "VellSet Data" )
        self._add_time_freq = True
      image = []
      for j in range(0, num_elements) :
        image.append(flattened_array[j])
      if self._simple_ntuple.isValidLabel(self._label):
        if len(image) != self._simple_ntuple.rows():
          print "Number of rows has changed! Clearing tuple!"
          self._simple_ntuple.clear()
        self._simple_ntuple.replaceColumn (self._label,image)
      else:
# add columns for new image data
        self._simple_ntuple.addColumn (self._label,image)
# add time or frequency column for 1-D plot
        if self._add_time_freq:
          if n_cols == num_elements:
            image = []
#add a time column
            self._x_label = "time"
            time_range = self._rec.cells.domain.time[1] - self._rec.cells.domain.time[0]
            x_step = time_range / n_cols
            start_time = self._rec.cells.domain.time[0] + 0.5 * x_step 
            for i in range(0, n_cols ) :
              current_time = start_time + i * x_step
              image.append(current_time)
            self._simple_ntuple.addColumn (self._x_label, image)
# add a frequency column 
          if n_rows == num_elements:
            image = []
            self._x_label = "freq"
            freq_range = self._rec.cells.domain.freq[1] - self._rec.cells.domain.freq[0]
            x_step = freq_range / n_rows
            start_freq = self._rec.cells.domain.freq[0] + 0.5 * x_step 
            for i in range(0, n_rows ) :
              current_freq = start_freq + i * x_step
              image.append(current_freq)
            self._simple_ntuple.addColumn (self._x_label, image)
          self._add_time_freq = False
        plot = self._display_controller.createDisplay ( 'XY Plot', self._simple_ntuple, [self._x_label,self._label] )
        if self._canvas == None:
          self._canvas = self._window_controller.currentCanvas()
        self._canvas.addDisplay ( plot )

  def set_data (self,dataitem,default_open=None,**opts):
    """ this callback receives data from the meqbrowser, when the
        user has requested a plot. It decides whether the data is
        from a VellSet or visu data record, and  after any
        necessary preprocssing forwards the data to one of
        the functions which does the actual plotting """

    self._rec = dataitem.data;
# if we are single stepping through requests, Oleg may reset the
# cache, so check for a non-data record situation
    if isinstance(self._rec, bool):
      return

# are we dealing with Vellsets?
    if self._rec.has_key("vellsets"):
# how many VellSet planes (e.g. I, Q, U, V would each be a plane) are there?
      number_of_planes = len(self._rec["vellsets"])
      for i in range(number_of_planes):
# get the shape tuple - useful if the Vells have been compressed down to
# a constant
        self._shape = self._rec.vellsets[i]["shape"]
# handle "value" first
        if self._rec.vellsets[i].has_key("value"):
          key = " value "
          complex_type = False;
          if self._rec.vellsets[i].value.type() == Complex32:
            complex_type = True;
          if self._rec.vellsets[i].value.type() == Complex64:
            complex_type = True;

          self._value_array = self._rec.vellsets[i].value
          if complex_type:
#extract real component
            self._value_real_array = self._rec.vellsets[i].value.getreal()
            self._data_type = " real"
            self._label = "plane " + str(i) + key + self._data_type 
            self._z_real_min = self._value_real_array.min()
            self._z_real_max = self._value_real_array.max()
            self.display_vells_data(self._value_real_array)
#extract imaginary component
            self._value_imag_array = self._rec.vellsets[i].value.getimag()
            self._data_type = " imag"
            self._label = "plane " + str(i) + key + self._data_type 
            self._z_imag_min = self._value_imag_array.min()
            self._z_imag_max = self._value_imag_array.max()
            self.display_vells_data(self._value_imag_array)
          else:
#we have a real array
            self._data_type = " real"
            self._label = "plane " + str(i) + key + self._data_type 
            self._z_real_min = self._value_array.min()
            self._z_real_max = self._value_array.max()
            self.display_vells_data(self._value_array)

# handle "perturbations" - at present we do nothing ...
        if self._rec.vellsets[i].has_key("perturbations"):
          number_of_perturbations = len(self._rec.vellsets[i].perturbations)
          for j in range(number_of_perturbations):
            perturb = self._rec.vellsets[i].perturbations[j]
#            print "self._perturbations[j] ",  perturb

# handle "perturbed_value"
        if self._rec.vellsets[i].has_key("perturbed_value"):
          number_of_perturbed_arrays = len(self._rec.vellsets[i].perturbed_value)
          for j in range(number_of_perturbed_arrays):
            complex_type = False;
            if self._rec.vellsets[i].perturbed_value[j].type() == Complex32:
              complex_type = True;
            if self._rec.vellsets[i].perturbed_value[j].type() == Complex64:
              complex_type = True;

            perturbed_array_diff = self._rec.vellsets[i].perturbed_value[j]
            key = " perturbed_value "
            if complex_type:
              real_array = perturbed_array_diff.getreal()
              self._data_type = " real"
              self._label =  "plane " + str(i) + key + str(j) + self._data_type 
              self.display_vells_data(real_array)
              imag_array = perturbed_array_diff.getimag()
              self._data_type = " imag"
              self._label =  "plane " + str(i) + key + str(j) + self._data_type 
              self.display_vells_data(imag_array)
            else:
              self._data_type = " real"
              self._label =  "plane " + str(i) + key + str(j) + self._data_type 
              self.display_vells_data(perturbed_array_diff)
    
# otherwise we are dealing with a set of visualization data
    if self._rec.has_key("visu"):
# do plotting of visualization data
      self.display_visu_data()

gridded_workspace.registerViewer(dict,ResultPlotter,dmitype='meqresult',priority=-10)
