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

    # First get the (mean) values of its child results in yy (and xx):
    # NB: Here we need Tony's Result unpacking object...
    xx = []
    yy = []
    for i,ch in enumerate(children):
      _dprint(0,'- child',i,':',dmi.dmi_typename(ch),': ch =',ch)
      v0 = ch.vellsets[0].value[0]
      print '--- v0:',type(v0),'::',v0
      if isinstance(v0,complex):
        xx.append(v0.real)
        yy.append(v0.imag)
        xlabel = 'real part'
        ylabel = 'imag part'
      else:
        xx.append(v0)
        yy.append(v0)
        xlabel = 'x'
        ylabel = 'y'

    # Then make the pylab figure (I could not resist the temptation to
    # make some supporting classes to make things easy, albeit hidden):
    import Graphics         # A collection of Graphics classes
    import Figure           # A class that holds one or more Subplots

    # First make an (empty) pylab figure:
    fig = Figure.Figure()
    
    # A Graphics object is a Subplot object.
    grs = Graphics.Scatter(yy=yy, xx=xx,
                           title='VisuNodes.ScatterPlot',
                           xlabel=xlabel, ylabel=ylabel,
                           color='blue', style='o')
    
    # NB: Other Graphics object may be added to it, using grs.add(grs2)
    # .............
    # When complete, add the Subplot object to the Figure:
    fig.add(grs)

    # Finished: dispose of the Figure:
    fig.oneliners()
    svg_list_of_strings = fig.plot(dispose=['show','svg'])
    # NB: If the pylab plot is not needed, remove 'show' from the dispose list.
    # If dispose contains 'svg', .plot() returns the contents of the .svg file.
    # This is a list of strings, which is attached to the MeqResult of this pyNode.
    # It should then be picked up by Tony to recreate the SVG plot in the browser....
    result = meq.result()
    result.svg_plot = svg_list_of_strings
    return result


#========================================================================
# A version of ScatterPlot that uses pylab commands directly:
#========================================================================
    
class TheHardWay (pynode.PyNode):
  """Make a scatter-plot of the means of the results of its children"""


  def __init__ (self, *args):
    pynode.PyNode.__init__(self,*args);
    self.set_symdeps('domain','resolution');
                              
  def get_result (self, request, *children):
    import pylab                                 # kludge....!

    xlabel = 'x'
    ylabel = 'y'
    pylab.figure(1)
    pylab.subplot(111)
    pylab.title('VisuNodes.TheHardWay')

    xx = []
    yy = []
    for i,ch in enumerate(children):
      _dprint(0,'- child',i,':',dmi.dmi_typename(ch),': ch =',ch)
      v0 = ch.vellsets[0].value[0]
      print '--- v0:',type(v0),'::',v0
      if isinstance(v0,complex):
        xx.append(v0.real)
        yy.append(v0.imag)
        pylab.xlabel('real part')
        pylab.ylabel('imag part')
      else:
        xx.append(v0)
        yy.append(v0)
        pylab.xlabel(xlabel)
        pylab.ylabel(ylabel)

    pylab.plot(xx, yy, color='red', marker='o', linestyle=None)
    pylab.grid()

    # Finished:
    svg_list_of_strings = pylab_dispose(dispose=['show','svg'])
    # NB: If the pylab plot is not needed, remove 'show' from the dispose list.
    # If dispose contains 'svg', .plot() returns the contents of the .svg file.
    # This is a list of strings, which is attached to the MeqResult of this pyNode.
    # It should then be picked up by Tony to recreate the SVG plot in the browser....
    result = meq.result()
    result.svg_plot = svg_list_of_strings
    return result

#-------------------------------------------------------------------
    
def pylab_dispose(dispose='show'):
    """Generic routine to dispose of the pylab figure.
    Dipose can be a string (show, svg), or a list of strings"""

    import pylab                   
    rootname = 'xxx'
    print '** dispose(): ',dispose,rootname
    if dispose==None:
        return None
    if isinstance(dispose,str):
        dispose = [dispose]
    result = None
    svgname = None

    file_extensions = ['png','PNG','svg','SVG']
    for ext in file_extensions:
        if ext in dispose:
            filename = rootname+'.'+ext
            if ext in ['svg','SVG']: svgname = filename
            r = pylab.savefig(filename)
            print '** dispose:',ext,filename,'->',r

    if isinstance(svgname,str):
        file = open(filename,'r')
        result = file.readlines()
        file.close()
        print '** svg:',filename,'->',type(result),len(result)
        # for s in result: print '-',s
        if False:
            import os
            os.system("%s -size 640x480 %s" % ('display',filename))
            # -> error: "display: Opening and ending tag mismatch: name line 0 and text"
        
    if 'show' in dispose:
        # pylab.show._needmain = False
        pylab.show()
        # pylab.ion()
        # pylab.draw()
        # pylab.close()
        
    # Finished: return the result (if any):
    return result




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
    classname = "ScatterPlot"
    # classname = "TheHardWay"
    ns.pynode << Meq.PyNode(children=cc, class_name=classname, module_name=__file__)
                
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
