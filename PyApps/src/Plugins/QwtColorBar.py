#!/usr/bin/env python

# an adaption of the PyQwt-4.2 QwtImagePlotDemo.py example so that
# we can draw color bars


#% $Id$ 

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

from Timba.GUI.pixmaps import pixmaps
from QwtPlotImage import *
from math import log
from math import exp

from Timba.utils import verbosity
_dbg = verbosity(0,name='QwtColorBar');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;


colorbar_instructions = \
'''The colorbar displays the current range of intensities in the corresponding image display. You can interact with the colorbar to change the range of intensities displayed in the image.<br><br>
Button 1 (Left): If you click the <b>left</b> mouse button on a location inside the colorbar and then drag it, a rectangular square will be seen. When you release the left mouse button, the range of intensity defined in the vertical (Y) direction will now specify the maximum range of intensity that will be shown in the image display. Image pixels with values greater or less than the selected range will be plotted with the maximum or minimum allowed values. The color rainbow or grayscale will always cover the specified range of pixels, so you can obtain increased detail by zooming in on an intensity range.<br><br>
Button 2 (Right):Clicking the <b>right</b> mouse button in the colorbar window will cause a context menu with to appear. If you have already zoomed into the colorbar using the method described above, one of the options to appear will be 'unzoom intensity range '. If you click on this menu item, then the colorbar scale (and the image scale) is reset to the intrinsic range associated with the current image. The other option allows you to lock or unlock the colorbar. If you lock the colorbar, then the scale will be fixed; even if you load a new image, the scale will not change. Nor will you be able to reset the intensity scale to the default, if you had previously zoomed in. To enable the colorbar to change the intensity range, you must then unlock the colorbar.'''

class QwtColorBar(QwtPlot):
    menu_table = {
        'unzoom intensity range': 200,
        'lock colorbar scale': 201,
        'unlock colorbar scale': 202,
        }

    def __init__(self, colorbar_number=0, parent=None):
        QwtPlot.__init__(self, parent)
        self._mainwin = parent and parent.topLevelWidget()
        self.colorbar_number = colorbar_number
        # create copy of standard application font..
        font = QFont(QApplication.font());
        fi = QFontInfo(font);
        # and scale it down to 70%
        font.setPointSize(fi.pointSize()*0.7);
        # apply font to QwtPlot
        self.setTitleFont(font);
        for axis in range(0,4):
          self.setAxisFont(axis,font);
          self.setAxisTitleFont(axis,font);

	# make a QwtPlot widget
        self.plotLayout().setMargin(0)
        self.plotLayout().setCanvasMargin(0)
        self.plotLayout().setAlignCanvasToScales(1)
	# set axis parameters
        self.enableAxis(QwtPlot.yLeft)
        self.enableAxis(QwtPlot.xBottom, False)
        self.enableGridX(False)
        self.enableGridY(False)
        self.setAxisLabelRotation(QwtPlot.yLeft,270)
        self.setAxisLabelAlignment(QwtPlot.yLeft, Qt.AlignTop)
        # default color bar
        self.plotImage = QwtPlotImage(self)
        self.min = 0.0
        self.max = 256.0
        self.is_active = False
        self.log_scale = False
        self.ampl_phase = False
        self.bar_array = reshape(arange(self.max), (1,256))
        self.y_scale = (self.min, self.max)
        self.plotImage.setData(self.bar_array, None, self.y_scale)

# Over-ride default QWT Plot size policy of MinimumExpanding
# Otherwise minimum size of plots is too large when embedded in a
# QGridlayout
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

        # width limits - the following seem reasonable
        # we don't want the bar to resize itself freely - it becomes too big!
        self.setMaximumWidth(self.sizeHint().width() * 1.5)

        self.zoomStack = []
        self.connect(self,
                     SIGNAL('plotMouseMoved(const QMouseEvent&)'),
                     self.onMouseMoved)
        self.connect(self,
                     SIGNAL('plotMousePressed(const QMouseEvent&)'),
                     self.onMousePressed)
        self.connect(self,
                     SIGNAL('plotMouseReleased(const QMouseEvent&)'),
                     self.onMouseReleased)

        # add intructions on how to use
        QWhatsThis.add(self, colorbar_instructions)

        # create pull_down menu and add menu components
        if self._mainwin:
          self._menu = QPopupMenu(self._mainwin);
        else:
          self._menu = QPopupMenu(None);

        toggle_id = self.menu_table['unzoom intensity range']
        self._menu.insertItem("unzoom intensity range", toggle_id)
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = self.menu_table['lock colorbar scale']
        self._menu.insertItem(pixmaps.close_lock.iconset(),'lock colorbar scale ', toggle_id)
        toggle_id = self.menu_table['unlock colorbar scale']
        self._menu.insertItem(pixmaps.open_lock.iconset(),'unlock colorbar scale ', toggle_id)
        self._menu.setItemVisible(toggle_id, False)
        QObject.connect(self._menu,SIGNAL("activated(int)"), self.handle_basic_menu_id)
        self._lock_bar = False
        
