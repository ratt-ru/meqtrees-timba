#!/usr/bin/python

# modules that are imported
from math import sin
from math import cos
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
  if style_string == "rectangle":
    representation = 0
  if style_string == "filled rectangle":
    representation = 1
  if style_string == "+":
    representation = 2
  if style_string == "x":
    representation = 3
  if style_string == "triangle":
    representation = 4
  if style_string == "filled triangle":
    representation = 5
  if style_string == "circle":
    representation = 6
  if style_string == "filled circle":
    representation = 7
  return style

class ResultPlotter(BrowserPlugin):
  _icon = pixmaps.bars3d
  viewer_name = "Result Plotter";
  def is_viewable (data):
    return len(data) > 0;
  is_viewable = staticmethod(is_viewable);

  def __init__(self,parent,dataitem=None,default_open=None,**opts):
#    print "in RecordPlotter constructor"
    self._rec = None;
    self._ntuple_controller = NTupleController.instance()
    self._window_controller = WindowController.instance()
    self._window_controller.createInspector ()

# used for 'embedded display'
#    self._window = CanvasWindow(parent, "MeqDisplay",0)

# used for 'standalone display'
    self._window = CanvasWindow(None, "MeqDisplay",0)
    self._Qlabel = QLabel("",parent);

# have Hippo window close without asking permission to discard etc
    self._window.setAllowClose()
    self._window.show()
    self._display_controller = DisplayController.instance()
    self._canvas = None
    self._image_ntuple = None
    self._simple_ntuple = None
    self._data_ntuple = None
    self._circles_computed = False

    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

  def __del__(self):
#    print "in destructor"
    self._window_controller.closeAllWindows()
                                                                                           
  def wtop (self):
# used for 'embedded display'
#    return self._window

# used for 'standalone display'
    return self._Qlabel

# compute points for two circles
  def compute_circles (self):
    self._radius_ntuple = None
    self._xy_plot = None
    x_pos = []
    y_pos = []
    x1_pos = []
    y1_pos = []
    angle = -5.0
    for j in range(0, 73 ) :
       angle = angle + 5.0
       x = 10.0 * cos(angle/57.2957795)
       y = 10.0 * sin(angle/57.2957795)
       x1 = 12.0 * cos(angle/57.2957795)
       y1 = 12.0 * sin(angle/57.2957795)
       x_pos.append(x)
       y_pos.append(y)
       x1_pos.append(x1)
       y1_pos.append(y1)
    if self._radius_ntuple == None:
       self._radius_ntuple = self._ntuple_controller.createNTuple()
       self._radius_ntuple.setTitle ("circle data")

    label = 'xx_0'
    self._radius_ntuple.addColumn (label,x_pos)
    label = 'yy_0'
    self._radius_ntuple.addColumn (label,y_pos)
    label = 'xx_1'
    self._radius_ntuple.addColumn (label,x1_pos)
    label = 'yy_1'
    self._radius_ntuple.addColumn (label,y1_pos)

    self._circles_computed = True

  def display_solution_data (self):
     if self._data_ntuple == None:
       self._data_ntuple = self._ntuple_controller.createNTuple()
       self._data_ntuple.setTitle ("WSRT Meq Solution")
       labels = ['xx_r','xx_i','xy_r','xy_i','yx_r','yx_i','yy_r','yy_i']
       self._data_ntuple.setLabels(labels)

# xx - extract real component
     if self._data_xx != None:
       complex_type = False
       label_r = 'xx_r'
       label_i = 'xx_i'
       num_plot_arrays = len(self._data_xx)
#       print "num_plot_arrays ", num_plot_arrays
       if self._data_xx[0].type() == Complex64:
         complex_type = True
       xx_r = None
       xx_i = None
       if complex_type:
         xx_r = self._data_xx.getreal()
         xx_i = self._data_xx.getimage()
       else:
         xx_r = self._data_xx
