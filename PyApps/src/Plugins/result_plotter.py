#!/usr/bin/python

# modules that are imported
from math import sin
from math import cos
from math import pow
from math import sqrt

# modules that are imported
from Timba.dmi import *
from Timba import utils
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI import widgets
from Timba.GUI.browsers import *
from Timba import Grid

from qt import *
from numarray import *
from Timba.Plugins.display_image import *
from Timba.Plugins.realvsimag import *

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
    self._hippo = None
    self._visu_plotter = None
    self._window_controller = None
    self._plot_type = None
    self._wtop = None;
    self.dataitem = dataitem
    self._attributes_checked = False

    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

  def __del__(self):
    if self._window_controller:
      self._window_controller.closeAllWindows()
                                                                                           
# function needed by Oleg for reasons known only to him!
  def wtop (self):
    return self._wtop;
    

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
           Message = plot_color + " is not a valid color.\n Using blue by default"
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
           Message = plot_color + " is not a valid color.\n Using blue by default"
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
           Message = plot_color + " is not a valid color.\n Using blue by default"
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
           Message = plot_line_style + " is not a valid line style.\n Using dots by default"
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
           Message = plot_line_style + " is not a valid line style for mean circles.\n Using lines by default"
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
           Message = plot_line_style + " is not a valid line style for stddev circles.\n Using DotLine by default"
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
          _dprint(3, 'attrib_parms ',  attrib_parms, ' has length ', len( attrib_parms));
          _dprint(3, 'processing attribute list ',i, ' ', attrib_parms);
          if attrib_parms.has_key('plot'):
            plot_parms = attrib_parms.get('plot')
            _dprint(3, '*** plot_parms ',  plot_parms, ' has length ', len( plot_parms));
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
        _dprint(3, 'pre_work setting visu_plotter to QwtImagePlot for spectra!')
        self._visu_plotter = QwtImagePlot(self._plot_type,parent=self.wparent())
        self.set_widgets(self._visu_plotter,self.dataitem.caption,icon=self.icon())
        self._wtop = self._visu_plotter;       # QwtImagePlot inherits from QwtPlot

      if self._plot_type == 'realvsimag':
        _dprint(3, 'pre_work setting visu_plotter to realvsimag_plotter!')
        self._visu_plotter = realvsimag_plotter(self._plot_type,parent=self.wparent())
        self.set_widgets(self._visu_plotter.plot,self.dataitem.caption,icon=self.icon())
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
      self._wtop = self._visu_plotter.plot;  # plot widget is our top widget

# now do the plotting
    self._visu_plotter.plot_data(leaf, attrib_list)

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
# if not a leaf, and we find a 'value' field, then call
# recursive method 'tree_traversal'
        if node.has_key('value'):
          self.tree_traversal(node['value'], node['label'], attribute_list)
      else:
        _dprint(3, 'tree: leaf node has label(s) ', node['label'])
        _dprint(3, 'tree: leaf node has incoming label ', label)
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
      if self._visu_plotter is None:
        self._visu_plotter = QwtImagePlot('spectra',parent=self.wparent())
        self._wtop = self._visu_plotter;       # QwtImagePlot inherits from QwtPlot
      self._visu_plotter.plot_vells_data(self._rec)
# otherwise we are dealing with a set of visualization data
    else:
      if self._rec.has_key("visu"):
# do plotting of visualization data
        self.display_visu_data()

# enable & highlight the cell
    self.enable();
    self.flash_refresh();


    _dprint(3, 'exiting set_data')

Grid.Services.registerViewer(dict,ResultPlotter,dmitype='meqresult',priority=10)
