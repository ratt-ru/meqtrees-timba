#!/usr/bin/env python

# modules that are imported
import sys
import random
import qt
import vtk
from vtk.qt.QVTKRenderWindowInteractor import *
#from vtk.util.vtkImageImportFromArray import *
from vtkImageImportFromNumarray import *
from Timba.dmi import *
from Timba import utils
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI import widgets
from Timba.GUI.browsers import *
from Timba import Grid
import numarray 

rendering_control_instructions = \
'''vtkInteractorStyle implements the "joystick" style of interaction. That is, holding down the mouse keys generates a stream of events that cause continuous actions (e.g., rotate, translate, pan, zoom). (The class vtkInteractorStyleTrackball implements a grab and move style.) The event bindings for this class include the following:<br><br>
Keypress j / Keypress t: toggle between joystick (position sensitive) and trackball (motion sensitive) styles. In joystick style, motion occurs continuously as long as a mouse button is pressed. In trackball style, motion occurs when the mouse button is pressed and the mouse pointer moves.<br><br>
Keypress c / Keypress a: toggle between camera and actor modes. In camera mode, mouse events affect the camera position and focal point. In actor mode, mouse events affect the actor that is under the mouse pointer.<br><br>
Button 1 (Left): rotate the camera around its focal point (if camera mode) or rotate the actor around its origin (if actor mode). The rotation is in the direction defined from the center of the renderer's viewport towards the mouse position. In joystick mode, the magnitude of the rotation is determined by the distance the mouse is from the center of the render window.<br><br>
Button 2 (Middle): pan the camera (if camera mode) or translate the actor (if actor mode). In joystick mode, the direction of pan or translation is from the center of the viewport towards the mouse position. In trackball mode, the direction of motion is the direction the mouse moves. (Note: with 2-button mice, pan is defined as <Shift>-Button 1.)<br><br>
Button 3 (Right): zoom the camera (if camera mode) or scale the actor (if actor mode). Zoom in/increase scale if the mouse position is in the top half of the viewport; zoom out/decrease scale if the mouse position is in the bottom half. In joystick mode, the amount of zoom is controlled by the distance of the mouse pointer from the horizontal centerline of the window.<br><br>
Keypress 3: toggle the render window into and out of stereo mode. By default, red-blue stereo pairs are created. Some systems support Crystal Eyes LCD stereo glasses; you have to invoke SetStereoTypeToCrystalEyes() on the rendering window.<br><br>
Keypress f: fly to the picked point.<br><br>
Keypress p: perform a pick operation. The render window interactor has an internal instance of vtkCellPicker that it uses to pick.<br><br>
Keypress r: reset the camera view along the current view direction. Centers the actors and moves the camera so that all actors are visible.<br><br>
Keypress s: modify the representation of all actors so that they are surfaces. <br><br> 
Keypress u: invoke the user-defined function. Typically, this keypress will bring up an interactor that you can type commands in.<br><br>
Keypress w: modify the representation of all actors so that they are wireframe.'''
#-----------------------------
# Building Qt GUI
#-----------------------------
#-----------------------------
class vtk_qt_3d_display(qt.QWidget):

  def __init__( self, *args ):
    qt.QWidget.__init__(self, *args)
#    self.resize(640,640)
    self.setCaption("VTK 3D Demo")

#-----------------------------
    winlayout = qt.QVBoxLayout(self,20,20,"WinLayout")
#-----------------------------
    winsplitter = qt.QSplitter(self,"WinSplitter")
    winsplitter.setOrientation(qt.QSplitter.Vertical)
    winsplitter.setHandleWidth(10)
#-----------------------------
    self.renwininter = QVTKRenderWindowInteractor(winsplitter)
    qt.QWhatsThis.add(self.renwininter, rendering_control_instructions)
#    self.renwininter.setGeometry(qt.QRect(20,20,600,400))

# next line causes confusion when run inside the browser
#    self.renwininter.AddObserver("ExitEvent", lambda o, e, a=app: a.quit())
    self.renwin = self.renwininter.GetRenderWindow()
    self.inter = self.renwin.GetInteractor()