#         print "xx_r ", xx_r
#         print "rank xx_r[0]", xx_r[0].rank 
#         print "xx_r[0] contains ", xx_r[0]
       image_r = []
       image_i = []
       for i in range(0, num_plot_arrays):
          array_dim = len(xx_r[i].shape)
          num_elements = 1
          for j in range(0, array_dim):
            num_elements = num_elements * xx_r[i].shape[j]
          flattened_array_r = numarray.reshape(xx_r[i],(num_elements,))
          for j in range(0, num_elements): 
            image_r.append(flattened_array_r[j])
          if xx_i != None:
            flattened_array_i = numarray.reshape(xx_i[i],(num_elements,))
            for j in range(0, num_elements): 
              image_i.append(flattened_array_i[j])
          else:
            for j in range(0, num_elements): 
              image_i.append(0.0)
#       print "image_r ", image_r
#       print "image_i ", image_i
       if self._data_ntuple.isValidLabel(label_r):
         self._data_ntuple.replaceColumn (label_r,image_r)
       else:
         self._data_ntuple.addColumn (label_r,image_r)

       if self._data_ntuple.isValidLabel(label_i):
         self._data_ntuple.replaceColumn (label_i,image_i)
       else:
         self._data_ntuple.addColumn (label_i,image_i)

     if self._xy_plot == None:
       label_xy = ['xx_r','xx_i']
       self._xy_plot = self._display_controller.createDisplay ('XY Plot',self._data_ntuple, label_xy )
       index = self._display_controller.activeDataRepIndex(self._xy_plot)
       data_rep0 = self._xy_plot.getDataRep(index)
       data_rep0.setRepColor(self._data_color)
#       data_rep0.setRepSize(5.0)
       print "created xx_r xx_i plot"

       label_xx_yy = ['xx_0','yy_0']
       data_rep = self._display_controller.addDataRep(self._xy_plot, 'Strip Chart', self._radius_ntuple, label_xx_yy)
       plot_color = setColorStyle("red")
       data_rep.setRepColor(plot_color)
       line_style = setLineStyle("dashdot")
       data_rep.setRepStyle(line_style)
       print "created xx_0 yy_0 plot"

       label_xx_yy = ['xx_1','yy_1']
       data_rep = self._display_controller.addDataRep(self._xy_plot, 'Strip Chart', self._radius_ntuple, label_xx_yy)
       plot_color = setColorStyle("blue")
       data_rep.setRepColor(plot_color)
       line_style = setLineStyle("dashdot")
       data_rep.setRepStyle(line_style)
       print "created xx_1 yy_1 plot"

       if self._canvas == None:
         self._canvas = self._window_controller.currentCanvas()
       self._xy_plot.setTitle('xy = blue, yx = red')
       self._xy_plot.setLabel('x', 'real');
       self._xy_plot.setLabel('y', 'imaginary');
       self._canvas.addDisplay (self._xy_plot)
       print "created display"


  def display_vells_data (self, plot_array):
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
#    print "n_rows n_cols is_vector ", n_rows, " ",  n_cols, " ", is_vector
#    print "is_one_point_image ", is_one_point_image

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
#          print "result_plotter added freq column"
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
#          print "result_plotter added time column"

# do image plot
        if is_one_point_image == False:
          image_plot = self._display_controller.createDisplay( 'Z Plot', self._image_ntuple,[self._label,])
#        print "created image_plot object"
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
 #        print "called image_plot.setRange stuff"
          real_array = self._label.find("real")
#        if real_array>=0:
#          image_plot.setRange ( 'z', self._z_real_min, self._z_real_max)
#        else:
#          image_plot.setRange ( 'z', self._z_imag_min, self._z_imag_max)
          image_plot.setOffset ( 'x', start_freq )
          image_plot.setOffset ( 'y', start_time )
#        print "called image_plot.setOffset stuff"
#        image_plot.setLabel ( 'x', 'Time' )
#        image_plot.setLabel ( 'y', 'Freq' )
          image_plot.setLabel ( 'x', 'Freq' )
          image_plot.setLabel ( 'y', 'Time' )
          image_plot.setNumberOfBins ( 'x', n_rows )
          image_plot.setNumberOfBins ( 'y', n_cols )
