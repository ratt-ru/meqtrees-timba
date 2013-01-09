#!/usr/bin/env python
# -*- coding: utf-8 -*-

#% $Id: vtk_qt_3d_display.py 6836 2009-03-05 18:55:17Z twillis $ 

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
#
#  (c) 2013.				 (c) 2011.
#  National Research Council		 Conseil national de recherches
#  Ottawa, Canada, K1A 0R6 		 Ottawa, Canada, K1A 0R6
#
#  This software is free software;	 Ce logiciel est libre, vous
#  you can redistribute it and/or	 pouvez le redistribuer et/ou le
#  modify it under the terms of	         modifier selon les termes de la
#  the GNU General Public License	 Licence Publique Generale GNU
#  as published by the Free		 publiee par la Free Software
#  Software Foundation; either	 	 Foundation (version 3 ou bien
#  version 2 of the License, or	 	 toute autre version ulterieure
#  (at your option) any later	 	 choisie par vous).
#  version.
#
#  This software is distributed in	 Ce logiciel est distribue car
#  the hope that it will be		 potentiellement utile, mais
#  useful, but WITHOUT ANY		 SANS AUCUNE GARANTIE, ni
#  WARRANTY; without even the	 	 explicite ni implicite, y
#  implied warranty of			 compris les garanties de
#  MERCHANTABILITY or FITNESS FOR	 commercialisation ou
#  A PARTICULAR PURPOSE.  See the	 d'adaptation dans un but
#  GNU General Public License for	 specifique. Reportez-vous a la
#  more details.			 Licence Publique Generale GNU
#  					 pour plus de details.
#
#  You should have received a copy	 Vous devez avoir reçu une copie
#  of the GNU General Public		 de la Licence Publique Generale
#  License along with this		 GNU en meme temps que ce
#  software; if not, contact the	 logiciel ; si ce n'est pas le
#  Free Software Foundation, Inc.	 cas, communiquez avec la Free
#  at http://www.fsf.org.		 Software Foundation, Inc. au
#						 http://www.fsf.org.
#
#  email:				 courriel:
#  business@hia-iha.nrc-cnrc.gc.ca	 business@hia-iha.nrc-cnrc.gc.ca
#
#  National Research Council		 Conseil national de recherches
#      Canada				    Canada
#  Herzberg Institute of Astrophysics	 Institut Herzberg d'astrophysique
#  5071 West Saanich Rd.		 5071 West Saanich Rd.
#  Victoria BC V9E 2E7			 Victoria BC V9E 2E7
#  CANADA					 CANADA
#


raise RuntimeError,"MeqTrees VTK support temporarily disabled (29/08/2011). See bug 863."

# modules that are imported



import sys
import random
#import qt
from PyQt4 import Qt as qt
import traceback
import math 

#test if vtk has been installed
global has_vtk
has_vtk = False
try:
  import vtk
  try:
    from vtk.qt4.QVTKRenderWindowInteractor import *
  except:
# depreciated!
    print 'Importation of the local QVTKRenderWindowInteractor_qt4.py file is depreciated.' 
    from QVTKRenderWindowInteractor_qt4 import *
  from Timba.Plugins.vtkImageImportFromNumpy import *
  has_vtk = True
except:
  pass

# traceback.print_exc();

#from Timba.dmi import *
#from Timba import utils
#from Timba.GUI.pixmaps import pixmaps
#from Timba.GUI import widgets
#from Timba.GUI.browsers import *
from Timba.Plugins.ResultsRange_qt4 import *
#from Timba import Grid

import numpy 