# for drag & drop stuff ...
        self.setAcceptDrops(True)
        self.yhb = 0
        self.ylb = 0
        self.xhb = 0
        self.xlb = 0

        # replot
        self.replot()
    # __init__()

    def get_data_range(self):
      """ returns range of this widget when called by 'foreign'
          widget on which we have done a drop event
      """ 
      rng = (self.min, self.max, self.colorbar_number, self.ampl_phase)
      return rng

    def dragEnterEvent(self, event):
      """ drag & drop event callback entered when we move out of or
          in to a widget 
      """ 
      try:
        event.accept(QTextDrag.canDecode(event))
      except:
        pass

    def dropEvent(self, event):
      """ callback that handles a drop event from frag & drop """
      try:
        command= QString()
        if QTextDrag.decode(event, command): # fills 'command' with decoded text
          if str(command) == "copyColorRange":
            if event.source() != self:
              rng = event.source().get_data_range();
              if self.colorbar_number == rng[2] and not self._lock_bar:
                self.zoomStack == []
                self.zoomState = (
                  self.axisScale(QwtPlot.yLeft).lBound(),
                  self.axisScale(QwtPlot.yLeft).hBound(),
                  )
                self.zoomStack.append(self.zoomState)
                toggle_id = self.menu_table['unzoom intensity range']
                self._menu.setItemVisible(toggle_id, True)
                self.setRange(rng[0], rng[1], rng[2],rng[3])
#           else:
#             print 'dropping into same widget'
#       else:
#         print 'decode failure'
      except:
        pass

    def startDrag(self):
      """ operations done when we start a drag event """ 
      d = QTextDrag('copyColorRange', self)
      d.dragCopy()

    def setRange(self, min, max,colorbar_number=0, ampl_phase=False):
      """ sets display range for this colorbar and emits signal
          to associated display to set corresponding range 
      """ 
      if ampl_phase != self.ampl_phase:
        return

      if colorbar_number == self.colorbar_number:
        if min > max:
          temp = max
          max = min
          min = temp
#       if abs(max - min) < 0.00005:
        if abs(max - min) < 2.0e-8:
          if max == 0.0 or min == 0.0:
            min = -0.1
            max = 0.1
          else:
            min = 0.9 * min
            max = 1.1 * max
        self.min = min * 1.0
        self.max = max * 1.0

        # send event to display_image.py that range has changed
        self.emit_range()

        if self.log_scale:
          max = log(self.max)
          min = log(self.min)
          delta = (max - min) / 255.0
          for i in range (256):
            self.bar_array[0,i] = exp (min + i * delta)
        else:
          delta = (self.max - self.min) / 255.0
          for i in range (256):
            self.bar_array[0,i] = self.min + i * delta
        self.y_scale = (self.min, self.max)
        self.plotImage.setData(self.bar_array, None, self.y_scale)
        self.show()
        self.replot()
    # set Range()

    def getTransformOffset(self):
      """ get the offset value for a plot with a log scale """
      return self.plotImage.getTransformOffset()
 
    def setScales(self):
      self.plotImage.setLogScale(self.log_scale)
      self.plotImage.setLogYScale(self.log_scale)
      if self.log_scale:
        self.setAxisOptions(QwtPlot.yLeft, QwtAutoScale.Floating | QwtAutoScale.Logarithmic)
      else:
        self.setAxisOptions(QwtPlot.yLeft, QwtAutoScale.None)

    def setMaxRange(self, limits, colorbar_number=0, log_scale=False, ampl_phase=False):
      """ sets maximum range parameters for this colorbar """
      if colorbar_number == self.colorbar_number:
        self.ampl_phase = ampl_phase
        
        if self.ampl_phase is None:
          self.ampl_phase = False
        self.log_scale = log_scale
        self.setScales()
        min = limits[0]
        max = limits[1]
        if min > max:
            temp = max
            max = min
            min = temp
