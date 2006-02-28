#!/usr/bin/python

# modules that are imported
from math import sin
from math import cos
from math import pow
from math import sqrt

# modules that are imported
from Timba.dmi import *
from Timba import utils
from Timba.Meq import meqds
from Timba.Meq.meqds import mqs
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI import widgets
from Timba.GUI.browsers import *
from Timba import Grid

from qt import *
from numarray import *
from Timba.Plugins.display_image import *
from Timba.Plugins.realvsimag import *
from QwtPlotImage import *
from QwtColorBar import *
from SpectrumData import *
from VellsData import *
from SolverData import *
from ND_Controller import *
from ResultsRange import *
from BufferSizeDialog import *
from plot_printer import *

from Timba.utils import verbosity
_dbg = verbosity(0,name='result_plotter');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;


class ResultPlotter(GriddedPlugin):
  """ a class to visualize data, VellSets or visu data, that is 
      contained within a node's cache_result record. Objects of 
      this class are launched from the meqbrowser GUI """

  _icon = pixmaps.bars3d
  viewer_name = "Result Plotter";
  def is_viewable (data):
    return len(data) > 0;
  is_viewable = staticmethod(is_viewable);

# the following global tables replicate similar tables found in the
# realvsimag plotter. The idea is that the system first checks the
# contents of 'visu' plot records against these tables here 
# during tree traversal. Otherwise every leaf node would issue
# warnings about the same unacceptable parameters - which would
# really irritate the user. The 'check_attributes' function defined
# below does the work.
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
        'square': QwtSymbol.Rect,
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
  
  def __init__(self,gw,dataitem,cellspec={},**opts):
    GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);
    """ Instantiate HippoDraw objects that are used to control
        various aspects of plotting, if the hippo plotter
        is instantiated.
    """
    self._rec = None;
    self._plot_type = None
    self._wtop = None;
    self.dataitem = dataitem
    self._attributes_checked = False
    self._vells_data = None
    self._solver_data = None
    self.num_possible_ND_axes = None
    self.old_plot_data_rank = -1
    self.active_image_index = None
    self._spectrum_data = None
    self.data_list = []
    self.data_list_labels = []
    self.data_list_length = 0
    self.max_list_length = 10
    self.ignore_replay = False
    self._window_controller = None

    self.reset_plot_stuff()

# back to 'real' work
    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

  def reset_plot_stuff(self):
    """ resets widgets to None. Needed if we have been putting
        out a message about Cache not containing results, etc
    """
    self._visu_plotter = None
    self.colorbar = {}
    self.results_selector = None
    self.spectrum_node_selector = None
    self.ND_Controls = None
    self.layout_parent = None
    self.layout = None


  def __del__(self):
    if self._window_controller:
      self._window_controller.closeAllWindows()
                                                                                           
  def wtop (self):
    """ function needed by Oleg for reasons known only to him! """
    return self._wtop;

  def plotSpectra(self, leaf_record):
    """ stores and plots data for a visu Spectra node """
    self._spectrum_data = None
    if self._spectrum_data is None:
      (self._data_labels, self._string_tag) = self._visu_plotter.getSpectrumTags()
      self._spectrum_data = SpectrumData(self._data_labels, self._string_tag)
    if leaf_record.has_key('value'):
      self._data_values = leaf_record['value']

# store the data
    self._spectrum_data.StoreSpectrumData(self._data_values)

# test and update the context menu
    plot_menus = self._spectrum_data.getMenuLabels()
    self._visu_plotter.setSpectrumMenuItems(plot_menus)
    spectrum_menu_items = len(plot_menus)
    if spectrum_menu_items > 2: 
      marker_parms = self._spectrum_data.getMarkerParms()
      marker_labels = self._spectrum_data.getMarkerLabels()
      self._visu_plotter.setSpectrumMarkers(marker_parms, marker_labels)