rendering_control_instructions = \
'''
You can interact directly with the 3-dimensional VTK display by using your the left, middle and right mouse buttons. <br><br>
Button 1 (Left): Rotates the camera around its focal point. The rotation is in the direction defined from the center of the renderer's viewport towards the mouse position.<br><br>
Button 2 (Middle): Pans the camera. The direction of motion is the direction the mouse moves. (Note: with 2-button mice, pan is defined as 'Shift'-Button 1.)<br><br>
Button 3 (Right): Zooms the camera. Moving the mouse from the top to the bottom of the display causes the camera to appear to move away from the display (zoom out). Moving the mouse from the bottom to the top of the display causes the camera to appear to move toward the display (zoom in).<br><br>
You can control and select the active plane to be moved by means of the spinbox and slider widgets shown beneath the 3-dimensional display. The text to the left of the spinbox tells which axis/plane is active. Moving the slider or clicking the spinbox will cause the active plane to move so that you can see how the data changes as you move through the cube.<br><br>
Since VTK uses the right mouse button to control the camera zoom in the 3-D display, you cannot obtain a context menu directly within the 3-D display. However, by right clicking in the area near the spinbox and slider, you will obtain a context menu. This menu will allow you to change to a new active plane, switch back to the 2-dimensional display or print a copy of the display to a Postscript file.<br><br>
Hardcopy printing is a bit primitive at present; essentially you get a screenshot of the display. So if you want a reasonably sized hardcopy you need to float the display widget from the MeqBrowser and resize it with your mouse to be larger.<br><br>
'''
if has_vtk:

  class MEQ_QVTKRenderWindowInteractor(QVTKRenderWindowInteractor):
    """ We override the default QVTKRenderWindowInteractor
        class in order to add an extra method
    """
    def __init__(self, parent=None,wflags=QtCore.Qt.WindowFlags(),**kw):

      if not has_vtk:
        return None
      QVTKRenderWindowInteractor.__init__(self,parent,wflags,**kw)

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
    self.png_number = 0
    self.renwininter = None
    self.warped_surface = False
    self.scale_factor = 50
    self.data_min = 1000000.0
    self.data_max = -1000000.0
    self.spacing = None
    self.scale_values = (1.0, 1.0, 1.0)

#   self.setCaption("VTK 3D Display")

#-----------------------------
#   self.winlayout = qt.QVBoxLayout(self,20,20,"WinLayout")
    self.winlayout = qt.QVBoxLayout(self)
#-----------------------------
    self.winsplitter = qt.QSplitter(self)
    self.winsplitter.setOrientation(qt.Qt.Vertical)
    self.winsplitter.setHandleWidth(10)
#   self.winsplitter.setOpaqueResize(True)
    self.winlayout.addWidget(self.winsplitter)
#-----------------------------

# create VBox for controls
    self.v_box_controls = qt.QWidget(self.winsplitter)
    self.v_box = qt.QVBoxLayout()
    self.v_box_controls.setLayout(self.v_box)

# spinbox / slider control GUI
#   self.index_selector = ResultsRange(self.v_box_controls)
    self.index_selector = ResultsRange()
    self.v_box.addWidget(self.index_selector)
    self.index_selector.setStringInfo(' selector index ')
    self.index_selector.init3DContextmenu()
    offset_index = 0
    self.index_selector.set_offset_index(offset_index)
# create connections from spinbox / slider control GUI
# context menu to callbacks
    qt.QObject.connect(self.index_selector,Qt.SIGNAL("save_display"),self.grab_display)
    qt.QObject.connect(self.index_selector,Qt.SIGNAL("postscript_requested"),self.CaptureImage)
    qt.QObject.connect(self.index_selector,Qt.SIGNAL("update_requested"),self.testEvent)
    qt.QObject.connect(self.index_selector,Qt.SIGNAL("X_axis_selected"),self.AlignXaxis)
    qt.QObject.connect(self.index_selector,Qt.SIGNAL("Y_axis_selected"),self.AlignYaxis)
    qt.QObject.connect(self.index_selector,Qt.SIGNAL("Z_axis_selected"),self.AlignZaxis)
    qt.QObject.connect(self.index_selector,Qt.SIGNAL("show_ND_Controller"),self.hide_Event)
    qt.QObject.connect(self.index_selector,Qt.SIGNAL('result_index'), self.SetSlice)
    qt.QObject.connect(self.index_selector,Qt.SIGNAL('twoD_display_requested'), self.two_D_Event)
    qt.QObject.connect(self.index_selector,Qt.SIGNAL('align_camera'), self.AlignCamera)
    qt.QObject.connect(self.index_selector,Qt.SIGNAL('update_scale'), self.UpdateScale)

  def delete_vtk_renderer(self):
    if not self.renwininter is None:
      self.renwininter.setParent(Qt.QWidget())
    self.renwininter = None
    self.image_array = None

  def hide_vtk_controls(self):
    self.v_box_controls.hide()

  def show_vtk_controls(self):
    self.v_box_controls.show()

  def set_initial_display(self):
    if self.renwininter is None:
      self.renwininter = MEQ_QVTKRenderWindowInteractor(self.winsplitter)
      self.renwininter.setWhatsThis(rendering_control_instructions)
      self.renwin = self.renwininter.GetRenderWindow()
      self.inter = self.renwin.GetInteractor()
      self.winsplitter.insertWidget(0,self.renwininter)
      self.winsplitter.addWidget(self.v_box_controls)
      self.winsplitter.setSizes([500,100])
      self.renwininter.show()