#       if abs(max - min) < 0.00005:
        if abs(max - min) < 2.0e-8:
          if max == 0.0 or min == 0.0:
            min = -0.1
            max = 0.1
          else:
            min = 0.9 * min
            max = 1.1 * max
        if not self._lock_bar:
          self.image_min = min * 1.0
          self.image_max = max * 1.0
          self.min = self.image_min
          self.max = self.image_max
        if self.log_scale:
          if self.min <= 0.0:
            offset = -1.0 * self.min + 0.001
            self.min = self.min + offset
            self.max = self.max + offset
            self.image_min = self.min
            self.image_max = self.max
          max = log(self.max)
          min = log(self.min)
          delta = (max - min) / 255.0
          for i in range (256):
            self.bar_array[0,i] = exp (min + i * delta)
          _dprint(3, 'log bar array is ',self.bar_array)
        else:
          delta = (self.max - self.min) / 255.0
          for i in range (256):
            self.bar_array[0,i] = self.min + i * delta
        if not self._lock_bar:
          self.y_scale = (self.min, self.max)
          self.plotImage.setData(self.bar_array, None, self.y_scale)
          self.show()
          self.replot()
    # setMaxRange()

    def showDisplay(self, show_self, colorbar_number=0):
      """ callback to show or hide this colorbar """
      if colorbar_number == self.colorbar_number:
        self.is_active = True
        if show_self > 0:
          self.show()
        else:
          self.hide()
        self.replot()
    # showDisplay

    def unHide(self):
      """ callback to show this colorbar """
      if self.is_active:
        self.show()

    def handle_basic_menu_id(self, menuid):
      """ callback to handle most common basic context menu selections """
      if menuid < 0:
