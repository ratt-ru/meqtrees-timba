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

# some general utility functions
def setColorStyle(color_string):
  """ convert a color specified as a string into a Hippo color """
  color = None;
# define colors
  if color_string == "red":
    color = Color(255,0,0)
  if color_string == "blue":
    color = Color(0,0,255)
  if color_string == "green":
    color = Color(0,255,0)
  if color_string == "yellow":
    color = Color(255,255,0)
  if color_string == "orange":
    color = Color(255,165,0)
  if color_string == "cyan":
    color = Color(0,255,255)
  if color_string == "magenta":
    color = Color(255,0,255)
  if color_string == "black":
    color = Color(0,0,0)
  if color_string == "white":
    color = Color(255,255,255)
  if color_string == "darkgray":
    color = Color(152,152,152)
  if color_string == "lightgray":
    color = Color(211,211,211)
  return color

def setLineStyle(style_string):
  """ convert a line style specified as a string to a Hippo number """
  style = None;
# define line style as a number
  if style_string == "solid":
    style = 0
  if style_string == "dash":
    style = 1
  if style_string == "dot":
    style = 2
  if style_string == "dashdot":
    style = 3
  if style_string == "dashdotdot":
    style = 4
  if style_string == "invisible":
    style = 5
  return style

def setPointRepresentation(style_string):
  """ convert a data point representation specified as a string 
  to a Hippo number """
  representation = None;
# define representation style as a number
  if style_string == "square":
    representation = 0
  if style_string == "filled_rectangle":
    representation = 1
  if style_string == "plus":
    representation = 2
  if style_string == "times":
    representation = 3
  if style_string == "triangle":
    representation = 4
  if style_string == "filled_triangle":
    representation = 5
  if style_string == "circle":
    representation = 6
  if style_string == "filled_circle":
    representation = 7
  return style

class visu_plotter:
  """ A class to plot visualzation data - XY vs YX solutions, spectra, etc
      that are generated in data collection and data concatenation
      nodes """

  def __init__(self, group_label, ntuple_controller, display_controller, window_controller, canvas):
    """ set initial default settings for plots """
    self._group_label = group_label
    self._display_controller = display_controller
    self._ntuple_controller = ntuple_controller 
    self._window_controller = window_controller
    self._canvas = canvas
    self._realvsimag_ntuple = None
    self._radius_ntuple = None
    self._line_ntuple = None
    self._image_ntuple = None
    self._simple_ntuple = None
    self._data_plot = None
    self._x_label = 'real'
    self._y_label = 'imaginary'
    self._label_r = self._x_label
    self._label_i = self._y_label
    self._plot_title = None
    self._data_color = setColorStyle("blue")
    self._plot_type = 'realvsimag'
#    self.compute_circles(10,12)

# compute points for two circles
  def compute_circles (self, item_label ,avg_r, avg_i):
    """ compute values for circle running through specified
        point and a line pointing to the point """

    x_sq = pow(avg_r, 2)
    y_sq = pow(avg_i, 2)
    radius = sqrt(x_sq + y_sq)
    x_pos = []
    y_pos = []
    angle = -5.0
    for j in range(0, 73 ) :
       angle = angle + 5.0
       x = radius * cos(angle/57.2957795)
       y = radius * sin(angle/57.2957795)
       x_pos.append(x)
       y_pos.append(y)
    if self._radius_ntuple == None:
       self._radius_ntuple = self._ntuple_controller.createNTuple()
       self._radius_ntuple.setTitle ("circle data")
    if self._line_ntuple == None:
       self._line_ntuple = self._ntuple_controller.createNTuple()
       self._line_ntuple.setTitle ("line data")

# store radius data
    label = item_label + '_xx_circle'
    if self._radius_ntuple.isValidLabel(label):
      self._radius_ntuple.replaceColumn (label,x_pos)
    else:
      self._radius_ntuple.addColumn (label,x_pos)
    label = item_label + '_yy_circle'
    if self._radius_ntuple.isValidLabel(label):
      self._radius_ntuple.replaceColumn (label,y_pos)
    else:
      self._radius_ntuple.addColumn (label,y_pos)