# plot active instance of array
    if self.active_image_index is None or self.active_image_index > spectrum_menu_items - 1:
      self.active_image_index = spectrum_menu_items - 1
      self._spectrum_data.setActivePlot(self.active_image_index)
    plot_label = self._spectrum_data.getPlotLabel()
    plot_data = self._spectrum_data.getActivePlotArray()
    self._visu_plotter.array_plot(plot_label, plot_data, False)

    _dprint(2, 'exiting plotSpectra');

  def check_attributes(self, attributes):
     """ check parameters of plot attributes against allowable values """
     plot_parms = None
     if attributes.has_key('plot'):
       plot_parms = attributes.get('plot')
       if plot_parms.has_key('attrib'):
         temp_parms = plot_parms.get('attrib')
         plot_parms = temp_parms
       if plot_parms.has_key('color'):
         plot_color = plot_parms.get('color')
         if not self.color_table.has_key(plot_color):
           Message = str(plot_color) + " is not a valid color.\n Using blue by default"
           plot_parms['color'] = "blue"
           mb_color = QMessageBox("realvsimag.py",
                      Message,
                      QMessageBox.Warning,
                      QMessageBox.Ok | QMessageBox.Default,
                      QMessageBox.NoButton,
                      QMessageBox.NoButton)
           mb_color.exec_loop()
       if plot_parms.has_key('mean_circle_color'):
         plot_color = plot_parms.get('mean_circle_color')
         if not self.color_table.has_key(plot_color):
           Message = str(plot_color) + " is not a valid color.\n Using blue by default"
           plot_parms['mean_circle_color'] = "blue"
           mb_color = QMessageBox("realvsimag.py",
                      Message,
                      QMessageBox.Warning,
                      QMessageBox.Ok | QMessageBox.Default,
                      QMessageBox.NoButton,
                      QMessageBox.NoButton)
           mb_color.exec_loop()
       if plot_parms.has_key('stddev_circle_color'):
         plot_color = plot_parms.get('stddev_circle_color')
         if not self.color_table.has_key(plot_color):
           Message = str(plot_color) + " is not a valid color.\n Using blue by default"
           plot_parms['stddev_circle_color'] = "blue"
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
           Message = str(plot_line_style) + " is not a valid line style.\n Using dots by default"
           plot_parms['line_style'] = "dots"
           mb_style = QMessageBox("realvsimag.py",
                      Message,
                      QMessageBox.Warning,
                      QMessageBox.Ok | QMessageBox.Default,
                      QMessageBox.NoButton,
                      QMessageBox.NoButton)
           mb_style.exec_loop()
       if plot_parms.has_key('mean_circle_style'):
         plot_line_style = plot_parms.get('mean_circle_style')
         if not self.line_style_table.has_key(plot_line_style):
           Message = str(plot_line_style) + " is not a valid line style for mean circles.\n Using lines by default"
           plot_parms['mean_circle_style'] = "lines"
           mb_style = QMessageBox("realvsimag.py",
                      Message,
                      QMessageBox.Warning,
                      QMessageBox.Ok | QMessageBox.Default,
                      QMessageBox.NoButton,
                      QMessageBox.NoButton)
           mb_style.exec_loop()
       if plot_parms.has_key('stddev_circle_style'):
         plot_line_style = plot_parms.get('stddev_circle_style')
         if not self.line_style_table.has_key(plot_line_style):
           Message = str(plot_line_style) + " is not a valid line style for stddev circles.\n Using DotLine by default"
           plot_parms['stddev_circle_style'] = "DotLine"
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
           Message = str(plot_symbol) + " is not a valid symbol.\n Using circle by default"
           plot_parms['symbol'] = "circle"
           mb_symbol = QMessageBox("realvsimag.py",
                      Message,
                      QMessageBox.Warning,
                      QMessageBox.Ok | QMessageBox.Default,
                      QMessageBox.NoButton,
                      QMessageBox.NoButton)
           mb_symbol.exec_loop()
  # check_attributes

#
# tree traversal code adapted from the pasteur institute python 
# programming course chapter on recursive data structures at
# http://www.pasteur.fr/formation/infobio/python/ch13s03.html
#

  def do_prework(self, node, attribute_list):
    """ do any processing before actual handling of data in a leaf node """
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
          if plot_parms.has_key('results_buffer'):
            self.max_list_length = plot_parms.get('results_buffer')
      else:
# first get plot_type at first possible point in list - nearest root
        list_length = len(attribute_list)
        for i in range(list_length):
          attrib_parms = attribute_list[i]
          _dprint(3, 'attrib_parms ',  attrib_parms, ' has length ', len( attrib_parms));
          _dprint(3, 'processing attribute list ',i, ' ', attrib_parms);
          if attrib_parms.has_key('plot'):
            plot_parms = attrib_parms.get('plot')
            _dprint(3, '*** plot_parms ',  plot_parms, ' has length ', len( plot_parms));
            if plot_parms.has_key('attrib'):
              temp_parms = plot_parms.get('attrib')
              plot_parms = temp_parms
            if plot_parms.has_key('results_buffer'):
              self.max_list_length = plot_parms.get('results_buffer')
            if plot_parms.has_key('plot_type'):
              self._plot_type = plot_parms.get('plot_type')
              break
            if plot_parms.has_key('type'):
              self._plot_type = plot_parms.get('type')
              break
      _dprint(3, 'pre_work gives plot_type ', self._plot_type)
      if self._plot_type == 'spectra':
        _dprint(3, 'pre_work setting visu_plotter to QwtImageDisplay for spectra!')
        self.create_image_plotters()

      if self._plot_type == 'realvsimag':
        _dprint(3, 'pre_work setting visu_plotter to realvsimag_plotter!')
        self.layout_parent = QWidget(self.wparent())
        self.layout = QGridLayout(self.layout_parent)
        self._visu_plotter = realvsimag_plotter(self._plot_type,parent=self.layout_parent)
        self.layout.addWidget(self._visu_plotter.plot, 0, 1)
        self.set_widgets(self.layout_parent,self.dataitem.caption,icon=self.icon())
        self._wtop = self.layout_parent;       


  def do_postwork(self, node):
    """ do any processing needed after data in a leaf node has been handled """
    _dprint(3,"in postwork: do nothing at present");


  def is_leaf(self, node):
    """ tests if a node is actually a leaf node """
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
    """ method which does actual plotting at a leaf node """

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
      self._visu_plotter = realvsimag_plotter(self._plot_type,parent=self.wparent())
      self.set_widgets(self._visu_plotter,self.dataitem.caption,icon=self.icon())
      self._wtop = self._visu_plotter.plot;  # plot widget is our top widget

# now do the plotting
    if self._plot_type == 'spectra':
      if self.first_leaf_node:
        self.leaf_node_list = []
        self.list_attrib_lists = []
        self.list_labels = []
        self._visu_plotter.plot_data(leaf, attrib_list, label=self.label)
        self.plotSpectra(leaf)
        self.leaf_node_list.append(leaf)
        self.list_attrib_lists.append(attrib_list)
        self.list_labels.append(self.label)
        self.first_leaf_node = False
      else:
        self.leaf_node_list.append(leaf)
        self.list_attrib_lists.append(attrib_list)
        self.list_labels.append(self.label)
        self.adjust_spectrum_selector()
    else:
      self._visu_plotter.plot_data(leaf, attrib_list, label=self.label)

  # do_leafwork

  def tree_traversal (self, node, label=None, attribute_list=None):
    """ routine to do a recursive tree traversal of a Visu plot tree """
    _dprint(3,' ');
    _dprint(3,' ******* ');
    _dprint(3,'in tree traversal with node having length ', len(node));
    _dprint(3,' ******* ');
    _dprint(3,'length of node ', len(node))
    is_root = False
    if label is None:
      label = 'root'
      is_root = True
      node['plot_label'] = ''
      
    _dprint(3, 'node has incoming label ', label)
    if attribute_list is None:
      attribute_list = []
    else:
      _dprint(3, 'tree: has incoming attribute list ', attribute_list)
    
    if isinstance(node, dict):
      _dprint(3, 'node is a dict')
      if self._visu_plotter is None and not is_root:
# call the do_prework method to do any actions needed before
# an actual leaf node performs plotting operations
        self.do_prework(node, attribute_list)
# test if this node is a leaf
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
              node['plot_label'] = tuple(temp)
            else:
              temp = label + '\n' + node['label']
              node['plot_label'] = temp
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
# if not a leaf, and we find a 'value' field, then call
# recursive method 'tree_traversal'
        if node.has_key('value'):
          self.tree_traversal(node['value'], node['plot_label'], attribute_list)
      else:
        try:
          _dprint(3, 'tree: leaf node has label(s) ', node['plot_label'])
          _dprint(3, 'tree: leaf node has incoming label ', label)
        except:
          _dprint(3, 'node label field expected, not found, so am exiting')
          Message = "Failure of result_plotter tree-traversal.\n Result_plotter does not yet work with MeqHistoryCollect nodes."
          mb = QMessageBox("result_plotter.py",
                     Message,
                     QMessageBox.Warning,
                     QMessageBox.Ok | QMessageBox.Default,
                     QMessageBox.NoButton,
                     QMessageBox.NoButton)
          mb.exec_loop()
          return
        if is_root and node.has_key('attrib') and len(node['attrib']) > 0:
          if not self._attributes_checked:
            self.check_attributes(node['attrib'])
          attribute_list.append(node['attrib'])

# call the do_prework method to do any actions needed before
# actual leaf node performs plotting operations
          self.do_prework(node, attribute_list)

# if all tests are passed and this is a leaf, than do actual plotting work
        self.do_leafwork(node,attribute_list)

# no post work at the present time
#      self.do_postwork(node)

# if we are at a level where we encounter a bunch of nodes in a list
# then we must preform a recursive tree traversal starting with
# each element in the list
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
              node[i]['plot_label'] = tuple(temp)
            else:
              temp = label + '\n' + node[i]['label']
              node[i]['plot_label'] = temp
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
    self.first_leaf_node = True
    self.tree_traversal( self._rec.visu)
# now update the plot for 'realvsimag', 'errors' or 'standalone' plot
    _dprint(3, 'testing for update with self._plot_type ', self._plot_type)
    if not self._visu_plotter is None and not self._plot_type == 'spectra':
      self._visu_plotter.update_plot()
      self._visu_plotter.reset_data_collectors()

  def create_image_plotters(self):
    self.layout_parent = QWidget(self.wparent())
    self.layout = QGridLayout(self.layout_parent)
    self._visu_plotter = QwtImageDisplay('spectra',parent=self.layout_parent)

    self.layout.addWidget(self._visu_plotter, 0, 1)
    QObject.connect(self._visu_plotter, PYSIGNAL('handle_menu_id'), self.update_vells_display) 
    QObject.connect(self._visu_plotter, PYSIGNAL('handle_spectrum_menu_id'), self.update_spectrum_display) 
    QObject.connect(self._visu_plotter, PYSIGNAL('vells_axes_labels'), self.set_ND_controls) 
    QObject.connect(self._visu_plotter, PYSIGNAL('colorbar_needed'), self.set_ColorBar) 

    self.plotPrinter = plot_printer(self._visu_plotter)
    QObject.connect(self._visu_plotter, PYSIGNAL('do_print'), self.plotPrinter.do_print) 
    self.set_widgets(self.layout_parent,self.dataitem.caption,icon=self.icon())
    self._wtop = self.layout_parent;       

  # create_image_plotters

  def set_data (self,dataitem,default_open=None,**opts):
    """ this callback receives data from the meqbrowser, when the
        user has requested a plot. It decides whether the data is
        from a VellSet or visu data record, and  after any
        necessary preprocssing forwards the data to one of
        the functions which does the actual plotting """

    _dprint(3, '** in result_plotter:set_data callback')
    self._rec = dataitem.data;
# if we are single stepping through requests, Oleg may reset the
# cache, so check for a non-data record situation
    if isinstance(self._rec, bool):
      return

    self.label = '';  # extra label, filled in if possible