# create VBox for controls
    self.v_box_controls = qt.QVBox(winsplitter)
# add control buttons
    self.h_box = qt.QHBox(self.v_box_controls)
# buttons
#    self.button_quit = qt.QPushButton("Quit",self.h_box)
    self.button_test = qt.QPushButton("Update",self.h_box)
    self.button_capture = qt.QPushButton("Postscript",self.h_box)
    self.button_x = qt.QPushButton("X Freq",self.h_box)
    self.button_y = qt.QPushButton("Y Time",self.h_box)
    self.button_z = qt.QPushButton("Z Plane",self.h_box)
# lcd
    self.lcd = qt.QLCDNumber(2, self.v_box_controls, "lcd")
    self.lcd.setSegmentStyle(qt.QLCDNumber.Filled)
    self.lcd.setNumDigits(3)
    self.lcd.display(0)
# slider
    self.slider = qt.QSlider(qt.Qt.Horizontal,self.v_box_controls)
    self.slider.setTickmarks(qt.QSlider.Below)
    self.slider.setTickInterval(10)

# create connections from buttons to callbacks
#    qt.QObject.connect(self.button_quit, qt.SIGNAL("clicked()"), qt.qApp, qt.SLOT("quit()"))
    qt.QObject.connect(self.button_test, qt.SIGNAL("clicked()"),self.testEvent)
    qt.QObject.connect(self.button_capture,qt.SIGNAL("clicked()"),self.CaptureImage)
    qt.QObject.connect(self.button_x,qt.SIGNAL("clicked()"),self.AlignXaxis)
    qt.QObject.connect(self.button_y,qt.SIGNAL("clicked()"),self.AlignYaxis)
    qt.QObject.connect(self.button_z,qt.SIGNAL("clicked()"),self.AlignZaxis)

    qt.QObject.connect(self.slider, qt.SIGNAL("valueChanged(int)"), self.lcd, qt.SLOT("display(int)"))
    qt.QObject.connect(self.slider, qt.SIGNAL("valueChanged(int)"), self.SetSlice)

#-----------------------------
    winsplitter.setSizes([400,100])
    winlayout.addWidget(winsplitter)

#-----------------------------

#=============================
# VTK code to create test array
#=============================
    self.image_array = None
    self.iteration = 0
#    self.define_image()

#    self.define_random_image()
#    self.set_initial_display()

  def set_initial_display(self):
    self.extents =  self.image_array.GetDataExtent()
    self.spacing = self.image_array.GetDataSpacing()
    self.origin = self.image_array.GetDataOrigin()

# An outline is shown for context.
    outline = vtk.vtkOutlineFilter()
    outline.SetInput(self.image_array.GetOutput())

    outlineMapper = vtk.vtkPolyDataMapper()
    outlineMapper.SetInput(outline.GetOutput())

    outlineActor = vtk.vtkActor()
    outlineActor.SetMapper(outlineMapper)

# The shared picker enables us to use 3 planes at one time
# and gets the picking order right
    picker = vtk.vtkCellPicker()
    picker.SetTolerance(0.005)

# create blue to red color table
    lut = vtk.vtkLookupTable()
    lut.SetHueRange(0.6667, 0.0)
    lut.Build()

# get locations for initial slices
    xMin, xMax, yMin, yMax, zMin, zMax =  self.extents
    x_index = (xMax-xMin) / 2
    y_index = (yMax-yMin) / 2
    z_index = (zMax-zMin) / 2

# The 3 image plane widgets are used to probe the dataset.
    self.planeWidgetX = vtk.vtkImagePlaneWidget()
    self.planeWidgetX.DisplayTextOn()
    self.planeWidgetX.SetInput(self.image_array.GetOutput())
    self.planeWidgetX.SetPlaneOrientationToXAxes()
    self.planeWidgetX.SetSliceIndex(x_index)
    self.planeWidgetX.SetPicker(picker)
    self.planeWidgetX.SetKeyPressActivationValue("x")
    prop1 = self.planeWidgetX.GetPlaneProperty()