# should not be any such menuid that we need to handle here
        return True
      if menuid == self.menu_table['unzoom intensity range']:
        self.unzoom()
        return 
      if menuid == self.menu_table['lock colorbar scale']:
        self._menu.setItemVisible(menuid, False)
        toggle_id = self.menu_table['unlock colorbar scale']
        self._menu.setItemVisible(toggle_id, True)
        if len(self.zoomStack):
          toggle_id = self.menu_table['unzoom intensity range']
          self._menu.setItemVisible(toggle_id, False)
        self._lock_bar = True
        self.emit_range()
        return 
      if menuid == self.menu_table['unlock colorbar scale']:
        self._menu.setItemVisible(menuid, False)
        toggle_id = self.menu_table['lock colorbar scale']
        self._menu.setItemVisible(toggle_id, True)
        if len(self.zoomStack):
          toggle_id = self.menu_table['unzoom intensity range']
          self._menu.setItemVisible(toggle_id, True)
        self._lock_bar = False
        self.emit_range()
        return 

    def emit_range(self):
      self.emit(PYSIGNAL("set_image_range"),(self.min, self.max, self.colorbar_number,self._lock_bar))

    def setBarLock(self, set_lock=False):
      self._lock_bar = set_lock  
      if self._lock_bar:
        toggle_id = self.menu_table['lock colorbar scale']
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = self.menu_table['unlock colorbar scale']
        self._menu.setItemVisible(toggle_id, True)
      else:
        toggle_id == self.menu_table['unlock colorbar scale']
        self._menu.setItemVisible(toggle_id, False)
        toggle_id = self.menu_table['lock colorbar scale']
        self._menu.setItemVisible(toggle_id, True)
      self.emit_range()

    def unzoom(self):
      """ callback to set range of this colorbar back to default """
      if len(self.zoomStack):
        while len(self.zoomStack):
          ymin, ymax = self.zoomStack.pop()

        toggle_id = self.menu_table['unzoom intensity range']
        self._menu.setItemVisible(toggle_id, False)

      self.setAxisScale(QwtPlot.yLeft, self.image_min, self.image_max)
      if self.image_min > self.image_max:
        temp = self.image_max
        self.image_max = self.image_min
        self.image_min = temp
      self.setRange(self.image_min, self.image_max, self.colorbar_number,self.ampl_phase)

    # set the type of colorbar display, can be one of "hippo", "grayscale" 
    # or "brentjens"
    def setDisplayType(self,display_type):
        self.plotImage.setDisplayType(display_type)
        self.plotImage.setData(self.bar_array, None, self.y_scale)
        self.replot()
    # setDisplayType()


    def drawCanvasItems(self, painter, rectangle, maps, filter):
        self.plotImage.drawImage(
            painter, maps[QwtPlot.xBottom], maps[QwtPlot.yLeft])
        QwtPlot.drawCanvasItems(self, painter, rectangle, maps, filter)
    # drawCanvasItems()

    def onMouseMoved(self, e):
      """ callback to handle mouse moved event """
      xPos = e.pos().x()
      yPos = e.pos().y()
      # Test if mouse has moved outside the plot. If yes, we're 
      # starting a drag.
      if xPos < self.xlb-10 or xPos > self.xhb+10 or yPos > self.ylb+10 or yPos < self.yhb-10:
        self.enableOutline(0)
        self.startDrag()
    # onMouseMoved()

    def onMousePressed(self, e):
      """ callback to handle mouse pressed event """
      if Qt.LeftButton == e.button():
        # get bounds of plot. Keep them around for later test if
        # we're initiating a drag operation
        self.yhb = self.transform(QwtPlot.yLeft, self.axisScale(QwtPlot.yLeft).hBound())
        self.ylb = self.transform(QwtPlot.yLeft, self.axisScale(QwtPlot.yLeft).lBound())
        self.xhb = self.transform(QwtPlot.xBottom, self.axisScale(QwtPlot.xBottom).hBound())
        self.xlb = self.transform(QwtPlot.xBottom, self.axisScale(QwtPlot.xBottom).lBound())
        # Python semantics: self.pos = e.pos() does not work; force a copy
        _dprint(3, 'e.pos() ', e.pos())
        self.xpos = e.pos().x()
        self.ypos = e.pos().y()
        _dprint(3, 'self.xpos self.ypos ', self.xpos, ' ', self.ypos)
        if not self._lock_bar:
          self.enableOutline(1)
          self.setOutlinePen(QPen(Qt.black))
          self.setOutlineStyle(Qwt.Rect)
          self.zooming = 1
          if self.zoomStack == []:
            self.zoomState = (
              self.axisScale(QwtPlot.yLeft).lBound(),
              self.axisScale(QwtPlot.yLeft).hBound(),
              )
          # fake a mouse move to show the cursor position
          self.onMouseMoved(e)
      elif Qt.RightButton == e.button():
        e.accept()
        self._menu.popup(e.globalPos())
    # onMousePressed()

    def onMouseReleased(self, e):
      """ handles mouse release event if we're not doing a drop """

      # if color bar is locked, do nothing
      if self._lock_bar:
        return

      if Qt.LeftButton == e.button():
        xmin = min(self.xpos, e.pos().x())
        xmax = max(self.xpos, e.pos().x())
        ymin = min(self.ypos, e.pos().y())
        ymax = max(self.ypos, e.pos().y())
        self.setOutlineStyle(Qwt.Cross)
        xmin = self.invTransform(QwtPlot.xBottom, xmin)
        xmax = self.invTransform(QwtPlot.xBottom, xmax)
        ymin = self.invTransform(QwtPlot.yLeft, ymin)
        ymax = self.invTransform(QwtPlot.yLeft, ymax)
        if xmin == xmax or ymin == ymax:
          return
        self.zoomStack.append(self.zoomState)
        self.zoomState = (ymin, ymax)
        self.enableOutline(0)
        if len(self.zoomStack):
          toggle_id = self.menu_table['unzoom intensity range']
          self._menu.setItemVisible(toggle_id, True)
      elif Qt.RightButton == e.button():
        if len(self.zoomStack):
          ymin, ymax = self.zoomStack.pop()
        else:
          return

      self.setAxisScale(QwtPlot.yLeft, ymin, ymax)
      if ymin > ymax:
        temp = ymax
        ymax = ymin
        ymin = temp
      self.setRange(ymin, ymax, self.colorbar_number, self.ampl_phase)

      self.replot()
    # onMouseReleased()

# class QwtColorBar

# the following tests the QwtColorBar class
def make():
    demo = QwtColorBar()
#   demo.setMaxRange((1.0e-11, 0.001),0,True)
    demo.setMaxRange((1.0e-11, 1.0),0)

    demo.resize(50, 200)
    demo.show()
    return demo

# make()

def main(args):
    app = QApplication(args)
    demo = make()
    app.setMainWidget(demo)
    app.exec_loop()

# main()

# Admire
if __name__ == '__main__':
    main(sys.argv)




