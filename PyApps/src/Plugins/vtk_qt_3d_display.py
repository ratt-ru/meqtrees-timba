#!/usr/bin/env python

#% $Id$ 

#
# Copyright (C) 2006
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

import sys
import random
import qt

#test if vtk has been installed
global has_vtk
has_vtk = False
try:
  import vtk
  from vtk.qt.QVTKRenderWindowInteractor import *
  from vtkImageImportFromNumarray import *
  #from vtk.util.vtkImageImportFromArray import *
  has_vtk = True
except:
  pass

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

if has_vtk:
  class MEQ_QVTKRenderWindowInteractor(QVTKRenderWindowInteractor):
    """ We override the default QVTKRenderWindowInteractor
        class in order to add an extra method
    """
    def __init__(self, parent=None, name=None, *args, **kw):
      if not has_vtk:
        return None
      QVTKRenderWindowInteractor.__init__(self,parent,name,*args,**kw)

    def contextMenuEvent(self,ev):
      """ This function is necessary when a QVTKRenderWindowInteractor
          is embedded inside the MeqTrees browser. Any higher-level 
          context menu is now ignored when the right mouse
          button is clicked inside the QVTKRenderWindowInteractor.
      """
      ev.accept()

class vtk_qt_3d_display(qt.QWidget):

  def __init__( self, *args ):
    if not has_vtk:
      return None
    qt.QWidget.__init__(self, *args)
#    self.resize(640,640)
#=============================
# VTK code to create test array
#=============================
    self.complex_plot = False
    self.toggle_ND_Controller = 1
    self.button_hide = None
    self.image_array = None
    self.iteration = 0
    self.renwininter = None

    self.setCaption("VTK 3D Demo")

#-----------------------------
    self.winlayout = qt.QVBoxLayout(self,20,20,"WinLayout")
#-----------------------------
    self.winsplitter = qt.QSplitter(self,"WinSplitter")
    self.winsplitter.setOrientation(qt.QSplitter.Vertical)
    self.winsplitter.setHandleWidth(10)
    self.winlayout.addWidget(self.winsplitter)
#-----------------------------

# create VBox for controls
    self.v_box_controls = qt.QVBox(self.winsplitter)
# add control buttons
    self.h_box = qt.QHBox(self.v_box_controls)
# buttons
    self.button_capture = qt.QPushButton("Postscript",self.h_box)
    self.button_x = qt.QPushButton("X",self.h_box)
    self.button_y = qt.QPushButton("Y",self.h_box)
    self.button_z = qt.QPushButton("Z",self.h_box)
    self.button_z.setPaletteBackgroundColor(Qt.green)
# lcd
    self.lcd = qt.QLCDNumber(2, self.v_box_controls, "lcd")
    self.lcd.setSegmentStyle(qt.QLCDNumber.Filled)
    self.lcd.setNumDigits(3)
    self.lcd.display(0)
# slider
    self.h_box1 = qt.QHBox(self.v_box_controls)
    self.slider = qt.QSlider(qt.Qt.Horizontal,self.h_box1)
    self.slider.setTickmarks(qt.QSlider.Below)
    self.slider.setTickInterval(10)
    self.h_box1.setStretchFactor(self.slider,1)

# create connections from buttons to callbacks
    qt.QObject.connect(self.button_capture,qt.SIGNAL("clicked()"),self.CaptureImage)
    qt.QObject.connect(self.button_x,qt.SIGNAL("clicked()"),self.AlignXaxis)
    qt.QObject.connect(self.button_y,qt.SIGNAL("clicked()"),self.AlignYaxis)
    qt.QObject.connect(self.button_z,qt.SIGNAL("clicked()"),self.AlignZaxis)

    qt.QObject.connect(self.slider, qt.SIGNAL("valueChanged(int)"), self.lcd, qt.SLOT("display(int)"))
    qt.QObject.connect(self.slider, qt.SIGNAL("valueChanged(int)"), self.SetSlice)

  def delete_vtk_renderer(self):
    if not self.renwininter is None:
      self.renwininter.reparent(QWidget(), 0, QPoint()) 
    self.renwininter = None
    self.image_array = None

  def hide_vtk_controls(self):
    self.v_box_controls.hide()

  def show_vtk_controls(self):
    self.v_box_controls.show()

  def set_initial_display(self):
    if self.renwininter is None:
      self.renwininter = MEQ_QVTKRenderWindowInteractor(self.winsplitter)
      qt.QWhatsThis.add(self.renwininter, rendering_control_instructions)
      self.renwin = self.renwininter.GetRenderWindow()
      self.inter = self.renwin.GetInteractor()
      self.winsplitter.moveToFirst(self.renwininter)
      self.winsplitter.moveToLast(self.v_box_controls)
      self.winsplitter.setSizes([400,100])
      self.renwininter.show()

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
    self.lut = vtk.vtkLookupTable()
    self.lut.SetHueRange(0.6667, 0.0)
    self.lut.Build()

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
    self.planeWidgetX.SetLookupTable(self.lut)
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