#    prop1.SetColor(1, 0, 0)
    self.planeWidgetX.SetLookupTable(lut)
    self.planeWidgetX.TextureInterpolateOff()
    self.planeWidgetX.SetResliceInterpolate(0)

    self.planeWidgetY = vtk.vtkImagePlaneWidget()
    self.planeWidgetY.DisplayTextOn()
    self.planeWidgetY.SetInput(self.image_array.GetOutput())
    self.planeWidgetY.SetPlaneOrientationToYAxes()
    self.planeWidgetY.SetSliceIndex(y_index)
    self.planeWidgetY.SetPicker(picker)
    self.planeWidgetY.SetKeyPressActivationValue("y")
    prop2 = self.planeWidgetY.GetPlaneProperty()
#    prop2.SetColor(1, 1, 0)
    self.planeWidgetY.SetLookupTable(self.planeWidgetX.GetLookupTable())
    self.planeWidgetY.TextureInterpolateOff()
    self.planeWidgetY.SetResliceInterpolate(0)

# for the z-slice, turn off texture interpolation:
# interpolation is now nearest neighbour, to demonstrate
# cross-hair cursor snapping to pixel centers
    self.planeWidgetZ = vtk.vtkImagePlaneWidget()
    self.planeWidgetZ.DisplayTextOn()
    self.planeWidgetZ.SetInput(self.image_array.GetOutput())
    self.planeWidgetZ.SetPlaneOrientationToZAxes()
    self.planeWidgetZ.SetSliceIndex(z_index)
    self.planeWidgetZ.SetPicker(picker)
    self.planeWidgetZ.SetKeyPressActivationValue("z")
    prop3 = self.planeWidgetZ.GetPlaneProperty()
#   prop3.SetColor(0, 0, 1)
    self.planeWidgetZ.SetLookupTable(self.planeWidgetX.GetLookupTable())
    self.planeWidgetZ.TextureInterpolateOff()
    self.planeWidgetZ.SetResliceInterpolate(0)

# Create the RenderWindow and Renderer
    self.ren = vtk.vtkRenderer()
    self.renwin.AddRenderer(self.ren)
    
# Add the outline actor to the renderer, set the background color and size
    self.ren.AddActor(outlineActor)
    self.ren.SetBackground(0.1, 0.1, 0.2)
#    self.renwin.SetSize(600, 600)

    self.current_widget = self.planeWidgetZ
    self.mode_widget = self.planeWidgetZ
    self.slider.setRange(zMin,zMax)
    self.slider.setValue(z_index)

# Create a text property for cube axes
    tprop = vtk.vtkTextProperty()
    tprop.SetColor(1, 1, 1)
    tprop.ShadowOn()

# Create a vtkCubeAxesActor2D.  Use the outer edges of the bounding box to
# draw the axes.  Add the actor to the renderer.
    axes = vtk.vtkCubeAxesActor2D()
    axes.SetInput(self.image_array.GetOutput())
    axes.SetCamera(self.ren.GetActiveCamera())
    axes.SetLabelFormat("%6.4g")
    axes.SetFlyModeToOuterEdges()
    axes.SetFontFactor(0.8)
    axes.SetAxisTitleTextProperty(tprop)
    axes.SetAxisLabelTextProperty(tprop)
    axes.SetXLabel("X Freq")
    axes.SetYLabel("Y Time")
    axes.SetZLabel("Z Plane")
    self.ren.AddProp(axes)

# Set the interactor for the widgets
    self.planeWidgetX.SetInteractor(self.inter)
    self.planeWidgetX.On()
    self.planeWidgetY.SetInteractor(self.inter)
    self.planeWidgetY.On()
    self.planeWidgetZ.SetInteractor(self.inter)
    self.planeWidgetZ.On()

# Create an initial interesting view
    cam1 = self.ren.GetActiveCamera()
    cam1.Elevation(110)
#    cam1.SetViewUp(0, 0, -1)
    cam1.SetViewUp(0, 0, 1)
    cam1.Azimuth(45)
    self.ren.ResetCameraClippingRange()