# there's a problem here somewhere ...
    if dmi_typename(self._rec) != 'MeqResult': # data is not already a result?
      # try to put request ID in label
      rq_id_found = False
      if self._rec.cache.has_key("request_id"):
        self.label = "rq " + str(self._rec.cache.request_id);
        rq_id_found = True
      if self._rec.cache.has_key("result"):
        self._rec = self._rec.cache.result; # look for cache.result record
        if not rq_id_found and self._rec.has_key("request_id"):
          self.label = "rq " + str(self._rec.request_id);
      else:
# cached_result not found, display an empty viewer with a "no result
# in this node record" message (the user can then use the Display with
# menu to switch to a different viewer)
        Message = "No result record was found in the cache, so no plot can be made with the <b>Result Plotter</b>! You may wish to select another type of display."
        cache_message = QLabel(Message,self.wparent())
        cache_message.setTextFormat(Qt.RichText)
        self._wtop = cache_message
        self.set_widgets(cache_message)
        self.reset_plot_stuff()
        return

# update display with current data
    process_result = self.process_data()

# add this data set to internal list for later replay
    if process_result:
      label_found = False
      if len(self.data_list_labels) > 0:
        for i in range(len(self.data_list_labels)):
          if self.data_list_labels[i] == self.label:
            label_found = True
      if not label_found and self.max_list_length > 0:
        self.data_list.append(self._rec)
        self.data_list_labels.append(self.label)
        if len(self.data_list_labels) > self.max_list_length:
          del self.data_list_labels[0]
          del self.data_list[0]
        if len(self.data_list) != self.data_list_length:
          self.data_list_length = len(self.data_list)
          if self.data_list_length > 1:
            _dprint(3, 'calling adjust_selector')
            self.adjust_selector()

  def process_data (self):
    """ process the actual record structure associated with a Cache result """
    process_result = False
# are we dealing with Vellsets?
    if self._rec.has_key("dims"):
      _dprint(3, '*** dims field exists ', self._rec.dims)
    if self._rec.has_key("vellsets") and not self._rec.has_key("cells"):
      Message = "No cells record for vellsets; scalar assumed. No plot can be made with the <b>Result Plotter</b>. Use the record browser to get further information about this vellset." 
      if self._rec.vellsets[0].has_key("value"):
        value = self._rec.vellsets[0].value
        str_value = str(value[0])
        Message = "This vellset " + self.label + "  has scalar value: <b>" + str_value + "</b>";

      cache_message = QLabel(Message,self.wparent())
      cache_message.setTextFormat(Qt.RichText)
      self._wtop = cache_message
      self.set_widgets(cache_message)
      self.reset_plot_stuff()
      return process_result
    if self._rec.has_key("vellsets") or self._rec.has_key("solver_result"):
      if self._visu_plotter is None:
        self.create_image_plotters()
        _dprint(3, 'passed create_image_plotters')
      if self._rec.has_key("vellsets"):
        self.plot_vells_data()
      else:
        self.plot_solver()
      process_result = True
# otherwise we are dealing with a set of visualization data
    else:
      if self._rec.has_key("visu"):
# do plotting of visualization data
        self.display_visu_data()
        _dprint(3, 'passed display_visu_data')
        process_result = True

# enable & highlight the cell
    self.enable();
    self.flash_refresh();
    _dprint(3, 'exiting process_data')
    return process_result

  def replay_data (self, data_index):
    """ callback to redisplay contents of a result record stored in 
        a results history buffer
    """
    if self.ignore_replay:
      self.ignore_replay = False
      return
    if data_index < len(self.data_list):
      self._rec = self.data_list[data_index]
      self.label = self.data_list_labels[data_index]
      self.results_selector.setLabel(self.data_list_labels[data_index])
      process_result = self.process_data()

  def select_spectrum_node (self, data_index):
    """ callback to redisplay contents of a spectrum leaf node stored in 
        a list of leaf nodes
    """
    if self.ignore_replay:
      self.ignore_replay = False
      return
    if data_index < len(self.leaf_node_list):
      leaf = self.leaf_node_list[data_index]
      attrib_list = self.list_attrib_lists[data_index]
      label = self.list_labels[data_index]
      self._visu_plotter.plot_data(leaf, attrib_list,label)
      self.plotSpectra(leaf)

  def plot_vells_data (self):
      """ process incoming vells data and attributes into the
          appropriate type of plot """

