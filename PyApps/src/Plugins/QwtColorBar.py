#!/usr/bin/env python

# an adaption of the PyQwt-4.2 QwtImagePlotDemo.py example so that
# we can draw color bars

from Timba.GUI.pixmaps import pixmaps
from QwtPlotImage import *

colorbar_instructions = \
'''The colorbar displays the current range of intensities in the corresponding image display. You can interact with the colorbar to change the range of intensities displayed in the image.<br><br>
Button 1 (Left): If you click the <b>left</b> mouse button on a location inside the colorbar and then drag it, a rectangular square will be seen. When you release the left mouse button, the range of intensity defined in the vertical (Y) direction will now specify the maximum range of intensity that will be shown in the image display. Image pixels with values greater or less than the selected range will be plotted with the maximum or minimum allowed values. The color rainbow or grayscale will always cover the specified range of pixels, so you can obtain increased detail by zooming in on an intensity range.<br><br>
Button 2 (Right):Clicking the <b>right</b> mouse button in the colorbar window will cause a context menu with the option to 'unzoom intensity range' to appear. If you click on this menu item, then the colorbar scale (and the image scale) is reset to the intrinsic range associated with the current image.'''

class QwtColorBar(QwtPlot):

    def __init__(self, colorbar_number=0, plot_key=None, parent=None):
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
        self.image_min = None
        self.image_max = None
        self.bar_array = reshape(arange(self.max), (1,256))
        self.y_scale = arange(2)
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

        # create pull_down menu  - needed to over-ride Oleg's default
        if self._mainwin:
          self._menu = QPopupMenu(self._mainwin);
          zoom = QAction(self);
#         zoom.setIconSet(pixmaps.viewmag.iconset());
          zoom.setText("unzoom intensity range");
          zoom.addTo(self._menu);
          QObject.connect(self._menu,SIGNAL("activated(int)"), self.unzoom)
        
        # replot
        self.replot()
    # __init__()

    def setRange(self, min, max,colorbar_number=0):
      if colorbar_number == self.colorbar_number:
        if min > max:
          temp = max
          max = min
          min = temp
        if abs(max - min) < 0.00005:
          if max == 0.0 or min == 0.0:
            min = -0.1
            max = 0.1
          else:
            min = 0.9 * min
            max = 1.1 * max
        self.min = min * 1.0
        self.max = max * 1.0
        self.emit(PYSIGNAL("set_image_range"),(self.min, self.max, self.colorbar_number))
        self.delta = (self.max - self.min) / 256.0
        for i in range (256):
          self.bar_array[0,i] = self.min + i * self.delta
        self.y_scale = (self.min, self.max)
        self.plotImage.setData(self.bar_array, None, self.y_scale)
        self.show()
        self.replot()
    # set Range()

    def setMaxRange(self, limits, colorbar_number=0):
      if colorbar_number == self.colorbar_number:
        min = limits[0]
        max = limits[1]
        if min > max:
            temp = max
            max = min
            min = temp
        if abs(max - min) < 0.00005:
          if max == 0.0 or min == 0.0:
            min = -0.1
            max = 0.1
          else:
            min = 0.9 * min
            max = 1.1 * max
        self.image_min = min * 1.0
        self.image_max = max * 1.0
        self.min = self.image_min
        self.max = self.image_max
        self.delta = (self.max - self.min) / 256.0
        for i in range (256):
          self.bar_array[0,i] = self.min + i * self.delta
        self.y_scale = (self.min, self.max)
        self.plotImage.setData(self.bar_array, None, self.y_scale)
        self.show()
        self.replot()
    # set Range()

    def showDisplay(self, show_self, colorbar_number=0):
      if colorbar_number == self.colorbar_number:
        if show_self > 0:
          self.show()
        else:
          self.hide()
        self.replot()
    # showDisplay

    def unzoom(self):
        if len(self.zoomStack):
          while len(self.zoomStack):
            xmin, xmax, ymin, ymax = self.zoomStack.pop()
          self.setAxisScale(QwtPlot.xBottom, xmin, xmax)
          self.setAxisScale(QwtPlot.yLeft, self.image_min, self.image_max)
          if self.image_min > self.image_max:
            temp = self.image_max
            self.image_max = self.image_min
            self.image_min = temp
          self.setRange(self.image_min, self.image_max, self.colorbar_number)
#         self.emit(PYSIGNAL("set_image_range"),(self.image_min, self.image_max, self.colorbar_number))
        else:
          return

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
        pass
    # onMouseMoved()

    def onMousePressed(self, e):
        if Qt.LeftButton == e.button():
            # Python semantics: self.pos = e.pos() does not work; force a copy
            self.xpos = e.pos().x()
            self.ypos = e.pos().y()
            self.enableOutline(1)
            self.setOutlinePen(QPen(Qt.black))
            self.setOutlineStyle(Qwt.Rect)
            self.zooming = 1
            if self.zoomStack == []:
                self.zoomState = (
                    self.axisScale(QwtPlot.xBottom).lBound(),
                    self.axisScale(QwtPlot.xBottom).hBound(),
                    self.axisScale(QwtPlot.yLeft).lBound(),
                    self.axisScale(QwtPlot.yLeft).hBound(),
                    )
        elif Qt.RightButton == e.button():
            e.accept()
            self._menu.popup(e.globalPos())
        # fake a mouse move to show the cursor position
        self.onMouseMoved(e)
    # onMousePressed()

    def onMouseReleased(self, e):
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
            self.zoomState = (xmin, xmax, ymin, ymax)
            self.enableOutline(0)
        elif Qt.RightButton == e.button():
            if len(self.zoomStack):
                xmin, xmax, ymin, ymax = self.zoomStack.pop()
            else:
                return

        self.setAxisScale(QwtPlot.xBottom, xmin, xmax)
        self.setAxisScale(QwtPlot.yLeft, ymin, ymax)
        if ymin > ymax:
          temp = ymax
          ymax = ymin
          ymin = temp
        self.setRange(ymin, ymax, self.colorbar_number)
#       self.emit(PYSIGNAL("set_image_range"),(ymin, ymax, self.colorbar_number))

        self.replot()
    # onMouseReleased()

    # what about printing?
    # We may need something here.

# class QwtColorBar

# the following tests the QwtColorBar class
def make():
    demo = QwtColorBar()
    demo.setRange(-512, 512)
    demo.setDisplayType("grayscale")
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