# Align the camera so that it faces the desired widget
  def AlignCamera(self, slice_number):
    xMin, xMax, yMin, yMax, zMin, zMax = self.extents
    ox, oy, oz = self.origin
    sx, sy, sz = self.spacing
    cx = ox+(0.5*(xMax-xMin))*sx
    cy = oy+(0.5*(yMax-yMin))*sy
    cz = oz+(0.5*(zMax-zMin))*sz
    vx, vy, vz = 0, 0, 0
    nx, ny, nz = 0, 0, 0
    iaxis = self.current_widget.GetPlaneOrientation()
    if iaxis == 0:
        vz = -1
        nx = ox + xMax*sx
        cx = ox + slice_number*sx
    elif iaxis == 1:
        vz = -1
        ny = oy+yMax*sy
        cy = oy+slice_number*sy
    else:
        vy = 1
        nz = oz+zMax*sz
        cz = oz+slice_number*sz
 
    px = cx+nx*2
    py = cy+ny*2
    pz = cz+nz*3

    camera = self.ren.GetActiveCamera()
    camera.SetFocalPoint(cx, cy, cz)
    camera.SetPosition(px, py, pz)
    camera.ComputeViewPlaneNormal()
    camera.SetViewUp(vx, vy, vz)
    camera.OrthogonalizeViewUp()
#    self.ren.ResetCameraClippingRange()
    self.ren.ResetCamera()
    self.renwin.Render()
 
# Capture the display to a Postscript file
  def CaptureImage(self):
    if not self.image_array is None:
      w2i = vtk.vtkWindowToImageFilter()
      writer = vtk.vtkPostScriptWriter()
      w2i.SetInput(self.renwin)
      w2i.Update()
      writer.SetInput(w2i.GetOutput())
      writer.SetFileName("image.ps")
      self.renwin.Render()
      writer.Write()

# Align the widget back into orthonormal position,
# set the slider to reflect the widget's position,
# call AlignCamera to set the camera facing the widget
  def AlignXaxis(self):
    xMin, xMax, yMin, yMax, zMin, zMax =  self.extents
    slice_number = None
    po = self.planeWidgetX.GetPlaneOrientation()
    if po == 3:
        self.planeWidgetX.SetPlaneOrientationToXAxes()
        slice_number = (xMax-xMin)/2
        self.planeWidgetX.SetSliceIndex(slice_number)
    else:
        slice_number = self.planeWidgetX.GetSliceIndex()
 
    self.current_widget = self.planeWidgetX
    self.slider.setRange(xMin,xMax)
    self.slider.setValue(slice_number)
    self.AlignCamera(slice_number)

  def AlignYaxis(self):
    xMin, xMax, yMin, yMax, zMin, zMax =  self.extents
    slice_number = None
    po = self.planeWidgetY.GetPlaneOrientation()
    if po == 3:
        self.planeWidgetY.SetPlaneOrientationToYAxes()
        slice_number = (yMax-yMin)/2
        self.planeWidgetY.SetSliceIndex(slice_number)
    else:
        slice_number = self.planeWidgetY.GetSliceIndex()
 
    self.current_widget = self.planeWidgetY
    self.slider.setRange(yMin,yMax)
    self.slider.setValue(slice_number)
    self.AlignCamera(slice_number)
 
  def AlignZaxis(self):
    xMin, xMax, yMin, yMax, zMin, zMax =  self.extents
    slice_number = None
    po = self.planeWidgetZ.GetPlaneOrientation()
    if po == 3:
        self.planeWidgetZ.SetPlaneOrientationToZAxes()
        slice_number = (zMax-zMin)/2
        self.planeWidgetZ.SetSliceIndex(slice_number)
    else:
        slice_number = self.planeWidgetZ.GetSliceIndex()
 
    self.current_widget = self.planeWidgetZ
    self.slider.setRange(zMin,zMax)
    self.slider.setValue(slice_number)
    self.AlignCamera(slice_number)

  def SetSlice(self, sl):
    self.current_widget.SetSliceIndex(sl)
    self.ren.ResetCameraClippingRange()
    self.renwin.Render()