# Paul Kemper suggested the following:
      camstyle = vtk.vtkInteractorStyleTrackballCamera()
      self.renwininter.SetInteractorStyle(camstyle)


    self.extents =  self.image_array.GetDataExtent()
    self.spacing = self.image_array.GetDataSpacing()
    self.origin = self.image_array.GetDataOrigin()

# An outline is shown for context.
    if self.warped_surface:
      self.index_selector.initWarpContextmenu()
      sx, sy, sz = self.image_array.GetDataSpacing()
      xMin, xMax, yMin, yMax, zMin, zMax = self.image_array.GetDataExtent()
      xMin = sx * xMin
      xMax = sx * xMax
      yMin = sy * yMin
      yMax = sy * yMax
      self.scale_factor = 0.5 * ((xMax-xMin) + (yMax-yMin)) / (self.data_max - self.data_min)
      zMin = self.data_min * self.scale_factor
      zMax = self.data_max * self.scale_factor
      self.outline = vtk.vtkOutlineSource();
      self.outline.SetBounds(xMin, xMax, yMin, yMax, zMin, zMax)
    else:
      self.index_selector.init3DContextmenu()
      self.outline = vtk.vtkOutlineFilter()
      self.outline.SetInput(self.image_array.GetOutput())
    outlineMapper = vtk.vtkPolyDataMapper();
    outlineMapper.SetInput(self.outline.GetOutput() );
    outlineActor = vtk.vtkActor();
    outlineActor.SetMapper(outlineMapper);

# create blue to red color table
    self.lut = vtk.vtkLookupTable()
    self.lut.SetHueRange(0.6667, 0.0)
    self.lut.SetNumberOfColors(256)
    self.lut.Build()

# here is where the 2-D image gets warped
    if self.warped_surface:
      geometry = vtk.vtkImageDataGeometryFilter()
      geometry.SetInput(self.image_array.GetOutput())
      self.warp = vtk.vtkWarpScalar()
      self.warp.SetInput(geometry.GetOutput())
      self.warp.SetScaleFactor(self.scale_factor)
      self.mapper = vtk.vtkPolyDataMapper();
      self.mapper.SetInput(self.warp.GetPolyDataOutput())
      self.mapper.SetScalarRange(self.data_min,self.data_max)
      self.mapper.SetLookupTable(self.lut)
      self.mapper.ImmediateModeRenderingOff()
      warp_actor = vtk.vtkActor()
#     warp_actor.SetScale(2,1,1)
      warp_actor.SetMapper(self.mapper)

      min_range = 0.5 * self.scale_factor
      max_range = 2.0 * self.scale_factor
      self.index_selector.set_emit(False)
      self.index_selector.setMaxValue(max_range,False)
      self.index_selector.setMinValue(min_range)
      self.index_selector.setTickInterval( (max_range - min_range) / 10 )
      self.index_selector.setRange(max_range, False)
      self.index_selector.setValue(self.scale_factor)
      self.index_selector.setLabel('display gain')
      self.index_selector.hideNDControllerOption()
      self.index_selector.reset_scale_toggle()
      self.index_selector.set_emit(True)
    else:
# set up ImagePlaneWidgets ...

# The shared picker enables us to use 3 planes at one time
# and gets the picking order right
      picker = vtk.vtkCellPicker()
      picker.SetTolerance(0.005)

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
      self.planeWidgetY.SetLookupTable(self.planeWidgetX.GetLookupTable())
      self.planeWidgetY.TextureInterpolateOff()
      self.planeWidgetY.SetResliceInterpolate(0)

      self.planeWidgetZ = vtk.vtkImagePlaneWidget()
      self.planeWidgetZ.DisplayTextOn()
      self.planeWidgetZ.SetInput(self.image_array.GetOutput())
      self.planeWidgetZ.SetPlaneOrientationToZAxes()
      self.planeWidgetZ.SetSliceIndex(z_index)
      self.planeWidgetZ.SetPicker(picker)
      self.planeWidgetZ.SetKeyPressActivationValue("z")
      self.planeWidgetZ.SetLookupTable(self.planeWidgetX.GetLookupTable())
      self.planeWidgetZ.TextureInterpolateOff()
      self.planeWidgetZ.SetResliceInterpolate(0)
    
      self.current_widget = self.planeWidgetZ
      self.mode_widget = self.planeWidgetZ
      self.index_selector.set_emit(False)
      self.index_selector.setMinValue(zMin)
      self.index_selector.setMaxValue(zMax,False)
      self.index_selector.setTickInterval( (zMax-zMin) / 10 )
      self.index_selector.setRange(zMax, False)
      self.index_selector.setValue(z_index)
      self.index_selector.setLabel('Z axis')
      self.index_selector.reset_scale_toggle()
      self.index_selector.set_emit(True)

