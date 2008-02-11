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

from Timba.TDL import *
from Timba import pynode
from Timba import dmi
from Timba import utils
from Timba.Meq import meq
from Timba.Meq import meqds
import Meow.Bookmarks

_dbg = utils.verbosity(0,name='BeamPhasePlot');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

from numarray import *


# This PyNode uses matplotlib (pylab) to plot beam weights that have been
# stored in a 'mep' table by the script MG_AGW_store_beam_weights.py. 
# We use the casacore pyrap python wrappers to get data from the aips++ 
# formatted mep table.

class BeamPhasePlot (pynode.PyNode):
  """ Make a plot of beam weights and orientations """

  def __init__ (self, *args):
    pynode.PyNode.__init__(self,*args);
    self.set_symdeps('domain','resolution');

    # we need the following two lines to output a svg file 
    # without hanging the system
    import matplotlib
    matplotlib.use('SVG')


  def update_state (self,mystate):
    """ get the name of the mep file from which to read weights """
    mystate('file_name','beam_weights.mep');
    print 'file name is ', self.file_name


# The following method to plot an arrow with amplitude and
# direction was adapted from a plotting script of Walter Brisken
  def arrow(self,x, y, u, v,rotate_angle=False):
    """ calculate vertices of a filled arrow shape as a function of 
        amplitude and phase """
  
    X = zeros(shape=(4,),type=Float32)
    Y = zeros(shape=(4,),type=Float32)
    if rotate_angle:
      t = -1.0 * math.atan2(v, u)
    else:
      t = math.atan2(v, u)
    a = 0.5*math.sqrt(u*u + v*v)
    X[0] = x+a*math.sin(t)
    Y[0] = y+a*math.cos(t)
    X[1] = x+a*math.sin(t+2.9)
    Y[1] = y+a*math.cos(t+2.9)
    X[2] = x+a*math.sin(t-2.9)
    Y[2] = y+a*math.cos(t-2.9)
    X[3] = x+a*math.sin(t)
    Y[3] = y+a*math.cos(t)
    return (X,Y)

  def plot_weights(self,i, j, weight_re, weight_im, flip_weight,rotate_angle):
      """ determine a colour for the arrow plot and then plot the weights """
      abs_value = math.sqrt(weight_re * weight_re + weight_im * weight_im)
      if abs_value < 0.3:
        colour = 'b'
      if abs_value >= 0.3 and abs_value < 0.6:
        colour = 'g'
      if abs_value >= 0.6:
        colour = 'r'
      if flip_weight:
        p, q = self.arrow(i, j+0.5, weight_im, weight_re, rotate_angle)
      else:
        p, q = self.arrow(i+0.5, j, weight_re, weight_im, rotate_angle)
      # use the supplied matplotlib 'fill' function
      import pylab
      pylab.fill(p,q, colour)

# find weight with maximum amplitude
  def get_max_value (self):
    max_abs = 0.0
    for k in range(len(self.weight_re)):
      abs_value = math.sqrt(self.weight_re[k] * self.weight_re[k] + self.weight_im[k] * self.weight_im[k])
      if abs_value > max_abs:
        max_abs = abs_value
    return max_abs

  def create_figure (self, max_abs):
# do first group of weights
    flip_weight = False
    rotate_angle = True
    counter = 0
    i = 8
    j = -1
    for k in range(len(self.weight_re)):
      j = j + 1
      if j > 9:
        i = i - 1
        j = 0
        if i < 0:
          break
      self.plot_weights(i, j, self.weight_re[counter]/max_abs, self.weight_im[counter]/max_abs,flip_weight,rotate_angle)
      counter = counter + 1

# do second group of weights
    flip_weight = True
    rotate_angle = False
    start = counter
    i = 9
    j = -1
    for k in range(start,len(self.weight_re)):
      j = j + 1
      if j > 8:
        i = i - 1
        j = 0
        if i < 0:
          break
      self.plot_weights(i, j, self.weight_re[counter]/max_abs, self.weight_im[counter]/max_abs, flip_weight,rotate_angle)
      counter = counter + 1

# plot an arrow with normalized amplitude of 1 as a reference
    self.plot_weights(-1.5, 0.5, 1.0, 0.0,False,False)

  def get_result (self, request, *children):
    """ plot data from the mep file """

# first load data from table
    import pylab
    try:
      import pycasatable
      t = pycasatable.table(self.file_name)
    except:
      try:
        import pyrap_tables
        t = pyrap_tables.table(self.file_name)
      except:
        print 'no python interface to aips++ tables was found'
        result = meq.result()
        return result
    num_rows = len(t.rownumbers(t))
    print 'number of rows ', num_rows
    svg_list = []

# read in and store weights in a list
# first plot phase conjugate weights
#   pylab.subplot(211)
    pylab.figure(1)
    row_number = -1
    self.weight_re = []
    self.weight_im = []
    status = True
    while status:
      row_number = row_number + 1
      try:
        name = t.getcell('NAME', row_number)
#       print ' weight name ', name
      except:
        print 'setting status to false on EOF'
        status = False
        break
      if name.find('I_parm_max') > -1:
        print 'setting status to false on finding I_parm_max'
        status = False
        break
      else:
        try: 
          self.weight_re.append(t.getcell('VALUES',row_number)[0][0])
          row_number = row_number + 1
          name = t.getcell('NAME', row_number)
#         print ' weight name ', name
          self.weight_im.append(t.getcell('VALUES',row_number)[0][0])
        except:
          status = False
    max_abs = self.get_max_value()
    self.create_figure(max_abs)
    pylab.xlabel('X/I location of feed')
    pylab.ylabel('Y/J location of feed')
    pylab.grid(True)
    pylab.title('Amplitude and Phase of Conjugate Beam Weights')

    svg_name = 'demo'
    pylab.savefig(svg_name)
    file_name = svg_name + '.svg' 
    file = open(file_name,'r')
    svg_list.append(file.readlines())
    file.close()

# try to plot gaussian fitted weights
    self.weight_re = []
    self.weight_im = []
    status = True

    while status:
      row_number = row_number + 1
      try:
        name = t.getcell('NAME', row_number)
  #       print ' weight name ', name
      except:
        print 'part 2: setting status to false on EOF'
        status = False
        break
      if name.find('I_parm_max') > -1:
        print 'part 2: setting status to false on finding I_parm_max'
        status = False
        break
      else:
        try: 
          self.weight_re.append(t.getcell('VALUES',row_number)[0][0])
          row_number = row_number + 1
          name = t.getcell('NAME', row_number)
          self.weight_im.append(t.getcell('VALUES',row_number)[0][0])
        except:
          status = False
    t.close()
    if len(self.weight_re) > 0:
      print 'generating 2nd plot with num data points: ', len(self.weight_re)
#     pylab.subplot(212)
      pylab.figure(2)
      max_abs = self.get_max_value()
      self.create_figure(max_abs)
      pylab.xlabel('X/I location of feed')
      pylab.ylabel('Y/J location of feed')
      pylab.grid(True)
      pylab.title('Amplitude and Phase of Beam Weights')
      svg_name = 'demo'
      pylab.savefig(svg_name)
      file_name = svg_name + '.svg' 
      file = open(file_name,'r')
      svg_list.append(file.readlines())
      file.close()

    # save the file
    result = meq.result()
    result.svg_plot = svg_list
    return result