# store line data
    x1_pos = []
    y1_pos = []
    x1_pos.append(0)
    y1_pos.append(0)
    x1_pos.append(avg_r)
    y1_pos.append(avg_i)
    label = item_label + '_xx_line'
    if self._line_ntuple.isValidLabel(label):
      self._line_ntuple.replaceColumn (label,x1_pos)
    else:
      self._line_ntuple.addColumn (label,x1_pos)
    label = item_label + '_yy_line'
    if self._line_ntuple.isValidLabel(label):
      self._line_ntuple.replaceColumn (label,y1_pos)
    else:
      self._line_ntuple.addColumn (label,y1_pos)


  def real_vs_imag_plot (self,item_label):
    """ plot real va imaginary values together with circles
        indicating average values """
 
# get and combine all plot array data together into one Tuple
    num_plot_arrays = len(self._data_values)
    image_r = []
    image_i = []
    for i in range(0, num_plot_arrays):
      xx_r = None
      xx_i = None
      if self._data_values[i].type() == Complex64:
          xx_r = self._data_values[i].getreal()
          xx_i = self._data_values[i].getimag()
      else:
        xx_r = self._data_values[i]
      array_dim = len(xx_r.shape)
      num_elements = 1
      for j in range(0, array_dim):
        num_elements = num_elements * xx_r.shape[j]
      flattened_array_r = numarray.reshape(xx_r,(num_elements,))
       
      for j in range(0, num_elements): 
        image_r.append(flattened_array_r[j])
      if xx_i != None:
        flattened_array_i = numarray.reshape(xx_i,(num_elements,))
        for j in range(0, num_elements): 
          image_i.append(flattened_array_i[j])
      else:
        for j in range(0, num_elements): 
          image_i.append(0.0)

# add columns to tuple
    num_rows = len(image_r)
    if num_rows == 0:
      print 'nothing to update!'
      return
    if self._realvsimag_ntuple is None:
      self._realvsimag_ntuple = self._ntuple_controller.createNTuple()
    self._plot_exists = False
    if self._realvsimag_ntuple.isValidLabel(self._label_r):
      if num_rows != self._realvsimag_ntuple.rows():
        print "Number of rows has changed! Clearing tuple!"
        self._realvsimag_ntuple.clear()
      self._realvsimag_ntuple.replaceColumn (self._label_r,image_r)
      self._plot_exists = True
    else:
      self._realvsimag_ntuple.addColumn (self._label_r,image_r)
#      print 'added real column'

    if self._realvsimag_ntuple.isValidLabel(self._label_i):
      self._realvsimag_ntuple.replaceColumn (self._label_i,image_i)
    else:
      self._realvsimag_ntuple.addColumn (self._label_i,image_i)
#      print 'added imag column'

# create / update plot title
    if self._plot_exists == False:
        string_color = self._attrib_parms.get('color', 'blue')
        self._data_color = setColorStyle(string_color)
        if self._plot_title is None:
          self._plot_title = self._plot_type +':'
        self._plot_title = self._plot_title + ' ' + self._attrib_parms.get('label','')
        self._plot_title = self._plot_title + ' ' + string_color

# obtain / calculate parameters for circles
    if self._plot_type == 'realvsimag':
      sum_r = self._realvsimag_ntuple.sum(self._label_r)
      sum_i = self._realvsimag_ntuple.sum(self._label_i)
# following can fail if we had to execute a 'clear' operation above
#      rows = self._realvsimag_ntuple.rows()
      avg_r = sum_r / num_rows
      avg_i = sum_i / num_rows
      self.compute_circles(item_label, avg_r, avg_i)

# here we create a display if one previously doesn't exist
    if self._data_plot == None:
      tuple_labels = [self._label_r, self._label_i]
      self._data_plot = self._display_controller.createDisplay ('XY Plot',self._realvsimag_ntuple, tuple_labels )
      if self._plot_title is None:
        self._plot_title = 'This is the title!'
      self._data_plot.setTitle(self._plot_title)
      self._data_plot.setLabel('x', 'real')
      self._data_plot.setLabel('y', 'imaginary')
      index = self._display_controller.activeDataRepIndex(self._data_plot)
      data_rep0 = self._data_plot.getDataRep(index)
      data_rep0.setRepColor(self._data_color)
# we should be able to do the following but things seem to be ignored!!
      data_rep0.setRepStyle(4)
      data_rep0.setRepSize(5)