# create scalar bar for display of intensity range
    self.scalar_bar = vtk.vtkScalarBarActor()
    self.scalar_bar.SetLookupTable(self.lut)
    self.scalar_bar.SetOrientationToVertical()
    self.scalar_bar.SetWidth(0.1)
    self.scalar_bar.SetHeight(0.8)
    self.scalar_bar.SetTitle("Intensity")
    self.scalar_bar.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    self.scalar_bar.GetPositionCoordinate().SetValue(0.01, 0.1)


# Create the RenderWindow and Renderer
    self.ren = vtk.vtkRenderer()
    self.renwin.AddRenderer(self.ren)
    
# Add the outline actor to the renderer, set the background color and size
    if self.warped_surface:
      self.ren.AddActor(warp_actor)
    self.ren.AddActor(outlineActor)
    self.ren.SetBackground(0.1, 0.1, 0.2)
    self.ren.AddActor2D(self.scalar_bar)

# Create a text property for cube axes
    tprop = vtk.vtkTextProperty()
    tprop.SetColor(1, 1, 1)
    tprop.ShadowOn()

# Create a vtkCubeAxesActor2D.  Use the outer edges of the bounding box to
# draw the axes.  Add the actor to the renderer.
    self.axes = vtk.vtkCubeAxesActor2D()
    if self.warped_surface:
      if zMin < 0.0 and zMax > 0.0:
        zLoc = 0.0
      else:
        zLoc = zMin 
      self.axes.SetBounds(xMin, xMax, yMin, yMax, zLoc, zLoc)
      self.axes.SetZLabel(" ")
    else:
      self.axes.SetInput(self.image_array.GetOutput())
      self.axes.SetZLabel("Z")
    self.axes.SetCamera(self.ren.GetActiveCamera())
    self.axes.SetLabelFormat("%6.4g")
    self.axes.SetFlyModeToOuterEdges()
    self.axes.SetFontFactor(0.8)
    self.axes.SetAxisTitleTextProperty(tprop)
    self.axes.SetAxisLabelTextProperty(tprop)
    self.axes.SetXLabel("X")
    self.axes.SetYLabel("Y")
    self.ren.AddProp(self.axes)

# Set the interactor for the widgets
    if not self.warped_surface:
      self.planeWidgetX.SetInteractor(self.inter)
      self.planeWidgetX.On()
      self.planeWidgetY.SetInteractor(self.inter)
      self.planeWidgetY.On()
      self.planeWidgetZ.SetInteractor(self.inter)
      self.planeWidgetZ.On()

    self.initialize_camera()

  def initialize_camera(self):
# Create an initial interesting view
    cam1 = self.ren.GetActiveCamera()
    cam1.Azimuth(45)
    if self.warped_surface:
      cam1.Elevation(30)
      xMin, xMax, yMin, yMax, zMin, zMax = self.image_array.GetDataExtent()
      cx = 0.5*(xMax-xMin)
      cy = 0.5*(yMax-yMin)
      cz = 0
      cam1.SetFocalPoint(cx, cy, cz)
    else:
      cam1.Elevation(110)
      cam1.SetViewUp(0, 0, 1)
    cam1.ParallelProjectionOn()
    self.ren.ResetCamera()
    self.ren.ResetCameraClippingRange()

# Align the camera so that it faces the desired widget
  def AlignCamera(self):
    xMin, xMax, yMin, yMax, zMin, zMax = self.extents
    ox, oy, oz = self.origin
    sx, sy, sz = self.spacing
    cx = ox+(0.5*(xMax-xMin))*sx
    cy = oy+(0.5*(yMax-yMin))*sy
    cz = oz+(0.5*(zMax-zMin))*sz
    vx, vy, vz = 0, 0, 0
    nx, ny, nz = 0, 0, 0
    iaxis = self.current_widget.GetPlaneOrientation()
    slice_number = self.current_widget.GetSliceIndex()
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
    self.ren.ResetCamera()
    self.renwin.Render()
 
