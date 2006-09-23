#!/usr/bin/env python

# This example shows how to combine data from both the imaging and
# graphics pipelines. The vtkMergeFilter is used to merge the data
# from each together. This script is an adaption of the VTK
# example script:
# VTK/Examples/VisualizationAlgorithms/Python/imageWarp.py
import vtk
import numarray
import random
from math import *
from vtkImageImportFromNumarray import *

# Create an image with numarray and convert to VTK ImageData format.
# The image is extracted as a set of polygons (vtkImageDataGeometryFilter). 
# We then warp the plane using the scalar values.

# image is just a scaled sin(x) / x. (One could probably compute
# this more quickly.)
num_arrays = 100
array_dim = 100
image_numarray = numarray.ones((1,num_arrays,array_dim),type=numarray.Float32)
for k in range(num_arrays):
  k_dist = abs (k - num_arrays/2) 
  for i in range(array_dim):
    i_dist = abs (i - array_dim/2)
    dist = sqrt(k_dist*k_dist + i_dist*i_dist)
    if dist == 0:
      image_numarray[0,k,i] = 1.0
    else:
      image_numarray[0,k,i] =  sin(dist) / dist

data_min = image_numarray.min()
data_max = image_numarray.max()

# now display it
image_array = vtkImageImportFromNumarray()
image_array.SetArray(image_numarray)

geometry = vtk.vtkImageDataGeometryFilter()
geometry.SetInput(image_array.GetOutput())
warp = vtk.vtkWarpScalar()
warp.SetInput(geometry.GetOutput())
scale_factor = 50.0
warp.SetScaleFactor(scale_factor)

# create blue to red color table
lut = vtk.vtkLookupTable()
lut.SetHueRange(0.6667, 0.0)
lut.SetNumberOfColors(256)
lut.Build()
lut.SetRange(scale_factor*data_min, scale_factor*data_max)

mapper = vtk.vtkPolyDataMapper();
mapper.SetInput(warp.GetPolyDataOutput())
mapper.SetLookupTable(lut)
mapper.ImmediateModeRenderingOff()
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# create scalar bar
scalar_bar = vtk.vtkScalarBarActor()
scalar_bar.SetLookupTable(lut)
scalar_bar.SetOrientationToVertical()
scalar_bar.SetWidth(0.1)
scalar_bar.SetHeight(0.8)
scalar_bar.SetTitle("Intensity")
scalar_bar.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
scalar_bar.GetPositionCoordinate().SetValue(0.01, 0.1)

# Create renderer stuff
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)
iren.Initialize()

camstyle = vtk.vtkInteractorStyleTrackballCamera()
iren.SetInteractorStyle(camstyle)

#  Make the bounding box
outline = vtk.vtkOutlineSource();
xMin, xMax, yMin, yMax, zMin, zMax = image_array.GetDataExtent()
outline.SetBounds(xMin, xMax, yMin, yMax, data_min * scale_factor, data_max* scale_factor)
outline_mapper = vtk.vtkPolyDataMapper();
outline_mapper.SetInput(outline.GetOutput() );
outline_actor = vtk.vtkActor();
outline_actor.SetMapper(outline_mapper);
outline_actor.VisibilityOn();

# Create a text property for cube axes
tprop = vtk.vtkTextProperty()
tprop.SetColor(1, 1, 1)
tprop.ShadowOn()

# Create a vtkCubeAxesActor2D.  Use the outer edges of the bounding box to
# draw the axes.  Add the actor to the renderer.
axes = vtk.vtkCubeAxesActor2D()
axes.SetBounds(xMin, xMax, yMin, yMax,  data_min * scale_factor, data_max* scale_factor)
axes.SetCamera(ren.GetActiveCamera())
axes.SetLabelFormat("%6.4g")
axes.SetFlyModeToOuterEdges()
axes.SetFontFactor(0.8)
axes.SetAxisTitleTextProperty(tprop)
axes.SetAxisLabelTextProperty(tprop)
axes.SetXLabel("X")
axes.SetYLabel("Y")
axes.SetZLabel("Z")
ren.AddProp(axes)

# Add the actors to the renderer, set the background and size
ren.AddActor(actor)
ren.AddActor(outline_actor);
ren.AddActor2D(scalar_bar)
ren.SetBackground(0.1, 0.2, 0.4)
ren.ResetCameraClippingRange()

renWin.SetSize(500, 500)

cam1 = ren.GetActiveCamera()
cx = 0.5*(xMax-xMin)
cy = 0.5*(yMax-yMin)
cz = 0
cam1.SetFocalPoint(cx, cy, cz)
cam1.SetPosition(cx,cy, cz)
cam1.Azimuth(40)
cam1.Elevation(30)
cam1.Zoom(-5)
ren.ResetCamera()

renWin.Render()
iren.Start()
