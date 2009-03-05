#!/usr/bin/python

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
from Timba.Plugins.plotting_functions import *
import plot_printer

from ResultsRange import *
from BufferSizeDialog import *
import os
import tempfile

from Timba.utils import verbosity
_dbg = verbosity(0,name='svg_plotter');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

# The following class is a python translation and adaption of the
# same C++ class in the picture.cpp program provided in the
# QT Assistant documentation for Qt3

class PictureDisplay(QWidget):
  """ a class for handling data destined for display within 
      a QPicture or QPixmap 
  """

  menu_table = {
    'Save Display in PNG Format': 321,
    }

  def __init__( self, parent=None, name=None):
#   fl = Qt.WType_TopLevel|Qt.WStyle_Customize;
#   fl = Qt.WType_TopLevel
#    fl = Qt.WStyle_Customize;
#    fl |= Qt.WStyle_DialogBorder|Qt.WStyle_Title; 
#   QWidget.__init__(self, parent, name, fl)
    QWidget.__init__(self, parent, name)
  
# set up to use QPicture by default - we need a default for the
# paintEvent method
    self.pict = QPicture()
    self.image_type = "Qicture"
    self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
    
    #add a printer
#   self.printer = QAction(self);
#   self.printer.setIconSet(pixmaps.fileprint.iconset());
#   self.printer.setText("Print plot");
#   QObject.connect(self.printer,SIGNAL("activated()"),self.printplot);

    # create basic menu
    self._menu = QPopupMenu(self);
    QObject.connect(self._menu,SIGNAL("activated(int)"),self.handle_menu_id);

#   self.printer.addTo(self._menu);

# add option to save in PNG format
    toggle_id = self.menu_table['Save Display in PNG Format']
    self._menu.insertItem("Save Display in PNG Format", toggle_id)
    self._menu.setItemVisible(toggle_id, True)

  def mousePressEvent(self, e):
    if Qt.RightButton == e.button():            
      e.accept()
      self._menu.popup(e.globalPos());        
      return              

  def paintEvent(self, QPaintEvent):
    paint = QPainter(self)
    if self.pict:
      if self.image_type == "Qicture":
        paint.drawPicture(self.pict)
        return
      else:
        if self.image_type == "Qpixmap":
          paint.drawPixmap(0,0,self.pict)

  def handle_menu_id(self, menuid):
    if menuid == self.menu_table['Save Display in PNG Format']:
        self._window_title = 'png_grab'
        self.emit(PYSIGNAL("save_display"),(self._window_title,))
        return True

  def printplot(self):
    """ make a hardcopy of current displayed plot """
#   self.emit(PYSIGNAL("do_print"),(True,False))
  # printplot()

  def loadPicture(self,filename):
    print 'loading file ', filename
    try:
      found = False
      if filename.find(".svg") > -1:
        self.pict.load(filename, "svg")
        found = True
      else:
        if filename.find(".png") > -1:
          self.pict = None
          self.pict = QPixmap()
          self.image_type = "Qpixmap" 
          self.pict.load(filename, "png")
          found = True
      if found:
        print '** pict.load(',filename,'): Success! \n'
      else:
        print '** pict.load(',filename,'): Not able to load the picture!\n'
    except:
      print '** pict.load(',filename,'): Not able to load the picture - f*%&ing pylab!\n'

  def resizeEvent(self, ev):
    self.resize(ev.size())

  def sizeHint(self):
    hint = QSize(self.minimumSizeHint())
    return hint;

  def printPlot(self):
        try:
            printer = QPrinter(QPrinter.HighResolution)
        except AttributeError:
            printer = QPrinter()
        printer.setOrientation(QPrinter.Landscape)
        printer.setColorMode(QPrinter.Color)
        printer.setOutputToFile(True)
        printer.setOutputFileName('realvsimag.ps')
        if printer.setup():
            filter = PrintFilter()
            if (QPrinter.GrayScale == printer.colorMode()):
                filter.setOptions(QwtPlotPrintFilter.PrintAll
                                  & ~QwtPlotPrintFilter.PrintCanvasBackground)
            try:
              self.plot.print_(printer, filter)
            except:
              self.plot.printPlot(printer, filter)
    # printPlot()


class SvgPlotter(GriddedPlugin):
  """ a class to visualize data from external svg graphics files """

  _icon = pixmaps.bars3d
  viewer_name = "Svg Plotter";
  def is_viewable (data):
    return len(data) > 0;
  is_viewable = staticmethod(is_viewable);

  def __init__(self,gw,dataitem,cellspec={},**opts):
    GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);
    """ a plugin for showing svg plots """
    self._rec = None;
    self._wtop = None;
    self.dataitem = dataitem
    self.png_number = 0
    self.data_list = []
    self.data_list_labels = []
    self.data_list_length = 0
    self.max_list_length = 50
    self.layout_created = False
    self.counter = -1

    self.reset_plot_stuff()