# Capture the display to a Postscript file
  def CaptureImage(self):
    if not self.image_array is None:
      self.png_number = self.png_number + 1
      png_str = str(self.png_number)
      save_file = './vtk_plot' + png_str + '.ps'
      save_file_no_space= save_file.replace(' ','_')
      w2i = vtk.vtkWindowToImageFilter()
      writer = vtk.vtkPostScriptWriter()
      w2i.SetInput(self.renwin)
      w2i.Update()
      writer.SetInput(w2i.GetOutput())
      writer.SetFileName(save_file_no_space)
      self.renwin.Render()
      writer.Write()

# Capture the display to a PNG file
  def grab_display(self):
    if not self.image_array is None:
      self.png_number = self.png_number + 1
      png_str = str(self.png_number)
      save_file = './vtk_plot' + png_str + '.png'
      save_file_no_space= save_file.replace(' ','_')
      w2if = vtk.vtkWindowToImageFilter()
      w2if.SetInput(self.renwin)
      w2if.Update()
      writer = vtk.vtkPNGWriter()
      writer.SetInput(w2if.GetOutput())
      writer.SetFileName(save_file_no_space)
      self.renwin.Render()
      writer.Write()

# Align the widget back into orthonormal position,
# set the slider to reflect the widget's position,
# call AlignCamera to set the camera facing the widget
  def AlignXaxis(self):
    print 'in AlignXaxis'
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
    self.index_selector.set_emit(False)
    self.index_selector.setMinValue(xMin)
    self.index_selector.setMaxValue(xMax,False)
    self.index_selector.setRange(xMax, False)
    self.index_selector.setValue(slice_number)
    self.index_selector.setTickInterval( (xMax-xMin) / 10 )
    self.index_selector.setLabel('X axis')
    self.index_selector.set_emit(True)

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
    self.index_selector.set_emit(False)
    self.index_selector.setMinValue(yMin)
    self.index_selector.setMaxValue(yMax,False)
    self.index_selector.setRange(yMax, False)
    self.index_selector.setValue(slice_number)
    self.index_selector.setTickInterval( (yMax-yMin) / 10 )
    self.index_selector.setLabel('Y axis')
    self.index_selector.set_emit(True)
#   self.AlignYaxis()
 
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
    self.index_selector.set_emit(False)
    self.index_selector.setMinValue(zMin)
    self.index_selector.setMaxValue(zMax,False)
    self.index_selector.setRange(zMax, False)
    self.index_selector.setValue(slice_number)
    self.index_selector.setTickInterval((zMax-zMin) / 10 )
    self.index_selector.setLabel('Z axis')
    self.index_selector.set_emit(True)
#   self.AlignZaxis()

  def SetSlice(self, sl):
    if self.warped_surface:
      self.scale_factor = sl
      xMin, xMax, yMin, yMax, zMin, zMax = self.image_array.GetDataExtent()
      sx, sy, sz = self.image_array.GetDataSpacing()
      xMin = sx * xMin
      xMax = sx * xMax
      yMin = sy * yMin
      yMax = sy * yMax
      zMin = self.data_min * self.scale_factor
      zMax = self.data_max * self.scale_factor
      if zMin < 0.0 and zMax > 0.0:
        zLoc = 0.0
      else:
        zLoc = zMin 
      self.outline.SetBounds(xMin, xMax, yMin, yMax, zMin, zMax)
      self.axes.SetBounds(xMin, xMax, yMin, yMax, zLoc, zLoc)
      self.warp.SetScaleFactor(self.scale_factor)
    else:
      self.current_widget.SetSliceIndex(sl)
      self.ren.ResetCameraClippingRange()
    self.renwin.Render()

  def UpdateBounds(self):
    if self.warped_surface:
      xMin, xMax, yMin, yMax, zMin, zMax = self.image_array.GetDataExtent()
      sx, sy, sz = self.image_array.GetDataSpacing()
      xMin = sx * xMin
      xMax = sx * xMax
      yMin = sy * yMin
      yMax = sy * yMax
      self.scale_factor = 0.5 * ((xMax-xMin) + (yMax-yMin)) / (self.data_max - self.data_min)
      zMin = self.data_min * self.scale_factor
      zMax = self.data_max * self.scale_factor
      if zMin < 0.0 and zMax > 0.0:
        zLoc = 0.0
      else:
        zLoc = zMin 
      self.outline.SetBounds(xMin, xMax, yMin, yMax, zMin, zMax)
      self.axes.SetBounds(xMin, xMax, yMin, yMax, zLoc, zLoc)
      self.warp.SetScaleFactor(self.scale_factor)
      self.mapper.SetScalarRange(self.data_min,self.data_max)

      min_range = 0.5 * self.scale_factor
      max_range = 2.0 * self.scale_factor
      self.index_selector.set_emit(False)
      self.index_selector.setMaxValue(max_range,False)
      self.index_selector.setMinValue(min_range)
      self.index_selector.setTickInterval( (max_range - min_range) / 10 )
      self.index_selector.setRange(max_range, False)
      self.index_selector.setValue(self.scale_factor)
      self.index_selector.setLabel('display gain')
      self.index_selector.set_emit(True)

    else:

      self.extents =  self.image_array.GetDataExtent()
      self.spacing = self.image_array.GetDataSpacing()
      self.origin = self.image_array.GetDataOrigin()

