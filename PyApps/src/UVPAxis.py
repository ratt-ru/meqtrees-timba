##
## Copyright (C) 2002
## ASTRON (Netherlands Foundation for Research in Astronomy)
## P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##


# Manages the properties of a coordinate axis of a dataset.
# The UVPAxis class is used to scale and shift coordinates. One of
# its applications is the mapping of a value in the real world to a
# value in the pixel or intensity domain. For example for making graphs
# of data. The transfer function is: world = itsOffset +
# itsScale*axis. The inverse function is of course; axis = (world -
# itsOffset)/itsScale. Therefore itsScale may never have a zero value.
#
# This is a python translation of Michiel Brentjens UVPAxis.cc code
class UVPAxis:
  def __init__(self, scale=1.0,offset=0.0,type=" ",unit=" "):
    assert scale != 0.0, 'scale cannot be zero!'
    self._itsScale = float(scale)
    self._itsInverseScale = float(1.0 / self._itsScale)
    self._itsOffset = float(offset)
    self._itsType = type
    self._itsUnit = unit

   # Sets the transferfunction for this axis: world = offset + scale*axis.
   # scale may not be 0.0.
   #offset may have any value.
  def setTransferFunction(self, scale,offset):
    assert scale != 0.0, 'scale cannot be zero!'
    self._itsScale  = float(scale) 
    self._itsInverseScale = float(1.0/self._itsScale) 
    self._itsOffset = float(offset) 

  # Calculates scale and offset of the transfer function from the
  # provided world- and axis-ranges.

  # calcTransferFunction calculates itsScale and itsOffset fromn the
  # world and axis ranges that are provided by the caller.
  # axisMin and axisMax may be pixel coordinates on a screen. axisMin may
  # not be equal to axisMax. worldMin may not be equal to worldMax.
  #
  def calcTransferFunction(self, worldMin, worldMax, axisMin, axisMax):
    assert axisMin != axisMax, 'axisMin and axisMax cannot have the same values'
    assert worldMin != worldMax, 'worldMin and worldMax cannot have the same values'
    self._itsScale        = (float(worldMax)-float(worldMin))/(float(axisMax)-float(axisMin)) 
    self._itsInverseScale = float(1.0/self._itsScale) 
    self._itsOffset       = float(worldMax) - self._itsScale*float(axisMax) 

  # axis = (world - itsOffset)/itsScale
  # world is the real-world value of the coordinate.
  # returns the corresponding value on the axis.
  #
  def worldToAxis(self, world):
    return (float(world) - self._itsOffset)*self._itsInverseScale

  # world = itsOffset + itsScale*axis
  # axis is the value of the coordinate on the axis. For
  #    example a pixel coordinate.
  # returns the corresponding real-world value.
  #
  def axisToWorld(self, axis):
    return self._itsOffset + float(axis)*self._itsScale;

  # returns itsScale.
  def getScale(self):
     return self._itsScale

  # returns itsOffset.
  def getOffset(self):
    return self._itsOffset

  # returns itsType.
  def getType(self):
     return self._itsType

  # returns itsUnit.
  def getUnit(self):
    return self._itsUnit

#
# self-test block
#
if __name__ == '__main__':
  a = UVPAxis()
  a.calcTransferFunction(1.0, 20.0, 1.0, 5.0)
  print 'scale is ', a.getScale()
  print 'offset is ', a.getOffset()
  print 'expected max axis value should be 5 and is ', a.worldToAxis(20.0)
  print 'expected min axis value should be 1 and is ', a.worldToAxis(1.0)
  print 'expected max world value should be 20 and is ', a.axisToWorld(5.0)
  print 'expected min world value should be 1 and is ', a.axisToWorld(1.0)