# if we are single stepping through requests, Oleg may reset the
# cache, so check for a non-data record situation
      if isinstance(self._rec, bool):
        return

      _dprint(3, 'handling vellsets')
      self._vells_plot = True
      self._visu_plotter.setVellsPlot(self._vells_plot)

      if self._vells_data is None:
        self._vells_data = VellsData()
# store the data
      self._vells_data.StoreVellsData(self._rec,self.label)
      if self.num_possible_ND_axes is None:
        vells_data_parms = self._vells_data.getVellsDataParms()
        vells_axis_parms = vells_data_parms[0]
        axis_labels = vells_data_parms[1]
        self._visu_plotter.setVellsParms(vells_axis_parms, axis_labels)
        self.num_possible_ND_axes = vells_data_parms[2]
        if len(vells_axis_parms) > 2 and self.num_possible_ND_axes > 2:
          self.toggle_array_rank = self.num_possible_ND_axes
          self.set_ND_controls (axis_labels, vells_axis_parms)

        # get initial axis parameters
        axis_parms =  self._vells_data.getActiveAxisParms()
        self._visu_plotter.setAxisParms(axis_parms)

# generate basic menu
      self._visu_plotter.initVellsContextMenu()

      self.raw_data_rank = self._vells_data.getActiveDataRank()

# do we have flags for data?	  
      if self._vells_data.activePlaneHasFlags():
        flag_plane = self._vells_data.getActivePlane()
        self._visu_plotter.set_flag_toggles(flag_plane, True)
        self._visu_plotter.setFlagsData(self._vells_data.getActiveFlagData())

# test and update the context menu
      menu_labels = self._vells_data.getMenuLabels()
      vells_menu_items = len(menu_labels)
      if vells_menu_items > 1:
        self._visu_plotter.setMenuItems(menu_labels)

# plot the appropriate plane / perturbed value
      plot_data = self._vells_data.getActiveData()
      if plot_data.rank != self.old_plot_data_rank:
        self.old_plot_data_rank = plot_data.rank
        # get initial axis parameters
        axis_parms =  self._vells_data.getActiveAxisParms()
        self._visu_plotter.setAxisParms(axis_parms)
      plot_label = self._vells_data.getPlotLabel()
      if not self.test_vells_scalar(plot_data, plot_label):
        self._visu_plotter.plot_vells_array(plot_data, plot_label)

    # end plot_vells_data()

  def plot_solver (self):
    """ plots data from a MeqSolver node """
    if self._solver_data is None:
        self._solver_data = SolverData()
# store the data
    self._solver_data.StoreSolverData(self._rec,self.label)
# retrieve it
    self._solver_array =  self._solver_data.getSolverData()
    (metrics_rank, iteration_number, solver_offsets) = self._solver_data.getSolverMetrics()
    self._visu_plotter.set_solver_metrics(metrics_rank, iteration_number, solver_offsets)
    shape = self._solver_array.shape
    title = ''
    if shape[1] > 1:
      self._x_title = 'Solvable Coeffs'
      self._y_title = 'Iteration Nr'
      title = self.label + " Solver Incremental Solutions"
    else:
      self._y_title = 'Value'
      self._x_title = 'Iteration Nr'
      title = self.label + " Solver Incremental Solution"
    self._visu_plotter.array_plot(title, self._solver_array)

  def test_vells_scalar (self, data_array, data_label):
    """ test if incoming Vells contains only a scalar value """
