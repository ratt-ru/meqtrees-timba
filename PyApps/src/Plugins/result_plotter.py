#!/usr/bin/python

# modules that are imported

#% $Id: result_plotter.py 6419 2008-10-03 10:17:35Z oms $ 

#
# Copyright (C) 2002-2007
# ASTRON (Netherlands Foundation for Research in Astronomy)
# and The MeqTree Foundation
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from math import sin
from math import cos
from math import pow
from math import sqrt
import string

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
from Timba.Plugins.display_image import *
from Timba.Plugins.realvsimag import *
from Timba.Plugins.plotting_functions import *

global has_vtk
has_vtk = False
try:
  from Timba.Plugins.vtk_qt_3d_display import *
  has_vtk = True
except:
  pass

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
    self.active_image_index = None
    self._spectrum_data = None
    self.png_number = 0
    self.data_list = []
    self.data_list_labels = []
    self.data_list_length = 0
    self.max_list_length = 50
    self._window_controller = None
    self.array_shape = None
    self.actual_rank = None
    self.plot_3D = False
    self.ND_plotter = None
    self.ND_labels = None
    self.ND_parms = None 
    self.layout_created = False

    self.reset_plot_stuff()

# back to 'real' work
    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

  def reset_plot_stuff(self):
    """ resets widgets to None. Needed if we have been putting
        out a message about Cache not containing results, etc
    """
    self._visu_plotter = None
    self.QTextEdit = None
    self.colorbar = {}
    self.results_selector = None
    self.spectrum_node_selector = None
    self.status_label = None
    self.ND_Controls = None
    self.ND_plotter = None
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
    self._visu_plotter.array_plot(plot_data, data_label=plot_label,flip_axes=False)

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

# create grid layout for widgets
      self.create_layout_stuff()

      if self._plot_type == 'spectra':
        _dprint(3, 'pre_work setting visu_plotter to QwtImageDisplay for spectra!')
        self.create_2D_plotter()

      if self._plot_type == 'realvsimag':
        _dprint(3, 'pre_work setting visu_plotter to realvsimag_plotter!')

        self._visu_plotter = realvsimag_plotter(self._plot_type,parent=self.layout_parent)
        QObject.connect(self._visu_plotter.plot, PYSIGNAL('save_display'), self.grab_display) 
        self.layout.addWidget(self._visu_plotter.plot, 0, 1)
        self._visu_plotter.plot.show()
        _dprint(3, 'issued show call to realvsimag self._visu_plotter')


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
      QObject.connect(self._visu_plotter.plot, PYSIGNAL('save_display'), self.grab_display) 
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

  def create_layout_stuff(self):
    """ create grid layouts into which plotter widgets are inserted """
    if self.layout_parent is None or not self.layout_created:
      self.layout_parent = QWidget(self.wparent())
      self.layout = QGridLayout(self.layout_parent)
      self.QTextEdit = QTextEdit(self.layout_parent)
      self.layout.addWidget(self.QTextEdit, 0, 1)
      self.QTextEdit.hide()
      self.QTextEdit.setReadOnly(True)
      self.set_widgets(self.layout_parent,self.dataitem.caption,icon=self.icon())
      self.layout_created = True
    self._wtop = self.layout_parent;       

  def create_2D_plotter(self):
    self._visu_plotter, self.plotPrinter = create_2D_Plotters(self.layout, self.layout_parent, self.ND_plotter)
    QObject.connect(self._visu_plotter, PYSIGNAL('handle_menu_id'), self.update_vells_display) 
    QObject.connect(self._visu_plotter, PYSIGNAL('handle_spectrum_menu_id'), self.update_spectrum_display) 
    QObject.connect(self._visu_plotter, PYSIGNAL('colorbar_needed'), self.set_ColorBar) 
    QObject.connect(self._visu_plotter, PYSIGNAL('show_ND_Controller'), self.ND_controller_showDisplay)
    QObject.connect(self._visu_plotter, PYSIGNAL('show_3D_Display'), self.show_3D_Display)
    QObject.connect(self._visu_plotter, PYSIGNAL('do_print'), self.plotPrinter.do_print) 
    QObject.connect(self._visu_plotter, PYSIGNAL('save_display'), self.grab_display) 
    QObject.connect(self._visu_plotter, PYSIGNAL('full_vells_image'), self.request_full_image) 
    # create status label display
    self.status_label = QLabel(self.layout_parent)
    sansFont = QFont( "Helvetica [Cronyx]", 8 )
    self.status_label.setFont(sansFont)
    self.layout.addMultiCellWidget(self.status_label,1,1,0,2)
    self.status_label.setText("Move the mouse within the plot canvas"
                            " to show the cursor position.")
    self.status_label.show()
    QObject.connect(self._visu_plotter, PYSIGNAL('status_update'), self.update_status)

  # create_2D_plotter

  def update_status(self, status):
     if not status is None:
       self.status_label.setText(status)


  def grab_display(self, title):
    self.png_number = self.png_number + 1
    png_str = str(self.png_number)
    if title is None:
      save_file = './meqbrowser' + png_str + '.png'
    else:
      save_file = title + png_str + '.png'
    save_file_no_space= save_file.replace(' ','_')
    result = QPixmap.grabWidget(self.layout_parent).save(save_file_no_space, "PNG")

    
  def set_data (self,dataitem,default_open=None,**opts):
    """ this callback receives data from the meqbrowser, when the
        user has requested a plot. It decides whether the data is
        from a VellSet or visu data record, and  after any
        necessary preprocssing forwards the data to one of
        the functions which does the actual plotting """

    _dprint(3, '** in result_plotter:set_data callback')
    self._rec = dataitem.data;
    _dprint(3, 'set_data: initial self._rec ', self._rec)
