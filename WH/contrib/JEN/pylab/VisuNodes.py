# standard preamble
#
#% $Id$ 
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

from Timba.TDL import *
from Timba import pynode
from Timba import dmi
from Timba import utils
from Timba.Meq import meq

import inspect
import random


Settings.forest_state.cache_policy = 100;

_dbg = utils.verbosity(0,name='test_pynode');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;



#=====================================================================================
# Various specialized visualization pyNodes:
#=====================================================================================


class ScatterPlot (pynode.PyNode):
  """Make a scatter-plot of the means of the results of its children"""


  def __init__ (self, *args):
    pynode.PyNode.__init__(self,*args);
    self.set_symdeps('domain','resolution');
                              
  def get_result (self, request, *children):
    import pylab                                 # kludge....!
    # import Points2D

    xlabel = 'x'
    ylabel = 'y'
    make_plot = True
    if make_plot:
      pylab.figure(1)
      pylab.subplot(111)
      pylab.title('VisuNodes.ScatterPlot')

    xx = []
    yy = []
    for i,ch in enumerate(children):
      _dprint(0,'- child',i,':',dmi.dmi_typename(ch),': ch =',ch)
      v0 = ch.vellsets[0].value[0]
      print '--- v0:',type(v0),'::',v0
      if isinstance(v0,complex):
        xx.append(v0.real)
        yy.append(v0.imag)
        if make_plot:
          pylab.xlabel('real part')
          pylab.ylabel('imag part')
      else:
        xx.append(v0)
        yy.append(v0)
        if make_plot:
          pylab.xlabel(xlabel)
          pylab.ylabel(ylabel)

    if make_plot:
      # Make pylab numarrays and plot axes:
      xx = pylab.array(xx)
      yy = pylab.array(yy)
      [xmin,xmax] = [xx.min(),xx.max()]
      [ymin,ymax] = [yy.min(),yy.max()]
      pylab.plot([xmin,xmax], [0,0], color='black', linewidth=3)
      pylab.plot([0,0],[ymin,ymax], color='black', linewidth=3)

      # Plot the points themselves:
      pylab.plot(xx, yy, color='red', marker='o', linestyle=None)

      # Indicate the mean position:
      xmean = pylab.mean(xx)
      ymean = pylab.mean(yy)
      pylab.plot([xmean], [ymean], markeredgecolor='red',
                 marker='+', markersize=30, linestyle=None)
      pylab.text(xmean, ymean, ' mean', color='red', fontsize=20)

      # Make the stddev circle:
      stddev = (xx.stddev()**2+yy.stddev()**2)**0.5
      pylab.text(xmean+0.7*stddev, ymean+0.7*stddev, ' stddev', color='red', fontsize=20)
      # pylab.arrow([xmean,ymean], [xmean+stddev,ymean+stddev], color='red')
      make_circle(x0=xmean, y0=ymean, radius=stddev,
                  na=30, a1=0.0, a2=2*pylab.pi,
                  plot=make_plot, color='red', linestyle='--') 

    # Finished:
    if make_plot:
      pylab.grid()
      pylab.show()
    return None
    


#=====================================================================================
# Some helper functions:
#=====================================================================================

def make_circle(x0=0.0, y0=0.0, radius=1.0,
                na=30, a1=0.0, a2=None,
                plot=True, color='red', linestyle='--'):
  """Make a circle with given centre(x0,y0) and radius"""
  if plot:
    import pylab
    if a2==None: a2 = 2*pylab.pi
    xx = []
    yy = []
    aa = 2*pylab.pi*pylab.array(range(na))/float(na-1)
    for a in aa:
      xx.append(x0+radius*pylab.cos(a))
      yy.append(y0+radius*pylab.sin(a))
    pylab.plot(xx, yy, color='red', linestyle='--')
  return True

#=====================================================================================
# Make a test-forest:
#=====================================================================================

def _define_forest (ns,**kwargs):
  """Make trees with the various pyNodes"""
  cc = []
  
  if 1:
    for i in range(12):
      value = i
      value = complex(i,i)
      value = random.gauss(0,1)
      value = complex(random.gauss(0,1),random.gauss(0,1))
      cc.append(ns[str(i)] << value)
    ns.pynode << Meq.PyNode(children=cc, class_name="ScatterPlot", module_name=__file__)
                
  return True
  

#=====================================================================================
# Execute a test-forest:
#=====================================================================================

def _test_forest (mqs,parent,**kwargs):
  from Timba.Meq import meq
  cells = meq.cells(meq.domain(0,1,0,1),num_freq=20,num_time=10);
  request = meq.request(cells,rqtype='ev');
  mqs.execute('pynode',request);
  return True


#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':
#  from Timba.Meq import meqds 
  Timba.TDL._dbg.set_verbose(5);
  ns = NodeScope();
  _define_forest(ns);
  ns.Resolve();