#        print "called image_plot.setNumberOfBins stuff"
          if self._canvas == None:
            self._canvas = self._window_controller.currentCanvas()
#          print "created self._canvas object"
          self._canvas.addDisplay ( image_plot ) 
#        print "result_plotter passed addDisplay ( image_plot )"

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
    self._rec = dataitem.data;
#    try: print self._rec.a;
#    except: print 'No such field rec.a';
#    print "cache result contains ", self._rec.cache_result
#    if self._rec.has_key('cache_result'):
#      print "cache result contains cells ", self._rec.cache_result.cells
#      print "cache result contains cell segments ", self._rec.cache_result.cells.segments
#    print self._rec.field_names();
#    for f in self._rec.field_names():
#        print "field name: ", f
#        print "has sub fields ", self._rec[f].field_names()
#        if isinstance(self._rec[f],(array_class,)):
#           print "this is an array: ", self._rec[f];
#        if isinstance(self._rec[f],(dict,)):
#           print "this is a dict: ", self._rec[f];
#           print " "
#           print "the dict has sequential contents"
#           for value in self._rec[f].keys():
#             print value, '\t',self._rec[f][value]
#           print "   "
#	   if self._rec[f].has_key('cells'):
#             print 'now printing out contents for cells key'
#             print '  ', self._rec[f]['cells']
#	     sub_rec = self._rec[f]['cells']
#             if isinstance(sub_rec,(dict,)):
#               print ' '
#               print 'printing out dict cells contents sequentially'
#               for val in sub_rec.keys():
#                 print '     ' , val, '\t',sub_rec[val]
#	   if self._rec[f].has_key('vellsets'):
#             print 'now printing out contents for vellsets key'
#             print '  ', self._rec[f]['vellsets']
#	     sub_rec = self._rec[f]['vellsets']
#             if isinstance(sub_rec,(tuple,)):
#               print "vellsets is a tuple: ", sub_rec;
#               for x in sub_rec:
#                   print 'velset component ', x
#                   if isinstance(x,(dict,)):
#                       print ' '
#                       print 'printing out vellsets cells contents sequentially'
#                       for y in x.keys():
#                             print '     ' , y, '\t',x[y]
#        if isinstance(self._rec[f],(tuple,)):
#           print "this is a tuple: ", self._rec[f];
#        if isinstance(self._rec[f],(list,)):
#           print "this is a list: ", self._rec[f];
#    self._dummy = self._rec.a

#    print self._rec.field_names();

#    for fld in self._rec.field_names():
# handle "cells" field first as they define frequency range etc
#      if fld == "cells":
#        print "self._rec.cells.cell_size.freq", self._rec.cells.cell_size.freq
#        print "self._rec.cells.cell_size.time", self._rec.cells.cell_size.time
#        print "self._rec.cells.domain.freq", self._rec.cells.domain.freq
#        print "self._rec.cells.domain.start freq", self._rec.cells.domain.freq[0]
#        print "self._rec.cells.domain.end freq", self._rec.cells.domain.freq[1]
#        print "self._rec.cells.domain.time", self._rec.cells.domain.time
#        print "self._rec.cells.domain.start time", self._rec.cells.domain.time[0]
#        print "self._rec.cells.domain.end time", self._rec.cells.domain.time[1]

# process the data record

# are we dealing with Vellsets?
    if self._rec.has_key("vellsets"):
#      if fld == "vellsets":
# vellsets appear to be stored in a 'tuple' format
# first get number of vellsets in the tuple
#        print "vellsets tuple length ", len(self._rec.vellsets)

# how many VellSet planes (e.g. I, Q, U, V would each be a plane) are there?
        number_of_planes = len(self._rec["vellsets"])
#        print "number of VellSet planes ", number_of_planes
        for i in range(number_of_planes):
# get the shape tuple - useful if the Vells have been compressed down to
# a constant
          self._shape = self._rec.vellsets[i]["shape"]
#          print "shape is ", self._shape
#          print "vellset has fields ", i," ", self._rec.vellsets[i].field_names()
          fields = self._rec.vellsets[i].field_names()