# if we are single stepping through requests, Oleg may reset the
# cache, so check for a non-data record situation
    if self._rec is None:
      return
    if isinstance(self._rec, bool):
      return

# if this node is a Composer, it might have a plot_label which we
# want to use later
    try:
      self._plot_label = self._rec.plot_label
    except:
      self._plot_label = None

    self.label = '';  # extra label, filled in if possible
# there's a problem here somewhere ...
    if dmi_typename(self._rec) != 'MeqResult': # data is not already a result?
      # try to put request ID in label
      rq_id_found = False
      data_failure = False
      try:
        if self._rec.cache.has_key("request_id"):
          self.label = "rq " + str(self._rec.cache.request_id);
          rq_id_found = True
        if self._rec.cache.has_key("result"):
          self._rec = self._rec.cache.result; # look for cache.result record
          if not rq_id_found and self._rec.has_key("request_id"):
            self.label = "rq " + str(self._rec.request_id);
        else:
          data_failure = True
        _dprint(3, 'we have req id ', self.label)
      except:
        data_failure = True
      if data_failure:
        _dprint(3, ' we have a data failure')
# cached_result not found, display an empty viewer with a "no result
# in this node record" message (the user can then use the Display with
# menu to switch to a different viewer)
        Message = "No cache result record was found for this node, so no plot can be made."
        cache_message = QLabel(Message,self.wparent())
        cache_message.setTextFormat(Qt.RichText)
        self._wtop = cache_message
        self.set_widgets(cache_message)
        self.reset_plot_stuff()

        return

# check for label matching - this is necessary as a node may be called
# by multiple parents, and thus send the same result to the display
# more than once
    label_found = False
    if len(self.data_list_labels) > 0:
      for i in range(len(self.data_list_labels)):
        if self.data_list_labels[i] == self.label:
          label_found = True
    if not label_found and self.max_list_length > 0:
# update display with current data
      process_result = self.process_data()
# add this data set to internal list for later replay if result was OK
      if process_result:
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

    if self._rec.has_key("vellsets") or self._rec.has_key("solver_result"):
      self.create_layout_stuff()
      if self._rec.has_key("vellsets"):
        process_result = self.plot_vells_data()
        if not process_result:
          Message = "The result record for this node had no valid data, so no plot can be made."
          cache_message = QLabel(Message,self.wparent())
          cache_message.setTextFormat(Qt.RichText)
          self._wtop = cache_message
          self.set_widgets(cache_message)
          self.reset_plot_stuff()
      else:
        if self._visu_plotter is None:
          self.create_2D_plotter()
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
    if data_index < len(self.data_list):
      self._rec = self.data_list[data_index]
      self.label = self.data_list_labels[data_index]
      self.results_selector.setLabel(self.label)
      process_result = self.process_data()

  def select_spectrum_node (self, data_index):
    """ callback to redisplay contents of a spectrum leaf node stored in 
        a list of leaf nodes
    """
    if data_index < len(self.leaf_node_list):
      leaf = self.leaf_node_list[data_index]
      attrib_list = self.list_attrib_lists[data_index]
      label = self.list_labels[data_index]
      self._visu_plotter.plot_data(leaf, attrib_list,label)
      self.plotSpectra(leaf)

  def plot_vells_data (self, store_rec=True):
      """ process incoming vells data and attributes into the
          appropriate type of plot """

