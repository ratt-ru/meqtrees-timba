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

from UVPAxis import *
from numarray import *
from qt import *

class ComplexColorMap:

  def __init__(self, numColors):
# create arrays for holding colormap values
#    self._itsComplexColormap = zeros((numColors*numColors), UInt32)
    self._itsComplexColormap = []
    self._itsRealIndex = zeros((numColors),UInt32)
    self._itsImagIndex = zeros((numColors),UInt32)
    for i in range(numColors):
      self._itsRealIndex[i] = i;
      self._itsImagIndex[i] = numColors*i;
    for j in range(numColors*numColors):
      
      c = QColor(qRgb(j%numColors, j/numColors, 0),j+numColors)
#      print "c ",c
      self._itsComplexColormap.append(c)
#      self._itsComplexColormap[j] = self.set_Rgb(j%numColors, j/numColors, 0)

# create UVPAxis objects for scaling values
    self._itsXAxis = UVPAxis(1, 0, "X", "arbitrary")
    self._itsYAxis = UVPAxis(1, 0, "Y", "arbitrary")

    slope = 1.0;
    self.initColormap(slope)
  
  def initColormap(self, slope):
    print 'in initColormap'
    min_color = 0;
    max_color = 255;
    numColors = len(self._itsRealIndex)

  # The complex color table;
    for i in range(numColors):
      green  = fabs(min_color + slope*(float(i)-numColors/2));
      if green < min_color:
        green = min_color 
      if green > max_color:
        green = max_color 
      Green = int(green + 0.5);
      Blueim  = 0;
      if  i < numColors>>1:
        Blueim = Green>>1

      for r in range(numColors):
        red  = fabs(min_color + slope*(float(r)-numColors/2));
        if red < min_color:
          red = min_color;
        if red > max_color:
          red = max_color;
        Red = int(red + 0.5);
        Bluere  = 0;
        if  r < numColors>>1:
          Bluere = Red>>1;
          location = self._itsRealIndex[r]+self._itsImagIndex[i];
#          modify_color = QColor()
#          self._itsComplexColormap[location] = self.set_Rgb(Red, Green, Blueim+Bluere)
#          modify_color.setRgb(Red, Green, Blueim+Bluere)

          self._itsComplexColormap[location].setRgb(Red, Green, Blueim+Bluere)

#copied from Qt's qcolor.h header
# set RGB value
  def set_Rgb(self, r, g, b ):
    if ( int(r) > 255 or int(g) > 255 or int(b) > 255 ):
      print "RGB parameter(s) out of range"
      return 0
    value = (0xff << 24) | ((int(r) & 0xff) << 16) | ((int(g) & 0xff) << 8) | (int(b) & 0xff)
    return value

  def getNumberOfColors(self):
    return len(self._itsRealIndex)

  def getXAxis(self): 
    return self._itsXAxis
  def getYAxis(self):
    return self._itsYAxis;

  def setXAxis(self, axis):
    self._itsXAxis = axis;
  def setYAxis(self, axis):
    self._itsYAxis = axis;

  def get_color_value(self,r,i):
    location = self._itsRealIndex[r]+self._itsImagIndex[i];
    return self._itsComplexColormap[location] 

#
# self-test block
#
if __name__ == '__main__':
  a = ComplexColorMap(256)
  print a.getNumberOfColors()
