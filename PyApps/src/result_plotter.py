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

  color_table = {
        'none': None,
        'black': Qt.black,
        'blue': Qt.blue,
        'cyan': Qt.cyan,
        'gray': Qt.gray,
        'green': Qt.green,
        'magenta': Qt.magenta,
        'red': Qt.red,
        'white': Qt.white,
        'yellow': Qt.yellow,
        'darkBlue' : Qt.darkBlue,
        'darkCyan' : Qt.darkCyan,
        'darkGray' : Qt.darkGray,
        'darkGreen' : Qt.darkGreen,
        'darkMagenta' : Qt.darkMagenta,
        'darkRed' : Qt.darkRed,
        'darkYellow' : Qt.darkYellow,
        'lightGray' : Qt.lightGray,
        }

  symbol_table = {
        'none': QwtSymbol.None,
        'rectangle': QwtSymbol.Rect,
        'ellipse': QwtSymbol.Ellipse,
        'dot': QwtSymbol.Ellipse,
        'circle': QwtSymbol.Ellipse,
	'xcross': QwtSymbol.XCross,
	'cross': QwtSymbol.Cross,
	'triangle': QwtSymbol.Triangle,
	'diamond': QwtSymbol.Diamond,
        }

  line_style_table = {
        'none': QwtCurve.NoCurve,
        'lines' : QwtCurve.Lines,
        'steps' : QwtCurve.Steps,
        'stick' : QwtCurve.Sticks,
        'dots' : QwtCurve.Dots,
#        'none': Qt.NoPen,
        'SolidLine' : Qt.SolidLine,
        'DashLine' : Qt.DashLine,
        'DotLine' : Qt.DotLine,
        'DashDotLine' : Qt.DashDotLine,
        'DashDotDotLine' : Qt.DashDotDotLine,
        'solidline' : Qt.SolidLine,
        'dashline' : Qt.DashLine,
        'dotline' : Qt.DotLine,
        'dashdotline' : Qt.DashDotLine,
        'dashdotdotline' : Qt.DashDotDotLine,
        }


  def __init__(self,parent=None,dataitem=None,default_open=None,**opts):
    """ Instantiate HippoDraw objects that are used to control
        various aspects of plotting
    """
    self._rec = None;
    self._hippo = None
    self._visu_plotter = None
    self._parent = parent;
    self._window_controller = None
    self._plot_type = None
    self._wtop = None;
    self._attributes_checked = False

    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

  def __del__(self):
    if self._window_controller:
      self._window_controller.closeAllWindows()
                                                                                           
  def wtop (self):
    return self._wtop;
    

  def check_attributes(self, attributes):
     plot_parms = None
     if attributes.has_key('plot'):
       plot_parms = attributes.get('plot')
       if plot_parms.has_key('attrib'):
         temp_parms = plot_parms.get('attrib')
         plot_parms = temp_parms
       if plot_parms.has_key('color'):
         plot_color = plot_parms.get('color')
         if not self.color_table.has_key(plot_color):
           Message = plot_color + " is not a valid color.\n Using blue by default"
           plot_parms['color'] = "blue"
           mb_color = QMessageBox("realvsimag.py",
                      Message,
                      QMessageBox.Warning,
                      QMessageBox.Ok | QMessageBox.Default,
                      QMessageBox.NoButton,
                      QMessageBox.NoButton)
           mb_color.exec_loop()
       if plot_parms.has_key('line_style'):
         plot_line_style = plot_parms.get('line_style')
         if not self.line_style_table.has_key(plot_line_style):
           Message = plot_line_style + " is not a valid line style.\n Using dots by default"
           plot_parms['line_style'] = "dots"
           mb_style = QMessageBox("realvsimag.py",
                      Message,
                      QMessageBox.Warning,
                      QMessageBox.Ok | QMessageBox.Default,
                      QMessageBox.NoButton,
                      QMessageBox.NoButton)
           mb_style.exec_loop()
       if plot_parms.has_key('symbol'):
         plot_symbol = plot_parms.get('symbol')
         if not self.symbol_table.has_key(plot_symbol):
           Message = plot_symbol + " is not a valid symbol.\n Using circle by default"
           plot_parms['symbol'] = "circle"
           mb_symbol = QMessageBox("realvsimag.py",
                      Message,
                      QMessageBox.Warning,
                      QMessageBox.Ok | QMessageBox.Default,
                      QMessageBox.NoButton,
                      QMessageBox.NoButton)
           mb_symbol.exec_loop()

#
# tree traversal code adapted from the pasteur institute python 
# programming course chapter on recursive data structures at
# http://www.pasteur.fr/formation/infobio/python/ch13s03.html
#

  def do_prework(self, node, attribute_list):
    _dprint(3, 'doing prework with attribute list ',attribute_list)