# if we are single stepping through requests, Oleg may reset the
# cache, so check for a non-data record situation
      if store_rec and isinstance(self._rec, bool):
        return

      _dprint(3, 'handling vellsets')

# store the data
      if self._vells_data is None:
        self._vells_data = VellsData()

      self._vells_data.set_3D_Display(False)

      if store_rec:
        self._vells_data.setInitialSelection(False)
        if not self._plot_label is None:
          self._vells_data.set_exterior_plot_label(self._plot_label)
        self._vells_data.StoreVellsData(self._rec,self.label)

      if self._vells_data.isVellsScalar():
        if not self._visu_plotter is None:
          self._visu_plotter.hide()
        Message =  self._vells_data.getScalarString()
        if Message.find("has no data") > -1:
          return False
        else:
          self.QTextEdit.setText(Message)
          self.QTextEdit.show()
          return True

      self._vells_plot = True

      if self._visu_plotter is None:
        if not self.ND_Controls is None:
          self.ND_Controls.reparent(QWidget(), 0, QPoint())
          self.ND_Controls = None
        ranks = self._vells_data.getActiveDataRanks()
        self.create_2D_plotter()
        self._vells_data.setInitialSelectedAxes(ranks[1],ranks[2], reset=True)

      self._visu_plotter.setVellsPlot(self._vells_plot)

# vells axes can change even if data shape has not changed
# so we need to always call this function
      self.update_display_control()

# generate basic menu
      self._visu_plotter.initVellsContextMenu()

# do we have flags for data?	  
      self.test_for_flags()

# test and update the context menu
      menu_data = self._vells_data.getMenuData()
      menu_labels = menu_data[0]
      vells_menu_items = len(menu_labels)
      if vells_menu_items > 1:
        self._visu_plotter.setMenuItems(menu_data)

      if not menu_data[4] is None and len(menu_data[4]) > 0:
        self._visu_plotter.setBigArrays(menu_data[4])

# reset color bar request - just in case
      self._visu_plotter.reset_color_bar(True)

# plot the appropriate plane / perturbed value
# we make a deep copy as the plot array may be modified by flagging etc
# during plotting
      plot_data = self._vells_data.getActiveData().copy()

      # get initial axis parameters
      axis_parms =  self._vells_data.getActiveAxisParms()
      self._visu_plotter.setAxisParms(axis_parms)
      plot_label = self._vells_data.getPlotLabel()
      if not self.test_vells_scalar(plot_data, plot_label):
        black_colour = 0
        self._visu_plotter.setFlagColour(black_colour)
        self._visu_plotter.plot_vells_array(plot_data, plot_label)

      return True
    # end plot_vells_data()

  def test_for_flags(self):
    flag_plane = self._vells_data.getActivePlane()
    if self._vells_data.activePlaneHasFlags():
      self._visu_plotter.set_flag_toggles(flag_plane, True)
      self._visu_plotter.setFlagsData(self._vells_data.getActiveFlagData())
    else:
      self._visu_plotter.set_flag_toggles(flag_plane, False)
      self._visu_plotter.unsetFlagsData()

  def request_full_image(self,signal):
    """ request a full filled-in image from the Vells """
    self._vells_data.request_full_image(signal)
    plot_data = self._vells_data.getActiveData().copy()
    # get initial axis parameters
    axis_parms =  self._vells_data.getActiveAxisParms()
    self._visu_plotter.setAxisParms(axis_parms)
    plot_label = self._vells_data.getPlotLabel()
    if signal:
      if not self.test_vells_scalar(plot_data, plot_label):
        white_colour = 255
        self._visu_plotter.setFlagColour(white_colour)
    else:
      self.test_for_flags()
      black_colour = 0
      self._visu_plotter.setFlagColour(black_colour)
    self._visu_plotter.plot_vells_array(plot_data, plot_label)

  def update_display_control (self):
      vells_data_parms = self._vells_data.getVellsDataParms()
      vells_axis_parms = vells_data_parms[0]
      axis_labels = vells_data_parms[1]
      _dprint(3, 'vells_axis_parms ', vells_axis_parms)
      self._visu_plotter.setVellsParms(vells_axis_parms, axis_labels)
      display_change = False
      if vells_data_parms[2] != self.num_possible_ND_axes:
        self.num_possible_ND_axes = vells_data_parms[2]
        display_change = True

      if vells_data_parms[3] != self.array_shape:
        self.array_shape = vells_data_parms[3]
        display_change = True

      ranks = self._vells_data.getActiveDataRanks()
      _dprint(3, 'received ranks ', ranks)
      actual_rank = ranks[0]
      self.array_rank = ranks[1]
      self.array_shape = ranks[2]
      _dprint(3, 'actual plot array rank ', actual_rank)
      _dprint(3, 'self.actual_rank ', self.actual_rank)
      if self.actual_rank != actual_rank:
        self.actual_rank = actual_rank
        display_change = True
      self._visu_plotter.set_original_array_rank(self.actual_rank)
      _dprint(3, ' set_original_array_rank set to ', self.actual_rank)
      if self.actual_rank > 2 and self.ND_Controls is None:
         display_change = True
      if self.actual_rank <= 2 and not self.ND_Controls is None:
         self.ND_Controls.hide()
      _dprint(3, 'display_change ', display_change)
      if display_change and self.actual_rank > 2:
        _dprint(3, 'calling set_ND_controls')
        # store for later use
        self.ND_labels = axis_labels
        self.ND_parms = vells_axis_parms 
        self.set_ND_controls(labels=axis_labels, parms=vells_axis_parms)
      else:
        if len(vells_axis_parms) <= 2 or self.num_possible_ND_axes <= 2 or self.actual_rank <= 2:
          if not self.ND_Controls is None:
            self.ND_Controls.hide()

  def plot_solver (self):
    """ plots data from a MeqSolver node """
    if self._solver_data is None:
        self._solver_data = SolverData()
