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

class ResultPlotter(BrowserPlugin):
  _icon = pixmaps.bars3d
  viewer_name = "Result Plotter";
  def is_viewable (data):
    return len(data) > 0;
  is_viewable = staticmethod(is_viewable);

  def __init__(self,parent,dataitem=None,default_open=None,**opts):
    print "in RecordPlotter constructor"
    self._rec = None;
    self._ntuple_controller = NTupleController.instance()
    self._window_controller = WindowController.instance()
    self._window_controller.createInspector ()
# needed for destructor
    self._window = CanvasWindow(parent, "MeqDisplay",0)
    self._window.show()
    self._display_controller = DisplayController.instance()
    self._canvas = None
    self._image_ntuple = None
    self._simple_ntuple = None

    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

  def __del__(self):
    print "in destructor"
    self._window.quitOnLastWindowClose(False)
                                                                                           
  def wtop (self):
    return self._window

  def display_data (self, plot_array):
# figure out type and rank of incoming array
    array_dim = len(plot_array.shape)
    array_rank = plot_array.rank
    n_rows = plot_array.shape[0]
    n_cols = 1
    if array_rank == 2:
      n_cols = plot_array.shape[1]
    self._add_time_freq = False;
    if n_cols > 1:
# first display an image 
      if self._image_ntuple == None:
        self._image_ntuple = self._ntuple_controller.createNTuple()
        self._image_ntuple.setTitle ("VellSet Data")
        self._add_time_freq = True;
      image_size = n_rows * n_cols
      image = []
      for j in range(0, n_rows ) :
        for i in range(0, n_cols) :
          print self._label, 'image appending ', plot_array[j][i]
          image.append(plot_array[j][i])
      if self._image_ntuple.isValidLabel(self._label):
        self._image_ntuple.replaceColumn (self._label,image)
      else:
# add columns for new image data
        self._image_ntuple.addColumn (self._label,image)
# add time and frequency columns for xyz plots
# first add time column
        if self._add_time_freq:
          xyz_x_label = "time"
          image = []
          time_range = self._rec.cells.domain.time[1] - self._rec.cells.domain.time[0]
          x_step = time_range / n_rows
          start_time = self._rec.cells.domain.time[0] 
          for j in range(0, n_rows ) :
            current_time = start_time + j * x_step
            for i in range(0, n_cols) :
              image.append(current_time)
          self._image_ntuple.addColumn (xyz_x_label, image)
# then add frequency column
          xyz_y_label = "freq"
          image = []
          freq_range = self._rec.cells.domain.freq[1] - self._rec.cells.domain.freq[0]
          y_step = freq_range / n_cols
          start_freq = self._rec.cells.domain.freq[0] 
          for j in range(0, n_rows ) :
            for i in range(0, n_cols) :
              current_freq = start_freq + i * y_step
              image.append(current_freq)
          self._image_ntuple.addColumn (xyz_y_label, image)
          self._add_time_freq = False

# do image plot
        image_plot = self._display_controller.createDisplay( 'Z Plot', self._image_ntuple,[self._label,])
        freq_range = self._rec.cells.domain.freq[1] - self._rec.cells.domain.freq[0]
        time_range = self._rec.cells.domain.time[1] - self._rec.cells.domain.time[0]
        x_step = time_range / n_rows
        y_step = freq_range / n_cols
        start_time = self._rec.cells.domain.time[0] 
        start_freq = self._rec.cells.domain.freq[0] 
        image_plot.setBinWidth ( 'x', x_step )
        image_plot.setBinWidth ( 'y', y_step )
        image_plot.setRange ( 'x', start_time, start_time + n_rows * x_step)
        image_plot.setRange ( 'y', start_freq, start_freq + n_cols * y_step)
        real_array = self._label.find("real")
#        if real_array>=0:
#          image_plot.setRange ( 'z', self._z_real_min, self._z_real_max)
#        else:
#          image_plot.setRange ( 'z', self._z_imag_min, self._z_imag_max)
        image_plot.setOffset ( 'x', start_time )
        image_plot.setOffset ( 'y', start_freq )
#        image_plot.setLabel ( 'x', 'Time' )
#        image_plot.setLabel ( 'y', 'Freq' )
        image_plot.setLabel ( 'x', 'Freq' )
        image_plot.setLabel ( 'y', 'Time' )
        image_plot.setNumberOfBins ( 'x', n_rows )
        image_plot.setNumberOfBins ( 'y', n_cols )
        if self._canvas == None:
          self._canvas = self._window_controller.currentCanvas()
        self._canvas.addDisplay ( image_plot ) 

# now do an XYZ plot
        bindings = ["time", "freq",  self._label ]
        xyz_plot = self._display_controller.createDisplay ( 'XYZ Plot', self._image_ntuple, bindings )
        xyz_plot.setLabel ( 'x', 'Time' )
        xyz_plot.setLabel ( 'y', 'Freq' )
        if self._canvas == None:
          self._canvas = self._window_controller.currentCanvas()
#        self._canvas.addDisplay ( xyz_plot )
                                                                                
    if n_cols == 1:
      if self._simple_ntuple == None:
