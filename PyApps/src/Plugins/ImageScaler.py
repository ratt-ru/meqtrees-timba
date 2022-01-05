#!/usr/bin/env python3


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
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys
import numpy
import math

# Maps a double interval into an integer interval

# The ImageScaler class maps an interval of type double into an interval of
# type int. It consists of two intervals D = [d1, d2] (double) and 
# I = [i1, i2] (int), which are specified with the setDblRange and setIntRange
# members. The point d1 is mapped to the point i1, and d2 is mapped to i2. 
# Any point inside or outside D can be mapped to a point inside or outside
# I using transform or limTransform or vice versa using invTransform. 
# D can be scaled linearly or logarithmically, as specified with setDblRange.
#
# This is a translation of the QWT Package's QwtDiMap class to work 
# directly with python numpy arrays

class ImageScaler:
  LogMin = 1.0e-150
  LogMax = 1.0e150

  def __init__(self, i1=0, i2=1, d1=0.0, d2=1.0, logarithmic=False):
    self.d_x1 = float(d1)        # lower bound of double interval
    self.d_x2 = float(d2)        # upper bound of double interval
    self.d_y1 = i1               # lower bound of integer interval
    self.d_y2 = i2               # upper bound of integer interval
    self.d_cnv = 1.0             # conversion factor
    self.d_log = logarithmic     # logarithmic scale?
    self.setDblRange(self.d_x1, self.d_x2, logarithmic)

  def d1(self):
# return the first border of the double interval
    return self.d_x1

  def d2(self):
# return the second border of the double interval
    return self.d_x2

  def i1(self):
# return the first border of the integer interval
    return self.d_y1

  def i2(self):
# return the second border of the integer interval
    return self.d_y2

  def logarithmic(self):
# return TRUE if the double interval is scaled logarithmically
    return self.d_log

  def cnv(self):
# return the conversion factor
    return self.d_cnv

  def iTransform(self,x):
#  Transform a point in double interval into an point in the
#  integer interval
#  param: x floating point array to be transformed
#  linear mapping:<dd>rint(i1 + (i2 - i1) / (d2 - d1) * (x - d1))
#  logarithmic mapping:<dd>rint(i1 + (i2 - i1) / log(d2 / d1) * log(x / d1))
#  warning: The specified point is allowed to lie outside the intervals. If you
#  want to limit the returned value, use the limTransform method.
    temp_array = None
    if self.d_log:
        temp_array = numpy.around((numpy.log(x) - self.d_x1) * self.d_cnv)
    else:
        temp_array = numpy.around((x - self.d_x1) * self.d_cnv)
    return self.d_y1 + temp_array.astype(numpy.int32)


  def setDblRange(self, d1, d2, lg=False):
# Specify the borders of the double interval
# param: d1 first border
# param: d2 second border 
# param: lg logarithmic (TRUE) or linear (FALSE) scaling
    if lg:
        self.d_log = True;
        if d1 < self.LogMin: 
           d1 = self.LogMin
        elif d1 > self.LogMax: 
           d1 = self.LogMax
        
        if d2 < self.LogMin: 
           d2 = self.LogMin
        elif d2 > self.LogMax: 
           d2 = self.LogMax
        
        self.d_x1 = math.log(d1);
        self.d_x2 = math.log(d2);
    else:
        self.d_log = False
        self.d_x1 = d1
        self.d_x2 = d2
    self.newFactor();

  def newFactor(self):
# Re-calculate the conversion factor.
    if self.d_x2 != self.d_x1:
       self.d_cnv = 1.0 * (self.d_y2 - self.d_y1) / (self.d_x2 - self.d_x1); 
    else: 
       d_cnv = 0.0;

  def setIntRange(self, i1, i2):
# Specify the borders of the integer interval
# param: i1 first border
# param: i2 second border
    self.d_y1 = i1
    self.d_y2 = i2
    self.newFactor()

  def invTransform(self, y):
# Transform an integer value into a double value
# param: y integer array to be transformed
# linear mapping:<dd>d1 + (d2 - d1) / (i2 - i1) * (y - i1)
# logarithmic mapping:<dd>d1 + (d2 - d1) / log(i2 / i1) * log(y / i1)
    if self.d_cnv == 0.0:
       return 0.0;
    else:
       temp_array = self.d_x1 + ((y - self.d_y1) / self.d_cnv).astype(numpy.float64) 
       if self.d_log: 
           return numpy.exp(temp_array)
       else:
           return temp_array

  def limTransform(self, x):
# Transform and limit
# The function is similar to transform, but limits the input value
# to the nearest border of the map's double interval if it lies outside
# that interval.
# param: x array to be transformed
# return transformed value
    if self.d_log: 
      if x > self.LogMax:
          x = self.LogMax
      elif x < self.LogMin:
          x = self.LogMin
      x = numpy.log(x)
    
    if  x > max(self.d_x1, self.d_x2):
      x = max(self.d_x1, self.d_x2);
    elif  x < min(self.d_x1, self.d_x2):
      x = min(self.d_x1, self.d_x2);

    if self.d_log:
      return self.transform(numpy.exp(x))
    else:
      return self.transform(x)

  def xTransform(self, x):
# Exact transformation
# This function is similar to transform, but
# makes the integer interval appear to be double. 
# param: x array to be transformed
# linear mapping:<dd>i1 + (i2 - i1) / (d2 - d1) * (x - d1)
# logarithmic mapping:<dd>i1 + (i2 - i1) / log(d2 / d1) * log(x / d1)
    if self.d_log:
       rv = float(self.d_y1) + (numpy.log(x) - self.d_x1) * self.d_cnv;    
    else:
       rv = float(self.d_y1) + (x - self.d_x1) * self.d_cnv;
    return rv;


  def transform(self, x):
#  Transform a point in double interval into an point in the
#  integer interval
# param x value
# return:
# linear mapping:<dd>rint(i1 + (i2 - i1) / (d2 - d1) * (x - d1))
# logarithmic mapping:<dd>rint(i1 + (i2 - i1) / log(d2 / d1) * log(x / d1))

# warning The specified point is allowed to lie outside the intervals. If you
# want to limit the returned value, use QwtDiMap::limTransform.
    if self.d_log:
        rv =  self.d_y1 + numpy.ceil((numpy.log(x) - self.d_x1) * self.d_cnv)
    else:
        rv = self.d_y1 + numpy.ceil((x - self.d_x1) * self.d_cnv)
    return rv

def main(args):
  b = 1 + numpy.array(list(range(1000)))
  c = 1.0 * b
  a = ImageScaler(1, 256, c.min(), c.max(), True)
  print(a.logarithmic())
  print(a.d2())
  print(a.cnv())
  d = a.iTransform(c)
  print('d = ',  d)
  d = a.xTransform(c)
  print('d = ',  d)
  e = a.invTransform(d)
  print('e = ',  e)

if __name__ == '__main__':
    main(sys.argv)