# store the data
    self._solver_data.StoreSolverData(self._rec,self.label)

# refresh plotter in case of solver data
    self._visu_plotter.cleanup()

# try calculating condition numbers
    if self._solver_data.processCovarArray():
      self._visu_plotter.set_condition_numbers(self._solver_data.getConditionNumbers())
#   else:
#     Message = "Failure to calculate Covariance Matrix condition number!\nIs the numpy package installed?"
#     mb = QMessageBox("result_plotter.py",
#          Message,
#          QMessageBox.Warning,
#          QMessageBox.Ok | QMessageBox.Default,
#          QMessageBox.NoButton,
#          QMessageBox.NoButton)
#     mb.exec_loop()

    if self._solver_data.calculateCovarEigenVectors():
      self._visu_plotter.set_eigenvectors(self._solver_data.getEigenVectors())

# retrieve solver data
    self._solver_array =  self._solver_data.getSolverData()
    self._visu_plotter.set_solver_metrics(self._solver_data.getSolverMetrics())
    self._visu_plotter.set_solver_labels(self._solver_data.getSolverLabels())
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
    self._visu_plotter.array_plot(self._solver_array,data_label=title)

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
    if not is_scalar:
      test_scalar = True
      for i in range(len(shape)):
        if shape[i] > 1:
          test_scalar = False
      is_scalar = test_scalar
      if is_scalar:
        scalar_data = data_array
    if is_scalar:
      self._visu_plotter.report_scalar_value(data_label, scalar_data)
      return True
    else:
      return False

  def update_vells_display (self, menuid):
    """ callback to handle a request from the lower level 
        display_image.py code for different Vells data """
    _dprint(3, 'starting update_vells_display')
     
    self._vells_data.unravelMenuId(menuid)
    plot_label = self._vells_data.getPlotLabel()
    plot_data = self._vells_data.getActiveData().copy()

# do we have flags for data?	  
    self.test_for_flags()

    if self._vells_data.getShapeChange():
      self.update_display_control()
      axis_parms =  self._vells_data.getActiveAxisParms()
      self._visu_plotter.setAxisParms(axis_parms)
    self._visu_plotter.reset_color_bar(True)
    if self._vells_data.isVellsScalar():