# do we have a scalar?
    is_scalar = False
    scalar_data = 0.0
    try:
      shape = data_array.shape
      _dprint(3,'data_array shape is ', shape)
    except:
      is_scalar = True
      scalar_data = data_array
    if not is_scalar and len(shape) == 1:
      if shape[0] == 1:
        is_scalar = True
        scalar_data = data_array[0]
    if is_scalar:
      self._visu_plotter.report_scalar_value(data_label, scalar_data)
      return True
    else:
      return False

  def update_vells_display (self, menuid):
    """ callback to handle a request from the lower level 
        display_image.py code for different Vells data """
    self._vells_data.unravelMenuId(menuid)
    plot_label = self._vells_data.getPlotLabel()
    plot_data = self._vells_data.getActiveData()
    raw_data_rank = self._vells_data.getActiveDataRank()
    if self.raw_data_rank != raw_data_rank:
      self.old_plot_data_rank = plot_data.rank
      self.raw_data_rank = raw_data_rank
      # get initial axis parameters
      axis_parms =  self._vells_data.getActiveAxisParms()
      self._visu_plotter.setAxisParms(axis_parms)
    self._visu_plotter.reset_color_bar(True)
    if not self.test_vells_scalar(plot_data, plot_label):
      self._visu_plotter.plot_vells_array(plot_data, plot_label)

  def update_spectrum_display(self, menuid):
    """ callback to handle a request from the lower level 
        display_image.py code for different Spectrum data """
    self._spectrum_data.setActivePlot(menuid)
    plot_label = self._spectrum_data.getPlotLabel()
    plot_data = self._spectrum_data.getActivePlotArray()
    self._visu_plotter.array_plot(plot_label, plot_data, False)

  def setSelectedAxes (self,first_axis, second_axis):
    """ callback to handle a request from the N-dimensional
        controller to set new (sub)axes for the Vells display 
    """
    self._visu_plotter.delete_cross_sections()
    if self._vells_plot:
      self._vells_data.setSelectedAxes(first_axis, second_axis)
      axis_parms = self._vells_data.getActiveAxisParms()
      self._visu_plotter.setAxisParms(axis_parms)
      self._visu_plotter.delete_cross_sections()
      plot_array = self._vells_data.getActiveData()
      self._visu_plotter.array_plot(" ", plot_array)

  def setArraySelector (self,lcd_number, slider_value, display_string):
    """ callback to handle a request from the N-dimensional
        controller that the user has changed an index into a dimension 
    """
    self._vells_data.updateArraySelector(lcd_number,slider_value)
    if self._vells_plot:
      plot_array = self._vells_data.getActiveData()
      self._visu_plotter.array_plot('data: '+ display_string, plot_array)

  def adjust_selector (self):
    """ instantiate and/or adjust contents of ResultsRange object """
    if self.results_selector is None:
      self.results_selector = ResultsRange(self.layout_parent)
      self.results_selector.setMaxValue(self.max_list_length)
      self.layout.addWidget(self.results_selector, 1,1)
      self.results_selector.show()
      QObject.connect(self.results_selector, PYSIGNAL('result_index'), self.replay_data)
      QObject.connect(self.results_selector, PYSIGNAL('adjust_results_buffer_size'), self.set_results_buffer)
      self._visu_plotter.setResultsSelector()
      if self._plot_type == 'realvsimag':
        QObject.connect(self._visu_plotter.plot, PYSIGNAL('show_results_selector'), self.show_selector)
      else:
        QObject.connect(self._visu_plotter, PYSIGNAL('show_results_selector'), self.show_selector)
    self.ignore_replay = True
    self.results_selector.setRange(self.data_list_length)
    self.results_selector.setLabel(self.label)

  def show_selector (self, do_show_selector):
    """ callback to show or hide a ResultsRange object """
    if do_show_selector:
      self.results_selector.show()
    else:
      self.results_selector.hide()

  def adjust_spectrum_selector (self):
    """ instantiate and/or adjust contents of ResultsRange object """
    if self.spectrum_node_selector is None:
      self.spectrum_node_selector = ResultsRange(self.layout_parent)
      self.spectrum_node_selector.setStringInfo(' spectrum ')
      self.layout.addWidget(self.spectrum_node_selector, 2,1)
      self.spectrum_node_selector.show()
      QObject.connect(self.spectrum_node_selector, PYSIGNAL('result_index'), self.select_spectrum_node)