#          print "vellset fields ", fields
# first get the 'value' field
          for f in self._rec.vellsets[i].field_names():
# handle "value" first
            if f == "value":
#              print "velset value for vellset ", i, " ", self._rec.vellsets[i].value
               complex_type = False;
               if self._rec.vellsets[i].value.type() == Complex32:
                 complex_type = True;
               if self._rec.vellsets[i].value.type() == Complex64:
                 complex_type = True;

               self._value_array = self._rec.vellsets[i].value
               if complex_type:
#extract real component
#                 print "self._value_array ", self._value_array
                 self._value_real_array = self._rec.vellsets[i].value.getreal()
                 self._data_type = " real"
                 self._label = f + self._data_type 
                 self._z_real_min = self._value_real_array.min()
                 self._z_real_max = self._value_real_array.max()
#                 print "value real max and min ", self._z_real_max, " ",self._z_real_min
                 self.display_vells_data(self._value_real_array)
#extract imaginary component
                 self._value_imag_array = self._rec.vellsets[i].value.getimag()
                 self._data_type = " imag"
                 self._label = f + self._data_type 
                 self._z_imag_min = self._value_imag_array.min()
                 self._z_imag_max = self._value_imag_array.max()
                 self.display_vells_data(self._value_imag_array)
               else:
#                 print "self._value_array ", self._value_array
                 self._data_type = " real"
                 self._label = f + self._data_type 
                 self._z_real_min = self._value_array.min()
                 self._z_real_max = self._value_array.max()
                 self.display_vells_data(self._value_array)
          for f in self._rec.vellsets[i].field_names():
# handle "perturbations"
            if f == "perturbations":
              number_of_perturbations = len(self._rec.vellsets[i].perturbations)
              self._perturbations = zeros((number_of_perturbations,))
              for j in range(number_of_perturbations):
                self._perturbations[j] = self._rec.vellsets[i].perturbations[j]
# handle "perturbed_value"
            if f == "perturbed_value":
              number_of_perturbed_arrays = len(self._rec.vellsets[i].perturbed_value)
              for j in range(number_of_perturbed_arrays):
                complex_type = False;
                if self._rec.vellsets[i].perturbed_value[j].type() == Complex32:
                  complex_type = True;
                if self._rec.vellsets[i].perturbed_value[j].type() == Complex64:
                  complex_type = True;

                perturbed_array_diff = self._rec.vellsets[i].perturbed_value[j]
                if complex_type:
                  real_array = perturbed_array_diff.getreal()
                  self._data_type = " real"
                  self._label = f + " " + str(j) + self._data_type 
                  self.display_vells_data(real_array)
                  imag_array = perturbed_array_diff.getimag()
                  self._data_type = " imag"
                  self._label = f + " " + str(j) + self._data_type 
                  self.display_vells_data(imag_array)
                else:
                  self._data_type = " real"
                  self._label = f + " " + str(j) + self._data_type 
                  self.display_vells_data(perturbed_array_diff)
    
# otherwise we are dealing with a set of solutions data
    else:
      if self._circles_computed == False:
        self.compute_circles()
#      print "keys are ", self._rec.keys()
#      print self._rec.top.xx.value
#      print "xx keys are ", self._rec.top.xx.keys()
      default_color = "red"
      color = None
      if self._rec.top.xx.has_key('attrib'):
        attrib = self._rec.top.xx['attrib']
        print 'contents of attrib ', attrib
        string_color = attrib.get('color', default_color) 
        self._data_color = setColorStyle(string_color)
	
#      print len(self._rec.top.xx.value)
#      print self._rec.top.xx.value[0]
#      print self._rec.top.xx.value[1]
#      print self._rec.field_names();
        
      self._data_xx = None
      self._data_yx = None
      self._data_xy = None
      self._data_yy = None
      self._data_xx =  self._rec.top.xx.value
# now do plotting
      self.display_solution_data()

gridded_workspace.registerViewer(dict,ResultPlotter,dmitype='meqresult',priority=-10)