# add circles if they have been computed
      if (self._radius_ntuple != None):
        label_xx_yy = [item_label+'_xx_circle', item_label +'_yy_circle']
        data_rep = self._display_controller.addDataRep(self._data_plot, 'Strip Chart', self._radius_ntuple, label_xx_yy)
        data_rep.setRepColor(self._data_color)
        line_style = setLineStyle("dashdot")
        data_rep.setRepStyle(line_style)

        label_xx_yy = [item_label+'_xx_line', item_label +'_yy_line']
        data_rep = self._display_controller.addDataRep(self._data_plot, 'Strip Chart', self._line_ntuple, label_xx_yy)
        data_rep.setRepColor(self._data_color)
        line_style = setLineStyle("solid")
        data_rep.setRepStyle(line_style)
      if self._canvas == None:
        self._canvas = self._window_controller.currentCanvas()
      self._canvas.addDisplay (self._data_plot)

# here we add a new data rep to an existing plot
    if self._plot_exists == False:
# update title
      self._data_plot.setTitle(self._plot_title)
      tuple_labels = [self._label_r, self._label_i]
# add the new data rep
      data_rep = self._display_controller.addDataRep(self._data_plot, 'XY Plot', self._realvsimag_ntuple, tuple_labels)
      data_rep.setRepColor(self._data_color)
