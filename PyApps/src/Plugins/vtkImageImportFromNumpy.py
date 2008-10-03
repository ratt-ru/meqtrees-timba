#
#% $Id: vtkImageImportFromNumpy.py 5418 2007-07-19 16:49:13Z oms $ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
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
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""
vtkImageImportFromNumpy: a Numpy front-end to vtkImageImport

Adapted by AGW directly from the VTK distribution's  
vtkImageImportFromArray.py code module

Load a Numpy Python array into a VTK image.

Methods:

  GetOutput() -- connect to VTK image pipeline
  SetArray()  -- set the array to load in
  
Convert python 'Int' to VTK_UNSIGNED_SHORT:
(python doesn't support unsigned short, so this might be necessary)

  SetConvertIntToUnsignedShort(yesno)
  ConvertIntToUnsignedShortOn()
  ConvertIntToUnsignedShortOff()

Methods from vtkImageImport: 
(if you don't set these, sensible defaults will be used)

  SetDataExtent()
  SetDataSpacing()
  SetDataOrigin()
"""

import numpy
from vtk import vtkImageImport
from vtk.util.vtkConstants import *

class vtkImageImportFromNumpy:
    def __init__(self):
        self.__import = vtkImageImport()
        self.__ConvertIntToUnsignedShort = 0

    # type dictionary: note that python doesn't support
    # unsigned integers properly!
    __typeDict = {'c':VTK_UNSIGNED_CHAR,
                  'b':VTK_UNSIGNED_CHAR,
                  '1':VTK_CHAR,
                  's':VTK_SHORT,
                  'i':VTK_INT,
                  'l':VTK_LONG,
                  'f':VTK_FLOAT,
                  'd':VTK_DOUBLE,
                  'F':VTK_FLOAT,
                  'D':VTK_DOUBLE }

    # convert 'Int32' to 'unsigned short'
    def SetConvertIntToUnsignedShort(self,yesno):
        self.__ConvertIntToUnsignedShort = yesno

    def GetConvertIntToUnsignedShort(self):
        return self.__ConvertIntToUnsignedShort
    
    def ConvertIntToUnsignedShortOn(self):
        self.__ConvertIntToUnsignedShort = 1

    def ConvertIntToUnsignedShortOff(self):
        self.__ConvertIntToUnsignedShort = 0

    # get the output
    def GetOutput(self):
        return self.__import.GetOutput()

    # import an array
    def SetArray(self,imArray):
        assert not numpy.issubdtype(imArray.dtype, complex), \
           "Complex numpy arrays cannot be converted to vtk arrays."\
           "Use real() or imag() to get a component of the array before"\
           " passing it to vtk."
        numComponents = 1
        dim = imArray.shape
        assert len(dim) < 4, \
           "Only arrays of dimensionality 3 or lower are allowed!"

        type = self.__typeDict[imArray.dtype.char]
        if (self.__ConvertIntToUnsignedShort and imArray.dtype.char == 'i'):
            type = VTK_UNSIGNED_SHORT
        # Point the VTK array to the numpy data.
        self.__import.CopyImportVoidPointer(imArray.data, imArray.nbytes)
        self.__import.SetDataScalarType(type)
        self.__import.SetNumberOfScalarComponents(numComponents)
        extent = self.__import.GetDataExtent()
        self.__import.SetDataExtent(extent[0],extent[0]+dim[2]-1,
                                    extent[2],extent[2]+dim[1]-1,
                                    extent[4],extent[4]+dim[0]-1)
        self.__import.SetWholeExtent(extent[0],extent[0]+dim[2]-1,
                                     extent[2],extent[2]+dim[1]-1,
                                     extent[4],extent[4]+dim[0]-1)

    # a whole bunch of methods copied from vtkImageImport

    def SetDataExtent(self,extent):
        self.__import.SetDataExtent(extent)

    def GetDataExtent(self):
        return self.__import.GetDataExtent()
    
    def SetDataSpacing(self,spacing):
        self.__import.SetDataSpacing(spacing)

    def GetDataSpacing(self):
        return self.__import.GetDataSpacing()
    
    def SetDataOrigin(self,origin):
        self.__import.SetDataOrigin(origin)

    def GetDataOrigin(self):
        return self.__import.GetDataOrigin()
    
