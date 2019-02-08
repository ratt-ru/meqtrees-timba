##
## Copyright (C) 2002-2007
## ASTRON (Netherlands Foundation for Research in Astronomy)
## and The MeqTree Foundation
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

# This is a python translation of Michiel Brentjens UVPDisplayArea.cc code


#% $Id$ 


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
#  You should have received a copy	 Vous devez avoir recu une copie
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
from .UVPAxis import *
import numpy
import math
from qt import *

class ComplexColorMap:

  def __init__(self, numColors):
# create arrays for holding colormap values
#    self._itsComplexColormap = numpy.zeros((numColors*numColors), numpy.uint32)
    self._itsComplexColormap = []
    self._itsRealIndex = numpy.zeros((numColors),numpy.uint32)
    self._itsImagIndex = numpy.zeros((numColors),numpy.uint32)
    for i in range(numColors):
      self._itsRealIndex[i] = i;
      self._itsImagIndex[i] = numColors*i;
    for j in range(numColors*numColors):
      
#      c = QColor(qRgb(j%numColors, j/numColors, 0),j+numColors)
#      print "c ",c
      c = QColor(qRgb(j%numColors, j/numColors, 0),j+numColors)
#      d = (long(c.rgb()))
#      print j , d
      self._itsComplexColormap.append(c)

# create UVPAxis objects for scaling values
    self._itsXAxis = UVPAxis(1, 0, "X", "arbitrary")
    self._itsYAxis = UVPAxis(1, 0, "Y", "arbitrary")

    slope = 1.0;
    self.initColormap(slope)
  
  def initColormap(self, slope):
    print('in initColormap')
    min_color = 0;
    max_color = 255;
    numColors = len(self._itsRealIndex)

  # The complex color table;
    for i in range(numColors):
      green  = abs(min_color + slope*(float(i)-numColors/2));
      if green < min_color:
        green = min_color 
      if green > max_color:
        green = max_color 
      Green = int(green + 0.5);
      Blueim  = 0;
      if  i < numColors>>1:
        Blueim = Green>>1

      for r in range(numColors):
        red  = abs(min_color + slope*(float(r)-numColors/2));
        if red < min_color:
          red = min_color;
        if red > max_color:
          red = max_color;
        Red = int(red + 0.5);
        Bluere  = 0;
        if  r < numColors>>1:
          Bluere = Red>>1;
          location = self._itsRealIndex[r]+self._itsImagIndex[i];
          self._itsComplexColormap[location].setRgb(Red, Green, Blueim+Bluere)
          temp = self._itsComplexColormap[location].rgb()

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

# return a color value as an unsigned int
  def get_color_value(self,r,i):
    location = self._itsRealIndex[r]+self._itsImagIndex[i];
    return self._itsComplexColormap[location].rgb() 

#
# self-test block
#
if __name__ == '__main__':
  a = ComplexColorMap(256)
  print(a.getNumberOfColors())