# get locations for initial slices
      xMin, xMax, yMin, yMax, zMin, zMax =  self.extents
      x_index = (xMax-xMin) / 2
      y_index = (yMax-yMin) / 2
      z_index = (zMax-zMin) / 2

      self.planeWidgetX.SetSliceIndex(x_index)
      self.planeWidgetY.SetSliceIndex(y_index)
      self.planeWidgetZ.SetSliceIndex(z_index)
    
      self.current_widget = self.planeWidgetZ
      self.mode_widget = self.planeWidgetZ
      self.index_selector.set_emit(False)
      self.index_selector.setMinValue(zMin)
      self.index_selector.setMaxValue(zMax,False)
      self.index_selector.setTickInterval( (zMax-zMin) / 10 )
      self.index_selector.setRange(zMax, False)
      self.index_selector.setValue(z_index)
      self.index_selector.setLabel('Z axis')
      self.index_selector.set_emit(True)

  def UpdateScale(self, do_scale=False):
    if do_scale:
      self.image_array.SetDataSpacing(self.scale_values)
    else:
      if self.warped_surface:
        self.image_array.SetDataSpacing((1.0, 1.0, 0.0))
      else:
        self.image_array.SetDataSpacing((1.0, 1.0, 1.0))
    self.UpdateBounds()
    self.initialize_camera()
    self.renwin.Render()

        
      


#=============================
# VTK code for test arrays
#=============================
  def define_sinx_image(self, iteration=1):
# image is just a scaled sin(x) / x. (One could probably compute
# this more quickly.)
    num_ys = 300
    num_xs = 300
    image_numarray = numpy.ones((1,num_ys,num_xs),dtype=numpy.float32)
    for k in range(num_ys):
      k_dist = abs (k - num_ys/2)
      for i in range(num_xs):         
        i_dist = abs (i - num_xs/2)
        dist = math.sqrt(k_dist*k_dist + i_dist*i_dist)         
        if dist == 0:
          image_numarray[0,k,i] = 1.0 * iteration         
        else:
          image_numarray[0,k,i] =  iteration * math.sin(dist) / dist

    self.array_plot(image_numarray)

  def define_image(self, iteration=1):
#    num_arrays = 2
#    num_arrays = 92
#    num_arrays = 10
#    array_dim = 700
    num_arrays = 600
    array_dim = 64
    axis_slice = slice(0,array_dim)
    gain = 1.0 / num_arrays
    image_numarray = numpy.ones((num_arrays,array_dim,array_dim),dtype=numpy.float32)
    array_selector = []
    array_selector.append(0)
    array_selector.append(axis_slice)
    array_selector.append(axis_slice)
#   max_distance = num_arrays / iteration
    max_distance = num_arrays 
    for k in range(max_distance):
      array_tuple = tuple(array_selector)
      image_numarray[array_tuple] = iteration * k * gain
      if k < max_distance:
        array_selector[0] = k + 1
    self.array_plot(image_numarray)

  def define_complex_image(self, iteration=1):