#=============================
# VTK code for test array
#=============================
  def define_image(self, iteration=1):
    num_arrays = 92
    num_arrays = 800
    num_arrays = 2
    num_arrays = 300
    array_dim = 64
    gain = 1.0 / num_arrays
    if self.image_array is None:
      self.image_numarray = numarray.ones((num_arrays,array_dim,array_dim),type=numarray.Float32)
      for k in range(num_arrays):
        for i in range(array_dim):
          for j in range(array_dim):
            self.image_numarray[k,i,j] = iteration * k * gain

#note: for vtkImageImportFromNumarray to work, incoming array
#      must have rank 3
      self.image_array = vtkImageImportFromNumarray()
      self.image_array.SetArray(self.image_numarray)
      spacing = (3.2, 3.2, 1.5)
      self.image_array.SetDataSpacing(spacing)
      self.set_initial_display()
    else:
      for k in range(num_arrays):
        for i in range(array_dim):
          for j in range(array_dim):
            self.image_numarray[k,i,j] = iteration * k * gain
      self.image_array.SetArray(self.image_numarray)
# refresh display if data contents updated after
# first display
      self.renwin.Render()

#=============================
# VTK code for test array
#=============================
  def define_random_image(self):
    num_arrays = 93
    array_dim = 64
    image_numarray = numarray.ones((num_arrays,array_dim,array_dim),type=numarray.Float32)
    for k in range(num_arrays):
      for i in range(array_dim):
        for j in range(array_dim):
          image_numarray[k,i,j] = random.random()

    if self.image_array is None:
      self.iteration = 0
      self.image_array = vtkImageImportFromNumarray()
      self.image_array.SetArray(image_numarray)
      spacing = (3.2, 3.2, 1.5)
      self.image_array.SetDataSpacing(spacing)
      self.set_initial_display()
    else:
      self.image_array.SetArray(image_numarray)
# refresh display if data contents updated after
# first display
      self.renwin.Render()

  def array_plot(self, caption, plot_array):
    if self.image_array is None:
      self.image_array = vtkImageImportFromNumarray()
      if plot_array.rank > 3:
        self.image_array.SetArray(plot_array[0])
      else:
        self.image_array.SetArray(plot_array)
      spacing = (3.2, 3.2, 1.5)
      self.image_array.SetDataSpacing(spacing)
      self.set_initial_display()
    else:
      if plot_array.rank > 3:
        self.image_array.SetArray(plot_array[0])
      else:
        self.image_array.SetArray(plot_array)
# refresh display if data contents updated after
# first display
      self.renwin.Render()

  def start_timer(self, time):
    timer = qt.QTimer()
    timer.connect(timer, qt.SIGNAL('timeout()'), self.timerEvent)
    timer.start(time)

  def testEvent(self):
    self.iteration = self.iteration + 1
    self.define_image(self.iteration)
#    self.define_random_image()

  def AddVTKExitEvent(self):
# next line causes confusion when run inside the browser
    self.renwininter.AddObserver("ExitEvent", lambda o, e, a=app: a.quit())

class ThreeDPlotter(GriddedPlugin):
  """ a class to plot very simple histograms of array data distributions """

  _icon = pixmaps.bars3d
  viewer_name = "3D Plotter";
  def is_viewable (data):
    return len(data) > 0;
  is_viewable = staticmethod(is_viewable);

  def __init__(self,gw,dataitem,cellspec={},**opts):
    GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);

# create the plotter
    self._plotter = vtk_qt_3d_display(self.wparent())
    self._plotter.show()
    self.set_widgets(self._plotter,dataitem.caption,icon=self.icon());

    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);

#  def __del__(self):
#    print "in destructor"
                                                                                           
  def wtop (self):
    return self._plotter

  def set_data (self,dataitem,default_open=None,**opts):
    """ this function is the callback interface to the meqbrowser and
        handles new incoming data for the histogram """

# enable & highlight the cell
    self.enable();
    self.flash_refresh();
    
Grid.Services.registerViewer(array_class,ThreeDPlotter,priority=15)

#=============================
if __name__ == "__main__":
  app = qt.QApplication(sys.argv)
  qt.QObject.connect(app,qt.SIGNAL("lastWindowClosed()"),
		app,qt.SLOT("quit()"))
  display = vtk_qt_3d_display()
  display.AddVTKExitEvent()
  display.show()
  app.exec_loop()