# do X-Y plot
        self._simple_ntuple = self._ntuple_controller.createNTuple()
        self._simple_ntuple.setTitle ( "VellSet Data" )
        self._add_time_freq = True
      image = []
      for j in range(0, n_rows) :
         if array_rank == 2:
           image.append(plot_array[j][0])
         else:
           image.append(plot_array[j])
      if self._simple_ntuple.isValidLabel(self._label):
        self._simple_ntuple.replaceColumn (self._label,image)
      else:
# add columns for new image data
        self._simple_ntuple.addColumn (self._label,image)
# add time and frequency columns for xyz plots
# first add time column
        if self._add_time_freq:
          xyz_x_label = "time"
          image = []
          time_range = self._rec.cells.domain.time[1] - self._rec.cells.domain.time[0]
          x_step = time_range / n_rows
          start_time = self._rec.cells.domain.time[0] 
          for j in range(0, n_rows ) :
            current_time = start_time + j * x_step
            image.append(current_time)
          self._simple_ntuple.addColumn (xyz_x_label, image)
# then add frequency column - useless for a 1-D array, but ...
          xyz_y_label = "freq"
          image = []
          freq_range = self._rec.cells.domain.freq[1] - self._rec.cells.domain.freq[0]
          y_step = freq_range / n_cols
          start_freq = self._rec.cells.domain.freq[0] 
          for j in range(0, n_rows ) :
            for i in range(0, n_cols) :
              current_freq = start_freq + i * y_step
              image.append(current_freq)
          self._simple_ntuple.addColumn (xyz_y_label, image)
          self._add_time_freq = False
      plot = self._display_controller.createDisplay ( 'XY Plot', self._simple_ntuple, ["time",self._label] )
      if self._canvas == None:
        self._canvas = self._window_controller.currentCanvas()
      self._canvas.addDisplay ( plot )

  def set_data (self,dataitem,default_open=None,**opts):
    self._rec = dataitem.data;
#    print "In ResultPlotter set_data "
#    print "record has fields ", self._rec.field_names()
#    self._pprint = PrettyPrinter(width=78,stream=sys.stderr);
#    self._pprint.pprint(self._rec);
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

# do remaining fields
    for fld in self._rec.field_names():
# handle "VellSets" main field
      if fld == "vellsets":
# vellsets appear to be stored in a 'tuple' format
# first get number of vellsets in the tuple
#        print "vellsets tuple length ", len(self._rec.vellsets)
        number_of_vellsets = len(self._rec.vellsets)
        for i in range(number_of_vellsets):
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
                 self.display_data(self._value_real_array)
#extract imaginary component
                 self._value_imag_array = self._rec.vellsets[i].value.getimag()
                 self._data_type = " imag"
                 self._label = f + self._data_type 
                 self._z_imag_min = self._value_imag_array.min()
                 self._z_imag_max = self._value_imag_array.max()
                 self.display_data(self._value_imag_array)
               else:
#                 print "self._value_array ", self._value_array
                 self._data_type = " real"
                 self._label = f + self._data_type 
                 self._z_real_min = self._value_array.min()
                 self._z_real_max = self._value_array.max()
                 self.display_data(self._value_array)
          for f in self._rec.vellsets[i].field_names():
#            print "field name: ", f
# handle "perturbations"
            if f == "perturbations":
#              print "number of perturbed_values for velset ", i, " ", len(self._rec.vellsets[i].perturbations)
              number_of_perturbations = len(self._rec.vellsets[i].perturbations)
              self._perturbations = zeros((number_of_perturbations,))
              for j in range(number_of_perturbations):
#                print "self._rec.vellsets.perturbed_value", i, " ", j, " ",self._rec.vellsets[i].perturbations[j]
                self._perturbations[j] = self._rec.vellsets[i].perturbations[j]
# handle "perturbed_value"
            if f == "perturbed_value":
#              print "number of perturbed arrays for velset ", i, " ", len(self._rec.vellsets[i].perturbed_value)
              number_of_perturbed_arrays = len(self._rec.vellsets[i].perturbed_value)
              for j in range(number_of_perturbed_arrays):
                complex_type = False;
                if self._rec.vellsets[i].perturbed_value[j].type() == Complex32:
                  complex_type = True;
                if self._rec.vellsets[i].perturbed_value[j].type() == Complex64:
                  complex_type = True;

#                print "self._rec.vellsets.perturbed_array", i, " ", j, " ",self._rec.vellsets[i].perturbed_value[j]
#                perturbed_array_diff = self._value_array - self._rec.vellsets[i].perturbed_value[j]
                perturbed_array_diff = self._rec.vellsets[i].perturbed_value[j]
#                print "perturbed_array_diff ", perturbed_array_diff
                if complex_type:
                  real_array = perturbed_array_diff.getreal()
                  self._data_type = " real"
                  self._label = f + " " + str(j) + self._data_type 
                  self.display_data(real_array)
#		  print "real array ", real_array
                  imag_array = perturbed_array_diff.getimag()
                  self._data_type = " imag"
                  self._label = f + " " + str(j) + self._data_type 
                  self.display_data(imag_array)
#		  print "imag array ", imag_array
                else:
                  self._data_type = " real"
                  self._label = f + " " + str(j) + self._data_type 
                  self.display_data(perturbed_array_diff)
    
gridded_workspace.registerViewer(dict,ResultPlotter,dmitype='meqresult',priority=-10)
