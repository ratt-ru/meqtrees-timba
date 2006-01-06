#!/usr/bin/python

# modules that are imported
from Timba.dmi import *
from Timba import utils
from Timba.Meq import meqds
from Timba.Meq.meqds import mqs
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI import widgets
from Timba.GUI.browsers import *
from Timba import Grid

from Timba.Plugins.display_image import *

from Timba.utils import verbosity
_dbg = verbosity(0,name='array_plotter');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;


from numarray import *
from qt import *
from qwt import *
from QwtPlotImage import *
from QwtColorBar import *
from ND_Controller import *
from plot_printer import *

from vtk_qt_3d_display import *


class ArrayPlotter(GriddedPlugin):
  """ a class to plot raw arrays contained within a Meq tree """

  _icon = pixmaps.bars3d
  viewer_name = "Array Plotter";
  def is_viewable (data):
    return len(data) > 0;
  is_viewable = staticmethod(is_viewable);

  def __init__(self,gw,dataitem,cellspec={},**opts):
    GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);
    _dprint(3,'** array_plotter: starting init')

# now create plotter and colorbar

# first figure out the actual rank of the array we are plotting
    self.actual_rank = 0
    self.array_shape = dataitem.data.shape
    self.array_rank = dataitem.data.rank
    for i in range(len(self.array_shape)):
      if self.array_shape[i] > 1:
        self.actual_rank = self.actual_rank + 1
    self.layout_parent = None
    self.array_selector = None
    self.colorbar = {}
    self.layout_parent = QWidget(self.wparent())
    self.layout = QGridLayout(self.layout_parent)
    self._plotter = QwtImageDisplay('spectra',parent=self.layout_parent)
    if self.actual_rank  > 1:
      self.layout.addWidget(self._plotter, 0, 1)
      if dataitem.data.type() == Complex32 or dataitem.data.type() == Complex64:
        num_colorbars = 2
      else:
        num_colorbars = 1
      for i in range(num_colorbars):
        self.colorbar[i] =  QwtColorBar(colorbar_number=i,parent=self.layout_parent)
        if i == 0:
          self.layout.addWidget(self.colorbar[i], 0, i)
        else:
          self.layout.addWidget(self.colorbar[i], 0, 2)
        self.colorbar[i].setRange(-1,1,colorbar_number=i)
        self.colorbar[i].hide()
        QObject.connect(self._plotter, PYSIGNAL('max_image_range'), self.colorbar[i].setMaxRange) 
        QObject.connect(self._plotter, PYSIGNAL('display_type'), self.colorbar[i].setDisplayType) 
        QObject.connect(self._plotter, PYSIGNAL('set_log_scale'), self.colorbar[i].setLogScale) 
        QObject.connect(self._plotter, PYSIGNAL('show_colorbar_display'), self.colorbar[i].showDisplay)
        QObject.connect(self.colorbar[i], PYSIGNAL('set_image_range'), self._plotter.setImageRange)

      if self.array_rank > 2:
        _dprint(3,' array_plotter: array has rank and shape: ', self.array_rank, ' ', self.array_shape)
        _dprint(3,' array_plotter: so an ND Controller GUI is needed')
        self._plotter.set_toggle_array_rank(self.array_rank)
        self.set_ND_controls()

    else:
      self.layout.addWidget(self._plotter, 0, 0)

    self.plotPrinter = plot_printer(self._plotter, self.colorbar)
    QObject.connect(self._plotter, PYSIGNAL('do_print'), self.plotPrinter.do_print)
    self._plotter.show()
    self.set_widgets(self.layout_parent,dataitem.caption,icon=self.icon());

    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

#  def __del__(self):
#    print "in destructor"
                                                                                           
  def wtop (self):
    if self.layout_parent is None:
      return self._plotter
    else:
      return self.layout_parent

  def set_data (self,dataitem,default_open=None,**opts):
    """ this function is the callback interface to the meqbrowser and
        handles new incoming data """

# pass array to the plotter
    if self.array_rank > 2:
      self.data = dataitem.data
      if self.array_selector is None:
        second_axis = None
        first_axis = None
        for i in range(self.array_rank-1,-1,-1):
          if self.data.shape[i] > 1:
            if second_axis is None:
              second_axis = i
            else:
              if first_axis is None:
                first_axis = i
        if not first_axis is None and not second_axis is None:
          self.array_selector = []
          for i in range(self.array_rank):
            if i == first_axis:
              axis_slice = slice(0,self.data.shape[first_axis])
              self.array_selector.append(axis_slice)
            elif i == second_axis:
              axis_slice = slice(0,self.data.shape[second_axis])
              self.array_selector.append(axis_slice)
            else:
              self.array_selector.append(0)
      self.array_tuple = tuple(self.array_selector)
      self._plotter.array_plot('data', self.data[self.array_tuple])
    else:
      self._plotter.array_plot('data', dataitem.data)

# enable & highlight the cell
    self.enable();
    self.flash_refresh();

# will need more set up parameters eventually
  def set_ND_controls (self):
    """ this function adds the extra GUI control buttons etc if we are
        displaying data for a numarray of dimension 3 or greater """

    labels = None
    parms = None
    self.ND_Controls = ND_Controller(self.array_shape, labels, parms, self.layout_parent) 
    QObject.connect(self.ND_Controls, PYSIGNAL('sliderValueChanged'), self.setArraySelector)
    QObject.connect(self.ND_Controls, PYSIGNAL('defineSelectedAxes'), self.setSelectedAxes)
    QObject.connect(self._plotter, PYSIGNAL('show_ND_Controller'), self.ND_Controls.showDisplay)

    self.layout.addMultiCellWidget(self.ND_Controls,1,1,0,2)

  def setArraySelector (self,lcd_number, slider_value, display_string):
    self.array_selector[lcd_number] = slider_value
    self.array_tuple = tuple(self.array_selector)
    self._plotter.array_plot('data: '+ display_string, self.data[self.array_tuple])

  def setSelectedAxes (self,first_axis, second_axis):
    self._plotter.delete_cross_sections()
    self.array_selector = []
    for i in range(self.array_rank):
      if i == first_axis: 
        axis_slice = slice(0,self.array_shape[first_axis])
        self.array_selector.append(axis_slice)
      elif i == second_axis:
        axis_slice = slice(0,self.array_shape[second_axis])
        self.array_selector.append(axis_slice)
      else:
        self.array_selector.append(0)
    self.array_tuple = tuple(self.array_selector)
    self._plotter.array_plot('data', self.data[self.array_tuple])

# leave use of VTK until later
#   else:
#     self._plotter = vtk_qt_3d_display(self.wparent())
    
Grid.Services.registerViewer(array_class,ArrayPlotter,priority=10)