#    num_arrays = 2
#    num_arrays = 92
#    num_arrays = 10
#    array_dim = 700
    num_arrays = 600
    array_dim = 64
    axis_slice = slice(0,array_dim)
    gain = 1.0 / num_arrays
    image_cx_numarray = numpy.ones((num_arrays,array_dim,array_dim),dtype=numpy.complex64)
    image_r_numarray = numpy.ones((num_arrays,array_dim,array_dim),dtype=numpy.float32)
    image_i_numarray = numpy.ones((num_arrays,array_dim,array_dim),dtype=numpy.float32)
    array_selector = []
    array_selector.append(0)
    array_selector.append(axis_slice)
    array_selector.append(axis_slice)
    max_distance = num_arrays / iteration
    for k in range(max_distance):
      array_tuple = tuple(array_selector)
      image_r_numarray[array_tuple] = iteration * k * gain
      image_i_numarray[array_tuple] = iteration * gain / (k+1)
      if k < max_distance:
        array_selector[0] = k + 1
    image_cx_numarray.real = image_r_numarray
    image_cx_numarray.imag = image_i_numarray
    self.array_plot(image_cx_numarray)

  def define_complex_image1(self, iteration=1):
    num_arrays = 20
    array_dim = 3
    axis_slice = slice(1,array_dim)
    axis_slice1 = slice(1,array_dim-1)
    gain = 1.0 / num_arrays
    image_cx_numarray = numpy.zeros((num_arrays,array_dim,array_dim),dtype=numpy.complex64)
    image_r_numarray = numpy.zeros((num_arrays,array_dim,array_dim),dtype=numpy.float32)
    image_i_numarray = numpy.zeros((num_arrays,array_dim,array_dim),dtype=numpy.float32)
    array_selector = []
    array_selector.append(0)
    array_selector.append(axis_slice)
    array_selector.append(axis_slice1)
    max_distance = num_arrays / iteration
    for k in range(max_distance):
      array_tuple = tuple(array_selector)
      image_r_numarray[array_tuple] = iteration * k * gain
      image_i_numarray[array_tuple] = iteration * gain / (k+1)
      if k < max_distance:
        array_selector[0] = k + 1
    image_cx_numarray.real = image_r_numarray
    image_cx_numarray.imag = image_i_numarray
    self.array_plot(image_cx_numarray)

#=============================
# VTK code for test array
#=============================
  def define_random_image(self):
    num_arrays = 93
    array_dim = 64
    image_numarray = numpy.ones((num_arrays,array_dim,array_dim),dtype=numpy.float32)
    for k in range(num_arrays):
      for i in range(array_dim):
        for j in range(array_dim):
          image_numarray[k,i,j] = random.random()
    self.array_plot(image_numarray)

  def array_plot(self, inc_array, data_label='', dummy_parm=False):
    """ convert an incoming numpy into a format that can
        be plotted with VTK
    """
    # first make sure that VTK can really show something useful for the
    # array. Make sure all dimension shapes are 500 or less
    shape = inc_array.shape
    len_shape = len(shape)
    incs = numpy.ones(len_shape)
    resize_image = False
    for i in range(len_shape):
      if shape[i] > 500:
        resize_image = True
        incs[i] = 1 + (shape[i] / 500)
    if resize_image:
      if inc_array.ndim == 2:
        incoming_array = inc_array[::incs[0],::incs[1]]
      else:
        incoming_array = inc_array[::incs[0],::incs[1],::incs[2]]
      Message = "Array has been resampled to fit the 3D VTK display"
      mb_reporter = Qt.QMessageBox.warning(self, "VtkDisplay", Message)
    else:
      incoming_array = inc_array
    
    if incoming_array.ndim == 2:
        temp_array = numpy.ones((1,incoming_array.shape[0],incoming_array.shape[1]),dtype=incoming_array.dtype) 
        temp_array[0,:incoming_array.shape[0],:incoming_array.shape[1]] = incoming_array
        incoming_array = temp_array
    plot_array = None
# convert a complex array to reals followed by imaginaries
    if incoming_array.dtype == numpy.complex64 or incoming_array.dtype == numpy.complex128:
        real_array =  incoming_array.real
        imag_array =  incoming_array.imag
        (nx,ny,nz) = real_array.shape

        image_for_display = numpy.zeros(shape=(nx,ny,nz*2),dtype=real_array.dtype);
        image_for_display[:nx,:ny,:nz] = real_array[:nx,:ny,:nz]
        image_for_display[:nx,:ny,nz:] = imag_array[:nx,:ny,:nz]
        plot_array = image_for_display
        self.complex_plot = True
    else:
        plot_array = incoming_array
        self.complex_plot = False
    if plot_array.ndim == 3 and plot_array.shape[0] == 1:
      self.warped_surface = True
      if  plot_array.min() != self.data_min or plot_array.max() != self.data_max:
        self.data_min = plot_array.min()
        self.data_max = plot_array.max()
# make sure that we're not trying to plot a flat surface
        if self.data_min == self.data_max:
          print ' '
          print ' **************************************** '
          print ' sorry - cannot visualize a flat surface! '
          print ' **************************************** '
          print ' '
          return
    else:
      self.warped_surface = False
    if self.image_array is None:
      self.image_array = vtkImageImportFromNumpy()
      if plot_array.ndim > 3:
        self.image_array.SetArray(plot_array[0])
      else:
        self.image_array.SetArray(plot_array)