# back to 'real' work
    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

  def reset_plot_stuff(self):
    """ resets widgets to None. Needed if we have been putting
        out a message about Cache not containing results, etc
    """
    self._svg_plotter = None
    self.plotPrinter = None
    self.results_selector = None
    self.status_label = None
    self.layout_parent = None
    self.layout = None

  def wtop (self):
    """ function needed by Oleg for reasons known only to him! """
    return self._wtop;

  def create_layout_stuff(self):
    """ create grid layouts into which plotter widgets are inserted """
    if self.layout_parent is None or not self.layout_created:
      self.layout_parent = QWidget(self.wparent())
      self.layout = QGridLayout(self.layout_parent)
      self.set_widgets(self.layout_parent,self.dataitem.caption,icon=self.icon())
      self.layout_created = True
    self._wtop = self.layout_parent;       

  def update_status(self, status):
     if not status is None:
       self.status_label.setText(status)

  def grab_display(self, title=None):
    self.png_number = self.png_number + 1
    png_str = str(self.png_number)
    if title is None:
      save_file = './meqbrowser' + png_str + '.png'
    else:
      save_file = title + png_str + '.png'
    save_file_no_space= save_file.replace(' ','_')
    result = QPixmap.grabWidget(self._svg_plotter).save(save_file_no_space, "PNG")
    
  def set_data (self,dataitem,default_open=None,**opts):
    """ this callback receives data from the meqbrowser, when the
        user has requested a plot. It decides whether the data is
        from a VellSet or visu data record, and  after any
        necessary preprocssing forwards the data to one of
        the functions which does the actual plotting """

    _dprint(3, '** in svg_plotter:set_data callback')
    self._rec = dataitem.data;
    _dprint(3, 'set_data: initial self._rec ', self._rec)
# if we are single stepping through requests, Oleg may reset the
# cache, so check for a non-data record situation
    if self._rec is None:
      return
    if isinstance(self._rec, bool):
      return

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
    
# update display with current data
    process_result = self.process_data()

# add this data set to internal list for later replay
    if process_result:
      if self.max_list_length > 0:
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
# are we dealing with an svg result?

    if self._rec.has_key("svg_plot"):
      self.create_layout_stuff()
      self.show_svg_plot()
      process_result = True

# enable & highlight the cell
    self.enable();
    self.flash_refresh();
    _dprint(3, 'exiting process_data')
    return process_result

  def replay_data (self, data_index):
    """ call to redisplay contents of a result record stored in 
        a results history buffer
    """
    if data_index < len(self.data_list):
      self._rec = self.data_list[data_index]
      self.label = self.data_list_labels[data_index]
      self.results_selector.setLabel(self.label)
      process_result = self.process_data()

  def show_svg_plot(self, store_rec=True):
    """ process incoming vells data and attributes into the
        appropriate type of plot """

# if we are single stepping through requests, Oleg may reset the
# cache, so check for a non-data record situation
    if store_rec and isinstance(self._rec, bool):
      return

    svg_plot = self._rec.svg_plot
#   print 'incoming plot string is ', svg_plot
#   print '***************************'
#   print 'handling svg_plot event - string has length ', len(svg_plot)
#   print '***************************'

    fd, file_name = tempfile.mkstemp(text='w',suffix='.svg',dir='/tmp')
    file = os.fdopen(fd,"w")
    try:
      result = file.writelines(svg_plot)
    except:
      try:
        result = file.writelines(svg_plot[1])
      except:
        print 'There is nothing to plot!'
        return
    file.close()

    if not self._svg_plotter is None:
      self._svg_plotter.reparent(QWidget(), 0, QPoint())
      self._svg_plotter = None
    if self._svg_plotter is None:
      self._svg_plotter = PictureDisplay(parent=self.layout_parent)
      self.layout.addWidget(self._svg_plotter, 0, 0)
      self.plotPrinter = plot_printer.plot_printer(self._svg_plotter)
      QObject.connect(self._svg_plotter,PYSIGNAL('do_print'), self.plotPrinter.do_print)
      QObject.connect(self._svg_plotter, PYSIGNAL('save_display'), self.grab_display)
    self._svg_plotter.loadPicture(file_name)
    self._svg_plotter.show()
    
    # finally, get rid of the temporary file
#   if False:       # presently disabled, for testing 
    try:
      os.system("/bin/rm -fr "+ file_name);
    except:   pass

    # end show_svg_plot()

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

    self.show_svg_plot(store_rec=False)

  def adjust_selector (self):
    """ instantiate and/or adjust contents of ResultsRange object """
    if self.results_selector is None:
      self.results_selector = ResultsRange(self.layout_parent)
      self.results_selector.setMaxValue(self.max_list_length)
      self.results_selector.set_offset_index(0)
      self.results_selector.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Minimum)
      self.layout.addWidget(self.results_selector, 1,0,Qt.AlignHCenter)
      self.results_selector.show()
      QObject.connect(self.results_selector, PYSIGNAL('result_index'), self.replay_data)
      QObject.connect(self.results_selector, PYSIGNAL('adjust_results_buffer_size'), self.set_results_buffer)
    self.results_selector.set_emit(False)
    self.results_selector.setRange(self.data_list_length-1)
    self.results_selector.setLabel(self.label)
    self.results_selector.set_emit(True)

#Grid.Services.registerViewer(dmi_type('MeqResult',record),SvgPlotter,priority=10)
Grid.Services.registerViewer(meqds.NodeClass(),SvgPlotter,priority=50)

#############  test stuff from here on #########
def usage( prog ):
  print 'usage : %s <svg_plotter input file>' % prog
  return 1

def main( argv ):
  fileName = ""
  if len(argv) > 1:
    fileName = argv[1]
  if not QFile.exists(fileName):
    print "unable to plot - file not found "
    return
  else:
    app = QApplication(argv)
    plot = PictureDisplay()
    app.setMainWidget(plot)
    plot.loadPicture(fileName)
    plot.setCaption("Qt Example - Picture")
    plot.show()
    app.exec_loop()

# Admire
if __name__ == '__main__':
  """ We need at least one argument: the name of the svg file to plot """
  if len(sys.argv) < 2:
    usage(sys.argv[0])
  else:
    main(sys.argv)