#     QObject.connect(self.spectrum_node_selector, PYSIGNAL('adjust_results_buffer_size'), self.set_spectrum_node_buffer)
      QObject.connect(self._visu_plotter, PYSIGNAL('show_results_selector'), self.show_spectrum_selector)
    self.ignore_replay = True
    self.spectrum_node_selector.setMaxValue(len(self.leaf_node_list),False)
    self.spectrum_node_selector.setRange(len(self.leaf_node_list), False)
    self.spectrum_node_selector.setLabel(self.label)
    self.spectrum_node_selector.disableContextmenu()
    

  def show_spectrum_selector (self, do_show_selector):
    """ callback to show or hide a ResultsRange object """
    if do_show_selector:
      self.spectrum_node_selector.show()
    else:
      self.spectrum_node_selector.hide()

  def set_results_buffer (self, result_value):
    """ callback to set the number of results records that can be
        stored in a results history buffer 
    """ 
    if result_value < 0:
      return
    self.max_list_length = result_value
    if len(self.data_list_labels) > self.max_list_length:
      differ = len(self.data_list_labels) - self.max_list_length
      for i in range(differ):
        del self.data_list_labels[0]
        del self.data_list[0]

    if len(self.data_list) != self.data_list_length:
      self.data_list_length = len(self.data_list)

  def set_ND_controls (self, labels, parms):
    """ this function adds the extra GUI control buttons etc if we are
        displaying data for a numarray of dimension 3 or greater """

    _dprint(3, 'in result_plotter:set_ND_controls so we must have caught a vells_axes_labels signal')
 
# make sure we can toggle ND controller by telling plotter 
# that array rank is at least 3
    self._visu_plotter.set_toggle_array_rank(3)

    shape = None
    self.ND_Controls = ND_Controller(shape, labels, parms, self.layout_parent)
    QObject.connect(self.ND_Controls, PYSIGNAL('sliderValueChanged'), self.setArraySelector)
    QObject.connect(self.ND_Controls, PYSIGNAL('defineSelectedAxes'), self.setSelectedAxes)
    QObject.connect(self._visu_plotter, PYSIGNAL('reset_axes_labels'), self.ND_Controls.redefineAxes) 
    QObject.connect(self._visu_plotter, PYSIGNAL('show_ND_Controller'), self.ND_Controls.showDisplay)
    self.layout.addMultiCellWidget(self.ND_Controls,2,2,0,2)
    self.ND_Controls.show()

  def set_ColorBar (self):
    """ this function adds a colorbar for 2 Ddisplays """

    # create two color bars in case we are displaying complex arrays
    self.colorbar = {}
    for i in range(2):
      self.colorbar[i] =  QwtColorBar(colorbar_number= i, parent=self.layout_parent)
      self.colorbar[i].setMaxRange((-1, 1))
      QObject.connect(self._visu_plotter, PYSIGNAL('max_image_range'), self.colorbar[i].setMaxRange) 
      QObject.connect(self._visu_plotter, PYSIGNAL('display_type'), self.colorbar[i].setDisplayType) 
      QObject.connect(self._visu_plotter, PYSIGNAL('show_colorbar_display'), self.colorbar[i].showDisplay)
      QObject.connect(self.colorbar[i], PYSIGNAL('set_image_range'), self._visu_plotter.setImageRange) 
      if i == 0:
        self.layout.addWidget(self.colorbar[i], 0, i)
        self.colorbar[i].show()
      else:
        self.layout.addWidget(self.colorbar[i], 0, 2)
        self.colorbar[i].hide()
    self.plotPrinter.add_colorbar(self.colorbar)

Grid.Services.registerViewer(dmi_type('MeqResult',record),ResultPlotter,priority=10)
Grid.Services.registerViewer(meqds.NodeClass('MeqDataCollect'),ResultPlotter,priority=10)
Grid.Services.registerViewer(meqds.NodeClass('MeqDataConcat'),ResultPlotter,priority=10)
Grid.Services.registerViewer(meqds.NodeClass(),ResultPlotter,priority=22)