# create scalar bar
    self.scalar_bar = vtk.vtkScalarBarActor()
    self.scalar_bar.SetLookupTable(self.lut)
    self.scalar_bar.SetOrientationToVertical()
    self.scalar_bar.SetWidth(0.1)
    self.scalar_bar.SetHeight(0.8)
    self.scalar_bar.SetTitle("Intensity")
    self.scalar_bar.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
#   self.scalar_bar.GetPositionCoordinate().SetCoordinateSystemToViewport()
    self.scalar_bar.GetPositionCoordinate().SetValue(0.01, 0.1)

# Create the RenderWindow and Renderer
    self.ren = vtk.vtkRenderer()
    self.renwin.AddRenderer(self.ren)
    
# Add the outline actor to the renderer, set the background color and size
    self.ren.AddActor(outlineActor)
    self.ren.SetBackground(0.1, 0.1, 0.2)
#    self.renwin.SetSize(600, 600)
    self.ren.AddActor2D(self.scalar_bar)

    self.current_widget = self.planeWidgetZ
    self.mode_widget = self.planeWidgetZ
    self.slider.setRange(zMin,zMax)
    self.slider.setTickInterval( (zMax-zMin) / 10 )
    self.slider.setValue(z_index)

# Create a text property for cube axes
    tprop = vtk.vtkTextProperty()
    tprop.SetColor(1, 1, 1)
    tprop.ShadowOn()

# Create a vtkCubeAxesActor2D.  Use the outer edges of the bounding box to
# draw the axes.  Add the actor to the renderer.
    self.axes = vtk.vtkCubeAxesActor2D()
    self.axes.SetInput(self.image_array.GetOutput())
    self.axes.SetCamera(self.ren.GetActiveCamera())
    self.axes.SetLabelFormat("%6.4g")
    self.axes.SetFlyModeToOuterEdges()
    self.axes.SetFontFactor(0.8)
    self.axes.SetAxisTitleTextProperty(tprop)
    self.axes.SetAxisLabelTextProperty(tprop)
    self.axes.SetXLabel("X")
    self.axes.SetYLabel("Y")
    self.axes.SetZLabel("Z")
    self.ren.AddProp(self.axes)

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

# Use parallel projection, rather than perspective
    cam1.ParallelProjectionOn()

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
    self.slider.setTickInterval( (xMax-xMin) / 10 )
    self.slider.setValue(slice_number)
    self.AlignCamera(slice_number)
    self.button_x.setPaletteBackgroundColor(Qt.green)
    self.button_y.unsetPalette()
    self.button_z.unsetPalette()

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
    self.slider.setTickInterval( (yMax-yMin) / 10 )
    self.slider.setValue(slice_number)
    self.AlignCamera(slice_number)
    self.button_x.unsetPalette()
    self.button_y.setPaletteBackgroundColor(Qt.green)
    self.button_z.unsetPalette()
 
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
    self.slider.setTickInterval( (zMax-zMin) / 10 )
    self.slider.setValue(slice_number)
    self.AlignCamera(slice_number)
    self.button_x.unsetPalette()
    self.button_y.unsetPalette()
    self.button_z.setPaletteBackgroundColor(Qt.green)

  def SetSlice(self, sl):
    self.current_widget.SetSliceIndex(sl)
    self.ren.ResetCameraClippingRange()
    self.renwin.Render()

#=============================
# VTK code for test array
#=============================
  def define_image(self, iteration=1):
#    num_arrays = 2
#    num_arrays = 92
#    num_arrays = 10
#    array_dim = 700
    num_arrays = 800
    array_dim = 64
    axis_slice = slice(0,array_dim)
    gain = 1.0 / num_arrays
    if self.image_array is None:
      self.image_numarray = numarray.ones((num_arrays,array_dim,array_dim),type=numarray.Float32)
      array_selector = []
      array_selector.append(0)
      array_selector.append(axis_slice)
      array_selector.append(axis_slice)
      for k in range(num_arrays):
        array_tuple = tuple(array_selector)
        self.image_numarray[array_tuple] = iteration * k * gain
        if k < num_arrays:
          array_selector[0] = k + 1
#note: for vtkImageImportFromNumarray to work, incoming array
#      must have rank 3
      self.image_array = vtkImageImportFromNumarray()
      self.image_array.SetArray(self.image_numarray)
      spacing = (3.2, 3.2, 1.5)
      self.image_array.SetDataSpacing(spacing)
      self.set_initial_display()
      self.AddVTKExitEvent()
      self.lut.SetRange(self.image_numarray.min(), self.image_numarray.max())
    else:
      array_selector = []
      array_selector.append(0)
      array_selector.append(axis_slice)
      array_selector.append(axis_slice)
      for k in range(num_arrays):
        array_tuple = tuple(array_selector)
        self.image_numarray[array_tuple] = iteration * k * gain
        if k < num_arrays:
          array_selector[0] = k+1
      self.lut.SetRange(self.image_numarray.min(), self.image_numarray.max())
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

  def array_plot(self, caption, plot_array, dummy_parm=False):