# we check if a plotter has been constructed - 
    if isinstance(node, dict) and self._visu_plotter is None:
      if len(attribute_list) == 0 and node.has_key('attrib'):
        _dprint(2,'length of attrib', len(node['attrib']));
        if len(node['attrib']) > 0:
          attrib_parms = node['attrib']
          plot_parms = attrib_parms.get('plot')
          if plot_parms.has_key('plot_type'):
            self._plot_type = plot_parms.get('plot_type')
          if plot_parms.has_key('type'):
            self._plot_type = plot_parms.get('type')
      else:
# first get plot_type at first possible point in list - nearest root
        list_length = len(attribute_list)
        for i in range(list_length):
          attrib_parms = attribute_list[i]
          _dprint(3, 'attrib_parms ',  attrib_parms, ' has length ', len( attrib_parms))
          _dprint(3, 'processing attribute list ',i, ' ', attrib_parms)
          if attrib_parms.has_key('plot'):
            plot_parms = attrib_parms.get('plot')
            _dprint(3, '*** plot_parms ',  plot_parms, ' has length ', len( plot_parms))
            if plot_parms.has_key('attrib'):
              temp_parms = plot_parms.get('attrib')
              plot_parms = temp_parms
            if plot_parms.has_key('plot_type'):
              self._plot_type = plot_parms.get('plot_type')
              break
            if plot_parms.has_key('type'):
              self._plot_type = plot_parms.get('type')
              break
      _dprint(3, 'pre_work gives plot_type ', self._plot_type)
      if self._plot_type == 'spectra':
        self._visu_plotter = QwtImagePlot(self._plot_type,parent=self._parent)
        self._wtop = self._visu_plotter;       # QwtImagePlot inherits from QwtPlot

      if self._plot_type == 'realvsimag':
        self._visu_plotter = realvsimag_plotter(self._plot_type,parent=self._parent)
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

  def do_leafwork(self, leaf, attrib_list):
    _dprint(3,'at leaf attribute list is ', attrib_list)
# If we arrive here without having gotten a plot type
# it is because the user specified an invalid type somehow.
# Post a message and select the default. 
    if self._visu_plotter is None:
      message = None
      if not self._plot_type is None:
        Message = self._plot_type + " is not a valid plot type.\n Using realvsimag by dafault." 
      else:
        Message = "Failure to find a valid plot type.\n Using realvsimag by default."
      mb = QMessageBox("result_plotter.py",
                     Message,
                     QMessageBox.Warning,
                     QMessageBox.Ok | QMessageBox.Default,
                     QMessageBox.NoButton,
                     QMessageBox.NoButton)
      mb.exec_loop()
      self._plot_type = "realvsimag"
      self._visu_plotter = realvsimag_plotter(self._plot_type,parent=self._parent)
      self._wtop = self._visu_plotter.plot;  # plot widget is our top widget

# now do the plotting
    self._visu_plotter.plot_data(leaf, attrib_list)

  def tree_traversal (self, node, label=None, attribute_list=None):
    _dprint(3,' ');
    _dprint(3,' ******* ');
    _dprint(3,'in tree traversal with node having length ', len(node));
    _dprint(3,' ******* ');
    _dprint(3,'length of node ', len(node))
    is_root = False
    if label is None:
      label = 'root'
      is_root = True
    _dprint(3, 'node has incoming label ', label)
    if attribute_list is None:
      attribute_list = []
    else:
      _dprint(3, 'tree: has incoming attribute list ', attribute_list)
    
    if isinstance(node, dict):
      _dprint(3, 'node is a dict')
      if self._visu_plotter is None and not is_root:
        self.do_prework(node, attribute_list)
      if not self.is_leaf(node):
        if node.has_key('label'):
          _dprint(3, 'tree: dict node has label(s) ', node['label'])
          if not node['label'] == label:
            if isinstance(node['label'], tuple):
              _dprint(3, 'tree: dict node label(s) is tuple')
              temp = list(node['label'])
              for j in range(0, len(temp)):
                tmp = label + '\n' + temp[j] 
                temp[j] = tmp
              node['label'] = tuple(temp)
            else:
              temp = label + '\n' + node['label']
              node['label'] = temp
        if node.has_key('attrib') and len(node['attrib']) > 0:
          _dprint(3, 'tree: dict node has attrib ', node['attrib'])
          if not self._attributes_checked:
            self.check_attributes(node['attrib'])
          attribute_list.append(node['attrib'])
        else:
          _dprint(3, 'tree: dict node has no valid attrib ')
          if is_root:
            attrib = {}
            plot_spec = {}
            plot_spec['plot_type'] = 'realvsimag'
            plot_spec['mean_circle'] = False
            plot_spec['mean_arrow'] = False
            plot_spec['stddev_circle'] = False
            attrib['plot'] = plot_spec
            attribute_list.append(attrib)
        if node.has_key('value'):
          self.tree_traversal(node['value'], node['label'], attribute_list)
      else:
        _dprint(3, 'tree: leaf node has label(s) ', node['label'])
        _dprint(3, 'tree: leaf node has incoming label ', label)
        if is_root and node.has_key('attrib') and len(node['attrib']) > 0:
          if not self._attributes_checked:
            self.check_attributes(node['attrib'])
          attribute_list.append(node['attrib'])
          self.do_prework(node, attribute_list)
        self.do_leafwork(node,attribute_list)