#     self._visu_plotter.report_scalar_value(plot_label, plot_data)
      if not self._visu_plotter is None:
        self._visu_plotter.hide()
      Message =  self._vells_data.getScalarString()
      if Message.find("has no data") > -1:
        return 
      else:
        self.QTextEdit.setText(Message)
        self.QTextEdit.show()
        return
    else:
      if not self.test_vells_scalar(plot_data, plot_label):
        if not self.QTextEdit is None:
          self.QTextEdit.hide()
        if not self._visu_plotter is None:
          self._visu_plotter.show()
        black_colour = 0
        self._visu_plotter.setFlagColour(black_colour)
        self._visu_plotter.plot_vells_array(plot_data, plot_label)

  def update_spectrum_display(self, menuid):
    """ callback to handle a request from the lower level 
        display_image.py code for different Spectrum data 
    """
    self._spectrum_data.setActivePlot(menuid)
    plot_label = self._spectrum_data.getPlotLabel()
    plot_data = self._spectrum_data.getActivePlotArray()
    self._visu_plotter.array_plot(plot_data, data_label=plot_label, flip_axes=False)

  def setSelectedAxes (self,first_axis, second_axis, third_axis=-1):
    """ callback to handle a request from the N-dimensional
        controller to set new (sub)axes for the Vells display 
    """
    if self._vells_plot:
      self._vells_data.setSelectedAxes(first_axis, second_axis, third_axis)
      axis_parms = self._vells_data.getActiveAxisParms()
      plot_array = self._vells_data.getActiveData().copy()
      if not self._visu_plotter is None:
        self._visu_plotter.delete_cross_sections()
        self._visu_plotter.setAxisParms(axis_parms)
        self._visu_plotter.array_plot(plot_array)
      else:
        if not self.ND_plotter is None:
          self.ND_plotter.delete_vtk_renderer()
          self.ND_plotter.array_plot(plot_array)
          self.ND_plotter.setAxisParms(axis_parms)


  def setArraySelector (self,lcd_number, slider_value, display_string):
    """ callback to handle a request from the N-dimensional
        controller that the user has changed an index into a dimension 
    """
    if self._vells_plot:
      self._vells_data.updateArraySelector(lcd_number,slider_value)
      plot_array = self._vells_data.getActiveData().copy()
      if not self._visu_plotter is None:
        self._visu_plotter.reset_color_bar(True)
        self._visu_plotter.array_plot(plot_array, data_label='data: '+ display_string)
      else:
        if not self.ND_plotter is None:
          self.ND_plotter.array_plot(plot_array, data_label='data: '+ display_string)

  def adjust_selector (self):
    """ instantiate and/or adjust contents of ResultsRange object """
    if self.results_selector is None:
      self.results_selector = ResultsRange(self.layout_parent)
      self.results_selector.setMaxValue(self.max_list_length)
      self.results_selector.set_offset_index(0)
      self.layout.addWidget(self.results_selector, 3,1,Qt.AlignHCenter)
      self.results_selector.show()
      QObject.connect(self.results_selector, PYSIGNAL('result_index'), self.replay_data)
      QObject.connect(self.results_selector, PYSIGNAL('adjust_results_buffer_size'), self.set_results_buffer)
      if not self._visu_plotter is None:
        self._visu_plotter.setResultsSelector()
      if self._plot_type == 'realvsimag':
        QObject.connect(self._visu_plotter.plot, PYSIGNAL('show_results_selector'), self.show_selector)
      else:
        if not self._visu_plotter is None:
          QObject.connect(self._visu_plotter, PYSIGNAL('show_results_selector'), self.show_selector)
    self.results_selector.set_emit(False)
    self.results_selector.setRange(self.data_list_length-1)
    self.results_selector.setLabel(self.label)
    self.results_selector.set_emit(True)

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
      self.layout.addWidget(self.spectrum_node_selector, 5, 1, Qt.AlignHCenter)
      self.spectrum_node_selector.show()
      QObject.connect(self.spectrum_node_selector, PYSIGNAL('result_index'), self.select_spectrum_node)