# convert a complex array to reals followed by imaginaries
    if plot_array.type() == numarray.Complex32 or plot_array.type() == numarray.Complex64:
        real_array =  plot_array.getreal()
        imag_array =  plot_array.getimag()
        (nx,ny,nz) = real_array.shape

        image_for_display = array(shape=(nx*2,ny,nz),type=real_array.type());
        image_for_display[:nx,:] = real_array
        image_for_display[nx:,:] = imag_array

        plot_array = image_for_display
        self.complex_plot = True
    else:
        self.complex_plot = False
    if self.image_array is None:
      self.image_array = vtkImageImportFromNumarray()
      if plot_array.rank > 3:
        self.image_array.SetArray(plot_array[0])
      else:
        self.image_array.SetArray(plot_array)

# use default VTK parameters for spacing at the moment
      spacing = (1.0, 1.0, 1.0)
      self.image_array.SetDataSpacing(spacing)
      self.set_initial_display()
      self.lut.SetRange(plot_array.min(), plot_array.max())
      if not self.button_hide is None:
        self.toggle_ND_Controller = 1
        self.button_hide.setText('Hide ND Controller')
      self.button_x.unsetPalette()
      self.button_y.unsetPalette()
      self.button_z.unsetPalette()
      self.button_z.setPaletteBackgroundColor(Qt.green)
    else:
      if plot_array.rank > 3:
        self.image_array.SetArray(plot_array[0])
      else:
        self.image_array.SetArray(plot_array)
      self.lut.SetRange(plot_array.min(), plot_array.max())
# refresh display if data contents updated after
# first display
      self.renwin.Render()
 
  def reset_image_array(self):
    self.image_array = None

  def start_timer(self, time):
    timer = qt.QTimer()
    timer.connect(timer, qt.SIGNAL('timeout()'), self.timerEvent)
    timer.start(time)

  def testEvent(self):
    self.iteration = self.iteration + 1
    self.define_image(self.iteration)
#    self.define_random_image()

  def Add2DButton(self):
    self.button_test = qt.QPushButton("2D Display",self.h_box)
    qt.QObject.connect(self.button_test, qt.SIGNAL("clicked()"),self.two_D_Event)

  def two_D_Event(self):
    self.emit(PYSIGNAL("show_2D_Display"),(0,))

  def AddNDButton(self):
    self.button_hide = qt.QPushButton("Hide ND Controller",self.h_box)
    qt.QObject.connect(self.button_hide, qt.SIGNAL("clicked()"),self.hide_Event)

  def HideNDButton(self):
    if not self.button_hide is None:
      self.button_hide.reparent(QWidget(), 0, QPoint()) 
      self.button_hide = None

  def hide_Event(self):
    if self.toggle_ND_Controller == 1:
      self.toggle_ND_Controller = 0
      if not self.button_hide is None:
        self.button_hide.setText('Show ND Controller')
    else:
      self.toggle_ND_Controller = 1
      if not self.button_hide is None:
        self.button_hide.setText('Hide ND Controller')
    if not self.button_hide is None:
      self.emit(PYSIGNAL("show_ND_Controller"),(self.toggle_ND_Controller,))

  def AddVTKExitEvent(self):
# next line causes confusion when run inside the browser
    self.renwininter.AddObserver("ExitEvent", lambda o, e, a=app: a.quit())

# used in standalone test mode
  def AddUpdateButton(self):
    self.button_test = qt.QPushButton("Update",self.h_box)
    qt.QObject.connect(self.button_test, qt.SIGNAL("clicked()"),self.testEvent)

  def setAxisParms(self, axis_parms):
    if axis_parms[2] is None:
      self.button_x.setText('X')
      if not self.axes is None:
        self.axes.SetXLabel('X')
    else: 
      self.button_x.setText('X ' + axis_parms[2])
      if not self.axes is None:
        self.axes.SetXLabel('X ' + axis_parms[2])
    if axis_parms[1] is None:
      self.button_y.setText('Y')
      if not self.axes is None:
        self.axes.SetYLabel('Y')
    else: 
      self.button_y.setText('Y ' + axis_parms[1])
      if not self.axes is None:
        self.axes.SetYLabel('Y ' + axis_parms[1])
    if axis_parms[0] is None:
      if self.complex_plot:
        Z_text = 'Z (real then imag) '
      else:
        Z_text = 'Z '
      self.button_z.setText(Z_text)
      if not self.axes is None:
        self.axes.SetZLabel(Z_text)
    else: 
      if self.complex_plot:
        Z_text = 'Z (real then imag) '
      else:
        Z_text = 'Z '
      self.button_z.setText(Z_text + axis_parms[0])
      if not self.axes is None:
        self.axes.SetZLabel(Z_text + axis_parms[0])

#=============================
if __name__ == "__main__":
  if has_vtk:
    app = qt.QApplication(sys.argv)
    qt.QObject.connect(app,qt.SIGNAL("lastWindowClosed()"),
		app,qt.SLOT("quit()"))
    display = vtk_qt_3d_display()
    display.AddUpdateButton()
    display.show()
    display.testEvent()
    app.exec_loop()