#      self.do_postwork(node)
    if isinstance(node, list):
      _dprint(3, 'node is a list')
      for i in range(len(node)):
        temp_label = None
        temp_list = attribute_list[:] 
        _dprint(3, 'list iter starting with attribute list ', i, ' ', temp_list)
        if isinstance(label, tuple):
          temp_label = label[i]
        else:
          temp_label = label
          
        if isinstance(node[i], dict):
          if node[i].has_key('label'):
            _dprint(3, 'tree: list node number has label(s) ', i, ' ',node[i]['label'])
            if isinstance(node[i]['label'], tuple):
              _dprint(3, 'tree: list node label(s) is tuple')
              temp = list(node[i]['label'])
              for j in range(0, len(temp)):
                tmp = temp_label + '\n' + temp[j]
                temp[j] = tmp
              node[i]['label'] = tuple(temp)
            else:
              temp = label + '\n' + node[i]['label']
              node[i]['label'] = temp
          if node[i].has_key('attrib'):
            _dprint(3, 'list: dict node has attrib ', i, ' ', node[i]['attrib'])
            if len(node[i]['attrib']) > 0:
              if not self._attributes_checked:
                self.check_attributes(node[i]['attrib'])
              temp_list.append(node[i]['attrib'])
          self.tree_traversal(node[i], node[i]['label'], temp_list)

  def display_visu_data (self):
    """ extract group_label key from incoming visu data record and
      create a visu_plotter object to plot the data 
    """
# traverse the plot record tree and retrieve data
    _dprint(3, ' ')
    _dprint(3, 'calling tree_traversal from display_visu_data')
    self.tree_traversal( self._rec.visu)
# now update the plot for 'realvsimag', 'errors' or 'standalone' plot
    _dprint(3, 'testing for update with self._plot_type ', self._plot_type)
    if not self._visu_plotter is None and not self._plot_type == 'spectra':
      self._visu_plotter.update_plot()
      self._visu_plotter.reset_data_collectors()

  def display_vells_data (self, plot_array):
    """ extract parameters and data from an array that is
        part of a VellSet and plot the array """ 

# construct hippo window if it doesn't exist
    if self._hippo is None:
      import sihippo
      _dprint(3,"HippoDraw version " + sihippo.__version__);
      from sihippo import *
      self._ntuple_controller = NTupleController.instance()
      self._window_controller = WindowController.instance()
      self._window_controller.createInspector ()
      self._window = CanvasWindow(self._parent, "MeqDisplay",0)
      self._wtop = self._window

      self._window.setAllowClose()
      self._window.show()
      self._display_controller = DisplayController.instance()
      self._canvas = None
      self._image_ntuple = None
      self._simple_ntuple = None
      self._hippo = True

# figure out type and rank of incoming array
    array_dim = len(plot_array.shape)
    array_rank = plot_array.rank
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
      _dprint(3,'in display_vells_data plotting image' ) 
# first display an image 
      if self._image_ntuple == None:
        self._image_ntuple = self._ntuple_controller.createNTuple()
        self._image_ntuple.setTitle ("VellSet Data")
        self._add_time_freq = True;
      image_size = n_rows * n_cols
      _dprint(3,'in display_vells_data image_size', image_size ) 
      image = []
      for j in range(0, n_rows ) :
        for i in range(0, n_cols) :
          image.append(plot_array[j][i])
      if self._image_ntuple.isValidLabel(self._label):
        if len(image) != self._image_ntuple.rows():
          _dprint(3, "Number of rows has changed! Clearing tuple!")
          self._image_ntuple.clear()
        self._image_ntuple.replaceColumn (self._label,image)
        _dprint(3,'passed self._image_ntuple.replaceColumn')
      else:
# add columns for new image data
        self._image_ntuple.addColumn (self._label,image)
        _dprint(3,'passed self._image_ntuple.addColumn')