#     QObject.connect(self.spectrum_node_selector, PYSIGNAL('adjust_results_buffer_size'), self.set_spectrum_node_buffer)
      QObject.connect(self._visu_plotter, PYSIGNAL('show_results_selector'), self.show_spectrum_selector)
    self.spectrum_node_selector.set_emit(False)
    self.spectrum_node_selector.setMaxValue(len(self.leaf_node_list),False)
    self.spectrum_node_selector.setRange(len(self.leaf_node_list), False)
    self.spectrum_node_selector.setLabel(self.label)
    self.spectrum_node_selector.disableContextmenu()
    self.spectrum_node_selector.set_emit(True)
    

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

  def ND_controller_showDisplay(self, show_self):
    """ tells ND_Controller to show or hide itself """
    if not self.ND_Controls is None:
      self.ND_Controls.showDisplay(show_self)

  def set_ND_controls (self, labels=None, parms=None, num_axes=2):
    """ this function adds the extra GUI control buttons etc if we are
        displaying data for a numpy array of dimension 3 or greater """

    self.ND_Controls = create_ND_Controls(self.layout, self.layout_parent, self.array_shape, self.ND_Controls, self.ND_plotter, labels, parms, num_axes)

    QObject.connect(self.ND_Controls, PYSIGNAL('sliderValueChanged'), self.setArraySelector)
    QObject.connect(self.ND_Controls, PYSIGNAL('defineSelectedAxes'), self.setSelectedAxes)

  def show_3D_Display(self, display_flag_3D):
    if not has_vtk:
      return
    if self._vells_data is None:
      Message = '3D displays are not yet implemented for this data type'
      mb_color = QMessageBox("result_plotter.py",
                 Message,
                 QMessageBox.Warning,
                 QMessageBox.Ok | QMessageBox.Default,
                 QMessageBox.NoButton,
                 QMessageBox.NoButton)
      mb_color.exec_loop()
      return
    axis_increments = None
    if not display_flag_3D:
      plot_array = self._vells_data.getActiveData().copy()
      if plot_array.min() == plot_array.max():
        return
    axis_increments = self._visu_plotter.getActiveAxesInc()

    _dprint(3, 'got 3D plot request, deleting 2-D stuff')
    self._visu_plotter = delete_2D_Plotters(self.colorbar, self._visu_plotter)
    self.status_label.reparent(QWidget(), 0, QPoint())
    self.status_label = None

    if self.ND_plotter is None:
      self.ND_plotter = create_ND_Plotter (self.layout, self.layout_parent)
      QObject.connect(self.ND_plotter, PYSIGNAL('show_2D_Display'), self.show_2D_Display)
      QObject.connect(self.ND_plotter, PYSIGNAL('show_ND_Controller'), self.ND_controller_showDisplay)
    else:
      self.ND_plotter.delete_vtk_renderer()
      self.ND_plotter.show_vtk_controls()

# create 3-D Controller
    if display_flag_3D:
      self.set_ND_controls(self.ND_labels, self.ND_parms,num_axes=3)

      self._vells_data.set_3D_Display(display_flag_3D)
      self._vells_data.setInitialSelectedAxes(self.array_rank,self.array_shape,reset=True)
    else:
      if not self.ND_Controls is None:
        self.ND_Controls.reparent(QWidget(), 0, QPoint())
        self.ND_Controls = None
    self.axis_parms = self._vells_data.getActiveAxisParms()
    plot_array = self._vells_data.getActiveData().copy()
    if plot_array.min() == plot_array.max():
      return
    
    self.ND_plotter.array_plot(plot_array)
    self.ND_plotter.setAxisParms(self.axis_parms)
    if not axis_increments is None:
      self.ND_plotter.setAxisIncrements(axis_increments)

  def show_2D_Display(self, display_flag):
    _dprint(3, 'in show_2D_Display ')
    self.create_2D_plotter()
# create 3-D Controller appropriate for 2-D screen displays
    _dprint(3, 'calling set_ND_controls with self.ND_labels, self.ND_parms ', self.ND_labels, ' ', self.ND_parms)
    self.set_ND_controls(self.ND_labels, self.ND_parms,num_axes=2)
    self._vells_data.set_3D_Display(False)
    _dprint(3, 'calling setInitialSelectedAxes with reset=True, and self.array_rank,self.array_shape ', self.array_rank, ' ', self.array_shape)
    self._vells_data.setInitialSelectedAxes(self.array_rank,self.array_shape, reset=True)
    self._visu_plotter.set_original_array_rank(3)
    self.plot_vells_data(store_rec=False)

  def set_ColorBar (self):
    """ this function adds a colorbar for 2-D displays """
    # create two color bars in case we are displaying complex arrays
    self.colorbar = create_ColorBar(self.layout, self.layout_parent, self._visu_plotter, self.plotPrinter)

Grid.Services.registerViewer(dmi_type('MeqResult',record),ResultPlotter,priority=10)
Grid.Services.registerViewer(meqds.NodeClass('MeqDataCollect'),ResultPlotter,priority=10)
Grid.Services.registerViewer(meqds.NodeClass('MeqDataConcat'),ResultPlotter,priority=10)
Grid.Services.registerViewer(meqds.NodeClass(),ResultPlotter,priority=22)