# add circles for new data rep
      if (self._radius_ntuple != None):
        label_xx_yy = [item_label+'_xx_circle', item_label +'_yy_circle']
        data_rep = self._display_controller.addDataRep(self._data_plot, 'Strip Chart', self._radius_ntuple, label_xx_yy)
        data_rep.setRepColor(self._data_color)
        line_style = setLineStyle("dashdot")
        data_rep.setRepStyle(line_style)

        label_xx_yy = [item_label+'_xx_line', item_label +'_yy_line']
        data_rep = self._display_controller.addDataRep(self._data_plot, 'Strip Chart', self._line_ntuple, label_xx_yy)
        data_rep.setRepColor(self._data_color)
        line_style = setLineStyle("solid")
        data_rep.setRepStyle(line_style)

  def spectrum_plot (self, data_label, plot_array):
    """ figure out shape, rank etc of a spectrum array and
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

# test if we have a 2-D array
    if is_vector == False:
# display an image 
      if self._image_ntuple == None:
        self._image_ntuple = self._ntuple_controller.createNTuple()
        self._image_ntuple.setTitle ("Spectral Data")
      image_size = n_rows * n_cols
      image = []
      for j in range(0, n_rows ) :
        for i in range(0, n_cols) :
          image.append(plot_array[j][i])
      if self._image_ntuple.isValidLabel(data_label):
        if len(image) != self._image_ntuple.rows():
          print "Number of rows has changed! Clearing tuple!"
          self._realvsimag_ntuple.clear()
        self._image_ntuple.replaceColumn (data_label,image)
      else:
# add columns for new image data
        self._image_ntuple.addColumn (data_label,image)
# do image plot
        image_plot = self._display_controller.createDisplay( 'Z Plot', self._image_ntuple,[data_label,])
        image_plot.setLabel ( 'x', 'channels' )
        image_plot.setLabel ( 'y', 'time sequence' )
        image_plot.setNumberOfBins ( 'x', n_rows )
        image_plot.setNumberOfBins ( 'y', n_cols )
        if self._canvas == None:
          self._canvas = self._window_controller.currentCanvas()
        self._canvas.addDisplay ( image_plot ) 
                                                                                
    if is_vector == True:
      if self._simple_ntuple == None:
# do X-Y plot
        self._simple_ntuple = self._ntuple_controller.createNTuple()
        self._simple_ntuple.setTitle ( "Spectral Data" )
# add stuff for channels
        image = []
        if n_cols > 1:
          for j in range(0, n_cols ) :
            image.append(j)
        if n_rows > 1:
          for j in range(0, n_rows ) :
            image.append(j)
        if n_cols == 1 & n_rows == 1:
            image.append(0)
        self._simple_ntuple.addColumn ("channel", image)

# add actual data
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
      if n_cols == 1 & n_rows == 1:
        for j in range(0, n_cols) :
         if array_rank == 2:
           image.append(plot_array[0][j])
         else:
           image.append(plot_array[j])
      if self._simple_ntuple.isValidLabel(data_label):
        if len(image) != self._simple_ntuple.rows():
          print "Number of rows has changed! Clearing tuple!"
          self._simple_ntuple.clear()
        self._simple_ntuple.replaceColumn (data_label,image)
      else:
# add columns for new image data
        self._simple_ntuple.addColumn (data_label,image)
# Now create a new plot for this data label
        plot = self._display_controller.createDisplay ( 'XY Plot', self._simple_ntuple, ["channel",data_label] )
        if self._canvas == None:
          self._canvas = self._window_controller.currentCanvas()
        self._canvas.addDisplay ( plot )

  def plot_data(self, item_label, visu_record):
    """ process incoming data and attributes into the
        appropriate type of plot """

# first find out what kind of plot we are making
    plot_types = None
    if visu_record.has_key('attrib'):
      self._attrib_parms = visu_record['attrib']
      plot_types = self._attrib_parms.get('plot_type',self._plot_type)

# convert to a tuple if necessary
      if isinstance(plot_types, str):
        plot_types = (plot_types,)

    if visu_record.has_key('value'):
      self._data_values = visu_record['value']

# extract and define the tuple labels for this data item
    self._label_r = item_label + "_r"
    self._label_i = item_label + "_i"

    for j in range(len(plot_types)):
      self._plot_type = plot_types[j]
# now generate  particular plot type
      if  self._plot_type == 'realvsimag':
        self.real_vs_imag_plot(item_label)

# if request is for spectra iterate through each data set
# and display the spectra
      if  self._plot_type == 'spectra':
        plot_label = self._attrib_parms.get('label','')
        num_plot_arrays = len(self._data_values)
        for i in range(0, num_plot_arrays):
          complex_type = False;
          if self._data_values[i].type() == Complex64:   
            complex_type = True;
          if complex_type:
            real_array =  self._data_values[i].getreal()
            self._data_type = " real"
            data_label = plot_label + "_" + str(i) +  "_" + self._data_type
            self.spectrum_plot(data_label, real_array)
            imag_array =  self._data_values[i].getimag()
            self._data_type = " imag"
            data_label = plot_label +  "_" +str(i) +  "_" +self._data_type
            self.spectrum_plot(data_label, imag_array)
          else:
            self._data_type = " real"
            data_label = plot_label +  "_" +str(i) +  "_" +self._data_type
            self.spectrum_plot(data_label, self._data_values[i])

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
    self._ntuple_controller = NTupleController.instance()
    self._window_controller = WindowController.instance()
    self._window_controller.createInspector ()

# used for 'embedded display'
#    self._window = CanvasWindow(parent, "MeqDisplay",0)

# used for 'standalone display'
    self._window = CanvasWindow(None, "MeqDisplay",0)
# this QLabel is needed so that Oleg's browser is
# happy that a child is present
    self._Qlabel = QLabel("",parent);

# have Hippo window close without asking permission to discard etc
    self._window.setAllowClose()

    self._window.show()
    self._display_controller = DisplayController.instance()
    self._canvas = None
    self._image_ntuple = None
    self._simple_ntuple = None
    self._realvsimag_ntuple = None
    self._plotter_dict = {}

    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

  def __del__(self):
    self._window_controller.closeAllWindows()
                                                                                           
  def wtop (self):
# used for 'embedded display'
#    return self._window

# used for 'standalone display'
    return self._Qlabel

  def display_visu_data (self):
    """ extract group_label key from incoming visu data record and
      create a visu_plotter object to plot the data 
    """

# get group label from incoming record
# we have one group label key so get first group key
    group_label_keys = self._rec.visu.keys()
    for j in range(0, len(group_label_keys)):
      group_label =  group_label_keys[j]
      if self._plotter_dict.has_key(group_label) == False:
#create a new visu plotter
        visual_plotter = visu_plotter(group_label, self._ntuple_controller,self._display_controller,self._window_controller, self._canvas) 
#add the new plotter to a 'dict' of visualization plotters
        self._plotter_dict[group_label] = visual_plotter

# get item labels keys - can be 1 or more
      item_label_keys = self._rec.visu[group_label].keys()
      for i in range(0, len(item_label_keys)):
        item_label =  item_label_keys[i]
#insert the data into the plotter
        self._plotter_dict[group_label].plot_data(item_label,self._rec.visu[group_label][item_label])

  def display_vells_data (self, plot_array):
    """ extract parameters and data from an array that is
        part of a VellSet and plot the array """ 

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