# add time and frequency columns for xyz plots
# first add frequency column
        if self._add_time_freq:
          _dprint(3,'creating frequency axis')
          xyz_x_label = "freq"
          image = []
          freq_range = self._rec.cells.domain.freq[1] - self._rec.cells.domain.freq[0]
          x_step = freq_range / n_rows
          start_freq = self._rec.cells.domain.freq[0] + 0.5 * x_step 
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
          _dprint(3,'creating time axis')
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
        _dprint(3,'testing is_one_point_image ')
        _dprint(3,'is_one_point_image ', is_one_point_image)
        if is_one_point_image == False:
          _dprint(3,'creating Z plot')
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
        _dprint(3,'creating XYZ plot')
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
          _dprint(3, "Number of rows has changed! Clearing tuple!")
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
    _dprint(3,'exiting display_vells_data' ) 

  def set_data (self,dataitem,default_open=None,**opts):
    """ this callback receives data from the meqbrowser, when the
        user has requested a plot. It decides whether the data is
        from a VellSet or visu data record, and  after any
        necessary preprocessing forwards the data to one of
        the functions which does the actual plotting """

    self._rec = dataitem.data;
# if we are single stepping through requests, Oleg may reset the
# cache, so check for a non-data record situation
    if isinstance(self._rec, bool):
      return

# are we dealing with Vellsets?
    if self._rec.has_key("vellsets"):
      _dprint(3, 'handling vellsets')
# how many VellSet planes (e.g. I, Q, U, V would each be a plane) are there?
      number_of_planes = len(self._rec["vellsets"])
      _dprint(3, 'number of planes ', number_of_planes)
      for i in range(number_of_planes):
# get the shape tuple - useful if the Vells have been compressed down to
# a constant
        self._shape = self._rec.vellsets[i]["shape"]
# handle "value" first
        if self._rec.vellsets[i].has_key("value"):
          key = " value "
          complex_type = False;
# test if we have a numarray
          try:
            if self._rec.vellsets[i].value.type() == Complex32:
              complex_type = True;
            if self._rec.vellsets[i].value.type() == Complex64:
              complex_type = True;
            self._value_array = self._rec.vellsets[i].value
            _dprint(3, 'self._value_array ', self._value_array)
          except:
            temp_array = numarray.asarray(self._rec.vellsets[i].value)
            self._value_array = numarray.resize(temp_array,self._shape)
            if self._value_array.type() == Complex32:
              complex_type = True;
            if self._value_array.type() == Complex64:
              complex_type = True;

          if complex_type:
            _dprint(3,'handling complex array')
#extract real component
            self._value_real_array = self._value_array.getreal()
            self._data_type = " real"
            self._label = "plane " + str(i) + key + self._data_type 
            self._z_real_min = self._value_real_array.min()
            self._z_real_max = self._value_real_array.max()
            self.display_vells_data(self._value_real_array)
#extract imaginary component
            self._value_imag_array = self._value_array.getimag()
            self._data_type = " imag"
            self._label = "plane " + str(i) + key + self._data_type 
            self._z_imag_min = self._value_imag_array.min()
            self._z_imag_max = self._value_imag_array.max()
            self.display_vells_data(self._value_imag_array)
          else:
#we have a real array
            _dprint(3,'handling real array')
            self._data_type = " real"
            self._label = "plane " + str(i) + key + self._data_type 
            self._z_real_min = self._value_array.min()
            self._z_real_max = self._value_array.max()
            self.display_vells_data(self._value_array)
            _dprint(3,'passed display_vells_data')

# handle "perturbations" - at present we do nothing ...
        if self._rec.vellsets[i].has_key("perturbations"):
          _dprint(3, 'perturbations key exists')
          number_of_perturbations = len(self._rec.vellsets[i].perturbations)
          for j in range(number_of_perturbations):
            perturb = self._rec.vellsets[i].perturbations[j]

# handle "perturbed_value"
        if self._rec.vellsets[i].has_key("perturbed_value"):
          number_of_perturbed_arrays = len(self._rec.vellsets[i].perturbed_value)
          for j in range(number_of_perturbed_arrays):
# test if we have a numarray
            complex_type = False;
            perturbed_array_diff = None
            try:
              if self._rec.vellsets[i].perturbed_value[j].type() == Complex32:
                complex_type = True;
              if self._rec.vellsets[i].perturbed_value[j].type() == Complex64:
                complex_type = True;
              perturbed_array_diff = self._rec.vellsets[i].perturbed_value[j]
            except:
              temp_array = numarray.asarray(self._rec.vellsets[i].perturbed_value[j])
              perturbed_array_diff = numarray.resize(temp_array,self._shape)
              if perturbed_array_diff.type() == Complex32:
                complex_type = True;
              if perturbed_array_diff.type() == Complex64:
                complex_type = True;

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

    _dprint(3, 'exiting set_data')

gridded_workspace.registerViewer(dict,ResultPlotter,dmitype='meqresult',priority=-10)