# use default VTK parameters for spacing at the moment
      if self.warped_surface:
        spacing = (1.0, 1.0, 0.0)
      else:
        spacing = (1.0, 1.0, 1.0)
      self.image_array.SetDataSpacing(spacing)

# create new VTK pipeline
      self.set_initial_display()

      self.lut.SetTableRange(plot_array.min(), plot_array.max())
      self.lut.ForceBuild()
    else:
      if plot_array.ndim > 3:
        self.image_array.SetArray(plot_array[0])
      else:
        self.image_array.SetArray(plot_array)
      self.lut.SetTableRange(plot_array.min(), plot_array.max())
      self.lut.ForceBuild()
      self.UpdateBounds()
# refresh display if data contents updated after
# first display
      self.renwin.Render()
 
  def setAxisIncrements(self, axis_increments):
    """ used to set proper range of axes -
        not that useful at present 
    """
    if len(axis_increments) == 2:
      if self.warped_surface:
        self.scale_values = (axis_increments[0], axis_increments[1], 0.0)
      else:
        self.scale_values = (axis_increments[0], axis_increments[1], 1.0)
    else:
      self.scale_values = axis_increments
    pass

  def reset_image_array(self):
    self.image_array = None

  def AddUpdate(self):
    self.index_selector.displayUpdateItem()

  def HideNDButton(self):
    self.index_selector.hideNDControllerOption()

  def start_timer(self, time):
    timer = qt.QTimer()
    timer.connect(timer, qt.SIGNAL('timeout()'), self.testEvent)
    timer.start(time)

  def testEvent(self):
    self.iteration = self.iteration + 1
    self.define_random_image()
#   self.define_image(self.iteration)
#   self.define_complex_image(self.iteration)
#   self.define_complex_image1(self.iteration)
#   self.define_sinx_image(self.iteration)

  def two_D_Event(self):
    self.emit(Qt.SIGNAL("show_2D_Display"),0)

  def hide_Event(self, toggle_ND_Controller):
    self.emit(Qt.SIGNAL("show_ND_Controller"),toggle_ND_Controller)

  def AddVTKExitEvent(self):
# next line causes confusion if run inside the MeqBrowser
    self.renwininter.AddObserver("ExitEvent", lambda o, e, a=app: a.quit())

  def setAxisParms(self, axis_parms):
    """ set display information from axis parameters """

    if self.warped_surface:
      text = ' '
      if axis_parms[1] is None:
        text = 'X'
      else:
        text = 'X ' + axis_parms[1]
      if not self.axes is None:
          self.axes.SetXLabel(text)

      if axis_parms[0] is None:
        text = 'Y'
      else: 
        text = 'Y ' + axis_parms[0]
      if not self.axes is None:
        self.axes.SetYLabel(text)
    else:
      text = ' '
      text_menu = ' '
      if axis_parms[2] is None:
        text_menu = 'X axis '
        if self.complex_plot:
          text = 'X (real then imag) '
        else:
          text = 'X '
      else: 
        text_menu = 'X axis: ' + axis_parms[2]
        if self.complex_plot:
          text = 'X ' + axis_parms[2] + ' (real then imag)'
        else:
          text = 'X ' + axis_parms[2]
      self.index_selector.setXMenuLabel(text_menu)
      if not self.axes is None:
        self.axes.SetXLabel(text)

      if axis_parms[1] is None:
        text_menu = 'Y axis '
        text = 'Y'
      else:
        text_menu = 'Y axis: ' + axis_parms[1]
        text = 'Y ' + axis_parms[1]
      self.index_selector.setYMenuLabel(text_menu)
      if not self.axes is None:
          self.axes.SetYLabel(text)

      if axis_parms[0] is None:
        text = 'Z'
        text_menu = 'Z axis '
      else: 
        text_menu = 'Z axis: ' + axis_parms[0]
        text = 'Z ' + axis_parms[0]
      self.index_selector.setZMenuLabel(text_menu)
      if not self.axes is None:
        self.axes.SetZLabel(text)

#=============================
if __name__ == "__main__":
  if has_vtk:
    app = qt.QApplication(sys.argv)
    qt.QObject.connect(app,qt.SIGNAL("lastWindowClosed()"),
		app,qt.SLOT("quit()"))
    display = vtk_qt_3d_display()
    display.show()
    display.AddUpdate()
    display.testEvent()
    app.exec_()
  else:
    print ' '
    print '**** Sorry! It looks like VTK is not available! ****'

